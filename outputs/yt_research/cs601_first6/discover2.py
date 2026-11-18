"""Step 1b: second discovery round, by named expert / official channel (the gaps round 1 left)."""
import json, sys
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[3]; sys.path.insert(0, str(ROOT / "src")); load_dotenv(ROOT / ".env")
from profsagent.delivery.sources import YouTube
Q = {"L2_L3": ["MCP 201 David Soria Parra", "Model Context Protocol origins David Soria Parra Justin Spahr-Summers",
               "MCP specification streamable HTTP transport explained", "MCP sampling roots elicitation explained"],
     "L4_L5": ["How we build effective agents Barry Zhang Anthropic", "Claude Code Boris Cherny agentic coding talk",
               "how do coding agents work under the hood tools", "context rot long context LLM chroma"],
     "L6": ["MCP servers VS Code agent mode", "Claude Code MCP server add configuration", "designing good tools for AI agents MCP best practices"],
     "L1": ["AI assisted programming lecture university 2025", "GitHub Copilot research productivity study talk"]}
yt = YouTube(); p = Path(__file__).with_name("candidates.json"); c = json.loads(p.read_text(encoding="utf-8")); have = {x["id"]: x for x in c}
new = {}
for lec, qs in Q.items():
    for q in qs:
        ids = yt.search(q, n=10); print(lec, len(ids), q)
        for v in ids:
            if v in have:
                have[v]["lectures"] = sorted(set(have[v]["lectures"]) | {lec}); have[v]["queries"].append("yt: " + q)
            else:
                new.setdefault(v, {"lectures": set(), "queries": []}); new[v]["lectures"].add(lec); new[v]["queries"].append("yt: " + q)
det = yt.videos(list(new))
for vid, f in new.items():
    d = det.get(vid)
    if d:
        c.append({**{k: d[k] for k in ("id","url","title","channel","published","duration_s","views","likes","captions","language","embeddable","blocked_in_india")},
                  "subscribers": None, "description": d["description"][:1500], "lectures": sorted(f["lectures"]), "queries": f["queries"]})
        if d["duration_s"] >= 480:
            print(f"  NEW {vid} {d['duration_s']//60}m {d['views']} {d['channel'][:22]} | {d['title'][:80]}")
c.sort(key=lambda x: -x["views"]); p.write_text(json.dumps(c, indent=1, ensure_ascii=False), encoding="utf-8"); print(len(c), "candidates")
