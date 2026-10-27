"""What each screen shows, built from a run's files (state.json, run.log, llm_calls.jsonl). Read-only; no AI calls.

Every item keeps the reference it came from where the run has one: regulation clause ids, KG course codes with their
TechTree link, URLs of courses at other universities, DOIs and ISBNs.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from profsagent.config import DATA

STEPS = [
    ("fill_details", "Filling in the details you left blank"),
    ("gate0_details", "Your check: course details"),
    ("s1_intake", "Reading your form"),
    ("s2_positioning", "Finding related IIIT-D courses and similar courses elsewhere"),
    ("s3_constraints", "Turning your wishes and the regulations into rules"),
    ("gate1_context", "Your check: course context"),
    ("s4_outcomes", "Writing course outcomes and learning outcomes"),
    ("gate2_outcomes", "Your check: outcomes"),
    ("s5_structure", "Planning modules and weeks"),
    ("s7_activities_assessment", "Planning labs, tutorials and assessment"),
    ("s8_resources", "Finding and checking books and papers"),
    ("s9_narrative", "Writing the course description"),
    ("render", "Filling in the course sheet"),
    ("gate3_proposal", "Your check: final course sheet"),
    ("publish", "Saving the course"),
]
BLOOM = {1: "Remember", 2: "Understand", 3: "Apply", 4: "Analyse", 5: "Evaluate", 6: "Create"}
PROGRAMME = {"BTECH-COMMON": "B.Tech (all)", "BTECH-CSE": "B.Tech CSE", "BTECH-CSAI": "B.Tech CSAI", "MTECH-CSE": "M.Tech CSE"}
ASSESS = {"endsem": "End-sem exam", "midsem": "Mid-sem exam", "quiz": "Quizzes", "assignment": "Assignments", "project": "Project", "lab": "Labs",
          "presentation": "Presentations", "report": "Reports", "participation": "Participation", "other": "Other"}
FIXABLE = {"professor": "Needs your decision", "repair": "ProfsAgent could not fix this", "fixer": "ProfsAgent could not fix this"}


def state_of(run_dir: Path) -> dict | None:
    p = run_dir / "state.json"
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except ValueError:   # being written right now
        return None


@lru_cache(maxsize=1)
def _catalogue() -> dict:
    """Course code → TechTree entry; cross-listed entries ("CSE600/ECE600/ECE600A") answer for each of their codes."""
    try:
        idx = json.loads((DATA / "techtree_index.json").read_text(encoding="utf-8"))
    except OSError:
        return {}
    out: dict = {}
    for v in idx.values():
        for c in (v.get("code") or "").upper().split("/"):
            if c.strip():
                out.setdefault(c.strip(), v)
    return out


def course_ref(code: str | None) -> dict:
    c = _catalogue().get((code or "").upper(), {})
    return {"code": code, "name": c.get("name"), "url": c.get("catalogue_url")}


# ------------------------------------------------------------------ progress
def progress(run_dir: Path, st: dict | None) -> dict:
    st = st or {}
    done = set(st.get("stages_done", [])) | {a["gate"] for a in st.get("approvals", []) if a.get("decision") == "approve"}
    if (run_dir / "fill.json").exists():
        done.add("fill_details")
    if (run_dir / "input.yaml").exists() and (run_dir / "details_review.json").exists() and \
            json.loads((run_dir / "details_review.json").read_text(encoding="utf-8")).get("decision") == "approve":
        done.add("gate0_details")
    if (run_dir / "proposal.md").exists():
        done.add("render")
    if st.get("neo4j_load"):
        done.add("publish")
    steps = [{"id": k, "label": v, "done": k in done, "gate": k.startswith("gate")} for k, v in STEPS]
    cur = next((s for s in steps if not s["done"]), None)
    log = []
    p = run_dir / "run.log"
    if p.exists():
        log = [x for x in p.read_text(encoding="utf-8", errors="replace").splitlines() if x.strip()][-10:]
    calls = 0
    c = run_dir / "llm_calls.jsonl"
    if c.exists():
        with c.open("rb") as f:
            calls = sum(1 for _ in f)
    return {"steps": steps, "current": cur["id"] if cur else None, "current_label": cur["label"] if cur else None,
            "done": sum(s["done"] for s in steps), "total": len(steps), "log": log, "ai_calls": calls}


# ------------------------------------------------------------------ shared
def _ltp(d) -> str:
    return f"{_num(d.get('L'))}-{_num(d.get('T'))}-{_num(d.get('P'))}" if isinstance(d, dict) else str(d or "")


def course_summary(st: dict) -> dict:
    cc = st.get("cco_compact") or {}
    d = st.get("defaults") or {}
    return {"name": cc.get("course_name"), "credits": _num(d.get("credits")), "ltp": _ltp(st.get("ltp") or d.get("ltp")), "weeks": st.get("weeks"),
            "level": st.get("level"), "department": st.get("department")}


# one plain line per kind of open problem; the individual messages stay available under it
PLAIN = {
    "V23": "Course outcomes are linked to programme outcomes that no assessment tests yet",
    "VA-PROCTOR": "Less than 40% of the marks come from invigilated assessment (the course template asks for at least 40%)",
    "V21": "The topic hours don't add up to the lecture hours available",
    "VCO-BL": "Too few course outcomes are at the higher thinking levels (Analyse, Evaluate, Create)",
    "T4": "A course outcome isn't linked to every programme's outcomes",
    "V19": "An assessment covers topics before they are taught",
    "V20": "An assessment weight is outside the usual range for IIIT-D courses",
    "VTG-TAUGHT": "A topic group from your form isn't taught anywhere",
    "VT-ORDER": "A topic is taught before what it builds on",
}


def open_problems(payload: dict | None) -> dict:
    p = payload or {}
    items = [{"message": x.get("message"), "code": x.get("code"), "where": ", ".join(x.get("nodes") or []), "who": FIXABLE.get(x.get("fixable_by"), "")}
             for x in p.get("open", [])]
    groups: dict[str, dict] = {}
    for x in items:
        g = groups.setdefault(x["code"], {"code": x["code"], "plain": PLAIN.get(x["code"]) or (x["message"] if x["code"].startswith("VREG") else None),
                                          "items": []})
        g["items"].append(x)
    return {"blocked": bool(p.get("blocked")), "errors": p.get("open_errors", 0), "warnings": p.get("open_warnings", 0), "problem": p.get("problem"),
            "items": items, "groups": list(groups.values())}


def _issues(st: dict, ids: set[str]) -> list[dict]:
    out = []
    for stage, vs in (st.get("violations") or {}).items():
        for v in vs:
            if any(n in ids or n.split(".")[0] in ids for n in v.get("nodes") or []):
                out.append({"severity": v.get("severity"), "message": v.get("message"), "code": v.get("code")})
    return out


# ------------------------------------------------------------------ rules in plain words
TARGETS = {"schedule.weeks": "Teaching weeks", "course.credits": "Credits", "schedule.lecture_hours_per_week": "Lecture hours per week",
           "schedule.tutorial_hours_per_week": "Tutorial hours per week", "lab.hours_per_week": "Lab hours per week"}
COMPONENT = {"midsem": "a mid-sem exam", "endsem": "an end-sem exam"}
OPS = {"==": ":", "<=": "at most", ">=": "at least", "<": "below", ">": "above", "!=": "not"}


def _num(v):
    return int(v) if isinstance(v, float) and v.is_integer() else v


def _raw(k: dict) -> str:
    return re.sub(r"^\s*[-•*]\s*", "", k.get("raw") or "").strip()


def rule_text(k: dict) -> tuple[str, str]:
    """(plain sentence, kind): kind is 'exclude' for "should NOT become" rules, else 'include'.
    Known targets get a fixed sentence; anything else keeps the professor's own words."""
    t, v = k.get("target") or "", _num(k.get("value"))
    inner = re.search(r"\[(.+?)\]", t)
    if t.startswith("content.must_exclude"):
        said, checked = _raw(k), (inner.group(1) if inner else "")
        if said and checked and checked.lower() not in said.lower():
            return f"Must not become: {said} (checked as: {checked})", "exclude"
        return "Must not become: " + (said or checked or t), "exclude"
    if t == "lab.tools_include":
        return f"Lab tools include: {v}", "include"
    if t.startswith("assessment.component[") and t.endswith(".present"):
        what = COMPONENT.get(inner.group(1), inner.group(1)) if inner else t
        return (f"Assessment includes {what}" if v is not False else f"Assessment has no {what}"), "include"
    if t == "lab.present":
        return ("The course has a lab" if v is not False else "No lab"), "include"
    if t == "schedule.midsem_after_week":
        return f"Mid-sem exam after week {v}", "include"
    if t in TARGETS:
        return f"{TARGETS[t]}{OPS.get(k.get('op'), ' ' + str(k.get('op')))} {v}", "include"
    return _raw(k) or f"{t.replace('.', ' ').replace('_', ' ')} {OPS.get(k.get('op'), k.get('op'))} {v}", "include"


