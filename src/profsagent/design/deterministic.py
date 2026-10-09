"""Deterministic design steps — no LLM anywhere in this file.

- regulation defaults + assumption ledger (S1)
- hours budget + feasibility (S3)
- greedy topological scheduler with an infeasibility explanation (S6; CP-SAT replaces it later)
- computed CO–PO strengths from the assessment blueprint (S7, docs/01 §6.5)
"""
from __future__ import annotations

import heapq
import math
from collections import defaultdict

from profsagent.config import pedagogy, regulations


# ------------------------------------------------------------------ S1 defaults
def apply_defaults(cco: dict) -> dict:
    """Returns {ltp, weeks, credits, level, constraints:[K01..], assumptions:[ASM..], context_fields:{...}}.
    Values the professor gave are tagged USER; regulation-derived values DEFAULT; anything else is an Assumption."""
    regs = {f["id"]: f for f in regulations()["facts"]}
    f = cco["fields"]
    asm, cons = [], []

    def a(what, value, basis, confirm="course instructor / DOAA"):
        asm.append({"id": f"ASM{len(asm) + 1:02d}", "what": what, "value": value, "basis": basis, "confirm_with": confirm, "status": "open"})

    credits = f["credits"]["value"] if f["credits"]["status"] == "given" else None
    credits_src = "USER"
    if credits is None:
        credits, credits_src = 4, "DEFAULT"
        a("credits", 4, "UGREG-2025§4(2): courses are 4, 2 or 1 credit; 425 of 475 catalogue courses are 4-credit")
    try:
        credits = int(credits)
    except (TypeError, ValueError):
        credits, credits_src = 4, "DEFAULT"
    reg_ltp = regs["UGREG-2025§4(2)a"]["values"] if credits == 4 else regs["UGREG-2025§4(2)b"]["values"]

    ltp_f = f["ltp"]
    if ltp_f["status"] == "given" and ltp_f.get("L") is not None:
        L, T, P, ltp_src = ltp_f["L"], ltp_f.get("T") or 0, ltp_f.get("P") or 0, "USER"
    else:
        L, T = reg_ltp["lecture_h_per_week"], reg_ltp.get("tutorial_h_per_week", 0)
        lab_req = f["lab"].get("required")
        P = 2 if lab_req == "yes" else 0
        ltp_src = "DEFAULT"
        a("L-T-P", f"{L}-{T}-{P}", f"UGREG-2025§4(2): {credits}-credit = {L}h lecture + {T}h interaction/week; lab hours "
          + ("2h/week because the professor marked a lab as required (INFERRED amount)" if P else "0 because no lab was requested"))

    weeks = f["semester_weeks"]["value"] if f["semester_weeks"]["status"] == "given" else None
    weeks_src = "USER"
    if not weeks:
        weeks, weeks_src = regs["UGREG-2025§2"]["values"]["teaching_weeks"], "REGULATION"
    weeks = int(weeks)

    level = f["level_or_code"].get("level")
    if level is not None and int(level) >= 10:   # G1 sometimes writes the course number (400) instead of its level digit (4)
        level = int(str(int(level))[0])
    if level is None and f["level_or_code"].get("code"):
        digits = [c for c in f["level_or_code"]["code"] if c.isdigit()]
        level = int(digits[0]) if digits else None
    if level is not None and str(level) not in pedagogy()["bloom_bands"]:   # no Bloom band for it: fall back below
        level = None
    if level is None:
        yrs = f["target_students"].get("years") or []
        level = min(yrs) if yrs else 3
        a("course level", level, f"no code/level given; set to the lowest target year ({yrs or 'unspecified → 3'}) (INFERRED)")

    ms = regulations()["assumptions"]["midsem_after_week"]
    a("mid-semester exam timing", f"after teaching week {ms['value']}", ms["basis"], "academic calendar (DOAA)")
    if f["weekly_effort_hours"]["status"] != "given":
        a("weekly student effort", None, "not supplied; effort is reported (contact + take-home estimates), not constrained")

    cons += [
        {"id": "K01", "target": "schedule.weeks", "op": "==", "value": weeks, "hardness": "hard",
         "source": {"tag": weeks_src if weeks_src != "REGULATION" else "REGULATION", "ref": "UGREG-2025§2" if weeks_src == "REGULATION" else "CCO.semester_weeks"}},
        {"id": "K02", "target": "course.credits", "op": "==", "value": credits, "hardness": "hard",
         "source": {"tag": credits_src, "ref": "CCO.credits" if credits_src == "USER" else "ASM01"}},
        {"id": "K03", "target": "schedule.lecture_hours_per_week", "op": "==", "value": L, "hardness": "hard",
         "source": {"tag": ltp_src, "ref": "CCO.ltp" if ltp_src == "USER" else "UGREG-2025§4(2)a"}},
        {"id": "K04", "target": "schedule.tutorial_hours_per_week", "op": "==", "value": T, "hardness": "hard", "source": {"tag": ltp_src, "ref": "CCO.ltp"}},
        {"id": "K05", "target": "lab.hours_per_week", "op": "==", "value": P, "hardness": "hard", "source": {"tag": ltp_src, "ref": "CCO.ltp"}},
        {"id": "K06", "target": "assessment.component[midsem].present", "op": "present", "value": True, "hardness": "soft",
         "source": {"tag": "REGULATION", "ref": "UGREG-2025§6.2"}},
        {"id": "K07", "target": "assessment.component[endsem].present", "op": "present", "value": True, "hardness": "soft",
         "source": {"tag": "REGULATION", "ref": "UGREG-2025§6.2"}},
        {"id": "K08", "target": "schedule.midsem_after_week", "op": "==", "value": ms["value"], "hardness": "soft",
         "source": {"tag": "INFERRED", "ref": "ASM"}},
    ]
    if f["lab"].get("required") == "yes":
        cons.append({"id": "K09", "target": "lab.present", "op": "present", "value": True, "hardness": "hard", "source": {"tag": "USER", "ref": "CCO.lab"}})
    return {"ltp": {"L": L, "T": T, "P": P}, "weeks": weeks, "credits": credits, "level": level, "midsem_after_week": ms["value"],
            "constraints": cons, "assumptions": asm}


