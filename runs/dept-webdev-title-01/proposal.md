# Web Development for All — Course Proposal (ProfsAgent draft)

> Run `dept-webdev-title-01` · generated deterministically from the design graph · validator status: **0 errors, 28 warnings** (see Appendix E). Approvals: gate1_context=approve (auto (dev run)), gate2_outcomes=approve (auto (dev run))

## 1. Assumption ledger (values not supplied by the professor)

| id | what | value | basis | confirm with |
|---|---|---|---|---|
| ASM01 | credits | 4 | UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit | course instructor / DOAA |
| ASM02 | L-T-P | 3-1-0 | UGREG-2025§4(2): 4-credit = 3h lecture + 1h interaction/week; lab hours 0 because no lab was requested | course instructor / DOAA |
| ASM03 | course level | 3 | no code/level given; set to the lowest target year (unspecified → 3) (INFERRED) | course instructor / DOAA |
| ASM04 | mid-semester exam timing | after teaching week 7 | mid-semester recess and exam fall roughly mid-way through 13 teaching weeks; confirm from the academic calendar | academic calendar (DOAA) |
| ASM05 | weekly student effort | None | not supplied; effort is reported (contact + take-home estimates), not constrained | course instructor / DOAA |

## 2. Course header

| Field | Value |
|---|---|
| Course Code | to be assigned (level 3xx) |
| Course Name | Web Development for All `[USER]` |
| Credits | 4 |
| L-T-P | 3-1-0 · 13 teaching weeks `[UGREG-2025§2, §4]` |
| Offered to | BTECH-COMMON, BTECH-CSE, BTECH-CSAI, MTECH-CSE · years [] |

## 3. Course description

This course provides a comprehensive grounding in full-stack web development principles, client-side dynamic interactivity, performance diagnostics, and secure backend service architecture. Students begin by constructing responsive multi-device web layouts using semantic HTML5 markup and CSS Flexbox and Grid models. They then progress to client-side scripting, utilizing asynchronous JavaScript, DOM manipulation, and Fetch APIs to build interactive web application features. The course further covers web performance profiling, where students diagnose network bottlenecks, rendering layout thrashing, and Core Web Vitals using browser developer tools. Finally, students evaluate RESTful backend service architectures with a focus on authentication patterns, OWASP security controls, and system scalability. Taught through 3 hours of lectures and 1 hour of tutorial per week over 13 weeks, the course enables students to build responsive front-end interfaces, integrate asynchronous web APIs, profile interface bottlenecks, and evaluate full-stack architectural trade-offs across usability, security, and scalability requirements.

## 4. Pre-requisites and anti-requisites

| Kind | Course | Relied-upon topics | Justification |
|---|---|---|---|

**Anti-requisites:** none — every checked course is below the anti-requisite overlap threshold (Appendix D).

**Existence check:** distinct — No candidate course in the catalogue has a weighted Jaccard overlap exceeding the substantial overlap threshold of 0.15.

## 5. Bloom band

L3–L5 · basis: level 3xx band [3,5] — provisional table (docs/01 §6.4), ceilings raised to BL4+ for the IIIT-D template rule; to be refit from corpus priors

## 6. Course Outcomes (Post Conditions) and Learning Outcomes

**CO1 (BL3, procedural) — Write responsive web layouts using standard HTML5 markup and CSS styling rules for specified multi-device wireframes.** `[CATALOGUE, INFERRED]`  
verb *write* · behaviour *responsive web layouts using standard HTML5 markup and CSS styling rules* · condition *given multi-device wireframes and accessibility guidelines* · degree *such that all rendered layout elements match wireframe specifications across target viewports without layout breaking* · evidence: programming_assignment, lab_task · marks share (computed): 28.25%

- CO1.LO1 (L3) Construct semantic HTML5 page structures for a given page layout wireframe, ensuring proper structural tags and ARIA accessibility attributes.
- CO1.LO2 (L3) Apply CSS Flexbox and Grid layout rules to align page elements according to a given single-viewport design specification.
- CO1.LO3 (L3 ★capstone) Write responsive CSS media queries for a supplied two-view wireframe sheet, ensuring interface rendering scales across mobile and desktop breakpoints.