def ref_label(ref: str | None) -> dict | None:
    """A rule's source as the professor should see it, with a link for regulation clauses."""
    if not ref:
        return None
    if ref.startswith("UGREG-2025"):
        from profsagent.config import regulations
        doc = (regulations().get("source_docs") or {}).get("UGREG-2025") or {}
        return {"text": "UG Regulations 2025 " + ref[len("UGREG-2025"):], "url": doc.get("url")}
    if ref.startswith("ASM"):
        return {"text": "Assumption (above)", "url": None}
    if ref.startswith("CCO"):
        return {"text": "Your form", "url": None}
    return {"text": ref, "url": None}


# ------------------------------------------------------------------ gate 1: context
def gate1(st: dict) -> dict:
    pos = st.get("positioning") or {}
    judged = {o.get("course_uid"): o for o in pos.get("overlaps") or []}
    ext = {e["id"]: e for e in st.get("external_courses") or []}
    wishes, rules = [], []
    for k in st.get("constraints") or []:
        src = k.get("source") or {}
        text, kind = rule_text(k)
        item = {"text": text, "kind": kind, "hard": k.get("hardness") == "hard", "ref": src.get("ref"),
                "source": ref_label(src.get("ref")), "tag": src.get("tag")}
        bucket = wishes if src.get("tag") == "USER" else rules
        if not any(x["text"] == text for x in bucket):   # the same wish is often compiled from two form fields
            bucket.append(item)
    comparable = []
    for c in pos.get("comparable") or []:
        if c.get("kind") == "external":
            e = ext.get(c.get("ref"), {})
            comparable.append({"title": c.get("title"), "where": e.get("institution"), "url": e.get("url"), "take": c.get("take"), "avoid": c.get("avoid")})
        else:
            r = course_ref(c.get("ref"))
            comparable.append({"title": f"{c.get('ref')} {r['name'] or c.get('title') or ''}".strip(), "where": "IIIT-D", "url": r["url"],
                               "take": c.get("take"), "avoid": c.get("avoid")})
    return {
        "course": course_summary(st),
        "assumptions": [{"what": a.get("what"), "value": a.get("value") if a.get("value") is not None else "Not fixed: estimated in the plan",
                         "basis": a.get("basis"), "confirm_with": a.get("confirm_with")}
                        for a in (st.get("defaults") or {}).get("assumptions", [])],
        "wishes": wishes, "rules": rules,
        "untranslatable": [x if isinstance(x, str) else (x.get("raw") or x.get("text") or json.dumps(x, ensure_ascii=False)) for x in st.get("constraints_untranslatable") or []],
        "constraint_conflicts": st.get("constraint_conflicts") or [],
        "form_conflicts": (st.get("cco") or {}).get("conflicts") or [],
        "existence": pos.get("existence"),
        "prerequisites": [{**course_ref(p.get("course_uid")), "kind": p.get("kind"), "relied_topics": p.get("relied_topics") or [],
                           "why": p.get("justification"), "alternatives": [course_ref(a) for a in p.get("alternatives") or []]}
                          for p in pos.get("prerequisites") or []],
        # overlaps as the KG computed them (IDF-weighted topic overlap), with the AI's verdict where it gave one
        "overlaps": [{**course_ref(o.get("course_uid")), "pct": round(100 * (o.get("weighted_jaccard") or 0), 1),
                      "verdict": judged.get(o.get("course_uid"), {}).get("verdict"), "shared": o.get("shared_topics") or [],
                      "difference": judged.get(o.get("course_uid"), {}).get("differentiation")}
                     for o in sorted(st.get("overlap_computed") or pos.get("overlaps") or [], key=lambda o: -(o.get("weighted_jaccard") or 0))
                     if (o.get("weighted_jaccard") or 0) > 0],
        "anti_requisites": [course_ref(a if isinstance(a, str) else a.get("course_uid")) for a in pos.get("anti_requisites") or []],
        "comparable": comparable,
        "topics": [{"id": g.get("id"), "title": g.get("title"), "topics": [t.get("text") for t in g.get("topics") or []]} for g in st.get("topic_groups") or []],
        "topics_treatment": (st.get("cco_compact") or {}).get("topics_treatment"),
        "concerns": [c.get("detail") if isinstance(c, dict) else c for c in pos.get("concerns") or []],
    }