def hours_budget(ltp: dict, weeks: int) -> dict:
    return {"weeks": weeks, "lecture_hours_per_week": ltp["L"], "lecture_hours_total": ltp["L"] * weeks,
            "tutorial_hours_total": ltp["T"] * weeks, "lab_hours_total": ltp["P"] * weeks}


def bloom_band(level: int) -> dict:
    ped = pedagogy()
    lo, hi = ped["bloom_bands"][str(level)]
    return {"floor": lo, "ceiling": hi, "basis": f"level {level}xx band [{lo},{hi}] — {ped['bloom_band_basis']}", "source_tag": "INFERRED"}


# ------------------------------------------------------------------ S5/S6 topic DAG + scheduler
def find_cycle(nodes: list[str], edges: list[tuple[str, str]]) -> list[str] | None:
    adj = defaultdict(list)
    for a, b in edges:
        adj[a].append(b)
    color: dict[str, int] = {}
    stack: list[str] = []

    def dfs(u):
        color[u] = 1
        stack.append(u)
        for v in adj[u]:
            if color.get(v) == 1:
                return stack[stack.index(v):] + [v]
            if color.get(v, 0) == 0:
                c = dfs(v)
                if c:
                    return c
        stack.pop()
        color[u] = 2
        return None

    for n in nodes:
        if color.get(n, 0) == 0:
            c = dfs(n)
            if c:
                return c
    return None


def break_cycles(nodes: list[str], edges: list[tuple[str, str]], order_key: dict[str, tuple]) -> tuple[list[tuple[str, str]], list[tuple[str, str]]]:
    """Greedy feedback-arc removal. Edges are (prerequisite, dependent). In each cycle, drop the edge that most
    contradicts the suggested order (dependent suggested before its prerequisite); ties → the last edge."""
    edges = list(dict.fromkeys(edges))
    dropped = []
    while True:
        cyc = find_cycle(nodes, edges)
        if not cyc:
            return edges, dropped
        cyc_edges = list(zip(cyc, cyc[1:]))
        contradicting = [e for e in cyc_edges if order_key.get(e[1], ()) < order_key.get(e[0], ())]
        worst = contradicting[0] if contradicting else cyc_edges[-1]
        edges.remove(worst)
        dropped.append(worst)


