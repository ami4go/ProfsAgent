"""Which minutes of which YouTube video teach each component (architecture aid A4, rebuilt 2026-11-01).

The 28 Oct run matched one 45-second window per video against the topic's title, so 18 of 33 clips started in the
first minute (where a video announces its topic) and most were 90 s long. Now:

  locate  — per component, the transcript (30 s windows) is compared with the component's own description (title,
            what it teaches, key terms); the similarity is smoothed over 3 windows, so a stretch must stay on the
            component; a stretch grows while it stays near its peak, snaps to the creator's chapter when one contains
            it, and is kept between 2 and 25 minutes. Best stretches per component, one per video.
  check   — the AI reads each stretch's transcript (D6) and says whether it teaches the component fully, partly or only
            mentions it, with the exact start and end markers (intros, plugs and outros left out).
  choose  — per component the best checked segment (fully > partly; clarity, level, length close to the component's
            minutes, source; a video already used in the lecture is preferred); a partial segment gets a second one
            from another video. Components no segment teaches go to the NotebookLM pack; activities and discussions
            are taught in class.
"""
from __future__ import annotations

import re

import numpy as np

from profsagent.delivery.common import embed, hms, rcfg
from profsagent.delivery.coverage import windows_from_transcript
from profsagent.delivery.models import SegmentChecks

TS = re.compile(r"^\s*[\[(]?((?:\d{1,2}:)?\d{1,2}:\d{2})[\])]?\s*[-–—:|]?\s*(.+?)\s*$")


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


def _smooth(x: np.ndarray, k: int) -> np.ndarray:
    if k <= 1 or len(x) < k:
        return x
    pad = k // 2
    xp = np.pad(x, (pad, k - 1 - pad), mode="edge")
    return np.convolve(xp, np.ones(k) / k, mode="valid")


def video_windows(v: dict) -> list[dict]:
    if "_win" not in v:
        v["_win"] = windows_from_transcript(v["_tr"], rcfg()["segments"]["window_s"]) if v.get("_tr") else []
        v["_wvec"] = embed([w["text"] for w in v["_win"]]) if v["_win"] else None
    return v["_win"]


def locate(comps: list[dict], videos: list[dict]) -> dict[str, list[dict]]:
    """Candidate stretches per component id: [{vid, start, end, peak, chapter}] best first, one per video."""
    cfg = rcfg()["segments"]
    usable = [v for v in videos if v.get("_tr") and (v.get("duration_s") or 0) >= cfg["min_video_s"]]
    if not comps or not usable:
        return {}
    cv = embed([component_text(c) for c in comps])
    out: dict[str, list[dict]] = {c["id"]: [] for c in comps}
    for v in usable:
        win = video_windows(v)
        if not win:
            continue
        sims = v["_wvec"] @ cv.T                          # windows × components
        chap = chapters(v.get("description", ""), v.get("duration_s"))
        total = win[-1]["end"]
        for j, c in enumerate(comps):
            sm = _smooth(sims[:, j], cfg["smooth"])
            p = int(np.argmax(sm))
            peak = float(sm[p])
            if peak < cfg["sim_floor"]:
                continue
            lo = hi = p
            while lo > 0 and sm[lo - 1] >= peak - cfg["drop_from_peak"]:
                lo -= 1
            while hi < len(sm) - 1 and sm[hi + 1] >= peak - cfg["drop_from_peak"]:
                hi += 1
            start, end, ch = win[lo]["start"], win[hi]["end"], None
            for x in chap:                                # the creator's own section that contains the peak
                if x["start"] <= win[p]["start"] < x["end"] and cfg["min_s"] <= x["end"] - x["start"] <= cfg["max_s"]:
                    if start - x["start"] < 120:          # the chapter begins shortly before: start with it
                        start = min(start, x["start"])
                    if x["end"] - end < 120:              # ... and ends shortly after: end with it
                        end = max(end, x["end"])
                    ch = x["title"]
                    break
            if end - start < cfg["min_s"]:                # too short to teach: widen around the peak
                grow = (cfg["min_s"] - (end - start)) / 2
                start, end = max(0.0, start - grow), min(total, end + grow)
            if end - start > cfg["max_s"]:                # too long for one component: centre on the peak
                mid = (win[p]["start"] + win[p]["end"]) / 2
                start, end = max(0.0, mid - cfg["max_s"] / 2), min(total, mid + cfg["max_s"] / 2)
            out[c["id"]].append({"vid": v["id"], "start": round(start, 1), "end": round(end, 1), "peak": round(peak, 3),
                                 "chapter": ch})
    tier = {v["id"]: v.get("tier", 4) for v in usable}
    for k in out:
        out[k] = sorted(out[k], key=lambda s: -(s["peak"] + 0.02 * (4 - tier[s["vid"]])))[: cfg["per_component"]]
    return out


