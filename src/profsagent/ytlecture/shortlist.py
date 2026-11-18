"""Choosing which videos to read (17 Nov redesign of step 5).

Measured on the manual CS601 playlists (scripts/bench_shortlist.py): of 30 hand-picked videos that were among the
candidates, the old pre-rank showed the triage agent 7 with full metadata and 14 more as bare titles; 9 it never saw.
One call then had to judge ~130 videos, cover every part and respect a budget at once, and at 5-8K tokens it was too
long for Groq, so after Gemini's quota it fell to the weakest model. The new step splits the work:

  1. EVIDENCE   every strong candidate gets a table of contents: uploader chapters (parser fixed), else YouTube's key
                moments from the watch page; the full description; the most-replayed peaks
  2. RANK       code: best match of the part against the title AND each chapter (local embeddings), a local cross-encoder
                re-rank of the top pairs, and a quality prior (tier, named authority, views per year, likes, and a
                channel REPUTATION learned from the verifier's scores in all earlier runs)
  3. GRADE      the AI grades ~15 cards per PART, 0-3, twice in opposite orders (averaged: cancels position bias); each
                call is ~3K tokens, so the fast free models can take it
  4. SELECT     code: a budgeted coverage choice (every part covered, long lectures that serve several parts preferred,
                channels mixed, reading cost counted by video length); part of the budget is kept for a second round
                chosen the same way after the first videos are verified, for the parts that are still thin
"""
from __future__ import annotations

import glob
import json
import math
import threading
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from profsagent.delivery.common import RUNS, embed
from profsagent.ytlecture import evidence as E
from profsagent.ytlecture import tools as T
from profsagent.ytlecture.tools import cfg

_EMB = threading.Lock()
_CE = {"m": None, "dead": False, "lock": threading.Lock()}


def scfg() -> dict:
    return cfg().get("shortlist", {})


def _embed(texts: list[str]) -> np.ndarray:
    with _EMB:
        return embed(texts)


