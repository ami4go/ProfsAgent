"""LLM client with multi-key, multi-model fallback for free-tier Gemini + Groq.

Walk order for a role: endpoints in config order; for each Gemini model every key in GEMINI_API_KEYS.
An (provider, model, key#) slot that fails with 429 / 503 / timeout goes on cooldown (persisted to
data/cache/llm_state.json) and the next slot is tried. JSON outputs are validated with Pydantic; on a
validation error the call is retried once with the error appended (possibly on a different slot).

Keys are referred to by index only in logs.
"""
from __future__ import annotations

import hashlib
import os
import json
import re
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TypeVar

import httpx
import numpy as np
from pydantic import BaseModel, ValidationError

from profsagent.config import CACHE, keys, models_cfg

T = TypeVar("T", bound=BaseModel)
GEMINI = "https://generativelanguage.googleapis.com/v1beta/models"
GROQ = "https://api.groq.com/openai/v1/chat/completions"


class AllEndpointsFailed(RuntimeError):
    pass


@dataclass
class CallRecord:
    prompt_id: str
    prompt_version: str
    role: str
    endpoint: str | None = None
    attempts: list[dict] = field(default_factory=list)
    prompt_tokens: int = 0
    output_tokens: int = 0
    latency_s: float = 0.0
    schema_retries: int = 0
    ok: bool = False
    error: str | None = None


def _fp(key: str) -> str:
    """Stable, non-secret slot id for an API key (cooldowns survive reordering keys in .env)."""
    return "k" + hashlib.sha256(key.encode()).hexdigest()[:8]


def _approx_tokens(text: str) -> int:
    return len(text) // 4


def _extract_json(text: str) -> Any:
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        m = re.search(r"\{.*\}|\[.*\]", text, re.S)
        if m:
            return json.loads(m.group(0))
        raise


class SlotState:
    """Cooldown bookkeeping shared across processes via a small JSON file."""

    def __init__(self, path: Path):
        self.path = path
        self.lock = threading.Lock()
        self.state: dict[str, dict] = json.loads(path.read_text()) if path.exists() else {}

    def _save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.state, indent=1))

    def available(self, slot: str) -> bool:
        return self.state.get(slot, {}).get("until", 0) <= time.time()

    def wait_interval(self, slot: str, min_interval: float) -> None:
        last = self.state.get(slot, {}).get("last", 0)
        delta = time.time() - last
        if delta < min_interval:
            time.sleep(min_interval - delta)

    def touch(self, slot: str) -> None:
        with self.lock:
            self.state.setdefault(slot, {})["last"] = time.time()
            self._save()

    def cool(self, slot: str, seconds: float, reason: str) -> None:
        with self.lock:
            s = self.state.setdefault(slot, {})
            s["until"] = time.time() + seconds
            s["reason"] = reason[:160]
            self._save()


