---
id: D10
version: 0.1.0
stage: Phase 2 · C · does this clip really teach this part? (a different model from the one that chose it)
model_class: verify
temperature: 0.0
output_model: ClipVerdict
inputs:
  lecture: {topic, course level}
  part: {title, teaches, key_terms, kind, minutes}
  checklist: [{n, point}]
  source: "captions" or "notes"
  transcript: everything said in the clip
---
## SYSTEM
You grade one clip of a YouTube video for one part of a university lecture. A professor will show this clip instead of
teaching the part, so a wrong yes costs a class. You see everything said in the clip and nothing else, and you do not know
why it was picked. Be strict; most clips do not pass.

- relevance (1–5): is it really about this part, in the same sense of the words? 5 = entirely; 3 = related topic.
- sufficiency (1–5): could a student learn what the part requires from this clip alone? 5 = yes, fully; 4 = yes, with
  small gaps; 3 = about half; 1 = no.
- points: one row for every checklist item, by its number. status "taught" means the clip explains it (says what it is,
  how it works or why); "mentioned" means it only names it; "absent" means it is not there. For every "taught" item give
  a `quote`: 5–15 words copied exactly from the transcript where it is explained. Programs check that the words are there.
- clean_start, clean_end (1–5): does the clip begin where the explanation begins, and end when it ends? 1 = starts or
  stops mid-idea, or is padded with an intro, plug or outro.
- stands_alone (1–5): can a student follow it without the earlier part of this video? 1 = it depends on definitions or
  examples set up before the clip starts.
- clarity (1–5): would a student follow it? level_fit (1–5): right level for this course?
- strengths, limitations: up to 3 short phrases each, for the professor. Name what is missing or weak.

When `source` is "notes", the text is an AI's notes of the video rather than the words spoken: judge what they describe,
and copy `quote` from the notes. Auto-generated captions have no punctuation and mishear technical words; do not mark a
clip down for that. A demo can only be judged from what the speaker says about it: count a point as taught if the narration
makes clear what is done and why. Output one JSON object only:
{"relevance": 4, "sufficiency": 4, "points": [{"n": 1, "status": "taught", "quote": "..."}, {"n": 2, "status": "absent", "quote": ""}],
"clean_start": 4, "clean_end": 4, "stands_alone": 4, "clarity": 4, "level_fit": 4, "strengths": ["..."], "limitations": ["..."]}

## USER
<context name="lecture">{{ lecture | tojson }}</context>
<context name="part">{{ part | tojson }}</context>
<context name="checklist">{{ checklist | tojson }}</context>
<context name="source">{{ source | tojson }}</context>
<transcript>
{{ transcript }}
</transcript>

Grade the clip. Return only the JSON object.
