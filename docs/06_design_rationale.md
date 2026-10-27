# ProfsAgent — Design Questions and Answers

Short, evidence-based answers to the design questions reviewers ask. Numbers come from this repository (saved runs,
the defect suite, the graph audit); where a number is still being measured, the section says so.

---

## 1. Why a knowledge graph instead of RAG?

**Short answer: not instead of. ProfsAgent uses both, for different jobs.** Retrieval (RAG) finds text that is
*similar*; the knowledge graph answers questions that need an *exact* answer, a count, or a chain of links.

| Job | Needs | Tool used | Where in the code |
|---|---|---|---|
| Find courses similar to the new one; find well-written example COs | "Text like this" | **RAG**: BM25 + embeddings, rank fusion | `rag/index.py`, `kg.search_courses`, `kg.exemplar_cos` |
| Is AI501 a 5xx course? Does CSE999 exist? | One exact fact | **Graph** | V14, V16, V17 |
| Typical CO count and assessment weights for level-3 courses | Aggregation over many courses | **Graph** | `kg.priors`, V20, VKG-NORM |
| Is a design topic the same as an IIIT-D topic? | Similarity + an identity | Embeddings over **graph** topics | `kg.topic_candidates`, the S5 `SAME_AS` check |
| Which books do similar courses use? | Links from courses to resources | **Graph** | `kg.corpus_resources` |
| CO → LO → topic → lecture → assessment for the new course | A chain of typed links | **Design graph** | `design/store.py`, T-rules, `neo4j_sync.check_run` |

**Why RAG alone is not enough:**
1. **Validation needs exact answers.** A check like "the prerequisite is not a higher level than the course" needs the
   level of one specific course, every time. RAG returns paragraphs ranked by similarity: the right fact may be missing,
   or the wrong course's sheet may rank first. The graph returns one answer, or none. The defect suite's invalid
   prerequisite (`NONEXISTENT101`) and the benchmark's real error (AI501, a 5xx course, listed for a 4xx course) are
   caught by graph lookups.
2. **Counts and averages are not retrievable.** "The median level-3 course has 4 COs" comes from aggregating 93
   courses, not from any single document.
3. **Identity matters.** 84 catalogue rows are cross-listed under several codes (e.g. AI501 / ECE363 / CSE343). The graph
   resolves every alias to one course; text chunks would treat them as different courses.
4. **Traceability is a graph by nature.** Each new course is a chain from programme outcomes down to assessments. The
   checks "every LO is taught and assessed" and "nothing is assessed before it is taught" follow links in that chain.
5. **Phases 2 and 3 attach to it.** Slides and videos attach to lectures and LOs; marks attach to assessments and,
   through them, to COs. CO attainment is computed by walking those links.

**What the graph costs, honestly:** it has to be built and kept correct. The audit (`scripts/audit_kg.py`) found 71 data
errors in 21 of 471 courses (mostly duplicate week numbers), and topic clustering is weak (90% of canonical topics occur
in one course), so topic matching still relies on embeddings. The design uses the graph where it is reliable (catalogue,
structure, numbers) and retrieval where text similarity is what matters.

---

## 2. Why build a separate graph for every new course?

- **Every item has an id, a source and a status** (draft, approved, frozen), so the proposal can always be traced back to
  why it says what it says, and approved parts cannot be changed by later repairs.
- **It connects the new course to the institution**: after approval it is loaded into Neo4j next to the 471 real
  courses (own course code CSE1001…, links to real prerequisites, topics and programme outcomes).
- **Phase 2 and 3 need it**: materials, feedback and marks attach to its lectures, LOs and assessments.
- **Today's limitation:** during Phase 1 the validators read the same content from the run state, not from this graph;
  the graph's own checks run after approval. Planned: prerequisite-topic and curriculum-level checks on the joined
  graphs before the final gate.

---

## 3. Why Neo4j?

A property graph with typed nodes and relationships, a query language for multi-hop questions (prerequisite chains,
"which courses cover this topic"), a free desktop edition, and a browser for showing the graph to professors. The
pipeline reads it once per run and keeps working without it: a stub graph (`KG_BACKEND=stub`) exists for development,
and publishing a design is skipped, not failed, when Neo4j is down.

---

## 4. Why an agent pipeline (stages S1–S9) instead of one big prompt?

- **Each stage is small enough to check.** COs are validated before LOs are written; LOs before topics; topics before
  assessment. A mistake is caught where it happens, not in a 20-page document.
- **Each stage has the right context.** The LO prompt sees the approved COs; the assessment prompt sees the schedule.
- **Repair is local.** A failing stage is repaired or regenerated alone.
- **The professor approves at three gates** (context, outcomes, proposal) instead of only at the end.
- **Numbers are never written by the model**: hours, schedule, CO–PO strengths and weights are computed in code
  (`design/deterministic.py`).

