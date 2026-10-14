# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-control` · generated deterministically from the design graph · validator status: **5 errors, 9 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM04 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate level specified as text without a formal course code. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 4xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. The curriculum addresses AI-assisted coding environments, agent skills, model context protocols, requirements engineering with executable specifications, automated testing, and software factory architectures. The course is taught through lectures, tutorials, and laboratory sessions emphasizing hands-on development and experimentation. Upon completion, students will be able to construct developer workflows incorporating AI-assisted coding tools, implement agent skills and context engineering mechanisms, translate informal requirements into executable specifications, evaluate reliability and performance of AI-generated code, and architect end-to-end agentic software development factories.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Generic programming | Students need solid software engineering fundamentals, unit testing, and advanced programming capabilities to evaluate and work with AI-generated code. |
| desirable | AI501 `[CATALOGUE]` | ML Model Evaluation, Accuracy, Precision | Familiarity with machine learning evaluation metrics helps students understand the reliability and evaluation of AI coding tools. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in Software Engineering focusing on data mining, defect prediction, and ML applications in software engineering, the new course focuses on modern AI-native software development, coding agents, agentic workflows, and human-AI collaborative development practices.

## 5. Bloom band

L3–L6 · basis: level 4xx band [3,6] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Construct developer workflows incorporating AI-assisted coding tools and coding agents, for a given software development task, such that all public tests pass and no warnings from the configured static analyser.** `[CORPUS, USER]`  
verb *Construct* · behaviour *developer workflows incorporating AI-assisted coding tools and coding agents* · condition *for a given software development task* · degree *such that all public tests pass and no warnings from the configured static analyser* · evidence: programming_assignment, lab_task · marks share (computed): 19.0%

- CO1.LO1 (L3) Configure an AI-assisted coding environment with connected LLM backends and static analyzers for a given development task, producing a working setup note.
- CO1.LO2 (L3) Construct coding agent interactions and prompt pipelines for a supplied module, verifying that all public tests pass.
- CO1.LO3 (L3 ★capstone) Construct end-to-end developer workflows incorporating AI-assisted coding tools and coding agents, for a given software development task, such that all public tests pass and no warnings from the configured static analyser.

**CO2 (L3, procedural) — Implement agent skills, tool uses, and context engineering mechanisms, using an agent orchestration framework, justifying each design decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *Implement* · behaviour *agent skills, tool uses, and context engineering mechanisms* · condition *using an agent orchestration framework* · degree *justifying each design decision against at least one stated requirement* · evidence: programming_assignment, design_document · marks share (computed): 31.25%

- CO2.LO1 (L2) Explain the protocol specifications and data exchange patterns of Model Context Protocol (MCP) using supplied protocol traces.
- CO2.LO2 (L3) Implement custom agent skills and external tool use functions within an agent framework for a supplied requirement specification.
- CO2.LO3 (L3 ★capstone) Implement advanced agent skills, tool uses, and context engineering mechanisms, using an agent orchestration framework, justifying each design decision against at least one stated requirement.

**CO3 (L4, conceptual) — Translate informal system requirements into executable specifications and structured prompt specifications, for a supplied problem statement, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *Translate* · behaviour *informal system requirements into executable specifications and structured prompt specifications* · condition *for a supplied problem statement* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 24.75%

- CO3.LO1 (L4) Examine informal software requirement narratives to identify system use cases and actor boundaries for a supplied problem statement.
- CO3.LO2 (L4 ★capstone) Translate informal system requirements into executable specifications and structured prompt specifications for a specific core module, covering every use case in the supplied requirements document.

**CO4 (L5, procedural) — Evaluate the reliability and performance of AI-generated code and software development loops, using automated testing and evaluation metrics, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *the reliability and performance of AI-generated code and software development loops* · condition *using automated testing and evaluation metrics* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, report, code_review · marks share (computed): 13.75%

- CO4.LO1 (L3) Execute automated test suites on AI-generated code snippets using a supplied evaluation script.
- CO4.LO2 (L5 ★capstone) Evaluate the reliability and performance of AI-generated code snippets and individual software development loops, using automated testing and evaluation metrics, identifying at least three distinct failure causes with supporting log evidence.

