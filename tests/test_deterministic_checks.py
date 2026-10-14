"""Validation layer v2, stage 2: regulation checks, the constraint compiler (normalisation, checkers, conflicts,
coverage), schedule order (VT-ORDER), statement length (VT-LEN) and vague degree phrases. No LLM calls."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.kg.quality import vague_degree
from profsagent.validate import constraints as K
from profsagent.validate import regulation, rules

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def codes(vs, code=None, sev=None, node=None):
    return [x for x in vs if (code is None or x["code"] == code) and (sev is None or x["severity"] == sev)
            and (node is None or node in x["nodes"])]


def add(s, **c):
    s["constraints"].append({"id": "K90", "hardness": "hard", "raw": "", **c})
    return s


# ---------------------------------------------------------------- regulation
def test_clean_frame_passes_regulation(s):
    assert regulation.check_regulation(s) == []


@pytest.mark.parametrize("change, code", [
    (lambda s: s.update(weeks=50), "VREG-WEEKS"),
    (lambda s: s["ltp"].update(L=0), "VREG-LTP"),
    (lambda s: s["ltp"].update(L=6, T=3, P=6), "VREG-LTP"),
    (lambda s: s["defaults"].update(credits=3), "VREG-CREDITS"),
])
def test_regulation_violations(s, change, code):
    change(s)
    assert codes(regulation.check_regulation(s), code, "error")


def test_intake_stage_runs_regulation(s):
    s["weeks"] = 50
    assert codes(rules.run(s, ["intake"]), "VREG-WEEKS")


# ---------------------------------------------------------------- compiler: one requirement, many shapes
@pytest.mark.parametrize("c, kind, op, arg", [
    ({"target": "content.must_exclude", "op": "not_in", "value": "general AI"}, "content.must_exclude[]", "exclude", "general AI"),
    ({"target": "content.must_exclude[general AI]", "op": "==", "value": True}, "content.must_exclude[]", "exclude", "general AI"),
    ({"target": "content.must_exclude[<phrase>]", "op": "in", "value": "Java features"}, "content.must_exclude[]", "exclude", "Java features"),
    ({"target": "content.must_ exclude", "op": "not_in", "value": "theory of LLMs"}, "content.must_exclude[]", "exclude", "theory of LLMs"),
    ({"target": "content.must_include", "op": "in", "value": "unit testing"}, "content.must_include[]", "include", "unit testing"),
    ({"target": "assessment.component[final project].present", "op": "==", "value": True}, "assessment.component[].present", "present", "final project"),
    ({"target": "assessment.component[endsem].present", "op": "absent", "value": None}, "assessment.component[].present", "absent", "endsem"),
    ({"target": "assessment.component[endsem].present", "op": "==", "value": False}, "assessment.component[].present", "absent", "endsem"),
    ({"target": "lab.present", "op": "present", "value": True}, "lab.present", "present", None),
])
def test_compiler_normalises_shapes(c, kind, op, arg):
    p = K.compile_constraint({"id": "K1", "hardness": "hard", **c})
    assert (p.kind, p.op) == (kind, op) and p.malformed is None
    assert (p.args[0] if p.args else None) == arg


@pytest.mark.parametrize("c", [
    {"target": "content.must_include[<phrase>]", "op": "in", "value": None},
    {"target": "co.count", "op": "in", "value": 5},
    {"target": "co.count", "op": "==", "value": "five"},
    {"target": "content.must_include[practical components rather than relying solely on theoretical treatment of large language models]",
     "op": "==", "value": True},
])
def test_compiler_flags_uncheckable_constraints(c):
    assert K.compile_constraint({"id": "K1", "hardness": "hard", **c}).malformed


@pytest.mark.parametrize("name, typ", [("final project", "project"), ("practical assignments", "assignment"),
                                       ("end-sem exam", "endsem"), ("midsem", "midsem"), ("hands-on coding exercises", None)])
def test_component_names_resolve_to_types(name, typ):
    assert K.component_type(name) == typ


# ---------------------------------------------------------------- checkers
def test_clean_design_constraints_hold(s):
    vs = [x for st in ("intake", "cos", "structure", "schedule", "labs", "assessment", "resources") for x in K.check_stage(s, st)]
    assert codes(vs, sev="error") == []


def test_co_count(s):
    add(s, target="co.count", op="==", value=12)
    assert codes(K.check_stage(s, "cos"), "VK", "error", "K90")


def test_required_tool_no_lab_uses_is_an_error(s):
    add(s, target="lab.tools_include", op="in", value="Kubernetes cluster")
    assert codes(K.check_stage(s, "labs"), "VK", "error", "K90")


def test_lab_presence(s):
    add(s, target="lab.present", op="absent", value=None)
    assert codes(K.check_stage(s, "labs"), "VK", "error", "K90")


def test_lab_tool_in_infrastructure_is_only_a_warning(s):
    s["cco_compact"]["lab"]["infrastructure"] = ["Kubernetes cluster"]
    add(s, target="lab.tools_include", op="in", value="Kubernetes cluster")
    assert codes(K.check_stage(s, "labs"), "VK", "warning", "K90") and not codes(K.check_stage(s, "labs"), "VK", "error", "K90")


def test_topic_group_order(s):
    tgs = [g["id"] for g in s["topic_groups"]]
    add(s, target=f"schedule.topic_group[{tgs[-1]}].order_before[{tgs[0]}]", op="before", value=None)
    assert codes(K.check_stage(s, "schedule"), "VK", "error", "K90")


def test_blocked_week(s):
    add(s, target="schedule.week[2].blocked", op="==", value=True)
    assert codes(K.check_stage(s, "schedule"), "VK", "error", "K90")


def test_must_include_absent_is_error_partial_is_warning(s):
    add(s, target="content.must_include[quantum annealing hardware]", op="==", value=True)
    assert codes(K.check_stage(s, "structure"), "VK-CONTENT", "error", "K90")
    s["constraints"][-1]["target"] = "content.must_include[practical hands-on quantum annealing]"
    assert codes(K.check_stage(s, "structure"), "VK-CONTENT", "warning", "K90")


def test_component_named_by_type_word(s):
    types = {c["type"] for c in s["assessment"]["components"]}
    assert "project" in types
    add(s, target="assessment.component[final project].present", op="==", value=True)
    assert not codes(K.check_stage(s, "assessment"), node="K90")
    s["assessment"]["components"] = [c for c in s["assessment"]["components"] if c["type"] != "project"]
    assert codes(K.check_stage(s, "assessment"), "VK", "error", "K90")


def test_unresolvable_component_is_a_warning(s):
    add(s, target="assessment.component[hands-on coding exercises].present", op="==", value=True)
    assert codes(K.check_stage(s, "assessment"), "VK", "warning", "K90")


# ---------------------------------------------------------------- S3: conflicts and coverage
@pytest.mark.parametrize("cs, conflict", [
    ([("co.count", "==", 5), ("co.count", "==", 12)], True),
    ([("co.count", "<=", 4), ("co.count", ">=", 6)], True),
    ([("co.count", ">=", 4), ("co.count", "<=", 5)], False),
    ([("lab.hours_per_week", "==", 2), ("lab.hours_per_week", "!=", 2)], True),
])
def test_numeric_conflicts(s, cs, conflict):
    s["constraints"] = [{"id": f"K{90 + i}", "target": t, "op": op, "value": val, "hardness": "hard"} for i, (t, op, val) in enumerate(cs)]
    s.pop("co_count", None)
    assert bool(codes(K.conflicts(s), "VK-CONFLICT")) is conflict


def test_soft_constraints_never_conflict(s):
    s["constraints"] = [{"id": "K90", "target": "co.count", "op": "==", "value": 5, "hardness": "soft"},
                        {"id": "K91", "target": "co.count", "op": "==", "value": 12, "hardness": "hard"}]
    s.pop("co_count", None)
    assert codes(K.conflicts(s), "VK-CONFLICT") == []


def test_presence_and_content_conflicts(s):
    s["constraints"] = [{"id": "K90", "target": "assessment.component[endsem].present", "op": "present", "value": True, "hardness": "hard"},
                        {"id": "K91", "target": "assessment.component[endsem].present", "op": "absent", "value": None, "hardness": "hard"},
                        {"id": "K92", "target": "content.must_include[unit testing]", "op": "==", "value": True, "hardness": "hard"},
                        {"id": "K93", "target": "content.must_exclude", "op": "not_in", "value": "unit testing", "hardness": "hard"}]
    assert len(codes(K.conflicts(s), "VK-CONFLICT")) == 2


def test_co_count_against_the_template_rule(s):
    s["constraints"] = [{"id": "K90", "target": "co.count", "op": "==", "value": 12, "hardness": "hard"}]
    assert codes(K.conflicts(s), "VK-CONFLICT", node="CO-COUNT-RULE")


def test_unenforced_constraints_are_listed(s):
    add(s, target="other", op="==", value=True, raw="weights must sum to 130%")
    v = codes(K.unenforced(s), "VK-UNENFORCED", "warning", "K90")
    assert v and K.coverage(s)["unenforced"] == ["K90"]


# ---------------------------------------------------------------- schedule order and statements
def test_topic_scheduled_before_its_prerequisite(s):
    tw = s["schedule"]["topic_weeks"]
    early, late = min(tw, key=lambda t: min(tw[t])), max(tw, key=lambda t: min(tw[t]))
    for t in (t for m in s["modules"] for t in m["topics"]):
        if t["id"] == early:
            t["requires"] = [*t.get("requires", []), late]
    assert codes(rules.check_schedule(s), "VT-ORDER", "error")
    s["schedule"]["dropped_edges"] = [[late, early]]    # the scheduler dropped it to break a cycle: VT-DAG reports it
    assert codes(rules.check_schedule(s), "VT-ORDER") == []


def test_statement_length(s):
    c = s["cos"][0]
    c["statement"] = f"{c['verb']} agents."
    assert codes(rules.check_cos(s), "VT-LEN", "warning", c["id"])


@pytest.mark.parametrize("degree, vague", [("deeply", True), ("in depth", True), ("in a good manner", True),
                                           ("with all 10 tests passing", False), ("fully explained with 3 cited sources", False)])
def test_vague_degree_words_and_phrases(degree, vague):
    assert bool(vague_degree(degree)) is vague
