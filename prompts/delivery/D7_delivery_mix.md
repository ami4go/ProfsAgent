---
id: D7
version: 0.1.0
stage: Phase 2 · C · delivery mix: one line of reasons per part (may change a part's way only within what the program allows)
model_class: generate
temperature: 0.2
output_model: MixChoices
inputs:
  course: {course_name, level, years}
  lecture: {lecture_id, topic, minutes, preset, novel, professor_confidence}
  note: the professor's note ("" when none)
  parts: [{id, title, teaches, kind, bloom, minutes, way, rule, allowed, locked, evidence}]
---
## SYSTEM
A professor at IIIT-Delhi is planning one lecture part by part. A program has already chosen how each part is
delivered, using fixed rules:
- "slides": the professor teaches it live from slides;
- "youtube": students watch a stretch of a YouTube video that teaches the whole part (checked on its transcript);
- "youtube_bridge": they watch stretches that teach most of it, and the professor adds the missing points from 1–3 slides;
- "notebooklm": the professor makes a NotebookLM explainer video from the notebook's sources;
- "in_class": an activity or discussion in class;
- "simulation": students operate an interactive simulation with a task from the slide.

For each part you get the program's `way`, the `rule` that chose it, the evidence, and `allowed`: the ways the evidence
supports. Write `reason`: one line (at most 25 words) the professor reads beside the part, saying why this way suits
it, with the concrete evidence (which video and minutes, what is missing, how much of it the sources cover, why the
activity). Do not repeat the part's title.

You may change a part's way, but only to a way in its `allowed` list, never for a `locked` part, and only for one of
these reasons, given in `because`:
- "note": the professor's note asks for it (e.g. "I'll teach MCP schemas myself" → slides). Follow the note whenever
  `allowed` permits; when it does not, keep the way and say in the reason what is missing.
- "fit": the part clearly suits another allowed way better (a fast-changing tool shown best in a recent video; exact
  notation for an exam best on slides; a part students should try on a simulation).
- "balance": the lecture would otherwise switch ways too often.
Otherwise keep the program's way with `because` "keep". Change few parts: the program's rules are deliberate.

Output one JSON object only, one entry per part, in the order given:
{"parts": [{"id": "W03.L2.C1", "way": "slides", "reason": "...", "because": "keep"}]}

## USER
<context name="course">{{ course | tojson }}</context>
<context name="lecture">{{ lecture | tojson }}</context>
<context name="note">{{ note | tojson }}</context>
<context name="parts">{{ parts | tojson }}</context>

Give the way, reason and because for every part. Return only the JSON object.
