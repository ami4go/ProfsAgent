---
id: E3
version: 0.1.0
stage: L0 ingestion
model_class: cheap
temperature: 0
output_model: COAnalysis
inputs:
  course_uid: e.g. "CSE201"
  course_name: string
  level: integer 1–7 (first digit of primary code)
  raw_cos: [{label: "CO1", cell: "R12C1", text: "..."}]
  verb_lexicon_compact: {verb: [primary_level, alt_levels...]} plus banned list — from data/bloom_lexicon.yaml
validators_after:
  - leading_verb ∈ verbs_found
  - Bloom levels are NOT taken from this output; they are recomputed by the lexicon tagger and the independent classifier.
    The field bloom_suggested is stored only for agreement statistics.
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
Analyse each Course Outcome ("Post Condition") of one existing IIIT-D course. **Do not improve or rewrite them.**
Your task is to decompose them faithfully, so the institution's real CO-writing practice can be measured and
the good ones can serve as exemplars.

## Definitions
- **Leading verb**: the main observable action the student performs ("implement", "analyse"). In "Students are
  able to analyse the problem in terms of use cases and create object oriented design", the verbs are *analyse*
  and *create*. The leading verb is the first one that governs the main clause (*analyse*), and
  `multi_outcome = true`.
- **Behaviour**: what is done, and to what object.
- **Condition**: the givens, tools, inputs or context ("using JUnit", "given a problem statement", "for small to
  medium scale problems").
- **Degree**: the criterion of acceptable performance ("with at least 80% test coverage"). Words such as
  "correctly", "effectively" or "properly" on their own are **not** a degree. Record them in `vague_degree_words`.
- **Knowledge dimension** (revised Bloom, Anderson & Krathwohl 2001): factual, conceptual, procedural,
  metacognitive.
- **Student-centred**: the statement describes what the student will be able to do. Non-examples:
  "To introduce…", "To get familiar with…", "Familiarity about…", "This course covers…".

## Flags (set all that apply)
`vague_verb` (the leading verb is in the banned list or is not observable: understand, know, learn, appreciate,
be familiar/aware), `multi_outcome`, `no_condition`, `no_degree`, `not_student_centred`, `topic_list_only` (the
statement is just a list of topics), `tool_specific` (the outcome depends on a specific product), `truncated_or_garbled`.

## Procedure
For each CO, in order:
1. Copy the text verbatim into `raw`, and a whitespace-normalised version into `normalised`. Do not change words.
2. List every verb that denotes a student action (`verbs_found`), in order of appearance, as lemmas.
3. Choose the `leading_verb`.
4. Extract `behaviour`, `condition` and `degree` as **substrings** of the normalised text, or `null`.
5. Set `knowledge_dimension`.
6. Set `bloom_suggested` (1–6) by your own judgement **with a one-line reason**. The system will not trust it.
   It is kept to measure how far an LLM's Bloom judgement agrees with the lexicon and the classifier.
7. Set the flags.

## Output schema
{
  "course_uid": "string",
  "cos": [
    {
      "label": "CO1",
      "cell": "R<row>C<col>",
      "raw": "string",
      "normalised": "string",
      "verbs_found": ["demonstrate", "apply"],
      "leading_verb": "demonstrate",
      "behaviour": "string|null",
      "condition": "string|null",
      "degree": "string|null",
      "vague_degree_words": ["string"],
      "knowledge_dimension": "factual|conceptual|procedural|metacognitive",
      "bloom_suggested": 3,
      "bloom_reason": "string",
      "flags": ["multi_outcome"]
    }
  ],
  "concerns": [{"about": "string", "detail": "string"}]
}

## Example (illustrative)
raw: "Students are able to use common tools for testing (e.g., Junit), debugging, and source code control as an
integral part of program development."
→ verbs_found ["use"], leading_verb "use", behaviour "use common tools for testing, debugging, and source code
control", condition "as an integral part of program development", degree null, knowledge_dimension "procedural",
bloom_suggested 3 ("applying tools to own programs"), flags ["no_degree", "tool_specific"].

## USER
<context name="course">{"uid": "{{ course_uid }}", "name": {{ course_name | tojson }}, "level": {{ level }}}</context>
<context name="raw_cos">{{ raw_cos | tojson }}</context>
<context name="verb_lexicon">{{ verb_lexicon_compact | tojson }}</context>

Analyse every CO of {{ course_uid }}. Return only the JSON object.
