"""Polite, cached web fetching + HTML→text extraction."""
from __future__ import annotations

import hashlib
import json
import re
import time
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup

from profsagent.config import CACHE

UA = "ProfsAgent-research/0.1 (IIIT-Delhi BTP; course-design research; contact via IIIT-D CSE)"
_client = httpx.Client(timeout=30, follow_redirects=True, headers={"User-Agent": UA})


def domain(url: str) -> str:
    return (urlparse(url).hostname or "").lower().removeprefix("www.")


def domain_matches(url: str, domains: list[str]) -> bool:
    d = domain(url)
    return any(d == x or d.endswith("." + x) for x in domains)


def html_to_text(html: str) -> tuple[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    title = (soup.title.string or "").strip() if soup.title and soup.title.string else ""
    for t in soup(["script", "style", "noscript", "svg", "header", "footer", "nav", "form"]):
        t.decompose()
    text = soup.get_text("\n")
    text = re.sub(r"[ \t\r\f\v]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n", text).strip()
    return title, text


def fetch(url: str, max_age_s: int = 7 * 86400) -> dict:
    """{url, final_url, status, title, text, fetched_at, error}. Cached on disk."""
    cache = CACHE / "web"
    cache.mkdir(parents=True, exist_ok=True)
    p = cache / (hashlib.sha256(url.encode()).hexdigest()[:24] + ".json")
    if p.exists():
        d = json.loads(p.read_text(encoding="utf-8"))
        if time.time() - d.get("fetched_at", 0) < max_age_s:
            return d
    out = {"url": url, "final_url": url, "status": None, "title": "", "text": "", "fetched_at": time.time(), "error": None}
    try:
        r = _client.get(url)
        out["status"], out["final_url"] = r.status_code, str(r.url)
        ctype = r.headers.get("content-type", "")
        if r.status_code == 200 and "html" in ctype:
            out["title"], out["text"] = html_to_text(r.text)
        elif r.status_code == 200 and ("text" in ctype or "xml" in ctype):
            out["text"] = r.text
        elif r.status_code == 200:
            out["error"] = f"unsupported content-type {ctype}"
    except Exception as e:  # noqa: BLE001
        out["error"] = f"{type(e).__name__}: {e}"[:200]
    p.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    time.sleep(0.5)
    return out
