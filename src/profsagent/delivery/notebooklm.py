"""NotebookLM pack per lecture: what the professor pastes into NotebookLM to make what no YouTube video delivers.

NotebookLM has no official API for its Video Overviews, quizzes or flashcards, so the system prepares everything and
the professor does the clicks: the sources to add (course context written from the approved design, the verified
videos, the readings and practice), one Video Overview prompt per component no video teaches, and quiz and flashcard
prompts for the whole lecture. No AI call: every prompt is filled from the component plan, so it cannot invent.
"""
from __future__ import annotations

from profsagent.delivery.brief import clean

STEPS_NOTE = ("NotebookLM's buttons move from time to time; if a name below differs, look for the same item in the "
              "Studio panel on the right.")


def course_context(st: dict, b: dict, comps: list[dict], earlier: list[dict]) -> str:
    cc = st["cco_compact"]
    years = "/".join(str(y) for y in (cc.get("target_students") or {}).get("years") or []) or "senior"
    L = [f"COURSE: {cc['course_name']} (IIIT-Delhi, level {st.get('level')}xx, {years}-year B.Tech students)",
         f"LECTURE: {b['lecture_id']} · week {b['week']} · {b['topic']} ({sum(c['minutes'] for c in comps)} minutes)",
         "", "LEARNING OUTCOMES (what students must be able to do):"]
    L += [f"- {clean(x['statement'])}." for x in b["learning_outcomes"]]
    if b.get("builds_on") or earlier:
        L += ["", "STUDENTS ALREADY KNOW:"]
        L += [f"- {x['topic']} (week {x['week']})" for x in b.get("builds_on", [])]
        L += [f"- {c['title']} (earlier lecture on this topic)" for c in earlier]
    L += ["", "THIS LECTURE, PART BY PART:"]
    for i, c in enumerate(comps, 1):
        L.append(f"{i}. {c['title']} ({c['minutes']} min, {c.get('kind', 'concept').replace('_', ' ')})")
        L.append(f"   Teaches: {c['teaches']}")
        if c.get("key_terms"):
            L.append(f"   Key terms: {', '.join(c['key_terms'])}")
    if b.get("leads_to"):
        L += ["", "COMES LATER (do not teach here):"] + [f"- {x['topic']} (week {x['week']})" for x in b["leads_to"]]
    return "\n".join(L)


def video_prompt(st: dict, b: dict, c: dict, before: list[dict], after: list[dict], row: dict | None = None) -> str:
    """`row`: the component's timeline row; with a `gap`, the video is a companion to the YouTube minutes shown."""
    cc = st["cco_compact"]
    years = "/".join(str(y) for y in (cc.get("target_students") or {}).get("years") or []) or "senior"
    p = [f"Make an explainer video for {years}-year B.Tech computer science students on ONE part of the lecture "
         f"\"{b['topic']}\": {c['title']}.",
         f"It must teach: {c['teaches']}"]
    gap = (row or {}).get("gap")
    if gap:
        segs = "; ".join(f"{s['start']}–{s['end']} of \"{s['video']}\"" for s in row.get("segments", []))
        p.append(f"Students also watch {segs} ({gap['video_minutes']} min), which covers part of this. Focus on what it "
                 "leaves out" + (f": {'; '.join(gap['missing'])}." if gap.get("missing") else ".") +
                 " Mention the video's part in one sentence at most.")
    if c.get("key_terms"):
        p.append(f"Explain each of these terms in plain words when it first comes up: {', '.join(c['key_terms'])}.")
    if before:
        p.append(f"Students have just covered: {'; '.join(x['title'] for x in before[-3:])}. Do not repeat it.")
    if after:
        p.append(f"Do not cover what comes next in the lecture: {'; '.join(x['title'] for x in after[:3])}.")
    p.append("Structure: (1) why this matters, in one sentence; (2) the idea step by step; (3) one concrete, worked "
             "example; (4) a two-sentence recap.")
    p.append(f"Aim for about {min(c['minutes'], 10)} minutes. Use only the sources in this notebook; do not invent tools, "
             "versions, numbers or quotes that are not in them.")
    return " ".join(p)


