"""The Claude Code handoff (src/profsagent/agentcc): a run marked `agent: claude_code` writes a request per AI step and
waits; the session checks drafts against the pipeline's own validators and submits one answer. Here a thread plays
the session. No AI calls, no Neo4j."""
from __future__ import annotations

import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from profsagent.agentcc import bridge as B  # noqa: E402
from profsagent.agentcc import protocol as P  # noqa: E402
from profsagent.agentcc.__main__ import main as cli  # noqa: E402
from profsagent.app import formmap  # noqa: E402


class Out(BaseModel):
    title: str
    weeks: int


@pytest.fixture
def runs(tmp_path, monkeypatch):
    monkeypatch.setattr(B, "POLL_S", 0.05)
    import profsagent.agentcc.__main__ as M
    monkeypatch.setattr(M, "RUNS", tmp_path)
    monkeypatch.setattr(M, "SEEN", tmp_path / "_agentcc_seen.json")
    (tmp_path / "ml-2").mkdir()
    return tmp_path


def session(runs: Path, steps: list[tuple[str, dict]], log: list):
    """Plays the Claude Code session: waits for a request, then for each (kind, obj) sends a draft or the answer."""
    def go():
        t0 = time.time()
        while not P.open_requests(runs) and time.time() - t0 < 10:
            time.sleep(0.05)
        req = P.open_requests(runs)[0]
        log.append(P.read_json(req))
        for kind, obj in steps:
            f = runs / f"{kind}.json"
            f.write_text(json.dumps(obj), encoding="utf-8")
            log.append((kind, cli([("check" if kind == "draft" else "submit"), str(req), str(f)])))
    t = threading.Thread(target=go, daemon=True)
    t.start()
    return t


def test_structured_step_waits_for_the_session_and_rejects_a_bad_answer(runs):
    br = B.AgentBridge(runs / "ml-2", {"agent": "claude_code", "exclude_courses": ["AI501", "CSE343"]})
    log = []
    t = session(runs, [("draft", {"title": "ML"}), ("answer", {"title": "ML with AI501", "weeks": 13}), ("answer", {"title": "ML", "weeks": 13})], log)
    obj, rec = br.structured(system="sys", user="inputs", model_cls=Out, prompt_id="G1", prompt_version="1")
    t.join(5)
    req = log[0]
    assert req["pid"] == "G1" and req["kind"] == "structured" and req["hidden"]["courses"] == ["AI501", "CSE343"] and "weeks" in json.dumps(req["schema"])
    assert log[1] == ("draft", 2)                          # schema error reported on the draft
    assert log[2] == ("answer", 2)                         # names a hidden course: rejected
    assert log[3] == ("answer", 0)
    assert obj.title == "ML" and rec.endpoint == "claude-code"
    calls = [json.loads(x) for x in (runs / "ml-2" / "llm_calls.jsonl").read_text(encoding="utf-8").splitlines()]
    assert len(calls) == 1 and calls[0]["prompt_id"] == "G1" and calls[0]["drafts_checked"] == 1
    assert "handed to Claude Code" in (runs / "ml-2" / "run.log").read_text(encoding="utf-8")


def test_generate_step_reports_the_stage_validators_on_each_draft(runs, monkeypatch):
    from profsagent.validate import engine
    from profsagent.llm import prompts

    class FakePrompt:
        version = "9"

        def render(self, **ctx):
            return "brief", json.dumps(ctx)
    monkeypatch.setattr(B, "load_prompt", lambda pid: FakePrompt())
    monkeypatch.setitem(B.OUTPUT_MODELS, "GX", Out)
    # a stand-in validator: weeks must be 13
    monkeypatch.setattr(engine, "check", lambda state, stages: [] if state["out"]["weeks"] == 13 else
                        [{"code": "VT-WEEKS", "severity": "error", "message": "13 weeks", "nodes": ["W"]}])
    monkeypatch.setattr(engine, "errors", lambda vs: [x for x in vs if x["severity"] == "error"])
    monkeypatch.setattr(engine, "apply_fixers", lambda st, comp, apply, stages, vs: (comp, vs, []))
    monkeypatch.setattr(engine, "strip_v2", lambda vs: vs)
    monkeypatch.setattr(engine, "error_codes", lambda vs: sorted({x["code"] for x in vs}))
    monkeypatch.setattr(engine, "open_items", lambda vs: vs)

    class RT:
        state = {"form": {}}
        llm = None
        logs = []

        def log(self, m):
            self.logs.append(m)
    rt = RT()
    br = B.AgentBridge(runs / "ml-2", {"agent": "claude_code"})
    log = []
    t = session(runs, [("draft", {"title": "ML", "weeks": 14}), ("answer", {"title": "ML", "weeks": 13})], log)
    comp, vs, trace = br.generate(rt, "GX", {"cco": {"name": "ML"}}, apply=lambda s, c: {**s, "out": c}, stages=["structure"])
    t.join(5)
    assert log[0]["checks"] == ["structure"] and log[0]["kind"] == "generate"
    assert log[1] == ("draft", 2)                          # the validator's error came back on the draft
    assert comp == {"title": "ML", "weeks": 13} and vs == [] and trace["final_errors"] == 0 and trace["repairs"] == []
    assert trace["agent"]["drafts_checked"] == 1 and any("accepted from Claude Code" in m for m in rt.logs)


