# ProfsAgent: where the work is (read this first)

Short status note for teammates and their coding agents, so nobody has to re-read the whole repo or chat history.
Newest entry on top. Owners: Phase 2 deliverable A (UI, simulations) Amit, B (lecture content) Parth, C (resources,
experts) Vihan.

## 2026-11-05, later (Parth): fixes in C's and A's code after a review (please check)

Reviewed C and A (offline: tests, data, built pages; no AI calls) and fixed what was clearly a bug. All 376 offline tests
pass (`tests/test_app*.py` need fastapi, not installed here).

**For Vihan (C):**
- `mix.save`: editing an approved mix sets it back to proposed and moves its pack and quiz to `materials_outdated`
  (new field in `LectureMix`), so nobody uses a quiz made for the old mix; approving again clears it.
- `mix.make_quiz`: no `KeyError` when a mix part's component left the lecture's plan (its question is dropped by your
  existing check).
- Recap and quiz at the class edges: B's `outline()` now merges them (`content/generate.class_edges`), so a class that
  ends topic A and starts topic B opens with one recap and closes with one quiz (same minutes). You may still want a
  session-aware reserve on C's side.
- `tests/test_delivery.py`: the transcript test skips when `youtube-transcript-api` is missing. New `requirements.txt`.
- **Still yours (data, needs AI calls):** commit CS-601's components / mix / NotebookLM / quiz; re-run once YouTube
  unblocks (the 29 Oct snapshot has 3 empty lectures — W05.L1, W10.L1, W12.L1 — 10 without readings and 16 without
  practice); update doc 04 with components, timeline, mix and D8.

**For Amit (A and the app):**
- `app/delivery._result`: reads C's `continues` (since 1 Nov) as well as `continuation_of`, so "Continues …" shows again.
- Simulation types (`simulations/types.yaml`): AI/ML examples added to step-through, parameter explorer and networks.
  "Attention" topics no longer land on *experiments on yourself* (psychology). Accuracy on the 165 labels unchanged
  (75.2%), cross-validated 72.7% → 73.9%; `params.json` and `coverage.md` not regenerated.
- Trusted links: Transformer Explainer (Polo Club) and LLM Visualization (bbycroft.net) in `external/sources.yaml` and
  `index.json`. `external.text_for_matching`: hand-written entries also match topic by topic (downloaded PhET / Falstad
  lists keep the joined form, so Falstad's "Transformers" circuits don't match vision transformers). Transformers
  course: 0 → 4 of 22 lectures get a link; CS-601 and CSE201 unchanged.
- Stepper engine: a widget may name its legend colours (`legend: {done: 'inside'}`); default words unchanged.
- `auto.monte_carlo` 1.0.1: legend inside / outside / estimate (was "done / compared / swapped"), the question asked as a
  prediction, up to 2000 points. Checked in a browser.
- **Still yours:** `pip install playwright` to run `sims.py qa` (0/11 ran here: missing package, Chrome is present);
  render the DBSCAN and convolution MP4s; review the 3 `auto.*` drafts; an attention simulation would serve AI courses.

## 2026-11-05 (Parth): B follows C's delivery mix; narrated decks and videos; a Transformers sample course

**Slides for the delivery mix (`content/models.py`, `checks.py`, `generate.py`, `render.py`, B1 v0.5.0):**
- New slide kinds, used when `lecture.outline` exists: `recap` (first), `watch` + `debrief` (video and NotebookLM
  parts), `bridge` (the part's bridge points), `simulation`, `quiz` (last; C's D8 writes the questions).
- Each slide records its outline part in `component`. **Code, not the AI, fills** a watch slide's `clip` and a
  simulation slide's `link` from the outline (`fill_from_outline`), so no invented links. They show as a WATCH / OPEN
  panel on the slide and in the handout.
- New checks (`check_outline`): `D-OUTLINE` (a part with no slide, an unknown part, recap not first, quiz not last),
  `D-WATCH` (video part without a watch slide, or a watch slide without a clip), `D-SIM`. `deck.json` schema 2
  (version 1 decks still load).
- **For Amit:** `deck.json` slides may carry `kind` recap / watch / debrief / bridge / simulation / quiz, `component`,
  `clip` and `link`; `material.json` may carry `narration` (below).

