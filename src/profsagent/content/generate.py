"""Phase 2 deliverable B: generate one lecture's slides and notes from its brief (the survey's `generate_material`).

    generate_material(run_id, lecture_id, options) -> manifest

Flow, one lecture at a time:
  1. inputs   the lecture brief (delivery/brief.py), the course's verified Phase 1 resources and C's resources for the
              lecture (approved only, unless options.include_pending), each given a short id the slides can cite
  2. B6       the running example (content/example.py): the AI writes small data and Python that computes every number
              the lecture shows; code runs it (checked, sandboxed) and keeps the values (example.json). None for a topic
              without a numeric example; if the code still fails after a repair, a D-EXAMPLE warning
  3. B1       one AI call writes the content slides (content/models.LectureDeck), writing [[name]] for the example's
              numbers (code fills them in) and plots that name the example's values (code draws them)
  4. checks   content/checks.py (structure) and content/verify.py (code syntax, citation match); with errors, B1 is
              asked again with the findings (kept only if errors drop)
  5. B2       only when options.review == "ai" (a professor who wants the system to check the slides): a different
              model reviews the deck and answers its quiz blind (content/ai_review.py); its errors get one B1 repair
  6. frame    code writes the title, objectives and references slides from the brief and the cited sources
  7. render   slides.html with typeset maths and plots, measured in Chrome (content/slides_html.py; with checks, so an
              overflowing slide or a formula KaTeX cannot parse goes back to B1 like any other error), slides.pdf from
              it, slides.pptx (with speaker notes; a slide with maths or a plot carries its body as a picture), notes.md
Output: runs/<id>/delivery/material/<lecture_id>/{deck.json, example.json, slides.html, slides.pdf, slides.pptx,
notes.md, quiz.json, material.json}; the AI calls are logged in material/llm_calls.jsonl. material.json `status` starts as draft (ai-reviewed after B2); the
professor's decision (content/review.py) sets approved | redo | rejected.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from profsagent.config import load_yaml
from profsagent.content.ai_review import after_repair, model_of, review_deck
from profsagent.content.checks import check_deck, content_range, slide_range  # noqa: F401  (content_range: run_content)
from profsagent.content.models import FIRST_CONTENT_SLIDE, LectureDeck
from profsagent.content.render import render_markdown, render_pptx
from profsagent.content.sessions import build_sessions
from profsagent.content.example import fill_values, make_example
from profsagent.content.plan import make_plan, repair_slides, write_deck
from profsagent.content.example import for_b1 as example_for_b1
from profsagent.content.slides_html import deck_html, layout_findings, measure, needs_picture
from profsagent.content.student import student_page
from profsagent.content.style import apply_look, for_b1, load_style
from profsagent.content.verify import verify
from profsagent.delivery.brief import build_briefs, clean
from profsagent.delivery.common import load_state, now, out_dir, read_json, write_json
from profsagent.llm.client import LLMClient
from profsagent.llm.prompts import load_prompt
from profsagent.validate.record import WARN, errors, v

PID = "B1"
KINDS = ("reading", "video", "practice", "recorded_lecture")


def cfg() -> dict:
    return load_yaml("config/content.yaml")


def material_dir(run_id: str, lecture_id: str) -> Path:
    return out_dir(run_id) / "material" / lecture_id


def units(st: dict, c: dict | None = None) -> dict[str, dict]:
    """Every lecture a deck can be made for: the class sessions (W03.S1: config `classes`, content/sessions.py) and
    C's per-topic briefs (W03.L1), by id."""
    c = c or cfg()
    briefs = build_briefs(st)
    sessions = build_sessions(st, c["classes"]["per_week"], c["classes"]["minutes"], briefs)
    return {u["lecture_id"]: u for u in sessions + briefs}


