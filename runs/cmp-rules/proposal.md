# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `cmp-rules` · generated deterministically from the design graph · validator status: **0 errors, 4 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate corresponds to a 300-level course (3rd year standing).; Advanced undergraduate corresponds to a 400-level course (4th year elective standing). | professor |
| — | ambiguous: curriculum_context | — | The text is an overarching narrative intended as the answer to Q1 (course positioning).; The text is an unpartitioned block intended to address multiple standard curriculum questions (Q1–Q6) simultaneously without explicit section labels. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-COMMON, BTECH-CSE, BTECH-CSAI, MTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with increasingly capable coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agentic software development processes, focusing on agent environment configuration, requirements decomposition, spec-driven planning, iterative development loops, execution tracing, and automated quality assessment. Designed for senior undergraduate students with strong software development fundamentals, the course enables learners to configure agentic development environments, decompose informal requirements into executable specifications, orchestrate iterative agent-assisted coding workflows, diagnose context-drift and failure causes from execution traces, and evaluate the reliability and maintainability of agent-generated software deliverables. Instruction is delivered through lectures, tutorials, laboratory sessions, and a semester-long project.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students require solid programming proficiency, object-oriented design, and testing fundamentals in order to structure, verify, and operate agent-assisted software development loops. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — Although CSE701 exceeds the substantial overlap threshold (0.185 >= 0.15), it focuses on research literature and empirical mining of software repositories using AI models, whereas the proposed course focuses on practical, hands-on software development workflows using autonomous coding agents and model context protocols.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4), ceilings raised to BL4+ for the IIIT-D template rule; to be refit from corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (BL3, procedural) — Configure an agentic development environment integrating Model Context Protocol (MCP) servers, context engineering assets, and external tool interfaces, for a modular software development task, meeting the stated interface specification for every public tool endpoint.** `[INFERRED, USER]`  
verb *configure* · behaviour *an agentic development environment integrating Model Context Protocol (MCP) servers, context engineering assets, and external tool interfaces* · condition *for a modular software development task* · degree *meeting the stated interface specification for every public tool endpoint* · evidence: programming_assignment, lab_task · marks share (computed): 16.5%

- CO1.LO1 (L2) Explain the role and message exchange patterns of Model Context Protocol (MCP) clients, servers, and tool resources, for three reference IDE configurations, identifying at least two messaging primitives per configuration.
- CO1.LO2 (L3) Construct structured context engineering assets including system prompts and file-context manifests, for a supplied single-service repository, completing all 4 steps of the lab sheet within the session.
- CO1.LO3 (L3 ★capstone) Configure an MCP tool bridge connecting an autonomous coding agent to a local version-control server, for a supplied micro-repository task, producing output that matches the reference for 3 supplied inputs.

**CO2 (BL4, procedural) — Decompose informal software requirements into executable specifications, task plans, and structured context documents for autonomous coding agents, for a supplied multi-tier software feature, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *decompose* · behaviour *informal software requirements into executable specifications, task plans, and structured context documents for autonomous coding agents* · condition *for a supplied multi-tier software feature* · degree *covering every use case in the supplied requirements document* · evidence: design_document, exam_question · marks share (computed): 19.33%

- CO2.LO1 (L4) Analyze informal feature requirements to identify agent execution dependencies and missing context preconditions, for a supplied two-page specification, within 45 minutes.
- CO2.LO2 (L3) Translate user stories into formal executable acceptance specifications with declarative schemas, for a supplied authentication module, covering every use case in the supplied requirements document.
- CO2.LO3 (L4 ★capstone) Decompose an ambiguous user requirement into an atomic execution checklist and input-output test assertions, for a single backend authentication service, justifying each design decision against at least one stated requirement.

