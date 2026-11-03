"""Component plans: what each lecture teaches, piece by piece and minute by minute (D5 + program checks).

A topic is often taught over several lectures (W01.L2 and W02.L1 both teach "Model context protocols"). The topic's
whole lecture time is planned at once, so a later lecture gets the topic's later components instead of leftovers.
Each component says what students must learn (`teaches`, `key_terms`), its kind, Bloom level, LOs and minutes; it is
then delivered by verified video segments (segments.py), a NotebookLM video the professor makes (notebooklm.py), or
in class (activities, discussions). Deliverable B builds its slides on the same plan.

Each lecture keeps a few minutes free for the opening recap and the closing review quiz (mix.reserve_for; recorded as
`reserved` and `lecture_minutes` in the plan's lectures), so the components add up to the rest.

The AI proposes; the program enforces the time rules (minutes add up per lecture, within bounds, multiples of
`round_to`) and repairs small misses itself. A plan it cannot repair is asked for again once with the problems
listed; failing that, a plan is built from the learning outcomes without AI.
"""
from __future__ import annotations

from profsagent.delivery.brief import clean
from profsagent.delivery.common import rcfg
from profsagent.delivery.models import ComponentPlan


def minutes_of(b: dict) -> int:
    step = rcfg()["components"]["round_to"]
    return max(step, int(round(b["hours"] * 60 / step)) * step)


def topic_groups(briefs: dict) -> dict[str, list[dict]]:
    """topic_id -> its lectures in timetable order."""
    out: dict[str, list[dict]] = {}
    for lid in sorted(briefs):
        out.setdefault(briefs[lid]["topic_id"], []).append(briefs[lid])
    return out


def _fit_minutes(mins: list[int], total: int) -> list[int] | None:
    """Scale minutes to add up to `total`, in multiples of round_to and within bounds; None if impossible."""
    c = rcfg()["components"]
    step, lo, hi = c["round_to"], c["min_minutes"], c["max_minutes"]
    n = len(mins)
    if not n or not (n * lo <= total <= n * hi):
        return None
    raw = [m * total / sum(mins) for m in mins] if sum(mins) else [total / n] * n
    out = [min(hi, max(lo, int(round(x / step)) * step)) for x in raw]
    order = sorted(range(n), key=lambda i: -(raw[i] - out[i]))      # largest shortfall first
    while sum(out) != total:
        diff = total - sum(out)
        moved = False
        for i in (order if diff > 0 else reversed(order)):
            nxt = out[i] + (step if diff > 0 else -step)
            if lo <= nxt <= hi:
                out[i] = nxt
                moved = True
                break
        if not moved:
            return None
    return out


def check_plan(comps: list[dict], lectures: list[dict], lo_ids: list[str]) -> tuple[list[dict], list[str]]:
    """Repair what the program can (minutes) and list what it cannot. Returns (components, problems)."""
    c = rcfg()["components"]
    problems = []
    want = {x["lecture_id"]: x["minutes"] for x in lectures}
    order = [x["lecture_id"] for x in lectures]
    comps = [x for x in comps if x["lecture_id"] in want]
    # lecture order must follow the timetable
    if [x["lecture_id"] for x in comps] != sorted((x["lecture_id"] for x in comps), key=order.index):
        comps = sorted(comps, key=lambda x: order.index(x["lecture_id"]))
    for lid, total in want.items():
        mine = [x for x in comps if x["lecture_id"] == lid]
        if not mine:
            problems.append(f"lecture {lid} has no components; it needs components adding up to {total} minutes")
            continue
        fixed = _fit_minutes([x["minutes"] for x in mine], total)
        if fixed is None:
            problems.append(f"lecture {lid}: {len(mine)} components cannot add up to {total} minutes with each between "
                            f"{c['min_minutes']} and {c['max_minutes']} minutes; use about {max(1, round(total / c['target_minutes']))} components")
            continue
        for x, m in zip(mine, fixed):
            if m != x["minutes"]:
                x["minutes_proposed"] = x["minutes"]
            x["minutes"] = m
    known = set(lo_ids)
    for x in comps:
        x["lo_ids"] = [i for i in x.get("lo_ids", []) if i in known]
        if len(x.get("teaches", "").split()) < 8:
            problems.append(f"component '{x['title']}' needs a concrete 'teaches' description (2–3 sentences)")
    missing = known - {i for x in comps for i in x["lo_ids"]}
    if missing:
        problems.append(f"learning outcomes not served by any component: {', '.join(sorted(missing))}")
    return comps, problems


def fallback_plan(group: list[dict], minutes: dict[str, int] | None = None) -> list[dict]:
    """No AI: one component per learning outcome (cycled), minutes split evenly — honest, but generic. `minutes`: the
    component minutes per lecture (the lecture less its recap and quiz); default the whole lecture."""
    c = rcfg()["components"]
    los = [lo for lo in group[0]["learning_outcomes"]] or [{"id": None, "statement": group[0]["topic"], "bloom_level": 2}]
    out, k = [], 0
    for b in group:
        total = (minutes or {}).get(b["lecture_id"]) or minutes_of(b)
        n = max(1, min(len(los), round(total / c["target_minutes"]))) if total >= 2 * c["min_minutes"] else 1
        while n > 1 and _fit_minutes([1] * n, total) is None:
            n -= 1
        mins = _fit_minutes([1] * n, total) or [total]
        for m in mins:
            lo = los[k % len(los)]
            k += 1
            text = clean(lo["statement"])
            out.append({"lecture_id": b["lecture_id"], "title": f"{b['topic']}: part {k}", "teaches": text + ".",
                        "key_terms": [], "kind": "concept", "bloom": lo.get("bloom_level") or 2,
                        "lo_ids": [lo["id"]] if lo.get("id") else [], "minutes": m})
    return out