**CO2 (BL3, procedural) — Implement dynamic client-side interactivity using asynchronous API requests and DOM manipulation for interactive web application features.** `[CATALOGUE, INFERRED]`  
verb *implement* · behaviour *dynamic client-side interactivity using asynchronous API requests and DOM manipulation* · condition *given backend API endpoints and user interaction event specifications* · degree *such that asynchronous data updates render correctly without full page reloads and all public interface tests pass* · evidence: programming_assignment, lab_task · marks share (computed): 29.75%

- CO2.LO1 (L3) Modify Document Object Model trees using JavaScript event listeners to update dynamic page elements in response to user actions.
- CO2.LO2 (L3) Execute asynchronous HTTP requests using Fetch API and Promises to parse structured JSON data from a backend endpoint.
- CO2.LO3 (L3 ★capstone) Implement dynamic client-side data updates using async API requests and DOM manipulation for a supplied live comments feed component.

**CO3 (BL4, procedural) — Diagnose performance bottlenecks and rendering issues in web interfaces with browser developer tools and performance metrics.** `[CATALOGUE, INFERRED]`  
verb *diagnose* · behaviour *performance bottlenecks and rendering issues in web interfaces* · condition *given a web application profile and browser network and performance logs* · degree *identifying at least three distinct performance bottlenecks supported by log evidence and performance metrics* · evidence: exam_question, lab_task · marks share (computed): 19.25%

- CO3.LO1 (L4) Analyze browser network waterfall logs to classify page loading latencies and resource transfer sizes.
- CO3.LO2 (L4) Inspect client-side JavaScript execution timelines and layout thrashing using browser performance profiling tools.
- CO3.LO3 (L4 ★capstone) Diagnose rendering performance bottlenecks in a supplied slow single-page web interface using browser developer tools and core web vitals.

**CO4 (BL5, conceptual) — Evaluate RESTful backend service designs against security, scalability, and usability requirements for a full-stack web system.** `[CATALOGUE, INFERRED]`  
verb *evaluate* · behaviour *RESTful backend service designs against security, scalability, and usability requirements* · condition *for a given full-stack web application architecture document* · degree *justifying each design decision against stated security and scalability requirements* · evidence: design_document, exam_question · marks share (computed): 22.75%

- CO4.LO1 (L4) Analyze RESTful URI structures and HTTP request methods against REST architectural constraints for a given web service spec.
- CO4.LO2 (L5) Assess authentication strategies and rate-limiting controls in a backend service design against security and scalability guidelines.
- CO4.LO3 (L5 ★capstone) Evaluate a supplied backend service architecture document against security and scalability constraints for a full-stack web application.

## 7. Weekly lecture plan

| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |
|---|---|---|---|---|---|
| 1 | Semantic HTML5 Markup and ARIA Accessibility Landmarks (M1.T1)<br>HTML5 Form Validation and Document Structure Rules (M1.T2) | CO1.LO1 | CO1 | Pair exercise constructing semantic HTML5 page structures and ARIA landmark attributes for a given layout mockup. |  |
| 2 | CSS Flexbox Model and One-Dimensional Layout Alignment (M1.T3)<br>CSS Grid Systems and Two-Dimensional Container Layouts (M1.T4) | CO1.LO2 | CO1 | Hands-on problem-solving to implement CSS Flexbox and Grid rules for a single-viewport layout specification. |  |
| 3 | Responsive CSS Media Queries and Viewport Breakpoints (M1.T5)<br>DOM Manipulation Tree Operations and Event Listener Handling (M2.T1) | CO1.LO3, CO2.LO1 | CO1, CO2 | Small-group coding exercise writing responsive media queries and testing breakpoint scaling across mobile and desktop views. | Q:Quiz1 (quiz) |
| 4 | DOM Manipulation Tree Operations and Event Listener Handling (M2.T1)<br>Asynchronous JavaScript, Promises, and Fetch API Integration (M2.T2) | CO2.LO1, CO2.LO2 | CO2 | Interactive DOM tree manipulation exercise using JavaScript event listeners to update dynamic page elements. | A:Assign1 released |
| 5 | Asynchronous JavaScript, Promises, and Fetch API Integration (M2.T2)<br>Dynamic Client-Side Component Rendering (M2.T3) | CO2.LO2, CO2.LO3 | CO2 | Guided pair-programming session executing Fetch API calls with Promises to parse dynamic JSON responses. | A:Assign1 due; Q:Quiz2 (quiz) |
| 6 | Dynamic Client-Side Component Rendering (M2.T3)<br>Real-Time UI Feed Updates and Async Error Handling (M2.T4)<br>Browser Network Waterfall Profiling and Resource Timing Analysis (M3.T1) | CO2.LO3, CO3.LO1 | CO2, CO3 | Code walkthrough and exercise implementing dynamic UI feed updates and async error handling for live components. | A:Assign2 released |
| 7 | Browser Network Waterfall Profiling and Resource Timing Analysis (M3.T1)<br>JavaScript Execution Timelines and Main-Thread Layout Thrashing (M3.T2) | CO3.LO1, CO3.LO2 | CO3 | Mid-semester review and practice analyzing browser network waterfall logs to classify network latency bottlenecks. | E:Midsem (midsem) |
| — | **Mid-semester recess + mid-sem exam** | | | | |
| 8 | JavaScript Execution Timelines and Main-Thread Layout Thrashing (M3.T2)<br>Core Web Vitals and Diagnostic Bottleneck Evaluation (M3.T3) | CO3.LO2, CO3.LO3 | CO3 | Hands-on profiling activity inspecting JavaScript execution timelines and main-thread layout thrashing using browser tools. | A:Assign2 due |
| 9 | Core Web Vitals and Diagnostic Bottleneck Evaluation (M3.T3)<br>REST Architectural Constraints and Resource URI Conventions (M4.T1) | CO3.LO3, CO4.LO1 | CO3, CO4 | Diagnostic session evaluating Core Web Vitals and identifying performance bottlenecks on a sample slow single-page interface. | Q:Quiz3 (quiz) |
| 10 | REST Architectural Constraints and Resource URI Conventions (M4.T1)<br>Web Application Authentication Strategies and OAuth/JWT Patterns (M4.T2)<br>API Rate-Limiting Controls and OWASP Vulnerability Assessment (M4.T3) | CO4.LO1, CO4.LO2 | CO4 | Case study analysis evaluating REST architectural constraints and URI conventions against service specifications. |  |
| 11 | API Rate-Limiting Controls and OWASP Vulnerability Assessment (M4.T3)<br>Backend Service Scalability and Load Balancing Architecture (M4.T4) | CO4.LO2, CO4.LO3 | CO4 | Group discussion and vulnerability audit assessing OAuth/JWT authentication strategies and API rate-limiting controls. | Q:Quiz4 (quiz) |
| 12 | Backend Service Scalability and Load Balancing Architecture (M4.T4)<br>Full-Stack Web Architecture Trade-off Evaluation (M4.T5) | CO4.LO3 | CO4 | Structured evaluation exercise analyzing backend service scalability and load balancing trade-offs in architecture documents. | R:Report1 released |
| 13 |  |  |  | Comprehensive review and problem-solving session covering full-stack web architecture evaluation and performance trade-offs. | R:Report1 due; E:Endsem (endsem) |

## 8. Weekly lab plan

No lab component (P = 0).

Infrastructure: Modern Web Browser with Developer Tools (Chrome/Firefox) and Code Editor (needs_confirmation)

## 9. Assessment plan

| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |
|---|---|---|---|---|---|
| assignment | 25.0 | A:Assign1 (W4→W5), A:Assign2 (W6→W8) | — | implement, design, tool-use |  |
| quiz | 15.0 | Q:Quiz1 (W3→W3), Q:Quiz2 (W5→W5), Q:Quiz3 (W9→W9), Q:Quiz4 (W11→W11) | best 3 of 4 | analyse-data, theory, tool-use |  |
| midsem | 20.0 | E:Midsem (W7→W7) | — | analyse-data, design, theory |  |
| report | 10.0 | R:Report1 (W12→W13) | — | evaluate-critique, written-communication | The written report is a focused 10% synthesis evaluation on backend architecture and security trade-offs, complementary to exams and programming assignments. |
| endsem | 30.0 | E:Endsem (W13→W13) | — | evaluate-critique, analyse-data, design, theory |  |
| **Sum** | **100.0** | | | | |

