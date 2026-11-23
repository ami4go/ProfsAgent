"""Shortlisting from what the videos SAY (23 Nov): the grader judged ~15 title cards per part, so a plain-titled lecture
that teaches a part well and a well-titled video that barely does looked alike. Now:

  1. POOL        the title/chapter ranking (shortlist.rank) only cuts ~300 candidates to the ~40 worth a transcript:
                 each part's best, the nominated videos, round-robin across parts
  2. TRANSCRIPTS captions (paced, hourly cap) in a background thread while the main thread reads the watch pages'
                 "Show transcript" panels (the headless browser must stay on one thread); no AI notes here
  3. WINDOWS     every transcript cut into overlapping 60-s windows, embedded locally (MiniLM, cached on disk); each
                 part is compared with every window, and the local cross-encoder re-reads each part's best excerpts
  4. EXCERPTS    per part and video, the best stretch (~2 min) around the best window: what the grader reads, and the
                 spans the reader zooms into later instead of a skim call

No AI call happens here: everything is local except the transcript downloads, which are cached for 90 days and reused
by the reading step.
"""
from __future__ import annotations

import threading
import time

import numpy as np

from profsagent.delivery import sources as S
from profsagent.delivery.common import read_json
from profsagent.ytlecture import evidence as E
from profsagent.ytlecture.tools import Trace, cfg


def tcfg() -> dict:
    return cfg().get("transcript_shortlist", {})


# ---------------------------------------------------------------- 1 pool
def pool(R: dict, n: int, nominated: dict[int, list[str]] | None = None, cap: int = 2) -> list[str]:
    """Up to n video ids: the nominated ones first, then each part's next best by the local score, taken in turn
    (part 0's 1st, part 1's 1st, ..., part 0's 2nd ...), at most `cap` per channel within a part's list."""
    from profsagent.ytlecture import shortlist as SL
    out = list(dict.fromkeys(v for lst in (nominated or {}).values() for v in lst))[:n]
    lists = SL.per_part_lists(R, n, cap)
    k = 0
    while len(out) < n and any(k < len(l) for l in lists.values()):
        for i in sorted(lists):
            if k < len(lists[i]) and lists[i][k] not in out:
                out.append(lists[i][k])
                if len(out) >= n:
                    break
        k += 1
    return out


# ---------------------------------------------------------------- 2 transcripts
def _browser_cached(vid: str) -> list[dict] | None:
    d = read_json(S._cache_path("browser_tx", vid))
    if d and time.time() - d.get("_at", 0) < 90 * 86400 and isinstance(d.get("v"), dict) and d["v"].get("rows"):
        return d["v"]["rows"]
    return None


def cached_rows(vid: str) -> list[dict] | None | bool:
    """Rows from either cache; False when the caption cache says the video has no captions; None when not cached."""
    rows = _browser_cached(vid)
    if rows:
        return rows
    if S.transcript_known(vid):
        return S.transcript(vid) or False        # a cache hit: sends nothing
    return None


def caption_slot_free() -> bool:
    """A caption request now would neither be refused (blocked) nor wait for the hourly cap."""
    c = S.rcfg()["transcripts"]
    if S.transcripts_blocked():
        return False
    cap = c.get("max_per_hour")
    recent = [x for x in S._tx.get("times", []) if time.time() - x < 3600]
    return not cap or len(recent) < cap


