"""Phase 2 · Deliverable B — lecture slides and notes for an approved Phase 1 course run.

  python scripts/run_content.py plan     --run-id cs601-02 --lectures W01.L1          # inputs and cost, no AI calls
  python scripts/run_content.py generate --run-id cs601-02 --lectures W01.L1 [--include-pending] [--note "..."]
  python scripts/run_content.py generate --run-id cs601-02 --from-survey              # every lecture with generate_material: yes
  python scripts/run_content.py check    --run-id cs601-02 --lectures W01.L1          # re-check and re-render a saved deck

Outputs: runs/<id>/delivery/material/<lecture>/ (slides.pptx, notes.md, deck.json, material.json).
One B1 call per lecture, plus at most `deck.repair_rounds` when the deck has errors (config/content.yaml).
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
from profsagent.content.checks import check_deck, content_range  # noqa: E402
from profsagent.content.models import LectureDeck  # noqa: E402
from profsagent.delivery import survey as sv  # noqa: E402
from profsagent.delivery.brief import build_briefs  # noqa: E402
from profsagent.delivery.common import load_state, read_json, write_json  # noqa: E402
from profsagent.validate.record import errors  # noqa: E402


def lectures(a, briefs: dict) -> list[str]:
    if a.from_survey:
        return [lid for lid, t in sv.tasks(sv.load(a.run_id) or {}).items() if "generate_material" in t["choices"]]
    ids = [x.strip() for x in (a.lectures or "").split(",") if x.strip()]
    unknown = [x for x in ids if x not in briefs]
    if unknown:
        sys.exit(f"unknown lectures {unknown}; this run has {list(briefs)[:5]} …")
    return ids


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["plan", "generate", "check"])
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--lectures", help="comma-separated lecture ids, e.g. W01.L1,W02.L1")
    ap.add_argument("--from-survey", action="store_true", help="the lectures whose survey answer asks for generated material")
    ap.add_argument("--include-pending", action="store_true", help="also cite C's resources the professor has not approved yet")
    ap.add_argument("--note", default="", help="what the professor wants emphasised")
    a = ap.parse_args()
    st = load_state(a.run_id)
    briefs = {b["lecture_id"]: b for b in build_briefs(st)}
    ids = lectures(a, briefs)
    if not ids:
        sys.exit("no lectures chosen: give --lectures or answer generate_material in the survey")
    c = G.cfg()
    pending = a.include_pending or c["sources"]["include_pending"]

    if a.cmd == "plan":
        for lid in ids:
            b = briefs[lid]
            src = G.gather_sources(st, a.run_id, b, pending, c["sources"]["max_external"])
            lo, hi = content_range(b["hours"], c)
            print(f"{lid}  {b['topic']}  ({b['hours']:g} h, {len(b['learning_outcomes'])} LOs)  content slides {lo}–{hi}  "
                  f"sources {list(src)}")
        print(f"AI calls: {len(ids)} (up to {len(ids) * (1 + c['deck']['repair_rounds'])} with repairs)")
    elif a.cmd == "generate":
        for lid in ids:
            m = G.generate_material(a.run_id, lid, {"include_pending": pending, "note": a.note})
            print(json.dumps({k: m[k] for k in ("lecture_id", "slides", "errors", "warnings", "cited", "files")}, ensure_ascii=False))
    else:
        for lid in ids:
            d = G.material_dir(a.run_id, lid)
            man = read_json(d / "material.json")
            if not man:
                sys.exit(f"no generated material for {lid}; run generate first")
            deck, b = LectureDeck.model_validate(read_json(d / "deck.json")), briefs[lid]
            found = check_deck(deck, G.lecture_input(b), set(man["sources"]), c)
            man["slides"], found = G.write_outputs(d, deck, G.frame(st, b), man["sources"], c, found)
            man.update(findings=found, errors=len(errors(found)), warnings=len(found) - len(errors(found)))
            write_json(d / "material.json", man)
            print(f"{lid}: {man['errors']} errors, {man['warnings']} warnings, {man['slides']} slides (re-rendered)")
            for x in found:
                print(f"  {x['severity']:7} {x['code']:10} {x['message']}")


if __name__ == "__main__":
    main()