class LLMClient:
    def __init__(self, run_log_path: Path | None = None):
        self.cfg = models_cfg()
        self.lim = self.cfg["limits"]
        self.gemini_keys = keys("GEMINI_API_KEYS")
        self.groq_keys = keys("GROQ_API_KEYS")
        self.slots = SlotState(CACHE / "llm_state.json")
        self.http = httpx.Client(timeout=self.lim["timeout_s"])
        self.run_log_path = run_log_path
        self.cache_enabled = True
        self.ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")
        self.totals = {"calls": 0, "prompt_tokens": 0, "output_tokens": 0}

    # ------------------------------------------------------------------ slots
    def _slots_for(self, role: str, prompt_chars: int):
        for ep in self.cfg["roles"][role]:
            if ep.get("max_prompt_tokens") and prompt_chars / 3.2 > ep["max_prompt_tokens"]:
                continue
            ks = {"gemini": self.gemini_keys, "groq": self.groq_keys, "ollama": ["local"]}[ep["provider"]]
            for i, k in enumerate(ks):
                yield ep, i, k, f"{ep['provider']}:{ep['model']}:{_fp(k)}"

    # ------------------------------------------------------------------ raw calls
    def _gemini(self, model: str, key: str, system: str, user: str, temperature: float, json_mode: bool,
                tools: list | None = None) -> tuple[str, dict, dict]:
        body: dict = {
            "contents": [{"role": "user", "parts": [{"text": user}]}],
            "generationConfig": {"temperature": temperature},
        }
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"
        if tools:
            body["tools"] = tools
        r = self.http.post(f"{GEMINI}/{model}:generateContent", headers={"x-goog-api-key": key}, json=body)
        if r.status_code != 200:
            raise _HTTPError(r.status_code, r.text)
        j = r.json()
        cands = j.get("candidates") or []
        if not cands or "content" not in cands[0]:
            raise _HTTPError(599, f"no content: finishReason={cands[0].get('finishReason') if cands else 'none'}")
        text = "".join(p.get("text", "") for p in cands[0]["content"].get("parts", []) if not p.get("thought"))
        um = j.get("usageMetadata", {})
        usage = {"prompt": um.get("promptTokenCount", 0), "output": um.get("candidatesTokenCount", 0) + um.get("thoughtsTokenCount", 0)}
        return text, usage, cands[0].get("groundingMetadata", {})

    def _groq(self, model: str, key: str, system: str, user: str, temperature: float, json_mode: bool) -> tuple[str, dict, dict]:
        body: dict = {
            "model": model,
            "messages": ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}],
            "temperature": temperature,
            "reasoning_effort": "low",
        }
        if json_mode:
            body["response_format"] = {"type": "json_object"}
        r = self.http.post(GROQ, headers={"Authorization": f"Bearer {key}"}, json=body)
        if r.status_code != 200:
            raise _HTTPError(r.status_code, r.text)
        j = r.json()
        u = j.get("usage", {})
        return j["choices"][0]["message"]["content"] or "", {"prompt": u.get("prompt_tokens", 0), "output": u.get("completion_tokens", 0)}, {}

    @staticmethod
    def _until_pacific_midnight() -> float:
        from datetime import datetime, timedelta
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("America/Los_Angeles"))
        nxt = (now + timedelta(days=1)).replace(hour=0, minute=5, second=0, microsecond=0)
        return (nxt - now).total_seconds()

    def _ollama(self, model: str, system: str, user: str, temperature: float, json_mode: bool) -> tuple[str, dict, dict]:
        """Local fallback (CPU): Ollama chat API. No quota; slow (~10 tok/s generation on this machine)."""
        approx = (len(system) + len(user)) // 3
        num_ctx = int(min(32768, max(8192, approx * 1.3 + 6000)))
        body = {"model": model, "stream": False, "think": False,
                "messages": ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": user}],
                "options": {"temperature": temperature, "num_ctx": num_ctx}}
        if json_mode:
            body["format"] = "json"
        r = httpx.post(f"{self.ollama_url}/api/chat", json=body, timeout=self.lim.get("ollama_timeout_s", 2400))
        if r.status_code != 200:
            raise _HTTPError(r.status_code, r.text)
        j = r.json()
        return j.get("message", {}).get("content", ""), {"prompt": j.get("prompt_eval_count", 0), "output": j.get("eval_count", 0)}, {}

    def _cooldown_for(self, err: "_HTTPError") -> tuple[float, str]:
        t = err.text
        if err.status == 429:
            if re.search(r"PerDay", t):
                return self._until_pacific_midnight(), "429 daily quota"
            m = re.search(r'"retryDelay":\s*"(\d+(?:\.\d+)?)s"', t)
            return (float(m.group(1)) + 2 if m else self.lim["cooldown_429_default_s"]), "429 rate"
        if err.status in (500, 502, 503, 504, 599):
            return self.lim["cooldown_503_s"], f"{err.status} unavailable"
        if err.status == 404 or (err.status == 400 and re.search(r"not (found|supported)", t, re.I)):
            return self._until_pacific_midnight(), f"{err.status} model unsupported"
        return 0, ""

    def raw(self, role: str, system: str, user: str, temperature: float = 0.2, json_mode: bool = True,
            tools: list | None = None, record: CallRecord | None = None) -> tuple[str, dict, dict]:
        """Try every eligible slot; if all are cooling down, wait for the soonest one (bounded by max_wait_s)."""
        waited = 0.0
        max_wait = self.lim.get("max_wait_s", 600)
        while True:
            try:
                return self._raw_once(role, system, user, temperature, json_mode, tools, record)
            except AllEndpointsFailed as e:
                slots = [s for ep, _, _, s in self._slots_for(role, len(system) + len(user)) if not (tools and ep["provider"] != "gemini")]
                soonest = min((self.slots.state.get(s, {}).get("until", 0) for s in slots), default=0) - time.time()
                if not slots or soonest > max_wait - waited:
                    raise
                pause = max(soonest, 3) + 1
                if record is not None:
                    record.attempts.append({"slot": "*", "ok": False, "why": f"all slots cooling; waiting {pause:.0f}s"})
                time.sleep(pause)
                waited += pause
                last_err = e  # noqa: F841

    def _raw_once(self, role: str, system: str, user: str, temperature: float, json_mode: bool,
                  tools: list | None, record: CallRecord | None) -> tuple[str, dict, dict]:
        last = None
        for ep, ki, key, slot in self._slots_for(role, len(system) + len(user)):
            if not self.slots.available(slot):
                continue
            if tools and ep["provider"] != "gemini":
                continue
            self.slots.wait_interval(slot, self.lim["min_interval_s"])
            self.slots.touch(slot)
            t0 = time.time()
            try:
                if ep["provider"] == "gemini":
                    out = self._gemini(ep["model"], key, system, user, temperature, json_mode, tools)
                elif ep["provider"] == "ollama":
                    out = self._ollama(ep["model"], system, user, temperature, json_mode)
                else:
                    out = self._groq(ep["model"], key, system, user, temperature, json_mode)
                if record is not None:
                    record.endpoint = slot
                    record.attempts.append({"slot": slot, "ok": True, "s": round(time.time() - t0, 1)})
                return out
            except _HTTPError as e:
                if e.status == 413 or (e.status == 400 and re.search(r"json_validate_failed|max completion tokens|context length|too large", e.text, re.I)):
                    if record is not None:  # request-specific failure: try the next endpoint, no cooldown
                        record.attempts.append({"slot": slot, "ok": False, "status": e.status, "why": "request-specific: " + e.text[:80]})
                    last = e
                    continue
                secs, why = self._cooldown_for(e)
                if record is not None:
                    record.attempts.append({"slot": slot, "ok": False, "status": e.status, "why": why or e.text[:120]})
                if secs:
                    if e.status in (500, 502, 503, 504, 599) and ep["provider"] == "gemini":
                        for kx in self.gemini_keys:   # overload is model-wide: cool every key
                            self.slots.cool(f"gemini:{ep['model']}:{_fp(kx)}", secs, why)
                    else:
                        self.slots.cool(slot, secs, why)
                    last = e
                    continue
                raise
            except (httpx.TimeoutException, httpx.TransportError) as e:
                self.slots.cool(slot, 300 if ep["provider"] == "ollama" else self.lim["cooldown_timeout_s"], type(e).__name__)
                if record is not None:
                    record.attempts.append({"slot": slot, "ok": False, "why": type(e).__name__})
                last = e
                continue
        raise AllEndpointsFailed(f"all endpoints for role '{role}' unavailable; last: {str(last)[:200]}")

    # ------------------------------------------------------------------ structured calls
    def structured(self, *, system: str, user: str, model_cls: type[T], role: str = "generate", temperature: float = 0.2,
                   prompt_id: str = "?", prompt_version: str = "?", run_id: str | None = None) -> tuple[T, CallRecord]:
        rec = CallRecord(prompt_id=prompt_id, prompt_version=prompt_version, role=role)
        t0 = time.time()
        cache_path = None
        if self.cfg.get("cache", {}).get("enabled") and self.cache_enabled:
            key = hashlib.sha256(f"{role}|{temperature}|{model_cls.__name__}|{system}|{user}".encode()).hexdigest()[:32]
            cache_path = CACHE / "llm" / f"{key}.json"
            if cache_path.exists():
                cached = json.loads(cache_path.read_text(encoding="utf-8"))
                try:
                    obj = model_cls.model_validate(cached["obj"])
                    rec.ok, rec.endpoint = True, f"cache({cached.get('endpoint')})"
                    self._log(rec, system, user, "<cached>", run_id)
                    return obj, rec
                except ValidationError:
                    pass
        msg_user = user
        raw_text = ""
        for attempt in range(self.lim["schema_retries"] + 1):
            text, usage, _ = self.raw(role, system, msg_user, temperature, json_mode=True, record=rec)
            raw_text = text
            rec.prompt_tokens += usage["prompt"]
            rec.output_tokens += usage["output"]
            try:
                obj = model_cls.model_validate(_extract_json(text))
                rec.ok = True
                break
            except (ValidationError, json.JSONDecodeError, ValueError) as e:
                rec.schema_retries += 1
                err = str(e)[:3000]
                if attempt >= self.lim["schema_retries"]:
                    rec.error = f"schema: {err[:500]}"
                    self._log(rec, system, user, raw_text, run_id)
                    raise
                msg_user = (user + "\n\n## YOUR PREVIOUS OUTPUT FAILED VALIDATION\nFix exactly these errors and return the "
                            "complete corrected JSON object (no commentary):\n" + err)
        rec.latency_s = round(time.time() - t0, 1)
        self._log(rec, system, user, raw_text, run_id)
        if cache_path is not None:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            cache_path.write_text(json.dumps({"endpoint": rec.endpoint, "obj": obj.model_dump()}, ensure_ascii=False), encoding="utf-8")
        return obj, rec

    def grounded_search(self, query: str, instruction: str) -> dict:
        rec = CallRecord(prompt_id="SEARCH", prompt_version="-", role="search")
        text, usage, gm = self.raw("search", "", f"{instruction}\n\nQuery: {query}", 0.0, json_mode=False,
                                   tools=[{"google_search": {}}], record=rec)
        rec.ok, rec.prompt_tokens, rec.output_tokens = True, usage["prompt"], usage["output"]
        self._log(rec, "", query, text, None)
        return {
            "text": text,
            "queries": gm.get("webSearchQueries", []),
            "sources": [{"title": c.get("web", {}).get("title"), "uri": c.get("web", {}).get("uri")} for c in gm.get("groundingChunks", [])],
        }

    # ------------------------------------------------------------------ embeddings
    def embed(self, texts: list[str], task_type: str = "RETRIEVAL_DOCUMENT") -> np.ndarray:
        emb_cfg = self.cfg["embedding"]
        cache_dir = CACHE / "emb"
        cache_dir.mkdir(parents=True, exist_ok=True)
        out: list[np.ndarray | None] = []
        todo: list[int] = []
        paths = []
        for i, t in enumerate(texts):
            h = hashlib.sha256(f"{emb_cfg['model']}|{emb_cfg['dim']}|{task_type}|{t}".encode()).hexdigest()[:24]
            p = cache_dir / f"{h}.npy"
            paths.append(p)
            if p.exists():
                out.append(np.load(p))
            else:
                out.append(None)
                todo.append(i)
        batch_size = 40
        for b in range(0, len(todo), batch_size):
            batch = todo[b:b + batch_size]
            body = {"requests": [{"model": f"models/{emb_cfg['model']}", "content": {"parts": [{"text": texts[i][:8000]}]},
                                  "outputDimensionality": emb_cfg["dim"], "taskType": task_type} for i in batch]}
            done, last, waited = False, None, 0
            while not done:
                progressed = False
                for ki, key in enumerate(self.gemini_keys):
                    slot = f"gemini:{emb_cfg['model']}:{_fp(key)}"
                    if not self.slots.available(slot):
                        continue
                    progressed = True
                    try:
                        r = self.http.post(f"{GEMINI}/{emb_cfg['model']}:batchEmbedContents", headers={"x-goog-api-key": key}, json=body)
                        if r.status_code != 200:
                            raise _HTTPError(r.status_code, r.text)
                        vecs = [np.asarray(e["values"], dtype=np.float32) for e in r.json()["embeddings"]]
                        for i, v in zip(batch, vecs):
                            v = v / (np.linalg.norm(v) + 1e-9)
                            np.save(paths[i], v)
                            out[i] = v
                        done = True
                        break
                    except _HTTPError as e:
                        secs, why = self._cooldown_for(e)
                        self.slots.cool(slot, secs or 60, why or str(e.status))
                        last = e
                    except (httpx.TimeoutException, httpx.TransportError) as e:
                        self.slots.cool(slot, 30, type(e).__name__)
                        last = e
                if done:
                    break
                # every key cooling down: wait for the soonest one unless all are on a daily cooldown
                soonest = min(self.slots.state.get(f"gemini:{emb_cfg['model']}:{_fp(kx)}", {}).get("until", 0)
                              for kx in self.gemini_keys) - time.time()
                if soonest > 900 or waited > 600:
                    raise AllEndpointsFailed(f"embedding quota exhausted: {str(last)[:200]}")
                time.sleep(max(soonest, 5))
                waited += max(soonest, 5)
        return np.vstack(out) if out else np.zeros((0, emb_cfg["dim"]), dtype=np.float32)

    # ------------------------------------------------------------------ logging
    def _log(self, rec: CallRecord, system: str, user: str, output: str, run_id: str | None) -> None:
        self.totals["calls"] += 1
        self.totals["prompt_tokens"] += rec.prompt_tokens
        self.totals["output_tokens"] += rec.output_tokens
        if not self.run_log_path:
            return
        self.run_log_path.parent.mkdir(parents=True, exist_ok=True)
        entry = {**rec.__dict__, "ts": time.time(), "run_id": run_id,
                 "prompt_sha": hashlib.sha256((system + user).encode()).hexdigest()[:16],
                 "user_prompt": user, "output": output}
        with self.run_log_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")


class _HTTPError(Exception):
    def __init__(self, status: int, text: str):
        super().__init__(f"HTTP {status}: {text[:300]}")
        self.status = status
        self.text = text
