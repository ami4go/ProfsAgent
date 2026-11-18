"""Free YouTube search: the endpoint youtube.com's own search box calls (InnerTube), with yt-dlp as the fallback.

18 Nov study (outputs/yt_research/repo_comparison): on 33 CS601 part queries this search found as many of the manual
playlists' videos as the YouTube Data API (13-14 vs 13 of 37), at no quota cost (the API spends 100 of 10,000 daily
units a search), while DuckDuckGo videos answered nothing 50 times out of 56. It also found 3 manual picks the engine
never found, because the API budget allowed only ~8 per-part searches a lecture.

  search(q, kind="video"|"playlist", duration=None|"long"|"medium")   one results page (~20)
  channel_search(channel_id, q)                                         a channel's own search tab

It is not an official API: YouTube can change it without notice. So every call is cached, paced and checked; after
`max_fails` failures in a row the same request goes through yt-dlp (maintained against YouTube's changes every few
weeks), and when both fail the caller falls back to the YouTube Data API. Search filters are YouTube's own `sp` codes
(tested: EgQQARgC returned 20 of 20 videos over 20 min, EgQQARgD 20 of 20 of 4-20 min; youtubei.js's filter option
was ignored).
"""
from __future__ import annotations

import random
import re
import threading
import time

import httpx

from profsagent.delivery import sources as S
from profsagent.ytlecture.tools import Trace, cfg

SP = {("video", None): "EgIQAQ%3D%3D", ("video", "long"): "EgQQARgC", ("video", "medium"): "EgQQARgD",
      ("playlist", None): "EgIQAw%3D%3D"}
CHANNEL_SEARCH = "EgZzZWFyY2jyBgQKAloA"
_UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
_st = {"fails": 0, "last": 0.0, "lock": threading.Lock(), "ytdlp_dead": False}


def icfg() -> dict:
    return cfg().get("innertube", {})


def secs(t: str | None) -> int | None:
    t = (t or "").strip()
    if not re.fullmatch(r"\d+(:\d+){1,2}", t):
        return None
    s = 0
    for p in t.split(":"):
        s = s * 60 + int(p)
    return s


def _text(o) -> str:
    if not isinstance(o, dict):
        return ""
    return o.get("simpleText") or "".join(r.get("text", "") for r in o.get("runs", []))


def _walk(o, key: str, out: list) -> list:
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                out.append(v)
            else:
                _walk(v, key, out)
    elif isinstance(o, list):
        for v in o:
            _walk(v, key, out)
    return out


def parse_videos(d: dict) -> list[dict]:
    """[{id, title, channel, channel_id, duration_s, views, published_ago}] from a search or channel-search response."""
    out, seen = [], set()
    for v in _walk(d, "videoRenderer", []):
        vid = v.get("videoId")
        if not vid or vid in seen:
            continue
        seen.add(vid)
        owner = ((v.get("ownerText") or v.get("longBylineText") or {}).get("runs") or [{}])[0]
        views = re.sub(r"[^\d]", "", _text(v.get("viewCountText")))
        out.append({"id": vid, "title": _text(v.get("title")), "channel": owner.get("text", ""),
                    "channel_id": ((owner.get("navigationEndpoint") or {}).get("browseEndpoint") or {}).get("browseId"),
                    "duration_s": secs(_text(v.get("lengthText"))), "views": int(views) if views else None,
                    "published_ago": _text(v.get("publishedTimeText"))})
    return out


def parse_playlists(d: dict) -> list[dict]:
    """[{id, title, channel}] from a playlist search (YouTube now sends these as lockupViewModel)."""
    out = []
    for lk in _walk(d, "lockupViewModel", []):
        if lk.get("contentType") != "LOCKUP_CONTENT_TYPE_PLAYLIST" or not lk.get("contentId"):
            continue
        md = (lk.get("metadata") or {}).get("lockupMetadataViewModel") or {}
        rows = ((md.get("metadata") or {}).get("contentMetadataViewModel") or {}).get("metadataRows") or []
        first = [((p.get("text") or {}).get("content") or "") for p in (rows[0].get("metadataParts") or [])] if rows else []
        out.append({"id": lk["contentId"], "title": ((md.get("title") or {}).get("content") or ""),
                    "channel": first[0] if first else ""})
    return out


