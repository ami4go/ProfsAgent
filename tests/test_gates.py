"""Validation layer v2, stage 2: blocking gates. A gate with open errors cannot be approved without a reason (recorded as
an override); auto-approved dev runs record that the gate would have blocked. The gate node is exercised with a fake
runtime and a scripted interrupt(), so no graph, LLM or checkpoint is needed."""
import copy
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.orchestrator import graph as G
from profsagent.validate import engine

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def state():
    s = json.loads(FIXTURE.read_text(encoding="utf-8"))
    s["approvals"] = []
    return s


def clean(s):
    s["violations"] = {k: [x for x in v if x["severity"] != "error"] for k, v in s["violations"].items()}
    return s


# ---------------------------------------------------------------- policy
def test_view_of_a_design_with_open_errors(state):
    view = engine.gate_view(state)
    assert view["blocked"] and view["open_total"] == len(view["open"]) and "V23" in view["open_codes"]
    assert view["coverage"]["errors"] == view["open_total"] and view["coverage"]["constraints"]["total"] > 0


def test_clean_design_is_not_blocked(state):
    assert not engine.gate_view(clean(state))["blocked"]


def test_approve_without_reason_is_refused(state):
    d, problem = engine.resolve_gate(engine.gate_view(state), {"decision": "approve", "by": "Prof X"}, auto=False)
    assert d is None and "reason" in problem


def test_approve_with_reason_records_an_override(state):
    view = engine.gate_view(state)
    d, problem = engine.resolve_gate(view, {"decision": "approve", "by": "Prof X", "comment": "V23 links reviewed by hand"}, auto=False)
    assert problem is None and d["override"] == {"codes": view["open_codes"], "errors": view["open_total"],
                                                  "reason": "V23 links reviewed by hand"}


def test_reject_is_always_allowed(state):
    d, problem = engine.resolve_gate(engine.gate_view(state), {"decision": "reject", "by": "Prof X"}, auto=False)
    assert problem is None and d["decision"] == "reject"


def test_clean_approve_needs_no_reason(state):
    d, problem = engine.resolve_gate(engine.gate_view(clean(state)), {"decision": "approve", "by": "Prof X"}, auto=False)
    assert problem is None and "override" not in d


def test_auto_approval_records_would_block(state):
    d, _ = engine.resolve_gate(engine.gate_view(state), None, auto=True)
    assert d["decision"] == "approve" and d["override"]["would_block"]


# ---------------------------------------------------------------- the gate node
class FakeGraph:
    def freeze_labels(self, labels):
        return []

    def put(self, *a, **k):
        pass


def run_gate(monkeypatch, state, replies, auto=False):
    rt = SimpleNamespace(run_id="gate-test", state=state, graph=FakeGraph(), lines=[], save=lambda: None)
    rt.log = rt.lines.append
    monkeypatch.setitem(G._RT, rt.run_id, rt)
    asked = []

    def fake_interrupt(payload):
        asked.append(copy.deepcopy(payload))
        return replies.pop(0)
    monkeypatch.setattr(G, "interrupt", fake_interrupt)
    out = G._gate("gate2_outcomes", lambda st: {"cos": len(st.get("cos", []))})({"run_id": rt.run_id, "auto_approve": auto})
    return out, rt, asked


def test_gate_asks_again_until_there_is_a_reason(monkeypatch, state):
    out, rt, asked = run_gate(monkeypatch, state, [{"decision": "approve", "by": "Prof X"},
                                                   {"decision": "approve", "by": "Prof X", "comment": "accepted for now"}])
    assert len(asked) == 2 and asked[0]["blocked"] and "problem" in asked[1]
    app = state["approvals"][-1]
    assert out == {} and app["decision"] == "approve" and app["override"]["reason"] == "accepted for now"


def test_gate_reject_stops_the_run(monkeypatch, state):
    out, rt, asked = run_gate(monkeypatch, state, [{"decision": "reject", "by": "Prof X"}])
    assert out == {"rejected_at": "gate2_outcomes"} and len(asked) == 1


def test_auto_gate_records_would_block(monkeypatch, state):
    out, rt, asked = run_gate(monkeypatch, state, [], auto=True)
    assert asked == [] and out == {}
    assert state["would_block"][0]["gate"] == "gate2_outcomes" and "V23" in state["would_block"][0]["codes"]
    assert state["approvals"][-1]["override"]["would_block"]
