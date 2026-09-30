# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-bloom_inconsistencies` · generated deterministically from the design graph · validator status: **1 errors, 20 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level specified without a concrete course code | professor |
| — | CONFLICT ['K15', 'K16'] | — | Setting all Course Outcomes strictly to Bloom Level 1 contradicts the special constraint requiring them to be assessed exclusively with open-ended design projects at Bloom Level 6. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. This course matters for target students by equipping them with engineering practices for emerging AI developer tools. Upon completing the course, students will be able to configure agent-assisted coding workflows and context management tools, construct executable specifications from natural language requirements, analyze operational failures of agent-assisted software factory loops, evaluate the reliability and performance of AI-generated software artifacts, and assess end-to-end agent-assisted software development workflows. The course is taught through lectures, tutorials, laboratory sessions, and project work.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students require solid object-oriented programming, unit testing, and software design principles to effectively build, evaluate, and test applications using AI coding agents. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers 'Topics in Software Engineering: AI in SE' with a weighted Jaccard overlap of 0.185 (above the substantial overlap threshold of 0.15), CSE701 focuses broadly on data and machine learning techniques applied across software engineering repositories and metrics. In contrast, the new course focuses specifically on modern AI-native software development, agentic workflows, prompt/context engineering, and coding agents collaborating directly with developers.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure agent-assisted coding workflows and context management tools for a given software repository, integrating model context protocol and coding agents such that all public integration tasks execute successfully.** `[CORPUS, USER]`  
verb *configure* · behaviour *agent-assisted coding workflows and context management tools for a given software repository* · condition *integrating model context protocol and coding agents* · degree *such that all public integration tasks execute successfully* · evidence: programming_assignment, lab_task · marks share (computed): 18.0%

- CO1.LO1 (L1) Identify the basic components of agent-assisted coding workflows and context management configurations from a supplied repository description
- CO1.LO2 (L3 ★capstone) Configure agent-assisted coding workflows and context management tools for a given software repository using model context protocol

**CO2 (L3, procedural) — Construct executable specifications from natural language requirements documents, using spec-driven development practices such that every user case in the specification is covered by at least one testable artifact.** `[CORPUS, USER]`  
verb *construct* · behaviour *executable specifications from natural language requirements documents* · condition *using spec-driven development practices* · degree *such that every user case in the supplied requirements document is covered* · evidence: design_document, programming_assignment · marks share (computed): 18.25%

- CO2.LO1 (L3 ★capstone) Construct executable specifications from natural language requirements documents using spec-driven development practices
- CO2.LO2 (L2) Illustrate requirements-to-specification mappings using standard design templates

**CO3 (L4, procedural) — Analyze the operational failures of an agent-assisted software factory loop, identifying at least three distinct failure causes with supporting log evidence from the execution traces.** `[CORPUS, USER]`  
verb *analyze* · behaviour *the operational failures and generated outputs of an agent-assisted software factory loop* · condition *using execution traces and log evidence from supplied runs* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, programming_assignment · marks share (computed): 30.0%

- CO3.LO1 (L4 ★capstone) Analyze the operational failures of an agent-assisted software factory loop using execution traces and log evidence from supplied runs
- CO3.LO2 (L4) Examine operational logs from agent runs to differentiate between loop failures and syntax errors

**CO4 (L5, procedural) — Evaluate the reliability and performance of AI-generated software artifacts against automated testing suites and deployment criteria, measuring defect rates and justifying improvements against stated requirements.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *the reliability and performance of AI-generated software artifacts* · condition *against automated testing suites and deployment criteria* · degree *justifying each design decision against at least one stated requirement* · evidence: project_deliverable, report · marks share (computed): 12.5%

- CO4.LO1 (L5 ★capstone) Evaluate the reliability and performance of AI-generated software artifacts against automated testing suites and deployment criteria
- CO4.LO2 (L5) Appraise automated testing suites and deployment criteria for AI-generated code

**CO5 (L5, procedural) — Evaluate an end-to-end agent-assisted software development workflow for a complex application scenario, satisfying every acceptance criterion agreed at project milestones and demonstrated live with scenario walkthroughs.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *an end-to-end agent-assisted software development workflow for a complex application scenario* · condition *using integrated coding agents, MCP tools, and automated evaluation pipelines* · degree *such that the delivered system satisfies every acceptance criterion agreed at milestones, demonstrated live with scenario walkthroughs* · evidence: project_deliverable, presentation · marks share (computed): 21.25%

