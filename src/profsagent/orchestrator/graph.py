"""LangGraph orchestration of S1–S9 with three professor gates.

State checkpointed to runs/<run_id>/checkpoint.sqlite (thread_id = run_id). Heavy objects (LLM client, KG,
design graph) live in a Runtime registry keyed by run_id, not in the checkpointed state; each node re-attaches
from runs/<run_id>/state.json, so a run can be resumed in a new process.

Gates use `interrupt()`: the caller sees {gate, summary, open_errors, open_warnings} and resumes with
Command(resume={"decision": "approve"|"reject", "by": "...", "comment": "..."}). With auto_approve=True the gate
records an automatic approval (dev runs only — the approval is labelled "auto").
"""
from __future__ import annotations

import sqlite3
from typing import TypedDict

from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from profsagent.agents import pipeline as P
from profsagent.render.proposal import render
from profsagent.validate import rules

_RT: dict[str, P.Runtime] = {}


class S(TypedDict, total=False):
    run_id: str
    auto_approve: bool
    done: list[str]
    rejected_at: str


def _rt(state: S) -> P.Runtime:
    rid = state["run_id"]
    if rid not in _RT:
        _RT[rid] = P.attach_runtime(rid)
    return _RT[rid]


def _stage(fn, name):
    def node(state: S) -> S:
        rt = _rt(state)
        if name in rt.state.get("stages_done", []):
            rt.log(f"(skip {name}: already done)")
        else:
            fn(rt)
            rt.state.setdefault("stages_done", []).append(name)
            rt.save()
        return {"done": state.get("done", []) + [name]}
    node.__name__ = name
    return node


def _gate(name, summary_fn):
    def node(state: S) -> S:
        rt = _rt(state)
        if any(a["gate"] == name for a in rt.state.get("approvals", [])):
            return {}
        vs = P.all_violations(rt.state)
        payload = {"gate": name, "summary": summary_fn(rt.state), "open_errors": len(rules.errors(vs)),
                   "open_warnings": len(vs) - len(rules.errors(vs))}
        if state.get("auto_approve"):
            decision = {"decision": "approve", "by": "auto (dev run)", "comment": "auto-approved; not a professor decision"}
        else:
            decision = interrupt(payload)
        P.gate(rt, name, decision)
        if decision.get("decision") != "approve":
            return {"rejected_at": name}
        return {}
    node.__name__ = name
    return node


def _after_gate(state: S) -> str:
    return "stop" if state.get("rejected_at") else "go"


def _render(state: S) -> S:
    rt = _rt(state)
    render(rt)
    return {}


def build(checkpoint_path: str):
    g = StateGraph(S)
    g.add_node("s1_intake", _stage(P.s1_intake, "s1_intake"))
    g.add_node("s2_positioning", _stage(P.s2_positioning, "s2_positioning"))
    g.add_node("s3_constraints", _stage(P.s3_constraints, "s3_constraints"))
    g.add_node("gate1_context", _gate("gate1_context", lambda st: {
        "cco_conflicts": st["cco"]["conflicts"], "assumptions": st["defaults"]["assumptions"],
        "prerequisites": [p["course_uid"] for p in st["positioning"]["prerequisites"]],
        "constraint_conflicts": st.get("constraint_conflicts")}))
    g.add_node("s4_outcomes", _stage(P.s4_outcomes, "s4_outcomes"))
    g.add_node("gate2_outcomes", _gate("gate2_outcomes", lambda st: {
        "cos": [c["statement"] for c in st["cos"]], "n_los": len(st["los"]), "copo": len(st["copo"])}))
    g.add_node("s5_structure", _stage(P.s5_structure, "s5_structure"))
    g.add_node("s7_activities_assessment", _stage(P.s7_activities_assessment, "s7_activities_assessment"))
    g.add_node("s8_resources", _stage(P.s8_resources, "s8_resources"))
    g.add_node("s9_narrative", _stage(P.s9_narrative, "s9_narrative"))
    g.add_node("render", _render)
    g.add_node("gate3_proposal", _gate("gate3_proposal", lambda st: {"rendered": "proposal.md"}))

    g.add_edge(START, "s1_intake")
    g.add_edge("s1_intake", "s2_positioning")
    g.add_edge("s2_positioning", "s3_constraints")
    g.add_edge("s3_constraints", "gate1_context")
    g.add_conditional_edges("gate1_context", _after_gate, {"go": "s4_outcomes", "stop": END})
    g.add_edge("s4_outcomes", "gate2_outcomes")
    g.add_conditional_edges("gate2_outcomes", _after_gate, {"go": "s5_structure", "stop": END})
    g.add_edge("s5_structure", "s7_activities_assessment")
    g.add_edge("s7_activities_assessment", "s8_resources")
    g.add_edge("s8_resources", "s9_narrative")
    g.add_edge("s9_narrative", "render")
    g.add_edge("render", "gate3_proposal")
    g.add_edge("gate3_proposal", END)
    conn = sqlite3.connect(checkpoint_path, check_same_thread=False)
    return g.compile(checkpointer=SqliteSaver(conn))


def register(rt: P.Runtime) -> None:
    _RT[rt.run_id] = rt
