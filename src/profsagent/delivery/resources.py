"""Learning-resource aid (architecture aids A3 + A4): videos, recorded lectures, readings, books, papers and practice.

Per lecture that asked for help:  discover → filter → cover (transcripts / page text) → AI review (D2) → score
→ hard checks → diversify → cap (+ reserve for replacements) → explain → clip playlists.
Retrieval only: nothing here is generated except search queries and review text; every link comes from a real record.
"""
from __future__ import annotations

import math
import re
from collections import defaultdict

from profsagent.delivery import checks
from profsagent.delivery.common import embed, hms, norm, rcfg, years_since
from profsagent.delivery.coverage import chunks_from_text, coverage, windows_from_transcript
from profsagent.delivery.models import QueryPlan, ResourceReviews
from profsagent.delivery.review import source_multiplier
from profsagent.delivery.sources import (OpenAlex, YouTube, grounded_pages, github_repos, links_in, page, transcript,
                                        transcripts_blocked)
from profsagent.llm.prompts import load_prompt
from profsagent.research.fetch import domain
from profsagent.research.resources import openlibrary

KIND_CAP = {"video": "videos", "recorded_lecture": "recorded_lecture", "reading": "readings", "practice": "practice"}


# ------------------------------------------------------------------ AI calls
def llm_call(llm, pid: str, ctx: dict, model_cls, run_id: str, log):
    p = load_prompt(pid)
    system, user = p.render(**ctx)
    obj, rec = llm.structured(system=system, user=user, model_cls=model_cls, role=p.meta.get("model_class", "generate"),
                              temperature=float(p.meta.get("temperature", 0.2)), prompt_id=pid, prompt_version=p.version, run_id=run_id)
    log(f"  [{pid}] ok via {rec.endpoint} · {rec.prompt_tokens}+{rec.output_tokens} tok")
    return obj


def plan_queries(llm, st: dict, briefs: dict, reqs: dict, run_id: str, log) -> dict:
    """One D1 call per batch of 6 lectures."""
    out = {}
    items = list(reqs.items())
    course = {"course_name": st["cco_compact"]["course_name"], "level": st.get("level"),
              "years": (st["cco_compact"].get("target_students") or {}).get("years")}
    for i in range(0, len(items), 6):
        batch = []
        for lid, want in items[i:i + 6]:
            b = briefs[lid]
            batch.append({"lecture_id": lid, "topic": b["topic"], "module": b["module"],
                          "learning_outcomes": [x["statement"] for x in b["learning_outcomes"]],
                          "wants": [k.replace("want_", "") for k, v in want.items() if k.startswith("want_") and v],
                          "professor_note": want.get("note") or ""})
        try:
            plan = llm_call(llm, "D1", {"course": course, "lectures": batch}, QueryPlan, run_id, log)
            for q in plan.lectures:
                out[q.lecture_id] = q.model_dump()
        except Exception as e:  # noqa: BLE001 — fall back to queries built from the brief
            log(f"  [D1] failed ({type(e).__name__}); using topic-based queries")
        for x in batch:
            out.setdefault(x["lecture_id"], fallback_queries(briefs[x["lecture_id"]]))
    return out


def fallback_queries(b: dict) -> dict:
    t = b["topic"]
    return {"lecture_id": b["lecture_id"], "video_queries": [f"{t} lecture", f"{t} explained"], "reading_queries": [f"{t} tutorial"],
            "practice_queries": [f"{t} exercises notebook"], "recorded_lecture_query": f"{t} university lecture",
            "research_queries": [t], "practitioner_query": f"{t} engineer talk"}


# ------------------------------------------------------------------ helpers
def tier_of_channel(name: str) -> int:
    c = rcfg()["channels"]
    n = (name or "").lower()
    for tier in (1, 2, 3):
        if any(x.lower() in n for x in c[f"tier{tier}"]):
            return tier
    return 4


