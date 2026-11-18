"""The lecture deck: what the B1 prompt returns and what the checks and the renderer read.

The AI writes only the content slides. Code adds the title, objectives and references slides (content/generate.py),
because their text is fully decided by the lecture brief and the cited sources.
"""
from __future__ import annotations

import re
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class Series(BaseModel):
    """One layer of a plot. x, y (and y2) name lists of numbers computed by the running example (content/example.py)."""
    kind: Literal["points", "line", "bars", "segments"] = Field(description="segments: a vertical line from (x, y) to "
                                                                            "(x, y2) at each x, e.g. residuals")
    x: str = Field(description="name of the example value holding the x coordinates")
    y: str = Field(description="name of the example value holding the y coordinates")
    y2: str = Field("", description="segments: name of the value holding where each segment ends")
    label: str = Field("", description="legend text (short); empty: not in the legend")


class Plot(BaseModel):
    x_label: str = ""
    y_label: str = ""
    series: list[Series] = Field(default_factory=list, description="1-4 layers, drawn in order")
    log_y: bool = Field(False, description="a log scale on y (e.g. a loss over iterations)")


class Figure(BaseModel):
    """At most one visual per slide: flow, code and table are native PowerPoint shapes; a plot is drawn by code from
    the running example's computed values (content/slides_html.py), never from numbers the AI typed."""
    kind: Literal["none", "flow", "code", "table", "plot"] = "none"
    caption: str = ""
    steps: list[str] = Field(default_factory=list, description="flow: 2-6 short box labels, left to right")
    code: str = Field("", description="code: at most ~14 lines")
    language: str = ""
    rows: list[list[str]] = Field(default_factory=list, description="table: first row is the header, at most 6 rows x 4 columns")
    plot: Plot | None = Field(None, description="plot: what to draw from the example's values")

    @model_validator(mode="before")
    @classmethod
    def _flat_plot(cls, data):
        """Models often write a plot's fields on the figure itself ({"kind": "plot", "series": [...], "x_label": ...}):
        move them into `plot` instead of dropping them."""
        if isinstance(data, dict) and data.get("kind") == "plot" and not data.get("plot") \
                and any(k in data for k in ("series", "x_label", "y_label", "log_y")):
            data = dict(data)
            data["plot"] = {k: data.pop(k) for k in ("series", "x_label", "y_label", "log_y") if k in data}
        return data


class Quiz(BaseModel):
    """A check-for-understanding question: shown with its options, the answer and explanation go to the notes."""
    question: str
    options: list[str] = Field(default_factory=list, description="3-5 plausible options")
    answer: int = Field(0, description="index of the correct option, from 0")
    explanation: str = ""

    @field_validator("question", "options", "explanation")
    @classmethod
    def _maths(cls, v):
        return [unescape_latex(x, maths_only=True) for x in v] if isinstance(v, list) else unescape_latex(v, maths_only=True)


_CTRL = {"\t": "\\t", "\b": "\\b", "\f": "\\f", "\r": "\\r", "\v": "\\v"}
_INLINE = re.compile(r"\\\(.*?\\\)", re.S)


def unescape_latex(s: str, maths_only: bool = False) -> str:
    r"""Undo a JSON escape the model did not double: "\to", "\beta", "\frac", "\rho", "\nabla" written with one backslash
    arrive as a tab, backspace, form feed, carriage return or newline followed by the rest of the command. Tab,
    backspace, form feed, CR and VT never belong on a slide, so they are always restored; a newline only when a letter
    follows it inside maths (`maths_only`: s is plain text with inline \( \) maths)."""
    if not isinstance(s, str) or not any(c in s for c in "\t\b\f\r\v\n"):
        return s
    s = "".join(_CTRL.get(c, c) for c in s)
    if maths_only:
        return _INLINE.sub(lambda m: re.sub(r"\n(?=[A-Za-z])", r"\\n", m.group()), s)
    return re.sub(r"\n(?=[A-Za-z])", r"\\n", s)


