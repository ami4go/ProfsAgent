# Advanced Programming — Course Proposal (ProfsAgent draft)

> Run `cse201-dev-06` · generated deterministically from the design graph · validator status: **2 errors, 7 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

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

Advanced Programming is a second programming course that moves students from writing small single-file programs to building larger applications made of several components with clear interfaces. The course covers object-oriented design, inheritance hierarchies, generic programming, robust error handling, I/O serialization, design patterns, event-driven programming with graphical user interfaces, and multi-threading with synchronization primitives. Students learn how to write code that others can reuse and test, how to structure programs around established design patterns, and how to handle errors, input/output, and concurrency. By the end of the course, students working in pairs are able to take a reasonably well-specified application design and deliver a working, tested, multi-component program. The course is taught through lectures, tutorials, programming assignments, quizzes, examinations, and a collaborative team project.

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

**CO1 (L3, procedural) — Implement object-oriented classes, inheritance hierarchies, and interfaces, using Java collections and generics, such that all public test cases pass and static analysis warnings are resolved.** `[CORPUS, USER]`  
verb *implement* · behaviour *object-oriented classes, inheritance hierarchies, and interfaces, using Java collections and generics* · condition *using Java collections and generics* · degree *such that all public test cases pass and static analysis warnings are resolved* · evidence: programming_assignment, exam_question · marks share (computed): 31.67%

- CO1.LO1 (L3) Implement class encapsulation, association, and composition relationships, using basic object principles, such that all public test cases pass.
- CO1.LO2 (L3) Implement inheritance hierarchies, abstract classes, and interface-based polymorphism, using object-oriented principles, such that all public test cases pass.
- CO1.LO3 (L3 ★capstone) Implement generic classes and methods using the collections framework, given a data processing requirement, such that all public test cases pass and static analysis warnings are resolved.

**CO2 (L3, procedural) — Apply exception handling, assertions, and I/O serialization to develop robust programs, given a specification with error cases, meeting the stated interface specification for every public method.** `[USER]`  
verb *apply* · behaviour *exception handling, assertions, and I/O serialization to develop robust programs* · condition *given a specification with error cases* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment, lab_task · marks share (computed): 17.67%

- CO2.LO1 (L3) Apply exception handling and assertions to validate input conditions, given a specification with error cases, such that at least 80% of the provided test cases pass.
- CO2.LO2 (L3 ★capstone) Apply I/O streams and object serialization to persist object state, given a specification with error cases, meeting the stated interface specification for every public method.

**CO3 (L4, conceptual) — Deconstruct software requirements into UML class, sequence, and use-case diagrams, using object-oriented design principles, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *deconstruct* · behaviour *software requirements into UML class, sequence, and use-case diagrams* · condition *using object-oriented design principles* · degree *covering every use case in the supplied requirements document* · evidence: design_document, exam_question · marks share (computed): 19.0%

- CO3.LO1 (L4) Identify use cases and actor interactions, using object-oriented design principles, covering every use case in the supplied requirements document.
- CO3.LO2 (L4 ★capstone) Deconstruct software requirements into UML class and sequence diagrams, given a narrative system specification, covering every use case in the supplied requirements document.

**CO4 (L3, procedural) — Construct multi-threaded applications using synchronization primitives and thread pools, given a concurrent task specification, such that at least 80% of the provided test cases pass without race conditions.** `[CORPUS, USER]`  
verb *construct* · behaviour *multi-threaded applications using synchronization primitives and thread pools* · condition *given a concurrent task specification* · degree *such that at least 80% of the provided test cases pass without race conditions* · evidence: programming_assignment, lab_task · marks share (computed): 20.0%

- CO4.LO1 (L3) Implement threads and mutual exclusion locks, given a concurrent task specification, such that at least 80% of the provided test cases pass without race conditions.
- CO4.LO2 (L3 ★capstone) Construct multi-threaded applications using thread pools and synchronization barriers, given a producer-consumer task specification, such that at least 80% of the provided test cases pass without race conditions.

**CO5 (L5, metacognitive) — Evaluate a working multi-component application with a graphical user interface developed in pairs, using version control and unit testing, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *a working multi-component application with a graphical user interface in pairs, using version control and unit testing* · condition *working in pairs using version control and unit testing tools* · degree *such that the delivered system satisfies every acceptance criterion agreed at the first milestone* · evidence: project_deliverable, presentation, code_review · marks share (computed): 15.0%

