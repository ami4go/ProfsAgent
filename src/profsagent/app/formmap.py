"""The app's course form → the pipeline's 14-field form and run config (same shape as eval/inputs/_TEMPLATE.yaml).

Only the course name and description are required. Every other field the professor leaves blank is filled in by
ProfsAgent first (app/filler.py) and confirmed by the professor before the design starts, so the pipeline receives
a complete form.
"""
from __future__ import annotations

import re

NOT_SPECIFIED = "[NOT SPECIFIED]"
NO_TOPICS = "[NOT SPECIFIED — propose the topics from the description and the course intent]"
DEPARTMENTS = ["CSE", "ECE", "Math", "SSH", "HCD", "CB"]
PROGRAMMES = ["B.Tech CSE", "B.Tech CSAI", "B.Tech CSB", "B.Tech CSD", "B.Tech CSSS", "B.Tech CSAM", "B.Tech ECE", "B.Tech EVE", "M.Tech CSE", "M.Tech ECE", "PhD"]
YEARS = {"1st year": "1xx level (first year)", "2nd year": "2xx level (second year)", "3rd / 4th year": "3xx–4xx level (third / fourth year)",
         "Postgraduate": "5xx–6xx level (postgraduate)"}
LAB = {"weekly": "yes, a lab every week", "none": "no"}
ASSESSMENTS = ["Quizzes", "Assignments", "Labs", "Project", "Mid-sem", "End-sem", "Presentations", "Participation"]
CREDITS = ["1", "2", "4"]   # UGREG-2025§4(2): courses are 4, 2 or 1 credit

# every field ProfsAgent can fill in when the professor leaves it blank, in form order
FILLABLE = ["topics", "intent_question", "intent_emphasis", "intent_avoid", "department", "credits", "l", "t", "p", "weeks",
            "weekly_effort", "programmes", "year", "background", "lab", "lab_infra", "assess_pref", "assess_avoid", "assess_why", "special"]
LISTS = {"programmes", "assess_pref", "assess_avoid"}
# what must have a value before the design can start (after ProfsAgent's suggestions and the professor's check)
NEEDED = {"topics": "List the topics, one group per line", "department": "Pick the proposing department",
          "credits": "Pick the credits", "weeks": "Give the number of teaching weeks", "programmes": "Pick at least one programme",
          "year": "Pick the year", "lab": "Say whether the course has a lab"}


def _s(v) -> str:
    return str(v if v is not None else "").strip()


def _lines(v) -> list[str]:
    return [x.strip(" -•\t") for x in _s(v).splitlines() if x.strip(" -•\t")]


def _hours(v: str) -> float | None:
    try:
        x = float(v)
    except ValueError:
        return None
    return x if 0 <= x <= 8 and (x * 2).is_integer() else None


def blank(f: dict, key: str) -> bool:
    v = f.get(key)
    if key in LISTS:
        return not v
    if key == "lab":
        return _s(v) not in LAB
    return not _s(v)


def _check_values(f: dict, e: dict) -> None:
    """Values that are given must be valid (blank ones are fine here)."""
    if _s(f.get("credits")) and _s(f.get("credits")) not in CREDITS:
        e["credits"] = "IIIT-D courses are 1, 2 or 4 credits (UG Regulations 2025, §4(2))"
    if any(_s(f.get(k)) for k in ("l", "t", "p")) and any(_hours(_s(f.get(k))) is None for k in ("l", "t", "p") if _s(f.get(k))):
        e["ltp"] = "Hours per week are numbers from 0 to 8, in steps of 0.5 (a 2-credit course has 1.5 lecture hours)"
    w = _s(f.get("weeks"))
    if w and (not w.isdigit() or not 1 <= int(w) <= 16):
        e["weeks"] = "Teaching weeks must be a number from 1 to 16"
    if _s(f.get("department")) and _s(f.get("department")) not in DEPARTMENTS:
        e["department"] = "Pick the proposing department"


def validate(f: dict) -> dict[str, str]:
    """Field → message for what the professor must fix before ProfsAgent can fill in the rest."""
    e: dict[str, str] = {}
    if len(_s(f.get("name"))) < 3:
        e["name"] = "Give the course a name"
    if len(_s(f.get("description"))) < 30:
        e["description"] = "Write a short description (two or three sentences)"
    _check_values(f, e)
    return e


def validate_complete(f: dict) -> dict[str, str]:
    """Before the design starts: the form must be complete (after ProfsAgent's suggestions and the professor's edits)."""
    e = dict(validate(f))
    for k, msg in NEEDED.items():
        if blank(f, k):
            e.setdefault(k, msg)
    if any(not _s(f.get(k)) for k in ("l", "t", "p")):
        e.setdefault("ltp", "Give the lecture, tutorial and lab hours per week")
    return e


