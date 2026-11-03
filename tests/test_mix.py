"""Deliverable C, the delivery mix (delivery/mix.py; doc "Lecture delivery mix — design proposal", 2 Nov; decisions 30):
the rules per part, the lecture-wide checks, D7's swaps within the rules, the professor's changes and approval, the
quiz and recap, and what B and the NotebookLM pack get. Offline: the AI, the sources and the simulation matcher are
replaced."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from profsagent.delivery import mix  # noqa: E402
from profsagent.delivery.models import LectureMix, MixChoice, MixChoices, Quiz, QuizQuestion  # noqa: E402

TEACH = "one two three four five six seven eight nine ten"


def seg(vid, start, end, minutes, verdict="teaches_fully", clarity=4, level=4):
    return {"video": f"Video {vid}", "video_id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "start": start, "end": end,
            "minutes": minutes, "verdict": verdict, "clarity": clarity, "level_fit": level}


def comp(lid, i, kind="concept", bloom=2, minutes=15, terms=("alpha",), title=None):
    return {"id": f"{lid}.C{i}", "lecture_id": lid, "title": title or f"Part {i}", "teaches": TEACH, "key_terms": list(terms),
            "kind": kind, "bloom": bloom, "lo_ids": ["LO1"], "minutes": minutes}


@pytest.fixture
def run(tmp_path, monkeypatch):
    """A course run with two lectures; returns a function that writes a lecture's components and timeline."""
    from profsagent.delivery import common
    from profsagent.delivery import survey as sv
    monkeypatch.setattr(common, "RUNS", tmp_path)
    rd = tmp_path / "r"
    d = rd / "delivery"
    (d / "lectures").mkdir(parents=True)
    (rd / "state.json").write_text(json.dumps({"cco_compact": {"course_name": "Course", "target_students": {"years": [3]}}, "level": 3}), encoding="utf-8")
    briefs = [{"lecture_id": lid, "topic_id": "T1", "topic": "Topic", "week": 1, "hours": 1.0, "novel": True, "module": "M",
               "learning_outcomes": [{"id": "LO1", "statement": "Explain things", "bloom_level": 2}], "builds_on": [], "leads_to": []}
              for lid in ("W01.L1", "W01.L2")]
    (d / "briefs.json").write_text(json.dumps(briefs), encoding="utf-8")
    monkeypatch.setattr(sv, "load", lambda run_id: {"lectures": {"W01.L1": {"confidence": 2}, "W01.L2": {"confidence": 2}}})
    monkeypatch.setattr(mix, "source_texts", lambda res: ["alpha beta gamma explained in depth"])
    monkeypatch.setattr(mix, "match_simulations", lambda comps: {})

    def write(lid, comps, timeline=(), reserved=(5, 5), sims=None):
        plans = json.loads((d / "components.json").read_text(encoding="utf-8")) if (d / "components.json").exists() else {}
        lec = {"lecture_id": lid, "minutes": sum(c["minutes"] for c in comps), "lecture_minutes": 60}
        if reserved is not None:
            lec["reserved"] = {"recap": reserved[0], "quiz": reserved[1]}
        p = plans.setdefault("T1", {"lectures": [], "components": []})
        p["lectures"] = [x for x in p["lectures"] if x["lecture_id"] != lid] + [lec]
        p["components"] = [c for c in p["components"] if c["lecture_id"] != lid] + list(comps)
        (d / "components.json").write_text(json.dumps(plans), encoding="utf-8")
        tl = [{"component": c["id"], "title": c["title"], "minutes": c["minutes"], "kind": c["kind"], "delivery": "notebooklm",
               "segments": []} for c in comps]
        for row in tl:
            for cid, segs in dict(timeline).items():
                if row["component"] == cid:
                    row["segments"], row["delivery"] = segs, "video"
        res = {"lecture_id": lid, "topic": "Topic", "timeline": tl, "clips": [], "items": {"video": [], "reading": [], "practice": []}}
        (d / "lectures" / f"{lid}.json").write_text(json.dumps({"lecture_id": lid, "topic": "Topic", "components": list(comps),
                                                                 "resources": res}), encoding="utf-8")
        if sims is not None:
            monkeypatch.setattr(mix, "match_simulations", lambda cs: sims)
    write.dir = d
    return write


