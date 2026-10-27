# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `cs601-kg-02` · generated deterministically from the design graph · validator status: **0 errors, 18 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Course level is 300 (3rd year undergraduate); Course level is 400 (4th year undergraduate) | professor |
| — | ambiguous: curriculum_context | — | Curriculum context is provided as an unstructured narrative block rather than mapped against questions Q1 through Q6; Text primarily addresses course positioning and foundation prerequisites without explicitly separating into individual question fields | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-COMMON, BTECH-CSE, BTECH-CSAI, MTECH-CSE · years [3, 4] |

## 3. Course description

This course examines AI-native software development, focusing on how developers collaborate with AI coding agents within structured software engineering workflows. Intended for third- and fourth-year B.Tech. Computer Science and Engineering students, the course addresses the core challenges of defining developer intent, managing context resources, and coordinating agentic tools. Students learn to configure agent workspaces using the Model Context Protocol, design executable software specifications from ambiguous requirements, instrument human-agent development loops to diagnose context failure modes, and establish continuous verification pipelines using synthetic defect injection. Additionally, students evaluate software quality metrics to refactor agent-generated technical debt across multi-turn workflows. The course is not a general introduction to artificial intelligence or basic programming, but a specialized study of collaborative human-AI software engineering. Instruction is delivered through a combination of lectures, tutorial sessions, and hands-on laboratory work, culminating in practical project development.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Data encapsulation, modularity, code reuse | Students require solid object-oriented software engineering foundations, modular design practices, and automated testing skills to supervise, evaluate, and verify agentic code generation in early development loops. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — The maximum computed topic overlap with any existing catalogue course is 0.08 with CSE594A, which is well below the substantial overlap threshold of 0.15. While CSE594A touches upon coding agents within a 2-credit focus on mathematical and algorithmic reasoning, the proposed course addresses the distinct domain of AI-native software engineering workflows, specification-driven development, context engineering, and automated testing.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4), ceilings raised to BL4+ for the IIIT-D template rule; to be refit from corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (BL3, procedural) — Configure AI coding agent environments and context resources, given a multi-component software specification and Model Context Protocol (MCP) tool definitions, such that all required tool invocations and context retrievals complete without protocol errors.** `[CATALOGUE, USER]`  
verb *configure* · behaviour *AI coding agent environments and context resources* · condition *given a multi-component software specification and Model Context Protocol (MCP) tool definitions* · degree *such that all required tool invocations and context retrievals complete without protocol errors* · evidence: lab_task, programming_assignment · marks share (computed): 15.42%

- CO1.LO1 (L2) Explain Model Context Protocol (MCP) tool schema specifications and context window retrieval mechanisms, given sample JSON-RPC protocol definitions, for 4 core protocol message types.
- CO1.LO2 (L3) Implement custom Model Context Protocol (MCP) server adapters, using Python or TypeScript SDKs, to expose local codebase metadata to a coding agent with zero protocol schema errors.
- CO1.LO3 (L3 ★capstone) Configure an integrated agentic workspace with multi-file context indexing, for a provided 3-service backend specification, verifying 5 required MCP tool invocations without execution errors.

**CO2 (BL3, procedural) — Construct executable software specifications and test-driven prompt context from ambiguous functional software requirements, using structured spec-driven development methods, such that at least 80% of generated code modules satisfy all specified unit tests on first synthesis.** `[USER]`  
verb *construct* · behaviour *executable software specifications and test-driven prompt context* · condition *from ambiguous functional software requirements, using structured spec-driven development methods* · degree *such that at least 80% of generated code modules satisfy all specified unit tests on first synthesis* · evidence: programming_assignment, exam_question · marks share (computed): 23.67%

- CO2.LO1 (L3) Translate ambiguous feature requests into structured specification documents containing formal input/output schemas and edge-case definitions for at least 3 requirements.
- CO2.LO2 (L3) Formulate test-driven prompt harnesses containing executable unit test cases for a single module interface using PyTest or JUnit, achieving 100% assertion coverage on valid inputs.
- CO2.LO3 (L3 ★capstone) Construct an executable specification package for a single microservice module, such that AI agent code generation passes all 5 pre-written unit tests on initial synthesis.

