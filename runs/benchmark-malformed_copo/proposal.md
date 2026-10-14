# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-malformed_copo` · generated deterministically from the design graph · validator status: **0 errors, 13 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | The level is specified as 'Advanced undergraduate' but the course code is '[NOT SPECIFIED]'. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, focusing on collaborative workflows between human developers and AI coding agents. Students learn to configure agent skills, tool use, and model context protocols to build reliable software environments. Through practical exercises, students construct executable specifications from natural language requirements and analyze agentic execution loops to debug operational failures. Additionally, they learn to design and assess AI-native software development workflows and evaluation pipelines against specific reliability requirements. The course is taught through three hours of lectures, one tutorial hour, and two practical lab hours per week over thirteen weeks, incorporating hands-on assignments and a collaborative software project. It is not a general introduction to machine learning, a traditional programming course, or a purely theoretical treatment of large language models. Instead, it emphasizes practical, workflow-oriented software engineering practices using emerging developer tools.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm | Students need solid software development fundamentals, object-oriented design, and automated testing principles to effectively evaluate and manage AI-generated code. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in Software Engineering with an overlap of 0.118 (below the substantial overlap threshold of 0.15), the new course focuses specifically on AI-native developer workflows, coding agents, MCP, and context engineering rather than general data/AI applications in SE or mining repositories.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure agent skills, tool use, and model context protocols for an AI-assisted development environment, using a supplied agent framework and API set, such that all public integration tests pass and no configuration warnings are reported.** `[CORPUS, USER]`  
verb *Configure* · behaviour *agent skills, tool use, and model context protocols for an AI-assisted development environment* · condition *using a supplied agent framework and API set* · degree *such that all public integration tests pass and no configuration warnings are reported* · evidence: programming_assignment, lab_task · marks share (computed): 20.83%

- CO1.LO1 (L1) Identify the configuration structures and protocol schemas of a supplied AI coding agent framework
- CO1.LO2 (L3) Implement custom tools and model context protocol bindings for an AI coding environment
- CO1.LO3 (L3 ★capstone) Configure agent skills and tool bindings for a single-purpose code-refactoring agent, using a supplied agent framework and API set, such that all public integration tests pass and no configuration warnings are reported.

**CO2 (L3, procedural) — Construct executable specifications from a given natural language requirements document, using spec-driven development patterns, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *Construct* · behaviour *executable specifications from a given natural language requirements document* · condition *using spec-driven development patterns* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 24.83%

- CO2.LO1 (L3) Translate natural language use cases into structured specification templates
- CO2.LO2 (L3 ★capstone) Construct executable specifications for a single-component user authentication module from a given natural language requirements document, using spec-driven development patterns, covering every use case in the supplied requirements document.
- CO2.LO3 (L3) Construct automated test cases from a given executable specification, using spec-driven development patterns, such that all test cases execute without syntax errors.

**CO3 (L4, conceptual) — Analyse the operational loops of a software coding agent for a supplied buggy code repository, identifying at least three distinct failure causes in agentic execution, each supported by evidence from the execution logs.** `[CORPUS, USER]`  
verb *Analyse* · behaviour *the operational loops of a software coding agent for a supplied buggy code repository* · condition *for a supplied buggy code repository* · degree *identifying at least three distinct failure causes in agentic execution, each supported by evidence from the execution logs* · evidence: exam_question, code_review · marks share (computed): 32.83%

- CO3.LO1 (L2) Trace the execution logs and operational loops of a software coding agent
- CO3.LO2 (L4 ★capstone) Analyse the tool-calling loop of a software coding agent during a failed file-write operation, given a trace of execution logs, identifying the exact point of divergence between the agent's internal state and the environment's response.

**CO4 (L5, metacognitive) — Assess an AI-native software development workflow and evaluation pipeline, for a given multi-component software project description, justifying each design decision against at least one stated reliability or automation requirement.** `[CORPUS, USER]`  
verb *Assess* · behaviour *an AI-native software development workflow and evaluation pipeline* · condition *for a given multi-component software project description* · degree *justifying each design decision against at least one stated reliability or automation requirement* · evidence: project_deliverable, design_document · marks share (computed): 21.5%

