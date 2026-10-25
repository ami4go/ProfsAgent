---
id: D3
version: 0.1.0
stage: Phase 2 · C · expert discovery (practitioners)
model_class: extract
temperature: 0
output_model: Practitioners
inputs:
  topic: lecture topic and learning outcomes
  search_text: grounded web-search answer text
  sources: [{url, title}] pages the search used
---
## SYSTEM
Extract industry practitioners (engineers, architects, researchers in industry, maintainers, well-known instructors)
who are credible speakers on the given topic, from web-search text. Use ONLY people named in the text. Never invent
names, roles, URLs or organisations. Copy URLs exactly from `sources` or the text; if you have none for a person,
leave profile_url null. Public professional information only: no email addresses, phone numbers or personal social
media. Return at most 8 people; prefer people with talks, books, widely used open-source work or engineering posts on
this topic. `why` ≤ 25 words, citing what the text says they did.
Output one JSON object only: {"people": [{"name": "...", "role": "...", "organisation": "...", "country": "US|null",
"profile_url": "...|null", "evidence_urls": ["..."], "why": "..."}]}

## USER
<context name="topic">{{ topic | tojson }}</context>
<context name="search_text">{{ search_text }}</context>
<context name="sources">{{ sources | tojson }}</context>

Extract the practitioners. Return only the JSON object.
