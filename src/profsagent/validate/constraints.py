"""Constraint compiler: the course's typed constraints (S1 defaults K01–K09 + G3's) as normalised predicates, one checker
per target, deterministic conflict detection, and the list of constraints nothing checks. NO LLM in this module.

G3 writes one requirement in several shapes, e.g. `content.must_exclude[phrase]` with op `==` true, or
`content.must_exclude` with the phrase in `value` and op `not_in`; presence as op `present` or `==` true; component
names as free text ("practical assignments"). compile_constraint() maps them all onto one Pred, so checkers never see
the raw shapes (before this, constraints written in the other shapes were silently never checked).

    VK             a constraint does not hold (error if hard, warning if soft)
    VK-CONTENT     a must_include / must_exclude phrase does not hold
    VK-MALFORMED   the constraint cannot be checked as written (placeholder phrase, op that cannot apply)
    VK-CONFLICT    hard constraints that cannot all hold, found at S3 before any generation
    VK-UNENFORCED  a constraint no checker covers, listed so that nothing passes unchecked
"""
from __future__ import annotations

import datetime
import math
import re
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable

from profsagent.validate.record import ERR, WARN, v
from profsagent.validate.text import covers, norm, toks

NUMERIC_OPS = {"==", "!=", "<=", "<", ">=", ">"}
NUMERIC_KINDS = {"co.count", "co.bloom_max", "co.bloom_min", "lab.hours_per_week", "schedule.weeks",
                 "schedule.lecture_hours_per_week", "schedule.tutorial_hours_per_week", "schedule.midsem_after_week",
                 "course.credits", "content.max_hours_on[]", "assessment.component[].weight_pct",
                 "assessment.component[].instances", "assessment.component_count", "assessment.events_per_week",
                 "resource.max_age_years"}
PRESENCE_KINDS = {"assessment.component[].present", "lab.present"}
DESCRIPTIVE_TOKENS = 7    # a content phrase with more content words is a description of an approach, not checkable


@dataclass(frozen=True)
class Pred:
    id: str
    kind: str                 # target with [] for each argument, e.g. "assessment.component[].present"
    args: tuple
    op: str                   # numeric op | present | absent | include | exclude | before | in | blocked
    value: object
    hard: bool
    target: str
    raw: str = ""
    malformed: str | None = None


def _parse(target: str) -> tuple[str, list[str]]:
    """'assessment.component[final project].present' -> ('assessment.component[].present', ['final project']).
    Whitespace is dropped outside brackets only ('content.must_ exclude' is a G3 typo; phrases keep their spaces)."""
    parts = re.split(r"(\[[^\]]*\])", target or "")
    t = "".join(p if p.startswith("[") else re.sub(r"\s+", "", p) for p in parts)
    kind, args = [], []
    for name, arg in re.findall(r"([A-Za-z_]+)(\[[^\]]*\])?", t):
        kind.append(name.lower() + ("[]" if arg else ""))
        if arg:
            args.append(arg[1:-1].strip().strip("'\""))
    return ".".join(kind), args


def _truth(x) -> bool | None:
    if isinstance(x, bool):
        return x
    if isinstance(x, (int, float)):
        return bool(x)
    if isinstance(x, str) and x.strip().lower() in ("true", "yes", "present", "required"):
        return True
    if isinstance(x, str) and x.strip().lower() in ("false", "no", "absent", "none"):
        return False
    return None


