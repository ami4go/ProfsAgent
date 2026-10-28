"""Graph facts snapshot (validation layer v2, Stage 3): what the graph checks need from the institutional graph,
stored in state["kg_facts"] once the course structure exists (after S5).

The validators stay pure functions of the state: deterministic, testable offline, and a rerun of the checks sees the
same graph facts as the run did (the snapshot carries a version hash of the graph it came from). Only the KGClient
contract is used, so the stub and Neo4j backends both work; the stub simply has no precedence evidence.

    norms              same-level courses: credits, CO count, highest CO Bloom level (lexicon), assessment components
    precedence         pairs of this design's topics that IIIT-D weekly plans teach in a consistent order
    catalogue_overlap  the courses whose topics overlap this design's final topics most (all courses, not only the
                       candidates retrieved at S2)
"""
from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter

TOP_OVERLAPS = 5


def version(kg, exclude=frozenset()) -> str:
    rows = [(r["uid"], r.get("level"), r.get("credits")) for r in kg.index(exclude=exclude)]
    return hashlib.sha1(json.dumps(rows, default=str).encode()).hexdigest()[:12]


def spread(values: list[float]) -> dict | None:
    """Quartiles and Tukey fences (Q1 - 1.5 IQR, Q3 + 1.5 IQR): outside the fences is unusual for this level."""
    v = sorted(values)
    if not v:
        return None
    q1, med, q3 = statistics.quantiles(v, n=4, method="inclusive") if len(v) >= 2 else (v[0], v[0], v[0])
    iqr = q3 - q1
    return {"n": len(v), "q1": q1, "median": med, "q3": q3, "lo": q1 - 1.5 * iqr, "hi": q3 + 1.5 * iqr}


def level_norms(kg, level, exclude=frozenset()) -> dict:
    rows = [r for r in kg.index(exclude=exclude) if r.get("level") == level]
    co_count, bloom_max, components = [], [], []
    for r in rows:
        c = kg.course(r["uid"], exclude=exclude) or {}
        cos = c.get("cos") or []
        if cos:
            co_count.append(len(cos))
            levels = [x["bloom_lexicon"] for x in cos if x.get("bloom_lexicon")]
            if levels:
                bloom_max.append(max(levels))
        ws = [a.get("weight_pct") for a in c.get("assessment") or []]
        if ws and None not in ws and abs(sum(ws) - 100) < 1:
            components.append(len(ws))
    return {"level": level, "n": len(rows), "credits": dict(Counter(str(r.get("credits")) for r in rows)),
            "co_count": spread(co_count), "bloom_max": spread(bloom_max), "components": spread(components)}


def _topics(state: dict) -> list[dict]:
    return [t for m in state.get("modules", []) for t in m["topics"]]


def precedence(kg, state: dict, exclude=frozenset()) -> list[dict]:
    topics = _topics(state)
    id_of = {}
    for t in topics:
        id_of.setdefault(t["title"], t["id"])
    ev = kg.precedence_evidence([t["title"] for t in topics], exclude=exclude) if hasattr(kg, "precedence_evidence") else []
    return [{"from": id_of[e["from"]], "to": id_of[e["to"]], "from_title": e["from"], "to_title": e["to"],
             "support": e["support"], "against": e["against"], "courses": e["courses"]} for e in ev]


def catalogue_overlap(kg, state: dict, exclude=frozenset(), k: int = TOP_OVERLAPS) -> list[dict]:
    titles = [t["title"] for t in _topics(state)]
    if not titles:
        return []
    out = []
    for r in kg.index(exclude=exclude):
        ov = kg.topic_overlap(titles, r["uid"])
        if ov.get("weighted_jaccard"):
            out.append({"course_uid": r["uid"], "name": r.get("name"), "weighted_jaccard": ov["weighted_jaccard"],
                        "shared_topics": ov.get("shared_topics", [])[:8]})
    return sorted(out, key=lambda o: (-o["weighted_jaccard"], o["course_uid"]))[:k]


def snapshot(kg, state: dict, exclude=frozenset()) -> dict:
    level = state.get("level")
    return {
        "version": version(kg, exclude),
        "level": level,
        "norms": level_norms(kg, level, exclude),
        "precedence": precedence(kg, state, exclude),
        "catalogue_overlap": catalogue_overlap(kg, state, exclude),
        "method": {"embedder": getattr(kg, "embed_name", type(kg).__name__), "match_sim": getattr(kg, "match_sim", None),
                   "excluded": sorted(exclude)},
    }
