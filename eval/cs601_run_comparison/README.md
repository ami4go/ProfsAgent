# CS-601 "Software Development using AI": run cs601-kg-02 and comparison with earlier methods

Run on 28 Oct 2026, 00:23:45 → 02:11:53 IST (1 h 48 min). Command:
`python scripts/run_design.py --input eval/inputs/CS-601.yaml --run-id cs601-kg-02 --auto-approve --no-research`
with `PROFSAGENT_STRONG_ONLY=1` (no lite or local models), `KG_BACKEND=neo4j`, and an empty AI cache (every call fresh).

Files in this folder: `cs601-kg-02_run.log` (the complete run log), `metrics.json` (every number below, per run).
The design itself is in `runs/cs601-kg-02/` (proposal.md, proposal.csv, course_template.xlsx, workload.md,
validation_report.json, evaluation_deterministic.json, llm_calls.jsonl).

## Result in one line

**0 errors, 18 warnings, Tier 1 verdict REVIEW** (not FAIL). Every one of the 13 AI calls went to a strong model
(gemini-3.5 / 3.7 / 3.8-flash). The earlier Neo4j run (cs601-kg-01), which ran on the lite model, had **58 errors** and
FAILED.

## 1. The four CS-601 runs side by side

Older runs were made with older validators, so every run was re-checked with **today's rules** (same code for all four,
no AI calls). "Errors at the time" is what that run's own log reported.

| | cs601-01 (30 Sep) | cs601-02 (15 Oct) | cs601-kg-01 (26 Oct) | **cs601-kg-02 (28 Oct)** |
|---|---|---|---|---|
| Method | first pipeline, Groq + Gemini | re-run, mostly cached answers | Neo4j KG, quota ran out | **Neo4j KG, strong models only, fresh** |
| AI calls (successful) | 24 | 34 (26 from cache) | 21 (2 from cache) | **13** |
| Models that answered | 18 lite, 5 gpt-oss-120b, 1 qwen | 21 lite, 9 gemini-2.5-flash, 3 gpt-oss, 1 3.7-flash | 19 lite, 2 3.8-flash | **9× 3.5-flash, 3× 3.7-flash, 1× 3.8-flash** |
| Tokens in / out | 124k / 31k | 32k / 35k | 134k / 38k | **77k / 82k** |
| Wall time | 3 min | 12 min (cached) | 3 min | **108 min** (≈90 min of it waiting on busy servers) |
| Errors at the time | 0 | 4 | 58 | **0** |
| **Errors with today's rules** | 1 (VA-PROCTOR) | 6 (4× V23, 2× VT-TEMPLATE) | 58 (58× V23) | **0** |
| Warnings with today's rules | 11 | 60 | 132 | **18** |
| Tier 1 verdict (today) | FAIL | FAIL | FAIL | **REVIEW** |
| COs / LOs / modules / topics | 5 / 11 / 6 / 16 | 4 / 12 / 8 / 16 | 4 / 10 / 4 / 12 | **5 / 15 / 5 / 15** |
| CO–PO links | 8 (one programme only) | 60 | **143** (everything mapped to everything) | **20** |
| PO coverage (B.Tech CSE) | n/a | 80% | 100% (over-mapped) | **60%** |
| Lecture hours used | 35 / 39 | 36.5 / 39 | 36 / 39 | **39 / 39** |
| Proctored share (needs ≥ 40%) | **30% (fails)** | 60% | 55% | **55%** |
| Student outside-class load (target 10–12 h/wk) | not computed | 10.7 h | 10.1 h | **11.1 h** |
| Resources verified | 5 / 5 | 6 / 6 | 8 / 8 | **7 / 7** (1 rejected: no library record) |
| CO length (words, median) | 22 | 22.5 | 22.5 | **35** (each CO has condition + measurable degree) |
| Loaded into Neo4j | no (no Neo4j then) | yes | yes | **not yet** (Neo4j was stopped at 02:11; load pending) |

What the numbers say:

- **The lite model was the problem, not the pipeline.** cs601-kg-01 mapped every CO to almost every programme outcome
  (143 links, 100% "coverage"), and the rules caught it: 58× V23, "CO→PO claimed but no assessed activity
  evidences it". With strong models the same pipeline made 20 links, every one backed by an assessed activity: 0 errors.
