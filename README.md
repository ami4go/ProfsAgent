# ProfsAgent — AI-Assisted Curricular Design

Course-design system for IIIT-Delhi. This repository contains both halves of the architecture:

**Layer A (The Institutional Knowledge Graph):** Built by the KG teammate. It crawls existing IIIT-D courses, extracts structured JSON using Gemini LLM, enriches them with Bloom's Taxonomy tags, canonicalises topics, and loads everything into a Neo4j Graph Database to act as the institutional "Memory".
Code: `src/profsagent/ingest/`

**Layer B (The Course Design Pipeline):** Built by Vihan. The agentic pipeline that takes professor input → curriculum positioning (internal KG + external research at top universities) → constraints → COs / CO–PO / LOs → structure → schedule → labs & assessment → resources → rendered proposal. It handles the LangGraph pipeline, RAG, prompts, validators, and evaluation.
Code: `src/profsagent/agents/`, `src/profsagent/validate/`, `src/profsagent/rag/`, etc.

Design docs: `docs/01_stage1_architecture.md`. Prompts: `prompts/README.md`.

## Run
```bash
pip install ddgs python-pptx langgraph langgraph-checkpoint-sqlite beautifulsoup4 httpx pydantic jinja2 pyyaml numpy pytest neo4j python-dotenv sentence-transformers openpyxl reportlab youtube-transcript-api
# .env (git-ignored): GEMINI_API_KEYS=k1,k2,k3   GROQ_API_KEYS=k1   NEO4J_PASSWORD=password

# --- LAYER A: Build the Knowledge Graph ---
python src/profsagent/ingest/extract.py     # Extracts JSON from course sheets
python src/profsagent/ingest/enrich.py      # Tags Bloom's Verbs
python src/profsagent/ingest/canonicalise.py # Clusters topics
python src/profsagent/ingest/load.py        # Pushes everything to local Neo4j

# --- LAYER B: Run the Design Pipeline ---
# Runs read the Neo4j graph above by default (start Neo4j first); KG_BACKEND=stub uses the 17-course stub instead
python scripts/build_stub_kg.py --no-fetch                  # (re)parse the stub courses (KG_BACKEND=stub only)
python scripts/run_design.py --input eval/inputs/cse201_P2.yaml --run-id cse201-dev-01 --auto-approve
python scripts/evaluate_run.py --run-id cse201-dev-01 --reference eval/reference/cse201_sheet.tsv
python -m pytest -q tests
```
Without `--auto-approve` the run stops at each professor gate. Answer a gate with
`--resume --decision approve|reject --by "<name>"`.

Continue a run that stopped on an error (quota, network) from its last checkpoint:
`python scripts/run_design.py --run-id <id> --continue`. Ollama must be running (`ollama serve`) for the local fallback.

**Quota reality (free tier, measured):** Gemini allows 20 requests/day per model per *project*, and keys from one project share it.
A full run takes about 20–40 calls, so keep the cache on while developing and spread keys across projects.

Outputs in `runs/<run-id>/`:
- `course_template.xlsx`: **the official IIIT-D CSE course description template, filled** (see below)
- `proposal.md` / `proposal.csv`: the full proposal with appendices
- `state.json`: the full design state
- `design_graph.json`: Layer B nodes and edges with provenance
- `llm_calls.jsonl`: every prompt, output, endpoint, tokens and fallback attempt
- `run.log`
- `evaluation.json`

## Code map
| Path | What |
|---|---|
| `llm/client.py` | fallback chain Gemini 3.8/3.7/3.5/2.5-flash (3 keys) → Groq gpt-oss-120b → Gemini flash-lite ×3 → Groq qwen3.8 → **local Ollama gemma4 / qwen3.5** (CPU, minutes per call). 503 cools the model on all keys; daily 429 cools until Pacific midnight; 413 / truncated JSON moves on; dev response cache; grounded search; embeddings |
| `llm/prompts.py` | prompt loader (front-matter, `## SYSTEM`/`## USER`, Jinja2, `{% include %}` of common rules) |
| `models/io.py` | Pydantic output model for every prompt |
| `kg/client.py` | **KGClient contract with the KG teammate** |
| `kg/stub.py`, `kg/sheet_parser.py`, `kg/quality.py` | stub Layer A, sheet parser, Bloom lexicon tagging + CO quality score |
| `rag/index.py` | hybrid BM25 + dense retrieval (RRF) with course exclusion |
| `research/external.py` | comparable-course search: X1 plan → Google-Search grounding (whitelisted domains) + Stanford ExploreCourses + NUSMods → fetch → X2 page classification → evidence-quote check; blocklists for held-out tests |
| `research/resources.py` | OpenLibrary / Crossref candidates + deterministic verification (V15) |
| `design/store.py` | Layer B graph (uid, version, status, provenance; frozen nodes immutable) |
| `design/deterministic.py` | regulation defaults, hours budget, scheduler with infeasibility explanation, computed CO–PO strengths |
| `validate/rules.py` | validators V1–V23 + T-rules. **No LLM** |
| `agents/loop.py` | generate → validate → bounded, monotone R1 repair |
| `agents/pipeline.py` | stages S1–S9 and gates |
| `orchestrator/graph.py` | LangGraph state machine, SQLite checkpoints, `interrupt()` gates |
| `render/proposal.py` | deterministic rendering (no LLM) |

