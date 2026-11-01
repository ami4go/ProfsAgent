"""The professor's edits at a waiting check (Context, Outcomes, Final sheet), applied in place and checked again.

At a check the pipeline is paused inside a LangGraph interrupt. When it resumes, the check re-reads
runs/<id>/state.json and design_graph.json (orchestrator/graph.py re-attaches from disk), recomputes its open problems,
and the later stages build on that state. So an edit here:
  1. changes the run state, and the design graph (what goes to Neo4j) the same way the pipeline stage writes it;
  2. runs the same deterministic checks again (validate/engine.check; the core profile makes no AI calls);
  3. gives the gate its new open problems (engine.gate_view), so "Continue" needs no reason once they are gone;
  4. records what changed: state["professor_edits"], and created_by="professor" on the changed design-graph nodes.
On the Final sheet the course documents (proposal, Excel template) are rendered again.
Vihan's pipeline code is unchanged; docs/decisions.md entry 21 proposes a "revise" decision inside the pipeline.

apply(run_dir, gate, section, value, by) -> {"changes": [...], "payload": {...}, "open_before": n, "open_after": n}
raises EditError({field: message}) when the edit can't be applied; nothing is saved then.
"""
from __future__ import annotations

import copy
import json
import re
import time
from pathlib import Path
from types import SimpleNamespace

from profsagent.config import pedagogy
from profsagent.design import deterministic as det
from profsagent.design.store import DesignGraph
from profsagent.validate import engine, rules

PROF = [{"tag": "USER", "ref": "professor edit", "basis": None}]
ASSESS_TYPES = ["quiz", "assignment", "midsem", "endsem", "project", "lab", "presentation", "report", "participation", "other"]
PROCTORED_TYPES = {"midsem", "endsem", "quiz"}
ROLES = {"primary": "Textbook", "reference": "Reference", "reading": "Reading"}   # the roles G10 gives
# results of the stages that write them; "structure" also holds the scheduler's findings
STAGE_RULES = {"structure": ["structure", "schedule"]}


class EditError(ValueError):
    """Problems to show next to the edit form: {field path: message}."""

    def __init__(self, errors: dict[str, str]):
        super().__init__("; ".join(errors.values()))
        self.errors = errors


def _s(v) -> str:
    return re.sub(r"\s+", " ", str(v if v is not None else "")).strip()


def _num(v, what: str, path: str, lo: float, hi: float, errs: dict, integer: bool = False):
    try:
        x = float(str(v).strip())
    except (TypeError, ValueError):
        errs[path] = f"{what}: give a number"
        return None
    if not lo <= x <= hi:
        errs[path] = f"{what}: between {lo:g} and {hi:g}"
        return None
    if integer:
        if not x.is_integer():
            errs[path] = f"{what}: a whole number"
            return None
        return int(x)
    return int(x) if x.is_integer() else round(x, 2)


def _same(a, b) -> bool:
    return json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)


def _next(existing, prefix: str, start: int = 1) -> str:
    """The next free id with this prefix: CO6, TG5, K17, M1.T7 ..."""
    nums = [int(m.group(1)) for x in existing if (m := re.fullmatch(re.escape(prefix) + r"(\d+)", str(x)))]
    return f"{prefix}{max(nums + [start - 1]) + 1}"


def _short(t, n: int = 60) -> str:
    t = _s(t)
    return t if len(t) <= n else t[:n - 1] + "…"


# ------------------------------------------------------------------ design graph helpers
def _sync(g: DesignGraph, label: str, items: dict[str, dict], created_by: str) -> None:
    """Make the graph's `label` nodes equal `items` (local id -> props): unchanged nodes stay as they are, changed and new
    ones are written by `created_by`, missing ones are removed with their links."""
    have = {n["local_id"]: n for n in g.by_label(label)}
    for lid, props in items.items():
        old = have.get(lid)
        if old is not None and _same(old["props"], props):
            continue
        g.put(label, lid, props, created_by=created_by, sources=props.get("sources") or PROF)
    for lid, n in have.items():
        if lid not in items:
            g.remove(n["uid"])


def _relink(g: DesignGraph, rel: str, src_label: str, links: list[tuple]) -> None:
    g.drop_edges(rel, src_label)
    for src, dst, *props in links:
        g.link(src, rel, dst, **(props[0] if props else {}))


# ------------------------------------------------------------------ checks and documents
def recheck(st: dict) -> None:
    """The same deterministic checks the stages ran, on the edited state (only for the stages that have run)."""
    for key in list((st.get("violations") or {})):
        if key in rules.STAGE_CHECKS or key in STAGE_RULES:
            st["violations"][key] = engine.check(st, STAGE_RULES.get(key, [key]))


def gate_payload(st: dict) -> dict:
    v = engine.gate_view(st)
    vs = engine.recorded(st)
    errs = engine.errors(vs)
    return {"blocked": v["blocked"], "open": v["open"], "open_errors": len(errs), "open_warnings": len(vs) - len(errs),
            "report": v["report"], "coverage": v["coverage"]}


def _rerender(run_dir: Path, st: dict) -> str | None:
    """The Final sheet's documents, drawn again from the edited state. Returns a problem, or None."""
    from profsagent.render.proposal import render

    def log(msg: str) -> None:
        with (run_dir / "run.log").open("a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")
    try:
        render(SimpleNamespace(state=st, run_dir=run_dir, run_id=run_dir.name, log=log))
    except Exception as e:  # noqa: BLE001 — the edit is saved either way
        return f"The course sheet could not be drawn again ({type(e).__name__}: {str(e)[:120]})"
    try:
        from profsagent.evaluate.deterministic import evaluate
        ev = evaluate(st)
        (run_dir / "evaluation_deterministic.json").write_text(json.dumps(ev, indent=1, default=str), encoding="utf-8")
        st["evaluation_deterministic"] = ev.get("summary")
    except Exception as e:  # noqa: BLE001
        log(f"evaluation (tier 1) after the professor's edit skipped: {type(e).__name__}")
    pdf = run_dir / "course_sheet.pdf"     # made again from the new state when it is next downloaded
    if pdf.exists():
        pdf.unlink()
    return None


