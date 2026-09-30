# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `cs601-01` · generated deterministically from the design graph · validator status: **0 errors, 10 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Level provided as text, course code not specified | professor |
| — | ambiguous: curriculum_context | — | Contains a single descriptive paragraph, not split into Q1–Q6 | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

Software Development using AI examines AI-native software development where developers collaborate with coding agents. The course introduces the orchestration of agent skills and the Model Context Protocol, enabling students to configure agents that satisfy most test cases. It covers translating natural‑language requirements into executable specifications, iterative loop engineering with trace analysis, and evaluation of automated testing and reliability frameworks. Throughout the 13‑week term, students engage in lectures, labs, and a substantial project that integrates multi‑module development using emerging AI tools. By the end of the course, students will be able to design, implement, and assess AI‑assisted development workflows. The course does not become a general introduction to AI or machine learning.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 (or CSE201) `[CATALOGUE]` | Unit testing using JUnit, Unified Modelling Language (sequence diagram, class diagram, use case diagram), Collection framework | Students require strong programming fundamentals, object-oriented design, unit testing, and software development practices to effectively evaluate and build software using coding agents. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in software engineering and CSE594A covers agentic reasoning, neither focuses specifically on modern AI-native software development workflows, agentic coding environments, spec-driven development, and human-AI collaborative software factories as proposed in this course.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure coding agents and agent skills, using an agent orchestration framework and Model Context Protocol, such that at least 80% of the provided test cases pass.** `[CORPUS, USER]`  
verb *Configure* · behaviour *coding agents and agent skills* · condition *using an agent orchestration framework and Model Context Protocol* · degree *such that at least 80% of the provided test cases pass* · evidence: programming_assignment, lab_task · marks share (computed): 15.0%

- CO1.LO1 (L1) Identify developer workflows and components of AI-assisted coding tools using standard terminology.
- CO1.LO2 (L3) Configure coding agents and agent skills using an agent orchestration framework.
- CO1.LO3 (L3 ★capstone) Configure Model Context Protocol bindings for coding agents using an agent orchestration framework, for 3 supplied test configurations.

**CO2 (L3, procedural) — Construct executable specifications from a given natural-language requirements document, using spec-driven development tools, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *Construct* · behaviour *executable specifications from a given natural-language requirements document* · condition *using spec-driven development tools* · degree *covering every use case in the supplied requirements document* · evidence: design_document, programming_assignment · marks share (computed): 15.0%

- CO2.LO1 (L2) Describe natural-language requirements documents in terms of functional use cases and boundaries.
- CO2.LO2 (L3 ★capstone) Construct executable test specifications from a given natural-language requirements document using spec-driven development tools, covering 3 supplied use cases.

**CO3 (L4, metacognitive) — Analyze execution traces produced by coding agents during iterative loop engineering, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *Analyze* · behaviour *execution traces produced by coding agents during iterative loop engineering* · condition *during iterative loop engineering* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: code_review, exam_question · marks share (computed): 20.0%

- CO3.LO1 (L4) Examine execution logs produced by coding agents during iterative loop engineering to isolate warning messages.
- CO3.LO2 (L4 ★capstone) Analyze trace error outputs produced by coding agents during iterative loop engineering, identifying at least three distinct failure causes with supporting log evidence.

**CO4 (L5, conceptual) — Evaluate automated testing and reliability frameworks for agent-generated code, justifying each evaluation decision against at least one stated requirement.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *automated testing and reliability frameworks for agent-generated code* · condition *for agent-generated code* · degree *justifying each evaluation decision against at least one stated requirement* · evidence: design_document, report · marks share (computed): 15.0%

- CO4.LO1 (L2) Compare automated testing and reliability frameworks for agent-generated code across common metrics.
- CO4.LO2 (L5 ★capstone) Evaluate test coverage reports from automated testing frameworks for agent-generated code, justifying each evaluation decision against at least one stated requirement.

**CO5 (L5, procedural) — Evaluate a complete AI-native software development workflow for a given multi-module project, demonstrated live with two scenario walkthroughs chosen by the evaluator.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *a complete AI-native software development workflow for a given multi-module project* · condition *for a given multi-module project* · degree *demonstrated live, with 2 scenario walkthroughs chosen by the evaluator* · evidence: project_deliverable, presentation · marks share (computed): 35.0%

