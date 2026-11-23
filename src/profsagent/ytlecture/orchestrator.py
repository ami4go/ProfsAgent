"""The orchestrator: runs delivery mode 2 for a set of lectures, topic by topic, as a fixed sequence of stages. Each stage's
result is checkpointed, so an interrupted run (quota, a YouTube block) resumes where it stopped.

  per topic (all lectures of one schedule topic are planned together, so later lectures continue the earlier ones)
    1 PLAN        Y1 planner → parts with minutes and must-cover points per lecture                  (METHODS §1)
    2 SCOUT       web searches "who teaches this" → Y2 scout → authorities, course pages, part queries (METHODS §2)
    3 SEARCH      round 1: YouTube API (authority + part queries), Tavily[youtube.com], DuckDuckGo
                  videos, SerpApi YouTube, the topic's lecture playlists, course-page links
                  round 2: channel expansion (search inside the channels that recur or are authorities)
    4 FILTER      metadata rules (length, language, region, embeddable, hype titles, duplicates, recency)  (§3)
  per lecture
    5 TRIAGE      local-embedding pre-rank → Y3 triage → shortlist                                     (§4)
    6 EVIDENCE    chapters → captions → browser transcript panel → Gemini notes                       (§4)
    7 READ        Y4 skim (long videos) → Y5 zoom: exact clips with quotes; code checks quotes and snaps   (§5)
    8 VERIFY      Y6, a different model, per clip: points taught, standalone, accurate             (§6)
    9 ASSEMBLE    code: score, gate, choose 1-2 clips per part in teaching order, fit the slot          (§7)
   10 GAPS        Y7 for parts still empty → one more search/read/verify round → assemble again
   11 REPORT      lecture JSON, playlists for the player, PLAYLISTS.md, TRACE.md (the run's own methods log)
"""
from __future__ import annotations

import json
import re
import threading
import time
from pathlib import Path

import numpy as np

from profsagent.delivery.brief import build_briefs
from profsagent.delivery.common import embed, load_state, out_dir, read_json, write_json
from profsagent.ytlecture import agents as A
from profsagent.ytlecture import evidence as E
from profsagent.ytlecture import innertube as IT
from profsagent.ytlecture import shortlist as SL
from profsagent.ytlecture import tools as T
from profsagent.ytlecture import txshort as TX
from profsagent.ytlecture.assemble import choose
from profsagent.ytlecture.tools import Budget, Trace, cfg


_EMB = SL._EMB      # one lock for the shared embedding model (shortlist.py uses it too)


def _embed(texts: list[str]):
    """The local embedding model, one caller at a time (readers run in threads)."""
    with _EMB:
        return embed(texts)


_STOP = set("a an the and or of for to in on with using use how what why vs versus explained explanation tutorial intro "
             "introduction guide example examples basics step by from your you is are into its it part lecture course build "
             "building".split())


def core_term(phrases: list[str]) -> str:
    """The two most frequent content words of a topic's search phrases, in their original spelling."""
    from collections import Counter
    c, first = Counter(), {}
    for p in phrases:
        for w in dict.fromkeys(re.findall(r"[A-Za-z0-9+#.-]+", p)):
            k = w.lower()
            if k not in _STOP and len(k) >= 2:
                c[k] += 1
                first.setdefault(k, w)
    return " ".join(first[w] for w, _ in c.most_common(2))


def _bloom(n) -> str:
    return {1: "remember", 2: "understand", 3: "apply", 4: "analyse", 5: "evaluate", 6: "create"}.get(n, "?")


