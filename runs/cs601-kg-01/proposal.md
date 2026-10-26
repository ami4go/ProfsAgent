# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `cs601-kg-01` · generated deterministically from the design graph · validator status: **58 errors, 132 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Advanced undergraduate corresponds to a 300-level course (3rd year standing).; Advanced undergraduate corresponds to a 400-level course (4th year elective standing). | professor |
| — | ambiguous: curriculum_context | — | The text is an overarching narrative intended as the answer to Q1 (course positioning).; The text is an unpartitioned block intended to address multiple standard curriculum questions (Q1–Q6) simultaneously without explicit section labels. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-COMMON, BTECH-CSE, BTECH-CSAI, MTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with coding agents. It covers agent orchestration and environments, requirements and spec-driven development, workflow inspection and loop engineering, and AI-native workflows and software factories. Designed for senior undergraduate students in computer science, the course requires prerequisite knowledge of unit testing, object-oriented development, and version control. Upon completing the course, students will be able to configure AI coding agents and development environments, formulate executable specifications from natural language requirements, analyze execution traces from iterative workflows to identify failure causes, and design AI-native software development workflows for multi-module applications. The course is taught through a combination of lectures, tutorials, and practical laboratory sessions.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 (or CSE600A) `[CATALOGUE]` | Unit testing using JUnit, Object oriented development process, version controlling and collaboration | Students must know advanced programming, testing, and version control to effectively collaborate with coding agents and build software. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE594A covers agentic reasoning and mentions coding agents briefly, its primary focus is on algorithmic and mathematical problem-solving rather than software development workflows, agent-assisted software engineering, and production practices. The new course is distinct.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4), ceilings raised to BL4+ for the IIIT-D template rule; to be refit from corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (BL3, procedural) — Configure AI coding agents and development environments, using agent orchestration frameworks and supplied tool specifications, such that at least 80% of the provided test cases pass.** `[CORPUS, USER]`  
verb *configure* · behaviour *AI coding agents and development environments* · condition *using agent orchestration frameworks and supplied tool specifications* · degree *such that at least 80% of the provided test cases pass* · evidence: programming_assignment, lab_task · marks share (computed): 36.33%

- CO1.LO1 (L3) Configure an agent orchestration framework on a supplied development machine using provided environment parameters and extension lists.
- CO1.LO2 (L3) Apply custom tool specifications into an active coding agent session for a supplied task description.
- CO1.LO3 (L3 ★capstone) Operate configured AI coding agents and environments to implement a supplied module
- CO1.LO4 (L3) Configure environment parameters and extension lists for an agent orchestration framework.

**CO2 (BL5, conceptual) — Formulate executable specifications from natural language requirements documents, using spec-driven development practices, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *formulate* · behaviour *executable specifications from natural language requirements documents* · condition *using spec-driven development practices* · degree *covering every use case in the supplied requirements document* · evidence: design_document, project_deliverable · marks share (computed): 25.17%

- CO2.LO1 (L2) Identify use cases from a supplied natural language requirements document for a single component.
- CO2.LO2 (L5 ★capstone) Formulate executable specifications for one isolated feature from a supplied requirements document, using spec-driven development practices.

**CO3 (BL4, procedural) — Analyze execution traces from coding agents during iterative workflows, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *analyze* · behaviour *execution traces from coding agents during iterative workflows* · condition *using workflow inspection logs* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, code_review · marks share (computed): 18.5%

- CO3.LO1 (L4) Inspect workflow inspection logs from a coding agent execution session to trace step-by-step execution.
- CO3.LO2 (L4 ★capstone) Examine execution traces from coding agents during iterative workflows using workflow inspection logs, identifying at least three distinct failure causes with supporting log evidence.

**CO4 (BL5, metacognitive) — Design an AI-native software development workflow for a multi-module application, justifying each design decision against at least one stated requirement for reliability and automation.** `[CORPUS, USER]`  
verb *design* · behaviour *an AI-native software development workflow for a multi-module application* · condition *for a supplied engineering problem statement* · degree *justifying each design decision against at least one stated requirement for reliability and automation* · evidence: design_document, project_deliverable · marks share (computed): 20.0%

