"""Auto-build: the machine tries to build a requested simulation itself (decisions.md 28; docs/09 §11, A5).

A professor's request (a topic, and what students should see or try) becomes a RECIPE for the stepper engine
(simulations/_engines/stepper/README.md, "Recipes"): one AI call writes it, and the automatic checks
(_engines/stepper/qa_recipe.py) run it in Chrome with the network blocked. When they find problems, the AI gets them
back and tries again, at most 3 attempts in all. A recipe that passes becomes a catalogue entry simulations/auto.<topic>/
(status draft, built_by machine) and the request becomes "ready"; otherwise the request goes to the team, with the reason.
The AI may also decline when a step-by-step simulation cannot teach the topic.

Cost: 1 to 3 calls of the "generate" role (Gemini first; the keys already in .env). No other AI.

    python -m profsagent.sims.autobuild worker [--runs DIR]   build every queued request, one at a time (the app starts this)
    python -m profsagent.sims.autobuild example               run the automatic checks on the hand-written example recipe

Before building, the machine looks for an existing simulation (sims/websearch.py: our catalogue, the saved links, a web
search trusted sites first, and the top pages opened in Chrome). When it finds some, the professor reviews them; only when
nothing fits, or the professor rejects them all, does it build (decisions.md 29: "visit the top 3-4 pages, then only fall
back to auto-creation").

Request statuses (runs/_simulation_requests.json): requested (old, not started) -> queued -> searching ->
review (found: the professor approves one -> chosen, or rejects them all -> build_queued) | building (nothing found) ->
ready (sim_id) | needs_team (reason) | paused (the AI quota is used up; try again later).
Files per request: runs/_simulation_builds/<request id>/ (each attempt's recipe and problems, the AI calls, the log).
"""
from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
import threading
import time
from pathlib import Path

import yaml

from profsagent.config import ROOT, RUNS
from profsagent.sims import catalogue as C

ENGINE = C.SIMS / "_engines" / "stepper"
README = ENGINE / "README.md"
EXAMPLE = ENGINE / "example_recipe.js"
QA = ENGINE / "qa_recipe.py"
REQUESTS = "_simulation_requests.json"
BUILDS = "_simulation_builds"
WORKER = "_simulation_autobuild.json"        # the worker's heartbeat: {"pid", "alive_at", "request"}
ATTEMPTS = 3
PROMPT_VERSION = "0.1.0"
# what a recipe may not contain, with the words the AI is told (lookbehind: node.parent.x is fine, a bare parent.x is not)
FORBIDDEN = [(r"\bfetch\s*\(", "fetch()"), (r"XMLHttpRequest", "XMLHttpRequest"), (r"WebSocket", "WebSocket"), (r"\bimport\s*\(", "import()"),
             (r"\beval\s*\(", "eval()"), (r"new\s+Function", "new Function"), (r"localStorage", "localStorage"), (r"sessionStorage", "sessionStorage"),
             (r"indexedDB", "indexedDB"), (r"</script", "the text </script"), (r"https?://", "web addresses (http:// or https://)"),
             (r"(?<![.\w$])parent\.", "a variable named parent (it means the browser's parent window; rename it)"),
             (r"(?<![.\w$])top\.", "a variable named top (it means the browser's top window; rename it, e.g. topIndex)"),
             (r"postMessage", "postMessage"), (r"(?<![.\w$])document\.", "document (the page)"), (r"(?<![.\w$])window\.", "window (the page)"),
             (r"(?<![.\w$])globalThis\b", "globalThis"), (r"setInterval", "setInterval (timers)"), (r"setTimeout", "setTimeout (timers)"),
             (r"\bWorker\s*\(", "Worker()")]

SYSTEM = """You write interactive teaching simulations for university students (IIIT-Delhi) as a RECIPE for an existing,
tested step-through engine. You never write HTML or drawing code: each step lists widgets and the engine draws them.
Your recipe is accepted only if automatic checks pass in a browser:
- run() must work on every preset, every example and 40 inputs from random();
- check() must agree with run() on all of them, by working the answer out with a DIFFERENT method (it must not call run),
  and it must reject a slightly corrupted result;
- run() must return exactly the textbook result of each example;
- every step must name a real code line, have a one-sentence note and use the widgets correctly.
Write for students meeting the topic for the first time: plain words, one idea per step, and prediction questions
(ask) at the moments where thinking ahead teaches the most."""