def transcript_text(v: dict, start: float, end: float, max_words: int) -> str:
    """The stretch's transcript with a [m:ss] marker every window; long stretches are sampled evenly."""
    win = [w for w in video_windows(v) if w["end"] > start - 1 and w["start"] < end + 1]
    if not win:
        return ""
    idx = list(range(len(win)))
    while sum(len(win[i]["text"].split()) for i in idx) > max_words and len(idx) > 2:
        # drop every other window from the middle (start and end markers are what the AI must place)
        idx = idx[:1] + idx[1:-1][::2] + idx[-1:] if len(idx) > 6 else idx[:1] + idx[2:]
    out, last = [], None
    for i in idx:
        if last is not None and i != last + 1:
            out.append("[…]")
        out.append(f"[{hms(win[i]['start'])}] {win[i]['text']}")
        last = i
    return "\n".join(out)


def check(llm, b: dict, st: dict, comps: list[dict], cands: dict[str, list[dict]], videos: dict, run_id: str, log) -> list[dict]:
    """D6 on every candidate stretch; returns the checked stretches with verdict and refined start/end (seconds)."""
    from profsagent.delivery.resources import llm_call
    cfg = rcfg()["segments"]
    by_id = {c["id"]: c for c in comps}
    items = []
    for cid, ss in cands.items():
        for s in ss:
            v = videos[s["vid"]]
            text = transcript_text(v, s["start"], s["end"], cfg["max_words_per_stretch"])
            if text:
                items.append({**s, "cid": cid, "_text": text})
    done, batch, words = [], [], 0

    def flush():
        nonlocal batch, words
        if not batch:
            return
        for i, s in enumerate(batch):
            s["sid"] = f"s{i + 1}"
        ctx = {"lecture": {"topic": b["topic"], "course_level": st.get("level")},
               "stretches": [{"id": s["sid"], "component": {k: by_id[s["cid"]][k] for k in ("title", "teaches", "key_terms", "minutes")},
                              "video": videos[s["vid"]]["title"], "channel": videos[s["vid"]].get("source"),
                              "stretch": f"{hms(s['start'])}–{hms(s['end'])}", "transcript": s["_text"]} for s in batch]}
        try:
            res = llm_call(llm, "D6", ctx, SegmentChecks, run_id, log)
            got = {x.id: x.model_dump() for x in res.checks}
        except Exception as e:  # noqa: BLE001 — unchecked stretches are never used to teach a component
            log(f"  [D6] failed for {b['lecture_id']} ({type(e).__name__}); {len(batch)} stretches left unchecked")
            got = {}
        for s in batch:
            r = got.get(s["sid"])
            if not r:
                continue
            s.update(verdict=r["verdict"], covered=r["covered"], missing=r["missing"], clarity=r["clarity"],
                     level_fit=r["level_fit"], note=r["note"])
            a, z = secs(r["start"]), secs(r["end"])
            # the AI's markers must lie inside the stretch it was shown; otherwise keep the located stretch
            if a is not None and z is not None and s["start"] - 60 <= a < z <= s["end"] + 60 and z - a >= cfg["min_segment_s"]:
                s["start"], s["end"] = max(0.0, a - cfg["pad_s"]), z
                s["refined"] = True
            done.append(s)
        batch, words = [], 0

    for s in items:
        n = len(s["_text"].split())
        if batch and words + n > cfg["max_words_per_call"]:
            flush()
        batch.append(s)
        words += n
    flush()
    for s in done:
        s.pop("_text", None)
        s.pop("sid", None)
    return done


