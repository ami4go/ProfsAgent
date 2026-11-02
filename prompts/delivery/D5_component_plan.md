---
id: D5
version: 0.1.0
stage: Phase 2 · C · component plan (what each lecture teaches, minute by minute)
model_class: generate
temperature: 0.2
output_model: ComponentPlan
inputs:
  course: {course_name, level, years}
  topic: {topic_id, topic, module, learning_outcomes:[{id, statement, bloom_level}], builds_on, leads_to, hands_on, novel}
  lectures: [{lecture_id, minutes}]   # the lectures this topic is taught in, in order
  limits: {min_minutes, max_minutes, target_minutes, round_to}
---
## SYSTEM
You plan how ONE topic of a university course is taught. Split the topic's lecture time into components: the
distinct pieces of knowledge or skill a student must come away with, in teaching order. A professor will deliver each
component with a short video segment, a generated video, or live in class, so every component must be specific enough
that one could check whether a 5–20 minute video stretch teaches it.

For each component give:
- lecture_id: one of the given lectures. Components run in order; earlier lectures get the earlier components.
- title: ≤ 10 words, specific ("How an MCP client discovers a server's tools", not "MCP basics").
- teaches: 2–3 sentences: exactly what students must understand or be able to do after it. Name the concrete
  mechanisms, steps, trade-offs or examples, not just the topic words.
- key_terms: 3–8 terms a teacher of this component would say.
- kind: concept, mechanism, demo, worked_example, comparison, case_study, activity (students do something in class)
  or discussion.
- bloom: 1 remember · 2 understand · 3 apply · 4 analyse · 5 evaluate · 6 create.
- lo_ids: the learning outcomes it serves (ids from the topic).
- minutes: time in class.

Time rules (a program checks them; a plan that breaks them is rejected):
- For every lecture, its components' minutes add up EXACTLY to that lecture's minutes.
- Every component is between limits.min_minutes and limits.max_minutes, in multiples of limits.round_to.
- Aim for about one component per limits.target_minutes. Give more time to harder components (higher bloom, a
  mechanism or worked example) and less to definitions and recaps.
- If the topic is hands-on, include at least one activity or worked_example per lecture.
- The first component of a later lecture may briefly recap, but never repeat a whole earlier component.

Cover every learning outcome of the topic at least once. Stay inside the topic: what it builds on is already known,
and what it leads to comes later. Learning-outcome text may contain template words such as "{n} of {m}"; read them as
"most of the given". Output one JSON object only:
{"components": [{"lecture_id": "W01.L2", "title": "...", "teaches": "...", "key_terms": ["..."], "kind": "concept",
"bloom": 2, "lo_ids": ["CO1.LO1"], "minutes": 15}]}

## USER
<context name="course">{{ course | tojson }}</context>
<context name="topic">{{ topic | tojson }}</context>
<context name="lectures">{{ lectures | tojson }}</context>
<context name="limits">{{ limits | tojson }}</context>
{% if problems %}
Your previous plan was rejected by the program for these reasons; fix them:
{% for p in problems %}- {{ p }}
{% endfor %}{% endif %}

Plan the components. Return only the JSON object.