---

## 5. Why not validate everything with one LLM check?

This is the supervisor's question, and it is being measured rather than argued
(`scripts/compare_validation.py`, results in `eval/compare_validation/report.md`):

| Scheme | What it is |
|---|---|
| Rules (current) | Every check in code |
| LLM check alone | One LLM review of the whole design against a checklist |
| Hard rules + LLM check (new `llm` profile) | 38 exact rules in code + one LLM check per stage for the judgement items |

Measured on the 23 injected defects (21 Oct 2026; repeat 1 complete, repeat 2 cut short by the day's API quota):

| Scheme | Defects caught | Notes |
|---|---|---|
| All rules in code | **23/23** | Same answer every run, free |
| 38 hard rules only | **19/23** | Misses the four judgement defects: banned verbs, duplicate COs, two vague-degree variants |
| One LLM check alone | **10/23** as blocking errors (12/23 counting warnings) | Catches all four judgement defects; misses the exact ones: weights summing to 130%, a non-existent prerequisite, impossible hours, contradictory constraints, wrong week counts, an L-T-P with no lectures |
| Hard rules + LLM check | **23/23** (14/14 in the part of repeat 2 that ran) | Same coverage as all rules with 38 instead of 59 rules |

Further observations:
- **The LLM check found two real problems that all 59 rules miss**, on the design used as "clean": two LOs still
  contain unfilled template text ("for {n} of {m} short items"), and one LO that requires a live demonstration is
  assessed only by the written end-semester exam.
- **It is not stable in detail**: run twice on the same design, the sets of errors it reports overlap only 44% (Jaccard),
  although its catch / miss verdict per defect agreed in 13 of 14 cases.
- **Some defects are invisible to it**: a wrong number of schedule weeks changes nothing the check is shown.
- **Cost**: about 1–2 minutes per call on the free tier, and 48 calls exhausted the day's quota.

**Conclusion:** one LLM check alone catches about half the defects; it is valuable for the judgement items and finds
problems rules cannot express, while exact rules remain necessary for numbers, references, regulations and catalogue
facts. Hence the hybrid profile.

Why the hard rules stay in code whatever the result: an LLM cannot be guaranteed to add up weights correctly across a
long design, does not know IIIT-D's catalogue or regulations unless they are pasted in, can give a different answer on
each run (a blocking gate needs the same answer every time), tends to approve its own model family's output, and costs
an API call per check on a free tier of about 20 requests per model per day.

---

## 6. Why human gates?

The professor owns the course. Gates are where the professor confirms the context, freezes the outcomes and approves
the proposal. Since validation v2 a gate **blocks** while errors are open; approving anyway needs a written reason, which
is recorded. Automatic test runs record that the gate *would* have blocked.

---

## 7. Why Bloom's taxonomy and the PO / CO / LO structure?

It is what IIIT-D's course template and NBA / NAAC accreditation use: course outcomes with action verbs at a stated
cognitive level, mapped to programme outcomes, with CO–PO strength justified by assessment. Following that structure
makes the output usable by the institution as is, and makes much of it checkable (verb levels, counts, CO–PO evidence).

---

## 8. Why several models and a local embedding model?

- **Several models:** the Gemini free tier allows about 20 requests per model per day and the 3.x models are often
  overloaded; the client falls back through a list of models instead of failing the run.
- **A different model for checking than for generating** (the `check` and judge roles), to reduce a model approving its
  own output.
- **Local embeddings** (all-MiniLM-L6-v2): free, offline, no daily quota, and calibrated on this data (topic match
  threshold 0.66).

---

## 9. How is quality measured?

| Tier | What | Cost |
|---|---|---|
| Tier 1 | Deterministic score of a finished design: completeness, alignment, constraints, regulation; PASS / REVIEW / FAIL | Free |
| Tier 2 | Comparison with a real IIIT-D course hidden from the graph (topic coverage and order, assessment split, prerequisites) | Free (local embeddings) |
| Tier 3 | Judge panel: several LLMs score six rubrics, with bias controls | 1–3 calls per design |
| Validator testing | 23 injected defects must all be detected | Free |

Only the deterministic tiers can fail a design; the judges can only send it to the professor for review.

---

## 10. Known limitations

- Phase 1 still lacks a project brief and marking rubrics (planned in Phases 2 and 3 respectively).
- Topic canonicalisation in the graph is weak, so topic-level reasoning leans on embeddings.
- Generated designs still contain open errors in most saved runs; the new validation layer has not yet had a full
  end-to-end benchmark.
- The judge panel and the LLM-check scheme need professor-labelled examples before their thresholds can be trusted.
