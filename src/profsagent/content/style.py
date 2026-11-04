"""The professor's own style for generated slides ("style transfer"), learned from one or more of their decks.

    learn_style(run_id, pptx_paths) -> profile        python scripts/run_content.py style --run-id <id> --from a.pptx[,b.pptx]
    load_style(run_id) -> profile | None

Two parts, both without AI calls:
- look: their first deck becomes the template (delivery/style/template.pptx: its masters, background and logo stay;
  its slides are removed when a deck is rendered on it); the theme's colours and fonts replace config/content.yaml
  `render` (ink from dk1, accent from accent1, a pale accent for panels; the body font for text).
- writing: measured on their slides: bullets per slide, words per bullet, how titles are capitalised, "we" or "you",
  and up to 6 of their bullets as examples of tone. B1 gets it as `lecture.style`.
Saved as delivery/style/profile.json; every deck of the run uses it from then on.
"""
from __future__ import annotations

import re
import shutil
import statistics
from pathlib import Path

from lxml import etree

from profsagent.delivery.common import out_dir, read_json, write_json

NS = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}
RT_THEME = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/theme"


def style_dir(run_id: str) -> Path:
    return out_dir(run_id) / "style"


def theme(prs) -> dict:
    """Colours (hex) and fonts of the deck's first master theme: {colors: {dk1, lt1, accent1…}, fonts: {major, minor}}."""
    part = prs.slide_masters[0].part.part_related_by(RT_THEME)
    root = etree.fromstring(part.blob)
    colors = {}
    for el in root.find(".//a:clrScheme", NS) or []:
        name = etree.QName(el).localname
        srgb, sys_ = el.find("a:srgbClr", NS), el.find("a:sysClr", NS)
        val = srgb.get("val") if srgb is not None else (sys_.get("lastClr") if sys_ is not None else None)
        if val:
            colors[name] = val.upper()
    fonts = {}
    for kind in ("major", "minor"):
        f = root.find(f".//a:{kind}Font/a:latin", NS)
        if f is not None and f.get("typeface"):
            fonts[kind] = f.get("typeface")
    return {"colors": colors, "fonts": fonts}


def _tint(hex_: str, share: float) -> str:
    """The colour mixed with white (share 0..1 of white): a pale version for panels and badges."""
    r, g, b = (int(hex_[i:i + 2], 16) for i in (0, 2, 4))
    return "".join(f"{round(c + (255 - c) * share):02X}" for c in (r, g, b))


def _luma(hex_: str) -> float:
    r, g, b = (int(hex_[i:i + 2], 16) for i in (0, 2, 4))
    return 0.299 * r + 0.587 * g + 0.114 * b


def writing(prs_list) -> dict:
    """How the professor writes slides, measured on every slide with a title and bullet-like lines."""
    titles, per_slide, words, bullets = [], [], [], []
    for prs in prs_list:
        for s in prs.slides:
            title = s.shapes.title.text_frame.text.strip() if s.shapes.title is not None and s.shapes.title.has_text_frame else ""
            lines = [p.text.strip() for sh in s.shapes if sh.has_text_frame and sh != s.shapes.title
                     for p in sh.text_frame.paragraphs if len(p.text.strip().split()) >= 2]
            if title:
                titles.append(title)
            if lines:
                per_slide.append(len(lines))
                words += [len(x.split()) for x in lines]
                bullets += lines
    def title_case(t: str) -> bool:
        ws = [w for w in re.findall(r"[A-Za-z][A-Za-z'-]*", t) if len(w) > 3]
        return bool(ws) and sum(w[0].isupper() for w in ws[1:]) >= max(1, len(ws[1:]) * 0.6)
    text = " ".join(bullets).lower()
    we, you = len(re.findall(r"\bwe\b|\bour\b|\blet's\b", text)), len(re.findall(r"\byou\b|\byour\b", text))
    pick = sorted({b for b in bullets if 5 <= len(b.split()) <= 25}, key=len)
    return {"slides_measured": len(per_slide),
            "bullets_per_slide": round(statistics.median(per_slide)) if per_slide else None,
            "words_per_bullet": round(statistics.median(words)) if words else None,
            "title_case": ("Title Case" if sum(map(title_case, titles)) > len(titles) / 2 else "Sentence case") if titles else None,
            "voice": "we" if we > you * 1.5 else "you" if you > we * 1.5 else "mixed" if we + you else "impersonal",
            "questions_in_titles": round(sum(t.endswith("?") for t in titles) / len(titles), 2) if titles else 0,
            "examples": pick[:: max(1, len(pick) // 6)][:6]}


def learn_style(run_id: str, paths: list[Path]) -> dict:
    from pptx import Presentation
    if not paths:
        raise ValueError("give at least one .pptx of the professor's")
    decks = [Presentation(str(p)) for p in paths]
    th = theme(decks[0])
    d = style_dir(run_id)
    d.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(paths[0], d / "template.pptx")
    col = th["colors"]
    ink = next((col[k] for k in ("dk1", "dk2") if k in col and _luma(col[k]) < 110), None)
    accent = next((col[k] for k in ("accent1", "accent2", "accent5") if k in col and 40 < _luma(col[k]) < 200), None)
    look = {"template": "template.pptx",
            "width_in": round(decks[0].slide_width / 914400, 3), "height_in": round(decks[0].slide_height / 914400, 3),
            "colors": {k: v for k, v in {"ink": ink, "accent": accent, "accent_soft": _tint(accent, 0.82) if accent else None,
                                         "muted": _tint(ink, 0.45) if ink else None}.items() if v},
            "font": th["fonts"].get("minor"), "title_font": th["fonts"].get("major"), "theme": th}
    prof = {"from": [str(p) for p in paths], "look": look, "writing": writing(decks)}
    write_json(d / "profile.json", prof)
    return prof


def load_style(run_id: str) -> dict | None:
    p = style_dir(run_id) / "profile.json"
    prof = read_json(p) if p.exists() else None
    if prof and prof["look"].get("template"):
        prof["look"]["template_path"] = str(style_dir(run_id) / prof["look"]["template"])
    return prof


def apply_look(cfg: dict, prof: dict | None) -> dict:
    """config/content.yaml `render` with the professor's look; unchanged without a profile."""
    if not prof:
        return cfg
    lk = prof["look"]
    r = {**cfg["render"], "colors": {**cfg["render"]["colors"], **lk.get("colors", {})}}
    for k in ("width_in", "height_in"):
        if lk.get(k):
            r[k] = lk[k]
    if lk.get("font"):
        r["font"] = lk["font"]
    if lk.get("template_path") and Path(lk["template_path"]).exists():
        r["template"] = lk["template_path"]
    return {**cfg, "render": r}


def for_b1(prof: dict | None) -> dict | None:
    """The writing part as B1 sees it (`lecture.style`)."""
    if not prof or not prof["writing"].get("slides_measured"):
        return None
    w = prof["writing"]
    return {k: w[k] for k in ("bullets_per_slide", "words_per_bullet", "title_case", "voice", "examples")}
