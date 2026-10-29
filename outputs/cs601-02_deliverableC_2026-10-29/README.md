# Deliverable C results: CS601 "Software Development using AI", full run of 28–29 Oct 2026

A read-only snapshot of `runs/cs601-02/delivery/` after the full `recommend --refresh` run (all 27 lectures). It is kept
here, not in `runs/cs601-02`, because the app (deliverable A) uses `runs/cs601-02` as its example course and its tests
expect results for only W01.L1, W01.L2 and W02.L1. Deliverable B reads approved items from `runs/<id>/delivery/lectures`.

- `report.md`: every lecture, readable: videos, readings, practice, clips and guest speakers with scores and reasons.
- `lectures/<id>.json`: shown items, reserve, rejected (with reasons), clips, experts (same schema as the run folder).
- `guest_kits/<id>.md`: speaker brief, ranked speakers and an invitation draft, for the lectures that asked for a guest (W08.L2: none passed the checks).
- `briefs.*`, `survey.yaml`, `review.yaml`, `queries.json`, `delivery.log`: inputs, decisions file, search queries, run log.

Totals: 58 videos (53 judged from transcripts), 31 readings, 11 practice items, 33 clip entries, 72 guest speakers;
70 AI calls, 4,732 YouTube units, 2 h 27 min. How it works and the known gaps: `docs/08_phase2_C_resources_and_guests.pdf`.