- CO5.LO1 (L3) Execute unit testing and version control workflows for a multi-component application developed in pairs, working in pairs using version control and unit testing tools, justifying each design decision against at least one stated requirement.
- CO5.LO2 (L5 ★capstone) Evaluate a graphical user interface application developed in pairs, working in pairs using version control and unit testing tools, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Regular hands-on practice: Classes, objects, encapsulation and object relationships (M1.T1) | CO1.LO1 | CO1 | Guided problem-solving on designing classes, encapsulation, and object relationships with code tracing. |  |
| 2 | Inheritance hierarchies, abstract classes and polymorphism (M1.T2) | CO1.LO2 | CO1 | Worked trace-diagnosis of inheritance hierarchies, abstract classes, and polymorphism problems. | A:PA1 released |
| 3 | Generics, comparing and cloning objects, and the collections framework (M1.T3) | CO1.LO3 | CO1 | Problem-solving session on writing generic classes and applying collections framework collections. | A:Quiz1 (quiz) |
| 4 | Exception handling, assertions and defensive programming (M2.T1) | CO2.LO1 | CO2 | Designing exception handling strategies and assertions for faulty specifications. | A:PA1 due |
| 5 | I/O streams and object serialization (M2.T2) | CO2.LO2 | CO2 | Problem-solving on I/O stream reading/writing and object serialization state preservation. | A:Quiz2 (quiz); A:PA2 released |
| 6 | Unit testing, debugging and version control workflows (M2.T3) | CO5.LO1 | CO5 | Writing unit tests and debugging exercises combined with Git version control commands. | A:PA2 due; A:ProjM1 released |
| 7 | Use cases and actor interactions (M3.T1)<br>UML class and sequence diagrams (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Analyzing use cases and actor interactions from a narrative requirements document. | A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | UML class and sequence diagrams (M3.T2)<br>Threads, mutual exclusion and race conditions (M4.T1) | CO3.LO2, CO4.LO1 | CO3, CO4 | Drawing and reviewing UML class and sequence diagrams for a given software specification. | A:ProjM2 released |
| 9 | Threads, mutual exclusion and race conditions (M4.T1)<br>Thread pools and producer-consumer synchronization patterns (M4.T2) | CO4.LO1, CO4.LO2 | CO4 | Tracing mutual exclusion locks and identifying race conditions in multi-threaded code snippets. | A:Quiz3 (quiz); A:ProjFinal released |
| 10 | Thread pools and producer-consumer synchronization patterns (M4.T2)<br>Event-driven programming and graphical user interfaces (M5.T1) | CO4.LO2, CO5.LO2 | CO4, CO5 | Designing thread pools and producer-consumer synchronization pattern workflows. | A:PA3 released |
| 11 | Event-driven programming and graphical user interfaces (M5.T1)<br>Design patterns applied to real problems (M5.T2) | CO3.LO2, CO5.LO2 | CO3, CO5 | Evaluating GUI event-driven architectures and design patterns against stated requirements. | A:PA3 due; A:ProjM1 due; A:ProjM2 due |
| 12 | Design patterns applied to real problems (M5.T2)<br>Pair programming and collaborative version control workflows (M5.T3) | CO3.LO2, CO5.LO1, CO5.LO2 | CO3, CO5 | Critiquing design pattern applications and planning pair programming workflows. | A:Quiz4 (quiz) |
| 13 | Pair programming and collaborative version control workflows (M5.T3) | CO5.LO1 | CO5 | Collaborative version control and peer code review practice for multi-component projects. | A:ProjFinal due; A:Endsem (endsem) |

## 8. Weekly lab plan

No lab component (P = 0).

Infrastructure: Students' own laptops (available); Java JDK, IDE (Eclipse/IntelliJ), JUnit, Git/GitHub (available)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W3→W3), A:Quiz2 (W5→W5), A:Quiz3 (W9→W9), A:Quiz4 (W12→W12) | best 3 of 4 | analyse-data |  |
| programming_assignment | 25.0 | A:PA1 (W2→W4), A:PA2 (W5→W6), A:PA3 (W10→W11) | — | implement, tool-use |  |
| project | 25.0 | A:ProjM1 (W6→W11), A:ProjM2 (W8→W11), A:ProjFinal (W9→W13) | — | design, implement, teamwork, written-communication, evaluate-critique |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | design, implement, analyse-data |  |
| endsem | 20.0 | A:Endsem (W13→W13) | — | design, implement, analyse-data |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 31.67%, CO2 17.67%, CO3 19.0%, CO4 20.0%, CO5 15.0%

## 10. Resource material

Policy: **mixed** — Advanced programming requires a combination of foundational language-specific best practices, software design patterns, concurrency principles, and object-oriented analysis and design methods which are best covered across standard reference textbooks rather than a single volume.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Joshua Bloch (2008). *Effective Java*. | 9780132778046 | yes | M1.T3, M2.T1 |
| reference | Eric Freeman, Elisabeth Freeman, Kathy Sierra, Bert Bates (2004). *Head First design patterns*. | 9789867794529 | yes | M5.T2 |
| reference | Brian Goetz, Joshua Bloch, Joseph Bowbeer, Doug Lea (2006). *Java Concurrency in Practice*. | 9780132702256 | yes | M4.T1, M4.T2 |
| reference | Craig Larman (1998). *Applying UML and patterns*. | 9780131969452 | yes | M3.T1, M3.T2 |
| reading | Robert C. Martin (2008). *Clean Code: A Handbook of Agile Software Craftsmanship*. | 9780136083221 | yes | M2.T3, M5.T3 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|---|
| CO1 | 3 [unclaimed] | 3 [3] |  |  | 2 [2] |
| CO2 | 3 [2] | 3 [3] |  |  | 1 [unclaimed] |
| CO3 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [2] | 2 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [3] | 1 [unclaimed] | 1 [unclaimed] | 2 [2] |
| CO5 | 1 [unclaimed] | 3 [3] | 3 [3] | 3 [2] | 3 [unclaimed] |

PO legend: PO3 = Adapt techniques to new problems; PO4 = Design/implement/evaluate systems; PO5 = Teamwork; PO7 = Communication; PO9 = Advanced techniques and tools

- CO1→PO4: The CO requires students to design and implement OO software using modern Java tools, directly exercising PO4. (activities: implement)
- CO1→PO9: Use of Java collections, generics and static analysis tools reflects advanced programming techniques linked to PO9. (activities: tool-use)
- CO2→PO4: Robust program development via exception handling and I/O requires implementation skills covered by PO4. (activities: implement)
- CO2→PO3: Choosing appropriate error‑handling techniques adapts known models to new problem specifications. (activities: implement)
- CO3→PO4: Creating UML artefacts is a core design activity aligning with PO4. (activities: design)
- CO3→PO7: UML diagrams communicate system design to stakeholders, fulfilling PO7. (activities: written-communication)
- CO4→PO4: Building concurrent applications is a primary implementation task covered by PO4. (activities: implement)
- CO4→PO9: Use of threads, synchronization, and thread pools employs advanced concurrency techniques linked to PO9. (activities: tool-use)
- CO5→PO5: The CO explicitly requires pair work with version control, directly exercising teamwork (PO5). (activities: teamwork)
- CO5→PO4: Evaluation of a complete system using modern tools aligns with PO4. (activities: evaluate-critique)
- CO5→PO7: Presentation of the project and code review require effective communication. (activities: oral-presentation)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1 | 1 | A:Quiz1@L3, A:PA1@L3, A:Midsem@L3 |
| CO1.LO2 | L3 | M1.T2 | 2 | A:Quiz1@L3, A:PA1@L3, A:Midsem@L3 |
| CO1.LO3 | L3 | M1.T3 | 3 | A:Quiz2@L3, A:PA2@L3, A:Midsem@L3, A:Endsem@L3 |
| CO2.LO1 | L3 | M2.T1 | 4 | A:Quiz2@L3, A:PA2@L3, A:Midsem@L3 |
| CO2.LO2 | L3 | M2.T2 | 5 | A:PA2@L3, A:Midsem@L3, A:Endsem@L3 |
| CO3.LO1 | L4 | M3.T1 | 7 | A:Quiz3@L4, A:ProjM1@L4, A:Endsem@L4 |
| CO3.LO2 | L4 | M3.T2, M5.T2 | 7, 8, 11, 12 | A:ProjM1@L4, A:Endsem@L4 |
| CO4.LO1 | L3 | M4.T1 | 8, 9 | A:Quiz3@L3, A:PA3@L3, A:ProjM2@L3 |
| CO4.LO2 | L3 | M4.T2 | 9, 10 | A:Quiz4@L3, A:PA3@L3, A:Endsem@L3 |
| CO5.LO1 | L3 | M2.T3, M5.T3 | 6, 12, 13 | A:ProjM2@L3, A:ProjFinal@L3 |
| CO5.LO2 | L5 | M5.T1, M5.T2 | 10, 11, 12 | A:Quiz4@L5, A:ProjFinal@L5 |

## Appendix C — Modules and topics

**M1 Object-Oriented Foundations and Inheritance** (primary CO1, CO3)
- M1.T1 Regular hands-on practice: Classes, objects, encapsulation and object relationships — 3.0 h · LOs CO1.LO1
- M1.T2 Inheritance hierarchies, abstract classes and polymorphism — 3.0 h · LOs CO1.LO2 · requires M1.T1
- M1.T3 Generics, comparing and cloning objects, and the collections framework — 3.0 h · LOs CO1.LO3 · requires M1.T2
**M2 Robust Programming, I/O and Tooling** (primary CO2, CO5)
- M2.T1 Exception handling, assertions and defensive programming — 3.0 h · LOs CO2.LO1 · requires M1.T1
- M2.T2 I/O streams and object serialization — 3.0 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Unit testing, debugging and version control workflows — 3.0 h · LOs CO5.LO1 · requires M1.T3
**M3 Object-Oriented Analysis and Design** (primary CO3)
- M3.T1 Use cases and actor interactions — 2.5 h · LOs CO3.LO1
- M3.T2 UML class and sequence diagrams — 3.0 h · LOs CO3.LO2 · requires M3.T1, M1.T2
**M4 Concurrency and Synchronization** (primary CO4)
- M4.T1 Threads, mutual exclusion and race conditions — 3.0 h · LOs CO4.LO1 · requires M1.T3
- M4.T2 Thread pools and producer-consumer synchronization patterns — 3.0 h · LOs CO4.LO2 · requires M4.T1
**M5 Event-Driven Programming, GUIs and Project Integration** (primary CO5)
- M5.T1 Event-driven programming and graphical user interfaces — 3.0 h · LOs CO5.LO2 · requires M1.T2, M2.T2
- M5.T2 Design patterns applied to real problems — 2.5 h · LOs CO3.LO2, CO5.LO2 · requires M3.T2
- M5.T3 Pair programming and collaborative version control workflows — 2.0 h · LOs CO5.LO1 · requires M2.T3

Schedule: feasible · 37.0 h needed / 39.0 h available

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
| los | VLO-COPY | error | CO4.LO2, CO4 | CO4.LO2 restates its parent CO4 (token overlap 0.82); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO5.LO2, CO5 | CO5.LO2 restates its parent CO5 (token overlap 0.87); an LO must be a narrower, single-task step |
| assessment | VA-LOAD | warning | W11 | 3 assessment events due in week 11 (cap 2) |
| copo | VCOPO-ACT | warning | CO2, BTECH-CSE/PO3 | CO2→BTECH-CSE/PO3: none of its evidencing activities maps to that PO, so its strength can never be computed |
| cos | V11 | warning | CO5 | CO CO5 condition is not visible in the statement text |
| los | V11 | warning | CO3.LO2 | LO CO3.LO2 condition is not visible in the statement text |
| los | V11 | warning | CO4.LO2 | LO CO4.LO2 condition is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 30.0 h vs budget 39.0 h (±15%) |
| los | VB | warning | CO3.LO1 | LO CO3.LO1: claimed Bloom L4 but verb 'identify' is lexicon L1 |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 3 → 2 · round 1 accepted (3→2); round 2 rejected (2→2); round 3 rejected (2→2)
- structure: errors 3 → 0 · round 1 rejected (3→2); round 2 accepted (3→1); round 3 accepted (1→0)
- assessment: errors 6 → 0 · round 1 accepted (6→1); round 2 rejected (1→1); round 3 accepted (1→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: semester_weeks: Semester weeks field was marked as not specified in the input, but regulations (UGREG-2025§2) specify 13 weeks of teaching.
- intake: weekly_effort_hours: Weekly student effort hours are omitted from the intake form.
- positioning: Lab credits and LTP structure: The CCO specifies L=3.0, T=1.0, P=0 with 4 credits, but the description and special constraints mandate a team project with a graphical interface and regular hands-on practice. Ensure that tutorial slots or informal lab support adequately accommodate practical execution.
- los: hours_budget: The sum of estimated lecture hours (29.5) and tutorial hours (11.0) is slightly below the target budget (39.0 lecture and 13.0 tutorial hours) because exact topic granularity distributes across 11 LOs. This will be balanced during weekly scheduling.
- labs: V18: P=0 and no lab is required, but hands-on LOs exist. Hands-on practice has been routed into tutorial problem-solving sessions and assignments.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules follow a logical progression from foundational object-oriented concepts to advanced architectural topics. Module 1 establishes object-oriented foundations and inheritance, building upon the prerequisites CSE101 and CSE102. Module 2 introduces robust programming and tooling, followed by Module 3 on object-oriented analysis and design. Module 4 covers concurrency and synchronization, and Module 5 integrates these concepts through event-driven programming, graphical user interfaces, and project implementation.
- **assessment rationale:** The assessment mix comprises quizzes, programming assignments, a course project, mid-semester, and end-semester examinations. This balanced structure evaluates both individual theoretical understanding through exams and quizzes, and practical software construction skills through programming assignments and a pair-programming project with milestones.
- **positioning rationale:** This course differs from CSE101, which provides basic procedural programming and an introductory touch to classes and objects, by focusing deeply on object-oriented design, architectural patterns, concurrency, testing, and team-based application building. It differs from CSE584, which concentrates on formal program verification, dependent types, and mathematical correctness proofs.