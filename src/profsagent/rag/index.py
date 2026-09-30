"""Hybrid retrieval: BM25 (lexical) + dense (Gemini embeddings), fused with reciprocal-rank fusion.

Small-corpus implementation (numpy, in memory, embeddings cached on disk). Every document carries metadata
used for filtering: doc_type, course uid + aliases, level. `exclude` filters by course uid/alias BEFORE ranking
so an excluded course can never appear in any context (dev-run target, gold set, blocklisted items).
"""
from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field

import numpy as np

TOKEN_RE = re.compile(r"[a-z0-9]+")
STOP = set("a an the of and or to in for on with by is are be as at from this that these those it its into via using use "
           "students student able will course courses week weeks introduction basic basics overview".split())


def tokens(text: str) -> list[str]:
    return [t for t in TOKEN_RE.findall((text or "").lower()) if t not in STOP and len(t) > 1]


@dataclass
class Doc:
    id: str
    text: str
    doc_type: str                     # course_desc | co | week | assessment | regulation | po | topic | external
    uid: str | None = None            # owning course uid (Layer A) if any
    aliases: list[str] = field(default_factory=list)
    level: int | None = None
    meta: dict = field(default_factory=dict)


class HybridIndex:
    def __init__(self, docs: list[Doc], embed_fn=None, k1: float = 1.4, b: float = 0.75):
        self.docs = docs
        self.embed_fn = embed_fn
        self.toks = [tokens(d.text) for d in docs]
        self.df = Counter(t for ts in self.toks for t in set(ts))
        self.N = len(docs)
        self.avgdl = sum(map(len, self.toks)) / max(self.N, 1)
        self.k1, self.b = k1, b
        self.tf = [Counter(ts) for ts in self.toks]
        self.emb: np.ndarray | None = None
        if embed_fn is not None and docs:
            self.emb = embed_fn([d.text for d in docs], "RETRIEVAL_DOCUMENT")

    def _bm25(self, q: list[str], idx: list[int]) -> np.ndarray:
        out = np.zeros(len(idx))
        for j, i in enumerate(idx):
            dl = len(self.toks[i]) or 1
            s = 0.0
            for t in q:
                f = self.tf[i].get(t, 0)
                if not f:
                    continue
                idf = math.log(1 + (self.N - self.df[t] + 0.5) / (self.df[t] + 0.5))
                s += idf * f * (self.k1 + 1) / (f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            out[j] = s
        return out

    def search(self, query: str, k: int = 10, doc_types: set[str] | None = None, exclude: set[str] = frozenset(),
               level_max: int | None = None, rrf_k: int = 60) -> list[tuple[Doc, float]]:
        ex = {e.upper() for e in exclude}
        idx = [i for i, d in enumerate(self.docs)
               if (doc_types is None or d.doc_type in doc_types)
               and not ({(d.uid or "").upper(), *[a.upper() for a in d.aliases]} & ex)
               and (level_max is None or d.level is None or d.level <= level_max)]
        if not idx:
            return []
        ranks: dict[int, float] = {}
        bm = self._bm25(tokens(query), idx)
        for r, j in enumerate(np.argsort(-bm)):
            if bm[j] > 0:
                ranks[idx[j]] = ranks.get(idx[j], 0) + 1 / (rrf_k + r)
        if self.emb is not None and self.embed_fn is not None:
            qv = self.embed_fn([query], "RETRIEVAL_QUERY")[0]
            sims = self.emb[idx] @ qv
            for r, j in enumerate(np.argsort(-sims)):
                ranks[idx[j]] = ranks.get(idx[j], 0) + 1 / (rrf_k + r)
        best = sorted(ranks.items(), key=lambda x: -x[1])[:k]
        return [(self.docs[i], s) for i, s in best]
