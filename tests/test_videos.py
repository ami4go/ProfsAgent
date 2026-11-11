"""Videos for a lecture (10 Nov): metadata shortlist, digest, the AI's markers, the independent check and its gate, the plan
for the lecture (blocks), and how the delivery mix treats it. Offline: no API calls."""
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from profsagent.delivery import segments as sg  # noqa: E402
from profsagent.delivery import sources as so  # noqa: E402
from profsagent.delivery import videos as vd  # noqa: E402
from profsagent.delivery.models import ClipVerdict, PointCheck  # noqa: E402


def video(vid="v", texts=None, step=30.0, tier=2, desc=""):
    texts = texts or ["word " * 40] * 40
    tr = [{"start": i * step, "dur": step, "text": t} for i, t in enumerate(texts)]
    return {"id": vid, "title": vid, "duration_s": len(texts) * step, "tier": tier, "description": desc, "_tr": tr, "source": "ch"}


def part(n, minutes=10, **kw):
    return {"id": f"L.C{n}", "title": f"part {n}", "teaches": "Explain how the thing works in detail. Students compare the two common ways.",
            "key_terms": ["alpha", "beta"], "kind": "concept", "minutes": minutes, **kw}


def clip(cid, vid, a, z, **kw):
    d = dict(cid=cid, vid=vid, start=float(a), end=float(z), verdict="teaches_fully", verified=True, relevance=5, sufficiency=4, coverage=0.8,
             clean_start=4, clean_end=4, stands_alone=4, clarity=4, level_fit=4, covered=[], missing=[], evidence=[], strengths=[], limitations=[],
             peak=0.6, source="captions", checker="x:y", reader="a:b", failed_gate=[])
    d.update(kw)
    return d


VIDS = {"v1": {"tier": 2}, "v2": {"tier": 1}, "v3": {"tier": 4}}


# ------------------------------------------------------------------ what a part requires
def test_checklist_is_the_sentences_and_the_key_terms_every_time():
    c = part(1)
    got = sg.checklist(c)
    assert got == sg.checklist(c) and len(got) == 4 and got[0].startswith("Explain how") and "alpha" in got[2]


# ------------------------------------------------------------------ what the AI reads
def test_a_short_transcript_is_read_whole():
    v = video(texts=["a b c " * 10] * 10)
    v["_win"] = [{"start": s["start"], "end": s["start"] + 30, "text": s["text"]} for s in v["_tr"]]
    txt = sg.digest(v, np.zeros((10, 1)), [0])
    assert "skipped" not in txt and txt.count("[") == 10


def test_a_long_transcript_keeps_the_closest_passages_of_every_part_from_anywhere(monkeypatch):
    v = video(texts=["word " * 200] * 60)
    v["_win"] = [{"start": s["start"], "end": s["start"] + 30, "text": s["text"]} for s in v["_tr"]]
    sm = np.zeros((60, 2))
    sm[3:6, 0] = 0.9                                 # part 1 is taught near the start, very closely matched
    sm[50:53, 1] = 0.5                               # part 2 near the end, less so: it must not lose its share of the words
    monkeypatch.setitem(sg.vcfg(), "max_words_per_read", 1500)
    txt = sg.digest(v, sm, [0, 1])
    assert "[2:00]" in txt and "[25:30]" in txt and "skipped to" in txt and len(txt.split()) < 2600


def test_markers_must_be_real_and_the_end_marker_window_is_included():
    v = video(desc="0:00 Intro\n3:10 The idea\n8:00 Next\n12:00 End")
    v["_win"] = [{"start": s["start"], "end": s["start"] + 30, "text": s["text"]} for s in v["_tr"]]
    assert sg.parse_range("4:00", "7:00", v) == (235.0, 450.0)              # 5 s of context; the window at 7:00 ends at 7:30
    assert sg.parse_range("3:00", "7:45", v)[0:2] == (190.0, 480.0)         # both edges move to the chapter's
    assert sg.parse_range("7:00", "4:00", v) is None
    assert sg.parse_range("99:00", "120:00", v) is None                     # not in this video
    assert sg.parse_range("4:00", "4:10", v) is None                        # too short to teach anything


