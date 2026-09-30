"""Pydantic output models for every LLM prompt (the `output_model` named in each prompt's front-matter).

Policy: fields that validators or downstream code depend on are required; everything else is optional.
Extra keys are ignored (logged by the client via the raw output), so harmless additions don't burn retries.
"""
from __future__ import annotations

from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class M(BaseModel):
    model_config = ConfigDict(extra="ignore", populate_by_name=True)


class Concern(M):
    about: Optional[str] = None
    detail: Optional[str] = None


class Missing(M):
    field: Optional[str] = None
    reason: Optional[str] = None


class Source(M):
    tag: str
    ref: Optional[str] = None
    basis: Optional[str] = None


class Base(M):
    concerns: list[Concern] = Field(default_factory=list)
    missing: list[Missing] = Field(default_factory=list)


# ------------------------------------------------------------------ G1 intake → CCO
class Field_(M):
    status: Literal["given", "missing", "ambiguous"]
    raw: Optional[Any] = None
    value: Optional[Any] = None


class TopicItem(M):
    id: str
    text: str


class TopicGroup(M):
    id: str
    title: str
    topics: list[TopicItem] = Field(default_factory=list)


class TopicsField(Field_):
    topics_treatment: Literal["fixed", "hypotheses", "missing"] = "missing"
    topic_groups: list[TopicGroup] = Field(default_factory=list)


class NegConstraint(M):
    id: str
    raw: str
    checkable_form: Optional[str] = None
    checkable: bool = False


class IntentField(Field_):
    central_question: Optional[str] = None
    pedagogical_emphasis: Optional[str] = None
    negative_constraints: list[NegConstraint] = Field(default_factory=list)


class StudentsField(Field_):
    programmes: list[str] = Field(default_factory=list)
    unmapped_programmes: list[str] = Field(default_factory=list)
    years: list[int] = Field(default_factory=list)
    assumed_background: list[str] = Field(default_factory=list)


class LevelField(Field_):
    code: Optional[str] = None
    level: Optional[int] = None


class LTPField(Field_):
    L: Optional[float] = None
    T: Optional[float] = None
    P: Optional[float] = None


class LabField(Field_):
    required: Optional[Literal["yes", "no"]] = None
    infrastructure: list[str] = Field(default_factory=list)


class AssessPrefField(Field_):
    preferred: list[str] = Field(default_factory=list)
    avoid: list[str] = Field(default_factory=list)
    rationale: Optional[str] = None


class SpecialItem(M):
    id: str
    text: str


class SpecialField(Field_):
    items: list[SpecialItem] = Field(default_factory=list)


class CurriculumField(Field_):
    answers: dict[str, Optional[str]] = Field(default_factory=dict)


class CCOFields(M):
    course_name: Field_
    short_description: Field_
    topics: TopicsField
    intent: IntentField
    target_students: StudentsField
    level_or_code: LevelField
    credits: Field_
    ltp: LTPField
    semester_weeks: Field_
    weekly_effort_hours: Field_
    lab: LabField
    assessment_prefs: AssessPrefField
    special_constraints: SpecialField
    curriculum_context: CurriculumField


class Conflict(M):
    fields: list[str] = Field(default_factory=list)
    detail: str = ""
    regulation_ref: Optional[str] = None


class Ambiguity(M):
    field: str
    interpretations: list[str] = Field(default_factory=list)


class CourseContextObject(Base):
    fields: CCOFields
    ambiguities: list[Ambiguity] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)


# ------------------------------------------------------------------ X1 search planning / X2 page reading
class SearchQuery(M):
    query: str
    target_institutions: list[str] = Field(default_factory=list)
    equivalent_titles: list[str] = Field(default_factory=list)
    why: Optional[str] = None


class SearchPlan(Base):
    equivalent_course_titles: list[str] = Field(default_factory=list)
    distinguishing_keywords: list[str] = Field(default_factory=list)
    queries: list[SearchQuery]
    catalogue_keywords: list[str] = Field(default_factory=list)


class ExtWeek(M):
    week: Optional[str] = None
    topics: list[str] = Field(default_factory=list)


class ExtAssessment(M):
    component: str
    weight_pct: Optional[float] = None


