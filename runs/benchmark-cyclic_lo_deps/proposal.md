# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-cyclic_lo_deps` · generated deterministically from the design graph · validator status: **9 errors, 7 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level specified without a concrete course code | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to configure agent skills and tool use protocols, translate requirements into executable specifications, analyze execution traces from automated agent workflows, and assess pipelines integrating automated testing and reliability checks. Students will be able to configure agent skills and tool use protocols using an orchestration framework, translate natural language requirements into executable specifications, analyze execution traces to identify failure causes, and assess AI-native development pipelines. The course is taught through lectures, tutorials, and laboratory sessions emphasizing hands-on project work and developer workflows.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students require a strong grounding in advanced programming concepts, modularity, and automated testing to effectively understand automated testing and execute hands-on coding projects with AI tools. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in Software Engineering with an overlap of 0.185 (which is above the substantial threshold of 0.15), CSE701 focuses broadly on data and research literature in software engineering, whereas the new course specifically targets modern AI-native software development workflows, coding agents, and human-AI collaborative execution.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure agent skills, tool use protocols, and context engineering mechanisms for coding agents, using an agent orchestration framework, such that the configured agents successfully execute supplied coding tasks meeting functional specifications.** `[CORPUS, USER]`  
verb *configure* · behaviour *agent skills, tool use protocols, and context engineering mechanisms for coding agents* · condition *using an agent orchestration framework* · degree *such that the configured agents successfully execute supplied coding tasks meeting functional specifications* · evidence: lab_task, programming_assignment · marks share (computed): 31.17%

- CO1.LO1 (L1) Identify agent skills and context engineering mechanisms for coding agents using an agent orchestration framework, listing at least three protocol parameters for a supplied configuration file.
- CO1.LO2 (L3) Configure tool use protocols and agent skills using an agent orchestration framework, such that at least 80% of the provided test cases pass for a simple task.
- CO1.LO3 (L3 ★capstone) Configure agent skills, tool use protocols, and context engineering mechanisms for coding agents, using an agent orchestration framework, such that the configured agents successfully execute supplied coding tasks meeting functional specifications.

**CO2 (L3, procedural) — Translate natural language software requirements into executable specifications and structured development plans, using spec-driven development tools, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *translate* · behaviour *natural language software requirements into executable specifications and structured development plans* · condition *using spec-driven development tools* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 23.58%

- CO2.LO1 (L2) Exemplify natural language software requirements into intermediate structured development plans, using spec-driven development tools, for a supplied subset of use cases.
- CO2.LO2 (L3 ★capstone) Translate natural language software requirements into executable specifications and structured development plans, using spec-driven development tools, covering every use case in the supplied requirements document.

**CO3 (L4, conceptual) — Analyze execution traces and feedback loops from automated agent workflows, using log analysis tools for a supplied software factory artifact of at most 1000 lines of code, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *analyze* · behaviour *execution traces and feedback loops from automated agent workflows* · condition *using log analysis tools for a supplied software factory artifact of at most 1000 lines of code* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, programming_assignment · marks share (computed): 25.75%

- CO3.LO1 (L2) Trace execution logs from automated agent workflows using log analysis tools for a supplied software factory artifact of at most 500 lines of code, identifying the primary timestamped event sequence.
- CO3.LO2 (L4 ★capstone) Analyze execution traces and feedback loops from automated agent workflows, using log analysis tools for a supplied software factory artifact of at most 1000 lines of code, identifying at least three distinct failure causes with supporting log evidence.

**CO4 (L5, metacognitive) — Assess an AI-native software development pipeline integrating automated testing, evaluation, and reliability checks, justifying each assessment decision against at least one stated reliability requirement.** `[CORPUS, USER]`  
verb *assess* · behaviour *an AI-native software development pipeline integrating automated testing, evaluation, and reliability checks* · condition *given a multi-component software project requirements document* · degree *justifying each design decision against at least one stated reliability requirement* · evidence: project_deliverable, design_document · marks share (computed): 19.5%

