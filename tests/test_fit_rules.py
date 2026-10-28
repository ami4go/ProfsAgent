"""Course-fit warnings (family "fit", settled by the professor): VC-AUDIENCE (a title naming a broad audience at
level 3+) and VC-NOLAB (mostly hands-on LOs, no lab hours, no lab decision). Uses the committed clean CS-601 design."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.validate import engine

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def found(s, code, stage):
    return [x for x in engine.check(s, [stage]) if x["code"] == code]


def test_clean_design_has_no_fit_warnings(s):
    assert not found(s, "VC-AUDIENCE", "intake") and not found(s, "VC-NOLAB", "los")


# ------------------------------------------------------------------ VC-AUDIENCE
@pytest.mark.parametrize("title", ["Web Development for All", "Python for Everyone", "Statistics for Non-Majors", "Design 101"])
def test_broad_audience_title_at_level_3_is_flagged_for_the_professor(s, title):
    s["form"]["1. COURSE NAME"] = title
    (x,) = found(s, "VC-AUDIENCE", "intake")
    assert (x["severity"], x["family"], x["fixable_by"]) == ("warning", "fit", "professor")
    assert x["evidence"]["level"] == 3 and "inferred" in x["message"]       # the fixture's level was not given


@pytest.mark.parametrize("title", ["Introduction to Transformer Architecture", "Foundations of Finance", "Compiler Optimisation"])
def test_introduction_and_foundations_are_not_audience_words(s, title):
    s["form"]["1. COURSE NAME"] = title                    # most IIIT-D "Introduction to ..." courses are level 5-6
    assert not found(s, "VC-AUDIENCE", "intake")


def test_broad_audience_title_at_level_1_or_2_is_fine(s):
    s["form"]["1. COURSE NAME"], s["level"] = "Web Development for All", 2
    assert not found(s, "VC-AUDIENCE", "intake")


def test_a_given_level_is_reported_as_given(s):
    s["form"]["1. COURSE NAME"] = "Web Development for All"
    s["cco"]["fields"]["level_or_code"]["status"] = "given"
    (x,) = found(s, "VC-AUDIENCE", "intake")
    assert "as given" in x["message"] and x["evidence"]["level_given"] is True


# ------------------------------------------------------------------ VC-NOLAB
def no_lab(s, hands_on: int, lab_required=None):
    s["ltp"]["P"], s["lab_required"] = 0, lab_required
    for i, lo in enumerate(s["los"]):
        lo["hands_on"] = i < hands_on
    return s


def test_mostly_hands_on_los_without_lab_hours_are_flagged(s):
    (x,) = found(no_lab(s, 9), "VC-NOLAB", "los")
    assert (x["severity"], x["family"], x["fixable_by"]) == ("warning", "fit", "professor")   # R1 must not "repair" L-T-P
    assert x["evidence"]["share"] == 0.75 and len(x["evidence"]["hands_on"]) == 9


def test_a_professor_who_said_no_lab_is_not_asked_again(s):
    assert not found(no_lab(s, 12, lab_required="no"), "VC-NOLAB", "los")   # the CSE201 runs: tutorials by choice


def test_few_hands_on_los_or_a_lab_need_no_warning(s):
    assert not found(no_lab(s, 5), "VC-NOLAB", "los")                        # 5/12 < 0.5
    s = no_lab(s, 12)
    s["ltp"]["P"] = 2
    assert not found(s, "VC-NOLAB", "los")


def test_fit_warnings_never_reach_the_repair_step(s):
    s["form"]["1. COURSE NAME"] = "Web Development for All"
    vs = engine.check(no_lab(s, 12))
    fit = [x for x in vs if x["family"] == "fit"]
    assert {x["code"] for x in fit} == {"VC-AUDIENCE", "VC-NOLAB"}
    assert not engine.errors(fit) and all(x["fixable_by"] == "professor" for x in fit)


def test_fit_warnings_send_a_design_to_review_not_fail(s):
    from profsagent.evaluate.deterministic import evaluate
    base = evaluate(s)["summary"]
    s["form"]["1. COURSE NAME"] = "Web Development for All"     # (P = 0 on this design would add a real lab-plan error)
    summary = evaluate(s)["summary"]
    assert summary["errors"] == base["errors"]                                # a warning only: no new errors
    assert any("(VC-AUDIENCE)" in r for r in summary["review_reasons"])
    assert summary["verdict"] in ("REVIEW", "FAIL") and (base["verdict"] == "FAIL") == (summary["verdict"] == "FAIL")
