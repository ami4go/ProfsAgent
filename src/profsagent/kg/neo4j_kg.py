"""Neo4jKG — implements KGClient (kg/client.py) from the Layer A institutional graph in Neo4j.

Drop-in for StubKG: same methods, same return shapes and the same helpers (co_quality, assess_type, HybridIndex,
programme config). Course data is read from Neo4j once, when the client is created; the retrieval index and the
topic embeddings are built from it on first use.

Embeddings (embedder= or $KG_EMBEDDER):
- local (default): LOCAL_MODEL runs on this machine with sentence-transformers. No API key and no daily quota; the
  model (~90 MB) is downloaded once, and vectors are cached in data/cache/emb_local/.
- gemini: LLMClient.embed (gemini-embedding-001; needs GEMINI_API_KEYS, ~1,000 texts per free key per day).
- off: BM25-only retrieval and no topic matching, like the stub without an LLM.
Each model scores similarity on its own scale, so each has its own topic-match threshold.

Differences from the stub, beyond covering every course in the graph (471) instead of ~17 parsed sheets:
- topic candidates are the graph's canonical Topic nodes, each listed with every course that covers it;
- corpus_resources lists every course that uses a resource, not only the course asked about;
- priors(level=...) restricts the corpus to that course level (the stub ignores level);
- prereqs / anti never name an excluded course.
As in the stub, topic_overlap is Jaccard over embedding-matched topic phrases (no IDF yet) and topic_precedence is
empty until the PRECEDES topic DAG is computed.

    python -m profsagent.kg.neo4j_kg            # load from Neo4j and print a summary (no embeddings)
    python -m profsagent.kg.neo4j_kg --warm     # also embed every course text and topic once (fills the cache)
"""
from __future__ import annotations

import hashlib
import os
import re
import statistics
from functools import cached_property
from pathlib import Path

import numpy as np
from neo4j import GraphDatabase

from profsagent.config import pedagogy, programme
from profsagent.kg.quality import co_quality
from profsagent.kg.stub import assess_type, slug
from profsagent.rag.index import Doc, HybridIndex

# ------------------------------------------------------------------ Cypher (one read per entity type)
COURSES_Q = """
MATCH (c:Course)
OPTIONAL MATCH (c)-[r:REQUIRES]->(p:Course)
WITH c, collect(CASE WHEN p IS NULL THEN null ELSE {uid: p.code, kind: r.kind} END) AS prereqs
OPTIONAL MATCH (c)-[:ANTI_REQUISITE]->(a:Course)
RETURN c {.code, .name, .aliases, .credits, .level, .semester, .cluster, .description, .catalogue_url,
          .prerequisite_text, .anti_requisite_text} AS c, prereqs, collect(a.code) AS anti
"""
COS_Q = """
MATCH (c:Course)-[:HAS_CO]->(co:CourseOutcome)
RETURN c.code AS uid, co.label AS label, co.text AS text, co.order AS ord
ORDER BY uid, ord
"""
WEEKS_Q = """
MATCH (c:Course)-[:HAS_WEEK]->(w:WeekPlan)
OPTIONAL MATCH (w)-[cv:COVERS]->(t:Topic)
WITH c, w, cv, t ORDER BY cv.order
WITH c, w, collect(CASE WHEN t IS NULL THEN null ELSE cv.raw_text END) AS topics
OPTIONAL MATCH (w)-[:MEETS]->(co:CourseOutcome)
WITH c, w, topics, co ORDER BY co.order
RETURN c.code AS uid, w.week_number AS week, w.order AS ord, topics, collect(co.label) AS co_refs
ORDER BY uid, ord
"""
ASSESS_Q = """
MATCH (c:Course)-[:HAS_ASSESSMENT]->(a:AssessmentComponent)
RETURN c.code AS uid, a.name AS raw_label, a.weight_pct AS weight_pct, a.order AS ord
ORDER BY uid, ord
"""
RESOURCES_Q = """
MATCH (c:Course)-[u:USES_RESOURCE]->(r:Resource)
RETURN c.code AS uid, r.id AS rid, r.title AS title, u.type AS type, u.order AS ord
ORDER BY uid, ord
"""
TOPICS_Q = """
MATCH (t:Topic)<-[:COVERS]-(:WeekPlan)<-[:HAS_WEEK]-(c:Course)
RETURN t.id AS id, t.name AS name, collect(DISTINCT c.code) AS courses
ORDER BY id
"""


