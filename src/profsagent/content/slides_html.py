"""Deliverable B: the lecture deck as HTML slides with typeset maths, measured in a real browser.

    deck_html(deck, frame, sources, cfg) -> html       slides.html: 16:9 slides (1280 x 720 px), one file, works offline
    measure(path, cfg, pdf=None, shots=None) -> dict   opens slides.html in Chrome (Playwright): fits each slide, finds
                                                       maths errors, prints slides.pdf, cuts slide bodies for the .pptx
    layout_findings(report) -> findings                D-OVERFLOW (measured) and D-MATH, for the checks and repair loop

Maths: bullets, block text and quiz text carry inline maths as \\( ... \\); `math` and `steps` blocks are display
formulas. KaTeX (content/assets/katex, MIT) is inlined into the page, fonts included, only when the deck has maths.

Fitting: python-pptx can only estimate text size (render.fit); here the browser measures it. A slide whose body does
not fit is shrunk in 5% steps down to `html.min_scale`; what still does not fit is a D-OVERFLOW error, so B1 is asked
to shorten or split that slide. A formula KaTeX cannot parse is a D-MATH error, with KaTeX's message.

The slides come in the .pptx's order (title, objectives, content slides from FIRST_CONTENT_SLIDE, references), so slide
numbers in findings, the .pptx and the PDF agree.
"""
from __future__ import annotations

import base64
import html
import math
import re
from functools import lru_cache
from pathlib import Path

from profsagent.content.models import FIRST_CONTENT_SLIDE, Block, Figure, LectureDeck, Plot, Quiz, Slide
from profsagent.validate.record import ERR, v

ASSETS = Path(__file__).resolve().parent / "assets" / "katex"
MATH = re.compile(r"\\\(|\\\[|\$\$")          # inline \( \), display \[ \] or $$ $$ in plain text
BADGE = {"example": "Example", "worked_problem": "Worked problem", "activity": "Activity", "check": "Check",
         "summary": "Summary", "recap": "Recap", "watch": "Watch", "debrief": "Debrief", "bridge": "Bridge",
         "simulation": "Try it", "quiz": "Review quiz", "answer": "Answer"}
PANEL = {"watch": "WATCH", "simulation": "OPEN"}
DEFAULT_COL = {"ink": "#1F2937", "muted": "#6B7280", "accent": "#0F766E"}       # config/content.yaml render.colors


def esc(s: str) -> str:
    """Slide text as HTML: escaped, with **bold** (models write Markdown emphasis) shown as bold."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(s or "", quote=False))


# ------------------------------------------------------------------ maths
def slide_text(s: Slide) -> list[str]:
    """Every piece of plain text on a slide that may hold inline maths."""
    q = s.quiz
    return [s.title, *s.bullets, *(b.text for b in s.blocks), *(b.term for b in s.blocks),
            *([q.question, *q.options] if q else [])]


def has_math(s: Slide) -> bool:
    return any(b.kind in ("math", "steps") for b in s.blocks) or any(MATH.search(t or "") for t in slide_text(s))


@lru_cache(maxsize=1)
def katex_assets() -> str:
    """KaTeX's CSS (fonts as data URIs, woff2 only) and scripts, ready to inline in a page."""
    css = (ASSETS / "katex.min.css").read_text(encoding="utf-8")
    css = re.sub(r',\s*url\(fonts/[^)]+\.(?:woff|ttf)\) format\("(?:woff|truetype)"\)', "", css)

    def font(m: re.Match) -> str:
        data = base64.b64encode((ASSETS / "fonts" / m.group(1)).read_bytes()).decode()
        return f"url(data:font/woff2;base64,{data})"
    css = re.sub(r"url\(fonts/([^)]+\.woff2)\)", font, css)
    js = "\n".join((ASSETS / f).read_text(encoding="utf-8").replace("</script", "<\\/script")
                   for f in ("katex.min.js", "auto-render.min.js"))
    return f"<style>{css}</style><script>{js}</script>"


# per slide, so a formula KaTeX cannot parse (auto-render then leaves its source as text) is reported on its slide
RENDER_MATH = ("document.querySelectorAll('.slide').forEach(s=>{s.__errs=[];renderMathInElement(s,{delimiters:["
               "{left:'$$',right:'$$',display:true},{left:'\\\\[',right:'\\\\]',display:true},"
               "{left:'\\\\(',right:'\\\\)',display:false}],ignoredTags:['script','noscript','style','textarea','pre','code'],"
               "throwOnError:false,errorCallback:(m,e)=>s.__errs.push({tex:m.slice(0,160),"
               "message:String(e&&e.message||e).slice(0,200)})})});")