Per-CO marks share (computed from LO-level blueprint): CO1 28.25%, CO2 29.75%, CO3 19.25%, CO4 22.75%

## 10. Resource material

Policy: **mixed** — Standard foundational textbooks cover HTML, CSS, JavaScript, and Web Security, supplemented by reference texts for REST APIs and Web Performance.

| Role | Reference | Identifier | Verified | Supports |
|---|---|---|---|---|
| primary | Jon Duckett (2014). *HTML & CSS*. | 9781118871645 | yes | M1.T1, M1.T2, M1.T3, M1.T5 |
| primary | Marijn Haverbeke (2024). *Eloquent Javascript*. | 9781718504110 | yes | M2.T1, M2.T2, M2.T3, M2.T4 |
| reference | Ilya Grigorik (2014). *High Performance Browser Networking*. | 9789351104711 | yes | M3.T1, M3.T3, M4.T4 |
| reference | Leonard Richardson, Michael Amundsen, Sam Ruby (2013). *RESTful Web APIs: Services for a Changing World*. | 9781449358068 | yes | M4.T1, M4.T5 |
| reference | Dafydd Stuttard, Marcus Pinto (2011). *The web application hacker's handbook*. | 9788126533404 | yes | M4.T2, M4.T3 |

## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)

| CO | PO1 | PO2 | PO3 | PO4 | PO5 | PO10 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PSO1 | PSO2 | PSO3 | PSO4 | PSO5 | PO2 | PSO1 | PSO2 | PSO3 | PSO4 | PSO8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CO1 | 2 [unclaimed] | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [2] |  | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 3 [3] | 2 [2] | 2 [1] | 2 [unclaimed] | 3 [2] | 2 [unclaimed] | 3 [unclaimed] |  | 2 [unclaimed] | 2 [unclaimed] | 3 [3] | 2 [2] |  |
| CO2 | 2 [unclaimed] | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [2] |  | 2 [unclaimed] | 2 [unclaimed] | 2 [2] | 3 [3] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 3 [2] | 2 [unclaimed] | 3 [1] |  | 2 [unclaimed] | 2 [2] | 3 [3] | 2 [unclaimed] |  |
| CO3 | 3 [unclaimed] | 3 [3] | 3 [unclaimed] | 3 [unclaimed] | 1 [3] |  | 3 [unclaimed] | 3 [unclaimed] | 3 [2] | 3 [unclaimed] | 1 [3] | 3 [unclaimed] | 3 [unclaimed] | 3 [unclaimed] | 3 [3] | 3 [unclaimed] |  | 3 [unclaimed] | 3 [2] | 3 [unclaimed] | 1 [3] |  |
| CO4 | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 3 [unclaimed] | 1 [unclaimed] | 2 [2] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 3 [3] | 1 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 2 [unclaimed] | 3 [3] | 2 [unclaimed] | 2 [2] | 2 [unclaimed] | 2 [unclaimed] | 3 [3] | 1 [unclaimed] | 2 [unclaimed] |

PO legend: PO1 = PO1; PO2 = PO2; PO3 = PO3; PO4 = PO4; PO5 = PO5; PO10 = PO10; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO5 = PSO5; PO2 = PO2; PSO1 = PSO1; PSO2 = PSO2; PSO3 = PSO3; PSO4 = PSO4; PSO8 = PSO8

