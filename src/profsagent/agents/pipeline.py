"""Stage implementations S1–S9 (docs/01 §7). Each stage: build the prompt context (KG + RAG + research +
upstream approved state), run the agent loop, write Layer B nodes with provenance, record violations.

The mutable run state (`rt.state`) is plain JSON, so LangGraph can checkpoint it; the DesignGraph is written
through at the end of every stage for traceability.
"""
from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from profsagent.agents.loop import call, generate
from profsagent.config import RUNS, bloom_lexicon, degree_bank, pedagogy, regulations
from profsagent.design import deterministic as det
from profsagent.design.store import DesignGraph
from profsagent.kg.stub import StubKG
from profsagent.llm.client import LLMClient
from profsagent.research.external import Blocklist, ExternalResearch
from profsagent.research.resources import crossref, openlibrary, verify_pick
from profsagent.validate import rules


@dataclass
class Runtime:
    run_id: str
    run_dir: Path
    state: dict
    exclude: set[str] = field(default_factory=set)
    blocklist: Blocklist = field(default_factory=Blocklist)
    llm: LLMClient | None = None
    kg: StubKG | None = None
    graph: DesignGraph | None = None
    research_enabled: bool = True

    def log(self, msg: str) -> None:
        line = f"{time.strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with (self.run_dir / "run.log").open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    def save(self) -> None:
        (self.run_dir / "state.json").write_text(json.dumps(self.state, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
        if self.graph:
            self.graph.save()


def make_runtime(run_id: str, form: dict, run_cfg: dict) -> Runtime:
    run_dir = RUNS / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    llm = LLMClient(run_dir / "llm_calls.jsonl")
    rt = Runtime(run_id=run_id, run_dir=run_dir, state={"form": form, "run_cfg": run_cfg, "traces": {}, "violations": {}, "concerns": {},
                                                        "approvals": []},
                 exclude={c.upper() for c in run_cfg.get("exclude_courses", [])},
                 blocklist=Blocklist(**run_cfg.get("blocklist", {})), llm=llm, kg=StubKG(llm),
                 graph=DesignGraph(run_cfg.get("project_id", "P0001"), run_dir / "design_graph.json"),
                 research_enabled=run_cfg.get("external_research", True))
    return rt


def attach_runtime(run_id: str) -> Runtime:
    run_dir = RUNS / run_id
    st = json.loads((run_dir / "state.json").read_text(encoding="utf-8"))
    llm = LLMClient(run_dir / "llm_calls.jsonl")
    cfg = st["run_cfg"]
    g = DesignGraph.load(run_dir / "design_graph.json") if (run_dir / "design_graph.json").exists() else DesignGraph(cfg.get("project_id", "P0001"), run_dir / "design_graph.json")
    return Runtime(run_id=run_id, run_dir=run_dir, state=st, exclude={c.upper() for c in cfg.get("exclude_courses", [])},
                   blocklist=Blocklist(**cfg.get("blocklist", {})), llm=llm, kg=StubKG(llm), graph=g,
                   research_enabled=cfg.get("external_research", True))


def _record(rt: Runtime, stage: str, comp: dict | None, vs: list[dict], trace: dict | None) -> None:
    rt.state["violations"][stage] = vs
    if trace:
        rt.state["traces"][stage] = trace
    if comp and comp.get("concerns"):
        rt.state["concerns"][stage] = comp["concerns"]


def _verb_lexicon() -> dict:
    lx = bloom_lexicon()
    return {f"L{k}": v for k, v in lx["levels"].items()}


# ================================================================== S1 intake
def s1_intake(rt: Runtime) -> None:
    rt.log("S1 intake → Course Context Object")
    regs = regulations()
    obj, meta = call(rt, "G1", {"form": rt.state["form"], "programmes": [{"uid": "BTECH-CSE", "name": "B.Tech. Computer Science and Engineering"}],
                                "regulation_facts": [{"id": f["id"], "text": f["text"]} for f in regs["facts"]]})
    cco = obj.model_dump()
    d = det.apply_defaults(cco)
    f = cco["fields"]
    st = rt.state
    st["cco"] = cco
    st["defaults"] = d
    st.update(ltp=d["ltp"], weeks=d["weeks"], level=d["level"], midsem_after_week=d["midsem_after_week"],
              lab_required=f["lab"].get("required"), topic_groups=f["topics"]["topic_groups"],
              hours_budget=det.hours_budget(d["ltp"], d["weeks"]), bloom_band=det.bloom_band(d["level"]))
    progs = f["target_students"].get("programmes") or ["BTECH-CSE"]
    st["programmes"] = [p for p in progs if p == "BTECH-CSE"] or ["BTECH-CSE"]
    st["programme_pos"] = [po for p in st["programmes"] for po in rt.kg.programme_pos(p)]
    st["activity_po_map"] = {k: v for p in st["programmes"] for k, v in pedagogy()["activity_po_map"].get(p, {}).items()}
    st["cco_compact"] = {
        "course_name": f["course_name"].get("value"), "description": f["short_description"].get("value"),
        "topic_groups": f["topics"]["topic_groups"], "topics_treatment": f["topics"]["topics_treatment"],
        "central_question": f["intent"].get("central_question"), "pedagogical_emphasis": f["intent"].get("pedagogical_emphasis"),
        "negative_constraints": f["intent"].get("negative_constraints"), "target_students": {k: f["target_students"].get(k) for k in ("programmes", "years", "assumed_background")},
        "level": d["level"], "credits": d["credits"], "ltp": d["ltp"], "weeks": d["weeks"],
        "lab": {"required": f["lab"].get("required"), "infrastructure": f["lab"].get("infrastructure")},
        "assessment_prefs": {k: f["assessment_prefs"].get(k) for k in ("preferred", "avoid", "rationale")},
        "special_constraints": f["special_constraints"].get("items"),
    }
    g = rt.graph
    g.put("NewCourse", "COURSE", {"title": st["cco_compact"]["course_name"], "credits": d["credits"], "ltp": d["ltp"], "weeks": d["weeks"],
                                  "level": d["level"]}, created_by="G1", prompt_version=meta["prompt_version"])
    for k, fv in f.items():
        g.put("ContextField", f"CCO.{k}", {"status": fv.get("status"), "raw": fv.get("raw"), "value": fv.get("value")}, created_by="G1",
              sources=[{"tag": "USER", "ref": f"CCO.{k}"}])
    for a in d["assumptions"]:
        g.put("Assumption", a["id"], a, created_by="S1-defaults", sources=[{"tag": "INFERRED", "ref": None, "basis": a["basis"]}])
    for tg in st["topic_groups"]:
        g.put("TopicGroup", tg["id"], tg, created_by="G1", sources=[{"tag": "USER", "ref": "CCO.topics"}])
    _record(rt, "intake", cco, [], {"generator": meta})
    rt.log(f"  CCO: {len(st['topic_groups'])} topic groups · level {d['level']} · L-T-P {d['ltp']} · {d['weeks']} weeks · "
           f"{len(d['assumptions'])} assumptions · conflicts {len(cco['conflicts'])}")
    rt.save()


# ================================================================== S2 positioning (internal KG + external research)
def s2_positioning(rt: Runtime) -> None:
    rt.log("S2 curriculum positioning")
    st, kg = rt.state, rt.kg
    cc = st["cco_compact"]
    new_topics = [t["text"] for g in cc["topic_groups"] for t in g["topics"]] or [g["title"] for g in cc["topic_groups"]]
    query = f"{cc['course_name']}. {cc.get('description') or ''} " + "; ".join(new_topics)
    hits = kg.search_courses(query, k=12, exclude=rt.exclude)
    uids = [h["uid"] for h in hits]
    for bg in (cc["target_students"].get("assumed_background") or []):   # courses the professor named explicitly
        for code in re.findall(r"[A-Z]{2,4}\s?\d{3}[A-Z]?", bg):
            u = kg.resolve(code)
            if u and u not in uids and u.upper() not in rt.exclude:
                uids.append(u)
    candidates, overlaps = [], []
    for u in uids:
        c = kg.course(u, exclude=rt.exclude)
        if not c:
            continue
        ov = kg.topic_overlap(new_topics, u)
        overlaps.append({"course_uid": u, **ov})
        candidates.append({"uid": u, "aliases": c["aliases"], "name": c["name"], "level": c["level"], "credits": c["credits"],
                           "cluster": c["cluster"], "description": (c["description"] or "")[:700],
                           "cos": [x["text"][:220] for x in c["cos"]], "topics": c["topics"][:40],
                           "prereqs": [p["uid"] for p in c["prereqs"]], "prereq_text": c["prereq_text"], "anti": c.get("anti_index"),
                           "overlap": {"weighted_jaccard": ov["weighted_jaccard"], "shared_topics": ov["shared_topics"][:12], "method": ov["method"]}})
    st["overlap_computed"] = overlaps
    st["known_course_uids"] = [r["uid"] for r in kg.index(exclude=rt.exclude)]
    st["course_levels"] = {r["uid"]: r["level"] for r in kg.index(exclude=rt.exclude)}
    topic_links = [{"tg_id": g["id"], "text": t["text"], "candidate_topics": kg.topic_candidates([t["text"]], k=3, exclude=rt.exclude)[0]["candidates"]}
                   for g in cc["topic_groups"] for t in g["topics"]][:40]
    rt.log(f"  internal candidates: {[c['uid'] + ' ' + str(c['overlap']['weighted_jaccard']) for c in candidates]}")

    ext = {"accepted": [], "rejected": [], "plan": None}
    rpath = rt.run_dir / "research.json"
    if rpath.exists():
        ext = json.loads(rpath.read_text(encoding="utf-8"))
        rt.log(f"  external research loaded from {rpath.name} ({len(ext['accepted'])} accepted)")
    elif rt.research_enabled:
        from profsagent.research.external import ExternalResearch
        try:
            ext = ExternalResearch(rt.llm, rt.log).run(cc, rt.blocklist, rt.run_id)
            rpath.write_text(json.dumps(ext, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
        except Exception as e:  # noqa: BLE001
            rt.log(f"  external research failed: {e}")
    st["external_courses"] = ext["accepted"]
    st["research"] = {"plan": ext.get("plan"), "rejected": ext.get("rejected")}
    ext_compact = [{"id": e["id"], "institution": e["institution"], "title": f"{e.get('course_code') or ''} {e.get('course_title') or ''}".strip(),
                    "url": e["url"], "summary": e.get("summary"), "topics": e.get("topics", [])[:20],
                    "assessment": e.get("assessment"), "relevance": e.get("relevance")} for e in ext["accepted"]]
    for e in ext["accepted"]:
        rt.graph.put("ExternalCourse", e["id"], {k: e.get(k) for k in ("institution", "course_code", "course_title", "url", "summary", "topics",
                                                                        "weekly_sequence", "assessment", "relevance")},
                     created_by="X2", sources=[{"tag": "EXTERNAL", "ref": e["url"]}])
    th = pedagogy()["thresholds"]
    ctx = {"cco": cc, "new_course_topic_links": topic_links, "candidates": candidates,
           "programme_structure": {"note": "programme core/elective structure not available in the stub KG"},
           "thresholds": {"anti_requisite_overlap": th["anti_requisite_overlap"], "substantial_overlap": th["substantial_overlap"]},
           "external_candidates": ext_compact}
    comp, vs, trace = generate(rt, "G2", ctx, apply=lambda s, c: {**s, "positioning": c}, stages=["positioning"])
    st["positioning"] = comp
    for p in comp["prerequisites"]:
        rt.graph.link("COURSE", "REQUIRES", p["course_uid"], kind=p["kind"], relied_topics=p["relied_topics"], justification=p["justification"])
    for o in overlaps:
        rt.graph.link("COURSE", "OVERLAPS", o["course_uid"], weighted_jaccard=o["weighted_jaccard"], method=o["method"])
    for c in comp["comparable"]:
        rt.graph.link("COURSE", "COMPARABLE_TO", c["ref"], take=c["take"], avoid=c["avoid"])
    _record(rt, "positioning", comp, vs, trace)
    rt.save()


# ================================================================== S3 constraints + feasibility
def s3_constraints(rt: Runtime) -> None:
    rt.log("S3 constraints + feasibility")
    st = rt.state
    regs = regulations()
    obj, meta = call(rt, "G3", {"cco": st["cco_compact"], "regulation_facts": [{"id": f["id"], "text": f["text"]} for f in regs["facts"]]})
    tc = obj.model_dump()
    st["constraints"] = st["defaults"]["constraints"] + tc["constraints"]
    st["constraint_conflicts"] = tc["conflicts"]
    st["constraints_untranslatable"] = tc["untranslatable"]
    hb = st["hours_budget"]
    st["feasibility"] = {"lecture_hours_available": hb["lecture_hours_total"], "tutorial_hours_available": hb["tutorial_hours_total"],
                         "lab_hours_available": hb["lab_hours_total"], "note": "topic-level feasibility is checked after S5 by the scheduler"}
    for c in st["constraints"]:
        rt.graph.put("Constraint", c["id"], c, created_by="G3" if c["id"] >= "K10" else "S1-defaults", sources=[c.get("source") or {}])
    _record(rt, "constraints", tc, [], {"generator": meta})
    rt.log(f"  {len(st['constraints'])} constraints ({len(tc['constraints'])} from professor text) · conflicts {len(tc['conflicts'])}")
    rt.save()


# ================================================================== S4 outcomes
def s4_outcomes(rt: Runtime) -> None:
    rt.log("S4 learning design: COs → CO–PO → LOs")
    st, kg = rt.state, rt.kg
    lx = bloom_lexicon()
    ped = pedagogy()
    cc = st["cco_compact"]
    ex_query = f"{cc['course_name']} " + " ".join(g["title"] for g in cc["topic_groups"])
    exemplars = kg.exemplar_cos(ex_query, st["level"], k=8, exclude=rt.exclude)
    pri = kg.priors(exclude=rt.exclude)
    st["weight_priors"] = pri["weights"]
    co_count = dict(ped["co_count"])
    ctx = {"cco": cc, "positioning": {k: st["positioning"].get(k) for k in ("prerequisites", "overlaps", "comparable", "existence")},
           "constraints": [c for c in st["constraints"] if c["target"].startswith(("co.", "content."))],
           "bloom_band": st["bloom_band"], "co_count": co_count, "verb_lexicon": _verb_lexicon(), "banned_verbs": lx["banned"],
           "degree_bank": degree_bank(), "exemplars": exemplars, "programme_pos": st["programme_pos"],
           "assessment_evidence_types": ped["assessment_evidence_types"]}
    comp, vs, trace = generate(rt, "G4", ctx, apply=lambda s, c: {**s, "cos": c["cos"], "topic_group_proposals": c["topic_group_proposals"]},
                               stages=["cos"])
    st["cos"], st["topic_group_proposals"] = comp["cos"], comp["topic_group_proposals"]
    _record(rt, "cos", comp, vs, trace)
    rt.graph.remove_label("CO")
    for c in st["cos"]:
        rt.graph.put("CO", c["id"], c, created_by="G4", sources=c.get("sources"))
        for tg in c.get("covers_topic_groups", []):
            rt.graph.link(c["id"], "COVERS_GROUP", tg)

    # CO–PO
    pos = st["programme_pos"]
    ctx5 = {"cos": [{k: c[k] for k in ("id", "statement", "verb", "behaviour", "condition", "degree", "bloom_level", "evidence_types")} for c in st["cos"]],
            "programme_pos": pos, "activity_vocabulary": ped["activity_vocabulary"], "activity_po_map": st["activity_po_map"],
            "corpus_patterns": [], "po_gap_hints": st["positioning"].get("po_gap_hints", [])}
    comp5, vs5, trace5 = generate(rt, "G5", ctx5, apply=lambda s, c: {**s, "copo": c["mappings"]}, stages=["copo"])
    st["copo"] = comp5["mappings"]
    _record(rt, "copo", comp5, vs5, trace5)
    for m in st["copo"]:
        rt.graph.link(m["co_id"], "MAPS_TO", m["po_uid"], strength_provisional=m["strength_provisional"], justification=m["justification"],
                      evidencing_activities=m["evidencing_activities"])

    # LOs
    cand_topics = kg.topic_candidates([t["text"] for g in cc["topic_groups"] for t in g["topics"]][:30], k=2, exclude=rt.exclude)
    canon = {c["topic_uid"]: c for x in cand_topics for c in x["candidates"]}
    ctx6 = {"cos": st["cos"], "cco": cc, "positioning": {"prerequisites": st["positioning"].get("prerequisites")},
            "hours_budget": st["hours_budget"], "lo_count": ped["lo_count"], "verb_lexicon": _verb_lexicon(), "banned_verbs": lx["banned"],
            "degree_bank": degree_bank(),
            "canonical_topic_candidates": [{"topic_uid": u, "canonical_name": c["canonical_name"], "definition": None} for u, c in list(canon.items())[:40]]}
    comp6, vs6, trace6 = generate(rt, "G6", ctx6, apply=lambda s, c: {**s, "los": c["los"]}, stages=["los"])
    st["los"] = comp6["los"]
    _record(rt, "los", comp6, vs6, trace6)
    rt.graph.remove_label("LO")
    for lo in st["los"]:
        rt.graph.put("LO", lo["id"], lo, created_by="G6", sources=lo.get("sources"))
        rt.graph.link(lo["parent_co"], "DECOMPOSES_INTO", lo["id"])
        for r in lo.get("requires", []):
            rt.graph.link(lo["id"], "REQUIRES", r)
    rt.save()


# ================================================================== S5 structure + S6 schedule
def s5_structure(rt: Runtime) -> None:
    rt.log("S5 structure (modules/topics) → S6 schedule")
    st = rt.state
    hb = st["hours_budget"]
    priors = []  # stub KG has no per-topic hour priors
    ctx = {"los": st["los"], "cos": [{k: c[k] for k in ("id", "statement", "bloom_level")} for c in st["cos"]],
           "hours_budget": {**hb, "lecture_hours_per_week": st["ltp"]["L"]}, "corpus_topic_priors": priors,
           "topic_precedence_prior": [], "constraints": [c for c in st["constraints"] if c["target"].startswith(("schedule.", "content."))],
           "topic_groups": st["topic_groups"], "topic_group_proposals": st.get("topic_group_proposals", []),
           "special_constraints": st["cco_compact"].get("special_constraints")}

    def apply(s, c):
        s = {**s, "modules": c["modules"]}
        topics = [{**t, "module_order": m["order"]} for m in c["modules"] for t in m["topics"]]
        s["schedule"] = det.schedule(topics, s["weeks"], s["ltp"]["L"], s["midsem_after_week"])
        return s
    comp, vs, trace = generate(rt, "G7", ctx, apply=apply, stages=["structure", "schedule"])
    st["modules"] = comp["modules"]
    st["structure_meta"] = {k: comp.get(k) for k in ("cut_candidates", "constraint_notes", "hours_total")}
    topics = [{**t, "module_order": m["order"]} for m in comp["modules"] for t in m["topics"]]
    st["schedule"] = det.schedule(topics, st["weeks"], st["ltp"]["L"], st["midsem_after_week"])
    _record(rt, "structure", comp, vs, trace)
    g = rt.graph
    for lab in ("Module", "CourseTopic", "Week", "Lecture"):
        g.remove_label(lab)
    for m in st["modules"]:
        g.put("Module", m["id"], {k: m[k] for k in ("title", "order", "primary_cos")}, created_by="G7")
        for t in m["topics"]:
            g.put("CourseTopic", t["id"], t, created_by="G7", sources=t.get("sources"))
            g.link(m["id"], "CONTAINS", t["id"], order=t.get("suggested_order"))
            for lo in t["serves_los"]:
                g.link(lo, "TAUGHT_VIA", t["id"])
            for r in t.get("requires", []):
                g.link(t["id"], "REQUIRES", r)
            if t.get("topic_uid"):
                g.link(t["id"], "SAME_AS", t["topic_uid"])
    for w in st["schedule"]["weeks"]:
        g.put("Week", f"W{w['week']:02d}", {"n": w["week"], "lecture_hours": st["ltp"]["L"], "tutorial_hours": st["ltp"]["T"], "lab_hours": st["ltp"]["P"],
                                           "is_midsem_boundary": w["is_midsem_boundary"]}, created_by="S6-scheduler")
        for i, it in enumerate(w["items"], 1):
            lid = f"W{w['week']:02d}.L{i}"
            g.put("Lecture", lid, {"slot": i, "hours": it["hours"]}, created_by="S6-scheduler")
            g.link(lid, "IN_WEEK", f"W{w['week']:02d}")
            g.link(it["topic_id"], "DELIVERED_IN", lid, hours=it["hours"])
    s = st["schedule"]
    rt.log(f"  schedule: {'feasible' if s['feasible'] else 'INFEASIBLE'} · need {s['hours_needed']} h / {s['hours_available']} h")
    rt.save()


def _schedule_view(st: dict) -> list[dict]:
    tmap = {t["id"]: {**t, "module": m["id"]} for m in st["modules"] for t in m["topics"]}
    out = []
    for w in st["schedule"]["weeks"]:
        out.append({"week": w["week"], "midsem_exam_after_this_week": w["week"] == st["midsem_after_week"],
                    "topics": [{"id": it["topic_id"], "title": tmap[it["topic_id"]]["title"], "hours": it["hours"],
                                "hands_on": tmap[it["topic_id"]].get("hands_on"), "serves_los": tmap[it["topic_id"]]["serves_los"]}
                               for it in w["items"] if it["topic_id"] in tmap]})
    return out


# ================================================================== S7 labs/tutorials + assessment
def s7_activities_assessment(rt: Runtime) -> None:
    rt.log("S7 lab/tutorial plan + assessment blueprint")
    st = rt.state
    ped = pedagogy()
    sched = _schedule_view(st)
    ctx8 = {"schedule": sched, "los": [{k: lo[k] for k in ("id", "statement", "bloom_level", "hands_on", "suggested_task_type")} for lo in st["los"]],
            "ltp": st["ltp"], "weeks": st["weeks"], "lab_info": st["cco_compact"]["lab"],
            "constraints": [c for c in st["constraints"] if c["target"].startswith("lab.")]}
    comp8, vs8, trace8 = generate(rt, "G8", ctx8, apply=lambda s, c: {**s, "labs_tutorials": c}, stages=["labs"])
    st["labs_tutorials"] = comp8
    _record(rt, "labs", comp8, vs8, trace8)

    lo_parent = {lo["id"]: lo["parent_co"] for lo in st["los"]}
    wp = {t: {"median": v["median"], "iqr": v["iqr"], "n": v["n"]} for t, v in (st.get("weight_priors") or {}).items()}
    for t, band in ped["thresholds"]["weight_band_fallback"].items():
        if wp.get(t, {}).get("n", 0) < 5:
            wp[t] = {"median": None, "iqr": band, "n": wp.get(t, {}).get("n", 0), "note": "fallback band (stub n < 5)"}
    ctx9 = {"los": [{k: lo[k] for k in ("id", "parent_co", "statement", "bloom_level", "suggested_task_type", "is_capstone")} for lo in st["los"]],
            "cos": [{"id": c["id"], "bloom_level": c["bloom_level"], "evidence_types": c["evidence_types"],
                     "po_mappings": [m for m in st["copo"] if m["co_id"] == c["id"]]} for c in st["cos"]],
            "schedule": {"weeks": sched, "midsem_week": st["midsem_after_week"],
                         "endsem_window": f"after teaching week {st['weeks']}",
                         "note": f"The mid-sem exam is held in the recess after teaching week {st['midsem_after_week']}: give it release_week = "
                                 f"due_week = {st['midsem_after_week']} (it covers weeks 1–{st['midsem_after_week']}). The end-sem exam: "
                                 f"release_week = due_week = {st['weeks']} (it may cover everything)."},
            "labs_tutorials": {"labs": [{k: l[k] for k in ("id", "week", "produces_assessed_artifact")} for l in comp8.get("labs", [])]},
            "constraints": [c for c in st["constraints"] if c["target"].startswith("assessment.")],
            "weight_priors": wp, "component_count": ped["thresholds"]["component_count"],
            "activity_vocabulary": ped["activity_vocabulary"], "activity_po_map": st["activity_po_map"]}

    def apply9(s, c):
        s = {**s, "assessment": c}
        s["copo_computed"] = det.copo_strengths([x["id"] for x in s["cos"]], lo_parent, c["components"], s["activity_po_map"], s["copo"],
                                                ped["thresholds"]["co_po_strength"])
        return s
    comp9, vs9, trace9 = generate(rt, "G9", ctx9, apply=apply9, stages=["assessment"])
    st["assessment"] = comp9
    st["copo_computed"] = det.copo_strengths([x["id"] for x in st["cos"]], lo_parent, comp9["components"], st["activity_po_map"], st["copo"],
                                             ped["thresholds"]["co_po_strength"])
    st["co_marks_share"] = det.co_marks_share(lo_parent, comp9["components"])
    _record(rt, "assessment", comp9, vs9, trace9)
    g = rt.graph
    for lab in ("LabSession", "Tutorial", "Assessment"):
        g.remove_label(lab)
    for s_ in comp8.get("labs", []):
        g.put("LabSession", s_["id"], s_, created_by="G8")
        g.link(s_["id"], "IN_WEEK", f"W{s_['week']:02d}")
        for lo in s_["practises_los"]:
            g.link(lo, "PRACTISED_IN", s_["id"])
    for s_ in comp8.get("tutorials", []):
        g.put("Tutorial", s_["id"], s_, created_by="G8")
        g.link(s_["id"], "IN_WEEK", f"W{s_['week']:02d}")
    for c in comp9["components"]:
        for inst in c["instances"]:
            g.put("Assessment", inst["id"], {**inst, "type": c["type"], "component_weight_pct": c["weight_pct"], "activity_types": c["activity_types"]},
                  created_by="G9")
            g.link(inst["id"], "RELEASED_IN", f"W{inst['release_week']:02d}")
            g.link(inst["id"], "DUE_IN", f"W{inst['due_week']:02d}")
            for a in inst["assesses"]:
                g.link(inst["id"], "ASSESSES", a["lo_id"], marks_pct=a["marks_pct_of_instance"], bloom_level=a["bloom_level"])
            for t in inst.get("covers_topics", []):
                g.link(inst["id"], "COVERS", t)
    for r in st["copo_computed"]:
        for e in g.out(r["co_id"], "MAPS_TO"):
            if e["dst"] == r["po_uid"]:
                e["props"].update(strength_computed=r["strength_computed"], share=r["share"])
    rt.save()


# ================================================================== S8 resources
def s8_resources(rt: Runtime) -> None:
    rt.log("S8 resources (API candidates → G10 → verification)")
    st, kg = rt.state, rt.kg
    rel = [p["course_uid"] for p in st["positioning"].get("prerequisites", [])] + [o["course_uid"] for o in st["positioning"].get("overlaps", [])[:4]]
    ext_tbs = [tb for e in st.get("external_courses", []) for tb in e.get("textbooks", [])][:12]
    qp, _ = call(rt, "X3", {"course": {"course_name": st["cco_compact"]["course_name"], "level": st["level"], "description": st["cco_compact"].get("description")},
                            "modules": [{"id": m["id"], "title": m["title"], "topics": [t["title"] for t in m["topics"]]} for m in st["modules"]],
                            "external_textbooks": ext_tbs}, role="extract")
    queries = [(q.kind, q.query) for q in qp.queries[:12]]
    cands: dict[str, dict] = {}
    for kind, q in queries:
        for c in (openlibrary(q, 2) if kind == "book" else crossref(q, 3)):
            cands.setdefault(c["candidate_id"], c)
    rt.log(f"  {len(cands)} API candidates from {len(queries)} X3 queries")
    ctx = {"modules_topics": [{"id": m["id"], "title": m["title"], "topics": [{"id": t["id"], "title": t["title"]} for t in m["topics"]]} for m in st["modules"]],
           "cco": st["cco_compact"], "corpus_resources": kg.corpus_resources(rel)[:10], "retrieved_external": list(cands.values())}
    obj, meta = call(rt, "G10", ctx)
    comp = obj.model_dump()
    kept = []
    for r in comp["resources"]:
        r["verification"] = verify_pick(r, cands)
        kept.append(r)
    st["resources"] = kept
    st["resource_policy"] = {"textbook_policy": comp["textbook_policy"], "reason": comp["policy_reason"], "search_requests": comp["search_requests"]}
    vs = rules.run(st, ["resources"])
    _record(rt, "resources", comp, vs, {"generator": meta})
    for r in kept:
        rid = r["candidate_id"]
        rt.graph.put("Resource", f"RES:{rid}", r, created_by="G10", sources=[{"tag": "EXTERNAL", "ref": cands.get(rid, {}).get("url")}])
        for s_ in r["supports_topics"]:
            rt.graph.link(s_["topic_id"], "READING", f"RES:{rid}")
    rt.log(f"  resources: {sum(r['verification']['verified'] for r in kept)}/{len(kept)} verified")
    rt.save()


# ================================================================== S9 narrative
def s9_narrative(rt: Runtime) -> None:
    rt.log("S9 narrative")
    st = rt.state
    summary = {"cos": [{"id": c["id"], "statement": c["statement"]} for c in st["cos"]],
               "modules": [{"id": m["id"], "title": m["title"], "topics": [t["title"] for t in m["topics"]]} for m in st["modules"]],
               "prerequisites": st["positioning"].get("prerequisites"), "overlaps": st["positioning"].get("overlaps"),
               "assessment_components": [{"type": c["type"], "weight_pct": c["weight_pct"]} for c in st["assessment"]["components"]],
               "labs": bool(st["labs_tutorials"].get("labs")), "ltp": st["ltp"], "weeks": st["weeks"]}
    obj, meta = call(rt, "G11", {"approved_graph_summary": summary, "cco": st["cco_compact"]})
    st["narrative"] = obj.model_dump()
    _record(rt, "narrative", st["narrative"], [], {"generator": meta})
    rt.save()


# ================================================================== gates
GATE_FREEZE = {"gate1_context": ["ContextField", "Constraint", "TopicGroup"], "gate2_outcomes": ["CO", "LO"], "gate3_proposal": []}


def all_violations(st: dict) -> list[dict]:
    return [x for vs in st.get("violations", {}).values() for x in vs]


def gate(rt: Runtime, name: str, decision: dict) -> None:
    st = rt.state
    frozen = rt.graph.freeze_labels(GATE_FREEZE.get(name, [])) if decision.get("decision") == "approve" else []
    st["approvals"].append({"gate": name, **decision, "at": time.time(), "frozen": len(frozen),
                            "open_errors": len(rules.errors(all_violations(st)))})
    rt.graph.put("Approval", f"APP{len(st['approvals'])}", st["approvals"][-1], created_by=decision.get("by", "professor"))
    rt.log(f"GATE {name}: {decision.get('decision')} by {decision.get('by')} · froze {len(frozen)} nodes")
    rt.save()
