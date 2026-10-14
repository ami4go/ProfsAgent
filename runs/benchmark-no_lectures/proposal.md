# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-no_lectures` · generated deterministically from the design graph · validator status: **1 errors, 15 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level specified without a specific course code. | professor |
| — | CONFLICT ['K17', 'UGREG-2025§4(2)a'] | — | The professor's special constraint requires 0 lecture hours (K17), whereas UGREG-2025§4(2)a specifies that a 4-credit course will have 3 hours of lectures per week. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. The course matters for target students by equipping them with engineering practices required for AI-assisted environments. Upon completing the course, students will be able to configure agent-assisted coding environments using custom skills and model context protocols, construct executable specifications from natural language requirements, deconstruct software development loops into iterative workflows, evaluate the reliability and performance of AI-generated codebases using automated testing, and evaluate an end-to-end AI-native software development factory. The course is taught through lectures, tutorials, and laboratory sessions.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm, Collection framework | Students require strong programming and software engineering fundamentals to effectively evaluate, test, and build software using coding agents. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in Software Engineering with an overlap of 0.185, it focuses primarily on data mining, defect prediction, and research literature review rather than modern AI-native agentic software development, loop engineering, and context engineering.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure an agent-assisted coding environment using custom skills and model context protocols, for a provided software repository, meeting the stated interface specification for every public method.** `[CORPUS, USER]`  
verb *Configure* · behaviour *an agent-assisted coding environment using custom skills and model context protocols* · condition *for a provided software repository* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment, lab_task · marks share (computed): 22.5%

- CO1.LO1 (L1) Identify the basic configuration parameters and protocol endpoints required for an agent-assisted coding environment
- CO1.LO2 (L3) Implement custom skills and model context protocols using provided development tools
- CO1.LO3 (L3 ★capstone) Configure custom skills and model context protocols, for a provided software repository, meeting the stated interface specification for every public method.

**CO2 (L3, procedural) — Construct executable specifications from natural language requirements, using spec-driven development tools, such that all acceptance tests pass.** `[CORPUS, USER]`  
verb *Construct* · behaviour *executable specifications* · condition *using spec-driven development tools from natural language requirements* · degree *such that all acceptance tests pass* · evidence: programming_assignment, design_document · marks share (computed): 12.5%

- CO2.LO1 (L2) Translate natural language requirements into structured textual specifications
- CO2.LO2 (L3 ★capstone) Construct executable specifications for a supplied REST API module, using spec-driven development tools, such that all acceptance tests pass.

**CO3 (L4, conceptual) — Deconstruct software development loops into iterative workflows, for a supplied project brief, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *Deconstruct* · behaviour *software development loops into iterative workflows* · condition *for a supplied project brief* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, report · marks share (computed): 20.0%

- CO3.LO1 (L4) Examine software development loops to isolate repetitive workflow phases
- CO3.LO2 (L4 ★capstone) Deconstruct software development loops into iterative workflows, for a supplied project brief, identifying at least three distinct failure causes, each supported by evidence from the report.

**CO4 (L5, metacognitive) — Evaluate the reliability and performance of AI-generated codebases, using automated testing and evaluation frameworks, justifying each validation choice against stated requirements.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *the reliability and performance of AI-generated codebases* · condition *using automated testing and evaluation frameworks* · degree *justifying each validation choice against stated requirements* · evidence: design_document, code_review · marks share (computed): 22.5%

- CO4.LO1 (L3) Execute automated testing frameworks on AI-generated codebases to gather performance and reliability metrics
- CO4.LO2 (L5 ★capstone) Evaluate the reliability and performance of AI-generated codebases, using automated testing and evaluation frameworks, justifying each design decision against at least one stated requirement.

**CO5 (L5, procedural) — Evaluate an end-to-end AI-native software development factory, for a complex real-world application domain, demonstrated live with three scenario walkthroughs chosen by the evaluator.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *an end-to-end AI-native software development factory* · condition *for a complex real-world application domain* · degree *demonstrated live, with 3 scenario walkthroughs chosen by the evaluator* · evidence: project_deliverable, presentation · marks share (computed): 22.5%

