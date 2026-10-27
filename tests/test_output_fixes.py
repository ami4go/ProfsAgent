"""Fixes to the course sheet output (28 Oct 2026, docs/decisions.md): CO length and V11 for LOs only, ISBN and year from
one and the same edition, and the template's activity column without exams. No network: Open Library is faked."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from profsagent.config import pedagogy  # noqa: E402
from profsagent.render.course_template import template_data  # noqa: E402
from profsagent.research import resources  # noqa: E402
from profsagent.validate import rules  # noqa: E402

FIX = json.loads((Path(__file__).parent / "fixtures" / "cs601_design_state.json").read_text(encoding="utf-8"))


def test_co_length_limit_follows_the_iiitd_corpus():
    assert pedagogy()["thresholds"]["statement_words"]["CO"] == [8, 35]
    st = json.loads(json.dumps(FIX))
    st["cos"][0]["statement"] = " ".join([st["cos"][0]["statement"]] + ["padding"] * 40)
    assert any(x["code"] == "VT-LEN" and x["nodes"] == [st["cos"][0]["id"]] for x in rules.run(st, ["cos"]))


def test_v11_visibility_is_checked_for_los_only():
    cos = [x for x in rules.run(FIX, ["cos"]) if x["code"] == "V11" and "not visible" in x["message"]]
    los = [x for x in rules.run(FIX, ["los"]) if x["code"] == "V11" and "not visible" in x["message"]]
    assert cos == [] and los                         # COs keep condition/degree in their fields; LOs must show them


def test_activity_column_lists_only_assignments_labs_tutorials_and_project_work():
    acts = " ".join(t["activities"] for t in template_data(FIX)["topics"])
    assert "Tutorial" in acts
    assert not any(w in acts for w in ("Mid-sem", "End-sem", "Midsem", "Endsem", "Quiz"))


# ---- the JavaScript case from the Web Development run: a 2017 CreateSpace reprint's ISBN had been paired with 1996
WORK = {"docs": [{"key": "/works/OL1643770W", "title": "JavaScript", "subtitle": "The Definitive Guide", "author_name": ["David Flanagan"],
                  "author_key": ["OL183270A"], "first_publish_year": 1996, "isbn": ["9781548955489", "9781491952023"], "publisher": ["CreateSpace"]}]}
EDITIONS = {"entries": [
    {"key": "/books/A", "title": "JavaScript", "subtitle": "the Definitive Guide", "publish_date": "2017", "isbn_13": ["9781548955489"],
     "authors": [{"key": "/authors/OL183270A"}], "publishers": ["CreateSpace Independent Publishing Platform"]},
    {"key": "/books/B", "title": "JavaScript", "subtitle": "o guia definitivo", "publish_date": "2013", "isbn_13": ["9788565837194"],
     "languages": [{"key": "/languages/por"}], "publishers": ["Bookman"]},
    {"key": "/books/C", "title": "JavaScript", "subtitle": "The Definitive Guide", "publish_date": "Jun 02, 2020", "isbn_13": ["9781491952023"],
     "authors": [{"key": "/authors/OL183270A"}], "publishers": ["O'Reilly Media"]},
    {"key": "/books/D", "title": "JavaScript", "subtitle": "The Definitive Guide", "publish_date": "2011", "isbn_13": ["9780596805524"],
     "authors": [{"key": "/authors/OL183270A"}], "publishers": ["O'Reilly"]},
]}


def fake_get(url, params):
    return EDITIONS if url.endswith("/editions.json") else WORK if "search.json" in url else None


def test_isbn_year_and_publisher_come_from_one_edition(monkeypatch):
    monkeypatch.setattr(resources, "_cached_get", fake_get)
    c = resources.openlibrary("JavaScript The Definitive Guide", 1)[0]
    assert c["identifier"]["isbn"] == "9781491952023" and c["year"] == 2020 and c["publisher"] == "O'Reilly Media"
    assert c["first_published"] == 1996 and c["url"].endswith("/books/C")


def test_no_proper_edition_means_no_isbn(monkeypatch):
    only_reprint = {"entries": [EDITIONS["entries"][0]]}
    monkeypatch.setattr(resources, "_cached_get", lambda url, p: only_reprint if url.endswith("/editions.json") else WORK)
    c = resources.openlibrary("JavaScript The Definitive Guide", 1)[0]
    assert c["identifier"]["isbn"] is None and c["year"] == 1996
