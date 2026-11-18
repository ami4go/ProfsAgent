"""Deterministic parts of delivery mode 2 (no network, no AI): plan checks, evidence texts, quote checks, assembly."""
from profsagent.ytlecture import assemble, evidence as E, models as Mx, tools as T
from profsagent.ytlecture.agents import check_plan, fix_plan


def _part(title, minutes, n=4):
    return {"title": title, "teaches": "x", "must_cover": [f"p{i}" for i in range(n)], "minutes": minutes, "kind": "concept",
            "search_phrases": [title]}


def test_plan_checks_and_fix():
    plan = Mx.TopicPlan(fast_moving=True, level_note="", lectures=[Mx.LecturePlan(lecture_id="W01.L1", parts=[
        Mx.Part(title="A", teaches="t", must_cover=["a", "b", "c"], minutes=30, search_phrases=["a"]),
        Mx.Part(title="B", teaches="t", must_cover=["a", "b", "c"], minutes=30, search_phrases=["b"]),
        Mx.Part(title="C", teaches="t", must_cover=["a", "b", "c"], minutes=30, search_phrases=["c"])])])
    lecs = [{"lecture_id": "W01.L1", "slot_minutes": 60}]
    errs = check_plan(plan, lecs)
    assert any("add up to 90" in e for e in errs)
    fixed = fix_plan(plan, lecs)
    tot = sum(p["minutes"] for p in fixed["lectures"][0]["parts"])
    assert 0.85 * 51 <= tot <= 1.1 * 51                     # rescaled to fill_target (0.85) of the slot


def test_plan_wrong_lectures_reported():
    plan = Mx.TopicPlan(fast_moving=False, level_note="", lectures=[Mx.LecturePlan(lecture_id="W09.L9", parts=[])])
    errs = check_plan(plan, [{"lecture_id": "W01.L1", "slot_minutes": 60}])
    assert any("lectures must be exactly" in e for e in errs)


ROWS = [{"start": float(t), "dur": 10.0, "text": f"sentence number {t // 10} about the harness loop and tool calls"} for t in range(0, 600, 10)]


def test_lines_skim_snap():
    ls = E.lines(ROWS, 20.0)
    assert ls[0][0] == 0 and ls[1][0] == 20
    assert E.skim(ROWS).count("\n") < len(ROWS) // 3
    assert E.snap(ROWS, 123, "start") == 120
    assert E.snap(ROWS, 123, "end") == 130


def test_quote_near_finds_and_rejects():
    rows = [{"start": 0, "dur": 5, "text": "welcome everyone"}, {"start": 5, "dur": 5, "text": "so the agent harness calls the model in a loop"},
            {"start": 10, "dur": 5, "text": "and feeds tool results back"}]
    assert E.quote_near("the agent harness calls the model in a loop", rows, 6) == 5
    assert E.quote_near("completely unrelated words about cooking pasta tonight", rows, 6) is None


def test_secs_and_ts():
    assert E.secs("1:02:03") == 3723 and E.secs("4:05") == 245 and E.secs("abc") is None
    assert E.ts(3723) == "1:02:03" and E.ts(245) == "4:05"


def test_youtube_ids_in():
    vids, lists = T.youtube_ids_in('<a href="https://www.youtube.com/watch?v=sTdz6PZoAnw&list=PLyzOVJj3bHQunmnnTXrNbZnBaCA-ieK4L">'
                                   ' https://youtu.be/LCEmiRjPEtQ ')
    assert vids == ["sTdz6PZoAnw", "LCEmiRjPEtQ"] and lists == ["PLyzOVJj3bHQunmnnTXrNbZnBaCA-ieK4L"]


def _clip(video, part, a, b, rating=4, cov=0.8, ev="captions", standalone=True, recommend=True):
    return {"video": video, "part": part, "a": a, "b": b, "covers": [0, 1], "treatment": "explains", "standalone": standalone,
            "level": "right", "rating": rating, "concerns": "", "summary": "s", "evidence": ev, "reader": "gemini:x",
            "quote_notes": [], "check": {"coverage": cov, "standalone": standalone, "accurate": True, "recommend": recommend,
                                         "issue": "", "checker": "nvidia:y"}}