# ------------------------------------------------------------------ pieces
def block_html(b: Block) -> str:
    if b.kind == "math":
        return f'<div class="dm">\\[{esc(b.latex)}\\]</div>'
    if b.kind == "steps":
        rows = "".join(f'<div class="st"><span class="n">{i}</span><span class="f">\\[{esc(s.latex)}\\]</span>'
                       f'<span class="why">{esc(s.why)}</span></div>' for i, s in enumerate(b.steps, 1))
        return f'<div class="steps">{rows}</div>'
    if b.kind == "definition":
        return f'<div class="def"><b>{esc(b.term)}</b><span>{esc(b.text)}</span></div>'
    if b.kind == "think":
        return f'<div class="think"><b>Think:</b> {esc(b.text)}</div>'
    return f'<div class="note">{esc(b.text)}</div>'


def needs_picture(s: Slide) -> bool:
    """A slide the .pptx shows as its browser-drawn body: typeset maths or a plot."""
    return has_math(s) or s.figure.kind == "plot"


def plot_problems(p: Plot | None, values: dict) -> list[str]:
    """Why a plot cannot be drawn from the values (empty when it can)."""
    if p is None or not p.series:
        return ["a plot needs at least one series"]
    out = []
    for k, sr in enumerate(p.series, 1):
        names = [sr.x, sr.y] + ([sr.y2] if sr.kind == "segments" else [])
        miss = [nm for nm in names if not isinstance(values.get(nm), list) or not values[nm]
                or isinstance(values[nm][0], list) or isinstance(values[nm][0], str)]
        if miss:
            out.append(f"series {k} ({sr.kind}): {', '.join(miss)} is not a list of numbers the example computed")
        elif len({len(values[nm]) for nm in names}) != 1:
            out.append(f"series {k} ({sr.kind}): {' / '.join(names)} have different lengths")
        elif p.log_y and any(y <= 0 for nm in names[1:] for y in values[nm]):
            out.append(f"series {k}: a log scale needs positive y values")
    return out


def ticks(lo: float, hi: float, n: int = 5) -> list[float]:
    """About n round tick values covering [lo, hi]."""
    if hi <= lo:
        hi = lo + 1
    raw = (hi - lo) / n
    mag = 10 ** math.floor(math.log10(raw))
    step = next(m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= raw)
    a, b = math.floor(lo / step + 1e-9), math.ceil(hi / step - 1e-9)       # the ticks cover [lo, hi] fully
    return [round(k * step, 10) for k in range(a, b + 1)]


def padded(lo: float, hi: float, share: float) -> tuple[float, float]:
    """[lo, hi] widened by `share` of its span, without crossing 0 when the data do not."""
    pad = (hi - lo) * share or 0.5
    return (lo - pad if lo - pad >= 0 or lo < 0 else 0.0), hi + pad


def tick_label(t: float) -> str:
    return str(int(t)) if float(t).is_integer() else f"{t:g}"


def log_label(e: float) -> str:
    """A decade on a log axis: 0.01 … 1000 written out, beyond that 10 with a superscript exponent."""
    if -2 <= e <= 3:
        return tick_label(10 ** e)
    return f'10<tspan dy="-7" font-size="10">{int(e)}</tspan>'