- CO1→PO3: Writing responsive web layouts directly contributes to designing user interface components that satisfy multi-device functional specifications. (activities: design, implement)
- CO1→PO5: Utilizing modern standard HTML5 markup and CSS layout techniques requires applying current web development tools. (activities: implement, tool-use)
- CO1→PSO4: Designing and implementing responsive frontend components fulfills application needs using contemporary web standards. (activities: design, implement)
- CO1→PSO5: Applies standard CSS layout engines and frontend markup techniques for multi-device web user interface engineering. (activities: tool-use)
- CO1→PSO3: Translates wireframe layout specifications into structured DOM trees and responsive CSS rendering rules. (activities: design, implement)
- CO1→PSO1: Requires basic foundational understanding of web technologies, markup structure, and document rendering principles. (activities: theory)
- CO1→PSO3: Developing responsive interfaces enables constructing compliant client-side presentation layers for modern applications. (activities: design, implement)
- CO1→PSO4: Leverages HTML5 semantic elements and modern CSS layout mechanisms to implement multi-device web user interfaces. (activities: tool-use)
- CO2→PO3: Implementing dynamic client-side interactivity builds functional interactive application components. (activities: implement, design)
- CO2→PO5: Employs modern asynchronous fetch APIs and browser DOM manipulation mechanisms. (activities: implement, tool-use)
- CO2→PSO4: Directly implements interactive client-side application modules communicating with backend endpoints. (activities: implement, design)
- CO2→PSO3: Adapts established asynchronous programming patterns and event-handling techniques to implement dynamic client features. (activities: analyse-data)
- CO2→PSO3: Implements asynchronous data handling and DOM state update logic for interactive application workflows. (activities: implement)
- CO2→PSO5: Provides client-side interface integration mechanisms suitable for displaying data-driven application responses. (activities: implement)
- CO2→PSO3: Develops interactive client-side execution layers integrated with RESTful application services. (activities: implement)
- CO2→PSO2: Adapts event-driven programming paradigms and asynchronous data fetch mechanisms to user interaction tasks. (activities: analyse-data)
- CO3→PO2: Diagnosing performance bottlenecks requires systematic analysis of network logs and browser execution metrics. (activities: analyse-data, evaluate-critique)
- CO3→PO5: Uses specialized browser developer tools and profiling instrumentation to diagnose rendering bottlenecks. (activities: tool-use)
- CO3→PSO5: Applies browser diagnostic toolchains and profiling techniques for web performance engineering. (activities: tool-use)
- CO3→PSO3: Analyzes bottleneck patterns using profiling data to identify interface rendering inefficiencies. (activities: analyse-data)
- CO3→PSO4: Analyzes quantitative network logs and rendering timeline data to pinpoint runtime bottlenecks. (activities: analyse-data, evaluate-critique)
- CO3→PSO4: Utilizes advanced browser profiling and network diagnostic tools to evaluate interface performance. (activities: tool-use)
- CO3→PSO2: Applies performance diagnostic models to analyze empirical trace data and logs. (activities: analyse-data)
- CO4→PO2: Evaluating backend architectures involves analytical assessment of security and scalability constraints. (activities: evaluate-critique, analyse-data)
- CO4→PO10: Articulates architectural evaluations and design trade-offs within structured design documentation. (activities: written-communication)
- CO4→PSO4: Evaluates full-stack architectural designs against specified non-functional requirements. (activities: evaluate-critique, design)
- CO4→PSO4: Analyzes web architecture documentation against systemic security and scalability trade-offs. (activities: evaluate-critique, analyse-data)
- CO4→PO2: Produces written technical evaluations justifying architectural decisions against requirements. (activities: written-communication)
- CO4→PSO3: Critically evaluates server-side service designs to ensure robustness, security, and scalability. (activities: evaluate-critique)

## Appendix B — Traceability matrix (LO → topics → weeks → assessments)

| LO | Bloom | Topics | Weeks | Assessed by |
|---|---|---|---|---|
| CO1.LO1 | L3 | M1.T1, M1.T2 | 1 | A:Assign1@L3, Q:Quiz1@L3, E:Midsem@L3 |
| CO1.LO2 | L3 | M1.T3, M1.T4 | 2 | A:Assign1@L3, Q:Quiz1@L3, E:Midsem@L3 |
| CO1.LO3 | L3 | M1.T5 | 3 | A:Assign1@L3, E:Midsem@L3, E:Endsem@L3 |
| CO2.LO1 | L3 | M2.T1 | 3, 4 | A:Assign2@L3, Q:Quiz2@L3, E:Midsem@L3 |
| CO2.LO2 | L3 | M2.T2 | 4, 5 | A:Assign2@L3, Q:Quiz2@L3, E:Midsem@L3 |
| CO2.LO3 | L3 | M2.T3, M2.T4 | 5, 6 | A:Assign2@L3, E:Midsem@L3, E:Endsem@L3 |
| CO3.LO1 | L4 | M3.T1 | 6, 7 | Q:Quiz3@L4, E:Midsem@L4, E:Endsem@L4 |
| CO3.LO2 | L4 | M3.T2 | 7, 8 | Q:Quiz3@L4, E:Endsem@L4 |
| CO3.LO3 | L4 | M3.T3 | 8, 9 | Q:Quiz3@L4, E:Endsem@L4 |
| CO4.LO1 | L4 | M4.T1 | 9, 10 | Q:Quiz4@L4, E:Endsem@L4 |
| CO4.LO2 | L5 | M4.T2, M4.T3 | 10, 11 | Q:Quiz4@L5, R:Report1@L5, E:Endsem@L5 |
| CO4.LO3 | L5 | M4.T4, M4.T5 | 11, 12 | R:Report1@L5, E:Endsem@L5 |

