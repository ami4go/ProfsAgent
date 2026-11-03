# Stepper engine (type 1: step-through processes)

The engine gives every step-through simulation the same controls and behaviour:
- Back, Next, ⏮, ⏭, Play, a step slider and keyboard keys (← → Home End Space);
- the algorithm's code with the current line highlighted;
- **predict-the-next-step** questions, with a score;
- the live **independent check** line;
- **a shareable link**: the inputs sit after `#`, so a link reproduces the state;
- **class examples in the app**: with `../_engines/share/share.js` loaded before the engine, every change of the inputs is also sent to the ProfsAgent app, which can keep it as a professor's class example;
- a dark, phone-friendly layout that works offline with no libraries.

A simulation supplies only its algorithm, its drawing and its check. The first one is `os.memory.page_replacement`.

```html
<link rel="stylesheet" href="../_engines/stepper/stepper.css">
<script src="../_engines/share/share.js"></script>      <!-- optional: lets the app keep a class example -->
<script src="../_engines/stepper/stepper.js"></script>
<script>
const api = Stepper.mount({
  title, intro,                                   // header text
  inputs: [{ id, label, kind: 'text' | 'number' | 'select', options: [[value, label]], min, max, step, mono, help }],
  presets: [{ name, values: { <input id>: value } }],
  code: ['line 1', ...]  or  values => [...],    // shown with line numbers; a step's `line` (1-based) is highlighted
  run(values) {                                   // the algorithm: returns the trace, or { error: { field, message } }
    return { steps: [{ line, note, ask: { q, options, answer, why } }], summary: '<html>', ...anything render needs };
  },
  render(view, step, k, trace, values) { },       // draw step k into the view element
  check(values, trace) { return { ok, text }; },  // an INDEPENDENT second implementation; shown under the controls
  playMs: 900,                                    // optional: Play speed
  describe(values) { return 'plain one-line summary'; },   // optional: how the app names the setup (default: label: value · ...)
});
</script>
```

- `ask` on a step makes the engine stop before that step and ask the question. The answer is checked against `answer`, and `why` is shown afterwards.
- `Stepper.h(tag, attrs, ...children)` is a small helper for building elements in `render`.
- `scripts/sims.py build` inlines `stepper.css` and `stepper.js` into the page, so the result is one offline file.
- `render` is optional: without it, the engine draws each step's `view` with its ready-made widgets (below).

## Recipes (what the auto-build writes)

A **recipe** is one plain JavaScript object, `const recipe = { ... };`, that the engine mounts. It never draws anything itself: every step lists **widgets** that describe what is on screen, and the engine draws them. The auto-build (`src/profsagent/sims/autobuild.py`) asks an AI for a recipe and accepts it only if `qa_recipe.py` passes. `example_recipe.js` (binary search) is a complete example.

**Fields:**
- `title`: a short title.
- `summary`: one line on what students do.
- `topics`: 2–8 topic names.
- `intro`: 1–2 plain sentences.
- `checked_by`: one line on how `check` works the answer out independently.
- `inputs`: `[{id, label, kind: 'text' | 'number' | 'select', options: [[value, label]], min, max, step, mono, help}]`. Values always arrive as **strings**.
- `presets`: at least 2 `{name, values}`. Give every input a value, as a string.
- `code`: the algorithm as short pseudocode lines, shown with line numbers.
- `run(values)` returns `{steps, summary, result}`, or `{error: {field, message}}` for an input it cannot use.
  - `steps`: 1–500 `{line, note, view, ask}`.
    - `line`: the 1-based line of `code` being done.
    - `note`: one plain sentence.
    - `view`: the widgets.
    - `ask` (optional): `{q, options, answer, why}`, where `answer` is one of `options`.
  - `summary`: short HTML (`b`, `i`, `br`, `table`) shown after the run.
  - `result`: the final answer as JSON (a number, string, list or small object). The checks compare it.
- `check(values, trace)` returns `{ok, text}`. It works out `trace.result` again by a **different method**, and must never call `run`. `text` says what was compared.
- `examples`: at least 2 `{values, result}`: textbook answers worked out by hand. `run` must return exactly that `result`.
- `random(rng)` returns valid random `values`. `rng()` gives a number in [0, 1); the checks try 40 random inputs.
- **Helpers:** extra functions may be added as properties (for example `parse`) and called as `recipe.parse(...)`. Input parsing may be shared by `run` and `check`; the algorithm may not.

**Widgets** (a step's `view` is a list of them; each may have a `label`):

| `type` | Fields |
|---|---|
| `array` | `items: [...]`, `marks: {index: mark}`, `pointers: {name: index}`, `bars: true` (draw the values as bars) |
| `stacks` | `stacks: [{name, items: [bottom … top], marks: {index: mark}, mark}]`, `disks: true` (item width grows with its value) |
| `callstack` | `frames: ['hanoi(3, A, C, B)', …]`; the last frame is the one running |
| `vars` | `values: {name: value}`, `marks: {name: mark}` |
| `table` | `columns: [...]`, `rows: [[...]]`, `marks: {"row,col": mark}` |
| `text` | `text`, `mark` |
| `plot` | `x: [min, max]`, `y: [min, max]`, `points: [{x, y, mark, label}]` (or `[x, y]`), `lines: [{points: [[x, y], …], mark, label}]`, `shapes: [{kind: 'circle', cx, cy, r} \| {kind: 'rect', x, y, w, h} \| {kind: 'segment', x1, y1, x2, y2}]` (each with an optional `mark`), `xlabel`, `ylabel`, `equal: true` (same scale on both axes) |
| `graph` | `nodes: [{id, label, mark, x, y}]` (x, y in 0..1; without them the nodes sit on a circle), `edges: [{from, to, label, mark}]`, `directed: true` |
| `grid` | `cells: [[…], …]` (rows of equal length, at most 40 × 40), `marks: {"row,col": mark}`, `heat: true` (shade numbers by size), `hide_values: true` |

**Every step must show a figure:** at least one `array`, `stacks`, `plot`, `graph` or `grid` widget. A `table`, `vars` or
`text` may sit beside the figure, never instead of it; a page of tables is not a simulation. Pick the figure that shows
the idea: `plot` for sampling, geometry, functions and convergence (for example, Monte Carlo points in the square with
the circle as a shape, and the running estimate as a line in a second plot); `graph` for networks, trees and state
machines; `grid` for matrices, mazes, dynamic programming and cellular automata; `array` with bars for sorting;
`stacks` for stacks and Tower of Hanoi.

**Marks:** `active` (yellow), `compare` (blue), `swap` (red), `done` (green), `min` (purple), `muted` (faded).
For a random process, put a small seeded generator (for example mulberry32) in a helper, so `run` stays deterministic
and the same seed always gives the same points; allow enough samples (for example up to 500, in batches per step) for
the idea to show. Random points cannot be worked out by hand, so give such a recipe an optional text input that lists a
few points explicitly (for example `0.1,0.2 0.9,0.8 0.5,0.5`; empty means "use the seeded generator"), and write the
`examples` with listed points, whose result you can work out by hand.

**Rules:**
- Use plain JavaScript only: no libraries, no network, no `document` or `window`, no `eval`, no storage.
- `run` must be deterministic.
- Keep inputs small (for example, at most 20 items), so a run stays under 500 steps.
