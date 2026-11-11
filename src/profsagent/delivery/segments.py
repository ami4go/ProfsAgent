"""Which minutes of which video teach which parts of a lecture (decided 10 Nov, docs/decisions.md 38).

The question is asked per lecture, not per part: one video may teach the first three parts and nothing else, and those
three should then be one watch of that video, with the rest of the lecture delivered some other way.

  digest  — programs cut a long transcript to the passages closest to the parts (30 s windows, MiniLM, smoothed so a passage
            must stay on a part), from anywhere in the video; a short one is sent whole.
  read    — D9: the AI reads one video against all the parts it may teach and gives each part's start and end. The markers
            are checked against the transcript.
  verify  — D10: a different model reads every word of the clip, without being told why it was picked, and grades it on a
            fixed checklist (the sentences of the part's `teaches` and its key terms), quoting the clip for each point taught.
            Programs check the quotes and compute the coverage.
  gate    — all thresholds must hold (config `videos.gate`). A clip that fails is not suggested at all.
  assign  — among the clips that passed, the best plan for the lecture: a dynamic programme over the parts in teaching order
            that rewards a video continuing into the next part and penalises switching videos.
"""
from __future__ import annotations

import re

import numpy as np

from profsagent.delivery.common import embed, hms, rcfg
from profsagent.delivery.coverage import windows_from_transcript
from profsagent.delivery.models import ClipVerdict, VideoReading
from profsagent.llm.prompts import load_prompt

TS = re.compile(r"^\s*[\[(]?((?:\d{1,2}:)?\d{1,2}:\d{2})[\])]?\s*[-–—:|]?\s*(.+?)\s*$")


def vcfg() -> dict:
    return rcfg()["videos"]


def secs(t: str) -> float | None:
    """'12:30' or '1:02:03' -> seconds."""
    p = (t or "").strip().strip("[]()").split(":")
    if len(p) not in (2, 3) or not all(x.isdigit() for x in p):
        return None
    v = 0
    for x in p:
        v = v * 60 + int(x)
    return float(v)


def chapters(description: str, duration_s: float | None) -> list[dict]:
    """The creator's chapters ('0:00 Intro', '4:12 How tools are listed', ...): YouTube requires the first at 0:00
    and at least three, so anything else is not a chapter list."""
    rows = []
    for line in (description or "").splitlines():
        m = TS.match(line)
        if m and secs(m.group(1)) is not None:
            rows.append((secs(m.group(1)), m.group(2)[:120]))
    rows = sorted(dict(rows).items())
    if len(rows) < 3 or rows[0][0] != 0:
        return []
    ends = [s for s, _ in rows[1:]] + [float(duration_s or rows[-1][0] + 60)]
    return [{"start": s, "end": e, "title": t} for (s, t), e in zip(rows, ends) if e > s]


def component_text(c: dict) -> str:
    terms = ", ".join(c.get("key_terms") or [])
    return f"{c['title']}. {c['teaches']}" + (f" Key terms: {terms}." if terms else "")


def checklist(c: dict) -> list[str]:
    """What the part requires, the same every time it is asked: the sentences of `teaches`, then the key terms."""
    sent = [x.strip(" .") for x in re.split(r"(?<=[.;])\s+", c.get("teaches") or "") if len(x.split()) >= 4]
    return sent[:5] + [f"The term \"{t}\": what it is or does" for t in (c.get("key_terms") or [])[:6]]


# ------------------------------------------------------------------ programs: where in a video each part may be taught
def _smooth(x: np.ndarray, k: int) -> np.ndarray:
    if k <= 1 or len(x) < k:
        return x
    pad = k // 2
    xp = np.pad(x, (pad, k - 1 - pad), mode="edge")
    return np.convolve(xp, np.ones(k) / k, mode="valid")


def video_windows(v: dict) -> list[dict]:
    if "_win" not in v:
        v["_win"] = windows_from_transcript(v["_tr"], vcfg()["window_s"]) if v.get("_tr") else []
        v["_wvec"] = embed([w["text"] for w in v["_win"]]) if v["_win"] else None
    return v["_win"]


