"""Lecture briefs: what each lecture covers, what it builds on and what depends on it — read from the approved design.

A lecture is one slot of the Phase 1 timetable (`schedule.weeks[].items[]`), with the same id the design graph uses
(W02.L1 = week 2, lecture 1). No AI call: everything comes from the approved design, so the brief cannot invent.
"""
from __future__ import annotations

import re
from collections import defaultdict

from profsagent.delivery.common import load_state, norm


def build_briefs(st: dict) -> list[dict]:
    tmap = {t["id"]: {**t, "module_id": m["id"], "module_title": m["title"]} for m in st["modules"] for t in m["topics"]}
    los = {lo["id"]: lo for lo in st.get("los", [])}
    cos = {c["id"]: c for c in st.get("cos", [])}
    topic_weeks = (st.get("schedule") or {}).get("topic_weeks", {})
    first_week = {t: min(w) for t, w in topic_weeks.items() if w}
    required_by = defaultdict(list)
    for t in tmap.values():
        for r in t.get("requires", []):
            required_by[r].append(t["id"])
    comps = (st.get("assessment") or {}).get("components", [])
    lt = st.get("labs_tutorials") or {}
    prereq_courses = [{"course": p["course_uid"], "kind": p.get("kind"), "relied_topics": p.get("relied_topics", [])}
                      for p in (st.get("positioning") or {}).get("prerequisites", [])]
    briefs = []
    for w in st["schedule"]["weeks"]:
        for i, it in enumerate(w["items"], 1):
            t = tmap.get(it["topic_id"])
            if not t:
                continue
            lid = f"W{w['week']:02d}.L{i}"
            lo_ids = list(t.get("serves_los", []))
            lo_set = set(lo_ids)
            dependents = [{"topic": tmap[d]["title"], "week": first_week.get(d)} for d in required_by.get(t["id"], [])
                          if d in tmap and first_week.get(d, 99) >= w["week"]]
            assessed_in = []
            for c in comps:
                for inst in c["instances"]:
                    hits = (t["id"] in inst.get("covers_topics", [])) or bool(lo_set & {a["lo_id"] for a in inst["assesses"]})
                    if hits:
                        assessed_in.append({"id": inst["id"].split(":", 1)[-1], "type": c["type"], "due_week": inst["due_week"]})
            labs = [{"week": s["week"], "title": s.get("title") or s.get("exercise", "")[:80], "tools": s.get("tools", [])}
                    for s in lt.get("labs", []) if t["id"] in s.get("uses_topics", []) or lo_set & set(s.get("practises_los", []))]
            builds_on = [{"topic": tmap[r]["title"], "week": first_week.get(r)} for r in t.get("requires", []) if r in tmap]
            co_ids = sorted({los[x]["parent_co"] for x in lo_ids if x in los})
            briefs.append({
                "lecture_id": lid, "week": w["week"], "slot": i, "hours": it["hours"],
                "topic_id": t["id"], "topic": t["title"], "module": t["module_title"],
                "continues": len(topic_weeks.get(t["id"], [])) > 1,
                "learning_outcomes": [{"id": x, "statement": los[x]["statement"], "bloom_level": los[x]["bloom_level"],
                                       "co": los[x]["parent_co"]} for x in lo_ids if x in los],
                "course_outcomes": [{"id": c, "statement": cos[c]["statement"]} for c in co_ids if c in cos],
                "builds_on": builds_on, "prerequisite_courses": prereq_courses if w["week"] <= 3 else [],
                "leads_to": dependents, "assessed_in": assessed_in, "labs": labs,
                "hands_on": bool(t.get("hands_on")), "outside_load_hours": t.get("outside_load_hours"),
                # no matching IIIT-D topic in the knowledge graph → new to IIIT-D, likely the hardest to teach
                "novel": not t.get("topic_uid"),
            })
    _mark_novel(briefs, tmap)
    for b in briefs:
        b["summary"] = summary(b)
        b["targets"] = targets(b)
    return briefs


def _mark_novel(briefs: list[dict], tmap: dict) -> None:
    """A topic is new to IIIT-D when the design linked it to no IIIT-D topic, or only to a weak match: the linked
    canonical topic's name is not semantically close to the topic title (local embeddings, same threshold the
    knowledge graph uses for topic matching)."""
    from profsagent.delivery.common import embed
    from profsagent.kg.neo4j_kg import LOCAL_TOPIC_MATCH_SIM
    pairs = {}
    for b in briefs:
        uid = tmap[b["topic_id"]].get("topic_uid")
        if uid:
            pairs[b["topic_id"]] = (b["topic"], uid.split(":", 1)[-1].replace("-", " "))
    sims = {}
    if pairs:
        keys = list(pairs)
        a = embed([pairs[k][0] for k in keys])
        c = embed([pairs[k][1] for k in keys])
        sims = {k: float(a[i] @ c[i]) for i, k in enumerate(keys)}
    for b in briefs:
        sim = sims.get(b["topic_id"])
        b["iiitd_match"] = {"topic": pairs.get(b["topic_id"], (None, None))[1], "similarity": None if sim is None else round(sim, 2)}
        b["novel"] = sim is None or sim < LOCAL_TOPIC_MATCH_SIM


