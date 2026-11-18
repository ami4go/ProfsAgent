"""clip-finder's approach as a LOCATOR: chunk a transcript with its own chunker (60 s, sentence-aware, 12 s overlap),
embed chunks and the part, and see whether the top chunks land on the clips our verifier accepted.
Embeddings: our local all-MiniLM (clip-finder uses gemini-embedding-001; not used here). Optional: the local
cross-encoder re-ranks the top 15 chunks. No network calls (cached transcripts only)."""
import glob
import json
import random
import sys

import numpy as np

REPO = sys.argv[1]
sys.path.insert(0, "D:/BTP/src")
sys.path.insert(0, REPO + "/backend")
from youtube_utils import chunk_transcript_entries  # noqa: E402  (clip-finder's own chunker)

from profsagent.delivery.common import embed  # noqa: E402
from profsagent.ytlecture.evaluate import read_json_tx  # noqa: E402
from profsagent.ytlecture import shortlist as SL  # noqa: E402

pairs = []
for f in glob.glob("D:/BTP/runs/*/delivery/ytlecture/state/M?.T?.json"):
    d = json.load(open(f, encoding="utf-8"))
    plans = {lp["lecture_id"]: lp["parts"] for lp in d["plan"]["lectures"]}
    for lid, l in d["lectures"].items():
        for k in l.get("clips") or []:
            chk = k.get("check") or {}
            if k["part"] < 0 or chk.get("coverage", 0) < 0.5 or not chk.get("recommend", True):
                continue
            p = plans[lid][k["part"]]
            pairs.append((k["video"], f"{p['title']}. {p['teaches']} " + " ".join(p.get("must_cover", [])[:4]), k["a"], k["b"]))
random.seed(0)
seen, cases = set(), []
for v, q, a, b in pairs:
    if (v, q) in seen:
        continue
    seen.add((v, q))
    rows = read_json_tx(v)
    if not rows:
        continue
    dur = rows[-1]["start"] + rows[-1].get("dur", 0)
    if dur < 900:            # locating only matters inside long videos
        continue
    cases.append((v, q, a, b, rows, dur))
print("cases (verified clip in a video ≥ 15 min, cached words):", len(cases))
hit1 = hit3 = rhit3 = ce1 = ce3 = 0
for v, q, a, b, rows, dur in cases:
    ch = chunk_transcript_entries([{"text": r["text"], "start": r["start"], "duration": r.get("dur", 0)} for r in rows])
    cv = embed([c["text"] for c in ch])
    qv = embed([q])[0]
    s = cv @ qv / (np.linalg.norm(cv, axis=1) * np.linalg.norm(qv) + 1e-9)
    order = list(np.argsort(-s))
    ov = lambda c: min(b, c["end_seconds"]) - max(a, c["start_seconds"]) >= 20  # noqa: E731
    hit1 += ov(ch[order[0]])
    hit3 += any(ov(ch[j]) for j in order[:3])
    rnd = random.sample(range(len(ch)), min(3, len(ch)))
    rhit3 += any(ov(ch[j]) for j in rnd)
    top = order[:15]
    ce = SL.cross_scores([(q, ch[j]["text"]) for j in top])
    if ce is not None:
        o2 = [top[j] for j in np.argsort(-ce)]
        ce1 += ov(ch[o2[0]])
        ce3 += any(ov(ch[j]) for j in o2[:3])
n = max(1, len(cases))
print(f"MiniLM top-1 lands on the verified clip: {hit1}/{n} ({100 * hit1 // n}%)")
print(f"MiniLM top-3: {hit3}/{n} ({100 * hit3 // n}%)   random 3 chunks: {rhit3}/{n} ({100 * rhit3 // n}%)")
print(f"+ cross-encoder top-1: {ce1}/{n} ({100 * ce1 // n}%)  top-3: {ce3}/{n} ({100 * ce3 // n}%)")
