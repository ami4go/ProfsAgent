"""The violation record shared by every check module (rules, regulation, constraints). NO LLM in this module.

    {code, severity: error|warning, nodes: [ids], message, evidence[, fix_hint]}
rules.run adds `stage`; validate/engine.py adds the record v2 fields (family, fixable_by).
"""
from __future__ import annotations

ERR, WARN = "error", "warning"


FIX_HINTS = {
    "VLO-COPY": "Keep the same verb and Bloom level, but rewrite the LO as ONE concrete task: a narrower object (one component, "
                "one subsystem, one supplied artefact), a specific given input as the condition, and a degree checkable by a single "
                "assessment task. Do not change the statement's first word away from the declared verb.",
    "VLO-DUP": "Make the two LOs name different skills or objects; merge them if they really are one step.",
    "V10": "The statement must START with the declared verb (same word). If you change the verb, update `verb` and `bloom_level` together.",
    "V11": "Add a checkable degree (number, threshold, or explicit criterion) and a condition (given X / using Y) inside the statement text.",
    "V12": "Replace the banned verb with an observable verb from the lexicon at the intended level.",
    "T2": "Add or re-level an LO so that at least one LO of this CO is at exactly the CO's Bloom level.",
    "V19": "Move the instance to a later release week, or remove the not-yet-taught topics/LOs from what it covers.",
    "V20": "Bring the weight inside the band, or add a weight_justification tied to the course intent.",
    "VA-ORDER": "List instances chronologically: each later instance must have release and due weeks ≥ the previous one.",
    "VT-SIZE": "Split the topic into 2–3 topics of ≤ 2 h each, distributing its LOs.",
    "V21": "Adjust topic hours so the total is 85–100% of the lecture budget.",
    "VCO-BL": "Raise at least half of the COs to BL4 (Analyzing), BL5 (Evaluating) or BL6 (Creating): change the verb to one from that "
              "level of the IIIT-D taxonomy and make the task genuinely analytical, evaluative or creative; update verb and bloom_level together.",
    "T4": "Map the CO to at least one outcome of EVERY listed programme (B.Tech common POs, B.Tech CSE PSOs, B.Tech CSAI PSOs, "
          "M.Tech CSE POs/PSOs), each with a one-line explanation; keep only links the course actually develops.",
    "VA-PROCTOR": "Make proctored evaluation (mid-sem, end-sem, in-class quizzes or other invigilated tests) at least 40% of the grade, "
                  "taking weight from take-home components; keep the total at 100.",
    "VT-LOAD": "Give every topic an outside_load_hours value so the hours-weighted average is within the recommended weekly range.",
    "VTG-TAUGHT": "Add a topic that teaches this topic group (with covers_topic_groups), or propose dropping the group upstream.",
    "VT-ORDER": "Add the prerequisite to the dependent topic's `requires`, or move the dependent topic later in its module order, so "
                "it is taught after what it builds on.",
    "VT-LEN": "Rewrite the statement as one outcome of typical length: verb, object, condition and degree, without lists or padding.",
    "VS-LOCOPY": "Keep the verb and Bloom level, but narrow the LO to one concrete task: one component or artefact, a specific "
                 "given input as the condition, and a degree one assessment task can check.",
    "VS-LOFIT": "Move the LO under the CO it serves, or rewrite it so it is a step towards its own parent CO.",
    "VS-CODUP": "Merge the two COs, or make them name different capabilities.",
    "VKG-PREC": "Check the order: move the later topic before the other, or keep it and note why this course differs from IIIT-D practice.",
    "VKG-DUP": "Declare the course as an anti-requisite, or change the topics so the new course is distinct from it.",
    "VKG-NORM": "Confirm the value is intended for this level, or bring it closer to what same-level IIIT-D courses use.",
}


def v(code, sev, nodes, msg, **ev):
    d = {"code": code, "severity": sev, "nodes": list(nodes), "message": msg, "evidence": ev}
    if code in FIX_HINTS:
        d["fix_hint"] = FIX_HINTS[code]
    return d


def errors(vs: list[dict]) -> list[dict]:
    return [x for x in vs if x["severity"] == ERR]
