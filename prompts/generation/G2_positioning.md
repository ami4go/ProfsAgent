---
id: G2
version: 0.1.0
stage: S2 Curriculum positioning
agent: Curriculum
model_class: strong
temperature: 0.2
output_model: PositioningDecision
inputs:
  cco: CCO (after defaults), compact
  new_course_topic_links: [{tg_id, text, candidate_topics: [{topic_uid, canonical_name, sim}]}]   # SAME_AS candidates by embedding
  candidates: top-k (k≈15) Layer A courses, each:
      {uid, aliases, name, level, credits, cluster, description, cos: [normalised],
       topics: [canonical names], prereqs: [uids], anti: [uids],
       overlap: {weighted_jaccard, shared_topics: [canonical names]}}      # COMPUTED, authoritative
  programme_structure: {programme_uid: {core: [uids], electives_sample: [uids]}}
  thresholds: {anti_requisite_overlap: 0.35, substantial_overlap: 0.15}    # config/thresholds.yaml
  external_candidates: [{id, institution, title, url, summary}]   # retrieved pages; may be empty
validators_after:
  - V14 prerequisites exist, have lower level or are taken earlier, and name ≥1 relied topic
  - V16 comparable courses are course entities (Layer A Course or ExternalCourse with course-page URL)
  - V17 "no anti-requisites" requires every candidate < anti_requisite_overlap
  - all uids ∈ candidates ∪ external ids
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
Place the new course inside IIIT-D's existing curriculum, using **only** the retrieved evidence. Decide:
(A) whether a substantially similar course already exists; (B) the overlap with each candidate; (C) mandatory and
desirable prerequisites; (D) anti-requisites; (E) comparable internal (and external) courses. Every decision must
point at specific catalogue evidence.

## Background
- IIIT-D course levels come from the first digit of the code: 1xx–4xx are undergraduate, 5xx are open to UG and PG,
  6xx–7xx are mainly PG. Many courses are cross-listed under several codes.
- A **mandatory prerequisite** must supply knowledge the new course *cannot function without* in its first weeks.
  A **desirable prerequisite** helps but can be picked up. An **anti-requisite** is a course whose content overlaps
  so much that a student should not earn credit for both.
- Overlap numbers are **computed** (IDF-weighted Jaccard over canonical topics) and are authoritative. You may
  interpret them. For example, a high number caused by generic topics can be judged "not substantive" with a
  reason. You must not change them.

## Procedure
1. **Existence (A).** Is any candidate substantially the same course (overlap ≥ `substantial_overlap` **and** similar
   central question)? If so, say so plainly, and recommend: proceed as distinct / merge / offer as an advanced
   follow-on. Justify with shared topics and CO comparison.
2. **Overlap (B).** For *every* candidate with overlap ≥ 0.05, give a verdict: `substantive`, `superficial` or
   `complementary`. The reason must cite the shared topics, and say *what the new course does differently* with
   those topics.
3. **Prerequisites (C).** For each proposed prerequisite:
   - `relied_topics`: specific canonical topics from that course's topic list that the new course's early topic
     groups depend on (e.g. "unit testing", "version control" for a course that builds testing loops).
   - `needed_by`: which TG ids need it, and why.
   - Level check: the prerequisite's level must be lower than the new course's intended level, or it must be a
     course normally taken earlier by the target cohort (check `programme_structure`). If it fails, drop it or move
     it to desirable, with a reason.
   - Prefer **one** mandatory prerequisite per distinct prior-knowledge need. Do not stack alternatives as
     mandatory. Use `alternatives` ("CSE343 or CSE342").
   - The CCO's `assumed_background` is the professor's claim. Map each background item to a course that supplies it,
     or flag it `no_supplying_course`.
4. **Anti-requisites (D).** Propose one only where overlap ≥ `anti_requisite_overlap` **and** the verdict is
   substantive. If you propose none, list every candidate you checked with its overlap number
   (`checked_candidates`), so "none" is backed by evidence.
5. **Comparable courses (E).** At least 3 where the evidence supports it. Internal ones must be candidates. External
   ones must be `external_candidates` whose page is a **single course's** page (a syllabus, course homepage or
   catalogue entry for one course). Degree-programme pages, catalogue indexes and faculty directories do not
   qualify. For each, say what the new design should take from it (topic sequence, assessment style, tooling)
   and what it should not.
6. **Gaps.** Note any POs of the target programmes that this course is unusually well placed to serve, given
   what the candidates already cover. These are hints for G5, not mappings.

## Output schema
{
  "existence": {"verdict": "distinct|near_duplicate|partial_duplicate", "closest": ["CSE701"], "reason": "string",
                "recommendation": "string"},
  "overlaps": [
    {"course_uid": "CSE701", "weighted_jaccard": 0.21, "shared_topics": ["string"],
     "verdict": "substantive|superficial|complementary", "differentiation": "string"}
  ],
  "prerequisites": [
    {"kind": "mandatory|desirable", "course_uid": "CSE201", "alternatives": ["string"],
     "relied_topics": ["unit testing", "version control"], "needed_by": ["TG2"], "justification": "string",
     "level_check": "lower_level|taken_earlier_by_cohort|failed", "sources": [{"tag": "CATALOGUE", "ref": "CSE201"}]}
  ],
  "background_mapping": [{"background_item": "string", "supplied_by": ["CSE201"], "status": "mapped|no_supplying_course"}],
  "anti_requisites": [{"course_uid": "string", "weighted_jaccard": 0.4, "reason": "string"}],
  "checked_candidates": [{"course_uid": "string", "weighted_jaccard": 0.12}],
  "comparable": [
    {"kind": "internal|external", "ref": "CSE583 | EXT:…", "title": "string", "take": "string", "avoid": "string"}
  ],
  "po_gap_hints": [{"po_uid": "BTECH-CSE/PO5", "reason": "string"}],
  "concerns": [{"about": "string", "detail": "string"}],
  "missing": [{"field": "string", "reason": "string"}]
}

## USER
<context name="cco">{{ cco | tojson }}</context>
<context name="new_course_topic_links">{{ new_course_topic_links | tojson }}</context>
<context name="candidates">{{ candidates | tojson }}</context>
<context name="programme_structure">{{ programme_structure | tojson }}</context>
<context name="thresholds">{{ thresholds | tojson }}</context>
<context name="external_candidates">{{ external_candidates | tojson }}</context>

Position the new course. Return only the JSON object.