# ------------------------------------------------------------------ gate 2: outcomes
def gate2(st: dict) -> dict:
    po_label = {}
    for po in st.get("programme_pos") or []:
        po_label[po["uid"]] = {"short": po.get("short_label") or po["uid"].split("/")[-1], "text": (po.get("text") or "").split(":")[0]}
    cos = []
    for co in st.get("cos") or []:
        pos = [{"programme": PROGRAMME.get(m["po_uid"].split("/")[0], m["po_uid"].split("/")[0]), **po_label.get(m["po_uid"], {"short": m["po_uid"], "text": ""}),
                "strength": m.get("strength_provisional")} for m in st.get("copo") or [] if m.get("co_id") == co["id"]]
        cos.append({"id": co["id"], "statement": co.get("statement"), "level": BLOOM.get(co.get("bloom_level"), ""),
                    "los": [{"id": lo["id"], "statement": lo.get("statement"), "level": BLOOM.get(lo.get("bloom_level"), "")}
                            for lo in st.get("los") or [] if lo.get("parent_co") == co["id"]],
                    "pos": pos, "issues": _issues(st, {co["id"]})})
    titles = {g.get("id"): g.get("title") for g in st.get("topic_groups") or []}
    proposals = [{"action": p.get("action"), "targets": [titles.get(t, t) for t in p.get("targets") or []], "proposal": p.get("proposal"), "reason": p.get("reason")}
                 for p in st.get("topic_group_proposals") or []]
    return {"course": course_summary(st), "cos": cos, "co_count_target": st.get("co_count"), "band": st.get("bloom_band"),
            "proposals": proposals, "no_topics_given": not st.get("topic_groups")}


