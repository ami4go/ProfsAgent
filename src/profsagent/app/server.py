"""FastAPI server: the professor UI (static/index.html) and its JSON API over RunManager (course design, Phase 1)
and DeliveryManager (lecture delivery, Phase 2: Vihan's deliverable C, docs/04_phase2_UI_integration_guide.md).

Settings (environment or .env): APP_HOST (default 127.0.0.1, this laptop only), APP_PORT (8000),
KG_BACKEND (neo4j | stub, read by the pipeline), NEO4J_URI.
"""
from __future__ import annotations

import importlib.util
import os
import re
import socket
import time
from contextlib import asynccontextmanager
from pathlib import Path
from urllib.parse import urlparse

import yaml
from fastapi import Body, FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse

from profsagent.app import delivery as dv
from profsagent.app import formmap, views
from profsagent.app.runner import PREFIX, RunManager, read_meta
from profsagent.config import ROOT, RUNS, keys

STATIC = Path(__file__).resolve().parent / "static"
RUN_ID = re.compile(rf"^{PREFIX}[a-z0-9-]+$")
NO_CACHE = {"Cache-Control": "no-store"}

# "Fill with an example": only the required fields and a few others, so ProfsAgent fills in the rest
EXAMPLE = {
    "name": "Software Development using AI",
    "description": "This course examines modern AI-native software development, where developers collaborate with increasingly capable "
                   "coding agents. It covers how to define intent, provide effective context, structure development workflows and "
                   "coordinate AI tools. Students gain practical experience designing and evaluating agent-assisted development processes.",
    "topics": "", "intent_question": "", "intent_emphasis": "", "intent_avoid": "",
    "department": "CSE", "credits": "", "l": "", "t": "", "p": "", "weeks": "", "weekly_effort": "", "programmes": [], "year": "",
    "background": "CSE201 Advanced Programming", "lab": "", "lab_infra": "",
    "assess_pref": [], "assess_avoid": [], "assess_why": "", "special": "", "topics_flexible": True, "external_research": True,
}


_NEO4J = {"at": 0.0, "up": False}


def _neo4j_up() -> bool:
    """Is anything listening on Neo4j's bolt port? Cached for 10 s (a refused localhost connection takes ~2 s on Windows)."""
    if time.time() - _NEO4J["at"] < 10:
        return _NEO4J["up"]
    u = urlparse(os.environ.get("NEO4J_URI", "bolt://localhost:7687"))
    host = "127.0.0.1" if u.hostname in (None, "localhost") else u.hostname
    try:
        with socket.create_connection((host, u.port or 7687), timeout=1.0):
            up = True
    except OSError:
        up = False
    _NEO4J.update(at=time.time(), up=up)
    return up


