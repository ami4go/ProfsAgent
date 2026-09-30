"""Compare a design run with a reference course (e.g. the real CSE201 sheet, or later CS146S).

  python scripts/evaluate_run.py --run-id cse201-dev-01 --reference eval/reference/cse201_sheet.tsv

Metrics (all deterministic; embeddings only for topic matching at the calibrated threshold):
  topic recall / precision   generated topics vs reference weekly-plan topics (1-1 greedy matching)
  sequence agreement         Kendall tau between generated week and reference week of matched topic pairs
  CO count, Bloom spread     vs reference COs (reference Bloom from the lexicon)
  prerequisites              exact code match
  assessment                 component-type weights side by side
  validator summary          errors / warnings by code
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _s in (sys.stdout, sys.stderr):  # Windows consoles default to cp1252; logs contain arrows and ≈
    _s.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(ROOT / "src"))

import numpy as np  # noqa: E402

from profsagent.config import RUNS, pedagogy  # noqa: E402
from profsagent.kg.quality import co_quality  # noqa: E402
from profsagent.kg.stub import assess_type, split_topics  # noqa: E402
from profsagent.llm.client import LLMClient  # noqa: E402


def load_reference(p: Path) -> dict:
    ref = {"cos": [], "weeks": [], "assess": [], "prereq": [], "resources": []}
    for line in p.read_text(encoding="utf-8").splitlines():
        parts = line.split("\t")
        if parts[0].startswith("CO") and len(parts) > 1:
            ref["cos"].append(parts[1])
        elif parts[0] == "WEEK":
            ref["weeks"].append({"week": int(parts[1]), "topics": [t.strip() for t in parts[2].split(";") if t.strip()]})
        elif parts[0] == "ASSESS":
            ref["assess"].append({"type": assess_type(parts[1]), "weight": float(parts[2])})
        elif parts[0].startswith("Pre-requisite"):
            ref["prereq"] = [c.strip().replace(" ", "") for c in parts[1].split(",")]
        elif parts[0] == "RESOURCE":
            ref["resources"].append(parts[2])
    return ref


def kendall_tau(a: list[float], b: list[float]) -> float | None:
    n = len(a)
    if n < 3:
        return None
    c = d = 0
    for i in range(n):
        for j in range(i + 1, n):
            s = (a[i] - a[j]) * (b[i] - b[j])
            c += s > 0
            d += s < 0
    return round((c - d) / max(c + d, 1), 3)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--reference", required=True)
    a = ap.parse_args()
    st = json.loads((RUNS / a.run_id / "state.json").read_text(encoding="utf-8"))
    ref = load_reference(Path(a.reference))
    llm = LLMClient()
    th = pedagogy()["thresholds"]["topic_match_sim"]

    gen = []  # (title, week_first)
    tw = st["schedule"]["topic_weeks"]
    for m in st["modules"]:
        for t in m["topics"]:
            gen.append((t["title"], min(tw.get(t["id"], [99]))))
    reft = [(t, w["week"]) for w in ref["weeks"] for t in w["topics"] if not t.lower().startswith("end semester")]
    gv = llm.embed([g[0] for g in gen], "SEMANTIC_SIMILARITY")
    rv = llm.embed([r[0] for r in reft], "SEMANTIC_SIMILARITY")
    sims = gv @ rv.T
    pairs, used_g, used_r = [], set(), set()
    for flat in np.argsort(-sims, axis=None):
        i, j = divmod(int(flat), sims.shape[1])
        if sims[i, j] < th:
            break
        if i in used_g or j in used_r:
            continue
        used_g.add(i)
        used_r.add(j)
        pairs.append((i, j, float(sims[i, j])))
    recall = len(used_r) / len(reft)
    coverage_recall = float((sims.max(axis=0) >= th).mean()) if len(gen) else 0.0   # many-to-one: any generated topic covers it
    precision = len(used_g) / len(gen)
    tau = kendall_tau([gen[i][1] for i, _, _ in pairs], [reft[j][1] for _, j, _ in pairs])

    ref_bloom = [co_quality(c)[3] for c in ref["cos"]]
    gen_assess = Counter()
    for c in st["assessment"]["components"]:
        gen_assess[assess_type(c["type"])] += c["weight_pct"]
    ref_assess = Counter()
    for x in ref["assess"]:
        ref_assess[x["type"]] += x["weight"]
    vs = [x for v in st.get("violations", {}).values() for x in v]
    report = {
        "run_id": a.run_id,
        "topics": {"generated": len(gen), "reference": len(reft), "matched": len(pairs), "recall": round(recall, 3), "coverage_recall": round(coverage_recall, 3),
                   "precision": round(precision, 3), "sequence_kendall_tau": tau, "threshold": th,
                   "missed_reference_topics": [reft[j][0] for j in range(len(reft)) if j not in used_r],
                   "extra_generated_topics": [gen[i][0] for i in range(len(gen)) if i not in used_g],
                   "pairs": [{"generated": gen[i][0], "gen_week": gen[i][1], "reference": reft[j][0], "ref_week": reft[j][1], "sim": round(s, 3)} for i, j, s in pairs]},
        "cos": {"generated": len(st["cos"]), "reference": len(ref["cos"]), "generated_bloom": sorted(int(c["bloom_level"]) for c in st["cos"]),
                "reference_bloom_lexicon": ref_bloom},
        "prerequisites": {"generated": sorted(p["course_uid"] for p in st["positioning"]["prerequisites"] if p["kind"] == "mandatory"),
                          "reference": sorted(ref["prereq"])},
        "assessment_weights": {"generated": dict(gen_assess), "reference": dict(ref_assess)},
        "resources": {"generated": [r["title"] for r in st.get("resources", [])], "reference": ref["resources"],
                      "verified": sum(r["verification"]["verified"] for r in st.get("resources", []))},
        "validators": {"errors": Counter(x["code"] for x in vs if x["severity"] == "error"),
                       "warnings": Counter(x["code"] for x in vs if x["severity"] == "warning")},
        "external_courses": [f"{e['institution']}: {e.get('course_code')} {e.get('course_title')}" for e in st.get("external_courses", [])],
        "llm_calls": sum(1 for _ in open(RUNS / a.run_id / "llm_calls.jsonl", encoding="utf-8")) if (RUNS / a.run_id / "llm_calls.jsonl").exists() else None,
    }
    out = RUNS / a.run_id / "evaluation.json"
    out.write_text(json.dumps(report, indent=1, ensure_ascii=False, default=dict), encoding="utf-8")
    print(json.dumps({k: v for k, v in report.items() if k != "topics"} | {"topics": {k: v for k, v in report["topics"].items() if k != "pairs"}},
                     indent=1, ensure_ascii=False, default=dict))


if __name__ == "__main__":
    main()
