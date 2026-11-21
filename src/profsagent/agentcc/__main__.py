"""The Claude Code session's side of the handoff (run from the repo root as `PYTHONPATH=src python -m profsagent.agentcc ...`):

  python -m profsagent.agentcc watch [--all] [--timeout S]   wait until a run asks for a step, print it, exit
  python -m profsagent.agentcc list                           every open request
  python -m profsagent.agentcc check  <request> <draft.json>  the pipeline's validators on a draft (waits for the run)
  python -m profsagent.agentcc submit <request> <answer.json> hand back the finished answer
  python -m profsagent.agentcc deliver <request>              a delivery job's files are written: check them, mark it done
  python -m profsagent.agentcc kg --run <run_id> search "<text>" | course <code> | topics "<text>" | index
                                                              the IIIT-D course database, read-only, hidden courses left out
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")

from profsagent.agentcc import protocol as P  # noqa: E402
from profsagent.config import RUNS  # noqa: E402

SEEN = RUNS / "_agentcc_seen.json"


def _seen() -> set[str]:
    return set(P.read_json(SEEN)) if SEEN.exists() else set()


def _describe(req: Path) -> str:
    r = P.read_json(req)
    return f"{req}\n  run {r['run_id']}  step {r['pid']} ({r['kind']})  checks: {', '.join(r['checks']) or 'schema only'}"


def cmd_watch(a) -> int:
    t0 = time.time()
    while True:
        seen = set() if a.all else _seen()
        new = [p for p in P.open_requests(RUNS) if str(p) not in seen]
        if new:
            for p in new:
                print(_describe(p))
            P.write_json(SEEN, sorted(_seen() | {str(p) for p in new}))
            return 0
        if a.timeout and time.time() - t0 > a.timeout:
            print("no request")
            return 1
        time.sleep(2)


def cmd_list(a) -> int:
    reqs = P.open_requests(RUNS)
    print("\n".join(_describe(p) for p in reqs) if reqs else "no open request")
    return 0


def _wait_report(req: Path, t0: float, want: str, timeout: float = 180) -> dict | None:
    chk, done = P.sibling(req, "check.json"), P.sibling(req, "done.json")
    while time.time() - t0 < timeout:
        if want == "answer" and done.exists() and done.stat().st_mtime >= t0 - 1:
            return {"accepted": True, **P.read_json(done)}
        if chk.exists():
            r = P.read_json(chk)
            if r.get("at", 0) >= t0 and (r.get("for") == want):
                return r
        time.sleep(0.5)
    return None


def _print_report(r: dict) -> int:
    if r.get("accepted"):
        print(f"ACCEPTED after {r.get('seconds')}s, {r.get('drafts')} drafts checked; "
              f"{len(r.get('errors') or [])} errors, {r.get('warnings')} warnings left")
        return 0
    if r.get("schema_errors"):
        print("SCHEMA ERRORS (the JSON does not fit the output format):")
        for e in r["schema_errors"]:
            print("  -", e)
    if r.get("hidden_named"):
        print("NAMES A HIDDEN COURSE OR DOMAIN:", ", ".join(r["hidden_named"]))
    errs, warns = r.get("errors") or [], r.get("warnings") or []
    if r.get("fixers_applied"):
        print("fixers the pipeline would apply:", ", ".join(r["fixers_applied"]))
    print(f"{len(errs)} errors, {len(warns)} warnings" + (" (answer REJECTED; fix and submit again)" if r.get("rejected") else ""))
    for x in errs:
        print(f"  ERROR {x.get('code')}: {x.get('message')}  nodes={x.get('nodes')}")
    for x in warns[:25]:
        print(f"  warn  {x.get('code')}: {x.get('message')}  nodes={x.get('nodes')}")
    if len(warns) > 25:
        print(f"  … {len(warns) - 25} more warnings (full report: {r.get('path', 'the .check.json file')})")
    return 0 if not (r.get("schema_errors") or r.get("hidden_named") or errs or r.get("rejected")) else 2


def _hand(a, kind: str) -> int:
    req = Path(a.request).resolve()
    if not req.name.endswith(".request.json") or not req.exists():
        print("not a request file:", req)
        return 1
    if P.sibling(req, "done.json").exists():
        print("this request is already answered")
        return 1
    obj = json.loads(Path(a.file).read_text(encoding="utf-8"))       # must be valid JSON before it is handed over
    t0 = time.time()
    P.write_json(P.sibling(req, f"{kind}.json"), obj)
    r = _wait_report(req, t0, kind)
    if r is None:
        print("the run did not answer within 3 minutes: is the app (or the step) still running?")
        return 1
    r["path"] = str(P.sibling(req, "check.json"))
    return _print_report(r)


def cmd_deliver(a) -> int:
    from profsagent.agentcc import delivery as D
    req = Path(a.request).resolve()
    if not req.name.endswith(".request.json") or not req.exists():
        print("not a request file:", req)
        return 1
    if P.sibling(req, "done.json").exists():
        print("this request is already answered")
        return 1
    probs = D.finish(req)
    if probs:
        print(f"{len(probs)} problems; the job stays open:")
        for x in probs:
            print("  -", x)
        return 2
    print("DELIVERED: request done, the app shows the result")
    return 0


def cmd_kg(a) -> int:
    import yaml
    from profsagent.kg.neo4j_kg import Neo4jKG
    spec = yaml.safe_load((RUNS / a.run / "input.yaml").read_text(encoding="utf-8")) if a.run else {}
    ex = {c.upper() for c in ((spec or {}).get("run") or {}).get("exclude_courses", [])}
    kg = Neo4jKG(None)
    if a.what == "search":
        out = kg.search_courses(a.arg, k=a.k, exclude=ex)
    elif a.what == "course":
        u = kg.resolve(a.arg)
        out = kg.course(u, exclude=ex) if u and u.upper() not in ex else None
    elif a.what == "topics":
        out = kg.topic_candidates([a.arg], k=a.k, exclude=ex)
    else:
        out = kg.index(exclude=ex)
    print(json.dumps(out, indent=1, ensure_ascii=False, default=str))
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="python -m profsagent.agentcc")
    sub = ap.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("watch")
    w.add_argument("--all", action="store_true", help="also requests already announced")
    w.add_argument("--timeout", type=float, default=0)
    sub.add_parser("list")
    for k in ("check", "submit"):
        s = sub.add_parser(k)
        s.add_argument("request")
        s.add_argument("file")
    sub.add_parser("deliver").add_argument("request")
    g = sub.add_parser("kg")
    g.add_argument("--run", default=None, help="run id: its hidden courses are left out")
    g.add_argument("--k", type=int, default=10)
    g.add_argument("what", choices=["search", "course", "topics", "index"])
    g.add_argument("arg", nargs="?", default="")
    a = ap.parse_args(argv)
    if a.cmd == "watch":
        return cmd_watch(a)
    if a.cmd == "list":
        return cmd_list(a)
    if a.cmd == "check":
        return _hand(a, "draft")
    if a.cmd == "deliver":
        return cmd_deliver(a)
    if a.cmd == "submit":
        return _hand(a, "answer")
    return cmd_kg(a)


if __name__ == "__main__":
    sys.exit(main())