def tier_of_domain(url: str, topic: str = "") -> int:
    d = domain(url)
    for tier in (1, 2, 3):
        if any(d == x or d.endswith("." + x) or (("/" in x) and x in url) for x in rcfg()["domains"][f"tier{tier}"]):
            return tier
    if d.startswith(("docs.", "developer.", "developers.", "learn.")) or d.endswith(".readthedocs.io") or "/docs/" in url:
        return 3                                    # official documentation
    stem = re.sub(r"[^a-z0-9]", "", d.split(".")[-2] if d.count(".") >= 1 else d)
    words = re.sub(r"[^a-z0-9]", "", (topic or "").lower())
    if len(stem) >= 6 and stem in words:            # the topic's own site, e.g. modelcontextprotocol.io
        return 3
    return 4


def clean_url(url: str) -> str:
    """Drop tracking parameters (utm_*, fbclid, ...) and empty fragments."""
    from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
    p = urlsplit(url)
    q = [(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True)
         if not k.lower().startswith(("utm_", "fbclid", "gclid", "mc_", "ref_src"))]
    frag = "" if p.fragment in ("", "0") else p.fragment
    return urlunsplit((p.scheme, p.netloc, p.path, urlencode(q), frag))


def blocked(url: str, title: str = "") -> str | None:
    bl = rcfg()["blocklist"]
    for d in bl["domains"] + (rcfg()["paywall_domains"] if rcfg().get("free_only") else []):
        if d.split("/")[0] in domain(url) and (("/" not in d) or d in url):
            return f"blocked or paywalled source ({d})"
    for t in bl["title_fragments"]:
        if t.lower() in (title or "").lower():
            return f"blocked title ({t})"
    return None


# ------------------------------------------------------------------ discovery per lecture
def discover(llm, b: dict, want: dict, q: dict, log) -> list[dict]:
    yt = YouTube()
    cands: list[dict] = []
    # videos and recorded lectures
    vids = {}
    if want.get("want_videos") or want.get("want_clips"):
        for query in q.get("video_queries", [])[: rcfg()["youtube"]["max_searches_per_lecture"]]:
            for v in yt.search(query):
                vids.setdefault(v, "video")
    if want.get("want_recorded_lecture") and q.get("recorded_lecture_query"):
        for v in yt.search(q["recorded_lecture_query"], long=True):
            vids[v] = "recorded_lecture"
    details = yt.videos(list(vids))
    chans = yt.channels([d["channel_id"] for d in details.values()])
    for vid, kind in vids.items():
        d = details.get(vid)
        if not d:
            continue
        if kind == "video" and (d["duration_s"] or 0) >= rcfg()["durations"]["recorded_lecture_min"] and want.get("want_recorded_lecture"):
            kind = "recorded_lecture"
        cands.append({**d, "kind": kind, "source": d["channel"], "tier": tier_of_channel(d["channel"]),
                      "subscribers": (chans.get(d["channel_id"]) or {}).get("subscribers"), "free": True})
    # readings: web pages (grounded search), books, survey papers
    dom = [x for t in (1, 2, 3) for x in rcfg()["domains"][f"tier{t}"]]
    if want.get("want_readings"):
        for query in q.get("reading_queries", [])[:1]:   # web search is the scarcest quota: one query per lecture
            for p in grounded_pages(llm, query, dom, "readings (tutorials, lecture notes, book chapters, documentation)"):
                cands.append({"kind": "reading", "url": p["url"], "title": p.get("title") or "", "page_type": p.get("type"), "redirect": p.get("redirect")})
        for bk in openlibrary(b["topic"], 3):
            cands.append({"kind": "reading", "page_type": "book", "url": bk["url"], "title": bk["title"], "authors": bk.get("authors", []),
                          "year": bk.get("year"), "identifier": bk.get("identifier"), "source": "OpenLibrary", "tier": 2, "record": bk})
        for w in OpenAlex().works(b["topic"], n=10, min_year=2015, review_only=True)[:4]:
            if w.get("open_access") and w.get("oa_url"):
                cands.append({"kind": "reading", "page_type": "survey paper", "url": w["oa_url"], "title": w["title"],
                              "year": w["year"], "cited_by": w["cited_by"], "source": w.get("venue") or "OpenAlex",
                              "authors": [a["name"] for a in w["authors"][:4]], "doi": w.get("doi")})
    # practice: notebooks, exercises, repos
    if want.get("want_practice"):
        for query in q.get("practice_queries", [])[:1]:
            for p in grounded_pages(llm, query, dom, "practice material (exercises, notebooks, labs, datasets)"):
                cands.append({"kind": "practice", "url": p["url"], "title": p.get("title") or "", "page_type": p.get("type"), "redirect": p.get("redirect")})
            for r in github_repos(f"{query} in:name,description,readme", 5):
                if r["stars"] >= 50:
                    cands.append({"kind": "practice", "page_type": "repository", "url": r["url"], "title": f"{r['name']} — {r['description'][:120]}",
                                  "source": "GitHub", "tier": 3, "stars": r["stars"], "updated": r["updated"], "licence": r["licence"]})
    if want.get("want_readings") or want.get("want_practice"):
        # links the video creators give in their descriptions: docs, posts, repos (no search quota needed)
        best = sorted((c for c in cands if c["kind"] in ("video", "recorded_lecture")), key=lambda c: -(c.get("views") or 0))[:8]
        for c in best:
            for u in links_in(c.get("description", ""))[:4]:
                kind = "practice" if ("github.com" in u or "colab.research" in u) and want.get("want_practice") else "reading"
                if kind == "reading" and not want.get("want_readings"):
                    continue
                cands.append({"kind": kind, "url": u, "title": "", "page_type": "linked by video", "via": c["title"][:80]})
    log(f"  {b['lecture_id']}: {len(cands)} raw candidates "
        f"({sum(c['kind'] in ('video', 'recorded_lecture') for c in cands)} videos)")
    return cands


