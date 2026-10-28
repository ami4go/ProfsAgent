"""Structure guard (validation layer v2, Stage 1): invalid LLM output falls back to the next model instead of crashing
the run, and Gemini's constrained JSON-Schema output degrades to plain JSON when a model rejects the schema.
No network: endpoints are faked; cooldowns go to a temp file, the response cache is off."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pytest
from pydantic import BaseModel

from profsagent.llm.client import LLMClient, SlotState, _HTTPError


class Out(BaseModel):
    title: str
    weeks: int


GOOD = json.dumps({"title": "AI-native software development", "weeks": 13})
BROKEN = '{"title": "AI-native software development", weeks: 13'   # the kind of reply that crashed 2 benchmark runs


@pytest.fixture
def client(tmp_path, monkeypatch):
    c = LLMClient()
    c.slots = SlotState(tmp_path / "llm_state.json")
    c.cache_enabled = False
    c.gemini_keys, c.groq_keys = ["test-key"], []
    c.lim = {**c.lim, "min_interval_s": 0, "max_wait_s": 0, "schema_retries": 1, "schema_fallback_models": 2,
             "native_json_schema": False}
    c.cfg = {**c.cfg, "roles": {"generate": [{"provider": "gemini", "model": "model-a"}, {"provider": "gemini", "model": "model-b"},
                                             {"provider": "gemini", "model": "model-c"}]}}
    return c


def fake_gemini(replies: dict, calls: list):
    def _gemini(model, key, system, user, temperature, json_mode, tools=None, response_schema=None):
        calls.append((model, response_schema is not None))
        r = replies[model]
        if isinstance(r, Exception):
            raise r
        return (r.pop(0) if isinstance(r, list) else r), {"prompt": 10, "output": 5}, {}
    return _gemini


def test_valid_output_needs_no_fallback(client, monkeypatch):
    calls = []
    monkeypatch.setattr(client, "_gemini", fake_gemini({"model-a": GOOD}, calls))
    obj, rec = client.structured(system="s", user="u", model_cls=Out)
    assert obj.weeks == 13 and [m for m, _ in calls] == ["model-a"]


def test_invalid_output_falls_back_to_the_next_model(client, monkeypatch):
    calls = []
    monkeypatch.setattr(client, "_gemini", fake_gemini({"model-a": BROKEN, "model-b": GOOD}, calls))
    obj, rec = client.structured(system="s", user="u", model_cls=Out)
    assert obj.title.startswith("AI-native")
    assert [m for m, _ in calls] == ["model-a", "model-a", "model-b"]   # first try + 1 schema retry, then the next model
    assert rec.ok and rec.endpoint.startswith("gemini:model-b:")
    assert any("next model" in a.get("why", "") for a in rec.attempts)


def test_retry_on_the_same_model_still_comes_first(client, monkeypatch):
    calls = []
    monkeypatch.setattr(client, "_gemini", fake_gemini({"model-a": [BROKEN, GOOD]}, calls))
    obj, _ = client.structured(system="s", user="u", model_cls=Out)
    assert obj.weeks == 13 and [m for m, _ in calls] == ["model-a", "model-a"]


def test_every_model_invalid_raises_the_validation_error(client, monkeypatch):
    calls = []
    monkeypatch.setattr(client, "_gemini", fake_gemini({"model-a": BROKEN, "model-b": BROKEN, "model-c": BROKEN}, calls))
    with pytest.raises(json.JSONDecodeError):
        client.structured(system="s", user="u", model_cls=Out)
    assert [m for m, _ in calls] == ["model-a", "model-a", "model-b", "model-b", "model-c", "model-c"]


def test_fallback_stops_when_no_model_is_left(client, monkeypatch):
    client.cfg["roles"]["generate"] = [{"provider": "gemini", "model": "model-a"}]
    calls = []
    monkeypatch.setattr(client, "_gemini", fake_gemini({"model-a": BROKEN}, calls))
    with pytest.raises(json.JSONDecodeError):
        client.structured(system="s", user="u", model_cls=Out)
    assert [m for m, _ in calls] == ["model-a", "model-a"]


def test_native_schema_is_sent_when_enabled(client, monkeypatch):
    client.lim["native_json_schema"] = True
    calls = []
    monkeypatch.setattr(client, "_gemini", fake_gemini({"model-a": GOOD}, calls))
    client.structured(system="s", user="u", model_cls=Out)
    assert calls == [("model-a", True)]


def test_rejected_schema_degrades_to_plain_json(client, monkeypatch):
    client.lim["native_json_schema"] = True
    calls = []

    def _gemini(model, key, system, user, temperature, json_mode, tools=None, response_schema=None):
        calls.append((model, response_schema is not None))
        if response_schema is not None:
            raise _HTTPError(400, '{"error": {"message": "Invalid JSON payload: unknown field in responseJsonSchema"}}')
        return GOOD, {"prompt": 1, "output": 1}, {}
    monkeypatch.setattr(client, "_gemini", _gemini)
    obj, rec = client.structured(system="s", user="u", model_cls=Out)
    assert obj.weeks == 13 and calls == [("model-a", True), ("model-a", False)]
    assert "model-a" in client.no_native_schema
    client.structured(system="s", user="u2", model_cls=Out)              # later calls skip the schema for that model
    assert calls[-1] == ("model-a", False)


def test_strong_only_waits_for_strong_models_instead_of_lite(client, monkeypatch):
    client.cfg = {**client.cfg, "roles": {"generate": [{"provider": "gemini", "model": "model-a"},
                                                       {"provider": "gemini", "model": "model-a-lite"},
                                                       {"provider": "ollama", "model": "local"}]}}
    calls = []
    monkeypatch.setattr(client, "_gemini", fake_gemini({"model-a": _HTTPError(503, "high demand"), "model-a-lite": GOOD}, calls))
    obj, rec = client.structured(system="s", user="u", model_cls=Out)       # default: falls back to the lite model
    assert rec.endpoint.startswith("gemini:model-a-lite")
    client.strong_only = True
    client.slots = SlotState(client.slots.path.parent / "fresh_state.json")
    calls.clear()
    assert [s.split(":")[1] for _, _, _, s in client._slots_for("generate", 10)] == ["model-a"]
    with pytest.raises(Exception):                                          # max_wait_s 0: no weak fallback, the call fails
        client.structured(system="s2", user="u2", model_cls=Out)
    assert [m for m, _ in calls] == ["model-a"]


def test_excluded_models_are_never_called(client, monkeypatch):
    calls = []
    monkeypatch.setattr(client, "_gemini", fake_gemini({"model-a": GOOD, "model-b": GOOD}, calls))
    obj, rec = client.structured(system="s", user="u", model_cls=Out, exclude_models=frozenset({"gemini:model-a"}))
    assert [m for m, _ in calls] == ["model-b"] and rec.endpoint.startswith("gemini:model-b:")
    calls.clear()
    monkeypatch.setattr(client, "_gemini", fake_gemini({"model-b": BROKEN, "model-c": GOOD}, calls))
    client.structured(system="s", user="u", model_cls=Out, exclude_models=frozenset({"gemini:model-a"}))
    assert "model-a" not in [m for m, _ in calls] and calls[-1][0] == "model-c"   # fallback still skips the excluded one
