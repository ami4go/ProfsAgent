# ProfsAgent: where the work is (read this first)

Short status note for teammates and their coding agents, so nobody has to re-read the whole repo or chat history.
Newest entry on top. Owner of Phase 2 deliverable C: Vihan.

## 2026-10-28: provider fallbacks, transcript-block handling, quality filters

### State of play
- Phase 1 (course design) is done. Phase 2 deliverable C (per-lecture briefs, the professor's survey, learning
  resources and guest speakers) is built; the last full run is `runs/cs601-02/delivery/` (27 lectures).
- In that run, **weeks 7–13 came out weak** because YouTube blocked transcript downloads from the home IP partway
  through. The code below fixes the cause. The full-run outputs are kept local, not in git: Amit's app tests use
  `runs/cs601-02` as their example and expect results for exactly 3 lectures (W01.L1, W01.L2, W02.L1).
- **Next step:** re-run everything once so the new filters apply (about an hour; searches and transcripts are mostly
  cached):
  `python scripts/run_delivery.py recommend --run-id cs601-02 --refresh`
  then refresh Neo4j: `python scripts/run_delivery.py graph --run-id cs601-02`.
- UI contract for Amit: `docs/04_phase2_UI_integration_guide.md` (unchanged by this update except the new
  `partial` field below).

### 1. LLM fallbacks beyond Gemini (`src/profsagent/llm/client.py`, `config/models.yaml`)
- New generic OpenAI-compatible provider support. Providers are declared under `providers:` in `config/models.yaml`
  (`base_url`, `keys_env`, `min_interval_s`, optional `max_tokens`, `headers`). A provider with no keys in `.env`
  is skipped silently.
- Configured: **NVIDIA NIM** (`NVIDIA_API_KEYS`, 3 free keys set), **Mistral** (`MISTRAL_API_KEYS`, not set),
  **OpenRouter** `:free` models (`OPENROUTER_API_KEYS`, not set).
- Fallback order (roles `generate` and `extract`): **Gemini → NVIDIA → Groq gpt-oss → the rest** (Gemini
  flash-lite, Groq Qwen, Mistral, OpenRouter, local Ollama).
- NVIDIA models in use (checked 2026-10-28, answer in 1–5 s): `nvidia/nemotron-3-ultra-550b-a55b`,
  `minimaxai/minimax-m3.1-flash`, `nvidia/nemotron-3.5-lightning-30b-a3b`. Free tier is ~40 requests/min, so
  `min_interval_s: 1.6`; `timeout_s: 75` because some NIM models hang instead of failing (deepseek-v4.1-flash,
  glm-5.3, gemma-4-31b, gpt-oss-20b did); a hanging model is benched on all keys at once. kimi-k2.6 is "not found
  for account"; NIM's gpt-oss-120b was retired 2026-09-03 (Groq's still works).
- Unfamiliar-provider errors no longer crash a run: the (provider, model, key) slot is benched for an hour and the
  next one is tried. A model that rejects JSON mode is retried without it.
- `python scripts/check_llm.py [--provider nvidia,groq]` sends one tiny call per configured model and prints
  ok / the error. Use it after adding keys or when a model disappears (free rosters change often).
- Not used: Cerebras (now a card-only trial), GitHub Models (reported retired 2026-07-30).
- Embeddings stay on Gemini only: mixing two embedding models would make similarities meaningless.

### 2. Web search order (`src/profsagent/delivery/sources.py`)
- Readings / practice: **Tavily → DuckDuckGo → Gemini grounding** (`web_search()`, `duckduckgo()` via the `ddgs`
  package, no key). Measured on 7 reading queries: pages that open and cover the topic 75% / 65% / 40%; Gemini's
  answer text contains many invented deep links.
- Expert / practitioner search (`grounded_text`) keeps **Gemini first**, then Tavily, then DuckDuckGo.
- Bug fixed: a link written in `backticks` kept the backtick and 404'd; cached results are cleaned on read.
- New dependency: `pip install ddgs` (added to the README install line).

### 3. YouTube transcript block (fix 2)
- The block is per **IP**, not per API key: extra YouTube keys do not help (and extra projects to raise quota are
  against YouTube's API policy). Data API use was 4,228 of 9,000 units, never the bottleneck.
- `sources.transcript()`: requests are spaced `transcripts.min_interval_s` (1.5 s) plus up to `jitter_s` (1 s);
  after the first `IpBlocked` / `RequestBlocked` no more transcript requests are sent in that process
  (`transcripts_blocked()` gives the time).
- A lecture built without some transcripts is saved with `"partial": {reason, videos_without_transcript}`; a
  continuation lecture of a partial one is partial too. The report shows a ⚠ Partial banner. **A plain `recommend`
  run (no `--refresh`) redoes only partial lectures.** UI: show the banner when `lecture.partial` exists.

### 4. Quality filters (fix 3)
- D2 review prompt v0.2.0 adds `generic` (general intro to a broader concept, e.g. IBM "What is an API") and
  `hands_on` (practice only: something students do). Both are new optional fields of `ResourceReview`.
- `checks.resource()` new rules: `R-GENERIC` (error), `R-SOURCE` social-media post as reading/practice (error;
  list in `config/resources.yaml: social_domains`), `R-PRACTICE` paper offered as practice or review says not
  hands-on (error), unreviewed practice without repo / notebook / exercise signals (warning).

### Tests
- `tests/test_delivery.py`: 16 pass (new: filters, transcript breaker). Full suite: 185 pass with Neo4j running
  (12 Neo4j tests skip when it is not; start it with `D:/neo4j/neo4j-community-5.26.25/bin/neo4j.bat console`).

### Secrets
- All keys live in `.env` (git-ignored): GEMINI_API_KEYS, GROQ_API_KEYS, NVIDIA_API_KEYS, TAVILY_API_KEY,
  YOUTUBE_API_KEY, OPENALEX_API_KEY. Never commit or print them.