def enrich(cands: list[dict], b: dict, log) -> list[dict]:
    """Fetch pages, attach coverage; fetch transcripts for the best-looking videos only."""
    targets = b["targets"]
    out, seen = [], set()
    tv = embed([t["text"] for t in targets])
    # pre-score videos by title/description similarity so transcripts are fetched for the promising ones
    vids = [c for c in cands if c["kind"] in ("video", "recorded_lecture")]
    if vids:
        vv = embed([f"{c['title']}. {c['description'][:400]}" for c in vids])
        for c, v in zip(vids, vv):
            c["_pre"] = float((tv @ v).max()) + 0.1 * (5 - c["tier"]) / 4
        for c in sorted(vids, key=lambda c: -c["_pre"])[: rcfg()["transcripts"]["max_per_lecture"]]:
            c["_fetch_transcript"] = True
    for c in cands:
        if c["kind"] in ("video", "recorded_lecture"):
            key = c["id"]
            if key in seen:
                continue
            seen.add(key)
            tr = transcript(c["id"]) if c.get("_fetch_transcript") else None
            if c.get("_fetch_transcript") and not tr and transcripts_blocked():
                c["_tx_missing"] = True
            if tr:
                c["coverage"] = coverage(windows_from_transcript(tr), targets)
            else:   # metadata only (title, description, chapter markers): weaker evidence, never gives timestamps
                c["coverage"] = coverage(chunks_from_text(f"{c['title']}. {c['description']}", 60), targets)
                c["coverage"]["evidence"] = "metadata"
            c["transcript"] = bool(tr)
            if tr:
                c["captions"] = True     # a downloadable transcript means captions exist (auto-generated ones included)
        else:
            if c.get("page_type") == "book":
                c["coverage"] = coverage([{"start": None, "end": None, "text": c["title"]}], targets)
                c["coverage"]["evidence"] = "title"
            else:
                pg = page(c["url"])
                if pg.get("status") != 200 or len((pg.get("text") or "").split()) < 150:
                    c["dead"] = f"page not readable (status {pg.get('status')}, {pg.get('error') or 'too short'})"
                else:
                    c["url"] = clean_url(pg.get("final_url") or c["url"])
                    t = (c.get("title") or "").strip()
                    if not t or (" " not in t and "." in t):          # search gave a domain ("amazon.com"), not a title
                        t = (pg.get("title") or "").strip() or c["url"]
                    c["title"] = t
                    c["coverage"] = coverage(chunks_from_text(pg["text"]), targets)
                    c["words"] = len(pg["text"].split())
            key = c["url"].split("#")[0].rstrip("/")
            if key in seen:
                continue
            seen.add(key)
            c.setdefault("source", domain(c["url"]))
            c.setdefault("tier", tier_of_domain(c["url"], b["topic"]))
        why = blocked(c.get("url", ""), c.get("title", ""))
        if why:
            c["dead"] = why
        out.append(c)
    return out


