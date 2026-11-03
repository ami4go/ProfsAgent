"""The delivery mix: how each part (component) of a lecture is delivered, proposed by rules, explained by the AI and
decided by the professor (doc "Lecture delivery mix — design proposal", 2 Nov; docs/decisions.md 30).

A part is delivered one way: slides (taught live), youtube (a checked stretch teaches all of it), youtube_bridge
(stretches teach most of it; 1–3 slides add the rest), notebooklm (a NotebookLM video the professor makes), in_class (an
activity or discussion) or simulation (students operate one with a task from the slide). Each lecture opens with a short
recap of the previous one and closes with a review quiz; D5 keeps those minutes free (components.py, `reserve`).

  propose(run, lecture, locked, note)   rules (config/delivery_mix.yaml) -> lecture checks -> D7 reasons -> checks again;
                                        writes delivery/mix/<lecture>.json (status "proposed"), and the NotebookLM pack
                                        for the proposed NotebookLM parts only
  save(run, lecture, changes, ...)      the professor's ways, locks and preset (each change logged in
                                        delivery/app_mix_changes.jsonl); approve=True also makes the materials
  materials(run, lecture)               after approval: the NotebookLM pack and the quiz (D8, delivery/quiz/<lecture>.json
                                        and .md, with the recap taken from the previous lecture's quiz)
  course_style(run, style)              "slides" | "mix" | "flipped", asked once per course (delivery/mix/course.json)

The rules, in order (the first that matches wins; the preset limits which ways can match):
  R1   in class: an activity or discussion; a worked example or case study at Bloom 4+
  R1b  simulation: a process, mechanism or algorithm at Bloom 2–4 with a matching simulation (Amit's rule)
  P    the professor's own habit, once they have made enough changes (preferences)
  R2   youtube: a stretch teaches the part fully, clarity and level fit >= 4, 0.6–1.3 x the part's minutes
  R3   youtube_bridge: stretches teach it partly and cover >= 60% of its minutes
  R4   notebooklm: a concept, mechanism or comparison; the notebook's sources cover >= 60% of its key terms; the
       professor's confidence <= 3 or a new topic
  R5   slides
Then the lecture as a whole: the first part is taught live, at most 2 NotebookLM videos, at most 4 switches of way,
video in class at most 40% of the minutes (longer clips and the excess are watched before class). A part the professor
set or locked is never changed by the program; it only gets a note.
"""
from __future__ import annotations

import json
import re
import time
from functools import lru_cache
from pathlib import Path

from profsagent.config import load_yaml
from profsagent.delivery.common import load_state, now, out_dir, rcfg, read_json, write_json
from profsagent.delivery.models import LectureMix, MixChoices, Quiz

VIDEO_WAYS = ("youtube", "youtube_bridge", "notebooklm")
LABEL = {"slides": "slides", "youtube": "a YouTube stretch", "youtube_bridge": "YouTube stretches plus bridge slides",
         "notebooklm": "a NotebookLM video", "in_class": "in class", "simulation": "a simulation"}


@lru_cache(maxsize=None)
def mcfg() -> dict:
    return load_yaml("config/delivery_mix.yaml")


def _dir(run_id: str) -> Path:
    return out_dir(run_id) / "mix"


def load(run_id: str, lecture_id: str) -> dict | None:
    return read_json(_dir(run_id) / f"{lecture_id}.json")


def _save(run_id: str, m: dict) -> dict:
    m = LectureMix(**m).model_dump()          # the file always has the documented shape
    write_json(_dir(run_id) / f"{m['lecture_id']}.json", m)
    return m


def course_style(run_id: str, style: str | None = None) -> str:
    """The course's delivery style ("slides" | "mix" | "flipped"); with `style`, set it."""
    p = _dir(run_id) / "course.json"
    if style is not None:
        if style not in mcfg()["course_styles"]:
            raise ValueError(f"unknown course style {style!r}")
        write_json(p, {"style": style, "set_at": now()})
        return style
    return (read_json(p) or {}).get("style") or "mix"


# ------------------------------------------------------------------ minutes kept for the recap and the quiz
def reserve_for(minutes: int, first: bool) -> tuple[int, int]:
    """(recap, quiz) minutes kept free in a lecture of `minutes`; the course's first lecture has no recap."""
    r = mcfg()["reserve"]
    quiz = next((q for m, q in r["quiz"] if minutes >= m), 0)
    recap = 0 if first else next((q for m, q in r["recap"] if minutes >= m), 0)
    return recap, quiz


def _first_lecture(run_id: str) -> str | None:
    ids = [b["lecture_id"] for b in read_json(out_dir(run_id) / "briefs.json", []) or []]
    return min(ids) if ids else None


