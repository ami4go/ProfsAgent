# Decisions and changes log

A running record of the decisions the team takes and the changes that follow from them, so anyone can see **what**
changed, **why**, **who agreed**, and **where** in the code. Newest first.

**How to add an entry:** date, a one-line title, then *Decision*, *Why*, *Changed* (files, commits) and *Agreed by*.
Mark anything still waiting for someone as **Open**.

---

## 2026-11-11: the professor app's frontend is rebuilt (dark, component-based)

### 38. A new frontend with a design system replaces the single `index.html`
- **Decision (Vihan, 11 Nov):** rework the complete UI from scratch as a premium dark application; the stack was left open.
- **Why:** the one-file UI (2,200 lines) had reached the limit of what could be changed safely, and `docs/10_ui_improvement_plan.md`
  already asked for a split, a status vocabulary and the course as the place you work in.
- **Changed:**
  - **`frontend/`** (new): React 19 + TypeScript + Vite + Tailwind 4, TanStack Query, Radix, Motion. Design tokens, a component kit
    and every screen of the old app (`docs/11_frontend.md` has the map and the design system).
  - **Information architecture** (plan §7): Courses | Simulations, with Ctrl K. A course has four tabs: Overview, Design, Lectures,
    Student view. Old `#/run/…` and `#/delivery/…` links redirect.
  - **`app/server.py`:** `GET /` serves the build (`static/ui`, committed, so the app still runs with Python alone); the `/fonts/`
    route and `static/index.html` are gone. One new read-only endpoint, `GET /api/runs/{id}/stage/{gate}`, so an approved step can
    be read again. No other API change.
  - **`scripts/run_app_demo.py`** (new): the real app with recorded runs replayed in place of the AI stages, to work on the UI and
    to demo without keys or Neo4j.
- **Checked:** `npm run build` (type-check) and `npm test` (28 tests); `tests/test_app*.py` (62 pass, 2 new); every screen driven in
  a browser against the demo server (create → four checks with edits, overrides and stop; lecture plan, resources, speakers, slides,
  simulations, student view); axe audit of nine screens: no violations; no horizontal overflow at 390, 820 and 1280 px.
- **Not checked here:** a live AI run and Neo4j (no keys on the build machine); simulation suggestions and the briefs of a newly
  approved course (they need the local embedding model, which could not be downloaded there).
- **Open:** Amit's review of the new look against the plan in `docs/10`; the course-sheet PDF export uses a Windows font path
  (`scripts/export_course_sheet_pdf.py`), so the PDF download fails on Linux and macOS (the app now says so instead of opening an error page).
- **Agreed by:** Vihan (asked for it). **Open:** Amit.

---

## 2026-11-04: Vihan's delivery mix in the app (the Lecture plan tab is its editor)

