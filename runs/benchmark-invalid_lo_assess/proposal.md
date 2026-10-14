# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-invalid_lo_assess` · generated deterministically from the design graph · validator status: **4 errors, 17 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Level is stated as Advanced undergraduate, but course code is missing. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with increasingly capable coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. The curriculum is delivered through lectures, tutorials, and laboratory sessions, engaging students with hands-on coding and project work. By the end of the course, students will be able to configure coding agents and agent skills using orchestration frameworks, construct executable specifications from requirements documents, analyse development loops and execution traces, and assess the reliability and correctness of automated test suites and agent-generated software outputs. The course is taught through a combination of lectures, tutorials, and practical lab sessions.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 (or CSE201) `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm, Collection framework | Students need solid software development and advanced programming fundamentals to understand automated testing, code structure, and hands-on agent-assisted development. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers some overlapping themes on AI in software engineering (weighted Jaccard 0.185), it focuses on general data mining and empirical studies of software repositories rather than hands-on AI-native developer workflows, coding agents, and agentic software engineering.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure coding agents and agent skills using an agent orchestration framework and Model Context Protocol, such that at least 80% of the provided test cases pass.** `[CORPUS, USER]`  
verb *configure* · behaviour *coding agents and agent skills* · condition *using an agent orchestration framework and Model Context Protocol* · degree *such that at least 80% of the provided test cases pass* · evidence: programming_assignment, lab_task · marks share (computed): 20.0%

- CO1.LO1 (L3) Configure agent orchestration frameworks on development machines for coding tasks, completing all setup steps within the lab session.
- CO1.LO2 (L3) Apply coding agents and agent skills using Model Context Protocol, producing output that matches the reference for 3 supplied inputs.
- CO1.LO3 (L3 ★capstone) Configure an agent orchestration framework and Model Context Protocol on a development machine, such that at least 80% of the provided test cases pass.

**CO2 (L3, procedural) — Construct executable specifications and context engineering artifacts from a given requirements document, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *construct* · behaviour *executable specifications and context engineering artifacts* · condition *from a given requirements document* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 24.5%

- CO2.LO1 (L3) Identify functional requirements and use cases from a provided requirements document for context engineering.
- CO2.LO2 (L3 ★capstone) Construct executable specifications for a given software module, covering every use case in the supplied requirements document.

**CO3 (L4, metacognitive) — Analyse the development loops and execution traces produced by coding agents for a supplied software task, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *analyse* · behaviour *the development loops and execution traces produced by coding agents* · condition *for a supplied software task* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, code_review · marks share (computed): 24.5%

- CO3.LO1 (L4) Trace development loops and execution logs produced by coding agents for a supplied software task.
- CO3.LO2 (L4 ★capstone) Analyse the development loops for a supplied software task, identifying at least three distinct failure causes in the execution logs.

**CO4 (L5, conceptual) — Assess the reliability and correctness of automated test suites and software outputs generated through agentic workflows, justifying each evaluation decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *assess* · behaviour *the reliability and correctness of automated test suites and software outputs generated through agentic workflows* · condition *using automated testing tools and evaluation benchmarks* · degree *justifying each evaluation decision against at least one stated requirement* · evidence: report, code_review · marks share (computed): 18.5%

- CO4.LO1 (L5) Execute automated test suites and evaluation benchmarks on software outputs generated through agentic workflows.
- CO4.LO2 (L5 ★capstone) Assess a single test suite execution report generated through agentic workflows, justifying each evaluation decision against at least one stated requirement.

**CO5 (L5, metacognitive) — Assess an end-to-end AI-native software development workflow for a multi-module application, demonstrated live, with 3 scenario walkthroughs chosen by the evaluator.** `[CORPUS, USER]`  
verb *assess* · behaviour *an end-to-end AI-native software development workflow for a multi-module application* · condition *using collaborative coding agents, software factories, and automated deployment tools* · degree *demonstrated live, with 3 scenario walkthroughs chosen by the evaluator* · evidence: project_deliverable, presentation · marks share (computed): 12.5%