def for_window(run_id: str, lecture_id: str, start_min: float = 0, minutes: float | None = None) -> list[dict]:
    """The components of `lecture_id` taught in minutes [start_min, start_min + minutes) of it, in order: what a class
    session (deliverable B's W03.S1, which may cover only part of a lecture) should teach. Each comes with `from_min`,
    and with `minutes_here` when the window cuts it. [] when the lecture has no plan yet."""
    from profsagent.delivery.common import out_dir, read_json
    plans = read_json(out_dir(run_id) / "components.json", {}) or {}
    comps = [c for p in plans.values() for c in p["components"] if c["lecture_id"] == lecture_id]
    lec = next((x for p in plans.values() for x in p.get("lectures", []) if x["lecture_id"] == lecture_id), {})
    res = lec.get("reserved") or {}
    if comps and res.get("recap"):              # the recap opens the lecture and the quiz closes it
        comps = [{"id": f"{lecture_id}.RECAP", "lecture_id": lecture_id, "title": "Recap of the previous lecture", "kind": "recap",
                  "teaches": "Two or three questions on the previous lecture, answered and discussed.", "key_terms": [],
                  "bloom": 2, "lo_ids": [], "minutes": res["recap"], "in_class": False}] + comps
    if comps and res.get("quiz"):
        comps = comps + [{"id": f"{lecture_id}.QUIZ", "lecture_id": lecture_id, "title": "Review quiz", "kind": "quiz",
                          "teaches": "One question per part of this lecture, then the answers.", "key_terms": [],
                          "bloom": 2, "lo_ids": [], "minutes": res["quiz"], "in_class": False}]
    end = float("inf") if minutes is None else start_min + minutes
    out, t = [], 0.0
    for c in comps:
        a, z = t, t + c["minutes"]
        t = z
        if z <= start_min or a >= end:
            continue
        here = min(z, end) - max(a, start_min)
        out.append({**c, "from_min": a, **({"minutes_here": round(here)} if here < c["minutes"] else {})})
    return out


def plan_topic(llm, st: dict, group: list[dict], run_id: str, log) -> dict:
    """Component plan for one topic over its lectures: {topic_id, lectures, components, via, problems}."""
    from profsagent.delivery.mix import _first_lecture, reserve_for
    from profsagent.delivery.resources import llm_call
    first = group[0]
    course_first = _first_lecture(run_id)
    lectures = []
    for b in group:                                   # minutes for the components: the lecture less its recap and quiz
        recap, quiz = reserve_for(minutes_of(b), b["lecture_id"] == course_first)
        lectures.append({"lecture_id": b["lecture_id"], "minutes": minutes_of(b) - recap - quiz, "lecture_minutes": minutes_of(b),
                         "reserved": {"recap": recap, "quiz": quiz}})
    lo_ids = [x["id"] for x in first["learning_outcomes"]]
    c = rcfg()["components"]
    ctx = {"course": {"course_name": st["cco_compact"]["course_name"], "level": st.get("level"),
                      "years": (st["cco_compact"].get("target_students") or {}).get("years")},
           "topic": {"topic_id": first["topic_id"], "topic": first["topic"], "module": first["module"],
                     "learning_outcomes": [{"id": x["id"], "statement": clean(x["statement"]), "bloom_level": x["bloom_level"]}
                                           for x in first["learning_outcomes"]],
                     "builds_on": [x["topic"] for x in first.get("builds_on", [])],
                     "leads_to": [x["topic"] for x in first.get("leads_to", [])],
                     "hands_on": any(b.get("hands_on") for b in group), "novel": first.get("novel")},
           "lectures": [{"lecture_id": x["lecture_id"], "minutes": x["minutes"]} for x in lectures],
           "limits": {k: c[k] for k in ("min_minutes", "max_minutes", "target_minutes", "round_to")}, "problems": []}
    comps, problems, via = None, [], "fallback (no AI)"
    for attempt in range(2):
        try:
            plan = llm_call(llm, "D5", ctx, ComponentPlan, run_id, log)
        except Exception as e:  # noqa: BLE001 — no model left: fall back to the outcome-based plan
            log(f"  [D5] failed for {first['topic_id']} ({type(e).__name__}); plan built from the learning outcomes")
            break
        got, problems = check_plan([x.model_dump() for x in plan.components], lectures, lo_ids)
        if not any("has no components" in p or "cannot add up" in p for p in problems):
            comps, via = got, "AI (D5)"
            break
        log(f"  [D5] plan for {first['topic_id']} rejected: {'; '.join(problems)[:200]}")
        ctx["problems"] = problems
    if comps is None:
        comps, problems = fallback_plan(group, {x["lecture_id"]: x["minutes"] for x in lectures}), []
    n = {}
    for x in comps:                                   # ids: W03.L1.C1, W03.L1.C2, ...
        n[x["lecture_id"]] = n.get(x["lecture_id"], 0) + 1
        x["id"] = f"{x['lecture_id']}.C{n[x['lecture_id']]}"
        x["in_class"] = x.get("kind") in c["in_class_kinds"]
    log(f"  components {first['topic_id']}: {len(comps)} over {len(group)} lecture(s) via {via}")
    return {"topic_id": first["topic_id"], "topic": first["topic"], "lectures": lectures, "components": comps,
            "via": via, "problems": [p for p in problems if "has no components" not in p and "cannot add up" not in p]}
