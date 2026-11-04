"""The text of a lecture's references, so the teaching lesson (content/lesson.py) is grounded in what they actually say.

    reference_text(src) -> str        one source's text, fetched once and cached in data/cache/refs/ (git-ignored)
    passages(sources) -> [passage]    ~180-word passages with ids "C3#12" (source id # number)
    retrieve(query, passages, k)      the k passages closest to the query (local embedding model, no AI calls)

What is read: arXiv papers (the PDF's text), web pages (the readable text; an index page with little text also reads
up to `max_pages` pages it links to under the same folder, e.g. a book chapter's sections) and PDFs. A source that
cannot be read (paywalled DOI, ISBN only) is skipped and reported. The text is used only to ground the AI's teaching;
check_copying (lesson.py) flags long word-for-word overlaps, so the lesson explains in its own words.
"""
from __future__ import annotations

import hashlib
import io
import re
from urllib.parse import urljoin, urlparse

from profsagent.config import ROOT

CACHE = ROOT / "data" / "cache" / "refs"
UA = {"User-Agent": "ProfsAgent/0.1 (course material; reads open references once and caches them)"}


def _get(url: str):
    import httpx
    r = httpx.get(url, timeout=60, follow_redirects=True, headers=UA)
    r.raise_for_status()
    return r


def _pdf_text(data: bytes) -> str:
    from pypdf import PdfReader
    return "\n".join(p.extract_text() or "" for p in PdfReader(io.BytesIO(data)).pages)


def _html_text(html: str) -> tuple[str, list[str]]:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    links = [a.get("href") for a in soup.find_all("a") if a.get("href")]
    for t in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
        t.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    return main.get_text("\n"), links


def _fetch(url: str, max_pages: int) -> str:
    if re.search(r"arxiv\.org/abs/", url):
        url = url.replace("/abs/", "/pdf/")
    r = _get(url)
    if "pdf" in r.headers.get("content-type", "") or url.lower().endswith(".pdf"):
        return _pdf_text(r.content)
    text, links = _html_text(r.text)
    if len(text.split()) < 1500 and max_pages:         # an index page: read the pages it links to in the same folder
        base = url.rsplit("/", 1)[0] + "/"
        seen, parts = set(), [text]
        for href in links:
            u = urljoin(url, href).split("#")[0]
            if u.startswith(base) and u != url and u not in seen and urlparse(u).path.endswith((".html", "/")):
                seen.add(u)
                try:
                    parts.append(_html_text(_get(u).text)[0])
                except Exception:  # noqa: BLE001 — one unreadable section does not lose the others
                    continue
                if len(seen) >= max_pages:
                    break
        text = "\n".join(parts)
    return text


def source_url(src: dict) -> str | None:
    u = src.get("url") or ""
    return u if u.startswith("http") and "doi.org" not in u else None


def reference_text(src: dict, max_pages: int = 10) -> str:
    """The source's text (cached by URL); "" when it has no readable URL."""
    url = source_url(src)
    if not url:
        return ""
    CACHE.mkdir(parents=True, exist_ok=True)
    p = CACHE / (hashlib.sha1(url.encode()).hexdigest()[:16] + ".txt")
    if p.exists():
        return p.read_text(encoding="utf-8")
    text = re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", _fetch(url, max_pages))).strip()
    p.write_text(text, encoding="utf-8")
    return text


def passages(texts: dict[str, str], words: int = 180, step: int = 150) -> list[dict]:
    """{source id: text} -> [{id "C3#4", source, text}], overlapping windows so an idea is not cut in half."""
    out = []
    for sid, text in texts.items():
        w = text.split()
        for n, i in enumerate(range(0, max(1, len(w) - 30), step), 1):
            chunk = " ".join(w[i:i + words])
            if len(chunk.split()) >= 40:
                out.append({"id": f"{sid}#{n}", "source": sid, "text": chunk})
    return out


def retrieve(query: str, ps: list[dict], k: int, embed=None, exclude: set[str] = frozenset()) -> list[dict]:
    """The k passages closest to the query, at most 3 from one source so one long book does not crowd out the rest."""
    if embed is None:
        from profsagent.delivery.common import embed
    cand = [p for p in ps if p["id"] not in exclude]
    if not cand:
        return []
    import numpy as np
    sims = embed([p["text"] for p in cand]) @ embed([query])[0]
    out, per = [], {}
    for j in np.argsort(-sims):
        p = cand[int(j)]
        if per.get(p["source"], 0) < 3:
            out.append({**p, "similarity": round(float(sims[j]), 3)})
            per[p["source"]] = per.get(p["source"], 0) + 1
        if len(out) == k:
            break
    return out