# ------------------------------------------------------------------ inputs
def outline(run_id: str, brief: dict) -> list[dict]:
    """C's component plan for this lecture or class (deliverable C, delivery/components.py): what each part teaches, its
    minutes and how it is delivered (a video clip, a NotebookLM video, or in class). [] when C has no plan yet.
    With an approved delivery mix (delivery/mix.py) each part also carries `way` (slides, youtube, youtube_bridge,
    notebooklm, in_class, simulation), `when` (in_class / pre_class), the `bridge` points the slides add and the
    `simulation`; the recap and the quiz come first and last when C kept minutes for them."""
    from profsagent.delivery.components import for_window
    from profsagent.delivery.mix import outline_rows
    parts = brief.get("parts") or [{"lecture_id": brief["lecture_id"], "brief_from_min": 0, "brief_minutes": None, "minutes": None}]
    out = []
    for p in parts:
        lec = read_json(out_dir(run_id) / "lectures" / f"{p['lecture_id']}.json", {}) or {}
        how = {x["component"]: x for x in (lec.get("resources") or {}).get("timeline") or []}
        mixed = outline_rows(run_id, p["lecture_id"])
        comps = for_window(run_id, p["lecture_id"], p.get("brief_from_min", 0), p.get("brief_minutes"))
        scale = (p["minutes"] / p["brief_minutes"]) if p.get("minutes") and p.get("brief_minutes") else 1.0
        for c in comps:
            row = how.get(c["id"]) or {}
            mx = mixed.get(c["id"])
            segs = row.get("segments") or []
            if mx and mx["way"] not in ("youtube", "youtube_bridge"):
                segs = []
            clip = "; ".join(f"{s['start']}–{s['end']} of \"{s['video']}\"" for s in segs)
            how_by = row.get("delivery") or ("in_class" if c.get("in_class") else "slides")
            if mx:
                how_by = {"youtube": "video", "youtube_bridge": "video", "simulation": "in_class"}.get(mx["way"], mx["way"])
            out.append({"id": c["id"], "title": c["title"], "teaches": c["teaches"], "key_terms": c.get("key_terms", []),
                        "kind": c.get("kind"), "minutes": round(c.get("minutes_here", c["minutes"]) * scale),
                        "delivered_by": how_by, **({"clip": clip} if clip else {}),
                        **({"way": mx["way"], "when": mx["when"]} if mx else {}),
                        **({"bridge": mx["bridge"]} if mx and mx.get("bridge") else {}),
                        **({"simulation": mx["simulation"]} if mx and mx["way"] == "simulation" and mx.get("simulation") else {})})
    return class_edges(out)


def class_edges(parts: list[dict]) -> list[dict]:
    """C reserves a recap and a review quiz per topic lecture; a class that ends one topic and starts the next would get
    the first topic's quiz and the second's recap back to back mid-class. The recaps become one recap that opens the
    class and the quizzes one quiz that closes it, with the same minutes in total."""
    recaps = [p for p in parts if p.get("kind") == "recap"]
    quizzes = [p for p in parts if p.get("kind") == "quiz"]
    rest = [p for p in parts if p.get("kind") not in ("recap", "quiz")]
    merge = lambda xs: [{**xs[0], "minutes": sum(x["minutes"] for x in xs)}] if xs else []  # noqa: E731
    return merge(recaps) + rest + merge(quizzes)


def lecture_input(brief: dict, note: str = "", run_id: str | None = None) -> dict:
    """The brief as B1 sees it: statements cleaned of template holes, the time in minutes, and (with `run_id`) C's
    component plan as `outline`."""
    return {"lecture_id": brief["lecture_id"], "topic": brief["topic"], "module": brief["module"], "hours": brief["hours"],
            "minutes": round(brief["hours"] * 60),
            "learning_outcomes": [{"id": lo["id"], "statement": clean(lo["statement"]), "bloom_level": lo["bloom_level"]}
                                  for lo in brief["learning_outcomes"]],
            "course_outcomes": [{"id": c["id"], "statement": clean(c["statement"])} for c in brief["course_outcomes"]],
            "builds_on": brief.get("builds_on") or [],
            "prerequisites": [{"course": p["course"], "relied_topics": p.get("relied_topics", [])} for p in brief.get("prerequisite_courses") or []],
            "leads_to": brief.get("leads_to") or [], "assessed_in": brief.get("assessed_in") or [],
            "hands_on": brief.get("hands_on", False), "labs": brief.get("labs") or [], "professor_note": note,
            "parts": [{"topic": x["topic"], "minutes": x["minutes"]} for x in brief.get("parts") or []],
            **({"outline": o} if run_id and (o := outline(run_id, brief)) else {})}


