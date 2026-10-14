# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-bloom_inconsistencies` · generated deterministically from the design graph · validator status: **1 errors, 2 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level specified without a specific course code. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

Software Development using AI examines modern AI-native software development workflows where developers collaborate with coding agents. The course covers configuring developer environments, Model Context Protocol specifications, agent orchestration frameworks, context engineering, and spec-driven development. For advanced undergraduate computer science students, mastering the design, coordination, and evaluation of human-AI collaborative workflows is essential for modern software engineering practice. Students will learn to implement AI-assisted coding workflows, assess executable specifications from natural language requirements, analyze execution traces of iterative agentic loops to diagnose failures, and evaluate the reliability of AI-generated applications using deployment metrics. The course is delivered through lectures, tutorials, practical laboratory sessions, and a comprehensive development project. It is structured specifically as a workflow-oriented engineering course rather than a general introduction to machine learning or a traditional programming course.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm, Generic programming | Students need strong software development fundamentals, object-oriented design, and unit testing experience to effectively collaborate with coding agents and build reliable software. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in Software Engineering with an overlap of 0.185, its focus is on general data mining of software repositories, defect prediction, and research-oriented AI applications. The new course ('Software Development using AI') specifically targets modern AI-native development, coding agents, MCP, loop engineering, and practical workflow design for AI-assisted coding.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Implement AI-assisted coding workflows and coding agent tool integrations for a given development task, using an agent orchestration framework, such that at least 80% of the provided test cases pass.** `[CORPUS, USER]`  
verb *Implement* · behaviour *AI-assisted coding workflows and coding agent tool integrations* · condition *for a given development task, using an agent orchestration framework* · degree *such that at least 80% of the provided test cases pass* · evidence: programming_assignment · marks share (computed): 16.0%

- CO1.LO1 (L3) Configure AI-assisted coding tools and developer environments for a given software repository, using an agent configuration profile, such that all connection tests pass.
- CO1.LO2 (L3) Apply custom agent skills and tool use definitions for a supplied codebase, using Model Context Protocol specifications, meeting the stated interface specification for every public method.
- CO1.LO3 (L3 ★capstone) Implement agent orchestration framework configurations for a given development task, using supplied API keys, such that at least 80% of the provided test cases pass.

**CO2 (L5, conceptual) — Assess executable specifications from natural language functional requirements for a supplied software project, using context engineering principles, justifying each design choice against stated requirements.** `[CORPUS, USER]`  
verb *Assess* · behaviour *executable specifications from natural language functional requirements* · condition *for a supplied software project, using context engineering principles* · degree *justifying each design choice against stated requirements* · evidence: design_document · marks share (computed): 27.33%

- CO2.LO1 (L3) Write natural language functional requirements for a supplied software project, covering every use case in the supplied requirements document.
- CO2.LO2 (L3) Construct executable specifications from natural language functional requirements, using context engineering principles, justifying each design decision against at least one stated requirement.
- CO2.LO3 (L5 ★capstone) Assess executable specification documents for a supplied software project, using context engineering principles, justifying each design choice against stated requirements.

**CO3 (L4, procedural) — Analyze the output and execution traces of iterative agentic development loops for a supplied buggy implementation, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *Analyze* · behaviour *the output and execution traces of iterative agentic development loops* · condition *for a supplied buggy implementation* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: lab_task, exam_question · marks share (computed): 30.83%

- CO3.LO1 (L2) Trace the execution output of a single iteration loop for a supplied buggy implementation, identifying at least three distinct failure causes with supporting log evidence.
- CO3.LO2 (L4) Diagnose software factory breakdowns within iterative agentic development loops, using execution traces and test logs, identifying at least three distinct failure causes with supporting log evidence.
- CO3.LO3 (L4 ★capstone) Analyze trace log outputs of iterative agentic development loops for a supplied buggy implementation, identifying at least three distinct failure causes with supporting log evidence.

**CO4 (L5, conceptual) — Evaluate the reliability and performance of an AI-generated software application against test coverage and deployment metrics, recommending at least two targeted improvements with justification.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *the reliability and performance of an AI-generated software application* · condition *against test coverage and deployment metrics* · degree *recommending at least two targeted improvements with justification* · evidence: project_deliverable, report · marks share (computed): 25.83%

