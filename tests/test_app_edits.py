"""Professor edits at a waiting check (app/edits.py): applied to the run in place, checked again with the pipeline's own
deterministic checks, the design graph kept in step, and the check's open problems refreshed. Runs on a copy of the
committed run cs601-02, cut back to how it looked while it waited at each check. No AI calls, no Neo4j."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest  # noqa: E402

from profsagent.agents.pipeline import GATE_FREEZE  # noqa: E402
from profsagent.app import edits, views  # noqa: E402
from profsagent.app.runner import RunManager, read_meta, write_meta  # noqa: E402
from profsagent.app.server import create_app  # noqa: E402
from profsagent.config import RUNS, pedagogy  # noqa: E402
from profsagent.design.store import DesignGraph  # noqa: E402

REAL = RUNS / "cs601-02"
GATES = ["gate1_context", "gate2_outcomes", "gate3_proposal"]
LATER = {"gate1_context": ["cos", "copo", "los", "topic_group_proposals", "weight_priors", "modules", "schedule", "structure_meta", "kg_facts",
                           "labs_tutorials", "assessment", "assessment_adjustments", "copo_computed", "co_marks_share", "resources",
                           "resources_rejected", "resource_policy", "narrative"],
         "gate2_outcomes": ["modules", "schedule", "structure_meta", "kg_facts", "labs_tutorials", "assessment", "assessment_adjustments",
                            "copo_computed", "co_marks_share", "resources", "resources_rejected", "resource_policy", "narrative"],
         "gate3_proposal": []}
STAGES_BEFORE = {"gate1_context": ["intake", "positioning", "constraints"],
                 "gate2_outcomes": ["intake", "positioning", "constraints", "cos", "copo", "los"], "gate3_proposal": None}


class NoDriver:
    def step(self, *a, **k):
        raise AssertionError("no pipeline step should run in these tests")


def waiting_at(tmp_path: Path, gate: str) -> tuple[RunManager, str, Path]:
    """A copy of cs601-02 as it was while waiting at `gate`."""
    runs = tmp_path / "runs"
    d = runs / "app-edit-test-01"
    d.mkdir(parents=True)
    for f in ("state.json", "design_graph.json"):
        shutil.copy(REAL / f, d / f)
    st = json.loads((d / "state.json").read_text(encoding="utf-8"))
    i = GATES.index(gate)
    st["approvals"] = st["approvals"][:i]
    for k in LATER[gate]:
        st.pop(k, None)
    if STAGES_BEFORE[gate]:
        st["violations"] = {k: v for k, v in st["violations"].items() if k in STAGES_BEFORE[gate]}
    (d / "state.json").write_text(json.dumps(st, indent=1, ensure_ascii=False), encoding="utf-8")
    g = DesignGraph.load(d / "design_graph.json")
    g.set_status(list(g.nodes), "draft")
    for a in st["approvals"]:
        g.freeze_labels(GATE_FREEZE[a["gate"]])
    g.save()
    if gate == "gate3_proposal":
        shutil.copy(REAL / "proposal.md", d / "proposal.md")
    meta = {"run_id": d.name, "title": "Edit test", "by": "Professor", "created_at": 0, "status": "waiting", "gate": gate, "phase": "design",
            "payload": {"gate": gate, **edits.gate_payload(st)}, "history": []}
    write_meta(d, meta)
    return RunManager(runs=runs, driver=NoDriver(), filler=object(), isolate=False), d.name, d


def state(d: Path) -> dict:
    return json.loads((d / "state.json").read_text(encoding="utf-8"))


# ------------------------------------------------------------------ Context
def test_removing_one_of_two_conflicting_rules_clears_the_conflict(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate1_context")
    wishes = views.gate1(state(d))["edit"]["wishes"]
    out = mgr.edit(rid, "gate1_context", "wishes", wishes + [
        {"kind": "include", "text": "functional backend logic", "hard": True},
        {"kind": "exclude", "text": "static visual design without functional backend", "hard": True}])
    assert out["open_after"] > out["open_before"]                                  # the word-overlap check flags the pair
    m = read_meta(d)
    assert m["payload"]["blocked"] and any(x["code"] == "VK-CONFLICT" for x in m["payload"]["open"])
    st = state(d)
    new = [c for c in st["constraints"] if (c.get("source") or {}).get("ref") == "professor edit"]
    assert [c["target"] for c in new] == ["content.must_include[functional backend logic]",
                                          "content.must_exclude[static visual design without functional backend]"]
    wishes = views.gate1(st)["edit"]["wishes"]
    keep = [w for w in wishes if w["text"] != "functional backend logic"]           # the professor deletes the include rule
    out = mgr.edit(rid, "gate1_context", "wishes", keep)
    assert any("removed" in c for c in out["changes"])
    m = read_meta(d)
    assert not any(x["code"] == "VK-CONFLICT" for x in m["payload"]["open"])
    g = DesignGraph.load(d / "design_graph.json")
    assert {n["local_id"] for n in g.by_label("Constraint")} == {c["id"] for c in state(d)["constraints"]}
    assert [e["section"] for e in state(d)["professor_edits"]] == ["wishes", "wishes"]


def test_course_frame_rules_cannot_be_removed_or_loosened(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate1_context")
    st = state(d)
    for c in st["constraints"]:          # as on Web Development, where the professor gave weeks, credits and L-T-P in Details
        if c["id"] in ("K01", "K02", "K03"):
            c["source"] = {"tag": "USER", "ref": "CCO.credits"}
    (d / "state.json").write_text(json.dumps(st), encoding="utf-8")
    wishes = views.gate1(state(d))["edit"]["wishes"]
    frame = [w for w in wishes if w["locked"]]
    assert {k for w in frame for k in w["ids"]} >= {"K01", "K02", "K03"}   # K09 shares a row with the identical K17, which stays editable
    for w in frame:
        w["hard"] = False
    rest = [w for w in wishes if not w["locked"]]
    out = mgr.edit(rid, "gate1_context", "wishes", frame + rest[1:])   # one real wish removed, frame rules "loosened"
    after = {c["id"]: c for c in state(d)["constraints"]}
    assert all(k in after and after[k]["hardness"] == "hard" for k in ("K01", "K02", "K03"))
    removable = [k for k in rest[0]["ids"] if k != "K09"]              # the frame rule in a shared row stays
    assert len(out["changes"]) == 1 and out["changes"][0].startswith(f"Rule {removable[0]} removed") and "K09" in after
    out = mgr.edit(rid, "gate1_context", "wishes", rest[1:])            # leaving them out of the list doesn't delete them either
    assert {"K01", "K02", "K03", "K09"} <= {c["id"] for c in state(d)["constraints"]}


def test_rewording_a_rule_and_making_it_a_preference(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate1_context")
    wishes = views.gate1(state(d))["edit"]["wishes"]
    w = next(x for x in wishes if x["text_editable"])
    w.update(text="a theory-only course on large language models", hard=False)
    out = mgr.edit(rid, "gate1_context", "wishes", wishes)
    c = next(c for c in state(d)["constraints"] if c["id"] == w["ids"][0])
    assert c["target"].endswith("[a theory-only course on large language models]") and c["hardness"] == "soft"
    assert len(out["changes"]) == 2


def test_course_level_and_midsem_week_can_be_set(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate1_context")
    a = {x["what"]: x for x in views.gate1(state(d))["edit"]["assumptions"]}
    assert a["course level"]["editable"] and not a["credits"]["editable"]
    out = mgr.edit(rid, "gate1_context", "assumptions", [{"id": a["course level"]["id"], "value": 4},
                                                         {"id": a["mid-semester exam timing"]["id"], "value": "6"},
                                                         {"id": a["credits"]["id"], "confirm": True}])
    st = state(d)
    lo, hi = pedagogy()["bloom_bands"]["4"]
    assert st["level"] == 4 and st["bloom_band"]["floor"] == lo and st["bloom_band"]["ceiling"] == hi and st["cco_compact"]["level"] == 4
    assert st["midsem_after_week"] == 6 and next(c for c in st["constraints"] if c["target"] == "schedule.midsem_after_week")["value"] == 6
    status = {x["what"]: x["status"] for x in st["defaults"]["assumptions"]}
    assert status["course level"] == "set by professor" and status["credits"] == "confirmed"
    assert len(out["changes"]) == 3
    assert DesignGraph.load(d / "design_graph.json").props("COURSE")["level"] == 4
    bad = mgr.edit(rid, "gate1_context", "assumptions", [{"id": a["mid-semester exam timing"]["id"], "value": 40}])
    assert "errors" in bad and state(d)["midsem_after_week"] == 6                 # nothing saved


def test_topic_groups_edited_in_place(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate1_context")
    groups = views.gate1(state(d))["edit"]["topics"]
    groups[0]["title"] = "AI-native development (renamed)"
    groups[1]["topics"].append("Prompt injection and tool security")
    del groups[2]
    groups.append({"title": "Web security", "topics": ["OWASP top 10", "Secure APIs"]})
    out = mgr.edit(rid, "gate1_context", "topics", groups)
    st = state(d)
    assert [g["id"] for g in st["topic_groups"]] == ["TG1", "TG2", "TG4", "TG5", "TG6", "TG7"]
    assert st["cco_compact"]["topic_groups"] == st["topic_groups"]
    assert st["topic_groups"][1]["topics"][-1]["text"] == "Prompt injection and tool security"
    assert {n["local_id"] for n in DesignGraph.load(d / "design_graph.json").by_label("TopicGroup")} == {g["id"] for g in st["topic_groups"]}
    assert any("renamed" in c for c in out["changes"]) and any("removed the group" in c for c in out["changes"])
    assert views.gate1(st)["overlaps_before_topic_edit"] is True
    assert mgr.edit(rid, "gate1_context", "topics", [{"title": "", "topics": []}])["errors"]


def test_prerequisites_must_be_iiitd_courses(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate1_context")
    pre = views.gate1(state(d))["edit"]["prerequisites"]
    assert "0.code" in mgr.edit(rid, "gate1_context", "prerequisites", [{"code": "XYZ999", "kind": "mandatory"}])["errors"]
    out = mgr.edit(rid, "gate1_context", "prerequisites", pre + [{"code": "cse 102", "kind": "desirable"}])
    st = state(d)
    assert st["positioning"]["prerequisites"][-1]["course_uid"] == "CSE102" and out["changes"][0].startswith("Added recommended course CSE102")
    g = DesignGraph.load(d / "design_graph.json")
    assert "CSE102" in {e["dst"] for e in g.out("COURSE", "REQUIRES")}


def test_an_edit_needs_the_run_to_wait_at_that_check(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate1_context")
    assert "problem" in mgr.edit(rid, "gate2_outcomes", "co", {})
    assert "_" in mgr.edit(rid, "gate1_context", "nonsense", {})["errors"]
    m = read_meta(d)
    m["status"] = "running"
    write_meta(d, m)
    assert "problem" in mgr.edit(rid, "gate1_context", "topics", [])


# ------------------------------------------------------------------ Outcomes
def test_a_course_outcome_rewritten_with_its_learning_outcomes_and_po_links(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate2_outcomes")
    co = views.gate2(state(d))["edit"]["cos"]["CO1"]
    co["statement"] = "Design AI-assisted development workflows for small web applications, justifying each tool choice."
    co["bloom_level"] = 6
    dropped = co["los"].pop(0)["id"]
    co["los"].append({"statement": "Configure a coding agent with project rules and a test command.", "bloom_level": 3,
                      "condition": "given a starter repository", "degree": "so that the agent's changes pass the tests", "suggested_task_type": "lab_task"})
    co["pos"] = co["pos"][1:] + [{"po_uid": "BTECH-COMMON/PO11", "strength": 2}]
    out = mgr.edit(rid, "gate2_outcomes", "co", co)
    st = state(d)
    c1 = next(c for c in st["cos"] if c["id"] == "CO1")
    assert c1["verb"] == "design" and c1["bloom_level"] == 6 and c1["behaviour"].startswith("AI-assisted development workflows")
    ids = [lo["id"] for lo in st["los"] if lo["parent_co"] == "CO1"]
    assert dropped not in ids and ids[-1].startswith("CO1.LO") and next(lo for lo in st["los"] if lo["id"] == ids[-1])["hands_on"] is True
    assert all(dropped not in (lo.get("requires") or []) for lo in st["los"])
    assert {m["po_uid"] for m in st["copo"] if m["co_id"] == "CO1"} >= {"BTECH-COMMON/PO11"}
    g = DesignGraph.load(d / "design_graph.json")
    assert g.get(dropped) is None and g.get(ids[-1])["created_by"] == "professor"
    assert any(e["dst"] == "BTECH-COMMON/PO11" for e in g.out("CO1", "MAPS_TO"))
    assert any(c.startswith("CO1 reworded") for c in out["changes"])
    assert views.gate2(st)["cos"][0]["edited"] is True


def test_a_new_outcome_needs_its_condition_and_standard(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate2_outcomes")
    co = {"statement": "Evaluate the security of AI-generated code against common weaknesses.", "bloom_level": 5, "condition": "", "degree": "",
          "covers_topic_groups": ["TG1"], "evidence_types": ["code_review"], "los": [], "pos": []}
    assert {"co.condition", "co.degree"} <= set(mgr.edit(rid, "gate2_outcomes", "co", co)["errors"])
    co.update(condition="given a pull request written by a coding agent", degree="identifying every planted weakness")
    out = mgr.edit(rid, "gate2_outcomes", "co", co)
    new = state(d)["cos"][-1]
    assert new["id"] == "CO5" and new["evidence_types"] == ["code_review"] and out["changes"][0].startswith("CO5 added")


def test_deleting_a_course_outcome_removes_its_learning_outcomes(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate2_outcomes")
    n_lo = sum(1 for lo in state(d)["los"] if lo["parent_co"] == "CO4")
    out = mgr.edit(rid, "gate2_outcomes", "co_delete", {"id": "CO4"})
    st = state(d)
    assert "CO4" not in {c["id"] for c in st["cos"]} and not any(lo["parent_co"] == "CO4" for lo in st["los"])
    assert not any(m["co_id"] == "CO4" for m in st["copo"]) and f"{n_lo} learning outcome" in out["changes"][0]
    assert DesignGraph.load(d / "design_graph.json").get("CO4") is None


# ------------------------------------------------------------------ Final sheet
def test_topic_hours_change_remakes_the_weekly_plan_and_the_sheet(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate3_proposal")
    before = state(d)["schedule"]["hours_needed"]
    mods = views.gate3(state(d), d)["edit"]["weeks"]
    mods[0]["topics"][0]["hours"] = float(mods[0]["topics"][0]["hours"]) + 3
    gone = mods[1]["topics"].pop(0)["id"]
    mods[1]["topics"].append({"title": "Securing agent tool calls", "hours": 1.5, "serves_los": "CO1.LO1"})
    out = mgr.edit(rid, "gate3_proposal", "weeks", mods)
    st = state(d)
    assert st["schedule"]["hours_needed"] != before and any(c.startswith("Weekly plan made again") for c in out["changes"])
    assert all(gone not in (i.get("covers_topics") or []) for c in st["assessment"]["components"] for i in c["instances"])
    new = st["modules"][1]["topics"][-1]
    assert new["serves_los"] == ["CO1.LO1"] and new["id"].startswith(st["modules"][1]["id"] + ".T")
    g = DesignGraph.load(d / "design_graph.json")
    assert g.get(gone) is None and {n["local_id"] for n in g.by_label("Lecture")} == {
        f"W{w['week']:02d}.L{i}" for w in st["schedule"]["weeks"] for i in range(1, len(w["items"]) + 1)}
    assert "Securing agent tool calls" in (d / "proposal.md").read_text(encoding="utf-8")    # the sheet is drawn again
    assert "errors" in mgr.edit(rid, "gate3_proposal", "weeks", [{"id": "M1", "title": "x", "topics": [{"title": "t", "hours": 0}]}])


def test_assessment_weights_and_a_new_component(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate3_proposal")
    comps = views.gate3(state(d), d)["edit"]["assessment"]
    comps[0]["weight"] = comps[0]["weight"] - 5
    comps.append({"type": "presentation", "weight": 5, "invigilated": False, "due": [12]})
    out = mgr.edit(rid, "gate3_proposal", "assessment", comps)
    st = state(d)
    assert st["assessment"]["weight_sum"] == 100 and st["assessment"]["components"][-1]["instances"][0]["due_week"] == 12
    assert st["assessment"]["components"][-1]["instances"][0]["assesses"]          # the LOs taught by week 12
    assert any(c.startswith("Assessment added: Presentations") for c in out["changes"])
    comps = views.gate3(st, d)["edit"]["assessment"][:-1]
    out = mgr.edit(rid, "gate3_proposal", "assessment", comps)
    assert any("not 100%" in c for c in out["changes"])


def test_books_added_by_isbn_and_removed(tmp_path, monkeypatch):
    mgr, rid, d = waiting_at(tmp_path, "gate3_proposal")
    monkeypatch.setattr(edits, "_lookup", lambda ident: {"candidate_id": "ISBN:9781098166304", "title": "AI Engineering", "year": 2024,
                                                         "authors": ["Chip Huyen"], "venue": "O'Reilly",
                                                         "identifier": {"isbn": "9781098166304", "doi": None, "arxiv": None, "url": None}}
                        if "9781098166304" in ident.replace("-", "") else None)
    books = views.gate3(state(d), d)["edit"]["books"]
    removed = books.pop(0)["title"]
    out = mgr.edit(rid, "gate3_proposal", "books", books + [{"ident": "978-1-098-16630-4", "role": "primary"}])
    st = state(d)
    assert st["resources"][-1]["title"] == "AI Engineering" and st["resources"][-1]["verification"]["verified"]
    assert removed not in {r["title"] for r in st["resources"]} and len(out["changes"]) == 2
    assert "0.ident" in mgr.edit(rid, "gate3_proposal", "books", [{"ident": "0000000000"}])["errors"]


def test_continuing_records_the_edits_with_the_approval(tmp_path):
    mgr, rid, d = waiting_at(tmp_path, "gate3_proposal")
    mgr.edit(rid, "gate3_proposal", "description", {"text": "A hands-on course on building software with AI coding agents, "
                                                            "from specification to testing and review."})
    assert mgr.decide(rid, "gate3_proposal", "approve", "Professor", "fine") in (None, "")
    pending = read_meta(d)["pending"]["payload"]
    assert pending["professor_edits"] == ["Course description rewritten"]


def test_edit_endpoint(tmp_path):
    """Through the real app on a free local port (starlette's TestClient doesn't match the installed httpx)."""
    import socket
    import threading
    import time
    import httpx
    import uvicorn
    mgr, rid, d = waiting_at(tmp_path, "gate1_context")
    with socket.socket() as sk:
        sk.bind(("127.0.0.1", 0))
        port = sk.getsockname()[1]
    srv = uvicorn.Server(uvicorn.Config(create_app(manager=mgr, start_worker=False), host="127.0.0.1", port=port, log_level="warning"))
    th = threading.Thread(target=srv.run, daemon=True)
    th.start()
    while not srv.started:
        time.sleep(0.05)
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=30) as c:
            _endpoint_checks(c, rid)
    finally:
        srv.should_exit = True
        th.join(5)


def _endpoint_checks(c, rid):
    r = c.post(f"/api/runs/{rid}/edit", json={"gate": "gate1_context", "section": "prerequisites", "value": [{"code": "NOPE1", "kind": "mandatory"}]})
    assert r.status_code == 422 and "0.code" in r.json()["errors"]
    groups = c.get(f"/api/runs/{rid}").json()["view"]["edit"]["topics"]
    groups[0]["title"] = "Renamed"
    r = c.post(f"/api/runs/{rid}/edit", json={"gate": "gate1_context", "section": "topics", "value": groups})
    assert r.status_code == 200 and r.json()["run"]["view"]["topics"][0]["title"] == "Renamed"
    assert r.json()["run"]["view"]["edited"]["topics"]
    r = c.post(f"/api/runs/{rid}/edit", json={"gate": "gate2_outcomes", "section": "co", "value": {}})
    assert r.status_code == 409
