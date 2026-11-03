"""Simulations on trusted sites, suggested as links only (decisions.md 27; docs/05 §5).

The professor opens the link, judges it and approves or rejects it; we do not copy, embed or check these simulations.
The sites are listed in simulations/external/sources.yaml. PhET and Falstad publish their lists, so `build()` downloads
them; the others are written there by hand. The result is simulations/external/index.json (committed, so nobody has
to download anything to use the app):

    python scripts/sims.py external        rebuild index.json from the sites (a few seconds; needs the internet)

    entries() -> [{"id": "ext:<site>:<id>", "site", "site_name", "title", "url", "summary", "topics"}]
"""
from __future__ import annotations

import html
import json
import re
import time
import urllib.request
from functools import lru_cache

import yaml

from profsagent.sims.catalogue import SIMS

DIR = SIMS / "external"
SOURCES = DIR / "sources.yaml"
INDEX = DIR / "index.json"
FOUND = DIR / "found.json"          # pages a professor approved from a request's web search (websearch.py), kept for everyone
UA = "ProfsAgent/0.1 (IIIT-Delhi course design research)"
PHET_META = "https://phet.colorado.edu/services/metadata/1.3/simulations?format=json&type=html&locale=en"
FALSTAD_APPLETS = "https://www.falstad.com/mathphysics.html"
FALSTAD_CIRCUITS = "https://www.falstad.com/circuit/e-index.html"


def _get(url: str, timeout: int = 60) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 - fixed https URLs above
        return r.read().decode("utf-8", errors="replace")