def gather_sources(st: dict, run_id: str, brief: dict, include_pending: bool, max_external: int) -> dict[str, dict]:
    """Short id -> source. C1.. the course's verified resources that support this lecture's topics (all of them when none
    does); L1.. C's resources for the lecture (for a class session, for each topic part), approved (or, for testing,
    pending) items in rank order."""
    out: dict[str, dict] = {}
    course = st.get("resources") or []
    parts = brief.get("parts") or [brief]
    topics = {x["topic_id"] for x in parts}
    mine = [r for r in course if any(s.get("topic_id") in topics for s in r.get("supports_topics") or [])] or course
    for i, r in enumerate(mine, 1):
        out[f"C{i}"] = {"title": r.get("title"), "year": r.get("year"), "url": _link(r.get("identifier")),
                        "kind": r.get("role") or "course resource", "approved": True}
    picked = []
    for x in parts:
        lec = read_json(out_dir(run_id) / "lectures" / f"{x['lecture_id']}.json", {}) or {}
        items = (lec.get("resources") or {}).get("items") or {}
        picked += [it for kind in KINDS for it in items.get(kind) or [] if it not in picked and
                   (it.get("status_decision") == "approve" or (include_pending and it.get("status_decision") in (None, "pending")))]
    for i, it in enumerate(picked[:max_external], 1):
        out[f"L{i}"] = {"title": it.get("title"), "year": it.get("year") or (it.get("published") or "")[:4] or None,
                        "url": it.get("url"), "kind": it.get("kind"), "approved": it.get("status_decision") == "approve"}
    return out


def _link(identifier: dict | None) -> str | None:
    """A Phase 1 resource identifier {isbn, doi, arxiv, url} as one link (or the ISBN as text)."""
    i = identifier or {}
    return (i.get("url") or (f"https://doi.org/{i['doi']}" if i.get("doi") else None)
            or (f"https://arxiv.org/abs/{i['arxiv']}" if i.get("arxiv") else None) or (f"ISBN {i['isbn']}" if i.get("isbn") else None))


def frame_slides(sources: dict) -> int:
    """Slides code adds around the content: title and objectives, and references when the lecture has sources."""
    return 2 + (1 if sources else 0)


def frame(st: dict, brief: dict) -> dict:
    """Text of the slides code writes itself."""
    course = st["cco_compact"]["course_name"]
    los = [f"{clean(lo['statement'])} ({lo['id']})" for lo in brief["learning_outcomes"]]
    return {"course": course, "footer": f"{course}  ·  {brief['lecture_id']}",
            "subtitle": f"Week {brief['week']} · {brief['module']} · " + (f"{round(brief['hours'] * 60)} min" if brief.get("parts")
                                                                          else f"{brief['hours']:g} h"),
            "draft_note": "Draft generated by ProfsAgent from the course design: review and edit before teaching.",
            "objectives": los,
            "objectives_notes": "These are the lecture's learning outcomes from the approved course design. "
                                f"Assessed in: {', '.join(a['id'] for a in brief.get('assessed_in') or []) or 'not assessed directly'}."}


def fill_from_outline(deck: LectureDeck, outline: list[dict]) -> LectureDeck:
    """Code, not the AI, writes what a slide shows students to watch or open: a watch slide gets its part's clip, a
    simulation slide its part's simulation (title and link). Unknown parts are left to check_outline."""
    parts = {p["id"]: p for p in outline}
    for s in deck.slides:
        p = parts.get(s.component)
        if not p:
            continue
        if s.kind == "watch" and p.get("clip"):
            s.clip = p["clip"]
        if s.kind == "watch" and p.get("delivered_by") == "notebooklm" and not s.clip:
            s.clip = f"NotebookLM video on \"{p['title']}\" (made by the professor from the lecture's NotebookLM pack)"
        sim = p.get("simulation") or {}
        if s.kind == "simulation" and sim:
            s.link = " — ".join(x for x in (sim.get("title"), sim.get("url") or sim.get("id")) if x)
    return deck


