# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-inv_assess_weights` · generated deterministically from the design graph · validator status: **5 errors, 3 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level indicated textually without a specific course code. | professor |
| — | CONFLICT ['special_constraints', 'assessment_prefs'] | — | The special constraints state assessment weights must sum to 130%, which contradicts standard institutional grading policies. | professor |
| — | CONFLICT ['K16'] | — | The professor specified that assessment weights must sum to 130%, which contradicts standard institutional grading norms where totals must sum to 100%. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. The curriculum addresses Model Context Protocol and developer tools, iterative human-agent coding loops and failure analysis, automated testing and code reliability evaluation using JUnit, and specification-driven development with context engineering. Target students are upper-level undergraduate students in the BTech Computer Science and Engineering programme who possess strong programming and software development fundamentals. Through lectures, tutorials, and practical laboratory sessions involving hands-on coding and project work, students learn to configure agentic workflows, analyze failure modes, evaluate code correctness, and justify context engineering strategies for complex software features.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students need solid software engineering fundamentals, unit testing, and programming capabilities to effectively evaluate and build agent-assisted software. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 (Topics in Software Engineering: AI in SE) touches upon AI applications in software engineering with an overlap of 0.185, it focuses on mining software repositories, defect prediction, and research literature review [CATALOGUE]. In contrast, the new course focuses on modern AI-native software development workflows, agentic tool use (MCP), and human-agent collaborative engineering [USER].

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure an agentic software development workflow using Model Context Protocol (MCP) and tool integrations, given a set of software requirements and a list of available developer tools, such that the configured agent successfully executes at least 80% of the specified tool calls without human intervention.** `[INFERRED, USER]`  
verb *configure* · behaviour *an agentic software development workflow using Model Context Protocol (MCP) and tool integrations* · condition *given a set of software requirements and a list of available developer tools* · degree *such that the configured agent successfully executes at least 80% of the specified tool calls without human intervention* · evidence: programming_assignment, lab_task · marks share (computed): 36.0%

- CO1.LO1 (L1) Identify available developer tools and Model Context Protocol specifications, given a system configuration document, listing all integration endpoints.
- CO1.LO2 (L3) Implement basic tool integration scripts using Model Context Protocol interfaces, given a set of developer tools, such that test tool calls return expected JSON payloads.
- CO1.LO3 (L3 ★capstone) Configure an agentic software development workflow using Model Context Protocol (MCP) components, given a specific set of software requirements and tool lists, such that setup scripts execute initialization without errors.
- CO1.LO4 (L3) Configure developer tools and Model Context Protocol integrations, given a tool list and a software configuration document, such that test tool calls return expected JSON payloads.

**CO2 (L4, procedural) — Analyze the performance and failure modes of an iterative human-agent coding loop, for a multi-file software modification task using a provided agent orchestration framework, identifying at least three distinct failure causes with supporting log evidence.** `[USER]`  
verb *analyze* · behaviour *the performance and failure modes of an iterative human-agent coding loop* · condition *for a multi-file software modification task using a provided agent orchestration framework* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: code_review, report · marks share (computed): 21.5%

- CO2.LO1 (L2) Trace execution logs from an iterative human-agent coding loop, for a multi-file modification task, identifying message sequences and state transitions.
- CO2.LO2 (L4 ★capstone) Analyze failure modes of an iterative human-agent coding loop, for a multi-file software modification task using a provided agent orchestration framework, identifying at least three distinct failure causes with supporting log evidence.

**CO3 (L5, procedural) — Evaluate the reliability and correctness of code generated by an AI coding agent, using automated test suites and evaluation frameworks built on top of JUnit, justifying each evaluation verdict against a predefined test coverage and functional correctness specification.** `[CATALOGUE, USER]`  
verb *evaluate* · behaviour *the reliability and correctness of code generated by an AI coding agent* · condition *using automated test suites and evaluation frameworks built on top of JUnit* · degree *justifying each evaluation verdict against a predefined test coverage and functional correctness specification* · evidence: project_deliverable, design_document · marks share (computed): 25.0%

