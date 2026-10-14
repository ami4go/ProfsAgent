# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-excessive_cos` · generated deterministically from the design graph · validator status: **3 errors, 21 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level specified without an explicit course code. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. The course matters for target students by equipping them with practical skills in agentic development environments, tool use and orchestration frameworks, specification-driven development, loop engineering and execution traces, testing, evaluation, and reliability, as well as a capstone project. Students will be able to configure coding assistants, implement agent skills and tool use integrations, construct executable specifications, analyse loop engineering execution traces, evaluate reliability and automated test coverage, and assess end-to-end AI-native software development projects. The course is taught through lectures, tutorials, and laboratory sessions involving hands-on coding and projects.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Data encapsulation, modularity, code reuse, Generic programming | Students require strong programming and software engineering fundamentals, including object-oriented design and unit testing, to effectively build and evaluate agent-assisted software. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — CSE701 covers general AI applications in software engineering and mining software repositories, whereas the new course focuses specifically on AI-native software development, agentic workflows, and human-AI collaborative development processes.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure coding assistants and developer workflows for a given software task, using an agentic development environment, such that at least 80% of the provided test cases pass.** `[CORPUS, USER]`  
verb *configure* · behaviour *coding assistants and developer workflows* · condition *for a given software task, using an agentic development environment* · degree *such that at least 80% of the provided test cases pass* · evidence: programming_assignment, lab_task · marks share (computed): 18.33%

- CO1.LO1 (L1) Identify the core components and configuration parameters of an agentic development environment for a given software project.
- CO1.LO2 (L3 ★capstone) Configure coding assistant extensions within an integrated development environment, given a sample user project, such that at least 80% of the provided test cases pass.

**CO2 (L3, procedural) — Implement agent skills and tool use integrations within an orchestration framework, given an API specification, meeting the stated interface specification for every public method.** `[CORPUS, USER]`  
verb *implement* · behaviour *agent skills and tool use integrations* · condition *within an orchestration framework, given an API specification* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment · marks share (computed): 18.33%

- CO2.LO1 (L3) Examine the API specifications and communication protocols required for tool use integration within an orchestration framework.
- CO2.LO2 (L3 ★capstone) Implement agent skill integration routines for an orchestration framework, given a target API specification, meeting the stated interface specification for every public method.

**CO3 (L3, procedural) — Construct executable specifications from natural language requirements using a spec-driven development tool, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *construct* · behaviour *executable specifications from natural language requirements* · condition *using a spec-driven development tool* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 18.33%

- CO3.LO1 (L3) Translate natural language requirements into structured intermediate representation models suitable for spec-driven development.
- CO3.LO2 (L3 ★capstone) Construct executable test specifications from user stories, using a requirements translation tool, covering every use case in the supplied requirements document.

**CO4 (L4, metacognitive) — Analyse loop engineering execution traces from a coding agent run, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *analyse* · behaviour *loop engineering execution traces from a coding agent run* · condition *inspecting generated logs and checkpoints* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, report · marks share (computed): 15.5%

- CO4.LO1 (L2) Trace the execution flow and checkpoint logs generated during an automated coding agent run.
- CO4.LO2 (L4 ★capstone) Analyse loop checkpoint logs from an automated agent run, given a failure trace record, identifying at least three distinct failure causes with supporting log evidence.

**CO5 (L5, conceptual) — Evaluate the reliability and automated test coverage of an AI-generated software artifact, justifying each validation choice against at least one stated requirement.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *the reliability and automated test coverage of an AI-generated software artifact* · condition *using automated testing frameworks and evaluation pipelines* · degree *justifying each validation choice against at least one stated requirement* · evidence: code_review, report · marks share (computed): 19.5%

- CO5.LO1 (L3) Configure automated testing frameworks and evaluation pipelines for AI-generated software artifacts.
- CO5.LO2 (L5 ★capstone) Evaluate the test coverage report of a generated software module, using automated coverage tooling, justifying each validation choice against at least one stated requirement.