- CO4.LO1 (L5) Select automation tools and reliability components for an AI-native software development workflow.
- CO4.LO2 (L3 ★capstone) Construct the CI/CD integration pipeline component within an AI-native development workflow, justifying its scheduling parameters against the supplied reliability requirements.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Agent orchestration frameworks setup (M1.T1) | CO1.LO1, CO1.LO4 | CO1 | Worked trace-setup and verification of agent orchestration framework configurations in pairs. |  |
| 2 | Development environments configuration (M1.T2) | CO1.LO1, CO1.LO4 | CO1 | Step-by-step peer troubleshooting of development environment configuration errors. |  |
| 3 | Tool use and custom tool specifications (M1.T3) | CO1.LO2 | CO1 | Design exercise formulating custom tool specification JSON schemas for specific API actions. | A:Quiz1 (quiz) |
| 4 | Coding agents and context engineering (M1.T4) | CO1.LO3 | CO1 | Context engineering walkthrough, analyzing prompt injection and context window management for coding agents. | A:Assignment1 released; A:ProjM1 released |
| 5 | Use cases identification from requirements (M2.T1) | CO2.LO1 | CO2 | Group analysis of natural language requirements to extract boundary use cases. |  |
| 6 | Spec-driven development practices (M2.T2) | CO2.LO2 | CO2 | Review and peer critique of executable specifications for isolated features. | A:Quiz2 (quiz); A:Assignment1 due |
| 7 | Iterative development and workflow inspection logs (M3.T1) | CO3.LO1 | CO3 | Trace inspection practice analyzing sample workflow logs from previous agent runs. | A:Midsem (midsem); A:ProjM2 released |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Loop engineering and failure analysis (M3.T2) | CO3.LO2 | CO3 | Worked diagnosis of failing execution traces to identify root-cause failure modes. | A:ProjM1 due |
| 9 | Automated testing and reliability components (M4.T1) | CO4.LO1 | CO4 | Comparative evaluation of automated testing tools for reliability components. | A:Quiz3 (quiz); A:ProjFinal released |
| 10 | Software factories and CI/CD integration pipelines (M4.T2) | CO4.LO2 | CO4 | Mapping reliability requirements to CI/CD pipeline scheduling intervals. |  |
| 11 | CI/CD integration pipelines and deployment automation (M4.T3) | CO4.LO2 | CO4 | Review of pipeline stage configurations and automated deployment scripts. | A:ProjM2 due |
| 12 | Advanced deployment strategies and monitoring (M4.T4) | CO4.LO2 | CO4 | Discussion on monitoring metric thresholds and automated rollback strategies. |  |
| 13 |  |  |  |  | A:ProjFinal due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Agent Orchestration Framework Setup** — Students set up the agent orchestration framework on their assigned development machines using provided environment parameters and extension lists. | CO1.LO1, CO1.LO4 | Student development machines, software development environments |
| 2 | **Development Environments Configuration** — Students configure their development environments, verifying extension lists and parameters for agent frameworks. | CO1.LO1, CO1.LO4 | Student development machines, software development environments |
| 3 | **Custom Tool Specifications** — Students apply custom tool specifications into an active coding agent session for a supplied task description. | CO1.LO2 | Student development machines, access to AI coding tools/APIs |
| 4 | **Coding Agents and Context Engineering** — Students operate configured AI coding agents and environments to implement a supplied module. | CO1.LO3 | Student development machines, access to AI coding tools/APIs |
| 5 | **Use Cases Identification Lab** — Students practice identifying use cases from a natural language requirements document for a single component. | CO2.LO1 | Student development machines |
| 6 | **Spec-Driven Development Practices** — Students formulate executable specifications for an isolated feature from a requirements document using spec-driven development. | CO2.LO2 | Student development machines, software development environments |
| 7 | **Midterm Exam Catch-up / Open Lab** — Open lab session for catch-up and preparation ahead of the mid-semester examination. | CO3.LO1 | Student development machines |
| 8 | **Loop Engineering and Failure Analysis** — Students examine execution traces from coding agents using inspection logs, identifying at least three distinct failure causes. | CO3.LO2 | Student development machines, access to AI coding tools/APIs |
| 9 | **Automated Testing Components** — Students set up and test reliability components for an AI-native software development workflow. | CO4.LO1 | Student development machines, software development environments |
| 10 | **Software Factories and CI/CD Integration** — Students construct CI/CD integration pipeline components within an AI-native development workflow. | CO4.LO2 | Student development machines, software development environments |
| 11 | **CI/CD Deployment Automation** — Students build deployment automation pipelines and justify scheduling parameters against reliability requirements. | CO4.LO2 | Student development machines, software development environments |
| 12 | **Advanced Deployment and Monitoring** — Students implement advanced deployment strategies and monitoring tools for AI-driven development workflows. | CO4.LO2 | Student development machines, access to AI coding tools/APIs |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3), A:Quiz2 (W6→W6), A:Quiz3 (W9→W9) | — | analyse-data |  |
| assignment | 20.0 | A:Assignment1 (W4→W6) | — | implement, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, theory |  |
| project | 25.0 | A:ProjM1 (W4→W8), A:ProjM2 (W7→W11), A:ProjFinal (W9→W13) | — | design, implement, evaluate-critique, teamwork, written-communication |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data, evaluate-critique, theory |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 36.33%, CO2 25.17%, CO3 18.5%, CO4 20.0%

