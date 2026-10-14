# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-vague_degree` · generated deterministically from the design graph · validator status: **8 errors, 4 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

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

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Designed for third and fourth-year BTech Computer Science and Engineering students, the course matters because it addresses the rapid shift toward agentic software engineering and AI-assisted development practices. Students will be able to configure agent skills and tool use mechanisms, translate high-level requirements into executable specifications using the Model Context Protocol, analyze loop engineering patterns in coding agent workflows, evaluate automated testing and reliability metrics for AI-generated code bases, and assess AI-native software development workflows through live scenario walkthroughs. The course is taught through a combination of lectures, tutorials, and practical laboratory sessions, supported by hands-on development and project-based evaluation.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 (or CSE201) `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students require strong programming and software development fundamentals, including automated testing and modular design, to effectively evaluate and construct AI-assisted software systems. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in software engineering with a weighted jaccard overlap of 0.185, it focuses broadly on data and AI models applied to software engineering tasks such as defect prediction and mining repositories. The new course specifically targets modern AI-native software development, agentic workflows, coding agents, and human-AI collaborative development processes.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure agent skills and tool use mechanisms, using an agent orchestration framework, such that at least 90% of the provided test cases pass.** `[CORPUS, USER]`  
verb *Configure* · behaviour *agent skills and tool use mechanisms* · condition *using an agent orchestration framework* · degree *such that at least 90% of the provided test cases pass* · evidence: programming_assignment, lab_task · marks share (computed): 27.5%

- CO1.LO1 (L1) Identify agent skills and tool use mechanisms in an agent orchestration framework thoroughly.
- CO1.LO2 (L3 ★capstone) Configure agent skills and tool use mechanisms, using an agent orchestration framework, thoroughly.

**CO2 (L3, procedural) — Translate high-level requirements into executable specifications, using Model Context Protocol and structured context engineering, justifying each design decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *Translate* · behaviour *high-level requirements into executable specifications* · condition *using Model Context Protocol and structured context engineering* · degree *justifying each design decision against at least one stated requirement* · evidence: design_document, programming_assignment · marks share (computed): 25.5%

- CO2.LO1 (L2) Describe high-level requirements and Model Context Protocol principles deeply.
- CO2.LO2 (L3 ★capstone) Translate high-level requirements into executable specifications, using Model Context Protocol and structured context engineering, deeply.

**CO3 (L4, conceptual) — Analyze loop engineering patterns in coding agent workflows, using supplied execution traces and logs, identifying at least 3 distinct patterns, each supported by evidence from the execution traces.** `[CORPUS, USER]`  
verb *Analyze* · behaviour *loop engineering patterns in coding agent workflows* · condition *using supplied execution traces and logs* · degree *identifying at least 3 distinct patterns, each supported by evidence from the execution traces* · evidence: exam_question, report · marks share (computed): 17.75%

- CO3.LO1 (L4) Examine loop engineering patterns in coding agent workflows thoroughly.
- CO3.LO2 (L4 ★capstone) Analyze loop engineering patterns in coding agent workflows, using supplied execution traces and logs, deeply.

**CO4 (L5, procedural) — Evaluate automated testing and reliability metrics for AI-generated code bases, using benchmark suites and verification tools, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *automated testing and reliability metrics for AI-generated code bases* · condition *using benchmark suites and verification tools* · degree *such that the delivered system satisfies every acceptance criterion agreed at the first milestone* · evidence: programming_assignment, project_deliverable · marks share (computed): 16.5%

- CO4.LO1 (L3) Demonstrate automated testing tools on AI-generated code bases thoroughly.
- CO4.LO2 (L5 ★capstone) Evaluate automated testing and reliability metrics for AI-generated code bases, using benchmark suites and verification tools, deeply.

**CO5 (L5, metacognitive) — Evaluate an AI-native software development workflow, incorporating coding agents and emergent developer tools, demonstrated live, with 3 scenario walkthroughs chosen by the evaluator.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *an AI-native software development workflow* · condition *incorporating coding agents and emergent developer tools* · degree *demonstrated live, with 3 scenario walkthroughs chosen by the evaluator* · evidence: project_deliverable, presentation · marks share (computed): 12.75%

- CO5.LO1 (L2) Discuss components of an AI-native software development workflow thoroughly.
- CO5.LO2 (L5 ★capstone) Evaluate an AI-native software development workflow, incorporating coding agents and emergent developer tools, deeply.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Agent skills and capabilities (M1.T1)<br>Coding agents and tool use mechanisms (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Worked trace-diagnosis of 3 agent capability definitions, in pairs. |  |
| 2 | Coding agents and tool use mechanisms (M1.T2)<br>Tool use execution and framework integration (M1.T3) | CO1.LO2 | CO1 | Review and peer-review of coding agent tool-call payload configurations. | A:PA1 released |
| 3 | Advanced agent capabilities and orchestration workflows (M1.T4)<br>Model Context Protocol and context engineering principles (M2.T1) | CO1.LO2, CO2.LO1 | CO1, CO2 | Problem-solving session on multi-agent orchestration workflow failure modes. | A:PA1 due |
| 4 | Model Context Protocol and context engineering principles (M2.T1)<br>Requirements to executable specifications using spec-driven development (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Worked trace-diagnosis of Model Context Protocol context schemas, in groups. | A:Quiz1 (quiz); A:ProjM1 released |
| 5 | Executable specifications design and validation (M2.T3)<br>Specification-driven development case studies (M2.T4) | CO2.LO2 | CO2 | Trace-diagnosis of ambiguities in high-level requirements turned into specifications. |  |
| 6 | Specification-driven development case studies (M2.T4)<br>Loop engineering patterns in coding agent workflows (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Group discussion and peer review of specification validation test cases. |  |
| 7 | Iterative development and software factories analysis (M3.T2)<br>Software factory architectures and analysis (M3.T3) | CO3.LO2 | CO3 | Worked trace-diagnosis of loop engineering infinite loops in agent runs. | A:Midsem (midsem); A:ProjM1 due |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Software factory architectures and analysis (M3.T3)<br>Iterative development trace evaluation (M3.T4) | CO3.LO2 | CO3 | Analysis of software factory execution logs to identify performance bottlenecks. | A:ProjM2 released |
| 9 | Automated testing tools and evaluation benchmarks (M4.T1)<br>Reliability metrics and verification tools for AI-generated code (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Worked trace-diagnosis of failing automated tests on AI-generated code snippets. |  |
| 10 | Reliability metrics and verification tools for AI-generated code (M4.T2)<br>Verification tools and reliability frameworks (M4.T3) | CO4.LO2 | CO4 | Peer review of reliability metrics computation sheets on benchmark suites. |  |
| 11 | Acceptance criteria and automated evaluation (M4.T4)<br>Components of an AI-native software development workflow (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Problem-solving on verification tool warning messages and correctness proofs. | A:PA2 (assignment) |
| 12 | Components of an AI-native software development workflow (M5.T1)<br>Evaluating emergent developer tools and AI workflows (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Group discussion comparing components of different AI-native software workflows. |  |
| 13 | Evaluating emergent developer tools and AI workflows (M5.T2)<br>Workflow integration and scenario walkthroughs (M5.T3) | CO5.LO2 | CO5 | Walkthrough and peer critique of AI-native software workflow evaluation reports. | A:ProjM2 due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Agent Skills and Basic Tool Use Configuration** — Configure basic agent skills and simple tool use mechanisms using an agent framework. | CO1.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 2 | **Tool Use Execution and Framework Integration** — Implement tool use execution pipelines and integrate them within an agent orchestration framework. | CO1.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 3 | **Advanced Agent Capabilities and Orchestration Workflows** — Build multi-step agent orchestration workflows incorporating advanced agent capabilities. | CO1.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 4 | **Spec-Driven Development and Executable Specifications** — Translate high-level functional requirements into executable specifications using structured context engineering. | CO2.LO2 | Student development machines, software development environments |
| 5 | **Executable Specifications Design and Validation** — Design and validate executable specifications against system requirement test cases. | CO2.LO2 | Student development machines, software development environments |
| 6 | **Specification-Driven Development Case Studies** — Implement a medium-scale feature set following end-to-end specification-driven development case studies. | CO2.LO2 | Student development machines, software development environments |
| 7 | **Software Factory Architectures and Trace Analysis** — Analyze software factory architectures and execution traces to identify agent bottlenecks. | CO3.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 8 | **Iterative Development Trace Evaluation** — Examine iterative execution logs and trace outputs from multi-agent software factories. | CO3.LO2 | Student development machines, software development environments |
| 9 | **Automated Testing Tools and Reliability Metrics** — Deploy automated testing frameworks and calculate reliability metrics on AI-generated code. | CO4.LO1, CO4.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 10 | **Verification Tools and Reliability Frameworks** — Execute verification tools on generated code to measure correctness against reliability frameworks. | CO4.LO2 | Student development machines, software development environments |
| 11 | **Acceptance Criteria and Automated Evaluation** — Write automated evaluation scripts and check acceptance criteria compliance for agent outputs. | CO4.LO2 | Student development machines, software development environments |
| 12 | **Evaluating Emergent Developer Tools** — Set up and evaluate emergent AI developer tools within a standard software development workflow. | CO5.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |
| 13 | **Workflow Integration and Scenario Walkthroughs** — Integrate end-to-end AI-native workflows and perform end-to-end scenario evaluations. | CO5.LO2 | Student development machines, software development environments, access to AI coding tools/APIs |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W4→W4) | — | analyse-data |  |
| assignment | 25.0 | A:PA1 (W2→W3), A:PA2 (W11→W11) | — | implement, tool-use | Hands-on coding exercises and practical assignments are emphasized in course preferences. |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, written-communication |  |
| project | 25.0 | A:ProjM1 (W4→W7), A:ProjM2 (W8→W13) | — | design, implement, evaluate-critique, oral-presentation, written-communication | Substantial project-based evaluation requested by professor preferences. |
| endsem | 20.0 | A:Endsem (W13→W13) | — | analyse-data, written-communication |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 27.5%, CO2 25.5%, CO3 17.75%, CO4 16.5%, CO5 12.75%

## 10. Resource material

Policy: **mixed** — Due to the fast-moving nature of AI-native software development, coding agents, and Model Context Protocol (MCP), a mixed policy combining foundational reference texts with recent research papers and framework documentation is used.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reference | Antonio Gullí (2025). *Agentic Design Patterns.*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T4, M3.T1 |
| reading |  (2025). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M2.T1 |
| reading | Yujia Li, Shunyu Yao, Guanzhi Wang, John Yang, Alexander Novikov, Bogdan Georgiev (2024). *Competition-level code generation with alphacode and related agent papers*. | R:hash:1-li-yujia-et-al-competition-level-code- | NO: candidate_id not in retrieved candidates | M1.T2, M4.T1 |
| reference | Srinivasan Sekar (2026). *Under the Hood: The Protocol Specification*. | 10.1007/979-8-8688-2364-0_6 | yes | M2.T1 |
| reference | John E. Robert, Ipek Ozkaya, Douglas C. Schmidt (2026). *Transforming Software Engineering and Software Acquisition with Large Language Models*. | 10.1201/9781003492252-7 | yes | M5.T1 |
| reference | Jerin George Mathew, Jacopo Rossi (2025). *Large Language Model Agents*. | 10.1007/978-3-031-92285-5_8 | yes | M1.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 2 [3] | 2 [unclaimed] | 2 [2] |
| CO2 | 2 [unclaimed] | 2 [3] | 3 [unclaimed] | 2 [unclaimed] |
| CO3 | 3 [3] | 1 [unclaimed] | 3 [unclaimed] | 1 [unclaimed] |
| CO4 | 1 [unclaimed] | 3 [3] | 1 [unclaimed] | 3 [2] |
| CO5 | 2 [unclaimed] | 3 [3] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring agent skills and tool use mechanisms directly maps to implementing computer-based applications using modern frameworks and tools. (activities: implement, tool-use)
- CO1→PO9: Uses advanced orchestration tools and frameworks for building agentic systems. (activities: tool-use)
- CO2→PO4: Translating requirements into executable specifications is a core system design activity using modern methodologies. (activities: design)
- CO3→PO3: Analyzing loop engineering patterns from execution traces involves examining and adapting techniques for agent workflows. (activities: analyse-data)
- CO4→PO4: Evaluating automated testing and reliability metrics corresponds directly to system evaluation using benchmark suites. (activities: evaluate-critique)
- CO4→PO9: Involves using advanced verification tools and benchmark suites for AI-generated code. (activities: tool-use)
- CO5→PO4: Evaluating AI-native software development workflows aligns with system evaluation using modern tools. (activities: evaluate-critique)
- CO5→PO7: Live demonstrations and scenario walkthroughs require effective oral communication. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1, A:Midsem@L1, A:Endsem@L1 |
| CO1.LO2 | L3 | M1.T2, M1.T3, M1.T4 | 1, 2, 3 | A:PA1@L3 |
| CO2.LO1 | L2 | M2.T1 | 3, 4 | A:Quiz1@L2, A:Midsem@L2, A:Endsem@L2 |
| CO2.LO2 | L3 | M2.T2, M2.T3, M2.T4 | 4, 5, 6 | A:ProjM1@L3 |
| CO3.LO1 | L4 | M3.T1 | 6 | A:Midsem@L4, A:Endsem@L4 |
| CO3.LO2 | L4 | M3.T2, M3.T3, M3.T4 | 7, 8 | A:ProjM2@L4 |
| CO4.LO1 | L3 | M4.T1 | 9 | A:Endsem@L3 |
| CO4.LO2 | L5 | M4.T2, M4.T3, M4.T4 | 9, 10, 11 | A:PA2@L5 |
| CO5.LO1 | L2 | M5.T1 | 11, 12 | A:Endsem@L2 |
| CO5.LO2 | L5 | M5.T2, M5.T3 | 12, 13 | A:ProjM2@L5 |

## Appendix C — Modules and topics

**M1 Agent Orchestration and Tool Use** (primary CO1)
- M1.T1 Agent skills and capabilities — 2.0 h · LOs CO1.LO1
- M1.T2 Coding agents and tool use mechanisms — 2.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Tool use execution and framework integration — 2.0 h · LOs CO1.LO2 · requires M1.T2
- M1.T4 Advanced agent capabilities and orchestration workflows — 2.0 h · LOs CO1.LO2 · requires M1.T3
**M2 Model Context Protocol and Specification-Driven Development** (primary CO2)
- M2.T1 Model Context Protocol and context engineering principles — 2.0 h · LOs CO2.LO1 · requires M1.T2
- M2.T2 Requirements to executable specifications using spec-driven development — 2.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Executable specifications design and validation — 2.0 h · LOs CO2.LO2 · requires M2.T2
- M2.T4 Specification-driven development case studies — 2.0 h · LOs CO2.LO2 · requires M2.T3
**M3 Loop Engineering and Agent Workflows** (primary CO3)
- M3.T1 Loop engineering patterns in coding agent workflows — 2.0 h · LOs CO3.LO1 · requires M2.T2
- M3.T2 Iterative development and software factories analysis — 2.0 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Software factory architectures and analysis — 2.0 h · LOs CO3.LO2 · requires M3.T2
- M3.T4 Iterative development trace evaluation — 2.0 h · LOs CO3.LO2 · requires M3.T3
**M4 Automated Testing and Evaluation for AI Code Bases** (primary CO4)
- M4.T1 Automated testing tools and evaluation benchmarks — 2.0 h · LOs CO4.LO1 · requires M3.T2
- M4.T2 Reliability metrics and verification tools for AI-generated code — 2.0 h · LOs CO4.LO2 · requires M4.T1
- M4.T3 Verification tools and reliability frameworks — 2.0 h · LOs CO4.LO2 · requires M4.T2
- M4.T4 Acceptance criteria and automated evaluation — 2.0 h · LOs CO4.LO2 · requires M4.T3
**M5 AI-Native Software Development Workflows and Projects** (primary CO5)
- M5.T1 Components of an AI-native software development workflow — 3.0 h · LOs CO5.LO1 · requires M4.T2
- M5.T2 Evaluating emergent developer tools and AI workflows — 2.0 h · LOs CO5.LO2 · requires M5.T1
- M5.T3 Workflow integration and scenario walkthroughs — 2.0 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 39.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 addresses traditional AI and data-driven methods in software engineering (e.g., repository mining, defect prediction), whereas this course focuses on contemporary AI-native development workflows, coding agents, and agentic software engineering frameworks. |
| CSE594A | 0.08 | complementary | CSE594A concentrates broadly on agentic reasoning for algorithmic, mathematical, and scientific problem-solving, whereas this course applies agents specifically to software development workflows and engineering practices. |
| CSE582 | 0.067 | complementary | CSE582 emphasizes traditional software product line engineering, maintenance, and re-engineering, whereas this course focuses on software production through AI-native automation and coding agents. |
| CSE581 | 0.034 | superficial | CSE581 covers traditional systems analysis, design, and requirements engineering theories, whereas this course focuses on specification-driven development for AI coding agents. |
| AI501 | 0.034 | superficial | AI501 provides foundational machine learning theory and evaluation metrics, whereas this course deals with evaluating and testing software built via AI-assisted workflows. |
| CSE201 | 0.017 | superficial | CSE201 teaches foundational advanced programming and object-oriented design in Java, whereas this course assumes these fundamentals and focuses on AI-native developer collaboration. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Research literature review structure and project-based evaluation methodology. Avoid: Focusing primarily on mining software repositories and legacy data analysis rather than modern generative coding agents.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Foundational treatment of agentic protocols such as MCP and multi-agent collaboration frameworks. Avoid: Narrowly focusing on algorithmic and mathematical problem solving instead of practical software development workflows.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Practical tool integration approach and team-based application building. Avoid: Treating open source contribution processes as the primary learning objective rather than AI-assisted engineering.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| los | V11 | error | CO1.LO1 | LO CO1.LO1 degree is vague (['thoroughly']): 'thoroughly' |
| los | V11 | error | CO1.LO2 | LO CO1.LO2 degree is vague (['thoroughly']): 'thoroughly' |
| los | V11 | error | CO3.LO1 | LO CO3.LO1 degree is vague (['thoroughly']): 'thoroughly' |
| los | V11 | error | CO4.LO1 | LO CO4.LO1 degree is vague (['thoroughly']): 'thoroughly' |
| los | V11 | error | CO5.LO1 | LO CO5.LO1 degree is vague (['thoroughly']): 'thoroughly' |
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Agentic Design Patterns.' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:1-li-yujia-et-al-competition-level-code- | resource 'Competition-level code generation with alphacode and related agent papers' not verified: ['candidate_id not in retrieved candidates'] |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 condition is not visible in the statement text |

**Repair history**

- cos: errors 6 → 0 · round 1 accepted (6→0)
- los: errors 5 → 5 · round 1 rejected (5→1); round 2 rejected (5→1); round 3 rejected (5→1)
- structure: errors 5 → 0 · round 1 rejected (5→1); round 2 accepted (5→0)
- assessment: errors 10 → 0 · round 1 accepted (10→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Special constraint requires learning objectives to use exact degree strings 'thoroughly' or 'deeply', which will need to be verified during outcome design.
- cos: SC1: Special constraint SC1 requires the exact degree string 'thoroughly' or 'deeply' for all LOs, which has been applied directly to all CO degrees to ensure compliance.
- los: Special Constraint SC1: All LO degrees were set to 'thoroughly' or 'deeply' to comply with SC1 while maintaining checkable granularity.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules follow a logical progression from foundational agent orchestration and tool use to specification-driven development, loop engineering, automated testing, and comprehensive AI-native workflows, relying on prerequisites such as CSE201 to ensure that students possess necessary programming and software development fundamentals.
- **assessment rationale:** The assessment mix—comprising quizzes, assignments, a mid-semester examination, a final project, and an end-semester examination—directly matches the course objectives by balancing theoretical comprehension with rigorous practical evaluation of agent-assisted software workflows and coding tasks.
- **positioning rationale:** Unlike CSE701, which addresses traditional AI and data-driven methods in software engineering, or CSE594A, which focuses on agentic reasoning for algorithmic and scientific problem-solving, this course is uniquely positioned to apply coding agents specifically to software development workflows and engineering practices.