def _text(s: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")[:60]


# ------------------------------------------------------------------ parsers (pure; tested on saved snippets)
def parse_phet(meta: dict, min_grade: int = 3) -> list[dict]:
    """PhET's metadata service: title, description, learning goals and keywords of each HTML simulation.
    Grade levels run 0 (primary) to 3 (university); we keep the ones PhET marks as university level."""
    kw = {str(k): ((v.get("strings") or {}).get("en") or "") for k, v in (meta.get("keywords") or {}).items()}
    out = []
    for p in meta.get("projects") or []:
        for s in p.get("simulations") or []:
            loc = (s.get("localizedSimulations") or {}).get("en")
            if not loc or (s.get("highGradeLevel") or 0) < min_grade:
                continue
            topics = [kw[str(i)] for i in s.get("keywordIds") or [] if kw.get(str(i))]
            out.append({"id": s.get("name") or _slug(loc["title"]), "title": loc["title"],
                        "url": "https://phet.colorado.edu" + (loc.get("simPageUrl") or f"/en/simulations/{s.get('name')}"),
                        "summary": _text(loc.get("description"))[:300], "topics": list(dict.fromkeys(topics))[:15],
                        "goals": _text((loc.get("learningGoals") or "").replace("<br/>", ". "))[:400]})
    return out


def parse_falstad_applets(page: str) -> list[dict]:
    """falstad.com/mathphysics.html: sections (<h2>) of applets, each a title link and a one-line description."""
    out, section = [], ""
    for m in re.finditer(r"<h2>(.*?)</h2>|<big><b>\s*<a href=\"([^\"]+)\">(.*?)</a>\s*</b></big>\s*<br>\s*<small>(.*?)</small>", page, re.S | re.I):
        if m.group(1) is not None:
            section = _text(m.group(1))
            continue
        href, title, desc = m.group(2), _text(m.group(3)), _text(m.group(4))
        if href.startswith("http") and "falstad.com" not in href:
            continue
        url = href if href.startswith("http") else "https://www.falstad.com/" + href.lstrip("/")
        out.append({"id": _slug(href.strip("/").split("/")[-1] or title), "title": re.sub(r"\s+Applet$", "", title), "url": url,
                    "summary": desc, "topics": [section] if section else []})
    return out


def parse_falstad_circuits(page: str) -> list[dict]:
    """falstad.com/circuit/e-index.html: circuit examples under bold section names (Basics, Op-Amps, Flip-Flops…)."""
    out, section = [], ""
    for m in re.finditer(r"<b>(.*?)</b>|<a href=\"(e-[^\"]+\.html)\">(.*?)</a>", page, re.S | re.I):
        if m.group(1) is not None:
            section = _text(m.group(1))
            continue
        title = _text(m.group(3))
        out.append({"id": "circuit-" + _slug(m.group(2)[2:-5]), "title": f"Circuit: {title}", "url": "https://www.falstad.com/circuit/" + m.group(2),
                    "summary": f"Falstad circuit simulator example ({section}): {title}; change the parts and watch the currents and voltages." if section
                    else f"Falstad circuit simulator example: {title}.", "topics": [x for x in (section, "electronic circuits") if x]})
    seen, uniq = set(), []
    for e in out:
        if e["id"] not in seen:
            seen.add(e["id"])
            uniq.append(e)
    return uniq


# ------------------------------------------------------------------ the index
_src = {"mtime": None, "data": None}


def sources() -> dict:
    mt = SOURCES.stat().st_mtime
    if _src["mtime"] != mt:
        _src.update(mtime=mt, data=yaml.safe_load(SOURCES.read_text(encoding="utf-8")))
    return _src["data"]


def build(fetch=_get) -> dict:
    """Download PhET's and Falstad's lists, add the hand-written ones, and write index.json. Returns a summary."""
    src = sources()
    sites = src["sites"]
    by_site: dict[str, list[dict]] = {}
    by_site["phet"] = parse_phet(json.loads(fetch(PHET_META)))
    by_site["falstad"] = parse_falstad_applets(fetch(FALSTAD_APPLETS)) + parse_falstad_circuits(fetch(FALSTAD_CIRCUITS))
    for site, rows in (src.get("curated") or {}).items():
        by_site.setdefault(site, []).extend(rows)
    entries = []
    for site, rows in by_site.items():
        for r in rows:
            entries.append({"id": f"ext:{site}:{r['id']}", "site": site, "site_name": sites[site]["name"], "title": r["title"], "url": r["url"],
                            "summary": r.get("summary") or "", "topics": list(r.get("topics") or []), "goals": r.get("goals") or ""})
    ids = [e["id"] for e in entries]
    assert len(ids) == len(set(ids)), "duplicate ids in the external index"
    out = {"built_at": time.strftime("%Y-%m-%d %H:%M"), "sites": sites, "entries": entries}
    INDEX.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    entries_cache.cache_clear()
    return {s: len(v) for s, v in by_site.items()}


@lru_cache(maxsize=2)
def entries_cache(mtime: float, found_mtime: float = 0.0) -> tuple[dict, ...]:
    out = json.loads(INDEX.read_text(encoding="utf-8")).get("entries") or [] if INDEX.exists() else []
    if FOUND.exists():
        out = out + (json.loads(FOUND.read_text(encoding="utf-8")) or [])
    return tuple(out)


def _mt(p) -> float:
    return p.stat().st_mtime if p.exists() else 0.0


def entries() -> list[dict]:
    return list(entries_cache(_mt(INDEX), _mt(FOUND)))


def add_found(url: str, title: str, summary: str, site_name: str, topic: str, request_id: str, by: str = "Professor") -> str:
    """Keep a page a professor approved from a web search, so it is suggested for other lectures too. Returns its id."""
    import hashlib
    rows = json.loads(FOUND.read_text(encoding="utf-8")) if FOUND.exists() else []
    for r in rows:
        if r["url"] == url:
            if topic and topic not in r["topics"]:
                r["topics"].append(topic)
            FOUND.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
            return r["id"]
    base = _slug(re.sub(r"^https?://(www\.)?", "", url))[:60]
    ext_id = f"ext:web:{base}-{hashlib.sha1(url.encode()).hexdigest()[:6]}"
    rows.append({"id": ext_id, "site": "web", "site_name": site_name, "title": title, "url": url, "summary": summary, "topics": [topic] if topic else [],
                 "goals": "", "found_for": request_id, "approved_by": by, "at": time.strftime("%Y-%m-%d %H:%M")})
    FOUND.parent.mkdir(parents=True, exist_ok=True)
    FOUND.write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    return ext_id


def get(ext_id: str) -> dict | None:
    return next((e for e in entries() if e["id"] == ext_id), None)


def shows_code(e: dict) -> bool:
    """The simulation shows the algorithm's code beside it (its own flag, or its site's in sources.yaml)."""
    if "shows_code" in e:
        return bool(e["shows_code"])
    return bool(((sources().get("sites") or {}).get(e.get("site")) or {}).get("shows_code"))


def text_for_matching(e: dict) -> list[str]:
    """What a lecture topic is compared with: the title, and the title with its topics."""
    return [e["title"], e["title"] + ": " + ", ".join(e["topics"][:8])]