def to_pipeline(f: dict) -> tuple[dict, dict]:
    """(form, run_cfg) for agents.pipeline.make_runtime. A field still empty becomes [NOT SPECIFIED] (the pipeline then
    infers it and lists it as an assumption)."""
    topics = _lines(f.get("topics"))
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    topic_lines = [t if re.match(r"^[A-Z][.)]\s", t) else f"{letters[i % 26]}. {t}" for i, t in enumerate(topics)]
    treatment = ("starting hypotheses — may add/drop/reorder with justification" if f.get("topics_flexible", True)
                 else "fixed — keep these topics; do not add or drop any")
    avoid_lines = _lines(f.get("intent_avoid"))
    intent = (f"Central question the course answers: {_s(f.get('intent_question')) or NOT_SPECIFIED}\n"
              f"Pedagogical emphasis: {_s(f.get('intent_emphasis')) or NOT_SPECIFIED}\n"
              "This course should NOT become:\n" + ("\n".join(f"- {x}" for x in avoid_lines) if avoid_lines else f"- {NOT_SPECIFIED}"))
    year = _s(f.get("year"))
    students = (f"Programmes: {', '.join(f.get('programmes') or []) or NOT_SPECIFIED}\n"
                f"Year: {year or NOT_SPECIFIED}\n"
                f"Assumed background: {_s(f.get('background')) or NOT_SPECIFIED}")
    l, t, p = (_s(f.get(k)) for k in ("l", "t", "p"))
    lab = (f"Lab required: {LAB.get(_s(f.get('lab')), NOT_SPECIFIED)}\n"
           f"Available infrastructure: {_s(f.get('lab_infra')) or NOT_SPECIFIED}")
    pref, avoid = f.get("assess_pref") or [], f.get("assess_avoid") or []
    assess = (f"Preferred components: {', '.join(x.lower() for x in pref) or NOT_SPECIFIED}\n"
              f"Components to avoid: {', '.join(x.lower() for x in avoid) or 'none'}\n"
              f"Rationale: {_s(f.get('assess_why'))}")
    effort = _s(f.get("weekly_effort"))
    nums = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", effort)]
    if len(nums) == 2:   # the pipeline reads one number ("10-12" is ambiguous to it): send the middle of the range
        mid = (nums[0] + nums[1]) / 2
        effort = str(int(mid)) if mid.is_integer() else str(mid)
    form = {
        "1. COURSE NAME": _s(f.get("name")),
        "2. SHORT COURSE DESCRIPTION": _s(f.get("description")),
        "3. TOPICS / CONTENT AREAS": (f"Treatment of this list: {treatment}\n" + "\n".join(topic_lines)) if topic_lines else NO_TOPICS,
        "4. COURSE INTENT": intent,
        "5. TARGET STUDENTS": students,
        "6. EXPECTED LEVEL / COURSE CODE": f"{YEARS[year]}; code to be assigned" if year in YEARS else NOT_SPECIFIED,
        "7. CREDITS": _s(f.get("credits")) or NOT_SPECIFIED,
        "8. L-T-P / CONTACT HOURS": f"{l}-{t}-{p} ({l} lecture, {t} tutorial and {p} lab hours per week)" if l and t and p else NOT_SPECIFIED,
        "9. SEMESTER LENGTH": f"{_s(f.get('weeks'))} teaching weeks" if _s(f.get("weeks")) else NOT_SPECIFIED,
        "10. WEEKLY STUDENT EFFORT": f"{effort} hours a week outside lectures (labs, tutorials, homework, self-study)" if effort else NOT_SPECIFIED,
        "11. LAB / PRACTICAL COMPONENT": lab,
        "12. ASSESSMENT PREFERENCES": assess,
        "13. SPECIAL CONSTRAINTS": _s(f.get("special")) or "[NONE]",
        "14. CURRICULUM CONTEXT": "[NOT SUPPLIED — derive curriculum positioning from the institutional knowledge graph.]",
    }
    slug = re.sub(r"[^A-Z0-9]+", "-", _s(f.get("name")).upper()).strip("-")[:24] or "COURSE"
    run_cfg = {"project_id": f"P-APP-{slug}", "exclude_courses": [], "blocklist": {"domains": [], "course_codes": [], "title_fragments": []},
               "external_research": bool(f.get("external_research", True)), "department": _s(f.get("department")) or "CSE"}
    return form, run_cfg
