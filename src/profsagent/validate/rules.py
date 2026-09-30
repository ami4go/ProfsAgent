"""Deterministic validators V1–V23 + traceability rules T1–T10 (docs/01 §6.3, §8). NO LLM in this module.

Each check takes the design state (plain dicts assembled from Layer B) and returns violations:
    {code, severity: error|warning, nodes: [ids], message, evidence}
Checks are grouped by the stage whose output they judge, so the repair router can scope a repair.
"""
from __future__ import annotations

import re
from collections import Counter, defaultdict

from profsagent.config import pedagogy
from profsagent.design.deterministic import find_cycle
from profsagent.kg.quality import banned_in, bloom_of_verb, lemma, vague_degree, verbs_in

ERR, WARN = "error", "warning"


FIX_HINTS = {
    "VLO-COPY": "Keep the same verb and Bloom level, but rewrite the LO as ONE concrete task: a narrower object (one component, "
                "one subsystem, one supplied artefact), a specific given input as the condition, and a degree checkable by a single "
                "assessment task. Do not change the statement's first word away from the declared verb.",
    "VLO-DUP": "Make the two LOs name different skills or objects; merge them if they really are one step.",
    "V10": "The statement must START with the declared verb (same word). If you change the verb, update `verb` and `bloom_level` together.",
    "V11": "Add a checkable degree (number, threshold, or explicit criterion) and a condition (given X / using Y) inside the statement text.",
    "V12": "Replace the banned verb with an observable verb from the lexicon at the intended level.",
    "T2": "Add or re-level an LO so that at least one LO of this CO is at exactly the CO's Bloom level.",
    "V19": "Move the instance to a later release week, or remove the not-yet-taught topics/LOs from what it covers.",
    "V20": "Bring the weight inside the band, or add a weight_justification tied to the course intent.",
    "VA-ORDER": "List instances chronologically: each later instance must have release and due weeks ≥ the previous one.",
    "VT-SIZE": "Split the topic into 2–3 topics of ≤ 2 h each, distributing its LOs.",
    "V21": "Adjust topic hours so the total is 85–100% of the lecture budget.",
    "VTG-TAUGHT": "Add a topic that teaches this topic group (with covers_topic_groups), or propose dropping the group upstream.",
}


def v(code, sev, nodes, msg, **ev):
    d = {"code": code, "severity": sev, "nodes": list(nodes), "message": msg, "evidence": ev}
    if code in FIX_HINTS:
        d["fix_hint"] = FIX_HINTS[code]
    return d


# ------------------------------------------------------------------ statements (COs and LOs)
def _statement_checks(items: list[dict], kind: str) -> list[dict]:
    out = []
    for it in items:
        i, st = it["id"], it.get("statement", "")
        verb = lemma(it.get("verb", ""))
        # V12 banned verbs anywhere in the verb or the first clause
        b = banned_in(it.get("verb", "")) or banned_in(st.split(",")[0])
        if b:
            out.append(v("V12", ERR, [i], f"{kind} {i} uses banned/vague verb(s) {b}", statement=st))
        # V10 exactly one leading verb, and it must be the declared verb, from the lexicon
        if bloom_of_verb(verb) is None:
            out.append(v("V10", ERR, [i], f"{kind} {i}: verb '{it.get('verb')}' is not in the Bloom lexicon"))
        first_words = re.findall(r"[A-Za-z-]+", st)[:1]
        if first_words and lemma(first_words[0]) != verb:
            out.append(v("V10", ERR, [i], f"{kind} {i}: statement starts with '{first_words[0]}' but declares verb '{verb}' (Bloom level must follow the verb actually used)", statement=st))
        head = st.split(",")[0]
        chained = re.findall(r"\b(and|or|then)\s+([A-Za-z-]+)", head)
        chained = [w for _, w in chained if bloom_of_verb(lemma(w)) is not None and lemma(w) != verb and w.lower() not in ("test", "model", "map", "use")]
        if chained:
            out.append(v("V10", ERR, [i], f"{kind} {i} chains verbs ('{verb}' + {chained}): one outcome per statement", statement=st))
        # V11 condition + degree present, non-vacuous, and present in the statement
        for part in ("condition", "degree"):
            val = (it.get(part) or "").strip()
            if len(val) < 4:
                out.append(v("V11", ERR, [i], f"{kind} {i} has no {part}"))
            elif part == "degree" and vague_degree(val):
                out.append(v("V11", ERR, [i], f"{kind} {i} degree is vague ({vague_degree(val)}): '{val}'"))
            elif _norm(val)[:25] not in _norm(st):
                out.append(v("V11", WARN, [i], f"{kind} {i} {part} is not visible in the statement text", part_text=val))
        # Bloom triangulation (lexicon vs claimed)
        lex = bloom_of_verb(verb)
        amb = pedagogy()  # noqa: F841 (kept for future ambiguous-verb handling)
        if lex is not None and it.get("bloom_level") and abs(lex - int(it["bloom_level"])) >= 2:
            out.append(v("VB", WARN, [i], f"{kind} {i}: claimed Bloom L{it['bloom_level']} but verb '{verb}' is lexicon L{lex}"))
    return out


