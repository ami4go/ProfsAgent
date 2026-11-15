r"""Deterministic checks of a generated lecture deck (no LLM). Findings use the Phase 1 violation record
(validate/record.py), so they read like every other validator finding.

    D-LO        error    a learning outcome of the lecture is served by no slide
    D-APPLY     warning  an outcome at Bloom level 3+ has no example / worked problem slide
    D-REF       error    a slide names an unknown outcome or source id
    D-COUNT     error    content slide count outside the range for the lecture's hours (config/content.yaml)
    D-EMPTY     error    a slide with no bullets, blocks, figure or question
    D-FIGURE    error    a figure that cannot be drawn (flow < 2 steps, empty code, ragged or oversized table, a plot
                         whose series are not lists of numbers the example computed, or of different lengths)
    D-VALUE     error    [[name]] for a value the running example did not compute (content/example.py)
    D-ARITH     error    a formula whose number-only parts do not agree, e.g. "0.2^2 + 0.3^2 = 0.6" (content/arith.py)
    D-EXAMPLE   warning  the example's code failed even after a repair: the deck has no computed numbers
    D-BLOCK     error    a block missing what its kind needs (a formula, 2+ steps, a term and meaning, text)
                warning  a derivation step after the first without its reason, or more than 6 steps on one slide
    D-MATH      error    unbalanced braces or \( \) delimiters in maths (KaTeX's own errors come from the render)
    D-TEMPLATE  error    unfilled {placeholder} text (outside maths, where braces are LaTeX)
    D-DENSE     warning  too many or too long bullets
    D-QUIZ      error    a check slide without a question, or a question with 3-5 options missing or a wrong answer index
                         (warning: no explanation)
    D-NOTES     warning  a slide without speaker notes
    D-TIME      warning  the slides' minutes differ from the lecture length by more than the tolerance
    D-CHECK     warning  fewer check-for-understanding slides than lecture hours
    D-OVERFLOW  error    a slide that does not fit even at the smallest text size, measured in Chrome (slides_html.py)
                warning  .pptx text estimated not to fit its box (render.py), or a title over two lines
With deliverable C's outline (lecture.outline: the class's parts, their minutes and how each is delivered):
    D-OUTLINE   error    a slide names a part that is not in the outline
                warning  a part of the outline has no slide; the recap is not first or the review quiz not last
    D-WATCH     warning  a part delivered by a video (YouTube or NotebookLM) has no watch slide, or a watch slide
                         has no clip to show
    D-SIM       warning  a part delivered by a simulation has no simulation slide
"""
from __future__ import annotations

import re

from profsagent.content.arith import check_arith
from profsagent.content.example import PLACEHOLDER
from profsagent.content.models import FIRST_CONTENT_SLIDE, LectureDeck
from profsagent.content.slides_html import plot_problems
from profsagent.validate.record import ERR, WARN, v

HOLE = re.compile(r"\{[a-z_][a-z0-9_]*\}", re.I)
MATH_SPAN = re.compile(r"\\\((.*?)\\\)|\\\[(.*?)\\\]|\$\$(.*?)\$\$", re.S)   # \( \), \[ \] and $$ $$ spans
INLINE = re.compile(r"\\\((.*?)\\\)", re.S)
OPEN_MATH = re.compile(r"\\[(\[].*", re.S)                                         # an unclosed \( or \[ to the end
BARE_TEX = re.compile(r"\\[A-Za-z]+(?:\{[^{}]*\})*")                                # \hat{y}, \frac{a}{b}, \alpha


def content_range(hours: float, cfg: dict, depth: str = "standard") -> tuple[int, int]:
    per = (cfg["deck"].get("slides_per_hour_by_depth") or {}).get(depth) or cfg["deck"]["slides_per_hour"]
    return max(3, round(per["min"] * hours)), max(4, round(per["max"] * hours))


def slide_range(lecture: dict, cfg: dict) -> tuple[int, int]:
    """Content slides wanted: exactly the professor's count when given (lecture.content_slides), else the range for the
    lecture's hours at its content depth."""
    n = lecture.get("content_slides")
    return (n, n) if n else content_range(lecture["hours"], cfg, lecture.get("depth") or "standard")