def ways(m):
    return [p["way"] for p in m["parts"]]


# ------------------------------------------------------------------ the rules, part by part
def test_each_rule_picks_its_way_in_order(run):
    L = "W01.L2"
    cs = [comp(L, 1, kind="concept", minutes=10), comp(L, 2, kind="activity", bloom=3, minutes=10),
          comp(L, 3, kind="mechanism", minutes=10), comp(L, 4, kind="concept", minutes=10), comp(L, 5, kind="comparison", minutes=10,
                                                                                               terms=("zeta",))]
    run(L, cs, timeline={f"{L}.C3": [seg("a", "1:00", "10:00", 9.0)],                    # R2: fully, clear, 0.9 x the part
                         f"{L}.C4": [seg("b", "0:30", "7:00", 6.5, verdict="teaches_partly")]})   # R3: 65% of the part
    m = mix.propose("r", L, use_ai=False)
    assert ways(m) == ["slides", "in_class", "youtube", "youtube_bridge", "slides"]
    # C1 (first part) would be NotebookLM by R4, but the first part is taught live; C5's sources lack "zeta" -> slides
    assert m["parts"][0]["alternative"]["way"] == "notebooklm" and any(x["code"] == "L-FIRST" for x in m["checks"])
    assert [p["rule"] for p in m["parts"]][1:4] == ["R1", "R2", "R3"] and m["parts"][4]["uncovered"] == ["zeta"]
    assert m["parts"][3]["bridge"] == [] and m["parts"][2]["segments"][0]["start"] == "1:00"
    LectureMix(**m)                                                        # the file has the documented shape
    assert m["recap_minutes"] == 5 and m["quiz_minutes"] == 5 and m["totals"]["recap"] == 5


def test_a_matching_simulation_takes_a_mechanism_part(run):
    L = "W01.L2"
    cs = [comp(L, 1, minutes=25), comp(L, 2, kind="mechanism", bloom=3, minutes=25)]
    sim = {"id": "algorithms.graph.dijkstra", "url": None, "title": "Dijkstra step by step", "source": "catalogue", "score": 0.81}
    run(L, cs, sims={f"{L}.C2": [sim]})
    m = mix.propose("r", L, use_ai=False)
    assert m["parts"][1]["way"] == "simulation" and m["parts"][1]["rule"] == "R1b"
    assert m["parts"][1]["simulation"]["id"] == "algorithms.graph.dijkstra" and m["totals"]["simulation"] == 25
    assert m["preset"] == "full_mix" or "simulation" in mix.mcfg()["presets"][m["preset"]]


def test_a_confident_professor_teaches_live_and_a_course_style_limits_the_ways(run):
    from profsagent.delivery import survey as sv
    L = "W01.L2"
    cs = [comp(L, 1, minutes=25), comp(L, 2, kind="concept", minutes=25)]
    run(L, cs)
    sv.load = lambda run_id: {"lectures": {L: {"confidence": 5}}}
    briefs = json.loads((run.dir / "briefs.json").read_text(encoding="utf-8"))
    for b in briefs:
        b["novel"] = False
    (run.dir / "briefs.json").write_text(json.dumps(briefs), encoding="utf-8")
    m = mix.propose("r", L, use_ai=False)
    assert ways(m) == ["slides", "slides"] and "confidence 5" in m["parts"][1]["reason"] and m["preset"] == "slides_only"
    mix.course_style("r", "flipped")
    run(L, cs, timeline={f"{L}.C2": [seg("a", "0:00", "24:00", 24.0)]})
    m = mix.propose("r", L, use_ai=False)
    assert m["preset"] == "flipped" and m["parts"][1]["way"] == "youtube" and m["parts"][1]["when"] == "pre_class"
    assert m["totals"]["video_in_class"] == 0 and m["totals"]["video_pre_class"] == 24


