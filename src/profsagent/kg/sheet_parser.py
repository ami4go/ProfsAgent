"""Deterministic parser for IIIT-D course-directory sheets (published Google Sheets exported as CSV).

STUB-SIDE ONLY. The KG teammate owns the production extractor (prompts E1–E4). This parser is good enough to
give the design pipeline realistic retrieval text and priors: header fields, prerequisites, COs, weekly
lecture/lab plan, assessment plan and resources, each with row references.
"""
from __future__ import annotations

import csv
import io
import re

CODE_RE = re.compile(r"\b([A-Z]{2,4})\s?-?(\d{3}[A-Z]?)\b")
CO_LABEL_RE = re.compile(r"^\s*C\s*O?\s*0*(\d{1,2})\s*$", re.I)
SECTION_ANCHORS = [
    ("prereq", re.compile(r"^pre-?requisites?\s*$", re.I)),
    ("cos", re.compile(r"^(post\s*conditions?|course\s+outcomes?)", re.I)),
    ("lecture", re.compile(r"^weekly\s+lecture\s+plan", re.I)),
    ("lab", re.compile(r"^weekly\s+lab\s+plan", re.I)),
    ("assessment", re.compile(r"^assessment\s+plan", re.I)),
    ("resources", re.compile(r"^resource\s+material", re.I)),
]
HEADER_KEYS = {
    "course code": "code_raw",
    "department": "department",
    "course name": "name",
    "credits": "credits",
    "course offered to": "offered_to",
    "course description": "description",
}


def norm_codes(text: str) -> list[str]:
    return [f"{a}{b}" for a, b in CODE_RE.findall(text or "")]


def _cells(row: list[str]) -> list[str]:
    return [(c or "").strip() for c in row]


def _first_value(row: list[str]) -> str | None:
    for c in row[1:]:
        if c.strip():
            return c.strip()
    return None


def _is_junk(first: str) -> bool:
    return first.startswith("*please") or first.startswith("*plase")


