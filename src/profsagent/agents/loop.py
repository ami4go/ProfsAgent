"""The standard agent loop: context → prompt → schema-validated JSON → deterministic validators → bounded repair.

Repair (R1) is scoped to one component, bounded (≤ max_rounds) and monotone: a patch is accepted only if the
number of validator ERRORS strictly decreases and it does not introduce a new error code. R1 sees the current content
of the nodes the errors name (evidence_nodes). It stops early when it cannot help (see generate), and the remaining
violations are escalated to the professor at the next gate (non-negotiable 7).
"""
from __future__ import annotations

import copy
import json
from typing import Callable

from pydantic import BaseModel, ValidationError

from profsagent.config import models_cfg
from profsagent.llm.prompts import load_prompt
from profsagent.models.io import OUTPUT_MODELS, RepairPatch
from profsagent.validate import engine, rules


def temperature(meta: dict) -> float:
    """Prompt front-matter temperature; 0.2 only when none is declared (a declared 0 must stay 0)."""
    t = meta.get("temperature")
    return 0.2 if t is None or t == "" else float(t)


def call(rt, pid: str, ctx: dict, role: str = "generate", extra_user: str = "") -> tuple[BaseModel, dict]:
    p = load_prompt(pid)
    system, user = p.render(**ctx)
    if extra_user:
        user = f"{user}\n\n{extra_user}"
    obj, rec = rt.llm.structured(system=system, user=user, model_cls=OUTPUT_MODELS[pid], role=role, temperature=temperature(p.meta),
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


def _in_reach(err: dict, frozen: set[str]) -> bool:
    """R1 can work on an error unless only the professor can resolve it, or every node it names is frozen."""
    return err.get("fixable_by") != "professor" and not (err.get("nodes") and set(err["nodes"]) <= frozen)


def evidence_nodes(comp: dict, errs: list[dict], max_nodes: int = 25, max_chars: int = 2500) -> dict:
    """The current content of every node the errors name, so R1 patches what is there instead of recalling it."""
    out = {}
    for e in errs:
        for ident in e.get("nodes", []):
            if ident in out or len(out) >= max_nodes:
                continue
            hit = next(_find(comp, ident), None)
            if hit:
                s = dumps(hit[2])
                out[ident] = hit[2] if len(s) <= max_chars else {"id": ident, "truncated_json": s[:max_chars]}
    return out


def _regenerate_note(errs: list[dict]) -> str:
    return ('<context name="previous_attempt">Your previous answer for this component failed these checks (computed by '
            "programs, not opinions), and a minimal repair could not fix them. Produce the whole component again, following "
            "every rule above and avoiding these violations:\n" + dumps(engine.strip_v2(errs)[:30]) + "</context>")


def generate(rt, pid: str, ctx: dict, *, apply: Callable[[dict, dict], dict], stages: list[str],
             frozen: set[str] | None = None, max_rounds: int = 3, role: str = "generate") -> tuple[dict, list[dict], dict]:
    """Returns (component_json, violations_after, trace).

    Stopping rule: R1 is not called when no open error is within its reach (_in_reach), and stops when it proposes no
    change, repeats a rejected patch, or after `repair_stall_rounds` rejected patches in a row (config/models.yaml).
    Then, if `regenerate_on_stall` > 0 and nothing is frozen, the generator is called once more with the open errors
    as evidence, and its answer is kept only if it has fewer errors."""
    lim = models_cfg().get("limits", {})
    obj, meta = call(rt, pid, ctx, role)
    comp = obj.model_dump()
    state = apply(copy.deepcopy(rt.state), comp)
    vs = engine.check(state, stages)
    trace = {"generator": meta, "initial_errors": len(rules.errors(vs)), "initial_warnings": len(vs) - len(rules.errors(vs)),
             "initial_error_codes": engine.error_codes(vs), "repairs": []}
    rt.log(f"  [{pid}] validators: {trace['initial_errors']} errors, {trace['initial_warnings']} warnings")
    comp, vs, trace["fixes"] = engine.apply_fixers(rt.state, comp, apply, stages, vs)
    for f in trace["fixes"]:
        rt.log(f"  [fixer {f['fixer']}] errors {f['errors_before']} → {f['errors_after']} {'ACCEPT' if f['accepted'] else 'REJECT'}")
    frozen = frozen or set()
    feedback, rejected_in_row, rejected = None, 0, set()
    stall_limit = int(lim.get("repair_stall_rounds", 2))
    for rnd in range(1, max_rounds + 1):
        errs = rules.errors(vs)
        if not errs:
            break
        reach = [e for e in errs if _in_reach(e, frozen)]
        if not reach:
            trace["stop_reason"] = "no open error is within R1's reach (professor-only, or only frozen nodes)"
            break
        try:
            patch, pmeta = call(rt, "R1", {
                "component": comp, "component_prompt_id": pid, "violations": engine.strip_v2(reach)[:40],
                "violating_nodes": evidence_nodes(comp, reach), "frozen_ids": sorted(frozen), "round": rnd,
                "context_min": {**{k: x for k, x in ctx.items() if len(dumps(x)) < 6000},
                                **({"previous_patch_rejected_because": feedback} if feedback else {})}})
        except Exception as e:  # noqa: BLE001
            trace["repairs"].append({"round": rnd, "accepted": False, "why": f"R1 failed: {e}"[:200]})
            break
        if not patch.ops:
            trace["repairs"].append({"round": rnd, "accepted": False, "why": "R1 proposed no change",
                                     "unfixable": [u.model_dump() for u in patch.unfixable], "endpoint": pmeta["endpoint"]})
            trace["stop_reason"] = "R1 proposed no change"
            break
        cand, notes = apply_patch(comp, patch, frozen)
        try:
            cand = OUTPUT_MODELS[pid].model_validate(cand).model_dump()
        except ValidationError as e:
            trace["repairs"].append({"round": rnd, "accepted": False, "why": f"patched component invalid: {str(e)[:200]}", "notes": notes})
            break
        key = dumps(cand)
        if key in rejected:
            trace["repairs"].append({"round": rnd, "accepted": False, "why": "R1 repeated a rejected patch", "endpoint": pmeta["endpoint"]})
            trace["stop_reason"] = "R1 repeated a rejected patch"
            break
        vs2 = engine.check(apply(copy.deepcopy(rt.state), cand), stages)
        e1, e2 = rules.errors(vs), rules.errors(vs2)
        new_codes = {x["code"] for x in e2} - {x["code"] for x in e1}
        ok = len(e2) < len(e1) and not new_codes
        trace["repairs"].append({"round": rnd, "accepted": ok, "errors_before": len(e1), "errors_after": len(e2),
                                 "new_error_codes": sorted(new_codes), "ops": len(patch.ops), "notes": notes,
                                 "unfixable": [u.model_dump() for u in patch.unfixable], "endpoint": pmeta["endpoint"]})
        rt.log(f"  [R1 round {rnd}] errors {len(e1)} → {len(e2)} {'ACCEPT' if ok else 'REJECT'}"
               + (f" (new codes {sorted(new_codes)})" if new_codes else ""))
        if not ok:  # keep the last accepted component; tell R1 why this patch was rejected and try again
            rejected.add(key)
            rejected_in_row += 1
            if rejected_in_row >= stall_limit:
                trace["stop_reason"] = f"{rejected_in_row} rejected patches in a row"
                break
            intro = "; ".join(x["message"] for x in e2 if x["code"] in new_codes)[:800]
            feedback = f"your previous patch left {len(e2)} errors (was {len(e1)})" + (f" and introduced new error types {sorted(new_codes)}: {intro}" if new_codes else "")
            continue
        comp, vs, feedback, rejected_in_row = cand, vs2, None, 0
    if trace.get("stop_reason"):
        rt.log(f"  [R1] stopped: {trace['stop_reason']}")

    trace["regenerations"] = []
    for _ in range(int(lim.get("regenerate_on_stall", 0))):
        errs = rules.errors(vs)
        if frozen or not any(_in_reach(e, frozen) for e in errs):
            break
        try:
            obj2, meta2 = call(rt, pid, ctx, role, extra_user=_regenerate_note(errs))
        except Exception as e:  # noqa: BLE001
            trace["regenerations"].append({"accepted": False, "why": f"generator failed: {e}"[:200]})
            break
        cand = obj2.model_dump()
        vs2 = engine.check(apply(copy.deepcopy(rt.state), cand), stages)
        cand, vs2, fixes2 = engine.apply_fixers(rt.state, cand, apply, stages, vs2)
        ok = len(rules.errors(vs2)) < len(errs)
        trace["regenerations"].append({"accepted": ok, "errors_before": len(errs), "errors_after": len(rules.errors(vs2)),
                                       "error_codes_after": engine.error_codes(vs2), "fixes": fixes2, "endpoint": meta2["endpoint"]})
        rt.log(f"  [{pid} regenerate] errors {len(errs)} → {len(rules.errors(vs2))} {'ACCEPT' if ok else 'REJECT'}")
        if ok:
            comp, vs = cand, vs2
    trace["final_errors"] = len(rules.errors(vs))
    trace["final_warnings"] = len(vs) - trace["final_errors"]
    trace["final_error_codes"] = engine.error_codes(vs)
    trace["open"] = engine.open_items(vs)
    return comp, vs, trace


def dumps(x) -> str:
    return json.dumps(x, ensure_ascii=False, default=str)
