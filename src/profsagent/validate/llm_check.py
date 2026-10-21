"""The "llm" validation profile: exact rules in code + one LLM check per stage (config/llm_check.yaml, prompt C1).

engine.check() uses this module when it is configured (the pipeline does it for profile llm): the rule findings are
filtered to the hard rules, and the LLM check adds findings for the judgement items of the stages being checked.
LLM findings use the normal record shape (code "LLM:<stage>.<item>", severity from the checklist, so the same item is
always an error or always a warning), so fixers, R1 repair, gates and the report treat them like any other finding.

Cost control: results are cached per (stages, checked content); a run stops calling the LLM after
budget_calls_per_run calls (later checks then use the hard rules only, and say so). A failed call never stops a run.
review_design() checks a whole finished design in one call (used by scripts/compare_validation.py).
"""
from __future__ import annotations

import hashlib
import json

from pydantic import BaseModel, Field

from profsagent.config import load_yaml
from profsagent.validate.record import ERR, WARN

_llm = None
_run_id = None
_calls = 0
_cache: dict[str, list[dict]] = {}
STAGE_OF = {"schedule": "structure"}   # S5 checks structure + schedule together: one LLM call for both


class LLMFinding(BaseModel):
    item: str
    nodes: list[str] = Field(default_factory=list)
    issue: str
    fix: str = ""


class LLMCheckResult(BaseModel):
    findings: list[LLMFinding] = Field(default_factory=list)


def cfg() -> dict:
    return load_yaml("config/llm_check.yaml")


def hard_rules() -> set[str]:
    return set(cfg()["hard_rules"])


def configure(llm, run_id: str | None = None) -> None:
    """llm=None switches the LLM check off (engine.check then runs every rule, as before)."""
    global _llm, _run_id, _calls
    _llm, _run_id, _calls = llm, run_id, 0
    _cache.clear()


def enabled() -> bool:
    return _llm is not None


def calls_made() -> int:
    return _calls


# ------------------------------------------------------------------ what the LLM sees
def _lo_brief(state):
    return [{"id": lo["id"], "parent_co": lo.get("parent_co"), "statement": lo["statement"], "bloom_level": lo.get("bloom_level")}
            for lo in state.get("los", [])]


def design_part(state: dict, stage: str) -> tuple[object, object]:
    """(the part to check, what it builds on) for one checklist stage."""
    cos = [{k: c.get(k) for k in ("id", "statement", "verb", "bloom_level", "condition", "degree")} for c in state.get("cos", [])]
    if stage == "positioning":
        p = state.get("positioning") or {}
        return {k: p.get(k) for k in ("prerequisites", "overlaps", "anti_requisites", "comparable", "existence")}, None
    if stage == "cos":
        return cos, None
    if stage == "copo":
        used = {m["po_uid"] for m in state.get("copo", [])}
        pos = [{"uid": p.get("uid"), "text": p.get("text")} for p in state.get("programme_pos", []) if p.get("uid") in used]
        maps = [{k: m.get(k) for k in ("co_id", "po_uid", "strength_provisional", "justification")} for m in state.get("copo", [])]
        return maps, {"cos": cos, "programme_outcomes": pos}
    if stage == "los":
        return [{k: lo.get(k) for k in ("id", "parent_co", "statement", "verb", "bloom_level", "requires")} for lo in state.get("los", [])], \
            {"cos": cos}
    if stage == "structure":
        tw = (state.get("schedule") or {}).get("topic_weeks", {})
        mods = [{"id": m["id"], "title": m["title"],
                 "topics": [{k: t.get(k) for k in ("id", "title", "est_hours", "serves_los", "requires", "outside_load_hours")}
                            | {"weeks": tw.get(t["id"], [])} for t in m["topics"]]} for m in state.get("modules", [])]
        return mods, {"los": _lo_brief(state), "topic_groups": state.get("topic_groups")}
    if stage == "labs":
        lt = state.get("labs_tutorials") or {}
        return {"labs": lt.get("labs"), "tutorials": lt.get("tutorials")}, {"los": _lo_brief(state)}
    if stage == "assessment":
        comps = [{"type": c["type"], "weight_pct": c.get("weight_pct"), "weight_justification": c.get("weight_justification"),
                  "instances": [{k: i.get(k) for k in ("id", "format", "release_week", "due_week", "est_student_hours")}
                                | {"assesses": [{"lo": a.get("lo_id"), "bloom_level": a.get("bloom_level")} for a in i.get("assesses", [])]}
                                for i in c.get("instances", [])]}
                 for c in (state.get("assessment") or {}).get("components", [])]
        return comps, {"los": _lo_brief(state), "topic_weeks": (state.get("schedule") or {}).get("topic_weeks")}
    return None, None


