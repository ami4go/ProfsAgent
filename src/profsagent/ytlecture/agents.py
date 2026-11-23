"""The AI sub-agents. Each one: build its context → render its prompt → schema-validated JSON (LLMClient.structured, which
walks Gemini 3.8/3.6 flash then the other free providers) → deterministic checks. Nothing an agent says is used before
code has checked it (ids exist, times are inside the video, quotes are in the words, minutes add up).

  Y1 planner     parts of each lecture, with minutes and must-cover checkpoints        role generate
  Y2 scout       who teaches this (authorities), course pages, two queries per part    role generate
  Y3 triage      which candidate videos are worth reading (metadata only)              role extract   (fallback)
  Y3N nominator   names the strong-source videos worth grading (titles only)            role grade
  Y3G grader     grades ~15 video cards 0-3 for ONE part (shortlist.py chooses)       role grade
  Y4 skim        regions of a long video worth reading in full                         role read
  Y5 zoom        exact clips with quotes, coverage, level, rating                      role read
  Y6 verifier    second reader, always a different model from Y5's                     role verify
  Y7 gaps        new searches for parts still empty, or accept the gap                 role generate
"""
from __future__ import annotations

import json

from profsagent.llm.prompts import load_prompt
from profsagent.ytlecture import evidence as E
from profsagent.ytlecture import models as Mx
from profsagent.ytlecture.tools import Trace, cfg


def _temp(meta: dict) -> float:
    t = meta.get("temperature")
    return 0.2 if t in (None, "") else float(t)


def ask(llm, pid: str, ctx: dict, model_cls, trace: Trace, scope: str, run_id: str, exclude: frozenset[str] = frozenset()):
    """One sub-agent call. Returns (object, endpoint 'provider:model')."""
    p = load_prompt(pid)
    system, user = p.render(**ctx)
    obj, rec = llm.structured(system=system, user=user, model_cls=model_cls, role=p.meta.get("role", "generate"),
                              temperature=_temp(p.meta), prompt_id=pid, prompt_version=p.version, run_id=run_id,
                              exclude_models=exclude)
    ep = (rec.endpoint or "").replace("cache(", "").rstrip(")")
    model = ":".join(ep.split(":")[:2]) if ep else "?"
    trace.ai(pid, scope, rec.endpoint or "?", rec.prompt_tokens + rec.output_tokens,
             f"schema retries {rec.schema_retries}" if rec.schema_retries else "")
    return obj, model


# ---------------------------------------------------------------- Y1 planner
def plan_topic(llm, course: dict, topic: dict, lectures: list[dict], earlier: list[str], later: list[str],
               trace: Trace, run_id: str) -> dict:
    c = cfg()["lecture"]
    ctx = {"course": course, "topic": topic, "lectures": lectures, "earlier": earlier, "later": later,
           "parts_min": c["parts_min"], "parts_max": c["parts_max"], "fill_pct": round(100 * c["fill_target"]), "feedback": ""}
    scope = topic["id"]
    plan, problems = None, []
    for _ in range(2):
        plan, _m = ask(llm, "Y1", ctx, Mx.TopicPlan, trace, scope, run_id)
        problems = check_plan(plan, lectures)
        if not problems:
            break
        trace.step(scope, "planner output broke rules; asked again", problems=problems)
        ctx["feedback"] = "\n".join(f"- {p}" for p in problems)
    out = fix_plan(plan, lectures)
    if problems:
        trace.step(scope, "planner rules fixed by code (minutes rescaled, extra parts dropped)", problems=problems)
    return out


def check_plan(plan: Mx.TopicPlan, lectures: list[dict]) -> list[str]:
    c = cfg()["lecture"]
    errs = []
    got = [x.lecture_id for x in plan.lectures]
    want = [x["lecture_id"] for x in lectures]
    if got != want:
        errs.append(f"lectures must be exactly {want} in that order; got {got}")
    seen = set()
    for lp, lec in zip(plan.lectures, lectures):
        n = len(lp.parts)
        if not c["parts_min"] <= n <= c["parts_max"]:
            errs.append(f"{lp.lecture_id}: {n} parts; need {c['parts_min']}-{c['parts_max']}")
        tot, target = sum(p.minutes for p in lp.parts), lec["slot_minutes"] * c["fill_target"]
        if not 0.85 * target <= tot <= 1.1 * target:
            errs.append(f"{lp.lecture_id}: part minutes add up to {tot}; need about {round(target)}")
        for p in lp.parts:
            k = p.title.lower().strip()
            if k in seen:
                errs.append(f"part '{p.title}' appears twice")
            seen.add(k)
            if not 3 <= len(p.must_cover) <= 6:
                errs.append(f"part '{p.title}': {len(p.must_cover)} must_cover points; need 3-6")
    return errs


