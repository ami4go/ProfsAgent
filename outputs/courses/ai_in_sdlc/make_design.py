"""Writes the hand-authored design of "AI in SDLC" (2 credits, 13 lectures) in ProfsAgent's run format:
runs/ai-in-sdlc-01/state.json. The course design (COs, LOs, CO-PO, modules, schedule, assessment, labs, resources) is
written here by hand; only regulation facts (Bloom band for the level, CO count for the credits, hours budget) are
taken from ProfsAgent's deterministic helpers so its validators can check the design."""
import json
import sys
from pathlib import Path

import yaml

sys.path.insert(0, "D:/BTP/src")
from profsagent.config import pedagogy  # noqa: E402
from profsagent.design import deterministic as det  # noqa: E402

RUN = Path("D:/BTP/runs/ai-in-sdlc-01")
LEVEL, CREDITS, WEEKS, LTP = 4, 2, 13, {"L": 1.5, "T": 0, "P": 1}     # IIIT-D credits = L + T + P/2


def abcd(verb, behaviour, condition, degree):
    return {"statement": f"{verb.capitalize()} {behaviour}, {condition}, {degree}.", "verb": verb, "behaviour": behaviour,
            "condition": condition, "degree": degree}


# ---------------------------------------------------------------- course outcomes (2-3 for a 2-credit course)
COS = [
    {"id": "CO1", **abcd("apply", "AI assistants to requirements engineering and software architecture", "for a small software product",
                         "producing testable user stories and an architecture decision record traceable to stakeholder input"),
     "bloom_level": 3},
    {"id": "CO2", **abcd("analyse", "AI-generated code for correctness and maintainability defects",
                         "while developing a multi-module program with AI assistants",
                         "accepting changes only when reviewed automated checks and mutation scores support them"),
     "bloom_level": 4},
    {"id": "CO3", **abcd("evaluate", "the use of AI in a team's security, delivery and maintenance practice",
                         "for a given project and its risks", "justifying each recommendation with published evidence and own measurements"),
     "bloom_level": 5},
]

# ---------------------------------------------------------------- learning outcomes (2-4 per CO)
LOS = [
    ("CO1.LO1", "CO1", 2, abcd("describe", "where AI tools enter each phase of the software development lifecycle and what changes for the engineer",
                               "using the lifecycle of a real open-source project", "naming at least one tool and one risk for each phase")),
    ("CO1.LO2", "CO1", 2, abcd("explain", "how an LLM assistant turns a prompt and its context into code",
                               "using worked examples of an inline completion, a chat answer and an agent run",
                               "identifying context limits, non-determinism and hallucination as causes of failure")),
    ("CO1.LO3", "CO1", 3, abcd("write", "requirements with an AI assistant from an interview transcript or a product brief",
                               "for a small web product", "producing user stories with Given-When-Then acceptance criteria and resolving the ambiguities with the stakeholder")),
    ("CO1.LO4", "CO1", 3, abcd("use", "an AI assistant to compare architecture options and record a design decision",
                               "for a small web service", "as an architecture decision record and a diagram-as-code that a peer can check against the requirements")),
    ("CO2.LO1", "CO2", 3, abcd("implement", "a feature with an AI assistant or agent, choosing the mode and the context it is given",
                               "from a written feature specification", "so that the result builds and passes the provided tests with every change reviewed")),
    ("CO2.LO2", "CO2", 4, abcd("analyse", "an AI-generated pull request and a legacy module refactored with AI help",
                               "given a review checklist", "identifying correctness, readability and maintainability defects and fixing every critical one")),
    ("CO2.LO3", "CO2", 3, abcd("use", "an AI assistant to write and strengthen unit tests", "for an existing module",
                               "raising branch coverage and mutation score to a stated target and rejecting tests whose expected values are wrong")),
    ("CO2.LO4", "CO2", 4, abcd("diagnose", "failures in given programs with AI assistance", "including automated repairs the assistant proposes",
                               "localising each fault and accepting a repair only when tests and a reasoned explanation support it")),
    ("CO3.LO1", "CO3", 5, abcd("assess", "the security of AI-assisted code and coding agents", "for a given repository and agent setup",
                               "finding insecure suggestions, hallucinated dependencies, leaked secrets and prompt-injection paths and ranking them by risk")),
    ("CO3.LO2", "CO3", 3, abcd("apply", "AI to delivery and maintenance work, from pull-request review in continuous integration to a library migration",
                               "on a team project and a legacy codebase", "keeping the regression tests green and recording which AI review comments were acted on and why")),
    ("CO3.LO3", "CO3", 5, abcd("evaluate", "the effect of AI tools on a team's productivity and software quality",
                               "using published controlled studies, benchmark results and the student's own measurements", "explaining why the results differ between settings")),
    ("CO3.LO4", "CO3", 5, abcd("recommend", "an AI adoption policy for a software team", "given a project's risks",
                               "covering licensing and IP, privacy, human oversight and accountability, each point justified with evidence from the course")),
]
LO_BLOOM = {i: b for i, _co, b, _d in LOS}

