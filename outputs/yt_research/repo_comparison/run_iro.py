"""irotechlab-yt-search (InnerTube, Python): 20 video results per query."""
import asyncio
import json
import sys
import time

REPO, QF, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, REPO)
from irotechlab_yt_search import YouTubeSearch  # noqa: E402


async def main():
    qs = json.load(open(QF, encoding="utf-8"))["queries"]
    s = YouTubeSearch()
    out = []
    for q in qs:
        t = time.time()
        try:
            vids = await s.search(q["q"], max_results=20, filter_type="video", region_code="IN", language="en")
            err = ""
        except Exception as e:  # noqa: BLE001
            vids, err = [], f"{type(e).__name__}: {e}"[:160]
        out.append({**q, "secs": round(time.time() - t, 2), "error": err,
                    "results": [{"id": v.id, "title": v.title, "channel": v.channel, "duration_s": v.duration_seconds,
                                 "views": v.view_count, "published": v.published} for v in vids]})
        print(q["lecture"], q["part"], len(vids), out[-1]["secs"], err, flush=True)
        await asyncio.sleep(1.0)
    await s.client.close()
    json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1)


asyncio.run(main())
