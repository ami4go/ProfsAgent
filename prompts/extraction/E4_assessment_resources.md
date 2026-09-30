---
id: E4
version: 0.1.0
stage: L0 ingestion
model_class: cheap
temperature: 0
output_model: AssessmentResourceExtraction
inputs:
  course_uid: string
  assessment_cells: [[row, col, text], ...]
  resource_cells: [[row, col, text], ...]
  weekly_events: events[] from E2 output (for cross-checking counts)
validators_after:
  - Σ weight_pct reported; if ≠ 100 it is recorded as a corpus data-quality fact (not "fixed")
  - resources go to deterministic API verification (Crossref / OpenLibrary / arXiv); unverified ones keep verified=false
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
Normalise the Assessment Plan and the Resource Material sections of one IIIT-D course sheet.

## Part A — Assessment plan
Map each row to one canonical type:
`quiz, assignment, lab, project, midsem, endsem, presentation, report, participation, peer_evaluation, viva,
homework, tutorial, other`.
- Keep `raw_label` exactly as written.
- `weight_pct`: the number as written (e.g. "20", "20%", "0.2" → 20). If a row has a range or text ("15-20"),
  record `weight_pct: null`, put the text in `weight_raw` and add a concern.
- Structure hidden in the text ("best 3 of 4 quizzes", "2 assignments", "project in 3 milestones") goes into
  `instances_declared` and `best_k`.
- Cross-check against `weekly_events`: count how many events of the matching type appear in the weekly plan and
  report the count as `instances_in_plan`. **Do not reconcile a mismatch.** Report both numbers.
- Report the sum of weights exactly as computed from the rows. Do not normalise to 100.

## Part B — Resources
For each resource row, parse whatever is present into bibliographic fields. **Do not complete missing fields from
memory.** If the sheet says "Core Java - Volumes I and II", output that title, and leave authors, year, edition
and publisher `null` unless they are written there. A deterministic lookup step fills and verifies metadata
later, and anything you add from memory would contaminate the verification statistics.
Types: `textbook, reference_book, paper, online_course, documentation, website, video, other`.

## Output schema
{
  "course_uid": "string",
  "assessment": [
    {"row": "R<row>", "raw_label": "string", "type": "quiz", "weight_pct": 10, "weight_raw": "string|null",
     "instances_declared": 4, "best_k": 3, "instances_in_plan": 2, "notes": "string|null"}
  ],
  "weight_sum": 100,
  "resources": [
    {"row": "R<row>", "type": "textbook", "raw": "string", "title": "string|null", "authors": ["string"],
     "year": null, "edition": null, "publisher": null, "isbn": null, "doi": null, "url": "string|null"}
  ],
  "concerns": [{"about": "string", "detail": "string"}],
  "missing": [{"field": "string", "reason": "string"}]
}

## USER
<context name="course_uid">{{ course_uid }}</context>
<context name="assessment_cells">{{ assessment_cells | tojson }}</context>
<context name="resource_cells">{{ resource_cells | tojson }}</context>
<context name="weekly_events">{{ weekly_events | tojson }}</context>

Normalise the assessment plan and resources of {{ course_uid }}. Return only the JSON object.
