"""Deterministic checks of a generated lecture deck (no LLM). Findings use the Phase 1 violation record
(validate/record.py), so they read like every other validator finding.

    D-LO        error    a learning outcome of the lecture is served by no slide
    D-APPLY     warning  an outcome at Bloom level 3+ has no example / worked problem slide
    D-REF       error    a slide names an unknown outcome or source id
    D-COUNT     error    content slide count outside the range for the lecture's hours (config/content.yaml)
    D-EMPTY     error    a slide with neither bullets nor a figure
    D-FIGURE    error    a figure that cannot be drawn (flow < 2 steps, empty code, ragged or oversized table)
    D-TEMPLATE  error    unfilled {placeholder} text
    D-DENSE     warning  too many or too long bullets
    D-QUIZ      error    a check slide without a question, or a question with 3-5 options missing or a wrong answer index
                         (warning: no explanation)
    D-NOTES     warning  a slide without speaker notes
    D-TIME      warning  the slides' minutes differ from the lecture length by more than the tolerance
    D-CHECK     warning  fewer check-for-understanding slides than lecture hours
    D-OVERFLOW  warning  text that does not fit its box even at the smallest font (raised by render.py)
"""
from __future__ import annotations

import re

from profsagent.content.models import FIRST_CONTENT_SLIDE, LectureDeck
from profsagent.validate.record import ERR, WARN, v

HOLE = re.compile(r"\{[a-z_][a-z0-9_]*\}", re.I)


def content_range(hours: float, cfg: dict) -> tuple[int, int]:
    per = cfg["deck"]["slides_per_hour"]
    return max(3, round(per["min"] * hours)), max(4, round(per["max"] * hours))


def check_deck(deck: LectureDeck, lecture: dict, source_ids: set[str], cfg: dict) -> list[dict]:
    """`lecture`: the brief as given to B1 (learning_outcomes with id and bloom_level, hours, minutes)."""
    d, out = cfg["deck"], []
    los = {lo["id"]: lo for lo in lecture["learning_outcomes"]}
    served = {lo for s in deck.slides for lo in s.los}
    applied = {lo for s in deck.slides if s.kind in ("example", "worked_problem", "activity") for lo in s.los}
    for lo_id, lo in los.items():
        if lo_id not in served:
            out.append(v("D-LO", ERR, [lo_id], f"{lo_id} is served by no slide"))
        elif int(lo.get("bloom_level") or 0) >= 3 and lo_id not in applied:
            out.append(v("D-APPLY", WARN, [lo_id], f"{lo_id} (Bloom {lo['bloom_level']}) has no example, worked problem or activity slide"))

    lo_min, lo_max = content_range(lecture["hours"], cfg)
    if not lo_min <= len(deck.slides) <= lo_max:
        out.append(v("D-COUNT", ERR, [], f"{len(deck.slides)} content slides for a {lecture['hours']:g}-hour lecture "
                                         f"(expected {lo_min}–{lo_max})", expected=[lo_min, lo_max]))
    for i, s in enumerate(deck.slides, FIRST_CONTENT_SLIDE):
        sid = f"slide {i}"
        for bad in sorted(set(s.los) - set(los)):
            out.append(v("D-REF", ERR, [sid], f"{sid} names unknown outcome {bad}"))
        for bad in sorted(set(s.sources) - source_ids):
            out.append(v("D-REF", ERR, [sid], f"{sid} cites unknown source {bad}"))
        if not s.bullets and s.figure.kind == "none" and s.quiz is None:
            out.append(v("D-EMPTY", ERR, [sid], f"{sid} ('{s.title}') has no bullets, figure or question"))
        out += _figure(sid, s.figure) + _quiz(sid, s)
        q = s.quiz
        text = " ".join([s.title, *s.bullets, s.notes, s.figure.caption, *s.figure.steps, *(c for r in s.figure.rows for c in r),
                         *([q.question, *q.options, q.explanation] if q else [])])
        if HOLE.search(text):
            out.append(v("D-TEMPLATE", ERR, [sid], f"{sid} has unfilled template text {sorted(set(HOLE.findall(text)))}"))
        long = [b for b in s.bullets if len(b.split()) > d["max_bullet_words"]]
        if len(s.bullets) > d["max_bullets"] or long:
            out.append(v("D-DENSE", WARN, [sid], f"{sid}: {len(s.bullets)} bullets, {len(long)} over {d['max_bullet_words']} words"))
        if not s.notes.strip():
            out.append(v("D-NOTES", WARN, [sid], f"{sid} ('{s.title}') has no speaker notes"))

    minutes = sum(s.minutes for s in deck.slides)
    if abs(minutes - lecture["minutes"]) > d["minutes_tolerance"] * lecture["minutes"]:
        out.append(v("D-TIME", WARN, [], f"slides add up to {minutes:g} min for a {lecture['minutes']:g}-min lecture"))
    checks, wanted = sum(s.kind == "check" for s in deck.slides), max(1, round(lecture["hours"]))
    if checks < wanted:
        out.append(v("D-CHECK", WARN, [], f"{checks} check-for-understanding slides for a {lecture['hours']:g}-hour lecture "
                                         f"(at least {wanted}, one per hour)"))
    for x in out:
        x["stage"] = "content"
    return out


def _quiz(sid: str, s) -> list[dict]:
    q = s.quiz
    if s.kind == "check" and q is None:
        return [v("D-QUIZ", ERR, [sid], f"{sid} is a check slide without a question")]
    if q is None:
        return []
    opts = [o.strip().lower() for o in q.options]
    if not 3 <= len(opts) <= 5 or len(set(opts)) != len(opts):
        return [v("D-QUIZ", ERR, [sid], f"{sid}: a question needs 3-5 distinct options, has {len(opts)}")]
    if not 0 <= q.answer < len(opts):
        return [v("D-QUIZ", ERR, [sid], f"{sid}: answer index {q.answer} is not one of the {len(opts)} options")]
    if not q.explanation.strip():
        return [v("D-QUIZ", WARN, [sid], f"{sid}: the question has no explanation for the answer")]
    return []


def _figure(sid: str, f) -> list[dict]:
    if f.kind == "flow" and len([x for x in f.steps if x.strip()]) < 2:
        return [v("D-FIGURE", ERR, [sid], f"{sid}: a flow needs at least 2 steps")]
    if f.kind == "flow" and len(f.steps) > 6:
        return [v("D-FIGURE", ERR, [sid], f"{sid}: a flow of {len(f.steps)} steps does not fit (at most 6)")]
    if f.kind == "code" and not f.code.strip():
        return [v("D-FIGURE", ERR, [sid], f"{sid}: empty code figure")]
    if f.kind == "table":
        widths = {len(r) for r in f.rows}
        if len(f.rows) < 2 or len(widths) != 1:
            return [v("D-FIGURE", ERR, [sid], f"{sid}: a table needs a header and rows of equal width")]
        if len(f.rows) > 6 or max(widths) > 4:
            return [v("D-FIGURE", ERR, [sid], f"{sid}: a {len(f.rows)}x{max(widths)} table does not fit (at most 6x4)")]
    return []
