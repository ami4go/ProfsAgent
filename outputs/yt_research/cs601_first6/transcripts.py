"""Step 3: fetch transcripts for the shortlist (paced: YouTube blocks fast transcript scraping). Saves tx/<id>.txt as '[m:ss] text' lines."""
import json, sys, time
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / "src")); load_dotenv(ROOT / ".env")
from profsagent.delivery.sources import transcript, transcript_known, transcripts_blocked
D = Path(__file__).parent / "tx"; D.mkdir(exist_ok=True)
ids = [l.split()[0] for l in (Path(__file__).parent / "shortlist.txt").read_text().splitlines() if l.strip() and not l.startswith("#")]
def ts(s): s = int(s); return f"{s//3600}:{s%3600//60:02d}:{s%60:02d}" if s >= 3600 else f"{s//60}:{s%60:02d}"
for v in ids:
    f = D / f"{v}.txt"
    if f.exists(): continue
    known = transcript_known(v); t = transcript(v)
    if t is None:
        print(v, "NONE", "blocked" if transcripts_blocked() else ""); 
        if transcripts_blocked(): break
        continue
    # merge into ~20 s lines for reading
    lines, cur, start = [], [], None
    for s in t:
        if start is None: start = s["start"]
        cur.append(s["text"].replace("\n", " "))
        if s["start"] + s["dur"] - start >= 20: lines.append(f"[{ts(start)}] {' '.join(cur)}"); cur, start = [], None
    if cur: lines.append(f"[{ts(start)}] {' '.join(cur)}")
    f.write_text("\n".join(lines), encoding="utf-8"); print(v, "ok", len(lines), "cached" if known else "", flush=True)
