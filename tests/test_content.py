"""Phase 2 deliverable B (content/): deck checks, rendering and generate_material, offline with a fake LLM and the
committed clean CS-601 design (writes only to a temporary folder)."""
import json
import sys
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest
from pptx import Presentation

from profsagent.content import generate as G
from profsagent.content.checks import check_deck
from profsagent.content.models import Figure, LectureDeck, Quiz, Slide
from profsagent.content.render import fit
from profsagent.delivery.brief import build_briefs

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture(scope="module")
def st():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def brief(st):
    return build_briefs(st)[0]                                    # W01.L1, 2 h


@pytest.fixture
def lecture(brief):
    return G.lecture_input(brief)


def good_deck(lecture: dict, n: int = 18) -> LectureDeck:
    los = [lo["id"] for lo in lecture["learning_outcomes"]]
    slides = [Slide(kind="concept", title=f"Idea {i}", bullets=["one point", "another point"], notes="say this",
                    los=[los[i % len(los)]], sources=["C1"], minutes=lecture["minutes"] / n) for i in range(n - 4)]
    slides += [Slide(kind="worked_problem", title="Worked", bullets=["step 1", "step 2"], los=los, notes="n", minutes=lecture["minutes"] / n,
                     figure=Figure(kind="flow", steps=["Spec", "Prompt", "Test"])),
               Slide(kind="check", title="Check 1", quiz=Quiz(question="Which?", options=["a", "b", "c"], answer=1, explanation="b"),
                     los=los[:1], notes="n", minutes=lecture["minutes"] / n),
               Slide(kind="check", title="Check 2", quiz=Quiz(question="Why?", options=["x", "y", "z"], answer=0, explanation="x"),
                     los=los[:1], notes="n", minutes=lecture["minutes"] / n),
               Slide(kind="summary", title="Summary", bullets=["recap"], los=los, notes="n", minutes=lecture["minutes"] / n)]
    return LectureDeck(lecture_id=lecture["lecture_id"], title="T", slides=slides)


def codes(found, sev=None):
    return {x["code"] for x in found if sev is None or x["severity"] == sev}


CFG = G.cfg()


# ------------------------------------------------------------------ checks
def test_a_good_deck_has_no_errors(lecture):
    assert codes(check_deck(good_deck(lecture), lecture, {"C1"}, CFG), "error") == set()


def test_every_learning_outcome_must_be_served(lecture):
    deck = good_deck(lecture)
    lo = lecture["learning_outcomes"][0]["id"]
    for s in deck.slides:
        s.los = [x for x in s.los if x != lo]
    assert any(x["code"] == "D-LO" and lo in x["nodes"] for x in check_deck(deck, lecture, {"C1"}, CFG))


def test_unknown_ids_holes_and_bad_figures_are_errors(lecture):
    deck = good_deck(lecture)
    deck.slides[0].sources, deck.slides[1].los = ["L9"], ["CO9.LO9"]
    deck.slides[2].bullets = ["for {n} of {m} items"]
    deck.slides[3].figure = Figure(kind="flow", steps=["only one"])
    deck.slides[4].figure = Figure(kind="table", rows=[["a", "b"], ["c"]])
    assert {"D-REF", "D-TEMPLATE", "D-FIGURE"} <= codes(check_deck(deck, lecture, {"C1"}, CFG), "error")


def test_slide_count_follows_the_lecture_hours(lecture):
    assert "D-COUNT" in codes(check_deck(good_deck(lecture, n=6), lecture, {"C1"}, CFG), "error")   # 2 h: 16-28


def test_check_slides_need_a_valid_question(lecture):
    deck = good_deck(lecture)
    deck.slides[-3].quiz = None
    deck.slides[-2].quiz.answer = 7
    found = check_deck(deck, lecture, {"C1"}, CFG)
    assert sum(x["code"] == "D-QUIZ" and x["severity"] == "error" for x in found) == 2


def test_fewer_checks_than_hours_is_a_warning(lecture):
    deck = good_deck(lecture)
    deck.slides[-3].kind, deck.slides[-3].bullets = "concept", ["x"]
    assert "D-CHECK" in codes(check_deck(deck, lecture, {"C1"}, CFG), "warning")


# ------------------------------------------------------------------ rendering
def test_fit_shrinks_long_text_and_reports_what_cannot_fit():
    from pptx.util import Inches
    assert fit(["short"], Inches(6), Inches(1), 24, 14) == (24, True)
    size, ok = fit(["word " * 80], Inches(6), Inches(1.5), 24, 14)
    assert size < 24 or not ok
    assert fit(["word " * 400], Inches(3), Inches(0.5), 24, 14) == (14, False)