- CO5.LO1 (L5 ★capstone) Evaluate an end-to-end agent-assisted software development workflow for a complex application scenario using integrated coding agents, MCP tools, and automated evaluation pipelines
- CO5.LO2 (L5) Assess end-to-end agent-assisted workflows using validation pipelines and milestone criteria

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding and basic developer workflows (M1.T1)<br>Coding agents and context engineering configuration (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Trace-diagnosis of sample agent-assisted coding workflow descriptions in pairs. |  |
| 2 | Coding agents and context engineering configuration (M1.T2)<br>Model context protocol integration tasks (M1.T3) | CO1.LO2 | CO1 | Worked configuration exercise mapping context management tools to repository structures. |  |
| 3 | Model context protocol integration tasks (M1.T3)<br>Requirements to executable specifications mapping (M2.T1) | CO1.LO2, CO2.LO2 | CO1, CO2 | Group problem-solving on model context protocol integration failure scenarios. |  |
| 4 | Requirements to executable specifications mapping (M2.T1)<br>Spec-driven development practices and testable artifacts (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Worked mapping of natural language requirements to design templates in small groups. | A:Quiz1 (quiz); A:PA1 released |
| 5 | Spec-driven development practices and testable artifacts (M2.T2)<br>Constructing executable specifications from natural language documents (M2.T3) | CO2.LO1 | CO2 | Peer review of specification-to-testable-artifact mapping documents. | A:ProjM1 released |
| 6 | Constructing executable specifications from natural language documents (M2.T3)<br>Software factories and iterative development loops (M3.T1) | CO2.LO1, CO3.LO1 | CO2, CO3 | Worked trace analysis exercise parsing natural language specifications into executable rules. | A:PA1 due |
| 7 | Software factories and iterative development loops (M3.T1)<br>Loop engineering and operational log examination (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Mid-semester review and problem-solving session on software factory loop mechanics. |  |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Loop engineering and operational log examination (M3.T2)<br>Trace debugging and operational failure analysis (M3.T3) | CO3.LO1, CO3.LO2 | CO3 | Pair-based log examination to differentiate loop failures from syntax errors. | A:Midsem (midsem) |
| 9 | Automated testing suites for AI-generated code (M4.T1) | CO4.LO2 | CO4 | Worked debugging exercise on failed execution traces from automated agent runs. | A:ProjM1 due; A:ProjM2 released |
| 10 | Reliability and performance evaluation criteria (M4.T2) | CO4.LO1 | CO4 | Appraisal and comparative review of automated testing suites for AI-generated code. |  |
| 11 | Deployment criteria and defect rate appraisal (M4.T3) | CO4.LO1 | CO4 | Discussion and criteria mapping for reliability and performance evaluation metrics. |  |
| 12 | Validation pipelines and workflow assessment (M5.T1)<br>Emerging developer tools and milestone criteria (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Review of deployment checklist items and defect rate calculations. |  |
| 13 | Capstone project delivery and live scenario walkthroughs (M5.T3) | CO5.LO1 | CO5 | Capstone integration discussion and final workflow validation check. | A:ProjM2 due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Agent-Assisted Coding Setup** — Configure basic agent-assisted developer workflows and environment settings on a local repository. | CO1.LO2 | Student development machines, software development environments |
| 2 | **Model Context Protocol Integration** — Implement model context protocol integration tasks and verify context configuration in a test project. | CO1.LO2 | Student development machines, access to AI coding tools/APIs |
| 3 | **Advanced Context Protocol Workflows** — Build custom integration tasks using model context protocol configurations to connect external tools. | CO1.LO2 | Student development machines, access to AI coding tools/APIs |
| 4 | **Spec-Driven Development Practice** — Write testable artifacts and execute spec-driven development practices on a sample requirements file. | CO2.LO1 | Student development machines, software development environments |
| 5 | **Executable Specifications from Natural Language** — Construct executable specifications directly from natural language documents using structured templates. | CO2.LO1 | Student development machines, software development environments |
| 6 | **Software Factories and Development Loops** — Implement iterative development loops within a software factory automation framework. | CO3.LO1 | Student development machines, software development environments |
| 7 | **Loop Engineering and Operational Logs** — Examine operational logs from automated loops to identify failure points. | CO3.LO2 | Student development machines, software development environments |
| 8 | **Trace Debugging and Failure Analysis** — Perform trace debugging and operational failure analysis on failed execution runs. | CO3.LO1, CO3.LO2 | Student development machines, software development environments |
| 9 | **Automated Testing Suites for AI Code** — Design and execute automated testing suites specifically targeting AI-generated code repositories. | CO4.LO2 | Student development machines, access to AI coding tools/APIs |
| 10 | **Reliability and Performance Evaluation** — Evaluate reliability and performance metrics of generated artifacts against deployment criteria. | CO4.LO1 | Student development machines, software development environments |
| 11 | **Deployment Criteria and Defect Rate Appraisal** — Appraise defect rates and verify deployment criteria readiness for software components. | CO4.LO1, CO4.LO2 | Student development machines, software development environments |
| 12 | **Validation Pipelines and Milestone Assessment** — Construct validation pipelines and assess end-to-end workflow milestones. | CO5.LO1, CO5.LO2 | Student development machines, access to AI coding tools/APIs |
| 13 | **Capstone Project Walkthroughs** — Conduct live scenario walkthroughs and finalize capstone project deliverables. | CO5.LO1 | Student development machines, access to AI coding tools/APIs |

Infrastructure: Student development machines (available); Access to AI coding tools/APIs (needs_confirmation); Software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W4→W4) | — | tool-use |  |
| assignment | 20.0 | A:PA1 (W4→W6) | — | implement, tool-use, design |  |
| midsem | 20.0 | A:Midsem (W8→W8) | — | analyse-data, written-communication |  |
| project | 25.0 | A:ProjM1 (W5→W9), A:ProjM2 (W9→W13) | — | design, implement, evaluate-critique, teamwork, oral-presentation |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique, written-communication |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 18.0%, CO2 18.25%, CO3 30.0%, CO4 12.5%, CO5 21.25%

## 10. Resource material

Policy: **reading_list** — The course covers emerging AI-native software development, agentic frameworks, and spec-driven workflows where comprehensive traditional textbooks are not yet available; hence a reading list of recent books, book chapters, and peer-reviewed papers is utilized.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Agentic Design Patterns*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T2 |
| reading | Prof Dr Oliver Koch (2026). *From Vibe to Value - How Specification-Driven Development Professionalizes AI Coding*. | 10.2139/ssrn.6453101 | yes | M2.T1, M2.T2 |
| reading | Zhou Keyu, Qing Xiaotian, Zheng Yang (2026). *An Empirical Study on Engineering Modeling Efficiency of Vibe Coding: A Standardized Evaluation Framework for Generative AI-Assisted Programming*. | 10.1109/icet69987.2026.11659181 | yes | M4.T2 |
| reading | Prateek Sharma Kharel, Suman Thapalia (2026). *Assessing the Impact of Ai Vibe Coding on Reviewing and Debugging Ai-generated Code*. | 10.36948/ijfmr.2026.v08i04.85314 | yes | M3.T3 |
| reading | Satej Kumar Sahu (2025). *Megabrains 101: Generative AI and LLMs Unboxed*. | 10.1007/979-8-8688-1609-3_1 | yes | M1.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|---|
| CO1 |  | 3 [3] |  |  | 3 [2] |
| CO2 |  | 3 [3] | 2 [unclaimed] | 2 [unclaimed] | 3 [unclaimed] |
| CO3 | 3 [3] | 2 [unclaimed] |  | 3 [unclaimed] | 2 [unclaimed] |
| CO4 |  | 3 [3] | 3 [unclaimed] | 3 [unclaimed] | 3 [2] |
| CO5 | 3 [unclaimed] | 3 [3] | 1 [unclaimed] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring workflows and tools maps directly to designing and implementing systems using modern tools. (activities: implement, tool-use)
- CO1→PO9: Using advanced model context protocols and coding agents utilizes advanced computing tools. (activities: tool-use)
- CO2→PO4: Constructing executable specifications corresponds to designing applications to meet specific needs. (activities: design, implement)
- CO3→PO3: Analyzing operational failures requires examining and troubleshooting execution traces to solve new software loop issues. (activities: analyse-data)
- CO4→PO4: Evaluating software artifacts against testing suites matches system evaluation needs. (activities: evaluate-critique)
- CO4→PO9: Assessing AI-generated artifacts relates to understanding advanced computing techniques. (activities: evaluate-critique, tool-use)
- CO5→PO4: End-to-end evaluation of workflows directly exercises system evaluation capabilities. (activities: evaluate-critique)
- CO5→PO7: Live scenario walkthroughs require effective verbal communication of technical workflows. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1 |
| CO1.LO2 | L3 | M1.T2, M1.T3 | 1, 2, 3 | A:PA1@L3 |
| CO2.LO1 | L3 | M2.T2, M2.T3 | 4, 5, 6 | A:PA1@L3, A:ProjM1@L3 |
| CO3.LO1 | L4 | M3.T1, M3.T3 | 6, 7, 8 | A:Midsem@L4, A:Endsem@L4 |
| CO4.LO1 | L5 | M4.T2, M4.T3 | 10, 11 | A:ProjM2@L5 |
| CO5.LO1 | L5 | M5.T2, M5.T3 | 12, 13 | A:ProjM2@L5 |
| CO2.LO2 | L2 | M2.T1 | 3, 4 | A:Quiz1@L2 |
| CO3.LO2 | L4 | M3.T2 | 7, 8 | A:Midsem@L4 |
| CO4.LO2 | L5 | M4.T1 | 9 | A:ProjM1@L5 |
| CO5.LO2 | L5 | M5.T1 | 12 | A:Endsem@L5 |

## Appendix C — Modules and topics

**M1 AI-Assisted Coding Workflows and Context Management** (primary CO1)
- M1.T1 AI-assisted coding and basic developer workflows — 2.0 h · LOs CO1.LO1
- M1.T2 Coding agents and context engineering configuration — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Model context protocol integration tasks — 2.0 h · LOs CO1.LO2 · requires M1.T2
**M2 Spec-Driven Development and Requirements Engineering** (primary CO2)
- M2.T1 Requirements to executable specifications mapping — 3.0 h · LOs CO2.LO2 · requires M1.T3
- M2.T2 Spec-driven development practices and testable artifacts — 3.0 h · LOs CO2.LO1 · requires M2.T1
- M2.T3 Constructing executable specifications from natural language documents — 3.0 h · LOs CO2.LO1 · requires M2.T2
**M3 Software Factory Loops and Failure Analysis** (primary CO3)
- M3.T1 Software factories and iterative development loops — 3.0 h · LOs CO3.LO1 · requires M2.T3
- M3.T2 Loop engineering and operational log examination — 3.0 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Trace debugging and operational failure analysis — 2.0 h · LOs CO3.LO1 · requires M3.T2
**M4 Automated Testing, Reliability, and Deployment** (primary CO4)
- M4.T1 Automated testing suites for AI-generated code — 3.0 h · LOs CO4.LO2 · requires M3.T3
- M4.T2 Reliability and performance evaluation criteria — 3.0 h · LOs CO4.LO1 · requires M4.T1
- M4.T3 Deployment criteria and defect rate appraisal — 3.0 h · LOs CO4.LO1 · requires M4.T2
**M5 End-to-End Workflow Assessment and Capstone Integration** (primary CO5)
- M5.T1 Validation pipelines and workflow assessment — 2.0 h · LOs CO5.LO2 · requires M4.T3
- M5.T2 Emerging developer tools and milestone criteria — 1.0 h · LOs CO5.LO1 · requires M5.T1
- M5.T3 Capstone project delivery and live scenario walkthroughs — 3.0 h · LOs CO5.LO1 · requires M5.T2

Schedule: feasible · 39.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 covers mining software repositories and applying broader AI/ML models to general software engineering tasks (such as defect prediction and log analysis), whereas this course focuses on agent-assisted workflows, agent skills, MCP, loop engineering, and hands-on operational practice with coding agents. |
| CSE582 | 0.067 | complementary | CSE582 deals with traditional software product lines, evolution, maintenance, and re-engineering, whereas this course addresses AI-native development and agentic software engineering practices. |
| CSE594A | 0.08 | complementary | CSE594A focuses generally on agentic reasoning for algorithmic, mathematical, and scientific problem-solving, whereas this course focuses specifically on software development, coding agents, and software engineering workflows. |
| CSE581 | 0.034 | superficial | CSE581 covers traditional systems analysis and empirical requirements engineering theories, which shares minimal topical intersection with AI-native spec-driven development. |
| AI501 | 0.034 | superficial | AI501 is a foundational machine learning theory and methodology course, whereas this course focuses on software engineering practices using coding agents and avoids general ML theory. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Research-oriented perspective on evaluating AI impact in software engineering artifacts. Avoid: Heavy reliance on repository mining and statistical bug prediction models rather than modern LLM coding agents.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Foundational concepts of agentic protocols, LLM reasoning, and tool use. Avoid: Mathematical and algorithmic problem-solving focus, shifting instead towards software engineering workflows.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation styles and practical tooling integration. Avoid: Traditional open-source community process focus without modern AI coding assistants.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Agentic Design Patterns' not verified: ['candidate_id not in retrieved candidates'] |
| assessment | VA-MIDSEM | warning | A:Midsem | mid-sem placed in week 8, calendar assumption is after week 7 |
| cos | V11 | warning | CO3 | CO CO3 condition is not visible in the statement text |
| cos | V11 | warning | CO4 | CO CO4 degree is not visible in the statement text |
| cos | V11 | warning | CO5 | CO CO5 condition is not visible in the statement text |
| cos | V11 | warning | CO5 | CO CO5 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO2 | LO CO2.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO2 | LO CO2.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO2 | LO CO3.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO2 | LO CO3.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 degree is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 54.0 h vs budget 39 h (±15%) |

**Repair history**

- cos: errors 2 → 0 · round 1 accepted (2→0)
- los: errors 5 → 0 · round 1 rejected (5→1); round 2 accepted (5→0)
- structure: errors 2 → 0 · round 1 accepted (2→0)
- assessment: errors 7 → 0 · round 1 accepted (7→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Special constraint SC1 requests setting all Course Outcomes to Bloom Level 1 while assessing them with Bloom Level 6 open-ended design projects, which may conflict with alignment rules.
- positioning: SC1: Setting all Course Outcomes to Bloom Level 1 while assessing them exclusively with open-ended design projects (Bloom Level 6) creates a significant pedagogical mismatch that may conflict with standard curriculum guidelines.
- constraints: Course Outcomes definition: The special constraint asks for Course Outcomes to be set to Bloom Level 1 while being assessed at Bloom Level 6, which creates a pedagogical mismatch regarding constructive alignment.
- cos: special_constraints: Special constraint SC1 requests Bloom Level 1 for all COs while simultaneously demanding Bloom Level 6 open-ended design projects in assessments. This output follows the standard IIIT-D 3xx Bloom band [3, 5] and includes L6 to support the project evaluation requirements.
- copo: CO5oral-presentation: Oral presentation is mapped to PO7 in activity_po_map, which supports CO5 via scenario walkthroughs.
- los: SC1 constraint in context: Special constraint SC1 requests setting all Course Outcomes to Bloom Level 1 while assessing them at Bloom Level 6, but the given COs already have assigned Bloom levels 3, 4, and 5. This output follows the provided CO levels while ensuring proper LO decomposition.
- structure: SC1 instruction conflict: Special constraint SC1 asks to set all Course Outcomes to Bloom Level 1 while assessing with Bloom 6 projects, but COs and LOs are frozen in the context data with levels ranging up to 5. The module structure adheres to the provided LO contexts.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress logically from foundational AI-assisted coding and context management in M1 to specification-driven development in M2, operational software factory loops in M3, automated testing and deployment in M4, and finally end-to-end capstone integration in M5, building upon prerequisite software engineering fundamentals from CSE201.
- **assessment rationale:** The assessment mix comprises quizzes, assignments, midsem and endsem examinations, and a project. This combination balances theoretical evaluation through exams with practical, hands-on demonstration of coding agents, executable specifications, and end-to-end workflow assessment aligned with the course outcomes.
- **positioning rationale:** Unlike CSE701 which covers repository mining and general AI/ML models, CSE582 which addresses traditional product lines, CSE594A which focuses on algorithmic problem-solving, CSE581 which covers traditional requirements engineering, or AI501 which is a foundational machine learning theory course, this course specifically focuses on agent-assisted workflows, coding agents, model context protocol, and loop engineering.