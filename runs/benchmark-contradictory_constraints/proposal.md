# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-contradictory_constraints` · generated deterministically from the design graph · validator status: **3 errors, 16 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Level is specified as Advanced undergraduate; Course code is missing | professor |
| — | CONFLICT ['special_constraints'] | — | Contradictory course outcome count constraints provided: SC1 requires exactly 5 Course Outcomes while SC2 requires exactly 12 Course Outcomes. | professor |
| — | CONFLICT ['K14', 'K15'] | — | Special constraint SC1 specifies exactly 5 Course Outcomes while SC2 specifies exactly 12 Course Outcomes, which are mutually exclusive. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with increasingly capable coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. Targeted at third and fourth-year Bachelor of Technology students, the course matters because it prepares engineers for emerging paradigms where autonomous tools integrate directly into the software lifecycle. Upon completion, students will be able to configure AI-assisted coding tools and developer workspaces, translate requirements into executable specifications, deconstruct iterative development loops, evaluate the reliability and performance of AI-generated code, and execute comprehensive AI-native software development projects. The course is taught through a combination of lectures, tutorials, laboratory sessions, and a semester-long project using student development machines and software development environments.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm | Students must possess strong software engineering and programming fundamentals to build and evaluate applications using coding agents. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in Software Engineering with an overlap of 0.185 focusing on data and ML applications in SE, the new course specifically targets modern AI-native development workflows, coding agents, prompt/context engineering, and agentic software factories rather than general mining of software repositories or defect prediction.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure AI-assisted coding tools and developer workflows, using an agent orchestration framework and prompt context configurations, such that automated development tasks are executed with at least 80% passing acceptance tests.** `[CORPUS, USER]`  
verb *configure* · behaviour *AI-assisted coding tools and developer workflows* · condition *using an agent orchestration framework and prompt context configurations* · degree *such that automated development tasks are executed with at least 80% passing acceptance tests* · evidence: programming_assignment, lab_task · marks share (computed): 23.5%

- CO1.LO1 (L1) Identify the core components of AI-assisted coding tools and developer workspaces using standard documentation.
- CO1.LO2 (L3) Configure prompt context settings and agent skills within a supplied developer environment.
- CO1.LO3 (L3 ★capstone) Configure an agent orchestration framework using prompt context configurations for automated development tasks, such that automated development tasks are executed with at least 80% passing acceptance tests.

**CO2 (L3, procedural) — Translate high-level software requirements into executable specifications, using spec-driven development guidelines and requirement mapping templates, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *translate* · behaviour *high-level software requirements into executable specifications* · condition *using spec-driven development guidelines and requirement mapping templates* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 18.0%

- CO2.LO1 (L3) Examine high-level software requirements using requirements engineering principles to identify functional scope.
- CO2.LO2 (L3 ★capstone) Translate high-level software requirements into executable specification models, using requirement mapping templates, covering every use case in the supplied requirements document.

**CO3 (L4, conceptual) — Deconstruct iterative software development loops and agent interactions, using software factory pipelines and loop engineering metrics, identifying at least three distinct failure causes with supporting log evidence from the execution trace.** `[CORPUS, USER]`  
verb *deconstruct* · behaviour *iterative software development loops and agent interactions* · condition *using software factory pipelines and loop engineering metrics* · degree *identifying at least three distinct failure causes with supporting log evidence from the execution trace* · evidence: exam_question, report · marks share (computed): 16.0%

- CO3.LO1 (L2) Trace iterative software development loops and agent interactions using execution logs.
- CO3.LO2 (L4 ★capstone) Deconstruct software factory pipelines and loop engineering metrics, identifying at least three distinct failure causes with supporting log evidence from the execution trace.

**CO4 (L5, metacognitive) — Evaluate the reliability and performance of AI-generated code and deployment pipelines, using automated testing frameworks and evaluation suites, justifying each assessment decision against stated quality criteria.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *the reliability and performance of AI-generated code and deployment pipelines* · condition *using automated testing frameworks and evaluation suites* · degree *justifying each assessment decision against stated quality criteria* · evidence: project_deliverable, code_review · marks share (computed): 17.5%

