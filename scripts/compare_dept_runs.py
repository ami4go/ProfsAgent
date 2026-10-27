"""Title-only vs full-form design runs for the department courses (eval/inputs/dept_courses). No LLM calls.

  python scripts/compare_dept_runs.py      # writes eval/dept_courses_comparison/README.md + metrics.json

For every finished run: verdict, errors, warnings, models used, size of the design, what the intake had to infer.
For every course with both runs: how close the two designs are (local all-MiniLM-L6-v2 embeddings: each CO / module of
one run matched to its most similar one in the other run).
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")

RUNS = ROOT / "runs"
OUT = ROOT / "eval" / "dept_courses_comparison"
COURSES = [("webdev", "Web Development for All", "CSE"), ("compopt", "Compiler Optimisation", "CSE"),
           ("quantfin", "Introduction to Quantitative Finance", "SSH"),
           ("transformers", "Introduction to Transformer Architecture", "CSE"),
           ("tda", "Topological Data Analysis", "Math"),
           ("convui", "Designing Conversational and Voice Interfaces", "HCD"),
           ("proteindl", "Deep Learning for Protein Structure and Design", "CB"),
           ("tinyml", "TinyML: Machine Learning on Microcontrollers", "ECE")]


def model(ep: str) -> str:
    return ep.split(":")[1] if ep.count(":") >= 2 else ep


def secs(t: str) -> int:
    h, m, s = map(int, t.split(":"))
    return h * 3600 + m * 60 + s


def facts(rid: str) -> dict | None:
    d = RUNS / rid
    if not (d / "evaluation_deterministic.json").exists():
        return None
    st = json.loads((d / "state.json").read_text(encoding="utf-8"))
    ev = json.loads((d / "evaluation_deterministic.json").read_text(encoding="utf-8"))
    calls = [json.loads(x) for x in open(d / "llm_calls.jsonl", encoding="utf-8") if x.strip()]
    ok = [c for c in calls if str(c.get("ok")) == "True"]
    log = (d / "run.log").read_text(encoding="utf-8", errors="replace").splitlines()
    ts = [secs(m.group(1)) for x in log if (m := re.match(r"(\d\d:\d\d:\d\d) ", x))]
    wall = sum((b - a) % 86400 for a, b in zip(ts, ts[1:]))
    fields = (st.get("cco") or {}).get("fields") or {}
    status = Counter(v.get("status", "?") for v in fields.values())
    comps = (st.get("assessment") or {}).get("components") or []
    overlap = ((st.get("kg_facts") or {}).get("catalogue_overlap") or [{}])[0]
    return {
        "run_id": rid, "verdict": ev["summary"]["verdict"], "errors": ev["summary"]["errors"],
        "warnings": ev["validation"]["warnings"], "warnings_by_code": ev["validation"]["warnings_by_code"],
        "calls": len(ok), "models": dict(Counter(model(c["endpoint"]) for c in ok)),
        "tokens": [sum(int(c.get("prompt_tokens") or 0) for c in ok), sum(int(c.get("output_tokens") or 0) for c in ok)],
        "wall_min": round(wall / 60), "repairs": sum(1 for x in log if "[R1 round" in x or "[fixer" in x),
        "fields": dict(status), "inferred": [k for k, v in fields.items() if v.get("status") != "given"],
        "level": st.get("level"), "ltp": st.get("ltp"), "weeks": st.get("weeks"),
        "topic_groups": len(st.get("topic_groups") or []),
        "cos": [{"id": c["id"], "bloom": c.get("bloom_level"), "statement": c["statement"]} for c in st["cos"]],
        "los": len(st["los"]), "modules": [m["title"] for m in st["modules"]],
        "topics": sum(len(m.get("topics") or []) for m in st["modules"]),
        "assessment": [(c["type"], c.get("weight_pct")) for c in comps],
        "proctored_pct": ev["workload"]["proctored_pct"], "hours": [ev["workload"]["lecture_hours_planned"], ev["workload"]["lecture_hours_budget"]],
        "outside_load": ev["workload"]["outside_load_avg_h_per_week"],
        "constraints": ev["constraints"]["total"], "hard_ok_pct": ev["constraints"]["hard_satisfied_pct"],
        "po_coverage": ev["alignment"]["po_coverage_pct_by_programme"],
        "resources": [r.get("title") for r in st.get("resources") or []],
        "closest_iiitd": f"{overlap.get('course_uid', '-')} {overlap.get('name', '')} ({overlap.get('weighted_jaccard', 0)})",
    }


def closeness(a: list[str], b: list[str], enc) -> float | None:
    if not a or not b or enc is None:
        return None
    import numpy as np
    ea, eb = enc.encode(a, normalize_embeddings=True), enc.encode(b, normalize_embeddings=True)
    sim = ea @ eb.T
    return round(float((sim.max(1).mean() + sim.max(0).mean()) / 2), 2)


def table(rows: list[list]) -> list[str]:
    out = ["| " + " | ".join(map(str, rows[0])) + " |", "|" + "---|" * len(rows[0])]
    return out + ["| " + " | ".join(map(str, r)) + " |" for r in rows[1:]]


def main() -> None:
    try:
        from sentence_transformers import SentenceTransformer
        enc = SentenceTransformer("all-MiniLM-L6-v2", local_files_only=True)
    except Exception:
        enc = None
    data, md = {}, []
    for slug, title, dept in COURSES:
        t, f = facts(f"dept-{slug}-title-01"), facts(f"dept-{slug}-full-01")
        pair = None
        if t and f:
            pair = {"co_closeness": closeness([c["statement"] for c in t["cos"]], [c["statement"] for c in f["cos"]], enc),
                    "module_closeness": closeness(t["modules"], f["modules"], enc)}
        data[slug] = {"title": title, "dept": dept, "title_only": t, "full": f, "pair": pair}
    done = sum(1 for v in data.values() for k in ("title_only", "full") if v[k])

    md += ["# Department courses: title only vs title + description + material", "",
           f"{done} of 16 runs finished (updated automatically after every run). Each course was designed twice with "
           "`scripts/run_design.py` (strong Gemini models only, Neo4j KG, no external research, gates auto-approved):",
           "", "- **title only**: just the course name; every other form field `[NOT SPECIFIED]`",
           "- **full**: the name, a description, a topic list and the material the professor has", "",
           "Inputs: `eval/inputs/dept_courses/`. Designs: `runs/dept-<course>-<title|full>-01/`. Numbers: `metrics.json`.",
           "Closeness: each CO (module) of one run matched to its most similar in the other, cosine of local "
           "all-MiniLM-L6-v2 embeddings averaged both ways (1.0 = same wording; ≈0.5 = related but different).", "",
           "## Summary", ""]
    rows = [["Course", "Dept", "Version", "Verdict", "Errors", "Warnings", "Repairs", "Calls (models)", "Time",
             "COs / LOs", "Modules / topics", "Level · L-T-P", "Fields inferred"]]
    for slug, v in data.items():
        for k, name in (("title_only", "title"), ("full", "full")):
            r = v[k]
            if not r:
                rows.append([v["title"], v["dept"], name, "not run yet", "", "", "", "", "", "", "", "", ""])
                continue
            ltp = r["ltp"] or {}
            rows.append([v["title"], v["dept"], name, r["verdict"], r["errors"], r["warnings"], r["repairs"],
                         f"{r['calls']} ({', '.join(f'{n}× {m}' for m, n in r['models'].items())})", f"{r['wall_min']} min",
                         f"{len(r['cos'])} / {r['los']}", f"{len(r['modules'])} / {r['topics']}",
                         f"{r['level']} · {ltp.get('L')}-{ltp.get('T')}-{ltp.get('P')}", f"{len(r['inferred'])} of {sum(r['fields'].values())}"])
    md += table(rows)
    pairs = [(v["title"], v["pair"]) for v in data.values() if v["pair"]]
    if pairs:
        md += ["", "## How close are the two versions of each course?", ""]
        md += table([["Course", "CO closeness", "Module closeness"]] + [[t, p["co_closeness"], p["module_closeness"]] for t, p in pairs])

    for slug, v in data.items():
        if not (v["title_only"] or v["full"]):
            continue
        md += ["", f"## {v['title']} ({v['dept']})", ""]
        rows = [["", "Title only", "Full"]]
        g = lambda k, fn=str: [fn(v[x][k]) if v[x] else "-" for x in ("title_only", "full")]
        rows += [["Verdict / errors / warnings"] + [f"{v[x]['verdict']} / {v[x]['errors']} / {v[x]['warnings']}" if v[x] else "-" for x in ("title_only", "full")],
                 ["Warnings by code"] + g("warnings_by_code", lambda d: ", ".join(f"{k} {n}" for k, n in d.items()) or "none"),
                 ["Fields the intake inferred"] + g("inferred", lambda l: ", ".join(l) or "none"),
                 ["Topic groups from intake"] + g("topic_groups"),
                 ["Lecture hours used"] + g("hours", lambda h: f"{h[0]} / {h[1]}"),
                 ["Assessment"] + g("assessment", lambda a: ", ".join(f"{t} {w:g}%" for t, w in a)),
                 ["Proctored share"] + g("proctored_pct", lambda p: f"{p}%"),
                 ["Outside-class load (h/week)"] + g("outside_load"),
                 ["Constraints (hard satisfied)"] + [f"{v[x]['constraints']} ({v[x]['hard_ok_pct']}%)" if v[x] else "-" for x in ("title_only", "full")],
                 ["PO coverage"] + g("po_coverage", lambda d: ", ".join(f"{k} {p}%" for k, p in d.items())),
                 ["Closest IIIT-D course (overlap)"] + g("closest_iiitd"),
                 ["Modules"] + g("modules", lambda l: "; ".join(l)),
                 ["Resources"] + g("resources", lambda l: "; ".join(map(str, l)))]
        md += table(rows)
        for x, name in (("title_only", "title only"), ("full", "full")):
            if v[x]:
                md += ["", f"**COs, {name}:**", ""] + [f"- {c['id']} (L{c['bloom']}): {c['statement']}" for c in v[x]["cos"]]
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "README.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    (OUT / "metrics.json").write_text(json.dumps(data, indent=1, ensure_ascii=False), encoding="utf-8")
    print(f"{done}/16 runs in eval/dept_courses_comparison/README.md")


if __name__ == "__main__":
    main()
