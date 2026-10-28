"""Class sessions: the week's lecture hours as the classes actually taught (config/content.yaml `classes`).

The Phase 1 schedule gives each week topic chunks (e.g. 2 h of one topic and 1 h of the next), and the delivery briefs
(delivery/brief.py, deliverable C) keep one "lecture" per chunk, so their lengths vary from 0.25 h to 2.5 h. IIIT-D
teaches the L hours as fixed classes (2 × 90 min for L = 3), so B makes one deck per class: the week's chunks are packed
into its classes in schedule order, and a class may finish one topic and start the next.

A session has the brief's fields (so lecture_input, gather_sources and frame read it the same way) plus `parts`: the
briefs it draws on, with the minutes of each. Ids are W03.S1, W03.S2, …; the briefs keep their W03.L1 ids for C and the UI.
"""
from __future__ import annotations

from profsagent.delivery.brief import build_briefs

UNION = ("learning_outcomes", "course_outcomes", "builds_on", "prerequisite_courses", "leads_to", "assessed_in", "labs")


def _union(lists: list[list]) -> list:
    out, seen = [], set()
    for xs in lists:
        for x in xs or []:
            k = x.get("id") or repr(sorted(x.items())) if isinstance(x, dict) else repr(x)
            if k not in seen:
                seen.add(k)
                out.append(x)
    return out


def build_sessions(st: dict, per_week: int, minutes: int, briefs: list[dict] | None = None) -> list[dict]:
    briefs = briefs if briefs is not None else build_briefs(st)
    by_week: dict[int, list[dict]] = {}
    for b in briefs:
        by_week.setdefault(b["week"], []).append(b)
    out = []
    for week in sorted(by_week):
        chunks = [[b, b["hours"]] for b in by_week[week]]
        share = sum(b["hours"] for b in by_week[week]) / per_week        # topic hours each class covers
        for slot in range(1, per_week + 1):
            need, parts = share, []
            while need > 1e-9 and chunks:
                b, left = chunks[0]
                take = min(need, left)
                parts.append((b, take))
                chunks[0][1] -= take
                need -= take
                if chunks[0][1] <= 1e-9:
                    chunks.pop(0)
            if parts:
                out.append(_session(week, slot, minutes, share, parts))
    return out


def _session(week: int, slot: int, minutes: int, share: float, parts: list[tuple[dict, float]]) -> dict:
    bs = [b for b, _ in parts]
    first = bs[0]
    s = {"lecture_id": f"W{week:02d}.S{slot}", "week": week, "slot": slot, "hours": minutes / 60,
         "topic_id": first["topic_id"], "topic": " · ".join(dict.fromkeys(b["topic"] for b in bs)),
         "module": " · ".join(dict.fromkeys(b["module"] for b in bs)),
         "hands_on": any(b.get("hands_on") for b in bs), "novel": any(b.get("novel") for b in bs),
         "parts": [{"lecture_id": b["lecture_id"], "topic_id": b["topic_id"], "topic": b["topic"],
                    "minutes": round(h / share * minutes)} for b, h in parts]}
    for k in UNION:
        s[k] = _union([b.get(k) for b in bs])
    return s


def is_session(lecture_id: str) -> bool:
    return ".S" in lecture_id
