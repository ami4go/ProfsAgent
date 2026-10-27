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
from profsagent.kg.quality import PREFIX_RE, banned_in, bloom_of_verb, bloom_range_of_verb, lemma, vague_degree, verbs_in
from profsagent.validate import constraints, regulation, semantic, text
from profsagent.validate.record import ERR, FIX_HINTS, WARN, errors, v  # noqa: F401 (errors, FIX_HINTS re-exported)


# ------------------------------------------------------------------ statements (COs and LOs)
def _statement_checks(items: list[dict], kind: str) -> list[dict]:
    out = []
    for it in items:
        i, st = it["id"], it.get("statement", "")
        verb = lemma(it.get("verb", ""))
        # VT-TEMPLATE: a degree-bank template copied without filling it in ("for {n} of {m} short items")
        holes = sorted({h for f in ("statement", "condition", "degree") for h in re.findall(r"\{[A-Za-z_]+\}", it.get(f) or "")})
        if holes:
            out.append(v("VT-TEMPLATE", ERR, [i], f"{kind} {i} still contains unfilled template text {holes}", statement=st))
        # V12 banned verbs: the declared verb, the statement's leading verb, or a verb chained with and/or/then.
        # Not anywhere in the clause: "Evaluate natural-language understanding models" or "a robot grasp planner"
        # use the words as nouns.
        head = PREFIX_RE.sub("", st.split(",")[0]).lower()
        b = banned_in(it.get("verb", "")) or [w for w in banned_in(head) if re.match(rf"\s*{re.escape(w)}\b", head)
                                               or re.search(rf"\b(and|or|then)\s+{re.escape(w)}\b", head)]
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
            elif kind != "CO" and _norm(val)[:25] not in _norm(st):
                # LOs only: a CO is a short sentence (≤ 35 words, like IIIT-D's) whose full condition/degree live in its fields
                out.append(v("V11", WARN, [i], f"{kind} {i} {part} is not visible in the statement text", part_text=val))
        # VT-LEN: length outside the range of real IIIT-D statements (config/pedagogy.yaml thresholds.statement_words)
        lo_hi = (pedagogy()["thresholds"].get("statement_words") or {}).get(kind)
        n_words = len(st.split())
        if lo_hi and st and not (lo_hi[0] <= n_words <= lo_hi[1]):
            out.append(v("VT-LEN", WARN, [i], f"{kind} {i} is {n_words} words; typical {kind} statements are {lo_hi[0]}–{lo_hi[1]}", statement=st))
        # Bloom triangulation (lexicon vs claimed); ambiguous verbs (e.g. develop: L3–L6) accept their whole range
        rng = bloom_range_of_verb(verb)
        if rng and it.get("bloom_level"):
            claimed = int(it["bloom_level"])
            gap = 0 if rng[0] <= claimed <= rng[1] else min(abs(claimed - rng[0]), abs(claimed - rng[1]))
            if gap >= 2:
                lex = f"L{rng[0]}" if rng[0] == rng[1] else f"L{rng[0]}–L{rng[1]}"
                out.append(v("VB", WARN, [i], f"{kind} {i}: claimed Bloom L{claimed} but verb '{verb}' is lexicon {lex}"))
    return out


_toks, _jacc, _covers, _norm = text.toks, text.jacc, text.covers, text.norm


