"""What a video says, and when: the evidence cascade, and the texts the readers see (METHODS §4-5).

  1. chapters     the uploader's chapter list in the description: free, exact, needs no transcript
  2. captions     youtube-transcript-api (paced; YouTube blocks an IP after ~25 quick requests)
  3. browser      the watch page's own "Show transcript" panel in headless Chromium: keeps working while the caption API is
                  blocked, and also exposes YouTube's auto-generated chapters ("key moments")
  4. notes        Gemini's timestamped notes of the public video: a paraphrase, the last resort

Each evidence record says which source produced it, so a clip placed from chapters or notes is shown as "preview".
"""
from __future__ import annotations

import re
import threading

from profsagent.delivery import sources as S
from profsagent.delivery.segments import chapters as desc_chapters
from profsagent.ytlecture.tools import Trace, cfg


def ts(sec: float) -> str:
    s = int(round(sec))
    return f"{s // 3600}:{s % 3600 // 60:02d}:{s % 60:02d}" if s >= 3600 else f"{s // 60}:{s % 60:02d}"


def secs(t: str) -> float | None:
    t = (t or "").strip().strip("[]")
    if not re.fullmatch(r"\d{1,2}(:\d{1,2}){1,2}", t):
        return None
    v = 0
    for p in t.split(":"):
        v = v * 60 + int(p)
    return float(v)


# ---------------------------------------------------------------- browser transcript (Playwright)
_pw = {"browser": None, "pw": None, "lock": threading.Lock(), "dead": False}

_JS_SEGMENTS = """() => [...document.querySelectorAll('ytd-transcript-segment-renderer, transcript-segment-view-model')]
  .map(s => s.innerText.replace(/\\s+/g, ' ').trim())"""
_JS_CHAPTERS = """() => [...new Map([...document.querySelectorAll('ytd-macro-markers-list-item-renderer')].map(c =>
  [c.querySelector('#time')?.innerText.trim(), (c.querySelector('h4')?.innerText || '').trim()]))].filter(x => x[0] && x[1])"""


def _browser():
    if _pw["dead"]:
        return None
    if _pw["browser"] is None:
        try:
            from playwright.sync_api import sync_playwright
            _pw["pw"] = sync_playwright().start()
            _pw["browser"] = _pw["pw"].chromium.launch(headless=True)
        except Exception:  # noqa: BLE001 — Playwright or Chromium not installed: this source is skipped
            _pw["dead"] = True
            return None
    return _pw["browser"]


def close_browser() -> None:
    if _pw["browser"] is not None:
        try:
            _pw["browser"].close()
            _pw["pw"].stop()
        except Exception:  # noqa: BLE001
            pass
        _pw["browser"] = _pw["pw"] = None


def browser_transcript(vid: str) -> dict | None:
    """{rows: [{start, dur, text}], chapters: [{start, title}]} read from the watch page, or None. Cached 90 days."""
    def run():
        b = _browser()
        if b is None:
            return {"error": "no browser"}
        with _pw["lock"]:
            ctx = b.new_context(locale="en-US", viewport={"width": 1280, "height": 900})
            page = ctx.new_page()
            try:
                page.goto(f"https://www.youtube.com/watch?v={vid}&hl=en", wait_until="domcontentloaded",
                          timeout=cfg()["evidence"]["browser_timeout_s"] * 1000)
                page.wait_for_timeout(3500)
                page.evaluate("() => document.querySelector('video')?.pause()")
                for _ in range(3):                       # the lower half of the page renders lazily
                    page.mouse.wheel(0, 700)
                    page.wait_for_timeout(600)
                page.evaluate("() => window.scrollTo(0, 0)")
                page.evaluate("() => document.querySelector('#description-inline-expander #expand')?.click()")
                page.wait_for_timeout(800)
                btn = page.get_by_role("button", name=re.compile(r"^Show transcript$", re.I))
                if btn.count() == 0:
                    return {"error": "no transcript button"}
                btn.first.click()
                segs = []
                for _ in range(25):
                    page.wait_for_timeout(700)
                    segs = page.evaluate(_JS_SEGMENTS)
                    if segs:
                        break
                chaps = page.evaluate(_JS_CHAPTERS)
            except Exception as e:  # noqa: BLE001
                return {"error": type(e).__name__}
            finally:
                ctx.close()
        rows = []
        for s in segs:
            m = re.match(r"^(\d+(?::\d+)+)\s+(?:\d+ (?:hours?|minutes?|seconds?),?\s*)*(.*)$", s)
            if m and secs(m.group(1)) is not None:
                rows.append({"start": secs(m.group(1)), "text": m.group(2)})
        if len(rows) < 5:
            return {"error": "transcript panel empty"}
        for a, b2 in zip(rows, rows[1:]):
            a["dur"] = max(0.5, b2["start"] - a["start"])
        rows[-1]["dur"] = 5.0
        ch = [{"start": secs(t), "title": h} for t, h in chaps if secs(t) is not None]
        return {"rows": rows, "chapters": ch}
    v = S._cached("browser_tx", vid, 90, run)
    return None if "error" in v else v


