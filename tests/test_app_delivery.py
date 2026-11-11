"""Phase 2 (lecture delivery) in the app, over Vihan's deliverable C backend: views, choices, review actions, own links,
ratings, background jobs and the HTTP API. Runs on a temporary copy of runs/cs601-02 (no AI, no network)."""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest  # noqa: E402
import yaml  # noqa: E402

from profsagent.app import delivery as dv  # noqa: E402
from profsagent.config import RUNS  # noqa: E402

pytestmark = pytest.mark.skipif(not (RUNS / "cs601-02" / "delivery" / "lectures").exists(), reason="needs runs/cs601-02 with delivery results")


@pytest.fixture
def runs(tmp_path, monkeypatch):
    """A private runs/ folder holding cs601-02; every delivery module reads and writes there."""
    import shutil
    import profsagent.delivery.common as common
    import profsagent.delivery.review as review
    r = tmp_path / "runs"
    r.mkdir()
    shutil.copytree(RUNS / "cs601-02", r / "cs601-02", ignore=shutil.ignore_patterns("checkpoint.sqlite*", "llm_calls.jsonl"))
    monkeypatch.setattr(common, "RUNS", r)
    monkeypatch.setattr(dv, "RUNS", r)
    monkeypatch.setattr(review, "FEEDBACK", tmp_path / "delivery_feedback.json")
    return r


@pytest.fixture
def rid(runs):
    return dv.copy_example(runs)


def test_example_copy_leaves_the_source_alone(runs, rid):
    before = (runs / "cs601-02" / "delivery" / "survey.yaml").read_text(encoding="utf-8")
    c = dv.courses(runs)[0]
    assert c["run_id"] == rid and c["example"] and c["lectures"] == 27 and c["with_results"] == 3
    dv.save_choices(rid, "W05.L2", {"own_material": "yes", "assistance": "yes", "want_readings": "yes"})
    assert (runs / "cs601-02" / "delivery" / "survey.yaml").read_text(encoding="utf-8") == before


def test_view_has_the_guide_shapes(runs, rid):
    v = dv.view(rid, runs)
    assert len(v["lectures"]) == 27 and sorted(v["results"]) == ["W01.L1", "W01.L2", "W02.L1"] and v["kits"] == ["W01.L1", "W01.L2", "W02.L1"]
    r = v["results"]["W01.L1"]
    card = r["items"]["video"][0]
    assert {"key", "url", "title", "tier", "total", "scores", "rationale", "warnings", "review", "cover", "approved"} <= set(card)
    assert r["experts"]["experts"] and v["results"]["W02.L1"]["experts"] == {"same_as": "W01.L2"}
    assert v["material_connected"] == {"generate": True, "attach": False} and set(v["keys"]) == {"youtube", "openalex", "tavily"}


def test_choices_validation_and_when_c_starts(runs, rid):
    assert dv.save_choices(rid, "W05.L2", {})["errors"]["none"]
    assert "wants" in dv.save_choices(rid, "W05.L2", {"assistance": "yes"})["errors"]
    assert {"attach", "tasks"} <= set(dv.save_choices(rid, "W05.L2", {"attach_material": "yes"})["errors"])
    assert dv.save_choices(rid, "W05.L2", {"own_material": "yes"})["start_c"] is False                     # nothing for C
    out = dv.save_choices(rid, "W05.L2", {"own_material": "yes", "assistance": "yes", "want_readings": "yes"})
    assert out["start_c"] and not out["refresh"]                                                           # new search
    a = yaml.safe_load((runs / rid / "delivery" / "survey.yaml").read_text(encoding="utf-8"))["lectures"]["W05.L2"]
    assert a["assistance"] == "yes" and a["want_readings"] == "yes" and a["want_videos"] == "no" and a["guest_lecture"] == "no"
    same = dv.save_choices(rid, "W01.L1", {**{k: v for k, v in dv.view(rid, runs)["survey"]["W01.L1"].items()}, "note": "a note only"})
    assert same["start_c"] is False                                                                         # results kept
    changed = dv.save_choices(rid, "W01.L1", {**dv.view(rid, runs)["survey"]["W01.L1"], "want_practice": "yes"})
    assert changed["start_c"] and changed["refresh"]                                                       # C's wants changed


