# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-excessive_los` · generated deterministically from the design graph · validator status: **8 errors, 7 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM04 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Level is specified as Advanced undergraduate; Course code is not specified | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 4xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. This course is designed for third and fourth-year undergraduate students in the Computer Science and Engineering programme who possess strong programming and software development fundamentals. Upon completing the course, students will be able to configure agent infrastructure and tools, deconstruct feature requests into executable specifications, implement iterative development loops and software factories, assess the reliability and correctness of agent-generated code, and design AI-native software development processes for multi-module application problems. The course is taught through a combination of lectures, tutorials, and practical laboratory sessions, supported by hands-on projects and assignments.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students require strong software development fundamentals, object-oriented concepts, and basic testing skills to effectively build and evaluate AI-assisted software projects. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers aspects of AI in Software Engineering such as automated testing and code review assistance, the new course focuses specifically on modern AI-native software development, agentic workflows, model context protocols (MCP), and human-agent collaborative loops rather than general mining of software repositories or general AI applications in SE.

## 5. Bloom band

L3–L6 · basis: level 4xx band [3,6] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure agent skills, Model Context Protocol servers, and tool integrations, for a provided software development environment, meeting the stated interface specification for every public method.** `[CORPUS, USER]`  
verb *Configure* · behaviour *agent skills, Model Context Protocol servers, and tool integrations* · condition *for a provided software development environment* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment, lab_task · marks share (computed): 16.0%

- CO1.LO1 (L3) Configure agent skills within a provided development environment to enable tool invocation, ensuring correct registration of at least three custom skill functions.
- CO1.LO2 (L3) Configure Model Context Protocol servers for a provided software development environment, verifying successful communication across all defined transport channels.
- CO1.LO3 (L3 ★capstone) Configure tool integrations, for a provided software development environment, meeting the stated interface specification for every public method.

**CO2 (L4, conceptual) — Deconstruct natural language feature requests into executable specifications, using spec-driven development frameworks, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *Deconstruct* · behaviour *natural language feature requests into executable specifications* · condition *using spec-driven development frameworks* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 25.67%

- CO2.LO1 (L2) Classify natural language user stories into functional requirement categories using requirements engineering principles.
- CO2.LO2 (L4 ★capstone) Deconstruct a complex user authentication story into formal Gherkin executable specifications, given an ambiguous product requirements document, justifying each design decision against at least one stated requirement.

**CO3 (L3, procedural) — Implement iterative development loops and software factories, for a collaborative human-agent programming task, with all public tests passing and no warnings from the configured static analyser.** `[CORPUS, USER]`  
verb *Implement* · behaviour *iterative development loops and software factories* · condition *for a collaborative human-agent programming task* · degree *with all public tests passing and no warnings from the configured static analyser* · evidence: programming_assignment, project_deliverable · marks share (computed): 18.0%

- CO3.LO1 (L3) Construct iterative development loops for single-agent tasks, verifying proper execution across at least three test scenarios.
- CO3.LO2 (L3 ★capstone) Implement an automated prompt-test repair loop for a Python microservice, within a pre-configured multi-agent workflow, with all public tests passing and no warnings from the configured static analyser.

**CO4 (L5, procedural) — Assess the reliability and correctness of agent-generated code, using automated testing suites and evaluation harnesses, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *Assess* · behaviour *the reliability and correctness of agent-generated code* · condition *using automated testing suites and evaluation harnesses* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: code_review, report · marks share (computed): 17.0%

- CO4.LO1 (L3) Execute automated testing suites on agent-generated code artifacts to collect execution logs and test metrics.
- CO4.LO2 (L5 ★capstone) Assess the functional correctness and boundary-case handling of an LLM-generated sorting module, using a synthetic fuzz-testing harness, identifying at least three distinct failure causes with supporting log evidence.