def check_deck(deck: LectureDeck, lecture: dict, source_ids: set[str], cfg: dict, values: dict | None = None) -> list[dict]:
    """`lecture`: the brief as given to B1 (learning_outcomes with id and bloom_level, hours, minutes). `values`: the
    running example's computed values (content/example.py), after they were filled into the deck."""
    d, out = cfg["deck"], []
    los = {lo["id"]: lo for lo in lecture["learning_outcomes"]}
    served = {lo for s in deck.slides for lo in s.los}
    applied = {lo for s in deck.slides if s.kind in ("example", "worked_problem", "activity") for lo in s.los}
    for lo_id, lo in los.items():
        if lo_id not in served:
            out.append(v("D-LO", ERR, [lo_id], f"{lo_id} is served by no slide"))
        elif int(lo.get("bloom_level") or 0) >= 3 and lo_id not in applied:
            out.append(v("D-APPLY", WARN, [lo_id], f"{lo_id} (Bloom {lo['bloom_level']}) has no example, worked problem or activity slide"))

    lo_min, lo_max = slide_range(lecture, cfg)
    if not lo_min <= len(deck.slides) <= lo_max:
        out.append(v("D-COUNT", ERR, [], f"{len(deck.slides)} content slides for a {lecture['hours']:g}-hour lecture "
                                         + (f"(the professor asked for {lo_min})" if lo_min == lo_max else f"(expected {lo_min}–{lo_max})"),
                     expected=[lo_min, lo_max]))
    for i, s in enumerate(deck.slides, FIRST_CONTENT_SLIDE):
        sid = f"slide {i}"
        for bad in sorted(set(s.los) - set(los)):
            out.append(v("D-REF", ERR, [sid], f"{sid} names unknown outcome {bad}"))
        for bad in sorted(set(s.sources) - source_ids):
            out.append(v("D-REF", ERR, [sid], f"{sid} cites unknown source {bad}"))
        if not s.bullets and not s.blocks and s.figure.kind == "none" and s.quiz is None:
            out.append(v("D-EMPTY", ERR, [sid], f"{sid} ('{s.title}') has no bullets, blocks, figure or question"))
        out += _figure(sid, s.figure, values or {}) + _quiz(sid, s) + _blocks(sid, s) + check_arith(sid, s)
        left = sorted(set(PLACEHOLDER.findall(s.model_dump_json())))      # fill_values left only unknown names
        if left:
            out.append(v("D-VALUE", ERR, [sid], f"{sid} names values the example did not compute: "
                                                f"{', '.join(f'[[{x}]]' for x in left)} (use only the example's names)"))
        q = s.quiz
        fields = [s.title, *s.bullets, s.notes, s.figure.caption, *s.figure.steps, *(c for r in s.figure.rows for c in r),
                  *(x for b in s.blocks for x in (b.term, b.text)), *([q.question, *q.options, q.explanation] if q else [])]
        # braces inside maths are LaTeX, not template holes (an unclosed \( is D-MATH: its rest is maths too)
        plain = [OPEN_MATH.sub(" ", MATH_SPAN.sub(" ", f)) for f in fields]
        shown = (plain[:2 + len(s.bullets)] + plain[3 + len(s.bullets):]                # all but the notes (spoken),
                 + [OPEN_MATH.sub(" ", MATH_SPAN.sub(" ", st.why)) for b in s.blocks for st in b.steps])   # + step reasons
        bare = sorted({m.group() for t in shown for m in BARE_TEX.finditer(t)})
        if bare:
            out.append(v("D-MATH", ERR, [sid], f"{sid}: LaTeX outside maths delimiters, shown as raw code: {', '.join(bare[:4])} "
                                               "(write it inside \\( ... \\), also in tables, flow boxes and captions)"))
        text = " ".join(BARE_TEX.sub(" ", t) for t in plain)
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
    out += check_outline(deck, lecture.get("outline") or [])
    for x in out:
        x["stage"] = "content"
    return out


