"""Deterministic rendering of the design state into the IIIT-D course proposal form (+ appendices).

No LLM here: the only prose is G11's narrative, which was generated from approved nodes. Outputs:
  runs/<id>/proposal.md   — human-readable proposal in the course-directory form + appendices
  runs/<id>/proposal.csv  — the same content in the course-directory sheet layout (diffable against real sheets)
"""
from __future__ import annotations

import csv
import io
from collections import defaultdict

from profsagent.validate import rules


def _tag(sources) -> str:
    tags = sorted({(s.get("tag") if isinstance(s, dict) else str(s)) for s in (sources or []) if s})
    return f" `[{', '.join(t for t in tags if t)}]`" if tags else ""


def _week_rows(st: dict) -> list[dict]:
    tmap = {t["id"]: t for m in st["modules"] for t in m["topics"]}
    lo_parent = {lo["id"]: lo["parent_co"] for lo in st["los"]}
    labs = defaultdict(list)
    for s in st.get("labs_tutorials", {}).get("labs", []):
        labs[s["week"]].append(s)
    tuts = defaultdict(list)
    for s in st.get("labs_tutorials", {}).get("tutorials", []):
        tuts[s["week"]].append(s)
    events = defaultdict(list)
    for c in st["assessment"]["components"]:
        for inst in c["instances"]:
            if inst["release_week"] == inst["due_week"]:
                events[inst["release_week"]].append(f"{inst['id']} ({c['type']})")
            else:
                events[inst["release_week"]].append(f"{inst['id']} released")
                events[inst["due_week"]].append(f"{inst['id']} due")
    rows = []
    for w in st["schedule"]["weeks"]:
        tids = list(dict.fromkeys(it["topic_id"] for it in w["items"]))
        los = sorted({lo for t in tids for lo in tmap.get(t, {}).get("serves_los", [])})
        rows.append({"week": w["week"], "topics": [f"{tmap[t]['title']} ({t})" for t in tids if t in tmap],
                     "los": los, "cos": sorted({lo_parent.get(lo, "?") for lo in los}),
                     "tutorial": "; ".join(s["activity"] for s in tuts[w["week"]]),
                     "lab": "; ".join(f"{s['title'] or s['exercise'][:60]}" for s in labs[w["week"]]),
                     "events": "; ".join(events[w["week"]]), "midsem_after": w["week"] == st["midsem_after_week"]})
    return rows


