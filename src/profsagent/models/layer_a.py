from typing import List, Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Models for E1: Header and Prerequisites
# ---------------------------------------------------------------------------
class CourseHeader(BaseModel):
    course_code: str = Field(description="Primary course code, e.g., 'CSE201'")
    aliases: List[str] = Field(default_factory=list, description="Other codes if cross-listed")
    name: str = Field(description="Full name of the course")
    credits: str = Field(description="Credit value")
    offered_to: List[str] = Field(description="Target audience, e.g., 'UG', 'PG'")
    department: Optional[str] = Field(None, description="Department offering the course")
    description: str = Field(description="Course description paragraph")
    prerequisites_mandatory: List[str] = Field(default_factory=list, description="List of mandatory prerequisite codes or subjects")
    prerequisites_desirable: List[str] = Field(default_factory=list, description="List of desirable prerequisite codes or subjects")

# ---------------------------------------------------------------------------
# Models for E2: Weekly Plan
# ---------------------------------------------------------------------------
class WeekPlan(BaseModel):
    week: str = Field(description="Week number or range, e.g., '1', '2-4'")
    lecture_topics: List[str] = Field(description="Atomic topic phrases extracted from the lecture topic cell")
    cos_met: List[str] = Field(description="List of CO labels met in this week, e.g., ['CO1', 'CO2']")
    tutorial_assignment: Optional[str] = Field(None, description="Raw text of tutorial or assignment info")

class WeeklyPlanExtraction(BaseModel):
    weeks: List[WeekPlan]

# ---------------------------------------------------------------------------
# Models for E3: Course Outcomes
# ---------------------------------------------------------------------------
class CourseOutcome(BaseModel):
    label: str = Field(description="CO identifier, e.g., 'CO1'")
    raw_text: str = Field(description="The full statement of the course outcome")

class OutcomesExtraction(BaseModel):
    outcomes: List[CourseOutcome]

# ---------------------------------------------------------------------------
# Models for E4: Assessment and Resources
# ---------------------------------------------------------------------------
class AssessmentComponent(BaseModel):
    type_label: str = Field(description="Type of assessment, e.g., 'Quiz', 'Mid-Sem'")
    weight_pct: float = Field(description="Percentage contribution to final grade")

class ResourceItem(BaseModel):
    type_label: str = Field(description="Type of resource, e.g., 'Textbook', 'Reference'")
    title: str = Field(description="Full citation or title of the resource")

class EvalResourceExtraction(BaseModel):
    assessments: List[AssessmentComponent]
    resources: List[ResourceItem]

# ---------------------------------------------------------------------------
# Complete Course Extraction (Aggregation)
# ---------------------------------------------------------------------------
class ExtractedCourse(BaseModel):
    header: CourseHeader
    outcomes: List[CourseOutcome]
    weekly_plan: List[WeekPlan]
    assessments: List[AssessmentComponent]
    resources: List[ResourceItem]
