"""Search before building (sims/websearch.py; app/simulations.review_found; the auto-build worker): a request first looks
for existing simulations, the professor reviews them, and the machine builds only when none fits. No network here:
the web search and the page visits are replaced by fixed results."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pytest  # noqa: E402

from profsagent.app import simulations as S  # noqa: E402
from profsagent.sims import autobuild as AB  # noqa: E402
from profsagent.sims import external as X  # noqa: E402
from profsagent.sims import websearch as W  # noqa: E402
from test_app_simulations import fake_embed, rid, runs  # noqa: E402,F401 - fixtures: a private copy of the CS-601 course


def page(title, canvas=0, ranges=0, buttons=0, text="", heads="", ok=True, url=""):
    return {"ok": ok, "title": title, "meta": "", "heads": heads, "text": text, "canvas": canvas, "svg": 0, "iframe": 0, "ranges": ranges,
            "buttons": buttons, "inputs": 0, "words": 2, "final_url": url, "shot": "1.jpg"}


def test_page_judging_rules():
    assert W.keywords("Introduction to the Tower of Hanoi") == ["tower", "hanoi"]
    assert W.names_topic(page("Tower of Hanoi - Recursion Visualization"), "https://x.org/a", "Tower of Hanoi")
    assert W.names_topic(page("Virtual Labs"), "https://ds2-iiith.vlabs.ac.in/exp/selection-sort/overview.html", "Selection Sort")    # by its address
    assert not W.names_topic(page("Virtual Labs", heads="Merge Sort"), "https://ds1-iiith.vlabs.ac.in/exp/merge-sort/overview.html", "Selection Sort")
    assert W.interactive(page("x", canvas=1, buttons=4)) >= 3 and W.interactive(page("x")) < 3                # an article is not a simulation
    assert W.page_title(page("Virtual Labs", heads="Selection Sort | Overview"), {}, "https://ds2-iiith.vlabs.ac.in/exp/selection-sort/") == "Selection Sort"
    assert W.SKIP.search("https://en.wikipedia.org/wiki/Tower_of_Hanoi") and W.SKIP.search("https://x.org/notes.pdf")
    assert W.trusted("https://dm1-iiith.vlabs.ac.in/exp/recursion/simulation/index.html") and not W.trusted("https://www.mathsisfun.com/x")


def test_find_visits_the_top_pages_and_keeps_real_simulations(tmp_path, monkeypatch):
    from profsagent.sims import classify
    monkeypatch.setattr(classify, "embed", fake_embed)
    results = {
        True: [{"url": "https://dm1-iiith.vlabs.ac.in/exp/recursion/simulation/index.html", "title": "Tower of Hanoi", "content": "", "score": 0.6, "via": "tavily"},
               {"url": "https://www.geogebra.org/m/abc", "title": "Design examples", "content": "", "score": 0.5, "via": "tavily"},
               {"url": "https://phet.colorado.edu/en/licensing", "title": "Licensing", "content": "", "score": 0.05, "via": "tavily"}],   # too weak: not visited
        False: [{"url": "https://en.wikipedia.org/wiki/Tower_of_Hanoi", "title": "Tower of Hanoi", "content": "", "score": 0.8, "via": "tavily"},    # skipped
                {"url": "https://www.mathplayground.com/logic_tower_of_hanoi.html", "title": "Tower of Hanoi", "content": "", "score": 0.6, "via": "tavily"}],
    }
    monkeypatch.setattr(W, "web", lambda q, domains=None: results[bool(domains)])
    seen = []
    pages = {"vlabs": page("Tower of Hanoi - Recursion Visualization", canvas=1, buttons=4, text="Tower of Hanoi recursion"),
             "geogebra": page("Design examples of interactivities", canvas=1, buttons=4, text="geometry"),
             "mathplayground": page("Tower of Hanoi | Math Playground", canvas=1, text="tower of hanoi puzzle game")}

    def fake_visit(urls, shots):
        seen.extend(urls)
        return [{**next(v for k, v in pages.items() if k in u), "final_url": u, "shot": f"{i + 1}.jpg"} for i, u in enumerate(urls)]
    monkeypatch.setattr(W, "visit", fake_visit)
    monkeypatch.setattr(S, "entries", lambda: [])                     # nothing of ours
    monkeypatch.setattr(X, "entries", lambda: [])
    out = W.find({"id": "R009", "topic": "Tower of Hanoi", "what": "the recursion moving the disks"}, tmp_path)
    assert not any("wikipedia" in u or "licensing" in u for u in seen)          # skipped before visiting
    assert [c["site"] for c in out] == ["Virtual Labs (IITs/IIITs, MoE)", "mathplayground.com"]       # geogebra: not about the topic
    assert out[0]["trusted"] and not out[1]["trusted"] and [c["n"] for c in out] == [1, 2] and out[0]["shot"] == "1.jpg"


def test_review_approve_reject_and_build(runs, rid, monkeypatch, tmp_path):
    monkeypatch.setattr(X, "FOUND", tmp_path / "found.json")
    S.suggestions(rid, runs, wait=True)
    lid = json.loads((runs / rid / "delivery" / "briefs.json").read_text(encoding="utf-8"))[4]["lecture_id"]
    found = [{"n": 1, "kind": "link", "url": "https://dm1-iiith.vlabs.ac.in/exp/recursion/simulation/index.html", "title": "Tower of Hanoi",
              "summary": "", "site": "Virtual Labs (IITs/IIITs, MoE)", "trusted": True, "ext_id": None, "shot": "1.jpg"},
             {"n": 2, "kind": "link", "url": "https://www.mathplayground.com/logic_tower_of_hanoi.html", "title": "Tower of Hanoi game",
              "summary": "", "site": "mathplayground.com", "trusted": False, "ext_id": None, "shot": "2.jpg"}]
    a = S.add_request({"topic": "Tower of Hanoi", "what": "See the recursion move the disks", "run_id": rid, "lecture": lid}, runs)["request"]
    b = S.add_request({"topic": "Tower of Hanoi", "what": "See the recursion move the disks"}, runs)["request"]
    for r in (a, b):
        AB.set_request(runs, r["id"], status="review", found=json.loads(json.dumps(found)))
    # approve: the request is done, the page joins the saved links, and the lecture gets it approved
    out = S.review_found(a["id"], 1, "approve", runs)
    assert out["request"]["status"] == "chosen" and not out["start_build"]
    ext_id = out["request"]["chosen"]["ext_id"]
    assert ext_id.startswith("ext:web:") and X.get(ext_id)["url"] == found[0]["url"]
    item = next(i for i in S.course_view(rid, runs)["lectures"][lid]["items"] if i["id"] == ext_id)
    assert item["decision"]["decision"] == "approve" and item["external"]
    # reject them all: the machine builds one
    assert S.review_found(b["id"], 1, "reject", runs)["start_build"] is False
    out = S.review_found(b["id"], 2, "reject", runs)
    assert out["start_build"] and out["request"]["status"] == "build_queued"
    assert S.review_found(b["id"], 1, "approve", runs)["problem"]                      # no longer under review
    # "None of these fit" carries the professor's note to the builder
    c = S.add_request({"topic": "Tower of Hanoi", "what": "See the recursion"}, runs)["request"]
    AB.set_request(runs, c["id"], status="review", found=found)
    assert S.build_again(c["id"], runs, note="show the call stack")["request"]["status"] == "build_queued"
    req = next(r for r in AB.read_requests(runs) if r["id"] == c["id"])
    prompt = AB.user_prompt(req)
    assert "did not fit: Tower of Hanoi (Virtual Labs" in prompt and "show the call stack" in prompt


def test_worker_searches_first_and_builds_only_when_nothing_fits(tmp_path, monkeypatch):
    runs = tmp_path / "runs"
    runs.mkdir()
    a = S.add_request({"topic": "Tower of Hanoi", "what": "See the recursion move the disks"}, runs)["request"]
    b = S.add_request({"topic": "TCP congestion control", "what": "Change the window and watch the rate"}, runs)["request"]
    monkeypatch.setattr(W, "find", lambda req, work, log=print: [{"n": 1, "kind": "link", "url": "https://x.vlabs.ac.in/h", "title": "Hanoi"}]
                        if "Hanoi" in req["topic"] else [])
    built = []
    monkeypatch.setattr(AB, "build_request", lambda req, runs, log=print: built.append(req["id"]) or {"status": "ready", "sim_id": "auto.x", "build": {}})
    assert AB.worker(runs) == 0
    rows = {r["id"]: r for r in AB.read_requests(runs)}
    assert rows[a["id"]]["status"] == "review" and rows[a["id"]]["found"][0]["title"] == "Hanoi"      # found: waits for the professor
    assert rows[b["id"]]["status"] == "ready" and built == [b["id"]]                                  # nothing found: built at once
