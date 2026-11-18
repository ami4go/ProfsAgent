"""Deterministic assembly: score every checked clip, then choose each part's clips in teaching order (METHODS §6-7).

No AI here. The same inputs always give the same playlist, and every choice can be explained from the numbers.
"""
from __future__ import annotations

import itertools
import re

from profsagent.delivery.common import years_since
from profsagent.ytlecture.tools import cfg


def score(k: dict, v: dict, part: dict, fast: bool) -> tuple[float, list[str]]:
    """(score 0-1, reasons it is lower) for one clip of one part."""
    s, why = cfg()["scoring"], []
    n = max(1, len(part["must_cover"]))
    chk = k.get("check")
    if chk:
        cov = chk["coverage"]
        stand = chk["standalone"] and k["standalone"]
    else:
        cov = 0.7 * len(k["covers"]) / n                     # the reader's own claim, discounted: nobody checked it
        stand = k["standalone"]
        why.append("not verified by a second model")
    t = v.get("tier", 4)
    age = years_since(v.get("published")) or 0
    horizon = 2.5 if fast else 6.0
    rec = max(0.0, 1 - age / horizon)
    val = (s["coverage"] * cov + s["rating"] * k["rating"] / 5 + s["tier"] * (5 - t) / 4 + s["standalone"] * stand
           + s["recency"] * rec)
    if k["evidence"] == "chapters":
        val -= s["chapters_only_penalty"]
        why.append("placed from chapters only")
    elif k["evidence"] == "notes":
        val -= s["notes_penalty"]
        why.append("placed from AI notes, not captions")
    if k["level"] != "right":
        val -= 0.08
        why.append(f"level: {k['level'].replace('_', ' ')}")
    if k.get("quote_notes"):
        val -= 0.03 * len(k["quote_notes"])
    if not stand:   # 17 Nov audit: 18-24% of chosen minutes needed earlier context of their video; it cost only 0.10
        val -= s.get("not_standalone_penalty", 0.06)
        why.append("needs earlier context of its video")
    if chk and not chk["recommend"]:
        val -= 0.12
        why.append(f"second reader had doubts: {chk.get('issue') or 'none given'}")
    elif chk and not chk["accurate"]:
        val -= 0.12
        why.append(f"second reader questioned a claim (may be newer than its knowledge): {chk.get('issue') or ''}")
    return round(max(val, 0.0), 3), why


_CAPTION = re.compile(r"transcri|caption|typo|misspel|mis-?hear|garbled|spelling", re.I)
_RECENT = re.compile(r"deprecat|no longer|newer|latest|new version|released|recent|replaced|now support|renamed|"
                     r"as of 20|outdated|superseded|current spec", re.I)


def soft_inaccuracy(issue: str, fast: bool) -> bool:
    """An "inaccurate" verdict that is about caption errors, or (on a fast-moving topic) about what is new or deprecated,
    is not a veto: the verifier's knowledge may be older than the video (16 Nov: "speaker incorrectly states SSE is
    deprecated" vetoed 22 min of correct MCP teaching)."""
    return bool(_CAPTION.search(issue)) or (fast and bool(_RECENT.search(issue)))


def gate(k: dict, fast: bool, v: dict) -> str | None:
    """Why a clip may not be shown at all, or None."""
    s = cfg()["scoring"]
    chk = k.get("check")
    if chk:
        # The second reader's "would not show it" vetoes only a clip that also covers under half of its part; otherwise
        # it is a score penalty (first W01.L2 run: strict must-cover points made it veto every partial clip of a part).
        if not chk["recommend"] and chk["coverage"] < s["gate_min_coverage"]:
            return f"second reader would not show it ({chk.get('issue') or 'no reason given'})"
        if not chk["accurate"] and not soft_inaccuracy(chk.get("issue") or "", fast):
            return f"inaccurate: {chk.get('issue')}"
        if chk["coverage"] < s["gate_min_coverage"] and k["evidence"] != "chapters":
            return f"covers only {round(100 * chk['coverage'])}% of the part's points"
    if k["rating"] < s["gate_min_rating"]:
        return f"rated {k['rating']}/5"
    if fast and v.get("published") and (v["published"][:4]).isdigit() and int(v["published"][:4]) < cfg()["filter"]["fast_moving_min_year"]:
        return f"from {v['published'][:4]}; the topic changes fast"
    return None


def _cov(k: dict, part: dict) -> float:
    chk = k.get("check")
    if chk:
        return chk["coverage"]
    return 0.7 * len(k["covers"]) / max(1, len(part["must_cover"]))


def union_cov(combo, part: dict) -> float:
    """Share of the part's points that the clips cover together (verifier's per-point weights, else the reader's claim)."""
    n = max(1, len(part["must_cover"]))
    best: dict[str, float] = {}
    for k in combo:
        chk = k.get("check") or {}
        pts = chk.get("points")
        if pts is None:
            pts = {str(i): (0.7 if not chk else chk["coverage"]) for i in k["covers"]}
        for i, w in pts.items():
            best[i] = max(best.get(i, 0.0), w)
    return sum(best.values()) / n


