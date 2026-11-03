"""The auto-build (sims/autobuild.py): the machine turns a simulation request into a recipe for the stepper engine and
accepts it only when the automatic checks (simulations/_engines/stepper/qa_recipe.py) pass. No AI here: a stand-in returns
recipes. The browser tests need Playwright with Chrome; they run the real checks on the hand-written example recipe."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest  # noqa: E402

from profsagent.sims import autobuild as AB  # noqa: E402
from profsagent.sims import catalogue as C  # noqa: E402

EXAMPLE = AB.EXAMPLE.read_text(encoding="utf-8")


def _chrome() -> bool:
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            p.chromium.launch(channel="chrome").close()
        return True
    except Exception:  # noqa: BLE001
        return False


needs_chrome = pytest.mark.skipif(not _chrome(), reason="needs Playwright with Chrome")


def test_reading_the_ai_reply_and_the_static_rules():
    assert AB.extract("Here it is:\n```javascript\nconst recipe = { a: 1 };\n```\nDone.") == ("code", "const recipe = { a: 1 };")
    assert AB.extract("DECLINE: an ethics debate has no steps to show") == ("decline", "an ethics debate has no steps to show")
    assert AB.extract("Sorry, I cannot.")[0] == "none"
    assert AB.static_problems(EXAMPLE) == []
    bad = "const recipe = { run() { fetch('x'); document.title = 1; return localStorage; } };"
    found = " ".join(AB.static_problems(bad))
    assert "fetch" in found and "document" in found and "localStorage" in found
    assert AB.static_problems("const recipe = { run(n) { return n.parent.top.window.x; } };") == []     # properties are fine
    page = AB.page_src(EXAMPLE, "Binary <search>")
    assert "<title>Binary &lt;search&gt;</title>" in page and "../_engines/stepper/stepper.js" in page and "Stepper.mount(recipe)" in page


@needs_chrome
def test_the_checks_accept_the_example_and_catch_mistakes(tmp_path):
    ok = AB.run_checks(EXAMPLE, tmp_path / "good", "Binary search")
    assert ok["ok"], ok["problems"]
    assert ok["meta"]["title"] == "Binary search, step by step" and len(ok["meta"]["topics"]) >= 2
    bad = (EXAMPLE
           .replace("return { ok: okIndex && okLooks,", "return { ok: true,")                # a check that accepts anything
           .replace("result: { index: 5, looks: 3 } }", "result: { index: 4, looks: 3 } }")      # a wrong textbook answer
           .replace("type: 'vars'", "type: 'variables'"))                                         # a widget the engine does not have
    rep = AB.run_checks(bad, tmp_path / "bad", "Binary search")
    text = " | ".join(rep["problems"])
    assert not rep["ok"]
    assert "accepted a wrong result" in text and "textbook answer" in text and "unknown widget" in text
    lazy = EXAMPLE.replace("const { a, t } = p, r = trace.result || {};", "const { a, t } = p, r = recipe.run(values).result;")
    rep = AB.run_checks(lazy, tmp_path / "lazy", "Binary search")
    assert any("calls run()" in x for x in rep["problems"])
    # Amit, 3 Nov: a simulation shows a figure; a list shown only as a table, beside variables, is refused
    tables = EXAMPLE.replace("return [{ type: 'array', label: 'The list', items: a, marks, pointers },",
                             "return [{ type: 'table', label: 'The list', columns: a.map((_, i) => i), rows: [a] },")
    rep = AB.run_checks(tables, tmp_path / "tables", "Binary search")
    assert any("must show a figure" in x for x in rep["problems"]), rep["problems"]


class FakeAI:
    """Returns the given replies in turn, like LLMClient.raw."""
    def __init__(self, replies):
        self.replies, self.prompts = list(replies), []

    def raw(self, role, system, user, temperature=0.2, json_mode=True, record=None, **kw):
        self.prompts.append(user)
        return self.replies.pop(0), {"prompt": len(user) // 4, "output": 500}, {}

    def _log(self, *a, **kw):
        pass


@pytest.fixture
def sims_copy(tmp_path, monkeypatch):
    """A private simulations/ folder (engines, library, types) so a built entry never lands in the real catalogue."""
    s = tmp_path / "simulations"
    for part in ("_engines", "_lib"):
        shutil.copytree(C.SIMS / part, s / part)
    shutil.copy(C.SIMS / "types.yaml", s / "types.yaml")
    monkeypatch.setattr(C, "SIMS", s)
    monkeypatch.setattr(C, "BUILD", s / "_build")
    monkeypatch.setattr(C, "LIB", s / "_lib")
    for name, rel in (("ENGINE", "_engines/stepper"), ("README", "_engines/stepper/README.md"), ("EXAMPLE", "_engines/stepper/example_recipe.js"),
                      ("QA", "_engines/stepper/qa_recipe.py")):
        monkeypatch.setattr(AB, name, s / rel)
    runs = tmp_path / "runs"
    runs.mkdir()
    return s, runs


@needs_chrome
def test_a_request_is_built_after_one_retry(sims_copy):
    s, runs = sims_copy
    req = {"id": "R007", "topic": "Binary search", "what": "See how the range halves each time", "course": "DSA", "at": "2026-11-03 10:00:00"}
    AB.update_requests(runs, lambda rows: rows.append({**req, "status": "queued"}))
    broken = EXAMPLE.replace("  examples: [", "  old_examples: [")                      # no examples: the checks must refuse it
    ai = FakeAI(["```javascript\n" + broken + "\n```", "Fixed:\n```javascript\n" + EXAMPLE + "\n```"])
    out = AB.build_request(req, runs, llm=ai, log=lambda m: None)
    assert out["status"] == "ready" and out["build"]["attempts"] == 2 and out["build"]["calls"] == 2, out
    assert "Problems found" in ai.prompts[1] and "examples" in ai.prompts[1]                # the second prompt carries the problems
    sid = out["sim_id"]
    assert sid == "auto.binary_search" and (s / sid / "sim.yaml").exists()
    e = next(x for x in C.entries() if x["id"] == sid)
    assert C.problems(e) == [] and e["status"] == "draft" and e["built_by"] == "machine" and e["request"] == "R007"
    assert e["class_example"] is True and (C.BUILD / f"{sid}.html").exists()
    assert json.loads((C.BUILD / "qa_report.json").read_text(encoding="utf-8"))[sid]["ok"] is True
    assert (runs / AB.BUILDS / "R007" / "attempt-1.problems.txt").read_text(encoding="utf-8") != "none"


@needs_chrome
def test_a_built_simulation_waits_for_the_professor(sims_copy):
    """Amit, 3 Nov: what the machine builds is not in the list until a professor approves it; Reject (with a reason)
    takes it out of the catalogue and builds it again with that reason."""
    from profsagent.app import simulations as S
    s, runs = sims_copy
    REPLY = "```javascript\n" + EXAMPLE + "\n```"
    req = {"id": "R009", "topic": "Binary search", "what": "See how the range halves each time", "at": "2026-11-03 10:00:00"}
    AB.update_requests(runs, lambda rows: rows.append({**req, "status": "queued"}))
    AB.set_request(runs, "R009", **AB.build_request(req, runs, llm=FakeAI([REPLY]), log=lambda m: None))
    sid = S.requests(runs)[0]["sim_id"]
    cat = S.catalogue_view(runs)
    assert sid not in [e["id"] for e in cat["entries"]] and sid in [e["id"] for e in cat["pending"]]
    assert S.review_build("R009", "reject", "", runs)["problem"].startswith("Write")
    assert S.review_build("R009", "reject", "No picture of the range", runs) == {"ok": True, "start_build": True}
    r = S.requests(runs)[0]
    assert r["status"] == "build_queued" and r["note"] == "No picture of the range" and r["sim_id"] is None and not (s / sid).exists()
    assert list((runs / AB.BUILDS / "rejected").glob(sid + "-*/sim.yaml"))
    assert "No picture of the range" in AB.user_prompt(r)                                   # the rebuild carries the reason
    AB.set_request(runs, "R009", **AB.build_request(r, runs, llm=FakeAI([REPLY]), log=lambda m: None))
    assert S.review_build("R009", "approve", runs=runs) == {"ok": True}
    assert S.requests(runs)[0]["status"] == "approved" and sid in [e["id"] for e in S.catalogue_view(runs)["entries"]]
    assert "approved_by" in (s / sid / "sim.yaml").read_text(encoding="utf-8")
    assert S.review_build("R009", "approve", runs=runs)["problem"]                         # nothing left to review


def test_declined_and_unusable_replies(sims_copy):
    _, runs = sims_copy
    req = {"id": "R008", "topic": "Ethics of AI", "what": "Debate the trade-offs", "at": "2026-11-03 10:00:00"}
    AB.update_requests(runs, lambda rows: rows.append({**req, "status": "queued"}))
    out = AB.build_request(req, runs, llm=FakeAI(["DECLINE: a debate has no steps to show"]), log=lambda m: None)
    assert out["status"] == "needs_team" and "does not suit" in out["reason"]
    out = AB.build_request(req, runs, llm=FakeAI(["no code", "still none", "nothing"]), log=lambda m: None)
    assert out["status"] == "needs_team" and out["build"]["calls"] == 3 and "3 attempts" in out["reason"]


def test_requests_file_and_worker_state(tmp_path, monkeypatch):
    from profsagent.app import simulations as S
    runs = tmp_path / "runs"
    runs.mkdir()
    a = S.add_request({"topic": "Tower of Hanoi", "what": "See the recursion move the disks"}, runs)["request"]
    b = S.add_request({"topic": "Selection sort", "what": "See the minimum chosen and swapped"}, runs)["request"]
    assert (a["id"], b["id"], a["status"]) == ("R001", "R002", "queued")
    assert S.build_again("R001", runs)["problem"]                      # already queued
    AB.set_request(runs, "R001", status="needs_team", reason="x")
    assert S.build_again("R001", runs)["request"]["status"] == "build_queued"      # Try again: build (the search was done)
    AB.set_request(runs, "R002", status="requested")
    assert S.build_again("R002", runs)["request"]["status"] == "queued"            # an old request: look for existing ones first
    assert not AB.worker_alive(runs)
    (runs / AB.WORKER).write_text(json.dumps({"pid": 1, "alive_at": __import__("time").time()}), encoding="utf-8")
    assert AB.worker_alive(runs) and AB.start_worker(runs) is False   # one worker at a time
