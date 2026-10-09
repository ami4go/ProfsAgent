# Task: extract IIIT-Delhi course sheets into ExtractedCourse JSON

Input: `/home/claude/ext/prompts/<NAME>.txt` — cells from a course spreadsheet, one per line as `row,col: value`, grouped
into sections (HEADER, PREREQUISITES, OUTCOMES, LECTURE_PLAN, LAB_PLAN, ASSESSMENT_PLAN, RESOURCES). Section splitting is
heuristic: for non-template sheets content may sit in the "wrong" section — read the whole file.
Output: write `/home/claude/ext/out/<NAME>.json` (same NAME, .json) with the Write tool. Schema is the Pydantic model in
`/home/claude/ext/layer_a.py`:

```
{"header": {"course_code": str, "aliases": [str], "name": str, "credits": str, "offered_to": [str],
            "department": str|null, "description": str,
            "prerequisites_mandatory": [str], "prerequisites_desirable": [str]},
 "outcomes": [{"label": "CO1", "raw_text": str}],
 "weekly_plan": [{"week": str, "lecture_topics": [str], "cos_met": [str], "tutorial_assignment": str|null}],
 "assessments": [{"type_label": str, "weight_pct": number}],
 "resources": [{"type_label": str, "title": str}]}
```

## Rules (match the existing 154 Gemini extractions)
- EXTRACT, never invent. Copy text verbatim (fix only obvious whitespace/line-break splits). Missing → `[]`/`null`/`""`.
- course_code: primary code without spaces ("CSE642"). Cross-listed codes ("CSE343/CSE543/ECE363") → first is
  course_code, rest go in aliases. If the sheet has no code (e.g. "CSExyz"), use the code in NAME (the filename).
- credits: string as given ("4", "2+2"). offered_to: split "UG/PG" → ["UG","PG"]; keep other phrasings verbatim.
- department: only if the sheet states it, else null.
- description: the course description paragraph verbatim (or "" if none).
- prerequisites_*: one string per prerequisite, verbatim as written ("MTH201 Probability & Statistics"). Text that says
  "none"/"nil" → []. "Pre-requisite(other)" items go into prerequisites_desirable.
- outcomes: label "CO1".. in sheet order; raw_text = full statement. If the sheet lists outcomes without labels, number
  them CO1, CO2, … in order. Ignore empty CO header cells (CO6–CO8 with no text).
- weekly_plan: one entry per row of the lecture plan. week: plain numbers, drop "W"/"Week" ("W1-W3" → "1-3",
  "Week 5" → "5"; keep "12, 13" style as written). lecture_topics: split the lecture cell into atomic topic phrases
  (split on ";", ",", newlines, " and " ONLY when they separate distinct topics; keep "X: a, b" sub-lists sensible).
  cos_met: ["CO1","CO2"] normalised labels. tutorial_assignment: the assignment/lab/tutorial cell for that row verbatim,
  else null. If a lab plan exists with week numbers, append its exercise text to tutorial_assignment of the matching
  week (prefix "Lab: "). Skip placeholder rows ("*Please insert more rows…").
- assessments: type_label verbatim ("Mid-sem", "Assignment"), weight_pct number. Ranges "10-15" → midpoint. Skip
  rows with no weight. Don't normalise to 100 — copy what's there.
- resources: type_label as given ("Textbook", "Reference", "Internet Resource"); title = full citation verbatim.
  If a cell lists several books, one item per book.
- If the file contains NO real course content (HTML/JS junk, a Bloom-taxonomy reference sheet only, a Numbers
  cover page), do NOT write JSON; instead write `/home/claude/ext/out/<NAME>.SKIP` with a one-line reason.

## Process
For each NAME in your batch: Read the .txt, write the .json. When the batch is done run
`cd /home/claude/ext && python3 validate.py <NAME> <NAME> ...` and fix every FAIL (and WARN if it's your mistake;
weights that genuinely don't sum to 100 in the sheet are fine). Do not modify files outside out/ for your batch.
Final reply: just the validate.py summary lines that aren't OK, plus any courses you're unsure about (≤10 lines).