# ------------------------------------------------------------------ files and locks
def _rj(p: Path, default=None):
    try:
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
    except (OSError, ValueError):
        return default


def _wj(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(p.suffix + f".{os.getpid()}.tmp")
    tmp.write_text(json.dumps(obj, indent=1, ensure_ascii=False), encoding="utf-8")
    for i in range(20):                       # OneDrive or a reader may hold the file for a moment
        try:
            os.replace(tmp, p)
            return
        except PermissionError:
            time.sleep(0.1 * (i + 1))
    os.replace(tmp, p)


class _Lock:
    """A lock file next to the requests file, so the app and the worker never overwrite each other's changes."""
    def __init__(self, runs: Path):
        self.p = runs / (REQUESTS + ".lock")

    def __enter__(self):
        t0 = time.time()
        while True:
            try:
                fd = os.open(self.p, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                return self
            except FileExistsError:
                try:
                    if time.time() - self.p.stat().st_mtime > 30:     # left behind by a process that died
                        self.p.unlink()
                        continue
                except OSError:
                    pass
                if time.time() - t0 > 10:
                    raise TimeoutError("the simulation requests file is busy")
                time.sleep(0.05)

    def __exit__(self, *a):
        try:
            self.p.unlink()
        except OSError:
            pass


def read_requests(runs: Path | None = None) -> list[dict]:
    return _rj((runs or RUNS) / REQUESTS, []) or []


def update_requests(runs: Path | None, fn) -> list[dict]:
    """fn(rows) changes the rows in place, under the lock; returns the rows."""
    runs = runs or RUNS
    with _Lock(runs):
        rows = read_requests(runs)
        fn(rows)
        _wj(runs / REQUESTS, rows)
    return rows


def set_request(runs: Path | None, req_id: str, **fields) -> dict | None:
    out = {}

    def fn(rows):
        for r in rows:
            if r.get("id") == req_id:
                r.update(fields)
                out.update(r)
    update_requests(runs, fn)
    return out or None


# ------------------------------------------------------------------ the AI's part
def user_prompt(req: dict, previous: str | None = None, problems: list[str] | None = None) -> str:
    parts = ["# The engine and how to write a recipe\n\n" + README.read_text(encoding="utf-8"),
             "# A complete recipe that passes every check (binary search)\n\n```javascript\n" + EXAMPLE.read_text(encoding="utf-8") + "\n```",
             "# The professor's request\n\n" + f"- Topic: {req.get('topic')}\n- What students should see or try: {req.get('what')}\n"
             + (f"- Course: {req['course']}\n" if req.get("course") else "")
             + ("- The professor looked at these existing simulations and they did not fit: "
                + "; ".join(f"{c.get('title')} ({c.get('site')})" for c in req.get("found") or []) + "\n" if req.get("found") else "")
             + (f"- What the professor wants instead: {req['note']}\n" if req.get("note") else ""),
             """# What to return

Return ONE ```javascript code block that defines `const recipe = { ... };` and nothing else in the block.
- Teach exactly the requested topic, at university level, with the widgets that show it best (for example array with
  marks and pointers for sorting; stacks with disks for Tower of Hanoi; plot for sampling, geometry and convergence;
  graph for networks and trees; grid for matrices and dynamic programming).
- Every step must show a figure (array, stacks, plot, graph or grid). Tables and variables may only sit beside it.
- Choose presets that show the interesting cases, keep inputs small, and give at least 2 textbook examples whose result
  you have worked out by hand.
- If a step-by-step simulation cannot teach this topic at all, return instead the single line
  DECLINE: <one sentence saying why>"""]
    if previous is not None:
        parts.append("# Your previous recipe failed the automatic checks\n\n```javascript\n" + previous + "\n```\n\n"
                     "Problems found:\n" + "\n".join(f"- {p}" for p in (problems or [])[:25])
                     + "\n\nFix every problem and return the whole corrected recipe in one ```javascript block.")
    return "\n\n".join(parts)


def extract(text: str) -> tuple[str, str]:
    """("code", recipe) | ("decline", reason) | ("none", what came back)."""
    m = re.search(r"^\s*DECLINE:\s*(.+)$", text or "", re.M)
    blocks = re.findall(r"```(?:javascript|js)?\s*\n(.*?)```", text or "", re.S)
    code = next((b for b in blocks if re.search(r"\bconst\s+recipe\s*=", b)), None)
    if code is None and re.search(r"\bconst\s+recipe\s*=", text or ""):
        code = text
    if code is not None:
        return "code", code.strip()
    if m:
        return "decline", m.group(1).strip()[:300]
    return "none", (text or "")[:300]


def static_problems(code: str) -> list[str]:
    p = []
    if len(code) > 80_000:
        p.append("the recipe is too long (at most 80 KB)")
    if not re.search(r"\bconst\s+recipe\s*=\s*\{", code):
        p.append("the code must define const recipe = { ... };")
    for pat, words in FORBIDDEN:
        if re.search(pat, code):
            p.append(f"the recipe must not use {words}: plain JavaScript only, with no network, page, timers or storage")
    return p


def page_src(code: str, title: str) -> str:
    return ("<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
            f"<title>{html.escape(title)}</title>\n<link rel=\"stylesheet\" href=\"../_engines/stepper/stepper.css\">\n</head>\n<body>\n"
            "<script src=\"../_engines/share/share.js\"></script>\n<script src=\"../_engines/stepper/stepper.js\"></script>\n"
            "<script>\n'use strict';\n// recipe: written by the machine (auto-build), accepted by _engines/stepper/qa_recipe.py\n"
            + code.strip() + "\nwindow.__recipe = recipe;\nwindow.__sim = Stepper.mount(recipe);\n</script>\n</body>\n</html>\n")


def run_checks(code: str, where: Path, title: str = "Simulation") -> dict:
    """The automatic checks on one recipe: {"ok", "problems", "meta", "seconds", "summary"}."""
    where.mkdir(parents=True, exist_ok=True)
    sp = static_problems(code)
    if sp:
        return {"ok": False, "problems": sp, "meta": {}, "seconds": 0.0, "summary": "refused before running: " + sp[0]}
    page = where / "page.html"
    page.write_text(C.inline(page_src(code, title)), encoding="utf-8")
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, str(QA), str(page), str(where / "shots")], capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=300)
        lines = [x for x in (r.stdout or "").splitlines() if x.strip()]
    except subprocess.TimeoutExpired:
        return {"ok": False, "problems": ["the checks took longer than 5 minutes (a step loops forever?)"], "meta": {}, "seconds": 300.0,
                "summary": "timed out"}
    meta = next((json.loads(x[5:]) for x in lines if x.startswith("META:")), {})
    probs = [x[len("PROBLEM: "):] for x in lines if x.startswith("PROBLEM: ")]
    if r.returncode != 0 and not probs:
        probs = [((r.stderr or "") + (r.stdout or "")).strip()[-400:] or "the checks stopped without a report"]
    return {"ok": r.returncode == 0 and not probs, "problems": probs, "meta": meta, "seconds": round(time.time() - t0, 1),
            "summary": next((x for x in reversed(lines) if x.startswith("PROBLEMS:")), "")}