**CO6 (L5, metacognitive) — Evaluate an end-to-end AI-native software development project incorporating coding agents and automated workflows, justifying each design decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *an end-to-end AI-native software development project* · condition *incorporating coding agents and automated workflows* · degree *demonstrated live, with 2 scenario walkthroughs chosen by the evaluator* · evidence: project_deliverable, presentation · marks share (computed): 10.0%

- CO6.LO1 (L5) Design an end-to-end AI-native software development project plan incorporating coding agents and automated workflows.
- CO6.LO2 (L5 ★capstone) Evaluate a final software project integrating multiple coding agents, demonstrated live, with 2 scenario walkthroughs chosen by the evaluator.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding environments and configuration (M1.T1) | CO1.LO1 | CO1 | Worked trace-diagnosis of 2 sample agent environment configuration setups, in pairs. |  |
| 2 | Coding assistants and developer workflows (M1.T2) | CO1.LO2 | CO1 | Problem-solving session on resolving extension configuration conflicts and failing test cases. | A:Assign1 released |
| 3 | API specifications and communication protocols for tool integration (M2.T1) | CO2.LO1 | CO2 | Worked analysis of communication protocols and API specification document schemas. | A:Quiz1 (quiz) |
| 4 | Agent skills and context engineering (M2.T2) | CO2.LO2 | CO2 | Interface verification exercise matching method signatures to API contracts. | A:Assign1 due; A:Assign2 released |
| 5 | Requirements engineering and intermediate representation models (M3.T1) | CO3.LO1 | CO3 | Group translation task converting ambiguous user requirements into structured intermediate models. |  |
| 6 | Requirements to executable specifications (M3.T2) | CO3.LO2 | CO3 | Worked trace of test specification generation and requirement coverage checking. | A:Assign2 due; A:Assign3 released |
| 7 | Loop engineering and iterative execution flow (M4.T1) | CO4.LO1 | CO4 | Execution flow tracing exercise using sample checkpoint logs. | A:Midsem (midsem); A:ProjMilestone1 released |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Software factories and failure trace analysis (M4.T2) | CO4.LO2 | CO4 | Failure trace analysis and log correlation drill in small groups. | A:Assign3 due |
| 9 | Automated testing frameworks and evaluation pipelines (M5.T1) | CO5.LO1 | CO5 | Pipeline configuration review and test case design for AI artifacts. |  |
| 10 | Reliability and deployment of generated software artifacts (M5.T2) | CO5.LO2 | CO5 | Coverage report review and requirement justification exercise. | A:ProjMilestone1 due; A:ProjMilestone2 released |
| 11 | Hands-on coding and project planning (M6.T1) | CO6.LO1 | CO6 | Project milestone review and architecture planning feedback session. |  |
| 12 | Emerging developer tools and project evaluation (M6.T2) | CO6.LO2 | CO6 | Peer evaluation of multi-agent demonstration walkthrough outlines. |  |
| 13 |  |  |  |  | A:Endsem (endsem); A:ProjMilestone2 due |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Environment Setup** — Install and configure basic development environments and baseline tools. | CO1.LO1 | VS Code, Git |
| 2 | **Coding Assistants Configuration** — Configure coding assistant extensions within the IDE to pass sample project test cases. | CO1.LO2 | IDE, Coding Assistant Extensions |
| 3 | **API Specifications** — Inspect API specifications and communication protocols for tool integration. | CO2.LO1 | Postman, OpenAPI specs |
| 4 | **Agent Skills and Context** — Implement agent skill integration routines meeting public method interface specifications. | CO2.LO2 | Python, API Client libraries |
| 5 | **Intermediate Representations** — Translate natural language requirements into structured intermediate models. | CO3.LO1 | Markdown, JSON Schema |
| 6 | **Executable Specifications** — Construct executable test specifications from user stories using translation tooling. | CO3.LO2 | Requirements Translation Tool |
| 7 | **Mid-sem Catch-up Lab** — Open lab session for catch-up and revision ahead of mid-semester evaluations. | CO4.LO1 | Development machines |
| 8 | **Failure Trace Analysis** — Analyze loop checkpoint logs from an agent run to identify failure causes. | CO4.LO2 | Log analyzer, Agent logs |
| 9 | **Automated Testing Frameworks** — Configure automated testing frameworks and evaluation pipelines for generated code. | CO5.LO1 | Pytest, CI pipelines |
| 10 | **Reliability and Coverage** — Evaluate test coverage reports of generated modules against stated requirements. | CO5.LO2 | Coverage.py, Code Review Tools |
| 11 | **Project Planning** — Design and outline an end-to-end AI-native software development project plan. | CO6.LO1 | Project Management Tools |
| 12 | **Project Evaluation** — Demonstrate live evaluation of a multi-agent software project with scenario walkthroughs. | CO6.LO2 | Presentation tools, Source repository |

