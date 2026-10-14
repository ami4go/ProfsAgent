# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-duplicate_outcomes` · generated deterministically from the design graph · validator status: **3 errors, 12 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | The level is specified as 'Advanced undergraduate' which typically maps to 3rd or 4th year (level 3 or 4), but the exact course code is not specified. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, focusing on how developers collaborate with coding agents. Designed for advanced undergraduate students, it covers defining intent, context engineering, structuring development workflows, and coordinating AI tools. Rather than serving as a general introduction to machine learning, a traditional programming course, or a theoretical study of large language models, it emphasizes practical, workflow-oriented software engineering. Students will learn to configure AI coding tools using Model Context Protocol servers, construct executable specifications from natural language requirements, and analyze iterative agentic debugging loops. They will also evaluate automated testing, deployment, and reliability metrics for agent-generated artifacts, culminating in the delivery of an end-to-end software application. The course is taught through three hours of lectures, one hour of tutorial, and two hours of practical labs per week over thirteen weeks, heavily incorporating hands-on development and a collaborative group project.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students must have strong programming fundamentals, object-oriented design skills, and familiarity with unit testing before undertaking hands-on AI-assisted software development projects. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While both courses explore the intersection of AI and Software Engineering, CSE701 is a level 7 research-oriented course focusing on applying ML models to SE data (e.g., defect prediction, log analysis), whereas this course is a level 3 practical course focusing on developer workflows and collaboration with coding agents.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure AI coding tools and agent skills within a given development environment, integrating Model Context Protocol servers to support developer workflows, such that all public integration checks pass and no configuration warnings are reported.** `[CORPUS, USER]`  
verb *Configure* · behaviour *AI coding tools and agent skills* · condition *within a given development environment, integrating Model Context Protocol servers to support developer workflows* · degree *such that all public integration checks pass and no configuration warnings are reported* · evidence: lab_task, programming_assignment · marks share (computed): 23.0%

- CO1.LO1 (L1) Identify the core components of AI-native developer workflows and agent skills within a supplied programming environment.
- CO1.LO2 (L3) Configure AI coding tools and agent interfaces for a given local workspace following standard setup guidelines.
- CO1.LO3 (L3 ★capstone) Configure Model Context Protocol servers within a given developer environment, such that all public integration checks pass and no configuration warnings are reported.

**CO2 (L3, procedural) — Construct executable specifications from natural language requirements using spec-driven development tools, for a supplied functional specification document, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *Construct* · behaviour *executable specifications from natural language requirements* · condition *using spec-driven development tools, for a supplied functional specification document* · degree *covering every use case in the supplied requirements document* · evidence: programming_assignment, design_document · marks share (computed): 14.0%

- CO2.LO1 (L1) Identify natural language requirements in a supplied functional specification document.
- CO2.LO2 (L3 ★capstone) Construct executable specifications using spec-driven development tools, covering every use case in the supplied requirements document.

**CO3 (L4, procedural) — Analyze agent-assisted software development loops and iterative workflows, for a supplied project codebase of at most 5000 lines of code within 60 minutes, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *Analyze* · behaviour *agent-assisted software development loops and iterative workflows* · condition *for a supplied project codebase of at most 5000 lines of code within 60 minutes* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, code_review · marks share (computed): 13.0%

- CO3.LO1 (L2) Trace agent-assisted software development loops and iterative workflows for a supplied project codebase.
- CO3.LO2 (L4 ★capstone) Analyze execution logs of a multi-agent software factory run for a supplied run of at most 5000 lines of log output, identifying the exact step where the agent loop diverged from the specification.

**CO4 (L5, conceptual) — Evaluate automated testing, deployment, and reliability metrics for an agent-generated software artifact, identifying at least three distinct reliability vulnerabilities, with a proposed mitigation for each.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *automated testing, deployment, and reliability metrics* · condition *for an agent-generated software artifact* · degree *identifying at least three distinct reliability vulnerabilities, with a proposed mitigation for each* · evidence: code_review, report · marks share (computed): 25.0%

- CO4.LO1 (L4) Examine automated testing and deployment metrics for an agent-generated software artifact against baseline performance standards.
- CO4.LO2 (L5 ★capstone) Evaluate the reliability of an agent-generated API client against a supplied suite of 50 edge-case integration tests, proposing a concrete architectural mitigation for the most critical failure mode.

