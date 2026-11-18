import time, yt_dlp
for vid in ["cixmqTsi2A4", "sTdz6PZoAnw"]:
    t = time.time()
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True}) as y:
        i = y.extract_info(f"https://www.youtube.com/watch?v={vid}", download=False)
    print(vid, round(time.time() - t, 1), "s | chapters", len(i.get("chapters") or []), "| heatmap", len(i.get("heatmap") or []),
          "| auto-captions en", "en" in (i.get("automatic_captions") or {}), "| subs", list((i.get("subtitles") or {}).keys())[:3],
          "| tags", (i.get("tags") or [])[:4], "| likes", i.get("like_count"), "| subscribers", i.get("channel_follower_count"))
# in-channel search
t = time.time()
with yt_dlp.YoutubeDL({"extract_flat": True, "quiet": True, "no_warnings": True}) as y:
    r = y.extract_info("https://www.youtube.com/channel/UCrDwWp7EBBv4NwvScIpBDOA/search?query=model%20context%20protocol", download=False)
print("channel search", round(time.time() - t, 1), "s", [e.get("title", "")[:45] for e in (r.get("entries") or [])[:4]])