def check_cos(state: dict) -> list[dict]:
    ped = pedagogy()
    cos = state.get("cos", [])
    band = state["bloom_band"]
    out = []
    n = len(cos)
    cc = state.get("co_count") or ped["co_count"]
    if not (cc["min"] <= n <= cc["max"]):
        out.append(v("V4", ERR, [c["id"] for c in cos], f"{n} COs; expected {cc['min']}–{cc['max']} ({cc.get('basis', 'config')})"))
    hb = ped.get("co_high_bloom")
    if hb and n:
        high = [c["id"] for c in cos if int(c["bloom_level"]) >= hb["min_level"]]
        if len(high) < hb["min_fraction"] * n:
            out.append(v("VCO-BL", ERR, [c["id"] for c in cos if c["id"] not in high],
                         f"only {len(high)} of {n} COs are at BL{hb['min_level']}–BL6; the IIIT-D template requires at least half"))
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
            dups = [c["id"] for c in cos if (lemma(c["verb"]), _norm(c["behaviour"])[:40]) == (vb, beh)]
            out.append(v("VCO-DUP", ERR, dups, f"{k} COs share verb '{vb}' and object"))
    tgs = {g["id"] for g in state.get("topic_groups", [])}
    covered = {t for c in cos for t in c.get("covers_topic_groups", [])}
    dropped = {t for p in state.get("topic_group_proposals", []) if p.get("action") in ("drop", "merge") for t in p.get("targets", [])}
    miss = tgs - covered - dropped
    if miss:
        out.append(v("VCO-COVER", ERR, sorted(miss), f"topic groups not covered by any CO and not proposed for drop/merge: {sorted(miss)}"))
    bad = covered - tgs
    if bad:
        out.append(v("T10", ERR, sorted(bad), f"COs reference unknown topic groups {sorted(bad)}"))
    out += constraints.check_stage(state, "cos")          # co.count, co.bloom_min / bloom_max
    return out + _statement_checks(cos, "CO") + semantic.check_cos(state)


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
    for (co, po), k in Counter((m["co_id"], m["po_uid"]) for m in state.get("copo", [])).items():
        if k > 1:
            out.append(v("T4", WARN, [co, po], f"{co}→{po} is mapped {k} times"))
    lim = pedagogy().get("copo_per_programme", {"min": 1, "max_warn": 5})
    progs = state.get("programmes") or sorted({p.split("/")[0] for p in pos})
    for c in cos:
        if not per.get(c):
            out.append(v("T4", ERR, [c], f"{c} maps to no PO"))
            continue
        for prog in progs:   # IIIT-D template: map every CO against every CSE programme
            k = len({m["po_uid"] for m in per[c] if m["po_uid"].split("/")[0] == prog})   # distinct: duplicates must not inflate
            if k < lim["min"]:
                out.append(v("T4", ERR, [c, prog], f"{c} maps to no outcome of {prog} (the template asks for a mapping for every CSE programme)"))
            elif k > lim["max_warn"]:
                out.append(v("T4", WARN, [c, prog], f"{c} maps to {k} outcomes of {prog}; keep only the strong links"))
        for m in per[c]:
            if not (m.get("justification") or "").strip():
                out.append(v("T4", ERR, [c, m["po_uid"]], f"{c}→{m['po_uid']} has no explanation (the template has a CO-Explanation column)"))
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
    return out + _lab_fit_checks(state, los) + semantic.check_los(state)


