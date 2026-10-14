# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-missing_assessment` · generated deterministically from the design graph · validator status: **6 errors, 1 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | The level is specified as 'Advanced undergraduate' (typically 3rd or 4th year, level 3 or 4), but the exact course code is '[NOT SPECIFIED]'. | professor |
| — | CONFLICT ['assessment_prefs', 'special_constraints'] | — | Field 12 (Assessment Preferences) lists preferred components (practical assignments, hands-on coding, etc.), whereas Field 13 (Special Constraints) contains a critical instruction stating 'Do not include any assessment components. The assessment list must be empty.' | professor |
| — | CONFLICT ['K17', 'K15'] | — | Special constraint SC1 requires 0 assessment components, but assessment preferences prefer practical assignments. | professor |
| — | CONFLICT ['K17', 'K16'] | — | Special constraint SC1 requires 0 assessment components, but assessment preferences prefer project-based evaluation. | professor |
| — | CONFLICT ['K17', 'UGREG-2025§2'] | — | Special constraint SC1 requires 0 assessment components, which conflicts with the regulation requiring mid-semester and end-semester examinations. | professor |
| — | CONFLICT ['K17', 'UGREG-2025§6.2'] | — | Special constraint SC1 requires 0 assessment components, which conflicts with the regulation stating mid-semester and end-semester exams shall normally be scheduled. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with increasingly capable coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. The curriculum addresses context engineering, the Model Context Protocol, specification-driven development, testing and evaluation loops for non-deterministic code, and multi-agent collaboration workflows. Students will learn to configure AI-assisted developer workflows, decompose software specifications into modular executable specifications, implement automated test suites for agent-generated codebases, and evaluate multi-agent software factory setups. The course is taught through lectures, tutorials, and practical laboratory sessions emphasizing hands-on development and experimentation.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students must have strong programming and software development fundamentals, including testing concepts, before learning AI-assisted workflows. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 (overlap 0.185) covers AI in Software Engineering, it is a Level 7 research-oriented course focusing on applying AI models to SE tasks. The proposed course is a Level 3 course focusing on developer workflows and collaboration with AI coding agents.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure an AI-assisted developer workflow using context engineering and tool integration, given a set of software requirements and an agent orchestration framework, with all public tests passing and no warnings from the configured static analyser.** `[CORPUS, USER]`  
verb *configure* · behaviour *an AI-assisted developer workflow using context engineering and tool integration* · condition *given a set of software requirements and an agent orchestration framework* · degree *with all public tests passing and no warnings from the configured static analyser* · evidence: programming_assignment, code_review · marks share (computed): 25.0%

- CO1.LO1 (L2) Explain the principles of context engineering and Model Context Protocol (MCP) in AI-assisted coding, given a set of API documentations and workflow scenarios, for 3 of 4 short items.
- CO1.LO2 (L3) Implement custom tools and context schemas for an agent orchestration framework, using a provided SDK, producing output that matches the reference for 3 supplied inputs.
- CO1.LO3 (L3 ★capstone) Configure a local development environment with integrated static analysis and automated agent feedback loops, given a set of software requirements and an agent orchestration framework, with all public tests passing and no warnings from the configured static analyser.

**CO2 (L4, procedural) — Decompose a natural language software specification into modular, executable specifications, using a spec-driven development tool, justifying each design decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *decompose* · behaviour *a natural language software specification into modular, executable specifications* · condition *using a spec-driven development tool* · degree *justifying each design decision against at least one stated requirement* · evidence: design_document, lab_task · marks share (computed): 18.75%

- CO2.LO1 (L4) Analyse natural language software requirements to identify core functional modules and dependencies, for a supplied requirements document of at most 5 pages, identifying at least 3 distinct modules, each supported by evidence from the document.
- CO2.LO2 (L3) Translate functional modules into structured, machine-readable schemas, using a spec-driven development tool, meeting the stated interface specification for every public method.
- CO2.LO3 (L4 ★capstone) Deconstruct a multi-page natural language specification into modular, executable test specifications using a spec-driven development tool, justifying each design decision against at least one stated requirement.

**CO3 (L3, procedural) — Implement automated test suites and evaluation loops for an agent-generated codebase, using a modern testing framework, such that at least 90% of the provided test cases pass.** `[CATALOGUE, USER]`  
verb *implement* · behaviour *automated test suites and evaluation loops for an agent-generated codebase* · condition *using a modern testing framework* · degree *such that at least 90% of the provided test cases pass* · evidence: programming_assignment, lab_task · marks share (computed): 23.75%

