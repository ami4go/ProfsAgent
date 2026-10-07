"""CS-601 defect-injection benchmark: run the design pipeline on mutated professor forms.

  python scripts/run_defect_benchmark.py            # run every pending mutation + the control, resumable
  python scripts/run_defect_benchmark.py --status   # show done / pending / failed

Each mutation appends a "CRITICAL: ..." instruction to form field 13 of eval/inputs/CS-601.yaml and turns external
research off. The "control" run does the same with no instruction, so errors caused by research-off are not
mistaken for detections. Runs that already have proposal.md are skipped; a run stopped by this script is continued
from its checkpoint; the batch stops at the first quota failure so remaining runs are not wasted.
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _s in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252
    _s.reconfigure(encoding="utf-8", errors="replace")
BASE_INPUT = ROOT / "eval/inputs/CS-601.yaml"
RUNS = ROOT / "runs"
STATUS_FILE = RUNS / "benchmark_status.json"
STALLED = RUNS / "_stalled_2026-09-30"
MARKER = ".benchmark_v2"   # written into run dirs started by this version of the script
SC_LINE = '"13. SPECIAL CONSTRAINTS": "[NONE]"'
QUOTA_MARKERS = ("AllEndpointsFailed", "exceeded your current quota", "RESOURCE_EXHAUSTED")

MUTATIONS = [
    {"id": "inv_assess_weights", "prompt": "CRITICAL: The assessment weights must sum to exactly 130%."},
    {"id": "banned_verbs", "prompt": "CRITICAL: You must use the exact verb 'understand' for all Course Outcomes."},
    {"id": "bloom_inconsistencies", "prompt": "CRITICAL: Set all Course Outcomes to Bloom Level 1, but assess them only with open-ended design projects (Bloom 6)."},
    {"id": "orphan_los", "prompt": "CRITICAL: Create 3 Learning Outcomes that have no parent CO (set parent_co to 'NONE')."},
    {"id": "invalid_lo_assess", "prompt": "CRITICAL: Map all assessments to LOs with IDs like 'LO_FAKE_1' that do not exist."},
    {"id": "assess_before_teach", "prompt": "CRITICAL: The final exam must be scheduled in week 2, covering topics from week 14."},
    {"id": "temporal_inversions", "prompt": "CRITICAL: Topics in week 4 must require/depend on topics that are only taught in week 8."},
    {"id": "invalid_prereqs", "prompt": "CRITICAL: List exactly 'NONEXISTENT101' as a mandatory prerequisite course."},
    {"id": "impossible_hours", "prompt": "CRITICAL: The course must have 300 lecture hours in a single semester."},
    {"id": "contradictory_constraints", "prompt": "CRITICAL: The course must have exactly 5 Course Outcomes. Also, the course must have exactly 12 Course Outcomes."},
    {"id": "invalid_week_counts", "prompt": "CRITICAL: Set the semester length to exactly 50 weeks."},
    {"id": "malformed_copo", "prompt": "CRITICAL: Map all COs to a Programme Outcome called 'PO_MAGIC' which does not exist."},
    {"id": "duplicate_outcomes", "prompt": "CRITICAL: Create two Course Outcomes with exactly the same verb and behaviour text."},
    {"id": "missing_assessment", "prompt": "CRITICAL: Do not include any assessment components. The assessment list must be empty."},
    {"id": "no_lectures", "prompt": "CRITICAL: The course must have exactly 0 lecture hours."},
    {"id": "vague_degree", "prompt": "CRITICAL: For all LOs, use the exact degree string 'thoroughly' or 'deeply'."},
    {"id": "cyclic_lo_deps", "prompt": "CRITICAL: Make LO 1 require LO 2, and LO 2 require LO 1 (dependency cycle)."},
    {"id": "excessive_cos", "prompt": "CRITICAL: Create exactly 15 Course Outcomes."},
    {"id": "excessive_los", "prompt": "CRITICAL: Create exactly 15 Learning Outcomes for the first Course Outcome."},
    {"id": "no_topics", "prompt": "CRITICAL: Do not include any topics or topic groups in the course."}
]

def write_input(mut_id, prompt):
    """Text substitution on the base form (keeps its formatting and comments); written as UTF-8.
    Field 13 becomes "[NONE]\n<prompt>", the same value the 2026-09-30 runs received."""
    with open(BASE_INPUT, encoding="utf-8", newline="") as f:   # keep the base file's line endings
        text = f.read()
    assert SC_LINE in text and "external_research: true" in text, "CS-601.yaml changed; update write_input()"
    if prompt:
        text = text.replace(SC_LINE, '"13. SPECIAL CONSTRAINTS": ' + json.dumps("[NONE]\n" + prompt, ensure_ascii=False))
    text = text.replace("external_research: true", "external_research: false")
    out = ROOT / f"eval/inputs/CS-601-mut-{mut_id}.yaml"
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return out


def is_done(run_dir):
    return (run_dir / "proposal.md").exists()


def score(state_file):
    """v1 scoring, unchanged: detected = the final state has any error-severity violation."""
    detected, violation_codes = False, []
    if state_file.exists():
        state = json.loads(state_file.read_text(encoding="utf-8"))
        for v_list in state.get("violations", {}).values():
            for v in v_list:
                if v.get("severity") == "error":
                    detected = True
                    violation_codes.append(v.get("code"))
    return detected, violation_codes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true", help="print run status and exit")
    a = ap.parse_args()

    plan = [{"id": "control", "prompt": None}] + MUTATIONS
    status = json.loads(STATUS_FILE.read_text(encoding="utf-8")) if STATUS_FILE.exists() else {}

    if a.status:
        for mut in plan:
            rd = RUNS / f"benchmark-{mut['id']}"
            print(f"{mut['id']:28} {'done' if is_done(rd) else status.get(mut['id'], {}).get('state', 'pending')}")
        return

    for i, mut in enumerate(plan):
        run_id = f"benchmark-{mut['id']}"
        run_dir = RUNS / run_id
        if is_done(run_dir):
            print(f"[{i}/{len(MUTATIONS)}] {mut['id']}: done, skipping")
            continue
        # partial runs left by the 2026-09-30 batch were started from mis-encoded inputs: move them aside, start fresh
        if run_dir.exists() and not (run_dir / MARKER).exists():
            STALLED.mkdir(exist_ok=True)
            shutil.move(str(run_dir), str(STALLED / run_dir.name))
            print(f"[{i}/{len(MUTATIONS)}] {mut['id']}: moved stalled 2026-09-30 run to runs/{STALLED.name}/")
        resume = run_dir.exists() and (run_dir / "state.json").exists()
        cmd = [sys.executable, "scripts/run_design.py", "--run-id", run_id, "--auto-approve"]
        if resume:
            cmd.append("--continue")
        else:
            cmd += ["--input", str(write_input(mut["id"], mut["prompt"]).relative_to(ROOT))]
        run_dir.mkdir(parents=True, exist_ok=True)
        (run_dir / MARKER).touch()
        print(f"[{i}/{len(MUTATIONS)}] {mut['id']}: {'continue' if resume else 'start'}", flush=True)
        t0 = time.time()
        with open(run_dir / "benchmark_stdout.log", "a", encoding="utf-8") as log:
            p = subprocess.run(cmd, cwd=str(ROOT), stdout=log, stderr=subprocess.STDOUT)
        tail = (run_dir / "benchmark_stdout.log").read_text(encoding="utf-8", errors="replace")[-3000:]
        ok = p.returncode == 0 and is_done(run_dir)
        status[mut["id"]] = {"state": "done" if ok else "failed", "exit_code": p.returncode,
                             "minutes": round((time.time() - t0) / 60, 1), "error_tail": None if ok else tail[-600:]}
        STATUS_FILE.write_text(json.dumps(status, indent=1), encoding="utf-8")
        print(f"    {'DONE' if ok else 'FAILED'} in {status[mut['id']]['minutes']} min", flush=True)
        if not ok and any(k in tail for k in QUOTA_MARKERS):
            print("API quota exhausted: stopping. Re-run this script later; finished runs are kept.")
            break

    pending = [m["id"] for m in plan if not is_done(RUNS / f"benchmark-{m['id']}")]
    if pending:
        print(f"\n{len(pending)} runs not finished yet: {pending}\nResults file is written once every run is done.")
        return

    results = []
    for mut in MUTATIONS:
        detected, codes = score(RUNS / f"benchmark-{mut['id']}" / "state.json")
        results.append({"id": mut["id"], "prompt": mut["prompt"], "detected": detected, "violations": codes})
        print(f"Result for {mut['id']}: Detected={detected}, Violations={codes}")
    control_detected, control_codes = score(RUNS / "benchmark-control" / "state.json")
    detected_count = sum(1 for r in results if r["detected"])
    dir_score = detected_count / len(MUTATIONS) if MUTATIONS else 0

    print("\n--- Benchmark Results ---")
    print(f"Total Mutations: {len(MUTATIONS)}")
    print(f"Detected: {detected_count}")
    print(f"DIR (Detected / Injected Ratio): {dir_score:.2f}")
    print(f"Control (no mutation) errors: {control_codes}")

    res_file = ROOT / "defect_benchmark_results.json"
    res_file.write_text(json.dumps({
        "total": len(MUTATIONS),
        "detected": detected_count,
        "dir": dir_score,
        "control": {"detected": control_detected, "violations": control_codes},
        "details": results
    }, indent=2), encoding="utf-8")
    print(f"Results saved to {res_file}")


if __name__ == '__main__':
    main()
