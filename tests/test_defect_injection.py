"""Direct-injection suite (validation layer v2, Stage 1): every benchmark defect written into a clean design must be
reported by its validator. No LLM calls. Known gaps are expected failures (strict), so closing one fails the suite
until its `known_gap` is removed from profsagent/bench/defects.py."""
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest

from profsagent.bench.defects import DEFECTS
from profsagent.validate import rules

FIXTURE = ROOT / "tests/fixtures/cs601_design_state.json"   # copy of runs/cs601-02/state.json (CS-601, template + Neo4j KB)

# Errors the clean design already has. V23: CO2's claimed link to PSO "CSAI-PSO1" is not evidenced by any assessed
# activity in that run. Pinned so that any NEW error on the clean design (a false alarm) fails the suite.
CLEAN_BASELINE_ERRORS = {"V23"}


@pytest.fixture(scope="module")
def base():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


def error_codes(state):
    return {x["code"] for x in rules.errors(rules.run(state))}


def test_clean_design_matches_the_baseline(base):
    assert error_codes(base) == CLEAN_BASELINE_ERRORS


@pytest.mark.parametrize("d", [pytest.param(d, id=d.name, marks=pytest.mark.xfail(strict=True, reason=d.known_gap) if d.known_gap else ())
                               for d in DEFECTS])
def test_defect_is_reported(base, d):
    mutated = d.apply(base)
    assert mutated != base, "the defect did not change the design"
    fired = error_codes(mutated)
    assert fired & set(d.expected), f"expected one of {d.expected}, got new errors {sorted(fired - CLEAN_BASELINE_ERRORS)}"


def test_catalogue_covers_the_benchmark_mutations():
    spec = importlib.util.spec_from_file_location("run_defect_benchmark", ROOT / "scripts/run_defect_benchmark.py")
    bench = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bench)
    assert {d.id for d in DEFECTS if not d.variant} == {m["id"] for m in bench.MUTATIONS}