def check_outline(deck: LectureDeck, outline: list[dict]) -> list[dict]:
    """The deck against C's plan for the class: every part taught, video and simulation parts introduced, the recap
    first and the review quiz last."""
    if not outline:
        return []
    parts = {p["id"]: p for p in outline}
    slides = list(enumerate(deck.slides, FIRST_CONTENT_SLIDE))
    by_part: dict[str, list] = {}
    out = []
    for i, s in slides:
        if s.component and s.component not in parts:
            out.append(v("D-OUTLINE", ERR, [f"slide {i}"], f"slide {i} names part {s.component}, which is not in the outline"))
        by_part.setdefault(s.component, []).append((i, s))
    for pid, p in parts.items():
        mine = by_part.get(pid) or []
        if not mine:
            out.append(v("D-OUTLINE", WARN, [pid], f"part {pid} ('{p['title']}', {p['minutes']} min) has no slide"))
            continue
        kinds = {s.kind for _, s in mine}
        if p.get("delivered_by") in ("video", "notebooklm") and "watch" not in kinds:
            out.append(v("D-WATCH", WARN, [pid], f"part {pid} ('{p['title']}') is delivered by a video but has no watch slide"))
        if p.get("way") == "simulation" and "simulation" not in kinds:
            out.append(v("D-SIM", WARN, [pid], f"part {pid} ('{p['title']}') is delivered by a simulation but has no simulation slide"))
    for i, s in slides:
        if s.kind == "watch" and not s.clip and (parts.get(s.component) or {}).get("delivered_by") == "video":
            out.append(v("D-WATCH", WARN, [f"slide {i}"], f"slide {i} ('{s.title}') is a watch slide with no clip from the outline"))
    first = [p for p in outline if p.get("kind") == "recap"]
    last = [p for p in outline if p.get("kind") == "quiz"]
    if first and deck.slides and deck.slides[0].component != first[0]["id"]:
        out.append(v("D-OUTLINE", WARN, ["slide 3"], "the recap of the previous lecture should open the class"))
    if last and deck.slides and deck.slides[-1].component != last[-1]["id"]:
        out.append(v("D-OUTLINE", WARN, [f"slide {slides[-1][0]}"], "the review quiz should close the class"))
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


def balanced(tex: str) -> bool:
    r"""Braces balanced (escaped \{ \} do not count) and \left / \right paired."""
    depth = 0
    for m in re.finditer(r"\\.|[{}]", tex):
        t = m.group()
        depth += 1 if t == "{" else -1 if t == "}" else 0
        if depth < 0:
            return False
    return depth == 0 and len(re.findall(r"\\left\b", tex)) == len(re.findall(r"\\right\b", tex))


def text_math_ok(t: str) -> bool:
    r"""Inline maths in plain text: every \( closed by \), and the maths inside balanced."""
    return t.count("\\(") == t.count("\\)") and all(balanced(x) for x in INLINE.findall(t))


def _blocks(sid: str, s) -> list[dict]:
    out = []
    for k, b in enumerate(s.blocks, 1):
        where = f"{sid} block {k} ({b.kind})"
        need = {"math": b.latex.strip(), "steps": len(b.steps) >= 2, "definition": b.term.strip() and b.text.strip(),
                "think": b.text.strip(), "note": b.text.strip()}[b.kind]
        if not need:
            out.append(v("D-BLOCK", ERR, [sid], f"{where} is missing its " + {"math": "formula", "steps": "steps (at least 2)",
                       "definition": "term or meaning", "think": "question", "note": "text"}[b.kind]))
        if b.kind == "steps" and any(not st.why.strip() for st in b.steps[1:]):
            out.append(v("D-BLOCK", WARN, [sid], f"{where}: every step after the first needs the reason it follows"))
        if b.kind == "steps" and len(b.steps) > 6:
            out.append(v("D-BLOCK", WARN, [sid], f"{where}: {len(b.steps)} steps on one slide (at most 6): split the derivation"))
        tex = [b.latex] + [st.latex for st in b.steps]
        bad = [t for t in tex if t and not balanced(t)]
        bad += [t for t in (b.text, b.term) if not text_math_ok(t)]
        if bad:
            out.append(v("D-MATH", ERR, [sid], f"{where}: unbalanced braces or delimiters in {bad[0][:80]!r}"))
    for t in [s.title, *s.bullets, *([s.quiz.question, *s.quiz.options] if s.quiz else [])]:
        if not text_math_ok(t):
            out.append(v("D-MATH", ERR, [sid], f"{sid}: unbalanced braces or delimiters in {t[:80]!r}"))
            break
    return out


def _figure(sid: str, f, values: dict | None = None) -> list[dict]:
    values = values or {}
    if f.kind == "plot":
        bad = plot_problems(f.plot, values)
        return [v("D-FIGURE", ERR, [sid], f"{sid}: the plot cannot be drawn: {bad[0]}")] if bad else []
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