VIDEOS = {"v1": {"id": "v1", "title": "Lecture", "tier": 1, "published": "2026-01-01T00:00:00Z"},
          "v2": {"id": "v2", "title": "Tutorial", "tier": 3, "published": "2025-06-01T00:00:00Z"},
          "v3": {"id": "v3", "title": "Old", "tier": 2, "published": "2019-01-01T00:00:00Z"}}


def test_choose_fills_parts_in_order_without_overlap():
    lec = {"lecture_id": "W01.L1", "slot_minutes": 60, "parts": [_part("A", 15), _part("B", 15), _part("C", 15)]}
    clips = [_clip("v1", 0, 0, 840), _clip("v1", 1, 800, 1700),            # overlaps the first by 40 s -> not both
             _clip("v2", 1, 100, 1000, rating=3), _clip("v1", 2, 2000, 2900), _clip("v2", 2, 0, 600, recommend=False)]
    out = assemble.choose(lec, clips, VIDEOS, fast=False, taken=[])
    picked = [(k["video"], k["part"], k["a"]) for pp in out["plan"] for k in pp["clips"]]
    assert ("v1", 0, 0) in picked and ("v1", 2, 2000) in picked
    assert ("v1", 1, 800) not in picked and ("v2", 1, 100) in picked
    assert not out["gaps"] and out["status"] == "ready"
    assert all(k["video"] != "v2" or k["part"] != 2 for pp in out["plan"] for k in pp["clips"])   # gated clip never chosen


def test_choose_reports_gap_and_fast_moving_gate():
    lec = {"lecture_id": "W01.L1", "slot_minutes": 60, "parts": [_part("A", 20), _part("B", 20)]}
    clips = [_clip("v1", 0, 0, 1200), _clip("v3", 1, 0, 1200)]
    out = assemble.choose(lec, clips, VIDEOS, fast=True, taken=[])
    assert out["gaps"] == [1]
    assert "changes fast" in clips[1]["gate"]


def test_taken_clips_not_repeated_across_lectures():
    lec = {"lecture_id": "W02.L1", "slot_minutes": 30, "parts": [_part("A", 12)]}
    taken = [_clip("v1", 0, 0, 700)]
    out = assemble.choose(lec, [_clip("v1", 0, 10, 700)], VIDEOS, fast=False, taken=taken)
    assert out["gaps"] == [0]


def test_chapters_only_scores_lower():
    p = _part("A", 10)
    s1, _ = assemble.score(_clip("v1", 0, 0, 600), VIDEOS["v1"], p, False)
    s2, why = assemble.score(_clip("v1", 0, 0, 600, ev="chapters"), VIDEOS["v1"], p, False)
    assert s2 < s1 and "placed from chapters only" in why


def test_tier_lookup():
    assert T.tier("Missing Semester") == 1 and T.tier("IBM Technology") == 2 and T.tier("Some Random Channel") == 4


def test_duplicate_plans_are_split_across_lectures():
    parts = [Mx.Part(title=t, teaches="t", must_cover=["a", "b", "c"], minutes=9, search_phrases=[t]) for t in "ABCDEF"]
    plan = Mx.TopicPlan(fast_moving=True, level_note="", lectures=[Mx.LecturePlan(lecture_id="W02.L2", parts=parts),
                                                                  Mx.LecturePlan(lecture_id="W03.L1", parts=parts)])
    out = fix_plan(plan, [{"lecture_id": "W02.L2", "slot_minutes": 60}, {"lecture_id": "W03.L1", "slot_minutes": 60}])
    a, b = ([p["title"] for p in l["parts"]] for l in out["lectures"])
    assert a == ["A", "B", "C"] and b == ["D", "E", "F"]