**CO5 (L5, metacognitive) — Evaluate an end-to-end software application through collaborative agent workflows, such that the delivered system satisfies every acceptance criterion agreed at the first milestone and is demonstrated live with three scenario walkthroughs chosen by the evaluator.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *an end-to-end software application through collaborative agent workflows* · condition *such that the delivered system satisfies every acceptance criterion agreed at the first milestone* · degree *demonstrated live with three scenario walkthroughs chosen by the evaluator* · evidence: project_deliverable, presentation · marks share (computed): 25.0%

- CO5.LO1 (L5) Plan an end-to-end software application project using collaborative agent workflows and milestone criteria.
- CO5.LO2 (L5 ★capstone) Evaluate an end-to-end software application through collaborative agent workflows, demonstrated live, with three scenario walkthroughs chosen by the evaluator.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Core Components of AI-Native Workflows (M1.T1)<br>Local Workspace Configuration for AI Tools (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Analyze AI-native workflow architectures and compare local vs cloud-based developer environments in small groups. |  |
| 2 | Local Workspace Configuration for AI Tools (M1.T2)<br>Model Context Protocol (MCP) Architecture (M1.T3) | CO1.LO2, CO1.LO3 | CO1 | Troubleshoot local workspace configurations and resolve environment path conflicts in pairs. |  |
| 3 | Context Engineering and MCP Server Integration (M1.T4)<br>Requirements Engineering and Spec Parsing (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Peer review of MCP server configuration files to identify potential security and integration risks. | A:Quiz1 (quiz); A:Assign1 released |
| 4 | Requirements Engineering and Spec Parsing (M2.T1)<br>Executable Specifications and Spec-Driven Tools (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Parse a messy natural language specification document to extract clean functional requirements. | A:Assign1 due |
| 5 | Executable Specifications and Spec-Driven Tools (M2.T2)<br>Loop Engineering and Iterative Workflows (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Design test cases for executable specifications and map them to user stories. | A:Assign2 released |
| 6 | Multi-Agent Software Factories (M3.T2)<br>Execution Log Analysis and Debugging (M3.T3) | CO3.LO2 | CO3 | Trace a complex agent-assisted software development loop step-by-step on a sample codebase. | A:Quiz2 (quiz); A:Assign2 due |
| 7 | Execution Log Analysis and Debugging (M3.T3)<br>Automated Testing and Evaluation Metrics (M4.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Mid-sem review and problem-solving session on agent loop divergence scenarios. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Automated Testing and Evaluation Metrics (M4.T1)<br>Deployment Metrics and Baseline Performance (M4.T2) | CO4.LO1 | CO4 | Analyze automated testing metrics and calculate baseline performance scores for a sample artifact. |  |
| 9 | Reliability Evaluation of Agent-Generated API Clients (M4.T3) | CO4.LO2 | CO4 | Design a suite of 50 edge-case integration tests for a mock API client. | A:ProjM1 released |
| 10 | Project Planning and Collaborative Workflows (M5.T1)<br>Hands-on Coding with Emerging Developer Tools (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Collaborative project planning exercise: defining milestones and agent roles for a team project. |  |
| 11 | Hands-on Coding with Emerging Developer Tools (M5.T2)<br>Live Scenario Walkthroughs and System Evaluation (M5.T3) | CO5.LO2 | CO5 | Design scenario walkthroughs and evaluation rubrics for live system testing. | A:ProjM1 due |
| 12 | Live Scenario Walkthroughs and System Evaluation (M5.T3) | CO5.LO2 | CO5 | Peer feedback session on system evaluation results and live demo dry-runs. | A:ProjFinal released |
| 13 |  |  |  | Course wrap-up and discussion of emerging trends in AI-native developer tools. | A:ProjFinal due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Local Workspace Configuration** — Configure local development environments with AI coding assistants (e.g., VS Code, Cursor) and verify API connectivity to local and cloud LLMs. | CO1.LO2 | VS Code, Cursor, Local LLM APIs |
| 2 | **Model Context Protocol Server Setup** — Develop and configure a basic Model Context Protocol (MCP) server using Node.js or Python, verifying connection over standard input/output transports. | CO1.LO3 | Node.js, Python, MCP SDK |
| 3 | **Context Engineering and MCP Integration** — Integrate custom MCP servers with an AI client, configuring context engineering rules to pass all public integration checks without warnings. | CO1.LO3 | MCP Servers, SSE Transports |
| 4 | **Constructing Executable Specifications** — Construct executable specifications using Gherkin syntax and spec-driven tools like Cucumber to cover all use cases in a provided requirements document. | CO2.LO2 | Cucumber, Behave, Gherkin |
| 5 | **Spec-Driven Development Iteration** — Iterate on executable specifications to handle edge cases, running automated test suites to ensure complete coverage of the requirements. | CO2.LO2 | Spec-driven testing frameworks |
| 6 | **Multi-Agent Factory Execution** — Deploy and run a multi-agent software factory, capturing and saving execution logs of up to 5000 lines for subsequent analysis. | CO3.LO2 | Autogen, CrewAI |
| 7 | **Mid-Semester Catch-up and Open Lab** — Open lab session for students to catch up on pending lab exercises and receive additional TA support. No new content is introduced. |  |  |
| 8 | **Execution Log Analysis and Debugging** — Analyze execution logs from the multi-agent run to identify the exact step where the agent loop diverged from the specification. | CO3.LO2 | Log parsers, Python |
| 9 | **Reliability Evaluation of API Clients** — Evaluate the reliability of an agent-generated API client against a suite of 50 edge-case integration tests, identifying critical failure modes. | CO4.LO2 | Pytest, Integration test suites |
| 10 | **Collaborative Agent Workspaces** — Set up collaborative agent workflows using emerging developer tools to prepare for the end-to-end software application project. | CO5.LO2 | Git, GitHub, Collaborative agent tools |
| 11 | **Live Scenario Walkthrough Preparation** — Conduct live scenario walkthroughs of the collaborative agent system, testing against evaluator-selected scenarios to evaluate system performance. | CO5.LO2 | Live evaluation scripts |
| 12 | **System Evaluation and Live Demos** — Perform final system evaluations and live demonstrations of the end-to-end software application under three evaluator-selected scenario walkthroughs. | CO5.LO2 | Live evaluation scripts |
| 13 | **Final Project Showcase and Viva** — Final project showcase and viva session where teams present their completed agent-assisted software applications and receive final evaluations. | CO5.LO2 | Presentation tools |

Infrastructure: Student development machines (available); Software development environments (available); TA support (available); Access to AI coding tools/APIs (needs_confirmation); Commercial LLM API Credits (OpenAI/Anthropic) (needs_confirmation)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3), A:Quiz2 (W6→W6) | — | tool-use |  |
| assignment | 20.0 | A:Assign1 (W3→W4), A:Assign2 (W5→W6) | — | implement, tool-use, design |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | evaluate-critique |  |
| project | 25.0 | A:ProjM1 (W9→W11), A:ProjFinal (W12→W13) | — | design, implement, teamwork, oral-presentation |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | evaluate-critique, written-communication |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 23.0%, CO2 14.0%, CO3 13.0%, CO4 25.0%, CO5 25.0%

## 10. Resource material

Policy: **mixed** — AI-native software development is a rapidly evolving field with no single comprehensive textbook. The course combines emerging reference books on agentic design patterns with official protocol specifications and recent research papers on multi-agent workflows and LLM evaluation.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Gullí, Antonio. "Agentic Design Patterns." Springer, 2025*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M3.T1, M3.T2 |
| reading |  (None). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M1.T3, M1.T4 |
| reading | Yujia Li, Shunyu Yao, Guanzhi Wang, John Yang, Alexander Novikov, Bogdan Georgiev (None). *1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022.
2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022.
3) Wang, Guanzhi, et al. "Voyager: An Open-Ended Embodied Agent with Large Language Models." TMLR 2023.
4) Yang, John, et al. "Swe-agent: Agent-computer interfaces enable automated software engineering." NeurIPS 2024.
5) Novikov, Alexander, et al. "AlphaEvolve: A coding agent for scientific and algorithmic discovery." arXiv:2506.13131, 2025.
6) Georgiev, Bogdan, et al. "Mathematical exploration and discovery at scale." arXiv:2511.02864, 2025.
7) Other ongoing research reports.*. | R:hash:1-li-yujia-et-al-competition-level-code- | NO: candidate_id not in retrieved candidates | M1.T1, M3.T1 |
| reference | Yisen Xu (2025). *MUARF: Leveraging Multi-Agent Workflows for Automated Code Refactoring*. | 10.1109/icse-companion66252.2025.00071 | yes | M3.T2 |
| reference | Ashraf Elnashar, Max Moundas, Douglas Schmidt, Jesse Spencer-Smith (2024). *Evaluating the Performance of LLM-Generated Code for ChatGPT-4 and AutoGen Along with Top-Rated Human Solutions*. | 10.5220/0012820600003753 | yes | M4.T1, M4.T3 |
| reference |  (2005). *Specification-Driven Verification and Validation*. | 10.1201/9780203496299.ch14 | yes | M2.T1, M2.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 3 [3] |  |  | 3 [2] |
| CO2 | 3 [3] |  |  | 3 [unclaimed] |
| CO3 | 3 [2] |  |  | 3 [unclaimed] |
| CO4 | 3 [3] |  | 3 [unclaimed] | 3 [unclaimed] |
| CO5 | 3 [3] | 3 [2] | 3 [2] |  |