class ExternalPage(Base):
    page_type: Literal["single_course_page", "course_catalogue_entry", "programme_page", "catalogue_index",
                       "faculty_or_directory", "news_or_blog", "other"]
    institution_id: Optional[str] = None
    course_code: Optional[str] = None
    course_title: Optional[str] = None
    term: Optional[str] = None
    level: Optional[str] = None
    summary: Optional[str] = None
    learning_outcomes: list[str] = Field(default_factory=list)
    topics: list[str] = Field(default_factory=list)
    weekly_sequence: list[ExtWeek] = Field(default_factory=list)
    assessment: list[ExtAssessment] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)
    textbooks: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    pedagogy_notes: Optional[str] = None
    evidence_quotes: list[str] = Field(default_factory=list)
    relevance: Literal["high", "medium", "low", "none"] = "low"
    relevance_reason: Optional[str] = None


# ------------------------------------------------------------------ G2 positioning
class Existence(M):
    verdict: Literal["distinct", "near_duplicate", "partial_duplicate"]
    closest: list[str] = Field(default_factory=list)
    reason: str = ""
    recommendation: str = ""


class Overlap(M):
    course_uid: str
    weighted_jaccard: Optional[float] = None
    shared_topics: list[str] = Field(default_factory=list)
    verdict: Literal["substantive", "superficial", "complementary"]
    differentiation: str = ""


class Prereq(M):
    kind: Literal["mandatory", "desirable"]
    course_uid: str
    alternatives: list[str] = Field(default_factory=list)
    relied_topics: list[str] = Field(default_factory=list)
    needed_by: list[str] = Field(default_factory=list)
    justification: str = ""
    level_check: Literal["lower_level", "taken_earlier_by_cohort", "failed"] = "lower_level"
    sources: list[Source] = Field(default_factory=list)


class BgMap(M):
    background_item: str
    supplied_by: list[str] = Field(default_factory=list)
    status: Literal["mapped", "no_supplying_course"] = "mapped"


class AntiReq(M):
    course_uid: str
    weighted_jaccard: Optional[float] = None
    reason: str = ""


class Checked(M):
    course_uid: str
    weighted_jaccard: Optional[float] = None


class Comparable(M):
    kind: Literal["internal", "external"]
    ref: str
    title: str = ""
    take: str = ""
    avoid: str = ""


class POGap(M):
    po_uid: str
    reason: str = ""


class PositioningDecision(Base):
    existence: Existence
    overlaps: list[Overlap] = Field(default_factory=list)
    prerequisites: list[Prereq] = Field(default_factory=list)
    background_mapping: list[BgMap] = Field(default_factory=list)
    anti_requisites: list[AntiReq] = Field(default_factory=list)
    checked_candidates: list[Checked] = Field(default_factory=list)
    comparable: list[Comparable] = Field(default_factory=list)
    po_gap_hints: list[POGap] = Field(default_factory=list)


# ------------------------------------------------------------------ G3 constraints
class TypedConstraint(M):
    id: str
    target: str
    op: str
    value: Optional[Any] = None
    hardness: Literal["hard", "soft"]
    raw: str = ""
    source: Optional[Source] = None
    note: Optional[str] = None


class CConflict(M):
    ids: list[str] = Field(default_factory=list)
    reason: str = ""


class Untranslatable(M):
    raw: str = ""
    source: Optional[str] = None
    why: str = ""


class TypedConstraints(Base):
    constraints: list[TypedConstraint] = Field(default_factory=list)
    conflicts: list[CConflict] = Field(default_factory=list)
    untranslatable: list[Untranslatable] = Field(default_factory=list)


# ------------------------------------------------------------------ G4 COs
def _lvl(v):
    return int(v) if v is not None else v


class CODraft(M):
    id: str
    statement: str
    verb: str
    behaviour: str
    condition: str
    degree: str
    bloom_level: int = Field(ge=1, le=6)
    knowledge_dimension: Literal["factual", "conceptual", "procedural", "metacognitive"]
    covers_topic_groups: list[str] = Field(default_factory=list)
    evidence_types: list[str] = Field(default_factory=list)
    builds_on_prereq_topics: list[str] = Field(default_factory=list)
    differentiation_note: Optional[str] = None
    nc_risks: list[str] = Field(default_factory=list)
    rationale: str = ""
    sources: list[Source] = Field(default_factory=list)

    _v = field_validator("bloom_level", mode="before")(_lvl)


