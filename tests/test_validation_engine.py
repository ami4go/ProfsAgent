"""Validation engine (validation layer v2, Stage 1): record v2 annotations, the fixer registry, and the wiring into
agents/loop.generate. No LLM calls: the generator and R1 are faked."""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.agents import loop
from profsagent.validate import engine, rules

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"
R1_KEYS = {"code", "severity", "nodes", "message", "evidence", "fix_hint", "stage"}   # what R1 has always been shown


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture
def no_fixers(monkeypatch):
    monkeypatch.setattr(engine, "FIXERS", [])
    return engine.FIXERS


def _comps(state):
    return state["assessment"]["components"]


def _normalise_weights(state, comp, errors):          # a test fixer: take the excess off the largest component
    total = sum(c["weight_pct"] for c in comp["components"])
    big = max(comp["components"], key=lambda c: c["weight_pct"])
    big["weight_pct"] -= total - 100
    return comp, [f"{big['type']} reduced by {total - 100} so weights sum to 100"]


def test_every_validator_code_has_a_family():
    codes = set(re.findall(r'\bv\("([A-Z0-9-]+)"', (ROOT / "src/profsagent/validate/rules.py").read_text(encoding="utf-8")))
    assert codes and codes <= set(engine.FAMILY), f"unclassified codes: {sorted(codes - set(engine.FAMILY))}"


def test_check_annotates_record_v2(s, no_fixers):
    s2 = copy.deepcopy(s)
    _comps(s2)[0]["weight_pct"] += 30
    s2["resources"][0]["verification"] = {"verified": False, "problems": ["not found"]}
    vs = {x["code"]: x for x in engine.check(s2)}
    assert vs["V1"]["family"] == "rule" and vs["V1"]["fixable_by"] == "repair"          # assessment stage: R1 can repair
    assert vs["V15"]["family"] == "resource" and vs["V15"]["fixable_by"] == "professor"  # S8 has no repair step
    assert vs["V23"]["family"] == "rule"


def test_registered_fixer_marks_its_codes(s, monkeypatch, no_fixers):
    engine.fixer("normalise-weights", ["V1"])(_normalise_weights)
    s2 = copy.deepcopy(s)
    _comps(s2)[0]["weight_pct"] += 30
    v1 = next(x for x in engine.check(s2) if x["code"] == "V1")
    assert v1["fixable_by"] == "fixer"


def test_r1_sees_the_same_fields_as_before(s, no_fixers):
    s2 = copy.deepcopy(s)
    _comps(s2)[0]["weight_pct"] += 30
    for x in engine.strip_v2(engine.check(s2)):
        assert set(x) <= R1_KEYS


def test_fixer_is_kept_only_if_errors_drop(s, no_fixers):
    apply = lambda st, c: {**st, "assessment": c}                      # noqa: E731
    bad = copy.deepcopy(s["assessment"])
    bad["components"][0]["weight_pct"] += 30
    vs = engine.check(apply(s, bad), ["assessment"])
    assert "V1" in engine.error_codes(vs)

    engine.fixer("normalise-weights", ["V1"])(_normalise_weights)
    comp, vs2, log = engine.apply_fixers(s, bad, apply, ["assessment"], vs)
    assert log[0]["accepted"] and "V1" not in engine.error_codes(vs2)

    engine.FIXERS.clear()
    engine.fixer("breaks-marks", ["V1"])(lambda st, c, e: (
        {**c, "components": [{**c["components"][0], "instances": [{**i, "assesses": []} for i in c["components"][0]["instances"]]},
                             *c["components"][1:]]}, ["dropped marks"]))
    comp3, vs3, log3 = engine.apply_fixers(s, bad, apply, ["assessment"], vs)
    assert not log3[0]["accepted"] and comp3 is bad                   # new error codes -> rejected, component unchanged


class _Obj:
    def __init__(self, d):
        self._d = d

    def model_dump(self):
        return copy.deepcopy(self._d)


class _RT:
    def __init__(self, state):
        self.state, self.lines = state, []

    def log(self, msg):
        self.lines.append(msg)


def test_generate_runs_fixers_then_repair_and_reports_open_items(s, monkeypatch, no_fixers):
    draft = copy.deepcopy(s["assessment"])
    draft["components"][0]["weight_pct"] += 30
    calls = []

    def fake_call(rt, pid, ctx, role="generate"):
        calls.append(pid)
        if pid == "R1":
            raise RuntimeError("no LLM in tests")
        return _Obj(draft), {"prompt_id": pid, "endpoint": "fake"}
    monkeypatch.setattr(loop, "call", fake_call)
    engine.fixer("normalise-weights", ["V1"])(_normalise_weights)

    rt = _RT(s)
    comp, vs, trace = loop.generate(rt, "G9", {}, apply=lambda st, c: {**st, "assessment": c}, stages=["assessment"])
    assert "V1" in trace["initial_error_codes"]
    assert trace["fixes"][0]["accepted"]
    assert trace["final_error_codes"] == ["V23"]                      # the clean design's known open error remains
    assert trace["open"] and {(o["code"], o["family"], o["fixable_by"]) for o in trace["open"]} == {("V23", "rule", "repair")}
    assert calls == ["G9", "R1"] and trace["repairs"][0]["why"].startswith("R1 failed")
    assert any("fixer normalise-weights" in line for line in rt.lines)
