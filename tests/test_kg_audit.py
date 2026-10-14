"""Layer A audit (validation layer v2, Stage 3) and deterministic canonical topic ids. No LLM calls; the Neo4j test is
skipped when the graph is not running."""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.ingest import canonicalise
from profsagent.kg import audit


def course(code, cos=("CO1", "CO2"), weeks=None, assess=((50, "Midsem"), (50, "Endsem")), prereqs=(), aliases=(), level=2):
    weeks = weeks if weeks is not None else [{"week": "1", "lecture_topics": ["Sorting"], "cos_met": ["CO1"]},
                                            {"week": "2", "lecture_topics": ["Hashing"], "cos_met": ["CO2"]}]
    return {"header": {"course_code": code, "aliases": list(aliases), "level": level, "credits": 4,
                       "prerequisite_links": [{"code": p, "kind": k, "sources": ["sheet"]} for p, k in prereqs]},
            "outcomes": [{"label": c, "raw_text": "Implement sorting algorithms for a given input size", "bloom_level": "Apply"}
                         for c in cos],
            "weekly_plan": weeks, "assessments": [{"type_label": n, "weight_pct": w} for w, n in assess]}


def write(tmp_path, courses, mapping=None):
    d = tmp_path / "enriched"
    d.mkdir()
    for c in courses:
        (d / f"{c['header']['course_code']}.json").write_text(json.dumps(c), encoding="utf-8")
    topics = {t for c in courses for w in c["weekly_plan"] for t in w["lecture_topics"]}
    mapping = mapping if mapping is not None else {t: {"canonical_id": canonicalise.canonical_id(t), "canonical_name": t} for t in topics}
    m = tmp_path / "mapping.json"
    m.write_text(json.dumps(mapping), encoding="utf-8")
    return d, m


def codes(rep, course=None):
    return {x["code"] for x in rep["findings"] if course is None or x["course"] == course}


def test_clean_courses_have_no_findings(tmp_path):
    weeks = [{"week": "1", "lecture_topics": ["Trees"], "cos_met": ["CO1"]}, {"week": "2", "lecture_topics": ["Heaps"], "cos_met": ["CO2"]}]
    rep = audit.audit_files(*write(tmp_path, [course("CSE101"), course("CSE102", weeks=weeks, prereqs=[("CSE101", "mandatory")])]))
    assert rep["findings"] == [] and rep["stats"]["courses"] == 2


def test_load_breaking_data_is_an_error(tmp_path):
    weeks = [{"week": "1", "lecture_topics": ["Sorting"], "cos_met": ["CO1", "CO9"]},
             {"week": "1", "lecture_topics": ["Hashing"], "cos_met": ["CO2"]}]
    bad = course("CSE201", cos=("CO1", "CO2", "CO2"), weeks=weeks, prereqs=[("CSE999", "mandatory"), ("CSE201", "mandatory")])
    rep = audit.audit_files(*write(tmp_path, [bad]))
    assert {"KA-CO-DUP", "KA-CO-REF", "KA-WEEK-DUP", "KA-PREREQ-DANGLING", "KA-PREREQ-SELF"} <= codes(rep, "CSE201")
    assert all(x["severity"] == "error" for x in rep["findings"] if x["code"] in {"KA-CO-DUP", "KA-WEEK-DUP"})


def test_corpus_level_checks(tmp_path):
    a = course("CSE301", prereqs=[("CSE302", "mandatory")], aliases=["CSE301A"])
    b = course("CSE302", prereqs=[("CSE301", "mandatory")], aliases=["CSE301A"])     # cycle + shared alias + same sheet
    c = course("CSE303", weeks=[{"week": "1", "lecture_topics": ["Graphs"], "cos_met": []}], assess=((40, "Quiz"), (40, "Endsem")))
    mapping = {"Sorting": {"canonical_id": "TOPIC_A", "canonical_name": "Sorting"},
               "Hashing": {"canonical_id": "TOPIC_B", "canonical_name": "hashing"},
               "Old topic": {"canonical_id": "TOPIC_C", "canonical_name": "Hashing"}}           # same slug as TOPIC_B; unused
    rep = audit.audit_files(*write(tmp_path, [a, b, c], mapping))
    got = codes(rep)
    assert {"KA-PREREQ-CYCLE", "KA-ALIAS", "KA-DUP-SHEET", "KA-TOPIC-UNMAPPED", "KA-TOPIC-SLUG", "KA-TOPIC-STALE", "KA-WEIGHTS"} <= got
    assert "KA-CO-UNMET" not in got          # CSE303's weeks map to no CO at all: not a per-CO gap