def _post(endpoint: str, body: dict) -> dict | None:
    c = icfg()
    with _st["lock"]:
        wait = _st["last"] + c.get("min_interval_s", 1.0) + random.random() * c.get("jitter_s", 0.5) - time.time()
        if wait > 0:
            time.sleep(wait)
        _st["last"] = time.time()
    ctx = {"client": {"hl": "en", "gl": cfg()["search"].get("region", "IN"), "clientName": "WEB",
                      "clientVersion": c.get("client_version", "2.20261116.00.00")}}
    try:
        r = httpx.post(f"https://www.youtube.com/youtubei/v1/{endpoint}?prettyPrint=false", json={"context": ctx, **body},
                       headers={"User-Agent": _UA, "Origin": "https://www.youtube.com", "Accept-Language": "en-US,en;q=0.9"},
                       timeout=c.get("timeout_s", 20))
        return r.json() if r.status_code == 200 else None
    except (httpx.HTTPError, ValueError):
        return None


def _ytdlp(url: str, n: int) -> list[dict] | None:
    """The same page through yt-dlp (flat: no per-video requests). None when yt-dlp is missing or fails."""
    if _st["ytdlp_dead"]:
        return None
    try:
        import yt_dlp
    except ImportError:
        _st["ytdlp_dead"] = True
        return None
    try:
        with yt_dlp.YoutubeDL({"extract_flat": True, "quiet": True, "no_warnings": True, "skip_download": True,
                               "playlistend": n}) as y:
            info = y.extract_info(url, download=False)
    except Exception:  # noqa: BLE001
        return None
    out = []
    for e in (info or {}).get("entries") or []:
        if not e.get("id"):
            continue
        playlist = e.get("ie_key") == "YoutubeTab" or str(e.get("url", "")).find("list=") >= 0
        out.append({"id": e["id"], "title": e.get("title") or "", "channel": e.get("channel") or e.get("uploader") or "",
                    "channel_id": e.get("channel_id"), "duration_s": int(e["duration"]) if e.get("duration") else None,
                    "views": e.get("view_count"), "published_ago": "", "playlist": playlist})
    return out


def _run(key: str, endpoint: str, body: dict, parse, fallback_url: str, n: int) -> list[dict] | dict:
    """Cached call: InnerTube, else (after max_fails in a row) yt-dlp. {"error": ...} when neither answered."""
    def go():
        if _st["fails"] < icfg().get("max_fails", 3):
            d = _post(endpoint, body)
            if d is not None:
                _st["fails"] = 0
                got = parse(d)
                if got:
                    return got[:n]
                # an answer we could not parse: perhaps YouTube changed its layout, so yt-dlp is asked as well
            else:
                _st["fails"] += 1
        got = _ytdlp(fallback_url, n)
        return got[:n] if got is not None else {"error": "innertube and yt-dlp both failed"}
    return S._cached("innertube", key, icfg().get("cache_days", 14), go)


def search(q: str, trace: Trace, scope: str, kind: str = "video", duration: str | None = None, n: int = 20) -> list[dict]:
    from urllib.parse import quote_plus
    sp = SP.get((kind, duration), SP[(kind, None)])
    v = _run(f"search|{kind}|{duration}|{q}|{n}", "search", {"query": q, "params": sp},
             parse_videos if kind == "video" else parse_playlists,
             f"https://www.youtube.com/results?search_query={quote_plus(q)}&sp={sp}", n)
    res = v if isinstance(v, list) else []
    if kind == "playlist":
        res = [x for x in res if x.get("playlist", True)]
    trace.tool(f"innertube.search[{kind}{'|' + duration if duration else ''}]", q, len(res),
               v.get("error", "") if isinstance(v, dict) else "", scope)
    return res


def channel_search(channel_id: str, q: str, trace: Trace, scope: str, n: int = 15) -> list[dict]:
    """A channel's own search tab. Only videos whose owner IS that channel are returned (18 Nov: a channel search
    returned YouTube Movies entries, whose owner line is a genre such as "Action & adventure • 2024", with no channel)."""
    from urllib.parse import quote_plus
    v = _run(f"channel|{channel_id}|{q}|{n}", "browse", {"browseId": channel_id, "params": CHANNEL_SEARCH, "query": q},
             parse_videos, f"https://www.youtube.com/channel/{channel_id}/search?query={quote_plus(q)}", n)
    res = v if isinstance(v, list) else []
    for x in res:                     # yt-dlp reads the channel's own tab, where it often leaves the channel id out
        if x.get("channel_id") is None and "published_ago" in x and x.get("published_ago") == "" and "playlist" in x:
            x["channel_id"] = channel_id
    own = [x for x in res if x.get("channel_id") == channel_id]
    trace.tool("innertube.channel_search", f"{channel_id}: {q}", len(own),
               (v.get("error", "") if isinstance(v, dict) else "") + (f"; {len(res) - len(own)} from other channels dropped"
                                                                      if len(own) < len(res) else ""), scope)
    return own


def available() -> bool:
    return bool(icfg().get("enabled", True)) and not (_st["fails"] >= icfg().get("max_fails", 3) and _st["ytdlp_dead"])