# ---------------------------------------------------------------- modules and topics (one 1.5 h lecture a week)
SRC = lambda ref: [{"tag": "HAND", "ref": ref, "basis": None}]  # noqa: E731
MODULES = [
    ("M1", "Foundations: how AI meets the software lifecycle", ["CO1"], [
        ("AI across the software development lifecycle: where it helps, where it fails", ["CO1.LO1"], [], False, "SWEBOK v4; Hou et al. 2024"),
        ("How LLM coding assistants and agents work: context, prompting, tools and failure modes", ["CO1.LO2"], ["M1.T1"], True, "Chen et al. 2021; Anthropic 2025"),
    ]),
    ("M2", "AI for requirements and design", ["CO1"], [
        ("AI-assisted requirements engineering: elicitation, user stories and acceptance criteria", ["CO1.LO3"], ["M1.T2"], True, "Arora et al. 2024"),
        ("AI-assisted software design: architecture options, decision records and diagrams as code", ["CO1.LO4"], ["M2.T1"], True, "Software Engineering at Google; Nguyen-Duc et al. 2024"),
    ]),
    ("M3", "AI-assisted construction and code review", ["CO2"], [
        ("Generating code with assistants and agents: modes, context and specification-driven development", ["CO2.LO1"], ["M1.T2", "M2.T2"], True, "Anthropic 2025; Jimenez et al. 2024"),
        ("Reviewing AI-generated code and refactoring legacy code with AI", ["CO2.LO2"], ["M3.T1"], True, "Software Engineering at Google"),
    ]),
    ("M4", "AI for testing and debugging", ["CO2"], [
        ("AI-generated unit tests: oracles, coverage and mutation testing", ["CO2.LO3"], ["M3.T1"], True, "Schäfer et al. 2024"),
        ("Debugging with AI: fault localisation and automated program repair", ["CO2.LO4"], ["M4.T1"], True, "Fan et al. 2023 (APR)"),
    ]),
    ("M5", "Security, delivery and maintenance", ["CO3"], [
        ("Security of AI-assisted development: insecure code, package hallucination and prompt injection", ["CO3.LO1"], ["M3.T2"], True, "Pearce et al. 2022; Spracklen et al. 2025; OWASP 2025"),
        ("AI in continuous integration and DevOps: review bots, pipeline automation and incident triage", ["CO3.LO2"], ["M5.T1"], True, "DORA 2024"),
        ("AI for maintenance and evolution: documentation, migration and technical debt", ["CO3.LO2"], ["M3.T2", "M4.T1"], True, "Nguyen-Duc et al. 2024"),
    ]),
    ("M6", "Measuring and governing AI in software teams", ["CO3"], [
        ("Measuring the impact of AI tools: controlled studies, benchmarks and team metrics", ["CO3.LO3"], ["M4.T1", "M5.T2"], False, "Peng et al. 2023; Becker et al. 2025; Jimenez et al. 2024"),
        ("Responsible adoption: licensing, privacy, oversight and a team AI policy", ["CO3.LO4"], ["M6.T1", "M5.T1"], False, "OWASP 2025; DORA 2024"),
    ]),
]
OUTSIDE = 5.0        # hours a week outside lectures (TEMPLATE: 2.5-3 per credit -> 5-6 for 2 credits)
modules, order = [], []
for k, (mid, title, cos, topics) in enumerate(MODULES, 1):
    ts = []
    for j, (tt, los, req, hands, ref) in enumerate(topics, 1):
        tid = f"{mid}.T{j}"
        ts.append({"id": tid, "title": tt, "est_hours": 1.5, "serves_los": los, "requires": req, "topic_uid": None,
                   "hands_on": hands, "outside_load_hours": OUTSIDE, "sources": SRC(ref)})
        order.append(tid)
    modules.append({"id": mid, "title": title, "order": k, "primary_cos": cos, "topics": ts})
