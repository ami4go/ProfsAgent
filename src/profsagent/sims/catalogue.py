"""The simulation catalogue (simulations/, docs/09_phase2_A_simulation_catalogue.md §7).

Each simulation is a folder simulations/<id>/ with a sim.yaml, its page (page.html, or page.src.html for pages that use
a shared library from simulations/_lib), a qa.py, and optionally the source of a video. This module loads and checks
the entries, builds each page into one offline file (simulations/_build/<id>.html), and runs the QA scripts.

    entries() -> [entry]                 every sim.yaml, with "_dir"
    problems(entry) -> [str]             what is wrong with one entry (empty = fine)
    build(entry) -> Path                 the single-file page
    run_qa(entry, page) -> dict          {"ok", "seconds", "summary"}
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from functools import lru_cache
from pathlib import Path

import yaml

from profsagent.config import DATA, ROOT

SIMS = Path(os.environ.get("PROFSAGENT_SIMS_DIR") or ROOT / "simulations")    # (a copy, for the app's QA servers)
BUILD = SIMS / "_build"
LIB = SIMS / "_lib"
REQUIRED = ("id", "type", "title", "summary", "version", "status", "courses", "topics", "interactivity", "engine", "files", "checks",
            "changelog")
STATUSES = {"draft", "team-checked", "retired"}
# shared files a page_src may load: libraries (simulations/_lib) and engines (simulations/_engines/<type>/)
ASSET_JS = re.compile(r'<script src="\.\./(_lib|_engines)/([A-Za-z0-9._/-]+\.js)"></script>')
ASSET_CSS = re.compile(r'<link rel="stylesheet" href="\.\./(_lib|_engines)/([A-Za-z0-9._/-]+\.css)">')


@lru_cache(maxsize=1)
def types() -> dict:
    return yaml.safe_load((SIMS / "types.yaml").read_text(encoding="utf-8"))


def type_ids() -> list[str]:
    return [t["id"] for t in types()["types"]]


@lru_cache(maxsize=1)
def known_courses() -> set[str]:
    """Course codes in the IIIT-D catalogue (TechTree); cross-listed entries count for each of their codes."""
    try:
        idx = json.loads((DATA / "techtree_index.json").read_text(encoding="utf-8"))
    except OSError:
        return set()
    out = set()
    for v in idx.values():
        for c in re.split(r"[/,]", v.get("code") or ""):
            c = re.sub(r"\s+", "", c).upper()
            if c:
                out.add(c)
    return out


def entries(include_retired: bool = True) -> list[dict]:
    out = []
    for f in sorted(SIMS.glob("*/sim.yaml")):
        if f.parent.name.startswith("_"):
            continue
        e = yaml.safe_load(f.read_text(encoding="utf-8")) or {}
        e["_dir"] = f.parent
        if include_retired or e.get("status") != "retired":
            out.append(e)
    return out


def get(sim_id: str) -> dict:
    for e in entries():
        if e.get("id") == sim_id:
            return e
    raise KeyError(sim_id)


def problems(e: dict) -> list[str]:
    p = [f"missing {k}" for k in REQUIRED if k not in e]
    if p:
        return p
    d: Path = e["_dir"]
    if e["id"] != d.name:
        p.append(f"id {e['id']!r} differs from its folder {d.name!r}")
    ts = e["type"] if isinstance(e["type"], list) else [e["type"]]
    p += [f"unknown type {t!r}" for t in ts if t not in type_ids()]
    if e["status"] not in STATUSES:
        p.append(f"status must be one of {sorted(STATUSES)}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(e["version"])):
        p.append("version must look like 1.2.0")
    if e["interactivity"] not in types()["levels"]:
        p.append(f"interactivity must be one of {list(types()['levels'])}")
    known = known_courses()
    if known:
        p += [f"course {c} is not in the IIIT-D catalogue" for c in e["courses"] if str(c).upper() not in known]
    files = e["files"]
    page = files.get("page") or files.get("page_src")
    if not page:
        p.append("files needs page (self-contained) or page_src (uses simulations/_lib)")
    for k, v in files.items():
        if not (d / v).exists():
            p.append(f"files.{k}: {v} does not exist")
    if files.get("page_src") and (d / files["page_src"]).exists():
        html = (d / files["page_src"]).read_text(encoding="utf-8")
        assets = ASSET_JS.findall(html) + ASSET_CSS.findall(html)
        p += [f"{root}/{x} does not exist" for root, x in assets if not (SIMS / root / x).exists()]
        if re.search(r'<(script|link)[^>]+(src|href)="(https?:)?//', html):
            p.append("page_src loads something from the internet; pages must work offline")
    if not isinstance(e["summary"], str) or not 20 <= len(e["summary"]) <= 240:
        p.append("summary must be one plain line of 20-240 characters (what students do)")
    if not isinstance(e.get("class_example", False), bool):
        p.append("class_example must be true or false")
    if e.get("class_example") and files.get("page_src") and (d / files["page_src"]).exists() and             "_engines/share/share.js" not in (d / files["page_src"]).read_text(encoding="utf-8"):
        p.append("class_example: true needs the page to load ../_engines/share/share.js")
    log = e["changelog"]
    if not log or str(log[0].get("version")) != str(e["version"]):
        p.append("the first changelog entry must be the current version")
    return p


def build(e: dict) -> Path:
    """One offline HTML file: a self-contained page as it is, or page_src with its library (and its licence notices) inlined."""
    BUILD.mkdir(parents=True, exist_ok=True)
    d, files = e["_dir"], e["files"]
    out = BUILD / f"{e['id']}.html"
    if files.get("page"):
        out.write_bytes((d / files["page"]).read_bytes())
        return out
    out.write_text(inline((d / files["page_src"]).read_text(encoding="utf-8")), encoding="utf-8")
    return out


def inline(src: str) -> str:
    """A page source with its ../_lib and ../_engines files (and the libraries' licence notices) put inside it."""
    notice = (LIB / "LICENSES.txt").read_text(encoding="utf-8").replace("*/", "* /") if (LIB / "LICENSES.txt").exists() else ""

    def inline_js(m):
        code = (SIMS / m.group(1) / m.group(2)).read_text(encoding="utf-8").replace("</script", "<\\/script")
        head = "/*!\n" + notice + "\n*/\n" if m.group(1) == "_lib" else ""
        return "<script>\n" + head + code + "\n</script>"

    def inline_css(m):
        return "<style>\n" + (SIMS / m.group(1) / m.group(2)).read_text(encoding="utf-8") + "\n</style>"
    return ASSET_JS.sub(inline_js, ASSET_CSS.sub(inline_css, src))


def run_qa(e: dict, page: Path | None = None, timeout: int = 900) -> dict:
    page = page or build(e)
    shots = BUILD / "qa" / e["id"]
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, str(e["_dir"] / e["files"]["qa"]), str(page), str(shots)], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        lines = [x for x in (r.stdout or "").splitlines() if x.strip()]
        summary = next((x for x in reversed(lines) if x.startswith("PROBLEMS:")), (lines[-1] if lines else (r.stderr or "")[-300:]))
        return {"ok": r.returncode == 0, "seconds": round(time.time() - t0, 1), "summary": summary,
                "problems": [x for x in lines if x.startswith("PROBLEM:")][:20]}
    except subprocess.TimeoutExpired:
        return {"ok": False, "seconds": round(time.time() - t0, 1), "summary": f"timed out after {timeout} s", "problems": []}
