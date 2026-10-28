"""Phase 2 deliverable B: generate one lecture's slides and notes from its brief (the survey's `generate_material`).

    generate_material(run_id, lecture_id, options) -> manifest

Flow, one lecture at a time:
  1. inputs   the lecture brief (delivery/brief.py), the course's verified Phase 1 resources and C's resources for the
              lecture (approved only, unless options.include_pending), each given a short id the slides can cite
  2. B1       one AI call writes the content slides (content/models.LectureDeck)
  3. checks   content/checks.py; with errors, B1 is asked again with the findings (kept only if errors drop)
  4. frame    code writes the title, objectives and references slides from the brief and the cited sources
  5. render   slides.pptx (with speaker notes) and notes.md
Output: runs/<id>/delivery/material/<lecture_id>/{deck.json, slides.pptx, notes.md, quiz.json, material.json}.
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from profsagent.config import load_yaml
from profsagent.content.checks import check_deck, content_range
from profsagent.content.models import LectureDeck
from profsagent.content.render import render_markdown, render_pptx
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


# ------------------------------------------------------------------ inputs
def lecture_input(brief: dict, note: str = "") -> dict:
    """The brief as B1 sees it: statements cleaned of template holes, the time in minutes."""
    return {"lecture_id": brief["lecture_id"], "topic": brief["topic"], "module": brief["module"], "hours": brief["hours"],
            "minutes": round(brief["hours"] * 60),
            "learning_outcomes": [{"id": lo["id"], "statement": clean(lo["statement"]), "bloom_level": lo["bloom_level"]}
                                  for lo in brief["learning_outcomes"]],
            "course_outcomes": [{"id": c["id"], "statement": clean(c["statement"])} for c in brief["course_outcomes"]],
            "builds_on": brief.get("builds_on") or [],
            "prerequisites": [{"course": p["course"], "relied_topics": p.get("relied_topics", [])} for p in brief.get("prerequisite_courses") or []],
            "leads_to": brief.get("leads_to") or [], "assessed_in": brief.get("assessed_in") or [],
            "hands_on": brief.get("hands_on", False), "labs": brief.get("labs") or [], "professor_note": note}


def gather_sources(st: dict, run_id: str, brief: dict, include_pending: bool, max_external: int) -> dict[str, dict]:
    """Short id -> source. C1.. the course's verified resources that support this lecture's topic (all of them when none
    does); L1.. C's resources for the lecture, approved (or, for testing, pending) items in rank order."""
    out: dict[str, dict] = {}
    course = st.get("resources") or []
    mine = [r for r in course if any(s.get("topic_id") == brief["topic_id"] for s in r.get("supports_topics") or [])] or course
    for i, r in enumerate(mine, 1):
        out[f"C{i}"] = {"title": r.get("title"), "year": r.get("year"), "url": _link(r.get("identifier")),
                        "kind": r.get("role") or "course resource", "approved": True}
    lec = read_json(out_dir(run_id) / "lectures" / f"{brief['lecture_id']}.json", {}) or {}
    items = (lec.get("resources") or {}).get("items") or {}
    picked = [it for kind in KINDS for it in items.get(kind) or []
              if it.get("status_decision") == "approve" or (include_pending and it.get("status_decision") in (None, "pending"))]
    for i, it in enumerate(picked[:max_external], 1):
        out[f"L{i}"] = {"title": it.get("title"), "year": it.get("year") or (it.get("published") or "")[:4] or None,
                        "url": it.get("url"), "kind": it.get("kind"), "approved": it.get("status_decision") == "approve"}
    return out


def _link(identifier: dict | None) -> str | None:
    """A Phase 1 resource identifier {isbn, doi, arxiv, url} as one link (or the ISBN as text)."""
    i = identifier or {}
    return (i.get("url") or (f"https://doi.org/{i['doi']}" if i.get("doi") else None)
            or (f"https://arxiv.org/abs/{i['arxiv']}" if i.get("arxiv") else None) or (f"ISBN {i['isbn']}" if i.get("isbn") else None))


def frame(st: dict, brief: dict) -> dict:
    """Text of the slides code writes itself."""
    course = st["cco_compact"]["course_name"]
    los = [f"{clean(lo['statement'])} ({lo['id']})" for lo in brief["learning_outcomes"]]
    return {"course": course, "footer": f"{course}  ·  {brief['lecture_id']}",
            "subtitle": f"Week {brief['week']} · {brief['module']} · {brief['hours']:g} h",
            "draft_note": "Draft generated by ProfsAgent from the course design: review and edit before teaching.",
            "objectives": los,
            "objectives_notes": "These are the lecture's learning outcomes from the approved course design. "
                                f"Assessed in: {', '.join(a['id'] for a in brief.get('assessed_in') or []) or 'not assessed directly'}."}