def _num(x) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def compile_constraint(c: dict) -> Pred:
    target = c.get("target") or ""
    kind, args = _parse(target)
    op = str(c.get("op") or "").strip().lower()
    val = c.get("value")
    mal = None
    if kind in ("content.must_include", "content.must_exclude"):          # phrase given in `value`
        kind, args = kind + "[]", ([val] if isinstance(val, str) else [])
    if kind in ("content.must_include[]", "content.must_exclude[]", "content.max_hours_on[]"):
        phrase = (args[0] if args else "").strip()
        if (not phrase or phrase.startswith("<")) and isinstance(val, str) and kind != "content.max_hours_on[]":
            phrase = val.strip().strip("'\"")
        if not phrase or phrase.startswith("<") or not toks(phrase):
            mal = f"placeholder or empty phrase in '{target}'"
        elif len(toks(phrase) - {"and", "the", "with", "using", "than", "rather"}) > DESCRIPTIVE_TOKENS:
            mal = f"'{phrase[:80]}' describes an approach rather than content a topic can cover"
        args = [phrase]
        if kind != "content.max_hours_on[]":
            op = "include" if kind == "content.must_include[]" else "exclude"
    if kind in PRESENCE_KINDS:
        t = _truth(val)
        if op in ("present", "in") or (op == "==" and t is not False) or (op == "!=" and t is False):
            op = "present"
        elif op in ("absent", "not_in") or (op == "==" and t is False) or (op == "!=" and t is True):
            op = "absent"
        else:
            mal = f"op '{op}' with value {val!r} cannot express presence"
    elif kind in NUMERIC_KINDS:
        if op not in NUMERIC_OPS:
            mal = mal or f"op '{op}' cannot apply to a number"
        elif _num(val) is None:
            mal = mal or f"value {val!r} is not a number"
    elif kind == "schedule.topic_group[].order_before[]":
        if op == "after" and len(args) == 2:
            args = [args[1], args[0]]
        op = "before"
    elif kind == "schedule.week[].blocked":
        op = "blocked" if _truth(val) is not False else "open"
    elif kind in ("schedule.topic_group[].weeks", "lab.tools_include", "resource.type_allowed"):
        op = "in"
    return Pred(id=c.get("id", "?"), kind=kind, args=tuple(args), op=op, value=val, hard=c.get("hardness") == "hard",
                target=target, raw=str(c.get("raw") or "")[:160], malformed=mal)


def compile_all(constraints: list[dict]) -> list[Pred]:
    return [compile_constraint(c) for c in constraints or []]


# ------------------------------------------------------------------ state lookups
def _topics(s):
    return [t for m in s.get("modules", []) for t in m["topics"]]


def _comps(s):
    return (s.get("assessment") or {}).get("components", [])


def _labs(s):
    return (s.get("labs_tutorials") or {}).get("labs", [])


def _holds(measured: float, op: str, val: float) -> bool:
    return {"==": abs(measured - val) < 0.01, "!=": abs(measured - val) >= 0.01, "<=": measured <= val + 1e-6,
            "<": measured < val, ">=": measured >= val - 1e-6, ">": measured > val}[op]


def _fail(p: Pred, msg: str, code: str = "VK", **ev) -> dict:
    return v(code, ERR if p.hard else WARN, [p.id], msg, constraint=p.target, raw=p.raw, **ev)


def _numeric(p: Pred, measured: float | None, what: str) -> list[dict]:
    if measured is None:
        return []
    val = float(p.value)
    return [] if _holds(measured, p.op, val) else [_fail(p, f"{what} is {measured:g}, but {p.id} requires {p.op} {val:g}")]


def _singular(w: str) -> str:
    return w[:-1] if w.endswith("s") and len(w) > 3 else w


def component_type(name: str) -> str | None:
    """The canonical assessment type a constraint's component name denotes, or None when a rule cannot tell
    ("hands-on coding exercises" could be assignments, labs or neither): exact type, a type word inside the name
    ("final project" -> project), else the corpus label mapper."""
    from profsagent.config import pedagogy
    from profsagent.kg.stub import ASSESS_TYPES, assess_type   # kept local: kg.stub loads the retrieval stack
    known = set(pedagogy()["thresholds"]["weight_band_fallback"]) | {t for t, _ in ASSESS_TYPES}
    key = re.sub(r"[\s_-]+", " ", (name or "").lower()).strip()
    if key in known:
        return key
    hit = next((w for w in (_singular(x) for x in re.findall(r"[a-z]+", key)) if w in known), None)
    if hit:
        return hit
    mapped = assess_type(name)
    return None if mapped == "other" else mapped


def find_component(s: dict, name: str) -> dict | None:
    """The assessment component a constraint names: exact type, else the type the name resolves to (component_type),
    else, for names that are not a type, an instance whose format covers the name."""
    comps = _comps(s)
    key = re.sub(r"[\s_-]+", " ", (name or "").lower()).strip()
    for c in comps:
        if str(c["type"]).lower().replace("_", " ") == key:
            return c
    words = {_singular(w) for w in re.findall(r"[a-z]+", key)}
    for c in comps:
        if _singular(str(c["type"]).lower()) in words:
            return c
    typ = component_type(name)   # same resolution as everywhere else: "final project" is a project, not the end-sem
    if typ:
        return next((c for c in comps if str(c["type"]).lower() == typ), None)
    for c in comps:
        if covers(name, [i.get("format", "") for i in c["instances"]]):
            return c
    return None