**CO5 (L6, metacognitive) — Design an AI-native software development process, for a given multi-module application problem, justifying each design decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *Design* · behaviour *an AI-native software development process* · condition *for a given multi-module application problem* · degree *justifying each design decision against at least one stated requirement* · evidence: project_deliverable, design_document · marks share (computed): 23.33%

- CO5.LO1 (L6) Plan the integration of AI coding agents, testing suites, and development workflows for a multi-module application problem.
- CO5.LO2 (L6 ★capstone) Design an end-to-end pull-request review and patch-generation pipeline, for an open-source web application repository, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Agent skills setup and function registration (M1.T1) | CO1.LO1 | CO1 | Worked trace-diagnosis of 3 function registration setups, in pairs, identifying common configuration errors. | A:PA1 released |
| 2 | Model Context Protocol server configuration (M1.T2) | CO1.LO2 | CO1 | Trace-diagnosis of 2 failing Model Context Protocol server handshake sequences, in pairs. |  |
| 3 | Tool integrations and context engineering (M1.T3) | CO1.LO3 | CO1 | Peer review of interface specifications for tool integrations against stated requirements. | A:PA1 due |
| 4 | Requirements engineering and user story classification (M2.T1) | CO2.LO1 | CO2 | Categorization exercise classifying 10 ambiguous natural language user stories into functional requirements. | A:Quiz1 (quiz) |
| 5 | Spec-driven development and executable Gherkin specifications (M2.T2) | CO2.LO2 | CO2 | Worked conversion of natural language authentication scenarios into Gherkin feature files, in pairs. | A:ProjM1 released |
| 6 | Loop engineering for single-agent tasks (M3.T1) | CO3.LO1 | CO3 | Tracing single-agent execution loops and identifying loop termination bottlenecks. | A:PA2 released |
| 7 | Multi-agent workflows and automated prompt-test repair loops (M3.T2) | CO3.LO2 | CO3 | Debugging multi-agent prompt-test repair traces for a broken microservice implementation. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Automated testing suites and execution log collection (M4.T1) | CO4.LO1 | CO4 | Parsing and analyzing execution logs and test metrics from automated test runs. | A:PA2 due; A:Report1 released; A:ProjM2 released |
| 9 | Fuzz testing, code analysis, and reliability assessment (M4.T2) | CO4.LO2 | CO4 | Analyzing fuzz-testing failure logs and tracing root causes for sorting module boundary failures. | A:ProjM1 due |
| 10 | Architectural planning for multi-module AI workflows (M5.T1) | CO5.LO1 | CO5 | Reviewing and critiquing architectural diagrams for multi-module AI workflow integration. | A:Report1 due; A:ProjFinal released |
| 11 | End-to-end pull-request review and patch-generation pipelines (M5.T2)<br>Patch-generation pipelines and review integration (M5.T3) | CO5.LO2 | CO5 | Evaluating pull-request patch diffs and identifying potential regression issues. | A:ProjM2 due |
| 12 | Patch-generation pipelines and review integration (M5.T3) | CO5.LO2 | CO5 | Dry-run reviews of end-to-end project pipelines against acceptance criteria. |  |
| 13 |  |  |  |  | A:ProjFinal due |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Agent skills setup and function registration** — Students configure agent skills within the provided development environment and register at least three custom skill functions. | CO1.LO1 | Student development machines, software development environments |
| 2 | **Model Context Protocol server configuration** — Students configure Model Context Protocol servers and verify successful communication across defined transport channels. | CO1.LO2 | Student development machines, software development environments |
| 3 | **Tool integrations and context engineering** — Students implement and verify tool integrations meeting interface specifications for public methods. | CO1.LO3 | Student development machines, software development environments |
| 4 | **Requirements classification practice** — Students review requirements engineering classifications and apply user story categories to case studies. | CO2.LO1 | Student development machines |
| 5 | **Spec-driven development and Gherkin specifications** — Students deconstruct user authentication stories into formal Gherkin executable specifications. | CO2.LO2 | Student development machines, software development environments |
| 6 | **Loop engineering for single-agent tasks** — Students construct iterative development loops for single-agent tasks and verify execution across test scenarios. | CO3.LO1 | Student development machines, software development environments |
| 7 | **Multi-agent workflows and prompt-test repair loops** — Students implement automated prompt-test repair loops for a Python microservice within a multi-agent workflow. | CO3.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 8 | **Automated testing suites and execution logs** — Students execute automated testing suites on agent-generated code to collect logs and test metrics. | CO4.LO1 | Student development machines, software development environments |
| 9 | **Fuzz testing and reliability assessment** — Students assess functional correctness and boundary-case handling of a sorting module using a synthetic fuzz-testing harness. | CO4.LO2 | Student development machines, software development environments |
| 10 | **Architectural planning for multi-module workflows** — Students draft architectural integration plans for multi-module AI workflows and testing suites. | CO5.LO1 | Student development machines |
| 11 | **PR review and patch-generation pipelines** — Students design and test end-to-end pull-request review and patch-generation pipelines for open-source repositories. | CO5.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 12 | **Pipeline finalization and integration** — Students finalize patch-generation pipelines and review integration to satisfy acceptance criteria. | CO5.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (needs_confirmation); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W4→W4) | — | analyse-data |  |
| assignment | 20.0 | A:PA1 (W1→W3), A:PA2 (W6→W8) | — | tool-use, implement |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, design |  |
| report | 15.0 | A:Report1 (W8→W10) | — | evaluate-critique, written-communication | Required for assessing advanced evaluation and fuzz-testing skills under CO4. |
| project | 35.0 | A:ProjM1 (W5→W9), A:ProjM2 (W8→W11), A:ProjFinal (W10→W13) | — | design, implement, teamwork, evaluate-critique |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 16.0%, CO2 25.67%, CO3 18.0%, CO4 17.0%, CO5 23.33%

