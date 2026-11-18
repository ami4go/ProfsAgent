"""Builds playlists.json + PLAYLISTS.md from the hand-curated spec below (durations and totals are computed, not typed).

check = how the clip's content and boundaries were confirmed:
  transcript   read in the caption transcript (boundaries at caption lines, accurate to about ±10 s)
  browser-tx   transcript read through the YouTube page's own transcript panel (the API was IP-blocked by then)
  chapters     the uploader's chapter markers only; content NOT read, so preview it before class
"""
import json
from pathlib import Path

HERE = Path(__file__).parent
cand = {c["id"]: c for c in json.loads((HERE / "candidates.json").read_text(encoding="utf-8"))}


def s(t: str) -> int:
    v = 0
    for p in t.split(":"):
        v = v * 60 + int(p)
    return v


def hms(x: int) -> str:
    return f"{x // 3600}:{x % 3600 // 60:02d}:{x % 60:02d}" if x >= 3600 else f"{x // 60}:{x % 60:02d}"


def C(vid, a, b, check, why):
    return {"video": vid, "start": a, "end": b, "check": check, "why": why}


SPEC = [
 {"id": "W01.L1", "topic": "Developer workflows and AI-assisted coding", "slot_min": 120,
  "lo": "CO1.LO3 (BL1): identify the core components of developer workflows and AI-assisted coding",
  "parts": [
   {"part": "1. Why software development is changing: Software 1.0 → 2.0 → 3.0, LLMs as a new kind of computer", "clips": [
     C("LCEmiRjPEtQ", "1:25", "11:04", "transcript", "Karpathy's Software 1.0/2.0/3.0 framing and 'LLMs as utilities, fabs and operating systems': the clearest big-picture opening for students who know only classical programming.")]},
   {"part": "2. Partial autonomy: humans and AI in a generate–verify loop", "clips": [
     C("LCEmiRjPEtQ", "18:22", "29:06", "transcript", "Partial-autonomy apps, the generate/verify loop, the 'autonomy slider' and the Iron-Man-suit analogy. This is the mental model for every workflow later in the course.")]},
   {"part": "3. From autocomplete to coding agents: a first live demo", "clips": [
     C("sTdz6PZoAnw", "0:00", "11:37", "transcript", "MIT Missing Semester (2026), a university lecture at exactly this level. The spectrum from autocomplete and inline chat to agents, a live Claude Code task, permissions, iterating, interrupting, and the TDD question.")]},
   {"part": "4. Where AI fits in the software lifecycle (and why coding speed alone does not help)", "clips": [
     C("4wMRXmLpdA8", "0:00", "9:05", "transcript", "IBM Technology: AI in each SDLC phase; over- and under-delegation; specs and harness. It is short, whiteboard style, and maps directly to 'components of a workflow'.")]},
   {"part": "5. Vibe coding vs spec-driven development vs agentic engineering", "clips": [
     C("mViFYTwWvcM", "0:00", "8:50", "transcript", "IBM Technology: vibe coding vs spec-driven development, with the reversed workflow (spec → design → code) shown on a whiteboard."),
     C("96jN2OCOfLs", "15:46", "23:44", "transcript", "Karpathy (Sequoia, 2026): agentic engineering preserves the professional quality bar, and the human owns taste, design and oversight. A strong contrast with vibe coding.")]},
   {"part": "6. Everyday workflow uses: bug-fixing with tests, code review, codebase understanding, the agent as a shell (plus privacy)", "clips": [
     C("sTdz6PZoAnw", "26:44", "41:43", "transcript", "Missing Semester: privacy note, then worked use cases (write a failing test → agent fixes → runs the suite → commits in the repo's style, review, onboarding, shell, vibe coding)."),
     C("gv0WHhKelSE", "6:27", "10:34", "browser-tx", "Anthropic's Cal Rueb: the use cases across the lifecycle (discovery, design, build, deploy, support, migrations).")]},
   {"part": "7. Verifying and reviewing AI-written code: who is accountable", "clips": [
     C("b2QkhmQ0sT0", "2:34", "16:20", "transcript", "A Meta senior staff engineer on reviewing AI code: review as a gradient, blast radius, feature gates, requiring proof in PRs, leaf vs trunk code, independent agent reviews."),
     C("sTdz6PZoAnw", "58:40", "1:00:20", "transcript", "Missing Semester's closing caveats: subtly wrong code, debugging spirals, why your own CS skills still matter.")]}]},

 {"id": "W01.L2", "topic": "Model Context Protocol and architecture (part 1 of 2)", "slot_min": 60,
  "lo": "CO1.LO1 (BL1): identify the configuration schema and protocol requirements for MCP",
  "parts": [
   {"part": "1. The integration problem: N models × M data sources, and what MCP is", "clips": [
     C("oblaHqULUHk", "0:00", "7:18", "transcript", "TechWorld with Nana: a backend engineer's motivating scenario (chatbot × databases → 8 custom integrations), why LLMs need LLM-friendly responses, and that MCP does not replace APIs. The best beginner framing found.")]},
   {"part": "2. Why Anthropic built MCP, from the source (LSP inspiration, value for each party)", "clips": [
     C("kQmXtrmQ5Zg", "0:56", "9:39", "transcript", "Mahesh Murag (Anthropic) at AI Engineer Summit: the motivation, the Language Server Protocol analogy, fragmentation, and what clients, servers and enterprises each gain.")]},
   {"part": "3. Architecture: host, client and server, and who calls whom", "clips": [
     C("oblaHqULUHk", "7:18", "11:01", "transcript", "Tools as functions on a server; runtime discovery ('give me all your tools'); the LLM proposes and the application orchestrates."),
     C("oblaHqULUHk", "20:56", "25:41", "transcript", "The architecture walked through on one example: the MCP server wraps the database, the host owns the MCP client, and the LLM never opens connections itself.")]},
   {"part": "4. The three server primitives: tools, resources, prompts", "clips": [
     C("CQywdSdi5iA", "0:35", "3:13", "transcript", "MCP co-creator David Soria Parra (Anthropic): tools, resources and prompts in one breath, with prompts as slash commands."),
     C("kQmXtrmQ5Zg", "9:39", "14:18", "transcript", "Mahesh: the same primitives classified by who controls them (model-controlled tools, application-controlled resources, user-controlled prompts), with Claude Desktop examples.")]},
   {"part": "5. The protocol itself: JSON-RPC 2.0 messages and components", "clips": [
     C("RhTiAOGwbYE", "13:12", "19:50", "chapters", "KodeKloud: component breakdown, architecture and JSON-RPC 2.0 message format (chapters 'Components', 'Architecture', 'Protocol – JSON-RPC 2.0').")]},
   {"part": "6. Transports: stdio for local, Streamable HTTP for remote", "clips": [
     C("sNFcx-jUnvg", "2:17", "6:49", "transcript", "theailanguage: what Streamable HTTP is, the client–server sequence diagram, and the five lifecycle components (part 2 continues the lifecycle).")]},
   {"part": "7. What people build with MCP (use cases)", "clips": [
     C("uBL0siiliGo", "0:00", "6:30", "transcript", "Gaurav Sen: compact use cases (SEO, RAG, apps) that consolidate the idea before part 2.")]}]},

 {"id": "W02.L1", "topic": "Model Context Protocol and architecture (part 2 of 2)", "slot_min": 120,
  "lo": "CO1.LO1 (BL1), continued: protocol requirements, configuration schema, security",
  "parts": [
   {"part": "1. The primitives in depth, from the protocol's co-creator (prompts, resources, tools, sampling, roots, completions)", "clips": [
     C("HNzH5Us1Rvg", "0:13", "17:30", "transcript", "'MCP 201' (Anthropic, Code w/ Claude): each primitive with a live example, the interaction model, then sampling (the server asks the client's model), roots and completions. This is the authoritative deep dive.")]},
   {"part": "2. Tools vs resources vs prompts on one worked scenario", "clips": [
     C("XXh-lrWTMeQ", "5:57", "18:45", "transcript", "A single support-desk scenario: a database as tools, log files as resources, response templates as prompts. Students see when to use which.")]},
   {"part": "3. Connection lifecycle: initialisation and capability negotiation, requests, notifications, sessions", "clips": [
     C("sNFcx-jUnvg", "6:00", "14:50", "transcript", "Sequence-diagram walk-through: initialise → requests → notifications → server-sent messages → session ids, the protocol requirements of LO1.")]},
   {"part": "4. The configuration schema: how a host is told about servers", "clips": [
     C("-8k9lGpGQ6g", "4:59", "10:28", "chapters", "Tech With Tim: registering a server in Claude Desktop's JSON config, plus common configuration errors and fixes."),
     C("vUQfqW5GKAQ", "0:20", "2:23", "chapters", "VS Code (official): installing the GitHub MCP server into a VS Code/Copilot workspace."),
     C("X7lgIa6guKg", "0:00", "13:51", "chapters", "Net Ninja: adding MCP servers to Claude Code (scopes, project config). Whole video; content not read, so preview it.")]},
   {"part": "5. Remote servers and authorization (OAuth 2.1)", "clips": [
     C("HNzH5Us1Rvg", "17:30", "24:02", "transcript", "MCP 201: moving from local servers to remote ones over Streamable HTTP, and why authorization is OAuth 2.1."),
     C("mYKMwZcGynw", "2:47", "14:06", "transcript", "Aaron Parecki (Okta, OAuth spec editor): OAuth from first principles (hotel key-card analogy), then the MCP auth flow: discovery, metadata, dynamic client registration.")]},
   {"part": "6. Security, access control and production concerns", "clips": [
     C("oblaHqULUHk", "11:01", "14:43", "transcript", "Secrets stay in the server, never in the LLM; access control at the server."),
     C("oblaHqULUHk", "25:41", "29:38", "transcript", "Reference vs enterprise servers, tool-count limits, server-side policies.")]},
   {"part": "7. Where MCP is going (and advice for server authors)", "clips": [
     C("v3Fr2JR47KA", "5:07", "13:42", "chapters", "David Soria Parra (2026): skills + MCP + CLI as the connectivity stack, progressive discovery, programmatic tool calling, best practices for server authors (chapters; this talk's transcript was fetched but only skimmed).")]}]},

 {"id": "W02.L2", "topic": "Coding agents and context engineering (part 1 of 2): how coding agents work", "slot_min": 60,
  "lo": "CO1.LO2 (BL3), groundwork: what a coding agent is made of",
  "parts": [
   {"part": "1. What an agent is (and when not to build one)", "clips": [
     C("D7_ipDqhtwk", "0:55", "14:39", "transcript", "Barry Zhang (Anthropic) 'How we build effective agents': workflows vs agents, a checklist for when to use an agent, keep it simple (environment + tools + prompt in a loop), think from the agent's context window.")]},
   {"part": "2. Under the hood: LLM → chat → tool calls → the agent harness loop", "clips": [
     C("sTdz6PZoAnw", "11:37", "26:44", "transcript", "Missing Semester: the LLM as a conditional distribution, how multi-turn chat is built, tool calls, the harness loop, then the opening demo replayed step by step. The best 'from first principles' segment found.")]},
   {"part": "3. A real coding agent's design: a pure agent, agentic search, permissions", "clips": [
     C("gv0WHhKelSE", "3:16", "6:27", "browser-tx", "Anthropic: Claude Code is 'tools + model in a loop'; agentic search (grep/glob) instead of indexing the repository; the permission system.")]},
   {"part": "4. Inside a production agent: one while-loop, the core tools, to-do lists", "clips": [
     C("RFKCzGlAU6Q", "7:54", "19:25", "transcript", "PromptLayer's Jared Zoneraich, 'How Claude Code works': less scaffolding, more model; the core tools (bash, grep, edit); why to-do lists keep long tasks on track.")]}]},

 {"id": "W03.L1", "topic": "Coding agents and context engineering (part 2 of 2): context engineering", "slot_min": 60,
  "lo": "CO1.LO2 (BL3): configure what goes into the agent's context",
  "parts": [
   {"part": "1. What context engineering is: write, select, compress, isolate", "clips": [
     C("4GiqzUHD5AA", "0:00", "14:05", "transcript", "Lance Martin (LangChain): the four strategies with examples from Claude Code, Cursor and ChatGPT memory. It stops before the framework-specific LangGraph section.")]},
   {"part": "2. Why more context can make agents worse: context rot and four failure modes", "clips": [
     C("BwXremQ-i6I", "0:00", "10:21", "chapters", "IBM Technology: context rot, poisoning, distraction, confusion and clash, then the fixes (validate, compact, curate, prune). Whole video, chapters only.")]},
   {"part": "3. Context tools in coding agents: clear, rewind, compaction, llms.txt, AGENTS.md/CLAUDE.md, skills, subagents", "clips": [
     C("sTdz6PZoAnw", "46:15", "57:30", "transcript", "Missing Semester: each context-management feature explained with the reason it exists.")]},
   {"part": "4. Configuring an agent workspace in practice", "clips": [
     C("gv0WHhKelSE", "10:34", "18:06", "browser-tx", "Anthropic: CLAUDE.md, permission settings, CLI tools vs MCP servers, /clear vs /compact, plan first, TDD, multiple agents, Esc to steer. This is the 'configure' half of LO2.")]},
   {"part": "5. Advanced: the smart zone, research → plan → implement, intentional compaction", "clips": [
     C("rmvDxxNubIg", "3:05", "8:30", "transcript", "Dex Horthy (who popularised 'context engineering'): the dumb zone, what compaction keeps, subagents for context control, research prompts."),
     C("rmvDxxNubIg", "12:14", "18:35", "transcript", "On-demand compressed context; research → plan → implement; why humans must read the plan.")]}]},

 {"id": "W03.L2", "topic": "Custom tool integrations using MCP (hands-on)", "slot_min": 120,
  "lo": "CO1.LO2 (BL3): configure custom tool integrations in agent workspaces using MCP",
  "parts": [
   {"part": "1. Use an existing server, build a server, build a client: the whole loop once", "clips": [
     C("RhTiAOGwbYE", "19:50", "40:14", "chapters", "KodeKloud: demo of using an existing server, building a server, building a client (with free labs that pair well with the lab session).")]},
   {"part": "2. Building a Python MCP server with FastMCP: tools, resources, prompts", "clips": [
     C("rnljvmHorQw", "3:10", "20:43", "chapters", "ZazenCodes: the FastMCP library, project layout, running the server, connecting it to Claude Desktop, adding resources and prompts.")]},
   {"part": "3. Testing and debugging a server with MCP Inspector", "clips": [
     C("rnljvmHorQw", "20:43", "23:15", "chapters", "Inspecting the local server just built."),
     C("Y0tZ35dFFx4", "0:00", "8:22", "chapters", "AI Anytime: MCP Inspector end to end. Whole video; preview it.")]},
   {"part": "4. A richer custom server, and common integration failures", "clips": [
     C("-8k9lGpGQ6g", "7:25", "26:01", "chapters", "Tech With Tim: common Claude MCP issues and fixes, then an advanced custom server demo.")]},
   {"part": "5. Wiring your own server into a coding-agent workspace", "clips": [
     C("vUQfqW5GKAQ", "4:40", "9:07", "chapters", "VS Code (official): building and installing your own MCP server in a VS Code/Copilot agent workspace, then a recap.")]},
   {"part": "6. Designing tools agents can use well, and shipping them", "clips": [
     C("v3Fr2JR47KA", "12:00", "13:42", "chapters", "David Soria Parra: best practices for server authors."),
     C("rnljvmHorQw", "23:15", "27:56", "chapters", "Distributing a Python MCP server so teammates can install it.")]}]},
]