def test_short_tier_names_match_whole_words():
    assert T.tier("MIT OpenCourseWare") == 1 and T.tier("IIT Madras") == 1
    assert T.tier("Kent Smith Codes") == 4


def test_extras_fill_up_to_target_after_planned_parts():
    lec = {"lecture_id": "W01.L1", "slot_minutes": 60, "parts": [_part("Agent loop", 25), _part("Context windows", 26)]}
    clips = [_clip("v1", 0, 0, 600), _clip("v1", 1, 700, 1300)]                     # 20 min planned-part video
    for i, (a, b) in enumerate([(2000, 2900), (3000, 3600), (4000, 4900)]):         # 15 + 10 + 15 min of extras
        k = _clip("v1", -1, a, b, rating=5, cov=0.9)
        k["extra_title"] = ["Tool calls explained", "Context compaction", "Subagents"][i]
        clips.append(k)
    out = assemble.choose(lec, clips, VIDEOS, fast=False, taken=[])
    planned = [pp for pp in out["plan"] if pp["part"] >= 0]
    extras = [pp for pp in out["plan"] if pp["part"] == -1]
    assert [len(pp["clips"]) for pp in planned] == [1, 1] and extras
    assert out["total_s"] <= 0.95 * 3600 and out["total_s"] >= 0.85 * 3600 - 900
    assert out["gaps"] == []


def test_topup_grows_well_taught_parts_when_others_are_empty():
    lec = {"lecture_id": "W01.L1", "slot_minutes": 60, "parts": [_part("A", 15), _part("B", 15), _part("C", 15)]}
    clips = [_clip("v1", 0, 0, 900), _clip("v2", 0, 0, 600, rating=5), _clip("v1", 0, 1000, 1600, rating=5),
             _clip("v1", 1, 2000, 2900)]                                            # part C has no video at all
    clips[0]["check"]["points"] = {"0": 1.0}
    clips[1]["check"]["points"] = {"0": 1.0}                                        # v2 repeats point 0: never topped up
    clips[2]["check"]["points"] = {"1": 1.0}                                        # same video, continues: allowed
    out = assemble.choose(lec, clips, VIDEOS, fast=False, taken=[])
    a = next(pp for pp in out["plan"] if pp["part"] == 0)
    assert out["gaps"] == [2]
    assert sum(k["b"] - k["a"] for k in a["clips"]) > 1.6 * 900                     # beyond the normal per-part cap
    assert sum(k["b"] - k["a"] for k in a["clips"]) <= 2.0 * 900
    assert all(k["video"] == "v1" for k in a["clips"])
    assert out["total_s"] <= 0.95 * 3600


def test_recency_and_caption_inaccuracies_are_not_vetoes():
    k = _clip("v1", 0, 0, 900)
    k["check"] |= {"accurate": False, "issue": "Speaker incorrectly states SSE is deprecated"}
    assert assemble.gate(k, True, VIDEOS["v1"]) is None
    assert assemble.gate(k, False, VIDEOS["v1"]).startswith("inaccurate")
    k["check"]["issue"] = "The clip contains transcription errors"
    assert assemble.gate(k, False, VIDEOS["v1"]) is None
    k["check"]["issue"] = "States that gradient descent maximises the loss"
    assert assemble.gate(k, True, VIDEOS["v1"]).startswith("inaccurate")


def test_topup_allows_one_second_explanation_from_another_teacher():
    lec = {"lecture_id": "W01.L1", "slot_minutes": 90, "parts": [_part("A", 15), _part("B", 15), _part("C", 30)]}
    clips = [_clip("v1", 0, 0, 900), _clip("v2", 0, 0, 700, rating=5), _clip("v3", 0, 0, 600, rating=5)]
    for k in clips:
        k["check"]["points"] = {"0": 1.0, "1": 1.0}                                   # all three teach the same points
    VID = VIDEOS | {"v3": {"id": "v3", "title": "Other", "tier": 1, "published": "2026-01-01T00:00:00Z"}}
    out = assemble.choose(lec, clips, VID, fast=False, taken=[])
    a = next(pp for pp in out["plan"] if pp["part"] == 0)
    assert len(a["clips"]) == 2 and a.get("second_explanation")                       # one repeat, never two


