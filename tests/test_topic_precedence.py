"""Topic precedence from real weekly plans (validation layer v2, Stage 3). Offline: the graph is built in memory and a
fake embedder matches a phrase only to itself (ignoring case); the live test is skipped without Neo4j."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pytest

from profsagent.kg.neo4j_kg import Neo4jKG
from profsagent.kg.stub import StubKG


class ExactEmbedder:
    def __init__(self):
        self.dim = {}

    def embed(self, texts, task_type="SEMANTIC_SIMILARITY"):
        v = np.zeros((len(texts), 64), dtype=np.float32)
        for i, t in enumerate(texts):
            v[i, self.dim.setdefault(t.lower(), len(self.dim))] = 1
        return v


def graph(courses: dict[str, list[list[str]]]) -> Neo4jKG:
    kg = Neo4jKG.__new__(Neo4jKG)
    kg.embedder, kg.match_sim, kg.embed_name = ExactEmbedder(), 0.9, "exact"
    kg.by_uid = {u: {"uid": u, "aliases": [u], "weeks": [{"week": i + 1, "topics": ts, "co_refs": []} for i, ts in enumerate(ws)]}
                 for u, ws in courses.items()}
    kg.alias = {u: u for u in courses}
    names = sorted({t for ws in courses.values() for w in ws for t in w})
    kg.topics = [{"id": f"TOPIC_{i}", "name": n, "courses": []} for i, n in enumerate(names)]
    return kg


def pair(ev, a, b):
    return next((e for e in ev if (e["from"], e["to"]) == (a, b)), None)


def test_consistent_order_across_courses_is_evidence():
    kg = graph({"CSE101": [["Recursion"], ["Sorting"]], "CSE102": [["Recursion", "Arrays"], ["Sorting"]],
                "CSE103": [["Recursion"], ["Hashing"], ["Sorting"]]})
    e = pair(kg.precedence_evidence(["Recursion", "Sorting", "Hashing"]), "Recursion", "Sorting")
    assert e == {"from": "Recursion", "to": "Sorting", "support": 3, "against": 0, "courses": ["CSE101", "CSE102", "CSE103"]}
    assert pair(kg.precedence_evidence(["Recursion", "Hashing"]), "Recursion", "Hashing") is None   # one course only


def test_mixed_order_is_not_evidence():
    kg = graph({"A101": [["Trees"], ["Graphs"], ["Heaps"]], "B101": [["Trees"], ["Graphs"], ["Tries"]], "C101": [["Graphs"], ["Trees"]]})
    assert kg.precedence_evidence(["Trees", "Graphs"]) == []                # 2 of 3 = 0.67 < 0.8
    assert kg.precedence_evidence(["Trees", "Graphs"], min_confidence=0.6)[0]["against"] == 1


def test_same_week_and_events_say_nothing():
    kg = graph({"A101": [["Trees", "Graphs"], ["Heaps"]], "B101": [["Trees", "Graphs"], ["Tries"]],
                "C101": [["Mid-sem exam"], ["Trees"], ["Heaps"]], "D101": [["Mid-sem exam"], ["Trees"], ["Tries"]]})
    assert kg.precedence_evidence(["Trees", "Graphs"]) == []
    assert kg.precedence_evidence(["Mid-sem exam", "Trees"]) == []          # an exam is not subject matter


def test_copied_sheets_and_held_out_courses_vote_once_or_not_at_all():
    plan = [["Lexing"], ["Parsing"]]
    kg = graph({"CSE600": [["Lexing"], ["Parsing"], ["Types"]], "CSE600A": [["Lexing"], ["Parsing"], ["Codegen"]],
                "ECE700": plan, "MTH700": plan})
    ev = kg.precedence_evidence(["Lexing", "Parsing"])
    assert pair(ev, "Lexing", "Parsing")["support"] == 2                    # CSE600/CSE600A + ECE700/MTH700 (same sheet)
    assert kg.precedence_evidence(["Lexing", "Parsing"], exclude={"ECE700", "MTH700"}) == []


def test_topic_precedence_speaks_canonical_uids():
    kg = graph({"A101": [["Binary Trees"], ["Graphs"], ["Heaps"]], "B101": [["Binary Trees"], ["Graphs"], ["Tries"]]})
    assert kg.topic_precedence(["T:binary-trees", "T:graphs", "T:unknown"]) == [
        {"from": "T:binary-trees", "to": "T:graphs", "support": 2, "against": 0, "courses": ["A101", "B101"]}]


def test_no_embeddings_no_evidence():
    kg = graph({"A101": [["Trees"], ["Graphs"], ["Heaps"]], "B101": [["Trees"], ["Graphs"], ["Tries"]]})
    assert kg.precedence_evidence(["Trees", "Graphs"])
    kg = graph({"A101": [["Trees"], ["Graphs"], ["Heaps"]], "B101": [["Trees"], ["Graphs"], ["Tries"]]})
    kg.embedder = None
    assert kg.precedence_evidence(["Trees", "Graphs"]) == [] and StubKG().precedence_evidence(["Trees", "Graphs"]) == []


def test_live_graph_shape():
    from test_neo4j_kg import kgs
    neo, _ = kgs()
    ev = neo.precedence_evidence(["Recursion", "Dynamic programming", "Hashing"])
    assert all(set(e) == {"from", "to", "support", "against", "courses"} and e["support"] >= 2 for e in ev)
    for e in (e for e in ev if e["support"] <= len(e["courses"])):         # hiding every supporting course removes the pair
        assert pair(neo.precedence_evidence(["Recursion", "Dynamic programming", "Hashing"], exclude=set(e["courses"])),
                    e["from"], e["to"]) is None
