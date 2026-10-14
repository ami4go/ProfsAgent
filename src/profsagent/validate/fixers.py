"""Deterministic fixers (validation layer v2): corrections a rule fully decides, applied to a stage's component before
R1 repair. NO LLM. Each fixer edits only what its rule determines and leaves every pedagogical choice to the generator;
engine.apply_fixers keeps a fix only if the error count strictly drops and no new error code appears.

    drop-dangling-refs   T10   links to LOs, topics, topic groups, POs or COs that do not exist are removed
                               (an assessment entry removed this way gives its marks back to the other entries)
    normalise-marks      VA-MARKS  an instance's LO marks shares are rescaled to sum to exactly 100
    declared-n           V3    a best-k-of-n component's declared n is set to the number of instances it schedules
(Weights, the proctored minimum, assessment timing and instance order are fitted by design/deterministic.fit_assessment
inside the S7 apply step, so they are not repeated here.)
"""
from __future__ import annotations

from profsagent.design.deterministic import _largest_remainder
from profsagent.validate.engine import fixer


def _rebalance(entries: list[dict]) -> None:
    shares = [float(a["marks_pct_of_instance"]) for a in entries]
    if entries and sum(shares) > 0:
        for a, sh in zip(entries, _largest_remainder(shares)):
            a["marks_pct_of_instance"] = float(sh)


def _topic_ids(state: dict, comp: dict) -> set[str]:
    modules = comp.get("modules") if "modules" in comp else state.get("modules", [])
    return {t["id"] for m in modules or [] for t in m["topics"]}


@fixer("drop-dangling-refs", ["T10"])
def drop_dangling_refs(state: dict, comp: dict, errors: list[dict]) -> tuple[dict, list[str]]:
    notes: list[str] = []
    los = {lo["id"] for lo in (comp.get("los") if "los" in comp else state.get("los", []))}
    cos = {c["id"] for c in (comp.get("cos") if "cos" in comp else state.get("cos", []))}
    tgs = {g["id"] for g in state.get("topic_groups", [])}
    pos = {p["uid"] for p in state.get("programme_pos", [])}
    topics = _topic_ids(state, comp)

    def keep(owner: str, field: str, ids: list, known: set) -> list:
        bad = [x for x in ids if x not in known]
        if bad:
            notes.append(f"{owner}: removed unknown {field} {bad}")
        return [x for x in ids if x in known]

    for c in comp.get("cos", []):                                         # G4
        c["covers_topic_groups"] = keep(c["id"], "topic groups", c.get("covers_topic_groups", []), tgs)
    if "mappings" in comp:                                                # G5
        bad = [m for m in comp["mappings"] if m["po_uid"] not in pos or m["co_id"] not in cos]
        if bad:
            notes.append(f"removed {len(bad)} CO–PO mappings to unknown POs/COs: {sorted({m['po_uid'] for m in bad})}")
            comp["mappings"] = [m for m in comp["mappings"] if m not in bad]
    for lo in comp.get("los", []):                                        # G6
        lo["requires"] = keep(lo["id"], "LO prerequisites", lo.get("requires", []), los)
    for m in comp.get("modules", []):                                     # G7
        for t in m["topics"]:
            t["serves_los"] = keep(t["id"], "LOs", t.get("serves_los", []), los)
            t["covers_topic_groups"] = keep(t["id"], "topic groups", t.get("covers_topic_groups", []), tgs)
    for s in comp.get("labs", []) + comp.get("tutorials", []):           # G8
        s["uses_topics"] = keep(s["id"], "topics", s.get("uses_topics", []), topics)
        s["practises_los"] = keep(s["id"], "LOs", s.get("practises_los", []), los)
    for c in comp.get("components", []):                                  # G9
        for inst in c["instances"]:
            inst["covers_topics"] = keep(inst["id"], "topics", inst.get("covers_topics", []), topics)
            good = [a for a in inst["assesses"] if a["lo_id"] in los]
            if good and len(good) < len(inst["assesses"]):
                notes.append(f"{inst['id']}: removed marks on unknown LOs {[a['lo_id'] for a in inst['assesses'] if a['lo_id'] not in los]}")
                inst["assesses"] = good
                _rebalance(good)
    return comp, notes


@fixer("normalise-marks", ["VA-MARKS"])
def normalise_marks(state: dict, comp: dict, errors: list[dict]) -> tuple[dict, list[str]]:
    notes = []
    for c in comp.get("components", []):
        for inst in c["instances"]:
            total = sum(float(a["marks_pct_of_instance"]) for a in inst["assesses"])
            if inst["assesses"] and total > 0 and abs(total - 100) > 0.5:
                _rebalance(inst["assesses"])
                notes.append(f"{inst['id']}: LO marks shares rescaled from {total:g} to 100")
    return comp, notes


@fixer("declared-n", ["V3"])
def declared_n(state: dict, comp: dict, errors: list[dict]) -> tuple[dict, list[str]]:
    notes = []
    for c in comp.get("components", []):
        if c.get("n") is not None and c["n"] != len(c["instances"]):
            notes.append(f"{c['type']}: declared n {c['n']} set to the {len(c['instances'])} instances scheduled")
            c["n"] = len(c["instances"])
    return comp, notes