def _export_pdf(run_dir: Path) -> Path:
    """<run>/course_sheet.pdf via scripts/export_course_sheet_pdf.py (same layout as the official template).
    The script reads <ROOT>/runs/<id>; point its ROOT at the folder above this run's runs folder."""
    spec = importlib.util.spec_from_file_location("export_course_sheet_pdf", ROOT / "scripts" / "export_course_sheet_pdf.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    if run_dir.parent.name == "runs":
        mod.ROOT = run_dir.parent.parent
    return mod.build(run_dir.name)


LID = re.compile(r"^W\d\d\.L\d+$")


def create_app(manager: RunManager | None = None, start_worker: bool = True, delivery: dv.DeliveryManager | None = None) -> FastAPI:
    mgr = manager or RunManager()
    dmgr = delivery or dv.DeliveryManager(runs=mgr.runs)

    @asynccontextmanager
    async def lifespan(_app):
        if start_worker:
            mgr.start()
            dmgr.start()
        yield
        mgr.stop()
        dmgr.stop()

    app = FastAPI(title="ProfsAgent", lifespan=lifespan)
    app.state.manager = mgr
    app.state.delivery = dmgr

    def run_dir(rid: str) -> Path:
        d = mgr.runs / rid
        if not RUN_ID.match(rid) or not (d / "app.json").exists():
            raise HTTPException(404, "No such course run")
        return d

    @app.get("/")
    def index():
        return FileResponse(STATIC / "index.html", headers=NO_CACHE)

    @app.get("/api/health")
    def health():
        backend = (os.environ.get("KG_BACKEND") or "neo4j").lower()
        return {"kg_backend": backend, "neo4j": _neo4j_up() if backend == "neo4j" else None,
                "keys": {"gemini": len(keys("GEMINI_API_KEYS")), "groq": len(keys("GROQ_API_KEYS"))},
                "working_on": mgr.current, "queued": mgr.q.qsize(), "now": time.time()}

    @app.get("/api/options")
    def options():
        return {"departments": formmap.DEPARTMENTS, "programmes": formmap.PROGRAMMES, "years": list(formmap.YEARS), "credits": formmap.CREDITS,
                "assessments": formmap.ASSESSMENTS, "example": EXAMPLE}

    @app.get("/api/catalogue")
    def catalogue(codes: str = ""):
        """Look up course codes the professor typed (e.g. in 'Students should already know') in the TechTree catalogue."""
        found = []
        for c in dict.fromkeys(re.sub(r"\s+", "", x).upper() for x in codes.split(",") if x.strip()):
            r = views.course_ref(c)
            found.append({**r, "found": bool(r["name"])})
        return found[:12]

    @app.get("/api/runs")
    def runs():
        return mgr.list()

    @app.post("/api/runs")
    def create(form: dict = Body(...)):
        rid, errs = mgr.create(form)
        if errs:
            return JSONResponse({"errors": errs}, status_code=422)
        return {"run_id": rid}

    @app.get("/api/runs/{rid}")
    def run(rid: str):
        d = run_dir(rid)
        m = read_meta(d)
        st = views.state_of(d)
        out = {k: m.get(k) for k in ("run_id", "title", "by", "created_at", "status", "gate", "error", "resume_at", "history")}
        out["queue_position"] = mgr.queue_position(rid)
        out["progress"] = views.progress(d, st)
        out["approvals"] = views.approvals(st, d)
        out["phase"] = m.get("phase") or "design"
        out["view"] = None
        if m.get("status") == "waiting" and m.get("gate") == "gate0_details":
            out["view"] = views.details(d)
        elif st and m.get("status") == "waiting":
            g = m.get("gate")
            out["problems"] = views.open_problems(m.get("payload"))
            out["view"] = (views.gate1(st) if g == "gate1_context" else views.gate2(st) if g == "gate2_outcomes" else views.gate3(st, d))
        elif st and m.get("status") == "done":
            out["view"] = views.gate3(st, d)
        if st:
            out["course"] = views.course_summary(st)
        return JSONResponse(out, headers=NO_CACHE)

    @app.post("/api/runs/{rid}/decision")
    def decision(rid: str, body: dict = Body(...)):
        run_dir(rid)
        problem = mgr.decide(rid, body.get("gate", ""), body.get("decision", ""), body.get("by", ""), body.get("comment", ""), body.get("values"))
        if isinstance(problem, dict):
            return JSONResponse({"errors": problem}, status_code=422)
        if problem:
            return JSONResponse({"problem": problem}, status_code=409)
        return {"ok": True}

    @app.delete("/api/runs/{rid}")
    def delete(rid: str):
        """Move the course to runs/_deleted/ (nothing is erased), take a published design out of Neo4j, end a running step."""
        run_dir(rid)
        dmgr.cancel(rid)
        return mgr.delete(rid)

    @app.post("/api/runs/{rid}/retry")
    def retry(rid: str):
        run_dir(rid)
        problem = mgr.retry(rid)
        if problem:
            return JSONResponse({"problem": problem}, status_code=409)
        return {"ok": True}

    @app.get("/api/runs/{rid}/form")
    def form(rid: str):
        d = run_dir(rid)
        spec = yaml.safe_load((d / "input.yaml").read_text(encoding="utf-8"))
        return {k: v for k, v in (spec.get("app_form_original") or spec.get("app_form") or {}).items() if k != "consent"}

    @app.get("/api/runs/{rid}/proposal")
    def proposal(rid: str):
        d = run_dir(rid)
        if not (d / "proposal.md").exists():
            raise HTTPException(404, "The proposal isn't written yet")
        return {"html": views.proposal_html(d)}

    @app.get("/api/runs/{rid}/download/{kind}")
    def download(rid: str, kind: str):
        d = run_dir(rid)
        title = re.sub(r"[^A-Za-z0-9]+", "_", read_meta(d).get("title") or rid).strip("_")
        if kind == "pdf":
            if not (d / "state.json").exists() or not (d / "proposal.md").exists():
                raise HTTPException(404, "The course sheet isn't ready yet")
            pdf = d / "course_sheet.pdf"
            if not pdf.exists() or pdf.stat().st_mtime < (d / "state.json").stat().st_mtime:
                _export_pdf(d)
            return FileResponse(pdf, filename=f"{title}_course_sheet.pdf", media_type="application/pdf", headers=NO_CACHE)
        files = {"xlsx": ("course_template.xlsx", f"{title}_IIITD_template.xlsx"), "md": ("proposal.md", f"{title}_proposal.md")}
        if kind not in files or not (d / files[kind][0]).exists():
            raise HTTPException(404, "Not available")
        return FileResponse(d / files[kind][0], filename=files[kind][1], headers=NO_CACHE)

    @app.get("/api/runs/{rid}/feedback")
    def get_feedback(rid: str):
        p = run_dir(rid) / "design_feedback.yaml"
        if not p.exists():
            return {"entries": []}
        return yaml.safe_load(p.read_text(encoding="utf-8")) or {"entries": []}

    @app.post("/api/runs/{rid}/feedback")
    def post_feedback(rid: str, body: dict = Body(...)):
        d = run_dir(rid)
        ratings = {}
        for k in ("outcomes", "weeks", "assessment", "books", "overall"):
            v = (body.get("ratings") or {}).get(k)
            if v is not None:
                if not isinstance(v, int) or not 1 <= v <= 5:
                    return JSONResponse({"problem": "Ratings go from 1 to 5"}, status_code=422)
                ratings[k] = v
        if not ratings and not str(body.get("change") or "").strip():
            return JSONResponse({"problem": "Give at least one rating or comment"}, status_code=422)
        p = d / "design_feedback.yaml"
        data = (yaml.safe_load(p.read_text(encoding="utf-8")) if p.exists() else None) or {"run_id": rid, "entries": []}
        data["entries"].append({"at": time.strftime("%Y-%m-%d %H:%M:%S"), "by": str(body.get("by") or "").strip(), "ratings": ratings,
                                "change": str(body.get("change") or "").strip(), "time_saved": str(body.get("time_saved") or "")})
        p.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return {"ok": True, "entries": len(data["entries"])}

    # ================================================================ Phase 2: lecture delivery (guide §5)
    def course_dir(rid: str) -> Path:
        d = run_dir(rid)
        if not dv.approved(d):
            raise HTTPException(409, "Lecture delivery opens once the course design is approved")
        return d

    def lecture_id(lid: str) -> str:
        if not LID.match(lid):
            raise HTTPException(404, "No such lecture")
        return lid

    def nocache(obj):
        return JSONResponse(obj, headers=NO_CACHE)

    @app.get("/api/delivery")
    def delivery_courses():
        return nocache({"courses": dv.courses(mgr.runs), "example_available": (mgr.runs / dv.EXAMPLE_SOURCE / "state.json").exists()})

    @app.post("/api/delivery/example")
    def delivery_example():
        """A private copy of the CS-601 example run (Vihan's real results for three lectures); his files stay untouched."""
        return {"run_id": dv.copy_example(mgr.runs)}

    @app.get("/api/delivery/{rid}")
    def delivery_view(rid: str):
        course_dir(rid)
        return nocache(dv.view(rid, mgr.runs))

    @app.put("/api/delivery/{rid}/survey/{lid}")
    def delivery_save(rid: str, lid: str, answers: dict = Body(...)):
        course_dir(rid)
        out = dv.save_choices(rid, lecture_id(lid), answers)
        if out.get("errors"):
            return JSONResponse(out, status_code=422)
        if out.get("start_c"):
            dmgr.queue_recommend(rid, [lid], refresh=out["refresh"])
        return out

    @app.post("/api/delivery/{rid}/start")
    def delivery_start(rid: str, body: dict = Body(...)):
        """(Re)start C's search for lectures whose saved choices ask for resources or a guest (Try again, bulk-filled lectures)."""
        course_dir(rid)
        v = dv.view(rid, mgr.runs)
        want = [lid for lid in body.get("lectures") or [] if LID.match(lid) and (v["survey"].get(lid) or {}) and
                ((v["survey"][lid].get("assistance") == "yes") or (v["survey"][lid].get("guest_lecture") == "yes"))]
        if want:
            dmgr.queue_recommend(rid, want, refresh=bool(body.get("refresh")))
        return {"started": want}

    @app.post("/api/delivery/{rid}/bulk")
    def delivery_bulk(rid: str, body: dict = Body(...)):
        course_dir(rid)
        out = dv.bulk(rid, lecture_id(body.get("lid", "")), "module" if body.get("scope") == "module" else "week")
        return JSONResponse(out, status_code=409) if out.get("problem") else out

    @app.get("/api/delivery/{rid}/previous/{lid}")
    def delivery_previous(rid: str, lid: str):
        course_dir(rid)
        out = dv.same_as_previous(rid, lecture_id(lid))
        return JSONResponse(out, status_code=409) if out.get("problem") else out

    @app.post("/api/delivery/{rid}/attachments/{lid}")
    async def delivery_attach(rid: str, lid: str, files: list[UploadFile] = File(...)):
        """Files for the material team (B): stored under runs/<id>/delivery/attachments/<lecture>/ (guide question c)."""
        course_dir(rid)
        lecture_id(lid)
        saved = []
        for f in files[:10]:
            data = await f.read()
            if len(data) > 50 * 1024 * 1024:
                raise HTTPException(413, f"{f.filename} is larger than 50 MB")
            saved.append(dv.save_attachment(rid, lid, f.filename or "file", data))
        return {"saved": saved}

    @app.post("/api/delivery/{rid}/review")
    def delivery_review(rid: str, body: dict = Body(...)):
        course_dir(rid)
        out = dv.review(rid, lecture_id(body.get("lid", "")), str(body.get("kind", "")), str(body.get("key", "")),
                        str(body.get("decision", "")), str(body.get("reason") or ""), str(body.get("title") or ""))
        return JSONResponse(out, status_code=409) if out.get("problem") else out

    @app.post("/api/delivery/{rid}/undo")
    def delivery_undo(rid: str, body: dict = Body(...)):
        course_dir(rid)
        return dv.undo_approve(rid, lecture_id(body.get("lid", "")), str(body.get("kind", "")), str(body.get("key", "")))

    @app.post("/api/delivery/{rid}/own")
    def delivery_own(rid: str, body: dict = Body(...)):
        course_dir(rid)
        out = dv.own_link(rid, lecture_id(body.get("lid", "")), str(body.get("title") or ""), str(body.get("url") or ""),
                          str(body.get("kind") or "reading"), body.get("remove"))
        return JSONResponse(out, status_code=422) if out.get("problem") else out

    @app.post("/api/delivery/{rid}/rate")
    def delivery_rate(rid: str, body: dict = Body(...)):
        course_dir(rid)
        out = dv.rate(rid, lecture_id(body.get("lid", "")), str(body.get("key", "")), str(body.get("title") or ""),
                      body.get("rating"), str(body.get("comment") or ""))
        return JSONResponse(out, status_code=422) if out.get("problem") else out

    @app.post("/api/delivery/{rid}/health")
    def delivery_health(rid: str):
        course_dir(rid)
        dmgr.queue_health(rid)
        return {"queued": True}

    @app.post("/api/delivery/{rid}/health/dismiss")
    def delivery_dismiss(rid: str, body: dict = Body(...)):
        course_dir(rid)
        dv.dismiss_dead(rid, str(body.get("url") or ""))
        return {"ok": True}

    @app.get("/api/delivery/{rid}/kit/{lid}")
    def delivery_kit(rid: str, lid: str):
        d = course_dir(rid)
        p = d / "delivery" / "guest_kits" / f"{lecture_id(lid)}.md"
        if not p.exists():
            raise HTTPException(404, "No guest-lecture kit for this lecture yet")
        return {"md": p.read_text(encoding="utf-8")}

    @app.get("/api/delivery/{rid}/report")
    def delivery_report(rid: str):
        import markdown
        d = course_dir(rid)
        p = d / "delivery" / "report.md"
        if not p.exists():
            raise HTTPException(404, "No report yet")
        return {"html": markdown.markdown(p.read_text(encoding="utf-8"), extensions=["sane_lists"])}

    return app