def fix_plan(plan: Mx.TopicPlan, lectures: list[dict]) -> dict:
    """Deterministic repair of what is left after the re-ask: unknown lectures dropped, parts capped, minutes rescaled."""
    c = cfg()["lecture"]
    by = {lp.lecture_id: lp for lp in plan.lectures}
    out = {"fast_moving": plan.fast_moving, "level_note": plan.level_note, "lectures": []}
    # The same part planned for two lectures (15 Nov, M2.T1: the model gave the whole topic's six parts to BOTH lectures):
    # keep one copy of every part in teaching order and split that list over the lectures by slot length.
    per_lec = [[p.model_dump() for p in (by[l["lecture_id"]].parts if l["lecture_id"] in by else [])] for l in lectures]
    titles = [p["title"].lower().strip() for ps in per_lec for p in ps]
    if len(lectures) > 1 and len(set(titles)) < len(titles):
        unique = list({p["title"].lower().strip(): p for ps in per_lec for p in ps}.values())
        per_lec = split_parts(unique, [l["slot_minutes"] for l in lectures])
    for lec, raw in zip(lectures, per_lec):
        parts = raw[: c["parts_max"]]
        for p in parts:
            p["must_cover"] = [m for m in p["must_cover"] if m.strip()][:6]
            p["search_phrases"] = [s for s in p["search_phrases"] if s.strip()][:3] or [p["title"]]
            p["minutes"] = max(3, int(p["minutes"]))
        tot, target = sum(p["minutes"] for p in parts), lec["slot_minutes"] * c["fill_target"]
        if parts and not 0.85 * target <= tot <= 1.1 * target:
            for p in parts:
                p["minutes"] = max(3, round(p["minutes"] * target / tot))
        out["lectures"].append({"lecture_id": lec["lecture_id"], "slot_minutes": lec["slot_minutes"], "parts": parts})
    return out


def split_parts(parts: list, slots: list[int]) -> list[list]:
    """Consecutive runs of `parts` (teaching order kept), each lecture getting a share proportional to its slot, at least 1."""
    n, total = len(parts), sum(slots) or 1
    counts = [max(1, round(n * s / total)) for s in slots]
    while sum(counts) > n:
        counts[counts.index(max(counts))] -= 1
    while sum(counts) < n:
        counts[counts.index(min(counts))] += 1
    out, i = [], 0
    for k in counts:
        out.append(parts[i:i + k])
        i += k
    return out


# ---------------------------------------------------------------- Y2 scout
def scout(llm, topic: dict, plan: dict, results: list[dict], trace: Trace, run_id: str) -> dict:
    slim = {"fast_moving": plan["fast_moving"], "lectures": [{"lecture_id": l["lecture_id"], "parts": [
        {"part": i, "title": p["title"], "search_phrases": p["search_phrases"]} for i, p in enumerate(l["parts"])]} for l in plan["lectures"]]}
    rep, _ = ask(llm, "Y2", {"topic": topic, "plan": slim, "results": results[:30]}, Mx.ScoutReport, trace, topic["id"], run_id)
    blob = json.dumps(results).lower()
    auths = []
    for a in rep.authorities[:10]:
        d = a.model_dump()
        d["evidence"] = "search" if a.name.lower() in blob else "knowledge"     # corrected by code, not trusted
        auths.append(d)
    urls = {r["url"] for r in results}
    pages = [u for u in rep.course_pages if u in urls][: cfg()["search"]["scout_pages_read"]]   # only URLs that were given
    pq: dict[str, dict[int, list[str]]] = {}
    nparts = {l["lecture_id"]: len(l["parts"]) for l in plan["lectures"]}
    for q in rep.part_queries:
        if q.lecture_id in nparts and 0 <= q.part < nparts[q.lecture_id]:
            pq.setdefault(q.lecture_id, {}).setdefault(q.part, []).extend(x.strip() for x in q.queries if x.strip())
    for lid, n in nparts.items():                                                   # a part the scout skipped
        for i in range(n):
            if not pq.get(lid, {}).get(i):
                part = next(l for l in plan["lectures"] if l["lecture_id"] == lid)["parts"][i]
                pq.setdefault(lid, {})[i] = [f"{part['search_phrases'][0]} explained"]
    return {"authorities": auths, "course_pages": pages, "part_queries": {lid: {str(k): v[:3] for k, v in d.items()} for lid, d in pq.items()}}