# ------------------------------------------------------------------ scoring
def reception(c: dict) -> float:
    if c["kind"] in ("video", "recorded_lecture"):
        yrs = max(years_since(c.get("published")) or 1.0, 0.25)
        v = c.get("views") or 0
        per_year = min(math.log10(v / yrs + 1) / 6, 1.0)
        like = min(((c.get("likes") or 0) / v) / 0.04, 1.0) if v and c.get("likes") is not None else 0.5
        return round(0.5 * per_year + 0.5 * like, 3)
    if c.get("cited_by") is not None:
        return round(min(math.log10(c["cited_by"] + 1) / 3, 1.0), 3)
    if c.get("stars") is not None:
        return round(min(math.log10(c["stars"] + 1) / 4, 1.0), 3)
    return 0.5


def practicality(c: dict, b: dict) -> float:
    s, n = 0.0, 0
    d = rcfg()["durations"]
    if c["kind"] == "video":
        dur = c.get("duration_s") or 0
        s += 1.0 if dur <= d["clip_max"] else 0.7 if dur <= d["video_max"] else 0.3
        n += 1
        s += 1.0 if c.get("captions") else 0.5
        n += 1
    elif c["kind"] == "recorded_lecture":
        dur = c.get("duration_s") or 0
        s += 1.0 if d["recorded_lecture_min"] <= dur <= 2 * d["video_max"] else 0.5
        n += 1
        s += 1.0 if c.get("captions") else 0.5
        n += 1
    if "Creative Commons" in str(c.get("licence")) or c.get("licence") in ("MIT", "Apache-2.0", "CC-BY-4.0"):
        s += 1.0
        n += 1
    yrs = years_since(c.get("published") or c.get("updated")) if (c.get("published") or c.get("updated")) else (
        (2026 - c["year"]) if c.get("year") else None)
    if yrs is not None and b.get("novel"):
        s += 1.0 if yrs <= rcfg()["recency_years_fast_topics"] else 0.4
        n += 1
    return round(s / n, 3) if n else 0.6


def quality(c: dict) -> tuple[float, float]:
    r = c.get("review")
    if not r:
        return 0.5, 0.6
    q = (r["clarity"] + r["correctness"] + r["depth"] + r["examples"]) / 20
    if r["explains"] == "mentions":
        q *= 0.6
    elif r["explains"] == "off_topic":
        q = 0.0
    return round(q, 3), round(r["level_fit"] / 5, 3)


