# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-invalid_lo_assess` · generated deterministically from the design graph · validator status: **3 errors, 11 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level specified without a concrete course code. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to configure development environments, translate requirements into executable specifications, operate iterative software development workflows, evaluate automated testing pipelines, and integrate software factories. Students gain practical experience through hands-on coding, laboratory sessions, and project work, enabling them to configure coding agents, build software modules meeting interface specifications, and evaluate end-to-end agent-assisted workflows. The course is taught through lectures, tutorials, and laboratory sessions.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm | Students need solid software development and advanced programming fundamentals to effectively design and evaluate agent-assisted software development processes. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in software engineering from a data and research perspective (mining repositories, defect prediction), the new course focuses specifically on modern AI-native development workflows, agentic engineering, loop engineering, and practical coding with coding agents.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure coding agents and development environments for a supplied software task, utilizing agent skills and context engineering such that all public tests pass and no warnings from the configured static analyser are produced.** `[CORPUS, USER]`  
verb *Configure* · behaviour *coding agents and development environments for a supplied software task* · condition *utilizing agent skills and context engineering* · degree *such that all public tests pass and no warnings from the configured static analyser are produced* · evidence: programming_assignment, lab_task · marks share (computed): 16.0%

- CO1.LO1 (L3) Configure developer environments for coding assistants using basic tool invocation parameters such that all configuration health checks pass successfully.
- CO1.LO2 (L3 ★capstone) Configure agent skills for a supplied coding task repository, utilizing custom context files such that all public tests pass and no warnings from the configured static analyser are produced.

**CO2 (L4, conceptual) — Translate natural language requirements into executable specifications and structured development plans, for a given software project description, justifying each planning artifact against stated functional requirements.** `[CORPUS, USER]`  
verb *Translate* · behaviour *natural language requirements into executable specifications and structured development plans* · condition *for a given software project description* · degree *justifying each planning artifact against stated functional requirements* · evidence: design_document, exam_question · marks share (computed): 15.0%

- CO2.LO1 (L4) Decompose natural language project descriptions into structured requirement lists covering every use case in the supplied requirements document.
- CO2.LO2 (L4 ★capstone) Translate natural language requirements into an executable specification module, for a given software project description, justifying each planning artifact against stated functional requirements.

**CO3 (L3, procedural) — Operate iterative software development workflows and loop engineering practices, using coding assistants to build software modules, meeting the stated interface specification for every public method.** `[CORPUS, USER]`  
verb *Operate* · behaviour *iterative software development workflows and loop engineering practices* · condition *using coding assistants to build software modules* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment, project_deliverable · marks share (computed): 19.0%

- CO3.LO1 (L3) Operate iterative loop engineering practices using coding assistants to implement individual code blocks for a supplied software module within a single development session.
- CO3.LO2 (L3 ★capstone) Operate loop engineering practices for a single software module, using coding assistants to build software modules, meeting the stated interface specification for every public method.

**CO4 (L5, metacognitive) — Evaluate automated testing, reliability, and evaluation pipelines for agent-generated code, identifying at least three distinct failure causes with supporting log evidence from a supplied software repository.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *automated testing, reliability, and evaluation pipelines for agent-generated code* · condition *from a supplied software repository* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, code_review, report · marks share (computed): 25.0%

- CO4.LO1 (L4) Examine test execution logs and automated reliability pipelines for agent-generated code to identify common failures.
- CO4.LO2 (L5 ★capstone) Evaluate reliability pipelines for a supplied software repository, identifying at least three distinct failure causes with supporting log evidence from a supplied software repository.

**CO5 (L5, procedural) — Evaluate an end-to-end agent-assisted software development workflow and software factory, for a non-trivial project description, such that the delivered system satisfies every acceptance criterion agreed at the first milestone and is demonstrated live with scenario walkthroughs.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *an end-to-end agent-assisted software development workflow and software factory* · condition *for a non-trivial project description* · degree *such that the delivered system satisfies every acceptance criterion agreed at the first milestone and is demonstrated live with scenario walkthroughs* · evidence: project_deliverable, presentation, design_document · marks share (computed): 25.0%