**Review of Vihan's outline wiring (1 Nov):** correct; his 30 tests pass. Two points for Vihan:
- In a class that ends one topic and starts the next (e.g. W03.S1 = 60 min of A + 30 min of B), A's review quiz and
  B's recap land back to back in the middle of the class. Recap and quiz should open and close the *class*.
- CS-601's `components.json` and mix are not in the repo (scratch run), so B cannot use the outline on CS-601 yet:
  please commit them (or a snapshot) when ready.

**Narration (`content/narrate.py`, `run_content.py narrate [--video]`, no AI calls):**
- Each slide is read from its speaker notes (questions read with options, a pause, then the answer) with the Windows
  speech synthesizer. PowerPoint then builds `slides_narrated.pptx` (audio plays on entry, slides advance by
  themselves) and, with `--video`, `slides_narrated.mp4`. Windows + PowerPoint only; the voice is set in
  `config/content.yaml → narration`. Output is large and git-ignored.
- CS-601 W03.S1: 19 slides, 7.5 min of narration, made in about 1 minute.

**Transformers sample (`runs/ai-transformers-01/`):** a hand-written course design for "Introduction to Transformer
Architecture" (5 COs, 12 LOs, 13 weeks, 16 real references; modelled on Stanford CS224N, D2L ch. 11, The Annotated
Transformer, nanoGPT). It is not a Phase 1 run (`state.json → design_source` says so), and is used for B's week 1-2
sample decks.

## 2026-11-03 (Vihan): the delivery mix — each part of a lecture delivered one way, proposed by rules, decided by the professor

**What.** The proposal "Lecture delivery mix" (2 Nov) and Amit's reply (`docs/decisions.md` 30) are built on C's side;
the details, file shape and functions for the app are in `docs/decisions.md` 32.
- `delivery/mix.py` (new) + `config/delivery_mix.yaml` (new): for each part the rules pick slides, a YouTube stretch,
  YouTube + bridge slides, a NotebookLM video, in class, or a simulation (Amit's rule); then the lecture checks (first part
  live, at most 2 NotebookLM videos, at most 4 switches, video in class ≤ 40%, clips over 8 min before class); then **D7**
  (new prompt) writes one reason per part and may change a way only within what the evidence allows (a professor's
  note, a better fit, balance). The professor changes, locks, picks a preset and approves (`save`); each change is logged
  and, after 20, becomes a per-professor rule. Approval makes the NotebookLM pack for the NotebookLM parts only and the
  closing quiz (**D8**, new prompt; 4–8 questions, one per part, checked by code) with a recap from the previous lecture.
- `components.py`: D5 keeps 5–15 min free per lecture for the recap and quiz; `for_window` puts them first and last.
  Plans made before this give the minutes up from their longest slide parts (`L-RESERVE` note).
- `notebooklm.py`: with a mix, only its NotebookLM parts get a video prompt, and a part whose sources lack key terms
  says which source to add. `pipeline.recommend` proposes the mix for every lecture it saves; CLI `run_delivery.py mix`.
- `content/generate.outline` (for Parth): parts of an approved mix carry `way`, `when`, `bridge`, `simulation`; recap
  and quiz entries come first and last. D6 v0.2.0: a stretch using the words in another sense is off_topic.
- Tests: `tests/test_mix.py` (13, offline).

**On CS-601 (scratch run, 27 lectures, 142 parts):** slides 81, in class 43, NotebookLM 13 (was 122 prompts, at most 2 a
lecture now), YouTube + bridge 5, simulations 0 (nothing in the catalogue fits this course); minutes add up in every
lecture. YouTube stays rare because only 5 parts have a stretch that teaches them fully: the 16 lectures still partial
from the transcript block will add more when they are redone.

## 2026-11-01 (Vihan): deliverable C rebuilt around lecture components; guest-speaker fixes; Gemini 3.8/3.6 only

**Why.** The 28 Oct run matched one 45 s transcript window against the topic title: 18 of 33 clips started in a video's
first minute (the intro that announces the topic), 20 of 33 were 1.5 min long, a lecture got 0–6.6 min of clips, the
coverage score saturated (27 of 58 videos ≥ 0.85), and three continuation lectures came out empty. Guests: Google
Scholar was never searched, OpenAlex affiliations were often wrong, 15 of 49 academics shown had h-index 0–1, co-authors
of one paper filled several slots, and "pipeline evaluation" pulled in civil engineers who study oil pipelines.