def closeness(parts: list[dict], v: dict) -> np.ndarray | None:
    """Windows x parts, smoothed. None when the video has no transcript."""
    if not video_windows(v) or not parts:
        return None
    sims = v["_wvec"] @ embed([component_text(c) for c in parts]).T
    return np.column_stack([_smooth(sims[:, j], vcfg()["smooth"]) for j in range(len(parts))])


def digest(v: dict, sm: np.ndarray, keep_parts: list[int]) -> str:
    """The transcript the AI reads: whole when short, otherwise the windows closest to the parts, taken in turn from each part
    so that one well-matched part cannot use up the words of the others; in time order, with the skips marked."""
    cfg, win = vcfg(), video_windows(v)
    n_words = [len(w["text"].split()) for w in win]
    if sum(n_words) <= cfg["read_whole_words"]:
        chosen = set(range(len(win)))
    else:
        order = {j: list(np.argsort(-sm[:, j])) for j in keep_parts}
        chosen, total = set(), 0
        while total < cfg["max_words_per_read"] and any(order.values()):
            for j in keep_parts:
                while order[j] and int(order[j][0]) in chosen:
                    order[j].pop(0)
                if not order[j]:
                    continue
                i = int(order[j].pop(0))
                for k in range(max(0, i - 1), min(len(win), i + 2)):    # a window and its neighbours: passages, not fragments
                    if k not in chosen:
                        chosen.add(k)
                        total += n_words[k]
                if total >= cfg["max_words_per_read"]:
                    break
    out, last = [], None
    for i in sorted(chosen):
        if last is not None and i != last + 1:
            out.append(f"[… skipped to {hms(win[i]['start'])}]")
        out.append(f"[{hms(win[i]['start'])}] {win[i]['text']}")
        last = i
    return "\n".join(out)


def clip_text(v: dict, start: float, end: float) -> str:
    """Everything said between start and end, with a marker every window. Never sampled: the checker must see all of it."""
    return "\n".join(f"[{hms(w['start'])}] {w['text']}" for w in video_windows(v) if w["end"] > start + 1 and w["start"] < end - 1)


def parse_range(a: str, z: str, v: dict) -> tuple[float, float] | None:
    """The AI's markers as a usable clip: on real windows (the end marker's window is included), moved to a chapter edge
    when one is close, inside the length limits. None when they are not markers of this transcript."""
    cfg, win = vcfg(), video_windows(v)
    s, e = secs(a), secs(z)
    if s is None or e is None or not win or e < s:
        return None
    i = min(range(len(win)), key=lambda k: abs(win[k]["start"] - s))
    j = min(range(len(win)), key=lambda k: abs(win[k]["start"] - e))
    if abs(win[i]["start"] - s) > cfg["window_s"] + 1 or abs(win[j]["start"] - e) > cfg["window_s"] + 1 or j < i:
        return None
    start, end = max(0.0, win[i]["start"] - cfg["pad_s"]), win[j]["end"]
    for ch in chapters(v.get("description", ""), v.get("duration_s")):
        if abs(ch["start"] - start) <= cfg["snap_s"]:
            start = ch["start"]
        if abs(ch["end"] - end) <= cfg["snap_s"]:
            end = ch["end"]
    if not cfg["min_s"] <= end - start <= cfg["max_s"]:
        return None
    return round(start, 1), round(end, 1)


# ------------------------------------------------------------------ D9: read one video against the lecture's parts
def _short(c: dict) -> str:
    return c["id"].split(".")[-1]


def _endpoint_model(ep: str | None) -> str:
    """'provider:model:keyprint', or 'cache(...)' of it, -> 'provider:model', the form exclude_models uses."""
    ep = (ep or "").removeprefix("cache(").removesuffix(")")
    return ep.rsplit(":", 1)[0]