class TGProposal(M):
    action: Literal["drop", "merge", "add", "reorder"]
    targets: list[str] = Field(default_factory=list)
    proposal: str = ""
    reason: str = ""


class CODraftSet(Base):
    cos: list[CODraft]
    topic_group_proposals: list[TGProposal] = Field(default_factory=list)
    level_distribution: dict[str, int] = Field(default_factory=dict)


# ------------------------------------------------------------------ G5 CO–PO
class COPOLink(M):
    co_id: str
    po_uid: str
    strength_provisional: int = Field(ge=1, le=3)
    co_phrase: str = ""
    po_phrase: str = ""
    justification: str = ""
    evidencing_activities: list[str] = Field(default_factory=list)


class UnmappedPO(M):
    po_uid: str
    reason: str = ""


class COPOProposal(Base):
    mappings: list[COPOLink]
    unmapped_pos: list[UnmappedPO] = Field(default_factory=list)


# ------------------------------------------------------------------ G6 LOs
class TopicHint(M):
    phrase: str
    topic_uid: Optional[str] = None


class LODraft(M):
    id: str
    parent_co: str
    statement: str
    verb: str
    behaviour: str
    condition: str
    degree: str
    bloom_level: int = Field(ge=1, le=6)
    knowledge_dimension: Literal["factual", "conceptual", "procedural", "metacognitive"]
    is_capstone: bool = False
    requires: list[str] = Field(default_factory=list)
    topic_hints: list[TopicHint] = Field(default_factory=list)
    hands_on: bool = False
    est_lecture_h: float = 0
    est_tutorial_h: float = 0
    est_lab_h: float = 0
    hours_basis: str = ""
    suggested_task_type: Optional[str] = None
    sources: list[Source] = Field(default_factory=list)

    _v = field_validator("bloom_level", mode="before")(_lvl)


class LODraftSet(Base):
    los: list[LODraft]
    hours_total: dict[str, float] = Field(default_factory=dict)


# ------------------------------------------------------------------ G7 structure
class CourseTopicDraft(M):
    id: str
    title: str
    est_hours: float = Field(gt=0)
    hours_basis: str = ""
    serves_los: list[str]
    covers_topic_groups: list[str] = Field(default_factory=list)
    requires: list[str] = Field(default_factory=list)
    topic_uid: Optional[str] = None
    hands_on: bool = False
    suggested_order: int = 0
    sources: list[Source] = Field(default_factory=list)


class ModuleDraft(M):
    id: str
    title: str
    order: int
    primary_cos: list[str] = Field(default_factory=list)
    topics: list[CourseTopicDraft]


class CutCandidate(M):
    topic_id: str
    hours: Optional[float] = None
    impact: str = ""


class ConstraintNote(M):
    constraint_id: str
    note: str = ""


class StructureDraft(Base):
    modules: list[ModuleDraft]
    hours_total: Optional[float] = None
    cut_candidates: list[CutCandidate] = Field(default_factory=list)
    constraint_notes: list[ConstraintNote] = Field(default_factory=list)


# ------------------------------------------------------------------ G8 lab / tutorial
class LabSessionDraft(M):
    week: int
    id: str
    title: str = ""
    exercise: str
    practises_los: list[str] = Field(default_factory=list)
    uses_topics: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    hours: float = 2
    produces_assessed_artifact: Optional[str] = None
    notes: Optional[str] = None


class TutorialDraft(M):
    week: int
    id: str
    activity: str
    practises_los: list[str] = Field(default_factory=list)
    uses_topics: list[str] = Field(default_factory=list)
    hours: float = 1


class InfraReq(M):
    item: str
    for_weeks: list[int] = Field(default_factory=list)
    status: Literal["available", "needs_confirmation"] = "needs_confirmation"
    source: Optional[str] = None