# ------------------------------------------------------------------ one request
def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", (s or "").lower()).strip("_")[:40] or "simulation"


def publish(req: dict, code: str, meta: dict, report: dict, build: dict) -> str:
    """The recipe that passed becomes a catalogue entry, marked as built by the machine and not yet reviewed by the team."""
    base = "auto." + _slug(req.get("topic") or meta.get("title"))
    sid, n = base, 2
    while (C.SIMS / sid).exists():
        sid, n = f"{base}_{n}", n + 1
    d = C.SIMS / sid
    d.mkdir(parents=True)
    title = (meta.get("title") or req.get("topic") or "Simulation").strip()
    (d / "page.src.html").write_text(page_src(code, title), encoding="utf-8")
    today = time.strftime("%Y-%m-%d")
    entry = {
        "id": sid, "type": ["1-step-through"], "title": title,
        "summary": (meta.get("summary") or req.get("what") or title).strip()[:240],
        "shows_code": True,                     # the stepper engine always shows the code beside the simulation
        "version": "1.0.0", "status": "draft", "built_by": "machine", "request": req.get("id"),
        "courses": [], "topics": [str(t) for t in (meta.get("topics") or [req.get("topic")])][:8],
        "interactivity": "L3", "engine": {"name": "stepper", "path": "_engines/stepper"},
        "files": {"page_src": "page.src.html", "qa": "../_engines/stepper/qa_recipe.py"},
        "checks": {"independent": (meta.get("checked_by") or "")[:300],
                   "qa": "automatic (qa_recipe.py): presets, textbook examples and 40 random inputs against the independent check; "
                         "a corrupted result must be rejected; widgets, code lines and questions valid; every example to its end; phone; offline"},
        "sensitive": False, "offline": True, "class_example": True,
        "build": build,
        "changelog": [{"version": "1.0.0", "date": today, "by": "machine",
                       "change": f"built from request {req.get('id')} ({req.get('topic')}); passed the automatic checks on attempt {build.get('attempts')}"}],
    }
    if len(entry["summary"]) < 20:
        entry["summary"] = (entry["summary"] + " — step through it and predict each step.")[:240]
    (d / "sim.yaml").write_text("# Built by the machine (auto-build, decisions.md 28). Checked automatically; not yet reviewed by the team.\n"
                                + yaml.safe_dump(entry, allow_unicode=True, sort_keys=False, width=140), encoding="utf-8")
    e = {**entry, "_dir": d}
    problems = C.problems(e)
    if problems:
        raise ValueError("the new entry is not valid: " + "; ".join(problems))
    C.build(e)
    qa_path = C.BUILD / "qa_report.json"
    old = _rj(qa_path, {}) or {}
    old[sid] = {"ok": True, "seconds": report.get("seconds"), "summary": report.get("summary"), "problems": [], "version": "1.0.0",
                "at": time.strftime("%Y-%m-%d %H:%M")}
    _wj(qa_path, old)
    return sid