def read(llm, b: dict, st: dict, parts: list[dict], v: dict, run_id: str, log) -> dict:
    """{"findings": [...], "reader": "provider:model", "failed": bool}. Only parts with a close passage are asked about."""
    cfg = vcfg()
    sm = closeness(parts, v)
    if sm is None:
        return {"findings": [], "reader": "", "failed": False}
    near = [j for j in range(len(parts)) if float(sm[:, j].max()) >= cfg["sim_floor"]]
    if not near:
        return {"findings": [], "reader": "", "failed": False}
    p = load_prompt("D9")
    system, user = p.render(lecture={"topic": b["topic"], "course_level": st.get("level")},
                            parts=[{"id": _short(parts[j]), **{k: parts[j].get(k) for k in ("title", "teaches", "key_terms", "minutes")}} for j in near],
                            video={"title": v["title"], "channel": v.get("source"), "duration": hms(v.get("duration_s"))},
                            chapters=[f"{hms(c['start'])} {c['title']}" for c in chapters(v.get("description", ""), v.get("duration_s"))],
                            transcript=digest(v, sm, near))
    try:
        got, rec = llm.structured(system=system, user=user, model_cls=VideoReading, role=p.meta.get("model_class", "read"),
                                  temperature=float(p.meta.get("temperature", 0.1)), prompt_id="D9", prompt_version=p.version, run_id=run_id)
    except Exception as e:  # noqa: BLE001 — an unread video is reported, never treated as "does not teach it"
        log(f"  [D9] failed for {v['id']} ({type(e).__name__})")
        return {"findings": [], "reader": "", "failed": True}
    log(f"  [D9] {v['title'][:60]} via {rec.endpoint} · {rec.prompt_tokens}+{rec.output_tokens} tok")
    by = {_short(parts[j]): j for j in near}
    out = []
    for f in got.parts:
        j = by.get(f.part)
        if j is None or f.teaches == "no":
            continue
        r = parse_range(f.start, f.end, v)
        if r is None:
            continue
        lo, hi = r
        win = video_windows(v)
        inside = [k for k in range(len(win)) if win[k]["end"] > lo and win[k]["start"] < hi]
        out.append({"cid": parts[j]["id"], "vid": v["id"], "start": lo, "end": hi, "claim": f.teaches, "why": f.why,
                    "peak": round(float(sm[inside, j].max()) if inside else 0.0, 3), "chapter": _chapter(v, lo, hi)})
    return {"findings": out, "reader": _endpoint_model(rec.endpoint), "failed": False}


def _chapter(v: dict, lo: float, hi: float) -> str | None:
    for ch in chapters(v.get("description", ""), v.get("duration_s")):
        if ch["start"] <= (lo + hi) / 2 < ch["end"]:
            return ch["title"]
    return None


# ------------------------------------------------------------------ D10: a second model checks each clip
def _tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (s or "").lower())


def quote_found(quote: str, text: str) -> bool:
    """The quote's words appear in the clip, in order, allowing a word or two to differ (captions are copied imperfectly)."""
    q, t = _tokens(quote), " ".join(_tokens(text))
    if len(q) < 3:
        return False
    if " ".join(q) in t:
        return True
    grams = [" ".join(q[i:i + 2]) for i in range(len(q) - 1)]
    return sum(g in t for g in grams) / len(grams) >= 0.5


def quote_time(quote: str, v: dict, start: float, end: float) -> str | None:
    q = set(_tokens(quote))
    win = [w for w in video_windows(v) if w["end"] > start and w["start"] < end]
    if not q or not win:
        return None
    return hms(max(win, key=lambda w: len(q & set(_tokens(w["text"]))))["start"])


def verify(llm, b: dict, st: dict, c: dict, f: dict, v: dict, reader: str, run_id: str, log) -> dict | None:
    """The finding with the checker's grades, the coverage programs computed, and `failed_gate` (empty when it passes).
    None when no model other than the reader could answer, or the clip is too long to be read whole."""
    cfg = vcfg()
    text = clip_text(v, f["start"], f["end"])
    if not text or len(text.split()) > cfg["max_words_per_clip"]:
        return None
    pts = checklist(c)
    source = "notes" if v.get("evidence") == "notes" else "captions"
    p = load_prompt("D10")
    system, user = p.render(lecture={"topic": b["topic"], "course_level": st.get("level")},
                            part={k: c.get(k) for k in ("title", "teaches", "key_terms", "kind", "minutes")},
                            checklist=[{"n": i, "point": x} for i, x in enumerate(pts, 1)], source=source, transcript=text)
    try:
        got, rec = llm.structured(system=system, user=user, model_cls=ClipVerdict, role=p.meta.get("model_class", "verify"),
                                  temperature=float(p.meta.get("temperature", 0.0)), prompt_id="D10", prompt_version=p.version,
                                  run_id=run_id, exclude_models=frozenset({reader} if reader else set()))
    except Exception as e:  # noqa: BLE001 — unchecked means not suggested
        log(f"  [D10] failed for {v['id']} {_short(c)} ({type(e).__name__})")
        return None
    return score_clip(f, got, pts, c, v, text, _endpoint_model(rec.endpoint), reader)