class Orchestrator:
    def __init__(self, run_id: str, log=print, refresh: bool = False, redo_lectures: bool = False, redo_search: bool = False):
        from profsagent.llm.client import LLMClient
        self.run_id = run_id
        self.log = log
        self.refresh = refresh
        self._checkpoint = None                 # saves the current topic's checkpoint (set per topic)
        self.redo_lectures = redo_lectures or redo_search  # keep plan, scout and search; redo triage onwards
        self.redo_search = redo_search          # keep plan and scout; search again (18 Nov: to measure a new search)
        self.st = load_state(run_id)
        self.dir = out_dir(run_id) / "ytlecture"
        (self.dir / "state").mkdir(parents=True, exist_ok=True)
        (self.dir / "lectures").mkdir(exist_ok=True)
        self.llm = LLMClient(self.dir / "llm_calls.jsonl")
        self.trace = Trace()
        old = read_json(self.dir / "trace.jsonl.json") or []
        self.trace.rows = [] if refresh else old
        bp = out_dir(run_id) / "briefs.json"
        self.briefs = read_json(bp) or build_briefs(self.st)
        f = self.st.get("form") or {}
        self.course = {"name": f.get("1. COURSE NAME") or "", "description": (self.st.get("narrative") or {}).get("course_description")
                       or f.get("2. SHORT COURSE DESCRIPTION", ""), "students": f.get("5. TARGET STUDENTS", "")[:400]}

    # ------------------------------------------------------------ checkpoints
    def _ck(self, tid: str) -> dict:
        p = self.dir / "state" / f"{tid}.json"
        return {} if self.refresh else (read_json(p) or {})

    def _save(self, tid: str, ck: dict) -> None:
        write_json(self.dir / "state" / f"{tid}.json", ck)
        write_json(self.dir / "trace.jsonl.json", self.trace.rows)

    # ------------------------------------------------------------ entry point
    def run(self, lectures: list[str] | None = None) -> dict:
        want = [b for b in self.briefs if not lectures or b["lecture_id"] in lectures]
        topics = list(dict.fromkeys(b["topic_id"] for b in want))
        if self.redo_lectures:   # 17 Nov audit: TRACE.md mixed the old and new rows of a redone lecture
            ids = {b["lecture_id"] for b in want}
            self.trace.rows = [r for r in self.trace.rows if str(r.get("scope", "")).split("/")[0] not in ids]
        self.log(f"ytlecture {self.run_id}: {len(want)} lectures in {len(topics)} topics · YouTube units used today {T.yt().quota.used()}")
        results = {}
        try:
            for tid in topics:
                group = [b for b in self.briefs if b["topic_id"] == tid]
                todo = [b["lecture_id"] for b in want if b["topic_id"] == tid]
                results.update(self.topic(tid, group, todo))
        finally:
            E.close_browser()
            write_json(self.dir / "trace.jsonl.json", self.trace.rows)
        from profsagent.ytlecture.report import write_all
        return write_all(self.run_id, self.dir, self.trace)

    # ------------------------------------------------------------ re-assembly only (no AI, no search)
    def reassemble(self, lectures: list[str] | None = None) -> dict:
        """Recompute every finished lecture's playlist from its stored clips and checks: free, used after a change to the
        scoring, gate or selection rules. Lectures go in timetable order across all topics, each avoiding the clips that
        earlier lectures use (17 Nov audit: topic by topic, a later lecture could keep a clip an earlier one needed)."""
        from profsagent.ytlecture.report import lecture_json, write_all
        cks = {p.stem: read_json(p) or {} for p in sorted((self.dir / "state").glob("M*.json")) if not p.stem.endswith(".bak")}
        where = {lp["lecture_id"]: (tid, lp) for tid, ck in cks.items() for lp in ((ck.get("plan") or {}).get("lectures") or [])}
        for ck in cks.values():
            for v in (ck.get("candidates") or {}).values():
                v["tier"] = T.tier(v.get("channel", ""))
        taken: list[dict] = []
        touched = set()
        for b in self.briefs:
            lid = b["lecture_id"]
            if lid not in where:
                continue
            tid, lp = where[lid]
            ck = cks[tid]
            lck = (ck.get("lectures") or {}).get(lid) or {}
            if not lck.get("clips") and not lck.get("assembly"):
                continue
            if lectures is None or lid in lectures:
                cands, fast = ck.get("candidates") or {}, bool(ck["plan"]["fast_moving"])
                reserved = self.reserved_for_later(tid, cks)
                clips = [k for k in lck["clips"] if k["video"] not in reserved]
                videos = {k: cands[k] for k in {c["video"] for c in clips} if k in cands}
                lck["assembly"] = choose(lp, clips, videos, fast, taken)
                topic = {"id": tid, "title": b["topic"], "module": b.get("module")}
                write_json(self.dir / "lectures" / f"{lid}.json", lecture_json(self.run_id, topic, lp, b, lck, cands, {}, fast))
                self.log(f"{lid}: {lck['assembly']['status']} · video {round(lck['assembly']['total_s'] / 60)} of {lp['slot_minutes']} min")
                touched.add(tid)
            for pp in (lck.get("assembly") or {}).get("plan", []):
                taken += pp["clips"]
        for tid in touched:                  # topics not asked for are left untouched (another run may be writing them)
            write_json(self.dir / "state" / f"{tid}.json", cks[tid])
        return write_all(self.run_id, self.dir, self.trace)

    # ------------------------------------------------------------ one topic
    def topic(self, tid: str, group: list[dict], todo: list[str]) -> dict:
        ck = self._ck(tid)
        tr, scope = self.trace, tid
        b0 = group[0]
        topic = {"id": tid, "title": b0["topic"], "module": b0.get("module"), "novel": b0.get("novel")}
        lectures = [{"lecture_id": b["lecture_id"], "slot_minutes": round(b["hours"] * 60), "hands_on": b.get("hands_on"),
                     "labs": b.get("labs"), "learning_outcomes": [{"statement": re.sub(r"\{n\} of \{m\}", "most", lo["statement"]),
                                                                   "bloom": _bloom(lo.get("bloom_level"))} for lo in b["learning_outcomes"]]}
                    for b in group]
        self.log(f"topic {tid} · {topic['title']} · lectures {', '.join(l['lecture_id'] for l in lectures)}")
        course = {**self.course, "prerequisites": b0.get("prerequisite_courses")}

        # 1 PLAN
        if "plan" not in ck:
            earlier = [x["topic"] for x in b0.get("builds_on", [])]
            later = [x["topic"] for x in group[-1].get("leads_to", [])]
            ck["plan"] = A.plan_topic(self.llm, course, topic, lectures, earlier, later, tr, self.run_id)
            tr.step(scope, "planned parts", lectures={l["lecture_id"]: [p["title"] for p in l["parts"]] for l in ck["plan"]["lectures"]})
            self._save(tid, ck)
        plan = ck["plan"]
        fast = bool(plan["fast_moving"])
        for l in plan["lectures"]:
            self.log(f"  plan {l['lecture_id']}: " + " | ".join(f"{p['title']} ({p['minutes']}m)" for p in l["parts"]))

        # 2 SCOUT
        if "scout" not in ck:
            s = cfg()["search"]
            qs = [f"{topic['title']} university course lecture videos", f"{topic['title']} lecture youtube",
                  f"{topic['title']} explained talk by creator OR author", f"best course to learn {topic['title']}"][: s["scout_web_queries"]]
            results = []
            for q in qs:
                results += [{"url": r["url"], "title": r["title"], "content": r["content"][:400]} for r in T.web(q, tr, scope)]
            ck["scout"] = A.scout(self.llm, topic, plan, results, tr, self.run_id)
            tr.step(scope, "authorities found", authorities=[f"{a['name']} ({a['kind']}, {a['evidence']})" for a in ck["scout"]["authorities"]],
                    course_pages=ck["scout"]["course_pages"])
            self._save(tid, ck)
        sc = ck["scout"]
        self.log(f"  authorities: {', '.join(a['name'] for a in sc['authorities'])}")

        # 3 SEARCH + 4 FILTER. Topic-level searches once; per-lecture searches only for the lectures asked for. A search
        # stage cut short by the YouTube quota is not marked done, so the next run repeats it (cached queries are free).
        if "candidates" in ck and "searched" not in ck:          # checkpoints from before per-lecture searching
            ck["searched"] = ["topic"] + [l["lecture_id"] for l in plan["lectures"]]
        if self.redo_search and not getattr(self, "_research_done", set()) >= {tid}:
            # keep only the candidates that lectures NOT being redone still use (their clips must keep their videos)
            keepv = {v for lid, l in (ck.get("lectures") or {}).items() if lid not in todo
                     for v in set(l.get("read", [])) | {k["video"] for k in l.get("clips", [])}}
            ck["candidates"] = {v: x for v, x in (ck.get("candidates") or {}).items() if v in keepv}
            ck["searched"] = []
            self._research_done = getattr(self, "_research_done", set()) | {tid}
        searched = ck.setdefault("searched", [])
        need = [l for l in plan["lectures"] if l["lecture_id"] in todo and l["lecture_id"] not in searched]
        if "topic" not in searched or need:
            new, complete = self.search(topic, plan, sc, tr, need, "topic" not in searched)
            merged = ck.get("candidates") or {}
            for vid, v in new.items():
                if vid in merged:
                    merged[vid]["parts"] = sorted(set(merged[vid].get("parts", [])) | set(v["parts"]))
                    merged[vid]["found_by"] = (merged[vid].get("found_by", []) + v["found_by"])[:8]
                else:
                    merged[vid] = v
            ck["candidates"] = merged
            if complete:
                ck["searched"] = list(dict.fromkeys(searched + ["topic"] + [l["lecture_id"] for l in need]))
            else:
                self.log("  ! YouTube quota ran out during the search: the next run repeats the skipped searches")
                tr.step(scope, "search incomplete (YouTube quota); will be repeated next run")
            self._save(tid, ck)
        cands = ck["candidates"]
        for v in cands.values():                 # tiers are recomputed: the lists change between runs (stored ones go stale)
            v["tier"] = T.tier(v.get("channel", ""))
        own = cands
        cands = self.with_course_pool(tid, own, fast)
        self._reserved = self.reserved_for_later(tid)

        def keep_used(lck: dict) -> None:
            """Videos read for this topic (course-pool or gap-round ones too) are saved with its checkpoint, so re-assembly
            and the report find every clip's video."""
            for vid in set(lck.get("read", [])) | {k["video"] for k in lck.get("clips", [])}:
                if vid in cands and vid not in own:
                    own[vid] = cands[vid]

        out = {}
        taken: list[dict] = []                   # this topic's earlier lectures; other topics' are added per lecture

        def checkpoint():
            for x in (ck.get("lectures") or {}).values():
                keep_used(x)
            self._save(tid, ck)
        self._checkpoint = checkpoint
        self._level = plan.get("level_note", "")
        for lp in plan["lectures"]:
            lid = lp["lecture_id"]
            lck = ck.setdefault("lectures", {}).setdefault(lid, {})
            if lid in todo and self.redo_lectures:
                lck.clear()
            if lid not in todo:
                for pp in (lck.get("assembly") or {}).get("plan", []):
                    taken += pp["clips"]
                continue
            res = self.lecture(topic, lp, cands, fast, sc, taken + self.taken_elsewhere(tid, before=lid), lck, tr)
            keep_used(lck)
            self._save(tid, ck)
            for pp in res["assembly"]["plan"]:
                taken += pp["clips"]
            out[lid] = res
        return out

    # ------------------------------------------------------------ search helpers: free first, the API as the fallback
    @staticmethod
    def video_search(q: str, tr: Trace, scope: str, long: bool = False, n: int | None = None) -> list[dict]:
        """Videos for a query: the free InnerTube search (18 Nov: as good as the API, no quota), else the YouTube API."""
        if IT.available():
            got = IT.search(q, tr, scope, duration="long" if long else None, n=n or 20)
            if got:
                return got
        return T.yt_search(q, tr, scope, long=long, n=n)

    @staticmethod
    def playlist_search(q: str, tr: Trace, scope: str) -> list[dict]:
        if IT.available():
            got = IT.search(q, tr, scope, kind="playlist", n=10)
            if got:
                return got
        return T.yt_search(q, tr, scope, n=10, kind="playlist")

    # ------------------------------------------------------------ search (round 1 + round 2) and filter
    def search(self, topic: dict, plan: dict, sc: dict, tr: Trace, lectures: list[dict], topic_level: bool) -> tuple[dict, bool]:
        """(filtered candidates found now, complete). complete=False when a YouTube search was skipped for quota."""
        s = cfg()["search"]
        scope = topic["id"]
        found: dict[str, dict] = {}
        skipped0 = sum(1 for r in tr.rows if r["kind"] == "tool" and str(r.get("note", "")).startswith("skipped: no YouTube"))

        def add(ids, how, lid=None, part=None):
            for v in ids:
                f = found.setdefault(v, {"how": [], "parts": []})
                f["how"].append(how)
                if lid is not None:
                    f["parts"].append(f"{lid}#{part}")

        # topic level: authorities (YouTube API), the topic's lecture playlists, course pages
        free = IT.available()
        n_auth = s.get("authority_queries_free", 8) if free else 4
        for a in (sc["authorities"][:n_auth] if topic_level else []):
            add([x["id"] for x in self.video_search(a["query"], tr, scope)], f"youtube: {a['query']}")
        for pl in (self.playlist_search(f"{topic['title']} lecture course", tr, scope)[: 10] if topic_level else []):
            if T.tier(pl["channel"]) <= 2 or any(a["name"].lower() in (pl["channel"] + pl["title"]).lower() for a in sc["authorities"]):
                add(T.playlist_videos(pl["id"], tr, scope), f"playlist: {pl['title'][:60]} ({pl['channel']})")
        for url in (sc["course_pages"] if topic_level else []):
            vids, lists = T.page_links(url, tr, scope)
            add(vids, f"course page: {url}")
            for pid in lists[:2]:
                add(T.playlist_videos(pid, tr, scope), f"course page playlist: {url}")

        # per lecture, per part
        for lp in lectures:
            lid = lp["lecture_id"]
            b = Budget({"yt": s["yt_searches_per_lecture"] - 2, "tavily": s["tavily_per_lecture"], "ddg": s["ddg_per_lecture"],
                        "serp": s["serpapi_youtube_per_lecture"]})
            pq = sc["part_queries"].get(lid, {})
            order = sorted(range(len(lp["parts"])), key=lambda i: -lp["parts"][i]["minutes"])   # biggest parts first
            for i in order:
                qs = pq.get(str(i)) or [lp["parts"][i]["search_phrases"][0]]
                q0 = qs[0]
                long = lp["parts"][i]["minutes"] >= 15
                got_free = False
                if IT.available():
                    # 18 Nov: free, so every part gets its scout queries and search phrases (the API budget allowed ~8 a
                    # lecture, which missed 3 of the manual picks); a long part's first query asks for videos over 20 min
                    fq = list(dict.fromkeys(qs + lp["parts"][i]["search_phrases"]))[: s.get("free_queries_per_part", 3)]
                    for k, q in enumerate(fq):
                        got = IT.search(q, tr, lid, duration="long" if long and k == 0 else None)
                        add([x["id"] for x in got], f"youtube: {q}", lid, i)
                        got_free = got_free or bool(got)
                if not got_free and b.take("yt"):
                    add([x["id"] for x in T.yt_search(q0, tr, lid, long=long)], f"youtube: {q0}", lid, i)
                for q in ([] if got_free else qs[:2]):        # DuckDuckGo videos only stands in for YouTube's own search
                    if b.take("ddg"):
                        add(T.ddg_videos(q, tr, lid), f"duckduckgo: {q}", lid, i)
                if b.take("tavily"):
                    rows = T.tavily(qs[-1], tr, lid, youtube_only=True)
                    add([v for r in rows for v in T.youtube_ids_in(r["url"])[0]], f"tavily: {qs[-1]}", lid, i)
            for i in ([] if IT.available() else order[:2]):      # SerpApi's YouTube engine is the same YouTube search
                if b.take("serp"):
                    q = f"{lp['parts'][i]['search_phrases'][0]} lecture"
                    add(T.serp_youtube(q, tr, lid), f"serpapi youtube: {q}", lid, i)
        tr.step(scope, "round 1 search done", candidates=len(found))

        det = T.details(list(found))
        # round 2: channel expansion — channels that are authorities, tier 1-2, or recur among the candidates
        counts: dict[str, int] = {}
        names: dict[str, str] = {}
        for v in det.values():
            if v.get("channel_id"):
                counts[v["channel_id"]] = counts.get(v["channel_id"], 0) + 1
                names[v["channel_id"]] = v["channel"]
        auth = [a["name"].lower() for a in sc["authorities"]]
        rank = sorted(counts, key=lambda c: (-(any(a in names[c].lower() or names[c].lower() in a for a in auth)),
                                             T.tier(names[c]), -counts[c]))
        n_ch = (s.get("channel_expansion_free", 8) if IT.available() else s["channel_expansion"]) if topic_level else 0
        picked = [c for c in rank if counts[c] >= 2 or T.tier(names[c]) <= 2 or any(a in names[c].lower() for a in auth)][:n_ch]
        # The channel search used the course's topic title ("Model context protocols and architecture"), a phrase no video
        # is titled by (17 Nov audit). The two words that recur most in the plan's search phrases are the topic's core term
        # ("MCP server", "attention mechanism").
        core = core_term([s_ for l in plan["lectures"] for p in l["parts"] for s_ in p["search_phrases"]]) or topic["title"]
        from_channel: dict[str, str] = {}
        for c in picked:
            got = IT.channel_search(c, core, tr, scope) if IT.available() else []
            if not got:
                got = T.yt_search(core, tr, scope, n=10, channel_id=c)
            for x in got:
                if x["id"] not in found:
                    from_channel[x["id"]] = c
            add([x["id"] for x in got], f"channel search: {names[c]}")
        tr.step(scope, "round 2 channel expansion", channels=[names[c] for c in picked])
        det.update(T.details([v for v in found if v not in det]))
        # a channel search may only add that channel's own videos (checked against the API's channel id)
        wrong = [v for v, c in from_channel.items() if v in det and det[v].get("channel_id") not in (None, c)]
        for v in wrong:
            det.pop(v, None)
        if wrong:
            tr.step(scope, "channel search: videos of other channels dropped", n=len(wrong))

        # 4 FILTER
        f = cfg()["filter"]
        keep, why_out = {}, {}
        seen_titles = set()
        skip = re.compile(f["skip_titles"], re.I)
        min_year = f["fast_moving_min_year"] if plan["fast_moving"] else 0
        for vid, v in sorted(det.items(), key=lambda kv: (kv[1].get("tier", 4), -(kv[1].get("views") or 0))):
            dur = v.get("duration_s") or 0
            lang = (v.get("language") or "en").lower()
            tkey = re.sub(r"[^a-z0-9]+", " ", v["title"].lower()).strip()[:60]
            reason = (f"too short ({dur}s)" if dur < f["min_video_s"] else "too long" if dur > f["max_video_s"]
                      else "not embeddable" if not v.get("embeddable", True) else "not public" if not v.get("public", True)
                      else "blocked in India" if v.get("blocked_in_india") else "made for kids" if v.get("made_for_kids")
                      else f"language {lang}" if not any(lang.startswith(x) for x in f["languages"])
                      else "title rule" if skip.search(v["title"]) else "duplicate title" if tkey in seen_titles
                      else f"older than {min_year}" if min_year and (v.get("published") or "0")[:4] < str(min_year) else None)
            if reason:
                why_out[reason.split(" (")[0]] = why_out.get(reason.split(" (")[0], 0) + 1
                continue
            seen_titles.add(tkey)
            keep[vid] = {**{k: v.get(k) for k in ("id", "url", "title", "channel", "channel_id", "published", "duration_s", "views",
                                                   "likes", "language", "description", "tier", "subscribers")},
                         "found_by": found[vid]["how"][:6], "parts": sorted(set(found[vid]["parts"]))}
        tr.step(scope, "filtered candidates", kept=len(keep), dropped=why_out)
        self.log(f"  candidates: {len(found)} found, {len(keep)} after filters ({', '.join(f'{k} {n}' for k, n in why_out.items())})")
        skipped = sum(1 for r in tr.rows if r["kind"] == "tool" and str(r.get("note", "")).startswith("skipped: no YouTube")) - skipped0
        return keep, skipped == 0

    # ------------------------------------------------------------ one lecture
    def lecture(self, topic: dict, lp: dict, cands: dict, fast: bool, sc: dict, taken: list[dict], lck: dict, tr: Trace) -> dict:
        lid, parts = lp["lecture_id"], lp["parts"]
        brief = next(b for b in self.briefs if b["lecture_id"] == lid)
        lecture = {"lecture_id": lid, "topic": topic["title"], "slot_minutes": lp["slot_minutes"],
                   "learning_outcomes": [lo["statement"] for lo in brief["learning_outcomes"]]}

        # 5 TRIAGE
        if "triage" not in lck:
            R = SL.rank(parts, cands, lid, sc)
            pool, ranked, roster = self.prerank(parts, cands, lid, sc, R=R)
            lck["ranked"] = {str(i): r for i, r in ranked.items()}
            lck["roster"] = [v["id"] for v in roster]
            tri = self.grade_and_select(lecture, parts, cands, fast, R, lck, tr) if SL.scfg().get("mode", "grade") == "grade" else None
            lck["triage"] = tri or A.triage(self.llm, lecture, parts, pool, fast, tr, self.run_id, ranked=ranked, roster=roster)
            tr.step(lid, "triage", picks=[(p["video_id"], p["parts"], p["reason"][:80]) for p in lck["triage"]["picks"]],
                    rejects=[(r["video_id"], r["reason"][:60]) for r in lck["triage"]["rejects"][:12]])
        picks = lck["triage"]["picks"]
        self.log(f"  {lid}: shortlist {len(picks)} videos")

        # 6 EVIDENCE + 7 READ
        lck.setdefault("clips", [])
        lck.setdefault("read", [])
        evs: dict[str, dict] = {}
        self.read_many(lecture, parts, [(p["video_id"], p["parts"]) for p in picks], cands, evs, lck, tr)
        # 8 VERIFY + 9 ASSEMBLE
        asm = self.verify_and_choose(lecture, lp, parts, cands, evs, lck, fast, taken, tr)
        # 10a SECOND READ, local first: empty AND under-filled parts (< 60% of their minutes) get their next-best unread
        # candidates (embedding rank), read with that part as focus. No new search, so no YouTube quota.
        thin = sorted(set(asm["gaps"]) | {pp["part"] for pp in asm["plan"] if pp["part"] >= 0 and pp["clips"] and
                                          sum(k["b"] - k["a"] for k in pp["clips"]) < 0.6 * 60 * parts[pp["part"]]["minutes"]})
        # (17 Nov audit: the flags were set before the work and the clips kept out of the checkpoint until the end, so an
        # interrupted run lost the round's clips and never read those videos again. Clips are now saved as they are read,
        # unverified ones are verified on resume, and each flag is set only when its round is done.)
        if thin and not lck.get("second_read"):
            n2 = cfg()["reading"]["second_read_videos"]
            # 17 Nov: with grades, the rest of the reading budget goes to the thin parts by the same coverage choice
            items = self.second_wave(parts, cands, lck, thin, asm["gaps"])[:n2]
            if not items:
                ranked = lck.get("ranked") or {}
                extra: dict[str, list[int]] = {}
                for i in thin:
                    for vid in [x for x in ranked.get(str(i), []) if x not in lck["read"] and x in cands][:2 if i not in asm["gaps"] else 3]:
                        extra.setdefault(vid, []).append(i)
                items = list(extra.items())[:n2]
            tr.step(lid, "second read for empty and thin parts", parts=thin, videos=[v for v, _ in items])
            self.read_many(lecture, parts, items, cands, evs, lck, tr)
            asm = self.verify_and_choose(lecture, lp, parts, cands, evs, lck, fast, taken, tr)
            lck["second_read"] = True
        # 10b GAPS, new searches: one bounded round
        if asm["gaps"] and not lck.get("gap_round"):
            gl = [{"lecture_id": lid, "part": i, "title": parts[i]["title"], "teaches": parts[i]["teaches"],
                   "tried": sc["part_queries"].get(lid, {}).get(str(i), []) + parts[i]["search_phrases"]} for i in asm["gaps"]]
            try:
                actions = A.gaps(self.llm, topic, gl, tr, self.run_id)
            except Exception as e:  # noqa: BLE001
                actions = []
                tr.step(lid, f"gap agent failed: {type(e).__name__}")
            new = self.gap_search(lid, actions, cands, tr, fast, parts=parts)
            tr.step(lid, "gap round", actions=[(a["part"], a["action"], a["queries"], a["reason"][:80]) for a in actions], new_videos=len(new))
            self.read_many(lecture, parts, list(new.items()), cands, evs, lck, tr)
            asm = self.verify_and_choose(lecture, lp, parts, cands, evs, lck, fast, taken, tr)
            lck["gap_round"] = True
        lck["assembly"] = asm
        tr.step(lid, "assembled", status=asm["status"], fill=asm["fill"], gaps=asm["gaps"], warnings=asm["warnings"])
        self.log(f"  {lid}: {asm['status']} · video {round(asm['total_s'] / 60)} of {lp['slot_minutes']} min · "
                 f"gaps {[parts[i]['title'] for i in asm['gaps']] or 'none'}")
        from profsagent.ytlecture.report import lecture_json
        res = lecture_json(self.run_id, topic, lp, brief, lck, cands, evs, fast)
        write_json(self.dir / "lectures" / f"{lid}.json", res)
        lck["assembly"] = asm
        return {"assembly": asm, "result": res}

    def prerank(self, parts: list[dict], cands: dict, lid: str, sc: dict | None = None,
                R: dict | None = None) -> tuple[list[dict], dict, list[dict]]:
        """(pool with full metadata, per-part ranked ids, roster of authoritative candidates outside the pool), from the
        local ranking in shortlist.rank (chapters, cross-encoder, quality prior, reputation). Used by the one-call triage
        (shortlist mode "list"), and in every mode for the per-part lists the second round falls back on.

        17 Nov audit: short plain titles of the best sources ranked low on every part; the per-part lists overlapped, so
        the pool held 24-35 of its 45 places (now filled with the next best); the roster kept a channel's first 6 by
        wording, which dropped Anthropic's most-watched talk (now its 6 best by the full score)."""
        t = cfg()["triage"]
        R = R or SL.rank(parts, cands, lid, sc)
        vids = R["vids"]
        if not vids:
            return [], {}, []
        per = max(4, t["prefilter_per_lecture"] // max(1, len(parts)))
        ranked = SL.per_part_lists(R, per, t.get("per_channel_in_part", 2))
        keep = list(dict.fromkeys(x for i in ranked for x in ranked[i]))
        best = R["score"].max(axis=0)
        for j in np.argsort(-best):
            if len(keep) >= t["prefilter_per_lecture"]:
                break
            if vids[j]["id"] not in keep:
                keep.append(vids[j]["id"])
        pool = [cands[v] for v in keep]
        inpool = set(keep)
        rel = R["rel"].max(axis=0)
        roster, by_ch = [], {}
        order = sorted(range(len(vids)), key=lambda j: (min(vids[j].get("tier", 4), 3), -best[j]))
        for j in order:
            v = vids[j]
            if v["id"] in inpool or not (v.get("tier", 4) <= 2 or R["auth"][j]) or rel[j] < t.get("roster_min_sim", 0.25):
                continue
            ch = v.get("channel_id") or v.get("channel")
            if by_ch.get(ch, 0) >= t.get("roster_per_channel", 4):
                continue
            by_ch[ch] = by_ch.get(ch, 0) + 1
            roster.append(v)
            if len(roster) >= t.get("roster_max", 60):
                break
        return pool, ranked, roster

    def reading_units(self, lecture: dict) -> float:
        t = cfg()["triage"]
        n = max(t.get("shortlist_min", 6), min(t.get("shortlist_max", 14), round(lecture["slot_minutes"] / 10)))
        return n * SL.scfg().get("budget_factor", 1.3)

    def grade_and_select(self, lecture: dict, parts: list[dict], cands: dict, fast: bool, R: dict, lck: dict, tr: Trace) -> dict | None:
        """Step 5 since 17 Nov: the AI grades ~15 cards per part (twice, opposite orders), code chooses the first wave.
        None when no grade came back (every provider failed): the caller falls back to the one-call triage."""
        lid = lecture["lecture_id"]
        nom = SL.nominations(self.llm, lecture, parts, R, fast, tr, self.run_id)
        lck["nominated"] = {str(i): v for i, v in nom.items()}
        # 23 Nov: the grader reads what the videos SAY (txshort.py); the title cards only when too few have transcripts
        txr = TX.run(parts, cands, R, nom, tr, lid) if TX.tcfg().get("enabled", True) else None
        if txr:
            sets, ex, lck["tx_spans"] = txr
            lck["tx_match"] = {v: {str(i): {"a": d["a"], "b": d["b"], "rel": round(d["rel"], 3)} for i, d in per.items()}
                               for v, per in ex.items()}
        else:
            sets, ex = SL.grade_sets(R, parts, nominated=nom), None
        lck["grade_mode"] = "transcript" if txr else "title"
        G = SL.grade(self.llm, lecture, parts, sets, cands, fast, getattr(self, "_level", ""), tr, self.run_id, excerpts=ex)
        if not G:
            tr.step(lid, "grading returned nothing; one-call triage instead")
            return None
        prior_of = {v["id"]: round(float(p), 4) for v, p in zip(R["vids"], R["prior"]) if v["id"] in G}
        B = self.reading_units(lecture)
        picks = SL.select(G, parts, cands, prior_of, B * SL.scfg().get("first_wave", 0.7))
        lck["grades"] = {v: {str(i): d for i, d in per.items()} for v, per in G.items()}
        lck["prior"] = prior_of
        lck["budget_units"] = B
        rejects = [{"video_id": v, "reason": (max(per.values(), key=lambda d: d["n"])["reason"] or "graded 0 for every part")[:120]}
                   for v, per in G.items() if max(d["g"] for d in per.values()) == 0]
        tr.step(lid, "graded", parts=len(parts), cards=sum(len(x) for x in sets.values()), videos_graded=len(G),
                strong=sorted(v for v, per in G.items() if max(d["g"] for d in per.values()) >= 2)[:40],
                units=round(B, 1))
        return {"picks": picks, "rejects": rejects, "mode": "grade"}

    def second_wave(self, parts: list[dict], cands: dict, lck: dict, thin: list[int], gaps: list[int]) -> list[tuple[str, list[int]]]:
        """The rest of the reading budget, chosen by the same coverage rule for the parts still empty (need 1) or thin
        (need 0.6), from graded videos not yet read. [] without grades."""
        if not lck.get("grades"):
            return []
        G = {v: {int(i): d for i, d in per.items()} for v, per in lck["grades"].items()}
        spent = sum(SL.units(cands[v]) for v in lck["read"] if v in cands)
        rest = max(SL.scfg().get("second_min_units", 3.0), lck.get("budget_units", 10) - spent)
        need = {i: (1.0 if i in gaps else 0.6) for i in thin}
        got = SL.select(G, parts, cands, lck.get("prior") or {}, rest, need=need, exclude=set(lck["read"]))
        return [(p["video_id"], [i for i in p["parts"] if i in need] or p["parts"]) for p in got]

    # ------------------------------------------------------------ the course pool and who has first claim on a video
    def _checkpoints(self) -> dict[str, dict]:
        return {p.stem: read_json(p) or {} for p in sorted((self.dir / "state").glob("M*.json")) if not p.stem.endswith(".bak")}

    def topic_ranks(self, cks: dict[str, dict]) -> dict[str, tuple]:
        """A topic's place in the timetable: (index of its first lecture in the briefs, topic id)."""
        order = {b["lecture_id"]: i for i, b in enumerate(getattr(self, "briefs", []) or [])}
        return {t: (min((order.get(l["lecture_id"], 10**9) for l in ((ck.get("plan") or {}).get("lectures") or [])), default=10**9), t)
                for t, ck in cks.items()}

    @staticmethod
    def found_here(v: dict) -> bool:
        """Found by the topic's own searches (not a copy borrowed from the course pool)."""
        how = v.get("found_by") or []
        return not how or any(not str(h).startswith("course pool") for h in how)

    def reserved_for_later(self, tid: str, cks: dict[str, dict] | None = None) -> set[str]:
        """Videos that a LATER topic's own searches found and this topic's did not: that topic has first claim on them.
        18 Nov, Transformers r5/r6: through the course pool W01.L2 used Raschka's "Self-Attention and Scaled Dot-Product"
        and NPTEL Lec 15, both found for W02.L1's topic, and the timetable rule then gave them to W01.L2, so W02.L1 lost
        20-22 min it had already cut."""
        if not cfg()["triage"].get("course_pool", True):
            return set()
        cks = cks if cks is not None else self._checkpoints()
        ranks = self.topic_ranks(cks)
        me = ranks.get(tid, (10**9, tid))
        later = {vid for t, ck in cks.items() if t != tid and ranks[t] > me
                 for vid, v in (ck.get("candidates") or {}).items() if self.found_here(v)}
        own = {vid for vid, v in ((cks.get(tid) or {}).get("candidates") or {}).items() if self.found_here(v)}
        return later - own

    def with_course_pool(self, tid: str, cands: dict, fast: bool) -> dict:
        """This topic's candidates plus those found for EARLIER topics of the course (17 Nov audit: the manual pass used
        one anchor lecture in 4 lectures of 3 topics; the engine saw each topic's own search results only). 18 Nov: later
        topics' videos are theirs first (reserved_for_later). Read-only copies, not saved into this topic's checkpoint."""
        if not cfg()["triage"].get("course_pool", True):
            return cands
        merged = dict(cands)
        fast_year = cfg()["filter"]["fast_moving_min_year"] if fast else 0
        cks = self._checkpoints()
        ranks = self.topic_ranks(cks)
        me = ranks.get(tid, (10**9, tid))
        for t, ck in cks.items():
            if t == tid or ranks[t] > me:
                continue
            for vid, v in (ck.get("candidates") or {}).items():
                if vid in merged or (fast_year and (v.get("published") or "0")[:4] < str(fast_year)):
                    continue
                merged[vid] = {**v, "tier": T.tier(v.get("channel", "")), "parts": [], "found_by": [f"course pool: {t}"]}
        return merged

    def taken_elsewhere(self, tid: str, before: str | None = None) -> list[dict]:
        """Clips already chosen by lectures of the course's OTHER topics that come earlier in the timetable than lecture
        `before` (17 Nov audit: 4 clips of 2-8 min played in two lectures, because `taken` covered one topic only). The
        timetable decides who keeps a clip, not which lecture happened to be assembled first."""
        order = {b["lecture_id"]: i for i, b in enumerate(getattr(self, "briefs", []) or [])}
        limit = order.get(before, 10**9) if before else 10**9
        out = []
        for p in sorted((self.dir / "state").glob("M*.json")):
            if p.stem == tid or p.stem.endswith(".bak"):
                continue
            for lid, lck in ((read_json(p) or {}).get("lectures") or {}).items():
                if order.get(lid, -1) >= limit:
                    continue
                for pp in (lck.get("assembly") or {}).get("plan", []):
                    out += [{"video": k["video"], "a": k["a"], "b": k["b"]} for k in pp["clips"]]
        return out

    def verify_and_choose(self, lecture, lp, parts, cands, evs, lck, fast, taken, tr) -> dict:
        """Verify every clip not checked yet (new ones, or ones left over from an interrupted run), then assemble."""
        todo = [k for k in lck["clips"] if "check" not in k]
        if todo:
            for k in todo:
                if k["video"] not in evs:
                    evs[k["video"]] = E.evidence(cands[k["video"]], tr, lecture["lecture_id"])
            A.verify(self.llm, lecture, parts, todo, evs, tr, self.run_id)
            if self._checkpoint:
                self._checkpoint()
        reserved = getattr(self, "_reserved", set())
        clips = [k for k in lck["clips"] if k["video"] not in reserved]
        if len(clips) < len(lck["clips"]):
            tr.step(lecture["lecture_id"], "clips of videos a later topic found first are left to it",
                    n=len(lck["clips"]) - len(clips))
        videos = {k: cands[k] for k in {c["video"] for c in clips}}
        return choose(lp, clips, videos, fast, taken)

    def read_many(self, lecture: dict, parts: list[dict], items: list[tuple[str, list[int]]], cands: dict, evs: dict,
                  lck: dict, tr: Trace, add: bool = True) -> list[dict]:
        """Evidence one video at a time (caption pacing and the browser are single-threaded), then the AI reading of several
        videos at once: each read is 1-2 calls that wait on a model, and the providers' limits are independent."""
        from concurrent.futures import ThreadPoolExecutor
        todo = []
        for vid, ps in items:
            if vid not in cands:
                continue
            if vid not in evs:
                evs[vid] = E.evidence(cands[vid], tr, lecture["lecture_id"])
            if vid not in lck["read"]:
                todo.append((vid, ps))
        out: list[dict] = []
        with ThreadPoolExecutor(max_workers=max(1, cfg()["reading"]["workers"])) as pool:
            futs = [(vid, pool.submit(self.read, lecture, parts, cands[vid], evs[vid], ps, tr,
                                      (lck.get("tx_spans") or {}).get(vid))) for vid, ps in todo]
            for vid, f in futs:
                got = f.result()
                if got is None:
                    # 18 Nov: the laptop slept mid-run; on waking, the three best videos of Transformers W01.L2 failed
                    # with "getaddrinfo failed", were marked read with no clips and never retried. A failed read is now
                    # retried on the next run; after `read_retries` failures the video is given up.
                    fails = lck.setdefault("read_failed", {})
                    fails[vid] = fails.get(vid, 0) + 1
                    if fails[vid] < cfg()["reading"].get("read_retries", 2):
                        continue
                    got = []
                out += got
                lck["read"].append(vid)
                if add:
                    lck["clips"] += got
                if self._checkpoint:
                    self._checkpoint()
        return out

    def chapter_regions(self, parts: list[dict], ev: dict, hint: list[int]) -> list[tuple[float, float]]:
        """For a long video with chapters: the chapters closest to each focus part (local embeddings), instead of a skim call."""
        ch = [c for c in ev["chapters"] if c["end"] - c["start"] >= 30]
        # Short (often auto-generated) chapters cannot stand in for a skim: 15 Nov, a 20-min talk with 1-2 min chapters gave
        # the reader 3 slivers of ~1.5 min, so every clip it cut was under a minute and was dropped.
        if len(ch) < 3 or sum(c["end"] - c["start"] for c in ch) / len(ch) < 180:
            return []
        focus = [i for i in (hint or range(len(parts))) if 0 <= i < len(parts)]
        cv = _embed([c["title"] for c in ch])
        pv = _embed([f"{parts[i]['title']}. {parts[i]['teaches']}" for i in focus])
        sim = (pv @ cv.T) / (np.linalg.norm(pv, axis=1, keepdims=True) * np.linalg.norm(cv, axis=1) + 1e-9)
        regions = []
        for r, row in enumerate(sim):
            want = max(300.0, 0.8 * 60 * parts[focus[r]]["minutes"])      # at least the part's length, at least 5 min
            for j in np.argsort(-row)[: cfg()["reading"]["chapter_regions"]]:
                if row[j] >= 0.25:
                    a = ch[j]["start"]
                    regions.append((a, max(ch[j]["end"], min(a + want, ch[-1]["end"]))))
        merged: list[list[float]] = []
        for a, b in sorted(regions):
            if merged and a <= merged[-1][1] + 60:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        return [(a, b) for a, b in merged]

    @staticmethod
    def span_regions(spans: dict | None, hint: list[int]) -> list[tuple[float, float]]:
        """For a long video matched by transcript windows (txshort.spans): the regions of its focus parts, merged."""
        out = sorted((float(a), float(b)) for i in hint for a, b in (spans or {}).get(str(i), []))
        merged: list[list[float]] = []
        for a, b in out:
            if merged and a <= merged[-1][1] + 60:
                merged[-1][1] = max(merged[-1][1], b)
            else:
                merged.append([a, b])
        return [(a, b) for a, b in merged]

    def read(self, lecture: dict, parts: list[dict], v: dict, ev: dict, hint: list[int], tr: Trace,
             spans: dict | None = None) -> list[dict]:
        scope = f"{lecture['lecture_id']}/{v['id']}"
        if not ev["rows"] and not ev["chapters"]:
            tr.step(scope, "not read: no words and no chapters")
            return []
        dur = float(v.get("duration_s") or 0)
        try:
            regions = []
            if ev["rows"] and dur > cfg()["reading"]["short_video_s"]:
                # 23 Nov: where the words match the focus parts (found while shortlisting) beats chapter titles
                regions = self.span_regions(spans, hint) if TX.tcfg().get("spans_for_reading", True) else []
                if regions:
                    tr.step(scope, "skim skipped: regions from the transcript match", regions=[(E.ts(a), E.ts(b)) for a, b in regions])
                else:
                    regions = self.chapter_regions(parts, ev, hint)
                    if regions:
                        tr.step(scope, "skim skipped: regions from chapters", regions=[(E.ts(a), E.ts(b)) for a, b in regions])
            if regions:
                pass
            elif ev["rows"] and dur > cfg()["reading"]["short_video_s"]:
                wins, _ = A.skim_windows(self.llm, lecture, parts, v, ev, hint, tr, self.run_id)
                if not wins:
                    tr.step(scope, "skim found nothing for this lecture")
                    return []
                regions = [(w["a"], w["b"]) for w in wins]
            else:
                regions = [(0.0, dur)]
            clips, model = A.zoom_clips(self.llm, lecture, parts, v, ev, regions, tr, self.run_id, focus=hint)
        except Exception as e:  # noqa: BLE001 — one unreadable video must not stop the lecture
            tr.step(scope, f"read failed: {type(e).__name__}: {str(e)[:120]}")
            return None                  # not marked read: retried by the next run (read_many)
        tr.step(scope, "read", evidence=ev["source"], clips=[(k["part"], E.ts(k["a"]), E.ts(k["b"]), k["rating"]) for k in clips])
        return clips

    def gap_search(self, lid: str, actions: list[dict], cands: dict, tr: Trace, fast: bool = False,
                   parts: list[dict] | None = None) -> dict[str, list[int]]:
        """New videos (not seen before) for the gap parts: {video_id: [parts]}, filtered like round 1, then ranked by how
        well title and description match the gap part (18 Nov: ranked by tier and views alone, the gap round read IBM's
        "What is Random Forest?" and a Primavera P6 course for an LSTM part)."""
        new: dict[str, list[int]] = {}
        for a in actions:
            if a["action"] != "search":
                continue
            for q in a["queries"][:3]:
                got = [x["id"] for x in self.video_search(q, tr, lid)]
                ids = got + ([] if got else T.ddg_videos(q, tr, lid))
                for v in ids:
                    if v not in cands:
                        new.setdefault(v, []).append(a["part"])
        if not new:
            return {}
        det = T.details(list(new))
        f = cfg()["filter"]
        skip = re.compile(f["skip_titles"], re.I)
        min_year = str(f["fast_moving_min_year"]) if fast else ""      # 17 Nov audit: round 1 had this rule, the gap round not
        out = {}
        scored = []
        for vid, v in det.items():
            dur = v.get("duration_s") or 0
            if f["min_video_s"] <= dur <= f["max_video_s"] and v.get("embeddable", True) and not v.get("blocked_in_india") \
                    and not skip.search(v["title"]) and any((v.get("language") or "en").lower().startswith(x) for x in f["languages"]) \
                    and not (min_year and (v.get("published") or "0")[:4] < min_year):
                cands[vid] = {**{k: v.get(k) for k in ("id", "url", "title", "channel", "channel_id", "published", "duration_s", "views",
                                                       "likes", "language", "description", "tier", "subscribers")},
                              "found_by": ["gap round"], "parts": [f"{lid}#{p}" for p in new[vid]]}
                scored.append(vid)
        if not scored:
            return {}
        if parts:
            vt = SL._embed([f"{cands[v]['title']}. {(cands[v].get('description') or '')[:300]}" for v in scored])
            pt = SL._embed([SL.part_text(p) for p in parts])
            sim = SL._cos(pt, vt)
            floor = cfg()["reading"].get("gap_min_sim", 0.35)
            best = {v: max(float(sim[p, j]) for p in new[v] if 0 <= p < len(parts)) for j, v in enumerate(scored)}
            keep = sorted((v for v in scored if best[v] >= floor),
                          key=lambda v: -(best[v] + {1: 0.10, 2: 0.06}.get(cands[v].get("tier", 4), 0.0)))
            tr.step(lid, "gap round candidates", kept=len(keep), below_match_floor=len(scored) - len(keep))
        else:
            keep = sorted(scored, key=lambda v: (cands[v].get("tier", 4), -(cands[v].get("views") or 0)))
        for vid in keep[: cfg()["reading"]["gap_round_videos"]]:   # new videos read per lecture in the gap round
            out[vid] = sorted(set(new[vid]))
        return out
