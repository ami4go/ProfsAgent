"""Tools the orchestrator and its sub-agents use. Every call is cached on disk, kept inside its free quota, and recorded in
the run's trace (what was asked, of which service, what came back), so a run can be audited and its method replicated.

  YouTube Data API     search (videos, playlists, by channel), video + channel details, playlist items   YOUTUBE_API_KEY
  SerpApi              YouTube search engine and Google web search (scarce: ~250 a month)                 SERPAPI_API_KEY
  Tavily               web search, also restricted to youtube.com (1,000 a month)                        TAVILY_API_KEY
  DuckDuckGo           web and video search (no key; rate-limited, so spaced and treated as optional)
  Pages                course pages read for the YouTube links they list (Phase 1's cached fetcher)
"""
from __future__ import annotations

import os
import re
import threading
import time
from functools import lru_cache

import yaml

from profsagent.config import CONFIG
from profsagent.delivery import sources as S
from profsagent.delivery.common import iso_duration_s
from profsagent.delivery.resources import rcfg

YT_ID = re.compile(r"(?:youtube\.com/(?:watch\?(?:[^\s\"'<>]*&)?v=|embed/|shorts/|live/)|youtu\.be/)([\w-]{11})")
YT_LIST = re.compile(r"youtube\.com/(?:playlist\?|watch\?[^\s\"'<>]*?)list=([\w-]{13,64})")


@lru_cache(maxsize=1)
def cfg() -> dict:
    return yaml.safe_load((CONFIG / "ytlecture.yaml").read_text(encoding="utf-8"))


def _word_hit(name: str, n: str) -> bool:
    """`name` appears in channel title `n` as whole words (17 Nov audit: substring matching made "Lets Decode Together"
    tier 1 through "ETH", and "AI Engineering from Scratch with Avinash" tier 1 through "AI Engineer")."""
    return re.search(r"(?<![a-z0-9])" + re.escape(name.lower()) + r"(?![a-z0-9])", n) is not None


@lru_cache(maxsize=4096)
def tier(channel: str) -> int:
    """1 = primary source / university, 2 = established educator, 3 = known, 4 = unknown. Names match as whole words;
    brand names (tiers.exact1/exact2) only as the whole channel title, so "Claude Code Tips by Ravi" is not Anthropic."""
    n = (channel or "").lower().strip()
    t = cfg()["tiers"]
    for lvl in (1, 2):
        if any(n == x.lower() for x in t.get(f"exact{lvl}", [])):
            return lvl
    for lvl in (1, 2):
        if any(_word_hit(x, n) for x in t[f"tier{lvl}"]):
            return lvl
    rc = rcfg()["channels"]                  # the shared lists, matched the same way (their own lookup uses substrings)
    for lvl in (1, 2, 3):
        if any(_word_hit(x, n) for x in rc[f"tier{lvl}"]):
            return lvl
    return 4


@lru_cache(maxsize=4096)
def is_edu(channel: str) -> bool:
    """A university, course or educator channel (the tiers.tier1 word list), as opposed to a vendor's own channel
    (exact1). 17 Nov: both are tier 1, and the vendors' many product talks crowded out the university lectures."""
    n = (channel or "").lower().strip()
    return any(_word_hit(x, n) for x in cfg()["tiers"]["tier1"])


class Trace:
    """Append-only record of every tool call and decision; written next to the outputs as trace.jsonl + trace.md."""

    def __init__(self):
        self.rows: list[dict] = []

    def tool(self, tool: str, query: str, n: int, note: str = "", scope: str = "") -> None:
        self.rows.append({"t": time.strftime("%H:%M:%S"), "kind": "tool", "tool": tool, "query": query, "results": n,
                          "note": note, "scope": scope})

    def step(self, scope: str, msg: str, **data) -> None:
        self.rows.append({"t": time.strftime("%H:%M:%S"), "kind": "step", "scope": scope, "msg": msg, **data})

    def ai(self, agent: str, scope: str, endpoint: str, tokens: int, note: str = "") -> None:
        self.rows.append({"t": time.strftime("%H:%M:%S"), "kind": "ai", "agent": agent, "scope": scope, "endpoint": endpoint,
                          "tokens": tokens, "note": note})


class Budget:
    """Per-lecture spend counters for the scarce services (the YouTube unit quota itself is in sources.YouTube.quota)."""

    def __init__(self, scope_cfg: dict):
        self.cap = dict(scope_cfg)
        self.used: dict[str, int] = {}

    def take(self, what: str, n: int = 1) -> bool:
        if self.used.get(what, 0) + n > self.cap.get(what, 10**9):
            return False
        self.used[what] = self.used.get(what, 0) + n
        return True


