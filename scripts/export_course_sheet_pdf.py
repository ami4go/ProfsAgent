"""Export a design run as a PDF laid out like the official IIIT-D CSE course description template.

  python scripts/export_course_sheet_pdf.py --run-id cs601-01

Writes runs/<run-id>/course_sheet.pdf from runs/<run-id>/state.json (no LLM). Sections follow
templates/iiitd_cse_course_template.xlsx (header, COs with BL levels, suggested topics with average load, labs,
assessment plan, resources, CO–PO/PSO mapping for the CSE programmes), plus the week-by-week schedule as an annex.
The content comes from render/course_template.py, the same data that fills runs/<run-id>/course_template.xlsx.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from reportlab.lib import colors  # noqa: E402
from reportlab.lib.enums import TA_CENTER  # noqa: E402
from reportlab.lib.pagesizes import A4, landscape  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import mm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402

from profsagent.config import programme  # noqa: E402
from profsagent.render.course_template import PROGRAMME_LABEL, pretty_assessment, template_data  # noqa: E402

FONT_DIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FONT_DIR / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_DIR / "arialbd.ttf")))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")

BODY = ParagraphStyle("body", fontName="Arial", fontSize=8.4, leading=10.8)
SMALL = ParagraphStyle("small", parent=BODY, fontSize=7.4, leading=9.2)
BOLD = ParagraphStyle("bold", parent=BODY, fontName="Arial-Bold")
HEAD = ParagraphStyle("head", parent=BODY, fontName="Arial-Bold", fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=3,
                      textColor=colors.HexColor("#1f3b57"))
TITLE = ParagraphStyle("title", parent=BODY, fontName="Arial-Bold", fontSize=13, leading=17, alignment=TA_CENTER)
NOTE = ParagraphStyle("note", parent=BODY, fontSize=7, leading=9, textColor=colors.HexColor("#666666"))
HEADER_BG = colors.HexColor("#dfe8f1")
GRID = colors.HexColor("#9aa9b8")


def P(text, style=BODY):
    text = str("" if text is None else text).replace("‑", "-").replace(" ", " ")
    return Paragraph(text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"), style)


TINY = ParagraphStyle("tiny", parent=BODY, fontSize=6.4, leading=7.8)


def mapping_cell(strength, explanation):
    """A CO–PO cell: the strength in bold with its explanation under it (the template's COk / COk-Explanation pair)."""
    esc = lambda s: str(s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")  # noqa: E731
    return Paragraph(f"<b>{esc(strength)}</b><br/><font size=6.4>{esc(explanation)}</font>" if explanation else f"<b>{esc(strength)}</b>", TINY)


def table(rows, widths, header=True, label_col=False):
    t = Table(rows, colWidths=widths, repeatRows=1 if header else 0)
    st = [("GRID", (0, 0), (-1, -1), 0.5, GRID), ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
          ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]
    if header:
        st.append(("BACKGROUND", (0, 0), (-1, 0), HEADER_BG))
    if label_col:
        st.append(("BACKGROUND", (0, 0), (0, -1), HEADER_BG))
    t.setStyle(TableStyle(st))
    return t


def build(run_id: str) -> Path:
    run = ROOT / "runs" / run_id
    st = json.loads((run / "state.json").read_text(encoding="utf-8"))
    td = template_data(st)
    W = A4[0] - 30 * mm
    story = [P("Course Description (IIIT-Delhi CSE course template)", TITLE), Spacer(1, 6)]

    story.append(table([[P(k, BOLD), P(v)] for k, v in td["header"]], [38 * mm, W - 38 * mm], header=False, label_col=True))

    story.append(P("Course Outcomes", HEAD))
    story.append(table([[P("CO #", BOLD), P("Outcome", BOLD), P("BL #", BOLD)]] +
                       [[P(c["id"], BOLD), P(c["statement"]), P(c["bl"])] for c in td["cos"]], [14 * mm, W - 30 * mm, 16 * mm]))
    high = sum(1 for c in td["cos"] if int(c["bl"][2:]) >= 4)
    story.append(P(f"{high} of {len(td['cos'])} COs target BL4–BL6 (template: at least half).", NOTE))
    story.append(Spacer(1, 4))
    story.append(table([[P("Approval Date", BOLD), P(td["approval_date"] or "(new course: left empty)")],
                        [P("Proposing Dept", BOLD), P(td["proposing_dept"])]], [38 * mm, W - 38 * mm], header=False, label_col=True))

    story.append(P("Suggested Topics", HEAD))
    rows = [[P("List Of Topics", BOLD), P("Relevant CO", BOLD), P("Assignment/lab/tutorial", BOLD), P("Average load (h/week)", BOLD)]]
    for t in td["topics"]:
        rows.append([P(t["title"]), P(t["cos"]), P(t["activities"], SMALL), P("" if t["load"] is None else f"{t['load']:g}")])
    story.append(table(rows, [W * 0.38, W * 0.12, W * 0.36, W * 0.14]))
    loads = [(t["load"]) for t in td["topics"] if t["load"] is not None]
    story.append(P("Average load = expected hours of weekly work outside lectures, including labs, tutorials, homework and "
                   "self-study (template: 10–12 h for a 4-credit course)." + (f" Mean over topics: {sum(loads) / len(loads):.1f} h." if loads else ""), NOTE))

    story.append(P("Suggested Plan of Labs", HEAD))
    if td["labs"]:
        rows = [[P("List of Lab Topics", BOLD), P("Relevant CO", BOLD), P("Hardware/software platform", BOLD)]]
        rows += [[P(x["title"]), P(x["cos"]), P(x["platform"])] for x in td["labs"]]
        story.append(table(rows, [W * 0.58, W * 0.12, W * 0.30]))
    else:
        story.append(P("Labs are not applicable to this course."))

    rows = [[P("Type of Evaluation", BOLD), P("% Contribution in Grade", BOLD)]]
    rows += [[P(a["type"]), P(f"{a['weight']:g}")] for a in td["assessment"]]
    rows.append([P("Total", BOLD), P(f"{sum(a['weight'] for a in td['assessment']):g}", BOLD)])
    story.append(KeepTogether([P("Suggested Assessment Plan", HEAD), table(rows, [W * 0.6, W * 0.4]),
                               P(f"Proctored evaluation: {td['proctored_pct']:g}% (template: at least 40%).", NOTE)]))

    rows = [[P("Name/Title", BOLD), P("Type", BOLD)]] + [[P(r["title"]), P(r["type"])] for r in td["resources"]]
    story.append(KeepTogether([P("Suggested Resources", HEAD), table(rows, [W - 34 * mm, 34 * mm])]))

    # CO -> programme outcome mapping (template block for CSExxx courses)
    story.append(PageBreak())
    story.append(P("CO mapping with the programmes offered by the CSE department", HEAD))
    story.append(P("Cell = mapping strength (1 low, 2 medium, 3 high) with its explanation, as in the template's CO / CO-Explanation columns.", NOTE))
    co_ids = [c["id"] for c in td["cos"]]
    for uid, label in [(u, PROGRAMME_LABEL[u]) for u in ("BTECH-COMMON", "BTECH-CSE", "BTECH-CSAI", "MTECH-CSE")]:
        pos = programme(uid)["po"]
        rows = [[P(label, BOLD), P("Program Outcome", BOLD)] + [P(c, BOLD) for c in co_ids]]
        for po in pos:
            cells = []
            for c in co_ids:
                hit = td["mapping"].get((c, po["id"]))
                cells.append(mapping_cell(hit[0], hit[1]) if hit else P(""))
            rows.append([P(po["label"], BOLD), P(po["text"], SMALL)] + cells)
        cw = min(26 * mm, (W - 22 * mm - 48 * mm) / max(len(co_ids), 1))
        story.append(table(rows, [22 * mm, W - 22 * mm - cw * len(co_ids)] + [cw] * len(co_ids)))
        story.append(Spacer(1, 8))

    # Annex: week-by-week schedule (not part of the template, kept for the professor's review)
    lo_parent = {lo["id"]: lo["parent_co"] for lo in st["los"]}
    tmap = {t["id"]: t for m in st["modules"] for t in m["topics"]}
    events = defaultdict(list)
    for c in st["assessment"]["components"]:
        for i in c["instances"]:
            name = pretty_assessment(i["id"])
            events[i["release_week"]].append(name if i["release_week"] == i["due_week"] else f"{name} released")
            if i["release_week"] != i["due_week"]:
                events[i["due_week"]].append(f"{name} due")
    story.append(P("Annex: week-by-week schedule", HEAD))
    rows = [[P("Week", BOLD), P("Lecture topics", BOLD), P("COs", BOLD), P("Assessments", BOLD)]]
    for w in st["schedule"]["weeks"]:
        tids = list(dict.fromkeys(it["topic_id"] for it in w["items"]))
        cos = sorted({lo_parent.get(lo, "") for t in tids for lo in tmap.get(t, {}).get("serves_los", [])} - {""})
        rows.append([P(w["week"]), P("\n".join(f"• {tmap[t]['title']}" for t in tids if t in tmap) or "Project work and review"),
                     P(", ".join(cos)), P("\n".join(events[w["week"]]))])
    story.append(table(rows, [12 * mm, W * 0.55, 18 * mm, W - 12 * mm - W * 0.55 - 18 * mm]))
    story += [Spacer(1, 10), P(f"Draft generated by ProfsAgent from design run {run_id}. Not an approved IIIT-Delhi course record.",
                                ParagraphStyle("c", parent=NOTE, alignment=TA_CENTER))]
    out = run / "course_sheet.pdf"
    SimpleDocTemplate(str(out), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=14 * mm, bottomMargin=14 * mm,
                      title=f"{st['cco_compact']['course_name']} — Course Description", author="ProfsAgent (draft)").build(story)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    print(build(ap.parse_args().run_id))
