# Decisions and changes log

A running record of the decisions the team takes and the changes that follow from them, so anyone can see **what**
changed, **why**, **who agreed**, and **where** in the code. Newest first.

**How to add an entry:** date, a one-line title, then *Decision*, *Why*, *Changed* (files, commits) and *Agreed by*.
Mark anything still waiting for someone as **Open**.

---

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
