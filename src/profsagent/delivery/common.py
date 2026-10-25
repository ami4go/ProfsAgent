"""Shared helpers for the delivery aids: config, run paths, quotas, local embeddings, text utilities."""
from __future__ import annotations

import datetime as dt
import json
import re
import time
from functools import lru_cache
from pathlib import Path

import numpy as np

from profsagent.config import CACHE, RUNS, load_yaml


@lru_cache(maxsize=None)
def rcfg() -> dict:
    return load_yaml("config/resources.yaml")


@lru_cache(maxsize=None)
def xcfg() -> dict:
    return load_yaml("config/experts.yaml")


def run_dir(run_id: str) -> Path:
    return RUNS / run_id


def out_dir(run_id: str) -> Path:
    d = RUNS / run_id / "delivery"
    d.mkdir(parents=True, exist_ok=True)
    return d


def load_state(run_id: str) -> dict:
    return json.loads((RUNS / run_id / "state.json").read_text(encoding="utf-8"))


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=1, ensure_ascii=False, default=str), encoding="utf-8")


def read_json(path: Path, default=None):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else default


# ------------------------------------------------------------------ quotas
class Quota:
    """Daily unit counter (e.g. YouTube Data API units), reset at midnight Pacific like Google's quotas."""

    def __init__(self, name: str, daily_limit: int):
        self.path = CACHE / f"quota_{name}.json"
        self.limit = daily_limit

    @staticmethod
    def _day() -> str:
        return (dt.datetime.now(dt.timezone.utc) - dt.timedelta(hours=8)).strftime("%Y-%m-%d")

    def used(self) -> int:
        d = read_json(self.path, {})
        return d.get("used", 0) if d.get("day") == self._day() else 0

    def can(self, units: int) -> bool:
        return self.used() + units <= self.limit

    def spend(self, units: int) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        write_json(self.path, {"day": self._day(), "used": self.used() + units})


# ------------------------------------------------------------------ local embeddings (no API quota)
@lru_cache(maxsize=1)
def embedder():
    from profsagent.kg.neo4j_kg import LocalEmbedder   # all-MiniLM-L6-v2, cached on disk
    return LocalEmbedder()


def embed(texts: list[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 384), dtype=np.float32)
    return embedder().embed([t[:1000] for t in texts])


# ------------------------------------------------------------------ text utilities
def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "")).strip()


def iso_duration_s(d: str | None) -> int | None:
    """ISO-8601 duration (PT1H2M3S) → seconds."""
    if not d:
        return None
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", d)
    if not m:
        return None
    days, h, mi, s = (int(x or 0) for x in m.groups())
    return days * 86400 + h * 3600 + mi * 60 + s


def hms(sec: float | None) -> str:
    if sec is None:
        return "?"
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60}:{sec % 60:02d}"


def years_since(iso: str | None) -> float | None:
    if not iso:
        return None
    try:
        t = dt.datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return max((dt.datetime.now(dt.timezone.utc) - t).days / 365.25, 0.0)
    except ValueError:
        return None


def now() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")