def _cos(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return (a @ b.T) / (np.linalg.norm(a, axis=1, keepdims=True) * np.linalg.norm(b, axis=1) + 1e-9)


# ---------------------------------------------------------------- local cross-encoder
def cross_scores(pairs: list[tuple[str, str]]) -> np.ndarray | None:
    """Relevance 0-1 of (part, video card) pairs from a small local re-ranker (reads both texts together, unlike the
    embeddings, which compare two separate summaries). None when the model cannot be loaded."""
    if not pairs or _CE["dead"] or not scfg().get("cross_encoder"):
        return None
    with _CE["lock"]:
        if _CE["m"] is None:
            try:
                from sentence_transformers import CrossEncoder
                _CE["m"] = CrossEncoder(scfg()["cross_encoder"])
            except Exception:  # noqa: BLE001 — not installed or not downloadable: rank without it
                _CE["dead"] = True
                return None
        logits = np.asarray(_CE["m"].predict(pairs, batch_size=32, show_progress_bar=False), dtype=float)
    return 1.0 / (1.0 + np.exp(-logits))


# ---------------------------------------------------------------- channel reputation from earlier runs
_REP: dict = {}


def reputation(exclude_run: str | None = None) -> dict[str, tuple[float, int]]:
    """{channel: (smoothed mean outcome, videos)}. A read video's outcome is its best verified clip score, or
    `no_clip_outcome` when reading it gave no clip. Smoothed towards `prior` with weight `prior_weight`, so one lucky
    video does not make a channel. Built from every runs/*/delivery/ytlecture/state file (exclude_run: for honest
    benchmarks on that run)."""
    key = exclude_run or ""
    if key in _REP:
        return _REP[key]
    c = scfg().get("reputation", {})
    m, k, none = c.get("prior", 0.5), c.get("prior_weight", 3), c.get("no_clip_outcome", 0.35)
    per: dict[str, dict[str, float]] = {}
    for f in glob.glob(str(RUNS / "*" / "delivery" / "ytlecture" / "state" / "*.json")):
        if exclude_run and f"{exclude_run}" in f.replace("\\", "/").split("/"):
            continue
        try:
            d = json.load(open(f, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        cands = d.get("candidates") or {}
        for l in (d.get("lectures") or {}).values():
            best: dict[str, float] = {}
            for k_ in l.get("clips") or []:
                if (k_.get("check") or {}).get("coverage") is None:
                    continue
                best[k_["video"]] = max(best.get(k_["video"], 0.0), float(k_.get("score") or 0))
            for vid in l.get("read") or []:
                ch = (cands.get(vid) or {}).get("channel")
                if ch:
                    per.setdefault(ch, {})[vid] = max(per.get(ch, {}).get(vid, 0.0), best.get(vid, none))
    out = {ch: ((sum(v.values()) + k * m) / (len(v) + k), len(v)) for ch, v in per.items()}
    _REP[key] = out
    return out


# ---------------------------------------------------------------- ranking
def part_text(p: dict) -> str:
    return f"{p['title']}. {p['teaches']} {' '.join(p.get('search_phrases') or [])}"


def ce_text(v: dict) -> str:
    ch = "; ".join(c["title"] for c in E.chapters_of(v))[:500]
    return f"{v['title']} | {v.get('channel', '')} | chapters: {ch or 'none'} | {(v.get('description') or '')[:200]}"


def popularity(v: dict) -> float:
    """0-1: views per year on a log scale, 1k a year → 0, 1M a year → 1."""
    views, year = v.get("views") or 0, (v.get("published") or "")[:4]
    age = max(0.5, 2026.9 - int(year)) if year.isdigit() else 2.0
    return min(1.0, max(0.0, (math.log10(views / age + 1) - 3) / 3))


def subscribers_score(v: dict) -> float:
    """0-1: the channel's subscribers on a log scale, 10k → 0, 1M → 1 (18 Nov: the study's yt-pipeline rubric ranks
    by channel size; the counts were already fetched with each video's details but never used)."""
    n = v.get("subscribers") or 0
    return min(1.0, max(0.0, (math.log10(n + 1) - 4) / 2))


def prior(v: dict, auth: bool, lid: str, rep: dict) -> float:
    """Quality and fit-to-lecture, independent of the part."""
    t, r = cfg()["triage"], scfg()
    s = {1: t.get("tier1_bonus", 0.10), 2: t.get("tier2_bonus", 0.06)}.get(v.get("tier", 4), 0.0)
    s += t.get("authority_bonus", 0.08) * auth
    s += r.get("edu_bonus", 0.06) * T.is_edu(v.get("channel", ""))
    s += 0.06 * any(x.startswith(lid + "#") for x in v.get("parts", []))          # found by this lecture's own queries
    views = v.get("views") or 0
    s += r.get("popularity_bonus", 0.06) * popularity(v)
    if v.get("likes") and views >= 1000 and v["likes"] / views >= 0.03:
        s += r.get("likes_bonus", 0.02)
    s += r.get("subscriber_bonus", 0.04) * subscribers_score(v)
    mean, n = rep.get(v.get("channel", ""), (None, 0))
    if mean is not None:
        s += r.get("reputation_weight", 0.25) * (mean - scfg().get("reputation", {}).get("prior", 0.5))
    return s


def is_authority(v: dict, sc: dict | None) -> bool:
    # A person's name may be in the title (a talk on another channel); any other authority must BE the channel, or
    # product names the scout lists ("Claude Code") make every video mentioning them an authority.
    for a in (sc or {}).get("authorities", []):
        if len(a["name"]) < 4:
            continue
        text = f"{v.get('channel', '')} {v['title']}" if a.get("kind") == "person" else v.get("channel", "")
        if T._word_hit(a["name"], text.lower()):
            return True
    return False


def fetch_pages(vids: list[dict], n: int) -> int:
    """Read the watch page of the first n candidates that have not had it read (key moments, full description)."""
    if not scfg().get("watch_pages", True):
        return 0
    got = 0
    for v in [v for v in vids if not v.get("page_read")][:n]:
        page = E.watch_page(v["id"])
        if page is None:
            if E._page["fails"] >= cfg().get("watch_page", {}).get("max_fails", 5):
                break
            continue
        E.enrich(v, page)
        got += 1
    return got


def rank(parts: list[dict], cands: dict, lid: str, sc: dict | None, exclude_run: str | None = None,
         pages: bool = True) -> dict:
    """{vids, score[part, video], rel, prior, auth}: how well each candidate serves each part, all computed locally."""
    vids = list(cands.values())
    if not vids or not parts:
        return {"vids": vids, "score": np.zeros((len(parts), len(vids))), "rel": None, "prior": np.zeros(len(vids)), "auth": []}
    rep = reputation(exclude_run)
    auth = [is_authority(v, sc) for v in vids]
    pr = np.array([prior(v, a, lid, rep) for v, a in zip(vids, auth)])
    pv = _embed([part_text(p) for p in parts])

    def blob() -> np.ndarray:
        meta = [f"{v['title']}. " + "; ".join(c["title"] for c in E.chapters_of(v))[:600] + " " + (v.get("description") or "")[:300] for v in vids]
        return _cos(pv, _embed(meta))
    sim = blob()
    if pages:   # the watch pages of the strongest candidates, then the blob again (descriptions and chapters changed)
        order = np.argsort(-(sim.max(axis=0) + pr))
        if fetch_pages([vids[j] for j in order], scfg().get("pages_per_lecture", 60)):
            sim = blob()
    # each chapter on its own: "Lecture 7: Agentic Coding" with a chapter "MCP architecture" matches the MCP part
    chap = np.zeros_like(sim)
    rows, owner = [], []
    for j, v in enumerate(vids):
        for c in E.chapters_of(v):
            if len(c["title"]) >= 6:
                rows.append(c["title"])
                owner.append(j)
    if rows:
        cs = _cos(pv, _embed(rows))
        owner_a = np.array(owner)
        for j in set(owner):
            chap[:, j] = cs[:, owner_a == j].max(axis=1)
    rel = np.maximum(sim, chap - scfg().get("chapter_margin", 0.03))
    score = rel + pr
    # local cross-encoder on each part's strongest pairs
    w_ce = scfg().get("cross_weight", 0.3)
    top = scfg().get("cross_top", 40)
    if w_ce:
        pairs, idx = [], []
        for i, p in enumerate(parts):
            q = f"{p['title']}. {p['teaches']}"
            for j in np.argsort(-score[i])[:top]:
                pairs.append((q, ce_text(vids[j])))
                idx.append((i, j))
        ce = cross_scores(pairs)
        if ce is not None:
            adj = np.full_like(score, -0.5 * w_ce)         # unscored pairs sit below the scored ones
            for (i, j), x in zip(idx, ce):
                adj[i, j] = w_ce * (x - 0.5)
            score = score + adj
    return {"vids": vids, "score": score, "rel": rel, "prior": pr, "auth": auth}


def per_part_lists(R: dict, n: int, cap: int) -> dict[int, list[str]]:
    """Each part's best n candidates, at most `cap` per channel."""
    out = {}
    for i in range(R["score"].shape[0]):
        order, by_ch = [], {}
        for j in np.argsort(-R["score"][i]):
            v = R["vids"][j]
            ch = v.get("channel_id") or v.get("channel")
            if by_ch.get(ch, 0) >= cap:
                continue
            by_ch[ch] = by_ch.get(ch, 0) + 1
            order.append(v["id"])
            if len(order) >= n:
                break
        out[i] = order
    return out


def strong(R: dict, j: int) -> bool:
    v = R["vids"][j]
    return v.get("tier", 4) <= 2 or bool(R["auth"][j]) or R["prior"][j] >= 0.12


def nominee_rows(R: dict, parts: list[dict]) -> list[dict]:
    """The strong-source videos the nominator sees (title, channel, length, year): on-topic enough by wording
    (best part similarity >= nominee_min_sim), ordered by quality + similarity, at most `nominee_per_channel` each."""
    c = scfg()
    vids = R["vids"]
    if not vids:
        return []
    best = R["rel"].max(axis=0)
    pw = c.get("nominee_pop_weight", 0.25)     # the canonical talks are the much-watched ones (600k views for both
    js = sorted((j for j in range(len(vids)) if strong(R, j) and best[j] >= c.get("nominee_min_sim", 0.28)),   # missed ones)
                key=lambda j: -(R["prior"][j] + best[j] + pw * popularity(vids[j])))
    out, by_ch = [], {}
    for j in js:
        v = vids[j]
        ch = v.get("channel_id") or v.get("channel")
        if by_ch.get(ch, 0) >= c.get("nominee_per_channel", 4):
            continue
        by_ch[ch] = by_ch.get(ch, 0) + 1
        out.append({"id": v["id"], "title": v["title"], "channel": v.get("channel", ""), "length": E.ts(v.get("duration_s") or 0),
                    "year": (v.get("published") or "")[:4]})
        if len(out) >= c.get("nominees", 80):
            break
    return out


def nominations(llm, lecture: dict, parts: list[dict], R: dict, fast: bool, trace, run_id: str) -> dict[int, list[str]]:
    """{part: [video ids]} the nominator names; {} when the call fails (the grading goes on without it)."""
    from profsagent.ytlecture import agents as A
    rows = nominee_rows(R, parts)
    if not rows or not scfg().get("nominations", 8):
        return {}
    try:
        res = A.nominate(llm, lecture, parts, rows, fast, trace, run_id)
    except Exception as e:  # noqa: BLE001
        trace.step(lecture["lecture_id"], f"nominator failed: {type(e).__name__}")
        return {}
    ok = {r["id"] for r in rows}
    out: dict[int, list[str]] = {}
    for n in res.nominations[: scfg().get("nominations", 8)]:
        if n.video_id in ok:
            for i in dict.fromkeys(n.parts):
                if 0 <= i < len(parts):
                    out.setdefault(i, []).append(n.video_id)
    return out


def grade_sets(R: dict, parts: list[dict], exclude: set[str] = frozenset(),
               nominated: dict[int, list[str]] | None = None) -> dict[int, list[str]]:
    """The cards each part's grader sees: its best `cards_per_part` candidates (2 per channel), the videos the
    nominator named for it (up to `nominated_cards`), and up to `anchor_cards` long videos from strong sources."""
    c = scfg()
    n, extra = c.get("cards_per_part", 12), c.get("anchor_cards", 3)
    vids = R["vids"]
    base = per_part_lists(R, n + len(exclude), c.get("per_channel_in_part", 2))
    out = {}
    for i, lst in base.items():
        lst = [x for x in lst if x not in exclude][:n]
        nom = [x for x in (nominated or {}).get(i, []) if x not in lst and x not in exclude][: c.get("nominated_cards", 4)]
        lst += nom
        longs = [j for j in np.argsort(-R["score"][i]) if vids[j]["id"] not in lst and vids[j]["id"] not in exclude
                 and (vids[j].get("duration_s") or 0) >= c.get("anchor_min_s", 1800) and strong(R, j)]
        out[i] = lst + [vids[j]["id"] for j in longs[:extra]]
    return out


# ---------------------------------------------------------------- the AI grades (cards per part)
def card(v: dict, part: dict) -> dict:
    """What the grader sees of one video. Long chapter lists are cut to the chapters nearest the part (in time order)."""
    ch = E.chapters_of(v)
    n = scfg().get("card_chapters", 12)
    if len(ch) > n:
        s = _cos(_embed([part_text(part)]), _embed([c["title"] for c in ch]))[0]
        keep = sorted(np.argsort(-s)[:n])
        ch = [ch[k] for k in keep]
    kind = "none" if not ch else ("YouTube key moments" if ch[0].get("auto") else "uploader chapters")
    return {"id": v["id"], "title": v["title"], "channel": v.get("channel", ""), "tier": v.get("tier", 4),
            "length": E.ts(v.get("duration_s") or 0), "year": (v.get("published") or "")[:4], "views": v.get("views"),
            "chapters": [f"{E.ts(c['start'])} {c['title'][:45]}" for c in ch], "chapters_from": kind,
            "description": " ".join((v.get("description") or "").split())[:140]}


def _short(n) -> str:
    n = n or 0
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}k" if n >= 1e3 else str(n)


def card_text(c: dict) -> str:
    """One card as 2-3 short lines (17 Nov: as JSON, ~19 cards made 5-6K-token prompts, too long for Groq)."""
    out = f"[{c['id']}] {c['title'][:80]} | {c['channel'][:30]} (tier {c['tier']}) | {c['length']} | {c['year']} | {_short(c['views'])} views"
    if c["chapters"]:
        out += f"\n  chapters ({c['chapters_from']}): " + " · ".join(c["chapters"])
    if c["description"]:
        out += f"\n  about: {c['description']}"
    return out


def grade(llm, lecture: dict, parts: list[dict], sets: dict[int, list[str]], cands: dict, fast: bool, level_note: str,
          trace, run_id: str) -> dict[str, dict[int, dict]]:
    """{video_id: {part: {"g": mean grade 0-3, "n": calls, "where", "reason", "level_ok", "standalone"}}}. Each part is
    graded `orders` times, the cards reversed each time; the calls run in parallel over the free providers."""
    from profsagent.ytlecture import agents as A
    orders = scfg().get("grade_orders", 2)
    jobs = []
    for i, ids in sets.items():
        cards = [card(cands[x], parts[i]) for x in ids if x in cands]
        for o in range(orders):
            jobs.append((i, cards if o % 2 == 0 else cards[::-1]))

    def one(job):
        i, cards = job
        try:
            return i, A.grade_part(llm, lecture, i, parts[i], parts, cards, fast, level_note, trace, run_id)
        except Exception as e:  # noqa: BLE001 — one failed call: the other order still counts
            trace.step(lecture["lecture_id"], f"grading part {i} failed: {type(e).__name__}")
            return i, None
    with ThreadPoolExecutor(max_workers=scfg().get("grade_workers", 4)) as ex:
        res = list(ex.map(one, jobs))
    out: dict[str, dict[int, dict]] = {}
    for i, g in res:
        if g is None:
            continue
        allowed = set(sets[i])
        for x in g.grades:
            if x.video_id not in allowed:
                continue
            cur = out.setdefault(x.video_id, {}).setdefault(i, {"sum": 0.0, "n": 0, "where": "", "reason": "",
                                                                "level_ok": True, "standalone": True})
            cur["sum"] += x.grade
            cur["n"] += 1
            cur["where"] = cur["where"] or x.where
            cur["reason"] = cur["reason"] or x.reason
            cur["level_ok"] = cur["level_ok"] and x.level_ok
            cur["standalone"] = cur["standalone"] and x.standalone
    for per in out.values():
        for d in per.values():
            d["g"] = round(d.pop("sum") / max(1, d["n"]), 2)
    return out


# ---------------------------------------------------------------- the choice (code)
def units(v: dict) -> float:
    """Reading cost: a short video is 1-2 AI calls, a long one a skim plus up to 4 zoom chunks."""
    d = v.get("duration_s") or 0
    return 1.0 if d <= 1200 else 1.5 if d <= 2700 else 2.0 if d <= 4500 else 2.5


def parts_cap(v: dict) -> int:
    """How many parts one reading of a video realistically yields clips for (17 Nov, Transformers W01.L1: three long
    university lectures graded for 4-7 parts each took the first wave and gave 1-4 clips each, while StatQuest's
    graded-3 videos for parts 0 and 1 were never read)."""
    return 2 if (v.get("duration_s") or 0) <= 1200 else 3


def select(G: dict[str, dict], parts: list[dict], cands: dict, prior_of: dict[str, float], budget: float,
           need: dict[int, float] | None = None, exclude: set[str] = frozenset(), have: dict[int, list[float]] | None = None) -> list[dict]:
    """Greedy budgeted coverage. A part's value is its best grades with falling weights (1, 0.55, 0.3: a second and third
    source are worth less than the first), times its minutes and its need (1 = empty; the second round lowers it for
    parts already filled). A video counts for at most parts_cap(v) parts (its most valuable ones). Each step adds the
    video with the best gain per reading unit; at most 3 per channel."""
    c = scfg()
    gmin, w = c.get("min_grade", 1.5), c.get("rank_weights", [1.0, 0.55, 0.3])
    mins = [max(1.0, p["minutes"]) for p in parts]
    mw = [m / (sum(mins) / len(mins)) for m in mins]
    need = need if need is not None else {i: 1.0 for i in range(len(parts))}
    have = {i: list(v) for i, v in (have or {}).items()}

    def pv(gs: list[float]) -> float:
        gs = sorted((g for g in gs if g >= gmin), reverse=True)
        return sum(wk * g / 3 for wk, g in zip(w, gs))

    def value(state: dict[int, list[float]]) -> float:
        return sum(mw[i] * need.get(i, 0) * pv(state.get(i, [])) for i in range(len(parts)))
    chosen, spent, by_ch = [], 0.0, {}
    state = {i: list(have.get(i, [])) for i in range(len(parts))}
    pool = [v for v in G if v in cands and v not in exclude]
    while True:
        base, best = value(state), None
        for v in pool:
            if any(x["video_id"] == v for x in chosen):
                continue
            u = units(cands[v])
            ch = cands[v].get("channel_id") or cands[v].get("channel")
            if spent + u > budget + 1e-9 or by_ch.get(ch, 0) >= c.get("per_channel", 3):
                continue
            # the parts it counts for: those where it adds most, at most parts_cap of them
            alone = {i: mw[i] * need.get(i, 0) * (pv(state[i] + [d["g"]]) - pv(state[i])) for i, d in G[v].items() if i in state}
            use = sorted((i for i in alone if alone[i] > 0), key=lambda i: -alone[i])[: parts_cap(cands[v])]
            st = {i: state[i] + ([G[v][i]["g"]] if i in use else []) for i in state}
            gain = value(st) - base
            if gain <= c.get("min_gain", 0.04):
                continue
            key = (gain + c.get("prior_weight", 0.15) * max(0.0, prior_of.get(v, 0))) / u
            if best is None or key > best[0]:
                best = (key, v, st, u, ch)
        if best is None:
            break
        _, v, state, u, ch = best
        spent += u
        by_ch[ch] = by_ch.get(ch, 0) + 1
        ps = sorted(i for i, d in G[v].items() if d["g"] >= gmin)
        strong = [i for i in ps if G[v][i]["g"] >= 2]
        top = max(G[v].values(), key=lambda d: d["g"])
        chosen.append({"video_id": v, "parts": ps, "fit": max(1, min(5, round(1 + 4 * top["g"] / 3))),
                       "authority": 5 - min(4, cands[v].get("tier", 4)), "level_ok": all(G[v][i]["level_ok"] for i in ps),
                       "likely_standalone": all(G[v][i]["standalone"] for i in ps),
                       "anchor": len(strong) >= 2 and (cands[v].get("duration_s") or 0) >= c.get("anchor_min_s", 1800),
                       "reason": f"grades {', '.join(f'part {i}: {G[v][i]['g']}' for i in ps)}; {top['reason'][:120]}",
                       "where": {str(i): G[v][i]["where"] for i in ps if G[v][i]["where"]}})
    return chosen