def browser_cached(vid: str) -> bool:
    """A transcript panel read in the last 90 days is in the cache (reading it again sends nothing)."""
    import time
    from profsagent.delivery.common import read_json
    d = read_json(S._cache_path("browser_tx", vid))
    return bool(d) and time.time() - d.get("_at", 0) < 90 * 86400 and isinstance(d.get("v"), dict) and bool(d["v"].get("rows"))


# ---------------------------------------------------------------- the watch page (key moments, most replayed)
# The Data API has no chapters: only the description, which we parse. YouTube's automatic chapters ("key moments") and
# the "most replayed" graph exist only in the watch page's embedded JSON, which one plain GET returns (no browser, no
# quota). Tested 17 Nov on 17 CS601 candidates: key moments on 4 of 14 videos without uploader chapters, the graph on 7.
_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")
_page = {"fails": 0, "last": 0.0, "lock": threading.Lock()}


def _json_after(h: str, marker: str) -> dict | None:
    import json
    i = h.find(marker)
    if i < 0:
        return None
    try:
        return json.JSONDecoder().raw_decode(h, i + len(marker))[0]
    except ValueError:
        return None


def _walk(o, key: str):
    """Every value stored under `key` anywhere in a JSON tree."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                yield v
            yield from _walk(v, key)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v, key)


def parse_watch_page(h: str) -> dict:
    """{key_moments: [{start, title}], chapters_kind: auto|uploader|"", description, replayed: [{start, end, intensity}]}"""
    data = _json_after(h, "var ytInitialData = ") or {}
    player = _json_after(h, "ytInitialPlayerResponse = ") or {}
    out = {"key_moments": [], "chapters_kind": "", "description": "", "replayed": []}
    for mm in _walk(data, "markersMap"):
        for m in mm if isinstance(mm, list) else []:
            if m.get("key") not in ("AUTO_CHAPTERS", "DESCRIPTION_CHAPTERS"):
                continue
            rows = []
            for c in (m.get("value") or {}).get("chapters") or []:
                cr = c.get("chapterRenderer") or {}
                t = (cr.get("title") or {}).get("simpleText") or ""
                if t and cr.get("timeRangeStartMillis") is not None:
                    rows.append({"start": cr["timeRangeStartMillis"] / 1000.0, "title": t[:120]})
            if rows:
                out["key_moments"] = rows
                out["chapters_kind"] = "auto" if m["key"] == "AUTO_CHAPTERS" else "uploader"
                break
        if out["key_moments"]:
            break
    for ml in _walk(data, "markersList"):
        if isinstance(ml, dict) and ml.get("markerType") == "MARKER_TYPE_HEATMAP":
            for k in ml.get("markers") or []:
                try:
                    a = int(k["startMillis"]) / 1000.0
                    out["replayed"].append({"start": a, "end": a + int(k["durationMillis"]) / 1000.0,
                                            "intensity": round(float(k.get("intensityScoreNormalized", 0)), 3)})
                except (KeyError, ValueError, TypeError):
                    continue
            break
    out["description"] = ((player.get("videoDetails") or {}).get("shortDescription") or "")[:5000]
    out["ok"] = bool(data)
    return out


def watch_page(vid: str) -> dict | None:
    """The watch page's key moments, full description and most-replayed graph; cached 90 days. None when YouTube does not
    return the page's data (consent or bot check): after 5 such answers in a row the source is skipped for this run."""
    import random
    import time
    import urllib.request

    def run():
        c = cfg().get("watch_page", {})
        if _page["fails"] >= c.get("max_fails", 5):
            return {"error": "skipped"}
        with _page["lock"]:
            wait = _page["last"] + c.get("min_interval_s", 1.5) + random.random() * c.get("jitter_s", 1.0) - time.time()
            if wait > 0:
                time.sleep(wait)
            _page["last"] = time.time()
        try:
            req = urllib.request.Request(f"https://www.youtube.com/watch?v={vid}&hl=en",
                                         headers={"User-Agent": _UA, "Accept-Language": "en-US,en;q=0.9"})
            h = urllib.request.urlopen(req, timeout=c.get("timeout_s", 25)).read().decode("utf-8", "ignore")
        except Exception as e:  # noqa: BLE001
            _page["fails"] += 1
            return {"error": type(e).__name__}
        got = parse_watch_page(h)
        if not got.pop("ok"):
            _page["fails"] += 1
            return {"error": "no page data"}
        _page["fails"] = 0
        return got
    v = S._cached("watch_page", vid, 90, run)
    return None if "error" in v else v