# ------------------------------------------------------------------ generate_material
class FakeLLM:
    """Returns the given decks (B1) and reviews (B2) in order; records each prompt and the models it was told to avoid."""
    def __init__(self, decks, reviews=()):
        self.decks, self.reviews, self.calls, self.excluded = decks, list(reviews), [], []

    def structured(self, *, system, user, model_cls, role, temperature, prompt_id, prompt_version, run_id=None,
                   exclude_models=frozenset()):
        self.calls.append(user)
        self.excluded.append(set(exclude_models))
        if prompt_id == "B2":
            r = self.reviews.pop(0)
            if isinstance(r, Exception):
                raise r
            return r, SimpleNamespace(endpoint="fake:reviewer:k1", prompt_tokens=10, output_tokens=20, latency_s=0.1)
        return self.decks.pop(0), SimpleNamespace(endpoint="fake:model:k1", prompt_tokens=10, output_tokens=20, latency_s=0.1)


@pytest.fixture
def run(st, tmp_path, monkeypatch):
    monkeypatch.setattr(G, "load_state", lambda run_id: st)
    monkeypatch.setattr(G, "out_dir", lambda run_id: tmp_path)
    monkeypatch.setattr("profsagent.content.review.out_dir", lambda run_id: tmp_path)
    monkeypatch.setattr(G, "verify", lambda deck, sources, cfg: ([], []))      # no embedding model in these tests
    return tmp_path


def test_generate_writes_slides_notes_quiz_and_manifest(run, lecture):
    llm = FakeLLM([good_deck(lecture)])
    m = G.generate_material("cs601", lecture["lecture_id"], llm=llm, log=lambda _: None)
    d = run / "material" / lecture["lecture_id"]
    assert len(llm.calls) == 1 and m["errors"] == 0 and m["cited"] == ["C1"]
    prs = Presentation(str(d / "slides.pptx"))
    assert len(prs.slides) == m["slides"] == 18 + 3                       # title + objectives + 18 + references
    assert "Answer: B. b" in prs.slides[2 + 15].notes_slide.notes_text_frame.text
    assert json.loads((d / "quiz.json").read_text(encoding="utf-8"))[0]["answer"] == 1
    notes = (d / "notes.md").read_text(encoding="utf-8")
    assert "## References" in notes and "Draft generated by ProfsAgent" in notes
    assert '"C1"' in llm.calls[0] and "Write the content slides" in llm.calls[0]


def test_a_deck_with_errors_is_repaired_once_and_kept_only_if_better(run, lecture):
    bad = good_deck(lecture, n=6)                                          # D-COUNT
    llm = FakeLLM([bad, good_deck(lecture)])
    m = G.generate_material("cs601", lecture["lecture_id"], llm=llm, log=lambda _: None)
    assert len(llm.calls) == 2 and "D-COUNT" in llm.calls[1] and m["errors"] == 0
    llm = FakeLLM([bad, good_deck(lecture, n=5)])                           # the repair is no better: keep the first
    m = G.generate_material("cs601", lecture["lecture_id"], llm=llm, log=lambda _: None)
    assert m["content_slides"] == 6 and m["errors"] == 1


def test_sources_are_course_resources_then_approved_lecture_resources(st, brief, run):
    lec = {"resources": {"items": {"reading": [{"title": "Approved", "url": "https://a.org", "kind": "reading", "status_decision": "approve"},
                                               {"title": "Pending", "url": "https://p.org", "kind": "reading"}]}}}
    (run / "lectures").mkdir()
    (run / "lectures" / f"{brief['lecture_id']}.json").write_text(json.dumps(lec), encoding="utf-8")
    src = G.gather_sources(st, "cs601", brief, include_pending=False, max_external=8)
    assert [s["title"] for k, s in src.items() if k.startswith("L")] == ["Approved"]
    assert all(s["approved"] for s in src.values()) and any(k.startswith("C") for k in src)
    assert len([k for k in G.gather_sources(st, "cs601", brief, True, 8) if k.startswith("L")]) == 2


# ------------------------------------------------------------------ verify: code syntax and citation match
from profsagent.content import review as R  # noqa: E402
from profsagent.content import verify as V  # noqa: E402


def code_deck(language: str, code: str) -> LectureDeck:
    return LectureDeck(lecture_id="X", title="T", slides=[Slide(kind="example", title="Code", bullets=["b"], notes="n",
                                                               figure=Figure(kind="code", language=language, code=code))])


