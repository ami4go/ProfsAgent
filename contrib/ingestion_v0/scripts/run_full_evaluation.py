"""
Master Evaluation Runner for ProfsAgent.

Orchestrates the complete evaluation pipeline:
  1. Claim C2 — Defect Injection Benchmark (code validators vs LLM reviewer)
  2. Claims C1/C2/C3 — Ablation Study (No-KG, No-Validators, No-Scheduler)
  3. Combined publication-ready JSON report

Usage:
    python -m scripts.run_full_evaluation
"""

import json
import math
from pathlib import Path
from typing import Any

from profsagent.validate.ablation_study import AblationStudy
from profsagent.validate.defect_injector import DefectCategory, DefectInjector
from profsagent.validate.deterministic import DeterministicValidator
from profsagent.validate.llm_reviewer import LLMReviewer
from profsagent.models.schema import (
    AssessmentComponent,
    AssessmentType,
    CourseHeader,
    CourseOutcome,
    ParsedCourse,
    WeekPlanItem,
)


def compute_wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float, float]:
    """Wilson score 95% confidence interval for a binomial proportion."""
    if n == 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denom = 1 + (z ** 2) / n
    centre = (p + (z ** 2) / (2 * n)) / denom
    spread = (z * math.sqrt((p * (1 - p) / n) + (z ** 2) / (4 * (n ** 2)))) / denom
    lower = max(0.0, round(centre - spread, 3))
    upper = min(1.0, round(centre + spread, 3))
    return round(p, 3), lower, upper


