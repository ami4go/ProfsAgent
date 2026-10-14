# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-impossible_hours` · generated deterministically from the design graph · validator status: **0 errors, 9 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | The level is specified qualitatively as 'Advanced undergraduate' which implies 3rd or 4th year (300/400 level), but no specific course code or numeric level is provided. | professor |
| — | CONFLICT ['special_constraints'] | — | The request for 300 lecture hours in a single semester is physically impossible and directly contradicts standard IIIT-D regulations (UGREG-2025§4(2)a), which state that a standard 4-credit course has about 3 hours of lectures per week (totaling ~39 hours per semester). | professor |
| — | CONFLICT ['SC1', 'UGREG-2025§2'] | — | The professor specified 300 lecture hours in a single semester (SC1), which directly conflicts with regulation UGREG-2025§2 and UGREG-2025§4(2)a specifying 13 weeks of teaching and about 39 lecture hours for a 4-credit course. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. This course matters for third and fourth-year Bachelor of Technology students in Computer Science and Engineering by bridging core software foundations and emerging AI-assisted engineering practices. Upon completing the course, students will be able to configure AI coding agents and tool integrations using orchestration frameworks, construct executable specifications and context engineering pipelines from requirements, deconstruct development workflows and failure causes using execution traces, evaluate code reliability using automated testing harnesses, and assess end-to-end software factories. The course is taught through a combination of lectures, tutorials, and laboratory sessions incorporating hands-on coding and project work.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm | Students require strong programming and software engineering fundamentals, including automated testing and structured code design, to effectively engage with agent-assisted software development. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 explores AI applications in software engineering and data-driven SE, the new course specifically focuses on modern AI-native software development, agentic workflows, and coding agents rather than general AI techniques applied to software engineering repositories.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure AI coding agents and tool integrations using an agent orchestration framework, meeting the stated interface specification for every public method.** `[CORPUS, USER]`  
verb *Configure* · behaviour *AI coding agents and tool integrations* · condition *using an agent orchestration framework* · degree *meeting the stated interface specification for every public method* · evidence: lab_task, programming_assignment · marks share (computed): 26.0%

- CO1.LO1 (L2) Identify the core components and communication protocols of an agent orchestration framework using supplied documentation.
- CO1.LO2 (L3 ★capstone) Configure MCP server bindings and tool call intercepts using an agent orchestration framework, meeting the stated interface specification for every public method.

**CO2 (L3, procedural) — Construct executable specifications and context engineering pipelines from natural language requirements, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *Construct* · behaviour *executable specifications and context engineering pipelines* · condition *from natural language requirements* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 16.0%

- CO2.LO1 (L3) Examine natural language requirements to extract structured use cases and domain entities for context engineering.
- CO2.LO2 (L3 ★capstone) Construct prompt templates and context window management scripts from natural language requirements, covering every use case in the supplied requirements document.

**CO3 (L4, conceptual) — Deconstruct AI-assisted software development workflows and loop engineering strategies for a supplied codebase, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *Deconstruct* · behaviour *AI-assisted software development workflows and loop engineering strategies* · condition *for a supplied codebase* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, code_review · marks share (computed): 23.83%

- CO3.LO1 (L2) Trace execution logs and developer workflows to identify anomalies in agent-assisted development iterations.
- CO3.LO2 (L4 ★capstone) Deconstruct execution traces and retry loop patterns for a supplied codebase, identifying at least three distinct failure causes with supporting log evidence.

**CO4 (L5, procedural) — Evaluate the reliability and performance of agent-generated code using automated testing and evaluation harnesses, such that at least 80% of the provided test cases pass.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *the reliability and performance of agent-generated code* · condition *using automated testing and evaluation harnesses* · degree *such that at least 80% of the provided test cases pass* · evidence: programming_assignment, project_deliverable · marks share (computed): 18.33%

- CO4.LO1 (L3) Implement automated test harnesses for validating outputs generated by coding agents.
- CO4.LO2 (L5 ★capstone) Evaluate agent execution latency and accuracy metrics using automated testing and evaluation harnesses, such that at least 80% of the provided test cases pass.

**CO5 (L5, metacognitive) — Assess an end-to-end AI-native software factory incorporating coding agents, automated workflows, and deployment pipelines, justifying each design decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *Assess* · behaviour *an end-to-end AI-native software factory* · condition *incorporating coding agents, automated workflows, and deployment pipelines* · degree *justifying each design decision against at least one stated requirement* · evidence: project_deliverable, design_document · marks share (computed): 15.83%