def test_a_part_never_plays_three_explanations_of_the_same_points():
    lec = {"lecture_id": "W01.L1", "slot_minutes": 60, "parts": [_part("A", 30)]}
    clips = [_clip(v, 0, 0, 600) for v in ("v1", "v2", "v3")]
    for k in clips:
        k["check"]["points"] = {"0": 1.0, "1": 1.0}
    VID = VIDEOS | {"v3": {"id": "v3", "title": "Other", "tier": 1, "published": "2026-01-01T00:00:00Z"}}
    out = assemble.choose(lec, clips, VID, fast=False, taken=[])
    assert len({k["video"] for k in out["plan"][0]["clips"]}) == 2


# ---- 17 Nov audit fixes
def test_tier_matches_whole_words_and_exact_brands():
    T.tier.cache_clear()
    assert T.tier("MIT OpenCourseWare") == 1 and T.tier("IIT Madras") == 1 and T.tier("NPTEL-NOC IITM") == 1
    assert T.tier("John Smith") == 4 and T.tier("Lets Decode Together") == 4 and T.tier("iitian codes") == 4
    assert T.tier("AI Engineering from Scratch with Avinash.") == 4 and T.tier("AI Engineer") == 1
    assert T.tier("Claude Code Tips by Ravi") == 4 and T.tier("Anthropic") == 1 and T.tier("Java dev to AI") == 4


def test_boundaries_snap_to_whole_sentences():
    rows = [{"start": 0, "dur": 5, "text": "Welcome back."}, {"start": 5, "dur": 5, "text": "Today we look at"},
            {"start": 10, "dur": 5, "text": "context windows, and this means"}, {"start": 15, "dur": 5, "text": "tools can read it all."},
            {"start": 20, "dur": 5, "text": "Next we see"}, {"start": 25, "dur": 5, "text": "how agents plan."}]
    assert E.sentence_start(rows, 10) == 5          # "context windows, ..." is mid-sentence: back to "Today we look at"
    assert E.sentence_start(rows, 20) == 20         # already a sentence start
    assert E.sentence_end(rows, 22) == 30           # "Next we see" runs on to "how agents plan."
    assert E.sentence_end(rows, 20) == 20           # a sentence ends exactly there
    flat = [{"start": i * 5, "dur": 5, "text": "no punctuation here"} for i in range(6)]
    assert E.sentence_start(flat, 12) == 12 and E.sentence_end(flat, 12) == 12   # unpunctuated captions: unchanged


def test_core_term_for_channel_search():
    from profsagent.ytlecture.orchestrator import core_term
    assert core_term(["MCP server explained", "build an MCP server", "MCP tools tutorial"]) == "MCP server"


def test_course_pool_and_clips_taken_by_other_topics(tmp_path):
    import json as _j
    from profsagent.ytlecture.orchestrator import Orchestrator
    o = object.__new__(Orchestrator)
    o.dir = tmp_path
    (tmp_path / "state").mkdir()
    other = {"candidates": {"vA": {"id": "vA", "title": "Lecture 7: Agentic Coding", "channel": "Missing Semester",
                                   "published": "2026-01-10"},
                            "vOld": {"id": "vOld", "title": "Old", "channel": "x", "published": "2019-01-01"}},
             "lectures": {"W01.L1": {"assembly": {"plan": [{"part": 0, "clips": [{"video": "vA", "a": 10, "b": 400}]}]}}}}
    (tmp_path / "state" / "M1.T1.json").write_text(_j.dumps(other), encoding="utf-8")
    merged = o.with_course_pool("M2.T1", {"vB": {"id": "vB"}}, fast=True)
    assert set(merged) == {"vA", "vB"} and merged["vA"]["tier"] == 1           # the old video is filtered (fast-moving)
    assert o.taken_elsewhere("M2.T1") == [{"video": "vA", "a": 10, "b": 400}]
    assert o.taken_elsewhere("M1.T1") == []


