# CS601 (Software Development using AI): YouTube lecture playlists for the first 6 lectures

Delivery mode 2: each lecture is taught entirely by the clips below, in order. Times are start → end in the source video.
`check`: **transcript** = content and boundaries read in the captions (about ±10 s); **browser-tx** = read via the YouTube page's transcript panel; **chapters** = uploader chapters only, so preview before class.
The embed links play exactly the clip (`start`/`end` parameters).

## W01.L1: Developer workflows and AI-assisted coding
*CO1.LO3 (BL1): identify the core components of developer workflows and AI-assisted coding*  ·  slot 120 min  ·  **video 1:32:25** (77% of the slot; the rest is for questions, a quiz or the lab)

**1. Why software development is changing: Software 1.0 → 2.0 → 3.0, LLMs as a new kind of computer** (9:39)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [1:25–11:04](https://www.youtube.com/watch?v=LCEmiRjPEtQ&t=85s) | Andrej Karpathy: Software Is Changing (Again) (Y Combinator, 2025) | 9:39 | transcript | Karpathy's Software 1.0/2.0/3.0 framing and 'LLMs as utilities, fabs and operating systems': the clearest big-picture opening for students who know only classical programming. |

**2. Partial autonomy: humans and AI in a generate–verify loop** (10:44)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [18:22–29:06](https://www.youtube.com/watch?v=LCEmiRjPEtQ&t=1102s) | Andrej Karpathy: Software Is Changing (Again) (Y Combinator, 2025) | 10:44 | transcript | Partial-autonomy apps, the generate/verify loop, the 'autonomy slider' and the Iron-Man-suit analogy. This is the mental model for every workflow later in the course. |

**3. From autocomplete to coding agents: a first live demo** (11:37)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:00–11:37](https://www.youtube.com/watch?v=sTdz6PZoAnw&t=0s) | Lecture 7: Agentic Coding (Missing Semester, 2026) | 11:37 | transcript | MIT Missing Semester (2026), a university lecture at exactly this level. The spectrum from autocomplete and inline chat to agents, a live Claude Code task, permissions, iterating, interrupting, and the TDD question. |

**4. Where AI fits in the software lifecycle (and why coding speed alone does not help)** (9:05)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:00–9:05](https://www.youtube.com/watch?v=4wMRXmLpdA8&t=0s) | AI in the SDLC: Rethinking AI Coding Tools & AI Agents (IBM Technology, 2026) | 9:05 | transcript | IBM Technology: AI in each SDLC phase; over- and under-delegation; specs and harness. It is short, whiteboard style, and maps directly to 'components of a workflow'. |

**5. Vibe coding vs spec-driven development vs agentic engineering** (16:48)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:00–8:50](https://www.youtube.com/watch?v=mViFYTwWvcM&t=0s) | Spec-Driven Development: AI Assisted Coding Explained (IBM Technology, 2026) | 8:50 | transcript | IBM Technology: vibe coding vs spec-driven development, with the reversed workflow (spec → design → code) shown on a whiteboard. |
| [15:46–23:44](https://www.youtube.com/watch?v=96jN2OCOfLs&t=946s) | Andrej Karpathy: From Vibe Coding to Agentic Engineering w/ Stephanie  (Sequoia Capital, 2026) | 7:58 | transcript | Karpathy (Sequoia, 2026): agentic engineering preserves the professional quality bar, and the human owns taste, design and oversight. A strong contrast with vibe coding. |

**6. Everyday workflow uses: bug-fixing with tests, code review, codebase understanding, the agent as a shell (plus privacy)** (19:06)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [26:44–41:43](https://www.youtube.com/watch?v=sTdz6PZoAnw&t=1604s) | Lecture 7: Agentic Coding (Missing Semester, 2026) | 14:59 | transcript | Missing Semester: privacy note, then worked use cases (write a failing test → agent fixes → runs the suite → commits in the repo's style, review, onboarding, shell, vibe coding). |
| [6:27–10:34](https://www.youtube.com/watch?v=gv0WHhKelSE&t=387s) | Claude Code best practices | Code w/ Claude (Anthropic, 2025) | 4:07 | browser-tx | Anthropic's Cal Rueb: the use cases across the lifecycle (discovery, design, build, deploy, support, migrations). |

**7. Verifying and reviewing AI-written code: who is accountable** (15:26)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [2:34–16:20](https://www.youtube.com/watch?v=b2QkhmQ0sT0&t=154s) | How I Review AI Code - (Meta Senior Staff Engineer) (John Kim, 2026) | 13:46 | transcript | A Meta senior staff engineer on reviewing AI code: review as a gradient, blast radius, feature gates, requiring proof in PRs, leaf vs trunk code, independent agent reviews. |
| [58:40–1:00:20](https://www.youtube.com/watch?v=sTdz6PZoAnw&t=3520s) | Lecture 7: Agentic Coding (Missing Semester, 2026) | 1:40 | transcript | Missing Semester's closing caveats: subtly wrong code, debugging spirals, why your own CS skills still matter. |

## W01.L2: Model Context Protocol and architecture (part 1 of 2)
*CO1.LO1 (BL1): identify the configuration schema and protocol requirements for MCP*  ·  slot 60 min  ·  **video 49:26** (82% of the slot; the rest is for questions, a quiz or the lab)

**1. The integration problem: N models × M data sources, and what MCP is** (7:18)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:00–7:18](https://www.youtube.com/watch?v=oblaHqULUHk&t=0s) | MCP Explained Simply — What It Is and Why It Exists (TechWorld with Nana, 2026) | 7:18 | transcript | TechWorld with Nana: a backend engineer's motivating scenario (chatbot × databases → 8 custom integrations), why LLMs need LLM-friendly responses, and that MCP does not replace APIs. The best beginner framing found. |

**2. Why Anthropic built MCP, from the source (LSP inspiration, value for each party)** (8:43)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:56–9:39](https://www.youtube.com/watch?v=kQmXtrmQ5Zg&t=56s) | Building Agents with Model Context Protocol - Full Workshop with Mahes (AI Engineer, 2025) | 8:43 | transcript | Mahesh Murag (Anthropic) at AI Engineer Summit: the motivation, the Language Server Protocol analogy, fragmentation, and what clients, servers and enterprises each gain. |

**3. Architecture: host, client and server, and who calls whom** (8:28)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [7:18–11:01](https://www.youtube.com/watch?v=oblaHqULUHk&t=438s) | MCP Explained Simply — What It Is and Why It Exists (TechWorld with Nana, 2026) | 3:43 | transcript | Tools as functions on a server; runtime discovery ('give me all your tools'); the LLM proposes and the application orchestrates. |
| [20:56–25:41](https://www.youtube.com/watch?v=oblaHqULUHk&t=1256s) | MCP Explained Simply — What It Is and Why It Exists (TechWorld with Nana, 2026) | 4:45 | transcript | The architecture walked through on one example: the MCP server wraps the database, the host owns the MCP client, and the LLM never opens connections itself. |

**4. The three server primitives: tools, resources, prompts** (7:17)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:35–3:13](https://www.youtube.com/watch?v=CQywdSdi5iA&t=35s) | The Model Context Protocol (MCP) (Anthropic, 2025) | 2:38 | transcript | MCP co-creator David Soria Parra (Anthropic): tools, resources and prompts in one breath, with prompts as slash commands. |
| [9:39–14:18](https://www.youtube.com/watch?v=kQmXtrmQ5Zg&t=579s) | Building Agents with Model Context Protocol - Full Workshop with Mahes (AI Engineer, 2025) | 4:39 | transcript | Mahesh: the same primitives classified by who controls them (model-controlled tools, application-controlled resources, user-controlled prompts), with Claude Desktop examples. |

**5. The protocol itself: JSON-RPC 2.0 messages and components** (6:38)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [13:12–19:50](https://www.youtube.com/watch?v=RhTiAOGwbYE&t=792s) | MCP Tutorial: Build Your First MCP Server and Client from Scratch (Fre (KodeKloud, 2025) | 6:38 | chapters | KodeKloud: component breakdown, architecture and JSON-RPC 2.0 message format (chapters 'Components', 'Architecture', 'Protocol – JSON-RPC 2.0'). |

**6. Transports: stdio for local, Streamable HTTP for remote** (4:32)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [2:17–6:49](https://www.youtube.com/watch?v=sNFcx-jUnvg&t=137s) | MCP Course #10 - Visual Overview of MCP Streamable HTTP Server & Clien (theailanguage, 2025) | 4:32 | transcript | theailanguage: what Streamable HTTP is, the client–server sequence diagram, and the five lifecycle components (part 2 continues the lifecycle). |

**7. What people build with MCP (use cases)** (6:30)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:00–6:30](https://www.youtube.com/watch?v=uBL0siiliGo&t=0s) | Model Context Protocol: A Deep Dive into the future of AI systems (Gaurav Sen, 2025) | 6:30 | transcript | Gaurav Sen: compact use cases (SEO, RAG, apps) that consolidate the idea before part 2. |

## W02.L1: Model Context Protocol and architecture (part 2 of 2)
*CO1.LO1 (BL1), continued: protocol requirements, configuration schema, security*  ·  slot 120 min  ·  **video 1:34:23** (79% of the slot; the rest is for questions, a quiz or the lab)

**1. The primitives in depth, from the protocol's co-creator (prompts, resources, tools, sampling, roots, completions)** (17:17)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:13–17:30](https://www.youtube.com/watch?v=HNzH5Us1Rvg&t=13s) | MCP 201 | Code w/ Claude (Anthropic, 2025) | 17:17 | transcript | 'MCP 201' (Anthropic, Code w/ Claude): each primitive with a live example, the interaction model, then sampling (the server asks the client's model), roots and completions. This is the authoritative deep dive. |

**2. Tools vs resources vs prompts on one worked scenario** (12:48)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [5:57–18:45](https://www.youtube.com/watch?v=XXh-lrWTMeQ&t=357s) | MCP | Tools, Resources, Prompts | Do you know the difference? (J-HAYER, 2025) | 12:48 | transcript | A single support-desk scenario: a database as tools, log files as resources, response templates as prompts. Students see when to use which. |

**3. Connection lifecycle: initialisation and capability negotiation, requests, notifications, sessions** (8:50)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [6:00–14:50](https://www.youtube.com/watch?v=sNFcx-jUnvg&t=360s) | MCP Course #10 - Visual Overview of MCP Streamable HTTP Server & Clien (theailanguage, 2025) | 8:50 | transcript | Sequence-diagram walk-through: initialise → requests → notifications → server-sent messages → session ids, the protocol requirements of LO1. |

**4. The configuration schema: how a host is told about servers** (21:23)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [4:59–10:28](https://www.youtube.com/watch?v=-8k9lGpGQ6g&t=299s) | Build Anything With a CUSTOM MCP Server - Python Tutorial (Tech With Tim, 2025) | 5:29 | chapters | Tech With Tim: registering a server in Claude Desktop's JSON config, plus common configuration errors and fixes. |
| [0:20–2:23](https://www.youtube.com/watch?v=vUQfqW5GKAQ&t=20s) | MCP Servers in VS Code and GitHub Copilot (Visual Studio Code, 2025) | 2:03 | chapters | VS Code (official): installing the GitHub MCP server into a VS Code/Copilot workspace. |
| [0:00–13:51](https://www.youtube.com/watch?v=X7lgIa6guKg&t=0s) | Claude Code Tutorial #7 - MCP Servers (Net Ninja, 2025) | 13:51 | chapters | Net Ninja: adding MCP servers to Claude Code (scopes, project config). Whole video; content not read, so preview it. |

**5. Remote servers and authorization (OAuth 2.1)** (17:51)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [17:30–24:02](https://www.youtube.com/watch?v=HNzH5Us1Rvg&t=1050s) | MCP 201 | Code w/ Claude (Anthropic, 2025) | 6:32 | transcript | MCP 201: moving from local servers to remote ones over Streamable HTTP, and why authorization is OAuth 2.1. |
| [2:47–14:06](https://www.youtube.com/watch?v=mYKMwZcGynw&t=167s) | [Session] Intro to OAuth for MCP Servers with Aaron Parecki, Okta (Agentic AI Foundation, 2025) | 11:19 | transcript | Aaron Parecki (Okta, OAuth spec editor): OAuth from first principles (hotel key-card analogy), then the MCP auth flow: discovery, metadata, dynamic client registration. |

**6. Security, access control and production concerns** (7:39)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [11:01–14:43](https://www.youtube.com/watch?v=oblaHqULUHk&t=661s) | MCP Explained Simply — What It Is and Why It Exists (TechWorld with Nana, 2026) | 3:42 | transcript | Secrets stay in the server, never in the LLM; access control at the server. |
| [25:41–29:38](https://www.youtube.com/watch?v=oblaHqULUHk&t=1541s) | MCP Explained Simply — What It Is and Why It Exists (TechWorld with Nana, 2026) | 3:57 | transcript | Reference vs enterprise servers, tool-count limits, server-side policies. |

**7. Where MCP is going (and advice for server authors)** (8:35)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [5:07–13:42](https://www.youtube.com/watch?v=v3Fr2JR47KA&t=307s) | The Future of MCP — David Soria Parra, Anthropic (AI Engineer, 2026) | 8:35 | chapters | David Soria Parra (2026): skills + MCP + CLI as the connectivity stack, progressive discovery, programmatic tool calling, best practices for server authors (chapters; this talk's transcript was fetched but only skimmed). |

## W02.L2: Coding agents and context engineering (part 1 of 2): how coding agents work
*CO1.LO2 (BL3), groundwork: what a coding agent is made of*  ·  slot 60 min  ·  **video 43:33** (73% of the slot; the rest is for questions, a quiz or the lab)

**1. What an agent is (and when not to build one)** (13:44)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:55–14:39](https://www.youtube.com/watch?v=D7_ipDqhtwk&t=55s) | How We Build Effective Agents: Barry Zhang, Anthropic (AI Engineer, 2025) | 13:44 | transcript | Barry Zhang (Anthropic) 'How we build effective agents': workflows vs agents, a checklist for when to use an agent, keep it simple (environment + tools + prompt in a loop), think from the agent's context window. |

**2. Under the hood: LLM → chat → tool calls → the agent harness loop** (15:07)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [11:37–26:44](https://www.youtube.com/watch?v=sTdz6PZoAnw&t=697s) | Lecture 7: Agentic Coding (Missing Semester, 2026) | 15:07 | transcript | Missing Semester: the LLM as a conditional distribution, how multi-turn chat is built, tool calls, the harness loop, then the opening demo replayed step by step. The best 'from first principles' segment found. |

**3. A real coding agent's design: a pure agent, agentic search, permissions** (3:11)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [3:16–6:27](https://www.youtube.com/watch?v=gv0WHhKelSE&t=196s) | Claude Code best practices | Code w/ Claude (Anthropic, 2025) | 3:11 | browser-tx | Anthropic: Claude Code is 'tools + model in a loop'; agentic search (grep/glob) instead of indexing the repository; the permission system. |

**4. Inside a production agent: one while-loop, the core tools, to-do lists** (11:31)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [7:54–19:25](https://www.youtube.com/watch?v=RFKCzGlAU6Q&t=474s) | How Claude Code Works - Jared Zoneraich, PromptLayer (AI Engineer, 2025) | 11:31 | transcript | PromptLayer's Jared Zoneraich, 'How Claude Code works': less scaffolding, more model; the core tools (bash, grep, edit); why to-do lists keep long tasks on track. |

## W03.L1: Coding agents and context engineering (part 2 of 2): context engineering
*CO1.LO2 (BL3): configure what goes into the agent's context*  ·  slot 60 min  ·  **video 54:59** (92% of the slot; the rest is for questions, a quiz or the lab)

**1. What context engineering is: write, select, compress, isolate** (14:05)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:00–14:05](https://www.youtube.com/watch?v=4GiqzUHD5AA&t=0s) | Context Engineering for Agents (LangChain, 2025) | 14:05 | transcript | Lance Martin (LangChain): the four strategies with examples from Claude Code, Cursor and ChatGPT memory. It stops before the framework-specific LangGraph section. |

**2. Why more context can make agents worse: context rot and four failure modes** (10:21)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [0:00–10:21](https://www.youtube.com/watch?v=BwXremQ-i6I&t=0s) | Context Engineering for AI Agents: 4 Failure Modes to Avoid (IBM Technology, 2026) | 10:21 | chapters | IBM Technology: context rot, poisoning, distraction, confusion and clash, then the fixes (validate, compact, curate, prune). Whole video, chapters only. |

**3. Context tools in coding agents: clear, rewind, compaction, llms.txt, AGENTS.md/CLAUDE.md, skills, subagents** (11:15)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [46:15–57:30](https://www.youtube.com/watch?v=sTdz6PZoAnw&t=2775s) | Lecture 7: Agentic Coding (Missing Semester, 2026) | 11:15 | transcript | Missing Semester: each context-management feature explained with the reason it exists. |

**4. Configuring an agent workspace in practice** (7:32)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [10:34–18:06](https://www.youtube.com/watch?v=gv0WHhKelSE&t=634s) | Claude Code best practices | Code w/ Claude (Anthropic, 2025) | 7:32 | browser-tx | Anthropic: CLAUDE.md, permission settings, CLI tools vs MCP servers, /clear vs /compact, plan first, TDD, multiple agents, Esc to steer. This is the 'configure' half of LO2. |

**5. Advanced: the smart zone, research → plan → implement, intentional compaction** (11:46)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [3:05–8:30](https://www.youtube.com/watch?v=rmvDxxNubIg&t=185s) | No Vibes Allowed: Solving Hard Problems in Complex Codebases – Dex Hor (AI Engineer, 2025) | 5:25 | transcript | Dex Horthy (who popularised 'context engineering'): the dumb zone, what compaction keeps, subagents for context control, research prompts. |
| [12:14–18:35](https://www.youtube.com/watch?v=rmvDxxNubIg&t=734s) | No Vibes Allowed: Solving Hard Problems in Complex Codebases – Dex Hor (AI Engineer, 2025) | 6:21 | transcript | On-demand compressed context; research → plan → implement; why humans must read the plan. |

## W03.L2: Custom tool integrations using MCP (hands-on)
*CO1.LO2 (BL3): configure custom tool integrations in agent workspaces using MCP*  ·  slot 120 min  ·  **video 1:18:17** (65% of the slot; the rest is for questions, a quiz or the lab)

**1. Use an existing server, build a server, build a client: the whole loop once** (20:24)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [19:50–40:14](https://www.youtube.com/watch?v=RhTiAOGwbYE&t=1190s) | MCP Tutorial: Build Your First MCP Server and Client from Scratch (Fre (KodeKloud, 2025) | 20:24 | chapters | KodeKloud: demo of using an existing server, building a server, building a client (with free labs that pair well with the lab session). |

**2. Building a Python MCP server with FastMCP: tools, resources, prompts** (17:33)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [3:10–20:43](https://www.youtube.com/watch?v=rnljvmHorQw&t=190s) | FastMCP — the best way to build an MCP server with Python (ZazenCodes, 2025) | 17:33 | chapters | ZazenCodes: the FastMCP library, project layout, running the server, connecting it to Claude Desktop, adding resources and prompts. |

**3. Testing and debugging a server with MCP Inspector** (10:54)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [20:43–23:15](https://www.youtube.com/watch?v=rnljvmHorQw&t=1243s) | FastMCP — the best way to build an MCP server with Python (ZazenCodes, 2025) | 2:32 | chapters | Inspecting the local server just built. |
| [0:00–8:22](https://www.youtube.com/watch?v=Y0tZ35dFFx4&t=0s) | 10 - MCP Inspector: Test and Debug your MCP Server Locally (AI Anytime, 2025) | 8:22 | chapters | AI Anytime: MCP Inspector end to end. Whole video; preview it. |

**4. A richer custom server, and common integration failures** (18:36)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [7:25–26:01](https://www.youtube.com/watch?v=-8k9lGpGQ6g&t=445s) | Build Anything With a CUSTOM MCP Server - Python Tutorial (Tech With Tim, 2025) | 18:36 | chapters | Tech With Tim: common Claude MCP issues and fixes, then an advanced custom server demo. |

**5. Wiring your own server into a coding-agent workspace** (4:27)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [4:40–9:07](https://www.youtube.com/watch?v=vUQfqW5GKAQ&t=280s) | MCP Servers in VS Code and GitHub Copilot (Visual Studio Code, 2025) | 4:27 | chapters | VS Code (official): building and installing your own MCP server in a VS Code/Copilot agent workspace, then a recap. |

**6. Designing tools agents can use well, and shipping them** (6:23)

| Clip | Video | Length | Check | Why this clip |
|---|---|---|---|---|
| [12:00–13:42](https://www.youtube.com/watch?v=v3Fr2JR47KA&t=720s) | The Future of MCP — David Soria Parra, Anthropic (AI Engineer, 2026) | 1:42 | chapters | David Soria Parra: best practices for server authors. |
| [23:15–27:56](https://www.youtube.com/watch?v=rnljvmHorQw&t=1395s) | FastMCP — the best way to build an MCP server with Python (ZazenCodes, 2025) | 4:41 | chapters | Distributing a Python MCP server so teammates can install it. |
