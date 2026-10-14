"""Evaluation tier 1: deterministic quality metrics of a finished design. NO LLM, no reference course needed.

Validation decides what must be fixed during generation; this module measures the finished design and reports the
numbers, not one opaque score:
    completeness   how many COs, LOs, topics, weeks, labs, assessments, resources
    alignment      % of COs with LOs, LOs taught, LOs assessed at their level, COs assessed, topic groups taught,
                   topics scheduled, labs practising an LO; programme-outcome coverage
    constraints    hard/soft constraints checked and satisfied, malformed, unenforced, conflicts
    regulation     weeks, credits, L-T-P against the regulation
    validation     open errors and warnings by family and code (recomputed from the design)
    text, bloom    statement lengths, vague degrees, banned verbs; Bloom distribution against the band and template
    workload       lecture hours vs budget, outside-lecture load, assessment events per week, proctored share
    resources      verified share and age
    gates          overrides and "would have blocked"
    summary        verdict PASS | REVIEW | FAIL: FAIL = open errors; REVIEW = something needs a human to confirm
                   (coverage below 100%, unenforced or malformed constraints, confirm-warnings); else PASS
"""
from __future__ import annotations

import datetime
import statistics
from collections import Counter

from profsagent.config import pedagogy
from profsagent.validate import constraints as K
from profsagent.validate import engine, regulation, rules

CONFIRM_CODES = {"VK", "VK-CONTENT", "VK-MALFORMED", "VK-UNENFORCED"}   # warnings that ask a human to confirm


def _pct(part: int, whole: int) -> float | None:
    return round(100 * part / whole, 1) if whole else None


def _words(items: list[dict]) -> dict:
    n = [len((x.get("statement") or "").split()) for x in items]
    return {"min": min(n), "median": statistics.median(n), "max": max(n)} if n else {}


