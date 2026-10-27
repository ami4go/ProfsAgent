"""Runs one step of a course run in its own process, so the app can end it at once (Delete).

    python -m profsagent.app.stepper <run_dir> <kind> [<payload.json>]

kind: "fill" (fill in the blank details) or "start" | "resume" | "continue" (the design pipeline).
The result goes to <run_dir>/step_result.json: {"ok": {...}} or {"error": {type, message, quota, traceback}}.
The pipeline's own log lines go to stdout, i.e. the terminal the app runs in.
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from pathlib import Path


def main(argv: list[str]) -> int:
    for s in (sys.stdout, sys.stderr):   # pipeline logs contain arrows and ≈; Windows consoles default to cp1252
        s.reconfigure(encoding="utf-8", errors="replace")
    run_dir, kind = Path(argv[1]), argv[2]
    payload = json.loads(Path(argv[3]).read_text(encoding="utf-8")) if len(argv) > 3 else None
    import profsagent.config  # noqa: F401  (loads .env)
    if not os.environ.get("GROQ_API_KEYS") and os.environ.get("GROQ_API_KEY"):
        os.environ["GROQ_API_KEYS"] = os.environ["GROQ_API_KEY"]
    try:
        if kind == "fill":
            from profsagent.app.filler import DetailsFiller
            out = {"ok": DetailsFiller().fill(run_dir)}
        else:
            from profsagent.app.runner import PipelineDriver
            out = {"ok": PipelineDriver().step(run_dir.name, kind, payload)}
    except Exception as e:  # noqa: BLE001 — reported to the app, which decides between pause and "Try again"
        from profsagent.llm.client import AllEndpointsFailed
        out = {"error": {"type": type(e).__name__, "message": str(e)[:2000], "quota": isinstance(e, AllEndpointsFailed),
                         "traceback": traceback.format_exc()}}
    (run_dir / "step_result.json").write_text(json.dumps(out, ensure_ascii=False, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