assert len(order) == WEEKS
WEEK = {t: w for w, t in enumerate(order, 1)}
schedule = {"weeks": [{"week": w, "items": [{"topic_id": t, "hours": 1.5}], "is_midsem_boundary": w == 7} for w, t in enumerate(order, 1)],
            "topic_weeks": {t: [w] for w, t in enumerate(order, 1)}, "feasible": True,
            "explanation": "one 1.5-hour lecture a week, in prerequisite order; mid-semester exam after week 7",
            "hours_needed": 1.5 * WEEKS, "hours_available": LTP["L"] * WEEKS, "dropped_edges": [], "order": order}

# ---------------------------------------------------------------- labs (P = 1: six 2-hour labs, every other week)
LABS = [
    (2, "Prompting and context with a coding assistant",
     "Solve the same three tasks with inline completion, chat and an agent; vary the context given (files, conventions, tests) and log which failures each change removes.",
     ["CO1.LO2"], ["M1.T2"], ["Python", "VS Code", "an AI coding assistant (free tier)"]),
    (4, "From interview to user stories and a decision record",
     "From a recorded stakeholder interview, use an assistant to draft user stories with Given-When-Then criteria, list and resolve ambiguities, then compare two architectures and write an ADR with a Mermaid diagram.",
     ["CO1.LO3", "CO1.LO4"], ["M2.T1", "M2.T2"], ["an LLM chat assistant", "Markdown", "Mermaid"]),
    (6, "Generate a feature, then review the pull request",
     "Implement a specified feature with an agent on a branch, open a pull request, and review a classmate's AI-generated PR against the course checklist; fix the critical findings.",
     ["CO2.LO1", "CO2.LO2"], ["M3.T1", "M3.T2"], ["Git", "GitHub", "an AI coding agent", "pytest"]),
    (8, "Tests that catch bugs: coverage and mutation score",
     "Generate unit tests for a module with an assistant, measure branch coverage and mutation score, remove tests with wrong oracles, then localise and repair two seeded faults with AI help.",
     ["CO2.LO3", "CO2.LO4"], ["M4.T1", "M4.T2"], ["pytest", "coverage.py", "mutmut", "an AI assistant"]),
    (10, "Secure the pipeline",
     "Audit an AI-written repository for insecure code, hallucinated or vulnerable dependencies and secrets; add static analysis and an AI review step to a GitHub Actions workflow.",
     ["CO3.LO1", "CO3.LO2"], ["M5.T1", "M5.T2"], ["GitHub Actions", "Semgrep", "pip-audit", "gitleaks"]),
    (12, "Migrate and measure",
     "Migrate a legacy module to a newer library version with AI help, keep the regression tests green, and time comparable tasks with and without the assistant to report the measured effect.",
     ["CO3.LO2", "CO3.LO3"], ["M5.T3", "M6.T1"], ["an AI coding assistant", "pytest", "a time log"]),
]
labs = [{"week": w, "id": f"W{w:02d}.LAB", "title": t, "exercise": e, "practises_los": los, "uses_topics": tp, "tools": tools}
        for w, t, e, los, tp, tools in LABS]


# ---------------------------------------------------------------- assessment (>= 40% proctored: quizzes + midsem)
def inst(iid, rel, due, topics, los):
    share = round(100 / len(los), 1)
    return {"id": iid, "release_week": rel, "due_week": due, "covers_topics": topics,
            "assesses": [{"lo_id": x, "marks_pct_of_instance": share, "bloom_level": LO_BLOOM[x]} for x in los]}


