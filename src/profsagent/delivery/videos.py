"""Videos for a topic's components (architecture aid A4): search once per topic, verify segments per lecture.

  search      the D1 video queries of the topic's lectures (cached 21 days) → YouTube details
  filter      no Shorts (< 3 min), nothing blocked; longer recorded lectures are welcome (only a segment is used)
  transcripts for the videos whose title/description best match the components (one fetch per video, cached 90 days)
  segments    locate → AI check (D6) → choose, per lecture (segments.py)
  2nd pass    components still without a video get their own YouTube search (a few per topic), then the same steps
Output per lecture: the videos used (with the components and minutes each teaches), alternatives, the clip list in
teaching order, and the timeline (component → delivered by video / NotebookLM / in class).
"""
from __future__ import annotations

from profsagent.delivery.common import embed, hms, rcfg
from profsagent.delivery.resources import blocked, reception, tier_of_channel
from profsagent.delivery.segments import check, choose, component_text, locate
from profsagent.delivery.sources import YouTube, transcript, transcripts_blocked


def records(yt: YouTube, ids: list[str]) -> list[dict]:
    details = yt.videos(ids)
    chans = yt.channels([d["channel_id"] for d in details.values()])
    out = []
    for vid in ids:
        d = details.get(vid)
        if d:
            out.append({**d, "kind": "video", "source": d["channel"], "tier": tier_of_channel(d["channel"]),
                        "subscribers": (chans.get(d["channel_id"]) or {}).get("subscribers"), "free": True})
    return out


def usable(v: dict) -> str | None:
    """Why a video cannot teach a component, or None."""
    dur = v.get("duration_s") or 0
    if dur < rcfg()["segments"]["min_video_s"]:
        return f"too short to teach a component ({hms(dur)})"
    if dur > 3 * 3600:
        return f"too long to find a segment in ({hms(dur)})"
    if not v.get("public", True):
        return "video is not public"
    if v.get("blocked_in_india"):
        return "video is not available in India"
    if v.get("made_for_kids"):
        return "video is made for children"
    lang = (v.get("language") or "en").lower()
    if not (lang.startswith("en") or lang.startswith("hi")):
        return f"audio language is '{lang}'"
    return blocked(v.get("url", ""), v.get("title", ""))


def fetch_transcripts(vids: list[dict], comps: list[dict], n: int, log) -> None:
    """Transcripts for the n videos whose title and description best match the components."""
    todo = [v for v in vids if "_tr" not in v and not v.get("dead")]
    if not todo or not comps:
        return
    cv = embed([component_text(c) for c in comps])
    vv = embed([f"{v['title']}. {(v.get('description') or '')[:400]}" for v in todo])
    pre = (vv @ cv.T).max(axis=1)
    for v, p in zip(todo, pre):
        v["_pre"] = float(p) + 0.05 * (4 - v["tier"]) / 3
    for v in sorted(todo, key=lambda v: -v["_pre"])[:n]:
        v["_tr"] = transcript(v["id"])
        v["transcript"] = bool(v["_tr"])
        if v["_tr"]:
            v["captions"] = True
        elif transcripts_blocked():
            v["_tx_missing"] = True