def test_python_snippets_are_parsed():
    found, report = V.check_code(code_deck("python", "def f(x):\n    return x + 1\n"))
    assert found == [] and report[0]["status"] == "ok"
    found, report = V.check_code(code_deck("python", "def f(x)\n    return x\n"))
    assert found[0]["code"] == "D-CODE" and found[0]["nodes"] == ["slide 3"] and report[0]["status"] == "error"


def test_json_snippets_are_parsed():
    assert V.check_code(code_deck("json", '{"mcpServers": {"fs": {"command": "npx"}}}'))[0] == []
    assert V.check_code(code_deck("json", '{"mcpServers": {"fs": {"command": "npx",}}}'))[0][0]["code"] == "D-CODE"
    pair = '// Request\n{"id": 1, "method": "tools/call"}\n// Response\n{"id": 1, "result": {}}'
    assert V.check_code(code_deck("json", pair))[0] == []                              # a labelled request + response
    assert V.check_code(code_deck("json", pair.replace('"result": {}', '"result": {')))[0][0]["code"] == "D-CODE"


@pytest.mark.skipif(not __import__("shutil").which("gcc"), reason="needs gcc")
def test_c_fragments_are_wrapped_and_only_syntax_counts():
    assert V.check_code(code_deck("c", "int n = 3;\nprintf(\"%d\", n);"))[0] == []          # statements go inside main()
    assert V.check_code(code_deck("c", "int y = undeclared_helper(2);"))[0] == []            # unknown name: not syntax
    assert V.check_code(code_deck("c", "int n = 3\nprintf(\"%d\", n);"))[0][0]["code"] == "D-CODE"


def test_java_without_a_jdk_is_reported_as_not_verified(monkeypatch):
    real = V.shutil.which
    monkeypatch.setattr(V.shutil, "which", lambda name: None if name == "javac" else real(name))
    found, report = V.check_code(code_deck("java", "String s = q.isBlank() ? \"a\" : \"b\";"))
    assert found[0]["code"] == "D-UNVERIFIED" and found[0]["severity"] == "warning" and report[0]["status"] == "unchecked"


def test_java_wrapping_and_javac_messages():
    assert V.wrap_java("import java.util.*;\nclass A {}") .startswith("import")
    assert V.wrap_java("int twice(int x) {\n  return 2 * x;\n}").startswith("class Snippet {\nint twice")
    assert "void snippet()" in V.wrap_java("int n = 2;\nSystem.out.println(n);")
    blank = ("Snippet.java:9: error: cannot find symbol\n        if (query.blank()) {\n                 ^\n"
             "  symbol:   method blank()\n  location: variable query of type String\n1 error")
    assert V.java_problem(blank) == "String has no method blank()"                       # the bug in the first deck
    assert V.java_problem("Snippet.java:3: error: cannot find symbol\n  symbol:   class BoundedStack\n"
                          "  location: class Snippet") is None                            # undeclared in a fragment: fine
    assert V.java_problem("Snippet.java:2: error: ';' expected") == "';' expected"


def test_a_weak_citation_is_flagged():
    sources = {"C1": {"title": "about apples"}, "C2": {"title": "about pears"}, "C3": {"title": "about plums"}}
    vec = {"about apples": [1, 0, 0], "about pears": [0, 1, 0], "about plums": [0, 0, 1]}

    def embed(texts):
        import numpy as np
        return np.array([vec.get(t, [0.9, 0.1, 0.0]) for t in texts], dtype=float)       # every slide is about apples
    deck = LectureDeck(lecture_id="X", title="T", slides=[Slide(kind="concept", title="Apples", bullets=["a"], sources=["C1"]),
                                                          Slide(kind="concept", title="Apples", bullets=["a"], sources=["C3"])])
    found = V.check_grounding(deck, sources, 0.35, embed)
    assert [(x["code"], x["nodes"]) for x in found] == [("D-GROUND", ["slide 4", "C3"])]


# ------------------------------------------------------------------ the professor's review
def test_review_decisions_reach_material_json(run, lecture):
    llm = FakeLLM([good_deck(lecture)])
    G.generate_material("cs601", lecture["lecture_id"], llm=llm, log=lambda _: None)
    rows = R.write("cs601")
    lid = lecture["lecture_id"]
    assert rows[lid]["decision"] == "pending" and rows[lid]["status"] == "draft"
    p = run / "material" / "review.yaml"
    p.write_text(p.read_text(encoding="utf-8").replace("decision: pending", "decision: redo"), encoding="utf-8")
    assert R.apply("cs601")["refused"] == [{"lecture": lid, "why": "redo needs a reason"}]
    p.write_text(p.read_text(encoding="utf-8").replace("reason: ''", "reason: more worked examples"), encoding="utf-8")
    assert R.apply("cs601")["redo"] == 1 and R.redo_requests("cs601") == {lid: "more worked examples"}


