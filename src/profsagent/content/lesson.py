"""A class taught as a short video series: 3-4 subtopics, each taught (not read) from the references, each ending in a
quiz.

    teach_class(run_id, lecture_id, options) -> manifest        python scripts/run_content.py teach --lectures W02.S1 [--video]

1. references  the lecture's sources are read (content/references.py: arXiv papers, web chapters, PDFs) and cut into
               passages; the ones closest to the topic and outcomes go to the plan
2. B4 plan     3-4 parts in teaching order: outcomes, what each teaches, key ideas, one worked example, minutes
3. B5 per part the passages closest to that part ground it; the AI writes 5-8 slides whose `narration` is the spoken
               teaching (150-220 words per slide: motivation, mechanism, intuition, the example with numbers, a
               misconception), short bullets as anchors only, a recap and 3 quiz questions. Checked in code (below);
               with errors the part is asked for again once and kept only if errors drop.
4. decks       one deck per part: the part's title slide, its teaching slides (narration = speaker notes), the recap,
               then each question on its own slide followed by an answer slide that explains it. narrate.py turns each
               part into a video (the question is asked, "pause the video", then the answer slide explains).
Checks: L-COUNT (slide count), L-NARRATION (too short to teach / too long), L-COPY (12+ words copied word for word from a
reference), L-REF (an unknown passage id), L-UNCITED (most slides cite no passage), L-QUIZ (3 valid questions),
L-LO (an outcome no part teaches), plus the deck figure checks and compiled code snippets.
Output: material/<lecture>/lesson/{lesson.json, lesson.md, references.json, part_1/ … part_N/ (the usual deck files)}.
"""
from __future__ import annotations

import re
from typing import Callable

from profsagent.content import generate as G
from profsagent.content.checks import _figure
from profsagent.content.models import LectureDeck, LessonPlan, Slide, TeachingPart
from profsagent.content.references import passages, reference_text, retrieve
from profsagent.content.style import apply_look, load_style
from profsagent.content.verify import check_code
from profsagent.delivery.brief import clean
from profsagent.delivery.common import load_state, now, write_json
from profsagent.llm.prompts import load_prompt
from profsagent.validate.record import ERR, WARN, errors, v

LETTERS = "ABCDE"


def _ask(llm, pid: str, ctx: dict, model_cls, run_id: str, log):
    p = load_prompt(pid)
    system, user = p.render(**ctx)
    obj, rec = llm.structured(system=system, user=user, model_cls=model_cls, role=p.meta.get("model_class", "generate"),
                              temperature=float(p.meta.get("temperature", 0.3)), prompt_id=pid, prompt_version=p.version,
                              run_id=run_id)
    log(f"  [{pid}] ok via {rec.endpoint} · {rec.prompt_tokens}+{rec.output_tokens} tok")
    return obj, {"prompt": pid, "endpoint": rec.endpoint, "prompt_tokens": rec.prompt_tokens, "output_tokens": rec.output_tokens}