# ------------------------------------------------------------------ the lecture as a whole
def test_video_beyond_the_cap_and_long_clips_go_before_class(run):
    L = "W01.L2"
    cs = [comp(L, 1, minutes=10)] + [comp(L, i, kind="mechanism", minutes=15) for i in (2, 3, 4)]
    tl = {f"{L}.C2": [seg("a", "0:00", "7:00", 7.0, verdict="teaches_partly"), seg("a2", "0:00", "7:00", 7.0, verdict="teaches_partly")],
          f"{L}.C3": [seg("b", "0:00", "14:00", 14.0)], f"{L}.C4": [seg("c", "0:00", "12:00", 12.0)]}
    run(L, cs, timeline=tl)
    m = mix.propose("r", L, use_ai=False)
    assert ways(m) == ["slides", "youtube_bridge", "youtube", "youtube"]
    assert m["totals"]["video_share"] <= mix.mcfg()["lecture"]["video_share_max"]
    assert {p["component"] for p in m["parts"] if p["when"] == "pre_class"} >= {f"{L}.C3", f"{L}.C4"}     # clips over 8 min
    assert any(x["code"] == "L-LONG" for x in m["checks"])


def test_at_most_two_notebooklm_videos_and_few_switches(run):
    L = "W01.L2"
    cs = [comp(L, i, minutes=10) for i in range(1, 6)]
    run(L, cs)
    m = mix.propose("r", L, use_ai=False)
    assert ways(m).count("notebooklm") == 2 and m["parts"][0]["way"] == "slides"
    assert mix._switches(m["parts"]) <= mix.mcfg()["lecture"]["max_switches"]


def test_locked_rows_and_professor_choices_are_never_changed_by_the_program(run):
    L = "W01.L2"
    cs = [comp(L, i, minutes=10) for i in range(1, 6)]
    run(L, cs)
    m = mix.propose("r", L, locked={f"{L}.C1": "notebooklm", f"{L}.C2": "notebooklm", f"{L}.C3": "notebooklm"}, use_ai=False)
    assert ways(m)[:3] == ["notebooklm"] * 3 and all(p["locked"] for p in m["parts"][:3])
    assert any(x["code"] == "L-NLM" for x in m["checks"]) and any(x["code"] == "L-FIRST" for x in m["checks"])
    again = mix.propose("r", L, use_ai=False)                     # locks in the file stay on the next proposal
    assert ways(again)[:3] == ["notebooklm"] * 3


def test_an_old_plan_gives_up_minutes_for_the_recap_and_quiz(run):
    L = "W01.L2"
    cs = [comp(L, 1, minutes=30), comp(L, 2, kind="mechanism", minutes=30)]
    run(L, cs, timeline={f"{L}.C2": [seg("a", "0:00", "25:00", 25.0)]}, reserved=None)
    m = mix.propose("r", L, use_ai=False)
    assert m["recap_minutes"] + m["quiz_minutes"] == 10 and sum(p["minutes"] for p in m["parts"]) == 50
    assert m["parts"][0]["minutes"] == 20 and m["parts"][1]["minutes"] == 30          # taken from the slides part, not the clip
    assert any(x["code"] == "L-RESERVE" for x in m["checks"])


