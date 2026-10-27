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


SELF_PUBLISHED = ("createspace", "independentlypublished", "lulu", "kindledirect", "amazondigital", "draft2digital", "smashwords")


def _year_of(s) -> int | None:
    y = re.findall(r"(1[89]\d\d|20\d\d)", str(s or ""))
    return int(y[-1]) if y else None


def best_edition(work_key: str, title: str, author_keys: list[str]) -> dict | None:
    """The newest proper edition of an OpenLibrary work: English (or unstated), the same title, an author of the work, a
    real publisher (no self-published reprints) and an ISBN-13. A work search returns the ISBNs of ALL its editions with the
    FIRST publication year, so taking the first ISBN paired, e.g., a 2017 CreateSpace reprint's ISBN with 1996; the ISBN,
    year and publisher here all describe one edition."""
    j = _cached_get(f"https://openlibrary.org{work_key}/editions.json", {"limit": 100})
    entries = (j or {}).get("entries", [])
    authors = {f"/authors/{k}" for k in author_keys}
    full, short = _n(title)[:30], _n(title.split(":")[0])[:30]
    for want in dict.fromkeys((full, short)):        # the title with its subtitle first, then the main title alone
        best = None
        for e in entries:
            isbn = next((re.sub(r"\D", "", i) for i in e.get("isbn_13") or [] if len(re.sub(r"\D", "", i)) == 13), None)
            year = _year_of(e.get("publish_date"))
            if not isbn or not year or not _n(str(e.get("title", "")) + str(e.get("subtitle") or "")).startswith(want):
                continue
            langs = {x.get("key") for x in e.get("languages") or [] if isinstance(x, dict)}
            if langs and "/languages/eng" not in langs:
                continue
            eauth = {x.get("key") for x in e.get("authors") or [] if isinstance(x, dict)}
            if authors and eauth and not (eauth & authors):
                continue
            pubs = e.get("publishers") or []
            if any(s in _n(p) for p in pubs for s in SELF_PUBLISHED):
                continue
            if best is None or year > best["year"]:
                best = {"isbn": isbn, "year": year, "publisher": pubs[0] if pubs else None, "key": e.get("key")}
        if best:
            return best
    return None


def openlibrary(query: str, limit: int = 3) -> list[dict]:
    j = _cached_get("https://openlibrary.org/search.json",
                    {"q": query, "limit": limit, "fields": "key,title,subtitle,author_name,author_key,first_publish_year,isbn,publisher,edition_count"})
    out = []
    for d in (j or {}).get("docs", [])[:limit]:
        title = d.get("title") + (f": {d['subtitle']}" if d.get("subtitle") else "")
        ed = best_edition(d["key"], title, d.get("author_key") or [])
        base = {"candidate_id": f"OL:{d['key'].split('/')[-1]}", "kind": "book", "title": title, "authors": d.get("author_name", [])[:4],
                "source": "openlibrary", "query": query, "first_published": d.get("first_publish_year")}
        if ed:   # ISBN, year and publisher of one and the same edition (the newest proper one)
            out.append({**base, "year": ed["year"], "publisher": ed["publisher"], "identifier": {"isbn": ed["isbn"]},
                        "url": f"https://openlibrary.org{ed['key']}", "year_note": "year of the edition the ISBN belongs to (newest English edition)"})
        else:    # no edition we can vouch for: no ISBN rather than a mismatched one
            out.append({**base, "year": d.get("first_publish_year"), "publisher": (d.get("publisher") or [None])[0], "identifier": {"isbn": None},
                        "url": f"https://openlibrary.org{d['key']}", "year_note": "first publication year; no edition with a matching ISBN found"})
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
