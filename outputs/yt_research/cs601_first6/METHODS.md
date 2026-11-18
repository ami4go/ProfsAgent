# How the YouTube lectures for CS601 weeks 1–3 were found

This is a working log. It records what was done, with which tool, and why, so the steps can be rebuilt inside ProfsAgent's video engine (`src/profsagent/delivery/videos.py`).

Delivery mode 2 replaces the professor for a whole lecture: the lecture is a **playlist of clips** taken from one or more YouTube videos, with start/end times. A clip is shown only if it teaches a part of the lecture well on its own.

## 0. Inputs read from the run (no AI)

| What | Where | Used for |
|---|---|---|
| Lecture ids, topics, hours | `runs/cs601-02/state.json` → `schedule.weeks`, `modules[].topics` | which 6 lectures, how long each is |
| Learning outcome + Bloom level per lecture | `runs/cs601-02/delivery/briefs.md` | what the clips must make a student able to do |
| Prerequisites (CSE201) | same | pitch: students know Git, JUnit and OOP, but not LLMs |

The first 6 lectures (the topic is split across lectures where the schedule splits it):

| Lecture | Topic | Hours | LO (Bloom) |
|---|---|---|---|
| W01.L1 | Developer workflows and AI-assisted coding | 2.0 | CO1.LO3: identify core components of AI-assisted workflows (BL1) |
| W01.L2 | MCP and architecture (part 1) | 1.0 | CO1.LO1: identify the MCP configuration schema and protocol requirements (BL1) |
| W02.L1 | MCP and architecture (part 2) | 2.0 | CO1.LO1 (continued) |
| W02.L2 | Coding agents and context engineering (part 1) | 1.0 | CO1.LO2: configure tool integrations in agent workspaces (BL3) |
| W03.L1 | Coding agents and context engineering (part 2) | 1.0 | CO1.LO2 (continued) |
| W03.L2 | Custom tool integrations using MCP | 2.0 | CO1.LO2 (hands-on) |

## 1. Break each lecture into parts *before* searching

A lecture title alone ("Model context protocols and architecture") is too coarse to search with: every video matches it, and none tells you what is missing. Each lecture was first broken into 4–7 **parts** (concepts in teaching order). Each part was given a target length that sums to the lecture's hours. The search is then **per part**, and a lecture is complete only when every part has a clip.

This is the single most useful step. The system's D1 queries already do this, but they should be stored as explicit parts with minutes, not only as queries.

## 2. Discovery: cast a wide net, with cheap tools first