# ------------------------------------------------------------------ D7
def test_d7_may_change_a_way_only_within_the_rules(run, monkeypatch):
    from profsagent.delivery import resources
    L = "W01.L2"
    cs = [comp(L, 1, minutes=20), comp(L, 2, kind="mechanism", minutes=20), comp(L, 3, kind="concept", minutes=20)]
    run(L, cs, timeline={f"{L}.C2": [seg("a", "1:00", "19:00", 18.0)]})
    seen = {}

    def fake(llm, pid, ctx, model_cls, run_id, log):
        seen["ctx"] = ctx
        return MixChoices(parts=[MixChoice(id=f"{L}.C1", way="youtube", reason="r1", because="fit"),        # no video: refused
                                 MixChoice(id=f"{L}.C2", way="slides", reason="I teach it", because="note"),
                                 MixChoice(id=f"{L}.C3", way="in_class", reason="r3", because="keep")])   # "keep" with a change: refused
    monkeypatch.setattr(resources, "llm_call", fake)
    m = mix.propose("r", L, note="I'll teach part 2 myself", use_ai=True)
    assert ways(m) == ["slides", "slides", "notebooklm"] and m["parts"][1]["rule"] == "D7-note"
    assert m["parts"][1]["reason"] == "I teach it" and m["proposed_by"] == "rules + D7"
    assert seen["ctx"]["note"] == "I'll teach part 2 myself" and "youtube" in seen["ctx"]["parts"][1]["allowed"]
    m = mix.propose("r", L, note="", use_ai=True)                               # without a note, a "note" change is refused
    assert m["parts"][1]["way"] == "youtube"


# ------------------------------------------------------------------ the professor: changes, preferences, approval
def test_professor_changes_are_checked_logged_and_learnt(run, monkeypatch):
    L = "W01.L2"
    cs = [comp(L, 1, minutes=30), comp(L, 2, kind="comparison", minutes=30)]
    run(L, cs)
    mix.propose("r", L, use_ai=False)
    bad = mix.save("r", L, {f"{L}.C2": {"way": "youtube"}})
    assert "no checked video" in bad["errors"][f"{L}.C2"]
    ok = mix.save("r", L, {f"{L}.C2": {"way": "in_class", "locked": True}})["mix"]
    assert ok["parts"][1]["way"] == "in_class" and ok["parts"][1]["set_by"] == "professor" and ok["status"] == "proposed"
    rows = [json.loads(x) for x in mix.changes_path("r").read_text(encoding="utf-8").splitlines()]
    assert rows[-1]["from"] == "notebooklm" and rows[-1]["to"] == "in_class" and rows[-1]["kind"] == "comparison"
    with mix.changes_path("r").open("a", encoding="utf-8") as f:                  # 20 changes: comparisons go in class
        for _ in range(19):
            f.write(json.dumps({"kind": "comparison", "from": "slides", "to": "in_class"}) + "\n")
    assert mix.preferences("r")["comparison"]["way"] == "in_class"
    m = mix.propose("r", L, use_ai=False)
    assert m["parts"][1]["rule"] in ("P", "professor") and m["parts"][1]["way"] == "in_class"


def test_approval_makes_the_pack_and_the_quiz_with_a_recap(run, monkeypatch):
    from profsagent.delivery import resources
    for L in ("W01.L1", "W01.L2"):
        run(L, [comp(L, 1, minutes=20), comp(L, 2, kind="mechanism", minutes=20),
                comp(L, 3, minutes=10, terms=("zeta",))], timeline={f"{L}.C2": [seg("a" + L, "1:00", "19:00", 18.0)]})

    def fake(llm, pid, ctx, model_cls, run_id, log):
        assert pid == "D8" and ctx["n_questions"] == 4
        cid = [p["id"] for p in ctx["parts"]]
        return Quiz(questions=[QuizQuestion(component=cid[0], question="q1", options=["a", "b", "c", "d"], answer="b"),
                               QuizQuestion(component=cid[1], question="q2", options=["a", "b", "c", "d"], answer="A"),
                               QuizQuestion(component=cid[2], question="q3", options=["a", "b", "c", "d"], answer="C"),
                               QuizQuestion(component=cid[0], question="q4", options=["a", "a", "c", "d"], answer="A"),   # dropped
                               QuizQuestion(component="X.C9", question="q5", options=[], answer="x")])                   # dropped
    monkeypatch.setattr(resources, "llm_call", fake)
    for L in ("W01.L1", "W01.L2"):
        mix.propose("r", L, use_ai=False)
        m = mix.approve("r", L, by="Prof")["mix"]
        assert m["status"] == "approved" and m["approved_by"] == "Prof" and m["materials"]["quiz_questions"] == 3
    q = json.loads((run.dir / "quiz" / "W01.L2.json").read_text(encoding="utf-8"))
    right = {"q1": "b", "q2": "a", "q3": "c"}                    # options are shuffled; the answer letter follows its option
    assert all(x["options"]["ABCD".index(x["answer"])] == right[x["question"]] for x in q["questions"])
    assert len(q["questions"]) == 3 and any("questions" in p for p in q["problems"])
    assert [x["component"] for x in q["recap"]] == ["W01.L1.C1", "W01.L1.C2", "W01.L1.C3"]
    first = json.loads((run.dir / "quiz" / "W01.L1.json").read_text(encoding="utf-8"))
    assert first["recap"] == [] or mix.load("r", "W01.L1")["recap_minutes"]
    md = (run.dir / "notebooklm" / "W01.L2.md").read_text(encoding="utf-8")
    nlm = [p["component"] for p in m["parts"] if p["way"] == "notebooklm"]
    assert md.count("### W01.L2.C") == len(nlm) and "approved by Prof" in md
    lec = json.loads((run.dir / "lectures" / "W01.L2.json").read_text(encoding="utf-8"))
    assert lec["resources"]["notebooklm"]["components"] == nlm
    assert "## Answers" in (run.dir / "quiz" / "W01.L2.md").read_text(encoding="utf-8")


