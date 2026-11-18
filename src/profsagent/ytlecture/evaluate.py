"""Is a mode-2 run good enough? Fixed criteria per lecture, plus a spot-check printout of each chosen clip's first and last
words (from the cached transcript), so a person can confirm in a minute that each clip really teaches its part.

    python -m profsagent.ytlecture.evaluate cs601-02 W02.L1,W02.L2 [--spot]

Satisfactory lecture (all must hold):
  fill        video time >= 65% of the slot
  parts       at most one part with no clip, and that part <= 20% of the planned minutes
  coverage    minutes-weighted verifier coverage of the chosen (verified) clips >= 0.5
  unverified  <= 25% of the minutes not checked by a second model
  sources     >= 40% of the minutes from tier 1-2 sources (primary/university/established educators), or mean score >= 0.6
  preview     <= 30% of the minutes placed from chapters or AI notes only
"""
from __future__ import annotations

import json
import sys

from profsagent.delivery.common import out_dir, read_json
from profsagent.ytlecture.evidence import plain, ts
from profsagent.ytlecture.tools import tier

CRITERIA = {"fill": 0.65, "coverage": 0.5, "sources": 0.4, "preview": 0.3, "score": 0.6, "unverified": 0.25}


def lecture_metrics(L: dict) -> dict:
    clips = [c for p in L["parts"] for c in p["clips"]]
    secs = sum(c["clip_s"] for c in clips) or 1
    planned = sum(p["minutes"] for p in L["parts"]) or 1
    gap_parts = [p for p in L["parts"] if p["gap"]]
    # 17 Nov audit: unverified clips counted as coverage 0, mixing "not checked" with "teaches nothing"; and the stored
    # tier went stale when the tier lists changed. Coverage is over verified clips; the unverified share is its own check.
    ver = [c for c in clips if (c.get("verifier") or {}).get("coverage") is not None]
    vsecs = sum(c["clip_s"] for c in ver) or 1
    cov = sum(c["verifier"]["coverage"] * c["clip_s"] for c in ver) / vsecs
    unverified = 1 - sum(c["clip_s"] for c in ver) / secs if clips else 0.0
    tier12 = sum(c["clip_s"] for c in clips if tier(c.get("channel") or "") <= 2) / secs
    preview = sum(c["clip_s"] for c in clips if c["check"] in ("chapters", "notes")) / secs
    score = sum((c.get("score") or 0) * c["clip_s"] for c in clips) / secs
    m = {"fill": L["video_total_s"] / (L["slot_min"] * 60), "gaps": len(gap_parts),
         "gap_share": sum(p["minutes"] for p in gap_parts) / planned, "coverage": cov, "tier12": tier12,
         "preview": preview, "score": score, "unverified": unverified, "clips": len(clips), "videos": len({c["video"] for c in clips})}
    fails = []
    if m["fill"] < CRITERIA["fill"]:
        fails.append(f"fill {m['fill']:.0%}")
    if m["gaps"] > 1 or m["gap_share"] > 0.2:
        fails.append(f"{m['gaps']} empty parts ({m['gap_share']:.0%} of planned minutes)")
    if clips and m["coverage"] < CRITERIA["coverage"]:
        fails.append(f"coverage {m['coverage']:.2f}")
    if clips and m["tier12"] < CRITERIA["sources"] and m["score"] < CRITERIA["score"]:
        fails.append(f"sources: tier 1-2 {m['tier12']:.0%}, score {m['score']:.2f}")
    if m["unverified"] > CRITERIA["unverified"]:
        fails.append(f"unverified {m['unverified']:.0%}")
    if m["preview"] > CRITERIA["preview"]:
        fails.append(f"preview-only {m['preview']:.0%}")
    m["fails"] = fails
    m["ok"] = not fails
    return m


def report(run_id: str, lectures: list[str] | None = None, spot: bool = False) -> str:
    d = out_dir(run_id) / "ytlecture"
    rows, spots = [], []
    for p in sorted((d / "lectures").glob("*.json")):
        L = read_json(p)
        if not L or (lectures and L["id"] not in lectures):
            continue
        m = lecture_metrics(L)
        rows.append(f"| {L['id']} | {L['topic'][:40]} | {round(L['video_total_s'] / 60)}/{L['slot_min']} | {m['gaps']} | "
                    f"{m['coverage']:.2f} | {m['unverified']:.0%} | {m['tier12']:.0%} | {m['preview']:.0%} | {m['clips']} / {m['videos']} | "
                    f"{'OK' if m['ok'] else 'NO: ' + '; '.join(m['fails'])} |")
        if spot:
            spots.append(f"\n### {L['id']} spot check")
            for part in L["parts"]:
                for c in part["clips"]:
                    tx = read_json_tx(c["video"])
                    head = " ".join(plain(tx, c["a"], c["a"] + 20).split()[:22]) if tx else "(no cached words)"
                    tail = " ".join(plain(tx, c["b"] - 20, c["b"]).split()[-18:]) if tx else ""
                    spots.append(f"- **{part['title'][:50]}** · {c['title'][:50]} {c['start']}–{c['end']}\n  start: \"{head}\"\n  end: \"…{tail}\"")
    out = ["| Lecture | Topic | Video/slot min | Empty parts | Coverage | Unverified | Tier 1-2 | Preview | Clips / videos | Verdict |",
           "|---|---|---|---|---|---|---|---|---|---|"] + rows
    return "\n".join(out + spots)


def read_json_tx(vid: str) -> list[dict] | None:
    """Cached words of a video: captions, else the browser transcript (never a network call)."""
    from profsagent.delivery import sources as S
    d = read_json(S._cache_path("transcript", vid))
    if d and isinstance(d.get("v"), list):
        return d["v"]
    b = read_json(S._cache_path("browser_tx", vid))
    if b and isinstance(b.get("v"), dict) and b["v"].get("rows"):
        return b["v"]["rows"]
    return None


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:  # noqa: BLE001
        pass
    lec = sys.argv[2].split(",") if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
    print(report(sys.argv[1], lec, spot="--spot" in sys.argv))