def build_clean_base_courses() -> list[dict[str, Any]]:
    """Constructs 4 representative, clean IIIT-D base courses."""
    return [
        {
            "id": "CSE101", "name": "Introduction to Programming", "credits": 4,
            "cos": [
                {"id": "CO1", "statement": "Formulate algorithmic solutions using Python to solve computational tasks.", "verb": "formulate", "bloom_level": 3, "condition": "using Python", "degree": "to solve computational tasks"},
                {"id": "CO2", "statement": "Implement modular code applying functions to minimize code duplication.", "verb": "implement", "bloom_level": 3, "condition": "applying functions", "degree": "to minimize code duplication"},
                {"id": "CO3", "statement": "Debug syntax errors using unit testing to achieve clean execution.", "verb": "debug", "bloom_level": 4, "condition": "using unit testing", "degree": "to achieve clean execution"},
                {"id": "CO4", "statement": "Apply data structures including dictionaries to organize records.", "verb": "apply", "bloom_level": 3, "condition": "including dictionaries", "degree": "to organize records"},
            ],
            "assessments": [
                {"id": "A1", "name": "Midsem", "weight_pct": 25.0, "week": 7, "mapped_los": ["LO1.1"]},
                {"id": "A2", "name": "Endsem", "weight_pct": 35.0, "week": 14, "mapped_los": ["LO1.2"]},
                {"id": "A3", "name": "Assignments", "weight_pct": 25.0, "week": 10, "mapped_los": ["LO1.1", "LO1.2"]},
                {"id": "A4", "name": "Quizzes", "weight_pct": 15.0, "week": 5, "mapped_los": ["LO1.1"]},
            ],
            "topics": [
                {"id": "T1", "name": "Control Flow and Loops", "hours": 3.0, "week": 2},
                {"id": "T2", "name": "Functions and Recursion", "hours": 3.0, "week": 4},
                {"id": "T3", "name": "Lists and Dictionaries", "hours": 3.0, "week": 6},
                {"id": "T4", "name": "File Handling and Exceptions", "hours": 3.0, "week": 9},
            ],
            "los": [
                {"id": "LO1.1", "co_id": "CO1", "statement": "Trace loop iterations.", "verb": "trace", "bloom_level": 2},
                {"id": "LO1.2", "co_id": "CO2", "statement": "Write functions with parameters.", "verb": "write", "bloom_level": 3},
            ],
        },
        {
            "id": "CSE201", "name": "Advanced Programming", "credits": 4,
            "cos": [
                {"id": "CO1", "statement": "Design object-oriented software applying inheritance to achieve reusability.", "verb": "design", "bloom_level": 6, "condition": "applying inheritance", "degree": "to achieve reusability"},
                {"id": "CO2", "statement": "Implement thread synchronization using semaphores to prevent race conditions.", "verb": "implement", "bloom_level": 3, "condition": "using semaphores", "degree": "to prevent race conditions"},
                {"id": "CO3", "statement": "Analyze asymptotic complexity using Big-O notation to evaluate scalability.", "verb": "analyze", "bloom_level": 4, "condition": "using Big-O notation", "degree": "to evaluate scalability"},
                {"id": "CO4", "statement": "Test application components using JUnit to satisfy edge case criteria.", "verb": "test", "bloom_level": 5, "condition": "using JUnit", "degree": "to satisfy edge case criteria"},
            ],
            "assessments": [
                {"id": "A1", "name": "Midsem", "weight_pct": 25.0, "week": 7, "mapped_los": ["LO2.1"]},
                {"id": "A2", "name": "Endsem", "weight_pct": 35.0, "week": 14, "mapped_los": ["LO2.2"]},
                {"id": "A3", "name": "Project", "weight_pct": 20.0, "week": 12, "mapped_los": ["LO2.1", "LO2.2"]},
                {"id": "A4", "name": "Quizzes", "weight_pct": 20.0, "week": 4, "mapped_los": ["LO2.1"]},
            ],
            "topics": [
                {"id": "T1", "name": "Object-Oriented Design", "hours": 3.0, "week": 1},
                {"id": "T2", "name": "Polymorphism and Interfaces", "hours": 3.0, "week": 3},
                {"id": "T3", "name": "Concurrency and Synchronization", "hours": 3.0, "week": 8},
                {"id": "T4", "name": "Design Patterns", "hours": 3.0, "week": 11},
            ],
            "los": [
                {"id": "LO2.1", "co_id": "CO1", "statement": "Construct class hierarchies.", "verb": "construct", "bloom_level": 3},
                {"id": "LO2.2", "co_id": "CO2", "statement": "Acquire mutex locks properly.", "verb": "acquire", "bloom_level": 3},
            ],
        },
        {
            "id": "CSE222", "name": "Data Structures and Algorithms", "credits": 4,
            "cos": [
                {"id": "CO1", "statement": "Analyze time and space complexity using recurrences to classify efficiency.", "verb": "analyze", "bloom_level": 4, "condition": "using recurrences", "degree": "to classify efficiency"},
                {"id": "CO2", "statement": "Design divide-and-conquer algorithms to solve sorting and searching problems.", "verb": "design", "bloom_level": 6, "condition": "using divide-and-conquer", "degree": "to solve sorting problems"},
                {"id": "CO3", "statement": "Implement balanced search trees using pointers to maintain logarithmic depth.", "verb": "implement", "bloom_level": 3, "condition": "using pointers", "degree": "to maintain logarithmic depth"},
                {"id": "CO4", "statement": "Evaluate graph shortest path algorithms to identify optimal network routes.", "verb": "evaluate", "bloom_level": 5, "condition": "using Dijkstra's algorithm", "degree": "to identify optimal routes"},
            ],
            "assessments": [
                {"id": "A1", "name": "Midsem", "weight_pct": 25.0, "week": 7, "mapped_los": ["LO3.1"]},
                {"id": "A2", "name": "Endsem", "weight_pct": 35.0, "week": 14, "mapped_los": ["LO3.2"]},
                {"id": "A3", "name": "Assignments", "weight_pct": 25.0, "week": 9, "mapped_los": ["LO3.1", "LO3.2"]},
                {"id": "A4", "name": "Quizzes", "weight_pct": 15.0, "week": 4, "mapped_los": ["LO3.1"]},
            ],
            "topics": [
                {"id": "T1", "name": "Asymptotic Analysis", "hours": 3.0, "week": 1},
                {"id": "T2", "name": "Heaps and Priority Queues", "hours": 3.0, "week": 4},
                {"id": "T3", "name": "Graph Traversals (BFS/DFS)", "hours": 3.0, "week": 7},
                {"id": "T4", "name": "Dynamic Programming", "hours": 3.0, "week": 10},
            ],
            "los": [
                {"id": "LO3.1", "co_id": "CO1", "statement": "Solve recurrence relations.", "verb": "solve", "bloom_level": 3},
                {"id": "LO3.2", "co_id": "CO3", "statement": "Rotate AVL tree nodes.", "verb": "rotate", "bloom_level": 3},
            ],
        },
        {
            "id": "CSE231", "name": "Operating Systems", "credits": 4,
            "cos": [
                {"id": "CO1", "statement": "Analyze process scheduling policies using simulation to evaluate throughput.", "verb": "analyze", "bloom_level": 4, "condition": "using simulation", "degree": "to evaluate throughput"},
                {"id": "CO2", "statement": "Design deadlock avoidance mechanisms applying Banker's algorithm to ensure safety.", "verb": "design", "bloom_level": 6, "condition": "applying Banker's algorithm", "degree": "to ensure safety"},
                {"id": "CO3", "statement": "Implement virtual memory page replacement to minimize page fault rates.", "verb": "implement", "bloom_level": 3, "condition": "using LRU policy", "degree": "to minimize page faults"},
                {"id": "CO4", "statement": "Evaluate file system directory structures to measure disk lookup latency.", "verb": "evaluate", "bloom_level": 5, "condition": "using indexed allocation", "degree": "to measure latency"},
            ],
            "assessments": [
                {"id": "A1", "name": "Midsem", "weight_pct": 25.0, "week": 7, "mapped_los": ["LO4.1"]},
                {"id": "A2", "name": "Endsem", "weight_pct": 35.0, "week": 14, "mapped_los": ["LO4.2"]},
                {"id": "A3", "name": "Labs & Projects", "weight_pct": 25.0, "week": 12, "mapped_los": ["LO4.1", "LO4.2"]},
                {"id": "A4", "name": "Quizzes", "weight_pct": 15.0, "week": 5, "mapped_los": ["LO4.1"]},
            ],
            "topics": [
                {"id": "T1", "name": "Processes and System Calls", "hours": 3.0, "week": 1},
                {"id": "T2", "name": "CPU Scheduling Algorithms", "hours": 3.0, "week": 3},
                {"id": "T3", "name": "Virtual Memory and Paging", "hours": 3.0, "week": 9},
                {"id": "T4", "name": "File Systems and I/O", "hours": 3.0, "week": 12},
            ],
            "los": [
                {"id": "LO4.1", "co_id": "CO1", "statement": "Calculate turnaround time.", "verb": "calculate", "bloom_level": 3},
                {"id": "LO4.2", "co_id": "CO3", "statement": "Trace page fault traps.", "verb": "trace", "bloom_level": 2},
            ],
        },
    ]


