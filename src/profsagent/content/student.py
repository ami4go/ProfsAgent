"""Student mode: one self-contained page per class that students follow during (and after) the lecture.

    student_page(deck, frame, sources, quiz=None) -> html          written as material/<lecture>/student.html

What students get, in the class's order: a "before class" list (videos marked pre-class, readings), every content slide
WITHOUT the speaker notes or answer keys, recap questions with answers to reveal, in-class check questions answered by
clicking (right / wrong and the explanation), the watch and simulation panels as links, and the review quiz at the end
(C's D8 quiz for the lecture when it exists, else the deck's check questions) with a score. One HTML file: no internet,
no libraries; works on a phone; light and dark. No AI calls: it is rendered from deck.json each time the deck is written.
"""
from __future__ import annotations

import html
import json
import re

from profsagent.content.models import FIRST_CONTENT_SLIDE, LectureDeck
from profsagent.content.render import ref_line

esc = html.escape


def _link(text: str) -> str:
    """Text with its URLs made into links (the clip and simulation panels)."""
    return re.sub(r"(https?://[^\s<>\"']+)", r'<a href="\1" target="_blank" rel="noopener">\1</a>', esc(text))


def _figure(f) -> str:
    if f.kind == "flow":
        return '<div class="flow">' + '<span class="arrow">→</span>'.join(f'<span class="box">{esc(s)}</span>' for s in f.steps) + "</div>"
    if f.kind == "code":
        return f'<pre class="code"><code>{esc(f.code)}</code></pre>'
    if f.kind == "table" and f.rows:
        head = "".join(f"<th>{esc(c)}</th>" for c in f.rows[0])
        body = "".join("<tr>" + "".join(f"<td>{esc(c)}</td>" for c in r) + "</tr>" for r in f.rows[1:])
        return f'<div class="tw"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>'
    return ""


def _question(qid: str, q: dict) -> str:
    opts = "".join(f'<button class="opt" data-q="{qid}" data-i="{i}">{"ABCDE"[i]}. {esc(o)}</button>' for i, o in enumerate(q["options"]))
    return (f'<div class="q" id="{qid}" data-answer="{q["answer"]}"><p class="qt">{esc(q["question"])}</p><div class="opts">{opts}</div>'
            f'<p class="why" hidden>{esc(q.get("explanation") or "")}</p></div>')


def student_page(deck: LectureDeck, frame: dict, sources: dict[str, dict], quiz: list[dict] | None = None) -> str:
    cards, before, checks = [], [], []
    for i, s in enumerate(deck.slides, FIRST_CONTENT_SLIDE):
        kind = s.kind.replace("_", " ")
        body = ""
        if s.kind == "recap":
            body += "<ol class='recap'>" + "".join(f"<li>{esc(b)}</li>" for b in s.bullets) + "</ol>"
            body += f'<details><summary>Show the answers</summary><p>{esc(s.notes)}</p></details>' if s.notes else ""
        else:
            if s.clip or s.link:
                label = "Watch" if s.kind == "watch" else "Open"
                body += f'<div class="panel"><b>{label}</b><span>{_link(s.clip or s.link)}</span></div>'
                if s.kind == "watch" and s.clip:
                    before.append(f"{esc(s.title)}: {_link(s.clip)}")
            if s.bullets and s.kind != "check":
                body += "<ul>" + "".join(f"<li>{esc(b)}</li>" for b in s.bullets) + "</ul>"
            body += _figure(s.figure)
            if s.quiz:
                q = {"question": s.quiz.question, "options": s.quiz.options, "answer": s.quiz.answer, "explanation": s.quiz.explanation}
                body += _question(f"s{i}", q)
                checks.append(q)
        cite = " ".join(f"[{x}]" for x in s.sources)
        cards.append(f'<section class="card k-{s.kind}" id="slide-{i}"><header><span class="no">{i}</span><h2>{esc(s.title)}</h2>'
                     f'<span class="kind">{esc(kind)}</span></header>{body}'
                     + (f'<p class="src">Sources: {esc(cite)}</p>' if cite else "") + "</section>")
    final = quiz or checks
    quiz_html = "".join(_question(f"f{n}", q) for n, q in enumerate(final, 1))
    cited = [sid for sid in sources if any(sid in sl.sources for sl in deck.slides)]
    refs = "".join(f"<li>[{esc(sid)}] {_link(ref_line(sources[sid]))}</li>" for sid in cited)
    before_html = ("<ul>" + "".join(f"<li>{x}</li>" for x in before) + "</ul>") if before else "<p>Nothing to do before class.</p>"
    objectives = "".join(f"<li>{esc(re.sub(r' [(]CO[0-9.LO]+[)]$', '', o))}</li>" for o in frame["objectives"])
    return TEMPLATE.format(title=esc(deck.title), course=esc(frame["course"]), subtitle=esc(frame["subtitle"]),
                           objectives=objectives, before=before_html, cards="".join(cards), quiz=quiz_html,
                           n_quiz=len(final), refs=f"<ol>{refs}</ol>" if refs else "", data=json.dumps(len(final)))


