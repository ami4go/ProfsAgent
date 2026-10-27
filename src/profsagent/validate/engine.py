"""Validation engine (validation layer v2): the one entry point to validation. It selects the run's profile
(configure), runs a stage's checks, annotates every violation (record v2), applies registered deterministic fixers, and
reports what stays open for R1 repair or the professor.

    record.py      the violation record every checker returns
    rules.py       the catalogue of checks (with regulation.py, constraints.py, semantic.py, text.py), no LLM
    llm_check.py   the optional LLM check (llm profile only)
    engine.py      configure -> check -> deterministic fixers -> R1 repair (agents/loop.generate) -> open items, gates
    report.py      the readable report shown at gates and in the proposal

Fixers are accepted only if errors strictly drop and no new error code appears.

Violation record v2 = the rules.v() fields {code, severity, nodes, message, evidence[, fix_hint], stage} plus
    family      rule | regulation | constraint | graph | kg | semantic | resource | fit
    fixable_by  fixer | repair | professor
The v2 fields are bookkeeping only: strip_v2() removes them before violations are shown to R1, so repair prompts
(and their cache keys) are unchanged.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Callable

from profsagent.config import validation_profile
from profsagent.validate import llm_check, rules, semantic
from profsagent.validate.record import errors  # noqa: F401 (callers take errors from the engine, not from rules)

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
    "V14": "kg", "V16": "kg", "V17": "kg", "V20": "kg", "VKG-PREC": "kg", "VKG-DUP": "kg", "VKG-NORM": "kg",
    # meaning compared with a local embedding model (warnings until calibrated)
    "VS-LOCOPY": "semantic", "VS-LOFIT": "semantic", "VS-CODUP": "semantic",
    # external verification of references
    "V15": "resource",
    # internal rules on a single component
    "T2": "rule", "T3": "rule", "V1": "rule", "V3": "rule", "V6": "rule", "V7": "rule", "V8": "rule", "V9": "rule",
    "V10": "rule", "V11": "rule", "V12": "rule", "V13": "rule", "V18": "rule", "V19": "rule", "V21": "rule", "V23": "rule",
    "VA-LOAD": "rule", "VA-MARKS": "rule", "VA-ORDER": "rule", "VA-PROJ": "rule", "VA-TIME": "rule", "VB": "rule",
    "VCO-DUP": "rule", "VCO-SPREAD": "rule", "VCOPO-ACT": "rule", "VLO-COPY": "rule", "VLO-COUNT": "rule",
    "VLO-DUP": "rule", "VT-SIZE": "rule", "VT-LEN": "rule", "VT-TEMPLATE": "rule",
    # the course frame against the audience and practice the course implies (level, lab): the professor decides
    "VC-AUDIENCE": "fit", "VC-NOLAB": "fit",
}
# Families whose findings only the professor can settle, whatever stage raised them (R1 must not "repair" a level or L-T-P).
PROFESSOR_FAMILIES = {"fit"}

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
        x["family"] = FAMILY.get(x["code"]) or ("llm" if x["code"].startswith("LLM:") else "rule")
        x["fixable_by"] = ("fixer" if x["code"] in fixable else
                           "professor" if x["family"] in PROFESSOR_FAMILIES else
                           "repair" if x.get("stage") in REPAIRABLE_STAGES else "professor")
    return vs


def configure(run_cfg: dict, llm=None, run_id: str | None = None) -> str:
    """Select the run's validation profile (config/validation.yaml, $PROFSAGENT_VALIDATION) and set up its checkers:
      core  rules + IIIT-D knowledge-graph checks (the default: 23/23 planted defects, no AI calls; eval/compare_validation)
      full  core + meaning checks with the local embedding model
      llm   hard rules in code + one LLM check per stage (validate/llm_check.py; 4/23 when it was the only checker)
    Recorded in run_cfg so --resume / --continue keep the profile the run started with."""
    profile = run_cfg["validation_profile"] = run_cfg.get("validation_profile") or validation_profile()
    if profile == "full":
        semantic.configure_local()   # PROFSAGENT_SEMANTIC=off still skips it
    else:
        semantic.configure(None)
    llm_check.configure(llm if profile == "llm" else None, run_id)
    return profile


def check(state: dict, stages: list[str] | None = None) -> list[dict]:
    """rules.run with record v2 annotations. Under the llm validation profile (validate/llm_check.py configured), only
    the hard rules come from code and the judgement items come from one LLM check of the same stages."""
    vs = rules.run(state, stages)
    if llm_check.enabled():
        hard = llm_check.hard_rules()
        vs = [x for x in vs if x["code"] in hard] + llm_check.check(state, stages)
    return annotate(vs)


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


# ------------------------------------------------------------------ gates: block on open errors, override with a reason
def recorded(state: dict) -> list[dict]:
    """Every violation recorded so far (state["violations"] by stage), annotated with record v2 fields."""
    return annotate([dict(x) for vs in (state.get("violations") or {}).values() for x in vs])


def coverage(state: dict) -> dict:
    """What validation looked at: stages checked, errors/warnings by family, and constraint coverage."""
    from collections import Counter
    from profsagent.validate import constraints
    vs = recorded(state)
    errs = rules.errors(vs)
    return {"stages_checked": sorted((state.get("violations") or {}).keys()), "errors": len(errs), "warnings": len(vs) - len(errs),
            "errors_by_family": dict(Counter(x["family"] for x in errs)),
            "constraints": constraints.coverage(state) if state.get("constraints") is not None else None}


def gate_view(state: dict, cap: int = 40) -> dict:
    """What a gate shows: blocked or not, the open errors (grouped by who can close them) and the coverage report.
    `report` is the readable version: open errors under plain headings, repeats merged, warnings as counts."""
    from profsagent.validate import report
    vs = recorded(state)
    errs = rules.errors(vs)
    order = {"professor": 0, "repair": 1, "fixer": 2}
    items = sorted(({"code": x["code"], "stage": x.get("stage"), "nodes": x["nodes"][:6], "message": x["message"][:200],
                     "fixable_by": x["fixable_by"]} for x in errs), key=lambda i: (order.get(i["fixable_by"], 3), i["stage"] or "", i["code"]))
    return {"blocked": bool(errs), "open_codes": sorted({x["code"] for x in errs}), "open": items[:cap],
            "open_total": len(errs), "coverage": coverage(state), "report": report.lines(vs, errors_only=True)}


def resolve_gate(view: dict, decision: dict | None, auto: bool) -> tuple[dict | None, str | None]:
    """Gate policy. Returns (decision to record, problem). A problem means: ask the professor again.
    - no open errors: the professor's decision stands;
    - open errors: approving needs a reason, recorded as an override of the open error codes; rejecting is always allowed;
    - dev / benchmark runs (auto): approve, and record the override as "would have blocked"."""
    if auto:
        d = {"decision": "approve", "by": "auto (dev run)", "comment": "auto-approved; not a professor decision"}
        if view["blocked"]:
            d["override"] = {"codes": view["open_codes"], "errors": view["open_total"], "reason": "auto-approved dev run",
                             "would_block": True}
        return d, None
    decision = dict(decision or {})
    if decision.get("decision") != "approve" or not view["blocked"]:
        return decision, None
    reason = str(decision.get("reason") or decision.get("comment") or "").strip()
    if not reason:
        return None, (f"{view['open_total']} open errors ({', '.join(view['open_codes'])}): approving needs a reason "
                      f"(it is recorded as an override), or reject to stop the run")
    decision["override"] = {"codes": view["open_codes"], "errors": view["open_total"], "reason": reason}
    return decision, None


from profsagent.validate import fixers  # noqa: E402,F401  (registers the deterministic fixers)
