# Advanced Programming — Course Proposal (ProfsAgent draft)

> Run `cse201-dev-02` · generated deterministically from the design graph · validator status: **0 errors, 5 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM02 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 2xx) |
| Course Name | Advanced Programming `[USER]` |
| Credits | 4 |
| L-T-P | 3.0-1.0-0 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-CSE · years [2] |

## 3. Course description

Advanced Programming is a second-tier course designed for second-year Bachelor of Technology students in Computer Science and Engineering. The course transitions students from writing small, single-file programs to developing robust, multi-component applications with clear interfaces. Students learn to implement object-oriented hierarchies and reusable generic components, construct robust multi-component programs using defensive programming and input/output streams, analyze concurrent multi-threaded execution traces, and design object-oriented software architectures with corresponding unit test suites. The instructional methodology comprises lectures and tutorials. By the conclusion of the course, students are able to design, build, and test applications such that their constituent parts can be developed independently and reused.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|
| mandatory | CSE101 `[CATALOGUE]` | classes, objects, inheritance, Exception handling, assertions | Students must know basic procedural constructs, functions, and elementary object concepts before moving to multi-component software design. |
| mandatory | CSE102 `[CATALOGUE]` | basic data structures, arrays, linked lists | Students must be comfortable with basic data structures and algorithmic problem solving before building larger applications using collections and generics. |

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — CSE600 is an upper-level/graduate object-oriented course with an anti-requisite link to CSE101/CSE201, whereas this course is designed as a core 200-level undergraduate programming continuation covering component design, testing, tooling, and concurrency.

## 5. Bloom band

L2–L5 · basis: level 2xx band [2,5] — provisional table (docs/01 §6.4); to be refit from quality-filtered corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (L3, procedural) — Implement object-oriented hierarchies and reusable generic components, using an object-oriented programming language and standard collections libraries, such that at least 80% of the provided test cases pass.** `[CORPUS, USER]`  
verb *implement* · behaviour *object-oriented hierarchies and reusable generic components* · condition *using an object-oriented programming language and standard collections libraries* · degree *such that at least 80% of the provided test cases pass* · evidence: programming_assignment, exam_question · marks share (computed): 28.33%

- CO1.LO1 (L3) Implement class hierarchies with inheritance and polymorphism, using an object-oriented programming language, such that at least 80% of the provided test cases pass.
- CO1.LO2 (L3 ★capstone) Implement reusable generic components and standard collections libraries, using an object-oriented programming language, such that at least 80% of the provided test cases pass.

**CO2 (L3, procedural) — Construct robust multi-component programs, using defensive programming techniques, exception handling mechanisms, and input/output streams, meeting the stated interface specification for every public method.** `[CORPUS, USER]`  
verb *construct* · behaviour *robust multi-component programs* · condition *using defensive programming techniques, exception handling mechanisms, and input/output streams* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment, code_review · marks share (computed): 26.25%

- CO2.LO1 (L3) Construct exception handling mechanisms and defensive programming checks, using exception handling features, meeting the stated interface specification for every public method.
- CO2.LO2 (L3 ★capstone) Construct robust multi-component programs with input/output streams and serialization, using defensive programming techniques, meeting the stated interface specification for every public method.

**CO3 (L4, conceptual) — Analyze concurrent multi-threaded execution traces, using synchronization primitives and thread pools, identifying at least two distinct race conditions or deadlocks with supporting log evidence.** `[CORPUS, USER]`  
verb *analyze* · behaviour *concurrent multi-threaded execution traces* · condition *using synchronization primitives and thread pools* · degree *identifying at least two distinct race conditions or deadlocks with supporting log evidence* · evidence: exam_question, programming_assignment · marks share (computed): 15.83%

- CO3.LO1 (L4) Examine concurrent threads and synchronization primitives, using thread execution traces, identifying at least two distinct race conditions or deadlocks with supporting log evidence.
- CO3.LO2 (L4 ★capstone) Analyze concurrent multi-threaded execution traces, using synchronization primitives and thread pools, identifying at least two distinct race conditions or deadlocks with supporting log evidence.

**CO4 (L5, metacognitive) — Design an object-oriented software architecture and unit test suite, for a given multi-component requirements document, justifying each design choice against stated requirements.** `[CORPUS, USER]`  
verb *design* · behaviour *an object-oriented software architecture and unit test suite* · condition *for a given multi-component requirements document* · degree *justifying each design choice against stated requirements* · evidence: design_document, project_deliverable · marks share (computed): 32.92%