**CO3 (BL4, conceptual) — Diagnose failure modes and context drift in human-agent iterative development loops, given execution traces and interaction logs from an automated AI software factory workflow, identifying at least three distinct root causes of sub-optimal code generation with supporting log evidence.** `[USER]`  
verb *diagnose* · behaviour *failure modes and context drift in human-agent iterative development loops* · condition *given execution traces and interaction logs from an automated AI software factory workflow* · degree *identifying at least three distinct root causes of sub-optimal code generation with supporting log evidence* · evidence: code_review, report · marks share (computed): 25.08%

- CO3.LO1 (L2) Categorise typical context window degradation patterns and hallucination triggers from agent multi-turn conversation transcripts across 3 distinct interaction scenarios.
- CO3.LO2 (L3) Profile execution traces of an agentic loop to track token usage, tool latency, and step repetition in a sample 10-step trajectory.
- CO3.LO3 (L4 ★capstone) Diagnose context degradation causes in a supplied multi-turn software factory log, identifying 2 specific context failures with supporting log evidence in under 1 page.

**CO4 (BL4, procedural) — Analyse automated testing and verification pipelines for agent-generated software components, using synthetic defect insertion and automated regression suites in a continuous integration environment, determining code coverage gaps and identifying at least 90% of introduced functional defects.** `[CATALOGUE, USER]`  
verb *analyse* · behaviour *automated testing and verification pipelines for agent-generated software components* · condition *using synthetic defect insertion and automated regression suites in a continuous integration environment* · degree *determining code coverage gaps and identifying at least 90% of introduced functional defects* · evidence: programming_assignment, project_deliverable · marks share (computed): 21.25%

- CO4.LO1 (L3) Instrument automated regression testing workflows in CI/CD pipelines to validate agent-generated commits across dynamic containerized builds.
- CO4.LO2 (L3) Apply synthetic fault injection on generated code suites using automated mutation tools to discover un-tested execution paths across 3 target modules.
- CO4.LO3 (L4 ★capstone) Analyse defect detection efficiency for an agent-synthesized module under synthetic bug injection, uncovering at least 80% of inserted bugs in the CI pipeline.

**CO5 (BL5, metacognitive) — Evaluate the reliability and maintainability of AI-assisted software projects across multi-turn human-agent collaborative workflows using standardized software quality benchmarks, justifying each architectural refactoring recommendation against quantitative reliability and maintainability metrics.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *the reliability and maintainability of AI-assisted software projects* · condition *across multi-turn human-agent collaborative workflows using standardized software quality benchmarks* · degree *justifying each architectural refactoring recommendation against quantitative reliability and maintainability metrics* · evidence: project_deliverable, presentation · marks share (computed): 14.58%

