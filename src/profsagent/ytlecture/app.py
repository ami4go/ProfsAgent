"""Web-app glue for delivery mode 2: start a run in the background, report its progress, and serve the player."""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

from profsagent.config import RUNS

_jobs: dict[str, dict] = {}
_lock = threading.Lock()


def _dir(rid: str, runs: Path | None = None) -> Path:
    return (runs or RUNS) / rid / "delivery" / "ytlecture"


def view(rid: str, runs: Path | None = None) -> dict:
    d = _dir(rid, runs)
    lecs = []
    for p in sorted((d / "lectures").glob("*.json")):
        try:
            x = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        lecs.append({"lecture_id": x["id"], "topic": x["topic"], "status": x["status"], "recommendation": x["recommendation"],
                     "slot_min": x["slot_min"], "video_min": round(x["video_total_s"] / 60), "gaps": x["gaps"],
                     "warnings": x["warnings"], "parts": [{"title": pp["title"], "minutes": pp["minutes"], "gap": pp["gap"],
                                                           "clips": pp["clips"]} for pp in x["parts"]]})
    job = _jobs.get(rid) or {}
    return {"job": {k: job.get(k) for k in ("state", "lectures", "started", "finished", "log", "error")} if job else None,
            "lectures": lecs, "player": f"/api/delivery/{rid}/videos/player/player.html" if (d / "player.html").exists() else None}


def start(rid: str, lectures: list[str], refresh: bool = False, runs: Path | None = None) -> dict:
    with _lock:
        if any(j.get("state") == "running" for j in _jobs.values()):
            return {"started": False, "why": "another video search is running"}
        job = {"state": "running", "lectures": lectures, "started": time.time(), "log": [], "error": None}
        _jobs[rid] = job

    def log(msg: str) -> None:
        job["log"] = (job["log"] + [f"{time.strftime('%H:%M:%S')} {msg}"])[-200:]

    def work():
        from profsagent.ytlecture import run
        try:
            run(rid, lectures or None, refresh=refresh, log=log)
            job["state"] = "done"
        except Exception as e:  # noqa: BLE001 — shown to the professor; the checkpoints let a retry continue
            job["state"], job["error"] = "failed", f"{type(e).__name__}: {str(e)[:300]}"
        job["finished"] = time.time()
    threading.Thread(target=work, daemon=True, name=f"ytlecture-{rid}").start()
    return {"started": True}


def player_file(rid: str, name: str, runs: Path | None = None) -> Path | None:
    if name not in ("player.html", "playlists.js"):
        return None
    p = _dir(rid, runs) / name
    return p if p.exists() else None