# ------------------------------------------------------------------ outputs
def write_outputs(d: Path, deck: LectureDeck, fr: dict, sources: dict, c: dict, found: list[dict]) -> tuple[int, list[dict]]:
    """deck.json, slides.pptx, notes.md and quiz.json; returns the slide count and the findings with the renderer's
    D-OVERFLOW warnings (replacing any from an earlier render)."""
    write_json(d / "deck.json", deck.model_dump())
    n, overflows = render_pptx(deck, fr, sources, c, d / "slides.pptx")
    (d / "notes.md").write_text(render_markdown(deck, fr, sources), encoding="utf-8")
    write_json(d / "quiz.json", [{"slide": i, "los": s.los, **s.quiz.model_dump()} for i, s in enumerate(deck.slides, 1) if s.quiz])
    over = [{**v("D-OVERFLOW", WARN, [f"slide {o['slide']}"], f"slide {o['slide']}: the {o['what']} text may not fit its "
                                                                "box; shorten it in PowerPoint"), "stage": "render"} for o in overflows]
    return n, [x for x in found if x["code"] != "D-OVERFLOW"] + over


# ------------------------------------------------------------------ generation
def _ask(llm, ctx: dict, run_id: str, log) -> tuple[LectureDeck, dict]:
    p = load_prompt(PID)
    system, user = p.render(**ctx)
    deck, rec = llm.structured(system=system, user=user, model_cls=LectureDeck, role=p.meta.get("model_class", "generate"),
                               temperature=float(p.meta.get("temperature", 0.3)), prompt_id=PID, prompt_version=p.version,
                               run_id=run_id)
    log(f"  [{PID}] ok via {rec.endpoint} · {rec.prompt_tokens}+{rec.output_tokens} tok · {rec.latency_s:.1f}s")
    return deck, {"endpoint": rec.endpoint, "prompt_tokens": rec.prompt_tokens, "output_tokens": rec.output_tokens}


def generate_material(run_id: str, lecture_id: str, options: dict | None = None, *, llm=None,
                      log: Callable[[str], None] = print) -> dict:
    """Slides and notes for one lecture. options: include_pending (bool), note (str: what the professor wants
    emphasised). Returns the manifest written to material.json."""
    o, c = options or {}, cfg()
    st = load_state(run_id)
    brief = next((b for b in build_briefs(st) if b["lecture_id"] == lecture_id), None)
    if brief is None:
        raise KeyError(f"no lecture {lecture_id} in runs/{run_id}")
    d = material_dir(run_id, lecture_id)
    llm = llm or LLMClient(out_dir(run_id) / "llm_calls.jsonl")
    lecture = lecture_input(brief, o.get("note", ""))
    sources = gather_sources(st, run_id, brief, o.get("include_pending", c["sources"]["include_pending"]), c["sources"]["max_external"])
    lo_min, lo_max = content_range(brief["hours"], c)
    ctx = {"course": {"course_name": st["cco_compact"]["course_name"], "level": st.get("level")}, "lecture": lecture,
           "sources": [{"id": k, **{f: s[f] for f in ("kind", "title", "year", "url")}} for k, s in sources.items()],
           "slides": {"min": lo_min, "max": lo_max}, "problems": []}

    log(f"B lecture material {run_id} {lecture_id}: {brief['topic']} ({brief['hours']:g} h, {len(sources)} sources)")
    deck, call = _ask(llm, ctx, run_id, log)
    calls = [call]
    found = check_deck(deck, lecture, set(sources), c)
    log(f"  [{PID}] checks: {len(errors(found))} errors, {len(found) - len(errors(found))} warnings")
    for rnd in range(1, c["deck"]["repair_rounds"] + 1):
        if not errors(found):
            break
        ctx["problems"] = [{"code": x["code"], "where": x["nodes"], "problem": x["message"]} for x in found]
        deck2, call = _ask(llm, ctx, run_id, log)
        calls.append(call)
        found2 = check_deck(deck2, lecture, set(sources), c)
        keep = len(errors(found2)) < len(errors(found))
        log(f"  [{PID} repair {rnd}] errors {len(errors(found))} → {len(errors(found2))} {'ACCEPT' if keep else 'REJECT'}")
        if keep:
            deck, found = deck2, found2

    deck.lecture_id = lecture_id
    n, found = write_outputs(d, deck, frame(st, brief), sources, c, found)
    manifest = {"lecture_id": lecture_id, "topic": brief["topic"], "generated_at": now(), "prompt": f"{PID} {load_prompt(PID).version}",
                "files": {"slides": str((d / "slides.pptx").relative_to(out_dir(run_id))),
                          "notes": str((d / "notes.md").relative_to(out_dir(run_id))),
                          "deck": str((d / "deck.json").relative_to(out_dir(run_id))),
                          "quiz": str((d / "quiz.json").relative_to(out_dir(run_id)))},
                "slides": n, "content_slides": len(deck.slides), "minutes": sum(s.minutes for s in deck.slides),
                "errors": len(errors(found)), "warnings": len(found) - len(errors(found)), "findings": found,
                "sources": sources, "cited": sorted({s for sl in deck.slides for s in sl.sources}), "calls": calls}
    write_json(d / "material.json", manifest)
    log(f"  slides: {n} ({len(deck.slides)} content) · {manifest['errors']} errors, {manifest['warnings']} warnings → {d}")
    return manifest
