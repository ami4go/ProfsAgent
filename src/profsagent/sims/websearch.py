"""Find existing simulations for a request before the machine builds one (decisions.md 29; Amit: "visit the top 3-4 pages,
then only fall back to auto-creation").

    find(req, work) -> [candidate]       best first; [] when nothing fits (then the auto-build starts)

Where it looks, cheapest first:
  1. our catalogue and the saved links to trusted sites (simulations/external/index.json + found.json), with the local model;
  2. a web search restricted to trusted sites (Tavily include_domains; simulations/external/sources.yaml "search"), then an
     open web search (Tavily, or DuckDuckGo when Tavily has no key or credit) — 2 searches per request, cached 21 days;
  3. the top pages are opened in Chrome: the page must load, have controls or a drawing area (canvas, sliders, buttons…)
     and be about the topic (local model). A screenshot of each goes to the professor, who approves or rejects.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import re
import time
from pathlib import Path
from urllib.parse import urlparse

import httpx

from profsagent.config import CACHE
from profsagent.sims import external as X

VISIT = 3                 # pages opened from each web search, trusted sites and the open web (Amit: "at least visit top 3-4 pages")
SHOW = 4                  # candidates shown to the professor
REL_MIN = 0.40            # topic similarity of a visited page (title + opening text) to keep it
SKIP = re.compile(r"(wikipedia\.org|youtube\.com|youtu\.be|facebook\.com|twitter\.com|x\.com|instagram\.com|linkedin\.com|reddit\.com|quora\.com|"
                  r"stackoverflow\.com|medium\.com|amazon\.|coursera\.org|udemy\.com|scribd\.com|slideshare\.net|\.pdf($|\?))", re.I)


def _search_cfg() -> dict:
    return X.sources().get("search") or {}


def site_name(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    names = _search_cfg().get("names") or {}
    for dom, name in names.items():
        if host == dom or host.endswith("." + dom):
            return name
    return host


def site_shows_code(url: str) -> bool:
    """A trusted site whose simulations show their code (sources.yaml sites: shows_code), e.g. VisuAlgo, Python Tutor."""
    host = urlparse(url).netloc.lower().removeprefix("www.")
    for site in (X.sources().get("sites") or {}).values():
        h = urlparse(site.get("home") or "").netloc.lower().removeprefix("www.")
        if site.get("shows_code") and h and (host == h or host.endswith("." + h)):
            return True
    return False


def trusted(url: str) -> bool:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    return any(host == d or host.endswith("." + d) for d in _search_cfg().get("domains") or [])


# ------------------------------------------------------------------ web search (Tavily; DuckDuckGo as the fallback)
def _cache(key: str) -> Path:
    return CACHE / "sims_web" / (hashlib.sha256(key.encode()).hexdigest()[:24] + ".json")


def tavily(query: str, domains: list[str] | None = None, n: int = 6) -> list[dict] | None:
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        return None
    ck = _cache(f"tavily|{query}|{domains}|{n}")
    if ck.exists() and time.time() - ck.stat().st_mtime < 21 * 86400:
        return json.loads(ck.read_text(encoding="utf-8"))
    body = {"query": query, "max_results": n, "search_depth": "basic", "include_answer": False}
    if domains:
        body["include_domains"] = domains
    try:
        r = httpx.post("https://api.tavily.com/search", headers={"Authorization": f"Bearer {key}"}, json=body, timeout=40)
    except httpx.HTTPError:
        return None
    if r.status_code != 200:
        return None
    out = [{"url": x["url"], "title": x.get("title") or "", "content": (x.get("content") or "")[:800], "score": x.get("score") or 0, "via": "tavily"}
           for x in r.json().get("results", [])]
    ck.parent.mkdir(parents=True, exist_ok=True)
    ck.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    return out


def web(query: str, domains: list[str] | None = None) -> list[dict]:
    t = tavily(query, domains)
    if t is not None:
        return t
    try:                                    # no Tavily key or credit: DuckDuckGo through the delivery module's cached helper
        from profsagent.delivery.sources import duckduckgo
        q = query + (" (" + " OR ".join(f"site:{d}" for d in domains[:6]) + ")" if domains else "")
        return [{**x, "score": 0.5, "via": "duckduckgo"} for x in (duckduckgo(q, 6) or [])]
    except Exception:  # noqa: BLE001
        return []


# ------------------------------------------------------------------ visiting pages
VISIT_JS = r"""
() => {
  const vis = e => { const r = e.getBoundingClientRect(); return r.width > 40 && r.height > 20; };
  const VIDEO = /youtube|youtu\.be|vimeo|dailymotion/i;     // a video is not a simulation
  const big = sel => [...document.querySelectorAll(sel)].filter(e => { const r = e.getBoundingClientRect(); return r.width > 150 && r.height > 100 && !VIDEO.test(e.src || ''); }).length;
  const main = document.querySelector('main, #main, .main, article') || document.body;
  const text = (document.body.innerText || '').replace(/\s+/g, ' ').trim();
  const meta = (document.querySelector('meta[name="description"]') || {}).content || '';
  const heads = [...document.querySelectorAll('h1, h2')].map(h => (h.innerText || '').trim()).filter(Boolean).slice(0, 6).join(' | ');
  // a code or pseudocode panel (3+ lines that read like code), as VisuAlgo, Python Tutor and our step-by-step pages have
  const codeLike = /\b(for|while|if|else|return|def|function|int|void|let|var|end|do|then|repeat|until)\b|==|<=|>=|:=|\+=/;
  const code = [...document.querySelectorAll('pre, code, ol.code, .code, [class*="pseudo" i], [class*="codetrace" i], [id*="code" i]')]
    .filter(e => { const r = e.getBoundingClientRect(); const t = (e.innerText || '').trim(); return r.width > 80 && r.height > 30 && t.split('\n').length >= 3 && codeLike.test(t); }).length;
  return { title: document.title || '', meta, heads, code, text: text.slice(0, 2500),
           canvas: big('canvas'), svg: big('svg'), iframe: big('iframe'),
           ranges: [...main.querySelectorAll('input[type=range]')].filter(vis).length,
           buttons: [...main.querySelectorAll('button, input[type=button], input[type=submit], [role=button]')].filter(vis).length,
           inputs: [...main.querySelectorAll('input[type=text], input[type=number], select, textarea')].filter(vis).length,
           words: (text.match(/\b(simulat\w*|interactive|visuali[sz]\w*|animat\w*|applet|virtual lab|drag|click|step)\b/gi) || []).length };
}
"""


FOLLOW_JS = r"""
(prefix) => {
  const links = [...document.querySelectorAll('a[href]')].filter(a => a.href.startsWith(prefix) && a.href.split('#')[0] !== location.href.split('#')[0]);
  for (const rx of [/^\s*(simulation|simulator|start simulation|launch simulation)\s*$/i, /^\s*(demo|interactive demo|animation)\s*$/i, /^\s*(practice|try it|launch)\s*$/i]) {
    const a = links.find(a => rx.test(a.innerText || ''));
    if (a) return a.href;
  }
  return null;
}
"""


def measure(pg) -> dict:
    """The page's numbers, adding the controls inside embedded frames (many simulations live in an iframe)."""
    rec = pg.evaluate(VISIT_JS)
    for fr in pg.frames[1:6]:
        if re.search(r"youtube|youtu\.be|vimeo|dailymotion", fr.url or "", re.I):
            continue
        try:
            sub = fr.evaluate(VISIT_JS)
        except Exception:  # noqa: BLE001 - a frame that went away or cannot be read
            continue
        for k in ("canvas", "svg", "ranges", "buttons", "inputs", "words", "code"):
            rec[k] = rec.get(k, 0) + sub.get(k, 0)
        if len(rec.get("text", "")) < 400:
            rec["text"] = (rec.get("text", "") + " " + sub.get("text", ""))[:2500]
    return rec