# ------------------------------------------------------------------ the check: programs decide
def test_a_quote_must_really_be_in_the_clip():
    text = "so the client sends an initialize request and the server answers with its capabilities"
    assert sg.quote_found("the client sends an initialize request", text)
    assert sg.quote_found("the client sends a initialize request and server", text)   # a copying slip
    assert not sg.quote_found("gradient descent minimises the loss function", text)
    assert not sg.quote_found("the", text)


def _verdict(status=("taught",) * 4, quote="the speaker explains how the thing works here", **kw):
    d = dict(relevance=5, sufficiency=5, clean_start=4, clean_end=4, stands_alone=4, clarity=4, level_fit=4,
             points=[PointCheck(n=i + 1, status=s, quote=quote if s == "taught" else "") for i, s in enumerate(status)])
    d.update(kw)
    return ClipVerdict(**d)


def _score(verdict, text="the speaker explains how the thing works here and goes on", c=None):
    c = c or part(1)
    v = video()
    v["_win"] = [{"start": 0.0, "end": 600.0, "text": text}]
    return sg.score_clip({"cid": c["id"], "vid": "v", "start": 0.0, "end": 480.0, "claim": "fully"}, verdict, sg.checklist(c), c, v, text, "x:y", "a:b")


def test_a_clip_passes_only_when_every_threshold_holds():
    assert _score(_verdict())["failed_gate"] == []
    assert any("sufficiency" in x for x in _score(_verdict(sufficiency=3))["failed_gate"])
    assert any("relevance" in x for x in _score(_verdict(relevance=3))["failed_gate"])
    assert any("stands_alone" in x for x in _score(_verdict(stands_alone=2))["failed_gate"])


def test_points_said_to_be_taught_without_real_words_do_not_count():
    r = _score(_verdict(quote="a sentence that was never said in this clip at all"))
    assert r["coverage"] == 0 and r["quotes_not_found"] == 4 and any("coverage" in x for x in r["failed_gate"])


def test_coverage_is_computed_from_the_points():
    r = _score(_verdict(status=("taught", "taught", "taught", "absent")))
    assert r["coverage"] == 0.75 and not r["failed_gate"] and len(r["evidence"]) == 3 and len(r["missing"]) == 1


def test_notes_have_no_quotes_to_check_but_say_so():
    c = part(1)
    v = {**video(), "evidence": "notes"}
    v["_win"] = [{"start": 0.0, "end": 600.0, "text": "notes"}]
    r = sg.score_clip({"cid": c["id"], "vid": "v", "start": 0.0, "end": 480.0}, _verdict(quote="paraphrase"), sg.checklist(c), c, v, "notes", "x:y", "a:b")
    assert r["coverage"] == 1 and r["source"] == "notes"


# ------------------------------------------------------------------ the plan for the lecture
def test_one_video_teaching_the_first_parts_becomes_one_block_and_the_rest_get_none():
    parts = [part(i) for i in (1, 2, 3, 4, 5)]
    clips = [clip("L.C1", "v1", 0, 420), clip("L.C2", "v1", 420, 900), clip("L.C3", "v1", 900, 1380)]
    got = sg.assign(parts, clips, VIDS)
    assert [s and s["vid"] for s in got["path"]] == ["v1", "v1", "v1", None, None]
    assert sg.blocks_of(parts, got["path"]) == [[0, 1, 2]]


def test_staying_with_one_video_beats_a_slightly_better_switch():
    parts = [part(1), part(2)]
    clips = [clip("L.C1", "v1", 0, 480), clip("L.C2", "v1", 500, 1000), clip("L.C2", "v2", 100, 600, coverage=0.85)]
    assert sg.assign(parts, clips, VIDS)["path"][1]["vid"] == "v1"


def test_a_much_better_clip_still_wins_over_continuity():
    parts = [part(1), part(2)]
    clips = [clip("L.C1", "v1", 0, 480), clip("L.C2", "v1", 500, 1000, coverage=0.66, sufficiency=4, clarity=4, level_fit=4),
             clip("L.C2", "v2", 100, 600, coverage=1.0, sufficiency=5, clarity=5, level_fit=5, stands_alone=5, clean_start=5, clean_end=5)]
    assert sg.assign(parts, clips, VIDS)["path"][1]["vid"] == "v2"


