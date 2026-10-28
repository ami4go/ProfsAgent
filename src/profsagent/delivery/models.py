"""Output formats for the delivery prompts (prompts/delivery/D1–D4). Validated with Pydantic like Phase 1."""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


class M(BaseModel):
    model_config = ConfigDict(extra="ignore")


# ------------------------------------------------------------------ D1 search queries
class LectureQueries(M):
    lecture_id: str
    video_queries: list[str] = Field(default_factory=list)
    reading_queries: list[str] = Field(default_factory=list)
    practice_queries: list[str] = Field(default_factory=list)
    recorded_lecture_query: Optional[str] = None
    research_queries: list[str] = Field(default_factory=list)      # paper / academic-expert search phrases
    practitioner_query: Optional[str] = None


class QueryPlan(M):
    lectures: list[LectureQueries]


# ------------------------------------------------------------------ D2 resource review (AI checklist + review text)
class ResourceReview(M):
    id: str
    clarity: int = Field(ge=1, le=5)
    correctness: int = Field(ge=1, le=5)
    depth: int = Field(ge=1, le=5)
    examples: int = Field(ge=1, le=5)
    level_fit: int = Field(ge=1, le=5)
    explains: Literal["explains", "mentions", "off_topic"]
    issues: list[str] = Field(default_factory=list)
    review: str = ""
    use_as: Literal["professor_prep", "pre_class", "in_class_clip", "after_class", "flipped_class", "lab", "practice"] = "after_class"
    generic: bool = False            # a general introduction to a broader or prerequisite concept, not this lecture's topic
    hands_on: bool | None = None     # practice candidates only: students do something (exercises, notebook, code, lab)


class ResourceReviews(M):
    reviews: list[ResourceReview]


# ------------------------------------------------------------------ D3 practitioners from web search
class Practitioner(M):
    name: str
    role: str = ""
    organisation: str = ""
    country: Optional[str] = None
    profile_url: Optional[str] = None
    evidence_urls: list[str] = Field(default_factory=list)
    why: str = ""


class Practitioners(M):
    people: list[Practitioner] = Field(default_factory=list)


# ------------------------------------------------------------------ D4 expert rationale
class ExpertNote(M):
    id: str
    fit: Literal["strong", "moderate", "weak"]
    why: str
    evidence_ids: list[str] = Field(default_factory=list)
    suggested_format: Literal["live_remote_60", "live_in_person", "recorded_talk", "panel", "qa_after_recorded"] = "live_remote_60"
    concerns: list[str] = Field(default_factory=list)


class ExpertNotes(M):
    notes: list[ExpertNote]