- CO5.LO1 (L2) Compare alternative AI-native software factory architectures incorporating coding agents, automated workflows, and deployment pipelines.
- CO5.LO2 (L5 ★capstone) Assess agent communication protocols and CI/CD triggers within an end-to-end AI-native software factory, justifying each design decision against at least one stated requirement.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Agent orchestration framework components (M1.T1)<br>Communication protocols and developer workflows (M1.T2) | CO1.LO1 | CO1 | Worked trace-diagnosis of sample orchestrator logs in pairs, identifying component message flows. |  |
| 2 | MCP server bindings and tool call intercepts (M1.T3)<br>Agent skills and tool integration specifications (M1.T4) | CO1.LO2 | CO1 | Worked trace-diagnosis of 3 failing MCP tool call intercepts, in pairs. |  |
| 3 | Agent skills and tool integration specifications (M1.T4)<br>Requirements engineering and domain entity extraction (M2.T1)<br>Spec-driven development use case analysis (M2.T2) | CO1.LO2, CO2.LO1 | CO1, CO2 | Entity extraction and structured use case derivation exercise on a provided natural language specification. | A:Assignment1 released |
| 4 | Spec-driven development use case analysis (M2.T2)<br>Context engineering pipelines and prompt templates (M2.T3) | CO2.LO1, CO2.LO2 | CO2 | Worked trace-diagnosis of ambiguous prompt templates, refactoring them into structured use case mappings. | A:Quiz1 (quiz); A:Assignment1 due |
| 5 | Requirements to executable specifications mapping (M2.T4)<br>Execution log tracing and developer workflow inspection (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Trace inspection and anomaly identification exercise using sample execution logs from agent-assisted coding iterations. | A:Assignment2 released |
| 6 | Execution log tracing and developer workflow inspection (M3.T1)<br>Iterative development anomaly detection (M3.T2)<br>Loop engineering and retry strategies (M3.T3) | CO3.LO1, CO3.LO2 | CO3 | Worked trace-diagnosis of 3 iterative development anomaly logs, identifying root causes in pairs. | A:Assignment2 due; A:ProjectMilestone1 released |
| 7 | Loop engineering and retry strategies (M3.T3)<br>Assisting code review and failure diagnosis (M3.T4) | CO3.LO2 | CO3 | Mid-semester review and problem-solving session on retry loop pattern failures. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Automated test harness construction for coding agents (M4.T1)<br>Unit testing and static analysis integration (M4.T2) | CO4.LO1 | CO4 | Peer review of unit test cases and static analysis configurations for coding agent outputs. | A:ProjectMilestone2 released |
| 9 | Agent execution latency and accuracy metrics (M4.T3)<br>Evaluation frameworks and reliability benchmarks (M4.T4) | CO4.LO2 | CO4 | Worked calculation of agent execution latency percentiles and accuracy metrics on sample benchmark runs. | A:ProjectMilestone1 due |
| 10 | Evaluation frameworks and reliability benchmarks (M4.T4)<br>AI-native software factory architectures (M5.T1)<br>Automated workflows and deployment pipelines (M5.T2) | CO4.LO2, CO5.LO1 | CO4, CO5 | Comparative analysis discussion of alternative AI-native software factory architectural blueprints. | A:ProjectFinal released |
| 11 | Automated workflows and deployment pipelines (M5.T2)<br>Agent communication protocols and CI/CD triggers (M5.T3) | CO5.LO1, CO5.LO2 | CO5 | Architectural tradeoff analysis and justification discussion for automated deployment pipelines. | A:ProjectMilestone2 due |
| 12 | Agent communication protocols and CI/CD triggers (M5.T3)<br>Emerging developer tools and capstone project integration (M5.T4) | CO5.LO2 | CO5 | Capstone project design review and protocol justification critique in small groups. |  |
| 13 |  |  |  |  | A:ProjectFinal due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Lab setup and orchestration framework review** — Verify local developer environments, install required tooling, and inspect sample agent orchestration configurations. | CO1.LO1 | Python, Git, Student development machines |
| 2 | **MCP server bindings and tool call intercepts** — Configure MCP server bindings and implement tool call intercepts meeting interface specifications. | CO1.LO2 | Python, MCP SDK, Student development machines |
| 3 | **Agent skills and tool integration specifications** — Develop and test agent skills and tool integration specifications against functional requirements. | CO1.LO2 | Python, Agent development framework |
| 4 | **Context engineering pipelines and prompt templates** — Construct prompt templates and context window management scripts from natural language requirements. | CO2.LO2 | Python, Prompt engineering tools |
| 5 | **Requirements to executable specifications mapping** — Map natural language requirements to executable specifications and validate context pipelines. | CO2.LO2 | Python, Executable specification runners |
| 6 | **Loop engineering and retry strategies** — Implement loop engineering and retry strategies for agentic workflows. | CO3.LO2 | Python, Execution tracing tools |
| 7 | **Execution trace deconstruction and failure diagnosis** — Deconstruct execution traces and retry loop patterns to identify failure causes with log evidence. | CO3.LO2 | Python, Log analysis tools |
| 8 | **Automated test harness construction** — Implement automated test harnesses for validating outputs generated by coding agents. | CO4.LO1 | Python, Pytest, Static analysis tools |
| 9 | **Evaluation frameworks and latency metrics** — Evaluate agent execution latency and accuracy metrics using automated testing and evaluation harnesses. | CO4.LO2 | Python, Evaluation benchmark frameworks |
| 10 | **Agent evaluation benchmarks** — Run evaluation frameworks and reliability benchmarks to achieve target pass rates on test cases. | CO4.LO2 | Python, Evaluation benchmark frameworks |
| 11 | **Agent communication protocols and CI/CD triggers** — Integrate agent communication protocols and CI/CD triggers within an AI-native software factory. | CO5.LO2 | GitHub Actions, CI/CD pipelines, Python |
| 12 | **Capstone project integration and emerging developer tools** — Incorporate emerging developer tools into capstone project integration and end-to-end pipelines. | CO5.LO2 | Software development environments, AI coding tools/APIs |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (needs_confirmation); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W4→W4) | — | analyse-data |  |
| assignment | 20.0 | A:Assignment1 (W3→W4), A:Assignment2 (W5→W6) | — | implement, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, design |  |
| project | 25.0 | A:ProjectMilestone1 (W6→W9), A:ProjectMilestone2 (W8→W11), A:ProjectFinal (W10→W13) | — | design, implement, evaluate-critique, teamwork |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique, design |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 26.0%, CO2 16.0%, CO3 23.83%, CO4 18.33%, CO5 15.83%