## 10. Resource material

Policy: **mixed** — Because AI-native software development and coding agents are rapidly evolving domains, the course utilizes a mix of established reference textbooks on design patterns and software engineering, alongside recent peer-reviewed conference proceedings and research papers covering agentic design patterns and automated program repair.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reference | Erich Gamma, John Vlissides, Richard Helm, Ralph Johnson (1995). *Design Patterns: Elements of Reusable Object-Oriented Software*. | 9780133052664 | yes | M5.T1 |
| primary | Antonio Gullí (2025). *Agentic Design Patterns*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T1, M3.T1 |
| reading | Noble Saji Mathews, Meiyappan Nagappan (2024). *Test-Driven Development and LLM-based Code Generation*. | 10.1145/3691620.3695527 | yes | M2.T2 |
| reading | Yingling Li, Muxin Cai, Junjie Chen, Yang Xu (2025). *Context-aware prompting for LLM-based program repair*. | 10.1007/s10515-025-00512-w | yes | M3.T2, M5.T2 |
| reading | Ramtin Ehsani, Esteban Parra, Sonia Haiduc, Preetha Chatterjee (2025). *Hierarchical Knowledge Injection for Improving LLM-based Program Repair*. | 10.1109/ase63991.2025.00122 | yes | M4.T2 |
| reading | OpenAI (2025). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M1.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 3 [3] |  |  | 3 [2] |
| CO2 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] |  | 2 [unclaimed] |
| CO3 | 2 [unclaimed] | 3 [3] | – [2] |  | 2 [unclaimed] |
| CO4 |  | 3 [3] |  | 3 [unclaimed] | 3 [2] |
| CO5 |  | 3 [3] | 3 [unclaimed] |  | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring tools and agent skills directly serves the implementation of systems using modern methodologies. (activities: implement, tool-use)
- CO1→PO9: Model Context Protocol servers and agent tools represent advanced computing techniques. (activities: tool-use)
- CO2→PO4: Deconstructing feature requests into specs is a core part of system design using modern tools. (activities: design)
- CO3→PO4: Implementing development loops and software factories directly maps to system implementation. (activities: implement)
- CO3→PO5: Collaborative tasks foster teamwork dynamics, though partially human-agent in this context. (activities: teamwork)
- CO4→PO4: Assessing reliability and correctness corresponds to system evaluation. (activities: evaluate-critique)
- CO4→PO9: Evaluation harnesses and automated testing suites are advanced tool usage. (activities: tool-use)
- CO5→PO4: Designing an AI-native software process is a direct instance of system and methodology design. (activities: design)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1 | 1 | A:PA1@L3, A:Midsem@L3 |
| CO1.LO2 | L3 | M1.T2 | 2 | A:PA1@L3, A:Midsem@L3 |
| CO1.LO3 | L3 | M1.T3 | 3 | A:PA1@L3 |
| CO2.LO1 | L2 | M2.T1 | 4 | A:Quiz1@L2, A:Midsem@L2 |
| CO2.LO2 | L4 | M2.T2 | 5 | A:ProjM1@L4 |
| CO3.LO1 | L3 | M3.T1 | 6 | A:PA2@L3, A:Midsem@L3 |
| CO3.LO2 | L3 | M3.T2 | 7 | A:PA2@L3, A:Midsem@L3 |
| CO4.LO1 | L3 | M4.T1 | 8 | A:PA2@L3, A:Report1@L3 |
| CO4.LO2 | L5 | M4.T2 | 9 | A:Report1@L5 |
| CO5.LO1 | L6 | M5.T1 | 10 | A:ProjM2@L6 |
| CO5.LO2 | L6 | M5.T2, M5.T3 | 11, 12 | A:ProjFinal@L6 |