- CO4.LO1 (L2) Illustrate object-oriented software architecture and unit test suites, for a given multi-component requirements document, justifying each design choice against stated requirements.
- CO4.LO2 (L5 ★capstone) Design an object-oriented software architecture and unit test suite, for a given multi-component requirements document, justifying each design choice against stated requirements.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Classes and Objects Fundamentals (M1.T1)<br>Inheritance and Polymorphism (M1.T2) | CO1.LO1 | CO1 | Worked trace-diagnosis of 3 class hierarchy and polymorphism code snippets, in pairs |  |
| 2 | Inheritance and Polymorphism (M1.T2)<br>Generic Classes and Methods (M2.T1) | CO1.LO1, CO1.LO2 | CO1 | Problem-solving on implementing generic methods and collection wrappers for custom types |  |
| 3 | Generic Classes and Methods (M2.T1)<br>Standard Collections Framework (M2.T2) | CO1.LO2 | CO1 | Practical exercises on sorting and searching using the Standard Collections Framework | A:Quiz1 (quiz); A:PA1 released |
| 4 | Exception Handling Mechanisms (M3.T1)<br>Defensive Programming and Assertions (M3.T2) | CO2.LO1 | CO2 | Writing defensive assertions and custom exception propagation logic for a given buggy module | A:PA1 due |
| 5 | Defensive Programming and Assertions (M3.T2)<br>Stream Architectures and Byte/Character I/O (M4.T1) | CO2.LO1, CO2.LO2 | CO2 | Peer review of defensive programming checks and input stream reader implementations |  |
| 6 | Stream Architectures and Byte/Character I/O (M4.T1)<br>Object Serialization and Robust Persistence (M4.T2) | CO2.LO2 | CO2 | Debugging object serialization routines and handling persistent state corruption issues | A:Quiz2 (quiz); A:PA2 released |
| 7 | Threads and Mutual Exclusion (M5.T1)<br>Synchronization Primitives and Deadlocks (M5.T2) | CO3.LO1 | CO3 | Analysis of thread execution logs to identify race conditions and mutual exclusion failures | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Synchronization Primitives and Deadlocks (M5.T2)<br>Thread Pools and Trace Analysis (M5.T3) | CO3.LO1, CO3.LO2 | CO3 | Tracing deadlock scenarios and evaluating thread pool configuration parameters | A:PA2 due |
| 9 | Thread Pools and Trace Analysis (M5.T3) | CO3.LO2 | CO3 | Trace analysis and debugging exercise on multi-threaded producer-consumer implementations | A:Quiz3 (quiz) |
| 10 | UML Modelling and Unit Testing Suites (M6.T1) | CO4.LO1 | CO4 | Designing UML class diagrams and writing unit test suites for a case study specification |  |
| 11 | UML Modelling and Unit Testing Suites (M6.T1)<br>Object-Oriented Design Patterns (M6.T2) | CO4.LO1, CO4.LO2 | CO4 | Evaluating design pattern applicability and refactoring monolithic classes | A:Quiz4 (quiz); A:ProjectMilestone1 (project) |
| 12 | Object-Oriented Design Patterns (M6.T2) | CO4.LO2 | CO4 | Design review and architectural critique of student project design patterns | A:ProjectMilestone2 released |
| 13 |  |  |  |  | A:ProjectMilestone2 due; A:Endsem (endsem) |

## 8. Weekly lab plan

No lab component (P = 0).

Infrastructure: Java JDK (available); an IDE (Eclipse/IntelliJ) (available); JUnit (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3), A:Quiz2 (W6→W6), A:Quiz3 (W9→W9), A:Quiz4 (W11→W11) | best 3 of 4 | analyse-data |  |
| assignment | 20.0 | A:PA1 (W3→W4), A:PA2 (W6→W8) | — | implement, tool-use |  |
| project | 25.0 | A:ProjectMilestone1 (W11→W11), A:ProjectMilestone2 (W12→W13) | — | design, implement, evaluate-critique, teamwork, written-communication |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | analyse-data |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | analyse-data, design |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 28.33%, CO2 26.25%, CO3 15.83%, CO4 32.92%

## 10. Resource material

