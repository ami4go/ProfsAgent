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


# ------------------------------------------------------------------ D5 component plan for a topic
ComponentKind = Literal["concept", "mechanism", "demo", "worked_example", "comparison", "case_study", "activity", "discussion"]


class Component(M):
    lecture_id: str
    title: str
    teaches: str                                   # what students must take away, concretely (2–3 sentences)
    key_terms: list[str] = Field(default_factory=list)
    kind: ComponentKind = "concept"
    bloom: int = Field(default=2, ge=1, le=6)
    lo_ids: list[str] = Field(default_factory=list)
    minutes: int = Field(ge=1, le=180)


class ComponentPlan(M):
    components: list[Component]


# ------------------------------------------------------------------ D6 does this video stretch teach the component?
class SegmentCheck(M):
    id: str                                        # the stretch id given in the prompt (s1, s2, ...)
    verdict: Literal["teaches_fully", "teaches_partly", "mentions", "off_topic"]
    start: str = ""                                # m:ss (or h:mm:ss) of the first marker that teaches it
    end: str = ""                                  # m:ss of the marker where the teaching of it ends
    covered: list[str] = Field(default_factory=list)   # points of the component this stretch teaches
    missing: list[str] = Field(default_factory=list)   # points it leaves out
    clarity: int = Field(default=3, ge=1, le=5)
    level_fit: int = Field(default=3, ge=1, le=5)
    note: str = ""                                 # ≤ 25 words for the professor


class SegmentChecks(M):
    checks: list[SegmentCheck]


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
    same_field: bool = True          # False when the evidence is from another field that only shares words with the topic
    why: str
    evidence_ids: list[str] = Field(default_factory=list)
    suggested_format: Literal["live_remote_60", "live_in_person", "recorded_talk", "panel", "qa_after_recorded"] = "live_remote_60"
    concerns: list[str] = Field(default_factory=list)


class ExpertNotes(M):
    notes: list[ExpertNote]
