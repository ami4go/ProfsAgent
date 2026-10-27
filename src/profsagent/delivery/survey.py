"""The professor's per-lecture answers, asked before anything is searched or generated (plan §2, C2).

For every lecture the professor first reads the brief summary, then picks one or more ways to deliver it:
  own_material       teach it with my own material (nothing to do)
  attach_material    I attach my material (files / links) and ProfsAgent works with it (slides, summary, quiz, gap check …)
  generate_material  generate the lecture material (slides, notes) — deliverable B
  assistance         find learning resources: videos, readings, practice, recorded lecture, clip playlists — deliverable C
  guest_lecture      suggest guest speakers to invite — deliverable C
Several can be chosen together (e.g. own material + assistance + guest); each chosen option becomes a task.
The want_* questions are asked only when assistance is chosen.

Stored as runs/<id>/delivery/survey.yaml so a professor (or the UI, deliverable A) can fill it in:
  --init         write the questions with every answer blank ("~")
  --ask          answer them in the terminal, lecture by lecture (with "same as last" and week-level shortcuts)
  --defaults     fill blanks with test defaults (own material + assistance everywhere, guest for ★ new topics)
"""
from __future__ import annotations

import yaml

from profsagent.delivery.common import out_dir

CHOICES = [
    ("own_material", "Will you teach this lecture with your own material?"),
    ("attach_material", "Do you want to attach your own material (slides, notes, papers, links) and have ProfsAgent work with it?"),
    ("generate_material", "Do you want ProfsAgent to generate the lecture material (slides and notes)?"),
    ("assistance", "Do you want learning resources found for you (videos, blogs and readings, practice, recorded lectures)?"),
    ("guest_lecture", "Do you want suggestions for a guest speaker (expert or practitioner) to invite for this lecture?"),
]
QUESTIONS = [   # asked only when assistance is chosen
    ("want_videos", "Lecture video recommendations (short explainers, talks)?"),
    ("want_readings", "Blogs, articles, book chapters or documentation to read?"),
    ("want_practice", "Interactive material or practice (notebooks, exercises, datasets)?"),
    ("want_recorded_lecture", "A full recorded lecture from another university (flipped class)?"),
    ("want_clips", "Clip playlists (only the minutes of a long video that cover this topic)?"),
]
ATTACH_TASKS = ["slides", "summary", "quiz", "gap_check", "enrich"]   # what to do with attached material
EXTRA = [("confidence", "How confident are you teaching this topic? (1 = not at all, 5 = fully)"),
         ("note", "Anything we should know? (e.g. 'students struggle with X')")]
WANTS = [q for q, _ in QUESTIONS] + ["want_guest"]
YES = ("yes", "y", "true", "1")


def _yes(v) -> bool:
    return str(v).lower() in YES


def path(run_id: str):
    return out_dir(run_id) / "survey.yaml"


def _lecture(b: dict) -> dict:
    return {"topic": b["topic"], "week": b["week"], "new_at_iiitd": b["novel"], "summary": b["summary"],
            **{q: None for q, _ in CHOICES}, "attachments": [], "attach_tasks": [],
            **{q: None for q, _ in QUESTIONS}, "confidence": None, "note": ""}


def blank(briefs: list[dict]) -> dict:
    return {"_questions": {q: f"{t} [yes/no]" for q, t in CHOICES}
            | {"attachments": "Files or links you attach (when attach_material is yes)",
               "attach_tasks": f"What to do with them: any of {ATTACH_TASKS}"}
            | {q: f"(if assistance) {t} [yes/no]" for q, t in QUESTIONS} | {k: t for k, t in EXTRA},
            "lectures": {b["lecture_id"]: _lecture(b) for b in briefs}}


def _migrate(a: dict) -> dict:
    """Answers in the first survey format (teach_myself, want_guest) mapped to the delivery choices."""
    a = dict(a)
    if "teach_myself" in a and a.get("own_material") is None:
        a["own_material"] = "yes" if str(a.get("teach_myself")).lower() in ("yes", "partly") else "no"
    if a.get("assistance") is None and any(_yes(a.get(q)) for q, _ in QUESTIONS):
        a["assistance"] = "yes"
    if "want_guest" in a and a.get("guest_lecture") is None:
        a["guest_lecture"] = "yes" if _yes(a["want_guest"]) else "no"
    return a


def load(run_id: str) -> dict | None:
    p = path(run_id)
    return yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else None


def save(run_id: str, survey: dict) -> None:
    hdr = ("# ProfsAgent · per-lecture choices for the professor. Read the summary, then answer yes / no to each choice;\n"
           "# several can be yes. The want_* questions apply only when assistance is yes. Leave ~ for unanswered.\n")
    path(run_id).write_text(hdr + yaml.safe_dump(survey, sort_keys=False, allow_unicode=True, width=120), encoding="utf-8")