### 37. The professor sees, changes and approves how each part of a lecture is taught, in the app
- **Decision (Amit, 4 Nov, for the demo on 5 Nov):** build the mix editor and bring all of Vihan's 0c26ee9 into the UI.
- **Changed:**
  - **Backend.** Vihan's `delivery/mix.py` is used unchanged:
    - `app/delivery.py`: `mix_view()` (every lecture's plan, its quiz after approval, the course style) sits in the delivery view; `DeliveryManager.queue_mix()` runs mix jobs, resumed after a restart.
    - `app/delivery_step.py`: kind `mix`. `propose` (with the professor's note, D7) and `preset` (re-propose in a style) map to `mix.save(preset=…)`; `approve` maps to `mix.approve`, which writes the NotebookLM pack for the NotebookLM parts and the D8 quiz.
    - `server.py`: `POST /api/delivery/{rid}/mix/{lid}` with these actions:
      - `save` (way / lock / before or in class; `mix.save` refuses a way the evidence cannot support, e.g. YouTube without a checked stretch, and the app shows its reason);
      - `style`;
      - `propose` / `preset` / `approve` (queued).
  - **The Lecture plan tab:**
    - each part shows its time, how it is taught (only possible ways), "Before class" for video and NotebookLM parts, a Lock, D7's reason, the checked YouTube stretches, the bridge points, the terms NotebookLM's sources miss, and the simulation (Try it). The next-best way has a "Use this" button;
    - the five styles (Slides only / Slides + clips / Slides + NotebookLM / Flipped / Full mix);
    - the lecture checks in plain words;
    - the minutes per way, and the professor's preparation;
    - a note with "Plan again with my note", and "Approve the plan". After approval it links the NotebookLM prompts and shows the closing quiz and recap questions.
    - A lecture whose parts were made before the mix existed gets "Plan how to teach each part".
  - **Elsewhere on the screen:**
    - the class-time bar follows the plan: recap first, quiz last, and parts watched before class are hatched;
    - a "Teaching style" choice on the lecture list sets the course style (`course_style`).
- **Checked:**
  - `tests/test_app_mix.py`: the view, jobs and errors, and the professor's changes through the HTTP API;
  - a real search on 2 lectures of the CS-601 practice copy (`app-cs601-example-01`) made their parts and plans with Vihan's code.
- **Agreed by:** Amit (4 Nov).
- **For Vihan:** nothing changed in `delivery/`. If the mix file's shape changes, the editor reads `parts[].{way, when, allowed, alternative, segments, bridge, uncovered, simulation, locked}` and `totals`.

## 2026-11-03: the simulation page: a chalkboard stage, code on request, Present mode

### 36. Every stepper-engine simulation (all machine-built ones, and Page replacement) gets one calm page that fits the screen
- **Decision (Amit, 3 Nov):** of three designs (`Temporary/ui_plan/sim_design/`: A lecture hall, B chalkboard, C trace), go with A plus B as a Present mode. He also asked for:
  - a chalkboard look for the stage on the left;
  - no sideways scrolling: everything fits inside;
  - no coloured step strip, just the step;
  - the code shown only when clicked.
- **Why:** the old page drew a small figure in a large black box. It also:
  - showed the final answer from step 1, spoiling the predict questions;
  - greyed out "Next" with no reason while a question was open;
  - cut the code line off;
  - marked things by colour alone;
  - printed a technical "Checked:" line.
- **Changed** (`simulations/_engines/stepper/stepper.js`, `stepper.css`):
  - **Layout:** the light page of the app; the title, an Example list, "Change the input" (the input form is hidden until then) and "⛶ Present".
  - **The board:** a chalkboard holding the figure, drawn in chalk colours, with one sentence below it on what just happened, the predict question and, at the last step only, the result.
  - **Controls:** Back, Next (it says "Answer to go on" while a question is open) and Play, with a plain step slider and "Step n of N".
  - **Beside the board:**
    - "Values" (the recipe's `vars`, moved off the board; a value that just changed is marked with what it was);
    - "Code", hidden until "Show the code" or the C key.
  - **Legend:** shows the colours the step uses (now, compared, swapped, done, smallest).
  - **Present** (P, or the button): the board fills the screen with larger type and a floating control bar; Setup (S), Code (C) and Exit (Esc).
  - **Fit:**
    - on a computer the page is exactly one screen: bars, piles and plots scale to it, and two plots sit side by side;
    - on a phone it is one column and scrolls only downwards;
    - nothing ever scrolls sideways (checked at 1440×900, 1280×720 and 390 px).
  - **Inside the app:** the page hides its own title, because the app's window already shows it; the app's window no longer shows a version number.
  - **Other:**
    - fonts are bundled into `stepper.css` (OFL), so a page is still one offline file;
    - the independent check is shown only when it fails;
    - Page replacement's own grid is redrawn in chalk colours (presentation only, same version).
- **Checked:**
  - `qa_recipe.py` now also fails a page that scrolls on a computer;
  - all 3 machine-built pages and Page replacement pass their checks;
  - Chrome click-through: 66 checks, 0 problems; tests pass.
- **Agreed by:** Amit (3 Nov).

## 2026-11-03: machine-built simulations wait for the professor, and must show a figure

### 35. A simulation the machine built is approved or rejected by the professor before anyone sees it; every step must show a picture
- **Decision (Amit, 3 Nov):** after his Monte Carlo request, Amit asked for three things:
  - Approval: "it didn't ask me for approve it or reject it … it just automatically got loaded".
  - Figures: "a simulation … is something visual, not just the table entries".
  - Pages: show 1 2 3 with 10 on each page.
- **Changed:**
  - **Approval:**
    - A build now ends as "Built: your review" on the request. It is not in the Simulations list or the lecture suggestions until approved.
    - The request row has Try it, Approve and Reject.
    - Reject needs a reason. The build moves out of the catalogue (to `runs/_simulation_builds/rejected/`) and is built again with the reason as the professor's note.
    - Approving it on its lecture page approves it too.
    - Approval is written into the entry's `sim.yaml` (`approved_by`, `approved_at`). Its `status` stays `draft` until the team checks it.
    - Code: `app/simulations.py` `awaiting()`, `approve_build()`, `review_build()`, and `pending` in `catalogue_view`; `POST /api/simulations/requests/{id}/review`.
  - **Figures:**
    - The stepper engine has three drawn widgets: `plot` (points, lines and shapes on axes), `graph` (nodes and edges) and `grid` (a board of squares).
    - `qa_recipe.py` refuses a recipe if any step lacks a figure (`array`, `stacks`, `plot`, `graph` or `grid`). A table, variables or text may only sit beside one.
    - The README the AI reads, and the build prompt, say so and suggest the right figure per topic.
    - Our 8 hand-made simulations already draw figures; page replacement uses the textbook frames grid.
  - **Pages:** the list shows 10 a page, with page numbers (1 2 … N, ‹ ›); search links are paged the same way.
- **The Monte Carlo build (R004):**
  - Its arithmetic was right, but it showed only tables, and its "random" points came from a short repeating formula.
  - It was rejected with that reason; the old copy is in `runs/_simulation_builds/rejected/`.
  - The rebuild failed on 3 Nov: Gemini answered 503 (unavailable), and the NVIDIA fallback stops at 8,192 output tokens, too short for a whole recipe.
  - The request waits with "Try again".
- **Checked:**
  - tests: `test_autobuild.py` (the figure rule; build → reject → rebuild → approve) and `test_app_simulations.py`;
  - Chrome click-through: 65 checks, 0 problems.
- **One card per topic, up to 3 simulations (Amit, later on 3 Nov):** "for a single topic we can keep three simulations and let the user try any of them … keep the search results and newly generated ones altogether."
  - **What a topic card holds:** each finished request (approved build, or found pages approved) becomes one card named after its topic. In order, it holds:
    - the pages the professor approved;
    - the build;
    - the best pages its search found, by score.
  - **Limits:** at most 3 options; rejected pages never come back. When none of the 3 shows its code, a candidate that does takes the last place.
  - **Using it:** "Try it" lists the options, and each opens on its own (ours in the app, a site in a new tab). Requests with the same topic share a card.
  - **Code:** `app/simulations.py` `topic_groups()` (`topics` in `catalogue_view`), and `simGroupCard` in `index.html`.
  - **Backfill:** Tower of Hanoi (R001) and Selection Sort (R002) were built before the search step existed, so their searches were run now and kept on the requests:
    - Hanoi: ours, Virtual Labs, Math Playground;
    - Selection Sort: ours, Virtual Labs, W3Schools (with code);
    - Bubble Sort shows the two pages Amit approved (VisuAlgo, Virtual Labs).
  - **Tests:** `test_topic_groups_keep_the_build_and_the_pages_found_online`; Chrome click-through 66 checks, 0 problems.
- **Agreed by:** Amit (3 Nov).
- **Open for Vihan:** NVIDIA `max_tokens: 8192` in `config/models.yaml` truncates long generations, such as a simulation recipe of about 13k tokens. Could the `generate` role ask for more when the provider allows it?

## 2026-11-03: less text on screen; the research_queries stopgap removed

### 34. The app shows only what a professor needs; system details stay off the screen
- **Decision (Amit, 3 Nov):** remove text a professor does not need to know; if something is really needed, keep it very short.
- **Removed:**
  - "Course database connected" (shown only when the database or the AI keys are missing);
  - the how-it-works paragraphs on Your courses, Describe your course, Lecture delivery, the lecture list, the three checks, the Simulations page and the simulation requests;
  - process counts ("72 found · 27 passed the checks · 45 removed"), score bars, source-tier chips, "Why it was picked", "up to 3", "Standard YouTube licence";
  - "Approved links last checked …: all working" (a warning still appears when a link is dead);
  - the "Checked twice" chips on books (a warning still shows when a check fails), and the technical notes on programme-outcome strengths;
  - in simulations: "Built by the machine", "No check report yet", "Checked <date>", "External, not checked by us", the match percentages, and the "Covers:" lines (they still count for search);
  - rule codes (V23, VK-CONFLICT …) on screen. They remain as a tooltip, for the team.
- **Shortened:**
  - "Shows the code alongside" → "With code";
  - the problem banner → "N open problems. Fix with Edit, or continue with a reason.";
  - the choice descriptions, the request status lines and the class-example line;
  - the student-view banner → "What students see: only what you approved.".
- **The Simulations page (Amit, later on 3 Nov):**
  - A request leaves "Your requests" once it is done:
    - you approved something it found; or
    - its simulation is built. The simulation is then in the list, and a toast says so if the page is open.
  - Only requests still being worked on, or waiting for you, stay listed.
  - Because a request now closes at the first approval, a second simulation for that lecture is added on the lecture page.
  - Simulations of the same thing share one card, with one line per version (Ours / the site, "With code", Try it / Open). The grouping key is the title without "step by step", "· try it yourself", "(…)" and the like, and a title that starts with another's joins its group. Examples:
    - Falstad's "Low-Pass Filter (RC)", "(RL)" and the plain one;
    - two built "Binary search" pages;
    - in a search, ours with a link on the same subject.
  - "Your requests" folds open or closed, and the app remembers the choice. While folded it says "Needs you" when a request is waiting for you.
  - The list shows 10 simulations, then "Show more"; links found by a search come 10 at a time too.
- **Also:** `app/delivery_step.py` no longer patches `experts.iiitd_faculty`. Vihan's code has fallen back to the lecture topic since 0914269, and he agreed to the removal (entry 32 (d)); its test went with it.
- **Changed:** `src/profsagent/app/static/index.html`, `src/profsagent/app/delivery_step.py`, `tests/test_app_delivery.py`, `tests/test_sims.py` (pages approved from a web search carry site "web").
- **Checked:**
  - tests pass (`test_llm_check.py` left out: the known Python 3.10 failure);
  - Chrome click-through of simulations, lecture delivery and in-place editing: 0 problems.
- **Agreed by:** Amit (3 Nov).

## 2026-11-03: the app's new look (UI plan phases 0 and 2)

### 33. A calmer professor app: one design system, a class-time bar, and a shorter lecture page
- **Decision (Amit, 3 Nov):** start the UI work in `docs/10_ui_improvement_plan.md` with phase 0 (foundations) and phase 2 (the lecture page).
  - Style: calm minimalism, with bento layouts only on overview pages.
  - Signature element: the class-time bar.
  - The app stays plain JavaScript (no React), and the fonts ship with it.
  - Course-centred navigation (phase 1) comes later.
- **Why:** measured on 3 Nov, the lecture page was 4,417 px tall, with 1,367 words, 41 buttons and 20 form fields. The lecture list showed 77 chips, and the Simulations page had 16 primary buttons. Professors could not tell what to do next.
- **Changed** (`src/profsagent/app/static/index.html`, plus a `/fonts/` route in `server.py`):
  - **Design tokens.**
    - Colours: one palette (cool paper, IIIT-D navy, and ok / warn / error / info colours).
    - Six "way" colours for how class time is spent: slides, video, NotebookLM, in class, simulation, quiz. All pass WCAG AA with white labels.
    - Type scale and fonts, bundled under the SIL Open Font License in `static/fonts/` with their licences: Atkinson Hyperlegible Next (text), Bricolage Grotesque (titles), JetBrains Mono (codes).
    - Radii and motion, which respects reduced-motion settings.
    - The old colour names still work, mapped onto the new tokens.
  - **One primary button per screen.**
    - Finished course: "Next: plan the lectures"; the PDF and Excel buttons become secondary.
    - Home: only the oldest course waiting for you.
    - Lecture delivery: your own course, not the example copy.
    - Simulations: "Ask for a new simulation".
  - **After approval, open problems are amber ("Approved with items left open"), not red.**
  - **The class-time bar.**
    - Shows each part of the lecture in minutes, coloured by how it is taught.
    - Built from deliverable C's lecture plan (`components` and `timeline`).
    - Appears in the lecture list, and large at the top of the lecture page.
    - Hidden from the list until a course has at least one plan.
  - **Lecture list.**
    - Status filter with counts: All, Needs a decision, Ready to review, Decided.
    - One status per row, plus the simulation chip.
    - "★ New topic" only when it tells something; it is hidden when most topics are new.
    - A legend that names only the colours in use.
  - **Lecture page.**
    - Two columns: the work on the left; "About this lecture" (outcomes, assessment, more) in a side panel.
    - Once choices are saved they show as a short summary with Change, Apply to week and Apply to this module.
    - The progress card shows only while something is running, failed or not started.
  - **Plain words.** No team names in the choices ("Material team (B)", "(Parth)"); "Make the slides for me"; one name per action across screens.
  - **Fix.** In the Lecture plan tab, a part taught by a checked YouTube stretch said "Videos were not asked for" instead of listing the video.
  - **Accessibility (WCAG 2.1 AA, checked with `Temporary/ui_plan/a11y_check.py`):**
    - text and field-edge contrast;
    - header / navigation / main landmarks, with `aria-current` on the current section;
    - heading order;
    - star ratings announce their state;
    - text links at least 24 px high;
    - no sideways scrolling at 320 px (wide tables scroll inside themselves).
- **Measured** (same data as the baseline, 1,440 px wide):
  - Lecture page: 4,417 → 3,167 px, 1,367 → 1,013 words, form fields 20 → 1. Most of what remains is the results themselves.
  - Lecture list: 77 → 3 chips.
  - Primary buttons: Simulations 16 → 1, finished course 3 → 1, Lecture delivery 2 → 1.
- **Checked:**
  - tests: 414 passed, 1 skipped (`test_llm_check.py` left out: the known Python 3.10 failure);
  - Chrome click-through of simulations, lecture delivery and in-place editing: 0 problems;
  - the slides tab still opens.
- **Agreed by:** Amit (3 Nov).
- **For Vihan and Parth:** nothing changes in your code. The lecture page reads `components` and `timeline` exactly as deliverable C writes them; if their shape changes, please tell us.

## 2026-11-03: the delivery mix is built (`delivery/mix.py`); answers to Amit's (a)–(e) in entry 30

### 32. Each part of a lecture gets one way (slides, YouTube, YouTube + bridge slides, NotebookLM, in class, simulation), proposed by rules, explained by D7, decided by the professor; recap and quiz minutes are kept free
- **Decision (Vihan, 3 Nov):** build the proposal "Lecture delivery mix" with Amit's simulation rule (entry 30), phases 1–2 on C's side.
- **(a) The file** `runs/<id>/delivery/mix/<lecture>.json`, shape checked by `LectureMix` / `PartMix` in `delivery/models.py`:
  - lecture: `lecture_id`, `topic`, `minutes` (whole lecture), `status` `proposed | approved`, `preset` (`slides_only | slides_clips | slides_notebooklm | flipped | full_mix`), `preset_by` `ai | professor`, `course_style`, `parts`, `recap_minutes`, `quiz_minutes`, `totals` (minutes for `slides`, `video_in_class`, `video_pre_class`, `notebooklm`, `in_class`, `simulation`, `recap`, `quiz`, and `video_share`), `prep_minutes`, `checks` ([{code, message}]), `note`, `proposed_by` (`rules` | `rules + D7`), `proposed_at`, `approved_at`, `approved_by`, `materials` ({notebooklm, quiz, quiz_questions}).
  - part: `component`, `title`, `minutes`, `kind`, `bloom`, `way` (`slides | youtube | youtube_bridge | notebooklm | in_class | simulation`), `when` (`in_class | pre_class`), `rule` (R1, R1b, P, R2–R5, L for a lecture check, D7, D7-note, professor), `reason`, `alternative` ({way, reason}), `allowed` (ways the evidence supports), `locked`, `set_by` (`ai | professor`), `prep_minutes`, `segments` (video, video_id, url, start, end, minutes, verdict), `video_minutes`, `bridge` (points the slides add), `coverage` and `uncovered` (key terms in / missing from the NotebookLM sources), `simulation` ({id | url, title, source, score, class_example}; the best match, shown as evidence whatever the way).
  - Course style: `delivery/mix/course.json` ({style}); professor changes: `delivery/app_mix_changes.jsonl` (written by `mix.save`, so the app does not need to write it).
- **(b) Functions for the app** (`profsagent.delivery.mix`), all synchronous, run them in the background worker:
  - `propose(run, lecture, locked=None, note="", sims=None)`: `locked` = component ids to keep, or {id: way | {way, when}}; rows locked in the file stay too. About 10–15 s with D7 (the first call in a process loads the local models).
  - `save(run, lecture, changes={id: {way?, locked?, when?, reason?}}, preset=None, approve=False, by="Professor")` → {"mix"} or {"errors": {id: message}} (a way the evidence cannot support is refused, e.g. YouTube without a checked stretch). A new preset proposes again, keeping locked and professor rows. `approve=True` approves and makes the materials.
  - `approve(run, lecture, by)`, `materials(run, lecture)`: the NotebookLM pack for the approved NotebookLM parts only, and the quiz `delivery/quiz/<lecture>.json` + `.md` (D8; the recap is 3 questions from the previous lecture's quiz).
  - `load(run, lecture)`, `course_style(run, style=None)`, `reserve_for(minutes, first)`.
  - CLI: `python scripts/run_delivery.py mix --run-id <id> [--lectures …] [--note …] [--no-ai] [--approve] [--style slides|mix|flipped]`. `recommend` now proposes the mix for each lecture it saves (an approved mix with the same parts is kept).
- **(c) Simulations:** rule R1b after R1, as Amit proposed (mechanism or demo, or a part whose text names an algorithm or process; Bloom 2–4; catalogue ≥ 0.60 or link ≥ 0.65). Pass your `match_parts` result as `sims={component id: [{id | url, title, source, score, class_example?}]}`; without it, `mix.match_simulations()` matches each part with the same local model and thresholds (no `app/` import). On CS-601 no part matches (none of the 10 entries or 377 links is about AI-assisted development); on test parts it finds Dijkstra (0.93), round robin (0.94) and Ohm's law (0.95).
- **(d)** Agreed: remove the `research_queries` stopgap. **(e)** Agreed: without `SERPAPI_API_KEY` guests fall back to OpenAlex and Semantic Scholar (Scholar needs that key in your `.env`; SerpApi's free plan is 250 searches a month).
- **Also changed (C):** D5 keeps the recap and quiz minutes free (`reserve` in `config/delivery_mix.yaml`: quiz 10 min from 90-min lectures, 5 from 45; recap 5 from 45 min, not in the course's first lecture). `components.for_window` puts the recap and quiz first and last, and `content/generate.outline` adds `way`, `when`, `bridge` and `simulation` from an approved mix (Parth: the slide types are yours; `delivered_by` keeps its old values). D6 v0.2.0 marks a stretch that uses the words in another sense as off_topic.
- **On the CS-601 scratch run (27 lectures, 142 parts):** slides 81, in class 43, NotebookLM 13 (was 122 prompts), YouTube + bridge 5; minutes add up in all 27; D7 changed 7 parts, none refused.
- **Still open:** the four team questions in entry 30 (videos in or before class; where the quiz runs; NotebookLM effort; Parth's B1 input). The defaults until decided: 40% cap moves video before class; quiz as JSON + Markdown; at most 2 NotebookLM videos per lecture.
- **Agreed by:** Vihan. **Open** for Amit (the app side, phase 2) and Parth (B1 slide types for watch, debrief, bridge, simulation, recap and quiz).

## 2026-11-03: up to 2 simulations per lecture; always show one with its code

### 31. A professor may approve up to 2 simulations for a lecture (and from one request); the shown results always include one that shows the algorithm's code beside it, when one matches
- **Decision (Amit, 3 Nov):** "let the professor approve more than 1 link, 2 will be good enough, and always show the top results and one with the sideways code: the simulation along with the code develops a solid understanding."
- **Changed:**
  - **The code flag.** `sim.yaml` gains `shows_code`:
    - true for the 8 step-by-step entries, both machine-built drafts included (the stepper engine always shows the code with the current line lit);
    - false for DBSCAN and convolution.
    - Sites in `simulations/external/sources.yaml` can set it too: VisuAlgo and Python Tutor do (27 saved links).
    - Pages found on the web are checked when the search opens them: a code or pseudocode panel of 3 or more code-like lines, inside frames too (W3Schools' DSA pages pass).
  - **One with code among the shown results:** `app/simulations.with_code()`. When none of the top results shows its code, the best one that does takes the last shown place.
    - It applies to the lecture suggestions (ours and links) and to a request's finds.
    - On the lecture card, when the top suggestion has no code, the best one with code is shown beside it.
    - The label is "Shows the code alongside".
  - **At most 2 approved:**
    - `decide()` refuses a third approval on a lecture ("Undo one first"), and the card shows "n of 2 approved" with no Approve buttons once full.
    - In a request's review, a second find can be approved ("Also approve") while it is chosen; `chosen` is now a list, and undoing the last one returns the request to review.
    - A request made from a lecture puts both on the lecture.
  - **The search, tightened from real runs:**
    - results that end on the same page (two Virtual Labs pages leading to one demo) are shown once;
    - our own simulations must also name the topic's key words, so Selection Sort is no longer offered for "Merge Sort".
- **Measured (real searches, 3 Nov):**
  - Merge Sort: Virtual Labs demo, VisuAlgo (code), W3Schools (code).
  - Selection Sort: ours (code), Virtual Labs demo, VisuAlgo (code), W3Schools (code).
- **Checked:**
  - tests: `test_websearch.py` (the limit of 2 per lecture and per request, undo, `with_code`, site flags);
  - full suite: 424 passed, 1 skipped; 1 failure, the known Python 3.10 problem in `test_llm_check.py`;
  - Chrome click-through: 0 problems, including "Also approve", no third Approve, and the code label.
- **Agreed by:** Amit (3 Nov).
- **For Vihan:** the mix (entry 30) should allow up to 2 simulations per part, and prefer one that shows its code.

## 2026-11-03: reply to Vihan's "Lecture delivery mix" proposal (2 Nov)

### 30. The app can hold the mix in the Lecture plan tab; simulations should be a fifth way to deliver a part; what the app needs from `mix.py`
- **Context:**
  - Amit read Vihan's proposal "Lecture delivery mix — design proposal" (2 Nov): each lecture delivered part by part as slides, a YouTube stretch, a NotebookLM video or an in-class activity, closed by a review quiz. The AI proposes the mix, the professor changes it, and only then are slides, clips and prompts made.
  - On 3 Nov `main` had nothing new from Vihan or Parth after 0914269. Amit's simulation work is pushed as **1739acb**; it changes only the app's files and adds `simulations/` and `src/profsagent/sims/`. Entries 24–29 describe it.
- **Answer to "Amit: can the Lecture plan tab hold dropdowns per part and a minutes bar?": yes, no separate Mix step.** The tab already lists each part with its minutes and how it is delivered. We add:
  - a **minutes bar** at the top: the lecture's minutes split by way (live slides / video in class / video before class / NotebookLM / in class / simulation / recap / quiz), plus the professor's preparation time;
  - a **dropdown per part**, a **lock** per row and the **preset** for the lecture;
  - **Accept all** and **Approve the mix**;
  - a **note** box ("I'll teach MCP schemas myself") that asks again and keeps the locked rows.
  - **Course style** (mostly slides / a mix / flipped) is asked once, on the course's page in Lecture delivery, and sets the default preset.
- **Proposal: simulations as a fifth way.** The four ways leave out the app's simulations (A): our 10 checked or machine-built simulations, 377 saved trusted-site links (PhET, VisuAlgo, Falstad…) and the request flow (search the web, then build).
  - **Rule,** placed after rule 1 (in class): a part that is a process, mechanism or algorithm (Bloom 2–4), for which a simulation matches, is delivered as **Simulation**.
    - "Matches" means our catalogue at similarity ≥ 0.60 or a saved link at ≥ 0.65, judged on the part's title, what it teaches and its key terms.
    - In class, students operate it with a task from the slide, starting from the professor's class example. In a flipped class it goes on the pre-class list.
    - It counts as **active time, not video**, for the 40% cap.
  - **Evidence** shown in the mix: the simulation (ours, built by the machine, or a link with its site), its match, and the class example if one is saved.
  - **`PartMix.way`** gains `simulation`, with `simulation: {id | url, title, source, class_example}`.
  - **For Parth (B1):** a simulation slide: title, link or QR, what to try (2 focus questions) and a debrief line, like the watch and debrief slides for videos.
  - **Our side (A):** matching **per part** instead of per lecture: `app/simulations.match_parts(run, lecture, components)` → candidates per component, with the same local model and no AI calls. "Ask for a simulation" can also start from a part.
- **What the app will do, by Vihan's phases:**
  - **Phase 1, now** (nothing needed from Vihan): the read-only minutes bar and a "way" column worked out from today's `timeline` (video / NotebookLM / in class), plus simulation candidates per part.
  - **Phase 2, once `mix.py` exists:**
    - endpoints `GET /api/delivery/<run>/mix/<lecture>`, `PUT …/mix/<lecture>` (the professor's ways, locks, preset and approval) and `POST …/mix/<lecture>/again` (with the note);
    - "Generate the lecture material" waits for an approved mix when one exists;
    - the student view in lecture order (recap, parts, quiz) with a pre-class list;
    - every change the professor makes is logged (with the part's signals) in `delivery/app_mix_changes.jsonl`, for the per-professor rules.
- **Asked of Vihan:**
  - **(a)** The exact shape of `delivery/mix/<lecture>.json` (`LectureMix` / `PartMix`): field names, the `way` values (with `simulation`), `locked`, `set_by`, and `status: proposed | approved`. The app will read and write it.
  - **(b)** A function the app can call to **propose again with locked rows and a note** (`mix.propose(run, lecture, locked, note)`), run in the app's background worker like `recommend`.
  - **(c)** Adding the simulation rule to `mix.py`. The app gives the candidates per part: `app/simulations.match_parts`, or a small function in `sims/` if `delivery/` should not import `app/`.
  - **(d)** For information: the app still has its stopgap for the empty `research_queries` crash (`app/delivery_step.guard_empty_research_queries`). Vihan fixed the cause, so we remove it in the next app change.
  - **(e)** For information: `SERPAPI_API_KEY` (Google Scholar) is not in Amit's `.env`, so guest search on his laptop falls back to the other sources.
- **Still open (team; Amit has not decided yet):**
  - videos in class or before class (whether the 40% cap is a hard limit or becomes a pre-class list);
  - where the quiz runs: slides, a Google Form, or the app with scores saved (only the app keeps the scores for the semester feedback);
  - whether professors will spend 10–15 min per NotebookLM video, or it is capped at 1–2 per lecture;
  - Parth: can B1 take the mix as input (one deck that follows it)?
- **Agreed by:** Amit (the answer and the simulation proposal, 3 Nov). Waiting for Vihan on (a)–(c), and for Parth on the simulation slide.

## 2026-11-03: look for existing simulations before building one

### 29. A request first searches our catalogue, the saved links and the web, opens the top pages, and the professor reviews what it found; the machine builds only when nothing fits
- **Decision (Amit, 3 Nov):**
  - The auto-build made a Selection Sort simulation even though VisuAlgo already has one. Amit then found a Virtual Labs (IIIT Hyderabad) Tower of Hanoi simulation himself.
  - His rule: "make your searches more robust, at least visit the top 3–4 pages with the similar search, then only fall back to auto-creation". Existing pages go to the professor to approve or reject first.
- **How it works** (`src/profsagent/sims/websearch.py`), cheapest first:
  1. **Saved lists (free):** our catalogue and the saved links, matched with the local model.
  2. **Two web searches**, Tavily (cached 21 days; DuckDuckGo when Tavily has no key or credit):
     - trusted sites only: Virtual Labs (`vlabs.ac.in`, new), PhET, VisuAlgo, Falstad, Python Tutor, CircuitVerse, Seeing Theory, USF visualizations, GeoGebra, TensorFlow Playground, Polo Club (`simulations/external/sources.yaml`, `search:`);
     - then the open web.
     - Wikipedia, YouTube, PDFs, social sites and course sites are skipped.
  3. **Visits:** the top 3 pages of each search (plus the saved links) are opened in Chrome. A page is kept only if:
     - it loads;
     - it has controls or a drawing area (canvas, sliders, buttons; controls inside embedded frames count, video frames do not);
     - it matches the topic (local model);
     - its title, headings or address name the topic: 2 of 2 key words, 2 of 3, 3 of 4. This stops a merge-sort page being offered for Selection Sort.
     - An overview page follows its own "Simulation", "Demo" or "Practice" link within the same part of the site. Virtual Labs works this way: its Selection Sort overview leads to `selection_demo.html`.
     - Each kept page gets a screenshot.
- **Request flow** (statuses in `runs/_simulation_requests.json`):
  - queued → searching → **review** when something was found; nothing found → building.
  - In review, the professor sees up to 4 finds (ours first, then trusted sites, then the web), each with a screenshot, **Try it / Open ↗**, **Approve** and **Not this**, plus "None of these fit: build a new one" with an optional "what is missing".
  - **Approve:** the request is **chosen** and nothing is built.
    - The page joins the saved links (`simulations/external/found.json`), so it is suggested for other lectures too.
    - A request made from a lecture puts it on that lecture, approved.
  - **Rejecting all, or "None of these fit":** build_queued, and the builder's prompt lists what was rejected and the professor's note.
  - "Try again" after a failed build builds straight away (the search was already done).
- **Measured on 3 Nov** (real searches): about 1 minute and 2 Tavily searches per request.
  - **Tower of Hanoi:** Virtual Labs `dm1-iiith…/exp/recursion/simulation/`, Math Playground, towersofhanoi.info (plus ours).
  - **Selection Sort:** Virtual Labs' Selection Sort demo, VisuAlgo Sorting, W3Schools' DSA demo (plus ours).
  - **TCP congestion control:** nothing that is an interactive simulation, so it is built.
- **Also changed:**
  - `external.add_found()`;
  - endpoints `POST /api/simulations/requests/<id>/found/<n>` (approve / reject / undo) and `GET …/shot/<n>.jpg`, and `…/build` takes a note;
  - `PROFSAGENT_SIMS_SEARCH=local` (QA and demos: saved lists only, no web).
- **Checked:**
  - `tests/test_websearch.py` (4): the judging rules, a search with fixed results, the review flow including a lecture request and the builder's prompt, and the worker searching first;
  - full suite: 423 passed, 1 skipped; 1 failure, the known Python 3.10 problem in `test_llm_check.py`;
  - Chrome click-through: 0 problems, including approve (Chosen, nothing built) and reject all (then built).
- **Agreed by:** Amit (3 Nov).
- **Open:**
  - the local model can offer a near-miss from our catalogue (for "Binary search tree" it offered our "Binary search"); the professor rejects it;
  - Tavily's free tier is 1,000 searches a month (2 per request).

## 2026-11-03: the machine builds requested simulations itself

### 28. Auto-build: a simulation request becomes a recipe for our step-by-step engine, accepted only when automatic checks pass
- **Decision (Amit, 3 Nov):**
  - When a professor asks for a simulation, the machine first tries to build it itself. The team only gets what it cannot build.
  - The AI never writes a whole page. It writes a short **recipe** for an existing, tested engine; the engine draws it, and automatic checks decide.
  - This keeps the cost at 1–3 calls on the keys we already have.
- **How it works:**
  - **Engine:** the stepper engine gained ready-made views: `array` (marks, pointers, bars), `stacks` (pegs and disks), `callstack`, `vars`, `table` and `text`. A recipe's steps just list what is on screen.
  - **The recipe** has: the algorithm (`run`), an independent second method (`check`), textbook answers (`examples`) and a random-input maker (`random`). The format is in `simulations/_engines/stepper/README.md`, "Recipes", with a hand-written example in `example_recipe.js` (binary search).
  - **The checks** (`_engines/stepper/qa_recipe.py`, in Chrome with the network blocked):
    - `run` works on every preset, every example and 40 random inputs;
    - `check` agrees with `run` on all of them, does not call `run`, and rejects a deliberately corrupted result;
    - `run` matches every textbook answer;
    - widgets, code lines and questions are valid;
    - every example plays to its end;
    - no sideways scrolling on a phone; no network.
    - Before running, a scan refuses network, page, storage and timer use.
  - **The builder** (`src/profsagent/sims/autobuild.py`):
    - one AI call (`generate` role) writes the recipe;
    - if the checks find problems, they go back to the AI, at most 3 attempts in all;
    - the AI may decline when a step-by-step simulation cannot teach the topic;
    - a recipe that passes becomes `simulations/auto.<topic>/` (`status: draft`, `built_by: machine`, the request id and the build record), so it appears in the catalogue and in lecture suggestions;
    - otherwise the request becomes "Sent to the team", with the reason.
  - **The worker** runs in its own process, one request at a time, with a heartbeat file. The app starts it after a request, on "Build it now / Try again", and at start-up for requests left half-built.
- **In the app:**
  - a new request is built straight away;
  - "Your requests" shows: waiting / being built (attempt n of 3) / **Ready to try** (Try it) / sent to the team (reason, Try again) / paused (AI quota);
  - the page refreshes itself while something is building;
  - machine-built simulations carry a "Built by the machine" label;
  - a request made from a lecture page puts the new simulation on that lecture, waiting for the professor's decision.
- **First real builds (3 Nov), Amit's two requests:**
  - **Tower of Hanoi** (`auto.tower_of_hanoi`): 2 AI calls, 86 s. The first attempt was refused by the scan: a variable named `top`.
  - **Selection Sort** (`auto.selection_sort`): 1 call, 43 s.
  - Both used Gemini 3.6 Flash.
  - Their textbook answers were checked by hand: Hanoi 7/3/1 moves (2ⁿ−1); selection sort 10 comparisons and 3 swaps for `29 10 14 37 13`, 2 swaps for `5 4 3 2 1`.
- **Also changed:**
  - `catalogue.inline()` (a page from its text);
  - `PROFSAGENT_SIMS_DIR` (point the catalogue at a copy) and `PROFSAGENT_AUTOBUILD_REPLY` (a stand-in AI that answers from a file), both for QA servers and demos;
  - `create_app(sims_autobuild=…)`;
  - `.gitignore`: `runs/_simulation_builds/`, `runs/_simulation_autobuild.json`, `runs/_simulation_requests.json.lock`.
- **Checked:**
  - `tests/test_autobuild.py` (5): the example passes; a recipe whose check accepts anything, whose textbook answer is wrong, or that uses an unknown widget is refused; a check that calls `run` is refused; one retry then success; decline; the requests file and the worker.
  - Full suite: 419 passed, 1 skipped; 1 failure, the known Python 3.10 problem in `test_llm_check.py`.
  - Chrome click-through: 0 problems, including a request built in the app (stand-in AI), Try it, and the lecture page.
- **Agreed by:** Amit (3 Nov).
- **Open:**
  - machine-built simulations need a team review (`draft` → `team-checked`);
  - only the step-by-step kind can be machine-built today; each other kind needs its engine, recipe format and checker first;
  - a stronger model might pass harder topics.

## 2026-11-03: simulations on trusted sites, as links

### 27. Lectures also get links to simulations on trusted sites; the professor opens, approves or rejects them, and can ask for a new one
- **Decision (Amit, 3 Nov):**
  - We give the professor **only the link** to simulations on other sites. We never copy or embed them, so their licences are never a problem, and we do not check them.
  - The professor opens the link and approves or rejects it.
  - If nothing fits, he asks us for a simulation in a line or two. His rejection reason becomes the starting text of the request.
  - Later, the machine should try to build requested simulations itself (engine + recipe + check); the team only gets what it cannot build.
- **The sites:** PhET, Falstad (circuits and maths/physics applets), VisuAlgo, Python Tutor, CircuitVerse, TensorFlow Playground, CNN Explainer, Seeing Theory.
- **Changed:**
  - **Where the list of links comes from:**
    - `simulations/external/sources.yaml` lists the sites, plus hand-written entries for the six sites with short, stable lists;
    - `src/profsagent/sims/external.py` downloads PhET's metadata (82 university-level simulations) and Falstad's lists (59 applets, 200 circuit examples);
    - `python scripts/sims.py external` rebuilds `simulations/external/index.json` (377 links, committed, so nobody has to download anything).
  - **`app/simulations.py`:**
    - each lecture also gets up to 3 links whose title or topics are close to its topic (MiniLM, similarity ≥ 0.65, no AI calls);
    - the cut-off was chosen on IIIT-D's 9,784 weekly topics: below it, wrong matches appeared, such as "TCP/IP networks" → network flow;
    - links can be approved, rejected (reason required) or undone; an approved link stays on the lecture even when it is no longer suggested;
    - the stored suggestions are remade when the links index changes.
  - **`index.html`:**
    - on the lecture card, an **On other trusted sites** section: site name, "External, not checked by us", **Open ↗**, Approve, Reject;
    - after a rejection, the app points to **Ask for a new simulation**, whose text starts from the latest rejection reason; that button is highlighted when nothing is left to judge;
    - the student view shows approved links;
    - the Simulations page search also lists matching links.
- **Checked:**
  - tests: `tests/test_app_simulations.py` (6) and `tests/test_sims.py` (14, including the parsers on saved snippets). Full suite: 412 passed, 1 skipped; 1 failure in `test_llm_check.py`, the known Python 3.10 problem;
  - Chrome click-through (`Temporary/qa_sims_ui.py`): 0 problems, including an AVL-tree lecture → VisuAlgo BST, a Dijkstra lecture → ours + VisuAlgo (rejected, then a request prefilled from the reason), and "fourier" → Falstad and PhET.
- **Agreed by:** Amit (3 Nov).
- **Open:**
  - the "Check approved links" job (Vihan's health check) does not cover approved simulation links yet;
  - the optional Tavily search restricted to these sites, when nothing in the index matches;
  - rebuild the index now and then (`scripts/sims.py external`).

## 2026-11-03: simulations inside the app

### 26. Simulations in the professor app: a Simulation card on each lecture page, a Simulations page, class examples, and the student view
- **Decision:** Amit asked for the simulations to be part of the existing website, not separate tooling ("yes go ahead", 3 Nov).
  - We built the app part of stage A2 of doc 09.
  - Two changes from the doc's proposal:
    - the simulation is **its own card** on the lecture page, not a sixth delivery choice;
    - its data stays in the **app's own files**.
  - So Vihan's survey, review and pipeline code are **unchanged**.
- **What the professor sees:**
  - **Lecture page:** a **Simulation** card, above Results.
    - It lists catalogue entries whose title or topics match the lecture topic, as a "close" or "possible" match with the % similarity. The match uses the local MiniLM model, with no AI calls.
    - **Try it** opens a large preview window.
    - **Approve / Replace / Reject** work as for resources: a reason is required to reject, and everything can be undone.
    - **Add one from the catalogue** and **Ask for a new simulation** are always there.
    - When nothing matches, the card names the kind of simulation the topic suits (the A1 classifier), or says there is no clear fit.
  - **Class example:** in the preview, the professor sets the simulation up as for class and presses **Use this setup as the class example**. Students then open it at exactly that setup.
  - **Versions:** an approval belongs to a version. If the entry changes, the card says "Updated since you approved it" and offers to approve the new version.
  - **Student view:** approved simulations come first in each lecture.
  - **Lecture list:** "Simulation" and "Simulation suggested" chips.
  - **Simulations page** (top menu):
    - kept simple at Amit's request: a search box and the list (title, one line on what students do, what it covers, ✓ checked, **Try it**, and the lectures where it is approved);
    - **Ask for a new simulation** sits at the top;
    - the professor's requests are listed at the bottom;
    - there are no kind or course filters and no list of the 12 kinds, and the lecture card has no kind or level chips: Amit found them of no use to a professor.
- **Changed:**
  - **New `src/profsagent/app/simulations.py`:**
    - suggestions run in the background, about 30 s the first time per course, and are cached in `runs/<id>/delivery/simulations/suggestions.json`, which is remade when the lectures or the catalogue change;
    - decisions, class examples and history go in `decisions.json`;
    - requests go in `runs/_simulation_requests.json`, which is git-ignored because it holds professors' ideas.
  - **`server.py`:**
    - `GET /api/simulations`;
    - `GET /api/simulations/<id>/page`: the built page, rebuilt when its source changes, served with `Content-Security-Policy: sandbox allow-scripts …; connect-src 'none'`, so it gets its own origin and no network;
    - `POST /api/simulations/requests`;
    - `POST /api/delivery/<run>/simulations/<lecture>` and `…/class-example`;
    - `GET /api/delivery/<run>` starts the suggestions.
  - **`delivery.view()`:** has one new key, `simulations`. A failure there never breaks delivery.
  - **`static/index.html`:** the card, the preview window (outside the page's re-rendering, so polling never reloads a simulation), the Simulations page and the student rows.
  - **Catalogue:**
    - `sim.yaml` gains `summary` (required) and `class_example`;
    - new `simulations/_engines/share/share.js`: a page puts its setup in its link and tells the app;
    - the stepper engine uses it;
    - convolution 1.2.0, DBSCAN 1.2.0 and page replacement 1.1.0 report and restore their setup.
- **Checked:**
  - `tests/test_app_simulations.py` (5 tests). Full suite: 395 passed, 16 skipped; 1 failure in `test_llm_check.py`, the known Python 3.10 f-string problem.
  - `scripts/sims.py qa`: 8 of 8, including new checks that each framed page reports its setup and that a link restores it.
  - A Chrome click-through on copies of the courses (`Temporary/qa_sims_ui.py`): 30 checks, 0 problems; laptop and phone; offline.
  - On Amit's Web Development and the CS-601 example, no lecture matches the 8 simulations we have (best match 35%). Their cards say so, and offer the catalogue or a request.
- **Agreed by:** Amit (3 Nov).
- **Open:**
  - **Vihan (optional):** if delivery should know about simulations, a survey key `simulation` and a review kind `simulation` in his files; the app would then write there too.
  - **Parth:** a slide that links the approved simulation, with its class example.
  - **Later:**
    - stars and "did it help?" for simulations;
    - Neo4j nodes;
    - class examples for the five older pages;
    - A6, suggestions from the slides.

## 2026-11-03: simulation catalogue, stage A1 built

### 25. A `simulations/` catalogue with one command to check everything; the stepper engine; DBSCAN interactive; the topic → type classifier
- **Decision:** build stage A1 of doc 09 (Amit approved the plan on 2 Nov). He also proposed, for later (stage **A6**), AI suggestions of simulations from a lecture's slide material.
- **Changed (all new, ours):**
  - **The catalogue:**
    - `simulations/` holds `types.yaml` (the 12 types), `_lib/manim-web-0.40.1.js` with its MIT notices, `_engines/stepper/`, `classifier/labels.tsv` + `params.json`, the generated `coverage.md`, and 8 entries, each with `sim.yaml`, its page and `qa.py`;
    - `src/profsagent/sims/catalogue.py` loads and checks entries (types, levels, IIIT-D course codes, files, nothing loaded from the internet, change log) and builds one offline HTML file per entry, with libraries, engines and licence notices inlined;
    - `scripts/sims.py` provides `list | check | build | qa | coverage`;
    - `.gitignore` adds `simulations/_build/` (builds, screenshots, reports).
  - **Entries:** the 5 earlier simulations moved in unchanged (their QA scripts now take the page as an argument). Convolution now uses the shared library. Two are new:
    - **`ml.clustering.dbscan`** (CSE343/AI201, manim-web): add, drag or remove points; ε and minPts; four examples (the video's data, two moons, rings, mixed densities); step mode as in the video. A live check recomputes every label from the definition, without the visiting order.
    - **`os.memory.page_replacement`** (CSE231): FIFO, LRU and Optimal on the reusable **stepper engine** (`_engines/stepper/`: controls, code line, predict questions, keyboard, shareable link). A second implementation checks it live, and Belady's anomaly is shown.
  - **The classifier:** `src/profsagent/sims/classify.py` labels each of the 9,784 weekly topics from `data/enriched` with a type or "none". It uses the local MiniLM model (no AI calls), calibrated on 165 topics hand-labelled by Claude for Amit's review.
- **Checked:**
  - **Browser QA:** `scripts/sims.py qa` passes 8 of 8.
  - **DBSCAN:** all 3,312 labels agree with scikit-learn (4 datasets × 4 ε × 3 minPts); 22 steps, as in the video.
  - **Page replacement:** textbook answers (FIFO 15, LRU 12, Optimal 9; Belady 9 → 10), and 5,400 runs agree with a Python implementation.
  - **Unit tests:** `tests/test_sims.py` has 12.
  - **Classifier:** 73% cross-validated, against 51% for always answering "none". 51% of all topics get a type; Psychology is mostly "experiments on yourself" and Economics "decisions and games".
- **Agreed by:** Amit (the plan); built by Amit with Claude.
- **Open:**
  - **Amit:** review `simulations/classifier/labels.tsv`. The classifier over-assigns "networks" in CSE and under-assigns Environmental Science and Communication; better examples in `types.yaml` are the next step.
  - **Next (A2):** the decisions-and-games and experiments-on-yourself engines, and the app integration (S2 suggestions, Simulation (A) tab).

## 2026-11-02: simulation catalogue and build plan for every kind of course (proposal)

### 24. Simulations for every kind of course: 12 simulation types, one engine each, a catalogue, and a Simulation (A) tab
- **Proposal:** `docs/09_phase2_A_simulation_catalogue.md` v0.2 (+ PDF, 9 pages). v0.1 covered only maths, signals and ML; Amit asked for a plan that handles every kind of course.
  - **Topics are classified by what students do,** not by subject. There are **12 types**: step-through process, parameter explorer, systems over time, chance and crowds, networks, machines inside, code sandbox, data explorer, 3D models, decisions/games/role-play, experiments on yourself, and maps/timelines/arguments. Virtual labs, classroom games and studios are built from these.
  - **Each type has** one engine, its own independent check, and a configuration format. "No simulation recommended" (with a better format suggested) is a valid outcome.
  - **Coverage:** every IIIT-D department is mapped with real weekly topics from the knowledge graph (CSE, ECE, Maths, Design, SSH, Biology, Sociology, Entrepreneurship, Economics, Psychology, AI, Communication, Environmental Science, Management), and so are other disciplines for later.
  - **Special situations:** sensitive topics, AI role-play partners, running student code, security labs, lab courses, heavy computation, datasets, multi-player games, assessment, language and accessibility.
  - **Tracking:** catalogue entries (`sim.yaml`) carry versions and change logs, the professor's class example is saved, and a student's state lives in the page's link.
  - **In the app:** a Simulation (A) tab on the lecture page (mock-up in the doc).
- **Why:** to plan engines in the order that opens the most departments, rather than one-off simulations per subject.
- **Changed:** docs only (`docs/09_*`, `docs/img/09_simulation_tab_mockup.png`). No code yet.
- **Agreed by:** Amit (proposal).
- **Open:**
  - **Vihan:** survey keys `simulation` / `sim_note`, review kind `simulation`, graph labels (doc 09 §9).
  - **Parth:** the simulation slide.
  - **Team:**
    - the 12 types and the engine order;
    - which department follows CSE/ECE;
    - the rules for sensitive topics and the AI role-play partner;
    - the `simulations/` repo layout.

## 2026-10-29: the professor can change everything at the checks, in place

### 23. Fix in Vihan's `_post_deadline`: every gzipped Gemini reply failed (for Vihan)
- **What happened:** after pulling 8f27687, Web Development stopped at "Writing course outcomes" with `httpx.DecodingError: Error -3 while decompressing data: incorrect header check` (`llm/client.py` line 233). The fix is in the same file.
- **Cause:** `_post_deadline` collected the reply with `r.iter_bytes()`, which already unzips it. It then built `httpx.Response(..., headers=r.headers, content=...)` with the original `Content-Encoding: gzip`, so httpx tried to unzip the plain bytes a second time.
  - Gemini replies are gzipped, so **every Gemini call** failed. Groq and NVIDIA replies are not compressed, which is why the Context step (G3 on Groq) still worked.
- **Changed (Vihan's file, with Amit's OK):** `llm/client.py` `_post_deadline` collects `r.iter_raw()` (the bytes as sent), so the rebuilt response is decoded exactly once.
  - One word changed, plus a comment. The whole-reply deadline is unchanged.
- **Checked:**
  - a real Gemini call through `_post_deadline` returns 200 with `Content-Encoding: gzip` and the text "OK";
  - NVIDIA `minimax-m3.1-flash` and `nemotron-3.5-lightning` return 200 through the same path;
  - the full suite passes (366).
- **Keys:** Amit's `.env` now has `NVIDIA_API_KEYS` (1 key; tested OK), so the NVIDIA fallbacks in `config/models.yaml` are usable on his laptop too.
- **Agreed by:** Amit.
- **Open (Vihan):** please keep `iter_raw()` if you change `_post_deadline` again. A test with a gzipped fake response would catch this.

### 22. "Should NOT become" lines are written as plain phrases
- **Decision:** the AI fill in the Details step (`app/filler.py`) writes each "should NOT become" line as one plain phrase, e.g. "a front-end-only design course". No double negatives such as "… without backend logic".
- **Why:** on Web Development the filled line "…nor focus purely on static visual design without functional backend logic" was split by G3 into two hard rules:
  - K15 *must include* "functional backend logic";
  - K16 *must exclude* "static visual design without functional backend".
  - The conflict check compares words, and 2 of K15's 3 words appear in K16, so it raised `VK-CONFLICT`. Both rules actually ask for the same thing, so it was a false alarm that blocked the Context check.
- **Changed:** `app/filler.py` (the `intent_avoid` instruction).
- **Agreed by:** Amit.
- **Open (Vihan):** the root cause is in `validate/constraints.py` `conflicts()` (lines 499–503), which uses `text.covers()`: ≥ 60 % shared words counts as "the same thing". Two options:
  - skip the pair when the exclude phrase says "without <the required thing>";
  - or compare meaning with the local embedding model before calling it a conflict.

### 21. Edit at the Context, Outcomes and Final checks: change, check again, continue (no restart)
- **Decision:** everything ProfsAgent wrote can be changed by the professor on the check screens.
  - **Save and check again** applies the change to the run, re-runs the same deterministic checks (no AI calls) and refreshes the open problems on the same screen.
  - If the problems are gone, **Continue** needs no reason.
  - Before this, a professor who disagreed could only continue with a reason or stop and start again, about 40 minutes for a new run.
- **What can be changed:**
  | Check | Editable |
  |---|---|
  | Context | topic groups and topics (add, remove, rename, reorder); course level and mid-sem week (the other assumptions can be confirmed); the rules made from the professor's words (reword the checked phrase, must/preferred, remove, add); prerequisites (add/remove; codes must exist in the course database). The regulation rules stay fixed. |
  | Outcomes | every CO: statement, Bloom level, condition, standard, topic groups, evidence; add or remove COs. Its LOs (statement, level, condition, standard, how assessed; add, remove, reorder) and its programme-outcome links (strength 1–3, add, remove). Reject the AI's proposed topic changes. |
  | Final sheet | modules and topics (titles, hours, order, which LOs a topic teaches; the weeks are then planned again by the pipeline's own scheduler `deterministic.schedule`); labs (title, week); assessment (weights, invigilated, due weeks, add or remove a component; the CO marks shares are recomputed); books and papers (role, remove, add by ISBN or DOI, looked up on OpenLibrary or Crossref and added only if found); the course description. The proposal and the Excel template are drawn again. |
- **How it works without changing the pipeline:**
  - **Where an edit goes:** at a check the pipeline is paused in a LangGraph `interrupt`, and on resume `orchestrator/graph.py` re-attaches from `state.json` and `design_graph.json`. So `app/edits.py` edits those two files while the run waits.
  - **The design graph is updated the same way the stage writes it,** so Neo4j gets the professor's version. Changed nodes get `created_by: professor`.
  - **The rechecks** run `engine.check` per stage, and `engine.gate_view` gives the new open problems. When the professor continues, the gate recomputes its view from the edited state, so the same result holds inside the pipeline.
  - **Every change is recorded:** in `state["professor_edits"]`, in `run.log`, and on the approval (`professor_edits` in the gate decision, so it reaches the Approval node). The Review record lists them.
- **Checked:**
  - **Tests:** 14 new tests in `tests/test_app_edits.py`, on copies of `cs601-02` cut back to each check (52 app tests pass). Among them, the Web Development case: removing K15 clears the `VK-CONFLICT`.
  - **Screens:** a headless click-through of every editor at laptop and phone width, with no page errors.
- **Changed:** `app/edits.py` (new), `app/runner.py` (`edit`, and edits stored with the decision), `app/server.py` (`POST /api/runs/{id}/edit`), `app/views.py` (editable data on each check screen) and `app/static/index.html` (Edit buttons and editors).
- **Agreed by:** Amit.
- **Open (Vihan):**
  - **A "revise" decision inside the pipeline.** Native support would be cleaner than the app editing the paused run's files: `resume={"decision": "revise", "changes": …}`, with the stage applying the changes and the gate asking again. The app would then send its edits that way. Until then the app's edits rely on the gate re-reading `state.json` on resume, so please keep that behaviour, or tell Amit if it changes.
  - **Topic overlaps aren't recomputed after topic edits.** Context shows the S2 overlaps worked out from the topics before the edit, with a note saying so; recomputing them needs the KG in the app.
  - **Professor's text isn't rewritten by the AI.** A CO, LO or rule the professor wrote is checked by the deterministic rules only (verb, Bloom level, length, conditions); later stages build on it as written.

## 2026-10-28 (night): Parth's lecture slides (deliverable B) in the app

### 20. Generated slides on the lecture page, through Parth's `generate_material` and `content.review`
- **Decision:** when the professor ticks **Generate the lecture material for me**, saving the choices starts Parth's `content.generate.generate_material(run, lecture, {note})`. It runs as a background job in its own process (`app/delivery_step.py`, kind `material`), like the resource search.
  - **When slides are made:** once, when the choice is first saved. After that only on request: **Generate again**, or **Redo with my instructions**, whose text becomes B1's `feedback`.
  - **Optional second-AI check:** a box (`review: "ai"`, B2) for a professor in a hurry; it costs 1–2 more AI calls.
  - **Approved slides are protected:** replacing them asks for confirmation (`force`).
- **The Generated slides tab** (shown whenever slides exist for the lecture):
  - **Top:** status (draft · "checked by a second AI, not by you" · approved · being redone · rejected), slide count, minutes, the AI reviewer's verdict, and downloads (`slides.pptx`, `notes.md`, `quiz.json`).
  - **Review:** approve / redo / reject go through `content.review.write` + `apply` (`material/review.yaml`). A reason is required for redo and reject.
  - **Below:** every problem found by Parth's checks, then a preview of each content slide from `deck.json`, numbered as in the .pptx (from slide 3). It shows bullets, flow, code or table figures, quizzes with the answer marked, outcomes, sources and speaker notes.
  - **Elsewhere:** a slides chip on the lecture list, a progress row, and approved slides offered in the student view.
- **Not connected:** `attach_material` (Parth: not built yet). The choice and uploaded files are saved for it.
- **Checked:**
  - **Tests:** 4 new app tests (14 delivery tests in all). Parth's own W01.L1 deck is used for the preview and review.
  - **Live:** W05.L2 on a CS-601 example copy took 73 s and gave 8 slides (5 with content, for a 30-min topic), 0 errors and 0 warnings.
  - **Screens:** a headless click-through at laptop and phone width on a read-only copy of the app.
  - **Full suite:** 360 pass.
- **Changed:** `app/delivery.py` (`material_summary`, `material_detail`, `material_review`, `queue_material`), `app/delivery_step.py`, `app/server.py` (4 endpoints) and `app/static/index.html`.
- **Agreed by:** Amit. Parth's code is unchanged.
- **Open:**
  - **Parth:** `scripts/compare_validation.py` line 181 uses a Python 3.12 f-string (the same quotes nested inside), so it fails to import on Python 3.10, and `tests/test_llm_check.py` fails on Amit's laptop. Use other quotes there, or agree that the team runs Python ≥ 3.12.
  - **Team:** Parth's per-class decks (`W03.S1`, 90-min classes) have no place in the lecture list yet. The UI follows C's per-topic lectures (`W03.L1`). Decide whether the survey and C move to class ids.

## 2026-10-28 (late evening): the app on Vihan's delivery update (e4ace89)

### 19. Why the app found no resources or speakers, and what changed
- **Cause:** a crash, not a missing key. `delivery/experts.py` line 164 (`iiitd_faculty`) takes `research_queries[0]`, but the query planner returns **no** research queries for applied topics.
  - Both Web Development lectures tried (W01.L1 HTML, W01.L2 CSS) had 0 research queries, so each search ended in `IndexError` after finding the academics, and nothing was saved: no resources, no speakers.
  - The other three places in `experts.py` already fall back with `or [b["topic"]]`.
- **App change (Vihan's file not edited):** the app's search process (`app/delivery_step.py`, `guard_empty_research_queries`) wraps `iiitd_faculty` so an empty list falls back to the lecture topic.
  - **Verified:** re-running W01.L2 on a private copy now saves 3 videos and 2 readings (MDN among them; 9 of 58 candidates passed).
- **Speakers:** for CSS, no speaker passed. Of 27 candidates, 10 were assessed and none reached Vihan's floor (topical fit ≥ 0.5, total ≥ 0.45). OpenAlex finds unrelated researchers for an applied topic. The one real CSS expert found (Jen Simmons) scored 0.21. That is the quality floor working, not a key problem.
- **Vihan's update taken into the app:**
  - lectures saved as `partial` (blocked transcripts) show an amber Partial banner and status, and a **Finish the search** button. It runs a plain `recommend`, which redoes only partial lectures;
  - the new D2 filters and the provider order need nothing from the UI.
- **Delete:** removing a course now also removes its lecture-delivery records from Neo4j (`(:Delivery {run_id})`), not only its design records (`app/runner.py`).
- **Installed on Amit's laptop:**
  - `ddgs`, new in Vihan's update;
  - `youtube-transcript-api`, in the README install line but missing here. Without it, videos were judged from title and description only, and Vihan's transcript test failed.
- **Keys:** compared with Vihan's `.env`, Amit's lacked `OPENALEX_API_KEY` (added later the same evening, tested OK) and still lacks `NVIDIA_API_KEYS` (an optional, faster LLM fallback when Gemini is slow or out of quota).
- **Tests:** 220 pass, including 2 new app tests (the guard, partial lectures).
- **Agreed by:** Amit.
- **Open (Vihan):**
  - change line 164 to `((q or {}).get("research_queries") or [b["topic"]])[0]`; the app's guard then becomes a no-op;
  - consider a practitioner-first speaker search for applied topics (web development, tools), where academic records don't fit.

## 2026-10-28 (afternoon): Phase 2 deliverable B, slide generation v1

### 18. Lecture slides are generated per lecture from the brief, checked in code and rendered as editable .pptx
- **Decision:** `generate_material(run_id, lecture_id, options)` (`src/profsagent/content/`) is B's call for the survey's
  `generate_material` choice.
  - **One AI call (B1) per lecture** writes only the content slides.
  - **Code writes the rest:** the title, objectives and references slides, from the brief and the cited sources.
  - **Checks in code:** LO coverage, slide count per hour, figures, quizzes, references, density, timing.
  - **Repair:** at most one call, kept only if errors drop.
  - **Rendering:** python-pptx, native shapes, text fitted to its box, `D-OVERFLOW` when it cannot fit.
- **Sources:**
  - The course's verified Phase 1 resources, plus C's resources once the professor approved them ("retrieve before
    generate", D6).
  - Pending C items only with `include_pending` (tests).
- **Reference: THU-MAIC/OpenMAIC.**
  - **Taken:** structured quiz scenes (options, answer, explanation; answer in the speaker notes only), a versioned deck
    contract (`schema_version`), and checks on the rendered layout.
  - **Not taken:** narration, AI classmates, interactive HTML. Their pipeline is a web classroom; ours produces material
    the professor edits and teaches.
  - **For v2:** outline first, then slides, with a professor gate between.
- **Why:** the slide text is the only part that needs judgement. The structure, references and checks are fully
  decided by the course design, so code owns them, as in Phase 1.
- **Checked:**
  - **Tests:** `tests/test_content.py`, 10 offline tests with a fake AI.
  - **Live:** cs601-02 W01.L1 gave 21 slides, 0 errors and 0 warnings, in 1 call. It was inspected as images through
    PowerPoint. Code panels and bullets were fixed after that inspection.
- **Changed:**
  - **Code:** `src/profsagent/content/` (models, checks, render, generate).
  - **Prompt and settings:** `prompts/content/B1_lecture_deck.md`, `config/content.yaml`.
  - **Script and tests:** `scripts/run_content.py`, `tests/test_content.py`.
  - **Docs:** README, `updates.md`.
- **Added the same day:**
  - **Code checks:** snippets are syntax-checked with real compilers (`D-CODE`); a missing compiler gives
    `D-UNVERIFIED`, never a pass.
  - **Citation checks:** a citation that matches its slide weakly gives `D-GROUND`. The floor of 0.35 is calibrated
    on W01.L1 (cited median 0.38 vs uncited 0.28).
  - **Professor review:** `material/review.yaml` with approve, redo or reject. A redo passes the reason to B1; an
    approved deck is protected.
  - **Slide numbers:** findings, quiz.json and the handout use the slide numbers of the .pptx.
  - **AI review for a professor in a hurry** (`content/ai_review.py`, prompt B2, `--auto-review`, off by default):
    - **The reviewer is never the writer:** one call to a model other than the deck's generator (the client's new
      `exclude_models`, as for the Stage 5 judges). It reports wrong facts, code that does the wrong thing, ambiguous
      quiz questions, unclear steps and level mismatches (`D-AI`).
    - **Blind quiz check:** it answers every quiz question without the key; a different answer is `D-QUIZKEY`.
    - **Repair:** its errors get one B1 repair, kept unless the code checks find more errors. Fixed errors stay as
      `D-AI-FIXED` warnings for a glance, because the reviewer does not re-read the new slides.
    - **Status `ai-reviewed`, never `approved`:** only the professor approves. A failed review leaves a draft.
    - **Cost:** 1 more call per lecture, 2 when the reviewer finds errors.
  - **JDK installed** (Temurin 21): Java snippets are now compiled. On W01.L1 it confirmed the `query.blank()` bug
    (slide 17).
- **Agreed by:** Parth. **Open:** the `attach_material` processor; the UI screens (Amit); measuring the AI reviewer
  on planted mistakes (not done: no new mutations for now).

## 2026-10-28 (night): validation and evaluation as one layer each; course-fit warnings

### 17. Validation has one entry point, evaluation runs all three tiers, and two course-fit warnings are added
- **Decision:**
  - **Validation:** `validate/engine.py` is the only way into validation: it selects the profile (`configure`, moved
    from `agents/pipeline.py`), runs the checks and counts errors. S8 resources now go through it too.
  - **Default profile:** stays `core` (rules + IIIT-D graph checks: 23/23 planted defects, no AI calls). The LLM check
    stays optional (4/23 alone).
  - **Evaluation:** `evaluate/engine.py` runs tiers 1–3 after every design. Tier 2 runs only with a reference sheet.
    Tier 3 is only planned (0 calls) unless judging is switched on.
  - **Two warnings in a new family, `fit`, settled by the professor and never sent to R1:**
    - `VC-AUDIENCE`: the title names a broad audience ("for All", "101") at level 3+.
    - `VC-NOLAB`: at least half the LOs are hands-on, P = 0, and no lab decision was given.
    - Either sends the design to REVIEW.
- **Why:**
  - The title-only run `dept-webdev-title-01` ("Web Development for All") passed every check as a level-3 course with
    no lab. Nothing turned "for All" into a requirement, so no rule was broken.
  - The level was inferred, so only the professor can settle it at gate 1.
  - "Introduction to" is deliberately not an audience word: 22 of the 39 IIIT-D "Introduction to …" courses are level 5–6.
- **Checked:**
  - **Findings:** every saved run's findings before and after (32 runs): the only difference is the two new warnings on
    `dept-webdev-title-01`.
  - **Benchmark:** the 23-defect rules benchmark is unchanged (23/23; `eval/compare_validation/rules.json` identical).
  - **Tests:** 297 tests pass.
- **Changed:**
  - **Validation:** `validate/engine.py`, `validate/rules.py`, `validate/report.py`, `config/pedagogy.yaml`
    (`hands_on_without_lab_share`).
  - **Evaluation:** `evaluate/engine.py` (new), `evaluate/reference.py` (`reference_code`), `evaluate/deterministic.py`.
  - **Callers:** `orchestrator/graph.py`, `agents/pipeline.py`, `agents/loop.py`, `render/proposal.py`.
  - **Scripts:** `scripts/evaluate_design.py` (`--all-tiers`, `--judge`), `scripts/evaluate_reference.py`.
  - **Tests:** `tests/test_fit_rules.py`, `tests/test_evaluation_engine.py`.
- **Agreed by:** Parth.

## 2026-10-28 (later): Phase 2 lecture delivery in the app

### 16. Vihan's deliverable C is wired into the app, following `docs/04_phase2_UI_integration_guide.md`
- **Decision:** the app gets a **Lecture delivery** section (screens S0–S8 of the guide) for every approved course, reached from the header, the course cards and the finished-course page.
  - **Choices:** the summary always comes first; the choices are multi-select; reasons are required to replace or reject.
  - **Kit and students:** the guest kit is copy-only (no Send); students see approved items only.
  - **Warnings:** always shown, never hidden behind a click.
- **API framework (guide question a):** FastAPI, the same server as course design. The endpoints follow guide §5: `/api/delivery/{run}/…` for survey, start, review, undo, own links, ratings, link check, guest kit and report.
- **How the backend is used:**
  - **Searches:** `pipeline.recommend` runs as a background job in its own process (`app/delivery_step.py`), so the page stays usable and Delete can stop it. `graph.write` follows each search (skipped if Neo4j is down).
  - **Decisions:** each one is written to `review.yaml` and applied at once with `review.apply`.
  - **Choices:** written with `survey.save`. A search starts only when resources or a guest are chosen, and repeats (`refresh`) only when those choices change.
  - **Link check:** `review.health` runs as a job; dead links show on the lecture with a one-click Replace.
- **Two additions the guide left to the UI:**
  - **Own links** (S5, "store it in the UI"): kept in `delivery/app_own_links.json` and shown as approved.
  - **Ratings:** `review.record_feedback` adds up every row of `feedback.yaml` each time it runs, so the app writes one rating per call and keeps the history in `delivery/app_feedback_log.yaml`. That way no rating is counted twice.
- **Attachments (guide question c):** stored in `runs/<id>/delivery/attachments/<lecture>/`. The survey records them as `delivery/attachments/<lecture>/<file>`.
- **Vihan's run stays untouched:** the app never edits `runs/cs601-02`. "Open a copy of the CS-601 example" copies it into `runs/app-cs601-example-NN`, with its real results for W01.L1, W01.L2 and W02.L1.
- **Changed:**
  - `src/profsagent/app/delivery.py`, `app/delivery_step.py`, `app/server.py` (16 endpoints) and `app/static/index.html`;
  - tests: `tests/test_app_delivery.py` (8 tests on a temporary copy of cs601-02).
- **Verified:**
  - a headless click-through at laptop and phone width (choices, review, own link, guest shortlist, kit, continuation lecture, validation, student view and rating);
  - one real search through the app (W03.L1, readings + practice, 6.4 min).
- **Agreed by:** Amit (integration); the backend is Vihan's, unchanged.
- **Open:**
  - **B (Parth):** "attach my material" and "generate material" are saved in the survey, with files stored, but nothing runs yet: guide §4 says "Parth to define the call" (question b).
  - **Search keys on Amit's laptop:** `.env` has no `YOUTUBE_API_KEY` (free; needed for videos, recorded lectures and clips) and no `TAVILY_API_KEY` (free tier; better reading search). The real test found 12 candidates, and all 12 failed C's checks. Six covered neither the topic nor its outcomes. Four were Open Library book records with titles only, which the AI reviewer couldn't judge. Four were pages that refused access or were PDFs C cannot read. Several had more than one problem. The app shows a banner until the YouTube key is added.
  - **PDFs (Vihan):** C's page reader rejects PDFs ("unsupported content-type application/pdf"), which drops arXiv and publisher papers. Reading PDFs, or preferring arXiv's HTML version, would help.
  - **Ratings file (Vihan):** the first rating creates `data/delivery_feedback.json` (per-source averages). Decide whether to commit it or add it to `.gitignore`.

## 2026-10-28

**Verified the same day.** The Web Development course was re-run from the same professor form (`app-web-development-02` vs `-01`, local runs):
- **CO length:** COs are 11–15 words (before: 32–43), with no V11 or length warnings on COs.
- **Books:** all 8 books pass the independent ISBN check.
- **Activity column:** no more exams in it.
- **PDF:** the explanations sit in the mapping cells.
- **Result:** 0 open errors; Neo4j checks 14/14.

**Open, found during that check:**
- **Duplicate editions:** the same book can now be listed twice in different editions ("Learning React" 2020 and 2017). Resources should be de-duplicated per work (`agents/pipeline.py` `_verify_resources` / G10). Needs Vihan.
- **Excel lock:** when `templates/iiitd_cse_course_template.xlsx` is open in Excel, Windows locks it and a run cannot write `course_template.xlsx` (the run still finishes; the log says so). Reading the template into memory, or copying it first, would avoid this. Needs Vihan (`render/course_template.py`).
- **Odd verbs:** two of the shorter COs use analytical verbs that read oddly for a hands-on course ("Examine client-side pages…", "Differentiate component-based single-page applications…"). This probably comes from the template rule that at least half the COs be BL4–BL6. Watch the next runs before changing anything.

### 1. Course outcomes are written short, like IIIT-D's own
- **Decision:**
  - A CO statement is one short sentence: the prompt aims for 15–25 words.
  - The length warning (VT-LEN) now fires above **35 words** instead of 50.
  - The full condition and degree stay in the CO's separate `condition` / `degree` fields, where the assessment stage reads them.
- **Why:** generated COs ran 32–43 words (the Web Development run). The 1,899 COs IIIT-D professors wrote (Layer A corpus) have a median of 16 words, and 96% have 35 or fewer.
- **Changed:**
  - `config/pedagogy.yaml`: `thresholds.statement_words.CO` changed from [8, 50] to [8, 35]. **Parth:** this is your VT-LEN limit from validation v2.
  - `prompts/generation/G4_course_outcomes.md` (version 0.3.0 → 0.4.0): the short-sentence rule, and shorter worked examples.
- **Agreed by:** Amit, Vihan.

### 2. "Condition / degree not visible in the statement" (V11) is checked for learning outcomes only
- **Decision:** COs no longer get this yellow warning. LOs still do, since each LO is one concrete task. The V11 *errors* (missing or vague condition/degree) still apply to both.
- **Why:** a short CO cannot carry its full condition and degree, and the warning was pushing COs to grow long.
- **Changed:** `src/profsagent/validate/rules.py` (V11 visibility check skipped when `kind == "CO"`).
- **Agreed by:** Amit, Vihan.

### 3. A book's ISBN, year and publisher come from one and the same edition
- **Decision:** for each Open Library work, use the **newest proper edition**: English (or language not stated), the same title, an author of the work, a real publisher (no self-published reprints such as CreateSpace) and an ISBN-13. If no edition qualifies, the book gets no ISBN rather than a wrong one.
- **Why:**
  - The work search returns the ISBNs of *all* editions and the *first* publication year. The code took the first ISBN, so the Web Development sheet cited "Flanagan (1996), JavaScript: The Definitive Guide" with the ISBN of a 2017 CreateSpace reprint.
  - "MongoDB: The Definitive Guide (2010)" carried a 2019 ISBN.
  - The check passed because it compared the pick with that same mixed record.
- **Result:**

  | Book | Now cited as |
  |---|---|
  | JavaScript: The Definitive Guide | 2020 O'Reilly 7th edition (ISBN 9781491952023) |
  | Learning React | 2020 2nd edition |
  | MongoDB: The Definitive Guide | 2013 2nd edition |
  | Express in Action | unchanged |
- **Changed:** `src/profsagent/research/resources.py`:
  - new `best_edition()`;
  - `openlibrary()` now asks for `author_key` and records `first_published` separately.
- **Agreed by:** Amit, Vihan.

### 4. The template's "Assignment/lab/tutorial" column lists only that kind of work
- **Decision:** the topic table's activity column shows assignments, labs, tutorials and project or report work. It no longer shows quizzes, mid-sem or end-sem, which are already in the assessment plan.
- **Why:** almost every row said "MidSem; EndSem", which hid the activities the template asks for.
- **Changed:** `src/profsagent/render/course_template.py` (`ACTIVITY_TYPES`); the Excel and PDF both use it.
- **Agreed by:** Amit, Vihan.

### 5. PDF: each CO–PO explanation sits beside its strength
- **Decision:** in the course-sheet PDF, a mapping cell shows the strength (1–3) and, under it, the explanation. This matches the template's CO / CO-Explanation column pairs. The Excel output already had them.
- **Changed:** `scripts/export_course_sheet_pdf.py` (`mapping_cell`).
- **Agreed by:** Amit, Vihan.

### 6. App: a second, independent check of every ISBN and DOI
- **Decision:** at the final check, the app looks every ISBN (Open Library edition record) and DOI (Crossref) up again on its own, and compares title and year with the citation. A mismatch shows as a yellow "Check failed" warning on the book.
- **Changed:** `src/profsagent/app/views.py` (`reference_check`, cached in `runs/<run>/reference_check.json`).
- **Agreed by:** Amit.

### 7. App: no name, no AI notice, no "On this laptop" label
- **Decision:**
  - The form no longer asks for the professor's name or for an AI-service consent tick.
  - Decisions are recorded as `APP_USER_NAME` from `.env`, or "Professor".
- **Note:** Gemini's free-tier terms still apply (Google may use prompts). When professors type into the app, tell them in person.
- **Changed:** `app/formmap.py`, `app/runner.py`, `app/server.py`, `app/static/index.html`.
- **Agreed by:** Amit.

### 8. App: Delete a course at any stage, into a bin
- **Decision:** every course has a Delete button.
  - **Files:** the course folder moves to `runs/_deleted/<run>-<time>/`. Nothing is erased, so a mistake can be undone.
  - **Neo4j:** an approved design that was published there is removed again, with `design.neo4j_sync.delete_run`.
  - **Running work:** each pipeline step now runs in its own process (`app/stepper.py`), so Delete ends a step that is in progress.
- **Changed:**
  - `app/runner.py` (`delete`, `_run_step`), `app/stepper.py`, `app/server.py` (`DELETE /api/runs/{id}`);
  - `.gitignore` now ignores `runs/app-*/` and `runs/_deleted/`, so courses made in the app never reach GitHub.
- **Agreed by:** Amit.

## 2026-10-27

### 9. Collect all missing information first, let the professor check it, then design
- **Decision:**
  - Only the course name and description are required.
  - Every field left blank (topics, intent, credits, L-T-P, weeks, programmes, year, background, lab, assessment preferences…) is filled in first by one AI call.
  - That call is grounded in the description, the most similar IIIT-D courses (Layer A) and the regulation/template rules. Code then checks each value: allowed choices, the regulations' hours and weeks, and only cited courses that were actually shown.
  - The professor edits and confirms the complete form (the app's **Details** step) before the pipeline starts.
  - So the app has four checks: Details, Context, Outcomes, Final sheet.
- **Why:** the pipeline's intake (G1) never fills a missing field, and defaults cover only five regulation values. A test run with topics left blank designed a course with 0 topic groups and 0% overlap with every IIIT-D course.
- **Changed:** `src/profsagent/app/filler.py`, `formmap.py`, `runner.py`, `views.py`. The pipeline itself is unchanged; it simply receives a complete form.
- **Agreed by:** Amit.

### 10. A local web app for professors (platform step 1)
- **Decision:** a FastAPI app (`python scripts/run_app.py`, http://127.0.0.1:8000) drives the existing pipeline unchanged:
  - background runs, one at a time;
  - the gates with their sources shown;
  - approving with open errors needs a reason, recorded as an override; stopping needs a reason;
  - a quota pause that continues by itself;
  - downloads, and feedback ratings saved per run.
- **Changed:** `src/profsagent/app/`, `scripts/run_app.py`, `tests/test_app.py` (commit `1e38241`). Extra install: `pip install fastapi uvicorn markdown`.
- **Agreed by:** Amit.
- **Open:** letting professors *edit* outcomes at a gate (today a gate takes approve or stop with a comment). Needs Vihan.

### 11. Hosting: Amit's laptop, free tiers only
- **Decision:** the platform runs on Amit's laptop with the free Gemini/Groq keys and Neo4j Desktop. An IIIT-D server is requested only if professors want to use it themselves. No paid hosting.
- **Why:** free tiers were chosen, and Hugging Face Docker Spaces now need a paid plan.
- **Agreed by:** Amit.

### 12. Phase 2, deliverable A: simulations plan
- **Decision:** simulations follow "reuse → template driven by real code → new generation", always checked automatically and approved by the professor. Full plan in `docs/05_phase2_A_simulations_and_tools.pdf` (commit `3471d31`).
- **Open (Vihan):** a `simulation` choice in `survey.yaml` and a `simulation` review kind, as proposed in section 6.1 of that document.

## 2026-10-15

### 13. Generated courses in Neo4j, and a safer wipe (commit `05a2eac`)
- **Decision:**
  - `Neo4jKG.topic_candidates` returns only topics with similarity ≥ 0.66, so an empty answer means the topic is new to IIIT-D.
  - The pipeline keeps a SAME_AS topic link only if it is among those candidates.
  - `load.py --wipe` deletes only Layer A labels and re-attaches design runs.
  - Generated courses get a code (department prefix + 1001, 1002, …), readable captions and hub links.
  - `check_run()` runs after each load.
- **Changed:** `kg/neo4j_kg.py`, `agents/pipeline.py`, `orchestrator/graph.py`, `design/neo4j_sync.py`, `scripts/load_design_to_neo4j.py`, `src/profsagent/ingest/load.py`.
- **Agreed by:** Amit. Vihan was to be told about the edits to his files (`neo4j_sync.py`, `pipeline.py`, `graph.py`).

## 2026-10-13 to 2026-10-14

### 14. The pipeline reads the Neo4j institutional graph by default
- **Decision:**
  - `KG_BACKEND=neo4j` is the default; `run.kg_backend: stub` or `KG_BACKEND=stub` brings the stub back.
  - The backend is recorded per run, so a resumed run keeps it.
  - `kg/stub.py` and `data/stub_kg` stay (contract tests, helpers).
- **Changed:** `agents/pipeline.py` (`make_kg`), commits `3db4ca9`, `9fc23e5`; README `048565e`.
- **Agreed by:** Amit, Vihan.

### 15. Local embeddings for the knowledge graph, topic-match cut-off 0.66
- **Decision:**
  - The Neo4j connector embeds with a local model (`all-MiniLM-L6-v2`, CPU, no key, no quota) instead of Gemini.
  - Topics count as the same at similarity ≥ 0.66, calibrated on 218 labelled pairs (about 80% right; AUC 0.91 vs 0.85 for Gemini).
- **Changed:** `kg/neo4j_kg.py`, commits `6d0697e`, `e38ccd2`, `5011a2a`, `3db4ca9`.
- **Agreed by:** Amit, Vihan.