def test_redo_feedback_goes_to_the_ai_and_an_approved_deck_is_protected(run, lecture):
    llm = FakeLLM([good_deck(lecture)])
    m = G.generate_material("cs601", lecture["lecture_id"], {"feedback": "more worked examples"}, llm=llm, log=lambda _: None)
    assert "more worked examples" in llm.calls[0] and "PROFESSOR" in llm.calls[0] and m["feedback"] == "more worked examples"
    mp = run / "material" / lecture["lecture_id"] / "material.json"
    mp.write_text(mp.read_text(encoding="utf-8").replace('"status": "draft"', '"status": "approved"'), encoding="utf-8")
    with pytest.raises(ValueError, match="approved"):
        G.generate_material("cs601", lecture["lecture_id"], llm=FakeLLM([good_deck(lecture)]), log=lambda _: None)
    assert G.generate_material("cs601", lecture["lecture_id"], {"force": True}, llm=FakeLLM([good_deck(lecture)]),
                               log=lambda _: None)["status"] == "draft"


# ------------------------------------------------------------------ the AI review (a professor in a hurry)
from profsagent.content.models import DeckReview, QuizAnswer, ReviewIssue  # noqa: E402

AI = {"review": "ai"}


def test_ai_review_by_another_model_answers_the_quiz_blind(run, lecture):
    deck = good_deck(lecture)                       # check slides are .pptx slides 18 (answer 1) and 19 (answer 0)
    ok = DeckReview(issues=[ReviewIssue(slide=5, severity="warning", kind="clarity", problem="term used before defined")],
                    quiz_answers=[QuizAnswer(slide=18, answer=1), QuizAnswer(slide=19, answer=0)], verdict="safe to teach")
    llm = FakeLLM([deck], [ok])
    m = G.generate_material("cs601", lecture["lecture_id"], AI, llm=llm, log=lambda _: None)
    assert len(llm.calls) == 2 and llm.excluded[1] == {"fake:model"}             # the writer never reviews its own deck
    review_prompt = llm.calls[1]
    assert '"Which?"' in review_prompt and '"answer"' not in review_prompt       # questions go without their key
    assert m["status"] == "ai-reviewed" and m["ai_review"]["model"] == "fake:reviewer" and not m["ai_review"]["repaired"]
    assert m["errors"] == 0 and [x["code"] for x in m["findings"]] == ["D-AI"]


def test_ai_review_errors_are_repaired_once_and_left_for_a_glance(run, lecture):
    bad = DeckReview(issues=[ReviewIssue(slide=4, severity="error", kind="fact", problem="MCP is not a REST API",
                                         fix="describe it as JSON-RPC")],
                     quiz_answers=[QuizAnswer(slide=18, answer=2, why="c is also right")], verdict="two errors")
    llm = FakeLLM([good_deck(lecture), good_deck(lecture)], [bad])
    m = G.generate_material("cs601", lecture["lecture_id"], AI, llm=llm, log=lambda _: None)
    assert len(llm.calls) == 3 and "D-QUIZKEY" in llm.calls[2] and "JSON-RPC" in llm.calls[2]
    assert m["ai_review"]["repaired"] and m["ai_review"]["quiz_disagreements"] == 1 and m["status"] == "ai-reviewed"
    assert m["errors"] == 0 and [x["code"] for x in m["findings"]] == ["D-AI-FIXED", "D-AI-FIXED"]


def test_a_failed_ai_review_keeps_the_draft(run, lecture):
    llm = FakeLLM([good_deck(lecture)], [RuntimeError("no quota")])
    m = G.generate_material("cs601", lecture["lecture_id"], AI, llm=llm, log=lambda _: None)
    assert m["status"] == "draft" and "no quota" in m["ai_review"]["error"] and (run / "material" / lecture["lecture_id"] / "slides.pptx").exists()


# ------------------------------------------------------------------ class sessions (2 x 90 min a week)
from profsagent.content.sessions import build_sessions  # noqa: E402


def test_each_week_becomes_two_90_minute_classes_in_schedule_order(st):
    briefs = build_briefs(st)
    sessions = build_sessions(st, 2, 90, briefs)
    weeks = sorted({b["week"] for b in briefs})
    assert len(sessions) == 2 * len(weeks) and {s["hours"] for s in sessions} == {1.5}
    for s in sessions:
        assert sum(p["minutes"] for p in s["parts"]) in (89, 90, 91)               # rounding of split topics
    for w in weeks:                                                                # topics keep the schedule's order
        order = [p["lecture_id"] for s in sessions if s["week"] == w for p in s["parts"]]
        assert list(dict.fromkeys(order)) == [b["lecture_id"] for b in briefs if b["week"] == w]
    s = next(s for s in sessions if len(s["parts"]) > 1)                           # a class spanning two topics
    los = {lo["id"] for p in s["parts"] for b in briefs if b["lecture_id"] == p["lecture_id"] for lo in b["learning_outcomes"]}
    assert {lo["id"] for lo in s["learning_outcomes"]} == los and " · " in s["topic"]


