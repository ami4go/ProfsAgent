"""Validation layer v2, stage 2: deterministic fixers, run through engine.apply_fixers exactly as agents/loop.generate
runs them (each stage's component and apply function as in agents/pipeline.py). No LLM calls."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.validate import engine

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"
LABS = (lambda s, c: {**s, "labs_tutorials": c}, ["labs"])
ASSESS = (lambda s, c: {**s, "assessment": c}, ["assessment"])
COPO = (lambda s, c: {**s, "copo": c["mappings"]}, ["copo"])
STRUCT = (lambda s, c: {**s, "modules": c["modules"]}, ["structure"])


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def run(s, comp, stage):
    apply, stages = stage
    vs = engine.check(apply(s, comp), stages)
    comp2, vs2, log = engine.apply_fixers(s, comp, apply, stages, vs)
    return engine.error_codes(vs), comp2, engine.error_codes(vs2), log


def test_fixers_are_registered():
    assert {f.name for f in engine.FIXERS} >= {"drop-dangling-refs", "normalise-marks", "declared-n"}


def test_dangling_refs_in_labs(s):
    lt = copy.deepcopy(s["labs_tutorials"])
    lt["labs"][0]["uses_topics"].append("M9.T9")
    lt["labs"][0]["practises_los"].append("CO9.LO9")
    before, comp, after, log = run(s, lt, LABS)
    assert "T10" in before and "T10" not in after and log[0]["accepted"]
    assert "M9.T9" not in comp["labs"][0]["uses_topics"] and "CO9.LO9" not in comp["labs"][0]["practises_los"]


def test_dangling_refs_in_assessment_give_marks_back(s):
    a = copy.deepcopy(s["assessment"])
    inst = a["components"][0]["instances"][0]
    inst["covers_topics"].append("M9.T9")
    inst["assesses"].append({"lo_id": "LO_FAKE_1", "marks_pct_of_instance": 20.0, "bloom_level": 2})
    before, comp, after, log = run(s, a, ASSESS)
    assert {"T10", "VA-MARKS"} <= set(before) and not {"T10", "VA-MARKS"} & set(after)
    fixed = comp["components"][0]["instances"][0]
    assert "LO_FAKE_1" not in [x["lo_id"] for x in fixed["assesses"]]
    assert sum(x["marks_pct_of_instance"] for x in fixed["assesses"]) == 100


def test_marks_shares_rescaled(s):
    a = copy.deepcopy(s["assessment"])
    entries = a["components"][0]["instances"][0]["assesses"]
    entries[0]["marks_pct_of_instance"] = float(entries[0]["marks_pct_of_instance"]) - 30
    before, comp, after, log = run(s, a, ASSESS)
    assert "VA-MARKS" in before and "VA-MARKS" not in after
    assert sum(x["marks_pct_of_instance"] for x in comp["components"][0]["instances"][0]["assesses"]) == 100


def test_declared_n_matches_the_schedule(s):
    a = copy.deepcopy(s["assessment"])
    c = next(c for c in a["components"] if len(c["instances"]) >= 1)
    c["n"] = len(c["instances"]) + 3
    before, comp, after, log = run(s, a, ASSESS)
    assert "V3" in before and "V3" not in after
    assert next(x for x in comp["components"] if x["type"] == c["type"])["n"] == len(c["instances"])


def test_dangling_topic_lo_in_structure(s):
    m = {"modules": copy.deepcopy(s["modules"])}
    m["modules"][0]["topics"][0]["serves_los"].append("CO9.LO9")
    before, comp, after, log = run(s, m, STRUCT)
    assert "T10" in before and "T10" not in after


def test_unknown_pos_are_dropped_and_mapping_gaps_left_for_repair(s):
    c = {"mappings": copy.deepcopy(s["copo"])}
    for x in c["mappings"]:
        x["po_uid"] = "PO_MAGIC"
    before, comp, after, log = run(s, c, COPO)
    assert "T10" in before and "T4" in before          # template rule: every CO maps to every programme
    assert log[0]["accepted"] and comp["mappings"] == []
    assert "T10" not in after and "T4" in after         # the real mappings are a judgement: left for R1 / the professor


def test_fix_without_improvement_is_not_kept(s):
    a = copy.deepcopy(s["assessment"])
    inst = a["components"][0]["instances"][0]
    inst["assesses"] = [{"lo_id": "LO_FAKE_1", "marks_pct_of_instance": 100.0, "bloom_level": 2}]   # nothing valid to keep
    before, comp, after, log = run(s, a, ASSESS)
    assert "T10" in before and not log[0]["accepted"] and comp is a


def test_fixable_codes_are_annotated(s):
    s2 = copy.deepcopy(s)
    s2["labs_tutorials"]["labs"][0]["uses_topics"].append("M9.T9")
    t10 = next(x for x in engine.check(s2) if x["code"] == "T10")
    assert t10["fixable_by"] == "fixer"