def test_watch_announces_each_request_once(runs):
    br = B.AgentBridge(runs / "ml-2", {})
    br._request("G3", "1", "structured", "b", "i", {}, None)
    assert cli(["watch", "--timeout", "1"]) == 0
    assert cli(["watch", "--timeout", "0.5"]) == 1       # already announced
    assert cli(["watch", "--all", "--timeout", "0.5"]) == 0


def test_the_form_marks_a_claude_code_run_and_the_pipeline_picks_the_bridge(tmp_path):
    f = json.loads((Path(__file__).resolve().parents[1] / "Temporary/ml_compare/ml_form.json").read_text(encoding="utf-8")) \
        if (Path(__file__).resolve().parents[1] / "Temporary/ml_compare/ml_form.json").exists() else \
        {"name": "Machine Learning", "description": "x", "hold_out": ["AI501"]}
    _, cfg1 = formmap.to_pipeline(f)
    _, cfg2 = formmap.to_pipeline({**f, "agent": "claude_code"})
    assert "agent" not in cfg1 and cfg2["agent"] == "claude_code" and "AI501" in cfg2["exclude_courses"]
    assert isinstance(B.llm_for(tmp_path, cfg2), B.AgentBridge)
    assert not isinstance(B.llm_for(tmp_path, cfg1), B.AgentBridge)


# ------------------------------------------------------------------ delivery jobs of a claude_code run (agentcc/delivery.py)
def _delivery_run(root: Path, rid: str = "app-ml-2") -> Path:
    import yaml
    d = root / rid
    (d / "delivery").mkdir(parents=True)
    (d / "state.json").write_text(json.dumps({"run_cfg": {"agent": "claude_code", "exclude_courses": ["AI501"],
                                                          "blocklist": ["techtree.iiitd.edu.in"]}}), encoding="utf-8")
    (d / "delivery" / "survey.yaml").write_text(yaml.safe_dump({"lectures": {"W06.L1": {
        "topic": "Backpropagation", "own_material": "no", "attach_material": "no", "generate_material": "yes",
        "assistance": "yes", "guest_lecture": "yes", "want_videos": "yes", "want_readings": "no"}}}), encoding="utf-8")
    return d


def test_delivery_job_is_handed_over_and_reused(tmp_path, monkeypatch):
    from profsagent.agentcc import delivery as D
    import profsagent.delivery.common as C
    from profsagent.app import delivery_step
    d = _delivery_run(tmp_path)
    monkeypatch.setattr(D, "RUNS", tmp_path)
    monkeypatch.setattr(C, "RUNS", tmp_path)
    af = d / "delivery" / "app_step_args.json"
    af.write_text(json.dumps({"lectures": ["W06.L1"], "refresh": False}), encoding="utf-8")
    assert delivery_step.main(["x", "app-ml-2", "recommend", str(af)]) == 0
    res = json.loads((d / "delivery" / "app_step_result.json").read_text(encoding="utf-8"))
    assert res["pending"] and not res["ok"]["reused"]
    reqs = list((d / "agentcc").glob("*.request.json"))
    assert len(reqs) == 1 and P.read_json(reqs[0])["owner_pid"] is None
    assert P.open_requests(tmp_path) == reqs                      # the watcher sees it though the step process ended
    assert D.hand_off("app-ml-2", "recommend", {"lectures": ["W06.L1"], "refresh": False}, tmp_path)["reused"]
    assert "handed to Claude Code" in (d / "delivery" / "delivery.log").read_text(encoding="utf-8")
    assert not D.is_agent("other", tmp_path)


def test_delivery_finish_checks_files_then_marks_done(tmp_path):
    from profsagent.agentcc import delivery as D
    d = _delivery_run(tmp_path)
    req = tmp_path / "app-ml-2" / "agentcc" / D.hand_off("app-ml-2", "recommend", {"lectures": ["W06.L1"]}, tmp_path)["request"]
    probs = D.finish(req)
    assert any("lectures/W06.L1.json is missing" in x for x in probs) and not P.sibling(req, "done.json").exists()
    lec = {"lecture_id": "W06.L1", "topic": "Backpropagation", "components": [
        {"id": "W06.L1.C1", "lecture_id": "W06.L1", "title": "Chain rule", "teaches": "x", "kind": "concept", "bloom": 2,
         "lo_ids": [], "minutes": 80, "in_class": False}],
        "resources": {"items": {"video": [{"url": "https://www.youtube.com/watch?v=x", "title": "v", "rank": 1, "total": 0.8}]},
                      "reserve": {}},
        "experts": {"experts": [{"name": "A. Person", "kind": "academic", "rank": 1, "total": 0.8, "why": "see AI501"}], "reserve": []}}
    (d / "delivery" / "lectures").mkdir()
    (d / "delivery" / "lectures" / "W06.L1.json").write_text(json.dumps(lec), encoding="utf-8")
    assert D.finish(req) == ["names a hidden course or domain: AI501"]
    lec["experts"]["experts"][0]["why"] = "Works on optimisation."
    (d / "delivery" / "lectures" / "W06.L1.json").write_text(json.dumps(lec), encoding="utf-8")
    assert D.finish(req) == []
    assert P.sibling(req, "done.json").exists() and P.open_requests(tmp_path) == []
    jobs = json.loads((d / "delivery" / "app_jobs.json").read_text(encoding="utf-8"))
    assert jobs["lectures"]["W06.L1"]["state"] == "done"