def _payload(state: dict, stages: list[str]) -> dict:
    c = cfg()
    out = []
    for st in stages:
        items = c["stages"].get(st)
        if not items:
            continue
        design, ctx = design_part(state, st)
        if design is None:
            continue
        out.append({"stage": st, "items": [{"id": f"{st}.{i['id']}", "check": i["check"]} for i in items], "design": design,
                    "context": ctx})
    form = {k: (str(v)[:1200] if v is not None else None) for k, v in (state.get("form") or {}).items()}
    frame = {k: state.get(k) for k in c["frame_fields"]} | {"credits": (state.get("defaults") or {}).get("credits")}
    cons = [{k: x.get(k) for k in ("id", "target", "op", "value", "hardness", "raw")} for x in state.get("constraints", [])]
    return {"brief": form, "frame": frame, "constraints": cons, "stages": out}


def _findings(obj: LLMCheckResult, stages: list[str], endpoint: str | None) -> list[dict]:
    sev = {f"{st}.{i['id']}": i["severity"] for st in stages for i in cfg()["stages"].get(st, [])}
    text = {f"{st}.{i['id']}": i["check"] for st in stages for i in cfg()["stages"].get(st, [])}
    out = []
    for f in obj.findings:
        item = f.item if f.item in sev else next((k for k in sev if k.endswith("." + f.item)), None)
        stage = (item or (stages[0] + ".other")).split(".")[0]
        out.append({"code": f"LLM:{item or stage + '.other'}", "severity": ERR if sev.get(item) == "error" else WARN,
                    "nodes": [str(n) for n in f.nodes][:12], "message": f.issue, "fix_hint": f.fix or text.get(item, ""),
                    "evidence": {"checked_by": endpoint, "item": item}, "stage": stage})
    return out


def _note(stage: str, message: str) -> dict:
    return {"code": "LLM:unavailable", "severity": WARN, "nodes": [], "message": message, "evidence": {}, "stage": stage}


def ask(llm, state: dict, stages: list[str], run_id: str | None = None) -> tuple[list[dict], dict]:
    """One C1 call for the given checklist stages. Returns (findings, call info)."""
    from profsagent.llm.prompts import load_prompt
    p = load_prompt("C1")
    payload = _payload(state, stages)
    if not payload["stages"]:
        return [], {"calls": 0}
    system, user = p.render(**payload)
    obj, rec = llm.structured(system=system, user=user, model_cls=LLMCheckResult, role=cfg()["role"], temperature=0,
                              prompt_id="C1", prompt_version=p.version, run_id=run_id)
    ep = getattr(rec, "endpoint", None)
    return _findings(obj, [s["stage"] for s in payload["stages"]], ep), {"calls": 1, "endpoint": ep}


def check(state: dict, stages: list[str] | None) -> list[dict]:
    """LLM findings for the checklist stages among `stages` (engine.check calls this under the llm profile)."""
    global _calls
    if not _llm:
        return []
    wanted = list(dict.fromkeys(STAGE_OF.get(s, s) for s in (stages or list(cfg()["stages"]))))
    wanted = [s for s in wanted if s in cfg()["stages"]]
    if not wanted:
        return []
    payload = _payload(state, wanted)
    key = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
    if key in _cache:
        return [dict(x) for x in _cache[key]]
    if _calls >= cfg()["budget_calls_per_run"]:
        return [_note(wanted[0], f"LLM check budget ({cfg()['budget_calls_per_run']} calls) used up; only the hard rules "
                                 "checked this stage")]
    _calls += 1
    try:
        out, _ = ask(_llm, state, wanted, _run_id)
    except Exception as e:  # noqa: BLE001 — an unavailable checker must not stop the design run
        return [_note(wanted[0], f"LLM check unavailable ({type(e).__name__}); only the hard rules checked this stage")]
    _cache[key] = out
    return [dict(x) for x in out]


def review_design(state: dict, llm, run_id: str | None = None) -> tuple[list[dict], dict]:
    """The whole finished design in one call (every checklist stage)."""
    return ask(llm, state, list(cfg()["stages"]), run_id)
