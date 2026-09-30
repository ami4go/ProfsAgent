"""StubKG — implements KGClient from data/stub_kg (parsed course sheets). Replace with the Neo4j client later.

Differences from production Layer A (documented so nobody mistakes stub numbers for results):
- topics are split deterministically from weekly-plan cells (no LLM atomisation, no canonical clustering);
  "canonical" topic uids are slugs of phrases, per course;
- topic overlap = Jaccard over embedding-matched topic phrases (greedy 1-1, cosine ≥ threshold), no IDF;
- priors come from the ~17 stub courses, so `n` is small and callers fall back to config bands.
"""
from __future__ import annotations

import json
import re
import statistics
from functools import cached_property

import numpy as np

from profsagent.config import DATA, pedagogy, programme
from profsagent.kg.quality import co_quality
from profsagent.rag.index import Doc, HybridIndex

ASSESS_TYPES = [
    ("endsem", r"end[\s-]*sem|final exam|end[\s-]*term|final"), ("midsem", r"mid[\s-]*sem|mid[\s-]*term"),
    ("quiz", r"quiz"), ("lab", r"\blab"), ("project", r"project"), ("assignment", r"assignment|homework|problem set"),
    ("presentation", r"presentation|seminar"), ("report", r"report|paper|state of art"),
    ("participation", r"participation|attendance|in-?class|peer"),
]


def assess_type(label: str) -> str:
    for t, rx in ASSESS_TYPES:
        if re.search(rx, label or "", re.I):
            return t
    return "other"


def split_topics(raw: str) -> list[str]:
    if not raw:
        return []
    parts = re.split(r"\n|•|\*|;|(?<=[a-z\)]),\s+(?=[A-Z])|\s–\s", raw)
    out = []
    for p in parts:
        p = re.sub(r"^\s*(introduction to|intro to|overview of|basics of|basic)\s+", "", p.strip(" -–:.,\t"), flags=re.I)
        if 2 < len(p) <= 120 and not re.match(r"^(end semester review|mid-?sem|revision|holiday|student presentations?)$", p, re.I):
            out.append(p)
    return out


def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


