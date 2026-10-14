# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-invalid_prereqs` · generated deterministically from the design graph · validator status: **2 errors, 9 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level specified without a concrete alphanumeric course code. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, focusing on how developers collaborate with coding agents. Designed for third- and fourth-year students, the curriculum addresses how to define intent, engineer context, structure iterative development workflows, and coordinate AI tools. Students will learn to configure agentic coding tools and context protocols for development environments, and translate informal system requirements into executable specifications. Additionally, they will analyze execution traces and loop outputs of AI coding agents to diagnose software failures, and evaluate the reliability of agent-generated test suites. Finally, students will evaluate end-to-end AI-native software development workflows. The course is taught through three hours of lectures, one tutorial hour, and two hours of practical laboratory sessions per week, complemented by a substantial hands-on development project.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | NONEXISTENT101 `[CATALOGUE]` |  | Mandated by special constraint SC1 in the course description. |
| desirable | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm, Collection framework | Provides foundational programming, design, and testing skills required for hands-on software development projects. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — Although CSE701 covers AI in software engineering, its focus is on data mining, defect prediction, and research topics rather than modern AI-native development workflows, coding agents, and agentic software engineering practices.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure agentic coding tools and context engineering protocols for a given development environment, meeting the stated interface specification for every integrated tool.** `[CORPUS, USER]`  
verb *Configure* · behaviour *agentic coding tools and context engineering protocols* · condition *for a given development environment* · degree *meeting the stated interface specification for every integrated tool* · evidence: programming_assignment, lab_task · marks share (computed): 16.0%

- CO1.LO1 (L1) Identify the core components and APIs of agentic coding tools for a given development environment, listing their required configuration parameters.
- CO1.LO2 (L3 ★capstone) Configure the Model Context Protocol server settings and tool permissions for a supplied VS Code development environment, meeting the stated interface specification for every integrated tool.

**CO2 (L3, procedural) — Translate informal system requirements into executable specifications for a supplied software project, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *Translate* · behaviour *informal system requirements into executable specifications* · condition *for a supplied software project* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 15.5%

- CO2.LO1 (L2) Distinguish informal system requirements from formal specifications for a supplied software project, identifying ambiguities in the source text.
- CO2.LO2 (L3 ★capstone) Translate informal user stories into Gherkin feature files for a supplied software project, covering every use case in the supplied requirements document.

**CO3 (L4, procedural) — Analyze the execution traces and loop outputs produced by an AI coding agent for a supplied buggy implementation, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *Analyze* · behaviour *execution traces and loop outputs produced by an AI coding agent* · condition *for a supplied buggy implementation* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, code_review · marks share (computed): 18.5%

- CO3.LO1 (L2) Trace execution logs and loop outputs produced by an AI coding agent for a supplied buggy implementation, identifying control flow paths.
- CO3.LO2 (L4 ★capstone) Analyze execution traces from an Aider coding agent for a supplied buggy Python function, identifying at least three distinct failure causes with supporting log evidence.

**CO4 (L5, conceptual) — Evaluate the reliability and correctness of automated test suites generated by coding agents, justifying each evaluation decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *the reliability and correctness of automated test suites generated by coding agents* · condition *for a given software module* · degree *justifying each evaluation decision against at least one stated requirement* · evidence: design_document, presentation · marks share (computed): 25.0%

- CO4.LO1 (L4) Examine automated test suites generated by coding agents for a given software module, listing coverage metrics and test failures.
- CO4.LO2 (L5 ★capstone) Evaluate the reliability and correctness of unit test suites generated by GitHub Copilot for a given software module, justifying each evaluation decision against at least one stated requirement.

**CO5 (L5, metacognitive) — Evaluate an end-to-end AI-native software development workflow for a given multi-component application, demonstrated live with three scenario walkthroughs chosen by the evaluator.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *an end-to-end AI-native software development workflow* · condition *for a given multi-component application* · degree *demonstrated live, with three scenario walkthroughs chosen by the evaluator* · evidence: project_deliverable, presentation · marks share (computed): 25.0%

