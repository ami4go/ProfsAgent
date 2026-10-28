"""Phase 2 · Deliverable B — lecture slides and notes for an approved Phase 1 course run.

  python scripts/run_content.py plan     --run-id cs601-02 --lectures W03.S1,W03.S2   # inputs and cost, no AI calls
Lecture ids: W03.S1 is week 3's first class (config/content.yaml `classes`: 2 x 90 min a week); W03.L1 is C's
per-topic lecture brief (its length is the topic's hours that week). Decks are normally made per class.
  python scripts/run_content.py generate --run-id cs601-02 --lectures W01.L1 [--include-pending] [--note "..."]
  python scripts/run_content.py generate --run-id cs601-02 --from-survey              # every lecture with generate_material: yes
  python scripts/run_content.py generate --run-id cs601-02 --redo                     # decks the professor sent back (review.yaml)
  python scripts/run_content.py generate --run-id cs601-02 --lectures W01.L2 --auto-review   # a different AI checks the deck
  python scripts/run_content.py check    --run-id cs601-02 --lectures W01.L1          # re-check and re-render a saved deck
  python scripts/run_content.py review   --run-id cs601-02 [--apply]                  # write review.yaml / apply decisions

Outputs: runs/<id>/delivery/material/<lecture>/ (slides.pptx, notes.md, quiz.json, deck.json, material.json) and
material/review.yaml. One B1 call per lecture, plus at most `deck.repair_rounds` when the deck has errors
(config/content.yaml); --auto-review adds one B2 call, and one more B1 call when the reviewer finds errors. check and
review make no AI calls. With several lectures, one that fails is reported at the end and the others still run.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(ROOT / "src"))

from profsagent.content import generate as G  # noqa: E402
from profsagent.content import review as R  # noqa: E402
from profsagent.content.checks import check_deck, content_range  # noqa: E402
from profsagent.content.models import LectureDeck  # noqa: E402
from profsagent.content.verify import verify  # noqa: E402
from profsagent.delivery import survey as sv  # noqa: E402
from profsagent.delivery.common import load_state, read_json, write_json  # noqa: E402
from profsagent.validate.record import errors  # noqa: E402


def lectures(a, briefs: dict) -> list[str]:
    if a.from_survey:
        return [lid for lid, t in sv.tasks(sv.load(a.run_id) or {}).items() if "generate_material" in t["choices"]]
    if a.redo:
        return list(R.redo_requests(a.run_id))
    ids = [x.strip() for x in (a.lectures or "").split(",") if x.strip()]
    unknown = [x for x in ids if x not in briefs]
    if unknown:
        sys.exit(f"unknown lectures {unknown}; this run has classes {list(briefs)[:3]} … and topic lectures {[k for k in briefs if '.L' in k][:3]} …")
    return ids


def show(lid: str, m: dict) -> None:
    print(f"{lid}: {m['errors']} errors, {m['warnings']} warnings, {m['slides']} slides, status {m.get('status', 'draft')}")
    ai = m.get("ai_review")
    if ai:
        print(f"  AI review: {ai.get('error') or (ai['model'] + ' · ' + ai['verdict'] + (' · repaired' if ai['repaired'] else ''))}")
    for x in m["findings"]:
        print(f"  {x['severity']:7} {x['code']:12} {x['message']}")
    for r in m.get("code_checks") or []:
        print(f"  code    slide {r['slide']:<3} {r['language'] or '?':10} {r['status']:9} {r['detail']}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "generate", "check", "review"])
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--lectures", help="comma-separated lecture ids, e.g. W01.L1,W02.L1")
    ap.add_argument("--from-survey", action="store_true", help="the lectures whose survey answer asks for generated material")
    ap.add_argument("--redo", action="store_true", help="the lectures the professor sent back with `redo` in review.yaml")
    ap.add_argument("--include-pending", action="store_true", help="also cite C's resources the professor has not approved yet")
    ap.add_argument("--note", default="", help="what the professor wants emphasised")
    ap.add_argument("--force", action="store_true", help="generate: replace a deck the professor approved")
    ap.add_argument("--auto-review", action="store_true", help="generate: a different AI model checks each deck (1-2 more calls)")
    ap.add_argument("--apply", action="store_true", help="review: apply the decisions in review.yaml")
    a = ap.parse_args()

    if a.cmd == "review":
        if a.apply:
            print(json.dumps(R.apply(a.run_id), ensure_ascii=False))
        rows = R.write(a.run_id)
        print(f"{len(rows)} generated lectures in runs/{a.run_id}/delivery/material/review.yaml")
        return

    st = load_state(a.run_id)
    briefs = G.units(st)                            # class sessions (W03.S1) and C's per-topic briefs (W03.L1)
    ids = lectures(a, briefs)
    if not ids:
        sys.exit("no lectures chosen: give --lectures, answer generate_material in the survey, or mark redo in review.yaml")
    c = G.cfg()
    pending = a.include_pending or c["sources"]["include_pending"]

    if a.cmd == "plan":
        for lid in ids:
            b = briefs[lid]
            src = G.gather_sources(st, a.run_id, b, pending, c["sources"]["max_external"])
            lo, hi = content_range(b["hours"], c)
            print(f"{lid}  {b['topic']}  ({round(b['hours'] * 60)} min, {len(b['learning_outcomes'])} LOs)  content slides {lo}–{hi}  "
                  f"sources {list(src)}")
        per = 1 + c["deck"]["repair_rounds"] + (2 if a.auto_review else 0)
        print(f"AI calls: {len(ids) * (2 if a.auto_review else 1)} (up to {len(ids) * per} with repairs)")
    elif a.cmd == "generate":
        feedback = R.redo_requests(a.run_id) if a.redo else {}
        failed = {}
        for n, lid in enumerate(ids, 1):
            print(f"\n=== {n}/{len(ids)} {lid}")
            try:
                m = G.generate_material(a.run_id, lid, {"include_pending": pending, "note": a.note, "force": a.force,
                                                        "feedback": feedback.get(lid),
                                                        "review": "ai" if a.auto_review else None})
            except Exception as e:                  # e.g. no model or quota left: the other lectures still run
                failed[lid] = f"{type(e).__name__}: {e}"[:300]
                print(f"{lid}: FAILED {failed[lid]}")
                continue
            show(lid, m)
        print(f"\n{len(ids) - len(failed)} of {len(ids)} lectures generated")
        if failed:
            print("failed (run them again with --lectures):", ",".join(failed))
            sys.exit(1)
    else:
        for lid in ids:
            d = G.material_dir(a.run_id, lid)
            man = read_json(d / "material.json")
            if not man:
                sys.exit(f"no generated material for {lid}; run generate first")
            deck, b = LectureDeck.model_validate(read_json(d / "deck.json")), briefs[lid]
            more, man["code_checks"] = verify(deck, man["sources"], c)
            # the code checks are redone; the AI review's findings are kept (re-reviewing would need a call)
            found = (check_deck(deck, G.lecture_input(b), set(man["sources"]), c) + more
                     + [x for x in man["findings"] if x.get("stage") == "ai-review"])
            man["slides"], found = G.write_outputs(d, deck, G.frame(st, b), man["sources"], c, found)
            man.update(findings=found, errors=len(errors(found)), warnings=len(found) - len(errors(found)))
            write_json(d / "material.json", man)
            show(lid, man)


if __name__ == "__main__":
    main()
