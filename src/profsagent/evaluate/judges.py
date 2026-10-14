"""Evaluation tier 3: an LLM judge panel scores a finished design against G-Eval rubrics (config/judging.yaml).

How the panel is kept honest:
- independent opinion: judges see the professor's brief and the design, never the validator findings or the
  design's own narrative about itself (prompt J1);
- evidence before score: each dimension lists node ids or quotes, then reasoning, then an anchored 1-5 score;
- a panel, not one judge (PoLL): up to `panel.size` judges, aggregated by the median, with the spread reported and a
  dimension flagged when judges are `disagreement_spread` points apart; agreement as Krippendorff's alpha and
  quadratic-weighted kappa (evaluate/agreement.py);
- self-preference: a judge whose model generated at least `self_preference_share` of the design is skipped;
- position bias (pairwise, prompt J2): every comparison runs in both orders and counts only when both agree;
- verbosity: the rubric says length is not quality, every design is shown in the same compact form, and
  agreement.length_bias checks across runs whether scores follow design length;
- cost (cascade): a design Tier 1 fails is not judged (fix the errors first); the first judge alone decides when it is
  clearly good or clearly weak; the rest of the panel runs only for the uncertain middle.
plan() reports the panel and the number of calls without making any.
"""
from __future__ import annotations

import statistics
from collections import Counter
from typing import Literal

from pydantic import BaseModel, Field

from profsagent.config import load_yaml, models_cfg
from profsagent.evaluate.agreement import panel_agreement
from profsagent.llm.prompts import load_prompt

CONTENT_STAGES = ("positioning", "cos", "copo", "los", "structure", "labs", "assessment")


class DimensionScore(BaseModel):
    dimension: str
    evidence: list[str] = Field(default_factory=list)
    reasoning: str = ""
    score: int = Field(ge=1, le=5)


class JudgeScores(BaseModel):
    dimensions: list[DimensionScore]
    overall_comment: str = ""


class PairDecision(BaseModel):
    dimension: str
    evidence: list[str] = Field(default_factory=list)
    better: Literal["1", "2", "tie"]


class PairwiseVerdicts(BaseModel):
    dimensions: list[PairDecision]


def cfg() -> dict:
    return load_yaml("config/judging.yaml")


# ------------------------------------------------------------------ what judges see
def brief_excerpt(state: dict, max_chars: int = 1500) -> dict:
    return {k: (str(v)[:max_chars] if v is not None else None) for k, v in (state.get("form") or {}).items()}


def design_excerpt(state: dict) -> dict:
    """The design in one compact form for every run: outcomes, structure, schedule, labs, assessment. No validator
    findings, narrative or graph facts."""
    tw = (state.get("schedule") or {}).get("topic_weeks", {})
    lt = state.get("labs_tutorials") or {}
    return {
        "level": state.get("level"), "credits": (state.get("defaults") or {}).get("credits"), "ltp": state.get("ltp"),
        "weeks": state.get("weeks"), "midsem_after_week": state.get("midsem_after_week"),
        "cos": [{"id": c["id"], "statement": c["statement"], "bloom_level": c.get("bloom_level")} for c in state.get("cos", [])],
        "los": [{"id": lo["id"], "parent_co": lo.get("parent_co"), "statement": lo["statement"], "bloom_level": lo.get("bloom_level")}
                for lo in state.get("los", [])],
        "modules": [{"id": m["id"], "title": m["title"],
                     "topics": [{"id": t["id"], "title": t["title"], "serves_los": t.get("serves_los", []), "weeks": tw.get(t["id"], [])}
                                for t in m["topics"]]} for m in state.get("modules", [])],
        "labs": [{"week": x.get("week"), "title": x.get("title"), "practises_los": x.get("practises_los", [])} for x in lt.get("labs", [])],
        "assessment": [{"type": c["type"], "weight_pct": c.get("weight_pct"),
                        "instances": [{"id": i["id"], "format": i.get("format"), "release_week": i.get("release_week"),
                                       "due_week": i.get("due_week"), "assesses": [a.get("lo_id") for a in i.get("assesses", [])]}
                                      for i in c.get("instances", [])]}
                       for c in (state.get("assessment") or {}).get("components", [])],
        "prerequisites": [p["course_uid"] for p in (state.get("positioning") or {}).get("prerequisites", [])],
        "resources": [r.get("title") for r in state.get("resources", [])],
    }


def rubrics() -> dict:
    return cfg()["rubrics"]


# ------------------------------------------------------------------ panel selection
def _model(endpoint: str) -> str:
    e = endpoint[len("cache("):-1] if endpoint.startswith("cache(") else endpoint
    parts = e.split(":")
    return ":".join(parts[:2])


