"""Deliverable B, deck mode "per_slide": plan the deck (B7), check the plan in code, then write each slide in its own
call (B8) and repair only the slides the checks fault.

    make_plan(llm, ctx, cfg, values, run_id, log) -> (plan | None, calls, open problems)
    plan_problems(plan, lecture, cfg, values) -> findings          D-PLAN: what the plan misses, before any slide exists
    write_deck(llm, ctx, plan, lecture_id, run_id, log) -> (deck, calls)
    repair_slides(llm, ctx, plan, deck, found, check, prep, rounds, run_id, log) -> (deck, found, code, calls)

Why: one call that writes a whole deck has to decide the structure and write 15-20 slides at once, so each slide gets
little of the model's attention, it drops what it set up (an opening question never answered), and a repair rewrites
everything (a repair once went from 1 error to 5). Instructional Agents gets its depth from one call per slide; here the
slides are also written from a plan that code has checked, with what the earlier slides said, and a fault is repaired
on its own slide only.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Callable

from profsagent.content.checks import slide_range
from profsagent.content.models import FIRST_CONTENT_SLIDE, LIMIT_ROLES, DeckPlan, LectureDeck, Slide
from profsagent.llm.prompts import load_prompt
from profsagent.validate.record import ERR, errors, v

NODE = re.compile(r"^slide (\d+)$")


def _call(llm, pid: str, ctx: dict, model_cls, run_id: str):
    p = load_prompt(pid)
    system, user = p.render(**ctx)
    obj, rec = llm.structured(system=system, user=user, model_cls=model_cls, role=p.meta.get("model_class", "generate"),
                              temperature=float(p.meta.get("temperature", 0.3)), prompt_id=pid, prompt_version=p.version,
                              run_id=run_id)
    return obj, {"prompt": pid, "endpoint": rec.endpoint, "prompt_tokens": rec.prompt_tokens,
                 "output_tokens": rec.output_tokens, "latency_s": getattr(rec, "latency_s", None)}


# ------------------------------------------------------------------ B7: the plan
def plan_problems(plan: DeckPlan, lecture: dict, cfg: dict, values: dict | None) -> list[dict]:
    """What the plan misses, as D-PLAN errors the planner is asked to fix."""
    out, slides = [], plan.slides
    err = lambda where, msg: out.append(v("D-PLAN", ERR, [where], msg))  # noqa: E731
    lo_min, lo_max = slide_range(lecture, cfg)
    if not lo_min <= len(slides) <= lo_max:
        err("plan", f"{len(slides)} content slides planned; the lecture needs "
                    + (f"exactly {lo_min} (the professor's slide count)" if lo_min == lo_max else f"{lo_min}-{lo_max}"))
    los = {lo["id"]: lo for lo in lecture["learning_outcomes"]}
    for lo_id, lo in los.items():
        mine = [s for s in slides if lo_id in s.los]
        if not mine:
            err(lo_id, f"{lo_id} ('{lo['statement'][:80]}') is taught by no slide")
        elif int(lo.get("bloom_level") or 0) >= 3 and not any(
                s.role == "worked_example" or s.kind in ("example", "worked_problem", "activity") for s in mine):
            err(lo_id, f"{lo_id} (Bloom {lo['bloom_level']}) has no worked_example slide that uses the skill step by step")
    for k, s in enumerate(slides, FIRST_CONTENT_SLIDE):
        bad = sorted(set(s.los) - set(los))
        if bad:
            err(f"plan slide {k}", f"plan slide {k} names unknown outcomes {bad}")
        if values is not None and values:
            miss = [n for n in s.values if n not in values]
            if miss:
                err(f"plan slide {k}", f"plan slide {k} names values the example does not have: {miss[:6]}")
    checks, wanted = sum(s.kind == "check" for s in slides), max(1, round(lecture["hours"]))
    if checks < wanted:
        err("plan", f"{checks} check slides for a {lecture['hours']:g}-hour lecture; plan at least {wanted}")
    tail = [s.kind for s in slides[-2:]]
    if slides and "summary" not in tail:
        err("plan", "the deck does not end with a summary slide")
    first = next((s for s in slides if s.kind != "recap"), None)
    if first is not None and first.role != "opening":
        err(f"plan slide {FIRST_CONTENT_SLIDE + slides.index(first)}", "the first content slide must be the opening: a "
                                                                      "concrete question, not a definition")
    if values is not None and not any(s.answers_opening for s in slides):   # any running example, numeric or a case
        err("plan", f"no slide answers the opening question ('{plan.opening_question[:80]}')")
    roles = [s.role for s in slides]
    k = 0
    while k < len(roles):                                   # each run of derivation slides needs a worked example
        if roles[k] == "derivation":
            j = k
            while j + 1 < len(roles) and roles[j + 1] == "derivation":
                j += 1
            if values and "worked_example" not in roles[j + 1:j + 3]:
                err(f"plan slide {FIRST_CONTENT_SLIDE + j}", f"the derivation ending on plan slide {FIRST_CONTENT_SLIDE + j} "
                                                            "is not followed by a worked_example on the running example")
            k = j + 1
        else:
            k += 1
    if (lecture.get("depth") or "standard") != "basic" and not any(s.role in LIMIT_ROLES for s in slides):
        err("plan", "no limits or misconception slide: where the method breaks, what it assumes, or the mistake "
                    "students most often make")
    parts = {p["id"] for p in lecture.get("outline") or []}
    for k, s in enumerate(slides, FIRST_CONTENT_SLIDE):
        if parts and s.component and s.component not in parts:
            err(f"plan slide {k}", f"plan slide {k} names part {s.component}, which is not in the outline")
    for x in out:
        x["stage"] = "plan"
    return out


def make_plan(llm, ctx: dict, cfg: dict, values: dict | None, run_id: str, log) -> tuple[DeckPlan | None, list[dict], list[dict]]:
    """B7, checked; one more B7 call with the problems when the plan has any (kept only if it has fewer)."""
    calls, rounds = [], int((cfg.get("deck") or {}).get("plan_repair_rounds", 1))
    c = {**ctx, "problems": []}
    plan, call = _call(llm, "B7", c, DeckPlan, run_id)
    calls.append(call)
    probs = plan_problems(plan, ctx["lecture"], cfg, values)
    log(f"  [B7] plan: {len(plan.slides)} slides, {len(probs)} problems")
    for _ in range(rounds):
        if not probs:
            break
        c["problems"] = [{"code": x["code"], "where": x["nodes"], "problem": x["message"]} for x in probs]
        plan2, call = _call(llm, "B7", c, DeckPlan, run_id)
        calls.append(call)
        probs2 = plan_problems(plan2, ctx["lecture"], cfg, values)
        keep = len(probs2) < len(probs)
        log(f"  [B7 repair] problems {len(probs)} → {len(probs2)} {'ACCEPT' if keep else 'REJECT'}")
        if keep:
            plan, probs = plan2, probs2
    return plan, calls, probs


# ------------------------------------------------------------------ B8: one slide per call
def plan_view(plan: DeckPlan) -> dict:
    return {"title": plan.title, "opening_question": plan.opening_question,
            "slides": [{"n": k, "kind": s.kind, "title": s.title, "role": s.role, "teaches": s.teaches}
                       for k, s in enumerate(plan.slides, FIRST_CONTENT_SLIDE)]}


def recap(s: Slide, n: int) -> dict:
    """What a written slide said, for the slides after it."""
    formulas = [st.latex for b in s.blocks for st in b.steps][-2:] + [b.latex for b in s.blocks if b.kind == "math"]
    defs = [b.term for b in s.blocks if b.kind == "definition"]
    return {"n": n, "title": s.title, "bullets": s.bullets, **({"defines": defs} if defs else {}),
            **({"formulas": formulas[:3]} if formulas else {})}


def enforce(s: Slide, entry, n: int) -> Slide:
    """The plan decides a slide's kind, title, outcomes, minutes and part; the writer decides its content."""
    s.kind, s.title, s.component = entry.kind, entry.title or s.title, entry.component or s.component
    s.los = sorted(set(entry.los) | set(s.los)) if entry.los else s.los
    s.minutes = entry.minutes or s.minutes
    return s