def test_clips_out_of_teaching_order_are_not_a_block():
    parts = [part(1), part(2)]
    clips = [clip("L.C1", "v1", 900, 1400), clip("L.C2", "v1", 0, 480)]
    got = sg.assign(parts, clips, VIDS)
    assert [s and s["vid"] for s in got["path"]] == ["v1", "v1"] and sg.blocks_of(parts, got["path"]) == [[0], [1]]


def test_a_part_never_goes_without_a_clip_that_passed_to_save_a_switch():
    parts = [part(1), part(2), part(3)]
    clips = [clip("L.C1", "v1", 0, 480), clip("L.C2", "v3", 0, 480), clip("L.C3", "v1", 500, 1000)]
    assert all(sg.assign(parts, clips, VIDS)["path"])


def test_a_clip_much_shorter_or_longer_than_the_part_is_dropped():
    parts = [part(1, minutes=30)]
    assert sg.assign(parts, [clip("L.C1", "v1", 0, 300)], VIDS)["path"] == [None]         # 5 min for a 30-min part
    parts = [part(1, minutes=5)]
    got = sg.assign(parts, [clip("L.C1", "v1", 0, 1200)], VIDS)
    assert got["path"] == [None] and "min of video" in got["dropped"][0]["dropped"]


def test_a_block_is_judged_on_its_total_length():
    # 3 min for a 10-min part fails alone, but with its neighbour the block's 15 min serve 20 min of class
    parts = [part(1), part(2)]
    assert sg.assign([parts[0]], [clip("L.C1", "v1", 0, 180)], VIDS)["path"] == [None]
    got = sg.assign(parts, [clip("L.C1", "v1", 0, 180), clip("L.C2", "v1", 180, 900)], VIDS)
    assert all(got["path"]) and sg.blocks_of(parts, got["path"]) == [[0, 1]]


def test_the_same_minutes_are_not_used_twice():
    parts = [part(1), part(2, in_class=True), part(3)]
    clips = [clip("L.C1", "v1", 0, 480), clip("L.C3", "v1", 0, 480, coverage=0.7)]        # not neighbours: not one watch
    got = sg.assign(parts, clips, VIDS)
    assert [bool(s) for s in got["path"]] == [True, False, False] and "same minutes" in got["dropped"][0]["dropped"]
    # ... nor across the lectures of a topic
    got = sg.assign([part(1)], [clip("L.C1", "v1", 0, 480)], VIDS, taken=[clip("X.C9", "v1", 30, 500)])
    assert got["path"] == [None] and "earlier lecture" in got["dropped"][0]["dropped"]


def test_an_activity_in_the_middle_ends_a_block():
    parts = [part(1), part(2, in_class=True), part(3)]
    got = sg.assign(parts, [clip("L.C1", "v1", 0, 480), clip("L.C3", "v1", 500, 1000)], VIDS)
    assert sg.blocks_of(parts, got["path"]) == [[0], [2]]


# ------------------------------------------------------------------ the funnel, before any transcript
def _fake_embed(texts):
    keys = ["alpha", "beta", "gamma"]
    out = []
    for t in texts:
        v = np.array([1.0 if k in t.lower() else 0.0 for k in keys]) + 1e-6
        out.append(v / np.linalg.norm(v))
    return np.vstack(out)


def test_the_shortlist_reaches_different_parts_and_cached_transcripts_are_free(monkeypatch):
    monkeypatch.setattr(vd, "embed", _fake_embed)
    known = {"a2"}
    monkeypatch.setattr(vd, "transcript_known", lambda i: i in known)
    def v(i, t, tier=4):
        return {"id": i, "title": t, "description": "", "tier": tier, "duration_s": 600}
    parts = [{"id": "C1", "title": "alpha", "teaches": "", "key_terms": []}, {"id": "C2", "title": "beta", "teaches": "", "key_terms": []}]
    vids = [v("a1", "alpha one"), v("a2", "alpha two"), v("a3", "alpha three"), v("b1", "beta one")]
    got = [x["id"] for x in vd.shortlist(vids, parts, new_budget=2, max_total=3)]
    assert "b1" in got and "a2" in got and len(got) == 3             # one for each part first; the known one costs no budget


