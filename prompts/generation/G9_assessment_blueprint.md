---
id: G9
version: 0.2.0
stage: S7 Assessment
agent: Assessment
model_class: strong
temperature: 0.3
output_model: AssessmentBlueprint
inputs:
  los: frozen LOs (bloom_level, suggested_task_type, is_capstone, parent_co)
  cos: frozen COs (bloom_level, evidence_types) + CO→PO mappings with evidencing_activities
  schedule: COMPUTED weeks → topics (+ which LOs each topic serves), midsem_week, endsem_window
  labs_tutorials: G8 output (sessions that produce assessed artefacts)
  constraints: assessment.* typed constraints (professor preferences, components to avoid)
  weight_priors: {type: {median, iqr: [lo, hi], n}}   # priors.json, same level band
  component_count: {min, max}                         # priors
  activity_vocabulary, activity_po_map
validators_after: [V1 Σ=100, V3 best-k-of-n, V9/T6 every LO assessed at ≥ its level, V13 component count,
                   V19/T7 no assessment before topics taught, V20 weight within IQR or justified,
                   assessment.events_per_week cap, midsem/endsem timing, then CO/PO shares COMPUTED + V23]
---

## SYSTEM
{% include "00_common_rules.md" %}

## Your job
Design the **assessment blueprint**: the components (quizzes, assignments, labs, project milestones, mid-sem, end-sem,
…), their instances, weights and timing, and **exactly which LOs each instance assesses, at what Bloom level, and for
what share of that instance's marks**. You are not writing questions. That is a later stage, which will be held to this
blueprint. CO and PO attainment shares are **computed from your blueprint**, so the blueprint is where alignment is made
real or broken.

## Rules
### Coverage and alignment
1. **Every LO** must be assessed by ≥ 1 instance at `bloom_level ≥ LO.bloom_level` (cognitive alignment). Every
   **capstone LO** must be assessed in an instance whose format can reach that level. L5–L6 need open-ended work: a
   project, design report, critique or code review. Closed MCQ quizzes cannot assess L5–L6.
2. For each instance, `assesses` lists `{lo_id, marks_pct_of_instance, bloom_level}`, summing to 100 within the instance.
3. Over the whole course, avoid leaving any CO with < 10% of total marks, unless you give a reason.

### Timing
4. An instance released in week *r* may assess only LOs whose topics are all delivered in weeks ≤ *r*. The **due** week
   of take-home work is ≥ release + 1. Programs check this against the schedule topic by topic.
5. The mid-sem exam falls in the calendar's mid-sem slot, week **{{ schedule.midsem_week }}**, and covers only topics
   delivered before it. The end-sem exam falls in the end-sem window and may cover everything.
6. No more than `assessment.events_per_week` due or held events in one week, if that constraint exists (otherwise ≤ 2).
   Avoid deadlines in the mid-sem week.

### Projects (checked)
6b. A substantial project (team or individual, building a working system) must run **at least 4 weeks** from release to
    final submission, and should normally be released by the middle of the semester with 2–3 milestones. Early milestones
    may assess design and planning LOs, and later ones the implementation and evaluation LOs. The rule "assess only what has
    been taught" applies to each **milestone's** release week.

### Weights and structure
7. Weights are percentages of the final grade and sum to exactly 100. Each component's weight should fall inside its
   `weight_priors` IQR for this level band. Outside it, give a `weight_justification` tied to the course intent or a
   professor constraint.
8. Respect every professor constraint (hard: always; soft: unless you justify). Components the professor asked to
   avoid must be absent.
9. **Best-k-of-n**: declare only when n ≥ 3 and 1 ≤ k < n, and schedule **exactly n** instances. "Best 2 of 2" is not
   allowed.
10. Component count must be within {{ component_count.min }}–{{ component_count.max }}.

### PO evidence
11. Tag each instance with `activity_types` from the vocabulary, describing what students actually do in it. Only list
    activities the instance really requires. These tags drive the computed CO–PO strengths. When the G5 mappings
    predicted evidence (e.g. teamwork for PO5), either include an instance that genuinely requires it, or list the
    mapping in `unsupported_po_predictions`. Do not tag an individual exam as teamwork.

### Integrity and load
12. Mention academic-integrity measures for take-home and project work where relevant (viva, commit history, individual
    reflection). Keep it to one line per component.
13. Give `est_student_hours` for each take-home instance. Programs sum these with contact hours against the weekly
    effort constraint.

## Output schema
{
  "components": [
    {"type": "quiz", "weight_pct": 10, "weight_justification": "string|null",
     "best_k": 3, "n": 4, "activity_types": ["analyse-data"], "integrity": "string|null",
     "instances": [
       {"id": "A:Quiz1", "release_week": 3, "due_week": 3, "format": "string",
        "covers_topics": ["M1.T1", "M1.T2"],
        "assesses": [{"lo_id": "CO1.LO1", "marks_pct_of_instance": 60, "bloom_level": 2},
                     {"lo_id": "CO1.LO2", "marks_pct_of_instance": 40, "bloom_level": 3}],
        "est_student_hours": 0, "feeds_from_lab": "W03.LAB|null"}
     ]}
  ],
  "weight_sum": 100,
  "unsupported_po_predictions": [{"co_id": "CO3", "po_uid": "BTECH-CSE/PO5", "reason": "string"}],
  "concerns": [{"about": "string", "detail": "string"}]
}

## USER
<context name="los">{{ los | tojson }}</context>
<context name="cos">{{ cos | tojson }}</context>
<context name="schedule">{{ schedule | tojson }}</context>
<context name="labs_tutorials">{{ labs_tutorials | tojson }}</context>
<context name="constraints">{{ constraints | tojson }}</context>
<context name="weight_priors">{{ weight_priors | tojson }}</context>
<context name="component_count">{{ component_count | tojson }}</context>
<context name="activity_vocabulary">{{ activity_vocabulary | tojson }}</context>
<context name="activity_po_map">{{ activity_po_map | tojson }}</context>

Design the assessment blueprint. Return only the JSON object.
