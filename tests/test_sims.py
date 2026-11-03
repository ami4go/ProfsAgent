"""The simulation catalogue (simulations/, src/profsagent/sims): the 12 types, every entry's sim.yaml, the single-file
builds, and the classifier's labels. Fast: no browser (each entry's own qa.py runs with `python scripts/sims.py qa`)."""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest  # noqa: E402

from profsagent.sims import catalogue as C  # noqa: E402
from profsagent.sims import classify  # noqa: E402


def test_the_12_types_are_complete():
    ts = C.types()["types"]
    assert [t["id"].split("-")[0] for t in ts] == [str(i) for i in range(1, 13)]
    for t in ts:
        assert t["name"] and t["does"] and t["engine"] and t["check"] and len(t["examples"]) >= 8
    assert len(C.types()["none_examples"]) >= 8 and set(C.types()["levels"]) == {"L0", "L1", "L2", "L3", "L4", "L5"}


def test_every_entry_is_valid_and_unique():
    es = C.entries()
    assert len(es) >= 8
    assert len({e["id"] for e in es}) == len(es)
    bad = {e["id"]: C.problems(e) for e in es if C.problems(e)}
    assert not bad, bad


def test_problems_are_found(tmp_path):
    src = C.SIMS / "os.memory.page_replacement"
    d = tmp_path / "os.memory.page_replacement"
    shutil.copytree(src, d)
    e = {**C.get("os.memory.page_replacement"), "_dir": d}
    assert C.problems(e) == []
    assert any("unknown type" in p for p in C.problems({**e, "type": ["13-telepathy"]}))
    assert any("not in the IIIT-D catalogue" in p for p in C.problems({**e, "courses": ["XYZ999"]}))
    assert any("version" in p for p in C.problems({**e, "version": "one"}))
    assert any("summary" in p for p in C.problems({**e, "summary": "short"}))
    assert any("class_example must be" in p for p in C.problems({**e, "class_example": "yes"}))
    (d / "page.src.html").write_text((src / "page.src.html").read_text(encoding="utf-8").replace('<script src="../_engines/share/share.js"></script>', ""), encoding="utf-8")
    assert any("share.js" in p for p in C.problems(e))           # class examples need the page to report its setup
    (d / "page.src.html").write_text('<script src="https://cdn.example.org/x.js"></script>', encoding="utf-8")
    assert any("internet" in p for p in C.problems(e))
    assert any("missing" in p for p in C.problems({k: v for k, v in e.items() if k != "checks"}))


@pytest.mark.parametrize("sim_id", [e["id"] for e in C.entries()])
def test_build_is_one_offline_file(sim_id):
    e = C.get(sim_id)
    html = C.build(e).read_text(encoding="utf-8")
    assert not re.search(r'<(script|link)[^>]+(src|href)="\.\./', html), "a shared file was not inlined"
    assert not re.search(r'<(script|link)[^>]+(src|href)="(https?:)?//', html), "loads something from the internet"
    if e["engine"].get("name") == "manim-web":
        assert "Permission is hereby granted" in html and "manim-web" in html    # the MIT notice ships with the page


def test_classifier_labels_are_well_formed():
    rows = classify.read_labels()
    assert len(rows) == 165
    ids = set(classify.types_ids()) | {classify.NONE}
    assert all(r["ok"] and r["ok"] <= ids for r in rows)
    assert len({r["dept"] for r in rows}) == 15


def test_external_index_and_parsers():
    """The links index (simulations/external/index.json) and the parsers that build it from PhET's and Falstad's lists."""
    from profsagent.sims import external as X
    es = X.entries()
    assert len(es) > 100 and len({e["id"] for e in es}) == len(es)
    sites = X.sources()["sites"]
    assert all(e["url"].startswith("https://") and e["site"] in sites and e["title"] for e in es)
    meta = {"keywords": {"7": {"strings": {"en": "Motion"}}},
            "projects": [{"simulations": [
                {"name": "projectile-motion", "highGradeLevel": 3, "keywordIds": [7],
                 "localizedSimulations": {"en": {"title": "Projectile Motion", "simPageUrl": "/en/simulations/projectile-motion",
                                                 "description": "Blast a car out of a cannon.", "learningGoals": "Predict range.<br/>Explain."}}},
                {"name": "kids-only", "highGradeLevel": 1, "localizedSimulations": {"en": {"title": "Kids"}}}]}]}
    ph = X.parse_phet(meta)
    assert [p["title"] for p in ph] == ["Projectile Motion"] and ph[0]["topics"] == ["Motion"]
    assert ph[0]["url"] == "https://phet.colorado.edu/en/simulations/projectile-motion"
    applets = X.parse_falstad_applets('<h2>Signal Processing</h2><table><tr><td><big><b>\n<a href="fourier/">\nFourier Series Applet\n</a></b></big><br><small>\n'
                                      'Sines and cosines.\n</small></td></tr></table>')
    assert applets == [{"id": "fourier", "title": "Fourier Series", "url": "https://www.falstad.com/fourier/", "summary": "Sines and cosines.",
                        "topics": ["Signal Processing"]}]
    circ = X.parse_falstad_circuits('<li><b>Basics</b><ul><li id="ohms"><a href="e-ohms.html">Ohm\'s Law</a><li><a href="e-ohms.html">Ohm\'s Law</a>')
    assert len(circ) == 1 and circ[0]["url"] == "https://www.falstad.com/circuit/e-ohms.html" and circ[0]["topics"][0] == "Basics"
