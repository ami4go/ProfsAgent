"""Checks of a deck that need tools beyond the deck itself (no AI calls): code syntax and citation match.

    D-CODE        error    a code figure that does not parse (Python: ast; JSON: json; C/C++: gcc/g++ -fsyntax-only; Java: javac;
                           JavaScript: node --check), or Java calling a method a JDK type does not have
    D-UNVERIFIED  warning  a code figure no checker on this machine can parse (e.g. Java without a JDK): not verified
    D-GROUND      warning  a cited source matches the slide worse than the average offered source and below the floor
                           (local embeddings of the slide text and the source's title: a topical match only; whether the
                           source supports each claim still needs a reader)

Snippets on slides are often fragments (a method without its class, statements without main), so each is compiled once
inside the one wrapper its shape calls for (wrap_java, wrap_c), and for compiled languages only syntax messages count:
an identifier the fragment never declares is not an error (except a missing method on a JDK type, see java_problem).
"""
from __future__ import annotations

import ast
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import numpy as np

from profsagent.content.models import FIRST_CONTENT_SLIDE, LectureDeck
from profsagent.validate.record import ERR, WARN, v

LANG = {"python": "python", "py": "python", "python3": "python", "java": "java", "c": "c", "cpp": "cpp", "c++": "cpp",
        "javascript": "js", "js": "js", "node": "js", "json": "json"}
C_SYNTAX = re.compile(r"expected|stray|unterminated|missing terminating|unbalanced", re.I)
JAVA_SYNTAX = re.compile(r"expected|illegal start|not a statement|unclosed|reached end of file|orphaned", re.I)
# JDK types whose methods javac knows even in a fragment: "cannot find symbol ... method x ... of type String" is real
JDK_TYPES = {"String", "StringBuilder", "Integer", "Long", "Double", "Boolean", "Character", "Object", "Math", "System",
             "List", "ArrayList", "Map", "HashMap", "Set", "HashSet", "Optional", "Stream", "Arrays", "Collections"}


# ------------------------------------------------------------------ code
def _run(cmd: list[str], src: str, suffix: str) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as d:
        f = Path(d) / f"Snippet{suffix}"
        f.write_text(src, encoding="utf-8")
        r = subprocess.run(cmd + [str(f)], capture_output=True, text=True, timeout=60, cwd=d)
        return r.returncode == 0, (r.stderr or r.stdout).replace(str(f), "snippet")


def _json(code: str) -> str | None:
    """Slides often show a request and its response one after the other, labelled with // lines: each value must parse."""
    text = "\n".join("" if ln.strip().startswith("//") else ln for ln in code.splitlines())
    dec, i = json.JSONDecoder(), 0
    try:
        while True:
            while i < len(text) and text[i].isspace():
                i += 1
            if i == len(text):
                return None
            _, i = dec.raw_decode(text, i)
    except json.JSONDecodeError as e:
        return f"line {e.lineno}: {e.msg}"


def _python(code: str) -> str | None:
    try:
        ast.parse(code)
        return None
    except SyntaxError as e:
        return f"line {e.lineno}: {e.msg}"


FUNC_DEF = re.compile(r"^[\w<>\[\],:*&\s]+\s+[*&]?\w+\s*\([^;{)]*\)\s*(const\s*)?(throws [\w.,\s]+)?\{", re.M)
JAVA_TYPE_DECL = re.compile(r"^\s*(import |package |(public |abstract |final )*(class|interface|enum|record) |@\w+)", re.M)


def wrap_c(code: str, lang: str) -> str:
    """The snippet as a compilable unit: common headers, and statements without a function placed inside main()."""
    head = "#include <bits/stdc++.h>\nusing namespace std;\n" if lang == "cpp" else "#include <stdio.h>\n#include <stdlib.h>\n#include <string.h>\n"
    return head + (code if FUNC_DEF.search(code) or "#include" in code else "int main(void) {\n" + code + "\nreturn 0;\n}\n")


def wrap_java(code: str) -> str:
    """As written when it declares a type; members (a method) inside a class; plain statements inside a method."""
    if JAVA_TYPE_DECL.search(code):
        return code
    if FUNC_DEF.search(code):
        return "class Snippet {\n" + code + "\n}\n"
    return "class Snippet {\nvoid snippet() throws Exception {\n" + code + "\n}\n}\n"


