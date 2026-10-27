"""Start the ProfsAgent app on this laptop and open it in the browser.

  python scripts/run_app.py                 # http://127.0.0.1:8000
  python scripts/run_app.py --port 8100 --no-browser

Needs Neo4j Desktop running with the graph loaded (or KG_BACKEND=stub), the AI keys in .env, and
`pip install fastapi uvicorn markdown` on top of the pipeline's requirements.
Course runs are saved under runs/app-*/ and survive a restart: a run that was working continues by itself.
"""
from __future__ import annotations

import argparse
import os
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _s in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252; pipeline logs contain arrows and ≈
    _s.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(ROOT / "src"))

import uvicorn  # noqa: E402

import profsagent.config  # noqa: E402,F401  (loads .env into the environment)
from profsagent.app.server import create_app  # noqa: E402

if not os.environ.get("GROQ_API_KEYS") and os.environ.get("GROQ_API_KEY"):   # a single key under the singular name
    os.environ["GROQ_API_KEYS"] = os.environ["GROQ_API_KEY"]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=os.environ.get("APP_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("APP_PORT", "8000")))
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    url = f"http://{'127.0.0.1' if a.host in ('0.0.0.0', '::') else a.host}:{a.port}"
    print(f"ProfsAgent is starting at {url}  (Ctrl+C to stop)")
    if not a.no_browser:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run(create_app(), host=a.host, port=a.port, log_level="warning")


if __name__ == "__main__":
    main()
