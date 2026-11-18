"""Step 1 of the CS601 YouTube research: candidate discovery.

Every query goes through the project's own cached YouTube client (src/profsagent/delivery/sources.py), so a rerun costs no quota.
Writes candidates.json: every video found, with its metadata and which query found it.
Run from D:\\BTP:  python outputs/yt_research/cs601_first6/discover.py
"""
import json
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))
load_dotenv(ROOT / ".env")
from profsagent.delivery.sources import YouTube, web_videos  # noqa: E402

OUT = Path(__file__).with_name("candidates.json")

# Queries per lecture: one plain "lecture" query, one "explained/tutorial" query, one named expert/event query.
# long=True asks YouTube for videos over 20 minutes (lecture-length).
QUERIES = {
    "L1": [("AI-assisted software development workflow lecture", True),
           ("Software is changing again Karpathy", False),
           ("agentic coding lecture missing semester", False),
           ("how to use AI coding assistants effectively professional developers", False),
           ("vibe coding vs AI assisted engineering talk", False)],
    "L2_L3": [("Model Context Protocol explained architecture", False),
              ("Model Context Protocol MCP full workshop", True),
              ("MCP host client server JSON-RPC transport explained", False),
              ("MCP tools resources prompts primitives explained", False),
              ("MCP security authorization OAuth talk", False)],
    "L4_L5": [("context engineering for coding agents talk", False),
              ("how coding agents work agent loop explained", False),
              ("Claude Code best practices talk Anthropic", False),
              ("advanced context engineering complex codebases", False),
              ("context engineering LLM agents lecture", True)],
    "L6": [("build an MCP server tutorial python", False),
           ("build MCP server FastMCP tutorial", False),
           ("MCP inspector test MCP server", False),
           ("building custom MCP server workshop", True)],
}


def main():
    yt = YouTube()
    assert yt.ok, "YOUTUBE_API_KEY missing"
    found = {}       # id -> {"queries": [...]}
    for lec, qs in QUERIES.items():
        for q, long in qs:
            ids = yt.search(q, n=15, long=long)
            web = web_videos(q, n=15)          # free DuckDuckGo video search: catches what YouTube's ranking buries
            print(f"{lec:6} yt={len(ids):2} ddg={len(web):2}  {q}")
            for src, lst in (("yt", ids), ("ddg", web)):
                for v in lst:
                    found.setdefault(v, {"lectures": set(), "queries": []})
                    found[v]["lectures"].add(lec)
                    found[v]["queries"].append(f"{src}: {q}")
    det = yt.videos(list(found))
    chans = yt.channels([d["channel_id"] for d in det.values()])
    out = []
    for vid, f in found.items():
        d = det.get(vid)
        if not d:
            continue
        out.append({**{k: d[k] for k in ("id", "url", "title", "channel", "published", "duration_s", "views", "likes",
                                         "captions", "language", "embeddable", "blocked_in_india")},
                    "subscribers": (chans.get(d["channel_id"]) or {}).get("subscribers"),
                    "description": d["description"][:1500],
                    "lectures": sorted(f["lectures"]), "queries": f["queries"]})
    out.sort(key=lambda x: -x["views"])
    OUT.write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{len(out)} candidates -> {OUT}; quota left today ~{yt.quota.left() if hasattr(yt.quota, 'left') else '?'}")


if __name__ == "__main__":
    main()