# ================================================================== Context (gate 1)
def _topics(st: dict, g: DesignGraph, value) -> list[str]:
    """value: [{id?, title, topics: [text]}] in order."""
    if not isinstance(value, list):
        raise EditError({"topics": "Send the list of topic groups"})
    old = {tg["id"]: tg for tg in st.get("topic_groups") or []}
    out, errs, changes = [], {}, []
    ids = list(old)
    for i, x in enumerate(value):
        title = _s(x.get("title"))
        texts = [t for t in (_s(t) for t in x.get("topics") or []) if t]
        if not title:
            errs[f"{i}.title"] = "Give the topic group a name"
            continue
        gid = x.get("id") if x.get("id") in old else None
        if gid is None:
            gid = _next(ids, "TG")
            ids.append(gid)
        prev = old.get(gid, {})
        by_text = {t["text"]: t for t in prev.get("topics") or []}
        tids = [t["id"] for t in prev.get("topics") or []]
        items = []
        for text in texts:
            if text in by_text:
                items.append(by_text.pop(text))
            else:
                tid = _next(tids, f"{gid}.")
                tids.append(tid)
                items.append({"id": tid, "text": text})
        out.append({**prev, "id": gid, "title": title, "topics": items})
        if not prev:
            changes.append(f"Topics: added the group “{title}”")
            continue
        if prev.get("title") != title:
            changes.append(f"Topics: renamed “{prev.get('title')}” to “{title}”")
        before = [t["text"] for t in prev.get("topics") or []]
        for t in texts:
            if t not in before:
                changes.append(f"Topics: added “{_short(t)}” to {title}")
        for t in before:
            if t not in texts:
                changes.append(f"Topics: removed “{_short(t)}” from {title}")
        if not changes and [t["id"] for t in items] != [t["id"] for t in prev.get("topics") or []]:
            changes.append(f"Topics: reordered {title}")
    if errs:
        raise EditError(errs)
    kept = {tg["id"] for tg in out}
    changes += [f"Topics: removed the group “{tg['title']}”" for gid, tg in old.items() if gid not in kept]
    if [tg["id"] for tg in out] != [tg["id"] for tg in old.values() if tg["id"] in kept] and not changes:
        changes.append("Topics: reordered the groups")
    if not changes:
        return []
    st["topic_groups"] = out
    st["cco_compact"]["topic_groups"] = copy.deepcopy(out)
    fields = (st.get("cco") or {}).get("fields") or {}
    if isinstance(fields.get("topics"), dict):
        fields["topics"]["topic_groups"] = copy.deepcopy(out)
    for p in (st.get("positioning") or {}).get("prerequisites") or []:
        if p.get("needed_by"):
            p["needed_by"] = [t for t in p["needed_by"] if t in kept]
    _sync(g, "TopicGroup", {tg["id"]: tg for tg in out}, "professor")
    return changes


EDITABLE_ASSUMPTIONS = ("course level", "mid-semester exam timing")


def _assumptions(st: dict, g: DesignGraph, value) -> list[str]:
    """value: [{id, value?, confirm?}]. Course level and mid-sem week can be changed; every assumption can be confirmed."""
    asm = {a["id"]: a for a in (st.get("defaults") or {}).get("assumptions") or []}
    errs, changes = {}, []
    for i, x in enumerate(value or []):
        a = asm.get(x.get("id"))
        if not a:
            continue
        new = x.get("value")
        if a["what"] == "course level" and new not in (None, ""):
            levels = sorted(int(k) for k in pedagogy()["bloom_bands"])
            lvl = _num(new, "Course level", f"{i}.value", min(levels), max(levels), errs, integer=True)
            if lvl is not None and lvl != st.get("level"):
                st["level"] = st["defaults"]["level"] = st["cco_compact"]["level"] = lvl
                st["bloom_band"] = det.bloom_band(lvl)
                a.update(value=lvl, status="set by professor")
                if g.get("COURSE"):
                    g.update("COURSE", "level", lvl, "professor")
                changes.append(f"Course level set to {lvl} (Bloom levels {st['bloom_band']['floor']}–{st['bloom_band']['ceiling']})")
                continue
        if a["what"] == "mid-semester exam timing" and new not in (None, ""):
            wk = _num(re.sub(r"\D", "", str(new)) or new, "Mid-sem week", f"{i}.value", 1, int(st.get("weeks") or 13) - 1, errs, integer=True)
            if wk is not None and wk != st.get("midsem_after_week"):
                st["midsem_after_week"] = st["defaults"]["midsem_after_week"] = wk
                for c in st.get("constraints") or []:
                    if c.get("target") == "schedule.midsem_after_week":   # stays a template rule, now with the professor's week
                        c["value"] = wk
                        c["note"] = "week set by the professor at the Context check"
                a.update(value=f"after teaching week {wk}", status="set by professor")
                changes.append(f"Mid-sem exam set to after teaching week {wk}")
                continue
        if x.get("confirm") and a.get("status") == "open":
            a["status"] = "confirmed"
            changes.append(f"Confirmed: {a['what']} = {a['value']}")
    if errs:
        raise EditError(errs)
    if changes:
        _sync(g, "Assumption", {a["id"]: a for a in st["defaults"]["assumptions"]}, "professor")
        _sync(g, "Constraint", {c["id"]: c for c in st.get("constraints") or []}, "professor")
    return changes


def locked_rules(st: dict) -> set[str]:
    """The course frame (weeks, credits, L-T-P, lab hours, exams, mid-sem week): rules S1 made from the Details form and
    the regulations (deterministic.apply_defaults). They change only in the Details step, or as an assumption above."""
    return {c["id"] for c in (st.get("defaults") or {}).get("constraints") or []}


def _content_kind(c: dict) -> str | None:
    m = re.match(r"content\.must_(include|exclude)\[", c.get("target") or "")
    return m.group(1) if m else None


def _inner(c: dict) -> str:
    m = re.search(r"\[(.+)\]$", c.get("target") or "")
    return m.group(1) if m else ""