def test_prerank_shows_authoritative_plain_titles_in_the_roster():
    from profsagent.ytlecture.orchestrator import Orchestrator
    o = object.__new__(Orchestrator)
    parts = [_part("JSON-RPC message lifecycle", 10), _part("MCP tool schemas", 10)]
    for p in parts:
        p["search_phrases"] = [p["title"]]
    cands = {f"v{i}": {"id": f"v{i}", "title": f"MCP JSON-RPC tool schema tutorial {i}", "channel": f"Small {i}", "tier": 4,
                       "description": "MCP JSON-RPC tool schema", "parts": []} for i in range(30)}
    cands["anchor"] = {"id": "anchor", "title": "The Model Context Protocol (MCP)", "channel": "Anthropic", "tier": 1,
                       "description": "", "parts": []}
    _offline()
    pool, ranked, roster = o.prerank(parts, cands, "W01.L1", {"authorities": [{"name": "Anthropic"}]})
    assert "anchor" in {v["id"] for v in pool} | {v["id"] for v in roster}


# ---------------------------------------------------------------- 17 Nov: shortlist redesign
def _offline():
    """No watch-page fetch, no cross-encoder download in tests."""
    T.cfg.cache_clear()
    T.cfg()["shortlist"]["watch_pages"] = False
    T.cfg()["shortlist"]["cross_weight"] = 0


def test_chapters_with_bullets_and_emoji():
    from profsagent.delivery.segments import chapters
    assert [c["title"] for c in chapters("- 0:00:00 Intro\n- 0:00:42 Core\n- 0:05:48 When", 600)] == ["Intro", "Core", "When"]
    assert len(chapters("⌨️ (0:00:00) A\n⌨️ (0:01:00) B\n⌨️ (0:02:00) C", 600)) == 3
    assert chapters("Call us at 12:30 today", 600) == []


def test_watch_page_key_moments_heatmap_and_description():
    import json as _j
    data = {"playerOverlays": {"markersMap": [{"key": "AUTO_CHAPTERS", "value": {"chapters": [
        {"chapterRenderer": {"title": {"simpleText": "The case for agents"}, "timeRangeStartMillis": 0}},
        {"chapterRenderer": {"title": {"simpleText": "Building blocks"}, "timeRangeStartMillis": 729120}}]}}]},
        "frameworkUpdates": {"markersList": {"markerType": "MARKER_TYPE_HEATMAP", "markers": [
            {"startMillis": str(i * 10000), "durationMillis": "10000", "intensityScoreNormalized": 1.0 if i == 7 else 0.2}
            for i in range(20)]}}}
    player = {"videoDetails": {"shortDescription": "full text " * 400}}
    h = f"<script>var ytInitialData = {_j.dumps(data)};</script><script>var ytInitialPlayerResponse = {_j.dumps(player)};</script>"
    p = E.parse_watch_page(h)
    assert p["ok"] and p["chapters_kind"] == "auto" and p["key_moments"][1] == {"start": 729.12, "title": "Building blocks"}
    assert len(p["description"]) > 3000
    assert E.peaks(p["replayed"]) == [{"start": 70.0, "end": 80.0, "intensity": 1.0}]
    v = {"id": "x", "title": "t", "description": "short", "duration_s": 1500}
    E.enrich(v, p)
    ch = E.chapters_of(v)
    assert v["description"].startswith("full text") and ch[0]["auto"] and ch[1]["end"] == 1500
    assert E.parse_watch_page("<html>consent</html>")["ok"] is False