| Tool | Cost | What it found | Notes |
|---|---|---|---|
| Web search (Claude's WebSearch) | free | which **university courses** teach this (Stanford CS146S, MIT Missing Semester 2026 "Agentic Coding", Cambridge, UMD), which **experts and events** own the topic (AI Engineer Summit, Anthropic's Code w/ Claude, Mahesh Murag's MCP workshop, Dex Horthy on context engineering) | Ask "who teaches this / which course has it" *before* asking YouTube for videos. Finding the course/expert first gives far better queries. CS146S has **no official recordings** (only AI-narrated third-party summaries), and those were excluded. |
| YouTube Data API `search.list` | 100 units each (10,000/day free) | 19 topic queries in round 1 (15 results each), 13 expert/official queries in round 2 | `videoDuration=long` for lecture-length queries; `regionCode=IN`, `relevanceLanguage=en`. Every result is cached 21 days by `sources.YouTube`. |
| DuckDuckGo video search (`ddgs`) | free | 15 results for the first query, then **0 for all others** | Rate-limited after one call. It is not dependable as a main source and needs back-off or spacing between calls. |
| YouTube `videos.list` + `channels.list` | 1 unit / 50 videos | duration, views, likes, channel, captions flag, region block, language | Metadata for all ~380 candidates cost about 10 units. |

**Two rounds of queries.** Round 1 used topic phrasing ("Model Context Protocol explained architecture"). Round 2 used **named people and official channels** ("MCP 201 David Soria Parra", "How we build effective agents Barry Zhang", "How Claude Code works"). Round 2 found the best MCP and agent material, all from the protocol's or tool's own authors (Anthropic, AI Engineer), which round 1 missed. Round 2's query list came from the web-search step and from knowing who the primary sources are.
→ **For the system:** after round 1, extract recurring speaker names, channels and events from the top results' titles and descriptions, then search those directly.

## 3. Filter on metadata (no transcripts yet)

Dropped:
- under 8 minutes for a whole part, or Shorts
- not English (several Hindi and Tamil MCP explainers appear high in results for `regionCode=IN`)
- clickbait or tool-hype titles ("Learn 97% of Claude in 16 minutes")
- product demos that teach one vendor's UI and no concept
- podcasts with no visual teaching, unless they contain a uniquely authoritative explanation

Note: the API's `captions` flag only means *uploaded* captions. Auto-captions usually exist even when it says false, so it is not used as a filter.

## 4. Shortlist, then read transcripts

39 videos were shortlisted, about 6–10 per lecture, mixing official/primary sources with the best-rated explainers. Transcripts were fetched with `youtube-transcript-api` through `sources.transcript()`:
- paced at 4–7 s per request, at most 40 per hour, cached 90 days
- YouTube blocks an IP that fetches transcripts too fast
- 12 of the 39 were already cached from earlier runs

Each transcript was merged into about 20-second lines `[m:ss] text` (`tx/<id>.txt`), so it can be read quickly and a clip boundary can be placed at a sentence.

**What happened:** 24 transcripts arrived. Then YouTube blocked the IP (`IpBlocked`/`RequestBlocked`) at the 25th request: 12 new requests in about 4 minutes, on top of earlier use today. The pacing was not enough.

**Fallbacks, in the order they were tried:**
1. **Uploader chapters in the description.** These are free, need no transcript, and are already in the metadata. 25 of the 39 shortlisted videos had them, including almost all the hands-on MCP tutorials. Chapter timestamps are exact, and the chapter titles say what each section teaches.
2. **The in-app browser's transcript panel.** On the YouTube watch page, the Show transcript button keeps working when the API is blocked. It also exposes **YouTube's auto-generated chapters** ("key moments") for videos whose uploader wrote none (e.g. *Claude Code best practices* had 18). It worked for `gv0WHhKelSE`. It failed on `-uW5-TaVXu4`, where the page's description panel never rendered, so that video was not used.
3. *Not used this time:* Gemini timestamped notes (`sources.video_notes`). This spends Gemini quota and gives a paraphrase, not a transcript.

→ **For the system:**
- Read chapters before asking for any transcript. When chapters exist, a part's clip can often be placed without a transcript at all.
- Lower `max_per_hour` to about 20.
- Treat a block as the signal to switch to chapters, not as the end of the run.

## 5. Reading transcripts efficiently

Reading every transcript in full is expensive (a 1-hour talk is about 15k tokens). The approach used was:
1. **Skim:** `skim.py <id> <every_s> <words>` prints one line per 40–120 s with the first 20–30 words. It shows where the topic changes, which is enough to place candidate clip boundaries.
2. **Read the window:** print only the lines between two times (the `show` awk helper in the session) to confirm that a clip starts at the beginning of a thought and ends at a natural stop.
3. **Read in full** only the anchor lecture (MIT Missing Semester "Agentic Coding"). It was reused in four lectures, so reading it once paid off.

Boundaries are at caption-line starts, so they are accurate to about ±10 s.
→ **For the system:** this is the same "skim, then zoom" pattern the LLM read step should follow. Send the model a 60-second skim to choose regions, then the full text of only those regions to set boundaries. This cuts tokens per video by roughly 5–10×.

## 6. How a clip was chosen for a part (the judgement, written down)

In order of weight:
1. **Teaches the part, not just mentions it.** Prefer a clip whose speaker *explains* (definitions, diagrams, worked example) over one that demos a product. Example: of 8 "MCP explained" videos, Nana's was chosen for the problem framing because it starts from a backend engineer's concrete integration problem.
2. **Primary sources for protocol facts.** For what MCP *is* and its primitives, use the co-creator (David Soria Parra, *MCP 201*) and the Anthropic workshop (Mahesh Murag), not third-party explainers that may be out of date. For OAuth, use an OAuth spec editor (Aaron Parecki).
3. **University lecture over talk over tutorial, when quality is equal.** MIT Missing Semester 2026 "Agentic Coding" pitches at exactly a 3rd-year CS level and was used in 4 of the 6 lectures.
4. **Self-contained.** The clip must not need the earlier minutes of its video. Live-coding workshops (e.g. Matt Pocock's 96-min workflow session) were rejected: no 10-minute window stood alone, and room logistics broke the flow.
5. **Recency where tools change fast.** For Claude Code and VS Code features, prefer 2025–26 videos and flag version-specific UI.
6. **Pitch.** Students know Git, JUnit and OOP (CSE201), not LLM internals. Videos that assume LangChain/LangGraph were cut before the framework part (Lance Martin's talk ends at 14:05 for that reason).
7. **Mix voices.** No lecture relies on a single video; 4–9 sources per lecture.
8. Popularity is only a tie-breaker. Views mostly measure hype: the most-viewed results were "Learn 97% of Claude in 16 minutes" and similar.

**Rejected, with reasons** (to train the filter):
- Hindi/Tamil MCP explainers. High views for region IN, but the course is in English. They could serve as optional extra material.
- Stanford CS146S "playlist": AI-narrated summaries of slides, not lectures.
- Podcasts (Lenny's, Pragmatic Engineer, Latent Space): no visuals, and the teaching is scattered.
- *Software engineering at the tipping point* (Google): good, but about org-level ecosystems, not this LO.
- Product-launch videos (*How the Claude Code team uses Claude Code*): mostly a product tour.

## 7. Assembling the lecture

- Parts are in teaching order. One video may supply several non-adjacent parts, e.g. Missing Semester gives the demo (part 3) and the use cases (part 6) of W01.L1, and the internals for W02.L2.
- Within one lecture, no second here repeats; across lectures a video may recur.
- Video time is 72–92% of the slot. The remainder is for a check-in quiz, discussion or (W03.L2) the lab. A 60-minute lecture of pure video is too long without a pause.
- Each clip has an **embed URL with `start` and `end`** (`https://www.youtube.com/embed/<id>?start=S&end=E`). It plays exactly the clip and stops, so the system needs no download or cutting to serve clips. A student-facing page can chain these embeds.
- `build_playlists.py` computes all lengths and totals from start/end, and asserts every end ≤ video length. Nothing is added up by hand.

## 8. Quota and effort used

- YouTube API: 32 searches × 100 + about 10 units of details ≈ **3,200 of 10,000 units**.
- Transcripts: 24 via API (12 from cache) + 1 via browser. Then IP-blocked.
- Web search: 4 queries.
- Most of the time went to reading: about 6 videos read closely, about 15 skimmed.

## 9. What to change in ProfsAgent's video engine (recommendations)

| # | Change | Why (from this run) |
|---|---|---|
| 1 | Store each lecture's **parts with target minutes** as first-class data, and search per part | The coarse topic query found the hype videos and missed the primary sources |
| 2 | Add a **"who teaches this" web step** before YouTube search: find university courses, protocol authors and conference talks, then search those names | Round 2 (named people and channels) found the best MCP and agent material |
| 3 | **Speaker/channel expansion:** pull recurring names from round-1 descriptions and search them | Same as above, automated |
| 4 | **Chapters first**, including YouTube's auto chapters via the watch page; transcript only when chapters cannot place the clip | 25/39 had chapters; the transcript API blocks after about 25 requests |
| 5 | **Skim-then-zoom** LLM reading (section 5) | About 5–10× fewer tokens per video |
| 6 | Source **tiers for facts**: protocol and spec authors > university > established educators > others | Explainers drift from the spec (e.g. older MCP videos predate Streamable HTTP and OAuth 2.1) |
| 7 | A **standalone-ness check** on each clip: does it need earlier context, and does it start and end on a thought? | Workshop and live-coding clips fail this |
| 8 | Serve clips as **`embed?start&end`** URLs | No download, exact clip, works in the frontend |
| 9 | A **`check` field** per clip (transcript / chapters / notes) shown to the professor | Clips placed from chapters only need a human preview |
| 10 | Per-lecture **coverage report**: video time vs slot, parts with no clip | W02.L2 is at 73%; a part with no clip should go to mode 1 or 3 instead |

## Files

| File | What |
|---|---|
| `discover.py`, `discover2.py` | the two discovery rounds (YouTube API + DuckDuckGo), using the project's cached client |
| `candidates.json` | all 382 videos found, with metadata and the queries that found each |
| `shortlist.txt` | the 39 videos whose transcripts were requested |
| `transcripts.py`, `tx/*.txt` | paced transcript fetch; 24 transcripts as `[m:ss] text` lines |
| `skim.py` | the one-line-per-minute skimmer |
| `build_playlists.py` | the curated spec → `playlists.json` (machine-readable) and `PLAYLISTS.md` (readable) |