def fetch(vids: list[str], trace: Trace, scope: str, max_s: float | None = None) -> dict[str, list[dict] | None]:
    """{video: rows or None}. Cached first; then captions in a background thread and the browser panel in this one, both
    taking the next video from the same list, until the list is empty or `max_s` seconds have passed."""
    c = tcfg()
    max_s = max_s if max_s is not None else 60 * c.get("max_fetch_minutes", 15)
    out: dict[str, list[dict] | None] = {}
    todo: list[str] = []
    for v in vids:
        got = cached_rows(v)
        if got is None:
            todo.append(v)
        else:
            out[v] = got or None
    n_cached = len(out)
    lock, start = threading.Lock(), time.time()
    tried: dict[str, set] = {v: set() for v in todo}

    def take(src: str) -> str | None:
        with lock:
            if time.time() - start > max_s:
                return None
            for v in todo:
                if v not in out and src not in tried[v] and not tried[v] & {"busy"}:
                    tried[v] |= {src, "busy"}
                    return v
        return None

    def done(v: str, rows: list[dict] | None, final: bool) -> None:
        with lock:
            tried[v].discard("busy")
            if rows or final:
                out[v] = rows or None

    def captions():
        while caption_slot_free():
            v = take("captions")
            if v is None:
                return
            rows = S.transcript(v)
            # "no captions" is an answer (the panel would be empty too); any other failure leaves it to the browser
            done(v, rows, final=bool(rows) or S.transcript_known(v))
    th = None
    if c.get("captions", True):
        th = threading.Thread(target=captions, daemon=True)
        th.start()
    if c.get("browser", True):
        while True:
            v = take("browser")
            if v is None:
                if th is not None and th.is_alive() and time.time() - start <= max_s and any(v_ not in out for v_ in todo):
                    time.sleep(0.5)        # the caption thread holds the rest; it may give some back
                    continue
                break
            got = E.browser_transcript(v)
            done(v, (got or {}).get("rows"), final=True)
            if E._pw["dead"]:
                break
    if th is not None:
        th.join(timeout=max(0.0, max_s - (time.time() - start)) + 30)
    for v in todo:
        out.setdefault(v, None)
    n_ok = sum(1 for v in vids if out.get(v))
    trace.step(scope, "transcripts for shortlisting", videos=len(vids), from_cache=n_cached, with_words=n_ok,
               seconds=round(time.time() - start))
    return out


# ---------------------------------------------------------------- 3 windows
def windows(rows: list[dict], size: float | None = None, step: float | None = None) -> list[tuple[float, float, str]]:
    """Overlapping windows [(a, b, text)] of `size` seconds every `step` seconds (60/30: ~150 words, within the
    embedding model's input)."""
    size = size or tcfg().get("window_s", 60)
    step = step or tcfg().get("step_s", 30)
    if not rows:
        return []
    end = max(r["start"] + r.get("dur", 0) for r in rows)
    out, a = [], rows[0]["start"]
    while a < end:
        b = min(end, a + size)
        text = E.plain(rows, a, b)
        if len(text.split()) >= 15:
            out.append((a, b, " ".join(text.split())))
        a += step
    return out


def part_query(p: dict) -> str:
    """What a window is compared with: the part and its must-cover points (the checklist clips are judged on later)."""
    pts = "; ".join(p.get("must_cover") or [])
    return f"{p['title']}. {p['teaches']} {pts}"


def match(parts: list[dict], rows_of: dict[str, list[dict]]) -> dict[str, dict]:
    """{video: {"wins": [(a, b, text)], "sim": array[parts, windows]}} for the videos with words."""
    from profsagent.ytlecture import shortlist as SL
    pv = SL._embed([part_query(p) for p in parts])
    out = {}
    for vid, rows in rows_of.items():
        if not rows:
            continue
        w = windows(rows)
        if not w:
            continue
        wv = SL._embed([t for _, _, t in w])
        out[vid] = {"wins": w, "sim": SL._cos(pv, wv)}
    return out


def _smooth(row: np.ndarray) -> np.ndarray:
    """Each window's similarity averaged with its neighbours (weights .25 .5 .25): a part is taught over minutes, so a
    lone matching window (a passing mention) counts less than a run of them."""
    if len(row) < 3:
        return row
    p = np.pad(row, 1, mode="edge")
    return 0.25 * p[:-2] + 0.5 * p[1:-1] + 0.25 * p[2:]


