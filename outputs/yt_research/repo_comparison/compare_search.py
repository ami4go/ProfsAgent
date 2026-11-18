"""Compare the three search sources on the same 33 CS601 part queries, against the manual gold and the engine's pool."""
import json
import re
import sys
from collections import defaultdict

sys.path.insert(0, "D:/BTP/src")
from profsagent.ytlecture import tools as T  # noqa: E402

Q = json.load(open("queries.json", encoding="utf-8"))
gold, engine = Q["gold"], set(Q["engine_candidates"])
allgold = {v for l in gold.values() for v in l}


def dur_s(r):
    if r.get("duration_s"):
        return r["duration_s"]
    d = r.get("duration") or ""
    if re.fullmatch(r"\d+(:\d+){1,2}", d):
        s = 0
        for p in d.split(":"):
            s = s * 60 + int(p)
        return s
    return None


def year(r):
    p = str(r.get("published") or "")
    if re.match(r"\d{4}", p):
        return int(p[:4])
    m = re.search(r"(\d+)\s*(years?|y|months?|mo|weeks?|w|days?|d|hours?|h)", p)
    if m:
        n, u = int(m.group(1)), m.group(2)
        months = n * 12 if u.startswith("y") else n if u.startswith("mo") else 0
        return 2026 if months < 11 else 2026 - (months + 1) // 12
    return None


res = {"youtube-for-ai-agents (youtubei.js)": json.load(open("res_ytai.json", encoding="utf-8"))["search"],
       "irotechlab-yt-search (InnerTube)": json.load(open("res_iro.json", encoding="utf-8")),
       "YouTube Data API (yt-pipeline)": json.load(open("res_api.json", encoding="utf-8")),
       "yt-dlp (ytsearch20)": json.load(open("res_ytdlp.json", encoding="utf-8")),
       "scrapetube": json.load(open("res_scrapetube.json", encoding="utf-8")),
       "youtube-search-python (httpx<0.28)": json.load(open("res_ysp.json", encoding="utf-8"))}
sets = {}
print("| Source | Videos (unique) | Gold found (of 37) | Gold in a top 10 | In engine pool | New to engine | ≥ 20 min | Tier 1-2 | 2025+ | s/query |")
print("|---|---|---|---|---|---|---|---|---|---|")
for name, rows in res.items():
    vids, by_lec, top10 = {}, defaultdict(set), set()
    for q in rows:
        for k, r in enumerate(q["results"]):
            vids[r["id"]] = r
            by_lec[q["lecture"]].add(r["id"])
            if k < 10 and r["id"] in set(gold.get(q["lecture"], [])):
                top10.add((q["lecture"], r["id"]))
    g = sum(len(set(gold[l]) & by_lec[l]) for l in gold)
    any_g = {v for l in gold for v in set(gold[l]) & by_lec[l]}
    sets[name] = set(vids)
    n = len(vids)
    long_ = sum(1 for r in vids.values() if (dur_s(r) or 0) >= 1200)
    t12 = sum(1 for r in vids.values() if T.tier(r.get("channel", "")) <= 2)
    new = sum(1 for r in vids.values() if (year(r) or 0) >= 2025)
    secs = sum(q["secs"] for q in rows) / max(1, len(rows))
    print(f"| {name} | {n} | {g} ({len(any_g)} distinct) | {len(top10)} | {len(set(vids) & engine)} | {len(set(vids) - engine)} | "
          f"{round(100 * long_ / n)}% | {round(100 * t12 / n)}% | {round(100 * new / n)}% | {secs:.2f} |")
names = list(sets)
print()
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        a, b = sets[names[i]], sets[names[j]]
        print(f"overlap {names[i][:22]} vs {names[j][:22]}: {len(a & b)} shared, Jaccard {len(a & b) / len(a | b):.2f}")
u = set().union(*sets.values())
print("union", len(u), "gold in union", len(allgold & u), "gold in engine pool", len(allgold & engine), "gold in union not in engine", sorted(allgold & u - engine))
print("gold in engine OR union", len(allgold & (u | engine)))
# snippets from captions (youtubei.js only)
yt = res["youtube-for-ai-agents (youtubei.js)"]
cap = sum(1 for q in yt for r in q["results"] if any("Automatic captions" in s or "captions" in s.lower() for s in r.get("snippets", [])))
print("youtubei.js results whose snippet comes from the CAPTIONS (YouTube matched the spoken words):", cap, "of", sum(len(q["results"]) for q in yt))
