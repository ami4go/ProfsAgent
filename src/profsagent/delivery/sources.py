"""External services used by the delivery aids, each cached on disk and kept within its free quota (integration layer).

  YouTube Data API v3   search (100 units), videos/channels details (1 unit per 50)         YOUTUBE_API_KEY
  Transcripts           youtube-transcript-api, run locally (cloud IPs are blocked by YouTube)
  Web                   readings / practice: Tavily (TAVILY_API_KEY, 1,000/month), then DuckDuckGo (ddgs, no key), then
                        Gemini Google-Search grounding; expert search: Gemini first, then Tavily, DuckDuckGo; polite cached fetch
  Books                 OpenLibrary / Crossref (Phase 1 research.resources)
  Papers, authors       OpenAlex (OPENALEX_API_KEY), DBLP (no key)
  Code / practice       GitHub search (GITHUB_TOKEN optional)
Google Scholar has no API and forbids scraping, so academics get a Scholar *search link* for the professor instead.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
import re
import time
from urllib.parse import quote_plus

import httpx

from profsagent.config import CACHE
from profsagent.delivery.common import Quota, iso_duration_s, rcfg, read_json, write_json
from profsagent.research.fetch import domain, fetch

_http = httpx.Client(timeout=40, follow_redirects=True,
                     headers={"User-Agent": "ProfsAgent/0.2 (IIIT-Delhi BTP; course delivery research)"})


def _cache_path(ns: str, key: str):
    return CACHE / "delivery" / ns / (hashlib.sha256(key.encode()).hexdigest()[:24] + ".json")


def _cached(ns: str, key: str, max_age_days: float, fn):
    """Cache successful results only: a failure (quota, network) must be retried next time, not remembered."""
    p = _cache_path(ns, key)
    d = read_json(p)
    if d is not None and time.time() - d.get("_at", 0) < max_age_days * 86400 and not (isinstance(d["v"], dict) and "error" in d["v"]):
        return d["v"]
    v = fn()
    if not (isinstance(v, dict) and "error" in v):
        write_json(p, {"_at": time.time(), "v": v})
    return v


def _get(url: str, params: dict, tries: int = 3, headers: dict | None = None):
    for i in range(tries):
        try:
            r = _http.get(url, params=params, headers=headers)
            if r.status_code in (429, 500, 502, 503) and i < tries - 1:
                time.sleep(2 * (i + 1))
                continue
            return r
        except httpx.HTTPError:
            if i == tries - 1:
                raise
            time.sleep(2 * (i + 1))
    return None


# ------------------------------------------------------------------ YouTube
class YouTube:
    API = "https://www.googleapis.com/youtube/v3"

    def __init__(self):
        self.key = os.environ.get("YOUTUBE_API_KEY", "")
        self.quota = Quota("youtube", rcfg()["youtube"]["daily_unit_budget"])

    @property
    def ok(self) -> bool:
        return bool(self.key)

    def search(self, query: str, n: int | None = None, long: bool = False) -> list[str]:
        """Video ids for a query (100 units unless cached for 21 days)."""
        n = n or rcfg()["youtube"]["results_per_search"]
        key = f"{query}|{n}|{long}"
        p = _cache_path("yt_search", key)
        if read_json(p) is None and not (self.ok and self.quota.can(100)):
            return []

        def run():
            params = {"part": "id", "q": query, "type": "video", "maxResults": n, "key": self.key, "safeSearch": "strict",
                      "relevanceLanguage": rcfg()["youtube"]["language"], "regionCode": rcfg()["youtube"]["region"],
                      "videoEmbeddable": "true"}
            if long:
                params["videoDuration"] = "long"
            r = _get(f"{self.API}/search", params)
            self.quota.spend(100)
            if r is None or r.status_code != 200:
                return []
            return [i["id"]["videoId"] for i in r.json().get("items", []) if i.get("id", {}).get("videoId")]
        return _cached("yt_search", key, 21, run)

    def videos(self, ids: list[str]) -> dict[str, dict]:
        """Details for video ids (1 unit per 50), cached 7 days per video."""
        out, todo = {}, []
        for v in dict.fromkeys(ids):
            d = read_json(_cache_path("yt_video", v))
            if d and time.time() - d["_at"] < 7 * 86400:
                out[v] = d["v"]
            else:
                todo.append(v)
        for i in range(0, len(todo), 50):
            if not (self.ok and self.quota.can(1)):
                break
            batch = todo[i:i + 50]
            r = _get(f"{self.API}/videos", {"part": "snippet,contentDetails,statistics,status", "id": ",".join(batch), "key": self.key})
            self.quota.spend(1)
            if r is None or r.status_code != 200:
                continue
            got = {}
            for it in r.json().get("items", []):
                sn, cd, stt, st = it.get("snippet", {}), it.get("contentDetails", {}), it.get("statistics", {}), it.get("status", {})
                rr = cd.get("regionRestriction") or {}
                got[it["id"]] = {
                    "id": it["id"], "url": f"https://www.youtube.com/watch?v={it['id']}", "title": sn.get("title", ""),
                    "description": (sn.get("description") or "")[:3000], "channel": sn.get("channelTitle", ""),
                    "channel_id": sn.get("channelId"), "published": sn.get("publishedAt"), "language": sn.get("defaultAudioLanguage") or sn.get("defaultLanguage"),
                    "duration_s": iso_duration_s(cd.get("duration")), "captions": cd.get("caption") == "true",
                    "licence": "Creative Commons (CC BY)" if st.get("license") == "creativeCommon" else "Standard YouTube licence",
                    "embeddable": st.get("embeddable", False), "public": st.get("privacyStatus") == "public",
                    "blocked_in_india": "IN" in rr.get("blocked", []) or (bool(rr.get("allowed")) and "IN" not in rr.get("allowed", [])),
                    "views": int(stt.get("viewCount", 0) or 0), "likes": int(stt["likeCount"]) if stt.get("likeCount") else None,
                    "comments": int(stt["commentCount"]) if stt.get("commentCount") else None,
                    "made_for_kids": st.get("madeForKids", False),
                }
            for v in batch:
                if v in got:
                    write_json(_cache_path("yt_video", v), {"_at": time.time(), "v": got[v]})
                    out[v] = got[v]
        return out

    def channels(self, ids: list[str]) -> dict[str, dict]:
        out, todo = {}, []
        for c in dict.fromkeys(x for x in ids if x):
            d = read_json(_cache_path("yt_channel", c))
            if d and time.time() - d["_at"] < 30 * 86400:
                out[c] = d["v"]
            else:
                todo.append(c)
        for i in range(0, len(todo), 50):
            if not (self.ok and self.quota.can(1)):
                break
            r = _get(f"{self.API}/channels", {"part": "snippet,statistics", "id": ",".join(todo[i:i + 50]), "key": self.key})
            self.quota.spend(1)
            if r is None or r.status_code != 200:
                continue
            for it in r.json().get("items", []):
                v = {"id": it["id"], "title": it["snippet"].get("title"), "subscribers": int(it["statistics"].get("subscriberCount", 0) or 0),
                     "country": it["snippet"].get("country"), "description": (it["snippet"].get("description") or "")[:500]}
                write_json(_cache_path("yt_channel", it["id"]), {"_at": time.time(), "v": v})
                out[it["id"]] = v
        return out


# YouTube blocks an IP that asks for many transcripts quickly (IpBlocked after ~60 in 10 minutes, 2026-10-25), so
# requests are spaced out, and after the first block none are sent for the rest of the process.
_tx = {"blocked": None, "last": 0.0}
BLOCKED = ("IpBlocked", "RequestBlocked", "TooManyRequests")


def transcripts_blocked() -> str | None:
    """Time (HH:MM) YouTube started blocking transcript requests in this process, or None."""
    return _tx["blocked"]


def transcript(video_id: str) -> list[dict] | None:
    """[{start, dur, text}] or None. Cached 90 days. Works from a home/campus network; cloud IPs are blocked."""
    def run():
        if _tx["blocked"]:
            return {"error": "skipped: transcripts blocked"}
        cfg = rcfg()["transcripts"]
        wait = _tx["last"] + cfg.get("min_interval_s", 1.5) + random.uniform(0, cfg.get("jitter_s", 1.0)) - time.time()
        if wait > 0:
            time.sleep(wait)
        _tx["last"] = time.time()
        try:
            from youtube_transcript_api import YouTubeTranscriptApi
            t = YouTubeTranscriptApi().fetch(video_id, languages=["en", "en-US", "en-GB", "en-IN"])
            return [{"start": s.start, "dur": s.duration, "text": s.text} for s in t]
        except Exception as e:  # noqa: BLE001 — no captions, disabled, blocked: the caller falls back to metadata
            if type(e).__name__ in BLOCKED:
                _tx["blocked"] = time.strftime("%H:%M")
            return {"error": f"{type(e).__name__}"}
    v = _cached("transcript", video_id, 90, run)
    return None if isinstance(v, dict) else v


# ------------------------------------------------------------------ web pages (readings, practice, practitioners)
def grounded_pages(llm, query: str, domains: list[str] | None, kind: str) -> list[dict]:
    """Find pages for readings / practice: Tavily, then DuckDuckGo, then Gemini Google-Search grounding.
    Returns [{url, title, type}] (each source cached 21 days)."""
    dom = f" Prefer pages on these sites: {', '.join(domains)}." if domains else ""
    instruction = (f"You are finding free, publicly readable {kind} for a university lecture. Search the web and list "
                   "specific pages (an article, tutorial, book chapter, lecture notes page, documentation page, notebook or "
                   "exercise set), not home pages, course catalogues or paywalled pages." + dom +
                   " Answer with one line per page: URL | title | type (article, tutorial, chapter, notes, docs, notebook, "
                   "exercises, paper). Up to 8 lines. If nothing suitable, answer NONE.")

    def run():
        try:
            res = llm.grounded_search(query, instruction)
        except Exception as e:  # noqa: BLE001
            return {"error": str(e)[:200]}
        out = []
        for line in res["text"].splitlines():
            m = re.search(r"https?://[^\s|)\]>\"'`]+", line)       # a link in `backticks` must not keep the backtick
            if not m:
                continue
            parts = [p.strip(" *-") for p in line.split("|")]
            out.append({"url": m.group(0).rstrip(".,;"), "title": parts[1] if len(parts) > 1 else "",
                        "type": (parts[2] if len(parts) > 2 else "article").lower()})
        for s in res.get("sources", []):
            if s.get("uri"):
                out.append({"url": s["uri"], "title": s.get("title") or "", "type": "article", "redirect": True})
        return out
    # Order Tavily -> DuckDuckGo -> Gemini (measured 2026-10-28 on 7 reading queries: pages that open and cover the
    # topic 75% / 65% / 40%; Gemini writes many invented deep links), and Gemini's small daily quota is kept for experts.
    t = web_search(query)
    if t:
        return [{"url": x["url"], "title": x["title"], "type": "article"} for x in t]
    v = _cached("grounded", f"{kind}|{query}|{domains}", 21, run)
    if isinstance(v, dict):
        return []
    return [{**x, "url": x["url"].rstrip("`.,;")} for x in v]   # results cached before the backtick fix


def tavily(query: str, n: int = 8) -> list[dict] | None:
    """Tavily web search (free 1,000 searches/month, TAVILY_API_KEY). [{url, title, content}] or None if unavailable."""
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        return None

    def run():
        try:
            r = _http.post("https://api.tavily.com/search", headers={"Authorization": f"Bearer {key}"},
                           json={"api_key": key, "query": query, "max_results": n, "search_depth": "basic", "include_answer": False})
            if r.status_code != 200:
                return {"error": f"HTTP {r.status_code}"}
            return [{"url": x["url"], "title": x.get("title") or "", "content": (x.get("content") or "")[:1200]} for x in r.json().get("results", [])]
        except httpx.HTTPError as e:
            return {"error": type(e).__name__}
    v = _cached("tavily", f"{query}|{n}", 21, run)
    return None if isinstance(v, dict) else v


def duckduckgo(query: str, n: int = 8) -> list[dict] | None:
    """DuckDuckGo web search through the ddgs package: no key and no quota, but rate-limited if hammered."""
    def run():
        try:
            from ddgs import DDGS
            time.sleep(1.0)
            return [{"url": x["href"], "title": x.get("title") or "", "content": (x.get("body") or "")[:1200]}
                    for x in DDGS().text(query, max_results=n) if x.get("href")]
        except Exception as e:  # noqa: BLE001 — not installed, rate-limited, network
            return {"error": type(e).__name__}
    v = _cached("ddg", f"{query}|{n}", 21, run)
    return None if isinstance(v, dict) else v


def web_search(query: str, n: int = 8) -> list[dict] | None:
    """[{url, title, content, via}] from Tavily, or DuckDuckGo when Tavily has no key, is out of credit or found nothing."""
    for name, fn in (("tavily", tavily), ("duckduckgo", duckduckgo)):
        t = fn(query, n)
        if t:
            return [{**x, "via": name} for x in t]
    return None


def grounded_text(llm, query: str, instruction: str) -> dict | None:
    """{text, sources} from a Google-Search-grounded answer, cached 21 days; None when search is unavailable
    (the free grounding model has a small daily quota shared across keys of one Google project)."""
    def run():
        try:
            r = llm.grounded_search(query, instruction)
            return {"text": r["text"], "sources": r.get("sources", [])}
        except Exception as e:  # noqa: BLE001
            return {"error": f"{type(e).__name__}: {str(e)[:150]}"}
    v = _cached("grounded_text", f"{instruction[:80]}|{query}", 21, run)
    if "error" not in v:
        return v
    t = web_search(query)                 # fallback when the Gemini search quota is used up
    if t:
        return {"text": "\n\n".join(f"{x['title']} — {x['url']}\n{x['content']}" for x in t),
                "sources": [{"uri": x["url"], "title": x["title"], "snippet": x["content"]} for x in t], "via": t[0]["via"]}
    return None


def links_in(text: str) -> list[str]:
    """Web links in a video description (creators often link the docs, posts and repos they used)."""
    skip = ("youtube.com", "youtu.be", "twitter.com", "x.com", "instagram.com", "facebook.com", "tiktok.com", "discord",
            "patreon.com", "linkedin.com", "bit.ly", "amzn.to", "t.me", "linktr.ee", "buymeacoffee", "ko-fi", "spotify.com", "apple.com/podcast")
    out = []
    for u in re.findall(r"https?://[^\s)\]>\"'`]+", text or ""):
        u = u.rstrip(".,;")
        if not any(x in u for x in skip):
            out.append(u)
    return list(dict.fromkeys(out))


def page(url: str) -> dict:
    """{url, final_url, status, title, text} — Phase 1's cached fetcher (follows grounding redirects)."""
    return fetch(url, max_age_s=14 * 86400)


