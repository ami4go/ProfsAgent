"""
Course domain models for the Evaluation & Validation framework.

These models represent the parsed, structured course data that flows through
the validation pipeline. They are intentionally decoupled from the upstream
Pydantic LLM-output models (profsagent.models.io) so that the evaluation
harness can operate independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class AssessmentType(str, Enum):
    MIDSEM = "midsem"
    ENDSEM = "endsem"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    PROJECT = "project"
    LAB = "lab"
    PRESENTATION = "presentation"
    VIVA = "viva"
    OTHER = "other"


@dataclass
class CourseHeader:
    """Basic course identification metadata."""
    course_code: str
    course_title: str
    credits: int = 4
    department: str = "CSE"
    prerequisites: list[str] = field(default_factory=list)


@dataclass
class CourseOutcome:
    """A single Course Outcome (CO) with Bloom verb decomposition."""
    co_id: str
    description: str
    action_verb: str = ""
    bloom_level: int = 3
    condition: str = ""
    degree: str = ""
    covers_topic_groups: list[str] = field(default_factory=list)


@dataclass
class WeekPlanItem:
    """A single week entry in the 14-week lecture plan."""
    week_number: int
    topic_summary: str
    hours: float = 3.0
    mapped_cos: list[str] = field(default_factory=list)
    mapped_los: list[str] = field(default_factory=list)


@dataclass
class AssessmentComponent:
    """A single assessment item in the course evaluation plan."""
    name: str
    assessment_type: AssessmentType = AssessmentType.OTHER
    weight_percentage: float = 0.0
    scheduled_week: int | None = None
    mapped_cos: list[str] = field(default_factory=list)
    mapped_los: list[str] = field(default_factory=list)


@dataclass
class ParsedCourse:
    """
    Complete parsed course representation consumed by validators.

    This is the central data structure for the evaluation pipeline.
    It aggregates header info, COs, weekly plans, and assessments.
    """
    header: CourseHeader
    course_outcomes: list[CourseOutcome] = field(default_factory=list)
    weekly_plans: list[WeekPlanItem] = field(default_factory=list)
    assessments: list[AssessmentComponent] = field(default_factory=list)

    @property
    def total_assessment_weight(self) -> float:
        return sum(a.weight_percentage for a in self.assessments)

    @property
    def total_lecture_hours(self) -> float:
        return sum(w.hours for w in self.weekly_plans)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for validator consumption."""
        return {
            "id": self.header.course_code,
            "name": self.header.course_title,
            "credits": self.header.credits,
            "cos": [
                {
                    "id": co.co_id,
                    "statement": co.description,
                    "verb": co.action_verb,
                    "bloom_level": co.bloom_level,
                    "condition": co.condition,
                    "degree": co.degree,
                }
                for co in self.course_outcomes
            ],
            "assessments": [
                {
                    "id": f"A{i+1}",
                    "name": a.name,
                    "weight_pct": a.weight_percentage,
                    "week": a.scheduled_week,
                    "type": a.assessment_type.value,
                    "mapped_cos": a.mapped_cos,
                    "mapped_los": a.mapped_los,
                }
                for i, a in enumerate(self.assessments)
            ],
            "topics": [
                {
                    "id": f"T{w.week_number}",
                    "name": w.topic_summary,
                    "hours": w.hours,
                    "week": w.week_number,
                }
                for w in self.weekly_plans
            ],
        }


@dataclass
class ValidationViolation:
    """A single validation finding (error or warning)."""
    validator_id: str
    severity: str          # "error" | "warning"
    node_ids: list[str]
    message: str
    evidence: dict[str, Any] = field(default_factory=dict)
    fix_hint: str = ""


@dataclass
class ValidationReport:
    """Aggregate report from running all validators on a course."""
    course_id: str
    violations: list[ValidationViolation] = field(default_factory=list)
    warnings: list[ValidationViolation] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.violations) == 0

    @property
    def total_findings(self) -> int:
        return len(self.violations) + len(self.warnings)

    def has_rule(self, rule_code: str) -> bool:
        """Check if any finding matches the given rule code."""
        return any(
            v.validator_id == rule_code
            for v in self.violations + self.warnings
        )
