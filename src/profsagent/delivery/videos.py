"""Videos for a lecture (decided 10 Nov, docs/decisions.md 38). The funnel, cheapest evidence first:

  find        each lecture's D1 queries on YouTube; a free DuckDuckGo video search for every part; the topic's university lecture
              series (playlists of tier 1-2 channels). Every part is searched without spending YouTube quota on each.
  filter      metadata only: no Shorts, trailers, blocked or foreign-language videos, no re-uploads of the same title
  shortlist   title, description and chapters against the parts, picked so that together they reach the most parts; only these
              cost a transcript (40 new ones an hour), and ones already cached cost nothing
  extract     captions; for a worthwhile video with none (or while YouTube blocks them) Gemini's timestamped notes of the video
  read        the AI reads the videos that together reach the most parts and says which parts each teaches and where (D9)
  verify      a different model checks each clip on every word of it (D10); programs check its quotes and apply the gate
  2nd pass    the longest parts still without a clip get a YouTube search of their own, then the same steps
  plan        among the clips that passed, the best plan for the lecture: one video across consecutive parts is one block (segments.py)

A part with no clip that passed gets no video at all; the delivery mix gives it NotebookLM or slides. A partly useful video is
never shown to students, but it is kept as a source for NotebookLM (`sources`).
"""
from __future__ import annotations

import re

import numpy as np

from profsagent.delivery.common import embed, hms, rcfg, years_since
from profsagent.delivery.resources import blocked, reception, tier_of_channel
from profsagent.delivery.segments import (
    assign, blocks_of, chapters, closeness, component_text, read, utility, vcfg, verify)
from profsagent.delivery.sources import YouTube, transcript, transcript_known, transcripts_blocked, video_notes, web_videos


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
    """Why a video cannot teach a part, or None. Metadata only."""
    dur = v.get("duration_s") or 0
    if dur < vcfg()["min_video_s"]:
        return f"too short to teach a part ({hms(dur)})"
    if dur > 3 * 3600:
        return f"too long to find a clip in ({hms(dur)})"
    if not v.get("public", True):
        return "video is not public"
    if v.get("blocked_in_india"):
        return "video is not available in India"
    if v.get("made_for_kids"):
        return "video is made for children"
    lang = (v.get("language") or "en").lower()
    if not (lang.startswith("en") or lang.startswith("hi")):
        return f"audio language is '{lang}'"
    if re.search(vcfg()["skip_titles"], v.get("title") or "", re.I):
        return "a trailer, Short or course overview"
    return blocked(v.get("url", ""), v.get("title", ""))