# ---------------------------------------------------------------- YouTube Data API
_yt = None


def yt() -> S.YouTube:
    global _yt
    if _yt is None:
        _yt = S.YouTube()
    return _yt


def yt_search(q: str, trace: Trace, scope: str, n: int | None = None, long: bool = False, channel_id: str | None = None,
              kind: str = "video") -> list[dict]:
    """[{id, title, channel, channel_id}] for videos (or playlists). 100 units unless cached 21 days."""
    n = n or cfg()["search"]["yt_results"]
    key = f"ytl|{kind}|{q}|{n}|{long}|{channel_id}"
    y = yt()
    if S.read_json(S._cache_path("yt_search", key)) is None and not (y.ok and y.quota.can(100)):
        trace.tool("youtube.search", q, 0, "skipped: no YouTube units left today", scope)
        return []

    def run():
        p = {"part": "snippet", "q": q, "type": kind, "maxResults": n, "key": y.key, "safeSearch": "moderate",
             "relevanceLanguage": cfg()["search"]["language"], "regionCode": cfg()["search"]["region"]}
        if kind == "video":
            p["videoEmbeddable"] = "true"
            if long:
                p["videoDuration"] = "long"
        if channel_id:
            p["channelId"] = channel_id
        r = S._get(f"{y.API}/search", p)
        y.quota.spend(100)
        if r is None or r.status_code != 200:
            return {"error": f"HTTP {getattr(r, 'status_code', '?')}"}
        out = []
        for it in r.json().get("items", []):
            i, sn = it.get("id", {}), it.get("snippet", {})
            vid = i.get("videoId") or i.get("playlistId")
            if vid:
                out.append({"id": vid, "title": sn.get("title", ""), "channel": sn.get("channelTitle", ""),
                            "channel_id": sn.get("channelId")})
        return out
    v = S._cached("yt_search", key, 21, run)
    res = [] if isinstance(v, dict) else v
    trace.tool("youtube.search" + (f"[{kind}]" if kind != "video" else "") + ("[long]" if long else "")
               + (f"[channel]" if channel_id else ""), q, len(res), v.get("error", "") if isinstance(v, dict) else "", scope)
    return res


def playlist_videos(pid: str, trace: Trace, scope: str, n: int = 50) -> list[str]:
    items = yt().playlist_items(pid, n)
    trace.tool("youtube.playlistItems", pid, len(items), "", scope)
    return [x["id"] for x in items]


def details(ids: list[str]) -> dict[str, dict]:
    """Full metadata for videos (1 unit per 50, cached 7 days) plus channel subscribers and source tier."""
    ids = list(dict.fromkeys(i for i in ids if i and len(i) == 11))
    d = yt().videos(ids)
    ch = yt().channels([x["channel_id"] for x in d.values() if x.get("channel_id")])
    for v in d.values():
        v["subscribers"] = (ch.get(v.get("channel_id")) or {}).get("subscribers")
        v["tier"] = tier(v.get("channel", ""))
    return d


# ---------------------------------------------------------------- SerpApi (YouTube engine + Google)
def serp_youtube(q: str, trace: Trace, scope: str) -> list[str]:
    if not os.environ.get("SERPAPI_API_KEY") or S.serpapi_left() <= cfg()["search"]["serpapi_keep"]:
        trace.tool("serpapi.youtube", q, 0, "skipped: no key or monthly plan nearly used", scope)
        return []
    j = S._serpapi({"engine": "youtube", "search_query": q, "gl": "in", "hl": "en"}, "serp_yt", q)
    ids = [] if "error" in j else [m.group(1) for x in j.get("video_results", []) for m in [YT_ID.search(x.get("link", ""))] if m]
    trace.tool("serpapi.youtube", q, len(ids), j.get("error", "") if "error" in j else "", scope)
    return ids


def serp_google(q: str, trace: Trace, scope: str, n: int = 8) -> list[dict]:
    if not os.environ.get("SERPAPI_API_KEY") or S.serpapi_left() <= cfg()["search"]["serpapi_keep"]:
        return []
    j = S._serpapi({"engine": "google", "q": q, "num": n, "gl": "in", "hl": "en"}, "serp_g", f"{q}|{n}")
    rows = [] if "error" in j else [{"url": x.get("link", ""), "title": x.get("title", ""), "content": x.get("snippet", "")}
                                    for x in j.get("organic_results", [])]
    trace.tool("serpapi.google", q, len(rows), j.get("error", "") if "error" in j else "", scope)
    return rows


