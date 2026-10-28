"""Evaluation tier 2: a generated course against the real course it re-creates, held out from the graph during the
run (run_cfg.exclude_courses), e.g. the cse201-dev runs against the real CSE201 sheet in data/enriched. No LLM and no
API calls: embeddings come from the local model (kg/neo4j_kg.LocalEmbedder) or an `embed` function passed in.

Metrics (reference = the real sheet, design = the generated course):
  topics       1-1 greedy matching at the topic-match threshold: precision, recall, F1 (one design topic can match one
               reference topic only); coverage recall (a reference topic is covered when a design topic, or one part of
               a compound title such as "I/O streams and object serialization", reaches the threshold); lexical recall
               (>= 60% of a reference topic's words appear in one design topic); BERTScore-style soft precision/recall/F1
               (mean best cosine similarity, no threshold); Kendall tau-b between the design week and the reference week
               of matched pairs.
               The real sheets list short phrases ("Interfaces"), designs compound titles, and short phrases embed far
               from longer ones: coverage still UNDER-counts (cse201-dev-05: 46% measured; on reading, most of the
               missed CSE201 topics are inside some design topic). Compare runs with it; do not read it as a grade.
  cos          soft precision/recall/F1 of CO statements; ROUGE-L F1 of each reference CO with its closest design CO
               (lexical); count; highest and mean Bloom level (lexicon for both)
  assessment   weight per component type: total variation distance (0 = same split, 1 = disjoint), type Jaccard
  structure    credits equal, CO / week / component count differences, mandatory prerequisites Jaccard
  resources    reference titles a design resource names (token coverage, as the constraint checks use)
Not a verdict: the real sheet is one good design, not the only one. Use it to compare runs and track changes.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

import numpy as np

from profsagent.kg.neo4j_kg import LOCAL_TOPIC_MATCH_SIM, NOT_A_TOPIC, LocalEmbedder
from profsagent.kg.quality import co_quality
from profsagent.kg.stub import assess_type
from profsagent.validate.text import covers

ROOT = Path(__file__).resolve().parents[3]
ENRICHED = ROOT / "data" / "enriched"


def reference_code(state: dict, enriched_dir: Path = ENRICHED) -> str | None:
    """The course to compare with: run.reference_course, else the first held-out course (run.exclude_courses) whose
    sheet is in data/enriched; None when there is none."""
    cfg = state.get("run_cfg") or {}
    named = [cfg["reference_course"]] if cfg.get("reference_course") else []
    return next((c.upper() for c in named + list(cfg.get("exclude_courses", [])) if (Path(enriched_dir) / f"{c.upper()}.json").exists()), None)


def load_reference(code: str, enriched_dir: Path = ENRICHED) -> dict:
    d = json.loads((Path(enriched_dir) / f"{code}.json").read_text(encoding="utf-8"))
    h = d["header"]
    return {"code": h["course_code"], "name": h.get("name"), "level": h.get("level"),
            "credits": (h.get("catalogue") or {}).get("credits") or h.get("credits"),
            "cos": [o["raw_text"] for o in d.get("outcomes", [])],
            "topics": [(str(t).strip(), i + 1) for i, w in enumerate(d.get("weekly_plan", []))
                       for t in w.get("lecture_topics", []) if str(t).strip() and not NOT_A_TOPIC.search(str(t))],
            "weeks": len(d.get("weekly_plan", [])),
            "assessment": [(assess_type(a.get("type") or a.get("type_label") or ""), a.get("weight_pct") or 0) for a in d.get("assessments", [])],
            "prereqs": sorted(x["code"] for x in h.get("prerequisite_links", []) if x.get("kind") == "mandatory"),
            "resources": [r["title"] for r in d.get("resources", []) if r.get("title")]}


def design_view(state: dict) -> dict:
    tw = (state.get("schedule") or {}).get("topic_weeks", {})
    topics = [(t["title"], min(tw[t["id"]]) if tw.get(t["id"]) else None) for m in state.get("modules", []) for t in m["topics"]]
    return {"credits": (state.get("defaults") or {}).get("credits"),
            "cos": [c["statement"] for c in state.get("cos", [])],
            "co_bloom": [int(c["bloom_level"]) for c in state.get("cos", []) if str(c.get("bloom_level", "")).isdigit()],
            "topics": topics, "weeks": state.get("weeks"),
            "assessment": [(assess_type(c["type"]), c.get("weight_pct") or 0) for c in (state.get("assessment") or {}).get("components", [])],
            "prereqs": sorted(p["course_uid"] for p in (state.get("positioning") or {}).get("prerequisites", []) if p.get("kind") == "mandatory"),
            "resources": [r.get("title") or "" for r in state.get("resources", [])]}


# ------------------------------------------------------------------ metrics
def _f1(p: float, r: float) -> float:
    return round(2 * p * r / (p + r), 3) if p + r else 0.0


def soft_prf(sims: np.ndarray) -> dict:
    """BERTScore-style greedy soft match over whole phrases: precision = mean over design items of the best similarity
    to any reference item, recall the other way round."""
    if sims.size == 0:
        return {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    p, r = float(sims.max(axis=1).mean()), float(sims.max(axis=0).mean())
    return {"precision": round(p, 3), "recall": round(r, 3), "f1": _f1(p, r)}


def title_parts(title: str) -> list[str]:
    """A compound topic title and its parts: "I/O streams and object serialization" -> itself, "I/O streams",
    "object serialization"."""
    parts = [p.strip() for p in re.split(r",|;|\band\b", title) if len(p.strip()) >= 3]
    return [title] + [p for p in parts if p != title]


def _coverage(design: list[str], reference: list[str], embed, th: float) -> float:
    if not design or not reference:
        return 0.0
    parts = list(dict.fromkeys(p for t in design for p in title_parts(t)))
    return round(float(((embed(reference) @ embed(parts).T).max(axis=1) >= th).mean()), 3)


def greedy_pairs(sims: np.ndarray, th: float) -> list[tuple[int, int, float]]:
    pairs, used_d, used_r = [], set(), set()
    for flat in np.argsort(-sims, axis=None, kind="stable"):
        i, j = divmod(int(flat), sims.shape[1])
        if sims[i, j] < th:
            break
        if i not in used_d and j not in used_r:
            used_d.add(i)
            used_r.add(j)
            pairs.append((i, j, float(sims[i, j])))
    return pairs


def kendall_tau_b(a: list[float], b: list[float]) -> float | None:
    if len(a) < 3:
        return None
    from scipy.stats import kendalltau
    t = kendalltau(a, b).statistic
    return None if t is None or np.isnan(t) else round(float(t), 3)


def _tokens(s: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", (s or "").lower())


def rouge_l(candidate: str, reference: str) -> float:
    """ROUGE-L F1 (longest common token subsequence)."""
    c, r = _tokens(candidate), _tokens(reference)
    if not c or not r:
        return 0.0
    prev = [0] * (len(r) + 1)
    for x in c:
        cur = [0]
        for j, y in enumerate(r, 1):
            cur.append(prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1]))
        prev = cur
    lcs = prev[-1]
    return _f1(lcs / len(c), lcs / len(r))


def _weights(rows: list[tuple[str, float]]) -> dict[str, float]:
    out = Counter()
    for t, w in rows:
        out[t] += w
    total = sum(out.values()) or 1
    return {t: w / total for t, w in out.items()}


def local_embed():
    e = LocalEmbedder()
    return lambda texts: e.embed(texts, "SEMANTIC_SIMILARITY")


def evaluate_reference(state: dict, ref: dict, embed=None, match_sim: float = LOCAL_TOPIC_MATCH_SIM) -> dict:
    """`embed(texts) -> unit vectors`, the local model by default; `match_sim` must suit the embedder."""
    embed = embed or local_embed()
    d = design_view(state)

    def sims(a: list[str], b: list[str]) -> np.ndarray:
        return embed(a) @ embed(b).T if a and b else np.zeros((len(a), len(b)))

    dt, rt = [t for t, _ in d["topics"]], [t for t, _ in ref["topics"]]
    ts = sims(dt, rt)
    pairs = greedy_pairs(ts, match_sim) if ts.size else []
    p = len(pairs) / len(dt) if dt else 0.0
    r = len(pairs) / len(rt) if rt else 0.0
    ordered = [(d["topics"][i][1], ref["topics"][j][1]) for i, j, _ in pairs if d["topics"][i][1] is not None]
    topics = {"design": len(dt), "reference": len(rt), "matched": len(pairs), "precision": round(p, 3), "recall": round(r, 3),
              "f1": _f1(p, r), "coverage_recall": _coverage(dt, rt, embed, match_sim),
              "lexical_recall": round(sum(covers(x, dt) for x in rt) / len(rt), 3) if rt else 0.0,
              "soft": soft_prf(ts), "order_kendall_tau_b": kendall_tau_b([a for a, _ in ordered], [b for _, b in ordered]),
              "match_sim": match_sim,
              "pairs": [{"design": dt[i], "design_week": d["topics"][i][1], "reference": rt[j], "reference_week": ref["topics"][j][1],
                         "sim": round(s, 3)} for i, j, s in pairs],
              "missed_reference": [rt[j] for j in range(len(rt)) if j not in {j for _, j, _ in pairs}]}

    cs = sims(d["cos"], ref["cos"])
    ref_bloom = [b for b in (co_quality(c)[3] for c in ref["cos"]) if b]
    best = cs.argmax(axis=0) if cs.size else []
    cos = {"design": len(d["cos"]), "reference": len(ref["cos"]), "soft": soft_prf(cs),
           "rouge_l_f1": round(float(np.mean([rouge_l(d["cos"][int(best[j])], ref["cos"][j]) for j in range(len(ref["cos"]))])), 3)
           if cs.size else 0.0,
           "bloom_max": {"design": max(d["co_bloom"], default=None), "reference": max(ref_bloom, default=None)},
           "bloom_mean": {"design": round(float(np.mean(d["co_bloom"])), 2) if d["co_bloom"] else None,
                          "reference": round(float(np.mean(ref_bloom)), 2) if ref_bloom else None}}

    dw, rw = _weights(d["assessment"]), _weights(ref["assessment"])
    types = set(dw) | set(rw)
    assessment = {"design": {t: round(100 * w, 1) for t, w in sorted(dw.items())},
                  "reference": {t: round(100 * w, 1) for t, w in sorted(rw.items())},
                  "total_variation": round(0.5 * sum(abs(dw.get(t, 0) - rw.get(t, 0)) for t in types), 3) if dw and rw else None,
                  "type_jaccard": round(len(set(dw) & set(rw)) / len(types), 3) if types else None}

    dp, rp = set(d["prereqs"]), set(ref["prereqs"])
    structure = {"credits_equal": str(d["credits"]) == str(ref["credits"]) if ref["credits"] is not None else None,
                 "co_count_diff": len(d["cos"]) - len(ref["cos"]), "weeks_diff": (d["weeks"] or 0) - ref["weeks"],
                 "component_count_diff": len(d["assessment"]) - len(ref["assessment"]),
                 "prereq": {"design": sorted(dp), "reference": sorted(rp),
                            "jaccard": round(len(dp & rp) / len(dp | rp), 3) if dp | rp else 1.0}}
    found = [t for t in ref["resources"] if any(covers(t, [x]) or covers(x, [t]) for x in d["resources"] if x)]
    resources = {"design": len(d["resources"]), "reference": len(ref["resources"]), "reference_named": found,
                 "recall": round(len(found) / len(ref["resources"]), 3) if ref["resources"] else None}

    summary = {"reference": ref["code"], "topic_f1": topics["f1"], "topic_soft_f1": topics["soft"]["f1"],
               "topic_coverage_recall": topics["coverage_recall"], "topic_lexical_recall": topics["lexical_recall"],
               "order_tau_b": topics["order_kendall_tau_b"],
               "co_soft_f1": cos["soft"]["f1"], "co_rouge_l": cos["rouge_l_f1"],
               "assessment_tv": assessment["total_variation"], "prereq_jaccard": structure["prereq"]["jaccard"],
               "resource_recall": resources["recall"]}
    return {"summary": summary, "topics": topics, "cos": cos, "assessment": assessment, "structure": structure,
            "resources": resources}
