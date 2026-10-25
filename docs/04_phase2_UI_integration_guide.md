# ProfsAgent Phase 2 · UI integration guide (for Deliverable A)

**For:** Amit (A: UI and simulations)
**From:** Vihan (C: learning resources and guest speakers)
**Also involves:** Parth (B: lecture material and content generation)
**Status:** C's backend is built and tested on CS-601 (`runs/cs601-02`). This guide describes what the UI must show, in what order, what each button does, and which backend function or file is behind it.

---

## 1. The idea in one paragraph

Phase 1 produces an approved course design. Phase 2 helps the professor **deliver** it, one lecture at a time. For **every lecture** the UI first shows a short summary of what the lecture covers. The professor then picks **how they want to deliver it**, and **several options can be picked together**. Each picked option starts its own piece of work, done by B or C. The results come back to the same lecture page, where the professor approves, replaces or rejects each item. Only approved items reach students. **Nothing is searched or generated for a lecture before the professor has made a choice for it.**

---

## 2. Who does what

| Part | Owner | What it does | UI's job |
|---|---|---|---|
| A | Amit | All screens; simulations and visuals | Render data, collect choices, call the backend, show progress |
| B | Parth | Generates lecture material (slides, notes) and works on material the professor attaches | Send the request, show the generated material |
| C | Vihan | Lecture briefs, the delivery-choice survey, learning resources (videos, readings, practice, recorded lectures, clip playlists), guest speakers, guest-lecture kits, the review gate, feedback, link health | Show the brief and choices; show resource and speaker cards; send the review decisions |

---

## 3. The full flow (screens in order)

```
S0 Pick course run ─► S1 Lecture list ─► S2 Lecture page: summary + delivery choices (ALWAYS FIRST)
                                                   │  (multi-select)
          ┌───────────────┬───────────────┬────────┴───────┬──────────────────┬──────────────────┐
          ▼               ▼               ▼                ▼                  ▼
   Own material   Attach material   Generate material   Assistance        Guest lecture
   (nothing to    (upload → B)      (→ B)              (→ C resources)   (→ C speakers)
    run)
          └───────────────┴───────────────┴────────┬───────┴──────────────────┘
                                                   ▼
                                    S3 Progress (one job per chosen option)
                                                   ▼
                                    S4 Results on the lecture page (one tab per chosen option)
                                                   ▼
                                    S5 Review: approve / replace / reject (+ reason) / add own link
                                                   ▼
                     S6 Guest kit + invitation draft (copy only, never sent)   S7 Student view (approved only)
                                                   ▼
                                    S8 Feedback ratings + link-health alerts
```

### S0 · Pick a course run

- List the finished Phase 1 runs (folders under `runs/`, e.g. `cs601-02`) with course name and status.
- When a run is opened for delivery the first time, build the briefs (`make_briefs`, see §6).

### S1 · Lecture list (the course timeline)

One row or card per lecture, grouped by week (CS-601 has 27). Each shows:

- **Lecture id** (`W01.L2` = week 1, lecture 2), **topic**, **module**, **hours**.
- A **★ New at IIIT-D** badge when `novel` is true: no IIIT-D course teaches a close match, so the lecture is likely hard to prepare. Make it visible: these lectures need help most.
- **Choice status:** "not decided" / the chosen options as small chips (Own · Attach · Generate · Resources · Guest).
- **Work status:** not started / running / ready for review / reviewed.
- **"Continues"** marker when the same topic runs over several lectures (`continues: true`).
- Filters by week, module, ★ new, status. **Bulk actions:** "apply these choices to the whole week / module", "same as previous lecture" (the CLI already has these, see §6).

### S2 · Lecture page: summary and delivery choices (always the first step)

This is the most important screen. **The choices must always be asked before anything is generated or searched.**

**(a) Summary card, shown at the top.** Use `summary` from `briefs.json`: a plain-language paragraph of about 95–160 words, generated from the design with no AI. It says:

- the hours and week, and the module it belongs to;
- whether it is new at IIIT-D;
- what students should be able to do afterwards (learning outcomes, with Bloom level);
- which course outcome it serves;
- what students already know, including prerequisite courses such as CSE201;
- what comes next, the labs, whether the topic continues, and where it is assessed.

Show it as a paragraph. Under it, put a **"More detail"** expander with the structured fields:

- learning outcomes (id, statement, Bloom level);
- course outcomes;
- `builds_on`, `prerequisite_courses`, `leads_to`;
- `assessed_in` (id, type, week);
- `labs`, `hands_on`, `outside_load_hours`;
- `iiitd_match` (closest IIIT-D topic and similarity).

**(b) "How do you want to deliver this lecture?"** Checkboxes, **several allowed**. Every chosen option becomes a task:

| Choice (survey key) | Label for the professor | Extra inputs shown when ticked | What happens | Owner |
|---|---|---|---|---|
| `own_material` | I'll teach it with my own material | none | Nothing to run. Marked as covered. | — |
| `attach_material` | I'll attach my material, work with it | **Upload files / paste links** → `attachments: [...]`; **What to do with it** (multi-select) → `attach_tasks`: `slides`, `summary`, `quiz`, `gap_check` (what the material misses against the learning outcomes), `enrich` (add examples or references) | Sends the files and tasks to B | B |
| `generate_material` | Generate the lecture material for me | (B decides its own options, e.g. slide count or style) | B generates slides and notes from the brief | B |
| `assistance` | Find learning resources for me | Five sub-toggles, each yes/no: `want_videos` (short explainers, talks), `want_readings` (blogs, articles, documentation, book chapters), `want_practice` (notebooks, exercises, datasets), `want_recorded_lecture` (a full lecture from another university, for a flipped class), `want_clips` (clip playlists: only the minutes of long videos that cover this lecture) | C searches, checks and ranks resources | C |
| `guest_lecture` | Suggest a guest speaker to invite | none | C finds, checks and ranks 5–7 speakers (researchers and industry, India and abroad) and writes a guest kit | C |

Also on this screen:

- **Confidence** 1–5 ("How confident are you teaching this topic?") and a free-text **note** (e.g. "students struggle with X"). C passes the note to its AI reviewer, so it is not decoration.
- Combinations are normal: *own material + resources + guest*; *attach + resources*; *generate + guest*. Do not make the options exclusive.
- The **Save / Start** button writes the answers (§6.2), then starts one job per chosen option (§4).
- Re-opening the page later shows the saved answers and lets the professor change them. When C's choices change (assistance or guest, or the `want_*` toggles), call `recommend` again for that lecture with `refresh: true`. Without it, C skips lectures that already have results.

### S3 · Progress

One progress row per chosen option ("Finding resources…", "Finding guest speakers…", "Generating slides…").

- C's work takes about **1.5–3 minutes per lecture**. Run it as a background job and never block the page.
- Progress text: tail `runs/<id>/delivery/delivery.log`. Lines look like `W01.L2: 54 raw candidates (22 videos)` and `saved W01.L2`.
- A job is done when `runs/<id>/delivery/lectures/<lecture_id>.json` is updated (`generated_at`).

### S4 · Results on the lecture page

One tab per chosen option: **My material**, **Attached material (B)**, **Generated material (B)**, **Resources (C)**, **Clip playlist (C)**, **Guest speakers (C)**.

#### Resources tab

Card groups in this order:

- **Videos**: at most 3.
- **Recorded lecture**: at most 1.
- **Readings**: at most 2.
- **Practice**: at most 1.

Each group is ranked; rank 1 is first. Data: `resources.items.<kind>[]` (kinds: `video`, `recorded_lecture`, `reading`, `practice`).

**Resource card fields** (all from the lecture JSON):

