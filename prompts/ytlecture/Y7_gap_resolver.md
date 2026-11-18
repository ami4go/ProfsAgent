---
id: Y7
version: 1.0.0
stage: ytlecture · decide what to do about parts that no verified clip covers (one bounded second round)
role: ytl_generate
temperature: 0.3
output_model: GapPlan
---
## SYSTEM
{% include "ytl_common.md" %}

Some parts of a lecture have no clip that passed the checks. For each such part, choose an action:
- "search": propose 2-3 NEW YouTube searches likely to find a teaching video for it. Try a narrower sub-concept, the
  vocabulary practitioners use, an official channel or a named teacher. Do not repeat the searches already tried.
- "accept_gap": when a good standalone video on this part is unlikely to exist (it is very course-specific, or better
  taught live). Say why; the professor will cover it another way.

Shape: {"actions": [{"part": 2, "lecture_id": "W01.L1", "action": "search", "queries": ["...", "..."], "reason": "..."}]}

## USER
<context name="topic">{{ topic | tojson }}</context>
<context name="gaps">{{ gaps | tojson }}</context>
Return the GapPlan JSON.