class LabTutorialPlan(Base):
    labs: list[LabSessionDraft] = Field(default_factory=list)
    tutorials: list[TutorialDraft] = Field(default_factory=list)
    infra_requirements: list[InfraReq] = Field(default_factory=list)


# ------------------------------------------------------------------ G9 assessment
class LOAssess(M):
    lo_id: str
    marks_pct_of_instance: float
    bloom_level: int = Field(ge=1, le=6)

    _v = field_validator("bloom_level", mode="before")(_lvl)


class AssessInstance(M):
    id: str
    release_week: int
    due_week: int
    format: str = ""
    covers_topics: list[str] = Field(default_factory=list)
    assesses: list[LOAssess]
    est_student_hours: float = 0
    feeds_from_lab: Optional[str] = None


class Component(M):
    type: str
    weight_pct: float
    weight_justification: Optional[str] = None
    best_k: Optional[int] = None
    n: Optional[int] = None
    activity_types: list[str] = Field(default_factory=list)
    integrity: Optional[str] = None
    instances: list[AssessInstance]


class UnsupportedPO(M):
    co_id: str
    po_uid: str
    reason: str = ""


class AssessmentBlueprint(Base):
    components: list[Component]
    weight_sum: Optional[float] = None
    unsupported_po_predictions: list[UnsupportedPO] = Field(default_factory=list)


# ------------------------------------------------------------------ G10 resources
class Identifier(M):
    isbn: Optional[str] = None
    doi: Optional[str] = None
    arxiv: Optional[str] = None
    url: Optional[str] = None


class TopicSupport(M):
    topic_id: str
    reason: str = ""


class ResourcePick(M):
    candidate_id: str
    role: Literal["primary", "reference", "reading"]
    title: str
    authors: list[str] = Field(default_factory=list)
    year: Optional[int] = None
    edition: Optional[str] = None
    venue: Optional[str] = None
    identifier: Identifier = Field(default_factory=Identifier)
    supports_topics: list[TopicSupport] = Field(default_factory=list)
    sources: list[Source] = Field(default_factory=list)


class SearchRequest(M):
    need: str
    for_topics: list[str] = Field(default_factory=list)


class ResourceCandidates(Base):
    textbook_policy: Literal["textbook", "reading_list", "mixed"]
    policy_reason: str = ""
    resources: list[ResourcePick] = Field(default_factory=list)
    search_requests: list[SearchRequest] = Field(default_factory=list)


# ------------------------------------------------------------------ G11 narrative
class Narrative(Base):
    course_description: str
    sequencing_rationale: str = ""
    assessment_rationale: str = ""
    positioning_rationale: str = ""
    grounding: list[str] = Field(default_factory=list)


# ------------------------------------------------------------------ R1 repair
class PatchOp(M):
    op: Literal["update", "add", "remove"]
    id: Optional[str] = None
    field: Optional[str] = None
    value: Optional[Any] = None
    node: Optional[dict] = None
    for_violation: Optional[str] = None


class Collateral(M):
    id: str
    reason: str = ""


class Unfixable(M):
    violation: str
    blocked_by: Optional[str] = None
    explanation: str = ""


class LeftWarning(M):
    violation: str
    reason: str = ""


class RepairPatch(Base):
    ops: list[PatchOp] = Field(default_factory=list)
    collateral: list[Collateral] = Field(default_factory=list)
    unfixable: list[Unfixable] = Field(default_factory=list)
    left_warnings: list[LeftWarning] = Field(default_factory=list)


class ResQuery(M):
    kind: Literal["book", "paper"] = "book"
    query: str
    for_modules: list[str] = Field(default_factory=list)
    why: Optional[str] = None


class ResourceQueryPlan(Base):
    queries: list[ResQuery]


OUTPUT_MODELS = {
    "G1": CourseContextObject, "X1": SearchPlan, "X2": ExternalPage, "G2": PositioningDecision, "G3": TypedConstraints,
    "G4": CODraftSet, "G5": COPOProposal, "G6": LODraftSet, "G7": StructureDraft, "G8": LabTutorialPlan,
    "G9": AssessmentBlueprint, "G10": ResourceCandidates, "X3": ResourceQueryPlan, "G11": Narrative, "R1": RepairPatch,
}
