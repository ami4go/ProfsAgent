# Prompts — index and conventions

Every LLM call in ProfsAgent uses exactly one file from this directory. The prompt file, its `version`,
the model, the rendered inputs and the raw output are all logged per call (`run_log.py`), and each
generated node records its `prompt_id` + `prompt_version`.

## Files
| ID | File | Stage | Model class | Temp |
|---|---|---|---|---|
| 00 | `00_common_rules.md` | prefix of every prompt | — | — |
| E1 | `extraction/E1_header_prereqs.md` | L0 | cheap | 0 |
| E2 | `extraction/E2_weekly_plan.md` | L0 | cheap | 0 |
| E3 | `extraction/E3_co_analysis.md` | L0 | cheap | 0 |
| E4 | `extraction/E4_assessment_resources.md` | L0 | cheap | 0 |
| E5 | `extraction/E5_topic_clusters.md` | L0 | strong | 0 |
| E6 | `extraction/E6_corpus_co_po.md` | L0 | strong | 0 |
| G1 | `generation/G1_intake_cco.md` | S1 | strong | 0 |
| G2 | `generation/G2_positioning.md` | S2 | strong | 0.2 |
| G3 | `generation/G3_constraints.md` | S3 | strong | 0 |
| G4 | `generation/G4_course_outcomes.md` | S4 | strong | 0.4 |
| G5 | `generation/G5_co_po_mapping.md` | S4 | strong | 0.2 |
| G6 | `generation/G6_learning_outcomes.md` | S4 | strong | 0.3 |
| G7 | `generation/G7_structure.md` | S5 | strong | 0.3 |
| G8 | `generation/G8_lab_tutorial.md` | S7 | strong | 0.4 |
| G9 | `generation/G9_assessment_blueprint.md` | S7 | strong | 0.3 |
| G10 | `generation/G10_resources.md` | S8 | strong | 0.2 |
| G11 | `generation/G11_narrative.md` | S9 | strong | 0.5 |
| R1 | `repair/R1_repair.md` | any | strong | 0 |

## Conventions
- **Front-matter** (YAML) declares `id`, `version`, `inputs`, `output_model`, and `validators_after`.
- **Template syntax**: Jinja2. `{{ var }}` is a rendered variable. `{% include %}` pulls in `00_common_rules.md`.
- **Inputs are JSON** blocks wrapped in `<context name="...">…</context>` tags. The model is told that anything
  inside `<context>` is data, not instructions (this protects against injection from scraped sheets).
- **Outputs are a single JSON object** validated by the Pydantic model named in `output_model`, called through
  `instructor`. On validation failure, retry once with the Pydantic error appended. After that, log it and raise.
- **No self-certification.** No prompt asks the model to state that its output passes checks. Prompts may ask for
  `concerns[]`: things the model is unsure about. Only validators decide PASS/FAIL (C2).
- **Versioning.** Any wording change bumps `version`. Prompt files are frozen (git tag) during experiments, the same
  rule as the Gem files.
- **Few-shot examples** use domains *other than* the course under design, so they can't leak target content, and
  they never come from the gold set.
