"""Evaluation tier 3: judge panel, cascade, bias controls, agreement (validation layer v2, Stage 5). No API calls:
the LLM client is faked, so these tests spend no quota."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.evaluate import judges
from profsagent.evaluate.agreement import krippendorff_alpha, length_bias, panel_agreement, weighted_kappa
from profsagent.llm.prompts import load_prompt

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"
DIMS = list(judges.rubrics())


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def scores(*vals, comment=""):
    return {"dimensions": [{"dimension": d, "evidence": ["CO1"], "reasoning": "r", "score": v} for d, v in zip(DIMS, vals)],
            "overall_comment": comment}


class FakeLLM:
    """replies[role] -> a JudgeScores dict, a list of PairwiseVerdicts dicts (one per call), or an Exception."""
    def __init__(self, replies, gemini=True, groq=False):
        self.replies, self.calls = replies, []
        self.gemini_keys, self.groq_keys = (["k"] if gemini else []), (["g"] if groq else [])

    def structured(self, *, system, user, model_cls, role, temperature, prompt_id, prompt_version, run_id=None):
        self.calls.append((role, prompt_id, user))
        r = self.replies[role]
        if isinstance(r, Exception):
            raise r
        if isinstance(r, list):
            r = r.pop(0)
        return model_cls.model_validate(r), SimpleNamespace(endpoint=f"fake:{role}", ok=True)


# ------------------------------------------------------------------ what judges see, who judges
def test_judges_never_see_validator_findings_or_the_narrative(s):
    d = judges.design_excerpt(s)
    assert set(d) >= {"cos", "los", "modules", "assessment", "labs"}
    text = json.dumps(d)
    assert s["narrative"]["sequencing_rationale"] and s["narrative"]["sequencing_rationale"][:60] not in text
    assert "violations" not in text and "V23" not in text
    assert d["modules"][0]["topics"][0]["weeks"] == s["schedule"]["topic_weeks"][d["modules"][0]["topics"][0]["id"]]
    system, user = load_prompt("J1").render(brief=judges.brief_excerpt(s), design=d, rubrics=judges.rubrics())
    assert "Length is not quality" in system and '<context name="design">' in user and "V23" not in user


def test_panel_skips_the_generator_model_and_providers_without_keys(s):
    panel, skipped = judges.select_panel(s, FakeLLM({}))
    assert panel == ["judge_a", "judge_b"]                                 # fixture: 6 of 7 stages by gemini-3.5-flash-lite
    why = {x["judge"]: x["why"] for x in skipped}
    assert "self-preference" in why["judge_d"] and "no API key" in why["judge_c"]
    panel2, _ = judges.select_panel(s, FakeLLM({}, groq=True))
    assert panel2 == ["judge_a", "judge_b", "judge_c"]


def test_generator_models_read_cached_endpoints(s):
    assert judges.generator_models(s)["gemini:gemini-3.5-flash-lite"] == 6


# ------------------------------------------------------------------ cascade and aggregation
def test_tier1_fail_is_not_judged_unless_forced(s):
    llm = FakeLLM({"judge_a": scores(5, 5, 5, 5, 5, 5)})
    rep = judges.evaluate_judges(s, llm, tier1_verdict="FAIL")
    assert rep["calls"] == 0 and "Tier 1" in rep["skipped"] and llm.calls == []
    rep = judges.evaluate_judges(s, llm, tier1_verdict="FAIL", force=True)
    assert rep["calls"] == 1 and rep["summary"]["band"] == "good"


def test_clearly_good_first_judge_stops_the_cascade(s):
    llm = FakeLLM({"judge_a": scores(5, 4, 4, 5, 4, 5), "judge_b": scores(1, 1, 1, 1, 1, 1)})
    rep = judges.evaluate_judges(s, llm, tier1_verdict="PASS")
    assert [c[0] for c in llm.calls] == ["judge_a"] and "clearly good" in rep["cascade_stop"]
    assert rep["agreement"] is None and rep["summary"]["judges_used"] == 1


def test_uncertain_first_judge_calls_the_panel_and_flags_disagreement(s):
    llm = FakeLLM({"judge_a": scores(3, 3, 4, 3, 3, 4), "judge_b": scores(5, 3, 4, 3, 1, 4)})
    rep = judges.evaluate_judges(s, llm, tier1_verdict="PASS")
    assert [c[0] for c in llm.calls] == ["judge_a", "judge_b"] and rep["calls"] == 2
    co = rep["dimensions"]["co_quality"]
    assert co["median"] == 4 and co["spread"] == 2 and co["disagreement"]
    assert set(rep["summary"]["disagreements"]) == {"co_quality", "assessment_validity"}
    assert rep["agreement"]["judges"] == ["judge_a", "judge_b"] and "judge_a~judge_b" in rep["agreement"]["weighted_kappa"]


def test_no_cascade_always_uses_the_panel(s):
    llm = FakeLLM({"judge_a": scores(5, 5, 5, 5, 5, 5), "judge_b": scores(5, 5, 5, 5, 5, 4)})
    rep = judges.evaluate_judges(s, llm, tier1_verdict="PASS", cascade=False)
    assert rep["calls"] == 2 and "cascade_stop" not in rep


def test_a_failing_judge_is_reported_and_the_rest_still_count(s):
    llm = FakeLLM({"judge_a": RuntimeError("429 quota"), "judge_b": scores(4, 4, 4, 4, 4, 4)})
    rep = judges.evaluate_judges(s, llm, tier1_verdict="PASS")
    assert rep["summary"]["missing_judges"] == ["judge_a"] and rep["summary"]["judges_used"] == 1
    assert "429" in rep["judges"]["judge_a"]["error"]
    assert judges.combined_verdict("PASS", rep)["verdict"] == "REVIEW"


def test_unknown_or_repeated_dimensions_are_ignored(s):
    reply = scores(4, 4, 4, 4, 4)                                           # brief_fit missing
    reply["dimensions"] += [{"dimension": "co_quality", "score": 1}, {"dimension": "made_up", "score": 1}]
    llm = FakeLLM({"judge_a": reply, "judge_b": scores(4, 4, 4, 4, 4, 4)})
    rep = judges.evaluate_judges(s, llm, tier1_verdict="PASS", cascade=False)
    assert rep["judges"]["judge_a"]["scores"]["co_quality"] == 4 and rep["judges"]["judge_a"]["scores"]["brief_fit"] is None
    assert rep["dimensions"]["brief_fit"]["n"] == 1 and "made_up" not in rep["dimensions"]


def test_combined_verdict(s):
    good = {"summary": {"band": "good", "mean": 4.5, "min": 4, "disagreements": [], "missing_judges": []}}
    assert judges.combined_verdict("PASS", good) == {"verdict": "PASS", "reasons": []}
    assert judges.combined_verdict("FAIL", good)["verdict"] == "FAIL"                     # judges never overrule errors
    weak = {"summary": {**good["summary"], "band": "weak", "mean": 1.8}}
    assert judges.combined_verdict("PASS", weak)["verdict"] == "REVIEW"                   # ...and never fail a design
    assert judges.combined_verdict("PASS", {"skipped": "no judge available"})["verdict"] == "REVIEW"


def test_plan_makes_no_calls(s):
    llm = FakeLLM({})
    p = judges.plan(s, llm, "PASS")
    assert llm.calls == [] and p["calls_min"] == 1 and p["calls_max"] == 2 and p["prompt_tokens_est"] > 1000
    assert judges.plan(s, llm, "FAIL")["calls_max"] == 0


# ------------------------------------------------------------------ pairwise, both orders
def verdicts(*picks):
    return {"dimensions": [{"dimension": d, "evidence": [], "better": b} for d, b in zip(DIMS, picks)]}


def test_position_biased_judge_counts_as_ties(s):
    llm = FakeLLM({"judge_a": [verdicts(*"111111"), verdicts(*"111111")]})       # always prefers whatever comes first
    rep = judges.compare(s, s, llm, "judge_a")
    assert rep["wins"] == {"A": 0, "B": 0, "tie": 6} and rep["position_consistency"] == 0.0 and rep["calls"] == 2


def test_consistent_preference_wins(s):
    # order A,B: design 1 (A) better on the first three; order B,A: design 2 (A again) better on the same three
    llm = FakeLLM({"judge_a": [verdicts("1", "1", "1", "tie", "tie", "2"), verdicts("2", "2", "2", "tie", "tie", "1")]})
    rep = judges.compare(s, s, llm, "judge_a")
    assert rep["wins"] == {"A": 3, "B": 1, "tie": 2} and rep["position_consistency"] == 1.0
    assert rep["dimensions"]["brief_fit"] == {"order_ab": "B", "order_ba": "B", "winner": "B"}
    second_user = llm.calls[1][2]
    assert second_user.index('"design_1"') < second_user.index('"design_2"')


# ------------------------------------------------------------------ agreement statistics
def test_krippendorff_alpha_matches_the_published_example():
    n = None   # Krippendorff (2011), "Computing Krippendorff's alpha-reliability", 4 coders x 12 units
    data = [[1, 2, 3, 3, 2, 1, 4, 1, 2, n, n, n], [1, 2, 3, 3, 2, 2, 4, 1, 2, 5, n, 3],
            [n, 3, 3, 3, 2, 3, 4, 2, 2, 5, 1, n], [1, 2, 3, 3, 2, 4, 4, 1, 2, 5, 1, n]]
    assert krippendorff_alpha(data, "nominal") == 0.743 and krippendorff_alpha(data, "interval") == 0.849
    assert krippendorff_alpha([[3, 4, 5], [3, 4, 5]]) == 1.0 and krippendorff_alpha([[3], [None]]) is None


def test_weighted_kappa_and_length_bias():
    assert weighted_kappa([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]) == 1.0
    assert weighted_kappa([1, 2, 3, 4, 5], [2, 3, 4, 5, 5]) > weighted_kappa([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert length_bias([100, 200, 300, 400], [2, 3, 4, 5]) == 1.0 and length_bias([1, 2], [1, 2]) is None
    pa = panel_agreement({"a": {"x": 4, "y": 2}, "b": {"x": 4, "y": 2}})
    assert pa["krippendorff_alpha_interval"] == 1.0 and pa["weighted_kappa"] == {"a~b": 1.0}