def _toks(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(t) > 2}


def _jacc(a: str, b: str) -> float:
    x, y = _toks(a), _toks(b)
    return len(x & y) / max(len(x | y), 1)


def _covers(phrase: str, texts: list[str]) -> bool:
    """Deterministic check that a required phrase is visibly covered by some text (≥60% of its content tokens)."""
    p = _toks(phrase) - {"and", "the", "using", "with", "programming"}
    return bool(p) and any(len(p & _toks(t)) / len(p) >= 0.6 for t in texts)


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", (s or "").lower()).strip()


def check_cos(state: dict) -> list[dict]:
    ped = pedagogy()
    cos = state.get("cos", [])
    band = state["bloom_band"]
    out = []
    n = len(cos)
    if not (ped["co_count"]["min"] <= n <= ped["co_count"]["max"]):
        out.append(v("V4", ERR, [c["id"] for c in cos], f"{n} COs; expected {ped['co_count']['min']}–{ped['co_count']['max']}"))
    for c in cos:
        lvl = int(c["bloom_level"])
        if lvl > band["ceiling"]:
            out.append(v("V7", ERR, [c["id"]], f"{c['id']} Bloom L{lvl} above band ceiling L{band['ceiling']}"))
        if lvl < band["floor"]:
            out.append(v("V8", ERR, [c["id"]], f"{c['id']} Bloom L{lvl} below band floor L{band['floor']}"))
    if len({int(c["bloom_level"]) for c in cos}) < 2 and n > 1:
        out.append(v("VCO-SPREAD", WARN, [c["id"] for c in cos], "all COs are at one Bloom level"))
    pairs = Counter((lemma(c["verb"]), _norm(c["behaviour"])[:40]) for c in cos)
    for (vb, beh), k in pairs.items():
        if k > 1:
            out.append(v("VCO-DUP", ERR, [c["id"] for c in cos if lemma(c["verb"]) == vb], f"{k} COs share verb '{vb}' and object"))
    tgs = {g["id"] for g in state.get("topic_groups", [])}
    covered = {t for c in cos for t in c.get("covers_topic_groups", [])}
    dropped = {t for p in state.get("topic_group_proposals", []) if p.get("action") in ("drop", "merge") for t in p.get("targets", [])}
    miss = tgs - covered - dropped
    if miss:
        out.append(v("VCO-COVER", ERR, sorted(miss), f"topic groups not covered by any CO and not proposed for drop/merge: {sorted(miss)}"))
    bad = covered - tgs
    if bad:
        out.append(v("T10", ERR, sorted(bad), f"COs reference unknown topic groups {sorted(bad)}"))
    return out + _statement_checks(cos, "CO")