def plot_svg(p: Plot, values: dict, col: dict) -> str:
    """An SVG plot of the example's values: axes with round ticks, then the series in order, legend below."""
    W, H, L, R, T, B = 560, 360, 58, 14, 12, 46
    xs = [x for sr in p.series for x in values[sr.x]]
    ys = [y for sr in p.series for nm in ([sr.y] + ([sr.y2] if sr.kind == "segments" else [])) for y in values[nm]]
    if any(sr.kind == "bars" for sr in p.series) and not p.log_y:
        ys.append(0)
    fy = (lambda v: math.log10(v)) if p.log_y else (lambda v: v)
    xt = ticks(*padded(min(xs), max(xs), 0.04))
    if p.log_y:
        e0, e1 = math.floor(fy(min(ys))), math.ceil(fy(max(ys)))
        every = max(1, math.ceil((e1 - e0) / 6))                       # at most ~7 decade labels
        e1 = e0 + math.ceil((e1 - e0) / every) * every
        yt = [float(e) for e in range(e0, max(e1, e0 + 1) + 1, every)]
    else:
        yt = ticks(*padded(min(ys), max(ys), 0.06))
    X = lambda v: L + (v - xt[0]) / (xt[-1] - xt[0]) * (W - L - R)              # noqa: E731
    Y = lambda v: H - B - (fy(v) - yt[0]) / (yt[-1] - yt[0]) * (H - T - B)      # noqa: E731
    palette = {"points": [col["ink"], "#6366f1", "#d97706"], "line": [col["accent"], "#d97706", "#6366f1", col["muted"]],
               "bars": [col["accent"], "#d97706", "#6366f1"], "segments": ["#c2410c", "#6366f1"]}
    used: dict[str, int] = {}
    s = [f'<svg class="plot" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="inherit">']
    for t in yt:
        yy = H - B - (t - yt[0]) / (yt[-1] - yt[0]) * (H - T - B)
        s.append(f'<line x1="{L}" y1="{yy:.1f}" x2="{W - R}" y2="{yy:.1f}" stroke="#e5e7eb"/>'
                 f'<text x="{L - 8}" y="{yy + 5:.1f}" text-anchor="end" font-size="14" fill="{col["muted"]}">'
                 f'{log_label(t) if p.log_y else tick_label(t)}</text>')
    for t in xt:
        s.append(f'<text x="{X(t):.1f}" y="{H - B + 20}" text-anchor="middle" font-size="14" fill="{col["muted"]}">{tick_label(t)}</text>')
    s.append(f'<line x1="{L}" y1="{H - B}" x2="{W - R}" y2="{H - B}" stroke="{col["ink"]}" stroke-width="1.5"/>'
             f'<line x1="{L}" y1="{T}" x2="{L}" y2="{H - B}" stroke="{col["ink"]}" stroke-width="1.5"/>')
    if p.x_label:
        s.append(f'<text x="{(L + W - R) / 2}" y="{H - 6}" text-anchor="middle" font-size="15" fill="{col["ink"]}">{esc(p.x_label)}</text>')
    if p.y_label:
        s.append(f'<text x="16" y="{(T + H - B) / 2}" text-anchor="middle" font-size="15" fill="{col["ink"]}" '
                 f'transform="rotate(-90 16 {(T + H - B) / 2})">{esc(p.y_label)}</text>')
    legend = []
    for sr in p.series:
        c = palette[sr.kind][used.get(sr.kind, 0) % len(palette[sr.kind])]
        used[sr.kind] = used.get(sr.kind, 0) + 1
        xv, yv = values[sr.x], values[sr.y]
        if sr.kind == "points":
            s += [f'<circle cx="{X(a):.1f}" cy="{Y(b):.1f}" r="6" fill="{c}"/>' for a, b in zip(xv, yv)]
        elif sr.kind == "line":
            pts = " ".join(f"{X(a):.1f},{Y(b):.1f}" for a, b in sorted(zip(xv, yv)))
            s.append(f'<polyline points="{pts}" fill="none" stroke="{c}" stroke-width="3"/>')
        elif sr.kind == "bars":
            bw = max(4.0, (W - L - R) / max(len(xv), 1) * 0.6)
            base = Y(10 ** yt[0]) if p.log_y else Y(max(0, yt[0]))
            s += [f'<rect x="{X(a) - bw / 2:.1f}" y="{min(Y(b), base):.1f}" width="{bw:.1f}" height="{abs(base - Y(b)):.1f}" '
                  f'fill="{c}" opacity="0.85"/>' for a, b in zip(xv, yv)]
        else:
            s += [f'<line x1="{X(a):.1f}" y1="{Y(b):.1f}" x2="{X(a):.1f}" y2="{Y(e):.1f}" stroke="{c}" stroke-width="2.5" '
                  f'stroke-dasharray="5 3"/>' for a, b, e in zip(xv, yv, values[sr.y2])]
        if sr.label:
            mark = (f'<span class="sw" style="background:{c};border-radius:50%"></span>' if sr.kind == "points"
                    else f'<span class="sw" style="background:{c}"></span>')
            legend.append(f"<span>{mark}{esc(sr.label)}</span>")
    s.append("</svg>")
    return "".join(s) + (f'<div class="legend">{"".join(legend)}</div>' if legend else "")