class Step(BaseModel):
    """One line of a derivation, with the rule that takes the previous line to this one."""
    latex: str = Field(description="the line as LaTeX, without $ or \\[ \\] delimiters")
    why: str = Field("", description="the rule or move that gives this line (at most 10 words); empty on the first line")

    @field_validator("latex")
    @classmethod
    def _latex(cls, v: str) -> str:
        return unescape_latex(v)


class Block(BaseModel):
    """Teaching blocks shown below the bullets, in order (rendered by content/slides_html.py with KaTeX).
    math: one display formula. steps: a derivation, one line per step with its reason. definition: a term and its meaning.
    think: a question students answer before the teacher explains. note: a short boxed remark (a takeaway, a warning)."""
    kind: Literal["math", "steps", "definition", "think", "note"]
    latex: str = Field("", description="math: the formula as LaTeX, without delimiters")
    steps: list[Step] = Field(default_factory=list, description="steps: 2-6 lines")
    term: str = Field("", description="definition: the term")
    text: str = Field("", description="definition: its meaning; think: the question; note: the remark. Inline maths as \\( ... \\)")

    @field_validator("latex")
    @classmethod
    def _latex(cls, v: str) -> str:
        return unescape_latex(v)

    @field_validator("term", "text")
    @classmethod
    def _text(cls, v: str) -> str:
        return unescape_latex(v, maths_only=True)


KINDS_FOR_PARTS = ("recap", "watch", "debrief", "bridge", "simulation", "quiz")   # with deliverable C's outline / mix


class Slide(BaseModel):
    kind: Literal["concept", "example", "worked_problem", "activity", "check", "summary",
                  "recap", "watch", "debrief", "bridge", "simulation", "quiz", "answer"]
    title: str
    bullets: list[str] = Field(default_factory=list, description="inline maths as \\( ... \\)")

    @field_validator("title", "bullets")
    @classmethod
    def _maths(cls, v):
        return [unescape_latex(x, maths_only=True) for x in v] if isinstance(v, list) else unescape_latex(v, maths_only=True)
    blocks: list[Block] = Field(default_factory=list, description="formulas, derivation steps, definitions, think "
                                                                  "questions and notes, below the bullets")
    figure: Figure = Field(default_factory=Figure)
    quiz: Quiz | None = Field(None, description="required on a check slide")
    notes: str = Field("", description="speaker notes: what to say, 40-120 words")
    los: list[str] = Field(default_factory=list, description="ids of the lecture's learning outcomes this slide serves")
    sources: list[str] = Field(default_factory=list, description="ids of the given sources this slide draws on")
    minutes: float = 3.0
    component: str = Field("", description="id of the lecture.outline part this slide teaches (when an outline is given)")
    # filled by code from the outline, never by the AI (content/generate.fill_from_outline): what to watch or open
    clip: str = ""
    link: str = ""


FIRST_CONTENT_SLIDE = 3   # the .pptx opens with the title and objectives slides code adds; every finding, the quiz
                          # and the handout number content slides as they appear in the .pptx
SCHEMA_VERSION = "3"   # bump when a field changes meaning; deck.json records it so old decks are recognised
                       # 2: slide kinds for C's delivery mix, `component`, `clip`, `link` (version 1 decks still load)
                       # 3: `blocks` (maths, derivation steps, definitions; version 1-2 decks load with none)


class LectureDeck(BaseModel):
    schema_version: str = SCHEMA_VERSION
    lecture_id: str
    title: str
    slides: list[Slide]


# ------------------------------------------------------------------ B7 / B8: plan the deck, then one slide per call (content/plan.py)
ROLES = ("opening", "motivation", "definition", "intuition", "derivation", "worked_example", "method", "code",
         "evaluation", "interpretation", "limits", "misconception", "check", "summary", "recap", "watch", "debrief",
         "bridge", "simulation", "activity", "quiz", "other")
LIMIT_ROLES = ("limits", "misconception", "failure")      # "failure": the name before 2026-11-15