def score(c: dict, b: dict) -> None:
    w = rcfg()["weights"]
    q, lvl = quality(c)
    cov = c.get("coverage", {})
    cred = {"transcript": 1.0, "text": 1.0, "metadata": 0.7, "title": 0.6}.get(cov.get("evidence"), 0.6)
    s = {"coverage": round(cov.get("score", 0.0) * cred, 3), "quality": q,
         "authority": rcfg()["tier_scores"][c.get("tier", 4)], "level_fit": lvl,
         "reception": reception(c), "practicality": practicality(c, b)}
    c["scores"] = {k: round(v, 3) for k, v in s.items()}
    mult = source_multiplier(c.get("source"))            # professors' and students' ratings of this source (neutral if none)
    c["total"] = round(min(1.0, sum(w[k] * s[k] for k in w) * mult), 3)
    if mult != 1.0:
        c["feedback_multiplier"] = mult


def site(c: dict) -> str:
    """modelcontextprotocol.io and modelcontextprotocol.info are the same source (official site vs mirror)."""
    src = (c.get("source") or "").lower()
    parts = src.split(".")
    return parts[-2] if len(parts) >= 2 else src


def mentions_only(c: dict) -> bool:
    return (c.get("review") or {}).get("explains") == "mentions"


def diversify(cands: list[dict], k: int) -> list[dict]:
    """Greedy MMR: penalise a second item from the same channel/site and near-duplicate titles."""
    pool = sorted(cands, key=lambda c: -c["total"])
    picked: list[dict] = []
    tv = {id(c): v for c, v in zip(pool, embed([c["title"] for c in pool]))} if pool else {}
    while pool and len(picked) < k:
        def adj(c):
            pen = 0.08 * sum(1 for p in picked if (p.get("source") or "").lower() == (c.get("source") or "").lower())
            if c["kind"] in ("reading", "practice") and any(site(p) == site(c) and p["kind"] == c["kind"] for p in picked):
                pen += 0.25
            if picked:
                pen += 0.15 * max(float(tv[id(c)] @ tv[id(p)]) > 0.85 for p in picked)
            if mentions_only(c):           # AI review: names the topic but does not teach it
                pen += 0.12
            return c["total"] - pen
        best = max(pool, key=adj)
        picked.append(best)
        pool.remove(best)
    return picked


# ------------------------------------------------------------------ per-lecture run
def review(llm, b: dict, want: dict, cands: list[dict], st: dict, run_id: str, log) -> None:
    """AI checklist (D2) on the items that would be shown: per kind, the provisional top (cap + 2) by score.
    When the topic continues in the next lecture, a second call reviews the next-best items too, since that
    lecture is given them."""
    caps = rcfg()["caps"]
    alive = [c for c in cands if not c.get("dead")]
    for c in alive:
        score(c, b)
    n = rcfg()["review"]["max_candidates_per_call"] + 2
    first, nxt = [], []
    for kind, capkey in KIND_CAP.items():
        pool = sorted((c for c in alive if c["kind"] == kind), key=lambda c: -c["total"])
        first += pool[: caps[capkey] + 2]
        nxt += pool[caps[capkey] + 2: 2 * caps[capkey] + 4]
    first = sorted(first, key=lambda c: -c["total"])[:n]
    _review_batch(llm, b, want, first, st, run_id, log)
    if b.get("continues"):
        rest = [c for c in sorted(nxt, key=lambda c: -c["total"]) if c not in first and c["total"] >= caps.get("min_continuation_score", 0)]
        _review_batch(llm, b, want, rest[:n], st, run_id, log)


