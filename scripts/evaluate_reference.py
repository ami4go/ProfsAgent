"""Evaluation tier 2: compare a design run with the real course it re-creates (held out from the graph during the run).
Local embeddings only, no API calls. The reference is data/enriched/<code>.json; by default the run's excluded course.

  python scripts/evaluate_reference.py --run-id cse201-dev-05            # writes runs/cse201-dev-05/evaluation_reference.json
  python scripts/evaluate_reference.py --run-id cs601-02 --course CSE601 # any course sheet as the reference
  python scripts/evaluate_reference.py --all                             # one line per run that held a course out
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
from profsagent.evaluate.reference import ENRICHED, evaluate_reference, load_reference, local_embed  # noqa: E402

COLS = [("topic_f1", "topic F1"), ("topic_soft_f1", "soft F1"), ("topic_coverage_recall", "covered"), ("topic_lexical_recall", "words"),
        ("order_tau_b", "order τb"), ("co_soft_f1", "CO soft F1"), ("co_rouge_l", "CO ROUGE-L"), ("assessment_tv", "assess TV"),
        ("prereq_jaccard", "prereq J"), ("resource_recall", "books")]


def finished(run_dir: Path) -> dict | None:
    f = run_dir / "state.json"
    if not f.exists():
        return None
    s = json.loads(f.read_text(encoding="utf-8"))
    return s if s.get("cos") and s.get("modules") else None


def held_out(s: dict) -> str | None:
    ex = [c.upper() for c in s.get("run_cfg", {}).get("exclude_courses", [])]
    return next((c for c in ex if (ENRICHED / f"{c}.json").exists()), None)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--course", help="reference course code (default: the course the run held out)")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    embed = local_embed()
    if a.run_id:
        s = finished(RUNS / a.run_id)
        if s is None:
            sys.exit(f"no finished design in runs/{a.run_id}")
        code = (a.course or held_out(s) or "").upper()
        if not code:
            sys.exit("the run held no course out; name a reference with --course")
        ev = evaluate_reference(s, load_reference(code), embed)
        out = RUNS / a.run_id / "evaluation_reference.json"
        out.write_text(json.dumps(ev, indent=1, ensure_ascii=False), encoding="utf-8")
        print(json.dumps(ev["summary"], indent=1, ensure_ascii=False))
        t = ev["topics"]
        print(f"topics: {t['matched']} of {t['reference']} reference topics matched, {t['design']} generated (sim ≥ {t['match_sim']})")
        print(f"missed: {t['missed_reference'][:10]}")
        print(f"wrote {out.relative_to(ROOT)}")
    elif a.all:
        print(f"{'run':<16} {'ref':<7} " + " ".join(f"{h:>10}" for _, h in COLS))
        for d in sorted(p for p in RUNS.iterdir() if p.is_dir()):
            s = finished(d)
            code = held_out(s) if s else None
            if not code:
                continue
            sm = evaluate_reference(s, load_reference(code), embed)["summary"]
            print(f"{d.name:<16} {code:<7} " + " ".join(f"{'-' if sm[k] is None else sm[k]:>10}" for k, _ in COLS))
    else:
        ap.error("give --run-id or --all")


if __name__ == "__main__":
    main()