## 10. Resource material

Policy: **mixed** — Because AI-native software development and agentic engineering are fast-moving fields with emerging practices, a combination of specialized reference books, framework documentation, recent research papers, and modern software engineering literature is utilized.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reading | Yujia Li, David Choi, Junyoung Chung, Nate Kushman (2022). *Competition-level code generation with AlphaCode*. | 10.1126/science.abq1158 | yes | M1.T4, M3.T1 |
| reading | Martin Monperrus (2026). *Bootstrapping Coding Agents: The Specification Is the Program*. | 10.1109/ms.2026.3687051 | yes | M2.T2 |
| reading | Prof Dr Oliver Koch (2026). *From Vibe to Value - How Specification-Driven Development Professionalizes AI Coding*. | 10.2139/ssrn.6453101 | yes | M2.T1 |
| reference | Jez Humble, David Farley (2010). *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*. | 9780321670229 | yes | M4.T2, M4.T3 |
| reading | John E. Robert, Ipek Ozkaya, Douglas C. Schmidt (2026). *Transforming Software Engineering and Software Acquisition with Large Language Models*. | 10.1201/9781003492252-7 | yes | M4.T1 |
| reading | Preethika Chandrasekaran, Imron Shajahan, Saran Sankaran, Benjamin Nast (2026). *Large Language Models for Quality Control of Large Language Models*. | 10.5220/0014649700004058 | yes | M4.T1 |
| reading | Samuel Navarro, Manuel Ballarín, Carlos Cetina, Jaime Font (2026). *Large Language Models for Software Models: An Empirical Evaluation in Game Software Engineering*. | 10.2139/ssrn.7009289 | yes | M1.T4 |
| reading | Mark Marron (2026). *Specifications for Humans, Agents, and Tooling: BOSQUE API (BAPI) Tooling*. | 10.1145/3842652.3843194 | yes | M2.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO1 | PO2 | PO3 | PO4 | PO5 | PO6 | PO7 | PO8 | PO9 | PO10 | PO11 | PO12 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PSO6 | PO1 | PO2 | PO3 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PSO6 | PSO7 | PSO8 | PSO9 | PSO10 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CO1 | 2 [1] | 2 [1] | 2 [2] | 2 [1] | 2 [3] | – [1] | – [1] | – [1] | – [1] | – [1] | – [1] | – [2] | 2 [1] | 2 [1] | 2 [1] | 3 [2] | 2 [3] | 2 [2] | 2 [1] | 2 [2] | 2 [1] | 2 [2] | – [1] | – [1] | – [1] | – [1] | 2 [1] | 2 [1] | 3 [2] | 2 [3] | – [1] | – [1] | – [1] | – [1] | – [2] | – [1] |
| CO2 | 2 [1] | 3 [2] | 2 [3] | 3 [1] | 2 [2] | – [1] | – [1] | – [1] | 2 [1] | 2 [2] | – [1] | – [1] | 2 [1] | 2 [1] | 3 [2] | 3 [3] | – [1] | 2 [1] | 2 [1] | 2 [2] | 3 [2] | 2 [2] | – [1] | – [1] | 2 [2] | – [2] | 2 [1] | 3 [1] | 3 [3] | – [1] | – [1] | 2 [1] | – [1] | 2 [2] | – [1] | – [1] |
| CO3 | 2 [1] | 3 [3] | 1 [1] | 3 [3] | 1 [1] | – [1] | – [1] | – [1] | 1 [1] | 1 [2] | – [1] | – [1] | 2 [1] | 2 [2] | 3 [2] | 2 [2] | – [1] | 2 [1] | 2 [2] | 1 [1] | 3 [3] | 1 [1] | – [1] | – [2] | 1 [1] | – [2] | 2 [1] | 3 [2] | 2 [2] | – [1] | – [1] | 1 [1] | – [1] | 1 [1] | – [1] | – [1] |
| CO4 | 2 [1] | 3 [2] | 3 [3] | 3 [2] | 3 [2] | – [1] | – [1] | – [1] | 3 [2] | 3 [2] | – [2] | – [1] | 2 [1] | 2 [2] | 2 [2] | 3 [3] | – [2] | 2 [2] | 2 [1] | 3 [2] | 3 [2] | 3 [2] | – [1] | – [2] | 3 [2] | – [3] | 2 [1] | 2 [1] | 3 [3] | – [2] | – [1] | 3 [2] | – [1] | 3 [2] |  | – [1] |