def check_copo(state: dict) -> list[dict]:
    out = []
    cos = {c["id"] for c in state.get("cos", [])}
    pos = {p["uid"] for p in state.get("programme_pos", [])}
    per = defaultdict(list)
    for m in state.get("copo", []):
        per[m["co_id"]].append(m)
        if m["po_uid"] not in pos:
            out.append(v("T10", ERR, [m["co_id"], m["po_uid"]], f"unknown PO {m['po_uid']}"))
        if m["co_id"] not in cos:
            out.append(v("T10", ERR, [m["co_id"]], f"mapping for unknown CO {m['co_id']}"))
        apm = state.get("activity_po_map", {})
        if not any(m["po_uid"] in apm.get(a, []) for a in m.get("evidencing_activities", [])):
            out.append(v("VCOPO-ACT", WARN, [m["co_id"], m["po_uid"]],
                         f"{m['co_id']}→{m['po_uid']}: none of its evidencing activities maps to that PO, so its strength can never be computed"))
    for c in cos:
        k = len(per.get(c, []))
        if k == 0:
            out.append(v("T4", ERR, [c], f"{c} maps to no PO"))
        elif k > 3:
            out.append(v("T4", WARN, [c], f"{c} maps to {k} POs (max 3)"))
    return out


def check_los(state: dict) -> list[dict]:
    ped = pedagogy()["lo_count"]
    cos = {c["id"]: c for c in state.get("cos", [])}
    los = state.get("los", [])
    out = _statement_checks(los, "LO")
    by_co = defaultdict(list)
    for lo in los:
        if lo["parent_co"] not in cos:
            out.append(v("T1", ERR, [lo["id"]], f"{lo['id']} has unknown parent {lo['parent_co']}"))
            continue
        by_co[lo["parent_co"]].append(lo)
        if not lo["id"].startswith(lo["parent_co"] + "."):
            out.append(v("T1", WARN, [lo["id"]], f"{lo['id']} id does not follow CO<k>.LO<j> for parent {lo['parent_co']}"))
        if int(lo["bloom_level"]) > int(cos[lo["parent_co"]]["bloom_level"]):
            out.append(v("T3", ERR, [lo["id"]], f"{lo['id']} L{lo['bloom_level']} above parent {lo['parent_co']} L{cos[lo['parent_co']]['bloom_level']}"))
    for cid, c in cos.items():
        k = len(by_co[cid])
        if k < ped["per_co_min"] or k > ped["per_co_max"]:
            out.append(v("T2", ERR, [cid], f"{cid} has {k} LOs (expected {ped['per_co_min']}–{ped['per_co_max']})"))
        if by_co[cid] and not any(int(lo["bloom_level"]) == int(c["bloom_level"]) for lo in by_co[cid]):
            out.append(v("T2", ERR, [cid], f"{cid} (L{c['bloom_level']}) has no LO at its own level — nothing in the course reaches it"))
    if not (ped["total_min"] <= len(los) <= ped["total_max"]):
        out.append(v("VLO-COUNT", ERR, [], f"{len(los)} LOs in total (expected {ped['total_min']}–{ped['total_max']})"))
    # distinctness: an LO must not restate its parent CO or a sibling LO
    for lo in los:
        c = cos.get(lo["parent_co"])
        if c and _jacc(lo["statement"], c["statement"]) >= 0.8:
            out.append(v("VLO-COPY", ERR, [lo["id"], c["id"]], f"{lo['id']} restates its parent {c['id']} (token overlap {_jacc(lo['statement'], c['statement']):.2f}); an LO must be a narrower, single-task step"))
    for i, a in enumerate(los):
        for b in los[i + 1:]:
            if _jacc(a["statement"], b["statement"]) >= 0.8:
                out.append(v("VLO-DUP", ERR, [a["id"], b["id"]], f"{a['id']} and {b['id']} are near-duplicates"))
    ids = {lo["id"] for lo in los}
    edges = [(r, lo["id"]) for lo in los for r in lo.get("requires", [])]
    for a, b in edges:
        if a not in ids:
            out.append(v("T10", ERR, [b], f"{b} requires unknown LO {a}"))
    cyc = find_cycle(sorted(ids), [(a, b) for a, b in edges if a in ids])
    if cyc:
        out.append(v("VLO-DAG", ERR, cyc, f"LO dependency cycle: {' → '.join(cyc)}"))
    hb = state.get("hours_budget")
    if hb and los:
        lec = sum(float(lo.get("est_lecture_h", 0)) for lo in los)
        if hb["lecture_hours_total"] and abs(lec - hb["lecture_hours_total"]) / hb["lecture_hours_total"] > 0.15:
            out.append(v("V21", WARN, [], f"LO lecture-hour estimates sum to {lec:.1f} h vs budget {hb['lecture_hours_total']} h (±15%)"))
    return out


