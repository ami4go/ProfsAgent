# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-inv_assess_weights` · generated deterministically from the design graph · validator status: **1 errors, 12 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | The level is specified as 'Advanced undergraduate' but the exact course code is not specified, leaving the precise level (e.g., 300-level vs 400-level) ambiguous. | professor |
| — | CONFLICT ['K15'] | — | Assessment weights summing to 130% violates standard institutional grading norm where total assessment weight must sum to 100%. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with increasingly capable coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. The curriculum addresses coding agents and Model Context Protocol servers, specification and requirement parsing, workflow analysis and loop engineering, automated testing and deployment pipelines, as well as multi-module integration and software factories. Grounded in strong programming and software development fundamentals from prerequisite coursework, the course matters for senior undergraduate students preparing for modern engineering environments. Students learn to configure coding agents, construct executable specifications from natural language requirements, analyse iterative developer workflows, evaluate automated testing and deployment pipelines, and execute multi-module AI-native workflows. Instruction is delivered through lectures, tutorials, and laboratory sessions emphasizing hands-on development and experimentation.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm, Collection framework | Students require strong programming, modularity, and automated testing fundamentals to effectively design and evaluate agent-assisted software development processes. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in software engineering from a data and research perspective (weighted Jaccard 0.118), the new course specifically targets modern AI-native software development, developer-agent collaboration, workflows, and spec-driven agentic engineering.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure coding agents and Model Context Protocol servers, for a given development task, such that all public integration tests pass and no warnings are reported from the configured static analyser.** `[CORPUS, USER]`  
verb *configure* · behaviour *coding agents and Model Context Protocol servers* · condition *for a given development task* · degree *such that all public integration tests pass and no warnings are reported from the configured static analyser* · evidence: programming_assignment, lab_task · marks share (computed): 23.33%

- CO1.LO1 (L1) Identify coding agent capabilities, tool use APIs, and Model Context Protocol server mechanisms for a supplied development environment configuration guide.
- CO1.LO2 (L3 ★capstone) Configure MCP server connection parameters and tool use permissions for a supplied agent workspace, such that all public integration tests pass and no warnings are reported from the configured static analyser.

**CO2 (L3, procedural) — Construct executable specifications from natural language requirements, using spec-driven development tools, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *construct* · behaviour *executable specifications from natural language requirements* · condition *using spec-driven development tools* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 25.33%

- CO2.LO1 (L2) Identify user scenarios, input-output parameters, and system boundaries from natural language feature descriptions in a supplied requirement snippet.
- CO2.LO2 (L3 ★capstone) Construct protocol definition files and schema bindings from natural language requirements using spec-driven development tools, covering every use case in the supplied requirements document.

**CO3 (L4, conceptual) — Analyse iterative developer workflows and loop engineering setups, for a supplied agent-assisted repository, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *analyse* · behaviour *iterative developer workflows and loop engineering setups* · condition *for a supplied agent-assisted repository* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, code_review · marks share (computed): 18.83%

- CO3.LO1 (L2) Trace execution traces and log files of agent-assisted repositories, identifying execution steps and loop iterations.
- CO3.LO2 (L4 ★capstone) Analyse execution log checkpoints and retry loop metrics for a supplied agent-assisted repository, identifying at least three distinct failure causes with supporting log evidence.

**CO4 (L5, metacognitive) — Evaluate automated testing, evaluation, and deployment pipelines, for a given AI-native software project, justifying each design decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *automated testing, evaluation, and deployment pipelines* · condition *for a given AI-native software project* · degree *justifying each design decision against at least one stated requirement* · evidence: design_document, presentation · marks share (computed): 15.83%

- CO4.LO1 (L2) Compare automated testing and evaluation metrics for AI-generated code snippets against baseline test requirements.
- CO4.LO2 (L5 ★capstone) Evaluate continuous integration test execution outputs and deployment check scripts for a given AI-native software project, justifying each design decision against at least one stated requirement.

