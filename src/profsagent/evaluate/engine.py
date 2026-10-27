"""Evaluation engine: the one entry point to evaluating a finished design, in three tiers. Run after the final render
(orchestrator/graph._render) and by `scripts/evaluate_design.py --all-tiers`.

    tier 1  deterministic.py  completeness, alignment, constraints, regulation, workload (no AI, always)
    tier 2  reference.py      the design against a real IIIT-D course sheet (local embeddings, no API calls). Runs when the
                              run names one (run.reference_course) or held one out (run.exclude_courses) and its sheet is
                              in data/enriched; otherwise skipped with the reason
    tier 3  judges.py         LLM judge panel. By default only PLANNED: the panel and the number of calls it would cost,
                              0 calls. Judged only when asked: run.judge: true in the input, or PROFSAGENT_JUDGE=1

Each tier is independent: one failing is reported and does not stop the others. Files written in the run folder:
evaluation_deterministic.json (tier 1, unchanged format), evaluation_reference.json (tier 2, when run),
evaluation_judges.json (tier 3 plan or scores) and evaluation.json (one summary of every tier and the overall verdict).
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Callable

from profsagent.evaluate import judges
from profsagent.evaluate.deterministic import evaluate as tier1
from profsagent.evaluate.reference import evaluate_reference, load_reference, reference_code


def judging_enabled(run_cfg: dict) -> bool:
    return bool(run_cfg.get("judge")) or os.environ.get("PROFSAGENT_JUDGE", "").lower() in ("1", "true", "yes", "on")


def _write(run_dir: Path, name: str, obj: dict) -> None:
    (run_dir / name).write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=str), encoding="utf-8")


def evaluate_run(state: dict, run_dir: Path, llm=None, *, embed: Callable | None = None, judge: bool | None = None,
                 log: Callable[[str], None] = print) -> dict:
    """All three tiers for one finished design. `embed` overrides the local model (tests); `judge` overrides
    judging_enabled(). Returns the evaluation.json summary."""
    run_dir = Path(run_dir)
    out: dict = {}

    try:
        ev = tier1(state)
        _write(run_dir, "evaluation_deterministic.json", ev)
        s = out["tier1"] = ev["summary"]
        log(f"evaluation (tier 1): {s['verdict']} · {s['errors']} errors · alignment min {s['alignment_min_pct']}% · "
            f"hard constraints satisfied {s['hard_constraints_satisfied_pct']}%")
    except Exception as e:  # noqa: BLE001 — each tier is reported on its own
        out["tier1"] = {"verdict": None, "error": f"{type(e).__name__}: {e}"[:300]}
        log(f"evaluation (tier 1) failed: {out['tier1']['error'][:160]}")
    verdict1 = out["tier1"].get("verdict")

    code = reference_code(state)
    if not code:
        named = (state.get("run_cfg") or {}).get("reference_course")
        out["tier2"] = {"status": "skipped", "reason": f"no sheet for reference course {named} in data/enriched" if named else
                        "no reference course (set run.reference_course to compare with a real sheet)"}
        log(f"evaluation (tier 2): skipped, {out['tier2']['reason']}")
    else:
        try:
            ev2 = evaluate_reference(state, load_reference(code), embed)
            _write(run_dir, "evaluation_reference.json", ev2)
            out["tier2"] = {"status": "done", "summary": ev2["summary"]}
            s2 = ev2["summary"]
            log(f"evaluation (tier 2): vs {code} · topic coverage {s2['topic_coverage_recall']} · CO soft F1 {s2['co_soft_f1']} · "
                f"assessment distance {s2['assessment_tv']}")
        except Exception as e:  # noqa: BLE001
            out["tier2"] = {"status": "failed", "reference": code, "error": f"{type(e).__name__}: {e}"[:300]}
            log(f"evaluation (tier 2) failed: {out['tier2']['error'][:160]}")

    run_judges = judging_enabled(state.get("run_cfg") or {}) if judge is None else judge
    try:
        if run_judges:
            judged = judges.evaluate_judges(state, llm, tier1_verdict=verdict1, run_id=run_dir.name)
            _write(run_dir, "evaluation_judges.json", judged)
            out["tier3"] = {"status": "judged" if judged.get("summary") else "skipped", "calls": judged.get("calls", 0),
                            "summary": judged.get("summary"), "reason": judged.get("skipped")}
            out["verdict"] = judges.combined_verdict(verdict1, judged)
        else:
            plan = judges.plan(state, llm, verdict1)
            _write(run_dir, "evaluation_judges.json", {"planned_only": True, **plan})
            out["tier3"] = {"status": "planned", "calls": 0, "would_cost_calls": [plan["calls_min"], plan["calls_max"]],
                            "panel": [p["judge"] for p in plan["panel"]],
                            "reason": "judging is off (run.judge: true or PROFSAGENT_JUDGE=1 to run the panel)"}
    except Exception as e:  # noqa: BLE001
        out["tier3"] = {"status": "failed", "calls": 0, "error": f"{type(e).__name__}: {e}"[:300]}
    t3 = out["tier3"]
    log(f"evaluation (tier 3): {t3['status']}"
        + (f" · panel {t3['panel']} would cost {t3['would_cost_calls'][0]}–{t3['would_cost_calls'][1]} calls" if t3["status"] == "planned" else "")
        + (f" · {t3['summary']['band']} (mean {t3['summary']['mean']})" if t3.get("summary") else "")
        + (f" · {t3.get('error', '')[:120]}" if t3["status"] == "failed" else ""))

    out.setdefault("verdict", {"verdict": verdict1, "reasons": ["tiers 1–2 only; the judge panel (tier 3) did not run"]})
    _write(run_dir, "evaluation.json", out)
    return out