- CO4.LO1 (L2) Compare testing, evaluation, and reliability check components in an AI-native software development pipeline, contrasting at least two metric types in a comparative table.
- CO4.LO2 (L5 ★capstone) Assess an AI-native software development pipeline integrating automated testing, evaluation, and reliability checks, justifying each assessment decision against at least one stated reliability requirement.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Agent skills and protocol parameters (M1.T1)<br>Tool use protocols and agent configuration (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Examine sample configuration files in pairs and trace at least three protocol parameters for agent orchestration frameworks. |  |
| 2 | Tool use protocols and agent configuration (M1.T2)<br>Developer workflows and context engineering mechanisms (M1.T3) | CO1.LO2, CO1.LO3 | CO1 | Trace tool use configuration files and debug 2 failing agent setups in small groups. | A:PA1 released |
| 3 | Developer workflows and context engineering mechanisms (M1.T3)<br>Software requirements and requirements engineering (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Review requirements engineering specifications and convert natural language text into intermediate structured development plans. | A:Quiz1 (quiz); A:PA1 due; A:PA2 released |
| 4 | Software requirements and requirements engineering (M2.T1)<br>Spec-driven development tools and executable specifications (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Evaluate spec-driven development artifacts and verify coverage of use cases in requirement documents. | A:Quiz2 (quiz) |
| 5 | Spec-driven development tools and executable specifications (M2.T2)<br>Loop engineering and iterative development (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Trace timestamped event sequences from provided execution logs of agent workflows in pairs. | A:PA2 due; A:DesignDoc released; A:ProjM1 released |
| 6 | Software factories and execution trace analysis (M3.T2) | CO3.LO2 | CO3 | Analyze execution traces to identify failure causes and map log evidence to software factory code segments. | A:Quiz3 (quiz); A:DesignDoc due |
| 7 | Automated testing and machine learning model evaluation (M4.T1)<br>Reliability checks and project evaluation frameworks (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Compare testing and evaluation metric types in a comparative table through guided group discussion. | A:Quiz4 (quiz); A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Reliability checks and project evaluation frameworks (M4.T2) | CO4.LO2 | CO4 | Review project evaluation frameworks and justify reliability decisions against project requirements. | A:ProjM1 due; A:ProjM2 released |
| 9 |  |  |  |  |  |
| 10 |  |  |  |  |  |
| 11 |  |  |  |  |  |
| 12 |  |  |  |  | A:ProjM2 due |
| 13 |  |  |  |  | A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Tool use protocols and agent configuration setup** — Configure basic tool use protocols and agent settings in the orchestration framework. Run a simple task and verify that at least 80% of test cases pass. | CO1.LO2 | AI coding tools/APIs, software development environments |
| 2 | **Context engineering and developer workflows** — Implement developer workflows and context engineering mechanisms using the orchestration framework to execute coding tasks. | CO1.LO3 | AI coding tools/APIs, software development environments |
| 3 | **Advanced context engineering and requirements translation** — Extend context engineering configurations and practise translating initial software requirements into intermediate structured development plans. | CO1.LO3 | AI coding tools/APIs, software development environments |
| 4 | **Spec-driven development tools and executable specifications** — Translate natural language requirements into executable specifications and structured development plans using spec-driven development tools. | CO2.LO2 | Spec-driven development tools, software development environments |
| 5 | **Loop engineering and iterative development** — Build and test iterative development loops using agent workflows to refine code artifacts automatically. | CO3.LO1 | AI coding tools/APIs, log analysis tools |
| 6 | **Software factories and execution trace analysis** — Trace execution logs from automated agent workflows and analyze failure causes with supporting log evidence from software factory artifacts. | CO3.LO2 | log analysis tools, software development environments |
| 7 | **Mid-sem week open lab and catch-up** — Open lab session for catch-up on prior exercises and review of pipeline evaluation frameworks. | CO4.LO2 | software development environments |
| 8 | **Reliability checks and project evaluation frameworks** — Assess an AI-native software development pipeline integrating automated testing and reliability checks against stated requirements. | CO4.LO2 | AI coding tools/APIs, software development environments |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (needs_confirmation); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3), A:Quiz2 (W4→W4), A:Quiz3 (W6→W6), A:Quiz4 (W7→W7) | best 3 of 4 | tool-use, analyse-data |  |
| assignment | 25.0 | A:PA1 (W2→W3), A:PA2 (W3→W5), A:DesignDoc (W5→W6) | — | implement, tool-use, design |  |
| project | 30.0 | A:ProjM1 (W5→W8), A:ProjM2 (W8→W12) | — | design, implement, evaluate-critique, tool-use |  |
| midsem | 15.0 | A:Midsem (W7→W7) | — | analyse-data, written-communication | Reduced written mid-semester examination weight of 15% accommodates greater continuous assessment weighting across practical programming assignments and project milestones. |
| endsem | 20.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique, written-communication |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 31.17%, CO2 23.58%, CO3 25.75%, CO4 19.5%

## 10. Resource material

Policy: **mixed** — Because AI-native software development and agentic workflows are rapidly evolving domains, the course relies on a combination of reference textbooks on agentic design patterns, official protocol documentation, and recent research papers alongside foundational software engineering texts.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Gullí, Antonio. "Agentic Design Patterns." Springer, 2025*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T1, M1.T2 |
| reference | OpenAI (2024). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M1.T2 |
| reading | Yujia Li, Shunyu Yao, Guanzhi Wang, John Yang, Alexander Novikov, Bogdan Georgiev (2024). *1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022.
2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022.
3) Wang, Guanzhi, et al. "Voyager: An Open-Ended Embodied Agent with Large Language Models." TMLR 2023.
4) Yang, John, et al. "Swe-agent: Agent-computer interfaces enable automated software engineering." NeurIPS 2024.
5) Novikov, Alexander, et al. "AlphaEvolve: A coding agent for scientific and algorithmic discovery." arXiv:2506.13131, 2025.
6) Georgiev, Bogdan, et al. "Mathematical exploration and discovery at scale." arXiv:2511.02864, 2025.
7) Other ongoing research reports.*. | R:hash:1-li-yujia-et-al-competition-level-code- | NO: candidate_id not in retrieved candidates | M3.T2, M4.T1 |
| reference | Ian Sommerville (2005). *Software Engineering*. | 9780133943030 | yes | M2.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 1 [unclaimed] | 3 [3] | 1 [unclaimed] | 3 [2] |
| CO2 | 2 [unclaimed] | 3 [3] | 1 [unclaimed] | 3 [unclaimed] |
| CO3 | 3 [3] | 3 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 3 [2] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring agent skills and tool protocols using an orchestration framework directly corresponds to designing and implementing a computer-based system using modern tools. (activities: implement, tool-use)
- CO1→PO9: Utilizing agent orchestration frameworks and context engineering mechanisms requires advanced techniques and tools in software engineering. (activities: tool-use)
- CO2→PO4: Translating requirements into executable specifications using spec-driven development tools constitutes the design phase of system development. (activities: design, tool-use)
- CO3→PO3: Analyzing execution traces and failure causes requires adapting log analysis and debugging techniques to solve agent workflow failures. (activities: analyse-data)
- CO4→PO4: Assessing and evaluating an AI-native software development pipeline against reliability requirements maps directly to system evaluation. (activities: evaluate-critique)
- CO4→PO9: Working with AI-native development pipelines and automated evaluation methodologies engages advanced computing tools. (activities: evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1, A:Midsem@L1 |
| CO1.LO2 | L3 | M1.T2 | 1, 2 | A:PA1@L3 |
| CO1.LO3 | L3 | M1.T3 | 2, 3 | A:PA2@L3, A:ProjM1@L3 |
| CO2.LO1 | L2 | M2.T1 | 3, 4 | A:Quiz2@L2, A:Midsem@L2 |
| CO2.LO2 | L3 | M2.T2 | 4, 5 | A:DesignDoc@L3, A:ProjM1@L3 |
| CO3.LO1 | L2 | M3.T1 | 5 | A:Quiz3@L2, A:Midsem@L2 |
| CO3.LO2 | L4 | M3.T2 | 6 | A:ProjM2@L4, A:Endsem@L4 |
| CO4.LO1 | L2 | M4.T1 | 7 | A:Quiz4@L2, A:Endsem@L2 |
| CO4.LO2 | L5 | M4.T2 | 7, 8 | A:ProjM2@L5 |

## Appendix C — Modules and topics

**M1 Agent Orchestration and Tool Use** (primary CO1)
- M1.T1 Agent skills and protocol parameters — 2.0 h · LOs CO1.LO1
- M1.T2 Tool use protocols and agent configuration — 2.5 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Developer workflows and context engineering mechanisms — 2.5 h · LOs CO1.LO3 · requires M1.T2
**M2 Spec-Driven Development and Requirements Engineering** (primary CO2)
- M2.T1 Software requirements and requirements engineering — 2.5 h · LOs CO2.LO1
- M2.T2 Spec-driven development tools and executable specifications — 3.0 h · LOs CO2.LO2 · requires M2.T1
**M3 Log Analysis and Automated Agent Workflows** (primary CO3)
- M3.T1 Loop engineering and iterative development — 2.5 h · LOs CO3.LO1
- M3.T2 Software factories and execution trace analysis — 3.0 h · LOs CO3.LO2 · requires M3.T1
**M4 Pipeline Assessment, Testing, and Reliability** (primary CO4)
- M4.T1 Automated testing and machine learning model evaluation — 2.5 h · LOs CO4.LO1
- M4.T2 Reliability checks and project evaluation frameworks — 3.0 h · LOs CO4.LO2 · requires M4.T1, M1.T3, M2.T2, M3.T2

Schedule: feasible · 23.5 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 examines data-driven software engineering and research literature, whereas the new course focuses on operationalizing AI coding agents, developer workflows, and agentic engineering practices. |
| CSE594A | 0.08 | complementary | CSE594A focuses primarily on agentic reasoning for algorithmic and mathematical problem-solving, whereas this course applies agentic systems specifically to software development workflows and engineering practice. |
| CSE582 | 0.067 | superficial | CSE582 addresses traditional software product lines, maintenance, and re-engineering, whereas the new course investigates AI-driven software factories and generative workflow automation. |
| CSE581 | 0.034 | superficial | CSE581 covers cognitive perspectives and traditional/agile systems analysis, whereas the new course focuses on AI-native specification and execution. |
| AI501 | 0.034 | superficial | AI501 provides foundational machine learning theory and modeling, whereas this course assumes ML capability and applies AI tools to software engineering workflows. |
| CSE201 | 0.017 | superficial | CSE201 teaches foundational advanced programming and manual unit testing in Java, whereas the new course deals with automated agentic testing and loop engineering. |
| CSE583 | 0.0 | superficial | CSE583 focuses on open-source software and tools, whereas this course focuses on AI-native development. |
| CSE665 | 0.0 | superficial | CSE665 covers foundational transformer architectures and LLM training principles, whereas this course applies existing models to software workflows. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Literature review structure and assessment format for evaluating AI applications in software engineering. Avoid: Over-reliance on retrospective data mining of repositories rather than active, real-time AI-native workflow construction.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Foundational concepts of agentic protocols (such as MCP) and agent tool use. Avoid: Mathematical and algorithmic problem-solving focus, keeping the emphasis strictly on software development engineering.
- **CSE201** Advanced Programming — IIIT-D catalogue. Take: Rigorous testing and modular design practices as a baseline for engineering reliability. Avoid: Traditional manual design pattern instruction without AI assistance.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| los | VLO-COPY | error | CO1.LO3, CO1 | CO1.LO3 restates its parent CO1 (token overlap 1.00); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO2.LO2, CO2 | CO2.LO2 restates its parent CO2 (token overlap 1.00); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO3.LO2, CO3 | CO3.LO2 restates its parent CO3 (token overlap 1.00); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO4.LO2, CO4 | CO4.LO2 restates its parent CO4 (token overlap 1.00); an LO must be a narrower, single-task step |
| los | VLO-COUNT | error |  | 9 LOs in total (expected 10–20) |
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Gullí, Antonio. "Agentic Design Patterns." Springer, 2025' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:1-li-yujia-et-al-competition-level-code- | resource '1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022.
2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022.
3) Wang, Guanzhi, et al. " |
| structure | V21 | error |  | topics fill only 23.5 h of 39 h (< 85%): the schedule would leave teaching weeks empty |
| cos | V11 | warning | CO4 | CO CO4 condition is not visible in the statement text |
| cos | V11 | warning | CO4 | CO CO4 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 degree is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 31.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W09, W10, W11, W12, W13 | weeks with no lecture topics: [9, 10, 11, 12, 13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 5 → 5 · round 1 rejected (5→11); round 2 rejected (5→7); round 3 rejected (5→12)
- structure: errors 1 → 1 · round 1 rejected (1→9); round 2 rejected (1→3); round 3 rejected (1→1)
- assessment: errors 2 → 0 · round 1 accepted (2→1); round 2 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Special constraints contain a circular dependency requirement (LO 1 requires LO 2, and LO 2 requires LO 1), which creates a cycle in learning outcome dependencies.
- positioning: Special Constraint SC1: CRITICAL: Make LO 1 require LO 2, and LO 2 require LO 1 (dependency cycle). This is handled by downstream validation components as noted in special constraints.
- constraints: Special constraints: SC1 introduces a dependency cycle between LO1 and LO2 which is pedagogically invalid and cannot be modeled using standard target parameters.
- cos: SC1: Special constraint SC1 requests a dependency cycle between LO1 and LO2, which will be managed at the Learning Outcome stage as instructed.
- los: SC1: Special constraint SC1 requests a dependency cycle between LO 1 and LO 2 (make LO 1 require LO 2, and LO 2 require LO 1). However, structural rule 4 requires the dependency graph to be acyclic. Acyclic rule takes precedence to prevent deadlocks, so no cycle was created.
- los: hours_total: The sum of estimated hours across the 9 generated LOs (Lecture: 31h, Tutorial: 10h, Lab: 22h) is slightly below the budget targets (Lecture: 39h, Tutorial: 13h, Lab: 26h) to maintain appropriate scope and granularity per LO without artificial padding.
- structure: special_constraints: SC1 requested a dependency cycle between LO1 and LO2, which violates valid structural rules and DAG requirements.
- narrative: SC1: Special constraint SC1 mentions a dependency cycle between LO 1 and LO 2, which contradicts standard instructional design practices and cannot be formally represented in the approved graph summary.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress from foundational agent orchestration and tool use to spec-driven development, log analysis of automated agent workflows, and finally pipeline assessment and reliability checks. This sequence builds upon the mandatory prerequisite knowledge of advanced programming and automated testing from CSE201.
- **assessment rationale:** The assessment mix comprising quizzes, assignments, projects, mid-semester, and end-semester examinations aligns with the course outcomes by combining theoretical understanding with practical, hands-on evaluation of agent-assisted software development processes, projects, and pipeline reliability.
- **positioning rationale:** This course differs from CSE701, which emphasizes data-driven software engineering and research literature, and CSE594A, which focuses on agentic reasoning for algorithmic problem-solving, by specifically targeting operationalized AI coding agents, developer workflows, and agentic software engineering practices.