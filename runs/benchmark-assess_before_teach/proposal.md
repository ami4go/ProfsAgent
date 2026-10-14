# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-assess_before_teach` · generated deterministically from the design graph · validator status: **7 errors, 11 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level specified without a concrete course code. | professor |
| — | CONFLICT ['special_constraints', 'curriculum_context'] | — | Special constraint states the final exam must be scheduled in week 2 covering topics from week 14, which contradicts standard academic calendar sequencing and UGREG-2025§6.2. | professor |
| — | CONFLICT ['K14', 'REGULATION'] | — | Special constraint K14 requires the final exam to be scheduled in week 2 covering week 14, which conflicts with standard semester progression and the academic calendar where the semester has 13 weeks of teaching and the end-semester examination occurs at the end of the semester. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. Target students build upon strong programming and software development fundamentals to engage in automated testing and agent-assisted coding workflows. Upon completing the course, students are able to operate coding agents using orchestration frameworks, implement agent skills and tool integrations via the Model Context Protocol, construct executable specifications from requirements documents, analyse iterative development loops with log evidence, and evaluate AI-native software development workflows for multi-component applications. The course is taught through lectures, tutorials, and practical laboratory sessions complemented by hands-on projects.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Strong programming and software development fundamentals are required before students can engage in automated testing and agent-assisted coding workflows. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in software engineering (with an overlap of 0.185), it focuses broadly on data mining from repositories, defect prediction, and general AI applications in SE. The new course specifically targets modern AI-native software development involving coding agents, developer workflows, loop engineering, and agentic protocols (such as MCP).

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Operate coding agents using an agent orchestration framework, such that all public tests pass and no warnings are generated from the configured static analyser.** `[CORPUS, USER]`  
verb *operate* · behaviour *coding agents* · condition *using an agent orchestration framework* · degree *such that all public tests pass and no warnings are generated from the configured static analyser* · evidence: programming_assignment, lab_task · marks share (computed): 12.67%

- CO1.LO1 (L3) Configure an agent orchestration framework for a supplied local code repository, specifying environment variables and prompt templates.
- CO1.LO2 (L3 ★capstone) Operate coding agents using an agent orchestration framework, on a supplied programming task, such that all public tests pass and no warnings are generated from the configured static analyser.

**CO2 (L3, procedural) — Implement agent skills and tool integrations using the Model Context Protocol (MCP), meeting the stated interface specification for every public method.** `[CORPUS, USER]`  
verb *implement* · behaviour *agent skills and tool integrations* · condition *using the Model Context Protocol (MCP)* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment, code_review · marks share (computed): 21.5%

- CO2.LO1 (L3) Implement server-side MCP connection handlers and data schemas, producing output that matches the reference for 2 supplied inputs.
- CO2.LO2 (L3 ★capstone) Implement agent skills and tool integrations using the Model Context Protocol (MCP), on a supplied server module, meeting the stated interface specification for every public method.

**CO3 (L3, conceptual) — Construct executable specifications from natural language requirements documents, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *construct* · behaviour *executable specifications* · condition *from natural language requirements documents* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 16.67%

- CO3.LO1 (L3) Identify functional requirements and user stories from natural language requirements documents, for a supplied text of at most 5 pages.
- CO3.LO2 (L3 ★capstone) Construct executable specifications from natural language requirements documents, for a supplied use-case specification, covering every use case in the supplied requirements document.

**CO4 (L4, procedural) — Analyse iterative development loops and automated testing executions, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *analyse* · behaviour *iterative development loops and automated testing executions* · condition *using execution logs and profiling tools* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, report · marks share (computed): 21.67%

- CO4.LO1 (L4) Trace iterative development loops and automated testing executions, using execution logs and profiling tools within 60 minutes.
- CO4.LO2 (L4 ★capstone) Analyse iterative development loops and automated testing executions, using execution logs and profiling tools, identifying at least three distinct failure causes with supporting log evidence.