## Appendix C — Modules and topics

**M1 Agentic Infrastructure and Tooling** (primary CO1)
- M1.T1 Agent skills setup and function registration — 3.0 h · LOs CO1.LO1
- M1.T2 Model Context Protocol server configuration — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Tool integrations and context engineering — 3.0 h · LOs CO1.LO3 · requires M1.T2
**M2 Specification and Requirements Engineering** (primary CO2)
- M2.T1 Requirements engineering and user story classification — 3.0 h · LOs CO2.LO1
- M2.T2 Spec-driven development and executable Gherkin specifications — 3.0 h · LOs CO2.LO2 · requires M2.T1
**M3 Iterative Loops and Software Factories** (primary CO3)
- M3.T1 Loop engineering for single-agent tasks — 3.0 h · LOs CO3.LO1
- M3.T2 Multi-agent workflows and automated prompt-test repair loops — 3.0 h · LOs CO3.LO2 · requires M3.T1
**M4 Reliability Assessment and Testing** (primary CO4)
- M4.T1 Automated testing suites and execution log collection — 3.0 h · LOs CO4.LO1
- M4.T2 Fuzz testing, code analysis, and reliability assessment — 3.0 h · LOs CO4.LO2 · requires M4.T1
**M5 AI-Native Process Design and Capstone Integration** (primary CO5)
- M5.T1 Architectural planning for multi-module AI workflows — 3.0 h · LOs CO5.LO1 · requires M1.T3, M2.T2, M3.T2, M4.T2
- M5.T2 End-to-end pull-request review and patch-generation pipelines — 2.0 h · LOs CO5.LO2 · requires M5.T1
- M5.T3 Patch-generation pipelines and review integration — 2.0 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 34.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 examines data-driven software engineering and research literature on AI in SE, whereas the new course centers on hands-on, agentic development workflows, MCP, and practical tool use. |
| CSE594A | 0.08 | complementary | CSE594A emphasizes agentic reasoning for algorithmic and mathematical problem solving, whereas the new course focuses specifically on software development processes, engineering practices, and developer workflows. |
| CSE582 | 0.067 | superficial | CSE582 deals with software product lines, maintenance, and traditional software re-engineering, whereas the new course addresses AI-native methods and autonomous coding tools. |
| CSE581 | 0.034 | superficial | CSE581 focuses on systems analysis and traditional requirements engineering theory, whereas the new course focuses on spec-driven development using AI coding agents. |
| AI501 | 0.034 | superficial | AI501 is a core machine learning theory course, whereas the new course applies engineering practices and tools without teaching foundational machine learning models. |
| CSE201 | 0.017 | complementary | CSE201 provides foundational object-oriented programming and traditional unit testing, which the new course builds upon by introducing AI-assisted and automated testing workflows. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Literature review standards and assignment structures regarding AI tools in software tasks. Avoid: Focusing purely on repository data mining rather than modern interactive coding agents and developer workflows.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Foundational concepts of agentic protocols such as MCP and tool use. Avoid: Deep focus on algorithmic and mathematical problem solving instead of practical software development.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation structure and collaborative tooling practices (e.g., version control, issue tracking). Avoid: Traditional open-source community governance models that do not involve AI coding agents.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| assessment | V19 | error | A:PA1, M1.T2 | A:PA1 (released week 1) covers topic M1.T2 taught until week 2 |
| assessment | V19 | error | A:PA1, M1.T3 | A:PA1 (released week 1) covers topic M1.T3 taught until week 3 |
| assessment | V19 | error | A:PA2, M3.T2 | A:PA2 (released week 6) covers topic M3.T2 taught until week 7 |
| assessment | V19 | error | A:PA2, M4.T1 | A:PA2 (released week 6) covers topic M4.T1 taught until week 8 |
| assessment | V19 | error | A:Report1, M4.T2 | A:Report1 (released week 8) covers topic M4.T2 taught until week 9 |
| assessment | V23 | error | CO3, BTECH-CSE/PO5 | CO3→BTECH-CSE/PO5 claimed (provisional 2) but no assessed activity evidences it |
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Agentic Design Patterns' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| assessment | VA-REG | warning | K07 | no endsem component although UGREG-2025§6.2 normally schedules one |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 27.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- los: errors 4 → 0 · round 1 accepted (4→0)
- structure: errors 2 → 0 · round 1 accepted (2→0)
- assessment: errors 6 → 6 · round 1 rejected (6→1); round 2 rejected (6→1); round 3 rejected (6→1)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Special constraint SC1 requires exactly 15 Learning Outcomes for the first Course Outcome, which may conflict with standard granular outcomes design practices.
- constraints: cco.special_constraints[0]: The professor requested exactly 15 Learning Outcomes for the first Course Outcome, which is structurally unusual and cannot be mapped to the standard constraint vocabulary.
- los: Hours Budget vs Sum of LO Estimates: The sum of estimated hours across the 11 generated LOs totals 30 lecture hours, 10 tutorial hours, and 22 lab hours, which is slightly below the institutional budget of 39 lecture hours, 13 tutorial hours, and 26 lab hours. This leaves headroom for project-based consultation and open lab sessions.
- structure: special_constraints: Special constraint SC1 asks for exactly 15 Learning Outcomes for CO1, but the provided context for CO1 only contains 3 Learning Outcomes (CO1.LO1, CO1.LO2, CO1.LO3). Since LOs are frozen, the structure proceeds with the provided 3 LOs.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules follow a logical progression from foundational tooling to advanced process design, building upon the mandatory prerequisite course CSE201 which provides software development and unit testing fundamentals.
- **assessment rationale:** The assessment mix comprising quizzes, assignments, mid-semester exams, reports, and a capstone project aligns with the practical, workflow-oriented learning outcomes and emphasis on hands-on coding and evaluation.
- **positioning rationale:** Unlike CSE701 which focuses on data-driven software engineering literature, CSE594A which emphasizes algorithmic reasoning, or traditional software engineering courses like CSE582 and CSE581, this course specifically centres on hands-on agentic development workflows, Model Context Protocol, and practical AI-native engineering practices.