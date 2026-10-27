"""The local professor app: form mapping, filling in blank fields, screen views on a real run, the run manager's
gate flow (details → context → outcomes → final) and quota pause, and the HTTP API. The pipeline and the AI are
replaced by fakes here (no AI calls, no Neo4j)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest  # noqa: E402
import yaml  # noqa: E402

from profsagent.app import formmap, views  # noqa: E402
from profsagent.app.filler import DetailsFiller, FillOut, Suggestion  # noqa: E402
from profsagent.app.runner import RunManager, read_meta  # noqa: E402
from profsagent.app.server import EXAMPLE, create_app  # noqa: E402
from profsagent.config import RUNS  # noqa: E402
from profsagent.llm.client import AllEndpointsFailed  # noqa: E402

REAL = RUNS / "cs601-02"   # a committed, finished design run

FULL = {"topics": "A. Agents: coding agents, tool use\nB. Testing: unit tests, evaluation", "intent_question": "How do humans and agents build software?",
        "intent_emphasis": "hands-on", "intent_avoid": "An ML course", "department": "CSE", "credits": "4", "l": "3", "t": "1", "p": "2",
        "weeks": "13", "weekly_effort": "10-12", "programmes": ["B.Tech CSE"], "year": "3rd / 4th year", "background": "CSE201",
        "lab": "weekly", "lab_infra": "laptops", "assess_pref": ["Project"], "assess_avoid": [], "assess_why": "practice", "special": ""}


def good_form(**kw):
    """What a professor submits: the example (name, description and a few fields; the rest blank)."""
    return {**EXAMPLE, "by": "Prof. Test", "consent": True, **kw}


# ------------------------------------------------------------------ form
def test_only_name_and_description_are_required():
    e = formmap.validate({})
    assert {"name", "description", "by", "consent"} == set(e)
    assert formmap.validate(good_form()) == {}
    assert "credits" in formmap.validate(good_form(credits="3"))                  # UGREG-2025§4(2): 1, 2 or 4
    assert formmap.validate(good_form(credits="2", l="1.5", t="0.5", p="0")) == {}  # 2 credits: 1.5 lecture hours
    assert "ltp" in formmap.validate(good_form(l="x"))


def test_the_design_needs_a_complete_form():
    e = formmap.validate_complete(good_form())
    assert {"topics", "credits", "ltp", "weeks", "programmes", "year", "lab"} <= set(e)
    assert formmap.validate_complete(good_form(**FULL)) == {}


def test_to_pipeline_fills_the_14_fields():
    form, cfg = formmap.to_pipeline(good_form(**FULL))
    assert list(form) == [k for k in form if k[0].isdigit()] and len(form) == 14
    assert form["7. CREDITS"] == "4" and form["8. L-T-P / CONTACT HOURS"].startswith("3-1-2")
    assert form["10. WEEKLY STUDENT EFFORT"].startswith("11 hours")                # one number: the middle of 10-12
    assert form["3. TOPICS / CONTENT AREAS"].splitlines()[1].startswith("A. ")
    assert cfg["department"] == "CSE" and cfg["external_research"] is True and cfg["exclude_courses"] == []
    form, _ = formmap.to_pipeline(good_form())                                       # blanks reach the pipeline as [NOT SPECIFIED]
    assert form["3. TOPICS / CONTENT AREAS"].startswith("[NOT SPECIFIED") and form["7. CREDITS"] == "[NOT SPECIFIED]"


# ------------------------------------------------------------------ filling in the blanks: code checks on the AI's suggestions
SIMILAR = [{"code": "CSE594A", "name": "Agentic Reasoning", "credits": 4, "url": "https://techtree.iiitd.edu.in/x"}]


def test_check_keeps_only_valid_grounded_suggestions():
    form = good_form()                                                   # department CSE and background given by the professor
    blanks = [k for k in formmap.FILLABLE if formmap.blank(form, k)]
    raw = {
        "topics": Suggestion(value=["A. Agents: tool use", "B. Testing: evaluation"], reason="From the description", sources=["description", "CSE594A", "CSE999"]),
        "credits": Suggestion(value="4", reason="Most similar courses are 4 credits", sources=["CSE594A"]),
        "l": Suggestion(value="2", reason="r", sources=[]), "t": Suggestion(value="1", reason="r"), "p": Suggestion(value="0", reason="r"),
        "weeks": Suggestion(value="14", reason="r"), "lab": Suggestion(value="yes", reason="hands-on"),
        "year": Suggestion(value="Final year", reason="not an allowed value"),
        "programmes": Suggestion(value=["B.Tech CSE", "B.Tech Nonsense"], reason="r"),
        "weekly_effort": Suggestion(value="20", reason="r"),
        "department": Suggestion(value="ECE", reason="the professor already gave CSE"),
    }
    f = DetailsFiller.check(raw, form, blanks, SIMILAR)
    assert "department" not in f and "year" not in f                                 # given by the professor / not allowed
    assert [s["text"] for s in f["topics"]["sources"]] == ["Your description", "CSE594A Agentic Reasoning"]   # CSE999 was never shown
    assert f["programmes"]["value"] == ["B.Tech CSE"]
    assert f["lab"]["value"] == "weekly"
    assert f["l"]["value"] == "3" and "UG Regulations 2025 §4(2)a" in f["l"]["corrected"]       # 4 credits = 3 lecture hours
    assert f["weeks"]["value"] == "13" and f["weeks"]["corrected"]                                # UGREG-2025§2
    assert f["p"]["value"] == "2"                                                                 # weekly lab, not 0 hours
    assert f["weekly_effort"]["value"] == "10-12"                                                 # template: 2.5–3 h per credit


class FakeKG:
    def search_courses(self, text, k=15, exclude=frozenset()):
        return [{"uid": "CSE594A", "score": 1.0, "hits": []}]

    def course(self, uid, exclude=frozenset()):
        return {"uid": uid, "name": "Agentic Reasoning", "credits": 4, "level": 5, "description": "Agents", "topics": ["agents"],
                "prereq_text": None, "assessment": [{"type": "project", "weight_pct": 40}], "catalogue_url": None}


class FakeLLM:
    def __init__(self):
        self.calls = []

    def structured(self, **kw):
        self.calls.append(kw)
        blanks = json.loads(kw["user"])["fields_to_fill"]
        vals = {"topics": "A. Agents: tool use", "credits": "4", "l": "3", "t": "1", "p": "2", "weeks": "13", "programmes": ["B.Tech CSE"],
                "year": "3rd / 4th year", "lab": "weekly", "assess_pref": ["Project"], "assess_avoid": []}
        return FillOut(fields={k: Suggestion(value=vals.get(k, f"{k} text"), reason=f"why {k}", sources=["description"]) for k in blanks}), \
            type("Rec", (), {"endpoint": "fake"})()


def test_fill_writes_suggestions_for_the_blanks_only(tmp_path):
    (tmp_path / "input.yaml").write_text(yaml.safe_dump({"app_form": good_form()}), encoding="utf-8")
    llm = FakeLLM()
    out = DetailsFiller(kg=FakeKG(), llm=llm).fill(tmp_path)
    assert out["status"] == "waiting" and out["gate"] == "gate0_details"
    fill = json.loads((tmp_path / "fill.json").read_text(encoding="utf-8"))
    asked = json.loads(llm.calls[0]["user"])
    assert "department" not in asked["fields_to_fill"] and "topics" in asked["fields_to_fill"]     # the professor gave CSE
    assert asked["similar_iiitd_courses"][0]["code"] == "CSE594A" and asked["regulation_facts"]
    assert set(fill["fields"]) == set(asked["fields_to_fill"]) and fill["unfilled"] == []
    merged = views.details(tmp_path)["form"]
    assert formmap.validate_complete(merged) == {}


# ------------------------------------------------------------------ views on a real run
@pytest.mark.skipif(not (REAL / "state.json").exists(), reason="needs runs/cs601-02")
def test_views_build_from_a_real_run():
    st = views.state_of(REAL)
    g1 = views.gate1(st)
    assert any(p["code"] == "CSE201" and p["name"] == "Advanced Programming" and p["url"] for p in g1["prerequisites"])
    assert all(o["pct"] > 0 for o in g1["overlaps"])
    assert g1["assumptions"] and all(a["basis"] for a in g1["assumptions"])
    assert any(r["ref"] and r["ref"].startswith("UGREG") for r in g1["rules"])
    assert g1["topics"] and g1["topics"][0]["topics"]
    g2 = views.gate2(st)
    assert len(g2["cos"]) == 4 and all(c["los"] and c["pos"] for c in g2["cos"])
    assert g2["no_topics_given"] is False and isinstance(g2["proposals"], list)
    g3 = views.gate3(st, REAL)
    assert len(g3["weeks"]) == 13 and g3["assessment_total"] == 100
    assert any(b["link"] and b["link"].startswith("https://doi.org/") for b in g3["books"])
    p = views.progress(REAL, st)
    assert p["ai_calls"] > 0 and next(s for s in p["steps"] if s["id"] == "s1_intake")["done"]
    assert "<table>" in views.proposal_html(REAL)


# ------------------------------------------------------------------ run manager with a fake filler and pipeline
class FakeFiller:
    """Fills every blank field with a valid value; fail_next raises once."""
    def __init__(self):
        self.fail_next = None

    def fill(self, run_dir):
        if self.fail_next:
            e, self.fail_next = self.fail_next, None
            raise e
        form = yaml.safe_load((run_dir / "input.yaml").read_text(encoding="utf-8"))["app_form"]
        fields = {k: {"value": v, "reason": "fake", "sources": [], "corrected": None} for k, v in FULL.items() if formmap.blank(form, k) and v}
        (run_dir / "fill.json").write_text(json.dumps({"fields": fields, "unfilled": [], "similar": [], "given": []}), encoding="utf-8")
        return {"status": "waiting", "gate": "gate0_details", "payload": {"gate": "gate0_details", "filled": len(fields)}}


class FakeDriver:
    """start → gate1; resume walks gate1 → gate2 → gate3 → done; 'reject' stops; fail_next raises once."""
    def __init__(self):
        self.calls, self.fail_next = [], None

    def step(self, rid, kind, payload=None):
        self.calls.append((rid, kind, payload))
        if self.fail_next:
            e, self.fail_next = self.fail_next, None
            raise e
        n = sum(1 for c in self.calls if c[0] == rid and c[1] == "resume" and c[2]["decision"] == "approve")
        if payload and payload.get("decision") == "reject":
            return {"status": "stopped", "gate": ["gate1_context", "gate2_outcomes", "gate3_proposal"][n]}
        if kind == "resume" and n == 3:
            return {"status": "done"}
        gate = ["gate1_context", "gate2_outcomes", "gate3_proposal"][n]
        return {"status": "waiting", "gate": gate, "payload": {"gate": gate, "blocked": gate == "gate2_outcomes", "open_errors": 1, "open": []}}


def wait_for(mgr, rid, status, timeout=10):
    t0 = time.time()
    while time.time() - t0 < timeout:
        m = read_meta(mgr.runs / rid)
        if m.get("status") == status and mgr.q.empty() and mgr.current is None:
            return m
        time.sleep(0.05)
    raise AssertionError(f"{rid} never reached {status}: {read_meta(mgr.runs / rid)}")


def confirm_details(mgr, rid, **edits):
    """The professor checks the completed form (gate0_details) and confirms it, possibly with edits."""
    m = wait_for(mgr, rid, "waiting")
    assert m["gate"] == "gate0_details"
    values = {**views.details(mgr.runs / rid)["form"], **edits}
    assert mgr.decide(rid, "gate0_details", "approve", "P", "", values) is None


@pytest.fixture
def mgr(tmp_path):
    m = RunManager(runs=tmp_path, driver=FakeDriver(), filler=FakeFiller(), tick_s=0.1)
    m.start()
    yield m
    m.stop()


def test_details_are_filled_and_checked_before_any_design(mgr):
    rid, errs = mgr.create(good_form())
    assert not errs and rid.startswith("app-software-development-using-ai-")
    m = wait_for(mgr, rid, "waiting")
    assert m["gate"] == "gate0_details" and m["phase"] == "details" and m["consent"]["given"]
    assert mgr.driver.calls == []                                                    # nothing designed yet
    d = mgr.runs / rid
    gaps = mgr.decide(rid, "gate0_details", "approve", "P", "", {**views.details(d)["form"], "topics": "", "credits": ""})
    assert isinstance(gaps, dict) and {"topics", "credits"} <= set(gaps)              # the professor emptied two: still missing
    assert mgr.decide(rid, "gate0_details", "approve", "P", "", {**views.details(d)["form"], "credits": "2", "l": "1.5", "t": "0.5", "p": "0"}) is None
    m = wait_for(mgr, rid, "waiting")
    assert m["gate"] == "gate1_context" and m["phase"] == "design" and mgr.driver.calls[0][1] == "start"
    spec = yaml.safe_load((d / "input.yaml").read_text(encoding="utf-8"))
    assert spec["form"]["7. CREDITS"] == "2" and not spec["form"]["3. TOPICS / CONTENT AREAS"].startswith("[NOT SPECIFIED")
    review = json.loads((d / "details_review.json").read_text(encoding="utf-8"))
    assert "topics" in review["accepted"] and {"credits", "l", "t", "p"} <= set(review["changed_by_professor"])
    assert views.approvals(None, d)[0]["gate"] == "gate0_details"


def test_gate_flow_with_reasons_and_overrides(mgr):
    rid, _ = mgr.create(good_form())
    confirm_details(mgr, rid)
    m = wait_for(mgr, rid, "waiting")
    assert m["gate"] == "gate1_context"
    assert mgr.decide(rid, "gate2_outcomes", "approve", "P", "") is not None          # not the waiting gate
    assert mgr.decide(rid, "gate1_context", "reject", "P", "") is not None            # stopping needs a reason
    assert mgr.decide(rid, "gate1_context", "approve", "P", "") is None
    m = wait_for(mgr, rid, "waiting")
    assert m["gate"] == "gate2_outcomes"
    assert mgr.decide(rid, "gate2_outcomes", "approve", "P", "") is not None           # blocked: needs a reason
    assert mgr.decide(rid, "gate2_outcomes", "approve", "P", "PO3 is covered by the project") is None
    m = wait_for(mgr, rid, "waiting")
    sent = mgr.driver.calls[-1][2]
    assert sent["reason"] == "PO3 is covered by the project" and sent["by"] == "P"
    assert mgr.decide(rid, "gate3_proposal", "approve", "P", "") is None
    m = wait_for(mgr, rid, "done")
    assert [h["event"] for h in m["history"]][-1] == "finished"


def test_stopping_at_the_details_step(mgr):
    rid, _ = mgr.create(good_form())
    wait_for(mgr, rid, "waiting")
    assert mgr.decide(rid, "gate0_details", "reject", "P", "") is not None            # needs a reason
    assert mgr.decide(rid, "gate0_details", "reject", "P", "Wrong course idea") is None
    m = wait_for(mgr, rid, "stopped")
    assert m["gate"] == "gate0_details" and mgr.driver.calls == []


def test_reject_stops_the_run(mgr):
    rid, _ = mgr.create(good_form())
    confirm_details(mgr, rid)
    wait_for(mgr, rid, "waiting")
    assert mgr.decide(rid, "gate1_context", "reject", "P", "Topics are wrong") is None
    m = wait_for(mgr, rid, "stopped")
    assert m["gate"] == "gate1_context"


def test_quota_exhaustion_pauses_then_continues(mgr, monkeypatch):
    import profsagent.app.runner as R
    monkeypatch.setattr(R, "quota_resume_at", lambda now=None: time.time() - 1)   # the quota is already back
    mgr.filler.fail_next = AllEndpointsFailed("all endpoints for role 'generate' unavailable")
    rid, _ = mgr.create(good_form())
    m = wait_for(mgr, rid, "paused")                                                # while filling in the details
    assert m["resume_at"] > time.time() and "quota" in m["error"]["message"]
    assert mgr.retry(rid) is None                                                   # "Try now" fills again
    confirm_details(mgr, rid)
    mgr.driver.fail_next = AllEndpointsFailed("all endpoints for role 'generate' unavailable")
    m = wait_for(mgr, rid, "paused")                                                # while designing
    assert mgr.retry(rid) is None
    m = wait_for(mgr, rid, "waiting")
    assert m["gate"] == "gate1_context" and mgr.driver.calls[-1][1] == "continue"


def test_other_errors_wait_for_try_again(mgr):
    rid, _ = mgr.create(good_form())
    mgr.driver.fail_next = RuntimeError("boom")
    confirm_details(mgr, rid)
    m = wait_for(mgr, rid, "error")
    assert "Try again" in m["error"]["message"] and (mgr.runs / rid / "app_error.log").exists()
    mgr.retry(rid)
    assert wait_for(mgr, rid, "waiting")["gate"] == "gate1_context"


def test_restart_continues_a_run_that_was_working(tmp_path):
    d = tmp_path / "app-x-01"
    d.mkdir()
    (d / "input.yaml").write_text(yaml.safe_dump({"app_form": good_form()}), encoding="utf-8")
    (d / "app.json").write_text(json.dumps({"run_id": "app-x-01", "status": "running", "phase": "details", "pending": {"kind": "fill"}, "history": []}))
    m = RunManager(runs=tmp_path, driver=FakeDriver(), filler=FakeFiller(), tick_s=0.1)
    m.start()
    try:
        assert wait_for(m, "app-x-01", "waiting")["gate"] == "gate0_details"
    finally:
        m.stop()


# ------------------------------------------------------------------ HTTP API
@pytest.fixture
def server(tmp_path):
    """The real app on a free local port (starlette's TestClient doesn't match the installed httpx)."""
    import socket
    import threading
    import httpx
    import uvicorn
    with socket.socket() as sk:
        sk.bind(("127.0.0.1", 0))
        port = sk.getsockname()[1]
    mgr = RunManager(runs=tmp_path, driver=FakeDriver(), filler=FakeFiller(), tick_s=0.1)
    srv = uvicorn.Server(uvicorn.Config(create_app(mgr), host="127.0.0.1", port=port, log_level="warning"))
    t = threading.Thread(target=srv.run, daemon=True)
    t.start()
    while not srv.started:
        time.sleep(0.05)
    with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=10) as c:
        yield c, mgr
    srv.should_exit = True
    t.join(5)


def test_api(server):
    c, mgr = server
    assert c.get("/").status_code == 200 and "ProfsAgent" in c.get("/").text
    assert c.get("/api/options").json()["example"]["name"]
    assert c.get("/api/catalogue?codes=cse201,XYZ999").json()[0]["name"] == "Advanced Programming"
    r = c.post("/api/runs", json={"name": ""})
    assert r.status_code == 422 and {"name", "description", "consent"} <= set(r.json()["errors"])
    rid = c.post("/api/runs", json=good_form()).json()["run_id"]
    wait_for(mgr, rid, "waiting")
    run = c.get(f"/api/runs/{rid}").json()
    assert run["gate"] == "gate0_details" and run["view"]["filled"]["topics"]["reason"] and run["progress"]["steps"][0]["done"]
    r = c.post(f"/api/runs/{rid}/decision", json={"gate": "gate0_details", "decision": "approve", "values": {**run["view"]["form"], "year": ""}})
    assert r.status_code == 422 and "year" in r.json()["errors"]
    assert c.post(f"/api/runs/{rid}/decision", json={"gate": "gate0_details", "decision": "approve", "values": run["view"]["form"]}).json()["ok"]
    wait_for(mgr, rid, "waiting")
    run = c.get(f"/api/runs/{rid}").json()
    assert run["status"] == "waiting" and run["gate"] == "gate1_context"
    assert c.post(f"/api/runs/{rid}/decision", json={"gate": "gate1_context", "decision": "reject"}).status_code == 409
    assert c.get("/api/runs/app-nope-01").status_code == 404
    assert c.get("/api/runs/..%2F..%2Fsecrets").status_code == 404
    assert c.get(f"/api/runs/{rid}/form").json()["topics"] == ""                     # "start again" refills what the professor typed
    assert c.post(f"/api/runs/{rid}/feedback", json={"ratings": {"overall": 9}}).status_code == 422
    assert c.post(f"/api/runs/{rid}/feedback", json={"ratings": {"overall": 4}, "change": "More labs", "by": "P"}).json()["entries"] == 1
    assert c.get(f"/api/runs/{rid}/feedback").json()["entries"][0]["ratings"] == {"overall": 4}
    assert c.get(f"/api/runs/{rid}/download/pdf").status_code == 404                  # no design yet