| Show | Field | Notes |
|---|---|---|
| Title (link) | `title`, `url` | Open in a new tab; for YouTube, embed if `embeddable` is not false |
| Source + tier badge | `source`, `tier` | Tier 1 = university/official course, 2 = known educator, 3 = official docs / recognised publisher, 4 = other |
| Duration / year | `duration_s` (format h:mm:ss), `published` / `year` | |
| Score | `total` (0–1) | Show as a bar or "0.91"; on hover show `scores` (coverage, quality, authority, level_fit, reception, practicality) |
| Why it was picked | `rationale` | One line; always show |
| AI review | `review.review`, `review.use_as` | `use_as` → label: `professor_prep` "for your preparation", `pre_class` "before class", `in_class_clip` "in-class clip", `after_class` "after class", `flipped_class`, `lab`, `practice` |
| Where the topic is covered | `coverage.per_target[*].segments[{start, end}]` | For videos: "Topic covered at 3:10–7:40" → link `url&t=190s`. `coverage.evidence` = `transcript` / `text` / `metadata` |
| Warnings (yellow) | `findings[]` with `severity: "warning"` | e.g. "no captions", "coverage judged from the metadata only". Always show them |
| Captions / licence | `captions`, `licence` | Accessibility and reuse |
| Actions | | **Approve · Replace · Reject** (S5) |

- **Reserve list** (`resources.reserve.<kind>[]`): next-best items, already checked. Not shown by default. A **"Show more"** link reveals them; **Replace** takes the top reserve item.
- **Removed items** (`resources.rejected[]`: title, url, `why[]`) are useful for a "Why not X?" panel. Hide them by default.
- **Counts** (`resources.counts`): "72 found · 15 passed the checks · 57 removed". This builds trust; show it small.

#### Clip playlist tab

Data: `resources.clips[]`, each `{target, video, source, url (with &t=), start, end, minutes}`. Show an ordered playlist: "Watch 0:45–4:10 of *Video X* for *learning outcome Y*". It appears only when `want_clips` is yes.

#### Guest speakers tab

Data: `experts.experts[]` (5–7, ranked), reserve in `experts.reserve[]`, removed in `experts.rejected[]` (`name`, `why[]`).

| Show | Field | Notes |
|---|---|---|
| Name, role, affiliation, country | `name`, `role`, `affiliation`, `country` | Country is a 2-letter code; show a flag or the name |
| Kind badge | `kind` | `academic` (researcher), `industry`, `iiitd` (IIIT-D faculty). IIIT-D faculty get no special treatment; they appear only if their score is good |
| Fit badge | `fit` | `strong` / `moderate` (from the AI check, run twice; the lower verdict is kept) |
| Why | `why` | ≤ 45 words, written for the professor |
| Evidence | `evidence[]` `{kind, title, year, url, venue}` | Papers, talks, repositories; show the top 2–3 as links |
| Profile links | `links` | Any of `openalex`, `orcid`, `scholar_search`, `dblp`, `github`, `website`, `page`, `talk` |
| Score | `total`, `scores` | Hover: topical_fit, teaching, practical, standing, recency, feasibility (time-zone fit for IST) |
| Suggested format | `suggested_format` | `live_remote_60`, `live_in_person` (India only), `recorded_talk`, `panel`, `qa_after_recorded` |
| Warnings | `findings[]` (warning) + `concerns[]` | e.g. "relevant papers appear in little-known venues; check before inviting" |
| How identity was confirmed | `verified_identity` | Small grey text, e.g. "OpenAlex author record + ORCID" |
| Actions | | **Shortlist (approve) · Replace · Reject** + **Open guest kit** |

**Continuation lectures.** When a topic spans several lectures (W01.L2 → W02.L1), the later lecture's JSON has `continuation_of: "W01.L2"`:

- its resources are the *next-best, different* items, so students get new material;
- `experts` is `{"same_as": "W01.L2"}`. Show "Same guest list as W01.L2" with a link; do not show an empty list.

### S5 · Review gate (approve / replace / reject)

Every shown item (resource or speaker) has three actions:

| Action | Needs a reason? | Effect |
|---|---|---|
| Approve | no | Item is frozen and can be released to students |
| Replace | **yes** (required) | Item is removed, and the top reserve item of the same kind takes its place |
| Reject | **yes** (required) | Item is removed, with nothing in its place |

