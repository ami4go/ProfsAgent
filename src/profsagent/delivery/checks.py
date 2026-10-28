"""Hard rules in code for delivery items (plan §6). Same finding format as Phase 1: code, severity, message.

Errors remove the item before the professor sees it (the next-ranked candidate takes its place);
warnings are shown next to the item.
"""
from __future__ import annotations

import re

from profsagent.delivery.common import rcfg

ERR, WARN = "error", "warning"
EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
HANDS_ON = ("repository", "notebook", "exercises", "exercise", "lab", "dataset")
HANDS_ON_SITES = ("github.com", "colab.research.google.com", "kaggle.com", ".ipynb", "exercism.org", "leetcode.com")
PAPER_SITES = ("arxiv.org", "doi.org", "dl.acm.org", "ieeexplore.ieee.org", "semanticscholar.org", "openreview.net")


def f(code: str, sev: str, msg: str) -> dict:
    return {"code": code, "severity": sev, "message": msg}


def resource(c: dict, b: dict) -> list[dict]:
    out = []
    if c.get("dead"):
        out.append(f("R-LINK", ERR, c["dead"]))
        return out
    if c["kind"] in ("video", "recorded_lecture"):
        if not c.get("public", True):
            out.append(f("R-LINK", ERR, "video is not public"))
        if not c.get("embeddable", True):
            out.append(f("R-EMBED", WARN, "video cannot be embedded in the course page (link only)"))
        if c.get("blocked_in_india"):
            out.append(f("R-REGION", ERR, "video is not available in India"))
        if c.get("made_for_kids"):
            out.append(f("R-LEVEL", ERR, "video is made for children"))
        if not c.get("duration_s"):
            out.append(f("R-META", ERR, "duration unknown"))
        elif c["kind"] == "video" and c["duration_s"] > rcfg()["durations"]["video_max"]:
            out.append(f("R-DURATION", ERR, f"too long for a lecture resource ({c['duration_s'] // 60} min); offer it as a recorded lecture instead"))
        if not c.get("captions"):
            out.append(f("R-CAPTIONS", WARN, "no captions"))
        lang = (c.get("language") or "en").lower()
        if not (lang.startswith("en") or lang.startswith("hi")):
            out.append(f("R-LANG", ERR, f"audio language is '{lang}'"))
    cov = c.get("coverage") or {}
    per = cov.get("per_target", {})
    topic = per.get(b["topic_id"], {})
    if not cov or not per:
        out.append(f("R-COVER", ERR, "no evidence about what it covers"))
    elif not any(v["covered"] for v in per.values()):
        out.append(f("R-COVER", ERR, "covers neither the lecture topic nor any of its learning outcomes"))
    elif not topic.get("covered") and cov.get("score", 0) < 0.3:
        out.append(f("R-COVER", WARN, "covers some learning outcomes but not the lecture topic itself"))
    if cov.get("evidence") in ("metadata", "title"):
        out.append(f("R-EVIDENCE", WARN, f"coverage judged from the {cov['evidence']} only (no transcript or text)"))
    for v in per.values():
        for s in v.get("segments", []):
            if c.get("duration_s") and not (0 <= s["start"] < s["end"] <= c["duration_s"] + 5):
                out.append(f("R-TIMESTAMP", ERR, "a clip timestamp lies outside the video"))
    r = c.get("review")
    if r and r.get("explains") == "off_topic":
        out.append(f("R-REVIEW", ERR, "AI review: off topic (" + "; ".join(r.get("issues", [])[:2]) + ")"))
    elif r and r.get("explains") == "mentions":
        out.append(f("R-REVIEW", WARN, "AI review: mentions the topic but does not really teach it"))
    if r and r.get("correctness", 5) <= 2:
        out.append(f("R-REVIEW", WARN, "AI review: possible inaccuracies (" + "; ".join(r.get("issues", [])[:2]) + ")"))
    if c["kind"] in ("reading", "practice"):
        url = (c.get("url") or "").lower()
        social = next((d for d in rcfg().get("social_domains", []) if d in url), None)
        if social:
            out.append(f("R-SOURCE", ERR, f"a social-media post ({social}), not a reading"))
        if r and r.get("generic"):
            out.append(f("R-GENERIC", ERR, "AI review: a general introduction to a broader concept, not this lecture's topic"))
    if c["kind"] == "practice":
        url = (c.get("url") or "").lower()
        if c.get("page_type") == "paper" or any(s in url for s in PAPER_SITES):
            out.append(f("R-PRACTICE", ERR, "a paper is not practice material"))
        elif r and r.get("hands_on") is False:
            out.append(f("R-PRACTICE", ERR, "AI review: nothing for students to do (no exercises, notebook, code or lab)"))
        elif not r and not ((c.get("page_type") or "").lower() in HANDS_ON or any(s in url for s in HANDS_ON_SITES)):
            out.append(f("R-PRACTICE", WARN, "not checked to be hands-on (no exercises, notebook or code seen)"))
    if c.get("page_type") == "book" and not (c.get("identifier") or {}).get("isbn") and not c.get("record"):
        out.append(f("R-BOOK", ERR, "book has no library record"))
    return out


def expert(e: dict) -> list[dict]:
    out = []
    if not e.get("verified_identity"):
        out.append(f("X-IDENTITY", ERR, "identity not confirmed in any authoritative source"))
    if not e.get("evidence"):
        out.append(f("X-EVIDENCE", ERR, "no evidence of expertise on this topic"))
    blob = " ".join(str(v) for v in e.values())
    if EMAIL.search(blob):
        out.append(f("X-PRIVACY", ERR, "personal contact data present"))
    note = e.get("note") or {}
    if note.get("fit") == "weak":
        out.append(f("X-FIT", ERR, "AI check: evidence is only weakly related to this lecture"))
    for c in note.get("concerns", [])[:2]:
        out.append(f("X-CONCERN", WARN, c))
    if e.get("venue_quality") is not None and e["venue_quality"] < 0.45:
        out.append(f("X-VENUE", WARN, "relevant papers appear in little-known or low-reputation venues; check before inviting"))
    if e.get("latest_year") and e["latest_year"] < 2019:
        out.append(f("X-RECENCY", WARN, f"latest relevant evidence is from {e['latest_year']}"))
    return out