def convert_state_to_parsed_course(s: dict[str, Any]) -> ParsedCourse:
    """Converts a dict course state to ParsedCourse for validator execution."""
    header = CourseHeader(
        course_code=s.get("id", "CSE"),
        course_title=s.get("name", "Course"),
        credits=s.get("credits", 4),
    )
    cos = [
        CourseOutcome(
            co_id=c["id"], description=c.get("statement", ""),
            action_verb=c.get("verb", "apply"),
            bloom_level=c.get("bloom_level", 3),
            condition=c.get("condition", ""),
            degree=c.get("degree", ""),
        )
        for c in s.get("cos", [])
    ]
    assessments = [
        AssessmentComponent(
            name=a.get("name", a["id"]),
            assessment_type=(
                AssessmentType.MIDSEM if "mid" in a.get("name", "").lower()
                else AssessmentType.ENDSEM if "end" in a.get("name", "").lower()
                else AssessmentType.QUIZ if "quiz" in a.get("name", "").lower()
                else AssessmentType.ASSIGNMENT if "assign" in a.get("name", "").lower()
                else AssessmentType.PROJECT if "project" in a.get("name", "").lower()
                else AssessmentType.OTHER
            ),
            weight_percentage=float(a.get("weight_pct", 25.0)),
            scheduled_week=a.get("week"),
            mapped_cos=[c.co_id for c in cos],
            mapped_los=a.get("mapped_los", []),
        )
        for a in s.get("assessments", [])
    ]
    weeks = [WeekPlanItem(week_number=i, topic_summary=f"Topic {i}") for i in range(1, 15)]

    return ParsedCourse(header=header, course_outcomes=cos, weekly_plans=weeks, assessments=assessments)


