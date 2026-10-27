"""Readable validation report (Phase 1): findings under plain headings, repeats of one check merged into one line.

What the professor reads at a gate and in the proposal's Appendix E. The individual findings are unchanged and still
kept in the run state (and written to runs/<id>/validation_report.json); this only decides how they are shown.

    CO1→MTECH-CSE/PO3 claimed but no assessed activity evidences it    \
    CO2→MTECH-CSE/PO3 claimed but no assessed activity evidences it     >  one line: "4×  CO1, CO2, CO3, CO4 …"
    ...                                                                 /
"""
from __future__ import annotations

from profsagent.validate.engine import FAMILY

GROUPS = [
    "University regulations and course template",
    "Your requirements",
    "IIIT-D catalogue",
    "Outcomes (COs and LOs)",
    "CO–PO mapping",
    "Topics, schedule and labs",
    "Assessment plan",
    "Resources",
    "Course frame",
]
BY_FAMILY = {"regulation": GROUPS[0], "constraint": GROUPS[1], "kg": GROUPS[2], "semantic": GROUPS[3], "resource": GROUPS[7],
             "fit": GROUPS[8]}
COPO_CODES = {"T4", "V23", "VCOPO-ACT"}
BY_STAGE = {"positioning": GROUPS[2], "cos": GROUPS[3], "los": GROUPS[3], "copo": GROUPS[4], "structure": GROUPS[5], "schedule": GROUPS[5],
            "labs": GROUPS[5], "assessment": GROUPS[6], "resources": GROUPS[7]}


def group_of(x: dict) -> str:
    fam = x.get("family") or FAMILY.get(x["code"], "rule")
    if fam in BY_FAMILY:
        return BY_FAMILY[fam]
    if x["code"] in COPO_CODES:
        return GROUPS[4]
    return BY_STAGE.get(x.get("stage"), GROUPS[8])


def grouped(vs: list[dict], max_nodes: int = 8) -> list[dict]:
    """One row per (group, severity, code): how many findings, which parts of the design, one example message.
    Errors before warnings; groups in GROUPS order."""
    rows: dict[tuple, dict] = {}
    for x in vs:
        key = (group_of(x), x["severity"], x["code"])
        r = rows.setdefault(key, {"group": key[0], "severity": key[1], "code": key[2], "count": 0, "nodes": [],
                                  "message": x["message"], "fix_hint": x.get("fix_hint")})
        r["count"] += 1
        for n in x.get("nodes", []):
            if n not in r["nodes"]:
                r["nodes"].append(n)
    out = sorted(rows.values(), key=lambda r: (r["severity"] != "error", GROUPS.index(r["group"]), -r["count"], r["code"]))
    for r in out:
        r["more_nodes"] = max(0, len(r["nodes"]) - max_nodes)
        r["nodes"] = r["nodes"][:max_nodes]
    return out


def summary(vs: list[dict]) -> dict:
    errs = [x for x in vs if x["severity"] == "error"]
    by_group = {}
    for x in vs:
        g = by_group.setdefault(group_of(x), {"errors": 0, "warnings": 0})
        g["errors" if x["severity"] == "error" else "warnings"] += 1
    return {"errors": len(errs), "warnings": len(vs) - len(errs),
            "by_group": {g: by_group[g] for g in GROUPS if g in by_group}}


def _parts(r: dict) -> str:
    return ", ".join(map(str, r["nodes"])) + (f" (+{r['more_nodes']} more)" if r["more_nodes"] else "")


def lines(vs: list[dict], errors_only: bool = False) -> list[str]:
    """Plain-text lines for the command line and gate payloads: errors one line per check; warnings likewise unless
    errors_only, in which case they become one count per group."""
    out, group = [], None
    rows = grouped(vs)
    for r in rows:
        if errors_only and r["severity"] != "error":
            continue
        if r["group"] != group:
            group = r["group"]
            out.append(f"{group}:")
        times = f"{r['count']}× " if r["count"] > 1 else ""
        more = " (and similar)" if r["count"] > 1 else ""
        out.append(f"  [{r['severity']}] {times}{r['message'][:160]}{more} — {_parts(r)}")
    if errors_only:
        warn = {g: c["warnings"] for g, c in summary(vs)["by_group"].items() if c["warnings"]}
        if warn:
            out.append("Warnings (not blocking): " + "; ".join(f"{g} {n}" for g, n in warn.items()))
    return out


def markdown(vs: list[dict]) -> str:
    """The proposal's Appendix E table."""
    s = summary(vs)
    md = [f"**{s['errors']} errors, {s['warnings']} warnings.** Repeats of the same check are merged into one row; "
          "the full list is in `validation_report.json`.\n",
          "| Area | Severity | Check | Count | Parts of the design | Example |", "|---|---|---|---|---|---|"]
    for r in grouped(vs):
        md.append(f"| {r['group']} | {r['severity']} | {r['code']} | {r['count']} | {_parts(r)} | {r['message'][:200]} |")
    return "\n".join(md)