- CO4.LO1 (L3) Measure test coverage and deployment metrics for a supplied AI-generated software application, producing output that matches the reference for 3 supplied inputs.
- CO4.LO2 (L5) Appraise the reliability and execution metrics of an AI-generated software module against test coverage and deployment thresholds, recommending at least two targeted improvements with justification.
- CO4.LO3 (L5 ★capstone) Evaluate deployment metrics of an AI-generated software release against test coverage and deployment metrics, recommending at least two targeted improvements with justification.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding environments setup (M1.T1)<br>Configuring developer workflows and connection tests (M1.T2) | CO1.LO1 | CO1 | Interactive discussion on configuring API keys and troubleshooting connection failures in developer environments. |  |
| 2 | Configuring developer workflows and connection tests (M1.T2)<br>Model Context Protocol specifications (M2.T1)<br>Custom agent skills and tool use definitions (M2.T2) | CO1.LO1, CO1.LO2 | CO1 | Group exercise mapping a set of public method interfaces to Model Context Protocol specifications. | L:Lab1 (lab) |
| 3 | Custom agent skills and tool use definitions (M2.T2)<br>Agent orchestration framework configurations (M3.T1) | CO1.LO2, CO1.LO3 | CO1 | Walkthrough of configuring agent orchestration parameters and analyzing test case pass rates. |  |
| 4 | Coding agents and software development integration (M3.T2)<br>Natural language functional requirements for software projects (M4.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Drafting and peer-reviewing natural language functional requirements for a sample software project. | A:ProgAssign1 released |
| 5 | Natural language functional requirements for software projects (M4.T1)<br>Requirements to executable specifications mapping (M4.T2)<br>Context engineering principles for software specification (M5.T1) | CO2.LO1, CO2.LO2 | CO2 | Mapping natural language requirements to executable specifications in small groups. | A:ProgAssign1 due |
| 6 | Context engineering principles for software specification (M5.T1)<br>Spec-driven development and design decision justification (M5.T2)<br>Assessing executable specification documents (M6.T1) | CO2.LO2, CO2.LO3 | CO2 | Evaluating design decision justifications in peer-constructed specifications. | A:DesignAssign2 released |
| 7 | Assessing executable specification documents (M6.T1)<br>Design choice evaluation against stated requirements (M6.T2)<br>Iterative development and execution trace analysis (M7.T1) | CO2.LO3, CO3.LO1 | CO2, CO3 | Tracing execution outputs of single iteration loops to identify failure causes with log evidence. | P:Milestone1 released; E:MidSem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Iterative development and execution trace analysis (M7.T1)<br>Identifying failure causes with log evidence (M7.T2)<br>Diagnosing software factory breakdowns (M8.T1) | CO3.LO1, CO3.LO2 | CO3 | Analyzing log evidence to identify failure causes in a buggy implementation. | A:DesignAssign2 due |
| 9 | Diagnosing software factory breakdowns (M8.T1)<br>Execution traces and test log diagnostics (M8.T2)<br>Loop engineering in iterative agentic development (M9.T1) | CO3.LO2, CO3.LO3 | CO3 | Worked trace-diagnosis of failing agentic development runs using test logs. | L:Lab2 (lab); P:Milestone1 due |
| 10 | Loop engineering in iterative agentic development (M9.T1)<br>Advanced trace log output analysis for buggy implementations (M9.T2)<br>Automated testing for AI-generated applications (M10.T1) | CO3.LO3, CO4.LO1 | CO3, CO4 | Analyzing advanced trace log outputs for buggy implementations in pairs. | P:Milestone2 released |
| 11 | Measuring test coverage and deployment metrics (M10.T2)<br>Appraising reliability and execution metrics (M11.T1)<br>ML model evaluation and targeted improvements (M11.T2) | CO4.LO1, CO4.LO2 | CO4 | Appraising reliability and execution metrics against thresholds and proposing improvements. | L:Lab3 (lab); A:Report3 released |
| 12 | Comprehensive evaluation of deployment metrics (M12.T1)<br>Project deliverables and software release appraisal (M12.T2) | CO4.LO3 | CO4 | Evaluating deployment metrics and drafting recommendations for software release improvement. | A:Report3 due; P:Milestone2 due; P:Milestone3 released |
| 13 |  |  |  | Peer review of final project deliverables and software release appraisals. | P:Milestone3 due; E:EndSem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Setting up AI-Assisted Environments** — Configure local development environments with AI coding assistants, set up API keys, and run connection tests to verify integration. | CO1.LO1 | Student development machines, access to AI coding tools/APIs |
| 2 | **Model Context Protocol and Custom Skills** — Define custom agent skills and tools using Model Context Protocol (MCP) specifications for a given codebase, ensuring all public method interfaces are met. | CO1.LO2 | Student development machines, access to AI coding tools/APIs |
| 3 | **Agent Orchestration Configuration** — Configure an agent orchestration framework for a given development task, ensuring at least 80% of the provided test cases pass. | CO1.LO3 | Student development machines, access to AI coding tools/APIs |
| 4 | **Coding Agent Integration** — Integrate a coding agent into a software development workflow to automate code generation and test execution. | CO1.LO3 | Student development machines, access to AI coding tools/APIs |
| 5 | **Context Engineering for Specifications** — Construct executable specifications from natural language requirements using context engineering principles, justifying design decisions. | CO2.LO2 | Student development machines, access to AI coding tools/APIs |
| 6 | **Assessing Executable Specifications** — Assess executable specification documents for a supplied software project, justifying each design choice against stated requirements. | CO2.LO3 | Student development machines, access to AI coding tools/APIs |
| 7 | **Mid-semester Review and Catch-up Lab** — Open lab session for catch-up on previous labs, refining executable specifications, and preparing for the mid-semester evaluation. | CO2.LO3 | Student development machines |
| 8 | **Diagnosing Software Factory Breakdowns** — Diagnose software factory breakdowns within iterative agentic development loops, identifying failure causes using execution traces. | CO3.LO2 | Student development machines, access to AI coding tools/APIs |
| 9 | **Loop Engineering and Trace Analysis** — Analyze trace log outputs of iterative agentic development loops for a buggy implementation to identify three distinct failure causes. | CO3.LO3 | Student development machines, access to AI coding tools/APIs |
| 10 | **Automated Testing for AI Applications** — Measure test coverage and deployment metrics for a supplied AI-generated software application, matching reference outputs. | CO4.LO1 | Student development machines, software development environments |
| 11 | **Measuring Test Coverage and Deployment Metrics** — Run automated tests and measure coverage and deployment metrics for a supplied software application. | CO4.LO1 | Student development machines, software development environments |
| 12 | **Release Evaluation and Deployment Metrics** — Evaluate deployment metrics of an AI-generated software release, recommending targeted improvements with justification. | CO4.LO3 | Student development machines, software development environments |
| 13 | **Final Project Deliverable Submission** — Finalize and submit the AI-generated software release project, including comprehensive deployment metrics and evaluation reports. | CO4.LO3 | Student development machines |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| lab | 15.0 | L:Lab1 (W2→W2), L:Lab2 (W9→W9), L:Lab3 (W11→W11) | — | implement, tool-use, analyse-data |  |
| assignment | 15.0 | A:ProgAssign1 (W4→W5), A:DesignAssign2 (W6→W8), A:Report3 (W11→W12) | — | implement, design, written-communication |  |
| project | 25.0 | P:Milestone1 (W7→W9), P:Milestone2 (W10→W12), P:Milestone3 (W12→W13) | — | design, implement, evaluate-critique, teamwork, written-communication |  |
| midsem | 20.0 | E:MidSem (W7→W7) | — | design, implement |  |
| endsem | 25.0 | E:EndSem (W13→W13) | — | analyse-data, implement |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 16.0%, CO2 27.33%, CO3 30.83%, CO4 25.83%

## 10. Resource material

Policy: **mixed** — As AI-assisted software development is a rapidly evolving field, we combine a foundational reference book on agentic design patterns with recent peer-reviewed literature and preprints on specification-driven development and multi-agent workflows.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Gullí, Antonio. "Agentic Design Patterns." Springer, 2025*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M2.T2, M3.T1, M9.T1 |
| primary | Prof Dr Oliver Koch (2026). *From Vibe to Value - How Specification-Driven Development Professionalizes AI Coding*. | 10.2139/ssrn.6453101 | yes | M4.T1, M4.T2, M5.T1, M5.T2 |
| reference | Yisen Xu (2025). *MUARF: Leveraging Multi-Agent Workflows for Automated Code Refactoring*. | 10.1109/icse-companion66252.2025.00071 | yes | M3.T2, M7.T1 |
| reference | ALEXON GOMES (2025). *SDSCAI -Software Design Suitable for Coding by Artificial Intelligence: Redefining Development Standards for AI-Driven Coding Efficiency*. | 10.2139/ssrn.5223627 | yes | M5.T2, M6.T2 |
| reference | Ian Sommerville (2005). *Software Engineering*. | 9780133943030 | yes | M4.T1, M10.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 3 [3] |  | 2 [unclaimed] | 2 [2] |
| CO2 |  | 3 [3] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] |
| CO3 | 3 [2] | 3 [unclaimed] | 1 [unclaimed] | 1 [unclaimed] | 2 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Directly implements computer applications using modern agent orchestration tools. (activities: implement, tool-use)
- CO1→PO9: Utilizes advanced agentic tools for software workflows. (activities: tool-use)
- CO2→PO4: Focuses on designing and assessing specifications for software systems. (activities: design, evaluate-critique)
- CO3→PO3: Analyzes execution data to diagnose software failures. (activities: analyse-data)
- CO4→PO4: Evaluates application performance and reliability against metrics. (activities: evaluate-critique, written-communication)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1, M1.T2 | 1, 2 | L:Lab1@L3 |
| CO1.LO2 | L3 | M2.T1, M2.T2 | 2, 3 | A:ProgAssign1@L3, E:MidSem@L3 |
| CO1.LO3 | L3 | M3.T1, M3.T2 | 3, 4 | A:ProgAssign1@L3 |
| CO2.LO1 | L3 | M4.T1, M4.T2 | 4, 5 | A:DesignAssign2@L3, E:MidSem@L3 |
| CO2.LO2 | L3 | M5.T1, M5.T2 | 5, 6 | A:DesignAssign2@L3, E:MidSem@L3 |
| CO2.LO3 | L5 | M6.T1, M6.T2 | 6, 7 | P:Milestone1@L5 |
| CO3.LO1 | L2 | M7.T1, M7.T2 | 7, 8 | E:EndSem@L2 |
| CO3.LO2 | L4 | M8.T1, M8.T2 | 8, 9 | L:Lab2@L4, E:EndSem@L4 |
| CO3.LO3 | L4 | M9.T1, M9.T2 | 9, 10 | P:Milestone2@L4 |
| CO4.LO1 | L3 | M10.T1, M10.T2 | 10, 11 | L:Lab3@L3, E:EndSem@L3 |
| CO4.LO2 | L5 | M11.T1, M11.T2 | 11 | A:Report3@L5 |
| CO4.LO3 | L5 | M12.T1, M12.T2 | 12 | P:Milestone3@L5 |