**CO5 (L5, procedural) — Evaluate an AI-native software development workflow and software factory, for a complex multi-module problem, such that the delivered system satisfies every acceptance criterion agreed at the first milestone and is demonstrated live with two scenario walkthroughs chosen by the evaluator.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *an AI-native software development workflow and software factory* · condition *for a complex multi-module problem* · degree *such that the delivered system satisfies every acceptance criterion agreed at the first milestone and is demonstrated live with two scenario walkthroughs chosen by the evaluator* · evidence: project_deliverable, presentation · marks share (computed): 20.0%

- CO5.LO1 (L5) Evaluate a multi-module AI-native development workflow integration plan incorporating coding agents, specification tools, and testing pipelines, justifying each design choice against stated requirements.
- CO5.LO2 (L5 ★capstone) Evaluate multi-agent pipeline telemetry and final deliverable artifacts for a complex multi-module problem, such that the delivered system satisfies every acceptance criterion agreed at the first milestone and is demonstrated live with two scenario walkthroughs chosen by the evaluator.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Coding agent capabilities and architecture (M1.T1)<br>Model Context Protocol server mechanisms and tool use APIs (M1.T2) | CO1.LO1 | CO1 | Worked trace-diagnosis of coding agent architecture configurations, in pairs. |  |
| 2 | Model Context Protocol server mechanisms and tool use APIs (M1.T2)<br>Agent workspace configuration and connection parameters (M1.T3) | CO1.LO1, CO1.LO2 | CO1 | Trace-diagnosis of tool use API call logs and error responses, in groups of three. |  |
| 3 | Agent workspace configuration and connection parameters (M1.T3)<br>Natural language feature descriptions and requirement parsing (M2.T1) | CO1.LO2, CO2.LO1 | CO1, CO2 | Problem-solving session mapping workspace configuration errors to connection parameters. | A:Quiz1 (quiz); A:Assignment1 released |
| 4 | Natural language feature descriptions and requirement parsing (M2.T1)<br>Spec-driven development tools and protocol definition files (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Parsing natural language requirement snippets to identify input-output parameters and boundaries, in pairs. | A:Assignment1 due |
| 5 | Spec-driven development tools and protocol definition files (M2.T2)<br>Workflow log analysis and execution trace identification (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Worked exercise identifying user scenarios and system boundaries from complex requirement documents. | A:Quiz2 (quiz); A:Assignment2 released |
| 6 | Workflow log analysis and execution trace identification (M3.T1)<br>Loop engineering and retry loop metric analysis (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Tracing execution steps and loop iterations in provided agent log files. | A:Assignment2 due |
| 7 | Loop engineering and retry loop metric analysis (M3.T2)<br>Code review and analysis in agent-assisted repositories (M3.T3) | CO3.LO2 | CO3 | Problem-solving on workflow log analysis and execution trace identification. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Code review and analysis in agent-assisted repositories (M3.T3)<br>Automated testing and evaluation metrics for generated code (M4.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Review of code analysis techniques in agent-assisted repositories, in pairs. | A:Quiz3 (quiz); A:ProjectMilestone1 released |
| 9 | Continuous integration test execution and reliability checks (M4.T2) | CO4.LO2 | CO4 | Comparative evaluation of automated testing metrics against baseline requirements. | A:Quiz4 (quiz) |
| 10 | Multi-module AI-native workflow integration planning (M5.T1) | CO5.LO1 | CO5 | Group discussion and critique of multi-module AI-native workflow integration plans. | A:ProjectMilestone1 due; A:ProjectDeliverable released |
| 11 | Emerging developer tools and multi-agent software factory execution (M5.T2)<br>Capstone project demonstration and validation scenarios (M5.T3) | CO5.LO2 | CO5 | Evaluation and justification exercises for multi-module integration workflow designs. |  |
| 12 | Capstone project demonstration and validation scenarios (M5.T3) | CO5.LO2 | CO5 | Capstone project rubric review and peer feedback on validation scenarios. | A:ProjectDeliverable due |
| 13 |  |  |  |  | A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Introduction to Development Environments and Tooling** — Verify and configure local software development environments and access channels for AI coding tools. | CO1.LO1 | Student development machines, software development environments |
| 2 | **Agent Workspace Configuration** — Configure agent workspace connection parameters and establish initial tool use permissions. | CO1.LO2 | Student development machines, access to AI coding tools/APIs |
| 3 | **Advanced Workspace Settings and Integration** — Test agent workspace parameters against integration checks and resolve configuration warnings. | CO1.LO2 | Student development machines, access to AI coding tools/APIs |
| 4 | **Spec-Driven Protocol Definitions** — Construct protocol definition files and schema bindings using spec-driven development tools. | CO2.LO2 | Student development machines, software development environments |
| 5 | **Refining Protocol Schemas** — Extend and refine schema bindings and protocol files to cover edge-case requirements. | CO2.LO2 | Student development machines, software development environments |
| 6 | **Retry Loop Metric Analysis** — Examine execution log checkpoints and compute retry loop metrics to identify failure causes. | CO3.LO2 | Student development machines, software development environments |
| 7 | **Log Checkpoint Diagnosis** — Analyze agent execution logs to isolate distinct failure modes with supporting log evidence. | CO3.LO2 | Student development machines, software development environments |
| 8 | **Mid-Sem Catch-up and Open Lab** — Open lab session for catch-up, review of mid-term feedback, and repository exploration. | CO3.LO2 | Student development machines |
| 9 | **CI Test Execution and Deployment Checks** — Evaluate continuous integration test execution outputs and write deployment check scripts. | CO4.LO2 | Student development machines, software development environments |
| 10 | **Workflow Integration Setup** — Configure multi-module repository structures and testing pipelines for project workflows. | CO4.LO2 | Student development machines, software development environments |
| 11 | **Multi-Agent Software Factory Execution** — Execute multi-agent workflows and evaluate pipeline telemetry against acceptance criteria. | CO5.LO2 | Student development machines, access to AI coding tools/APIs |
| 12 | **Capstone Demonstration and Validation** — Conduct live scenario walkthroughs and validate final multi-module deliverable artifacts. | CO5.LO2 | Student development machines, access to AI coding tools/APIs |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3), A:Quiz2 (W5→W5), A:Quiz3 (W8→W8), A:Quiz4 (W9→W9) | best 3 of 4 | tool-use, analyse-data |  |
| assignment | 20.0 | A:Assignment1 (W3→W4), A:Assignment2 (W5→W6) | — | implement, design |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, design |  |
| project | 25.0 | A:ProjectMilestone1 (W8→W10), A:ProjectDeliverable (W10→W12) | — | design, implement, evaluate-critique, teamwork, oral-presentation, written-communication |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique, design |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 23.33%, CO2 25.33%, CO3 18.83%, CO4 15.83%, CO5 20.0%

## 10. Resource material

Policy: **mixed** — Because AI-native software development and coding agents are rapidly evolving domains, standard software engineering textbooks are supplemented with recent peer-reviewed chapters and articles focusing on the Model Context Protocol, agentic workflows, and automated coding agents.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Ian Sommerville (2005). *Software Engineering*. | 9780133943030 | yes | M2.T1, M4.T1 |
| reference | Sarat Piridi (2026). *Connecting to the Model Context Protocol*. | 10.1007/979-8-8688-2888-1_8 | yes | M1.T2 |
| reading | Igor Zuykov (2026). *Architectural Principles for Multi-Agent Systems Based on The Model Context Protocol*. | 10.37547/tajet/volume08issue03-12 | yes | M1.T1, M5.T2 |
| reference | Dhivya Nagasubramanian (2026). *Agentic Workflows and AI Agents*. | 10.4324/9781003729068-16 | yes | M3.T2 |
| reading | Yeswanth Kumar Polishetty (2026). *Autonomous Coding Agents for Software Development Testing and Debugging*. | 10.2139/ssrn.7515638 | yes | M1.T1, M4.T1 |
| reading | Jahnavi Bellapukonda (2026). *A Comparative Evaluation of LLM-based Coding Agents for Automated Software development Tasks*. | 10.2139/ssrn.6755658 | yes | M4.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 | PO10 |
|---|---|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 3 [3] |  |  | 2 [2] |  |
| CO2 | 3 [unclaimed] | 3 [3] |  |  | 2 [unclaimed] |  |
| CO3 | 3 [2] | 3 [unclaimed] |  |  | 2 [unclaimed] | – [2] |
| CO4 | 3 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [1] | 3 [unclaimed] |  |
| CO5 |  | 3 [3] | 3 [unclaimed] | 3 [2] | 3 [unclaimed] |  |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools; PO10 = Research tasks

- CO1→PO4: Configuring agents and servers directly aligns with implementing and utilizing modern development tools to build application components. (activities: implement, tool-use)
- CO1→PO9: Utilizes advanced agentic tools and Model Context Protocol servers in modern software engineering. (activities: tool-use)
- CO2→PO4: Constructing executable specifications constitutes designing the foundational behavioral structure of an application. (activities: design, implement)
- CO3→PO3: Analyzing developer workflows requires applying diagnostic techniques to identify failure causes in new setups. (activities: analyse-data)
- CO3→PO10: Investigating logs to discover distinct failure causes mirrors small-scale empirical research tasks. (activities: research-investigation)
- CO4→PO4: Evaluating deployment pipelines and design decisions directly serves the evaluation dimension of system development. (activities: evaluate-critique, design)
- CO4→PO7: Written justifications of design decisions contribute to technical communication skills. (activities: written-communication)
- CO5→PO4: Delivering and demonstrating a complex multi-module system satisfies end-to-end system implementation and evaluation. (activities: implement, evaluate-critique)
- CO5→PO7: Live scenario walkthroughs and demonstrations exercise oral presentation and technical communication abilities. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1, M1.T2 | 1, 2 | A:Quiz1@L1, A:Midsem@L1 |
| CO1.LO2 | L3 | M1.T3 | 2, 3 | A:Assignment1@L3, A:Endsem@L3 |
| CO2.LO1 | L2 | M2.T1 | 3, 4 | A:Quiz2@L2, A:Midsem@L2 |
| CO2.LO2 | L3 | M2.T2 | 4, 5 | A:Assignment2@L3, A:Endsem@L3 |
| CO3.LO1 | L2 | M3.T1 | 5, 6 | A:Quiz3@L2, A:Midsem@L2 |
| CO3.LO2 | L4 | M3.T2, M3.T3 | 6, 7, 8 | A:Endsem@L4 |
| CO4.LO1 | L2 | M4.T1 | 8 | A:Quiz4@L2 |
| CO4.LO2 | L5 | M4.T2 | 9 | A:ProjectMilestone1@L5, A:Endsem@L5 |
| CO5.LO1 | L5 | M5.T1 | 10 | A:ProjectMilestone1@L5 |
| CO5.LO2 | L5 | M5.T2, M5.T3 | 11, 12 | A:ProjectDeliverable@L5 |

## Appendix C — Modules and topics

**M1 Coding Agents and Model Context Protocol** (primary CO1)
- M1.T1 Coding agent capabilities and architecture — 2.5 h · LOs CO1.LO1
- M1.T2 Model Context Protocol server mechanisms and tool use APIs — 2.5 h · LOs CO1.LO1 · requires M1.T1
- M1.T3 Agent workspace configuration and connection parameters — 3.0 h · LOs CO1.LO2 · requires M1.T2
**M2 Specification and Requirement Parsing** (primary CO2)
- M2.T1 Natural language feature descriptions and requirement parsing — 2.5 h · LOs CO2.LO1 · requires M1.T1
- M2.T2 Spec-driven development tools and protocol definition files — 3.0 h · LOs CO2.LO2 · requires M2.T1
**M3 Workflow Analysis and Loop Engineering** (primary CO3)
- M3.T1 Workflow log analysis and execution trace identification — 2.5 h · LOs CO3.LO1 · requires M1.T3
- M3.T2 Loop engineering and retry loop metric analysis — 3.0 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Code review and analysis in agent-assisted repositories — 2.5 h · LOs CO3.LO2 · requires M3.T2
**M4 Automated Testing and Deployment Pipelines** (primary CO4)
- M4.T1 Automated testing and evaluation metrics for generated code — 2.5 h · LOs CO4.LO1 · requires M2.T2
- M4.T2 Continuous integration test execution and reliability checks — 3.0 h · LOs CO4.LO2 · requires M4.T1
**M5 Multi-Module Integration and Software Factories** (primary CO5)
- M5.T1 Multi-module AI-native workflow integration planning — 3.0 h · LOs CO5.LO1 · requires M1.T3, M2.T2, M3.T2, M4.T2
- M5.T2 Emerging developer tools and multi-agent software factory execution — 2.0 h · LOs CO5.LO2 · requires M5.T1
- M5.T3 Capstone project demonstration and validation scenarios — 2.0 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 34.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.118 | complementary | CSE701 focuses on data mining and AI models for SE tasks and research, whereas this course emphasizes practical, workflow-oriented design of agent-assisted software development processes. |
| CSE581 | 0.062 | superficial | CSE581 covers traditional systems analysis and requirements engineering, whereas this course focuses on spec-driven development and executable specifications for AI agents. |
| CSE582 | 0.118 | complementary | CSE582 addresses legacy software maintenance, product lines, and re-engineering, whereas this course deals with AI-native development loops and software factories. |
| CSE594A | 0.077 | complementary | CSE594A is a 2-credit course focused broadly on agentic reasoning for algorithmic and mathematical problem solving, whereas this course is a 4-credit course specialized entirely in software engineering workflows and AI-native coding processes. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Practical project-based evaluation structure and team-based application building. Avoid: Focus on traditional open-source licensing and manual open-source toolchains rather than AI-native workflows.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Foundational concepts of agent protocols and tool use. Avoid: Algorithmic and mathematical problem-solving focus; this course must strictly maintain a software engineering focus.
- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Rigorous treatment of how AI impacts software engineering life-cycle tasks. Avoid: Heavy emphasis on empirical data mining and research literature review instead of practical workflow engineering.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| assessment | V23 | error | CO3, BTECH-CSE/PO10 | CO3→BTECH-CSE/PO10 claimed (provisional 2) but no assessed activity evidences it |
| assessment | VA-PROJ | warning | project | project released in week 8, late in a 13-week semester |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 25.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 7 → 0 · round 1 accepted (7→1); round 2 accepted (1→0)
- structure: errors 2 → 0 · round 1 rejected (2→4); round 2 accepted (2→0)
- assessment: errors 5 → 1 · round 1 accepted (5→1); round 2 rejected (1→4); round 3 rejected (1→2)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: The professor specified that assessment weights must sum to exactly 130%, which violates standard grading schemes where weights sum to 100%.
- positioning: assessment_prefs: The professor specified special constraint SC1 stating that assessment weights must sum to exactly 130%, which violates standard IIIT-D grading policies where weights must sum to 100%.
- constraints: Special constraint SC1: The professor specified that assessment weights must sum to 130%, which conflicts with standard institutional rules requiring total assessment weights to equal 100%.
- los: hours_total: Sum of lecture hours across proposed LOs is 24 hours against the budget of 39 hours, and tutorial hours is 11 against 13. The shortfall reflects the modular breakdown where foundational and capstone LOs are consolidated; additional hours can be allocated to practical lab-assisted implementation sessions if required.
- narrative: SC1: The assessment weights provided in the approved graph sum to 100% (10 + 20 + 20 + 25 + 25), whereas constraint SC1 states they sum to 130%. This discrepancy has been reported for upstream resolution.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress from foundational agent configuration and specification parsing to workflow analysis, testing pipelines, and multi-module software factories, building directly upon the software engineering and programming fundamentals established in prerequisite course CSE201.
- **assessment rationale:** The assessment mix of quizzes, assignments, midsem, endsem, and a project aligns with the course objectives by combining theoretical understanding with practical application, hands-on coding, and project-based evaluation of agent-assisted workflows.
- **positioning rationale:** Unlike CSE701 which focuses on data mining and AI models for SE research, CSE581 which covers traditional requirements engineering, CSE582 which addresses legacy maintenance, or CSE594A which focuses on algorithmic agentic reasoning, this course specializes in practical, workflow-oriented software engineering processes for AI-native coding.