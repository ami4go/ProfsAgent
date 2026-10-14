"""Evaluation tier 1 (deterministic metrics and verdict). No LLM calls."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.evaluate.deterministic import evaluate

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def passing(s):
    """The fixture without its two known findings: the unevidenced CO–PO claims (V23) and the unresolvable
    'hands-on coding exercises' component constraint (K14, a confirm-warning)."""
    s["copo_computed"] = [r for r in s["copo_computed"] if not r["claimed"] or r["strength_computed"] > 0]
    s["constraints"] = [c for c in s["constraints"] if c["id"] != "K14"]
    return s


def test_report_sections(s):
    ev = evaluate(s)
    assert set(ev) == {"summary", "completeness", "alignment", "constraints", "regulation", "validation", "text", "bloom",
                       "workload", "resources", "gates"}
    assert ev["completeness"]["cos"] == len(s["cos"]) and ev["constraints"]["total"] == len(s["constraints"])


def test_fixture_fails_on_its_open_errors(s):
    ev = evaluate(s)
    assert ev["summary"]["verdict"] == "FAIL" and ev["validation"]["errors_by_code"] == {"V23": ev["summary"]["errors"]}
    assert ev["constraints"]["to_confirm"] == ["K14"] and ev["alignment"]["los_taught_pct"] == 100.0


def test_clean_design_passes(s):
    ev = evaluate(passing(s))
    assert ev["summary"] == {"verdict": "PASS", "errors": 0, "regulation_ok": True, "alignment_min_pct": 100.0,
                             "hard_constraints_satisfied_pct": 100.0, "review_reasons": []}


def test_unenforced_constraint_needs_review(s):
    s = passing(s)
    s["constraints"].append({"id": "K90", "target": "other", "op": "==", "value": True, "hardness": "hard", "raw": "pairs only"})
    ev = evaluate(s)
    assert ev["summary"]["verdict"] == "REVIEW" and ev["constraints"]["unenforced"] == ["K90"]


def test_untaught_lo_lowers_alignment(s):
    s = passing(s)
    target = s["los"][-1]["id"]
    for t in (t for m in s["modules"] for t in m["topics"]):
        t["serves_los"] = [x for x in t["serves_los"] if x != target]
    ev = evaluate(s)
    assert ev["alignment"]["los_taught_pct"] < 100 and ev["summary"]["verdict"] == "FAIL"   # T5: LO not taught


def test_regulation_failure_is_reported(s):
    s = passing(s)
    s["weeks"] = 50
    ev = evaluate(s)
    assert not ev["summary"]["regulation_ok"] and ev["regulation"][0]["code"] == "VREG-WEEKS"


def test_would_block_and_overrides_are_counted(s):
    s["approvals"] = [{"gate": "gate1_context", "decision": "approve", "override": {"codes": ["V23"], "would_block": True}}]
    s["would_block"] = [{"gate": "gate1_context", "codes": ["V23"], "errors": 4}]
    ev = evaluate(s)
    assert ev["gates"] == {"approvals": 1, "overrides": 1, "would_block": ["gate1_context"]}