- **The rules catch real problems in older runs too.** cs601-01 put only 30% of marks on invigilated work (the
  regulation asks for at least 40%). cs601-02 still had the `{n} of {m}` template holes that the LLM-only check found
  and that became rule VT-TEMPLATE.
- **Quality went up, not just the error count.** The new run has more LOs (15, three per CO), uses the whole 39-hour
  budget, hits the outside-class load target, and every CO states a condition and a measurable degree (e.g. "at least
  80% of generated code modules satisfy all specified unit tests").
- **The cost is time.** Strong models were busy at night (503s and 3-minute timeouts), so the run waited about 90 minutes
  in total; G9 alone waited 60 min. Fewer calls (13 vs 21–34) because nothing had to be repaired.

## 2. Validation methods compared (same 23 planted defects in one CS-601 design)

From `eval/compare_validation/` (21–22 Oct; manual audit in `audit_llm_detections.md`).

| Method | Defects caught (of 23) | AI calls | Time | Same answer twice? |
|---|---|---|---|---|
| **Our hybrid: rules + KG checks (+ LLM only for meaning)** | **23** | 0 for the rules | ≈ 5 ms | yes, always |
| Hard rules alone (the subset kept in the LLM profile) | 19 | 0 | ms | yes |
| LLM-only, round 1 (as errors, right reason) | **4** (7 if right item but wrong reason; auto-score 10 was overstated) | 1 per stage | minutes | 44% overlap between repeats |
| LLM-only, round 1 (counting warnings) | 5 | | | |
| LLM-only, round 2 (4 defects, 3.1-flash-lite) | 1 of 4 as errors, 2 of 4 noticed | 5 | 8–401 s per call, ≈16.4k prompt tokens each | |

The LLM did find two real things the rules had missed: the `{n} of {m}` placeholders (now rule VT-TEMPLATE, which
re-checking shows in cs601-02) and a live demo assessed only by a written end-sem. That is why the LLM stays in the
design as a **meaning reviewer**, not as the validator.

## 3. Generation methods compared (how the design itself was made)

| | LLM alone writes the course | Our pipeline (cs601-kg-02) |
|---|---|---|
| Who checks it | nobody, or the same LLM | rule validators after every AI step (G1–G11), plus KG checks |
| Errors in the CO–PO map with a weak model | not visible | caught: 58× V23 in cs601-kg-01 |
| Uses IIIT-D data | no | yes: 93 level-3 courses set the norms (CO count, Bloom, components); closest course CSE701 (overlap 0.077) |
| Repeatable | no | rules and KG checks are deterministic; AI answers are cached per run |
| Professor control | edit the text afterwards | 3 approval gates (auto-approved in this dev run) |

## 4. The design produced (cs601-kg-02)

**Course outcomes** (Bloom band 3–5; 60% at level 4+, needs ≥ 50%):

| CO | Bloom | Statement |
|---|---|---|
| CO1 | 3 | Configure AI coding agent environments and context resources, given a multi-component software specification and Model Context Protocol (MCP) tool definitions, such that all required tool invocations and context retrievals complete without protocol errors. |
| CO2 | 3 | Construct executable software specifications and test-driven prompt context from ambiguous functional software requirements, using structured spec-driven development methods, such that at least 80% of generated code modules satisfy all specified unit tests on first synthesis. |
| CO3 | 4 | Diagnose failure modes and context drift in human-agent iterative development loops, given execution traces and interaction logs from an automated AI software factory workflow, identifying at least three distinct root causes of sub-optimal code generation with supporting log evidence. |
| CO4 | 4 | Analyse automated testing and verification pipelines for agent-generated software components, using synthetic defect insertion and automated regression suites in a continuous integration environment, determining code coverage gaps and identifying at least 90% of introduced functional defects. |
| CO5 | 5 | Evaluate the reliability and maintainability of AI-assisted software projects across multi-turn human-agent collaborative workflows using standardized software quality benchmarks, justifying each architectural refactoring recommendation against quantitative reliability and maintainability metrics. |

**Modules:** M1 Agent Workspace & Model Context Protocol · M2 Specification-Driven Development & Prompt Harnesses ·
M3 Agentic Loops & Context Diagnostics · M4 Automated Testing & Continuous Verification Pipelines ·
M5 Code Quality, Refactoring & Project Maintenance. 13 weeks, 13 labs, 13 tutorials, schedule feasible (39 h / 39 h).

**Assessment:** quiz 10% · assignment 20% · mid-sem 20% · project 25% · end-sem 25% (proctored 55%).

**Resources (all verified against a library record):** ChatDev: Communicative Agents for Software Development (2024) ·
Test-Driven Development (2002) · Introduction to Software Testing (2017) · Software Engineering at Google (2020) ·
Refactoring (1999) · Evaluating the Effectiveness of LLMs in Fixing Maintainability Issues in Real-World Projects
(2025) · The SWE-Bench Illusion (2026). Rejected: OpenAI MCP / Agent2Agent protocol docs (no library record).

**Constraints:** 17 (8 from the professor's text), 16 checked, 11 hard, 100% of hard constraints satisfied, 0 conflicts.
K17 ("assessment should emphasise applying modern AI-assisted practice") has no automatic check; confirm by hand.

**Knowledge-graph facts:** links to IIIT-D topics kept 0 of 15 (the course is new, nothing similar enough at 0.66);
0 topic-order pairs from IIIT-D weekly plans; closest course CSE701 "Topics in SE: AI in SE" (weighted Jaccard 0.077,
shared: requirements engineering, defect detection); norms from 93 level-3 courses.

## 5. All 18 warnings (none blocks the design)

| Code | Count | What it says | Action |
|---|---|---|---|
| V11 | 11 | an LO's condition (or one degree) is in a separate field but not visible in the sentence | rephrase LO text, optional |
| VB | 4 | claimed Bloom level differs from the verb's lexicon level (CO2.LO2 "formulate" L3 vs L6; CO3.LO1 "categorise" L2 vs L4; CO5.LO1 "measure" L3 vs L5; CO5.LO2 "formulate" L4 vs L6) | professor decides |
| VK-UNENFORCED | 1 | K17 cannot be checked automatically | confirm by hand |
| VA-PROJ | 1 | project released in week 8 of 13 | fine for a 25% project, or move earlier |
| V15 | 1 | 1 resource removed (MCP / A2A docs have no library record) | add manually if wanted |

## 6. AI calls, in order

| Step | Prompt | Model that answered | Tokens in+out | Time |
|---|---|---|---|---|
| S1 intake | G1 | gemini-3.7-flash | 3,431 + 6,432 | 423 s |
| S2 positioning | G2 | gemini-3.8-flash | 10,798 + 6,005 | 142 s |
| S3 constraints | G3 | gemini-3.5-flash | 3,017 + 3,672 | 481 s |
| S4 COs | G4 | gemini-3.5-flash | 9,446 + 3,990 | 29 s |
| S4 CO–PO | G5 | gemini-3.5-flash | 5,332 + 6,420 | 39 s |
| S4 LOs | G6 | gemini-3.5-flash | 6,423 + 10,583 | 184 s |
| S5 structure | G7 | gemini-3.5-flash | 7,923 + 7,603 | 904 s |
| S7 labs/tutorials | G8 | gemini-3.5-flash | 4,548 + 9,470 | 46 s |
| S7 assessment | G9 | gemini-3.5-flash | 9,241 + 9,516 | 3,597 s |
| S8 resource queries | X3 | gemini-3.7-flash | 1,736 + 1,176 | 93 s |
| S8 resources | G10 | gemini-3.7-flash | 6,468 + 11,900 | 316 s |
| S8 replacement | G10 | gemini-3.5-flash | 5,043 + 3,048 | 27 s |
| S9 narrative | G11 | gemini-3.5-flash | 3,267 + 2,675 | 144 s |

Long times are waits for a free strong model (503 "busy" and 180 s timeouts), not long answers. No call fell back to a
lite model.

## 7. Caveats

- `--no-research` was used (no external university search), as in cs601-kg-01, so both KG runs are comparable; cs601-01
  and cs601-02 did use external research.
- cs601-02 reused 26 cached answers from earlier runs, so it is partly a replay.
- Gates were auto-approved (dev run). A real run stops for the professor at gates 1–3.
- Neo4j was stopped when the run ended, so the design is not in the graph yet. Load it with
  `python scripts/load_design_to_neo4j.py --run-id cs601-kg-02` once Neo4j is running.