**CO5 (L5, metacognitive) — Evaluate AI-native software development workflows for a given multi-component application, justifying each design decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *AI-native software development workflows* · condition *for a given multi-component application* · degree *justifying each design decision against at least one stated requirement* · evidence: project_deliverable, presentation · marks share (computed): 27.5%

- CO5.LO1 (L5) Assess AI-native software development workflows for a given multi-component application, answering evaluator questions on 3 design choices in 15 minutes.
- CO5.LO2 (L5 ★capstone) Evaluate AI-native software development workflows for a given multi-component application, for a supplied project architecture, justifying each design decision against at least one stated requirement.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Setup and Configuration of Agent Orchestration Frameworks (M1.T1) | CO1.LO1 | CO1 | Walkthrough and collaborative configuration of environment variables and API keys for LLM access in pairs. |  |
| 2 | AI-Assisted Coding and Agent Operation (M1.T2) | CO1.LO2 | CO1 | Group discussion and live debugging of a coding agent's failing runs on a sample Python repository. |  |
| 3 | Multi-Agent Collaboration and Orchestration (M1.T3)<br>Requirements Engineering and User Story Extraction (M2.T1) | CO1.LO2, CO3.LO1 | CO1, CO3 | Interactive tracing of multi-agent communication protocols using sequence diagrams on a whiteboard. | Lab_Assignment_1 released |
| 4 | Requirements Engineering and User Story Extraction (M2.T1)<br>Constructing Executable Specifications (M2.T2) | CO3.LO1, CO3.LO2 | CO3 | In-class exercise extracting user stories and functional requirements from a 3-page sample requirements document. | Lab_Assignment_1 due |
| 5 | Constructing Executable Specifications (M2.T2)<br>Validation and Verification of Executable Specs (M2.T3) | CO3.LO2 | CO3 | Peer review of Gherkin specifications written by other groups, checking for completeness and ambiguity. |  |
| 6 | Validation and Verification of Executable Specs (M2.T3)<br>Model Context Protocol and Context Engineering (M3.T1) | CO2.LO1, CO3.LO2 | CO2, CO3 | Collaborative design of MCP custom schemas for a mock weather and calendar service on paper. | Lab_Assignment_2 released |
| 7 | Model Context Protocol and Context Engineering (M3.T1)<br>Agent Skills and Tool Integration (M3.T2) | CO2.LO1, CO2.LO2 | CO2 | Mid-sem review session. Worked walkthrough of sample exam questions on requirements and MCP protocol design. | Midsem_Exam (midsem); Lab_Assignment_2 due |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Agent Skills and Tool Integration (M3.T2)<br>Secure Tool Execution and Sandboxing (M3.T3) | CO2.LO2 | CO2 | Interactive threat-modeling of tool execution, identifying potential security exploits in unsandboxed environments. | Project_Milestone_1 released |
| 9 | Loop Engineering and Iterative Development Tracing (M4.T1) | CO4.LO1 | CO4 | Worked trace-diagnosis of 3 failing agent runs using execution logs, identifying where the loop diverged. |  |
| 10 | Automated Testing and Reliability Analysis (M4.T2) | CO4.LO2 | CO4 | Group analysis of reliability metrics and plotting failure distributions from a provided dataset of agent executions. | Project_Milestone_1 due |
| 11 | Debugging and Failure Analysis of Agentic Workflows (M4.T3)<br>Software Factories and Workflow Assessment (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Mock presentation session where students defend their workflow design choices against peer evaluator questions. | Lab_Assignment_3 released |
| 12 | Software Factories and Workflow Assessment (M5.T1)<br>Multi-Component Application Architectures and Deployment (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Interactive architectural mapping of a multi-component AI application, identifying potential bottlenecks. | Lab_Assignment_3 due |
| 13 | Workflow Evaluation and Design Justification (M5.T3) | CO5.LO2 | CO5 | Peer evaluation and structured feedback on draft design justification documents using a provided rubric. | Endsem_Exam (endsem); Project_Milestone_2 released |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Agent Orchestration Setup** — Configure a local agent orchestration framework (such as LangGraph) on student development machines. Set up environment variables, configure API keys, and verify connectivity by executing a basic single-agent prompt template. | CO1.LO1 | Python, LangGraph, OpenAI API |
| 2 | **AI-Assisted Bug Fixing** — Run a pre-configured coding agent on a provided Python repository to resolve simple bugs. Students must configure static analysis tools to ensure that the agent's output produces no warnings and passes all public tests. | CO1.LO2 | Python, Aider, Ruff |
| 3 | **Multi-Agent Collaboration** — Implement a multi-agent system where a coder agent and a tester agent collaborate. The coder agent generates code to solve a programming task, while the tester agent executes tests and provides feedback iteratively. | CO1.LO2 | Python, LangGraph |
| 4 | **Gherkin Feature Construction** — Translate natural language user stories and requirements documents into Gherkin feature files for a specified use-case, ensuring complete coverage of all functional requirements. | CO3.LO2 | Behave, Gherkin |
| 5 | **Executable Spec Implementation** — Implement step definitions in Python for the Gherkin feature files created in Week 4. Execute the specifications to validate system behavior and verify that all tests pass. | CO3.LO2 | Python, Behave |
| 6 | **MCP Server Setup** — Implement a basic server-side Model Context Protocol (MCP) connection handler. Define custom data schemas to expose local database schemas to an external agent. | CO2.LO1 | Python, MCP SDK |
| 7 | **Mid-Semester Catch-up and Review** — Open lab session for catching up on previous labs, debugging MCP handlers, and preparing for mid-semester evaluations. No new content is introduced. | CO2.LO1 | Python, MCP SDK |
| 8 | **Secure Tool Integration** — Integrate custom tools into an MCP server and implement secure execution of these tools using a Docker-based sandbox environment to prevent unauthorized system access. | CO2.LO2 | Python, MCP SDK, Docker |
| 9 | **Agent Loop Tracing** — Trace the execution of an iterative coding agent loop using LangSmith. Analyze execution logs to map the agent's decision steps and identify state transitions. | CO4.LO1 | LangSmith, Python |
| 10 | **Reliability and Failure Analysis** — Analyze execution logs of 100 automated agent runs to identify, categorize, and document at least three distinct failure modes, providing supporting log evidence. | CO4.LO2 | Python, Pandas, LangSmith |
| 11 | **Workflow Debugging** — Debug a failing multi-agent workflow by modifying prompt templates and tool schemas based on failure analysis, ensuring the workflow successfully completes the task. | CO4.LO2 | Python, LangGraph |
| 12 | **Multi-Component Deployment** — Deploy a multi-component AI-native application consisting of a frontend, an orchestrator, and multiple MCP tools using Docker Compose. | CO5.LO2 | Docker Compose, Python |
| 13 | **Workflow Evaluation & Justification** — Conduct a structured evaluation of the deployed workflow, writing a design justification report that maps each design decision against stated system requirements. | CO5.LO2 | Markdown |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); OpenAI/Anthropic API Keys (needs_confirmation); Docker Desktop (needs_confirmation); LangSmith accounts (needs_confirmation)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| midsem | 20.0 | Midsem_Exam (W7→W7) | — | design, implement |  |
| endsem | 25.0 | Endsem_Exam (W13→W13) | — | analyse-data, evaluate-critique |  |
| project | 35.0 | Project_Milestone_1 (W8→W10), Project_Milestone_2 (W13→W14) | — | implement, evaluate-critique, written-communication |  |
| lab | 20.0 | Lab_Assignment_1 (W3→W4), Lab_Assignment_2 (W6→W7), Lab_Assignment_3 (W11→W12) | — | implement, tool-use |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 12.67%, CO2 21.5%, CO3 16.67%, CO4 21.67%, CO5 27.5%

## 10. Resource material

Policy: **mixed** — Since AI-native software development is a rapidly evolving field, there is no single standard textbook. We combine emerging reference books on agentic design patterns with official protocol documentations and recent research papers.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Gullí, Antonio. "Agentic Design Patterns." Springer, 2025*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T2, M1.T3 |
| reading |  (None). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M3.T1, M3.T2 |
| reading | Yujia Li, Shunyu Yao, Guanzhi Wang, John Yang, Alexander Novikov, Bogdan Georgiev (2025). *1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022. 2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022. 3) Wang, Guanzhi, et al. "Voyager: An Open-Ended Embodied Agent with Large Language Models." TMLR 2023. 4) Yang, John, et al. "Swe-agent: Agent-computer interfaces enable automated software engineering." NeurIPS 2024. 5) Novikov, Alexander, et al. "AlphaEvolve: A coding agent for scientific and algorithmic discovery." arXiv:2506.13131, 2025. 6) Georgiev, Bogdan, et al. "Mathematical exploration and discovery at scale." arXiv:2511.02864, 2025. 7) Other ongoing research reports.*. | R:hash:1-li-yujia-et-al-competition-level-code- | NO: candidate_id not in retrieved candidates | M1.T2, M4.T1 |
| reference | Jaehyung Jeong, Jayeon Pyo, Jiho Lee, JaeSeung Song (2025). *Preserving oneM2M Security Semantics in LLM-IoT Integration with Model Context Protocol*. | 10.1109/aiot66900.2025.00032 | yes | M3.T3 |
| reference | Judice Antony, A. Ashwini, S. Balasubramaniam (2025). *5 Future Frontiers of Software Testing Beyond Debugging and Accuracy Automation Driven by Generative AI*. | 10.1515/9783111677798-005 | yes | M4.T2 |
| reference | Banu Priya Prathaban, R. Subash, A. Ashwini (2025). *4 Generative AI for Debugging and Error Detection*. | 10.1515/9783111677798-004 | yes | M4.T3 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 |  | 3 [3] |  | 2 [2] |
| CO2 |  | 3 [3] | 3 [unclaimed] | 3 [unclaimed] |
| CO3 |  | 3 [3] |  | 2 [unclaimed] |
| CO4 | 3 [2] | 3 [2] |  | 3 [unclaimed] |
| CO5 | 2 [unclaimed] | 3 [3] | 3 [unclaimed] | 3 [2] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Operating coding agents via agent orchestration frameworks directly utilizes modern tools and methodologies to implement computer-based applications. (activities: tool-use, implement)
- CO1→PO9: Utilizing agent orchestration frameworks involves advanced computing tools. (activities: tool-use)
- CO2→PO4: Implementing tool integrations using MCP aligns directly with implementing computer-based systems using modern methodologies. (activities: implement, tool-use)
- CO3→PO4: Constructing executable specifications is a core system design and implementation activity. (activities: design, implement)
- CO4→PO3: Analysing development loops and failures helps adapt techniques for solving new problems in software execution. (activities: analyse-data)
- CO4→PO4: Analysing automated testing executions contributes to evaluating computer-based systems. (activities: evaluate-critique)
- CO5→PO4: Evaluating AI-native software development workflows directly aligns with evaluating multi-component applications. (activities: evaluate-critique)
- CO5→PO9: AI-native software development workflows represent advanced techniques and tools in computing. (activities: evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1 | 1 | Midsem_Exam@L3, Lab_Assignment_1@L3 |
| CO1.LO2 | L3 | M1.T2, M1.T3 | 2, 3 | Midsem_Exam@L3, Lab_Assignment_1@L3 |
| CO2.LO1 | L3 | M3.T1 | 6, 7 | Midsem_Exam@L3 |
| CO2.LO2 | L3 | M3.T2, M3.T3 | 7, 8 | Project_Milestone_1@L3 |
| CO3.LO1 | L3 | M2.T1 | 3, 4 | Midsem_Exam@L3 |
| CO3.LO2 | L3 | M2.T2, M2.T3 | 4, 5, 6 | Midsem_Exam@L3, Lab_Assignment_2@L3 |
| CO4.LO1 | L4 | M4.T1 | 9 | Endsem_Exam@L4 |
| CO4.LO2 | L4 | M4.T2, M4.T3 | 10, 11 | Endsem_Exam@L4, Lab_Assignment_3@L4 |
| CO5.LO1 | L5 | M5.T1 | 11, 12 | Endsem_Exam@L5 |
| CO5.LO2 | L5 | M5.T2, M5.T3 | 12, 13 | Project_Milestone_2@L5 |

## Appendix C — Modules and topics

**M1 Agent Orchestration & Coding Agents** (primary CO1)
- M1.T1 Setup and Configuration of Agent Orchestration Frameworks — 3.0 h · LOs CO1.LO1
- M1.T2 AI-Assisted Coding and Agent Operation — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Multi-Agent Collaboration and Orchestration — 2.0 h · LOs CO1.LO2 · requires M1.T2
**M2 Requirements & Executable Specifications** (primary CO3)
- M2.T1 Requirements Engineering and User Story Extraction — 3.0 h · LOs CO3.LO1
- M2.T2 Constructing Executable Specifications — 3.0 h · LOs CO3.LO2 · requires M2.T1
- M2.T3 Validation and Verification of Executable Specs — 2.0 h · LOs CO3.LO2 · requires M2.T2
**M3 Model Context Protocol (MCP) & Tool Integration** (primary CO2)
- M3.T1 Model Context Protocol and Context Engineering — 3.0 h · LOs CO2.LO1 · requires M1.T1
- M3.T2 Agent Skills and Tool Integration — 3.0 h · LOs CO2.LO2 · requires M3.T1
- M3.T3 Secure Tool Execution and Sandboxing — 2.0 h · LOs CO2.LO2 · requires M3.T2
**M4 Iterative Development & Automated Testing** (primary CO4)
- M4.T1 Loop Engineering and Iterative Development Tracing — 3.0 h · LOs CO4.LO1 · requires M1.T2
- M4.T2 Automated Testing and Reliability Analysis — 3.0 h · LOs CO4.LO2 · requires M4.T1
- M4.T3 Debugging and Failure Analysis of Agentic Workflows — 2.0 h · LOs CO4.LO2 · requires M4.T2
**M5 Workflow Evaluation & Deployment** (primary CO5)
- M5.T1 Software Factories and Workflow Assessment — 2.0 h · LOs CO5.LO1 · requires M3.T2, M2.T2, M4.T2
- M5.T2 Multi-Component Application Architectures and Deployment — 2.0 h · LOs CO5.LO2 · requires M5.T1
- M5.T3 Workflow Evaluation and Design Justification — 3.0 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 39.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 looks at data and mining software repositories or general AI assistance models retrospectively, whereas the new course focuses on hands-on, agent-native development workflows, interactive coding agents, and real-time execution loops. |
| CSE594A | 0.08 | complementary | CSE594A focuses on the broader theoretical and algorithmic foundations of agentic reasoning for mathematical and scientific problem solving, while the new course specifically addresses software engineering workflows and developer tool integration. |
| CSE582 | 0.067 | superficial | CSE582 deals with traditional software product lines, maintenance, and re-engineering, whereas the new course examines modern AI-driven code generation and agent factories. |
| CSE581 | 0.034 | superficial | CSE581 covers classical systems analysis, human factors, and requirements engineering methodologies, whereas the new course centers on spec-driven development with AI agents. |
| AI501 | 0.034 | superficial | AI501 is a foundational core course in machine learning algorithms and theory, whereas the new course applies existing coding tools and agents to software development. |
| CSE201 | 0.017 | complementary | CSE201 teaches foundational advanced programming concepts in Java and standard unit testing, while the new course focuses on automated testing and validation using AI-native coding agents. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Incorporate literature review methods and project health monitoring metrics. Avoid: Avoid excessive focus on historical software repository data mining.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Adopt protocols like MCP and multi-agent coordination frameworks. Avoid: Avoid deep mathematical and algorithmic proofs for reasoning.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Use practical project-based execution and open tooling integration styles. Avoid: Avoid traditional open-source licensing and manual issue tracking structures.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| los | VLO-COPY | error | CO1.LO2, CO1 | CO1.LO2 restates its parent CO1 (token overlap 0.88); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO2.LO2, CO2 | CO2.LO2 restates its parent CO2 (token overlap 0.87); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO3.LO2, CO3 | CO3.LO2 restates its parent CO3 (token overlap 0.88); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO5.LO2, CO5 | CO5.LO2 restates its parent CO5 (token overlap 0.86); an LO must be a narrower, single-task step |
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Gullí, Antonio. "Agentic Design Patterns." Springer, 2025' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:1-li-yujia-et-al-competition-level-code- | resource '1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022. 2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022. 3) Wang, Guanzhi, et al. " |
| assessment | VA-PROJ | warning | project | project released in week 8, late in a 13-week semester |
| cos | V11 | warning | CO4 | CO CO4 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 25.0 h vs budget 39 h (±15%) |
| los | VB | warning | CO3.LO1 | LO CO3.LO1: claimed Bloom L3 but verb 'identify' is lexicon L1 |
| los | VB | warning | CO4.LO1 | LO CO4.LO1: claimed Bloom L4 but verb 'trace' is lexicon L2 |