def render(rt) -> None:
    st = rt.state
    cc = st["cco_compact"]
    d = st["defaults"]
    pos = st["positioning"]
    vs = [x for v in st.get("violations", {}).values() for x in v]
    errs = rules.errors(vs)
    L = []
    w = L.append
    w(f"# {cc['course_name']} — Course Proposal (ProfsAgent draft)\n")
    w(f"> Run `{rt.run_id}` · generated deterministically from the design graph · validator status: **{len(errs)} errors, "
      f"{len(vs) - len(errs)} warnings** (see Appendix E). Approvals: " +
      ", ".join(f"{a['gate']}={a['decision']} ({a['by']})" for a in st.get("approvals", [])) + "\n")

    w("## 1. Assumption ledger (values not supplied by the professor)\n")
    w("| id | what | value | basis | confirm with |\n|---|---|---|---|---|")
    for a in d["assumptions"]:
        w(f"| {a['id']} | {a['what']} | {a['value']} | {a['basis']} | {a['confirm_with']} |")
    for amb in st["cco"].get("ambiguities", []):
        w(f"| — | ambiguous: {amb['field']} | — | {'; '.join(amb['interpretations'])} | professor |")
    for c in st["cco"].get("conflicts", []) + [{"fields": x["ids"], "detail": x["reason"]} for x in st.get("constraint_conflicts", [])]:
        w(f"| — | CONFLICT {c.get('fields')} | — | {c.get('detail')} | professor |")
    w("")

    w("## 2. Course header\n")
    w("| Field | Value |\n|---|---|")
    w(f"| Course Code | {st['cco']['fields']['level_or_code'].get('code') or 'to be assigned'} (level {st['level']}xx) |")
    w(f"| Course Name | {cc['course_name']} `[USER]` |")
    w(f"| Credits | {d['credits']} |")
    w(f"| L-T-P | {st['ltp']['L']}-{st['ltp']['T']}-{st['ltp']['P']} · {st['weeks']} teaching weeks `[UGREG-2025§2, §4]` |")
    w(f"| Offered to | {', '.join(st['programmes'])} · years {cc['target_students'].get('years')} |\n")

    w("## 3. Course description\n")
    w(st.get("narrative", {}).get("course_description", "_(narrative not generated)_") + "\n")

    w("## 4. Pre-requisites and anti-requisites\n")
    w("| Kind | Course | Relied-upon topics | Justification |\n|---|---|---|---|")
    for p in pos.get("prerequisites", []):
        alt = f" (or {', '.join(p['alternatives'])})" if p.get("alternatives") else ""
        w(f"| {p['kind']} | {p['course_uid']}{alt} `[CATALOGUE]` | {', '.join(p['relied_topics'])} | {p['justification']} |")
    anti = pos.get("anti_requisites", [])
    w("\n**Anti-requisites:** " + (", ".join(f"{a['course_uid']} ({a['reason']})" for a in anti) if anti else
                                   "none — every checked course is below the anti-requisite overlap threshold (Appendix D)."))
    w(f"\n**Existence check:** {pos['existence']['verdict']} — {pos['existence']['reason']}\n")

    w("## 5. Bloom band\n")
    b = st["bloom_band"]
    w(f"L{b['floor']}–L{b['ceiling']} · basis: {b['basis']}\n")

    w("## 6. Course Outcomes (Post Conditions) and Learning Outcomes\n")
    los_by = defaultdict(list)
    for lo in st["los"]:
        los_by[lo["parent_co"]].append(lo)
    share = st.get("co_marks_share", {})
    for c in st["cos"]:
        w(f"**{c['id']} (L{c['bloom_level']}, {c['knowledge_dimension']}) — {c['statement']}**{_tag(c.get('sources'))}  ")
        w(f"verb *{c['verb']}* · behaviour *{c['behaviour']}* · condition *{c['condition']}* · degree *{c['degree']}* · "
          f"evidence: {', '.join(c['evidence_types'])} · marks share (computed): {share.get(c['id'], 0)}%\n")
        for lo in los_by[c["id"]]:
            cap = " ★capstone" if lo.get("is_capstone") else ""
            w(f"- {lo['id']} (L{lo['bloom_level']}{cap}) {lo['statement']}")
        w("")

    w("## 7. Weekly lecture plan\n")
    w("| Week | Lecture topics | LOs met | COs met | Tutorial | Assessment events |\n|---|---|---|---|---|---|")
    rows = _week_rows(st)
    for r in rows:
        w(f"| {r['week']} | {'<br>'.join(r['topics'])} | {', '.join(r['los'])} | {', '.join(r['cos'])} | {r['tutorial']} | {r['events']} |")
        if r["midsem_after"]:
            w("| — | **Mid-semester recess + mid-sem exam** | | | | |")
    w("")

    w("## 8. Weekly lab plan\n")
    labs = st.get("labs_tutorials", {}).get("labs", [])
    if labs:
        w("| Week | Exercise | LOs practised | Tools |\n|---|---|---|---|")
        for s in labs:
            w(f"| {s['week']} | **{s['title']}** — {s['exercise']} | {', '.join(s['practises_los'])} | {', '.join(s['tools'])} |")
    else:
        w("No lab component (P = 0).")
    infra = st.get("labs_tutorials", {}).get("infra_requirements", [])
    if infra:
        w("\nInfrastructure: " + "; ".join(f"{i['item']} ({i['status']})" for i in infra))
    w("")

    w("## 9. Assessment plan\n")
    w("| Component | Weight % | Instances (release→due week) | best-k | Activities | Justification |\n|---|---|---|---|---|---|")
    for c in st["assessment"]["components"]:
        inst = ", ".join(f"{i['id']} (W{i['release_week']}→W{i['due_week']})" for i in c["instances"])
        bk = f"best {c['best_k']} of {c.get('n') or len(c['instances'])}" if c.get("best_k") else "—"
        w(f"| {c['type']} | {c['weight_pct']} | {inst} | {bk} | {', '.join(c['activity_types'])} | {c.get('weight_justification') or ''} |")
    w(f"| **Sum** | **{sum(c['weight_pct'] for c in st['assessment']['components'])}** | | | | |\n")
    w("Per-CO marks share (computed from LO-level blueprint): " + ", ".join(f"{k} {v}%" for k, v in sorted(share.items())) + "\n")

    w("## 10. Resource material\n")
    w(f"Policy: **{st.get('resource_policy', {}).get('textbook_policy')}** — {st.get('resource_policy', {}).get('reason')}\n")
    w("| Role | Reference | Identifier | Verified | Supports |\n|---|---|---|---|---|")
    for r in st.get("resources", []):
        ident = r["identifier"].get("isbn") or r["identifier"].get("doi") or r["identifier"].get("url") or r["candidate_id"]
        ok = "yes" if r["verification"]["verified"] else "NO: " + "; ".join(r["verification"]["problems"])
        w(f"| {r['role']} | {', '.join(r['authors'])} ({r.get('year')}). *{r['title']}*. | {ident} | {ok} | {', '.join(s['topic_id'] for s in r['supports_topics'])} |")
    w("")

    w("## Appendix A — CO–PO matrix (strength COMPUTED from assessment evidence; provisional in brackets)\n")
    pos_ids = [p["uid"] for p in st["programme_pos"]]
    used = sorted({r["po_uid"] for r in st.get("copo_computed", [])}, key=lambda x: pos_ids.index(x) if x in pos_ids else 99)
    w("| CO | " + " | ".join(u.split("/")[-1] for u in used) + " |\n|---|" + "---|" * len(used))
    cell = {(r["co_id"], r["po_uid"]): r for r in st.get("copo_computed", [])}
    for c in st["cos"]:
        vals = []
        for u in used:
            r = cell.get((c["id"], u))
            vals.append("" if not r else f"{r['strength_computed'] or '–'}" + (f" [{r['strength_provisional']}]" if r["claimed"] else " [unclaimed]"))
        w(f"| {c['id']} | " + " | ".join(vals) + " |")
    w("\nPO legend: " + "; ".join(f"{p['uid'].split('/')[-1]} = {p['short_label']}" for p in st["programme_pos"] if p["uid"] in used) + "\n")
    for m in st["copo"]:
        w(f"- {m['co_id']}→{m['po_uid'].split('/')[-1]}: {m['justification']} (activities: {', '.join(m['evidencing_activities'])})")
    w("")

    w("## Appendix B — Traceability matrix (LO → topics → weeks → assessments)\n")
    tw = st["schedule"]["topic_weeks"]
    by_lo_topics = defaultdict(list)
    for m in st["modules"]:
        for t in m["topics"]:
            for lo in t["serves_los"]:
                by_lo_topics[lo].append(t["id"])
    by_lo_assess = defaultdict(list)
    for c in st["assessment"]["components"]:
        for inst in c["instances"]:
            for a in inst["assesses"]:
                by_lo_assess[a["lo_id"]].append(f"{inst['id']}@L{a['bloom_level']}")
    w("| LO | Bloom | Topics | Weeks | Assessed by |\n|---|---|---|---|---|")
    for lo in st["los"]:
        ts = by_lo_topics.get(lo["id"], [])
        wks = sorted({x for t in ts for x in tw.get(t, [])})
        w(f"| {lo['id']} | L{lo['bloom_level']} | {', '.join(ts) or '**none**'} | {', '.join(map(str, wks))} | {', '.join(by_lo_assess.get(lo['id'], [])) or '**none**'} |")
    w("")

    w("## Appendix C — Modules and topics\n")
    for m in st["modules"]:
        w(f"**{m['id']} {m['title']}** (primary {', '.join(m['primary_cos'])})")
        for t in m["topics"]:
            req = f" · requires {', '.join(t['requires'])}" if t.get("requires") else ""
            w(f"- {t['id']} {t['title']} — {t['est_hours']} h · LOs {', '.join(t['serves_los'])}{req}")
    s = st["schedule"]
    w(f"\nSchedule: {'feasible' if s['feasible'] else 'INFEASIBLE — ' + (s['explanation'] or '')} · {s['hours_needed']} h needed / {s['hours_available']} h available\n")

    w("## Appendix D — Curriculum positioning\n")
    w("| Course | Computed overlap | Verdict | Differentiation |\n|---|---|---|---|")
    comp_ov = {o["course_uid"]: o for o in st.get("overlap_computed", [])}
    for o in pos.get("overlaps", []):
        w(f"| {o['course_uid']} | {comp_ov.get(o['course_uid'], {}).get('weighted_jaccard')} | {o['verdict']} | {o['differentiation']} |")
    w(f"\nOverlap method: {next(iter(comp_ov.values()), {}).get('method', 'n/a')}\n")
    w("**Comparable courses**\n")
    for c in pos.get("comparable", []):
        ext = next((e for e in st.get("external_courses", []) if e["id"] == c["ref"]), None)
        where = f" — {ext['institution']}, <{ext['url']}>" if ext else " — IIIT-D catalogue"
        w(f"- **{c['ref']}** {c['title']}{where}. Take: {c['take']} Avoid: {c['avoid']}")
    rej = (st.get("research") or {}).get("rejected") or []
    if rej:
        w(f"\nExternal pages examined and rejected: {len(rej)} (e.g. " + "; ".join(f"{r.get('url', '')[:60]} → {r.get('reason')}" for r in rej[:5]) + ")")
    w("")

    w("## Appendix E — Validation report (deterministic validators; not LLM self-assessment)\n")
    w("| Stage | Code | Severity | Nodes | Message |\n|---|---|---|---|---|")
    for x in sorted(vs, key=lambda x: (x["severity"] != "error", x["stage"], x["code"])):
        w(f"| {x['stage']} | {x['code']} | {x['severity']} | {', '.join(map(str, x['nodes']))[:60]} | {x['message'][:220]} |")
    w("\n**Repair history**\n")
    for stg, tr in st.get("traces", {}).items():
        if tr.get("repairs"):
            w(f"- {stg}: errors {tr.get('initial_errors')} → {tr.get('final_errors')} · " +
              "; ".join(f"round {r['round']} {'accepted' if r['accepted'] else 'rejected'} ({r.get('errors_before')}→{r.get('errors_after')})" for r in tr["repairs"]))
    w("\n**Model-reported concerns (not validated; for the professor's attention)**\n")
    for stg, cs in st.get("concerns", {}).items():
        for c in cs[:6]:
            w(f"- {stg}: {c.get('about')}: {c.get('detail')}")
    nar = st.get("narrative", {})
    if nar:
        w("\n## Appendix F — Rationales (G11)\n")
        for k in ("sequencing_rationale", "assessment_rationale", "positioning_rationale"):
            w(f"- **{k.replace('_', ' ')}:** {nar.get(k)}")
    (rt.run_dir / "proposal.md").write_text("\n".join(L), encoding="utf-8")

    # course-directory sheet layout
    buf = io.StringIO()
    cw = csv.writer(buf)
    cw.writerow(["Course Code", st["cco"]["fields"]["level_or_code"].get("code") or ""])
    cw.writerow(["Course Name", cc["course_name"]])
    cw.writerow(["Credits", d["credits"]])
    cw.writerow(["Course Offered to", "UG"])
    cw.writerow(["Course Description", nar.get("course_description", "")])
    cw.writerow(["Pre-requisites"])
    cw.writerow(["Pre-requisite (Mandatory)", "Pre-requisite (Desirable)", "Pre-requisite(other)"])
    cw.writerow([", ".join(p["course_uid"] for p in pos.get("prerequisites", []) if p["kind"] == "mandatory"),
                 ", ".join(p["course_uid"] for p in pos.get("prerequisites", []) if p["kind"] == "desirable"), ""])
    cw.writerow(["Post Conditions"])
    cw.writerow([c["id"] for c in st["cos"]])
    cw.writerow([c["statement"] for c in st["cos"]])
    cw.writerow(["Weekly Lecture Plan"])
    cw.writerow(["Week Number", "Lecture Topic", "COs Met", "Tutorial", "Assignments / Project"])
    for r in rows:
        cw.writerow([r["week"], "\n".join(r["topics"]), ", ".join(r["cos"]), r["tutorial"], r["events"]])
    cw.writerow(["Weekly Lab Plan"])
    cw.writerow(["Week Number", "Laboratory Exercise", "COs Met", "Platform"])
    lo_parent = {lo["id"]: lo["parent_co"] for lo in st["los"]}
    for s_ in labs:
        cw.writerow([s_["week"], s_["exercise"], ", ".join(sorted({lo_parent.get(x, '?') for x in s_["practises_los"]})), ", ".join(s_["tools"])])
    cw.writerow(["Assessment Plan"])
    cw.writerow(["Type of Evaluation", "% Contribution in Grade"])
    for c in st["assessment"]["components"]:
        cw.writerow([c["type"], c["weight_pct"]])
    cw.writerow(["Resource Material"])
    cw.writerow(["Type", "Title"])
    for r in st.get("resources", []):
        cw.writerow([r["role"], f"{', '.join(r['authors'])} ({r.get('year')}). {r['title']}"])
    (rt.run_dir / "proposal.csv").write_text(buf.getvalue(), encoding="utf-8")
    rt.log(f"rendered proposal.md + proposal.csv ({len(errs)} errors, {len(vs) - len(errs)} warnings)")
