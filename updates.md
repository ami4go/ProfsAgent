# ProfsAgent: where the work is (read this first)

Short status note for teammates and their coding agents, so nobody has to re-read the whole repo or chat history.
Newest entry on top. Owners: Phase 2 deliverable A (UI, simulations) Amit, B (lecture content) Parth, C (resources,
experts) Vihan.

## 2026-10-28, afternoon (Parth): deliverable B slide generation v1; validation and evaluation layers

### Deliverable B: lecture slides and notes (`src/profsagent/content/`, README section "Deliverable B")
- **The call for `generate_material`** (UI guide §4, "Parth to define the call"):
  - `content.generate.generate_material(run_id, lecture_id, options) -> manifest`. Options: `include_pending` (cite C
    items not yet approved; testing only) and `note` (what the professor wants emphasised).
  - It reads `delivery/briefs` (built from the run's state) and C's `delivery/lectures/<id>.json` items whose
    `status_decision` is `approve`.
- **Output** in `runs/<id>/delivery/material/<lecture>/`:
  - `slides.pptx`, `notes.md`, `quiz.json`, `deck.json`.
  - `material.json`: what the UI reads. It has `files`, `slides`, `errors`, `warnings`, `findings`, `sources`, `cited`
    and `calls`.
- **Cost:** one B1 call per lecture (plus one repair call only if the deck has errors).
- **First live run:** cs601-02 W01.L1, 21 slides, 0 errors and 0 warnings after layout fixes, 1 call. A copy is in
  `eval/content_examples/cs601-02_W01.L1/`.
  - The copy in `runs/cs601-02/delivery/material/` is not committed: Amit's app tests expect that run unchanged.
- **Ideas taken from THU-MAIC/OpenMAIC:** structured quiz scenes, a versioned deck contract (`schema_version`), and
  layout checks on the rendered output.
  - Not taken: narration/TTS, agent classmates, interactive HTML scenes. For v2: outline first, then slides, with a
    professor gate between.
- **Checks beyond structure (`content/verify.py`, no AI calls):**
  - **Code snippets are compiled for syntax:** Python with ast, C/C++ with gcc/g++, Java with javac, JavaScript with
    node. A missing compiler gives a `D-UNVERIFIED` warning, never a pass. This laptop has no JDK, so the Java in the
    first deck is unverified; with a JDK, `query.blank()` is caught as "String has no method blank()".
  - **Weak citations (`D-GROUND`):** a slide whose cited source matches it worse than the average offered source.
    This is a topical match on the source title only.
- **Professor review (`content/review.py`):**
  - Decisions go in `material/review.yaml`: approve, redo (the reason becomes the AI's instructions), or reject.
  - `material.json` gets a `status` the UI can show: draft, approved, redo or rejected.
  - An approved deck is never overwritten without `--force`.
- **AI review for a professor in a hurry (`content/ai_review.py`, `--auto-review` / `options.review: "ai"`):**
  - A different model from the one that wrote the slides checks every slide and answers the quiz without the key.
  - Its errors get one repair. The status becomes `ai-reviewed`; only the professor can approve.
  - UI: show `ai-reviewed` as "checked by AI, not by you", with `material.json → ai_review.verdict` and the findings.
  - AI calls for slides are now logged in `delivery/material/llm_calls.jsonl`, not `delivery/llm_calls.jsonl`.
- **Slides are made per class, not per topic chunk (`content/sessions.py`, `config/content.yaml → classes`):**
  - C's briefs (`W03.L1`, …) are one per topic chunk of the schedule, so their lengths vary (0.25–2.5 h). IIIT-D
    teaches L = 3 as 2 classes a week, so B packs each week's chunks, in order, into **2 classes of 90 min**
    (`W03.S1`, `W03.S2`). A class can finish one topic and start the next; B1 gets the minutes per topic.
  - C's brief ids are unchanged (survey, resources and the UI still use them). `generate_material` accepts both kinds
    of id. **To discuss:** should the survey and C's resources move to class ids too?
  - CS-601 (`runs/cs601-02/delivery/material/`): weeks 1–2 were made per topic chunk (W01.L1, W01.L2, W02.L1, W02.L2);
    weeks 3–13 per class (W03.S1 … W13.S2, being generated). W03.L1 is superseded by W03.S1.
- **Smaller fixes:** JSON snippets are checked (a labelled request + response pair is fine); `check` keeps the AI
  review's findings; NVIDIA timeout 75 s → 240 s (a deck takes 2–3 min to write).
- **Java checks:** a JDK (Temurin 21) is now installed on Parth's laptop. Elsewhere, Java snippets stay "not verified"
  until a JDK is installed.
- **Not built yet:** `attach_material` (the professor's own pptx/pdf → summary / quiz / gap check).
- **New dependency:** `python-pptx`.

### Validation and evaluation (decisions log entry 17)
- `validate/engine.py` is the only entry point to validation. `engine.configure(run_cfg, llm, run_id)` replaces
  `pipeline._set_validation_profile`.
- `evaluate/engine.py` runs tiers 1–3 after every design. Tier 3 (judges) is only planned, with 0 calls, unless
  `run.judge: true` or `PROFSAGENT_JUDGE=1`. Writes `evaluation.json`.
- New warning family `fit`, settled by the professor:
  - `VC-AUDIENCE`: a "for All"-type title at level 3+.
  - `VC-NOLAB`: mostly hands-on LOs with P = 0 and no lab decision.
- `PROFSAGENT_STRONG_ONLY=1` (llm client) keeps a run off lite and local models. It still works with the new providers.

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