LOCAL_MODEL = "sentence-transformers/all-MiniLM-L6-v2"   # 384 dims, English, reads up to 256 word pieces per text
# Topic-match cut-off, hand-calibrated (14 Oct 2026) for what topic_overlap needs: a pair counts as shared when one
# topic is the same as, or substantially covered by, the other ("Testing" vs "unit testing"). On 42 pairs of new
# CSE201 topics vs their best match in real candidate courses it is right 79% of the time (0.82: 55%); on 176
# sampled pairs of graph topics, 82% (AUC 0.91, vs 0.85 for gemini-embedding-001 on the same pairs).
LOCAL_TOPIC_MATCH_SIM = 0.66
LOCAL_CACHE = Path(__file__).resolve().parents[3] / "data" / "cache" / "emb_local"


def _norm(code: str) -> str:
    return re.sub(r"\s|-", "", code or "").upper()


class LocalEmbedder:
    """Same call as LLMClient.embed(texts, task_type), computed on this machine. The model is symmetric, so
    task_type is ignored. Vectors are unit length and cached in one file per model."""

    def __init__(self, model: str = LOCAL_MODEL):
        self.model_name = model
        self.path = LOCAL_CACHE / f"{model.split('/')[-1]}.npz"

    @cached_property
    def model(self):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError("local embeddings need `pip install sentence-transformers` (or set KG_EMBEDDER=gemini)") from e
        try:
            return SentenceTransformer(self.model_name, device="cpu", local_files_only=True)
        except OSError:  # first use on this machine: download the model once from huggingface.co
            return SentenceTransformer(self.model_name, device="cpu")

    @cached_property
    def cache(self) -> dict[str, np.ndarray]:
        if not self.path.exists():
            return {}
        with np.load(self.path) as z:
            return dict(zip(z["keys"].tolist(), z["vecs"]))

    def _save(self) -> None:
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp.npz")
            np.savez(tmp, keys=np.array(list(self.cache)), vecs=np.vstack(list(self.cache.values())))
            os.replace(tmp, self.path)
        except OSError as e:  # e.g. OneDrive holding the file; the vectors are recomputed next time
            print(f"[kg] embedding cache not saved ({e})", flush=True)

    def embed(self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> np.ndarray:
        keys = [hashlib.sha256(t.encode()).hexdigest()[:24] for t in texts]
        todo = {k: t for k, t in zip(keys, texts) if k not in self.cache}
        if todo:
            vecs = self.model.encode(list(todo.values()), batch_size=64, normalize_embeddings=True, convert_to_numpy=True)
            self.cache.update(zip(todo, vecs.astype(np.float32)))
            if len(todo) >= 100:  # corpus-sized batches only; single queries take milliseconds to recompute
                self._save()
        if not keys:
            return np.zeros((0, self.model.get_sentence_embedding_dimension()), dtype=np.float32)
        return np.vstack([self.cache[k] for k in keys])


class Neo4jKG:
    def __init__(self, llm=None, uri: str | None = None, user: str | None = None, password: str | None = None,
                 embedder: str | None = None):
        self.llm = llm
        self.th = pedagogy()["thresholds"]
        mode = (embedder or os.environ.get("KG_EMBEDDER") or "local").lower()
        if mode == "local":
            self.embedder, self.match_sim, self.embed_name = LocalEmbedder(), LOCAL_TOPIC_MATCH_SIM, LOCAL_MODEL.split("/")[-1]
        elif mode == "gemini":
            self.embedder, self.match_sim, self.embed_name = llm, self.th["topic_match_sim"], "gemini-embedding-001"
        elif mode == "off":
            self.embedder, self.match_sim, self.embed_name = None, None, "none"
        else:
            raise ValueError(f"KG_EMBEDDER must be local, gemini or off, not {mode!r}")
        driver = GraphDatabase.driver(uri or os.environ.get("NEO4J_URI", "bolt://localhost:7687"),
                                      auth=(user or os.environ.get("NEO4J_USER", "neo4j"),
                                            password or os.environ.get("NEO4J_PASSWORD", "")))
        try:
            with driver.session() as s:
                rows = {name: [r.data() for r in s.run(q)] for name, q in
                        [("courses", COURSES_Q), ("cos", COS_Q), ("weeks", WEEKS_Q), ("assessment", ASSESS_Q),
                         ("resources", RESOURCES_Q), ("topics", TOPICS_Q)]}
        finally:
            driver.close()

        self.by_uid: dict[str, dict] = {}
        for r in rows["courses"]:
            c, uid = r["c"], r["c"]["code"]
            self.by_uid[uid] = {
                "uid": uid, "aliases": [uid] + [a for a in (c.get("aliases") or []) if a != uid],
                "name": c.get("name") or "", "level": c.get("level"), "credits": c.get("credits"),
                "cluster": c.get("cluster"), "semester": c.get("semester"), "description": c.get("description"),
                "catalogue_url": c.get("catalogue_url"), "prereq_text": c.get("prerequisite_text") or [],
                "anti_text": c.get("anti_requisite_text"),
                "prereqs": sorted(r["prereqs"], key=lambda p: p["uid"]), "anti": sorted(r["anti"]),
                "cos": [], "weeks": [], "assessment": [], "resources": [],
            }
        self.alias = {a: uid for uid, r in self.by_uid.items() for a in r["aliases"]}
        for r in rows["cos"]:
            self.by_uid[r["uid"]]["cos"].append({"label": r["label"], "text": r["text"]})
        for r in rows["weeks"]:
            self.by_uid[r["uid"]]["weeks"].append({"week": r["week"], "topics": r["topics"], "co_refs": r["co_refs"]})
        for r in rows["assessment"]:
            self.by_uid[r["uid"]]["assessment"].append({"raw_label": r["raw_label"], "weight_pct": r["weight_pct"]})
        self.used_by: dict[str, list[str]] = {}
        for r in rows["resources"]:
            self.by_uid[r["uid"]]["resources"].append({"rid": r["rid"], "title": r["title"], "type": r["type"]})
            self.used_by.setdefault(r["rid"], []).append(r["uid"])
        self.topics: list[dict] = rows["topics"]

    # ------------------------------------------------------------------ helpers
    def resolve(self, code: str) -> str | None:
        c = _norm(code)
        return self.alias.get(c) or (c if c in self.by_uid else None)

    def _excluded(self, uid: str, exclude: set[str]) -> bool:
        ex = {_norm(e) for e in exclude}
        r = self.by_uid.get(uid, {})
        return bool({uid.upper(), *[a.upper() for a in r.get("aliases", [])]} & ex)

    def _course_topics(self, uid: str) -> list[str]:
        seen, out = set(), []
        for w in self.by_uid.get(uid, {}).get("weeks", []):
            for t in w["topics"]:
                if t.lower() not in seen:
                    seen.add(t.lower())
                    out.append(t)
        return out

    @cached_property
    def rag(self) -> HybridIndex:
        docs: list[Doc] = []
        for uid, r in self.by_uid.items():
            base = dict(uid=uid, aliases=r["aliases"], level=r["level"])
            docs.append(Doc(id=f"{uid}/desc", text=f"{r['name']}. {r['description'] or ''}", doc_type="course_desc", **base))
            for c in r["cos"]:
                docs.append(Doc(id=f"{uid}/{c['label']}", text=f"{r['name']}: {c['text']}", doc_type="co", **base))
            for i, w in enumerate(r["weeks"], start=1):
                if w["topics"]:
                    docs.append(Doc(id=f"{uid}/W{i:02d}", text=f"{r['name']} week {w['week']}: {'; '.join(w['topics'])}",
                                    doc_type="week", **base))
        embed = self.embedder.embed if self.embedder else None
        try:
            return HybridIndex(docs, embed)
        except Exception as e:  # noqa: BLE001 — degrade to lexical-only retrieval rather than fail the run
            print(f"[rag] dense index unavailable ({type(e).__name__}: {str(e)[:120]}); using BM25 only", flush=True)
            return HybridIndex(docs, None)

    @cached_property
    def _phrase_vecs(self) -> dict[str, np.ndarray]:
        """Embedding of every topic phrase in the graph (week topics and canonical topic names), in one batch."""
        if not self.embedder:
            return {}
        phrases = sorted({t for r in self.by_uid.values() for w in r["weeks"] for t in w["topics"]}
                         | {t["name"] for t in self.topics})
        try:
            return dict(zip(phrases, self.embedder.embed(phrases, "SEMANTIC_SIMILARITY")))
        except Exception as e:  # noqa: BLE001 — topic matching degrades to "no candidates" rather than fail the run
            print(f"[kg] topic embeddings unavailable ({type(e).__name__}: {str(e)[:120]}); topic matching disabled", flush=True)
            return {}

    @cached_property
    def _topic_matrix(self) -> tuple[list[dict], np.ndarray | None]:
        pool = [t for t in self.topics if t["name"] in self._phrase_vecs]
        return pool, (np.vstack([self._phrase_vecs[t["name"]] for t in pool]) if pool else None)

    @cached_property
    def _rag_lexical(self) -> HybridIndex:
        return HybridIndex(self.rag.docs, None)

    def _search(self, text: str, **kw):
        """Hybrid search; words only when the query itself cannot be embedded (e.g. the embedding quota is used up)."""
        try:
            return self.rag.search(text, **kw)
        except Exception as e:  # noqa: BLE001 — a missing query vector must not stop the design run
            print(f"[rag] query embedding unavailable ({type(e).__name__}); using BM25 only", flush=True)
            return self._rag_lexical.search(text, **kw)

    def _embed_phrases(self, phrases: list[str]) -> np.ndarray | None:
        try:
            return self.embedder.embed(phrases, "SEMANTIC_SIMILARITY")
        except Exception as e:  # noqa: BLE001 — topic matching degrades to "nothing found" rather than fail the run
            print(f"[kg] phrase embedding unavailable ({type(e).__name__}); no topic matches", flush=True)
            return None

    # ------------------------------------------------------------------ KGClient
    def index(self, exclude=frozenset()):
        return [{k: r[k] for k in ("uid", "aliases", "name", "level", "credits", "cluster")}
                for uid, r in sorted(self.by_uid.items()) if not self._excluded(uid, exclude)]

    def course(self, uid, exclude=frozenset()):
        uid = self.resolve(uid) or uid
        if uid not in self.by_uid or self._excluded(uid, exclude):
            return None
        r = self.by_uid[uid]
        cos = []
        for c in r["cos"]:
            q, flags, lv, bl = co_quality(c["text"])
            cos.append({"uid": f"{uid}/{c['label']}", "label": c["label"], "text": c["text"], "quality_score": q,
                        "quality_flags": flags, "leading_verb": lv, "bloom_lexicon": bl})
        return {
            "uid": uid, "aliases": r["aliases"], "name": r["name"], "level": r["level"], "credits": r["credits"],
            "cluster": r["cluster"], "semester": r["semester"], "description": r["description"],
            "prereqs": [p for p in r["prereqs"] if not self._excluded(p["uid"], exclude)], "prereq_text": r["prereq_text"],
            "anti_index": r["anti_text"], "anti": [a for a in r["anti"] if not self._excluded(a, exclude)],
            "cos": cos, "topics": self._course_topics(uid),
            "weeks": [{"week": w["week"], "topics": w["topics"], "co_refs": w["co_refs"]} for w in r["weeks"]],
            "assessment": [{"type": assess_type(a["raw_label"]), "weight_pct": a["weight_pct"], "raw_label": a["raw_label"]}
                           for a in r["assessment"]],
            "resources": [{"type": x["type"], "title": x["title"]} for x in r["resources"]],
            "catalogue_url": r["catalogue_url"],
        }

    def search_courses(self, text, k=15, exclude=frozenset()):
        hits = self._search(text, k=k * 4, exclude={_norm(e) for e in exclude})
        agg: dict[str, dict] = {}
        for d, s in hits:
            a = agg.setdefault(d.uid, {"uid": d.uid, "score": 0.0, "hits": []})
            a["score"] += s
            if len(a["hits"]) < 3:
                a["hits"].append(d.text[:160])
        return sorted(agg.values(), key=lambda x: -x["score"])[:k]

    def topic_overlap(self, new_topics, uid):
        uid = self.resolve(uid) or uid
        ts = [t for t in self._course_topics(uid) if t in self._phrase_vecs]
        if not ts or not new_topics or not self.embedder:
            return {"weighted_jaccard": 0.0, "shared_topics": [], "method": "neo4j: no topics or no embeddings"}
        vecs = np.vstack([self._phrase_vecs[t] for t in ts])
        nv = self._embed_phrases(new_topics)
        if nv is None:
            return {"weighted_jaccard": 0.0, "shared_topics": [], "method": "neo4j: embeddings unavailable"}
        sims = nv @ vecs.T
        used_old, shared = set(), []
        for i in np.argsort(-sims.max(axis=1)):
            j = int(np.argmax(np.where(np.isin(np.arange(len(ts)), list(used_old)), -1, sims[i])))
            if sims[i, j] >= self.match_sim and j not in used_old:
                used_old.add(j)
                shared.append(f"{new_topics[i]} ≈ {ts[j]}")
        n = len(shared)
        jac = n / (len(new_topics) + len(ts) - n)
        return {"weighted_jaccard": round(jac, 3), "shared_topics": shared,
                "method": f"neo4j: Jaccard over embedding-matched topic phrases ({self.embed_name}, cos ≥ {self.match_sim}), no IDF"}

    def topic_candidates(self, phrases, k=5, exclude=frozenset()):
        pool, mat = self._topic_matrix if (self.embedder and phrases) else ([], None)
        if mat is None:
            return [{"phrase": p, "candidates": []} for p in phrases]
        courses = [[u for u in t["courses"] if not self._excluded(u, exclude)] for t in pool]
        keep = np.array([bool(c) for c in courses])
        pv = self._embed_phrases(phrases)
        if pv is None:
            return [{"phrase": p, "candidates": []} for p in phrases]
        out = []
        for i, p in enumerate(phrases):
            sims = np.where(keep, mat @ pv[i], -np.inf)
            cands, seen = [], set()
            for j in np.argsort(-sims):
                if not keep[j]:
                    break
                key = slug(pool[j]["name"])
                if key in seen:
                    continue
                seen.add(key)
                cands.append({"topic_uid": f"T:{key}", "canonical_name": pool[j]["name"], "sim": round(float(sims[j]), 3),
                              "courses": courses[j]})
                if len(cands) >= k:
                    break
            out.append({"phrase": p, "candidates": cands})
        return out

    def programme_pos(self, programme_uid):
        p = programme(programme_uid)
        return [{"uid": x["id"], "text": x["text"], "short_label": x.get("short_label")} for x in p["po"]]

    def exemplar_cos(self, text, level, k=8, exclude=frozenset(), min_quality=0.7):
        hits = self._search(text, k=60, doc_types={"co"}, exclude={_norm(e) for e in exclude})
        out = []
        for d, _ in hits:
            label = d.id.split("/")[-1]
            c = next((c for c in self.by_uid[d.uid]["cos"] if c["label"] == label), None)
            if not c:
                continue
            q, flags, lv, bl = co_quality(c["text"])
            if q >= min_quality:
                out.append({"uid": d.id, "course": self.by_uid[d.uid]["name"], "statement": c["text"], "bloom_lexicon": bl,
                            "quality_score": q})
            if len(out) >= k:
                break
        return out

    def priors(self, level=None, exclude=frozenset()):
        weights: dict[str, list[float]] = {}
        co_counts, comp_counts = [], []
        for uid, r in self.by_uid.items():
            if self._excluded(uid, exclude) or (level is not None and r["level"] != level):
                continue
            if r["cos"]:
                co_counts.append(len(r["cos"]))
            ws = [(assess_type(a["raw_label"]), a["weight_pct"]) for a in r["assessment"] if a["weight_pct"] is not None]
            if ws and abs(sum(w for _, w in ws) - 100) < 1:
                comp_counts.append(len(ws))
                agg: dict[str, float] = {}
                for t, w in ws:
                    agg[t] = agg.get(t, 0) + w
                for t, w in agg.items():
                    weights.setdefault(t, []).append(w)

        def q(v):
            v = sorted(v)
            if len(v) < 4:
                return [min(v), max(v)]
            qs = statistics.quantiles(v, n=4)
            return [qs[0], qs[2]]
        return {
            "n_courses": len(co_counts),
            "co_count": {"median": statistics.median(co_counts) if co_counts else None, "n": len(co_counts)},
            "component_count": {"median": statistics.median(comp_counts) if comp_counts else None, "n": len(comp_counts)},
            "weights": {t: {"median": statistics.median(v), "iqr": q(v), "n": len(v)} for t, v in weights.items()},
            "note": "priors from the Neo4j institutional graph" + (f" (level {level})" if level is not None else ""),
        }

    def corpus_resources(self, uids):
        out, seen = [], set()
        for uid in uids:
            uid = self.resolve(uid) or uid
            for x in (self.by_uid.get(uid) or {}).get("resources", []):
                if x["rid"] in seen:
                    continue
                seen.add(x["rid"])
                out.append({"resource_uid": x["rid"], "title": x["title"], "type": x["type"],
                            "used_by_courses": self.used_by.get(x["rid"], [uid]), "verified": False})
        return out

    def topic_precedence(self, topic_uids):
        return []


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(description="Load the institutional graph from Neo4j and print a summary.")
    ap.add_argument("--warm", action="store_true", help="embed every course text and topic once")
    args = ap.parse_args()
    llm = None
    if args.warm and (os.environ.get("KG_EMBEDDER") or "local").lower() == "gemini":
        from profsagent.llm.client import LLMClient
        llm = LLMClient()
    kg = Neo4jKG(llm)
    n_weeks = sum(len(r["weeks"]) for r in kg.by_uid.values())
    print(f"courses {len(kg.by_uid)} | aliases {len(kg.alias)} | COs {sum(len(r['cos']) for r in kg.by_uid.values())} | "
          f"weeks {n_weeks} | topics {len(kg.topics)} | resources {len(kg.used_by)}")
    if args.warm:
        print(f"embedder: {kg.embed_name} | retrieval documents: {len(kg.rag.docs)} (dense: {kg.rag.emb is not None}) | "
              f"topic phrases embedded: {len(kg._phrase_vecs)}")
