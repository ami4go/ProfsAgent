"""Export a design run as a PDF in the IIIT-D course-directory sheet format (only the directory's fields).

  python scripts/export_course_sheet_pdf.py --run-id cs601-01

Writes runs/<run-id>/course_sheet.pdf. Content comes from runs/<run-id>/state.json (no LLM).
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("Arial", str(FONT_DIR / "arial.ttf")))
pdfmetrics.registerFont(TTFont("Arial-Bold", str(FONT_DIR / "arialbd.ttf")))
pdfmetrics.registerFontFamily("Arial", normal="Arial", bold="Arial-Bold")

BODY = ParagraphStyle("body", fontName="Arial", fontSize=8.6, leading=11)
BOLD = ParagraphStyle("bold", parent=BODY, fontName="Arial-Bold")
HEAD = ParagraphStyle("head", parent=BODY, fontName="Arial-Bold", fontSize=10.5, leading=14, spaceBefore=8, spaceAfter=3,
                      textColor=colors.HexColor("#1f3b57"))
TITLE = ParagraphStyle("title", parent=BODY, fontName="Arial-Bold", fontSize=13, leading=17, alignment=TA_CENTER)
NOTE = ParagraphStyle("note", parent=BODY, fontSize=7, leading=9, textColor=colors.HexColor("#666666"), alignment=TA_CENTER)
HEADER_BG = colors.HexColor("#dfe8f1")
GRID = colors.HexColor("#9aa9b8")


def P(text, style=BODY):
    text = str(text or "").replace("‑", "-").replace(" ", " ")   # non-breaking hyphen/space: not in Arial
    return Paragraph(text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br/>"), style)


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


def pretty_assessment(iid: str) -> str:
    s = iid.split(":", 1)[-1]
    s = re.sub(r"^ProjMilestone", "Project Milestone ", s)
    s = re.sub(r"^ProjFinal", "Project (final)", s)
    s = re.sub(r"^Proj(?!ect)", "Project ", s)
    s = s.replace("Midsem", "Mid-sem exam").replace("Endsem", "End-sem exam")
    s = re.sub(r"(?<=[a-z])(?=\d)", " ", s)
    return re.sub(r"\s+", " ", s).strip()


TYPE_LABEL = {"quiz": "Quiz", "assignment": "Assignment", "midsem": "Mid-sem", "endsem": "End-sem", "project": "Project",
              "report": "Report", "lab": "Lab", "presentation": "Presentation", "participation": "Participation"}


def build(run_id: str) -> Path:
    run = ROOT / "runs" / run_id
    st = json.loads((run / "state.json").read_text(encoding="utf-8"))
    cc, f = st["cco_compact"], st["cco"]["fields"]
    lo_parent = {lo["id"]: lo["parent_co"] for lo in st["los"]}
    tmap = {t["id"]: t for m in st["modules"] for t in m["topics"]}
    W = A4[0] - 30 * mm
    story = [P("Course Proposal", TITLE), Spacer(1, 6)]

    years = cc["target_students"].get("years") or []
    offered = "UG" + (f" (B.Tech. CSE, year {'/'.join(map(str, years))})" if years else "")
    code = f["level_or_code"].get("code") or f"To be assigned ({st['level']}xx level)"
    header = [[P("Course Code", BOLD), P(code)], [P("Department", BOLD), P("CSE")], [P("Course Name", BOLD), P(cc["course_name"])],
              [P("Credits", BOLD), P(st["defaults"]["credits"])], [P("Course Offered to", BOLD), P(offered)],
              [P("Course Description", BOLD), P(st.get("narrative", {}).get("course_description", ""))]]
    story.append(table(header, [38 * mm, W - 38 * mm], header=False, label_col=True))

    # Pre-requisites
    story.append(P("Pre-requisites", HEAD))
    pre = defaultdict(list)
    for p in st["positioning"].get("prerequisites", []):
        alts = [a for a in p.get("alternatives", []) if a != p["course_uid"]]
        pre[p["kind"]].append(p["course_uid"] + (f" (or {', '.join(alts)})" if alts else ""))
    story.append(table([[P("Pre-requisite (Mandatory)", BOLD), P("Pre-requisite (Desirable)", BOLD), P("Pre-requisite (Other)", BOLD)],
                        [P(", ".join(pre["mandatory"]) or "None"), P(", ".join(pre["desirable"]) or "None"), P("None")]], [W / 3] * 3))

    # Post Conditions (COs)
    story.append(P("Post Conditions (Course Outcomes)", HEAD))
    story.append(table([[P("CO", BOLD), P("Students will be able to…", BOLD)]] + [[P(c["id"], BOLD), P(c["statement"])] for c in st["cos"]],
                       [16 * mm, W - 16 * mm]))

    # Weekly Lecture Plan
    story.append(P("Weekly Lecture Plan", HEAD))
    tut = defaultdict(list)
    for s in st.get("labs_tutorials", {}).get("tutorials", []):
        tut[s["week"]].append(s["activity"])
    events = defaultdict(list)
    for c in st["assessment"]["components"]:
        for i in c["instances"]:
            name = pretty_assessment(i["id"])
            if i["release_week"] == i["due_week"]:
                events[i["release_week"]].append(name)
            else:
                events[i["release_week"]].append(f"{name} released")
                events[i["due_week"]].append(f"{name} due")
    rows = [[Paragraph("Week<br/>Number", BOLD), P("Lecture Topic", BOLD), P("COs Met", BOLD), P("Tutorial", BOLD), P("Assignments / Project", BOLD)]]
    for w in st["schedule"]["weeks"]:
        tids = list(dict.fromkeys(it["topic_id"] for it in w["items"]))
        topics = [tmap[t]["title"] for t in tids if t in tmap]
        cos = sorted({lo_parent.get(lo, "") for t in tids for lo in tmap.get(t, {}).get("serves_los", [])} - {""})
        wk = w["week"]
        ev = events[wk][:]
        if wk == st["midsem_after_week"] and not any("Mid-sem" in e for e in ev):
            ev.append("Mid-sem exam (after this week)")
        rows.append([P(wk), P("\n".join(f"• {t}" for t in topics) or ("Project work and review" if ev else "—")), P(", ".join(cos)),
                     P("; ".join(tut[wk])), P("\n".join(ev))])
    story.append(table(rows, [17 * mm, 55 * mm, 18 * mm, (W - 90 * mm) * 0.58, (W - 90 * mm) * 0.42]))

    # Weekly Lab Plan
    labs = st.get("labs_tutorials", {}).get("labs", [])
    story.append(P("Weekly Lab Plan", HEAD))
    if labs:
        rows = [[Paragraph("Week<br/>Number", BOLD), P("Laboratory Exercise", BOLD), P("COs Met", BOLD), P("Platform (Hardware / Software)", BOLD)]]
        for s in sorted(labs, key=lambda x: x["week"]):
            cos = sorted({lo_parent.get(x, "") for x in s["practises_los"]} - {""})
            ex = (s.get("title") + ": " if s.get("title") else "") + s["exercise"]
            rows.append([P(s["week"]), P(ex), P(", ".join(cos)), P(", ".join(s.get("tools", [])))])
        story.append(table(rows, [17 * mm, W - 17 * mm - 18 * mm - 48 * mm, 18 * mm, 48 * mm]))
    else:
        story.append(P("Course does not have a lab component."))

    # Assessment Plan
    story.append(P("Assessment Plan", HEAD))
    rows = [[P("Type of Evaluation", BOLD), P("% Contribution in Grade", BOLD)]]
    for c in st["assessment"]["components"]:
        n = len(c["instances"])
        label = TYPE_LABEL.get(c["type"].lower(), c["type"].title())
        if n > 1:
            label += f" ({n}" + (f", best {c['best_k']}" if c.get("best_k") else "") + ")"
        rows.append([P(label), P(f"{c['weight_pct']:g}")])
    rows.append([P("Total", BOLD), P(f"{sum(c['weight_pct'] for c in st['assessment']['components']):g}", BOLD)])
    story.append(KeepTogether(table(rows, [W * 0.6, W * 0.4])))

    # Resource Material
    story.append(P("Resource Material", HEAD))
    role = {"primary": "Textbook", "reference": "Reference", "reading": "Reference (reading)"}
    rows = [[P("Type", BOLD), P("Title", BOLD)]]
    for r in st.get("resources", []):
        ident = r["identifier"].get("doi") and f"DOI: {r['identifier']['doi']}" or r["identifier"].get("isbn") and f"ISBN: {r['identifier']['isbn']}" or ""
        rows.append([P(role.get(r["role"], r["role"].title())),
                     P(f"{', '.join(r['authors'])} ({r.get('year')}). {r['title']}." + (f" {ident}" if ident else ""))])
    story.append(KeepTogether(table(rows, [34 * mm, W - 34 * mm])))

    story += [Spacer(1, 10), P(f"Draft generated by ProfsAgent from design run {run_id}. Not an approved IIIT-Delhi course record.", NOTE)]
    out = run / "course_sheet.pdf"
    SimpleDocTemplate(str(out), pagesize=A4, leftMargin=15 * mm, rightMargin=15 * mm, topMargin=14 * mm, bottomMargin=14 * mm,
                      title=f"{cc['course_name']} — Course Proposal", author="ProfsAgent (draft)").build(story)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", required=True)
    print(build(ap.parse_args().run_id))
