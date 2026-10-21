"""The llm validation profile: hard rules in code + one LLM check per stage. No API calls: the LLM is faked."""
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.agents import pipeline
from profsagent.llm.prompts import load_prompt
from profsagent.validate import engine, llm_check, report, rules

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def off_after():
    yield
    llm_check.configure(None)


class FakeLLM:
    def __init__(self, findings=None, fail=False):
        self.findings, self.fail, self.calls = findings or [], fail, []

    def structured(self, *, system, user, model_cls, role, temperature, prompt_id, prompt_version, run_id=None):
        self.calls.append({"role": role, "prompt_id": prompt_id, "user": user})
        if self.fail:
            raise RuntimeError("quota exhausted")
        return model_cls.model_validate({"findings": self.findings}), SimpleNamespace(endpoint="fake:checker")


def test_off_means_every_rule_as_before(s):
    llm_check.configure(None)
    assert [x["code"] for x in engine.check(s, ["los"])] == [x["code"] for x in rules.run(s, ["los"])]


def test_hard_rules_plus_llm_findings(s):
    fake = FakeLLM([{"item": "los.narrower", "nodes": ["CO1.LO3"], "issue": "restates CO1", "fix": "narrow the object"},
                    {"item": "builds_up", "nodes": ["CO2.LO1"], "issue": "order", "fix": ""}])
    llm_check.configure(fake, "test")
    vs = engine.check(s, ["los"])
    assert all(x["code"] in llm_check.hard_rules() or x["code"].startswith("LLM:") for x in vs)
    llm = {x["code"]: x for x in vs if x["code"].startswith("LLM:")}
    assert llm["LLM:los.narrower"]["severity"] == "error" and llm["LLM:los.builds_up"]["severity"] == "warning"   # from the checklist
    x = llm["LLM:los.narrower"]
    assert (x["family"], x["fixable_by"], x["stage"]) == ("llm", "repair", "los") and x["fix_hint"] == "narrow the object"
    assert fake.calls[0]["role"] == "check" and fake.calls[0]["prompt_id"] == "C1"
    assert report.group_of(x) == "Outcomes (COs and LOs)"


def test_judgement_rules_leave_code_under_the_llm_profile(s):
    s["los"][0]["statement"] = s["cos"][0]["statement"]          # VLO-COPY in code; a judgement item now
    llm_check.configure(FakeLLM(), "test")
    assert "VLO-COPY" not in {x["code"] for x in engine.check(s, ["los"])}
    llm_check.configure(None)
    assert "VLO-COPY" in {x["code"] for x in engine.check(s, ["los"])}


def test_structure_and_schedule_share_one_call_and_results_are_cached(s):
    fake = FakeLLM()
    llm_check.configure(fake, "test")
    engine.check(s, ["structure", "schedule"])
    engine.check(s, ["structure", "schedule"])
    assert len(fake.calls) == 1 and 'checklist structure' in fake.calls[0]["user"] and 'checklist schedule' not in fake.calls[0]["user"]


def test_unknown_item_is_a_warning(s):
    llm_check.configure(FakeLLM([{"item": "something_else", "nodes": [], "issue": "x"}]), "test")
    x = next(x for x in engine.check(s, ["cos"]) if x["code"].startswith("LLM:"))
    assert x["code"] == "LLM:cos.other" and x["severity"] == "warning"


def test_a_failed_check_never_stops_the_run(s):
    llm_check.configure(FakeLLM(fail=True), "test")
    vs = engine.check(s, ["assessment"])
    note = [x for x in vs if x["code"] == "LLM:unavailable"]
    assert note and note[0]["severity"] == "warning" and "hard rules" in note[0]["message"]


def test_budget_caps_the_calls(s, monkeypatch):
    fake = FakeLLM()
    llm_check.configure(fake, "test")
    monkeypatch.setattr(llm_check, "cfg", lambda: {**llm_check.load_yaml("config/llm_check.yaml"), "budget_calls_per_run": 1})
    engine.check(s, ["cos"])
    vs = engine.check(s, ["los"])
    assert len(fake.calls) == 1 and any("budget" in x["message"] for x in vs if x["code"] == "LLM:unavailable")


def test_whole_design_review_is_one_call(s):
    fake = FakeLLM([{"item": "assessment.measures_los", "nodes": ["A:Quiz1"], "issue": "recall quiz for an L5 LO", "fix": "x"}])
    f, info = llm_check.review_design(s, fake)
    assert info["calls"] == 1 and len(fake.calls) == 1 and f[0]["stage"] == "assessment" and f[0]["severity"] == "error"
    for st in llm_check.cfg()["stages"]:
        assert f"checklist {st}" in fake.calls[0]["user"]


def test_prompt_renders_without_validator_findings(s):
    system, user = load_prompt("C1").render(**llm_check._payload(s, ["cos"]))
    assert "Only the checklist" in system and '<context name="design cos">' in user and "V23" not in user


def test_profile_switches_the_checker(monkeypatch):
    monkeypatch.setenv("PROFSAGENT_SEMANTIC", "off")
    cfg = {"validation_profile": "llm"}
    pipeline._set_validation_profile(cfg, FakeLLM(), "run")
    assert llm_check.enabled()
    pipeline._set_validation_profile({"validation_profile": "core"}, FakeLLM(), "run")
    assert not llm_check.enabled()


def test_comparison_counts_only_errors_where_the_defect_is():
    spec = importlib.util.spec_from_file_location("compare_validation", ROOT / "scripts/compare_validation.py")
    cmp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cmp)
    t = {"nodes": ["CO1", "CO2"], "stages": ["cos"]}
    err = {"severity": "error", "code": "LLM:cos.distinct", "stage": "cos"}
    assert cmp.llm_detects([{**err, "nodes": ["CO2"]}], set(), t)
    assert not cmp.llm_detects([{**err, "nodes": ["CO4"]}], set(), t)               # an error elsewhere is not a detection
    assert not cmp.llm_detects([{**err, "nodes": ["CO1"], "severity": "warning"}], set(), t)
    lo_dup = {**err, "code": "LLM:los.distinct", "stage": "los", "nodes": ["CO1.LO13"]}
    assert cmp.llm_detects([lo_dup], set(), {"nodes": ["CO1"], "stages": ["los"]})          # an LO of CO1 is part of CO1
    assert not cmp.llm_detects([lo_dup], set(), {"nodes": ["CO1"], "stages": ["copo"]})     # ...but not a CO-PO defect
    t2 = {"nodes": [], "stages": ["schedule"]}
    assert cmp.llm_detects([{**err, "code": "LLM:structure.order", "stage": "structure", "nodes": []}], set(), t2)
    assert not cmp.llm_detects([{**err, "code": "LLM:structure.order", "stage": "structure", "nodes": []}],
                               {("LLM:structure.order", ())}, t2)                   # also reported on the clean design
    placeholder = {**err, "code": "LLM:los.narrower", "stage": "los", "nodes": ["CO1.LO3"]}
    assert not cmp.llm_detects([placeholder], {("LLM:los.narrower", ("CO1.LO3",))},
                               {"nodes": ["CO1.LO1", "CO1.LO3"], "stages": ["los"]})  # same finding as on the clean design
