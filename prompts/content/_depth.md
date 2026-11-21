---
id: _depth
version: 0.3.0
stage: Phase 2 · B · shared text, included by B1, B7 and B8 (B6 has its own depth line) (the professor's content depth)
---
{% set depth = lecture.get("depth") or "standard" %}{% if depth == "high" %}
Content depth: HIGH. The professor asked for the full treatment, not a survey:
- Cover what a standard treatment of this topic at this level contains (the field's textbook chapter on it and its
  primary sources): its central results, the reasons they hold and the consequences they are used for, not only the
  definitions and the arithmetic. Where later work has replaced or extended the method in common practice, say so and
  show how the newer method relates to this one.
- Establish every result the lecture uses completely: every step with its reason, nothing left as "it can be shown"
  (a derivation or proof in maths, a full trace or a correctness argument in algorithms, the evidence and the
  reasoning behind each claim in a conceptual topic).
- Give each central result its other standard views or approaches, and show how they relate or agree (for example
  a geometric and an algebraic view, a recursive and an iterative algorithm, two schools of thought on one question).
- State the conditions each result needs (assumptions, preconditions, bounds, the context a claim holds in), say why
  it needs them, derive or argue the bound or condition where there is one, and show on the example what happens when
  it fails.
- After each derivation, proof or method, a worked case on the running example; after each method, what it costs and
  when to prefer it.
- Explain why each formula, rule or step has its form before it is used.
{% elif depth == "basic" %}
Content depth: BASIC. The professor asked for an introduction: intuition, pictures and examples first; establish only
the central result, step by step; leave side derivations, proofs and bounds out (name them as "for later").
{% endif %}