# ---------------------------------------------------------------- Tavily + DuckDuckGo
def tavily(q: str, trace: Trace, scope: str, youtube_only: bool = False, n: int = 8) -> list[dict]:
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        return []
    ck = f"ytl|{q}|{n}|{youtube_only}"

    def run():
        body = {"api_key": key, "query": q, "max_results": n, "search_depth": "basic", "include_answer": False}
        if youtube_only:
            body["include_domains"] = ["youtube.com"]
        try:
            r = S._http.post("https://api.tavily.com/search", headers={"Authorization": f"Bearer {key}"}, json=body)
        except Exception as e:  # noqa: BLE001
            return {"error": type(e).__name__}
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}"}
        return [{"url": x["url"], "title": x.get("title") or "", "content": (x.get("content") or "")[:800]} for x in r.json().get("results", [])]
    v = S._cached("tavily", ck, 21, run)
    rows = [] if isinstance(v, dict) else v
    trace.tool("tavily" + ("[youtube.com]" if youtube_only else ""), q, len(rows), v.get("error", "") if isinstance(v, dict) else "", scope)
    return rows


def guarded(fn, *args, seconds: float = 60, default=None):
    """Call fn with a hard wall-clock limit (a daemon thread). 16 Nov: one search call in the scout hung for 3.5 h; the
    DuckDuckGo library has no overall timeout. A call past the limit gives `default` and is left to finish on its own."""
    box: dict = {}

    def target():
        try:
            box["v"] = fn(*args)
        except Exception as e:  # noqa: BLE001
            box["e"] = e
    t = threading.Thread(target=target, daemon=True)
    t.start()
    t.join(seconds)
    if t.is_alive() or "e" in box:
        return default
    return box.get("v", default)


_ddg = {"empty": 0, "until": 0.0}


def ddg_videos(q: str, trace: Trace, scope: str, n: int = 15) -> list[str]:
    # 17 Nov audit: 50 of 56 DuckDuckGo video searches returned nothing (rate-limited after the first few), each costing a
    # call and part of the lecture's budget. After `ddg_max_empty` empty answers in a row it is skipped for a while.
    if time.time() < _ddg["until"]:
        trace.tool("duckduckgo.videos", q, 0, "skipped: rate-limited earlier in this run", scope)
        return []
    ids = guarded(S.web_videos, q, n, seconds=cfg()["search"].get("tool_deadline_s", 60), default=[]) or []
    _ddg["empty"] = 0 if ids else _ddg["empty"] + 1
    if _ddg["empty"] >= cfg()["search"].get("ddg_max_empty", 4):
        _ddg["until"], _ddg["empty"] = time.time() + 1800, 0
    trace.tool("duckduckgo.videos", q, len(ids), "" if ids else "none (often rate-limited)", scope)
    return ids


def ddg_web(q: str, trace: Trace, scope: str, n: int = 8) -> list[dict]:
    rows = guarded(S.duckduckgo, q, n, seconds=cfg()["search"].get("tool_deadline_s", 60), default=[]) or []
    trace.tool("duckduckgo.web", q, len(rows), "", scope)
    return rows


def web(q: str, trace: Trace, scope: str, n: int = 8) -> list[dict]:
    """Open-web results for the scout: Tavily, then DuckDuckGo, then Google through SerpApi (each when the previous is empty)."""
    for fn in (tavily, ddg_web, serp_google):
        rows = fn(q, trace, scope, n=n)
        if rows:
            return rows
    return []


def youtube_ids_in(text: str) -> tuple[list[str], list[str]]:
    """(video ids, playlist ids) linked from any text."""
    return list(dict.fromkeys(YT_ID.findall(text or ""))), list(dict.fromkeys(YT_LIST.findall(text or "")))


def page_links(url: str, trace: Trace, scope: str) -> tuple[list[str], list[str]]:
    """A course page's YouTube videos and playlists (a course site usually links its lecture recordings)."""
    def run():
        try:
            r = S._http.get(url, timeout=25)
        except Exception as e:  # noqa: BLE001
            return {"error": type(e).__name__}
        if r.status_code != 200:
            return {"error": f"HTTP {r.status_code}"}
        return {"html": r.text[:2_000_000]}
    v = S._cached("course_page", url, 14, run)
    if "error" in v:
        trace.tool("page", url, 0, v["error"], scope)
        return [], []
    vids, lists = youtube_ids_in(v["html"])
    trace.tool("page", url, len(vids) + len(lists), f"{len(vids)} videos, {len(lists)} playlists", scope)
    return vids, lists


def iso_s(x) -> int | None:
    return iso_duration_s(x)