# ---------------------------------------------------------------- Y3 triage
def triage(llm, lecture: dict, parts: list[dict], cands: list[dict], fast: bool, trace: Trace, run_id: str,
           ranked: dict[int, list[str]] | None = None, roster: list[dict] | None = None) -> dict:
    t = dict(cfg()["triage"])
    # about one video per 10 minutes of slot (16 Nov, W02.L1: 10 reads for 7 parts of 15 min left most parts half filled)
    t["shortlist_per_lecture"] = max(t.get("shortlist_min", 6), min(t.get("shortlist_max", 14), round(lecture["slot_minutes"] / 10)))
    rows = [{"id": v["id"], "title": v["title"], "channel": v["channel"], "tier": v.get("tier", 4),
             "length": E.ts(v.get("duration_s") or 0), "year": (v.get("published") or "")[:4], "views": v.get("views"),
             "chapters": [c["title"] for c in E.chapters_of(v)][:25], "description": (v.get("description") or "")[:300]} for v in cands]
    more = [{"id": v["id"], "title": v["title"], "channel": v["channel"], "tier": v.get("tier", 4),
             "length": E.ts(v.get("duration_s") or 0), "year": (v.get("published") or "")[:4]} for v in (roster or [])]
    pts = [{"part": i, "title": p["title"], "teaches": p["teaches"], "minutes": p["minutes"]} for i, p in enumerate(parts)]
    res, _ = ask(llm, "Y3", {"lecture": lecture, "parts": pts, "candidates": rows, "authoritative": more,
                             "max_picks": t["shortlist_per_lecture"], "per_part": t["shortlist_per_part"], "fast_moving": fast},
                 Mx.Triage, trace, lecture["lecture_id"], run_id)
    ids = {v["id"] for v in cands} | {v["id"] for v in (roster or [])}
    picks, per_part = [], {}
    for p in sorted(res.picks, key=lambda x: -(x.fit * 2 + x.authority + 2 * x.likely_standalone + x.level_ok + 3 * x.anchor)):
        ps = [i for i in dict.fromkeys(p.parts) if 0 <= i < len(parts)]
        if p.video_id not in ids or not ps or any(x["video_id"] == p.video_id for x in picks):
            continue
        if not p.anchor and all(per_part.get(i, 0) >= t["shortlist_per_part"] for i in ps):
            continue                     # an anchor (one lecture serving several parts) is never refused for a full part
        for i in ps:
            per_part[i] = per_part.get(i, 0) + 1
        picks.append({**p.model_dump(), "parts": ps})
        if len(picks) >= t["shortlist_per_lecture"]:
            break
    # Top-up by code: models pick too few (first W01.L2 run: 5 of 10), so the reading budget is filled from the
    # embedding pre-rank (cands arrive in pre-rank order), parts with the fewest picks first; rejected ids are skipped.
    rejected = {r.video_id for r in res.rejects}
    tier = {v["id"]: v.get("tier", 4) for v in cands}
    ranked = ranked or {}
    while len(picks) < t["shortlist_per_lecture"]:
        open_parts = sorted((i for i in range(len(parts)) if per_part.get(i, 0) < t["shortlist_per_part"]),
                            key=lambda i: per_part.get(i, 0))
        added = False
        for i in open_parts:
            nxt = next((vid for vid in ranked.get(i, []) if vid not in rejected and vid in ids
                        and not any(x["video_id"] == vid for x in picks)), None)
            if nxt:
                per_part[i] = per_part.get(i, 0) + 1
                picks.append({"video_id": nxt, "parts": [i], "fit": 3, "authority": 5 - tier.get(nxt, 4), "level_ok": True,
                              "likely_standalone": True, "reason": "added by code: best embedding match for an under-covered part"})
                added = True
                break
        if not added:
            break
    # Last pass (17 Nov: the per-part ranked lists ran out at 7 of 8): any unrejected candidate in pre-rank order, for
    # the part its embedding ranks it highest on (else the least-covered part).
    for v in cands:
        if len(picks) >= t["shortlist_per_lecture"]:
            break
        vid = v["id"]
        if vid in rejected or vid not in ids or any(x["video_id"] == vid for x in picks):
            continue
        pos = {i: ranked[i].index(vid) for i in ranked if vid in ranked[i]}
        i = min(pos, key=pos.get) if pos else min(range(len(parts)), key=lambda j: per_part.get(j, 0))
        per_part[i] = per_part.get(i, 0) + 1
        picks.append({"video_id": vid, "parts": [i], "fit": 2, "authority": 5 - tier.get(vid, 4), "level_ok": True,
                      "likely_standalone": True, "reason": "added by code: next in the embedding pre-rank"})
    return {"picks": picks, "rejects": [r.model_dump() for r in res.rejects if r.video_id in ids]}


