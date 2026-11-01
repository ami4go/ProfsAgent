# Decisions and changes log

A running record of the decisions the team takes and the changes that follow from them, so anyone can see **what**
changed, **why**, **who agreed**, and **where** in the code. Newest first.

**How to add an entry:** date, a one-line title, then *Decision*, *Why*, *Changed* (files, commits) and *Agreed by*.
Mark anything still waiting for someone as **Open**.

---

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