def test_review_approve_undo_reject_replace(runs, rid):
    first = dv.view(rid, runs)["results"]["W01.L1"]["items"]["video"][0]
    assert dv.review(rid, "W01.L1", "video", first["key"], "approve", "")["ok"]
    assert dv.view(rid, runs)["results"]["W01.L1"]["items"]["video"][0]["approved"]
    dv.undo_approve(rid, "W01.L1", "video", first["key"])
    assert not dv.view(rid, runs)["results"]["W01.L1"]["items"]["video"][0]["approved"]
    assert dv.review(rid, "W01.L1", "video", first["key"], "reject", "")["problem"]                     # reason required
    reserve_top = dv.view(rid, runs)["results"]["W01.L1"]["reserve"]["video"][0]["key"]
    dv.review(rid, "W01.L1", "video", first["key"], "replace", "Too long", first["title"])
    v = dv.view(rid, runs)
    keys = [x["key"] for x in v["results"]["W01.L1"]["items"]["video"]]
    assert first["key"] not in keys and reserve_top in keys                                                 # next-best took its place
    assert v["actions"]["W01.L1"][-1] == {**v["actions"]["W01.L1"][-1], "decision": "replace", "reason": "Too long", "title": first["title"]}
    expert = v["results"]["W01.L1"]["experts"]["experts"][0]
    dv.review(rid, "W01.L1", "experts", expert["key"], "approve", "")
    assert dv.view(rid, runs)["results"]["W01.L1"]["experts"]["experts"][0]["approved"]


def test_own_links_ratings_and_bulk(runs, rid):
    assert dv.own_link(rid, "W01.L1", "", "nope", "reading")["problem"]
    assert dv.own_link(rid, "W01.L1", "Notes", "https://example.org/n", "reading")["own"][0]["title"] == "Notes"
    assert dv.rate(rid, "W01.L1", "https://example.org/n", "Notes", 9)["problem"]
    out = dv.rate(rid, "W01.L1", "https://example.org/n", "Notes", 4)
    assert out["recorded"]["ratings_recorded"] == 1 and not (runs / rid / "delivery" / "feedback.yaml").exists()
    dv.rate(rid, "W01.L1", "https://example.org/n", "Notes", 5)
    agg = json.loads((runs.parent / "delivery_feedback.json").read_text(encoding="utf-8"))
    assert agg["unknown"] == {"n": 2, "sum": 9}                                                             # each rating counted once
    assert dv.view(rid, runs)["ratings"]["W01.L1"]["https://example.org/n"]["r"] == 5
    s = yaml.safe_load((runs / rid / "delivery" / "survey.yaml").read_text(encoding="utf-8"))
    for lid in ("W05.L1", "W05.L2"):
        s["lectures"][lid].update({k: None for k in dv.CHOICES})
    (runs / rid / "delivery" / "survey.yaml").write_text(yaml.safe_dump(s, allow_unicode=True), encoding="utf-8")
    dv.save_choices(rid, "W05.L1", {"own_material": "yes", "guest_lecture": "yes"})
    assert dv.bulk(rid, "W05.L1", "week")["applied"] == ["W05.L2"]
    assert dv.view(rid, runs)["survey"]["W05.L2"]["guest_lecture"] == "yes"