# ------------------------------------------------------------------ gate 3: the whole proposal
def gate3(st: dict, run_dir: Path) -> dict:
    topics = {t["id"]: t["title"] for m in st.get("modules") or [] for t in m.get("topics", [])}
    labs = {}
    for lab in (st.get("labs_tutorials") or {}).get("labs", []):
        labs.setdefault(lab.get("week"), []).append(lab.get("title"))
    sched = st.get("schedule") or {}
    weeks = [{"week": w["week"], "topics": [{"title": topics.get(i["topic_id"], i["topic_id"]), "hours": i.get("hours")} for i in w.get("items", [])],
              "labs": labs.get(w["week"], []), "midsem_after": bool(w.get("is_midsem_boundary"))} for w in sched.get("weeks", [])]
    comps = (st.get("assessment") or {}).get("components") or []
    assess = [{"name": ASSESS.get(c.get("type"), c.get("type")), "weight": c.get("weight_pct"), "invigilated": bool(c.get("proctored")),
               "count": len(c.get("instances") or []), "due": sorted({i.get("due_week") for i in c.get("instances") or [] if i.get("due_week")})} for c in comps]
    books = []
    for r in st.get("resources") or []:
        ident = r.get("identifier") or {}
        link = (f"https://doi.org/{ident['doi']}" if ident.get("doi") else f"https://openlibrary.org/isbn/{ident['isbn']}" if ident.get("isbn")
                else f"https://arxiv.org/abs/{ident['arxiv']}" if ident.get("arxiv") else ident.get("url"))
        books.append({"title": r.get("title"), "authors": ", ".join((r.get("authors") or [])[:3]) + (" et al." if len(r.get("authors") or []) > 3 else ""),
                      "year": r.get("year"), "role": r.get("role"), "link": link,
                      "id": f"DOI {ident['doi']}" if ident.get("doi") else f"ISBN {ident['isbn']}" if ident.get("isbn") else None,
                      "verified": bool((r.get("verification") or {}).get("verified")), "note": r.get("matched_from")})
    ev = None
    p = run_dir / "evaluation_deterministic.json"
    if p.exists():
        try:
            ev = json.loads(p.read_text(encoding="utf-8")).get("summary")
        except ValueError:
            ev = None
    feas = st.get("feasibility") or {}
    return {
        "course": course_summary(st),
        "description": (st.get("narrative") or {}).get("course_description"),
        "weeks": weeks,
        "hours": {"planned": (st.get("structure_meta") or {}).get("hours_total"), "available": feas.get("lecture_hours_available")},
        "assessment": assess, "assessment_total": round(sum(c.get("weight_pct") or 0 for c in comps), 1),
        "invigilated_pct": round(sum(c.get("weight_pct") or 0 for c in comps if c.get("proctored")), 1),
        "co_marks": st.get("co_marks_share") or {},
        "books": books, "books_rejected": len(st.get("resources_rejected") or []), "recheck": reference_check(run_dir, books),
        "evaluation": ev,
        "files": {name: (run_dir / name).exists() for name in ("proposal.md", "course_template.xlsx", "course_sheet.pdf")},
    }


