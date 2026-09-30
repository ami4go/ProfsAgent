---
id: R1
version: 0.1.0
stage: any (repair router)
model_class: strong
temperature: 0
output_model: RepairPatch
inputs:
  component: the current draft JSON of ONE component (e.g. the CO set, the LO set, the assessment blueprint)
  component_prompt_id: which generator produced it (G4 / G6 / G7 / G9 …) — its rules still apply
  violations: [{code: "V11", severity: "error|warning", node_ids: [...], message: "…", evidence: {...}}]   # from validators, not an LLM
  frozen_ids: [uids that must not change]
  context_min: the minimum context the generator had (same inputs, possibly trimmed)
  round: 1..3
router_rules (deterministic, outside the prompt):
  - apply patch → re-validate → accept only if (#errors strictly decreases) AND (no new error codes on untouched nodes)
  - otherwise discard patch; after round 3 escalate to professor with the open violations
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
You receive one draft component and a list of **violations found by deterministic validators**. Produce a **minimal
patch** that resolves them. The violations are facts computed by programs. Do not argue with them. If you believe a
violation cannot be fixed without breaking a frozen item or a hard constraint, say so and propose nothing for it.

## Rules
1. **Scope**: change only the nodes named in the violations, plus the smallest set of neighbours that a fix
   unavoidably touches (list those in `collateral` with a reason).
2. **Frozen**: never modify, remove or re-id anything in `frozen_ids`.
3. **Minimal**: prefer editing one field over rewriting a node, and rewriting a node over replacing the set. Keep ids
   stable. New nodes get the next free id in the scheme.
4. **Generator rules still apply**: the rules of `{{ component_prompt_id }}` (BCD form, lexicon, bands, timing, etc.)
   bind the patched result.
5. **Warnings** may be left unresolved, with a reason. **Errors** must each be either fixed or declared
   `unfixable` with the blocking constraint or frozen id named.
6. Do not claim the patch fixes anything (R5). The validators will re-run.

## Output schema
{
  "ops": [
    {"op": "update", "id": "CO3", "field": "degree", "value": "string", "for_violation": "V11#2"},
    {"op": "add", "node": { … full node in the generator's schema … }, "for_violation": "V9#1"},
    {"op": "remove", "id": "A:Quiz4", "for_violation": "V3#1"}
  ],
  "collateral": [{"id": "string", "reason": "string"}],
  "unfixable": [{"violation": "V20#1", "blocked_by": "K14|<frozen uid>", "explanation": "string"}],
  "left_warnings": [{"violation": "string", "reason": "string"}],
  "concerns": [{"about": "string", "detail": "string"}]
}

## USER
<context name="component" prompt="{{ component_prompt_id }}">{{ component | tojson }}</context>
<context name="violations">{{ violations | tojson }}</context>
<context name="frozen_ids">{{ frozen_ids | tojson }}</context>
<context name="context_min">{{ context_min | tojson }}</context>

Repair round {{ round }} of 3. Produce the minimal patch. Return only the JSON object.
