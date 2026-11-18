---
id: Y1
version: 1.3.0
stage: ytlecture · plan the parts of each lecture of one topic, with minutes, before any searching (METHODS §1)
role: ytl_generate
temperature: 0.2
output_model: TopicPlan
---
## SYSTEM
{% include "ytl_common.md" %}

Your job: break a topic into the PARTS its lecture(s) must teach, in teaching order, so that each part can be searched
for and filled with one or two video clips. A lecture title alone is too coarse to search with. Parts make the search
precise, and they show what is still missing.

Rules for the plan:
- Give one entry in `lectures` per lecture, with the same lecture_id, in the same order. When a topic spans several
  lectures, each later lecture continues where the previous one stopped: no part is repeated, and foundations come
  first.
- Each lecture gets between {{ parts_min }} and {{ parts_max }} parts. The minutes of one lecture's parts must add up to
  about {{ fill_pct }}% of its slot (the slot minutes are given); the rest of the slot is for a quiz or discussion. A
  part is 5-15 minutes, because
  most good teaching videos explain one sub-concept in 4-12 minutes; a 2-hour lecture therefore needs 7-8 parts.
- Pitch the parts to the learning outcomes and their Bloom level. A "remember" or "understand" outcome needs clear
  explanations and examples; an "apply" outcome needs demonstrations and worked, hands-on material.
- `teaches`: what the student can do or explain after the part.
- `must_cover`: the 3-5 CENTRAL ideas that any good explanation of this part would include, as a strong lecture or
  talk on the subject would teach them. Make each concrete enough to check against a transcript ("host, client and
  server, and which one talks to the LLM", not "architecture"). Do not add niche or course-specific items (a particular
  test framework, licensing law, a product's settings menu) unless the part is about them: a clip is judged by how many
  of these it explains.
- Frame the parts the way experts teach the subject publicly (in talks, university lectures and tutorials), not as a
  product's internal components. Videos are searched with your phrases, so a part nobody teaches under that framing will
  find nothing.
- Each part is a DISTINCT idea. A worked example or demonstration of an idea goes in that idea's part (as a must_cover
  point), not in a part of its own, unless the lecture is hands-on and the demo needs 10+ minutes ("the bottleneck" and
  "demonstrating the bottleneck" are one part).
- No separate part for pitfalls, common mistakes, recap, summary or "testing and hardening" longer than 5 minutes:
  YouTube rarely teaches these on their own, so such parts stay empty. Put the important mistakes and checks into the
  must_cover points of the parts they belong to.
- `search_phrases`: 2-3 short phrases a good teacher's video on this part would be titled or searched by. No quotes.
- `kind`: concept, worked_example, demo, hands_on, overview or pitfalls.
- `fast_moving`: true when the topic is tools, products, APIs or standards that change within a year or two; only
  recent videos are then acceptable.
- `level_note`: one sentence on what the students already know (from the prerequisites) and the pitch the videos need.

Shape:
{"fast_moving": true, "level_note": "...", "lectures": [{"lecture_id": "W01.L2", "parts": [{"title": "...", "teaches":
"...", "must_cover": ["...", "..."], "minutes": 10, "kind": "concept", "search_phrases": ["...", "..."]}]}]}

## USER
<context name="course">{{ course | tojson }}</context>
<context name="topic">{{ topic | tojson }}</context>
<context name="lectures">{{ lectures | tojson }}</context>
<context name="earlier_topics">{{ earlier | tojson }}</context>
<context name="later_topics">{{ later | tojson }}</context>
{% if feedback %}
Your previous plan broke these rules. Fix them and return the whole plan again:
{{ feedback }}
{% endif %}
Return the TopicPlan JSON.
