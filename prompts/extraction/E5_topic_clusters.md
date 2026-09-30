---
id: E5
version: 0.1.0
stage: L0 topic canonicalisation
model_class: strong
temperature: 0
output_model: TopicClusterDecision
inputs:
  cluster_id: string
  members: [{mention_uid, phrase, surface, course_uid, course_name, week, neighbours: [phrases in same week]}]   # ≤ 60, sampled if larger
  backbone_candidates: [{ref, title, parent_title, description}]   # top-5 CS2023 KUs / SWEBOK v4 topics by embedding
  existing_topic_names: [canonical names already assigned elsewhere, for de-duplication]
validators_after:
  - backbone_ref ∈ backbone_candidates or null
  - every member appears in exactly one output group
  - canonical_name unique across the topic table (else merge review queue)
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
You receive one **cluster** of topic mentions that were grouped by embedding similarity across IIIT-D course
plans. Decide whether they really name the same teachable concept. Name the resulting canonical topic(s), write
a one-line definition, and map each to the reference taxonomy where the candidates support it.

## Why this matters
Every overlap, prerequisite and coverage computation in the system counts canonical topics. A cluster that merges
two different concepts creates false overlaps, and a concept split across two clusters hides real ones. Be
conservative. **When in doubt, split.**

## Rules
1. Same concept means an instructor would accept the phrases as interchangeable **in a syllabus**. Differences in
   depth ("Introduction to X" vs "X") do not split. Different objects do split: "Process scheduling" (OS) vs
   "Project scheduling" (SE). Use `course_name` and `neighbours` to disambiguate.
2. A tool/product mention ("JUnit") and its concept ("Unit testing") are **different** topics. Split them, and give
   the tool topic `kind: tool` plus a `tool_of` reference to the concept group.
3. `canonical_name`: 1–5 words, lower-case except proper nouns, singular, no "introduction to". Prefer the
   standard term used in CS2023/SWEBOK when a backbone candidate matches.
4. `definition`: one sentence, ≤ 25 words, that is neutral and does not mention any specific course.
5. `backbone_ref`: choose a candidate only if the topic sits *within* that knowledge unit. If none fits, use `null`
   and say why. Never produce a ref that isn't in the candidates.
6. If a canonical name already exists in `existing_topic_names` for what is the same concept, set
   `merge_with` to that name rather than creating a near-duplicate.

## Output schema
{
  "cluster_id": "string",
  "groups": [
    {
      "canonical_name": "unit testing",
      "definition": "string",
      "kind": "concept|technique|tool|application",
      "tool_of": "string|null",
      "backbone_ref": "string|null",
      "backbone_reason": "string",
      "merge_with": "string|null",
      "member_uids": ["CSE201/W07/m3"]
    }
  ],
  "split_reason": "string|null",
  "concerns": [{"about": "string", "detail": "string"}]
}

## USER
<context name="cluster">{"cluster_id": "{{ cluster_id }}", "members": {{ members | tojson }}}</context>
<context name="backbone_candidates">{{ backbone_candidates | tojson }}</context>
<context name="existing_topic_names">{{ existing_topic_names | tojson }}</context>

Decide the canonical topic(s) for this cluster. Return only the JSON object.