def score_clip(f: dict, got: ClipVerdict, pts: list[str], c: dict, v: dict, text: str, checker: str, reader: str) -> dict:
    """Programs, not the model, decide which points count and whether the clip passes."""
    by = {x.n: x for x in got.points}
    covered, missing, evidence, bad = [], [], [], 0
    notes = v.get("evidence") == "notes"
    for i, point in enumerate(pts, 1):
        x = by.get(i)
        if x and x.status == "taught" and (notes or quote_found(x.quote, text)):
            covered.append(point)
            evidence.append({"point": point, "quote": x.quote[:160], "at": quote_time(x.quote, v, f["start"], f["end"])})
        else:
            bad += bool(x and x.status == "taught")       # the model said taught but the words are not in the clip
            missing.append(point)
    cov = round(len(covered) / max(len(pts), 1), 2)
    out = {**f, "verdict": "teaches_fully", "verified": True, "relevance": got.relevance, "sufficiency": got.sufficiency, "coverage": cov,
           "covered": covered, "missing": missing, "evidence": evidence, "quotes_not_found": bad, "clean_start": got.clean_start, "clean_end": got.clean_end,
           "stands_alone": got.stands_alone, "clarity": got.clarity, "level_fit": got.level_fit, "strengths": got.strengths[:3],
           "limitations": got.limitations[:3], "note": "; ".join(got.strengths[:2])[:200], "checker": checker, "reader": reader,
           "source": "notes" if notes else "captions"}
    out["failed_gate"] = gate(out, c)
    return out


def gate(clip: dict, c: dict) -> list[str]:
    """Why the clip may not be suggested for this part; empty when it may. Length is only bounded from below here (a block's
    length is judged in `assign`)."""
    g = vcfg()["gate"]
    why = [f"{k} {clip[k]} < {g[k]}" for k in ("relevance", "sufficiency", "coverage", "clean_start", "clean_end", "stands_alone", "clarity", "level_fit")
           if clip[k] < g[k]]
    share = (clip["end"] - clip["start"]) / 60 / max(c["minutes"], 1)
    if share < g["min_share_in_block"]:
        why.append(f"only {round(100 * share)}% of the part's minutes")
    return why


# ------------------------------------------------------------------ the plan for the lecture
def utility(clip: dict, v: dict) -> float:
    """Above 1 for any clip that passed, so a part is never left without one to save a switch. Coverage counts most; the
    channel's standing is a tie-break and views do not count at all: popularity must not lift a clip that teaches less."""
    q = (clip["sufficiency"] + clip["clarity"] + clip["level_fit"] + clip["stands_alone"]) / 20
    edges = (clip["clean_start"] + clip["clean_end"]) / 10
    return round(1 + 0.5 * clip["coverage"] + 0.3 * q + 0.1 * edges + 0.1 * rcfg()["tier_scores"][v.get("tier", 4)], 3)


def _same_watch(a: dict, b: dict) -> bool:
    """b follows a in the same video, close enough to be one watch (the two may overlap where one idea leads to the next)."""
    return a["vid"] == b["vid"] and a["start"] <= b["start"] and b["start"] - a["end"] <= vcfg()["block_gap_s"]


def _overlap(a: dict, b: dict) -> float:
    if a["vid"] != b["vid"]:
        return 0.0
    return max(0.0, min(a["end"], b["end"]) - max(a["start"], b["start"])) / max(min(a["end"] - a["start"], b["end"] - b["start"]), 1)