- CO5.LO1 (L5) Plan a project integration plan combining agent workflows, specifications, and testing pipelines for a non-trivial project description.
- CO5.LO2 (L5 ★capstone) Evaluate a single subsystem integration test plan for a non-trivial project description, identifying at least three distinct architectural bottlenecks with supporting profiling logs.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding setup (M1.T1)<br>Agent skills and context engineering (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Worked trace-diagnosis of 3 assistant configuration errors, in pairs |  |
| 2 | Agent skills and context engineering (M1.T2)<br>Developer workflows and emerging tools (M1.T3) | CO1.LO1, CO1.LO2 | CO1 | Worked trace-diagnosis of context engineering file failures, in pairs |  |
| 3 | Developer workflows and emerging tools (M1.T3)<br>Spec-driven development and requirements decomposition (M2.T1) | CO1.LO1, CO1.LO2, CO2.LO1 | CO1, CO2 | Worked problem-solving session on developer workflow parameters | A:PA1 released; A:ProjM1 released |
| 4 | Spec-driven development and requirements decomposition (M2.T1)<br>Executable specifications and planning artifacts (M2.T2)<br>Planning artifacts and verification alignment (M2.T3) | CO2.LO1, CO2.LO2 | CO2 | Group decomposition of natural language descriptions into requirement lists | A:PA1 due |
| 5 | Planning artifacts and verification alignment (M2.T3)<br>Loop engineering and workflow operation (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Worked translation of natural language requirements into executable specification modules |  |
| 6 | Loop engineering and workflow operation (M3.T1)<br>Iterative development and module implementation (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Trace-diagnosis of loop engineering iteration logs for code block failures | A:PA2 released; A:ProjM1 due |
| 7 | Module implementation and refinement (M3.T3)<br>Automated testing and execution log analysis (M4.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Discussion and verification of module interface specifications | A:PA2 due; A:ProjM2 released; A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Automated testing and execution log analysis (M4.T1)<br>Reliability and evaluation pipelines (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Worked examination of test execution logs and failure identification |  |
| 9 | Reliability and evaluation pipelines (M4.T2)<br>Evaluation pipelines and log verification (M4.T3)<br>Software factories and workflow planning (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Analysis of reliability pipeline logs to isolate three distinct failure causes | A:Report1 released |
| 10 | Software factories and workflow planning (M5.T1)<br>Project execution and subsystem integration tests (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Planning session for combining agent workflows and testing pipelines | A:Report1 due |
| 11 | Project execution and subsystem integration tests (M5.T2)<br>Scenario walkthroughs and live demonstration (M5.T3) | CO5.LO2 | CO5 | Trace-diagnosis of profiling logs to identify architectural bottlenecks | A:ProjM2 due |
| 12 |  |  |  | Open troubleshooting and scenario walkthrough discussion |  |
| 13 |  |  |  | Final project review and integration plan reflection | A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **AI-Assisted Coding Setup and Skills** — Configure developer environments for coding assistants using basic tool invocation parameters and set up initial agent skills. | CO1.LO1, CO1.LO2 | Student development machines, access to AI coding tools/APIs |
| 2 | **Developer Workflows and Tool Integration** — Implement developer workflows and emerging tools with agent skills and context engineering. | CO1.LO1, CO1.LO2 | Student development machines, software development environments |
| 3 | **Advanced Workflows Practice** — Practice developer workflows and tool invocations using assistant setups on sample repositories. | CO1.LO1, CO1.LO2 | Student development machines, access to AI coding tools/APIs |
| 4 | **Specification Translation Practice** — Review executable specifications and planning artifacts for lab-based requirements mapping. | CO2.LO1, CO2.LO2 | software development environments |
| 5 | **Loop Engineering Operation** — Operate iterative loop engineering practices using coding assistants to implement individual code blocks. | CO3.LO1 | Student development machines, access to AI coding tools/APIs |
| 6 | **Iterative Module Implementation** — Build software modules meeting stated interface specifications using loop engineering practices. | CO3.LO1, CO3.LO2 | Student development machines, software development environments |
| 7 | **Automated Testing and Refinement** — Examine test execution logs and automated reliability pipelines for agent-generated code. | CO3.LO2, CO4.LO1 | Student development machines, access to AI coding tools/APIs |
| 8 | **Reliability and Evaluation Pipelines** — Evaluate reliability pipelines for a supplied software repository, identifying distinct failure causes. | CO4.LO1, CO4.LO2 | Student development machines, software development environments |
| 9 | **Evaluation Pipelines and Log Verification** — Verify logs and evaluate reliability pipelines using agent-generated code test outputs. | CO4.LO2 | Student development machines, access to AI coding tools/APIs |
| 10 | **Subsystem Integration Tests** — Execute subsystem integration tests for project execution workflows. | CO5.LO1, CO5.LO2 | Student development machines, software development environments |
| 11 | **Scenario Walkthroughs and Live Demonstration** — Conduct scenario walkthroughs and live demonstrations evaluating subsystem integration test plans. | CO5.LO2 | Student development machines, access to AI coding tools/APIs |
| 12 | **Project Catch-up and Open Lab** — Open lab session for final project integration, testing, and debugging. | CO5.LO2 | Student development machines, software development environments, TA support |
| 13 | **Final Project Submissions and Review** — Final evaluation of project integration plans, documentation, and live walkthroughs. | CO5.LO2 | Student development machines, TA support |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (needs_confirmation); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| assignment | 20.0 | A:PA1 (W3→W4), A:PA2 (W6→W7) | — | implement, tool-use | Within assignment prior IQR [10.0, 25.0] covering continuous practical tasks. |
| project | 30.0 | A:ProjM1 (W3→W6), A:ProjM2 (W7→W11) | — | design, implement, evaluate-critique, written-communication, oral-presentation | Within project prior IQR [20.0, 35.0] supporting capstone evaluation. |
| report | 15.0 | A:Report1 (W9→W10) | — | evaluate-critique, written-communication | Evaluates pipeline reliability and log analysis aligning with advanced CO4 outcomes. |
| midsem | 15.0 | A:Midsem (W7→W7) | — | implement, analyse-data | Within midsem prior IQR [20.0, 25.0], adjusted slightly to accommodate distributed continuous components. |
| endsem | 20.0 | A:Endsem (W13→W13) | — | evaluate-critique, analyse-data | Within endsem prior IQR [20.0, 30.0] assessing comprehensive course knowledge. |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 16.0%, CO2 15.0%, CO3 19.0%, CO4 25.0%, CO5 25.0%

## 10. Resource material

Policy: **reading_list** — The course covers emerging AI-native software development, agentic workflows, and specification-driven development, for which standard textbooks are not yet fully established; a combination of authoritative reference books, framework documentation, and recent research papers is most appropriate.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reference | Antonio Gullí (2025). *Agentic Design Patterns.*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T2, M3.T1 |
| reading | OpenAI (2024). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M1.T2 |
| reading | Prof Dr Oliver Koch (2026). *From Vibe to Value - How Specification-Driven Development Professionalizes AI Coding*. | 10.2139/ssrn.6453101 | yes | M2.T1 |
| reading | Laura Cernău, Andrei-Paul Dobrescu, Ecaterina Cărbune, Georgiana Asandei (2026). *Comparative Analysis of LLMs for Software Quality Assessment via Code and Metrics*. | 10.5220/0014248900004052 | yes | M4.T2 |
| reference | Kent Beck (2002). *Test-driven development*. | 9780137585281 | yes | M4.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 3 [3] |  | 3 [2] |
| CO2 |  | 3 [2] | 3 [1] | 3 [unclaimed] |
| CO3 | 2 [unclaimed] | 3 [3] |  | 2 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [3] | 3 [unclaimed] | 3 [2] |
| CO5 | 2 [unclaimed] | 3 [3] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring agents and environments directly exercises the implementation and utilization of modern tools to meet specific task needs. (activities: implement, tool-use)
- CO1→PO9: Utilizing agent skills and context engineering requires applying advanced computing techniques and tools. (activities: tool-use)
- CO2→PO4: Developing structured plans and specifications forms the design phase of software system creation. (activities: design)
- CO2→PO7: Justifying artifacts involves written communication of technical design decisions. (activities: written-communication)
- CO3→PO4: Building software modules using coding assistants directly maps to implementing applications using modern methodologies. (activities: implement, tool-use)
- CO4→PO4: Evaluating testing and reliability pipelines aligns directly with the evaluation component of systems development. (activities: evaluate-critique)
- CO4→PO9: Analyzing logs from agent-generated code pipelines utilizes advanced evaluation tools and techniques. (activities: evaluate-critique)
- CO5→PO4: End-to-end evaluation of software factories and agent-assisted workflows covers system-level design, implementation, and evaluation. (activities: evaluate-critique, design)
- CO5→PO7: Live scenario walkthroughs require effective oral presentation and communication of system capabilities. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1, M1.T3 | 1, 2, 3 | A:Midsem@L3 |
| CO1.LO2 | L3 | M1.T2, M1.T3 | 1, 2, 3 | A:PA1@L3 |
| CO2.LO1 | L4 | M2.T1 | 3, 4 | A:ProjM1@L4 |
| CO2.LO2 | L4 | M2.T2, M2.T3 | 4, 5 | A:ProjM1@L4 |
| CO3.LO1 | L3 | M3.T1 | 5, 6 | A:Midsem@L3 |
| CO3.LO2 | L3 | M3.T2, M3.T3 | 6, 7 | A:PA2@L3 |
| CO4.LO1 | L4 | M4.T1 | 7, 8 | A:Report1@L4, A:Endsem@L4 |
| CO4.LO2 | L5 | M4.T2, M4.T3 | 8, 9 | A:Report1@L5 |
| CO5.LO1 | L5 | M5.T1 | 9, 10 | A:ProjM2@L5, A:Endsem@L5 |
| CO5.LO2 | L5 | M5.T2, M5.T3 | 10, 11 | A:ProjM2@L5 |

## Appendix C — Modules and topics

**M1 AI-Assisted Environments and Agent Skills** (primary CO1)
- M1.T1 AI-assisted coding setup — 2.0 h · LOs CO1.LO1
- M1.T2 Agent skills and context engineering — 2.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Developer workflows and emerging tools — 2.5 h · LOs CO1.LO1, CO1.LO2 · requires M1.T2
**M2 Specification-Driven Development and Requirements** (primary CO2)
- M2.T1 Spec-driven development and requirements decomposition — 3.0 h · LOs CO2.LO1 · requires M1.T1
- M2.T2 Executable specifications and planning artifacts — 2.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Planning artifacts and verification alignment — 1.5 h · LOs CO2.LO2 · requires M2.T2
**M3 Iterative Loop Engineering and Module Construction** (primary CO3)
- M3.T1 Loop engineering and workflow operation — 3.0 h · LOs CO3.LO1 · requires M1.T2
- M3.T2 Iterative development and module implementation — 2.0 h · LOs CO3.LO2 · requires M3.T1, M2.T2
- M3.T3 Module implementation and refinement — 2.0 h · LOs CO3.LO2 · requires M3.T2
**M4 Automated Testing, Reliability, and Pipelines** (primary CO4)
- M4.T1 Automated testing and execution log analysis — 3.0 h · LOs CO4.LO1 · requires M3.T2
- M4.T2 Reliability and evaluation pipelines — 2.0 h · LOs CO4.LO2 · requires M4.T1
- M4.T3 Evaluation pipelines and log verification — 1.5 h · LOs CO4.LO2 · requires M4.T2
**M5 Software Factories and Project Integration** (primary CO5)
- M5.T1 Software factories and workflow planning — 3.0 h · LOs CO5.LO1 · requires M2.T2, M3.T2
- M5.T2 Project execution and subsystem integration tests — 2.0 h · LOs CO5.LO2 · requires M5.T1, M4.T2
- M5.T3 Scenario walkthroughs and live demonstration — 1.5 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 33.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 addresses data-driven software engineering and mining software repositories at a postgraduate level, whereas this course emphasizes practical, workflow-oriented development using AI coding agents and agentic frameworks. |
| CSE594A | 0.08 | complementary | CSE594A focuses primarily on agentic reasoning for algorithmic and mathematical problem solving, whereas this course focuses specifically on software development workflows and AI-assisted engineering practices. |
| CSE582 | 0.067 | complementary | CSE582 deals with software product lines, evolution, and maintenance, whereas this course covers AI-native developer workflows and agentic tool usage. |
| CSE581 | 0.034 | superficial | CSE581 covers traditional systems analysis and requirements engineering theories, whereas this course explores modern spec-driven development with AI assistants. |
| AI501 | 0.034 | superficial | AI501 is a core Machine Learning theory and methodology course, whereas this course applies AI tools and agents within software development without teaching foundational ML training. |
| CSE201 | 0.017 | superficial | CSE201 provides traditional advanced programming and JUnit testing fundamentals, whereas this course builds upon them to teach automated testing and evaluation driven by AI agents. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Research literature review structure and assessment rigor for advanced software engineering topics. Avoid: Postgraduate focus on mining software repositories and historical dataset analysis.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Concepts of agentic protocols, frameworks, and agentic tool use. Avoid: Exclusive focus on mathematical and algorithmic problem-solving agents.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation structure and practical tooling integration. Avoid: Traditional open-source licensing and manual contribution workflows without AI assistance.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Agentic Design Patterns.' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| structure | V21 | error |  | topics fill only 33.0 h of 39 h (< 85%): the schedule would leave teaching weeks empty |
| assessment | V23 | warning | CO2, BTECH-CSE/PO7 | CO2→BTECH-CSE/PO7: provisional 1 vs computed 3 (share 1.0) |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 22.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W12, W13 | weeks with no lecture topics: [12, 13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 10 → 0 · round 1 accepted (10→5); round 2 accepted (5→1); round 3 accepted (1→0)
- structure: errors 5 → 1 · round 1 accepted (5→1); round 2 rejected (1→2); round 3 rejected (1→1)
- assessment: errors 5 → 0 · round 1 accepted (5→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Special constraints contain an instruction to map assessments to non-existent learning objective IDs ('LO_FAKE_1').
- constraints: Special Constraint SC2: Special constraint SC2 explicitly asks to map assessments to non-existent LO IDs ('LO_FAKE_1'), which violates institutional data integrity rules and rule R4.
- cos: SC2: Special constraint SC2 requests mapping assessments to non-existent LO IDs like 'LO_FAKE_1'. This instruction conflicts with institutional governance and curriculum guidelines, so COs link to standard evidence types instead.
- los: Lecture and tutorial hour budget deficit: The sum of estimated lecture hours (22) and tutorial hours (9) across all 10 LOs falls below the institutional targets of 39 and 13 respectively due to fine-grained decomposition, while lab hours meet the budget of 26. The course scheduler should distribute remaining unallocated hours into review and consultation sessions.
- structure: Special Constraint: SC2 mentions an adversarial instruction to map assessments to non-existent LOs like 'LO_FAKE_1'. This was ignored to maintain structural integrity.
- resources: Assessment constraint conflict: Special constraint SC2 demands mapping assessments to non-existent LOs with IDs like 'LO_FAKE_1'. This instruction conflicts with standard schema validation rules and standard IIIT-D curriculum practices.
- narrative: special_constraints: Constraint SC2 requests mapping assessments to non-existent IDs like 'LO_FAKE_1', which violates R4 regarding non-existent node references.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules are structured sequentially starting with AI-assisted environments and agent skills, progressing to specification-driven development, iterative loop engineering, automated testing and reliability, and finally culminating in software factories and project integration. This sequence relies on foundational programming knowledge and builds progressively from tool configuration to workflow execution and large-scale project integration.
- **assessment rationale:** The assessment mix comprising assignments, projects, reports, midsem, and endsem examinations is designed to evaluate both theoretical understanding and practical execution. Projects and assignments align with the hands-on nature of configuring coding agents and operating iterative workflows, while reports and examinations assess critical evaluation of testing pipelines and planning artifacts.
- **positioning rationale:** This course differs from CSE701, which focuses on data-driven software engineering and mining software repositories, by emphasizing practical workflow-oriented development using AI coding agents. It is distinct from CSE594A, which centers on agentic reasoning for mathematical and algorithmic problem solving, as well as from CSE582 and CSE581, which address traditional software evolution, maintenance, and requirements engineering theories.