def _lab_fit_checks(state: dict, los: list[dict]) -> list[dict]:
    """VC-NOLAB: most LOs are hands-on but L-T-P has no lab, and the professor never decided against one (a "no" in the
    form's lab field is respected: the CSE201 runs teach hands-on LOs in tutorials by choice)."""
    if not los or (state.get("ltp") or {}).get("P") or state.get("lab_required") == "no":
        return []
    hands_on = [lo["id"] for lo in los if lo.get("hands_on")]
    share = len(hands_on) / len(los)
    if share < pedagogy()["thresholds"]["hands_on_without_lab_share"]:
        return []
    return [v("VC-NOLAB", WARN, ["ltp"],
              f"{len(hands_on)} of {len(los)} LOs are hands-on but L-T-P has no lab hours (P = 0) and no lab decision was "
              f"given; add lab hours or confirm that tutorials are enough", hands_on=hands_on, share=round(share, 2))]


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
    out += constraints.check_stage(state, "structure")    # content.must_include / must_exclude / max_hours_on
    hb = state.get("hours_budget")
    total = sum(float(t["est_hours"]) for t in topics)
    if hb and total > hb["lecture_hours_total"] + 1e-6:
        out.append(v("V21", ERR, [], f"topics need {total:.1f} h > {hb['lecture_hours_total']} h available"))
    if hb and topics and total < 0.85 * hb["lecture_hours_total"]:
        out.append(v("V21", ERR, [], f"topics fill only {total:.1f} h of {hb['lecture_hours_total']} h (< 85%): the schedule would leave teaching weeks empty"))
    target = (state.get("template_rules") or {}).get("outside_load_hours_per_week")
    if target and topics:
        missing = [t["id"] for t in topics if t.get("outside_load_hours") is None]
        if missing:
            out.append(v("VT-LOAD", WARN, missing, f"{len(missing)} topics have no average outside-lecture load (template column 'Average load')"))
        known = [t for t in topics if t.get("outside_load_hours") is not None]
        hrs = sum(float(t["est_hours"]) for t in known)
        if hrs:
            avg = sum(float(t["outside_load_hours"]) * float(t["est_hours"]) for t in known) / hrs
            if not (target["min"] - 1e-6 <= avg <= target["max"] + 1e-6):
                out.append(v("VT-LOAD", WARN, [t["id"] for t in known],
                             f"average outside-lecture load is {avg:.1f} h/week; the IIIT-D template recommends {target['min']:g}–{target['max']:g} h"))
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
    # VT-ORDER: a topic must not start before a topic it requires (edges the scheduler dropped to break a cycle are
    # already reported as VT-DAG)
    first = {t: min(ws) for t, ws in s.get("topic_weeks", {}).items() if ws}
    dropped = {tuple(e) for e in s.get("dropped_edges", [])}
    for m in state.get("modules", []):
        for t in m["topics"]:
            for r in t.get("requires", []):
                if t["id"] in first and r in first and (r, t["id"]) not in dropped and first[t["id"]] < first[r]:
                    out.append(v("VT-ORDER", ERR, [t["id"], r], f"topic {t['id']} starts in week {first[t['id']]}, before the topic "
                                 f"it requires, {r} (week {first[r]})"))
    out += constraints.check_stage(state, "schedule")     # weeks, hours per week, blocked weeks, topic-group order
    return out


