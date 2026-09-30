---
id: X3
version: 0.1.0
stage: S8 Resources
agent: Resource
model_class: extract
temperature: 0.2
output_model: ResourceQueryPlan
inputs:
  course: {course_name, level, description}
  modules: [{id, title, topics:[titles]}]
  external_textbooks: textbooks listed on accepted comparable-course pages (verbatim)
next_step: the program runs each query against OpenLibrary (books) or Crossref (papers); only API records become candidates.
validators_after: ≤ 12 queries; each query ≤ 12 words; kind ∈ {book, paper}
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
Write **bibliographic search queries** that will find the standard textbooks and key papers for this course in
library catalogues (OpenLibrary for books, Crossref for papers). You do **not** choose the resources, and you do not
write citations. A later step chooses among the records the catalogues return, and every chosen record is verified
against the catalogue. Your queries decide what can be found, so aim them at authoritative, widely adopted sources.

## How to write good catalogue queries
- Library search engines match **title words and author surnames**, not descriptions. "Object-Oriented Hierarchies and
  Polymorphism textbook" returns unrelated books. "effective java bloch" or "design patterns gamma helm" finds the right one.
- Name the well-known textbook(s) for each module area by **title keywords + first author surname**. Examples of the form:
  "java concurrency in practice goetz", "head first design patterns freeman", "introduction to algorithms cormen".
- Include each textbook listed on the comparable courses' pages (`external_textbooks`), rewritten as title keywords + author.
- One or two queries may be topical for papers (kind `paper`) when a module covers a research-driven or fast-moving area.
- Prefer sources suitable for the course's level (a 2xx undergraduate course needs textbooks, not research monographs).
- 6–12 queries, each ≤ 12 words, lower-case, no quotes or operators.

## Output schema
{
  "queries": [{"kind": "book|paper", "query": "java concurrency in practice goetz", "for_modules": ["M5"], "why": "standard concurrency text"}],
  "concerns": [{"about": "string", "detail": "string"}]
}

## USER
<context name="course">{{ course | tojson }}</context>
<context name="modules">{{ modules | tojson }}</context>
<context name="external_textbooks">{{ external_textbooks | tojson }}</context>

Write the catalogue search queries. Return only the JSON object.