def deliver_topic(llm, st: dict, plan: dict, briefs: dict, lids: list[str], queries: dict, run_id: str, log) -> dict:
    """{lecture_id: {timeline, videos, reserve, clips, rejected, partial?}} for the topic's lectures in `lids`."""
    cfg, yt = rcfg()["segments"], YouTube()
    comps_all = [c for c in plan["components"] if not c.get("in_class")]
    qs = list(dict.fromkeys(q for lid in sorted(plan_lids(plan)) for q in (queries.get(lid) or {}).get("video_queries", [])))
    qs = qs[: rcfg()["youtube"]["max_searches_per_lecture"] + len(plan["lectures"]) - 1]
    ids = list(dict.fromkeys(v for q in qs for v in yt.search(q)))
    vids, rejected = [], []
    for v in records(yt, ids):
        why = usable(v)
        (rejected.append({"title": v["title"], "url": v["url"], "why": [why]}) if why else vids.append(v))
    fetch_transcripts(vids, comps_all, cfg["transcripts_per_topic"], log)
    by_vid = {v["id"]: v for v in vids}
    log(f"  videos {plan['topic_id']}: {len(ids)} found, {len(vids)} usable, {sum(1 for v in vids if v.get('_tr'))} transcripts")
    out = {}
    checked_all: dict[str, list[dict]] = {}
    for lid in lids:
        comps = [c for c in plan["components"] if c["lecture_id"] == lid]
        teach = [c for c in comps if not c.get("in_class")]
        cands = locate(teach, [v for v in vids if v.get("_tr")])
        checked_all[lid] = check(llm, briefs[lid], st, teach, cands, by_vid, run_id, log) if cands else []
    # second pass: a search of its own for the components no video teaches, then for those only partly taught
    # (1 Nov trial: one such search found three videos that teach the MCP handshake fully)
    def need(c: dict) -> int | None:
        got = {s.get("verdict") for s in checked_all[c["lecture_id"]] if s["cid"] == c["id"]}
        return None if "teaches_fully" in got else 1 if "teaches_partly" in got else 0
    todo = [c for c in plan["components"] if c["lecture_id"] in lids and not c.get("in_class") and need(c) is not None]
    searches = 0
    for c in sorted(todo, key=lambda c: (need(c), -c["minutes"])):
        if searches >= cfg["component_searches_per_topic"] or not yt.quota.can(100):
            break
        searches += 1
        new_ids = [i for i in yt.search(f"{c['title']} {plan['topic']}"[:120]) if i not in by_vid]
        new = [v for v in records(yt, new_ids) if not usable(v)]
        fetch_transcripts(new, [c], 2, log)
        for v in new:
            by_vid[v["id"]] = v
            vids.append(v)
        cands = locate([c], [v for v in new if v.get("_tr")])
        if cands:
            checked_all[c["lecture_id"]] += check(llm, briefs[c["lecture_id"]], st, [c], cands, by_vid, run_id, log)
    if searches:
        log(f"  videos {plan['topic_id']}: {searches} component search(es) for parts no video taught (fully)")
    for lid in lids:
        comps = [c for c in plan["components"] if c["lecture_id"] == lid]
        timeline, alts = choose(comps, checked_all[lid], by_vid)
        out[lid] = build(lid, comps, timeline, alts, by_vid, rejected)
        missing = [v["id"] for v in vids if v.get("_tx_missing") and not v.get("_tr")]
        if missing:
            out[lid]["partial"] = {"reason": f"YouTube blocked transcript requests (from {transcripts_blocked()})",
                                   "videos_without_transcript": missing}
    return out


def plan_lids(plan: dict) -> list[str]:
    return [x["lecture_id"] for x in plan["lectures"]]


def build(lid: str, comps: list[dict], timeline: list[dict], alts: list[dict], by_vid: dict, rejected: list[dict]) -> dict:
    title = {c["id"]: c["title"] for c in comps}
    lecture_min = sum(c["minutes"] for c in comps) or 1
    used: dict[str, list[dict]] = {}
    for row in timeline:
        for s in row["segments"]:
            used.setdefault(s["vid"], []).append(s)
    videos = [video_item(by_vid[v], ss, title, lecture_min) for v, ss in used.items()]
    videos.sort(key=lambda x: (-x["scores"]["teaches"], -x["total"]))
    reserve_by: dict[str, list[dict]] = {}
    for s in alts:
        if s["vid"] not in used:
            reserve_by.setdefault(s["vid"], []).append(s)
    reserve = sorted((video_item(by_vid[v], ss, title, lecture_min) for v, ss in reserve_by.items()), key=lambda x: -x["total"])
    for i, x in enumerate(videos, 1):
        x["rank"], x["status"] = i, "proposed"
    for i, x in enumerate(reserve, len(videos) + 1):
        x["rank"], x["status"] = i, "reserve"
    clips = []
    for row in timeline:
        for s in row["segments"]:
            v = by_vid[s["vid"]]
            clips.append({"target": row["title"], "target_ids": [row["component"]], "component": row["component"],
                          "video": v["title"], "source": v.get("source"), "url": f"https://www.youtube.com/watch?v={v['id']}&t={int(s['start'])}s",
                          "start": hms(s["start"]), "end": hms(s["end"]), "minutes": round((s["end"] - s["start"]) / 60, 1),
                          "component_minutes": row["minutes"], "verdict": s["verdict"], "covered": s.get("covered", []),
                          "missing": s.get("missing", []), "note": s.get("note", "")})
    tl = [{"component": r["component"], "title": r["title"], "minutes": r["minutes"], "kind": r.get("kind"), "delivery": r["delivery"],
           **({"gap": r["gap"]} if r.get("gap") else {}),
           "segments": [{"video": by_vid[s["vid"]]["title"], "video_id": s["vid"],
                         "url": f"https://www.youtube.com/watch?v={s['vid']}&t={int(s['start'])}s",
                         "start": hms(s["start"]), "end": hms(s["end"]), "minutes": round((s["end"] - s["start"]) / 60, 1),
                         "verdict": s["verdict"], "score": s.get("score")}
                        for s in r["segments"]]} for r in timeline]
    return {"timeline": tl, "videos": videos, "reserve": reserve[:4], "clips": clips, "rejected": rejected[:15]}