def _wishes(st: dict, g: DesignGraph, value) -> list[str]:
    """The rules made from the professor's own words. value: [{ids: [K..], kind: include|exclude, text, hard}].
    Missing ids are deleted; new entries (no ids) become new include / exclude rules."""
    from profsagent.app.views import rule_text
    cons = st.get("constraints") or []
    frame = locked_rules(st)
    user = {c["id"]: c for c in cons if (c.get("source") or {}).get("tag") == "USER" and c["id"] not in frame}
    kept, errs, changes = set(), {}, []
    ids_all = [c["id"] for c in cons]
    for i, x in enumerate(value or []):
        hard = "hard" if x.get("hard", True) else "soft"
        text = _s(x.get("text"))
        if x.get("ids"):          # an existing rule (course-frame rules in it are left as they are)
            ids = [k for k in x["ids"] if k in user]
            kept |= set(ids)
            for k in ids:
                c = user[k]
                label = rule_text(c)[0]
                if _content_kind(c) and text and text != _inner(c):   # the edit box shows the phrase that is checked
                    c["target"] = f"content.must_{_content_kind(c)}[{text}]"
                    c["raw"] = text
                    c["source"] = {**PROF[0]}
                    changes.append(f"Rule {k} reworded: “{_short(label)}” → “{_short(text)}”")
                if c.get("hardness") != hard:
                    c["hardness"] = hard
                    changes.append(f"Rule {k} is now {'a must' if hard == 'hard' else 'a preference'}: “{_short(rule_text(c)[0])}”")
            continue
        kind = x.get("kind")
        if not text:
            errs[f"{i}.text"] = "Write the rule, or remove the empty line"
            continue
        if kind not in ("include", "exclude"):
            errs[f"{i}.kind"] = "Choose whether the course must include it or must not become it"
            continue
        k = _next(ids_all, "K", start=10)
        ids_all.append(k)
        cons.append({"id": k, "target": f"content.must_{kind}[{text}]", "op": "==", "value": True, "hardness": hard, "raw": text,
                     "source": {**PROF[0]}, "note": "added by the professor at the Context check"})
        kept.add(k)
        changes.append(f"Rule {k} added: {'must include' if kind == 'include' else 'must not become'} “{_short(text)}”")
    if errs:
        raise EditError(errs)
    for k, c in user.items():
        if k not in kept:
            cons.remove(c)
            changes.append(f"Rule {k} removed: “{_short(rule_text(c)[0])}”")
    if changes:
        st["constraints"] = cons
        gone = set(user) - kept
        if gone and st.get("constraint_conflicts"):   # the AI's own conflict notes that name a removed rule no longer apply
            st["constraint_conflicts"] = [x for x in st["constraint_conflicts"] if not (set(re.findall(r"\bK\d+\b", json.dumps(x))) & gone)]
        _sync(g, "Constraint", {c["id"]: c for c in cons}, "professor")
    return changes


def _prerequisites(st: dict, g: DesignGraph, value) -> list[str]:
    """value: [{code, kind: mandatory|desirable}]."""
    from profsagent.app.views import course_ref
    pos = st.setdefault("positioning", {})
    old = {p["course_uid"]: p for p in pos.get("prerequisites") or []}
    known = {u.upper() for u in st.get("known_course_uids") or []}
    out, errs, changes, seen = [], {}, [], set()
    for i, x in enumerate(value or []):
        code = re.sub(r"\s+", "", _s(x.get("code"))).upper()
        if not code or code in seen:
            continue
        seen.add(code)
        kind = "desirable" if x.get("kind") == "desirable" else "mandatory"
        if code not in old and known and code not in known:
            errs[f"{i}.code"] = f"{code} isn't in the IIIT-D course database"
            continue
        if code in old:
            p = old[code]
            if p.get("kind") != kind:
                changes.append(f"{code} is now {'a prerequisite' if kind == 'mandatory' else 'recommended'}")
                p["kind"] = kind
            out.append(p)
        else:
            out.append({"kind": kind, "course_uid": code, "alternatives": [], "relied_topics": [], "needed_by": [],
                        "justification": "Added by the professor at the Context check", "level_check": None, "sources": PROF})
            name = course_ref(code).get("name")
            changes.append(f"Added {'prerequisite' if kind == 'mandatory' else 'recommended course'} {code}" + (f" {name}" if name else ""))
    if errs:
        raise EditError(errs)
    changes += [f"Removed prerequisite {u}" for u in old if u not in seen]
    if changes:
        pos["prerequisites"] = out
        _relink(g, "REQUIRES", "NewCourse", [("COURSE", p["course_uid"], {"kind": p["kind"], "relied_topics": p.get("relied_topics") or [],
                                                                            "justification": p.get("justification")}) for p in out])
    return changes


# ================================================================== Outcomes (gate 2)
def _parts(statement: str) -> tuple[str, str]:
    """(verb, behaviour) of an outcome statement: its first word, and the rest of its first clause."""
    words = statement.split(None, 1)
    verb = re.sub(r"[^A-Za-z-]", "", words[0]).lower() if words else ""
    rest = words[1] if len(words) > 1 else ""
    return verb, rest.split(",")[0].strip().rstrip(".")


def _outcome_fields(x: dict, path: str, errs: dict, kind: str) -> dict:
    out = {}
    st_ = _s(x.get("statement"))
    if len(st_.split()) < 3:
        errs[f"{path}.statement"] = f"Write the {kind} as a sentence that starts with a verb"
    out["statement"] = st_
    out["verb"], out["behaviour"] = _parts(st_)
    lvl = _num(x.get("bloom_level"), "Bloom level", f"{path}.bloom_level", 1, 6, errs, integer=True)
    out["bloom_level"] = lvl
    for k in ("condition", "degree"):
        if k in x:
            out[k] = _s(x.get(k))
    return out