PO legend: PO1 = PO1; PO2 = PO2; PO3 = PO3; PO4 = PO4; PO5 = PO5; PO6 = PO6; PO7 = PO7; PO8 = PO8; PO9 = PO9; PO10 = PO10; PO11 = PO11; PO12 = PO12; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PSO6 = PSO6; PO1 = PO1; PO2 = PO2; PO3 = PO3; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PSO6 = PSO6; PSO7 = PSO7; PSO8 = PSO8; PSO9 = PSO9; PSO10 = PSO10

- CO1→PO5: Configuring AI coding agents directly exercises modern IT tool usage. (activities: tool-use, implement)
- CO1→PO1: Basic engineering principles underlie the setup of development environments. (activities: tool-use)
- CO1→PO2: Ensuring test case pass rates requires analyzing execution failure outcomes. (activities: tool-use)
- CO1→PO3: Setting up agent orchestration frameworks contributes to system component development. (activities: implement, tool-use)
- CO1→PO4: Verifying test case outcomes involves basic data interpretation. (activities: tool-use)
- CO1→PO6: Minor connection to professional engineering practice contexts. (activities: tool-use)
- CO1→PO7: Incidental connection regarding resource utilization. (activities: tool-use)
- CO1→PO8: Adhering to tool usage guidelines involves professional responsibility. (activities: tool-use)
- CO1→PO9: Individual lab tasks support environment configuration skills. (activities: tool-use)
- CO1→PO10: Comprehending tool specifications requires technical reading. (activities: tool-use)
- CO1→PO11: Orchestration touches upon workflow coordination principles. (activities: tool-use)
- CO1→PO12: Adapting to rapid technological changes in AI frameworks requires continuous learning. (activities: tool-use)
- CO1→PSO1: Touches upon theoretical limits of automated agent systems. (activities: tool-use)
- CO1→PSO2: Involves configuring systems across multiple software abstraction layers. (activities: tool-use)
- CO1→PSO3: Adapting standard orchestration setups for specific environments. (activities: tool-use)
- CO1→PSO4: Implementing and evaluating development environment configurations. (activities: implement, tool-use)
- CO1→PSO5: Directly applies advanced AI tooling and orchestration frameworks. (activities: tool-use, implement)
- CO1→PSO1: Applies foundational concepts of AI agent systems. (activities: tool-use)
- CO1→PSO2: Touches upon behavioral limits of coding agents. (activities: tool-use)
- CO1→PSO3: Implementing configuration setups using modern frameworks. (activities: implement, tool-use)
- CO1→PSO4: Analyzing test outcomes from AI agent runs. (activities: tool-use)
- CO1→PSO5: Applying AI coding agents to automate software generation decisions. (activities: implement, tool-use)
- CO1→PSO6: Minor awareness of AI automation impact. (activities: tool-use)
- CO1→PO1: Independent investigation into agent configurations. (activities: tool-use)
- CO1→PO2: Interpreting technical documentation. (activities: tool-use)
- CO1→PO3: Basic mastery of specialized development tools. (activities: tool-use)
- CO1→PSO1: Understanding agent capabilities and limitations. (activities: tool-use)
- CO1→PSO2: Adapting existing development environments. (activities: tool-use)
- CO1→PSO3: Developing and evaluating agent-based systems. (activities: implement, tool-use)
- CO1→PSO4: Direct utilization of advanced AI coding tools. (activities: tool-use, implement)
- CO1→PSO5: Exploratory use of emerging tools. (activities: tool-use)
- CO1→PSO6: Individual lab execution. (activities: tool-use)
- CO1→PSO7: Responsible tool use. (activities: tool-use)
- CO1→PSO8: Comprehension of technical requirements. (activities: tool-use)
- CO1→PSO9: Independent acquisition of new tool configuration skills. (activities: tool-use)
- CO1→PSO10: Minor impact awareness. (activities: tool-use)
- CO2→PO3: Formulating executable specifications directly fulfills system design and specification practices. (activities: design, implement)
- CO2→PO1: Foundational engineering knowledge supports rigorous specification writing. (activities: design)
- CO2→PO2: Analyzing natural language requirements to structure formal specifications. (activities: design, analyse-data)
- CO2→PO4: Investigating comprehensive use case coverage. (activities: design)
- CO2→PO5: Applying modern spec-driven development tools and techniques. (activities: design, implement)
- CO2→PO6: Contextual understanding of user requirements. (activities: design)
- CO2→PO7: Incidental connection to application domain constraints. (activities: design)
- CO2→PO8: Professional rigor in requirement adherence. (activities: design)
- CO2→PO9: Team collaboration on project design deliverables. (activities: design)
- CO2→PO10: Translating natural language text into clear, structured executable specifications. (activities: design, written-communication)
- CO2→PO11: Managing requirements traceability in software projects. (activities: design)
- CO2→PO12: Adapting modern software engineering methodologies. (activities: design)
- CO2→PSO1: Formal specification foundations. (activities: design)
- CO2→PSO2: Bridging high-level requirements to executable logic. (activities: design)
- CO2→PSO3: Adapting design models for specification-driven workflows. (activities: design)
- CO2→PSO4: Core design activity creating system specifications and deliverables. (activities: design, implement)
- CO2→PSO5: Utilizing advanced spec-driven tools. (activities: design)
- CO2→PSO1: Processing natural language inputs in AI-assisted workflows. (activities: design)
- CO2→PSO2: Limits of automated specification generation. (activities: design)
- CO2→PSO3: Designing structured algorithmic specifications. (activities: design, implement)
- CO2→PSO4: Modeling natural language requirements into computational specifications. (activities: design)
- CO2→PSO5: Transforming unstructured requirements into actionable agent inputs. (activities: design, implement)
- CO2→PSO6: Societal context of requirement definitions. (activities: design)
- CO2→PO1: Investigating design methodologies. (activities: design)
- CO2→PO2: Producing comprehensive design documents and deliverables. (activities: design, written-communication)
- CO2→PO3: Mastery of advanced software specification techniques. (activities: design)
- CO2→PSO1: Theoretical aspects of formal specifications. (activities: design)
- CO2→PSO2: Adapting requirements models. (activities: design)
- CO2→PSO3: Designing core executable specifications for new applications. (activities: design, implement)
- CO2→PSO4: Advanced development tool usage. (activities: design)
- CO2→PSO5: Exploratory design practices. (activities: design)
- CO2→PSO6: Teamwork on design documents. (activities: design)
- CO2→PSO7: Ethical requirement analysis. (activities: design)
- CO2→PSO8: Effective technical document creation. (activities: design, written-communication)
- CO2→PSO9: Lifelong learning in software engineering. (activities: design)
- CO2→PSO10: Impact awareness of system specifications. (activities: design)
- CO3→PO2: Analyzing execution traces and diagnosing failure causes directly exercises problem analysis. (activities: analyse-data, evaluate-critique)
- CO3→PO1: Basic engineering concepts aid trace analysis. (activities: analyse-data)
- CO3→PO3: Insights from failure analysis inform design improvements. (activities: analyse-data)
- CO3→PO4: Investigating agent execution traces and interpreting log data to draw valid conclusions. (activities: analyse-data, evaluate-critique)
- CO3→PO5: Using workflow inspection logs as modern diagnostic tools. (activities: analyse-data)
- CO3→PO6: Contextual safety in agent workflows. (activities: analyse-data)
- CO3→PO7: Incidental environmental impact awareness. (activities: analyse-data)
- CO3→PO8: Objective and truthful reporting of log evidence. (activities: analyse-data)
- CO3→PO9: Individual code review and trace analysis tasks. (activities: analyse-data)
- CO3→PO10: Communicating failure analysis and log evidence clearly in code reviews and exams. (activities: analyse-data, written-communication)
- CO3→PO11: Workflow debugging principles. (activities: analyse-data)
- CO3→PO12: Continuous skill enhancement in debugging modern systems. (activities: analyse-data)
- CO3→PSO1: Limits of agent execution models. (activities: analyse-data)
- CO3→PSO2: Inspecting low-level execution traces and logs across software abstraction layers. (activities: analyse-data)
- CO3→PSO3: Adapting analysis techniques for agent logs. (activities: analyse-data)
- CO3→PSO4: Evaluating system behavior through trace analysis and code review. (activities: analyse-data, evaluate-critique)
- CO3→PSO5: Using advanced log inspection tools. (activities: analyse-data)
- CO3→PSO1: Foundational AI agent behavior. (activities: analyse-data)
- CO3→PSO2: Analyzing failure modes inherent to AI/ML agent execution traces. (activities: analyse-data)
- CO3→PSO3: Debugging algorithmic workflows. (activities: analyse-data)
- CO3→PSO4: Directly analyzes agent execution traces and failure causes using computational and AI concepts. (activities: analyse-data, evaluate-critique)
- CO3→PSO5: Analyzing decisions made by AI coding agents. (activities: analyse-data)
- CO3→PSO6: Impact of agent failures. (activities: analyse-data)
- CO3→PO1: Independent investigation of complex agent execution logs. (activities: analyse-data, research-investigation)
- CO3→PO2: Documenting failure analysis findings. (activities: analyse-data)
- CO3→PO3: Mastery of trace analysis and debugging methodologies. (activities: analyse-data)
- CO3→PSO1: Theoretical limits of trace analysis. (activities: analyse-data)
- CO3→PSO2: Adapting log analysis techniques for agent workflows. (activities: analyse-data)
- CO3→PSO3: Evaluating system performance via log analysis. (activities: analyse-data, evaluate-critique)
- CO3→PSO4: Using log inspection tools. (activities: analyse-data)
- CO3→PSO5: Investigating novel failure modes. (activities: analyse-data)
- CO3→PSO6: Individual trace analysis. (activities: analyse-data)
- CO3→PSO7: Ethical and accurate reporting of logs. (activities: analyse-data)
- CO3→PSO8: Communicating analysis results. (activities: analyse-data)
- CO3→PSO9: Lifelong learning in debugging techniques. (activities: analyse-data)
- CO3→PSO10: Impact analysis of software failures. (activities: analyse-data)
- CO4→PO3: Designing complex AI-native workflows and multi-module architectures directly fulfills solution design. (activities: design, evaluate-critique)
- CO4→PO1: Fundamental engineering knowledge supports architectural design. (activities: design)
- CO4→PO2: Analyzing requirements to justify architectural decisions. (activities: design, analyse-data)
- CO4→PO4: Investigating workflow alternatives and evaluating trade-offs. (activities: design, evaluate-critique)
- CO4→PO5: Designing workflows utilizing modern AI tools and IT resources. (activities: design, tool-use)
- CO4→PO6: Reliability requirements for professional practice. (activities: design)
- CO4→PO7: Sustainable software architecture considerations. (activities: design)
- CO4→PO8: Ethical responsibility in engineering robust systems. (activities: design)
- CO4→PO9: Multi-module project deliverables often involve teamwork and division of labor. (activities: design, teamwork)
- CO4→PO10: Articulating and documenting design justifications effectively. (activities: design, written-communication)
- CO4→PO11: Managing multi-module project structures and reliability constraints. (activities: design, project-management)
- CO4→PO12: Adapting cutting-edge workflow practices. (activities: design)
- CO4→PSO1: Theoretical foundations of software architectures. (activities: design)
- CO4→PSO2: Designing systems spanning multiple application modules and layers. (activities: design)
- CO4→PSO3: Adapting architectural models for AI-native workflows. (activities: design)
- CO4→PSO4: Directly designs and evaluates a multi-module system application. (activities: design, implement)
- CO4→PSO5: Utilizing advanced AI-native workflow techniques. (activities: design, tool-use)
- CO4→PSO1: Integrates AI foundational principles into software workflows. (activities: design)
- CO4→PSO2: Limits of AI-driven workflow automation. (activities: design)
- CO4→PSO3: Designing workflow algorithms and components. (activities: design, implement)
- CO4→PSO4: Modeling problem domains using AI concepts. (activities: design, analyse-data)
- CO4→PSO5: Applying AI automation in development pipelines. (activities: design, implement)
- CO4→PSO6: Impact of AI software workflows. (activities: design)
- CO4→PO1: Independent investigation into novel development workflows. (activities: design, research-investigation)
- CO4→PO2: Writing detailed design deliverables and justifications. (activities: design, written-communication)
- CO4→PO3: Advanced mastery of AI-native software architecture and design. (activities: design, evaluate-critique)
- CO4→PSO1: Theoretical architecture principles. (activities: design)
- CO4→PSO2: Adapting multi-module design models. (activities: design)
- CO4→PSO3: Directly designs, develops, and evaluates novel multi-module application workflows. (activities: design, implement)
- CO4→PSO4: Using advanced AI development techniques. (activities: design, tool-use)
- CO4→PSO5: Cutting-edge workflow design exploration. (activities: design)
- CO4→PSO6: Collaborative team execution on multi-module deliverables. (activities: design, teamwork)
- CO4→PSO7: Professional rigor in architectural decision-making. (activities: design)
- CO4→PSO8: Communicating complex design decisions clearly. (activities: design, written-communication)
- CO4→PSO10: Impact of reliable system design. (activities: design)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1, M1.T2 | 1, 2 | A:Quiz1@L3 |
| CO1.LO2 | L3 | M1.T3 | 3 | A:Quiz1@L3 |
| CO1.LO3 | L3 | M1.T4 | 4 | A:Assignment1@L3, A:Endsem@L3 |
| CO2.LO1 | L2 | M2.T1 | 5 | A:Quiz2@L2, A:Midsem@L2 |
| CO2.LO2 | L5 | M2.T2 | 6 | A:ProjM1@L5, A:Endsem@L5 |
| CO3.LO1 | L4 | M3.T1 | 7 | A:Quiz3@L4, A:Midsem@L4 |
| CO3.LO2 | L4 | M3.T2 | 8 | A:ProjM2@L4, A:Endsem@L4 |
| CO4.LO1 | L5 | M4.T1 | 9 | A:ProjFinal@L5, A:Endsem@L5 |
| CO4.LO2 | L3 | M4.T2, M4.T3, M4.T4 | 10, 11, 12 | A:ProjM2@L3 |
| CO1.LO4 | L3 | M1.T1, M1.T2 | 1, 2 | A:Midsem@L3 |

