"""Simulations in the professor app (app/simulations.py): suggestions per lecture, the professor's decisions, class
examples, requests, the sandboxed pages and the HTTP API. Runs on a temporary copy of runs/cs601-02 whose first lectures
are renamed to topics the catalogue has. A word-count embedding stands in for the local model (fast, no download)."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import numpy as np  # noqa: E402
import pytest  # noqa: E402

from profsagent.app import delivery as dv  # noqa: E402
from profsagent.app import simulations as sims  # noqa: E402
from profsagent.config import RUNS  # noqa: E402

pytestmark = pytest.mark.skipif(not (RUNS / "cs601-02" / "delivery" / "briefs.json").exists(), reason="needs runs/cs601-02 with delivery briefs")
TOPICS = ["Page replacement algorithms: FIFO, LRU and Optimal", "Graphical convolution", "DBSCAN"]     # close enough for word counts


def fake_embed(texts):
    out = np.zeros((len(texts), 512), np.float32)
    for i, t in enumerate(texts):
        for w in re.findall(r"[a-z0-9]+", t.lower()):
            out[i, int(hashlib.md5(w.encode()).hexdigest(), 16) % 512] += 1
        out[i] /= np.linalg.norm(out[i]) or 1
    return out


@pytest.fixture
def runs(tmp_path, monkeypatch):
    import profsagent.delivery.common as common
    import profsagent.delivery.review as review
    from profsagent.sims import classify
    r = tmp_path / "runs"
    r.mkdir()
    shutil.copytree(RUNS / "cs601-02", r / "cs601-02", ignore=shutil.ignore_patterns("checkpoint.sqlite*", "llm_calls.jsonl"))
    monkeypatch.setattr(common, "RUNS", r)
    monkeypatch.setattr(dv, "RUNS", r)
    monkeypatch.setattr(sims, "RUNS", r)
    monkeypatch.setattr(review, "FEEDBACK", tmp_path / "delivery_feedback.json")
    monkeypatch.setattr(classify, "embed", fake_embed)
    sims._JOBS.clear()
    return r


@pytest.fixture
def rid(runs):
    rid = dv.copy_example(runs)
    p = runs / rid / "delivery" / "briefs.json"
    briefs = json.loads(p.read_text(encoding="utf-8"))
    for b, t in zip(briefs, TOPICS):
        b["topic"], b["summary"] = t, f"A lecture on {t.lower()}."
    p.write_text(json.dumps(briefs), encoding="utf-8")
    return rid


def lecture(runs, rid, lid):
    return sims.course_view(rid, runs)["lectures"].get(lid, {"items": [], "kind": None})


def test_suggestions_match_lecture_topics(runs, rid):
    assert sims.course_view(rid, runs)["state"] == "not started"          # the view never starts the job itself
    state, sug = sims.suggestions(rid, runs, wait=True)
    assert state == "ready"
    assert sug["W01.L1"]["matches"][0]["id"] == "os.memory.page_replacement" and sug["W01.L1"]["matches"][0]["close"]
    assert sug["W01.L2"]["matches"][0]["id"] == "signals.convolution.graphical"
    assert sug["W02.L1"]["matches"][0]["id"] == "ml.clustering.dbscan"
    assert all(len(v["matches"]) <= sims.TOP and all(m["score"] >= sims.MATCH for m in v["matches"]) for v in sug.values())
    assert all(v["kind"]["type"] in [*sims.C.type_ids(), "none"] for v in sug.values())
    item = lecture(runs, rid, "W01.L1")["items"][0]
    assert item["source"] == "suggested" and item["decision"] is None and item["class_example"] is True
    assert dv.view(rid, runs)["simulations"]["state"] == "ready"
    # a renamed lecture makes the stored suggestions out of date
    p = runs / rid / "delivery" / "briefs.json"
    briefs = json.loads(p.read_text(encoding="utf-8"))
    briefs[0]["topic"] = "Ethics of software engineering"
    p.write_text(json.dumps(briefs), encoding="utf-8")
    assert sims.suggestions(rid, runs, start=False)[0] == "not started"


def test_decisions_and_versions(runs, rid, monkeypatch):
    sims.suggestions(rid, runs, wait=True)
    pr = "os.memory.page_replacement"
    assert sims.decide(rid, "W01.L1", pr, "reject", runs=runs)["problem"] == "Write a short reason first"
    assert sims.decide(rid, "W99.L1", pr, "approve", runs=runs)["problem"] == "No such lecture"
    assert sims.decide(rid, "W01.L1", "no.such.sim", "approve", runs=runs)["problem"]
    assert sims.decide(rid, "W01.L1", pr, "approve", runs=runs) == {"ok": True}
    it = lecture(runs, rid, "W01.L1")["items"][0]
    assert it["decision"]["decision"] == "approve" and it["decision"]["version"] == it["version"] and not it["decision"]["outdated"]
    # the catalogue entry changes version: the approval is marked as needing another look
    bumped = [{**e, "version": "9.9.9"} if e["id"] == pr else e for e in sims.entries()]
    with monkeypatch.context() as m:              # (not monkeypatch.undo(): that would also undo the private runs/ folder)
        m.setattr(sims, "entries", lambda: bumped)
        assert lecture(runs, rid, "W01.L1")["items"][0]["decision"]["outdated"]
    # added from the catalogue goes first; replace and reject set items aside; undo brings them back
    assert sims.decide(rid, "W01.L2", "algorithms.graph.kosaraju", "add", runs=runs) == {"ok": True}
    items = lecture(runs, rid, "W01.L2")["items"]
    assert items[0]["id"] == "algorithms.graph.kosaraju" and items[0]["source"] == "added"
    sims.decide(rid, "W01.L2", "algorithms.graph.kosaraju", "replace", runs=runs)
    sims.decide(rid, "W01.L2", "signals.convolution.graphical", "reject", "Too advanced for this class", runs=runs)
    d = {i["id"]: i["decision"] for i in lecture(runs, rid, "W01.L2")["items"]}
    assert d["algorithms.graph.kosaraju"]["decision"] == "replace" and d["signals.convolution.graphical"]["reason"] == "Too advanced for this class"
    sims.decide(rid, "W01.L2", "signals.convolution.graphical", "undo", runs=runs)
    assert {i["id"]: i["decision"] for i in lecture(runs, rid, "W01.L2")["items"]}["signals.convolution.graphical"] is None
    hist = json.loads((runs / rid / "delivery" / "simulations" / "decisions.json").read_text(encoding="utf-8"))["history"]
    assert [h["decision"] for h in hist] == ["approve", "add", "replace", "reject", "undo"]


def test_class_examples(runs, rid):
    sims.suggestions(rid, runs, wait=True)
    pr = "os.memory.page_replacement"
    assert "cannot keep" in sims.class_example(rid, "W01.L1", "algorithms.graph.dijkstra", "a=1", runs=runs)["problem"]
    assert sims.class_example(rid, "W01.L1", pr, "", runs=runs)["problem"].startswith("Change something")
    assert sims.class_example(rid, "W01.L1", pr, "#refs=1+2+3&frames=4&algo=lru", "LRU, 4 frames", runs=runs) == {"ok": True}
    ex = lecture(runs, rid, "W01.L1")["items"][0]["example"]
    assert ex["state"] == "refs=1+2+3&frames=4&algo=lru" and ex["summary"] == "LRU, 4 frames" and ex["version"]
    assert sims.class_example(rid, "W01.L1", pr, "", clear=True, runs=runs) == {"ok": True}
    assert lecture(runs, rid, "W01.L1")["items"][0]["example"] is None


def test_requests_and_catalogue(runs, rid):
    assert set(sims.add_request({"topic": "", "what": "short"}, runs)["errors"]) == {"topic", "what"}
    assert sims.add_request({"topic": "TCP", "what": "Change the window and watch the rate", "kind": "nope"}, runs)["errors"] == {"kind": "Unknown kind"}
    r = sims.add_request({"topic": "TCP congestion control", "what": "Change the window and the loss rate; watch the rate", "kind": "3-systems-over-time",
                          "run_id": rid, "lecture": "W05.L1"}, runs)
    assert r["request"]["id"] == "R001" and r["request"]["course"] and r["request"]["status"] == "queued"     # the auto-build takes it
    sims.suggestions(rid, runs, wait=True)
    sims.decide(rid, "W01.L1", "os.memory.page_replacement", "approve", runs=runs)
    cat = sims.catalogue_view(runs)
    assert len(cat["entries"]) == len([e for e in sims.entries() if e.get("status") != "retired"]) and len(cat["types"]) == 12
    pr = next(e for e in cat["entries"] if e["id"] == "os.memory.page_replacement")
    assert pr["used"] == [{"run_id": rid, "course": pr["used"][0]["course"], "lecture": "W01.L1", "topic": TOPICS[0]}]
    assert pr["courses"][0]["code"] == "CSE231" and pr["level"]["id"] == "L3" and pr["summary"]
    assert cat["requests"][0]["topic"] == "TCP congestion control"


def test_http_api(runs, rid):
    """Through the real app on a free local port (starlette's TestClient doesn't match the installed httpx)."""
    import socket
    import threading
    import time
    import httpx
    import uvicorn
    from profsagent.app.runner import RunManager
    from profsagent.app.server import create_app
    sims.suggestions(rid, runs, wait=True)
    with socket.socket() as sk:
        sk.bind(("127.0.0.1", 0))
        port = sk.getsockname()[1]
    mgr = RunManager(runs=runs, driver=object(), filler=object(), isolate=False)
    srv = uvicorn.Server(uvicorn.Config(create_app(manager=mgr, start_worker=False), host="127.0.0.1", port=port, log_level="warning"))
    th = threading.Thread(target=srv.run, daemon=True)
    th.start()
    while not srv.started:
        time.sleep(0.05)
    try:
        with httpx.Client(base_url=f"http://127.0.0.1:{port}", timeout=60) as c:
            assert len(c.get("/api/simulations").json()["entries"]) >= 8
            r = c.get("/api/simulations/os.memory.page_replacement/page")
            csp = r.headers["content-security-policy"]
            assert r.status_code == 200 and "sandbox allow-scripts" in csp and "connect-src 'none'" in csp and "SimShare" in r.text
            assert c.get("/api/simulations/..%2F..%2Fapp.json/page").status_code == 404
            assert c.get("/api/simulations/no.such.sim/page").status_code == 404
            v = c.get(f"/api/delivery/{rid}").json()["simulations"]
            assert v["state"] == "ready" and v["lectures"]["W01.L1"]["items"][0]["id"] == "os.memory.page_replacement"
            r = c.post(f"/api/delivery/{rid}/simulations/W01.L1", json={"sim": "os.memory.page_replacement", "decision": "reject"})
            assert r.status_code == 422 and r.json()["problem"] == "Write a short reason first"
            assert c.post(f"/api/delivery/{rid}/simulations/W01.L1", json={"sim": "os.memory.page_replacement", "decision": "approve"}).json() == {"ok": True}
            r = c.post(f"/api/delivery/{rid}/simulations/W01.L1/class-example", json={"sim": "os.memory.page_replacement", "state": "frames=4", "summary": "4 frames"})
            assert r.json() == {"ok": True}
            assert c.post(f"/api/delivery/{rid}/simulations/bad/class-example", json={"sim": "x"}).status_code == 404
            r = c.post("/api/simulations/requests", json={"topic": "x"})
            assert r.status_code == 422 and "topic" in r.json()["errors"]
            it = c.get(f"/api/delivery/{rid}").json()["simulations"]["lectures"]["W01.L1"]["items"][0]
            assert it["decision"]["decision"] == "approve" and it["example"]["state"] == "frames=4"
    finally:
        srv.should_exit = True
        th.join(5)


def test_links_to_trusted_sites(runs, rid, monkeypatch):
    """Simulations on other sites are suggested as links: approve, reject (with a reason) or undo; never copied or checked."""
    from profsagent.sims import external as X
    fake = [{"id": "ext:visualgo:bst", "site": "visualgo", "site_name": "VisuAlgo", "title": "Binary Search Tree and AVL Tree",
             "url": "https://visualgo.net/en/bst", "summary": "Search, insert and delete in a BST.", "topics": ["binary search tree", "AVL tree"], "goals": ""},
            {"id": "ext:phet:projectile-motion", "site": "phet", "site_name": "PhET", "title": "Projectile Motion",
             "url": "https://phet.colorado.edu/en/simulations/projectile-motion", "summary": "Launch objects.", "topics": ["Motion"], "goals": ""}]
    monkeypatch.setattr(X, "entries", lambda: fake)
    p = runs / rid / "delivery" / "briefs.json"
    briefs = json.loads(p.read_text(encoding="utf-8"))
    briefs[3]["topic"] = "Binary Search Tree and AVL Tree"
    p.write_text(json.dumps(briefs), encoding="utf-8")
    lid = briefs[3]["lecture_id"]
    assert sims.suggestions(rid, runs, wait=True)[0] == "ready"
    link = next(i for i in lecture(runs, rid, lid)["items"] if i.get("external"))
    assert link["id"] == "ext:visualgo:bst" and link["source"] == "external" and link["url"] == "https://visualgo.net/en/bst"
    assert link["site_name"] == "VisuAlgo" and link["class_example"] is False and link["decision"] is None
    assert not any(i.get("external") for i in lecture(runs, rid, "W01.L1")["items"])          # page replacement: no link fits
    for bad in ("replace", "add"):
        assert sims.decide(rid, lid, link["id"], bad, runs=runs)["problem"].startswith("A link can only")
    assert sims.decide(rid, lid, "ext:visualgo:nope", "approve", runs=runs)["problem"] == "No such link"
    assert sims.decide(rid, lid, link["id"], "reject", runs=runs)["problem"] == "Write a short reason first"
    assert sims.decide(rid, lid, link["id"], "approve", runs=runs) == {"ok": True}
    assert sims.class_example(rid, lid, link["id"], "a=1", runs=runs)["problem"]          # links never keep a class example
    # an approved link stays on the lecture even when it is no longer suggested
    monkeypatch.setattr(sims, "EXT_MATCH", 0.999)
    it = next(i for i in lecture(runs, rid, lid)["items"] if i["id"] == link["id"])
    assert it["decision"]["decision"] == "approve" and it["source"] == "decided" and it["external"]
    cat = sims.catalogue_view(runs)["external"]
    assert cat["sites"][0] in ("VisuAlgo", "PhET") and any("visualgo" in x["text"] and x["url"].startswith("https://") for x in cat["entries"])
