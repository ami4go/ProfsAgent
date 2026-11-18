"""Print a transcript as one line per ~N seconds, first W words of each: a quick map to find where topics change."""
import re, sys
from pathlib import Path
vid, every, words = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 60, int(sys.argv[3]) if len(sys.argv) > 3 else 28
def sec(t): p = [int(x) for x in t.split(":")]; return sum(v * 60 ** i for i, v in enumerate(reversed(p)))
last = -10**9
for l in (Path(__file__).parent / "tx" / f"{vid}.txt").read_text(encoding="utf-8").splitlines():
    m = re.match(r"\[([\d:]+)\] (.*)", l)
    if m and sec(m[1]) - last >= every:
        last = sec(m[1]); print(f"[{m[1]}] {' '.join(m[2].split()[:words])}")
