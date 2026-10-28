"""Semantic checks VS-LOCOPY / VS-LOFIT / VS-CODUP (validation layer v2, Stage 4). Offline with a fake embedder that
gives chosen statements the same vector; the live test uses the local sentence-transformers model."""
import copy
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pytest

from profsagent.validate import engine, rules, semantic

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def no_model_after():
    yield
    semantic.configure(None)


def fake(aliases: dict[str, str] | None = None):
    """Every statement gets its own direction, except that a statement listed in `aliases` gets its target's."""
    aliases = aliases or {}
    dims = {}

    def embed(texts):
        v = np.zeros((len(texts), 128), dtype=np.float32)
        for i, t in enumerate(texts):
            v[i, dims.setdefault(aliases.get(t, t), len(dims))] = 1
        return v
    return embed


def vs_codes(state, stages=("cos", "los")):
    return sorted((x["code"], tuple(x["nodes"])) for x in rules.run(state, list(stages)) if x["code"].startswith("VS-"))


def test_off_without_a_model(s):
    semantic.configure(None)
    assert vs_codes(s) == []


def test_distinct_statements_are_quiet(s):
    semantic.configure(fake())
    assert vs_codes(s) == []


def test_lo_restating_its_co(s):
    co = {c["id"]: c for c in s["cos"]}
    lo = next(lo for lo in s["los"] if str(lo["bloom_level"]) == str(co[lo["parent_co"]]["bloom_level"]))
    semantic.configure(fake({lo["statement"]: co[lo["parent_co"]]["statement"]}))
    assert vs_codes(s) == [("VS-LOCOPY", (lo["id"], lo["parent_co"]))]
    lo["bloom_level"] = int(lo["bloom_level"]) - 1                  # a lower-level step may share its CO's wording
    assert vs_codes(s) == []


def test_lo_closer_to_another_co(s):
    lo = s["los"][0]
    other = next(c for c in s["cos"] if c["id"] != lo["parent_co"])
    semantic.configure(fake({lo["statement"]: other["statement"]}))
    assert vs_codes(s) == [("VS-LOFIT", (lo["id"], other["id"]))]


def test_cos_meaning_the_same(s):
    a, b = s["cos"][0], s["cos"][1]
    semantic.configure(fake({b["statement"]: a["statement"]}))
    assert ("VS-CODUP", (a["id"], b["id"])) in vs_codes(s, ["cos"])


def test_semantic_findings_are_warnings_and_classified(s):
    lo = s["los"][0]
    other = next(c for c in s["cos"] if c["id"] != lo["parent_co"])
    semantic.configure(fake({lo["statement"]: other["statement"]}))
    x = next(x for x in engine.check(s, ["los"]) if x["code"] == "VS-LOFIT")
    assert (x["severity"], x["family"], x["fixable_by"]) == ("warning", "semantic", "repair")
    codes = set(re.findall(r'\bv\("([A-Z0-9-]+)"', (ROOT / "src/profsagent/validate/semantic.py").read_text(encoding="utf-8")))
    assert codes and codes <= set(engine.FAMILY)


def test_errors_never_change(s):
    before = {x["code"] for x in rules.errors(rules.run(s))}
    semantic.configure(fake({s["los"][0]["statement"]: s["cos"][-1]["statement"]}))
    assert {x["code"] for x in rules.errors(rules.run(s))} == before


def test_switch_off_by_environment(monkeypatch):
    monkeypatch.setenv("PROFSAGENT_SEMANTIC", "off")
    assert semantic.configure_local() is False and not semantic.enabled()


def test_live_model_on_the_fixture(s):
    pytest.importorskip("sentence_transformers")
    assert semantic.configure_local() and semantic.MODEL == "all-MiniLM-L6-v2"
    out = [x for x in rules.run(s, ["cos", "los"]) if x["code"].startswith("VS-")]
    assert all(x["severity"] == "warning" and x["evidence"]["model"] == "all-MiniLM-L6-v2" for x in out)
    s2 = copy.deepcopy(s)
    co = s2["cos"][0]
    lo = next(lo for lo in s2["los"] if lo["parent_co"] == co["id"])
    lo["statement"], lo["bloom_level"] = co["statement"], co["bloom_level"]          # a verbatim copy
    assert ("VS-LOCOPY", (lo["id"], co["id"])) in vs_codes(s2)
