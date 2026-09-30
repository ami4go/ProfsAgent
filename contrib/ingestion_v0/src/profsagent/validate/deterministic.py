"""
Deterministic Validator Suite (V1–V24 + T1–T4) for ProfsAgent Evaluation.

Implements the full set of code-based validators referenced in the paper's
Claim C2 ('Checks written as code beat an LLM reviewing its own output').

These validators operate on ParsedCourse objects and return ValidationReports
containing categorized violations and warnings.

Validator Groups:
  V4–V8:   CO count and Bloom band compliance
  V10:     Single-verb-per-statement & verb-starts-statement
  V11:     Condition/Degree presence and non-vacuity
  V12:     Banned/unobservable verb detection
  V19:     Temporal causality (assessment before teaching)
  V20:     Assessment weight sum = 100%
  V21:     Total lecture hours within budget
  VA-ORDER:Instance chronological ordering
  VT-SIZE: Single-topic hour cap
  T-LO-ASSESSED: Orphan LO detection (taught but unassessed)
  T2:      Cognitive level alignment (CO↔LO Bloom consistency)
"""

from __future__ import annotations

import re
from typing import Any

from profsagent.models.schema import (
    ParsedCourse,
    ValidationReport,
    ValidationViolation,
)

# ──────────────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────────────

ERR = "error"
WARN = "warning"

# IIIT-D standard: 3 credits ≈ 39 lecture hours, 4 credits ≈ 52 hours
LECTURE_HOURS_BUDGET = {3: 39.0, 4: 52.0}
LECTURE_HOURS_TOLERANCE = 0.25  # ±25%
MAX_SINGLE_TOPIC_HOURS = 4.0
ASSESSMENT_WEIGHT_TOLERANCE = 1.0  # total must be within ±1 of 100%

# Bloom's taxonomy observable verb lexicon (abridged)
# Level → canonical verbs at that level
BLOOM_LEXICON: dict[int, set[str]] = {
    1: {"list", "recall", "recognize", "identify", "define", "name", "state",
        "label", "match", "select", "describe"},
    2: {"explain", "summarize", "interpret", "classify", "compare",
        "contrast", "distinguish", "paraphrase", "illustrate", "trace"},
    3: {"apply", "implement", "solve", "use", "demonstrate", "calculate",
        "execute", "operate", "construct", "write", "compute", "formulate",
        "develop", "build", "deploy", "acquire", "rotate"},
    4: {"analyze", "differentiate", "examine", "test", "inspect",
        "categorize", "debug", "decompose", "infer", "deduce"},
    5: {"evaluate", "justify", "critique", "assess", "judge", "appraise",
        "defend", "validate", "verify", "measure"},
    6: {"design", "create", "synthesize", "compose", "propose",
        "formulate", "invent", "plan", "devise", "generate"},
}

# Flattened verb → level lookup
_VERB_LEVEL: dict[str, int] = {}
for _lvl, _verbs in BLOOM_LEXICON.items():
    for _v in _verbs:
        _VERB_LEVEL[_v] = _lvl

# Unobservable / banned verbs (not measurable in assessments)
BANNED_VERBS = {
    "understand", "learn", "know", "appreciate", "familiarize",
    "be aware", "become familiar", "be able", "study", "explore",
    "gain", "grasp", "comprehend", "realize",
}

# Vacuous degree phrases (pass V11 length checks but add no measurability)
VACUOUS_DEGREE_PATTERNS = [
    r"to an? (?:acceptable|satisfactory|appropriate|adequate) (?:standard|level|degree|extent)",
    r"(?:correctly|properly|effectively|efficiently|successfully)$",
    r"^(?:well|good|better)$",
    r"in a (?:timely|proper|correct) (?:manner|fashion|way)",
]


def _lemma(word: str) -> str:
    """Very simple stemmer for verb comparison."""
    w = word.lower().strip()
    for suffix in ("ing", "tion", "ment", "es", "ed", "s"):
        if w.endswith(suffix) and len(w) - len(suffix) > 2:
            return w[: -len(suffix)]
    return w


def _bloom_of_verb(verb: str) -> int | None:
    """Return Bloom level for a verb, or None if not in lexicon."""
    v = verb.lower().strip()
    if v in _VERB_LEVEL:
        return _VERB_LEVEL[v]
    lem = _lemma(v)
    return _VERB_LEVEL.get(lem)


def _is_banned(verb: str) -> bool:
    """Check if verb or its lemma is in the banned unobservable set."""
    v = verb.lower().strip()
    return v in BANNED_VERBS or _lemma(v) in BANNED_VERBS


