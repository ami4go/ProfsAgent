"""Regulation checks: the course's frame (credits, L-T-P, teaching weeks) against config/regulations.yaml. NO LLM.

These values are fixed at S1 intake (from the professor's form, else regulation defaults), so no later stage can repair
them: a violation is for the professor to fix or to override with a reason at the gate (e.g. a deliberate half-semester
course).
    VREG-WEEKS    teaching weeks differ from the regulation's teaching weeks
    VREG-CREDITS  credits not offered by the regulation
    VREG-LTP      lecture/tutorial hours per week differ from what the regulation fixes for those credits
"""
from __future__ import annotations

from profsagent.config import regulations
from profsagent.validate.record import ERR, v


def _facts() -> dict[str, dict]:
    return {f["id"]: f for f in regulations()["facts"]}


def credit_rules() -> dict[float, dict]:
    """credits -> {lecture_h_per_week, tutorial_h_per_week?, ref}, from every fact that names a credit value."""
    out = {}
    for fid, f in _facts().items():
        vals = f.get("values") or {}
        if "credits" in vals:
            out[float(vals["credits"])] = {**vals, "ref": fid}
    return out


def teaching_weeks() -> tuple[int, str] | None:
    for fid, f in _facts().items():
        if "teaching_weeks" in (f.get("values") or {}):
            return int(f["values"]["teaching_weeks"]), fid
    return None


def check_regulation(state: dict) -> list[dict]:
    out = []
    tw = teaching_weeks()
    weeks = state.get("weeks")
    if tw and weeks is not None and int(weeks) != tw[0]:
        out.append(v("VREG-WEEKS", ERR, ["COURSE"], f"the course runs {weeks} teaching weeks; {tw[1]} sets {tw[0]}",
                     regulation=tw[1], value=weeks, expected=tw[0]))
    credits = (state.get("defaults") or {}).get("credits")
    rules = credit_rules()
    if credits is None or not rules:
        return out
    rule = rules.get(float(credits))
    if rule is None:
        out.append(v("VREG-CREDITS", ERR, ["COURSE"], f"{credits} credits is not a credit value the regulation defines "
                     f"({', '.join(f'{c:g}' for c in sorted(rules))})", value=credits))
        return out
    ltp = state.get("ltp") or {}
    for part, key in (("L", "lecture_h_per_week"), ("T", "tutorial_h_per_week")):
        if key in rule and ltp.get(part) is not None and abs(float(ltp[part]) - float(rule[key])) > 1e-6:
            out.append(v("VREG-LTP", ERR, ["COURSE"], f"L-T-P {ltp.get('L')}-{ltp.get('T')}-{ltp.get('P')}: {part} = {ltp[part]} h/week, "
                         f"but {rule['ref']} fixes {rule[key]} h/week for a {credits:g}-credit course",
                         regulation=rule["ref"], part=part, value=ltp[part], expected=rule[key]))
    return out
