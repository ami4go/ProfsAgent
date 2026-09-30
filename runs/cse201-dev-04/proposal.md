# Advanced Programming — Course Proposal (ProfsAgent draft)

> Run `cse201-dev-04` · generated deterministically from the design graph · validator status: **0 errors, 11 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM02 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |
| — | ambiguous: target_students | — | Taken by B.Tech. CSE as a core course and potentially other unspecified B.Tech. programmes as electives or open courses. | professor |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 2xx) |
| Course Name | Advanced Programming `[USER]` |
| Credits | 4 |
| L-T-P | 3.0-1.0-0 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [2] |

## 3. Course description

Advanced Programming is a second-year course that transitions students from small, single-file programs to larger, component-based applications with well-defined interfaces. Building on foundational programming and data‑structures knowledge, the course develops competence in object‑oriented design, reusable generic components, systematic testing, and concurrent execution. Students learn to apply design patterns, construct robust code through generics and exception handling, and create event‑driven graphical interfaces. Throughout the term, they work in pairs on a substantial project that integrates these concepts, delivering a tested, multi‑component Java application. Instruction combines lectures with regular hands‑on practice, including tutorials, quizzes, assignments, and examinations.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE101 `[CATALOGUE]` | classes, objects, inheritance, Exception handling, assertions | Students need foundational familiarity with basic programming constructs, functions, and introductory object concepts before moving to advanced object-oriented design and application structuring. |
| mandatory | CSE102 `[CATALOGUE]` | Handling arrays, methods, linear search, sorting, Linked lists, stacks, queues, trees | Understanding standard data structures and algorithmic complexity is required before utilizing collection frameworks and building multi-component applications. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — Although CSE600 covers Object Oriented Programming and Design, it is a 6xx-level postgraduate/advanced cross-listed course with an anti-requisite against CSE101/CSE201, whereas the proposed course is a 200-level core/elective undergraduate course (Level 2) intended to bridge introductory programming and advanced software systems for BTech CSE second-year students.

## 5. Bloom band