def check_structure(state: dict) -> list[dict]:
    out = []
    los = {lo["id"] for lo in state.get("los", [])}
    topics = [t for m in state.get("modules", []) for t in m["topics"]]
    tids = {t["id"] for t in topics}
    served = set()
    for t in topics:
        if not t.get("serves_los"):
            out.append(v("T5", ERR, [t["id"]], f"topic {t['id']} serves no LO (orphan)"))
        for lo in t.get("serves_los", []):
            if lo not in los:
                out.append(v("T10", ERR, [t["id"]], f"topic {t['id']} serves unknown LO {lo}"))
            served.add(lo)
        for r in t.get("requires", []):
            if r not in tids:
                out.append(v("T10", WARN, [t["id"]], f"topic {t['id']} requires unknown topic {r}"))
        if float(t["est_hours"]) > 3.01:
            out.append(v("VT-SIZE", ERR, [t["id"]], f"topic {t['id']} is {t['est_hours']} h (> 3 h; split it)"))
        for tg in t.get("covers_topic_groups", []):
            if tg not in {g["id"] for g in state.get("topic_groups", [])}:
                out.append(v("T10", ERR, [t["id"]], f"topic {t['id']} references unknown topic group {tg}"))
    for lo in sorted(los - served):
        out.append(v("T5", ERR, [lo], f"LO {lo} is not taught by any topic"))
    # every professor topic group (not explicitly dropped/merged at S4) must reach at least one taught topic
    dropped = {x for p in state.get("topic_group_proposals", []) if p.get("action") in ("drop", "merge") for x in p.get("targets", [])}
    taught_tgs = {tg for t in topics for tg in t.get("covers_topic_groups", [])}
    for g in state.get("topic_groups", []):
        if g["id"] not in dropped and g["id"] not in taught_tgs:
            out.append(v("VTG-TAUGHT", ERR, [g["id"]], f"topic group {g['id']} '{g.get('title')}' is not taught by any topic (and was not proposed for drop/merge)"))
    # content.must_include / must_exclude constraints, checked against topic titles and LO statements
    lt = state.get("labs_tutorials") or {}
    texts = ([t["title"] for t in topics] + [lo.get("statement", "") for lo in state.get("los", [])]
             + [x.get("exercise", "") + " " + x.get("title", "") for x in lt.get("labs", [])] + [x.get("activity", "") for x in lt.get("tutorials", [])]
             + [i.get("format", "") for c in (state.get("assessment") or {}).get("components", []) for i in c["instances"]])
    for cn in state.get("constraints", []):
        m = re.match(r"content\.(must_include|must_exclude)\[(.+)\]", cn.get("target", ""))
        if not m:
            continue
        phrase = m.group(2).strip("'\" ")
        if not phrase or phrase.startswith("<") or not _toks(phrase):
            out.append(v("VK-MALFORMED", WARN, [cn["id"]], f"constraint {cn['id']} has a placeholder/empty target '{cn['target']}' (from G3); raw: {cn.get('raw', '')[:100]}"))
            continue
        hit = _covers(phrase, texts)
        if m.group(1) == "must_include" and not hit:
            out.append(v("VK-CONTENT", ERR if cn.get("hardness") == "hard" else WARN, [cn["id"]], f"required content '{phrase}' ({cn['id']}) is not covered by any topic or LO"))
        if m.group(1) == "must_exclude" and hit:
            out.append(v("VK-CONTENT", ERR if cn.get("hardness") == "hard" else WARN, [cn["id"]], f"excluded content '{phrase}' ({cn['id']}) appears in the course"))
    hb = state.get("hours_budget")
    total = sum(float(t["est_hours"]) for t in topics)
    if hb and total > hb["lecture_hours_total"] + 1e-6:
        out.append(v("V21", ERR, [], f"topics need {total:.1f} h > {hb['lecture_hours_total']} h available"))
    if hb and topics and total < 0.85 * hb["lecture_hours_total"]:
        out.append(v("V21", ERR, [], f"topics fill only {total:.1f} h of {hb['lecture_hours_total']} h (< 85%): the schedule would leave teaching weeks empty"))
    return out


