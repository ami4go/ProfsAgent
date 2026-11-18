"""Deliverable B: the lecture's running example, with every number computed by code (prompt B6).

    make_example(llm, ctx, cfg, run_id, log) -> (example | None, calls)   B6 writes the data and Python; code runs it
    run_code(code, timeout_s) -> values                                    the values dict the code assigned
    fill_values(deck, values) -> (deck, unknown)                           [[name]] in the slides -> the computed value
    fmt(value, latex) -> str                                               how a value is written on a slide

Why: a model that types numbers gets arithmetic wrong (OpenMAIC's slides had wrong sums until the numbers were given to
it). Here the model never types a number from the example: it writes [[name]] and code fills in what the example's
code computed. Plots (Figure.plot) are drawn from the same values.

Safety: the code comes from a model, so before it runs it must pass an AST check (imports only from ALLOWED, no file,
process or reflection built-ins, no dunder attributes). It then runs in a separate `python -I` process, in an empty
temporary folder, with a minimal environment (no API keys) and a timeout.
"""
from __future__ import annotations

import ast
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

from profsagent.content.models import Example, LectureDeck

ALLOWED = {"numpy", "math", "fractions", "statistics", "itertools", "functools", "decimal", "heapq", "collections"}
BANNED = {"open", "exec", "eval", "compile", "__import__", "input", "globals", "locals", "vars", "getattr", "setattr",
          "delattr", "breakpoint", "help", "exit", "quit", "memoryview", "classmethod", "staticmethod", "type", "object"}
PLACEHOLDER = re.compile(r"\[\[([A-Za-z][A-Za-z0-9_]*)\]\]")
NAME = re.compile(r"^[A-Za-z][A-Za-z0-9_]{0,40}$")             # x, X, SS_res, w1: any identifier-like name
INLINE = re.compile(r"\\\(.*?\\\)", re.S)
FOOTER = """
def _plain(v):
    if hasattr(v, "tolist"):
        v = v.tolist()
    if isinstance(v, complex):                    # np.linalg.eig of a symmetric matrix: real values typed as complex
        v = v.real if abs(v.imag) <= 1e-9 * max(1.0, abs(v.real)) else str(v)
    if isinstance(v, (list, tuple)):
        return [_plain(x) for x in v]
    if isinstance(v, bool) or v is None:
        return v
    if isinstance(v, (int, float, str)):
        return v
    try:
        return float(v)
    except Exception:
        return str(v)
import json as _json
print("<<VALUES>>" + _json.dumps({str(k): _plain(v) for k, v in values.items()}))
"""


# ------------------------------------------------------------------ running the code
def unsafe(code: str) -> str | None:
    """Why the code may not run, or None."""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return f"syntax error on line {e.lineno}: {e.msg}"
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            mods = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            bad = [m for m in mods if m.split(".")[0] not in ALLOWED]
            if bad:
                return f"import of {bad[0]} is not allowed (only {', '.join(sorted(ALLOWED))})"
        elif isinstance(node, ast.Name) and node.id in BANNED:
            return f"`{node.id}` is not allowed"
        elif isinstance(node, ast.Attribute) and node.attr.startswith("_"):
            return f"attribute `{node.attr}` is not allowed"
    if not any(isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "values" for t in n.targets)
               for n in ast.walk(tree)):
        return "the code must assign a dict named `values`"
    return None


def clean_value(v: Any) -> Any:
    """A JSON value from the code as one the slides can show: a number, a short string, a list of numbers or a matrix
    (list of equal-length lists of numbers). Raises ValueError otherwise."""
    num = lambda x: isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)  # noqa: E731
    if num(v):
        return v
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, str) and len(v) <= 80:
        return v
    if isinstance(v, list) and v and all(num(x) for x in v):
        return v
    if isinstance(v, list) and v and all(isinstance(r, list) and r and all(num(x) for x in r) for r in v) \
            and len({len(r) for r in v}) == 1:
        return v
    raise ValueError("not a finite number, a short string, a list of numbers or a matrix")


