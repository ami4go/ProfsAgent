"""Load (or remove) a design run's course graph in Neo4j, linked to the IIIT-D graph (Layer A).

  python scripts/load_design_to_neo4j.py --run-id cs601-01            # load / reload
  python scripts/load_design_to_neo4j.py --run-id cs601-01 --delete   # remove it from Neo4j

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

from profsagent.design.neo4j_sync import delete_run, load_run  # noqa: E402

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--delete", action="store_true")
    a = ap.parse_args()
    if a.delete:
        print(f"removed {delete_run(a.run_id)} design nodes of {a.run_id}")
    else:
        print(json.dumps(load_run(ROOT / "runs" / a.run_id), indent=1))