def test_a_class_deck_is_generated_with_its_topic_minutes(run, st):
    s = build_sessions(st, 2, 90)[1]
    lecture = G.lecture_input(s)
    assert lecture["minutes"] == 90 and lecture["parts"]
    llm = FakeLLM([good_deck(lecture)])
    m = G.generate_material("cs601", s["lecture_id"], llm=llm, log=lambda _: None)
    assert m["errors"] == 0 and m["lecture_id"].endswith(".S2") and '"parts"' in llm.calls[0]


def test_the_reviewer_is_barred_only_from_the_model_that_wrote_the_kept_deck(run, lecture):
    class TwoWriters(FakeLLM):                      # B1 by model a (with errors), the kept repair by model b
        writers = ["fake:a:k1", "fake:b:k1"]

        def structured(self, **kw):
            obj, rec = super().structured(**kw)
            if kw["prompt_id"] == "B1":
                rec = SimpleNamespace(**{**vars(rec), "endpoint": self.writers.pop(0)})
            return obj, rec
    llm = TwoWriters([good_deck(lecture, n=6), good_deck(lecture)], [DeckReview(verdict="ok")])
    m = G.generate_material("cs601", lecture["lecture_id"], AI, llm=llm, log=lambda _: None)
    assert llm.excluded[-1] == {"fake:b"} and m["status"] == "ai-reviewed"   # model a may review model b's deck


# ------------------------------------------------------------------ slides for C's delivery mix (outline)
from profsagent.content.checks import check_outline  # noqa: E402

OUTLINE = [{"id": "L.RECAP", "title": "Recap", "kind": "recap", "minutes": 5, "delivered_by": "slides"},
           {"id": "L.C1", "title": "Attention", "kind": "concept", "minutes": 30, "delivered_by": "video",
            "clip": "1:00–9:00 of \"Attention explained\""},
           {"id": "L.C2", "title": "Masking", "kind": "concept", "minutes": 25, "delivered_by": "in_class", "way": "simulation",
            "simulation": {"title": "Attention playground", "url": "https://example.org/attn"}},
           {"id": "L.QUIZ", "title": "Review quiz", "kind": "quiz", "minutes": 10, "delivered_by": "slides"}]


def mix_deck(*kinds_parts):
    return LectureDeck(lecture_id="L", title="T", slides=[Slide(kind=k, title=f"{k} {c}", bullets=["a", "b"], notes="n", component=c)
                                                        for k, c in kinds_parts])


def test_slides_follow_the_outline_and_code_fills_clips_and_links():
    deck = mix_deck(("recap", "L.RECAP"), ("watch", "L.C1"), ("debrief", "L.C1"), ("simulation", "L.C2"), ("quiz", "L.QUIZ"))
    G.fill_from_outline(deck, OUTLINE)
    assert check_outline(deck, OUTLINE) == []
    assert "1:00–9:00" in deck.slides[1].clip and deck.slides[3].link == "Attention playground — https://example.org/attn"


def test_missing_parts_watch_and_simulation_slides_and_order_are_reported():
    deck = mix_deck(("concept", "L.C1"), ("concept", "L.C2"), ("concept", "L.X"), ("recap", "L.RECAP"))
    found = check_outline(G.fill_from_outline(deck, OUTLINE), OUTLINE)
    got = {(x["code"], x["severity"]) for x in found}
    assert {("D-OUTLINE", "error"), ("D-OUTLINE", "warning"), ("D-WATCH", "warning"), ("D-SIM", "warning")} <= got
    assert any("open the class" in x["message"] for x in found) and any("close the class" in x["message"] for x in found)


def test_watch_and_simulation_slides_show_their_clip_and_link(tmp_path):
    from profsagent.content.render import render_markdown, render_pptx
    deck = G.fill_from_outline(mix_deck(("watch", "L.C1"), ("simulation", "L.C2")), OUTLINE)
    fr = {"course": "C", "footer": "C · L", "subtitle": "s", "draft_note": "d", "objectives": ["o"], "objectives_notes": "n"}
    render_pptx(deck, fr, {}, CFG, tmp_path / "s.pptx")
    text = " ".join(sh.text_frame.text for sl in Presentation(str(tmp_path / "s.pptx")).slides for sh in sl.shapes if sh.has_text_frame)
    assert "WATCH" in text and "1:00–9:00" in text and "https://example.org/attn" in text and "Try it" in text
    assert "**WATCH:** 1:00–9:00" in render_markdown(deck, fr, {})