Policy: **mixed** — The course covers standard object-oriented programming concepts alongside specialized topics like concurrency and design patterns, making a mix of standard textbooks and targeted chapters appropriate.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | David J. Barnes, Michael Kolling, David Barnes, Kolling Barnes (2002). *Objects first with Java*. | 9780136060864 | yes | M1.T1, M1.T2, M3.T1 |
| reference | Danny Poo, Derek Kiong, Swarnalatha Ashok (2008). *Generics and Collections Framework*. | 10.1007/978-1-84628-963-7_12 | yes | M2.T1, M2.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|---|
| CO1 | 3 [2] | 2 [3] |  |  | 2 [unclaimed] |
| CO2 | 3 [unclaimed] | 3 [3] |  |  | 2 [unclaimed] |
| CO3 | 3 [2] | 3 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 2 [2] |
| CO4 | 3 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: Directly involves implementing object-oriented software components using standard language features and libraries, aligning with system implementation. (activities: implement, tool-use)
- CO1→PO3: Uses standard collections libraries and generic components to adapt techniques for software development. (activities: implement)
- CO2→PO4: Focuses on constructing robust multi-component programs meeting interface specifications through standard methodologies. (activities: implement, evaluate-critique)
- CO3→PO3: Applies synchronization primitives and thread pools to analyze concurrency and execution traces. (activities: analyse-data)
- CO3→PO9: Involves advanced multithreading analysis and identifying complex synchronization anomalies. (activities: analyse-data, tool-use)
- CO4→PO4: Directly covers designing object-oriented software architecture and evaluation through unit test suites against requirements. (activities: design, evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1, M1.T2 | 1, 2 | A:Quiz1@L3, A:PA1@L3, A:Midsem@L3 |
| CO1.LO2 | L3 | M2.T1, M2.T2 | 2, 3 | A:Quiz2@L3, A:PA1@L3, A:Midsem@L3 |
| CO2.LO1 | L3 | M3.T1, M3.T2 | 4, 5 | A:Quiz2@L3, A:PA2@L3, A:Midsem@L3 |
| CO2.LO2 | L3 | M4.T1, M4.T2 | 5, 6 | A:Quiz3@L3, A:PA2@L3, A:Endsem@L3 |
| CO3.LO1 | L4 | M5.T1, M5.T2 | 7, 8 | A:Quiz3@L4 |
| CO3.LO2 | L4 | M5.T3 | 8, 9 | A:Quiz4@L4, A:ProjectMilestone1@L4, A:Endsem@L4 |
| CO4.LO1 | L2 | M6.T1 | 10, 11 | A:Quiz4@L2, A:ProjectMilestone1@L2, A:Endsem@L2 |
| CO4.LO2 | L5 | M6.T2 | 11, 12 | A:ProjectMilestone2@L5, A:Endsem@L5 |

## Appendix C — Modules and topics

**M1 Object-Oriented Hierarchies and Polymorphism** (primary CO1)
- M1.T1 Classes and Objects Fundamentals — 1.5 h · LOs CO1.LO1
- M1.T2 Inheritance and Polymorphism — 2.5 h · LOs CO1.LO1 · requires M1.T1
**M2 Generics and Standard Collections** (primary CO1)
- M2.T1 Generic Classes and Methods — 2.5 h · LOs CO1.LO2 · requires M1.T2
- M2.T2 Standard Collections Framework — 2.5 h · LOs CO1.LO2 · requires M2.T1
**M3 Exception Handling and Defensive Programming** (primary CO2)
- M3.T1 Exception Handling Mechanisms — 2.0 h · LOs CO2.LO1 · requires M1.T2
- M3.T2 Defensive Programming and Assertions — 2.0 h · LOs CO2.LO1 · requires M3.T1
**M4 Input/Output Streams and Serialization** (primary CO2)
- M4.T1 Stream Architectures and Byte/Character I/O — 2.5 h · LOs CO2.LO2 · requires M3.T2
- M4.T2 Object Serialization and Robust Persistence — 2.5 h · LOs CO2.LO2 · requires M4.T1
**M5 Concurrency and Synchronization** (primary CO3)
- M5.T1 Threads and Mutual Exclusion — 2.0 h · LOs CO3.LO1 · requires M1.T1
- M5.T2 Synchronization Primitives and Deadlocks — 2.0 h · LOs CO3.LO1 · requires M5.T1
- M5.T3 Thread Pools and Trace Analysis — 5.0 h · LOs CO3.LO2 · requires M5.T2
**M6 Software Architecture, Design Patterns, and Testing** (primary CO4)
- M6.T1 UML Modelling and Unit Testing Suites — 4.0 h · LOs CO4.LO1 · requires M1.T2, M3.T2
- M6.T2 Object-Oriented Design Patterns — 4.0 h · LOs CO4.LO2 · requires M6.T1

Schedule: feasible · 35.0 h needed / 39.0 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|
| CSE101 | 0.095 | complementary | CSE101 introduces basic syntax, procedural elements, and simple object usage in Python. This course builds on that foundation by requiring students to design multi-component applications, implement design patterns, handle concurrency, and perform rigorous unit testing in Java. |
| CSE584 | 0.053 | superficial | CSE584 focuses on formal program verification and dependent types using Coq/F*. This course focuses on practical object-oriented application design, software architecture, and concurrency. |

Overlap method: stub: Jaccard over embedding-matched topic phrases (cos ≥ 0.87), no IDF

**Comparable courses**

- **CSE583** Software Development using Open Source — IIIT-D catalogue. Take: Integration of version control, testing tools, and collaborative team-based workflows. Avoid: Focusing heavily on open-source ecosystem licensing and service-oriented microservices instead of core object-oriented programming design.
- **EXT:NUS/CS2113** CS2113 Software Engineering & Object-Oriented Programming — National University of Singapore, <https://nusmods.com/courses/CS2113>. Take: Systematic software development processes, test automation, and building maintainable object-oriented applications. Avoid: Overemphasizing formal project management methodologies suited for senior-year software engineering courses.
- **EXT:STANFORD/CS190** CS 190 Software Design Studio — Stanford University, <https://explorecourses.stanford.edu/search?q=CS190>. Take: Emphasis on managing code complexity, structuring deep classes, and conducting code reviews. Avoid: Studio-only delivery format without adequate lecture and tutorial support for second-year foundational concepts.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

| Stage | Code | Severity | Nodes | Message |
|---|---|---|---|---|
| los | VLO-COUNT | warning |  | 8 LOs in total (expected 10–20) |
| schedule | V6 | warning | W13 | weeks with no lecture topics: [13] |
| structure | VT-SIZE | warning | M5.T3 | topic M5.T3 is 5.0 h (> 3 h; split it) |
| structure | VT-SIZE | warning | M6.T1 | topic M6.T1 is 4.0 h (> 3 h; split it) |
| structure | VT-SIZE | warning | M6.T2 | topic M6.T2 is 4.0 h (> 3 h; split it) |

**Repair history**

- assessment: errors 11 → 0 · round 1 accepted (11→2); round 2 accepted (2→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: level_or_code: The course code is not yet assigned (currently 2xx level).
- intake: lab: The professor specifies 'no separate lab slot' but requires a pair-programming project producing a working application with a GUI, which might require significant practical support.
- positioning: programme_structure: Programme core/elective structure is not available in the KG stub, making exact cohort placement reliant on year level tags.
- constraints: assessment weight distribution: Professor's rationale mentions a substantial share of grade from programming work, but no numeric weight is specified.
- copo: CO5/PO5 mapping gap: Although po_gap_hints mentions modern tool usage, teamwork (PO5) is not explicitly evidenced by the provided CO evidence types (programming_assignment, exam_question, code_review, design_document, project_deliverable without explicit group criteria).
- los: lecture hours total: Sum of LO lecture hours is 34.0 against a budget of 39.0 hours. Additional hours can be distributed across topics during scheduling.
- labs: V18: P=0 and lab is not required, but hands-on LOs exist. Hands-on practice has been integrated into tutorial sessions as per rule 7.
- resources: Candidate Resources: Corpus resources provided are primarily for Python (CSE101) and Algorithms (CSE102), and retrieved external records contain irrelevant books (e.g., Jane Austen novels), necessitating additional targeted search requests for advanced Java topics like concurrency and design patterns.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress from foundational object-oriented principles and generics to exception handling, I/O streams, concurrency, and architecture design, relying directly on the prerequisite competencies established in CSE101 and CSE102.
- **assessment rationale:** The assessment mix of quizzes, assignments, a project, a mid-semester examination, and an end-semester examination aligns with the course outcomes by balancing practical programming and application design through project work with individual evaluation via exams and quizzes.
- **positioning rationale:** This course differs from CSE101 by focusing on multi-component application design and concurrency rather than basic syntax, and differs from CSE584 by emphasizing practical object-oriented design instead of formal program verification.