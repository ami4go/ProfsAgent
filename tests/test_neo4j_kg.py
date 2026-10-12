"""Contract tests: Neo4jKG answers the KGClient questions in the same shapes as StubKG.

Needs Neo4j running with the Layer A graph loaded (python src/profsagent/ingest/load.py --wipe); skipped otherwise.
No LLM calls: retrieval runs BM25-only and topic matching returns no candidates, as the stub does without an LLM.
"""
import sys
from functools import lru_cache
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest

from profsagent.kg.stub import StubKG


@lru_cache(maxsize=1)
def _load():
    try:
        from neo4j.exceptions import AuthError, ServiceUnavailable
        from profsagent.kg.neo4j_kg import Neo4jKG
    except ImportError as e:
        return e
    try:
        return Neo4jKG(), StubKG()
    except (ServiceUnavailable, AuthError) as e:
        return e


def kgs():
    r = _load()
    if isinstance(r, Exception):
        pytest.skip(f"Neo4j graph not available ({type(r).__name__})")
    return r


def test_index_rows_have_stub_shape():
    neo, stub = kgs()
    rows = neo.index()
    assert len(rows) > 400
    assert set(rows[0]) == set(stub.index()[0])
    assert all(r["uid"] == r["aliases"][0] for r in rows)


def test_course_has_stub_shape_for_every_stub_course():
    neo, stub = kgs()
    for uid in sorted(stub.sheets):
        c, s = neo.course(uid), stub.course(uid)
        assert c is not None, uid
        assert set(s) <= set(c), (uid, set(s) - set(c))
        for key in ("cos", "prereqs", "weeks", "assessment", "resources"):
            if s[key] and c[key]:
                assert set(s[key][0]) == set(c[key][0]), (uid, key)


def test_resolve_official_old_and_formatted_codes():
    neo, _ = kgs()
    assert neo.resolve("CSE601") == "CSE601"
    assert neo.resolve("CSE 301") == "CSE601"      # old code on the Compilers sheet, kept as an alias
    assert neo.resolve("cse-101") == "CSE101"
    assert neo.resolve("XYZ999") is None


def test_exclude_hides_a_course_everywhere():
    neo, _ = kgs()
    x, ex = "CSE201", {"CSE201"}
    query = "Advanced Programming object oriented design patterns Java"
    assert neo.course(x, exclude=ex) is None
    assert x not in [r["uid"] for r in neo.index(exclude=ex)]
    assert x in [h["uid"] for h in neo.search_courses(query, k=10)]
    assert x not in [h["uid"] for h in neo.search_courses(query, k=10, exclude=ex)]
    assert not [e for e in neo.exemplar_cos(query, 2, k=20, exclude=ex) if e["uid"].startswith(x + "/")]
    assert neo.priors(exclude=ex)["n_courses"] == neo.priors()["n_courses"] - 1
    assert all(p["uid"] != x for r in neo.index() for p in (neo.course(r["uid"], exclude=ex) or {}).get("prereqs", []))


def test_priors_have_stub_shape_and_real_weights():
    neo, stub = kgs()
    p, s = neo.priors(), stub.priors()
    assert set(p) == set(s)
    assert p["weights"]["endsem"]["n"] > 100
    lo, hi = p["weights"]["endsem"]["iqr"]
    assert lo <= p["weights"]["endsem"]["median"] <= hi


def test_corpus_resources_have_stub_shape():
    neo, stub = kgs()
    res = neo.corpus_resources(["CSE101"])
    assert res and set(res[0]) == set(stub.corpus_resources(["CSE101"])[0])
    assert all(r["resource_uid"].startswith("R:") and "CSE101" in r["used_by_courses"] for r in res)


def test_search_finds_the_right_course():
    neo, _ = kgs()
    assert "CSE601" in [h["uid"] for h in neo.search_courses("compilers lexical analysis parsing code generation", k=5)]


def test_topic_methods_without_llm_behave_like_the_stub():
    neo, stub = kgs()
    assert neo.topic_candidates(["graph algorithms"]) == stub.topic_candidates(["graph algorithms"])
    ov = neo.topic_overlap(["graph algorithms"], "CSE222")
    assert ov["weighted_jaccard"] == 0.0 and ov["shared_topics"] == []
    assert neo.topic_precedence(["T:graphs"]) == []
