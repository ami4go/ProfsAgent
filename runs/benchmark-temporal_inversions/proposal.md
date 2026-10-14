# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-temporal_inversions` · generated deterministically from the design graph · validator status: **2 errors, 16 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Course level is stated as Advanced undergraduate, but specific course code is [NOT SPECIFIED]. | professor |
| — | CONFLICT ['K14'] | — | Topological ordering constraint requires week 4 topics to depend on week 8 topics, which violates chronological sequencing. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. The curriculum addresses AI-assisted coding and developer workflows, Model Context Protocol and tool use APIs, requirements engineering and specification-driven development, iterative loop engineering, and system assessment. Students will be able to configure AI-assisted coding tools, construct agent skills and Model Context Protocol integrations, decompose requirements into executable specifications, analyse iterative loop engineering workflows, and assess AI-native software development systems. The course is taught through a combination of lectures, tutorials, and practical laboratory sessions involving hands-on coding and projects.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm, Generic programming | Students require solid software development fundamentals and unit testing knowledge to build reliable software and set up automated testing loops in AI-native workflows. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers aspects of AI in Software Engineering and has an overlap of 0.185, the new course focuses specifically on modern AI-native software development involving collaborative coding agents, workflow engineering, and agentic protocols rather than general mining of software repositories and empirical software engineering topics.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure AI-assisted coding tools and developer workflows for a given software project, using agent orchestration frameworks, such that at least 80% of the provided acceptance tests pass.** `[CORPUS, USER]`  
verb *configure* · behaviour *AI-assisted coding tools and developer workflows* · condition *for a given software project, using agent orchestration frameworks* · degree *such that at least 80% of the provided acceptance tests pass* · evidence: programming_assignment, lab_task · marks share (computed): 23.5%

- CO1.LO1 (L1) Identify key components of AI-assisted coding tools and developer workflows for a given software project.
- CO1.LO2 (L3) Configure agent orchestration frameworks for a supplied multi-agent software project, such that at least 50% of the provided acceptance tests pass.
- CO1.LO3 (L3 ★capstone) Configure agent orchestration frameworks for a supplied multi-agent software project, such that at least 90% of the provided acceptance tests pass.

**CO2 (L3, procedural) — Construct agent skills and Model Context Protocol integrations for a given application codebase, utilizing specified tool use APIs, meeting the stated interface specification for every public method.** `[CORPUS, USER]`  
verb *construct* · behaviour *agent skills and Model Context Protocol integrations* · condition *for a given application codebase, utilizing specified tool use APIs* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment, code_review · marks share (computed): 23.5%

- CO2.LO1 (L2) Explain Model Context Protocol integrations and specified tool use APIs for a given application codebase.
- CO2.LO2 (L3) Construct agent skills using specified tool use APIs for a given application module, meeting the interface specification for at least 50% of public methods.
- CO2.LO3 (L3 ★capstone) Construct Model Context Protocol integrations using specified tool use APIs for a given application module, meeting the stated interface specification for every public method.

**CO3 (L4, conceptual) — Decompose requirements into executable specifications for a supplied software problem statement, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *decompose* · behaviour *requirements into executable specifications* · condition *for a supplied software problem statement* · degree *covering every use case in the supplied requirements document* · evidence: design_document, exam_question · marks share (computed): 20.0%

- CO3.LO1 (L1) Identify requirements and use cases from a supplied software problem statement.
- CO3.LO2 (L4) Decompose requirements into executable specifications for a supplied software problem statement, covering a single key use case from the supplied requirements document.
- CO3.LO3 (L4 ★capstone) Decompose requirements into executable specifications for a supplied software component problem statement, covering every use case in a single provided subsystem requirements document.

**CO4 (L4, conceptual) — Analyse iterative loop engineering workflows and automated testing outputs, identifying at least three distinct failure causes with supporting log evidence from the execution trace.** `[CORPUS, USER]`  
verb *analyse* · behaviour *iterative loop engineering workflows and automated testing outputs* · condition *using execution trace logs from software factories* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, report · marks share (computed): 15.5%

