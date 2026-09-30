"""Prompt loader: YAML front-matter + '## SYSTEM' / '## USER' sections, rendered with Jinja2.

`{% include "00_common_rules.md" %}` resolves relative to prompts/ with the included file's front-matter stripped.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache

import jinja2
import yaml

from profsagent.config import PROMPTS

FM_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


def _strip_fm(text: str) -> tuple[dict, str]:
    m = FM_RE.match(text)
    if not m:
        return {}, text
    try:
        meta = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:  # front-matter is documentation-style; only id/version/temperature are machine-read
        meta = {k: v.strip().strip('"') for k, v in re.findall(r"^(id|version|temperature|model_class):\s*(.+)$", m.group(1), re.M)}
    return meta, text[m.end():]


def _loader(name: str) -> str:
    p = PROMPTS / name
    if not p.exists():
        hits = list(PROMPTS.rglob(name))
        if not hits:
            raise jinja2.TemplateNotFound(name)
        p = hits[0]
    return _strip_fm(p.read_text(encoding="utf-8"))[1]


def _tojson(v) -> str:
    return json.dumps(v, ensure_ascii=False, default=str)


ENV = jinja2.Environment(loader=jinja2.FunctionLoader(_loader), undefined=jinja2.StrictUndefined,
                         keep_trailing_newline=True, autoescape=False)
ENV.filters["tojson"] = _tojson


@dataclass
class Prompt:
    id: str
    version: str
    meta: dict
    system_tpl: str
    user_tpl: str

    def render(self, **ctx) -> tuple[str, str]:
        system = ENV.from_string(self.system_tpl).render(**ctx).strip()
        user = ENV.from_string(self.user_tpl).render(**ctx).strip()
        return system, user


@lru_cache(maxsize=None)
def load_prompt(pid: str) -> Prompt:
    hits = [p for p in PROMPTS.rglob("*.md") if p.name.startswith(f"{pid}_")]
    if len(hits) != 1:
        raise FileNotFoundError(f"prompt {pid}: {hits}")
    meta, body = _strip_fm(hits[0].read_text(encoding="utf-8"))
    parts = re.split(r"^## USER\s*$", body, maxsplit=1, flags=re.M)
    if len(parts) != 2:
        raise ValueError(f"prompt {pid} lacks '## USER' section")
    system = re.sub(r"^## SYSTEM\s*$", "", parts[0], count=1, flags=re.M)
    return Prompt(id=str(meta.get("id", pid)), version=str(meta.get("version", "0")), meta=meta,
                  system_tpl=system, user_tpl=parts[1])