def _topic_ids(state: dict) -> set[str]:
    return {t["id"] for m in state.get("modules", []) for t in m["topics"]}


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
    tids = _topic_ids(state)
    for s in labs + plan.get("tutorials", []):
        for t in s.get("uses_topics", []):
            if t not in tids:
                out.append(v("T10", ERR, [s["id"]], f"{s['id']} uses unknown topic {t}"))
            if t in first_week and first_week[t] > s["week"]:
                out.append(v("V19", ERR, [s["id"], t], f"{s['id']} (week {s['week']}) uses topic {t} first taught in week {first_week[t]}"))
        for lo in s.get("practises_los", []):
            if lo not in los:
                out.append(v("T10", ERR, [s["id"]], f"{s['id']} practises unknown LO {lo}"))
    out += constraints.check_stage(state, "labs")         # lab.present, lab.hours_per_week, lab.tools_include
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
    tids = _topic_ids(state)
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
            for when in ("release_week", "due_week"):   # +2: exam weeks after the last teaching week
                if inst[when] > weeks + 2 or inst[when] < 1:
                    out.append(v("VA-TIME", ERR, [inst["id"]], f"{inst['id']} {when.replace('_', ' ')} {inst[when]} outside semester"))
            ref_week = inst["due_week"] if t == "project" else inst["release_week"]   # a project may run alongside teaching
            for tp in inst.get("covers_topics", []):
                if tp not in tids:
                    out.append(v("T10", ERR, [inst["id"]], f"{inst['id']} covers unknown topic {tp}"))
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
            # "after week M": the exam sits at the end of teaching week M or in the following week
            if t == "midsem" and midsem and inst["release_week"] not in (midsem, midsem + 1):
                out.append(v("VA-MIDSEM", WARN, [inst["id"]], f"mid-sem placed in week {inst['release_week']}, calendar assumption is after week {midsem} (week {midsem} or {midsem + 1})"))
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
        if ctype not in types and not any(p.kind == "assessment.component[].present" and p.op == "absent" and p.args
                                          and p.args[0].lower() == ctype for p in constraints.compile_all(state.get("constraints"))):
            out.append(v("VA-REG", WARN, [kid], f"no {ctype} component although UGREG-2025§6.2 normally schedules one"))
    out += constraints.check_stage(state, "assessment")   # component presence / weight / instances, counts
    pr = ped.get("proctored")
    if pr and comps:
        def is_proc(c):
            return c.get("proctored") if c.get("proctored") is not None else str(c["type"]).lower() in pr["types"]
        proc = sum(float(c["weight_pct"]) for c in comps if is_proc(c))
        if proc + 1e-6 < pr["min_pct"]:
            out.append(v("VA-PROCTOR", ERR, [c["type"] for c in comps],
                         f"only {proc:g}% of the grade is proctored evaluation; the IIIT-D template requires at least {pr['min_pct']}%"))
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
    rej = state.get("resources_rejected") or []
    if rej:
        out.append(v("V15", WARN, [], f"{len(rej)} resource(s) removed because no library record matched: "
                                     + "; ".join(str(x.get("title"))[:60] for x in rej)))
    if "resources" in state and len(state["resources"]) < 2:
        out.append(v("V15", WARN, [], f"only {len(state['resources'])} verified resource(s); add sources manually or widen the search"))
    policy = (state.get("resource_policy") or {}).get("textbook_policy")
    if policy in ("textbook", "mixed") and "resources" in state and not any(
            str(r.get("candidate_id", "")).startswith("OL:") or (r.get("identifier") or {}).get("isbn") for r in state["resources"]):
        out.append(v("V15", WARN, [], f"the resource policy is '{policy}' but no verified textbook is listed; add one"))
    out += constraints.check_stage(state, "resources")    # resource.type_allowed, resource.max_age_years
    return out


def check_intake(state: dict) -> list[dict]:
    """S1: the course frame against the regulation, constraints on it (course.credits), and the audience its title names."""
    return regulation.check_regulation(state) + constraints.check_stage(state, "intake") + _audience_checks(state)


# Words that name a broad or beginner audience. "Introduction to" / "Foundations of" are NOT among them: 22 of the 39
# IIIT-D catalogue courses titled "Introduction to ..." are level 5 or 6 (data/stub_kg/index.json, 2026-10-28).
AUDIENCE_RE = re.compile(r"\bfor\s+(all|everyone|everybody|beginners|non[- ]?majors|non[- ]?engineers)\b|\b101\b|\bprimer\b", re.I)


def _audience_checks(state: dict) -> list[dict]:
    """VC-AUDIENCE: the title names a broad audience but the course frame is level 3 or above, which the professor
    should confirm at gate 1 (level and target students are often inferred, not given)."""
    title = (state.get("form") or {}).get("1. COURSE NAME") or ""
    m, level = AUDIENCE_RE.search(title), state.get("level")
    if not m or level is None or int(level) < 3:
        return []
    given = (((state.get("cco") or {}).get("fields") or {}).get("level_or_code") or {}).get("status") == "given"
    return [v("VC-AUDIENCE", WARN, ["level"],
              f"the title says '{m.group(0)}' but the course is level {level} ({'as given' if given else 'inferred, not given'}) "
              f"for {', '.join(state.get('programmes') or []) or 'no programme yet'}; a course for a broad audience is "
              f"usually level 1–2 and open to every programme: confirm the level and the target students",
              level=int(level), audience=m.group(0), level_given=given)]


