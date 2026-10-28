"""The lecture deck: what the B1 prompt returns and what the checks and the renderer read.

The AI writes only the content slides. Code adds the title, objectives and references slides (content/generate.py),
because their text is fully decided by the lecture brief and the cited sources.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class Figure(BaseModel):
    """At most one visual per slide, drawn as native PowerPoint shapes (no image generation)."""
    kind: Literal["none", "flow", "code", "table"] = "none"
    caption: str = ""
    steps: list[str] = Field(default_factory=list, description="flow: 2-6 short box labels, left to right")
    code: str = Field("", description="code: at most ~14 lines")
    language: str = ""
    rows: list[list[str]] = Field(default_factory=list, description="table: first row is the header, at most 6 rows x 4 columns")


class Quiz(BaseModel):
    """A check-for-understanding question: shown with its options, the answer and explanation go to the notes."""
    question: str
    options: list[str] = Field(default_factory=list, description="3-5 plausible options")
    answer: int = Field(0, description="index of the correct option, from 0")
    explanation: str = ""


class Slide(BaseModel):
    kind: Literal["concept", "example", "worked_problem", "activity", "check", "summary"]
    title: str
    bullets: list[str] = Field(default_factory=list)
    figure: Figure = Field(default_factory=Figure)
    quiz: Quiz | None = Field(None, description="required on a check slide")
    notes: str = Field("", description="speaker notes: what to say, 40-120 words")
    los: list[str] = Field(default_factory=list, description="ids of the lecture's learning outcomes this slide serves")
    sources: list[str] = Field(default_factory=list, description="ids of the given sources this slide draws on")
    minutes: float = 3.0


FIRST_CONTENT_SLIDE = 3   # the .pptx opens with the title and objectives slides code adds; every finding, the quiz
                          # and the handout number content slides as they appear in the .pptx
SCHEMA_VERSION = "1"   # bump when a field changes meaning; deck.json records it so old decks are recognised


class LectureDeck(BaseModel):
    schema_version: str = SCHEMA_VERSION
    lecture_id: str
    title: str
    slides: list[Slide]


# ------------------------------------------------------------------ B2: the AI reviewer's answer (content/ai_review.py)
class ReviewIssue(BaseModel):
    slide: int = Field(description="the slide number as given in the deck")
    severity: Literal["error", "warning"] = Field(description="error: students would learn something wrong; warning: unclear, "
                                                              "too hard or too easy for the level, or missing a step")
    kind: Literal["fact", "code", "quiz", "clarity", "level", "other"]
    problem: str
    fix: str = Field("", description="what the slide should say instead")


class QuizAnswer(BaseModel):
    slide: int
    answer: int = Field(description="index of the option the reviewer thinks is correct, from 0")
    why: str = ""


class DeckReview(BaseModel):
    issues: list[ReviewIssue] = Field(default_factory=list)
    quiz_answers: list[QuizAnswer] = Field(default_factory=list)
    verdict: str = Field("", description="one sentence: is the deck safe to teach from, and what most needs a look")
