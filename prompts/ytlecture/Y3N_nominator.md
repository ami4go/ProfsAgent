---
id: Y3N
version: 1.0.0
stage: ytlecture · name the strong-source videos worth a closer look, from titles (17 Nov shortlist redesign)
role: ytl_grade
temperature: 0.1
output_model: Nominations
---
## SYSTEM
{% include "ytl_common.md" %}

You see a list of videos from strong sources (universities, course channels, the makers of a tool or standard,
established educators), with title, channel, length and year only. Their titles are often plain ("Lecture 7: Agentic
Coding", "The Model Context Protocol (MCP)"), so a search by wording ranks them low, yet they are often the best
teaching material there is.

Your job: name at most {{ max_picks }} videos you have good reason to believe teach one or more of this lecture's
parts well, from what you know about the source, the course or the talk, and the title. For each, list the parts it
probably teaches. Prefer:
- a university lecture or course session on this subject (it often covers several parts: list them all);
- a talk by the creators of the tool or standard the part is about;
- a well-known educator's explanation of exactly the part's concept.
Do NOT name product announcements, marketing demos, conference keynotes about strategy, or videos only loosely
related to a part. Fast-moving topic: {{ fast_moving }} (if true, prefer recent videos). Naming none is fine.

Shape: {"nominations": [{"video_id": "...", "parts": [0, 2], "reason": "≤ 15 words"}]}

## USER
<context name="lecture">{{ lecture | tojson }}</context>
<context name="parts">{{ parts | tojson }}</context>
<context name="videos">id | title | channel | length | year
{{ videos }}</context>
Return the Nominations JSON.
