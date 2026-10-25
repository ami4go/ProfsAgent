"""Does a resource actually cover the lecture's topic and learning outcomes — and where?

Videos: the transcript is cut into windows of ~45 s; each window and each target (the topic, each LO) are embedded
locally; a target is covered when some window is at least `sim_covered` similar. Neighbouring covering windows are
merged into segments, which give the timestamps of clip playlists ("watch 12:30–31:00 for X").
Pages: the same, over chunks of ~120 words (no timestamps).
"""
from __future__ import annotations

import numpy as np

from profsagent.delivery.common import embed, rcfg


def windows_from_transcript(tr: list[dict], window_s: float | None = None) -> list[dict]:
    window_s = window_s or rcfg()["coverage"]["window_s"]
    out, cur, start = [], [], None
    for s in tr:
        if start is None:
            start = s["start"]
        cur.append(s["text"].replace("\n", " "))
        end = s["start"] + s.get("dur", 0)
        if end - start >= window_s:
            out.append({"start": start, "end": end, "text": " ".join(cur)})
            cur, start = [], None
    if cur:
        out.append({"start": start, "end": tr[-1]["start"] + tr[-1].get("dur", 0), "text": " ".join(cur)})
    return out


def chunks_from_text(text: str, words: int | None = None) -> list[dict]:
    words = words or rcfg()["coverage"]["page_chunk_words"]
    w = text.split()
    return [{"start": None, "end": None, "text": " ".join(w[i:i + words])} for i in range(0, len(w), words)][:120]


def coverage(chunks: list[dict], targets: list[dict], sim_covered: float | None = None) -> dict:
    """{score, per_target: {id: {sim, covered, segments:[{start,end,sim}]}}, best_excerpt}.
    score = fraction of targets covered, the topic counting double (it is what the lecture is about)."""
    th = sim_covered if sim_covered is not None else rcfg()["coverage"]["sim_covered"]
    if not chunks or not targets:
        return {"score": 0.0, "per_target": {}, "best_excerpts": [], "evidence": "none"}
    cv = embed([c["text"] for c in chunks])
    tv = embed([t["text"] for t in targets])
    sims = tv @ cv.T                                   # targets × chunks
    per, total, got = {}, 0.0, 0.0
    gap, min_len = rcfg()["coverage"]["segment_gap_s"], rcfg()["coverage"]["min_segment_s"]
    for i, t in enumerate(targets):
        best = float(sims[i].max())
        covered = best >= th
        segs = []
        if covered and chunks[0]["start"] is not None:
            seg_th = max(th, best - 0.12)              # the stretch that teaches it, not every passing mention
            idx = [j for j in range(len(chunks)) if sims[i, j] >= seg_th]
            for j in idx:
                s, e = chunks[j]["start"], chunks[j]["end"]
                if segs and s - segs[-1]["end"] <= gap:
                    segs[-1]["end"] = e
                    segs[-1]["sim"] = max(segs[-1]["sim"], float(sims[i, j]))
                else:
                    segs.append({"start": s, "end": e, "sim": float(sims[i, j])})
            segs = [s for s in segs if s["end"] - s["start"] >= min_len] or segs[:1]
            total_len = chunks[-1]["end"] or 0
            intro = rcfg()["coverage"].get("intro_skip_s", 45)
            # in longer videos the opening minute only announces the topic: prefer the part that teaches it
            segs = sorted(segs, key=lambda s: -(s["sim"] - (0.06 if total_len > 300 and s["start"] < intro else 0)))[:3]
            clip_min = rcfg()["coverage"].get("clip_min_s", 90)
            for s in segs:                              # extend short clips forward to a usable length
                if s["end"] - s["start"] < clip_min:
                    s["end"] = min(total_len or s["start"] + clip_min, s["start"] + clip_min)
        w = 2.0 if t["kind"] == "topic" else 1.0
        total += w
        got += w * min(1.0, max(0.0, (best - (th - 0.10)) / 0.25))   # graded: 0 at th-0.10, full credit at th+0.15
        per[t["id"]] = {"text": t["text"], "sim": round(best, 3), "covered": covered,
                        "segments": [{"start": round(s["start"], 1), "end": round(s["end"], 1), "sim": round(s["sim"], 3)} for s in segs]}
    top = np.argsort(-sims.max(axis=0))[:3]
    return {"score": round(got / total, 3), "per_target": per,
            "best_excerpts": [chunks[j]["text"][:500] for j in sorted(top)], "evidence": "transcript" if chunks[0]["start"] is not None else "text"}