def grade_part(llm, lecture: dict, i: int, part: dict, parts: list[dict], cards: list[dict], fast: bool, level_note: str,
               trace: Trace, run_id: str, excerpts: bool = False):
    """Y3G: grade each card 0-3 for ONE part (17 Nov: one call choosing ~10 of ~130 videos for all parts at once was
    too hard for the small models it fell to, and its 5-8K-token prompt was too long for Groq)."""
    from profsagent.ytlecture import shortlist as SL
    others = [{"part": k, "title": p["title"]} for k, p in enumerate(parts) if k != i]
    pt = {"part": i, "title": part["title"], "teaches": part["teaches"], "must_cover": part.get("must_cover", [])[:6],
          "minutes": part["minutes"]}
    res, _ = ask(llm, "Y3G", {"lecture": {k: lecture[k] for k in ("lecture_id", "topic", "slot_minutes")}, "part": pt,
                              "other_parts": others, "cards": "\n".join(SL.card_text(c) for c in cards), "fast_moving": fast, "level_note": level_note,
                              "excerpts": excerpts},
                 Mx.Grades, trace, f"{lecture['lecture_id']}#{i}", run_id)
    return res


def nominate(llm, lecture: dict, parts: list[dict], rows: list[dict], fast: bool, trace: Trace, run_id: str):
    """Y3N: from ~80 strong-source titles, the few the AI KNOWS are excellent teaching material for this lecture. Their
    plain titles ("Lecture 7: Agentic Coding") rank 16th-200th by wording alone, so code cannot find them (17 Nov)."""
    pts = [{"part": i, "title": p["title"], "teaches": p["teaches"]} for i, p in enumerate(parts)]
    res, _ = ask(llm, "Y3N", {"lecture": {k: lecture[k] for k in ("lecture_id", "topic", "slot_minutes")}, "parts": pts,
                              "videos": "\n".join(f"{r['id']} | {r['title'][:80]} | {r['channel'][:30]} | {r['length']} | {r['year']}"
                                                   for r in rows), "max_picks": cfg().get("shortlist", {}).get("nominations", 8), "fast_moving": fast},
                 Mx.Nominations, trace, lecture["lecture_id"], run_id)
    return res


def part_def(k: dict, parts: list[dict], lecture: dict) -> dict:
    """The part a clip serves; for an EXTRA clip (part -1) a stand-in part built from its title and the lecture's outcomes."""
    if k["part"] >= 0:
        return parts[k["part"]]
    t = k.get("extra_title") or "additional material on the lecture topic"
    return {"title": t, "teaches": t, "minutes": 8, "kind": "concept",
            "must_cover": [t] + [lo for lo in (lecture.get("learning_outcomes") or [])][:2]}


