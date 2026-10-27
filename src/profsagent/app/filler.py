"""Step 1 of a course run: fill in every field the professor left blank, before any design work.

One AI call, grounded in the professor's own fields (above all the description), the most similar IIIT-D courses
from the institutional knowledge graph, the UG Regulations 2025 facts and the IIIT-D course template rules.
Code then checks every suggested value: only allowed choices, hours and weeks as the regulations set them, and
cited courses must be among the similar ones that were shown. Writes <run>/fill.json; the professor then checks
and edits the complete form (gate0_details) before the pipeline starts.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from profsagent.app import formmap, views
from profsagent.config import pedagogy, regulations

PROMPT_ID, PROMPT_VERSION = "APP-FILL", "0.1.0"


class Suggestion(BaseModel):
    value: str | list[str]
    reason: str = ""
    sources: list[str] = Field(default_factory=list)


class FillOut(BaseModel):
    fields: dict[str, Suggestion]


SPEC = {
    "topics": "4–7 topic groups, one per line, each as 'A. Group title: topic, topic, topic'",
    "intent_question": "the one central question the course answers (one sentence)",
    "intent_emphasis": "the teaching emphasis (a short phrase)",
    "intent_avoid": "1–3 lines: what the course should NOT become (for example a repeat of an existing IIIT-D course)",
    "department": "the proposing department (one of allowed_values.departments)",
    "credits": "1, 2 or 4",
    "l": "lecture hours per week, as the regulations set them for these credits",
    "t": "tutorial hours per week, as the regulations set them for these credits",
    "p": "lab hours per week (0 when there is no lab)",
    "weeks": "teaching weeks in the semester, as the regulations set them",
    "weekly_effort": "hours a week of student work outside lectures, as a range like '10-12' (template rule)",
    "programmes": "the programmes the course is offered to (a list from allowed_values.programmes)",
    "year": "the students' year (one of allowed_values.years)",
    "background": "what students should already know, naming IIIT-D prerequisite courses by code where suitable",
    "lab": "'weekly' if the course needs a lab every week, otherwise 'none'",
    "lab_infra": "what the lab needs (machines, software, compute, TA support), short",
    "assess_pref": "the preferred assessment components (a list from allowed_values.assessments)",
    "assess_avoid": "assessment components to avoid (a list from allowed_values.assessments; may be empty)",
    "assess_why": "one sentence on why this assessment mix suits the course",
    "special": "special constraints the design must respect, or an empty string if none are needed",
}

SYSTEM = """You help a professor at IIIT-Delhi complete the proposal form for a new course. The professor filled in some
fields and left others blank. Fill in ONLY the fields listed in fields_to_fill; the professor checks every value before
the course is designed.

Rules:
1. Ground every value in the evidence you are given: the professor's own fields (above all the description), the similar
   IIIT-D courses (cite their codes), the regulation facts (cite their ids, e.g. UGREG-2025§4(2)a) and the course template
   rules (cite "template"). Cite "description" when a value comes from the professor's text. Never invent a course code:
   cite only codes that appear in similar_iiitd_courses.
2. Stay consistent with what the professor wrote; never contradict a given field.
3. For choice fields use only the allowed values, spelled exactly as given.
4. Topics: cover what the description promises, at the depth of one semester with these credits. Use the similar courses
   to judge scope and wording, but design for this course: do not copy another course's topic list.
5. Background: name an IIIT-D course as a prerequisite only when it clearly supplies knowledge this course needs.
6. Each reason is one short, specific sentence saying what in the evidence led to the value.