def run_defect_benchmark(base_courses: list[dict[str, Any]]) -> dict[str, Any]:
    """Phase 1: Defect injection benchmark for Claim C2."""
    print("\n" + "=" * 70)
    print("  PHASE 1: Defect-Injection Benchmark (Claim C2)")
    print("=" * 70)

    injector = DefectInjector()
    validator = DeterministicValidator()
    reviewer = LLMReviewer()

    # 1. False Positive Rate on clean courses
    print("\n[FPR Test] Evaluating false positive rate on clean courses...")
    code_fps = 0
    llm_fps = 0

    for c in base_courses:
        parsed = convert_state_to_parsed_course(c)
        report = validator.validate_course(parsed)
        if len(report.violations) > 0:
            code_fps += 1
        llm_findings = reviewer.review_course_state(c)
        if len(llm_findings) > 0:
            llm_fps += 1

    code_fpr = round(code_fps / len(base_courses), 3)
    llm_fpr = round(llm_fps / len(base_courses), 3)
    print(f"  Deterministic Validators FPR: {code_fpr * 100}%")
    print(f"  LLM Reviewer FPR:             {llm_fpr * 100}%")

    # 2. Generate mutations
    print("\n[Mutation] Generating defect mutations...")
    mutations = injector.generate_full_mutation_suite(base_courses)
    print(f"  Generated {len(mutations)} mutations across 4 base courses")

    # 3. Benchmark
    category_stats: dict[DefectCategory, dict[str, Any]] = {
        cat: {"total": 0, "code_caught": 0, "llm_caught": 0}
        for cat in DefectCategory
    }

    for mut in mutations:
        cat = mut.defect.category
        category_stats[cat]["total"] += 1

        parsed_mut = convert_state_to_parsed_course(mut.course_state)
        report = validator.validate_course(parsed_mut)

        code_detected = False
        if not mut.defect.uncaught_by_design:
            if len(report.violations) > 0:
                code_detected = True

        if code_detected:
            category_stats[cat]["code_caught"] += 1

        llm_findings = reviewer.review_course_state(mut.course_state)
        llm_detected = reviewer.check_if_defect_caught(llm_findings, mut.defect)
        if llm_detected:
            category_stats[cat]["llm_caught"] += 1

    # 4. Results
    print("\n  Category-Wise Recall:")
    print(f"  {'Category':<30} {'N':>4}  {'Code Recall':>14}  {'LLM Recall':>14}  {'Δ':>8}")
    print("  " + "-" * 78)

    results_data = []
    total_code = sum(s["code_caught"] for s in category_stats.values())
    total_llm = sum(s["llm_caught"] for s in category_stats.values())

    for cat, stats in category_stats.items():
        n = stats["total"]
        k_code = stats["code_caught"]
        k_llm = stats["llm_caught"]
        p_code, low_c, high_c = compute_wilson_ci(k_code, n)
        p_llm, low_l, high_l = compute_wilson_ci(k_llm, n)
        delta = round(p_code - p_llm, 3)

        print(f"  {cat.value:<30} {n:>4}  {p_code*100:>5.1f}% [{low_c*100:>3.0f}%,{high_c*100:>3.0f}%]"
              f"  {p_llm*100:>5.1f}% [{low_l*100:>3.0f}%,{high_l*100:>3.0f}%]"
              f"  {'+' if delta > 0 else ''}{delta*100:.1f}%")

        results_data.append({
            "category": cat.value, "n": n,
            "code_recall": p_code, "code_ci": [low_c, high_c],
            "llm_recall": p_llm, "llm_ci": [low_l, high_l],
            "delta": delta,
        })

    overall_p_code, _, _ = compute_wilson_ci(total_code, len(mutations))
    overall_p_llm, _, _ = compute_wilson_ci(total_llm, len(mutations))

    print(f"\n  Overall Code Recall:  {overall_p_code*100:.1f}%")
    print(f"  Overall LLM Recall:   {overall_p_llm*100:.1f}%")
    print(f"  C2 Advantage:         +{(overall_p_code - overall_p_llm)*100:.1f}%")

    return {
        "total_injected": len(mutations),
        "false_positive_rates": {"code": code_fpr, "llm": llm_fpr},
        "overall_code_recall": overall_p_code,
        "overall_llm_recall": overall_p_llm,
        "c2_advantage": round(overall_p_code - overall_p_llm, 3),
        "categories": results_data,
    }