# ------------------------------------------------------------------ outputs
def c_quiz(d: Path) -> list[dict] | None:
    """Deliverable C's closing review quiz (D8) for this lecture, as {question, options, answer index, explanation}; None
    when C has not made one (C files it under the topic lecture's id, delivery/quiz/<lecture>.json)."""
    q = read_json(d.parent.parent / "quiz" / f"{d.name}.json") or {}
    out = []
    for x in q.get("questions") or []:
        opts, a = x.get("options") or [], x.get("answer")
        i = "ABCDE".index(a.upper()) if isinstance(a, str) and len(a) == 1 and a.upper() in "ABCDE" else a
        if opts and isinstance(i, int) and 0 <= i < len(opts):
            out.append({"question": x["question"], "options": opts, "answer": i, "explanation": x.get("explanation") or x.get("why") or ""})
    return out or None


RENDER_CODES = ("D-OVERFLOW", "D-MATH", "D-RENDER")


def example_values(d: Path) -> dict:
    """The running example's computed values (example.json beside the deck), {} when the lecture has none."""
    return (read_json(d / "example.json") or {}).get("values") or {}


def browser_check(d: Path, deck: LectureDeck, fr: dict, sources: dict, c: dict, values: dict | None = None) -> list[dict]:
    """Write slides.html and measure it in Chrome: D-OVERFLOW and D-MATH errors for the repair loop. [] when the browser
    check is off or cannot run (write_outputs then reports D-RENDER)."""
    if not (c.get("html") or {}).get("measure", True):
        return []
    d.mkdir(parents=True, exist_ok=True)
    (d / "slides.html").write_text(deck_html(deck, fr, sources, c, values), encoding="utf-8")
    rep = measure(d / "slides.html", c)
    return [] if rep.get("error") else layout_findings(rep)


def write_outputs(d: Path, deck: LectureDeck, fr: dict, sources: dict, c: dict, found: list[dict]) -> tuple[int, list[dict]]:
    """deck.json, slides.html, slides.pdf, slides.pptx, notes.md and quiz.json; returns the slide count and the findings
    with the renderer's D-OVERFLOW / D-MATH / D-RENDER findings (replacing any from an earlier render)."""
    write_json(d / "deck.json", deck.model_dump())
    values = example_values(d)
    (d / "slides.html").write_text(deck_html(deck, fr, sources, c, values), encoding="utf-8")
    shots = {n: d / "shots" / f"slide_{n:02d}.png" for n, s in enumerate(deck.slides, FIRST_CONTENT_SLIDE) if needs_picture(s)}
    if (c.get("html") or {}).get("measure", True):
        rep = measure(d / "slides.html", c, pdf=d / "slides.pdf", shots=shots)
    else:
        rep = {"error": "the browser check is off (config/content.yaml html.measure)"}
    pictures = {n: Path(x) for n, x in (rep.get("shots") or {}).items()}
    rendered = layout_findings(rep) if not rep.get("error") else [
        {**v("D-RENDER", WARN, [], f"slides.pdf was not made and maths shows as LaTeX source in slides.pptx: {rep['error']}"),
         "stage": "render"}]
    n, overflows = render_pptx(deck, fr, sources, c, d / "slides.pptx", pictures)
    (d / "notes.md").write_text(render_markdown(deck, fr, sources), encoding="utf-8")
    write_json(d / "quiz.json", [{"slide": i, "los": s.los, **s.quiz.model_dump()} for i, s in enumerate(deck.slides, FIRST_CONTENT_SLIDE) if s.quiz])
    (d / "student.html").write_text(student_page(deck, fr, sources, c_quiz(d), values), encoding="utf-8")
    over = [{**v("D-OVERFLOW", WARN, [f"slide {o['slide']}"], f"slide {o['slide']}: the {o['what']} text may not fit its "
                                                                "box; shorten it in PowerPoint"), "stage": "render"} for o in overflows]
    keep = [x for x in found if not (x["code"] in RENDER_CODES and x.get("stage") == "render")]   # content-stage D-MATH stays
    return n, keep + rendered + over


