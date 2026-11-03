// An example recipe for the stepper engine: binary search. Recipes are what the auto-build writes (README.md, "Recipes");
// this one is written by hand, shown to the AI as the model to follow, and run through the same automatic checks in the tests.
const recipe = {
  title: 'Binary search, step by step',
  summary: 'Type a sorted list and a value; step through how binary search halves the range and predict which half it keeps.',
  topics: ['binary search', 'searching a sorted array', 'divide and conquer', 'logarithmic time'],
  checked_by: 'a straight left-to-right scan of the list, and the number of comparisons against floor(log2 n) + 1',
  intro: 'Binary search finds a value in a sorted list by looking at the middle and throwing away the half that cannot contain it.',
  inputs: [
    { id: 'list', label: 'Sorted list (numbers separated by spaces)', kind: 'text', mono: true, help: 'Up to 20 whole numbers, smallest first.' },
    { id: 'target', label: 'Value to find', kind: 'number' },
  ],
  presets: [
    { name: 'Found after three looks', values: { list: '2 5 8 12 16 23 38 56 72 91', target: '23' } },
    { name: 'Not in the list', values: { list: '1 3 5 7 9 11', target: '4' } },
  ],
  code: [
    'lo = 0, hi = n - 1',
    'while lo <= hi:',
    '    mid = (lo + hi) // 2',
    '    if a[mid] == target: return mid',
    '    if a[mid] < target: lo = mid + 1',
    '    else: hi = mid - 1',
    'return "not found"',
  ],
  parse(values) {                           // input checking, shared by run and check (not part of the algorithm)
    const a = String(values.list || '').trim().split(/\s+/).filter(Boolean).map(Number);
    if (!a.length || a.some(x => !Number.isInteger(x))) return { error: { field: 'list', message: 'Type whole numbers separated by spaces.' } };
    if (a.length > 20) return { error: { field: 'list', message: 'At most 20 numbers.' } };
    if (a.some((x, i) => i && x < a[i - 1])) return { error: { field: 'list', message: 'The list must be sorted, smallest first.' } };
    const t = Number(values.target);
    if (!Number.isInteger(t)) return { error: { field: 'target', message: 'Type a whole number.' } };
    return { a, t };
  },
  run(values) {
    const p = recipe.parse(values);
    if (p.error) return p;
    const { a, t } = p, steps = [];
    const view = (lo, hi, mid, extra) => {
      const marks = {};
      a.forEach((_, i) => { if (i < lo || i > hi) marks[i] = 'muted'; });
      if (mid != null) marks[mid] = extra || 'compare';
      const pointers = { lo, hi };
      if (mid != null) pointers.mid = mid;
      return [{ type: 'array', label: 'The list', items: a, marks, pointers },
              { type: 'vars', label: 'Variables', values: { lo, hi, mid: mid == null ? '-' : mid, target: t } }];
    };
    let lo = 0, hi = a.length - 1, looks = 0, found = -1;
    steps.push({ line: 1, note: `Search the whole list: lo = 0, hi = ${hi}.`, view: view(lo, hi, null) });
    while (lo <= hi) {
      const mid = Math.floor((lo + hi) / 2);
      looks++;
      const keep = a[mid] === t ? 'found' : a[mid] < t ? 'right half' : 'left half';
      steps.push({ line: 3, note: `The middle of positions ${lo}..${hi} is ${mid}; a[${mid}] = ${a[mid]}.`, view: view(lo, hi, mid),
                   ask: { q: `Looking for ${t}: what happens next?`, options: ['found', 'left half', 'right half'], answer: keep,
                          why: a[mid] === t ? `a[${mid}] is ${t}.` : `${a[mid]} is ${a[mid] < t ? 'smaller' : 'larger'} than ${t}, so ${t} can only be to the ${a[mid] < t ? 'right' : 'left'}.` } });
      if (a[mid] === t) { found = mid; steps.push({ line: 4, note: `Found ${t} at position ${mid} after ${looks} look${looks === 1 ? '' : 's'}.`, view: view(lo, hi, mid, 'done') }); break; }
      if (a[mid] < t) { lo = mid + 1; steps.push({ line: 5, note: `${a[mid]} < ${t}: keep the right half, lo = ${lo}.`, view: view(lo, hi, null) }); }
      else { hi = mid - 1; steps.push({ line: 6, note: `${a[mid]} > ${t}: keep the left half, hi = ${hi}.`, view: view(lo, hi, null) }); }
    }
    if (found < 0) steps.push({ line: 7, note: `lo (${lo}) passed hi (${hi}): ${t} is not in the list. ${looks} look${looks === 1 ? '' : 's'}.`, view: view(lo, hi, null) });
    return { steps, summary: found >= 0 ? `<b>${t}</b> is at position ${found}; binary search looked ${looks} times (a scan would look ${found + 1} times).`
                                        : `<b>${t}</b> is not in the list; binary search looked ${looks} times (a scan looks ${a.length} times).`,
             result: { index: found, looks } };
  },
  check(values, trace) {                    // independent: a plain scan, and the worst-case number of looks
    const p = recipe.parse(values);
    if (p.error) return { ok: false, text: p.error.message };
    const { a, t } = p, r = trace.result || {};
    const present = a.includes(t);
    const okIndex = present ? (r.index >= 0 && a[r.index] === t) : r.index === -1;
    const okLooks = Number.isInteger(r.looks) && r.looks >= 1 && r.looks <= Math.floor(Math.log2(a.length)) + 1;
    return { ok: okIndex && okLooks, text: okIndex && okLooks ? `a left-to-right scan agrees (${present ? 'found at ' + r.index : 'not present'}), and ${r.looks} looks is within log2(n) + 1.`
                                                          : `the scan says ${present ? 'found' : 'not present'}; binary search gave position ${r.index} after ${r.looks} looks.` };
  },
  examples: [                               // textbook answers, worked out by hand
    { values: { list: '2 5 8 12 16 23 38 56 72 91', target: '23' }, result: { index: 5, looks: 3 } },
    { values: { list: '1 3 5 7 9 11', target: '4' }, result: { index: -1, looks: 3 } },
    { values: { list: '7', target: '7' }, result: { index: 0, looks: 1 } },
  ],
  random(rng) {                             // a valid random input, for the automatic checks
    const n = 1 + Math.floor(rng() * 16), a = [];
    let x = Math.floor(rng() * 5);
    for (let i = 0; i < n; i++) { a.push(x); x += 1 + Math.floor(rng() * 6); }
    const t = rng() < 0.6 ? a[Math.floor(rng() * n)] : Math.floor(rng() * (x + 3));
    return { list: a.join(' '), target: String(t) };
  },
};