def _content_texts(s: dict) -> list[str]:
    lt = s.get("labs_tutorials") or {}
    return ([t["title"] for t in _topics(s)] + [lo.get("statement", "") for lo in s.get("los", [])]
            + [x.get("exercise", "") + " " + x.get("title", "") for x in lt.get("labs", [])]
            + [x.get("activity", "") for x in lt.get("tutorials", [])]
            + [i.get("format", "") for c in _comps(s) for i in c["instances"]])


def _weeks_of(value) -> set[int] | None:
    if isinstance(value, (int, float)):
        return {int(value)}
    if isinstance(value, list):
        out = set()
        for x in value:
            w = _weeks_of(x)
            if w is None:
                return None
            out |= w
        return out
    if isinstance(value, str):
        m = re.fullmatch(r"\s*(\d+)\s*[-–]\s*(\d+)\s*", value)
        if m:
            return set(range(int(m.group(1)), int(m.group(2)) + 1))
        nums = re.findall(r"\d+", value)
        return {int(n) for n in nums} or None
    return None


# ------------------------------------------------------------------ checkers: kind -> (stage, fn(state, pred))
def _c_co_count(s, p):
    return _numeric(p, len(s["cos"]) if "cos" in s else None, "the number of COs")


def _c_co_bloom(s, p):
    if not s.get("cos"):
        return []
    lv = [int(c["bloom_level"]) for c in s["cos"]]
    return _numeric(p, max(lv) if p.kind == "co.bloom_max" else min(lv), "the highest CO Bloom level" if p.kind == "co.bloom_max" else "the lowest CO Bloom level")


def _c_lab_present(s, p):
    if "labs_tutorials" not in s:
        return []
    has = bool(_labs(s))
    if p.op == "present" and not has:
        return [_fail(p, f"no lab sessions are planned, but {p.id} requires a lab")]
    if p.op == "absent" and has:
        return [_fail(p, f"{len(_labs(s))} lab sessions are planned, but {p.id} rules labs out")]
    return []


def _c_lab_hours(s, p):
    return _numeric(p, _num((s.get("ltp") or {}).get("P")), "lab hours per week (L-T-P P)")


def _c_lab_tools(s, p):
    if not _labs(s):
        return []
    tools = [" ".join(map(str, lab.get("tools") or [])) for lab in _labs(s)]
    want = p.value if isinstance(p.value, list) else [p.value]
    missing = [w for w in want if isinstance(w, str) and w.strip() and not covers(w, tools)]
    if not missing:
        return []
    infra = ((s.get("cco_compact") or {}).get("lab") or {}).get("infrastructure") or []
    infra = infra if isinstance(infra, list) else [str(infra)]
    provided = [w for w in missing if covers(w, [str(x) for x in infra])]
    out = [_fail(p, f"no lab lists the tool(s) {[w for w in missing if w not in provided]} that {p.id} requires")]         if len(provided) < len(missing) else []
    if provided:   # listed by the professor as available infrastructure (e.g. "TA support"), not a tool a lab uses
        out.append(v("VK", WARN, [p.id], f"{provided} is available lab infrastructure but no lab names it ({p.id}); confirm",
                     constraint=p.target, raw=p.raw))
    return out


def _c_schedule_weeks(s, p):
    sch = s.get("schedule") or {}
    n = len(sch["weeks"]) if sch.get("weeks") else s.get("weeks")
    return _numeric(p, _num(n), "the number of teaching weeks")


def _c_ltp_part(s, p):
    part = "L" if p.kind == "schedule.lecture_hours_per_week" else "T"
    return _numeric(p, _num((s.get("ltp") or {}).get(part)), "lecture hours per week" if part == "L" else "tutorial hours per week")


def _c_midsem_week(s, p):
    mid = [i for c in _comps(s) if str(c["type"]).lower() == "midsem" for i in c["instances"]]
    if not mid:
        return []
    wk, val = mid[0]["release_week"], float(p.value)
    if p.op == "==":   # "after week M": the exam sits at the end of week M or in week M + 1
        return [] if wk in (val, val + 1) else [_fail(p, f"the mid-sem is in week {wk}, but {p.id} puts it after week {val:g}")]
    return _numeric(p, float(wk), "the mid-sem week")


