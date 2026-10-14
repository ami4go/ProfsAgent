# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `cs601-02` · generated deterministically from the design graph · validator status: **4 errors, 58 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | 'Advanced undergraduate' is not a direct integer value for 'level'. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-COMMON, BTECH-CSE, BTECH-CSAI, MTECH-CSE · years [3, 4] |

## 3. Course description

The course introduces AI-native software development where developers collaborate with coding agents. It examines how to define intent, provide effective model context, and structure workflows that integrate AI tools. Students will learn to configure agent‑assisted environments, translate unstructured requirements into executable specifications, analyse execution traces to diagnose failures, and assess automated testing pipelines against reliability criteria. Instruction combines lectures with laboratory sessions and a semester‑long project, enabling hands‑on practice of workflow design, tool integration, and reliable deployment.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 (or CSE600A) `[CATALOGUE]` | Unit testing using JUnit, version controlling and collaboration, Object Oriented Paradigm | Students require solid software engineering fundamentals, source code control, and unit testing frameworks to effectively evaluate and integrate AI-assisted coding outputs. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in Software Engineering focusing on data-driven methods, bug prediction, and mining repositories, the new course 'Software Development using AI' focuses specifically on modern AI-native developer workflows, coding agents, tool use, and agentic software engineering.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4), ceilings raised to BL4+ for the IIIT-D template rule; to be refit from corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (BL3, procedural) — Configure AI-assisted coding agents and tool integrations using model context protocols, for a given development environment, such that all public integration tests pass and no configuration warnings are reported.** `[CORPUS, USER]`  
verb *configure* · behaviour *AI-assisted coding agents and tool integrations using model context protocols* · condition *for a given development environment* · degree *such that all public integration tests pass and no configuration warnings are reported* · evidence: programming_assignment, lab_task · marks share (computed): 30.07%

- CO1.LO1 (L1) Identify the configuration schema and protocol requirements for model context protocols in a supplied developer workspace template.
- CO1.LO2 (L3 ★capstone) Configure custom tool integrations within agent workspaces using model context protocols, with all public tests passing and no warnings from the configured static analyser.
- CO1.LO3 (L1) Identify the core components of developer workflows and AI-assisted coding using contextualisation guidelines for {n} of {m} short items.

**CO2 (BL3, procedural) — Translate unstructured product requirements into executable specifications, using spec-driven development frameworks, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *translate* · behaviour *executable specifications from unstructured product requirements* · condition *using spec-driven development frameworks* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 19.93%

- CO2.LO1 (L2) Outline use cases and system boundaries from unstructured product descriptions using spec-driven development guidelines.
- CO2.LO2 (L3 ★capstone) Translate module requirements into executable specifications using spec-driven development frameworks, meeting the stated interface specification for every public method.
- CO2.LO3 (L2) Outline use cases and system boundaries from unstructured product descriptions using standards and specification guidelines for {n} of {m} short items.

**CO3 (BL4, procedural) — Analyze the execution traces produced by coding agents during iterative loop engineering tasks, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *analyze* · behaviour *execution traces and generated code produced by coding agents during iterative loop engineering tasks* · condition *for a supplied software artifact of at most 5000 lines* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, code_review · marks share (computed): 22.0%

- CO3.LO1 (L2) Trace execution logs produced by coding agents during iterative loop engineering tasks, recording all control-flow steps across the log artifact.
- CO3.LO2 (L4 ★capstone) Analyze execution traces produced by coding agents during iterative loop engineering tasks, for a supplied log file of at most 2000 lines, identifying at least three distinct failure causes with supporting log evidence.
- CO3.LO3 (L4) Examine iterative development logs and software factory outputs, identifying at least 2 of the 4 seeded defects, with a proposed fix for each.

**CO4 (BL5, procedural) — Assess automated testing and evaluation pipelines for AI-native software factories, justifying each design decision against at least one stated reliability requirement.** `[CORPUS, USER]`  
verb *assess* · behaviour *automated testing and evaluation pipelines for AI-native software factories* · condition *for a supplied multi-component software project* · degree *justifying each design decision against at least one stated reliability requirement* · evidence: project_deliverable, design_document · marks share (computed): 28.0%