class _FileAI:
    """Stands in for LLMClient.raw in QA servers and demos: every reply is the content of one file."""
    def __init__(self, path: Path):
        self.path = path

    def raw(self, role, system, user, temperature=0.2, json_mode=True, record=None, **kw):
        time.sleep(2)
        return self.path.read_text(encoding="utf-8"), {"prompt": len(user) // 4, "output": 0}, {}

    def _log(self, *a, **kw):
        pass


def build_request(req: dict, runs: Path | None = None, llm=None, log=print) -> dict:
    """Try to build one request. Returns the fields to store on it (status ready / needs_team / paused)."""
    from profsagent.llm.client import AllEndpointsFailed, CallRecord, LLMClient
    runs = runs or RUNS
    work = runs / BUILDS / req["id"]
    work.mkdir(parents=True, exist_ok=True)
    if llm is None and os.environ.get("PROFSAGENT_AUTOBUILD_REPLY"):     # QA and demos: the "AI" answers from a file, no AI calls
        llm = _FileAI(Path(os.environ["PROFSAGENT_AUTOBUILD_REPLY"]))
    llm = llm or LLMClient(work / "llm_calls.jsonl")
    t0, previous, problems, calls, models = time.time(), None, None, 0, []
    for attempt in range(1, ATTEMPTS + 1):
        set_request(runs, req["id"], status="building", build={"attempt": attempt, "of": ATTEMPTS, "started_at": req.get("build", {}).get("started_at") or time.strftime("%Y-%m-%d %H:%M:%S")})
        user = user_prompt(req, previous, problems)
        rec = CallRecord(prompt_id="sim_autobuild", prompt_version=PROMPT_VERSION, role="generate")
        log(f"{req['id']}: attempt {attempt}: asking the AI ({len(user):,} characters)")
        try:
            tc = time.time()
            text, usage, _meta = llm.raw("generate", SYSTEM, user, temperature=0.2, json_mode=False, record=rec)
            rec.prompt_tokens, rec.output_tokens, rec.latency_s, rec.ok = usage.get("prompt", 0), usage.get("output", 0), round(time.time() - tc, 1), True
            llm._log(rec, SYSTEM, user, text, req["id"])
        except AllEndpointsFailed as ex:
            return {"status": "paused", "reason": "The AI quota is used up for now; press Try again later.", "detail": str(ex)[:300],
                    "build": {"attempts": attempt - 1, "calls": calls, "seconds": round(time.time() - t0)}}
        calls += 1
        models.append((rec.endpoint or "").rsplit(":", 1)[0])
        (work / f"attempt-{attempt}.txt").write_text(text or "", encoding="utf-8")
        kind, body = extract(text)
        if kind == "decline":
            log(f"{req['id']}: the AI declined: {body}")
            return {"status": "needs_team", "reason": "A step-by-step simulation does not suit this request: " + body,
                    "build": {"attempts": attempt, "calls": calls, "models": models, "seconds": round(time.time() - t0)}}
        if kind == "none":
            problems = ["the reply had no ```javascript block defining const recipe = { ... };"]
            previous = body
            continue
        (work / f"attempt-{attempt}.js").write_text(body, encoding="utf-8")
        rep = run_checks(body, work / f"attempt-{attempt}", req.get("topic") or "Simulation")
        (work / f"attempt-{attempt}.problems.txt").write_text("\n".join(rep["problems"]) or "none", encoding="utf-8")
        log(f"{req['id']}: attempt {attempt}: {'passed' if rep['ok'] else str(len(rep['problems'])) + ' problems'} ({rep['seconds']} s)")
        if rep["ok"]:
            build = {"attempts": attempt, "calls": calls, "models": models, "seconds": round(time.time() - t0), "at": time.strftime("%Y-%m-%d %H:%M"),
                     "prompt_version": PROMPT_VERSION}
            try:
                sid = publish(req, body, rep["meta"], rep, build)
            except Exception as ex:  # noqa: BLE001
                return {"status": "needs_team", "reason": f"It passed the checks but could not be added to the catalogue: {ex}"[:300], "build": build}
            return {"status": "ready", "sim_id": sid, "reason": None, "build": build}
        previous, problems = body, rep["problems"]
    first = (problems or ["unknown problem"])[0]
    return {"status": "needs_team", "reason": f"The machine could not build it in {ATTEMPTS} attempts; the last problem: {first}"[:300],
            "build": {"attempts": ATTEMPTS, "calls": calls, "models": models, "seconds": round(time.time() - t0)}}


# ------------------------------------------------------------------ the worker (one at a time, in its own process)
def worker_alive(runs: Path | None = None) -> bool:
    w = _rj((runs or RUNS) / WORKER, {}) or {}
    return bool(w) and time.time() - w.get("alive_at", 0) < 45


def start_worker(runs: Path | None = None) -> bool:
    """Start the worker if requests wait and none is running. Requests left "building" by a worker that died are queued again."""
    runs = runs or RUNS
    if worker_alive(runs):
        return False

    def fn(rows):
        for r in rows:
            if r.get("status") == "building":
                r["status"] = "build_queued"
            elif r.get("status") == "searching":
                r["status"] = "queued"
    rows = update_requests(runs, fn)
    if not any(r.get("status") in ("queued", "build_queued") for r in rows):
        return False
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src") + os.pathsep + os.environ.get("PYTHONPATH", ""), "PYTHONIOENCODING": "utf-8"}
    log = (runs / BUILDS / "worker.log")
    log.parent.mkdir(parents=True, exist_ok=True)
    with log.open("a", encoding="utf-8") as fh:
        subprocess.Popen([sys.executable, "-m", "profsagent.sims.autobuild", "worker", "--runs", str(runs)], cwd=str(ROOT), env=env,
                         stdout=fh, stderr=subprocess.STDOUT)
    _wj(runs / WORKER, {"pid": None, "alive_at": time.time(), "request": None, "starting": True})
    return True


def worker(runs: Path | None = None) -> int:
    runs = runs or RUNS
    state = {"request": None, "stop": False}

    def beat():
        while not state["stop"]:
            _wj(runs / WORKER, {"pid": os.getpid(), "alive_at": time.time(), "request": state["request"]})
            time.sleep(10)
    threading.Thread(target=beat, daemon=True).start()
    log = lambda m: print(time.strftime("%H:%M:%S"), m, flush=True)  # noqa: E731
    try:
        while True:
            claimed = {}

            def claim(rows):
                q = sorted((r for r in rows if r.get("status") in ("queued", "build_queued")), key=lambda r: r.get("at") or "")
                if q:
                    claimed.update(q[0], phase="search" if q[0]["status"] == "queued" else "build")
                    q[0]["status"] = "searching" if q[0]["status"] == "queued" else "building"
            update_requests(runs, claim)
            if not claimed:
                return 0
            state["request"] = claimed["id"]
            if claimed["phase"] == "search":                 # look first; build only when nothing existing fits
                log(f"{claimed['id']}: looking for existing simulations of '{claimed.get('topic')}'")
                try:
                    from profsagent.sims import websearch
                    found = websearch.find(claimed, runs / BUILDS / claimed["id"], log=log)
                except Exception as ex:  # noqa: BLE001 - a failed search must not block building
                    log(f"{claimed['id']}: the search failed ({type(ex).__name__}: {ex}); building instead")
                    found = []
                now = time.strftime("%Y-%m-%d %H:%M:%S")
                if found:
                    set_request(runs, claimed["id"], status="review", found=found, searched_at=now)
                    log(f"{claimed['id']}: found {len(found)}; waiting for the professor's review")
                    continue
                set_request(runs, claimed["id"], status="building", found=[], searched_at=now)
                claimed["found"] = []
                log(f"{claimed['id']}: nothing existing fits; building one")
            log(f"{claimed['id']}: building '{claimed.get('topic')}'")
            try:
                out = build_request(claimed, runs, log=log)
            except Exception as ex:  # noqa: BLE001 - one bad request must not stop the others
                out = {"status": "needs_team", "reason": f"The auto-build stopped: {type(ex).__name__}: {ex}"[:300]}
            set_request(runs, claimed["id"], **out, finished_at=time.strftime("%Y-%m-%d %H:%M:%S"))
            log(f"{claimed['id']}: {out['status']}" + (f" ({out.get('sim_id') or out.get('reason')})"))
            if out["status"] == "ready" and claimed.get("run_id") and claimed.get("lecture"):
                try:                              # a request from a lecture page: the new simulation waits there for a decision
                    from profsagent.app import simulations as S
                    S.decide(claimed["run_id"], claimed["lecture"], out["sim_id"], "add", by="machine", runs=runs)
                except Exception as ex:  # noqa: BLE001
                    log(f"could not add it to {claimed['lecture']}: {ex}")
            if out["status"] == "paused":
                return 0                          # quota: stop; the professor presses Try again
    finally:
        state["stop"] = True
        try:
            (runs / WORKER).unlink()
        except OSError:
            pass


def main(argv: list[str]) -> int:
    if argv[:1] == ["worker"]:
        runs = Path(argv[argv.index("--runs") + 1]) if "--runs" in argv else RUNS
        return worker(runs)
    if argv[:1] == ["example"]:
        code = EXAMPLE.read_text(encoding="utf-8")
        rep = run_checks(code, C.BUILD / "autobuild_example", "Binary search")
        print("\n".join(["passed" if rep["ok"] else "FAILED"] + rep["problems"]))
        return 0 if rep["ok"] else 1
    print(__doc__)
    return 2


if __name__ == "__main__":
    for _s in (sys.stdout, sys.stderr):
        _s.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
