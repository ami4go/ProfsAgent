"""yt-pipeline's own flow per lecture: search the TOPIC (50 results, its yt_search.py call), then an AI picks 20 with
its Stage-3 rubric (copied from its SKILL.md). Scored against the manual gold. AI through our client, role ytl_grade
(Groq gpt-oss first; Gemini only 3.6/3.8 flash)."""
import json
import re
import sys
from pathlib import Path

import httpx

sys.path.insert(0, "D:/BTP/src")
from profsagent.llm.client import CallRecord, LLMClient  # noqa: E402

key = re.search(r"^YOUTUBE_API_KEY=(.*)$", open("D:/BTP/.env", encoding="utf-8").read(), re.M).group(1).strip().strip('"')
API = "https://www.googleapis.com/youtube/v3"
gl = json.load(open("D:/BTP/outputs/yt_research/cs601_first6/playlists.json", encoding="utf-8"))
RUBRIC = """From the search results, select the best 20 videos using these criteria:
1. Source credibility — Prefer established channels, verified creators, known institutions, conference talks, and channels with high subscriber counts
2. Relevance — Title and description must directly address the topic
3. Recency — Prefer recent content unless the topic is foundational
4. Diversity — Avoid multiple videos from the same channel; seek varied perspectives
5. Engagement — Higher view counts signal value, but don't override credibility
6. Duration — Prefer substantive content (8+ minutes) over shorts/clips
Return JSON: {"selected": ["video_id", ...]} with exactly 20 ids from the list."""
llm = LLMClient(Path(sys.argv[1]))
out = []
with httpx.Client(timeout=30) as c:
    for g in gl:
        gold = {cl["video"] for p in g["parts"] for cl in p["clips"]}
        r = c.get(f"{API}/search", params={"q": g["topic"], "part": "snippet", "type": "video", "maxResults": 50,
                                         "order": "relevance", "key": key}).json()
        ids = [i["id"]["videoId"] for i in r.get("items", [])]
        d = c.get(f"{API}/videos", params={"part": "snippet,statistics,contentDetails", "id": ",".join(ids), "key": key}).json()
        rows = [{"video_id": i["id"], "title": i["snippet"]["title"], "channel": i["snippet"]["channelTitle"],
                 "views": int(i["statistics"].get("viewCount", 0)), "duration": i["contentDetails"]["duration"],
                 "published_at": i["snippet"]["publishedAt"][:10], "description": i["snippet"]["description"][:200]}
                for i in d.get("items", [])]
        rec = CallRecord(prompt_id="yt-pipeline-stage3", prompt_version="1", role="ytl_grade")
        txt = llm.raw("ytl_grade", RUBRIC, f"Topic: {g['topic']}\n\nSearch results:\n{json.dumps(rows)}", temperature=0.1, record=rec)[0]
        m = re.search(r"\{.*\}", txt or "", re.S)
        sel = (json.loads(m.group(0)).get("selected") if m else []) or []
        sel = [x for x in sel if x in ids][:20]
        out.append({"lecture": g["id"], "topic": g["topic"], "n50": len(ids), "gold": len(gold), "gold_in_50": len(gold & set(ids)),
                    "gold_in_20": len(gold & set(sel)), "model": getattr(rec, "endpoint", "?") if rec else "?",
                    "picked": [(x, next((r["title"][:50] for r in rows if r["video_id"] == x), "")) for x in sel]})
        print(g["id"], g["topic"][:45], "| gold", len(gold), "in 50:", out[-1]["gold_in_50"], "in 20:", out[-1]["gold_in_20"], flush=True)
json.dump(out, open("res_pipeline.json", "w", encoding="utf-8"), indent=1)