## 10. Resource material

Policy: **reading_list** — The course covers fast-moving topics in AI-native software development and coding agents where standard comprehensive textbooks are not yet fully established; a reading list combining recent book chapters, conference proceedings, and developer guides is used instead.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reading | John E. Robert, Ipek Ozkaya, Douglas C. Schmidt (2026). *Transforming Software Engineering and Software Acquisition with Large Language Models*. | 10.1201/9781003492252-7 | yes | M5.T1 |
| reading | Jerin George Mathew, Jacopo Rossi (2025). *Large Language Model Agents*. | 10.1007/978-3-031-92285-5_8 | yes | M1.T1 |
| reading | Aymen El Amri (2024). *LLM Prompt Engineering for Developers*. | 9781836201724 | yes | M2.T3 |
| reading | Mohammed A. Shehab, Mohammad Wardat, Safwan Omari, Yaser Jararweh (2024). *Evaluating Large Language Models for Code Generation: Assessing Accuracy, Quality, and Performance*. | 10.1109/fllm63129.2024.10852439 | yes | M4.T3 |
| reading | Weixi Tong, Tianyi Zhang (2024). *CodeJudge: Evaluating Code Generation with Large Language Models*. | 10.18653/v1/2024.emnlp-main.1118 | yes | M4.T4 |
| reading | Mukul Paras Potta, Shouvick Mondal, Yogesh Kumar Meena (2025). *Evaluating Pre-Trained Large Language Models Using Simulated Human Inputs for Python Code Generation*. | 10.2139/ssrn.5293364 | yes | M4.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO9 |
|---|---|---|---|---|
| CO1 | 3 [unclaimed] | 3 [3] |  | 2 [2] |
| CO2 | 2 [unclaimed] | 3 [3] |  | 3 [unclaimed] |
| CO3 | 3 [3] | 3 [unclaimed] | 2 [unclaimed] | 3 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 3 [2] |
| CO5 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring agents using frameworks directly exercises modern system tooling and implementation methodologies. (activities: implement, tool-use)
- CO1→PO9: Utilises advanced AI tool integrations in software development. (activities: tool-use)
- CO2→PO4: Constructing pipelines from requirements corresponds to designing and implementing system components. (activities: design, implement)
- CO3→PO3: Deconstructing workflows and identifying failure causes adapts analytical techniques to software problems. (activities: analyse-data)
- CO4→PO4: Evaluating agent-generated code using test harnesses directly maps to system evaluation. (activities: evaluate-critique)
- CO4→PO9: Uses automated evaluation harnesses for advanced AI systems. (activities: tool-use)
- CO5→PO4: Assessing an end-to-end software factory and justifying design decisions covers system design and evaluation. (activities: design, evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L2 | M1.T1, M1.T2 | 1 | A:Quiz1@L2, A:Midsem@L2 |
| CO1.LO2 | L3 | M1.T3, M1.T4 | 2, 3 | A:Assignment1@L3 |
| CO2.LO1 | L3 | M2.T1, M2.T2 | 3, 4 | A:Assignment2@L3, A:Midsem@L3 |
| CO2.LO2 | L3 | M2.T3, M2.T4 | 4, 5 | A:Assignment2@L3 |
| CO3.LO1 | L2 | M3.T1, M3.T2 | 5, 6 | A:Midsem@L2 |
| CO3.LO2 | L4 | M3.T3, M3.T4 | 6, 7 | A:ProjectMilestone1@L4, A:Endsem@L4 |
| CO4.LO1 | L3 | M4.T1, M4.T2 | 8 | A:ProjectMilestone2@L3 |
| CO4.LO2 | L5 | M4.T3, M4.T4 | 9, 10 | A:ProjectMilestone2@L5, A:Endsem@L5 |
| CO5.LO1 | L2 | M5.T1, M5.T2 | 10, 11 | A:ProjectFinal@L2 |
| CO5.LO2 | L5 | M5.T3, M5.T4 | 11, 12 | A:ProjectFinal@L5, A:Endsem@L5 |

## Appendix C — Modules and topics

**M1 Agent Orchestration Foundations** (primary CO1)
- M1.T1 Agent orchestration framework components — 1.5 h · LOs CO1.LO1
- M1.T2 Communication protocols and developer workflows — 1.5 h · LOs CO1.LO1 · requires M1.T1
- M1.T3 MCP server bindings and tool call intercepts — 2.0 h · LOs CO1.LO2 · requires M1.T2
- M1.T4 Agent skills and tool integration specifications — 2.0 h · LOs CO1.LO2 · requires M1.T3
**M2 Specification and Context Engineering** (primary CO2)
- M2.T1 Requirements engineering and domain entity extraction — 1.5 h · LOs CO2.LO1
- M2.T2 Spec-driven development use case analysis — 1.5 h · LOs CO2.LO1 · requires M2.T1
- M2.T3 Context engineering pipelines and prompt templates — 2.0 h · LOs CO2.LO2 · requires M2.T2, M1.T4
- M2.T4 Requirements to executable specifications mapping — 2.0 h · LOs CO2.LO2 · requires M2.T3
**M3 Workflow Inspection and Loop Engineering** (primary CO3)
- M3.T1 Execution log tracing and developer workflow inspection — 1.5 h · LOs CO3.LO1
- M3.T2 Iterative development anomaly detection — 1.5 h · LOs CO3.LO1 · requires M3.T1
- M3.T3 Loop engineering and retry strategies — 2.0 h · LOs CO3.LO2 · requires M3.T2
- M3.T4 Assisting code review and failure diagnosis — 2.0 h · LOs CO3.LO2 · requires M3.T3
**M4 Testing and Evaluation Harnesses** (primary CO4)
- M4.T1 Automated test harness construction for coding agents — 1.5 h · LOs CO4.LO1 · requires M1.T4
- M4.T2 Unit testing and static analysis integration — 1.5 h · LOs CO4.LO1 · requires M4.T1
- M4.T3 Agent execution latency and accuracy metrics — 2.0 h · LOs CO4.LO2 · requires M4.T2
- M4.T4 Evaluation frameworks and reliability benchmarks — 2.0 h · LOs CO4.LO2 · requires M4.T3
**M5 Software Factories and End-to-End Integration** (primary CO5)
- M5.T1 AI-native software factory architectures — 1.5 h · LOs CO5.LO1 · requires M1.T4, M2.T4
- M5.T2 Automated workflows and deployment pipelines — 1.5 h · LOs CO5.LO1 · requires M5.T1
- M5.T3 Agent communication protocols and CI/CD triggers — 2.5 h · LOs CO5.LO2 · requires M5.T2, M4.T4
- M5.T4 Emerging developer tools and capstone project integration — 2.5 h · LOs CO5.LO2 · requires M5.T3

Schedule: feasible · 36.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 covers data-driven SE and broad AI applications in SE (such as defect prediction and mining repositories), whereas the new course focuses strictly on operational agent-assisted development workflows, loop engineering, and context engineering for AI-native software production. |
| CSE581 | 0.034 | superficial | CSE581 deals with traditional systems analysis, design, and software development theories, whereas the new course focuses on automated specifications and execution via AI coding agents. |
| CSE582 | 0.067 | complementary | CSE582 covers product line engineering, maintenance, and re-engineering, while the new course addresses AI-driven software factories and developer workflows. |
| CSE594A | 0.08 | complementary | CSE594A focuses generally on agentic reasoning for algorithmic and mathematical problem solving, whereas the new course focuses specifically on software development tasks and coding agents. |
| CSE201 | 0.017 | complementary | CSE201 teaches object-oriented programming, unit testing, and design patterns in Java, serving as a foundational prerequisite for advanced software development courses. |
| AI501 | 0.034 | superficial | AI501 covers foundational machine learning theory and evaluation, whereas the new course applies engineering practices and evaluation specifically to AI-native developer workflows. |
| CSE583 | 0.0 | superficial | CSE583 covers open source software development processes and tools. |
| CSE665 | 0.0 | superficial | CSE665 covers foundational large language model architectures and NLP principles. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Research literature review structure and project evaluation methodologies from CSE701. Avoid: Focusing purely on repository data mining rather than interactive developer workflows.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Core concepts of agentic protocols (such as MCP) and agent infrastructures. Avoid: Excessive focus on mathematical and algorithmic problem-solving agents instead of software engineering agents.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Practical project structuring, team collaboration, and tooling integration. Avoid: Traditional open-source process topics that do not involve AI agent collaboration.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 6 → 0 · round 1 rejected (6→4); round 2 accepted (6→0)
- assessment: errors 2 → 0 · round 1 accepted (2→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: The requirement of 300 lecture hours in a single semester (SC1) is extremely high and violates standard academic regulations. This would require over 23 hours of lectures per week in a standard 13-week semester.
- positioning: Special Constraint SC1: Special constraint SC1 states 'The course must have 300 lecture hours in a single semester', which is physically impossible for a standard 4-credit course in a 13-week semester.
- constraints: SC1 lecture hours: Special constraint SC1 mandates 300 lecture hours for a 4-credit course, which is mathematically impossible within a 13-week semester given standard credit norms.
- structure: Special constraint SC1 lecture hours: SC1 requires 300 lecture hours, which is physically impossible within a 13-week semester with 3 lecture hours per week (39 total hours). The course structure follows the 39-hour budget.
- narrative: SC1: The constraint stating '300 lecture hours in a single semester' is numerically impossible for a standard 13-week semester with an LTP of 3-1-2.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress logically from foundational agent orchestration and tooling in M1 to specification and context engineering in M2. Building upon these concepts, M3 addresses workflow inspection and loop engineering, followed by automated testing and evaluation harnesses in M4. Finally, M5 integrates these elements into software factories. This sequence relies on the programming and software engineering fundamentals established in CSE201.
- **assessment rationale:** The assessment mix comprises quizzes (10%), assignments (20%), mid-semester examinations (20%), a project (25%), and end-semester examinations (25%). This distribution balances theoretical evaluation with practical, workflow-oriented understanding and hands-on experimentation through coding assignments and a capstone project, directly supporting the intended learning outcomes.
- **positioning rationale:** Unlike CSE701 which covers data-driven software engineering and broad AI applications like defect prediction, or CSE581 which deals with traditional systems analysis, this course focuses strictly on operational agent-assisted development workflows, loop engineering, and context engineering. It complements CSE582 by addressing AI-driven software factories rather than traditional product line engineering, and differs from CSE594A and AI501 by targeting software development tasks and engineering practices rather than algorithmic problem solving or foundational machine learning theory.