def figure_html(f: Figure, values: dict | None = None, col: dict | None = None) -> str:
    cap = f'<p class="cap">{esc(f.caption)}</p>' if f.caption else ""
    if f.kind == "plot":
        if plot_problems(f.plot, values or {}):
            return f'<div class="fig"><p class="cap">[plot not drawn: {esc("; ".join(plot_problems(f.plot, values or {})))}]</p></div>'
        return f'<div class="fig">{plot_svg(f.plot, values, col or DEFAULT_COL)}{cap}</div>'
    if f.kind == "flow":
        boxes = '<span class="arr">↓</span>'.join(f'<span class="fb">{esc(s)}</span>' for s in f.steps if s.strip())
        return f'<div class="fig"><div class="flow">{boxes}</div>{cap}</div>'
    if f.kind == "code":
        lang = f'<span class="lang">{esc(f.language)}</span>' if f.language else ""
        return f'<div class="fig"><pre class="code">{lang}{esc(f.code.rstrip())}</pre>{cap}</div>'
    if f.kind == "table" and f.rows:
        head = "".join(f"<th>{esc(c)}</th>" for c in f.rows[0])
        body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in f.rows[1:])
        return f'<div class="fig"><table class="tb"><tr>{head}</tr>{body}</table>{cap}</div>'
    return ""


def quiz_html(q: Quiz) -> str:
    opts = "".join(f'<div class="opt"><span class="l">{"ABCDE"[i]}</span><span>{esc(o)}</span></div>'
                   for i, o in enumerate(q.options[:5]))
    return f'<div class="quiz"><p class="qq">{esc(q.question)}</p>{opts}</div>'


def content_body(s: Slide, values: dict | None = None, col: dict | None = None) -> str:
    out = ""
    show = s.clip if s.kind == "watch" else s.link if s.kind == "simulation" else ""
    if show:
        out += f'<div class="panel"><b>{PANEL[s.kind]}</b><span>{esc(show)}</span></div>'
    if s.quiz:
        return out + quiz_html(s.quiz)
    text = ("<ul>" + "".join(f"<li>{esc(b)}</li>" for b in s.bullets) + "</ul>" if s.bullets else "")
    text += "".join(block_html(b) for b in s.blocks)
    fig = figure_html(s.figure, values, col)
    if fig and text:
        wide = " wide" if s.figure.kind in ("code", "plot") else ""
        return out + f'<div class="cols{wide}"><div>{text}</div>{fig}</div>'
    return out + (f'<div class="solo">{fig}</div>' if fig else text)


def page(n: int, cls: str, title: str, body: str, foot: str, badge: str = "", tags: list[str] | None = None) -> str:
    chips = (f'<span class="badge">{esc(badge)}</span>' if badge else "") + "".join(f'<span class="lo">{esc(t)}</span>' for t in tags or [])
    return (f'<section class="slide {cls}" id="s{n}" data-n="{n}"><div class="hdr"><h1>{esc(title)}</h1>{chips}</div>'
            f'<div class="body">{body}</div><div class="foot"><span>{esc(foot)}</span><span>{n}</span></div></section>')


