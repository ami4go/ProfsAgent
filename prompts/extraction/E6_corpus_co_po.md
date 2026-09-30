---
id: E6
version: 0.1.0
stage: L0 derived edges
model_class: strong
temperature: 0
output_model: CorpusCOPOInference
inputs:
  programme_pos: [{uid, text}]                      # verbatim, from data/programmes/<prog>.yaml
  course: {uid, name, level, description}
  cos: [{uid, normalised, leading_verb, flags, topics: [canonical names from ADDRESSES]}]
  assessment_types: [types with weights]            # from E4
validators_after:
  - po uids ∈ programme_pos
  - stored as MAPS_TO_INFERRED only; never rendered as institutional fact
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
For each Course Outcome of one **existing** IIIT-D course, infer which programme outcomes (POs) it plausibly serves,
and how strongly. IIIT-D course sheets do not record CO–PO mappings, so everything you output is an **inference**.
It is stored with that label and is used only as statistical background ("outcomes like this usually serve PO4"),
never as a fact about the course.

## Relevance scale
- **3**: the PO is a *primary purpose* of this CO. Achieving the CO directly exercises the PO's capability.
- **2**: the CO substantially contributes to the PO, but the PO is not its main point.
- **1**: a weak or incidental contribution.
- Omit the PO entirely when the only link is shared vocabulary.

## Rules
1. At most 3 POs per CO. Most COs have 1–2.
2. Each link needs a justification that **quotes a phrase from the CO** and **a phrase from the PO**, and says why
   they correspond.
3. Consider the course's assessment types. A CO whose course has no team component should not be linked to
   "function effectively in teams" unless the CO itself says so.
4. COs flagged `vague_verb` or `topic_list_only` get at most relevance 1, and `low_information: true`.

## Output schema
{
  "course_uid": "string",
  "links": [
    {"co_uid": "CSE201/CO3", "po_uid": "BTECH-CSE/PO4", "relevance": 3,
     "co_phrase": "string", "po_phrase": "string", "justification": "string"}
  ],
  "low_information_cos": ["CSE201/COx"],
  "concerns": [{"about": "string", "detail": "string"}]
}

## USER
<context name="programme_pos">{{ programme_pos | tojson }}</context>
<context name="course">{{ course | tojson }}</context>
<context name="cos">{{ cos | tojson }}</context>
<context name="assessment_types">{{ assessment_types | tojson }}</context>

Infer CO→PO links for this course. Return only the JSON object.
