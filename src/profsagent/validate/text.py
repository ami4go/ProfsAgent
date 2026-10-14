"""Deterministic text helpers shared by the check modules (token sets, overlap, phrase coverage). NO LLM."""
from __future__ import annotations

import re


def toks(s: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", (s or "").lower()) if len(t) > 2}


def jacc(a: str, b: str) -> float:
    x, y = toks(a), toks(b)
    return len(x & y) / max(len(x | y), 1)


def covers(phrase: str, texts: list[str]) -> bool:
    """Deterministic check that a required phrase is visibly covered by some text (≥60% of its content tokens).
    'programming' is ignored only while ≥2 other tokens remain: dropping it from "functional programming" left the
    single token 'functional', which matched "non-functional requirements"."""
    p = toks(phrase) - {"and", "the", "using", "with"}
    if len(p - {"programming"}) >= 2:
        p -= {"programming"}
    return bool(p) and any(len(p & toks(t)) / len(p) >= 0.6 for t in texts)


def norm(s: str) -> str:
    """Lower-case alphanumerics with single spaces (removing '≥', '%' etc. must not leave double spaces)."""
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", "", (s or "").lower())).strip()