## Appendix C — Modules and topics

**M1 AI-Assisted Environments and Developer Workflows** (primary CO1)
- M1.T1 AI-assisted coding environments setup — 2.0 h · LOs CO1.LO1
- M1.T2 Configuring developer workflows and connection tests — 2.0 h · LOs CO1.LO1 · requires M1.T1
**M2 Model Context Protocol and Custom Agent Skills** (primary CO1)
- M2.T1 Model Context Protocol specifications — 1.5 h · LOs CO1.LO2 · requires M1.T2
- M2.T2 Custom agent skills and tool use definitions — 1.5 h · LOs CO1.LO2 · requires M2.T1
**M3 Agent Orchestration Frameworks and Coding Agents** (primary CO1)
- M3.T1 Agent orchestration framework configurations — 2.0 h · LOs CO1.LO3 · requires M2.T2
- M3.T2 Coding agents and software development integration — 2.0 h · LOs CO1.LO3 · requires M3.T1
**M4 Requirements Analysis and Natural Language Specifications** (primary CO2)
- M4.T1 Natural language functional requirements for software projects — 1.5 h · LOs CO2.LO1
- M4.T2 Requirements to executable specifications mapping — 1.5 h · LOs CO2.LO1 · requires M4.T1
**M5 Context Engineering and Spec-Driven Development** (primary CO2)
- M5.T1 Context engineering principles for software specification — 1.5 h · LOs CO2.LO2 · requires M4.T2
- M5.T2 Spec-driven development and design decision justification — 1.5 h · LOs CO2.LO2 · requires M5.T1
**M6 Assessment of Executable Specifications** (primary CO2)
- M6.T1 Assessing executable specification documents — 1.5 h · LOs CO2.LO3 · requires M5.T2
- M6.T2 Design choice evaluation against stated requirements — 1.5 h · LOs CO2.LO3 · requires M6.T1
**M7 Iterative Development and Execution Tracing** (primary CO3)
- M7.T1 Iterative development and execution trace analysis — 1.5 h · LOs CO3.LO1
- M7.T2 Identifying failure causes with log evidence — 1.5 h · LOs CO3.LO1 · requires M7.T1
**M8 Software Factory Breakdowns and Diagnostics** (primary CO3)
- M8.T1 Diagnosing software factory breakdowns — 1.5 h · LOs CO3.LO2 · requires M7.T2
- M8.T2 Execution traces and test log diagnostics — 1.5 h · LOs CO3.LO2 · requires M8.T1
**M9 Loop Engineering and Trace Analysis** (primary CO3)
- M9.T1 Loop engineering in iterative agentic development — 1.5 h · LOs CO3.LO3 · requires M8.T2
- M9.T2 Advanced trace log output analysis for buggy implementations — 1.5 h · LOs CO3.LO3 · requires M9.T1
**M10 Automated Testing and Deployment Metrics** (primary CO4)
- M10.T1 Automated testing for AI-generated applications — 1.0 h · LOs CO4.LO1
- M10.T2 Measuring test coverage and deployment metrics — 1.0 h · LOs CO4.LO1 · requires M10.T1
**M11 Reliability Appraisal and Recommendations** (primary CO4)
- M11.T1 Appraising reliability and execution metrics — 1.0 h · LOs CO4.LO2 · requires M10.T2
- M11.T2 ML model evaluation and targeted improvements — 1.0 h · LOs CO4.LO2 · requires M11.T1
**M12 Deployment Evaluation and System Refinement** (primary CO4)
- M12.T1 Comprehensive evaluation of deployment metrics — 1.5 h · LOs CO4.LO3 · requires M11.T2
- M12.T2 Project deliverables and software release appraisal — 1.5 h · LOs CO4.LO3 · requires M12.T1