PO legend: PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring modern AI coding tools and MCP servers directly aligns with implementing and utilizing modern tools to build development environments. (activities: implement, tool-use)
- CO1→PO9: Involves the application of advanced protocol tools and techniques in a specialized computing workflow. (activities: tool-use)
- CO2→PO4: Constructing executable specifications is a core system design and implementation activity using modern methodologies. (activities: design, implement)
- CO3→PO4: Analyzing development loops evaluates the functioning of software development processes and systems. (activities: evaluate-critique)
- CO4→PO4: Evaluating reliability metrics and vulnerabilities directly supports the evaluation dimension of system development. (activities: evaluate-critique)
- CO5→PO4: Comprehensive end-to-end evaluation of software applications covers the full system lifecycle evaluation requirement. (activities: evaluate-critique, teamwork)
- CO5→PO5: Collaborative workflows mirror team-based operational dynamics required to accomplish project milestones. (activities: teamwork)
- CO5→PO7: Live scenario walkthroughs require effective oral presentation and communication of technical functionality. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1, A:Midsem@L1 |
| CO1.LO2 | L3 | M1.T2 | 1, 2 | A:Midsem@L3 |
| CO1.LO3 | L3 | M1.T3, M1.T4 | 2, 3 | A:Assign1@L3 |
| CO2.LO1 | L1 | M2.T1 | 3, 4 | A:Midsem@L1 |
| CO2.LO2 | L3 | M2.T2 | 4, 5 | A:Assign2@L3 |
| CO3.LO1 | L2 | M3.T1 | 5 | A:Quiz2@L2, A:Midsem@L2 |
| CO3.LO2 | L4 | M3.T2, M3.T3 | 6, 7 | A:Midsem@L4 |
| CO4.LO1 | L4 | M4.T1, M4.T2 | 7, 8 | A:Endsem@L4 |
| CO4.LO2 | L5 | M4.T3 | 9 | A:Endsem@L5 |
| CO5.LO1 | L5 | M5.T1 | 10 | A:ProjM1@L5 |
| CO5.LO2 | L5 | M5.T2, M5.T3 | 10, 11, 12 | A:ProjFinal@L5 |