assessment = {"concerns": [], "missing": [], "weight_sum": 100.0, "components": [
    {"type": "quiz", "weight_pct": 10.0, "proctored": True, "instances": [
        inst("A:Quiz1", 3, 3, ["M1.T1", "M1.T2"], ["CO1.LO1", "CO1.LO2"]),
        inst("A:Quiz2", 9, 9, ["M4.T1", "M4.T2"], ["CO2.LO3", "CO2.LO4"]),
        inst("A:Quiz3", 11, 11, ["M5.T1", "M5.T2", "M5.T3"], ["CO3.LO1", "CO3.LO2"])]},
    {"type": "midsem", "weight_pct": 20.0, "proctored": True, "instances": [
        inst("A:Midsem", 8, 8, order[:7], ["CO1.LO2", "CO1.LO3", "CO1.LO4", "CO2.LO1", "CO2.LO2", "CO2.LO3"])]},
    {"type": "endsem", "weight_pct": 20.0, "proctored": True, "instances": [
        inst("A:Endsem", 13, 13, order[7:], ["CO2.LO4", "CO3.LO1", "CO3.LO2", "CO3.LO3", "CO3.LO4"])]},
    # each lab is due the week it runs; the week-10 lab also uses week 11's maintenance topic, so it is due in week 11
    {"type": "lab", "weight_pct": 20.0, "instances": [inst(f"A:Lab{w}", w, w + (w == 10), tp, los) for w, _t, _e, los, tp, _tools in LABS]},
    {"type": "project", "weight_pct": 30.0, "instances": [
        inst("A:Project-M1-requirements-and-design", 4, 5, ["M2.T1", "M2.T2"], ["CO1.LO3", "CO1.LO4"]),
        inst("A:Project-M2-build-and-test", 7, 10, ["M3.T1", "M3.T2", "M4.T1"], ["CO2.LO1", "CO2.LO2", "CO2.LO3"]),
        # the team's AI-use reflection and adoption policy is part of the final milestone (released once M6 is taught)
        inst("A:Project-M3-ship-secure-measure-and-policy", 13, 13, ["M5.T1", "M5.T2", "M5.T3", "M6.T1", "M6.T2"],
             ["CO3.LO1", "CO3.LO2", "CO3.LO3", "CO3.LO4"])]},
]}

# ---------------------------------------------------------------- CO-PO mapping, every CSE programme (TEMPLATE)
COPO = [  # (co, po_uid, strength 1-3, why, activities)
    ("CO1", "BTECH-COMMON/PO5", 3, "Students select and apply AI assistants as modern IT tools for requirements and design.", ["tool-use"]),
    ("CO1", "BTECH-COMMON/PO3", 2, "User stories, acceptance criteria and an architecture decision are designed to meet stated needs.", ["design"]),
    ("CO1", "BTECH-COMMON/PO10", 2, "Requirements and decision records are written for stakeholders and reviewers.", ["written-communication"]),
    ("CO1", "BTECH-COMMON/PO9", 1, "Requirements and design are done as a team project milestone.", ["teamwork"]),
    ("CO2", "BTECH-COMMON/PO5", 3, "Code, tests and repairs are produced with AI coding tools and checked with coverage and mutation tools.", ["tool-use", "implement"]),
    ("CO2", "BTECH-COMMON/PO2", 2, "Defects in AI-generated code are analysed and traced to their cause.", ["evaluate-critique"]),
    ("CO2", "BTECH-COMMON/PO3", 2, "A multi-module program is developed to a specification.", ["implement"]),
    ("CO3", "BTECH-COMMON/PO4", 2, "AI's effect is judged from controlled studies and the student's own timed measurements.", ["analyse-data", "research-investigation"]),
    ("CO3", "BTECH-COMMON/PO8", 2, "The adoption policy weighs licensing, privacy and accountability.", ["ethics-reflection"]),
    ("CO3", "BTECH-COMMON/PO6", 2, "Security and legal risks of AI-written software are assessed for the people who use it.", ["ethics-reflection"]),
    ("CO3", "BTECH-COMMON/PO12", 1, "AI tools change quickly; the course practises judging new evidence.", ["self-directed-learning"]),
    ("CO1", "BTECH-CSE/PSO4", 2, "Requirements and design for a computer-based application with modern tools.", ["design"]),
    ("CO1", "BTECH-CSE/PSO5", 2, "Use of advanced AI tools in software engineering.", ["tool-use"]),
    ("CO2", "BTECH-CSE/PSO4", 3, "Implement and evaluate software with modern tools and testing methods.", ["implement"]),
    ("CO2", "BTECH-CSE/PSO5", 3, "Advanced techniques: agentic coding, mutation testing, automated repair.", ["tool-use"]),
    ("CO2", "BTECH-CSE/PSO3", 2, "Testing and repair techniques adapted to AI-written code, judged on measured results.", ["analyse-data"]),
    ("CO3", "BTECH-CSE/PSO5", 3, "Security analysis, CI automation and measurement of AI tools.", ["tool-use"]),
    ("CO3", "BTECH-CSE/PSO4", 2, "Evaluating a system's delivery and maintenance practice.", ["evaluate-critique"]),
    ("CO1", "BTECH-CSAI/PSO1", 1, "How LLM assistants work is taught as applied AI.", ["theory"]),
    ("CO2", "BTECH-CSAI/PSO3", 2, "Implementing and testing programs and their data structures.", ["implement"]),
    ("CO2", "BTECH-CSAI/PSO2", 1, "Limits of AI code generation (hallucination, non-determinism) are analysed.", ["theory"]),
    ("CO3", "BTECH-CSAI/PSO6", 3, "Economic and societal impact of AI-based software development is evaluated.", ["ethics-reflection"]),
    ("CO1", "MTECH-CSE/PSO4", 2, "Use of advanced computing tools in requirements and design.", ["tool-use"]),
    ("CO1", "MTECH-CSE/PSO6", 1, "Team project milestone.", ["teamwork"]),
    ("CO2", "MTECH-CSE/PSO3", 3, "Develop and evaluate a system that meets stated needs.", ["implement"]),
    ("CO2", "MTECH-CSE/PSO4", 3, "Advanced AI coding and testing tools.", ["tool-use"]),
    ("CO3", "MTECH-CSE/PO1", 2, "Investigation of AI's effect with measurements.", ["research-investigation"]),
    ("CO3", "MTECH-CSE/PO2", 2, "A substantial written reflection and policy report.", ["written-communication"]),
    ("CO3", "MTECH-CSE/PSO7", 2, "Professional and ethical responsibility in AI adoption.", ["ethics-reflection"]),
    ("CO3", "MTECH-CSE/PSO10", 2, "Impact of AI-based development in an economic and societal context.", ["ethics-reflection"]),
]
programmes = ["BTECH-COMMON", "BTECH-CSE", "BTECH-CSAI", "MTECH-CSE"]
po_text = {}
for f in ("btech_common", "btech_cse", "btech_csai", "mtech_cse"):
    for p in yaml.safe_load(open(f"D:/BTP/data/programmes/{f}.yaml", encoding="utf-8"))["po"]:
        po_text[p["id"]] = (p["text"], p["label"])
