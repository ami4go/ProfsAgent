"""Load (or remove, or check) a design run's course graph in Neo4j, linked to the IIIT-D graph (Layer A).

  python scripts/load_design_to_neo4j.py --run-id cs601-01            # load / reload, then check it
  python scripts/load_design_to_neo4j.py --run-id cs601-01 --check    # only check what is in Neo4j
  python scripts/load_design_to_neo4j.py --run-id cs601-01 --delete   # remove it from Neo4j
  python scripts/load_design_to_neo4j.py --run-dir path/to/run        # a run folder outside runs/

New runs are loaded automatically after the final approval gate when Neo4j is reachable. Neo4j must be running.
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

from profsagent.design.neo4j_sync import check_run, delete_run, load_run  # noqa: E402


def print_checks(run_dir: Path) -> bool:
    checks = check_run(run_dir)
    for c in checks:
        print(f"  {'PASS' if c['ok'] else 'FAIL'}  {c['check']}: {c['detail']}")
    return all(c["ok"] for c in checks)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--run-dir")
    ap.add_argument("--delete", action="store_true")
    ap.add_argument("--check", action="store_true", help="only compare what is in Neo4j with the run's files")
    a = ap.parse_args()
    if not (a.run_id or a.run_dir):
        ap.error("give --run-id or --run-dir")
    run = Path(a.run_dir) if a.run_dir else ROOT / "runs" / a.run_id
    if a.delete:
        print(f"removed {delete_run(run.name)} design nodes of {run.name}")
    elif a.check:
        sys.exit(0 if print_checks(run) else 1)
    else:
        print(json.dumps(load_run(run), indent=1))
        print_checks(run)
