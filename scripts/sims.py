"""The simulation catalogue from the command line (simulations/, docs/09_phase2_A_simulation_catalogue.md).

    python scripts/sims.py list                 the entries, their type, courses, level and status
    python scripts/sims.py check                every sim.yaml checked (types, courses, files, versions)
    python scripts/sims.py build [id ...]       offline single-file pages into simulations/_build/
    python scripts/sims.py qa [id ...]          build, then run each entry's qa.py; report in simulations/_build/qa_report.json
    python scripts/sims.py coverage             topic -> type classifier over every IIIT-D course's weekly topics
    python scripts/sims.py external             rebuild simulations/external/index.json (PhET + Falstad lists, + sources.yaml)
"""
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")

from profsagent.sims import catalogue as C  # noqa: E402


def pick(ids):
    es = C.entries()
    if not ids:
        return es
    want = set(ids)
    out = [e for e in es if e.get("id") in want]
    missing = want - {e.get("id") for e in out}
    if missing:
        sys.exit(f"no such simulation: {', '.join(sorted(missing))}")
    return out


def cmd_list(_):
    for e in C.entries():
        ts = e["type"] if isinstance(e["type"], list) else [e["type"]]
        print(f"{e['id']:34s} {'+'.join(t.split('-')[0] for t in ts):6s} {','.join(e['courses']):16s} {e['interactivity']:3s} "
              f"v{e['version']:7s} {e['status']}")


def cmd_check(_):
    bad = 0
    for e in C.entries():
        p = C.problems(e)
        bad += bool(p)
        print(("✗ " if p else "✓ ") + e.get("id", str(e["_dir"].name)) + ("" if not p else "\n    " + "\n    ".join(p)))
    print(f"{len(C.entries()) - bad} of {len(C.entries())} entries are fine")
    return 1 if bad else 0


def cmd_build(ids):
    for e in pick(ids):
        out = C.build(e)
        print(f"{e['id']:34s} {out.stat().st_size / 1e6:5.2f} MB  {out.relative_to(C.ROOT)}")


def cmd_qa(ids):
    report, bad = {}, 0
    for e in pick(ids):
        print(f"{e['id']} …", flush=True)
        r = C.run_qa(e)
        report[e["id"]] = {**r, "version": e["version"], "at": time.strftime("%Y-%m-%d %H:%M")}
        bad += not r["ok"]
        print(f"  {'✓' if r['ok'] else '✗'} {r['seconds']} s · {r['summary']}" + "".join(f"\n    {x}" for x in r["problems"]))
    C.BUILD.mkdir(parents=True, exist_ok=True)
    path = C.BUILD / "qa_report.json"
    old = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    path.write_text(json.dumps({**old, **report}, indent=1, ensure_ascii=False), encoding="utf-8")   # keep other entries' last results
    print(f"{len(report) - bad} of {len(report)} passed · report: simulations/_build/qa_report.json")
    return 1 if bad else 0


def cmd_external(_):
    from profsagent.sims import external
    counts = external.build()
    print("  ".join(f"{k}: {v}" for k, v in counts.items()) + f"  ->  {sum(counts.values())} links in simulations/external/index.json")


def cmd_coverage(args):
    from profsagent.sims import classify
    return classify.main(args)


if __name__ == "__main__":
    cmds = {"list": cmd_list, "check": cmd_check, "build": cmd_build, "qa": cmd_qa, "coverage": cmd_coverage, "external": cmd_external}
    if len(sys.argv) < 2 or sys.argv[1] not in cmds:
        sys.exit(__doc__)
    sys.exit(cmds[sys.argv[1]](sys.argv[2:]) or 0)