def _co(st: dict, g: DesignGraph, value) -> list[str]:
    """One course outcome with its learning outcomes and programme-outcome links.
    value: {id?, statement, bloom_level, condition, degree, covers_topic_groups, evidence_types,
            los: [{id?, statement, bloom_level, condition, degree, suggested_task_type}], pos: [{po_uid, strength}]}"""
    errs, changes = {}, []
    cos, los, copo = st["cos"], st["los"], st.get("copo") or []
    cid = value.get("id") if any(c["id"] == value.get("id") for c in cos) else None
    co = next((c for c in cos if c["id"] == cid), None)
    f = _outcome_fields(value, "co", errs, "outcome")
    tgs = {tg["id"] for tg in st.get("topic_groups") or []}
    f["covers_topic_groups"] = [t for t in value.get("covers_topic_groups") or [] if t in tgs]
    vocab = pedagogy()["assessment_evidence_types"]
    f["evidence_types"] = [e for e in value.get("evidence_types") or [] if e in vocab]
    if len(f.get("condition") or "") < 4:
        errs["co.condition"] = "Say under what conditions (e.g. “given a small web application”)"
    if len(f.get("degree") or "") < 4:
        errs["co.degree"] = "Say to what standard (e.g. “so that all its tests pass”)"
    po_uids = {p["uid"] for p in st.get("programme_pos") or []}
    pos = []
    for j, p in enumerate(value.get("pos") or []):
        s = _num(p.get("strength"), "Strength", f"pos.{j}.strength", 0, 3, errs, integer=True)
        if p.get("po_uid") in po_uids and s:
            pos.append((p["po_uid"], s))
    new_los = []
    for j, x in enumerate(value.get("los") or []):
        lf = _outcome_fields(x, f"los.{j}", errs, "learning outcome")
        if x.get("suggested_task_type") in vocab:
            lf["suggested_task_type"] = x["suggested_task_type"]
        new_los.append((x.get("id"), lf))
    if errs:
        raise EditError(errs)

    if co is None:
        cid = _next([c["id"] for c in cos], "CO")
        co = {"id": cid, "knowledge_dimension": None, "builds_on_prereq_topics": [], "differentiation_note": None, "nc_risks": [],
              "rationale": "Written by the professor at the Outcomes check", "sources": PROF}
        cos.append(co)
        changes.append(f"{cid} added: “{_short(f['statement'])}”")
    else:
        if co.get("statement") != f["statement"]:
            changes.append(f"{cid} reworded: “{_short(co.get('statement'))}” → “{_short(f['statement'])}”")
        if co.get("bloom_level") != f["bloom_level"]:
            changes.append(f"{cid} Bloom level {co.get('bloom_level')} → {f['bloom_level']}")
        for k, what in (("condition", "condition"), ("degree", "standard"), ("covers_topic_groups", "topic groups"), ("evidence_types", "evidence")):
            if not _same(co.get(k), f.get(k)):
                changes.append(f"{cid} {what} changed")
    co.update(f)

    # learning outcomes of this CO
    mine = {lo["id"]: lo for lo in los if lo.get("parent_co") == cid}
    kept = []
    for lid, lf in new_los:
        lo = mine.get(lid)
        if lo is None:
            lid = _next([x["id"] for x in los], f"{cid}.LO")
            task = lf.get("suggested_task_type") or "exam_question"
            lo = {"id": lid, "parent_co": cid, "knowledge_dimension": None, "is_capstone": False, "requires": [], "topic_hints": [],
                  "hands_on": task in ("programming_assignment", "lab_task", "project_deliverable"), "est_lecture_h": 1.5,
                  "est_tutorial_h": 0.0, "est_lab_h": 0.0, "hours_basis": "set by the professor (default 1.5 h)",
                  "suggested_task_type": task, "condition": "", "degree": "", "sources": PROF}
            los.append(lo)
            changes.append(f"{lid} added: “{_short(lf['statement'])}”")
        else:
            if lo.get("statement") != lf["statement"]:
                changes.append(f"{lid} reworded: “{_short(lo.get('statement'))}” → “{_short(lf['statement'])}”")
            if lo.get("bloom_level") != lf["bloom_level"]:
                changes.append(f"{lid} Bloom level {lo.get('bloom_level')} → {lf['bloom_level']}")
            for k in ("condition", "degree", "suggested_task_type"):
                if k in lf and lo.get(k) != lf[k]:
                    changes.append(f"{lid} {'standard' if k == 'degree' else k.replace('_', ' ')} changed")
        lo.update({k: v for k, v in lf.items() if v is not None})
        kept.append(lid)
    gone = [lid for lid in mine if lid not in kept]
    for lid in gone:
        changes.append(f"{lid} removed: “{_short(mine[lid].get('statement'))}”")
    _drop_los(st, set(gone))

    # programme outcomes this CO supports
    before = {m["po_uid"]: m for m in copo if m["co_id"] == cid}
    po_text = {p["uid"]: p.get("text") or "" for p in st.get("programme_pos") or []}
    mapped = []
    for uid, s in pos:
        m = before.get(uid) or {"co_id": cid, "po_uid": uid, "co_phrase": co["statement"], "po_phrase": po_text.get(uid, "").split(":")[0],
                                "justification": "Set by the professor at the Outcomes check", "evidencing_activities": []}
        if uid not in before:
            changes.append(f"{cid} now supports {uid} (strength {s})")
        elif before[uid].get("strength_provisional") != s:
            changes.append(f"{cid} → {uid} strength {before[uid].get('strength_provisional')} → {s}")
        mapped.append({**m, "strength_provisional": s})
    changes += [f"{cid} no longer supports {uid}" for uid in before if uid not in dict(pos)]
    st["copo"] = [m for m in copo if m["co_id"] != cid] + mapped
    if changes:
        _sync_outcomes(g, st)
    return changes


def _drop_los(st: dict, gone: set[str]) -> None:
    if not gone:
        return
    st["los"] = [lo for lo in st["los"] if lo["id"] not in gone]
    for lo in st["los"]:
        lo["requires"] = [r for r in lo.get("requires") or [] if r not in gone]