def test_bloom_tagger_disagreement(tmp_path):
    c = course("CSE401")
    c["outcomes"] = [{"label": "CO1", "raw_text": "Design a compiler front end for a given grammar", "bloom_level": "Create"},
                     {"label": "CO2", "raw_text": "Explain and design caches", "bloom_level": "Create"},     # lexicon: explain = 2
                     {"label": "CO3", "raw_text": "Students will gain exposure to systems", "bloom_level": "Unclassified"}]
    rep = audit.audit_files(*write(tmp_path, [c]))
    dis = next(x for x in rep["findings"] if x["code"] == "KA-BLOOM-DISAGREE")
    assert dis["n"] == 1 and "CO2" in dis["message"]
    assert next(x for x in rep["findings"] if x["code"] == "KA-BLOOM-UNCLASSIFIED")["n"] == 1


def test_real_corpus_audit_runs():
    rep = audit.audit_files()
    assert rep["stats"]["courses"] > 400 and rep["stats"]["canonical_topics"] > 1000
    assert set(rep["summary"]["by_code"]) <= set(audit.CHECKS)
    assert "KA-TOPIC-UNMAPPED" not in rep["summary"]["by_code"]      # every lecture topic is loaded
    assert audit.table(rep).startswith("code")


def test_neo4j_matches_the_files():
    try:
        import os
        from dotenv import load_dotenv
        from neo4j import GraphDatabase
        from neo4j.exceptions import AuthError, ServiceUnavailable
        load_dotenv(ROOT / ".env")
        drv = GraphDatabase.driver(os.getenv("NEO4J_URI", "bolt://localhost:7687"),
                                   auth=(os.getenv("NEO4J_USER", "neo4j"), os.getenv("NEO4J_PASSWORD", "")))
        rep = audit.audit_neo4j(drv)
        drv.close()
    except (ImportError, ServiceUnavailable, AuthError) as e:
        pytest.skip(f"Neo4j graph not available ({type(e).__name__})")
    assert not {"KA-NEO-MISSING", "KA-NEO-EMPTY-CO"} & set(rep["summary"]["by_code"])


# ------------------------------------------------------------------ canonical topic ids
TOPICS = ["Sorting algorithms", "Sorting algorithm", "Hash tables", "hash tables", "Graph traversal", "Graphs traversal",
          "Dynamic programming", "Applications", "applications", "Greedy algorithms"]


def test_canonical_mapping_is_deterministic():
    a = canonicalise.build_mapping(TOPICS)
    shuffled = TOPICS[:]
    random.Random(7).shuffle(shuffled)
    assert canonicalise.build_mapping(shuffled) == a and set(a) == set(TOPICS)


def test_case_variants_share_one_id_and_name():
    m = canonicalise.build_mapping(TOPICS)
    assert m["Applications"] == m["applications"] and m["Hash tables"] == m["hash tables"]
    assert m["Sorting algorithm"]["canonical_name"] == "Sorting algorithm"          # the shortest name in the cluster


def test_ids_do_not_shift_when_a_topic_is_added():
    before = canonicalise.build_mapping(TOPICS)
    after = canonicalise.build_mapping(["Amortised analysis"] + TOPICS)
    assert all(after[t] == before[t] for t in TOPICS)
    assert all(v["canonical_id"].startswith("TOPIC_") for v in after.values())        # design/store.py recognises the prefix