## IIIT-D CSE course description template
The official template is stored in `templates/iiitd_cse_course_template.xlsx` (sheets *Template* and *Taxonomy*). The pipeline follows it:
- **Programme outcomes** for CO mapping are the template's, word for word: B.Tech. (common) PO1–PO12, B.Tech. (CSE) PSO1–PSO5,
  B.Tech. (CSAI) PSO1–PSO6, M.Tech. (CSE) PO1–PO3 + PSO1–PSO10 (`data/programmes/*.yaml`). Every CO of a CSE course is mapped
  against all four programmes, each link with a strength (1–3) and a one-line explanation (template "CO-Explanation" column).
  The earlier regulation-based list is archived in `data/programmes/archive/`.
- **Rules from the template**, checked in code (`validate/rules.py`): 2–3 COs for a 2-credit and 4–5 for a 4-credit course (V4);
  at least half of the COs at BL4–BL6 (VCO-BL); a mapping for every CSE programme (T4); at least 40% proctored evaluation
  (VA-PROCTOR); 10–12 h/week of work outside lectures for 4 credits, per topic "Average load" (VT-LOAD, warning).
- **Verbs**: the template's Taxonomy sheet is kept verbatim in `data/bloom_lexicon.yaml` (`iiitd_taxonomy`) and its verbs are merged
  into the lexicon the CO checks use.
- **Output**: every run writes `course_template.xlsx`: the official workbook with its rows, the two "Do not remove or edit this row"
  markers, the Department drop-down and the Taxonomy sheet kept; dummy rows replaced by the course's COs, topics, labs,
  assessments and resources; one CO / CO-Explanation column pair per CO in the mapping block. `department:` in the run config
  sets Department / Proposing Dept (default CSE).

## The new course's graph in Neo4j
After the final approval gate, every run loads its design graph (`design_graph.json`, Layer B) into Neo4j next to the IIIT-D
graph (Layer A), if Neo4j is reachable (`design/neo4j_sync.py`). Design nodes have the labels `DesignNode` and `D_<type>`
(`D_CO`, `D_LO`, `D_CourseTopic`, `D_Assessment`, ...) and a `run_id`; a `(:DesignRun)` node holds the run summary.
Links leave the design to real nodes: `REQUIRES`/`OVERLAPS` → `(:Course)`, `SAME_AS` → `(:Topic)`, `MAPS_TO` →
`(:ProgrammeOutcome)` (the template's outcomes).
Each run gets a generated course code, the department prefix + a number from 1001 (CSE1001, CSE1002, ...; real IIIT-D codes
have 3 digits), kept in `runs/<id>/course_code.txt` and stored as `course_code` on every node of the run (`code` on the course node).
Every node has a readable `name` caption ("CSE1001 · <title>", "Week 3", "W3 Lecture 2", "CO2.LO1", "Quiz1 (W3)"), design nodes
carry the label `Generated` and the IIIT-D graph's nodes `Institutional`. The course node is the hub, as `(:Course)` is in Layer A:
`HAS_CO`, `HAS_MODULE`, `HAS_WEEK`, `HAS_ASSESSMENT`, `USES_RESOURCE`, … link it to every part. `--check` compares what is in Neo4j
with the run's files (every node and link) and checks the course is complete (every CO has LOs, every LO taught and assessed,
weeks 1..N, …); the automatic load after the final gate runs the same check and logs failures. Example:
```cypher
MATCH (c:D_NewCourse {code:'CSE1001'})-[r:REQUIRES|OVERLAPS|COMPARABLE_TO]->(k:Course)
WHERE type(r) <> 'OVERLAPS' OR r.weighted_jaccard > 0 RETURN c, r, k
```
S5 keeps a topic's `SAME_AS` link to an IIIT-D topic only if the KG also finds that topic close to the topic's own title.
`load.py --wipe` clears only the IIIT-D graph; design runs stay and their links are re-attached.
Load, check or remove a run by hand: `python scripts/load_design_to_neo4j.py --run-id <id> [--check | --delete]`.

