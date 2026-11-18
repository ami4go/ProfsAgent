"""Delivery mode 2: a whole lecture taught by a playlist of YouTube clips, found and checked by ProfsAgent on its own.

Architecture (see docs/ytlecture.md): a deterministic orchestrator (orchestrator.py) runs fixed stages and checkpoints them;
seven AI sub-agents (agents.py, prompts/ytlecture/Y1-Y7) do the judgement steps; every agent output is checked by code;
tools (tools.py, evidence.py) do the searching and reading; assembly (assemble.py) is pure code.

    from profsagent.ytlecture import run
    run("cs601-02", ["W01.L1", "W01.L2"])
"""
from __future__ import annotations


def run(run_id: str, lectures: list[str] | None = None, refresh: bool = False, log=print, redo_lectures: bool = False,
        redo_search: bool = False) -> dict:
    from profsagent.ytlecture.orchestrator import Orchestrator
    return Orchestrator(run_id, log=log, refresh=refresh, redo_lectures=redo_lectures, redo_search=redo_search).run(lectures)