def quiz_prompt(b: dict, comps: list[dict]) -> str:
    hard = [c["title"] for c in comps if (c.get("bloom") or 2) >= 3]
    return (f"Quiz on the lecture \"{b['topic']}\", covering these parts: {'; '.join(c['title'] for c in comps)}. "
            f"About {min(15, max(5, 2 * len(comps)))} questions, at least one per part. Mix questions that check "
            "understanding with questions that apply an idea to a new situation" +
            (f" (especially for: {'; '.join(hard)})" if hard else "") +
            ". In each explanation, name the part the question tests. No trick questions about trivia; use only the sources.")


def flashcard_prompt(b: dict, comps: list[dict]) -> str:
    terms = list(dict.fromkeys(t for c in comps for t in c.get("key_terms") or []))
    return (f"Flashcards for revising \"{b['topic']}\": one card per key term" +
            (f" ({', '.join(terms)})" if terms else "") +
            ", and one per step of each process or mechanism taught. Front: a question; back: a one- or two-sentence "
            "answer in plain words. Use only the sources.")


def pack(st: dict, b: dict, comps: list[dict], earlier: list[dict], timeline: list[dict], sources: dict) -> tuple[str, dict]:
    """(markdown for the professor, summary for the lecture file)."""
    rows = {r["component"]: r for r in timeline}
    need = {r["component"] for r in timeline if r["delivery"] == "notebooklm" or r.get("gap")} if timeline else         {c["id"] for c in comps if not c.get("in_class")}
    todo = [c for c in comps if c["id"] in need]
    name = f"{st['cco_compact']['course_name']} · {b['lecture_id']} · {b['topic']}"
    L = [f"# NotebookLM pack · {b['lecture_id']} · {b['topic']}", "",
         f"Use this to make what no YouTube video teaches well enough for this lecture"
         f"{' — ' + str(len(todo)) + ' of ' + str(len(comps)) + ' parts' if todo else ' (every part already has a video or is taught in class: the quiz and flashcards below still help)'}, "
         "plus a quiz and flashcards for revision. NotebookLM is free at https://notebooklm.google.com with a Google account. "
         + STEPS_NOTE, ""]
    L += ["## 1 · Make the notebook", "", f"1. Open https://notebooklm.google.com → **Create new** → name it “{name}”.",
          "2. Add the sources below (**+ Add** → **Copied text** for the course context, **Website** for links, **YouTube** for videos).",
          "3. Wait until every source has loaded. Remove any that shows an error: NotebookLM uses only what loaded.", ""]
    L += ["**Sources**", "", "- Course context: the text in section 2 (as **Copied text**)."]
    for kind, label in (("video", "YouTube"), ("reading", "Website"), ("practice", "Website")):
        for x in sources.get(kind, []):
            L.append(f"- {label}: [{x['title'][:90]}]({x['url'].split('&t=')[0]})")
    L += ["", "## 2 · Course context (paste as a text source)", "", "```text", course_context(st, b, comps, earlier), "```", ""]
    if todo:
        L += ["## 3 · A video for each part no YouTube video teaches fully", "",
              "For each part: **Studio → Video Overview → Customize** (the pencil icon), format **Explainer**, language "
              "English, then paste the prompt and **Generate**. Watch it before class and check it against the sources.", ""]
        order = [c["id"] for c in comps]
        for c in todo:
            i = order.index(c["id"])
            gap = (rows.get(c["id"]) or {}).get("gap")
            L += [f"### {c['id']} · {c['title']} ({c['minutes']} min in class)" + (" · fills what the YouTube minutes leave out" if gap else ""),
                  "", "```text", video_prompt(st, b, c, earlier + comps[:i], comps[i + 1:], rows.get(c["id"])), "```", ""]
    n = 4 if todo else 3
    L += [f"## {n} · Quiz", "", "**Studio → Quiz → Customize**: number of questions **Standard**, difficulty **Medium**, then paste:", "",
          "```text", quiz_prompt(b, comps), "```", "",
          f"## {n + 1} · Flashcards", "", "**Studio → Flashcards → Customize**, then paste:", "", "```text", flashcard_prompt(b, comps), "```", "",
          f"## {n + 2} · Before class", "",
          "- Watch each generated video once: NotebookLM can still misread a source. Fix or regenerate anything wrong.",
          "- Share the notebook with students (Share → anyone with the link, viewer) if they should use the quiz and flashcards themselves.", ""]
    return "\n".join(L), {"pack": f"notebooklm/{b['lecture_id']}.md", "components": [c["id"] for c in todo],
                          "sources": sum(len(v) for v in sources.values()) + 1}
