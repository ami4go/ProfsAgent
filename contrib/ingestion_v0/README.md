# contrib/ingestion_v0: Layer A ingestion + evaluation harness (work in progress)

**Status: parked, not wired into the main package, and not runnable as delivered.**
This is a teammate contribution (from `profsagent.zip`), kept verbatim so the work isn't lost. It lives here
rather than in `src/profsagent/` because it defines its own `llm/client.py`, `models/`, `validate/` and package
`__init__` files, which would overwrite the working design pipeline.

## What's in it
| Path | What | State |
|---|---|---|
| `src/profsagent/ingest/pipeline.py` | Layer A batch ingestion: parse sheets → E1–E4 → enrich → canonicalise → validate → Neo4j → priors | **Does not run.** Imports 5 missing modules (below) |
| `src/profsagent/ingest/derived.py` | Course-overlap Jaccard + topic `PRECEDES` edges, Cypher sync to Neo4j | Needs the missing `canonicalize` module + `neo4j` driver |
| `src/profsagent/ingest/programmes.py` | Load programme JSON, write Institution/Programme/PEO/PO/PSO nodes to Neo4j | Runs once `config.settings` exists; see the data warning below |
| `src/profsagent/llm/extractors.py` | Deterministic E1–E4 extractors for plain-text sheets | **Does not run.** Needs missing `ingest.sheet_parser` and schema classes |
| `src/profsagent/validate/defect_injector.py` | 13 mutation operators in 5 categories (A Gem-audit, B arithmetic, C temporal, D traceability, E deliberate blind spots) | **Works.** Good basis for the C2 study |
| `src/profsagent/validate/deterministic.py` | Separate re-implementation of V4/V10/V11/V12/V19/V20/V21/VA-ORDER/VT-SIZE/T2 on its own schema | Runs, but see the issues below |
| `src/profsagent/validate/llm_reviewer.py` | "LLM reviewer" baseline for C2 | **Simulated.** Never calls a model |
| `src/profsagent/validate/ablation_study.py` | C1/C2/C3 ablations with Cohen's d | **Simulated.** Hand-coded degradations |
| `scripts/run_defect_benchmark.py`, `scripts/run_full_evaluation.py` | Benchmark and combined evaluation runners | Run only with a stand-in `config.settings` |
| `data/programmes/btech_cse.json` | Programme spec for Neo4j | **Not IIIT-D data.** See below |
| `tests/test_pipeline_and_derived.py` | Tests for ingestion + derived edges | Fail on import (missing modules) |

## Known issues (checked 2026-09-30)
1. **Missing modules.** These are imported but not included:
   - `profsagent.ingest.canonicalize`, `enrichment`, `neo4j_loader`, `priors`, `sheet_parser`
   - `profsagent.config.settings`
   - the schema classes `LabPlanItem`, `PrerequisiteItem`, `ResourceItem` and `ResourceType`

   `pipeline.py` also calls `DeterministicValidator(enricher)` and `validate_course(..., held_out_codes=...)`, which that class doesn't accept.
2. **The C2 baseline is simulated.** `LLMReviewer.review_course_state` never calls an LLM (the configured-key branch is
   `pass`). It runs hand-written rules designed to miss arithmetic and temporal defects, so "validators beat the LLM
   reviewer" holds by construction. **Its numbers must not be reported as an experimental result.**
3. **The ablations are simulated.** "No-KG" overwrites conditions and degrees with fixed generic text, and "No-Scheduler"
   reverses weeks and adds 40% to hours. Real ablations must re-run the pipeline with the component switched off
   (`scripts/run_design.py` already records per-stage traces).
4. **The benchmark's recall is inflated.**
   - A mutation counts as "caught" if *any* violation fires, not the rule it targets.
   - `convert_state_to_parsed_course` drops every CO's condition and degree, so V11 fires on every course.
   - Measured with a stand-in config: **validators flag 100% of the clean base courses** (false-positive rate 100%).
     The reported 84.6% "recall" therefore carries no information.
5. **The base courses aren't real IIIT-D sheets.** The four "clean IIIT-D base courses" are hand-written (14-week plans,
   invented COs and weights). For example, the real CSE201 has 5 COs and 30% end-sem, per `eval/reference/cse201_sheet.tsv`.
6. **Wrong institutional constants.**
   - `LECTURE_HOURS_BUDGET = {3: 39, 4: 52}`. IIIT-D UG Regulations §4 give a 4-credit course 3 h × 13 weeks = **39**
     lecture hours, and courses are 4, 2 or 1 credit.
   - The comment "3–6 COs per IIIT-D regulation" cites no source; the regulations don't specify a CO count.
7. **`btech_cse.json` is not IIIT-D's programme data.**
   - It holds the generic NBA template POs ("Engineering Knowledge", …), four invented PEOs, two PSOs and an
     "NBA Tier-1" label, with no source.
   - IIIT-D's actual B.Tech CSE objectives are in `data/programmes/btech_cse.yaml`, copied word for word from the
     regulations PDF. Use that file.

## To make it usable (suggested order)
1. Add the missing ingestion modules and a real `config.settings`, or rebase onto `src/profsagent/config.py`.
2. Replace `btech_cse.json` with a conversion of `data/programmes/btech_cse.yaml`.
3. Port `defect_injector.py` to the design pipeline's `state.json` shape, and score it against `src/profsagent/validate/rules.py`.
   Count a detection only when the **expected** rule fires, and report the false-positive rate on real clean courses.
4. Implement `LLMReviewer` with a real model call through `src/profsagent/llm/client.py`, using a different model family
   from the generator.
5. Implement the ablations as real pipeline runs (KG stub off, repair loop off, scheduler off), n ≥ 3 per condition.
