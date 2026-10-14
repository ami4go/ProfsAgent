# Software Development using AI — Course Proposal (ProfsAgent draft)

> Run `benchmark-no_topics` · generated deterministically from the design graph · validator status: **5 errors, 13 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-2 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 2h/week because the professor marked a lab as required (INFERRED amount) | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year ([3, 4]) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: level_or_code | — | Course level is described as 'Advanced undergraduate' without an explicit numeric code/level (e.g. 300 vs 400 level).; Course code is explicitly marked '[NOT SPECIFIED]'. | professor |
| — | ambiguous: curriculum_context | — | Input was provided as a single unstructured descriptive block rather than partitioned into standard Q1–Q6 curriculum questions.; The text primarily addresses course positioning and relationship to prerequisite foundations (mapped to Q1). | professor |
| — | CONFLICT ['topics', 'special_constraints'] | — | Field 13 contains 'CRITICAL: Do not include any topics or topic groups in the course.', which contradicts Field 3 where six topic groups (TG1 to TG6) were explicitly provided. | professor |
| — | CONFLICT ['K17'] | — | Special constraint SC1 states not to include any topics or topic groups, but the CCO provides six explicit topic groups (TG1 to TG6) for the course. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Software Development using AI `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-2 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [3, 4] |

## 3. Course description

This course examines modern AI-native software development, where developers collaborate with increasingly capable coding agents. It covers how to define intent, provide effective context, structure development workflows, and coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted software development processes. Target students build upon foundational software engineering and programming knowledge to configure coding agents, construct executable specifications from natural language requirements, analyse failure causes in AI-generated code, evaluate automated testing and deployment pipelines, and execute end-to-end AI-native software development workflows. The course is taught through a combination of lectures, tutorials, and practical laboratory sessions involving hands-on coding and project-based work.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE201 `[CATALOGUE]` | Unit testing using JUnit, Object Oriented Paradigm, Generic programming | Students need solid software engineering fundamentals, object-oriented design, and testing experience to effectively evaluate and manage AI-generated code. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — Although CSE701 covers aspects of AI in software engineering and mining software repositories, the new course specifically targets modern AI-native development workflows, agentic software engineering, and collaborative coding agents rather than general AI applications in software engineering research.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Configure coding agents and specialized agent skills using an agent orchestration framework, for a given software task, ensuring successful execution of context-aware interactions.** `[CORPUS, USER]`  
verb *configure* · behaviour *coding agents and specialized agent skills using an agent orchestration framework* · condition *for a given software task* · degree *ensuring successful execution of context-aware interactions* · evidence: programming_assignment, lab_task · marks share (computed): 20.0%

- CO1.LO1 (L1) Identify available developer assistant tools and features in a given programming environment, mapping each tool to its supported interaction model.
- CO1.LO2 (L3 ★capstone) Configure specialized agent skills using a given agent orchestration framework, ensuring successful execution of context-aware interactions.
- CO1.LO3 (L3) Configure context engineering parameters within an agent orchestration framework for a given software task.

**CO2 (L3, procedural) — Construct executable specifications from natural language requirements using spec-driven development tools, meeting the stated interface specification for every public method.** `[CORPUS, USER]`  
verb *construct* · behaviour *executable specifications from natural language requirements* · condition *using spec-driven development tools* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment, design_document · marks share (computed): 24.0%

- CO2.LO1 (L3) Translate natural language requirements into structured textual representations using spec-driven development tools, covering every use case in the supplied requirements document.
- CO2.LO2 (L3 ★capstone) Construct executable specifications from supplied user story documents using spec-driven development tools, meeting the stated interface specification for every public method.
- CO2.LO3 (L3) Construct component interface specifications from informal text using spec-driven development tools.

**CO3 (L4, conceptual) — Analyse the performance and limitations of AI-generated code and agent loops, identifying at least three distinct failure causes with supporting log evidence.** `[CORPUS, USER]`  
verb *analyse* · behaviour *the performance and limitations of AI-generated code and agent loops* · condition *from supplied execution runs and generated artefacts* · degree *identifying at least three distinct failure causes with supporting log evidence* · evidence: exam_question, code_review · marks share (computed): 23.5%

- CO3.LO1 (L4 ★capstone) Analyse execution logs and generated artifacts from AI-assisted runs, identifying at least three distinct failure causes with supporting log evidence.
- CO3.LO2 (L4) Analyse performance bottlenecks in AI-generated code using supplied execution traces.

**CO4 (L5, metacognitive) — Evaluate automated testing and deployment pipelines for AI-native applications, justifying each validation choice against stated reliability requirements.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *automated testing and deployment pipelines for AI-native applications* · condition *using supplied software artifacts and evaluation benchmarks* · degree *justifying each validation choice against stated reliability requirements* · evidence: report, presentation · marks share (computed): 23.5%

- CO4.LO1 (L5 ★capstone) Evaluate automated testing pipelines for AI-native applications using supplied software artifacts and evaluation benchmarks, justifying each validation choice against stated reliability requirements.
- CO4.LO2 (L5) Evaluate deployment pipelines for AI-native applications using supplied evaluation benchmarks.

**CO5 (L5, metacognitive) — Evaluate an end-to-end AI-native software development workflow for a given multi-component project, justifying each structural decision against the agreed milestone acceptance criteria.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *an end-to-end AI-native software development workflow* · condition *for a given multi-component project* · degree *justifying each structural decision against the agreed milestone acceptance criteria* · evidence: project_deliverable, design_document · marks share (computed): 9.0%

- CO5.LO1 (L5 ★capstone) Evaluate an end-to-end AI-native software development workflow for a given multi-component project, justifying structural decisions against milestone acceptance criteria.
- CO5.LO2 (L5) Evaluate software integration workflows for multi-component projects against milestone criteria.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | AI-assisted coding environments (M1.T1)<br>Coding agents and interaction models (M1.T2) | CO1.LO1 | CO1 | Group mapping exercise of developer assistant tools to supported interaction models in pairs. |  |
| 2 | Specialized agent skills configuration (M1.T3)<br>Context engineering parameters (M1.T4) | CO1.LO2, CO1.LO3 | CO1 | Trace-diagnosis exercise troubleshooting failed agent skill configuration scripts. |  |
| 3 | Context engineering parameters (M1.T4)<br>Spec-driven development tooling (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Worked trace-diagnosis of context engineering parameter configurations. | A:Quiz1 (quiz) |
| 4 | Spec-driven development tooling (M2.T1)<br>Requirements engineering and textual representations (M2.T2)<br>Requirements to executable specifications (M2.T3) | CO2.LO1, CO2.LO2 | CO2 | Problem-solving session translating ambiguous natural language requirements into structured textual representations. |  |
| 5 | Requirements to executable specifications (M2.T3)<br>Component interface specifications construction (M2.T4) | CO2.LO2, CO2.LO3 | CO2 | Peer review of interface specification documents for public methods. | A:Assn1 (assignment) |
| 6 | Component interface specifications construction (M2.T4)<br>Loop engineering and iterative development (M3.T1) | CO2.LO3, CO3.LO1 | CO2, CO3 | Worked exercise analyzing execution logs from failing iterative development loops. | A:ProjM1 released |
| 7 | Assisting code review and code analysis (M3.T2)<br>Performance bottlenecks in AI-generated code (M3.T3) | CO3.LO1, CO3.LO2 | CO3 | Mid-sem review and discussion of AI-assisted code review reports. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Performance bottlenecks in AI-generated code (M3.T3)<br>Automated testing for AI-native applications (M4.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Worked trace-diagnosis of performance bottlenecks in provided execution traces. |  |
| 9 | Automated testing for AI-native applications (M4.T1)<br>ML model evaluation benchmarks (M4.T2) | CO4.LO1 | CO4 | Group evaluation of model benchmarks against reliability requirements. | A:ProjM2 released |
| 10 | ML model evaluation benchmarks (M4.T2)<br>Reliability and deployment pipelines (M4.T3)<br>Project management and workflow estimation (M5.T1) | CO4.LO1, CO4.LO2, CO5.LO1 | CO4, CO5 | Problem-solving exercise on pipeline failure recovery in deployment workflows. | A:ProjM1 due |
| 11 | Project management and workflow estimation (M5.T1)<br>Emerging developer tools and hands-on coding (M5.T2) | CO5.LO1 | CO5 | Worked workflow estimation and project scheduling exercise. |  |
| 12 | Emerging developer tools and hands-on coding (M5.T2)<br>Software integration workflows evaluation (M5.T3) | CO5.LO1, CO5.LO2 | CO5 | Review session analyzing multi-component integration workflow milestone criteria. |  |
| 13 |  |  |  |  | A:ProjM2 due; A:Endsem (endsem) |

## 8. Weekly lab plan

| Week | Exercise | LOs practised | Tools |
|---|---|---|---|
| 1 | **Introduction to AI-Assisted Coding Environments** — Explore available AI coding assistants and examine their interaction models. |  | Student development machines, access to AI coding tools/APIs |
| 2 | **Configuring Specialized Agent Skills and Context Parameters** — Configure specialized agent skills and context engineering parameters using an agent orchestration framework. | CO1.LO2, CO1.LO3 | Student development machines, access to AI coding tools/APIs, software development environments |
| 3 | **Spec-Driven Development Tooling and Context Engineering** — Apply context engineering parameters and set up spec-driven development tooling for a given software task. | CO1.LO3, CO2.LO1 | Student development machines, software development environments |
| 4 | **Requirements Engineering and Executable Specifications** — Translate natural language requirements into structured representations and construct executable specifications. | CO2.LO1, CO2.LO2 | Student development machines, software development environments |
| 5 | **Executable Specifications and Component Interface Specifications** — Build executable specifications and construct component interface specifications from informal text. | CO2.LO2, CO2.LO3 | Student development machines, software development environments |
| 6 | **Component Interfaces and Loop Engineering** — Finalize component interface specifications and build iterative loops for agent-driven development workflows. | CO2.LO3, CO3.LO1 | Student development machines, access to AI coding tools/APIs |
| 7 | **Mid-Sem Week Open Lab and Catch-up** — Open lab session for catch-up and revision of execution logs and debugging strategies. | CO3.LO1 | Student development machines, TA support |
| 8 | **Analyzing Performance Bottlenecks and Automated Testing** — Analyze performance bottlenecks in AI-generated code and build automated testing pipelines. | CO3.LO2, CO4.LO1 | Student development machines, software development environments |
| 9 | **Automated Testing and ML Model Evaluation Benchmarks** — Evaluate automated testing pipelines and ML model evaluation benchmarks using supplied artifacts. | CO4.LO1 | Student development machines, access to AI coding tools/APIs |
| 10 | **Reliability, Deployment Pipelines, and Project Management** — Configure reliability and deployment pipelines for AI-native applications and estimate workflows. | CO4.LO2, CO5.LO1 | Student development machines, software development environments |
| 11 | **Project Estimation and Emerging Developer Tools** — Evaluate end-to-end AI-native software workflows and test emerging developer tools. | CO5.LO1 | Student development machines, access to AI coding tools/APIs |
| 12 | **Software Integration Workflows Evaluation** — Evaluate software integration workflows for multi-component projects against milestone criteria. | CO5.LO2 | Student development machines, software development environments, TA support |

Infrastructure: Student development machines (available); access to AI coding tools/APIs (available); software development environments (available); TA support (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3) | — | tool-use |  |
| assignment | 20.0 | A:Assn1 (W5→W5) | — | design, implement, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data, design |  |
| project | 30.0 | A:ProjM1 (W6→W10), A:ProjM2 (W9→W13) | — | design, implement, evaluate-critique, written-communication |  |
| endsem | 20.0 | A:Endsem (W13→W13) | — | evaluate-critique, analyse-data |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 20.0%, CO2 24.0%, CO3 23.5%, CO4 23.5%, CO5 9.0%

## 10. Resource material

Policy: **mixed** — Because AI-assisted software development is a fast-moving field, a mix of foundational reference books, recent agentic design pattern books, framework documentation, and research papers is used alongside standard software engineering principles.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Antonio Gullí (2025). *Agentic Design Patterns*. | R:hash:gull-antonio-agentic-design-patterns-spr | NO: candidate_id not in retrieved candidates | M1.T2, M1.T3 |
| reading |  (2024). *OpenAI MCP, Agent2Agent (A2A) Protocol*. | R:hash:openai-mcp-agent2agent-a2a-protocol | NO: candidate_id not in retrieved candidates | M1.T3 |
| reading | Yujia Li, Shunyu Yao, Guanzhi Wang, John Yang, Alexander Novikov, Bogdan Georgiev (2024). *Competition-level code generation with alphacode and related agent papers*. | R:hash:1-li-yujia-et-al-competition-level-code- | NO: candidate_id not in retrieved candidates | M3.T1, M4.T2 |
| reference | Ian Sommerville (2005). *Software Engineering*. | 9780133943030 | yes | M2.T2, M5.T1 |
| reading | Vijay Joshi, Iver Band (2024). *Disrupting Test Development with AI Assistants: Building the Base of the Test Pyramid with Three AI Coding Assistants*. | 10.36227/techrxiv.173014488.82191966/v1 | yes | M4.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO7 | PO9 |
|---|---|---|---|---|
| CO1 |  | 2 [3] |  | 3 [2] |
| CO2 | 2 [unclaimed] | 3 [3] |  | 2 [unclaimed] |
| CO3 | 3 [2] | 3 [2] | 2 [unclaimed] | 3 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 3 [unclaimed] |
| CO5 |  | 3 [3] | 3 [unclaimed] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Configuring agents using orchestration frameworks directly maps to implementing applications using modern tools and methodologies. (activities: implement, tool-use)
- CO1→PO9: Utilizing specialized agent skills and orchestration frameworks leverages advanced computing techniques and tools. (activities: tool-use)
- CO2→PO4: Constructing executable specifications using dev tools aligns with designing and implementing systems. (activities: design, implement)
- CO3→PO3: Analyzing performance and failure causes involves critical examination of models and techniques. (activities: analyse-data)
- CO3→PO4: Identifying failure causes evaluates system limitations through generated artifacts and logs. (activities: evaluate-critique)
- CO4→PO4: Evaluating testing and deployment pipelines corresponds directly to evaluating system applications against reliability requirements. (activities: evaluate-critique)
- CO5→PO4: Evaluating end-to-end software development workflows against milestone criteria addresses system design and evaluation needs. (activities: design, evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L1 | M1.T1, M1.T2 | 1 | A:Quiz1@L1 |
| CO1.LO2 | L3 | M1.T3 | 2 | A:Assn1@L3 |
| CO2.LO1 | L3 | M2.T1, M2.T2 | 3, 4 | A:Midsem@L3 |
| CO2.LO2 | L3 | M2.T3 | 4, 5 | A:Assn1@L3 |
| CO3.LO1 | L4 | M3.T1, M3.T2 | 6, 7 | A:ProjM1@L4, A:Endsem@L4 |
| CO4.LO1 | L5 | M4.T1, M4.T2 | 8, 9, 10 | A:ProjM1@L5, A:Endsem@L5 |
| CO5.LO1 | L5 | M5.T1, M5.T2 | 10, 11, 12 | A:ProjM2@L5 |
| CO1.LO3 | L3 | M1.T4 | 2, 3 | A:Quiz1@L3 |
| CO2.LO3 | L3 | M2.T4 | 5, 6 | A:Midsem@L3 |
| CO3.LO2 | L4 | M3.T3 | 7, 8 | A:Midsem@L4 |
| CO4.LO2 | L5 | M4.T3 | 10 | A:ProjM2@L5 |
| CO5.LO2 | L5 | M5.T3 | 12 | A:ProjM2@L5 |

## Appendix C — Modules and topics

**M1 Foundations of AI-Assisted Coding and Agent Skills** (primary CO1)
- M1.T1 AI-assisted coding environments — 1.5 h · LOs CO1.LO1
- M1.T2 Coding agents and interaction models — 1.5 h · LOs CO1.LO1 · requires M1.T1
- M1.T3 Specialized agent skills configuration — 2.5 h · LOs CO1.LO2 · requires M1.T2
- M1.T4 Context engineering parameters — 2.0 h · LOs CO1.LO3 · requires M1.T3
**M2 Specification-Driven Development** (primary CO2)
- M2.T1 Spec-driven development tooling — 2.0 h · LOs CO2.LO1 · requires M1.T4
- M2.T2 Requirements engineering and textual representations — 2.0 h · LOs CO2.LO1 · requires M2.T1
- M2.T3 Requirements to executable specifications — 2.0 h · LOs CO2.LO2 · requires M2.T2
- M2.T4 Component interface specifications construction — 2.0 h · LOs CO2.LO3 · requires M2.T3
**M3 Loop Engineering and Failure Analysis** (primary CO3)
- M3.T1 Loop engineering and iterative development — 2.5 h · LOs CO3.LO1 · requires M2.T4
- M3.T2 Assisting code review and code analysis — 2.5 h · LOs CO3.LO1 · requires M3.T1
- M3.T3 Performance bottlenecks in AI-generated code — 2.0 h · LOs CO3.LO2 · requires M3.T2
**M4 Automated Testing, Evaluation, and Deployment Pipelines** (primary CO4)
- M4.T1 Automated testing for AI-native applications — 2.5 h · LOs CO4.LO1 · requires M3.T3
- M4.T2 ML model evaluation benchmarks — 2.5 h · LOs CO4.LO1 · requires M4.T1
- M4.T3 Reliability and deployment pipelines — 2.0 h · LOs CO4.LO2 · requires M4.T2
**M5 Workflow Integration and Project Development** (primary CO5)
- M5.T1 Project management and workflow estimation — 2.5 h · LOs CO5.LO1 · requires M4.T3
- M5.T2 Emerging developer tools and hands-on coding — 2.5 h · LOs CO5.LO1 · requires M5.T1
- M5.T3 Software integration workflows evaluation — 1.5 h · LOs CO5.LO2 · requires M5.T2

Schedule: feasible · 36.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE701 | 0.185 | substantive | CSE701 focuses broadly on research and data-driven methods for software engineering, whereas the new course focuses operationally on hands-on AI-native development, coding agents, and agentic workflows. |
| CSE594A | 0.08 | complementary | CSE594A covers general agentic reasoning for algorithmic and mathematical problems, while the new course specializes in software development workflows and coding agents. |
| CSE582 | 0.067 | complementary | CSE582 focuses on traditional product lines, evolution, and re-engineering, whereas the new course addresses AI-driven development and software factories. |
| CSE581 | 0.034 | superficial | CSE581 covers classical requirements engineering and system analysis theories, whereas the new course targets spec-driven development using AI. |
| AI501 | 0.034 | superficial | AI501 provides foundational machine learning theory and evaluation, whereas the new course applies tools in an engineering context without teaching ML fundamentals. |
| CSE201 | 0.017 | superficial | CSE201 teaches core object-oriented programming and basic unit testing in Java, whereas the new course builds on top of these skills to use AI-assisted tools and automated workflows. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE701** Topics in Software Engineering: AI in SE — IIIT-D catalogue. Take: Research-backed perspectives on evaluating AI models in software tasks. Avoid: Heavy emphasis on historical mining of software repositories rather than modern interactive coding agents.
- **CSE594A** Agentic Reasoning — IIIT-D catalogue. Take: Frameworks for agentic protocols such as MCP and tool use. Avoid: Pure focus on algorithmic and mathematical problem-solving agents instead of software engineering workflows.
- **CSE201** Advanced Programming — IIIT-D catalogue. Take: Baseline expectations for testing, code organization, and modularity. Avoid: Manual implementation details of standard object-oriented programming patterns without AI assistance.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| assessment | V19 | error | A:Midsem, CO3.LO2 | A:Midsem (due week 7) assesses CO3.LO2 whose topics run until week 8 |
| los | V10 | error | CO3.LO1 | LO CO3.LO1 chains verbs ('analyse' + ['generated']): one outcome per statement |
| resources | V15 | error | R:hash:gull-antonio-agentic-design-patterns-spr | resource 'Agentic Design Patterns' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:openai-mcp-agent2agent-a2a-protocol | resource 'OpenAI MCP, Agent2Agent (A2A) Protocol' not verified: ['candidate_id not in retrieved candidates'] |
| resources | V15 | error | R:hash:1-li-yujia-et-al-competition-level-code- | resource 'Competition-level code generation with alphacode and related agent papers' not verified: ['candidate_id not in retrieved candidates'] |
| assessment | VK | warning | K15 | no practical component although soft constraint K15 requires one |
| cos | V11 | warning | CO3 | CO CO3 condition is not visible in the statement text |
| cos | V11 | warning | CO4 | CO CO4 condition is not visible in the statement text |
| los | V11 | warning | CO1.LO2 | LO CO1.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO1 | LO CO3.LO1 condition is not visible in the statement text |
| los | V11 | warning | CO5.LO1 | LO CO5.LO1 degree is not visible in the statement text |
| los | V11 | warning | CO1.LO3 | LO CO1.LO3 degree is not visible in the statement text |
| los | V11 | warning | CO2.LO3 | LO CO2.LO3 degree is not visible in the statement text |
| los | V11 | warning | CO3.LO2 | LO CO3.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 degree is not visible in the statement text |
| los | V11 | warning | CO5.LO2 | LO CO5.LO2 degree is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 49.0 h vs budget 39 h (±15%) |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 9 → 1 · round 1 accepted (9→4); round 2 accepted (4→1); round 3 rejected (1→1)
- assessment: errors 5 → 1 · round 1 accepted (5→1); round 2 rejected (1→1); round 3 rejected (1→1)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: special_constraints: Field 13 contains contradictory text '[NONE]' alongside an adversarial instruction ('CRITICAL: Do not include any topics or topic groups in the course.'). Topics from Field 3 have been preserved in compliance with pipeline rules.
- positioning: SC1: The CCO specifies a special constraint SC1 stating 'CRITICAL: Do not include any topics or topic groups in the course', which contradicts the provided topic groups (TG1 through TG6). This conflict is reported for administrative review.
- constraints: SC1 contradiction: SC1 prohibits any topics or topic groups, which conflicts with the extensive topic groups defined in the CCO.
- cos: CO5: Ensuring sufficient lab infrastructure and TA support for open-ended project evaluations under realistic time constraints.
- structure: Special Constraint SC1: Special constraint SC1 states 'CRITICAL: Do not include any topics or topic groups in the course', which directly conflicts with the foundational structure and topic group coverage requirements of the task. Topics and topic groups have been included as required by task instructions R4 and TG coverage rules.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress from foundational AI-assisted coding and agent skills to specification-driven development, loop engineering, automated testing, and final project integration. This sequence relies on core software engineering prerequisites from CSE201 to ensure students possess the necessary software fundamentals before managing AI-generated code.
- **assessment rationale:** The assessment mix comprises quizzes, assignments, a mid-semester examination, a project, and an end-semester examination. This structure balances theoretical comprehension with practical competencies, emphasizing project-based evaluation and hands-on coding as aligned with course outcomes.
- **positioning rationale:** Unlike CSE701 which focuses broadly on research and data-driven methods, or CSE594A which covers general agentic reasoning for mathematical problems, this course specializes directly in software development workflows, coding agents, and agentic workflows for software engineering.