def write_slide(llm, ctx: dict, plan: DeckPlan, k: int, before: list[dict], run_id: str,
                problems: list[dict] | None = None, previous: Slide | None = None) -> tuple[Slide, dict]:
    n = FIRST_CONTENT_SLIDE + k
    entry = plan.slides[k]
    c = {**ctx, "plan": plan_view(plan), "slide": {"n": n, **entry.model_dump()}, "before": before,
         "problems": problems or [], "previous": previous.model_dump(exclude_defaults=True) if previous else {}}
    s, call = _call(llm, "B8", c, Slide, run_id)
    return enforce(s, entry, n), call


def slide_ctx(ctx: dict) -> dict:
    """B8's context: the brief without the professor's material (the plan carries what each slide takes from it)."""
    return {**ctx, "lecture": {k: x for k, x in ctx["lecture"].items() if k != "professor_material"}}


def write_deck(llm, ctx: dict, plan: DeckPlan, lecture_id: str, run_id: str, log) -> tuple[LectureDeck, list[dict]]:
    sc, slides, calls = slide_ctx(ctx), [], []
    for k in range(len(plan.slides)):
        before = [recap(s, FIRST_CONTENT_SLIDE + i) for i, s in enumerate(slides)]
        s, call = write_slide(llm, sc, plan, k, before, run_id)
        calls.append(call)
        slides.append(s)
        log(f"  [B8] slide {FIRST_CONTENT_SLIDE + k}/{FIRST_CONTENT_SLIDE + len(plan.slides) - 1} '{s.title}' "
            f"via {call['endpoint']} · {call['output_tokens']} tok")
    return LectureDeck(lecture_id=lecture_id, title=plan.title, slides=slides), calls