def _c_family(code: str, lang: str) -> str | None:
    cc = shutil.which("g++" if lang == "cpp" else "gcc")
    ok, err = _run([cc, "-fsyntax-only"], wrap_c(code, lang), ".cpp" if lang == "cpp" else ".c")
    if ok:
        return None
    # only syntax counts: a fragment may use names it never declares
    return next((ln.split("error:", 1)[1].strip() for ln in err.splitlines() if "error:" in ln and C_SYNTAX.search(ln)), None)


def java_problem(out: str) -> str | None:
    """The first real problem in javac's output: a syntax error, or a missing method on a JDK type."""
    lines = out.splitlines()
    for i, ln in enumerate(lines):
        if "error:" not in ln:
            continue
        if JAVA_SYNTAX.search(ln):
            return ln.split("error:", 1)[1].strip()
        if "cannot find symbol" in ln:
            near = " ".join(lines[i:i + 5])
            m = re.search(r"symbol:\s+method (\w+).*?location:.*?of type (\w+)", near)
            if m and m.group(2) in JDK_TYPES:
                return f"{m.group(2)} has no method {m.group(1)}()"
    return None


def _java(code: str) -> str | None:
    ok, out = _run([shutil.which("javac"), "-proc:none", "-Xlint:none", "-d", "."], wrap_java(code), ".java")
    return None if ok else java_problem(out)


def _js(code: str) -> str | None:
    ok, out = _run([shutil.which("node"), "--check"], code, ".js")
    return None if ok else next((ln.strip() for ln in out.splitlines() if "Error" in ln), out.strip()[:160])


CHECKERS = {"python": (lambda: True, _python), "json": (lambda: True, _json), "c": (lambda: shutil.which("gcc"), lambda c: _c_family(c, "c")),
            "cpp": (lambda: shutil.which("g++"), lambda c: _c_family(c, "cpp")),
            "java": (lambda: shutil.which("javac"), _java), "js": (lambda: shutil.which("node"), _js)}


def check_code(deck: LectureDeck) -> tuple[list[dict], list[dict]]:
    """(findings, report): the report has one row per code figure, {slide, language, status ok|error|unchecked, detail}."""
    found, report = [], []
    for i, s in enumerate(deck.slides, FIRST_CONTENT_SLIDE):
        f = s.figure
        if f.kind != "code" or not f.code.strip():
            continue
        lang, sid = LANG.get(f.language.strip().lower()), f"slide {i}"
        available, checker = CHECKERS.get(lang, (lambda: False, None))
        if not available():
            why = f"no checker for '{f.language or 'unnamed'}' on this machine" + ("; install a JDK to check Java" if lang == "java" else "")
            report.append({"slide": i, "language": f.language, "status": "unchecked", "detail": why})
            found.append(v("D-UNVERIFIED", WARN, [sid], f"{sid}: the {f.language or 'code'} snippet was not checked ({why}); read it before teaching"))
            continue
        problem = checker(f.code)
        report.append({"slide": i, "language": f.language, "status": "error" if problem else "ok", "detail": problem or ""})
        if problem:
            found.append(v("D-CODE", ERR, [sid], f"{sid}: the {f.language} snippet does not compile: {problem}"))
    return found, report


# ------------------------------------------------------------------ citations
def check_grounding(deck: LectureDeck, sources: dict[str, dict], floor: float, embed) -> list[dict]:
    keys = list(sources)
    cites = [(i, s) for i, s in enumerate(deck.slides, FIRST_CONTENT_SLIDE) if s.sources]
    if not keys or not cites:
        return []
    src = embed([f"{sources[k]['title']}" for k in keys])
    slides = embed([f"{s.title}. {' '.join(s.bullets)}" for _, s in cites])
    out = []
    for (i, s), e in zip(cites, slides):
        sims = src @ e
        median = float(np.median(sims))
        for k in s.sources:
            if k in keys and float(sims[keys.index(k)]) < min(median, floor):
                out.append(v("D-GROUND", WARN, [f"slide {i}", k],
                             f"slide {i} ('{s.title}') cites [{k}] '{sources[k]['title']}', which matches it weakly "
                             f"({sims[keys.index(k)]:.2f}; average source {median:.2f}): check the citation",
                             similarity=round(float(sims[keys.index(k)]), 3)))
    return out


def verify(deck: LectureDeck, sources: dict[str, dict], cfg: dict, embed=None) -> tuple[list[dict], list[dict]]:
    """Code and citation checks: (findings, code report). `embed` overrides the local model (tests)."""
    if embed is None:
        from profsagent.delivery.common import embed
    found, report = check_code(deck)
    found += check_grounding(deck, sources, cfg["verify"]["grounding_floor"], embed)
    for x in found:
        x["stage"] = "content"
    return found, report