def _review_batch(llm, b: dict, want: dict, top: list[dict], st: dict, run_id: str, log) -> None:
    if not top:
        return
    for i, c in enumerate(top):
        c["_rid"] = f"r{i + 1}"
    ctx = {"lecture": {"lecture_id": b["lecture_id"], "topic": b["topic"], "learning_outcomes": [x["statement"] for x in b["learning_outcomes"]],
                       "course_level": st.get("level"), "professor_note": want.get("note") or ""},
           "candidates": [{"id": c["_rid"], "kind": c["kind"], "page_type": c.get("page_type"), "url": c.get("url"),
                           "title": c["title"], "source": c.get("source"),
                           "duration": hms(c.get("duration_s")) if c.get("duration_s") else None, "year": c.get("year") or (c.get("published") or "")[:4],
                           "coverage": {t["text"][:80]: v["covered"] for t, v in zip(b["targets"], c.get("coverage", {}).get("per_target", {}).values())},
                           "excerpts": [e[:450] for e in c.get("coverage", {}).get("best_excerpts", [])]} for c in top]}
    try:
        res = llm_call(llm, "D2", ctx, ResourceReviews, run_id, log)
        by = {r.id: r.model_dump() for r in res.reviews}
        for c in top:
            if c["_rid"] in by:
                c["review"] = by[c["_rid"]]
    except Exception as e:  # noqa: BLE001 — unreviewed items get a neutral quality score and a note
        log(f"  [D2] failed for {b['lecture_id']} ({type(e).__name__}); quality left neutral")


def explain(c: dict, b: dict) -> str:
    per = c.get("coverage", {}).get("per_target", {})
    parts = []
    for t in b["targets"]:
        v = per.get(t["id"])
        if not v:
            continue
        seg = v["segments"][0] if v.get("segments") else None
        label = "topic" if t["kind"] == "topic" else t["id"]
        parts.append(f"{label} {'✓' if v['covered'] else '✗'}" + (f" ({hms(seg['start'])}–{hms(seg['end'])})" if seg else ""))
    meta = [c.get("source") or "", f"tier {c.get('tier')}"]
    if c.get("duration_s"):
        meta.append(hms(c["duration_s"]))
    if c.get("views"):
        meta.append(f"{c['views']:,} views")
    if c.get("captions"):
        meta.append("captions")
    ev = {"transcript": "from transcript", "metadata": "from title/description only", "text": "from page text", "title": "from title only"}
    return f"Covers: {', '.join(parts)} [{ev.get(c.get('coverage', {}).get('evidence'), '')}] · " + " · ".join(m for m in meta if m)


def clip_playlist(items: list[dict], b: dict) -> list[dict]:
    """Best segment per target across the lecture's videos: the minutes to watch, in lecture order."""
    out = []
    for t in b["targets"]:
        best = None
        for c in items:
            v = c.get("coverage", {}).get("per_target", {}).get(t["id"])
            for s in (v or {}).get("segments", []):
                if best is None or s["sim"] > best[1]["sim"]:
                    best = (c, s)
        if best:
            c, s = best
            prev = next((o for o in out if o["_vid"] == c["id"] and s["start"] <= o["_end"] and s["end"] >= o["_start"]), None)
            if prev:                                    # same stretch of the same video teaches both: one clip
                prev["_start"], prev["_end"] = min(prev["_start"], s["start"]), max(prev["_end"], s["end"])
                prev["target"] += f" + {t['text']}"
                prev["target_ids"].append(t["id"])
                continue
            out.append({"target": t["text"], "target_ids": [t["id"]], "video": c["title"], "source": c.get("source"),
                        "_vid": c["id"], "_start": s["start"], "_end": s["end"]})
    for o in out:
        o.update(url=f"https://www.youtube.com/watch?v={o['_vid']}&t={int(o['_start'])}s", start=hms(o["_start"]), end=hms(o["_end"]),
                 minutes=round((o["_end"] - o["_start"]) / 60, 1))
        for k in ("_vid", "_start", "_end"):
            o.pop(k)
    return out


