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
