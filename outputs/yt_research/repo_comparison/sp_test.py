import asyncio, sys
sys.path.insert(0, sys.argv[1])
from irotechlab_yt_search.client import InnerTubeClient
from irotechlab_yt_search.utils import parse_search_results
async def run(q, sp):
    c = InnerTubeClient()
    ctx = {"client": {"hl": "en", "gl": "IN", "clientName": "WEB", "clientVersion": c.client_config["clientVersion"]}}
    d = await c.request("search", {"context": ctx, "query": q, "params": sp})
    await c.close()
    out = []
    def walk(o):
        if isinstance(o, dict):
            if "videoRenderer" in o:
                v = o["videoRenderer"]; t = (v.get("lengthText") or {}).get("simpleText", "")
                s = 0
                for p in t.split(":"):
                    s = s * 60 + int(p) if p.isdigit() else s
                out.append(s)
            for x in o.values(): walk(x)
        elif isinstance(o, list):
            for x in o: walk(x)
    walk(d)
    return out
async def main():
    for q in ["Model Context Protocol architecture", "scaled dot product attention"]:
        for name, sp in [("video only", "EgIQAQ%3D%3D"), ("video+long", "EgQQARgC"), ("video+medium", "EgQQARgD")]:
            ds = await run(q, sp)
            print(q[:30], name, len(ds), "≥20min:", sum(1 for x in ds if x >= 1200), "4-20min:", sum(1 for x in ds if 240 <= x < 1200))
            await asyncio.sleep(1)
asyncio.run(main())