# ------------------------------------------------------------------ generation
def _ask(llm, ctx: dict, run_id: str, log) -> tuple[LectureDeck, dict]:
    p = load_prompt(PID)
    system, user = p.render(**ctx)
    deck, rec = llm.structured(system=system, user=user, model_cls=LectureDeck, role=p.meta.get("model_class", "generate"),
                               temperature=float(p.meta.get("temperature", 0.3)), prompt_id=PID, prompt_version=p.version,
                               run_id=run_id)
    log(f"  [{PID}] ok via {rec.endpoint} · {rec.prompt_tokens}+{rec.output_tokens} tok · {rec.latency_s:.1f}s")
    return deck, {"endpoint": rec.endpoint, "prompt_tokens": rec.prompt_tokens, "output_tokens": rec.output_tokens}


def _ai_review(llm, deck, found, code, ctx, lecture, calls, author, check, run_id, log, prep=None):
    """B2 on the checked deck by any model but its `author` (the endpoint of the B1 call that wrote the kept deck; a
    rejected repair by another model does not bar that model), then one B1 repair when the reviewer reports errors
    (kept unless the code checks find more errors than before). A failed review leaves the deck as it was, recorded in
    ai_review.error."""
    try:
        ai_found, ai = review_deck(llm, deck, ctx["course"], lecture, {model_of(author)}, run_id, log)
    except Exception as e:                          # no reviewer model or quota left: keep the draft, say so
        log(f"  [B2] review failed: {e}")
        return deck, found, code, {"error": str(e)[:300]}
    calls.append({k: ai[k] for k in ("endpoint", "prompt_tokens", "output_tokens")})
    ai["repaired"] = False
    if errors(ai_found):
        ctx["problems"] = ([{"code": x["code"], "where": x["nodes"], "problem": x["message"]} for x in errors(ai_found + found)]
                           + [p for p in ctx["problems"] if p["code"] == "PROFESSOR"])
        deck2, call = _ask(llm, ctx, run_id, log)
        calls.append(call)
        deck2 = prep(deck2) if prep else fill_from_outline(deck2, lecture.get("outline") or [])
        found2, code2 = check(deck2)
        keep = len(errors(found2)) <= len(errors(found))
        log(f"  [{PID} after review] code-check errors {len(errors(found))} → {len(errors(found2))} {'ACCEPT' if keep else 'REJECT'}")
        if keep:
            deck, found, code, ai_found, ai["repaired"] = deck2, found2, code2, after_repair(ai_found), True
    return deck, found + ai_found, code, ai