# ------------------------------------------------------------------ repair, one slide at a time
def per_slide(found: list[dict], n_slides: int) -> dict[int, list[dict]]:
    """Error findings by content-slide index (findings on the deck as a whole are left out)."""
    out: dict[int, list[dict]] = {}
    for x in errors(found):
        for node in x.get("nodes") or []:
            m = NODE.match(str(node))
            if m and 0 <= int(m.group(1)) - FIRST_CONTENT_SLIDE < n_slides:
                out.setdefault(int(m.group(1)) - FIRST_CONTENT_SLIDE, []).append(x)
    return out


def repair_slides(llm, ctx: dict, plan: DeckPlan, deck: LectureDeck, found: list[dict], code: list[dict],
                  check: Callable, prep: Callable, rounds: int, run_id: str, log) -> tuple[LectureDeck, list[dict], list[dict], list[dict]]:
    """Rewrite each slide that has errors (B8 with its problems and previous version); keep a rewrite only when its own
    slide has fewer errors afterwards. Up to `rounds` rounds."""
    sc, calls = slide_ctx(ctx), []
    for rnd in range(1, rounds + 1):
        bad = per_slide(found, len(deck.slides))
        if not bad:
            break
        new = deck.model_copy(deep=True)
        for k, probs in sorted(bad.items()):
            before = [recap(s, FIRST_CONTENT_SLIDE + i) for i, s in enumerate(new.slides[:k])]
            pr = [{"code": x["code"], "problem": x["message"]} for x in probs]
            s, call = write_slide(llm, sc, plan, k, before, run_id, pr, deck.slides[k])
            calls.append(call)
            new.slides[k] = s
        new = prep(new)
        found2, code2 = check(new)
        old_n, new_n = Counter({k: len(v_) for k, v_ in bad.items()}), Counter({k: len(v_) for k, v_ in per_slide(found2, len(new.slides)).items()})
        worse = [k for k in bad if new_n[k] >= old_n[k]]
        for k in worse:                                       # a rewrite that did not help: keep the earlier slide
            new.slides[k] = deck.slides[k]
        if worse and len(worse) < len(bad):
            found2, code2 = check(new)
        kept = len(bad) - len(worse)
        log(f"  [B8 repair {rnd}] {len(bad)} slides rewritten, {kept} kept; errors {len(errors(found))} → "
            f"{len(errors(found2)) if kept else len(errors(found))}")
        if kept:
            deck, found, code = new, found2, code2
        else:
            break
    return deck, found, code, calls