def _c_credits(s, p):
    return _numeric(p, _num((s.get("defaults") or {}).get("credits")), "the credits")


def _c_week_blocked(s, p):
    sch = s.get("schedule") or {}
    n = int(_num(p.args[0]) or 0) if p.args else 0
    week = next((w for w in sch.get("weeks", []) if w["week"] == n), None)
    if week is None or p.op != "blocked":
        return []
    labs = [lab["id"] for lab in _labs(s) if lab.get("week") == n]
    if week["items"] or labs:
        return [_fail(p, f"week {n} has {len(week['items'])} lecture topics and {len(labs)} labs, but {p.id} blocks that week")]
    return []


def _tg_weeks(s, tg) -> list[int]:
    tw = (s.get("schedule") or {}).get("topic_weeks", {})
    return sorted({w for t in _topics(s) if tg in t.get("covers_topic_groups", []) for w in tw.get(t["id"], [])})


def _c_tg_order(s, p):
    if len(p.args) != 2:
        return [_fail(p, f"{p.id}: cannot read the two topic groups in '{p.target}'", "VK-MALFORMED")]
    a, b = _tg_weeks(s, p.args[0]), _tg_weeks(s, p.args[1])
    if not a or not b:
        return []
    return [] if a[0] < b[0] else [_fail(p, f"{p.args[0]} starts in week {a[0]}, not before {p.args[1]} (week {b[0]}) as {p.id} requires")]


def _c_tg_weeks(s, p):
    allowed = _weeks_of(p.value)
    if not p.args or allowed is None:
        return [_fail(p, f"{p.id}: cannot read the allowed weeks in {p.value!r}", "VK-MALFORMED")]
    got = _tg_weeks(s, p.args[0])
    outside = [w for w in got if w not in allowed]
    return [_fail(p, f"{p.args[0]} is taught in weeks {outside} outside {sorted(allowed)} ({p.id})")] if outside else []


def _c_content(s, p):
    if not _topics(s):
        return []
    phrase = p.args[0] if p.args else ""
    texts = _content_texts(s)
    # include: the phrase's words may be spread over the course ("hands-on development" across labs and topics);
    # exclude: only a single text counts, so scattered common words do not look like the excluded subject
    hit = covers(phrase, [" ".join(texts)]) if p.op == "include" else covers(phrase, texts)
    if p.op == "include" and not hit:
        words = toks(phrase) - {"and", "the", "using", "with"}
        seen = sorted(words & toks(" ".join(texts)))
        if seen:   # partly covered: whether the course means the same thing is a judgement, not a rule (stage 4: semantic)
            return [v("VK-CONTENT", WARN, [p.id], f"required content '{phrase}' ({p.id}) is only partly covered (found {seen}); "
                      f"confirm the course teaches it", constraint=p.target, raw=p.raw)]
        return [_fail(p, f"required content '{phrase}' ({p.id}) is not covered by any topic or LO", "VK-CONTENT")]
    if p.op == "exclude" and hit:
        return [_fail(p, f"excluded content '{phrase}' ({p.id}) appears in the course", "VK-CONTENT")]
    return []


def _c_max_hours_on(s, p):
    if not _topics(s):
        return []
    hrs = sum(float(t["est_hours"]) for t in _topics(s) if covers(p.args[0], [t["title"]]))
    return _numeric(p, hrs, f"lecture hours on '{p.args[0]}'")


def _c_component_present(s, p):
    if "assessment" not in s:
        return []
    name = p.args[0] if p.args else ""
    comp = find_component(s, name)
    if p.op == "absent" and comp:
        return [_fail(p, f"{name} present but {'hard' if p.hard else 'soft'} constraint {p.id} forbids it")]
    if p.op == "present" and not comp and (p.hard or p.id not in ("K06", "K07")):   # soft K06/K07 are reported as VA-REG
        if component_type(name) is None:   # the name is not a component type: a rule cannot tell, so ask
            return [v("VK", WARN, [p.id], f"no assessment component recognisably matches '{name}' ({p.id}); confirm that "
                      f"an existing component covers it, or add one", constraint=p.target, raw=p.raw)]
        return [_fail(p, f"no {name} component although {'hard' if p.hard else 'soft'} constraint {p.id} requires one")]
    return []


