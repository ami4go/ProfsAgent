"""Graph facts snapshot and graph checks VKG-PREC / VKG-DUP / VKG-NORM (validation layer v2, Stage 3). Offline: a
small fake KG; the live snapshot test is skipped without Neo4j."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.agents import pipeline
from profsagent.kg import facts
from profsagent.validate import engine, rules

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def norms(level=3, n=40, credits=None, co=(4, 4, 5), bloom=(4, 6, 6), comps=(4, 4, 5)):
    def spread(q1, med, q3):
        return {"n": n, "q1": q1, "median": med, "q3": q3, "lo": q1 - 1.5 * (q3 - q1), "hi": q3 + 1.5 * (q3 - q1)}
    return {"level": level, "n": n, "credits": credits or {"4": n - 2, "2": 2}, "co_count": spread(*co),
            "bloom_max": spread(*bloom), "components": spread(*comps)}


def with_facts(s, **kw):
    s["kg_facts"] = {"version": "test", "level": s["level"], "norms": norms(), "precedence": [], "catalogue_overlap": [], **kw}
    return s


def codes(s):
    return [x["code"] for x in rules.check_kg(s)]


def test_no_snapshot_no_graph_checks(s):
    assert rules.check_kg(s) == [] and "kg" in rules.STAGE_CHECKS


def test_fixture_with_typical_facts_is_quiet(s):
    assert rules.check_kg(with_facts(s)) == []


def test_topic_taught_against_institutional_order(s):
    # M1.T1 is in week 1, M8.T2 in weeks 12-13
    edge = {"from": "M8.T2", "to": "M1.T1", "from_title": "late topic", "to_title": "early topic", "support": 3, "against": 0,
            "courses": ["CSE101", "CSE102", "CSE201"]}
    out = rules.check_kg(with_facts(s, precedence=[edge]))
    assert [x["code"] for x in out] == ["VKG-PREC"] and out[0]["severity"] == "warning" and out[0]["nodes"] == ["M8.T2", "M1.T1"]
    assert "week 12" in out[0]["message"] and "3 IIIT-D courses" in out[0]["message"]
    agree = {**edge, "from": "M1.T1", "to": "M8.T2"}
    assert codes(with_facts(s, precedence=[agree])) == []


def test_duplicate_of_an_undeclared_course(s):
    ov = [{"course_uid": "CSE999", "name": "Same course", "weighted_jaccard": 0.5, "shared_topics": ["a ≈ b"]},
          {"course_uid": "CSE700", "name": "Related", "weighted_jaccard": 0.2, "shared_topics": []}]
    out = rules.check_kg(with_facts(s, catalogue_overlap=ov))
    assert [x["nodes"] for x in out if x["code"] == "VKG-DUP"] == [["CSE999"]]
    s2 = with_facts(copy.deepcopy(s), catalogue_overlap=ov)
    s2["positioning"]["anti_requisites"] = [{"course_uid": "CSE999"}]
    assert codes(s2) == []
    s3 = with_facts(copy.deepcopy(s), catalogue_overlap=[{**ov[0], "course_uid": "CSE201"}])     # the declared prerequisite
    assert codes(s3) == []


def test_unusual_for_the_level(s):
    s = with_facts(s, norms=norms(credits={"4": 39, "2": 1}))
    s["defaults"]["credits"] = 2                         # 1 of 40 same-level courses
    s["cos"] = s["cos"] * 3                              # 12 COs; usual 2.5-6.5
    out = rules.check_kg(s)
    assert sorted(x["nodes"][0] for x in out) == ["co_count", "credits"] and {x["code"] for x in out} == {"VKG-NORM"}


def test_too_few_same_level_courses_to_judge(s):
    s = with_facts(s, norms=norms(n=5))
    s["cos"] = s["cos"] * 3
    assert codes(s) == []


def test_graph_codes_are_professor_warnings(s):
    s = with_facts(s, catalogue_overlap=[{"course_uid": "CSE999", "name": "x", "weighted_jaccard": 0.9, "shared_topics": []}])
    x = next(x for x in engine.check(s, ["kg"]) if x["code"] == "VKG-DUP")
    assert (x["family"], x["fixable_by"], x["stage"]) == ("kg", "professor", "kg")


# ------------------------------------------------------------------ snapshot
class FakeKG:
    embed_name, match_sim = "fake", 0.9

    def __init__(self, fail=False):
        self.fail = fail

    def index(self, exclude=frozenset()):
        if self.fail:
            raise RuntimeError("graph down")
        rows = [{"uid": f"CSE{300 + i}", "name": f"Course {i}", "level": 3, "credits": 4} for i in range(10)]
        return [r for r in rows if r["uid"] not in exclude]

    def course(self, uid, exclude=frozenset()):
        i = int(uid[3:]) - 300
        n = 4 + i % 3
        return {"cos": [{"bloom_lexicon": 3 + i % 3}] * (3 + i % 3), "assessment": [{"weight_pct": 100 / n}] * n}

    def topic_overlap(self, new_topics, uid):
        return {"weighted_jaccard": 0.4 if uid == "CSE305" else 0.0, "shared_topics": [f"{new_topics[0]} ≈ x"]}

    def precedence_evidence(self, titles, exclude=frozenset()):
        return [{"from": titles[-1], "to": titles[0], "support": 2, "against": 0, "courses": ["CSE301", "CSE302"]}]


def test_snapshot_shape_and_ids(s):
    kf = facts.snapshot(FakeKG(), s, {"CSE309"})
    assert set(kf) == {"version", "level", "norms", "precedence", "catalogue_overlap", "method"}
    assert kf["norms"]["n"] == 9 and kf["norms"]["co_count"]["median"] == 4 and kf["norms"]["credits"] == {"4": 9}
    last = s["modules"][-1]["topics"][-1]
    assert kf["precedence"][0]["from"] == last["id"] and kf["precedence"][0]["from_title"] == last["title"]
    assert [o["course_uid"] for o in kf["catalogue_overlap"]] == ["CSE305"]
    assert kf["version"] == facts.snapshot(FakeKG(), s, {"CSE309"})["version"] != facts.snapshot(FakeKG(), s)["version"]
    s["kg_facts"] = kf
    assert {x["code"] for x in rules.check_kg(s)} == {"VKG-PREC", "VKG-DUP"}


class _RT:
    def __init__(self, state, kg):
        self.state, self.kg, self.exclude, self.lines = state, kg, set(), []

    def log(self, msg):
        self.lines.append(msg)


def test_pipeline_records_graph_checks_and_survives_a_graph_failure(s):
    rt = _RT(s, FakeKG())
    pipeline._graph_facts(rt)
    assert {x["code"] for x in s["violations"]["kg"]} == {"VKG-PREC", "VKG-DUP"} and "graph facts:" in rt.lines[-1]
    s2 = json.loads(FIXTURE.read_text(encoding="utf-8"))
    rt2 = _RT(s2, FakeKG(fail=True))
    pipeline._graph_facts(rt2)
    assert s2["kg_facts"] is None and "kg" not in s2["violations"] and "unavailable" in rt2.lines[-1]


def test_live_snapshot(s):
    from test_neo4j_kg import kgs
    neo, _ = kgs()
    kf = facts.snapshot(neo, s)
    assert kf["norms"]["n"] >= 8 and kf["catalogue_overlap"] and kf["method"]["embedder"] == "all-MiniLM-L6-v2"
    s["kg_facts"] = kf
    assert all(x["severity"] == "warning" for x in rules.check_kg(s))