# ------------------------------------------------------------------ checks
def _words(t: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", t.lower())


def shingles(text: str, n: int) -> set[tuple]:
    w = _words(text)
    return {tuple(w[i:i + n]) for i in range(len(w) - n + 1)}


def check_part(tp: TeachingPart, known: dict[str, str], cfg: dict) -> list[dict]:
    """`known`: passage id -> text, the passages this part was given."""
    L, out = cfg["lesson"], []
    lo, hi = L["slides"]["min"], L["slides"]["max"]
    if not lo <= len(tp.slides) <= hi:
        out.append(v("L-COUNT", ERR, [], f"{len(tp.slides)} teaching slides (expected {lo}-{hi})"))
    copied = set().union(*(shingles(t, L["copy_ngram"]) for t in known.values())) if known else set()
    uncited = 0
    for i, s in enumerate(tp.slides, 1):
        sid = f"slide {i}"
        n = len(s.narration.split())
        if n < L["narration_words"]["min"]:
            out.append(v("L-NARRATION", ERR, [sid], f"{sid} ('{s.title}'): {n} words of narration is too little to teach "
                                                     f"(at least {L['narration_words']['min']})"))
        elif n > L["narration_words"]["max"]:
            out.append(v("L-NARRATION", WARN, [sid], f"{sid} ('{s.title}'): {n} words of narration (at most {L['narration_words']['max']})"))
        hits = shingles(s.narration, L["copy_ngram"]) & copied
        if hits:
            out.append(v("L-COPY", ERR, [sid], f"{sid} ('{s.title}') copies a reference word for word: \"{' '.join(next(iter(hits)))}…\"; "
                                               "explain it in your own words"))
        bad = [r for r in s.refs if r not in known]
        if bad:
            out.append(v("L-REF", ERR, [sid], f"{sid} cites unknown passages {bad}"))
        uncited += not s.refs
        out += _figure(sid, s.figure)
        if len(s.bullets) > 4 or any(len(b.split()) > 14 for b in s.bullets):
            out.append(v("L-BULLETS", WARN, [sid], f"{sid}: bullets are anchors (at most 4 of at most 12 words)"))
    if tp.slides and uncited > len(tp.slides) / 2:
        out.append(v("L-UNCITED", WARN, [], f"{uncited} of {len(tp.slides)} slides cite no reference passage"))
    if len(tp.quiz) != 3:
        out.append(v("L-QUIZ", ERR, [], f"{len(tp.quiz)} quiz questions (3 wanted)"))
    for j, q in enumerate(tp.quiz, 1):
        opts = [o.strip().lower() for o in q.options]
        if len(opts) < 3 or len(set(opts)) != len(opts) or not 0 <= q.answer < len(opts) or not q.explanation.strip():
            out.append(v("L-QUIZ", ERR, [f"question {j}"], f"question {j} needs 3-5 distinct options, a valid answer and an explanation"))
    return out


# ------------------------------------------------------------------ one part as a deck
def part_deck(lecture_id: str, n: int, of: int, title: str, tp: TeachingPart, los: list[str], wpm: int) -> LectureDeck:
    slides = []
    for s in tp.slides:
        if s.figure.kind == "code" and not s.figure.language:      # unnamed code is checked as Python when it reads as Python
            if re.search(r"^\s*(import |from \w+ import |def |class )|torch\.|np\.", s.figure.code, re.M):
                s.figure.language = "python"
        kind = "example" if s.figure.kind in ("table", "code") or re.search(r"\bexample|worked|step\b", s.title, re.I) else "concept"
        slides.append(Slide(kind=kind, title=s.title, bullets=s.bullets, figure=s.figure, notes=s.narration, los=los,
                            sources=sorted({r.split("#")[0] for r in s.refs}), minutes=round(len(s.narration.split()) / wpm, 1)))
    if tp.recap:
        slides.append(Slide(kind="summary", title="What you learned", bullets=[x.strip() for x in re.split(r"(?<=\.)\s+", tp.recap) if x.strip()][:4],
                            notes=tp.recap, los=los, minutes=0.5))
    for j, q in enumerate(tp.quiz, 1):
        ask = f"Quiz question {j}. {q.question} Pause the video and choose your answer."
        slides.append(Slide(kind="check", title=f"Quiz {j} of {len(tp.quiz)}", quiz=q, notes=ask, los=los, minutes=0.7))
        right = q.options[q.answer] if 0 <= q.answer < len(q.options) else "?"
        why = [x.strip() for x in re.split(r"(?<=[.!?])\s+", q.explanation) if x.strip()][:3]
        slides.append(Slide(kind="answer", title=f"Answer {j}: {LETTERS[q.answer] if 0 <= q.answer < 5 else '?'}",
                            bullets=[f"{LETTERS[q.answer] if 0 <= q.answer < 5 else '?'}. {right}"] + why, notes=f"The answer is {LETTERS[q.answer] if 0 <= q.answer < 5 else ''}: {right}. {q.explanation}",
                            los=los, minutes=0.7))
    return LectureDeck(lecture_id=f"{lecture_id}.P{n}", title=f"Part {n} of {of}: {title}", slides=slides)


def lesson_md(m: dict) -> str:
    L = [f"# {m['topic']} — taught in {len(m['parts'])} parts", "", f"*{m['lecture_id']} · made {m['made_at'][:16]}*", ""]
    for p in m["parts"]:
        L += [f"## Part {p['n']}: {p['title']} ({p['minutes']} min)", "", f"**Teaches:** {p['teaches']}", "",
              f"**Key ideas:** {'; '.join(p['key_ideas'])}", "", f"**Worked example:** {p['example']}", "",
              f"Files: `{p['dir']}/slides.pptx`, `notes.md` (the full narration), `student.html`" +
              (f"; {p['errors']} errors, {p['warnings']} warnings" if p["errors"] or p["warnings"] else ""), ""]
    L += ["## References read", ""] + [f"- [{r['id']}] {r['title']} — " + (f"{r['words']} words" if r["words"] else f"not read: {r['error']}")
                                       for r in m["references"]]
    return "\n".join(L) + "\n"


def teach_class(run_id: str, lecture_id: str, options: dict | None = None, *, llm=None, embed=None,
                log: Callable[[str], None] = print) -> dict:
    o, c = options or {}, G.cfg()
    L = c["lesson"]
    st = load_state(run_id)
    unit = G.units(st, c).get(lecture_id)
    if unit is None:
        raise KeyError(f"no lecture {lecture_id} in runs/{run_id}")
    from profsagent.llm.client import LLMClient
    llm = llm or LLMClient(G.out_dir(run_id) / "material" / "llm_calls.jsonl")
    sources = G.gather_sources(st, run_id, unit, False, c["sources"]["max_external"])
    log(f"B lesson {run_id} {lecture_id}: {unit['topic']} · reading {len(sources)} references")
    texts, refs = {}, []
    for sid, s in sources.items():
        row = {"id": sid, "title": s["title"], "url": s.get("url"), "words": 0, "error": ""}
        try:
            t = reference_text(s, L["max_pages"])
            row["words"] = len(t.split())
            if t:
                texts[sid] = t
            else:
                row["error"] = "no readable link (ISBN or paywalled DOI)"
        except Exception as e:  # noqa: BLE001 — a reference that cannot be read is reported; the others still ground the lesson
            row["error"] = f"{type(e).__name__}: {e}"[:160]
        refs.append(row)
        log(f"  [{sid}] {s['title'][:60]}: " + (f"{row['words']} words" if row["words"] else f"not read ({row['error']})"))
    ps = passages(texts)
    if not ps:
        raise ValueError(f"{lecture_id}: none of the references could be read, and the lesson must be grounded in them")
    lecture = G.lecture_input(unit)
    course = {"course_name": st["cco_compact"]["course_name"], "level": st.get("level")}
    query = unit["topic"] + ". " + " ".join(x["statement"] for x in lecture["learning_outcomes"])
    top = retrieve(query, ps, L["plan_passages"], embed=embed)
    calls = []
    plan, call = _ask(llm, "B4", {"course": course, "parts": L["parts"], "minutes": L["minutes"], "passages": top,
                                  "lecture": {k: lecture[k] for k in ("lecture_id", "topic", "minutes", "learning_outcomes",
                                                                       "builds_on", "prerequisites", "leads_to")}},
                      LessonPlan, run_id, log)
    calls.append(call)
    plan_found = []
    lo_ids = {x["id"] for x in lecture["learning_outcomes"]}
    for x in sorted(lo_ids - {lo for p in plan.parts for lo in p.los}):
        plan_found.append(v("L-LO", WARN, [x], f"{x} is taught by no part of the plan"))
    if not L["parts"]["min"] <= len(plan.parts) <= L["parts"]["max"]:
        plan_found.append(v("L-PLAN", WARN, [], f"{len(plan.parts)} parts (expected {L['parts']['min']}-{L['parts']['max']})"))
    prof = load_style(run_id)
    c_render = apply_look(c, prof)
    base = G.material_dir(run_id, lecture_id) / "lesson"
    parts_out, used = [], set()
    for n, p in enumerate(plan.parts, 1):
        q = f"{p.title}. {p.teaches} {' '.join(p.key_ideas)} {p.example}"
        given = retrieve(q, ps, L["part_passages"], embed=embed, exclude=used if L["spread_passages"] else frozenset())
        known = {x["id"]: x["text"] for x in given}
        ctx = {"course": course, "before": [x.title for x in plan.parts[:n - 1]], "slides": L["slides"], "problems": [],
               "part": {"number": n, "of": len(plan.parts), **p.model_dump()},
               "passages": [{k: x[k] for k in ("id", "source", "text")} for x in given]}
        log(f"  part {n}/{len(plan.parts)}: {p.title} ({len(given)} passages)")
        tp, call = _ask(llm, "B5", ctx, TeachingPart, run_id, log)
        calls.append(call)
        found = check_part(tp, known, c)
        if errors(found):
            ctx["problems"] = [{"code": x["code"], "where": x["nodes"], "problem": x["message"]} for x in errors(found)]
            tp2, call = _ask(llm, "B5", ctx, TeachingPart, run_id, log)
            calls.append(call)
            found2 = check_part(tp2, known, c)
            keep = len(errors(found2)) < len(errors(found))
            log(f"  [B5 repair] errors {len(errors(found))} → {len(errors(found2))} {'ACCEPT' if keep else 'REJECT'}")
            if keep:
                tp, found = tp2, found2
        used |= {r for s in tp.slides for r in s.refs}
        deck = part_deck(lecture_id, n, len(plan.parts), p.title, tp, p.los or sorted(lo_ids), L["words_per_minute"])
        code_found, code_report = check_code(deck)
        found += code_found
        d = base / f"part_{n}"
        d.mkdir(parents=True, exist_ok=True)
        course_name = course["course_name"]
        fr = {"course": course_name, "footer": f"{course_name}  ·  {lecture_id} · part {n}/{len(plan.parts)}",
              "subtitle": f"{unit['topic']} · Part {n} of {len(plan.parts)} · about {p.minutes} min",
              "draft_note": "Teaching video drafted by ProfsAgent from the course's references: check before sharing.",
              "objectives": [p.teaches] + p.key_ideas,
              "objectives_notes": f"In this part: {p.title}. {p.teaches}"}
        nslides, found = G.write_outputs(d, deck, fr, sources, c_render, found)
        for x in found:
            x.setdefault("stage", "lesson")
        narr = sum(len(s.narration.split()) for s in tp.slides)
        pm = {"n": n, "title": p.title, "teaches": p.teaches, "key_ideas": p.key_ideas, "example": p.example, "los": p.los,
              "minutes": p.minutes, "dir": str(d.relative_to(G.out_dir(run_id))).replace("\\", "/"), "slides": nslides,
              "teaching_slides": len(tp.slides), "quiz": [x.model_dump() for x in tp.quiz], "narration_words": narr,
              "narration_minutes": round(narr / L["words_per_minute"], 1), "passages": sorted(known),
              "errors": len(errors(found)), "warnings": len(found) - len(errors(found)), "findings": found, "code_checks": code_report}
        if o.get("video") or o.get("narrate"):        # the part's video: narrated slides, its quiz at the end
            from profsagent.content.narrate import narrate
            pm["narration"] = narrate(d, deck, fr, c_render, video=bool(o.get("video")), animate=bool(o.get("animate")))
            log(f"  part {n}: {pm['narration']['minutes']} min of video")
        pm["teaching"] = tp.model_dump()               # what B5 wrote, so the part can be rebuilt without a call
        write_json(d / "part.json", pm)
        parts_out.append(pm)
        log(f"  part {n}: {len(tp.slides)} teaching slides, {narr} words of narration (~{pm['narration_minutes']} min), "
            f"{len(tp.quiz)} questions · {pm['errors']} errors, {pm['warnings']} warnings")
    m = {"lecture_id": lecture_id, "topic": unit["topic"], "made_at": now(), "plan": plan.model_dump(), "plan_findings": plan_found,
         "parts": parts_out, "references": refs, "calls": calls, "status": "draft"}
    write_json(base / "lesson.json", m)
    write_json(base / "references.json", {"references": refs, "passages_used": sorted(used)})
    (base / "lesson.md").write_text(lesson_md(m), encoding="utf-8")
    log(f"  lesson: {len(parts_out)} parts → {base}")
    return m
