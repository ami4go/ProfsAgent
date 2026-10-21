"""Teaching hours and weekly student workload (runs/<id>/workload.md and workload.csv). Deterministic, no LLM.

Per teaching week: lecture hours (scheduled topics), tutorial and lab hours (L-T-P), outside-lecture work, and the
assessment tasks due. Outside-lecture work per week is the hours-weighted average of the "average load" (h/week) of the
topics taught that week (the template's 'Average load' column; the same figure the VT-LOAD check averages). The total
is compared with the IIIT-D template's recommendation for the course's credits.
"""
from __future__ import annotations

import csv
import io
from pathlib import Path


def weekly(state: dict) -> dict:
    ltp = state.get("ltp") or {}
    topics = {t["id"]: t for m in state.get("modules", []) for t in m["topics"]}
    labs = {x["week"] for x in (state.get("labs_tutorials") or {}).get("labs", [])}
    due: dict[int, list[str]] = {}
    for c in (state.get("assessment") or {}).get("components", []):
        for inst in c.get("instances", []):
            if inst.get("due_week"):
                due.setdefault(int(inst["due_week"]), []).append(inst["id"])
    rows = []
    for w in (state.get("schedule") or {}).get("weeks", []):
        items = w.get("items", [])
        lec = sum(float(i["hours"]) for i in items)
        known = [(float(i["hours"]), topics[i["topic_id"]].get("outside_load_hours")) for i in items
                 if i.get("topic_id") in topics and topics[i["topic_id"]].get("outside_load_hours") is not None]
        hrs = sum(h for h, _ in known)
        outside = round(sum(h * float(load) for h, load in known) / hrs, 1) if hrs else None
        rows.append({"week": w["week"], "lecture_h": round(lec, 1), "tutorial_h": float(ltp.get("T") or 0),
                     "lab_h": float(ltp.get("P") or 0) if (w["week"] in labs or not labs) else 0.0,
                     "outside_h": outside, "topics": [topics[i["topic_id"]]["title"] for i in items if i.get("topic_id") in topics],
                     "due": due.get(w["week"], []), "midsem_after": bool(w.get("is_midsem_boundary"))})
    total = {k: round(sum(r[k] or 0 for r in rows), 1) for k in ("lecture_h", "tutorial_h", "lab_h", "outside_h")}
    target = (state.get("template_rules") or {}).get("outside_load_hours_per_week")
    known_weeks = [r["outside_h"] for r in rows if r["outside_h"] is not None]
    avg = round(sum(known_weeks) / len(known_weeks), 1) if known_weeks else None
    return {"rows": rows, "total": total, "avg_outside_h": avg, "target_outside_h": target,
            "credits": (state.get("defaults") or {}).get("credits"), "ltp": ltp}


def markdown(state: dict) -> str:
    d = weekly(state)
    ltp = d["ltp"]
    name = (state.get("cco_compact") or {}).get("course_name") or (state.get("form") or {}).get("1. COURSE NAME") or "the course"
    t = d["total"]
    out = [f"# Teaching hours and weekly workload — {name}", "",
           f"Credits {d['credits']} · L-T-P {ltp.get('L')}-{ltp.get('T')}-{ltp.get('P')} · {len(d['rows'])} teaching weeks", "",
           "## Totals", "", "| | Hours |", "|---|---|",
           f"| Lectures | {t['lecture_h']:g} |", f"| Tutorials | {t['tutorial_h']:g} |", f"| Labs | {t['lab_h']:g} |",
           f"| Contact hours in total | {t['lecture_h'] + t['tutorial_h'] + t['lab_h']:g} |",
           f"| Outside-lecture work (sum of the weekly figures) | {t['outside_h']:g} |", ""]
    if d["avg_outside_h"] is not None:
        tgt = d["target_outside_h"]
        rng = f"{tgt['min']:g}–{tgt['max']:g} h/week" if tgt else "not set"
        out += [f"Average outside-lecture work: **{d['avg_outside_h']:g} h/week** (IIIT-D template recommendation: {rng}).", ""]
    out += ["## Week by week", "",
            "| Week | Lecture h | Tutorial h | Lab h | Outside-lecture work h | Topics | Assessment due |",
            "|---|---|---|---|---|---|---|"]
    for r in d["rows"]:
        out.append(f"| {r['week']}{' (mid-sem after)' if r['midsem_after'] else ''} | {r['lecture_h']:g} | {r['tutorial_h']:g} | "
                   f"{r['lab_h']:g} | {'' if r['outside_h'] is None else format(r['outside_h'], 'g')} | "
                   f"{'; '.join(r['topics'])} | {', '.join(r['due'])} |")
    return "\n".join(out) + "\n"


def write(state: dict, run_dir: Path) -> None:
    run_dir = Path(run_dir)
    (run_dir / "workload.md").write_text(markdown(state), encoding="utf-8")
    d = weekly(state)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["week", "lecture_h", "tutorial_h", "lab_h", "outside_lecture_work_h", "topics", "assessment_due"])
    for r in d["rows"]:
        w.writerow([r["week"], r["lecture_h"], r["tutorial_h"], r["lab_h"], r["outside_h"], "; ".join(r["topics"]), ", ".join(r["due"])])
    w.writerow(["total", d["total"]["lecture_h"], d["total"]["tutorial_h"], d["total"]["lab_h"], d["total"]["outside_h"], "", ""])
    (run_dir / "workload.csv").write_text(buf.getvalue(), encoding="utf-8", newline="")   # csv already ends lines with \r\n