- CO3.LO1 (L3) Write unit tests and assertions to validate specific functional properties of non-deterministic agent outputs, using a modern testing framework, such that at least 90% of the provided test cases pass.
- CO3.LO2 (L3) Instrument an automated execution and evaluation loop that triggers agent regeneration upon test failures, given a test runner and an agent API, completing all 4 steps of the lab sheet within the session.
- CO3.LO3 (L3 ★capstone) Implement an end-to-end automated evaluation loop that executes tests and triggers agent regeneration, using a modern testing framework, such that at least 90% of the provided test cases pass.

**CO4 (L5, conceptual) — Evaluate the reliability and efficiency of different AI-native development workflows, given a multi-agent software factory setup, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *the reliability and efficiency of different AI-native development workflows* · condition *given a multi-agent software factory setup* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: project_deliverable, report · marks share (computed): 32.5%

- CO4.LO1 (L4) Profile execution metrics including latency, token usage, and cost of multi-agent workflows, given a multi-agent software factory setup, producing output that matches the reference for 3 supplied inputs.
- CO4.LO2 (L4) Diagnose failure modes and bottlenecks in multi-agent collaboration logs, for a supplied execution log of at most 1000 lines, identifying at least 3 distinct failure causes with supporting log evidence.
- CO4.LO3 (L5 ★capstone) Critique the execution efficiency of different AI-native development workflows in a multi-agent software factory setup, in at most 3 pages, citing at least 3 primary sources.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Context engineering principles (M1.T1)<br>Model Context Protocol (MCP) (M1.T2) | CO1.LO1 | CO1 | Worked trace-diagnosis of 2 sample context engineering configurations, in pairs. |  |
| 2 | Model Context Protocol (MCP) (M1.T2)<br>Agent skills and tool use (M1.T3) | CO1.LO1, CO1.LO2 | CO1 | Peer review of tool schema designs and custom agent skill definitions. |  |
| 3 | Agent skills and tool use (M1.T3)<br>Developer workflows and agent orchestration (M1.T4) | CO1.LO2, CO1.LO3 | CO1 | Debugging development environment configurations and static analysis warnings in small groups. | A:Quiz1 (quiz); A:PA1 released |
| 4 | Developer workflows and agent orchestration (M1.T4)<br>Requirements engineering and functional decomposition (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Analyzing a sample requirements document to extract core functional modules and identify module boundaries. |  |
| 5 | Requirements engineering and functional decomposition (M2.T1)<br>Spec-driven development and executable specifications (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Walkthrough and validation of machine-readable schema translations for interface specifications. | A:PA1 due |
| 6 | Spec-driven development and executable specifications (M2.T2)<br>Modular specifications and design decisions (M2.T3) | CO2.LO2, CO2.LO3 | CO2 | Peer critique of executable test specifications against stated functional requirements. | A:Proj1 released |
| 7 | Modular specifications and design decisions (M2.T3)<br>Unit testing non-deterministic agent outputs (M3.T1) | CO2.LO3, CO3.LO1 | CO2, CO3 | Problem-solving session on unit testing strategies for non-deterministic code outputs. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Unit testing non-deterministic agent outputs (M3.T1)<br>Automated execution and evaluation loops (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Tracing test failure scenarios and designing automated evaluation feedback loops. | A:PA2 released |
| 9 | Automated execution and evaluation loops (M3.T2)<br>Automated test suites and agent-generated codebases (M3.T3) | CO3.LO2, CO3.LO3 | CO3 | Reviewing automated test suite coverage reports for agent-generated codebases. | A:Proj1 due |
| 10 | Automated test suites and agent-generated codebases (M3.T3)<br>Execution metrics in multi-agent workflows (M4.T1) | CO3.LO3, CO4.LO1 | CO3, CO4 | Analyzing token usage and cost profiles from multi-agent workflow execution logs. | A:PA2 due; A:Proj2 released |
| 11 | Execution metrics in multi-agent workflows (M4.T1)<br>Failure modes and collaboration log diagnostics (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Collaborative root-cause analysis of failure causes from provided multi-agent execution logs. |  |
| 12 | Failure modes and collaboration log diagnostics (M4.T2)<br>Reliability and efficiency in software factories (M4.T3) | CO4.LO2, CO4.LO3 | CO4 | Critiquing AI-native development workflow efficiencies using primary literature sources. |  |
| 13 | Reliability and efficiency in software factories (M4.T3) | CO4.LO3 | CO4 | Open consultation and project presentation preparation for software factory case studies. | A:Proj2 due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Introduction to Context Engineering and MCP** — Explore basic context window structures and inspect MCP server configurations using local developer tools. | CO1.LO1 | Student development machines, software development environments |
| 2 | **Agent Skills and Tool Use Implementation** — Implement custom tools and context schemas for an agent orchestration framework using the provided SDK. | CO1.LO2 | Student development machines, access to AI coding tools/APIs, software development environments |
| 3 | **Developer Workflows and Agent Orchestration** — Configure a local development environment with integrated static analysis and automated agent feedback loops. | CO1.LO3 | Student development machines, access to AI coding tools/APIs, software development environments |
| 4 | **Requirements Engineering and Functional Decomposition** — Decompose a provided natural language requirements document into core functional modules and dependencies. | CO2.LO1 | Student development machines, software development environments |
| 5 | **Spec-Driven Development** — Translate functional modules into structured, machine-readable schemas using a spec-driven development tool. | CO2.LO2 | Student development machines, software development environments |
| 6 | **Modular Specifications and Design Decisions** — Deconstruct a natural language specification into modular, executable test specifications, justifying design choices. | CO2.LO3 | Student development machines, software development environments |
| 7 | **Mid-Sem Catch-up and Open Lab** — Catch-up session and open lab for mid-semester project preparation; no new lab content introduced. | CO2.LO3 | Student development machines, software development environments |
| 8 | **Unit Testing Non-Deterministic Outputs** — Write unit tests and assertions to validate specific functional properties of non-deterministic agent outputs. | CO3.LO1 | Student development machines, software development environments |
| 9 | **Automated Execution and Evaluation Loops** — Instrument an automated execution and evaluation loop that triggers agent regeneration upon test failures. | CO3.LO2 | Student development machines, access to AI coding tools/APIs, software development environments |
| 10 | **Automated Test Suites and Codebases** — Implement an end-to-end automated evaluation loop that executes tests and triggers agent regeneration. | CO3.LO3 | Student development machines, access to AI coding tools/APIs, software development environments |
| 11 | **Profiling Multi-Agent Execution Metrics** — Profile execution metrics including latency, token usage, and cost of multi-agent workflows. | CO4.LO1 | Student development machines, access to AI coding tools/APIs, software development environments |
| 12 | **Failure Modes and Log Diagnostics** — Diagnose failure modes and bottlenecks in multi-agent collaboration logs for a supplied execution log. | CO4.LO2 | Student development machines, software development environments |
| 13 | **Software Factory Reliability and Wrap-up** — Review reliability and efficiency metrics in multi-agent software factory setups and finalize project artifacts. | CO4.LO3 | Student development machines, software development environments |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3) | — | tool-use |  |
| assignment | 30.0 | A:PA1 (W3→W5), A:PA2 (W8→W10) | — | implement, tool-use | Allocated to practical coding assignments spanning development workflows, spec-driven development, and automated evaluation loops. |
| project | 35.0 | A:Proj1 (W6→W9), A:Proj2 (W10→W13) | — | design, implement, analyse-data, evaluate-critique, written-communication | Substantial open-ended project running over 6 weeks covering requirements decomposition, automated test loops, and multi-agent workflow evaluation. |
| midsem | 10.0 | A:Midsem (W7→W7) | — | analyse-data, design | Standard mid-sem examination assessing foundational analysis and specification translation. |
| endsem | 15.0 | A:Endsem (W13→W13) | — | analyse-data | Comprehensive end-sem examination covering log diagnostics and tool integration. |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 25.0%, CO2 18.75%, CO3 23.75%, CO4 32.5%

## 10. Resource material

Policy: **mixed** — Due to the fast-moving nature of AI-native software development, model context protocols, and agentic workflows, the course utilizes a combination of foundational reference books, framework documentation, and recent research papers.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Agentic Design Patterns*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T3 |
| reading |  (None). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M1.T2 |
| reading | Sarat Piridi (2026). *Connecting to the Model Context Protocol*. | 10.1007/979-8-8688-2888-1_8 | yes | M1.T2 |
| reading | Prof Dr Oliver Koch (2026). *From Vibe to Value - How Specification-Driven Development Professionalizes AI Coding*. | 10.2139/ssrn.6453101 | yes | M2.T2 |
| reading | Krishna Ronanki (2025). *Facilitating Trustworthy Human-Agent Collaboration in LLM-based Multi-Agent System oriented Software Engineering*. | 10.1145/3696630.3728717 | yes | M4.T3 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 |  | 3 [2] |  | 3 [3] |
| CO2 | 3 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [2] |
| CO3 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 3 [2] |
| CO4 | 3 [2] | 2 [3] | 2 [2] | 2 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO9: Configuring an AI-assisted workflow [CORPUS:CO1] directly exercises the ability to use advanced techniques and tools [PROGRAMME:BTECH-CSE/PO9]. (activities: tool-use)
- CO1→PO4: Setting up the developer workflow [CORPUS:CO1] involves implementing a computer-based system using modern tools [PROGRAMME:BTECH-CSE/PO4]. (activities: implement)
- CO2→PO4: Decomposing natural language specifications [CORPUS:CO2] is a core system design activity meeting desired needs [PROGRAMME:BTECH-CSE/PO4]. (activities: design)
- CO2→PO9: Using a spec-driven development tool [CORPUS:CO2] demonstrates the ability to use advanced software engineering tools [PROGRAMME:BTECH-CSE/PO9]. (activities: tool-use)
- CO3→PO4: Implementing automated test suites [CORPUS:CO3] directly contributes to the implementation and evaluation of computer-based systems [PROGRAMME:BTECH-CSE/PO4]. (activities: implement)
- CO3→PO9: Using modern testing frameworks [CORPUS:CO3] demonstrates the application of advanced software testing tools [PROGRAMME:BTECH-CSE/PO9]. (activities: tool-use)
- CO4→PO4: Evaluating the reliability and efficiency of AI-native workflows [CORPUS:CO4] directly maps to the evaluation of computer-based systems [PROGRAMME:BTECH-CSE/PO4]. (activities: evaluate-critique)
- CO4→PO7: Documenting failure causes with supporting log evidence [CORPUS:CO4] exercises written communication skills for technical audiences [PROGRAMME:BTECH-CSE/PO7]. (activities: written-communication)
- CO4→PO3: Analyzing log evidence to identify failure causes [CORPUS:CO4] helps adapt techniques for solving workflow efficiency problems [PROGRAMME:BTECH-CSE/PO3]. (activities: analyse-data)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L2 | M1.T1, M1.T2 | 1, 2 | A:Quiz1@L2 |
| CO1.LO2 | L3 | M1.T3 | 2, 3 | **none** |
| CO1.LO3 | L3 | M1.T4 | 3, 4 | A:PA1@L3 |
| CO2.LO1 | L4 | M2.T1 | 4, 5 | A:Midsem@L4 |
| CO2.LO2 | L3 | M2.T2 | 5, 6 | A:Midsem@L3 |
| CO2.LO3 | L4 | M2.T3 | 6, 7 | A:Proj1@L4 |
| CO3.LO1 | L3 | M3.T1 | 7, 8 | A:PA2@L3 |
| CO3.LO2 | L3 | M3.T2 | 8, 9 | A:PA2@L3 |
| CO3.LO3 | L3 | M3.T3 | 9, 10 | A:Proj1@L3 |
| CO4.LO1 | L4 | M4.T1 | 10, 11 | A:Proj2@L4 |
| CO4.LO2 | L4 | M4.T2 | 11, 12 | A:Endsem@L4 |
| CO4.LO3 | L5 | M4.T3 | 12, 13 | A:Proj2@L5 |

## Appendix C — Modules and topics

**M1 Context Engineering and Model Context Protocol** (primary CO1)
- M1.T1 Context engineering principles — 2.5 h · LOs CO1.LO1
- M1.T2 Model Context Protocol (MCP) — 2.5 h · LOs CO1.LO1 · requires M1.T1
- M1.T3 Agent skills and tool use — 2.5 h · LOs CO1.LO2 · requires M1.T2
- M1.T4 Developer workflows and agent orchestration — 2.5 h · LOs CO1.LO3 · requires M1.T3
**M2 Specification-Driven Development and Requirements Analysis** (primary CO2)
- M2.T1 Requirements engineering and functional decomposition — 3.0 h · LOs CO2.LO1
- M2.T2 Spec-driven development and executable specifications — 3.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Modular specifications and design decisions — 3.0 h · LOs CO2.LO3 · requires M2.T2, M1.T4
**M3 Testing and Evaluation Loops for Non-Deterministic Code** (primary CO3)
- M3.T1 Unit testing non-deterministic agent outputs — 3.0 h · LOs CO3.LO1
- M3.T2 Automated execution and evaluation loops — 3.0 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Automated test suites and agent-generated codebases — 3.0 h · LOs CO3.LO3 · requires M3.T2, M2.T3
**M4 Multi-Agent Collaboration, Profiling, and Workflow Evaluation** (primary CO4)
- M4.T1 Execution metrics in multi-agent workflows — 3.0 h · LOs CO4.LO1 · requires M3.T3
- M4.T2 Failure modes and collaboration log diagnostics — 3.0 h · LOs CO4.LO2 · requires M4.T1
- M4.T3 Reliability and efficiency in software factories — 3.0 h · LOs CO4.LO3 · requires M4.T2

Schedule: feasible · 37.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 focuses on the backend AI models and algorithms used to automate SE tasks (e.g., defect prediction, bug repair), whereas the new course focuses on the developer's interaction, workflow design, and collaboration with these AI tools. |
| CSE594A | 0.08 | complementary | CSE594A focuses on the theoretical reasoning protocols and infrastructure of LLM agents for mathematical and algorithmic problem solving. The new course focuses on the practical application of these agents in software engineering workflows. |
| CSE582 | 0.067 | superficial | CSE582 covers traditional software evolution, maintenance, and product lines. The overlap is limited to high-level software engineering concepts, whereas the new course is entirely AI-native. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: The focus on practical software engineering tasks like automated testing and code refactoring. Avoid: The heavy emphasis on research literature review and deep theoretical AI/ML model training.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: The use of agentic protocols (like MCP) and multi-agent collaboration concepts. Avoid: The focus on mathematical and scientific problem-solving reasoning.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: The highly practical, project-based evaluation structure and focus on modern developer tools (GitHub, etc.). Avoid: The focus on open-source licensing and traditional component integration.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| assessment | V19 | error | A:PA1, M1.T4 | A:PA1 (released week 3) covers topic M1.T4 taught until week 4 |
| assessment | V19 | error | A:PA2, M3.T2 | A:PA2 (released week 8) covers topic M3.T2 taught until week 9 |
| assessment | V19 | error | A:Proj1, M3.T3 | A:Proj1 (due week 9) covers topic M3.T3 taught until week 10 |
| assessment | V9 | error | CO1.LO2 | LO CO1.LO2 (L3) is never assessed at or above its Bloom level |
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Agentic Design Patterns' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| los | V11 | warning | CO4.LO3 | LO CO4.LO3 condition is not visible in the statement text |

**Repair history**

- los: errors 2 → 0 · round 1 accepted (2→0)
- structure: errors 1 → 0 · round 1 accepted (1→0)
- assessment: errors 4 → 4 · round 1 rejected (4→3); round 2 rejected (4→2); round 3 rejected (4→1)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: The special constraint contains an instruction injection attempting to override the assessment preferences. This has been flagged as a conflict and raw data is preserved without executing the instruction.
- positioning: CCO.special_constraints.SC1: SC1 states 'Do not include any assessment components. The assessment list must be empty', which directly contradicts CCO.assessment_prefs which lists preferred assessments like 'Practical assignments' and 'hands-on coding exercises'.
- constraints: CCO.special_constraints[SC1]: The special constraint SC1 explicitly forbids any assessment components, which directly contradicts the course's own assessment preferences (practical assignments, projects) and standard university regulations (UGREG-2025§2, UGREG-2025§6.2) requiring mid-sem and end-sem exams.
- assessment: Constraint K17: Constraint K17 in context specifies that component count must be 0 and assessment list must be empty. However, standard course design requires an assessment blueprint with components summing to 100% and fulfilling CO/PO alignment rules. We have followed the standard blueprint schema and component count rules (3-6 components) to satisfy the instruction prompt and task description.
- narrative: SC1: The CCO special constraint SC1 states that the assessment list must be empty, but the approved graph summary includes standard assessment components (quiz, assignment, project, midsem, endsem). The prose reflects the approved graph summary.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress from foundational context engineering and tool integration to specification-driven development, testing loops for non-deterministic code, and finally multi-agent workflows. This sequence builds upon the mandatory prerequisite CSE201, ensuring students possess software development and testing fundamentals before tackling AI-assisted workflows.
- **assessment rationale:** The assessment mix comprises assignments, a project, quizzes, midsem, and endsem examinations. This blend balances practical capability through hands-on projects and assignments with theoretical and analytical understanding evaluated via examinations and quizzes, aligning directly with the practical workflow orientation of the course outcomes.
- **positioning rationale:** Unlike CSE701 which focuses on backend AI models and algorithms for automated software engineering tasks, or CSE594A which emphasizes theoretical reasoning protocols for algorithmic problem solving, this course specifically targets the developer's interaction, workflow design, and practical collaboration with AI tools. CSE582 covers traditional software evolution and is distinct from this entirely AI-native course.