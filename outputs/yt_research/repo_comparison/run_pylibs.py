"""The four Python libraries on the same 33 queries, 20 video results each. One library per run:
  python run_pylibs.py <lib> queries.json res_<lib>.json      lib = ysp | ytdlp | scrapetube | pytubefix"""
import json
import re
import sys
import time
import traceback

LIB, QF, OUT = sys.argv[1], sys.argv[2], sys.argv[3]


def secs(t):
    t = str(t or "")
    if re.fullmatch(r"\d+(:\d+){1,2}", t):
        s = 0
        for p in t.split(":"):
            s = s * 60 + int(p)
        return s
    return None


def run_ysp(q):
    from youtubesearchpython import VideosSearch
    r = VideosSearch(q, limit=20).result()["result"]
    return [{"id": v["id"], "title": v["title"], "channel": (v.get("channel") or {}).get("name", ""),
             "duration_s": secs(v.get("duration")), "views": (v.get("viewCount") or {}).get("text"),
             "published": v.get("publishedTime")} for v in r]


def run_ytdlp(q):
    import yt_dlp
    with yt_dlp.YoutubeDL({"extract_flat": True, "quiet": True, "no_warnings": True, "skip_download": True}) as y:
        r = y.extract_info(f"ytsearch20:{q}", download=False)
    return [{"id": v["id"], "title": v.get("title"), "channel": v.get("channel") or v.get("uploader") or "",
             "duration_s": int(v["duration"]) if v.get("duration") else None, "views": v.get("view_count"),
             "published": v.get("upload_date") or ""} for v in r.get("entries", [])]


def run_scrapetube(q):
    import scrapetube
    out = []
    for v in scrapetube.get_search(q, limit=20, results_type="video"):
        t = "".join(x.get("text", "") for x in (v.get("title") or {}).get("runs", []))
        ch = "".join(x.get("text", "") for x in (v.get("ownerText") or v.get("longBylineText") or {}).get("runs", []))
        out.append({"id": v.get("videoId"), "title": t, "channel": ch,
                    "duration_s": secs((v.get("lengthText") or {}).get("simpleText")),
                    "views": (v.get("viewCountText") or {}).get("simpleText"),
                    "published": (v.get("publishedTimeText") or {}).get("simpleText")})
    return out


def run_pytubefix(q):
    from pytubefix import Search
    s = Search(q)
    vids = list(s.videos)[:20]
    out = []
    for v in vids:
        # title/author come from the search page; length and views trigger a per-video fetch, so they are skipped
        out.append({"id": v.video_id, "title": v.title, "channel": getattr(v, "_author", None) or "",
                    "duration_s": None, "views": None, "published": ""})
    return out


fn = {"ysp": run_ysp, "ytdlp": run_ytdlp, "scrapetube": run_scrapetube, "pytubefix": run_pytubefix}[LIB]
res = []
for q in json.load(open(QF, encoding="utf-8"))["queries"]:
    t = time.time()
    try:
        r, err = fn(q["q"]), ""
    except Exception as e:  # noqa: BLE001
        r, err = [], f"{type(e).__name__}: {e}"[:200]
        if not res:
            traceback.print_exc()
    res.append({**q, "secs": round(time.time() - t, 2), "error": err, "results": r})
    print(LIB, q["lecture"], q["part"], len(r), res[-1]["secs"], err[:100], flush=True)
    time.sleep(1.0)
json.dump(res, open(OUT, "w", encoding="utf-8"), indent=1)
