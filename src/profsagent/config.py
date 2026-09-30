"""Paths, settings and secrets. Secrets come only from .env / environment and are never logged."""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "config"
DATA = ROOT / "data"
PROMPTS = ROOT / "prompts"
RUNS = ROOT / "runs"
CACHE = DATA / "cache"


def _load_env() -> None:
    p = ROOT / ".env"
    if not p.exists():
        return
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())


_load_env()


def keys(name: str) -> list[str]:
    return [k.strip() for k in os.environ.get(name, "").split(",") if k.strip()]


@lru_cache(maxsize=None)
def load_yaml(rel: str) -> dict:
    return yaml.safe_load((ROOT / rel).read_text(encoding="utf-8"))


def models_cfg() -> dict:
    return load_yaml("config/models.yaml")


def pedagogy() -> dict:
    return load_yaml("config/pedagogy.yaml")


def regulations() -> dict:
    return load_yaml("config/regulations.yaml")


def institutions() -> dict:
    return load_yaml("config/institutions.yaml")


def bloom_lexicon() -> dict:
    return load_yaml("data/bloom_lexicon.yaml")


def degree_bank() -> dict:
    return load_yaml("data/degree_bank.yaml")


def programme(uid: str) -> dict:
    name = uid.lower().replace("btech-", "btech_")
    return load_yaml(f"data/programmes/{name}.yaml")
