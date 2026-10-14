# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-orphan_los` · generated deterministically from the design graph · validator status: **1 errors, 17 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level indicated textually without a specific institutional course code. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with increasingly capable coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. The course is designed for senior undergraduate students and addresses developer workspaces, agent orchestration, specification-driven development, loop engineering, software factories, and pipeline reliability. Students learn to configure AI-assisted coding tools and agent skills, construct executable specifications, analyze loop engineering workflows and coding agent outputs, evaluate automated testing and deployment pipelines, and assess AI-native software development processes. Instruction is delivered through a combination of lectures, tutorials, and laboratory sessions emphasizing hands-on practice, coding assignments, and a multi-module project.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students require solid software engineering and programming fundamentals including automated testing and modular design to effectively evaluate and integrate AI coding tools. |
| desirable | AI501 `[CATALOGUE]` | ML Model Evaluation, Accuracy | Understanding model evaluation and performance metrics helps students better assess the reliability of AI-generated code and agent outputs. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in Software Engineering with an overlap score of 0.185 (above the substantial overlap threshold of 0.15), it focuses broadly on data mining from repositories, defect prediction, and general research literature in AI for SE. The new course specifically targets modern AI-native software development involving coding agents, developer workflows, loop engineering, and context engineering.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure AI-assisted coding tools and agent skills, using an agent orchestration framework, such that at least 80% of the provided test cases pass.** `[CORPUS, USER]`  
verb *configure* · behaviour *AI-assisted coding tools and agent skills* · condition *using an agent orchestration framework* · degree *such that at least 80% of the provided test cases pass* · evidence: programming_assignment, lab_task · marks share (computed): 24.0%

- CO1.LO1 (L1) Identify the basic components of AI-assisted coding tools and developer workspaces
- CO1.LO2 (L3) Configure agent skills and context engineering parameters within an agent orchestration framework
- CO1.LO3 (L3 ★capstone) Configure agent skill parameters using a supplied configuration template within an agent orchestration framework, such that at least 80% of the provided test cases pass

**CO2 (L3, procedural) — Construct executable specifications from natural language requirements, using a specification-driven development tool, justifying each design decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *construct* · behaviour *executable specifications from natural language requirements* · condition *using a specification-driven development tool* · degree *justifying each design decision against at least one stated requirement* · evidence: design_document, programming_assignment · marks share (computed): 18.0%

- CO2.LO1 (L3) Translate natural language requirements into structured intermediate specifications
- CO2.LO2 (L3 ★capstone) Construct executable test cases from natural language requirements, using a specification-driven development tool, with all public tests passing and no warnings from the configured static analyser

**CO3 (L4, metacognitive) — Analyze loop engineering workflows and coding agent outputs, for a supplied software engineering task, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *analyze* · behaviour *loop engineering workflows and coding agent outputs* · condition *for a supplied software engineering task* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, code_review · marks share (computed): 23.0%

- CO3.LO1 (L2) Trace loop engineering workflows and coding agent outputs for a supplied software engineering task
- CO3.LO2 (L4 ★capstone) Analyze coding agent output logs for a supplied software engineering task, identifying at least three distinct failure causes with supporting log evidence

**CO4 (L5, conceptual) — Evaluate automated testing, deployment pipelines, and reliability metrics, using a software factory environment, identifying at least two distinct reliability bottlenecks, each supported by evidence from the runtime artefact.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *automated testing, deployment pipelines, and reliability metrics* · condition *using a software factory environment* · degree *identifying at least two distinct reliability bottlenecks, each supported by evidence from the runtime artefact* · evidence: report, exam_question · marks share (computed): 10.0%

- CO4.LO1 (L1) Identify automated testing and deployment pipeline outputs in a software factory environment
- CO4.LO2 (L5 ★capstone) Evaluate deployment pipeline reliability metrics, in at most 2 pages, citing at least 2 primary sources

**CO5 (L5, metacognitive) — Evaluate an AI-native software development process, given a multi-module application project prompt, justifying each process choice against the reliability metrics agreed at the first milestone.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *an AI-native software development process* · condition *given a multi-module application project prompt* · degree *justifying each process choice against the reliability metrics agreed at the first milestone* · evidence: project_deliverable, presentation · marks share (computed): 25.0%

