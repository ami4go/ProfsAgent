"""Repair loop (validation layer v2, Stage 4): R1 sees the nodes it must fix, stops when it cannot help, and the
optional regenerate-on-stall step. No LLM calls: the generator and R1 are faked."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.agents import loop
from profsagent.llm.prompts import load_prompt
from profsagent.models.io import PatchOp, RepairPatch
from profsagent.validate import engine

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def no_fixers(monkeypatch):
    monkeypatch.setattr(engine, "FIXERS", [])


def limits(monkeypatch, **kw):
    monkeypatch.setattr(loop, "models_cfg", lambda: {"limits": {"repair_stall_rounds": 2, "regenerate_on_stall": 0, **kw}})


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


def bad_draft(s):
    d = copy.deepcopy(s["assessment"])
    d["components"][0]["weight_pct"] += 30           # V1 (sum 130) and V20 (quiz 40%) on top of the fixture's V23s
    return d


def faker(s, r1_replies, regen=None, seen=None):
    calls = []

    def fake_call(rt, pid, ctx, role="generate", extra_user=""):
        calls.append(pid + ("+regen" if extra_user else ""))
        if seen is not None:
            seen.append((pid, ctx, extra_user))
        if pid == "R1":
            return r1_replies.pop(0), {"prompt_id": "R1", "endpoint": "fake"}
        if extra_user:
            return _Obj(regen), {"prompt_id": pid, "endpoint": "fake"}
        return _Obj(bad_draft(s)), {"prompt_id": pid, "endpoint": "fake"}
    return fake_call, calls


def run(s, monkeypatch, r1_replies, regen=None, seen=None, stages=("assessment",), pid="G9", apply=None):
    fake_call, calls = faker(s, r1_replies, regen, seen)
    monkeypatch.setattr(loop, "call", fake_call)
    rt = _RT(s)
    comp, vs, trace = loop.generate(rt, pid, {}, apply=apply or (lambda st, c: {**st, "assessment": c}), stages=list(stages))
    return comp, vs, trace, calls, rt


def irrelevant(n):
    return RepairPatch(ops=[PatchOp(op="update", id="A:Quiz1", field="format", value=f"in-class quiz, variant {n}")])


def test_r1_gets_the_nodes_it_must_fix(s, monkeypatch):
    limits(monkeypatch)
    seen = []
    _, _, trace, calls, _ = run(s, monkeypatch, [RepairPatch()], seen=seen)
    ctx = next(c for p, c, _ in seen if p == "R1")
    assert ctx["violating_nodes"]["quiz"]["weight_pct"] == 40.0                    # V1/V20 name the quiz component
    assert set(ctx["violating_nodes"]) <= {"quiz", "assignment", "midsem", "lab", "project", "endsem"}
    assert calls == ["G9", "R1"] and trace["stop_reason"] == "R1 proposed no change"


def test_stops_after_two_rejected_patches(s, monkeypatch):
    limits(monkeypatch)
    _, _, trace, calls, rt = run(s, monkeypatch, [irrelevant(1), irrelevant(2), irrelevant(3)])
    assert calls == ["G9", "R1", "R1"] and trace["stop_reason"] == "2 rejected patches in a row"
    assert any("[R1] stopped" in line for line in rt.lines)


def test_a_repeated_rejected_patch_stops(s, monkeypatch):
    limits(monkeypatch, repair_stall_rounds=5)
    _, _, trace, calls, _ = run(s, monkeypatch, [irrelevant(1), irrelevant(1), irrelevant(2)])
    assert calls == ["G9", "R1", "R1"] and trace["stop_reason"] == "R1 repeated a rejected patch"


def test_accepted_patch_then_no_change(s, monkeypatch):
    limits(monkeypatch)
    fix = RepairPatch(ops=[PatchOp(op="update", id="quiz", field="weight_pct", value=10.0)])
    comp, _, trace, calls, _ = run(s, monkeypatch, [fix, RepairPatch()])
    assert [r["accepted"] for r in trace["repairs"]] == [True, False] and calls == ["G9", "R1", "R1"]
    assert trace["final_error_codes"] == ["V23"] and comp["components"][0]["weight_pct"] == 10.0


def test_no_r1_call_for_professor_only_errors(s, monkeypatch):
    limits(monkeypatch)
    draft = {"resources": copy.deepcopy(s["resources"])}
    draft["resources"][0]["verification"] = {"verified": False, "problems": ["no library record"]}
    calls = []

    def fake_call(rt, pid, ctx, role="generate", extra_user=""):
        calls.append(pid)
        return _Obj(draft), {"endpoint": "fake"}
    monkeypatch.setattr(loop, "call", fake_call)
    _, vs, trace = loop.generate(_RT(s), "G10", {}, apply=lambda st, c: {**st, "resources": c["resources"]}, stages=["resources"])
    assert "V15" in trace["final_error_codes"] and calls == ["G10"] and "reach" in trace["stop_reason"]


def test_regenerate_on_stall_keeps_a_better_answer(s, monkeypatch):
    limits(monkeypatch, repair_stall_rounds=1, regenerate_on_stall=1)
    seen = []
    comp, _, trace, calls, _ = run(s, monkeypatch, [irrelevant(1)], regen=copy.deepcopy(s["assessment"]), seen=seen)
    assert calls == ["G9", "R1", "G9+regen"] and trace["regenerations"][0]["accepted"]
    assert trace["final_error_codes"] == ["V23"] and comp == s["assessment"]
    note = next(e for p, _, e in seen if e)
    assert "previous_attempt" in note and '"V1"' in note


def test_regenerate_is_dropped_when_not_better(s, monkeypatch):
    limits(monkeypatch, repair_stall_rounds=1, regenerate_on_stall=1)
    comp, _, trace, calls, _ = run(s, monkeypatch, [irrelevant(1)], regen=bad_draft(s))
    assert not trace["regenerations"][0]["accepted"] and "V1" in trace["final_error_codes"]


def test_regenerate_is_off_by_default(s, monkeypatch):
    limits(monkeypatch)
    _, _, trace, calls, _ = run(s, monkeypatch, [irrelevant(1), irrelevant(2)])
    assert trace["regenerations"] == [] and "G9+regen" not in calls
    from profsagent.config import models_cfg
    assert models_cfg()["limits"]["regenerate_on_stall"] == 0


def test_r1_prompt_shows_the_nodes():
    p = load_prompt("R1")
    _, user = p.render(component={}, component_prompt_id="G9", violations=[], frozen_ids=[], context_min={}, round=1,
                       violating_nodes={"quiz": {"type": "quiz", "weight_pct": 40}})
    assert p.version == "0.2.0" and '<context name="violating_nodes">{"quiz": {"type": "quiz", "weight_pct": 40}}' in user
