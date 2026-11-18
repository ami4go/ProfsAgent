# Delivery mode 2: whole lectures from YouTube clips (`src/profsagent/ytlecture`)

A lecture is delivered by one of three modes, never a mix:
1. the professor;
2. a playlist of YouTube clips;
3. an AI-narrated slide video.

This engine does mode 2 on its own. It plans what the lecture must teach, finds who teaches it best, searches several
services, reads the videos, cuts exact clips, has a second model check them, and assembles a playlist that fills the
slot. Its design follows a manual study (`outputs/yt_research/cs601_first6/METHODS.md`); section numbers below (§) point
there.

## Architecture: orchestrator, sub-agents, tools

```
                                ┌──────────────────────── Orchestrator (code, checkpointed) ───────────────────────┐
 lecture briefs (Phase 1) ──►   │ per topic:  PLAN ─► SCOUT ─► SEARCH r1 ─► SEARCH r2 ─► FILTER                     │
                                │ per lecture: TRIAGE ─► EVIDENCE ─► READ (skim→zoom) ─► VERIFY ─► ASSEMBLE ─► GAPS ─┤─► REPORT
                                └──────┬────────┬───────────┬───────────────┬──────────────┬──────────┬────────────┘
                AI sub-agents          Y1       Y2          Y3            Y4, Y5           Y6         Y7
                (prompts/ytlecture)  planner  scout       triage       skim / zoom      verifier   gap resolver
                Tools (code)         —        web         YouTube API, Tavily, DDG, SerpApi, playlists, course pages
                                                          evidence: chapters → captions → browser panel → Gemini notes
```

- **The orchestrator is code, not an LLM.** The stages are fixed, and every stage writes a checkpoint
  (`runs/<run>/delivery/ytlecture/state/<topic>.json`). An interrupted run resumes at the next stage: daily quotas run
  out and YouTube blocks caption requests, so this happens often. Free-tier models are not reliable enough to decide the
  control flow, and the project's rule is to keep AI output schema-constrained and checked by code.
- **The sub-agents do the judgement.** Each has one prompt (`prompts/ytlecture/Y*.md`) and a pydantic output schema
  (`models.py`). Code checks every answer before it is used (`agents.py`).
- **The tools do the fetching.** Each is cached on disk, kept within its free quota, and recorded in the trace
  (`tools.py`, `evidence.py`).
- **Assembly is code** (`assemble.py`): the same inputs always give the same playlist, with a score for each choice.

LLM routing comes from `config/models.yaml`. Gemini 3.8/3.6 flash goes first; on quota or errors the call falls to
NVIDIA NIM, Groq, Mistral and OpenRouter, in each role's order. The verifier always excludes the model that cut the
clip (`exclude_models`).

## Stages