Infrastructure: Student development machines (available); Access to AI coding tools/APIs (needs_confirmation); Software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3) | — | tool-use |  |
| assignment | 25.0 | A:Assign1 (W2→W4), A:Assign2 (W4→W6), A:Assign3 (W6→W8) | — | implement, design, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, design |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique |  |
| project | 20.0 | A:ProjMilestone1 (W7→W10), A:ProjMilestone2 (W10→W13) | — | design, implement, evaluate-critique, oral-presentation, teamwork |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 18.33%, CO2 18.33%, CO3 18.33%, CO4 15.5%, CO5 19.5%, CO6 10.0%

## 10. Resource material

Policy: **mixed** — Due to the fast-moving nature of AI-native software development, agentic workflows, and tool integration frameworks, a combination of recent reference books, official framework documentation, and cutting-edge research papers is supplemented by classic software engineering principles.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Agentic Design Patterns*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T2, M2.T2 |
| reading | OpenAI (2024). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M2.T1 |
| reading | Yujia Li, Shunyu Yao, Guanzhi Wang, John Yang, Alexander Novikov (2024). *1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022. 2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022. 3) Wang, Guanzhi, et al. "Voyager: An Open-Ended Embodied Agent with Large Language Models." TMLR 2023. 4) Yang, John, et al. "Swe-agent: Agent-computer interfaces enable automated software engineering." NeurIPS 2024. 5) Novikov, Alexander, et al. "AlphaEvolve: A coding agent for scientific and algorithmic discovery." arXiv:2506.13131, 2025.*. | R:hash:1-li-yujia-et-al-competition-level-code- | NO: candidate_id not in retrieved candidates | M4.T2, M5.T1 |
| reading | Andrii Tkachuk (2026). *SPECIFICATION-DRIVEN DEVELOPMENT AS STRUCTURED APPROACH FOR SOURCE CODE GENERATION*. | 10.52058/2786-6025-2026-4(58)-2631-2644 | yes | M3.T2 |
| reading | Noble Saji Mathews, Meiyappan Nagappan (2024). *Test-Driven Development and LLM-based Code Generation*. | 10.1145/3691620.3695527 | yes | M5.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|---|
| CO1 |  | 2 [3] |  |  | 3 [2] |
| CO2 | 2 [unclaimed] | 3 [3] |  |  | 2 [unclaimed] |
| CO3 | 2 [unclaimed] | 3 [3] |  |  | 2 [unclaimed] |
| CO4 | 3 [2] | 3 [unclaimed] | 1 [unclaimed] | 1 [unclaimed] | 3 [unclaimed] |
| CO5 | 3 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [unclaimed] | 3 [2] |
| CO6 |  | 3 [3] | 3 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring developer workflows and coding assistants directly exercises modern tooling and methodology to build application systems. (activities: tool-use, implement)
- CO1→PO9: Uses advanced tools in agentic development environments. (activities: tool-use)
- CO2→PO4: Direct implementation of software components using an orchestration framework. (activities: implement)
- CO3→PO4: Design activity mapping specifications to executable requirements using modern tools. (activities: design)
- CO4→PO3: Analysis of execution traces evaluates operational data and traces. (activities: analyse-data)
- CO5→PO4: Direct evaluation of software artifacts using automated testing. (activities: evaluate-critique)
- CO5→PO9: Uses advanced automated evaluation pipelines and testing frameworks. (activities: evaluate-critique)
- CO6→PO4: Comprehensive evaluation of an end-to-end software application project. (activities: evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1 |
| CO1.LO2 | L3 | M1.T2 | 2 | A:Assign1@L3 |
| CO2.LO1 | L3 | M2.T1 | 3 | A:Midsem@L3 |
| CO2.LO2 | L3 | M2.T2 | 4 | A:Assign2@L3 |
| CO3.LO1 | L3 | M3.T1 | 5 | A:Midsem@L3 |
| CO3.LO2 | L3 | M3.T2 | 6 | A:Assign3@L3 |
| CO4.LO1 | L2 | M4.T1 | 7 | A:ProjMilestone1@L2 |
| CO4.LO2 | L4 | M4.T2 | 8 | A:Endsem@L4 |
| CO5.LO1 | L3 | M5.T1 | 9 | A:Endsem@L3 |
| CO5.LO2 | L5 | M5.T2 | 10 | A:ProjMilestone1@L5 |
| CO6.LO1 | L5 | M6.T1 | 11 | A:ProjMilestone2@L5 |
| CO6.LO2 | L5 | M6.T2 | 12 | A:ProjMilestone2@L5 |

## Appendix C — Modules and topics

**M1 Agentic Development Environments** (primary CO1)
- M1.T1 AI-assisted coding environments and configuration — 3.0 h · LOs CO1.LO1
- M1.T2 Coding assistants and developer workflows — 3.0 h · LOs CO1.LO2 · requires M1.T1
**M2 Tool Use and Orchestration Frameworks** (primary CO2)
- M2.T1 API specifications and communication protocols for tool integration — 3.0 h · LOs CO2.LO1 · requires M1.T2
- M2.T2 Agent skills and context engineering — 3.0 h · LOs CO2.LO2 · requires M2.T1
**M3 Specification-Driven Development** (primary CO3)
- M3.T1 Requirements engineering and intermediate representation models — 3.0 h · LOs CO3.LO1 · requires M2.T2
- M3.T2 Requirements to executable specifications — 3.0 h · LOs CO3.LO2 · requires M3.T1
**M4 Loop Engineering and Execution Traces** (primary CO4)
- M4.T1 Loop engineering and iterative execution flow — 3.0 h · LOs CO4.LO1 · requires M3.T2
- M4.T2 Software factories and failure trace analysis — 3.0 h · LOs CO4.LO2 · requires M4.T1
**M5 Testing, Evaluation, and Reliability** (primary CO5)
- M5.T1 Automated testing frameworks and evaluation pipelines — 3.0 h · LOs CO5.LO1 · requires M4.T2
- M5.T2 Reliability and deployment of generated software artifacts — 3.0 h · LOs CO5.LO2 · requires M5.T1
**M6 Capstone Project and Emerging Tools** (primary CO6)
- M6.T1 Hands-on coding and project planning — 3.0 h · LOs CO6.LO1 · requires M5.T2, M1.T2, M2.T2, M3.T2
- M6.T2 Emerging developer tools and project evaluation — 3.0 h · LOs CO6.LO2 · requires M6.T1

Schedule: feasible · 36.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 investigates data-driven and research perspectives on AI in software engineering, whereas this course emphasizes practical, end-to-end agentic software development, tool use, and loop engineering. |
| CSE594A | 0.08 | complementary | CSE594A focuses on foundational agentic reasoning and algorithmic problem solving, whereas this course targets applied software engineering workflows and developer tool integration. |
| CSE582 | 0.067 | complementary | CSE582 covers product line evolution, maintenance, and legacy systems, whereas this course deals with modern AI-native development and software factories driven by coding agents. |
| CSE581 | 0.034 | superficial | CSE581 covers traditional systems analysis and requirements engineering theories, whereas this course focuses on spec-driven development using AI agents. |
| AI501 | 0.034 | superficial | AI501 provides foundational machine learning theory, whereas this course applies evaluation and reliability concepts specifically to AI-generated software artifacts. |
| CSE201 | 0.017 | complementary | CSE201 teaches foundational advanced programming and object-oriented design, whereas this course builds upon those fundamentals to explore automated testing and execution via AI coding assistants. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Research literature review structure and advanced software engineering case studies Avoid: Over-reliance on retrospective mining of software repositories rather than active agent-assisted development workflows
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Concepts of agentic protocols, MCP, and multi-agent collaboration frameworks Avoid: Deep focus on algorithmic and mathematical problem solving instead of software engineering workflows
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation structure and team-based practical execution models Avoid: Traditional open-source community governance topics not relevant to AI-native workflows

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Agentic Design Patterns' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:1-li-yujia-et-al-competition-level-code- | resource '1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022. 2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022. 3) Wang, Guanzhi, et al. " |
| cos | V11 | warning | CO4 | CO CO4 condition is not visible in the statement text |
| cos | V11 | warning | CO5 | CO CO5 condition is not visible in the statement text |
| cos | V11 | warning | CO6 | CO CO6 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO2 | LO CO2.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO2 | LO CO3.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO6.LO1 | LO CO6.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO6.LO2 | LO CO6.LO2 condition is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 27.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 6 → 0 · round 1 accepted (6→1); round 2 rejected (1→1); round 3 accepted (1→0)
- los: errors 8 → 0 · round 1 accepted (8→0)
- structure: errors 1 → 0 · round 1 rejected (1→2); round 2 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Constraint SC1 requests exactly 15 Course Outcomes, which exceeds standard institutional practice and guidelines.
- constraints: co. count: Creating exactly 15 Course Outcomes (SC1) is unusually high for a standard 4-credit course and may conflict with standard granular mapping guidelines.
- cos: SC1: Special constraint SC1 mandates exactly 15 Course Outcomes, which significantly exceeds the typical IIIT-D guideline of 4 to 5 COs and may lead to granularity overlap.
- los: Special constraint SC1: The special constraint SC1 mandates exactly 15 Course Outcomes, but the provided context data defines 6 Course Outcomes. We have created 12 Learning Outcomes (2 per CO) matching the provided 6 COs to satisfy structural and count limits (total LOs between 10 and 20). If 15 COs are strictly required, the curriculum intake needs to be expanded.
- los: Hours budget: The calculated total hours (Lecture: 29, Tutorial: 10, Lab: 20) are slightly below the target budget (Lecture: 39, Tutorial: 13, Lab: 26) due to the 6 COs provided. Additional topics or project phases can scale these hours to match the exact LTP budget.
- structure: SC1: Special constraint SC1 asks for exactly 15 Course Outcomes, but the context provides only 6 Course Outcomes (CO1 through CO6). The module structure is built strictly around the provided 6 COs.
- narrative: SC1: The approved graph contains 6 course outcomes (CO1-CO6), whereas negative/special constraint SC1 states 'CRITICAL: Create exactly 15 Course Outcomes.' This mismatch should be reviewed.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules follow a logical progression from foundational agentic development environments and tool orchestration to specification-driven design, loop engineering, and comprehensive testing, building directly upon the software engineering fundamentals required from prerequisite course CSE201.
- **assessment rationale:** The assessment mix comprises quizzes, assignments, a midsem exam, an endsem exam, and a project, aligning with practical course outcomes that require both conceptual understanding and hands-on implementation of AI-native developer workflows.
- **positioning rationale:** Unlike CSE701, which investigates data-driven and research perspectives, or CSE594A, which focuses on foundational agentic reasoning, this course emphasizes practical, end-to-end agentic software development, tool use, and loop engineering.