**CO5 (L6, metacognitive) — Architect an end-to-end agentic software development factory, incorporating coding agents, iterative loops, and automated deployment pipelines, demonstrated live, with 3 scenario walkthroughs chosen by the evaluator.** `[CORPUS, USER]`  
verb *Architect* · behaviour *an end-to-end agentic software development factory, incorporating coding agents, iterative loops, and automated deployment pipelines* · condition *demonstrated live* · degree *with 3 scenario walkthroughs chosen by the evaluator* · evidence: project_deliverable, presentation · marks share (computed): 11.25%

- CO5.LO1 (L3) Construct component modules of an agentic software factory including iterative loop handlers and deployment pipelines.
- CO5.LO2 (L6 ★capstone) Architect the final integration tier of an end-to-end agentic software development factory, incorporating coding agents, iterative loops, and automated deployment pipelines, demonstrated live, with 3 scenario walkthroughs chosen by the evaluator.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding environments setup (M1.T1)<br>Coding agents and interaction mechanisms (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Worked trace-diagnosis of 3 initial AI-assisted environment configuration failures, in pairs. |  |
| 2 | Coding agents and interaction mechanisms (M1.T2)<br>End-to-end AI-assisted developer workflows (M1.T3) | CO1.LO2, CO1.LO3 | CO1 | Peer review of coding agent prompt pipelines and debugging of edge case interaction failures. |  |
| 3 | End-to-end AI-assisted developer workflows (M1.T3)<br>Model Context Protocol specifications (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Problem-solving session tracing end-to-end developer workflows and resolving static analyzer warnings. | A:Assign1 released |
| 4 | Model Context Protocol specifications (M2.T1)<br>Custom agent skills and external tool use (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Analysis of Model Context Protocol specification traces and protocol message exchange patterns in groups. | A:Quiz1 (quiz); A:Assign1 due |
| 5 | Custom agent skills and external tool use (M2.T2)<br>Context engineering mechanisms in agent frameworks (M2.T3) | CO2.LO2, CO2.LO3 | CO2 | Worked trace-diagnosis of custom agent skill invocation errors and tool-use interface mismatches. |  |
| 6 | Software requirements analysis and use case identification (M3.T1)<br>Executable specifications and structured prompts (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Group problem-solving on examining informal software requirement narratives to identify system use cases and actor boundaries. | A:Assign2 (assignment); A:ProjMilestone1 released |
| 7 | Executable specifications and structured prompts (M3.T2)<br>Automated test execution on AI-generated code (M4.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Review of executable specifications and structured prompt translations for complex system modules. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Automated test execution on AI-generated code (M4.T1)<br>Reliability and evaluation metrics for AI software (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Mid-term post-mortem and discussion on automated test execution failures on AI-generated code. |  |
| 9 | Reliability and evaluation metrics for AI software (M4.T2)<br>Iterative loop engineering components (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Analysis of failure logs and evaluation metric computations for AI software reliability cases. | A:ProjMilestone1 due; A:ProjFinal released |
| 10 | Software factory components and orchestration (M5.T1b)<br>End-to-end software factory architecture (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Worked trace-diagnosis of iterative loop engineering components and software factory bottlenecks. |  |
| 11 | End-to-end software factory architecture (M5.T2)<br>Software factory deployment pipelines (M5.T2b) | CO5.LO2 | CO5 | Group design review of end-to-end software factory architecture integration plans. |  |
| 12 | Software factory deployment pipelines (M5.T2b) | CO5.LO2 | CO5 | Mock scenario walkthrough and peer critique for software factory deployment pipelines. |  |
| 13 |  |  |  | Open consultation and final course synthesis discussion on agentic software development futures. | A:ProjFinal due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **AI-Assisted Coding Environment Setup** — Configure an AI-assisted coding environment with connected LLM backends and static analyzers on student development machines, producing a working setup note. | CO1.LO1 | Student development machines, Software development environments |
| 2 | **Coding Agents Interaction** — Construct coding agent interactions and prompt pipelines for a supplied module, verifying that all public tests pass. | CO1.LO2 | Student development machines, Access to AI coding tools/APIs |
| 3 | **End-to-End Developer Workflows** — Construct end-to-end developer workflows incorporating AI-assisted coding tools and coding agents, ensuring all public tests pass and no static analyzer warnings. | CO1.LO3 | Student development machines, Access to AI coding tools/APIs |
| 4 | **Custom Agent Skills and Tool Use** — Implement custom agent skills and external tool use functions within an agent framework for a supplied requirement specification. | CO2.LO2 | Student development machines, Access to AI coding tools/APIs |
| 5 | **Context Engineering Mechanisms** — Implement advanced agent skills, tool uses, and context engineering mechanisms using an agent orchestration framework, justifying design decisions. | CO2.LO3 | Student development machines, Access to AI coding tools/APIs |
| 6 | **Executable Specifications and Structured Prompts** — Translate informal system requirements into executable specifications and structured prompt specifications for a specific core module. | CO3.LO2 | Student development machines |
| 7 | **Automated Test Execution** — Execute automated test suites on AI-generated code snippets using a supplied evaluation script. | CO4.LO1 | Student development machines, Access to AI coding tools/APIs |
| 8 | **Catch-up and Open Lab** — Open lab session for catch-up and consultation following mid-term examinations. | CO4.LO1 | Student development machines |
| 9 | **AI Software Reliability and Evaluation** — Evaluate reliability and performance of AI-generated code snippets using automated testing and evaluation metrics, identifying failure causes. | CO4.LO2 | Student development machines, Access to AI coding tools/APIs |
| 10 | **Agentic Software Factory Components** — Construct component modules of an agentic software factory including iterative loop handlers and deployment pipelines. | CO5.LO1 | Student development machines, Access to AI coding tools/APIs |
| 11 | **Software Factory Integration** — Architect the final integration tier of an end-to-end agentic software development factory incorporating coding agents and deployment pipelines. | CO5.LO2 | Student development machines, Access to AI coding tools/APIs |
| 12 | **Software Factory Demonstration Preparation** — Prepare and rehearse live scenario walkthroughs for the end-to-end agentic software development factory integration tier. | CO5.LO2 | Student development machines, Access to AI coding tools/APIs |
| 13 | **Final Project Presentations** — Demonstrate the end-to-end agentic software development factory live with 3 scenario walkthroughs chosen by the evaluator. | CO5.LO2 | Student development machines |

Infrastructure: Student development machines (available); Access to AI coding tools/APIs (available); Software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W4→W4) | — | analyse-data |  |
| assignment | 20.0 | A:Assign1 (W3→W4), A:Assign2 (W6→W6) | — | design, implement, tool-use |  |
| project | 25.0 | A:ProjMilestone1 (W6→W9), A:ProjFinal (W9→W13) | — | design, implement, evaluate-critique, oral-presentation |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, design |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data, design, evaluate-critique |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 19.0%, CO2 31.25%, CO3 24.75%, CO4 13.75%, CO5 11.25%

## 10. Resource material

Policy: **reading_list** — AI-native software development, coding agents, and the Model Context Protocol are rapidly evolving fast-moving topics without comprehensive established textbooks, making a curated reading list of recent conference papers and official technical literature necessary.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reading | Sarat Piridi (2026). *Connecting to the Model Context Protocol*. | 10.1007/979-8-8688-2888-1_8 | yes | M2.T1 |
| reading | Igor Zuykov (2026). *Architectural Principles for Multi-Agent Systems Based on The Model Context Protocol*. | 10.37547/tajet/volume08issue03-12 | yes | M2.T2, M2.T3 |
| reading | Yisen Xu (2025). *MUARF: Leveraging Multi-Agent Workflows for Automated Code Refactoring*. | 10.1109/icse-companion66252.2025.00071 | yes | M1.T2, M5.T2 |
| reading | Mohammed A. Shehab, Mohammad Wardat, Safwan Omari, Yaser Jararweh (2024). *Evaluating Large Language Models for Code Generation: Assessing Accuracy, Quality, and Performance*. | 10.1109/fllm63129.2024.10852439 | yes | M4.T2 |
| reading | Weixi Tong, Tianyi Zhang (2024). *CodeJudge: Evaluating Code Generation with Large Language Models*. | 10.18653/v1/2024.emnlp-main.1118 | yes | M4.T1, M4.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 3 [3] |  | 3 [2] |
| CO2 | 3 [unclaimed] | 3 [3] | 1 [unclaimed] | 2 [unclaimed] |
| CO3 | 3 [2] | 3 [unclaimed] | 1 [unclaimed] | 3 [unclaimed] |
| CO4 | 3 [unclaimed] | 3 [3] | 1 [unclaimed] | 3 [unclaimed] |
| CO5 |  | 3 [3] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Students construct developer workflows using modern AI tools, directly matching the design and implementation of systems using modern tools. (activities: design, implement, tool-use)
- CO1→PO9: Incorporating AI-assisted coding tools requires utilising advanced computing tools. (activities: tool-use)
- CO2→PO4: Students implement agent components and design decisions meeting requirements. (activities: design, implement)
- CO3→PO3: Translating informal requirements into structured prompt specifications adapts techniques to new problems. (activities: analyse-data, design)
- CO4→PO4: Students explicitly evaluate system reliability and performance using automated testing. (activities: evaluate-critique)
- CO5→PO4: Architecting an end-to-end agentic software development factory corresponds to designing complex systems. (activities: design, implement)
- CO5→PO7: Live demonstrations and scenario walkthroughs evaluate oral presentation and communication. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1 | 1 | A:Assign1@L3 |
| CO1.LO2 | L3 | M1.T2 | 1, 2 | A:Assign1@L3 |
| CO1.LO3 | L3 | M1.T3 | 2, 3 | A:Assign2@L3, A:Midsem@L3 |
| CO2.LO1 | L2 | M2.T1 | 3, 4 | A:Quiz1@L2, A:Midsem@L2 |
| CO2.LO2 | L3 | M2.T2 | 4, 5 | A:Assign2@L3, A:Endsem@L3 |
| CO2.LO3 | L3 | M2.T3 | 5 | A:ProjFinal@L3 |
| CO3.LO1 | L4 | M3.T1 | 6 | A:Assign2@L4, A:Midsem@L4 |
| CO3.LO2 | L4 | M3.T2 | 6, 7 | A:ProjMilestone1@L4, A:Endsem@L4 |
| CO4.LO1 | L3 | M4.T1 | 7, 8 | A:Endsem@L3 |
| CO4.LO2 | L5 | M4.T2 | 8, 9 | A:ProjFinal@L5 |
| CO5.LO1 | L3 | M5.T1, M5.T1b | 9, 10 | A:ProjMilestone1@L3 |
| CO5.LO2 | L6 | M5.T2, M5.T2b | 10, 11, 12 | A:ProjFinal@L6 |

## Appendix C — Modules and topics

**M1 Foundations of AI-Assisted Coding and Developer Workflows** (primary CO1)
- M1.T1 AI-assisted coding environments setup — 2.0 h · LOs CO1.LO1
- M1.T2 Coding agents and interaction mechanisms — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 End-to-end AI-assisted developer workflows — 3.0 h · LOs CO1.LO3 · requires M1.T2
**M2 Advanced Agent Skills and Context Engineering** (primary CO2)
- M2.T1 Model Context Protocol specifications — 2.0 h · LOs CO2.LO1 · requires M1.T3
- M2.T2 Custom agent skills and external tool use — 3.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Context engineering mechanisms in agent frameworks — 2.0 h · LOs CO2.LO3 · requires M2.T2
**M3 Requirements Engineering and Executable Specifications** (primary CO3)
- M3.T1 Software requirements analysis and use case identification — 2.0 h · LOs CO3.LO1
- M3.T2 Executable specifications and structured prompts — 3.0 h · LOs CO3.LO2 · requires M3.T1
**M4 Automated Testing and Reliability Evaluation** (primary CO4)
- M4.T1 Automated test execution on AI-generated code — 2.0 h · LOs CO4.LO1 · requires M1.T1
- M4.T2 Reliability and evaluation metrics for AI software — 3.0 h · LOs CO4.LO2 · requires M4.T1
**M5 Agentic Software Factories and Deployment** (primary CO5)
- M5.T1 Iterative loop engineering components — 2.0 h · LOs CO5.LO1 · requires M1.T3, M2.T3, M3.T2
- M5.T2 End-to-end software factory architecture — 2.5 h · LOs CO5.LO2 · requires M5.T1, M4.T2
- M5.T1b Software factory components and orchestration — 2.0 h · LOs CO5.LO1 · requires M5.T1
- M5.T2b Software factory deployment pipelines — 2.5 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 34.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 investigates mining software repositories and applying machine learning models to software engineering artifacts, whereas this course emphasizes practical, workflow-oriented design of agentic software development and coding agents. |
| CSE594A | 0.08 | complementary | CSE594A focuses primarily on agentic reasoning for algorithmic and mathematical problem solving, whereas this course targets software engineering workflows, coding agents, and spec-driven software development. |
| CSE582 | 0.067 | complementary | CSE582 covers traditional software evolution, product lines, and maintenance, whereas this course deals with AI-native development and software factories driven by coding agents. |
| CSE581 | 0.034 | superficial | CSE581 deals with classical systems analysis, design theories, and requirements engineering, whereas this course covers automated requirements and spec-driven development using AI. |
| AI501 | 0.034 | superficial | AI501 provides foundational machine learning theory and models, whereas this course uses AI tools in applied software development workflows. |
| CSE201 | 0.017 | superficial | CSE201 teaches object-oriented programming and manual unit testing in Java, whereas this course focuses on automated testing and evaluation in AI-assisted developer workflows. |
| CSE665 | 0.0 | superficial | CSE665 covers large language model architectures and NLP principles theoretically, whereas this course focuses on practical software engineering workflows with coding agents. |
| CSE583 | 0.0 | superficial | CSE583 covers open source tools and development methods, whereas this course focuses on AI-native agentic development. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Agentic protocols, tool use, and multi-agent collaboration concepts Avoid: Focusing solely on algorithmic and mathematical problem solving instead of software development workflows
- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Software engineering evaluation metrics and developer assistance paradigms Avoid: Historical repository data mining and purely analytical software engineering research
- **CSE581** Systems Analysis, Design and Requirements Engineering — IIIT-D catalogue. Take: Structured requirements engineering and specification approaches Avoid: Traditional waterfall-based systems analysis without AI integration

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| los | VLO-COPY | error | CO1.LO3, CO1 | CO1.LO3 restates its parent CO1 (token overlap 0.96); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO2.LO3, CO2 | CO2.LO3 restates its parent CO2 (token overlap 0.95); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO4.LO2, CO4 | CO4.LO2 restates its parent CO4 (token overlap 0.93); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO5.LO2, CO5 | CO5.LO2 restates its parent CO5 (token overlap 0.88); an LO must be a narrower, single-task step |
| positioning | V14 | error | AI501 | prerequisite AI501 is level 5xx > course level 4xx |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO2 | LO CO2.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO2 | LO CO3.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- positioning: errors 1 → 1 · round 1 rejected (1→1); round 2 rejected (1→1); round 3 rejected (1→1)
- los: errors 6 → 4 · round 1 accepted (6→4); round 2 rejected (4→4); round 3 rejected (4→4)
- structure: errors 2 → 0 · round 1 accepted (2→0)
- assessment: errors 5 → 0 · round 1 accepted (5→1); round 2 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: credits: Credits and L-T-P are missing, which will be required for downstream programme structure validation.
- los: hours_budget: Calculated total hours sum to Lecture: 36h, Tutorial: 12h, Lab: 24h, which is slightly under the 39h/13h/26h target budget by roughly 8%, fitting within acceptable scheduling bounds.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress from foundational AI-assisted coding workflows (M1) to advanced agent skills and context engineering (M2), followed by requirements and executable specifications (M3), automated testing and reliability evaluation (M4), and finally integrated agentic software factories and deployment (M5). This sequence relies on foundational programming skills from CSE201 and gradually builds toward complex multi-agent architectures.
- **assessment rationale:** The assessment scheme combines quizzes (10%), assignments (20%), a project (25%), midsem (20%), and endsem (25%). This mix balances theoretical comprehension with practical competencies such as implementing agent skills, evaluating reliability, and executing live scenarios as specified by the course outcomes.
- **positioning rationale:** While CSE701 investigates repository mining and machine learning models for software engineering, and CSE594A focuses on agentic reasoning for mathematical problems, this course targets practical workflow-oriented design of agentic software development and coding agents. Other courses such as CSE582, CSE581, AI501, CSE201, CSE665, and CSE583 address traditional evolution, classical systems analysis, machine learning theory, manual unit testing, or open-source tools rather than AI-native agentic software factories.