def deck_html(deck: LectureDeck, frame: dict, sources: dict[str, dict], cfg: dict, values: dict | None = None) -> str:
    """The whole deck as one page of 1280 x 720 slides (the PDF prints one slide per page). `values`: the running
    example's computed values (content/example.py), which plots are drawn from."""
    from profsagent.content.render import ref_line
    col = {k: f"#{x}" for k, x in cfg["render"]["colors"].items()}
    font = cfg["render"]["font"]
    secs = [f'<section class="slide cover" id="s1" data-n="1"><p class="course">{esc(frame["course"])}</p>'
            f'<h1>{esc(deck.title)}</h1><p class="subt">{esc(frame["subtitle"])}</p><p class="draft">{esc(frame["draft_note"])}</p></section>',
            page(2, "list", "By the end of this lecture you can", "<ul>" + "".join(f"<li>{esc(o)}</li>" for o in frame["objectives"]) + "</ul>",
                 frame["footer"])]
    for n, s in enumerate(deck.slides, FIRST_CONTENT_SLIDE):
        foot = frame["footer"] + (f"   ·   Sources: {' '.join(f'[{x}]' for x in s.sources)}" if s.sources else "")
        secs.append(page(n, f"k-{s.kind}", s.title, content_body(s, values, col), foot, BADGE.get(s.kind, ""), s.los))
    cited = [sid for sid in sources if any(sid in sl.sources for sl in deck.slides)]
    if cited:
        refs = "<ul>" + "".join(f"<li>[{esc(sid)}] {esc(ref_line(sources[sid]))}</li>" for sid in cited) + "</ul>"
        secs.append(page(len(secs) + 1, "list refs", "References", refs, frame["footer"]))
    maths = any(has_math(s) for s in deck.slides)
    h = cfg.get("html") or {}
    script = FIT_JS.replace("MIN_SCALE", str(h.get("min_scale", 0.8))).replace("RENDER_MATH", RENDER_MATH if maths else "")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{esc(deck.title)}</title>'
            + (katex_assets() if maths else "")
            + "<style>" + css(font, col)
            + "</style></head><body>" + "".join(secs) + f"<script>{script}</script></body></html>")


def css(font: str, col: dict) -> str:
    out = CSS.replace("FONT", font)
    for token, key in (("CODE_INK", "code_ink"), ("CODE_BG", "code_bg"), ("ACCENT_SOFT", "accent_soft"), ("ACCENT", "accent"),
                       ("MUTED", "muted"), ("PANEL", "panel"), ("INK", "ink")):     # longest tokens first
        out = out.replace(token, col[key])
    return out


