"""Optional AI review of a lecture deck, for a professor who wants the system to check the slides itself (B2).

One call to a model other than the one that wrote the deck (the generator's models are excluded, as for the Stage 5
judges, so a model never grades its own output). The reviewer reads every content slide with its notes and reports
wrong facts, code that does the wrong thing, ambiguous quiz questions, unclear steps and level mismatches; it also
answers each quiz question without the answer key, and code compares its answers with the key.

    D-AI        error | warning   an issue the reviewer found (kind: fact, code, quiz, clarity, level, other)
    D-QUIZKEY   error             the reviewer chose a different option than the answer key: the key or the question
                                  is wrong or ambiguous
    D-AI-FIXED  warning           an error the reviewer found that the deck was rewritten to fix; the new slides were
                                  checked by the code checks again but not re-read by the reviewer

Errors go to one B1 repair (content/generate.py), kept only if the code checks find no more errors than before. An AI
review is a second opinion, not an approval: the deck's status becomes `ai-reviewed`, and only the professor can set
`approved` (content/review.py). Cost: 1 call, plus 1 B1 call when the reviewer finds errors.
"""
from __future__ import annotations

from typing import Callable

from profsagent.content.models import FIRST_CONTENT_SLIDE, DeckReview, LectureDeck
from profsagent.llm.prompts import load_prompt
from profsagent.validate.record import ERR, WARN, v

PID = "B2"


def model_of(endpoint: str) -> str:
    """'provider:model' of a call record's endpoint ('gemini:gemini-3.8-flash:k1a2b3c4' or 'cache(...)')."""
    e = endpoint[len("cache("):-1] if endpoint.startswith("cache(") else endpoint
    return ":".join(e.split(":")[:2])


def review_input(deck: LectureDeck) -> tuple[list[dict], list[dict]]:
    """(slides, questions) as the reviewer sees them: numbered as in the .pptx, quiz answer keys left out."""
    slides, questions = [], []
    for i, s in enumerate(deck.slides, FIRST_CONTENT_SLIDE):
        f = s.figure
        fig = {"kind": f.kind, "caption": f.caption, "steps": f.steps, "code": f.code, "language": f.language,
               "rows": f.rows} if f.kind != "none" else None
        slides.append({"slide": i, "kind": s.kind, "title": s.title, "bullets": s.bullets, "figure": fig, "notes": s.notes})
        if s.quiz:
            questions.append({"slide": i, "question": s.quiz.question, "options": s.quiz.options})
    return slides, questions


def findings(review: DeckReview, deck: LectureDeck) -> list[dict]:
    """The reviewer's answer as findings on this deck; slide numbers outside the deck are dropped."""
    by_no = dict(enumerate(deck.slides, FIRST_CONTENT_SLIDE))
    out = []
    for x in review.issues:
        s = by_no.get(x.slide)
        if s is None:
            continue
        msg = f"slide {x.slide} ('{s.title}'): [{x.kind}] {x.problem}" + (f" Fix: {x.fix}" if x.fix else "")
        out.append(v("D-AI", ERR if x.severity == "error" else WARN, [f"slide {x.slide}"], msg, kind=x.kind,
                     title=s.title))
    for a in review.quiz_answers:
        s = by_no.get(a.slide)
        if s is None or s.quiz is None or a.answer == s.quiz.answer:
            continue
        opt = s.quiz.options
        mine = opt[a.answer] if 0 <= a.answer < len(opt) else f"option {a.answer}"
        key = opt[s.quiz.answer] if 0 <= s.quiz.answer < len(opt) else f"option {s.quiz.answer}"
        out.append(v("D-QUIZKEY", ERR, [f"slide {a.slide}"],
                     f"slide {a.slide} ('{s.title}'): the reviewer answered '{mine}' but the key says '{key}' "
                     f"({a.why or 'no reason given'}): check the question and its key", title=s.title))
    for x in out:
        x["stage"] = "ai-review"
    return out


def after_repair(found: list[dict]) -> list[dict]:
    """The reviewer's findings once the deck was rewritten to fix its errors: each error becomes a D-AI-FIXED warning
    (what the professor should glance at), warnings are kept with a note that the slide may have moved."""
    out = []
    for x in found:
        if x["severity"] == "error":
            out.append({**v("D-AI-FIXED", WARN, x["nodes"], f"{x['message']} (rewritten to fix this; not re-read by the "
                                                             "reviewer)", title=x["evidence"].get("title")), "stage": "ai-review"})
        else:
            out.append({**x, "message": f"{x['message']} (found before the rewrite; the slide may have moved)"})
    return out


def review_deck(llm, deck: LectureDeck, course: dict, lecture: dict, avoid: set[str], run_id: str,
                log: Callable[[str], None] = print) -> tuple[list[dict], dict]:
    """(findings, record): one B2 call by a model not in `avoid` ("provider:model" of the deck's generator)."""
    p = load_prompt(PID)
    slides, questions = review_input(deck)
    system, user = p.render(course=course, slides=slides, questions=questions,
                            lecture={k: lecture[k] for k in ("lecture_id", "topic", "minutes", "learning_outcomes")})
    rv, rec = llm.structured(system=system, user=user, model_cls=DeckReview, role=p.meta.get("model_class", "review"),
                             temperature=float(p.meta.get("temperature", 0.1)), prompt_id=PID, prompt_version=p.version,
                             run_id=run_id, exclude_models=frozenset(avoid))
    found = findings(rv, deck)
    n_err = sum(x["severity"] == "error" for x in found)
    log(f"  [{PID}] review via {rec.endpoint} · {n_err} errors, {len(found) - n_err} warnings · {rv.verdict}")
    return found, {"endpoint": rec.endpoint, "model": model_of(rec.endpoint), "prompt_tokens": rec.prompt_tokens,
                   "output_tokens": rec.output_tokens, "verdict": rv.verdict, "questions": len(questions),
                   "quiz_disagreements": sum(x["code"] == "D-QUIZKEY" for x in found),
                   "issues": [x.model_dump() for x in rv.issues]}