- The backend refuses Replace or Reject without a reason. The UI should not allow sending them empty either.
- Also add an **"Add my own link"** button (pin a resource the professor already knows). This is planned in C's design but not built yet; for now, store it in the UI and show it as approved.
- The decisions are written to `review.yaml`, then applied (§6.4). Reasons also feed the learning loop: sources that keep getting rejected drop in future rankings.

### S6 · Guest-lecture kit

`runs/<id>/delivery/guest_kits/<lecture_id>.md` holds a speaker brief, the session's learning outcomes, what students have already seen, what follows, the ranked speakers, and an **invitation draft**.

- Render it as a page with a **Copy invitation** button.
- **The system never contacts anyone.** No "Send" button and no stored emails; the privacy check rejects any candidate whose record contains an email address. The professor sends the invitation from their own email.

### S7 · Student view

Students see only **approved** items for each lecture, in rank order, with the use label ("before class", "after class"…) and the clip timestamps. They never see scores, warnings, removed items or speaker candidates.

### S8 · Feedback and link health

- **Ratings:** after a lecture, students or the professor rate approved items 1–5 with a comment. They are saved to `feedback.yaml` and applied with `record_feedback` (§6.5); average ratings per source adjust future rankings.
- **Link health:** a weekly job (`health`) re-checks approved links. Show an alert on the lecture: "Video X is no longer available. Replace with the next item?" (the reserve has candidates).

---

## 4. What each choice runs (routing table)

| Choice | Runs | Input | Output the UI reads |
|---|---|---|---|
| `own_material` | nothing | — | — |
| `attach_material` | B's processor (**Parth to define the call**) | `attachments`, `attach_tasks`, the lecture brief | B's output (slides / summary / quiz / gap report) |
| `generate_material` | B's generator (**Parth to define the call**) | the lecture brief (`briefs.json`) and, if available, C's **approved** resources as references | B's slides and notes |
| `assistance` | C: `pipeline.recommend(run_id, [lecture_id])` | `survey.yaml` (`want_*`, note) | `lectures/<id>.json → resources` |
| `guest_lecture` | C: the same `pipeline.recommend` call (it does both when both are asked) | `survey.yaml` | `lectures/<id>.json → experts`, `guest_kits/<id>.md` |

The helper `survey.tasks(survey)` returns exactly this split per lecture:

```python
{"W01.L1": {"choices": ["own_material", "assistance", "guest_lecture"],
            "attachments": [], "attach_tasks": [],
            "resources": ["videos", "readings"], "guest": True,
            "confidence": 2, "note": ""}}
```

Use it to decide which jobs to start; B can read `choices`, `attachments` and `attach_tasks` from it too.

---

## 5. How the UI should talk to the backend

Today C runs from the command line and reads and writes files under `runs/<id>/delivery/`. That is enough for a first UI. Recommended setup:

1. **A thin Python API layer** (FastAPI or Flask, Amit's choice) that imports `profsagent.delivery` and exposes the endpoints below. Everything is plain Python and JSON; there is no other server to run.
2. **Long jobs** (recommend, generate) run in a background worker or thread. The UI polls a status endpoint, which can read `delivery.log` and file timestamps.
3. **Files are the source of truth** for now. The same records are also written to Neo4j (§7) if the UI prefers querying the graph.

| Endpoint (suggested) | Backend call | Notes |
|---|---|---|
| `GET /runs` | list `runs/*/state.json` | course name in `state["cco_compact"]["course_name"]` |
| `POST /runs/{id}/briefs` | `pipeline.make_briefs(id)` | fast; no AI |
| `GET /runs/{id}/briefs` | read `delivery/briefs.json` | list of lecture briefs |
| `GET /runs/{id}/survey` | `survey.load(id)` (or `survey.init(id, briefs)` if missing) | |
| `PUT /runs/{id}/survey/{lecture}` | load → update that lecture's answers → `survey.save(id, s)` | validate `yes`/`no` values |
| `GET /runs/{id}/tasks` | `survey.tasks(survey.load(id))` | routing per lecture |
| `POST /runs/{id}/recommend` body `{lectures:[...], refresh:bool}` | `pipeline.recommend(id, lectures, refresh)` | background job; 1.5–3 min per lecture |
| `GET /runs/{id}/lectures/{lecture}` | read `delivery/lectures/<lecture>.json` | resources + experts |
| `GET /runs/{id}/guest-kit/{lecture}` | read `delivery/guest_kits/<lecture>.md` | render the markdown |
| `POST /runs/{id}/review` | write rows into `delivery/review.yaml` → `review.apply(id)` | returns counts + refused rows (missing reason) |
| `POST /runs/{id}/feedback` | write `delivery/feedback.yaml` → `review.record_feedback(id)` | |
| `POST /runs/{id}/health` | `review.health(id)` | dead approved links + reserve suggestions |
| `POST /runs/{id}/graph` | `graph.write(id)` | refresh Neo4j delivery records |
| `GET /runs/{id}/report` | read `delivery/report.md` | a whole-course printable summary |

The CLI equivalents, useful for testing the UI against real data:

```
python scripts/run_delivery.py briefs    --run-id cs601-02
python scripts/run_delivery.py survey    --run-id cs601-02 --init        # write the choices file (keeps old answers)
python scripts/run_delivery.py survey    --run-id cs601-02 --ask         # answer in the terminal
python scripts/run_delivery.py recommend --run-id cs601-02 --lectures W01.L1,W01.L2 [--refresh]
python scripts/run_delivery.py review    --run-id cs601-02 --apply
python scripts/run_delivery.py feedback  --run-id cs601-02
python scripts/run_delivery.py health    --run-id cs601-02
python scripts/run_delivery.py graph     --run-id cs601-02
```

---

## 6. Data contracts (files the UI reads and writes)

All under `runs/<run_id>/delivery/`.

### 6.1 `briefs.json` (read)

A list with one object per lecture:

```
lecture_id, week, slot, hours, topic_id, topic, module, continues,
learning_outcomes[{id, statement, bloom_level, co}], course_outcomes[{id, statement}],
builds_on[{topic, week}], prerequisite_courses[{course, kind, relied_topics[]}], leads_to[{topic, week}],
assessed_in[{id, type, due_week}], labs[{week, title, tools[]}], hands_on, outside_load_hours,
novel, iiitd_match{topic, similarity}, summary, targets[...internal...]
```

### 6.2 `survey.yaml` (read + write; one block per lecture)

```yaml
lectures:
  W01.L1:
    topic: Developer workflows and AI-assisted coding
    week: 1
    new_at_iiitd: true
    summary: "A 2-hour lecture in week 1 on …"     # copy of the brief summary, for reading only
    own_material: 'yes'          # yes / no / null (= not answered)
    attach_material: 'no'
    generate_material: 'no'
    assistance: 'yes'
    guest_lecture: 'yes'
    attachments: []              # file paths or URLs, when attach_material is yes
    attach_tasks: []             # any of slides, summary, quiz, gap_check, enrich
    want_videos: 'yes'           # the five want_* apply only when assistance is yes
    want_readings: 'yes'
    want_practice: 'no'
    want_recorded_lecture: 'no'
    want_clips: 'no'
    confidence: 2                # 1–5
    note: ''
```

- `null` (`~`) means "not answered". A lecture with no `yes` choice gets nothing.
- Old answer files (with `teach_myself` / `want_guest`) are converted automatically.

### 6.3 `lectures/<lecture_id>.json` (read)

```
lecture_id, topic, generated_at, [continuation_of],
resources: { want, items{video|recorded_lecture|reading|practice: [card]}, reserve{…}, rejected[{title,url,why[]}],
             clips[{target, video, source, url, start, end, minutes}], counts{candidates, passed_checks, rejected} },
experts:   { experts[card], reserve[card], rejected[{name, why[]}], counts{candidates, assessed, passed_checks} }
           or { same_as: "<lecture_id>" }
```

Card fields are listed in §3 (S4). Every card has `findings[]` = `{code, severity, message}`. Show `warning`s; `error`s never reach `items`.

### 6.4 `review.yaml` (write, then apply)

```yaml
lectures:
  W01.L1:
    video:                       # also reading, practice, recorded_lecture, experts
    - key: https://www.youtube.com/watch?v=wlpBCazAY9Q    # the item's url (for experts: the name)
      rank: 1
      title: AI-Assisted Coding Tutorial …
      decision: approve          # pending | approve | replace | reject
      reason: ''                 # required for replace / reject
```

The backend keeps this file in sync with the latest results; the UI only changes `decision` and `reason`. `review.apply(run_id)` returns `{approved, rejected, replaced, pending, refused[]}`.

### 6.5 `feedback.yaml` (write)

```yaml
lectures:
  W01.L1:
  - key: <item url>
    title: …
    rating: 4        # 1–5
    comment: ''
```

---

## 7. Neo4j (optional for the UI)

`graph.write(run_id)` stores C's records next to the Phase 1 design graph, each linked to its lecture node:

```
(:Delivery:LectureBrief)-[:BRIEF_OF]->(:D_Lecture)
(:Delivery:CoverageDecision {choices, resources, guest, attachments, attach_tasks, confidence, note})-[:DECISION_FOR]->(:D_Lecture)
(:Delivery:Recommendation {kind, title, url, rank, total, status, rationale, use_as, …})  → lecture
(:Delivery:Expert {name, role, affiliation, links, verified_identity, …})                 → lecture
(:Delivery:Evidence)                                                                    → expert
```

This is handy for a course-level dashboard ("how many lectures still need a decision", "which lectures have a guest shortlisted").

---

## 8. Rules the UI must keep

1. **Choices first, always.** No search or generation for a lecture until its choices are saved. The summary is shown before the choices.
2. **Several choices are allowed.** Never use radio buttons for the delivery choices.
3. **Reasons are required** for Replace and Reject.
4. **Never contact a speaker.** Copy-only invitation; no email fields.
5. **Always show warnings** (yellow) on cards; never hide them behind a click.
6. **Students see approved items only.**
7. **Free resources only.** C already filters out paid ones, so the UI needs no price display.
8. **Don't show internal ids** (`x3e2`, `r4`) or raw scores without labels.

---

## 9. States and edge cases to design for

| Situation | What the UI shows |
|---|---|
| Lecture not decided yet | "Choose how to deliver this lecture" + the summary; no results tabs |
| Job running | Progress row; the page stays usable |
| No item passed the checks for a kind | "No video passed the quality checks for this lecture." (rather than weak items) |
| Fewer than the maximum items | Normal: C shows fewer rather than weak ones (quality floor) |
| Continuation lecture | "Next-best items after W01.L2" note; guest list "same as W01.L2" |
| Daily quota reached (YouTube / AI) | "Search quota reached for today; try again tomorrow afternoon". YouTube resets at Pacific midnight: 12:30 pm IST in summer, 1:30 pm IST in winter |
| Approved link died | Health alert with a one-click Replace |
| Professor changes choices later | Start jobs only for the new or changed options (`refresh: true` for C); approve/reject decisions on unchanged items are kept |

---

## 10. Suggested build order for A

1. **S1 + S2 read-only:** list lectures, show summaries and details from `briefs.json`.
2. **S2 choices:** the multi-select form, writing `survey.yaml`; bulk "apply to week".
3. **S4 Resources and Guest tabs:** render cards from the existing CS-601 results (`runs/cs601-02/delivery/lectures/W01.L1.json`, `W01.L2.json`, `W02.L1.json` are real examples).
4. **S5 review actions** → `review.yaml` → `review.apply`.
5. **S3 background jobs** for `recommend`, with progress.
6. **S6 guest kit page**, then **S7 student view**.
7. **B integration** (attach / generate) once Parth's calls are fixed.
8. **S8 feedback + health alerts.**

**Questions for Amit / Parth to settle:**

- (a) The API framework.
- (b) B's call signature for `attach_material` and `generate_material`.
- (c) Where uploaded attachments are stored (suggested: `runs/<id>/delivery/attachments/<lecture_id>/`).