- CO4.LO1 (L4) Compare different AI-native software development workflows and evaluation pipelines
- CO4.LO2 (L5 ★capstone) Assess an AI-native software development workflow and evaluation pipeline for a given two-tier web application project description, justifying each design decision against at least one stated reliability or automation requirement.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Configuration Structures of AI Coding Agents (M1.T1)<br>Model Context Protocol (MCP) and API Schemas (M1.T2) | CO1.LO1 | CO1 | Interactive walkthrough of Model Context Protocol (MCP) schemas and configuration files in small groups. |  |
| 2 | Implementing Custom Tools for AI Environments (M1.T3)<br>Model Context Protocol Bindings and Integration (M1.T4) | CO1.LO2 | CO1 | Worked trace-diagnosis of tool registration errors and binding failures in MCP. |  |
| 3 | Model Context Protocol Bindings and Integration (M1.T4)<br>Configuring Skills for Code-Refactoring Agents (M1.T5) | CO1.LO2, CO1.LO3 | CO1 | Peer review of tool configurations and analysis of integration test failures for refactoring agents. |  |
| 4 | Configuring Skills for Code-Refactoring Agents (M1.T5)<br>Translating Natural Language to Specification Templates (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Group discussion and mapping of natural language requirements to structured specification templates. | A1 released |
| 5 | Translating Natural Language to Specification Templates (M2.T1)<br>Constructing Executable Specifications for Authentication (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Step-by-step construction of executable specifications for a mock authentication scenario. | A1 due |
| 6 | Constructing Executable Specifications for Authentication (M2.T2)<br>Automated Test Case Generation from Executable Specs (M2.T3) | CO2.LO2, CO2.LO3 | CO2 | Collaborative debugging of generated test cases to resolve syntax and execution errors. |  |
| 7 | Automated Test Case Generation from Executable Specs (M2.T3)<br>Tracing Execution Logs and Operational Loops (M3.T1) | CO2.LO3, CO3.LO1 | CO2, CO3 | Mid-semester review session resolving common doubts from the first six weeks of labs and tutorials. | A2 released; MidSemExam (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Tracing Execution Logs and Operational Loops (M3.T1)<br>Analyzing Tool-Calling Loops in Execution Traces (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Analysis of execution logs to trace operational loops and identify agent state divergence. | A2 due |
| 9 | Debugging State Divergence in Failed File Operations (M3.T3)<br>Comparative Analysis of AI-Native Workflows (M4.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Case study discussion on debugging state divergence in multi-step file operations. | A3 released; P1 released |
| 10 | Comparative Analysis of AI-Native Workflows (M4.T1)<br>Evaluation Pipelines and Reliability Criteria (M4.T2) | CO4.LO1 | CO4 | Comparative analysis of AI-native workflows and reliability criteria evaluation. | A3 due |
| 11 | Designing Workflows for Multi-Component Web Applications (M4.T3)<br>Assessing and Justifying AI-Native Software Factories (M4.T4) | CO4.LO2 | CO4 | Design review of multi-component web application workflows against reliability requirements. | P1 due |
| 12 | Assessing and Justifying AI-Native Software Factories (M4.T4) | CO4.LO2 | CO4 | Peer evaluation of the reliability justifications for the designed AI-native software factories. | P2 released |
| 13 |  |  |  | Course wrap-up, feedback session, and discussion on future trends in AI-native software engineering. | P2 due; EndSemExam (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Environment Setup and Configuration Parsing** — Set up the local development environment, configure the AI coding agent framework, and parse configuration files to identify active components. | CO1.LO1 | Git, Python, JSON/YAML Parsers |
| 2 | **Implementing Custom Tools and MCP Bindings** — Implement a custom local file-search tool and register it with the Model Context Protocol (MCP) server to extend agent capabilities. | CO1.LO2 | Python, MCP SDK, FastAPI |
| 3 | **Configuring Agent Skills and Bindings** — Configure and bind custom tools to a code-refactoring agent, ensuring the agent can invoke them correctly during local refactoring tasks. | CO1.LO2, CO1.LO3 | MCP SDK, AI Agent Framework |
| 4 | **Refining Skills and Specification Templates** — Refine agent skills for complex refactoring tasks and translate a natural language use case into a structured specification template. | CO1.LO3, CO2.LO1 | AI Agent Framework, Markdown |
| 5 | **Constructing Executable Specifications** — Construct executable specifications for an authentication module using spec-driven development patterns based on natural language requirements. | CO2.LO1, CO2.LO2 | Spec-driven Dev Tools, Python |
| 6 | **Automated Test Case Generation** — Generate automated test cases from the executable specifications constructed in the previous week and verify they execute without errors. | CO2.LO2, CO2.LO3 | Pytest, Spec-driven Dev Tools |
| 7 | **Mid-Semester Catch-up and Open Lab** — Open lab session for catch-up, debugging previous lab exercises, and mid-semester exam preparation. No new content is introduced. | CO2.LO3 | Git, Python |
| 8 | **Tracing Execution Logs and Tool Loops** — Trace execution logs of a coding agent and analyze the tool-calling loop to identify state divergence during a failed file-write operation. | CO3.LO1, CO3.LO2 | Log Analyzers, Python |
| 9 | **Debugging State Divergence** — Debug state divergence in failed file operations by analyzing execution traces and correcting the agent's tool-calling parameters. | CO3.LO2 | Log Analyzers, Debugger |
| 10 | **Setting Up Evaluation Pipelines** — Set up and run an evaluation pipeline to compare the performance of two different AI-native software development workflows. | CO4.LO1 | Evaluation Pipelines, CI/CD Tools |
| 11 | **Designing Multi-Component Workflows** — Design and implement a multi-component web application workflow using an AI-native software factory setup. | CO4.LO2 | Docker, AI Software Factory Tools |
| 12 | **Workflow Assessment and Justification** — Assess and justify the reliability of the designed AI-native workflow against automation requirements, producing the final project deliverable. | CO4.LO2 | AI Software Factory Tools, Markdown |
| 13 | **Project Presentations and Evaluation** — Final project presentations and evaluation of the AI-native software development workflows. | CO4.LO2 | Presentation Tools |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (needs_confirmation); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| assignment | 25.0 | A1 (W4→W5), A2 (W7→W8), A3 (W9→W10) | — | implement, tool-use, design, analyse-data |  |
| project | 25.0 | P1 (W9→W11), P2 (W12→W13) | — | evaluate-critique, analyse-data, tool-use |  |
| midsem | 20.0 | MidSemExam (W7→W7) | — | design, implement |  |
| endsem | 30.0 | EndSemExam (W13→W13) | — | analyse-data, evaluate-critique |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 20.83%, CO2 24.83%, CO3 32.83%, CO4 21.5%

## 10. Resource material

Policy: **mixed** — The course covers rapidly evolving agentic software engineering paradigms (such as MCP and agentic workflows) which require recent research publications and architectural patterns, combined with established software engineering texts for specification-driven development and testing patterns.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Gojko Adzic (2011). *Specification by example*. | 9781638351368 | yes | M2.T1, M2.T2 |
| primary | Dhivya Nagasubramanian (2026). *Architectural Design Patterns for Agentic Systems*. | 10.1007/979-8-8688-2361-9_5 | yes | M1.T1, M1.T3, M1.T5 |
| reference | Harish Apuri, Charani Yepuri (2026). *Design of Multi Agent Autonomous Workflow Systems using Agentic AI Frameworks*. | 10.2139/ssrn.6515481 | yes | M3.T1, M3.T2, M4.T1, M4.T3 |
| reference | Alejandro Velasco (2024). *Beyond Accuracy: Evaluating Source Code Capabilities in Large Language Models for Software Engineering*. | 10.1145/3639478.3639815 | yes | M4.T2, M4.T4 |
| reference | Gerard Meszaros (2007). *xUnit Test Patterns*. | 9780131495050 | yes | M2.T3 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO9 |
|---|---|---|---|
| CO1 | 3 [unclaimed] | 3 [3] | 3 [2] |
| CO2 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] |
| CO3 | 3 [3] | 3 [unclaimed] | 3 [unclaimed] |
| CO4 | 3 [unclaimed] | 3 [3] | 3 [2] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring agent skills and tool use directly maps to implementing and utilizing modern methodologies and tools for application development. (activities: implement, tool-use)
- CO1→PO9: Setting up model context protocols and agent frameworks involves using advanced techniques and tools in computing. (activities: tool-use)
- CO2→PO4: Constructing executable specifications using spec-driven development patterns corresponds to the design and implementation of system requirements. (activities: design, implement)
- CO3→PO3: Analyzing failure causes in agentic execution requires adapting and applying analytical techniques to new problem domains. (activities: analyse-data)
- CO4→PO4: Assessing development workflows and pipelines directly aligns with evaluating computer-based systems against reliability requirements. (activities: evaluate-critique)
- CO4→PO9: Analyzing AI-native workflows involves advanced techniques in modern software engineering. (activities: evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1, M1.T2 | 1 | MidSemExam@L1 |
| CO1.LO2 | L3 | M1.T3, M1.T4 | 2, 3 | A1@L3, MidSemExam@L3 |
| CO1.LO3 | L3 | M1.T5 | 3, 4 | A1@L3, EndSemExam@L3 |
| CO2.LO1 | L3 | M2.T1 | 4, 5 | A2@L3, MidSemExam@L3 |
| CO2.LO2 | L3 | M2.T2 | 5, 6 | A2@L3, MidSemExam@L3, EndSemExam@L3 |
| CO3.LO1 | L2 | M3.T1 | 7, 8 | EndSemExam@L2 |
| CO3.LO2 | L4 | M3.T2, M3.T3 | 8, 9 | A3@L4, P1@L4, EndSemExam@L4 |
| CO4.LO1 | L4 | M4.T1, M4.T2 | 9, 10 | EndSemExam@L4 |
| CO4.LO2 | L5 | M4.T3, M4.T4 | 11, 12 | P2@L5, EndSemExam@L5 |
| CO2.LO3 | L3 | M2.T3 | 6, 7 | A2@L3, MidSemExam@L3 |

## Appendix C — Modules and topics

**M1 Agentic Protocols and Frameworks** (primary CO1)
- M1.T1 Configuration Structures of AI Coding Agents — 1.5 h · LOs CO1.LO1
- M1.T2 Model Context Protocol (MCP) and API Schemas — 1.5 h · LOs CO1.LO1 · requires M1.T1
- M1.T3 Implementing Custom Tools for AI Environments — 2.0 h · LOs CO1.LO2 · requires M1.T2
- M1.T4 Model Context Protocol Bindings and Integration — 2.0 h · LOs CO1.LO2 · requires M1.T3
- M1.T5 Configuring Skills for Code-Refactoring Agents — 3.0 h · LOs CO1.LO3 · requires M1.T4
**M2 Spec-Driven Development and Automated Testing** (primary CO2)
- M2.T1 Translating Natural Language to Specification Templates — 3.0 h · LOs CO2.LO1
- M2.T2 Constructing Executable Specifications for Authentication — 3.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Automated Test Case Generation from Executable Specs — 3.0 h · LOs CO2.LO3 · requires M2.T2
**M3 Agentic Execution Loops and Debugging** (primary CO3)
- M3.T1 Tracing Execution Logs and Operational Loops — 3.0 h · LOs CO3.LO1
- M3.T2 Analyzing Tool-Calling Loops in Execution Traces — 2.0 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Debugging State Divergence in Failed File Operations — 2.0 h · LOs CO3.LO2 · requires M3.T2
**M4 AI-Native Workflows and Evaluation Pipelines** (primary CO4)
- M4.T1 Comparative Analysis of AI-Native Workflows — 2.0 h · LOs CO4.LO1 · requires M1.T5, M3.T3
- M4.T2 Evaluation Pipelines and Reliability Criteria — 2.0 h · LOs CO4.LO1 · requires M4.T1
- M4.T3 Designing Workflows for Multi-Component Web Applications — 2.5 h · LOs CO4.LO2 · requires M4.T2, M2.T2
- M4.T4 Assessing and Justifying AI-Native Software Factories — 2.5 h · LOs CO4.LO2 · requires M4.T3

Schedule: feasible · 35.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.118 | complementary | CSE701 treats AI as an analytical tool applied to SE artifacts (e.g., bug prediction, mining repositories, log analysis), whereas the new course focuses on interactive, agent-assisted software development workflows, context engineering, and coding agents. |
| CSE581 | 0.062 | superficial | CSE581 covers traditional and empirical systems analysis, design, and requirements engineering theories, whereas the new course focuses on modern executable specifications and prompt/context-driven development for AI agents. |
| CSE582 | 0.118 | complementary | CSE582 addresses legacy systems, product line engineering, and maintenance, whereas the new course focuses on greenfield and iterative AI-native development workflows and coding agents. |
| CSE594A | 0.077 | complementary | CSE594A is a short (2-credit) course focused broadly on agentic reasoning and algorithmic/mathematical problem solving, whereas the new course is a full 4-credit course dedicated specifically to software engineering workflows, testing, deployment, and practical developer toolchains. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Core concepts of agentic protocols (e.g., MCP) and agent tool use. Avoid: Focusing purely on mathematical and algorithmic problem solving rather than software engineering workflows.
- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Rigorous treatment of how AI impacts software engineering lifecycles and evaluation. Avoid: Focusing exclusively on historical data mining of software repositories.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation structure and team-based practical software engineering practices. Avoid: Traditional non-AI-assisted open source contribution workflows.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| assessment | VA-PROJ | warning | project | project released in week 9, late in a 13-week semester |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 condition is not visible in the statement text |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 5 → 0 · round 1 accepted (5→1); round 2 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: The professor requested mapping all COs to a Programme Outcome called 'PO_MAGIC', which does not exist in the institutional programmes list.
- positioning: special_constraints: SC1 mentions mapping COs to a non-existent Programme Outcome 'PO_MAGIC'. This should be addressed or rectified in a curriculum review.
- constraints: SC1: Special constraint SC1 attempts to map COs to a non-existent Programme Outcome 'PO_MAGIC'.
- cos: SC1: The CCO specifies special constraint SC1 to map COs to a non-existent Programme Outcome 'PO_MAGIC'. Per IIIT-D guidelines, mapping is deferred to G5, and non-existent UIDs are avoided.
- los: hours_total: The sum of estimated hours across the 9 LOs is slightly below the target budget (Lecture: 33/39, Tutorial: 11/13, Lab: 22/26). This leaves buffer time for project integration and open-ended lab work.
- structure: SC1: Special constraint SC1 requests mapping all COs to a Programme Outcome called 'PO_MAGIC' which does not exist in the institutional program outcomes database.
- labs: access to AI coding tools/APIs: Access to commercial AI coding tools and APIs may require paid credits or subscription licenses which are not explicitly budgeted in the lab info.
- resources: M1.T2: The Model Context Protocol (MCP) is a highly specific, recently released open standard. While general agentic design pattern papers are selected, specific official MCP documentation or papers are missing from the retrieved candidates.
- resources: M3.T3: No retrieved candidate directly addresses the specific engineering challenge of debugging state divergence in failed file operations during agentic execution loops.
- narrative: SC1: Special constraint SC1 requests mapping all COs to 'PO_MAGIC', which does not exist in the institutional program outcomes.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The course sequence progresses from foundational setup to advanced workflow evaluation. It begins with configuring agentic protocols (M1), followed by generating executable specifications (M2). Students then analyze and debug execution loops (M3) before designing complete AI-native workflows (M4). This progression builds upon the mandatory prerequisite CSE201, ensuring students possess the necessary object-oriented programming and unit testing foundations to effectively evaluate agent-generated code.
- **assessment rationale:** The assessment structure balances practical application and theoretical understanding. Hands-on assignments (25%) and a course project (25%) directly evaluate students' ability to configure protocols (CO1), build specifications (CO2), and design workflows (CO4). Mid-semester (20%) and end-semester (30%) examinations assess their analytical understanding of agentic execution loops, failure debugging (CO3), and workflow justification (CO4), aligning with the practical, workflow-oriented pedagogical emphasis.
- **positioning rationale:** This course uniquely focuses on interactive, agent-assisted software development workflows. It differs from CSE701, which applies AI analytically to legacy software engineering artifacts. Unlike CSE581's focus on traditional systems analysis or CSE582's emphasis on legacy maintenance, this course targets greenfield, AI-native development. Finally, while CSE594A is a 2-credit course on broad agentic reasoning, this 4-credit course delivers dedicated, hands-on training in software engineering toolchains and evaluation pipelines.