def excerpt(rows: list[dict], m: dict, i: int, words: int | None = None) -> dict:
    """The best stretch of the video for part i: {a, b, sim, text}. Centred on the best (smoothed) window and grown
    window by window towards the stronger neighbour until it holds `words` words."""
    words = words or tcfg().get("excerpt_words", 200)
    sm = _smooth(m["sim"][i])
    k = int(np.argmax(sm))
    lo = hi = k
    w = m["wins"]

    def n_words(a, b):
        return len(E.plain(rows, w[a][0], w[b][1]).split())
    while n_words(lo, hi) < words and (lo > 0 or hi < len(w) - 1):
        left = sm[lo - 1] if lo > 0 else -9
        right = sm[hi + 1] if hi < len(w) - 1 else -9
        if right >= left:
            hi += 1
        else:
            lo -= 1
    a, b = w[lo][0], w[hi][1]
    text = " ".join(E.plain(rows, a, b).split()[: int(words * 1.15)])
    return {"a": a, "b": b, "sim": float(sm[k]), "peak": float(m["sim"][i].max()), "text": text}


def spans(m: dict, i: int, minutes: float, n: int = 2) -> list[tuple[float, float]]:
    """Up to n regions of the video to read for part i: around its strongest (smoothed) windows, each grown while the
    windows stay within `span_drop` of the peak, then widened to at least the part's length (min 5 min)."""
    c = tcfg()
    sm = _smooth(m["sim"][i])
    w = m["wins"]
    want = max(300.0, 0.8 * 60 * minutes)
    used = np.zeros(len(w), dtype=bool)
    out: list[tuple[float, float]] = []
    for k in np.argsort(-sm):
        if len(out) >= n or sm[k] < c.get("span_min_sim", 0.3):
            break
        if used[k]:
            continue
        lo = hi = int(k)
        while lo > 0 and sm[lo - 1] >= sm[k] - c.get("span_drop", 0.08):
            lo -= 1
        while hi < len(w) - 1 and sm[hi + 1] >= sm[k] - c.get("span_drop", 0.08):
            hi += 1
        a, b = w[lo][0], w[hi][1]
        if b - a < want:
            grow = (want - (b - a)) / 2
            a, b = max(0.0, a - grow), min(w[-1][1], b + grow)
        used[lo:hi + 1] = True
        for j, (x, y, _) in enumerate(w):         # windows inside the region are used up
            if x >= a and y <= b:
                used[j] = True
        out.append((a, b))
    merged: list[list[float]] = []
    for a, b in sorted(out):
        if merged and a <= merged[-1][1] + 60:
            merged[-1][1] = max(merged[-1][1], b)
        else:
            merged.append([a, b])
    return [(round(a, 1), round(b, 1)) for a, b in merged]


# ---------------------------------------------------------------- 4 the transcript score and the grader's cards
def score(parts: list[dict], rows_of: dict[str, list[dict]], M: dict[str, dict]) -> dict[str, dict[int, dict]]:
    """{video: {part: {"rel", "a", "b", "text", "sim", "ce"}}}: rel = the excerpt's smoothed embedding similarity,
    blended with the local cross-encoder's reading of (part, excerpt) when the model is available."""
    from profsagent.ytlecture import shortlist as SL
    out: dict[str, dict[int, dict]] = {}
    pairs, idx = [], []
    for vid, m in M.items():
        for i, p in enumerate(parts):
            ex = excerpt(rows_of[vid], m, i)
            out.setdefault(vid, {})[i] = {**ex, "rel": ex["sim"]}
            pairs.append((f"{p['title']}. {p['teaches']}", ex["text"]))
            idx.append((vid, i))
    w = tcfg().get("cross_weight", 0.5)
    ce = SL.cross_scores(pairs) if pairs and w else None
    if ce is not None:
        for (vid, i), x in zip(idx, ce):
            d = out[vid][i]
            d["ce"] = round(float(x), 3)
            d["rel"] = (1 - w) * d["sim"] + w * float(x)
    return out