## Appendix C — Modules and topics

**M1 HTML5, CSS Layouts, and Responsive Web Design** (primary CO1)
- M1.T1 Semantic HTML5 Markup and ARIA Accessibility Landmarks — 1.5 h · LOs CO1.LO1
- M1.T2 HTML5 Form Validation and Document Structure Rules — 1.5 h · LOs CO1.LO1 · requires M1.T1
- M1.T3 CSS Flexbox Model and One-Dimensional Layout Alignment — 1.5 h · LOs CO1.LO2 · requires M1.T1
- M1.T4 CSS Grid Systems and Two-Dimensional Container Layouts — 1.5 h · LOs CO1.LO2 · requires M1.T3
- M1.T5 Responsive CSS Media Queries and Viewport Breakpoints — 2.5 h · LOs CO1.LO3 · requires M1.T4
**M2 Client-Side Scripting and Asynchronous Web APIs** (primary CO2)
- M2.T1 DOM Manipulation Tree Operations and Event Listener Handling — 2.5 h · LOs CO2.LO1 · requires M1.T1
- M2.T2 Asynchronous JavaScript, Promises, and Fetch API Integration — 2.5 h · LOs CO2.LO2 · requires M2.T1
- M2.T3 Dynamic Client-Side Component Rendering — 2.0 h · LOs CO2.LO3 · requires M2.T2
- M2.T4 Real-Time UI Feed Updates and Async Error Handling — 2.0 h · LOs CO2.LO3 · requires M2.T3
**M3 Web Performance Diagnostic Profiling and Optimization** (primary CO3)
- M3.T1 Browser Network Waterfall Profiling and Resource Timing Analysis — 2.5 h · LOs CO3.LO1 · requires M2.T4
- M3.T2 JavaScript Execution Timelines and Main-Thread Layout Thrashing — 2.5 h · LOs CO3.LO2 · requires M3.T1
- M3.T3 Core Web Vitals and Diagnostic Bottleneck Evaluation — 2.5 h · LOs CO3.LO3 · requires M3.T2
**M4 RESTful Web Architecture, Security, and Backend Evaluation** (primary CO4)
- M4.T1 REST Architectural Constraints and Resource URI Conventions — 2.5 h · LOs CO4.LO1 · requires M2.T2
- M4.T2 Web Application Authentication Strategies and OAuth/JWT Patterns — 2.0 h · LOs CO4.LO2 · requires M4.T1
- M4.T3 API Rate-Limiting Controls and OWASP Vulnerability Assessment — 2.0 h · LOs CO4.LO2 · requires M4.T2
- M4.T4 Backend Service Scalability and Load Balancing Architecture — 2.0 h · LOs CO4.LO3 · requires M4.T3
- M4.T5 Full-Stack Web Architecture Trade-off Evaluation — 2.5 h · LOs CO4.LO3 · requires M4.T4

Schedule: feasible · 36.0 h needed / 39 h available

## Appendix D — Curriculum positioning

| Course | Computed overlap | Verdict | Differentiation |
|---|---|---|---|

Overlap method: neo4j: no topics or no embeddings

**Comparable courses**