## Appendix C — Modules and topics

**M1 AI-Native Developer Workflows & Setup** (primary CO1)
- M1.T1 Core Components of AI-Native Workflows — 2.0 h · LOs CO1.LO1
- M1.T2 Local Workspace Configuration for AI Tools — 2.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Model Context Protocol (MCP) Architecture — 2.0 h · LOs CO1.LO3 · requires M1.T2
- M1.T4 Context Engineering and MCP Server Integration — 2.0 h · LOs CO1.LO3 · requires M1.T3
**M2 Specification-Driven Development** (primary CO2)
- M2.T1 Requirements Engineering and Spec Parsing — 2.0 h · LOs CO2.LO1
- M2.T2 Executable Specifications and Spec-Driven Tools — 3.0 h · LOs CO2.LO2 · requires M2.T1, M1.T4
**M3 Agentic Loops and Software Factories** (primary CO3)
- M3.T1 Loop Engineering and Iterative Workflows — 2.0 h · LOs CO3.LO1 · requires M2.T2
- M3.T2 Multi-Agent Software Factories — 2.5 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Execution Log Analysis and Debugging — 2.5 h · LOs CO3.LO2 · requires M3.T2
**M4 Testing, Evaluation, and Reliability** (primary CO4)
- M4.T1 Automated Testing and Evaluation Metrics — 2.0 h · LOs CO4.LO1 · requires M3.T3
- M4.T2 Deployment Metrics and Baseline Performance — 2.0 h · LOs CO4.LO1 · requires M4.T1
- M4.T3 Reliability Evaluation of Agent-Generated API Clients — 3.0 h · LOs CO4.LO2 · requires M4.T2
**M5 Collaborative Agent Projects** (primary CO5)
- M5.T1 Project Planning and Collaborative Workflows — 2.0 h · LOs CO5.LO1 · requires M4.T3
- M5.T2 Hands-on Coding with Emerging Developer Tools — 2.5 h · LOs CO5.LO2 · requires M5.T1
- M5.T3 Live Scenario Walkthroughs and System Evaluation — 2.5 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 34.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 focuses on the research and algorithmic application of AI models to automate SE tasks, whereas this course focuses on the practical developer workflow of collaborating with AI coding agents. |
| CSE594A | 0.08 | complementary | CSE594A focuses on the theoretical and algorithmic foundations of agentic reasoning for scientific and mathematical problem solving, whereas this course focuses on the practical software engineering workflows and tool coordination. |
| CSE582 | 0.067 | complementary | CSE582 focuses on software product lines, maintenance, and traditional software re-engineering, whereas this course focuses on AI-native development workflows. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: The integration of automated testing and code analysis tools. Avoid: The heavy research focus on literature review and ML model training for defect prediction.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: The conceptual frameworks for agentic protocols and multi-agent collaboration. Avoid: The focus on theoretical reasoning for mathematical and scientific problem solving.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: The project-heavy evaluation structure and emphasis on modern collaborative developer tools (like GitHub). Avoid: The focus on open-source licensing and traditional component integration.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Gullí, Antonio. "Agentic Design Patterns." Springer, 2025' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:1-li-yujia-et-al-competition-level-code- | resource '1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022.
2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022.
3) Wang, Guanzhi, et al. " |
| assessment | VA-PROJ | warning | project | project released in week 9, late in a 13-week semester |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 26.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 3 → 0 · round 1 accepted (3→0)
- los: errors 7 → 0 · round 1 accepted (7→2); round 2 accepted (2→0)
- assessment: errors 1 → 0 · round 1 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: The constraint 'Create two Course Outcomes with exactly the same verb and behaviour text' is highly unusual and may violate pedagogical principles of distinct, measurable outcomes.
- intake: credits: Missing credits and LTP values make it impossible to verify compliance with IIIT-D credit-hour regulations (UGREG-2025§4).
- positioning: SC1: Special constraint SC1 requires creating two Course Outcomes with exactly the same verb and behaviour text, which may lead to redundant or non-distinguishable outcomes.
- constraints: K17: Creating two Course Outcomes with exactly the same verb and behaviour text violates standard outcome-based education (OBE) principles where each outcome must be distinct and uniquely measurable.
- cos: CO6: CO6 has identical verb and behaviour text to CO5 as mandated by special constraint SC1, which violates general distinctness guidelines but satisfies the specific user constraint.
- labs: Access to AI coding tools/APIs: The lab plan heavily relies on API access for LLMs and agent frameworks. If paid API credits or licenses are not provided by the institution, students may face rate limits or out-of-pocket costs.
- assessment: project: The project runs for 3 weeks (Weeks 10-13) instead of the recommended 4 weeks because the prerequisite planning topic (M5.T1) is scheduled in Week 10.
- resources: M1.T2: No academic papers or official books in the current corpus directly cover local workspace configuration for AI tools, which is highly practical and fast-moving. This will rely heavily on online documentation and instructor-provided guides.
- narrative: SC1: Special constraint SC1 requested two Course Outcomes with exactly the same verb and behaviour text, but CO4 and CO5 have different behaviour texts despite sharing the verb 'Evaluate'.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The course progresses logically from foundational setup to complex systems. It begins with workspace configuration and Model Context Protocol integration (M1), moves to specification-driven development (M2), and then introduces agentic loops and debugging (M3). This builds the necessary skills for testing and reliability evaluation (M4), culminating in collaborative multi-agent projects (M5). This sequence relies on CSE201 as a prerequisite to ensure students possess the fundamental programming and unit testing skills required for these advanced workflows.
- **assessment rationale:** The assessment mix directly aligns with the course's practical, workflow-oriented outcomes. Quizzes (10%) and midsem (20%) evaluate conceptual understanding of agentic architectures. Assignments (20%) assess hands-on configuration (CO1) and specification-driven development (CO2). The final project (25%) and endsem (25%) evaluate higher-level capabilities: analyzing agentic loops (CO3), evaluating reliability metrics (CO4), and demonstrating collaborative agent workflows in an end-to-end application (CO5), matching the practical emphasis of the L-T-P structure.
- **positioning rationale:** This course is distinct from existing IIIT-D offerings. While CSE701 focuses on research and algorithmic applications of AI to automate software engineering, this course emphasizes practical developer workflows and tool coordination. It differs from CSE594A, which covers theoretical and algorithmic foundations of agentic reasoning for scientific problem-solving, by focusing on software engineering practices. Finally, unlike CSE582's focus on traditional software product lines and maintenance, this course is uniquely centered on AI-native development workflows.