**Repair history**

- cos: errors 2 → 0 · round 1 accepted (2→0)
- los: errors 5 → 4 · round 1 accepted (5→4); round 2 rejected (4→4); round 3 rejected (4→3)
- structure: errors 1 → 0 · round 1 rejected (1→3); round 2 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: The constraint requiring the final exam in week 2 covering week 14 topics is logically impossible under standard semester sequencing.
- positioning: SC1: Special constraint SC1 mandates scheduling the final exam in week 2 covering topics from week 14, which contradicts standard academic scheduling norms.
- constraints: Special Constraint SC1: The final exam is requested for week 2 covering week 14, but the semester only has 13 teaching weeks. This is logically inconsistent and conflicts with standard academic schedules.
- cos: SC1: Special constraint SC1 mandates scheduling the final exam in week 2 covering topics from week 14, which appears to be a typographic or logical contradiction in the intake constraints.
- copo: activity_po_map: Ensure that the assessment plan explicitly incorporates the indicated activities (tool-use, implement, analyse-data, evaluate-critique) and maps them appropriately to validate the provisional strengths.
- los: hours_total: Sum of allocated LO lecture hours (26h) and tutorial hours (10h) are slightly below the institutional target (39h lecture, 13h tutorial), but accurately reflect the decomposition granularity without padding.
- structure: K14 / SC1: The constraint specifies that the final exam must be scheduled in week 2, covering topics from week 14. This is chronologically impossible for a standard 13-week semester structure.
- labs: API Credit Budgeting: While 'access to AI coding tools/APIs' is listed in lab_info, the specific budget, credit allocation, or API keys for students are not confirmed, which could block hands-on execution.
- resources: SC1: The special constraint SC1 states 'The final exam must be scheduled in week 2, covering topics from week 14.' This is chronologically impossible and likely a typographical error in the CCO.
- resources: M2: No suitable resources covering Requirements Engineering and Executable Specifications were found in the corpus or external search results.
- resources: M5: No suitable resources covering Software Factories, Workflow Assessment, and Multi-Component Deployment were found in the corpus or external search results.
- narrative: SC1: Constraint SC1 specifies that the final exam must be scheduled in week 2 covering topics from week 14, which conflicts with standard academic calendars and the 13-week course duration.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress logically from foundational agent orchestration and specification extraction to tool integration via the Model Context Protocol, iterative development tracing, and final workflow evaluation. This sequencing relies on prerequisite competencies in programming and software development established in CSE201.
- **assessment rationale:** The assessment mix comprises a mid-semester examination, an end-semester examination, laboratory assignments, and a major project. This combination aligns with the practical, workflow-oriented pedagogical emphasis, directly evaluating both conceptual understanding and hands-on capability in operating coding agents and building tool integrations.
- **positioning rationale:** Unlike CSE701 which retrospectively examines data mining and general AI assistance, or CSE594A which focuses on algorithmic reasoning for mathematical problem-solving, this course specifically centres on software-engineering workflows, interactive coding agents, and real-time execution loops.