- **CSE566** Mobile & Middleware Systems — IIIT-D catalogue. Take: RESTful web service design patterns and backend service interaction principles. Avoid: Focus on mobile crowdsensing, mobile database caching, and low-level system middleware.
- **DES205** Design of Interactive Systems — IIIT-D catalogue. Take: User experience principles and task design for web-based interactive systems. Avoid: Focus on cognitive memory modeling and non-web multimodal interfaces.
- **CSE508** Information Retrieval — IIIT-D catalogue. Take: Basic web markup structures (HTML, XML) and practical web interface design. Avoid: Heavy theoretical focus on search engine indexing algorithms, vector space models, and web crawling.

## Appendix E — Validation report (deterministic validators; not LLM self-assessment)

**0 errors, 28 warnings.** Repeats of the same check are merged into one row; the full list is in `validation_report.json`.

| Area | Severity | Check | Count | Parts of the design | Example |
|---|---|---|---|---|---|
| Outcomes (COs and LOs) | warning | V11 | 23 | CO1.LO1, CO1.LO2, CO1.LO3, CO2.LO1, CO2.LO2, CO2.LO3, CO3.LO1, CO3.LO2 (+4 more) | LO CO1.LO1 condition is not visible in the statement text |
| CO–PO mapping | warning | V23 | 4 | CO2, BTECH-CSAI/PSO5, CO3, BTECH-COMMON/PO5, BTECH-CSE/PSO5, MTECH-CSE/PSO4 | CO2→BTECH-CSAI/PSO5: provisional 1 vs computed 3 (share 0.874) |
| Topics, schedule and labs | warning | V6 | 1 | W13 | weeks with no lecture topics: [13] |

**Repair history**

- cos: errors 2 → 0 · round 1 accepted (1→0)
- assessment: errors 4 → 0 · round 1 accepted (4→0)

**Model-reported concerns (not validated; for the professor's attention)**

- intake: intake_form_completeness: Only the course name was supplied in the intake form. All structural and content parameters must be resolved via regulations, defaults, or institutional knowledge graph retrieval.
- positioning: CCO.topic_groups: The intake form provided no topic groups or syllabus topics, preventing detailed topic-level prerequisite analysis and overlap calculation.
- constraints: CCO: No free-text requirements, assessment preferences, special constraints, or topic groups were provided in the CCO.
- constraints: CCO.lab: Course is titled 'Web Development for All' with LTP (3-1-0), but lab.required is null and P is 0. Clarification may be needed on practical component requirements.
- cos: CCO.topics_treatment: Topics treatment is marked as missing in CCO input context; proposed topic groups TG1-TG4 to establish a consistent curriculum structure.
- labs: V18: Course LTP is 3-1-0 with 0 lab hours (P=0), but nine learning outcomes (CO1.LO1, CO1.LO2, CO1.LO3, CO2.LO1, CO2.LO2, CO2.LO3, CO3.LO1, CO3.LO2, CO3.LO3) require hands-on practice. Hands-on practice has been integrated into tutorial sessions.
- resources: OL:OL19980166W: Publication year is 2014, which predates modern CSS Grid standards; supplemented by online documentation search request.
- narrative: positioning_rationale: No specific existing course codes were provided in the overlaps context, so positioning rationale evaluates against general subject areas rather than explicit course UIDs.

## Appendix F — Rationales (G11)

- **sequencing rationale:** Modules follow a structural progression starting from foundational layout design in M1 to dynamic client-side behavior in M2. M3 builds on client-side rendering by diagnosing performance bottlenecks and rendering issues. Finally, M4 expands the scope to full-stack system architecture, evaluating RESTful backend service design, security, and scalability after students have mastered front-end and profiling principles.
- **assessment rationale:** The assessment strategy combines formative and summative evaluation to match the learning levels of the COs. Continuous assignments (25%) and quizzes (15%) evaluate hands-on layout construction and client-side scripting (CO1, CO2). Examinations (20% midsem, 30% endsem) test conceptual understanding of web architecture and diagnostics (CO3, CO4). A technical report (10%) specifically assesses backend service design evaluation and trade-off analysis (CO4).
- **positioning rationale:** This course integrates client-side layout, dynamic API integration, interface performance diagnostics, and backend architecture evaluation into a single 3-1-0 elective. Unlike specialized backend or advanced software engineering courses, it provides a holistic end-to-end view of web system design, focusing equally on front-end rendering, profiling, and RESTful service evaluation.