"""Semantic checks with a local sentence-embedding model (validation layer v2, Stage 4). No LLM and no API calls.

They are warnings until calibrated against professor labels (Stage 6), and they run only when a model is configured
(configure_local(); the pipeline and the evaluation scripts do it at start-up). Without a model they return nothing,
so the rule tests and replays of saved states are unchanged.

  VS-LOCOPY  an LO at its CO's own Bloom level that means the same as the CO (cosine >= lo_copy_sim). The lexical
             VLO-COPY (token overlap >= 0.8) misses paraphrases: on the 28 saved runs, 50 at-level LOs reach 0.92 and
             VLO-COPY flags 22 of them; the others read as the CO restated with a different condition or degree.
             Lower-level LOs share their CO's object by design ("Identify agent skills" under "Configure agent
             skills", 0.91), so only at-level LOs are compared.
  VS-LOFIT   an LO closer to another CO than to its parent, by >= lo_fit_margin (11 of 304 saved LOs are closer to
             another CO at all; 2 by more than 0.1)
  VS-CODUP   two COs that mean the same (cosine >= co_dup_sim; saved runs: 99th percentile 0.66)
"""
from __future__ import annotations

import os

import numpy as np

from profsagent.config import pedagogy
from profsagent.validate.record import WARN, v

_embed = None
MODEL = None


def configure(embed, name: str = "custom") -> None:
    """`embed(texts) -> unit vectors (n, d)`; None switches the semantic checks off."""
    global _embed, MODEL
    _embed, MODEL = embed, (name if embed else None)


def configure_local() -> bool:
    """Use the local sentence-transformers model (the same one as the knowledge graph), unless PROFSAGENT_SEMANTIC=off
    or the package is missing. The model loads on the first check, not here."""
    if os.environ.get("PROFSAGENT_SEMANTIC", "on").lower() == "off":
        configure(None)
        return False
    try:
        import sentence_transformers  # noqa: F401
        from profsagent.kg.neo4j_kg import LOCAL_MODEL, LocalEmbedder
    except ImportError:
        configure(None)
        return False
    e = LocalEmbedder()
    configure(lambda texts: e.embed(texts, "SEMANTIC_SIMILARITY"), LOCAL_MODEL.split("/")[-1])
    return True


def enabled() -> bool:
    return _embed is not None


def _th() -> dict:
    return pedagogy()["thresholds"]["semantic"]


def _sims(a: list[str], b: list[str]) -> np.ndarray:
    return np.asarray(_embed(a)) @ np.asarray(_embed(b)).T


def check_cos(state: dict) -> list[dict]:
    cos = state.get("cos") or []
    if not enabled() or len(cos) < 2:
        return []
    th = _th()
    s = _sims([c["statement"] for c in cos], [c["statement"] for c in cos])
    out = []
    for i in range(len(cos)):
        for j in range(i + 1, len(cos)):
            if s[i, j] >= th["co_dup_sim"]:
                out.append(v("VS-CODUP", WARN, [cos[i]["id"], cos[j]["id"]],
                             f"{cos[i]['id']} and {cos[j]['id']} mean nearly the same (cosine {s[i, j]:.2f} ≥ {th['co_dup_sim']})",
                             cosine=round(float(s[i, j]), 3), model=MODEL))
    return out


def check_los(state: dict) -> list[dict]:
    cos, los = state.get("cos") or [], state.get("los") or []
    idx = {c["id"]: i for i, c in enumerate(cos)}
    los = [lo for lo in los if lo.get("parent_co") in idx]
    if not enabled() or not los:
        return []
    th = _th()
    s = _sims([lo["statement"] for lo in los], [c["statement"] for c in cos])
    out = []
    for i, lo in enumerate(los):
        j = idx[lo["parent_co"]]
        c, own = cos[j], float(s[i, j])
        if str(lo.get("bloom_level")) == str(c.get("bloom_level")) and own >= th["lo_copy_sim"]:
            out.append(v("VS-LOCOPY", WARN, [lo["id"], c["id"]],
                         f"{lo['id']} means nearly the same as its parent {c['id']} (cosine {own:.2f} ≥ {th['lo_copy_sim']}); "
                         f"an LO must be a narrower, single-task step", cosine=round(own, 3), model=MODEL))
        others = [(float(s[i, k]), cos[k]["id"]) for k in range(len(cos)) if k != j]
        if others:
            best, other = max(others)
            if best - own >= th["lo_fit_margin"]:
                out.append(v("VS-LOFIT", WARN, [lo["id"], other],
                             f"{lo['id']} is closer to {other} (cosine {best:.2f}) than to its parent {c['id']} ({own:.2f})",
                             own=round(own, 3), other=round(best, 3), model=MODEL))
    return out