- CO3.LO1 (L3) Execute automated test suites using JUnit on code generated by an AI coding agent, given a repository snapshot, producing a test execution report.
- CO3.LO2 (L5 ★capstone) Evaluate the correctness of code generated by an AI coding agent, using automated test suites built on top of JUnit, justifying each evaluation verdict against a predefined test coverage specification.

**CO4 (L5, conceptual) — Justify context engineering strategies and specification-driven development plans, for a complex software feature request given a legacy codebase, covering every use case in the supplied requirements document.** `[USER]`  
verb *justify* · behaviour *context engineering strategies and specification-driven development plans* · condition *for a complex software feature request given a legacy codebase* · degree *covering every use case in the supplied requirements document* · evidence: design_document, presentation · marks share (computed): 17.5%

- CO4.LO1 (L2) Describe context engineering strategies and specification-driven development approaches, given a software feature request, outlining key architectural boundaries.
- CO4.LO2 (L5 ★capstone) Justify context engineering strategies, for a complex software feature request given a legacy codebase, covering every use case in the supplied requirements document.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Developer tools and Model Context Protocol specifications overview (M1.T1)<br>MCP interfaces and basic tool integration scripting (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Identify developer tools and Model Context Protocol endpoints from sample configuration documents, in pairs. |  |
| 2 | MCP interfaces and basic tool integration scripting (M1.T2)<br>Additional developer tool configuration and integration validation (M1.T3) | CO1.LO2, CO1.LO4 | CO1 | Trace tool interface calls and verify JSON payload structures on sample integration scripts. |  |
| 3 | Additional developer tool configuration and integration validation (M1.T3)<br>Context engineering and agentic software development workflows (M1.T4) | CO1.LO3, CO1.LO4 | CO1 | Trace configuration parameters for agentic software workflows and validate initialization properties. | A:Quiz1 (quiz); A:Assign1 released |
| 4 | Context engineering and agentic software development workflows (M1.T4)<br>Iterative development and loop engineering message sequences (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Worked trace-diagnosis of message sequences and state transitions in iterative human-agent coding loops. | A:Assign1 due |
| 5 | Iterative development and loop engineering message sequences (M2.T1)<br>Software factories, code review, and failure mode analysis (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Analyze message sequences and state transition diagrams from multi-file modification tasks. | A:ProjM1 released |
| 6 | State transitions in iterative development loops (M2.T3)<br>Failure mode analysis using log evidence (M2.T4) | CO2.LO1, CO2.LO2 | CO2 | Review log evidence from coding loops to map state transitions and identify loop divergence causes. |  |
| 7 | Failure mode analysis using log evidence (M2.T4)<br>Automated testing and unit testing using JUnit (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Examine failure logs and map them to distinct failure modes using provided orchestration traces. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Evaluation frameworks, test coverage, and code correctness (M3.T2)<br>Unit testing using JUnit for AI-generated code (M3.T4) | CO3.LO1, CO3.LO2 | CO3 | Trace test execution reports from JUnit test suites run against AI-generated code repositories. | A:ProjM1 due; A:ProjM2 released |
| 9 | Unit testing using JUnit for AI-generated code (M3.T4)<br>Verification against functional correctness specifications (M3.T3) | CO3.LO1, CO3.LO2 | CO3 | Evaluate code correctness verdicts against predefined test coverage specifications in groups. |  |
| 10 | Spec-driven development and requirements engineering boundaries (M4.T1)<br>Requirements to executable specifications and code refactoring (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Describe context engineering strategies and sketch architectural boundaries for feature requests. |  |
| 11 | Requirements to executable specifications and code refactoring (M4.T2)<br>Architectural boundaries in specification-driven development (M4.T3) | CO4.LO1, CO4.LO2 | CO4 | Analyze architectural boundaries and specification-driven development constraints on case studies. |  |
| 12 | Legacy codebase refactoring strategies and justification (M4.T4) | CO4.LO2 | CO4 | Peer review of legacy codebase refactoring justifications against requirements documents. | A:ProjM2 due |
| 13 |  |  |  | Open Q&A and tutorial review of final project design documents. | A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Basic Tool Integration Scripting** — Implement basic tool integration scripts using Model Context Protocol interfaces such that test tool calls return expected JSON payloads. | CO1.LO2 | Student development machines, software development environments |
| 2 | **Developer Tool Configuration and Integration Validation** — Configure developer tools and Model Context Protocol integrations given a tool list and a software configuration document. | CO1.LO4, CO1.LO2 | Student development machines, software development environments |
| 3 | **Agentic Software Development Workflows Setup** — Configure an agentic software development workflow using Model Context Protocol components to execute initialization without errors. | CO1.LO3, CO1.LO4 | Student development machines, access to AI coding tools/APIs |
| 4 | **Context Engineering and Workflow Initialization** — Build and validate agentic workflow scripts and context initialization parameters. | CO1.LO3 | Student development machines, access to AI coding tools/APIs |
| 5 | **Software Factories and Failure Mode Analysis** — Analyze failure modes of an iterative human-agent coding loop using a provided agent orchestration framework. | CO2.LO2 | Student development machines, software development environments |
| 6 | **Log Evidence and Failure Mode Analysis** — Examine log evidence from coding loops to identify distinct failure causes with supporting data. | CO2.LO2 | Student development machines, software development environments |
| 7 | **Automated Testing Using JUnit** — Execute automated test suites using JUnit on code generated by an AI coding agent given a repository snapshot. | CO3.LO1 | Student development machines, software development environments |
| 8 | **Test Coverage and Evaluation Frameworks** — Evaluate the correctness of code generated by an AI coding agent using test suites built on top of JUnit. | CO3.LO2, CO3.LO1 | Student development machines, software development environments |
| 9 | **Verification Against Functional Specifications** — Perform verification of AI-generated code against functional correctness specifications using automated tests. | CO3.LO2, CO3.LO1 | Student development machines, software development environments |
| 10 | **Executable Specifications and Refactoring** — Translate software requirements into executable specifications and perform targeted code refactoring. | CO4.LO2 | Student development machines, software development environments |
| 11 | **Refactoring under Architectural Boundaries** — Refactor codebase sections while respecting architectural boundaries in specification-driven development. | CO4.LO2 | Student development machines, software development environments |
| 12 | **Legacy Codebase Refactoring Strategies** — Justify and implement legacy codebase refactoring strategies covering every use case in a supplied requirements document. | CO4.LO2 | Student development machines, software development environments |
| 13 | **Open Lab and Final Project Troubleshooting** — Perform final integration, debugging, and review of project deliverables with TA support. | CO4.LO2, CO3.LO2 | Student development machines, TA support |

Infrastructure: Student development machines (available); Access to AI coding tools/APIs (needs_confirmation); Software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3) | — | tool-use |  |
| assignment | 20.0 | A:Assign1 (W3→W4) | — | implement, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data |  |
| project | 30.0 | A:ProjM1 (W5→W8), A:ProjM2 (W8→W12) | — | implement, evaluate-critique, design, written-communication |  |
| endsem | 20.0 | A:Endsem (W13→W13) | — | analyse-data, design |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 36.0%, CO2 21.5%, CO3 25.0%, CO4 17.5%

## 10. Resource material

Policy: **mixed** — Because AI-native software engineering and Model Context Protocol tools are fast-moving domains, a combination of established software engineering principles (such as refactoring and design patterns), specialized reference books on agentic patterns, and recent research papers/framework documentation is utilized.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Agentic Design Patterns*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T4, M2.T1 |
| reading |  (2024). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M1.T1, M1.T2 |
| reference | Martin Fowler (1999). *Refactoring: Improving the Design of Existing Code*. | 9780201485677 | yes | M4.T2, M4.T4 |
| reading | Thomas Zimmermann (2024). *The Incredible Machine: Developer Productivity and the Impact of AI on Productivity (Keynote)*. | 10.1145/3663529.3674721 | yes | M3.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 1 [unclaimed] | 2 [3] |  | 3 [2] |
| CO2 | 3 [3] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] |
| CO3 | 2 [unclaimed] | 3 [3] | 3 [unclaimed] | 3 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring agentic workflows directly maps to implementing and utilizing modern development tools to build systems. (activities: implement, tool-use)
- CO1→PO9: Involves the application of advanced protocols like Model Context Protocol for tool integration. (activities: tool-use)
- CO2→PO3: Analyzing failure modes in iterative coding loops requires examining and adapting algorithmic and systemic approaches. (activities: analyse-data)
- CO3→PO4: Evaluating code correctness using automated test suites aligns directly with system evaluation methodologies. (activities: evaluate-critique)
- CO4→PO4: Specification-driven development plans form a core part of software system design. (activities: design, written-communication)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1, A:Midsem@L1 |
| CO1.LO2 | L3 | M1.T2 | 1, 2 | A:Assign1@L3 |
| CO1.LO3 | L3 | M1.T4 | 3, 4 | A:Assign1@L3 |
| CO2.LO1 | L2 | M2.T1, M2.T3 | 4, 5, 6 | A:Midsem@L2 |
| CO2.LO2 | L4 | M2.T2, M2.T4 | 5, 6, 7 | A:Midsem@L4, A:ProjM1@L4 |
| CO3.LO1 | L3 | M3.T1, M3.T4 | 7, 8, 9 | A:ProjM1@L3, A:Endsem@L3 |
| CO3.LO2 | L5 | M3.T2, M3.T3 | 8, 9 | A:ProjM2@L5 |
| CO4.LO1 | L2 | M4.T1, M4.T3 | 10, 11 | A:Endsem@L2 |
| CO4.LO2 | L5 | M4.T2, M4.T4 | 10, 11, 12 | A:ProjM2@L5 |
| CO1.LO4 | L3 | M1.T3 | 2, 3 | A:Assign1@L3 |

## Appendix C — Modules and topics

**M1 Model Context Protocol and Developer Tools** (primary CO1)
- M1.T1 Developer tools and Model Context Protocol specifications overview — 2.0 h · LOs CO1.LO1
- M1.T2 MCP interfaces and basic tool integration scripting — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Additional developer tool configuration and integration validation — 3.0 h · LOs CO1.LO4 · requires M1.T2
- M1.T4 Context engineering and agentic software development workflows — 3.0 h · LOs CO1.LO3 · requires M1.T3
**M2 Iterative Human-Agent Coding Loops and Failure Analysis** (primary CO2)
- M2.T1 Iterative development and loop engineering message sequences — 2.0 h · LOs CO2.LO1 · requires M1.T4
- M2.T2 Software factories, code review, and failure mode analysis — 2.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 State transitions in iterative development loops — 2.0 h · LOs CO2.LO1 · requires M2.T1
- M2.T4 Failure mode analysis using log evidence — 2.0 h · LOs CO2.LO2 · requires M2.T2
**M3 Automated Testing and Code Reliability Evaluation** (primary CO3)
- M3.T1 Automated testing and unit testing using JUnit — 2.0 h · LOs CO3.LO1 · requires M2.T2
- M3.T2 Evaluation frameworks, test coverage, and code correctness — 2.0 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Verification against functional correctness specifications — 2.0 h · LOs CO3.LO2 · requires M3.T2
- M3.T4 Unit testing using JUnit for AI-generated code — 2.0 h · LOs CO3.LO1 · requires M3.T1
**M4 Specification-Driven Development and Context Engineering** (primary CO4)
- M4.T1 Spec-driven development and requirements engineering boundaries — 2.0 h · LOs CO4.LO1 · requires M3.T2
- M4.T2 Requirements to executable specifications and code refactoring — 2.0 h · LOs CO4.LO2 · requires M4.T1
- M4.T3 Architectural boundaries in specification-driven development — 2.0 h · LOs CO4.LO1 · requires M4.T1
- M4.T4 Legacy codebase refactoring strategies and justification — 2.0 h · LOs CO4.LO2 · requires M4.T2

Schedule: feasible · 35.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 investigates data-driven and machine learning techniques for software engineering research and post-hoc analysis [CATALOGUE], whereas the new course focuses on active, real-time agentic workflows, coding agents, and context engineering during software construction [USER]. |
| CSE594A | 0.08 | complementary | CSE594A focuses primarily on agentic reasoning for algorithmic, mathematical, and scientific problem-solving [CATALOGUE], whereas the new course specializes specifically in software development engineering processes, workflows, and developer tools [USER]. |
| CSE582 | 0.067 | superficial | CSE582 covers traditional software product lines, maintenance, and re-engineering [CATALOGUE], sharing only high-level terminology with the new course's modern AI software factory concepts [USER]. |
| AI501 | 0.034 | superficial | AI501 is a foundational course covering core machine learning theory and risk minimization [CATALOGUE], whereas the new course applies existing models and agents to software development workflows [USER]. |
| CSE581 | 0.034 | superficial | CSE581 deals with traditional systems analysis, design, and human cognitive limitations [CATALOGUE], whereas the new course examines spec-driven development using AI coding agents [USER]. |
| CSE201 | 0.017 | superficial | CSE201 teaches object-oriented programming fundamentals and JUnit testing in Java [CATALOGUE], serving as a foundational programming prerequisite rather than overlapping in content [USER]. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Literature review structure and advanced software engineering research framing Avoid: Heavy focus on repository mining and offline data analytics rather than active workflow integration
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Foundational concepts of agentic protocols such as MCP and tool use Avoid: Over-emphasis on algorithmic and mathematical problem solving instead of software engineering applications
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation structure and practical tooling focus Avoid: Traditional open-source community process focus without AI agent integration

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| los | VLO-COPY | error | CO2.LO2, CO2 | CO2.LO2 restates its parent CO2 (token overlap 0.90); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO3.LO2, CO3 | CO3.LO2 restates its parent CO3 (token overlap 0.85); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO4.LO2, CO4 | CO4.LO2 restates its parent CO4 (token overlap 0.80); an LO must be a narrower, single-task step |
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Agentic Design Patterns' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 degree is not visible in the statement text |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- los: errors 5 → 3 · round 1 rejected (5→2); round 2 accepted (5→3); round 3 rejected (3→3)
- structure: errors 4 → 0 · round 1 accepted (4→3); round 2 accepted (3→0)
- assessment: errors 2 → 0 · round 1 accepted (2→1); round 2 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Special constraint requires assessment weights to sum to 130%, which violates normal grading norms.
- positioning: SC1: Assessment weights sum to 130% as stated in special constraints, which deviates from the standard 100% institutional norm.
- constraints: Assessment weight sum: Special constraint SC1 states assessment weights must sum to 130%, which requires resolution during Gate 1.
- los: hours_total: Calculated total hours (32L, 11T, 21P) fall slightly below the nominal budget (39L, 13T, 26P) due to granular breakdown across 9 LOs; remaining hours are allocated dynamically for buffer and project milestones.
- assessment: CO attainment distribution: CO4 has lower direct weight representation compared to CO1 and CO3 due to project integration.
- narrative: assessment_weights: The assessment component weights sum to 100% in the approved graph summary, whereas the CCO special constraints note a sum of 130%; the proposal uses the 100% distribution from the graph summary.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules follow a structured progression starting with foundational developer tools and the Model Context Protocol in Module 1, moving into iterative human-agent coding loops and failure analysis in Module 2, proceeding to automated testing and reliability evaluation in Module 3, and culminating in specification-driven development and context engineering in Module 4. This sequencing builds directly upon the software engineering fundamentals and unit testing prerequisite knowledge from course CSE201.
- **assessment rationale:** The assessment mix comprises quizzes (10%), assignments (20%), a mid-semester examination (20%), a major project (30%), and an end-semester examination (20%). This balanced distribution aligns directly with the course outcomes, combining theoretical analysis and performance evaluation with practical, hands-on project work that tests real-world workflow configuration and coding agent reliability.
- **positioning rationale:** This course is distinct from existing IIIT-Delhi courses. Unlike CSE701 which focuses on data-driven and machine learning techniques for software engineering research, or CSE594A which emphasizes agentic reasoning for scientific problem-solving, this course specializes specifically in software development engineering processes, workflows, and developer tools. It also differs from traditional software engineering courses like CSE201 and CSE582 by focusing on modern AI-native agent-assisted software construction rather than classical object-oriented programming or product lines.