# ------------------------------------------------------------------ narration script (content/narrate.py; the voice and
# PowerPoint parts need Windows and are tried by hand: run_content.py narrate)
from profsagent.content.narrate import narration_script  # noqa: E402


def test_the_narration_reads_notes_and_asks_before_it_answers(lecture):
    deck = good_deck(lecture)
    deck.slides[0].notes = "Attention → weights `softmax` [C1] (CO1.LO1)"
    fr = {"course": "C", "subtitle": "Week 1 · M · 90 min", "objectives": ["Explain attention (CO1.LO1)"]}
    texts = narration_script(deck, fr)
    assert len(texts) == 2 + len(deck.slides) + 1                        # title, objectives, content, references
    assert texts[2] == "Attention to weights softmax"                    # no markdown, ids or arrows read aloud
    q = next(t for t in texts if "Here is a question" in t)
    assert q.index("Pause the video") < q.index("The answer is B")


def test_a_class_spanning_two_topics_has_one_recap_first_and_one_quiz_last():
    parts = [{"id": "A.C3", "kind": "concept", "minutes": 40}, {"id": "A.QUIZ", "kind": "quiz", "minutes": 10},
             {"id": "B.RECAP", "kind": "recap", "minutes": 5}, {"id": "B.C1", "kind": "concept", "minutes": 35}]
    out = G.class_edges(parts)
    assert [p["id"] for p in out] == ["B.RECAP", "A.C3", "B.C1", "A.QUIZ"]
    assert sum(p["minutes"] for p in out) == 90 and G.class_edges(parts[:1]) == parts[:1]


# ------------------------------------------------------------------ the professor's own material (content/attach.py)
from profsagent.content import attach as A  # noqa: E402
from profsagent.content.models import AttachedQuestion, AttachedReport, Gap  # noqa: E402


def _vec(texts):
    """A fake embedding: 'attention' texts close to each other, everything else apart."""
    import numpy as np
    return np.array([[1.0, 0.0] if "attention" in t.lower() else [0.0, 1.0] for t in texts], dtype=float)


def test_attachments_are_read_and_unreadable_ones_reported(tmp_path, monkeypatch):
    from pptx import Presentation as P
    monkeypatch.setattr(A, "RUNS", tmp_path)
    d = tmp_path / "r" / "delivery" / "attachments" / "W01.L1"
    d.mkdir(parents=True)
    prs = P()
    s = prs.slides.add_slide(prs.slide_layouts[1])
    s.shapes.title.text, s.placeholders[1].text = "Attention", "queries meet keys"
    s.notes_slide.notes_text_frame.text = "say softmax"
    prs.save(str(d / "deck.pptx"))
    (d / "notes.md").write_text("# Attention\nweights sum to one", encoding="utf-8")
    (d / "pic.png").write_bytes(b"\x89PNG")
    parts = A.read_attachments("r", [f"delivery/attachments/W01.L1/{n}" for n in ("deck.pptx", "notes.md", "pic.png")])
    assert [p["id"] for p in parts] == ["P1", "P2", "P3"]
    assert "queries meet keys" in parts[0]["text"] and "Notes: say softmax" in parts[0]["text"]
    assert "weights sum to one" in parts[1]["text"] and parts[2]["error"] and not parts[2]["text"]


def test_coverage_and_the_checks_on_the_ai_report():
    los = [{"id": "LO1", "statement": "Explain attention weights"}, {"id": "LO2", "statement": "Train a tokenizer"}]
    parts = [{"id": "P1", "text": "attention " * 50}]
    cover = A.coverage(los, parts, CFG, embed=_vec)
    assert [c["status"] for c in cover] == ["covered", "missing"]
    rep = AttachedReport(quiz=[AttachedQuestion(question="q", options=["a", "a", "b"], answer=0, source="P9")],
                         gaps=[Gap(lo_id="LO2", status="covered"), Gap(lo_id="LO7", status="missing")])
    found = A.check_report(rep, {"LO1", "LO2"}, {"P1"}, cover, ["quiz", "gap_check"])
    assert {x["code"] for x in found} == {"A-QUIZ", "A-REF", "A-MISSING", "A-GAP"}
    assert A.valid_quiz(rep, found) == []
    ok = AttachedReport(quiz=[AttachedQuestion(question="q", options=["a", "b", "c"], answer=0, source="[P1] slide 3, slide 5")])
    assert A.check_report(ok, {"LO1"}, {"P1"}, cover, ["quiz"]) == []                 # a precise citation is fine