- CO5.LO1 (L5) Architect tool workflows, context engineering protocols, and specification methods into a unified plan for a given multi-component application.
- CO5.LO2 (L5 ★capstone) Evaluate the execution performance of an end-to-end AI-native software development workflow for a supplied microservice module, demonstrated live, with 3 scenario walkthroughs chosen by the evaluator.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding tools (M1.T1) | CO1.LO1 | CO1 | Interactive walkthrough of setting up API keys, configuring environment variables, and testing basic LLM API calls in Python. |  |
| 2 | Agentic protocols and framework setup (M1.T2) | CO1.LO2 | CO1 | Group discussion and peer review of MCP server configuration files, troubleshooting common connection and permission errors. | A:Lab1 released |
| 3 | Context engineering and prompt protocols (M1.T3) | CO1.LO2 | CO1 | Worked trace-diagnosis of 3 failing prompt protocols in pairs, optimizing context windows to reduce token usage and API latency. | A:Lab1 due; A:Lab2 (lab) |
| 4 | Requirements engineering (M2.T1) | CO2.LO1 | CO2 | Collaborative analysis of a poorly written requirements document, mapping ambiguous terms to structured specifications. |  |
| 5 | Domain-specific requirements engineering (M2.T2) | CO2.LO2 | CO2 | Live coding session translating complex user stories into Gherkin syntax, focusing on edge cases and background steps. | A:Assignment1 released |
| 6 | Loops (M3.T1) | CO3.LO1 | CO3 | Trace-debugging exercise: analyzing agent loop logs to identify infinite loops and redundant tool calls. | A:Assignment1 due |
| 7 | Assisting code review and code analysis (M3.T2) | CO3.LO2 | CO3 | Reviewing Aider execution traces in small groups, identifying patterns where the agent fails to apply code diffs correctly. | A:Lab3 released; A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Making testing more effective (M4.T1) | CO4.LO1 | CO4 | Mid-semester review session: open Q&A on requirements engineering, agent tracing, and MCP configuration. | A:Lab3 due |
| 9 | Usability and evaluation (M4.T2) | CO4.LO2 | CO4 | Evaluating AI-generated test suites: analyzing code coverage reports and identifying gaps in agent-generated unit tests. | A:Assignment2 released; A:ProjectMilestone1 released |
| 10 | Understanding creativity in software and software development (M5.T1) | CO5.LO1 | CO5 | Design workshop: drawing system architecture diagrams for multi-component AI-native workflows, focusing on tool-to-tool communication. | A:Assignment2 due |
| 11 | Capstone integration and workflow setup (M5.T2)<br>Live evaluation and scenario walkthroughs (M5.T3) | CO5.LO2 | CO5 | Walkthrough of capstone integration requirements, demonstrating how to structure the final microservice module for evaluation. | A:ProjectMilestone1 due |
| 12 | Live evaluation and scenario walkthroughs (M5.T3) | CO5.LO2 | CO5 | Mock scenario walkthroughs: practicing live evaluation steps and handling unexpected agent behaviors under evaluator constraints. | A:ProjectFinal released |
| 13 |  |  |  | Final course debrief: discussing the future of AI-native software engineering and career paths in agentic workflows. | A:ProjectFinal due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Introduction to Agentic Coding Environments** — Set up the local development environment and explore the APIs of common AI-assisted coding tools, verifying connectivity and listing configuration parameters. | CO1.LO1 | VS Code, Python, OpenAI API, Anthropic API |
| 2 | **Model Context Protocol Configuration** — Configure Model Context Protocol (MCP) server settings and tool permissions within VS Code, ensuring integration matches the provided interface specification. | CO1.LO2 | VS Code, MCP Server, Node.js, Python |
| 3 | **Context Engineering and Prompt Protocols** — Implement and test context engineering protocols to optimize prompt context for MCP-enabled tools, verifying tool execution against specifications. | CO1.LO2 | VS Code, MCP Server |
| 4 | **Analyzing Requirements Ambiguities** — Analyze a supplied informal software project requirements document, identifying and documenting at least five ambiguities or contradictions using an AI assistant. | CO2.LO1 | GitHub Copilot, Markdown Editor |
| 5 | **Gherkin Feature File Generation** — Translate informal user stories into executable Gherkin feature files using AI assistance, covering all specified use cases for the target project. | CO2.LO2 | VS Code, Cucumber Extension, AI Coding Agent |
| 6 | **Tracing Agent Execution Logs** — Trace execution logs and loop outputs generated by an AI coding agent on a buggy implementation, mapping out the control flow paths. | CO3.LO1 | Python, Log Analyzer, AI Coding Agent |
| 7 | **Aider Agent Trace Analysis** — Analyze execution traces from an Aider coding agent for a buggy Python function, identifying and documenting three distinct failure causes with log evidence. | CO3.LO2 | Aider, Python, Git |
| 8 | **Mid-Semester Catch-up and Open Lab** — No new lab content. Students use this session to catch up on previous lab exercises, refine their MCP configurations, and prepare for mid-semester evaluations. | CO3.LO2, CO2.LO2 | VS Code, Aider |
| 9 | **Evaluating Copilot Generated Test Suites** — Generate unit test suites using GitHub Copilot for a given module, evaluate their reliability, and justify decisions against requirements. | CO4.LO1, CO4.LO2 | GitHub Copilot, Pytest, Coverage.py |
| 10 | **Architecting AI-Native Workflows** — Design and document a unified workflow plan, integrating tool workflows and context engineering protocols for a multi-component application. | CO5.LO1 | Draw.io, Mermaid.js, Markdown Editor |
| 11 | **Capstone Integration and Workflow Setup** — Set up and integrate the end-to-end AI-native software development workflow for a supplied microservice module, preparing for live evaluation. | CO5.LO2 | Docker, GitHub Actions, AI Coding Agents |
| 12 | **Live Workflow Evaluation and Walkthroughs** — Demonstrate the AI-native workflow live, executing three scenario walkthroughs chosen by the evaluator to evaluate execution performance. | CO5.LO2 | Docker, AI Coding Agents, CLI Tools |
| 13 | **Final Project Review and Submission** — Finalize all project deliverables, document performance evaluations, and submit the complete workflow repository. | CO5.LO2 | Git, GitHub |