## Appendix C — Modules and topics

**M1 Agent Orchestration and Environments** (primary CO1)
- M1.T1 Agent orchestration frameworks setup — 3.0 h · LOs CO1.LO1, CO1.LO4
- M1.T2 Development environments configuration — 3.0 h · LOs CO1.LO1, CO1.LO4 · requires M1.T1
- M1.T3 Tool use and custom tool specifications — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T4 Coding agents and context engineering — 3.0 h · LOs CO1.LO3 · requires M1.T3
**M2 Requirements and Spec-Driven Development** (primary CO2)
- M2.T1 Use cases identification from requirements — 3.0 h · LOs CO2.LO1
- M2.T2 Spec-driven development practices — 3.0 h · LOs CO2.LO2 · requires M2.T1
**M3 Workflow Inspection and Loop Engineering** (primary CO3)
- M3.T1 Iterative development and workflow inspection logs — 3.0 h · LOs CO3.LO1 · requires M1.T4
- M3.T2 Loop engineering and failure analysis — 3.0 h · LOs CO3.LO2 · requires M3.T1
**M4 AI-Native Workflows and Software Factories** (primary CO4)
- M4.T1 Automated testing and reliability components — 3.0 h · LOs CO4.LO1 · requires M3.T2
- M4.T2 Software factories and CI/CD integration pipelines — 3.0 h · LOs CO4.LO2 · requires M4.T1
- M4.T3 CI/CD integration pipelines and deployment automation — 3.0 h · LOs CO4.LO2 · requires M4.T2
- M4.T4 Advanced deployment strategies and monitoring — 3.0 h · LOs CO4.LO2 · requires M4.T3