BLOOM = {1: "remember", 2: "understand", 3: "apply", 4: "analyse", 5: "evaluate", 6: "create"}


def clean(statement: str) -> str:
    """Learning-outcome text for a person: template placeholders left by the design ({n} of {m}) read as plain words."""
    s = re.sub(r"\{n\}\s*of\s*\{m\}", "most", statement or "")
    return norm(re.sub(r"\{\w+\}", "the given number of", s)).rstrip(".")


def short(text: str, words: int) -> str:
    w = norm(text).rstrip(".").split()
    return " ".join(w[:words]).rstrip(",;") + (" …" if len(w) > words else "")


def summary(b: dict) -> str:
    """What the professor reads before choosing how to deliver the lecture: about 90–160 words, from the design only."""
    s = [f"A {b['hours']:g}-hour lecture in week {b['week']} on “{b['topic']}”, part of the module “{b['module']}”."]
    if b["novel"]:
        s.append("No existing IIIT-D course teaches a close match, so this is likely new material to prepare.")
    elif (b.get("iiitd_match") or {}).get("topic"):
        s.append(f"A related topic (“{b['iiitd_match']['topic']}”) is already taught at IIIT-D.")
    if b["learning_outcomes"]:
        s.append("By the end, students should be able to: " + "; ".join(
            f"{clean(x['statement'])} ({BLOOM.get(x.get('bloom_level'), 'level ' + str(x.get('bloom_level')))})"
            for x in b["learning_outcomes"][:3]) + ".")
    if b["course_outcomes"]:
        co = "This serves " + "; ".join(f"{c['id']}: {short(c['statement'], 18)}" for c in b["course_outcomes"][:2])
        s.append(co if co.endswith("…") else co + ".")
    know = [x["topic"] for x in b["builds_on"][:3]] + [f"{x['course']} ({', '.join(x['relied_topics'][:2])})" for x in b["prerequisite_courses"][:2]]
    if know:
        s.append("Students come in knowing " + "; ".join(know) + ".")
    if b["leads_to"]:
        s.append("It prepares for " + ", ".join(f"{x['topic']} (week {x['week']})" for x in b["leads_to"][:3]) + ".")
    if b["hands_on"] or b["labs"]:
        labs = [f"{x.get('title')} in week {x.get('week')}" if isinstance(x, dict) else str(x) for x in b["labs"][:2]]
        s.append("It has a hands-on part" + (f" ({'; '.join(labs)})" if labs else "") + ".")
    if b["continues"]:
        s.append("The topic continues in the next lecture.")
    if b["assessed_in"]:
        s.append("Assessed in " + ", ".join(f"{x['id']} (week {x['due_week']})" for x in b["assessed_in"][:4]) + ".")
    return " ".join(s)


def targets(b: dict) -> list[dict]:
    """What a resource must cover for this lecture: the topic and each learning outcome."""
    out = [{"id": b["topic_id"], "kind": "topic", "text": b["topic"]}]
    out += [{"id": x["id"], "kind": "lo", "text": x["statement"]} for x in b["learning_outcomes"]]
    return out


def briefs_for_run(run_id: str) -> list[dict]:
    return build_briefs(load_state(run_id))


def briefs_markdown(st: dict, briefs: list[dict]) -> str:
    L = [f"# Lecture briefs — {st['cco_compact']['course_name']}", "",
         "Read from the approved Phase 1 design (no AI). ★ = topic with no close match at IIIT-D (likely new to teach).", ""]
    for b in briefs:
        L.append(f"## {b['lecture_id']} · Week {b['week']} · {b['topic']}{' ★' if b['novel'] else ''}")
        L.append(f"*{b['module']} · {b['hours']:g} h{' · hands-on' if b['hands_on'] else ''}{' · continues next lecture' if b['continues'] else ''}*\n")
        L.append(b["summary"] + "\n")
        if b["learning_outcomes"]:
            L.append("**Learning outcomes**")
            L += [f"- {x['id']} (BL{x['bloom_level']}): {clean(x['statement'])}" for x in b["learning_outcomes"]]
        if b["builds_on"] or b["prerequisite_courses"]:
            L.append("\n**Students should already know**")
            L += [f"- {x['topic']} (week {x['week']})" for x in b["builds_on"]]
            L += [f"- {p['course']} ({p['kind']}): {', '.join(p['relied_topics'][:4])}" for p in b["prerequisite_courses"]]
        if b["leads_to"] or b["assessed_in"] or b["labs"]:
            L.append("\n**This lecture feeds into**")
            L += [f"- later topic: {x['topic']} (week {x['week']})" for x in b["leads_to"]]
            L += [f"- assessment: {x['id']} ({x['type']}, due week {x['due_week']})" for x in b["assessed_in"]]
            L += [f"- lab (week {x['week']}): {x['title']}" for x in b["labs"]]
        L.append("")
    return "\n".join(L)
