"""The app side of C's delivery mix (Vihan's delivery/mix.py; docs/decisions.md 32 and 37): the plan in the delivery
view, the professor's changes through the app (checked against the evidence), and the background jobs that propose,
re-propose in a style and approve. Offline: no AI is called (the jobs are only queued)."""
import json
import socket
import sys
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from profsagent.app import delivery as dv  # noqa: E402
from profsagent.config import RUNS  # noqa: E402

pytestmark = pytest.mark.skipif(not (RUNS / "cs601-02" / "delivery" / "lectures").exists(), reason="needs runs/cs601-02 with delivery results")
L = "W01.L1"


@pytest.fixture
def runs(tmp_path, monkeypatch):
    import shutil
    import profsagent.delivery.common as common
    from profsagent.delivery import mix
    r = tmp_path / "runs"
    r.mkdir()
    shutil.copytree(RUNS / "cs601-02", r / "cs601-02", ignore=shutil.ignore_patterns("checkpoint.sqlite*", "llm_calls.jsonl"))
    monkeypatch.setattr(common, "RUNS", r)
    monkeypatch.setattr(dv, "RUNS", r)
    monkeypatch.setattr(mix, "match_simulations", lambda comps: {})
    monkeypatch.setattr(mix, "source_texts", lambda res: ["model context protocol schema tools explained"])
    return r


@pytest.fixture
def rid(runs):
    """An example copy whose first lecture has a part plan (as C writes it since 3 Nov) and a proposed mix (rules only)."""
    from profsagent.delivery import mix
    rid = dv.copy_example(runs)
    d = runs / rid / "delivery"
    comps = [{"id": f"{L}.C{i}", "lecture_id": L, "title": t, "teaches": t + " in practice", "key_terms": ["schema"], "kind": k, "bloom": 2,
              "lo_ids": ["CO1.LO1"], "minutes": m} for i, (t, k, m) in enumerate([("Why tools need a protocol", "concept", 30),
                                                                                    ("Write a tool schema in pairs", "activity", 40),
                                                                                    ("How a client calls a tool", "mechanism", 30)], 1)]
    seg = {"video": "MCP explained", "video_id": "v1", "url": "https://www.youtube.com/watch?v=v1", "start": "01:00", "end": "29:00",
           "minutes": 28, "verdict": "teaches_fully", "clarity": 5, "level_fit": 5}
    lec = json.loads((d / "lectures" / f"{L}.json").read_text(encoding="utf-8"))
    lec["components"] = comps
    lec.setdefault("resources", {})["timeline"] = [{"component": comps[0]["id"], "delivery": "video", "segments": [seg]},
                                                    {"component": comps[1]["id"], "delivery": "in_class", "segments": []},
                                                    {"component": comps[2]["id"], "delivery": "notebooklm", "segments": []}]
    (d / "lectures" / f"{L}.json").write_text(json.dumps(lec), encoding="utf-8")
    (d / "components.json").write_text(json.dumps({"T1": {"lectures": [{"lecture_id": L, "lecture_minutes": 120, "reserved": {"recap": 0, "quiz": 10}}],
                                                          "components": comps}}), encoding="utf-8")
    mix.propose(rid, L, use_ai=False, sims={})
    return rid


def test_the_plan_is_in_the_delivery_view(runs, rid):
    v = dv.view(rid, runs)["mix"]
    m = v["lectures"][L]
    assert m["status"] == "proposed" and [p["component"] for p in m["parts"]] == [f"{L}.C1", f"{L}.C2", f"{L}.C3"]
    assert m["quiz_minutes"] == 10 and v["style"] == "mix" and v["quiz"] == {}
    assert next(p for p in m["parts"] if p["component"].endswith("C2"))["way"] == "in_class"     # an activity is taught in class


def test_jobs_and_errors_for_the_mix(runs, rid):
    mgr = dv.DeliveryManager(runs)
    mgr.queue_mix(rid, L, {"action": "approve", "by": "Professor"})
    j = json.loads((runs / rid / "delivery" / "app_jobs.json").read_text(encoding="utf-8"))["mix"][L]
    assert j["state"] == "queued" and j["action"] == "approve" and mgr.q.get()[0] == "mix"
    assert "no parts yet" in dv._plain_error({"type": "ValueError", "message": "W01.L1 has no component plan yet: run recommend first"}, "mix")
    assert dv._plain_error({"type": "X", "message": "m", "quota": True}, "mix").startswith("The free AI quota")


def test_the_professor_changes_the_plan_through_the_app(runs, rid):
    import httpx
    import uvicorn
    from profsagent.app.runner import RunManager
    from profsagent.app.server import create_app
    with socket.socket() as sk:
        sk.bind(("127.0.0.1", 0))
        port = sk.getsockname()[1]
    mgr = RunManager(runs=runs, driver=object(), filler=object(), isolate=False)
    srv = uvicorn.Server(uvicorn.Config(create_app(manager=mgr, start_worker=False), host="127.0.0.1", port=port, log_level="warning"))
    threading.Thread(target=srv.run, daemon=True).start()
    while not srv.started:
        time.sleep(0.05)
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=60) as c:
            u = f"/api/delivery/{rid}/mix/{L}"
            r = c.post(u, json={"action": "save", "changes": {f"{L}.C3": {"way": "youtube"}}})          # no checked stretch for this part
            assert r.status_code == 409 and "not possible" in r.json()["problem"]
            r = c.post(u, json={"action": "save", "changes": {f"{L}.C2": {"locked": True}, f"{L}.C1": {"way": "in_class"}, "../x": {"way": "slides"}}})
            m = r.json()["mix"]
            p1, p2 = (next(p for p in m["parts"] if p["component"].endswith(s)) for s in ("C1", "C2"))
            assert r.status_code == 200 and p2["locked"] and p1["way"] == "in_class" and p1["set_by"] == "professor"
            assert c.post(u, json={"action": "preset", "preset": "nope"}).status_code == 409
            assert c.post(f"/api/delivery/{rid}/mix/W02.L2", json={"action": "approve"}).status_code == 409      # no plan there yet
            assert c.post(u, json={"action": "approve"}).json() == {"queued": True}
            assert c.get(f"/api/delivery/{rid}").json()["jobs"]["mix"][L]["state"] == "queued"
            assert c.post(u, json={"action": "style", "style": "flipped"}).json() == {"style": "flipped"}
            assert c.post(u, json={"action": "dance"}).status_code == 409
    finally:
        srv.should_exit = True