Schedule: feasible · 36.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE594A | 0.08 | complementary | The new course emphasizes practical software development workflows, specification-driven development, and engineering practice rather than pure agentic reasoning algorithms. |
| CSE701 | 0.032 | complementary | CSE701 investigates data science and AI models for software engineering tasks, whereas the new course centers on human-AI collaborative workflows and daily development practices. |
| CSE600 | 0.021 | superficial | CSE600 is a programming language and systems tool course, whereas the new course is an AI-native software engineering workflow course. |

Overlap method: neo4j: Jaccard over embedding-matched topic phrases (all-MiniLM-L6-v2, cos ≥ 0.66), no IDF

**Comparable courses**

- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Concepts of agentic protocols (like MCP) and agent applications. Avoid: Over-focusing on algorithmic and mathematical problem-solving rather than software engineering workflows.
- **CSE583** Software Engineering/Development Using Open Source — IIIT-D catalogue. Take: Project management practices, issue tracking, and team-based application building. Avoid: Traditional open-source release processes without AI-native workflow integration.
- **CSE201** Advanced Programming — IIIT-D catalogue. Take: Test-driven development and modular software design principles. Avoid: Manual programming syntax instruction from scratch.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

**58 errors, 132 warnings.** Repeats of the same check are merged into one row; the full list is in `validation_report.json`.