class PlanSlide(BaseModel):
    kind: Literal["concept", "example", "worked_problem", "activity", "check", "summary",
                  "recap", "watch", "debrief", "bridge", "simulation", "quiz"]
    title: str
    role: str = Field(description="what the slide does in the lecture: " + ", ".join(ROLES))
    teaches: str = Field(description="the ONE idea students take from this slide, one sentence")
    los: list[str] = Field(default_factory=list)
    values: list[str] = Field(default_factory=list, description="names of the running example's values the slide shows")
    visual: Literal["none", "steps", "math", "plot", "code", "table", "flow"] = "none"
    answers_opening: bool = Field(False, description="true on the slide that answers the opening question")
    minutes: float = 3.0
    component: str = ""
    material: str = Field("", description="with the professor's material: what this slide takes from it, cited P1…")


class DeckPlan(BaseModel):
    title: str
    opening_question: str = Field("", description="the concrete question the first content slide poses")
    key_results: list[str] = Field(default_factory=list, description="what a standard treatment of the topic must "
                                   "teach, decided before the slides; an item left out says '(not covered: why)'")
    slides: list[PlanSlide]


# ------------------------------------------------------------------ B6: the running example (content/example.py)
class ValueName(BaseModel):
    name: str = Field(description="the key the code assigns in `values` (letters, digits and _)")
    meaning: str = Field(description="what the value is, in a few words, e.g. 'slope of the fitted line'")


class Example(BaseModel):
    """One small example carried through the whole lecture. The AI writes the data and the code; code runs it, and every
    number the slides show comes from what it computed."""
    numeric: bool = Field(description="false for a case without quantities (then only title and story: the case)")
    title: str = ""
    story: str = Field("", description="the setting students see, 1-2 sentences (a non-numeric case: 2-4)")
    conventions: list[str] = Field(default_factory=list, description="definitions with their constant factors and "
                                   "normalisation, units, signs, indexing: what the slides must use too")
    code: str = Field("", description="Python (numpy allowed) that assigns a dict `values`")
    names: list[ValueName] = Field(default_factory=list, description="every key of `values`, with its meaning")


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


# ------------------------------------------------------------------ B3: the professor's own material (content/attach.py)
class AttachedQuestion(Quiz):
    source: str = Field("", description="the part of the material it comes from: P1, P2 …")


class Gap(BaseModel):
    lo_id: str
    status: Literal["covered", "partly", "missing"]
    evidence: str = ""
    add: str = Field("", description="what the professor should add for this outcome")


class Enrichment(BaseModel):
    kind: Literal["example", "figure", "check_question", "activity", "reading"]
    where: str = ""
    add: str


class AttachedReport(BaseModel):
    summary: str = ""
    key_points: list[str] = Field(default_factory=list)
    quiz: list[AttachedQuestion] = Field(default_factory=list)
    gaps: list[Gap] = Field(default_factory=list)
    issues: list[str] = Field(default_factory=list, description="statements that look outdated or wrong, quoted")
    enrich: list[Enrichment] = Field(default_factory=list)


# ------------------------------------------------------------------ B4 / B5: a class taught as 3-4 parts (content/lesson.py)
class PlanPart(BaseModel):
    title: str
    los: list[str] = Field(default_factory=list, description="ids of the learning outcomes this part teaches")
    teaches: str = Field(description="what students understand or can do after this part, in one or two sentences")
    key_ideas: list[str] = Field(default_factory=list, description="3-5 ideas, in the order they are taught")
    example: str = Field("", description="the worked example or demonstration that makes the part concrete")
    minutes: int = Field(10, description="video minutes, quiz included")


class LessonPlan(BaseModel):
    parts: list[PlanPart]


class TeachingSlide(BaseModel):
    title: str
    bullets: list[str] = Field(default_factory=list, description="2-4 short anchors (at most 12 words), never the script")
    figure: Figure = Field(default_factory=Figure)
    narration: str = Field(description="what the teacher says over this slide: 150-220 words of real teaching")
    refs: list[str] = Field(default_factory=list, description="ids of the reference passages it draws on, e.g. C3#12")


class TeachingPart(BaseModel):
    slides: list[TeachingSlide]
    quiz: list[Quiz] = Field(default_factory=list, description="3 questions on this part")
    recap: str = Field("", description="2-3 sentences that close the part before its quiz")