- CO5.LO1 (L5) Design agentic tools, specifications, loops, and evaluation components into a unified multi-module software project structure, meeting the stated interface specification for every public method.
- CO5.LO2 (L5 ★capstone) Evaluate final build artifacts of an AI-native software development workflow for a given multi-module project, demonstrated live, with 2 scenario walkthroughs chosen by the evaluator.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding and developer workflows (M1.T1)<br>Requirements to executable specifications (M2.T1) | CO1.LO1, CO2.LO1 | CO1, CO2 | Trace and analyze 2 sample developer workflow diagrams in groups, identifying tool components using standard terminology. |  |
| 2 | Requirements to executable specifications (M2.T1)<br>Spec-driven development tools (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Worked trace-diagnosis of 2 natural-language requirements documents to define functional use cases and boundaries in pairs. |  |
| 3 | Advanced spec-driven workflows (M2.T3)<br>Agent skills and tools configuration (M3.T1) | CO1.LO2, CO2.LO2 | CO1, CO2 | Group troubleshooting session mapping agent skill configurations against supplied orchestration framework errors. | A:Quiz1 (quiz) |
| 4 | Agent skills and tools configuration (M3.T1)<br>Model Context Protocol bindings (M3.T2) | CO1.LO2, CO1.LO3 | CO1 | Peer review of Model Context Protocol binding configurations for edge-case test setups. | A:Assignment1 released |
| 5 | Model Context Protocol bindings (M3.T2)<br>Execution log inspection and warnings (M4.T1) | CO1.LO3, CO3.LO1 | CO1, CO3 | Trace-diagnosis exercise inspecting execution logs from iterative agent loops to isolate warning messages. | A:Assignment1 due; A:Assignment2 released |
| 6 | Execution log inspection and warnings (M4.T1)<br>Iterative development and trace debugging (M4.T2) | CO3.LO1, CO3.LO2 | CO3 | Walkthrough and discussion of trace error outputs from agent loop engineering, matching logs to failure causes. |  |
| 7 | Advanced trace debugging practice (M4.T3)<br>Automated testing and reliability frameworks comparison (M5.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Mid-semester review problem-solving session comparing automated testing framework approaches. | A:Assignment2 due; A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Automated testing and reliability frameworks comparison (M5.T1)<br>Usability and evaluation of test coverage reports (M5.T2) | CO4.LO1, CO4.LO2 | CO4 | Comparative analysis exercise contrasting automated testing and reliability frameworks across common metrics in teams. |  |
| 9 | Usability and evaluation of test coverage reports (M5.T2)<br>Coverage report evaluation and feedback (M5.T3) | CO4.LO2 | CO4 | Worked evaluation of test coverage reports against stated requirements in pairs. | A:Report1 released; A:ProjMilestone1 released |
| 10 | Hands-on coding and multi-module project design (M6.T1)<br>Multi-module project integration practice (M6.T1b) | CO5.LO1 | CO5 | Architectural design review of multi-module project interface specifications in small groups. | A:Report1 due |
| 11 | Multi-module project integration practice (M6.T1b)<br>Emerging developer tools and live build evaluation (M6.T2) | CO5.LO1, CO5.LO2 | CO5 | Peer evaluation of multi-module project integration checkpoints and interface compliance. | A:ProjMilestone1 due; A:ProjFinal released |
| 12 | Live build evaluation exercises (M6.T3) | CO5.LO2 | CO5 | Mock presentation and scenario walkthrough preparation for final build artifact evaluations. |  |
| 13 |  |  |  |  | A:ProjFinal due |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Introduction to AI-Assisted Developer Workflows** — Explore basic AI-assisted coding tools and examine developer environment configurations in pairs. | CO1.LO1 | Student development machines, software development environments |
| 2 | **Spec-Driven Development Tools Practice** — Construct executable test specifications from natural-language requirements using spec-driven development tools. | CO2.LO2 | Student development machines, software development environments |
| 3 | **Agent Skills and Tool Configuration** — Configure coding agents and agent skills using an agent orchestration framework on local test environments. | CO1.LO2 | Student development machines, access to AI coding tools/APIs |
| 4 | **Model Context Protocol Bindings** — Configure Model Context Protocol bindings for coding agents using an agent orchestration framework for 3 test configurations. | CO1.LO3 | Student development machines, access to AI coding tools/APIs |
| 5 | **Advanced MCP Bindings and Log Inspection** — Refine MCP bindings and practice examining execution logs produced by coding agents during iterative loops. | CO1.LO3, CO3.LO1 | Student development machines, software development environments |
| 6 | **Iterative Development and Trace Debugging** — Analyze trace error outputs produced by coding agents during iterative loop engineering to identify failure causes. | CO3.LO2 | Student development machines, software development environments |
| 7 | **Advanced Trace Debugging Practice** — Conduct advanced trace debugging practice with complex failure logs and multi-step agent traces. | CO3.LO2 | Student development machines, software development environments |
| 8 | **Post-Midsem Catch-up and Open Lab** — Open lab session to catch up on debugging exercises and review automated testing frameworks. | CO3.LO2 | Student development machines |
| 9 | **Test Coverage and Evaluation Reports** — Evaluate test coverage reports from automated testing frameworks and draft justifications against requirements. | CO4.LO2 | Student development machines, software development environments |
| 10 | **Multi-Module Project Design** — Design agentic tools, specifications, and loops into a unified multi-module software project structure. | CO5.LO1 | Student development machines, software development environments |
| 11 | **Multi-Module Project Integration Practice** — Integrate multi-module project components and evaluate emerging developer tools in live builds. | CO5.LO1, CO5.LO2 | Student development machines, access to AI coding tools/APIs |
| 12 | **Live Build Evaluation Exercises** — Conduct live build evaluations of AI-native software development workflows with scenario walkthroughs. | CO5.LO2 | Student development machines, access to AI coding tools/APIs |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (needs_confirmation); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3) | — | analyse-data, tool-use |  |
| assignment | 20.0 | A:Assignment1 (W4→W5), A:Assignment2 (W5→W7) | — | implement, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data |  |
| report | 15.0 | A:Report1 (W9→W10) | — | evaluate-critique, written-communication |  |
| project | 35.0 | A:ProjMilestone1 (W9→W11), A:ProjFinal (W11→W13) | — | design, implement, evaluate-critique, oral-presentation, teamwork | Aligned with practical course preferences and multi-module capstone delivery over 4+ weeks. |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 15.0%, CO2 15.0%, CO3 20.0%, CO4 15.0%, CO5 35.0%

## 10. Resource material

Policy: **reading_list** — Due to the fast-moving nature of AI-native software development, coding agents, and specification-driven development tools, current peer-reviewed research papers and proceedings are more appropriate than static traditional textbooks.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reading | Andrii Tkachuk (2026). *SPECIFICATION-DRIVEN DEVELOPMENT AS STRUCTURED APPROACH FOR SOURCE CODE GENERATION*. | 10.52058/2786-6025-2026-4(58)-2631-2644 | yes | M2.T1 |
| reading | Kevin Lano, Qiaomu Xue (2022). *Code Generation by Example*. | 10.5220/0010973600003119 | yes | M2.T2 |
| reading | Anthony Shaw, Amin Beheshti (2026). *Complexity Backpressure for AI Coding Agents: A Cross-Model Study on Substantive Software Tasks*. | 10.1109/sse72781.2026.00047 | yes | M3.T1, M4.T2 |
| reading | Jahnavi Bellapukonda (2026). *A Comparative Evaluation of LLM-based Coding Agents for Automated Software development Tasks*. | 10.2139/ssrn.6755658 | yes | M5.T1 |
| reading | Mingxuan Xiao, Yan Xiao, Shunhui Ji, Jiahe Tu (2026). *BASFuzz: Toward Robustness Evaluation of LLM-based NLP Software via Automated Fuzz Testing*. | 10.1145/3843770 | yes | M5.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 3 [3] |  |  | 3 [2] |
| CO2 | 2 [unclaimed] | 3 [3] |  |  | 3 [unclaimed] |
| CO3 | 3 [3] |  |  |  |  |
| CO4 |  | 3 [3] |  | 3 [unclaimed] | 3 [2] |
| CO5 |  | 3 [2] | 3 [unclaimed] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring coding agents using frameworks directly aligns with implementing and utilizing modern development tools to build application components. (activities: implement, tool-use)
- CO1→PO9: Utilizing Model Context Protocol and orchestration frameworks demonstrates the application of advanced computing tools. (activities: tool-use)
- CO2→PO4: Constructing executable specifications translates requirements into design elements using spec-driven tools. (activities: design, implement)
- CO3→PO3: Analyzing execution traces and identifying failure causes involves examining process data to diagnose and adapt solutions. (activities: analyse-data)
- CO4→PO4: Evaluating testing frameworks directly matches the evaluation aspect of building computer-based systems. (activities: evaluate-critique)
- CO4→PO9: Assessing specialized reliability frameworks for agent-generated code involves advanced computing tool evaluation. (activities: evaluate-critique, tool-use)
- CO5→PO4: Evaluating multi-module project workflows covers system-level evaluation using modern methodologies. (activities: evaluate-critique)
- CO5→PO7: Live scenario walkthroughs require effective oral communication of technical workflows. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Quiz1@L1 |
| CO1.LO2 | L3 | M3.T1 | 3, 4 | A:Assignment1@L3 |
| CO1.LO3 | L3 | M3.T2 | 4, 5 | A:Assignment1@L3 |
| CO2.LO1 | L2 | M2.T1 | 1, 2 | A:Quiz1@L2 |
| CO2.LO2 | L3 | M2.T2, M2.T3 | 2, 3 | A:Assignment2@L3 |
| CO3.LO1 | L4 | M4.T1 | 5, 6 | A:Midsem@L4 |
| CO3.LO2 | L4 | M4.T2, M4.T3 | 6, 7 | A:Midsem@L4 |
| CO4.LO1 | L2 | M5.T1 | 7, 8 | A:Report1@L2 |
| CO4.LO2 | L5 | M5.T2, M5.T3 | 8, 9 | A:Report1@L5 |
| CO5.LO1 | L5 | M6.T1, M6.T1b | 10, 11 | A:ProjMilestone1@L5 |
| CO5.LO2 | L5 | M6.T2, M6.T3 | 11, 12 | A:ProjFinal@L5 |

## Appendix C — Modules and topics

**M1 Introduction to AI-Assisted Coding and Developer Workflows** (primary CO1)
- M1.T1 AI-assisted coding and developer workflows — 2.0 h · LOs CO1.LO1
**M2 Requirements and Specification-Driven Development** (primary CO2)
- M2.T1 Requirements to executable specifications — 2.0 h · LOs CO2.LO1 · requires M1.T1
- M2.T2 Spec-driven development tools — 2.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Advanced spec-driven workflows — 2.0 h · LOs CO2.LO2 · requires M2.T2
**M3 Coding Agents, Agent Skills, and Model Context Protocol** (primary CO1)
- M3.T1 Agent skills and tools configuration — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M3.T2 Model Context Protocol bindings — 3.0 h · LOs CO1.LO3 · requires M3.T1
**M4 Iterative Loop Engineering and Execution Trace Analysis** (primary CO3)
- M4.T1 Execution log inspection and warnings — 2.0 h · LOs CO3.LO1 · requires M3.T2
- M4.T2 Iterative development and trace debugging — 2.0 h · LOs CO3.LO2 · requires M4.T1
- M4.T3 Advanced trace debugging practice — 2.0 h · LOs CO3.LO2 · requires M4.T2
**M5 Automated Testing, Reliability, and Framework Evaluation** (primary CO4)
- M5.T1 Automated testing and reliability frameworks comparison — 3.0 h · LOs CO4.LO1 · requires M4.T2
- M5.T2 Usability and evaluation of test coverage reports — 2.0 h · LOs CO4.LO2 · requires M5.T1
- M5.T3 Coverage report evaluation and feedback — 2.0 h · LOs CO4.LO2 · requires M5.T2
**M6 Comprehensive Project Integration and Live Evaluation** (primary CO5)
- M6.T1 Hands-on coding and multi-module project design — 2.0 h · LOs CO5.LO1 · requires M5.T2, M2.T2
- M6.T2 Emerging developer tools and live build evaluation — 2.0 h · LOs CO5.LO2 · requires M6.T1
- M6.T1b Multi-module project integration practice — 2.0 h · LOs CO5.LO1 · requires M6.T1
- M6.T3 Live build evaluation exercises — 2.0 h · LOs CO5.LO2 · requires M6.T2

Schedule: feasible · 35.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.118 | complementary | CSE701 is a graduate-level seminar/topics course focusing broadly on mining software repositories and applying ML models to SE research problems, whereas the new course focuses on hands-on workflow engineering, agentic tools, and practical software development processes using AI agents. |
| CSE581 | 0.062 | complementary | CSE581 covers traditional and empirical systems analysis, design, and requirements engineering theories, whereas the new course deals with executable specifications and spec-driven development specifically for AI-native software workflows. |
| CSE582 | 0.118 | complementary | CSE582 focuses on software product lines, maintenance, re-engineering, and legacy systems, whereas the new course addresses iterative loop engineering and software factories powered by coding agents. |
| CSE594A | 0.077 | complementary | CSE594A is a 2-credit course focused on the foundational algorithms and protocols of agentic reasoning (such as algorithmic and mathematical problem solving), whereas the new course is a 4-credit course focused on practical software engineering workflows and developer tool integration. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation structure and practical tooling integration approach. Avoid: Traditional open-source licensing and component-based service architectures which are not the primary focus of AI-native workflows.
- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Perspectives on evaluating AI-assisted code review and automated testing. Avoid: Research-heavy literature review focus; the new course should remain practical and workflow-oriented.
- **EXT:STANFORD/CS146S** CS 146S The Modern Software Developer — Stanford University, <https://explorecourses.stanford.edu/search?q=CS146S>. Take: Topic sequencing on AI-powered IDEs, terminals, code review, and trust in AI tools within the software development life cycle. Avoid: Industry-practitioner guest lecture format if it dilutes structured academic lab requirements.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| assessment | VA-PROJ | warning | project | project released in week 9, late in a 13-week semester |
| assessment | VA-REG | warning | K07 | no endsem component although UGREG-2025§6.2 normally schedules one |
| cos | V11 | warning | CO5 | CO CO5 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 2 → 0 · round 1 accepted (2→1); round 2 accepted (1→0)
- los: errors 7 → 0 · round 1 accepted (7→3); round 2 accepted (3→0)
- structure: errors 5 → 0 · round 1 accepted (5→0)
- assessment: errors 4 → 0 · round 1 accepted (4→1); round 2 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- los: hours_total: Calculated total lecture hours (32), tutorial hours (11), and lab hours (23) are slightly below the exact budget of 39/13/26 due to indivisible module sizing, but remain within tolerance.
- resources: Lack of dedicated textbooks: AI-native software development and Model Context Protocol are emerging paradigms without established comprehensive textbooks, requiring reliance on recent research papers and technical documentation.

## Appendix F — Rationales (G11)

- **sequencing rationale:** Modules progress from foundational concepts of AI‑assisted coding (M1) to specification‑driven development (M2), then to configuring agents and protocols (M3). Mastery of specifications is required before applying iterative loop engineering (M4), which precedes testing and reliability evaluation (M5). The final integration project (M6) consolidates all prior skills, reflecting the prerequisite edges in the graph.
- **assessment rationale:** The mix of quizzes, assignments, a mid‑semester exam, a report, and a major project aligns with the cognitive levels of the COs: lower‑order knowledge is tested early, while higher‑order synthesis and evaluation are assessed through the project and report, matching the practical, workflow‑oriented emphasis.
- **positioning rationale:** Unlike CSE701, which focuses on mining software repositories and ML research, this course provides hands‑on experience with AI‑driven coding agents and workflow engineering, offering a distinct practical orientation for senior B.Tech CSE students.