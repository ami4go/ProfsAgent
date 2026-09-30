---
id: X1
version: 0.1.0
stage: S2 Curriculum positioning (external research)
agent: Research
model_class: strong
temperature: 0.3
output_model: SearchPlan
inputs:
  cco: CCO (compact): course name, description, topic groups, intent, level, target students
  institutions: [{id, name, country, domains}]   # whitelist, config/institutions.yaml
  limits: {max_queries}
next_step: program runs each query through Google-Search grounding restricted to whitelisted domains, plus
           catalogue adapters (Stanford ExploreCourses, NUSMods) with catalogue_keywords; fetched pages go to X2.
validators_after:
  - ≤ max_queries queries; every target_institution ∈ whitelist ids
  - no query names a specific course code unless it appears in the CCO
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
Plan a **web search for comparable courses** at leading universities (the whitelist below). The goal is to find
2–6 single-course pages (a syllabus, a course homepage or a catalogue entry for one course) whose content
genuinely resembles the course being designed. These become evidence for the course's positioning, topic
sequence and assessment design.

## Why a plan and not just the course title
Universities name the same course very differently. IIIT-Delhi's "Advanced Programming" (object orientation,
design, testing, concurrency) corresponds to courses named "Software Construction", "Principles of Software
Development", "Object-Oriented Programming and Design", "Programming Methodology II" and so on elsewhere. A search
on the literal title finds unrelated courses and misses the right ones. Your plan must therefore:
1. Work out the **equivalent course titles** that leading institutions actually use for this kind of course, from
   the content (topic groups + intent), not from the title alone. Give 4–8.
2. Pick **distinguishing keywords**: 5–10 terms that separate this course from near neighbours. For an
   OOP/design course: "design patterns", "unit testing", "UML", "concurrency", as opposed to a generic
   "introduction to programming".
3. Write **search queries**. Each query should combine an equivalent title or distinguishing keywords with words
   that pull up course pages ("course", "syllabus", "lecture schedule", "course homepage") and one or two
   institutions or domains. Use `site:` operators with whitelisted domains when a query targets one institution.
   Spread the queries across **at least 4 different institutions and at least 2 countries**.
4. Give **catalogue keywords**: 2–4 short keyword strings for searching institutional course catalogues directly
   (e.g. "software construction", "object oriented design").

## Rules
- Target only whitelisted institutions. Never target IIIT-Delhi or other Indian institutions. The internal
  catalogue is searched separately.
- Do not guess course codes ("MIT 6.1020") unless the CCO mentions them. Search engines resolve titles, and guessed
  codes produce confident wrong hits.
- Queries should be short (≤ 12 words excluding operators), as a person would type them.
- Do not include words that describe *this* proposal ("IIIT", "B.Tech", "proposal").

## Output schema
{
  "equivalent_course_titles": ["string"],
  "distinguishing_keywords": ["string"],
  "queries": [
    {"query": "software construction course syllabus site:mit.edu", "target_institutions": ["MIT"],
     "equivalent_titles": ["Software Construction"], "why": "string"}
  ],
  "catalogue_keywords": ["string"],
  "concerns": [{"about": "string", "detail": "string"}]
}

## USER
<context name="cco">{{ cco | tojson }}</context>
<context name="institutions">{{ institutions | tojson }}</context>
<context name="limits">{{ limits | tojson }}</context>

Plan the comparable-course search. Return only the JSON object.
