"""Direct-injection defect catalogue: the 20 defects of scripts/run_defect_benchmark.py, written straight into a clean
design state instead of asked for in the professor form, so they test the validators alone (no LLM, no API calls).

Each defect names the validator codes that should report it as an error. A defect whose check does not exist yet
(or does not fire yet) carries `known_gap`: the planned code and why it is missed today. The test suite marks those as
expected failures, so closing a gap in Stage 2 shows up as an unexpected pass that must be acknowledged.

Variants are realistic forms of the same defect, as the LLM produced them in the 2026-10-08 end-to-end runs (e.g. a
50-week semester with every hour total scaled to match, not just a longer schedule).
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class Defect:
    id: str                      # mutation id in scripts/run_defect_benchmark.py
    description: str
    expected: tuple[str, ...]    # validator codes that should fire as an error (any one is enough)
    apply: Callable[[dict], dict]
    variant: str | None = None   # None = the base defect; else a realistic variant of it
    known_gap: str | None = None # set while no check catches it (none open: closed in validation v2 stage 2)

    @property
    def name(self) -> str:
        return self.id if not self.variant else f"{self.id}[{self.variant}]"


# ------------------------------------------------------------------ helpers
def _topics(s):
    return [t for m in s.get("modules", []) for t in m["topics"]]


def _comps(s):
    return (s.get("assessment") or {}).get("components", [])


def _instances(s):
    return [i for c in _comps(s) for i in c["instances"]]


def _first_week(s):
    return {t: min(ws) for t, ws in (s.get("schedule") or {}).get("topic_weeks", {}).items() if ws}


def _on_copy(fn):
    def go(state):
        s = copy.deepcopy(state)
        fn(s)
        return s
    return go


# ------------------------------------------------------------------ the 20 defects
def _inv_weights(s):
    _comps(s)[0]["weight_pct"] += 30                                   # weights sum to 130


def _understand(s):
    c = s["cos"][0]
    c["verb"] = "understand"
    c["statement"] = f"Understand {c['behaviour']}, {c['condition']}, {c['degree']}."


def _all_bloom1(s):
    for c in s["cos"]:
        c["bloom_level"] = 1


def _orphan_lo(s):
    lo = copy.deepcopy(s["los"][0])
    lo.update(id="NONE.LO1", parent_co="NONE")
    s["los"].append(lo)


def _fake_lo_assess(s):
    _instances(s)[0]["assesses"][0]["lo_id"] = "LO_FAKE_1"


def _exam_week2(s):
    for c in _comps(s):
        if c["type"] in ("endsem", "midsem"):
            for i in c["instances"]:
                i["release_week"] = i["due_week"] = 2


def _temporal_inversion(s):
    fw = _first_week(s)
    early, late = min(fw, key=fw.get), max(fw, key=fw.get)
    for t in _topics(s):
        if t["id"] == early:
            t["requires"] = [*t.get("requires", []), late]               # an early topic needs one taught last


def _bad_prereq(s):
    s["positioning"].setdefault("prerequisites", []).append(
        {"kind": "mandatory", "course_uid": "NONEXISTENT101", "alternatives": [], "relied_topics": ["Programming basics"],
         "needed_by": ["TG1"], "justification": "required", "level_check": "lower_level", "sources": []})


def _hours_300(s):
    total = sum(float(t["est_hours"]) for t in _topics(s)) or 1
    for t in _topics(s):
        t["est_hours"] = round(float(t["est_hours"]) * 300 / total, 1)


def _contradictory(s):
    s.setdefault("constraints", []).extend([
        {"id": "K90", "target": "co.count", "op": "==", "value": 5, "hardness": "hard", "raw": "exactly 5 COs"},
        {"id": "K91", "target": "co.count", "op": "==", "value": 12, "hardness": "hard", "raw": "exactly 12 COs"}])


def _weeks_50_schedule_only(s):
    last = s["schedule"]["weeks"][-1]["week"]
    s["schedule"]["weeks"] += [{"week": last + k, "items": [], "is_midsem_boundary": False} for k in range(1, 51 - last)]


def _weeks_50_consistent(s):
    s["weeks"] = 50
    hb = s["hours_budget"]
    hb.update(weeks=50, lecture_hours_total=s["ltp"]["L"] * 50, tutorial_hours_total=s["ltp"]["T"] * 50,
              lab_hours_total=s["ltp"]["P"] * 50)
    _weeks_50_schedule_only(s)


def _po_magic(s):
    for m in s["copo"]:
        m["po_uid"] = "PO_MAGIC"


def _dup_cos(s):
    a, b = s["cos"][0], s["cos"][1]
    for k in ("verb", "behaviour", "condition", "degree", "statement"):
        b[k] = a[k]


def _no_assessment(s):
    s["assessment"]["components"] = []


def _no_lectures(s):
    s["ltp"]["L"] = 0
    s["hours_budget"].update(lecture_hours_per_week=0, lecture_hours_total=0)
    for t in _topics(s):
        t["est_hours"] = 0.0


def _ltp_6_3_6(s):
    s["ltp"].update(L=6, T=3, P=6)                                     # 15 contact h/week for a 4-credit course


def _vague(word):
    def fn(s):
        for lo in s["los"]:
            lo["degree"] = word
            lo["statement"] = lo["statement"].rstrip(".") + f" {word}."
    return fn


def _lo_cycle(s):
    a, b = s["los"][0], s["los"][1]
    a["requires"] = [*a.get("requires", []), b["id"]]
    b["requires"] = [*b.get("requires", []), a["id"]]


_EXTRA = ["prompt injection defence", "agent memory design", "cost accounting for LLM calls", "license compliance of generated code",
          "repository-scale refactoring", "code review bots", "flaky test triage", "secrets scanning", "on-call automation",
          "telemetry for agents"]


def _cos_15(s):
    base = s["cos"][0]
    for k in range(len(s["cos"]) + 1, 16):
        c = copy.deepcopy(base)
        obj = f"{_EXTRA[(k - 1) % len(_EXTRA)]} (part {k})"
        c.update(id=f"CO{k}", behaviour=obj, statement=f"{base['verb']} {obj}, {base['condition']}, {base['degree']}.")
        s["cos"].append(c)
        s["copo"].append({**s["copo"][0], "co_id": c["id"]})


def _los_15(s):
    base = s["los"][0]
    new = []
    for k in range(3, 16):
        lo = copy.deepcopy(base)
        obj = _EXTRA[(k - 3) % len(_EXTRA)]
        lo.update(id=f"{base['parent_co']}.LO{k}", behaviour=obj, statement=f"{base['verb']} {obj} {base['condition']} {base['degree']}.")
        new.append(lo)
    s["los"].extend(new)
    _topics(s)[0]["serves_los"] = [*_topics(s)[0]["serves_los"], *[lo["id"] for lo in new]]


def _no_topics(s):
    s["modules"] = []


D = Defect
DEFECTS: list[Defect] = [
    D("inv_assess_weights", "weights sum to 130%", ("V1",), _on_copy(_inv_weights)),
    D("banned_verbs", "a CO uses the banned verb 'understand'", ("V12",), _on_copy(_understand)),
    D("bloom_inconsistencies", "every CO at Bloom level 1", ("V8",), _on_copy(_all_bloom1)),
    D("orphan_los", "an LO whose parent CO does not exist", ("T1",), _on_copy(_orphan_lo)),
    D("invalid_lo_assess", "an assessment marks a non-existent LO", ("T10",), _on_copy(_fake_lo_assess)),
    D("assess_before_teach", "the exams move to week 2", ("V19",), _on_copy(_exam_week2)),
    D("temporal_inversions", "an early topic requires the last-taught topic", ("VT-ORDER",), _on_copy(_temporal_inversion)),
    D("invalid_prereqs", "prerequisite NONEXISTENT101", ("V14",), _on_copy(_bad_prereq)),
    D("impossible_hours", "topics need 300 lecture hours", ("V21", "VT-SIZE"), _on_copy(_hours_300)),
    D("contradictory_constraints", "hard constraints demand exactly 5 and exactly 12 COs", ("VK-CONFLICT",), _on_copy(_contradictory)),
    D("invalid_week_counts", "the schedule is stretched to 50 weeks", ("V2",), _on_copy(_weeks_50_schedule_only)),
    D("invalid_week_counts", "a 50-week semester with every hour total scaled to match", ("VREG-WEEKS",), _on_copy(_weeks_50_consistent),
      variant="consistent"),
    D("malformed_copo", "COs mapped to PO_MAGIC", ("T10",), _on_copy(_po_magic)),
    D("duplicate_outcomes", "two COs with the same verb and behaviour", ("VCO-DUP",), _on_copy(_dup_cos)),
    D("missing_assessment", "no assessment components", ("V1", "V9"), _on_copy(_no_assessment)),
    D("no_lectures", "L = 0 with zero lecture hours", ("VREG-LTP",), _on_copy(_no_lectures)),
    D("no_lectures", "L-T-P 6-3-6 for a 4-credit course", ("VREG-LTP",), _on_copy(_ltp_6_3_6),
      variant="ltp_6_3_6"),
    D("vague_degree", "every LO degree is 'thoroughly'", ("V11",), _on_copy(_vague("thoroughly"))),
    D("vague_degree", "every LO degree is 'deeply'", ("V11",), _on_copy(_vague("deeply")),
      variant="deeply"),
    D("cyclic_lo_deps", "LO1 requires LO2 and LO2 requires LO1", ("VLO-DAG",), _on_copy(_lo_cycle)),
    D("excessive_cos", "15 COs", ("V4",), _on_copy(_cos_15)),
    D("excessive_los", "15 LOs under one CO", ("T2", "VLO-COUNT"), _on_copy(_los_15)),
    D("no_topics", "no topics at all", ("T5", "VTG-TAUGHT"), _on_copy(_no_topics)),
]