def _cands_for_select():
    mk = lambda i, ch, d: {"id": i, "title": i, "channel": ch, "duration_s": d, "tier": 4}  # noqa: E731
    return {"short0": mk("short0", "A", 600), "short1": mk("short1", "B", 600), "long": mk("long", "C", 5400),
            "dup0": mk("dup0", "A", 600), "weak": mk("weak", "D", 600)}


def test_select_covers_parts_prefers_anchor_and_respects_budget():
    from profsagent.ytlecture import shortlist as SL
    _offline()
    parts = [_part("a", 10), _part("b", 10), _part("c", 10)]
    g = lambda x, n=2: {"g": x, "n": n, "where": "", "reason": "r", "level_ok": True, "standalone": True}  # noqa: E731
    G = {"short0": {0: g(3)}, "short1": {1: g(2.5)}, "long": {0: g(2.5), 1: g(2.5), 2: g(3)},
         "dup0": {0: g(2.5)}, "weak": {2: g(1)}}
    picks = SL.select(G, parts, _cands_for_select(), {}, budget=3.0)
    ids = [p["video_id"] for p in picks]
    assert ids[0] == "long" and next(p for p in picks if p["video_id"] == "long")["anchor"]
    assert "weak" not in ids                                         # a grade below min_grade never counts
    assert sum(SL.units(_cands_for_select()[i]) for i in ids) <= 3.0
    # second round: only part 2 is still needed; part 0's sources add nothing
    again = SL.select(G, parts, _cands_for_select(), {}, budget=3.0, need={2: 1.0}, exclude={"long"})
    assert again == []


def test_grade_sets_add_nominated_and_strong_long_videos():
    import numpy as np
    from profsagent.ytlecture import shortlist as SL
    _offline()
    vids = [{"id": f"v{i}", "title": "t", "channel": f"c{i}", "tier": 4, "duration_s": 600} for i in range(20)]
    vids.append({"id": "lec", "title": "Lecture 7", "channel": "Missing Semester", "tier": 1, "duration_s": 3600})
    score = np.array([[1.0 - i * 0.01 for i in range(20)] + [0.1]])
    R = {"vids": vids, "score": score, "rel": score, "prior": np.zeros(21), "auth": [False] * 21}
    s = SL.grade_sets(R, [_part("a", 10)])
    assert len(s[0]) == 13 and "lec" in s[0]                         # 12 by rank + the long tier-1 lecture
    s = SL.grade_sets(R, [_part("a", 10)], nominated={0: ["v19"]})
    assert "v19" in s[0]


def test_reputation_from_earlier_runs(tmp_path, monkeypatch):
    import json as _j
    from profsagent.ytlecture import shortlist as SL
    _offline()
    d = tmp_path / "r1" / "delivery" / "ytlecture" / "state"
    d.mkdir(parents=True)
    st = {"candidates": {"a": {"channel": "Good"}, "b": {"channel": "Good"}, "c": {"channel": "Bad"}},
          "lectures": {"W01.L1": {"read": ["a", "b", "c"], "clips": [
              {"video": "a", "score": 0.9, "check": {"coverage": 0.8}}, {"video": "b", "score": 0.8, "check": {"coverage": 0.7}}]}}}
    (d / "M1.T1.json").write_text(_j.dumps(st), encoding="utf-8")
    monkeypatch.setattr(SL, "RUNS", tmp_path)
    SL._REP.clear()
    rep = SL.reputation()
    assert rep["Good"][0] > 0.6 > 0.5 > rep["Bad"][0] and rep["Good"][1] == 2
    SL._REP.clear()
    assert SL.reputation(exclude_run="r1") == {}
    SL._REP.clear()