- CO4.LO1 (L3) Apply automated testing frameworks to execute AI-generated code snippets against test suites.
- CO4.LO2 (L5 ★capstone) Evaluate the robustness of continuous integration deployment pipelines, using automated evaluation suites, justifying each assessment decision against stated quality criteria.

**CO5 (L5, procedural) — Evaluate an AI-native software development project, using coding agents, MCP tools, and automated evaluation frameworks, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *an AI-native software development project* · condition *using coding agents, MCP tools, and automated evaluation frameworks* · degree *such that the delivered system satisfies every acceptance criterion agreed at the first milestone* · evidence: project_deliverable, presentation · marks share (computed): 25.0%

- CO5.LO1 (L3) Construct a modular prototype project plan using coding agents and MCP tools.
- CO5.LO2 (L5 ★capstone) Evaluate an end-to-end multi-agent coding project prototype, using automated evaluation frameworks, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding tool components and developer workspaces (M1.T1) | CO1.LO1 | CO1 | Worked trace-diagnosis of sample developer workspace configurations, in pairs. |  |
| 2 | Context engineering and agent skills in developer environments (M1.T2) | CO1.LO2 | CO1 | Worked trace-diagnosis of failing prompt context settings, in pairs. |  |
| 3 | Agent orchestration frameworks and developer workflows (M2.T1) | CO1.LO3 | CO1 | Peer review of agent orchestration configuration scripts and acceptance tests. | A:Quiz1 (quiz) |
| 4 | Requirements engineering and functional scope identification (M2.T2) | CO2.LO1 | CO2 | Worked exercise on extracting functional scope and use cases from raw requirements text. |  |
| 5 | Spec-driven development and requirement mapping templates (M2.T3) | CO2.LO2 | CO2 | Group mapping exercise translating requirements text into executable specification models. | A:Assign1 (assignment) |
| 6 | Iterative development loops and execution trace inspection (M3.T1) | CO3.LO1 | CO3 | Trace-diagnosis of software development execution logs to identify interaction anomalies. |  |
| 7 | Software factory pipelines and loop engineering metrics (M3.T2) | CO3.LO2 | CO3 | Mid-semester review and problem-solving session on software factory metrics. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Automated testing frameworks and unit testing using JUnit (M4.T1) | CO4.LO1 | CO4 | Worked debugging session on failing JUnit test suites for AI-generated code snippets. | A:ProjectMilestone released |
| 9 | Reliability evaluation and ML model evaluation in deployment pipelines (M4.T2) | CO4.LO2 | CO4 | Evaluation and discussion of CI deployment pipeline robustness metrics in small groups. | A:LabTask1 (lab) |
| 10 | Coding agents, MCP tools, and project management estimation (M5.T1)<br>Emerging developer tools and capstone project system evaluation (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Worked estimation exercise for modular prototype project plans using coding agents. |  |
| 11 | Emerging developer tools and capstone project system evaluation (M5.T2)<br>Project management estimation and risk tracking (M5.T3) | CO5.LO1, CO5.LO2 | CO5 | Risk tracking and project milestone review workshop. | A:ProjectMilestone due |
| 12 | Capstone project system evaluation methodologies (M5.T4) | CO5.LO2 | CO5 | Evaluation criteria alignment check for capstone project system prototypes. |  |
| 13 |  |  |  | Capstone presentation rehearsals and peer feedback sessions. | A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Developer Workspace Setup and AI Tool Inspection** — Install and configure the local developer workspace. Inspect AI-assisted coding tool components and document workspace settings. |  | VS Code, Git |
| 2 | **Context Engineering and Agent Skills Configuration** — Configure prompt context settings and agent skills within the supplied developer environment. | CO1.LO2 | Developer environment, AI coding assistants |
| 3 | **Agent Orchestration Framework Setup** — Configure an agent orchestration framework using prompt context configurations to execute automated development tasks. | CO1.LO3 | Agent orchestration framework, Python |
| 4 | **Functional Scope Identification Practice** — Examine high-level software requirements to identify functional scope and document initial system boundaries. | CO2.LO1 | Text editors, Requirements templates |
| 5 | **Spec-Driven Development and Requirement Mapping** — Translate high-level software requirements into executable specification models using requirement mapping templates. | CO2.LO2 | Mapping templates, Design tools |
| 6 | **Execution Trace Inspection** — Inspect iterative software development loops and agent interactions using execution logs. | CO3.LO1 | Log analyzer, IDE |
| 7 | **Midsem Catch-up and Open Lab** — Mid-semester exam week. Catch-up session for ongoing lab assignments and open lab support. |  | Development environment |
| 8 | **Automated Testing with JUnit** — Apply automated testing frameworks to execute AI-generated code snippets against unit test suites using JUnit. | CO4.LO1 | JUnit, Java development environment |
| 9 | **Reliability Evaluation in CI Pipelines** — Evaluate the robustness of continuous integration deployment pipelines using automated evaluation suites. | CO4.LO2 | CI deployment pipelines, Evaluation suites |
| 10 | **Project Planning with Coding Agents and MCP Tools** — Construct a modular prototype project plan using coding agents and MCP tools. | CO5.LO1 | MCP tools, Coding agents |
| 11 | **Estimation and Risk Tracking in Projects** — Refine project management estimation and risk tracking for ongoing capstone project prototypes. | CO5.LO1 | Project management tools |
| 12 | **Capstone Project System Evaluation** — Evaluate an end-to-end multi-agent coding project prototype using automated evaluation frameworks. | CO5.LO2 | Automated evaluation frameworks, Multi-agent prototype |
| 13 | **Final Project Review and Open Lab** — Final review of capstone deliverables and open consultation session. | CO5.LO2 | Development environment |

Infrastructure: Student development machines (available); Access to AI coding tools/APIs (needs_confirmation); Software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3) | — | analyse-data, tool-use |  |
| assignment | 20.0 | A:Assign1 (W5→W5) | — | implement, design, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, design |  |
| lab | 15.0 | A:LabTask1 (W9→W9) | — | implement, tool-use |  |
| project | 20.0 | A:ProjectMilestone (W8→W11) | — | design, implement, evaluate-critique, tool-use, oral-presentation |  |
| endsem | 15.0 | A:Endsem (W13→W13) | — | evaluate-critique, design |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 23.5%, CO2 18.0%, CO3 16.0%, CO4 17.5%, CO5 25.0%