def run_code(code: str, timeout_s: float = 20) -> dict[str, Any]:
    """Run the example's code and return its `values`. Raises ValueError with a message for the model on any failure."""
    why = unsafe(code)
    if why:
        raise ValueError(why)
    with tempfile.TemporaryDirectory(prefix="profsagent_example_") as tmp:
        script = Path(tmp) / "example.py"
        script.write_text(code + "\n" + FOOTER, encoding="utf-8")
        env = {"SYSTEMROOT": os.environ.get("SYSTEMROOT", ""), "PATH": str(Path(sys.executable).parent),
               "TEMP": tmp, "TMP": tmp, "PYTHONIOENCODING": "utf-8"}
        try:
            r = subprocess.run([sys.executable, "-I", str(script)], cwd=tmp, env=env, capture_output=True, text=True,
                               timeout=timeout_s, encoding="utf-8", errors="replace")
        except subprocess.TimeoutExpired:
            raise ValueError(f"the code did not finish in {timeout_s:g} s") from None
    if r.returncode != 0:
        last = [ln for ln in r.stderr.strip().splitlines() if ln.strip()][-3:]
        raise ValueError("the code failed: " + " | ".join(last)[:400])
    line = next((ln for ln in r.stdout.splitlines() if ln.startswith("<<VALUES>>")), None)
    if line is None:
        raise ValueError("the code printed no values")
    raw = json.loads(line[len("<<VALUES>>"):])
    out, bad = {}, []
    for k, v in raw.items():
        if not NAME.match(k):
            bad.append(f"name {k!r} is not a plain name (letters, digits and _)")
            continue
        try:
            out[k] = clean_value(v)
        except ValueError as e:
            bad.append(f"{k}: {e}")
    if bad:
        raise ValueError("bad values: " + "; ".join(bad[:6]))
    return out


# ------------------------------------------------------------------ writing values on slides
def fmt_num(x: float, latex: bool = False) -> str:
    if isinstance(x, int) or (float(x).is_integer() and abs(x) < 1e15):
        return str(int(x))
    s = f"{x:.4g}"
    if "e" in s:
        m, e = s.split("e")
        return f"{m} \\times 10^{{{int(e)}}}" if latex else f"{m} × 10^{int(e)}"
    return s


def fmt(v: Any, latex: bool = False) -> str:
    """A value as written on a slide: numbers to 4 significant figures, lists as (a, b, c), matrices as a bmatrix in
    maths and [[a, b], [c, d]] in text."""
    if isinstance(v, str):
        return v
    if isinstance(v, list) and v and isinstance(v[0], list):
        if latex:
            return "\\begin{bmatrix}" + " \\\\ ".join(" & ".join(fmt_num(x, True) for x in r) for r in v) + "\\end{bmatrix}"
        return "[" + ", ".join("[" + ", ".join(fmt_num(x) for x in r) + "]" for r in v) + "]"
    if isinstance(v, list):
        return "(" + ", ".join(fmt_num(x, latex) for x in v) + ")"
    return fmt_num(v, latex)


def preview(v: Any, n: int = 8) -> str:
    """A value as the model sees it in the prompt (long lists shortened)."""
    if isinstance(v, list) and len(v) > n:
        return fmt(v[:n]).rstrip(")") + f", … ({len(v)} items)"
    return fmt(v)


def fill_text(s: str, values: dict, latex: bool, unknown: set) -> str:
    def one(m: re.Match, in_maths: bool) -> str:
        name = m.group(1)
        if name not in values:
            unknown.add(name)
            return m.group(0)
        return fmt(values[name], in_maths)
    if latex:
        return PLACEHOLDER.sub(lambda m: one(m, True), s)
    out, last = [], 0
    for span in INLINE.finditer(s):                   # inside \( \) a value is written as maths
        out.append(PLACEHOLDER.sub(lambda m: one(m, False), s[last:span.start()]))
        out.append(PLACEHOLDER.sub(lambda m: one(m, True), span.group()))
        last = span.end()
    out.append(PLACEHOLDER.sub(lambda m: one(m, False), s[last:]))
    return "".join(out)