programme_pos = [{"uid": u, "text": t, "short_label": lab, "programme": u.split("/")[0]} for u, (t, lab) in po_text.items()]
co_stmt = {c["id"]: c["statement"] for c in COS}
copo = [{"co_id": c, "po_uid": u, "strength_provisional": s, "co_phrase": co_stmt[c][:120], "po_phrase": po_text[u][0][:120],
         "justification": why, "evidencing_activities": acts} for c, u, s, why, acts in COPO]


# ---------------------------------------------------------------- resources (identifiers checked 18 Nov 2026)
def ref(cid, role, title, authors, year, venue, topics, why, url=None, doi=None, arxiv=None, edition=None):
    return {"candidate_id": cid, "role": role, "title": title, "authors": authors, "year": year, "edition": edition, "venue": venue,
            "identifier": {"isbn": None, "doi": doi, "arxiv": arxiv, "url": url},
            "supports_topics": [{"topic_id": t, "reason": why} for t in topics], "status": "verified",
            "verification": {"verified": True, "problems": [], "by": "hand: title, authors, year and identifier checked by web search, 18 Nov 2026"}}


resources = [
    ref("book:genai-effective-sd-2024", "textbook", "Generative AI for Effective Software Development",
        ["Anh Nguyen-Duc (ed.)", "Pekka Abrahamsson (ed.)", "Foutse Khomh (ed.)"], 2024, "Springer",
        ["M1.T1", "M2.T1", "M2.T2", "M3.T1", "M5.T3", "M6.T2"], "Edited chapters on generative AI in each lifecycle phase."),
    ref("book:sommerville-se-10", "reference", "Software Engineering", ["Ian Sommerville"], 2015, "Pearson",
        ["M1.T1", "M2.T1", "M2.T2", "M4.T1"], "Lifecycle, requirements, design and testing vocabulary the course builds on.", edition="10th"),
    ref("https://abseil.io/resources/swe-book", "reference", "Software Engineering at Google: Lessons Learned from Programming Over Time",
        ["Titus Winters", "Tom Manshreck", "Hyrum Wright"], 2020, "O'Reilly", ["M2.T2", "M3.T2", "M5.T2"],
        "Code review, design docs, testing and CI at scale: the practice AI is inserted into.", url="https://abseil.io/resources/swe-book"),
    ref("https://www.computer.org/education/bodies-of-knowledge/software-engineering", "reference",
        "SWEBOK Guide V4.0: Guide to the Software Engineering Body of Knowledge", ["IEEE Computer Society"], 2024, "IEEE Computer Society",
        ["M1.T1"], "The lifecycle knowledge areas the course maps AI onto.", url="https://www.computer.org/education/bodies-of-knowledge/software-engineering"),
    ref("arxiv:2308.10620", "paper", "Large Language Models for Software Engineering: A Systematic Literature Review",
        ["Xinyi Hou", "et al."], 2024, "ACM TOSEM", ["M1.T1", "M6.T1"], "Map of LLM use across SE tasks.", arxiv="2308.10620"),
    ref("arxiv:2310.03533", "paper", "Large Language Models for Software Engineering: Survey and Open Problems",
        ["Angela Fan", "et al."], 2023, "ICSE-FoSE", ["M1.T1", "M4.T1"], "Open problems, esp. hallucination and testing.", arxiv="2310.03533"),
    ref("arxiv:2107.03374", "paper", "Evaluating Large Language Models Trained on Code", ["Mark Chen", "et al."], 2021, "arXiv",
        ["M1.T2", "M6.T1"], "How code models are trained and evaluated (HumanEval, pass@k).", arxiv="2107.03374"),
    ref("https://www.anthropic.com/engineering/claude-code-best-practices", "tool-doc", "Claude Code: Best practices for agentic coding",
        ["Anthropic"], 2025, "Anthropic Engineering", ["M1.T2", "M3.T1"], "Context files, plan-then-code and verification loops for agents.",
        url="https://www.anthropic.com/engineering/claude-code-best-practices"),
    ref("arxiv:2310.13976", "paper", "Advancing Requirements Engineering through Generative AI: Assessing the Role of LLMs",
        ["Chetan Arora", "John Grundy", "Mohamed Abdelrazek"], 2024, "Generative AI for Effective Software Development (Springer), ch. 6",
        ["M2.T1"], "LLMs in elicitation, analysis, specification and validation, with a SWOT analysis.", arxiv="2310.13976"),
    ref("arxiv:2310.06770", "paper", "SWE-bench: Can Language Models Resolve Real-World GitHub Issues?", ["Carlos E. Jimenez", "et al."], 2024, "ICLR",
        ["M3.T1", "M6.T1"], "The benchmark behind most coding-agent claims, and its limits.", arxiv="2310.06770"),
    ref("arxiv:2302.06527", "paper", "An Empirical Evaluation of Using Large Language Models for Automated Unit Test Generation",
        ["Max Schäfer", "Sarah Nadi", "Aryaz Eghbali", "Frank Tip"], 2024, "IEEE TSE", ["M4.T1"],
        "TestPilot: LLM-generated unit tests, coverage and the re-prompting loop.", arxiv="2302.06527", doi="10.1109/TSE.2023.3334955"),
    ref("arxiv:2205.10583", "paper", "Automated Repair of Programs from Large Language Models", ["Zhiyu Fan", "et al."], 2023, "ICSE",
        ["M4.T2"], "What LLM-based program repair fixes and what it gets wrong.", arxiv="2205.10583"),
    ref("arxiv:2108.09293", "paper", "Asleep at the Keyboard? Assessing the Security of GitHub Copilot's Code Contributions",
        ["Hammond Pearce", "et al."], 2022, "IEEE S&P", ["M5.T1"], "About 40% of suggestions in CWE scenarios were vulnerable.", arxiv="2108.09293"),
    ref("arxiv:2406.10279", "paper", "We Have a Package for You! A Comprehensive Analysis of Package Hallucinations by Code Generating LLMs",
        ["Joseph Spracklen", "et al."], 2025, "USENIX Security", ["M5.T1"], "Hallucinated package names and the attack they enable.", arxiv="2406.10279"),
    ref("https://genai.owasp.org/llm-top-10/", "reference", "OWASP Top 10 for LLM Applications 2025", ["OWASP GenAI Security Project"], 2025, "OWASP",
        ["M5.T1", "M6.T2"], "Prompt injection, excessive agency and supply-chain risks for agents.", url="https://genai.owasp.org/llm-top-10/"),
    ref("https://dora.dev/research/2024/dora-report/", "report", "Accelerate State of DevOps Report 2024", ["DORA (Google Cloud)"], 2024, "DORA",
        ["M5.T2", "M6.T1", "M6.T2"], "Delivery metrics and the measured effect of AI adoption on teams.", url="https://dora.dev/research/2024/dora-report/"),
    ref("arxiv:2302.06590", "paper", "The Impact of AI on Developer Productivity: Evidence from GitHub Copilot", ["Sida Peng", "et al."], 2023, "arXiv",
        ["M6.T1"], "Controlled experiment: 55.8% faster on a scoped task.", arxiv="2302.06590"),
    ref("arxiv:2507.09089", "paper", "Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity",
        ["Joel Becker", "Nate Rush", "Elizabeth Barnes", "David Rein"], 2025, "METR / arXiv", ["M6.T1"],
        "RCT: experienced developers were 19% slower with AI while believing they were faster.", arxiv="2507.09089"),
]

