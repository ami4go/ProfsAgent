/* Stepper engine (type 1, step-through processes). docs/09_phase2_A_simulation_catalogue.md §3; API in README.md.
   A simulation supplies its inputs, its code, run(values) -> trace, render(view, step, k, trace, values) and an
   independent check(values, trace); the engine gives it the controls, the highlighted code line, predict-the-next-step
   questions, keyboard keys, a shareable link and the live check line. No libraries; works offline. */
(function () {
  'use strict';
  const h = (tag, attrs = {}, ...kids) => {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(attrs)) { if (k === 'class') e.className = v; else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else if (v !== false && v != null) e.setAttribute(k, v === true ? '' : v); }
    for (const k of kids.flat()) if (k != null) e.append(k.nodeType ? k : document.createTextNode(String(k)));
    return e;
  };
  const SVGNS = 'http://www.w3.org/2000/svg';
  const sv = (tag, attrs = {}, ...kids) => {             // the same helper for SVG drawings
    const e = document.createElementNS(SVGNS, tag);
    for (const [k, v] of Object.entries(attrs)) if (v !== false && v != null) e.setAttribute(k === 'class' ? 'class' : k, v);
    for (const k of kids.flat()) if (k != null) e.append(k.nodeType ? k : document.createTextNode(String(k)));
    return e;
  };
  function readHash() { try { const q = new URLSearchParams(location.hash.slice(1)); const o = {}; for (const [k, v] of q) o[k] = v; return Object.keys(o).length ? o : null; } catch (e) { return null; } }
  // the setup goes into the link and, inside the ProfsAgent app, to the app (simulations/_engines/share/share.js; optional)
  function share(cfg, values) {
    const p = (cfg.presets || []).find(x => cfg.inputs.every(f => String(x.values[f.id]) === String(values[f.id])));
    const text = cfg.describe ? cfg.describe(values) : cfg.inputs.map(f => f.label + ': ' + values[f.id]).join(' · ');
    const summary = (p ? 'Example "' + p.name + '": ' : '') + text;
    if (window.SimShare) window.SimShare.write(values, summary);
    else try { history.replaceState(null, '', '#' + new URLSearchParams(values).toString()); } catch (e) {}
  }

  // ---------------------------------------------------------------- ready-made views: a simulation without its own render()
  // returns, on every step, view: [widget, ...]; the engine draws them (README.md lists the widgets). Machine-built
  // simulations always use these, so they only describe what is on screen, never how to draw it.
  const MARKS = ['active', 'compare', 'swap', 'done', 'min', 'muted'];
  const mk = k => (MARKS.includes(k) ? ' sv-' + k : '');
  const fmt = v => (v == null ? '' : typeof v === 'number' ? String(Math.round(v * 1000) / 1000) : typeof v === 'object' ? JSON.stringify(v) : String(v));
  const WIDGETS = {
    array(w) {
      const items = w.items || [], marks = w.marks || {}, ptr = {};
      for (const [name, i] of Object.entries(w.pointers || {})) (ptr[i] = ptr[i] || []).push(name);
      const max = Math.max(1, ...items.map(v => Math.abs(+v) || 0));
      return h('div', { class: 'sv-array' + (w.bars ? ' sv-bars' : '') }, ...items.map((v, i) => h('div', { class: 'sv-cell' + mk(marks[i]) },
        w.bars ? h('div', { class: 'sv-bartrack' }, h('div', { class: 'sv-bar', style: 'height:' + Math.max(3, Math.round(100 * Math.abs(+v || 0) / max)) + '%' })) : null,
        h('div', { class: 'sv-val' }, fmt(v)), h('div', { class: 'sv-idx' }, i), h('div', { class: 'sv-ptr' }, ptr[i] ? ptr[i].join(' ') : ''))),
        ...Object.entries(ptr).filter(([i]) => +i < 0 || +i >= items.length).map(([i, n]) => h('div', { class: 'sv-cell sv-muted' },
          h('div', { class: 'sv-val' }, '·'), h('div', { class: 'sv-idx' }, i), h('div', { class: 'sv-ptr' }, n.join(' ')))));
    },
    stacks(w) {
      const all = (w.stacks || []).flatMap(s => s.items || []), max = Math.max(1, ...all.map(v => Math.abs(+v) || 0));
      return h('div', { class: 'sv-stacks' }, ...(w.stacks || []).map(s => {
        const it = s.items || [], m = s.marks || {};
        return h('div', { class: 'sv-stack' + mk(s.mark) }, h('div', { class: 'sv-pile' }, ...it.map((v, j) => h('div', { class: 'sv-item' + (w.disks ? ' sv-disk' : '') + mk(m[j]),
          style: w.disks ? 'width:' + (24 + Math.round(70 * Math.abs(+v || 0) / max)) + '%' : null }, fmt(v))).reverse()), h('div', { class: 'sv-name' }, fmt(s.name)));
      }));
    },
    callstack(w) { const f = w.frames || []; return h('div', { class: 'sv-calls' }, ...f.map((x, i) => h('div', { class: 'sv-frame' + (i === f.length - 1 ? ' sv-active' : '') }, fmt(x))).reverse()); },
    vars(w) {
      const m = w.marks || {};
      return h('div', { class: 'sv-vars' }, ...Object.entries(w.values || {}).map(([k, v]) => h('span', { class: 'sv-var' + mk(m[k]) }, h('b', {}, k), ' = ', Array.isArray(v) ? '[' + v.map(fmt).join(', ') + ']' : fmt(v))));
    },
    table(w) {
      const m = w.marks || {};
      return h('div', { class: 'sv-tablebox' }, h('table', { class: 'sv-table' }, h('tr', {}, ...(w.columns || []).map(c => h('th', {}, fmt(c)))),
        ...(w.rows || []).map((r, ri) => h('tr', {}, ...r.map((c, ci) => h('td', { class: mk(m[ri + ',' + ci]).trim() }, fmt(c)))))));
    },
    text(w) { return h('p', { class: 'sv-text' + mk(w.mark) }, fmt(w.text)); },
    // ---- drawn figures: a simulation shows at least one of these (or array / stacks) on every step
    plot(w) {                                            // points, lines and shapes on x-y axes
      const [x0, x1] = w.x || [0, 1], [y0, y1] = w.y || [0, 1], W = 360, ml = w.ylabel ? 46 : 38, mr = 10, mt = 10, mb = w.xlabel ? 40 : 26;
      const ph = w.equal ? Math.max(140, Math.min(300, (W - ml - mr) * (y1 - y0) / ((x1 - x0) || 1))) : 210, H = ph + mt + mb;
      const X = v => ml + (W - ml - mr) * ((+v - x0) / ((x1 - x0) || 1)), Y = v => mt + ph - ph * ((+v - y0) / ((y1 - y0) || 1));
      const cls = (base, m) => base + (MARKS.includes(m) ? ' m-' + m : '');
      const id = 'clip' + Math.random().toString(36).slice(2, 8), tk = (a, b) => [a, (a + b) / 2, b];
      const ticks = [...tk(x0, x1).map(v => sv('text', { x: X(v), y: mt + ph + 16, 'text-anchor': 'middle', class: 'sv-tick' }, fmt(v))),
        ...tk(y0, y1).map(v => sv('text', { x: ml - 5, y: Y(v) + 4, 'text-anchor': 'end', class: 'sv-tick' }, fmt(v)))];
      const shapes = (w.shapes || []).map(s => s.kind === 'circle' ? sv('ellipse', { cx: X(s.cx), cy: Y(s.cy), rx: Math.abs(X(s.cx + s.r) - X(s.cx)), ry: Math.abs(Y(s.cy + s.r) - Y(s.cy)), class: cls('sv-shape', s.mark) })
        : s.kind === 'rect' ? sv('rect', { x: Math.min(X(s.x), X(s.x + s.w)), y: Math.min(Y(s.y), Y(s.y + s.h)), width: Math.abs(X(s.x + s.w) - X(s.x)), height: Math.abs(Y(s.y + s.h) - Y(s.y)), class: cls('sv-shape', s.mark) })
        : sv('line', { x1: X(s.x1), y1: Y(s.y1), x2: X(s.x2), y2: Y(s.y2), class: cls('sv-seg', s.mark) }));
      const lines = (w.lines || []).map(l => sv('polyline', { points: (l.points || []).map(p => X(p[0]) + ',' + Y(p[1])).join(' '), class: cls('sv-line', l.mark) }));
      const pts = (w.points || []).map(p => { const q = Array.isArray(p) ? { x: p[0], y: p[1] } : p;
        return sv('circle', { cx: X(q.x), cy: Y(q.y), r: q.mark === 'active' ? 5 : 3.2, class: cls('sv-pt', q.mark) }, q.label ? sv('title', {}, q.label) : null); });
      const legend = (w.lines || []).filter(l => l.label).map((l, i) => sv('text', { x: W - mr - 4, y: mt + 14 + 14 * i, 'text-anchor': 'end', class: cls('sv-legend', l.mark) }, l.label));
      return h('div', { class: 'sv-plot' }, sv('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': w.label || 'plot' },
        sv('defs', {}, sv('clipPath', { id }, sv('rect', { x: ml, y: mt, width: W - ml - mr, height: ph }))),
        sv('rect', { x: ml, y: mt, width: W - ml - mr, height: ph, class: 'sv-frame' }),
        sv('g', { 'clip-path': 'url(#' + id + ')' }, ...shapes, ...lines, ...pts), ...ticks, ...legend,
        w.xlabel ? sv('text', { x: (ml + W - mr) / 2, y: H - 6, 'text-anchor': 'middle', class: 'sv-axlabel' }, w.xlabel) : null,
        w.ylabel ? sv('text', { x: 12, y: mt + ph / 2, 'text-anchor': 'middle', class: 'sv-axlabel', transform: 'rotate(-90 12 ' + (mt + ph / 2) + ')' }, w.ylabel) : null));
    },
    graph(w) {                                           // nodes and edges; a circle layout unless the nodes give x, y in 0..1
      const ns = w.nodes || [], W = 360, H = 260, R = 16, at = {};
      ns.forEach((n, i) => { const a = -Math.PI / 2 + 2 * Math.PI * i / Math.max(1, ns.length);
        at[n.id] = n.x != null && n.y != null ? [30 + (W - 60) * n.x, 26 + (H - 52) * n.y] : [W / 2 + (W / 2 - 40) * Math.cos(a), H / 2 + (H / 2 - 32) * Math.sin(a)]; });
      const cls = (base, m) => base + (MARKS.includes(m) ? ' m-' + m : '');
      const id = 'arr' + Math.random().toString(36).slice(2, 8);
      const edges = (w.edges || []).filter(e => at[e.from] && at[e.to]).map(e => { const [ax, ay] = at[e.from], [bx, by] = at[e.to], d = Math.hypot(bx - ax, by - ay) || 1;
        const sx = ax + (bx - ax) * R / d, sy = ay + (by - ay) * R / d, tx = bx - (bx - ax) * (R + 2) / d, ty = by - (by - ay) * (R + 2) / d;
        return sv('g', {}, sv('line', { x1: sx, y1: sy, x2: tx, y2: ty, class: cls('sv-edge', e.mark), 'marker-end': w.directed ? 'url(#' + id + ')' : null }),
          e.label != null ? sv('text', { x: (ax + bx) / 2, y: (ay + by) / 2 - 4, 'text-anchor': 'middle', class: 'sv-elabel' }, fmt(e.label)) : null); });
      const nodes = ns.map(n => sv('g', {}, sv('circle', { cx: at[n.id][0], cy: at[n.id][1], r: R, class: cls('sv-node', n.mark) }),
        sv('text', { x: at[n.id][0], y: at[n.id][1] + 4, 'text-anchor': 'middle', class: 'sv-nlabel' }, fmt(n.label != null ? n.label : n.id))));
      return h('div', { class: 'sv-plot' }, sv('svg', { viewBox: '0 0 ' + W + ' ' + H, role: 'img', 'aria-label': w.label || 'graph' },
        sv('defs', {}, sv('marker', { id, viewBox: '0 0 10 10', refX: 9, refY: 5, markerWidth: 7, markerHeight: 7, orient: 'auto-start-reverse' }, sv('path', { d: 'M0,0 L10,5 L0,10 z', class: 'sv-arrow' }))),
        ...edges, ...nodes));
    },
    grid(w) {                                            // a board of squares: matrices, mazes, DP tables, cellular automata
      const cells = w.cells || [], m = w.marks || {}, nums = cells.flat().filter(v => typeof v === 'number'), max = Math.max(1, ...nums.map(Math.abs));
      return h('div', { class: 'sv-grid', style: 'grid-template-columns:repeat(' + ((cells[0] || []).length || 1) + ', minmax(0, 46px))' },
        ...cells.flatMap((row, r) => row.map((v, c) => h('div', { class: 'sv-sq' + mk(m[r + ',' + c]),
          style: w.heat && typeof v === 'number' ? 'background:rgba(159,211,240,' + (0.08 + 0.6 * Math.abs(v) / max).toFixed(2) + ')' : null }, w.hide_values ? '' : fmt(v)))));
    },
  };
  const FIGURES = ['array', 'stacks', 'plot', 'graph', 'grid'];
  function renderView(view, st, k, tr, values, valsBox) {
    // the figure goes on the board; with a values box beside it, `vars` widgets go there instead, and a value that just
    // changed is marked with what it was
    const ws = Array.isArray(st && st.view) ? st.view : [];
    const onBoard = ws.filter(w => !(valsBox && w && w.type === 'vars'));
    view.replaceChildren(...onBoard.map(w => h('section', { class: 'sv-w' }, w && w.label ? h('div', { class: 'sv-label' }, w.label) : null,
      w && WIDGETS[w.type] ? WIDGETS[w.type](w) : h('p', { class: 'sv-text' }, 'Unknown view: ' + (w && w.type)))));
    // a legend for the colours this step uses, so the meaning never rests on colour alone
    const used = new Set(), seen = o => { if (o && typeof o === 'object') for (const [k, v] of Object.entries(o)) { if (k === 'mark' || k === 'marks') { if (typeof v === 'string') used.add(v); else if (v && typeof v === 'object') Object.values(v).forEach(m => used.add(m)); } else seen(v); } };
    onBoard.forEach(seen);
    const words = { active: 'now', compare: 'compared', swap: 'swapped', done: 'done', min: 'smallest' };
    const keys = MARKS.filter(m => used.has(m) && words[m]);
    if (keys.length) view.append(h('div', { class: 'sv-legend-row' }, ...keys.map(m => h('span', { class: 'sv-key sv-key-' + m }, words[m]))));
    if (!valsBox) return;
    const prevStep = tr && k > 0 ? tr.steps[k - 1] : null;
    const before = Object.assign({}, ...((prevStep && Array.isArray(prevStep.view) ? prevStep.view : []).filter(w => w && w.type === 'vars').map(w => w.values || {})));
    valsBox.replaceChildren(...ws.filter(w => w && w.type === 'vars').flatMap(w => Object.entries(w.values || {}).map(([key, v]) => {
      const show = x => Array.isArray(x) ? '[' + x.map(fmt).join(', ') + ']' : fmt(x);
      const changed = k > 0 && key in before && show(before[key]) !== show(v);
      return h('div', { class: 'st-val' + (changed ? ' changed' : '') + mk((w.marks || {})[key]) }, h('b', {}, show(v)),
        h('span', {}, key), changed ? h('span', { class: 'was' }, 'was ' + show(before[key])) : null);
    })));
  }

  function mount(cfg) {
    const S = { values: {}, trace: null, k: 0, playing: null, predict: true, answered: {}, score: [0, 0] };
    const store = { get(k) { try { return sessionStorage.getItem(k); } catch (e) { return null; } }, set(k, v) { try { sessionStorage.setItem(k, v); } catch (e) {} } };
    const root = document.body;
    root.classList.add('st-app');
    if (window.parent !== window) root.classList.add('framed');      // inside the app: its window already shows the title
    // ---- the top: title, the example, "Change the input", Present
    const preset = h('select', { id: 'st-preset', 'aria-label': 'Example' });
    (cfg.presets || []).forEach((p, i) => preset.append(h('option', { value: i }, p.name)));
    preset.append(h('option', { value: 'own' }, 'Your own'));
    const bEdit = h('button', { class: 'st-link', 'aria-expanded': 'false', 'aria-controls': 'st-editor' }, 'Change the input');
    const bPresent = h('button', { class: 'st-btn', title: 'Present on a projector (P)' }, '⛶ Present');
    root.append(h('header', { class: 'st-head' }, h('div', { class: 'st-titles' }, h('h1', {}, cfg.title), cfg.intro ? h('p', {}, cfg.intro) : null),
      h('div', { class: 'st-tools' }, h('label', { class: 'st-exl', for: 'st-preset' }, 'Example'), preset, bEdit, bPresent)));
    // ---- the input, hidden until asked for
    const fields = {}, errs = {};
    const inputsBox = h('div', { class: 'st-fields' });
    for (const f of cfg.inputs) {
      let inp;
      if (f.kind === 'select') { inp = h('select', { id: 'st-' + f.id }); f.options.forEach(([v, l]) => inp.append(h('option', { value: v }, l))); }
      else inp = h('input', { id: 'st-' + f.id, type: f.kind === 'number' ? 'number' : 'text', class: f.mono ? 'mono' : '', min: f.min, max: f.max, step: f.step, spellcheck: 'false', autocomplete: 'off' });
      fields[f.id] = inp; errs[f.id] = h('div', { class: 'st-err' });
      inputsBox.append(h('div', { class: 'st-field' }, h('label', { for: 'st-' + f.id }, f.label), inp, f.help ? h('div', { class: 'st-help' }, f.help) : null, errs[f.id]));
      inp.addEventListener(f.kind === 'select' ? 'change' : 'input', () => { preset.value = 'own'; schedule(); });
    }
    const predictBox = h('input', { type: 'checkbox', id: 'st-predict', checked: true });
    const editor = h('section', { class: 'st-panel st-editor', id: 'st-editor', hidden: true, 'aria-label': 'Input' }, inputsBox,
      h('div', { class: 'st-edfoot' }, h('label', { class: 'st-row', for: 'st-predict' }, predictBox, 'Ask me to predict before showing each answer'),
        h('button', { class: 'st-btn', onclick: () => toggleEditor(false) }, 'Done')));
    // ---- the board: the figure, then one sentence on what just happened; the question; the result only at the end
    const view = h('div', { class: 'st-view' });
    const note = h('div', { class: 'st-note', 'aria-live': 'polite' });
    const summary = h('div', { class: 'st-summary', hidden: true });
    const board = h('section', { class: 'st-board', 'aria-label': 'The simulation' }, view, h('div', { class: 'st-caption' }, note, summary));
    // ---- the controls: Back, Next (the main one), Play, and the step
    const bBack = h('button', { class: 'st-btn', title: 'Previous step (←)' }, '◀ Back');
    const bNext = h('button', { class: 'st-btn primary', title: 'Next step (→)' }, 'Next ▶');
    const bPlay = h('button', { class: 'st-btn', title: 'Play (space)' }, '▶ Play');
    const slider = h('input', { type: 'range', min: 0, max: 0, value: 0, 'aria-label': 'Step' });
    const pos = h('span', { class: 'st-pos' });
    const checkLine = h('div', { class: 'st-check' });
    const controls = h('div', { class: 'st-controls' }, bBack, bNext, bPlay, h('div', { class: 'st-track' }, slider, pos), checkLine);
    // ---- beside the board: the values, and the code (shown only when asked for)
    const vals = h('div', { class: 'st-vals' });
    const valsCard = h('section', { class: 'st-card', hidden: true }, h('h2', {}, 'Values'), vals);
    const code = h('div', { class: 'st-code', 'aria-label': 'Algorithm' });
    const bCode = h('button', { class: 'st-link', 'aria-expanded': 'false', title: 'Code (C)' }, 'Show the code');
    const codeCard = h('section', { class: 'st-card st-codecard' }, h('div', { class: 'st-cardh' }, h('h2', {}, 'Code'), bCode), code);
    const side = h('aside', { class: 'st-side' }, valsCard, codeCard);
    // ---- present mode: the board fills the screen
    const pTools = h('div', { class: 'st-ptools' },
      h('button', { class: 'st-pbtn', onclick: () => toggleEditor(editor.hidden) }, 'Setup', h('kbd', {}, 'S')),
      h('button', { class: 'st-pbtn', onclick: () => toggleCode(!root.classList.contains('show-code')) }, 'Code', h('kbd', {}, 'C')),
      h('button', { class: 'st-pbtn', onclick: () => togglePresent(false) }, 'Exit', h('kbd', {}, 'Esc')));
    root.append(editor, h('main', { class: 'st-main' }, h('div', { class: 'st-left' }, board, controls), side), pTools);

    function toggleEditor(on) { editor.hidden = !on; bEdit.setAttribute('aria-expanded', String(on)); if (on) { const f = editor.querySelector('input, select'); if (f) f.focus(); } }
    function toggleCode(on) { root.classList.toggle('show-code', on); bCode.textContent = on ? 'Hide the code' : 'Show the code'; bCode.setAttribute('aria-expanded', String(on)); store.set('st-code', on ? '1' : '0'); }
    function togglePresent(on) {
      root.classList.toggle('present', on);
      try { if (on && root.requestFullscreen && window.parent === window) root.requestFullscreen().catch(() => {}); else if (!on && document.fullscreenElement) document.exitFullscreen(); } catch (e) {}
    }
    bEdit.onclick = () => toggleEditor(editor.hidden);
    bCode.onclick = () => toggleCode(!root.classList.contains('show-code'));
    bPresent.onclick = () => togglePresent(!root.classList.contains('present'));
    toggleCode(store.get('st-code') === '1');

    function values() { const o = {}; for (const f of cfg.inputs) o[f.id] = fields[f.id].value; return o; }
    function setValues(v) { for (const f of cfg.inputs) if (v[f.id] != null) fields[f.id].value = v[f.id]; }
    let timer = null;
    function schedule() { clearTimeout(timer); timer = setTimeout(recompute, 200); }
    function recompute() {
      stop();
      S.values = values();
      for (const id in errs) { errs[id].textContent = ''; fields[id].classList.remove('bad'); }
      const tr = cfg.run(S.values);
      if (tr.error) { const id = tr.error.field; if (id && errs[id]) { errs[id].textContent = tr.error.message; fields[id].classList.add('bad'); toggleEditor(true); }
        S.trace = null; view.textContent = ''; note.textContent = tr.error.message; checkLine.textContent = ''; summary.hidden = true; return; }
      S.trace = tr; S.k = 0; S.answered = {}; S.score = [0, 0]; S.lastAnswer = null;
      slider.max = tr.steps.length - 1; share(cfg, S.values);
      const ck = cfg.check(S.values, tr);                       // shown only when it fails; the text stays for the checks
      checkLine.className = 'st-check ' + (ck.ok ? 'ok' : 'bad');
      checkLine.innerHTML = (ck.ok ? '<b>✓ Checked:</b> ' : '<b>⚠ Check failed:</b> ') + ck.text;
      summary.innerHTML = tr.summary || '';
      show();
    }
    function codeLines() { return typeof cfg.code === 'function' ? cfg.code(S.values) : cfg.code; }
    function show() {
      const tr = S.trace; if (!tr) return;
      const st = tr.steps[S.k], last = tr.steps.length - 1;
      (cfg.render || renderView)(view, st, S.k, tr, S.values, vals);
      valsCard.hidden = !vals.childElementCount;
      code.replaceChildren(...codeLines().map((l, i) => h('div', { class: st.line === i + 1 ? 'on' : '' }, h('span', { class: 'ln' }, i + 1), l)));
      slider.value = S.k; pos.textContent = `Step ${S.k} of ${last}`;
      bBack.disabled = S.k === 0;
      const next = tr.steps[S.k + 1];
      const asking = S.predict && next && next.ask && !(S.k + 1 in S.answered);
      note.replaceChildren(h('p', { class: 'st-say' }, st.note || ''));
      if (S.lastAnswer && S.lastAnswer.k === S.k) note.append(h('p', { class: 'st-ask ' + (S.lastAnswer.right ? 'right' : 'wrong') }, S.lastAnswer.text));
      if (asking) {
        note.append(h('div', { class: 'st-ask' }, h('p', { class: 'st-q' }, next.ask.q),
          h('div', { class: 'opts' }, ...next.ask.options.map(o => h('button', { class: 'st-opt', onclick: () => answer(o) }, String(o))),
            h('button', { class: 'st-opt skip', onclick: () => answer(null) }, 'Skip'))));
      }
      bNext.disabled = S.k === last || asking;
      bNext.textContent = asking ? 'Answer to go on' : S.k === last ? 'Done' : 'Next ▶';
      summary.hidden = S.k !== last || !tr.summary;          // the result only at the end: no spoilers
      const [r, t] = S.score; if (t) pos.textContent += ` · predictions ${r}/${t}`;
    }
    function answer(o) {
      const next = S.trace.steps[S.k + 1]; S.answered[S.k + 1] = true;
      if (o !== null) { const right = String(o) === String(next.ask.answer); S.score[1]++; if (right) S.score[0]++;
        S.lastAnswer = { k: S.k + 1, right, text: (right ? '✓ Right. ' : `✗ Not quite: it is ${next.ask.answer}. `) + (next.ask.why || '') }; }
      else S.lastAnswer = null;
      go(S.k + 1);
    }
    function go(k) { if (!S.trace) return; S.k = Math.max(0, Math.min(S.trace.steps.length - 1, k)); show(); }
    function stop() { clearInterval(S.playing); S.playing = null; bPlay.textContent = '▶ Play'; }
    function toEnd() { stop(); S.predict = false; predictBox.checked = false; go(Infinity); }
    bBack.onclick = () => { stop(); go(S.k - 1); };
    bNext.onclick = () => go(S.k + 1);
    bPlay.onclick = () => { if (S.playing) return stop(); bPlay.textContent = '❚❚ Pause';
      S.playing = setInterval(() => { if (!S.trace || S.k >= S.trace.steps.length - 1 || bNext.disabled) return stop(); go(S.k + 1); }, cfg.playMs || 900); };
    slider.oninput = () => { stop(); S.predict = false; predictBox.checked = false; go(+slider.value); };
    predictBox.onchange = () => { S.predict = predictBox.checked; show(); };
    preset.onchange = () => { if (preset.value !== 'own') { setValues(cfg.presets[+preset.value].values); recompute(); } else toggleEditor(true); };
    document.addEventListener('keydown', ev => {
      if (ev.key === 'Escape') { if (!editor.hidden) toggleEditor(false); else if (root.classList.contains('present')) togglePresent(false); return; }
      if (/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName) || ev.ctrlKey || ev.metaKey || ev.altKey) return;
      if (ev.key === 'ArrowRight' && !bNext.disabled) { ev.preventDefault(); go(S.k + 1); }
      else if (ev.key === 'ArrowLeft') { ev.preventDefault(); stop(); go(S.k - 1); }
      else if (ev.key === 'Home') { stop(); go(0); } else if (ev.key === 'End') toEnd();
      else if (ev.key === ' ') { ev.preventDefault(); bPlay.onclick(); }
      else if (ev.key === 'p' || ev.key === 'P') togglePresent(!root.classList.contains('present'));
      else if (ev.key === 'c' || ev.key === 'C') toggleCode(!root.classList.contains('show-code'));
      else if ((ev.key === 's' || ev.key === 'S') && root.classList.contains('present')) toggleEditor(editor.hidden);
    });
    const fromLink = readHash();
    if (fromLink) {
      setValues(fromLink);
      const pi = (cfg.presets || []).findIndex(x => cfg.inputs.every(f => String(x.values[f.id]) === String(fields[f.id].value)));
      preset.value = pi >= 0 ? String(pi) : 'own';
    } else if (cfg.presets && cfg.presets.length) setValues(cfg.presets[0].values);
    recompute();
    return { S, go, toEnd, recompute, values, setValues, fields, toggleCode, togglePresent, toggleEditor };
  }
  window.Stepper = { mount, h, renderView, widgets: Object.keys(WIDGETS), figures: FIGURES, marks: MARKS };
})();
