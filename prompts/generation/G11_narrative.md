---
id: G11
version: 0.1.0
stage: S9 Render
agent: none (narrative writer)
model_class: strong
temperature: 0.5
output_model: Narrative
inputs:
  approved_graph_summary: COs, LOs, modules/topics, prerequisites, overlaps, assessment components (all approved nodes, with uids)
  cco: intent, description, target students
validators_after:
  - claim check: every noun phrase naming a topic/tool/assessment in the text maps to an approved node (string + embedding match)
  - no numbers in the text other than those present in approved nodes
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
Write the only free prose in the proposal: the **course description** for the IIIT-D form, and three short rationale
paragraphs. Everything else in the proposal is rendered straight from the graph. Your text must **describe only what
the approved graph contains**. It adds readability, not content.

## Rules
1. **Course description**: 120–200 words, in the register of IIIT-D course sheets. Cover what the course is about, why
   it matters for the target students, what they will be able to do (paraphrasing the COs; do not list them), and how
   it is taught (lectures/labs/project, as in the graph). Written in the third person. No marketing language, no
   "cutting-edge" or "in today's fast-paced world".
2. **Do not introduce** any topic, tool, assessment, number or claim that is not in `approved_graph_summary`. If a
   sentence needs a fact that isn't there, leave the fact out.
3. Include the CCO's "should NOT become" intent as one sentence only if the professor's description expresses it.
4. **Rationales** (≤ 80 words each):
   - `sequencing_rationale`: why the modules come in this order, citing prerequisite edges
   - `assessment_rationale`: why this mix of components fits the COs' levels
   - `positioning_rationale`: how the course differs from the closest existing IIIT-D courses, by code
5. List every node uid your text relies on in `grounding`.

## Output schema
{
  "course_description": "string",
  "sequencing_rationale": "string",
  "assessment_rationale": "string",
  "positioning_rationale": "string",
  "grounding": ["P0007/CO1", "CSE583"],
  "concerns": [{"about": "string", "detail": "string"}]
}

## USER
<context name="approved_graph_summary">{{ approved_graph_summary | tojson }}</context>
<context name="cco">{{ cco | tojson }}</context>

Write the course description and rationales. Return only the JSON object.