def url_alive(url: str) -> tuple[bool, int | None]:
    try:
        r = _http.head(url)
        if r.status_code in (403, 405, 400):   # many sites refuse HEAD
            r = _http.get(url)
        return r.status_code < 400, r.status_code
    except httpx.HTTPError:
        return False, None


# ------------------------------------------------------------------ papers and academics
class OpenAlex:
    API = "https://api.openalex.org"

    def __init__(self):
        self.key = os.environ.get("OPENALEX_API_KEY", "")

    def _p(self, params: dict) -> dict:
        return {**params, **({"api_key": self.key} if self.key else {})}

    def works(self, query: str, n: int = 50, min_year: int = 2012, review_only: bool = False, country: str | None = None) -> list[dict]:
        def run():
            flt = f"from_publication_date:{min_year}-01-01" + (",type:review" if review_only else "") + \
                  (f",authorships.institutions.country_code:{country}" if country else "")
            r = _get(f"{self.API}/works", self._p({"search": query, "per_page": min(n, 100), "filter": flt,
                                                     "select": "id,doi,title,publication_year,cited_by_count,authorships,open_access,primary_location,type"}))
            if r is None or r.status_code != 200:
                return []
            out = []
            for w in r.json().get("results", []):
                loc = w.get("primary_location") or {}
                out.append({"id": w["id"], "doi": w.get("doi"), "title": w.get("title") or "", "year": w.get("publication_year"),
                            "cited_by": w.get("cited_by_count", 0), "type": w.get("type"),
                            "open_access": (w.get("open_access") or {}).get("is_oa"), "oa_url": (w.get("open_access") or {}).get("oa_url"),
                            "venue": ((loc.get("source") or {}) or {}).get("display_name"),
                            "venue_id": ((loc.get("source") or {}) or {}).get("id"),
                            "authors": [{"id": a["author"]["id"], "name": a["author"]["display_name"], "orcid": a["author"].get("orcid"),
                                         "institutions": [{"name": i.get("display_name"), "country": i.get("country_code"), "type": i.get("type")}
                                                          for i in a.get("institutions", [])]}
                                        for a in w.get("authorships", [])]})
            return out
        return _cached("oa_works", f"v2|{query}|{n}|{min_year}|{review_only}|{country}", 14, run)

    def source(self, source_id: str | None) -> dict | None:
        """Venue reputation: OpenAlex source record (h-index, 2-year mean citedness, DOAJ), cached 90 days."""
        if not source_id:
            return None
        sid = source_id.rsplit("/", 1)[-1]

        def run():
            r = _get(f"{self.API}/sources/{sid}", self._p({}))
            if r is None or r.status_code != 200:
                return {"error": "unavailable"}
            j = r.json()
            st = j.get("summary_stats") or {}
            return {"name": j.get("display_name"), "h_index": st.get("h_index"), "citedness": st.get("2yr_mean_citedness"),
                    "type": j.get("type"), "in_doaj": j.get("is_in_doaj"), "host": j.get("host_organization_name")}
        v = _cached("oa_source", sid, 90, run)
        return None if "error" in v else v

    def find_author(self, name: str, institution_hint: str) -> dict | None:
        """An author record by name whose last known institution matches the hint (e.g. 'Indraprastha')."""
        def run():
            r = _get(f"{self.API}/authors", self._p({"search": name, "per_page": 10}))
            if r is None or r.status_code != 200:
                return {"error": "unavailable"}
            for a in r.json().get("results", []):
                insts = " ".join(i.get("display_name", "") for i in (a.get("last_known_institutions") or []))
                if institution_hint.lower() in insts.lower():
                    return {"id": a["id"]}
            return {"none": True}
        v = _cached("oa_find_author", f"{name}|{institution_hint}", 60, run)
        return None if ("error" in v or "none" in v) else self.author(v["id"])

    def works_by(self, author_id: str, query: str, n: int = 10) -> list[dict]:
        aid = author_id.rsplit("/", 1)[-1]

        def run():
            r = _get(f"{self.API}/works", self._p({"filter": f"author.id:{aid}", "search": query, "per_page": n,
                                                     "select": "id,doi,title,publication_year,cited_by_count,primary_location"}))
            if r is None or r.status_code != 200:
                return {"error": "unavailable"}
            return [{"id": w["id"], "doi": w.get("doi"), "title": w.get("title") or "", "year": w.get("publication_year"),
                     "cited_by": w.get("cited_by_count", 0), "venue": ((w.get("primary_location") or {}).get("source") or {}).get("display_name"),
                     "venue_id": ((w.get("primary_location") or {}).get("source") or {}).get("id")} for w in r.json().get("results", [])]
        v = _cached("oa_works_by", f"{aid}|{query}|{n}", 30, run)
        return [] if isinstance(v, dict) else v

    def author(self, author_id: str) -> dict | None:
        aid = author_id.rsplit("/", 1)[-1]

        def run():
            r = _get(f"{self.API}/authors/{aid}", self._p({}))
            if r is None or r.status_code != 200:
                return None
            a = r.json()
            inst = (a.get("last_known_institutions") or [{}])[0] if a.get("last_known_institutions") else {}
            return {"id": a["id"], "name": a["display_name"], "orcid": a.get("orcid"), "works_count": a.get("works_count", 0),
                    "cited_by": a.get("cited_by_count", 0), "h_index": (a.get("summary_stats") or {}).get("h_index"),
                    "two_year_citedness": (a.get("summary_stats") or {}).get("2yr_mean_citedness"),
                    "institution": inst.get("display_name"), "country": inst.get("country_code"), "inst_type": inst.get("type"),
                    "topics": [t.get("display_name") for t in (a.get("topics") or [])[:10]],
                    "counts_by_year": {c["year"]: c["works_count"] for c in (a.get("counts_by_year") or [])}}
        return _cached("oa_author", aid, 30, run)