# ------------------------------------------------------------------ evidence for one lecture
def _words(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", (s or "").lower()))


def term_found(term: str, text: str, words: set[str]) -> bool:
    """A key term is in the sources when the phrase is, or every word of 4+ letters in it is (any order)."""
    t = term.lower().strip()
    if not t:
        return True
    if t in text:
        return True
    big = [w for w in re.findall(r"[a-z0-9]+", t) if len(w) >= 4]
    return bool(big) and all(w in words for w in big)


def source_texts(resources: dict) -> list[str]:
    """Text of what the NotebookLM notebook would hold: the transcripts of the lecture's videos (from the cache only, so
    no request to YouTube) and the readings and practice pages (cached fetch)."""
    from profsagent.delivery.sources import _cache_path
    from profsagent.research.fetch import fetch
    out = []
    items = resources.get("items") or {}
    for v in items.get("video") or []:
        d = read_json(_cache_path("transcript", v["id"])) if v.get("id") else None
        if d and isinstance(d.get("v"), list):
            out.append(" ".join(x["text"] for x in d["v"]))
        out.append(f"{v.get('title', '')} {v.get('description', '')}")
    for k in ("reading", "practice"):
        for x in items.get(k) or []:
            try:
                out.append((fetch(x["url"], max_age_s=60 * 86400) or {}).get("text") or "")
            except Exception:  # noqa: BLE001 — an unreachable page simply adds nothing
                pass
            out.append(f"{x.get('title', '')} {x.get('description', '')}")
    return out


def coverage(terms: list[str], texts: list[str]) -> tuple[float | None, list[str]]:
    if not terms:
        return None, []
    text = " \n ".join(texts).lower()
    words = set(re.findall(r"[a-z0-9]+", text))
    missing = [t for t in terms if not term_found(t, text, words)]
    return round(1 - len(missing) / len(terms), 2), missing


def match_simulations(comps: list[dict]) -> dict[str, list[dict]]:
    """Simulations per component, when the app gives none (Amit's app/simulations.match_parts is preferred): the
    catalogue (similarity >= 0.60) and links to trusted sites (>= 0.65), with the app's local model; no AI calls."""
    try:
        import numpy as np

        from profsagent.sims import catalogue as C
        from profsagent.sims import classify as K
        from profsagent.sims import external as X
    except Exception:  # noqa: BLE001 — simulations not installed: no candidates
        return {}
    r = mcfg()["rules"]
    try:
        live = [e for e in C.entries() if e.get("status") != "retired"]
        xs = X.entries()
        ents = [(e, "catalogue", [e["title"]] + list(e["topics"]) + [e["title"] + ": " + ", ".join(e["topics"])]) for e in live]
        ents += [(x, "link", X.text_for_matching(x)) for x in xs]
        if not ents or not comps:
            return {}
        texts, owner = [], []
        for i, (_, _, ts) in enumerate(ents):
            texts += ts
            owner += [i] * len(ts)
        E = K.embed(texts)
        Q = K.embed([c["title"] for c in comps] + [c["title"] + ": " + ", ".join(c.get("key_terms") or []) for c in comps])
        n = len(comps)
        S = np.maximum(Q[:n] @ E.T, Q[n:] @ E.T)
        owner = np.array(owner)
    except Exception:  # noqa: BLE001 — the local model could not load: no candidates rather than a failed mix
        return {}
    out = {}
    for k, c in enumerate(comps):
        best: dict[int, float] = {}
        for j in np.argsort(-S[k])[:80]:
            i = int(owner[j])
            best[i] = max(best.get(i, 0.0), float(S[k, j]))
        got = []
        for i, sc in best.items():
            e, kind, _ = ents[i]
            if sc < (r["simulation_catalogue_min"] if kind == "catalogue" else r["simulation_link_min"]):
                continue
            got.append({"id": e["id"], "url": e.get("url"), "title": e["title"], "score": round(sc, 3),
                        "source": e.get("site_name") or ("built" if e["id"].startswith("auto.") else "catalogue")})
        if got:
            out[c["id"]] = sorted(got, key=lambda x: -x["score"])[:3]
    return out


def gather(run_id: str, lecture_id: str, sims: dict | None = None) -> dict:
    """Everything the rules look at for one lecture."""
    d = out_dir(run_id)
    lec = read_json(d / "lectures" / f"{lecture_id}.json") or {}
    if not lec.get("components"):
        raise ValueError(f"{lecture_id} has no component plan yet: run recommend first")
    briefs = {b["lecture_id"]: b for b in read_json(d / "briefs.json", []) or []}
    b = briefs.get(lecture_id) or {}
    try:
        from profsagent.delivery import survey as sv
        survey = sv._migrate(dict(((sv.load(run_id) or {}).get("lectures") or {}).get(lecture_id) or {}))
    except Exception:  # noqa: BLE001
        survey = {}
    res = lec.get("resources") or {}
    rows = {r["component"]: r for r in res.get("timeline") or []}
    vid_q = {v["id"]: v.get("scores") or {} for v in (res.get("items") or {}).get("video", []) if v.get("id")}
    clip_c = {}
    for k in res.get("clips") or []:
        clip_c.setdefault(k["component"], []).append(k)
    texts = source_texts(res)
    if sims is None:
        sims = match_simulations(lec["components"])
    plans = read_json(d / "components.json", {}) or {}
    plan_lec = next((x for p in plans.values() for x in p.get("lectures", []) if x["lecture_id"] == lecture_id), {})
    return {"lecture": lec, "brief": b, "survey": survey, "rows": rows, "video_quality": vid_q, "clips": clip_c,
            "texts": texts, "sims": sims or {}, "plan_lecture": plan_lec, "briefs": briefs}


# ------------------------------------------------------------------ rules for one part
def _segments(row: dict, vq: dict) -> list[dict]:
    out = []
    for s in row.get("segments") or []:
        q = vq.get(s.get("video_id")) or {}
        out.append({**s, "clarity": s.get("clarity") or round((q.get("clarity") or 0.6) * 5),
                    "level_fit": s.get("level_fit") or round((q.get("level_fit") or 0.6) * 5)})
    return out


def evidence(c: dict, g: dict, minutes: int) -> dict:
    """What supports each way for one part: stretches, their share of the part, source coverage, a simulation."""
    r = mcfg()["rules"]
    row = g["rows"].get(c["id"]) or {}
    segs = _segments(row, g["video_quality"])
    vmin = round(sum(s["minutes"] for s in segs), 1)
    lo, hi = r["youtube_length"]
    full = [s for s in segs if s["verdict"] == "teaches_fully" and s["clarity"] >= r["youtube_min_clarity"]
            and s["level_fit"] >= r["youtube_min_level_fit"] and lo <= s["minutes"] / max(minutes, 1) <= hi]
    cov, uncovered = coverage(c.get("key_terms") or [], g["texts"])
    missing = list((row.get("gap") or {}).get("missing") or [])
    if not missing:
        missing = [m for k in g["clips"].get(c["id"], []) for m in k.get("missing", [])]
    sim = (g["sims"].get(c["id"]) or [None])[0]
    allowed = ["slides", "in_class"]
    if full:
        allowed.append("youtube")
    if segs:
        allowed.append("youtube_bridge")
    if cov is None or cov >= r["notebooklm_min_coverage"]:
        allowed.append("notebooklm")
    if sim:
        allowed.append("simulation")
    return {"segments": segs, "full": full, "video_minutes": vmin, "share": vmin / max(minutes, 1), "coverage": cov,
            "uncovered": uncovered, "missing": list(dict.fromkeys(missing))[:6], "simulation": sim, "allowed": allowed}


def possible_ways(ev: dict) -> list[str]:
    """Ways the professor may pick for a part: a video way needs stretches, a simulation needs one; NotebookLM and
    slides and in class are always possible (NotebookLM with a warning when its sources miss terms)."""
    out = ["slides", "in_class", "notebooklm"]
    if ev["segments"]:
        out += ["youtube", "youtube_bridge"]
    if ev["simulation"]:
        out.append("simulation")
    return out


def _sim_text(c: dict) -> bool:
    r = mcfg()["rules"]
    if c.get("kind") in r["simulation_always"]:
        return True
    return bool(re.search(rf"\b({r['simulation_words']})", f"{c['title']} {c.get('teaches', '')}", re.I))


def candidates(c: dict, ev: dict, g: dict, prefs: dict) -> list[tuple[str, str]]:
    """[(way, rule)] in rule order: the first is the choice, the next one the alternative."""
    r = mcfg()["rules"]
    kind, bloom = c.get("kind") or "concept", c.get("bloom") or 2
    out = []
    if kind in r["in_class_kinds"] or (kind in r["in_class_hard_kinds"] and bloom >= r["in_class_hard_bloom"]):
        out.append(("in_class", "R1"))
    lo, hi = r["simulation_bloom"]
    if ev["simulation"] and kind in r["simulation_kinds"] and lo <= bloom <= hi and _sim_text(c):
        out.append(("simulation", "R1b"))
    p = prefs.get(kind)
    if p and p["way"] in possible_ways(ev):
        out.append((p["way"], "P"))
    if ev["full"]:
        out.append(("youtube", "R2"))
    if ev["segments"] and ev["share"] >= r["bridge_min_share"]:
        out.append(("youtube_bridge", "R3"))
    conf = g["survey"].get("confidence")
    if (kind in r["notebooklm_kinds"] and not ev["full"] and "notebooklm" in ev["allowed"]
            and ((conf or 99) <= r["notebooklm_max_confidence"] or g["brief"].get("novel"))):
        out.append(("notebooklm", "R4"))
    out.append(("slides", "R5"))
    if ev["segments"] and not any(w in ("youtube", "youtube_bridge") for w, _ in out):
        out.append(("youtube_bridge", "alt"))            # shown as the alternative: a clip plus slides
    return list(dict.fromkeys(out))


def _fmt_segs(segs: list[dict]) -> str:
    return "; ".join(f"{s['start']}–{s['end']} of \"{s['video'][:60]}\"" for s in segs[:2])


def rule_reason(way: str, rule: str, c: dict, ev: dict, g: dict, prefs: dict) -> str:
    """The reason a rule gives, in one line (D7 rewrites it when AI is on)."""
    mins = max(c["minutes"], 1)
    if rule == "R1":
        return f"{c.get('kind', '').replace('_', ' ').capitalize()} at Bloom {c.get('bloom')}: students do it in class; the slides carry the task and the debrief."
    if rule == "R1b":
        s = ev["simulation"]
        return f"Students operate \"{s['title']}\" ({s['source']}, match {s['score']:.2f}) with a task from the slide."
    if rule == "P":
        p = prefs[c.get("kind")]
        return f"You usually deliver {c.get('kind', '').replace('_', ' ')} parts as {LABEL[way]} ({p['count']} of {p['of']} of your changes)."
    if way == "youtube":
        s = ev["full"][0] if ev["full"] else ev["segments"][0]
        return f"{s['start']}–{s['end']} of \"{s['video'][:60]}\" teaches all of it ({s['minutes']} min, checked on the transcript)."
    if way == "youtube_bridge":
        miss = "; ".join(ev["missing"][:3])
        return (f"{_fmt_segs(ev['segments'])} teach {round(100 * ev['video_minutes'] / mins)}% of it; "
                f"1–3 slides add {miss or 'the rest'}.")
    if way == "notebooklm":
        cov = "" if ev["coverage"] is None else f"; the notebook's sources cover {round(100 * ev['coverage'])}% of its key terms"
        return f"No video teaches it fully{cov}, so a NotebookLM explainer can."
    if way == "slides":
        why = []
        if ev["segments"]:
            why.append(f"videos teach only {round(100 * ev['video_minutes'] / mins)}% of it")
        else:
            why.append("no checked video teaches it")
        if ev["coverage"] is not None and ev["coverage"] < mcfg()["rules"]["notebooklm_min_coverage"]:
            why.append(f"the sources lack {', '.join(ev['uncovered'][:3])}")
        elif (g["survey"].get("confidence") or 0) > mcfg()["rules"]["notebooklm_max_confidence"]:
            why.append(f"you know this topic (confidence {g['survey'].get('confidence')})")
        return "Taught live: " + "; ".join(why) + "."
    if way == "in_class":
        return "Done in class with a task on the slide."
    return LABEL.get(way, way)


def _part(c: dict, minutes: int, way: str, rule: str, ev: dict, reason: str, alt: tuple[str, str] | None) -> dict:
    p = {"component": c["id"], "title": c["title"], "minutes": minutes, "kind": c.get("kind") or "concept",
         "bloom": c.get("bloom") or 2, "way": way, "when": "in_class", "rule": rule, "reason": reason,
         "allowed": ev["allowed"], "coverage": ev["coverage"], "uncovered": ev["uncovered"]}
    if alt:
        p["alternative"] = {"way": alt[0], "reason": alt[1]}
    _attach(p, ev)
    return p


def _attach(p: dict, ev: dict) -> None:
    """Fill the way-specific evidence of a part (segments, bridge points, simulation)."""
    way = p["way"]
    p["segments"], p["video_minutes"], p["bridge"], p["simulation"] = [], 0.0, [], None
    if way in ("youtube", "youtube_bridge"):
        segs = ev["full"][:1] if (way == "youtube" and ev["full"]) else ev["segments"]
        p["segments"] = [{k: s[k] for k in ("video", "video_id", "url", "start", "end", "minutes", "verdict")} for s in segs]
        p["video_minutes"] = round(sum(s["minutes"] for s in segs), 1)
        if way == "youtube_bridge":
            p["bridge"] = ev["missing"]
    if ev["simulation"]:                     # the best matching simulation, shown as evidence whatever the way
        s = ev["simulation"]
        sid = s.get("id")
        p["simulation"] = {"id": sid if sid and not sid.startswith("ext:") else None, "url": s.get("url"), "title": s["title"],
                           "source": s.get("source", ""), "score": s.get("score", 0.0), "class_example": s.get("class_example")}


# ------------------------------------------------------------------ preferences learnt from the professor's changes
def changes_path(run_id: str) -> Path:
    return out_dir(run_id) / "app_mix_changes.jsonl"


def preferences(run_id: str) -> dict:
    """kind -> {way, count, of}: once the professor has made enough changes, the way they choose most for a kind."""
    p = mcfg()["preferences"]
    path = changes_path(run_id)
    if not path.exists():
        return {}
    rows = [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
    rows = [x for x in rows if x.get("to") and x.get("to") != x.get("from")]
    if len(rows) < p["min_changes"]:
        return {}
    out = {}
    for kind in {x.get("kind") for x in rows}:
        mine = [x["to"] for x in rows if x.get("kind") == kind]
        best = max(set(mine), key=mine.count)
        if mine.count(best) >= p["min_count"] and mine.count(best) / len(mine) >= p["min_share"]:
            out[kind] = {"way": best, "count": mine.count(best), "of": len(mine)}
    return out


# ------------------------------------------------------------------ the lecture as a whole
def _protected(p: dict) -> bool:
    return p.get("locked") or p.get("set_by") == "professor" or p.get("rule") == "D7-note"


def _switches(parts: list[dict]) -> int:
    return sum(1 for a, b in zip(parts, parts[1:]) if a["way"] != b["way"])


def lecture_checks(parts: list[dict], evs: dict, preset_ways: list[str], flipped: bool, minutes: int, act: bool = True) -> list[dict]:
    """Apply (act=True) or only report the lecture-wide rules. Never changes a protected part."""
    L = mcfg()["lecture"]
    notes = []

    def change(p, way, why):
        p["way"], p["rule"], p["reason"] = way, "L", why
        _attach(p, evs[p["component"]])

    if flipped:
        for p in parts:
            if p["way"] in VIDEO_WAYS and p["when"] != "pre_class" and not _protected(p):
                p["when"] = "pre_class"
    first = parts[0] if parts else None
    if L["first_part_live"] and first and not flipped and first["way"] in ("youtube", "notebooklm"):
        if act and not _protected(first):
            old = first["way"]
            change(first, "slides", f"The first part is taught live to frame the lecture; {LABEL[old]} stays the alternative.")
            first["alternative"] = {"way": old, "reason": "first part taught live"}
            notes.append({"code": "L-FIRST", "message": f"{first['component']}: taught live (was {LABEL[old]})"})
        else:
            notes.append({"code": "L-FIRST", "message": f"{first['component']} opens the lecture with {LABEL[first['way']]}; the proposal teaches the first part live"})
    nlm = [p for p in parts if p["way"] == "notebooklm"]
    if len(nlm) > L["notebooklm_max"]:
        extra = sorted([p for p in nlm if not _protected(p)], key=lambda p: (p.get("coverage") or 0, p["minutes"]))
        over = len(nlm) - L["notebooklm_max"]
        for p in (extra[:over] if act else []):
            change(p, "slides", f"Taught live: at most {L['notebooklm_max']} NotebookLM videos per lecture, and this part's sources are the weakest.")
            p["alternative"] = {"way": "notebooklm", "reason": "over the NotebookLM limit"}
        left = len([p for p in parts if p["way"] == "notebooklm"])
        if left > L["notebooklm_max"] or not act:
            notes.append({"code": "L-NLM", "message": f"{left} NotebookLM videos to make (about {mcfg()['prep_minutes']['notebooklm']} min each)"})
    if act:
        for _ in range(len(parts)):
            if _switches(parts) <= L["max_switches"]:
                break
            best = None
            for i, p in enumerate(parts):
                if _protected(p):
                    continue
                nb = [parts[j]["way"] for j in (i - 1, i + 1) if 0 <= j < len(parts)]
                if (len(set(nb)) == 1 and nb[0] != p["way"] and nb[0] not in ("in_class", "simulation")
                        and nb[0] in evs[p["component"]]["allowed"] and nb[0] in preset_ways):
                    if best is None or p["minutes"] < best[0]["minutes"]:
                        best = (p, nb[0])
            if not best:
                break
            change(best[0], best[1], f"Kept with its neighbouring parts ({LABEL[best[1]]}) so the lecture does not switch ways too often.")
    if _switches(parts) > L["max_switches"]:
        notes.append({"code": "L-SWITCH", "message": f"the lecture switches way {_switches(parts)} times (aim for at most {L['max_switches']})"})
    for p in parts:
        long = max((s["minutes"] for s in p.get("segments") or []), default=0)
        if p["way"] in ("youtube", "youtube_bridge") and p["when"] == "in_class" and long > L["clip_in_class_max_min"]:
            if act and not _protected(p):
                p["when"] = "pre_class"
                notes.append({"code": "L-LONG", "message": f"{p['component']}: a {long}-min clip is watched before class"})
            else:
                notes.append({"code": "L-LONG", "message": f"{p['component']}: a {long}-min clip in class (over {L['clip_in_class_max_min']} min)"})

    def share():
        return sum(_video_min(p) for p in parts if p["when"] == "in_class") / max(minutes, 1)
    while share() > L["video_share_max"]:
        movable = [p for p in parts if p["way"] in VIDEO_WAYS and p["when"] == "in_class" and not _protected(p)]
        if not act or not movable:
            notes.append({"code": "L-VIDEO", "message": f"video takes {round(100 * share())}% of class time (aim for at most {round(100 * L['video_share_max'])}%)"})
            break
        p = max(movable, key=_video_min)
        p["when"] = "pre_class"
        notes.append({"code": "L-VIDEO", "message": f"{p['component']}: watched before class to keep video under {round(100 * L['video_share_max'])}% of class time"})
    for p in parts:
        if p["way"] == "notebooklm" and p.get("coverage") is not None and p["coverage"] < mcfg()["rules"]["notebooklm_min_coverage"]:
            notes.append({"code": "L-SOURCES", "message": f"{p['component']}: add a source that explains {', '.join(p.get('uncovered', [])[:4])} before making its NotebookLM video"})
    return notes


def _video_min(p: dict) -> float:
    if p["way"] in ("youtube", "youtube_bridge"):
        return min(p.get("video_minutes") or p["minutes"], p["minutes"])
    if p["way"] == "notebooklm":
        return min(p["minutes"], 10)
    return 0.0


def totals(parts: list[dict], recap: int, quiz: int) -> tuple[dict, int]:
    """Minutes of the lecture by way (a video watched before class leaves its class minutes to a live debrief) and the
    professor's preparation time; each part gets its own prep_minutes."""
    t = {k: 0.0 for k in ("slides", "video_in_class", "video_pre_class", "notebooklm", "in_class", "simulation")}
    pm = mcfg()["prep_minutes"]
    prep = 0.0
    for p in parts:
        w, m = p["way"], p["minutes"]
        if w in VIDEO_WAYS:
            v = _video_min(p)
            if w == "notebooklm":
                t["notebooklm"] += v
            if p["when"] == "pre_class":
                t["video_pre_class"] += v
                t["slides"] += m
            else:
                t["video_in_class"] += v
                t["slides"] += m - v
        elif w in ("in_class", "simulation"):
            t[w] += m
        else:
            t["slides"] += m
        base = {"slides": pm["slides"] * m, "youtube": pm["youtube"] + (p.get("video_minutes") or 0),
                "youtube_bridge": pm["youtube_bridge"] + (p.get("video_minutes") or 0), "notebooklm": pm["notebooklm"],
                "in_class": pm["in_class"], "simulation": pm["simulation"]}[w]
        p["prep_minutes"] = int(round(base))
        prep += base
    t = {k: round(v, 1) for k, v in t.items()}
    t["recap"], t["quiz"] = recap, quiz
    t["video_share"] = round(t["video_in_class"] / max(sum(p["minutes"] for p in parts) + recap + quiz, 1), 2)
    return t, int(round(prep))


def _trim(parts: list[dict], need: int) -> int:
    """Old plans (before D5 kept minutes free): take `need` minutes from the longest parts, in steps, keeping each part
    at least the minimum. Returns the minutes taken."""
    c = rcfg()["components"]
    step, lo = c["round_to"], c["min_minutes"]
    taken = 0
    while taken < need:
        cand = [p for p in parts if p["minutes"] - step >= lo]
        if not cand:
            break
        order = {"slides": 0, "notebooklm": 1, "simulation": 2, "in_class": 3}      # video parts last: their clips are fixed
        p = min(cand, key=lambda x: (order.get(x["way"], 4), -x["minutes"]))
        p["minutes"] -= step
        taken += step
    return taken


def pick_preset(style: str, cands: dict) -> str:
    fixed = mcfg()["course_styles"].get(style)
    if fixed:
        return fixed
    ways = {w for cs in cands.values() for w, rule in cs if rule != "alt"}
    has_v, has_n = bool(ways & {"youtube", "youtube_bridge"}), "notebooklm" in ways
    if has_v and has_n:
        return "full_mix"
    if has_v or "simulation" in ways:
        return "slides_clips"
    if has_n:
        return "slides_notebooklm"
    return "slides_only"


# ------------------------------------------------------------------ D7: reasons (and swaps within the rules)
def ai_reasons(run_id: str, m: dict, evs: dict, g: dict, log) -> int:
    """D7 writes the reason for each part and may change a way for a reason the program accepts. Returns the number of
    parts it changed; on any failure the rule reasons stay."""
    from profsagent.delivery.resources import llm_call
    from profsagent.llm.client import LLMClient
    st = load_state(run_id)
    cc = st["cco_compact"]
    preset_ways = mcfg()["presets"][m["preset"]]
    parts = []
    for p in m["parts"]:
        ev = evs[p["component"]]
        e = []
        if ev["segments"]:
            e.append(f"stretches {_fmt_segs(ev['segments'])}: {ev['video_minutes']} of {p['minutes']} min, "
                     f"{'teaches fully' if ev['full'] else 'teaches partly'}" + (f"; missing: {'; '.join(ev['missing'][:3])}" if ev["missing"] else ""))
        else:
            e.append("no checked video stretch")
        if ev["coverage"] is not None:
            e.append(f"NotebookLM sources cover {round(100 * ev['coverage'])}% of key terms" + (f" (lack: {', '.join(ev['uncovered'][:3])})" if ev["uncovered"] else ""))
        if ev["simulation"]:
            e.append(f"simulation \"{ev['simulation']['title']}\" ({ev['simulation']['source']}, match {ev['simulation']['score']:.2f})")
        c = next(x for x in g["lecture"]["components"] if x["id"] == p["component"])
        parts.append({"id": p["component"], "title": p["title"], "teaches": c.get("teaches", "")[:400], "kind": p["kind"],
                      "bloom": p["bloom"], "minutes": p["minutes"], "way": p["way"], "rule": p["rule"],
                      "allowed": [w for w in ev["allowed"] if w in preset_ways], "locked": _protected(p), "evidence": "; ".join(e)})
    ctx = {"course": {"course_name": cc["course_name"], "level": st.get("level"), "years": (cc.get("target_students") or {}).get("years")},
           "lecture": {"lecture_id": m["lecture_id"], "topic": m["topic"], "minutes": m["minutes"], "preset": m["preset"],
                       "novel": bool(g["brief"].get("novel")), "professor_confidence": g["survey"].get("confidence")},
           "note": m.get("note") or "", "parts": parts}
    try:
        llm = LLMClient(out_dir(run_id) / "llm_calls.jsonl")
        got = llm_call(llm, "D7", ctx, MixChoices, run_id, log)
    except Exception as e:  # noqa: BLE001 — no model left: the rule reasons stay
        log(f"  [D7] failed ({type(e).__name__}); rule reasons kept")
        return 0
    by = {x.id: x for x in got.parts}
    changed = 0
    for p, x in zip(m["parts"], parts):
        ch = by.get(p["component"])
        if not ch:
            continue
        if ch.reason.strip():
            p["reason"] = ch.reason.strip()[:240]
        if ch.way == p["way"] or x["locked"]:
            continue
        ok = ch.way in x["allowed"] and ch.because in ("note", "fit", "balance") and (ch.because != "note" or m.get("note"))
        if not ok:
            log(f"  [D7] change of {p['component']} to {ch.way} ({ch.because}) refused: not allowed by the rules")
            continue
        old = p["way"]
        p["way"], p["rule"] = ch.way, ("D7-note" if ch.because == "note" else "D7")
        p["alternative"] = {"way": old, "reason": f"the rules chose {LABEL[old]}"}
        _attach(p, evs[p["component"]])
        changed += 1
    return changed


# ------------------------------------------------------------------ propose / save / approve
def _locked_rows(old: dict | None, locked) -> dict[str, dict]:
    keep = {}
    if old:
        for p in old["parts"]:
            if p.get("locked"):
                keep[p["component"]] = p
    if isinstance(locked, dict):
        for cid, v in locked.items():
            base = keep.get(cid) or next((p for p in (old or {}).get("parts", []) if p["component"] == cid), None) or {}
            way = v if isinstance(v, str) else (v or {}).get("way") or base.get("way")
            if way:
                keep[cid] = {**base, "component": cid, "way": way, "locked": True,
                             **({"when": v["when"]} if isinstance(v, dict) and v.get("when") else {})}
    elif locked:
        for cid in locked:
            base = next((p for p in (old or {}).get("parts", []) if p["component"] == cid), None)
            if base:
                keep[cid] = {**base, "locked": True}
    return keep


def propose(run_id: str, lecture_id: str, locked=None, note: str = "", sims: dict | None = None, use_ai: bool | None = None,
            preset: str | None = None, log=None, keep_approved: bool = False) -> dict:
    """Propose the mix for one lecture and write delivery/mix/<lecture>.json (status "proposed").

    locked: component ids whose current way stays, or {component id: way | {way, when}}; rows locked in the file stay too.
    note:   the professor's note, read by D7 ("I'll teach MCP schemas myself; keep videos short").
    sims:   {component id: [{id | url, title, source, score, class_example?}]} from the app (Amit's match_parts);
            None = the local matcher in this module.
    keep_approved: an approved mix whose parts are unchanged is returned as it is (used by recommend)."""
    log = log or (lambda *_: None)
    old = load(run_id, lecture_id)
    g = gather(run_id, lecture_id, sims)
    comps = g["lecture"]["components"]
    if keep_approved and old and old.get("status") == "approved" and [p["component"] for p in old["parts"]] == [c["id"] for c in comps]:
        return old
    b = g["brief"]
    total = int(g["plan_lecture"].get("lecture_minutes") or round((b.get("hours") or 0) * 60) or sum(c["minutes"] for c in comps))
    res = g["plan_lecture"].get("reserved")
    recap, quiz = (res["recap"], res["quiz"]) if res else reserve_for(total, lecture_id == _first_lecture(run_id))
    style = course_style(run_id)
    prefs = preferences(run_id)
    evs = {c["id"]: evidence(c, g, c["minutes"]) for c in comps}
    cands = {c["id"]: candidates(c, evs[c["id"]], g, prefs) for c in comps}
    preset_by = "professor" if preset else "ai"
    if not preset and old and old.get("preset_by") == "professor" and old.get("preset") in mcfg()["presets"]:
        preset, preset_by = old["preset"], "professor"
    preset = preset or pick_preset(style, cands)
    ways = mcfg()["presets"][preset]
    keep = _locked_rows(old, locked)
    parts = []
    for c in comps:
        ev = evs[c["id"]]
        if c["id"] in keep:
            k = keep[c["id"]]
            p = _part(c, c["minutes"], k["way"], k.get("rule") or "professor", ev, k.get("reason") or f"Kept as {LABEL[k['way']]} (locked).", None)
            p.update(locked=True, set_by=k.get("set_by") or "professor", when=k.get("when") or "in_class")
            parts.append(p)
            continue
        cs = [x for x in cands[c["id"]] if x[0] in ways or x[0] in ("slides", "in_class")]
        way, rule = cs[0]
        if rule == "alt":
            way, rule = "slides", "R5"
        alt = next(((w, rule_reason(w, r, c, ev, g, prefs)) for w, r in cs[1:] if w != way), None)
        parts.append(_part(c, c["minutes"], way, rule, ev, rule_reason(way, rule, c, ev, g, prefs), alt))
    checks = []
    taken = 0
    if not g["plan_lecture"].get("reserved") and recap + quiz:
        taken = _trim(parts, recap + quiz)
        if taken < recap + quiz:
            quiz = max(0, quiz - (recap + quiz - taken))
        checks.append({"code": "L-RESERVE", "message": f"the part plan was made before recap and quiz minutes were kept free; {taken} min were taken from the longest parts"})
    flipped = preset == "flipped"
    m = {"lecture_id": lecture_id, "topic": g["lecture"].get("topic") or b.get("topic", ""), "minutes": total,
         "status": "proposed", "preset": preset, "preset_by": preset_by, "course_style": style, "parts": parts, "recap_minutes": recap,
         "quiz_minutes": quiz, "note": note or "", "proposed_at": now(), "proposed_by": "rules"}
    checks += lecture_checks(parts, evs, ways, flipped, total)
    if use_ai if use_ai is not None else mcfg()["ai_reasons"]:
        n = ai_reasons(run_id, m, evs, g, log)
        m["proposed_by"] = "rules + D7"
        if n:
            again = lecture_checks(parts, evs, ways, flipped, total)
            checks = [x for x in checks if x["code"] in ("L-RESERVE", "L-FIRST")] + [x for x in again if x not in checks]
            checks.append({"code": "L-AI", "message": f"the AI changed {n} part(s) within the rules (see each reason)"})
    elif note:
        checks.append({"code": "L-NOTE", "message": "AI reasons are off, so the note was saved but not applied"})
    m["checks"] = checks
    m["totals"], m["prep_minutes"] = totals(parts, recap, quiz)
    m = _save(run_id, m)
    write_pack(run_id, lecture_id, m)
    log(f"  mix {lecture_id}: {preset} · " + ", ".join(f"{w} {sum(1 for p in parts if p['way'] == w)}" for w in mcfg()["ways"] if any(p["way"] == w for p in parts))
        + f" · video in class {round(100 * m['totals']['video_share'])}%")
    return m


def save(run_id: str, lecture_id: str, changes: dict | None = None, preset: str | None = None, approve: bool = False,
         by: str = "Professor", log=None) -> dict:
    """The professor's decisions: changes = {component id: {"way"?, "locked"?, "when"?, "reason"?}}. Each change of way is
    logged (with the part's signals) for the per-professor rules. Returns {"mix"} or {"errors": {component id: message}}.
    A new preset proposes again (locked and professor rows kept); approve=True approves and makes the materials."""
    m = load(run_id, lecture_id)
    if not m:
        return {"errors": {"_": "No proposal yet for this lecture."}}
    if preset and preset != m["preset"]:
        if preset not in mcfg()["presets"]:
            return {"errors": {"preset": f"Unknown preset {preset}."}}
        keep = {p["component"]: {"way": p["way"], "when": p["when"]} for p in m["parts"] if p.get("locked") or p.get("set_by") == "professor"}
        m = propose(run_id, lecture_id, locked=keep, note=m.get("note", ""), preset=preset, log=log)
    g = None
    errors = {}
    parts = {p["component"]: p for p in m["parts"]}
    for cid, ch in (changes or {}).items():
        p = parts.get(cid)
        if not p:
            errors[cid] = "Not a part of this lecture."
            continue
        if "way" in ch and ch["way"] != p["way"]:
            g = g or gather(run_id, lecture_id, sims={x["component"]: [x["simulation"]] for x in m["parts"] if x.get("simulation")})
            c = next(x for x in g["lecture"]["components"] if x["id"] == cid)
            ev = evidence(c, g, p["minutes"])
            if ch["way"] not in possible_ways(ev):
                errors[cid] = f"{LABEL.get(ch['way'], ch['way'])} is not possible here: " + (
                    "no checked video stretch for this part." if ch["way"] in ("youtube", "youtube_bridge") else "no matching simulation.")
                continue
            _log_change(run_id, lecture_id, p, ch["way"], by)
            old = p["way"]
            p.update(way=ch["way"], rule="professor", set_by="professor", reason=ch.get("reason") or f"Chosen by {by} (was {LABEL[old]}).")
            p["alternative"] = {"way": old, "reason": "the earlier proposal"}
            _attach(p, ev)
            p["allowed"] = ev["allowed"]
        if "locked" in ch:
            p["locked"] = bool(ch["locked"])
        if ch.get("when") in ("in_class", "pre_class"):
            p["when"] = ch["when"]
            p["set_by"] = "professor"
    if errors:
        return {"errors": errors}
    evs = {}
    if g is None:
        g = gather(run_id, lecture_id, sims={x["component"]: [x["simulation"]] for x in m["parts"] if x.get("simulation")})
    for c in g["lecture"]["components"]:
        if c["id"] in parts:
            evs[c["id"]] = evidence(c, g, parts[c["id"]]["minutes"])
    m["checks"] = [x for x in m.get("checks", []) if x["code"] in ("L-RESERVE", "L-AI", "L-NOTE")] + \
        lecture_checks(m["parts"], evs, mcfg()["presets"][m["preset"]], m["preset"] == "flipped", m["minutes"], act=False)
    m["totals"], m["prep_minutes"] = totals(m["parts"], m["recap_minutes"], m["quiz_minutes"])
    if approve:
        m.update(status="approved", approved_at=now(), approved_by=by)
    elif changes:
        m["status"] = "proposed"
    m = _save(run_id, m)
    if approve:
        m["materials"] = materials(run_id, lecture_id, log=log)
        m = _save(run_id, m)
    return {"mix": m}


def approve(run_id: str, lecture_id: str, by: str = "Professor", log=None) -> dict:
    return save(run_id, lecture_id, approve=True, by=by, log=log)


def _log_change(run_id: str, lecture_id: str, p: dict, to: str, by: str) -> None:
    row = {"at": now(), "lecture": lecture_id, "component": p["component"], "kind": p["kind"], "bloom": p["bloom"],
           "from": p["way"], "to": to, "rule": p.get("rule"), "by": by,
           "signals": {"video_minutes": p.get("video_minutes"), "coverage": p.get("coverage"), "minutes": p["minutes"],
                       "allowed": p.get("allowed")}}
    path = changes_path(run_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


# ------------------------------------------------------------------ materials: NotebookLM pack and quiz
def write_pack(run_id: str, lecture_id: str, m: dict) -> dict | None:
    """The NotebookLM pack for the mix's NotebookLM parts (and the flashcards); the lecture file's summary is updated."""
    from profsagent.delivery.notebooklm import pack
    d = out_dir(run_id)
    lp = d / "lectures" / f"{lecture_id}.json"
    lec = read_json(lp) or {}
    res = lec.get("resources")
    if not res:
        return None
    briefs = {b["lecture_id"]: b for b in read_json(d / "briefs.json", []) or []}
    plans = read_json(d / "components.json", {}) or {}
    comps = lec["components"]
    tid = briefs[lecture_id]["topic_id"]
    earlier = [c for c in (plans.get(tid) or {}).get("components", []) if c["lecture_id"] < lecture_id]
    srcs = {k: (res.get("items") or {}).get(k, []) for k in ("video", "reading", "practice")}
    md, summary = pack(load_state(run_id), briefs[lecture_id], comps, earlier, res.get("timeline") or [], srcs, mix=m)
    (d / "notebooklm").mkdir(exist_ok=True)
    (d / "notebooklm" / f"{lecture_id}.md").write_text(md, encoding="utf-8")
    res["notebooklm"] = summary
    write_json(lp, lec)
    return summary


def _quiz_problems(qs: list, ids: set[str], want: int) -> list[str]:
    out = []
    if len(qs) < want:
        out.append(f"{len(qs)} questions, {want} wanted")
    short = sum(1 for q in qs if not q.options)
    if short * 4 > max(len(qs), 1):
        out.append(f"{short} short-answer questions (at most one in four)")
    return out


def make_quiz(run_id: str, lecture_id: str, m: dict, log) -> dict:
    """D8: the closing quiz, one question per part (4–8); every question checked by the program."""
    from profsagent.delivery.resources import llm_call
    from profsagent.llm.client import LLMClient
    d = out_dir(run_id)
    lec = read_json(d / "lectures" / f"{lecture_id}.json") or {}
    comps = {c["id"]: c for c in lec.get("components") or []}
    clips = {}
    for k in (lec.get("resources") or {}).get("clips") or []:
        clips.setdefault(k["component"], []).extend(k.get("covered") or [])
    lo_n, hi_n = mcfg()["reserve"]["quiz_questions"]
    want = max(lo_n, min(hi_n, len(m["parts"])))
    st = load_state(run_id)
    cc = st["cco_compact"]
    b = {x["lecture_id"]: x for x in read_json(d / "briefs.json", []) or []}.get(lecture_id) or {}
    parts = [{"id": p["component"], "title": p["title"], "teaches": comps[p["component"]].get("teaches", ""),
              "key_terms": comps[p["component"]].get("key_terms", []), "bloom": p["bloom"],
              "lo_ids": comps[p["component"]].get("lo_ids", []), "way": p["way"],
              "taught_by_video": clips.get(p["component"], []) if p["way"] in ("youtube", "youtube_bridge") else [],
              "left_to_slides": p.get("bridge", [])} for p in m["parts"]]
    ctx = {"course": {"course_name": cc["course_name"], "level": st.get("level"), "years": (cc.get("target_students") or {}).get("years")},
           "lecture": {"lecture_id": lecture_id, "topic": m["topic"],
                       "learning_outcomes": [{"id": x["id"], "statement": x["statement"]} for x in b.get("learning_outcomes", [])]},
           "parts": parts, "n_questions": want}
    try:
        got = llm_call(LLMClient(d / "llm_calls.jsonl"), "D8", ctx, Quiz, run_id, log)
    except Exception as e:  # noqa: BLE001
        log(f"  [D8] failed ({type(e).__name__}); no quiz this time")
        return {"questions": [], "problems": [f"quiz not made ({type(e).__name__})"]}
    ok, dropped = [], []
    for q in got.questions:
        if q.component not in comps:
            dropped.append(f"unknown part {q.component}")
            continue
        if q.options and (len(q.options) != 4 or len(set(o.strip().lower() for o in q.options)) != 4 or q.answer.strip().upper() not in "ABCD" or len(q.answer.strip()) != 1):
            dropped.append(f"malformed multiple choice for {q.component}")
            continue
        q.lo_ids = [i for i in q.lo_ids if i in set(comps[q.component].get("lo_ids") or [])] or comps[q.component].get("lo_ids", [])
        if q.options:
            q.answer = q.answer.strip().upper()
            shuffle(q, f"{lecture_id}|{q.question}")
        ok.append(q)
    ok = ok[:hi_n]
    problems = dropped + _quiz_problems(ok, set(comps), want)
    missing = [p["component"] for p in m["parts"] if not any(q.component == p["component"] for q in ok)]
    if missing and len(m["parts"]) <= want:
        problems.append(f"no question on {', '.join(missing)}")
    return {"questions": [q.model_dump() for q in ok], "problems": problems}


def shuffle(q, seed: str) -> None:
    """Models put the right answer at B far too often (59% on CS-601): reorder the options with a fixed seed per question
    (the same quiz every time) and move the answer letter with them."""
    import hashlib
    import random
    right = q.options["ABCD".index(q.answer)]
    rng = random.Random(int(hashlib.sha256(seed.encode("utf-8")).hexdigest()[:12], 16))
    opts = list(q.options)
    rng.shuffle(opts)
    q.options, q.answer = opts, "ABCD"[opts.index(right)]


def recap_from(run_id: str, lecture_id: str) -> list[dict]:
    """Questions for the opening recap: from the previous lecture's quiz, one per part, at most `recap_questions`."""
    d = out_dir(run_id)
    ids = sorted(b["lecture_id"] for b in read_json(d / "briefs.json", []) or [])
    if lecture_id not in ids or ids.index(lecture_id) == 0:
        return []
    prev = read_json(d / "quiz" / f"{ids[ids.index(lecture_id) - 1]}.json") or {}
    out, seen = [], set()
    for q in prev.get("questions", []):
        if q["component"] not in seen:
            seen.add(q["component"])
            out.append(q)
    return out[:mcfg()["reserve"]["recap_questions"]]


def quiz_markdown(q: dict) -> str:
    L = [f"# Review quiz · {q['lecture_id']} · {q['topic']}", ""]
    if q.get("recap"):
        L += [f"## Recap of the previous lecture ({q['minutes']['recap']} min)", ""]
        for i, x in enumerate(q["recap"], 1):
            L += _q_md(i, x)
    L += [f"## Review quiz ({q['minutes']['quiz']} min)", ""]
    for i, x in enumerate(q["questions"], 1):
        L += _q_md(i, x)
    L += ["## Answers", ""]
    for name, qs in (("Recap", q.get("recap") or []), ("Quiz", q["questions"])):
        for i, x in enumerate(qs, 1):
            L.append(f"- {name} {i}: **{x['answer']}**: {x.get('explanation', '')} ({x['component']})")
    return "\n".join(L) + "\n"


def _q_md(i: int, x: dict) -> list[str]:
    L = [f"{i}. {x['question']}"]
    L += [f"   - {chr(65 + k)}. {o}" for k, o in enumerate(x.get("options") or [])]
    return L + [""]


def materials(run_id: str, lecture_id: str, log=None) -> dict:
    """After approval: the NotebookLM pack (only the approved NotebookLM parts) and the quiz with the recap."""
    log = log or (lambda *_: None)
    m = load(run_id, lecture_id)
    if not m or m.get("status") != "approved":
        raise ValueError(f"{lecture_id}: approve the mix first")
    d = out_dir(run_id)
    nl = write_pack(run_id, lecture_id, m)
    out = {"notebooklm": (nl or {}).get("pack")}
    if mcfg()["ai_quiz"]:
        qz = make_quiz(run_id, lecture_id, m, log)
        q = {"lecture_id": lecture_id, "topic": m["topic"], "made_at": now(),
             "minutes": {"recap": m["recap_minutes"], "quiz": m["quiz_minutes"]},
             "recap": recap_from(run_id, lecture_id) if m["recap_minutes"] else [], **qz}
        (d / "quiz").mkdir(exist_ok=True)
        write_json(d / "quiz" / f"{lecture_id}.json", q)
        (d / "quiz" / f"{lecture_id}.md").write_text(quiz_markdown(q), encoding="utf-8")
        out["quiz"] = f"quiz/{lecture_id}.json"
        out["quiz_questions"] = len(q["questions"])
        if qz.get("problems"):
            out["quiz_problems"] = qz["problems"]
    return out


def outline_rows(run_id: str, lecture_id: str) -> dict:
    """For B (content/generate.outline): component id -> {way, when, bridge, simulation} of an approved mix; {} otherwise."""
    m = load(run_id, lecture_id)
    if not m or m.get("status") != "approved":
        return {}
    return {p["component"]: {"way": p["way"], "when": p["when"], "bridge": p.get("bridge") or [], "simulation": p.get("simulation"),
                             "minutes": p["minutes"]} for p in m["parts"]}


def run_for(run_id: str, lectures: list[str] | None = None, approve_all: bool = False, note: str = "", use_ai: bool | None = None,
            log=None) -> list[dict]:
    """CLI: propose (and with approve_all, approve and make the materials) for the lectures that have results."""
    log = log or print
    d = out_dir(run_id)
    ids = sorted(p.stem for p in (d / "lectures").glob("*.json"))
    out = []
    for lid in ids:
        if lectures and lid not in lectures:
            continue
        lec = read_json(d / "lectures" / f"{lid}.json") or {}
        if not lec.get("components") or not lec.get("resources"):
            continue
        t = time.time()
        m = propose(run_id, lid, note=note, use_ai=use_ai, log=log)
        if approve_all:
            m = save(run_id, lid, approve=True, by="CLI", log=log)["mix"]
        log(f"  {lid}: {m['status']} in {time.time() - t:.0f}s")
        out.append(m)
    return out