def test_select_counts_a_video_for_few_parts_and_prefers_short_focused_ones():
    from profsagent.ytlecture import shortlist as SL
    _offline()
    parts = [_part(str(i), 10) for i in range(5)]
    g = lambda x: {"g": x, "n": 2, "where": "", "reason": "r", "level_ok": True, "standalone": True}  # noqa: E731
    cands = {"lec": {"id": "lec", "channel": "Uni", "duration_s": 5000, "tier": 1},
             "sq0": {"id": "sq0", "channel": "SQ", "duration_s": 1000, "tier": 2},
             "sq1": {"id": "sq1", "channel": "SQ2", "duration_s": 1000, "tier": 2}}
    G = {"lec": {i: g(3) for i in range(5)}, "sq0": {0: g(3), 1: g(3)}, "sq1": {2: g(3)}}
    ids = [p["video_id"] for p in SL.select(G, parts, cands, {}, budget=2.0)]
    assert ids == ["sq0", "sq1"]                     # 2 units: two focused videos beat one 83-min lecture (2.5 units)
    assert SL.parts_cap(cands["lec"]) == 3 and SL.units(cands["lec"]) == 2.5


# ---------------------------------------------------------------- 18 Nov: free InnerTube search
def _vr(vid, title, ch, chid, length="21:57", views="1,234 views"):
    return {"videoRenderer": {"videoId": vid, "title": {"runs": [{"text": title}]}, "lengthText": {"simpleText": length},
                              "viewCountText": {"simpleText": views}, "publishedTimeText": {"simpleText": "1 month ago"},
                              "ownerText": {"runs": [{"text": ch, "navigationEndpoint": {"browseEndpoint": {"browseId": chid}}}]}}}


def test_innertube_parsers():
    from profsagent.ytlecture import innertube as IT
    d = {"contents": {"x": [_vr("a1", "MCP explained", "Apna College", "UC1"), _vr("a1", "dup", "x", "y"),
                            {"lockupViewModel": {"contentType": "LOCKUP_CONTENT_TYPE_PLAYLIST", "contentId": "PL1",
                                                 "metadata": {"lockupMetadataViewModel": {"title": {"content": "CS25"},
                                                     "metadata": {"contentMetadataViewModel": {"metadataRows": [
                                                         {"metadataParts": [{"text": {"content": "Stanford Online"}}]}]}}}}}}]}}
    v = IT.parse_videos(d)
    assert v == [{"id": "a1", "title": "MCP explained", "channel": "Apna College", "channel_id": "UC1", "duration_s": 1317,
                  "views": 1234, "published_ago": "1 month ago"}]
    assert IT.parse_playlists(d) == [{"id": "PL1", "title": "CS25", "channel": "Stanford Online"}]


def test_channel_search_keeps_only_that_channel(monkeypatch):
    from profsagent.ytlecture import innertube as IT
    page = {"x": [_vr("own1", "Lecture 7", "Missing Semester", "UCms"),
                  {"videoRenderer": {"videoId": "film", "title": {"runs": [{"text": "TRANSFORMERS ONE"}]},
                                     "ownerText": {"runs": [{"text": "Action & adventure • 2024"}]}}}]}
    monkeypatch.setattr(IT.S, "_cached", lambda ns, key, days, fn: fn())
    monkeypatch.setattr(IT, "_post", lambda ep, body: page)
    IT._st["fails"] = 0
    tr = T.Trace()
    assert [x["id"] for x in IT.channel_search("UCms", "agentic coding", tr, "t")] == ["own1"]
    assert "1 from other channels dropped" in tr.rows[-1]["note"]


def test_video_search_falls_back_to_the_api(monkeypatch):
    from profsagent.ytlecture import innertube as IT
    from profsagent.ytlecture.orchestrator import Orchestrator
    monkeypatch.setattr(IT, "available", lambda: True)
    monkeypatch.setattr(IT, "search", lambda *a, **k: [])
    monkeypatch.setattr(T, "yt_search", lambda q, tr, scope, long=False, n=None: [{"id": "api1"}])
    assert Orchestrator.video_search("q", T.Trace(), "t") == [{"id": "api1"}]
    monkeypatch.setattr(IT, "search", lambda *a, **k: [{"id": "free1"}])
    assert Orchestrator.video_search("q", T.Trace(), "t") == [{"id": "free1"}]


