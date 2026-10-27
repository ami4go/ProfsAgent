"""One background delivery job in its own process (so the app can cancel it), over Vihan's deliverable C backend.

    python -m profsagent.app.delivery_step <run_id> recommend|health <args.json>

recommend: profsagent.delivery.pipeline.recommend(run_id, lectures, refresh), then graph.write (skipped if Neo4j is down)
health:    profsagent.delivery.review.health(run_id)
Result: runs/<id>/delivery/app_step_result.json = {"ok": ...} or {"error": {type, message, quota}}. C's log lines go to
stdout (the app's terminal) and to runs/<id>/delivery/delivery.log, which the lecture pages show.
"""
from __future__ import annotations

import json
import os
import sys
import traceback


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):
        s.reconfigure(encoding="utf-8", errors="replace")
    rid, kind, af = argv[1], argv[2], argv[3]
    import profsagent.config  # noqa: F401  (loads .env)
    from profsagent.delivery.common import out_dir
    if not os.environ.get("GROQ_API_KEYS") and os.environ.get("GROQ_API_KEY"):
        os.environ["GROQ_API_KEYS"] = os.environ["GROQ_API_KEY"]
    args = json.loads(open(af, encoding="utf-8").read())
    try:
        if kind == "recommend":
            from profsagent.delivery import pipeline
            out = {"ok": pipeline.recommend(rid, lectures=args.get("lectures"), refresh=bool(args.get("refresh")))}
            try:
                from profsagent.delivery.graph import write
                out["graph"] = write(rid)
            except Exception as e:  # noqa: BLE001 — the files are complete; Neo4j records can be written later
                out["graph"] = f"skipped ({type(e).__name__})"
        elif kind == "health":
            from profsagent.delivery import review
            out = {"ok": {"dead": review.health(rid)}}
        else:
            out = {"error": {"type": "ValueError", "message": f"unknown job {kind}"}}
    except BaseException as e:  # noqa: BLE001 — recommend raises SystemExit when no lecture asked for anything
        if isinstance(e, KeyboardInterrupt):
            raise
        from profsagent.llm.client import AllEndpointsFailed
        out = {"error": {"type": type(e).__name__, "message": str(e)[:2000], "quota": isinstance(e, AllEndpointsFailed),
                         "traceback": traceback.format_exc()}}
    (out_dir(rid) / "app_step_result.json").write_text(json.dumps(out, ensure_ascii=False, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