| Area | Severity | Check | Count | Parts of the design | Example |
|---|---|---|---|---|---|
| CO–PO mapping | error | V23 | 58 | CO1, BTECH-COMMON/PO10, BTECH-COMMON/PO11, BTECH-COMMON/PO12, BTECH-COMMON/PO6, BTECH-COMMON/PO7, BTECH-COMMON/PO8, BTECH-COMMON/PO9 (+15 more) | CO1→BTECH-COMMON/PO10 claimed (provisional 1) but no assessed activity evidences it |
| Your requirements | warning | VK | 1 | K16 | no assessment component recognisably matches 'coding_exercise' (K16); confirm that an existing component covers it, or add one |
| Outcomes (COs and LOs) | warning | V11 | 16 | CO3, CO4, CO1.LO1, CO1.LO2, CO1.LO3, CO2.LO1, CO2.LO2, CO3.LO1 (+3 more) | CO CO3 condition is not visible in the statement text |
| Outcomes (COs and LOs) | warning | V21 | 1 |  | LO lecture-hour estimates sum to 27.0 h vs budget 39 h (±15%) |
| CO–PO mapping | warning | VCOPO-ACT | 98 | CO1, BTECH-COMMON/PO1, BTECH-COMMON/PO2, BTECH-COMMON/PO4, BTECH-COMMON/PO6, BTECH-COMMON/PO7, BTECH-COMMON/PO8, BTECH-COMMON/PO9 (+30 more) | CO1→BTECH-COMMON/PO1: none of its evidencing activities maps to that PO, so its strength can never be computed |
| CO–PO mapping | warning | T4 | 12 | CO2, BTECH-COMMON, BTECH-CSAI, MTECH-CSE, CO3, CO4, CO1 | CO2 maps to 12 outcomes of BTECH-COMMON; keep only the strong links |
| CO–PO mapping | warning | V23 | 2 | CO2, BTECH-COMMON/PO4, MTECH-CSE/PSO2 | CO2→BTECH-COMMON/PO4: provisional 1 vs computed 3 (share 1.0) |
| Topics, schedule and labs | warning | V6 | 1 | W13 | weeks with no lecture topics: [13] |
| Resources | warning | V15 | 1 |  | 2 resource(s) removed because no library record matched: Gullí, Antonio. "Agentic Design Patterns." Springer, 2025; OpenAI MCP, Agent2Agent (A2A) Protocol |

