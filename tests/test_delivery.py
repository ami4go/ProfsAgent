"""Deliverable C (learning resources and expert speakers): offline tests, no API calls."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from profsagent.delivery import checks, common, review  # noqa: E402
from profsagent.delivery import survey as sv  # noqa: E402
from profsagent.delivery.common import iso_duration_s  # noqa: E402

RUN = ROOT / "runs" / "cs601-02" / "state.json"


@pytest.fixture
def tmp_runs(tmp_path, monkeypatch):
    monkeypatch.setattr(common, "RUNS", tmp_path)
    return tmp_path


def test_iso_duration():
    assert iso_duration_s("PT52M55S") == 3175 and iso_duration_s("PT1H2M3S") == 3723 and iso_duration_s(None) is None


@pytest.mark.skipif(not RUN.exists(), reason="needs runs/cs601-02")
def test_briefs_from_the_approved_design():
    from profsagent.delivery.brief import build_briefs
    st = json.loads(RUN.read_text(encoding="utf-8"))
    briefs = build_briefs(st)
    n_slots = sum(len(w["items"]) for w in st["schedule"]["weeks"])
    assert len(briefs) == n_slots                                   # one brief per timetable slot (= design-graph lecture)
    b = briefs[0]
    assert b["lecture_id"] == "W01.L1" and b["targets"][0]["kind"] == "topic" and b["summary"]
    assert all(t["id"] for t in b["targets"]) and isinstance(b["novel"], bool)


def test_survey_only_lectures_that_asked(tmp_runs):
    briefs = [{"lecture_id": "W01.L1", "topic": "A", "week": 1, "novel": True, "summary": "s"},
              {"lecture_id": "W01.L2", "topic": "B", "week": 1, "novel": False, "summary": "s"}]
    (tmp_runs / "r").mkdir()
    s = sv.init("r", briefs)
    assert sv.requests(s) == {} and sv.tasks(s) == {}               # nothing searched before the professor answers
    s["lectures"]["W01.L2"]["want_readings"] = "yes"                # a resource answer without choosing assistance …
    s["lectures"]["W01.L2"]["assistance"] = "no"
    s["lectures"]["W01.L1"].update(own_material="yes", attach_material="yes", attachments=["notes.pdf"], attach_tasks=["quiz"])
    sv.save("r", s)
    t = sv.tasks(sv.load("r"))
    assert sv.requests(sv.load("r")) == {}                          # … asks deliverable C for nothing
    assert t["W01.L1"]["choices"] == ["own_material", "attach_material"] and t["W01.L1"]["attachments"] == ["notes.pdf"]
    s["lectures"]["W01.L2"].update(assistance="yes", guest_lecture="yes")   # several choices at once
    sv.save("r", s)
    r = sv.requests(sv.load("r"))
    assert list(r) == ["W01.L2"] and r["W01.L2"]["want_readings"] and r["W01.L2"]["want_guest"] and not r["W01.L2"]["want_videos"]
    d = sv.apply_defaults("r", briefs)
    assert d["lectures"]["W01.L1"]["guest_lecture"] == "yes" and d["lectures"]["W01.L2"]["guest_lecture"] == "yes"


def test_old_survey_answers_are_migrated():
    old = {"lectures": {"W01.L1": {"teach_myself": "partly", "want_videos": "yes", "want_guest": "yes"},
                        "W01.L2": {"teach_myself": "yes", "want_videos": "no", "want_guest": "no"}}}
    t = sv.tasks(old)
    assert t["W01.L1"]["choices"] == ["own_material", "assistance", "guest_lecture"] and t["W01.L1"]["resources"] == ["videos"]
    assert t["W01.L2"]["choices"] == ["own_material"] and "W01.L2" not in sv.requests(old)


def test_coverage_finds_topic_and_timestamps():
    from profsagent.delivery.coverage import coverage, windows_from_transcript
    tr = [{"start": i * 10.0, "dur": 10.0, "text": t} for i, t in enumerate(
        ["welcome to the course and today's plan"] * 6 +
        ["a hash table stores keys in buckets; with chaining each bucket holds a linked list of colliding keys"] * 9 +
        ["now let us talk about the exam schedule and office hours"] * 6)]
    tg = [{"id": "T", "kind": "topic", "text": "Hash tables with chaining"},
          {"id": "L", "kind": "lo", "text": "Configure a TCP congestion control algorithm"}]
    cov = coverage(windows_from_transcript(tr), tg)
    assert cov["per_target"]["T"]["covered"] and not cov["per_target"]["L"]["covered"]
    seg = cov["per_target"]["T"]["segments"][0]
    assert 40 <= seg["start"] <= 70 and seg["end"] <= 160              # inside the chaining part, not the intro or the outro


def test_resource_checks():
    b = {"topic_id": "T"}
    good = {"kind": "video", "public": True, "embeddable": True, "duration_s": 600, "captions": True, "language": "en",
            "coverage": {"score": 0.8, "evidence": "transcript", "per_target": {"T": {"covered": True, "sim": 0.6, "segments": [{"start": 10, "end": 90, "sim": 0.6}]}}}}
    assert not [x for x in checks.resource(good, b) if x["severity"] == "error"]
    bad = {**good, "blocked_in_india": True, "duration_s": 99999,
           "coverage": {"score": 0, "per_target": {"T": {"covered": False, "sim": 0.1, "segments": []}}}}
    codes = {x["code"] for x in checks.resource(bad, b) if x["severity"] == "error"}
    assert {"R-REGION", "R-DURATION", "R-COVER"} <= codes
    off = {**good, "review": {"explains": "off_topic", "issues": ["about something else"]}}
    assert "R-REVIEW" in {x["code"] for x in checks.resource(off, b) if x["severity"] == "error"}


def test_expert_checks_identity_privacy_fit():
    ok = {"name": "A B", "verified_identity": "OpenAlex", "evidence": [{"kind": "paper", "title": "x"}], "note": {"fit": "strong"}}
    assert not [x for x in checks.expert(ok) if x["severity"] == "error"]
    assert "X-IDENTITY" in {x["code"] for x in checks.expert({**ok, "verified_identity": None})}
    assert "X-PRIVACY" in {x["code"] for x in checks.expert({**ok, "links": {"mail": "someone@example.org"}})}
    assert "X-FIT" in {x["code"] for x in checks.expert({**ok, "note": {"fit": "weak"}})}


def test_scoring_and_diversity():
    from profsagent.delivery.resources import diversify, score
    b = {"novel": False, "targets": []}
    base = {"kind": "video", "tier": 1, "duration_s": 600, "captions": True, "views": 100000, "likes": 3000,
            "published": "2022-01-01T00:00:00Z", "coverage": {"score": 0.9}}
    a = {**base, "title": "Hashing lecture 1", "source": "MIT OpenCourseWare"}
    c = {**base, "title": "Hashing lecture one", "source": "MIT OpenCourseWare"}
    d = {**base, "title": "Hash tables explained with animations", "source": "3Blue1Brown", "tier": 2}
    for x in (a, c, d):
        score(x, b)
    assert 0 < a["total"] <= 1 and set(a["scores"]) == {"coverage", "quality", "authority", "level_fit", "reception", "practicality"}
    picked = diversify([a, c, d], 2)
    assert {p["source"] for p in picked} == {"MIT OpenCourseWare", "3Blue1Brown"}   # no two near-identical items from one channel


def test_review_apply_replace_and_reason_required(tmp_runs):
    d = tmp_runs / "r" / "delivery" / "lectures"
    d.mkdir(parents=True)
    st = {"cco_compact": {"course_name": "T"}}
    (tmp_runs / "r" / "state.json").write_text(json.dumps(st), encoding="utf-8")
    item = lambda n, r: {"url": f"https://x/{n}", "title": f"v{n}", "rank": r, "total": 0.5, "rationale": "", "findings": []}  # noqa: E731
    lec = {"lecture_id": "W01.L1", "topic": "T", "resources": {"items": {"video": [item(1, 1), item(2, 2)]}, "reserve": {"video": [item(3, 3)]}}}
    (d / "W01.L1.json").write_text(json.dumps(lec), encoding="utf-8")
    from profsagent.delivery.pipeline import render
    render("r")
    import yaml
    p = tmp_runs / "r" / "delivery" / "review.yaml"
    rv = yaml.safe_load(p.read_text(encoding="utf-8"))
    rows = rv["lectures"]["W01.L1"]["video"]
    rows[0].update(decision="approve")
    rows[1].update(decision="replace", reason="")                  # no reason → refused
    p.write_text(yaml.safe_dump(rv), encoding="utf-8")
    s = review.apply("r")
    assert s["approved"] == 1 and s["refused"]
    rv = yaml.safe_load(p.read_text(encoding="utf-8"))
    rv["lectures"]["W01.L1"]["video"][1].update(decision="replace", reason="too basic")
    p.write_text(yaml.safe_dump(rv), encoding="utf-8")
    s = review.apply("r")
    out = json.loads((d / "W01.L1.json").read_text(encoding="utf-8"))
    assert s["replaced"] == 1 and [x["title"] for x in out["resources"]["items"]["video"]] == ["v1", "v3"]
    assert out["resources"]["items"]["video"][0]["status_decision"] == "approve" and out["decisions"][0]["reason"] == "too basic"


def test_guest_kit_has_brief_and_draft_and_no_contact_data():
    from profsagent.delivery.experts import guest_kit
    st = {"cco_compact": {"course_name": "Software Development using AI", "target_students": {"years": [3, 4]}}, "level": 3}
    b = {"lecture_id": "W02.L1", "topic": "Model context protocol", "week": 2, "hours": 2, "summary": "s",
         "learning_outcomes": [{"statement": "Configure an MCP server"}], "builds_on": [], "leads_to": [], "assessed_in": []}
    e = [{"rank": 1, "name": "A Person", "kind": "industry", "affiliation": "Co", "total": 0.8, "why": "w",
          "evidence": [{"title": "MCP talk"}], "suggested_format": "live_remote_60"}]
    kit = guest_kit(st, b, e)
    assert "Brief for the speaker" in kit and "Invitation draft" in kit and "Dear A Person" in kit and "@" not in kit


def test_continuation_gives_next_best_items_not_repeats():
    from profsagent.delivery.pipeline import continuation
    cov = {"per_target": {"T1": {"covered": True, "sim": 0.6, "segments": []}}}
    it = lambda n, t=0.8, c=cov: {"id": f"v{n}", "url": f"https://youtu.be/{n}", "title": f"v{n}", "rank": n, "total": t, "coverage": c,  # noqa: E731
                                  "review": {"explains": "explains"}}
    rd = lambda n, src, t=0.8: {**it(n, t), "kind": "reading", "source": src}  # noqa: E731
    prev = {"resources": {"items": {"video": [it(1), it(2), it(3)], "reading": [rd(10, "modelcontextprotocol.io")]},
                          "reserve": {"video": [it(4), it(5, 0.3), it(6, 0.8, {"per_target": {}}), it(7), it(8),
                                                {**it(9), "review": {"explains": "mentions"}}, {**it(13), "review": None}],
                                      "reading": [rd(11, "modelcontextprotocol.info"), rd(12, "example.org")]}},
            "experts": {"experts": [{"name": "A"}]}}
    b = {"lecture_id": "W02.L1", "topic": "T", "topic_id": "T1", "targets": []}
    out = continuation(prev, "W01.L2", b, {"want_videos": True, "want_readings": True, "want_guest": True})
    shown = [c["title"] for c in out["resources"]["items"]["video"]]
    # v5 is below the bar, v6 does not cover the topic, v9 only mentions it, v13 was never reviewed
    assert shown == ["v4", "v7", "v8"] and [c["rank"] for c in out["resources"]["items"]["video"]] == [1, 2, 3]
    assert [c["title"] for c in out["resources"]["items"]["reading"]] == ["v12"]          # the .info mirror is skipped
    assert out["continuation_of"] == "W01.L2" and out["experts"]["same_as"] == "W01.L2"


def test_mentions_only_items_follow_teaching_items():
    from profsagent.delivery.resources import diversify, mentions_only
    a = {"title": "alpha intro", "total": 0.85, "kind": "video", "source": "A", "review": {"explains": "mentions"}}
    c = {"title": "gamma deep dive", "total": 0.80, "kind": "video", "source": "C", "review": {"explains": "teaches"}}
    picked = diversify([a, c], 2)
    assert picked[0] is c and mentions_only(picked[1])


def test_official_documentation_is_recognised():
    from profsagent.delivery.resources import tier_of_domain
    assert tier_of_domain("https://modelcontextprotocol.io/specification/2026-07-28", "Model context protocols and architecture") == 3
    assert tier_of_domain("https://docs.example.org/guide", "anything") == 3
    assert tier_of_domain("https://ocw.mit.edu/courses/x", "anything") == 1
    assert tier_of_domain("https://someblog.net/post", "Model context protocols") == 4


def test_country_names_normalised():
    from profsagent.delivery.experts import country_code
    assert country_code("United States") == "US" and country_code("India") == "IN" and country_code("de") == "DE" and country_code(None) is None


def test_practice_generic_and_social_filters():
    b = {"topic_id": "T"}
    cov = {"score": 0.8, "evidence": "text", "per_target": {"T": {"covered": True, "sim": 0.6, "segments": []}}}
    def errs(c):
        return {x["code"] for x in checks.resource({"coverage": cov, **c}, b) if x["severity"] == "error"}
    assert "R-PRACTICE" in errs({"kind": "practice", "url": "https://arxiv.org/abs/2601.00001"})
    assert "R-PRACTICE" in errs({"kind": "practice", "url": "https://lab.example.org", "review": {"explains": "explains", "hands_on": False}})
    assert not errs({"kind": "practice", "url": "https://github.com/x/y", "page_type": "repository"})
    assert not errs({"kind": "practice", "url": "https://site.org/t", "review": {"explains": "explains", "hands_on": True}})
    assert "R-GENERIC" in errs({"kind": "reading", "url": "https://ibm.com/think/topics/api", "review": {"explains": "mentions", "generic": True}})
    assert "R-SOURCE" in errs({"kind": "reading", "url": "https://www.linkedin.com/pulse/some-post"})


def test_transcript_block_stops_requests_and_marks_partial(monkeypatch):
    from profsagent.delivery import sources

    class Blocked(Exception):
        pass
    Blocked.__name__ = "IpBlocked"
    calls = []

    class Api:
        def fetch(self, vid, languages=None):
            calls.append(vid)
            raise Blocked()
    import youtube_transcript_api
    monkeypatch.setattr(youtube_transcript_api, "YouTubeTranscriptApi", Api)
    monkeypatch.setattr(sources, "_tx", {"blocked": None, "last": 0.0})
    monkeypatch.setattr(sources, "_cached", lambda ns, key, age, fn: fn())
    monkeypatch.setattr(sources.time, "sleep", lambda s: None)
    assert sources.transcript("a") is None and sources.transcript("b") is None
    assert calls == ["a"] and sources.transcripts_blocked()      # after the first block no request is sent