- CO4.LO1 (L2) Compare automated testing mechanisms and evaluation metrics for AI-native software architectures.
- CO4.LO2 (L5 ★capstone) Assess automated testing pipelines for AI-native software factories, for a supplied multi-component software project, justifying each design decision against at least one stated reliability requirement.
- CO4.LO3 (L5) Evaluate deployment and reliability metrics for a supplied multi-component software project, demonstrating live, with 2 scenario walkthroughs chosen by the evaluator.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Developer workflows and AI-assisted coding (M1.T1)<br>Model context protocols and architecture (M1.T2) | CO1.LO1, CO1.LO3 | CO1 | Group discussion on developer workflow components; list 5 items. |  |
| 2 | Model context protocols and architecture (M1.T2)<br>Coding agents and context engineering (M2.T1) | CO1.LO1, CO1.LO2 | CO1 | Case‑study analysis of model context protocols; design a schema on whiteboard. |  |
| 3 | Coding agents and context engineering (M2.T1)<br>Custom tool integrations using model context protocols (M2.T2) | CO1.LO2 | CO1 | Peer review of custom tool integration code snippets; identify two improvement points. | A:Quiz1 (quiz) |
| 4 | Custom tool integrations using model context protocols (M2.T2)<br>Standards and specification guidelines for use cases (M3.T1)<br>Software requirements and requirements engineering (M3.T2) | CO1.LO2, CO2.LO1, CO2.LO3 | CO1, CO2 | Mini‑quiz on standards and specification guidelines; 5 short answer questions. | A:Assign1 released |
| 5 | Software requirements and requirements engineering (M3.T2)<br>Spec-driven development frameworks (M4.T1) | CO2.LO1, CO2.LO2 | CO2 | Design a simple spec‑driven module; outline interfaces in pairs. |  |
| 6 | Spec-driven development frameworks (M4.T1)<br>Requirements to executable specifications and code generation (M4.T2) | CO2.LO2 | CO2 | Walkthrough of generated code from specifications; spot mismatches. | A:Assign1 due; A:Assign2 released |
| 7 | Requirements to executable specifications and code generation (M4.T2)<br>Iterative development and loop engineering (M5.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Analyze loop‑engineering logs; identify one control‑flow anomaly. | A:Assign3 released; A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Iterative development and loop engineering (M5.T1)<br>Iterative development logs and software factory outputs (M5.T2) | CO3.LO1, CO3.LO3 | CO3 | Group defect‑hunt on iterative logs; each team reports two defects. | A:Assign2 due; A:ProjMilestone released |
| 9 | Software factories and execution trace analysis (M6.T1)<br>Testing and validation in iterative development (M6.T2) | CO3.LO2 | CO3 | Trace‑analysis problem set; students list three failure causes per log sample. | A:Assign3 due |
| 10 | Testing and validation in iterative development (M6.T2)<br>Automated testing and evaluation mechanisms (M7.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Design a test plan for iterative development artifact; present in pairs. | A:LabEval1 released |
| 11 | Automated testing and evaluation mechanisms (M7.T1)<br>Pipeline evaluation mechanisms and metrics (M7.T2)<br>Reliable and safe trustworthy software architectures (M8.T1) | CO4.LO1, CO4.LO2 | CO4 | Debate on automated testing metrics; each student defends one metric. |  |
| 12 | Reliable and safe trustworthy software architectures (M8.T1)<br>Deployment and reliability metric evaluation (M8.T2) | CO4.LO2, CO4.LO3 | CO4 | Scenario‑based discussion of reliability requirements for a project. | A:LabEval1 due; A:ProjMilestone due |
| 13 | Deployment and reliability metric evaluation (M8.T2) | CO4.LO3 | CO4 | Reflective session on deployment metrics; students propose one improvement. | A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 3 | **Custom tool integration lab** — Implement a custom tool integration using model context protocols and verify all tests pass. | CO1.LO2 | Student development machines, AI coding tools/APIs |
| 4 | **Hands‑on reinforcement lab** — Extend the previous integration, adding error handling and logging. | CO1.LO2 | Student development machines, AI coding tools/APIs |
| 5 | **Spec‑driven practice lab** — Create a simple spec‑driven module based on earlier requirements and generate skeleton code. | CO1.LO2 | Student development machines, software development environments |
| 6 | **Executable specification lab** — Translate given module requirements into executable specifications and run code generation. | CO2.LO2 | Student development machines, software development environments |
| 7 | **Iterative loop engineering lab** — Run an iterative development loop, capture logs, and annotate control‑flow steps. | CO3.LO1 | Student development machines, TA support |
| 8 | **Defect identification lab** — Analyse iterative development logs to locate seeded defects and propose fixes. | CO3.LO3 | Student development machines, TA support |
| 9 | **Trace analysis lab** — Examine execution traces, identify three failure causes and document evidence. | CO3.LO2 | Student development machines, TA support |
| 10 | **Testing pipeline lab** — Apply testing and validation techniques to an iterative development artifact. | CO3.LO2 | Student development machines, TA support |
| 11 | **Reliability assessment lab** — Assess an AI‑native testing pipeline against reliability requirements and justify decisions. | CO4.LO2 | Student development machines, AI coding tools/APIs |
| 12 | **Deployment metrics lab** — Evaluate deployment and reliability metrics for a multi‑component project with live walkthroughs. | CO4.LO3 | Student development machines, AI coding tools/APIs |
| 13 | **Final reliability lab** — Perform a second reliability scenario walkthrough, focusing on metric interpretation. | CO4.LO3 | Student development machines, AI coding tools/APIs |

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3) | — | theory, written-communication, research-investigation |  |
| assignment | 20.0 | A:Assign1 (W4→W6), A:Assign2 (W6→W8), A:Assign3 (W7→W9) | — | implement, design, tool-use, evaluate-critique, written-communication, research-investigation |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, evaluate-critique, theory |  |
| lab | 10.0 | A:LabEval1 (W10→W12) | — | analyse-data, evaluate-critique, tool-use, research-investigation, implement | The lab component focuses on practical application and skill development, which is adequately covered by a 10% weight in conjunction with other hands-on assignments. |
| project | 10.0 | A:ProjMilestone (W8→W12) | — | design, evaluate-critique, written-communication, tool-use, research-investigation | The project component, while significant, is balanced with other substantial assignments, allowing for a 10% weight to assess key capstone learning outcomes. |
| endsem | 30.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique, theory, written-communication |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 30.07%, CO2 19.93%, CO3 22.0%, CO4 28.0%

## 10. Resource material

Policy: **mixed** — Because AI-assisted software development and agentic workflows are rapidly evolving domains, the course utilizes a mix of specialized reference books, framework documentation, and recent research papers alongside standard reference literature.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reading | Yujia Li, David Choi, Junyoung Chung, Nate Kushman (2022). *Competition-level code generation with AlphaCode*. | 10.1126/science.abq1158 | yes | M4.T2, M6.T1 |
| reading | Andrii Tkachuk (2026). *SPECIFICATION-DRIVEN DEVELOPMENT AS STRUCTURED APPROACH FOR SOURCE CODE GENERATION*. | 10.52058/2786-6025-2026-4(58)-2631-2644 | yes | M4.T1 |
| reading | Anthony Shaw, Amin Beheshti (2026). *Complexity Backpressure for AI Coding Agents: A Cross-Model Study on Substantive Software Tasks*. | 10.1109/sse72781.2026.00047 | yes | M7.T2 |
| reference | S. Lakshmi, D. Helen, G. Sambasivam (2025). *8 Redefining and Transforming Software Development with Generative AI*. | 10.1515/9783111677798-008 | yes | M6.T1 |
| reading | Fareedh Basha (2026). *Query Tuning Framework Using the Model Context Protocol for Workflows*. | 10.2139/ssrn.6172059 | yes | M1.T2, M2.T2 |
| reading | Yeswanth Kumar Polishetty (2026). *Autonomous Coding Agents for Software Development Testing and Debugging*. | 10.2139/ssrn.7515638 | yes | M2.T1, M6.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO1 | PO2 | PO3 | PO4 | PO5 | PO10 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PO1 | PO2 | PO3 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PSO8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CO1 | 3 [1] | 3 [1] | 1 [unclaimed] | 3 [unclaimed] | 1 [3] | 2 [unclaimed] | 3 [1] | 3 [unclaimed] | 2 [unclaimed] | 3 [3] | 1 [2] | 3 [1] | 3 [unclaimed] | 1 [2] | 3 [unclaimed] | 1 [2] | 2 [1] | 2 [1] | – [1] | 3 [1] | 2 [unclaimed] | 3 [2] | 1 [3] | 2 [unclaimed] | 2 [unclaimed] |
| CO2 | 2 [unclaimed] | 3 [2] | 3 [3] | 3 [unclaimed] | 3 [unclaimed] | 3 [2] | 2 [1] | 2 [unclaimed] | 2 [2] | 3 [3] | 3 [unclaimed] | 2 [1] | 2 [unclaimed] | 3 [2] | 3 [2] | 3 [unclaimed] | 3 [2] | 3 [2] | – [1] | 2 [unclaimed] | 2 [2] | 3 [3] | 3 [unclaimed] | 3 [unclaimed] | 3 [2] |
| CO3 | 2 [1] | 3 [3] | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [unclaimed] | 2 [1] | 2 [unclaimed] | 3 [2] | 3 [2] | 2 [unclaimed] | 2 [1] | 2 [unclaimed] | 2 [unclaimed] | 3 [3] | 2 [2] | 2 [3] | 2 [1] | – [2] | 2 [1] | 3 [2] | 3 [unclaimed] | 2 [unclaimed] | 2 [2] | 2 [unclaimed] |
| CO4 | 3 [unclaimed] | 3 [2] | 2 [3] | 3 [unclaimed] | 2 [unclaimed] | 3 [2] | 3 [1] | 3 [unclaimed] | 3 [unclaimed] | 3 [3] | 2 [2] | 3 [1] | 3 [unclaimed] | 2 [unclaimed] | 3 [2] | 2 [2] | 2 [2] | 3 [2] | – [2] | 3 [unclaimed] | 3 [unclaimed] | 3 [3] | 2 [2] | 2 [unclaimed] | 3 [2] |

PO legend: PO1 = PO1; PO2 = PO2; PO3 = PO3; PO4 = PO4; PO5 = PO5; PO10 = PO10; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PO1 = PO1; PO2 = PO2; PO3 = PO3; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PSO8 = PSO8

- CO1→PO5: Configuring AI-assisted coding agents and tool integrations directly exercises modern engineering and IT tool usage. (activities: tool-use, implement)
- CO1→PO1: Basic engineering principles are applied when configuring development environments and integration tests. (activities: implement)
- CO1→PO2: Addressing integration test failures requires minor analytical reasoning. (activities: implement)
- CO1→PSO4: Configuration of coding agents implements tool-based application support. (activities: implement, tool-use)
- CO1→PSO5: Uses advanced model context protocols and coding agent integrations. (activities: tool-use)
- CO1→PSO1: Touches upon protocol foundations. (activities: implement)
- CO1→PSO3: Implementing agent tool integrations aligns with algorithmic problem solving. (activities: implement)
- CO1→PSO5: Configuring AI coding agents applies AI behaviors. (activities: tool-use)
- CO1→PSO1: Applies AI-related foundational concepts. (activities: implement)
- CO1→PO1: Development work involves configuring coding environments. (activities: implement)
- CO1→PO2: Reporting test outcomes satisfies documentation aspects. (activities: implement)
- CO1→PO3: Demonstrates baseline specialization mastery. (activities: implement)
- CO1→PSO4: Directly employs advanced AI tooling techniques. (activities: tool-use, implement)
- CO1→PSO3: Develops environment configurations. (activities: implement)
- CO1→PSO1: Touches upon protocol limits. (activities: implement)
- CO2→PO3: Translating unstructured requirements into executable specifications constitutes designing software system specifications. (activities: design, implement)
- CO2→PO2: Requires analyzing unstructured requirements to formulate technical specs. (activities: design)
- CO2→PO10: Producing executable specifications entails writing comprehensive design documentation. (activities: written-communication)
- CO2→PSO4: Spec-driven development frameworks are modern methodologies for designing applications. (activities: design, implement)
- CO2→PSO3: Adapts development frameworks to new product requirements. (activities: design)
- CO2→PSO1: Formal specifications touch upon theoretical limits of systems. (activities: design)
- CO2→PSO3: Designing executable specifications involves structured problem solving. (activities: design)
- CO2→PSO4: Models product requirements computationally. (activities: design)
- CO2→PSO1: Applies foundational computer science modeling concepts. (activities: design)
- CO2→PO1: Carries out independent specification development. (activities: design)
- CO2→PO2: Writing complete executable specifications serves as technical documentation. (activities: written-communication)
- CO2→PO3: Demonstrates methodology mastery. (activities: design)
- CO2→PSO3: Designs and develops executable system specifications from requirements. (activities: design, implement)
- CO2→PSO2: Adapts requirements engineering models. (activities: design)
- CO2→PSO8: Communicates requirements via clear executable documentation. (activities: written-communication)
- CO3→PO4: Analyzing execution traces and log evidence to identify failure causes constitutes rigorous data analysis and investigation. (activities: analyse-data, evaluate-critique)
- CO3→PO2: Reaching substantiated conclusions on agent failures requires deep problem analysis. (activities: analyse-data, evaluate-critique)
- CO3→PO1: Applies software engineering fundamentals during trace inspection. (activities: analyse-data)
- CO3→PSO3: Uses trace analysis techniques to solve debugging problems. (activities: analyse-data)
- CO3→PSO4: Evaluates computer-based system performance via execution traces. (activities: evaluate-critique)
- CO3→PSO1: Execution traces reflect computing runtime limitations. (activities: analyse-data)
- CO3→PSO4: Analyzing AI agent traces is a direct application of computational and AI problem analysis. (activities: analyse-data, evaluate-critique)
- CO3→PSO1: Touches upon AI agent foundations. (activities: analyse-data)
- CO3→PSO5: Analyzes iterative AI agent behaviors. (activities: analyse-data)
- CO3→PO1: Investigates practical engineering failures independently using logs. (activities: analyse-data, evaluate-critique)
- CO3→PO3: Demonstrates advanced diagnostic mastery. (activities: analyse-data)
- CO3→PO2: Log evidence contributes to technical reporting. (activities: written-communication)
- CO3→PSO5: Investigates cutting-edge AI coding agent traces. (activities: analyse-data)
- CO3→PSO2: Adapts analysis techniques to software traces. (activities: analyse-data)
- CO3→PSO1: Traces expose computing limits. (activities: analyse-data)
- CO4→PO3: Assessing and designing automated testing and evaluation pipelines directly addresses system-level design solutions. (activities: design, evaluate-critique)
- CO4→PO2: Justifying pipeline decisions requires analyzing reliability requirements. (activities: evaluate-critique)
- CO4→PO10: Documenting design justifications requires effective professional communication. (activities: written-communication)
- CO4→PSO4: Evaluating testing pipelines for AI-native software factories targets application evaluation needs. (activities: evaluate-critique, design)
- CO4→PSO5: Applies advanced techniques for AI software factories. (activities: design)
- CO4→PSO1: Reliability requirements touch upon theoretical computing limits. (activities: evaluate-critique)
- CO4→PSO4: Assesses AI-native system pipelines. (activities: evaluate-critique)
- CO4→PSO5: Applies AI evaluation concepts to software factories. (activities: design)
- CO4→PSO1: Touches upon AI systems foundations. (activities: design)
- CO4→PO1: Carries out investigation into testing pipelines. (activities: evaluate-critique)
- CO4→PO2: Writing design justifications aligns with technical reporting. (activities: written-communication)
- CO4→PO3: Demonstrates advanced specialization mastery in AI systems. (activities: design)
- CO4→PSO3: Evaluates testing pipelines for novel AI-native software factories. (activities: evaluate-critique, design)
- CO4→PSO4: Uses advanced testing and evaluation tooling. (activities: design)
- CO4→PSO8: Communicates design rationales clearly. (activities: written-communication)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T2 | 1, 2 | A:Quiz1@L1, A:Midsem@L1 |
| CO1.LO2 | L3 | M2.T1, M2.T2 | 2, 3, 4 | A:Assign1@L3, A:Midsem@L3 |
| CO2.LO1 | L2 | M3.T2 | 4, 5 | A:Assign2@L2 |
| CO2.LO2 | L3 | M4.T1, M4.T2 | 5, 6, 7 | A:Assign3@L3, A:Midsem@L3 |
| CO3.LO1 | L2 | M5.T1 | 7, 8 | A:LabEval1@L2 |
| CO3.LO2 | L4 | M6.T1, M6.T2 | 9, 10 | A:LabEval1@L4, A:Endsem@L4 |
| CO4.LO1 | L2 | M7.T1, M7.T2 | 10, 11 | A:ProjMilestone@L2, A:Endsem@L2 |
| CO4.LO2 | L5 | M8.T1 | 11, 12 | A:ProjMilestone@L5 |
| CO1.LO3 | L1 | M1.T1 | 1 | A:Quiz1@L1 |
| CO2.LO3 | L2 | M3.T1 | 4 | A:Assign2@L2 |
| CO3.LO3 | L4 | M5.T2 | 8 | A:LabEval1@L4 |
| CO4.LO3 | L5 | M8.T2 | 12, 13 | A:Endsem@L5 |

## Appendix C — Modules and topics

**M1 AI-Assisted Coding and Developer Workflows** (primary CO1)
- M1.T1 Developer workflows and AI-assisted coding — 2.0 h · LOs CO1.LO3
- M1.T2 Model context protocols and architecture — 3.0 h · LOs CO1.LO1 · requires M1.T1
**M2 Agent Workspaces and Tool Integrations** (primary CO1)
- M2.T1 Coding agents and context engineering — 2.0 h · LOs CO1.LO2 · requires M1.T2
- M2.T2 Custom tool integrations using model context protocols — 2.5 h · LOs CO1.LO2 · requires M2.T1
**M3 Requirements and Specification-Driven Development** (primary CO2)
- M3.T1 Standards and specification guidelines for use cases — 2.0 h · LOs CO2.LO3
- M3.T2 Software requirements and requirements engineering — 3.0 h · LOs CO2.LO1 · requires M3.T1
**M4 Executable Specifications and Code Generation** (primary CO2)
- M4.T1 Spec-driven development frameworks — 2.0 h · LOs CO2.LO2 · requires M3.T2
- M4.T2 Requirements to executable specifications and code generation — 2.5 h · LOs CO2.LO2 · requires M4.T1
**M5 Iterative Loop Engineering and Tracing** (primary CO3)
- M5.T1 Iterative development and loop engineering — 3.0 h · LOs CO3.LO1
- M5.T2 Iterative development logs and software factory outputs — 2.0 h · LOs CO3.LO3 · requires M5.T1
**M6 Diagnostic Log Analysis and Software Factories** (primary CO3)
- M6.T1 Software factories and execution trace analysis — 2.5 h · LOs CO3.LO2 · requires M5.T2
- M6.T2 Testing and validation in iterative development — 2.0 h · LOs CO3.LO2 · requires M6.T1
**M7 Automated Testing and Evaluation Metrics** (primary CO4)
- M7.T1 Automated testing and evaluation mechanisms — 1.75 h · LOs CO4.LO1
- M7.T2 Pipeline evaluation mechanisms and metrics — 1.75 h · LOs CO4.LO1 · requires M7.T1
**M8 Reliable AI-Native Pipelines and Deployment** (primary CO4)
- M8.T1 Reliable and safe trustworthy software architectures — 2.5 h · LOs CO4.LO2 · requires M7.T1
- M8.T2 Deployment and reliability metric evaluation — 2.0 h · LOs CO4.LO3 · requires M8.T1

Schedule: feasible · 36.5 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.032 | complementary | CSE701 examines data and machine learning models applied to software engineering tasks such as defect prediction and repository mining, whereas the new course focuses on interactive, agent-assisted workflows, prompt/context engineering, and coding agents. |
| CSE594A | 0.08 | complementary | CSE594A concentrates broadly on agentic reasoning and algorithmic/mathematical problem solving using LLMs, whereas the new course specifically addresses software engineering lifecycles, developer workflows, testing, and deployment using AI agents. |
| CSE600 | 0.021 | superficial | CSE600 is a core C++ programming language course covering syntax, templates, and basic testing, while the new course focuses entirely on AI-driven software development workflows and agentic tool integration. |

Overlap method: neo4j: Jaccard over embedding-matched topic phrases (all-MiniLM-L6-v2, cos ≥ 0.66), no IDF

**Comparable courses**

- **EXT:STANFORD/CS146S** CS 146S The Modern Software Developer — Stanford University, <https://explorecourses.stanford.edu/search?q=CS146S>. Take: Incorporate hands-on modules exploring how AI tools such as new-age IDEs, terminals, and code review platforms transform the software development life cycle. Avoid: Avoid excessive emphasis on general introductory programming or non-software workflows.
- **EXT:STANFORD/EE292M** EE 292M AI-Augmented Research and Development: Foundations and Practice — Stanford University, <https://explorecourses.stanford.edu/search?q=EE292M>. Take: Adopt evaluation frameworks and agentic system design patterns for detecting and analyzing AI tool failures during software creation. Avoid: Avoid overly theoretical discussions of large language model training that stray from software engineering applications.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Reference agentic protocols like MCP (Model Context Protocol) and agent reasoning concepts when introducing agentic software engineering and tool use. Avoid: Avoid deep dives into algorithmic and mathematical problem-solving agents that do not relate to software development processes.

External pages examined and rejected: 5 (e.g. https://nusmods.com/courses/CP1008 → relevance=low; https://nusmods.com/courses/CS2103DE → relevance=low; https://nusmods.com/courses/CS2113 → relevance=low; https://nusmods.com/courses/CS2103 → relevance=low; https://nusmods.com/courses/AI5202 → relevance=low)

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| assessment | V23 | error | CO1, MTECH-CSE/PO3 | CO1→MTECH-CSE/PO3 claimed (provisional 1) but no assessed activity evidences it |
| assessment | V23 | error | CO2, MTECH-CSE/PO3 | CO2→MTECH-CSE/PO3 claimed (provisional 1) but no assessed activity evidences it |
| assessment | V23 | error | CO3, MTECH-CSE/PO3 | CO3→MTECH-CSE/PO3 claimed (provisional 2) but no assessed activity evidences it |
| assessment | V23 | error | CO4, MTECH-CSE/PO3 | CO4→MTECH-CSE/PO3 claimed (provisional 2) but no assessed activity evidences it |
| assessment | V23 | warning | CO1, BTECH-COMMON/PO1 | CO1→BTECH-COMMON/PO1: provisional 1 vs computed 3 (share 0.778) |
| assessment | V23 | warning | CO1, BTECH-COMMON/PO2 | CO1→BTECH-COMMON/PO2: provisional 1 vs computed 3 (share 0.667) |
| assessment | V23 | warning | CO1, BTECH-COMMON/PO5 | CO1→BTECH-COMMON/PO5: provisional 3 vs computed 1 (share 0.222) |
| assessment | V23 | warning | CO1, BTECH-CSAI/PSO1 | CO1→BTECH-CSAI/PSO1: provisional 1 vs computed 3 (share 0.778) |
| assessment | V23 | warning | CO1, BTECH-CSE/PSO1 | CO1→BTECH-CSE/PSO1: provisional 1 vs computed 3 (share 0.778) |
| assessment | V23 | warning | CO1, MTECH-CSE/PSO1 | CO1→MTECH-CSE/PSO1: provisional 1 vs computed 3 (share 0.778) |
| assessment | V23 | warning | CO1, MTECH-CSE/PSO4 | CO1→MTECH-CSE/PSO4: provisional 3 vs computed 1 (share 0.222) |
| assessment | V23 | warning | CO4, BTECH-CSAI/PSO1 | CO4→BTECH-CSAI/PSO1: provisional 1 vs computed 3 (share 0.643) |
| assessment | V23 | warning | CO4, BTECH-CSE/PSO1 | CO4→BTECH-CSE/PSO1: provisional 1 vs computed 3 (share 0.643) |
| assessment | VA-PROJ | warning | project | project released in week 8, late in a 13-week semester |
| copo | T4 | warning | CO2, MTECH-CSE | CO2 maps to 6 outcomes of MTECH-CSE; keep only the strong links |
| copo | T4 | warning | CO1, MTECH-CSE | CO1 maps to 6 outcomes of MTECH-CSE; keep only the strong links |
| copo | T4 | warning | CO3, MTECH-CSE | CO3 maps to 6 outcomes of MTECH-CSE; keep only the strong links |
| copo | T4 | warning | CO4, MTECH-CSE | CO4 maps to 6 outcomes of MTECH-CSE; keep only the strong links |
| copo | VCOPO-ACT | warning | CO1, BTECH-COMMON/PO1 | CO1→BTECH-COMMON/PO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO1, BTECH-COMMON/PO2 | CO1→BTECH-COMMON/PO2: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO1, BTECH-CSE/PSO1 | CO1→BTECH-CSE/PSO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO1, BTECH-CSAI/PSO5 | CO1→BTECH-CSAI/PSO5: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO1, BTECH-CSAI/PSO1 | CO1→BTECH-CSAI/PSO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO1, MTECH-CSE/PO1 | CO1→MTECH-CSE/PO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO1, MTECH-CSE/PO2 | CO1→MTECH-CSE/PO2: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO1, MTECH-CSE/PO3 | CO1→MTECH-CSE/PO3: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO1, MTECH-CSE/PSO1 | CO1→MTECH-CSE/PSO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO2, BTECH-COMMON/PO2 | CO2→BTECH-COMMON/PO2: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO2, BTECH-CSE/PSO3 | CO2→BTECH-CSE/PSO3: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO2, BTECH-CSE/PSO1 | CO2→BTECH-CSE/PSO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO2, BTECH-CSAI/PSO4 | CO2→BTECH-CSAI/PSO4: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO2, BTECH-CSAI/PSO1 | CO2→BTECH-CSAI/PSO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO2, MTECH-CSE/PO1 | CO2→MTECH-CSE/PO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO2, MTECH-CSE/PO3 | CO2→MTECH-CSE/PO3: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO2, MTECH-CSE/PSO2 | CO2→MTECH-CSE/PSO2: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO3, BTECH-COMMON/PO1 | CO3→BTECH-COMMON/PO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO3, BTECH-CSE/PSO1 | CO3→BTECH-CSE/PSO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO3, BTECH-CSAI/PSO1 | CO3→BTECH-CSAI/PSO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO3, BTECH-CSAI/PSO5 | CO3→BTECH-CSAI/PSO5: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO3, MTECH-CSE/PO1 | CO3→MTECH-CSE/PO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO3, MTECH-CSE/PO3 | CO3→MTECH-CSE/PO3: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO3, MTECH-CSE/PSO5 | CO3→MTECH-CSE/PSO5: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO3, MTECH-CSE/PSO1 | CO3→MTECH-CSE/PSO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO4, BTECH-CSE/PSO5 | CO4→BTECH-CSE/PSO5: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO4, BTECH-CSE/PSO1 | CO4→BTECH-CSE/PSO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO4, BTECH-CSAI/PSO1 | CO4→BTECH-CSAI/PSO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO4, MTECH-CSE/PO1 | CO4→MTECH-CSE/PO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO4, MTECH-CSE/PO3 | CO4→MTECH-CSE/PO3: none of its evidencing activities maps to that PO, so its strength can never be computed |
| copo | VCOPO-ACT | warning | CO4, MTECH-CSE/PSO4 | CO4→MTECH-CSE/PSO4: none of its evidencing activities maps to that PO, so its strength can never be computed |
| cos | V11 | warning | CO3 | CO CO3 condition is not visible in the statement text |
| cos | V11 | warning | CO4 | CO CO4 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO2 | LO CO2.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO2 | LO CO3.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO3 | LO CO3.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO3 | LO CO4.LO3 degree is not visible in the statement text |
| resources | V15 | warning |  | 2 resource(s) removed because no library record matched: Gullí, Antonio. "Agentic Design Patterns." Springer, 2025; OpenAI MCP, Agent2Agent (A2A) Protocol |

**Repair history**

- cos: errors 3 → 0 · round 1 accepted (3→0)
- los: errors 6 → 0 · round 1 accepted (6→2); round 2 accepted (2→0)
- structure: errors 1 → 0 · round 1 accepted (1→0)
- assessment: errors 16 → 4 · round 1 accepted (16→6); round 2 accepted (6→5); round 3 accepted (5→4)

**Model-reported concerns (not validated; for the professor's attention)**

- copo: activity_po_map review: Some mapped activities rely on activity_po_map links that must be confirmed against the upcoming assessment plan to ensure computed strengths match provisional predictions.
- los: hours_total: Sum of LO lecture (32), tutorial (10), and lab (18) hours falls below the course budget (39/13/26). Unallocated hours can be distributed for review and project milestones during syllabus scheduling.

## Appendix F — Rationales (G11)

- **sequencing rationale:** Modules progress from foundational AI‑assisted coding concepts (M1) to tool integration (M2), then to specification‑driven development (M3, M4). Subsequent modules address iterative loop engineering (M5, M6) before culminating in testing, evaluation, and reliable pipeline design (M7, M8), reflecting prerequisite dependencies among topics.
- **assessment rationale:** The blend of quizzes, assignments, labs, and a project aligns with the four COs, providing formative checks for configuration skills, specification translation, trace analysis, and testing pipeline assessment, while the weighted end‑semester exam evaluates integrated understanding.
- **positioning rationale:** Unlike CSE701, which focuses on data‑driven defect prediction, and CSE594A, which emphasizes generic LLM reasoning, this course uniquely targets interactive, agent‑assisted software engineering workflows and reliable AI‑native pipelines.