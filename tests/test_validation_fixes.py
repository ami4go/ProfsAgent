"""Regression tests for validation-layer bugs (each failed before its fix). Uses the committed clean CS-601 design."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.agents.loop import temperature
from profsagent.design import deterministic as det
from profsagent.llm.prompts import load_prompt
from profsagent.validate import rules

BASE = ROOT / "runs/cs601-01/state.json"
pytestmark = pytest.mark.skipif(not BASE.exists(), reason="needs the committed runs/cs601-01/state.json")


@pytest.fixture
def s():
    return copy.deepcopy(json.loads(BASE.read_text(encoding="utf-8")))


def codes(vs, code, sev=None, node=None):
    return [x for x in vs if x["code"] == code and (sev is None or x["severity"] == sev) and (node is None or node in x["nodes"])]


# Rules added with the IIIT-D CSE course template (2026-10-14), after runs/cs601-01 was generated: that design
# predates them (e.g. it has 30% proctored evaluation), so they are excluded from this "clean design" check.
TEMPLATE_RULES = {"VA-PROCTOR", "VCO-BL", "VT-LOAD"}


def test_clean_design_has_no_errors(s):
    assert [x for x in rules.errors(rules.run(s)) if x["code"] not in TEMPLATE_RULES] == []


# ---- repair loop
def test_declared_zero_temperature_is_kept():
    assert temperature({"temperature": 0}) == 0.0
    assert temperature({"temperature": "0"}) == 0.0
    assert temperature({}) == 0.2
    assert temperature(load_prompt("R1").meta) == 0.0


# ---- computed CO–PO strengths / marks shares (feed V23)
def test_best_k_of_n_credits_the_component_weight_once():
    comp = {"type": "quiz", "weight_pct": 10.0, "best_k": 3, "n": 4, "activity_types": ["tool-use"],
            "instances": [{"id": f"Q{i}", "assesses": [{"lo_id": "L1", "marks_pct_of_instance": 100.0}]} for i in range(4)]}
    assert det.co_marks_share({"L1": "CO1"}, [comp]) == {"CO1": 10.0}
    other = {**comp, "type": "project", "weight_pct": 10.0, "best_k": None, "n": None, "activity_types": ["design"],
             "instances": [{"id": "P", "assesses": [{"lo_id": "L1", "marks_pct_of_instance": 100.0}]}]}
    rows = det.copo_strengths(["CO1"], {"L1": "CO1"}, [comp, other], {"tool-use": ["PO9"], "design": ["PO4"]}, [],
                              {"three": 0.6, "two": 0.3})
    assert {r["po_uid"]: r["share"] for r in rows} == {"PO4": 0.5, "PO9": 0.5}   # was 0.429 / 0.571


# ---- statement checks
def test_vb_accepts_the_range_of_an_ambiguous_verb(s):
    c = s["cos"][0]
    c.update(verb="Develop", bloom_level=3, statement="Develop " + c["statement"].split(" ", 1)[1])
    assert codes(rules.check_cos(s), "VB") == []
    # (the IIIT-D taxonomy lists "List" under BL1 and BL4, so List@5 is only one level off; "Define" is BL1-only)
    c.update(verb="Define", bloom_level=5, statement="Define " + c["statement"].split(" ", 1)[1])
    assert codes(rules.check_cos(s), "VB")                     # a real mismatch still warns


def test_v12_ignores_banned_words_used_as_nouns(s):
    c = s["cos"][0]
    c["statement"] = f"{c['verb']} natural-language understanding models for a robot grasp planner, {c['condition']}, {c['degree']}"
    assert codes(rules.check_cos(s), "V12") == []


@pytest.mark.parametrize("statement", ["Understand {b}", "Students will be able to understand {b}", "Configure and understand {b}"])
def test_v12_still_catches_banned_verbs(s, statement):
    c = s["cos"][0]
    c["statement"] = statement.format(b=c["behaviour"]) + f", {c['condition']}, {c['degree']}"
    assert codes(rules.check_cos(s), "V12", "error")


def test_v11_visibility_ignores_punctuation_spacing(s):
    c = s["cos"][0]
    c["degree"] = "with >= 80% of tests passing"
    c["statement"] = f"{c['verb']} {c['behaviour']}, {c['condition']}, with >=80% of tests passing."
    assert [x for x in codes(rules.check_cos(s), "V11") if c["id"] in x["nodes"]] == []


# ---- CO and CO–PO checks
def test_vco_dup_names_only_the_duplicates(s):
    a, b, c = s["cos"][:3]
    for k in ("verb", "behaviour", "condition", "degree", "statement"):
        b[k] = a[k]
    c["verb"] = a["verb"]
    c["statement"] = a["verb"] + " " + c["statement"].split(" ", 1)[1]
    assert [x["nodes"] for x in codes(rules.check_cos(s), "VCO-DUP")] == [[a["id"], b["id"]]]


def test_t4_counts_distinct_pos_and_flags_repeated_rows(s):
    row = {**s["copo"][0], "co_id": "CO1"}
    s["copo"] = [m for m in s["copo"] if m["co_id"] != "CO1"] + [row] * 4
    t4 = codes(rules.check_copo(s), "T4")
    assert [x["severity"] for x in t4] == ["warning"] and "mapped 4 times" in t4[0]["message"]


# ---- dangling ids
def test_unknown_topics_in_labs_and_assessments_are_t10(s):
    s["labs_tutorials"]["labs"][0]["uses_topics"].append("M9.T9")
    s["assessment"]["components"][0]["instances"][0]["covers_topics"].append("M9.T9")
    assert codes(rules.check_labs(s), "T10", "error")
    assert codes(rules.check_assessment(s), "T10", "error")


# ---- assessment timing
def test_due_week_outside_semester(s):
    s["assessment"]["components"][1]["instances"][0]["due_week"] = 20
    assert codes(rules.check_assessment(s), "VA-TIME", "error")


@pytest.mark.parametrize("offset, warns", [(0, False), (1, False), (-3, True), (4, True)])
def test_midsem_after_week_m_accepts_m_and_m_plus_1(s, offset, warns):
    for c in s["assessment"]["components"]:
        if c["type"] == "midsem":
            for i in c["instances"]:
                i["release_week"] = i["due_week"] = s["midsem_after_week"] + offset
    assert bool(codes(rules.check_assessment(s), "VA-MIDSEM")) is warns


# ---- professor constraints on assessment
def test_hard_present_constraint_is_enforced(s):
    s["assessment"]["components"] = [c for c in s["assessment"]["components"] if c["type"] != "project"]
    s["constraints"].append({"id": "K20", "target": "assessment.component[project].present", "op": "present", "value": True, "hardness": "hard"})
    assert codes(rules.check_assessment(s), "VK", "error", node="K20")


@pytest.mark.parametrize("op, value, violated", [("!=", 10, True), ("<", 10, True), (">", 5, False), ("<=", 10, False), ("==", 10, False)])
def test_weight_constraint_ops(s, op, value, violated):   # quiz weight is 10 in the baseline
    s["constraints"].append({"id": "K21", "target": "assessment.component[quiz].weight_pct", "op": op, "value": value, "hardness": "hard"})
    assert bool(codes(rules.check_assessment(s), "VK", node="K21")) is violated


def test_weight_constraint_on_missing_component(s):
    s["constraints"].append({"id": "K21", "target": "assessment.component[endsem].weight_pct", "op": ">=", "value": 30, "hardness": "hard"})
    assert codes(rules.check_assessment(s), "VK", "error", node="K21")      # no end-sem means 0% < 30%


def test_weight_constraint_with_unusable_op_is_reported(s):
    s["constraints"].append({"id": "K21", "target": "assessment.component[quiz].weight_pct", "op": "before", "value": 10, "hardness": "hard"})
    assert codes(rules.check_assessment(s), "VK-MALFORMED")


# ---- content constraints
def test_must_exclude_two_word_phrase_needs_both_words(s):
    s["modules"][0]["topics"][0]["title"] = "Non-functional requirements of agent systems"
    s["constraints"].append({"id": "K22", "target": "content.must_exclude[functional programming]", "op": "absent", "hardness": "hard"})
    assert codes(rules.check_structure(s), "VK-CONTENT") == []


def test_must_include_still_ignores_trailing_programming(s):
    s["modules"][0]["topics"][0]["title"] = "Graphical user interfaces"
    s["constraints"].append({"id": "K23", "target": "content.must_include[graphical user interface programming]", "op": "present", "hardness": "hard"})
    assert codes(rules.check_structure(s), "VK-CONTENT") == []