**What C does now (per topic, over all its lectures):**
1. **Component plan (D5, `delivery/components.py`):** the topic's lecture time is split into components (title, what it
   `teaches`, key terms, kind, Bloom, LOs, minutes) in teaching order. A program checks the minutes (add up exactly per
   lecture, 5–30 min, multiples of 5) and repairs small misses; one retry with the problems listed; a plan from the
   LOs without AI as the last resort. Saved in `runs/<id>/delivery/components.json` and in each
   `lectures/<id>.json → components`. A later lecture on the same topic gets the topic's later components, so there are no
   empty continuations any more (`continuation()` is gone; `lectures/<id>.json` has `continues` instead of
   `continuation_of`).
2. **Video segments (`delivery/videos.py`, `delivery/segments.py`):** one YouTube search set per topic (the D1 queries,
   cached), no Shorts (< 3 min); transcripts for the videos closest to the components. Per component the transcript
   (30 s windows, smoothed over 3) is compared with the component's description, the stretch snaps to the creator's
   chapter when one contains it, and is 5–25 min. The AI check **D6** reads each stretch's transcript and says
   teaches_fully / teaches_partly / mentions / off_topic, with exact start and end markers (intros, plugs, outros cut).
   Per component the best checked segment is chosen (fully > partly, clarity, level, length close to the component's
   minutes, source; a video already used in the lecture is preferred). A component only partly taught gets a `gap`
   (what the video leaves out); components without any segment go to NotebookLM; activities and discussions are in class.
3. **NotebookLM pack (`delivery/notebooklm.py`, no AI):** `runs/<id>/delivery/notebooklm/<lecture>.md` — the sources
   to add (course context text written from the design, the chosen videos, readings, practice), a Video Overview prompt
   per component no video teaches fully (gap prompts say what to add), and quiz and flashcard prompts.
4. **Readings and practice** are matched against the lecture's components; a later lecture of the topic searches for
   its own first component and never repeats a link given to an earlier one. D2 now reviews readings/practice only.

**Lecture file additions** (`lectures/<id>.json → resources`): `components`, `timeline` (component → delivery
video / notebooklm / in_class, with segments and `gap`), `clips` (one entry per chosen segment, now with `component`,
`verdict`, `covered`, `missing`), `notebooklm` ({pack, components}). Video items carry `components` (which parts they
teach, where) and `scores.teaches`; `items/reserve` keep their old shape.