**CO3 (BL3, procedural) — Implement iterative agentic development workflows that orchestrate coding agents, tool interactions, and automated feedback loops, for a multi-component software project, such that at least 80% of the provided acceptance test cases pass.** `[USER]`  
verb *implement* · behaviour *iterative agentic development workflows that orchestrate coding agents, tool interactions, and automated feedback loops* · condition *for a multi-component software project* · degree *such that at least 80% of the provided acceptance test cases pass* · evidence: programming_assignment, project_deliverable · marks share (computed): 18.33%

- CO3.LO1 (L3) Execute a closed-loop agent workflow integrating tool invocation and automated compiler error feedback, for a single failing function, producing output that matches the reference for 4 supplied inputs.
- CO3.LO2 (L3) Refactor agent prompt and context injection across successive turn iterations, for a stateful multi-step coding task, completing all 3 steps of the lab sheet within the session.
- CO3.LO3 (L3 ★capstone) Implement a test-driven loop orchestrating an autonomous coding agent to repair failing regressions, for a supplied three-module REST service, with all public tests passing and no warnings from the configured static analyser.

**CO4 (BL4, conceptual) — Diagnose anomalies, regressions, and context-drift failures in agent-assisted coding sessions, from supplied execution traces and automated test outputs, identifying at least three distinct failure causes with supporting log evidence.** `[USER]`  
verb *diagnose* · behaviour *anomalies, regressions, and context-drift failures in agent-assisted coding sessions* · condition *from supplied execution traces and automated test outputs* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: lab_task, code_review · marks share (computed): 27.5%

- CO4.LO1 (L2) Trace execution prompt-response histories and tool call logs, for a supplied failing agent transcript of at most 50 steps, within 30 minutes.
- CO4.LO2 (L4) Differentiate between prompt drift, tool call schema mismatches, and model hallucination errors, from two comparative session traces, identifying at least 3 distinct failure causes, each supported by evidence from the traces.
- CO4.LO3 (L4 ★capstone) Diagnose context poisoning and instruction decay in an agentic refactoring session, from a 40-step interaction log, identifying at least 3 distinct failure causes, each supported by evidence from the log.

**CO5 (BL5, procedural) — Evaluate the reliability, maintainability, and test coverage of agent-generated software deliverables, using automated testing frameworks and code review metrics, justifying each acceptance or rejection decision against at least one stated quality standard.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *the reliability, maintainability, and test coverage of agent-generated software deliverables* · condition *using automated testing frameworks and code review metrics* · degree *justifying each acceptance or rejection decision against at least one stated quality standard* · evidence: code_review, project_deliverable · marks share (computed): 18.33%