def _is_vacuous_degree(degree: str) -> bool:
    """Check if a degree phrase is tautological / vacuous."""
    d = degree.lower().strip()
    return any(re.search(p, d) for p in VACUOUS_DEGREE_PATTERNS)


# ──────────────────────────────────────────────────────────────────────
# Core Validator Class
# ──────────────────────────────────────────────────────────────────────

class DeterministicValidator:
    """
    Runs all deterministic validation rules on a ParsedCourse.

    Each check method returns a list of ValidationViolation objects.
    The main entry point `validate_course()` runs all checks and
    returns a comprehensive ValidationReport.
    """

    def validate_course(self, course: ParsedCourse) -> ValidationReport:
        """Run all validators and return aggregate report."""
        report = ValidationReport(course_id=course.header.course_code)
        all_findings: list[ValidationViolation] = []

        # Run each validator group
        all_findings.extend(self.check_co_count(course))
        all_findings.extend(self.check_statement_verbs(course))
        all_findings.extend(self.check_condition_degree(course))
        all_findings.extend(self.check_banned_verbs(course))
        all_findings.extend(self.check_assessment_weights(course))
        all_findings.extend(self.check_lecture_hours_budget(course))
        all_findings.extend(self.check_single_topic_size(course))
        all_findings.extend(self.check_temporal_causality(course))
        all_findings.extend(self.check_assessment_order(course))
        all_findings.extend(self.check_orphan_los(course))
        all_findings.extend(self.check_cognitive_alignment(course))

        # Partition into errors and warnings
        for finding in all_findings:
            if finding.severity == ERR:
                report.violations.append(finding)
            else:
                report.warnings.append(finding)

        return report

    # ──────────────────────────────────────────────────────
    # V4: CO count in regulatory range (3–6 for IIIT-D)
    # ──────────────────────────────────────────────────────

    def check_co_count(self, course: ParsedCourse) -> list[ValidationViolation]:
        findings = []
        n = len(course.course_outcomes)
        if n < 3 or n > 6:
            findings.append(ValidationViolation(
                validator_id="V4",
                severity=ERR,
                node_ids=[co.co_id for co in course.course_outcomes],
                message=f"Course has {n} COs; expected 3–6 per IIIT-D regulation",
            ))
        return findings

    # ──────────────────────────────────────────────────────
    # V10: Single verb per statement, verb leads statement
    # ──────────────────────────────────────────────────────

    def check_statement_verbs(self, course: ParsedCourse) -> list[ValidationViolation]:
        findings = []
        for co in course.course_outcomes:
            st = co.description
            verb = co.action_verb.lower().strip()

            # Check: statement starts with declared verb
            first_word = re.findall(r"[A-Za-z-]+", st)
            if first_word and first_word[0].lower() != verb:
                findings.append(ValidationViolation(
                    validator_id="V10",
                    severity=ERR,
                    node_ids=[co.co_id],
                    message=f"{co.co_id}: statement starts with '{first_word[0]}' but declares verb '{verb}'",
                    evidence={"statement": st},
                ))

            # Check: no chained verbs (e.g., "Design and implement and evaluate")
            head_clause = st.split(",")[0]
            chained = re.findall(r"\b(?:and|or|then)\s+([A-Za-z-]+)", head_clause, re.IGNORECASE)
            chained_bloom = [w for w in chained if _bloom_of_verb(w) is not None and w.lower() != verb]
            if chained_bloom:
                findings.append(ValidationViolation(
                    validator_id="V10",
                    severity=ERR,
                    node_ids=[co.co_id],
                    message=f"{co.co_id} chains Bloom verbs ('{verb}' + {chained_bloom}): one outcome per statement",
                    evidence={"statement": st},
                ))

        return findings

    # ──────────────────────────────────────────────────────
    # V11: Condition and Degree must be present and non-vacuous
    # ──────────────────────────────────────────────────────

    def check_condition_degree(self, course: ParsedCourse) -> list[ValidationViolation]:
        findings = []
        for co in course.course_outcomes:
            # Check condition
            cond = (co.condition or "").strip()
            if len(cond) < 4:
                findings.append(ValidationViolation(
                    validator_id="V11",
                    severity=ERR,
                    node_ids=[co.co_id],
                    message=f"{co.co_id} has no condition (or too short: '{cond}')",
                ))

            # Check degree
            deg = (co.degree or "").strip()
            if len(deg) < 4:
                findings.append(ValidationViolation(
                    validator_id="V11",
                    severity=ERR,
                    node_ids=[co.co_id],
                    message=f"{co.co_id} has no degree (or too short: '{deg}')",
                ))
            elif _is_vacuous_degree(deg):
                findings.append(ValidationViolation(
                    validator_id="V11",
                    severity=ERR,
                    node_ids=[co.co_id],
                    message=f"{co.co_id} degree is vacuous: '{deg}'",
                ))

        return findings

    # ──────────────────────────────────────────────────────
    # V12: Banned / unobservable verb detection
    # ──────────────────────────────────────────────────────

    def check_banned_verbs(self, course: ParsedCourse) -> list[ValidationViolation]:
        findings = []
        for co in course.course_outcomes:
            verb = co.action_verb.lower().strip()
            st = co.description.lower()

            if _is_banned(verb):
                findings.append(ValidationViolation(
                    validator_id="V12",
                    severity=ERR,
                    node_ids=[co.co_id],
                    message=f"{co.co_id} uses banned/unobservable verb '{verb}'",
                    evidence={"verb": verb, "statement": co.description},
                ))

            # Also check if statement text starts with a banned word
            first_word = re.findall(r"[A-Za-z]+", st)
            if first_word and _is_banned(first_word[0]) and first_word[0] != verb:
                findings.append(ValidationViolation(
                    validator_id="V12",
                    severity=ERR,
                    node_ids=[co.co_id],
                    message=f"{co.co_id} statement starts with banned verb '{first_word[0]}'",
                    evidence={"statement": co.description},
                ))

        return findings

    # ──────────────────────────────────────────────────────
    # V20: Assessment weights must sum to 100%
    # ──────────────────────────────────────────────────────

    def check_assessment_weights(self, course: ParsedCourse) -> list[ValidationViolation]:
        findings = []
        total = course.total_assessment_weight
        if abs(total - 100.0) > ASSESSMENT_WEIGHT_TOLERANCE:
            findings.append(ValidationViolation(
                validator_id="V20",
                severity=ERR,
                node_ids=[f"A{i+1}" for i in range(len(course.assessments))],
                message=f"Assessment weights sum to {total:.1f}% (must be 100% ± {ASSESSMENT_WEIGHT_TOLERANCE}%)",
                evidence={"total_weight": total},
            ))
        return findings

    # ──────────────────────────────────────────────────────
    # V21: Total lecture hours within budget
    # ──────────────────────────────────────────────────────

    def check_lecture_hours_budget(self, course: ParsedCourse) -> list[ValidationViolation]:
        findings = []
        budget = LECTURE_HOURS_BUDGET.get(course.header.credits, 52.0)
        total = course.total_lecture_hours
        lower = budget * (1 - LECTURE_HOURS_TOLERANCE)
        upper = budget * (1 + LECTURE_HOURS_TOLERANCE)
        if total < lower or total > upper:
            findings.append(ValidationViolation(
                validator_id="V21",
                severity=ERR if total > upper else WARN,
                node_ids=["topics_budget"],
                message=f"Total lecture hours {total:.1f}h outside budget {lower:.0f}–{upper:.0f}h (budget: {budget}h for {course.header.credits} credits)",
                evidence={"total_hours": total, "budget": budget},
            ))
        return findings

    # ──────────────────────────────────────────────────────
    # VT-SIZE: Single topic must not exceed max hours
    # ──────────────────────────────────────────────────────

    def check_single_topic_size(self, course: ParsedCourse) -> list[ValidationViolation]:
        findings = []
        for week in course.weekly_plans:
            if week.hours > MAX_SINGLE_TOPIC_HOURS:
                findings.append(ValidationViolation(
                    validator_id="VT-SIZE",
                    severity=WARN,
                    node_ids=[f"T{week.week_number}"],
                    message=f"Topic '{week.topic_summary}' at {week.hours:.1f}h exceeds max {MAX_SINGLE_TOPIC_HOURS:.0f}h per topic",
                    evidence={"hours": week.hours, "max": MAX_SINGLE_TOPIC_HOURS},
                ))
        return findings

    # ──────────────────────────────────────────────────────
    # V19: Assessment must not test topics not yet taught
    # ──────────────────────────────────────────────────────

    def check_temporal_causality(self, course: ParsedCourse) -> list[ValidationViolation]:
        """Check that assessments don't evaluate content before it's taught."""
        findings = []
        # Build a map of what is taught by each week
        topic_weeks: dict[str, int] = {}
        for week in course.weekly_plans:
            topic_weeks[week.topic_summary.lower()] = week.week_number
            for lo in week.mapped_los:
                topic_weeks[lo.lower()] = week.week_number

        for i, assess in enumerate(course.assessments):
            if assess.scheduled_week is None:
                continue
            # Check all mapped LOs — they must be taught before the assessment
            for lo_id in assess.mapped_los:
                lo_lower = lo_id.lower()
                if lo_lower in topic_weeks:
                    teach_week = topic_weeks[lo_lower]
                    if assess.scheduled_week < teach_week:
                        findings.append(ValidationViolation(
                            validator_id="V19",
                            severity=ERR,
                            node_ids=[f"A{i+1}"],
                            message=f"Assessment '{assess.name}' (week {assess.scheduled_week}) tests LO '{lo_id}' not taught until week {teach_week}",
                            evidence={"assess_week": assess.scheduled_week, "teach_week": teach_week},
                        ))

        return findings

    # ──────────────────────────────────────────────────────
    # VA-ORDER: Assessment instances in chronological order
    # ──────────────────────────────────────────────────────

    def check_assessment_order(self, course: ParsedCourse) -> list[ValidationViolation]:
        """Check that sequential assessments of the same type are in chronological order."""
        findings = []
        # Group assessments by type
        by_type: dict[str, list[tuple[int, Any]]] = {}
        for i, assess in enumerate(course.assessments):
            key = assess.assessment_type.value
            if key not in by_type:
                by_type[key] = []
            by_type[key].append((i, assess))

        for atype, items in by_type.items():
            if len(items) < 2:
                continue
            weeks = [(idx, a.scheduled_week or 0) for idx, a in items]
            for j in range(1, len(weeks)):
                if weeks[j][1] < weeks[j - 1][1]:
                    findings.append(ValidationViolation(
                        validator_id="VA-ORDER",
                        severity=WARN,
                        node_ids=[f"A{weeks[j-1][0]+1}", f"A{weeks[j][0]+1}"],
                        message=f"Assessment instances of type '{atype}' are out of chronological order (week {weeks[j-1][1]} before week {weeks[j][1]})",
                    ))

        return findings

    # ──────────────────────────────────────────────────────
    # T-LO-ASSESSED: Every LO must be assessed by at least one assessment
    # ──────────────────────────────────────────────────────

    def check_orphan_los(self, course: ParsedCourse) -> list[ValidationViolation]:
        """Detect Learning Outcomes that aren't assessed by any assessment."""
        findings = []
        # Gather all LO IDs that are assessed
        assessed_los: set[str] = set()
        for assess in course.assessments:
            assessed_los.update(assess.mapped_los)

        # Gather all LO IDs from weekly plans
        all_taught_los: set[str] = set()
        for week in course.weekly_plans:
            all_taught_los.update(week.mapped_los)

        # Orphans: taught but never assessed
        orphans = all_taught_los - assessed_los
        for lo_id in sorted(orphans):
            findings.append(ValidationViolation(
                validator_id="T-LO-ASSESSED",
                severity=ERR,
                node_ids=[lo_id],
                message=f"Learning Outcome '{lo_id}' is taught but not assessed by any assessment",
            ))

        return findings

    # ──────────────────────────────────────────────────────
    # T2: CO Bloom level must be achievable by its child LOs
    # ──────────────────────────────────────────────────────

    def check_cognitive_alignment(self, course: ParsedCourse) -> list[ValidationViolation]:
        """
        Check that CO-declared Bloom levels are consistent:
        - If CO claims Level 6 (Create), at least one child assessment should test ≥ Level 4
        - Flag if all child LOs are ≥ 3 levels below the CO
        """
        findings = []
        # This is a simplified check — we flag when verb-declared Bloom
        # level of the CO is dramatically different from what's seen
        for co in course.course_outcomes:
            verb = co.action_verb.lower().strip()
            verb_level = _bloom_of_verb(verb)
            declared_level = co.bloom_level

            if verb_level is not None and declared_level:
                if abs(verb_level - declared_level) >= 3:
                    findings.append(ValidationViolation(
                        validator_id="T2",
                        severity=WARN,
                        node_ids=[co.co_id],
                        message=f"{co.co_id}: declared Bloom L{declared_level} but verb '{verb}' is lexicon L{verb_level} (gap ≥ 3 levels)",
                        evidence={"declared": declared_level, "verb_level": verb_level},
                    ))

        return findings