CSS = """
@page { size: 13.333in 7.5in; margin: 0; }
* { box-sizing: border-box; }
body { margin: 0; background: #e5e7eb; font-family: 'FONT', 'Segoe UI', Arial, sans-serif; color: INK; }
.slide { width: 1280px; height: 720px; background: #fff; position: relative; overflow: hidden; margin: 0 auto 14px;
  break-after: page; page-break-after: always; }
.hdr { position: absolute; left: 58px; right: 58px; top: 28px; display: flex; align-items: center; gap: 10px;
  border-bottom: 3px solid ACCENT; padding-bottom: 10px; }
.hdr h1 { margin: 0; font-size: 30px; line-height: 1.2; flex: 1; }
.badge { font-size: 14px; font-weight: 700; color: ACCENT; background: ACCENT_SOFT; border-radius: 12px; padding: 3px 10px; white-space: nowrap; }
.lo { font-size: 13px; color: MUTED; border: 1px solid #d1d5db; border-radius: 10px; padding: 2px 8px; white-space: nowrap; }
.body { position: absolute; left: 58px; right: 58px; top: 112px; bottom: 46px; overflow: hidden; font-size: calc(21px * var(--s, 1)); line-height: 1.45; }
.foot { position: absolute; left: 58px; right: 58px; bottom: 14px; font-size: 12px; color: MUTED; display: flex; justify-content: space-between; gap: 20px; }
.foot span:first-child { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
ul { margin: 2px 0 10px; padding-left: 1.2em; } li { margin: 0.28em 0; } li::marker { color: ACCENT; }
.dm { margin: 0.35em 0 0.5em; }
.steps { display: flex; flex-direction: column; margin: 0.3em 0 0.5em; }
.st { display: grid; grid-template-columns: 1.6em 1fr 15em; align-items: center; gap: 0.7em; border-bottom: 1px dashed #d1d5db; }
.st .n { width: 1.4em; height: 1.4em; border-radius: 50%; background: ACCENT; color: #fff; font-size: 0.75em; font-weight: 700;
  display: flex; align-items: center; justify-content: center; }
.st .f .katex-display, .st .f .katex-display > .katex { margin: 0.3em 0; text-align: left; }
.st .why { color: #b45309; font-size: 0.8em; font-style: italic; line-height: 1.3; }
.def { display: flex; gap: 0.8em; align-items: baseline; border-left: 5px solid ACCENT; background: ACCENT_SOFT; padding: 0.45em 0.8em; margin: 0.4em 0 0.6em; }
.def b { white-space: nowrap; }
.think { border-left: 5px solid #d97706; background: #fff7ed; padding: 0.45em 0.8em; margin: 0.5em 0; }
.note { background: PANEL; border: 1px solid #e5e7eb; border-radius: 8px; padding: 0.45em 0.8em; margin: 0.5em 0; font-size: 0.95em; }
.cols { display: grid; grid-template-columns: 1.1fr 1fr; gap: 36px; align-items: start; }
.cols.wide { grid-template-columns: 0.9fr 1.1fr; }
.solo { display: flex; justify-content: center; } .solo .fig { width: 75%; }
.plot { width: 100%; max-height: 430px; display: block; }
.legend { display: flex; flex-wrap: wrap; gap: 6px 18px; justify-content: center; font-size: 0.72em; color: INK; margin-top: 4px; }
.legend .sw { display: inline-block; width: 14px; height: 14px; margin-right: 6px; vertical-align: -2px; }
.fig { min-width: 0; } .cap { color: MUTED; font-size: 0.75em; text-align: center; margin: 0.4em 0 0; }
.flow { display: flex; flex-direction: column; align-items: stretch; gap: 4px; }
.fb { border: 2px solid ACCENT; background: ACCENT_SOFT; border-radius: 10px; padding: 0.4em 0.7em; text-align: center; font-size: 0.85em; }
.arr { color: ACCENT; text-align: center; line-height: 1; }
.code { background: CODE_BG; color: CODE_INK; border-radius: 10px; padding: 14px 18px; font: calc(16px * var(--s, 1))/1.45 Consolas, monospace;
  margin: 0; white-space: pre; overflow: hidden; }
.lang { display: block; color: ACCENT_SOFT; font-size: 12px; margin-bottom: 6px; }
.tb { border-collapse: collapse; width: 100%; font-size: 0.85em; }
.tb th { background: ACCENT; color: #fff; text-align: left; padding: 0.35em 0.6em; } .tb td { background: PANEL; padding: 0.35em 0.6em; border-top: 2px solid #fff; }
.panel { display: flex; gap: 16px; align-items: center; background: ACCENT_SOFT; border-radius: 10px; padding: 0.5em 0.9em; margin-bottom: 0.7em; }
.panel b { color: ACCENT; }
.quiz { margin: 0 5%; } .qq { font-weight: 700; font-size: 1.15em; margin: 0 0 0.8em; }
.opt { display: flex; gap: 0.8em; align-items: center; background: PANEL; border-radius: 10px; padding: 0.45em 0.8em; margin: 0.45em 0; }
.opt .l { flex: none; width: 1.6em; height: 1.6em; border-radius: 50%; background: ACCENT; color: #fff; font-weight: 700;
  display: flex; align-items: center; justify-content: center; font-size: 0.8em; }
.cover { background: ACCENT; color: ACCENT_SOFT; padding: 150px 90px 0; }
.cover h1 { font-size: 50px; margin: 10px 0 24px; color: #fff; } .cover .course { font-size: 20px; margin: 0; }
.cover .subt { font-size: 20px; margin: 0; } .cover .draft { position: absolute; bottom: 40px; left: 90px; right: 90px; font-size: 14px; }
.refs .body { font-size: calc(17px * var(--s, 1)); }
.katex { font-size: 1.05em; } .katex-display { margin: 0.4em 0; }
@media print { body { background: #fff; } .slide { margin: 0; } }
"""