def visit(urls: list[str], shots: Path, timeout_s: int = 25) -> list[dict]:
    """Open each page in Chrome (downloads off), wait for it to draw, measure it and take a screenshot."""
    from playwright.sync_api import sync_playwright
    shots.mkdir(parents=True, exist_ok=True)
    out = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome")
        ctx = b.new_context(viewport={"width": 1280, "height": 800}, accept_downloads=False)
        for i, url in enumerate(urls):
            pg = ctx.new_page()
            rec = {"url": url, "ok": False}
            try:
                resp = pg.goto(url, timeout=timeout_s * 1000, wait_until="domcontentloaded")
                pg.wait_for_timeout(3500)                     # simulations draw after their scripts load
                rec.update(measure(pg), final_url=pg.url, status=resp.status if resp else None, ok=bool(resp and resp.status < 400))
                if rec["ok"] and interactive(rec) < 5:       # maybe an overview page: follow its own "Simulation" (or "Demo", then
                    # "Practice") link once, inside the same part of the site (Virtual Labs experiments work this way), and keep
                    # the followed page unless it is less interactive
                    prefix = rec["final_url"].split("?")[0].split("#")[0].rsplit("/", 1)[0] + "/"
                    link = pg.evaluate(FOLLOW_JS, prefix)
                    if link:
                        try:
                            resp2 = pg.goto(link, timeout=timeout_s * 1000, wait_until="domcontentloaded")
                            pg.wait_for_timeout(3500)
                            rec2 = {**measure(pg), "final_url": pg.url, "ok": bool(resp2 and resp2.status < 400)}
                        except Exception:  # noqa: BLE001
                            rec2 = {"ok": False}
                        if rec2["ok"] and interactive(rec2) >= interactive(rec):      # a page the site calls "Simulation" or "Demo" wins a tie
                            rec.update(rec2, followed=link)
                        else:
                            pg.goto(rec["final_url"], timeout=timeout_s * 1000, wait_until="domcontentloaded")
                            pg.wait_for_timeout(2500)
                shot = shots / f"{i + 1}.jpg"
                pg.screenshot(path=str(shot), type="jpeg", quality=60)
                rec["shot"] = shot.name
            except Exception as ex:  # noqa: BLE001 - a page that does not load is simply not a candidate
                rec["error"] = f"{type(ex).__name__}: {str(ex)[:120]}"
            finally:
                pg.close()
            out.append(rec)
        b.close()
    return out


