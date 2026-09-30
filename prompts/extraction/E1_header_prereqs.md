---
id: E1
version: 0.1.0
stage: L0 ingestion
model_class: cheap
temperature: 0
output_model: HeaderPrereqExtraction
inputs:
  course_uid: primary code from Courses.json (e.g. "CSE201")
  index_row: the Courses.json row (JSON)
  header_cells: parsed cells of the header section [[row, col, text], ...]
  prereq_cells: parsed cells of the Pre-requisites section [[row, col, text], ...]
  catalogue_candidates: list of {uid, aliases, name, level} — full course index (≈475 rows, compact)
validators_after:
  - every resolved code exists in the index
  - no self-prerequisite
  - cell refs exist in the parsed sheet
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
Extract the header fields and the prerequisite structure of **one** IIIT-D course from its proposal sheet,
and resolve each prerequisite to catalogue course codes where the text supports it.

## Background you need
- IIIT-D course sheets follow a proposal form with a header (Course Code, Department, Course Name, Credits,
  Course Offered to, Course Description) and a "Pre-requisites" block with three kinds: **Mandatory**,
  **Desirable** and **Other**. Older sheets lay these out as columns under one header row. Newer ones lay
  them out as rows. Some sheets put everything in one cell.
- Prerequisite text comes in several shapes:
  (a) codes: "CSE101, CSE102"
  (b) names: "Machine Learning", "Operating Systems"
  (c) name + code: "CSE102 Data Structures & Algorithms"
  (d) disjunctions: "ML (CSE343) or SML (CSE342)"
  (e) skills: "Experience with C/C++ programming", "Knowledge of AI and Learning techniques"
  (f) administrative: "Consent of the instructor"
- The Courses.json `Prerequisites` and `Preferable_Prerequisites` fields are a second, sometimes different,
  record of the same thing. When the sheet and the index disagree, **report both**. Do not choose between them.

## Procedure
1. Read the header cells and extract each field. Credits must be an integer that appears in the cells or
   the index row. If they disagree, report the sheet value and note the index value in `concerns`.
2. Split the prerequisite text into **atomic requirements**. A disjunction ("A or B") is one requirement with
   several alternatives. A conjunction ("A, B") is several requirements.
3. For each requirement, decide `kind` ∈ {mandatory, desirable, other}. The kind comes from the column or row
   label it appears under. If there is no label, use `mandatory` and add a concern.
4. Resolve each alternative:
   - If it contains a code pattern (letters + 3 digits, optional letter suffix), normalise it (remove spaces,
     upper-case) and look it up in `catalogue_candidates` aliases.
   - Else, if the text is a course name, match it against catalogue names. Accept only a clear match
     (same name modulo punctuation/abbreviation, e.g. "DSA" ↔ "Data Structures and Algorithms").
     Give `confidence` high/medium/low.
   - Else, classify it as a `skill` (keep a short normalised phrase) or as `administrative`.
5. Anti-requisites: extract them the same way from the sheet if present, and also from the index row.
6. Record the exact cell coordinates for every extracted item.

## Output schema
{
  "course_uid": "string",
  "header": {
    "codes_on_sheet": ["string"],          // all codes printed in the Course Code cell, normalised
    "name": "string|null",
    "department": "string|null",
    "credits": "integer|null",
    "offered_to": "string|null",           // e.g. "UG", "UG/PG", "PG"
    "description": "string|null",          // verbatim, whitespace-normalised
    "template_version": "old|new|unknown", // new = has Department / Weekly Lab Plan fields
    "cells": {"<field>": "R<row>C<col>"}
  },
  "prerequisites": [
    {
      "req_id": "P1",
      "kind": "mandatory|desirable|other",
      "raw_text": "string",
      "cell": "R<row>C<col>",
      "alternatives": [
        {
          "type": "course|skill|administrative",
          "resolved_uid": "string|null",    // must exist in catalogue_candidates
          "matched_on": "code|name|null",
          "confidence": "high|medium|low|null",
          "skill_phrase": "string|null"
        }
      ]
    }
  ],
  "anti_requisites": [
    {"raw_text": "string", "source": "sheet|index", "resolved_uid": "string|null", "confidence": "high|medium|low|null"}
  ],
  "index_disagreements": ["string"],
  "concerns": [{"about": "string", "detail": "string"}],
  "missing": [{"field": "string", "reason": "string"}]
}

## Example (illustrative; not a real sheet)
Cells: `R7C1 "Pre-requisite (Mandatory)" | R7C2 "Pre-requisite (Desirable)"`,
`R8C1 "CSE102 Data Structures, Linear Algebra" | R8C2 "Probability (MTH201) or Statistics"`.
→ Three requirements:
- P1 mandatory → course CSE102 (code, high)
- P2 mandatory → "Linear Algebra" matched by name only if the catalogue has a course with that name; otherwise
  a skill "linear algebra"
- P3 desirable → alternatives [course MTH201 (code, high), skill "statistics" or a name match]

## USER
<context name="course_uid">{{ course_uid }}</context>
<context name="index_row">{{ index_row | tojson }}</context>
<context name="header_cells">{{ header_cells | tojson }}</context>
<context name="prereq_cells">{{ prereq_cells | tojson }}</context>
<context name="catalogue_candidates">{{ catalogue_candidates | tojson }}</context>

Extract the header and prerequisites for {{ course_uid }} following the procedure. Return only the JSON object.