def _co_delete(st: dict, g: DesignGraph, value) -> list[str]:
    cid = (value or {}).get("id")
    co = next((c for c in st["cos"] if c["id"] == cid), None)
    if co is None:
        raise EditError({"co": "That course outcome no longer exists. Reload the page."})
    st["cos"].remove(co)
    gone = {lo["id"] for lo in st["los"] if lo.get("parent_co") == cid}
    _drop_los(st, gone)
    st["copo"] = [m for m in st.get("copo") or [] if m["co_id"] != cid]
    _sync_outcomes(g, st)
    return [f"{cid} removed, with its {len(gone)} learning outcome{'' if len(gone) == 1 else 's'}: “{_short(co.get('statement'))}”"]


def _proposals(st: dict, g: DesignGraph, value) -> list[str]:
    """value: {reject: [index]}: topic changes the AI proposed that the professor does not want."""
    props = st.get("topic_group_proposals") or []
    drop = sorted({int(i) for i in (value or {}).get("reject") or [] if str(i).isdigit() and int(i) < len(props)}, reverse=True)
    changes = []
    for i in drop:
        p = props.pop(i)
        changes.append(f"Rejected the proposal to {p.get('action')} {', '.join(p.get('targets') or [])}: “{_short(p.get('proposal'))}”")
    return changes


def _sync_outcomes(g: DesignGraph, st: dict) -> None:
    _sync(g, "CO", {c["id"]: c for c in st["cos"]}, "professor")
    _sync(g, "LO", {lo["id"]: lo for lo in st["los"]}, "professor")
    _relink(g, "COVERS_GROUP", "CO", [(c["id"], tg) for c in st["cos"] for tg in c.get("covers_topic_groups") or []])
    _relink(g, "DECOMPOSES_INTO", "CO", [(lo["parent_co"], lo["id"]) for lo in st["los"]])
    _relink(g, "REQUIRES", "LO", [(lo["id"], r) for lo in st["los"] for r in lo.get("requires") or []])
    _relink(g, "MAPS_TO", "CO", [(m["co_id"], m["po_uid"], {"strength_provisional": m["strength_provisional"], "justification": m.get("justification"),
                                                           "evidencing_activities": m.get("evidencing_activities") or []}) for m in st.get("copo") or []])


# ================================================================== Final sheet (gate 3)
def _weeks(st: dict, g: DesignGraph, value) -> list[str]:
    """The modules and their topics, in teaching order. value: [{id?, title, topics: [{id?, title, hours, serves_los}]}].
    The weekly plan is then made again by the pipeline's own scheduler (design/deterministic.schedule)."""
    old_m = {m["id"]: m for m in st.get("modules") or []}
    old_t = {t["id"]: t for m in old_m.values() for t in m["topics"]}
    lo_ids = {lo["id"] for lo in st.get("los") or []}
    errs, changes, mods = {}, [], []
    mids, tids = list(old_m), list(old_t)
    for i, x in enumerate(value or []):
        title = _s(x.get("title"))
        if not title:
            errs[f"{i}.title"] = "Give the module a name"
        mid = x.get("id") if x.get("id") in old_m else None
        if mid is None:
            mid = _next(mids, "M")
            mids.append(mid)
            changes.append(f"Module {mid} added: “{title}”")
        elif old_m[mid]["title"] != title:
            changes.append(f"Module {mid} renamed: “{old_m[mid]['title']}” → “{title}”")
        prev = old_m.get(mid, {"id": mid, "primary_cos": []})
        topics = []
        for j, y in enumerate(x.get("topics") or []):
            tt = _s(y.get("title"))
            path = f"{i}.topics.{j}"
            if not tt:
                errs[f"{path}.title"] = "Give the topic a name"
            hours = _num(y.get("hours"), "Hours", f"{path}.hours", 0.5, 20, errs)
            serves = [s for s in (_s(s).upper().replace(" ", "") for s in (y.get("serves_los") if isinstance(y.get("serves_los"), list)
                                                                        else str(y.get("serves_los") or "").split(","))) if s]
            bad = [s for s in serves if s not in {x.upper() for x in lo_ids}]
            if bad:
                errs[f"{path}.serves_los"] = f"Unknown learning outcome{'s' if len(bad) > 1 else ''}: {', '.join(bad)}"
            serves = [next(x for x in lo_ids if x.upper() == s) for s in serves if s not in bad]
            tid = y.get("id") if y.get("id") in old_t else None
            if tid is None:
                tid = _next(tids, f"{mid}.T")
                tids.append(tid)
                t = {"id": tid, "hours_basis": "set by the professor", "covers_topic_groups": [], "requires": [], "topic_uid": None,
                     "hands_on": False, "outside_load_hours": 0.0, "sources": PROF}
                changes.append(f"Topic added to {mid}: “{tt}” ({hours} h)")
            else:
                t = dict(old_t[tid])
                if t["title"] != tt:
                    changes.append(f"Topic {tid} renamed: “{_short(t['title'])}” → “{_short(tt)}”")
                if t.get("est_hours") != hours:
                    changes.append(f"Topic {tid} hours {t.get('est_hours')} → {hours}")
                if sorted(t.get("serves_los") or []) != sorted(serves):
                    changes.append(f"Topic {tid} now teaches {', '.join(serves) or 'no learning outcome'}")
            t.update(title=tt, est_hours=hours, serves_los=serves, suggested_order=j + 1)
            topics.append(t)
        mods.append({**prev, "id": mid, "title": title, "order": i + 1, "topics": topics})
    if errs:
        raise EditError(errs)
    new_ids = [t["id"] for m in mods for t in m["topics"]]
    gone = {tid for tid in old_t if tid not in new_ids}
    changes += [f"Topic {tid} removed: “{_short(old_t[tid]['title'])}”" for tid in gone]
    changes += [f"Module {mid} removed" for mid in old_m if mid not in {m["id"] for m in mods}]
    if not changes and new_ids != [t["id"] for m in old_m.values() for t in m["topics"]]:
        changes.append("Topics reordered")
    if not changes:
        return []
    for m in mods:
        for t in m["topics"]:
            t["requires"] = [r for r in t.get("requires") or [] if r not in gone]
    for c in (st.get("assessment") or {}).get("components") or []:
        for inst in c.get("instances") or []:
            inst["covers_topics"] = [t for t in inst.get("covers_topics") or [] if t not in gone]
    for kind in ("labs", "tutorials"):
        for s_ in (st.get("labs_tutorials") or {}).get(kind) or []:
            s_["uses_topics"] = [t for t in s_.get("uses_topics") or [] if t not in gone]
    for r in st.get("resources") or []:
        r["supports_topics"] = [x for x in r.get("supports_topics") or [] if x.get("topic_id") not in gone]
    st["modules"] = mods
    flat = [{**t, "module_order": m["order"]} for m in mods for t in m["topics"]]
    st["schedule"] = det.schedule(flat, st["weeks"], st["ltp"]["L"], st["midsem_after_week"])
    st.setdefault("structure_meta", {})["hours_total"] = round(sum(t["est_hours"] for t in flat), 2)
    s = st["schedule"]
    changes.append(f"Weekly plan made again: {s['hours_needed']} of {s['hours_available']} lecture hours"
                   + ("" if s["feasible"] else " (does not fit)"))
    _sync_plan(g, st)
    return changes