def run_ablation_study(base_courses: list[dict[str, Any]]) -> dict[str, Any]:
    """Phase 2: Ablation study for Claims C1, C2, C3."""
    print("\n" + "=" * 70)
    print("  PHASE 2: Ablation Study (Claims C1, C2, C3)")
    print("=" * 70)

    study = AblationStudy()
    results = study.run_all_ablations(base_courses)
    report = study.generate_report(results)

    for entry in report["ablation_study"]:
        print(f"\n  [{entry['claim']}] Condition: {entry['condition']}")
        print(f"    Courses tested: {entry['num_courses']}")
        print(f"    Metric Deltas (Control - Treatment):")
        for metric, delta in entry["metric_deltas"].items():
            effect = entry["effect_sizes"].get(metric, 0)
            size_label = "large" if abs(effect) >= 0.8 else "medium" if abs(effect) >= 0.5 else "small" if abs(effect) >= 0.2 else "negligible"
            print(f"      {metric:<30} Δ = {delta:>+8.4f}  (d = {effect:>6.3f}, {size_label})")
        print(f"    Interpretation: {entry['interpretation']}")

    return report


def main():
    """Run the complete ProfsAgent evaluation pipeline."""
    print("\n" + "█" * 70)
    print("  ProfsAgent — Complete Evaluation Pipeline")
    print("  Testing Claims C1 (Grounding), C2 (Verification), C3 (Feasibility)")
    print("█" * 70)

    base_courses = build_clean_base_courses()

    # Phase 1: Defect injection benchmark
    c2_results = run_defect_benchmark(base_courses)

    # Phase 2: Ablation study
    ablation_results = run_ablation_study(base_courses)

    # Combined report
    combined_report = {
        "evaluation_framework": "ProfsAgent v1.0",
        "claims_tested": ["C1_Grounding", "C2_Verification", "C3_Feasibility"],
        "phase_1_defect_benchmark": c2_results,
        "phase_2_ablation_study": ablation_results,
    }

    out_file = Path("data") / "full_evaluation_results.json"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(combined_report, indent=2, default=str), encoding="utf-8")

    print("\n" + "=" * 70)
    print(f"  ✓ Complete evaluation report saved to: {out_file}")
    print("=" * 70)

    return combined_report


if __name__ == "__main__":
    main()
