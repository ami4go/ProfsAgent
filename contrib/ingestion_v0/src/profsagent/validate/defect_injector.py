"""
Defect Injection Engine for ProfsAgent (Testing Claim C2 & Validator Sensitivity).

Generates grounded, parameterized mutations across 5 distinct categories:
- Category A: Empirical Gem Audit Defects (from CS146S / CSE201 runs)
- Category B: Arithmetic & Feasibility Violations (Budget, Hours, Weights)
- Category C: Temporal Causality & Scheduling Inversions
- Category D: Traceability & Constructive Alignment (Orphans, Under-testing)
- Category E: Uncaught Semantic Flaws (The Validator Blindspots)

Outputs both mutated course states and an exact ground-truth manifest
for computing category-wise recall with confidence intervals and false-positive rates.
"""

from copy import deepcopy
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class DefectCategory(str, Enum):
    A_EMPIRICAL_GEM = "A_EMPIRICAL_GEM"             # Real flaws from baseline audits
    B_ARITHMETIC_HOURS = "B_ARITHMETIC_HOURS"       # Numerical budget/feasibility errors
    C_TEMPORAL_CAUSALITY = "C_TEMPORAL_CAUSALITY"   # Sequence and causality inversions
    D_TRACEABILITY = "D_TRACEABILITY"               # Constructive alignment & orphan nodes
    E_UNCAUGHT_SEMANTIC = "E_UNCAUGHT_SEMANTIC"     # Subtle semantic flaws (Validator Blindspots)


@dataclass
class InjectedDefect:
    """Ground-truth metadata for a single injected flaw."""
    defect_id: str
    category: DefectCategory
    name: str
    target_node_id: str
    expected_rule_code: str | None  # None for Category E (deliberate blindspots)
    description: str
    original_value: Any
    mutated_value: Any
    uncaught_by_design: bool = False


@dataclass
class MutatedCourseResult:
    """A course state with a known injected defect and its manifest."""
    base_course_id: str
    course_state: dict[str, Any]
    defect: InjectedDefect


