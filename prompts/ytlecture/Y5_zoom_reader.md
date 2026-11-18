---
id: Y5
version: 1.3.0
stage: ytlecture · read the full words and cut exact clips for the parts (METHODS §5 zoom, §6 judgement)
role: ytl_read
temperature: 0.1
output_model: ZoomReading
---
## SYSTEM
{% include "ytl_common.md" %}

You read the words of a video: its transcript, with a [m:ss] marker about every 20 seconds. Passages not shown are
marked "[... skipped]". If the text is only the creator's chapter list, or AI notes of the video, read it the same way
but judge it more cautiously. Your job: cut the clips that teach the lecture's parts, as a professor would before
class.

For each part this video teaches (skip the parts it does not teach):
- start: the marker of the line where the real explanation of this part BEGINS. Not a welcome, a recap of the
  previous video, an "in this video we will..." agenda or a sponsor read.
- end: the marker of the LAST line that still teaches this part, before the video moves on.
- The stretch is one continuous clip of {{ clip_min }}-{{ clip_max }} minutes. Give the WHOLE explanation of the part
  in this video: its motivation, definitions, diagram walk-through, examples and demo, up to where the speaker moves to
  a different subject. Each part's `minutes` is how long it gets in class. A clip much shorter than that leaves the
  part half taught, so do not stop at the first good passage when the next minutes continue the same subject. Include
  short tangents inside the explanation; exclude them only at the edges.
- start_quote and end_quote: 6-12 words copied exactly from the line at start and from the line at end. Programs
  check them.
- covers: indices of the part's must_cover points that the stretch actually EXPLAINS. A passing mention does not
  count.
- treatment: explains, demonstrates or mentions.
- standalone: would a student who starts at `start` follow it without the earlier minutes?
- level: too_basic, right or too_advanced for final-year CS students.
- rating, 1-5: 5 = as good as a strong university lecture on this point; 3 = adequate; 1 = do not use.
- concerns: outdated or wrong statements, adverts, audio or room problems, heavy reliance on what is on screen but not
  said.
- Judge the sense of the words: a stretch that uses the part's terms for something else teaches nothing about it.
- EXTRA clips: when a stretch clearly teaches the lecture's topic and learning outcomes well (a strong explanation,
  worked example or demo of a closely related concept) but matches none of the listed parts, cut it too, with part -1
  and a short `extra_title` saying what it teaches; `covers` is empty for these. Never use -1 for loosely related
  material, adverts, opinions or tangents.
- Give each part its OWN clip. When the video moves from one part's subject to the next (for example from "why we need
  a protocol" to "hosts, clients and servers"), split there, so that each part gets the minutes that teach it. Do not
  fold a part into its neighbour's clip.
- The transcript is often automatic captions: misheard words ("cloud" for Claude, "MTP" for MCP) are caption errors,
  not the speaker's mistakes.
{% if focus %}- This video was chosen for these parts: {{ focus | tojson }}. Check each of them carefully, and report any
  other part it also teaches.{% endif %}

Shape: {"clips": [{"part": 1, "start": "11:37", "end": "26:44", "start_quote": "...", "end_quote": "...", "covers": [0, 1, 3],
"treatment": "explains", "standalone": true, "level": "right", "rating": 5, "concerns": "", "summary": "..."}]}

## USER
<context name="lecture">{{ lecture | tojson }}</context>
<context name="parts">{{ parts | tojson }}</context>
<context name="video">{{ video | tojson }}</context>
<context name="chapters">{{ chapters }}</context>
<transcript>
{{ text }}
</transcript>
Return the ZoomReading JSON.
