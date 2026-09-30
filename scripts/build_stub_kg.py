"""Build the STUB Layer A from the IIIT-D course directory.

  python scripts/build_stub_kg.py            # fetch (cached) + parse all courses
  python scripts/build_stub_kg.py --no-fetch # re-parse cached sheets only

Outputs:
  data/raw/courses.json                     raw index (cached)
  data/raw/sheets/<uid>.csv                 raw sheet exports (cached, sha256 in manifest)
  data/stub_kg/index.json                   normalised index rows
  data/stub_kg/courses/<uid>.json           parsed sheet + index row
  data/stub_kg/manifest.json                fetch metadata
Gold-set codes (data/gold_set.txt) keep only a stub index row: their sheets are never fetched.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from profsagent.kg.sheet_parser import norm_codes, parse_sheet_csv  # noqa: E402

# Small stub: enough for the design pipeline to have realistic neighbours. The full crawl is the KG teammate's job.
STUB_SET = ["CSE101", "CSE102", "CSE201", "CSE202", "CSE231", "CSE222", "CSE343", "CSE503", "CSE581", "CSE582",
            "CSE583", "CSE584", "CSE594A", "CSE600", "CSE665", "CSE701", "CSE508"]
INDEX_URL = "https://techtree.iiitd.edu.in/static/Courses.json"
RAW = ROOT / "data" / "raw"
OUT = ROOT / "data" / "stub_kg"


def load_gold() -> set[str]:
    p = ROOT / "data" / "gold_set.txt"
    if not p.exists():
        return set()
    return {l.split("#")[0].strip().upper() for l in p.read_text().splitlines() if l.split("#")[0].strip()}


def normalise_index_row(r: dict) -> dict:
    codes = norm_codes(r.get("Course Code", ""))
    name = (r.get("Course Name") or "").split(" # ")[0].strip()
    m = re.search(r'src="([^"]+)"', r.get("embed_link", ""))
    sheet = m.group(1).replace("&amp;", "&") if m else None
    csv_url = re.sub(r"pubhtml\?.*$", "pub?output=csv", sheet) if sheet else None
    uid = codes[0] if codes else f"X{r.get('Serial Number')}"
    level = int(re.search(r"\d", uid).group()) if re.search(r"\d", uid) else None
    def clean(v):
        v = (v or "").strip()
        return None if v.lower() in ("", "none", "nil", "na", "n/a") else v
    return {
        "uid": uid,
        "aliases": codes,
        "name": name,
        "credits": int(r["Credits"]) if str(r.get("Credits", "")).isdigit() else None,
        "level": level,
        "semester": clean(r.get("Semester")),
        "professor": clean(r.get("Professor")),
        "cluster": clean(r.get("Cluster")),
        "prereq_index": clean(r.get("Prerequisites")),
        "prereq_pref_index": clean(r.get("Preferable_Prerequisites")),
        "anti_index": clean(r.get("Antirequisites")),
        "csv_url": csv_url,
        "catalogue_url": "https://techtree.iiitd.edu.in" + r.get("Link", ""),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-fetch", action="store_true")
    ap.add_argument("--delay", type=float, default=0.4)
    ap.add_argument("--only", default=",".join(STUB_SET), help="comma-separated uids to fetch/parse")
    args = ap.parse_args()
    (RAW / "sheets").mkdir(parents=True, exist_ok=True)
    (OUT / "courses").mkdir(parents=True, exist_ok=True)
    gold = load_gold()

    idx_path = RAW / "courses.json"
    if not idx_path.exists() and not args.no_fetch:
        idx_path.write_bytes(httpx.get(INDEX_URL, timeout=60, verify=False).content)
    rows = [normalise_index_row(r) for r in json.loads(idx_path.read_text(encoding="utf-8"))["data"]]

    # merge duplicate uids (same primary code listed twice): keep first, note duplicates
    seen: dict[str, dict] = {}
    for r in rows:
        if r["uid"] in seen:
            seen[r["uid"]].setdefault("duplicates", []).append(r["name"])
        else:
            seen[r["uid"]] = r
    rows = list(seen.values())

    manifest = json.loads((OUT / "manifest.json").read_text()) if (OUT / "manifest.json").exists() else {}
    client = httpx.Client(timeout=40, follow_redirects=True)
    stats = {"fetched": 0, "cached": 0, "failed": 0, "gold_stub": 0, "parsed": 0, "no_cos": 0}
    only = {c.strip().upper() for c in args.only.split(",") if c.strip()}
    for i, r in enumerate(rows):
        uid = r["uid"]
        if only and not (set(r["aliases"]) & only):
            continue
        is_gold = any(a in gold for a in r["aliases"])
        r["is_gold_stub"] = is_gold
        dest = RAW / "sheets" / f"{uid}.csv"
        if is_gold:
            stats["gold_stub"] += 1
            (OUT / "courses" / f"{uid}.json").write_text(json.dumps({"index": r}, indent=1), encoding="utf-8")
            continue
        if not dest.exists() and not args.no_fetch and r["csv_url"]:
            try:
                resp = client.get(r["csv_url"])
                resp.raise_for_status()
                dest.write_bytes(resp.content)
                manifest[uid] = {"url": r["csv_url"], "sha256": hashlib.sha256(resp.content).hexdigest(),
                                 "fetched_at": datetime.now(timezone.utc).isoformat()}
                stats["fetched"] += 1
                time.sleep(args.delay)
            except Exception as e:  # noqa: BLE001
                manifest[uid] = {"url": r["csv_url"], "error": f"{type(e).__name__}: {e}"[:200]}
                stats["failed"] += 1
                print(f"[fail] {uid}: {e}", flush=True)
                continue
        elif dest.exists():
            stats["cached"] += 1
        if not dest.exists():
            continue
        parsed = parse_sheet_csv(dest.read_text(encoding="utf-8", errors="replace"))
        stats["parsed"] += 1
        stats["no_cos"] += int(not parsed["cos"])
        (OUT / "courses" / f"{uid}.json").write_text(json.dumps({"index": r, "sheet": parsed}, indent=1, ensure_ascii=False), encoding="utf-8")
        if (i + 1) % 50 == 0:
            print(f"{i + 1}/{len(rows)} {stats}", flush=True)
    (OUT / "index.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False), encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1), encoding="utf-8")
    print("done", stats)


if __name__ == "__main__":
    main()
