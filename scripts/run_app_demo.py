"""ProfsAgent in demo mode: the real app (server, screens, edits, checks, lecture delivery) with recorded design runs
replayed in place of the AI pipeline. For UI work and demos on a machine with no AI keys and no Neo4j.

  python scripts/run_app_demo.py                 # http://127.0.0.1:8000
  python scripts/run_app_demo.py --reset         # remove the demo courses and seed them again
  python scripts/run_app_demo.py --speed 0.3     # seconds per replayed stage (default 1.5)

What is real: every screen's data (app/views.py), every edit and its re-check (app/edits.py, validate/), approvals with
reasons and overrides (validate/engine.resolve_gate), downloads, and lecture delivery over the recorded results.
What is replayed: the design stages (their output is copied from a finished run under runs/) and the "fill in the blanks"
step. No AI is called, so searches and slide generation started here stop with the app's own "no AI key" messages.

Demo courses are runs/app-demo-* (git-ignored like every app course); they carry "demo": true in app.json.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import sys
import threading
import time
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(ROOT / "src"))
os.environ.setdefault("KG_BACKEND", "stub")          # the 17-course sample graph: no Neo4j needed

import uvicorn  # noqa: E402
import yaml  # noqa: E402

import profsagent.config  # noqa: E402,F401
from profsagent.app import delivery as dv  # noqa: E402
from profsagent.app import edits, formmap, views  # noqa: E402
from profsagent.app.runner import RunManager, read_meta, user_name, write_meta  # noqa: E402
from profsagent.app.server import create_app  # noqa: E402
from profsagent.config import RUNS  # noqa: E402
from profsagent.validate import engine  # noqa: E402

DEFAULT_SOURCE = "cs601-02"
# what each part of the pipeline adds to state.json, in order (the gate that follows it, its stages, its keys)
PARTS = [
    ("gate1_context", ["s1_intake", "s2_positioning", "s3_constraints"], None, ["intake", "positioning", "constraints"]),
    ("gate2_outcomes", ["s4_outcomes"], ["cos", "topic_group_proposals", "copo", "los"], ["cos", "copo", "los"]),
    ("gate3_proposal", ["s5_structure", "s7_activities_assessment", "s8_resources", "s9_narrative"],
     ["modules", "structure_meta", "schedule", "labs_tutorials", "assessment_adjustments", "assessment", "copo_computed", "co_marks_share",
      "resources", "resources_rejected", "resource_policy", "narrative"], ["structure", "labs", "assessment", "resources", "narrative"]),
]
LATER = [k for _, _, keys, _ in PARTS[1:] for k in keys]
DOCS = ["proposal.md", "proposal.csv", "course_template.xlsx", "course_sheet.pdf", "evaluation_deterministic.json", "course_code.txt"]
STAGE_LOG = dict(views.STEPS)
SPEED = 1.5

# the blanks of the example form ("Fill with an example"), as the recorded CS-601 run had them
FILL = {
    "topics": "A. AI-native development: AI-assisted coding, coding agents, context engineering\nB. Engineering practice: automated testing, "
              "code review, deployment\nC. Working with agents: task decomposition, tool use, evaluation of agent output\n"
              "D. Responsible use: security, licensing, limits of AI-generated code",
    "intent_question": "How do people and coding agents build reliable software together?",
    "intent_emphasis": "Learning by building; design and review before generation",
    "intent_avoid": "A prompt-engineering tips course\nA machine learning theory course",
    "department": "CSE", "credits": "4", "l": "3", "t": "0", "p": "2", "weeks": "13", "weekly_effort": "10-12",
    "programmes": ["B.Tech CSE", "B.Tech CSAI", "M.Tech CSE"], "year": "Postgraduate", "background": "CSE201 Advanced Programming",
    "lab": "weekly", "lab_infra": "Students' laptops; access to a coding agent; TA support",
    "assess_pref": ["Project", "Assignments", "Quizzes"], "assess_avoid": [], "assess_why": "Most of the grade should come from building software",
    "special": "",
}
WHY = {"credits": "IIIT-D courses are 1, 2 or 4 credits; a course with a weekly lab and a project is 4.",
       "weeks": "A semester has 13 teaching weeks.", "l": "3 lecture hours a week for a 4-credit course.",
       "weekly_effort": "The course template asks for 10–12 hours a week outside lectures for 4 credits."}


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _save(d: Path, st: dict) -> None:
    tmp = d / "state.json.tmp"
    tmp.write_text(json.dumps(st, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
    os.replace(tmp, d / "state.json")


def _log(d: Path, msg: str) -> None:
    with (d / "run.log").open("a", encoding="utf-8") as f:
        f.write(f"{time.strftime('%H:%M:%S')} {msg}\n")


def _source(d: Path) -> Path:
    return RUNS / (read_meta(d).get("demo_source") or DEFAULT_SOURCE)


def context_state(src: dict) -> dict:
    """The recorded state as it stood before the first check: no outcomes, plan or approvals yet."""
    st = {k: copy.deepcopy(v) for k, v in src.items() if k not in LATER and k not in ("approvals", "neo4j_load", "professor_edits")}
    st["approvals"], st["stages_done"] = [], []
    st["violations"] = {k: v for k, v in (src.get("violations") or {}).items() if k in PARTS[0][3]}
    return st


class ReplayFiller:
    def fill(self, run_dir: Path) -> dict:
        time.sleep(SPEED * 2)
        form = yaml.safe_load((run_dir / "input.yaml").read_text(encoding="utf-8"))["app_form"]
        ref = views.course_ref("CSE201")
        src = [{"text": "CSE201 Advanced Programming", "url": ref["url"]}] if ref["name"] else []
        fields = {k: {"value": v, "reason": WHY.get(k, "Recorded value from the CS-601 example run (demo mode: no AI was called)."),
                      "sources": src if k in ("topics", "background", "year") else [], "corrected": None}
                  for k, v in FILL.items() if formmap.blank(form, k) and v}
        (run_dir / "fill.json").write_text(json.dumps({"fields": fields, "unfilled": [k for k in ("special",) if formmap.blank(form, k)],
                                                      "similar": [ref] if ref["name"] else [], "given": []}, ensure_ascii=False), encoding="utf-8")
        return {"status": "waiting", "gate": "gate0_details", "payload": {"gate": "gate0_details", "filled": len(fields)}}


class ReplayDriver:
    """start / resume / continue, worked out from the run's own state.json: record the decision for the check that is
    waiting, then replay the stages up to the next check (or publish)."""

    def step(self, rid: str, kind: str, payload: dict | None = None) -> dict:
        d = RUNS / rid
        src_dir = _source(d)
        src = _load(src_dir / "state.json")
        st = _load(d / "state.json") if (d / "state.json").exists() else None
        if st is None:
            st = context_state(src)
            _save(d, st)
        done = {a["gate"] for a in st["approvals"]}
        waiting = next((g for g, _, _, _ in PARTS if g not in done and self._has(st, g)), None)
        if kind == "resume" and payload and waiting:
            decision, problem = engine.resolve_gate(engine.gate_view(st), payload, auto=False)
            if problem:
                return {"status": "waiting", "gate": waiting, "payload": {"gate": waiting, **edits.gate_payload(st), "problem": problem}}
            st["approvals"].append({"gate": waiting, **decision, "at": time.time(), "frozen": 0, "open_errors": len(engine.errors(engine.recorded(st)))})
            _log(d, f"GATE {waiting}: {decision.get('decision')} by {decision.get('by')}")
            _save(d, st)
            if decision.get("decision") != "approve":
                return {"status": "stopped", "gate": waiting}
            done.add(waiting)
        for gate, stages, keys, vkeys in PARTS:
            if gate in done:
                continue
            for s in stages:
                if s in st["stages_done"]:
                    continue
                _log(d, f"{s}: {STAGE_LOG.get(s, s).lower()} (replayed from runs/{src_dir.name})")
                time.sleep(SPEED)
                st["stages_done"].append(s)
                _save(d, st)
            for k in keys or []:
                if k not in st and k in src:
                    st[k] = copy.deepcopy(src[k])
            for k in vkeys:
                st.setdefault("violations", {}).setdefault(k, copy.deepcopy((src.get("violations") or {}).get(k, [])))
            _save(d, st)
            if gate == "gate3_proposal":
                self._documents(d, src_dir, st)
            _log(d, f"waiting at {gate}")
            return {"status": "waiting", "gate": gate, "payload": {"gate": gate, **edits.gate_payload(st)}}
        st["neo4j_load"] = {"skipped": "demo mode"}
        _save(d, st)
        _log(d, "publish: skipped (demo mode)")
        return {"status": "done"}

    @staticmethod
    def _has(st: dict, gate: str) -> bool:
        stages = next(s for g, s, _, _ in PARTS if g == gate)
        return all(s in st.get("stages_done", []) for s in stages)

    @staticmethod
    def _documents(d: Path, src_dir: Path, st: dict) -> None:
        time.sleep(SPEED)
        problem = edits._rerender(d, st)          # the real renderer on this run's state (proposal, Excel template, tier-1 evaluation)
        if problem or not (d / "proposal.md").exists():
            for name in DOCS:
                if (src_dir / name).exists() and not (d / name).exists():
                    shutil.copy2(src_dir / name, d / name)
        _save(d, st)
        _log(d, "render: course sheet written")


# ------------------------------------------------------------------ seeding
def _meta(rid: str, title: str, status: str, **kw) -> dict:
    now = time.time()
    return {"run_id": rid, "title": title, "by": user_name(), "created_at": kw.pop("age_h", 1) * -3600 + now, "status": status, "phase": "design",
            "demo": True, "pending": None, "history": [{"at": now, "event": "seeded for the demo"}], **kw}


def _seed_at(rid: str, source: str, gate: str | None, status: str = "waiting", age_h: float = 1, **kw) -> None:
    """A course whose replay has reached `gate` (None: before the first check), from a finished run under runs/."""
    d = RUNS / rid
    d.mkdir(parents=True)
    src_dir = RUNS / source
    src = _load(src_dir / "state.json")
    st = context_state(src)
    by = user_name()
    reached = False
    for g, stages, keys, vkeys in PARTS:
        if gate is None:
            break
        st["stages_done"] += stages
        for k in keys or []:
            if k in src:
                st[k] = copy.deepcopy(src[k])
        for k in vkeys:
            st["violations"].setdefault(k, copy.deepcopy((src.get("violations") or {}).get(k, [])))
        if g == gate:
            reached = True
            break
        st["approvals"].append({"gate": g, "decision": "approve", "by": by, "comment": "", "at": time.time() - 1800, "frozen": 0, "open_errors": 0})
    (d / "input.yaml").write_text(yaml.safe_dump({"run": src.get("run_cfg") or {}, "form": src.get("form") or {}, "app_form": {}}, allow_unicode=True), encoding="utf-8")
    (d / "details_review.json").write_text(json.dumps({"gate": "gate0_details", "decision": "approve", "by": by, "comment": "", "at": time.time() - 3000,
                                                       "suggested_by_profsagent": ["credits", "weeks", "topics"], "changed_by_professor": ["topics"]}), encoding="utf-8")
    (d / "fill.json").write_text(json.dumps({"fields": {}, "unfilled": [], "similar": [], "given": []}), encoding="utf-8")
    _save(d, st)
    _log(d, f"seeded from runs/{source}")
    title = (st.get("cco_compact") or {}).get("course_name") or source
    meta = _meta(rid, title, status, demo_source=source, age_h=age_h, gate=gate if reached else None, **kw)
    if status == "waiting" and reached:
        if gate == "gate3_proposal":
            ReplayDriver._documents(d, src_dir, st)
        meta["payload"] = {"gate": gate, **edits.gate_payload(st)}
    write_meta(d, meta)


def seed(rich: Path | None) -> None:
    by = user_name()
    # 1. approved, with lecture delivery (the richest recorded delivery run that is on this machine)
    src = rich or next((RUNS / r for r in ("cs601-c3", DEFAULT_SOURCE) if (RUNS / r / "delivery" / "lectures").exists()), None)
    if src is not None:
        rid = "app-demo-software-development-using-ai-01"
        shutil.copytree(src, RUNS / rid, ignore=shutil.ignore_patterns("checkpoint.sqlite*", "*.tmp", "*.out", "llm_calls.jsonl", "preview"))
        for name in DOCS + ["design_graph.json", "run.log"]:              # a delivery-only run folder has no course sheet: take the design's
            if not (RUNS / rid / name).exists() and (RUNS / DEFAULT_SOURCE / name).exists():
                shutil.copy2(RUNS / DEFAULT_SOURCE / name, RUNS / rid / name)
        mat = RUNS / DEFAULT_SOURCE / "delivery" / "material"          # generated slides, when the delivery run has none of its own
        if mat.exists() and not (RUNS / rid / "delivery" / "material").exists():
            shutil.copytree(mat, RUNS / rid / "delivery" / "material", ignore=lambda d, names: [n for n in names if d == str(mat) and ".S" in n])
        st = _load(RUNS / rid / "state.json")
        for a in st.get("approvals", []):
            a.update(by=by, comment="" if "auto" in str(a.get("comment")) else a.get("comment"))
        _save(RUNS / rid, st)
        (RUNS / rid / "details_review.json").write_text(json.dumps({"gate": "gate0_details", "decision": "approve", "by": by, "comment": "", "at": time.time() - 90000,
                                                                    "suggested_by_profsagent": sorted(FILL), "changed_by_professor": ["topics", "assess_pref"]}), encoding="utf-8")
        write_meta(RUNS / rid, _meta(rid, (st.get("cco_compact") or {}).get("course_name", "CS-601"), "done", gate="gate3_proposal", demo_source=DEFAULT_SOURCE,
                                     example_of=src.name, age_h=26))
    # 2–4. waiting at each check
    _seed_at("app-demo-web-development-for-all-01", "dept-webdev-title-01", "gate3_proposal", age_h=5)
    _seed_at("app-demo-advanced-programming-01", "cse201-dev-06", "gate2_outcomes", age_h=3)
    _seed_at("app-demo-software-development-using-ai-02", "cs601-kg-02", "gate1_context", age_h=2)
    # 5. stopped by the professor at the outcomes check
    _seed_at("app-demo-advanced-programming-02", "cse201-dev-04", "gate2_outcomes", status="stopped", age_h=50)
    d = RUNS / "app-demo-advanced-programming-02"
    st = _load(d / "state.json")
    st["approvals"].append({"gate": "gate2_outcomes", "decision": "reject", "by": by, "at": time.time() - 170000,
                            "comment": "The outcomes repeat CSE102; I will narrow the topics and start again."})
    _save(d, st)
    # 6. needs attention (an error the professor can retry) and 7. paused on the AI quota
    _seed_at("app-demo-advanced-programming-03", "cse201-dev-05", None, status="error", age_h=8,
             error={"message": "The course database (Neo4j) isn't running. Start it in Neo4j Desktop, then press Try again.",
                    "detail": "ServiceUnavailable: Couldn't connect to localhost:7687 (demo: press Try again to continue the replay)"})
    _seed_at("app-demo-web-development-for-all-02", "dept-webdev-title-01", "gate1_context", status="paused", age_h=0.4,
             resume_at=time.time() + 42 * 60, error={"message": "The free AI quota is used up for now.", "detail": "AllEndpointsFailed (demo)"})
    m = read_meta(RUNS / "app-demo-web-development-for-all-02")
    m["gate"] = None
    st = _load(RUNS / "app-demo-web-development-for-all-02" / "state.json")
    st["stages_done"] = st["stages_done"][:2]                 # stopped half-way through the context stages
    _save(RUNS / "app-demo-web-development-for-all-02", st)
    write_meta(RUNS / "app-demo-web-development-for-all-02", m)


def reset() -> None:
    for d in sorted(RUNS.glob("app-*")):
        try:
            if read_meta(d).get("demo"):
                shutil.rmtree(d)
        except Exception:  # noqa: BLE001, S112
            continue


def main() -> None:
    global SPEED
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--host", default=os.environ.get("APP_HOST", "127.0.0.1"))
    ap.add_argument("--port", type=int, default=int(os.environ.get("APP_PORT", "8000")))
    ap.add_argument("--reset", action="store_true", help="remove the demo courses and seed them again")
    ap.add_argument("--speed", type=float, default=SPEED, help="seconds per replayed stage")
    ap.add_argument("--rich", type=Path, default=None, help="a run folder with delivery results to use for the approved course")
    ap.add_argument("--no-browser", action="store_true")
    a = ap.parse_args()
    SPEED = a.speed
    if a.reset:
        reset()
    if not any(read_meta(d).get("demo") for d in RUNS.glob("app-*") if (d / "app.json").exists()):
        seed(a.rich)
    mgr = RunManager(driver=ReplayDriver(), filler=ReplayFiller(), tick_s=5.0, isolate=False)
    url = f"http://{'127.0.0.1' if a.host in ('0.0.0.0', '::') else a.host}:{a.port}"
    print(f"ProfsAgent (demo mode: recorded runs, no AI) is starting at {url}  (Ctrl+C to stop)")
    if not a.no_browser:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run(create_app(mgr, delivery=dv.DeliveryManager(runs=mgr.runs)), host=a.host, port=a.port, log_level="warning")


if __name__ == "__main__":
    main()