def grade_sets(TX: dict[str, dict[int, dict]], prior_of: dict[str, float], parts: list[dict], cands: dict,
               R: dict, nominated: dict[int, list[str]] | None = None) -> dict[int, list[str]]:
    """Per part: the `excerpt_cards` videos whose excerpt matches it best (plus a small quality prior), at most
    `per_channel_in_part` per channel, the nominated ones always among them; plus up to `title_cards` videos without
    words (graded from their title card, as before)."""
    from profsagent.ytlecture import shortlist as SL
    c, s = tcfg(), SL.scfg()
    n, cap, pw = c.get("excerpt_cards", 8), s.get("per_channel_in_part", 2), c.get("prior_weight", 0.5)
    out = {}
    for i in range(len(parts)):
        nom = [v for v in (nominated or {}).get(i, []) if v in TX]
        order = sorted((v for v in TX if v not in nom), key=lambda v: -(TX[v][i]["rel"] + pw * prior_of.get(v, 0.0)))
        lst, by_ch = list(nom[: c.get("nominated_cards", 2)]), {}
        for v in lst:
            ch = cands[v].get("channel_id") or cands[v].get("channel")
            by_ch[ch] = by_ch.get(ch, 0) + 1
        for v in order:
            if len(lst) >= n + len(nom[: c.get("nominated_cards", 2)]):
                break
            if TX[v][i]["rel"] < c.get("min_rel", 0.2):
                continue
            ch = cands[v].get("channel_id") or cands[v].get("channel")
            if by_ch.get(ch, 0) >= cap:
                continue
            by_ch[ch] = by_ch.get(ch, 0) + 1
            lst.append(v)
        # videos without words: the best few by the title ranking, so a lecture with no captions is not invisible
        if c.get("title_cards", 2):
            j_of = {v["id"]: j for j, v in enumerate(R["vids"])}
            wordless = [v for v in (nominated or {}).get(i, []) if v not in TX and v in j_of]
            wordless += [R["vids"][j]["id"] for j in np.argsort(-R["score"][i]) if R["vids"][j]["id"] not in TX]
            lst += list(dict.fromkeys(x for x in wordless if x not in lst))[: c.get("title_cards", 2)]
        out[i] = lst
    return out


def card_excerpt(d: dict) -> str:
    return f"[{E.ts(d['a'])}–{E.ts(d['b'])}] \"{d['text']}\""


def run(parts: list[dict], cands: dict, R: dict, nominated: dict[int, list[str]], trace: Trace, scope: str
        ) -> tuple[dict[int, list[str]], dict[str, dict[int, dict]], dict[str, dict[str, list]]] | None:
    """(grade sets, excerpts {video: {part: excerpt}}, reading spans {video: {part: [[a, b]]}}), or None when too few
    videos have words (the caller then grades title cards as before)."""
    c = tcfg()
    ids = pool(R, c.get("videos", 40), nominated)
    rows_of = fetch(ids, trace, scope)
    have = {v: r for v, r in rows_of.items() if r}
    if len(have) < c.get("min_videos", 6):
        trace.step(scope, "transcript shortlist skipped: too few transcripts", with_words=len(have), asked=len(ids))
        return None
    M = match(parts, have)
    TX = score(parts, have, M)
    prior_of = {v["id"]: float(p) for v, p in zip(R["vids"], R["prior"])}
    sets = grade_sets(TX, prior_of, parts, cands, R, nominated)
    sp = {v: {str(i): [list(x) for x in spans(M[v], i, p["minutes"])] for i, p in enumerate(parts)} for v in M}
    trace.step(scope, "transcript match", videos=len(TX),
               best={str(i): [(v, round(TX[v][i]["rel"], 2), E.ts(TX[v][i]["a"])) for v in sets[i] if v in TX][:5]
                     for i in range(len(parts))})
    return sets, TX, sp
