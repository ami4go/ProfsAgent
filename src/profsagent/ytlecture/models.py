"""Output schemas of the sub-agents (each AI call returns one of these, validated by pydantic, then by deterministic checks)."""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class M(BaseModel):
    model_config = ConfigDict(extra="ignore")


# ---------------------------------------------------------------- Y1 part planner
class Part(M):
    title: str = Field(description="what this part teaches, as a short heading")
    teaches: str = Field(description="2-3 sentences: what a student must understand after this part")
    must_cover: list[str] = Field(description="3-6 concrete checkpoints a clip must explain (not just mention)")
    minutes: int = Field(description="minutes of video this part should get")
    kind: Literal["concept", "worked_example", "demo", "hands_on", "overview", "pitfalls"] = "concept"
    search_phrases: list[str] = Field(description="2-3 phrasings a teacher would use as a YouTube search for this part")


class LecturePlan(M):
    lecture_id: str
    parts: list[Part]


class TopicPlan(M):
    fast_moving: bool = Field(description="true when tools/APIs/standards of this topic change within a year or two")
    level_note: str = Field(description="one sentence: what the students already know and what pitch the videos need")
    lectures: list[LecturePlan]


# ---------------------------------------------------------------- Y2 scout
class Authority(M):
    name: str = Field(description="person, channel, course, conference/event or organisation")
    kind: Literal["person", "channel", "course", "event", "organisation"]
    why: str = Field(description="why they are an authority on this topic (creator of the standard, course that teaches it ...)")
    query: str = Field(description="the YouTube search that finds their teaching on this topic")
    evidence: Literal["search", "knowledge"] = Field(description="'search' if it appears in the given results, else 'knowledge'")


class PartQueries(M):
    part: int = Field(description="index of the part (0-based) within its lecture")
    lecture_id: str
    queries: list[str] = Field(description="2 YouTube searches: one plain teaching phrasing, one with an authority's name")


class ScoutReport(M):
    authorities: list[Authority]
    course_pages: list[str] = Field(default_factory=list, description="URLs from the results that are course pages listing lecture videos")
    part_queries: list[PartQueries]


# ---------------------------------------------------------------- Y3 triage
class Pick(M):
    video_id: str
    parts: list[int] = Field(description="part indices this video probably teaches")
    fit: int = Field(ge=1, le=5, description="how well title/chapters/description match those parts")
    authority: int = Field(ge=1, le=5)
    level_ok: bool = Field(description="pitched at the students' level (not a beginner pep talk, not research-only)")
    likely_standalone: bool = Field(description="a talk/lecture/tutorial whose sections can be watched on their own (not a long live-coding stream)")
    anchor: bool = Field(default=False, description="a full lecture or talk from an authoritative source that teaches several parts")
    reason: str


class Reject(M):
    video_id: str
    reason: str


class Triage(M):
    picks: list[Pick]
    rejects: list[Reject] = Field(default_factory=list)


# ---------------------------------------------------------------- Y3G grader (one part, ~15 cards; 17 Nov)
class Grade(M):
    video_id: str
    grade: int = Field(ge=0, le=3, description="3 clearly teaches this part well; 2 likely teaches it in a findable section; "
                                               "1 only touches it; 0 off-topic, promotional, wrong level or outdated")
    where: str = Field(default="", description="the chapter or time where it is taught, when the metadata shows it")
    level_ok: bool = True
    standalone: bool = Field(default=True, description="its section on this part can be watched without the rest")
    reason: str = ""


class Grades(M):
    grades: list[Grade]


class Nomination(M):
    video_id: str
    parts: list[int] = Field(description="the parts it probably teaches")
    reason: str = ""


class Nominations(M):
    nominations: list[Nomination] = Field(default_factory=list)


# ---------------------------------------------------------------- Y4 skim reader
class Window(M):
    part: int = Field(description="part index, or -1 for an on-topic region that matches no listed part")
    start: str = Field(description="m:ss or h:mm:ss, copied from a marker in the skim")
    end: str
    why: str


class SkimReading(M):
    windows: list[Window]


# ---------------------------------------------------------------- Y5 zoom reader
class ClipCut(M):
    part: int = Field(description="part index, or -1 for an EXTRA stretch that teaches the lecture's topic but no listed part")
    extra_title: str = Field(default="", description="for part -1 only: a short heading for what the extra stretch teaches")
    start: str = Field(description="marker copied exactly from the text: the line where the explanation begins")
    end: str = Field(description="marker of the last line that still teaches this part")
    start_quote: str = Field(description="the first 6-12 words spoken at start, copied exactly")
    end_quote: str = Field(description="6-12 words spoken just before end, copied exactly")
    covers: list[int] = Field(description="indices of the part's must_cover points this stretch explains")
    treatment: Literal["explains", "demonstrates", "mentions"]
    standalone: bool = Field(description="understandable without the minutes before it in this video")
    level: Literal["too_basic", "right", "too_advanced"]
    rating: int = Field(ge=1, le=5, description="teaching quality of this stretch for this part")
    concerns: str = Field(default="", description="outdated or wrong statements, adverts, room noise; empty if none")
    summary: str


class ZoomReading(M):
    clips: list[ClipCut]


# ---------------------------------------------------------------- Y6 verifier
class PointVerdict(M):
    point: int
    taught: Literal["yes", "partly", "no"]
    quote: str = Field(default="", description="words from the clip that teach it, copied exactly; empty for 'no'")


class ClipCheck(M):
    clip: str = Field(description="the clip id given")
    points: list[PointVerdict]
    standalone: bool
    accurate: bool = Field(description="no statement a professor would have to correct")
    recommend: bool
    issue: str = Field(default="")


class Verification(M):
    checks: list[ClipCheck]


# ---------------------------------------------------------------- Y7 gap resolver
class GapAction(M):
    part: int
    lecture_id: str
    action: Literal["search", "accept_gap"]
    queries: list[str] = Field(default_factory=list, description="2-3 new searches: narrower sub-concept, other vocabulary, named teacher")
    reason: str


class GapPlan(M):
    actions: list[GapAction]