def _labs(st: dict, g: DesignGraph, value) -> list[str]:
    """value: [{id?, title, week}]."""
    lt = st.setdefault("labs_tutorials", {})
    old = {l_["id"]: l_ for l_ in lt.get("labs") or []}
    weeks = int(st.get("weeks") or 13)
    errs, changes, out, ids = {}, [], [], list(old)
    for i, x in enumerate(value or []):
        title = _s(x.get("title"))
        if not title:
            errs[f"{i}.title"] = "Say what the lab is about"
        wk = _num(x.get("week"), "Week", f"{i}.week", 1, weeks, errs, integer=True)
        lid = x.get("id") if x.get("id") in old else None
        if lid is None:
            lid = f"W{(wk or 0):02d}.LAB" if f"W{(wk or 0):02d}.LAB" not in ids else _next(ids, f"W{(wk or 0):02d}.LAB", start=2)
            ids.append(lid)
            lab = {"id": lid, "exercise": title, "practises_los": [], "uses_topics": [], "tools": [], "hours": float(st["ltp"].get("P") or 2),
                   "produces_assessed_artifact": None, "notes": "added by the professor"}
            changes.append(f"Lab added in week {wk}: “{_short(title)}”")
        else:
            lab = dict(old[lid])
            if lab.get("title") != title:
                changes.append(f"Lab {lid} renamed: “{_short(lab.get('title'))}” → “{_short(title)}”")
            if lab.get("week") != wk:
                changes.append(f"Lab {lid} moved to week {wk}")
        lab.update(title=title, week=wk)
        out.append(lab)
    if errs:
        raise EditError(errs)
    changes += [f"Lab {lid} removed: “{_short(old[lid].get('title'))}”" for lid in old if lid not in {x["id"] for x in out}]
    if changes:
        lt["labs"] = sorted(out, key=lambda x: (x["week"], x["id"]))
        _sync_plan(g, st)
    return changes


def _refit_marks(st: dict) -> None:
    ped = pedagogy()
    comps = st["assessment"]["components"]
    lo_parent = {lo["id"]: lo["parent_co"] for lo in st["los"]}
    st["assessment"]["weight_sum"] = round(sum(c["weight_pct"] for c in comps), 2)
    st["co_marks_share"] = det.co_marks_share(lo_parent, comps)
    st["copo_computed"] = det.copo_strengths([c["id"] for c in st["cos"]], lo_parent, comps, st.get("activity_po_map") or {}, st.get("copo") or [],
                                             ped["thresholds"]["co_po_strength"])


def _assessment(st: dict, g: DesignGraph, value) -> list[str]:
    """value: [{key?, type, weight, invigilated, due: [week per instance]}]; key = the component's position as shown."""
    from profsagent.app.views import ASSESS
    old = (st.get("assessment") or {}).get("components") or []
    weeks = int(st.get("weeks") or 13)
    errs, changes, out = {}, [], []
    used = set()
    for i, x in enumerate(value or []):
        key = x.get("key")
        c = copy.deepcopy(old[key]) if isinstance(key, int) and 0 <= key < len(old) else None
        typ = c["type"] if c else x.get("type")
        if typ not in ASSESS_TYPES:
            errs[f"{i}.type"] = "Choose the kind of assessment"
            continue
        w = _num(x.get("weight"), "Weight", f"{i}.weight", 0, 100, errs)
        due = []
        for j, d in enumerate(x.get("due") or []):
            wk = _num(d, "Week", f"{i}.due.{j}", 1, weeks, errs, integer=True)
            due.append(wk)
        name = ASSESS.get(typ, typ)
        proctored = bool(x.get("invigilated"))
        if c is None:
            wk = due[0] if due and due[0] else weeks
            topic_last, lo_last = rules._topic_last_week(st), rules._lo_last_week(st)
            los = sorted(lo for lo, last in lo_last.items() if last <= wk)
            share = round(100 / len(los), 2) if los else 0
            lvl = {lo["id"]: lo["bloom_level"] for lo in st["los"]}
            c = {"type": typ, "weight_justification": "set by the professor", "best_k": None, "n": None, "activity_types": [], "integrity": None,
                 "instances": [{"id": _next([z["id"] for k in old + out for z in k.get("instances") or []], f"A:{typ.upper()}"),
                                "release_week": wk, "due_week": wk, "format": name,
                                "covers_topics": sorted(t for t, last in topic_last.items() if last <= wk),
                                "assesses": [{"lo_id": lo, "marks_pct_of_instance": share, "bloom_level": lvl.get(lo)} for lo in los],
                                "est_student_hours": None, "feeds_from_lab": None}]}
            changes.append(f"Assessment added: {name}, {w}%, week {wk}" + (" (invigilated)" if proctored else ""))
        else:
            used.add(key)
            if c.get("weight_pct") != w:
                changes.append(f"{name}: weight {c.get('weight_pct')}% → {w}%")
            if bool(c.get("proctored")) != proctored:
                changes.append(f"{name}: {'invigilated' if proctored else 'not invigilated'}")
            for inst, wk in zip(c.get("instances") or [], due):
                if wk and inst.get("due_week") != wk:
                    changes.append(f"{name} {inst['id']}: due week {inst.get('due_week')} → {wk}")
                    inst["due_week"] = wk
                    inst["release_week"] = min(inst.get("release_week") or wk, wk)
        c.update(weight_pct=w, proctored=proctored)
        out.append(c)
    if errs:
        raise EditError(errs)
    changes += [f"Assessment removed: {ASSESS.get(c['type'], c['type'])} ({c.get('weight_pct')}%)" for k, c in enumerate(old) if k not in used]
    if changes:
        st["assessment"]["components"] = out
        _refit_marks(st)
        total = st["assessment"]["weight_sum"]
        if total != 100:
            changes.append(f"Weights now add up to {total:g}%, not 100%")
        _sync_plan(g, st)
    return changes


