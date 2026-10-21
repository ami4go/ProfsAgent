"""Compare the two validation schemes on the 23 injected defects (ground truth) and, optionally, on two design runs.

  rules   the current scheme: every rule in code (validate/rules.py). Free, instant.
  llm     the new scheme: the hard rules in code (config/llm_check.yaml) + an LLM check against the checklist.
          Reported three ways: LLM check alone ("one simple LLM check"), hard rules alone, and the two together.

  python scripts/compare_validation.py --scheme rules                 # no API calls
  python scripts/compare_validation.py --scheme llm --repeats 2       # 24 designs x 2 = 48 calls (cache off)
  python scripts/compare_validation.py --report [--runs RUN_RULES RUN_LLM]

Detection (same for every scheme): a defect is detected when the scheme reports an ERROR on the mutated design that it
does not report on the clean design. For the LLM check, the error must also concern the parts of the design the
defect changed (the nodes the defect's own rule points at), or, when those have no ids, the same stage; otherwise the
run-to-run variation of the LLM would count as detections. Results go to eval/compare_validation/.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(ROOT / "src"))

from profsagent.bench.defects import DEFECTS  # noqa: E402
from profsagent.config import RUNS  # noqa: E402
from profsagent.validate import llm_check, rules, semantic  # noqa: E402

OUT = ROOT / "eval" / "compare_validation"
FIXTURE = ROOT / "tests" / "fixtures" / "cs601_design_state.json"


def _key(x: dict) -> tuple:
    return x["code"], tuple(sorted(map(str, x.get("nodes", [])))), x.get("message", "")[:80]


def designs() -> list[tuple[str, dict, dict | None]]:
    """(name, state, defect) for the clean design and every injected defect."""
    base = json.loads(FIXTURE.read_text(encoding="utf-8"))
    return [("clean", base, None)] + [(d.name, d.apply(json.loads(json.dumps(base))), d) for d in DEFECTS]


def truth(mutated: dict, clean_errs: set, d) -> dict:
    """Where the defect is: the new errors of its own expected rules (all rules run, so this is the ground truth)."""
    new = [x for x in rules.errors(rules.run(mutated)) if x["code"] in d.expected and _key(x) not in clean_errs]
    return {"nodes": sorted({str(n) for x in new for n in x.get("nodes", [])}), "stages": sorted({x["stage"] for x in new})}


def run_rules() -> dict:
    semantic.configure(None)
    llm_check.configure(None)
    hard = llm_check.hard_rules()
    ds = designs()
    clean = {_key(x) for x in rules.errors(rules.run(ds[0][1]))}
    clean_hard = {k for k in clean if k[0] in hard}
    rows = []
    for name, st, d in ds[1:]:
        errs = rules.errors(rules.run(st))
        new = [x for x in errs if _key(x) not in clean]
        new_hard = [x for x in new if x["code"] in hard and _key(x) not in clean_hard]
        rows.append({"defect": name, "expected": list(d.expected), "truth": truth(st, clean, d),
                     "rules_all": bool({x["code"] for x in new} & set(d.expected)), "rules_all_any_new": bool(new),
                     "hard_only": bool(new_hard), "hard_codes": sorted({x["code"] for x in new_hard}),
                     "expected_is_hard": bool(set(d.expected) & hard)})
    out = {"scheme": "rules", "designs": len(ds), "clean_errors": len(clean), "rows": rows,
           "detected": {"rules_all": sum(r["rules_all"] for r in rows), "hard_only": sum(r["hard_only"] for r in rows)}}
    print(f"rules (all {len(rules_codes())} rule codes): {out['detected']['rules_all']}/{len(rows)} defects | "
          f"hard rules only ({len(hard)} codes): {out['detected']['hard_only']}/{len(rows)}")
    return out


def rules_codes() -> set[str]:
    from profsagent.validate.engine import FAMILY
    return {c for c in FAMILY if not c.startswith(("VS-", "VKG-"))}


def llm_detects(findings: list[dict], clean_items: set, t: dict) -> bool:
    for f in findings:
        if f["severity"] != "error" or f["code"] == "LLM:unavailable":
            continue
        if set(f.get("nodes", [])) & set(t["nodes"]):
            return True
        if (not t["nodes"] or not f.get("nodes")) and f["stage"] in {llm_check.STAGE_OF.get(s, s) for s in t["stages"]} \
                and f["code"] not in clean_items:
            return True
    return False


def run_llm(repeats: int, sleep_s: float) -> dict:
    from profsagent.llm.client import LLMClient
    semantic.configure(None)
    llm_check.configure(None)
    OUT.mkdir(parents=True, exist_ok=True)
    llm = LLMClient(OUT / "llm_calls.jsonl")
    llm.cache_enabled = False                       # every repeat is a fresh call
    ds = designs()
    clean_rules = {_key(x) for x in rules.errors(rules.run(ds[0][1]))}
    hard = llm_check.hard_rules()
    results = {name: [] for name, _, _ in ds}
    calls, t0 = 0, time.time()
    for rep in range(repeats):
        for name, st, _ in ds:
            try:
                f, info = llm_check.review_design(st, llm, run_id="compare-validation")
                calls += info.get("calls", 0)
                results[name].append({"findings": f, "endpoint": info.get("endpoint")})
            except Exception as e:  # noqa: BLE001
                results[name].append({"findings": [], "error": f"{type(e).__name__}: {str(e)[:160]}"})
            print(f"  repeat {rep + 1} {name:<36} {sum(x['severity'] == 'error' for x in results[name][-1]['findings'])} errors"
                  + (f"  ({results[name][-1].get('error')})" if results[name][-1].get("error") else ""), flush=True)
            time.sleep(sleep_s)
    rows = []
    for name, st, d in ds[1:]:
        t = truth(st, clean_rules, d)
        new_hard = [x for x in rules.errors(rules.run(st)) if x["code"] in hard and _key(x) not in clean_rules]
        per = []
        for r in range(repeats):
            clean_items = {f["code"] for f in results["clean"][r]["findings"] if f["severity"] == "error"}
            per.append(llm_detects(results[name][r]["findings"], clean_items, t))
        rows.append({"defect": name, "truth": t, "llm_only": per, "hard_only": bool(new_hard),
                     "hybrid": [p or bool(new_hard) for p in per],
                     "llm_errors": [sum(f["severity"] == "error" for f in results[name][r]["findings"]) for r in range(repeats)]})

    def items(name, r):
        return {(f["code"], tuple(sorted(f.get("nodes", [])))) for f in results[name][r]["findings"] if f["severity"] == "error"}
    consistency = None
    if repeats >= 2:
        js = []
        for name, _, _ in ds:
            a, b = items(name, 0), items(name, 1)
            js.append(len(a & b) / len(a | b) if a | b else 1.0)
        consistency = {"mean_jaccard_of_error_sets": round(sum(js) / len(js), 3),
                       "same_detection_both_repeats": sum(len(set(r["llm_only"])) == 1 for r in rows)}
    out = {"scheme": "llm", "repeats": repeats, "calls": calls, "seconds": round(time.time() - t0),
           "clean_llm_errors": [sum(f["severity"] == "error" for f in results["clean"][r]["findings"]) for r in range(repeats)],
           "rows": rows, "consistency": consistency, "raw": results,
           "detected": {"llm_only": [sum(r["llm_only"][k] for r in rows) for k in range(repeats)],
                        "hybrid": [sum(r["hybrid"][k] for r in rows) for k in range(repeats)],
                        "hard_only": sum(r["hard_only"] for r in rows)}}
    print(f"llm: LLM check alone {out['detected']['llm_only']} / {len(rows)} per repeat | hard rules + LLM "
          f"{out['detected']['hybrid']} | errors on the clean design {out['clean_llm_errors']} | consistency {consistency} | "
          f"{calls} calls, {out['seconds']} s")
    return out


def run_summary(run_id: str) -> dict | None:
    d = RUNS / run_id
    if not (d / "state.json").exists():
        return None
    st = json.loads((d / "state.json").read_text(encoding="utf-8"))
    vs = [x for v in (st.get("violations") or {}).values() for x in v]
    calls = [json.loads(line) for line in open(d / "llm_calls.jsonl", encoding="utf-8")] if (d / "llm_calls.jsonl").exists() else []
    ev = {}
    if (d / "evaluation_deterministic.json").exists():
        ev = json.loads((d / "evaluation_deterministic.json").read_text(encoding="utf-8")).get("summary", {})
    repairs = [r for tr in (st.get("traces") or {}).values() for r in (tr.get("repairs") or [])]
    from profsagent.agents.pipeline import is_book
    return {"run": run_id, "profile": st.get("run_cfg", {}).get("validation_profile"), "done": st.get("stages_done"),
            "errors_open": sum(x["severity"] == "error" for x in vs), "warnings": sum(x["severity"] == "warning" for x in vs),
            "llm_findings": sum(x["code"].startswith("LLM:") for x in vs),
            "llm_calls_total": len(calls), "check_calls": sum(c.get("prompt_id") == "C1" for c in calls),
            "repair_rounds": len(repairs), "repairs_accepted": sum(bool(r.get("accepted")) for r in repairs),
            "tier1": ev.get("verdict"), "lo_copies": sum(x["code"] == "VLO-COPY" for x in vs),
            "textbooks": sum(is_book(r) for r in st.get("resources", [])), "resources": len(st.get("resources", [])),
            "workload_file": (d / "workload.md").exists()}


def report(runs: list[str] | None) -> None:
    r = json.loads((OUT / "rules.json").read_text(encoding="utf-8")) if (OUT / "rules.json").exists() else None
    m = json.loads((OUT / "llm.json").read_text(encoding="utf-8")) if (OUT / "llm.json").exists() else None
    lines = ["# Validation schemes compared", ""]
    if r and m:
        n = len(r["rows"])
        lines += ["## Injected defects (ground truth: 23 known defects in one clean design)", "",
                  "| Scheme | Detected | Errors on the clean design | Run-to-run consistency | API calls |", "|---|---|---|---|---|",
                  f"| All rules in code (current) | {r['detected']['rules_all']}/{n} | {r['clean_errors']} | identical | 0 |",
                  f"| Hard rules only ({len(llm_check.hard_rules())} codes) | {r['detected']['hard_only']}/{n} | — | identical | 0 |",
                  f"| One LLM check alone | {' / '.join(str(x) for x in m['detected']['llm_only'])} of {n} per repeat | "
                  f"{' / '.join(map(str, m['clean_llm_errors']))} | {m['consistency']} | {m['calls']} |",
                  f"| Hard rules + LLM check (new scheme) | {' / '.join(str(x) for x in m['detected']['hybrid'])} of {n} | — | — | "
                  f"{m['calls']} |", "",
                  "| Defect | All rules | Hard rules | LLM alone (per repeat) | Hard + LLM |", "|---|---|---|---|---|"]
        mr = {x["defect"]: x for x in m["rows"]}
        for x in r["rows"]:
            y = mr.get(x["defect"], {})
            lines.append(f"| {x['defect']} | {'yes' if x['rules_all'] else 'no'} | {'yes' if x['hard_only'] else 'no'} | "
                         f"{' / '.join('yes' if v else 'no' for v in y.get('llm_only', []))} | "
                         f"{' / '.join('yes' if v else 'no' for v in y.get('hybrid', []))} |")
    if runs:
        rows = [run_summary(x) for x in runs]
        rows = [x for x in rows if x]
        if rows:
            keys = ["profile", "errors_open", "warnings", "llm_findings", "llm_calls_total", "check_calls", "repair_rounds",
                    "repairs_accepted", "tier1", "lo_copies", "textbooks", "resources", "workload_file"]
            lines += ["", "## Design runs (same CS-601 brief)", "", "| | " + " | ".join(x["run"] for x in rows) + " |",
                      "|---|" + "---|" * len(rows)]
            lines += [f"| {k} | " + " | ".join(str(x.get(k)) for x in rows) + " |" for k in keys]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {(OUT / 'report.md').relative_to(ROOT)}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scheme", choices=["rules", "llm"])
    ap.add_argument("--repeats", type=int, default=2)
    ap.add_argument("--sleep", type=float, default=2.0, help="seconds between LLM calls")
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--runs", nargs="*")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    if a.scheme == "rules":
        (OUT / "rules.json").write_text(json.dumps(run_rules(), indent=1, ensure_ascii=False), encoding="utf-8")
    elif a.scheme == "llm":
        (OUT / "llm.json").write_text(json.dumps(run_llm(a.repeats, a.sleep), indent=1, ensure_ascii=False, default=str),
                                      encoding="utf-8")
    if a.report:
        report(a.runs)
    if not (a.scheme or a.report):
        ap.error("give --scheme rules|llm and/or --report")


if __name__ == "__main__":
    main()
