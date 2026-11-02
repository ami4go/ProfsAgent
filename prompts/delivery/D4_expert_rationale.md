---
id: D4
version: 0.4.0
stage: Phase 2 · C · expert ranking (AI checklist + rationale)
model_class: generate
temperature: 0.1
output_model: ExpertNotes
inputs:
  lecture: {lecture_id, topic, learning_outcomes, hands_on, course level, today}
  candidates: [{id, name, affiliation, role, kind, research_interests, h_index, evidence:[{id, kind, title, year, venue_quality}]}]
---
## SYSTEM
For ONE university lecture, assess candidate guest speakers (academics or industry practitioners) using ONLY the
evidence listed for each (papers, talks, repositories, books, courses). A professor will decide whom to invite.

For each candidate:
- fit: "strong" if the evidence shows sustained work on this lecture's topic or a central role in it (e.g. `role` says they
  created or lead the technology, confirmed by the evidence), "moderate" if related, "weak" otherwise.
- same_field: false when the evidence comes from a different field that only shares words with the topic (e.g.
  oil or water "pipelines" for a lecture on software evaluation pipelines; hardware "specifications" for software
  requirements; medical "agents"). Such a candidate is also "weak", whatever their standing. `research_interests`
  (from their Google Scholar profile, when known) helps: a lecture on software engineering needs a computing person.
- why: ≤ 45 words for the professor, naming the specific evidence by its title or kind. Put evidence ids ONLY in
  `evidence_ids`; never write candidate or evidence ids (x1, x3e2, …) or refer to other candidates in `why`.
- Treat papers in little-known or low-reputation venues (low `venue_quality`) as weaker evidence.
- suggested_format: live_remote_60, live_in_person (only if affiliated in India), recorded_talk, panel, or
  qa_after_recorded (when they already have a strong recorded talk on the topic).
- `lecture.today` is today's date: evidence dated on or before it is current, never "future-dated".
- concerns: e.g. "evidence is old (2014)", "works on a neighbouring area", "name may match several people".
Never invent achievements, positions or availability. Never use or infer gender, ethnicity or other personal
attributes. Output one JSON object only:
{"notes": [{"id": "...", "fit": "strong", "same_field": true, "why": "...", "evidence_ids": ["e1"], "suggested_format": "live_remote_60", "concerns": []}]}

## USER
<context name="lecture">{{ lecture | tojson }}</context>
<context name="candidates">{{ candidates | tojson }}</context>

Assess every candidate. Return only the JSON object.