def test_b_gets_the_approved_ways_and_the_recap_and_quiz(run, monkeypatch):
    from profsagent.content import generate as G
    L = "W01.L2"
    run(L, [comp(L, 1, minutes=25), comp(L, 2, kind="mechanism", minutes=25)], timeline={f"{L}.C2": [seg("a", "1:00", "23:00", 22.0)]})
    mix.propose("r", L, use_ai=False)
    monkeypatch.setattr(mix, "materials", lambda run_id, lid, log=None: {})
    mix.approve("r", L)
    out = G.outline("r", {"lecture_id": L})
    assert [x["id"] for x in out] == [f"{L}.RECAP", f"{L}.C1", f"{L}.C2", f"{L}.QUIZ"]
    assert out[2]["way"] == "youtube" and out[2]["delivered_by"] == "video" and "1:00" in out[2]["clip"]
    assert out[1]["delivered_by"] == out[1]["way"] == "slides" and sum(x["minutes"] for x in out) == 60


def test_d5_keeps_minutes_for_the_recap_and_quiz(run, monkeypatch):
    from profsagent.delivery import components as cp
    from profsagent.delivery import resources

    def fail(*a, **k):
        raise RuntimeError("no model")
    monkeypatch.setattr(resources, "llm_call", fail)
    briefs = json.loads((run.dir / "briefs.json").read_text(encoding="utf-8"))
    briefs[1]["hours"] = 2.0
    st = {"cco_compact": {"course_name": "C"}, "level": 3}
    plan = cp.plan_topic(None, st, briefs, "r", lambda *_: None)
    got = {x["lecture_id"]: x for x in plan["lectures"]}
    assert got["W01.L1"]["reserved"] == {"recap": 0, "quiz": 5} and got["W01.L1"]["minutes"] == 55   # first lecture: no recap
    assert got["W01.L2"]["reserved"] == {"recap": 5, "quiz": 10} and got["W01.L2"]["minutes"] == 105
    for lid, x in got.items():
        assert sum(c["minutes"] for c in plan["components"] if c["lecture_id"] == lid) == x["minutes"]
    assert mix.reserve_for(30, False) == (0, 0) and mix.reserve_for(45, False) == (5, 5)


def test_source_coverage_reads_phrases_and_words():
    cov, missing = mix.coverage(["Model Context Protocol", "lazy tool registration", "JSON-RPC"],
                                ["The model context protocol uses json-rpc messages; tools register at start."])
    assert cov == 0.67 and missing == ["lazy tool registration"]
    assert mix.coverage([], ["x"]) == (None, [])
