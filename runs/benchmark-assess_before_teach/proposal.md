# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-assess_before_teach` · generated deterministically from the design graph · validator status: **3 errors, 6 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level specified without a concrete course code. | professor |
| — | CONFLICT ['special_constraints', 'semester_weeks'] | — | Special constraint SC1 mandates scheduling the final exam in week 2 covering week 14 topics, which contradicts standard academic calendars and semester progression. | professor |
| — | CONFLICT ['K15', 'UGREG-2025§2'] | — | Special constraint SC1 mandates the final exam in week 2 covering week 14, which contradicts UGREG-2025§2 stating the semester has 13 weeks and end-semester examinations are at the end of the semester. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with increasingly capable coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. Target students acquire the ability to configure AI-assisted coding tools and agent skills using agent orchestration frameworks, construct executable specifications and planning artifacts from requirements, analyse developer workflows and execution logs to diagnose failures, and assess the reliability and correctness of agent-generated code through automated test suites and evaluation harnesses. The course is taught through a combination of lectures, tutorials, and practical laboratory work, supported by hands-on coding projects.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students require strong software development and testing fundamentals to evaluate AI-generated code and integrate coding agents. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 ('Topics in Software Engineering: AI in SE') <context name="candidates">[{"uid": "CSE701", ...}]</context> has some overlap in mining software data and assisting code review, the new course focuses specifically on modern AI-native software development, agentic workflows, MCP, and loop engineering rather than general data-driven software engineering research.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure AI-assisted coding tools and agent skills, using an agent orchestration framework and Model Context Protocol, such that every configured tool connects successfully without authentication or protocol errors.** `[CORPUS, USER]`  
verb *configure* · behaviour *AI-assisted coding tools and agent skills* · condition *using an agent orchestration framework and Model Context Protocol* · degree *such that every configured tool connects successfully without authentication or protocol errors* · evidence: lab_task, programming_assignment · marks share (computed): 26.33%

- CO1.LO1 (L1) Identify the architectural components of agent orchestration frameworks and Model Context Protocol specifications, listing at least three core protocol primitives from the specification document.
- CO1.LO2 (L3) Configure AI-assisted coding tools and agent skills using an orchestration framework, producing output that matches the reference for 2 supplied tool configurations.
- CO1.LO3 (L3 ★capstone) Configure individual tool parameters and authentication tokens for an agent skill set, using an agent orchestration framework and Model Context Protocol, such that every configured tool connects successfully without authentication or protocol errors.

**CO2 (L3, procedural) — Construct executable specifications and planning artifacts, for a given set of user requirements, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *construct* · behaviour *executable specifications and planning artifacts* · condition *for a given set of user requirements* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 15.83%

- CO2.LO1 (L3 ★capstone) Construct executable specifications, for a supplied requirements document containing at most 5 use cases, covering every use case in the supplied requirements document.
- CO2.LO2 (L3) Construct user stories and workflow sequences, using a requirements template, covering at least two user roles.

**CO3 (L4, conceptual) — Analyse developer workflows and loop engineering setups, using execution logs from an AI-assisted coding environment, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *analyse* · behaviour *developer workflows and loop engineering setups* · condition *using execution logs from an AI-assisted coding environment* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, report · marks share (computed): 32.0%

- CO3.LO1 (L4) Examine developer workflows and loop engineering setups, using execution logs from an AI-assisted coding environment, identifying at least one failure cause with supporting log evidence.
- CO3.LO2 (L4 ★capstone) Analyse multi-agent execution traces, for a multi-agent execution trace of at most 500 lines, identifying at least three distinct failure causes with supporting log evidence.

**CO4 (L5, metacognitive) — Assess the reliability and correctness of agent-generated code, through automated test suites and evaluation harnesses, with all public tests passing and no warnings from the configured static analyser.** `[CORPUS, USER]`  
verb *assess* · behaviour *the reliability and correctness of agent-generated code* · condition *through automated test suites and evaluation harnesses* · degree *with all public tests passing and no warnings from the configured static analyser* · evidence: programming_assignment, code_review · marks share (computed): 15.83%