def test_material_for_chosen_weeks_only(runs, rid):
    s = yaml.safe_load((runs / rid / "delivery" / "survey.yaml").read_text(encoding="utf-8"))
    for lid in ("W05.L1", "W05.L2", "W06.L1"):
        s["lectures"][lid].update({k: None for k in dv.CHOICES + dv.WANTS})        # (old-format want_* answers count as choices)
    s["lectures"]["W05.L2"].update(own_material="yes", guest_lecture="yes")       # saved choices: kept, only added to
    (runs / rid / "delivery" / "survey.yaml").write_text(yaml.safe_dump(s, allow_unicode=True), encoding="utf-8")
    assert dv.for_weeks(rid, [5], False, False)["problem"] and dv.for_weeks(rid, [99], True, False)["problem"]
    out = dv.for_weeks(rid, [5], material=True, resources=False)
    assert [x["id"] for x in out["lectures"]] == ["W05.L1", "W05.L2"] and all(x["start_b"] for x in out["lectures"])
    v = dv.view(rid, runs)["survey"]
    assert v["W05.L1"]["generate_material"] == "yes" and v["W05.L1"]["assistance"] == "no"
    assert v["W05.L2"]["own_material"] == "yes" and v["W05.L2"]["guest_lecture"] == "yes" and v["W05.L2"]["generate_material"] == "yes"
    assert not v.get("W06.L1")                                                         # other weeks untouched
    both = dv.for_weeks(rid, [5], material=True, resources=True)
    assert all(x["start_c"] for x in both["lectures"]) and dv.view(rid, runs)["survey"]["W05.L1"]["want_videos"] == "yes"


def test_a_held_out_course_is_hidden_and_used_as_the_reference():
    from profsagent.app import formmap
    f = {"name": "Machine Learning", "description": "x" * 40, "hold_out": ["AI501", "cse 343"], "hold_out_domains": ["techtree.iiitd.edu.in"],
         "reference_course": "AI501___ECE363___ECE563___CSE343__CSE543"}
    _, cfg = formmap.to_pipeline(f)
    assert cfg["exclude_courses"] == ["AI501", "CSE343"] and cfg["blocklist"]["course_codes"] == ["AI501", "CSE343"]
    assert cfg["blocklist"]["domains"] == ["techtree.iiitd.edu.in"] and cfg["reference_course"].startswith("AI501")
    assert formmap.to_pipeline({"name": "X course", "description": "y" * 40})[1]["exclude_courses"] == []


def test_jobs_run_in_a_child_process_and_can_be_cancelled(runs, rid):
    ok = ("import json,sys; from pathlib import Path; d=Path(sys.argv[1]); "
          "(d/'app_step_result.json').write_text(json.dumps({'ok': {}}))")
    slow = "import time; time.sleep(60)"
    m = dv.DeliveryManager(runs=runs, step_cmd=lambda r, kind, af: [sys.executable, "-c", ok, str(runs / r / "delivery")])
    m.start()
    try:
        m.queue_recommend(rid, ["W05.L2"])
        t0 = time.time()
        while (dv.view(rid, runs)["jobs"]["lectures"]["W05.L2"]["state"] != "done") and time.time() - t0 < 20:
            time.sleep(0.1)
        assert dv.view(rid, runs)["jobs"]["lectures"]["W05.L2"]["state"] == "done"
        m.step_cmd = lambda r, kind, af: [sys.executable, "-c", slow]
        m.queue_recommend(rid, ["W06.L1"])
        while m.proc is None and time.time() - t0 < 20:
            time.sleep(0.05)
        proc = m.proc
        m.cancel(rid)
        proc.wait(timeout=10)
        assert proc.returncode is not None
    finally:
        m.stop()


def test_errors_are_explained():
    assert "quota" in dv._plain_error({"quota": True})
    assert "Nothing to search" in dv._plain_error({"type": "SystemExit", "message": "No lecture asked for anything yet"})


def test_attachments_are_kept_for_the_material_team(runs, rid):
    p = dv.save_attachment(rid, "W05.L2", "../../notes week5.pdf", b"%PDF-1.4 test")
    assert p == "delivery/attachments/W05.L2/notes week5.pdf" and (runs / rid / p).read_bytes().startswith(b"%PDF")
    assert dv.save_attachment(rid, "W05.L2", "notes week5.pdf", b"x").endswith("notes week5-1.pdf")       # never overwrites