- CO5.LO1 (L5) Evaluate agent workflows, context engineering, and automated testing, for a complex real-world application domain, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.
- CO5.LO2 (L5 ★capstone) Evaluate an end-to-end AI-native software development factory, for a supplied e-commerce domain microservice, demonstrated live, with 3 scenario walkthroughs chosen by the evaluator.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Coding agents configuration parameters and protocol endpoints (M1.T1)<br>Custom skills and model context protocols implementation (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Trace configuration parameters of 2 sample coding agent endpoints in pairs and verify endpoint reachability. |  |
| 2 | Custom skills and model context protocols implementation (M1.T2)<br>Model context protocol environment configuration and verification (M1.T3) | CO1.LO2, CO1.LO3 | CO1 | Review and debug custom skill interface declarations against provided specifications in small groups. |  |
| 3 | Model context protocol environment configuration and verification (M1.T3)<br>Spec-driven development and requirements translation (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Troubleshoot model context protocol configuration errors on sample repository setups. | A:Quiz1 (quiz) |
| 4 | Spec-driven development and requirements translation (M2.T1)<br>Executable specifications for REST API modules (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Translate 3 complex natural language user stories into structured textual specifications, peer-reviewing outputs. | A:Assignment1 released |
| 5 | Executable specifications for REST API modules (M2.T2)<br>Loop engineering and workflow phase isolation (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Critique and refine textual specifications into machine-readable format for REST API modules. | A:Assignment1 due; A:Assignment2 released |
| 6 | Iterative development and failure cause deconstruction (M3.T2) | CO3.LO2 | CO3 | Examine software development loop diagrams to isolate redundant workflow phases and bottlenecks. | A:Assignment2 due |
| 7 | Automated testing frameworks for AI-generated codebases (M4.T1)<br>Reliability and performance evaluation frameworks (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Mid-sem review and analysis of automated testing output logs from sample AI codebases. | A:Midsem (midsem); A:ProjectMilestone1 released |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Reliability and performance evaluation frameworks (M4.T2)<br>Project discussion and agent workflow integration (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Evaluate performance metrics trade-offs for 2 competing AI-generated codebases in groups. | A:ProjectFinal released |
| 9 | Project discussion and agent workflow integration (M5.T1)<br>Hands-on coding and software factories deployment (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Walk through milestone requirements and agent workflow integration plans for course projects. | A:ProjectMilestone1 due |
| 10 | Hands-on coding and software factories deployment (M5.T2) | CO5.LO2 | CO5 | Conduct peer simulations of scenario walkthroughs for the e-commerce domain microservice project. |  |
| 11 |  |  |  |  |  |
| 12 |  |  |  |  |  |
| 13 |  |  |  |  | A:ProjectFinal due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Agent Configuration and Custom Skills Setup** — Configure coding agent endpoints and implement basic custom skills using local development tools. | CO1.LO2 | Student development machines, software development environments |
| 2 | **Model Context Protocol Environment Configuration** — Set up and verify model context protocol environments, implementing custom skills and testing interface compliance. | CO1.LO2, CO1.LO3 | Student development machines, software development environments |
| 3 | **Protocol Environment Verification** — Verify configuration of model context protocols and test repository interfaces against stated specifications. | CO1.LO3 | Student development machines, software development environments |
| 4 | **Executable Specifications for REST APIs** — Construct executable specifications for supplied REST API modules using spec-driven development tools. | CO2.LO2 | Student development machines, software development environments |
| 5 | **REST API Spec-Driven Development** — Refine and validate executable specifications for REST API modules ensuring all acceptance tests pass. | CO2.LO2 | Student development machines, software development environments |
| 6 | **Failure Cause Deconstruction** — Deconstruct software development loops into iterative workflows, identifying at least three distinct failure causes supported by evidence. | CO3.LO2 | Student development machines, software development environments |
| 7 | **Automated Testing Frameworks Execution** — Execute automated testing frameworks on AI-generated codebases to gather performance and reliability metrics. | CO4.LO1 | Student development machines, access to AI coding tools/APIs |
| 8 | **Reliability and Performance Evaluation** — Evaluate reliability and performance of AI codebases using testing frameworks, justifying design decisions. | CO4.LO2 | Student development machines, access to AI coding tools/APIs |
| 9 | **Agent Workflow Integration** — Integrate agent workflows and initiate software factories deployment for project integration. | CO5.LO1, CO5.LO2 | Student development machines, access to AI coding tools/APIs |
| 10 | **Software Factories Deployment** — Deploy and evaluate end-to-end AI-native software development factory for a microservice domain. | CO5.LO2 | Student development machines, access to AI coding tools/APIs |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (needs_confirmation); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3) | — | tool-use |  |
| assignment | 25.0 | A:Assignment1 (W4→W5), A:Assignment2 (W5→W6) | — | implement, design, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, design |  |
| project | 25.0 | A:ProjectMilestone1 (W7→W9), A:ProjectFinal (W8→W13) | — | design, implement, evaluate-critique, oral-presentation, written-communication |  |
| endsem | 20.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique, design |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 22.5%, CO2 12.5%, CO3 20.0%, CO4 22.5%, CO5 22.5%

## 10. Resource material

Policy: **reading_list** — The course covers emerging topics in AI-native software development, agent-assisted coding, and model context protocols where traditional textbooks are not yet available.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reference | Ian Sommerville (2005). *Software Engineering*. | 9780133943030 | yes | M2.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 |  | 2 [3] |  | 3 [2] |
| CO2 |  | 3 [3] |  | 3 [unclaimed] |
| CO3 | 3 [2] | 3 [unclaimed] |  |  |
| CO4 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 3 [unclaimed] |
| CO5 | 2 [unclaimed] | 3 [3] | 2 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring modern coding environments using agent-assisted tools directly exercises system implementation using contemporary methodologies. (activities: implement, tool-use)
- CO1→PO9: Using model context protocols and custom skills requires advanced tool proficiency. (activities: tool-use)
- CO2→PO4: Constructing executable specifications via spec-driven tools is core to designing and implementing software requirements. (activities: design, implement)
- CO3→PO3: Deconstructing and analyzing workflows helps adapt techniques for iterative problem solving. (activities: analyse-data)
- CO4→PO4: Systematic evaluation of codebases directly maps to the evaluation component of PO4. (activities: evaluate-critique, tool-use)
- CO5→PO4: Evaluating end-to-end AI-native development systems aligns with system evaluation outcomes. (activities: evaluate-critique, oral-presentation)
- CO5→PO7: Live scenario walkthroughs and presentations require effective oral communication. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1 |
| CO1.LO2 | L3 | M1.T2 | 1, 2 | A:Assignment1@L3 |
| CO1.LO3 | L3 | M1.T3 | 2, 3 | A:Assignment1@L3 |
| CO2.LO1 | L2 | M2.T1 | 3, 4 | A:Assignment2@L2 |
| CO2.LO2 | L3 | M2.T2 | 4, 5 | A:Assignment2@L3 |
| CO3.LO1 | L4 | M3.T1 | 5 | A:Midsem@L4 |
| CO3.LO2 | L4 | M3.T2 | 6 | A:Midsem@L4 |
| CO4.LO1 | L3 | M4.T1 | 7 | A:ProjectMilestone1@L3 |
| CO4.LO2 | L5 | M4.T2 | 7, 8 | A:ProjectMilestone1@L5, A:Endsem@L5 |
| CO5.LO1 | L5 | M5.T1 | 8, 9 | A:ProjectFinal@L5, A:Endsem@L5 |
| CO5.LO2 | L5 | M5.T2 | 9, 10 | A:ProjectFinal@L5 |

## Appendix C — Modules and topics

**M1 Agent-Assisted Coding and Model Context Protocols** (primary CO1)
- M1.T1 Coding agents configuration parameters and protocol endpoints — 2.0 h · LOs CO1.LO1
- M1.T2 Custom skills and model context protocols implementation — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Model context protocol environment configuration and verification — 3.0 h · LOs CO1.LO3 · requires M1.T2
**M2 Spec-Driven Development and Executable Specifications** (primary CO2)
- M2.T1 Spec-driven development and requirements translation — 2.0 h · LOs CO2.LO1 · requires M1.T3
- M2.T2 Executable specifications for REST API modules — 3.0 h · LOs CO2.LO2 · requires M2.T1
**M3 Loop Engineering and Software Development Workflows** (primary CO3)
- M3.T1 Loop engineering and workflow phase isolation — 2.0 h · LOs CO3.LO1 · requires M2.T2
- M3.T2 Iterative development and failure cause deconstruction — 3.0 h · LOs CO3.LO2 · requires M3.T1
**M4 Automated Testing and Reliability Evaluation** (primary CO4)
- M4.T1 Automated testing frameworks for AI-generated codebases — 2.0 h · LOs CO4.LO1 · requires M3.T2
- M4.T2 Reliability and performance evaluation frameworks — 3.0 h · LOs CO4.LO2 · requires M4.T1
**M5 AI-Native Software Factories and Capstone Integration** (primary CO5)
- M5.T1 Project discussion and agent workflow integration — 2.0 h · LOs CO5.LO1 · requires M4.T2
- M5.T2 Hands-on coding and software factories deployment — 3.0 h · LOs CO5.LO2 · requires M5.T1

Schedule: feasible · 28.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | substantive | CSE701 treats AI in SE from a data and research perspective, whereas this course focuses on operationalizing AI coding agents, prompt/context engineering, and iterative workflow loops. |
| CSE581 | 0.034 | superficial | CSE581 covers traditional systems analysis and requirements engineering theories, whereas this course emphasizes executable specifications and spec-driven development for AI agents. |
| CSE582 | 0.067 | complementary | CSE582 addresses product lines, maintenance, and re-engineering, whereas this course targets AI-driven software factories and automated loop engineering. |
| CSE594A | 0.08 | complementary | CSE594A focuses on agentic reasoning for algorithmic and mathematical problem solving, whereas this course specializes in software development workflows, developer tooling, and coding agents. |
| CSE201 | 0.017 | superficial | CSE201 teaches object-oriented programming and basic unit testing in Java, whereas this course deals with automated testing and evaluation within AI-assisted workflows. |
| CSE583 | 0.0 | superficial | CSE583 focuses on open source software development processes and tools. |
| AI501 | 0.034 | superficial | AI501 provides a core machine learning foundation, whereas this course uses AI tools and models for applied software development workflows. |
| CSE665 | 0.0 | superficial | CSE665 covers the foundational principles and architecture of large language models. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Literature review structure and advanced software engineering project framing. Avoid: Excessive focus on mining software repositories rather than active agentic development.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Concepts of agentic protocols, MCP, and tool use. Avoid: Purely mathematical and algorithmic problem solving focus.
- **CSE201** Advanced Programming — IIIT-D catalogue. Take: Hands-on coding assignment structures and automated testing validation. Avoid: Traditional object-oriented design patterns without AI tooling.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| structure | V21 | error |  | topics fill only 28.0 h of 39 h (< 85%): the schedule would leave teaching weeks empty |
| cos | V11 | warning | CO5 | CO CO5 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 0.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W11, W12, W13 | weeks with no lecture topics: [11, 12, 13] |
| structure | VK-CONTENT | warning | K14 | required content 'practical assignments' (K14) is not covered by any topic or LO |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 6 → 0 · round 1 rejected (6→6); round 2 accepted (6→2); round 3 accepted (2→0)
- structure: errors 1 → 1 · round 1 rejected (1→6); round 2 rejected (1→1); round 3 rejected (1→6)
- assessment: errors 3 → 0 · round 1 accepted (3→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Special constraint specifies 0 lecture hours, which may conflict with standard institutional lecture credit requirements if credits are assigned.
- positioning: SC1: The special constraint mandates exactly 0 lecture hours for a 4-credit course, which requires careful alignment with tutorial and lab delivery models.
- constraints: Lecture hours vs credits: CCO.special_constraints specifies 0 lecture hours, but the course is configured as a 4-credit course with 3 lecture hours per week according to regulation UGREG-2025§4(2)a.
- cos: CO5: Requires careful scheduling of the project deliverable and live demonstration during lab hours given that lecture hours are 0.
- copo: CO5 oral-presentation mapping: CO5 maps to PO7 via oral-presentation, which requires ensuring that the assessment plan explicitly incorporates a graded live presentation or walkthrough.
- los: SC1: Special constraint SC1 mandates exactly 0 lecture hours. All hours are allocated to tutorials and labs, resulting in 11 tutorial hours and 26 lab hours.
- structure: Lecture hours total constraint: Special constraint K17 mandates 0 lecture hours, whereas standard course metadata defines 39 lecture hours. The module structure schedules topics using practical/tutorial hour equivalents.
- labs: infrastructure: Paid API access and specific AI coding tool licenses need explicit confirmation from the department.
- labs: schedule: Weeks 11 to 13 have no scheduled topics in the input data context, which may require adjustment if instructional weeks extend further.
- resources: Candidate Resources: The retrieved external candidates and corpus resources lack modern references specifically targeting AI-native development, coding agents, and Model Context Protocols (MCP). A focused search request has been added.
- narrative: SC1 vs approved_graph_summary: Special constraint SC1 states the course must have 0 lecture hours, whereas approved_graph_summary lists L: 3 hours.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress from foundational configuration of agent-assisted coding and model context protocols to spec-driven development, loop engineering, automated testing, and capstone AI-native software factory integration. This sequence relies on the foundational software engineering and programming prerequisites established in CSE201.
- **assessment rationale:** The assessment mix comprising quizzes, assignments, midsem, project, and endsem aligns with the practical, workflow-oriented pedagogical emphasis and evaluates both conceptual understanding and applied competencies spanning all course outcomes.
- **positioning rationale:** Unlike CSE701 which treats AI in software engineering from a data and research perspective, or AI501 which provides a machine learning foundation, this course focuses on operationalizing AI coding agents, prompt and context engineering, and iterative workflow loops.