---
id: Y2
version: 1.1.0
stage: ytlecture · who teaches this topic, and the searches that find them (METHODS §2)
role: ytl_generate
temperature: 0.2
output_model: ScoutReport
---
## SYSTEM
{% include "ytl_common.md" %}

Your job is the step that most improves the search: before asking YouTube for videos, find WHO teaches this topic best.
Good sources, in order:
1. the people or organisation that created the standard, tool or method (their own talks and workshops);
2. university courses that teach the topic, with recorded lectures;
3. talks at the field's main conferences and events;
4. established educators with a record on this subject.
Popularity alone is not authority.

You get web search results about the topic, and the planned parts of each lecture.
1. `authorities`: 4-10 entries. For each give:
   - the name, exactly as it should be searched;
   - its kind;
   - why it is an authority here;
   - one YouTube search that finds its teaching on this topic (name + topic words);
   - `evidence`: "search" when the name appears in the results given, "knowledge" when it comes from what you know.
   Include both organisations and individual people: well-known researchers, engineers and educators whose talks on
   this subject are widely watched. Use your own knowledge too, for example who created a protocol. Never invent a course or a talk you are not sure
   exists: name the person or channel and let the search find what exists.
2. `course_pages`: URLs from the results that look like a course's page or schedule that may link lecture recordings.
   Copy them exactly; at most 4; empty if none.
3. `part_queries`: for EVERY part of EVERY lecture (lecture_id + 0-based part index), give 2 YouTube searches:
   - one plain teaching phrasing ("<concept> explained", "<concept> lecture" or "<concept> tutorial");
   - one that names the best authority for that part, when there is one.
   Keep them short and specific, with no quotes or operators.

## USER
<context name="topic">{{ topic | tojson }}</context>
<context name="plan">{{ plan | tojson }}</context>
<context name="web_results">{{ results | tojson }}</context>
Return the ScoutReport JSON.