DESCRIPTION = ("How AI, above all large language models and coding agents, is used in every phase of the software development "
               "lifecycle: requirements, design, construction, code review, testing and debugging, security, delivery and "
               "maintenance. Students use the tools on a team project, learn what they do reliably and where they fail, verify "
               "their output with tests and reviews, and judge their effect and risks with published evidence and their own "
               "measurements.")
ped = pedagogy()
CAT = json.load(open("D:/BTP/runs/cs601-02/state.json", encoding="utf-8"))
state = {
    "cco_compact": {
        "course_name": "AI in SDLC",
        "description": DESCRIPTION,
        "credits": CREDITS, "ltp": LTP, "weeks": WEEKS, "level": LEVEL,
        "target_students": {"programmes": ["BTECH-CSE", "BTECH-CSAI", "MTECH-CSE"], "year": "B.Tech 3rd/4th year; M.Tech",
                            "assumed_background": ["CSE201 Advanced Programming", "basic software engineering practice (Git, unit tests)"]},
        "central_question": "How do you get reliable software out of tools that are fast, fluent and sometimes wrong?",
    },
    "department": "CSE", "level": LEVEL, "credits": CREDITS, "ltp": LTP, "weeks": WEEKS, "midsem_after_week": 7, "lab_required": "yes",
    # regulation facts for this level, credit count and L-T-P (ProfsAgent's deterministic helpers; not design choices)
    "bloom_band": det.bloom_band(LEVEL), "co_count": det.co_count_for(CREDITS), "hours_budget": det.hours_budget(LTP, WEEKS),
    "template_rules": {"co_high_bloom": ped["co_high_bloom"], "proctored": ped["proctored"],
                       "outside_load_hours_per_week": det.outside_load_target(CREDITS)},
    "constraints": [
        {"id": "K01", "target": "schedule.weeks", "op": "==", "value": WEEKS, "hardness": "hard", "source": {"tag": "REGULATION", "ref": "UGREG-2025§2"}},
        {"id": "K02", "target": "course.credits", "op": "==", "value": CREDITS, "hardness": "hard", "source": {"tag": "USER", "ref": "request 18 Nov 2026"}},
        {"id": "K03", "target": "schedule.lecture_hours_per_week", "op": "==", "value": LTP["L"], "hardness": "hard", "source": {"tag": "USER", "ref": "13 lectures of 1.5 h"}}],
    "programmes": programmes, "programme_pos": programme_pos,
    # institutional data, copied from the KG snapshot of runs/cs601-02 (same catalogue): not design choices
    "activity_po_map": CAT["activity_po_map"], "known_course_uids": CAT["known_course_uids"], "course_levels": CAT["course_levels"],
    "cos": COS,
    "los": [{"id": i, "parent_co": co, **d, "bloom_level": b, "is_capstone": i == "CO3.LO4", "requires": [],
             "topic_hints": [t["title"] for m in modules for t in m["topics"] if i in t["serves_los"]],
             "hands_on": any(t["hands_on"] for m in modules for t in m["topics"] if i in t["serves_los"]),
             "est_lecture_h": 1.5 * sum(1 for m in modules for t in m["topics"] if i in t["serves_los"])} for i, co, b, d in LOS],
    "copo": copo,
    "modules": modules, "schedule": schedule, "assessment": assessment,
    "labs_tutorials": {"concerns": [], "missing": [], "labs": labs, "tutorials": [], "infra_requirements": [
        "a free-tier AI coding assistant or agent for every student", "GitHub accounts with Actions enabled", "Python 3.11+ with pytest"]},
    "positioning": {"concerns": [], "missing": [], "prerequisites": [
        {"kind": "mandatory", "course_uid": "CSE201", "alternatives": [],
         "relied_topics": ["building multi-component programs", "unit testing", "version control and collaboration", "object-oriented design"],
         "justification": "Students must be able to build, test and version a multi-module program before they can judge AI-written code.",
         "level_check": "lower_level", "sources": [{"tag": "CATALOGUE", "ref": "CSE201", "basis": "IIIT-D catalogue: Advanced Programming"}]}],
        "comparable": [{"kind": "internal", "ref": "CSE701",
                        "note": ("CSE701 Topics in Software Engineering: AI in SE (4 credits, 7xx) is a research course on data and ML "
                                 "for software engineering: repository mining, defect prediction, project health and bug triage from "
                                 "papers. AI in SDLC is a 2-credit 4xx practice course: students use LLM assistants and agents in every "
                                 "lifecycle phase, verify their output and judge their effect and risks. Overlap is limited to the "
                                 "requirements, repair, testing and review topics, taught here hands-on with current tools.")}]},
    "resources": resources,
    # the course form as the department's sheet reads it (written for this design, not filled in by ProfsAgent)
    "cco": {"concerns": [], "missing": [], "ambiguities": [], "conflicts": [], "fields": {
        "course_name": {"status": "given", "raw": "AI in SDLC", "value": "AI in SDLC"},
        "short_description": {"status": "given", "raw": DESCRIPTION, "value": DESCRIPTION},
        "target_students": {"status": "given", "raw": "B.Tech CSE/CSAI 3rd and 4th year; M.Tech CSE", "value": None,
                            "programmes": ["BTECH-CSE", "BTECH-CSAI", "MTECH-CSE"], "unmapped_programmes": [],
                            "assumed_background": ["CSE201 Advanced Programming", "basic software engineering practice (Git, unit tests)"]},
        "level_or_code": {"status": "given", "raw": "4xx (code to be assigned)", "value": None, "code": None, "level": LEVEL},
        "credits": {"status": "given", "raw": str(CREDITS), "value": CREDITS},
        "ltp": {"status": "given", "raw": "1.5-0-1", "value": None, **LTP},
        "semester_weeks": {"status": "given", "raw": str(WEEKS), "value": WEEKS},
        "lab": {"status": "given", "raw": "Six 2-hour labs with AI coding tools", "value": None, "required": "yes",
                "infrastructure": ["a free-tier AI coding assistant or agent for every student", "GitHub with Actions", "Python 3.11+ with pytest"]}}},
    "defaults": {"ltp": LTP, "weeks": WEEKS, "credits": CREDITS, "level": LEVEL, "midsem_after_week": 7, "constraints": [], "assumptions": []},
    "narrative": {"concerns": [], "missing": [], "grounding": [],
        "course_description": DESCRIPTION,
        "sequencing_rationale": ("The course follows the lifecycle: first how AI tools work and where they enter it, then requirements and "
                                 "design, code and review, tests and debugging, and last security, delivery, maintenance, measurement and "
                                 "policy. Each lecture builds on the artefacts of the one before, as the team project does."),
        "assessment_rationale": ("Quizzes and the two exams (50%, proctored) check each student's own understanding; the labs practise each "
                                 "module's skill with the tools; the team project carries the whole lifecycle and ends with measured "
                                 "results and an AI-use policy, so the highest outcomes are assessed on real work."),
        "positioning_rationale": ("Builds on CSE201 Advanced Programming. CSE701 (Topics in Software Engineering: AI in SE) is a 7xx research "
                                  "course on data and ML for software engineering; this 2-credit 4xx course is hands-on practice with "
                                  "current LLM assistants and agents across the lifecycle.")},
    "design_source": {
        "kind": "hand-authored by Claude at the user's request (not a ProfsAgent Phase 1 run)",
        "modelled_on": ["SWEBOK V4.0 lifecycle knowledge areas", "Generative AI for Effective Software Development (Springer 2024)",
                        "published studies of AI in requirements, testing, repair, security and productivity (see resources)"],
        "input": "user request, 18 Nov 2026: a 2-credit course of about 13 lectures named 'AI in SDLC'; COs, LOs and the course design written by hand, not generated",
        "made_for": "regenerating the course from the start; the delivery stages (modes 1-3) run from this design",
        "generator": "outputs/courses/ai_in_sdlc/make_design.py",
    },
}

# ---------------------------------------------------------------- own checks
lo_ids = {lo["id"] for lo in state["los"]}
assert {x for m in modules for t in m["topics"] for x in t["serves_los"]} == lo_ids
assert {a["lo_id"] for c in assessment["components"] for i in c["instances"] for a in i["assesses"]} == lo_ids
assert abs(sum(c["weight_pct"] for c in assessment["components"]) - 100) < 1e-9
assert all(lo["bloom_level"] <= next(c for c in COS if c["id"] == lo["parent_co"])["bloom_level"] for lo in state["los"])
assert all(WEEK[r] < WEEK[t["id"]] for m in modules for t in m["topics"] for r in t["requires"])
RUN.mkdir(parents=True, exist_ok=True)
(RUN / "state.json").write_text(json.dumps(state, indent=1, ensure_ascii=False), encoding="utf-8")
print("written", RUN / "state.json", "| COs", len(COS), "LOs", len(LOS), "lectures", len(order), "labs", len(labs), "CO-PO", len(copo))
