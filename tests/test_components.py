"""Deliverable C, component-based delivery (2026-11-01): component plans, video segments, NotebookLM packs and the
guest-speaker selection rules. Offline: no API calls (the AI and the embedder are replaced where needed)."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from profsagent.delivery import components as cp  # noqa: E402
from profsagent.delivery import segments as sg  # noqa: E402


# ------------------------------------------------------------------ component plans
def test_minutes_are_fitted_to_the_lecture_in_whole_steps():
    got = cp._fit_minutes([12, 18, 33], 60)
    assert got and sum(got) == 60 and all(m % 5 == 0 and 5 <= m <= 30 for m in got)
    assert cp._fit_minutes([10], 60) is None                        # one component cannot fill an hour (max 30)
    assert cp._fit_minutes([10, 10], 5) is None                     # two components cannot fit in 5 minutes (min 5 each)


def test_check_plan_repairs_minutes_and_lists_what_it_cannot():
    lectures = [{"lecture_id": "W01.L2", "minutes": 60}, {"lecture_id": "W02.L1", "minutes": 120}]
    comps = [{"lecture_id": "W01.L2", "title": "a", "teaches": "one two three four five six seven eight nine", "minutes": 25, "lo_ids": ["LO1"]},
             {"lecture_id": "W01.L2", "title": "b", "teaches": "one two three four five six seven eight nine", "minutes": 25, "lo_ids": ["X"]}]
    got, problems = cp.check_plan(comps, lectures, ["LO1", "LO2"])
    assert [c["minutes"] for c in got] == [30, 30] and got[0]["minutes_proposed"] == 25
    assert got[1]["lo_ids"] == []                                    # an unknown LO id is dropped
    assert any("W02.L1 has no components" in p for p in problems) and any("LO2" in p for p in problems)


def test_fallback_plan_adds_up_per_lecture():
    group = [{"lecture_id": "W01.L1", "topic": "T", "hours": 2.0,
              "learning_outcomes": [{"id": "LO1", "statement": "Explain {n} of {m} things", "bloom_level": 2}]},
             {"lecture_id": "W02.L1", "topic": "T", "hours": 0.25, "learning_outcomes": []}]
    plan = cp.fallback_plan(group)
    for lid, total in (("W01.L1", 120), ("W02.L1", 15)):
        assert sum(c["minutes"] for c in plan if c["lecture_id"] == lid) == total
    assert "{n}" not in plan[0]["teaches"]


# ------------------------------------------------------------------ segments
def test_chapters_need_a_real_chapter_list():
    d = "Intro\n0:00 Intro\n1:30 What MCP is\n4:12 How tools are listed\n10:05 Demo"
    ch = sg.chapters(d, 900)
    assert [c["start"] for c in ch] == [0, 90, 252, 605] and ch[-1]["end"] == 900 and ch[2]["title"] == "How tools are listed"
    assert sg.chapters("1:30 only one\n4:00 two", 600) == []         # YouTube needs 0:00 and at least three
    assert sg.secs("1:02:03") == 3723 and sg.secs("12:30") == 750 and sg.secs("x") is None


def test_notebooklm_pack_has_prompts_only_for_parts_without_a_video():
    from profsagent.delivery.notebooklm import pack
    st = {"cco_compact": {"course_name": "Course", "target_students": {"years": [3, 4]}}, "level": 6}
    b = {"lecture_id": "W01.L2", "week": 1, "topic": "MCP", "learning_outcomes": [{"statement": "Use {n} of {m} tools"}],
         "builds_on": [], "leads_to": [{"topic": "Agents", "week": 2}]}
    comps = [{"id": "W01.L2.C1", "title": "What MCP is", "teaches": "t1", "key_terms": ["host"], "minutes": 10, "kind": "concept"},
             {"id": "W01.L2.C2", "title": "Tool discovery", "teaches": "t2", "key_terms": ["tools/list"], "minutes": 20, "kind": "mechanism"}]
    tl = [{"component": "W01.L2.C1", "delivery": "video"}, {"component": "W01.L2.C2", "delivery": "notebooklm"}]
    md, summary = pack(st, b, comps, [], tl, {"video": [{"title": "V", "url": "https://www.youtube.com/watch?v=x&t=30s"}]})
    assert summary["components"] == ["W01.L2.C2"] and "### W01.L2.C2" in md and "### W01.L2.C1" not in md
    assert "https://www.youtube.com/watch?v=x)" in md                # the source link is the whole video
    assert "most tools" in md and "{n}" not in md and "Quiz" in md and "Flashcards" in md and "tools/list" in md


# ------------------------------------------------------------------ guest speakers
def test_select_lists_iiitd_first_and_one_per_institution_and_paper(monkeypatch):
    from profsagent.delivery import experts as ex
    monkeypatch.setattr(ex, "xcfg", lambda: {"top_n": {"min": 1, "max": 7}, "diversity": {
        "min_industry": 0, "min_academic": 0, "max_same_country": 9, "max_same_affiliation": 1, "one_per_paper": True, "iiitd_first": 2}})
    p = lambda n, aff, total, kind="academic", paper="P0": {"name": n, "affiliation": aff, "total": total, "kind": kind, "country": "IN",  # noqa: E731
                                                            "evidence": [{"kind": "paper", "title": paper}]}
    cands = [p("A", "Univ X", 0.9, paper="P1"), p("B", "Univ X", 0.85, paper="P2"), p("C", "Univ Y", 0.8, paper="P1"),
             p("D", "Univ Z", 0.7, paper="P3"), {**p("I", "IIIT-Delhi", 0.5, kind="iiitd", paper="P4"), "note": {"fit": "strong"}},
             {**p("J", "IIIT-Delhi", 0.6, kind="iiitd", paper="P5"), "note": {"fit": "moderate"}}]
    got = [e["name"] for e in ex.select(cands)]
    # I first (IIIT-D, strong fit); B: same university as A; C: co-author of A's paper; J: a second IIIT-D person
    assert got == ["I", "A", "D"]


def test_affiliation_role_split_and_short_names():
    from profsagent.delivery.experts import _split_affiliation
    from profsagent.delivery.sources import short_name
    assert _split_affiliation("Associate Professor of Computer Science, Singapore Management University") == \
        ("Associate Professor of Computer Science", "Singapore Management University")
    assert _split_affiliation("Microsoft Research") == (None, "Microsoft Research")
    assert short_name("Christoph Treude") == "c treude" and short_name("C Treude") == "c treude"


def test_for_window_gives_a_class_the_components_of_its_minutes(tmp_path, monkeypatch):
    import json
    from profsagent.delivery import common
    monkeypatch.setattr(common, "RUNS", tmp_path)
    d = tmp_path / "r" / "delivery"
    d.mkdir(parents=True)
    comps = [{"id": f"W01.L1.C{i}", "lecture_id": "W01.L1", "minutes": m} for i, m in enumerate([30, 30, 60], 1)]
    (d / "components.json").write_text(json.dumps({"T": {"components": comps}}), encoding="utf-8")
    got = cp.for_window("r", "W01.L1", 45, 30)          # a class that starts 45 min into the lecture, for 30 min
    assert [c["id"] for c in got] == ["W01.L1.C2", "W01.L1.C3"] and got[0]["minutes_here"] == 15 and got[1]["from_min"] == 60
    assert [c["id"] for c in cp.for_window("r", "W01.L1")] == ["W01.L1.C1", "W01.L1.C2", "W01.L1.C3"]


def test_partly_taught_parts_get_a_gap_and_a_notebooklm_prompt():
    from profsagent.delivery.notebooklm import pack
    comps = [{"id": "L.C1", "title": "Handshake", "teaches": "the initialize handshake", "minutes": 15}]
    tl = [{"delivery": "video", "gap": {"video_minutes": 2.0, "missing": ["initialized notification"]}}]   # results from before 10 Nov
    st = {"cco_compact": {"course_name": "C"}, "level": 6}
    b = {"lecture_id": "L", "week": 1, "topic": "MCP", "learning_outcomes": [], "builds_on": [], "leads_to": []}
    row = {**tl[0], "component": "L.C1", "segments": [{"video": "V", "start": "0:00", "end": "2:00"}]}
    md, summary = pack(st, b, [{**comps[0], "key_terms": []}], [], [row], {})
    assert summary["components"] == ["L.C1"] and "initialized notification" in md and "leaves out" in md


def test_b_gets_the_components_of_its_class_with_how_each_is_delivered(tmp_path, monkeypatch):
    import json
    from profsagent.content import generate as G
    from profsagent.delivery import common
    monkeypatch.setattr(common, "RUNS", tmp_path)
    d = tmp_path / "r" / "delivery"
    (d / "lectures").mkdir(parents=True)
    comps = [{"id": f"W03.L1.C{i}", "lecture_id": "W03.L1", "title": f"t{i}", "teaches": "x", "minutes": 30} for i in (1, 2, 3, 4)]
    (d / "components.json").write_text(json.dumps({"T": {"components": comps}}), encoding="utf-8")
    tl = [{"component": "W03.L1.C3", "delivery": "video", "segments": [{"video": "V", "start": "1:00", "end": "9:00"}]}]
    (d / "lectures" / "W03.L1.json").write_text(json.dumps({"resources": {"timeline": tl}}), encoding="utf-8")
    # the second class of the week teaches the brief's minutes 60-120 in 90 class minutes
    s = {"lecture_id": "W03.S2", "parts": [{"lecture_id": "W03.L1", "minutes": 90, "brief_from_min": 60, "brief_minutes": 60}]}
    out = G.outline("r", s)
    assert [x["id"] for x in out] == ["W03.L1.C3", "W03.L1.C4"] and [x["minutes"] for x in out] == [45, 45]
    assert out[0]["delivered_by"] == "video" and "1:00–9:00" in out[0]["clip"] and out[1]["delivered_by"] == "slides"


def test_sessions_record_where_each_part_sits_in_its_brief():
    import json
    from profsagent.content.sessions import build_sessions
    st_path = ROOT / "runs" / "cs601-02" / "state.json"
    if not st_path.exists():
        return
    st = json.loads(st_path.read_text(encoding="utf-8"))
    seen: dict[str, int] = {}
    for s in build_sessions(st, 2, 90):
        for p in s["parts"]:
            assert p["brief_from_min"] == seen.get(p["lecture_id"], 0)     # parts of a brief follow each other
            seen[p["lecture_id"]] = p["brief_from_min"] + p["brief_minutes"]


def test_short_lists_are_filled_from_people_who_passed_every_check(monkeypatch):
    from profsagent.delivery import experts as ex
    monkeypatch.setattr(ex, "xcfg", lambda: {"top_n": {"min": 3, "max": 7}, "diversity": {
        "min_industry": 0, "min_academic": 0, "max_same_country": 9, "max_same_affiliation": 1, "one_per_paper": True, "iiitd_first": 2}})
    p = lambda n, total, paper: {"name": n, "affiliation": "Univ X", "total": total, "kind": "academic", "country": "IN",  # noqa: E731
                                 "evidence": [{"kind": "paper", "title": paper}]}
    got = [e["name"] for e in ex.select([p("A", 0.9, "P1"), p("B", 0.8, "P2"), p("C", 0.7, "P3"), p("D", 0.6, "P4")])]
    assert got == ["A", "B", "C"]           # one per university first (A), then filled to the minimum of 3


def test_scholar_titles_and_roles_are_read_robustly():
    from profsagent.delivery.experts import _same_titles, _split_affiliation
    assert _split_affiliation("Assistant Professor at Harokopio University of Athens") == ("Assistant Professor", "Harokopio University of Athens")
    assert _same_titles(["Production Machine Learning Pipelines"],
                        ["Production machine learning pipelines: Empirical analysis and optimization opportunities"])
    assert not _same_titles(["AI"], ["AI-assisted code generation"])