# ------------------------------------------------------------------ independent second check of every ISBN / DOI
def _recheck_one(b: dict) -> dict:
    """Look the identifier up on its own (OpenLibrary edition record / Crossref work) and compare title and year with the
    citation. A second, separate check from the pipeline's own verification."""
    from profsagent.research.resources import _cached_get, _n, _year_of
    ident = b.get("id") or ""
    if ident.startswith("ISBN "):
        rec = _cached_get(f"https://openlibrary.org/isbn/{ident[5:]}.json", {})
        if not rec:
            return {"status": "unreachable"}
        title = f"{rec.get('title', '')}: {rec.get('subtitle')}" if rec.get("subtitle") else rec.get("title", "")
        year, pub = _year_of(rec.get("publish_date")), ", ".join(rec.get("publishers") or [])
    elif ident.startswith("DOI "):
        rec = ((_cached_get(f"https://api.crossref.org/works/{ident[4:]}", {}) or {}).get("message")) or None
        if not rec:
            return {"status": "unreachable"}
        title = (rec.get("title") or [""])[0]
        year, pub = ((rec.get("issued") or {}).get("date-parts") or [[None]])[0][0], (rec.get("container-title") or [""])[0]
    else:
        return {"status": "no identifier"}
    same_title = _n(title)[:20] == _n(b.get("title"))[:20] or _n(b.get("title"))[:20] in _n(title)
    same_year = not (year and b.get("year")) or int(year) == int(b["year"])
    if same_title and same_year:
        return {"status": "match"}
    return {"status": "mismatch", "record": f"{ident} belongs to “{title}”" + (f" ({year}" + (f", {pub}" if pub else "") + ")" if year else "")}


def reference_check(run_dir: Path, books: list[dict]) -> dict:
    """{book title: result}, computed once per set of books and kept in <run>/reference_check.json."""
    key = json.dumps([(b.get("title"), b.get("id"), b.get("year")) for b in books], ensure_ascii=False)
    p = run_dir / "reference_check.json"
    if p.exists():
        try:
            old = json.loads(p.read_text(encoding="utf-8"))
            if old.get("key") == key:
                return old["results"]
        except (OSError, ValueError):
            pass
    results = {}
    for b in books:
        try:
            results[b.get("title")] = _recheck_one(b)
        except Exception:  # noqa: BLE001 — a lookup problem never blocks the page
            results[b.get("title")] = {"status": "unreachable"}
    if run_dir.name.startswith("app-"):   # cache only in the app's own run folders, never in committed CLI runs
        try:
            p.write_text(json.dumps({"key": key, "results": results}, ensure_ascii=False, indent=1), encoding="utf-8")
        except OSError:
            pass
    return results


def approvals(st: dict | None, run_dir: Path | None = None) -> list[dict]:
    out = []
    if run_dir is not None and (run_dir / "details_review.json").exists():
        r = json.loads((run_dir / "details_review.json").read_text(encoding="utf-8"))
        out.append({"gate": "gate0_details", "decision": r.get("decision"), "by": r.get("by"), "comment": r.get("comment"), "at": r.get("at"),
                    "override": None, "suggested": len(r.get("suggested_by_profsagent") or []), "changed": len(r.get("changed_by_professor") or [])})
    return out + [{"gate": a.get("gate"), "decision": a.get("decision"), "by": a.get("by"), "comment": a.get("comment"), "at": a.get("at"),
                   "override": a.get("override")} for a in (st or {}).get("approvals", [])]


# ------------------------------------------------------------------ gate 0: the complete form to check
def details(run_dir: Path) -> dict:
    """The professor's form with ProfsAgent's suggestions filled in, and for each suggestion its reason and sources."""
    import yaml
    from profsagent.app import formmap
    spec = yaml.safe_load((run_dir / "input.yaml").read_text(encoding="utf-8"))
    form = dict(spec.get("app_form") or {})
    fill = json.loads((run_dir / "fill.json").read_text(encoding="utf-8")) if (run_dir / "fill.json").exists() else {}
    filled = fill.get("fields") or {}
    for k, s in filled.items():
        form[k] = s["value"]
    form.pop("consent", None)
    return {"form": form, "filled": filled, "unfilled": fill.get("unfilled") or [], "similar": fill.get("similar") or [],
            "given": fill.get("given") or [], "needed": list(formmap.NEEDED) + ["ltp"]}


def proposal_html(run_dir: Path) -> str:
    import markdown
    src = (run_dir / "proposal.md").read_text(encoding="utf-8")
    src = re.sub(r"(?m)^(\s*)[*+] ", r"\1- ", src)
    return markdown.markdown(src, extensions=["tables", "sane_lists"])