def check_schedule(state: dict) -> list[dict]:
    s = state.get("schedule") or {}
    out = []
    if s and not s.get("feasible", True):
        out.append(v("V21", ERR, [], s.get("explanation") or "schedule infeasible"))
    if s and s.get("dropped_edges"):
        out.append(v("VT-DAG", WARN, [f"{a}->{b}" for a, b in s["dropped_edges"]], f"topic prerequisite cycle broken by dropping {s['dropped_edges']}"))
    weeks = state.get("weeks")
    if s and weeks and len(s.get("weeks", [])) != weeks:
        out.append(v("V2", ERR, [], f"schedule has {len(s['weeks'])} weeks, constraint says {weeks}"))
    if s:
        empty = [w["week"] for w in s["weeks"] if not w["items"]]
        if empty:
            out.append(v("V6", WARN, [f"W{w:02d}" for w in empty], f"weeks with no lecture topics: {empty}"))
    return out


def _topic_last_week(state: dict) -> dict[str, int]:
    return {t: max(ws) for t, ws in (state.get("schedule") or {}).get("topic_weeks", {}).items()}


def _lo_last_week(state: dict) -> dict[str, int]:
    last = _topic_last_week(state)
    lo_w: dict[str, int] = {}
    for m in state.get("modules", []):
        for t in m["topics"]:
            for lo in t.get("serves_los", []):
                if t["id"] in last:
                    lo_w[lo] = max(lo_w.get(lo, 0), last[t["id"]])
    return lo_w


def check_labs(state: dict) -> list[dict]:
    out = []
    plan = state.get("labs_tutorials") or {}
    ltp = state.get("ltp", {})
    los = {lo["id"]: lo for lo in state.get("los", [])}
    first_week = {}
    for t, ws in (state.get("schedule") or {}).get("topic_weeks", {}).items():
        first_week[t] = min(ws)
    labs = plan.get("labs", [])
    lab_required = state.get("lab_required") == "yes" or (ltp.get("P") or 0) > 0
    hands_on = [lo for lo in los.values() if lo.get("hands_on")]
    if (lab_required or hands_on) and not labs and (ltp.get("P") or 0) > 0:
        out.append(v("V18", ERR, [], "lab hours allocated / hands-on LOs present, but no lab plan"))
    if lab_required and (ltp.get("P") or 0) == 0:
        out.append(v("V18", ERR, [], "lab required by professor but L-T-P has P = 0"))
    practised = {lo for s in labs + plan.get("tutorials", []) for lo in s.get("practises_los", [])}
    if (ltp.get("P") or 0) > 0:
        for lo in hands_on:
            if lo["id"] not in practised:
                out.append(v("V18", WARN, [lo["id"]], f"hands-on LO {lo['id']} is never practised in a lab or tutorial"))
    for s in labs + plan.get("tutorials", []):
        for t in s.get("uses_topics", []):
            if t in first_week and first_week[t] > s["week"]:
                out.append(v("V19", ERR, [s["id"], t], f"{s['id']} (week {s['week']}) uses topic {t} first taught in week {first_week[t]}"))
        for lo in s.get("practises_los", []):
            if lo not in los:
                out.append(v("T10", ERR, [s["id"]], f"{s['id']} practises unknown LO {lo}"))
    return out


