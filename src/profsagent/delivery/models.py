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


# ------------------------------------------------------------------ the delivery mix (delivery/mix.py; file delivery/mix/<lecture>.json)
Way = Literal["slides", "youtube", "youtube_bridge", "notebooklm", "in_class", "simulation"]
When = Literal["in_class", "pre_class"]


class MixSegment(M):
    video: str
    video_id: str
    url: str
    start: str
    end: str
    minutes: float
    verdict: str


class MixSimulation(M):
    id: Optional[str] = None                       # catalogue entry (simulations/<id>) ...
    url: Optional[str] = None                      # ... or a link to a trusted site (ext:<site>:<slug>)
    title: str
    source: str = ""                               # "catalogue", "built", or the site's name
    score: float = 0.0
    class_example: Optional[dict] = None           # the setup students start from, when the professor saved one


class PartMix(M):
    component: str                                 # W03.L2.C1
    title: str
    minutes: int                                   # class minutes for this part
    kind: str = "concept"
    bloom: int = 2
    way: Way
    when: When = "in_class"                        # pre_class: watched before class; the part's minutes are a debrief
    rule: str                                      # R1 in class, R1b simulation, R2 YouTube, R3 YouTube + bridge, R4 NotebookLM,
                                                   # R5 slides, P preference, L lecture check, D7 AI, professor
    reason: str                                    # one line for the professor
    alternative: Optional[dict] = None             # {"way", "reason"}: the next best way
    allowed: list[Way] = Field(default_factory=list)   # ways the evidence supports (slides and in_class always)
    locked: bool = False
    set_by: Literal["ai", "professor"] = "ai"
    prep_minutes: int = 0
    segments: list[MixSegment] = Field(default_factory=list)   # youtube / youtube_bridge
    video_minutes: float = 0.0
    bridge: list[str] = Field(default_factory=list)            # youtube_bridge: points the professor's slides add
    coverage: Optional[float] = None               # share of key terms found in the NotebookLM sources
    uncovered: list[str] = Field(default_factory=list)         # key terms no source has
    simulation: Optional[MixSimulation] = None     # the best matching simulation (evidence; used when way is simulation)


class LectureMix(M):
    lecture_id: str
    topic: str
    minutes: int                                   # the lecture's minutes (parts + recap + quiz)
    status: Literal["proposed", "approved"] = "proposed"
    preset: Literal["slides_only", "slides_clips", "slides_notebooklm", "flipped", "full_mix"]
    preset_by: Literal["ai", "professor"] = "ai"
    course_style: Literal["slides", "mix", "flipped"] = "mix"
    parts: list[PartMix]
    recap_minutes: int = 0
    quiz_minutes: int = 0
    totals: dict = Field(default_factory=dict)     # minutes per way: slides, video_in_class, video_pre_class, notebooklm, in_class,
                                                   # simulation, recap, quiz; and video_share (in class)
    prep_minutes: int = 0
    checks: list[dict] = Field(default_factory=list)   # [{code, message}] lecture-level notes
    note: str = ""                                 # the professor's note for "propose again"
    proposed_by: str = "rules"                     # rules | rules + D7
    proposed_at: str = ""
    approved_at: str = ""
    approved_by: str = ""
    materials: dict = Field(default_factory=dict)  # after approval: {"notebooklm": path, "quiz": path}


# ------------------------------------------------------------------ D7 reasons for the mix (may swap within the rules)
class MixChoice(M):
    id: str                                        # component id
    way: Way
    reason: str                                    # ≤ 25 words
    because: Literal["keep", "note", "fit", "balance"] = "keep"


class MixChoices(M):
    parts: list[MixChoice]


# ------------------------------------------------------------------ D8 closing review quiz
class QuizQuestion(M):
    component: str
    lo_ids: list[str] = Field(default_factory=list)
    bloom: int = Field(default=2, ge=1, le=6)
    question: str
    options: list[str] = Field(default_factory=list)   # 4 for a multiple-choice question, empty for a short answer
    answer: str                                    # the correct option's letter (A–D), or the model answer
    explanation: str = ""


class Quiz(M):
    questions: list[QuizQuestion]


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