- CO5.LO1 (L5) Configure multi-module software development environments using collaborative coding agents and software factories.
- CO5.LO2 (L5 ★capstone) Assess an end-to-end AI-native software development workflow for a single component, demonstrated live, with 3 scenario walkthroughs chosen by practical evaluation.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Agent orchestration framework setup (M1.T1)<br>Model Context Protocol and agent skills integration (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Worked trace-diagnosis of 3 initial agent framework setup errors, in pairs. |  |
| 2 | Model Context Protocol and agent skills integration (M1.T2)<br>Coding agents configuration and test validation (M1.T3) | CO1.LO2, CO1.LO3 | CO1 | Problem-solving session on Model Context Protocol configuration issues and debugging agent skills integration. | A:Lab1 (lab) |
| 3 | Coding agents configuration and test validation (M1.T3)<br>Requirements engineering and use case identification (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Review and troubleshooting of coding agents configuration and test validation failures. | A:PA1 released |
| 4 | Requirements engineering and use case identification (M2.T1)<br>Spec-driven development and executable specifications (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Worked trace-diagnosis of ambiguous requirements documents into structured use case identification. | A:PA1 due |
| 5 | Spec-driven development and executable specifications (M2.T2)<br>Development loops and execution log tracing (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Collaborative drafting of executable specifications for a complex software module in small groups. | A:Lab2 (lab); A:DesignDoc released |
| 6 | Assisting code review and code analysis (M3.T2) | CO3.LO2 | CO3 | Analysis of development loops and identification of execution log failure causes from sample traces. | A:DesignDoc due; A:ProjectMilestone1 released |
| 7 | Automated testing and benchmark execution (M4.T1)<br>Machine learning model and workflow evaluation (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Walkthrough and evaluation of automated test suite execution reports against requirements. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Machine learning model and workflow evaluation (M4.T2)<br>Multi-agent collaboration and software factories (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Discussion and critique of machine learning model and workflow evaluation reports. | A:ProjectFinal released |
| 9 | Multi-agent collaboration and software factories (M5.T1)<br>Project discussion and live workflow walkthroughs (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Problem-solving on multi-agent collaboration setups and software factory configuration issues. | A:ProjectMilestone1 due |
| 10 | Project discussion and live workflow walkthroughs (M5.T2) | CO5.LO2 | CO5 | Peer review and critique of live workflow walkthrough plans for final presentation preparation. |  |
| 11 |  |  |  |  | A:ProjectFinal due |
| 12 |  |  |  |  |  |
| 13 |  |  |  |  | A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Agent Orchestration and MCP Setup** — Students configure agent orchestration frameworks and integrate Model Context Protocol (MCP) on their machines, verifying setup against 3 supplied test inputs. | CO1.LO1, CO1.LO2 | Student development machines, AI coding tools/APIs |
| 2 | **Coding Agents and Test Validation** — Students configure coding agents and run test validations, ensuring at least 80% of provided test cases pass successfully. | CO1.LO3 | Student development machines, AI coding tools/APIs |
| 3 | **Requirements to Coding Agents** — Students use configured coding agents to implement code based on functional requirements and use cases identified from requirements documents. | CO1.LO3, CO2.LO1 | Student development machines, AI coding tools/APIs |
| 4 | **Spec-Driven Development** — Students construct executable specifications for a given software module covering all use cases in the requirements document. | CO2.LO2 | Student development machines, software development environments |
| 5 | **Execution Log Tracing** — Students trace development loops and execution logs produced by coding agents for a supplied software task. | CO3.LO1 | Student development machines, AI coding tools/APIs |
| 6 | **Code Review and Analysis Practice** — Students analyze development loops and code review outputs to identify distinct failure causes in execution logs. | CO3.LO2 | Student development machines, software development environments |
| 7 | **Automated Testing and Benchmarks** — Students execute automated test suites and evaluation benchmarks on software outputs generated through agentic workflows. | CO4.LO1 | Student development machines, AI coding tools/APIs |
| 8 | **Workflow Evaluation** — Students assess single test suite execution reports generated through agentic workflows and justify evaluation decisions. | CO4.LO2 | Student development machines |
| 9 | **Multi-Agent Software Factories** — Students configure multi-module software development environments using collaborative coding agents and software factories. | CO5.LO1 | Student development machines, AI coding tools/APIs, software development environments |
| 10 | **End-to-End Workflow Walkthroughs** — Students perform live walkthroughs and present end-to-end AI-native software development workflows with 3 scenario walkthroughs. | CO5.LO2 | Student development machines, TA support |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| lab | 20.0 | A:Lab1 (W2→W2), A:Lab2 (W5→W5) | — | implement, tool-use |  |
| assignment | 20.0 | A:PA1 (W3→W4), A:DesignDoc (W5→W6) | — | design, implement, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data |  |
| project | 25.0 | A:ProjectMilestone1 (W6→W9), A:ProjectFinal (W8→W11) | — | design, implement, evaluate-critique, oral-presentation |  |
| endsem | 15.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique | Adjusted within prior band to accommodate project weighting for an AI-native hands-on course. |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 20.0%, CO2 24.5%, CO3 24.5%, CO4 18.5%, CO5 12.5%

## 10. Resource material

Policy: **mixed** — The course covers fast-moving topics in AI-native software development and coding agents where standard textbooks are complemented by recent research papers and framework documentation.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Agentic Design Patterns.*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T1, M5.T1 |
| reference |  (None). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M1.T2 |
| reference | Gerald Versluis (2026). *The Model Context Protocol*. | 10.1007/979-8-8688-3010-5_1 | yes | M1.T2 |
| reading | Jahnavi Bellapukonda (2026). *A Comparative Evaluation of LLM-based Coding Agents for Automated Software development Tasks*. | 10.2139/ssrn.6755658 | yes | M4.T1, M4.T2 |
| reading | Yujia Li, Shunyu Yao, Guanzhi Wang, John Yang, Alexander Novikov, Bogdan Georgiev (2024). *1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022.
2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022.
3) Wang, Guanzhi, et al. "Voyager: An Open-Ended Embodied Agent with Large Language Models." TMLR 2023.
4) Yang, John, et al. "Swe-agent: Agent-computer interfaces enable automated software engineering." NeurIPS 2024.
5) Novikov, Alexander, et al. "AlphaEvolve: A coding agent for scientific and algorithmic discovery." arXiv:2506.13131, 2025.
6) Georgiev, Bogdan, et al. "Mathematical exploration and discovery at scale." arXiv:2511.02864, 2025.
7) Other ongoing research reports.*. | R:hash:1-li-yujia-et-al-competition-level-code- | NO: candidate_id not in retrieved candidates | M3.T1, M4.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 |  | 3 [3] |  | 3 [2] |
| CO2 | 2 [unclaimed] | 2 [3] |  | 2 [unclaimed] |
| CO3 | 2 [3] | 2 [unclaimed] |  | 2 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [3] | 3 [unclaimed] | 3 [unclaimed] |
| CO5 |  | 3 [2] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring agents via orchestration frameworks directly implements and sets up a computer-based system using modern tools. (activities: implement, tool-use)
- CO1→PO9: Utilizing Model Context Protocol and agent orchestration frameworks demonstrates the application of advanced tools. (activities: tool-use)
- CO2→PO4: Constructing specifications and engineering artifacts directly aligns with designing application components to meet requirements. (activities: design, implement)
- CO3→PO3: Analysing execution traces and identifying failure causes exercises systematic problem analysis and adaptation. (activities: analyse-data)
- CO4→PO4: Assessing reliability and correctness corresponds directly to evaluating software systems against stated requirements. (activities: evaluate-critique)
- CO5→PO4: Evaluating multi-module application workflows using automated deployment tools contributes to overall system evaluation. (activities: evaluate-critique)
- CO5→PO7: Live scenario walkthroughs and presentations require effective oral communication of technical workflows. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1 | 1 | A:Lab1@L3 |
| CO1.LO2 | L3 | M1.T2 | 1, 2 | A:Lab1@L3 |
| CO1.LO3 | L3 | M1.T3 | 2, 3 | A:PA1@L3 |
| CO2.LO1 | L3 | M2.T1 | 3, 4 | A:Midsem@L3, A:Endsem@L3 |
| CO2.LO2 | L3 | M2.T2 | 4, 5 | A:DesignDoc@L3 |
| CO3.LO1 | L4 | M3.T1 | 5 | A:Lab2@L4 |
| CO3.LO2 | L4 | M3.T2 | 6 | A:Midsem@L4, A:Endsem@L4 |
| CO4.LO1 | L5 | M4.T1 | 7 | A:ProjectMilestone1@L5 |
| CO4.LO2 | L5 | M4.T2 | 7, 8 | A:ProjectFinal@L5, A:Endsem@L5 |
| CO5.LO1 | L5 | M5.T1 | 8, 9 | A:ProjectMilestone1@L5 |
| CO5.LO2 | L5 | M5.T2 | 9, 10 | A:ProjectFinal@L5 |

## Appendix C — Modules and topics

**M1 Agent Orchestration and Setup** (primary CO1)
- M1.T1 Agent orchestration framework setup — 2.0 h · LOs CO1.LO1
- M1.T2 Model Context Protocol and agent skills integration — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Coding agents configuration and test validation — 3.0 h · LOs CO1.LO3 · requires M1.T2
**M2 Context Engineering and Specifications** (primary CO2)
- M2.T1 Requirements engineering and use case identification — 2.0 h · LOs CO2.LO1
- M2.T2 Spec-driven development and executable specifications — 3.0 h · LOs CO2.LO2 · requires M2.T1
**M3 Loop Engineering and Failure Analysis** (primary CO3)
- M3.T1 Development loops and execution log tracing — 2.0 h · LOs CO3.LO1 · requires M1.T3
- M3.T2 Assisting code review and code analysis — 3.0 h · LOs CO3.LO2 · requires M3.T1
**M4 Automated Evaluation and Testing** (primary CO4)
- M4.T1 Automated testing and benchmark execution — 2.0 h · LOs CO4.LO1 · requires M1.T3
- M4.T2 Machine learning model and workflow evaluation — 3.0 h · LOs CO4.LO2 · requires M4.T1
**M5 Software Factories and Project Workflows** (primary CO5)
- M5.T1 Multi-agent collaboration and software factories — 3.0 h · LOs CO5.LO1 · requires M1.T3, M2.T2
- M5.T2 Project discussion and live workflow walkthroughs — 2.0 h · LOs CO5.LO2 · requires M5.T1, M3.T2, M4.T2

Schedule: feasible · 28.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 treats AI in SE from a data-mining and research perspective, whereas the new course focuses on practical, workflow-oriented agent-assisted software development and engineering practice. |
| CSE594A | 0.08 | complementary | CSE594A concentrates broadly on agentic reasoning and algorithmic/mathematical problem-solving using LLMs, while the new course applies agentic reasoning specifically to software development workflows and engineering tasks. |
| CSE582 | 0.067 | complementary | CSE582 deals with traditional software product lines, evolution, and maintenance, whereas the new course explores modern automated software factories and AI-driven workflows. |
| CSE581 | 0.034 | superficial | CSE581 covers traditional systems analysis and requirements engineering, whereas the new course focuses on spec-driven development using AI. |
| AI501 | 0.034 | superficial | AI501 provides foundational machine learning theory, whereas the new course assumes basic software and AI familiarity to study applied agentic coding workflows. |
| CSE201 | 0.017 | superficial | CSE201 teaches object-oriented programming and basic unit testing in Java, whereas the new course builds on these fundamentals to explore AI-assisted and agent-driven software engineering. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Advanced literature review and assessment style regarding AI applications in software engineering Avoid: Over-emphasis on data-mining repositories rather than active coding workflows
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Concepts of agentic protocols, tool use, and MCP infrastructure for agent development Avoid: Focus purely on algorithmic and mathematical problem-solving
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation structure and team-based practical development using modern tools Avoid: Traditional open-source process models without AI automation

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Agentic Design Patterns.' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:1-li-yujia-et-al-competition-level-code- | resource '1) Li, Yujia, et al. "Competition-level code generation with alphacode." Science, 2022.
2) Yao, Shunyu, et al. "React: Synergizing reasoning and acting in language models." ICLR 2022.
3) Wang, Guanzhi, et al. " |
| structure | V21 | error |  | topics fill only 28.0 h of 39 h (< 85%): the schedule would leave teaching weeks empty |
| cos | V11 | warning | CO4 | CO CO4 condition is not visible in the statement text |
| cos | V11 | warning | CO5 | CO CO5 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO2 | LO CO2.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 28.0 h vs budget 39 h (±15%) |
| los | VB | warning | CO2.LO1 | LO CO2.LO1: claimed Bloom L3 but verb 'identify' is lexicon L1 |
| los | VB | warning | CO3.LO1 | LO CO3.LO1: claimed Bloom L4 but verb 'trace' is lexicon L2 |
| los | VB | warning | CO4.LO1 | LO CO4.LO1: claimed Bloom L5 but verb 'execute' is lexicon L3 |
| los | VB | warning | CO5.LO1 | LO CO5.LO1: claimed Bloom L5 but verb 'configure' is lexicon L3 |
| schedule | V6 | warning | W11, W12, W13 | weeks with no lecture topics: [11, 12, 13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 6 → 0 · round 1 accepted (6→2); round 2 accepted (2→1); round 3 accepted (1→0)
- structure: errors 1 → 1 · round 1 rejected (1→6); round 2 rejected (1→1); round 3 rejected (1→6)
- assessment: errors 5 → 0 · round 1 accepted (5→1); round 2 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Instructor instruction requests mapping assessments to non-existent learning objective IDs like 'LO_FAKE_1'.
- positioning: special_constraints: SC1 requires mapping assessments to non-existent LO IDs like 'LO_FAKE_1'. The automated validator will likely flag this.
- constraints: Special constraint SC1: The special constraint explicitly requests mapping assessments to non-existent learning outcome IDs ('LO_FAKE_1'), which will fail validation against the institutional knowledge graph.
- cos: SC1: Special constraint SC1 mandates mapping assessments to non-existent LO IDs like 'LO_FAKE_1'. This violates institutional alignment rules for learning outcomes and should be reviewed.
- los: hours_total: Calculated total lecture hours (29), tutorial hours (11), and lab hours (24) are slightly below the budget of 39/13/26, but are adequate for the 11 defined LOs without artificial padding.
- los: SC1: Special constraint SC1 asks to map assessments to fake LO IDs like 'LO_FAKE_1', but R4 prohibits referencing non-existent IDs. We have adhered strictly to the valid LO schema.
- structure: special_constraints: Special constraint SC1 asks to map assessments to non-existent LO IDs like 'LO_FAKE_1'. This violates R4 and the structural rule that all topics/assessments must link to valid frozen LOs.
- narrative: SC1: Special constraint SC1 requests mapping assessments to non-existent LO IDs like 'LO_FAKE_1', which violates system node referencing rules.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress logically from foundational agent orchestration and setup through context engineering, execution loop analysis, automated testing, and finally multi-agent software factories. This sequence relies on core software development prerequisites such as CSE201 to ensure students possess the necessary programming fundamentals before tackling agent-assisted engineering workflows.
- **assessment rationale:** The assessment mix comprising labs, assignments, midsem, project, and endsem aligns with the practical, workflow-oriented emphasis of the course objectives. Practical assignments and labs evaluate hands-on configuration and debugging skills, while the project and examinations assess comprehensive understanding of agentic workflows and reliability analysis.
- **positioning rationale:** Unlike CSE701 which treats AI in software engineering from a data-mining and research perspective, or CSE594A which focuses on agentic reasoning and mathematical problem-solving, this course specifically targets practical, workflow-oriented agent-assisted software development. It differs from CSE582 by addressing modern automated software factories rather than traditional product lines.