def check_assessment(state: dict) -> list[dict]:
    ped = pedagogy()
    out = []
    comps = (state.get("assessment") or {}).get("components", [])
    los = {lo["id"]: lo for lo in state.get("los", [])}
    weeks = state.get("weeks", 13)
    total = sum(float(c["weight_pct"]) for c in comps)
    if abs(total - 100) > 0.01:
        out.append(v("V1", ERR, [c["type"] for c in comps], f"assessment weights sum to {total}, not 100"))
    cc = ped["thresholds"]["component_count"]
    if not (cc["min"] <= len(comps) <= cc["max"]):
        out.append(v("V13", WARN, [], f"{len(comps)} assessment components (expected {cc['min']}–{cc['max']})"))
    last_topic = _topic_last_week(state)
    priors = state.get("weight_priors", {})
    fallback = ped["thresholds"]["weight_band_fallback"]
    events = Counter()
    assessed: dict[str, int] = defaultdict(int)
    midsem = state.get("midsem_after_week")
    types = {c["type"].lower() for c in comps}
    for c in comps:
        n_inst = len(c["instances"])
        if c.get("best_k") is not None or c.get("n") is not None:
            k, n = c.get("best_k"), c.get("n")
            if n is not None and n != n_inst:
                out.append(v("V3", ERR, [c["type"]], f"{c['type']}: declares n={n} but schedules {n_inst} instances"))
            if k is not None and not (1 <= k < (n or n_inst)):
                out.append(v("V3", ERR, [c["type"]], f"{c['type']}: best {k} of {n or n_inst} is vacuous or invalid"))
            if (n or n_inst) < 3 and k is not None:
                out.append(v("V3", WARN, [c["type"]], f"{c['type']}: best-k-of-n with n < 3"))
        t = c["type"].lower()
        band = None
        pr = priors.get(t)
        if pr and pr.get("n", 0) >= 5:
            band = pr["iqr"]
        elif t in fallback:
            band = fallback[t]
        if band and not (band[0] - 1e-6 <= float(c["weight_pct"]) <= band[1] + 1e-6) and not (c.get("weight_justification") or "").strip():
            out.append(v("V20", ERR, [c["type"]], f"{c['type']} weight {c['weight_pct']}% outside band {band} with no justification"))
        for inst in c["instances"]:
            events[inst["due_week"]] += 1
            s = sum(float(a["marks_pct_of_instance"]) for a in inst["assesses"])
            if abs(s - 100) > 0.5:
                out.append(v("VA-MARKS", ERR, [inst["id"]], f"{inst['id']}: LO marks shares sum to {s}, not 100"))
            if inst["due_week"] < inst["release_week"]:
                out.append(v("VA-TIME", ERR, [inst["id"]], f"{inst['id']} due before release"))
            if inst["release_week"] > weeks + 2 or inst["release_week"] < 1:
                out.append(v("VA-TIME", ERR, [inst["id"]], f"{inst['id']} release week {inst['release_week']} outside semester"))
            ref_week = inst["due_week"] if t == "project" else inst["release_week"]   # a project may run alongside teaching
            for tp in inst.get("covers_topics", []):
                if tp in last_topic and last_topic[tp] > ref_week:
                    out.append(v("V19", ERR, [inst["id"], tp], f"{inst['id']} ({'due' if t == 'project' else 'released'} week {ref_week}) covers topic {tp} taught until week {last_topic[tp]}"))
            lo_last = _lo_last_week(state)
            for a in inst["assesses"]:
                lo = los.get(a["lo_id"])
                if not lo:
                    out.append(v("T10", ERR, [inst["id"]], f"{inst['id']} assesses unknown LO {a['lo_id']}"))
                    continue
                if int(a["bloom_level"]) >= int(lo["bloom_level"]):
                    assessed[a["lo_id"]] += 1
                if a["lo_id"] in lo_last and lo_last[a["lo_id"]] > inst["due_week"] and t not in ("project",):
                    out.append(v("V19", ERR, [inst["id"], a["lo_id"]], f"{inst['id']} (due week {inst['due_week']}) assesses {a['lo_id']} whose topics run until week {lo_last[a['lo_id']]}"))
            if t == "midsem" and midsem and inst["release_week"] != midsem:
                out.append(v("VA-MIDSEM", WARN, [inst["id"]], f"mid-sem placed in week {inst['release_week']}, calendar assumption is after week {midsem}"))
    for c in comps:
        rel = [i["release_week"] for i in c["instances"]]
        due = [i["due_week"] for i in c["instances"]]
        if rel != sorted(rel) or due != sorted(due):
            out.append(v("VA-ORDER", ERR, [i["id"] for i in c["instances"]], f"{c['type']} instances are out of order: releases {rel}, dues {due} (list them chronologically; milestones must precede the final)"))
        if c["type"].lower() == "project" and c["instances"]:
            first = min(i["release_week"] for i in c["instances"])
            last = max(i["due_week"] for i in c["instances"])
            if last - first < 4:
                out.append(v("VA-PROJ", ERR, [c["type"]], f"project runs only weeks {first}–{last} (< 4 weeks) — too short for a substantial project"))
            if first > weeks * 0.6:
                out.append(v("VA-PROJ", WARN, [c["type"]], f"project released in week {first}, late in a {weeks}-week semester"))
    for lo_id, lo in los.items():
        if not assessed.get(lo_id):
            out.append(v("V9", ERR, [lo_id], f"LO {lo_id} (L{lo['bloom_level']}) is never assessed at or above its Bloom level"))
    cap = ped["thresholds"]["max_events_per_week"]
    for w, k in events.items():
        if k > cap:
            out.append(v("VA-LOAD", WARN, [f"W{w:02d}"], f"{k} assessment events due in week {w} (cap {cap})"))
    for kid, ctype in (("K06", "midsem"), ("K07", "endsem")):
        if ctype not in types and not any(cn.get("target") == f"assessment.component[{ctype}].present" and cn.get("op") == "absent"
                                          for cn in state.get("constraints", [])):
            out.append(v("VA-REG", WARN, [kid], f"no {ctype} component although UGREG-2025§6.2 normally schedules one"))
    for cn in state.get("constraints", []):
        m = re.match(r"assessment\.component\[(\w+)\]\.(present|weight_pct)", cn.get("target", ""))
        if not m:
            continue
        ct, what = m.group(1).lower(), m.group(2)
        comp = next((c for c in comps if c["type"].lower() == ct), None)
        if what == "present" and cn["op"] == "absent" and comp and cn["hardness"] == "hard":
            out.append(v("VK", ERR, [cn["id"]], f"{ct} present but hard constraint {cn['id']} forbids it"))
        if what == "weight_pct" and comp and cn.get("value") is not None:
            w, val = float(comp["weight_pct"]), float(cn["value"])
            ok = {"<=": w <= val, ">=": w >= val, "==": abs(w - val) < 0.01}.get(cn["op"], True)
            if not ok:
                out.append(v("VK", ERR if cn["hardness"] == "hard" else WARN, [cn["id"]], f"{ct} weight {w} violates {cn['id']} ({cn['op']} {val})"))
    return out


