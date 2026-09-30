"""The standard agent loop: context → prompt → schema-validated JSON → deterministic validators → bounded repair.

Repair (R1) is scoped to one component, bounded (≤ max_rounds) and monotone: a patch is accepted only if the
number of validator ERRORS strictly decreases and it does not introduce a new error code. Otherwise the loop
stops and the remaining violations are escalated to the professor at the next gate (non-negotiable 7).
"""
from __future__ import annotations

import copy
import json
from typing import Callable

from pydantic import BaseModel, ValidationError

from profsagent.llm.prompts import load_prompt
from profsagent.models.io import OUTPUT_MODELS, RepairPatch
from profsagent.validate import rules


def call(rt, pid: str, ctx: dict, role: str = "generate") -> tuple[BaseModel, dict]:
    p = load_prompt(pid)
    system, user = p.render(**ctx)
    temp = float(p.meta.get("temperature", 0.2) or 0.2)
    obj, rec = rt.llm.structured(system=system, user=user, model_cls=OUTPUT_MODELS[pid], role=role, temperature=temp,
                                 prompt_id=pid, prompt_version=p.version, run_id=rt.run_id)
    rt.log(f"  [{pid}] ok via {rec.endpoint} · {rec.prompt_tokens}+{rec.output_tokens} tok · {rec.latency_s}s"
           + (f" · schema-retries {rec.schema_retries}" if rec.schema_retries else ""))
    return obj, {"prompt_id": pid, "prompt_version": p.version, "endpoint": rec.endpoint, "tokens": rec.prompt_tokens + rec.output_tokens}


def _find(comp, ident):
    """Yield (container_list, index, item) for items whose id/type equals ident, searching nested lists."""
    stack = [comp]
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, list):
            for i, it in enumerate(cur):
                if isinstance(it, dict) and (it.get("id") == ident or (it.get("type") == ident and "instances" in it)):
                    yield cur, i, it
                stack.append(it)


def _lists_of_dicts(comp):
    stack, out = [comp], []
    while stack:
        cur = stack.pop()
        if isinstance(cur, dict):
            stack.extend(cur.values())
        elif isinstance(cur, list):
            if cur and all(isinstance(x, dict) for x in cur):
                out.append(cur)
            stack.extend(cur)
    return out


def apply_patch(comp: dict, patch: RepairPatch, frozen: set[str]) -> tuple[dict, list[str]]:
    new = copy.deepcopy(comp)
    notes = []
    for op in patch.ops:
        target = op.id or (op.node or {}).get("id")
        if target and target in frozen:
            notes.append(f"skipped {op.op} on frozen {target}")
            continue
        if op.op == "update":
            hits = list(_find(new, op.id))
            if not hits:
                notes.append(f"update: {op.id} not found")
                continue
            _, _, it = hits[0]
            if op.field:
                it[op.field] = op.value
            elif isinstance(op.value, dict):
                it.update(op.value)
        elif op.op == "remove":
            hits = list(_find(new, op.id))
            for lst, i, _ in hits[:1]:
                lst.pop(i)
            if not hits:
                notes.append(f"remove: {op.id} not found")
        elif op.op == "add" and op.node:
            node = op.node
            cands = _lists_of_dicts(new)
            if not cands:
                notes.append("add: no target list")
                continue
            prefix = str(node.get("id", "")).split(".")[0].split(":")[0]

            def score(lst):
                keys = set(lst[0].keys())
                s = len(keys & set(node.keys()))
                if prefix and any(str(x.get("id", "")).startswith(prefix) for x in lst):
                    s += 3
                return s
            best = max(cands, key=score)
            best.append(node)
    return new, notes


def generate(rt, pid: str, ctx: dict, *, apply: Callable[[dict, dict], dict], stages: list[str],
             frozen: set[str] | None = None, max_rounds: int = 3, role: str = "generate") -> tuple[dict, list[dict], dict]:
    """Returns (component_json, violations_after, trace)."""
    obj, meta = call(rt, pid, ctx, role)
    comp = obj.model_dump()
    state = apply(copy.deepcopy(rt.state), comp)
    vs = rules.run(state, stages)
    trace = {"generator": meta, "initial_errors": len(rules.errors(vs)), "initial_warnings": len(vs) - len(rules.errors(vs)), "repairs": []}
    rt.log(f"  [{pid}] validators: {trace['initial_errors']} errors, {trace['initial_warnings']} warnings")
    frozen = frozen or set()
    feedback = None
    for rnd in range(1, max_rounds + 1):
        errs = rules.errors(vs)
        if not errs:
            break
        try:
            patch, pmeta = call(rt, "R1", {
                "component": comp, "component_prompt_id": pid, "violations": [x for x in vs if x["severity"] == "error"][:40],
                "frozen_ids": sorted(frozen), "round": rnd,
                "context_min": {**{k: x for k, x in ctx.items() if len(dumps(x)) < 6000},
                                **({"previous_patch_rejected_because": feedback} if feedback else {})}})
        except Exception as e:  # noqa: BLE001
            trace["repairs"].append({"round": rnd, "accepted": False, "why": f"R1 failed: {e}"[:200]})
            break
        cand, notes = apply_patch(comp, patch, frozen)
        try:
            cand = OUTPUT_MODELS[pid].model_validate(cand).model_dump()
        except ValidationError as e:
            trace["repairs"].append({"round": rnd, "accepted": False, "why": f"patched component invalid: {str(e)[:200]}", "notes": notes})
            break
        vs2 = rules.run(apply(copy.deepcopy(rt.state), cand), stages)
        e1, e2 = rules.errors(vs), rules.errors(vs2)
        new_codes = {x["code"] for x in e2} - {x["code"] for x in e1}
        ok = len(e2) < len(e1) and not new_codes
        trace["repairs"].append({"round": rnd, "accepted": ok, "errors_before": len(e1), "errors_after": len(e2),
                                 "new_error_codes": sorted(new_codes), "ops": len(patch.ops), "notes": notes,
                                 "unfixable": [u.model_dump() for u in patch.unfixable], "endpoint": pmeta["endpoint"]})
        rt.log(f"  [R1 round {rnd}] errors {len(e1)} → {len(e2)} {'ACCEPT' if ok else 'REJECT'}"
               + (f" (new codes {sorted(new_codes)})" if new_codes else ""))
        if not ok:  # keep the last accepted component; tell R1 why this patch was rejected and try again
            intro = "; ".join(x["message"] for x in e2 if x["code"] in new_codes)[:800]
            feedback = f"your previous patch left {len(e2)} errors (was {len(e1)})" + (f" and introduced new error types {sorted(new_codes)}: {intro}" if new_codes else "")
            continue
        comp, vs, feedback = cand, vs2, None
    trace["final_errors"] = len(rules.errors(vs))
    trace["final_warnings"] = len(vs) - trace["final_errors"]
    return comp, vs, trace


def dumps(x) -> str:
    return json.dumps(x, ensure_ascii=False, default=str)
