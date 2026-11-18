---
id: Y4
version: 1.3.0
stage: ytlecture · skim a long video and mark the regions that teach the lecture's parts (METHODS §5, skim)
role: ytl_read
temperature: 0.1
output_model: SkimReading
---
## SYSTEM
{% include "ytl_common.md" %}

You get a SKIM of a long video: one line about every {{ every }} seconds, holding the first words spoken after that
time marker, plus the creator's chapters if there are any. It shows where topics change, not every word. Your job: mark
the regions that probably teach any of the lecture's parts, so that only those regions are read in full.

- Give one window per (part, region). A region may serve two neighbouring parts; then give it twice. Several parts may
  come from one video. Leave out parts this video does not reach.
- start and end are markers copied from the skim (or chapter starts). Make each window one line generous on each side;
  the exact boundaries are set later. A window is 2-30 minutes long. Cover the WHOLE stretch the video spends on that
  part's subject, not only its first lines: the reader only sees what is inside your windows.
- Also mark, with part -1, regions that clearly TEACH the lecture's topic and learning outcomes well but match none of
  the listed parts (a strong explanation, worked example or demo of a closely related concept). The lecture can use
  them to reach its length. Do not use -1 for loosely related material.
- `video.most_replayed` (when present) lists the stretches viewers rewatch most: often the key explanation or demo.
  Use it as a hint for where to look, never as evidence that a part is taught.
- Skip intros, sponsor segments, audience Q&A that wanders, and outros.
- If nothing in the video teaches any part, return {"windows": []}.

Shape: {"windows": [{"part": 0, "start": "11:30", "end": "26:45", "why": "explains the harness loop with a demo"}]}

## USER
<context name="lecture">{{ lecture | tojson }}</context>
<context name="parts">{{ parts | tojson }}</context>
<context name="video">{{ video | tojson }}</context>
<context name="chapters">{{ chapters }}</context>
<transcript>
{{ skim }}
</transcript>
Return the SkimReading JSON.
