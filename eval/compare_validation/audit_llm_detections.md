# LLM-only check: manual audit of every detection credit (22 Oct 2026)

The automatic scorer credits the LLM when it raises an error on the same part of the design as the planted defect. I read
the message behind every credit and checked whether it is about the planted defect.

Scoring fix (scripts/compare_validation.py): a finding the LLM also makes on the clean design (same code and parts) no
longer counts. That removed one false credit in round 2 (vague_degree). Round 1's vague_degree credits survive the
automatic fix, because on the clean design that repeat used a different code for the same remark, so they are removed by
hand below.

## Round 1 (21 Oct, first repeat, 23 defects)

| Defect | Auto credit | Finding behind it | Right reason? |
|---|---|---|---|
| banned_verbs | yes | CO1 starts with "Understand" | yes |
| bloom_inconsistencies | yes | all COs declared Bloom 1 despite higher verbs | yes |
| temporal_inversions | yes | M1.T1 in week 1 requires M8.T2 taught in weeks 12–13 | yes |
| duplicate_outcomes | yes | CO1 and CO2 identical | yes |
| orphan_los | yes | "NONE.LO1 duplicates CO1.LO1" | right item, wrong reason (missing parent not mentioned) |
| excessive_cos | yes | CO5 and CO15 are duplicates | right item, wrong reason (never says "15 COs is too many") |
| excessive_los | yes | LO13–15 duplicate LO3–5 | right item, wrong reason (never says "too many LOs") |
| cyclic_lo_deps | yes | "CO1.LO2 restates the CO" | no (the cycle is not mentioned) |
| vague_degree | yes | "{n} of {m}" placeholder (also on the clean design) | no |
| vague_degree[deeply] | yes | "{n} of {m}" placeholder (also on the clean design) | no |
| assess_before_teach | warning only | exams moved to week 2 | yes, as a warning |

Round 1, as errors: 4 of 23 for the right reason, 7 of 23 counting right item / wrong reason, 10 of 23 auto (overstated).
With warnings: 5 of 23 for the right reason.

## Round 2 (22 Oct, 4 defects + clean, gemini-3.1-flash-lite, 5 calls, 0 failed, 604 s total)

| Defect | As error | As warning | Finding |
|---|---|---|---|
| banned_verbs | yes | — | CO1 uses "understand" |
| assess_before_teach | no | yes | exams scheduled in week 2 |
| impossible_hours | no | no | — |
| vague_degree | no | no | only the "{n} of {m}" placeholder, as on the clean design |

Round 2: 1 of 4 as errors, 2 of 4 noticed. Call times 144 s, 401 s, 36 s, 15 s, 8 s; ≈16.4k prompt tokens each.

## The LLM's real extra finds (both rounds, every design)

- CO1.LO3 / CO2.LO3 contain unfilled "{n} of {m}" template text. The rules missed it; it is now rule VT-TEMPLATE.
- The project milestone is weighted 10% for 15 hours of work (warning; a judgement call, not checked by any rule).