Schedule: feasible · 36.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 focuses on mining software repositories and applying machine learning models to specific SE research problems, whereas this course focuses on practical, workflow-oriented engineering practices using coding agents and LLM tools. |
| CSE582 | 0.067 | superficial | CSE582 deals with traditional software product lines, maintenance, and re-engineering, whereas this course emphasizes AI-driven agentic workflows and tool use. |
| CSE594A | 0.08 | complementary | CSE594A covers agentic reasoning across algorithmic, mathematical, and scientific problems with a 2-credit structure, whereas this course is a comprehensive 4-credit course focused specifically on software development processes and engineering practices. |
| CSE581 | 0.034 | superficial | CSE581 covers traditional systems analysis and requirements engineering theories without AI-native workflow integration. |
| AI501 | 0.034 | superficial | AI501 is a foundational course on machine learning theory and algorithms, whereas this course assumes programming fundamentals and focuses on using AI tools for software engineering. |
| CSE201 | 0.017 | complementary | CSE201 provides foundational object-oriented programming and standard unit testing, which serves as a prerequisite for building reliable software in this course. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Literature review structure and advanced software engineering perspectives. Avoid: Heavy focus on mining software repositories rather than interactive coding agents.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Agentic protocols, tool use, and MCP concepts. Avoid: Purely algorithmic and mathematical problem-solving focus.
- **CSE201** Advanced Programming — IIIT-D catalogue. Take: Standard testing frameworks and software design principles. Avoid: Traditional manual coding workflows without AI assistance.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Gullí, Antonio. "Agentic Design Patterns." Springer, 2025' not verified: ['candidate_id not in retrieved candidates'] |
| los | VB | warning | CO4.LO1 | LO CO4.LO1: claimed Bloom L3 but verb 'measure' is lexicon L5 |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 10 → 0 · round 1 accepted (10→3); round 2 accepted (3→1); round 3 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: The constraint requires setting all Course Outcomes to Bloom Level 1 while assessing them only with open-ended design projects (Bloom 6), which creates a pedagogical mismatch between outcome level and assessment level.
- positioning: Special Constraint SC1: Setting all Course Outcomes to Bloom Level 1 while assessing them only with open-ended design projects (Bloom 6) creates a mismatch in constructive alignment that downstream validation may flag.
- constraints: SC1: Setting Course Outcomes to Bloom Level 1 while assessing them exclusively with Bloom Level 6 projects contradicts standard alignment guidelines in curriculum design.
- cos: SC1: Special constraint SC1 requests setting all COs to Bloom level 1 while assessing them with Bloom level 6 open-ended projects. This contradicts the institution's Bloom band [3,5] and the CO formulation rules requiring Bloom levels to match the cognitive demand of the behaviour and verb. The COs have been set to appropriate levels within the [3,5] band instead.
- los: hours_budget: Calculated total hours (Lecture: 33, Tutorial: 12, Lab: 23) are slightly below the exact targets (39/13/26) due to granular distribution across 12 LOs, but remain well within the 15% tolerance band.
- structure: special_constraints: Special constraint SC1 asks to set all Course Outcomes to Bloom Level 1 while assessing them with open-ended design projects (Bloom 6). However, the frozen COs and LOs in context already define distinct Bloom levels ranging from 2 to 5. The topic structure has been generated strictly from the provided LOs and their Bloom levels.
- resources: M2.T1: No candidate resource in the corpus or retrieved external list directly covers the Model Context Protocol (MCP) specifications.
- resources: M1.T1: The current candidate list lacks practical documentation or textbooks on setting up modern AI-assisted developer environments.
- narrative: SC1: Special constraint SC1 requests setting all Course Outcomes to Bloom Level 1, but the approved course outcomes (CO1-CO4) are formulated at higher cognitive levels (Implement, Assess, Analyze, Evaluate), which better matches the 3rd/4th year BTech target audience.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The module sequence logically progresses from foundational setup to advanced evaluation. It begins with environment configuration and agent skills (M1–M3), moves to specification and context engineering (M4–M6), advances to iterative development and trace diagnostics (M7–M9), and concludes with automated testing and deployment metrics (M10–M12). This flow ensures students master tool integration before designing complex specifications and debugging agentic loops, building directly upon the software development and unit testing fundamentals acquired in CSE201.
- **assessment rationale:** The assessment scheme balances practical application and theoretical understanding. Labs (15%) and assignments (15%) evaluate hands-on tool integration and specification analysis (CO1, CO2). The course project (25%) requires students to collaboratively build, debug, and evaluate a complete AI-assisted application, directly addressing high-level analysis and evaluation outcomes (CO3, CO4). Midsem (20%) and endsem (25%) exams ensure individual accountability and conceptual mastery of loop engineering, context design, and reliability metrics.
- **positioning rationale:** This course fills a distinct niche at IIIT-D. Unlike CSE701, which focuses on mining software repositories and machine learning research, or CSE582 and CSE581, which cover traditional software product lines and requirements engineering, this course is AI-native. It also differs from the 2-credit CSE594A by focusing comprehensively on software engineering workflows rather than general scientific agent reasoning, and builds upon the programming foundations of CSE201 without duplicating basic ML concepts from AI501.