- CO5.LO1 (L3) Measure software maintainability metrics on AI-assisted code repositories using static analysis tools, reporting cyclomatic complexity and dependency coupling scores for 5 modules.
- CO5.LO2 (L4) Formulate architectural refactoring strategies to restructure agent-generated code debt, preserving 100% of functional test pass rates on a target subsystem.
- CO5.LO3 (L5 ★capstone) Evaluate the maintainability of a multi-turn collaborative project codebase using quality benchmarks, justifying 2 specific refactoring recommendations in a 10-minute presentation.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Model Context Protocol Specifications and Tool Schemas (M1.T1)<br>MCP Server Adapters Implementation (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Worked analysis and tracing of JSON-RPC protocol schemas for four MCP core message types in pairs. |  |
| 2 | MCP Server Adapters Implementation (M1.T2)<br>Integrated Agentic Workspace and Multi-File Context Indexing (M1.T3) | CO1.LO2, CO1.LO3 | CO1 | Walkthrough and debugging session on handling protocol schema validation errors in MCP server adapters. |  |
| 3 | Integrated Agentic Workspace and Multi-File Context Indexing (M1.T3)<br>Requirements Translation and Specification Schema Design (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Group drafting and peer review of structured specification schemas from ambiguous feature requests. | A:Assignment1 released |
| 4 | Requirements Translation and Specification Schema Design (M2.T1)<br>Test-Driven Prompt Harnessing and Unit Test Assertions (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Formulate edge-case input/output schemas for requirements translation and evaluate assertion completeness. | A:Quiz1 (quiz); A:Assignment1 due |
| 5 | Test-Driven Prompt Harnessing and Unit Test Assertions (M2.T2)<br>Executable Specification Packages and Agent Code Synthesis (M2.T3) | CO2.LO2, CO2.LO3 | CO2 | Interactive problem-solving on writing non-ambiguous prompt harnesses and unit assertions. |  |
| 6 | Executable Specification Packages and Agent Code Synthesis (M2.T3)<br>Context Degradation and Hallucination Pattern Analysis (M3.T1) | CO2.LO3, CO3.LO1 | CO2, CO3 | Categorize context window degradation and hallucination patterns using multi-turn conversation transcripts. | A:Assignment2 released |
| 7 | Context Degradation and Hallucination Pattern Analysis (M3.T1)<br>Agentic Loop Instrumentation and Trajectory Profiling (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Mid-semester review and problem-solving session analyzing context window degradation scenarios. | A:Assignment2 due; A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Software Factory Log Diagnosis and Context Failure Root-Cause Analysis (M3.T3) | CO3.LO3 | CO3 | Trace diagnosis of trajectory log files identifying context failure root causes in pairs. | A:Quiz2 (quiz); A:ProjM1 released |
| 9 | Continuous Integration and Automated Regression Pipelines for Agent Commits (M4.T1) | CO4.LO1 | CO4 | Hands-on walkthrough of containerized CI build configurations and automated regression validation. | A:ProjM1 due |
| 10 | Synthetic Fault Injection and Mutation Testing (M4.T2) | CO4.LO2 | CO4 | Analysis of mutation score outputs and un-tested execution paths in mutation test reports. | A:Assignment3 released |
| 11 | Automated Defect Detection Efficiency and Pipeline Evaluation (M4.T3)<br>Code Quality Benchmarking and Static Maintainability Metrics (M5.T1) | CO4.LO3, CO5.LO1 | CO4, CO5 | Calculations and comparison of static maintainability metrics across generated code bases. | A:Assignment3 due; A:ProjM2 released |
| 12 | Code Quality Benchmarking and Static Maintainability Metrics (M5.T1)<br>Architectural Refactoring Strategies for Agent-Generated Debt (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Peer evaluation of refactoring strategies preserving 100% test pass rates on target subsystems. | A:ProjM2 due; A:ProjM3 released |
| 13 | Architectural Refactoring Strategies for Agent-Generated Debt (M5.T2)<br>Maintainability Evaluation and Collaborative Project Benchmarking (M5.T3) | CO5.LO2, CO5.LO3 | CO5 | Practice 10-minute presentations justifying refactoring recommendations based on quality benchmarks. | A:ProjM3 due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **MCP Server Adapter Basics** — Build a baseline custom Model Context Protocol (MCP) server adapter using Python or TypeScript SDKs to expose local codebase metadata to a coding agent. | CO1.LO2 | Python SDK, TypeScript SDK, VS Code |
| 2 | **MCP Adapter Implementation & Workspace Context Indexing** — Implement custom MCP server adapters and configure multi-file context indexing for a 3-service backend specification, verifying MCP tool definitions. | CO1.LO2, CO1.LO3 | Python SDK, AI coding tools/APIs |
| 3 | **Integrated Agentic Workspace Verification** — Configure and test an integrated agentic workspace with multi-file context indexing to verify 5 required MCP tool invocations without execution errors. | CO1.LO3 | AI coding tools/APIs, MCP Inspector |
| 4 | **Test-Driven Prompt Harnessing** — Develop test-driven prompt harnesses containing executable PyTest unit test cases targeting a single module interface. | CO2.LO2 | PyTest, Python, AI coding tools/APIs |
| 5 | **Executable Specification Package Construction** — Construct an executable specification package for a microservice module, ensuring AI agent code synthesis passes all initial unit test assertions. | CO2.LO2, CO2.LO3 | PyTest, AI coding tools/APIs |
| 6 | **Agent Code Synthesis & Assertion Verification** — Finalize executable specification packages and execute automated synthesis verification across pre-written unit test suites. | CO2.LO3 | PyTest, AI coding tools/APIs |
| 7 | **Mid-Semester Open Lab and Catch-up Session** — Open lab session for catch-up on MCP adapters and specification package tasks prior to mid-sem exams. | CO1.LO3, CO2.LO3 | Student development machines, AI coding tools/APIs |
| 8 | **Agentic Loop Profiling & Context Diagnosis** — Profile 10-step agentic loop execution traces and diagnose context degradation failures in supplied software factory logs. | CO3.LO2, CO3.LO3 | Python Logging, Execution Profiler |
| 9 | **Automated Regression Pipelines for Agent Commits** — Instrument automated regression testing workflows in CI/CD pipelines to validate agent-generated commits across dynamic containerized builds. | CO4.LO1 | GitHub Actions, Docker |
| 10 | **Synthetic Fault Injection & Mutation Testing** — Apply synthetic fault injection on generated code suites using automated mutation tools to discover un-tested execution paths. | CO4.LO2 | MutMut / Mutation Framework, PyTest |
| 11 | **Pipeline Evaluation & Static Maintainability Metrics** — Analyse pipeline defect detection efficiency and measure software maintainability metrics, including cyclomatic complexity and dependency coupling. | CO4.LO3, CO5.LO1 | Radon, SonarQube / Static Analyzers |
| 12 | **Architectural Refactoring of Code Debt** — Formulate and execute architectural refactoring strategies on agent-generated code debt while preserving 100% of functional test pass rates. | CO5.LO1, CO5.LO2 | PyTest, Static Analysis Tools |
| 13 | **Maintainability Evaluation & Collaborative Benchmarking** — Evaluate the maintainability of a multi-turn collaborative project codebase using quality benchmarks and prepare refactoring recommendations. | CO5.LO3 | Benchmarking Suite, Presentation Tools |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available); Containerized CI execution environment (Docker / GitHub Actions runner) (needs_confirmation); Python mutation testing frameworks (MutMut / PIT) (needs_confirmation)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W4→W4), A:Quiz2 (W8→W8) | — | theory, analyse-data |  |
| assignment | 20.0 | A:Assignment1 (W3→W4), A:Assignment2 (W6→W7), A:Assignment3 (W10→W11) | — | implement, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | design, theory |  |
| project | 25.0 | A:ProjM1 (W8→W9), A:ProjM2 (W11→W12), A:ProjM3 (W12→W13) | — | design, implement, evaluate-critique, oral-presentation, written-communication, research-investigation |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | design, evaluate-critique, theory |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 15.42%, CO2 23.67%, CO3 25.08%, CO4 21.25%, CO5 14.58%

## 10. Resource material

Policy: **mixed** — AI-assisted software development is an emerging field requiring both canonical software engineering foundations (testing, refactoring, continuous integration) and current peer-reviewed research papers and framework documentation for agentic protocols and benchmarks.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Chen Qian, Wei Liu, Hongzhang Liu, Nuo Chen (2024). *ChatDev: Communicative Agents for Software Development*. | 10.18653/v1/2024.acl-long.810 | yes | M1.T3, M2.T3, M3.T2 |
| reference | Kent Beck (2002). *Test-driven development*. | 9780137585281 | yes | M2.T2 |
| reference | Paul Ammann (2017). *Introduction to software testing*. | 9781107172012 | yes | M4.T2, M4.T3 |
| reference | Titus Winters, Tom Manshreck, Hyrum Wright (2020). *Software Engineering at Google*. | 9781492082798 | yes | M4.T1, M5.T1 |
| reference | Martin Fowler (1999). *Refactoring: Improving the Design of Existing Code*. | 9780201485677 | yes | M5.T2 |
| reading | Henrique Nunes, Eduardo Figueiredo, Larissa Rocha, Sarah Nadi (2025). *Evaluating the Effectiveness of LLMs in Fixing Maintainability Issues in Real-World Projects*. | 10.1109/saner64311.2025.00069 | yes | M5.T1, M5.T3 |
| reading | Shanchao Liang, Spandan Garg, Roshanak Zilouchian Moghaddam (2026). *The SWE-Bench Illusion: When State-of-the-Art LLMs Remember Instead of Reason*. | 10.1145/3786583.3786882 | yes | M3.T1, M4.T3 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO1 | PO2 | PO3 | PO4 | PO5 | PO10 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PO1 | PO2 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PSO8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 2 [unclaimed] | 3 [unclaimed] | 2 [unclaimed] | 2 [3] |  | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 3 [unclaimed] | 2 [3] | 2 [unclaimed] | 2 [unclaimed] | 3 [unclaimed] | 2 [unclaimed] | 3 [2] |  |  | 2 [unclaimed] | 2 [unclaimed] | 3 [unclaimed] | 2 [3] |  |  |
| CO2 | 3 [unclaimed] | 1 [unclaimed] | 3 [3] | 1 [unclaimed] | 1 [unclaimed] |  | 3 [unclaimed] | 3 [unclaimed] |  | 3 [3] | 1 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 3 [3] | 1 [unclaimed] | 3 [unclaimed] |  |  | 3 [unclaimed] |  | 3 [3] | 1 [unclaimed] |  |  |
| CO3 | 3 [unclaimed] | 3 [3] | 3 [unclaimed] | 3 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 1 [2] | 3 [unclaimed] |  | 3 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 3 [3] | 3 [unclaimed] | 2 [3] | 2 [unclaimed] | 3 [unclaimed] | 1 [unclaimed] | 3 [unclaimed] |  | 2 [unclaimed] | 2 [unclaimed] |
| CO4 | 1 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 3 [3] | 3 [unclaimed] | 2 [unclaimed] | 1 [unclaimed] | 1 [unclaimed] |  | 3 [3] | 2 [unclaimed] | 1 [unclaimed] | 1 [unclaimed] | 3 [unclaimed] | 3 [2] | 3 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 1 [unclaimed] |  | 3 [3] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] |
| CO5 | 2 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 2 [unclaimed] | 2 [2] | 2 [unclaimed] | 2 [unclaimed] |  | 3 [3] |  | 2 [unclaimed] | 2 [unclaimed] | 3 [unclaimed] | 3 [2] | 3 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] |  | 3 [unclaimed] |  | 2 [unclaimed] | 2 [2] |

PO legend: PO1 = PO1; PO2 = PO2; PO3 = PO3; PO4 = PO4; PO5 = PO5; PO10 = PO10; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PO1 = PO1; PO2 = PO2; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PSO8 = PSO8

- CO1→PO5: Configuring AI coding agent environments and context resources requires applying modern IT tools and protocol integrations without errors. (activities: tool-use, implement)
- CO1→PSO5: Configuring MCP tool definitions and agent context directly utilizes advanced software engineering techniques and modern tools. (activities: tool-use)
- CO1→PSO5: Setting up agent environments and tool definitions enables AI agents to process context data into automated tool invocations. (activities: implement)
- CO1→PSO4: Configuring Model Context Protocol resources requires advanced computing tool mastery for seamless automated agent execution. (activities: tool-use)
- CO2→PO3: Constructing executable specifications and structured prompt contexts involves designing systematic software solutions from ambiguous requirements. (activities: design, implement)
- CO2→PSO4: Designing test-driven prompt contexts and executable specs ensures synthesized code satisfies unit test requirements. (activities: design, implement)
- CO2→PSO3: Structuring spec-driven development methods requires designing precise algorithmic prompts for efficient code generation. (activities: design, implement)
- CO2→PSO3: Developing executable software specifications for automated code synthesis addresses novel AI-assisted software engineering processes. (activities: design, implement)
- CO3→PO2: Analyzing execution traces and interaction logs allows students to diagnose root causes of sub-optimal code generation. (activities: analyse-data)
- CO3→PSO3: Diagnosing failure modes requires adapting analytical debugging techniques to human-agent context drift problems. (activities: analyse-data)
- CO3→PSO4: Analyzing context drift and agent workflow logs applies AI operational concepts to model failure mechanisms. (activities: analyse-data)
- CO3→PO1: Investigating workflow logs to isolate root causes of agent code degradation demonstrates independent practical analysis. (activities: research-investigation)
- CO4→PO4: Using synthetic defect insertion and automated regression suites involves experimental design and empirical data analysis. (activities: evaluate-critique, analyse-data)
- CO4→PSO4: Evaluating continuous integration testing pipelines determines coverage gaps and verifies agent-generated code quality. (activities: evaluate-critique)
- CO4→PSO4: Analyzing automated verification pipelines evaluates the correctness and reliability of AI-generated software artifacts. (activities: evaluate-critique, analyse-data)
- CO4→PSO3: Evaluating automated continuous integration pipelines ensures reliable deployment of novel agent-generated applications. (activities: evaluate-critique)
- CO5→PO10: Justifying architectural refactoring recommendations requires presenting clear technical presentations and reports to stakeholders. (activities: oral-presentation, written-communication)
- CO5→PSO4: Evaluating software quality metrics enables principled architectural refactoring of multi-turn AI-assisted projects. (activities: evaluate-critique)
- CO5→PSO4: Applying quantitative quality metrics models the long-term maintainability of multi-turn human-agent software workflows. (activities: evaluate-critique)
- CO5→PSO8: Presenting refactoring recommendations based on standardized benchmarks effectively communicates technical quality trade-offs. (activities: oral-presentation, written-communication)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L2 | M1.T1 | 1 | A:Quiz1@L2, A:Endsem@L2 |
| CO1.LO2 | L3 | M1.T2 | 1, 2 | A:Assignment1@L3 |
| CO1.LO3 | L3 | M1.T3 | 2, 3 | A:Assignment1@L3 |
| CO2.LO1 | L3 | M2.T1 | 3, 4 | A:Midsem@L3, A:Endsem@L3 |
| CO2.LO2 | L3 | M2.T2 | 4, 5 | A:Assignment2@L3 |
| CO2.LO3 | L3 | M2.T3 | 5, 6 | A:Assignment2@L3 |
| CO3.LO1 | L2 | M3.T1 | 6, 7 | A:Quiz2@L2, A:Endsem@L2 |
| CO3.LO2 | L3 | M3.T2 | 7 | A:Midsem@L3 |
| CO3.LO3 | L4 | M3.T3 | 8 | A:ProjM1@L4 |
| CO4.LO1 | L3 | M4.T1 | 9 | A:Assignment3@L3 |
| CO4.LO2 | L3 | M4.T2 | 10 | A:Assignment3@L3, A:Endsem@L3 |
| CO4.LO3 | L4 | M4.T3 | 11 | A:ProjM2@L4 |
| CO5.LO1 | L3 | M5.T1 | 11, 12 | A:ProjM3@L3 |
| CO5.LO2 | L4 | M5.T2 | 12, 13 | A:ProjM3@L4, A:Endsem@L4 |
| CO5.LO3 | L5 | M5.T3 | 13 | A:ProjM3@L5 |

## Appendix C — Modules and topics

**M1 Agent Workspace & Model Context Protocol** (primary CO1)
- M1.T1 Model Context Protocol Specifications and Tool Schemas — 2.0 h · LOs CO1.LO1
- M1.T2 MCP Server Adapters Implementation — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Integrated Agentic Workspace and Multi-File Context Indexing — 3.0 h · LOs CO1.LO3 · requires M1.T2
**M2 Specification-Driven Development & Prompt Harnesses** (primary CO2)
- M2.T1 Requirements Translation and Specification Schema Design — 3.0 h · LOs CO2.LO1 · requires M1.T1
- M2.T2 Test-Driven Prompt Harnessing and Unit Test Assertions — 2.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Executable Specification Packages and Agent Code Synthesis — 3.0 h · LOs CO2.LO3 · requires M2.T2, M1.T3
**M3 Agentic Loops & Context Diagnostics** (primary CO3)
- M3.T1 Context Degradation and Hallucination Pattern Analysis — 3.0 h · LOs CO3.LO1 · requires M1.T1
- M3.T2 Agentic Loop Instrumentation and Trajectory Profiling — 2.0 h · LOs CO3.LO2 · requires M1.T2
- M3.T3 Software Factory Log Diagnosis and Context Failure Root-Cause Analysis — 3.0 h · LOs CO3.LO3 · requires M3.T1, M3.T2
**M4 Automated Testing & Continuous Verification Pipelines** (primary CO4)
- M4.T1 Continuous Integration and Automated Regression Pipelines for Agent Commits — 3.0 h · LOs CO4.LO1 · requires M1.T3
- M4.T2 Synthetic Fault Injection and Mutation Testing — 3.0 h · LOs CO4.LO2 · requires M2.T2
- M4.T3 Automated Defect Detection Efficiency and Pipeline Evaluation — 2.0 h · LOs CO4.LO3 · requires M4.T1, M4.T2
**M5 Code Quality, Refactoring & Project Maintenance** (primary CO5)
- M5.T1 Code Quality Benchmarking and Static Maintainability Metrics — 3.0 h · LOs CO5.LO1 · requires M4.T1
- M5.T2 Architectural Refactoring Strategies for Agent-Generated Debt — 2.0 h · LOs CO5.LO2 · requires M5.T1, M3.T3
- M5.T3 Maintainability Evaluation and Collaborative Project Benchmarking — 2.0 h · LOs CO5.LO3 · requires M5.T2, M4.T3

Schedule: feasible · 39.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE594A | 0.08 | complementary | CSE594A focuses on foundational agentic reasoning architectures and protocols for algorithmic and mathematical problem solving. In contrast, the proposed course focuses entirely on the software engineering lifecycle—including specification planning, loop engineering, context engineering, MCP tooling, and automated testing with AI coding agents. |

Overlap method: neo4j: Jaccard over embedding-matched topic phrases (all-MiniLM-L6-v2, cos ≥ 0.66), no IDF

**Comparable courses**

- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Instructional coverage of agentic protocols such as MCP and tool invocation mechanisms. Avoid: Over-indexing on abstract algorithmic, mathematical, or scientific reasoning benchmarks instead of practical software development.
- **CSE583** Software Engineering/Development Using Open Source — IIIT-D catalogue. Take: Hands-on developer workflow tooling, version control integration, and project-based application development style. Avoid: Focus on manual open-source licensing regimes and legacy component integration devoid of generative coding workflows.
- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Techniques for developer assistance, automated bug triage, and automated software repair concepts. Avoid: Academic literature review seminars and mining repository data for predictive modeling rather than real-time AI-assisted development.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

**0 errors, 18 warnings.** Repeats of the same check are merged into one row; the full list is in `validation_report.json`.

| Area | Severity | Check | Count | Parts of the design | Example |
|---|---|---|---|---|---|
| Your requirements | warning | VK-UNENFORCED | 1 | K17 | no check exists for constraint K17 ('other'); confirm it by hand: Assessment should emphasize the ability to apply modern AI-assisted development practices rather than primarily testing theory. |
| Outcomes (COs and LOs) | warning | V11 | 11 | CO2.LO1, CO2.LO3, CO3.LO1, CO3.LO2, CO3.LO3, CO4.LO1, CO4.LO2, CO4.LO3 (+2 more) | LO CO2.LO1 condition is not visible in the statement text |
| Outcomes (COs and LOs) | warning | VB | 4 | CO2.LO2, CO3.LO1, CO5.LO1, CO5.LO2 | LO CO2.LO2: claimed Bloom L3 but verb 'formulate' is lexicon L6 |
| Assessment plan | warning | VA-PROJ | 1 | project | project released in week 8, late in a 13-week semester |
| Resources | warning | V15 | 1 |  | 1 resource(s) removed because no library record matched: OpenAI MCP, Agent2Agent (A2A) Protocol |

**Repair history**


**Model-reported concerns (not validated; for the professor's attention)**

- intake: topics: Topics are explicitly marked as starting hypotheses and may be modified, added, dropped, or reordered during course development.
- intake: lab: Lab component is marked as required, but L-T-P contact hours are unspecified, requiring reconciliation during credit and scheduling determination.
- positioning: CSE594A: CSE594A is a 5xx-level course covering agentic protocols (MCP) and automated coding agents; clear pedagogical boundaries should be maintained between CSE594A's reasoning focus and this course's SE workflow focus.
- labs: AI API Token Budget: Automated code synthesis and multi-turn agentic loop experiments across weeks 1-13 require shared or institutional API keys to prevent individual student cost barriers.
- resources: R:hash:905106f30a804529: Candidate record from corpus lacks structured author, publication year, and URL fields in the input context.
- resources: OL:OL16551230W: First edition publication year is 1999, which exceeds standard age limits for technical literature, though it remains the canonical reference for refactoring.
- resources: OL:OL1961692W: Publication year is 2002, exceeding standard recency guidelines, but serves as the canonical text for TDD.

## Appendix F — Rationales (G11)

- **sequencing rationale:** Building upon foundational software engineering and unit testing concepts from CSE201, the course begins with setting up agent workspaces and protocol adapters (M1). Students advance to specification-driven prompt engineering and code synthesis (M2). With operational context established, the curriculum progresses to diagnosing context degradation in agentic loops (M3), followed by automated continuous verification pipelines (M4). It culminates in evaluating long-term software quality and architectural refactoring strategies (M5).
- **assessment rationale:** The assessment structure matches the course's practical and analytical goals. Hands-on assignments (20%) and a continuous software project (25%) directly evaluate practical skills in configuring context protocols, synthesizing code, and building automated verification pipelines (CO1, CO2, CO4). Quizzes (10%), mid-semester (20%), and end-semester examinations (25%) evaluate theoretical understanding of context failure diagnostics and quantitative maintainability metrics (CO3, CO5).
- **positioning rationale:** Unlike CSE594A, which focuses on foundational agentic reasoning architectures for algorithmic and mathematical problem solving, this course addresses the full software development lifecycle. It specifically concentrates on specification-driven development, Model Context Protocol integration, automated testing pipelines, and software maintainability metrics within multi-turn human-agent workflows.