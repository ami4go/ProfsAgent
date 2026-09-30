# ProfsAgent — Institutional Knowledge Graph (Layer A)

## What Is This?

ProfsAgent is an AI-powered system that helps professors design university courses. This repository contains **Layer A** — the Institutional Knowledge Graph, which acts as the **"Memory"** of the university.

It maps out all existing IIIT-D courses, their weekly topics, course outcomes, prerequisites, and Bloom's Taxonomy levels into a queryable **Neo4j Graph Database**.

## Why Do We Need It?

1. **Overlap Detection** — Instantly detects if a proposed new course is too similar to an existing one.
2. **Hidden Dependencies (A → B → C)** — Maps transitive prerequisites across the entire curriculum.
3. **Historical Baselines** — Provides the validation engine with "normal standards" (e.g., 500-level courses should use advanced Bloom verbs like "Design", not basic ones like "Understand").

## Architecture Pipeline

```
Data Collection → AI Extraction → Enrichment → Topic Clustering → Neo4j Graph DB
```

| Step | Script | What It Does |
|------|--------|--------------|
| 1. Data Collection | `src/profsagent/ingest/crawl.py` | Crawls 475 course syllabi from IIIT-D's public portal |
| 2. Parsing | `src/profsagent/ingest/parse_sheet.py` | Parses raw CSV sheets into structured sections |
| 3. AI Extraction | `src/profsagent/ingest/extract.py` | Uses Gemini LLM to extract structured JSON from raw text |
| 4. Enrichment | `src/profsagent/ingest/enrich.py` | Tags Course Outcomes with Bloom's Taxonomy levels |
| 5. Topic Clustering | `src/profsagent/ingest/canonicalise.py` | Groups similar topics into canonical topic nodes |
| 6. Graph Loading | `src/profsagent/ingest/load.py` | Loads everything into Neo4j as a Knowledge Graph |

## Current Stats

- **983 Nodes** | **1,607 Relationships** | **32 Courses** (pilot batch)
- **550 raw topics** clustered into **512 canonical topic nodes**
- All Course Outcomes tagged with Bloom's Taxonomy levels

## Project Structure

```
ProfsAgent/
├── src/profsagent/
│   ├── ingest/           # All pipeline scripts
│   │   ├── crawl.py      # Step 1: Data collection
│   │   ├── parse_sheet.py# Step 2: CSV parsing
│   │   ├── extract.py    # Step 3: LLM extraction
│   │   ├── enrich.py     # Step 4: Bloom tagging
│   │   ├── canonicalise.py # Step 5: Topic clustering
│   │   └── load.py       # Step 6: Neo4j loading
│   └── models/
│       └── layer_a.py    # Pydantic data models
├── data/
│   ├── extracted/        # 32 structured course JSONs
│   ├── enriched/         # Bloom-tagged course JSONs
│   └── canonical/        # Topic mapping file
├── Institutional_KG/     # Architecture documentation
└── README.md
```

## How To Run

### Prerequisites
- Python 3.10+
- Neo4j Desktop (running locally on `bolt://localhost:7687`)
- A Gemini API key (for extraction step only)

### Setup
```bash
pip install google-genai instructor neo4j python-dotenv pydantic requests
```

### Run the Pipeline
```bash
# Step 1: Crawl course data
python src/profsagent/ingest/crawl.py

# Step 2: Extract with LLM
python src/profsagent/ingest/extract.py

# Step 3: Enrich with Bloom tags
python src/profsagent/ingest/enrich.py

# Step 4: Cluster topics
python src/profsagent/ingest/canonicalise.py

# Step 5: Load into Neo4j
python src/profsagent/ingest/load.py
```

### Sample Neo4j Queries
```cypher
-- See the full network
MATCH (n) RETURN n LIMIT 150

-- Deep dive into a specific course
MATCH path = (c:Course {code: 'AI 203'})-[*1..2]-() RETURN path

-- Find courses teaching a specific topic
MATCH (t:Topic {name: 'Introduction to Deep Learning'})<-[:COVERS]-(w)<-[:HAS_WEEK]-(c:Course)
RETURN t, w, c
```

## Current Limitations

1. **32/475 Courses Extracted** — Due to free-tier Gemini API rate limits. Pipeline scales to all 475 with a paid key.
2. **Deterministic Clustering** — Topic canonicalisation uses local string-matching instead of LLM-based semantic clustering.

## Team

- **Layer A (This Repo):** Institutional Knowledge Graph — Amit
- **Layer B:** Course Generation & Validation Agents
- **Evaluation:** Pipeline evaluation and testing