# ---------------------------------------------------------------- Y4 skim + Y5 zoom
def _parts_ctx(parts: list[dict], only: list[int] | None = None) -> list[dict]:
    return [{"part": i, "title": p["title"], "teaches": p["teaches"], "must_cover": p["must_cover"], "minutes": p["minutes"]}
            for i, p in enumerate(parts) if only is None or i in only]


def _video_ctx(v: dict, ev: dict) -> dict:
    out = {"title": v["title"], "channel": v["channel"], "length": E.ts(v.get("duration_s") or 0),
           "published": (v.get("published") or "")[:10], "text_source": ev["source"]}
    if v.get("replayed"):        # 17 Nov: the watch page's most-replayed peaks, a hint for the skim
        out["most_replayed"] = [f"{E.ts(r['start'])}-{E.ts(r['end'])}" for r in v["replayed"]]
    return out


def skim_windows(llm, lecture: dict, parts: list[dict], v: dict, ev: dict, hint_parts: list[int], trace: Trace, run_id: str) -> tuple[list[dict], str]:
    """Regions [(part, a, b)] of a long video worth reading in full."""
    res, model = ask(llm, "Y4", {"lecture": lecture, "parts": _parts_ctx(parts), "video": _video_ctx(v, ev),
                                 "chapters": E.chapters_text(ev["chapters"]), "skim": E.skim(ev["rows"]),
                                 "every": cfg()["reading"]["skim_every_s"]}, Mx.SkimReading, trace, f"{lecture['lecture_id']}/{v['id']}", run_id)
    dur = float(v.get("duration_s") or 0)
    out = []
    for w in res.windows:
        a, b = E.secs(w.start), E.secs(w.end)
        if a is None or b is None or not -1 <= w.part < len(parts):
            continue
        a, b = max(0.0, a), min(dur or b, b)
        if 90 <= b - a <= 40 * 60:
            out.append({"part": w.part, "a": a, "b": b, "why": w.why})
    return out, model


