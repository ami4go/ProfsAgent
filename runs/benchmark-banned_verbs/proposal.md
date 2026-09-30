# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-banned_verbs` · generated deterministically from the design graph · validator status: **0 errors, 13 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | The course level is stated as Advanced undergraduate, but no explicit course code or numeric level has been provided. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with increasingly capable coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. Students will be able to configure AI-assisted coding tools and agent workflows, construct executable specifications and Model Context Protocol integrations, analyse iterative loop engineering workflows and agent-generated code, evaluate automated testing and deployment pipelines, and assess complete AI-native software development processes for multi-module applications. The course is taught through lectures, tutorials, and laboratory sessions involving hands-on projects and emerging developer tools.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Collection framework, Exception handling | Students need foundational software development, object-oriented principles, and unit testing practices to evaluate and build reliable software using AI coding assistants. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — While CSE701 covers AI in software engineering with a weighted Jaccard overlap of 0.118, it focuses on mining software repositories, defect prediction, and data-driven SE research at the graduate level (level 7). The new course focuses on modern AI-native development, coding agents, MCP, and developer workflows at level 3.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure AI-assisted coding tools and coding agent workflows for a supplied software project repository, such that at least 80% of the provided test cases pass and all tool configurations satisfy repository interface guidelines.** `[CORPUS, USER]`  
verb *Configure* · behaviour *AI-assisted coding tools and coding agent workflows* · condition *for a supplied software project repository* · degree *such that at least 80% of the provided test cases pass and all tool configurations satisfy repository interface guidelines* · evidence: programming_assignment, lab_task · marks share (computed): 10.5%

- CO1.LO1 (L1) Identify the core components and developer workflows of AI-assisted coding tools for a supplied software project repository
- CO1.LO2 (L3 ★capstone) Configure AI-assisted coding tools and coding agent workflows for a supplied software project repository

**CO2 (L3, procedural) — Construct executable specifications and Model Context Protocol (MCP) tool integrations from given requirements documents, covering every use case in the supplied requirements document and justifying each tool integration decision against stated constraints.** `[CORPUS, USER]`  
verb *Construct* · behaviour *executable specifications and Model Context Protocol (MCP) tool integrations* · condition *from given requirements documents* · degree *covering every use case in the supplied requirements document and justifying each tool integration decision against stated constraints* · evidence: design_document, programming_assignment · marks share (computed): 22.5%

- CO2.LO1 (L3) Construct executable specifications from given requirements documents for a supplied software task
- CO2.LO2 (L3 ★capstone) Construct Model Context Protocol (MCP) tool bindings for a supplied module configuration, ensuring message schema compliance and correct parameter mapping

**CO3 (L4, conceptual) — Analyse iterative loop engineering workflows and agent-generated code for a supplied software artifact of at most 5,000 lines, identifying at least three distinct failure causes with supporting log evidence and a proposed fix for each.** `[CORPUS, USER]`  
verb *Analyse* · behaviour *iterative loop engineering workflows and agent-generated code* · condition *for a supplied software artifact of at most 5,000 lines* · degree *identifying at least three distinct failure causes with supporting log evidence and a proposed fix for each* · evidence: code_review, exam_question · marks share (computed): 27.0%

- CO3.LO1 (L4) Examine iterative loop engineering workflows and agent-generated code for a supplied software artifact of at most 5,000 lines
- CO3.LO2 (L4 ★capstone) Analyse execution trace logs for a supplied software artifact of at most 5,000 lines, identifying at least three distinct failure causes with supporting log evidence and a proposed fix for each

**CO4 (L5, metacognitive) — Evaluate the reliability, correctness, and performance of automated testing and deployment pipelines generated by AI coding agents, benchmarking them against standard baseline metrics and justifying each evaluation decision against stated requirements.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *the reliability, correctness, and performance of automated testing and deployment pipelines generated by AI coding agents* · condition *against standard baseline metrics* · degree *justifying each evaluation decision against stated requirements and covering every use case in the supplied requirements document* · evidence: design_document, report · marks share (computed): 30.0%

- CO4.LO1 (L5) Assess the reliability and correctness of automated testing and deployment pipelines generated by AI coding agents
- CO4.LO2 (L5 ★capstone) Evaluate the execution speed of automated testing pipelines generated by AI coding agents, benchmarking them against standard baseline metrics and justifying each evaluation decision against stated requirements

