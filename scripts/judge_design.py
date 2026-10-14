"""Evaluation tier 3: the LLM judge panel (config/judging.yaml, prompts J1/J2). DRY RUN unless --run is given: it
prints the panel, the judges skipped and why, the prompt size and how many calls a real run would make.

  python scripts/judge_design.py --run-id cs601-02                    # plan only, no API calls
  python scripts/judge_design.py --run-id cs601-02 --run              # judge (1-3 calls); writes evaluation_judges.json
  python scripts/judge_design.py --run-id cs601-02 --run --force      # judge even when Tier 1 fails
  python scripts/judge_design.py --compare cse201-dev-04 cse201-dev-05 --judge judge_a --run   # pairwise, 2 calls
  python scripts/judge_design.py --summary                            # saved judge reports: scores, agreement, length bias
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
from profsagent.evaluate import judges  # noqa: E402
from profsagent.evaluate.agreement import length_bias  # noqa: E402
from profsagent.evaluate.deterministic import evaluate  # noqa: E402

OUT = "evaluation_judges.json"


def load(run_id: str) -> dict:
    f = RUNS / run_id / "state.json"
    if not f.exists():
        sys.exit(f"no runs/{run_id}/state.json")
    return json.loads(f.read_text(encoding="utf-8"))


def client(run_id: str):
    from profsagent.llm.client import LLMClient
    return LLMClient(RUNS / run_id / "llm_calls.jsonl")


def one(a) -> None:
    s = load(a.run_id)
    tier1 = evaluate(s)["summary"]["verdict"]
    llm = client(a.run_id)
    p = judges.plan(s, llm, tier1, force=a.force, cascade=not a.no_cascade)
    print(f"Tier 1: {tier1} | panel: {[x['judge'] + ' ' + x['model'] for x in p['panel']]}")
    for x in p["skipped_judges"]:
        print(f"  skipped {x['judge']} ({x['model']}): {x['why']}")
    print(f"prompt ≈ {p['prompt_tokens_est']} tokens | calls: {p['calls_min']}–{p['calls_max']}"
          + ("" if p["judged"] else " (not judged: Tier 1 must pass first, or use --force)"))
    if not a.run:
        print("dry run: nothing was sent. Add --run to judge.")
        return
    rep = judges.evaluate_judges(s, llm, tier1_verdict=tier1, force=a.force, cascade=not a.no_cascade, run_id=a.run_id)
    rep["combined"] = judges.combined_verdict(tier1, rep)
    rep["tier1"] = tier1
    (RUNS / a.run_id / OUT).write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    if rep.get("summary"):
        for d, x in rep["dimensions"].items():
            print(f"  {x['name']:<26} median {x['median']}  scores {x['scores']}" + ("  DISAGREE" if x["disagreement"] else ""))
        print(f"band: {rep['summary']['band']} (mean {rep['summary']['mean']}) | agreement: {rep.get('agreement')}")
    print(f"combined verdict: {rep['combined']['verdict']} {rep['combined']['reasons']} | calls made: {rep['calls']}")
    print(f"wrote runs/{a.run_id}/{OUT}")


def pair(a) -> None:
    ra, rb = a.compare
    sa, sb = load(ra), load(rb)
    print(f"pairwise {ra} (A) vs {rb} (B) with {a.judge} ({judges.judge_model(a.judge)}): 2 calls, both orders")
    if sa.get("form") != sb.get("form"):
        print("  note: the two runs had different briefs; the brief of A is shown")
    if not a.run:
        print("dry run: nothing was sent. Add --run to compare.")
        return
    rep = judges.compare(sa, sb, client(ra), a.judge, run_id=ra)
    for d, x in rep["dimensions"].items():
        print(f"  {d:<20} A-first: {x['order_ab']}  B-first: {x['order_ba']}  -> {x['winner']}")
    print(f"wins {rep['wins']} | position consistency {rep['position_consistency']}")
    out = RUNS / ra / f"comparison_{rb}.json"
    out.write_text(json.dumps(rep, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}")


def summary() -> None:
    rows = []
    for d in sorted(p for p in RUNS.iterdir() if (p / OUT).exists()):
        rep = json.loads((d / OUT).read_text(encoding="utf-8"))
        s = rep.get("summary")
        if s:
            rows.append((d.name, s["mean"], s["band"], s["design_chars"], (rep.get("agreement") or {}).get("krippendorff_alpha_interval")))
            print(f"{d.name:<34} mean {s['mean']}  {s['band']:<10} α {rows[-1][4]}  design {s['design_chars']} chars")
    print(f"length bias (Spearman, design length vs mean score): {length_bias([r[3] for r in rows], [r[1] for r in rows])} "
          f"over {len(rows)} judged runs (needs ≥ 4)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id")
    ap.add_argument("--compare", nargs=2, metavar=("RUN_A", "RUN_B"))
    ap.add_argument("--judge", default="judge_a")
    ap.add_argument("--summary", action="store_true")
    ap.add_argument("--run", action="store_true", help="actually call the judges (spends API quota)")
    ap.add_argument("--force", action="store_true", help="judge even when Tier 1 fails")
    ap.add_argument("--no-cascade", action="store_true", help="always use the whole panel")
    a = ap.parse_args()
    if a.run_id:
        one(a)
    elif a.compare:
        pair(a)
    elif a.summary:
        summary()
    else:
        ap.error("give --run-id, --compare or --summary")


if __name__ == "__main__":
    main()