def zoom_clips(llm, lecture: dict, parts: list[dict], v: dict, ev: dict, regions: list[tuple[float, float]],
               trace: Trace, run_id: str, focus: list[int] | None = None) -> tuple[list[dict], str]:
    """Exact clips, from the full words of the given regions (the whole video for short ones). Checked by code: times in
    range, length bounds, quotes found near the boundaries, boundaries snapped to caption lines."""
    c, r = cfg()["lecture"], cfg()["reading"]
    rows, dur = ev["rows"], float(v.get("duration_s") or 0)
    if rows:
        merged = []
        for a, b in sorted((max(0, a - r["zoom_margin_s"]), min(dur, b + r["zoom_margin_s"])) for a, b in regions):
            if merged and a <= merged[-1][1]:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        # Long regions are read in consecutive chunks that each fit one call (16 Nov: the text was cut at zoom_max_chars,
        # so a 72-104 min workshop was read only for its first ~12 min and yielded 0-10 min of clips).
        chunks, cur = [], []
        for a, b in merged:
            lines = E.full(rows, a, b).splitlines()
            for ln in lines:
                if cur and sum(len(x) + 1 for x in cur) + len(ln) > r["zoom_max_chars"]:
                    chunks.append("\n".join(cur))
                    cur = cur[-3:]                         # ~1 min overlap, so an explanation is not cut at the seam
                cur.append(ln)
            cur.append("[... skipped]")
        if cur:
            chunks.append("\n".join(cur).removesuffix("[... skipped]").strip())
        chunks = [x for x in chunks if x.strip()]
        if len(chunks) > r.get("zoom_max_chunks", 4):
            trace.step(f"{lecture['lecture_id']}/{v['id']}", "regions longer than the reading limit; the rest was not read",
                       chunks=len(chunks), read=r.get("zoom_max_chunks", 4))
            chunks = chunks[: r.get("zoom_max_chunks", 4)]
    else:
        chunks = ["(chapters only: no words available)\n" + E.chapters_text(ev["chapters"])]
    got, model = [], "?"
    for text in chunks:
        res, model = ask(llm, "Y5", {"lecture": lecture, "parts": _parts_ctx(parts), "video": _video_ctx(v, ev),
                                     "chapters": E.chapters_text(ev["chapters"]), "text": text,
                                     "clip_min": c["clip_min_s"] // 60, "clip_max": c["clip_max_s"] // 60,
                                     "focus": [{"part": i, "title": parts[i]["title"]} for i in (focus or []) if 0 <= i < len(parts)]},
                         Mx.ZoomReading, trace, f"{lecture['lecture_id']}/{v['id']}", run_id)
        got += [(k, model) for k in res.clips]
    out = []
    for k, model in got:
        a, b = E.secs(k.start), E.secs(k.end)
        if a is None or b is None or not -1 <= k.part < len(parts) or (k.part == -1 and not k.extra_title.strip()):
            continue
        notes = []
        if rows:
            qa, qb = E.quote_near(k.start_quote, rows, a), E.quote_near(k.end_quote, rows, b)
            if qa is not None:
                a = qa
            else:
                notes.append("start quote not found")
            if qb is not None:
                b = max(b, qb)
            else:
                notes.append("end quote not found")
            a, b = E.snap(rows, a, "start"), E.snap(rows, b, "end")
            a, b = E.sentence_start(rows, a), E.sentence_end(rows, b)      # whole sentences at both ends
        b = min(b, dur) if dur else b
        if k.treatment == "mentions" or k.rating < 2 or b <= a:
            continue
        if rows and len(notes) == 2:    # 17 Nov audit: neither boundary is in the words, so the times may be invented
            trace.step(f"{lecture['lecture_id']}/{v['id']}", "clip dropped: neither quote found in the words", part=k.part,
                       start=k.start, end=k.end)
            continue
        npts = len(part_def({"part": k.part, "extra_title": k.extra_title}, parts, lecture)["must_cover"])
        out.append({"video": v["id"], "part": k.part, "extra_title": k.extra_title.strip()[:90] if k.part == -1 else "",
                    "a": round(a), "b": round(b), "covers": sorted(set(i for i in k.covers if 0 <= i < npts)),
                    "treatment": k.treatment, "standalone": k.standalone, "level": k.level, "rating": k.rating,
                    "concerns": k.concerns, "summary": k.summary, "evidence": ev["source"] if rows else "chapters",
                    "reader": model, "quote_notes": notes})
    # Stitch: fast readers often cut one explanation into neighbouring pieces (15 Nov: many 60-115 s pieces, each then
    # dropped as too short). Pieces of the same part less than a minute apart become one clip, then the length rule applies.
    out.sort(key=lambda k: (k["part"], k["a"]))
    stitched: list[dict] = []
    for k in out:
        prev = stitched[-1] if stitched else None
        if prev and prev["part"] == k["part"] and k["a"] - prev["b"] <= 60 and k["b"] - prev["a"] <= c["clip_max_s"]:
            prev["b"] = max(prev["b"], k["b"])
            prev["covers"] = sorted(set(prev["covers"]) | set(k["covers"]))
            prev["rating"] = max(prev["rating"], k["rating"])
            prev["standalone"] = prev["standalone"]
            prev["summary"] = f"{prev['summary']} {k['summary']}"[:600]
        else:
            stitched.append(dict(k))
    keep = []
    for k in stitched:
        if c["clip_min_s"] <= k["b"] - k["a"] <= c["clip_max_s"]:
            keep.append(k)
        else:
            trace.step(f"{lecture['lecture_id']}/{v['id']}", "clip dropped: length out of bounds", part=k["part"], length=k["b"] - k["a"])
    return keep, model


