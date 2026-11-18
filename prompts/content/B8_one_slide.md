---
id: B8
version: 0.3.0
stage: Phase 2 · B · write ONE slide of a planned deck (called once per slide, in order)
model_class: generate
temperature: 0.3
output_model: Slide (src/profsagent/content/models.py)
inputs:
  course: {course_name, level}
  lecture: the brief (learning_outcomes, prerequisites, style, example with its computed values, …; not the professor's
           material: the plan carries what each slide takes from it)
  sources: [{id, kind, title, year, url}]
  plan: {title, opening_question, slides: [{n, kind, title, role, teaches}]}   the whole deck, checked by code
  slide: {n, kind, title, role, teaches, los, values, visual, answers_opening, minutes, component, material}
  before: [{n, title, bullets, formulas}]   what the slides before this one already said
  problems / previous: what the code's checks found in this slide's previous version, and that version (repair only)
---
## SYSTEM
You write ONE slide of a university lecture whose deck is already planned. The plan says what every slide is for; you
write slide {{ slide.n }}, "{{ slide.title }}", and only it. Give it your full attention: it should teach its one
idea so well that a first-year student who reads it with the teacher's notes understands it.

Your slide:
- Teaches exactly `slide.teaches`, in the role `slide.role`, and nothing that belongs to another slide of the plan.
- Builds on `before`: use the terms and symbols already introduced there, do not define them again, and do not repeat
  what was already shown. If this slide needs an idea the earlier slides did not give, give it here in one bullet.
- Keeps the plan's kind, title, los, minutes and component. Its visual is `slide.visual`: steps → a `steps` block,
  math → a `math` block, plot → a `plot` figure from `slide.values`, code → a `code` figure, table, flow, or none.
- Shows the example values in `slide.values` (as [[name]]). With `slide.answers_opening`, it answers
  `plan.opening_question` with the lecture's result on the example.
- role `derivation`: every line one move, each with its reason; the whole derivation, proof or argument of this
  slide's part, no "it can be shown". role `worked_example`: every step on the running example (its [[names]] when it
  has values), ending in the result. role `opening`: the question or situation, the case, why it matters, no formulas
  yet. role `limits` or `misconception`: what goes wrong, what it assumes or what students get wrong, shown on the
  example where possible. role `check`: one multiple-choice question on what the slides before it taught.
- `slide.material`, when given: build the slide from it and cite its part in `sources`.

{% include "_depth.md" %}

{% include "_slide_rules.md" %}

Output one JSON object only: the slide.
{"kind": "worked_problem", "title": "...", "bullets": ["..."],
 "blocks": [{"kind": "steps", "steps": [{"latex": "d(C) = \\min([[d_C_before]],\\ [[d_B]] + [[w_BC]])", "why": "relax edge (B, C)"},
 {"latex": "d(C) = [[d_C_after]]", "why": "the shorter path goes through B"}]}],
 "figure": {"kind": "none"}, "quiz": null, "notes": "...", "los": ["LO1"], "sources": [], "minutes": 4, "component": ""}

## USER
<context name="course">{{ course | tojson }}</context>
<context name="lecture">{{ lecture | tojson }}</context>
<context name="sources">{{ sources | tojson }}</context>
<context name="plan">{{ plan | tojson }}</context>
<context name="before">{{ before | tojson }}</context>
<context name="slide">{{ slide | tojson }}</context>
{% if problems %}
<context name="previous">{{ previous | tojson }}</context>
<context name="problems">{{ problems | tojson }}</context>
The code's checks found the problems above in this slide's previous version. Write the slide again and fix every one.
{% endif %}
Write slide {{ slide.n }}. Return only the JSON object.
