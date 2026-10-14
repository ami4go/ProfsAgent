"""Validation engine (validation layer v2): runs a stage's checks, annotates every violation (record v2), applies
registered deterministic fixers, and reports what stays open for R1 repair or the professor.

rules.py remains the catalogue of checks. This module adds the record and the flow used by agents/loop.generate:
    check -> deterministic fixers (accepted only if errors strictly drop, no new error code) -> R1 repair -> open items

Violation record v2 = the rules.v() fields {code, severity, nodes, message, evidence[, fix_hint], stage} plus
    family      rule | regulation | constraint | graph | kg | resource
    fixable_by  fixer | repair | professor
The v2 fields are bookkeeping only: strip_v2() removes them before violations are shown to R1, so repair prompts
(and their cache keys) are unchanged.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Callable

from profsagent.validate import rules

# Every code in rules.py is classified here (tests/test_validation_engine.py fails on an unclassified code).
FAMILY: dict[str, str] = {
    # institutional regulation and the IIIT-D course template
    "V2": "regulation", "V4": "regulation", "VA-REG": "regulation", "VA-MIDSEM": "regulation",
    "VA-PROCTOR": "regulation", "VCO-BL": "regulation", "VT-LOAD": "regulation",
    "VREG-WEEKS": "regulation", "VREG-CREDITS": "regulation", "VREG-LTP": "regulation",
    # the professor's typed constraints
    "VK": "constraint", "VK-CONTENT": "constraint", "VK-MALFORMED": "constraint", "VK-CONFLICT": "constraint",
    "VK-UNENFORCED": "constraint",
    # references between parts of the design, and dependency graphs
    "T1": "graph", "T4": "graph", "T5": "graph", "T10": "graph", "VLO-DAG": "graph", "VT-DAG": "graph", "VT-ORDER": "graph",
    "VTG-TAUGHT": "graph", "VCO-COVER": "graph",
    # facts taken from the institutional knowledge graph (catalogue, levels, topic overlap, weight priors)
    "V14": "kg", "V16": "kg", "V17": "kg", "V20": "kg",
    # external verification of references
    "V15": "resource",
    # internal rules on a single component
    "T2": "rule", "T3": "rule", "V1": "rule", "V3": "rule", "V6": "rule", "V7": "rule", "V8": "rule", "V9": "rule",
    "V10": "rule", "V11": "rule", "V12": "rule", "V13": "rule", "V18": "rule", "V19": "rule", "V21": "rule", "V23": "rule",
    "VA-LOAD": "rule", "VA-MARKS": "rule", "VA-ORDER": "rule", "VA-PROJ": "rule", "VA-TIME": "rule", "VB": "rule",
    "VCO-DUP": "rule", "VCO-SPREAD": "rule", "VCOPO-ACT": "rule", "VLO-COPY": "rule", "VLO-COUNT": "rule",
    "VLO-DUP": "rule", "VT-SIZE": "rule", "VT-LEN": "rule",
}

# Stages whose component is generated through agents/loop.generate, so R1 can repair it (S8 resources cannot).
REPAIRABLE_STAGES = {"positioning", "cos", "copo", "los", "structure", "schedule", "labs", "assessment"}
V2_KEYS = ("family", "fixable_by")


@dataclass(frozen=True)
class Fixer:
    """A deterministic fix for errors whose correct value a rule fully decides.
    fn(state, component, errors) -> (component, notes); state is the stage's input state (read-only)."""
    name: str
    codes: frozenset[str]
    fn: Callable[[dict, dict, list[dict]], tuple[dict, list[str]]]


FIXERS: list[Fixer] = []


def fixer(name: str, codes: list[str]):
    """Register a deterministic fixer for the given error codes."""
    def register(fn):
        FIXERS.append(Fixer(name, frozenset(codes), fn))
        return fn
    return register


def annotate(vs: list[dict]) -> list[dict]:
    fixable = {c for f in FIXERS for c in f.codes}
    for x in vs:
        x["family"] = FAMILY.get(x["code"], "rule")
        x["fixable_by"] = ("fixer" if x["code"] in fixable else
                           "repair" if x.get("stage") in REPAIRABLE_STAGES else "professor")
    return vs


def check(state: dict, stages: list[str] | None = None) -> list[dict]:
    """rules.run with record v2 annotations."""
    return annotate(rules.run(state, stages))


def strip_v2(vs: list[dict]) -> list[dict]:
    return [{k: v for k, v in x.items() if k not in V2_KEYS} for x in vs]


def error_codes(vs: list[dict]) -> list[str]:
    return sorted({x["code"] for x in rules.errors(vs)})


def apply_fixers(state: dict, comp: dict, apply: Callable[[dict, dict], dict], stages: list[str],
                 vs: list[dict]) -> tuple[dict, list[dict], list[dict]]:
    """Run each registered fixer whose codes are among the open errors. A fix is kept only if the error count strictly
    drops and no new error code appears (the rule R1 patches follow). Returns (component, violations, fix log)."""
    log = []
    for f in FIXERS:
        errs = rules.errors(vs)
        hit = [x for x in errs if x["code"] in f.codes]
        if not hit:
            continue
        cand, notes = f.fn(copy.deepcopy(state), copy.deepcopy(comp), hit)
        vs2 = check(apply(copy.deepcopy(state), cand), stages)
        e2 = rules.errors(vs2)
        new = {x["code"] for x in e2} - {x["code"] for x in errs}
        ok = len(e2) < len(errs) and not new
        log.append({"fixer": f.name, "accepted": ok, "errors_before": len(errs), "errors_after": len(e2),
                    "new_error_codes": sorted(new), "notes": notes})
        if ok:
            comp, vs = cand, vs2
    return comp, vs, log


def open_items(vs: list[dict]) -> list[dict]:
    """Errors still open after fixers and repair, and who can close them."""
    return [{"code": x["code"], "family": x.get("family"), "nodes": x["nodes"], "fixable_by": x.get("fixable_by")}
            for x in rules.errors(vs)]
