"""Phase 1 outputs: the teaching-hours / workload file and the textbook rule. Offline (OpenLibrary is faked)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.agents import pipeline
from profsagent.llm.prompts import load_prompt
from profsagent.render import workload
from profsagent.validate import rules

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def test_workload_totals_and_weeks(s, tmp_path):
    d = workload.weekly(s)
    assert len(d["rows"]) == s["weeks"]
    lec = sum(float(i["hours"]) for w in s["schedule"]["weeks"] for i in w["items"])
    assert d["total"]["lecture_h"] == round(lec, 1) and d["total"]["tutorial_h"] == s["ltp"]["T"] * s["weeks"]
    lab_weeks = {x["week"] for x in s["labs_tutorials"]["labs"]}
    assert d["total"]["lab_h"] == s["ltp"]["P"] * len(lab_weeks)
    assert d["target_outside_h"] == {"min": 10.0, "max": 12.0} and d["avg_outside_h"] is not None
    workload.write(s, tmp_path)
    md = (tmp_path / "workload.md").read_text(encoding="utf-8")
    assert "Average outside-lecture work" in md and "| 13 |" in md
    csv_rows = (tmp_path / "workload.csv").read_text(encoding="utf-8").splitlines()
    assert csv_rows[0].startswith("week,") and csv_rows[-1].startswith("total,") and len(csv_rows) == s["weeks"] + 2


def test_missing_textbook_is_a_warning(s):
    s["resource_policy"] = {"textbook_policy": "mixed"}
    s["resources"] = [r for r in s["resources"] if not pipeline.is_book(r)]
    msgs = [x["message"] for x in rules.run(s, ["resources"]) if x["code"] == "V15"]
    assert any("no verified textbook" in m for m in msgs)
    s["resource_policy"] = {"textbook_policy": "reading_list"}
    assert not any("no verified textbook" in x["message"] for x in rules.run(s, ["resources"]))


def fake_openlibrary(books):
    def _ol(query, limit=3):
        return [{"candidate_id": f"OL:{i}", "kind": "book", "title": t, "authors": a, "year": y, "identifier": {"isbn": "978"},
                 "url": f"https://openlibrary.org/works/{i}", "source": "openlibrary"} for i, (t, a, y) in enumerate(books)]
    return _ol


def test_textbook_found_only_when_its_title_fits_the_course(s, monkeypatch):
    monkeypatch.setattr(pipeline, "openlibrary", fake_openlibrary([
        ("Commerce and Software Development Best Practices", ["A. Writer"], 2026),      # 2 of 3 words: too loose
        ("Software Testing: Specifications and Agents", ["T. Expert"], 2020)]))           # testing, specifications ...
    s["cco_compact"]["course_name"] = "Software Development using AI"
    cands = {}
    book = pipeline._find_textbook(s, cands)
    assert book and book["title"].startswith("Software Testing") and book["verification"]["verified"]
    assert book["role"] == "primary" and book["supports_topics"] and book["candidate_id"] in cands
    monkeypatch.setattr(pipeline, "openlibrary", fake_openlibrary([("Cooking for Busy People", ["C. Chef"], 2019)]))
    assert pipeline._find_textbook(s, {}) is None


def test_lo_prompt_has_the_self_check():
    p = load_prompt("G6")
    assert p.version == "0.3.0" and "Self-check before you answer" in p.system_tpl