def evaluate(state: dict) -> dict:
    cos, los = state.get("cos", []), state.get("los", [])
    topics = [t for m in state.get("modules", []) for t in m["topics"]]
    comps = (state.get("assessment") or {}).get("components", [])
    insts = [i for c in comps for i in c["instances"]]
    lt = state.get("labs_tutorials") or {}
    labs, tuts = lt.get("labs", []), lt.get("tutorials", [])
    sched = state.get("schedule") or {}
    res = state.get("resources", [])

    # ---- alignment
    lo_by_co = Counter(lo["parent_co"] for lo in los)
    served = {lo for t in topics for lo in t.get("serves_los", [])}
    lo_level = {lo["id"]: int(lo["bloom_level"]) for lo in los}
    assessed = {a["lo_id"] for i in insts for a in i["assesses"] if a["lo_id"] in lo_level and int(a["bloom_level"]) >= lo_level[a["lo_id"]]}
    co_of = {lo["id"]: lo["parent_co"] for lo in los}
    dropped = {x for p in state.get("topic_group_proposals", []) if p.get("action") in ("drop", "merge") for x in p.get("targets", [])}
    tgs = [g["id"] for g in state.get("topic_groups", []) if g["id"] not in dropped]
    taught_tgs = {tg for t in topics for tg in t.get("covers_topic_groups", [])}
    scheduled = set(sched.get("topic_weeks", {}))
    pos_by_prog = Counter(p.get("programme") for p in state.get("programme_pos", []))
    mapped = {m["po_uid"] for m in state.get("copo", [])}
    po_cov = {prog: _pct(sum(1 for p in state.get("programme_pos", []) if p.get("programme") == prog and p["uid"] in mapped), n)
              for prog, n in pos_by_prog.items()}
    alignment = {
        "cos_with_los_pct": _pct(sum(1 for c in cos if lo_by_co[c["id"]]), len(cos)),
        "los_taught_pct": _pct(sum(1 for lo in los if lo["id"] in served), len(los)),
        "los_assessed_at_level_pct": _pct(len(assessed), len(los)),
        "cos_assessed_pct": _pct(len({co_of[x] for x in assessed}), len(cos)),
        "topic_groups_taught_pct": _pct(sum(1 for g in tgs if g in taught_tgs), len(tgs)),
        "topics_scheduled_pct": _pct(sum(1 for t in topics if t["id"] in scheduled), len(topics)) if sched else None,
        "labs_practising_an_lo_pct": _pct(sum(1 for s in labs if s.get("practises_los")), len(labs)),
        "po_coverage_pct_by_programme": po_cov,
    }

    # ---- constraints
    preds = K.compile_all(state.get("constraints"))
    cov = K.coverage(state)
    failing = Counter()
    for st in ("intake", "cos", "structure", "schedule", "labs", "assessment", "resources"):
        for x in K.check_stage(state, st):
            if x["code"] in ("VK", "VK-CONTENT"):
                for n in x["nodes"]:
                    failing[(n, x["severity"])] += 1
    checked = [p for p in preds if p.kind in K.CHECKERS and not p.malformed]
    hard = [p for p in checked if p.hard]
    violated_hard = [p.id for p in hard if failing[(p.id, "error")]]
    to_confirm = sorted({n for (n, sev) in failing if sev == "warning"})
    constraint_metrics = {
        "total": cov["total"], "checked": cov["checked"], "hard_checked": len(hard),
        "hard_satisfied_pct": _pct(len(hard) - len(violated_hard), len(hard)), "hard_violated": violated_hard,
        "to_confirm": to_confirm, "malformed": cov["malformed"], "unenforced": cov["unenforced"],
        "conflicts": len(K.conflicts(state)) if state.get("constraints") is not None else 0,
    }

    # ---- regulation and validation
    reg = regulation.check_regulation(state)
    vs = engine.check(state)
    errs = rules.errors(vs)
    validation = {"errors": len(errs), "warnings": len(vs) - len(errs),
                  "errors_by_family": dict(Counter(x["family"] for x in errs)),
                  "errors_by_code": dict(Counter(x["code"] for x in errs).most_common()),
                  "warnings_by_code": dict(Counter(x["code"] for x in vs if x["severity"] != "error").most_common())}

    # ---- text and Bloom
    codes_by = Counter(x["code"] for x in vs)
    text = {"co_words": _words(cos), "lo_words": _words(los), "length_flags": codes_by["VT-LEN"],
            "vague_degrees": sum(1 for x in vs if x["code"] == "V11" and "vague" in x["message"]),
            "banned_verbs": codes_by["V12"]}
    band = state.get("bloom_band") or {}
    lv = [int(c["bloom_level"]) for c in cos]
    hb = pedagogy().get("co_high_bloom") or {}
    bloom = {"co_levels": dict(sorted(Counter(lv).items())), "band": [band.get("floor"), band.get("ceiling")],
             "outside_band": sum(1 for x in lv if band and not (band["floor"] <= x <= band["ceiling"])),
             "high_level_share_pct": _pct(sum(1 for x in lv if x >= hb.get("min_level", 4)), len(lv)),
             "high_level_required_pct": round(100 * hb["min_fraction"], 1) if hb else None}

    # ---- workload
    hbud = state.get("hours_budget") or {}
    lec = sum(float(t["est_hours"]) for t in topics)
    per_week = Counter(i["due_week"] for i in insts)
    pr = pedagogy().get("proctored") or {}
    proc = sum(float(c["weight_pct"]) for c in comps
               if (c.get("proctored") if c.get("proctored") is not None else str(c["type"]).lower() in pr.get("types", [])))
    known = [t for t in topics if t.get("outside_load_hours") is not None]
    hrs = sum(float(t["est_hours"]) for t in known)
    workload = {"lecture_hours_planned": lec, "lecture_hours_budget": hbud.get("lecture_hours_total"),
                "lecture_budget_used_pct": _pct(lec, hbud.get("lecture_hours_total") or 0),
                "outside_load_avg_h_per_week": round(sum(float(t["outside_load_hours"]) * float(t["est_hours"]) for t in known) / hrs, 1) if hrs else None,
                "outside_load_target": (state.get("template_rules") or {}).get("outside_load_hours_per_week"),
                "max_assessment_events_per_week": max(per_week.values(), default=0),
                "proctored_pct": round(proc, 1) if comps else None, "proctored_required_pct": pr.get("min_pct")}

    # ---- resources and gates
    years = [int(r["year"]) for r in res if str(r.get("year") or "").isdigit()]
    resources = {"count": len(res), "verified_pct": _pct(sum(1 for r in res if (r.get("verification") or {}).get("verified")), len(res)),
                 "median_age_years": datetime.date.today().year - int(statistics.median(years)) if years else None,
                 "rejected": len(state.get("resources_rejected") or [])}
    approvals = state.get("approvals", [])
    gates = {"approvals": len(approvals), "overrides": sum(1 for a in approvals if a.get("override")),
             "would_block": [w["gate"] for w in state.get("would_block", [])]}

    completeness = {"cos": len(cos), "los": len(los), "topics": len(topics), "modules": len(state.get("modules", [])),
                    "weeks_scheduled": len(sched.get("weeks", [])), "labs": len(labs), "tutorials": len(tuts),
                    "assessment_components": len(comps), "assessment_instances": len(insts), "resources": len(res)}

    # ---- verdict
    cov_values = [x for k, x in alignment.items() if k.endswith("_pct") and isinstance(x, (int, float))]
    review_reasons = []
    if cov_values and min(cov_values) < 100:
        review_reasons.append(f"alignment coverage below 100% ({min(cov_values)}%)")
    if constraint_metrics["unenforced"] or constraint_metrics["malformed"]:
        review_reasons.append(f"{len(constraint_metrics['unenforced']) + len(constraint_metrics['malformed'])} constraints nothing could check")
    confirm = [x for x in vs if x["severity"] != "error" and x["code"] in CONFIRM_CODES]
    if confirm:
        review_reasons.append(f"{len(confirm)} warnings ask for confirmation")
    verdict = "FAIL" if errs else ("REVIEW" if review_reasons else "PASS")
    summary = {"verdict": verdict, "errors": len(errs), "regulation_ok": not reg,
               "alignment_min_pct": min(cov_values) if cov_values else None,
               "hard_constraints_satisfied_pct": constraint_metrics["hard_satisfied_pct"], "review_reasons": review_reasons}
    return {"summary": summary, "completeness": completeness, "alignment": alignment, "constraints": constraint_metrics,
            "regulation": [{"code": x["code"], "message": x["message"]} for x in reg], "validation": validation,
            "text": text, "bloom": bloom, "workload": workload, "resources": resources, "gates": gates}
