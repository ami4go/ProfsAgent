import yaml
import json
import subprocess
from pathlib import Path
import os
import time

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

def main():
    root = Path("c:/Users/parth/Downloads/ProfsAgent-main/ProfsAgent-main")
    base_input = root / "eval/inputs/CS-601.yaml"
    with open(base_input, "r") as f:
        base_yaml = yaml.safe_load(f)

    results = []
    
    for i, mut in enumerate(MUTATIONS):
        print(f"Running mutation {i+1}/{len(MUTATIONS)}: {mut['id']}")
        
        mut_yaml = yaml.safe_load(json.dumps(base_yaml)) # deep copy
        
        # Inject the defect into special constraints
        orig_constraints = mut_yaml["form"].get("13. SPECIAL CONSTRAINTS", "")
        mut_yaml["form"]["13. SPECIAL CONSTRAINTS"] = orig_constraints + "\n" + mut["prompt"]
        
        # Optionally disable external research to speed things up since we are testing validators
        mut_yaml["run"]["external_research"] = False
        
        mut_file = root / f"eval/inputs/CS-601-mut-{mut['id']}.yaml"
        with open(mut_file, "w") as f:
            yaml.dump(mut_yaml, f)
            
        run_id = f"benchmark-{mut['id']}"
        
        cmd = ["python", "scripts/run_design.py", "--input", str(mut_file), "--run-id", run_id, "--auto-approve"]
        print(f"Executing: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=str(root))
        
        state_file = root / "runs" / run_id / "state.json"
        
        detected = False
        violation_codes = []
        if state_file.exists():
            with open(state_file, "r", encoding="utf-8") as f:
                state = json.load(f)
                violations = state.get("violations", {})
                
                # Check if there are any error severity violations
                for v_list in violations.values():
                    for v in v_list:
                        if v.get("severity") == "error":
                            detected = True
                            violation_codes.append(v.get("code"))
                            
        results.append({
            "id": mut["id"],
            "prompt": mut["prompt"],
            "detected": detected,
            "violations": violation_codes
        })
        
        print(f"Result for {mut['id']}: Detected={detected}, Violations={violation_codes}")
        
    detected_count = sum(1 for r in results if r["detected"])
    dir_score = detected_count / len(MUTATIONS) if MUTATIONS else 0
    
    print(f"\n--- Benchmark Results ---")
    print(f"Total Mutations: {len(MUTATIONS)}")
    print(f"Detected: {detected_count}")
    print(f"DIR (Detected / Injected Ratio): {dir_score:.2f}")
    
    res_file = root / "defect_benchmark_results.json"
    with open(res_file, "w") as f:
        json.dump({
            "total": len(MUTATIONS),
            "detected": detected_count,
            "dir": dir_score,
            "details": results
        }, f, indent=2)
    print(f"Results saved to {res_file}")

if __name__ == '__main__':
    main()