def _best_path(parts: list[dict], options: dict[str, list[dict]], videos: dict) -> list[dict | None]:
    """Viterbi over the parts in teaching order; a part may take no clip (only when none is left for it)."""
    cfg = vcfg()
    layers = [[None] + (options.get(c["id"], []) if not c.get("in_class") else []) for c in parts]

    def step(a, b):
        if a is None or b is None:
            return 0.0
        return cfg["continue_bonus"] if _same_watch(a, b) else -cfg["switch_penalty"]
    best = [[(0.0 if s is None else utility(s, videos[s["vid"]]), -1) for s in layers[0]]] if layers else []
    for i in range(1, len(layers)):
        row = []
        for s in layers[i]:
            gain = 0.0 if s is None else utility(s, videos[s["vid"]])
            k = max(range(len(layers[i - 1])), key=lambda p: best[i - 1][p][0] + step(layers[i - 1][p], s))
            row.append((best[i - 1][k][0] + step(layers[i - 1][k], s) + gain, k))
        best.append(row)
    if not best:
        return []
    k = max(range(len(best[-1])), key=lambda p: best[-1][p][0])
    path = [None] * len(layers)
    for i in range(len(layers) - 1, -1, -1):
        path[i] = layers[i][k]
        k = best[i][k][1]
    return path


def blocks_of(parts: list[dict], path: list[dict | None]) -> list[list[int]]:
    """Runs of consecutive parts delivered by one continuous watch of one video (a run of one is a block too)."""
    out = []
    for i, s in enumerate(path):
        if s is None:
            continue
        if out and out[-1][-1] == i - 1 and _same_watch(path[i - 1], s):
            out[-1].append(i)
        else:
            out.append([i])
    return out


def _problem(parts: list[dict], path: list[dict | None], videos: dict) -> tuple[int, str] | None:
    """(index of the part whose clip must go, why) for the first thing wrong with this plan, or None."""
    cfg = vcfg()
    g = cfg["gate"]
    blocks = blocks_of(parts, path)
    block_of = {i: k for k, b in enumerate(blocks) for i in b}
    for b in blocks:
        clips = [path[i] for i in b]
        watch = (max(s["end"] for s in clips) - min(s["start"] for s in clips)) / 60
        share = watch / max(sum(parts[i]["minutes"] for i in b), 1)
        if not g["min_share"] <= share <= g["max_share"]:
            i = min(b, key=lambda x: utility(path[x], videos[path[x]["vid"]]))
            return i, f"{round(watch, 1)} min of video for {sum(parts[x]['minutes'] for x in b)} min of class"
    idx = [i for i, s in enumerate(path) if s is not None]
    for x, i in enumerate(idx):
        for j in idx[x + 1:]:
            if block_of[i] != block_of[j] and _overlap(path[i], path[j]) > cfg["reuse_overlap"]:
                lose = min((i, j), key=lambda n: utility(path[n], videos[path[n]["vid"]]))
                return lose, "the same minutes already teach another part"
    return None


def assign(parts: list[dict], clips: list[dict], videos: dict, taken: list[dict] | None = None) -> dict:
    """{path: clip or None per part, alternatives, dropped}. `clips`: all that passed the gate; `taken`: clips another lecture
    of the topic already uses (the same minutes are not assigned twice in a course)."""
    options: dict[str, list[dict]] = {}
    dropped = []
    for s in clips:
        if any(_overlap(s, t) > vcfg()["reuse_overlap"] for t in taken or []):
            dropped.append({**s, "dropped": "already used in an earlier lecture"})
        else:
            options.setdefault(s["cid"], []).append(s)
    for _ in range(sum(len(v) for v in options.values()) + 1):
        path = _best_path(parts, options, videos)
        p = _problem(parts, path, videos)
        if p is None:
            break
        i, why = p
        s = path[i]
        options[s["cid"]] = [x for x in options[s["cid"]] if x is not s]
        dropped.append({**s, "dropped": why})
    used = {id(s) for s in path if s is not None}
    alts = [s for v in options.values() for s in v if id(s) not in used]
    return {"path": path, "alternatives": alts, "dropped": dropped}