TEMPLATE = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title><style>
:root{{--bg:#f7f7f4;--card:#fff;--ink:#1f2937;--muted:#6b7280;--accent:#0f766e;--soft:#ccfbf1;--line:#e5e7eb;--ok:#15803d;--bad:#b91c1c;--code:#111827;--codeink:#e5e7eb}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111312;--card:#1b1e1d;--ink:#e7e9e8;--muted:#9ca3af;--accent:#2dd4bf;--soft:#123a36;--line:#2b302e;--ok:#4ade80;--bad:#f87171;--code:#0b0f14;--codeink:#e5e7eb}}}}
*{{box-sizing:border-box}}body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif}}
main{{max-width:820px;margin:0 auto;padding:24px max(16px,env(safe-area-inset-left)) 64px}}
h1{{font-size:1.6rem;margin:.2rem 0;text-wrap:balance}}.sub{{color:var(--muted);margin:0 0 1rem}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}}
.card header{{display:flex;gap:10px;align-items:baseline}}.card h2{{font-size:1.15rem;margin:0;flex:1;text-wrap:balance}}
.no{{color:var(--muted);font-size:.85rem;min-width:1.6em}}.kind{{font-size:.75rem;text-transform:uppercase;letter-spacing:.06em;color:var(--accent);background:var(--soft);padding:2px 8px;border-radius:99px}}
ul,ol{{padding-left:1.3em}}li{{margin:.25em 0}}.src{{color:var(--muted);font-size:.8rem;margin:.6em 0 0}}
.panel{{display:flex;gap:12px;background:var(--soft);border-radius:8px;padding:10px 12px;margin:.6em 0;overflow-wrap:anywhere}}.panel b{{color:var(--accent)}}
.flow{{display:flex;flex-wrap:wrap;gap:6px;align-items:center;margin:.8em 0}}.box{{border:1.5px solid var(--accent);border-radius:8px;padding:6px 10px}}.arrow{{color:var(--muted)}}
pre.code{{background:var(--code);color:var(--codeink);padding:12px;border-radius:8px;overflow-x:auto;font:13px/1.45 Consolas,monospace}}
.tw{{overflow-x:auto}}table{{border-collapse:collapse;margin:.6em 0}}th,td{{border:1px solid var(--line);padding:6px 10px;text-align:left}}th{{background:var(--soft)}}
.q{{border-top:1px dashed var(--line);margin-top:.8em;padding-top:.6em}}.qt{{font-weight:600}}.opts{{display:grid;gap:6px}}
.opt{{text-align:left;font:inherit;color:inherit;background:transparent;border:1px solid var(--line);border-radius:8px;padding:8px 10px;cursor:pointer}}
.opt:hover{{border-color:var(--accent)}}.opt.right{{border-color:var(--ok);color:var(--ok);font-weight:600}}.opt.wrong{{border-color:var(--bad);color:var(--bad)}}
.why{{color:var(--muted)}}details summary{{cursor:pointer;color:var(--accent)}}#score{{font-weight:600;color:var(--accent)}}
nav.top{{position:sticky;top:0;background:var(--bg);padding:8px 0;display:flex;gap:14px;flex-wrap:wrap;font-size:.9rem;border-bottom:1px solid var(--line);z-index:2}}
a{{color:var(--accent)}}</style></head><body><main>
<p class="sub">{course} · {subtitle}</p><h1>{title}</h1>
<nav class="top"><a href="#before">Before class</a><a href="#slides">Class</a><a href="#quiz">Review quiz</a></nav>
<section class="card" id="before"><h2>By the end of this class you can</h2><ul>{objectives}</ul><h2>Before class</h2>{before}</section>
<div id="slides">{cards}</div>
<section class="card" id="quiz"><h2>Review quiz</h2><p class="sub">{n_quiz} questions · <span id="score">score: 0 / {n_quiz}</span></p>{quiz}</section>
<section class="card"><h2>References</h2>{refs}</section>
</main><script>
var total={data},done={{}};
document.addEventListener('click',function(e){{var b=e.target.closest('.opt');if(!b)return;var q=document.getElementById(b.dataset.q);
if(q.dataset.done)return;q.dataset.done=1;var ok=b.dataset.i===q.dataset.answer;b.classList.add(ok?'right':'wrong');
q.querySelectorAll('.opt').forEach(function(o){{if(o.dataset.i===q.dataset.answer)o.classList.add('right');}});
q.querySelector('.why').hidden=false;if(q.id.charAt(0)==='f'){{done[q.id]=ok;var s=0;for(var k in done)if(done[k])s++;
document.getElementById('score').textContent='score: '+s+' / '+total;}}}});
</script></body></html>"""