def test_attach_material_writes_a_report_and_can_make_slides_from_the_material(run, st, monkeypatch):
    from profsagent.delivery import common, survey as sv
    lid = build_briefs(st)[0]["lecture_id"]
    monkeypatch.setattr(A, "RUNS", run.parent)
    monkeypatch.setattr(A, "load_state", lambda run_id: st)
    (run.parent / "cs601" / "delivery" / "attachments" / lid).mkdir(parents=True)
    (run.parent / "cs601" / "delivery" / "attachments" / lid / "n.md").write_text("Attention is a soft lookup. " * 30, encoding="utf-8")
    monkeypatch.setattr(sv, "load", lambda r: {"lectures": {lid: {"attach_material": "yes", "attachments": [f"delivery/attachments/{lid}/n.md"],
                                                                     "attach_tasks": ["summary", "quiz", "gap_check", "slides"]}}})
    monkeypatch.setattr(common, "embed", _vec)
    lo = build_briefs(st)[0]["learning_outcomes"][0]["id"]
    rep = AttachedReport(summary="s", quiz=[AttachedQuestion(question="q", options=["a", "b", "c"], answer=1, source="P1")],
                         gaps=[Gap(lo_id=lo, status="partly", add="an example")])

    class Fake(FakeLLM):
        def structured(self, **kw):
            if kw["prompt_id"] == "B3":
                self.calls.append(kw["user"])
                return rep, SimpleNamespace(endpoint="fake:m:k", prompt_tokens=1, output_tokens=1)
            return super().structured(**kw)
    lecture = G.lecture_input(build_briefs(st)[0])
    llm = Fake([good_deck(lecture)])
    monkeypatch.setattr(G, "LLMClient", lambda *a: llm)
    m = A.attach_material("cs601", lid, llm=llm, log=lambda _: None)
    assert "[P1]" in llm.calls[0] and len(m["quiz"]) == 1 and m["gap_table"][0]["ai"] == "partly"
    assert "professor_material" in llm.calls[1] and m["slides"]["files"]                 # the deck was made from it
    md = (run / "material" / lid / "attached.md").read_text(encoding="utf-8")
    assert "## Gap check" in md and "## Quiz" in md and "### Answers" in md


# ------------------------------------------------------------------ the professor's style (content/style.py)
def test_a_style_is_learned_from_a_deck_and_used_as_the_template(tmp_path, monkeypatch, lecture):
    from pptx import Presentation as P
    from profsagent.content import style as S
    from profsagent.content.render import render_pptx
    monkeypatch.setattr(S, "out_dir", lambda run_id: tmp_path)
    prs = P()
    for i in range(3):
        s = prs.slides.add_slide(prs.slide_layouts[1])
        s.shapes.title.text = f"How We Build Model {i}"
        s.placeholders[1].text_frame.text = "we compute the scores first"
        s.placeholders[1].text_frame.add_paragraph().text = "then we normalise them with softmax"
    src = tmp_path / "mine.pptx"
    prs.save(str(src))
    prof = S.learn_style("r", [src])
    w = prof["writing"]
    assert w["bullets_per_slide"] == 2 and w["title_case"] == "Title Case" and w["voice"] == "we"
    assert prof["look"]["font"] and prof["look"]["colors"].get("accent")
    cfg = S.apply_look(CFG, S.load_style("r"))
    assert cfg["render"]["template"].endswith("template.pptx") and S.for_b1(S.load_style("r"))["voice"] == "we"
    fr = {"course": "C", "footer": "f", "subtitle": "s", "draft_note": "d", "objectives": ["o"], "objectives_notes": "n"}
    n, _ = render_pptx(good_deck(lecture), fr, {}, cfg, tmp_path / "out.pptx")
    out = P(str(tmp_path / "out.pptx"))
    assert len(out.slides) == n and "How We Build" not in " ".join(sh.text_frame.text for s in out.slides for sh in s.shapes if sh.has_text_frame)


# ------------------------------------------------------------------ student mode (content/student.py)
def test_the_student_page_has_the_questions_but_not_the_notes_or_answer_keys(lecture):
    from profsagent.content.student import student_page
    deck = good_deck(lecture)
    deck.slides[0].notes = "SECRET professor note"
    fr = {"course": "C", "subtitle": "s", "objectives": ["Explain things (CO1.LO1)"]}
    page = student_page(deck, fr, {"C1": {"title": "Book", "year": 2020, "url": "https://x.org"}})
    assert "SECRET" not in page and "Answer:" not in page and "Which?" in page and 'data-answer="1"' in page
    assert "Explain things</li>" in page and "https://x.org" in page and "score: 0 / 2" in page


