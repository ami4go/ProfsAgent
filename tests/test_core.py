"""Offline tests for deterministic parts: scheduler, CO–PO computation, validators, store freezing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from profsagent.design import deterministic as det
from profsagent.design.store import DesignGraph, FrozenError
from profsagent.validate import rules


def _state():
    cos = [{"id": "CO1", "statement": "Implement a class hierarchy for a given specification, such that 80% of tests pass.",
            "verb": "implement", "behaviour": "a class hierarchy", "condition": "for a given specification",
            "degree": "such that 80% of tests pass", "bloom_level": 3, "knowledge_dimension": "procedural",
            "covers_topic_groups": ["TG1"], "evidence_types": ["programming_assignment"]},
           {"id": "CO2", "statement": "Understand and design patterns effectively.", "verb": "understand",
            "behaviour": "patterns", "condition": "", "degree": "effectively", "bloom_level": 6,
            "knowledge_dimension": "conceptual", "covers_topic_groups": [], "evidence_types": []}]
    los = [{"id": "CO1.LO1", "parent_co": "CO1", "statement": "Write a class for a given interface, with all 5 tests passing.",
            "verb": "write", "behaviour": "a class", "condition": "for a given interface", "degree": "with all 5 tests passing",
            "bloom_level": 3, "knowledge_dimension": "procedural", "requires": [], "hands_on": True, "est_lecture_h": 3}]
    modules = [{"id": "M1", "title": "OOP", "order": 1, "primary_cos": ["CO1"], "topics": [
        {"id": "M1.T1", "title": "classes", "est_hours": 2, "serves_los": ["CO1.LO1"], "requires": []},
        {"id": "M1.T2", "title": "orphan", "est_hours": 3, "serves_los": [], "requires": ["M1.T1"]}]}]
    sched = det.schedule([{**t, "module_order": 1} for t in modules[0]["topics"]], 13, 3, 7)
    assessment = {"components": [
        {"type": "quiz", "weight_pct": 10, "best_k": 2, "n": 2, "activity_types": [], "instances": [
            {"id": "A:Quiz1", "release_week": 1, "due_week": 1, "covers_topics": ["M1.T2"], "assesses": [{"lo_id": "CO1.LO1", "marks_pct_of_instance": 100, "bloom_level": 2}]},
            {"id": "A:Quiz2", "release_week": 3, "due_week": 3, "covers_topics": [], "assesses": [{"lo_id": "CO1.LO1", "marks_pct_of_instance": 100, "bloom_level": 3}]}]},
        {"type": "project", "weight_pct": 80, "activity_types": ["teamwork"], "instances": [
            {"id": "A:Proj", "release_week": 5, "due_week": 13, "covers_topics": [], "assesses": [{"lo_id": "CO1.LO1", "marks_pct_of_instance": 100, "bloom_level": 3}]}]}]}
    return {"cos": cos, "los": los, "modules": modules, "schedule": sched, "assessment": assessment, "weeks": 13,
            "bloom_band": {"floor": 2, "ceiling": 5}, "topic_groups": [{"id": "TG1"}, {"id": "TG2"}],
            "hours_budget": {"lecture_hours_total": 39}, "midsem_after_week": 7, "constraints": [], "ltp": {"L": 3, "T": 1, "P": 0}}


def codes(vs):
    return {x["code"] for x in vs if x["severity"] == "error"}


def test_schedule_splits_and_orders():
    s = det.schedule([{"id": "B", "est_hours": 2, "requires": ["A"]}, {"id": "A", "est_hours": 2.5, "requires": []}], 13, 3, 7)
    assert s["order"] == ["A", "B"] and s["feasible"]
    assert s["topic_weeks"]["B"] == [1, 2]


def test_schedule_infeasible_explains():
    s = det.schedule([{"id": f"T{i}", "est_hours": 3} for i in range(15)], 13, 3, 7)
    assert not s["feasible"] and "45.0 lecture hours" in s["explanation"]


def test_cycle_broken():
    s = det.schedule([{"id": "A", "est_hours": 1, "requires": ["B"], "suggested_order": 1},
                      {"id": "B", "est_hours": 1, "requires": ["A"], "suggested_order": 2}], 13, 3, 7)
    assert s["dropped_edges"] and len(s["order"]) == 2


def test_validators_catch_seeded_defects():
    st = _state()
    c = codes(rules.run(st))
    assert {"V12", "V11", "V7", "VCO-COVER", "V4"} <= c          # banned verb, vague degree, above band, TG2 uncovered, 2 COs
    assert "T5" in c                                              # orphan topic
    assert "V3" in c                                              # best 2 of 2
    assert "V19" in c                                             # Quiz1 (week 1) covers M1.T2, which runs into week 2
    assert "V1" in c                                              # 90 != 100
    assert "T2" in c                                              # CO2 has no LOs


def test_copo_computed_strength():
    st = _state()
    lo_parent = {"CO1.LO1": "CO1"}
    r = det.copo_strengths(["CO1", "CO2"], lo_parent, st["assessment"]["components"], {"teamwork": ["PO5"]},
                           [{"co_id": "CO1", "po_uid": "PO5", "strength_provisional": 3}, {"co_id": "CO2", "po_uid": "PO4", "strength_provisional": 3}],
                           {"three": 0.6, "two": 0.3})
    d = {(x["co_id"], x["po_uid"]): x for x in r}
    assert d[("CO1", "PO5")]["strength_computed"] == 3          # 80/(80+10) of CO1 marks from teamwork
    assert d[("CO2", "PO4")]["strength_computed"] == 0 and d[("CO2", "PO4")]["claimed"]
    vs = rules.check_copo_computed({"copo_computed": r})
    assert any(x["code"] == "V23" and x["severity"] == "error" for x in vs)


def test_frozen_nodes_cannot_change(tmp_path):
    g = DesignGraph("P1", tmp_path / "g.json")
    g.put("CO", "CO1", {"statement": "x"}, created_by="G4")
    g.freeze_labels(["CO"])
    with pytest.raises(FrozenError):
        g.put("CO", "CO1", {"statement": "y"}, created_by="R1")
    with pytest.raises(FrozenError):
        g.update("CO1", "statement", "z", by="R1")


def test_new_rules_catch_review_defects():
    st = _state()
    st["los"].append({"id": "CO1.LO2", "parent_co": "CO1", "statement": st["cos"][0]["statement"], "verb": "implement",
                      "behaviour": "x", "condition": "for a given specification", "degree": "such that 80% of tests pass",
                      "bloom_level": 3, "knowledge_dimension": "procedural"})
    st["los"].append({"id": "CO1.LO3", "parent_co": "CO1", "statement": "Write a parser for a given grammar, with 5 tests passing.",
                      "verb": "verify", "behaviour": "a parser", "condition": "for a given grammar", "degree": "with 5 tests passing",
                      "bloom_level": 5, "knowledge_dimension": "procedural"})
    st["assessment"]["components"][1]["instances"] = [
        {"id": "A:ProjM1", "release_week": 11, "due_week": 12, "covers_topics": [], "assesses": [{"lo_id": "CO1.LO1", "marks_pct_of_instance": 100, "bloom_level": 3}]},
        {"id": "A:ProjFinal", "release_week": 9, "due_week": 13, "covers_topics": [], "assesses": [{"lo_id": "CO1.LO1", "marks_pct_of_instance": 100, "bloom_level": 3}]}]
    c = codes(rules.run(st))
    assert "VLO-COPY" in c          # LO restates its CO
    assert "V10" in c               # statement verb 'Write' != declared 'verify'
    assert "VA-ORDER" in c          # milestone released after the final
    assert "VTG-TAUGHT" in c        # topic groups never taught (no covers_topic_groups)
    assert "V21" in c               # 5 h of topics in a 39 h budget (under-filled)


def test_fix_hints_attached():
    vs = rules.run(_state())
    assert all("fix_hint" in x for x in vs if x["code"] in ("V10", "V11", "V12", "T2"))