def _len_fit(seg_min: float, comp_min: float) -> float:
    r = seg_min / max(comp_min, 1)
    if 0.5 <= r <= 1.5:
        return 1.0
    return max(0.4, 1 - 0.35 * abs(np.log2(r / (1.5 if r > 1.5 else 0.5))))


def seg_score(s: dict, comp: dict, v: dict) -> float:
    w = {"teaches_fully": 1.0, "teaches_partly": 0.55}.get(s.get("verdict"), 0.0)
    q = ((s.get("clarity") or 3) + (s.get("level_fit") or 3)) / 10
    auth = rcfg()["tier_scores"][v.get("tier", 4)]
    return round(w * (0.5 + 0.5 * q) * _len_fit((s["end"] - s["start"]) / 60, comp["minutes"]) * (0.85 + 0.15 * auth), 3)


def choose(comps: list[dict], checked: list[dict], videos: dict) -> tuple[list[dict], list[dict]]:
    """Per component: the segments that deliver it (best first). Returns (timeline, alternatives)."""
    used_vids: set[str] = set()
    taken: list[dict] = []                                # segments already given to another component

    def overlap(s: dict) -> float:                        # share of s already used for another part of the lecture
        o = max((min(s["end"], x["end"]) - max(s["start"], x["start"]) for x in taken if x["vid"] == s["vid"]), default=0)
        return max(0.0, o) / max(s["end"] - s["start"], 1)
    timeline, alts = [], []
    by_c: dict[str, list[dict]] = {}
    for s in checked:
        if s.get("verdict") in ("teaches_fully", "teaches_partly"):
            by_c.setdefault(s["cid"], []).append(s)
    for c in comps:
        row = {"component": c["id"], "title": c["title"], "minutes": c["minutes"], "kind": c.get("kind"), "segments": []}
        if c.get("in_class"):
            row["delivery"] = "in_class"
            timeline.append(row)
            continue
        cands = by_c.get(c["id"], [])
        for s in cands:
            # the same minutes rarely teach two different parts well: prefer another stretch when there is one
            s["score"] = round(seg_score(s, c, videos[s["vid"]]) + (0.05 if s["vid"] in used_vids else 0)
                               - (0.15 if overlap(s) > 0.5 else 0), 3)
        cands.sort(key=lambda s: -s["score"])
        if cands:
            best = cands[0]
            row["segments"].append(best)
            if best["verdict"] == "teaches_partly":       # a second video for what the first leaves out
                other = next((s for s in cands[1:] if s["vid"] != best["vid"]), None)
                if other:
                    row["segments"].append(other)
            used_vids |= {s["vid"] for s in row["segments"]}
            taken += row["segments"]
            alts += [s for s in cands if s not in row["segments"]]
        row["delivery"] = "video" if row["segments"] else "notebooklm"
        if row["segments"]:                               # what the chosen video minutes still leave out
            got = sum(s["end"] - s["start"] for s in row["segments"]) / 60
            fully = any(s["verdict"] == "teaches_fully" for s in row["segments"])
            if not fully or got < rcfg()["segments"]["gap_share"] * c["minutes"]:
                covered = {m.lower() for s in row["segments"] for m in s.get("covered", [])}
                missing = list(dict.fromkeys(m for s in row["segments"] for m in s.get("missing", []) if m.lower() not in covered))
                row["gap"] = {"video_minutes": round(got, 1), "missing": missing[:6]}
        timeline.append(row)
    return timeline, alts
