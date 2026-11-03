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
        w.bars ? h('div', { class: 'sv-bar', style: 'height:' + Math.max(4, Math.round(90 * Math.abs(+v || 0) / max)) + 'px' }) : null,
        h('div', { class: 'sv-val' }, fmt(v)), h('div', { class: 'sv-idx' }, i), ptr[i] ? h('div', { class: 'sv-ptr' }, ptr[i].join(' ')) : null)),
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
  };
  function renderView(view, st) {
    const ws = Array.isArray(st && st.view) ? st.view : [];
    view.replaceChildren(...ws.map(w => h('section', { class: 'sv-w' }, w && w.label ? h('div', { class: 'sv-label' }, w.label) : null,
      w && WIDGETS[w.type] ? WIDGETS[w.type](w) : h('p', { class: 'sv-text' }, 'Unknown view: ' + (w && w.type)))));
  }

  function mount(cfg) {
    const S = { values: {}, trace: null, k: 0, playing: null, predict: true, answered: {}, score: [0, 0] };
    const root = document.body;
    root.append(h('header', { class: 'st-head' }, h('h1', {}, cfg.title), h('p', {}, cfg.intro)));
    const view = h('div', { class: 'st-view', 'aria-live': 'polite' });
    const note = h('div', { class: 'st-note', 'aria-live': 'polite' });
    const slider = h('input', { type: 'range', min: 0, max: 0, value: 0, 'aria-label': 'Step' });
    const pos = h('span', { class: 'st-pos' });
    const bFirst = h('button', { 'aria-label': 'First step', title: 'First step (Home)' }, '⏮');
    const bBack = h('button', { 'aria-label': 'Previous step', title: 'Previous step (←)' }, '◀ Back');
    const bNext = h('button', { class: 'primary', 'aria-label': 'Next step', title: 'Next step (→)' }, 'Next ▶');
    const bLast = h('button', { 'aria-label': 'Last step', title: 'Last step (End)' }, '⏭');
    const bPlay = h('button', { title: 'Play (space)' }, '▶ Play');
    const checkLine = h('div', { class: 'st-check' });
    const stage = h('section', { class: 'st-stage' }, view, note, h('div', { class: 'st-bar' }, bFirst, bBack, bNext, bLast, bPlay, slider, pos), checkLine);
    const preset = h('select', { id: 'st-preset', 'aria-label': 'Example' });
    (cfg.presets || []).forEach((p, i) => preset.append(h('option', { value: i }, p.name)));
    preset.append(h('option', { value: 'own' }, 'Your own'));
    const fields = {}, errs = {};
    const inputsBox = h('div', {});
    for (const f of cfg.inputs) {
      let inp;
      if (f.kind === 'select') { inp = h('select', { id: 'st-' + f.id }); f.options.forEach(([v, l]) => inp.append(h('option', { value: v }, l))); }
      else inp = h('input', { id: 'st-' + f.id, type: f.kind === 'number' ? 'number' : 'text', class: f.mono ? 'mono' : '', min: f.min, max: f.max, step: f.step, spellcheck: 'false', autocomplete: 'off' });
      fields[f.id] = inp; errs[f.id] = h('div', { class: 'st-err' });
      inputsBox.append(...[h('label', { for: 'st-' + f.id }, f.label), inp, f.help ? h('div', { class: 'st-help' }, f.help) : null, errs[f.id]].filter(Boolean));
      inp.addEventListener(f.kind === 'select' ? 'change' : 'input', () => { preset.value = 'own'; schedule(); });
    }
    const predictBox = h('input', { type: 'checkbox', id: 'st-predict', checked: true });
    const code = h('div', { class: 'st-code', 'aria-label': 'Algorithm' });
    const summary = h('div', { class: 'st-summary' });
    const panel = h('aside', { class: 'st-panel' },
      h('h2', {}, 'Input'), h('label', { for: 'st-preset' }, 'Example'), preset, inputsBox,
      h('div', { class: 'st-row' }, predictBox, h('label', { for: 'st-predict', style: 'margin:0' }, 'Ask me to predict before showing the answer')),
      h('h2', {}, 'Algorithm'), code, h('h2', {}, 'Summary'), summary);
    root.append(h('div', { class: 'st-layout' }, stage, panel));

    function values() { const o = {}; for (const f of cfg.inputs) o[f.id] = fields[f.id].value; return o; }
    function setValues(v) { for (const f of cfg.inputs) if (v[f.id] != null) fields[f.id].value = v[f.id]; }
    let timer = null;
    function schedule() { clearTimeout(timer); timer = setTimeout(recompute, 200); }
    function recompute() {
      stop();
      S.values = values();
      for (const id in errs) { errs[id].textContent = ''; fields[id].classList.remove('bad'); }
      const tr = cfg.run(S.values);
      if (tr.error) { const id = tr.error.field; if (id && errs[id]) { errs[id].textContent = tr.error.message; fields[id].classList.add('bad'); }
        S.trace = null; view.textContent = ''; note.textContent = tr.error.message; checkLine.textContent = ''; return; }
      S.trace = tr; S.k = 0; S.answered = {}; S.score = [0, 0];
      slider.max = tr.steps.length - 1; share(cfg, S.values);
      const ck = cfg.check(S.values, tr);
      checkLine.className = 'st-check ' + (ck.ok ? 'ok' : 'bad');
      checkLine.innerHTML = (ck.ok ? '<b>✓ Checked:</b> ' : '<b>⚠ Check failed:</b> ') + ck.text;
      summary.innerHTML = tr.summary || '';
      show();
    }
    function codeLines() { return typeof cfg.code === 'function' ? cfg.code(S.values) : cfg.code; }
    function show() {
      const tr = S.trace; if (!tr) return;
      const st = tr.steps[S.k];
      (cfg.render || renderView)(view, st, S.k, tr, S.values);
      code.replaceChildren(...codeLines().map((l, i) => h('div', { class: st.line === i + 1 ? 'on' : '' }, h('span', { class: 'ln' }, i + 1), l)));
      slider.value = S.k; pos.textContent = `Step ${S.k} of ${tr.steps.length - 1}`;
      bFirst.disabled = bBack.disabled = S.k === 0; bLast.disabled = S.k === tr.steps.length - 1;
      const next = tr.steps[S.k + 1];
      const asking = S.predict && next && next.ask && !(S.k + 1 in S.answered);
      note.replaceChildren(st.note || '');
      if (asking) {
        const box = h('div', { class: 'st-ask' }, h('b', {}, 'Predict: '), next.ask.q);
        const opts = h('div', { class: 'opts' }, ...next.ask.options.map(o => h('button', { onclick: () => answer(o) }, String(o))), h('button', { onclick: () => answer(null) }, 'Skip'));
        box.append(opts); note.append(box);
      }
      bNext.disabled = S.k === tr.steps.length - 1 || asking;
      if (S.lastAnswer && S.lastAnswer.k === S.k) note.append(h('div', { class: 'st-ask ' + (S.lastAnswer.right ? 'right' : 'wrong') }, S.lastAnswer.text));
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
    bFirst.onclick = () => { stop(); go(0); }; bBack.onclick = () => { stop(); go(S.k - 1); };
    bNext.onclick = () => go(S.k + 1); bLast.onclick = () => { stop(); S.predict = false; predictBox.checked = false; go(Infinity); };
    bPlay.onclick = () => { if (S.playing) return stop(); bPlay.textContent = '❚❚ Pause';
      S.playing = setInterval(() => { if (!S.trace || S.k >= S.trace.steps.length - 1 || bNext.disabled) return stop(); go(S.k + 1); }, cfg.playMs || 900); };
    slider.oninput = () => { stop(); S.predict = false; predictBox.checked = false; go(+slider.value); };
    predictBox.onchange = () => { S.predict = predictBox.checked; show(); };
    preset.onchange = () => { if (preset.value !== 'own') { setValues(cfg.presets[+preset.value].values); recompute(); } };
    document.addEventListener('keydown', ev => {
      if (/INPUT|SELECT|TEXTAREA/.test(document.activeElement.tagName)) return;
      if (ev.key === 'ArrowRight' && !bNext.disabled) { ev.preventDefault(); go(S.k + 1); }
      else if (ev.key === 'ArrowLeft') { ev.preventDefault(); stop(); go(S.k - 1); }
      else if (ev.key === 'Home') { stop(); go(0); } else if (ev.key === 'End') bLast.onclick();
      else if (ev.key === ' ') { ev.preventDefault(); bPlay.onclick(); }
    });
    const fromLink = readHash();
    if (fromLink) {
      setValues(fromLink);
      const pi = (cfg.presets || []).findIndex(x => cfg.inputs.every(f => String(x.values[f.id]) === String(fields[f.id].value)));
      preset.value = pi >= 0 ? String(pi) : 'own';
    } else if (cfg.presets && cfg.presets.length) setValues(cfg.presets[0].values);
    recompute();
    return { S, go, recompute, values, setValues, fields };
  }
  window.Stepper = { mount, h, renderView, widgets: Object.keys(WIDGETS), marks: MARKS };
})();
