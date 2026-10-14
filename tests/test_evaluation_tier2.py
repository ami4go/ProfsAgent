"""Evaluation tier 2 (hold-out reference comparison). Offline with an exact-match fake embedder; the live test uses the
local sentence-transformers model and the saved cse201-dev-05 run."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import numpy as np
import pytest

from profsagent.evaluate import reference as ref_eval

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"


@pytest.fixture
def s():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def exact_embed():
    dims = {}

    def embed(texts):
        v = np.zeros((len(texts), 256), dtype=np.float32)
        for i, t in enumerate(texts):
            v[i, dims.setdefault(t.lower(), len(dims))] = 1
        return v
    return embed


def self_reference(s):
    """The design itself written as a reference sheet: every metric should be perfect."""
    v = ref_eval.design_view(s)
    return {"code": "SELF", "name": "self", "level": s["level"], "credits": v["credits"], "cos": v["cos"],
            "topics": [(t, w) for t, w in v["topics"]], "weeks": s["weeks"], "assessment": v["assessment"],
            "prereqs": v["prereqs"], "resources": v["resources"]}


def test_rouge_l():
    assert ref_eval.rouge_l("implement a parser", "implement a parser") == 1.0
    assert ref_eval.rouge_l("design caches", "explain proofs") == 0.0
    assert ref_eval.rouge_l("a b c d", "a c d e") == 0.75                     # LCS a c d: P = R = 3/4


def test_kendall_tau_b():
    assert ref_eval.kendall_tau_b([1, 2, 3, 4], [2, 3, 5, 9]) == 1.0
    assert ref_eval.kendall_tau_b([1, 2, 3, 4], [4, 3, 2, 1]) == -1.0
    assert ref_eval.kendall_tau_b([1, 2], [1, 2]) is None


def test_soft_prf():
    assert ref_eval.soft_prf(np.eye(3)) == {"precision": 1.0, "recall": 1.0, "f1": 1.0}
    m = np.array([[1.0, 0.0, 0.0]])                                            # one design item for three reference items
    assert ref_eval.soft_prf(m)["precision"] == 1.0 and ref_eval.soft_prf(m)["recall"] == round(1 / 3, 3)


def test_design_against_itself_is_perfect(s):
    ev = ref_eval.evaluate_reference(s, self_reference(s), exact_embed(), match_sim=0.9)
    sm = ev["summary"]
    assert sm["topic_f1"] == sm["topic_soft_f1"] == sm["co_soft_f1"] == sm["co_rouge_l"] == 1.0
    assert sm["order_tau_b"] == 1.0 and sm["assessment_tv"] == 0.0 and sm["prereq_jaccard"] == 1.0
    assert ev["structure"]["co_count_diff"] == 0 and ev["structure"]["credits_equal"] and not ev["topics"]["missed_reference"]


def test_reversed_order_and_missing_topics_are_measured(s):
    ref = self_reference(s)
    last = max(w for _, w in ref["topics"])
    ref["topics"] = [(t, last + 1 - w) for t, w in ref["topics"]][:-4] + [("Quantum error correction", 3)]
    ev = ref_eval.evaluate_reference(s, ref, exact_embed(), match_sim=0.9)
    assert ev["summary"]["order_tau_b"] < -0.9
    assert ev["topics"]["recall"] < 1 and ev["topics"]["precision"] < 1 and "Quantum error correction" in ev["topics"]["missed_reference"]


def test_assessment_split_distance(s):
    ref = self_reference(s)
    ref["assessment"] = [("endsem", 100)]
    ev = ref_eval.evaluate_reference(s, ref, exact_embed(), match_sim=0.9)
    endsem = ev["assessment"]["design"].get("endsem", 0) / 100
    assert ev["assessment"]["total_variation"] == round(1 - endsem, 3) and ev["assessment"]["type_jaccard"] < 1


def test_reference_loader_drops_events():
    ref = ref_eval.load_reference("CSE201")
    assert ref["weeks"] == 13 and ref["prereqs"] == ["CSE101", "CSE102"] and len(ref["cos"]) == 5
    assert not any("review" in t.lower() and "semester" in t.lower() for t, _ in ref["topics"])     # "End semester review"
    assert {t for t, _ in ref["assessment"]} == {"quiz", "assignment", "project", "midsem", "endsem"}


def test_live_cse201_hold_out():
    pytest.importorskip("sentence_transformers")
    s = json.loads((ROOT / "runs/cse201-dev-05/state.json").read_text(encoding="utf-8"))
    ev = ref_eval.evaluate_reference(s, ref_eval.load_reference("CSE201"))
    sm = ev["summary"]
    assert sm["reference"] == "CSE201" and all(0 <= sm[k] <= 1 for k in ("topic_f1", "topic_soft_f1", "co_soft_f1", "assessment_tv"))
    assert sm["prereq_jaccard"] == 1.0 and sm["order_tau_b"] > 0          # same prerequisites; topic order broadly agrees


def test_compound_titles_cover_each_part():
    assert ref_eval.title_parts("I/O streams and object serialization") == [
        "I/O streams and object serialization", "I/O streams", "object serialization"]
    embed = exact_embed()
    design, reference = ["I/O streams and object serialization"], ["Object serialization", "I/O streams", "JavaFX"]
    assert ref_eval._coverage(design, reference, embed, 0.9) == round(2 / 3, 3)     # 1-1 matching could credit only one