def _lookup(ident: str) -> dict | None:
    """A book by ISBN (OpenLibrary) or a paper by DOI (Crossref), as a resource record; None if not found."""
    from profsagent.research.resources import _cached_get, _year_of
    s = ident.strip()
    doi = re.search(r"(10\.\d{4,9}/\S+)", s)
    if doi:
        d = doi.group(1).rstrip(".")
        rec = ((_cached_get(f"https://api.crossref.org/works/{d}", {}) or {}).get("message")) or None
        if not rec or not (rec.get("title") or [None])[0]:
            return None
        year = ((rec.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        return {"candidate_id": f"DOI:{d}", "title": rec["title"][0], "year": year,
                "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in rec.get("author") or []][:8],
                "venue": (rec.get("container-title") or [None])[0], "identifier": {"isbn": None, "doi": d, "arxiv": None, "url": f"https://doi.org/{d}"}}
    isbn = re.sub(r"[^0-9Xx]", "", s).upper()
    if len(isbn) not in (10, 13):
        return None
    rec = _cached_get(f"https://openlibrary.org/isbn/{isbn}.json", {})
    if not rec or not rec.get("title"):
        return None
    authors = []
    for a in (rec.get("authors") or [])[:6]:
        ar = _cached_get(f"https://openlibrary.org{a.get('key')}.json", {}) if a.get("key") else None
        if ar and ar.get("name"):
            authors.append(ar["name"])
    if not authors and (rec.get("works") or [{}])[0].get("key"):
        w = _cached_get(f"https://openlibrary.org{rec['works'][0]['key']}.json", {}) or {}
        for a in (w.get("authors") or [])[:6]:
            ar = _cached_get(f"https://openlibrary.org{(a.get('author') or {}).get('key')}.json", {})
            if ar and ar.get("name"):
                authors.append(ar["name"])
    title = f"{rec['title']}: {rec['subtitle']}" if rec.get("subtitle") else rec["title"]
    return {"candidate_id": f"ISBN:{isbn}", "title": title, "year": _year_of(rec.get("publish_date")), "authors": authors,
            "venue": ", ".join(rec.get("publishers") or []) or None,
            "identifier": {"isbn": isbn, "doi": None, "arxiv": None, "url": f"https://openlibrary.org/isbn/{isbn}"}}


def _books(st: dict, g: DesignGraph, value) -> list[str]:
    """value: [{id, role}] for the books kept, and [{ident, role}] for books to add by ISBN or DOI."""
    old = {r["candidate_id"]: r for r in st.get("resources") or []}
    errs, changes, out, seen = {}, [], [], set()
    for i, x in enumerate(value or []):
        role = x.get("role") if x.get("role") in ROLES else (old.get(x.get("id")) or {}).get("role") or "reference"
        if x.get("id") in old:
            r = old[x["id"]]
            if r.get("role") != role:
                changes.append(f"“{_short(r['title'])}” is now a {ROLES[role].lower()}")
                r = {**r, "role": role}
            out.append(r)
            seen.add(x["id"])
            continue
        ident = _s(x.get("ident"))
        if not ident:
            continue
        rec = _lookup(ident)
        if rec is None:
            errs[f"{i}.ident"] = f"Nothing found online for “{ident}”. Check the ISBN or DOI."
            continue
        if rec["candidate_id"] in old or rec["candidate_id"] in seen:
            errs[f"{i}.ident"] = f"“{_short(rec['title'])}” is already on the list"
            continue
        seen.add(rec["candidate_id"])
        out.append({**rec, "role": role, "edition": None, "supports_topics": [], "sources": PROF,
                    "verification": {"verified": True, "problems": []}, "matched_from": "added by the professor; record looked up online"})
        changes.append(f"Added {ROLES[role].lower()} “{_short(rec['title'])}” ({rec['identifier']['isbn'] and 'ISBN ' + rec['identifier']['isbn'] or 'DOI ' + rec['identifier']['doi']})")
    if errs:
        raise EditError(errs)
    changes += [f"Removed “{_short(r['title'])}”" for cid, r in old.items() if cid not in seen]
    if changes:
        st["resources"] = out
        _sync_plan(g, st)
    return changes


def _description(st: dict, g: DesignGraph, value) -> list[str]:
    text = _s((value or {}).get("text"))
    if len(text.split()) < 10:
        raise EditError({"text": "Write at least a couple of sentences"})
    nar = st.setdefault("narrative", {})
    if nar.get("course_description") == text:
        return []
    nar["course_description"] = text
    return ["Course description rewritten"]


def _sync_plan(g: DesignGraph, st: dict) -> None:
    """The plan part of the design graph made equal to the state again, as S5–S8 write it (pipeline.py)."""
    ltp = st["ltp"]
    mods = st.get("modules") or []
    topics = {t["id"]: t for m in mods for t in m["topics"]}
    _sync(g, "Module", {m["id"]: {k: m.get(k) for k in ("title", "order", "primary_cos")} for m in mods}, "professor")
    _sync(g, "CourseTopic", topics, "professor")
    weeks, lectures, delivered, in_week = {}, {}, [], []
    for w in (st.get("schedule") or {}).get("weeks") or []:
        wid = f"W{w['week']:02d}"
        weeks[wid] = {"n": w["week"], "lecture_hours": ltp["L"], "tutorial_hours": ltp["T"], "lab_hours": ltp["P"],
                      "is_midsem_boundary": w["is_midsem_boundary"]}
        for i, it in enumerate(w["items"], 1):
            lid = f"{wid}.L{i}"
            lectures[lid] = {"slot": i, "hours": it["hours"]}
            in_week.append((lid, wid))
            delivered.append((it["topic_id"], lid, {"hours": it["hours"]}))
    _sync(g, "Week", weeks, "S6-scheduler")
    _sync(g, "Lecture", lectures, "S6-scheduler")
    _relink(g, "CONTAINS", "Module", [(m["id"], t["id"], {"order": t.get("suggested_order")}) for m in mods for t in m["topics"]])
    _relink(g, "TAUGHT_VIA", "LO", [(lo, t["id"]) for t in topics.values() for lo in t.get("serves_los") or []])
    _relink(g, "REQUIRES", "CourseTopic", [(t["id"], r) for t in topics.values() for r in t.get("requires") or []])
    _relink(g, "SAME_AS", "CourseTopic", [(t["id"], t["topic_uid"]) for t in topics.values() if t.get("topic_uid")])
    _relink(g, "IN_WEEK", "Lecture", in_week)
    _relink(g, "DELIVERED_IN", "CourseTopic", delivered)
    lt = st.get("labs_tutorials") or {}
    _sync(g, "LabSession", {x["id"]: x for x in lt.get("labs") or []}, "professor")
    _sync(g, "Tutorial", {x["id"]: x for x in lt.get("tutorials") or []}, "professor")
    _relink(g, "IN_WEEK", "LabSession", [(x["id"], f"W{x['week']:02d}") for x in lt.get("labs") or []])
    _relink(g, "IN_WEEK", "Tutorial", [(x["id"], f"W{x['week']:02d}") for x in lt.get("tutorials") or []])
    _relink(g, "PRACTISED_IN", "LO", [(lo, x["id"]) for x in lt.get("labs") or [] for lo in x.get("practises_los") or []])
    comps = (st.get("assessment") or {}).get("components") or []
    insts = [(c, i) for c in comps for i in c.get("instances") or []]
    _sync(g, "Assessment", {i["id"]: {**i, "type": c["type"], "component_weight_pct": c["weight_pct"], "activity_types": c.get("activity_types") or []}
                            for c, i in insts}, "professor")
    _relink(g, "RELEASED_IN", "Assessment", [(i["id"], f"W{i['release_week']:02d}") for _, i in insts])
    _relink(g, "DUE_IN", "Assessment", [(i["id"], f"W{i['due_week']:02d}") for _, i in insts])
    _relink(g, "ASSESSES", "Assessment", [(i["id"], a["lo_id"], {"marks_pct": a.get("marks_pct_of_instance"), "bloom_level": a.get("bloom_level")})
                                          for _, i in insts for a in i.get("assesses") or []])
    _relink(g, "COVERS", "Assessment", [(i["id"], t) for _, i in insts for t in i.get("covers_topics") or []])
    for r in st.get("copo_computed") or []:
        for e in g.out(r["co_id"], "MAPS_TO"):
            if e["dst"] == r["po_uid"]:
                e["props"].update(strength_computed=r.get("strength_computed"), share=r.get("share"))
    res = st.get("resources") or []
    _sync(g, "Resource", {f"RES:{r['candidate_id']}": r for r in res}, "professor")
    _relink(g, "READING", "CourseTopic", [(s_["topic_id"], f"RES:{r['candidate_id']}") for r in res for s_ in r.get("supports_topics") or []
                                          if s_.get("topic_id") in topics])


# ================================================================== entry point
SECTIONS = {
    "gate1_context": {"topics": _topics, "assumptions": _assumptions, "wishes": _wishes, "prerequisites": _prerequisites},
    "gate2_outcomes": {"co": _co, "co_delete": _co_delete, "proposals": _proposals},
    "gate3_proposal": {"weeks": _weeks, "labs": _labs, "assessment": _assessment, "books": _books, "description": _description},
}


def apply(run_dir: Path, gate: str, section: str, value, by: str) -> dict:
    fn = (SECTIONS.get(gate) or {}).get(section)
    if fn is None:
        raise EditError({"_": "This part can't be edited at this step."})
    st = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
    gpath = run_dir / "design_graph.json"
    g = DesignGraph.load(gpath) if gpath.exists() else DesignGraph((st.get("run_cfg") or {}).get("project_id", "P0001"), gpath)
    engine.configure(st.setdefault("run_cfg", {}))
    open_before = gate_payload(st)["open_errors"]
    work = copy.deepcopy(st)
    try:
        changes = fn(work, g, value)
        if not changes:
            return {"changes": [], "payload": None, "open_before": open_before, "open_after": open_before}
        recheck(work)
    except EditError:
        raise
    except Exception as e:  # noqa: BLE001 — a check that fails on the edited course: report it, save nothing
        raise EditError({"_": f"The edit could not be checked ({type(e).__name__}: {str(e)[:160]}). Nothing was changed."}) from e
    work.setdefault("professor_edits", []).append({"gate": gate, "section": section, "by": by, "at": time.time(), "changes": changes})
    (run_dir / "state.json").write_text(json.dumps(work, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    g.save()
    problem = None
    if gate == "gate3_proposal":
        problem = _rerender(run_dir, work)
        (run_dir / "state.json").write_text(json.dumps(work, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    payload = gate_payload(work)
    with (run_dir / "run.log").open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} PROFESSOR EDIT at {gate} ({section}) by {by}: " + "; ".join(changes)[:600]
                + f" · open errors {open_before} → {payload['open_errors']}\n")
    return {"changes": changes, "payload": payload, "open_before": open_before, "open_after": payload["open_errors"], "problem": problem}


def edits_at(st: dict | None, gate: str) -> list[dict]:
    return [e for e in (st or {}).get("professor_edits") or [] if e.get("gate") == gate]