- CO4.LO1 (L5 ★capstone) Assess agent-generated code modules, for a supplied agent-generated module of at most 300 lines, with all public tests passing and no warnings from the configured static analyser.
- CO4.LO2 (L5) Assess code coverage and static analysis alerts, using a testing framework report, with at least 80 percent test coverage achieved.

**CO5 (L5, metacognitive) — Assess an AI-native software development process, for a supplied complex project description, such that the delivered system satisfies every acceptance criterion agreed at the first milestone while justifying each design decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *assess* · behaviour *an AI-native software development process* · condition *for a supplied complex project description* · degree *such that the delivered system satisfies every acceptance criterion agreed at the first milestone while justifying each design decision against at least one stated requirement* · evidence: project_deliverable, presentation · marks share (computed): 10.0%

- CO5.LO1 (L5 ★capstone) Assess an AI-native software development process, for an end-to-end multi-agent capstone project implementation, such that the delivered system satisfies every acceptance criterion agreed at the first milestone while justifying each design decision against at least one stated requirement.
- CO5.LO2 (L5) Assess system integration deliverables, using milestone evaluation rubrics, demonstrating live with two scenario walkthroughs chosen by the evaluator.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Model Context Protocol overview and core primitives (M1.T1)<br>Agent skills structure and context engineering setup (M1.T2) | CO1.LO1 | CO1 | Worked trace-diagnosis of 3 Model Context Protocol primitives in pairs. |  |
| 2 | Tool use configuration and agent framework installation (M1.T3)<br>MCP connection handling and authentication tokens (M1.T4) | CO1.LO2, CO1.LO3 | CO1 | Problem-solving session debugging connection handling and token authentication errors. | A:Quiz1 (quiz); A:Assign1 released |
| 3 | Spec-driven development and requirements engineering (M2.T1) | CO2.LO1 | CO2 | Peer review of requirements specifications for consistency and completeness. |  |
| 4 | Requirements to executable specifications conversion (M2.T2) | CO2.LO1 | CO2 | Worked trace-diagnosis of failing executable specifications. | A:Assign1 due; A:Assign2 released |
| 5 | User stories and workflow sequences construction (M2.T3) | CO2.LO2 | CO2 | Group mapping exercise linking user stories to workflow sequence diagrams. |  |
| 6 | Developer workflows log analysis and failure parsing (M3.T1)<br>Loop engineering setups and iterative development loops (M3.T2) | CO3.LO1 | CO3 | Worked trace-diagnosis of 3 failing developer workflow logs. | A:Assign2 due; A:ProjectMilestone1 released |
| 7 | Loop engineering setups and iterative development loops (M3.T2)<br>Software factories failure analysis and multi-agent execution traces (M3.T3) | CO3.LO1, CO3.LO2 | CO3 | Analysis of multi-agent execution traces in small groups to identify failure causes. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Automated testing and evaluation harnesses for agent code (M4.T1)<br>Reliability assessment and static analyser integration (M4.T2) | CO4.LO1 | CO4 | Walkthrough of static analyser warning reports and remediation strategies. | A:Assign3 released |
| 9 | Reliability assessment and static analyser integration (M4.T2)<br>Code coverage and static analysis alerts assessment (M4.T3) | CO4.LO1, CO4.LO2 | CO4 | Problem-solving on improving test coverage metrics for edge cases. | A:ProjectMilestone1 due |
| 10 | Code coverage and static analysis alerts assessment (M4.T3)<br>Emerging developer tools integration and project management (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Discussion and scoping of capstone milestone acceptance criteria. | A:Assign3 due; A:ProjectFinal released |
| 11 | Emerging developer tools integration and project management (M5.T1)<br>Hands-on coding projects and multi-agent implementation (M5.T2) | CO5.LO1 | CO5 | Design review and troubleshooting for multi-agent project implementations. |  |
| 12 | System integration deliverables and milestone scenario walkthroughs (M5.T3) | CO5.LO2 | CO5 | Dry-run scenario walkthroughs and rubric assessment preparation. |  |
| 13 |  |  |  |  | A:ProjectFinal due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Introduction to MCP and Environment Setup** — Explore initial architecture concepts and set up local environment components. |  | Student development machines, software development environments |
| 2 | **Tool Configuration and Authentication** — Configure tool parameters and authentication tokens for an agent skill set using orchestration framework. | CO1.LO2, CO1.LO3 | Student development machines, access to AI coding tools/APIs |
| 3 | **Spec-Driven Development Practice** — Construct executable specifications from supplied requirements documents covering multiple use cases. | CO2.LO1 | Student development machines, software development environments |
| 4 | **Requirements to Executable Specifications** — Convert requirements into executable specifications and validate against test harness. | CO2.LO1 | Student development machines, software development environments |
| 5 | **User Stories and Workflow Sequences** — Construct user stories and workflow sequences covering at least two user roles using templates. | CO2.LO2 | Student development machines |
| 6 | **Log Analysis and Loop Engineering** — Examine developer workflows and parse logs to identify failure causes in iterative development loops. | CO3.LO1 | Student development machines, software development environments |
| 7 | **Mid-Sem Break / Catch-up Lab** — Open lab session for catch-up and review of multi-agent execution traces. | CO3.LO2 | Student development machines |
| 8 | **Automated Testing and Reliability Assessment** — Construct automated testing and evaluation harnesses for agent code with static analysers. | CO4.LO1 | Student development machines, software development environments |
| 9 | **Code Coverage and Static Analysis** — Assess code coverage and static analysis alerts using testing framework reports. | CO4.LO2 | Student development machines, software development environments |
| 10 | **Developer Tools Integration** — Integrate emerging developer tools and set up project management pipelines. | CO5.LO1 | Student development machines, access to AI coding tools/APIs |
| 11 | **Multi-Agent Implementation Project** — Build hands-on coding projects implementing multi-agent workflows. | CO5.LO1 | Student development machines, access to AI coding tools/APIs |
| 12 | **System Integration Walkthroughs** — Perform system integration deliverables and milestone scenario walkthroughs. | CO5.LO2 | Student development machines, TA support |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W2→W2) | — | tool-use |  |
| assignment | 25.0 | A:Assign1 (W2→W4), A:Assign2 (W4→W6), A:Assign3 (W8→W10) | — | implement, design, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data |  |
| project | 20.0 | A:ProjectMilestone1 (W6→W9), A:ProjectFinal (W10→W13) | — | design, implement, evaluate-critique, written-communication, oral-presentation |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 26.33%, CO2 15.83%, CO3 32.0%, CO4 15.83%, CO5 10.0%