def enrich(v: dict, page: dict) -> None:
    """Copy what the watch page adds onto a candidate: the full description (the API copy was cut at 3,000 characters
    until 17 Nov), key moments when there are no uploader chapters, and the most-replayed peaks."""
    if len(page.get("description") or "") > len(v.get("description") or ""):
        v["description"] = page["description"]
    if page.get("key_moments") and not chapters_of(v):
        v["key_moments"] = page["key_moments"]
        v["key_moments_kind"] = page.get("chapters_kind") or "auto"
    if page.get("replayed"):
        v["replayed"] = peaks(page["replayed"])
    v["page_read"] = True


def peaks(rows: list[dict], n: int = 3, min_ratio: float = 1.6) -> list[dict]:
    """The most-replayed windows: runs of the graph clearly above its median (a talk's opening always peaks: skipped)."""
    if len(rows) < 10:
        return []
    med = sorted(r["intensity"] for r in rows)[len(rows) // 2] or 0.01
    hot = [r for r in rows[1:] if r["intensity"] >= min_ratio * med and r["intensity"] >= 0.3]
    spans: list[dict] = []
    for r in hot:
        if spans and r["start"] - spans[-1]["end"] < 1:
            spans[-1]["end"] = r["end"]
            spans[-1]["intensity"] = max(spans[-1]["intensity"], r["intensity"])
        else:
            spans.append(dict(r))
    return sorted(spans, key=lambda s: -s["intensity"])[:n]


# ---------------------------------------------------------------- the cascade
def chapters_of(v: dict) -> list[dict]:
    """The uploader's chapters from the description; else YouTube's key moments read from the watch page."""
    ch = [{"start": c["start"], "end": c["end"], "title": c["title"]} for c in desc_chapters(v.get("description", ""), v.get("duration_s"))]
    km = v.get("key_moments") or []
    if ch or not km:
        return ch
    ends = [c["start"] for c in km[1:]] + [float(v.get("duration_s") or km[-1]["start"] + 60)]
    auto = v.get("key_moments_kind", "auto") == "auto"
    return [{"start": c["start"], "end": e, "title": c["title"], "auto": auto} for c, e in zip(km, ends) if e > c["start"]]


def evidence(v: dict, trace: Trace, scope: str) -> dict:
    """{source: captions|browser|notes|chapters|none, rows, chapters}. Chapters are always attached when they exist."""
    vid, dur = v["id"], v.get("duration_s")
    ch = chapters_of(v)
    for src in cfg()["evidence"]["order"]:
        rows, extra = None, []
        if src == "captions":
            if not S.transcript_known(vid) and browser_cached(vid):
                continue          # 23 Nov: the shortlist already read this one's transcript panel; no caption request
            if S.transcripts_blocked():
                continue
            rows = S.transcript(vid)
        elif src == "browser":
            got = browser_transcript(vid)
            if got:
                rows, extra = got["rows"], got.get("chapters") or []
        elif src == "notes":
            if (dur or 0) > cfg()["evidence"]["notes_max_video_s"]:
                continue
            rows = S.video_notes(vid, dur)
        trace.tool(f"evidence.{src}", vid, len(rows or []), "blocked" if src == "captions" and S.transcripts_blocked() else "", scope)
        if rows:
            if not ch and extra:                      # YouTube's auto chapters, when the uploader wrote none
                ends = [c["start"] for c in extra[1:]] + [float(dur or extra[-1]["start"] + 60)]
                ch = [{"start": c["start"], "end": e, "title": c["title"], "auto": True} for c, e in zip(extra, ends) if e > c["start"]]
            return {"source": src, "rows": rows, "chapters": ch}
    return {"source": "chapters" if ch else "none", "rows": [], "chapters": ch}


# ---------------------------------------------------------------- texts the readers see
def lines(rows: list[dict], every: float = 20.0, a: float = 0, b: float = 1e12) -> list[tuple[float, str]]:
    """Caption rows merged into ~`every`-second lines [(start, text)] within [a, b]."""
    out, cur, start = [], [], None
    for r in rows:
        if r["start"] + r.get("dur", 0) < a or r["start"] > b:
            continue
        if start is None:
            start = r["start"]
        cur.append(r["text"].replace("\n", " "))
        if r["start"] + r.get("dur", 0) - start >= every:
            out.append((start, " ".join(cur)))
            cur, start = [], None
    if cur:
        out.append((start, " ".join(cur)))
    return [(s, re.sub(r"\s+", " ", t).strip()) for s, t in out]


def skim(rows: list[dict]) -> str:
    """One line per ~45 s with its first ~28 words: shows where the topic changes at a fifth of the tokens."""
    c = cfg()["reading"]
    return "\n".join(f"[{ts(s)}] {' '.join(t.split()[:c['skim_words']])}" for s, t in lines(rows, c["skim_every_s"]))


def full(rows: list[dict], a: float = 0, b: float = 1e12) -> str:
    return "\n".join(f"[{ts(s)}] {t}" for s, t in lines(rows, 20.0, a, b))


def plain(rows: list[dict], a: float, b: float) -> str:
    return " ".join(r["text"] for r in rows if r["start"] + r.get("dur", 0) > a and r["start"] < b)


def chapters_text(ch: list[dict]) -> str:
    return "\n".join(f"[{ts(c['start'])}–{ts(c['end'])}] {c['title']}" for c in ch) or "(none)"


def snap(rows: list[dict], t: float, side: str) -> float:
    """Move a boundary onto a caption-line start (start: the nearest line start at or before t + 3 s; end: the end of the
    line that contains t), so a clip starts and stops at the edge of a sentence-ish unit."""
    if not rows:
        return t
    if side == "start":
        cands = [r["start"] for r in rows if r["start"] <= t + 3]
        return max(cands) if cands else rows[0]["start"]
    for r in rows:
        if r["start"] <= t < r["start"] + r.get("dur", 0) + 0.5:
            return r["start"] + r.get("dur", 0)
    return t


_SENT_END = re.compile(r"[.?!]['\")\]]*\s*$")


def sentence_start(rows: list[dict], t: float, back: float = 25.0) -> float:
    """Start of the sentence that contains t: the first caption row after a row ending in . ? or !, looking back at most
    `back` seconds. 17 Nov audit: line snapping alone opened clips mid-sentence ("terms, this means some AI tools ...",
    "order to continue moving it ..."), because caption lines do not follow sentences. Unpunctuated captions: unchanged."""
    i = max((k for k, r in enumerate(rows) if r["start"] <= t + 0.5), default=-1)
    if i <= 0:
        return t
    j = i
    while j > 0 and rows[j - 1]["start"] >= t - back:
        if _SENT_END.search(rows[j - 1]["text"].strip()):
            return rows[j]["start"]
        j -= 1
    return t                     # no sentence end in reach (or unpunctuated captions): keep the line start


def sentence_end(rows: list[dict], t: float, fwd: float = 15.0) -> float:
    """End of the sentence running at t: the end of the first row from t on that ends in . ? or !, at most `fwd` s on."""
    for r in rows:
        end = r["start"] + r.get("dur", 0)
        if end < t - 0.5:
            continue
        if r["start"] > t + fwd:
            break
        if _SENT_END.search(r["text"].strip()):
            return end
    return t


def _tok(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (s or "").lower())


def quote_near(quote: str, rows: list[dict], t: float, span: float = 60.0) -> float | None:
    """Time of the caption row (within ±span of t) where the quote's words best appear, or None if they do not appear."""
    q = _tok(quote)
    if len(q) < 3 or not rows:
        return None
    near = [r for r in rows if abs(r["start"] - t) <= span]
    grams = [" ".join(q[k:k + 2]) for k in range(len(q) - 1)]
    scored = []
    for i, r in enumerate(near):
        text = " ".join(_tok(" ".join(x["text"] for x in near[i:i + 3])))
        own = " ".join(_tok(r["text"]))
        # a window of 3 lines catches quotes that cross a line break; the line where the quote STARTS wins a tie
        scored.append((sum(g in text for g in grams) / len(grams), grams[0] in own, -i, r["start"]))
    if not scored:
        return None
    best = max(scored)
    return best[3] if best[0] >= 0.5 else None