Infrastructure: Student development machines (available); Access to AI coding tools/APIs (needs_confirmation); Software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| lab | 15.0 | A:Lab1 (W2→W3), A:Lab2 (W3→W3), A:Lab3 (W7→W8) | — | implement, tool-use, analyse-data |  |
| assignment | 15.0 | A:Assignment1 (W5→W6), A:Assignment2 (W9→W10) | — | design, implement, evaluate-critique, written-communication |  |
| project | 25.0 | A:ProjectMilestone1 (W9→W11), A:ProjectFinal (W12→W13) | — | design, evaluate-critique, oral-presentation |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, tool-use |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 16.0%, CO2 15.5%, CO3 18.5%, CO4 25.0%, CO5 25.0%

## 10. Resource material

Policy: **mixed** — Since AI-native software development is a rapidly evolving field, traditional software engineering and testing textbooks are used as foundational references, supplemented by a reading list of recent research papers and technical documentation for agentic workflows and prompt protocols.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reference | Ian Sommerville (2005). *Software Engineering*. | 9780133943030 | yes | M2.T1 |
| reference | Mauro Pezzè, Mauro Pezze, Michal Young (2007). *Software testing and analysis*. | 9780471455936 | yes | M3.T2, M4.T1 |
| reading | Xi Wang (2022). *A framework for Requirements specification of machine-learning systems*. | 10.18293/seke2022-143 | yes | M2.T2 |
| reading | Fuyuki Ishikawa, Yutaka Matsuno (2020). *Evidence-driven Requirements Engineering for Uncertainty of Machine Learning-based Systems*. | 10.1109/re48521.2020.00046 | yes | M2.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 3 [unclaimed] | 3 [3] |  | 3 [2] |
| CO2 | 2 [unclaimed] | 2 [3] | 2 [unclaimed] | 3 [unclaimed] |
| CO3 | 3 [2] | 3 [unclaimed] |  | 3 [2] |
| CO4 | 3 [unclaimed] | 3 [3] | 2 [1] | 3 [unclaimed] |
| CO5 |  | 3 [3] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring agentic coding tools directly exercises the design and implementation of development environments using modern tools. (activities: implement, tool-use)
- CO1→PO9: Involves applying advanced techniques and tools specific to context engineering. (activities: tool-use)
- CO2→PO4: Translating requirements into executable specifications is a core system design and implementation activity. (activities: design, implement)
- CO3→PO3: Analyzing execution traces requires methodical debugging and problem-solving techniques. (activities: analyse-data)
- CO3→PO9: Analyzes outputs from advanced AI coding agents. (activities: tool-use)
- CO4→PO4: Evaluating test suite reliability directly maps to system evaluation methodologies. (activities: evaluate-critique)
- CO4→PO7: Justification requires clear written documentation of evaluation decisions. (activities: written-communication)
- CO5→PO4: Evaluating complete workflows aligns with system-level evaluation. (activities: evaluate-critique)
- CO5→PO7: Live walkthroughs require effective oral presentation and communication. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Midsem@L1 |
| CO1.LO2 | L3 | M1.T2, M1.T3 | 2, 3 | A:Lab1@L3, A:Lab2@L3, A:Midsem@L3 |
| CO2.LO1 | L2 | M2.T1 | 4 | A:Midsem@L2 |
| CO2.LO2 | L3 | M2.T2 | 5 | A:Assignment1@L3, A:Midsem@L3 |
| CO3.LO1 | L2 | M3.T1 | 6 | A:Lab3@L2, A:Midsem@L2 |
| CO3.LO2 | L4 | M3.T2 | 7 | A:Lab3@L4, A:Midsem@L4, A:Endsem@L4 |
| CO4.LO1 | L4 | M4.T1 | 8 | A:Endsem@L4 |
| CO4.LO2 | L5 | M4.T2 | 9 | A:Assignment2@L5, A:Endsem@L5 |
| CO5.LO1 | L5 | M5.T1 | 10 | A:ProjectMilestone1@L5 |
| CO5.LO2 | L5 | M5.T2, M5.T3 | 11, 12 | A:ProjectFinal@L5 |