def test_popularity_cannot_get_a_video_onto_the_shortlist(monkeypatch):
    monkeypatch.setattr(vd, "embed", _fake_embed)
    monkeypatch.setattr(vd, "transcript_known", lambda i: False)
    parts = [{"id": "C1", "title": "alpha", "teaches": "", "key_terms": []}]
    vids = [{"id": "viral", "title": "gamma", "description": "", "tier": 4, "views": 10**8, "duration_s": 600},
            {"id": "quiet", "title": "alpha", "description": "", "tier": 4, "views": 90, "duration_s": 600}]
    assert vd.shortlist(vids, parts, 1, 1)[0]["id"] == "quiet"


def test_metadata_filter(monkeypatch):
    ok = {"title": "Attention explained", "duration_s": 900, "public": True, "url": "https://www.youtube.com/watch?v=x"}
    assert vd.usable(ok) is None
    assert "short" in vd.usable({**ok, "duration_s": 60})
    assert vd.usable({**ok, "title": "Course trailer: attention"})
    assert vd.usable({**ok, "language": "fr"})


# ------------------------------------------------------------------ services: a failure is not an answer
def test_notes_must_have_rising_times_inside_the_video_and_fill_it():
    good = "\n".join(f"[{i // 2}:{'30' if i % 2 else '00'}] something is explained here" for i in range(20))
    rows = so.parse_notes("intro\n" + good, 600)
    assert len(rows) == 20 and rows[1]["start"] == 30 and rows[-1]["start"] + rows[-1]["dur"] == 600
    assert so.parse_notes(good, 6000) is None                       # stops long before the video does
    assert so.parse_notes(good, 100) is None                        # times past the end
    assert so.parse_notes("[1:00] a\n[0:30] b\n[2:00] c", 150) is None
    assert so.parse_notes("no markers at all", 100) is None


def _no_cache(tmp_path, monkeypatch):
    monkeypatch.setattr(so, "CACHE", tmp_path)


def test_no_captions_is_remembered_but_a_block_is_not(tmp_path, monkeypatch):
    import types
    _no_cache(tmp_path, monkeypatch)
    calls = []

    class TranscriptsDisabled(Exception):
        pass

    class IpBlocked(Exception):
        pass
    raise_ = {"a": TranscriptsDisabled, "b": IpBlocked}

    class Api:
        def fetch(self, vid, languages=None):
            calls.append(vid)
            raise raise_[vid]()
    monkeypatch.setitem(sys.modules, "youtube_transcript_api", types.SimpleNamespace(YouTubeTranscriptApi=Api))
    monkeypatch.setattr(so, "rcfg", lambda: {"transcripts": {"min_interval_s": 0, "jitter_s": 0}})
    monkeypatch.setitem(so._tx, "blocked", None)
    assert so.transcript("a") is None and so.transcript("a") is None and calls == ["a"] and so.transcript_known("a")
    assert so.transcript("b") is None and so.transcripts_blocked() and not so.transcript_known("b")
    monkeypatch.setitem(so._tx, "blocked", None)


def test_a_failed_search_is_not_remembered_as_no_videos(tmp_path, monkeypatch):
    import types
    _no_cache(tmp_path, monkeypatch)
    monkeypatch.setenv("YOUTUBE_API_KEY", "k")
    monkeypatch.setattr(so.Quota, "can", lambda self, n: True)
    monkeypatch.setattr(so.Quota, "spend", lambda self, n: None)
    state = {"code": 403}
    monkeypatch.setattr(so, "_get", lambda *a, **k: types.SimpleNamespace(status_code=state["code"], json=lambda: {"items": [{"id": {"videoId": "abc"}}]}))
    before = so.YouTube.skipped
    yt = so.YouTube()
    assert yt.search("q") == [] and so.YouTube.skipped == before + 1
    state["code"] = 200
    assert yt.search("q") == ["abc"]
