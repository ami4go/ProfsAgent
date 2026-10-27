"""Evaluation engine (evaluate/engine.py): tiers 1-3 of a finished design. No API calls: tier 2 uses an exact-match
fake embedder, tier 3 a fake LLM, and by default tier 3 is only planned."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.evaluate import engine
from test_evaluation_tier2 import exact_embed
from test_judges import FakeLLM, scores

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def judging_off(monkeypatch):
    monkeypatch.delenv("PROFSAGENT_JUDGE", raising=False)


def read(d: Path, name: str) -> dict:
    return json.loads((d / name).read_text(encoding="utf-8"))


def test_default_makes_no_llm_calls_and_writes_every_tier(s, tmp_path):
    llm, lines = FakeLLM({}), []
    out = engine.evaluate_run(s, tmp_path, llm, log=lines.append)
    assert llm.calls == []
    assert out["tier1"]["verdict"] == read(tmp_path, "evaluation_deterministic.json")["summary"]["verdict"]
    assert out["tier2"]["status"] == "skipped" and "reference_course" in out["tier2"]["reason"]
    assert out["tier3"]["status"] == "planned" and out["tier3"]["calls"] == 0
    assert read(tmp_path, "evaluation_judges.json")["planned_only"] is True
    assert read(tmp_path, "evaluation.json")["verdict"]["verdict"] == out["tier1"]["verdict"]
    assert [ln.split(":")[0] for ln in lines] == ["evaluation (tier 1)", "evaluation (tier 2)", "evaluation (tier 3)"]


def test_tier2_compares_with_a_named_reference_sheet(s, tmp_path):
    s["run_cfg"]["reference_course"] = "cse201"
    out = engine.evaluate_run(s, tmp_path, embed=exact_embed(), log=lambda _: None)
    assert out["tier2"]["status"] == "done" and out["tier2"]["summary"]["reference"] == "CSE201"
    assert read(tmp_path, "evaluation_reference.json")["summary"] == out["tier2"]["summary"]


def test_tier2_uses_a_held_out_course_and_skips_an_unknown_one(s, tmp_path):
    s["run_cfg"]["exclude_courses"] = ["CSE201"]
    assert engine.evaluate_run(s, tmp_path, embed=exact_embed(), log=lambda _: None)["tier2"]["status"] == "done"
    s["run_cfg"] = {"reference_course": "XYZ999"}
    out = engine.evaluate_run(s, tmp_path, log=lambda _: None)
    assert out["tier2"]["status"] == "skipped" and "XYZ999" in out["tier2"]["reason"]


def test_judging_on_runs_the_panel_and_combines_the_verdicts(s, tmp_path, monkeypatch):
    monkeypatch.setattr(engine, "tier1", lambda st: {"summary": {"verdict": "PASS", "errors": 0, "alignment_min_pct": 100.0,
                                                                 "hard_constraints_satisfied_pct": 100.0}})
    llm = FakeLLM({"judge_a": scores(5, 5, 5, 5, 5, 5)})
    out = engine.evaluate_run(s, tmp_path, llm, judge=True, log=lambda _: None)
    assert out["tier3"]["status"] == "judged" and out["tier3"]["calls"] == 1 == len(llm.calls)   # first judge decisive
    assert out["verdict"]["verdict"] == "PASS" and read(tmp_path, "evaluation_judges.json")["summary"]["band"] == "good"


def test_a_tier1_fail_is_not_judged_even_with_judging_on(s, tmp_path, monkeypatch):
    monkeypatch.setenv("PROFSAGENT_JUDGE", "1")
    monkeypatch.setattr(engine, "tier1", lambda st: {"summary": {"verdict": "FAIL", "errors": 3, "alignment_min_pct": 100.0,
                                                                 "hard_constraints_satisfied_pct": 100.0}})
    llm = FakeLLM({"judge_a": scores(5, 5, 5, 5, 5, 5)})
    out = engine.evaluate_run(s, tmp_path, llm, log=lambda _: None)
    assert llm.calls == [] and out["tier3"]["status"] == "skipped" and out["verdict"]["verdict"] == "FAIL"


def test_judging_switch(monkeypatch):
    assert not engine.judging_enabled({})
    assert engine.judging_enabled({"judge": True})
    monkeypatch.setenv("PROFSAGENT_JUDGE", "1")
    assert engine.judging_enabled({})


def test_a_failing_tier_does_not_stop_the_others(s, tmp_path, monkeypatch):
    def boom(st):
        raise KeyError("cos")
    monkeypatch.setattr(engine, "tier1", boom)
    out = engine.evaluate_run(s, tmp_path, FakeLLM({}), log=lambda _: None)
    assert "KeyError" in out["tier1"]["error"] and out["tier3"]["status"] == "planned"
    assert (tmp_path / "evaluation.json").exists()
