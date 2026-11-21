"""The files a run and the Claude Code session exchange, in runs/<run_id>/agentcc/:

    NNN_<pid>.request.json   the run: the task (brief, inputs, output schema, the checks that apply, what is hidden)
    NNN_<pid>.draft.json     the session: a draft to check (optional, as often as it likes)
    NNN_<pid>.check.json     the run: what the pipeline's validators say about the last draft
    NNN_<pid>.answer.json    the session: the finished answer
    NNN_<pid>.notes.md       the session: how it worked (sources, decisions), optional
    NNN_<pid>.done.json      the run: accepted (or .check.json again with `rejected` if the answer does not parse)

A request is open while it has no .done.json. Only the run writes request/check/done files; only the session writes
draft/answer/notes files.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

from profsagent.config import RUNS

AGENT = "claude_code"
FOLDER = "agentcc"


def folder(run_dir: Path) -> Path:
    d = Path(run_dir) / FOLDER
    d.mkdir(parents=True, exist_ok=True)
    return d


def write_json(p: Path, obj) -> None:
    """Atomic: the other side never reads half a file."""
    tmp = p.with_name(p.name + f".tmp{os.getpid()}")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    for _ in range(50):                # OneDrive can hold a file for a moment right after it was written
        try:
            os.replace(tmp, p)
            return
        except PermissionError:
            time.sleep(0.2)
    os.replace(tmp, p)


def read_json(p: Path):
    for _ in range(25):
        try:
            return json.loads(Path(p).read_text(encoding="utf-8"))
        except (json.JSONDecodeError, PermissionError):
            time.sleep(0.2)
    return json.loads(Path(p).read_text(encoding="utf-8"))


def stem(req_path: Path) -> str:
    return re.sub(r"\.request\.json$", "", Path(req_path).name)


def sibling(req_path: Path, kind: str) -> Path:
    """kind: draft.json, check.json, answer.json, notes.md, done.json"""
    return Path(req_path).with_name(f"{stem(req_path)}.{kind}")


def next_request_path(run_dir: Path, pid: str) -> Path:
    d = folder(run_dir)
    n = len(list(d.glob("*.request.json"))) + 1
    return d / f"{n:03d}_{re.sub(r'[^A-Za-z0-9]+', '', pid)}.request.json"


def pid_alive(pid) -> bool:
    """Is the step process that wrote a request still running? (No pid recorded: assume yes.)"""
    if not pid:
        return True
    if os.name == "nt":
        import ctypes
        k = ctypes.windll.kernel32
        h = k.OpenProcess(0x1000, False, int(pid))          # PROCESS_QUERY_LIMITED_INFORMATION
        if not h:
            return False
        code = ctypes.c_ulong()
        k.GetExitCodeProcess(h, ctypes.byref(code))
        k.CloseHandle(h)
        return code.value == 259                              # STILL_ACTIVE
    try:
        os.kill(int(pid), 0)
        return True
    except OSError:
        return False


def open_requests(runs: Path = RUNS) -> list[Path]:
    """Every request in every run that is not answered yet and whose step process is still waiting, oldest first.
    A request whose process ended (the app was closed, the step was killed) is skipped: the step asks again when it
    is restarted."""
    out = []
    for p in Path(runs).glob(f"*/{FOLDER}/*.request.json"):
        if sibling(p, "done.json").exists():
            continue
        try:
            owner = read_json(p).get("owner_pid")
        except Exception:  # noqa: BLE001
            owner = None
        if pid_alive(owner):
            out.append(p)
    return sorted(out, key=lambda p: p.stat().st_mtime)


def is_agent_run(run_cfg: dict | None) -> bool:
    return str((run_cfg or {}).get("agent") or "").lower() == AGENT
