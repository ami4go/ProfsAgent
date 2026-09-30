"""Run the ProfsAgent design pipeline.

  python scripts/run_design.py --input eval/inputs/cse201_P2.yaml --run-id cse201-dev-01 --auto-approve
  python scripts/run_design.py --run-id cse201-dev-01 --resume --decision approve --by "Prof X"   # answer a gate

Without --auto-approve the run stops at each gate (LangGraph interrupt) and prints what needs approval.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _s in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252; logs contain arrows and ≈
    _s.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(ROOT / "src"))

import yaml  # noqa: E402
from langgraph.types import Command  # noqa: E402

from profsagent.agents.pipeline import make_runtime  # noqa: E402
from profsagent.config import RUNS  # noqa: E402
from profsagent.orchestrator.graph import build, register  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--auto-approve", action="store_true")
    ap.add_argument("--no-research", action="store_true")
    ap.add_argument("--resume", action="store_true", help="answer a pending professor gate")
    ap.add_argument("--continue", dest="cont", action="store_true", help="continue a run that stopped on an error")
    ap.add_argument("--decision", default="approve")
    ap.add_argument("--by", default="professor")
    ap.add_argument("--comment", default="")
    a = ap.parse_args()
    run_dir = RUNS / a.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    app = build(str(run_dir / "checkpoint.sqlite"))
    cfg = {"configurable": {"thread_id": a.run_id}}
    if a.resume:
        res = app.invoke(Command(resume={"decision": a.decision, "by": a.by, "comment": a.comment}), cfg)
    elif a.cont:
        res = app.invoke(None, cfg)
    else:
        spec = yaml.safe_load(Path(a.input).read_text(encoding="utf-8"))
        run_cfg = spec["run"]
        if a.no_research:
            run_cfg["external_research"] = False
        rt = make_runtime(a.run_id, spec["form"], run_cfg)
        rt.save()
        register(rt)
        res = app.invoke({"run_id": a.run_id, "auto_approve": a.auto_approve, "done": []}, cfg)
    intr = res.get("__interrupt__") if isinstance(res, dict) else None
    if intr:
        print("\n=== WAITING FOR PROFESSOR ===")
        print(json.dumps(intr[0].value, indent=1, ensure_ascii=False, default=str)[:4000])
        print(f"\nresume with: python scripts/run_design.py --run-id {a.run_id} --resume --decision approve --by \"<name>\"")
    else:
        print(f"\nfinished: {run_dir / 'proposal.md'}")


if __name__ == "__main__":
    main()