Return JSON only, in this shape:
{"fields": {"<field>": {"value": "<text>" or ["<choice>", ...], "reason": "<one sentence>", "sources": ["description", "CSE201", "UGREG-2025§2", "template"]}}}"""


def _num(x: float) -> str:
    return str(int(x)) if float(x).is_integer() else str(x)


class DetailsFiller:
    def __init__(self, kg=None, llm=None):
        self._kg, self._llm = kg, llm      # injectable for tests; built per run otherwise

    # ---------------------------------------------------------------- evidence
    @staticmethod
    def similar_courses(kg, form: dict, k: int = 6) -> list[dict]:
        query = f"{formmap._s(form.get('name'))}. {formmap._s(form.get('description'))} {formmap._s(form.get('topics'))}"
        out = []
        for hit in kg.search_courses(query, k=k):
            c = kg.course(hit["uid"])
            if not c:
                continue
            ref = views.course_ref(c["uid"])
            out.append({"code": c["uid"], "name": c.get("name"), "credits": c.get("credits"), "level": c.get("level"),
                        "url": ref.get("url") or c.get("catalogue_url"), "description": (c.get("description") or "")[:400],
                        "topics": (c.get("topics") or [])[:20], "prerequisites": c.get("prereq_text"),
                        "assessment": [f"{a['type']} {a['weight_pct']}%" for a in c.get("assessment") or [] if a.get("weight_pct") is not None][:8]})
        return out

    @staticmethod
    def rules() -> tuple[list[dict], list[str]]:
        regs = [{"id": f["id"], "text": f["text"]} for f in regulations()["facts"]]
        ped = pedagogy()
        template = [ped["outside_load"]["basis"], ped["proctored"]["basis"], ped["co_count"]["basis"]]
        return regs, template

    # ---------------------------------------------------------------- the step
    def fill(self, run_dir: Path) -> dict:
        spec = yaml.safe_load((run_dir / "input.yaml").read_text(encoding="utf-8"))
        form = spec["app_form"]
        blanks = [k for k in formmap.FILLABLE if formmap.blank(form, k)]
        llm = self._llm
        if llm is None:
            from profsagent.llm.client import LLMClient
            llm = LLMClient(run_dir / "llm_calls.jsonl")
        kg = self._kg
        if kg is None:
            from profsagent.agents.pipeline import make_kg
            kg = make_kg(llm, (os.environ.get("KG_BACKEND") or "neo4j").lower())
        similar = self.similar_courses(kg, form)
        regs, template = self.rules()
        result = {"at": time.time(), "prompt": f"{PROMPT_ID}@{PROMPT_VERSION}", "given": [k for k in formmap.FILLABLE if k not in blanks],
                  "blanks": blanks, "similar": [{k: c[k] for k in ("code", "name", "credits", "url")} for c in similar],
                  "fields": {}, "unfilled": [], "endpoint": None}
        if blanks:
            given = {k: v for k, v in form.items() if k in ("name", "description", *formmap.FILLABLE) and not formmap.blank(form, k)}
            user = json.dumps({
                "form_given": given,
                "fields_to_fill": {k: SPEC[k] for k in blanks},
                "allowed_values": {"departments": formmap.DEPARTMENTS, "programmes": formmap.PROGRAMMES, "years": list(formmap.YEARS),
                                   "credits": formmap.CREDITS, "assessments": formmap.ASSESSMENTS, "lab": list(formmap.LAB)},
                "similar_iiitd_courses": similar,
                "regulation_facts": regs,
                "template_rules": template,
            }, ensure_ascii=False, indent=1)
            out, rec = llm.structured(system=SYSTEM, user=user, model_cls=FillOut, role="generate", temperature=0.2,
                                      prompt_id=PROMPT_ID, prompt_version=PROMPT_VERSION, run_id=run_dir.name)
            result["endpoint"] = rec.endpoint
            result["fields"] = self.check(out.fields, form, blanks, similar)
        result["unfilled"] = [k for k in blanks if k not in result["fields"]]
        (run_dir / "fill.json").write_text(json.dumps(result, indent=1, ensure_ascii=False), encoding="utf-8")
        return {"status": "waiting", "gate": "gate0_details", "payload": {"gate": "gate0_details", "filled": len(result["fields"]),
                                                                         "unfilled": result["unfilled"]}}

    # ---------------------------------------------------------------- code checks on every suggestion
    @staticmethod
    def check(raw: dict, form: dict, blanks: list[str], similar: list[dict]) -> dict:
        codes = {c["code"].upper(): c for c in similar}
        fields: dict[str, dict] = {}

        def source(s: str) -> dict | None:
            s = str(s).strip()
            code = re.sub(r"\s+", "", s).upper()
            if code in codes:
                c = codes[code]
                return {"text": f"{c['code']} {c.get('name') or ''}".strip(), "url": c.get("url")}
            if s.upper().startswith("UGREG"):
                return views.ref_label(s)
            if "descr" in s.lower() or s.lower() in ("form", "your form"):
                return {"text": "Your description", "url": None}
            if "template" in s.lower():
                return {"text": "IIIT-D course template", "url": None}
            return None    # a course code we didn't show, or anything else: not a usable source

        for k in blanks:
            sug = raw.get(k)
            if sug is None:
                continue
            v = sug.value
            if k in formmap.LISTS:
                items = v if isinstance(v, list) else [x.strip() for x in re.split(r"[,;\n]", v)]
                allowed = formmap.PROGRAMMES if k == "programmes" else formmap.ASSESSMENTS
                v = [x for x in allowed if x in items]
                if not v and k != "assess_avoid":
                    continue
            else:
                v = "\n".join(v) if isinstance(v, list) else str(v).strip()
                if k == "department" and v not in formmap.DEPARTMENTS:
                    continue
                if k == "year" and v not in formmap.YEARS:
                    continue
                if k == "lab":
                    v = {"yes": "weekly", "no": "none"}.get(v.lower(), v.lower())
                    if v not in formmap.LAB:
                        continue
                if k == "credits":
                    try:
                        v = _num(float(v))
                    except ValueError:
                        continue
                    if v not in formmap.CREDITS:
                        continue
                if k in ("l", "t", "p"):
                    h = formmap._hours(v)
                    if h is None:
                        continue
                    v = _num(h)
                if k == "weeks" and not (v.isdigit() and 1 <= int(v) <= 16):
                    continue
                if k == "topics" and not formmap._lines(v):
                    continue
            srcs = [x for x in (source(s) for s in sug.sources) if x]
            fields[k] = {"value": v, "reason": sug.reason.strip()[:400], "sources": list({x["text"]: x for x in srcs}.values()), "corrected": None}
        DetailsFiller._regulation_fixes(fields, form)
        return fields

    @staticmethod
    def _regulation_fixes(fields: dict, form: dict) -> None:
        """Hours and weeks the AI suggested must match the regulations and the template; the professor's own values are
        never changed here (the design's regulation checks report those)."""
        facts = {f["id"]: f for f in regulations()["facts"]}

        def val(k):
            return fields[k]["value"] if k in fields else form.get(k)

        def fix(k, new, ref, why):
            if k in fields and str(fields[k]["value"]) != str(new):
                label = views.ref_label(ref) if ref.startswith("UGREG") else {"text": "IIIT-D course template", "url": None}
                fields[k].update(corrected=f"Set to {new} by {label['text']} (the AI suggested {fields[k]['value']}). {why}", value=str(new))
                if label not in fields[k]["sources"]:
                    fields[k]["sources"].append(label)

        credits = formmap._s(val("credits"))
        weeks = facts.get("UGREG-2025§2", {}).get("values", {}).get("teaching_weeks", 13)
        fix("weeks", weeks, "UGREG-2025§2", "A semester has 13 teaching weeks.")
        if credits == "4":
            fix("l", 3, "UGREG-2025§4(2)a", "A 4-credit course has 3 lecture hours a week.")
            fix("t", 1, "UGREG-2025§4(2)a", "A 4-credit course has 1 hour of interaction a week.")
        elif credits == "2":
            fix("l", 1.5, "UGREG-2025§4(2)b", "A 2-credit course has 1.5 lecture hours a week.")
        lab = formmap._s(val("lab"))
        if lab == "none":
            fix("p", 0, "UGREG-2025§4(2)a", "There is no lab.")
        elif lab == "weekly" and formmap._s(val("p")) in ("", "0"):
            fix("p", 2, "UGREG-2025§4(2)a", "A weekly lab is usually 2 hours.")
        if credits and "weekly_effort" in fields:
            ol = pedagogy()["outside_load"]
            lo, hi = _num(ol["per_credit_min"] * float(credits)), _num(ol["per_credit_max"] * float(credits))
            m = re.findall(r"\d+(?:\.\d+)?", fields["weekly_effort"]["value"])
            if not m or not all(float(lo) <= float(x) <= float(hi) for x in m):
                fix("weekly_effort", f"{lo}-{hi}", "template", f"The template recommends {lo}-{hi} hours a week for {credits} credits.")