def test_partial_lectures_are_flagged(runs, rid):
    p = runs / rid / "delivery" / "lectures" / "W01.L1.json"
    lec = json.loads(p.read_text(encoding="utf-8"))
    lec["partial"] = {"reason": "YouTube blocked transcript downloads", "videos_without_transcript": 2}
    p.write_text(json.dumps(lec), encoding="utf-8")
    assert dv.view(rid, runs)["results"]["W01.L1"]["partial"]["videos_without_transcript"] == 2
    assert dv.view(rid, runs)["results"]["W01.L2"]["partial"] is None


# ------------------------------------------------------------------ B: Parth's generated slides
EXAMPLE_DECK = Path(__file__).resolve().parents[1] / "eval" / "content_examples" / "cs601-02_W01.L1"


@pytest.fixture
def with_slides(runs, rid):
    """Parth's real W01.L1 deck (eval/content_examples) placed in the course, as generate_material leaves it."""
    import shutil
    if not EXAMPLE_DECK.exists():
        pytest.skip("needs eval/content_examples/cs601-02_W01.L1")
    d = runs / rid / "delivery" / "material" / "W01.L1"
    shutil.copytree(EXAMPLE_DECK, d, dirs_exist_ok=True)                  # the example copy may already carry Parth's decks
    m = json.loads((d / "material.json").read_text(encoding="utf-8"))
    m.update(status="draft", review=None, review_history=[])               # start from an unreviewed deck
    (d / "material.json").write_text(json.dumps(m), encoding="utf-8")
    return rid


def test_slides_summary_and_preview(runs, with_slides):
    rid = with_slides
    s = dv.view(rid, runs)["material"]["W01.L1"]
    assert s["status"] == "draft" and s["slides"] >= 10 and "slides.pptx" in s["files"]
    d = dv.material_detail(rid, "W01.L1")
    assert d["slides"][0]["number"] == 3                                   # numbered as in the .pptx (title, objectives first)
    assert any(sl.get("quiz") for sl in d["slides"]) and d["sources"]
    assert dv.material_detail(rid, "W05.L2") is None


def test_slides_review_through_parths_module(runs, with_slides):
    rid = with_slides
    assert "change" in dv.material_review(rid, "W01.L1", "redo", "")["problem"]          # redo needs instructions
    assert dv.material_review(rid, "W01.L1", "approve", "")["status"] == "approved"
    m = json.loads((runs / rid / "delivery" / "material" / "W01.L1" / "material.json").read_text(encoding="utf-8"))
    assert m["status"] == "approved" and m["review"]["decision"] == "approve"
    assert dv.material_review(rid, "W01.L1", "reject", "Using my own slides")["status"] == "rejected"
    assert dv.material_review(rid, "W05.L2", "approve", "")["problem"]                   # nothing generated there


def test_generate_starts_once_when_chosen(runs, rid, with_slides):
    out = dv.save_choices(rid, "W05.L2", {"own_material": "yes", "generate_material": "yes"})
    assert out["start_b"] and not out["start_c"]
    s = dv.view(rid, runs)["survey"]["W01.L1"]
    assert dv.save_choices(rid, "W01.L1", {**s, "generate_material": "yes"})["start_b"] is False      # slides already exist


def test_material_jobs_run_in_the_worker(runs, rid):
    ok = ("import json,sys; from pathlib import Path; d=Path(sys.argv[1]); "
          "(d/'app_step_result.json').write_text(json.dumps({'ok': {'slides': 21}}))")
    m = dv.DeliveryManager(runs=runs, step_cmd=lambda r, kind, af: [sys.executable, "-c", ok, str(runs / r / "delivery")])
    m.start()
    try:
        m.queue_material(rid, "W05.L2", {"note": "", "review": "ai"})
        t0 = time.time()
        while (dv.view(rid, runs)["jobs"].get("material", {}).get("W05.L2", {}).get("state") != "done") and time.time() - t0 < 20:
            time.sleep(0.1)
        j = dv.view(rid, runs)["jobs"]["material"]["W05.L2"]
        assert j["state"] == "done" and j["options"]["review"] == "ai"
    finally:
        m.stop()
    assert "protected" in dv._plain_error({"type": "ValueError", "message": "W01.L1: the professor approved these slides; pass force"}, "material")
