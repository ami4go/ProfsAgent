"""Deterministic Bloom tagging and CO quality scoring (docs/01 §4.4). No LLM."""
from __future__ import annotations

import re
from functools import lru_cache

from profsagent.config import bloom_lexicon

PREFIX_RE = re.compile(r"^\s*(students?\s+(are|will be|should be)\s+able\s+to|the\s+students?\s+will|able\s+to|to)\s+", re.I)
NOT_STUDENT_CENTRED = re.compile(r"^\s*(to\s+(get|introduce|familiari[sz]e|provide|expose|teach)|familiarity|in-?depth understanding|understanding|improved ability|knowledge of|this course)", re.I)


@lru_cache(maxsize=1)
def _lex() -> tuple[dict[str, int], set[str], list[str], dict[str, list[int]]]:
    lx = bloom_lexicon()
    verb_level = {v.lower(): int(lvl) for lvl, vs in lx["levels"].items() for v in vs}
    banned = [b.lower() for b in lx["banned"]]
    return verb_level, set(lx.get("vague_degree_words", [])), banned, {k: v for k, v in lx.get("ambiguous", {}).items()}


def lemma(word: str) -> str:
    w = word.lower().strip(".,;:()")
    verb_level = _lex()[0]
    if w in verb_level:
        return w
    for suf, rep in (("ies", "y"), ("es", ""), ("s", ""), ("ed", ""), ("ing", ""), ("ing", "e"), ("ed", "e")):
        if w.endswith(suf) and (w[: -len(suf)] + rep) in verb_level:
            return w[: -len(suf)] + rep
    return w


def verbs_in(text: str) -> list[str]:
    verb_level = _lex()[0]
    body = PREFIX_RE.sub("", text or "")
    return [lemma(t) for t in re.findall(r"[A-Za-z-]+", body) if lemma(t) in verb_level]


def banned_in(text: str) -> list[str]:
    t = (text or "").lower()
    return [b for b in _lex()[2] if re.search(rf"\b{re.escape(b)}\b", t)]


def leading_verb(text: str) -> str | None:
    body = PREFIX_RE.sub("", text or "").strip()
    first = re.findall(r"[A-Za-z-]+", body)[:1]
    if first and lemma(first[0]) in _lex()[0]:
        return lemma(first[0])
    vs = verbs_in(text)
    return vs[0] if vs else None


def bloom_of_verb(verb: str | None) -> int | None:
    if not verb:
        return None
    return _lex()[0].get(lemma(verb))


def vague_degree(degree: str | None) -> list[str]:
    if not degree:
        return []
    words = set(re.findall(r"[a-z]+", degree.lower()))
    return sorted(words & _lex()[1]) if len(words) <= 4 else []


def co_quality(text: str) -> tuple[float, list[str], str | None, int | None]:
    """Returns (score 0..1, flags, leading_verb, bloom_lexicon)."""
    flags: list[str] = []
    lv = leading_verb(text)
    score = 0.0
    if lv and not banned_in(text.split(",")[0]):
        score += 0.25
    else:
        flags.append("vague_verb")
    if NOT_STUDENT_CENTRED.match(text or ""):
        flags.append("not_student_centred")
    else:
        score += 0.25
    low = (text or "").lower()
    if re.search(r"\b(given|using|for (a|an|the)|with|under|in the context of|from)\b", low):
        score += 0.2
    else:
        flags.append("no_condition")
    if re.search(r"\d|\bat least\b|\bsuch that\b|\bwithin\b|\bwithout\b|\bmeeting\b|\bsatisf", low):
        score += 0.2
    else:
        flags.append("no_degree")
    if len(set(verbs_in(text))) <= 2:
        score += 0.1
    else:
        flags.append("multi_outcome")
    return round(score, 2), flags, lv, bloom_of_verb(lv)