def generator_models(state: dict) -> Counter:
    """provider:model -> number of design stages it generated (from the run's traces)."""
    out = Counter()
    for stage in CONTENT_STAGES:
        ep = ((state.get("traces") or {}).get(stage) or {}).get("generator", {}).get("endpoint")
        if ep:
            out[_model(ep)] += 1
    return out


def judge_model(role: str) -> str:
    ep = models_cfg()["roles"][role][0]
    return f"{ep['provider']}:{ep['model']}"


def select_panel(state: dict, llm) -> tuple[list[str], list[dict]]:
    c = cfg()["panel"]
    gen = generator_models(state)
    total = sum(gen.values()) or 1
    keys = {"gemini": getattr(llm, "gemini_keys", []), "groq": getattr(llm, "groq_keys", []), "ollama": ["local"]}
    panel, skipped = [], []
    for role in c["candidates"]:
        model = judge_model(role)
        share = gen.get(model, 0) / total
        if not keys.get(model.split(":")[0]):
            skipped.append({"judge": role, "model": model, "why": "no API key for this provider"})
        elif share >= c["self_preference_share"]:
            skipped.append({"judge": role, "model": model, "why": f"generated {share:.0%} of the design (self-preference)"})
        elif len(panel) < c["size"]:
            panel.append(role)
    return panel, skipped


# ------------------------------------------------------------------ judging
def judge(llm, role: str, brief: dict, design: dict, rubric: dict, run_id: str | None = None) -> dict:
    p = load_prompt("J1")
    system, user = p.render(brief=brief, design=design, rubrics=rubric)
    obj, rec = llm.structured(system=system, user=user, model_cls=JudgeScores, role=role, temperature=cfg()["panel"]["temperature"],
                              prompt_id="J1", prompt_version=p.version, run_id=run_id)
    scores, evidence = {d: None for d in rubric}, {}
    for d in obj.dimensions:
        if d.dimension in scores and scores[d.dimension] is None:      # first answer per known dimension
            scores[d.dimension] = d.score
            evidence[d.dimension] = {"evidence": d.evidence[:6], "reasoning": d.reasoning}
    return {"model": judge_model(role), "endpoint": getattr(rec, "endpoint", None), "scores": scores, "evidence": evidence,
            "comment": obj.overall_comment}


def _mean_min(scores: dict) -> tuple[float | None, int | None]:
    v = [x for x in scores.values() if x is not None]
    return (round(statistics.mean(v), 2), min(v)) if v else (None, None)


def _meets(scores: dict, rule: dict) -> bool:
    mean, low = _mean_min(scores)
    if mean is None:
        return False
    return (mean >= rule.get("mean_at_least", -1) and low >= rule.get("min_at_least", -1)
            and mean <= rule.get("mean_at_most", 99))


def band(medians: dict) -> str:
    v = cfg()["verdict"]
    return "good" if _meets(medians, v["good"]) else "acceptable" if _meets(medians, v["acceptable"]) else "weak"


def plan(state: dict, llm, tier1_verdict: str | None = None, force: bool = False, cascade: bool = True) -> dict:
    """What evaluate_judges would do, without calling anything."""
    c = cfg()
    panel, skipped = select_panel(state, llm)
    p = load_prompt("J1")
    system, user = p.render(brief=brief_excerpt(state), design=design_excerpt(state), rubrics=rubrics())
    skip = cascade and not force and tier1_verdict in c["cascade"]["skip_if_tier1"]
    return {"tier1": tier1_verdict, "judged": not skip and bool(panel), "panel": [{"judge": r, "model": judge_model(r)} for r in panel],
            "skipped_judges": skipped, "calls_min": 0 if skip or not panel else 1,
            "calls_max": 0 if skip else len(panel), "prompt_chars": len(system) + len(user),
            "prompt_tokens_est": round((len(system) + len(user)) / 3.2)}