class DefectInjector:
    """Generates parameterized mutations from clean base course states."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed

    # =================================================================
    # Category A: Real Gem Audit Defects (CS146S / CSE201)
    # =================================================================

    def inject_a1_vacuous_degree(self, state: dict[str, Any]) -> MutatedCourseResult:
        """Injects a vacuous degree that passes basic length check but is meaningless."""
        s = deepcopy(state)
        cos = s.get("cos", [])
        if not cos:
            raise ValueError("Course state has no COs")
        target = cos[0]
        orig_degree = target.get("degree", "to pass test suites")
        orig_statement = target.get("statement", "")

        vacuous_degree = "to an acceptable standard"
        target["degree"] = vacuous_degree
        # Update statement text to contain it
        target["statement"] = f"{target.get('verb', 'Design')} {target.get('object', 'systems')} using {target.get('condition', 'tools')} {vacuous_degree}."

        defect = InjectedDefect(
            defect_id=f"MUT-A1-{s.get('id', 'course')}",
            category=DefectCategory.A_EMPIRICAL_GEM,
            name="Vacuous Degree Statement",
            target_node_id=target.get("id", "CO1"),
            expected_rule_code="V11",
            description="Replaced measurable degree with vacuous phrase 'to an acceptable standard'",
            original_value=orig_degree,
            mutated_value=vacuous_degree,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    def inject_a2_chained_compound_verbs(self, state: dict[str, Any]) -> MutatedCourseResult:
        """Injects multiple action verbs chained in a single outcome."""
        s = deepcopy(state)
        cos = s.get("cos", [])
        target = cos[0]
        orig_statement = target.get("statement", "")

        mutated_statement = f"Design and implement and evaluate {target.get('object', 'applications')} to meet scalability criteria."
        target["statement"] = mutated_statement

        defect = InjectedDefect(
            defect_id=f"MUT-A2-{s.get('id', 'course')}",
            category=DefectCategory.A_EMPIRICAL_GEM,
            name="Chained Compound Verbs",
            target_node_id=target.get("id", "CO1"),
            expected_rule_code="V10",
            description="Chained three Bloom verbs ('design', 'implement', 'evaluate') into one outcome statement",
            original_value=orig_statement,
            mutated_value=mutated_statement,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    def inject_a3_banned_unobservable_verb(self, state: dict[str, Any]) -> MutatedCourseResult:
        """Replaces active Bloom verb with unobservable verb ('understand' / 'familiarize')."""
        s = deepcopy(state)
        cos = s.get("cos", [])
        target = cos[0]
        orig_verb = target.get("verb", "Design")
        orig_statement = target.get("statement", "")

        banned_verb = "understand"
        target["verb"] = banned_verb
        target["statement"] = f"Understand the core principles of {target.get('object', 'the domain')} under normal operating conditions."

        defect = InjectedDefect(
            defect_id=f"MUT-A3-{s.get('id', 'course')}",
            category=DefectCategory.A_EMPIRICAL_GEM,
            name="Banned Unobservable Verb",
            target_node_id=target.get("id", "CO1"),
            expected_rule_code="V12",
            description="Used unobservable verb 'understand' in outcome statement",
            original_value=orig_verb,
            mutated_value=banned_verb,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    # =================================================================
    # Category B: Arithmetic & Hours Feasibility (Violations of C3)
    # =================================================================

    def inject_b1_weight_sum_overflow(self, state: dict[str, Any]) -> MutatedCourseResult:
        """Perturbs assessment weights to sum to 115% instead of 100%."""
        s = deepcopy(state)
        assessments = s.get("assessments", [])
        if not assessments:
            raise ValueError("Course state has no assessments")
        target = assessments[0]
        orig_weight = target.get("weight_pct", 25.0)

        mutated_weight = orig_weight + 15.0
        target["weight_pct"] = mutated_weight

        defect = InjectedDefect(
            defect_id=f"MUT-B1-{s.get('id', 'course')}",
            category=DefectCategory.B_ARITHMETIC_HOURS,
            name="Assessment Weight Sum Overflow",
            target_node_id=target.get("id", "A1"),
            expected_rule_code="V20",
            description="Assessment weights sum to 115% (must be exactly 100%)",
            original_value=orig_weight,
            mutated_value=mutated_weight,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    def inject_b2_weight_sum_underflow(self, state: dict[str, Any]) -> MutatedCourseResult:
        """Perturbs assessment weights to sum to 85% instead of 100%."""
        s = deepcopy(state)
        assessments = s.get("assessments", [])
        target = assessments[-1]
        orig_weight = target.get("weight_pct", 20.0)

        mutated_weight = max(1.0, orig_weight - 15.0)
        target["weight_pct"] = mutated_weight

        defect = InjectedDefect(
            defect_id=f"MUT-B2-{s.get('id', 'course')}",
            category=DefectCategory.B_ARITHMETIC_HOURS,
            name="Assessment Weight Sum Underflow",
            target_node_id=target.get("id", "A_last"),
            expected_rule_code="V20",
            description="Assessment weights sum to 85% (must be exactly 100%)",
            original_value=orig_weight,
            mutated_value=mutated_weight,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    def inject_b3_excessive_lecture_hours(self, state: dict[str, Any]) -> MutatedCourseResult:
        """Inflates topic hours so total lecture hours exceed the 39-hour budget by >25%."""
        s = deepcopy(state)
        topics = s.get("topics", [])
        if not topics:
            raise ValueError("Course state has no topics")

        for t in topics:
            t["hours"] = t.get("hours", 2.0) * 1.5

        defect = InjectedDefect(
            defect_id=f"MUT-B3-{s.get('id', 'course')}",
            category=DefectCategory.B_ARITHMETIC_HOURS,
            name="Excessive Lecture Hours Budget",
            target_node_id="topics_budget",
            expected_rule_code="V21",
            description="Total lecture hours inflated to ~55 hours (exceeds IIIT-D 39h ceiling)",
            original_value=39.0,
            mutated_value=55.0,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    def inject_b4_oversized_single_topic(self, state: dict[str, Any]) -> MutatedCourseResult:
        """Allocates an excessive 9 hours to a single topic (rule limit is <= 3-4 hours)."""
        s = deepcopy(state)
        topics = s.get("topics", [])
        target = topics[0]
        orig_hours = target.get("hours", 2.0)

        target["hours"] = 9.0

        defect = InjectedDefect(
            defect_id=f"MUT-B4-{s.get('id', 'course')}",
            category=DefectCategory.B_ARITHMETIC_HOURS,
            name="Oversized Single Topic",
            target_node_id=target.get("id", "T1"),
            expected_rule_code="VT-SIZE",
            description="Single topic allocated 9.0 hours (exceeds max recommended topic chunk size)",
            original_value=orig_hours,
            mutated_value=9.0,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    # =================================================================
    # Category C: Temporal Causality & Scheduling Inversions
    # =================================================================

    def inject_c1_assessment_before_teaching(self, state: dict[str, Any]) -> MutatedCourseResult:
        """Schedules a quiz or exam in Week 3 that evaluates topics taught in Week 11."""
        s = deepcopy(state)
        assessments = s.get("assessments", [])
        target_assess = assessments[0]
        orig_week = target_assess.get("week", 5)

        # Move assessment to Week 2, but link it to advanced LOs/topics taught in Week 11
        target_assess["week"] = 2
        target_assess["covered_topics"] = ["Advanced Concurrency and Distributed Protocols"]

        defect = InjectedDefect(
            defect_id=f"MUT-C1-{s.get('id', 'course')}",
            category=DefectCategory.C_TEMPORAL_CAUSALITY,
            name="Assessment Scheduled Before Topic Delivery",
            target_node_id=target_assess.get("id", "A1"),
            expected_rule_code="V19",
            description="Assessment scheduled in Week 2 tests topics not taught until Week 11",
            original_value=orig_week,
            mutated_value=2,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    def inject_c2_chronological_instance_order_violation(self, state: dict[str, Any]) -> MutatedCourseResult:
        """Inverts instances of a repeating assessment (e.g. Assignment 2 due before Assignment 1)."""
        s = deepcopy(state)
        assessments = s.get("assessments", [])
        if len(assessments) >= 2:
            a1, a2 = assessments[0], assessments[1]
            a1["week"] = 8
            a2["week"] = 3
        else:
            assessments.append({"id": "A_early", "week": 2})

        defect = InjectedDefect(
            defect_id=f"MUT-C2-{s.get('id', 'course')}",
            category=DefectCategory.C_TEMPORAL_CAUSALITY,
            name="Assessment Instance Order Inversion",
            target_node_id="assessments_order",
            expected_rule_code="VA-ORDER",
            description="Assignment instances listed out of chronological sequence",
            original_value="Chronological",
            mutated_value="Inverted",
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    # =================================================================
    # Category D: Traceability & Constructive Alignment (Orphans, Gaps)
    # =================================================================

    def inject_d1_orphan_learning_outcome(self, state: dict[str, Any]) -> MutatedCourseResult:
        """Injects a Learning Outcome that is taught in lecture but disconnected from all assessments."""
        s = deepcopy(state)
        los = s.get("los", [])
        new_lo_id = f"LO_ORPHAN_{len(los) + 1}"
        new_lo = {
            "id": new_lo_id,
            "statement": "Implement distributed raft consensus using gRPC satisfying safety properties.",
            "verb": "implement",
            "bloom_level": 3,
            "condition": "using gRPC",
            "degree": "satisfying safety properties",
        }
        los.append(new_lo)
        # Ensure no assessment maps to this new LO
        for a in s.get("assessments", []):
            if "mapped_los" in a and new_lo_id in a["mapped_los"]:
                a["mapped_los"].remove(new_lo_id)

        defect = InjectedDefect(
            defect_id=f"MUT-D1-{s.get('id', 'course')}",
            category=DefectCategory.D_TRACEABILITY,
            name="Orphan Learning Outcome",
            target_node_id=new_lo_id,
            expected_rule_code="T-LO-ASSESSED",
            description="Learning Outcome is taught in syllabus but completely unassessed in any exam/quiz",
            original_value="Assessed",
            mutated_value="Orphan",
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    def inject_d2_cognitive_undertesting(self, state: dict[str, Any]) -> MutatedCourseResult:
        """CO declared at CREATE (Level 6), but all child LOs are only REMEMBER (Level 1)."""
        s = deepcopy(state)
        cos = s.get("cos", [])
        los = s.get("los", [])
        target_co = cos[0]
        target_co["bloom_level"] = 6
        target_co["verb"] = "design"

        # Demote all child LOs to Level 1
        for lo in los:
            if lo.get("co_id") == target_co.get("id"):
                lo["bloom_level"] = 1
                lo["verb"] = "recall"
                lo["statement"] = f"Recall definitions of {target_co.get('object', 'concepts')} from textbooks."

        defect = InjectedDefect(
            defect_id=f"MUT-D2-{s.get('id', 'course')}",
            category=DefectCategory.D_TRACEABILITY,
            name="Cognitive Level Under-Testing",
            target_node_id=target_co.get("id", "CO1"),
            expected_rule_code="T2",
            description="CO claims Bloom Level 6 (Create), but child LOs only test Level 1 (Remember)",
            original_value=6,
            mutated_value=1,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    # =================================================================
    # Category E: Uncaught Semantic Flaws (The Deliberate Blindspots)
    # =================================================================

    def inject_e1_domain_vocabulary_mismatch(self, state: dict[str, Any]) -> MutatedCourseResult:
        """
        Injects an outcome that is syntactically flawless (correct Bloom verb, condition, degree)
        but completely belongs to an unrelated subject domain (e.g. inserting an ECG biological
        signal processing LO into an Operating Systems thread module).
        *Deterministic code regex will pass this. Only human or deep semantic checks can catch it.*
        """
        s = deepcopy(state)
        los = s.get("los", [])
        target_lo = los[0]
        orig_statement = target_lo.get("statement", "")

        # Syntactically flawless outcome with BCD structure from medical signal processing
        alien_statement = "Design finite impulse response filters using MATLAB to extract fetal heart rates from maternal ECG signals with 95% SNR."
        target_lo["statement"] = alien_statement
        target_lo["verb"] = "design"
        target_lo["condition"] = "using MATLAB"
        target_lo["degree"] = "with 95% SNR"

        defect = InjectedDefect(
            defect_id=f"MUT-E1-{s.get('id', 'course')}",
            category=DefectCategory.E_UNCAUGHT_SEMANTIC,
            name="Domain Vocabulary Mismatch (Blindspot)",
            target_node_id=target_lo.get("id", "LO1"),
            expected_rule_code=None,  # No regex validator targets this!
            description="Syntactically valid BCD outcome inserted from completely unrelated discipline (Biomedical ECG in a CS course)",
            original_value=orig_statement,
            mutated_value=alien_statement,
            uncaught_by_design=True,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    def inject_e2_vacuous_tautological_condition(self, state: dict[str, Any]) -> MutatedCourseResult:
        """
        Injects a condition that sounds technical but is completely tautological and vacuous
        ('given typical computational problems requiring computer programs').
        """
        s = deepcopy(state)
        cos = s.get("cos", [])
        target_co = cos[0]
        orig_statement = target_co.get("statement", "")

        tautology = "Implement sorting algorithms given typical computational problems requiring computer programs to execute correctly."
        target_co["statement"] = tautology
        target_co["condition"] = "given typical computational problems requiring computer programs"
        target_co["degree"] = "to execute correctly"

        defect = InjectedDefect(
            defect_id=f"MUT-E2-{s.get('id', 'course')}",
            category=DefectCategory.E_UNCAUGHT_SEMANTIC,
            name="Tautological Semantic Condition (Blindspot)",
            target_node_id=target_co.get("id", "CO1"),
            expected_rule_code=None,
            description="Condition is grammatically valid and matches length checks but is a vacuous tautology",
            original_value=orig_statement,
            mutated_value=tautology,
            uncaught_by_design=True,
        )
        return MutatedCourseResult(base_course_id=s.get("id", "course"), course_state=s, defect=defect)

    # =================================================================
    # Master Mutation Suite Generator
    # =================================================================

    def generate_full_mutation_suite(self, base_courses: list[dict[str, Any]]) -> list[MutatedCourseResult]:
        """
        Applies all mutation operators across 3-5 base courses to create
        a balanced benchmark dataset (10-20 mutations per category).
        """
        suite: list[MutatedCourseResult] = []
        for course in base_courses:
            # Category A
            suite.append(self.inject_a1_vacuous_degree(course))
            suite.append(self.inject_a2_chained_compound_verbs(course))
            suite.append(self.inject_a3_banned_unobservable_verb(course))

            # Category B
            suite.append(self.inject_b1_weight_sum_overflow(course))
            suite.append(self.inject_b2_weight_sum_underflow(course))
            suite.append(self.inject_b3_excessive_lecture_hours(course))
            suite.append(self.inject_b4_oversized_single_topic(course))

            # Category C
            suite.append(self.inject_c1_assessment_before_teaching(course))
            suite.append(self.inject_c2_chronological_instance_order_violation(course))

            # Category D
            suite.append(self.inject_d1_orphan_learning_outcome(course))
            suite.append(self.inject_d2_cognitive_undertesting(course))

            # Category E (Uncaught blindspots)
            suite.append(self.inject_e1_domain_vocabulary_mismatch(course))
            suite.append(self.inject_e2_vacuous_tautological_condition(course))

        return suite
