"""Evaluation tier 1 (deterministic) for saved design runs. No LLM calls.

  python scripts/evaluate_design.py --run-id cs601-02        # writes runs/cs601-02/evaluation_deterministic.json
  python scripts/evaluate_design.py --all                    # one line per run in runs/ (nothing written)
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

from profsagent.config import RUNS  # noqa: E402
from profsagent.evaluate.deterministic import evaluate  # noqa: E402


def load(run_dir: Path) -> dict | None:
    f = run_dir / "state.json"
    if not f.exists():
        return None
    s = json.loads(f.read_text(encoding="utf-8"))
    return s if s.get("cos") and s.get("bloom_band") else None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    if a.run_id:
        s = load(RUNS / a.run_id)
        if s is None:
            sys.exit(f"no finished design in runs/{a.run_id}")
        ev = evaluate(s)
        out = RUNS / a.run_id / "evaluation_deterministic.json"
        out.write_text(json.dumps(ev, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
        print(json.dumps(ev["summary"], indent=1, ensure_ascii=False))
        print(f"→ {out.relative_to(ROOT)}")
    elif a.all:
        print(f"{'run':40} {'verdict':7} {'errors':>6} {'align%':>7} {'hard%':>6}  would-block")
        for d in sorted(p for p in RUNS.iterdir() if p.is_dir() and not p.name.startswith("_")):
            s = load(d)
            if s is None:
                continue
            ev = evaluate(s)
            x = ev["summary"]
            print(f"{d.name:40} {x['verdict']:7} {x['errors']:>6} {str(x['alignment_min_pct']):>7} "
                  f"{str(x['hard_constraints_satisfied_pct']):>6}  {','.join(ev['gates']['would_block']) or '-'}")
    else:
        ap.error("give --run-id or --all")


if __name__ == "__main__":
    main()
