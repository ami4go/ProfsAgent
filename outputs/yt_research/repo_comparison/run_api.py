"""The official YouTube Data API, the way yt-pipeline calls it (search.list + videos.list), 20 results per query.
Cost: 100 + 1 units a query. The key is read from D:/BTP/.env and never printed."""
import json
import re
import sys
import time

import httpx

QF, OUT = sys.argv[1], sys.argv[2]
key = re.search(r"^YOUTUBE_API_KEY=(.*)$", open("D:/BTP/.env", encoding="utf-8").read(), re.M).group(1).strip().strip('"')
API = "https://www.googleapis.com/youtube/v3"


def iso(d):
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d or "")
    if not m:
        return None
    dd, h, mi, s = (int(x or 0) for x in m.groups())
    return dd * 86400 + h * 3600 + mi * 60 + s


out = []
with httpx.Client(timeout=30) as c:
    for q in json.load(open(QF, encoding="utf-8"))["queries"]:
        t = time.time()
        r = c.get(f"{API}/search", params={"q": q["q"], "part": "snippet", "type": "video", "maxResults": 20,
                                         "order": "relevance", "regionCode": "IN", "relevanceLanguage": "en", "key": key})
        if r.status_code != 200:
            out.append({**q, "secs": round(time.time() - t, 2), "error": f"HTTP {r.status_code}", "results": []})
            print(q["lecture"], q["part"], "error", r.status_code, flush=True)
            if r.status_code == 403:
                break
            continue
        ids = [i["id"]["videoId"] for i in r.json().get("items", [])]
        d = c.get(f"{API}/videos", params={"part": "snippet,statistics,contentDetails", "id": ",".join(ids), "key": key}).json()
        by = {i["id"]: i for i in d.get("items", [])}
        res = []
        for vid in ids:
            i = by.get(vid)
            if not i:
                continue
            res.append({"id": vid, "title": i["snippet"]["title"], "channel": i["snippet"]["channelTitle"],
                        "duration_s": iso(i["contentDetails"].get("duration")), "views": int(i["statistics"].get("viewCount", 0)),
                        "published": i["snippet"]["publishedAt"][:10]})
        out.append({**q, "secs": round(time.time() - t, 2), "error": "", "results": res})
        print(q["lecture"], q["part"], len(res), out[-1]["secs"], flush=True)
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)