def repeats(combo, part: dict) -> int:
    """How many clips of a combination only repeat the others: from a video not otherwise in it, adding under
    topup_min_gain of the part's points. One such second explanation is allowed; 17 Nov W02.L1 had three
    "queries, keys, values -> scaled dot-product" intros in one part."""
    gain = cfg()["lecture"].get("topup_min_gain", 0.1)
    n, before = 0, []
    for k in sorted(combo, key=lambda x: -(x.get("score") or 0)):      # each clip against the better ones before it
        if before and not any(x["video"] == k["video"] for x in before) and \
                union_cov(before + [k], part) - union_cov(before, part) < gain:
            n += 1
        before.append(k)
    return n


def overlap(a: dict, b: dict) -> float:
    if a["video"] != b["video"]:
        return 0.0
    return max(0.0, min(a["b"], b["b"]) - max(a["a"], b["a"]))


def choose(lec: dict, clips: list[dict], videos: dict[str, dict], fast: bool, taken: list[dict]) -> dict:
    """Pick 1-2 clips per part, in order. `taken`: clips used by earlier lectures of the topic (never repeated)."""
    c = cfg()["lecture"]
    parts = lec["parts"]
    for k in clips:
        pdef = parts[k["part"]] if k["part"] >= 0 else {"must_cover": [k.get("extra_title") or "extra"]}
        k["score"], k["score_notes"] = score(k, videos[k["video"]], pdef, fast)
        k["gate"] = gate(k, fast, videos[k["video"]])
    chosen: list[dict] = []
    plan = []
    prev_video = None
    for i, p in enumerate(parts):
        target = p["minutes"] * 60
        opts = sorted([k for k in clips if k["part"] == i and not k["gate"]
                       and all(overlap(k, x) < 30 for x in chosen + taken)], key=lambda k: -k["score"])[:8]
        best, best_val, partial = None, -1.0, False
        combos = [(k,) for k in opts]
        for n in range(2, c["max_clips_per_part"] + 1):       # 2-3 clips for a long part (no two may overlap)
            combos += [x for x in itertools.combinations(opts[:6], n)
                       if all(overlap(a, b) < 30 for a, b in itertools.combinations(x, 2))][:40]
        for combo in combos:
            length = sum(k["b"] - k["a"] for k in combo)
            fill = length / target
            if fill > c["part_fill_max"] or repeats(combo, p) > 1:
                continue
            val = sum(k["score"] * (k["b"] - k["a"]) for k in combo) / length
            if len(combo) > 1:                         # complementary clips: credit what they cover together
                val += cfg()["scoring"]["coverage"] * (union_cov(combo, p) - max(_cov(k, p) for k in combo))
            val -= 0.25 * max(0.0, 0.85 - fill) + 0.1 * max(0.0, fill - 1.25)        # far from the planned minutes
            val -= 0.04 * (len(combo) - 1)                                            # a switch between videos costs a little
            if prev_video and combo[0]["video"] == prev_video:
                val += cfg()["scoring"]["continuity"]
            if fill < c["part_fill_min"]:
                val -= 0.3
            if val > best_val:
                best, best_val, partial = combo, val, fill < c["part_fill_min"]
        if best:                                                # short is "partly covered", never "dropped"
            ordered = sorted(best, key=lambda k: (k["video"] != (prev_video or ""), k["a"]))
            chosen.extend(ordered)
            prev_video = ordered[-1]["video"]
            plan.append({"part": i, "clips": ordered, "partial": partial})
            if repeats(best, p):
                plan[-1]["second_explanation"] = min(best, key=lambda k: k.get("score") or 0)["video"]
        else:
            plan.append({"part": i, "clips": [], "partial": False})
            prev_video = None
    # over the slot: drop the weakest second clips until it fits
    slot = lec["slot_minutes"] * 60
    def total():
        return sum(k["b"] - k["a"] for pp in plan for k in pp["clips"])
    while total() > c["fill_max"] * slot:
        seconds = [(k["score"], pp, k) for pp in plan if len(pp["clips"]) > 1 for k in pp["clips"]]
        if not seconds:
            break
        _, pp, k = min(seconds, key=lambda x: x[0])
        pp["clips"].remove(k)
    # EXTRA clips (on-topic stretches that match no planned part; 16 Nov: the planned parts' clips alone filled only ~42%
    # of the slot because a strong source spends 3-5 min on one narrow sub-topic). Added best first until the lecture
    # reaches its target, each placed after the planned part it is closest to.
    target_s = c.get("fill_target", 0.85) * slot
    extras = sorted([k for k in clips if k["part"] == -1 and not k["gate"]], key=lambda k: -k["score"])
    used = [k for pp in plan for k in pp["clips"]]
    added = []
    for k in extras:
        length = k["b"] - k["a"]
        if total() + sum(x["b"] - x["a"] for x in added) >= target_s:
            break
        if total() + sum(x["b"] - x["a"] for x in added) + length > c["fill_max"] * slot:
            continue
        if k["score"] < cfg()["scoring"].get("extra_min_score", 0.55) or any(overlap(k, x) >= 30 for x in used + added + taken):
            continue
        added.append(k)
    if added:
        from profsagent.delivery.common import embed
        import numpy as np
        pv = embed([p["title"] + ". " + p.get("teaches", "") for p in parts])
        ev = embed([k["extra_title"] for k in added])
        sim = (ev @ pv.T) / (np.linalg.norm(ev, axis=1, keepdims=True) * np.linalg.norm(pv, axis=1) + 1e-9)
        after = {id(k): int(np.argmax(sim[j])) for j, k in enumerate(added)}
        new_plan = []
        for pp in plan:
            new_plan.append(pp)
            for k in added:
                if after[id(k)] == pp["part"]:
                    new_plan.append({"part": -1, "title": k["extra_title"], "clips": [k], "partial": False, "extra": True})
        plan = new_plan
    # TOP-UP (16 Nov r8: W03.L2 had 137 min of checked clips but used 76, because each part stops near its planned
    # minutes while parts without video leave their minutes unused). Still under the target: let well-taught parts grow
    # up to topup_part_max x their planned minutes with their next best clips, best score first.
    used = [k for pp in plan for k in pp["clips"]]
    if total() < target_s:
        by_part = {pp["part"]: pp for pp in plan if pp["part"] >= 0 and pp["clips"]}
        pool = sorted([k for k in clips if k["part"] in by_part and not k["gate"] and k not in used
                       and k["score"] >= cfg()["scoring"].get("extra_min_score", 0.55)], key=lambda k: -k["score"])
        for k in pool:
            length = k["b"] - k["a"]
            pp = by_part[k["part"]]
            cap = c.get("topup_part_max", 2.0) * parts[k["part"]]["minutes"] * 60
            if total() >= target_s:
                break
            if (total() + length > c["fill_max"] * slot or sum(x["b"] - x["a"] for x in pp["clips"]) + length > cap
                    or len(pp["clips"]) >= c["max_clips_per_part"] + 1
                    or any(overlap(k, x) >= 30 for x in used + taken)):
                continue
            # no padding by repetition: a clip from another video must add points the part does not have yet (first
            # top-up: W03.L2 played three separate "the JSON-RPC message shapes" intros back to back)
            # ...but ONE second explanation per part is allowed (another teacher on the same core idea, 17 Nov: StatQuest's
            # RNN explanation after MIT's), with a higher bar
            p = parts[k["part"]]
            continues = any(x["video"] == k["video"] for x in pp["clips"])
            repeat = not continues and union_cov(pp["clips"] + [k], p) - union_cov(pp["clips"], p) < c.get("topup_min_gain", 0.1)
            # 18 Nov, Transformers W02.L1 at 45 of 90 min: clips scoring 0.68-0.75 were refused as repeats. A part still never
            # plays three EXPLANATIONS of the same points (17 Nov rule), but while the lecture is under fill_min one more
            # clip of those points is allowed when it teaches them differently (a demo after two explanations).
            if repeat:
                n = repeats(pp["clips"], p)
                short = total() < c["fill_min"] * slot
                differs = k.get("treatment") not in {x.get("treatment") for x in pp["clips"]}
                if k["score"] < c.get("topup_repeat_min_score", 0.6) or \
                        (n >= 1 and not (short and differs and n < c.get("topup_repeats_short", 2))):
                    continue
            if repeat:
                pp["second_explanation"] = k["video"]
            first = {}
            for x in pp["clips"] + [k]:
                first.setdefault(x["video"], len(first))
            pp["clips"] = sorted(pp["clips"] + [k], key=lambda x: (first[x["video"]], x["a"]))
            pp["topped_up"] = True
            used.append(k)
    tot = total()
    by_video: dict[str, int] = {}
    for pp in plan:
        for k in pp["clips"]:
            by_video[k["video"]] = by_video.get(k["video"], 0) + k["b"] - k["a"]
    warnings = []
    if tot and max(by_video.values()) / tot > c["max_share_one_video"]:
        vid = max(by_video, key=by_video.get)
        warnings.append(f"{round(100 * by_video[vid] / tot)}% of the lecture is one video ({videos[vid]['title'][:60]})")
    gaps = [pp["part"] for pp in plan if pp["part"] >= 0 and not pp["clips"]]
    fill = tot / slot if slot else 0
    status = "ready" if fill >= c["fill_min"] and not gaps else ("usable_with_gaps" if fill >= 0.4 else "not_enough_video")
    return {"plan": plan, "total_s": tot, "fill": round(fill, 2), "gaps": gaps, "status": status, "warnings": warnings}