**Repair history**

- cos: errors 3 → 0 · round 1 accepted (3→0)
- los: errors 4 → 0 · round 1 accepted (4→3); round 2 accepted (3→0)
- structure: errors 2 → 0 · round 1 accepted (2→1); round 2 rejected (1→11); round 3 accepted (1→0)
- assessment: errors 59 → 58 · round 1 accepted (59→58); round 2 rejected (None→None)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: credits and ltp: Both credits and L-T-P structure are unspecified; downstream credit-to-contact-hour alignment checks under UGREG-2025§4 cannot run until these are set.
- intake: curriculum_context: Curriculum context does not explicitly list prerequisite or antirequisite course codes (e.g. CSE201) to verify against institutional knowledge graph dependencies.
- constraints: assessment.component[midsem].present, assessment.component[endsem].present: Assessment preferences list practical assignments, coding exercises, and a final project, but do not state whether standard mid-semester or end-semester examinations are omitted, which interacts with calendar scheduling rules under UGREG-2025§6.2.
- structure: Total lecture hours: Sum of topic est_hours is 28.0, which is below the 39-hour budget. Additional advanced topics or deeper coverage units may be introduced if necessary to fully saturate the 39 hours.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress logically from foundational agent orchestration (M1) and specification-driven development (M2) to iterative workflow inspection (M3) and complete AI-native software factories (M4). This builds upon mandatory prerequisite knowledge in software engineering and version control from CSE201.
- **assessment rationale:** The assessment mix of quizzes, assignments, midterm examination, project, and end-semester examination balances theoretical understanding with practical application. The substantial project and assignment weightings directly evaluate students' abilities to execute hands-on AI-assisted development workflows matching the course outcomes.
- **positioning rationale:** Unlike CSE594A, which focuses on agentic reasoning algorithms, this course emphasizes practical software development workflows and specification-driven practices. It differs from CSE701, which investigates data science and AI models, by centering on human-AI collaborative workflows and engineering practices.