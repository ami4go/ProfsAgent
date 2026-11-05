"""Phase 2 deliverable B: work with the professor's own material for a lecture (the survey's `attach_material`).

    attach_material(run_id, lecture_id, options) -> manifest

The app (app/delivery.save_attachment) stores the files under delivery/attachments/<lecture>/ and the survey keeps
`attachments` (those paths and any links) and `attach_tasks` (slides, summary, quiz, gap_check, enrich).
1. read      every attachment as text: .pptx (slide text and notes), .pdf, .docx, .md / .txt, web links; one part each
             (P1, P2 …); a file that cannot be read is reported, never guessed
2. coverage  (no AI) each learning outcome against ~120-word passages of the material with the local embedding model:
             covered / partly / missing, with the closest passage (config/content.yaml `attach.coverage`)
3. B3        one AI call for summary, quiz, gap_check and enrich (only the tasks asked); the quiz is checked in code
             (3-5 distinct options, a valid answer, a known part) and the gap check is compared with step 2
4. slides    with the `slides` task, generate_material makes the deck from the material (it becomes sources P1…)
Output: material/<lecture>/attached.json and attached.md; for `slides` also the usual deck files.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Callable

import numpy as np

from profsagent.content.models import AttachedReport
from profsagent.delivery.brief import clean
from profsagent.delivery.common import RUNS, load_state, now, out_dir, read_json, write_json
from profsagent.llm.prompts import load_prompt
from profsagent.validate.record import ERR, WARN, errors, v

PID = "B3"
TASKS = ("slides", "summary", "quiz", "gap_check", "enrich")


# ------------------------------------------------------------------ 1. reading
def _pptx(p: Path) -> str:
    from pptx import Presentation
    out = []
    for i, s in enumerate(Presentation(str(p)).slides, 1):
        text = [sh.text_frame.text for sh in s.shapes if sh.has_text_frame and sh.text_frame.text.strip()]
        if s.has_notes_slide and s.notes_slide.notes_text_frame.text.strip():
            text.append("Notes: " + s.notes_slide.notes_text_frame.text)
        if text:
            out.append(f"(slide {i}) " + " | ".join(t.replace("\n", " / ") for t in text))
    return "\n".join(out)


def _pdf(p: Path) -> str:
    from pypdf import PdfReader
    return "\n".join(f"(page {i}) {pg.extract_text() or ''}" for i, pg in enumerate(PdfReader(str(p)).pages, 1))


def _docx(p: Path) -> str:
    import docx
    return "\n".join(par.text for par in docx.Document(str(p)).paragraphs if par.text.strip())


def _web(url: str) -> str:
    import httpx
    from bs4 import BeautifulSoup
    r = httpx.get(url, timeout=30, follow_redirects=True, headers={"User-Agent": "ProfsAgent/0.1 (course material reader)"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    for t in soup(["script", "style", "nav", "footer", "header"]):
        t.decompose()
    return soup.get_text("\n")


READERS = {".pptx": _pptx, ".pdf": _pdf, ".docx": _docx, ".md": lambda p: p.read_text(encoding="utf-8", errors="replace"),
           ".txt": lambda p: p.read_text(encoding="utf-8", errors="replace")}


def read_attachments(run_id: str, items: list[str]) -> list[dict]:
    """[{id P1…, name, kind, text, chars, error}] in the order given. Paths are relative to the course folder."""
    out = []
    for i, it in enumerate(items, 1):
        row = {"id": f"P{i}", "name": it.rsplit("/", 1)[-1] if not it.startswith("http") else it, "kind": "", "text": "", "error": ""}
        try:
            if it.startswith(("http://", "https://")):
                row["kind"], text = "link", _web(it)
            else:
                p = RUNS / run_id / it
                row["kind"] = p.suffix.lower().lstrip(".")
                reader = READERS.get(p.suffix.lower())
                if reader is None:
                    raise ValueError(f"cannot read {p.suffix or 'this'} files (pptx, pdf, docx, md, txt and links are read)")
                text = reader(p)
            row["text"] = re.sub(r"[ \t]+", " ", re.sub(r"\n\s*\n+", "\n", text)).strip()
            if not row["text"]:
                row["error"] = "no text found (a scanned PDF or images only?)"
        except Exception as e:  # noqa: BLE001 — reported to the professor, the other files still count
            row["error"] = f"{type(e).__name__}: {e}"[:200]
        row["chars"] = len(row["text"])
        out.append(row)
    return out


# ------------------------------------------------------------------ 2. coverage without AI
def passages(parts: list[dict], words: int = 120) -> list[tuple[str, str]]:
    out = []
    for p in parts:
        w = p["text"].split()
        for i in range(0, len(w), words):
            out.append((p["id"], " ".join(w[i:i + words])))
    return out


def coverage(los: list[dict], parts: list[dict], cfg: dict, embed=None) -> list[dict]:
    """Per learning outcome: the closest passage and covered / partly / missing by its similarity (a topical match)."""
    if embed is None:
        from profsagent.delivery.common import embed
    ps = passages(parts)
    th = cfg["attach"]["coverage"]
    if not ps or not los:
        return [{"lo_id": lo["id"], "status": "missing", "similarity": 0.0, "part": "", "passage": ""} for lo in los]
    P = embed([t for _, t in ps])
    L = embed([clean(lo["statement"]) for lo in los])
    S = L @ P.T
    out = []
    for lo, row in zip(los, S):
        j = int(np.argmax(row))
        s = float(row[j])
        out.append({"lo_id": lo["id"], "status": "covered" if s >= th["covered"] else "partly" if s >= th["partly"] else "missing",
                    "similarity": round(s, 3), "part": ps[j][0], "passage": ps[j][1][:300]})
    return out


# ------------------------------------------------------------------ 3. checks on the AI's answer
def check_report(rep: AttachedReport, los: set[str], part_ids: set[str], cover: list[dict], tasks: list[str]) -> list[dict]:
    """A-QUIZ (error) a question that cannot be used; A-REF (error) an unknown outcome or part; A-GAP (warning) the AI and
    the local model disagree strongly (the AI says covered, the material has nothing close); A-MISSING (warning) an
    outcome the gap check skipped."""
    out = []
    for i, q in enumerate(rep.quiz, 1):
        opts = [o.strip().lower() for o in q.options]
        if not 3 <= len(opts) <= 5 or len(set(opts)) != len(opts):
            out.append(v("A-QUIZ", ERR, [f"question {i}"], f"question {i} needs 3-5 distinct options, has {len(opts)}"))
        elif not 0 <= q.answer < len(opts):
            out.append(v("A-QUIZ", ERR, [f"question {i}"], f"question {i}: answer {q.answer} is not one of its options"))
        cited = set(re.findall(r"P\d+", q.source or ""))    # "P1", "[P1] slide 3, slide 5" …
        if q.source and not cited & part_ids:
            out.append(v("A-REF", ERR, [f"question {i}"], f"question {i} cites unknown part {q.source}"))
    if "gap_check" in tasks:
        seen = {g.lo_id for g in rep.gaps}
        for g in rep.gaps:
            if g.lo_id not in los:
                out.append(v("A-REF", ERR, [g.lo_id], f"the gap check names unknown outcome {g.lo_id}"))
        for lo in sorted(los - seen):
            out.append(v("A-MISSING", WARN, [lo], f"the gap check says nothing about {lo}"))
        local = {c["lo_id"]: c for c in cover}
        for g in rep.gaps:
            c = local.get(g.lo_id)
            if c and g.status == "covered" and c["status"] == "missing":
                out.append(v("A-GAP", WARN, [g.lo_id], f"{g.lo_id}: the AI says covered, but no passage of the material is close "
                                                       f"(best similarity {c['similarity']}); check it"))
    return out


def valid_quiz(rep: AttachedReport, found: list[dict]) -> list[dict]:
    bad = {int(x["nodes"][0].split()[-1]) for x in found if x["code"] == "A-QUIZ"}
    return [q.model_dump() for i, q in enumerate(rep.quiz, 1) if i not in bad]


# ------------------------------------------------------------------ outputs
def markdown(m: dict) -> str:
    r = m["report"]
    L = [f"# Your material for {m['lecture_id']}: {m['topic']}", "", f"*Read {len(m['parts'])} attachment(s); made {m['made_at'][:16]}*", ""]
    for p in m["parts"]:
        L.append(f"- [{p['id']}] {p['name']} ({p['kind']}, {p['chars']} characters)" + (f" — **not read:** {p['error']}" if p["error"] else ""))
    if r.get("summary"):
        L += ["", "## Summary", "", r["summary"], ""] + [f"- {k}" for k in r.get("key_points") or []]
    if m["gap_table"]:
        L += ["", "## Gap check (outcomes of this lecture)", "", "| Outcome | AI | Local model | What to add |", "|---|---|---|---|"]
        L += [f"| {g['lo_id']} | {g['ai']} | {g['local']} ({g['similarity']}) | {g['add']} |" for g in m["gap_table"]]
    if r.get("issues"):
        L += ["", "## Statements to check", ""] + [f"- {x}" for x in r["issues"]]
    if m["quiz"]:
        L += ["", "## Quiz", ""]
        for i, q in enumerate(m["quiz"], 1):
            L += [f"{i}. {q['question']}" + (f" *[{q['source']}]*" if q.get("source") else "")]
            L += [f"   - {'ABCDE'[k]}. {o}" for k, o in enumerate(q["options"])]
        L += ["", "### Answers", ""] + [f"{i}. {'ABCDE'[q['answer']]} — {q['explanation']}" for i, q in enumerate(m["quiz"], 1)]
    if r.get("enrich"):
        L += ["", "## Ideas to enrich it", ""] + [f"- **{e['kind'].replace('_', ' ')}** ({e['where']}): {e['add']}" for e in r["enrich"]]
    if m["findings"]:
        L += ["", "## Checks", ""] + [f"- {x['severity']} {x['code']}: {x['message']}" for x in m["findings"]]
    return "\n".join(L) + "\n"


def attach_material(run_id: str, lecture_id: str, options: dict | None = None, *, llm=None,
                    log: Callable[[str], None] = print) -> dict:
    """options: attachments (list; default the survey's), tasks (default the survey's attach_tasks), review ("ai", for
    the slides task). Returns the manifest written to material/<lecture>/attached.json."""
    from profsagent.content import generate as G
    from profsagent.delivery import survey as sv
    o, c = options or {}, G.cfg()
    st = load_state(run_id)
    unit = G.units(st, c).get(lecture_id)
    if unit is None:
        raise KeyError(f"no lecture {lecture_id} in runs/{run_id}")
    asked = sv.tasks(sv.load(run_id) or {})
    ids = [p["lecture_id"] for p in unit.get("parts") or []] or [lecture_id]          # a class: its topic lectures
    items = o.get("attachments") or [a for i in ids for a in (asked.get(i) or {}).get("attachments", [])]
    tasks = [t for t in (o.get("tasks") or sorted({t for i in ids for t in (asked.get(i) or {}).get("attach_tasks", [])})) if t in TASKS]
    if not items:
        raise ValueError(f"{lecture_id}: no attachments (the professor adds files or links in the survey)")
    tasks = tasks or ["summary", "quiz", "gap_check", "enrich"]
    log(f"B attached material {run_id} {lecture_id}: {len(items)} attachment(s), tasks {tasks}")
    parts = read_attachments(run_id, items)
    good = [p for p in parts if p["text"]]
    for p in parts:
        log(f"  [{p['id']}] {p['name']}: " + (f"{p['chars']} characters" if p["text"] else f"not read ({p['error']})"))
    if not good:
        raise ValueError(f"{lecture_id}: none of the attachments could be read")
    los = unit["learning_outcomes"]
    cover = coverage(los, good, c)
    m = {"lecture_id": lecture_id, "topic": unit["topic"], "made_at": now(), "tasks": tasks, "status": "draft",
         "parts": [{k: p[k] for k in ("id", "name", "kind", "chars", "error")} for p in parts], "coverage": cover,
         "report": {}, "quiz": [], "gap_table": [], "findings": [], "calls": []}
    text_tasks = [t for t in tasks if t != "slides"]
    if text_tasks:
        from profsagent.llm.client import LLMClient
        llm = llm or LLMClient(out_dir(run_id) / "material" / "llm_calls.jsonl")
        cap = c["attach"]["max_chars"]
        material = "\n\n".join(f"[{p['id']}] {p['name']}\n{p['text']}" for p in good)
        if len(material) > cap:
            material = material[:cap] + f"\n[… cut: {len(material) - cap} more characters not shown]"
        pr = load_prompt(PID)
        system, user = pr.render(course={"course_name": st["cco_compact"]["course_name"], "level": st.get("level")},
                                 lecture={"lecture_id": lecture_id, "topic": unit["topic"], "minutes": round(unit["hours"] * 60),
                                          "learning_outcomes": [{"id": x["id"], "statement": clean(x["statement"]),
                                                                 "bloom_level": x["bloom_level"]} for x in los]},
                                 coverage=[{k: x[k] for k in ("lo_id", "status", "part")} for x in cover],
                                 tasks=text_tasks, material=material)
        rep, rec = llm.structured(system=system, user=user, model_cls=AttachedReport, role=pr.meta.get("model_class", "generate"),
                                  temperature=float(pr.meta.get("temperature", 0.2)), prompt_id=PID, prompt_version=pr.version,
                                  run_id=run_id)
        log(f"  [{PID}] ok via {rec.endpoint} · {rec.prompt_tokens}+{rec.output_tokens} tok")
        m["calls"].append({"endpoint": rec.endpoint, "prompt_tokens": rec.prompt_tokens, "output_tokens": rec.output_tokens})
        found = check_report(rep, {x["id"] for x in los}, {p["id"] for p in good}, cover, text_tasks)
        local = {x["lo_id"]: x for x in cover}
        m.update(report=rep.model_dump(), quiz=valid_quiz(rep, found), findings=found,
                 gap_table=[{"lo_id": g.lo_id, "ai": g.status, "local": local.get(g.lo_id, {}).get("status", "?"),
                             "similarity": local.get(g.lo_id, {}).get("similarity", 0), "add": g.add} for g in rep.gaps])
        log(f"  checks: {len(errors(found))} errors, {len(found) - len(errors(found))} warnings; {len(m['quiz'])} usable questions")
    if "slides" in tasks:
        mat = {"text": "\n\n".join(f"[{p['id']}] {p['text']}" for p in good)[:c["attach"]["max_chars"]],
               "parts": [{"id": p["id"], "name": p["name"]} for p in good]}
        dm = G.generate_material(run_id, lecture_id, {"material": mat, "review": o.get("review"), "force": o.get("force")},
                                 log=log)
        m["slides"] = {k: dm[k] for k in ("files", "slides", "errors", "warnings", "status")}
    d = G.material_dir(run_id, lecture_id)
    write_json(d / "attached.json", m)
    (d / "attached.md").write_text(markdown(m), encoding="utf-8")
    log(f"  → {d / 'attached.md'}")
    return m
