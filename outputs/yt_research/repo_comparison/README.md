# YouTube search tools: comparative study (18 Nov 2026)

Tested against the ytlecture engine on the six CS601 lectures (W01.L1–W03.L2): 33 queries, one per lecture part (the
part's first search phrase), 20 results each, scored against the manual playlists (37 lecture–video picks, 27
distinct videos). Scripts and raw results are in this folder.

## Search: same 33 queries

| Source | Unique videos | Gold found (of 37) | Gold in a top 10 | New to the engine's pool | ≥ 20 min | Tier 1-2 | s/query | Notes |
|---|---|---|---|---|---|---|---|---|
| youtube-for-ai-agents (youtubei.js, MCP) | 488 | 14 | 11 | 351 | 22% | 19% | 0.8 | free; parser errors on current YouTube pages; duration filter silently ignored |
| irotechlab-yt-search (raw InnerTube) | 502 | 13 | 9 | 365 | 25% | 19% | 0.7 | free; type filter only, but raw params work (below) |
| YouTube Data API (yt-pipeline, engine) | 508 | 13 | 11 | 388 | 16% | 17% | 0.7 | 101 quota units a query |
| yt-dlp `ytsearch20:` | 497 | 11 | 11 | 354 | 26% | 15% | 2.1 | free; no upload date in flat mode; maintained weekly |
| scrapetube | 430 | 11 | 10 | 307 | 26% | 19% | 6.0 | free; 2 of 33 failed (JSON error) |
| youtube-search-python | 310 | 6 | 6 | 226 | 20% | 15% | 1.3 | broken: crashes with httpx 0.28; with httpx<0.28 still 16 of 33 failed |
| pytubefix | — | — | — | — | — | — | 18–27 | each title is a page fetch; can stop for an interactive prompt |

- The free sources return largely the same videos as the API (Jaccard 0.48 with the API, 0.69 between the two
  InnerTube tools).
- Plain per-part queries found 3 gold videos the engine never found (IBM "AI in the SDLC", AI Engineer "How Claude
  Code Works", Agentic AI Foundation "Intro to OAuth for MCP Servers"). Engine pool + these searches reach 23 of 27.
- Raw InnerTube filter params (tested): `EgQQARgC` = video + over 20 min → 20 of 20 long; `EgQQARgD` = 4–20 min →
  20 of 20. youtubei.js 17's duration option returned the same 9 of 20 long videos with or without it.

## Other features

| Feature | Result |
|---|---|
| In-channel search (youtubei.js `channel.search`, yt-dlp `/channel/<id>/search?query=`) | Free, ~1 s. AI Engineer → "Building Agents with MCP", "The Future of MCP"; Anthropic → "The Model Context Protocol (MCP)"; Missing Semester → "Lecture 7: Agentic Coding". "Stanford Online" returned movie trailers: results must be checked against the channel id |
| Playlist search (InnerTube) | Free; results come as `LockupView` (title in `metadata.title`, id in `content_id`) |
| Transcripts (youtube-transcript-plus, InnerTube `player` as ANDROID) | 53 of 55 in ~5 min (2 had no captions), no block. Same endpoint as our youtube-transcript-api 1.2.4: the difference is our cap of 20/hour |
| Video details (yt-dlp, 5–7 s a video) | chapters incl. key moments, heatmap (100 points), likes, **channel subscriber count**, tags, caption tracks |
| Search snippets (youtubei.js) | 26 of 660 results show caption text YouTube matched; no timestamps. Little value |
| Transcript chunk search as a clip locator (clip-finder's chunker, local MiniLM) | Top-3 chunks land on the verified clip 67% vs 51% for 3 random chunks; cross-encoder re-rank 61%. Not good enough to replace the skim call |
| yt-pipeline flow (topic search 50 → AI picks 20 by its rubric, our free models) | 8 of 37 gold in 20 picks (= all gold in the 50); 0 for W02.L1 and W02.L2 (one topic query misses parts) |
| youtube-skills (TranscriptOut) | Not tested live: needs an account (email + code), 100 free credits then paid |
