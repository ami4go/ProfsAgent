# Advanced Programming — Course Proposal (ProfsAgent draft)

> Run `cse201-dev-05` · generated deterministically from the design graph · validator status: **3 errors, 6 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

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

Advanced Programming is a second programming course that moves students from writing small single-file programs to building larger applications made of several components with clear interfaces. Designed for second-year Bachelor of Technology students in Computer Science and Engineering, the course focuses on object-oriented design, robust programming, software testing, concurrency, and event-driven applications with graphical user interfaces. Students learn how to write code that others can reuse and test, structure programs around established design patterns, and handle errors, input/output, and multi-threading. By the end of the course, students are able to implement object-oriented classes and inheritance hierarchies, construct multi-threaded applications, deconstruct requirements using UML diagrams, and evaluate a working multi-component application developed in pairs using version control and unit testing. The course is taught through lectures and tutorials with regular hands-on practice, utilizing Java as the vehicle while remaining focused on program design rather than language features alone.

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
verb *implement* · behaviour *object-oriented classes, inheritance hierarchies, and interfaces, using Java collections and generics* · condition *using Java collections and generics* · degree *such that all public test cases pass and static analysis warnings are resolved* · evidence: programming_assignment, exam_question · marks share (computed): 29.5%

- CO1.LO1 (L3) Implement class encapsulation, association, and composition relationships, using basic object principles, such that all public test cases pass.
- CO1.LO2 (L3) Implement inheritance hierarchies, abstract classes, and interface-based polymorphism, using object-oriented principles, such that all public test cases pass.
- CO1.LO3 (L3 ★capstone) Implement generic classes and methods using the collections framework, given a data processing requirement, such that all public test cases pass and static analysis warnings are resolved.

**CO2 (L3, procedural) — Apply exception handling, assertions, and I/O serialization to develop robust programs, given a specification with error cases, meeting the stated interface specification for every public method.** `[USER]`  
verb *apply* · behaviour *exception handling, assertions, and I/O serialization to develop robust programs* · condition *given a specification with error cases* · degree *meeting the stated interface specification for every public method* · evidence: programming_assignment, lab_task · marks share (computed): 15.67%

- CO2.LO1 (L3) Apply exception handling and assertions to validate input conditions, given a specification with error cases, such that at least 80% of the provided test cases pass.
- CO2.LO2 (L3 ★capstone) Apply I/O streams and object serialization to persist object state, given a specification with error cases, meeting the stated interface specification for every public method.

**CO3 (L4, conceptual) — Deconstruct software requirements into UML class, sequence, and use-case diagrams, using object-oriented design principles, covering every use case in the supplied requirements document.** `[CORPUS, USER]`  
verb *deconstruct* · behaviour *software requirements into UML class, sequence, and use-case diagrams* · condition *using object-oriented design principles* · degree *covering every use case in the supplied requirements document* · evidence: design_document, exam_question · marks share (computed): 23.17%

- CO3.LO1 (L4) Identify use cases and actor interactions, using object-oriented design principles, covering every use case in the supplied requirements document.
- CO3.LO2 (L4 ★capstone) Deconstruct software requirements into UML class and sequence diagrams, using object-oriented design principles, covering every use case in the supplied requirements document.

**CO4 (L3, procedural) — Construct multi-threaded applications using synchronization primitives and thread pools, given a concurrent task specification, such that at least 80% of the provided test cases pass without race conditions.** `[CORPUS, USER]`  
verb *construct* · behaviour *multi-threaded applications using synchronization primitives and thread pools* · condition *given a concurrent task specification* · degree *such that at least 80% of the provided test cases pass without race conditions* · evidence: programming_assignment, lab_task · marks share (computed): 23.33%

- CO4.LO1 (L3) Implement threads and mutual exclusion locks, given a concurrent task specification, such that at least 80% of the provided test cases pass without race conditions.
- CO4.LO2 (L3 ★capstone) Construct multi-threaded applications using thread pools and coordination patterns, given a concurrent task specification, such that at least 80% of the provided test cases pass without race conditions.

**CO5 (L5, metacognitive) — Evaluate a working multi-component application with a graphical user interface developed in pairs, using version control and unit testing, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.** `[CORPUS, USER]`  
verb *evaluate* · behaviour *a working multi-component application with a graphical user interface in pairs, using version control and unit testing* · condition *working in pairs using version control and unit testing tools* · degree *such that the delivered system satisfies every acceptance criterion agreed at the first milestone* · evidence: project_deliverable, presentation, code_review · marks share (computed): 11.67%

