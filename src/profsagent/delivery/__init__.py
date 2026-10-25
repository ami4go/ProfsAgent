"""Phase 2 · Deliverable C: learning resources and expert speakers for each lecture of an approved Phase 1 design.

Flow (docs/03_phase2_C_learning_resources_and_experts_plan.md):
  brief.py      lecture briefs from the approved design (no AI)
  survey.py     per-lecture delivery choices (own / attach / generate / assistance / guest; several allowed)
  resources.py  learning-resource aid (books, readings, videos, practice): discover → cover → review → rank → check
  experts.py    expert-speaker aid: academics + practitioners worldwide, ranked with evidence; guest-lecture kit
  checks.py     hard rules in code before the professor sees anything
  review.py     professor decisions (approve / replace / reject + reason), feedback, link health
  graph.py      delivery records in Neo4j, linked to the course's lectures
  pipeline.py   orchestration per run (scripts/run_delivery.py)
"""