def dblp_author(name: str) -> dict | None:
    """DBLP person record for a name (CS bibliography), or None."""
    def run():
        r = _get("https://dblp.org/search/author/api", {"q": name, "format": "json", "h": 3})
        if r is None or r.status_code != 200:
            return None
        hits = ((r.json().get("result") or {}).get("hits") or {}).get("hit") or []
        for h in hits:
            info = h.get("info", {})
            if info.get("author", "").lower().split(" 0")[0] == name.lower():
                return {"name": info["author"], "url": info.get("url")}
        return None
    return _cached("dblp_author", name.lower(), 60, run)


def scholar_search_url(name: str, affiliation: str | None = None) -> str:
    """A Google Scholar author-search link for the professor to click (Scholar has no API and forbids scraping)."""
    return "https://scholar.google.com/citations?view_op=search_authors&mauthors=" + quote_plus(f"{name} {affiliation or ''}".strip())


# ------------------------------------------------------------------ GitHub
def github_repos(query: str, n: int = 8) -> list[dict]:
    tok = os.environ.get("GITHUB_TOKEN")

    def run():
        r = _get("https://api.github.com/search/repositories", {"q": query, "sort": "stars", "order": "desc", "per_page": n},
                 headers={"Accept": "application/vnd.github+json", **({"Authorization": f"Bearer {tok}"} if tok else {})})
        if r is None or r.status_code != 200:
            return []
        return [{"url": it["html_url"], "name": it["full_name"], "description": it.get("description") or "", "stars": it.get("stargazers_count", 0),
                 "updated": it.get("pushed_at"), "licence": (it.get("license") or {}).get("spdx_id"), "owner": it["owner"]["login"],
                 "owner_type": it["owner"]["type"], "owner_url": it["owner"]["html_url"], "topics": it.get("topics", [])}
                for it in r.json().get("items", [])]
    return _cached("gh_repos", f"{query}|{n}", 14, run)


def github_user(login: str) -> dict | None:
    tok = os.environ.get("GITHUB_TOKEN")

    def run():
        r = _get(f"https://api.github.com/users/{login}", {}, headers={"Accept": "application/vnd.github+json",
                                                                         **({"Authorization": f"Bearer {tok}"} if tok else {})})
        if r is None or r.status_code != 200:
            return None
        u = r.json()
        return {"login": u["login"], "name": u.get("name"), "company": u.get("company"), "location": u.get("location"),
                "bio": u.get("bio"), "followers": u.get("followers", 0), "blog": u.get("blog"), "url": u["html_url"]}
    return _cached("gh_user", login, 30, run)


def domain_of(url: str) -> str:
    return domain(url)


def dumps(x) -> str:
    return json.dumps(x, ensure_ascii=False, default=str)