- CO5.LO1 (L5) Formulate an AI-native software development process plan for a multi-module application project
- CO5.LO2 (L5 ★capstone) Evaluate multi-module integration milestones, demonstrated live, with 2 scenario walkthroughs chosen by the evaluator

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Developer workspaces and AI assistance components (M1.T1) | CO1.LO1 | CO1 | Worked trace-diagnosis of 3 developer workspace configurations, in pairs |  |
| 2 | Agent skills and context engineering parameters (M1.T2) | CO1.LO2 | CO1 | Problem-solving session on resolving conflicting agent skills and context parameter bounds |  |
| 3 | Agent orchestration framework configuration templates (M1.T3) | CO1.LO3 | CO1 | Peer review of 2 agent orchestration configuration templates and error log matching | A:Quiz1 (quiz) |
| 4 | Requirements to structured intermediate specifications (M2.T1) | CO2.LO1 | CO2 | Worked translation exercises converting ambiguous user stories into structured specifications |  |
| 5 | Specification-driven development tools and executable tests (M2.T2)<br>Executable test validation and test runner integration (M2.T3) | CO2.LO2 | CO2 | Trace-diagnosis of 3 failing specification-driven test suites and static analyzer warnings |  |
| 6 | Executable test validation and test runner integration (M2.T3)<br>Loop engineering workflows and log tracing (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Problem-solving on test runner integration issues and loop engineering workflow logs | A:Asg1 (assignment) |
| 7 | Loop engineering workflows and log tracing (M3.T1)<br>Coding agent failure analysis and iterative development (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Mid-term review and joint problem-solving on coding agent output trace logs | A:Midsem (midsem); A:LabEval1 released |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Iterative patching and log-based root cause analysis (M3.T3)<br>Automated testing and deployment pipeline outputs (M4.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Worked root-cause analysis of 3 simulated coding agent patch failures in pairs | A:LabEval1 due |
| 9 | Automated testing and deployment pipeline outputs (M4.T1)<br>Deployment pipeline reliability metrics and evaluation (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Problem-solving session on pipeline reliability metrics calculation and outlier filtering | A:Proj1 released |
| 10 | Deployment pipeline reliability metrics and evaluation (M4.T2)<br>Deployment pipeline reliability benchmarking (M4.T3) | CO4.LO2 | CO4 | Peer critique of deployment pipeline reliability benchmarking reports and primary source citations |  |
| 11 | Deployment pipeline reliability benchmarking (M4.T3)<br>AI-native software development process planning (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Review and refinement of AI-native software development process plans for multi-module projects | A:Report1 (report); A:Proj2 released |
| 12 | AI-native software development process planning (M5.T1)<br>Multi-module integration milestones and scenario walkthroughs (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Dry run of multi-module integration scenario walkthroughs and risk mitigation analysis |  |
| 13 | Final project integration and milestone defense (M5.T3) | CO5.LO2 | CO5 | Final project milestone checklist verification and peer mock defense | A:Proj1 due; A:Proj2 due |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Developer Workspaces Setup** — Install and configure developer workspaces, integrate AI assistance extensions, and verify basic connectivity to AI coding tools. |  | Student development machines, access to AI coding tools/APIs |
| 2 | **Agent Skills and Context Parameters** — Configure agent skills and context engineering parameters within an agent orchestration framework, testing different parameter sets. | CO1.LO2 | Student development machines, software development environments |
| 3 | **Orchestration Framework Configuration** — Apply agent skill parameters using a supplied configuration template within an agent orchestration framework to pass test cases. | CO1.LO3 | Student development machines, software development environments |
| 4 | **Intermediate Specifications** — Translate sample natural language requirements into structured intermediate specifications and validate syntax. | CO2.LO1 | Student development machines, software development environments |
| 5 | **Specification-Driven Development Tools** — Construct executable test cases from natural language requirements using specification-driven development tools and test runners. | CO2.LO2 | Student development machines, software development environments |
| 6 | **Test Runner Integration and Tracing** — Integrate test runners with executable test validation tools and trace loop engineering workflows on sample tasks. | CO2.LO2, CO3.LO1 | Student development machines, software development environments |
| 7 | **Coding Agent Failure Analysis** — Examine coding agent output logs for a supplied software engineering task to identify failure causes. | CO3.LO2 | Student development machines, software development environments |
| 8 | **Log-Based Root Cause Analysis and Pipelines** — Perform iterative patching using log-based root cause analysis and identify automated testing pipeline outputs. | CO3.LO2, CO4.LO1 | Student development machines, software development environments |
| 9 | **Pipeline Outputs and Reliability Metrics** — Analyze automated testing and deployment pipeline outputs and evaluate pipeline reliability metrics. | CO4.LO1, CO4.LO2 | Student development machines, software development environments |
| 10 | **Pipeline Reliability Benchmarking** — Execute deployment pipeline reliability benchmarking tasks and compile comparative evaluation metrics. | CO4.LO2 | Student development machines, software development environments |
| 11 | **Process Planning for Multi-Module Projects** — Draft an AI-native software development process plan for a multi-module application project using templates. | CO5.LO1 | Student development machines, software development environments |
| 12 | **Multi-Module Integration Walkthroughs** — Conduct multi-module integration milestones and test scenario walkthroughs in pairs. | CO5.LO2 | Student development machines, software development environments |
| 13 | **Final Project Integration Defense** — Demonstrate final project integration live with scenario walkthroughs chosen by the evaluator. | CO5.LO2 | Student development machines, software development environments |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3) | — | tool-use | Within the median weight IQR for quizzes [10.0, 18.75], reflecting foundational knowledge assessment. |
| assignment | 20.0 | A:Asg1 (W6→W6) | — | design, implement, tool-use | Falls within the assignment weight IQR [10.0, 25.0], appropriate for practical programming tasks. |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data | In line with the mid-sem weight IQR [20.0, 25.0]. |
| lab | 15.0 | A:LabEval1 (W7→W8) | — | analyse-data, evaluate-critique | Fits within the fallback lab weight IQR [10, 25] for continuous assessment of analytical and review tasks. |
| report | 10.0 | A:Report1 (W11→W11) | — | evaluate-critique, written-communication | Within report weight IQR [5, 20], covering deployment pipeline evaluation. |
| project | 25.0 | A:Proj1 (W9→W13), A:Proj2 (W11→W13) | — | design, implement, evaluate-critique, teamwork, oral-presentation | Within the project weight IQR [20.0, 35.0], covering multi-module system integration over 4+ weeks. |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 24.0%, CO2 18.0%, CO3 23.0%, CO4 10.0%, CO5 25.0%

## 10. Resource material

Policy: **reading_list** — Due to the emerging and fast-moving nature of AI-native software development and coding agents, traditional textbooks are supplemented by recent research articles, conference proceedings, and foundational software engineering references.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Ian Sommerville (2005). *Software Engineering*. | 9780133943030 | yes | M4.T1 |
| reference | Jez Humble, David Farley (2010). *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*. | 9780321670229 | yes | M4.T2 |
| reading | Muhammed Abiodun (2026). *AI-Assisted Software Engineering: Evaluating Copilot, Cursor, and Autonomous AI Agents for Rapid Application Development*. | 10.2139/ssrn.7508618 | yes | M1.T1 |
| reading | Siniša Nešković, Kathrin Kirchner (2026). *Extending AI-Assisted Software Development Beyond Vibe Coding*. | 10.36227/techrxiv.177156350.06379872/v1 | yes | M1.T2 |
| reading | Savitha Ravi, Michael Coblenz (2026). *SPINACH: Inferring Properties of Web Applications for Property-Based Testing*. | 10.1145/3842652.3843198 | yes | M2.T2 |
| reading | Rubel Hassan Mollik, Arup Datta, Anamul Haque Mollah, Wajdi Aljedaani (2025). *RCEGen: A Generative Approach for Automated Root Cause Analysis Using Large Language Models (LLMs)*. | 10.3390/software4040029 | yes | M3.T3 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|---|
| CO1 | 1 [unclaimed] | 2 [2] |  |  | 3 [3] |
| CO2 | 2 [unclaimed] | 2 [3] |  |  | 2 [unclaimed] |
| CO3 | 3 [3] | 3 [unclaimed] |  |  | 3 [unclaimed] |
| CO4 |  | 3 [3] |  | 3 [unclaimed] | 3 [unclaimed] |
| CO5 |  | 3 [3] | 3 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO9: Configuring AI-assisted tools and agent orchestration frameworks directly utilizes advanced computing tools. (activities: tool-use)
- CO1→PO4: Setting up agent skills and tools contributes to implementing application components. (activities: implement)
- CO2→PO4: Constructing executable specifications is a core part of designing systems from requirements. (activities: design)
- CO3→PO3: Analyzing workflows and agent outputs requires adapting diagnostic techniques to solve software engineering failures. (activities: analyse-data)
- CO4→PO4: Evaluating pipelines and reliability metrics directly addresses the evaluation aspect of system engineering. (activities: evaluate-critique)
- CO5→PO4: Evaluating the development process against metrics assesses methodology effectiveness for applications. (activities: evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1, A:Midsem@L1 |
| CO1.LO2 | L3 | M1.T2 | 2 | A:Quiz1@L3 |
| CO1.LO3 | L3 | M1.T3 | 3 | A:Asg1@L3 |
| CO2.LO1 | L3 | M2.T1 | 4 | A:Midsem@L3 |
| CO2.LO2 | L3 | M2.T2, M2.T3 | 5, 6 | A:Asg1@L3 |
| CO3.LO1 | L2 | M3.T1 | 6, 7 | A:Midsem@L2 |
| CO3.LO2 | L4 | M3.T2, M3.T3 | 7, 8 | A:LabEval1@L4 |
| CO4.LO1 | L1 | M4.T1 | 8, 9 | A:Report1@L1 |
| CO4.LO2 | L5 | M4.T2, M4.T3 | 9, 10, 11 | A:Report1@L5 |
| CO5.LO1 | L5 | M5.T1 | 11, 12 | A:Proj1@L5 |
| CO5.LO2 | L5 | M5.T2, M5.T3 | 12, 13 | A:Proj2@L5 |

## Appendix C — Modules and topics

**M1 AI-Assisted Coding and Workspace Configuration** (primary CO1)
- M1.T1 Developer workspaces and AI assistance components — 3.0 h · LOs CO1.LO1
- M1.T2 Agent skills and context engineering parameters — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Agent orchestration framework configuration templates — 3.0 h · LOs CO1.LO3 · requires M1.T2
**M2 Specification-Driven Development and Requirements** (primary CO2)
- M2.T1 Requirements to structured intermediate specifications — 3.0 h · LOs CO2.LO1 · requires M1.T1
- M2.T2 Specification-driven development tools and executable tests — 2.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Executable test validation and test runner integration — 2.0 h · LOs CO2.LO2 · requires M2.T2
**M3 Loop Engineering and Agent Output Analysis** (primary CO3)
- M3.T1 Loop engineering workflows and log tracing — 3.0 h · LOs CO3.LO1 · requires M1.T3
- M3.T2 Coding agent failure analysis and iterative development — 2.0 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Iterative patching and log-based root cause analysis — 2.0 h · LOs CO3.LO2 · requires M3.T2
**M4 Software Factories and Pipeline Reliability Evaluation** (primary CO4)
- M4.T1 Automated testing and deployment pipeline outputs — 3.0 h · LOs CO4.LO1 · requires M3.T2
- M4.T2 Deployment pipeline reliability metrics and evaluation — 3.0 h · LOs CO4.LO2 · requires M4.T1
- M4.T3 Deployment pipeline reliability benchmarking — 2.0 h · LOs CO4.LO2 · requires M4.T2
**M5 AI-Native Software Development Process and Project Integration** (primary CO5)
- M5.T1 AI-native software development process planning — 3.0 h · LOs CO5.LO1 · requires M2.T2
- M5.T2 Multi-module integration milestones and scenario walkthroughs — 2.0 h · LOs CO5.LO2 · requires M5.T1, M4.T2
- M5.T3 Final project integration and milestone defense — 2.0 h · LOs CO5.LO2 · requires M5.T2, M4.T3

Schedule: feasible · 38.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 treats AI in SE from a data mining, predictive, and research perspective, whereas the new course focuses on practical, agent-assisted coding workflows, agent skills, and prompt/context engineering. |
| CSE582 | 0.067 | complementary | CSE582 addresses traditional product line engineering, maintenance, and re-engineering, while the new course addresses AI-driven software factories and automated agentic development loops. |
| CSE594A | 0.08 | complementary | CSE594A covers fundamental agentic reasoning and algorithmic/mathematical problem solving using LLMs, whereas the new course focuses specifically on software engineering workflows and coding tools. |
| CSE581 | 0.034 | superficial | CSE581 covers traditional systems analysis and requirements theory, whereas the new course focuses on spec-driven development using AI agents. |
| CSE201 | 0.017 | superficial | CSE201 provides foundational object-oriented programming and basic unit testing in Java, whereas the new course explores automated testing and evaluation in AI-native developer workflows. |
| AI501 | 0.034 | superficial | AI501 is a core machine learning course teaching statistical models and risk minimization, while the new course applies existing AI tools to software development tasks without teaching foundational machine learning theory. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Literature review structure and project evaluation methodologies. Avoid: Excessive focus on repository mining and historical bug prediction datasets rather than modern generative coding agents.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Concepts of agentic protocols, MCP, and multi-agent collaboration frameworks. Avoid: Deep mathematical and algorithmic reasoning proofs that detract from software engineering workflow application.
- **CSE582** Software Production Evolution and Maintenance — IIIT-D catalogue. Take: Concepts of software product lines and domain-specific requirements engineering adapted for AI code generation. Avoid: Legacy information systems and traditional maintenance models.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| positioning | V14 | error | AI501 | prerequisite AI501 is level 5xx > course level 3xx |
| assessment | VA-PROJ | warning | project | project released in week 9, late in a 13-week semester |
| assessment | VA-REG | warning | K07 | no endsem component although UGREG-2025§6.2 normally schedules one |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO2 | LO CO3.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 33.0 h vs budget 39 h (±15%) |

**Repair history**

- positioning: errors 1 → 1 · round 1 rejected (1→1); round 2 rejected (1→1); round 3 rejected (1→1)
- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 7 → 0 · round 1 accepted (7→5); round 2 accepted (5→0)
- structure: errors 5 → 0 · round 1 accepted (5→1); round 2 rejected (1→2); round 3 accepted (1→0)
- assessment: errors 7 → 0 · round 1 rejected (7→1); round 2 accepted (7→1); round 3 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Instructor requested 3 Learning Outcomes with parent_co set to 'NONE', which violates standard hierarchical mapping rules and should be reviewed.
- constraints: special_constraints: SC1 requests creating Learning Outcomes with no parent CO; this belongs to course outcome mapping rules rather than a schedulable or checkable content/assessment constraint.
- los: SC1: Special constraint SC1 requests creating 3 Learning Outcomes that have no parent CO (set parent_co to 'NONE'). However, structural rule 1 states that each LO has exactly one parent CO. To avoid violating structural rule 1, all LOs have been assigned to valid parent COs, and SC1 cannot be strictly satisfied without violating parent constraints.
- structure: special_constraints: Special constraint SC1 requested creating 3 Learning Outcomes with parent_co set to 'NONE', but the provided LOS context already contains frozen learning outcomes with standard parent CO mappings. No extra unmapped LOs were added.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress logically from basic AI-assisted coding and workspace configuration in Module 1 to specification-driven development in Module 2, loop engineering and agent analysis in Module 3, software factories and pipeline evaluation in Module 4, and finally multi-module project integration in Module 5. This sequence builds upon foundational software engineering and programming concepts from prerequisite courses such as CSE201.
- **assessment rationale:** The assessment mix comprises quizzes, assignments, mid-semester examinations, laboratory work, reports, and a project. This combination aligns with the practical, workflow-oriented learning outcomes by evaluating both theoretical comprehension through examinations and quizzes, and applied competencies through labs, programming assignments, and the milestone-based project.
- **positioning rationale:** Unlike CSE701 which treats AI in software engineering from a data mining and research perspective, CSE582 which focuses on traditional product line maintenance, CSE594A which emphasizes agentic reasoning and algorithms, or AI501 which teaches core machine learning theory, this course specifically focuses on practical agent-assisted coding workflows, developer tools, and software engineering practices in AI-native environments.