# ---------------------------------------------------------------- Y6 verifier
def verify(llm, lecture: dict, parts: list[dict], clips: list[dict], evs: dict[str, dict], trace: Trace, run_id: str) -> None:
    """Adds `check` to each clip. Batched; each batch excludes every model that cut a clip in it."""
    r = cfg()["reading"]
    lim = r["verify_max_chars"]
    batches, cur, size, cur_reader = [], [], 0, None
    # 17 Nov audit: batches are grouped by reader, so each excludes one model, not every reader in a mixed batch; a clip
    # longer than the limit gets its own batch with up to twice the words (it was cut at the limit, so the verifier never
    # saw its second half), and the cut is closed properly.
    for i in sorted(range(len(clips)), key=lambda i: str(clips[i].get("reader"))):
        k = clips[i]
        ev = evs[k["video"]]
        words = E.plain(ev["rows"], k["a"], k["b"]) if ev["rows"] else "(chapters only) " + "; ".join(
            ch["title"] for ch in ev["chapters"] if ch["end"] > k["a"] and ch["start"] < k["b"])
        p = part_def(k, parts, lecture)
        head = (f'<clip id="c{i}" part="{k["part"]}" part_title="{p["title"]}">\nmust_cover: '
                + json.dumps({j: m for j, m in enumerate(p["must_cover"])}, ensure_ascii=False) + "\nwords: ")
        if len(head) + len(words) + 8 > lim:
            if len(head) + len(words) + 8 > 2 * lim:
                trace.step(lecture["lecture_id"], "clip too long for one verifier call; its end was not checked",
                           video=k["video"], words=len(words))
            words = words[: 2 * lim - len(head) - 30] + " [...]"
            batches.append([(i, head + words + "\n</clip>")])
            continue
        block = head + words + "\n</clip>"
        if cur and (size + len(block) > lim or k.get("reader") != cur_reader):
            batches.append(cur)
            cur, size = [], 0
        cur.append((i, block))
        size += len(block)
        cur_reader = k.get("reader")
    if cur:
        batches.append(cur)
    retried: set[int] = set()
    while batches:
        b = batches.pop(0)
        exclude = frozenset(clips[i]["reader"] for i, _ in b if clips[i].get("reader") and clips[i]["reader"] != "?")
        try:
            res, model = ask(llm, "Y6", {"lecture": lecture, "clips": "\n".join(x for _, x in b)}, Mx.Verification, trace,
                             lecture["lecture_id"], run_id, exclude=exclude)
        except Exception as e:  # noqa: BLE001
            if len(b) > 1:   # 17 Nov: with the reader's model excluded only small-prompt models were left: one clip each
                batches = [[x] for x in b] + batches
                trace.step(lecture["lecture_id"], f"verifier batch failed ({type(e).__name__}); retrying its {len(b)} clips one by one")
            else:            # no other model left: the clip stays unverified (scored lower)
                trace.step(lecture["lecture_id"], f"verifier failed ({type(e).__name__}); clip left unverified")
            continue
        got = {c.clip: c for c in res.checks}
        missing = [(i, x) for i, x in b if f"c{i}" not in got and i not in retried]
        if missing:                       # the model left clips out of its answer: once more, on their own
            retried |= {i for i, _ in missing}
            batches.append(missing)
            trace.step(lecture["lecture_id"], f"verifier skipped {len(missing)} clips; asking again")
        for i, _ in b:
            k, chk = clips[i], got.get(f"c{i}")
            if chk is None:
                continue
            ev = evs[k["video"]]
            text = E.plain(ev["rows"], k["a"] - 5, k["b"] + 5) if ev["rows"] else ""
            n = len(part_def(k, parts, lecture)["must_cover"])
            pts: dict[str, float] = {}
            for pv in chk.points:
                if not 0 <= pv.point < n or pv.taught == "no":
                    continue
                ok = bool(text) and E.quote_near(pv.quote, [{"start": 0, "dur": 1, "text": text}], 0, 1e9) is not None
                w = (1.0 if pv.taught == "yes" else 0.5) * (1.0 if ok else 0.5)   # an unfound quote counts half
                pts[str(pv.point)] = max(pts.get(str(pv.point), 0.0), w)
            k["check"] = {"coverage": round(sum(pts.values()) / max(n, 1), 2), "points": pts, "standalone": chk.standalone,
                          "accurate": chk.accurate, "recommend": chk.recommend, "issue": chk.issue, "checker": model}


# ---------------------------------------------------------------- Y7 gaps
def gaps(llm, topic: dict, gap_list: list[dict], trace: Trace, run_id: str) -> list[dict]:
    res, _ = ask(llm, "Y7", {"topic": topic, "gaps": gap_list}, Mx.GapPlan, trace, topic["id"], run_id)
    ok = {(g["lecture_id"], g["part"]) for g in gap_list}
    return [a.model_dump() for a in res.actions if (a.lecture_id, a.part) in ok]
