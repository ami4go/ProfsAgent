r"""Deliverable B: check the arithmetic the slides show (D-ARITH, no AI).

    check_arith(sid, slide) -> findings

A model that writes "SS_res = 0.2^2 + (-0.3)^2 + 0.2^2 + (-0.3)^2 + 0.2^2 = 0.6" has done the sum itself, wrongly. Every
formula on a slide (step lines, `math` blocks, inline \( \) maths in bullets and block text) is split at its = and
\approx signs; the parts made only of numbers are evaluated, and they must agree with each other. A part with a symbol
(a variable, a sum over i, a matrix, a list) is skipped, so only pure arithmetic is checked.

Tolerance: slides round (4 significant figures by content/example.fmt), so parts agree when they differ by at most 1%
of the larger one or 0.006 absolute (for values near 0).
"""
from __future__ import annotations

import ast
import operator
import re

from profsagent.validate.record import ERR, v

INLINE = re.compile(r"\\\((.*?)\\\)", re.S)
SPLIT = re.compile(r"=|\\approx|\\simeq|≈")
SKIP = re.compile(r"<|>|\\le|\\ge|\\neq|\\in\b|\\begin|\\sum|\\prod|\\int|,|%|!")
OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul, ast.Div: operator.truediv,
       ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos}


def to_python(tex: str) -> str | None:
    """A LaTeX expression made only of numbers as a Python expression, or None when it holds anything else."""
    s = tex.strip()
    if not s or SKIP.search(s):
        return None
    s = s.replace("−", "-").replace("×", "*").replace("·", "*")
    s = re.sub(r"\\left|\\right|\\,|\\;|\\!|\\quad|\\qquad|\\displaystyle|\\text\{\s*\}", " ", s)
    s = re.sub(r"\\(?:times|cdot)", "*", s).replace("\\div", "/")
    s = s.replace("\\{", "(").replace("\\}", ")")
    for _ in range(10):                                     # innermost first: \frac{a}{b}, \sqrt{a}, ^{a}
        t = re.sub(r"\\[dt]?frac\{([^{}]*)\}\{([^{}]*)\}", r"((\1)/(\2))", s)
        t = re.sub(r"\\sqrt\{([^{}]*)\}", r"((\1)**0.5)", t)
        t = re.sub(r"\^\{([^{}]*)\}", r"**(\1)", t)
        if t == s:
            break
        s = t
    s = re.sub(r"\^(\d)", r"**\1", s)
    s = s.replace("{", "(").replace("}", ")").replace("[", "(").replace("]", ")")
    if re.search(r"[A-Za-z\\_]", s):                       # a symbol or a command left: not pure arithmetic
        return None
    s = re.sub(r"(\d|\))\s*\(", r"\1*(", s)                  # implicit multiplication: 2(6.8), (a)(b)
    s = re.sub(r"\)\s*(\d)", r")*\1", s)
    if not re.search(r"\d", s) or re.search(r"[^0-9+\-*/(). ]", s):
        return None
    return s


def evaluate(expr: str) -> float | None:
    """The value of a Python arithmetic expression (numbers, + - * / and small powers), None if it is anything else."""
    try:
        tree = ast.parse(expr, mode="eval")
    except SyntaxError:
        return None

    def ev(n):
        if isinstance(n, ast.Expression):
            return ev(n.body)
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return float(n.value)
        if isinstance(n, ast.UnaryOp) and type(n.op) in OPS:
            return OPS[type(n.op)](ev(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in OPS:
            a, b = ev(n.left), ev(n.right)
            if isinstance(n.op, ast.Pow) and abs(b) > 12:
                raise ValueError("power too large")
            return OPS[type(n.op)](a, b)
        raise ValueError("not arithmetic")
    try:
        return ev(tree)
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        return None


def agree(a: float, b: float) -> bool:
    return abs(a - b) <= max(0.01 * max(abs(a), abs(b)), 0.006)


def wrong_parts(tex: str) -> tuple[str, str, float] | None:
    """(the part that disagrees, the part it should equal, its true value) for the first mismatch in one formula."""
    parts = [p for p in SPLIT.split(tex)]
    vals = [(p, evaluate(e) if (e := to_python(p)) else None) for p in parts]
    nums = [(p, x) for p, x in vals if x is not None]
    for (p1, x1), (p2, x2) in zip(nums, nums[1:]):
        if not agree(x1, x2):
            return p2.strip(), p1.strip(), x1
    return None


def formulas(slide) -> list[str]:
    out = [st.latex for b in slide.blocks for st in b.steps] + [b.latex for b in slide.blocks if b.kind == "math"]
    for t in [*slide.bullets, *(b.text for b in slide.blocks)]:
        out += INLINE.findall(t)
    return [f for f in out if f]


def check_arith(sid: str, slide) -> list[dict]:
    out = []
    for f in formulas(slide):
        bad = wrong_parts(f)
        if bad:
            shown, source, true = bad
            out.append(v("D-ARITH", ERR, [sid], f"{sid}: `{source} = {shown}` is wrong: {source} is {true:.4g}. "
                                               "Use the example's computed [[name]] instead of doing arithmetic"))
    return out