## 10. Resource material

Policy: **mixed** — Because AI-assisted software development is a rapidly evolving field, a mixed approach combining standard software engineering reference texts with recent literature and documentation is utilized.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Ian Sommerville (2005). *Software Engineering*. | 9780133943030 | yes | M2.T2 |
| reference | Robert C. Martin (2017). *Clean Architecture: A Craftsman's Guide to Software Structure and Design*. | 9789352865123 | yes | M2.T3 |
| reference | Jez Humble, David Farley (2010). *Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*. | 9780321670229 | yes | M3.T2, M4.T2 |
| reference | Glenford J. Myers (2004). *The art of software testing*. | 9781118133156 | yes | M4.T1 |
| reading | G. Rainer (2025). *Machine Learning and Artificial Intelligence for Enhanced Software Engineering: Methods and Applications*. | 10.2139/ssrn.5752084 | yes | M1.T1, M5.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 1 [unclaimed] | 3 [3] |  | 3 [2] |
| CO2 | 2 [unclaimed] | 3 [3] |  | 2 [unclaimed] |
| CO3 | 3 [unclaimed] | 3 [unclaimed] |  | 1 [3] |
| CO4 |  | 3 [3] | 2 [unclaimed] | 3 [unclaimed] |
| CO5 |  | 3 [3] | 2 [unclaimed] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring AI-assisted tools and workflows directly maps to implementing systems using modern tooling as covered by PO4. (activities: implement, tool-use)
- CO1→PO9: Utilizing agent orchestration frameworks and prompt configurations exercises advanced computing techniques. (activities: tool-use)
- CO2→PO4: Translating requirements into specifications forms a core part of the system design process under PO4. (activities: design, implement)
- CO3→PO9: Deconstructing agent loops and software factory pipelines requires advanced analytical techniques. (activities: analyse-data)
- CO4→PO4: Evaluating reliability and performance of generated code aligns with the evaluation facet of PO4. (activities: evaluate-critique)
- CO5→PO4: Project evaluation against acceptance criteria directly satisfies system evaluation requirements. (activities: evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1 |
| CO1.LO2 | L3 | M1.T2 | 2 | A:LabTask1@L3 |
| CO1.LO3 | L3 | M2.T1 | 3 | A:Assign1@L3 |
| CO2.LO1 | L3 | M2.T2 | 4 | A:Midsem@L3 |
| CO2.LO2 | L3 | M2.T3 | 5 | A:Assign1@L3 |
| CO3.LO1 | L2 | M3.T1 | 6 | A:Quiz1@L2 |
| CO3.LO2 | L4 | M3.T2 | 7 | A:Midsem@L4 |
| CO4.LO1 | L3 | M4.T1 | 8 | A:LabTask1@L3 |
| CO4.LO2 | L5 | M4.T2 | 9 | A:ProjectMilestone@L5 |
| CO5.LO1 | L3 | M5.T1, M5.T3 | 10, 11 | A:ProjectMilestone@L3 |
| CO5.LO2 | L5 | M5.T2, M5.T4 | 10, 11, 12 | A:Endsem@L5 |

## Appendix C — Modules and topics

**M1 Foundations of AI-Assisted Coding and Developer Workspaces** (primary CO1)
- M1.T1 AI-assisted coding tool components and developer workspaces — 3.0 h · LOs CO1.LO1
- M1.T2 Context engineering and agent skills in developer environments — 3.0 h · LOs CO1.LO2 · requires M1.T1
**M2 Agent Orchestration and Specification-Driven Development** (primary CO1, CO2)
- M2.T1 Agent orchestration frameworks and developer workflows — 3.0 h · LOs CO1.LO3 · requires M1.T2
- M2.T2 Requirements engineering and functional scope identification — 3.0 h · LOs CO2.LO1
- M2.T3 Spec-driven development and requirement mapping templates — 3.0 h · LOs CO2.LO2 · requires M2.T2
**M3 Iterative Development Loops and Software Factory Pipelines** (primary CO3)
- M3.T1 Iterative development loops and execution trace inspection — 3.0 h · LOs CO3.LO1 · requires M2.T1
- M3.T2 Software factory pipelines and loop engineering metrics — 3.0 h · LOs CO3.LO2 · requires M3.T1
**M4 Automated Testing, Evaluation, and Deployment Pipelines** (primary CO4)
- M4.T1 Automated testing frameworks and unit testing using JUnit — 3.0 h · LOs CO4.LO1 · requires M2.T1
- M4.T2 Reliability evaluation and ML model evaluation in deployment pipelines — 3.0 h · LOs CO4.LO2 · requires M4.T1
**M5 AI-Native Software Development Projects and MCP Integration** (primary CO5)
- M5.T1 Coding agents, MCP tools, and project management estimation — 2.0 h · LOs CO5.LO1 · requires M2.T3, M3.T2
- M5.T2 Emerging developer tools and capstone project system evaluation — 2.0 h · LOs CO5.LO2 · requires M5.T1, M4.T2
- M5.T3 Project management estimation and risk tracking — 2.0 h · LOs CO5.LO1 · requires M5.T1
- M5.T4 Capstone project system evaluation methodologies — 2.0 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 35.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | complementary | CSE701 focuses on data-driven software engineering and mining repositories, whereas this course focuses on interactive workflows with autonomous coding agents and prompt/context engineering. |
| CSE581 | 0.034 | superficial | CSE581 covers classical systems analysis and requirements engineering theories, whereas this course addresses spec-driven development specifically for AI agents. |
| CSE582 | 0.067 | complementary | CSE582 focuses on product line engineering and legacy maintenance, whereas this course covers AI-driven software factories and automated loop engineering. |
| CSE594A | 0.08 | complementary | CSE594A is a broad introduction to agentic reasoning across algorithmic and scientific domains, whereas this course is specifically tailored to software development and engineering workflows. |
| CSE201 | 0.017 | complementary | CSE201 teaches foundational object-oriented programming and manual unit testing in Java, whereas this course assumes these skills to teach automated testing and evaluation of AI coding tools. |
| AI501 | 0.034 | superficial | AI501 is a foundational course on machine learning theory and models, whereas this course focuses entirely on applying AI tools and agents within software development lifecycles. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Research literature review structure and advanced software engineering evaluation topics. Avoid: Repository mining and legacy bug triaging focus, keeping the focus on real-time coding agents.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Core concepts of agentic protocols and multi-agent collaboration frameworks. Avoid: Purely mathematical and algorithmic problem-solving focus, instead emphasizing practical software engineering workflows.
- **CSE201** Advanced Programming — IIIT-D catalogue. Take: Foundational code structure, modularity, and testing concepts expected of the student cohort. Avoid: Manual, non-assisted implementation styles.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| assessment | V19 | error | A:Quiz1, CO3.LO1 | A:Quiz1 (due week 3) assesses CO3.LO1 whose topics run until week 6 |
| assessment | V20 | error | endsem | endsem weight 15.0% outside band [20.0, 30.0] with no justification |
| assessment | VA-PROJ | error | project | project runs only weeks 8–11 (< 4 weeks) — too short for a substantial project |
| assessment | V23 | warning | CO3, BTECH-CSE/PO9 | CO3→BTECH-CSE/PO9: provisional 3 vs computed 1 (share 0.25) |
| assessment | VA-PROJ | warning | project | project released in week 8, late in a 13-week semester |
| copo | VCOPO-ACT | warning | CO3, BTECH-CSE/PO9 | CO3→BTECH-CSE/PO9: none of its evidencing activities maps to that PO, so its strength can never be computed |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO2 | LO CO2.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO2 | LO CO3.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 32.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 6 → 0 · round 1 accepted (6→3); round 2 rejected (3→3); round 3 accepted (3→0)
- structure: errors 3 → 0 · round 1 rejected (3→3); round 2 rejected (3→5); round 3 accepted (3→0)
- assessment: errors 6 → 3 · round 1 accepted (6→3); round 2 rejected (3→3); round 3 rejected (3→3)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: The intake form contains conflicting requirements regarding the number of Course Outcomes (5 vs 12).
- positioning: Special constraints conflict: The CCO special_constraints contain a contradiction: SC1 requires exactly 5 Course Outcomes, while SC2 requires exactly 12 Course Outcomes.
- constraints: Contradictory Special Constraints: CCO.special_constraints contains conflicting requirements for the number of Course Outcomes (SC1 says 5, SC2 says 12).
- cos: SC1 and SC2: Special constraints contain conflicting counts: SC1 demands exactly 5 Course Outcomes, while SC2 demands exactly 12. We adhered to SC1 (5 COs) and standard IIIT-D course design norms.
- los: hours_total: The sum of LO lecture hours (33), tutorial hours (11), and lab hours (24) is slightly below the target budget (39, 13, 26). However, the hours are distributed reasonably across 11 distinct LOs spanning the 5 course outcomes.
- structure: special_constraints: Context contains conflicting special constraints SC1 (exactly 5 Course Outcomes) and SC2 (exactly 12 Course Outcomes). Proceeded using the 5 actual Course Outcomes present in the cos context.
- resources: Candidate Resources: Few external candidates cover emerging topics such as Model Context Protocol (MCP) and modern agent orchestration frameworks, requiring supplementary readings or documentation.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress from foundational tools to advanced orchestration, pipelines, and projects, reflecting the prerequisite knowledge from CSE201 and ensuring students master basic coding environments before tackling autonomous agent loops and capstone systems.
- **assessment rationale:** The assessment mix—comprising quizzes, assignments, mid-semester and end-semester examinations, laboratory work, and a project—aligns directly with the course outcomes by combining theoretical evaluation with practical, hands-on implementation and system validation.
- **positioning rationale:** Unlike CSE201 which teaches manual programming and testing, CSE701 focusing on repository mining, or AI501 covering machine learning theory, this course specifically targets interactive workflows and engineering practices for autonomous coding agents.