"""Delivery mode 2: find, cut and check YouTube clips that teach whole lectures.

    python scripts/run_ytlecture.py --run-id cs601-02 --lectures W01.L1,W01.L2,W02.L1
    python scripts/run_ytlecture.py --run-id cs601-02 --first 6
    python scripts/run_ytlecture.py --run-id cs601-02 --first 6 --refresh      # redo every stage (cached web/AI answers are reused)
    python scripts/run_ytlecture.py --run-id cs601-02 --serve                   # open the player for the run's playlists

Outputs: runs/<run-id>/delivery/ytlecture/ (PLAYLISTS.md, TRACE.md, player.html, playlists.json, lectures/*.json).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--lectures", help="comma-separated lecture ids, e.g. W01.L1,W01.L2")
    ap.add_argument("--first", type=int, help="the first N lectures of the timetable")
    ap.add_argument("--refresh", action="store_true", help="ignore the checkpoints of earlier runs")
    ap.add_argument("--redo-lectures", action="store_true", help="keep each topic's plan, scout and search; redo triage onwards")
    ap.add_argument("--redo-search", action="store_true", help="keep each topic's plan and scout; redo the search and the lectures")
    ap.add_argument("--reassemble", action="store_true", help="recompute playlists from stored clips (no AI, no search)")
    ap.add_argument("--serve", action="store_true", help="serve the player on http://127.0.0.1:8124/player.html")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    from profsagent.delivery.common import out_dir
    d = out_dir(a.run_id) / "ytlecture"
    if a.serve:
        import functools
        import http.server
        h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(d))
        print(f"player: http://127.0.0.1:8124/player.html  (Ctrl+C to stop)")
        http.server.ThreadingHTTPServer(("127.0.0.1", 8124), h).serve_forever()
        return
    from profsagent.delivery.brief import build_briefs
    from profsagent.delivery.common import load_state, read_json
    from profsagent.ytlecture import run
    lectures = a.lectures.split(",") if a.lectures else None
    if a.first:
        briefs = read_json(out_dir(a.run_id) / "briefs.json") or build_briefs(load_state(a.run_id))
        lectures = [b["lecture_id"] for b in briefs][: a.first]
    t0 = time.time()
    if not (a.reassemble or a.serve):
        # every 15 min, write where each thread is: a stalled run then shows exactly which call it waits on
        import faulthandler
        d.mkdir(parents=True, exist_ok=True)
        stacks = open(d / "stacks.txt", "w", encoding="utf-8")
        faulthandler.dump_traceback_later(900, repeat=True, file=stacks)

    def log(msg):
        print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)
    if a.reassemble:
        from profsagent.ytlecture.orchestrator import Orchestrator
        res = Orchestrator(a.run_id, log=log).reassemble(lectures)
    else:
        res = run(a.run_id, lectures, refresh=a.refresh, log=log, redo_lectures=a.redo_lectures or a.redo_search,
                  redo_search=a.redo_search)
    print()
    for lid, x in res["lectures"].items():
        print(f"{lid}: {x['status']:18} video {x['video_min']:3} of {x['slot_min']} min   gaps: {', '.join(x['gaps']) or 'none'}")
    print(f"\n{res['dir']}  ({round((time.time() - t0) / 60, 1)} min)")


if __name__ == "__main__":
    main()