def _c_component_weight(s, p):
    if "assessment" not in s:
        return []
    name = p.args[0] if p.args else ""
    comp = find_component(s, name)
    if not comp and component_type(name) is None:
        return [v("VK", WARN, [p.id], f"no assessment component recognisably matches '{name}' ({p.id}); its weight cannot be "
                  f"checked", constraint=p.target, raw=p.raw)]
    w = float(comp["weight_pct"]) if comp else 0.0   # a missing component of a known type weighs 0
    return _numeric(p, w, f"{name or '?'} weight")


def _c_component_instances(s, p):
    if "assessment" not in s:
        return []
    comp = find_component(s, p.args[0] if p.args else "")
    return _numeric(p, float(len(comp["instances"])) if comp else 0.0, f"{p.args[0] if p.args else '?'} instances")


def _c_component_count(s, p):
    return _numeric(p, float(len(_comps(s))) if "assessment" in s else None, "the number of assessment components")


def _c_events_per_week(s, p):
    if "assessment" not in s:
        return []
    per = defaultdict(int)
    for c in _comps(s):
        for i in c["instances"]:
            per[i["due_week"]] += 1
    return _numeric(p, float(max(per.values(), default=0)), "the most assessment events due in one week")


def _c_resource_type(s, p):
    allowed = {norm(x) for x in (p.value if isinstance(p.value, list) else [p.value]) if isinstance(x, str)}
    if not allowed:
        return [_fail(p, f"{p.id}: cannot read the allowed resource types in {p.value!r}", "VK-MALFORMED")]
    bad = [r.get("title", "?") for r in s.get("resources", []) if norm(r.get("role", "")) not in allowed]
    return [_fail(p, f"resources {bad} are not of an allowed type {sorted(allowed)} ({p.id})")] if bad else []


def _c_resource_age(s, p):
    oldest = min((int(r["year"]) for r in s.get("resources", []) if _num(r.get("year")) is not None), default=None)
    if oldest is None:
        return []
    return _numeric(p, float(datetime.date.today().year - oldest), "the age in years of the oldest resource")


CHECKERS: dict[str, tuple[str, Callable[[dict, Pred], list[dict]]]] = {
    "course.credits": ("intake", _c_credits),
    "co.count": ("cos", _c_co_count), "co.bloom_max": ("cos", _c_co_bloom), "co.bloom_min": ("cos", _c_co_bloom),
    "content.must_include[]": ("structure", _c_content), "content.must_exclude[]": ("structure", _c_content),
    "content.max_hours_on[]": ("structure", _c_max_hours_on),
    "schedule.weeks": ("schedule", _c_schedule_weeks), "schedule.lecture_hours_per_week": ("schedule", _c_ltp_part),
    "schedule.tutorial_hours_per_week": ("schedule", _c_ltp_part), "schedule.midsem_after_week": ("schedule", _c_midsem_week),
    "schedule.week[].blocked": ("schedule", _c_week_blocked), "schedule.topic_group[].order_before[]": ("schedule", _c_tg_order),
    "schedule.topic_group[].weeks": ("schedule", _c_tg_weeks),
    "lab.present": ("labs", _c_lab_present), "lab.hours_per_week": ("labs", _c_lab_hours), "lab.tools_include": ("labs", _c_lab_tools),
    "assessment.component[].present": ("assessment", _c_component_present),
    "assessment.component[].weight_pct": ("assessment", _c_component_weight),
    "assessment.component[].instances": ("assessment", _c_component_instances),
    "assessment.component_count": ("assessment", _c_component_count),
    "assessment.events_per_week": ("assessment", _c_events_per_week),
    "resource.type_allowed": ("resources", _c_resource_type), "resource.max_age_years": ("resources", _c_resource_age),
}


def check_stage(state: dict, stage: str) -> list[dict]:
    """Check every constraint whose target this stage produces."""
    out = []
    for p in compile_all(state.get("constraints")):
        stage_fn = CHECKERS.get(p.kind)
        if not stage_fn or stage_fn[0] != stage:
            continue
        if p.malformed:
            out.append(v("VK-MALFORMED", WARN, [p.id], f"constraint {p.id} cannot be checked as written: {p.malformed}",
                         constraint=p.target, raw=p.raw))
            continue
        out += stage_fn[1](state, p)
    return out