def check_copo_computed(state: dict) -> list[dict]:
    out = []
    for r in state.get("copo_computed", []):
        if r["claimed"] and r["strength_computed"] == 0:
            out.append(v("V23", ERR, [r["co_id"], r["po_uid"]], f"{r['co_id']}→{r['po_uid']} claimed (provisional {r['strength_provisional']}) but no assessed activity evidences it"))
        elif r["claimed"] and r["strength_provisional"] and abs(r["strength_provisional"] - r["strength_computed"]) >= 2:
            out.append(v("V23", WARN, [r["co_id"], r["po_uid"]], f"{r['co_id']}→{r['po_uid']}: provisional {r['strength_provisional']} vs computed {r['strength_computed']} (share {r['share']})"))
    return out


def check_positioning(state: dict) -> list[dict]:
    out = []
    pos = state.get("positioning") or {}
    known = set(state.get("known_course_uids", []))
    ext = {e["id"] for e in state.get("external_courses", [])}
    level = state.get("level") or 9
    lvl_of = state.get("course_levels", {})
    th = pedagogy()["thresholds"]
    for p in pos.get("prerequisites", []):
        if p["course_uid"] not in known:
            out.append(v("V14", ERR, [p["course_uid"]], f"prerequisite {p['course_uid']} not in the catalogue"))
        elif lvl_of.get(p["course_uid"], 0) > level:
            out.append(v("V14", ERR, [p["course_uid"]], f"prerequisite {p['course_uid']} is level {lvl_of[p['course_uid']]}xx > course level {level}xx"))
        if not p.get("relied_topics"):
            out.append(v("V14", ERR, [p["course_uid"]], f"prerequisite {p['course_uid']} names no relied-upon topics"))
    comps = pos.get("comparable", [])
    for c in comps:
        if c["kind"] == "internal" and c["ref"] not in known:
            out.append(v("V16", ERR, [c["ref"]], f"internal comparable {c['ref']} not in the catalogue"))
        if c["kind"] == "external" and c["ref"] not in ext:
            out.append(v("V16", ERR, [c["ref"]], f"external comparable {c['ref']} is not an accepted single-course page"))
    if len(comps) < 3:
        out.append(v("V16", WARN, [], f"only {len(comps)} comparable courses"))
    if not pos.get("anti_requisites"):
        overl = {o["course_uid"]: o.get("weighted_jaccard") or 0 for o in state.get("overlap_computed", [])}
        high = [u for u, x in overl.items() if x >= th["anti_requisite_overlap"]]
        if high:
            out.append(v("V17", ERR, high, f"'no anti-requisites' but computed overlap ≥ {th['anti_requisite_overlap']} with {high}"))
    for a in pos.get("anti_requisites", []):
        if a["course_uid"] not in known:
            out.append(v("V17", ERR, [a["course_uid"]], f"anti-requisite {a['course_uid']} not in the catalogue"))
    return out


def check_resources(state: dict) -> list[dict]:
    out = []
    for r in state.get("resources", []):
        if not r.get("verification", {}).get("verified"):
            out.append(v("V15", ERR, [r.get("candidate_id", "?")], f"resource '{r.get('title')}' not verified: {r.get('verification', {}).get('problems')}"))
        if not r.get("supports_topics"):
            out.append(v("V15", WARN, [r.get("candidate_id", "?")], f"resource '{r.get('title')}' supports no topic"))
    return out


STAGE_CHECKS = {
    "positioning": [check_positioning], "cos": [check_cos], "copo": [check_copo], "los": [check_los],
    "structure": [check_structure], "schedule": [check_schedule], "labs": [check_labs],
    "assessment": [check_assessment, check_copo_computed], "resources": [check_resources],
}


def run(state: dict, stages: list[str] | None = None) -> list[dict]:
    out = []
    for st, fns in STAGE_CHECKS.items():
        if stages and st not in stages:
            continue
        for fn in fns:
            for x in fn(state):
                x["stage"] = st
                out.append(x)
    return out


def errors(vs: list[dict]) -> list[dict]:
    return [x for x in vs if x["severity"] == ERR]
