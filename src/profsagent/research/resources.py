"""Resource candidates from bibliographic APIs + deterministic verification (V15).

Candidates always come from an API record (OpenLibrary for books, Crossref for papers), never from model
memory. G10 selects among them; `verify_pick` then checks the selection against the candidate record.
"""
from __future__ import annotations

import hashlib
import json
import re
import time

import httpx

from profsagent.config import CACHE

_c = httpx.Client(timeout=30, follow_redirects=True, headers={"User-Agent": "ProfsAgent/0.1 (IIIT-Delhi BTP research)"})


def _cached_get(url: str, params: dict) -> dict | None:
    d = CACHE / "biblio"
    d.mkdir(parents=True, exist_ok=True)
    p = d / (hashlib.sha256((url + json.dumps(params, sort_keys=True)).encode()).hexdigest()[:24] + ".json")
    if p.exists():
        return json.loads(p.read_text(encoding="utf-8"))
    try:
        r = _c.get(url, params=params)
        if r.status_code != 200:
            return None
        j = r.json()
    except Exception:  # noqa: BLE001
        return None
    p.write_text(json.dumps(j), encoding="utf-8")
    time.sleep(0.3)
    return j


def openlibrary(query: str, limit: int = 3) -> list[dict]:
    j = _cached_get("https://openlibrary.org/search.json",
                    {"q": query, "limit": limit, "fields": "key,title,subtitle,author_name,first_publish_year,isbn,publisher,edition_count"})
    out = []
    for d in (j or {}).get("docs", [])[:limit]:
        isbns = d.get("isbn") or []
        isbn13 = next((i for i in isbns if len(i) == 13), isbns[0] if isbns else None)
        out.append({"candidate_id": f"OL:{d['key'].split('/')[-1]}", "kind": "book",
                    "title": d.get("title") + (f": {d['subtitle']}" if d.get("subtitle") else ""),
                    "authors": d.get("author_name", [])[:4], "year": d.get("first_publish_year"),
                    "publisher": (d.get("publisher") or [None])[0], "identifier": {"isbn": isbn13},
                    "url": f"https://openlibrary.org{d['key']}", "source": "openlibrary", "query": query,
                    "year_note": "first_publish_year (edition years vary)"})
    return out


def crossref(query: str, limit: int = 3) -> list[dict]:
    j = _cached_get("https://api.crossref.org/works", {"query.bibliographic": query, "rows": limit,
                                                        "select": "DOI,title,author,issued,container-title,type"})
    out = []
    for it in ((j or {}).get("message") or {}).get("items", [])[:limit]:
        yr = ((it.get("issued") or {}).get("date-parts") or [[None]])[0][0]
        out.append({"candidate_id": f"DOI:{it['DOI']}", "kind": it.get("type"), "title": (it.get("title") or [""])[0],
                    "authors": [f"{a.get('given', '')} {a.get('family', '')}".strip() for a in it.get("author", [])[:4]],
                    "year": yr, "venue": (it.get("container-title") or [None])[0], "identifier": {"doi": it["DOI"]},
                    "url": f"https://doi.org/{it['DOI']}", "source": "crossref", "query": query})
    return out


def _n(s) -> str:
    return re.sub(r"[^a-z0-9]", "", str(s or "").lower())


def verify_pick(pick: dict, candidates: dict[str, dict]) -> dict:
    """Compare a G10 selection to its API candidate. Returns {verified, problems[]}."""
    c = candidates.get(pick.get("candidate_id"))
    if not c:
        return {"verified": False, "problems": ["candidate_id not in retrieved candidates"]}
    probs = []
    if _n(pick.get("title"))[:40] != _n(c.get("title"))[:40]:
        probs.append(f"title mismatch: {pick.get('title')!r} vs {c.get('title')!r}")
    if pick.get("year") and c.get("year") and int(pick["year"]) != int(c["year"]):
        probs.append(f"year mismatch: {pick.get('year')} vs {c.get('year')}")
    pa = {_n(a.split()[-1]) for a in pick.get("authors", []) if a}
    ca = {_n(a.split()[-1]) for a in c.get("authors", []) if a}
    if pa and ca and not (pa & ca):
        probs.append("author mismatch")
    return {"verified": not probs, "problems": probs}