- CO5.LO1 (L3) Execute unit testing and version control workflows for a multi-component application developed in pairs, working in pairs using version control and unit testing tools, justifying each design decision against at least one stated requirement.
- CO5.LO2 (L5 ★capstone) Evaluate a working multi-component application with a graphical user interface developed in pairs, working in pairs using version control and unit testing tools, such that the delivered system satisfies every acceptance criterion agreed at the first milestone.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Classes, encapsulation, and regular hands-on practice (M1.T1)<br>Object relationships, association, and composition (M1.T2) | CO1.LO1 | CO1 | Implement a small class hierarchy with encapsulation, association and composition; run provided test cases in pairs |  |
| 2 | Inheritance hierarchies and abstract classes (M1.T3)<br>Interface-based polymorphism and method resolution (M1.T4) | CO1.LO2 | CO1 | Extend previous classes to include inheritance and interfaces; debug failing cases using IDE | A:Quiz1 (quiz); A:PA1 released |
| 3 | Generic classes and methods (M2.T1)<br>Comparing, cloning, and the collections framework (M2.T2) | CO1.LO3 | CO1 | Create generic collection utilities; write unit tests for type safety |  |
| 4 | Exception handling and assertions (M2.T3)<br>I/O streams and object serialization (M2.T4) | CO2.LO1, CO2.LO2 | CO2 | Add exception handling and assertions to previous utilities; verify error paths | A:Quiz2 (quiz); A:PA1 due; A:PA2 released; A:ProjMilestone1 released |
| 5 | Use cases and actor interactions (M3.T1)<br>UML class and sequence diagrams (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Discuss use‑case identification and actor mapping for a sample system; produce a brief use‑case list |  |
| 6 | UML class and sequence diagrams (M3.T2)<br>Unit testing and version control workflows (M4.T1) | CO3.LO2, CO5.LO1 | CO3, CO5 | Draw UML class and sequence diagrams for the sample system; peer‑review diagrams | A:PA2 due |
| 7 | Unit testing and version control workflows (M4.T1)<br>Common creational, structural, and behavioural design patterns (M4.T2) | CO3.LO2, CO5.LO1 | CO3, CO5 | Introduce version‑control workflow; create a repository and commit initial design artifacts | A:Quiz3 (quiz); A:PA3 released; A:ProjMilestone1 due; A:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | Threads, mutual exclusion, and locks (M5.T1)<br>Thread pools and producer-consumer patterns (M5.T2) | CO4.LO1, CO4.LO2 | CO4 | Implement a synchronized counter using threads and locks; run concurrency tests | A:PA3 due; A:ProjMilestone2 released |
| 9 | Thread pools and producer-consumer patterns (M5.T2)<br>Event-driven programming, GUIs, and pair programming workflows (M5.T3) | CO4.LO2, CO5.LO2 | CO4, CO5 | Build a thread‑pool based producer‑consumer demo; analyse thread‑safety | A:Quiz4 (quiz); A:PA4 released |
| 10 | Event-driven programming, GUIs, and pair programming workflows (M5.T3) | CO5.LO2 | CO5 | Create a simple GUI event‑driven application; pair‑program and integrate with version control | A:PA4 due |
| 11 |  |  |  | Open tutorial for catch‑up, discussion of any pending concepts, and preparation for final assessment |  |
| 12 |  |  |  | Open tutorial for project demo rehearsals and peer feedback |  |
| 13 |  |  |  | Open tutorial for final Q&A and reflection on learning outcomes | A:ProjMilestone2 due; A:Endsem (endsem) |

## 8. Weekly lab plan

No lab component (P = 0).

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| quiz | 10.0 | A:Quiz1 (W2→W2), A:Quiz2 (W4→W4), A:Quiz3 (W7→W7), A:Quiz4 (W9→W9) | best 3 of 4 | analyse-data, tool-use |  |
| assignment | 20.0 | A:PA1 (W2→W4), A:PA2 (W4→W6), A:PA3 (W7→W8), A:PA4 (W9→W10) | — | implement, tool-use |  |
| project | 25.0 | A:ProjMilestone1 (W4→W7), A:ProjMilestone2 (W8→W13) | — | design, implement, evaluate-critique, teamwork, written-communication, oral-presentation, tool-use |  |
| midsem | 20.0 | A:Midsem (W7→W7) | — | design, implement, analyse-data |  |
| endsem | 25.0 | A:Endsem (W13→W13) | — | design, implement, analyse-data, evaluate-critique |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 29.5%, CO2 15.67%, CO3 23.17%, CO4 23.33%, CO5 11.67%

## 10. Resource material

Policy: **mixed** — The course covers object-oriented design, robust programming, design patterns, and concurrency using Java, supported by standard authoritative textbooks alongside specialized references for concurrency.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Joshua Bloch (2008). *Effective Java*. | 9780132778046 | yes | M1.T1, M2.T1, M2.T3 |
| primary | Erich Gamma, John Vlissides, Richard Helm, Ralph Johnson (1995). *Design Patterns: Elements of Reusable Object-Oriented Software*. | 9780133052664 | yes | M4.T2 |
| reference | Brian Goetz, Joshua Bloch, Joseph Bowbeer, Doug Lea (2006). *Java Concurrency in Practice*. | 9780132702256 | yes | M5.T1, M5.T2 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO3 | PO4 | PO5 | PO7 | PO9 |
|---|---|---|---|---|---|
| CO1 | 3 [unclaimed] | 3 [3] |  |  | 2 [2] |
| CO2 | 3 [2] | 3 [3] |  |  | 3 [unclaimed] |
| CO3 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [2] | 3 [unclaimed] |
| CO4 | 2 [unclaimed] | 3 [3] | 1 [unclaimed] | 1 [unclaimed] | 3 [2] |
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
| CO1.LO1 | L3 | M1.T1, M1.T2 | 1 | A:Quiz1@L3, A:PA1@L3, A:Midsem@L3 |
| CO1.LO2 | L3 | M1.T3, M1.T4 | 2 | A:Quiz1@L3, A:PA1@L3, A:Midsem@L3 |
| CO1.LO3 | L3 | M2.T1, M2.T2 | 3 | A:Quiz2@L3, A:PA2@L3, A:Midsem@L3, A:Endsem@L3 |
| CO2.LO1 | L3 | M2.T3 | 4 | A:Quiz2@L3, A:PA2@L3, A:Midsem@L3 |
| CO2.LO2 | L3 | M2.T4 | 4 | A:PA3@L3, A:Endsem@L3 |
| CO3.LO1 | L4 | M3.T1 | 5 | A:Quiz3@L4, A:ProjMilestone1@L4, A:Midsem@L4 |
| CO3.LO2 | L4 | M3.T2, M4.T2 | 5, 6, 7 | A:ProjMilestone1@L4, A:Endsem@L4 |
| CO4.LO1 | L3 | M5.T1 | 8 | A:Quiz4@L3, A:PA4@L3, A:Endsem@L3 |
| CO4.LO2 | L3 | M5.T2 | 8, 9 | A:Quiz4@L3, A:PA4@L3, A:ProjMilestone2@L3, A:Endsem@L3 |
| CO5.LO1 | L3 | M4.T1 | 6, 7 | A:Quiz3@L3, A:PA3@L3 |
| CO5.LO2 | L5 | M5.T3 | 9, 10 | A:ProjMilestone2@L5 |

## Appendix C — Modules and topics

**M1 Object-Oriented Fundamentals and Principles** (primary CO1)
- M1.T1 Classes, encapsulation, and regular hands-on practice — 1.5 h · LOs CO1.LO1
- M1.T2 Object relationships, association, and composition — 1.5 h · LOs CO1.LO1 · requires M1.T1
- M1.T3 Inheritance hierarchies and abstract classes — 1.5 h · LOs CO1.LO2 · requires M1.T2
- M1.T4 Interface-based polymorphism and method resolution — 1.5 h · LOs CO1.LO2 · requires M1.T3
**M2 Generics, Collections, and Robust Programming** (primary CO1, CO2)
- M2.T1 Generic classes and methods — 1.5 h · LOs CO1.LO3 · requires M1.T4
- M2.T2 Comparing, cloning, and the collections framework — 1.5 h · LOs CO1.LO3 · requires M2.T1
- M2.T3 Exception handling and assertions — 1.5 h · LOs CO2.LO1 · requires M2.T2
- M2.T4 I/O streams and object serialization — 1.5 h · LOs CO2.LO2 · requires M2.T3
**M3 Object-Oriented Design and Modeling** (primary CO3)
- M3.T1 Use cases and actor interactions — 2.0 h · LOs CO3.LO1
- M3.T2 UML class and sequence diagrams — 2.0 h · LOs CO3.LO2 · requires M3.T1
**M4 Testing, Tooling, and Design Patterns** (primary CO5)
- M4.T1 Unit testing and version control workflows — 2.5 h · LOs CO5.LO1 · requires M2.T2
- M4.T2 Common creational, structural, and behavioural design patterns — 2.5 h · LOs CO3.LO2 · requires M1.T4
**M5 Concurrency, GUIs, and Project Integration** (primary CO4, CO5)
- M5.T1 Threads, mutual exclusion, and locks — 2.0 h · LOs CO4.LO1
- M5.T2 Thread pools and producer-consumer patterns — 2.0 h · LOs CO4.LO2 · requires M5.T1
- M5.T3 Event-driven programming, GUIs, and pair programming workflows — 2.5 h · LOs CO5.LO2 · requires M1.T4

Schedule: feasible · 27.5 h needed / 39.0 h available

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
| los | VLO-COPY | error | CO3.LO2, CO3 | CO3.LO2 restates its parent CO3 (token overlap 1.00); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO4.LO2, CO4 | CO4.LO2 restates its parent CO4 (token overlap 0.85); an LO must be a narrower, single-task step |
| los | VLO-COPY | error | CO5.LO2, CO5 | CO5.LO2 restates its parent CO5 (token overlap 0.97); an LO must be a narrower, single-task step |
| assessment | VA-LOAD | warning | W07 | 3 assessment events due in week 7 (cap 2) |
| copo | VCOPO-ACT | warning | CO2, BTECH-CSE/PO3 | CO2→BTECH-CSE/PO3: none of its evidencing activities maps to that PO, so its strength can never be computed |
| cos | V11 | warning | CO5 | CO CO5 condition is not visible in the statement text |
| los | V21 | warning |  | LO lecture-hour estimates sum to 30.0 h vs budget 39.0 h (±15%) |
| los | VB | warning | CO3.LO1 | LO CO3.LO1: claimed Bloom L4 but verb 'identify' is lexicon L1 |
| schedule | V6 | warning | W11, W12, W13 | weeks with no lecture topics: [11, 12, 13] |

**Repair history**

- cos: errors 1 → 0 · round 1 accepted (1→0)
- los: errors 3 → 3 · round 1 rejected (3→4); round 2 rejected (3→3); round 3 rejected (3→4)
- structure: errors 2 → 0 · round 1 accepted (2→0)
- assessment: errors 4 → 0 · round 1 accepted (4→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: semester_weeks: Semester weeks field was marked as not specified in the input, but regulations (UGREG-2025§2) specify 13 weeks of teaching.
- intake: weekly_effort_hours: Weekly student effort hours are omitted from the intake form.
- positioning: Lab credits and LTP structure: The CCO specifies L=3.0, T=1.0, P=0 with 4 credits, but the description and special constraints mandate a team project with a graphical interface and regular hands-on practice. Ensure that tutorial slots or informal lab support adequately accommodate practical execution.
- los: hours_budget: The sum of estimated lecture hours (29.5) and tutorial hours (11.0) is slightly below the target budget (39.0 lecture and 13.0 tutorial hours) because exact topic granularity distributes across 11 LOs. This will be balanced during weekly scheduling.
- labs: V18: Hands‑on LOs exist but lab hours are zero; practice has been placed in tutorials, which may need adjustment to meet curriculum requirements.

## Appendix F — Rationales (G11)

- **sequencing rationale:** The modules progress from foundational object-oriented principles and inheritance to generics, robust programming, and design modeling, establishing prerequisites through CSE101 and CSE102 before advancing to testing, design patterns, concurrency, and project integration.
- **assessment rationale:** The assessment mix balances individual theoretical understanding through quizzes, mid-semester, and end-semester examinations with practical competence through programming assignments and a pair-programming course project.
- **positioning rationale:** Unlike CSE101 which covers basic procedural programming and introductory objects, and CSE584 which focuses on formal program verification, this course deepens object-oriented design, architectural patterns, concurrency, and team-based application development.