def evaluate_judges(state: dict, llm, *, tier1_verdict: str | None = None, force: bool = False, cascade: bool = True,
                    run_id: str | None = None) -> dict:
    c = cfg()
    if cascade and not force and tier1_verdict in c["cascade"]["skip_if_tier1"]:
        return {"skipped": f"Tier 1 verdict {tier1_verdict}: fix the open errors first (or judge anyway with force)", "calls": 0}
    panel, skipped = select_panel(state, llm)
    out = {"panel": [{"judge": r, "model": judge_model(r)} for r in panel], "skipped_judges": skipped, "judges": {}, "calls": 0}
    if not panel:
        return {**out, "skipped": "no judge available"}
    brief, design, rubric = brief_excerpt(state), design_excerpt(state), rubrics()
    stop = c["cascade"]["stop_after_first_if"]
    for i, role in enumerate(panel):
        out["calls"] += 1
        try:
            out["judges"][role] = judge(llm, role, brief, design, rubric, run_id)
        except Exception as e:  # noqa: BLE001 — a missing judge is reported, the others still count
            out["judges"][role] = {"model": judge_model(role), "error": f"{type(e).__name__}: {e}"[:300]}
            continue
        first = out["judges"][role]["scores"]
        if cascade and i == 0 and (_meets(first, stop["good"]) or _meets(first, stop["weak"])):
            out["cascade_stop"] = f"first judge decisive ({'clearly good' if _meets(first, stop['good']) else 'clearly weak'})"
            break
    ok = {r: j for r, j in out["judges"].items() if "scores" in j}
    if not ok:
        return {**out, "skipped": "every judge failed"}
    spread_flag = c["verdict"]["disagreement_spread"]
    dims = {}
    for d in rubric:
        vals = [j["scores"][d] for j in ok.values() if j["scores"].get(d) is not None]
        dims[d] = {"name": rubric[d]["name"], "scores": {r: j["scores"].get(d) for r, j in ok.items()},
                   "median": statistics.median(vals) if vals else None, "mean": round(statistics.mean(vals), 2) if vals else None,
                   "spread": (max(vals) - min(vals)) if vals else None, "n": len(vals)}
        dims[d]["disagreement"] = bool(vals) and dims[d]["spread"] >= spread_flag
    medians = {d: x["median"] for d, x in dims.items()}
    mean, low = _mean_min(medians)
    out["dimensions"] = dims
    out["agreement"] = panel_agreement({r: j["scores"] for r, j in ok.items()}) if len(ok) >= 2 else None
    out["summary"] = {"band": band(medians), "mean": mean, "min": low, "judges_used": len(ok),
                      "disagreements": [d for d, x in dims.items() if x["disagreement"]],
                      "missing_judges": [r for r, j in out["judges"].items() if "error" in j],
                      "design_chars": len(str(design))}
    return out


def combined_verdict(tier1_verdict: str | None, judged: dict) -> dict:
    """Deterministic tiers decide FAIL; the judges can only send a design to the professor (REVIEW), never fail it."""
    reasons = []
    if tier1_verdict == "FAIL":
        return {"verdict": "FAIL", "reasons": ["Tier 1: open errors"]}
    if tier1_verdict == "REVIEW":
        reasons.append("Tier 1: items to confirm")
    s = judged.get("summary")
    if not s:
        reasons.append(f"not judged: {judged.get('skipped', 'no summary')}")
    else:
        if s["band"] != "good":
            reasons.append(f"judges rate it {s['band']} (mean {s['mean']}, lowest {s['min']})")
        if s["disagreements"]:
            reasons.append(f"judges disagree on {s['disagreements']}")
        if s["missing_judges"]:
            reasons.append(f"judges missing: {s['missing_judges']}")
    return {"verdict": "REVIEW" if reasons else "PASS", "reasons": reasons}


# ------------------------------------------------------------------ pairwise, both orders
def compare(state_a: dict, state_b: dict, llm, role: str, run_id: str | None = None) -> dict:
    """Which design is better per dimension. Each order is asked once; a dimension counts only when both orders pick
    the same design, otherwise it is a tie (position bias)."""
    p = load_prompt("J2")
    rubric = rubrics()
    brief, a, b = brief_excerpt(state_a), design_excerpt(state_a), design_excerpt(state_b)
    picks = []
    for first, second, names in ((a, b, {"1": "A", "2": "B"}), (b, a, {"1": "B", "2": "A"})):
        system, user = p.render(brief=brief, design_1=first, design_2=second, rubrics=rubric)
        obj, _ = llm.structured(system=system, user=user, model_cls=PairwiseVerdicts, role=role,
                                temperature=cfg()["panel"]["temperature"], prompt_id="J2", prompt_version=p.version, run_id=run_id)
        got = {}
        for d in obj.dimensions:
            if d.dimension in rubric and d.dimension not in got:
                got[d.dimension] = names.get(d.better, "tie")
        picks.append(got)
    dims, consistent = {}, 0
    for d in rubric:
        ab, ba = picks[0].get(d), picks[1].get(d)
        same = ab is not None and ab == ba
        consistent += same
        dims[d] = {"order_ab": ab, "order_ba": ba, "winner": ab if same else "tie"}
    wins = Counter(x["winner"] for x in dims.values())
    return {"judge": role, "model": judge_model(role), "dimensions": dims, "calls": 2,
            "position_consistency": round(consistent / len(rubric), 3),
            "wins": {"A": wins.get("A", 0), "B": wins.get("B", 0), "tie": wins.get("tie", 0)},
            "same_brief": state_a.get("form") == state_b.get("form")}
