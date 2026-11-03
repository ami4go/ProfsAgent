"""Automatic checks for a recipe-based stepper page (machine-built simulations; README.md "Recipes").

    python qa_recipe.py <page.html> [screenshot folder]       prints PROBLEM: lines and "PROBLEMS: none" or a list

In Chrome with the network blocked, it checks that:
  - the recipe has every part (title, summary, topics, inputs, presets, code, run, check, examples, random);
  - run() works on every preset, every example and 40 random inputs: steps exist, each names a code line, each view uses
    the engine's widgets correctly, each prediction question has its answer among the options;
  - check() (the independent second method) agrees with run() on all of them, does not call run(), and says "wrong"
    when the result is deliberately corrupted;
  - run() gives the textbook answer for each example;
  - the page works: no errors, every example steps to its end, no sideways scrolling on a phone.
"""
import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")

PAGE = Path(sys.argv[1]).resolve()
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else PAGE.parent / "qa"
OUT.mkdir(parents=True, exist_ok=True)

CHECK_JS = r"""
() => {
  // each kind of problem is reported a few times at most, so one mistake repeated on every step cannot hide the others
  const R = window.__recipe, P = [], seen = {}, say = (m, key, max = 1) => { key = key || m; seen[key] = (seen[key] || 0) + 1; if (seen[key] <= max && P.length < 30) P.push(m); };
  if (!R) return { problems: ['the page has no recipe (window.__recipe)'], cases: 0 };
  for (const k of ['title', 'summary', 'intro', 'checked_by']) if (typeof R[k] !== 'string' || !R[k].trim()) say(`recipe.${k} must be a non-empty string`);
  if (!Array.isArray(R.topics) || R.topics.length < 2) say('recipe.topics must list at least 2 topics');
  for (const k of ['run', 'check', 'random']) if (typeof R[k] !== 'function') say(`recipe.${k} must be a function`);
  if (!Array.isArray(R.inputs) || !R.inputs.length) say('recipe.inputs must be a non-empty list');
  const ids = (R.inputs || []).map(f => f.id);
  if (new Set(ids).size !== ids.length) say('input ids must be unique');
  for (const f of R.inputs || []) if (!['text', 'number', 'select'].includes(f.kind)) say(`input ${f.id}: kind must be text, number or select`);
  if (!Array.isArray(R.presets) || R.presets.length < 2) say('recipe.presets must have at least 2 examples');
  if (!Array.isArray(R.examples) || R.examples.length < 2) say('recipe.examples must have at least 2 textbook answers');
  if (P.length) return { problems: P, cases: 0 };
  const src = String(R.check);
  if (/\brun\s*\(|recipe\s*\.\s*run\b|this\s*\.\s*run\b/.test(src)) say('check() calls run(); it must work the answer out again by its own, different method');
  const MARK = new Set(window.Stepper.marks), W = new Set(window.Stepper.widgets);
  const codeOf = v => (typeof R.code === 'function' ? R.code(v) : R.code) || [];
  const isInt = x => Number.isInteger(x);
  const checkView = (view, where) => {
    if (!Array.isArray(view) || !view.length) return say(`${where}: view must be a non-empty list of widgets`, 'noview');
    for (const w of view) {
      if (!w || !W.has(w.type)) { say(`${where}: unknown widget ${JSON.stringify(w && w.type)} (use ${[...W].join(', ')})`, 'unknown:' + (w && w.type)); continue; }
      const bad = m => say(`${where}: ${w.type} widget: ${m}`, 'w:' + w.type + ':' + m.replace(/[0-9]+/g, '#'));
      const marks = (o, n) => { for (const [k, v] of Object.entries(o || {})) { if (!MARK.has(v)) bad(`mark ${JSON.stringify(v)} (use ${[...MARK].join(', ')})`); if (n != null && !(isInt(+k) && +k >= 0 && +k < n)) bad(`mark on index ${k} outside 0..${n - 1}`); } };
      if (w.type === 'array') { if (!Array.isArray(w.items)) bad('items must be a list'); else { if (w.items.length > 60) bad('at most 60 items'); marks(w.marks, w.items.length);
        for (const [p, i] of Object.entries(w.pointers || {})) if (!isInt(i) || i < -1 || i > w.items.length) bad(`pointer ${p} = ${i} is not an index`); } }
      else if (w.type === 'stacks') { if (!Array.isArray(w.stacks) || w.stacks.some(s => !s || !Array.isArray(s.items))) bad('stacks must be a list of {name, items: [...]}');
        else for (const s of w.stacks) { marks(s.marks, s.items.length); if (s.mark && !MARK.has(s.mark)) bad(`mark ${s.mark}`); } }
      else if (w.type === 'callstack') { if (!Array.isArray(w.frames)) bad('frames must be a list'); }
      else if (w.type === 'vars') { if (!w.values || typeof w.values !== 'object' || Array.isArray(w.values)) bad('values must be an object'); else marks(w.marks, null); }
      else if (w.type === 'table') { if (!Array.isArray(w.columns) || !Array.isArray(w.rows) || w.rows.some(r => !Array.isArray(r) || r.length !== w.columns.length)) bad('rows must be lists as long as columns');
        else for (const [k, v] of Object.entries(w.marks || {})) { const [r, c] = k.split(',').map(Number); if (!MARK.has(v) || !(r >= 0 && r < w.rows.length && c >= 0 && c < w.columns.length)) bad(`mark ${k}: ${v}`); } }
      else if (w.type === 'text') { if (typeof w.text !== 'string') bad('text must be a string'); }
    }
  };
  const corrupt = x => {                    // a slightly wrong result, which an honest check must reject
    if (typeof x === 'number') return x + 1;
    if (typeof x === 'boolean') return !x;
    if (typeof x === 'string') return x + 'x';
    if (Array.isArray(x)) { const y = x.slice(); const i = y.findIndex((v, j) => j && JSON.stringify(v) !== JSON.stringify(y[0])); if (i > 0) { [y[0], y[i]] = [y[i], y[0]]; return y; } return y.length ? y.slice(1) : [0]; }
    if (x && typeof x === 'object') { const y = JSON.parse(JSON.stringify(x)); const k = Object.keys(y)[0]; if (k === undefined) return { wrong: 1 }; y[k] = corrupt(y[k]); return y; }
    return 'wrong';
  };
  let rs = 7; const rng = () => { rs = (rs + 0x6D2B79F5) >>> 0; let t = rs; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; };
  const cases = R.presets.map(p => ['preset "' + p.name + '"', p.values]).concat(R.examples.map((e, i) => ['example ' + (i + 1), e.values]));
  for (let i = 0; i < 40; i++) { try { cases.push(['random input ' + (i + 1), R.random(rng)]); } catch (e) { say('random() failed: ' + e.message); break; } }
  let corrupted = 0, caught = 0;
  for (const [name, values] of cases) {
    let tr;
    try { tr = R.run(JSON.parse(JSON.stringify(values))); } catch (e) { say(`${name}: run() threw ${e.message} for ${JSON.stringify(values).slice(0, 120)}`, 'threw', 3); continue; }
    if (!tr || tr.error) { say(`${name}: run() refused a valid input: ${JSON.stringify(tr && tr.error)} for ${JSON.stringify(values).slice(0, 120)}`, 'refused', 3); continue; }
    if (!Array.isArray(tr.steps) || tr.steps.length < 1 || tr.steps.length > 500) { say(`${name}: run() must return 1 to 500 steps (got ${tr.steps && tr.steps.length})`); continue; }
    if (tr.result === undefined) { say(`${name}: run() must return result (the final answer, for the checks)`); continue; }
    const code = codeOf(values);
    tr.steps.forEach((st, k) => {
      const where = `${name}, step ${k}`;
      if (!isInt(st.line) || st.line < 1 || st.line > code.length) say(`${where}: line ${st.line} is not a line of the code (1..${code.length})`, 'line', 2);
      if (typeof st.note !== 'string' || !st.note.trim()) say(`${where}: every step needs a note (one plain sentence)`, 'note');
      checkView(st.view, where);
      if (st.ask && (!Array.isArray(st.ask.options) || st.ask.options.length < 2 || !st.ask.options.map(String).includes(String(st.ask.answer)))) say(`${where}: ask.answer must be one of ask.options`, 'ask', 2);
    });
    let ck;
    try { ck = R.check(JSON.parse(JSON.stringify(values)), JSON.parse(JSON.stringify(tr))); } catch (e) { say(`${name}: check() threw ${e.message}`); continue; }
    if (!ck || ck.ok !== true) say(`${name}: the independent check disagrees: ${ck && ck.text}`, 'disagree', 3);
    if (corrupted < 6) {
      corrupted++;
      const bad = JSON.parse(JSON.stringify(tr)); bad.result = corrupt(bad.result);
      try { const c2 = R.check(JSON.parse(JSON.stringify(values)), bad); if (c2 && c2.ok === false) caught++; } catch (e) { caught++; }
    }
  }
  if (corrupted && caught < corrupted) say(`check() accepted a wrong result in ${corrupted - caught} of ${corrupted} tries (result changed slightly); it must recompute the answer and compare`);
  R.examples.forEach((e, i) => {
    try { const tr = R.run(JSON.parse(JSON.stringify(e.values))); const a = JSON.stringify(tr && tr.result), b = JSON.stringify(e.result);
      if (a !== b) say(`example ${i + 1}: run() gives ${a}, the textbook answer is ${b}`); } catch (err) { /* reported above */ }
  });
  return { problems: P, cases: cases.length };
}
"""