| # | Stage | Who | What it does | From the study |
|---|---|---|---|---|
| 1 | PLAN | Y1 planner | Splits each lecture of the topic into 3–8 parts: minutes (sum ≈ 85% of the slot), `must_cover` checkpoints, search phrases, kind; flags fast-moving topics. All lectures of one topic are planned together, so later ones continue. Code checks part counts, minutes and duplicates; it asks again once, then rescales minutes itself | §1 parts before search |
| 2 | SCOUT | web tools + Y2 | Runs web searches for courses, creators and talks (Tavily → DuckDuckGo → Google via SerpApi). Y2 names authorities, picks course pages and writes 2 queries per part. Code corrects the evidence label (in the results or not) and keeps only course-page URLs that were really given | §2 "who teaches this" |
| 3 | SEARCH r1 | tools | Since 18 Nov the **free InnerTube search** (`innertube.py`, the endpoint youtube.com's search box calls; yt-dlp as its fallback): up to 8 authority queries, the topic's lecture playlists, and per part up to 3 queries (scout queries + search phrases; a long part's first query asks for videos over 20 min). Tavily (youtube.com only) per part and YouTube links on course pages as before. Only when the free search fails: the YouTube API (`videoDuration=long` for long parts), DuckDuckGo videos and SerpApi YouTube, as before | §2 |
| 3b | SEARCH r2 | tools | Channel expansion: up to 8 channels that are authorities, tier 1–2, or recur among candidates, searched through their own search tab (free; only that channel's videos are kept, checked again against the API's channel id); the API's `channelId` search as the fallback | §2 two rounds |
| 4 | FILTER | code | Length, embeddable, public, region (India), audio language, title rules (Shorts, hype, other languages), duplicate titles, minimum year for fast-moving topics | §3 |
| 5 | SHORTLIST | code + Y3N + Y3G (`shortlist.py`) | Since 17 Nov. **Evidence:** the strongest ~60 candidates get their watch page read (one plain GET, cached 90 days): YouTube's key moments when the uploader wrote no chapters, the full description, the most-replayed peaks. **Rank (code, no quota):** each part against the title and against each chapter on its own (all-MiniLM), a local cross-encoder re-rank of each part's top 40, plus a quality prior (tier, university/educator channel, named authority, views per year, likes, channel reputation learned from the verifier's scores in all earlier runs). **Nominate (Y3N, 1 call):** from ~150 strong-source titles the AI names up to 8 it knows are excellent (plain-titled lectures and talks that wording cannot find). **Grade (Y3G, 2 calls per part):** ~12–19 cards per part graded 0–3, twice with the cards reversed, averaged. **Select (code):** budgeted coverage: every part's best grades with falling weights, reading cost by video length, ≤ 3 per channel; 70% of the budget is read first. `shortlist.mode: list` restores the old one-call triage (Y3) | §3–4, §6 |
| 6 | EVIDENCE | tools | Chapters, then the caption API (paced), then the watch page's transcript panel in headless Chromium (works while the API is blocked, and adds YouTube's auto chapters), then Gemini notes | §4 fallbacks |
| 7 | READ | Y4 + Y5 | Videos over 20 min are skimmed first (one line per 45 s) and Y4 marks regions. Y5 reads the full words of those regions (±75 s) and cuts clips: start/end, quotes, points covered, treatment, standalone, level, rating 1–5, concerns. Code moves boundaries to the quotes, snaps them to caption lines and drops clips outside 2–25 min or that only "mention" | §5 skim-then-zoom |
| 8 | VERIFY | Y6 | A different model checks each clip against its own words: each must_cover point yes/partly/no with a quote, standalone, accurate, recommend. Code checks the quotes; coverage = yes + ½·partly, halved where a quote is not found | §6 |
| 9 | ASSEMBLE | code | Score = coverage, rating, source tier, standalone, recency, minus penalties for chapters-only or notes evidence. A gate removes inaccurate, weakly-covering (< 50%) or too-old clips; the verifier's "would not show it" vetoes only below 50% coverage, otherwise it costs 0.12 of the score. Per part in order, it chooses 1–2 clips fitting 0.5–1.6× the planned minutes, never overlapping earlier lectures, with a bonus for staying on the same video. It then trims to ≤ 95% of the slot | §6–7 |
| 10a | SECOND READ | code + Y5/Y6 | The rest of the reading budget, chosen by the same coverage rule from the grades, for parts still empty (need 1) or under 60% filled (need 0.6); without grades, each thin part's next-best candidates by rank | first W01.L2 test |
| 10b | GAPS | Y7 + tools | For empty parts, new searches or "accept the gap" with a reason. One bounded round: ≤ 4 new videos read per lecture | §9 rec. 10 |
| 11 | REPORT | code | `lectures/<id>.json`, `playlists.json/js`, `player.html`, `PLAYLISTS.md`, `TRACE.md` | §7 embeds, §9 rec. 9 |

A lecture ends in one of three statuses:

| Status | Condition | Recommendation |
|---|---|---|
| `ready` | no gaps and ≥ 65% of the slot | mode 2 |
| `usable_with_gaps` | some parts empty, but ≥ 40% of the slot | mode 2, with the gap parts taught another way |
| `not_enough_video` | less than 40% of the slot | mode 1 or 3 for the whole lecture |

## Outputs

Everything goes to `runs/<run>/delivery/ytlecture/`:

| File | Contents |
|---|---|
| `lectures/<id>.json` | parts; chosen clips (times, embed URL, evidence kind, score and why, verifier result, points covered); 2 alternates per part; clips rejected with the reason; gaps; status and recommendation |
| `PLAYLISTS.md` | the professor's view |
| `player.html` + `playlists.js` | plays each lecture's clips back to back with the YouTube IFrame API, stopping at each clip's end. Serve the folder over http (`scripts/run_ytlecture.py --run-id <id> --serve`), because YouTube embeds do not play from `file://` |
| `TRACE.md` | the run's own methods log: every query per tool with result counts, each agent's decision and model, filter counts, what was dropped and why |
| `llm_calls.jsonl` | every AI call |

## Running

```bash
python scripts/run_ytlecture.py --run-id cs601-02 --first 6
python scripts/run_ytlecture.py --run-id cs601-02 --lectures W03.L2 --refresh
python scripts/run_ytlecture.py --run-id cs601-02 --serve
```

Budgets and thresholds are in `config/ytlecture.yaml`.

Measure the shortlist against the manual playlists (free and quick; `--grade` adds the AI grading, ~2 calls per part):

```bash
python scripts/bench_shortlist.py --run cs601-02 --verbose
python scripts/bench_shortlist.py --run cs601-02 --grade --verbose
```

**Cost of one 2-hour lecture:**
- YouTube: since 18 Nov no searches on the API (the free InnerTube search); details of the found videos and channels,
  1 unit per 50 (≈ 15–25 units). Before: about 8 searches (≈ 800 of the 10,000 daily units).
- Other search: about 6 Tavily, about 12 DuckDuckGo and 2 SerpApi searches.
- Transcripts: up to 10.
- AI calls: about 15–25 (the plan and scout calls are shared by the lectures of a topic).

## Known limits

- **Caption blocking:** the caption API is blocked after about 25 quick requests from one IP. The browser fallback
  needs Playwright's Chromium (`python -m playwright install chromium`), and the notes fallback spends Gemini quota.
- **Trust in the readers:** an AI reader can still misjudge a clip. That is why a different model verifies every clip,
  quotes are checked against the transcript, and clips placed from chapters or notes are flagged "preview".
- **No uploader authority signal:** the YouTube API gives no direct authority signal for the uploader. Authority comes
  from the tier lists in `config/ytlecture.yaml` and `config/resources.yaml`, and from the scout's authorities; extend
  the tier lists per field.

## Tuning log

| Run | Result | Change |
|---|---|---|
| W01.L2 #1 | 19 of 60 min; architecture part empty | triage picked 5 of 10 → code tops up from the embedding rank; zoom reader cut 2–5 min clips → prompt asks for the whole explanation, sized to the part; verifier vetoed every partial clip → veto only below 50% coverage |
| W01.L2 #2 | 28 of 60 min; architecture still empty | verifier marked an Anthropic clip "inaccurate" for caption errors ("MTP", "cloud") → prompts say caption errors are not mistakes; readers folded the architecture into neighbouring parts → "each part its own clip" plus focus parts; a second read of each empty part's best unread candidates before new searches |
| CS601 first 6, 15 Nov (Gemini + YouTube quotas used up) | 71/28/11/21/17/21 min | per-model roles with fast models first and short per-call timeouts; parallel reading (4 workers); chapter regions instead of a skim call (widened to ≥ the part's length, and only when chapters average ≥ 3 min); short good clips kept as "partly covered" instead of dropped; up to 3 clips per part; 2 clips judged by the points they cover together; neighbouring reader pieces stitched before the length check (min 60 s); a duplicated topic plan split across its lectures |
| CS601 W02.L1, W02.L2, W03.L2, 16 Nov (quotas fresh, planner v1.2) | 45/35/39 → 50/26/51 min | the assembler used 86–96% of the usable clip time: the limit was the clip pool, not the selection. So: reading budget scales with the slot (≈ 1 video per 10 min); a second read also for thin parts (< 60% filled); readers also cut EXTRA on-topic stretches (part −1, with a title), which the verifier checks against the outcomes and the assembler adds after the planned parts until about 85% of the slot |
| CS601 r7 → r8 → re-assembly, 16 Nov | 60/32/52 → 69/33/76 → 78/33/83 min (W02.L1, W03.L2 pass) | the reader saw only the first 12k characters of a long region, so long workshops gave 0–10 min → long regions read in up to 4 chunks. The assembler then used 76 of 137 usable minutes: parts stop near their planned length while empty parts leave minutes unused → TOP-UP: under the target, well-taught parts grow up to 2× their minutes, but a clip from another video must add ≥ 10% new points (no repeated intros). The verifier vetoed correct new facts ("SSE is deprecated") → caption and recency doubts are a −0.12 penalty, not a veto, and Y6 is told its knowledge may be older than the video. One verifier call waited 885 s for cooldowns → `max_wait_s_by_role` 120 s for ytl_* roles. Shortlist minimum 6 → 8 |
| Transformers W01.L1, W01.L2, W02.L1, 17 Nov (Gemini used up; YouTube ran out in W02.L1's search) | 41/52/66 of 90 min | the scout hung 3.5 h in one DuckDuckGo call → 60 s wall-clock guard (`search.tool_deadline_s`) and a stack dump to `stacks.txt` every 15 min. Clips cut by nemotron stayed unverified: with the reader excluded, only models with a 5,500-token limit were left → a failed batch is retried clip by clip, and Mistral and OpenRouter are added to the ytl_read and ytl_verify rosters. The no-repeat rule blocked StatQuest's RNN explanation after MIT's → ONE second explanation per part from another teacher (score ≥ 0.6), never more, also in the per-part choice (W02.L1 had three "Q, K, V" intros); the report marks it. Triage stopped at 7 of 8 when the per-part ranked lists ran out → last pass over the whole pre-rank. Re-assembly alone: 57/56/69 |
| Audit vs the manual pass, 17 Nov | the engine FOUND most of the manual's best sources but never read them | see "Audit, 17 Nov" below |

## Audit, 17 Nov (engine vs the manual pass on CS601, plus the Transformers run)

The engine shared about one video per lecture with the manual pass. For W01.L1, W01.L2 and W02.L2, most of the manual
sources (Missing Semester's "Agentic Coding", the Anthropic MCP workshop, TechWorld with Nana, Barry Zhang, David Soria
Parra) were candidates, but none reached triage. Fixed:

| # | Issue | Fix |
|---|---|---|
| 1 | Only the per-part embedding top lists reached triage; plain titles of the best sources ranked low on every part (Missing Semester 66th of 100 tier 1-2; "Claude Code best practices" 209th of 273 on the whole lecture) | stronger tier/authority bonuses; ≤ 2 videos per channel per part; a ROSTER of up to 100 tier 1, tier 2 and named-authority candidates (title + length) shown to Y3, which may mark 1-2 **anchors** (a lecture or talk teaching several parts) that are never refused for a full part. Manual sources shown to triage: 21 of 30 candidates (was 0-2 per lecture) |
| 2 | Candidates were per topic: a source found for one topic was invisible to the next | course-wide candidate pool (read-only; videos actually read are saved with the topic) |
| 3 | The same clip played in two lectures (4 cases, 2-8 min): `taken` covered one topic | clips of all earlier lectures in the timetable are taken; re-assembly runs lecture by lecture in timetable order |
| 4 | `tier()`'s word-boundary fix had literal backspace characters, so short names (MIT, IIT, CMU) never matched; longer names matched as substrings ("AI Engineering from Scratch" = tier 1 via "AI Engineer", "Lets Decode Together" via "ETH") | whole-word matching for all names; brand names (Claude, OpenAI, Java, GitHub ...) must be the whole channel title (`tiers.exact1/2`) |
| 5 | Stored tiers went stale when the lists changed | tiers recomputed whenever candidates are loaded and in evaluation |
| 6 | Clips started mid-sentence ("terms, this means ...") because snapping used caption lines | boundaries move to sentence starts/ends (punctuated captions, 51 of 61 videos) |
| 7 | A clip whose start and end quotes were both missing was kept | dropped (times may be invented) |
| 8 | The verifier saw only the first 14k characters of a long clip; mixed-reader batches excluded several models; clips it skipped were never retried | long clips verified alone with up to 2× the text; batches grouped by reader; skipped clips asked again once |
| 9 | Second read and gap round set their flag before the work, and kept clips out of the checkpoint: an interrupted run lost them | clips saved as read, unverified ones verified on resume, flags set after |
| 10 | Not-standalone clips were 18-24% of the chosen minutes (weight 0.10 only) | extra penalty 0.06, shown in the report |
| 11 | Channel expansion searched with the topic title ("Model context protocols and architecture") | the two most frequent words of the plan's search phrases ("MCP server") |
| 12 | DuckDuckGo videos returned nothing in 50 of 56 calls | skipped for 30 min after 4 empty answers in a row |
| 13 | Gap round had no recency filter for fast-moving topics | same year rule as round 1 |
| 14 | Parts that stay empty are mostly "pitfalls / recap / testing" parts; near-duplicate parts got ~1 min | planner v1.3: distinct ideas only; no such part over 5 min (folded into must_cover) |
| 15 | Evaluation counted unverified clips as coverage 0 | coverage over verified clips; unverified share is its own check (≤ 25%) |
| 16 | `--redo-lectures` left the old trace rows in TRACE.md | old rows of redone lectures dropped |
| 17 | Zoom silently stopped after 4 chunks | recorded in the trace |

Not fixed (known): embeddings cannot rank a plain-titled source well, so the roster depends on the triage model's
knowledge; 7 of 11 course pages are JavaScript sites with no links in their HTML; the manual's Karpathy talks were
never found (they came from knowing them, not from search).

## Shortlist redesign, 17 Nov

Benchmark: the 37 videos of the manual CS601 playlists (W01.L1–W03.L2), 30 of them among the engine's candidates.
Reputation from cs601-02 itself is left out (it would leak the answer).

| Step | Before | After |
|---|---|---|
| Shown to the AI with full metadata | 7 | 16 (cards) |
| Shown as a title only | 14 (roster, inside one ~130-video call) | 21 (nominee list, its own small call) |
| Reachable at all (card or nominee list) | 21 | 23 |
| Chosen for the first reading wave | 4 (old run) | 4 (graded benchmark, 17 Nov night: 82 calls, Gemini mostly 503) |

Bugs fixed on the way: uploader chapters behind a bullet ("- 0:00:00 Intro", 35 of 1,242 candidates) were not parsed;
descriptions were stored cut at 3,000 characters (148 at the cap); the 45-video pool really held 24–35; the roster
kept a channel's first 6 by wording, which dropped Anthropic's most-watched talk; the triage prompt (5–8K tokens) was
over Groq's limit, so after Gemini's quota it always fell to minimax. The watch-page fetch did not raise the count on
this benchmark (the hidden videos are plain-titled talks, not videos without chapters); it stays for the readers
(key moments as chapters, most-replayed peaks as a skim hint) and for videos with long descriptions.

The overlap with the manual picks did not rise: the nominator named 5 of the 21 gold videos in its list, and the
budget is spent on other strong, on-topic sources (Anthropic's MCP talk, Microsoft's official MCP course, KodeKloud,
IBM). The manual set is one good answer among several, so this proxy is weak; the end-to-end measure is the playlist
evaluation (coverage, tier 1-2 share, fill) of a real run.

**First real run (Transformers W01.L1, 17 Nov night): worse, then fixed.** The first wave spent its budget on three long
university lectures (Stanford 81 and 73 min, MIT 45 min), graded for 4–7 parts each, which gave 1–4 clips each; the
StatQuest videos graded 3 for parts 0 and 1 (the old run's best clips) were never read. Result 51/90 min with a gap
(old: 61/90, none). Fix: a video counts for at most 2 parts (≤ 20 min) or 3 (longer) in the choice, reading cost is
1 / 1.5 / 2 / 2.5 units up to 20 / 45 / 75 min / longer, and the budget factor went from 1.3 to 1.6 (the old run read
15 videos). On the stored grades the first wave becomes: SAJAL GHOSH RNN, StatQuest seq2seq, NPTEL IIT Delhi, MIT
6.S191, CodeToAGI, StatQuest RNN, Stanford NMT.

Providers that night: Gemini answered 503 to most calls, Groq's one key allows ~2 grading calls a minute, there is no
Mistral key, so most grading went to nemotron/minimax at 1–5 min a call (a lecture's grading took ~9 min).

**Transformers rerun, 18 Nov (same plans; r4 + r5 after a laptop-sleep hang): worse end to end.**

| Lecture | Before (16 Nov) | After | Read (before → after) | Clip minutes cut |
|---|---|---|---|---|
| W01.L1 | 61/90, no gaps, cov 0.79 | 56/90, no gaps, cov 0.67 | 15 → 10 | 122 → 77 |
| W01.L2 | 53/90, no gaps, cov 0.79 | 32/90, 1 gap, cov 0.74, tier 1-2 85% | 14 → 11 | 104 → 58 |
| W02.L1 | 64/90, 1 gap, cov 0.80 | 40/90, 2 gaps, cov 0.86 | 14 → 14 | 107 → 101 |

Why (the shortlist chose well: 3Blue1Brown, NPTEL, StatQuest, Raschka, Stanford, MIT): (1) fewer videos read, the
reading budget in units is smaller than the old 9 + 6 videos; (2) the course pool lets an EARLIER lecture take a later
lecture's material: W01.L2 used Raschka's "Self-Attention and Scaled Dot-Product" and NPTEL Lec 15, so W02.L1 lost
~20 min it had cut (the timetable rule then gives them to W01.L2); (3) reader variance: minimax/nemotron read 3Blue1Brown
twice and returned no clip, and cut most clips at 1-4 min. Also fixed: a read that failed (network after sleep, every
provider down) was marked read with no clips and never retried; it is now retried by the next run (`read_retries`).

## Free search, 18 Nov (from the repo/library study, outputs/yt_research/repo_comparison)

- `innertube.py`: YouTube's own search (InnerTube) for videos, playlists and a channel's search tab, cached 14 days,
  paced 1–1.5 s, yt-dlp as the fallback after 3 failures in a row, the YouTube API after both. Filters are YouTube's
  `sp` codes (tested: over 20 min 20/20, 4–20 min 20/20). A channel search keeps only videos whose owner is that
  channel (YouTube Movies entries came back for one channel).
- Per part up to 3 queries instead of 1 API query for the biggest parts only; DuckDuckGo videos and SerpApi YouTube
  (both stand-ins for YouTube's own search) only when the free search fails.
- Channel subscribers (already fetched with the details) now count in the shortlist's quality prior (10k → 0, 1M →
  0.04).
- The `evidence` caption pacing in this file was never read; the pacing is `config/resources.yaml transcripts`
  (40 new requests an hour, unchanged).
- `--redo-search` keeps a topic's plan and scout and runs the search and the lectures again.

**Transformers rerun with the free search (r6, 18 Nov, `--redo-search`, same plans):** 0 API search units (124
free searches, 2 API searches as fallback), candidates per topic 134-144 → 291-349. Playlists: W01.L1 44/90 (r5 56,
16 Nov 61), W01.L2 36/90 (32, 53), W02.L1 45/90 (40, 64); coverage 0.85 / 0.70 / 0.88. More candidates did not
raise the minutes: W02.L1 cut 108 clip minutes (16 Nov: 107) but used 45, losing 22 to clips an earlier lecture
took (course pool) and 31 that passed every check but were not chosen. W01.L1's gap round read IBM's "What is Random
Forest?" and a Primavera P6 course: gap-round videos are now ranked by their match to the gap part (`gap_min_sim`).

**First claim and top-up, 18 Nov (not rerun; recomputed from the stored Transformers clips):**
- A topic borrows from the course pool only from EARLIER topics, and the videos a later topic's own search found (and
  this topic's did not) are left to it, also in `--reassemble` (`reserved_for_later`). On the stored clips: W02.L1
  45 → 54 min, W01.L2 36 → 31 (it gives back W02.L1's videos), W01.L1 unchanged.
- Top-up: while a lecture is under fill_min, a part may take one more clip of points it already covers if that clip
  teaches them differently (a demo after two explanations; `topup_repeats_short`). Three explanations of the same
  points stay refused (17 Nov rule). W02.L1's refused clips were all same-treatment explanations, so no change there.
