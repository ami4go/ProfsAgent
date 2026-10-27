"""Phase 1 simplification: the readable validation report and the core/full validation profile. No LLM calls."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.config import validation_profile
from profsagent.validate import engine, report, rules, semantic

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_repeats_of_one_check_become_one_row(s):
    vs = engine.recorded(s)
    rows = report.grouped(vs)
    v23 = [r for r in rows if r["code"] == "V23" and r["severity"] == "error"]
    assert len(v23) == 1 and v23[0]["count"] == len([x for x in vs if x["code"] == "V23" and x["severity"] == "error"]) > 1
    assert v23[0]["group"] == "CO–PO mapping"
    assert len(rows) < len(vs) and sum(r["count"] for r in rows) == len(vs)          # nothing is dropped, only merged


def test_errors_come_first_and_groups_are_plain(s):
    rows = report.grouped(engine.recorded(s))
    sev = [r["severity"] for r in rows]
    assert sev == sorted(sev, key=lambda x: x != "error")
    assert {r["group"] for r in rows} <= set(report.GROUPS)


def test_group_of_each_family():
    assert report.group_of({"code": "VREG-WEEKS", "stage": "intake"}) == "University regulations and course template"
    assert report.group_of({"code": "VK", "stage": "assessment"}) == "Your requirements"
    assert report.group_of({"code": "V14", "stage": "positioning"}) == "IIIT-D catalogue"
    assert report.group_of({"code": "VLO-COPY", "stage": "los"}) == "Outcomes (COs and LOs)"
    assert report.group_of({"code": "V19", "stage": "assessment"}) == "Assessment plan"
    assert report.group_of({"code": "VT-ORDER", "stage": "schedule"}) == "Topics, schedule and labs"


def test_gate_lines_show_errors_and_count_warnings(s):
    vs = engine.recorded(s)
    lines = report.lines(vs, errors_only=True)
    assert lines[0] == "CO–PO mapping:" and "[error] 4×" in lines[1]
    assert lines[-1].startswith("Warnings (not blocking):")
    assert not any("[warning]" in ln for ln in lines)
    view = engine.gate_view(s)
    assert view["report"] == lines and view["blocked"]


def test_appendix_table(s):
    md = report.markdown(engine.recorded(s))
    s_ = report.summary(engine.recorded(s))
    assert md.startswith(f"**{s_['errors']} errors, {s_['warnings']} warnings.**") and "| Area | Severity |" in md


def test_profile_defaults_to_core_and_env_overrides(monkeypatch):
    monkeypatch.delenv("PROFSAGENT_VALIDATION", raising=False)
    assert validation_profile() == "core"
    monkeypatch.setenv("PROFSAGENT_VALIDATION", "full")
    assert validation_profile() == "full"
    monkeypatch.setenv("PROFSAGENT_VALIDATION", "everything")
    with pytest.raises(ValueError):
        validation_profile()


def test_core_profile_switches_the_research_extras_off(monkeypatch):
    monkeypatch.delenv("PROFSAGENT_VALIDATION", raising=False)
    semantic.configure(lambda texts: None, "fake")
    cfg = {}
    engine.configure(cfg)
    assert cfg["validation_profile"] == "core" and not semantic.enabled()
    resumed = {"validation_profile": "full"}               # a resumed run keeps the profile it started with
    monkeypatch.setenv("PROFSAGENT_SEMANTIC", "off")       # (no model load in the test)
    engine.configure(resumed)
    assert resumed["validation_profile"] == "full"
    semantic.configure(None)


def test_core_checks_are_unchanged(s):
    semantic.configure(None)
    assert {x["code"] for x in rules.errors(rules.run(s))} == {"V23", "VT-TEMPLATE"}           # same baseline as the defect suite