def _title_key(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()[:60]


def meta_text(v: dict) -> str:
    ch = "; ".join(c["title"] for c in chapters(v.get("description", ""), v.get("duration_s")))
    return f"{v['title']}. {ch or (v.get('description') or '')[:400]}"


def lecture_series(yt: YouTube, topic: str) -> list[dict]:
    """[{id, title}] of lectures in the playlists that universities and established educators have on this topic."""
    cfg = vcfg()
    out, seen = [], set()
    lists = [p for p in yt.playlists(f"{topic} lecture course") if tier_of_channel(p["channel"]) <= 2]
    for p in lists[: cfg["series_max_playlists"]]:
        for x in yt.playlist_items(p["id"]):
            if x["id"] not in seen:
                seen.add(x["id"])
                out.append(x)
    return out


def series_for(series: list[dict], parts: list[dict]) -> list[str]:
    cfg = vcfg()
    if not series or not parts:
        return []
    s = (embed([x["title"] for x in series]) @ embed([component_text(c) for c in parts]).T).max(axis=1)
    order = [int(i) for i in np.argsort(-s) if s[i] >= cfg["series_min_sim"]]
    return [series[i]["id"] for i in order[: cfg["series_videos_per_lecture"]]]


def shortlist(vids: list[dict], parts: list[dict], new_budget: int, max_total: int, novel: bool = False) -> list[dict]:
    """Greedy, on metadata: each pick is the video that adds the most to how well the parts are reached, so ten videos on the
    same part do not use up the transcripts. Views play no part. Transcripts already known cost no budget."""
    if not vids or not parts:
        return []
    S = embed([meta_text(v) for v in vids]) @ embed([component_text(c) for c in parts]).T
    recent = rcfg()["recency_years_fast_topics"]
    bonus = np.array([0.05 * (4 - v.get("tier", 4)) / 3 + (vcfg()["series_bonus"] if v.get("series") else 0)
                      - (0.05 if novel and (years_since(v.get("published")) or 0) > recent else 0) for v in vids])
    for v, row in zip(vids, S):
        v["_meta"] = float(row.max())
    covered, chosen, left, new = np.zeros(len(parts)), [], list(range(len(vids))), 0
    while left and len(chosen) < max_total:
        gains = [float((np.maximum(S[i], covered) - covered).sum() + bonus[i] + 0.001 * S[i].max()) for i in left]
        i = left.pop(int(np.argmax(gains)))
        if not transcript_known(vids[i]["id"]):
            if new >= new_budget:
                continue
            new += 1
        chosen.append(vids[i])
        covered = np.maximum(covered, S[i])
    return chosen


def extract(vids: list[dict], n_notes: int, log) -> None:
    """Captions for each video; then notes for the best ones left without any."""
    cfg = vcfg()
    for v in vids:
        if "_tr" in v:
            continue
        v["_tr"] = transcript(v["id"])
        v["transcript"] = bool(v["_tr"])
        if v["_tr"]:
            v["captions"], v["evidence"] = True, "captions"
        elif transcripts_blocked():
            v["_tx_missing"] = True
    pool = [v for v in vids if not v.get("_tr") and v.get("tier", 4) <= 2 and v.get("_meta", 0) >= cfg["notes_min_score"]]
    for v in sorted(pool, key=lambda v: -v.get("_meta", 0))[:n_notes]:
        got = video_notes(v["id"], v.get("duration_s"))
        if got:
            v["_tr"], v["transcript"], v["evidence"] = got, True, "notes"
            log(f"  notes from the video itself: {v['title'][:60]}")
        else:
            log(f"  no notes could be made for: {v['title'][:60]}")


def to_read(vids: list[dict], parts: list[dict], n: int) -> list[dict]:
    """The videos worth an AI call: greedy on how closely their passages (not titles) match the parts."""
    cfg = vcfg()
    rows = [(v, closeness(parts, v)) for v in vids if v.get("_tr")]
    rows = [(v, m.max(axis=0)) for v, m in rows if m is not None and float(m.max()) >= cfg["sim_floor"]]
    picked, covered = [], np.zeros(len(parts))
    while rows and len(picked) < n:
        g = [float((np.maximum(p, covered) - covered).sum() + 0.02 * (4 - v.get("tier", 4)) + (cfg["series_bonus"] if v.get("series") else 0)
                   + 0.001 * p.max()) for v, p in rows]
        v, p = rows.pop(int(np.argmax(g)))
        picked.append(v)
        covered = np.maximum(covered, p)
    return picked


class Lecture:
    """What is known so far about one lecture's videos."""

    def __init__(self, parts: list[dict]):
        self.parts, self.passed, self.tried, self.partly = parts, [], [], []
        self.map: dict[str, dict] = {}
        self.read_failed = 0
        self.funnel = {"found": 0, "usable": 0, "shortlisted": 0, "with_text": 0, "read": 0, "checked": 0, "passed": 0}

    def open_parts(self) -> list[dict]:
        got = {s["cid"] for s in self.passed}
        return [c for c in self.parts if c["id"] not in got]


def study(llm, b: dict, st: dict, lec: Lecture, parts: list[dict], vids: list[dict], by_vid: dict, run_id: str, log) -> None:
    """D9 on each video, then D10 on the most promising clips of each part until one passes."""
    cfg = vcfg()
    found, reader = [], {}
    for v in vids:
        r = read(llm, b, st, parts, v, run_id, log)
        lec.read_failed += r["failed"]
        lec.funnel["read"] += 1
        row = lec.map.setdefault(v["id"], {"video": v["title"], "url": v["url"], "channel": v.get("source"), "text": v.get("evidence"), "parts": {}})
        for f in r["findings"]:
            reader[f["vid"]] = r["reader"]
            found.append(f)
            row["parts"][f["cid"]] = {"claim": f["claim"], "start": hms(f["start"]), "end": hms(f["end"]), "result": "not checked"}
    teaches_many = {}
    for f in found:
        teaches_many[f["vid"]] = teaches_many.get(f["vid"], 0) + (f["claim"] == "fully")
    by_c: dict[str, list[dict]] = {}
    for f in found:
        by_c.setdefault(f["cid"], []).append(f)
    for c in parts:
        # a video the reader says teaches several parts is tried first: that is what lets it become one block
        fs = sorted(by_c.get(c["id"], []), key=lambda f: (f["claim"] != "fully", -teaches_many[f["vid"]],
                                                         -(f["peak"] + 0.02 * (4 - by_vid[f["vid"]].get("tier", 4)))))
        full = [f for f in fs if f["claim"] == "fully"]
        for f in fs:
            lec.partly.append(f)                          # whatever is found stays usable as a NotebookLM source
        for f in (full or fs)[: cfg["verify_per_part"]]:
            v = by_vid[f["vid"]]
            res = verify(llm, b, st, c, f, v, reader.get(f["vid"], ""), run_id, log)
            cell = lec.map[f["vid"]]["parts"][c["id"]]
            if res is None:
                cell["result"] = "could not be checked"
                continue
            lec.funnel["checked"] += 1
            lec.tried.append(res)
            cell.update(result="passed" if not res["failed_gate"] else "failed", why=res["failed_gate"], coverage=res["coverage"],
                        relevance=res["relevance"], sufficiency=res["sufficiency"], checker=res["checker"], reader=res["reader"])
            log(f"  [D10] {c['id']} {hms(f['start'])}–{hms(f['end'])} of {v['title'][:45]}: "
                + ("passed" if not res["failed_gate"] else "failed (" + "; ".join(res["failed_gate"][:3]) + ")"))
            if not res["failed_gate"]:
                lec.passed.append(res)
                lec.funnel["passed"] += 1
                break


def deliver_topic(llm, st: dict, plan: dict, briefs: dict, lids: list[str], queries: dict, run_id: str, log) -> dict:
    """{lecture_id: {timeline, blocks, videos, reserve, clips, rejected, sources, search, partial?}} for the topic's lectures in `lids`."""
    cfg, yt = vcfg(), YouTube()
    pool: dict[str, dict] = {}
    rejected: list[dict] = []
    series = lecture_series(yt, plan["topic"]) if lids else []
    log(f"  videos {plan['topic_id']}: {len(series)} lectures in university series")
    taken: list[dict] = []
    out = {}

    def add(ids: list[str], lec: Lecture | None) -> list[dict]:
        """Records for new ids (details are 1 unit per 50), filtered; returns all usable ones among `ids`."""
        new = [i for i in ids if i not in pool]
        for v in records(yt, new):
            why = usable(v)
            if why:
                rejected.append({"title": v["title"], "url": v["url"], "why": [why]})
                pool[v["id"]] = {**v, "unusable": True}
            else:
                pool[v["id"]] = v
        got, seen = [], set()
        for i in ids:
            v = pool.get(i)
            if v and not v.get("unusable") and _title_key(v["title"]) not in seen:
                seen.add(_title_key(v["title"]))
                got.append(v)
        return got

    for lid in lids:
        b = briefs[lid]
        comps = [c for c in plan["components"] if c["lecture_id"] == lid]
        parts = [c for c in comps if not c.get("in_class")]
        lec = Lecture(parts)
        skipped_before = YouTube.skipped
        ids: list[str] = []
        for q in (queries.get(lid) or {}).get("video_queries", [])[: rcfg()["youtube"]["max_searches_per_lecture"]]:
            ids += yt.search(q)
        if cfg["part_web_search"]:
            for c in parts:
                ids += web_videos(f"{c['title']} {plan['topic']} lecture"[:120])[:8]
        from_series = series_for(series, parts)
        ids = list(dict.fromkeys(ids + from_series))
        cands = add(ids, lec)
        for v in cands:
            v["series"] = v.get("series") or v["id"] in from_series
        lec.funnel.update(found=len(ids), usable=len(cands))
        short = shortlist(cands, parts, cfg["transcripts_per_lecture"], cfg["max_shortlist"], bool(b.get("novel")))
        extract(short, cfg["notes_when_blocked"] if transcripts_blocked() else cfg["notes_per_lecture"], log)
        lec.funnel.update(shortlisted=len(short), with_text=sum(1 for v in short if v.get("_tr")))
        chosen = to_read(short, parts, cfg["read_per_lecture"])
        log(f"  {lid}: {len(ids)} found, {len(cands)} usable, {len(short)} shortlisted, {lec.funnel['with_text']} with text, reading {len(chosen)}")
        study(llm, b, st, lec, parts, chosen, pool, run_id, log)
        # second pass: the longest parts still without a clip get a YouTube search of their own
        for c in sorted(lec.open_parts(), key=lambda c: -c["minutes"])[: cfg["part_searches_per_lecture"]]:
            if not yt.quota.can(100):
                YouTube.skipped += 1
                break
            new = add([i for i in yt.search(f"{c['title']} {plan['topic']}"[:120]) if i not in {v["id"] for v in short}], lec)
            s2 = shortlist(new, [c], cfg["transcripts_per_part_search"], cfg["transcripts_per_part_search"])
            extract(s2, 0, log)
            lec.funnel["with_text"] += sum(1 for v in s2 if v.get("_tr"))
            study(llm, b, st, lec, [c], to_read(s2, [c], cfg["transcripts_per_part_search"]), pool, run_id, log)
        plan_ = assign(comps, lec.passed, pool, taken)
        taken += [s for s in plan_["path"] if s is not None]
        out[lid] = build(lid, comps, plan_, pool, rejected, lec)
        log(f"  {lid}: {sum(1 for s in plan_['path'] if s)} of {len(parts)} parts have a video, in {len(out[lid]['blocks'])} block(s)")
        reasons = []
        missing = [v["id"] for v in short if v.get("_tx_missing") and not v.get("_tr")]
        if missing:
            reasons.append(f"YouTube blocked transcript requests (from {transcripts_blocked()})")
        if YouTube.skipped > skipped_before:
            reasons.append("the YouTube search quota ran out or the API failed")
        if lec.read_failed:
            reasons.append(f"{lec.read_failed} video(s) could not be read (no AI model answered)")
        if reasons:                                       # "no video" here is not a finding: the next run redoes this lecture
            out[lid]["partial"] = {"reason": "; ".join(reasons), "videos_without_transcript": missing}
    return out


def plan_lids(plan: dict) -> list[str]:
    return [x["lecture_id"] for x in plan["lectures"]]


def _link(vid: str, start: float) -> str:
    return f"https://www.youtube.com/watch?v={vid}&t={int(start)}s"


def build(lid: str, comps: list[dict], plan: dict, by_vid: dict, rejected: list[dict], lec: Lecture) -> dict:
    """The lecture's file: the same shape the rest of the system reads (timeline, videos, clips), plus the blocks and the search."""
    path, title = plan["path"], {c["id"]: c["title"] for c in comps}
    lecture_min = sum(c["minutes"] for c in comps) or 1
    blocks = blocks_of(comps, path)
    block_id = {i: f"b{k}" for k, b in enumerate(blocks, 1) for i in b}
    for i, s in enumerate(path):
        if s is not None:
            s["block"], s["score"] = block_id[i], round(utility(s, by_vid[s["vid"]]) - 1, 3)
    timeline, clips = [], []
    for i, c in enumerate(comps):
        s = path[i]
        row = {"component": c["id"], "title": c["title"], "minutes": c["minutes"], "kind": c.get("kind"), "segments": []}
        row["delivery"] = "in_class" if c.get("in_class") else "video" if s else "notebooklm"
        if s:
            v = by_vid[s["vid"]]
            mins = round((s["end"] - s["start"]) / 60, 1)
            row["segments"].append({"video": v["title"], "video_id": s["vid"], "url": _link(s["vid"], s["start"]), "start": hms(s["start"]), "end": hms(s["end"]),
                                    "minutes": mins, "verdict": s["verdict"], "verified": True, "block": s["block"], "score": s["score"], "coverage": s["coverage"],
                                    "relevance": s["relevance"], "sufficiency": s["sufficiency"], "clarity": s["clarity"], "level_fit": s["level_fit"],
                                    "evidence": s["evidence"][:3], "strengths": s["strengths"], "limitations": s["limitations"], "missing": s["missing"][:4],
                                    "source": s["source"], "checker": s["checker"]})
            clips.append({"target": c["title"], "target_ids": [c["id"]], "component": c["id"], "video": v["title"], "source": v.get("source"),
                          "url": _link(s["vid"], s["start"]), "start": hms(s["start"]), "end": hms(s["end"]), "minutes": mins, "component_minutes": c["minutes"],
                          "verdict": s["verdict"], "covered": s["covered"], "missing": s["missing"], "note": s.get("note", ""), "block": s["block"]})
        timeline.append(row)
    block_rows = []
    for k, b in enumerate(blocks, 1):
        ss = [path[i] for i in b]
        a, z = min(s["start"] for s in ss), max(s["end"] for s in ss)
        v = by_vid[ss[0]["vid"]]
        block_rows.append({"block": f"b{k}", "video": v["title"], "video_id": v["id"], "channel": v.get("source"), "url": _link(v["id"], a), "start": hms(a), "end": hms(z),
                           "minutes": round((z - a) / 60, 1), "parts": [comps[i]["id"] for i in b], "class_minutes": sum(comps[i]["minutes"] for i in b)})
    used: dict[str, list[dict]] = {}
    for s in path:
        if s is not None:
            used.setdefault(s["vid"], []).append(s)
    videos = sorted((video_item(by_vid[v], ss, title, lecture_min) for v, ss in used.items()), key=lambda x: (-x["scores"]["teaches"], -x["total"]))
    reserve_by: dict[str, list[dict]] = {}
    for s in plan["alternatives"]:
        if s["vid"] not in used:
            s["score"] = round(utility(s, by_vid[s["vid"]]) - 1, 3)
            reserve_by.setdefault(s["vid"], []).append(s)
    reserve = sorted((video_item(by_vid[v], ss, title, lecture_min) for v, ss in reserve_by.items()), key=lambda x: -x["total"])
    for i, x in enumerate(videos, 1):
        x["rank"], x["status"] = i, "proposed"
    for i, x in enumerate(reserve, len(videos) + 1):
        x["rank"], x["status"] = i, "reserve"
    # partly useful videos: not suggested to students, but NotebookLM can use them as sources
    src_ids = list(dict.fromkeys(f["vid"] for f in lec.partly if f["vid"] not in used and f["vid"] not in reserve_by))[:4]
    sources = [{k: by_vid[v].get(k) for k in ("kind", "id", "url", "title", "source", "description")} for v in src_ids]
    fails = [{"title": by_vid[s["vid"]]["title"], "url": _link(s["vid"], s["start"]), "why": [f"{s['cid'].split('.')[-1]}: {x}" for x in s["failed_gate"]]}
             for s in lec.tried if s["failed_gate"]][:15]
    fails += [{"title": by_vid[s["vid"]]["title"], "url": _link(s["vid"], s["start"]), "why": [f"{s['cid'].split('.')[-1]}: {s['dropped']}"]} for s in plan["dropped"]][:5]
    return {"timeline": timeline, "blocks": block_rows, "videos": videos, "reserve": reserve[:4], "clips": clips, "sources": sources,
            "rejected": fails + rejected[:15], "search": {"funnel": lec.funnel, "videos": list(lec.map.values())}}


def video_item(v: dict, segs: list[dict], title: dict, lecture_min: int) -> dict:
    """A video as the lecture file shows it: which parts it teaches, where, how much of each and the evidence."""
    segs = sorted(segs, key=lambda s: s["start"])
    taught = sum(min(s["end"] - s["start"], 60 * 30) / 60 for s in segs)
    best = max((s.get("score") or 0) for s in segs)
    clarity = sum(s["clarity"] for s in segs) / len(segs)
    level = sum(s["level_fit"] for s in segs) / len(segs)
    scores = {"teaches": round(min(1.0, taught / lecture_min), 3), "segment": round(min(1.0, best), 3), "clarity": round(clarity / 5, 3),
              "level_fit": round(level / 5, 3), "authority": rcfg()["tier_scores"][v.get("tier", 4)], "reception": reception(v),
              "match": round(sum(s["coverage"] for s in segs) / len(segs), 3)}
    total = round(0.75 * scores["segment"] + 0.15 * scores["reception"] + 0.10 * scores["teaches"], 3)
    parts = [f"{s['cid'].split('.')[-1]} {title.get(s['cid'], '')[:60]} ({hms(s['start'])}–{hms(s['end'])}, {round(100 * s['coverage'])}% of its points)" for s in segs]
    meta = [v.get("source") or "", f"tier {v.get('tier')}", hms(v.get("duration_s"))]
    if v.get("views"):
        meta.append(f"{v['views']:,} views")
    item = {k: v[k] for k in ("kind", "id", "url", "title", "source", "tier", "duration_s", "published", "licence", "captions",
                              "views", "likes", "comments", "subscribers", "transcript") if v.get(k) is not None}
    findings = [] if v.get("embeddable", True) else [{"code": "R-EMBED", "severity": "warning", "message": "video cannot be embedded in the course page (link only)"}]
    if v.get("evidence") == "notes":
        findings.append({"code": "R-NOTES", "severity": "warning", "message": "no captions: checked on AI notes of the video, so watch it before using it"})
    strengths = list(dict.fromkeys(x for s in segs for x in s["strengths"]))[:4]
    limits = list(dict.fromkeys(x for s in segs for x in s["limitations"]))[:4]
    item.update(scores=scores, total=total, findings=findings, strengths=strengths, limitations=limits,
                rationale="Teaches " + "; ".join(parts) + " [checked by a second AI on the " + ("notes of the video" if v.get("evidence") == "notes" else "transcript") + "] · " + " · ".join(m for m in meta if m),
                components=[{"id": s["cid"], "title": title.get(s["cid"], ""), "start": hms(s["start"]), "end": hms(s["end"]), "start_s": round(s["start"], 1), "end_s": round(s["end"], 1),
                             "verdict": s["verdict"], "coverage": s["coverage"], "covered": s["covered"], "missing": s["missing"], "evidence": s["evidence"], "note": s.get("note", ""),
                             "chapter": s.get("chapter"), "block": s.get("block")} for s in segs],
                coverage={"score": scores["match"], "evidence": v.get("evidence") or "transcript",
                          "per_target": {s["cid"]: {"text": title.get(s["cid"], ""), "covered": True, "sim": s["peak"],
                                                    "segments": [{"start": round(s["start"], 1), "end": round(s["end"], 1), "sim": s["peak"]}]} for s in segs}},
                review={"review": "; ".join(strengths)[:300], "issues": limits, "use_as": "in_class_clip", "explains": "explains"})
    if v.get("description"):
        item["description"] = v["description"][:700]
    return item
