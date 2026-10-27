# Department courses: title only vs title + description + material

1 of 16 runs finished (updated automatically after every run). Each course was designed twice with `scripts/run_design.py` (strong Gemini models only, Neo4j KG, no external research, gates auto-approved):

- **title only**: just the course name; every other form field `[NOT SPECIFIED]`
- **full**: the name, a description, a topic list and the material the professor has

Inputs: `eval/inputs/dept_courses/`. Designs: `runs/dept-<course>-<title|full>-01/`. Numbers: `metrics.json`.
Closeness: each CO (module) of one run matched to its most similar in the other, cosine of local all-MiniLM-L6-v2 embeddings averaged both ways (1.0 = same wording; ≈0.5 = related but different).

## Summary

| Course | Dept | Version | Verdict | Errors | Warnings | Repairs | Calls (models) | Time | COs / LOs | Modules / topics | Level · L-T-P | Fields inferred |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Web Development for All | CSE | title | REVIEW | 0 | 30 | 4 | 14 (14× gemini-3.5-flash) | 25 min | 4 / 12 | 4 / 17 | 3 · 3-1-0 | 12 of 14 |
| Web Development for All | CSE | full | not run yet |  |  |  |  |  |  |  |  |  |
| Compiler Optimisation | CSE | title | not run yet |  |  |  |  |  |  |  |  |  |
| Compiler Optimisation | CSE | full | not run yet |  |  |  |  |  |  |  |  |  |
| Introduction to Quantitative Finance | SSH | title | not run yet |  |  |  |  |  |  |  |  |  |
| Introduction to Quantitative Finance | SSH | full | not run yet |  |  |  |  |  |  |  |  |  |
| Introduction to Transformer Architecture | CSE | title | not run yet |  |  |  |  |  |  |  |  |  |
| Introduction to Transformer Architecture | CSE | full | not run yet |  |  |  |  |  |  |  |  |  |
| Topological Data Analysis | Math | title | not run yet |  |  |  |  |  |  |  |  |  |
| Topological Data Analysis | Math | full | not run yet |  |  |  |  |  |  |  |  |  |
| Designing Conversational and Voice Interfaces | HCD | title | not run yet |  |  |  |  |  |  |  |  |  |
| Designing Conversational and Voice Interfaces | HCD | full | not run yet |  |  |  |  |  |  |  |  |  |
| Deep Learning for Protein Structure and Design | CB | title | not run yet |  |  |  |  |  |  |  |  |  |
| Deep Learning for Protein Structure and Design | CB | full | not run yet |  |  |  |  |  |  |  |  |  |
| TinyML: Machine Learning on Microcontrollers | ECE | title | not run yet |  |  |  |  |  |  |  |  |  |
| TinyML: Machine Learning on Microcontrollers | ECE | full | not run yet |  |  |  |  |  |  |  |  |  |

## Web Development for All (CSE)

|  | Title only | Full |
|---|---|---|
| Verdict / errors / warnings | REVIEW / 0 / 30 | - |
| Warnings by code | V11 23, V23 4, VC-AUDIENCE 1, VC-NOLAB 1, V6 1 | - |
| Fields the intake inferred | short_description, topics, intent, target_students, level_or_code, credits, ltp, semester_weeks, weekly_effort_hours, lab, assessment_prefs, curriculum_context | - |
| Topic groups from intake | 0 | - |
| Lecture hours used | 36.0 / 39 | - |
| Assessment | assignment 25%, quiz 15%, midsem 20%, report 10%, endsem 30% | - |
| Proctored share | 65.0% | - |
| Outside-class load (h/week) | 11.0 | - |
| Constraints (hard satisfied) | 8 (100.0%) | - |
| PO coverage | BTECH-COMMON 33.3%, BTECH-CSE 60.0%, BTECH-CSAI 66.7%, MTECH-CSE 30.8% | - |
| Closest IIIT-D course (overlap) | -  (0) | - |
| Modules | HTML5, CSS Layouts, and Responsive Web Design; Client-Side Scripting and Asynchronous Web APIs; Web Performance Diagnostic Profiling and Optimization; RESTful Web Architecture, Security, and Backend Evaluation | - |
| Resources | HTML & CSS; Eloquent Javascript; High Performance Browser Networking; RESTful Web APIs: Services for a Changing World; The web application hacker's handbook | - |

**COs, title only:**

- CO1 (L3): Write responsive web layouts using standard HTML5 markup and CSS styling rules for specified multi-device wireframes.
- CO2 (L3): Implement dynamic client-side interactivity using asynchronous API requests and DOM manipulation for interactive web application features.
- CO3 (L4): Diagnose performance bottlenecks and rendering issues in web interfaces with browser developer tools and performance metrics.
- CO4 (L5): Evaluate RESTful backend service designs against security, scalability, and usability requirements for a full-stack web system.