**CO5 (L5, procedural) — Evaluate a complete AI-native software development process for a multi-module application, demonstrated live with 3 scenario walkthroughs chosen by the evaluator and satisfying every acceptance criterion agreed at the first milestone.** `[CORPUS, USER]`  
verb *Evaluate* · behaviour *a complete AI-native software development process for a multi-module application* · condition *using integrated coding agents, MCP tools, and iterative loop engineering frameworks* · degree *demonstrated live, with 3 scenario walkthroughs chosen by the evaluator such that the delivered system satisfies every acceptance criterion agreed at the first milestone* · evidence: project_deliverable, presentation · marks share (computed): 10.0%

- CO5.LO1 (L3) Implement integrated coding agents, MCP tools, and iterative loop engineering frameworks for a multi-module application
- CO5.LO2 (L5 ★capstone) Evaluate a multi-module application developed via an AI-native software development process, demonstrated live, with 3 scenario walkthroughs chosen by the evaluator such that the delivered system satisfies every acceptance criterion agreed at the first milestone

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding developer workflows (M1.T1)<br>Coding agents setup and configuration (M1.T2) | CO1.LO1, CO1.LO2 | CO1 | Trace-mapping exercise of core components in AI-assisted coding repositories, in pairs. |  |
| 2 | Coding agents setup and configuration (M1.T2)<br>Coding agents advanced setup (M1.T3)<br>Requirements to executable specifications (M2.T1) | CO1.LO2, CO2.LO1 | CO1, CO2 | Worked trace-diagnosis of agent setup configuration errors, in pairs. |  |
| 3 | Requirements to executable specifications (M2.T1)<br>MCP tool use and context engineering (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Requirement translation exercise: converting unstructured requirement paragraphs into structured executable specifications, individually. | A:PA1 released |
| 4 | MCP tool use and context engineering (M2.T2)<br>Advanced context engineering (M2.T3) | CO2.LO2 | CO2 | MCP message schema compliance review and parameter mapping correction drill, in pairs. |  |
| 5 | Advanced context engineering (M2.T3)<br>Iterative development loops (M3.T1) | CO2.LO2, CO3.LO1 | CO2, CO3 | Code review exercise examining agent-generated code artifacts of up to 5,000 lines for iterative loop flaws, in groups. | A:PA1 due; A:PA2 released |
| 6 | Iterative development loops (M3.T1)<br>Software factories and loop failure analysis (M3.T2)<br>Software factories failure analysis (M3.T3) | CO3.LO1, CO3.LO2 | CO3 | Trace log analysis exercise: identifying distinct failure causes and drafting fixes from provided logs, individually. |  |
| 7 | Software factories failure analysis (M3.T3)<br>Automated testing and reliability (M4.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Mid-sem review and discussion on evaluating automated testing and deployment pipelines, in groups. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Automated testing and reliability (M4.T1)<br>Deployment evaluation and reliability benchmarking (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Report drafting exercise assessing reliability and correctness of agent-generated testing pipelines, individually. | A:PA2 due; A:PR1 released |
| 9 | Deployment evaluation and reliability benchmarking (M4.T2)<br>Reliability benchmarking (M4.T3)<br>Hands-on projects and emerging developer tools (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Reliability benchmarking metric evaluation and decision justification drill, in pairs. |  |
| 10 | Hands-on projects and emerging developer tools (M5.T1)<br>End-to-end practical development workflow evaluation (M5.T2) | CO5.LO1, CO5.LO2 | CO5 | Multi-module architecture integration planning and milestone acceptance criteria review, in groups. | A:PR1 due; A:PR2 released |
| 11 | End-to-end practical development workflow evaluation (M5.T2)<br>Emerging developer tools practicals (M5.T3)<br>End-to-end practical workflow evaluation (M5.T4) | CO5.LO1, CO5.LO2 | CO5 | Scenario walkthrough preparation and acceptance criteria verification drill, in pairs. |  |
| 12 | End-to-end practical workflow evaluation (M5.T4) | CO5.LO2 | CO5 | Mock live evaluation walkthrough and peer critique of end-to-end development workflows, in groups. | A:PR2 due; A:PR3 released |
| 13 |  |  |  |  | A:Endsem (endsem); A:PR3 due |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Coding agents setup and configuration** — Configure local coding agent development environments and verify basic plugin operation. | CO1.LO2 | Student development machines, software development environments |
| 2 | **Advanced coding agents setup and executable specifications** — Set up advanced coding agent parameters and construct initial executable specifications from requirements. | CO1.LO2, CO2.LO1 | Student development machines, access to AI coding tools/APIs |
| 3 | **Executable specifications and MCP tool bindings** — Build executable specifications and construct Model Context Protocol (MCP) tool bindings ensuring schema compliance. | CO2.LO1, CO2.LO2 | Student development machines, access to AI coding tools/APIs |
| 4 | **Advanced context engineering and MCP bindings** — Implement advanced context engineering strategies and configure complex MCP tool bindings. | CO2.LO2 | Student development machines, access to AI coding tools/APIs |
| 5 | **Context engineering practice** — Practice advanced context engineering techniques for agent-driven workflows. | CO2.LO2 | Student development machines |
| 6 | **Software factories and loop failure analysis** — Analyze execution trace logs from software factories, identifying failure causes and proposing fixes. | CO3.LO2 | Student development machines |
| 7 | **Midterm week open lab / catch-up** — Catch-up session and open lab practice for trace log analysis. | CO3.LO2 | Student development machines |
| 8 | **Deployment evaluation and reliability benchmarking** — Benchmark automated testing pipeline execution speeds against baseline metrics. | CO4.LO2 | Student development machines |
| 9 | **Reliability benchmarking and developer tools** — Execute reliability benchmarking suites and experiment with emerging developer tools. | CO4.LO2, CO5.LO1 | Student development machines, access to AI coding tools/APIs |
| 10 | **End-to-end practical development workflow evaluation** — Implement integrated coding agents and MCP tools for a multi-module application. | CO5.LO1, CO5.LO2 | Student development machines, software development environments |
| 11 | **Emerging developer tools practicals** — Perform practical integration of emerging developer tools within multi-module project setups. | CO5.LO1 | Student development machines |
| 12 | **End-to-end workflow evaluation walkthroughs** — Conduct live demonstration and scenario walkthroughs of the final multi-module application. | CO5.LO2 | Student development machines |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (needs_confirmation); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data | Standard weight for mid-semester evaluation covering the first half of the course. |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data | Standard weight for end-semester comprehensive evaluation. |
| practical_assignment | 25.0 | A:PA1 (W3→W5), A:PA2 (W5→W8) | — | design, implement, tool-use | Weight allocated to hands-on programming and design tasks to reinforce tool configuration and MCP bindings. |
| project | 30.0 | A:PR1 (W8→W10), A:PR2 (W10→W12), A:PR3 (W12→W13) | — | design, evaluate-critique, oral-presentation | Substantial project weight to evaluate end-to-end integration and live scenario-based walkthroughs. |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 10.5%, CO2 22.5%, CO3 27.0%, CO4 30.0%, CO5 10.0%

## 10. Resource material

Policy: **reading_list** — As modern AI-native software development and coding agents represent a rapidly evolving field without established standard textbooks covering all aspects, a curated reading list of recent peer-reviewed conference and journal articles is used.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| reading | Shyam Agarwal, Hao He, Bogdan Vasilescu (2026). *AI IDEs or Autonomous Agents? Measuring the Impact of Coding Agents on Software Development*. | 10.1145/3793302.3793589 | yes | M1.T1, M1.T2 |
| reading | Prof Dr Oliver Koch (2026). *From Vibe to Value - How Specification-Driven Development Professionalizes AI Coding*. | 10.2139/ssrn.6453101 | yes | M2.T1 |
| reading | John E. Robert, Ipek Ozkaya, Douglas C. Schmidt (2026). *Transforming Software Engineering and Software Acquisition with Large Language Models*. | 10.1201/9781003492252-7 | yes | M2.T2, M2.T3 |
| reading | Praneeth Kodumagulla (2026). *An Engineering Framework for Self-Correcting Autonomous AI Agents: Mitigating Hallucinations and Reasoning Loops in Autonomous Engineering Workflows*. | 10.2139/ssrn.6759126 | yes | M3.T1, M3.T2 |
| reading | Nithya A, Sivasankaran V (2026). *Vulnerability Detection in AI‐Generated and Human‐Written Code of Multiple Programming Languages With Structured Learning*. | 10.1002/stvr.70021 | yes | M4.T1, M4.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 | 1 [unclaimed] | 3 [3] |  | 3 [2] |
| CO2 | 1 [unclaimed] | 3 [3] |  | 3 [unclaimed] |
| CO3 | 3 [2] |  |  |  |
| CO4 | 2 [unclaimed] | 3 [3] | 3 [unclaimed] | 3 [unclaimed] |
| CO5 |  | 3 [3] | 3 [unclaimed] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring tools and workflows directly implements development environments using modern tools. (activities: implement, tool-use)
- CO1→PO9: Involves applying advanced AI coding tools and agentic workflows. (activities: tool-use)
- CO2→PO4: Constructing specifications and tool integrations fulfills system design and implementation requirements. (activities: design, implement)
- CO3→PO3: Analyzing workflows and identifying failures adapts problem-solving techniques to agent-generated code. (activities: analyse-data)
- CO4→PO4: Evaluating automated testing and deployment pipelines covers the evaluation aspect of system engineering. (activities: evaluate-critique, design)
- CO5→PO4: Demonstrating and evaluating a complete multi-module development process satisfies end-to-end system evaluation. (activities: evaluate-critique, design)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1 | 1 | A:Midsem@L1 |
| CO1.LO2 | L3 | M1.T2, M1.T3 | 1, 2 | A:PA1@L3 |
| CO2.LO1 | L3 | M2.T1 | 2, 3 | A:Midsem@L3, A:PA1@L3 |
| CO2.LO2 | L3 | M2.T2, M2.T3 | 3, 4, 5 | A:PA2@L3 |
| CO3.LO1 | L4 | M3.T1 | 5, 6 | A:Endsem@L4 |
| CO3.LO2 | L4 | M3.T2, M3.T3 | 6, 7 | A:Midsem@L4, A:Endsem@L4 |
| CO4.LO1 | L5 | M4.T1 | 7, 8 | A:Endsem@L5, A:PR1@L5 |
| CO4.LO2 | L5 | M4.T2, M4.T3 | 8, 9 | A:PR2@L5 |
| CO5.LO1 | L3 | M5.T1, M5.T3 | 9, 10, 11 | A:PR3@L3 |
| CO5.LO2 | L5 | M5.T2, M5.T4 | 10, 11, 12 | A:PR3@L5 |

## Appendix C — Modules and topics

**M1 AI-Assisted Coding Tools and Developer Workflows** (primary CO1)
- M1.T1 AI-assisted coding developer workflows — 2.0 h · LOs CO1.LO1
- M1.T2 Coding agents setup and configuration — 1.75 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Coding agents advanced setup — 1.75 h · LOs CO1.LO2 · requires M1.T2
**M2 Specification-Driven Development and MCP Integration** (primary CO2)
- M2.T1 Requirements to executable specifications — 3.0 h · LOs CO2.LO1 · requires M1.T2
- M2.T2 MCP tool use and context engineering — 2.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Advanced context engineering — 2.0 h · LOs CO2.LO2 · requires M2.T2
**M3 Iterative Loop Engineering and Failure Analysis** (primary CO3)
- M3.T1 Iterative development loops — 3.0 h · LOs CO3.LO1 · requires M2.T2
- M3.T2 Software factories and loop failure analysis — 2.0 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Software factories failure analysis — 2.0 h · LOs CO3.LO2 · requires M3.T2
**M4 Automated Testing, Reliability, and Deployment Evaluation** (primary CO4)
- M4.T1 Automated testing and reliability — 3.0 h · LOs CO4.LO1 · requires M3.T2
- M4.T2 Deployment evaluation and reliability benchmarking — 2.0 h · LOs CO4.LO2 · requires M4.T1
- M4.T3 Reliability benchmarking — 2.0 h · LOs CO4.LO2 · requires M4.T2
**M5 Project Integration and End-to-End Evaluation** (primary CO5)
- M5.T1 Hands-on projects and emerging developer tools — 2.0 h · LOs CO5.LO1 · requires M4.T2
- M5.T2 End-to-end practical development workflow evaluation — 2.25 h · LOs CO5.LO2 · requires M5.T1
- M5.T3 Emerging developer tools practicals — 2.0 h · LOs CO5.LO1 · requires M5.T1
- M5.T4 End-to-end practical workflow evaluation — 2.25 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 35.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.118 | complementary | CSE701 explores data-driven software engineering and research literature analysis at level 7, whereas the new course provides practical workflow-oriented instruction on agentic software development and coding agents at level 3. |
| CSE581 | 0.062 | superficial | CSE581 covers traditional systems analysis and requirements engineering theories, while the new course addresses executable specifications and requirements in an AI-native coding context. |
| CSE582 | 0.118 | complementary | CSE582 focuses on software product lines, legacy systems, and maintenance, whereas the new course examines iterative loop engineering and agentic software factories. |
| CSE594A | 0.077 | complementary | CSE594A is a 2-credit course focused broadly on agentic reasoning and algorithmic/mathematical problem solving, whereas the new course is a 4-credit course dedicated specifically to software development workflows, coding agents, and engineering practice. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Core concepts of agentic protocols, MCP, and tool use for coding agents. Avoid: Focusing solely on algorithmic and mathematical problem-solving rather than software development workflows.
- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Assessment strategies for AI-assisted code review and refactoring. Avoid: Graduate-level mining of software repositories and empirical software engineering research focus.
- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Project-based evaluation structure and collaborative tooling integration. Avoid: Extensive focus on traditional open source licensing and community governance models.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| assessment | VA-PROJ | warning | project | project released in week 8, late in a 13-week semester |
| cos | V11 | warning | CO5 | CO CO5 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO1 | LO CO1.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO1 | LO CO2.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO2 | LO CO2.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO2.LO2 | LO CO2.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO1 | LO CO4.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 condition is not visible in the statement text |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 5 → 0 · round 1 accepted (5→1); round 2 accepted (1→0)
- structure: errors 6 → 0 · round 1 accepted (6→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: The special constraint mandates using the exact verb 'understand' for all Course Outcomes, which may conflict with Bloom's Taxonomy verb requirements typically enforced by downstream curriculum rules.
- constraints: Special Constraint SC1: The requirement to use the exact verb 'understand' for all Course Outcomes conflicts with standard Bloom's taxonomy guidelines for higher-level courses (level 3).
- cos: SC1: Special constraint SC1 mandates the exact verb 'understand' for all Course Outcomes, but the system instruction and Bloom band rules explicitly ban 'understand' and require observable action verbs. We prioritized valid lexicon verbs over SC1 to comply with institutional course design policy.
- los: Special Constraint SC1: Special constraint SC1 asks to use the exact verb 'understand' for all Course Outcomes, but standard IIIT-D Bloom taxonomy rules and the verb lexicon explicitly ban 'understand' as a measurable assessment verb. The existing COs use valid Bloom verbs (Configure, Construct, Analyse, Evaluate). The LOs follow valid Bloom taxonomy levels accordingly.
- structure: Course Outcomes Verb Convention: Special constraint SC1 requires all Course Outcomes to use the exact verb 'understand', whereas the provided COs and LOs use higher-level cognitive verbs.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules follow a structured progression starting with foundational AI-assisted coding tools and developer workflows in M1, advancing to specification-driven development and Model Context Protocol integration in M2, moving through iterative loop engineering and failure analysis in M3, covering automated testing, reliability, and deployment evaluation in M4, and culminating in project integration and end-to-end evaluation in M5. This sequence relies on foundational programming and software engineering principles established in prerequisite coursework such as CSE201.
- **assessment rationale:** The assessment mix comprises midsem examinations, endsem examinations, practical assignments, and a course project. This balanced combination aligns with the course outcomes by testing both conceptual understanding through examinations and practical competence in configuring tools, building specifications, analyzing failures, and executing end-to-end AI-native development workflows through assignments and project work.
- **positioning rationale:** Unlike CSE701, which explores data-driven software engineering and research literature at level 7, this course provides practical workflow-oriented instruction on agentic software development and coding agents at level 3. It differs from CSE581, which covers traditional requirements engineering, by focusing on executable specifications in an AI-native context. It complements CSE582 by addressing iterative loop engineering rather than legacy maintenance, and expands upon CSE594A by offering a 4-credit curriculum dedicated to software development workflows and engineering practice.