def init(run_id: str, briefs: list[dict], overwrite: bool = False) -> dict:
    old = load(run_id)
    s = blank(briefs)
    if old and not overwrite:   # keep answers already given for lectures that still exist
        for lid, ans in (old.get("lectures") or {}).items():
            if lid in s["lectures"]:
                ans = _migrate(ans)
                s["lectures"][lid].update({k: v for k, v in ans.items()
                                           if k in s["lectures"][lid] and k != "summary" and v not in (None, "", [])})
    save(run_id, s)
    return s


def apply_defaults(run_id: str, briefs: list[dict]) -> dict:
    """Test defaults for unanswered questions: own material plus resources everywhere, a guest for new topics."""
    s = load(run_id) or init(run_id, briefs)
    novel = {b["lecture_id"]: b["novel"] for b in briefs}
    for lid, a in s["lectures"].items():
        n = novel.get(lid)
        defaults = {"own_material": "yes", "attach_material": "no", "generate_material": "yes" if n else "no",
                    "assistance": "yes", "guest_lecture": "yes" if n else "no",
                    "want_videos": "yes", "want_readings": "yes", "want_practice": "yes" if n else "no",
                    "want_recorded_lecture": "no", "want_clips": "yes", "confidence": 2 if n else 4}
        for k, v in defaults.items():
            if a.get(k) in (None, ""):
                a[k] = v
    save(run_id, s)
    return s


def _yn(text: str, cur) -> str | None:
    got = input(f"   {text} [y/n]{f' ({cur})' if cur else ''}: ").strip().lower()
    return cur if not got else "yes" if got in YES else "no" if got in ("no", "n", "false", "0") else cur


def ask(run_id: str, briefs: list[dict]) -> dict:
    """Terminal questionnaire. Enter = keep the shown answer; 's' = same answers as the previous lecture;
    'w' = same answers for the rest of this week; 'q' = save and stop."""
    s = load(run_id) or init(run_id, briefs)
    bmap = {b["lecture_id"]: b for b in briefs}
    keys = [q for q, _ in CHOICES] + ["attachments", "attach_tasks"] + [q for q, _ in QUESTIONS] + ["confidence"]
    prev, week_fill = None, None
    for lid, a in s["lectures"].items():
        b = bmap.get(lid, {})
        if week_fill and week_fill[0] == a["week"]:
            a.update(week_fill[1])
            continue
        print(f"\n=== {lid} · week {a['week']} · {a['topic']}{' ★ new at IIIT-D' if a.get('new_at_iiitd') else ''}")
        print("   " + (b.get("summary") or a.get("summary") or ""))
        first = input("   [Enter] answer · [s] same as previous · [w] same for rest of week · [q] stop: ").strip().lower()
        if first == "q":
            break
        if first in ("s", "w") and prev:
            a.update(prev)
            if first == "w":
                week_fill = (a["week"], prev)
            continue
        print("   How do you want to deliver this lecture? (several can be yes)")
        for q, text in CHOICES:
            a[q] = _yn(text, a.get(q))
        if _yes(a.get("attach_material")):
            got = input("   Files or links to attach (comma-separated): ").strip()
            if got:
                a["attachments"] = [x.strip() for x in got.split(",") if x.strip()]
            got = input(f"   What should be done with them? any of {', '.join(ATTACH_TASKS)}: ").strip()
            if got:
                a["attach_tasks"] = [x.strip() for x in got.split(",") if x.strip() in ATTACH_TASKS]
        if _yes(a.get("assistance")):
            for q, text in QUESTIONS:
                a[q] = _yn(text, a.get(q))
        conf = f" ({a['confidence']})" if a.get("confidence") else ""
        got = input(f"   Confidence 1-5{conf}: ").strip()
        if got.isdigit():
            a["confidence"] = int(got)
        got = input("   Note (optional): ").strip()
        if got:
            a["note"] = got
        prev = {k: a.get(k) for k in keys}
        save(run_id, s)
    save(run_id, s)
    return s


def tasks(survey: dict) -> dict[str, dict]:
    """Per lecture, the chosen delivery options and the work each one starts (for the UI and the other deliverables)."""
    out = {}
    for lid, a in (survey or {}).get("lectures", {}).items():
        a = _migrate(a)
        chosen = [q for q, _ in CHOICES if _yes(a.get(q))]
        if chosen:
            out[lid] = {"choices": chosen, "attachments": a.get("attachments") or [], "attach_tasks": a.get("attach_tasks") or [],
                        "resources": [q[5:] for q, _ in QUESTIONS if "assistance" in chosen and _yes(a.get(q))],
                        "guest": "guest_lecture" in chosen, "confidence": a.get("confidence"), "note": a.get("note") or ""}
    return out


def requests(survey: dict) -> dict[str, dict]:
    """Lectures that asked deliverable C for something (resources and/or a guest), with what they asked for."""
    out = {}
    for lid, t in tasks(survey).items():
        wants = {q: q[5:] in t["resources"] for q, _ in QUESTIONS} | {"want_guest": t["guest"]}
        if any(wants.values()):
            out[lid] = {**wants, "confidence": t["confidence"], "note": t["note"], "choices": t["choices"]}
    return out