# ------------------------------------------------------------------ S3: conflicts and coverage
def _interval_conflict(preds: list[Pred]) -> bool:
    lo, lo_open, hi, hi_open = -math.inf, False, math.inf, False
    eq, ne = set(), set()
    for p in preds:
        x = float(p.value)
        if p.op == "==":
            eq.add(round(x, 6))
        elif p.op == "!=":
            ne.add(round(x, 6))
        elif p.op in ("<=", "<"):
            if x < hi or (x == hi and p.op == "<"):
                hi, hi_open = x, p.op == "<"
        elif p.op in (">=", ">"):
            if x > lo or (x == lo and p.op == ">"):
                lo, lo_open = x, p.op == ">"
    if len(eq) > 1:
        return True
    if eq:
        e = next(iter(eq))
        return e in ne or e < lo or e > hi or (e == lo and lo_open) or (e == hi and hi_open)
    return lo > hi or (lo == hi and (lo_open or hi_open or lo in ne))


def conflicts(state: dict) -> list[dict]:
    preds = [p for p in compile_all(state.get("constraints")) if p.hard and not p.malformed]
    out = []
    numeric, presence = defaultdict(list), defaultdict(list)
    for p in preds:
        if p.kind in NUMERIC_KINDS:
            numeric[(p.kind, p.args)].append(p)
        elif p.kind in PRESENCE_KINDS:
            presence[(p.kind, tuple(norm(a) for a in p.args))].append(p)
    for (kind, args), ps in numeric.items():
        if len(ps) > 1 and _interval_conflict(ps):
            out.append(v("VK-CONFLICT", ERR, [p.id for p in ps], f"hard constraints {', '.join(f'{p.id} ({p.op} {p.value})' for p in ps)} "
                         f"on {kind.replace('[]', '')}{list(args) if args else ''} cannot all hold", constraints=[p.target for p in ps]))
    for (kind, args), ps in presence.items():
        if {p.op for p in ps} >= {"present", "absent"}:
            out.append(v("VK-CONFLICT", ERR, [p.id for p in ps], f"hard constraints {', '.join(p.id for p in ps)} both require and forbid "
                         f"{kind.replace('[]', '')}{list(args) if args else ''}"))
    inc = [p for p in preds if p.op == "include"]
    for e in (p for p in preds if p.op == "exclude"):
        for i in inc:
            if covers(e.args[0], [i.args[0]]) or covers(i.args[0], [e.args[0]]):
                out.append(v("VK-CONFLICT", ERR, [i.id, e.id], f"{i.id} requires '{i.args[0]}' but {e.id} excludes '{e.args[0]}'"))
    band = state.get("co_count")      # institutional CO-count rule for the course's credits
    if band:
        for p in (q for q in preds if q.kind == "co.count"):
            feasible = [n for n in range(int(band["min"]), int(band["max"]) + 1) if _holds(float(n), p.op, float(p.value))]
            if not feasible:
                out.append(v("VK-CONFLICT", ERR, [p.id, "CO-COUNT-RULE"], f"{p.id} requires {p.op} {p.value} COs, but the "
                             f"{band.get('basis', 'course template')} allows {band['min']}–{band['max']}"))
    return out


def unenforced(state: dict) -> list[dict]:
    out = []
    for p in compile_all(state.get("constraints")):
        if p.kind not in CHECKERS:
            out.append(v("VK-UNENFORCED", WARN, [p.id], f"no check exists for constraint {p.id} ('{p.target}'); "
                         f"confirm it by hand: {p.raw or p.value}", constraint=p.target))
    return out


def check_constraints(state: dict) -> list[dict]:
    """S3: conflicts between hard constraints, and the constraints that no checker covers."""
    return conflicts(state) + unenforced(state)


def coverage(state: dict) -> dict:
    preds = compile_all(state.get("constraints"))
    checked = [p.id for p in preds if p.kind in CHECKERS and not p.malformed]
    return {"total": len(preds), "checked": len(checked), "malformed": [p.id for p in preds if p.kind in CHECKERS and p.malformed],
            "unenforced": [p.id for p in preds if p.kind not in CHECKERS]}