STOP = {"of", "the", "and", "a", "an", "in", "on", "for", "to", "with", "using", "introduction", "basics", "basic", "its", "how", "what"}


def keywords(topic: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", topic.lower()) if w not in STOP and len(w) > 1]


def names_topic(v: dict, url: str, topic: str) -> bool:
    """The page's own title, headings or address name the topic (most of its key words): its body text may list other topics."""
    kws = keywords(topic)
    ident = " ".join([v.get("title", ""), v.get("meta", ""), v.get("heads", ""), urlparse(v.get("final_url") or url).path.replace("-", " ").replace("_", " ")]).lower()
    hit = sum(1 for k in kws if k in ident or (len(k) > 4 and k.rstrip("s") in ident))
    return bool(kws) and hit >= math.ceil(0.6 * len(kws))        # 1 of 1, 2 of 2, 2 of 3, 3 of 4…


def page_title(v: dict, r: dict, url: str) -> str:
    """A readable title: some sites give every page the same one (Virtual Labs: "Virtual Labs")."""
    t = (v.get("title") or "").strip()
    if len(t) < 4 or t.lower() in ("virtual labs", "home", "index", "simulation") or t.lower() == site_name(url).lower():
        head = (v.get("heads") or "").split(" | ")[0].strip()
        path = [x for x in urlparse(v.get("final_url") or url).path.split("/") if x and not x.endswith(".html") and x not in ("exp", "simulation")]
        t = head or (r.get("title") or "").strip() or (path[-1].replace("-", " ").replace("_", " ").capitalize() if path else url)
        if t.lower() in ("virtual labs", "simulation") and path:
            t = path[-1].replace("-", " ").replace("_", " ").capitalize()
    return t[:140]


def interactive(v: dict) -> int:
    """How much the page looks like something students operate: drawing areas and controls, not just text."""
    return 3 * min(v.get("canvas", 0), 2) + 2 * min(v.get("iframe", 0), 1) + 2 * min(v.get("ranges", 0), 3) + min(v.get("svg", 0), 2) \
        + (2 if v.get("buttons", 0) >= 3 else 0) + (1 if v.get("inputs", 0) >= 1 else 0) + (1 if v.get("words", 0) >= 2 else 0)


# ------------------------------------------------------------------ the whole search for one request
def find(req: dict, work: Path, log=print) -> list[dict]:
    from profsagent.app import simulations as S
    from profsagent.sims import classify as K
    topic, what = (req.get("topic") or "").strip(), (req.get("what") or "").strip()
    seen, cands = set(), []
    # 1. ours and the saved links (free)
    local = S.compute([{"lecture_id": "REQ", "topic": topic, "summary": what}], "", S.entries()).get("REQ") or {}
    for m in local.get("matches", [])[:2]:
        e = S.entry(m["id"])
        # ours must also name the topic, as web pages must (the model alone offered Selection Sort for "Merge Sort")
        if e and e.get("status") != "retired" and names_topic({"title": e["title"], "heads": " ".join(e.get("topics") or [])}, "", topic):
            cands.append({"kind": "ours", "id": e["id"], "title": e["title"], "summary": e["summary"], "site": "ProfsAgent (ours)", "shows_code": bool(e.get("shows_code")),
                          "score": m["score"], "why": f"in our catalogue ({round(100 * m['score'])}% match)"})
            seen.add(e["id"])
    saved = []
    for m in local.get("external", [])[:2]:
        x = X.get(m["id"])
        if x:
            saved.append({"url": x["url"], "title": x["title"], "content": x["summary"], "score": m["score"], "via": "saved", "ext_id": x["id"],
                          "shows_code": X.shows_code(x)})
    if os.environ.get("PROFSAGENT_SIMS_SEARCH") == "local":   # QA servers and demos: no web search, no page visits
        cands += [{"kind": "link", "url": r["url"], "title": r["title"], "summary": r["content"], "site": site_name(r["url"]), "trusted": True, "shows_code": r["shows_code"],
                   "ext_id": r["ext_id"], "shot": None, "score": r["score"], "why": f"a saved link to a trusted site ({round(100 * r['score'])}% match)"}
                  for r in saved]
        cands = S.with_code(cands, SHOW, lambda c: c.get("shows_code"))
        for i, c in enumerate(cands):
            c["n"] = i + 1
        return cands
    # 2. the web: trusted sites first, then anywhere
    q = f"{topic} interactive simulation"
    found = saved + web(q, _search_cfg().get("domains")) + web(q)
    log(f"  search: {len(saved)} saved link(s), {len(found) - len(saved)} web result(s)")
    groups = {"saved": [], "trusted": [], "open": []}
    for r in sorted(found, key=lambda r: -(r.get("score") or 0)):
        if SKIP.search(r["url"]) or (r.get("via") == "tavily" and (r.get("score") or 0) < 0.25):
            continue
        key = r["url"].split("#")[0].rstrip("/")
        if key in seen:
            continue
        seen.add(key)
        groups["saved" if r.get("via") == "saved" else "trusted" if trusted(r["url"]) else "open"].append((r["url"], r))
    order = groups["saved"] + groups["trusted"][:VISIT] + groups["open"][:VISIT]       # the top pages of each search
    # 3. visit the top pages and judge them
    visited = visit([u for u, _ in order], work / "found")
    texts = [f"{topic}. {what}"] + [f"{v.get('title', '')}. {v.get('meta', '')} {v.get('text', '')[:600]}" for v in visited]
    E = K.embed(texts)
    finals = set()
    for (u, r), v, sim in zip(order, visited, (E[1:] @ E[0]).tolist()):
        final = (v.get("final_url") or u).split("#")[0].split("?")[0].rstrip("/")
        if final in finals:                              # two results that lead to the same page (e.g. after a Demo link)
            continue
        act = interactive(v) if v.get("ok") else 0
        named = names_topic(v, u, topic)
        keep = v.get("ok") and act >= 3 and sim >= REL_MIN and named
        log(f"  {'keep' if keep else 'skip'} {u} (loads {bool(v.get('ok'))}, controls {act}, code {v.get('code', 0)}, topic {sim:.2f}, named {named}"
            + (f", followed {v['followed']}" if v.get("followed") else "") + ")")
        if not keep:
            continue
        finals.add(final)
        cands.append({"kind": "link", "url": v.get("final_url") or u, "title": page_title(v, r, u),
                      "shows_code": bool(v.get("code")) or site_shows_code(u) or bool(r.get("shows_code")),
                      "summary": (v.get("meta") or r.get("content") or "")[:240], "site": site_name(u), "trusted": trusted(u),
                      "ext_id": r.get("ext_id"), "shot": v.get("shot"), "score": round(0.6 * sim + 0.05 * min(act, 8) + (0.1 if trusted(u) else 0), 3),
                      "why": ("on a trusted site" if trusted(u) else "found on the web (not a trusted site)") +
                             f"; opened by the machine: it loads, has controls or a drawing area, and matches the topic ({round(100 * sim)}%)"})
    links = sorted((c for c in cands if c["kind"] == "link"), key=lambda c: (not c["trusted"], -c["score"]))
    out = S.with_code([c for c in cands if c["kind"] == "ours"] + links, SHOW, lambda c: c.get("shows_code"))   # one with its code, when any
    for i, c in enumerate(out):
        c["n"] = i + 1
    return out