**For Parth (B uses C's plan; wired in, please review):**
- `content/sessions.py`: each session part also records `brief_from_min` and `brief_minutes` (where the part sits in its
  brief's own time).
- `content/generate.py`: `lecture_input(brief, note, run_id)` adds `outline` when C has a plan. That's the
  components of the lecture or class, from `delivery.components.for_window`, with `minutes` scaled to class time,
  `delivered_by` (video / notebooklm / in_class / slides) and the `clip` to show. There's no outline (and no change) when
  C has not run.
- `prompts/content/B1_lecture_deck.md` v0.4.0: one rule — follow the outline's order and minutes, give each
  component a slide, introduce the clip for video parts, use an activity slide for in-class parts.
- Tests in `tests/test_components.py`; `tests/test_content.py` passes unchanged.

**For Amit (app):** the lecture page has a **Lecture plan** tab (first when a plan exists; the old Clip playlist tab
only for lectures without one) and a **NotebookLM pack** page (`#/delivery/<id>/<lecture>/notebooklm`, copy buttons
per prompt); API: `_result` returns `components`, `timeline`, `notebooklm`; `view` lists `notebooklm`;
`GET /api/delivery/{rid}/notebooklm/{lid}`. Coverage labels for components read "part: …". The empty
`research_queries` crash is fixed in `experts.iiitd_faculty`, so the stopgap in `app/delivery_step.py` can go.

**Guest speakers (`delivery/experts.py`, `delivery/sources.py`, `config/experts.yaml`):**
- **Google Scholar through SerpApi** (`SERPAPI_API_KEY`, free plan 250 searches/month; its author-search API is
  discontinued, so people are found through a paper search and read with `google_scholar_author`): one Scholar search
  per lecture adds academics, and up to 8 profiles per lecture (outside academics; IIIT-D faculty are known) fix affiliation, h-index, citations, interests and
  country. Semantic Scholar (keyless, often rate-limited) is the fallback. All cached 90 days.
- Academics need h-index ≥ 5 (`record.min_h_index`); teaching / practical scores come from evidence only; one person
  per institution and per paper; IIIT-D faculty the AI check calls a strong fit are listed first; D4 v0.4.0 returns `same_field`
  (false → removed, e.g. oil pipelines); document-sharing sites (Scribd …) no longer confirm identity; people with no
  shared working hours with IST get "recorded talk" instead of a live slot.

**LLM (`config/models.yaml`, `llm/client.py`):** Gemini is **only gemini-3.8-flash and gemini-3.6-flash** (user's
rule: older and lite models are too weak); the first 2 keys of `GEMINI_API_KEYS` (new projects) take turns first, then
the rest (`limits.gemini_lead_keys`). Google-Search grounding has no free quota on 3.6/3.8, so `roles.search` is empty
and every caller falls back to Tavily → DuckDuckGo. judge_a/b are now 3.6/3.8 and judge_d an NVIDIA model
(`tests/test_judges.py` updated). The response cache no longer reuses answers from models that are not in the role's
list any more. Thanks for the `iter_raw` fix to `_post_deadline`.

**Fixes after the first full run (2 Nov):**
- Transcripts: at most 40 new requests an hour (`transcripts.max_per_hour`), 4–7 s apart, 10 per topic and 2 per
  component search. A block marks the lecture partial; a plain re-run (no `--refresh`) redoes only the partial ones.
- Segments: a stretch whose minutes are already used for another part of the same lecture loses 0.15, so two parts
  don't get the same minutes.
- Guests: the Scholar profile match also reads the paper that found the person, and accepts a long title prefix (Scholar
  shortens titles). "Assistant Professor at X" is split into role and institution. IIIT-D faculty go first only on a
  strong fit. Short lists are filled up to `top_n.min` from people who passed every check but share an institution or
  paper (listed after the varied picks). Semantic Scholar stops for the run after a rate limit.

**Results (CS-601, scratch run, not committed):** 27 lectures, 142 components (10–25 min), 57 checked video stretches
(13 start in the first minute, against 18 of 33 before; median 3 min). Only 5 components are taught fully by a video,
so most parts go to NotebookLM, which is too much work for a professor. 53 guests, no academic below h-index 5;
Parameswaran now shows UC Berkeley. YouTube blocked transcripts twice, so 16 lectures are still partial. A design for
choosing slides / clip / NotebookLM / in class per part, with a closing review quiz and the professor approving the mix,
is in the "Lecture delivery mix — design proposal" doc (Vihan will share it).

**Tests:** `tests/test_components.py` (new, offline, 17 tests). The continuation test in `tests/test_delivery.py` is removed.

## 2026-10-29 (Vihan): deliverable C full run, architecture PDF, AI reply deadline

- **Full run done** (28–29 Oct, all 27 lectures, transcripts worked, nothing partial): 58 videos, 31 readings,
  11 practice items, 33 clip entries, 72 guest speakers. Snapshot: `outputs/cs601-02_deliverableC_2026-10-29/`
  (start with its `report.md`). `runs/cs601-02` still holds only W01.L1, W01.L2 and W02.L1 results, because the app's
  tests use it as the example course.
- **How C works, with results and gaps:** `docs/08_phase2_C_resources_and_guests.pdf` (6 pages).
- **Known gaps:**
  - W05.L1, W10.L1 and W12.L1 (continuations) are empty.
  - No readings for W08.L2, W09.L1 or W11.L3: their topic names aren't web terms.
  - W08.L2 has no guests.
  - Prof. Jalote is in W01.L1's reserve, not its top 7.
- **`llm/client.py`:** every AI reply now has a hard deadline (`_post_deadline`). The provider's `timeout_s` (NVIDIA
  240 s) or `limits.timeout_s` (Gemini 180 s) now limits the whole reply, not only the gap between chunks: one review
  call in this run waited ~27 min. Failed attempts now log their duration (`"s"`) in `llm_calls.jsonl`.

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
