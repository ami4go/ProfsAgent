# Delivery support — Software Development using AI

Run `cs601-c2` · generated 2026-11-02 23:48:48 · 27 lectures with recommendations. Every link was checked to exist; items are ranked by how well they cover the lecture's topic and learning outcomes, then quality (AI review), source, level, reception and practicality. Decide in `review.yaml` (approve / replace / reject + reason).

## W01.L1 · Week 1 · Developer workflows and AI-assisted coding ★ new at IIIT-D
*A 2-hour lecture in week 1 on “Developer workflows and AI-assisted coding”, part of the module “AI-Assisted Coding and Developer Workflows”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Identify the core components of developer workflows and AI-assisted coding using contextualisation guidelines for most short items (remember). This serves CO1: Configure AI-assisted coding agents and tool integrations using model context protocols, for a given development environment, such that … Students come in knowing CSE201 (Unit testing using JUnit, version controlling and collaboration). It prepares for Model context protocols and architecture (week 1). Assessed in Quiz1 (week 3), Midsem (week 7), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:43). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Evolution from Traditional to AI-Augmented Developer Workflows** — Understand how software development lifecycles transition from manual writing and manual searching to AI-augmented authoring. Identify the shift from linear edi | 15 | [Prompt to Production: The Future of AI Code W](https://www.youtube.com/watch?v=bs1qPy_CWkM&t=263s) 4:23–6:44 (fully) + NotebookLM |
| C2 | **Core Architectural Components of Modern AI Code Assistants** — Identify the primary software building blocks connecting an editor to an underlying generative model. Detail how client-side plugins gather telemetry, local buf | 15 | NotebookLM video (`notebooklm/W01.L1.md`) |
| C3 | **Context Retrieval and Window Slicing in AI Assistants** — Understand how AI assistants extract active file snippets, open tabs, and recent terminal outputs to populate an inference prompt. Examine how context budgets l | 20 | NotebookLM video (`notebooklm/W01.L1.md`) |
| C4 | **Contextualisation Guidelines for Scoped Code Generation Tasks** — Identify and apply core contextualisation guidelines to constrain AI prompts for short coding items such as utility functions, docstrings, and unit tests. Expla | 15 | NotebookLM video (`notebooklm/W01.L1.md`) |
| C5 | **Interaction Modalities: Ghost Text, Chat, and Inline Edits** — Compare the operational patterns of in-line ghost-text autocompletion, docked conversational sidebars, and targeted in-line refactoring. Analyze when a develope | 15 | [AI-Assisted Coding Tutorial – OpenClaw, GitHu](https://www.youtube.com/watch?v=wlpBCazAY9Q&t=613s) 10:13–12:42 (partly) + NotebookLM for: docked chat sidebar usage; inline refactoring; comparison of modalities |
| C6 | **Demonstration of Context Feeding in an AI-Assisted IDE** — Observe how an AI coding assistant dynamically alters suggested code based on open editor tabs, language server protocol (LSP) diagnostics, and active comments. | 15 | NotebookLM video (`notebooklm/W01.L1.md`) |
| C7 | **Common Failure Modes: Hallucination and Stale Context in Workflows** — Examine concrete examples where AI assistants hallucinate deprecated API methods, fabricate package dependencies, or carry stale context across branch switches. | 10 | NotebookLM video (`notebooklm/W01.L1.md`) |
| C8 | **Verification Strategies and Quality Gates for AI-Assisted Code** — Evaluate verification techniques necessary to safely assimilate AI-generated snippets into professional codebases. Discuss the role of automated linting, locali | 15 | in class (discussion) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W01.L1.md`

**Videos**

1. [Prompt to Production: The Future of AI Code Workflows](https://www.youtube.com/watch?v=bs1qPy_CWkM) — score 0.36
   Teaches C1 Evolution from Traditional to AI-Augmented Developer Workflo (4:23–6:44, fully) [checked on the transcript] · IBM Technology · tier 2 · 7:15 · 73,588 views
   *Review:* Clear walkthrough of AI scaling execution vs verification; emphasizes evidence-based trust. Use: in-class clip.
2. [AI-Assisted Coding Tutorial – OpenClaw, GitHub Copilot, Claude Code, CodeRabbit, Gemini CLI](https://www.youtube.com/watch?v=wlpBCazAY9Q) — score 0.26
   Teaches C5 Interaction Modalities: Ghost Text, Chat, and Inline Edits (10:13–12:42, partly) [checked on the transcript] · freeCodeCamp.org · tier 2 · 1:25:26 · 296,296 views
   *Review:* Shows ghost text completions clearly but lacks comparison with chat/refactoring and cognitive load discussion. Use: in-class clip.

**Readings**

1. [AddyOsmani.com - My LLM coding workflow going into 2026](https://addyosmani.com/blog/ai-coding-workflow/) — score 0.75
   Covers: topic ✓, W01.L1.C1 ✓, W01.L1.C2 ✓, W01.L1.C3 ✓, W01.L1.C4 ✓, W01.L1.C5 ✗, W01.L1.C6 ✓, W01.L1.C7 ✓, W01.L1.C8 ✓ [from page text] · addyosmani.com · tier 4
   *Review:* Expert practitioner's AI coding workflow emphasizing verification and engineering discipline, great real-world context. Use: in-class clip.
2. [What is Agentic Coding? | IBM](https://www.ibm.com/think/topics/agentic-coding) — score 0.73
   Covers: topic ✓, W01.L1.C1 ✓, W01.L1.C2 ✓, W01.L1.C3 ✓, W01.L1.C4 ✓, W01.L1.C5 ✓, W01.L1.C6 ✓, W01.L1.C7 ✓, W01.L1.C8 ✓ [from page text] · ibm.com · tier 4
   *Review:* Clear explanation of agentic coding and practical applications, good for advanced workflow discussion. Use: in-class clip.

**Possible guest speakers** (guest kit: `guest_kits/W01.L1.md`)

1. **Pankaj Jalote** — IIIT-D faculty, IIIT-Delhi (IN) · score 0.85 · fit: strong
   Teaches AI in SE course at IIIT-D; recent papers on LLMs for requirements and test case design.
   Evidence: [Teaches CSE701 Topics in Software Engineering: AI in SE at IIIT-D](https://techtree.iiitd.edu.in/viewDescription/filename?=CSE701) (2026) · [Teaches CSE583 Software Development using Open Source at IIIT-D](https://techtree.iiitd.edu.in/viewDescription/filename?=CSE583) (2026)
   [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Pankaj+Jalote+IIIT+Delhi) · [openalex](https://openalex.org/A5057154526) · [orcid](https://orcid.org/0009-0001-8552-8394)
2. **Michael Sitarzewski** — open-source maintainer, — · score 0.73 · fit: strong
   Open-source framework for AI-assisted software development patterns shows practical workflow focus.
   Evidence: [msitarzewski/AGENT-ZERO (288 stars): Operational framework and pattern](https://github.com/msitarzewski/AGENT-ZERO) (2026)
   [github](https://github.com/msitarzewski) · [website](https://msitarzewski.com)
   ⚠ no academic publications, only repo
3. **Valerie Chen** — researcher, Carnegie Mellon University (US) · score 0.69 · fit: strong
   Two 2026 papers directly on AI automation transforming developer workflows and paired programming with agents.
   Evidence: [Code with Me or for Me? How Increasing AI Automation Transforms Develo](https://doi.org/10.1145/3772318.3790850) (2026) · [(Im)Paired Programming: Coding Agents Improve Productivity but Harm Un](https://doi.org/10.48550/arxiv.2607.26375) (2026)
   [openalex](https://openalex.org/A5088847857) · [orcid](https://orcid.org/0009-0007-2783-0265) · [scholar](https://scholar.google.com/citations?user=94yn2j0AAAAJ)
4. **Matt Pocock** — Developer and instructor, Matt Pocock · score 0.68 · fit: moderate
   YouTube walkthrough on AI coding workflow demonstrates practical industry experience.
   Evidence: [Full Walkthrough: Workflow for AI Coding — Matt Pocock - YouTube](https://www.youtube.com/watch?v=-QFHIoCo-Ko)
   [page](https://www.youtube.com/watch?v=-QFHIoCo-Ko)
   ⚠ only one talk, no academic publications
5. **Qais Hweidi** — open-source maintainer, — · score 0.57 · fit: moderate
   Practical guide repository for AI-assisted development tips.
   Evidence: [Qais-Hweidi/ai-assisted-development-guide (299 stars): Practical tips ](https://github.com/Qais-Hweidi/ai-assisted-development-guide) (2026)
   [github](https://github.com/Qais-Hweidi) · [website](https://QaisHweidi.com)
   ⚠ only a guide, not research

<sub>26 candidates found · 5 passed the checks · 21 removed</sub>

## W01.L2 · Week 1 · Model context protocols and architecture ★ new at IIIT-D
*A 1-hour lecture in week 1 on “Model context protocols and architecture”, part of the module “AI-Assisted Coding and Developer Workflows”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Identify the configuration schema and protocol requirements for model context protocols in a supplied developer workspace template (remember). This serves CO1: Configure AI-assisted coding agents and tool integrations using model context protocols, for a given development environment, such that … Students come in knowing Developer workflows and AI-assisted coding; CSE201 (Unit testing using JUnit, version controlling and collaboration). It prepares for Coding agents and context engineering (week 2). The topic continues in the next lecture. Assessed in Quiz1 (week 3), Midsem (week 7), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:43). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Motivation and Core Architecture of Model Context Protocols** — Explain why standardized context protocols are required to decouple LLM clients from disparate external tools and data sources. Students will understand the cli | 15 | [How Model Context Protocol (MCP) actually wor](https://www.youtube.com/watch?v=cGuyrANVi4A&t=0s) 0:00–3:07 (partly) + [MCP vs API: Simplifying AI Agent Integration ](https://www.youtube.com/watch?v=7j1t3UZA1TY&t=0s) 0:00–2:47 (partly) + NotebookLM for: M×N integration problem |
| C2 | **JSON-RPC Message Framing and Transport Layer Mechanisms** — Examine the transport mechanisms used to exchange messages between hosts and context servers, focusing on standard input/output (stdio) and Server-Sent Events ( | 15 | NotebookLM video (`notebooklm/W01.L2.md`) |
| C3 | **Protocol Initialization Handshake and Capability Negotiation** — Trace the step-by-step lifecycle of protocol initialization, including the client 'initialize' request, server response, and initialized notification. Students  | 15 | NotebookLM video (`notebooklm/W01.L2.md`) |
| C4 | **Comparing Local stdio and Remote SSE Deployment Architectures** — Compare the operational and architectural trade-offs between local stdio subprocesses and remote SSE network services. Students will evaluate factors such as lo | 15 | NotebookLM video (`notebooklm/W01.L2.md`) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W01.L2.md`

**Videos**

1. [How Model Context Protocol (MCP) actually works](https://www.youtube.com/watch?v=cGuyrANVi4A) — score 0.32
   Teaches C1 Motivation and Core Architecture of Model Context Protocols (0:00–3:07, partly) [checked on the transcript] · Google Cloud Tech · tier 2 · 7:58 · 415,672 views
   *Review:* Explains motivation well; lacks host layer and M×N discussion. Use: in-class clip.
2. [MCP vs API: Simplifying AI Agent Integration with External Data](https://www.youtube.com/watch?v=7j1t3UZA1TY) — score 0.29
   Teaches C1 Motivation and Core Architecture of Model Context Protocols (0:00–2:47, partly) [checked on the transcript] · IBM Technology · tier 2 · 13:11 · 1,274,687 views
   *Review:* Clear USB-C analogy for topology; mentions APIs but doesn't detail M×N bottleneck. Use: in-class clip.

**Readings**

1. [Overview - Model Context Protocol](https://modelcontextprotocol.io/specification/2025-11-25/basic) — score 0.75
   Covers: topic ✓, W01.L2.C1 ✓, W01.L2.C2 ✓, W01.L2.C3 ✓, W01.L2.C4 ✗ [from page text] · modelcontextprotocol.io · tier 3
   *Review:* Solid official specification overview covering JSON-RPC messaging, capability negotiation, and transports. Good for core protocol architecture, though excerpts lack concrete configuration examples. Use: before class.
2. [Model Context Protocol (MCP): Specification, Security & Enterprise (2026)](https://aibuzz.blog/model-context-protocol-explained/) — score 0.71
   Covers: topic ✓, W01.L2.C1 ✓, W01.L2.C2 ✓, W01.L2.C3 ✓, W01.L2.C4 ✓ [from page text] · aibuzz.blog · tier 4
   *Review:* Comprehensive 2026 guide to MCP specification, security, and enterprise deployment. Good for protocol overview but not tailored to course's workspace template; lacks hands-on configuration exercises. Use: before class.

**Practice**

1. [GitHub - microsoft/mcp-for-beginners: This open-source curriculum introduces the fundamentals of Model Context Protocol (MCP) through real-world, cross-language examples in .NET, Java, TypeScript, JavaScript, Rust and Python. Designed for developers, it focuses on practical techniques for building modular, scalable, and secure AI workflows from session setup to service orchestration. · GitHub](https://github.com/microsoft/mcp-for-beginners) — score 0.61
   Covers: topic ✓, W01.L2.C1 ✓, W01.L2.C2 ✗, W01.L2.C3 ✓, W01.L2.C4 ✓ [from page text] · github.com · tier 3

**Possible guest speakers** (guest kit: `guest_kits/W01.L2.md`)

1. **Shenao Wang** — industry, Ant Group (CN) · score 0.81 · fit: strong
   Authored key survey papers on MCP landscape and security threats (2025, 2026).
   Evidence: [Model Context Protocol (MCP): Landscape, Security Threats, and Future ](https://doi.org/10.1145/3796519) (2026) · [Model Context Protocol (MCP): Landscape, Security Threats, and Future ](https://doi.org/10.48366/r1596650) (2025)
   [openalex](https://openalex.org/A5029601880) · [orcid](https://orcid.org/0000-0003-3818-3343) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Shenao+Wang+Ant+Group+%28China%29)
   ⚠ name may match several people
2. **Xinyi Hou** — Ph.D. student, Huazhong University of Science and Technology (CN) · score 0.79 · fit: strong
   Authored MCP landscape survey and SMCP secure protocol paper (2026).
   Evidence: [Model Context Protocol (MCP): Landscape, Security Threats, and Future ](https://doi.org/10.1145/3796519) (2026) · [SMCP: Secure Model Context Protocol](https://doi.org/10.48550/arxiv.2602.01129) (2026)
   [openalex](https://openalex.org/A5065658217) · [orcid](https://orcid.org/0009-0005-9965-2109) · [scholar](https://scholar.google.com/citations?user=2UG5s9sAAAAJ)
   ⚠ Ph.D. student, limited seniority
3. **Yanjie Zhao** — researcher, Huazhong University of Science and Technology (CN) · score 0.76 · fit: strong
   Authored MCP landscape survey papers (2025, 2026); software engineering background.
   Evidence: [Model Context Protocol (MCP): Landscape, Security Threats, and Future ](https://doi.org/10.1145/3796519) (2026) · [Model Context Protocol (MCP): Landscape, Security Threats, and Future ](https://doi.org/10.48366/r1596650) (2025)
   [openalex](https://openalex.org/A5023970004) · [orcid](https://orcid.org/0000-0001-8793-5367) · [scholar](https://scholar.google.com/citations?user=7GNtSFMAAAAJ)
4. **Maheshkumar Mole** — industry, Motorola (US) · score 0.71 · fit: strong
   Authored paper on MCP standardizing agentic interoperability (2026).
   Evidence: [The Model Context Protocol (MCP): Standardizing Agentic Interoperabili](https://doi.org/10.52783/jisem.v11i1s.14215) (2026) · [The Model Context Protocol (MCP): Standardizing Agentic Interoperabili](https://doi.org/10.5281/zenodo.18433702) (2026)
   [openalex](https://openalex.org/A5118793771) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Maheshkumar+Mole+Motorola+%28United+States%29)
5. **Partha Pratim Ray** — researcher, Sikkim University (IN) · score 0.60 · fit: moderate
   Authored survey on MCP architecture (2025), though in low-reputation venue.
   Evidence: [A Survey on Model Context Protocol: Architecture, State-of-the-art, Ch](https://doi.org/10.36227/techrxiv.174495492.22752319/v1) (2025)
   [openalex](https://openalex.org/A5060873402) · [orcid](https://orcid.org/0000-0003-2306-2792) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Partha+Pratim+Ray+Sikkim+University)
   ⚠ evidence from low-reputation venue (venue_quality 0.4); relevant papers appear in little-known or low-reputation venues; check before inviting

<sub>34 candidates found · 6 passed the checks · 28 removed</sub>

## W02.L1 · Week 2 · Model context protocols and architecture ★ new at IIIT-D
*A 2-hour lecture in week 2 on “Model context protocols and architecture”, part of the module “AI-Assisted Coding and Developer Workflows”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Identify the configuration schema and protocol requirements for model context protocols in a supplied developer workspace template (remember). This serves CO1: Configure AI-assisted coding agents and tool integrations using model context protocols, for a given development environment, such that … Students come in knowing Developer workflows and AI-assisted coding; CSE201 (Unit testing using JUnit, version controlling and collaboration). It prepares for Coding agents and context engineering (week 2). The topic continues in the next lecture. Assessed in Quiz1 (week 3), Midsem (week 7), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:43). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Recap of Protocol Lifecycles and Core Primitives** — Summarize the JSON-RPC initialization handshake and introduce the three core MCP primitives: resources, prompts, and tools. Students will distinguish between pa | 15 | [How Model Context Protocol (MCP) actually wor](https://www.youtube.com/watch?v=cGuyrANVi4A&t=225s) 3:45–4:53 (partly) + [MCP vs API: Simplifying AI Agent Integration ](https://www.youtube.com/watch?v=7j1t3UZA1TY&t=224s) 3:44–5:28 (partly) + NotebookLM for: JSON-RPC initialization handshake |
| C2 | **Defining Resources and Resource Templates in Context Schemas** — Explain how context servers expose data via URI schemes and parameterized resource templates. Students will identify the schema fields used to define static tex | 20 | NotebookLM video (`notebooklm/W02.L1.md`) |
| C3 | **Tool Definitions and Dynamic Execution Callbacks** — Examine how servers declare executable tools using JSON Schema for input argument validation. Students will follow the flow from tool discovery (`tools/list`) t | 20 | [Model Context Protocol Clearly Explained | MC](https://www.youtube.com/watch?v=tzrwxLNHtRY&t=566s) 9:26–14:08 (partly) + NotebookLM for: tools/call invocation flow; structured execution results (callToolResult); error handling |
| C4 | **Developer Workspace Configuration Schemas and Server Registration** — Break down the structure of workspace configuration files, such as `mcpServers` sections in desktop or IDE configuration files. Students will identify mandatory | 20 | NotebookLM video (`notebooklm/W02.L1.md`) |
| C5 | **Security Boundaries, Environment Isolation, and Access Control** — Analyze security risks associated with granting language models access to local files and CLI execution via context protocols. Students will identify mitigation | 15 | NotebookLM video (`notebooklm/W02.L1.md`) |
| C6 | **Inspecting Configuration Templates for Model Context Protocols** — Walk through a supplied developer workspace template to identify configured context servers, missing schema fields, and transport definitions. Students will pin | 20 | NotebookLM video (`notebooklm/W02.L1.md`) |
| C7 | **Diagnosing Protocol Connection Failures and Logging Workflows** — Demonstrate how to detect and trace common protocol runtime errors using client diagnostic logs and server error codes. Students will evaluate stderr streams, m | 10 | NotebookLM video (`notebooklm/W02.L1.md`) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W02.L1.md`

**Videos**

1. [Model Context Protocol Clearly Explained | MCP Beyond the Hype](https://www.youtube.com/watch?v=tzrwxLNHtRY) — score 0.32
   Teaches C3 Tool Definitions and Dynamic Execution Callbacks (9:26–14:08, partly) [checked on the transcript] · codebasics · tier 2 · 15:04 · 636,856 views
   *Review:* Shows tool definition with input schema and list tools; omits call protocol details. Use: in-class clip.
2. [MCP vs API: Simplifying AI Agent Integration with External Data](https://www.youtube.com/watch?v=7j1t3UZA1TY) — score 0.25
   Teaches C1 Recap of Protocol Lifecycles and Core Primitives (3:44–5:28, partly) [checked on the transcript] · IBM Technology · tier 2 · 13:11 · 1,274,687 views
   *Review:* Clear primitives overview with discovery mechanism; no handshake coverage. Use: in-class clip.
3. [How Model Context Protocol (MCP) actually works](https://www.youtube.com/watch?v=cGuyrANVi4A) — score 0.26
   Teaches C1 Recap of Protocol Lifecycles and Core Primitives (3:45–4:53, partly) [checked on the transcript] · Google Cloud Tech · tier 2 · 7:58 · 415,672 views
   *Review:* Clear explanation of primitives and client-server model; omits JSON-RPC handshake details. Use: in-class clip.

**Readings**

1. [Architecture overview - Model Context Protocol](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture) — score 0.74
   Covers: topic ✓, W02.L1.C1 ✓, W02.L1.C2 ✓, W02.L1.C3 ✓, W02.L1.C4 ✓, W02.L1.C5 ✗, W02.L1.C6 ✓, W02.L1.C7 ✓ [from page text] · modelcontextprotocol.io · tier 3
   *Review:* Official documentation covering MCP architecture, JSON-RPC primitives, and discovery lifecycle. Excellent authoritative reading for understanding protocol concepts before configuring workspaces. Use: before class.
2. [A Complete Guide to the Model Context Protocol | Bolder Apps Blog](https://www.bolderapps.com/blog-posts/model-context-protocol) — score 0.72
   Covers: topic ✓, W02.L1.C1 ✓, W02.L1.C2 ✓, W02.L1.C3 ✓, W02.L1.C4 ✓, W02.L1.C5 ✓, W02.L1.C6 ✓, W02.L1.C7 ✓ [from page text] · bolderapps.com · tier 4
   *Review:* Clear, accessible breakdown of core MCP primitives (tools, resources, prompts) and their JSON schemas. Great overview for students learning protocol requirements. Use: after class.

**Possible guest speakers:** same topic as W01.L2; see its list and guest kit.

<sub>37 candidates found · 6 passed the checks · 31 removed</sub>

## W02.L2 · Week 2 · Coding agents and context engineering ★ new at IIIT-D
*A 1-hour lecture in week 2 on “Coding agents and context engineering”, part of the module “Agent Workspaces and Tool Integrations”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Configure custom tool integrations within agent workspaces using model context protocols, with all public tests passing and no warnings from the configured static analyser (apply). This serves CO1: Configure AI-assisted coding agents and tool integrations using model context protocols, for a given development environment, such that … Students come in knowing Model context protocols and architecture; CSE201 (Unit testing using JUnit, version controlling and collaboration). It prepares for Custom tool integrations using model context protocols (week 3). It has a hands-on part (Custom tool integration lab in week 3; Hands‑on reinforcement lab in week 4). The topic continues in the next lecture. Assessed in Quiz1 (week 3), Assign1 (week 6), Midsem (week 7), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:43). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Anatomy of coding agent workspaces and execution lifecycle** — Students will understand the core architectural layers of an autonomous coding agent workspace, including environment virtualization, state tracking, and scratc | 15 | [Context Engineering & Coding Agents with Curs](https://www.youtube.com/watch?v=3KAI__5dUn0&t=609s) 10:09–15:35 (partly) + [Agentic Engineering: 5 Terms Every AI Develop](https://www.youtube.com/watch?v=SIZsFGvtClM&t=331s) 5:31–10:39 (partly) + NotebookLM for: formal execution lifecycle walkthrough from prompt ingestion to tool dispatch; architectural scratchpad management; scratchpad management |
| C2 | **Context engineering strategies for constrained context windows** — Students will learn context engineering mechanisms such as selective file tree pruning, sliding context windows, and dynamic relevance filtering. They will eval | 15 | [Advanced Context Engineering for Agents](https://www.youtube.com/watch?v=IS_y40zY-hc&t=223s) 3:43–8:08 (partly) + [Context Engineering & Coding Agents with Curs](https://www.youtube.com/watch?v=3KAI__5dUn0&t=321s) 5:21–7:50 (partly) + NotebookLM for: selective file tree pruning; sliding context windows; dynamic relevance filtering (explicit) |
| C3 | **Structuring MCP tool schemas and workspace descriptors** — Students will learn how to structure tool definitions using Model Context Protocol (MCP) JSON schemas so agents can discover and invoke workspace tools cleanly. | 15 | NotebookLM video (`notebooklm/W02.L2.md`) |
| C4 | **Evaluating context pollution and tool discovery trade-offs** — Students will analyse the failure modes caused by context pollution when exposing too many MCP tools or verbose tool definitions to a coding agent. They will co | 15 | NotebookLM video (`notebooklm/W02.L2.md`) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W02.L2.md`

**Videos**

1. [Context Engineering & Coding Agents with Cursor](https://www.youtube.com/watch?v=3KAI__5dUn0) — score 0.40
   Teaches C2 Context engineering strategies for constrained context windo (5:21–7:50, partly); C1 Anatomy of coding agent workspaces and execution lifecycle (10:09–15:35, partly) [checked on the transcript] · OpenAI · tier 3 · 18:43 · 43,315 views
   *Review:* Explains semantic search and token budget trade-offs; misses file pruning and sliding windows.; Great industry insight into Cursor's workspace isolation and tooling, but lacks a formal step-by-step execution lifecycle trace. Use: in-class clip.
2. [Agentic Engineering: 5 Terms Every AI Developer Should Know](https://www.youtube.com/watch?v=SIZsFGvtClM) — score 0.37
   Teaches C1 Anatomy of coding agent workspaces and execution lifecycle (5:31–10:39, partly) [checked on the transcript] · IBM Technology · tier 2 · 11:41 · 67,222 views
   *Review:* Accessible overview of agent harnesses, execution loops, and sandboxing, though it omits specific scratchpad mechanics. Use: in-class clip.
3. [Advanced Context Engineering for Agents](https://www.youtube.com/watch?v=IS_y40zY-hc) — score 0.39
   Teaches C2 Context engineering strategies for constrained context windo (3:43–8:08, partly) [checked on the transcript] · YC Root Access · tier 4 · 14:38 · 216,859 views
   *Review:* Practical compaction and sub-agent strategies; assumes familiarity with agent loops. Use: in-class clip.

**Readings**

1. [Context Engineering for Coding Agents](https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html) — score 0.74
   Covers: topic ✓, W02.L2.C1 ✓, W02.L2.C2 ✓, W02.L2.C3 ✓, W02.L2.C4 ✓ [from page text] · martinfowler.com · tier 2
   *Review:* Good conceptual overview of context engineering for coding agents, but lacks hands-on MCP configuration guidance. Use: before class.
   ⚠ AI review: mentions the topic but does not really teach it
2. [Effective context engineering for AI agents \ Anthropic](https://www.anthropic.com/research/effective-context-engineering-for-ai-agents) — score 0.69
   Covers: topic ✓, W02.L2.C1 ✓, W02.L2.C2 ✓, W02.L2.C3 ✓, W02.L2.C4 ✓ [from page text] · anthropic.com · tier 3
   *Review:* Authoritative overview of context engineering principles, but not a tutorial on MCP tool integration. Use: before class.
   ⚠ AI review: mentions the topic but does not really teach it

**Possible guest speakers** (guest kit: `guest_kits/W02.L2.md`)

1. **Di Wang** — open-source maintainer, Tsinghua University · score 0.82 · fit: strong
   Maintains the popular repository How Claude Code Works, providing an in-depth exploration of coding agent loops, architecture, and context engineering.
   Evidence: [Windy3f3f3f3f/how-claude-code-works (3,800 stars): Deep dive into Clau](https://github.com/Windy3f3f3f3f/how-claude-code-works) (2026)
   [github](https://github.com/Windy3f3f3f3f)
2. **Han Li** — Postdoc, Queen's University (CA) · score 0.76 · fit: strong
   Has dedicated research interests in AI Agents and Model Context Protocol, and co-authored ContextBench evaluating context retrieval specifically for coding agents.
   Evidence: [ContextBench: A Benchmark for Context Retrieval in Coding Agents](https://doi.org/10.48550/arxiv.2602.05892) (2026)
   [openalex](https://openalex.org/A5125198720) · [scholar](https://scholar.google.com/citations?user=3xI3QLsAAAAJ)
3. **Matthias Galster** — researcher, University of Bergamo (IT) · score 0.69 · fit: strong
   Co-authored Context Engineering for AI Agents in Open-Source Software, directly addressing context engineering methodologies for software development agents.
   Evidence: [Context Engineering for AI Agents in Open-Source Software](https://doi.org/10.1145/3793302.3793350) (2026)
   [openalex](https://openalex.org/A5034571717) · [orcid](https://orcid.org/0000-0003-3491-1833) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Matthias+Galster+University+of+Bergamo) · [semantic scholar](https://www.semanticscholar.org/author/2387790888)
4. **Bapi Chatterjee** — IIIT-D faculty, IIIT-Delhi (IN) · score 0.61 · fit: moderate
   Teaches a graduate course on Agentic Reasoning, covering relevant principles of agent architectures and workflows.
   Evidence: [Teaches CSE594A Agentic Reasoning at IIIT-D](https://techtree.iiitd.edu.in/viewDescription/filename?=CSE594A) (2026)
   [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Bapi+Chatterjee+IIIT+Delhi) · [openalex](https://openalex.org/A5043227337) · [orcid](https://orcid.org/0000-0002-2742-4028)
   ⚠ course covers general agentic reasoning rather than coding agents or context engineering
5. **Karthik Vaidhyanathan** — Assistant Professor, IIIT Hyderabad (IN) · score 0.56 · fit: moderate
   Researches agentic AI and context strategies in software engineering, co-authoring papers on agent research agendas and context strategies for LLM-driven architectural decisions.
   Evidence: [A Research Agenda on Agents and Software Engineering: Outcomes from th](https://doi.org/10.48550/arxiv.2605.11720) (2026) · [Context Matters: Evaluating Context Strategies for Automated ADR Gener](https://doi.org/10.48550/arxiv.2604.03826) (2026)
   [openalex](https://openalex.org/A5081488877) · [orcid](https://orcid.org/0000-0003-2317-6175) · [scholar](https://scholar.google.com/citations?user=qtITyHkAAAAJ)
6. **Mukul Pratap Singh** — industry, Microsoft (US) · score 0.49 · fit: moderate
   Co-authored research on agentic context strategies and determining when language models should invoke tools within workspaces.
   Evidence: [Agentic Context Strategies for Multi-Format Document Understanding: Wh](https://doi.org/10.18653/v1/2026.acl-industry.133) (2026) · [Agentic Context Strategies for Multi-Format Document Understanding: Wh](https://doi.org/10.48448/p47s-sr28) (2026)
   [openalex](https://openalex.org/A5101442631) · [orcid](https://orcid.org/0000-0001-9510-4512) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Mukul+Pratap+Singh+Microsoft+%28United+States%29)
   ⚠ context strategies are evaluated on document understanding rather than software coding

<sub>29 candidates found · 7 passed the checks · 22 removed</sub>

## W03.L1 · Week 3 · Coding agents and context engineering ★ new at IIIT-D
*A 1-hour lecture in week 3 on “Coding agents and context engineering”, part of the module “Agent Workspaces and Tool Integrations”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Configure custom tool integrations within agent workspaces using model context protocols, with all public tests passing and no warnings from the configured static analyser (apply). This serves CO1: Configure AI-assisted coding agents and tool integrations using model context protocols, for a given development environment, such that … Students come in knowing Model context protocols and architecture; CSE201 (Unit testing using JUnit, version controlling and collaboration). It prepares for Custom tool integrations using model context protocols (week 3). It has a hands-on part (Custom tool integration lab in week 3; Hands‑on reinforcement lab in week 4). The topic continues in the next lecture. Assessed in Quiz1 (week 3), Assign1 (week 6), Midsem (week 7), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:43). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Static analysis constraints on agent tool configurations** — Students will identify common static analyser warnings and strict schema violations that arise when registering MCP server endpoints. They will review rule sets | 10 | NotebookLM video (`notebooklm/W03.L1.md`) |
| C2 | **Configuring custom MCP tool manifests and execution environments** — Students will write and configure MCP server manifest files to expose custom tools (such as git, linters, or test runners) directly inside an agent workspace. T | 20 | NotebookLM video (`notebooklm/W03.L1.md`) |
| C3 | **Validating workspace tool configurations against test suites** — Students will walk through setting up and running public integration test suites and static analysis tools against an MCP-integrated agent workspace. They will  | 20 | NotebookLM video (`notebooklm/W03.L1.md`) |
| C4 | **Diagnosing runtime tool configuration failures in agent workflows** — Students will examine real-world case studies where subtle tool configuration errors—such as malformed error responses or improper argument defaults—caused an a | 10 | NotebookLM video (`notebooklm/W03.L1.md`) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W03.L1.md`

**Readings**

1. [Building AI Coding Agents for the Terminal:Scaffolding, Harness, Context Engineering, and Lessons Learned](https://arxiv.org/html/2603.05344v1) — score 0.78
   Covers: topic ✓, W03.L1.C1 ✓, W03.L1.C2 ✓, W03.L1.C3 ✓, W03.L1.C4 ✓ [from page text] · arxiv.org · tier 2
   *Review:* Solid technical paper on terminal coding agent architecture and context assembly pipelines. Excellent conceptual background for context engineering design, though lacks specific MCP manifest syntax. Use: before class.
2. [What Is AI Context Engineering? Giving Coding Agents the Right Context](https://blog.codacy.com/ai-context-engineering) — score 0.66
   Covers: topic ✓, W03.L1.C1 ✓, W03.L1.C2 ✓, W03.L1.C3 ✓, W03.L1.C4 ✓ [from page text] · blog.codacy.com · tier 4
   *Review:* Clear article introducing context engineering for coding agents, contrasting context curation with raw window size. Great intuitive primer for pre-class reading, though light on technical protocol details. Use: before class.

**Practice**

1. [charlax/professional-programming — A collection of learning resources for curious software engineers](https://github.com/charlax/professional-programming) — score 0.61
   Covers: topic ✓, W03.L1.C1 ✗, W03.L1.C2 ✗, W03.L1.C3 ✗, W03.L1.C4 ✗ [from page text] · GitHub · tier 3

**Possible guest speakers:** same topic as W02.L2; see its list and guest kit.

<sub>27 candidates found · 3 passed the checks · 24 removed</sub>

## W03.L2 · Week 3 · Custom tool integrations using model context protocols ★ new at IIIT-D
*A 2-hour lecture in week 3 on “Custom tool integrations using model context protocols”, part of the module “Agent Workspaces and Tool Integrations”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Configure custom tool integrations within agent workspaces using model context protocols, with all public tests passing and no warnings from the configured static analyser (apply). This serves CO1: Configure AI-assisted coding agents and tool integrations using model context protocols, for a given development environment, such that … Students come in knowing Coding agents and context engineering; CSE201 (Unit testing using JUnit, version controlling and collaboration). It has a hands-on part (Custom tool integration lab in week 3; Hands‑on reinforcement lab in week 4). The topic continues in the next lecture. Assessed in Assign1 (week 6), Midsem (week 7), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Architecture of Model Context Protocol (MCP) clients and servers** — Students will understand the client-server architecture of the Model Context Protocol (MCP) and how LLM agent workspaces communicate with external tools. They w | 15 | [How Model Context Protocol (MCP) actually wor](https://www.youtube.com/watch?v=cGuyrANVi4A&t=129s) 2:09–6:36 (partly) + NotebookLM for: Role of Host Application vs MCP Client; Transport layer mechanisms (Stdio/SSE); Session initialization process |
| C2 | **JSON-RPC 2.0 protocol format for tool discovery and calls** — Students will learn how JSON-RPC 2.0 messages are structured for tools/list and tools/call requests in MCP. They will examine request IDs, method headers, param | 15 | [Model Context Protocol (MCP) Explained | The ](https://www.youtube.com/watch?v=jwquMzKkxo4&t=409s) 6:49–9:19 (partly) + NotebookLM for: Detailed JSON-RPC 2.0 message structure; Request IDs and method headers; Parameter payloads and response objects |
| C3 | **Defining strict input JSON schemas for MCP tools** — Students will learn how to write precise JSON Schema definitions for tool parameters to guide LLM tool calling. They will specify required fields, parameter dat | 15 | [Model Context Protocol Clearly Explained | MC](https://www.youtube.com/watch?v=tzrwxLNHtRY&t=619s) 10:19–12:17 (partly) + NotebookLM for: Step-by-step writing of JSON Schema definitions; Validation constraint rules; Data type specification details |
| C4 | **Implementing an MCP server using an official SDK** — Students will walk through building a lightweight MCP server using an official SDK. They will observe how decorated functions are exposed as callable tools and  | 20 | NotebookLM video (`notebooklm/W03.L2.md`) |
| C5 | **Activity: Writing and running a custom MCP server tool** — Students will write a custom tool function on an MCP server that executes local file or system operations and returns formatted content blocks. They will test t | 25 | in class (activity) |
| C6 | **Configuring workspace settings to discover custom MCP servers** — Students will configure an agent workspace JSON configuration file to register their custom server executable and command-line arguments. They will verify that  | 15 | [Model Context Protocol (MCP) Explained | The ](https://www.youtube.com/watch?v=jwquMzKkxo4&t=670s) 11:10–13:43 (partly) + NotebookLM for: writing the JSON configuration syntax; setting executable path and command-line arguments |
| C7 | **Handling execution errors and returning structured MCP errors** — Students will learn how to catch internal tool execution failures and map them to structured MCP error responses using the isError flag. They will distinguish b | 15 | [MCP (Model Context Protocol)Error Handling - ](https://www.youtube.com/watch?v=b9daqQNSLSU&t=84s) 1:24–2:46 (partly) + NotebookLM for: Complete code example/demo; Catching execution exceptions; CallToolResult structure |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W03.L2.md`

**Videos**

1. [Model Context Protocol (MCP) Explained | The Standard Connecting AI to Your Tools](https://www.youtube.com/watch?v=jwquMzKkxo4) — score 0.21
   Teaches C2 JSON-RPC 2.0 protocol format for tool discovery and calls (6:49–9:19, partly); C6 Configuring workspace settings to discover custom MCP server (11:10–13:43, partly) [checked on the transcript] · Ahmed Al-Imaad · tier 4 · 14:18 · 57 views
   *Review:* Mentions JSON-RPC 2.0 and list/call methods conceptually, but lacks message payloads and structural details.; Shows host UI settings and demonstrates tool execution verification, but does not show how to edit the underlying JSON file. Use: in-class clip.
2. [How Model Context Protocol (MCP) actually works](https://www.youtube.com/watch?v=cGuyrANVi4A) — score 0.39
   Teaches C1 Architecture of Model Context Protocol (MCP) clients and ser (2:09–6:36, partly) [checked on the transcript] · Google Cloud Tech · tier 2 · 7:58 · 415,672 views
   *Review:* Clear conceptual explanation of client-server architecture and tool exposure, but misses transport layer and host app details. Use: in-class clip.
3. [Model Context Protocol Clearly Explained | MCP Beyond the Hype](https://www.youtube.com/watch?v=tzrwxLNHtRY) — score 0.24
   Teaches C3 Defining strict input JSON schemas for MCP tools (10:19–12:17, partly) [checked on the transcript] · codebasics · tier 2 · 15:04 · 636,856 views
   *Review:* Shows real code examples of tool inputSchema and required properties, but passes over schema writing details quickly. Use: in-class clip.
4. [MCP (Model Context Protocol)Error Handling - model context protocol (mcp) (Ep-014)](https://www.youtube.com/watch?v=b9daqQNSLSU) — score 0.21
   Teaches C7 Handling execution errors and returning structured MCP error (1:24–2:46, partly) [checked on the transcript] · Tech Sharmit · tier 4 · 11:14 · 34 views
   *Review:* Introduces FastMCP's ToolError and the isError flag, but cuts off mid-explanation before demonstrating complete error handling. Use: in-class clip.

**Readings**

1. [Model Context Protocol (MCP) - Docs by LangChain](https://docs.langchain.com/oss/python/langchain/mcp) — score 0.72
   Covers: topic ✓, W03.L2.C1 ✓, W03.L2.C2 ✓, W03.L2.C3 ✓, W03.L2.C4 ✓, W03.L2.C5 ✓, W03.L2.C6 ✓, W03.L2.C7 ✗ [from page text] · docs.langchain.com · tier 3
   *Review:* Clear, technical documentation demonstrating how to connect MCP tools using LangChain code snippets (FastMCP, stdio, HTTP). Excellent practical reference for students implementing tool integrations. Use: after class.
2. [Tools - Model Context Protocol](https://modelcontextprotocol.io/specification/2026-07-28/server/tools) — score 0.62
   Covers: topic ✓, W03.L2.C1 ✓, W03.L2.C2 ✓, W03.L2.C3 ✓, W03.L2.C4 ✓, W03.L2.C5 ✗, W03.L2.C6 ✓, W03.L2.C7 ✓ [from page text] · modelcontextprotocol.io · tier 3

**Possible guest speakers** (guest kit: `guest_kits/W03.L2.md`)

1. **Rishabh Kumar** — Author, Independent · score 0.69 · fit: moderate
   Delivered an engineering talk titled 'Model Context Protocol (MCP): The Complete Engineering Guide — Architecture, Internals, and Real-World Use Cases', which directly addresses MCP architecture and implementation.
   Evidence: [Model Context Protocol (MCP): The Complete Engineering Guide — Archite](https://medium.com/@rishabhkr954/model-context-protocol-mcp-the-complete-engineering-guide-architecture-internals-and-0d7b5d988b08)
   [page](https://medium.com/@rishabhkr954/model-context-protocol-mcp-the-complete-engineering-guide-architecture-internals-and-0d7b5d988b08)
2. **Iwo Szapar** — Author, Production MCP Practitioner, Independent · score 0.63 · fit: moderate
   Gave a practitioner talk titled 'Context Engineering with MCP: Practitioner's Guide', offering direct practical insights on model context protocols.
   Evidence: [Context Engineering with MCP: Practitioner's Guide](https://www.iwoszapar.com/p/context-engineering-mcp)
   [page](https://www.iwoszapar.com/p/context-engineering-mcp)
3. **Parthasarathi Mukhopadhyay** — Professor, Department of Library and Information Science, University of Kalyani (IN) · score 0.58 · fit: moderate
   Published papers on integrating LLMs using Model Context Protocols for digital library systems and command-line conversational search.
   Evidence: [Enhancing Dspace with Large Language Models: Designing an Integration ](https://doi.org/10.5281/zenodo.17698958) (2025) · [Enhancing Dspace with Large Language Models: Designing an Integration ](https://doi.org/10.5281/zenodo.17598559) (2025)
   [openalex](https://openalex.org/A5063466662) · [orcid](https://orcid.org/0000-0003-0717-9413) · [scholar](https://scholar.google.com/citations?user=VOxKJ2sAAAAJ)
4. **Roger P. Wattenhofer** — researcher, ETH Zurich (CH) · score 0.55 · fit: moderate
   Co-authored a paper providing theoretical martingale analysis of information fidelity in tool-using LLM agents under the Model Context Protocol.
   Evidence: [Information Fidelity in Tool-Using LLM Agents: A Martingale Analysis o](https://doi.org/10.65109/gmhb4353) (2026) · [Information Fidelity in Tool-Using LLM Agents: A Martingale Analysis o](https://openalex.org/W7130236760) (2026)
   [openalex](https://openalex.org/A5078339613) · [orcid](https://orcid.org/0000-0002-6339-3134) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Roger+P.+Wattenhofer+ETH+Zurich)
5. **Yew-Soon Ong** — researcher, Agency for Science, Technology and Research (SG) · score 0.51 · fit: moderate
   Co-authored research analyzing information fidelity in tool-using agents using the Model Context Protocol.
   Evidence: [Information Fidelity in Tool-Using LLM Agents: A Martingale Analysis o](https://doi.org/10.65109/gmhb4353) (2026) · [Information Fidelity in Tool-Using LLM Agents: A Martingale Analysis o](https://openalex.org/W7130236760) (2026)
   [openalex](https://openalex.org/A5068243197) · [orcid](https://orcid.org/0000-0002-4480-169X) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Yew-Soon+Ong+Agency+for+Science%2C+Technology+and+Research)

<sub>32 candidates found · 5 passed the checks · 27 removed</sub>

## W04.L1 · Week 4 · Custom tool integrations using model context protocols ★ new at IIIT-D
*A 0.5-hour lecture in week 4 on “Custom tool integrations using model context protocols”, part of the module “Agent Workspaces and Tool Integrations”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Configure custom tool integrations within agent workspaces using model context protocols, with all public tests passing and no warnings from the configured static analyser (apply). This serves CO1: Configure AI-assisted coding agents and tool integrations using model context protocols, for a given development environment, such that … Students come in knowing Coding agents and context engineering. It has a hands-on part (Custom tool integration lab in week 3; Hands‑on reinforcement lab in week 4). The topic continues in the next lecture. Assessed in Assign1 (week 6), Midsem (week 7), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Static analysis and linter rules for safe MCP server code** — Students will configure static analysis tools to validate type safety, async patterns, and error handling in custom MCP server implementations. They will identi | 15 | NotebookLM video (`notebooklm/W04.L1.md`) |
| C2 | **Activity: Passing automated MCP tool test suites without warnings** — Students will run integration test suites against their configured MCP tool integration in an agent workspace environment. They will fix failing test cases and  | 15 | in class (activity) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W04.L1.md`

**Readings**

1. [Model Context Protocol Security Project · GitHub](https://github.com/ModelContextProtocol-Security) — score 0.60
   Covers: topic ✓, W04.L1.C1 ✓, W04.L1.C2 ✓ [from page text] · github.com · tier 3
   *Review:* A GitHub organization landing page aggregating MCP security repos. Useful as a pointer to tooling, but lacks direct instructional guidance for students configuring tools. Use: your preparation.
   ⚠ AI review: mentions the topic but does not really teach it

**Possible guest speakers:** same topic as W03.L2; see its list and guest kit.

<sub>27 candidates found · 1 passed the checks · 26 removed</sub>

## W04.L2 · Week 4 · Standards and specification guidelines for use cases
*A 2-hour lecture in week 4 on “Standards and specification guidelines for use cases”, part of the module “Requirements and Specification-Driven Development”. A related topic (“standards and specification”) is already taught at IIIT-D. By the end, students should be able to: Outline use cases and system boundaries from unstructured product descriptions using standards and specification guidelines for most short items (understand). This serves CO2: Translate unstructured product requirements into executable specifications, using spec-driven development frameworks, covering every use case in the supplied … It prepares for Software requirements and requirements engineering (week 4). Assessed in Assign2 (week 8), Midsem (week 7), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **The Need for Standardized Use Case Specifications** — Students will understand why unstructured product descriptions lead to scope creep and misinterpretation in software projects. They will identify standard use c | 10 | [Business Analysis Training: What is System Co](https://www.youtube.com/watch?v=ejfAB0eUfoc&t=23s) 0:23–3:53 (partly) + [Defining the Boundary  The Architecture of UM](https://www.youtube.com/watch?v=4bRrCYWN6g8&t=138s) 2:18–5:24 (partly) + NotebookLM for: why unstructured product descriptions cause scope creep and misinterpretation; standard use case specification components; ISO/IEC/IEEE 29148 |
| C2 | **Defining System Boundaries and Primary vs. Secondary Actors** — Students will learn how to construct clear system boundaries that separate internal automated behaviors from external user actions. They will classify primary a | 15 | [Defining the Boundary  The Architecture of UM](https://www.youtube.com/watch?v=4bRrCYWN6g8&t=166s) 2:46–7:05 (fully) + NotebookLM |
| C3 | **Standard Templates for Brief and Fully Dressed Use Cases** — Students will compare standard use case templates, including Cockburn's casual and fully dressed formats. They will learn the mandatory fields required to docum | 15 | NotebookLM video (`notebooklm/W04.L2.md`) |
| C4 | **Extracting Use Cases from Unstructured Narrative Text** — Students will apply a step-by-step heuristic to extract actor-goal pairs from informal user feedback and feature requests. They will learn how to filter out UI  | 20 | NotebookLM video (`notebooklm/W04.L2.md`) |
| C5 | **Formulating Main Success Scenarios with Strict Writing Guidelines** — Students will learn standard grammatical rules for writing Main Success Scenario steps, such as using subject-verb-object structure, active voice, and explicit  | 15 | NotebookLM video (`notebooklm/W04.L2.md`) |
| C6 | **Worked Example: Converting a Raw Feature Prompt to Use Case Outlines** — Students will watch the step-by-step transformation of a multi-paragraph, messy product description for an e-commerce checkout into formal use case outlines. Th | 20 | NotebookLM video (`notebooklm/W04.L2.md`) |
| C7 | **Specifying Preconditions, Guarantees, and Extension Branches** — Students will learn how to formalize entry preconditions, minimal and success guarantees, and exception handling branches in standard use case documentation. Th | 15 | NotebookLM video (`notebooklm/W04.L2.md`) |
| C8 | **Evaluating Use Case Quality and Completeness Checklist** — Students will analyze sample use case outlines against a standard quality checklist to detect boundary leaks, missing actors, and untestable steps. They will di | 10 | in class (discussion) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W04.L2.md`

**Videos**

1. [Defining the Boundary  The Architecture of UML Use Cases](https://www.youtube.com/watch?v=4bRrCYWN6g8) — score 0.42
   Teaches C1 The Need for Standardized Use Case Specifications (2:18–5:24, partly); C2 Defining System Boundaries and Primary vs. Secondary Actors (2:46–7:05, fully) [checked on the transcript] · Object-oriented with Java · tier 4 · 8:00 · 58 views
   *Review:* Useful UML boundary and actor introduction, but not a complete use case specification.; Clear, structured UML walkthrough with concrete boundary and actor examples. Use: in-class clip.
2. [Business Analysis Training: What is System Context and System Boundary in Requirements Engineering](https://www.youtube.com/watch?v=ejfAB0eUfoc) — score 0.32
   Teaches C1 The Need for Standardized Use Case Specifications (0:23–3:53, partly) [checked on the transcript] · Business Analysis Excellence | Esta Lessing CBAP® · tier 4 · 5:52 · 11,639 views
   *Review:* Practical boundary-definition lesson; lacks use case specification structure and standard reference. Use: in-class clip.

<sub>19 candidates found · 0 passed the checks · 19 removed</sub>

## W04.L3 · Week 4 · Software requirements and requirements engineering
*A 0.5-hour lecture in week 4 on “Software requirements and requirements engineering”, part of the module “Requirements and Specification-Driven Development”. A related topic (“software requirements and requirements engineering”) is already taught at IIIT-D. By the end, students should be able to: Outline use cases and system boundaries from unstructured product descriptions using spec-driven development guidelines (understand). This serves CO2: Translate unstructured product requirements into executable specifications, using spec-driven development frameworks, covering every use case in the supplied … Students come in knowing Standards and specification guidelines for use cases. It prepares for Spec-driven development frameworks (week 5). The topic continues in the next lecture. Assessed in Assign2 (week 8), Midsem (week 7), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Recap use case standards and spec guidelines** — Students review the IEEE 830 and UML use case standards, and the spec-driven development guidelines for structuring requirements. They identify the mandatory el | 15 | [What is Spec Driven Development. Intro to AI ](https://www.youtube.com/watch?v=0atkW_janVg&t=197s) 3:17–6:49 (partly) + NotebookLM for: IEEE 830; UML use case standards; mandatory elements of a use case specification |
| C2 | **Identify actors and system boundaries** — Students learn a step‑by‑step method to extract actors, primary and secondary, and to draw the system boundary from a raw product description. They practice dis | 15 | [Use Case Diagram Tutorial and EXAMPLE ( How t](https://www.youtube.com/watch?v=8V3r5STTmbA&t=69s) 1:09–4:42 (partly) + [UML Use Case Diagram Tutorial in EdrawMax | D](https://www.youtube.com/watch?v=uNtoyXJ1VDc&t=53s) 0:53–4:13 (partly) + NotebookLM for: step-by-step extraction from a raw product description; practice applying the method to a product description; explicit practice distinguishing internal from external actors |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W04.L3.md`

**Videos**

1. [Use Case Diagram Tutorial and EXAMPLE ( How to Draw Use Case Diagram )](https://www.youtube.com/watch?v=8V3r5STTmbA) — score 0.31
   Teaches C2 Identify actors and system boundaries (1:09–4:42, partly) [checked on the transcript] · The Business Analysis Doctor - IIBA Certification · tier 4 · 13:14 · 30,327 views
   *Review:* Clear UML explanation of actors and boundaries; lacks the required product-description extraction exercise. Use: in-class clip.
2. [What is Spec Driven Development. Intro to AI Coding for Real Projects Explained](https://www.youtube.com/watch?v=0atkW_janVg) — score 0.27
   Teaches C1 Recap use case standards and spec guidelines (3:17–6:49, partly) [checked on the transcript] · Codeless Developer · tier 4 · 7:10 · 2,717 views
   *Review:* Useful spec-driven workflow for AI coding, but omits IEEE 830 and use case specification requirements. Use: in-class clip.
3. [UML Use Case Diagram Tutorial in EdrawMax | Definition, Symbols, and Examples](https://www.youtube.com/watch?v=uNtoyXJ1VDc) — score 0.27
   Teaches C2 Identify actors and system boundaries (0:53–4:13, partly) [checked on the transcript] · Wondershare Edraw · tier 4 · 8:55 · 188,901 views
   *Review:* Provides actor-identification questions and boundary drawing, but no raw-description exercise or primary/secondary distinction. Use: in-class clip.

**Readings**

1. [Requirements Engineering: 9 Best Practices with Examples | Perforce Software](https://www.perforce.com/blog/alm/requirements-engineering-examples) — score 0.60
   Covers: topic ✓, W04.L3.C1 ✓, W04.L3.C2 ✗ [from page text] · perforce.com · tier 4
   *Review:* Practical best practices with examples, but lacks use case and boundary analysis. Use: in-class clip.
   ⚠ AI review: mentions the topic but does not really teach it

<sub>15 candidates found · 1 passed the checks · 14 removed</sub>

## W05.L1 · Week 5 · Software requirements and requirements engineering
*A 2.5-hour lecture in week 5 on “Software requirements and requirements engineering”, part of the module “Requirements and Specification-Driven Development”. A related topic (“software requirements and requirements engineering”) is already taught at IIIT-D. By the end, students should be able to: Outline use cases and system boundaries from unstructured product descriptions using spec-driven development guidelines (understand). This serves CO2: Translate unstructured product requirements into executable specifications, using spec-driven development frameworks, covering every use case in the supplied … Students come in knowing Standards and specification guidelines for use cases. It prepares for Spec-driven development frameworks (week 5). The topic continues in the next lecture. Assessed in Assign2 (week 8), Midsem (week 7), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Extract functional requirements from description** — Using a worked example, students parse an unstructured product description to list functional requirements, grouping them by user goal. They apply a template to | 15 | NotebookLM video (`notebooklm/W05.L1.md`) |
| C2 | **Write use case main success scenario** — Students construct the main success scenario for a use case, writing numbered steps that show actor–system interactions. They ensure each step is atomic, observ | 15 | NotebookLM video (`notebooklm/W05.L1.md`) |
| C3 | **Write use case extensions and alternate flows** — Students extend the main scenario with extension points, alternate flows, and exception handling, using the same numbering scheme. They learn to reference exten | 15 | [UML use case diagrams: Everything you need to](https://www.youtube.com/watch?v=4emxjxonNRI&t=553s) 9:13–11:40 (partly) + NotebookLM for: writing textual alternate flows and exception handling; numbering scheme for extensions; traceability |
| C4 | **Create system boundary context diagram** — In a live demo, the instructor builds a UML context diagram showing the system, actors, and external systems. Students see how the diagram validates the actor l | 15 | [Use Case Diagram Tutorial and EXAMPLE ( How t](https://www.youtube.com/watch?v=8V3r5STTmbA&t=69s) 1:09–4:53 (partly) + [UML use case diagrams: Everything you need to](https://www.youtube.com/watch?v=4emxjxonNRI&t=90s) 1:30–3:17 (partly) + NotebookLM for: live context-diagram construction; validation of the actor list and boundary decisions; complete context diagram |
| C5 | **Prioritize use cases with MoSCoW** — Students compare MoSCoW, business value, and risk‑based prioritization techniques on a sample use case set. They decide which use cases belong to Must, Should,  | 15 | [What is MoSCoW Prioritization Method? How MoS](https://www.youtube.com/watch?v=XVx5FKZb6l4&t=0s) 0:00–2:50 (partly) + [What is MoSCoW Prioritization Method? Definit](https://www.youtube.com/watch?v=pm4GbSRMElc&t=65s) 1:05–2:52 (partly) + NotebookLM for: comparison with business value and risk-based prioritization; application to a sample use case set |
| C6 | **Validate use cases against spec guidelines** — Through guided discussion, students apply a checklist derived from spec‑driven guidelines to assess completeness, consistency, and testability of their use case | 15 | in class (discussion) |
| C7 | **Map use cases to spec-driven framework artifacts** — Students learn how each use case maps to downstream artifacts such as feature files, acceptance criteria, and test cases in a spec‑driven development framework. | 15 | [What is Spec Driven Development. Intro to AI ](https://www.youtube.com/watch?v=0atkW_janVg&t=286s) 4:46–6:19 (partly) + NotebookLM for: Explicit mapping of use cases to downstream artifacts; Tracing a use case through the pipeline; Test case creation |
| C8 | **Case study: product description to use case model** — A full case study walks through transforming a realistic product description into a complete use case model, including actors, boundary, scenarios, and prioriti | 15 | [UML use case diagrams: Everything you need to](https://www.youtube.com/watch?v=4emxjxonNRI&t=90s) 1:30–3:17 (partly) + NotebookLM for: Full product description text; Detailed scenarios and use cases; Prioritization and transformation decisions |
| C9 | **Common pitfalls and quality checklist** — Discussion of frequent errors such as actor overload, vague steps, and missing extensions. Students use a quality checklist to review a peer's use case specific | 15 | in class (discussion) |
| C10 | **Summary and transition to spec-driven frameworks** — Recap of the use case engineering process, emphasizing how the produced artifacts feed into spec‑driven development frameworks. Students outline next steps for  | 15 | NotebookLM video (`notebooklm/W05.L1.md`) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W05.L1.md`

**Videos**

1. [UML use case diagrams: Everything you need to know](https://www.youtube.com/watch?v=4emxjxonNRI) — score 0.29
   Teaches C4 Create system boundary context diagram (1:30–3:17, partly); C8 Case study: product description to use case model (1:30–3:17, partly); C3 Write use case extensions and alternate flows (9:13–11:40, partly) [checked on the transcript] · Lucid Software · tier 4 · 12:42 · 1,054,164 views
   *Review:* Clear banking-app example teaches boundaries and actors, but the diagram build and validation are not shown.; Begins an example for a banking app with boundary and actors, but cuts off before covering scenarios or use cases.; Explains diagrammatic extend relationships, extension points, and conditio Use: in-class clip.
2. [Use Case Diagram Tutorial and EXAMPLE ( How to Draw Use Case Diagram )](https://www.youtube.com/watch?v=8V3r5STTmbA) — score 0.31
   Teaches C4 Create system boundary context diagram (1:09–4:53, partly) [checked on the transcript] · The Business Analysis Doctor - IIBA Certification · tier 4 · 13:14 · 30,327 views
   *Review:* Strong notation walkthrough, but no live diagram build or explicit actor-list validation. Use: in-class clip.
3. [What is MoSCoW Prioritization Method? How MoSCoW Makes Team Decisions Super Easy!](https://www.youtube.com/watch?v=XVx5FKZb6l4) — score 0.20
   Teaches C5 Prioritize use cases with MoSCoW (0:00–2:50, partly) [checked on the transcript] · projectcubicle · tier 4 · 3:17 · 6,457 views
   *Review:* Defines MoSCoW categories and drawbacks, but lacks practical use case practice and comparison with risk or business-value methods. Use: in-class clip.
4. [What is MoSCoW Prioritization Method? Definition, Overview, and Best Practices](https://www.youtube.com/watch?v=pm4GbSRMElc) — score 0.19
   Teaches C5 Prioritize use cases with MoSCoW (1:05–2:52, partly) [checked on the transcript] · ProductPlan · tier 4 · 3:27 · 92,848 views
   *Review:* Clear explanation of MoSCoW categories with screening questions, but omits comparative techniques and practical use case exercise. Use: in-class clip.
5. [What is Spec Driven Development. Intro to AI Coding for Real Projects Explained](https://www.youtube.com/watch?v=0atkW_janVg) — score 0.18
   Teaches C7 Map use cases to spec-driven framework artifacts (4:46–6:19, partly) [checked on the transcript] · Codeless Developer · tier 4 · 7:10 · 2,717 views
   *Review:* Explains spec-driven development workflow and artifacts, but does not trace a use case through to test cases. Use: in-class clip.

<sub>15 candidates found · 0 passed the checks · 15 removed</sub>

## W05.L2 · Week 5 · Spec-driven development frameworks ★ new at IIIT-D
*A 0.5-hour lecture in week 5 on “Spec-driven development frameworks”, part of the module “Executable Specifications and Code Generation”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Translate module requirements into executable specifications using spec-driven development frameworks, meeting the stated interface specification for every public method (apply). This serves CO2: Translate unstructured product requirements into executable specifications, using spec-driven development frameworks, covering every use case in the supplied … Students come in knowing Software requirements and requirements engineering. It prepares for Requirements to executable specifications and code generation (week 6). It has a hands-on part (Executable specification lab in week 6). The topic continues in the next lecture. Assessed in Assign2 (week 8), Assign3 (week 9), Midsem (week 7), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Foundations of Spec-Driven Development Frameworks** — Students will understand the core workflow of spec-driven development (SDD) where formal specifications serve as the single source of truth prior to implementat | 15 | [Full Course: Spec-Driven Development with Cod](https://www.youtube.com/watch?v=hy8UstR2NEg&t=24s) 0:24–4:17 (partly) + [Spec-Driven Development: AI Assisted Coding E](https://www.youtube.com/watch?v=mViFYTwWvcM&t=202s) 3:22–7:22 (partly) + NotebookLM for: Comparison between SDD and TDD; Decoupling interface contracts from test code; Static analyzers |
| C2 | **Anatomy of Executable Specifications and Schemas** — Students will examine the internal structural requirements of executable specifications using tools like OpenAPI, JSON Schema, or TypeSpec. They will learn how  | 15 | [Spec-Driven Development (SDD): Specifications](https://www.youtube.com/watch?v=AlsWWmCkYJk&t=81s) 1:21–5:46 (fully) + NotebookLM |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W05.L2.md`

**Videos**

1. [Spec-Driven Development (SDD): Specifications as Primary Human Output](https://www.youtube.com/watch?v=AlsWWmCkYJk) — score 0.56
   Teaches C2 Anatomy of Executable Specifications and Schemas (1:21–5:46, fully) [checked on the transcript] · Mirko Solutions Media · tier 4 · 7:47 · 88 views
   *Review:* Comprehensive explanation of executable specification structure, OpenAPI/JSON schemas, and automated validation. Use: in-class clip.
2. [Spec-Driven Development: AI Assisted Coding Explained](https://www.youtube.com/watch?v=mViFYTwWvcM) — score 0.36
   Teaches C1 Foundations of Spec-Driven Development Frameworks (3:22–7:22, partly) [checked on the transcript] · IBM Technology · tier 2 · 9:00 · 559,553 views
   *Review:* Explains the high-level SDD workflow and compares it with TDD, but lacks detail on contract decoupling. Use: in-class clip.
3. [Full Course: Spec-Driven Development with Coding Agents](https://www.youtube.com/watch?v=hy8UstR2NEg) — score 0.34
   Teaches C1 Foundations of Spec-Driven Development Frameworks (0:24–4:17, partly) [checked on the transcript] · DeepLearningAI · tier 3 · 1:01:34 · 380,111 views
   *Review:* Good overview of agentic SDD workflows and feature loops, but misses TDD comparison and static analyzers. Use: in-class clip.

**Readings**

1. [Making Specs Executable | Spec-Driven](https://specdriven.com/guides/executable-specs) — score 0.78
   Covers: topic ✓, W05.L2.C1 ✓, W05.L2.C2 ✓ [from page text] · specdriven.com · tier 3
   *Review:* Clear explanation of executable specifications and how BDD tools bridge specs and tests. Excellent pre-class reading, though excerpts lack concrete implementation code. Use: before class.
2. [Executable Specifications in Software Development & Testing](https://www.testmuai.com/blog/executable-specifications/) — score 0.69
   Covers: topic ✓, W05.L2.C1 ✓, W05.L2.C2 ✓ [from page text] · testmuai.com · tier 4
   *Review:* Provides a solid conceptual background on executable specifications, BDD origins, and supporting frameworks like Cucumber and Behave. Useful pre-class preparation. Use: before class.

**Possible guest speakers** (guest kit: `guest_kits/W05.L2.md`)

1. **Paul Everitt** — Developer Advocate, JetBrains · score 0.87 · fit: strong
   Delivered talks and a full course on Spec-Driven Development with Coding Agents.
   Evidence: [Spec-Driven Development with Coding Agents - DeepLearning.AI](https://learn.deeplearning.ai/courses/spec-driven-development-with-coding-agents/lesson/8bhg0p/introduction) · [Full Course: Spec-Driven Development with Coding Agents](https://www.youtube.com/watch?v=hy8UstR2NEg)
   [page](https://www.youtube.com/watch?v=hy8UstR2NEg)
2. **Matt Laver** — Senior Specialist Solutions Architect, AWS · score 0.87 · fit: strong
   Presented a talk at XConf Europe 2026 on how AWS approaches spec-driven development.
   Evidence: [How AWS thinks about spec-driven development — XConf Europe 2026 - You](https://www.youtube.com/watch?v=OJ6DiiSoUuQ) · [How AWS thinks about spec-driven development — XConf Europe 2026](https://www.youtube.com/watch?v=OJ6DiiSoUuQ)
   [page](https://www.youtube.com/watch?v=OJ6DiiSoUuQ)
3. **Simon Martinelli** — Software Architect and Creator of the AI Unified Process, Martinelli LLC · score 0.84 · fit: strong
   Authored The Spec-Driven Development Book and associated use case guides.
   Evidence: [Publications: The Spec-Driven Development Book and the Free Use Case G](https://unifiedprocess.ai/publications.html)
   [page](https://unifiedprocess.ai/publications.html)
4. **Den Delimarsky** — Principal Product Engineer, GitHub · score 0.84 · fit: strong
   Authored a GitHub Blog article introducing an open-source toolkit for spec-driven development with AI.
   Evidence: [Spec-driven development with AI: Get started with a new open source to](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
   [page](https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/)
5. **Birgitta Böckeler** — Distinguished Engineer and AI-assisted delivery expert, Thoughtworks · score 0.84 · fit: strong
   Gave a talk explaining spec-driven development frameworks and tools such as Kiro, spec-kit, and Tessl.
   Evidence: [Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
   [page](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)
6. **Sam Hatoum** — Publisher and Founder, SpecDriven · score 0.68 · fit: moderate
   Founder of SpecDriven with published material listing notable figures in spec-driven development.
   Evidence: [Notable People in Spec-Driven Development | Spec-Driven](https://specdriven.com/people)
   [page](https://specdriven.com/people)
   ⚠ evidence is a published directory page rather than a technical framework talk or paper
7. **David Harel** — researcher, Weizmann Institute of Science (IL) · score 0.66 · fit: strong
   Published papers on integrating machine learning and foundation models with executable specifications.
   Evidence: [An infrastructure software perspective toward computation offloading b](https://doi.org/10.1007/s11432-025-4311-9) (2025) · [Categorizing methods for integrating machine learning with executable ](https://doi.org/10.1007/s11432-022-3826-6) (2023)
   [openalex](https://openalex.org/A5088778612) · [orcid](https://orcid.org/0000-0001-7240-3931) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=David+Harel+Weizmann+Institute+of+Science)

<sub>26 candidates found · 4 passed the checks · 22 removed</sub>

## W06.L1 · Week 6 · Spec-driven development frameworks ★ new at IIIT-D
*A 1.5-hour lecture in week 6 on “Spec-driven development frameworks”, part of the module “Executable Specifications and Code Generation”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Translate module requirements into executable specifications using spec-driven development frameworks, meeting the stated interface specification for every public method (apply). This serves CO2: Translate unstructured product requirements into executable specifications, using spec-driven development frameworks, covering every use case in the supplied … Students come in knowing Software requirements and requirements engineering. It prepares for Requirements to executable specifications and code generation (week 6). It has a hands-on part (Executable specification lab in week 6). The topic continues in the next lecture. Assessed in Assign2 (week 8), Assign3 (week 9), Midsem (week 7), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Mapping Natural Language Requirements to Interface Contracts** — Students will learn how to systematically convert informal, natural-language module requirements into structured interface contracts. The instructor demonstrate | 15 | [Is Your OpenAPI Spec Actually Executable? | S](https://www.youtube.com/watch?v=oWh69rNlH_k&t=290s) 4:50–7:48 (partly) + [Spec-Driven Development (SDD): Specifications](https://www.youtube.com/watch?v=AlsWWmCkYJk&t=81s) 1:21–2:52 (partly) + NotebookLM for: converting natural language requirements to interface contracts; defining method signatures, parameters, and return types; mapping requirements to method signatures |
| C2 | **Specifying Preconditions, Postconditions, and Invariants** — Students will formulate explicit invariants, preconditions, and postconditions for every public method in a target module using contract specification framework | 20 | [Spec-Driven Development (SDD): Specifications](https://www.youtube.com/watch?v=AlsWWmCkYJk&t=81s) 1:21–4:50 (partly) + NotebookLM for: method-level preconditions and postconditions; class invariants; concrete validation constraints for input parameters |
| C3 | **Automated Test Generation from Executable Specifications** — Students will observe how spec-driven frameworks automatically synthesize property-based tests and mock servers directly from specification definitions. The dem | 20 | [Spec-Driven Development (SDD): Specifications](https://www.youtube.com/watch?v=AlsWWmCkYJk&t=168s) 2:48–3:53 (partly) + NotebookLM for: Property-based test generation; Mock server synthesis; Live demonstration or parsing of test failure outputs |
| C4 | **Translating Complex Module Requirements into Executable Specifications** — Students will follow a step-by-step translation of a multi-method business module's requirements into a complete, executable specification file. The worked exam | 20 | [Full Course: Spec-Driven Development with Cod](https://www.youtube.com/watch?v=hy8UstR2NEg&t=1092s) 18:12–22:53 (partly) + NotebookLM for: worked example of a multi-method business module; explicit request validation schema and error state specifications; direct mapping of requirements to executable test checks |
| C5 | **Mitigating Spec Drift and Handling Edge Cases** — Students will analyze techniques for maintaining synchronization between evolving executable specifications and generated code over time. They will evaluate tra | 15 | in class (discussion) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W06.L1.md`

**Videos**

1. [Spec-Driven Development (SDD): Specifications as Primary Human Output](https://www.youtube.com/watch?v=AlsWWmCkYJk) — score 0.26
   Teaches C1 Mapping Natural Language Requirements to Interface Contracts (1:21–2:52, partly); C2 Specifying Preconditions, Postconditions, and Invariants (1:21–4:50, partly); C3 Automated Test Generation from Executable Specifications (2:48–3:53, partly) [checked on the transcript] · Mirko Solutions Media · tier 4 · 7:47 · 88 views
   *Review:* Clear explanation of replacing vague prompts with technical specs; lacks interface-level method signatures and type details.; Explains system-level guardrails and machine-parsable specs for AI, but lacks explicit method preconditions and postconditions.; Explains executable specs and automated test  Use: in-class clip.
2. [Full Course: Spec-Driven Development with Coding Agents](https://www.youtube.com/watch?v=hy8UstR2NEg) — score 0.30
   Teaches C4 Translating Complex Module Requirements into Executable Spec (18:12–22:53, partly) [checked on the transcript] · DeepLearningAI · tier 3 · 1:01:34 · 380,111 views
   *Review:* Demonstrates interactive creation and review of feature spec files via AI agent prompts, but lacks detailed multi-method business logic validation. Use: in-class clip.
3. [Is Your OpenAPI Spec Actually Executable? | Specmatic Linter](https://www.youtube.com/watch?v=oWh69rNlH_k) — score 0.26
   Teaches C1 Mapping Natural Language Requirements to Interface Contracts (4:50–7:48, partly) [checked on the transcript] · Specmatic · tier 4 · 10:18 · 133 views
   *Review:* Demonstrates OpenAPI semantic validation catching runtime errors, but does not cover converting natural language into signatures. Use: in-class clip.

**Readings**

1. [Spec-Driven Development:From Code to Contract in the Age of AI Coding Assistants](https://arxiv.org/html/2602.00180v1) — score 0.81
   Covers: topic ✓, W06.L1.C1 ✓, W06.L1.C2 ✓, W06.L1.C3 ✓, W06.L1.C4 ✓, W06.L1.C5 ✓ [from page text] · arxiv.org · tier 2
   *Review:* A rigorous, clear overview of modern spec-driven development patterns, tooling categories, and workflows. Excellent for conceptual framing before class, though students will need supplementary concrete code examples. Use: before class.
2. [Spec-Driven Development Using Claude Code: Practical Guide | SaM Solutions](https://sam-solutions.com/blog/spec-driven-development-with-claude-code/) — score 0.74
   Covers: topic ✓, W06.L1.C1 ✓, W06.L1.C2 ✓, W06.L1.C3 ✓, W06.L1.C4 ✓, W06.L1.C5 ✓ [from page text] · sam-solutions.com · tier 4
   *Review:* A practical, step-by-step industry guide demonstrating how to move from requirements to verified code and test contracts. Useful after-class reading for seeing end-to-end SDD in an AI-assisted environment. Use: after class.

**Possible guest speakers:** same topic as W05.L2; see its list and guest kit.

<sub>26 candidates found · 6 passed the checks · 20 removed</sub>

## W06.L2 · Week 6 · Requirements to executable specifications and code generation ★ new at IIIT-D
*A 1.5-hour lecture in week 6 on “Requirements to executable specifications and code generation”, part of the module “Executable Specifications and Code Generation”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Translate module requirements into executable specifications using spec-driven development frameworks, meeting the stated interface specification for every public method (apply). This serves CO2: Translate unstructured product requirements into executable specifications, using spec-driven development frameworks, covering every use case in the supplied … Students come in knowing Spec-driven development frameworks. It has a hands-on part (Executable specification lab in week 6). The topic continues in the next lecture. Assessed in Assign3 (week 9), Midsem (week 7), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Deconstructing Requirements into Public Method Contracts** — Students will learn how to analyze informal requirements to identify public module methods, parameter contracts, and class invariants. They will establish stric | 15 | NotebookLM video (`notebooklm/W06.L2.md`) |
| C2 | **Structuring Executable Specifications in Spec-Driven Frameworks** — Students will learn the concrete syntax and structural conventions of spec-driven frameworks such as pytest-bdd or Behave. They will map high-level requirement  | 15 | NotebookLM video (`notebooklm/W06.L2.md`) |
| C3 | **Step-by-Step Translation of Requirements to Executable Specs** — Students will follow a complete worked example translating a payment-processing requirement brief into an automated executable specification suite. They will ob | 20 | NotebookLM video (`notebooklm/W06.L2.md`) |
| C4 | **Prompt Patterns for Generating Executable Specifications** — Students will learn effective prompting architectures to instruct LLMs to synthesize spec-driven test suites from unstructured requirements documents. They will | 15 | NotebookLM video (`notebooklm/W06.L2.md`) |
| C5 | **Hands-on Authoring of Executable Specs from Requirements** — Students will work in pairs to translate a natural-language requirement specification for a user session manager into an executable specification suite using a  | 25 | in class (activity) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W06.L2.md`

**Readings**

1. [Making Specs Executable | Spec-Driven](https://specdriven.com/guides/executable-specs) — score 0.72
   Covers: topic ✓, W06.L2.C1 ✗, W06.L2.C2 ✓, W06.L2.C3 ✓, W06.L2.C4 ✓, W06.L2.C5 ✓ [from page text] · specdriven.com · tier 4
   *Review:* Excellent explanation of executable specifications and BDD integration. Clearly articulates why specs must be verifiable and how step definitions bridge natural language specs to code. Use: before class.
2. [spec-kit/spec-driven.md at main · github/spec-kit · GitHub](https://github.com/github/spec-kit/blob/main/spec-driven.md) — score 0.69
   Covers: topic ✓, W06.L2.C1 ✓, W06.L2.C2 ✓, W06.L2.C3 ✓, W06.L2.C4 ✓, W06.L2.C5 ✓ [from page text] · github.com · tier 3
   *Review:* Detailed look at spec-kit's TDD imperative and governance rules. Good for understanding how structured spec templates constrain LLM code generation in practice. Use: before class.

**Possible guest speakers** (guest kit: `guest_kits/W06.L2.md`)

1. **Raju Halder** — researcher, Indian Institute of Technology Patna (IN) · score 0.52 · fit: moderate
   Published papers on formal verification and code generation for Solidity smart contracts, connecting formal specifications to code generation.
   Evidence: [SolGen: Secure Smart Contract Code Generation Using Large Language Mod](https://doi.org/10.1145/3717383.3717394) (2025) · [Formal verification and code generation for solidity smart contracts](https://doi.org/10.1016/b978-0-323-96146-2.00028-0) (2023)
   [openalex](https://openalex.org/A5032316006) · [orcid](https://orcid.org/0000-0002-8873-8258) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Raju+Halder+Indian+Institute+of+Technology+Patna)
   ⚠ focus is specialized on smart contracts

<sub>27 candidates found · 3 passed the checks · 24 removed</sub>

## W07.L1 · Week 7 · Requirements to executable specifications and code generation ★ new at IIIT-D
*A 1-hour lecture in week 7 on “Requirements to executable specifications and code generation”, part of the module “Executable Specifications and Code Generation”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Translate module requirements into executable specifications using spec-driven development frameworks, meeting the stated interface specification for every public method (apply). This serves CO2: Translate unstructured product requirements into executable specifications, using spec-driven development frameworks, covering every use case in the supplied … Students come in knowing Spec-driven development frameworks. It has a hands-on part (Executable specification lab in week 6). The topic continues in the next lecture. Assessed in Assign3 (week 9), Midsem (week 7), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Reviewing Spec Completeness and Interface Compliance** — Students review criteria for determining whether an executable specification suite is fully complete and airtight before running code generation. They will insp | 10 | [Spec-Driven Development Explained: The Workfl](https://www.youtube.com/watch?v=2XI-lO7ANYw&t=0s) 0:00–3:00 (partly) + [Spec-Driven Development: The Discipline Behin](https://www.youtube.com/watch?v=Gv4hd49lI4E&t=823s) 13:43–17:05 (partly) + NotebookLM for: specification completeness criteria; contract boundary validation; interface validation |
| C2 | **Spec-Guided AI Code Generation and Validation Loop** — Students will learn the automated feedback loop where LLMs consume executable specifications, generate implementation candidates, and refine code based on faili | 15 | [Spec-Driven Development Explained: The Workfl](https://www.youtube.com/watch?v=2XI-lO7ANYw&t=0s) 0:00–2:54 (partly) + NotebookLM for: test-driven prompt loop; automated test harness feedback; error trace analysis for refinement |
| C3 | **Iterative Code Generation Against Executable Specifications** — Students will use an AI assistant to generate production code that satisfies the executable specifications authored in the previous session. They will capture r | 20 | in class (activity) |
| C4 | **Comparing Conforming Implementations Against Spec Overfitting** — Students will compare code that truly satisfies underlying business logic against code that overfits or cheats executable test mocks. They will evaluate techniq | 15 | [Spec-Driven Development with Claude Code: A P](https://www.youtube.com/watch?v=yH-qzlkzPbs&t=253s) 4:13–9:07 (partly) + NotebookLM for: mutation testing; property-based validation; mock cheating detection |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W07.L1.md`

**Videos**

1. [Spec-Driven Development Explained: The Workflow That Keeps AI Agents Aligned](https://www.youtube.com/watch?v=2XI-lO7ANYw) — score 0.35
   Teaches C1 Reviewing Spec Completeness and Interface Compliance (0:00–3:00, partly); C2 Spec-Guided AI Code Generation and Validation Loop (0:00–2:54, partly) [checked on the transcript] · Augment Code · tier 4 · 4:32 · 17,908 views
   *Review:* Live spec review demo; focuses on assumptions not boundary failures.; Live demo of spec-driven agent workflow; mentions verification but not automated test-feedback loop. Use: in-class clip.
2. [Spec-Driven Development with Claude Code: A Practical Guide](https://www.youtube.com/watch?v=yH-qzlkzPbs) — score 0.34
   Teaches C4 Comparing Conforming Implementations Against Spec Overfittin (4:13–9:07, partly) [checked on the transcript] · SaM Solutions · tier 4 · 9:38 · 9,525 views
   *Review:* Covers automated validation hooks and sub-agent reviews; lacks mutation testing and property-based checks for mock overfitting. Use: in-class clip.
3. [Spec-Driven Development: The Discipline Behind Reliable AI Coding](https://www.youtube.com/watch?v=Gv4hd49lI4E) — score 0.33
   Teaches C1 Reviewing Spec Completeness and Interface Compliance (13:43–17:05, partly) [checked on the transcript] · deepsense · tier 4 · 18:12 · 8,939 views
   *Review:* Best practices for spec creation; lacks concrete completeness checklist. Use: in-class clip.

**Readings**

1. [Spec-Driven Development Using Claude Code: Practical Guide | SaM Solutions](https://sam-solutions.com/blog/spec-driven-development-with-claude-code/) — score 0.73
   Covers: topic ✓, W07.L1.C1 ✓, W07.L1.C2 ✓, W07.L1.C3 ✓, W07.L1.C4 ✓ [from page text] · sam-solutions.com · tier 4
   *Review:* Good overview of the spec-driven development workflow with AI agents and requirement-to-test mapping. Lacks specific framework code implementations. Use: before class.
2. [Executable specifications - HitchDev](https://hitchdev.com/hitchstory/approach/executable-specifications/) — score 0.69
   Covers: topic ✓, W07.L1.C1 ✓, W07.L1.C2 ✓, W07.L1.C3 ✓, W07.L1.C4 ✓ [from page text] · hitchdev.com · tier 4
   *Review:* Clear conceptual summary of executable specifications and separation of spec from test execution. Lacks detailed framework examples. Use: before class.

**Possible guest speakers:** same topic as W06.L2; see its list and guest kit.

<sub>28 candidates found · 3 passed the checks · 25 removed</sub>

## W07.L2 · Week 7 · Iterative development and loop engineering ★ new at IIIT-D
*A 2-hour lecture in week 7 on “Iterative development and loop engineering”, part of the module “Iterative Loop Engineering and Tracing”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Trace execution logs produced by coding agents during iterative loop engineering tasks, recording all control-flow steps across the log artifact (understand). This serves CO3: Analyze the execution traces produced by coding agents during iterative loop engineering tasks, identifying at least three distinct … It prepares for Iterative development logs and software factory outputs (week 8). It has a hands-on part (Iterative loop engineering lab in week 7). The topic continues in the next lecture. Assessed in LabEval1 (week 12), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Iterative Loop Engineering Overview** — Students learn the definition of iterative loop engineering, its role in AI‑assisted coding, and the high‑level phases of a coding agent's generate‑test‑refacto | 15 | [What Is Loop Engineering? Building Better AI ](https://www.youtube.com/watch?v=DQBqh6gcx7U&t=0s) 0:00–3:15 (fully) + NotebookLM |
| C2 | **Execution Log Structure and Fields** — Students identify the standard schema of an execution log, including timestamp, event type, agent identifier, and payload, and understand how each field maps to | 15 | NotebookLM video (`notebooklm/W07.L2.md`) |
| C3 | **Control‑Flow Step Taxonomy** — Students categorize the distinct step types recorded in logs—function calls, loop iterations, conditional branches, and agent decision points—and explain how ea | 15 | NotebookLM video (`notebooklm/W07.L2.md`) |
| C4 | **Instrumentation and Logging Frameworks** — Students observe a live demo of adding instrumentation hooks to a coding agent using Python's logging module and OpenTelemetry, seeing how logs are emitted in r | 15 | NotebookLM video (`notebooklm/W07.L2.md`) |
| C5 | **Worked Example: Simple Agent Loop Trace** — Students follow a step‑by‑step trace of a toy generate‑test‑refactor agent, mapping each log entry to source‑code changes and identifying the control‑flow path. | 15 | [The Agent Loop Explained: What Happens When Y](https://www.youtube.com/watch?v=Gy4ECDG_hI4&t=0s) 0:00–3:25 (fully) + NotebookLM |
| C6 | **Activity: Instrument a Toy Agent** — Students modify a provided skeleton agent to emit structured logs, run it on a sample task, and verify that all control‑flow steps appear in the output log. | 15 | in class (activity) |
| C7 | **Mapping Log Steps to Code Changes** — Students learn techniques to correlate log entries with diffs in the codebase, using timestamps and agent IDs to reconstruct the iterative development narrative | 15 | NotebookLM video (`notebooklm/W07.L2.md`) |
| C8 | **Pitfalls and Best Practices in Tracing** — Students compare common logging anti‑patterns—missing context, inconsistent granularity, and timestamp drift—with recommended practices for reliable traceabilit | 15 | NotebookLM video (`notebooklm/W07.L2.md`) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W07.L2.md`

**Videos**

1. [The Agent Loop Explained: What Happens When You Give Claude a Bug to Fix](https://www.youtube.com/watch?v=Gy4ECDG_hI4) — score 0.45
   Teaches C5 Worked Example: Simple Agent Loop Trace (0:00–3:25, fully) [checked on the transcript] · ByteMonk · tier 4 · 12:18 · 8,454 views
   *Review:* Clear walkthrough of agent loop with concrete bug-fix demo; assumes coding familiarity Use: in-class clip.
2. [What Is Loop Engineering? Building Better AI Agents](https://www.youtube.com/watch?v=DQBqh6gcx7U) — score 0.50
   Teaches C1 Iterative Loop Engineering Overview (0:00–3:15, fully) [checked on the transcript] · IBM Technology · tier 2 · 10:48 · 123,818 views
   *Review:* Clear definition with concrete checkout example; covers all three learning objectives. Use: in-class clip.

**Readings**

1. [The Agent-Run Loop: Reframing the SDLC as a Continuous Cycle | Augment Code](https://www.augmentcode.com/guides/agent-run-development-loop) — score 0.62
   Covers: topic ✓, W07.L2.C1 ✓, W07.L2.C2 ✗, W07.L2.C3 ✓, W07.L2.C4 ✗, W07.L2.C5 ✓, W07.L2.C6 ✓, W07.L2.C7 ✓, W07.L2.C8 ✗ [from page text] · augmentcode.com · tier 4
   *Review:* Good conceptual overview of agent-run loops; lacks technical depth on log tracing. Use: before class.
2. [What Is Loop Engineering? | IBM](https://www.ibm.com/think/topics/loop-engineering) — score 0.62
   Covers: topic ✓, W07.L2.C1 ✓, W07.L2.C2 ✗, W07.L2.C3 ✓, W07.L2.C4 ✓, W07.L2.C5 ✓, W07.L2.C6 ✓, W07.L2.C7 ✓, W07.L2.C8 ✗ [from page text] · ibm.com · tier 4
   *Review:* Clear definition of loop engineering from IBM; good for intro but lacks hands-on trace analysis. Use: before class.

**Practice**

1. [rohitg00/ai-engineering-from-scratch — Learn AI Engineering! Learn it. Build it. Ship it for others.](https://github.com/rohitg00/ai-engineering-from-scratch) — score 0.62
   Covers: topic ✗, W07.L2.C1 ✓, W07.L2.C2 ✓, W07.L2.C3 ✓, W07.L2.C4 ✗, W07.L2.C5 ✓, W07.L2.C6 ✓, W07.L2.C7 ✓, W07.L2.C8 ✗ [from page text] · GitHub · tier 3
   *Review:* Curriculum with lessons on agent loops; good for structured practice but main lecture topic not explicitly covered. Use: practice.
   ⚠ AI review: mentions the topic but does not really teach it

**Possible guest speakers** (guest kit: `guest_kits/W07.L2.md`)

1. **Christoph Treude** — Associate Professor of Computer Science, Singapore Management University (SG) · score 0.70 · fit: strong
   Co-authored the paper "Loop Engineering: Building Blocks, Adoption, and Impact", directly addressing the lecture's core topic on loop engineering.
   Evidence: [Loop Engineering: Building Blocks, Adoption, and Impact](https://doi.org/10.48550/arxiv.2608.21884) (2026)
   [openalex](https://openalex.org/A5134124070) · [orcid](https://orcid.org/0000-0002-6919-2149) · [scholar](https://scholar.google.com/citations?user=-ie8QFEAAAAJ)
2. **Jian Zhang** — researcher, Beihang University (CN) · score 0.69 · fit: strong
   Authored papers on agent execution traces, trace-driven debugging, and execution provenance ("Tracecoder", "AutoSaddler", and a survey on agent traces), matching the outcome on tracing coding agent execution logs.
   Evidence: [Tracecoder: A trace-driven multi-agent framework for automated debuggi](https://dl.acm.org/doi/abs/10.1145/3744916.3773187) (2026) · [AutoSaddler: Automatic harness optimization with durable updates from ](https://arxiv.org/abs/2608.23041) (2026)
   [scholar](https://scholar.google.com/citations?user=ki1y5TQAAAAJ)
3. **Jai Lal Lulla** — researcher, Research Engineer (SG) · score 0.68 · fit: strong
   Co-authored the paper "Loop Engineering: Building Blocks, Adoption, and Impact", directly covering the lecture's core subject.
   Evidence: [Loop Engineering: Building Blocks, Adoption, and Impact](https://doi.org/10.48550/arxiv.2608.21884) (2026)
   [openalex](https://openalex.org/A5120727286) · [orcid](https://orcid.org/0009-0005-0024-8238) · [scholar](https://scholar.google.com/citations?user=U6GH2EMAAAAJ)
4. **Sebastian Baltes** — researcher, Heidelberg University (DE) · score 0.67 · fit: strong
   Co-authored the paper "Loop Engineering: Building Blocks, Adoption, and Impact", providing direct evidence of research on loop engineering.
   Evidence: [Loop Engineering: Building Blocks, Adoption, and Impact](https://doi.org/10.48550/arxiv.2608.21884) (2026)
   [openalex](https://openalex.org/A5033132966) · [orcid](https://orcid.org/0000-0002-2442-7522) · [scholar](https://scholar.google.com/citations?user=xO09KrYAAAAJ)
5. **Seyedmoein Mohsenimofidi** — Doctoral researcher, Heidelberg University (DE) · score 0.66 · fit: strong
   Co-authored the paper "Loop Engineering: Building Blocks, Adoption, and Impact", demonstrating direct research involvement in loop engineering.
   Evidence: [Loop Engineering: Building Blocks, Adoption, and Impact](https://doi.org/10.48550/arxiv.2608.21884) (2026)
   [openalex](https://openalex.org/A5095107558) · [orcid](https://orcid.org/0009-0009-1620-2735) · [scholar](https://scholar.google.com/citations?user=Ze83xwwAAAAJ)

<sub>30 candidates found · 4 passed the checks · 26 removed</sub>

## W08.L1 · Week 8 · Iterative development and loop engineering ★ new at IIIT-D
*A 1-hour lecture in week 8 on “Iterative development and loop engineering”, part of the module “Iterative Loop Engineering and Tracing”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Trace execution logs produced by coding agents during iterative loop engineering tasks, recording all control-flow steps across the log artifact (understand). This serves CO3: Analyze the execution traces produced by coding agents during iterative loop engineering tasks, identifying at least three distinct … It prepares for Iterative development logs and software factory outputs (week 8). It has a hands-on part (Iterative loop engineering lab in week 7). The topic continues in the next lecture. Assessed in LabEval1 (week 12), Endsem (week 13).*

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Recap: Log Schema and Step Types** — Students quickly review the log schema and control‑flow taxonomy from the previous session to reinforce shared vocabulary before advanced topics. | 15 | NotebookLM video (`notebooklm/W08.L1.md`) |
| C2 | **Advanced Tracing: Nested and Parallel Loops** — Students examine how nested iterative loops and concurrent agent executions appear in a single log, learning to disambiguate interleaved control‑flow steps usin | 15 | NotebookLM video (`notebooklm/W08.L1.md`) |
| C3 | **Worked Example: Real‑World Agent Log Analysis** — Students walk through a full‑scale log from a production coding agent, extracting the generate‑test‑refactor cycles, identifying bottlenecks, and proposing inst | 15 | NotebookLM video (`notebooklm/W08.L1.md`) |
| C4 | **Activity: Group Log Trace Report** — In teams, students receive an anonymized iterative development log, produce a structured trace report linking each control‑flow step to code artifacts, and pres | 15 | in class (activity) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W08.L1.md`

**Readings**

1. [Loop Engineering: The Missing Discipline for Production AI Agents](https://aishwaryasrinivasan.substack.com/p/all-you-need-to-know-about-loop-engineering) — score 0.65
   Covers: topic ✓, W08.L1.C1 ✗, W08.L1.C2 ✓, W08.L1.C3 ✓, W08.L1.C4 ✗ [from page text] · aishwaryasrinivasan.substack.com · tier 4
   *Review:* Clear conceptual introduction to loop engineering; lacks practical log tracing exercises. Use: before class.
2. [What Is Loop Engineering? The New Meta for AI Coding Agents | MindStudio](https://www.mindstudio.ai/blog/what-is-loop-engineering-ai-coding-agents) — score 0.64
   Covers: topic ✓, W08.L1.C1 ✗, W08.L1.C2 ✓, W08.L1.C3 ✓, W08.L1.C4 ✗ [from page text] · mindstudio.ai · tier 4
   *Review:* Good conceptual overview of loop engineering vs chains; no practical log analysis. Use: before class.

**Possible guest speakers:** same topic as W07.L2; see its list and guest kit.

<sub>27 candidates found · 4 passed the checks · 23 removed</sub>

## W08.L2 · Week 8 · Iterative development logs and software factory outputs ★ new at IIIT-D
*A 2-hour lecture in week 8 on “Iterative development logs and software factory outputs”, part of the module “Iterative Loop Engineering and Tracing”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Examine iterative development logs and software factory outputs, identifying at least 2 of the 4 seeded defects, with a proposed fix for each (analyse). This serves CO3: Analyze the execution traces produced by coding agents during iterative loop engineering tasks, identifying at least three distinct … Students come in knowing Iterative development and loop engineering. It prepares for Software factories and execution trace analysis (week 9). It has a hands-on part (Defect identification lab in week 8). Assessed in LabEval1 (week 12), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:20). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Structure of iterative development logs** — Students will understand the standard sections of an iterative development log (commit metadata, test results, tool invocations) and the schema of software fact | 15 | [My Agentic Coding Workflow on a Real Feature,](https://www.youtube.com/watch?v=0OvbSRoiR0Q&t=1850s) 30:50–35:50 (partly) + NotebookLM for: test results in logs; tool invocations in logs; build reports schema |
| C2 | **Seeded defect taxonomy in factory outputs** — Students will learn the four categories of seeded defects (missing dependency, flaky test, configuration drift, resource leak) and their characteristic signatur | 15 | NotebookLM video (`notebooklm/W08.L2.md`) |
| C3 | **Parsing and querying log data with CLI tools** — Students will be able to use grep, jq, and custom scripts to extract relevant log entries and factory output fields for defect hunting. | 15 | NotebookLM video (`notebooklm/W08.L2.md`) |
| C4 | **Worked example: detecting a missing dependency defect** — Students will follow a step‑by‑step analysis of a sample log where a missing dependency causes a build failure, seeing how to locate the error trace, correlate  | 15 | NotebookLM video (`notebooklm/W08.L2.md`) |
| C5 | **Activity: find two seeded defects in a provided log set** — Students will individually examine a zip of logs and factory outputs, identify at least two of the four seeded defects, and write a brief fix proposal for each, | 15 | in class (activity) |
| C6 | **Comparing defect patterns across iterations** — Students will compare how the same defect type manifests differently across multiple iterations, noting variations in log verbosity, test flakiness, and factory | 15 | NotebookLM video (`notebooklm/W08.L2.md`) |
| C7 | **Case study: real‑world factory log analysis** — Students will review a redacted industry case where iterative logs revealed a configuration drift defect, discussing detection strategy, impact assessment, and  | 15 | NotebookLM video (`notebooklm/W08.L2.md`) |
| C8 | **Discussion: best practices for proposing fixes** — Students will evaluate fix proposals for completeness, testability, and regression risk, and agree on a checklist for future defect remediation in iterative loo | 15 | in class (discussion) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W08.L2.md`

**Videos**

1. [My Agentic Coding Workflow on a Real Feature, Start to Finish](https://www.youtube.com/watch?v=0OvbSRoiR0Q) — score 0.31
   Teaches C1 Structure of iterative development logs (30:50–35:50, partly) [checked on the transcript] · Damian Galarza · tier 4 · 42:07 · 2,161 views
   *Review:* Shows conventional commits for commit metadata; lacks log sections, test results, tool invocations, build reports, artifact manifests. Use: in-class clip.

**Possible guest speakers** (guest kit: `guest_kits/W08.L2.md`)

No candidate passed the checks for this lecture.

<sub>27 candidates found · 0 passed the checks · 27 removed</sub>

## W09.L1 · Week 9 · Software factories and execution trace analysis ★ new at IIIT-D
*A 2.5-hour lecture in week 9 on “Software factories and execution trace analysis”, part of the module “Diagnostic Log Analysis and Software Factories”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Analyze execution traces produced by coding agents during iterative loop engineering tasks, for a supplied log file of at most 2000 lines, identifying at least three distinct failure causes with supporting log evidence (analyse). This serves CO3: Analyze the execution traces produced by coding agents during iterative loop engineering tasks, identifying at least three distinct … Students come in knowing Iterative development logs and software factory outputs. It prepares for Testing and validation in iterative development (week 9). It has a hands-on part (Trace analysis lab in week 9; Testing pipeline lab in week 10). Assessed in LabEval1 (week 12), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:20). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Execution traces in software factories** — Students learn what execution traces are, how coding agents emit them during iterative loop engineering, and why they are essential for diagnosing failures in s | 15 | [Luciq Bits: How to Utilize Execution Traces](https://www.youtube.com/watch?v=oDTh2apD8TM&t=24s) 0:24–3:27 (partly) + NotebookLM for: coding agents emitting traces; iterative loop engineering; software factory context |
| C2 | **Log structure and iteration markers** — Students examine the standardized format of iterative development logs, including timestamps, iteration IDs, tool calls, and error markers, enabling systematic  | 15 | NotebookLM video (`notebooklm/W09.L1.md`) |
| C3 | **Typical failure patterns in agent traces** — Students identify three recurring failure categories—environment misconfiguration, dependency resolution errors, and logic regressions—and learn the trace signa | 15 | NotebookLM video (`notebooklm/W09.L1.md`) |
| C4 | **Trace collection and parsing tooling** — Students watch a live demonstration of the factory's trace collector, log aggregator, and a Python script that parses raw logs into structured JSON for analysis | 15 | NotebookLM video (`notebooklm/W09.L1.md`) |
| C5 | **Worked example: environment misconfiguration** — Students follow a step‑by‑step analysis of a 500‑line trace, locating missing environment variables, correlating error codes, and citing exact log lines as evid | 15 | NotebookLM video (`notebooklm/W09.L1.md`) |
| C6 | **Worked example: dependency resolution failure** — Students trace a version conflict across iterations, observe repeated fetch retries, and extract the specific dependency graph lines that prove the second failu | 15 | NotebookLM video (`notebooklm/W09.L1.md`) |
| C7 | **Worked example: logic regression detection** — Students compare successive iteration outputs, spot a behavioral change in test results, and pinpoint the commit diff lines that constitute the third failure ca | 15 | NotebookLM video (`notebooklm/W09.L1.md`) |
| C8 | **Comparing failure causes across traces** — Students contrast the three failure signatures side‑by‑side, evaluate their frequency and impact, and practice ranking them by severity using a structured rubri | 15 | NotebookLM video (`notebooklm/W09.L1.md`) |
| C9 | **Activity: analyze full 2000‑line log** — In pairs, students receive a 2000‑line factory log, apply the parsing script, identify at least three distinct failure causes, and record supporting log line nu | 15 | in class (activity) |
| C10 | **Discussion: reporting and best practices** — Students present their findings, critique evidence quality, discuss how to automate failure‑cause detection, and outline a checklist for future trace analyses. | 15 | in class (discussion) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W09.L1.md`

**Videos**

1. [Luciq Bits: How to Utilize Execution Traces](https://www.youtube.com/watch?v=oDTh2apD8TM) — score 0.21
   Teaches C1 Execution traces in software factories (0:24–3:27, partly) [checked on the transcript] · Luciq  · tier 4 · 4:31 · 353 views
   *Review:* Clear demo of execution traces for mobile app monitoring; not software factories or coding agents. Use: in-class clip.

**Practice**

1. [Using Execution Traces to Evaluate AI Agent Behavior](https://huggingface.co/blog/phranzia/using-execution-traces-to-evaluate-agent-behavior) — score 0.74
   Covers: topic ✓, W09.L1.C1 ✓, W09.L1.C2 ✓, W09.L1.C3 ✓, W09.L1.C4 ✓, W09.L1.C5 ✓, W09.L1.C6 ✓, W09.L1.C7 ✓, W09.L1.C8 ✓, W09.L1.C9 ✓, W09.L1.C10 ✓ [from page text] · huggingface.co · tier 3
   *Review:* Clear, practical overview of execution traces with good visuals; useful intro but light on deep analysis. Use: before class.

**Possible guest speakers** (guest kit: `guest_kits/W09.L1.md`)

1. **Ludovic Apvrille** — researcher, Télécom Paris (FR) · score 0.52 · fit: moderate
   Same 2023 and 2021 papers on execution trace analysis for latency violations; strong on trace analysis but focused on latency, not agentic loops.
   Evidence: [Execution trace analysis for a precise understanding of latency violat](https://doi.org/10.1007/s10270-022-01076-z) (2023) · [Execution Trace Analysis for a Precise Understanding of Latency Violat](https://doi.org/10.1109/models50736.2021.00021) (2021)
   [openalex](https://openalex.org/A5058794408) · [orcid](https://orcid.org/0000-0002-1167-4639) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Ludovic+Apvrille+T%C3%A9l%C3%A9com+Paris)
   ⚠ works on a neighbouring area (latency violations)
2. **Renaud Pacalet** — researcher, Télécom Paris (FR) · score 0.52 · fit: moderate
   Same 2023 and 2021 papers on execution trace analysis for latency violations; strong on trace analysis but focused on latency, not agentic loops.
   Evidence: [Execution trace analysis for a precise understanding of latency violat](https://doi.org/10.1007/s10270-022-01076-z) (2023) · [Execution Trace Analysis for a Precise Understanding of Latency Violat](https://doi.org/10.1109/models50736.2021.00021) (2021)
   [openalex](https://openalex.org/A5066041952) · [orcid](https://orcid.org/0000-0002-6676-1123) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Renaud+Pacalet+T%C3%A9l%C3%A9com+Paris)
   ⚠ works on a neighbouring area (latency violations)
3. **Hongdou He** — researcher, Yanshan University (CN) · score 0.49 · fit: moderate
   Same 2019 paper on mining probabilistic behavior models from dynamic software execution traces; relevant but predates agentic coding agents.
   Evidence: [Mining of Probabilistic Controlling Behavior Model From Dynamic Softwa](https://doi.org/10.1109/access.2019.2922998) (2019)
   [openalex](https://openalex.org/A5077981451) · [orcid](https://orcid.org/0000-0002-8801-8349) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Hongdou+He+Yanshan+University)
   ⚠ evidence is old (2019); works on a neighbouring area
4. **Guyu Zhao** — researcher, Yanshan University (CN) · score 0.49 · fit: moderate
   2019 paper on mining probabilistic behavior models from dynamic software execution traces; relevant but predates agentic coding agents.
   Evidence: [Mining of Probabilistic Controlling Behavior Model From Dynamic Softwa](https://doi.org/10.1109/access.2019.2922998) (2019)
   [openalex](https://openalex.org/A5055957685) · [orcid](https://orcid.org/0000-0002-1198-8662) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Guyu+Zhao+Yanshan+University)
   ⚠ evidence is old (2019); works on a neighbouring area

<sub>30 candidates found · 2 passed the checks · 28 removed</sub>

## W09.L2 · Week 9 · Testing and validation in iterative development ★ new at IIIT-D
*A 0.5-hour lecture in week 9 on “Testing and validation in iterative development”, part of the module “Diagnostic Log Analysis and Software Factories”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Analyze execution traces produced by coding agents during iterative loop engineering tasks, for a supplied log file of at most 2000 lines, identifying at least three distinct failure causes with supporting log evidence (analyse). This serves CO3: Analyze the execution traces produced by coding agents during iterative loop engineering tasks, identifying at least three distinct … Students come in knowing Software factories and execution trace analysis. It has a hands-on part (Trace analysis lab in week 9; Testing pipeline lab in week 10). The topic continues in the next lecture. Assessed in LabEval1 (week 12), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:20). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Trace structure and metadata** — Students learn the standard fields of an agent execution trace: timestamps, event types, tool calls, return values, and error codes. They understand how these f | 15 | NotebookLM video (`notebooklm/W09.L2.md`) |
| C2 | **Worked example: diagnosing tool misuse** — The instructor walks through a 500-line trace where the agent repeatedly calls a file‑write tool with an invalid path. Students see how to locate the offending  | 15 | NotebookLM video (`notebooklm/W09.L2.md`) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W09.L2.md`

**Readings**

1. [How to Debug AI Agents](https://www.langchain.com/blog/agent-observability-powers-agent-evaluation) — score 0.69
   Covers: topic ✓, W09.L2.C1 ✓, W09.L2.C2 ✓ [from page text] · langchain.com · tier 4
   *Review:* Clear explanation of agent trace structure and debugging with a concrete example of tool misuse; good for pre-class reading. Use: before class.

**Possible guest speakers** (guest kit: `guest_kits/W09.L2.md`)

1. **Timofey Bryksin** — researcher, JetBrains Research · score 0.56 · fit: strong
   Co-authored 'Debug Smarter, Not Harder' paper; research interests in data-driven SE and code analysis.
   Evidence: [Debug Smarter, Not Harder: AI Agents for Error Resolution in Computati](https://doi.org/10.18653/v1/2024.emnlp-demo.38) (2024) · [Debug Smarter, Not Harder: AI Agents for Error Resolution in Computati](https://doi.org/10.48550/arxiv.2410.14393) (2024)
   [openalex](https://openalex.org/A5065316896) · [orcid](https://orcid.org/0000-0001-9022-3563) · [scholar](https://scholar.google.com/citations?user=kcbdyR4AAAAJ)
   ⚠ Evidence from 2024, computational notebooks context
2. **Florent Avellaneda** — researcher, Université du Québec à Montréal (CA) · score 0.54 · fit: strong
   Authored 'DynamicsLLM: a Dynamic Analysis-based Tool for Generating Intelligent Execution Traces Using LLMs' on generating execution traces with LLMs.
   Evidence: [DynamicsLLM: a Dynamic Analysis-based Tool for Generating Intelligent ](https://openalex.org/W7154539973) (2026) · [DynamicsLLM: a Dynamic Analysis-based Tool for Generating Intelligent ](https://doi.org/10.48550/arxiv.2604.10661) (2026)
   [openalex](https://openalex.org/A5043879886) · [orcid](https://orcid.org/0000-0003-1030-5388) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Florent+Avellaneda+Universit%C3%A9+du+Qu%C3%A9bec+%C3%A0+Montr%C3%A9al)
   ⚠ Android-specific, but execution traces general
3. **Adam Fourney** — Senior Principal Researcher, Microsoft Research (US) · score 0.52 · fit: moderate
   Co-authored AutoGen Studio papers on no-code tool for building and debugging multi-agent systems.
   Evidence: [AUTOGEN STUDIO: A No-Code Developer Tool for Building and Debugging Mu](https://doi.org/10.18653/v1/2024.emnlp-demo.8) (2024) · [AutoGen Studio: A No-Code Developer Tool for Building and Debugging Mu](https://doi.org/10.48550/arxiv.2408.15247) (2024)
   [openalex](https://openalex.org/A5071293344) · [orcid](https://orcid.org/0000-0002-4986-7794) · [scholar](https://scholar.google.com/citations?user=NBoXr9oAAAAJ)
   ⚠ Evidence from 2024, not specifically about iterative development testing
4. **Jingya Chen** — industry, Microsoft (US) · score 0.51 · fit: moderate
   Co-authored AutoGen Studio papers on no-code tool for building and debugging multi-agent systems.
   Evidence: [AUTOGEN STUDIO: A No-Code Developer Tool for Building and Debugging Mu](https://doi.org/10.18653/v1/2024.emnlp-demo.8) (2024) · [AutoGen Studio: A No-Code Developer Tool for Building and Debugging Mu](https://doi.org/10.48550/arxiv.2408.15247) (2024)
   [openalex](https://openalex.org/A5031477562) · [orcid](https://orcid.org/0009-0004-4324-3456) · [scholar](https://scholar.google.com/citations?user=KiNLNDgAAAAJ)
   ⚠ Evidence from 2024, not specifically about iterative development testing
5. **Victor C. Dibia** — industry, Microsoft Research (US) · score 0.51 · fit: moderate
   Co-authored AutoGen Studio papers; research interests include AI agents and developer tools.
   Evidence: [AUTOGEN STUDIO: A No-Code Developer Tool for Building and Debugging Mu](https://doi.org/10.18653/v1/2024.emnlp-demo.8) (2024) · [AutoGen Studio: A No-Code Developer Tool for Building and Debugging Mu](https://doi.org/10.48550/arxiv.2408.15247) (2024)
   [openalex](https://openalex.org/A5047676499) · [orcid](https://orcid.org/0000-0002-1839-5632) · [scholar](https://scholar.google.com/citations?user=CHloX8EAAAAJ)
   ⚠ Evidence from 2024, not specifically about iterative development testing

<sub>27 candidates found · 1 passed the checks · 26 removed</sub>

## W10.L1 · Week 10 · Testing and validation in iterative development ★ new at IIIT-D
*A 1.5-hour lecture in week 10 on “Testing and validation in iterative development”, part of the module “Diagnostic Log Analysis and Software Factories”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Analyze execution traces produced by coding agents during iterative loop engineering tasks, for a supplied log file of at most 2000 lines, identifying at least three distinct failure causes with supporting log evidence (analyse). This serves CO3: Analyze the execution traces produced by coding agents during iterative loop engineering tasks, identifying at least three distinct … Students come in knowing Software factories and execution trace analysis. It has a hands-on part (Trace analysis lab in week 9; Testing pipeline lab in week 10). The topic continues in the next lecture. Assessed in LabEval1 (week 12), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:20). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Log parsing and query techniques** — Students practice using grep, jq, and awk to filter a 2000-line trace for specific event types, extract timestamps, and count occurrences of error codes. They l | 15 | NotebookLM video (`notebooklm/W10.L1.md`) |
| C2 | **Systematic trace analysis workflow** — A step‑by‑step method is introduced: (1) segment the trace by iteration, (2) hypothesize failure categories, (3) search for signature patterns, (4) collect supp | 15 | NotebookLM video (`notebooklm/W10.L1.md`) |
| C3 | **Worked example: multi-failure trace analysis** — The instructor analyses a full 2000-line trace containing three distinct failures: a permission error, a version mismatch, and a logic loop. For each failure, t | 15 | NotebookLM video (`notebooklm/W10.L1.md`) |
| C4 | **Activity: pair analysis of new trace** — In pairs, students receive a fresh 1500-line trace and must identify at least three failure causes, citing line numbers and error codes. They prepare a brief re | 15 | in class (activity) |
| C5 | **Comparison of analysis strategies** — Students compare manual trace inspection, scripted querying, and LLM‑assisted summarisation. They evaluate speed, accuracy, and false‑positive rates on the same | 15 | NotebookLM video (`notebooklm/W10.L1.md`) |
| C6 | **Discussion: validation and reporting findings** — The class discusses how to validate identified causes (re‑run, unit test, stakeholder confirmation) and how to structure a concise failure report for developers | 15 | in class (discussion) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W10.L1.md`

**Readings**

1. [Chapter 6 - Testing and Iteration | AI in Production Guide](https://azure.github.io/AI-in-Production-Guide/chapters/chapter_06_testing_waters_testing_iteration) — score 0.61
   Covers: topic ✓, W10.L1.C1 ✗, W10.L1.C2 ✓, W10.L1.C3 ✗, W10.L1.C4 ✗, W10.L1.C5 ✗, W10.L1.C6 ✓ [from page text] · azure.github.io · tier 4
   *Review:* Excellent chapter on testing and iteration in AI projects; aligns well with iterative development testing. Use: before class.

**Possible guest speakers:** same topic as W09.L2; see its list and guest kit.

<sub>27 candidates found · 1 passed the checks · 26 removed</sub>

## W10.L2 · Week 10 · Automated testing and evaluation mechanisms ★ new at IIIT-D
*A 1.5-hour lecture in week 10 on “Automated testing and evaluation mechanisms”, part of the module “Automated Testing and Evaluation Metrics”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Compare automated testing mechanisms and evaluation metrics for AI-native software architectures (understand). This serves CO4: Assess automated testing and evaluation pipelines for AI-native software factories, justifying each design decision against at least one … It prepares for Pipeline evaluation mechanisms and metrics (week 11), Reliable and safe trustworthy software architectures (week 11). The topic continues in the next lecture. Assessed in ProjMilestone (week 12), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:20). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **AI-native architectures and testing challenges** — Students will identify the distinctive characteristics of AI-native software (data‑driven behavior, non‑determinism, model drift) and explain why traditional te | 15 | [The agent evaluation revolution](https://www.youtube.com/watch?v=WZZLtwnZ4w0&t=83s) 1:23–3:45 (partly) + NotebookLM for: model drift; data-driven behavior; test oracle problem |
| C2 | **Unit testing mechanisms for ML models** — Students will describe property‑based testing, metamorphic testing, and model‑behavior contracts as unit‑level mechanisms for ML models. They will apply one mec | 15 | NotebookLM video (`notebooklm/W10.L2.md`) |
| C3 | **Integration testing for AI pipelines** — Students will explain contract testing, data‑drift detection, and end‑to‑end pipeline validation as integration mechanisms. They will compare how each mechanism | 15 | NotebookLM video (`notebooklm/W10.L2.md`) |
| C4 | **Model quality evaluation metrics** — Students will define accuracy, fairness, robustness, and calibration metrics and explain when each is appropriate for AI-native systems. They will compute a fai | 15 | [LLM Benchmarking | How one LLM is tested agai](https://www.youtube.com/watch?v=Pt-wu5BdflU&t=257s) 4:17–5:50 (partly) + NotebookLM for: fairness metric; robustness metric; calibration metric |
| C5 | **System-level evaluation metrics** — Students will describe latency, throughput, cost, and reliability metrics for deployed AI services. They will analyse a scenario to decide which system‑level me | 15 | NotebookLM video (`notebooklm/W10.L2.md`) |
| C6 | **Comparative framework for testing selection** — Students will use a decision matrix (mechanism vs. metric vs. risk) to compare and select appropriate testing mechanisms and evaluation metrics for a given AI-n | 15 | [LLM Evaluation Framework Explained | RAG Metr](https://www.youtube.com/watch?v=TtkO3iFb8fQ&t=82s) 1:22–4:18 (partly) + NotebookLM for: decision matrix (mechanism vs metric vs risk); risk tolerance justification; resource constraints justification |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W10.L2.md`

**Videos**

1. [LLM Evaluation Framework Explained | RAG Metrics, AI Testing & Production Monitoring](https://www.youtube.com/watch?v=TtkO3iFb8fQ) — score 0.21
   Teaches C6 Comparative framework for testing selection (1:22–4:18, partly) [checked on the transcript] · Micro Learning · tier 4 · 8:13 · 51 views
   *Review:* Presents model selection framework and RAG/agent metrics; lacks decision matrix for testing mechanisms. Use: in-class clip.
2. [The agent evaluation revolution](https://www.youtube.com/watch?v=WZZLtwnZ4w0) — score 0.25
   Teaches C1 AI-native architectures and testing challenges (1:23–3:45, partly) [checked on the transcript] · Google Cloud Tech · tier 2 · 8:32 · 31,966 views
   *Review:* Clear explanation of why traditional deterministic testing fails for autonomous agents, but missing specific concepts like model drift. Use: in-class clip.
3. [LLM Benchmarking | How one LLM is tested against another? | LLM Evaluation Benchmarks | Simplilearn](https://www.youtube.com/watch?v=Pt-wu5BdflU) — score 0.19
   Teaches C4 Model quality evaluation metrics (4:17–5:50, partly) [checked on the transcript] · Simplilearn · tier 4 · 9:19 · 3,306 views
   *Review:* Lists standard accuracy and NLP metrics, but completely omits fairness, robustness, calibration, and confusion matrix calculations. Use: in-class clip.

**Readings**

1. [How to Approach LLM Evaluation for AI-Native Applications | Improving](https://www.improving.com/thoughts/llm-evaluation-ai-native-applications/) — score 0.69
   Covers: topic ✓, W10.L2.C1 ✓, W10.L2.C2 ✗, W10.L2.C3 ✓, W10.L2.C4 ✓, W10.L2.C5 ✓, W10.L2.C6 ✓ [from page text] · improving.com · tier 4
   *Review:* Good overview of LLM evaluation approaches and common pitfalls; lacks depth on unit testing and concrete examples. Use: before class.

**Possible guest speakers** (guest kit: `guest_kits/W10.L2.md`)

1. **Cuiyun Gao** — researcher, Chinese University of Hong Kong (HK) · score 0.65 · fit: strong
   2025 top-venue paper on LLM-as-a-judge for SE evaluation, directly addresses automated evaluation mechanisms.
   Evidence: [Can LLMs Replace Human Evaluators? An Empirical Study of LLM-as-a-Judg](https://doi.org/10.1145/3728963) (2025)
   [openalex](https://openalex.org/A5061699251) · [orcid](https://orcid.org/0000-0003-4774-2434) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Cuiyun+Gao+Chinese+University+of+Hong+Kong)

<sub>30 candidates found · 1 passed the checks · 29 removed</sub>

## W11.L1 · Week 11 · Automated testing and evaluation mechanisms ★ new at IIIT-D
*A 0.25-hour lecture in week 11 on “Automated testing and evaluation mechanisms”, part of the module “Automated Testing and Evaluation Metrics”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Compare automated testing mechanisms and evaluation metrics for AI-native software architectures (understand). This serves CO4: Assess automated testing and evaluation pipelines for AI-native software factories, justifying each design decision against at least one … It prepares for Pipeline evaluation mechanisms and metrics (week 11), Reliable and safe trustworthy software architectures (week 11). The topic continues in the next lecture. Assessed in ProjMilestone (week 12), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:20). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Case study: applying comparison framework** — Students will walk through a realistic AI‑native service (e.g., a recommendation API) and apply the comparative framework to choose testing mechanisms and metri | 15 | NotebookLM video (`notebooklm/W11.L1.md`) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W11.L1.md`

**Readings**

1. [Evaluation of an Automated Testing Framework: A Case Study](https://www.scielo.sa.cr/scielo.php?script=sci_arttext&pid=S0379-39822020000300003) — score 0.70
   Covers: topic ✓, W11.L1.C1 ✓ [from page text] · scielo.sa.cr · tier 4
   *Review:* Case study evaluating a mobile testing framework with confusion matrix metrics; useful for evaluation mechanisms but not AI-native specific. Use: in-class clip.
2. [A Small Case Study in Test Automation (and other things) – The Shade Tree Developer](https://jeremydmiller.com/2020/05/06/a-small-case-study-in-test-automation-and-other-things/) — score 0.65
   Covers: topic ✓, W11.L1.C1 ✗ [from page text] · jeremydmiller.com · tier 4
   *Review:* Practical case study on test automation strategy and data setup; lacks AI-native context and evaluation metrics comparison. Use: in-class clip.

**Possible guest speakers:** same topic as W10.L2; see its list and guest kit.

<sub>27 candidates found · 3 passed the checks · 24 removed</sub>

## W11.L2 · Week 11 · Pipeline evaluation mechanisms and metrics ★ new at IIIT-D
*A 1.75-hour lecture in week 11 on “Pipeline evaluation mechanisms and metrics”, part of the module “Automated Testing and Evaluation Metrics”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Compare automated testing mechanisms and evaluation metrics for AI-native software architectures (understand). This serves CO4: Assess automated testing and evaluation pipelines for AI-native software factories, justifying each design decision against at least one … Students come in knowing Automated testing and evaluation mechanisms. Assessed in ProjMilestone (week 12), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:14). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **AI-Native Testing Landscape Overview** — Students will identify the unique challenges of testing AI-native systems, including nondeterminism, data drift, and model versioning. They will distinguish bet | 15 | NotebookLM video (`notebooklm/W11.L2.md`) |
| C2 | **Unit Testing ML Model Components** — Students will describe unit-level testing mechanisms such as property-based testing, metamorphic testing, and test oracle construction for individual model func | 15 | NotebookLM video (`notebooklm/W11.L2.md`) |
| C3 | **Integration Testing of ML Pipelines** — Students will outline integration testing strategies for end-to-end ML pipelines, including contract testing, schema validation, and pipeline replay. They will  | 15 | NotebookLM video (`notebooklm/W11.L2.md`) |
| C4 | **Model Performance Evaluation Metrics** — Students will define key model-centric metrics such as accuracy, F1, AUC, calibration error, and perplexity, and explain when each is appropriate. They will int | 15 | NotebookLM video (`notebooklm/W11.L2.md`) |
| C5 | **System-Level Quality Metrics** — Students will describe system-level metrics including latency, throughput, memory footprint, robustness to adversarial inputs, and data freshness. They will rel | 15 | NotebookLM video (`notebooklm/W11.L2.md`) |
| C6 | **Mapping Mechanisms to Metrics** — Students will apply a comparative framework that links each testing mechanism to the metrics it informs, highlighting coverage gaps. They will evaluate which co | 15 | NotebookLM video (`notebooklm/W11.L2.md`) |
| C7 | **Case Study: RAG Pipeline Evaluation** — Students will walk through a retrieval-augmented generation pipeline, applying unit, integration, and system tests, and compute model and system metrics. They w | 15 | [Why Your AI Application Needs Multiple Eval P](https://www.youtube.com/watch?v=DcZ-XCk-O_M&t=209s) 3:29–4:52 (partly) + NotebookLM for: Unit, integration, and system testing execution; Calculating model and system metrics; Critiquing an evaluation plan |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W11.L2.md`

**Videos**

1. [Why Your AI Application Needs Multiple Eval Pipelines? | CampusX](https://www.youtube.com/watch?v=DcZ-XCk-O_M) — score 0.24
   Teaches C7 Case Study: RAG Pipeline Evaluation (3:29–4:52, partly) [checked on the transcript] · CampusX · tier 4 · 28:06 · 37,318 views
   *Review:* Explains RAG chatbot architecture and motivates multi-pipeline component testing, but cuts off before testing details. Use: in-class clip.

**Readings**

1. [Towards More Standardized AI Evaluation:From Models to Agents](https://arxiv.org/html/2602.18029v1) — score 0.68
   Covers: topic ✓, W11.L2.C1 ✓, W11.L2.C2 ✗, W11.L2.C3 ✗, W11.L2.C4 ✓, W11.L2.C5 ✓, W11.L2.C6 ✓, W11.L2.C7 ✓ [from page text] · arxiv.org · tier 2
   *Review:* Useful conceptual framing of evaluation pipelines, methodological pillars, benchmark lifecycle, and limits of generic metrics. The excerpts lack a complete worked example and omit unit- and integration-level testing. Use: your preparation.
2. [How to build reliable evaluation pipelines for AI systems | Growthbook](https://www.growthbook.io/insights/how-build-reliable-evaluation-pipelines-ai-systems) — score 0.67
   Covers: topic ✓, W11.L2.C1 ✓, W11.L2.C2 ✗, W11.L2.C3 ✓, W11.L2.C4 ✓, W11.L2.C5 ✓, W11.L2.C6 ✓, W11.L2.C7 ✓ [from page text] · growthbook.io · tier 4
   *Review:* Strong explanation of layered metrics, failure-mode visibility, and data architecture for reliable AI evaluation. Useful for connecting mechanisms to operational metrics, though excerpts show few concrete worked examples. Use: before class.

**Possible guest speakers** (guest kit: `guest_kits/W11.L2.md`)

1. **Pankaj Jalote** — IIIT-D faculty, IIIT-Delhi (IN) · score 0.76 · fit: strong
   Teaches AI in Software Engineering (2026) and published on automated test case design using ChatGPT (2024), relevant to pipeline evaluation mechanisms.
   Evidence: [Teaches CSE701 Topics in Software Engineering: AI in SE at IIIT-D](https://techtree.iiitd.edu.in/viewDescription/filename?=CSE701) (2026) · [Teaches CSE583 Software Development using Open Source at IIIT-D](https://techtree.iiitd.edu.in/viewDescription/filename?=CSE583) (2026)
   [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Pankaj+Jalote+IIIT+Delhi) · [openalex](https://openalex.org/A5057154526) · [orcid](https://orcid.org/0009-0001-8552-8394)
2. **Riddam Jain** — Staff Engineer, — · score 0.64 · fit: moderate
   Talk on MLOps & AI Production Operations (2026) covers pipeline evaluation mechanisms and metrics for AI-native architectures.
   Evidence: [MLOps & AI Production Operations: The 2026 Guide · Riddam Jain](https://riddam.github.io/guides/mlops-production-guide/)
   [page](https://riddam.github.io/guides/mlops-production-guide/)
   ⚠ single talk, not sustained research
3. **Aditya Parameswaran** — researcher, Assoc. Prof, EECS, UC Berkeley & AI x Data Research Lead, Snowflake (US) · score 0.56 · fit: strong
   Published seminal papers on production ML pipelines (2021) and observability for ML pipelines (2021), directly relevant to pipeline evaluation mechanisms and metrics.
   Evidence: [Production Machine Learning Pipelines](https://doi.org/10.1145/3448016.3457566) (2021) · [Towards Observability for Machine Learning Pipelines](https://openalex.org/W3198313108) (2021)
   [openalex](https://openalex.org/A5013608601) · [orcid](https://orcid.org/0000-0002-4538-4752) · [scholar](https://scholar.google.com/citations?user=VeB3UbcAAAAJ)
   ⚠ papers from 2021, but still foundational
4. **Georgia Dede** — Assistant Professor, Harokopio University of Athens · score 0.49 · fit: moderate
   Co-authored multi-cloud pipeline evaluation framework (2026); research interests include evaluation of systems and decision support.
   Evidence: [Evaluation and Taxonomy Framework of Multi-Cloud Pipelines: An AI Case](https://ieeexplore.ieee.org/abstract/document/11679769/) (2026)
   [scholar](https://scholar.google.com/citations?user=x_MCOPUAAAAJ)
   ⚠ venue quality unknown; evaluation focus may be broader than automated testing
5. **Evangelia Filiopoulou** — Research Associate and Adjunct lecturer, Harokopio University of Athens · score 0.49 · fit: moderate
   Co-authored 2026 paper on evaluation framework for multi-cloud pipelines with AI case study.
   Evidence: [Evaluation and Taxonomy Framework of Multi-Cloud Pipelines: An AI Case](https://ieeexplore.ieee.org/abstract/document/11679769/) (2026)
   [scholar](https://scholar.google.com/citations?user=6R561xIAAAAJ)
   ⚠ primary research focus on cloud economics, not pipeline evaluation

<sub>29 candidates found · 4 passed the checks · 25 removed</sub>

## W11.L3 · Week 11 · Reliable and safe trustworthy software architectures
*A 1-hour lecture in week 11 on “Reliable and safe trustworthy software architectures”, part of the module “Reliable AI-Native Pipelines and Deployment”. A related topic (“reliable safe trustworthy”) is already taught at IIIT-D. By the end, students should be able to: Assess automated testing pipelines for AI-native software factories, for a supplied multi-component software project, justifying each design decision against at least one stated reliability requirement (evaluate). This serves CO4: Assess automated testing and evaluation pipelines for AI-native software factories, justifying each design decision against at least one … Students come in knowing Automated testing and evaluation mechanisms. It prepares for Deployment and reliability metric evaluation (week 12). It has a hands-on part (Reliability assessment lab in week 11). The topic continues in the next lecture. Assessed in ProjMilestone (week 12), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:14). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **AI-native factory pipeline architecture overview** — Students will understand the high-level structure of an AI-native software factory, identifying the major pipeline components such as data ingestion, model trai | 15 | [AI Harness Engineering Architecture Explained](https://www.youtube.com/watch?v=Zra5BsbyKCc&t=221s) 3:41–6:35 (partly) + NotebookLM for: data ingestion (explicit); model training; deployment |
| C2 | **Automated testing stages in AI pipelines** — Students will learn the concrete testing stages used in AI-native pipelines: unit tests for code, integration tests for data flows, model validation tests (accu | 15 | [🚀 System Design #01 | Introduction to System ](https://www.youtube.com/watch?v=CHROMBWqLM4&t=821s) 13:41–15:42 (partly) + NotebookLM for: model validation (accuracy, fairness); data drift detection; test tooling |
| C3 | **Mapping reliability requirements to pipeline stages** — Students will analyse a set of reliability requirements (e.g., reproducibility, latency, fault tolerance) and map each requirement to specific pipeline stages a | 15 | NotebookLM video (`notebooklm/W11.L3.md`) |
| C4 | **Worked example: assessing sample pipeline reliability** — Through a guided walkthrough, students will evaluate a provided sample AI pipeline against a list of reliability requirements, justifying each assessment decisi | 15 | NotebookLM video (`notebooklm/W11.L3.md`) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W11.L3.md`

**Videos**

1. [AI Harness Engineering Architecture Explained](https://www.youtube.com/watch?v=Zra5BsbyKCc) — score 0.20
   Teaches C1 AI-native factory pipeline architecture overview (3:41–6:35, partly) [checked on the transcript] · AI & Systems Engineering · tier 4 · 6:34 · 44 views
   *Review:* Shows inference pipeline with validation and routing; omits training/deployment. Use: in-class clip.
2. [🚀 System Design #01 | Introduction to System Design for AI Product Engineering](https://www.youtube.com/watch?v=CHROMBWqLM4) — score 0.23
   Teaches C2 Automated testing stages in AI pipelines (13:41–15:42, partly) [checked on the transcript] · Raj Kamal · tier 4 · 1:18:20 · 377 views
   *Review:* Covers general testing phases; lacks AI-specific model validation and drift detection. Use: in-class clip.

<sub>12 candidates found · 0 passed the checks · 12 removed</sub>

## W12.L1 · Week 12 · Reliable and safe trustworthy software architectures
*A 1.5-hour lecture in week 12 on “Reliable and safe trustworthy software architectures”, part of the module “Reliable AI-Native Pipelines and Deployment”. A related topic (“reliable safe trustworthy”) is already taught at IIIT-D. By the end, students should be able to: Assess automated testing pipelines for AI-native software factories, for a supplied multi-component software project, justifying each design decision against at least one stated reliability requirement (evaluate). This serves CO4: Assess automated testing and evaluation pipelines for AI-native software factories, justifying each design decision against at least one … Students come in knowing Automated testing and evaluation mechanisms. It prepares for Deployment and reliability metric evaluation (week 12). It has a hands-on part (Reliability assessment lab in week 11). The topic continues in the next lecture. Assessed in ProjMilestone (week 12), Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:14). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Recap: pipeline assessment criteria discussion** — Students will briefly revisit the assessment criteria and reliability requirement mappings covered previously, clarifying any gaps through instructor-led discus | 10 | in class (discussion) |
| C2 | **Defining reliability requirements for multi-component AI** — Students will learn how to elicit and formalize reliability requirements for a system composed of multiple AI services (e.g., service-level objectives, error bu | 15 | [🚀 System Design #01 | Introduction to System ](https://www.youtube.com/watch?v=CHROMBWqLM4&t=444s) 7:24–10:24 (partly) + NotebookLM for: service-level objectives; error budgets; cascade failure policies |
| C3 | **Case study: industry AI pipeline reliability** — Students will examine a real-world case study of an AI-native pipeline in production, focusing on how the organization defined reliability requirements, instrum | 15 | NotebookLM video (`notebooklm/W12.L1.md`) |
| C4 | **Worked example: assessing supplied project pipeline** — The instructor demonstrates a full assessment of the supplied multi-component software project's testing pipeline, linking each design decision to a specific re | 20 | NotebookLM video (`notebooklm/W12.L1.md`) |
| C5 | **Group activity: assess pipeline and justify** — In small groups, students receive a different pipeline configuration for the same project and must assess it against the reliability requirements, producing a w | 20 | in class (activity) |
| C6 | **Trade-offs: testing depth vs deployment speed** — Students will compare the impact of increasing test coverage and rigor on deployment latency and resource consumption. They will evaluate scenarios where faster | 10 | NotebookLM video (`notebooklm/W12.L1.md`) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W12.L1.md`

**Videos**

1. [🚀 System Design #01 | Introduction to System Design for AI Product Engineering](https://www.youtube.com/watch?v=CHROMBWqLM4) — score 0.28
   Teaches C2 Defining reliability requirements for multi-component AI (7:24–10:24, partly) [checked on the transcript] · Raj Kamal · tier 4 · 1:18:20 · 377 views
   *Review:* Clear walkthrough of availability SLAs in general system design; lacks AI-specific reliability concepts. Use: in-class clip.

<sub>12 candidates found · 0 passed the checks · 12 removed</sub>

## W12.L2 · Week 12 · Deployment and reliability metric evaluation ★ new at IIIT-D
*A 1.5-hour lecture in week 12 on “Deployment and reliability metric evaluation”, part of the module “Reliable AI-Native Pipelines and Deployment”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Evaluate deployment and reliability metrics for a supplied multi-component software project, demonstrating live, with 2 scenario walkthroughs chosen by the evaluator (evaluate). This serves CO4: Assess automated testing and evaluation pipelines for AI-native software factories, justifying each design decision against at least one … Students come in knowing Reliable and safe trustworthy software architectures. It has a hands-on part (Deployment metrics lab in week 12; Final reliability lab in week 13). The topic continues in the next lecture. Assessed in Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:14). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Key deployment metrics overview** — Students learn the definitions of latency, error rate, throughput, deployment frequency, and rollback time. They understand how each metric signals the health o | 15 | [DevOps Metrics Explained | DORA Metrics Every](https://www.youtube.com/watch?v=bFzVrx8zyFY&t=0s) 0:00–4:39 (partly) + [DevOps Metrics](https://www.youtube.com/watch?v=yIB3bl9OGW0&t=0s) 0:00–4:27 (partly) + NotebookLM for: latency; error rate; throughput |
| C2 | **Reliability metrics and SLOs** — Students define availability, MTBF, MTTR, SLO, SLI, and error budget. They see how these metrics quantify system reliability and guide release decisions. | 15 | [DevOps Metrics That Matter | DORA, Reliabilit](https://www.youtube.com/watch?v=6dW7r7DyklY&t=110s) 1:50–6:50 (partly) + [DevOps Metrics](https://www.youtube.com/watch?v=yIB3bl9OGW0&t=226s) 3:46–7:43 (partly) + NotebookLM for: error budget; how metrics guide release decisions |
| C3 | **Instrumenting a multi-component system with OpenTelemetry** — Students follow the steps to add traces, metrics, and logs across services using OpenTelemetry SDKs. They configure exporters to Prometheus and verify that data | 15 | NotebookLM video (`notebooklm/W12.L2.md`) |
| C4 | **Live dashboard walkthrough with Grafana** — Students watch the creation of a Grafana dashboard that visualizes deployment and reliability metrics. They learn to set alert rules on error‑budget burn rate. | 15 | NotebookLM video (`notebooklm/W12.L2.md`) |
| C5 | **Scenario walkthrough 1: load‑test and failure injection** — The instructor runs a k6 load test against the sample project, injects a service failure with Chaos Mesh, and evaluates whether SLOs remain satisfied. Students  | 15 | NotebookLM video (`notebooklm/W12.L2.md`) |
| C6 | **Student activity: evaluate metrics on supplied project** — In pairs, students use the instrumented project to compute deployment and reliability metrics, decide if a release meets the defined SLOs, and present their go/ | 15 | in class (activity) |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W12.L2.md`

**Videos**

1. [DevOps Metrics](https://www.youtube.com/watch?v=yIB3bl9OGW0) — score 0.34
   Teaches C1 Key deployment metrics overview (0:00–4:27, partly); C2 Reliability metrics and SLOs (3:46–7:43, partly) [checked on the transcript] · AltexSoft · tier 4 · 10:36 · 4,820 views
   *Review:* Only covers deployment frequency; other four metrics not addressed.; Covers MTTF, MTTR, MTBF, availability with formulas; misses SLO, SLI, error budget. Use: in-class clip.
2. [DevOps Metrics That Matter | DORA, Reliability & Delivery Performance](https://www.youtube.com/watch?v=6dW7r7DyklY) — score 0.36
   Teaches C2 Reliability metrics and SLOs (1:50–6:50, partly) [checked on the transcript] · Joshua Moses | Cybertrace Foundation · tier 4 · 9:57 · 7 views
   *Review:* Introduces SLI/SLO with latency example; mentions MTTR earlier; misses availability, MTBF, error budget. Use: in-class clip.
3. [DevOps Metrics Explained | DORA Metrics Every Engineer Must Know](https://www.youtube.com/watch?v=bFzVrx8zyFY) — score 0.34
   Teaches C1 Key deployment metrics overview (0:00–4:39, partly) [checked on the transcript] · K4 Coding Academy · tier 4 · 7:50 · 338 views
   *Review:* Explains deployment frequency and MTTR well; omits latency, error rate, throughput. Use: in-class clip.

**Readings**

1. [Reliability Metrics: What to Track & How to Act On Them | Cortex](https://www.cortex.io/post/how-to-choose-your-software-reliability-metrics) — score 0.68
   Covers: topic ✓, W12.L2.C1 ✓, W12.L2.C2 ✓, W12.L2.C3 ✗, W12.L2.C4 ✓, W12.L2.C5 ✓, W12.L2.C6 ✓ [from page text] · cortex.io · tier 4
   *Review:* Good overview of reliability metric selection and actionability; lacks hands-on evaluation exercises. Use: before class.
2. [10 Software Quality Metrics that Matter | LANSA](https://lansa.com/blog/app-development/software-quality-metrics/) — score 0.63
   Covers: topic ✓, W12.L2.C1 ✓, W12.L2.C2 ✓, W12.L2.C3 ✗, W12.L2.C4 ✓, W12.L2.C5 ✗, W12.L2.C6 ✓ [from page text] · lansa.com · tier 4
   *Review:* Broad overview of software quality metrics including availability; not focused on deployment evaluation. Use: before class.

**Possible guest speakers** (guest kit: `guest_kits/W12.L2.md`)

1. **P. K. Kapur** — researcher, Amity University (IN) · score 0.58 · fit: moderate
   Publishes software reliability growth models (2023, 2012) but evidence is theoretical modeling, not hands-on deployment/reliability metric evaluation with scenario walkthroughs.
   Evidence: [Software Reliability Growth Model for N-Version Fault Tolerant Softwar](https://doi.org/10.1142/s0218539323500262) (2023) · [A SOFTWARE RELIABILITY GROWTH MODEL FOR VITAL QUALITY METRICS](https://doi.org/10.7166/18-2-121) (2012)
   [openalex](https://openalex.org/A5013827274) · [orcid](https://orcid.org/0000-0001-8006-5952) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=P.+K.+Kapur+Amity+University)
   ⚠ evidence focuses on reliability modeling not deployment metrics; no demonstrated live evaluation walkthroughs
2. **P. Dhavakumar** — researcher, Vellore Institute of Technology University (IN) · score 0.57 · fit: moderate
   Recent paper on Naive Bayes defect prediction for reliability (2024) and reliability growth model optimization (2020), but work is predictive modeling not live deployment metric evaluation.
   Evidence: [Enhancing Software Reliability through Naive Bayes-based Defect Predic](https://doi.org/10.21203/rs.3.rs-4268707/v1) (2024) · [An efficient parameter optimization of software reliability growth mod](https://doi.org/10.1007/s12652-020-02476-z) (2020)
   [openalex](https://openalex.org/A5035571245) · [orcid](https://orcid.org/0000-0001-8365-4234) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=P.+Dhavakumar+Vellore+Institute+of+Technology+University)
   ⚠ modeling-focused not hands-on evaluation; no deployment metrics evidence
3. **Anu G. Aggarwal** — researcher, University of Delhi (IN) · score 0.56 · fit: moderate
   Papers on testing coverage in reliability assessment (2023) and N-version fault tolerance (2023) show reliability modeling expertise, not deployment metric evaluation practice.
   Evidence: [Modeling the Role of Testing Coverage in the Software Reliability Asse](https://doi.org/10.33889/ijmems.2023.8.3.028) (2023) · [Software Reliability Growth Model for N-Version Fault Tolerant Softwar](https://doi.org/10.1142/s0218539323500262) (2023)
   [openalex](https://openalex.org/A5041713395) · [orcid](https://orcid.org/0000-0001-5448-9540) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Anu+G.+Aggarwal+University+of+Delhi)
   ⚠ academic modeling focus; no live scenario walkthrough evidence
4. **Ritu Gupta** — researcher, Manipal Academy of Higher Education (IN) · score 0.56 · fit: moderate
   Same 2023 papers on testing coverage and N-version reliability models; academic reliability modeling background, not deployment evaluation practice.
   Evidence: [Modeling the Role of Testing Coverage in the Software Reliability Asse](https://doi.org/10.33889/ijmems.2023.8.3.028) (2023) · [Software Reliability Growth Model for N-Version Fault Tolerant Softwar](https://doi.org/10.1142/s0218539323500262) (2023)
   [openalex](https://openalex.org/A5101647307) · [orcid](https://orcid.org/0000-0001-7949-4733) · [scholar search](https://scholar.google.com/citations?view_op=search_authors&mauthors=Ritu+Gupta+Manipal+Academy+of+Higher+Education)
   ⚠ identical evidence to x4/x6; modeling not hands-on evaluation

<sub>27 candidates found · 2 passed the checks · 25 removed</sub>

## W13.L1 · Week 13 · Deployment and reliability metric evaluation ★ new at IIIT-D
*A 0.5-hour lecture in week 13 on “Deployment and reliability metric evaluation”, part of the module “Reliable AI-Native Pipelines and Deployment”. No existing IIIT-D course teaches a close match, so this is likely new material to prepare. By the end, students should be able to: Evaluate deployment and reliability metrics for a supplied multi-component software project, demonstrating live, with 2 scenario walkthroughs chosen by the evaluator (evaluate). This serves CO4: Assess automated testing and evaluation pipelines for AI-native software factories, justifying each design decision against at least one … Students come in knowing Reliable and safe trustworthy software architectures. It has a hands-on part (Deployment metrics lab in week 12; Final reliability lab in week 13). The topic continues in the next lecture. Assessed in Endsem (week 13).*

> ⚠ **Partial:** YouTube blocked transcript requests (from 22:14). Videos were judged from their title and description only and no clips could be made; the next `recommend` run redoes this lecture.

**Lecture plan** (what each part teaches, for how long, and how it is delivered)

| # | Part | Min | Delivered by |
|---|---|---|---|
| C1 | **Comparing scenario walkthroughs: lessons learned** — A brief recap of the first walkthrough is followed by a comparison with a second scenario (canary vs. blue‑green). Students analyse how metric patterns differ a | 15 | NotebookLM video (`notebooklm/W13.L1.md`) |
| C2 | **Scenario walkthrough 2: canary deployment evaluation** — The instructor demonstrates a live canary rollout, monitors the error budget in Grafana, makes a go/no‑go decision, and documents the evaluation for a post‑mort | 15 | [Module 10: Optimizing Delivery Metrics & Depl](https://www.youtube.com/watch?v=LiaBWWsplRI&t=68s) 1:08–6:08 (partly) + NotebookLM for: error budget monitoring in Grafana; go/no-go decision process; post-mortem documentation |

NotebookLM pack (sources, prompts for the missing videos, quiz, flashcards): `notebooklm/W13.L1.md`

**Videos**

1. [Module 10: Optimizing Delivery Metrics & Deployment Queries | AZ-400 Certification | English](https://www.youtube.com/watch?v=LiaBWWsplRI) — score 0.26
   Teaches C2 Scenario walkthrough 2: canary deployment evaluation (1:08–6:08, partly) [checked on the transcript] · QuickTechie Official · tier 4 · 7:16 · 9 views
   *Review:* Explains canary theory and metrics but lacks live demo, error budget, go/no-go, post-mortem. Use: in-class clip.

**Readings**

1. [Google SRE - Canary Release: Deployment Safety and Efficiency](https://sre.google/workbook/canarying-releases/) — score 0.76
   Covers: topic ✓, W13.L1.C1 ✓, W13.L1.C2 ✓ [from page text] · sre.google · tier 4
   *Review:* Authoritative Google SRE guide on canary evaluation with error budgets and SLOs; directly supports scenario walkthrough 2. Use: in-class clip.
2. [Deployment Strategies: 7 Methods for Successful Releases](https://www.enov8.com/blog/deployment-strategies-compared-and-explained/) — score 0.66
   Covers: topic ✓, W13.L1.C1 ✓, W13.L1.C2 ✓ [from page text] · enov8.com · tier 4
   *Review:* Clear article on deployment strategies (blue-green, canary); good for background but doesn't cover metric evaluation. Use: before class.
   ⚠ AI review: mentions the topic but does not really teach it

**Possible guest speakers:** same topic as W12.L2; see its list and guest kit.

<sub>27 candidates found · 3 passed the checks · 24 removed</sub>