# Fit every slide body (shrink in 5% steps down to MIN_SCALE), then record what still overflows and every maths error.
FIT_JS = r"""
RENDER_MATH
function leftover(s) {          // maths auto-render could not find the end of: still raw \( \[ $$ in the slide's text
  const w = document.createTreeWalker(s, NodeFilter.SHOW_TEXT), out = []; let n;
  while ((n = w.nextNode())) {
    if (n.parentElement.closest('.katex, pre, code')) continue;
    const t = n.textContent, i = t.search(/\\[(\[]|\$\$/);
    if (i >= 0) out.push({tex: t.slice(i, i + 160), message: 'not typeset: unbalanced braces or a missing closing delimiter'});
  }
  return out;
}
function over(b) {
  const r = b.getBoundingClientRect(); let o = Math.max(0, b.scrollHeight - b.clientHeight, b.scrollWidth - b.clientWidth);
  b.querySelectorAll('li, p, .dm, .st, .def, .think, .note, .fig, .opt, .panel, .katex-display, pre, tr').forEach(e => {
    const q = e.getBoundingClientRect(); o = Math.max(o, q.bottom - r.bottom, q.right - r.right, e.scrollWidth - e.clientWidth);
  });
  return Math.round(o);
}
async function fit() {
  document.body.offsetHeight; await document.fonts.ready;
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  const out = [];
  for (const s of document.querySelectorAll('.slide')) {
    const b = s.querySelector('.body'); let scale = 1;
    if (b) { while (over(b) > 1 && scale > MIN_SCALE + 1e-9) { scale = Math.round((scale - 0.05) * 100) / 100; b.style.setProperty('--s', scale); } }
    const h = s.querySelector('.hdr h1'); let lines = 1;
    if (h) { if (h.getBoundingClientRect().height > 40) h.style.fontSize = '25px';
             lines = Math.round(h.getBoundingClientRect().height / 30); }
    out.push({slide: +s.dataset.n, scale: scale, overflow_px: b ? Math.max(0, over(b) - 1) : 0, title_lines: lines,
              math_errors: (s.__errs || []).concat(leftover(s), [...s.querySelectorAll('.katex-error')].map(e => ({tex: e.textContent.slice(0, 160), message: (e.title || '').slice(0, 200)})))});
  }
  window.__layout = out; document.body.dataset.ready = '1';
}
fit();
"""


# ------------------------------------------------------------------ the browser
def measure(path: Path, cfg: dict, pdf: Path | None = None, shots: dict[int, Path] | None = None) -> dict:
    """Open slides.html in Chrome and return {"slides": [{slide, scale, overflow_px, title_px, math_errors}]}, after
    printing `pdf` and saving the body of each slide in `shots` ({slide number: png}) when asked. {"error": why} when
    the browser cannot be used (no Playwright or no Chrome): the deck is still written, without the PDF."""
    h = cfg.get("html") or {}
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return {"error": "Playwright is not installed (pip install playwright)"}
    try:
        with sync_playwright() as p:
            b = p.chromium.launch(channel=h.get("browser", "chrome"))
            try:
                pg = b.new_page(viewport={"width": 1280, "height": 720}, device_scale_factor=2 if shots else 1)
                pg.goto(Path(path).resolve().as_uri())
                pg.wait_for_selector("body[data-ready='1']", timeout=int(h.get("timeout_s", 60)) * 1000)
                rep = {"slides": pg.evaluate("window.__layout")}
                if pdf:
                    pg.pdf(path=str(pdf), width="13.333in", height="7.5in", print_background=True)
                    rep["pdf"] = str(pdf)
                if shots:
                    rep["shots"] = {}
                    for n, png in shots.items():
                        body = pg.locator(f"#s{n} .body")
                        if body.count():
                            png.parent.mkdir(parents=True, exist_ok=True)
                            body.screenshot(path=str(png))
                            rep["shots"][n] = str(png)
                return rep
            finally:
                b.close()
    except Exception as e:  # noqa: BLE001  (no Chrome, a hung page: the deck is still usable without the PDF)
        return {"error": f"{type(e).__name__}: {str(e).splitlines()[0][:200]}"}


def layout_findings(report: dict) -> list[dict]:
    """The browser's measurements as findings: D-MATH (error) for a formula KaTeX cannot parse, D-OVERFLOW (error) for a
    slide whose text does not fit even at the smallest scale, D-OVERFLOW (warning) for a title that wraps past two lines."""
    out = []
    for r in report.get("slides") or []:
        sid = f"slide {r['slide']}"
        for e in r.get("math_errors") or []:
            tex = e["tex"].removeprefix("KaTeX auto-render: Failed to parse ").removesuffix(" with ")
            out.append(v("D-MATH", ERR, [sid], f"{sid}: KaTeX cannot typeset {tex}: {e['message'] or 'parse error'}"))
        if r.get("overflow_px", 0) > 2:
            out.append(v("D-OVERFLOW", ERR, [sid], f"{sid}: the content does not fit the slide even at "
                                                   f"{round(r['scale'] * 100)}% text size ({r['overflow_px']} px too much): "
                                                   "shorten it or split it into two slides"))
        if r.get("title_lines", 1) > 2:
            out.append(v("D-OVERFLOW", "warning", [sid], f"{sid}: the title does not fit on one line: shorten it"))
    for x in out:
        x["stage"] = "render"
    return out