def video_item(v: dict, segs: list[dict], title: dict, lecture_min: int) -> dict:
    """A video as the lecture file shows it: which components it teaches, where, and how well."""
    segs = sorted(segs, key=lambda s: s["start"])
    w = {"teaches_fully": 1.0, "teaches_partly": 0.55}
    taught = sum(w.get(s["verdict"], 0) * min(s["end"] - s["start"], 60 * 30) / 60 for s in segs)
    best = max((s.get("score") or 0) for s in segs)
    clarity = sum(s.get("clarity") or 3 for s in segs) / len(segs)
    level = sum(s.get("level_fit") or 3 for s in segs) / len(segs)
    scores = {"teaches": round(min(1.0, taught / lecture_min), 3), "segment": round(best, 3), "clarity": round(clarity / 5, 3),
              "level_fit": round(level / 5, 3), "authority": rcfg()["tier_scores"][v.get("tier", 4)], "reception": reception(v)}
    total = round(0.75 * scores["segment"] + 0.15 * scores["reception"] + 0.10 * scores["teaches"], 3)
    parts = [f"{s['cid'].split('.')[-1]} {title.get(s['cid'], '')[:60]} ({hms(s['start'])}–{hms(s['end'])}, "
             f"{'fully' if s['verdict'] == 'teaches_fully' else 'partly'})" for s in segs]
    meta = [v.get("source") or "", f"tier {v.get('tier')}", hms(v.get("duration_s"))]
    if v.get("views"):
        meta.append(f"{v['views']:,} views")
    item = {k: v[k] for k in ("kind", "id", "url", "title", "source", "tier", "duration_s", "published", "licence", "captions",
                              "views", "likes", "comments", "subscribers", "transcript") if v.get(k) is not None}
    findings = [] if v.get("embeddable", True) else [{"code": "R-EMBED", "severity": "warning",
                                                      "message": "video cannot be embedded in the course page (link only)"}]
    item.update(scores=scores, total=total, findings=findings,
                rationale="Teaches " + "; ".join(parts) + " [checked on the transcript] · " + " · ".join(m for m in meta if m),
                components=[{"id": s["cid"], "title": title.get(s["cid"], ""), "start": hms(s["start"]), "end": hms(s["end"]),
                             "start_s": round(s["start"], 1), "end_s": round(s["end"], 1), "verdict": s["verdict"],
                             "covered": s.get("covered", []), "missing": s.get("missing", []), "note": s.get("note", ""),
                             "chapter": s.get("chapter")} for s in segs],
                coverage={"score": scores["teaches"], "evidence": "transcript",
                          "per_target": {s["cid"]: {"text": title.get(s["cid"], ""), "covered": True, "sim": s["peak"],
                                                    "segments": [{"start": round(s["start"], 1), "end": round(s["end"], 1), "sim": s["peak"]}]}
                                         for s in segs}},
                review={"review": "; ".join(x for x in (s.get("note") for s in segs) if x)[:300],
                        "issues": [f"leaves out: {m}" for s in segs for m in s.get("missing", [])][:4],
                        "use_as": "in_class_clip", "explains": "explains"})
    if v.get("description"):
        item["description"] = v["description"][:700]
    return item