def test_subscribers_in_prior():
    from profsagent.ytlecture import shortlist as SL
    _offline()
    assert SL.subscribers_score({"subscribers": 5000}) == 0 and SL.subscribers_score({"subscribers": 2_000_000}) == 1
    base = {"title": "t", "channel": "x", "tier": 4, "views": 0}
    assert SL.prior({**base, "subscribers": 1_000_000}, False, "W01.L1", {}) > SL.prior(base, False, "W01.L1", {})


# ---------------------------------------------------------------- 18 Nov: first claim on a topic's own videos
def test_later_topic_has_first_claim_on_its_own_videos(tmp_path):
    import json as _j
    from profsagent.ytlecture.orchestrator import Orchestrator
    o = object.__new__(Orchestrator)
    o.dir = tmp_path
    o.briefs = [{"lecture_id": "W01.L2"}, {"lecture_id": "W02.L1"}]
    (tmp_path / "state").mkdir()
    early = {"plan": {"lectures": [{"lecture_id": "W01.L2"}]},
             "candidates": {"shared": {"id": "shared", "title": "t", "channel": "c", "found_by": ["youtube: q"]},
                            "borrowed": {"id": "borrowed", "title": "t", "channel": "c", "found_by": ["course pool: M2.T1"]}}}
    late = {"plan": {"lectures": [{"lecture_id": "W02.L1"}]},
            "candidates": {"raschka": {"id": "raschka", "title": "t", "channel": "c", "found_by": ["youtube: sdpa"]},
                           "borrowed": {"id": "borrowed", "title": "t", "channel": "c", "found_by": ["youtube: q2"]},
                           "shared": {"id": "shared", "title": "t", "channel": "c", "found_by": ["youtube: q3"]}}}
    (tmp_path / "state" / "M1.T2.json").write_text(_j.dumps(early), encoding="utf-8")
    (tmp_path / "state" / "M2.T1.json").write_text(_j.dumps(late), encoding="utf-8")
    T.cfg.cache_clear()
    assert o.reserved_for_later("M1.T2") == {"raschka", "borrowed"}     # "shared" was found by both: no claim
    assert o.reserved_for_later("M2.T1") == set()
    assert "raschka" not in o.with_course_pool("M1.T2", dict(early["candidates"]), fast=False)   # no borrowing from later
    assert "shared" in o.with_course_pool("M2.T1", dict(late["candidates"]), fast=False)


def test_topup_adds_a_differently_taught_clip_while_the_lecture_is_short():
    from profsagent.ytlecture.assemble import choose
    _offline()
    part = {"title": "p", "teaches": "x", "must_cover": ["a"], "minutes": 10, "kind": "concept", "search_phrases": ["p"]}
    lec = {"lecture_id": "W01.L1", "slot_minutes": 60, "parts": [part]}

    def mk(v, treatment):
        return {"video": v, "part": 0, "a": 0, "b": 300, "covers": [0], "treatment": treatment, "standalone": True,
                "level": "right", "rating": 5, "concerns": "", "evidence": "captions",
                "check": {"coverage": 1.0, "standalone": True, "accurate": True, "recommend": True, "points": {"0": 1.0}}}
    vids = {f"v{i}": {"id": f"v{i}", "title": "t", "channel": f"c{i}", "tier": 1, "published": "2026-01-01T00:00:00Z"}
            for i in range(5)}
    explains = [mk(f"v{i}", "explains") for i in range(4)]
    used = [k["video"] for pp in choose(lec, explains, vids, False, [])["plan"] for k in pp["clips"]]
    assert len(used) == 2                                   # never a third explanation of the same points
    mixed = [mk(f"v{i}", "explains") for i in range(3)] + [mk("v4", "demonstrates")]
    used = [k["video"] for pp in choose(lec, mixed, vids, False, []) ["plan"] for k in pp["clips"]]
    assert len(used) == 3 and "v4" in used                  # short of 65%: a demo after two explanations is added
