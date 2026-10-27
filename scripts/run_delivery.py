"""Phase 2 · Deliverable C — learning resources and expert speakers for an approved Phase 1 course run.

  python scripts/run_delivery.py briefs    --run-id cs601-02               # lecture briefs (no AI)
  python scripts/run_delivery.py survey    --run-id cs601-02 --init        # write the per-lecture questions
  python scripts/run_delivery.py survey    --run-id cs601-02 --ask         # answer them in the terminal
  python scripts/run_delivery.py survey    --run-id cs601-02 --defaults    # test defaults for unanswered questions
  python scripts/run_delivery.py recommend --run-id cs601-02 [--lectures W02.L1,W03.L1] [--limit 3] [--refresh]
  python scripts/run_delivery.py review    --run-id cs601-02 --apply       # apply decisions from review.yaml
  python scripts/run_delivery.py feedback  --run-id cs601-02               # create / record feedback.yaml ratings
  python scripts/run_delivery.py health    --run-id cs601-02               # re-check approved links
  python scripts/run_delivery.py graph     --run-id cs601-02               # write delivery records to Neo4j
  python scripts/run_delivery.py all       --run-id cs601-02 --defaults --limit 3   # briefs → survey → recommend → graph

Outputs: runs/<id>/delivery/ (briefs.md, survey.yaml, report.md, review.yaml, guest_kits/, lectures/*.json).
Needs YOUTUBE_API_KEY and OPENALEX_API_KEY in .env; Gemini/Groq keys as in Phase 1.
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

from profsagent.delivery import pipeline, review  # noqa: E402
from profsagent.delivery import survey as sv  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["briefs", "survey", "recommend", "review", "feedback", "health", "graph", "all"])
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--ask", action="store_true")
    ap.add_argument("--defaults", action="store_true")
    ap.add_argument("--overwrite", action="store_true", help="survey --init: discard existing answers")
    ap.add_argument("--lectures", help="comma-separated lecture ids, e.g. W02.L1,W03.L2")
    ap.add_argument("--limit", type=int, help="at most this many lectures (useful for a first test)")
    ap.add_argument("--refresh", action="store_true", help="redo lectures that already have results")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--no-graph", action="store_true")
    a = ap.parse_args()
    lect = a.lectures.split(",") if a.lectures else None

    if a.cmd in ("briefs", "all"):
        b = pipeline.make_briefs(a.run_id)
        print(f"{len(b)} lecture briefs ({sum(x['novel'] for x in b)} new at IIIT-D) → runs/{a.run_id}/delivery/briefs.md")
    if a.cmd in ("survey", "all"):
        b = pipeline.make_briefs(a.run_id)
        if a.init or sv.load(a.run_id) is None:
            sv.init(a.run_id, b, overwrite=a.overwrite)
        if a.ask:
            sv.ask(a.run_id, b)
        if a.defaults:
            sv.apply_defaults(a.run_id, b)
        print(f"survey: {len(sv.requests(sv.load(a.run_id)))} lectures asked for help → runs/{a.run_id}/delivery/survey.yaml")
    if a.cmd in ("recommend", "all"):
        r = pipeline.recommend(a.run_id, lectures=lect, refresh=a.refresh, limit=a.limit)
        print(f"report: {r['report']} ({r['lectures']} lectures)")
    if a.cmd == "review":
        if a.apply:
            print(json.dumps(review.apply(a.run_id), indent=1))
        else:
            print(pipeline.render(a.run_id))
    if a.cmd == "feedback":
        print(json.dumps(review.record_feedback(a.run_id), indent=1))
    if a.cmd == "health":
        dead = review.health(a.run_id)
        print(f"{len(dead)} approved links are dead" + "".join(f"\n  {x['lecture']} {x['title'][:60]} ({x['status']})" for x in dead))
    if a.cmd == "graph" or (a.cmd == "all" and not a.no_graph):
        try:
            from profsagent.delivery.graph import write
            print("neo4j:", json.dumps(write(a.run_id)))
        except Exception as e:  # noqa: BLE001
            print(f"neo4j: skipped ({type(e).__name__}: {str(e)[:120]}); start Neo4j and run the graph command")


if __name__ == "__main__":
    main()