def check_constraint_set(state: dict) -> list[dict]:
    """S3: hard constraints that conflict, and constraints no checker covers."""
    return constraints.check_constraints(state)


def check_kg(state: dict) -> list[dict]:
    """After S5: the design against facts from the institutional graph (state["kg_facts"], kg/facts.py). Warnings only:
    the graph describes how IIIT-D courses usually are, not rules a new course must follow."""
    kf = state.get("kg_facts")
    if not kf:
        return []
    out = []
    th = pedagogy()["thresholds"]
    first = {tid: min(ws) for tid, ws in (state.get("schedule") or {}).get("topic_weeks", {}).items() if ws}
    for e in kf.get("precedence", []):
        a, b = first.get(e["from"]), first.get(e["to"])
        if a is not None and b is not None and a > b:
            out.append(v("VKG-PREC", WARN, [e["from"], e["to"]],
                         f"'{e['from_title']}' starts in week {a}, after '{e['to_title']}' (week {b}); {e['support']} IIIT-D "
                         f"courses teach it first ({', '.join(e['courses'][:4])}), {e['against']} the other way round",
                         support=e["support"], against=e["against"], courses=e["courses"]))
    pos = state.get("positioning") or {}
    declared = {a["course_uid"] for a in pos.get("anti_requisites", [])} | {p["course_uid"] for p in pos.get("prerequisites", [])}
    for o in kf.get("catalogue_overlap", []):
        if o["weighted_jaccard"] >= th["anti_requisite_overlap"] and o["course_uid"] not in declared:
            out.append(v("VKG-DUP", WARN, [o["course_uid"]],
                         f"topics overlap {o['course_uid']} ({o.get('name') or ''}) at {o['weighted_jaccard']} "
                         f"(≥ {th['anti_requisite_overlap']}), but it is not declared as an anti-requisite: {o['shared_topics'][:4]}",
                         shared_topics=o["shared_topics"]))
    out += _norm_checks(state, kf.get("norms") or {}, th["kg_norms"])
    return out


def _norm_checks(state: dict, n: dict, cfg: dict) -> list[dict]:
    if (n.get("n") or 0) < cfg["min_courses"]:
        return []
    out, lvl = [], f"{n['level']}xx"
    credits = (state.get("defaults") or {}).get("credits")
    if credits is not None:
        share = n["credits"].get(str(credits), 0) / n["n"]
        if share < cfg["rare_credit_share"]:
            out.append(v("VKG-NORM", WARN, ["credits"], f"{credits} credits: {share:.0%} of the {n['n']} level-{lvl} courses "
                                                        f"have that ({n['credits']})", share=round(share, 3)))
    cos = state.get("cos") or []
    bl = [int(c["bloom_level"]) for c in cos if str(c.get("bloom_level", "")).isdigit()]
    comps = (state.get("assessment") or {}).get("components") or []
    for key, what, value in (("co_count", "COs", len(cos) if cos else None), ("bloom_max", "highest CO Bloom level", max(bl) if bl else None),
                             ("components", "assessment components", len(comps) if comps else None)):
        s = n.get(key)
        if value is None or not s or s["n"] < cfg["min_courses"]:
            continue
        if not s["lo"] <= value <= s["hi"]:
            out.append(v("VKG-NORM", WARN, [key], f"{value} {what}: unusual for level {lvl} (IIIT-D median {s['median']:g}, "
                                                  f"usual range {max(s['lo'], 0):g}–{s['hi']:g}, {s['n']} courses)",
                         median=s["median"], lo=s["lo"], hi=s["hi"]))
    return out


STAGE_CHECKS = {
    "intake": [check_intake], "constraints": [check_constraint_set],
    "positioning": [check_positioning], "cos": [check_cos], "copo": [check_copo], "los": [check_los],
    "structure": [check_structure], "schedule": [check_schedule], "labs": [check_labs],
    "assessment": [check_assessment, check_copo_computed], "resources": [check_resources], "kg": [check_kg],
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