def main():
    out, md = [], ["# CS601 (Software Development using AI): YouTube lecture playlists for the first 6 lectures",
                   "", "Delivery mode 2: each lecture is taught entirely by the clips below, in order. Times are start → end in the source video.",
                   "`check`: **transcript** = content and boundaries read in the captions (about ±10 s); **browser-tx** = read via the YouTube "
                   "page's transcript panel; **chapters** = uploader chapters only, so preview before class.",
                   "The embed links play exactly the clip (`start`/`end` parameters).", ""]
    for L in SPEC:
        tot, parts = 0, []
        for P in L["parts"]:
            clips = []
            for c in P["clips"]:
                v = cand[c["video"]]
                a, b = s(c["start"]), s(c["end"])
                assert 0 <= a < b <= v["duration_s"] + 2, (c, v["duration_s"])
                clips.append({**c, "title": v["title"], "channel": v["channel"], "published": v["published"][:10],
                              "views": v["views"], "video_length": hms(v["duration_s"]), "clip_s": b - a,
                              "watch_url": f"https://www.youtube.com/watch?v={c['video']}&t={a}s",
                              "embed_url": f"https://www.youtube.com/embed/{c['video']}?start={a}&end={b}"})
                tot += b - a
            parts.append({"part": P["part"], "clips": clips, "part_s": sum(x["clip_s"] for x in clips)})
        out.append({**{k: L[k] for k in ("id", "topic", "slot_min", "lo")}, "video_total_s": tot, "parts": parts})
        md += [f"## {L['id']}: {L['topic']}",
               f"*{L['lo']}*  ·  slot {L['slot_min']} min  ·  **video {hms(tot)}** "
               f"({round(100 * tot / 60 / L['slot_min'])}% of the slot; the rest is for questions, a quiz or the lab)", ""]
        for P in parts:
            md.append(f"**{P['part']}** ({hms(P['part_s'])})")
            md.append("")
            md.append("| Clip | Video | Length | Check | Why this clip |")
            md.append("|---|---|---|---|---|")
            for c in P["clips"]:
                md.append(f"| [{c['start']}–{c['end']}]({c['watch_url']}) | {c['title'][:70]} ({c['channel']}, {c['published'][:4]}) "
                          f"| {hms(c['clip_s'])} | {c['check']} | {c['why']} |")
            md.append("")
    (HERE / "playlists.json").write_text(json.dumps(out, indent=1, ensure_ascii=False), encoding="utf-8")
    (HERE / "PLAYLISTS.md").write_text("\n".join(md), encoding="utf-8")
    # the same data as a script, so player.html works without fetch()
    (HERE / "playlists.js").write_text("window.PLAYLISTS = " + json.dumps(out, ensure_ascii=False) + ";\n", encoding="utf-8")
    for L in out:
        n = sum(len(p["clips"]) for p in L["parts"])
        vids = len({c["video"] for p in L["parts"] for c in p["clips"]})
        print(f"{L['id']}: {hms(L['video_total_s'])} of {L['slot_min']} min, {n} clips from {vids} videos")


if __name__ == "__main__":
    main()