L2–L5 · basis: level 2xx band [2,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Implement object-oriented hierarchies using classes, interfaces, and polymorphism, given a problem specification, such that all public tests pass and no warnings from the configured static analyser.** `[CORPUS, USER]`  
verb *implement* · behaviour *object-oriented hierarchies using classes, interfaces, and polymorphism* · condition *given a problem specification* · degree *such that all public tests pass and no warnings from the configured static analyser* · evidence: programming_assignment · marks share (computed): 18.33%

- CO1.LO1 (L3) Implement class definitions and object relationships including association and composition, given a set of basic class requirements, such that all public tests pass and no warnings from the configured static analyser.
- CO1.LO2 (L3 ★capstone) Implement inheritance hierarchies, abstract classes, and polymorphism via interfaces, given an abstract class specification, such that all public tests pass and no warnings from the configured static analyser.

**CO2 (L3, procedural) — Construct reusable and robust components using generics, the collections framework, and structured exception handling, given a set of software requirements, meeting the stated interface specification for every public method.** `[USER]`  
verb *construct* · behaviour *reusable and robust components using generics, the collections framework, and structured exception handling* · condition *given a set of software requirements* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment, code_review · marks share (computed): 18.33%

- CO2.LO1 (L3) Construct generic classes and methods along with object collections, given a data processing requirement, meeting the stated interface specification for every public method.
- CO2.LO2 (L3 ★capstone) Construct robust components using structured exception handling, assertions, and defensive programming, given a fault-prone operational context, meeting the stated interface specification for every public method.

**CO3 (L3, procedural) — Apply established design patterns and unit testing frameworks, given a modular software design problem, such that at least 80% of the provided test cases pass.** `[USER]`  
verb *apply* · behaviour *established design patterns and unit testing frameworks* · condition *given a modular software design problem* · degree *such that at least 80% of the provided test cases pass* · evidence: programming_assignment, code_review · marks share (computed): 16.67%

- CO3.LO1 (L3) Test software units using unit testing frameworks and assertions, given an untested codebase, such that at least 80% of the provided test cases pass.
- CO3.LO2 (L3 ★capstone) Apply established design patterns to solve structural and behavioral programming problems, given a modular software design problem, such that at least 80% of the provided test cases pass.

**CO4 (L3, procedural) — Develop concurrent multi-threaded programs using synchronization primitives and thread pools, given a throughput-bound task specification, identifying at least three distinct synchronization causes for potential race conditions with supporting log evidence.** `[CORPUS, USER]`  
verb *develop* · behaviour *concurrent multi-threaded programs using synchronization primitives and thread pools* · condition *given a throughput-bound task specification* · degree *identifying at least three distinct synchronization causes for potential race conditions with supporting log evidence* · evidence: programming_assignment, exam_question · marks share (computed): 25.0%

- CO4.LO1 (L3) Demonstrate thread creation, execution, and thread pool management, given a concurrent sub-task specification, identifying at least three distinct synchronization causes for potential race conditions with supporting log evidence.
- CO4.LO2 (L3 ★capstone) Write concurrent worker threads using synchronization primitives and mutual exclusion, given a throughput-bound task specification, identifying at least three distinct synchronization causes for potential race conditions with supporting log evidence.

**CO5 (L5, metacognitive) — Evaluate a multi-component application with a graphical interface, given a requirements document and design patterns, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *a multi-component application with a graphical interface* · condition *given a requirements document and design patterns* · degree *such that the delivered system satisfies every acceptance criterion agreed at the first milestone* · evidence: project_deliverable, presentation · marks share (computed): 25.0%

- CO5.LO1 (L4) Examine object-oriented design diagrams, use cases, and graphical interface requirements, given a software requirements document, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.
- CO5.LO2 (L5 ★capstone) Write test cases and verify integration conformance for a multi-component application with a graphical interface and applied design patterns, given a requirements document, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Classes and objects encapsulation and modularity (M1.T1)<br>Object relationships association and composition (M1.T2) | CO1.LO1 | CO1 | Implement a small class hierarchy covering encapsulation and association in pairs. |  |
| 2 | Object relationships association and composition (M1.T2)<br>Inheritance hierarchies and abstract classes (M1.T3) | CO1.LO1, CO1.LO2 | CO1 | Code exercises on inheritance and abstract classes, reviewing previous concepts. | A:PA1 released |
| 3 | Polymorphism via interfaces and method resolution (M1.T4)<br>Generics and comparing and cloning objects (M2.T1) | CO1.LO2, CO2.LO1 | CO1, CO2 | Create polymorphic interfaces and generic classes; test with simple objects. | A:Quiz1 (quiz) |
| 4 | Generics and comparing and cloning objects (M2.T1)<br>The collections framework (M2.T2) | CO2.LO1 | CO2 | Practice generics and collections by implementing a typed list. | A:PA1 due |
| 5 | Exception handling and assertions (M2.T3)<br>Defensive programming and I o streams (M2.T4) | CO2.LO2 | CO2 | Write code with exception handling and defensive checks for a data‑processing task. | A:PA2 released |
| 6 | Defensive programming and I o streams (M2.T4)<br>Unit testing and debugging (M3.T1)<br>Version control as part of everyday development (M3.T2) | CO2.LO2, CO3.LO1 | CO2, CO3 | Develop unit tests and use version control for a small module. | A:Quiz2 (quiz); A:PA2 due |
| 7 | Version control as part of everyday development (M3.T2)<br>Common creational and structural design patterns (M3.T3) | CO3.LO1, CO3.LO2 | CO3 | Review design patterns; sketch solutions for creational and structural patterns. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Behavioural patterns applied to real problems (M3.T4)<br>Threads execution and thread pool management (M4.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Apply behavioural pattern to a sample problem and create a simple thread pool. | A:PA3 (assignment) |
| 9 | Threads execution and thread pool management (M4.T1)<br>Synchronization primitives and mutual exclusion (M4.T2) | CO4.LO1 | CO4 | Write threaded code using a thread pool; identify potential race conditions. | A:Quiz3 (quiz); A:ProjFinal released |
| 10 | Race conditions deadlocks and producer consumer (M4.T3)<br>Concurrency speedup and log evidence analysis (M4.T4) | CO4.LO2 | CO4 | Implement synchronized workers for a producer‑consumer scenario. |  |
| 11 | Concurrency speedup and log evidence analysis (M4.T4)<br>Use cases and UML class diagrams (M5.T1) | CO4.LO2, CO5.LO1 | CO4, CO5 | Design UML use‑case diagram and outline integration test plan. | A:Quiz4 (quiz); A:PA4 (assignment); A:ProjM1 released |
| 12 | UML sequence and use-case diagrams (M5.T2)<br>Event-driven programming and GUI architectures (M5.T3) | CO5.LO1 | CO5 | Create sequence diagrams and prototype a GUI component. | A:ProjM1 due |
| 13 | Event-driven programming and GUI architectures (M5.T3)<br>Integration conformance and project verification (M5.T4) | CO5.LO1, CO5.LO2 | CO5 | Write integration test cases and verify conformance for the full project. | A:ProjFinal due; A:Endsem (endsem) |

## 8. Weekly lab plan

No lab component (P = 0).

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3), A:Quiz2 (W6→W6), A:Quiz3 (W9→W9), A:Quiz4 (W11→W11) | best 3 of 4 | analyse-data |  |
| assignment | 20.0 | A:PA1 (W2→W4), A:PA2 (W5→W6), A:PA3 (W8→W8), A:PA4 (W11→W11) | — | implement, tool-use |  |
| project | 25.0 | A:ProjM1 (W11→W12), A:ProjFinal (W9→W13) | — | design, implement, evaluate-critique, teamwork, oral-presentation |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 18.33%, CO2 18.33%, CO3 16.67%, CO4 25.0%, CO5 25.0%

## 10. Resource material

Policy: **mixed** — The course covers foundational object-oriented design and standard language libraries using established textbooks, supplemented by design pattern references and concurrency guides for advanced topics.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Joshua Bloch (2008). *Effective Java*. | 9780132778046 | yes | M1.T1, M2.T1, M2.T2 |
| reference | Erich Gamma, John Vlissides, Richard Helm, Ralph Johnson (1995). *Design Patterns: Elements of Reusable Object-Oriented Software*. | 9780133052664 | yes | M3.T3, M3.T4 |
| reference | Brian Goetz, Joshua Bloch, Joseph Bowbeer, Doug Lea (2006). *Java Concurrency in Practice*. | 9780132702256 | yes | M4.T1, M4.T2, M4.T3 |
| reference | Martin Fowler (2004). *UML Distilled : AND Software Engineering*. | 9780582894440 | yes | M5.T1, M5.T2 |
| reference | Kent Beck (2002). *Test-driven development*. | 9780137585281 | yes | M3.T1 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|---|
| CO1 | 3 [unclaimed] | 1 [3] |  |  | 1 [unclaimed] |
| CO2 | 3 [unclaimed] | 1 [3] |  |  | 1 [unclaimed] |
| CO3 | 3 [unclaimed] | 2 [3] |  |  | 2 [unclaimed] |
| CO4 | 3 [unclaimed] | 1 [3] |  |  | 1 [unclaimed] |
| CO5 |  | 3 [3] | 3 [unclaimed] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: The outcome focuses directly on implementing object-oriented hierarchies and using static analyzers, which directly maps to system implementation using tools. (activities: implement, tool-use)
- CO2→PO4: Constructing software components aligns with building applications to meet specification needs using modern programming constructs. (activities: implement)
- CO3→PO4: Applying design patterns and testing frameworks corresponds to designing and evaluating computer applications. (activities: design, evaluate-critique)
- CO4→PO4: Developing multi-threaded programs with concurrency mechanisms directly exercises implementation and evaluation of complex software systems. (activities: implement)
- CO5→PO4: Evaluating a multi-component graphical application matches the evaluation aspect of building applications to meet acceptance criteria. (activities: evaluate-critique)
- CO5→PO7: Presenting deliverables at project milestones engages communication skills with an audience. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1, M1.T2 | 1, 2 | A:Quiz1@L3, A:PA1@L3, A:Midsem@L3 |
| CO1.LO2 | L3 | M1.T3, M1.T4 | 2, 3 | A:Quiz1@L3, A:PA1@L3, A:Midsem@L3 |
| CO2.LO1 | L3 | M2.T1, M2.T2 | 3, 4 | A:Quiz2@L3, A:PA2@L3, A:Midsem@L3 |
| CO2.LO2 | L3 | M2.T3, M2.T4 | 5, 6 | A:Quiz2@L3, A:PA2@L3, A:Midsem@L3 |
| CO3.LO1 | L3 | M3.T1, M3.T2 | 6, 7 | A:Quiz3@L3, A:PA3@L3, A:Endsem@L3 |
| CO3.LO2 | L3 | M3.T3, M3.T4 | 7, 8 | A:PA3@L3, A:Endsem@L3 |
| CO4.LO1 | L3 | M4.T1, M4.T2 | 8, 9 | A:Quiz3@L3, A:PA4@L3, A:Endsem@L3 |
| CO4.LO2 | L3 | M4.T3, M4.T4 | 10, 11 | A:Quiz4@L3, A:PA4@L3, A:Endsem@L3 |
| CO5.LO1 | L4 | M5.T1, M5.T2, M5.T3 | 11, 12, 13 | A:ProjM1@L4 |
| CO5.LO2 | L5 | M5.T4 | 13 | A:ProjFinal@L5 |

## Appendix C — Modules and topics

**M1 Object-Oriented Foundations and Inheritance** (primary CO1)
- M1.T1 Classes and objects encapsulation and modularity — 2.0 h · LOs CO1.LO1
- M1.T2 Object relationships association and composition — 2.0 h · LOs CO1.LO1 · requires M1.T1
- M1.T3 Inheritance hierarchies and abstract classes — 2.0 h · LOs CO1.LO2 · requires M1.T2
- M1.T4 Polymorphism via interfaces and method resolution — 2.0 h · LOs CO1.LO2 · requires M1.T3
**M2 Generics Collections and Robust Components** (primary CO2)
- M2.T1 Generics and comparing and cloning objects — 2.0 h · LOs CO2.LO1 · requires M1.T4
- M2.T2 The collections framework — 2.0 h · LOs CO2.LO1 · requires M2.T1
- M2.T3 Exception handling and assertions — 2.0 h · LOs CO2.LO2 · requires M2.T2
- M2.T4 Defensive programming and I o streams — 2.0 h · LOs CO2.LO2 · requires M2.T3
**M3 Testing Tooling and Design Patterns** (primary CO3)
- M3.T1 Unit testing and debugging — 1.5 h · LOs CO3.LO1 · requires M2.T4
- M3.T2 Version control as part of everyday development — 1.5 h · LOs CO3.LO1 · requires M3.T1
- M3.T3 Common creational and structural design patterns — 2.0 h · LOs CO3.LO2 · requires M3.T2
- M3.T4 Behavioural patterns applied to real problems — 2.0 h · LOs CO3.LO2 · requires M3.T3
**M4 Concurrency and Synchronization** (primary CO4)
- M4.T1 Threads execution and thread pool management — 2.0 h · LOs CO4.LO1 · requires M2.T4
- M4.T2 Synchronization primitives and mutual exclusion — 2.0 h · LOs CO4.LO1 · requires M4.T1
- M4.T3 Race conditions deadlocks and producer consumer — 2.0 h · LOs CO4.LO2 · requires M4.T2
- M4.T4 Concurrency speedup and log evidence analysis — 2.0 h · LOs CO4.LO2 · requires M4.T3
**M5 Object-Oriented Design Diagrams and Graphical Interfaces** (primary CO5)
- M5.T1 Use cases and UML class diagrams — 2.0 h · LOs CO5.LO1 · requires M3.T4
- M5.T2 UML sequence and use-case diagrams — 2.0 h · LOs CO5.LO1 · requires M5.T1
- M5.T3 Event-driven programming and GUI architectures — 2.0 h · LOs CO5.LO1 · requires M5.T2
- M5.T4 Integration conformance and project verification — 2.0 h · LOs CO5.LO2 · requires M5.T3, M4.T4

Schedule: feasible · 39.0 h needed / 39.0 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE101 | 0.095 | complementary | CSE101 provides basic procedural programming and a brief introductory touch to classes and objects, whereas this course deepens object-oriented design, architectural patterns, concurrency, testing, and team-based application building. |
| CSE584 | 0.053 | superficial | CSE584 focuses on formal program verification, dependent types, and mathematical proofs of correctness (Coq/F*), whereas this course focuses on practical software design patterns, object hierarchies, and multi-component application development. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **EXT:STANFORD/CS108** CS 108 Object-Oriented Systems Design — Stanford University, <https://explorecourses.stanford.edu/search?q=CS108>. Take: Incorporate software-engineering strategies for team programming, GUI libraries, and practical design patterns applied to Java libraries. Avoid: Avoid excessive focus on platform-specific proprietary GUI frameworks without emphasizing portable object-oriented design principles.
- **EXT:NUS/CS2113** CS2113 Software Engineering & Object-Oriented Programming — National University of Singapore, <https://nusmods.com/courses/CS2113>. Take: Adopt industry-standard tools such as test automation, build automation, version control revisioning, and systematic team project management. Avoid: Avoid shifting primary focus away from core object-oriented design towards general software engineering life-cycle management.
- **EXT:STANFORD/CS190** CS 190 Software Design Studio — Stanford University, <https://explorecourses.stanford.edu/search?q=CS190>. Take: Use studio-style code reviews, discussions on minimizing code complexity, and techniques for creating deep, modular classes. Avoid: Avoid relying solely on a studio format without structured milestones for the pair-programming application project.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| assessment | V23 | warning | CO1, BTECH-CSE/PO4 | CO1→BTECH-CSE/PO4: provisional 3 vs computed 1 (share 0.273) |
| assessment | V23 | warning | CO2, BTECH-CSE/PO4 | CO2→BTECH-CSE/PO4: provisional 3 vs computed 1 (share 0.273) |
| assessment | V23 | warning | CO4, BTECH-CSE/PO4 | CO4→BTECH-CSE/PO4: provisional 3 vs computed 1 (share 0.2) |
| assessment | VA-PROJ | warning | project | project released in week 9, late in a 13-week semester |
| cos | VB | warning | CO4 | CO CO4: claimed Bloom L3 but verb 'develop' is lexicon L6 |
| los | V10 | warning | CO4.LO2 | LO CO4.LO2: statement does not start with its declared verb 'develop' |
| los | V10 | warning | CO5.LO2 | LO CO5.LO2: statement does not start with its declared verb 'verify' |
| los | VB | warning | CO4.LO2 | LO CO4.LO2: claimed Bloom L3 but verb 'develop' is lexicon L6 |
| structure | VK-MALFORMED | warning | K10 | constraint K10 has a placeholder/empty target 'content.must_exclude[<phrase>]' (from G3); raw: a Java language features course |
| structure | VK-MALFORMED | warning | K11 | constraint K11 has a placeholder/empty target 'content.must_exclude[<phrase>]' (from G3); raw: a data-structures course (that is covered by the prerequisite) |
| structure | VK-MALFORMED | warning | K18 | constraint K18 has a placeholder/empty target 'content.must_include[<phrase>]' (from G3); raw: The course project must be done in pairs and should produce a working application with a graphical i |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 2 → 0 · round 1 accepted (2→1); round 2 accepted (1→0)
- assessment: errors 10 → 0 · round 1 accepted (10→2); round 2 accepted (2→1); round 3 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: semester_weeks: Semester weeks field was marked as not specified in the input, but regulations (UGREG-2025§2) specify 13 weeks of teaching.
- intake: weekly_effort_hours: Weekly student effort hours are omitted from the intake form.
- positioning: Lab credits and LTP structure: The CCO specifies L=3.0, T=1.0, P=0 with 4 credits, but the description and special constraints mandate a team project with a graphical interface and regular hands-on practice. Ensure that tutorial slots or informal lab support adequately accommodate practical execution.
- constraints: Lab hours mismatch: CCO specifies L:3.0, T:1.0, P:0 (lab required: no), but negative constraint NC3 and infrastructure list imply hands-on practice.
- copo: Oral presentation activity mapping: CO5 maps to oral-presentation for PO7, but oral-presentation is mapped to PO7 in activity_po_map only via written-communication? Wait, activity_po_map has oral-presentation mapped to BTECH-CSE/PO7, which is correct.
- labs: K05 vs K12: Constraints K05 (lab.hours_per_week == 0) and K12 (lab.present == true) are contradictory.
- labs: V18: Hands‑on LOs exist but no lab sessions; practice is placed in tutorials, which may need verification.

## Appendix F — Rationales (G11)

- **sequencing rationale:** Modules progress from foundational object‑oriented concepts (M1) to generic collections (M2), then to design patterns and testing (M3), followed by concurrency (M4), and finally graphical design and integration (M5), reflecting prerequisite dependencies among topics and ensuring prerequisite knowledge is applied before more complex constructs.
- **assessment rationale:** The mix of quizzes, assignments, a project, and mid‑ and end‑semester exams aligns with the cognitive levels of the COs: lower‑order recall and understanding are assessed by quizzes, while higher‑order design, implementation, and evaluation are measured through assignments and the pair‑programming project, satisfying both individual and collaborative learning outcomes.
- **positioning rationale:** Unlike CSE101, which introduces basic procedural programming, this course deepens object‑oriented design, patterns, concurrency, and GUI development. It also differs from CSE584, which emphasizes formal verification, by focusing on practical software engineering and component reuse.