def generate_material(run_id: str, lecture_id: str, options: dict | None = None, *, llm=None,
                      log: Callable[[str], None] = print) -> dict:
    """Slides and notes for one lecture. options: include_pending (bool); note (str: what the professor wants
    emphasised); feedback (str: the professor's redo instructions, given to B1 as a problem to fix); force (bool: replace
    an approved deck); review ("ai": a different model checks the deck, see content/ai_review.py); material ({text, parts}:
    the professor's own material, from content/attach.py: the deck is built from it and cites it as P1…); slides (int: the
    deck's total slide count, code's title and objectives slides, and references when there are sources, included; the AI
    writes the rest, exactly); depth ("basic" | "standard" | "high": how deep the content goes, config deck.depth by
    default; without `slides` it also sets the slide range, config deck.slides_per_hour_by_depth). Returns the manifest
    written to material.json."""
    o, c = options or {}, cfg()
    old = read_json(material_dir(run_id, lecture_id) / "material.json") or {}
    if old.get("status") == "approved" and not o.get("force"):
        raise ValueError(f"{lecture_id}: the professor approved these slides; pass force to replace them")
    st = load_state(run_id)
    brief = units(st, c).get(lecture_id)
    if brief is None:
        raise KeyError(f"no lecture {lecture_id} in runs/{run_id}")
    d = material_dir(run_id, lecture_id)
    llm = llm or LLMClient(out_dir(run_id) / "material" / "llm_calls.jsonl")
    lecture = lecture_input(brief, o.get("note", ""), run_id)
    sources = gather_sources(st, run_id, brief, o.get("include_pending", c["sources"]["include_pending"]), c["sources"]["max_external"])
    prof = load_style(run_id)                      # the professor's own look and writing (content/style.py), if learned
    if for_b1(prof):
        lecture["style"] = for_b1(prof)
    c_render = apply_look(c, prof)
    mat = o.get("material")                        # the professor's own material (content/attach.py, task "slides")
    if mat:
        lecture["professor_material"] = mat["text"]
        sources.update({p["id"]: {"title": f"Professor's material: {p['name']}", "year": None, "url": None,
                                  "kind": "professor material", "approved": True} for p in mat["parts"]})
    lecture["depth"] = o.get("depth") or c["deck"].get("depth", "standard")
    if o.get("slides"):                            # the professor's total; code adds title, objectives (and references)
        lecture["content_slides"] = max(3, int(o["slides"]) - frame_slides(sources))
    lo_min, lo_max = slide_range(lecture, c)
    ctx = {"course": {"course_name": st["cco_compact"]["course_name"], "level": st.get("level")}, "lecture": lecture,
           "sources": [{"id": k, **{f: s[f] for f in ("kind", "title", "year", "url")}} for k, s in sources.items()],
           "slides": {"min": lo_min, "max": lo_max},
           "problems": [{"code": "PROFESSOR", "where": [], "problem": o["feedback"]}] if o.get("feedback") else []}

    fr = frame(st, brief)
    d.mkdir(parents=True, exist_ok=True)
    log(f"B lecture material {run_id} {lecture_id}: {brief['topic']} ({brief['hours']:g} h, {len(sources)} sources)")

    calls, example_note = [], ""                   # B6: the running example, its numbers computed by code
    ex = None
    if (c.get("example") or {}).get("enabled", True):
        ex, ex_calls, example_note = make_example(llm, {"course": ctx["course"], "lecture": lecture}, c, run_id, log)
        calls += ex_calls
    if ex:
        write_json(d / "example.json", ex)
        lecture["example"] = example_for_b1(ex)
    elif (d / "example.json").exists():
        (d / "example.json").unlink()                # an older example would no longer match the deck
    values = (ex or {}).get("values") or {}
    outline_parts = lecture.get("outline") or []

    def prep(dk: LectureDeck) -> LectureDeck:
        """What code adds to B1's deck: clips and links from the outline, the example's numbers for [[name]]."""
        return fill_values(fill_from_outline(dk, outline_parts), values)[0]

    def check(dk: LectureDeck) -> tuple[list[dict], list[dict]]:
        more, code = verify(dk, sources, c)
        return (check_deck(dk, lecture, set(sources), c, values) + more
                + browser_check(d, dk, fr, sources, c_render, values)), code

    mode, plan, plan_left = c["deck"].get("mode", "per_slide"), None, []
    if mode == "per_slide":                            # B7 plan, checked; B8 one slide per call (content/plan.py)
        try:
            plan, pcalls, plan_left = make_plan(llm, ctx, c, values if ex else None, run_id, log)
            calls += pcalls
        except Exception as e:  # noqa: BLE001  (no usable plan: write the deck in one call instead)
            log(f"  [B7] plan failed ({type(e).__name__}: {str(e)[:160]}); writing the deck in one call (B1)")
    if plan is not None:
        write_json(d / "plan.json", plan.model_dump())
        deck, wcalls = write_deck(llm, ctx, plan, lecture_id, run_id, log)
        calls += wcalls
        author = wcalls[-1]["endpoint"]
        deck = prep(deck)
        found, code = check(deck)
        log(f"  [B8] checks: {len(errors(found))} errors, {len(found) - len(errors(found))} warnings")
        deck, found, code, rcalls = repair_slides(llm, ctx, plan, deck, found, code, check, prep,
                                                  int(c["deck"].get("slide_repair_rounds", 2)), run_id, log)
        calls += rcalls
    else:
        deck, call = _ask(llm, ctx, run_id, log)
        calls.append(call)
        author = call["endpoint"]                      # author: who wrote the deck that is kept
        deck = prep(deck)
        found, code = check(deck)
        log(f"  [{PID}] checks: {len(errors(found))} errors, {len(found) - len(errors(found))} warnings")
    for rnd in range(1, (c["deck"]["repair_rounds"] if plan is None else 0) + 1):
        if not errors(found):
            break
        ctx["problems"] = [{"code": x["code"], "where": x["nodes"], "problem": x["message"]} for x in found
                           if x["severity"] == "error"] + [p for p in ctx["problems"] if p["code"] == "PROFESSOR"]
        deck2, call = _ask(llm, ctx, run_id, log)
        calls.append(call)
        deck2 = prep(deck2)
        found2, code2 = check(deck2)
        keep = len(errors(found2)) < len(errors(found))
        log(f"  [{PID} repair {rnd}] errors {len(errors(found))} → {len(errors(found2))} {'ACCEPT' if keep else 'REJECT'}")
        if keep:
            deck, found, code, author = deck2, found2, code2, call["endpoint"]

    ai = None
    if o.get("review") == "ai" and plan is not None:   # the reviewer's errors are repaired on their own slides
        try:
            ai_found, ai = review_deck(llm, deck, ctx["course"], lecture, {model_of(author)}, run_id, log)
            calls.append({k: ai[k] for k in ("endpoint", "prompt_tokens", "output_tokens")})
            ai["repaired"] = False
            if errors(ai_found):
                deck2, found2, code2, rc = repair_slides(llm, ctx, plan, deck, found + ai_found, code, check, prep, 1, run_id, log)
                calls += rc
                if deck2 is not deck:
                    deck, found, code, ai_found, ai["repaired"] = deck2, found2, code2, after_repair(ai_found), True
            found = [x for x in found if x.get("stage") != "ai-review"] + ai_found
        except Exception as e:  # noqa: BLE001  (no reviewer model or quota left: keep the draft, say so)
            log(f"  [B2] review failed: {e}")
            ai = {"error": str(e)[:300]}
    elif o.get("review") == "ai":
        deck, found, code, ai = _ai_review(llm, deck, found, code, ctx, lecture, calls, author, check, run_id, log, prep)
    if plan_left:
        found = found + [{**x, "severity": WARN, "message": "plan: " + x["message"]} for x in plan_left]

    if example_note and not example_note.startswith("B6: no numeric"):
        found = found + [{**v("D-EXAMPLE", WARN, [], f"no running example: {example_note}; the slides' numbers are the "
                                                      "AI's own, not computed"), "stage": "content"}]
    deck.lecture_id = lecture_id
    n, found = write_outputs(d, deck, fr, sources, c_render, found)
    prompts = (f"B7 {load_prompt('B7').version} + B8 {load_prompt('B8').version}" if plan is not None
               else f"{PID} {load_prompt(PID).version}")
    manifest = {"lecture_id": lecture_id, "topic": brief["topic"], "generated_at": now(), "prompt": prompts,
                "depth": lecture["depth"], **({"slides_asked": int(o["slides"])} if o.get("slides") else {}),
                "mode": "per_slide" if plan is not None else "deck",
                "files": {"slides": str((d / "slides.pptx").relative_to(out_dir(run_id))),
                          "notes": str((d / "notes.md").relative_to(out_dir(run_id))),
                          "deck": str((d / "deck.json").relative_to(out_dir(run_id))),
                          "quiz": str((d / "quiz.json").relative_to(out_dir(run_id))),
                          "student": str((d / "student.html").relative_to(out_dir(run_id))),
                          "slides_html": str((d / "slides.html").relative_to(out_dir(run_id))),
                          **({"slides_pdf": str((d / "slides.pdf").relative_to(out_dir(run_id)))} if (d / "slides.pdf").exists() else {}),
                          **({"example": str((d / "example.json").relative_to(out_dir(run_id)))} if ex else {})},
                "example": {"title": ex["title"], "values": len(values)} if ex else None,
                "slides": n, "content_slides": len(deck.slides), "minutes": sum(s.minutes for s in deck.slides),
                "errors": len(errors(found)), "warnings": len(found) - len(errors(found)), "findings": found,
                "code_checks": code, "sources": sources, "cited": sorted({s for sl in deck.slides for s in sl.sources}),
                "calls": calls, "ai_review": ai, "status": "ai-reviewed" if ai and not ai.get("error") else "draft",
                "review_history": old.get("review_history", []),
                "feedback": o.get("feedback") or None}
    write_json(d / "material.json", manifest)
    log(f"  slides: {n} ({len(deck.slides)} content) · {manifest['errors']} errors, {manifest['warnings']} warnings → {d}")
    return manifest