class StubKG:
    def __init__(self, llm=None):
        self.llm = llm
        self.rows = json.loads((DATA / "stub_kg" / "index.json").read_text(encoding="utf-8"))
        self.by_uid = {r["uid"]: r for r in self.rows}
        self.alias = {a: r["uid"] for r in self.rows for a in r["aliases"]}
        self.sheets: dict[str, dict] = {}
        for p in (DATA / "stub_kg" / "courses").glob("*.json"):
            d = json.loads(p.read_text(encoding="utf-8"))
            if "sheet" in d:
                self.sheets[d["index"]["uid"]] = d["sheet"]
        self.th = pedagogy()["thresholds"]

    # ------------------------------------------------------------------ helpers
    def resolve(self, code: str) -> str | None:
        c = re.sub(r"\s|-", "", code or "").upper()
        return self.alias.get(c) or (c if c in self.by_uid else None)

    def _excluded(self, uid: str, exclude: set[str]) -> bool:
        ex = {e.upper() for e in exclude}
        r = self.by_uid.get(uid, {})
        return bool({uid.upper(), *[a.upper() for a in r.get("aliases", [])]} & ex)

    def _course_topics(self, uid: str) -> list[str]:
        sh = self.sheets.get(uid) or {}
        seen, out = set(), []
        for w in sh.get("lecture_weeks", []):
            for t in split_topics(w.get("topic_raw", "")):
                if t.lower() not in seen:
                    seen.add(t.lower())
                    out.append(t)
        return out

    @cached_property
    def rag(self) -> HybridIndex:
        docs: list[Doc] = []
        for uid, sh in self.sheets.items():
            r = self.by_uid[uid]
            base = dict(uid=uid, aliases=r["aliases"], level=r["level"])
            h = sh.get("header", {})
            docs.append(Doc(id=f"{uid}/desc", text=f"{r['name']}. {h.get('description') or ''}", doc_type="course_desc", **base))
            for c in sh.get("cos", []):
                docs.append(Doc(id=f"{uid}/{c['label']}", text=f"{r['name']}: {c['text']}", doc_type="co", **base))
            for w in sh.get("lecture_weeks", []):
                if w.get("topic_raw"):
                    docs.append(Doc(id=f"{uid}/W{w.get('week') or 0:02d}", text=f"{r['name']} week {w.get('week')}: {w['topic_raw']}",
                                    doc_type="week", **base))
        embed = self.llm.embed if self.llm else None
        try:
            return HybridIndex(docs, embed)
        except Exception as e:  # noqa: BLE001 — degrade to lexical-only retrieval rather than fail the run
            print(f"[rag] dense index unavailable ({type(e).__name__}); using BM25 only", flush=True)
            return HybridIndex(docs, None)

    @cached_property
    def _topic_vecs(self) -> dict[str, tuple[list[str], np.ndarray | None]]:
        out = {}
        for uid in self.sheets:
            ts = self._course_topics(uid)
            out[uid] = (ts, self.llm.embed(ts, "SEMANTIC_SIMILARITY") if (self.llm and ts) else None)
        return out

    # ------------------------------------------------------------------ KGClient
    def index(self, exclude=frozenset()):
        return [{k: r[k] for k in ("uid", "aliases", "name", "level", "credits", "cluster")}
                for r in self.rows if not self._excluded(r["uid"], exclude)]

    def course(self, uid, exclude=frozenset()):
        uid = self.resolve(uid) or uid
        if uid not in self.by_uid or self._excluded(uid, exclude):
            return None
        r, sh = self.by_uid[uid], self.sheets.get(uid, {})
        cos = []
        for c in sh.get("cos", []):
            q, flags, lv, bl = co_quality(c["text"])
            cos.append({"uid": f"{uid}/{c['label']}", "label": c["label"], "text": c["text"], "quality_score": q,
                        "quality_flags": flags, "leading_verb": lv, "bloom_lexicon": bl})
        prereqs = []
        for p in sh.get("prerequisites", []):
            for code in re.findall(r"[A-Z]{2,4}\s?\d{3}[A-Z]?", p["raw"]):
                u = self.resolve(code)
                if u:
                    prereqs.append({"uid": u, "kind": p["kind"]})
        return {
            "uid": uid, "aliases": r["aliases"], "name": r["name"], "level": r["level"], "credits": r["credits"],
            "cluster": r["cluster"], "semester": r["semester"], "description": (sh.get("header") or {}).get("description"),
            "prereqs": prereqs, "prereq_text": [p["raw"] for p in sh.get("prerequisites", [])],
            "anti_index": r.get("anti_index"), "cos": cos, "topics": self._course_topics(uid),
            "weeks": [{"week": w.get("week"), "topics": split_topics(w.get("topic_raw", "")), "co_refs": w.get("co_refs", [])}
                      for w in sh.get("lecture_weeks", [])],
            "assessment": [{"type": assess_type(a["raw_label"]), "weight_pct": a["weight_pct"], "raw_label": a["raw_label"]}
                           for a in sh.get("assessment", [])],
            "resources": [{"type": x.get("type_raw"), "title": x.get("title_raw")} for x in sh.get("resources", [])],
            "catalogue_url": r.get("catalogue_url"),
        }

    def search_courses(self, text, k=15, exclude=frozenset()):
        hits = self.rag.search(text, k=k * 4, exclude=exclude)
        agg: dict[str, dict] = {}
        for d, s in hits:
            a = agg.setdefault(d.uid, {"uid": d.uid, "score": 0.0, "hits": []})
            a["score"] += s
            if len(a["hits"]) < 3:
                a["hits"].append(d.text[:160])
        return sorted(agg.values(), key=lambda x: -x["score"])[:k]

    def topic_overlap(self, new_topics, uid):
        ts, vecs = self._topic_vecs.get(uid, ([], None))
        if not ts or not new_topics or vecs is None:
            return {"weighted_jaccard": 0.0, "shared_topics": [], "method": "stub: no topics"}
        nv = self.llm.embed(new_topics, "SEMANTIC_SIMILARITY")
        sims = nv @ vecs.T
        used_old, shared = set(), []
        for i in np.argsort(-sims.max(axis=1)):
            j = int(np.argmax(np.where(np.isin(np.arange(len(ts)), list(used_old)), -1, sims[i])))
            if sims[i, j] >= self.th["topic_match_sim"] and j not in used_old:
                used_old.add(j)
                shared.append(f"{new_topics[i]} ≈ {ts[j]}")
        n = len(shared)
        jac = n / (len(new_topics) + len(ts) - n)
        return {"weighted_jaccard": round(jac, 3), "shared_topics": shared,
                "method": f"stub: Jaccard over embedding-matched topic phrases (cos ≥ {self.th['topic_match_sim']}), no IDF"}

    def topic_candidates(self, phrases, k=5, exclude=frozenset()):
        if not self.llm or not phrases:
            return [{"phrase": p, "candidates": []} for p in phrases]
        pool = [(uid, t) for uid, (ts, _) in self._topic_vecs.items() if not self._excluded(uid, exclude) for t in ts]
        if not pool:
            return [{"phrase": p, "candidates": []} for p in phrases]
        mat = np.vstack([self._topic_vecs[uid][1][self._topic_vecs[uid][0].index(t)] for uid, t in pool])
        pv = self.llm.embed(phrases, "SEMANTIC_SIMILARITY")
        out = []
        for i, p in enumerate(phrases):
            sims = mat @ pv[i]
            cands, seen = [], set()
            for j in np.argsort(-sims):
                uid, t = pool[j]
                key = slug(t)
                if key in seen:
                    continue
                seen.add(key)
                cands.append({"topic_uid": f"T:{key}", "canonical_name": t, "sim": round(float(sims[j]), 3), "courses": [uid]})
                if len(cands) >= k:
                    break
            out.append({"phrase": p, "candidates": cands})
        return out

    def programme_pos(self, programme_uid):
        p = programme(programme_uid)
        return [{"uid": x["id"], "text": x["text"], "short_label": x.get("short_label")} for x in p["po"]]

    def exemplar_cos(self, text, level, k=8, exclude=frozenset(), min_quality=0.7):
        hits = self.rag.search(text, k=60, doc_types={"co"}, exclude=exclude)
        out = []
        for d, _ in hits:
            label = d.id.split("/")[-1]
            c = next((c for c in self.sheets[d.uid]["cos"] if c["label"] == label), None)
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
        for uid, sh in self.sheets.items():
            if self._excluded(uid, exclude):
                continue
            if sh.get("cos"):
                co_counts.append(len(sh["cos"]))
            ws = [(assess_type(a["raw_label"]), a["weight_pct"]) for a in sh.get("assessment", []) if a["weight_pct"] is not None]
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
            "note": "stub priors from the small stub corpus; bands with n < 5 fall back to config/pedagogy.yaml",
        }

    def corpus_resources(self, uids):
        out = []
        for uid in uids:
            for x in (self.sheets.get(uid) or {}).get("resources", []):
                t = (x.get("title_raw") or "").strip()
                if t:
                    out.append({"resource_uid": f"R:hash:{slug(t)[:40]}", "title": t, "type": x.get("type_raw"),
                                "used_by_courses": [uid], "verified": False})
        return out

    def topic_precedence(self, topic_uids):
        return []
