"""How many hand-picked videos survive each step of choosing what to read (17 Nov). Free and quick: no YouTube quota,
no AI calls unless --grade.

Gold = the manual playlists (outputs/yt_research/cs601_first6/playlists.json, one list of videos per lecture). For each
gold lecture it reports, of the gold videos that are among the engine's candidates (course-wide pool):
  cards   shown to the AI with full metadata (grade mode: any part's cards; list mode: the 45-video pool)
  roster  shown as title-only in the list mode's authoritative roster
  top3    ranked in the top 3 of some part by code alone
  picked  (--grade) chosen for the first reading wave after the AI grades

  python scripts/bench_shortlist.py --run cs601-02                # ranking only
  python scripts/bench_shortlist.py --run cs601-02 --no-pages     # without the watch-page fetch
  python scripts/bench_shortlist.py --run cs601-02 --grade        # also the AI grades + choice (~2 calls per part)
"""
from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="cs601-02")
    ap.add_argument("--gold", default=str(ROOT / "outputs/yt_research/cs601_first6/playlists.json"))
    ap.add_argument("--no-pages", action="store_true", help="skip the watch-page fetch (key moments)")
    ap.add_argument("--no-cross", action="store_true", help="skip the local cross-encoder")
    ap.add_argument("--keep-reputation", action="store_true", help="let the benchmarked run's own results count (leaks)")
    ap.add_argument("--grade", action="store_true", help="also run the AI grading and the choice (spends free-tier calls)")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    from profsagent.ytlecture import shortlist as SL
    from profsagent.ytlecture import tools as T
    from profsagent.ytlecture.orchestrator import Orchestrator
    if a.no_cross:
        SL.scfg()["cross_weight"] = 0
    gl = json.load(open(a.gold, encoding="utf-8"))
    topics = {g["id"]: g.get("topic", "") for g in gl}
    gold = {g["id"]: [c["video"] for p in g["parts"] for c in p["clips"]] for g in gl}
    gold = {k: list(dict.fromkeys(v)) for k, v in gold.items()}
    files = sorted(glob.glob(str(ROOT / "runs" / a.run / "delivery" / "ytlecture" / "state" / "M*.T*.json")))
    states = [json.load(open(f, encoding="utf-8")) for f in files if ".bak" not in f]
    allc: dict[str, dict] = {}
    for s in states:
        allc.update(s.get("candidates") or {})
    for v in allc.values():
        v["tier"] = T.tier(v.get("channel", ""))
    exclude = None if a.keep_reputation else a.run
    llm = None
    if a.grade:
        from profsagent.llm.client import LLMClient
        llm = LLMClient(ROOT / "runs" / a.run / "delivery" / "ytlecture" / "bench_llm_calls.jsonl")
    tot = {"gold": 0, "cand": 0, "nominee_list": 0, "nominated": 0, "cards": 0, "reachable": 0, "roster": 0, "top3": 0, "picked": 0}
    for s in states:
        level = (s.get("plan") or {}).get("level_note", "")
        for lp in (s.get("plan") or {}).get("lectures", []):
            lid, parts = lp["lecture_id"], lp["parts"]
            if lid not in gold:
                continue
            g = set(gold[lid])
            inc = g & set(allc)
            R = SL.rank(parts, allc, lid, s.get("scout"), exclude_run=exclude, pages=not a.no_pages)
            pool, ranked, roster = Orchestrator.prerank(None, parts, allc, lid, s.get("scout"), R=R)
            nom_list = {r["id"] for r in SL.nominee_rows(R, parts)}
            lecture = {"lecture_id": lid, "topic": topics.get(lid, ""), "slot_minutes": lp["slot_minutes"]}
            nom = {}
            if a.grade:
                from profsagent.ytlecture.tools import Trace
                tr = Trace()
                nom = SL.nominations(llm, lecture, parts, R, bool((s.get("plan") or {}).get("fast_moving")), tr, "bench")
            sets = SL.grade_sets(R, parts, nominated=nom)
            cards = {x for ids in sets.values() for x in ids}
            top3 = {x for ids in SL.per_part_lists(R, 3, 2).values() for x in ids}
            row = {"gold": len(g), "cand": len(inc), "nominee_list": len(inc & nom_list), "nominated": len(inc & {x for v in nom.values() for x in v}),
                   "cards": len(inc & cards), "reachable": len(inc & (cards | nom_list)), "roster": len(inc & {v["id"] for v in roster} - cards),
                   "top3": len(inc & top3), "picked": 0}
            if a.grade:
                G = SL.grade(llm, lecture, parts, sets, allc, bool((s.get("plan") or {}).get("fast_moving")), level, tr, "bench")
                prior_of = {v["id"]: float(p) for v, p in zip(R["vids"], R["prior"]) if v["id"] in G}
                o = Orchestrator.__new__(Orchestrator)
                picks = SL.select(G, parts, allc, prior_of, o.reading_units(lecture) * SL.scfg().get("first_wave", 0.7))
                row["picked"] = len(inc & {p["video_id"] for p in picks})
                if a.verbose:
                    for p in picks:
                        print(f"   pick {p['video_id']} {'GOLD ' if p['video_id'] in g else ''}{p['parts']} "
                              f"{allc[p['video_id']]['title'][:60]} | {p['reason'][:80]}")
            for k in tot:
                tot[k] += row[k]
            print(lid, row, f"(cards {len(cards)}, pool {len(pool)}, roster {len(roster)})")
            if a.verbose:
                for x in sorted(inc - cards):
                    v = allc[x]
                    print(f"   not on a card: {x} tier {v['tier']} | {v.get('channel', '')[:24]} | {v['title'][:70]}")
    print("TOTAL", tot)


if __name__ == "__main__":
    main()
