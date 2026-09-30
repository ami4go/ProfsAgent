# ProfsAgent — AI-Assisted Curricular Design

Course-design system for IIIT-Delhi. This repository contains both halves of the architecture:

**Layer A (The Institutional Knowledge Graph):** Built by the KG teammate. It crawls existing IIIT-D courses, extracts structured JSON using Gemini LLM, enriches them with Bloom's Taxonomy tags, canonicalises topics, and loads everything into a Neo4j Graph Database to act as the institutional "Memory".
Code: `src/profsagent/ingest/`

**Layer B (The Course Design Pipeline):** Built by Vihan. The agentic pipeline that takes professor input → curriculum positioning (internal KG + external research at top universities) → constraints → COs / CO–PO / LOs → structure → schedule → labs & assessment → resources → rendered proposal. It handles the LangGraph pipeline, RAG, prompts, validators, and evaluation.
Code: `src/profsagent/agents/`, `src/profsagent/validate/`, `src/profsagent/rag/`, etc.

Design docs: `docs/01_stage1_architecture.md`, `Institutional_KG/01_stage1_architecture.md`. Prompts: `prompts/README.md`.

## Run
```bash
pip install langgraph langgraph-checkpoint-sqlite beautifulsoup4 httpx pydantic jinja2 pyyaml numpy pytest neo4j python-dotenv
# .env (git-ignored): GEMINI_API_KEYS=k1,k2,k3   GROQ_API_KEYS=k1   NEO4J_PASSWORD=password

# --- LAYER A: Build the Knowledge Graph ---
python src/profsagent/ingest/extract.py     # Extracts JSON from course sheets
python src/profsagent/ingest/enrich.py      # Tags Bloom's Verbs
python src/profsagent/ingest/canonicalise.py # Clusters topics
python src/profsagent/ingest/load.py        # Pushes everything to local Neo4j

# --- LAYER B: Run the Design Pipeline ---
python scripts/build_stub_kg.py --no-fetch                  # (re)parse the stub courses
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
- `proposal.md` / `proposal.csv`: the IIIT-D course-directory form plus appendices
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

## Test courses
- **Dev (tuning allowed):** CSE201 Advanced Programming. Its own sheet is excluded from the KG and RAG, and IIIT-D domains are blocklisted for research.
- **Final (no tuning):** Stanford CS146S (themodernsoftware.dev). Blocklist that domain and course code in the run config. Do not tune prompts on it.