# ------------------------------------------------------------------ animation (content/animate.py, needs manim)
def test_a_flow_becomes_a_short_animated_clip(tmp_path):
    pytest.importorskip("manim")
    from profsagent.content.animate import _clip
    p = _clip(["Tokens", "Scores", "Softmax"], 5.0, 4.0, 2.0, CFG["render"]["colors"], tmp_path / "anim" / "f.mp4")
    assert p.exists() and p.stat().st_size > 10_000


# ------------------------------------------------------------------ a class taught as 3-4 video parts (content/lesson.py)
from profsagent.content import lesson as LS  # noqa: E402
from profsagent.content.models import LessonPlan, PlanPart, TeachingPart, TeachingSlide  # noqa: E402

REF = ("Attention lets every position look at every other position. The scores are scaled by the square root of the key "
       "dimension so the softmax does not saturate when the dimension grows large and gradients stay useful. ") * 20


def teaching(n_slides=6, words=160, refs=("C1#1",), narration=None):
    q = Quiz(question="Why scale?", options=["speed", "stable softmax", "memory", "masking"], answer=1, explanation="it keeps it stable")
    return TeachingPart(slides=[TeachingSlide(title=f"Idea {i}", bullets=["scores", "softmax"], refs=list(refs),
                                              narration=narration or ("you compute the scores and then " * (words // 6)))
                                for i in range(n_slides)], recap="We scaled the scores. The softmax stayed stable.", quiz=[q, q, q])


def test_a_part_must_teach_in_its_own_words_and_end_with_three_questions():
    known = {"C1#1": REF}
    assert LS.check_part(teaching(), known, CFG) == []
    copied = " ".join(REF.split()[:30])
    found = LS.check_part(teaching(narration=copied + " and more words to explain " * 20), known, CFG)
    assert "L-COPY" in codes(found, "error")
    found = LS.check_part(teaching(n_slides=2, words=30, refs=("C9#9",)), known, CFG)
    assert {"L-COUNT", "L-NARRATION", "L-REF"} <= codes(found, "error")
    tp = teaching()
    tp.quiz = tp.quiz[:2]
    assert "L-QUIZ" in codes(LS.check_part(tp, known, CFG), "error")


def test_teach_class_plans_parts_teaches_each_and_asks_before_answering(run, st, monkeypatch):
    from profsagent.content.narrate import narration_script
    lid = "W01.S1"
    monkeypatch.setattr(LS, "load_state", lambda run_id: st)
    monkeypatch.setattr(LS, "reference_text", lambda src, max_pages=10: REF if src.get("url") else "")
    los = [x["id"] for x in G.units(st)[lid]["learning_outcomes"]]
    plan = LessonPlan(parts=[PlanPart(title=f"Part {i}", los=los, teaches="t", key_ideas=["a", "b"], example="e", minutes=10)
                             for i in range(3)])

    class Fake:
        def __init__(self):
            self.calls = []

        def structured(self, *, system, user, model_cls, prompt_id, **kw):
            self.calls.append((prompt_id, user))
            obj = plan if prompt_id == "B4" else teaching(refs=())
            return obj, SimpleNamespace(endpoint="fake:m:k", prompt_tokens=1, output_tokens=1)
    llm = Fake()
    m = LS.teach_class("cs601", lid, llm=llm, embed=_vec, log=lambda _: None)
    assert [c[0] for c in llm.calls] == ["B4", "B5", "B5", "B5"] and len(m["parts"]) == 3
    assert "Attention lets every position" in llm.calls[1][1]                       # the part is grounded in the reference
    d = run / "material" / lid / "lesson" / "part_2"
    deck = LectureDeck.model_validate(json.loads((d / "deck.json").read_text(encoding="utf-8")))
    kinds = [s.kind for s in deck.slides]
    assert kinds[-6:] == ["check", "answer"] * 3 and kinds[-7] == "summary"           # each question, then its answer
    fr = {"course": "C", "subtitle": "s", "objectives": ["o"]}
    said = narration_script(deck, fr)
    ask = next(t for t in said if t.startswith("Quiz question 1"))
    assert "Pause the video" in ask and "The answer is" not in ask                    # the question slide never gives it away
    assert any(t.startswith("The answer is B") for t in said)
    assert (run / "material" / lid / "lesson" / "lesson.md").exists() and (d / "student.html").exists()
    assert any(f["code"] == "L-UNCITED" for f in m["parts"][0]["findings"])          # slides citing nothing are flagged