def recommend_lecture(llm, st: dict, b: dict, want: dict, q: dict, run_id: str, log) -> dict:
    cands = discover(llm, b, want, q, log)
    cands = enrich(cands, b, log)
    review(llm, b, want, cands, st, run_id, log)
    for c in cands:
        score(c, b)
        c["findings"] = checks.resource(c, b)
    ok = [c for c in cands if not any(f["severity"] == "error" for f in c["findings"])]
    caps = rcfg()["caps"]
    # videos that may be shown (or used for a continuation) but were judged from metadata: fetch their transcript too
    for kind, capkey in KIND_CAP.items():
        if kind not in ("video", "recorded_lecture"):
            continue
        for c in sorted((c for c in ok if c["kind"] == kind), key=lambda c: -c["total"])[: caps[capkey] + caps["reserve"]]:
            if not c.get("transcript"):
                tr = transcript(c["id"])
                if not tr and transcripts_blocked():
                    c["_tx_missing"] = True
                if tr:
                    c["coverage"], c["transcript"], c["captions"] = coverage(windows_from_transcript(tr), b["targets"]), True, True
                    score(c, b)
                    c["findings"] = checks.resource(c, b)
    ok = [c for c in ok if not any(f["severity"] == "error" for f in c["findings"])]
    floor = caps.get("min_show_score", 0)
    for c in ok:
        if c["total"] < floor:
            c["findings"].append(checks.f("R-FLOOR", "error", f"score {c['total']:.2f} is below the quality floor {floor}"))
    ok = [c for c in ok if c["total"] >= floor]
    rejected = [c for c in cands if c not in ok]
    out = {"lecture_id": b["lecture_id"], "topic": b["topic"], "want": want, "queries": q, "items": {}, "reserve": {},
           "rejected": [{"title": c.get("title"), "url": c.get("url"), "why": [f["message"] for f in c["findings"] if f["severity"] == "error"]}
                        for c in rejected][:30]}
    for kind, capkey in KIND_CAP.items():
        pool = [c for c in ok if c["kind"] == kind]
        if not pool:
            continue
        ranked = diversify(pool, caps[capkey] + caps["reserve"])
        # shown items: those that teach the topic come before those that only mention it, then by score
        ranked = sorted(ranked[: caps[capkey]], key=lambda c: (mentions_only(c), -c["total"])) + ranked[caps[capkey]:]
        for i, c in enumerate(ranked, 1):
            c["rank"] = i
            c["rationale"] = explain(c, b)
            c["status"] = "proposed" if i <= caps[capkey] else "reserve"
        out["items"][kind] = [slim(c) for c in ranked[: caps[capkey]]]
        out["reserve"][kind] = [slim(c) for c in ranked[caps[capkey]:]]
    vids = [c for c in ok if c["kind"] in ("video", "recorded_lecture")]
    if want.get("want_clips"):
        out["clips"] = clip_playlist(vids, b)
    out["counts"] = {"candidates": len(cands), "passed_checks": len(ok), "rejected": len(rejected)}
    missing = [c["id"] for c in cands if c.get("_tx_missing") and not c.get("transcript")]
    if missing:   # videos judged from title and description only: the next plain run redoes this lecture
        out["partial"] = {"reason": f"YouTube blocked transcript requests (from {transcripts_blocked()})",
                          "videos_without_transcript": missing}
    return out


def slim(c: dict) -> dict:
    keep = ("kind", "id", "url", "title", "source", "tier", "page_type", "duration_s", "published", "year", "licence", "captions",
            "views", "likes", "comments", "subscribers", "authors", "doi", "identifier", "cited_by", "stars", "transcript",
            "scores", "total", "rank", "status", "rationale", "findings")
    out = {k: c[k] for k in keep if k in c and c[k] is not None}
    if c.get("description"):
        out["description"] = c["description"][:700]      # used to find speakers of talks and the links creators give
    if c.get("review"):
        out["review"] = {k: c["review"][k] for k in ("review", "issues", "use_as", "explains", "clarity", "correctness", "depth", "examples", "level_fit")}
    cov = c.get("coverage") or {}
    out["coverage"] = {"score": cov.get("score"), "evidence": cov.get("evidence"),
                       "per_target": {k: {"covered": v["covered"], "sim": v["sim"], "segments": v["segments"]} for k, v in cov.get("per_target", {}).items()}}
    out["title"] = norm(out.get("title", ""))
    return out