def fill_values(deck: LectureDeck, values: dict | None) -> tuple[LectureDeck, set[str]]:
    """The deck with every [[name]] replaced by its computed value (`latex` fields and \\( \\) spans as maths). Unknown
    names are left as they are and returned (checks.py reports them as D-VALUE)."""
    values, unknown = values or {}, set()

    def walk(x: Any, key: str = "") -> Any:
        if isinstance(x, str):
            return fill_text(x, values, key == "latex", unknown) if "[[" in x else x
        if isinstance(x, list):
            return [walk(i, key) for i in x]
        if isinstance(x, dict):
            return {k: walk(v, k) for k, v in x.items()}
        return x
    return LectureDeck.model_validate(walk(deck.model_dump())), unknown


# ------------------------------------------------------------------ B6
def for_b1(ex: dict) -> dict:
    """The example as B1 sees it: the story and each value's name, meaning and (shortened) value."""
    meaning = {n["name"]: n["meaning"] for n in ex.get("names") or []}
    return {"title": ex["title"], "story": ex["story"], **({"conventions": ex["conventions"]} if ex.get("conventions") else {}),
            "values": [{"name": k, "meaning": meaning.get(k, ""), "value": preview(v)} for k, v in ex["values"].items()]}


def make_example(llm, ctx: dict, cfg: dict, run_id: str, log) -> tuple[dict | None, list[dict], str]:
    """B6 for one lecture: (example with its computed values or None, the calls, a note on why there is none). The code
    is run; on failure B6 is asked again with the error (config example.repair_rounds times)."""
    from profsagent.llm.prompts import load_prompt
    e = cfg.get("example") or {}
    p = load_prompt("B6")
    ctx = {**ctx, "problems": []}
    calls, note = [], ""
    for attempt in range(1 + int(e.get("repair_rounds", 1))):
        system, user = p.render(**ctx)
        ex, rec = llm.structured(system=system, user=user, model_cls=Example, role=p.meta.get("model_class", "generate"),
                                 temperature=float(p.meta.get("temperature", 0.2)), prompt_id="B6", prompt_version=p.version,
                                 run_id=run_id)
        calls.append({"prompt": "B6", "endpoint": rec.endpoint, "prompt_tokens": rec.prompt_tokens, "output_tokens": rec.output_tokens})
        log(f"  [B6] ok via {rec.endpoint} · {rec.prompt_tokens}+{rec.output_tokens} tok")
        if not ex.numeric:                          # a case without quantities: the story runs through the lecture
            if ex.title.strip() or ex.story.strip():
                log(f"  [B6] running case '{ex.title}' (no numbers)")
                return {"title": ex.title, "story": ex.story, "numeric": False, "conventions": [], "names": [],
                        "values": {}}, calls, ""
            return None, calls, "B6: no numeric example for this topic"
        try:
            values = run_code(ex.code, float(e.get("timeout_s", 20)))
            missing = [n.name for n in ex.names if n.name not in values]
            if missing:
                raise ValueError(f"`values` lacks the declared names {missing[:8]}")
            if len(values) > int(e.get("max_values", 80)):
                raise ValueError(f"{len(values)} values: at most {e.get('max_values', 80)}")
        except ValueError as err:
            note = str(err)
            log(f"  [B6] attempt {attempt + 1}: {note}")
            ctx["problems"] = [{"code": "D-EXAMPLE", "problem": note, "previous_code": ex.code}]
            continue
        log(f"  [B6] example '{ex.title}': {len(values)} values computed")
        return {"title": ex.title, "story": ex.story, "numeric": True, "conventions": ex.conventions, "code": ex.code,
                "names": [n.model_dump() for n in ex.names], "values": values}, calls, ""
    return None, calls, note