## Validation (Phase 1 core)
Every generated part is checked before the next one is built: format guard → rule checks (university regulations and
course template, the professor's requirements, IIIT-D catalogue facts, consistency, outcome quality) → deterministic
fixers → R1 repair (kept only if errors drop; stops when it cannot help) → blocking gate (approving with open errors
needs a written reason).

- **One entry point:** `validate/engine.py` selects the profile (`configure`), runs a stage's checks (`check`), applies
  fixers and reports what stays open; the checks themselves live in `validate/rules.py` and its helpers.
- **Profile:** `config/validation.yaml` → `profile: core` (default: rules + IIIT-D graph checks; 23/23 planted defects,
  no AI calls). `full` (or `PROFSAGENT_VALIDATION=full`) adds meaning checks with the local embedding model; `llm` uses
  one LLM check per stage (4/23 when it was the only checker, `eval/compare_validation/`).
- **Course fit** (family `fit`, warnings the professor settles, never sent to R1): `VC-AUDIENCE` when the title names a
  broad audience ("for All", "101", …) but the level is 3+ ("Introduction to" is not such a word: most IIIT-D
  "Introduction to …" courses are level 5–6); `VC-NOLAB` when at least half the LOs are hands-on, P = 0 and the
  professor never said "no lab". Either sends the design to REVIEW.
- **Report:** gates and Appendix E show findings under plain headings with repeats merged into one line
  (`validate/report.py`); every individual finding is in `runs/<id>/validation_report.json`.

## Evaluation (tiers 1–3)
`evaluate/engine.py` evaluates every finished design (and `scripts/evaluate_design.py --run-id <id> --all-tiers` any
saved one). Each tier runs on its own, so one failing does not stop the others:

| Tier | What | Cost | File |
|---|---|---|---|
| 1 | completeness, alignment, constraints, regulation, workload, course fit → PASS / REVIEW / FAIL | none | `evaluation_deterministic.json` |
| 2 | the design against a real IIIT-D sheet (topics, COs, assessment, prerequisites, resources) when the run names `run.reference_course` or holds one out | local embeddings | `evaluation_reference.json` |
| 3 | LLM judge panel on G-Eval rubrics (`config/judging.yaml`); only **planned** (panel, call count) unless `run.judge: true` or `PROFSAGENT_JUDGE=1` | 0 calls by default | `evaluation_judges.json` |

`evaluation.json` holds every tier's summary and the overall verdict. Other tools: `scripts/evaluate_reference.py`
(tier 2 for any course), `scripts/judge_design.py` (tier 3 on its own), `scripts/audit_kg.py` (Layer A audit).

## Phase 2 · Deliverable C: learning resources and expert speakers
For an approved Phase 1 course run, per lecture (plan: `docs/03_phase2_C_learning_resources_and_experts_plan.md`):
1. **Lecture briefs** from the design (no AI): topic, learning outcomes, what students must already know, what depends on it,
   where it is assessed; ★ marks topics new to IIIT-D (no close match in the knowledge graph).
2. **Survey** (`runs/<id>/delivery/survey.yaml`): explicit questions per lecture — teach it yourself? lecture videos? readings
   (blogs, articles, chapters, docs)? practice? a full recorded lecture? clip playlists? a guest speaker? Nothing is searched
   for a lecture until one answer is yes.
3. **Learning resources** (free only): YouTube Data API, Gemini-grounded web search, OpenLibrary, OpenAlex surveys, GitHub;
   transcripts and page text are matched to the lecture's topic and LOs with local embeddings (coverage + timestamps),
   reviewed by AI (D2), scored on coverage · quality · authority · level · reception · practicality, checked in code,
   diversified and capped (3 videos, 2 readings, 1 practice), with a reserve for replacements and **clip playlists**.
4. **Expert speakers** (5–7, worldwide, research or industry): OpenAlex/DBLP/ORCID for academics (plus a Google Scholar search
   link — Scholar has no API), IIIT-D faculty of related courses, practitioners from grounded web search (confirmed on their
   own pages) and GitHub; ranked with evidence, AI fit check (D4), **guest-lecture kit** with an invitation draft the professor sends.
5. **Review** (`review.yaml`: approve / replace / reject + reason), feedback ratings that re-weight sources, link health checks,
   and Neo4j records linked to the course's lectures.
```bash
python scripts/run_delivery.py briefs    --run-id cs601-02
python scripts/run_delivery.py survey    --run-id cs601-02 --ask          # or --defaults for a test run
python scripts/run_delivery.py recommend --run-id cs601-02 --limit 3      # writes delivery/report.md + review.yaml
python scripts/run_delivery.py review    --run-id cs601-02 --apply
python scripts/run_delivery.py graph     --run-id cs601-02
```
Needs `YOUTUBE_API_KEY` and `OPENALEX_API_KEY` in `.env` (free). Tunables: `config/resources.yaml`, `config/experts.yaml`.
Transcripts are fetched locally (YouTube blocks cloud servers). Budget per lecture: ~300 YouTube units (of 10,000/day) and 3–5 AI calls.

## Phase 2 · Deliverable B: lecture slides and notes
For a lecture of an approved Phase 1 course run (`src/profsagent/content/`, settings `config/content.yaml`). This is
the survey's `generate_material` choice: `content.generate.generate_material(run_id, lecture_id, options)`.
1. **Inputs (no AI):** the lecture brief (topic, LOs, CO, prerequisites, where it is assessed) and the sources slides
   may cite: the course's verified Phase 1 resources (`C1…`) and C's resources for the lecture once approved (`L1…`).
2. **B1, one AI call:** the content slides (`content/models.LectureDeck`): concept, example, worked problem, activity,
   check (a multiple-choice question with answer and explanation) and summary slides, with speaker notes.
3. **Checks (no AI):** every LO served, Bloom 3+ LOs shown in use, slide count fits the hours, valid figures and
   questions, no unknown ids or `{placeholders}`, density, timing, one check per hour (`content/checks.py`); code
   snippets compiled for syntax (Python built in; C/C++ with gcc; Java with javac and JavaScript with node when
   installed, otherwise reported as not verified) and citations matched to the slide text with the local embedding model
   (`content/verify.py`). With errors, B1 is asked once more with the findings and the new deck is kept only if errors drop.
4. **Render:** code writes the title, objectives and references slides. `slides.pptx` is 16:9 with speaker notes, and
   flows, code and tables are drawn as editable shapes. Text is fitted to its box; text that still cannot fit is a
   `D-OVERFLOW` warning. Also written: `notes.md` (handout), `quiz.json`, `deck.json`, `material.json` (findings,
   sources, calls).
```bash
python scripts/run_content.py plan     --run-id cs601-02 --lectures W01.L1     # inputs and cost, no AI calls
python scripts/run_content.py generate --run-id cs601-02 --lectures W01.L1     # or --from-survey
python scripts/run_content.py check    --run-id cs601-02 --lectures W01.L1     # re-check and re-render, no AI calls
python scripts/run_content.py review   --run-id cs601-02 [--apply]             # professor: approve / redo / reject
python scripts/run_content.py generate --run-id cs601-02 --redo                # regenerate the decks sent back, with the reason
python scripts/run_content.py generate --run-id cs601-02 --lectures W01.L2 --auto-review   # a second AI model checks the deck
```
4b. **AI review, optional** (`--auto-review`, `content/ai_review.py`): for a professor who wants the system to check
   the slides. A model other than the writer reads every slide and notes (wrong facts, wrong code behaviour, ambiguous
   questions, unclear steps, level) and answers the quiz without the key. Its errors get one repair. The deck becomes
   `ai-reviewed`, not approved. Cost: 1–2 more calls per lecture.
5. **Professor review** (`content/review.py`): `material/review.yaml` lists every deck; `approve` freezes it (a new
   generation needs `--force`), `redo` regenerates it with the professor's reason as instructions, `reject` drops it.
   `material.json → status` is draft | ai-reviewed | approved | redo | rejected.
Output: `runs/<id>/delivery/material/<lecture>/`. Example: `eval/content_examples/cs601-02_W01.L1/`.

## Other scripts
- `scripts/export_course_template.py --run-id <id>`: (re)writes `runs/<id>/course_template.xlsx`.
- `scripts/load_design_to_neo4j.py --run-id <id> [--delete]`: loads (or removes) a run's design graph in Neo4j.
- `scripts/export_course_sheet_pdf.py --run-id <id>`: renders `runs/<id>/course_sheet.pdf` in the template's layout (plus a week-by-week annex).
- `scripts/run_defect_benchmark.py`: CS-601 mutation benchmark (see `BENCHMARK_FULL_REPORT.md`). A mutation counts as detected when
  *any* error survives, not the rule it targets, and there is no false-positive check on clean runs yet.

## Contributed: earlier ingestion + evaluation harness (parked)
`contrib/ingestion_v0/` holds an earlier teammate contribution, kept verbatim. **It is not wired into the main package and does not
run as delivered** (missing modules; its LLM-reviewer baseline and ablations are simulated; its benchmark flags 100% of clean
courses; its `btech_cse.json` has the B.Tech. common PO1–PO12 that the official template also uses, but its PEOs, PSOs and
"NBA Tier-1" label are unsourced: use `data/programmes/*.yaml`). Read `contrib/ingestion_v0/README.md`.
The defect injector is the part ready for reuse.

## Test courses
- **Dev (tuning allowed):** CSE201 Advanced Programming. Its own sheet is excluded from the KG and RAG, and IIIT-D domains are blocklisted for research.
- **Final (no tuning):** Stanford CS146S (themodernsoftware.dev). Blocklist that domain and course code in the run config. Do not tune prompts on it.