problems, errors, net = [], [], []


def expect(cond, msg):
    print(("ok: " if cond else "PROBLEM: ") + msg, flush=True)
    if not cond:
        problems.append(msg)


with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1400, "height": 900})
    pg.on("pageerror", lambda e: errors.append(str(e)[:300]))
    pg.on("console", lambda m: errors.append(m.text[:300]) if m.type == "error" else None)
    pg.route("http*://**", lambda r: (net.append(r.request.url), r.abort()))
    pg.goto(PAGE.as_uri())
    try:
        pg.wait_for_function("window.__recipe && window.__sim", timeout=15000)
    except Exception:  # noqa: BLE001
        expect(False, "the page did not start: " + "; ".join(errors[:3]))
        print("PROBLEMS:", json.dumps(problems, ensure_ascii=False))
        sys.exit(1)
    res = pg.evaluate(CHECK_JS)
    meta = pg.evaluate("() => { const R = window.__recipe; return {title: R.title, summary: R.summary, topics: R.topics, checked_by: R.checked_by, "
                       "steps: (() => { try { return R.run(R.presets[0].values).steps.length; } catch (e) { return null; } })()}; }")
    print("META:", json.dumps(meta, ensure_ascii=False), flush=True)
    for p in res["problems"]:
        expect(False, p)
    if not res["problems"]:
        expect(True, f"run() and the independent check agree on {res['cases']} inputs (presets, textbook examples, random)")
    first = pg.inner_text(".st-check") if pg.locator(".st-check").count() else ""
    expect(first.startswith("✓"), f"the live check line passes on the first example ({first[:80]!r})")
    pg.screenshot(path=str(OUT / "1_start.png"))
    n = pg.evaluate("window.__recipe.presets.length")
    for i in range(n):
        pg.select_option("#st-preset", str(i))
        pg.wait_for_timeout(350)
        pg.click("text=⏭")
        pos = pg.inner_text(".st-pos")
        expect("Step" in pos and pos.split("Step ")[1].split(" of ")[0] == pos.split(" of ")[1].split(" ")[0], f"example {i + 1} steps to its end ({pos})")
        pg.screenshot(path=str(OUT / f"2_example_{i + 1}_end.png"))
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.select_option("#st-preset", "0")
    pg.wait_for_timeout(400)
    sw = pg.evaluate("document.documentElement.scrollWidth")
    expect(sw <= 392, f"phone: no sideways scrolling ({sw}px)")
    pg.screenshot(path=str(OUT / "3_phone.png"), full_page=True)
    expect(not errors, "no errors in the page" + ("" if not errors else ": " + " | ".join(errors[:3])))
    expect(not net, "no network requests (works offline)" + ("" if not net else ": " + ", ".join(net[:3])))
    b.close()
print("PROBLEMS:", json.dumps(problems, ensure_ascii=False) if problems else "none")
sys.exit(1 if problems else 0)