## Appendix C — Modules and topics

**M1 Agentic Coding Tools and Protocols** (primary CO1)
- M1.T1 AI-assisted coding tools — 3.0 h · LOs CO1.LO1
- M1.T2 Agentic protocols and framework setup — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Context engineering and prompt protocols — 3.0 h · LOs CO1.LO2 · requires M1.T2
**M2 Specification and Executable Requirements** (primary CO2)
- M2.T1 Requirements engineering — 3.0 h · LOs CO2.LO1
- M2.T2 Domain-specific requirements engineering — 3.0 h · LOs CO2.LO2 · requires M2.T1
**M3 Execution Traces and Failure Analysis** (primary CO3)
- M3.T1 Loops — 3.0 h · LOs CO3.LO1
- M3.T2 Assisting code review and code analysis — 3.0 h · LOs CO3.LO2 · requires M3.T1
**M4 Automated Testing and Reliability Evaluation** (primary CO4)
- M4.T1 Making testing more effective — 3.0 h · LOs CO4.LO1
- M4.T2 Usability and evaluation — 3.0 h · LOs CO4.LO2 · requires M4.T1
**M5 Capstone Workflow Integration and Architecture** (primary CO5)
- M5.T1 Understanding creativity in software and software development — 3.0 h · LOs CO5.LO1 · requires M1.T2, M2.T2
- M5.T2 Capstone integration and workflow setup — 2.0 h · LOs CO5.LO2 · requires M5.T1, M3.T2, M4.T2
- M5.T3 Live evaluation and scenario walkthroughs — 2.0 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 34.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.118 | complementary | CSE701 focuses on data-driven SE, mining repositories, and research literature review, whereas the new course emphasizes practical workflow engineering, coding agents, and prompt/context engineering for application development. |
| CSE581 | 0.062 | complementary | CSE581 covers traditional and agile requirements engineering and design theories, whereas the new course focuses on executable specifications and spec-driven development using AI tools. |
| CSE582 | 0.118 | complementary | CSE582 focuses on product lines, evolution, maintenance, and re-engineering of legacy systems, whereas the new course deals with AI-native loops and agentic software development. |
| CSE594A | 0.077 | complementary | CSE594A is a short 2-credit course focusing broadly on agentic reasoning for algorithmic and mathematical problem solving, whereas this 4-credit course centers specifically on software development workflows, testing, deployment, and developer tooling. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Exploration of modern AI techniques applied to software engineering tasks. Avoid: Heavy focus on mining software repositories and predictive data analytics rather than workflow and agent-based coding.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Concepts of agentic protocols (e.g., MCP) and agentic workflows. Avoid: Exclusive focus on algorithmic, mathematical, and scientific problem-solving agents.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation structure and practical tooling integration. Avoid: Traditional open-source community management without AI agent integration.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| positioning | V14 | error | NONEXISTENT101 | prerequisite NONEXISTENT101 not in the catalogue |
| positioning | V14 | error | NONEXISTENT101 | prerequisite NONEXISTENT101 names no relied-upon topics |
| assessment | VA-PROJ | warning | project | project released in week 9, late in a 13-week semester |
| cos | V11 | warning | CO4 | CO CO4 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO2 | LO CO3.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 degree is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 27.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- positioning: errors 2 → 2 · round 1 rejected (2→2); round 2 rejected (2→2); round 3 rejected (2→2)
- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 9 → 0 · round 1 accepted (9→3); round 2 accepted (3→0)
- structure: errors 2 → 0 · round 1 accepted (2→0)
- assessment: errors 2 → 0 · round 1 accepted (2→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Prerequisite course 'NONEXISTENT101' listed in special constraints does not exist in the institutional knowledge graph.
- positioning: Prerequisite constraint SC1: SC1 requires 'NONEXISTENT101' as a mandatory prerequisite, which does not exist in the course catalogue (violating R3 and R4).
- constraints: Prerequisite course: SC1 specifies a mandatory prerequisite 'NONEXISTENT101', but course catalog validation rules apply and this ID may not exist in the institutional knowledge graph.
- cos: CO1: Prerequisite course 'NONEXISTENT101' mandated by special constraint SC1 does not exist in the institutional catalogue.
- los: hours_budget: Allocated hours total sum to 29 lecture, 10 tutorial, 24 lab hours, which is slightly below the exact targets (39, 13, 26). The remaining hours are distributed across project mentoring sessions and open lab hours not captured in individual LO estimates.
- los: positioning: Prerequisite course NONEXISTENT101 listed in positioning context does not exist institutionally per R3.
- structure: Special constraints: Special constraint SC1 requests listing 'NONEXISTENT101' as a mandatory prerequisite course, which is outside the scope of this module and topic generation task.
- labs: Access to AI coding tools/APIs: Requires paid API credits or licensing for LLM access (OpenAI/Anthropic APIs) which are not explicitly confirmed as funded or provided by the institution.
- resources: M1.T1, M1.T2, M1.T3, M3.T1, M5.T2: There are no textbooks or papers in the current candidate resources that cover agentic coding tools, Model Context Protocol (MCP), prompt protocols, or iterative execution loops. Search requests have been submitted to address this gap.
- resources: SC1: The CCO specifies a critical prerequisite 'NONEXISTENT101' which does not exist in the standard curriculum.
- narrative: NONEXISTENT101: The mandatory prerequisite 'NONEXISTENT101' failed its level check and appears to be a placeholder or invalid course code. This needs to be resolved with the department coordinator.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The course sequence progresses logically from foundational tool configuration to complex integration. It begins with agentic tools and context engineering in Module 1, builds to requirements translation in Module 2, moves to trace analysis and debugging in Module 3, covers automated testing evaluation in Module 4, and culminates in a capstone workflow integration in Module 5. Desirable prerequisite CSE201 ensures students possess the necessary object-oriented programming, collection frameworks, and unit testing background to engage with these advanced modules.
- **assessment rationale:** The assessment mix balances theoretical understanding and practical application. The midsem (20%) and endsem (25%) exams evaluate conceptual knowledge of requirements engineering, trace analysis, and reliability. Hands-on skills are heavily weighted through labs (15%), assignments (15%), and a major project (25%), aligning directly with the course's practical focus. This structure ensures students can configure tools, analyze agent loops, and demonstrate end-to-end workflows in live scenarios as required by the course outcomes.
- **positioning rationale:** This course is complementary to existing IIIT-D offerings. Unlike CSE701, which focuses on data-driven software engineering and repository mining, this course emphasizes practical workflow engineering. It differs from CSE581's focus on traditional and agile design theories by centering on AI-driven executable specifications. While CSE582 targets legacy system maintenance, this course addresses AI-native development loops. Finally, it expands on the algorithmic agent focus of CSE594A by providing a comprehensive, 4-credit treatment of software development workflows.