- CO4.LO1 (L4) Examine iterative loop engineering workflows and automated testing outputs using execution trace logs from software factories.
- CO4.LO2 (L4 ★capstone) Analyse iterative loop engineering workflows using execution trace logs from a single software factory run, identifying at least three distinct failure causes with supporting log evidence.

**CO5 (L5, procedural) — Assess an AI-native software development system for a complex multi-module project, justifying each design decision against at least one stated requirement and demonstrated live with scenario walkthroughs.** `[CORPUS, USER]`  
verb *assess* · behaviour *an AI-native software development system* · condition *for a complex multi-module project* · degree *justifying each design decision against at least one stated requirement and demonstrated live with scenario walkthroughs* · evidence: project_deliverable, presentation · marks share (computed): 17.5%

- CO5.LO1 (L5) Review an AI-native software development system for a complex multi-module project against stated requirements.
- CO5.LO2 (L5 ★capstone) Assess an AI-native software development system for a single module project, justifying each design decision against at least one stated requirement and demonstrated live with scenario walkthroughs.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding and developer workflows overview (M1.T1)<br>Agent orchestration frameworks configuration (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Worked trace-diagnosis of developer workflow components in pairs, reviewing sample tool outputs. |  |
| 2 | Agent orchestration frameworks configuration (M1.T2)<br>Coding agents deployment and pipeline configuration (M1.T3) | CO1.LO2, CO1.LO3 | CO1 | Trace analysis of agent orchestration configurations to resolve common startup failures. |  |
| 3 | Coding agents deployment and pipeline configuration (M1.T3)<br>Model Context Protocol integrations and tool use APIs (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Peer review of coding agent deployment scripts and pipeline configuration files. | A:PA1 (assignment) |
| 4 | Model Context Protocol integrations and tool use APIs (M2.T1)<br>Context engineering and agent skills construction (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Problem-solving session mapping Model Context Protocol integration requirements to API endpoints. | A:Quiz1 (quiz) |
| 5 | Context engineering and agent skills construction (M2.T2)<br>Advanced MCP codebase integration (M2.T3) | CO2.LO2, CO2.LO3 | CO2 | Walkthrough and debugging of agent skills construction tasks in small groups. | A:ProjectDeliverable released |
| 6 | Advanced MCP codebase integration (M2.T3)<br>Requirements elicitation and use case identification (M3.T1) | CO2.LO3, CO3.LO1 | CO2, CO3 | Code walk-through of advanced MCP codebase integrations to verify interface compliance. | A:PA2 (assignment) |
| 7 | Requirements to executable specifications decomposition (M3.T2) | CO3.LO2 | CO3 | Analysis of software problem statements to extract structured requirements and use cases. |  |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Comprehensive specification-driven development documentation (M3.T3) | CO3.LO3 | CO3 | Group critique of requirements decomposition into executable specifications. | A:DesignDoc (design_document) |
| 9 | Iterative loop engineering workflows and trace log examination (M4.T1)<br>Software factories and diagnostic evaluation (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Examination of iterative loop failure logs and tracing automated testing outputs. | A:Midsem (midsem) |
| 10 | Software factories and diagnostic evaluation (M4.T2)<br>AI-native software development system evaluation planning (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Review of software factory execution trace logs to isolate root causes of diagnostic test failures. |  |
| 11 | AI-native software development system evaluation planning (M5.T1)<br>Emerging developer tools and capstone system demonstration (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Discussion and planning of evaluation criteria for AI-native software development systems. |  |
| 12 | Capstone system demonstration and walkthrough (M5.T3) | CO5.LO2 | CO5 | Peer review of capstone system demonstration structure and design justifications. | A:ProjectDeliverable due |
| 13 |  |  |  |  |  |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Agent Orchestration Setup** — Configure agent orchestration frameworks on development machines and run a baseline multi-agent test case. | CO1.LO2 | Student development machines, access to AI coding tools/APIs |
| 2 | **Coding Agents Pipeline Configuration** — Deploy coding agents and configure local pipeline settings to pass initial automated acceptance tests. | CO1.LO2, CO1.LO3 | Student development machines, access to AI coding tools/APIs |
| 3 | **Advanced Pipeline Deployment** — Refine coding agent pipelines and execute test suites to achieve required acceptance thresholds. | CO1.LO3 | Student development machines, access to AI coding tools/APIs |
| 4 | **Context Engineering and Agent Skills** — Construct agent skills using specified tool use APIs for an application module. | CO2.LO2 | Student development machines, access to AI coding tools/APIs |
| 5 | **Advanced MCP Codebase Integration** — Implement Model Context Protocol integrations for application modules meeting public method interface specifications. | CO2.LO2, CO2.LO3 | Student development machines, access to AI coding tools/APIs |
| 6 | **MCP Integration Finalisation** — Finalise and test complex Model Context Protocol integrations against interface specifications. | CO2.LO3 | Student development machines, access to AI coding tools/APIs |
| 7 | **Requirements Decomposition** — Decompose requirements into executable specifications for a supplied software problem statement. | CO3.LO2 | Student development machines |
| 8 | **Specification-Driven Development** — Develop comprehensive specification documents covering every use case in a subsystem requirements document. | CO3.LO3 | Student development machines |
| 9 | **Trace Log Examination** — Examine execution trace logs from software factories to identify system behaviours. | CO4.LO1 | Student development machines |
| 10 | **Software Factory Diagnostic Evaluation** — Analyse iterative loop engineering workflows using execution trace logs, identifying distinct failure causes. | CO4.LO2 | Student development machines, access to AI coding tools/APIs |
| 11 | **Capstone System Preparation** — Set up project repositories and preliminary evaluation plans for the capstone system. | CO5.LO1 | Student development machines, access to AI coding tools/APIs |
| 12 | **Capstone Demonstration** — Demonstrate the AI-native software development system with scenario walkthroughs. | CO5.LO2 | Student development machines, access to AI coding tools/APIs |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (needs_confirmation); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W4→W4) | — | tool-use, analyse-data |  |
| assignment | 25.0 | A:PA1 (W3→W3), A:PA2 (W6→W6) | — | implement, tool-use |  |
| design_document | 20.0 | A:DesignDoc (W8→W8) | — | design, written-communication |  |
| midsem | 20.0 | A:Midsem (W9→W9) | — | analyse-data, written-communication |  |
| project | 25.0 | A:ProjectDeliverable (W5→W12) | — | design, implement, evaluate-critique, oral-presentation |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 23.5%, CO2 23.5%, CO3 20.0%, CO4 15.5%, CO5 17.5%

## 10. Resource material

Policy: **mixed** — Because AI-assisted software development and Model Context Protocol integrations are rapidly evolving domains, a combination of established software engineering textbooks and recent research proceedings/papers is utilized.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Ian Sommerville (2005). *Software Engineering*. | 9780133943030 | yes | M3.T1 |
| reference | Stuart J. Russell, Peter Norvig (1994). *Artificial intelligence: A modern approach*. | 9781292472553 | yes | M1.T1 |
| reading | Maryam Khan, Muhammad Azeem Akbar, Jussi Kasurinen (2025). *Integrating Large Language Models in Software EngineeringEducation: A Pilot Study through GitHub Repositories Mining*. | 10.2139/ssrn.5547515 | yes | M1.T1 |
| reading | Reem Aleithan (2025). *Revisiting SWE-Bench: On the Importance of Data Quality for LLM-Based Code Models*. | 10.1109/icse-companion66252.2025.00075 | yes | M4.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 2 [2] | 1 [unclaimed] | 3 [3] |
| CO2 | 2 [unclaimed] | 2 [3] | 1 [unclaimed] | 3 [unclaimed] |
| CO3 |  | 3 [3] | 3 [unclaimed] |  |
| CO4 | 2 [3] | 2 [unclaimed] | 3 [unclaimed] | 2 [unclaimed] |
| CO5 |  | 3 [3] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO9: Configuring AI-assisted tools and workflows directly aligns with utilizing advanced techniques and tools in computing. (activities: tool-use, implement)
- CO1→PO4: Configuring developer workflows uses modern methodologies to support system implementation. (activities: implement, tool-use)
- CO2→PO4: Constructing integrations and application codebase features is a core system implementation task. (activities: implement, tool-use)
- CO3→PO4: Decomposing requirements into executable specifications represents the design phase of software development. (activities: design)
- CO4→PO3: Analyzing engineering workflows and test outputs requires evaluating and adapting problem-solving techniques. (activities: analyse-data)
- CO5→PO4: Assessing and justifying design decisions for a multi-module system directly evaluates application design. (activities: evaluate-critique, oral-presentation)
- CO5→PO7: Scenario walkthroughs and live demonstrations require effective oral presentation and communication. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1 |
| CO1.LO2 | L3 | M1.T2 | 1, 2 | A:Midsem@L3 |
| CO1.LO3 | L3 | M1.T3 | 2, 3 | A:PA1@L3 |
| CO2.LO1 | L2 | M2.T1 | 3, 4 | A:Quiz1@L2 |
| CO2.LO2 | L3 | M2.T2 | 4, 5 | A:Midsem@L3 |
| CO2.LO3 | L3 | M2.T3 | 5, 6 | A:PA2@L3 |
| CO3.LO1 | L1 | M3.T1 | 6 | A:DesignDoc@L1 |
| CO3.LO2 | L4 | M3.T2 | 7 | A:DesignDoc@L4 |
| CO3.LO3 | L4 | M3.T3 | 8 | A:DesignDoc@L4 |
| CO4.LO1 | L4 | M4.T1 | 9 | A:Midsem@L4 |
| CO4.LO2 | L4 | M4.T2 | 9, 10 | A:ProjectDeliverable@L4 |
| CO5.LO1 | L5 | M5.T1 | 10, 11 | A:ProjectDeliverable@L5 |
| CO5.LO2 | L5 | M5.T2, M5.T3 | 11, 12 | A:ProjectDeliverable@L5 |

## Appendix C — Modules and topics

**M1 AI-Assisted Coding and Developer Workflows** (primary CO1)
- M1.T1 AI-assisted coding and developer workflows overview — 2.0 h · LOs CO1.LO1
- M1.T2 Agent orchestration frameworks configuration — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Coding agents deployment and pipeline configuration — 3.0 h · LOs CO1.LO3 · requires M1.T2
**M2 Model Context Protocol and Tool Use APIs** (primary CO2)
- M2.T1 Model Context Protocol integrations and tool use APIs — 2.0 h · LOs CO2.LO1 · requires M1.T1
- M2.T2 Context engineering and agent skills construction — 3.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Advanced MCP codebase integration — 3.0 h · LOs CO2.LO3 · requires M2.T2
**M3 Requirements Engineering and Specification-Driven Development** (primary CO3)
- M3.T1 Requirements elicitation and use case identification — 2.0 h · LOs CO3.LO1
- M3.T2 Requirements to executable specifications decomposition — 3.0 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Comprehensive specification-driven development documentation — 3.0 h · LOs CO3.LO3 · requires M3.T2
**M4 Iterative Loop Engineering and Software Factories** (primary CO4)
- M4.T1 Iterative loop engineering workflows and trace log examination — 2.0 h · LOs CO4.LO1 · requires M3.T3
- M4.T2 Software factories and diagnostic evaluation — 3.0 h · LOs CO4.LO2 · requires M4.T1
**M5 System Assessment and Capstone Integration** (primary CO5)
- M5.T1 AI-native software development system evaluation planning — 2.0 h · LOs CO5.LO1 · requires M1.T3, M2.T3, M3.T3, M4.T2
- M5.T2 Emerging developer tools and capstone system demonstration — 2.0 h · LOs CO5.LO2 · requires M5.T1
- M5.T3 Capstone system demonstration and walkthrough — 2.0 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 35.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 focuses on broader research and mining techniques in software engineering using AI, whereas the new course centers directly on hands-on AI-native development workflows, agentic tool use, and loop engineering. |
| CSE581 | 0.034 | superficial | CSE581 covers traditional systems analysis and requirements engineering, whereas this course deals with spec-driven development and requirements translated for autonomous coding agents. |
| CSE582 | 0.067 | complementary | CSE582 addresses software product lines, evolution, and maintenance, while this course looks at modern software factories powered by AI coding agents. |
| CSE594A | 0.08 | complementary | CSE594A focuses generally on agentic reasoning for algorithmic and mathematical problem solving, whereas this course is specifically tailored to software engineering and coding workflows. |
| CSE201 | 0.017 | superficial | CSE201 teaches foundational advanced programming and unit testing in Java, while this course assumes those skills and builds automated testing and evaluation loops for AI agents. |
| AI501 | 0.034 | superficial | AI501 provides a rigorous foundational treatment of machine learning theory and algorithms, whereas this course applies AI tools and agents within software engineering workflows. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Research-oriented perspective on evaluating AI tools in software engineering. Avoid: Excessive focus on software repository mining instead of practical workflow automation.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Foundational concepts of agentic protocols and tool use. Avoid: Broad algorithmic problem solving without software engineering constraints.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation style and collaborative tool usage. Avoid: Solely relying on traditional open-source development models without AI coding agents.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| los | VLO-COPY | error | CO5.LO2, CO5 | CO5.LO2 restates its parent CO5 (token overlap 0.88); an LO must be a narrower, single-task step |
| los | VLO-DUP | error | CO1.LO2, CO1.LO3 | CO1.LO2 and CO1.LO3 are near-duplicates |
| assessment | VA-MIDSEM | warning | A:Midsem | mid-sem placed in week 9, calendar assumption is after week 7 (week 7 or 8) |
| assessment | VA-REG | warning | K07 | no endsem component although UGREG-2025§6.2 normally schedules one |
| cos | V11 | warning | CO4 | CO CO4 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO2 | LO CO2.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO3 | LO CO2.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO3 | LO CO3.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 9 → 2 · round 1 accepted (9→3); round 2 rejected (3→3); round 3 accepted (3→2)
- structure: errors 1 → 0 · round 1 accepted (1→0)
- assessment: errors 10 → 0 · round 1 accepted (10→1); round 2 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Special constraint SC1 notes a dependency ordering conflict where week 4 topics depend on week 8 topics.
- positioning: SC1: Special constraint SC1 states that topics in week 4 must depend on topics taught in week 8, which represents a chronological inversion that requires careful syllabus sequencing by the curriculum planner.
- constraints: SC1 temporal paradox: Special constraint SC1 states that week 4 topics depend on week 8 topics, creating a logical cycle or impossible chronological dependency.
- cos: SC1: Special constraint SC1 requires topics in week 4 to depend on topics only taught in week 8; this scheduling dependency must be managed carefully in the weekly syllabus plan.
- los: hours_total: Lecture hours total 34 instead of 39 due to granularity constraints across 13 LOs. Schedulers can distribute the remaining 5 hours across lecture sessions.
- structure: Special constraint K14 / SC1: Special constraint states topics in week 4 must require topics only taught in week 8, which contradicts standard pedagogical progression where fundamentals precede advanced loops. Handled by establishing clear DAG dependencies.
- resources: Candidate Pool Limitations: The retrieved external candidates and corpus resources lack specific dedicated textbooks on Model Context Protocol (MCP), agent orchestration, and modern specification-driven development, requiring reliance on general SE and AI literature supplemented by recent papers.
- narrative: SC1: Special constraint SC1 states that topics in week 4 must require/depend on topics that are only taught in week 8, which presents a logical dependency contradiction that cannot be resolved through standard sequencing.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress from foundational AI-assisted coding and agent configuration through protocol integration and specification-driven development to iterative loop engineering and capstone system assessment. This sequence builds directly upon the software development and unit testing fundamentals established in prerequisite CSE201.
- **assessment rationale:** The assessment mix comprises quizzes, assignments, design documents, midsem examinations, and a project. This combination effectively evaluates both theoretical understanding and practical competency across all cognitive levels, ranging from configuration and code construction to comprehensive system design and live evaluation.
- **positioning rationale:** Unlike CSE701 which focuses on broader research and mining techniques in software engineering using AI, or CSE581 which covers traditional requirements engineering, this course centers directly on hands-on AI-native development workflows, agentic tool use, and loop engineering.