## 10. Resource material

Policy: **mixed** — Due to the fast-moving nature of AI-native software development and coding agents, a combination of specialized books, framework documentation, and recent research papers is utilized.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Agentic Design Patterns*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T2, M3.T2 |
| reading |  (None). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M1.T1, M1.T4 |
| reference | Srinivasan Sekar (2026). *Under the Hood: The Protocol Specification*. | 10.1007/979-8-8688-2364-0_6 | yes | M1.T1 |
| reading | Yujia Li, Shunyu Yao, Guanzhi Wang, John Yang, Alexander Novikov, Bogdan Georgiev (2024). *1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022. 2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022. 3) Wang, Guanzhi, et al. "Voyager: An Open-Ended Embodied Agent with Large Language Models." TMLR 2023. 4) Yang, John, et al. "Swe-agent: Agent-computer interfaces enable automated software engineering." NeurIPS 2024. 5) Novikov, Alexander, et al. "AlphaEvolve: A coding agent for scientific and algorithmic discovery." arXiv:2506.13131, 2025. 6) Georgiev, Bogdan, et al. "Mathematical exploration and discovery at scale." arXiv:2511.02864, 2025.*. | R:hash:1-li-yujia-et-al-competition-level-code- | NO: candidate_id not in retrieved candidates | M3.T3, M4.T1 |
| reference | Ziqian Bi, Junfeng Hao, Yue Ma, Ye Tao (2026). *Benchmark, Agent, and Tool-Use Harnesses for Large Language Models: A Taxonomy of Evaluation Infrastructure*. | 10.20944/preprints202609.0236.v1 | yes | M4.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 2 [2] |  | 3 [3] |
| CO2 | 2 [unclaimed] | 3 [3] |  | 3 [unclaimed] |
| CO3 | 3 [3] | 3 [unclaimed] | 2 [unclaimed] | 3 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [3] |  | 3 [2] |
| CO5 |  | 3 [3] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO9: Configuring modern AI-assisted coding tools and agent frameworks directly demonstrates the use of advanced computing tools. (activities: tool-use)
- CO1→PO4: Setting up agent tools contributes to implementing and deploying computer-based application environments. (activities: implement)
- CO2→PO4: Constructing executable specifications and planning artifacts constitutes the core design phase of computer-based systems. (activities: design)
- CO3→PO3: Analysing execution logs and loop engineering setups involves diagnosing problems and adapting techniques for developer workflows. (activities: analyse-data)
- CO4→PO4: Evaluating agent-generated code using test suites directly aligns with system evaluation and quality assurance. (activities: evaluate-critique)
- CO4→PO9: Using automated test suites and static analysers exercises advanced tool usage. (activities: tool-use)
- CO5→PO4: Assessing a complete AI-native software development process and delivered system evaluates a complex computer-based application. (activities: evaluate-critique)
- CO5→PO7: Justifying design decisions in project deliverables and presentations requires effective technical communication. (activities: written-communication, oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1, M1.T2 | 1 | A:Quiz1@L1, A:Midsem@L1 |
| CO1.LO2 | L3 | M1.T3 | 2 | A:Assign1@L3 |
| CO1.LO3 | L3 | M1.T4 | 2 | A:Assign1@L3 |
| CO2.LO1 | L3 | M2.T1, M2.T2 | 3, 4 | A:Assign2@L3, A:Endsem@L3 |
| CO3.LO1 | L4 | M3.T1, M3.T2 | 6, 7 | A:Midsem@L4, A:Endsem@L4 |
| CO3.LO2 | L4 | M3.T3 | 7 | A:ProjectMilestone1@L4 |
| CO4.LO1 | L5 | M4.T1, M4.T2 | 8, 9 | A:Assign3@L5, A:Endsem@L5 |
| CO5.LO1 | L5 | M5.T1, M5.T2 | 10, 11 | A:ProjectFinal@L5 |
| CO2.LO2 | L3 | M2.T3 | 5 | A:Assign2@L3 |
| CO4.LO2 | L5 | M4.T3 | 9, 10 | A:Assign3@L5 |
| CO5.LO2 | L5 | M5.T3 | 12 | A:ProjectFinal@L5 |

## Appendix C — Modules and topics

**M1 Agent Orchestration and Model Context Protocol** (primary CO1)
- M1.T1 Model Context Protocol overview and core primitives — 1.5 h · LOs CO1.LO1
- M1.T2 Agent skills structure and context engineering setup — 1.5 h · LOs CO1.LO1 · requires M1.T1
- M1.T3 Tool use configuration and agent framework installation — 1.5 h · LOs CO1.LO2 · requires M1.T2
- M1.T4 MCP connection handling and authentication tokens — 1.5 h · LOs CO1.LO3 · requires M1.T3
**M2 Specification and Planning for AI-Driven Systems** (primary CO2)
- M2.T1 Spec-driven development and requirements engineering — 3.0 h · LOs CO2.LO1 · requires M1.T4
- M2.T2 Requirements to executable specifications conversion — 3.0 h · LOs CO2.LO1 · requires M2.T1
- M2.T3 User stories and workflow sequences construction — 3.0 h · LOs CO2.LO2 · requires M2.T2
**M3 Developer Workflows and Loop Engineering Analysis** (primary CO3)
- M3.T1 Developer workflows log analysis and failure parsing — 2.0 h · LOs CO3.LO1 · requires M2.T3
- M3.T2 Loop engineering setups and iterative development loops — 2.0 h · LOs CO3.LO1 · requires M3.T1
- M3.T3 Software factories failure analysis and multi-agent execution traces — 2.0 h · LOs CO3.LO2 · requires M3.T2
**M4 Code Evaluation, Testing, and Reliability Assessment** (primary CO4)
- M4.T1 Automated testing and evaluation harnesses for agent code — 2.0 h · LOs CO4.LO1 · requires M3.T3
- M4.T2 Reliability assessment and static analyser integration — 2.0 h · LOs CO4.LO1 · requires M4.T1
- M4.T3 Code coverage and static analysis alerts assessment — 3.0 h · LOs CO4.LO2 · requires M4.T2
**M5 Capstoning and AI-Native Project Integration** (primary CO5)
- M5.T1 Emerging developer tools integration and project management — 2.5 h · LOs CO5.LO1 · requires M4.T3
- M5.T2 Hands-on coding projects and multi-agent implementation — 2.5 h · LOs CO5.LO1 · requires M5.T1
- M5.T3 System integration deliverables and milestone scenario walkthroughs — 2.5 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 35.5 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | substantive | CSE701 focuses broadly on data mining and AI applications in software engineering research, whereas the new course centers on practical, agent-driven engineering practices, tool use, and workflow orchestration. |
| CSE594A | 0.08 | complementary | CSE594A focuses on the theoretical and algorithmic foundations of agentic reasoning, whereas the new course applies agents directly to software development workflows. |
| CSE582 | 0.067 | superficial | CSE582 deals with software maintenance, product lines, and re-engineering in traditional settings, whereas the new course addresses AI-native and agent-assisted generation. |
| CSE581 | 0.034 | superficial | CSE581 covers traditional systems analysis and requirements theories, unlike the spec-driven AI development workflows in the new course. |
| AI501 | 0.034 | superficial | AI501 is a core Machine Learning course covering foundational theory, while the new course uses ML/AI tools exclusively for software engineering tasks. |
| CSE201 | 0.017 | superficial | CSE201 establishes object-oriented programming fundamentals and JUnit testing, which serve as background knowledge rather than overlapping course content. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Literature review structure and project evaluation methodologies Avoid: Excessive focus on mining historical software repositories instead of active AI-native workflows
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Agentic protocols and frameworks such as MCP Avoid: Deep mathematical and algorithmic reasoning focus tailored for scientific problem-solving
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation style and team-driven development practices Avoid: Traditional open-source licensing and manual issue tracking without AI agents

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Agentic Design Patterns' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:1-li-yujia-et-al-competition-level-code- | resource '1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022. 2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022. 3) Wang, Guanzhi, et al. " |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 degree is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 50.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 9 → 0 · round 1 accepted (9→5); round 2 accepted (5→4); round 3 accepted (4→0)
- structure: errors 8 → 0 · round 1 accepted (8→0)
- assessment: errors 4 → 0 · round 1 accepted (4→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: SC1 requests scheduling the final exam in week 2 covering week 14 topics, violating standard chronological course flow and examination regulations.
- positioning: special_constraints: SC1 specifies that the final exam must be scheduled in week 2 covering topics from week 14, which contradicts standard academic calendars and chronological course delivery.
- constraints: Special constraint SC1: Week 2 final exam covering week 14 is logically inconsistent with a 13-week semester structure.
- cos: SC1: Special constraint SC1 mandates scheduling the final exam in week 2 covering week 14 topics, which contradicts the standard 13-week semester structure.
- structure: Special Constraint SC1: Scheduling a final exam in week 2 covering week 14 topics contradicts standard 13-week academic calendar regulations; flagging for administrative review.
- narrative: SC1: Special constraint SC1 specifies scheduling the final exam in week 2 covering week 14, which conflicts with the standard 13-week semester structure.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules follow a logical progression from foundational agent orchestration and specification frameworks to workflow analysis, reliability assessment, and final project integration. This sequence relies on core software development and testing fundamentals established in prerequisite courses such as CSE201.
- **assessment rationale:** The assessment mix—comprising quizzes, assignments, a mid-semester examination, a project, and an end-semester examination—aligns with the course outcomes by balancing theoretical understanding with rigorous practical evaluation of agent-assisted software development, automated testing, and workflow execution.
- **positioning rationale:** Unlike CSE701, which focuses on data mining and AI applications in software engineering research, or CSE594A, which studies theoretical foundations of agentic reasoning, this course centers specifically on practical, agent-driven engineering practices, tool use, and workflow orchestration. It differs from traditional software engineering courses like CSE582 and CSE581 by directly addressing AI-native and agent-assisted generation.