def schedule(topics: list[dict], weeks: int, hours_per_week: float, midsem_after: int) -> dict:
    """topics: [{id, est_hours, requires:[ids], module_order, suggested_order}].
    Greedy list scheduling in topological order (priority = module order, suggested order), splitting topics across
    week boundaries. Returns {weeks:[{week, items:[{topic_id, hours}]}], topic_weeks:{id:[weeks]}, feasible, explanation}."""
    ids = [t["id"] for t in topics]
    by_id = {t["id"]: t for t in topics}
    key = {t["id"]: (t.get("module_order", 0), t.get("suggested_order", 0), t["id"]) for t in topics}
    edges = [(r, t["id"]) for t in topics for r in t.get("requires", []) if r in by_id]
    edges, dropped = break_cycles(ids, edges, key)
    indeg = {i: 0 for i in ids}
    succ = defaultdict(list)
    for a, b in edges:
        indeg[b] += 1
        succ[a].append(b)
    heap = [(key[i], i) for i in ids if indeg[i] == 0]
    heapq.heapify(heap)
    order = []
    while heap:
        _, u = heapq.heappop(heap)
        order.append(u)
        for v in succ[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                heapq.heappush(heap, (key[v], v))

    cap = weeks * hours_per_week
    need = sum(float(by_id[i]["est_hours"]) for i in order)
    wk, left = 1, hours_per_week
    plan = {w: [] for w in range(1, weeks + 1)}
    topic_weeks: dict[str, list[int]] = defaultdict(list)
    unscheduled = []
    for tid in order:
        h = float(by_id[tid]["est_hours"])
        while h > 1e-9:
            if wk > weeks:
                unscheduled.append({"topic_id": tid, "hours_left": round(h, 2)})
                break
            take = min(h, left)
            plan[wk].append({"topic_id": tid, "hours": round(take, 2)})
            topic_weeks[tid].append(wk)
            h -= take
            left -= take
            if left <= 1e-9:
                wk, left = wk + 1, hours_per_week
    feasible = not unscheduled
    expl = None
    if not feasible:
        expl = (f"{len(topics)} topics need {need:.1f} lecture hours but {weeks} weeks × {hours_per_week} h = {cap:.1f} h are "
                f"available ({need - cap:.1f} h over). Unscheduled: " + ", ".join(u["topic_id"] for u in unscheduled)
                + ". Drop or shorten topics (see G7 cut_candidates), or change L-T-P.")
    return {"weeks": [{"week": w, "items": plan[w], "is_midsem_boundary": w == midsem_after} for w in plan],
            "topic_weeks": dict(topic_weeks), "feasible": feasible, "explanation": expl, "hours_needed": round(need, 2),
            "hours_available": cap, "dropped_edges": dropped, "order": order}


# ------------------------------------------------------------------ S7 computed CO–PO strength
def copo_strengths(cos: list[str], lo_parent: dict[str, str], components: list[dict], activity_po_map: dict[str, list[str]],
                   mappings: list[dict], thresholds: dict) -> list[dict]:
    """marks(CO) from instances (component weight split evenly across instances, × marks_pct_of_instance);
    share(CO,PO) = marks from instances whose activity types map to PO / marks(CO)."""
    co_marks = defaultdict(float)
    co_po_marks = defaultdict(float)
    for comp in components:
        n = max(len(comp["instances"]), 1)
        eff = comp.get("best_k") or n
        per_inst = comp["weight_pct"] / (eff if comp.get("best_k") else n)
        pos = {po for act in comp.get("activity_types", []) for po in activity_po_map.get(act, [])}
        for inst in comp["instances"]:
            for a in inst["assesses"]:
                co = lo_parent.get(a["lo_id"])
                if not co:
                    continue
                m = per_inst * a["marks_pct_of_instance"] / 100
                co_marks[co] += m
                for po in pos:
                    co_po_marks[(co, po)] += m
    out = []
    claimed = {(m["co_id"], m["po_uid"]): m for m in mappings}
    keys = set(claimed) | {k for k in co_po_marks if k[0] in cos}
    for co, po in sorted(keys):
        share = co_po_marks.get((co, po), 0) / co_marks[co] if co_marks.get(co) else 0.0
        strength = 3 if share >= thresholds["three"] else 2 if share >= thresholds["two"] else 1 if share > 0 else 0
        out.append({"co_id": co, "po_uid": po, "share": round(share, 3), "strength_computed": strength,
                    "strength_provisional": claimed.get((co, po), {}).get("strength_provisional"), "claimed": (co, po) in claimed})
    return out


def co_marks_share(lo_parent: dict[str, str], components: list[dict]) -> dict[str, float]:
    share = defaultdict(float)
    for comp in components:
        n = max(len(comp["instances"]), 1)
        per = comp["weight_pct"] / (comp.get("best_k") or n)
        for inst in comp["instances"]:
            for a in inst["assesses"]:
                share[lo_parent.get(a["lo_id"], "?")] += per * a["marks_pct_of_instance"] / 100
    return {k: round(v, 2) for k, v in share.items()}


def ceil_div(a: float, b: float) -> int:
    return int(math.ceil(a / b))