def parse_sheet_csv(text: str) -> dict:
    rows = [_cells(r) for r in csv.reader(io.StringIO(text))]
    out: dict = {
        "header": {},
        "prerequisites": [],
        "cos": [],
        "lecture_weeks": [],
        "lab_weeks": [],
        "assessment": [],
        "resources": [],
        "warnings": [],
        "template_version": "old",
    }
    section = "header"
    table_cols: list[str] | None = None
    prereq_cols: dict[int, str] | None = None
    co_label_cols: dict[int, str] | None = None
    last_prereq_kind = "mandatory"

    for ri, row in enumerate(rows, start=1):
        if not any(row):
            continue
        first = row[0]
        fl = first.lower()
        if _is_junk(fl):
            continue
        # section switch
        switched = False
        for name, rx in SECTION_ANCHORS:
            if rx.match(first):
                section, table_cols, prereq_cols, co_label_cols = name, None, None, None
                switched = True
                if name == "lab":
                    out["template_version"] = "new"
                break
        if switched:
            # "Pre-requisites" rows sometimes carry values on the same row
            if section == "prereq" and _first_value(row):
                out["prerequisites"].append({"kind": "mandatory", "raw": _first_value(row), "row": ri})
            continue

        if section == "header":
            key = next((v for k, v in HEADER_KEYS.items() if fl.startswith(k)), None)
            if key:
                out["header"][key] = _first_value(row)
                if key == "department":
                    out["template_version"] = "new"
            elif fl.startswith("whether the course") or fl.startswith("if the course"):
                out["header"].setdefault("counting_notes", []).append(_first_value(row))
            continue

        if section == "prereq":
            kinds = {i: k for i, c in enumerate(row) for k in ("mandatory", "desirable", "other") if k in c.lower()}
            if len(kinds) >= 2:  # column layout header
                prereq_cols = kinds
                continue
            if prereq_cols:
                for i, kind in prereq_cols.items():
                    if i < len(row) and row[i]:
                        out["prerequisites"].append({"kind": kind, "raw": row[i], "row": ri})
                continue
            kind = next((k for k in ("mandatory", "desirable", "other") if k in fl), None)
            if kind:
                last_prereq_kind = kind
                val = _first_value(row)
                if val:
                    out["prerequisites"].append({"kind": kind, "raw": val, "row": ri})
            elif first:
                out["prerequisites"].append({"kind": last_prereq_kind, "raw": " ".join(c for c in row if c), "row": ri})
            continue

        if section == "cos":
            labels = {i: CO_LABEL_RE.match(c).group(1) for i, c in enumerate(row) if c and CO_LABEL_RE.match(c)}
            if len(labels) >= 2 and len(labels) == sum(1 for c in row if c):
                co_label_cols = labels
                continue
            if co_label_cols:
                for i, n in co_label_cols.items():
                    if i < len(row) and row[i]:
                        out["cos"].append({"label": f"CO{int(n)}", "text": row[i], "row": ri})
                co_label_cols = None
                continue
            inline = [re.match(r"^\s*C\s*O?\s*0*(\d{1,2})\s*[:.)-]\s*(.+)$", c, re.S) for c in row if c]
            if inline and all(inline):
                for mm in inline:
                    out["cos"].append({"label": f"CO{int(mm.group(1))}", "text": mm.group(2).strip(), "row": ri})
                continue
            if fl.startswith("week"):  # lecture table without a 'Weekly Lecture Plan' heading
                section, table_cols = "lecture", [c.lower() for c in row]
                continue
            m = CO_LABEL_RE.match(first)
            if m and _first_value(row):
                out["cos"].append({"label": f"CO{int(m.group(1))}", "text": _first_value(row), "row": ri})
            continue

        if section in ("lecture", "lab"):
            if fl.startswith("week") and not re.match(r"^week\s*\d", fl):
                table_cols = [c.lower() for c in row]
                continue
            if table_cols is None:
                if "does not have a lab" in fl or "no lab" in fl:
                    continue
                table_cols = ["week number", "topic", "cos met", "col3", "col4"]
            wk = re.match(r"^\s*(?:week\s*)?(\d{1,2})(?:\s*(?:-|–|to|&|,)\s*(\d{1,2}))?\s*$", first, re.I)
            rec = {"row": ri, "week": int(wk.group(1)) if wk else None}
            if wk and wk.group(2):
                rec["week_end"] = int(wk.group(2))
            for i, c in enumerate(row[1:], start=1):
                col = table_cols[i] if i < len(table_cols) else f"col{i}"
                if not c:
                    continue
                if "cos" in col or "co met" in col:
                    rec["cos_met_raw"] = c
                elif "tutorial" in col:
                    rec["tutorial"] = c
                elif "assignment" in col or "project" in col:
                    rec["assignments"] = c
                elif "platform" in col or "software" in col or "hardware" in col:
                    rec["platform"] = c
                elif "topic" in col or "exercise" in col or "laboratory" in col or i == 1:
                    rec["topic_raw"] = c
                else:
                    rec.setdefault("other", []).append(c)
            if rec["week"] is None and not rec.get("topic_raw"):
                continue
            if rec["week"] is None and out[f"{section}_weeks"]:
                # continuation row: append to previous week
                prev = out[f"{section}_weeks"][-1]
                for k, v in rec.items():
                    if k in ("row", "week"):
                        continue
                    prev[k] = (prev.get(k, "") + "\n" + v) if isinstance(v, str) else v
                continue
            rec["co_refs"] = sorted({f"CO{int(n)}" for n in re.findall(r"C\s*O?\s*0*(\d{1,2})", rec.get("cos_met_raw", ""), re.I)})
            out[f"{section}_weeks"].append(rec)
            continue

        if section == "assessment":
            if fl.startswith("type of evaluation"):
                continue
            val = _first_value(row)
            num = re.search(r"(\d+(?:\.\d+)?)", val or "")
            if first and num and len(row) > 1 and row[1] and re.search(r"\d", row[1]):
                out["assessment"].append({"raw_label": first, "weight_raw": row[1], "weight_pct": float(num.group(1)), "row": ri})
            elif first:
                out["assessment"].append({"raw_label": first, "weight_raw": val, "weight_pct": None, "row": ri})
            continue

        if section == "resources":
            if fl == "type" or fl.startswith("type,"):
                continue
            val = _first_value(row)
            if first or val:
                out["resources"].append({"type_raw": first or None, "title_raw": val or first, "row": ri})
            continue

    h = out["header"]
    try:
        h["credits"] = int(float(h.get("credits"))) if h.get("credits") else None
    except (TypeError, ValueError):
        out["warnings"].append(f"credits not numeric: {h.get('credits')!r}")
        h["credits"] = None
    h["codes_on_sheet"] = norm_codes(h.get("code_raw") or "")
    weights = [a["weight_pct"] for a in out["assessment"] if a["weight_pct"] is not None]
    out["assessment_weight_sum"] = sum(weights) if weights else None
    if not out["cos"]:
        out["warnings"].append("no COs parsed")
    if not out["lecture_weeks"]:
        out["warnings"].append("no lecture weeks parsed")
    return out