- CO5.LO1 (L5) Measure code complexity, test suite line and branch coverage, and security smells in agent-generated pull requests, using automated static analysis reports, completing all 4 steps of the lab sheet within the session.
- CO5.LO2 (L5) Review agent-synthesized unit test suites for edge-case coverage and assertion validity, for a supplied data-structure implementation, identifying at least 3 of the 4 seeded defects, with a proposed fix for each.
- CO5.LO3 (L5 ★capstone) Evaluate the architectural soundness and edge-case test completeness of an agent-generated pull request, using static analysis reports and mutation test scores, justifying each acceptance or rejection decision against at least one stated quality standard.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Model Context Protocol architecture and message exchange patterns (M1.T1)<br>Tool endpoint schemas and IDE runtime integration (M1.T2) | CO1.LO1 | CO1 | Pair analysis of two sample Model Context Protocol trace transcripts, mapping message exchange primitives to client-server sequence diagrams. |  |
| 2 | Structured prompt assets and file-context manifests (M1.T3)<br>Autonomous agent tool bridges and version control integration (M1.T4) | CO1.LO2, CO1.LO3 | CO1 | Worked construction and peer review of file-context manifests for a two-tier microservice repository. |  |
| 3 | Autonomous agent tool bridges and version control integration (M1.T4)<br>Informal requirement deconstruction and dependency mapping (M2.T1)<br>Context precondition extraction and boundary analysis (M2.T2) | CO1.LO3, CO2.LO1 | CO1, CO2 | Deconstruction of an ambiguous two-page feature specification into execution dependencies and missing context preconditions in small groups. | A:Assign1 released; A:Lab1 (lab) |
| 4 | Context precondition extraction and boundary analysis (M2.T2)<br>Declarative acceptance specifications and schema definition (M2.T3) | CO2.LO1, CO2.LO2 | CO2 | Collaborative translation of three informal user stories into declarative JSON schema acceptance specifications with boundary constraints. | A:Assign1 due |
| 5 | Atomic task planning and input-output test assertion generation (M2.T4)<br>Compiler and linter error-driven automated repair loops (M3.T1) | CO2.LO3, CO3.LO1 | CO2, CO3 | Decomposition of authentication user stories into atomic task checklists and derivation of four input-output test assertions per task. |  |
| 6 | Compiler and linter error-driven automated repair loops (M3.T1)<br>Multi-turn context management and prompt refactoring (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Step-by-step diagnostic tracing of compiler and linter error cascades from three failing automated code repair loops. | A:ProjM1 released |
| 7 | Multi-turn context management and prompt refactoring (M3.T2)<br>Test-driven agent orchestration and regression repair (M3.T3) | CO3.LO2, CO3.LO3 | CO3 | Worked review and trace-diagnosis of multi-turn context degradation and prompt refactoring strategies across prior session logs. | A:MidSem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Test-driven agent orchestration and regression repair (M3.T3)<br>Prompt-response transcript tracing and tool call log analysis (M4.T1)<br>Failure taxonomy: prompt drift, schema mismatch, and hallucination (M4.T2) | CO3.LO3, CO4.LO1, CO4.LO2 | CO3, CO4 | Collaborative trace-diagnosis of three failing agent execution logs, categorising errors into prompt drift and tool call schema mismatches. | A:ProjM1 due; A:ProjM2 released |
| 9 | Failure taxonomy: prompt drift, schema mismatch, and hallucination (M4.T2)<br>Context poisoning and instruction decay diagnostics (M4.T3) | CO4.LO2, CO4.LO3 | CO4 | Comparative analysis of paired session transcripts to isolate hallucinated parameters versus schema mismatches with supporting log evidence. | A:Assign2 released |
| 10 | Context poisoning and instruction decay diagnostics (M4.T3)<br>Automated static analysis and code complexity measurement (M5.T1) | CO4.LO3, CO5.LO1 | CO4, CO5 | Root-cause diagnosis of instruction decay and context poisoning across a 40-step agent refactoring transcript in pairs. | A:Lab2 (lab); A:ProjM2 due |
| 11 | Automated static analysis and code complexity measurement (M5.T1)<br>Edge-case defect detection in agent-synthesized test suites (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Worked calculation and critique of code complexity metrics and test suite branch coverage reports for agent-generated PRs. | A:Assign2 due |
| 12 | Architectural soundness appraisal and pull request review criteria (M5.T3) | CO5.LO3 | CO5 | Structured evaluation of two competing agent-generated pull requests against architectural soundness and mutation test quality standards. | A:Lab3 (lab); A:ProjM3 released |
| 13 |  |  |  | Comprehensive review and walkthrough of end-to-end pull request evaluation criteria, mutation testing trade-offs, and final exam preparation. | A:EndSem (endsem); A:ProjM3 due |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **MCP Environment Setup and Runtime Tool Inspection** — Configure local IDE runtime environment to communicate with reference Model Context Protocol endpoints, verify JSON-RPC message exchanges, and inspect tool discovery payloads. | CO1.LO1 | Student development machines, software development environments |
| 2 | **Context Engineering and Manifest Generation** — Construct structured context engineering assets including system prompts and file-context manifests for a single-service repository, validating against the four-step lab specification. | CO1.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 3 | **MCP Version Control Tool Bridge Integration** — Configure an MCP tool bridge connecting an autonomous coding agent to a local version-control repository, executing commit and branch operations across three reference tasks. | CO1.LO3 | Student development machines, software development environments, access to AI coding tools/APIs |
| 4 | **Declarative Acceptance Schemas and Test Fixtures** — Translate informal requirements into declarative acceptance schemas and formal test fixtures for an authentication module, verifying complete coverage across all specified use cases. | CO2.LO2 | Student development machines, software development environments |
| 5 | **Atomic Task Planning and Assertion Synthesis** — Decompose user requirements into atomic execution checklists and generate input-output assertions for an authentication service, documenting rationales against target requirements. | CO2.LO3 | Student development machines, software development environments, access to AI coding tools/APIs |
| 6 | **Compiler Error-Driven Automated Repair Loops** — Run closed-loop agent workflows driven by compiler and linter diagnostic errors to iteratively repair failing functions, validating outputs across four benchmark inputs. | CO3.LO1, CO3.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 7 | **Mid-Semester Open Lab and Catch-up** — Engage in an open catch-up session to resolve pending debugging issues on multi-turn prompt refactoring and MCP tool loops without introducing new lab exercises. | CO3.LO1, CO3.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 8 | **Test-Driven Regression Repair Orchestration** — Implement a test-driven repair loop orchestrating an autonomous coding agent to resolve failing regression suites on a three-module REST service until all tests pass. | CO3.LO3 | Student development machines, software development environments, access to AI coding tools/APIs |
| 9 | **Agent Execution Log and Failure Analysis** — Analyze prompt-response histories and tool invocation logs from failing agent sessions, identifying root causes across prompt drift, schema mismatch, and model hallucination. | CO4.LO1, CO4.LO2 | Student development machines, software development environments |
| 10 | **Context Poisoning and Instruction Decay Diagnostics** — Diagnose context poisoning and instruction decay in multi-turn agent interaction transcripts, isolating poisoned memory entries and proposing prompt restructuring fixes. | CO4.LO3 | Student development machines, software development environments |
| 11 | **Static Analysis and Complexity Auditing** — Run automated static analysis tools to evaluate cyclomatic complexity, branch coverage, and security smells in agent-generated pull requests, producing an audit report. | CO5.LO1 | Student development machines, software development environments |
| 12 | **Edge-Case Defect Detection in Synthesized Test Suites** — Evaluate agent-synthesized unit test suites on reference data-structure implementations, identifying seeded edge-case defects and authoring corrective test assertions. | CO5.LO2 | Student development machines, software development environments |
| 13 | **Capstone Project Integration and Demonstration** — Execute capstone project integration evaluations, running automated regression checks, mutation coverage analysis, and live pull request review demonstrations. | CO5.LO2, CO5.LO3 | Student development machines, software development environments, access to AI coding tools/APIs |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available); Dedicated institutional API quota/keys for AI coding tools (needs_confirmation); Automated code complexity and mutation testing tooling (e.g., Radon, MutPy) (needs_confirmation)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| midsem | 20.0 | A:MidSem (W7→W7) | — | theory, analyse-data |  |
| endsem | 25.0 | A:EndSem (W13→W13) | — | theory, analyse-data, evaluate-critique |  |
| assignment | 15.0 | A:Assign1 (W3→W4), A:Assign2 (W9→W11) | — | tool-use, implement, analyse-data, research-investigation |  |
| lab | 15.0 | A:Lab1 (W3→W3), A:Lab2 (W10→W10), A:Lab3 (W12→W12) | — | tool-use, implement, evaluate-critique |  |
| project | 25.0 | A:ProjM1 (W6→W8), A:ProjM2 (W8→W10), A:ProjM3 (W12→W13) | — | design, implement, evaluate-critique, written-communication |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 16.5%, CO2 19.33%, CO3 18.33%, CO4 27.5%, CO5 18.33%

## 10. Resource material

Policy: **mixed** — Because AI-native software engineering and agentic workflows are rapidly evolving domains, the course combines standard reference books with recent research papers and framework documentation.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reading | Partha Pratim Ray (2025). *A Survey on Model Context Protocol: Architecture, State-of-the-art, Challenges and Future Directions*. | 10.36227/techrxiv.174495492.22752319/v1 | yes | M1.T1 |
| reading | Srinivasan Sekar (2026). *Under the Hood: The Protocol Specification*. | 10.1007/979-8-8688-2364-0_6 | yes | M1.T2 |
| reference | Kent Beck (2002). *Test-driven development*. | 9780137585281 | yes | M3.T3 |
| reading | Jalendar Reddy Maligireddy (2025). *Zero-Trust Proof-Gated Agent Architecture (ZPAA): A Comprehensive Security Model for the Model Context Protocol (MCP)*. | 10.22541/au.175761889.90929465/v1 | yes | M1.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO1 | PO2 | PO3 | PO4 | PO5 | PO10 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PO1 | PO2 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PSO8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CO1 | 1 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 3 [3] |  | 1 [unclaimed] | 1 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 3 [3] | 1 [unclaimed] | 1 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 3 [2] | 2 [unclaimed] |  | 1 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 3 [3] | 2 [unclaimed] |  |
| CO2 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 3 [unclaimed] | 2 [unclaimed] | 2 [2] | 2 [unclaimed] | 2 [unclaimed] | 2 [2] | 2 [unclaimed] |  | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 3 [3] | 2 [unclaimed] |  | 2 [2] | 2 [unclaimed] | 2 [2] | 2 [unclaimed] |  |  | 2 [unclaimed] |
| CO3 | 2 [unclaimed] | 3 [unclaimed] | 2 [3] | 3 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 3 [3] |  | 2 [unclaimed] | 2 [unclaimed] | 2 [2] | 3 [unclaimed] | 2 [unclaimed] |  | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 3 [3] |  |  | 2 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [unclaimed] | 2 [unclaimed] | 3 [3] | 2 [unclaimed] |  | 2 [unclaimed] | 2 [unclaimed] | 3 [2] | 3 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 3 [2] | 2 [unclaimed] | 1 [3] |  | 2 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 2 [unclaimed] | 1 [unclaimed] |  |
| CO5 | 1 [unclaimed] | 3 [2] | 3 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 2 [unclaimed] | 1 [unclaimed] | 1 [unclaimed] | 1 [unclaimed] | 3 [3] | 1 [unclaimed] | 1 [unclaimed] | 1 [unclaimed] | 3 [unclaimed] | 3 [2] | 3 [unclaimed] |  | 2 [unclaimed] | 1 [unclaimed] | 1 [unclaimed] | 3 [2] | 1 [unclaimed] |  | 2 [unclaimed] |

PO legend: PO1 = PO1; PO2 = PO2; PO3 = PO3; PO4 = PO4; PO5 = PO5; PO10 = PO10; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PO1 = PO1; PO2 = PO2; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PSO8 = PSO8

- CO1→PO5: Configuring MCP servers and external interfaces directly requires selecting and applying modern agentic engineering tools. (activities: tool-use, implement)
- CO1→PSO5: Setting up agentic protocols and tooling environments embodies the application of advanced computing tools. (activities: tool-use)
- CO1→PSO5: Configuring the context environment provides the runtime foundation for autonomous AI decision-making and tool actions. (activities: implement)
- CO1→PSO4: Configuring state-of-the-art MCP infrastructure demonstrates direct competency with modern advanced computing tools. (activities: tool-use)
- CO2→PO2: Deconstructing informal requirements into structured specifications directly executes rigorous engineering problem analysis. (activities: analyse-data)
- CO2→PO10: Formulating structured context documents and task plans requires precise technical specification writing. (activities: written-communication)
- CO2→PSO3: Adapts requirements engineering models into formal agent task decompositions for software development. (activities: analyse-data)
- CO2→PSO4: Modeling feature requirements into AI agent-readable contexts employs computational and agentic representations. (activities: analyse-data)
- CO2→PO2: Writing executable specifications and structured context documents constitutes formal technical documentation. (activities: written-communication)
- CO2→PSO2: Applies structured analytical problem formulation to adapt software specifications for agent workflows. (activities: analyse-data)
- CO3→PO3: Designing and orchestrating multi-agent feedback processes implements an end-to-end engineering solution. (activities: implement, design)
- CO3→PSO4: Directly implements and tests complex agent-based software engineering workflows meeting target specifications. (activities: implement, design)
- CO3→PSO3: Constructs algorithmic orchestration loops and tool call logic to solve software delivery problems. (activities: implement, design)
- CO3→PSO3: Develops novel agent-orchestrated software systems meeting industrial software delivery acceptance criteria. (activities: implement, design)
- CO4→PO4: Investigates log traces and failure anomalies systematically to reach substantiated diagnostic conclusions. (activities: analyse-data, evaluate-critique)
- CO4→PSO3: Applies debugging and data trace analysis techniques to isolate context-drift and regression issues. (activities: analyse-data)
- CO4→PSO4: Analyzes AI-specific failure modes such as LLM context-drift and agent regressions using trace analysis. (activities: analyse-data, evaluate-critique)
- CO4→PO1: Conducts empirical investigation of runtime traces to isolate complex root causes in agentic workflows. (activities: research-investigation)
- CO5→PO2: Evaluates quality metrics to arrive at rigorously substantiated acceptance or rejection conclusions. (activities: evaluate-critique, analyse-data)
- CO5→PSO4: Directly focuses on evaluating system deliverables against software engineering maintainability and reliability standards. (activities: evaluate-critique)
- CO5→PSO4: Critically analyzes outputs of generative AI agents to benchmark software quality and reliability. (activities: evaluate-critique, analyse-data)
- CO5→PSO3: Applies automated testing frameworks to rigorously evaluate software systems for industry standards. (activities: evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L2 | M1.T1, M1.T2 | 1 | A:MidSem@L2 |
| CO1.LO2 | L3 | M1.T3 | 2 | A:Assign1@L3, A:Lab1@L3 |
| CO1.LO3 | L3 | M1.T4 | 2, 3 | A:Assign1@L3, A:Lab1@L3 |
| CO2.LO1 | L4 | M2.T1, M2.T2 | 3, 4 | A:MidSem@L4 |
| CO2.LO2 | L3 | M2.T3 | 4 | A:MidSem@L3 |
| CO2.LO3 | L4 | M2.T4 | 5 | A:ProjM1@L4 |
| CO3.LO1 | L3 | M3.T1 | 5, 6 | A:MidSem@L3 |
| CO3.LO2 | L3 | M3.T2 | 6, 7 | A:ProjM2@L3 |
| CO3.LO3 | L3 | M3.T3 | 7, 8 | A:EndSem@L3, A:ProjM2@L3 |
| CO4.LO1 | L2 | M4.T1 | 8 | A:EndSem@L2, A:Assign2@L2 |
| CO4.LO2 | L4 | M4.T2 | 8, 9 | A:EndSem@L4, A:Assign2@L4 |
| CO4.LO3 | L4 | M4.T3 | 9, 10 | A:EndSem@L4, A:Lab2@L4 |
| CO5.LO1 | L5 | M5.T1 | 10, 11 | A:Lab3@L5, A:ProjM3@L5 |
| CO5.LO2 | L5 | M5.T2 | 11 | A:EndSem@L5, A:Lab3@L5 |
| CO5.LO3 | L5 | M5.T3 | 12 | A:ProjM3@L5 |

## Appendix C — Modules and topics

**M1 Agent Environment Configuration and Context Engineering** (primary CO1)
- M1.T1 Model Context Protocol architecture and message exchange patterns — 1.5 h · LOs CO1.LO1
- M1.T2 Tool endpoint schemas and IDE runtime integration — 1.5 h · LOs CO1.LO1 · requires M1.T1
- M1.T3 Structured prompt assets and file-context manifests — 2.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T4 Autonomous agent tool bridges and version control integration — 2.0 h · LOs CO1.LO3 · requires M1.T2, M1.T3
**M2 Requirements Decomposition and Spec-Driven Planning** (primary CO2)
- M2.T1 Informal requirement deconstruction and dependency mapping — 1.5 h · LOs CO2.LO1
- M2.T2 Context precondition extraction and boundary analysis — 1.5 h · LOs CO2.LO1 · requires M2.T1
- M2.T3 Declarative acceptance specifications and schema definition — 2.0 h · LOs CO2.LO2 · requires M2.T2
- M2.T4 Atomic task planning and input-output test assertion generation — 2.5 h · LOs CO2.LO3 · requires M2.T3
**M3 Iterative Development and Feedback Loops** (primary CO3)
- M3.T1 Compiler and linter error-driven automated repair loops — 2.5 h · LOs CO3.LO1 · requires M1.T4
- M3.T2 Multi-turn context management and prompt refactoring — 2.0 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Test-driven agent orchestration and regression repair — 2.5 h · LOs CO3.LO3 · requires M2.T4, M3.T2
**M4 Agent Execution Tracing and Failure Diagnostics** (primary CO4)
- M4.T1 Prompt-response transcript tracing and tool call log analysis — 2.0 h · LOs CO4.LO1 · requires M3.T1
- M4.T2 Failure taxonomy: prompt drift, schema mismatch, and hallucination — 2.5 h · LOs CO4.LO2 · requires M4.T1
- M4.T3 Context poisoning and instruction decay diagnostics — 2.5 h · LOs CO4.LO3 · requires M4.T2
**M5 Automated Quality Assessment and Deliverable Appraisal** (primary CO5)
- M5.T1 Automated static analysis and code complexity measurement — 2.0 h · LOs CO5.LO1 · requires M3.T3
- M5.T2 Edge-case defect detection in agent-synthesized test suites — 2.5 h · LOs CO5.LO2 · requires M5.T1
- M5.T3 Architectural soundness appraisal and pull request review criteria — 2.5 h · LOs CO5.LO3 · requires M4.T3, M5.T2

Schedule: feasible · 35.5 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 approaches these topics from a research and empirical software analysis perspective, while the proposed course focuses on operational developer workflows collaborating directly with AI coding agents. |
| CSE594A | 0.08 | complementary | CSE594A is a 2-credit course covering agent reasoning algorithms and scientific problem solving, whereas the proposed course covers end-to-end software development, specification planning, testing loops, and developer tooling. |
| CSE582 | 0.067 | superficial | CSE582 focuses on traditional product line variability and legacy software evolution, whereas the new course focuses on generative agentic loops and AI-assisted specification development. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Coverage of modern agent protocols such as Model Context Protocol (MCP) and multi-agent coordination frameworks. Avoid: Orientation towards mathematical, algorithmic, and scientific problem-solving proofs.
- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Practical perspectives on developer assistance, automated bug fixing, and test enhancement. Avoid: Heavy reliance on research paper critique and mining of software repository data.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Workflow-centric pedagogy, pragmatic tool adoption, and heavy emphasis on project-based evaluation. Avoid: Instructional time spent on OSS licensing schemes and legacy package aggregation.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

**0 errors, 4 warnings.** Repeats of the same check are merged into one row; the full list is in `validation_report.json`.

| Area | Severity | Check | Count | Parts of the design | Example |
|---|---|---|---|---|---|
| Your requirements | warning | VK | 1 | K16 | no assessment component recognisably matches 'coding_exercise' (K16); confirm that an existing component covers it, or add one |
| CO–PO mapping | warning | V23 | 1 | CO4, MTECH-CSE/PO1 | CO4→MTECH-CSE/PO1: provisional 3 vs computed 1 (share 0.273) |
| Topics, schedule and labs | warning | V6 | 1 | W13 | weeks with no lecture topics: [13] |
| Resources | warning | V15 | 1 |  | 2 resource(s) removed because no library record matched: Agentic Design Patterns; OpenAI MCP, Agent2Agent (A2A) Protocol |

**Repair history**

- los: errors 1 → 0 · round 1 accepted (1→0)
- assessment: errors 1 → 0 · round 1 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: credits and ltp: Both credits and L-T-P structure are unspecified; downstream credit-to-contact-hour alignment checks under UGREG-2025§4 cannot run until these are set.
- intake: curriculum_context: Curriculum context does not explicitly list prerequisite or antirequisite course codes (e.g. CSE201) to verify against institutional knowledge graph dependencies.
- positioning: CSE701: Computed overlap is 0.185, surpassing substantial_overlap (0.15). However, the pedagogical focus, level (7 vs 3), and learning outcomes differ substantially.
- constraints: assessment.component[midsem].present, assessment.component[endsem].present: Assessment preferences list practical assignments, coding exercises, and a final project, but do not state whether standard mid-semester or end-semester examinations are omitted, which interacts with calendar scheduling rules under UGREG-2025§6.2.
- cos: CO3: Care must be taken in assessment design to ensure students demonstrate workflow orchestration rather than manually writing the solution code, to respect NC2.
- copo: BTECH-CSAI/PSO5: CO1 maps to BTECH-CSAI/PSO5 via activity 'implement', but CO1's primary focus is environment and server configuration rather than implementing core AI algorithms.
- los: CO4.LO2, CO5.LO2 tutorial allocation: Tutorial hours for CO4.LO2 and CO5.LO2 are set to 0 to accommodate hands-on trace inspection and code review within lab hours while keeping total tutorial hours at exactly 13.
- labs: W07.LAB: Week 7 is marked with midsem_exam_after_this_week: true; W07.LAB has been scheduled as an open catch-up session without introducing new lab exercises to comply with Rule 4.
- labs: infra_requirements: Institutional API token quotas and rate limits for commercial LLM coding APIs are not explicitly confirmed in CCO.lab and require confirmation prior to commencement.
- assessment: K16: Soft constraint K16 preferred component 'coding_exercise', which has been operationalized as supervised hands-on coding tests under the 'lab' component and practical implementation under 'assignment'.
- resources: Candidate Pool Limitations: The available external and corpus resource candidates lack comprehensive textbook coverage for advanced topics such as context poisoning, prompt drift, and agent error diagnostics, requiring reliance on research papers and framework documentation.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules follow a logical progression starting from foundational agent environment configuration and context engineering (M1), moving to requirements decomposition and spec-driven planning (M2), then to iterative development and feedback loops (M3), agent execution tracing and failure diagnostics (M4), and concluding with automated quality assessment and deliverable appraisal (M5). This sequence builds upon prerequisite programming and testing proficiencies from CSE201 to take students from tooling setup to execution, troubleshooting, and rigorous evaluation.
- **assessment rationale:** The assessment mix comprises midsem (20%), endsem (25%), assignments (15%), lab work (15%), and a course project (25%). This distribution directly matches the practical and workflow-oriented learning objectives, balancing theoretical understanding tested in examinations with hands-on competencies in configuring agents, executing iterative workflows, and appraising deliverables evaluated through labs, assignments, and the project.
- **positioning rationale:** While CSE701 approaches similar topics from a research and empirical software analysis perspective and CSE594A focuses on agent reasoning algorithms and scientific problem solving, this course specifically emphasizes operational developer workflows collaborating directly with AI coding agents and managing end-to-end software development processes.