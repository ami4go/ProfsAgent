"""
E1-E4 Information Extractors for ProfsAgent Course Sheets.

Implements the four distinct extraction stages:
E1 = Course Header + Prerequisites + Basic Constraints
E2 = Weekly Lecture Plan + Weekly Lab Plan
E3 = Course Outcomes (COs) Analysis
E4 = Assessment Components + Resource Materials

Supports deterministic parsing with structured Pydantic schema validation,
alongside prompt templates for LLM-assisted fallback when sheets vary widely.
"""

import json
import re
from typing import Any
from profsagent.ingest.sheet_parser import DeterministicSheetParser, RawCourseSections
from profsagent.models.schema import (
    AssessmentComponent,
    AssessmentType,
    CourseHeader,
    CourseOutcome,
    LabPlanItem,
    PrerequisiteItem,
    ParsedCourse,
    ResourceItem,
    ResourceType,
    WeekPlanItem,
)


class CourseSheetExtractors:
    """Orchestrates E1-E4 extraction with strict schema conformance."""

    def __init__(self, parser: DeterministicSheetParser | None = None) -> None:
        self.parser = parser or DeterministicSheetParser()

    # =================================================================
    # E1: Course Header and Prerequisites Extractor
    # =================================================================
    def extract_e1(self, sections: RawCourseSections) -> CourseHeader:
        """Deterministic E1 extractor for course code, title, credits, prereqs."""
        parsed = self.parser.parse_header_deterministic(sections.header_block)

        # Parse prerequisites from prerequisites block or header
        prereq_text = sections.prerequisites_block or sections.header_block
        prereqs: list[PrerequisiteItem] = []

        # Find course codes in prerequisite text (e.g., CSE101, CSE201, MTH100)
        found_codes = re.findall(r"\b([A-Z]{2,4}\s*[-]?\s*[0-9]{3}[A-Z]?)\b", prereq_text)
        current_code = parsed.get("course_code")

        for code in found_codes:
            clean_code = re.sub(r"[\s-]", "", code).upper()
            if clean_code != current_code:
                prereqs.append(PrerequisiteItem(
                    course_code=clean_code,
                    raw_condition=f"Requires {clean_code}",
                    is_hard_prerequisite=True,
                ))

        course_code = str(parsed.get("course_code", "UNKNOWN101"))
        credits_val = int(parsed.get("credits", 4))
        title = str(parsed.get("course_title", f"Course {course_code}"))
        department = str(parsed.get("department", "CSE"))

        # Derive level from course code digits (e.g. CSE201 -> 200, CSE501 -> 500)
        level_match = re.search(r"(\d)\d{2}", course_code)
        level = int(level_match.group(1)) * 100 if level_match else 200

        return CourseHeader(
            course_code=course_code,
            course_title=title,
            credits=credits_val,
            department=department,
            level=level,
            prerequisites=prereqs,
        )

    # =================================================================
    # E2: Weekly Lecture and Lab Plan Extractor
    # =================================================================
    def extract_e2(self, sections: RawCourseSections) -> tuple[list[WeekPlanItem], list[LabPlanItem]]:
        """Extracts week-wise lecture plans and lab activities."""
        week_plans: list[WeekPlanItem] = []
        lab_plans: list[LabPlanItem] = []

        # Parse weekly lecture plan
        lines = sections.weekly_lecture_block.splitlines()
        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Look for "Week 1: ...", "Week 1 - ...", "W1: ..."
            match = re.match(
                r"^(?:Week\s*([1-9]|1[0-9]|20)|W([1-9]|1[0-9]|20))\s*[:.-]?\s*(.*)",
                line_str,
                re.IGNORECASE,
            )
            if match:
                w_num = int(match.group(1) or match.group(2))
                summary = match.group(3).strip()
                subtopics = [s.strip() for s in summary.split(",") if len(s.strip()) > 3]

                week_plans.append(WeekPlanItem(
                    week_number=w_num,
                    topic_summary=summary,
                    subtopics=subtopics,
                    lecture_hours=3.0,
                ))

        # Parse lab plan if present
        lab_lines = sections.lab_plan_block.splitlines()
        for line in lab_lines:
            line_str = line.strip()
            if not line_str:
                continue
            lab_match = re.match(
                r"^(?:Lab\s*([1-9]|1[0-9])|Week\s*([1-9]|1[0-9]))\s*[:.-]?\s*(.*)",
                line_str,
                re.IGNORECASE,
            )
            if lab_match:
                l_num = int(lab_match.group(1) or lab_match.group(2))
                desc = lab_match.group(3).strip()
                lab_plans.append(LabPlanItem(
                    week_number=l_num,
                    lab_title=f"Lab {l_num}: {desc[:40]}",
                    lab_description=desc,
                    lab_hours=2.0,
                ))

        return week_plans, lab_plans

    # =================================================================
    # E3: Course Outcomes (COs) Extractor
    # =================================================================
    def extract_e3(self, sections: RawCourseSections) -> list[CourseOutcome]:
        """Extracts Course Outcomes and identifies action verbs."""
        raw_cos = self.parser.parse_course_outcomes_deterministic(sections.course_outcomes_block)
        outcomes: list[CourseOutcome] = []

        for item in raw_cos:
            co_id = item["co_id"]
            desc = item["description"]
            first_word = desc.split()[0].lower().rstrip(",.:;") if desc.split() else "unspecified"

            outcomes.append(CourseOutcome(
                co_id=co_id,
                description=desc,
                action_verb=first_word,
                mapped_pos=[],
            ))

        return outcomes

    # =================================================================
    # E4: Assessments and Resources Extractor
    # =================================================================
    def extract_e4(self, sections: RawCourseSections) -> tuple[list[AssessmentComponent], list[ResourceItem]]:
        """Extracts assessments with percentage weights and textbooks/readings."""
        raw_assessments = self.parser.parse_assessments_deterministic(sections.assessment_block)
        assessments: list[AssessmentComponent] = []

        for a in raw_assessments:
            name = str(a["name"])
            weight = float(a["weight_percentage"])

            # Classify assessment type
            name_lower = name.lower()
            if "midsem" in name_lower or "mid-term" in name_lower:
                atype = AssessmentType.MIDSEM
            elif "endsem" in name_lower or "final" in name_lower:
                atype = AssessmentType.ENDSEM
            elif "quiz" in name_lower:
                atype = AssessmentType.QUIZ
            elif "assignment" in name_lower or "homework" in name_lower:
                atype = AssessmentType.ASSIGNMENT
            elif "project" in name_lower:
                atype = AssessmentType.PROJECT
            elif "lab" in name_lower:
                atype = AssessmentType.LAB
            elif "presentation" in name_lower:
                atype = AssessmentType.PRESENTATION
            else:
                atype = AssessmentType.OTHER

            assessments.append(AssessmentComponent(
                name=name,
                assessment_type=atype,
                weight_percentage=weight,
            ))

        # Parse resources
        resources: list[ResourceItem] = []
        for line in sections.resources_block.splitlines():
            line_str = line.strip()
            if not line_str or len(line_str) < 5:
                continue
            # Strip leading list numbers: "1. ", "- "
            clean_res = re.sub(r"^[-*•0-9.]+\s*", "", line_str)
            # Detect textbook vs paper
            rtype = ResourceType.RESEARCH_PAPER if "paper" in clean_res.lower() or "proc." in clean_res.lower() else ResourceType.TEXTBOOK

            resources.append(ResourceItem(
                title=clean_res,
                resource_type=rtype,
            ))

        return assessments, resources

    # =================================================================
    # Complete Pipeline: Segment -> E1 + E2 + E3 + E4 -> ParsedCourse
    # =================================================================
    def extract_full_course(self, raw_text: str, is_gold_set: bool = False) -> ParsedCourse:
        """Runs the complete E1-E4 extraction pipeline over raw course sheet text."""
        sections = self.parser.segment_sheet(raw_text)

        header = self.extract_e1(sections)
        weekly_plans, lab_plans = self.extract_e2(sections)
        cos = self.extract_e3(sections)
        assessments, resources = self.extract_e4(sections)

        # Distribute CO coverage across comprehensive exams if unspecified
        all_co_ids = [co.co_id for co in cos]
        for a in assessments:
            if not a.mapped_cos:
                if a.assessment_type in {AssessmentType.MIDSEM, AssessmentType.ENDSEM, AssessmentType.PROJECT}:
                    a.mapped_cos = all_co_ids

        return ParsedCourse(
            header=header,
            course_outcomes=cos,
            weekly_plans=weekly_plans,
            lab_plans=lab_plans,
            assessments=assessments,
            resources=resources,
            is_gold_set=is_gold_set,
        )
