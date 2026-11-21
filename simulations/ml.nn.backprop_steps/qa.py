"""Automatic checks of the backpropagation page (Chrome, network blocked).
    python simulations/ml.nn.backprop_steps/qa.py [page.html] [screenshot folder]
(scripts/sims.py qa builds the single-file page first and passes it here)

1. The page's numbers against a NumPy implementation written here (matrices, not the page's loops): forward pass, every
   backward quantity, the centred finite differences, the kink flags, the pass/fail verdicts, the SGD step and the new
   loss, on 600 random inputs and weights (mini-batches of 1-4), to 1e-9.
2. Closed-form cases worked by hand: equal scores (P = 1/2, L = ln 2, every gradient +-1/2, the loss after one step
   log(1 + e^-6)); scores ln 3 and 0 (P = 3/4, L = ln 4/3, dW1 = -ln3/4); a conflicting pair (zero gradient); a dead
   unit (exact zeros); a ReLU kink (the centred difference is half the one-sided slope, relative error 1).
3. Gradient descent: for a small learning rate the loss goes down by about lr * |g|^2.
4. The predict questions: every answer the page expects, on every preset and on the random inputs, against NumPy.
5. The page's own independent check (forward-mode dual numbers) passes everywhere and rejects corrupted traces.
6. The page: every preset steps to its end; questions stop the steps and are marked; keyboard (arrows, Home, End,
   C for code with the right line lit, P and Esc); it fits 1440x900 and 1280x720 with nothing scrolling, at every stage,
   with a question showing and with the code open; the link and the class example; bad input; phone; offline."""
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
from playwright.sync_api import sync_playwright

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
PAGE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent / "_build" / f"{HERE.name}.html"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "_build" / "qa" / HERE.name
OUT.mkdir(parents=True, exist_ok=True)
problems = []
THRESHOLD, TINY, BOTH_ZERO = 1e-5, 1e-12, 1e-9


def expect(cond, msg):
    print(("ok: " if cond else "PROBLEM: ") + msg, flush=True)
    if not cond:
        problems.append(msg)


# ------------------------------------------------------------------ the NumPy reference
def unpack(v):
    X = [[float(v["x1"]), float(v["x2"])]]
    y = [int(v["y"]) - 1]
    for r in [r for r in v.get("more", "").split(";") if r.strip()]:
        a, b, c = r.split()
        X.append([float(a), float(b)])
        y.append(int(float(c)) - 1)
    m = lambda s: np.array([[float(x) for x in row.split()] for row in s.split(";")])  # noqa: E731
    return dict(X=np.array(X), y=np.array(y), W1=m(v["W1"]), b1=np.array([float(x) for x in v["b1"].split()]),
                W2=m(v["W2"]), b2=np.array([float(x) for x in v["b2"].split()]), lr=float(v["lr"]), eps=float(v["eps"]))


def forward(P):
    Z1 = P["X"] @ P["W1"] + P["b1"]
    H = np.maximum(Z1, 0.0)
    Z2 = H @ P["W2"] + P["b2"]
    lse = np.log(np.exp(Z2 - Z2.max(1, keepdims=True)).sum(1)) + Z2.max(1)
    Pr = np.exp(Z2 - lse[:, None])
    L = float(np.mean(lse - Z2[np.arange(len(P["y"])), P["y"]]))
    return dict(Z1=Z1, H=H, Z2=Z2, P=Pr, L=L)


NAMES = [("W1", 0, 0), ("W1", 0, 1), ("W1", 1, 0), ("W1", 1, 1), ("b1", 0), ("b1", 1),
         ("W2", 0, 0), ("W2", 0, 1), ("W2", 1, 0), ("W2", 1, 1), ("b2", 0), ("b2", 1)]


def nudge(P, q, d):
    Q = {k: (v.copy() if isinstance(v, np.ndarray) else v) for k, v in P.items()}
    Q[q[0]][q[1:]] = Q[q[0]][q[1:]] + d
    return Q


def reference(v):
    P = unpack(v)
    f = forward(P)
    B = len(P["y"])
    Y = np.eye(2)[P["y"]]
    g = {"dZ2": (f["P"] - Y) / B}
    g["dW2"] = f["H"].T @ g["dZ2"]
    g["db2"] = g["dZ2"].sum(0)
    g["dH"] = g["dZ2"] @ P["W2"].T
    g["M"] = (f["Z1"] > 0).astype(float)
    g["dZ1"] = g["dH"] * g["M"]
    g["dW1"] = P["X"].T @ g["dZ1"]
    g["db1"] = g["dZ1"].sum(0)
    grads = np.array([g["d" + q[0]][q[1:]] for q in NAMES])
    fd = []
    for i, q in enumerate(NAMES):
        Pp, Pm = nudge(P, q, P["eps"]), nudge(P, q, -P["eps"])
        Lp, Lm = forward(Pp)["L"], forward(Pm)["L"]
        n = (Lp - Lm) / (2 * P["eps"])
        a = grads[i]
        rel = abs(a - n) / max(abs(a) + abs(n), TINY)
        kink = bool(((forward(Pp)["Z1"] > 0) != g["M"].astype(bool)).any() or ((forward(Pm)["Z1"] > 0) != g["M"].astype(bool)).any())
        tiny = abs(a) + abs(n) < BOTH_ZERO
        fd.append(dict(num=n, rel=rel, kink=kink, tiny=tiny, ok=rel < THRESHOLD or tiny))
    P2 = dict(P)
    for k in ("W1", "b1", "W2", "b2"):
        P2[k] = P[k] - P["lr"] * g["d" + k]
    f2 = forward(P2)
    return dict(P=P, f=f, g=g, grads=grads, fd=fd, P2=P2, L2=f2["L"], gnorm2=float((grads ** 2).sum()))


def answers(r):
    """The predict answers, worked out from the NumPy numbers."""
    f, g, P = r["f"], r["g"], r["P"]
    z = f["Z2"][0]
    a = ["a tie (50/50)" if abs(z[0] - z[1]) < 1e-12 else ("class 1" if f["P"][0][0] > f["P"][0][1] else "class 2")]
    sign = lambda x: "zero" if abs(x) < 1e-12 else "positive" if x > 0 else "negative"  # noqa: E731   (0 up to rounding counts as 0)
    a.append(sign(g["dZ2"][0][P["y"][0]]))
    off1 = [j for j in (0, 1) if f["Z1"][0][j] <= 0]
    a.append({0: "neither", 2: "both"}.get(len(off1), f"unit {off1[0] + 1}" if off1 else ""))
    off_all = [j for j in (0, 1) if (f["Z1"][:, j] <= 0).all()]
    a.append(sign(g["dW1"][0][off_all[0] if off_all else 0]))
    a.append("yes" if all(x["ok"] for x in r["fd"]) else "no")
    a.append("down" if r["L2"] <= r["f"]["L"] else "up")
    return a


def close(a, b, tol=1e-9):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return bool(np.all(np.abs(a - b) <= tol * np.maximum(1.0, np.abs(b))))


# ------------------------------------------------------------------ inputs
def values(x1, x2, y, W1, b1, W2, b2, lr="0.5", eps="1e-5", more=""):
    return dict(x1=str(x1), x2=str(x2), y=str(y), more=more, W1=W1, b1=b1, W2=W2, b2=b2, lr=str(lr), eps=str(eps))


def rand_values(rnd):
    w = lambda: repr(round(rnd.uniform(-1.6, 1.6), rnd.choice([1, 2, 6, 17])))  # noqa: E731
    B = rnd.choice([1, 1, 2, 3, 4])
    more = "; ".join(f"{w()} {w()} {rnd.choice([1, 2])}" for _ in range(B - 1))
    return values(w(), w(), rnd.choice([1, 2]), f"{w()} {w()}; {w()} {w()}", f"{w()} {w()}", f"{w()} {w()}; {w()} {w()}", f"{w()} {w()}",
                  rnd.choice(["0.01", "0.1", "0.5", "1", "3"]), rnd.choice(["1e-4", "1e-5", "1e-5", "1e-6"]), more)


COMPUTE = """vs => vs.map(v => { const c = window.__bp.compute(v); if (c.error) return { error: c.error };
  const t = window.__bp.run(v);
  return { Z1: c.f.Z1, H: c.f.H, Z2: c.f.Z2, P: c.f.P, L: c.f.L, dZ2: c.g.dZ2, dW2: c.g.dW2, db2: c.g.db2, dH: c.g.dH, M: c.g.M, dZ1: c.g.dZ1,
    dW1: c.g.dW1, db1: c.g.db1, fd: c.gc.map(r => ({ num: r.num, rel: r.rel, kink: r.kink, tiny: r.tiny, pass: r.pass })),
    W1n: c.p2.W1, b1n: c.p2.b1, W2n: c.p2.W2, b2n: c.p2.b2, L2: c.f2.L, steps: t.steps.length,
    asks: t.steps.filter(s => s.ask).map(s => ({ q: s.ask.q, answer: s.ask.answer, options: s.ask.options })),
    check: window.__bp.independentCheck(v, t) }; })"""


def compare(v, pg_out, ref, stats):
    """Problems (a list) between the page's numbers and the NumPy reference for one input."""
    bad = []
    f, g = ref["f"], ref["g"]
    for k in ("Z1", "H", "Z2", "P"):
        if not close(pg_out[k], f[k]):
            bad.append(k)
    if not close(pg_out["L"], f["L"]):
        bad.append("L")
    for k in ("dZ2", "dW2", "db2", "dH", "M", "dZ1", "dW1", "db1"):
        d = float(np.max(np.abs(np.asarray(pg_out[k], float) - g[k])))
        stats["grad"] = max(stats["grad"], d)
        if not close(pg_out[k], g[k]):
            bad.append(k)
    eps = ref["P"]["eps"]
    tol_fd = max(1e-9, 64 * 2.2e-16 * (1 + abs(f["L"])) / eps)        # rounding in L(θ+ε) − L(θ−ε) grows as 1/ε
    for i, (a, b) in enumerate(zip(pg_out["fd"], ref["fd"])):
        d = abs(a["num"] - b["num"])
        stats["fd"] = max(stats["fd"], d)
        if eps >= 1e-5:
            stats["fd_1e5"] = max(stats["fd_1e5"], d)
        if d > tol_fd:
            bad.append(f"finite difference {i}")
        if a["kink"] != b["kink"]:
            bad.append(f"kink flag {i}")
        clear = b["tiny"] or b["rel"] < THRESHOLD / 10 or b["rel"] > THRESHOLD * 10      # far from the threshold
        if clear and a["pass"] != b["ok"]:
            bad.append(f"verdict {i}")
        stats["verdicts"] += 1
        stats["unclear"] += not clear
    for k, rk in (("W1n", "W1"), ("b1n", "b1"), ("W2n", "W2"), ("b2n", "b2")):
        if not close(pg_out[k], ref["P2"][rk]):
            bad.append(k)
    if not close(pg_out["L2"], ref["L2"]):
        bad.append("L after the step")
    if [a["answer"] for a in pg_out["asks"]] != answers(ref):
        bad.append(f"predict answers {[a['answer'] for a in pg_out['asks']]} vs {answers(ref)}")
    if any(str(a["answer"]) not in map(str, a["options"]) for a in pg_out["asks"]):
        bad.append("an answer is not among its options")
    if not pg_out["check"]["ok"]:
        bad.append("the page's own check: " + pg_out["check"]["text"])
    return bad


def framed(b, page_uri, out_dir, net):
    """The page inside a frame, as in the ProfsAgent app; the outer page records what the page reports."""
    wrap = out_dir / "_framed.html"
    wrap.write_text('<!doctype html><meta charset="utf-8"><script>window.msgs = []; addEventListener("message", e => msgs.push(e.data));</script>'
                    f'<iframe id="f" style="width:1300px;height:850px;border:0" src="{page_uri}"></iframe>', encoding="utf-8")
    p = b.new_page(viewport={"width": 1400, "height": 900})
    p.route("http*://**", lambda r: (net.append(r.request.url), r.abort()))
    p.goto(wrap.as_uri())
    return p


LAST = "(() => { const m = msgs.filter(x => x && x.type === 'profsagent-sim-state'); return m.length ? m[m.length - 1] : null; })()"
STATE = """() => { const v = document.querySelector('.st-view'), s = document.querySelector('.st-side'), d = document.documentElement;
  return { doc: [d.scrollWidth, d.scrollHeight], view: [v.scrollWidth - v.clientWidth, v.scrollHeight - v.clientHeight],
           side: [s.scrollHeight - s.clientHeight], pos: document.querySelector('.st-pos').textContent,
           asking: !!document.querySelector('.st-note .opts') }; }"""

with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1440, "height": 900})
    errs, net = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
    pg.on("console", lambda m: errs.append(m.text[:300]) if m.type == "error" else None)
    pg.route("http*://**", lambda r: (net.append(r.request.url), r.abort()))
    pg.goto(PAGE.as_uri())
    pg.wait_for_function("window.__bp && window.__bp.api.S.trace")
    presets = pg.evaluate("window.__bp.api.S && Array.from(document.querySelectorAll('#st-preset option')).filter(o => o.value !== 'own').map(o => o.textContent)")
    preset_values = pg.evaluate("""() => { const sel = document.querySelector('#st-preset'), out = [];
        for (let i = 0; i < sel.options.length - 1; i++) { sel.value = String(i); sel.dispatchEvent(new Event('change')); out.push(window.__bp.api.values()); }
        sel.value = '0'; sel.dispatchEvent(new Event('change')); return out; }""")
    expect(len(preset_values) == 7, f"7 examples ({len(preset_values)}): {presets}")

    # ---- 1 + 4 + 5: random inputs and the presets against NumPy
    rnd = random.Random(20261111)
    cases = [("preset " + str(i + 1), v) for i, v in enumerate(preset_values)] + [(f"random {i + 1}", rand_values(rnd)) for i in range(600)]
    outs = []
    for k in range(0, len(cases), 100):
        outs += pg.evaluate(COMPUTE, [v for _, v in cases[k:k + 100]])
    stats = dict(grad=0.0, fd=0.0, fd_1e5=0.0, verdicts=0, unclear=0)
    bad_cases, batches, kinks, fails = [], {1: 0, 2: 0, 3: 0, 4: 0}, 0, 0
    for (name, v), o in zip(cases, outs):
        if "error" in o:
            bad_cases.append(f"{name}: refused {o['error']} for {v}")
            continue
        ref = reference(v)
        batches[len(ref["P"]["y"])] += 1
        kinks += any(x["kink"] for x in ref["fd"])
        fails += not all(x["ok"] for x in ref["fd"])
        bad = compare(v, o, ref, stats)
        if o["steps"] != 22:
            bad.append(f"{o['steps']} steps, expected 22")
        if bad:
            bad_cases.append(f"{name}: {bad[:4]} for {json.dumps(v)[:200]}")
    expect(not bad_cases, f"page vs NumPy on {len(cases)} inputs (7 presets + 600 random; batches of 1-4: {batches}): forward, backward, "
                          f"finite differences, kink flags, verdicts, SGD step, new loss, predict answers, live check"
           + ("" if not bad_cases else " -- " + " | ".join(bad_cases[:3])))
    print(f"   largest differences: gradients {stats['grad']:.1e}; finite differences {stats['fd']:.1e} (ε ≥ 1e-5: {stats['fd_1e5']:.1e}); "
          f"{stats['unclear']} of {stats['verdicts']} verdicts within 10x of the threshold (not compared); {kinks} inputs with a kink, {fails} with a failing check")
    expect(stats["fd_1e5"] <= 1e-9 and stats["grad"] <= 1e-12, f"to 1e-9: finite differences with ε ≥ 1e-5 differ by at most {stats['fd_1e5']:.1e}, gradients by {stats['grad']:.1e}")

    # the reference itself: NumPy backprop against NumPy central differences, where no kink is near
    worst = 0.0
    for _, v in cases[7:]:
        r = reference(v)
        if np.min(np.abs(r["f"]["Z1"])) > 1e-3:
            worst = max(worst, max(x["rel"] for x in r["fd"] if not x["tiny"]) if any(not x["tiny"] for x in r["fd"]) else 0)
    expect(worst < 1e-5, f"the NumPy reference passes its own finite-difference check (below 1e-5) away from kinks (worst relative error {worst:.1e})")

    # ---- 2: closed-form cases
    def page_numbers(v):
        return pg.evaluate(COMPUTE, [v])[0]
    hand = values(1, 1, 1, "1 0.5; 0 0.5", "0 0", "1 0; 0 1", "0 0", lr=1)
    o = page_numbers(hand)
    half = [[-0.5, 0.5], [-0.5, 0.5]]
    expect(close(o["P"], [[0.5, 0.5]], 1e-15) and close(o["L"], math.log(2), 1e-15) and close(o["dZ2"], [[-0.5, 0.5]], 1e-15)
           and close(o["dW2"], half, 1e-15) and close(o["dW1"], half, 1e-15) and close(o["db1"], [-0.5, 0.5], 1e-15) and close(o["dH"], [[-0.5, 0.5]], 1e-15),
           "equal scores: P = (1/2, 1/2), L = ln 2, dZ2 = dH = dZ1 = (-1/2, 1/2), dW1 = dW2 = [[-1/2, 1/2], [-1/2, 1/2]]")
    expect(close(o["W1n"], [[1.5, 0], [0.5, 0]], 1e-15) and close(o["L2"], math.log1p(math.exp(-6)), 1e-12),
           f"equal scores, lr 1: W1 becomes [[1.5, 0], [0.5, 0]], and the new loss is log(1 + e^-6) = {math.log1p(math.exp(-6)):.7f} ({o['L2']:.7f})")
    l3 = math.log(3)
    o = page_numbers(values(1, 1, 1, "1 0; 0 1", "0 0", f"{l3!r} 0; 0 0", "0 0"))
    expect(close(o["P"], [[0.75, 0.25]], 1e-14) and close(o["L"], math.log(4 / 3), 1e-14) and close(o["dZ2"], [[-0.25, 0.25]], 1e-14)
           and close(o["dW2"], [[-0.25, 0.25], [-0.25, 0.25]], 1e-14) and close(o["dW1"], [[-l3 / 4, 0], [-l3 / 4, 0]], 1e-14),
           "scores (ln 3, 0): P = (3/4, 1/4), L = ln 4/3, dZ2 = (-1/4, 1/4), dW1 = [[-ln3/4, 0], [-ln3/4, 0]]")
    o = page_numbers(values(1, 1, 1, "1 0.5; 0 0.5", "0 0", "1 0; 0 1", "0 0", more="1 1 2"))
    big = max(abs(x) for k in ("dW1", "db1", "dW2", "db2") for x in np.ravel(o[k]))
    expect(close(o["L"], math.log(2), 1e-15) and big < 1e-15 and all(r["pass"] for r in o["fd"]),
           f"a conflicting pair (same x, classes 1 and 2): L = ln 2, every gradient 0 (largest {big:.1e}), the check passes ({[r['pass'] for r in o['fd']].count(True)} of 12)")
    o = page_numbers(preset_values[1])
    expect(all(o["dW1"][i][1] == 0 for i in (0, 1)) and o["db1"][1] == 0 and all(o["dW2"][1][k] == 0 for k in (0, 1))
           and all(o["fd"][i]["num"] == 0 for i in (1, 3, 5, 8, 9)),
           "a dead unit: its incoming weights, its bias and its outgoing weights get exactly 0, and so do their finite differences")
    o = page_numbers(preset_values[4])
    dh2, x = o["dH"][0][1], [1.0, 1.0]
    expect([i for i, r in enumerate(o["fd"]) if not r["pass"]] == [1, 3, 5] and all(o["fd"][i]["kink"] and o["fd"][i]["rel"] == 1 for i in (1, 3, 5))
           and all(abs(o["fd"][i]["num"] - dh2 * xi / 2) < 1e-6 for i, xi in ((1, x[0]), (3, x[1]), (5, 1.0))),
           f"the kink (z = 0 exactly): W1[1,2], W1[2,2], b1[2] fail with relative error 1; their centred difference is half the one-sided slope dH2/2 = {dh2 / 2:.6f}")

    # ---- 3: gradient descent with a small learning rate
    rnd2, n_ok, n = random.Random(5), 0, 0
    small = []
    while len(small) < 200:
        v = rand_values(rnd2)
        v["lr"] = "0.001"
        r = reference(v)
        if np.min(np.abs(r["f"]["Z1"])) > 0.05 and r["gnorm2"] > 1e-4:
            small.append(v)
    so = pg.evaluate(COMPUTE, small)
    for v, o in zip(small, so):
        r = reference(v)
        n += 1
        n_ok += o["L2"] < o["L"] and abs((o["L"] - o["L2"]) / 0.001 - r["gnorm2"]) <= 0.05 * r["gnorm2"]
    expect(n_ok == n, f"lr 0.001: the loss goes down by about lr·|g|² (within 5%) on {n_ok} of {n} random inputs")
    o = page_numbers(preset_values[6])
    expect(o["L2"] > o["L"], f"the 'overshoots' example: the loss goes up ({o['L']:.3f} -> {o['L2']:.3f})")
    o = page_numbers(preset_values[5])
    expect(o["L2"] < o["L"], f"the same mini-batch with lr 0.5: the loss goes down ({o['L']:.3f} -> {o['L2']:.3f})")

    # ---- 5: the live check catches wrong numbers
    caught = pg.evaluate("""v => { const B = window.__bp, out = [];
        for (const harm of [t => { t.g.dW1[0][0] += 1e-6; }, t => { t.g.db2[1] -= 1e-6; }, t => { t.f.L += 1e-7; }, t => { t.gc[7].num += 1e-5; }, t => { t.f2.L -= 1e-6; }, t => { t.f.P[0][0] += 1e-7; }]) {
          const t = B.run(v); harm(t); out.push(B.independentCheck(v, t).ok === false); }
        return out; }""", preset_values[0])
    expect(all(caught), f"the live check rejects a trace with one number changed slightly ({sum(caught)} of {len(caught)})")

    # ---- 6: the page itself
    for i in range(7):
        pg.select_option("#st-preset", str(i))
        pg.wait_for_timeout(250)
        ck = pg.text_content(".st-check") or ""
        pg.locator(".st-board").click(position={"x": 4, "y": 4})
        pg.keyboard.press("End")
        pos = pg.inner_text(".st-pos")
        summ = pg.inner_text(".st-summary") if pg.locator(".st-summary").is_visible() else ""
        expect(ck.startswith("✓ Checked") and "Step 21 of 21" in pos and "after one SGD step" in summ,
               f"example {i + 1} ({presets[i]}): live check passes, End reaches step 21, the result shows")
        pg.screenshot(path=str(OUT / f"5_example_{i + 1}_end.png"))

    # the predict questions in use: the 'unit 2 off' example, answered from the NumPy numbers
    pg.select_option("#st-preset", "1")
    pg.wait_for_timeout(250)
    pg.evaluate("(() => { const a = window.__bp.api; a.S.predict = true; document.querySelector('#st-predict').checked = true; a.go(0); })()")
    pg.locator(".st-board").click(position={"x": 4, "y": 4})
    want = answers(reference(preset_values[1]))
    asked, right, shot = [], 0, 0
    for _ in range(40):
        if pg.locator(".st-note .opts").count():
            q = pg.inner_text(".st-q")
            a = want[len(asked)]
            asked.append((q, a))
            if len(asked) == 2:                                    # one wrong answer on purpose
                wrong = [o for o in pg.locator(".st-note .opts .st-opt").all_inner_texts() if o not in (a, "Skip")][0]
                pg.locator(".st-note .opts .st-opt", has_text=wrong).first.click()
                expect("Not quite" in pg.inner_text(".st-note") and a in pg.inner_text(".st-note"), f"a wrong answer is marked and the right one ({a}) is shown")
            else:
                if shot < 2:
                    pg.screenshot(path=str(OUT / f"3_question_{len(asked)}.png")); shot += 1
                pg.locator(".st-note .opts .st-opt", has_text=a).first.click()
                right += "✓ Right" in pg.inner_text(".st-note")
            continue
        if "Step 21 of 21" in pg.inner_text(".st-pos"):
            break
        pg.keyboard.press("ArrowRight")
    expect(len(asked) == 6 and right == 5, f"6 questions stop the steps; the 5 answered from NumPy are marked right ({right}): "
                                           + "; ".join(f"{q[:48]}… → {a}" for q, a in asked))
    expect([a for _, a in asked][2:4] == ["unit 2", "zero"], "on the 'unit 2 off' example: unit 2 passes no gradient, and its weight's gradient is zero")
    expect("predictions 5/6" in pg.inner_text(".st-pos"), f"the score is kept ({pg.inner_text('.st-pos')})")

    # keyboard: arrows, Home, End, code (C) with the step's line lit, present (P) and Esc
    pg.keyboard.press("Home")
    expect("Step 0 of 21" in pg.inner_text(".st-pos"), "Home goes to the start")
    pg.evaluate("(() => { const a = window.__bp.api; a.S.predict = false; document.querySelector('#st-predict').checked = false; })()")
    for _ in range(9):
        pg.keyboard.press("ArrowRight")
    pg.keyboard.press("ArrowLeft")
    expect("Step 8 of 21" in pg.inner_text(".st-pos"), f"→ nine times and ← once: step 8 ({pg.inner_text('.st-pos')})")
    pg.keyboard.press("c")
    lit = pg.evaluate("Array.from(document.querySelectorAll('.st-code > div')).findIndex(d => d.classList.contains('on')) + 1")
    lit_text = pg.inner_text(".st-code div.on") if lit else ""
    expect(pg.locator(".st-code").is_visible() and lit == 8 and "db2 = dZ2.sum(axis=0)" in lit_text, f"C shows the code with the step's line lit (line {lit}: {lit_text.strip()!r})")
    pg.screenshot(path=str(OUT / "4_code_open.png"))
    pg.keyboard.press("p")
    expect(pg.evaluate("document.body.classList.contains('present')"), "P switches to present mode")
    pg.keyboard.press("ArrowRight")
    pg.screenshot(path=str(OUT / "6_present.png"))
    pg.keyboard.press("Escape")
    expect(not pg.evaluate("document.body.classList.contains('present')"), "Esc leaves present mode")
    pg.keyboard.press("End")
    expect("Step 21 of 21" in pg.inner_text(".st-pos"), "End goes to the last step")
    pg.keyboard.press("c")

    # what is on screen matches NumPy: the loss on the graph, a relative error in the table
    r0 = reference(preset_values[0])
    pg.select_option("#st-preset", "0")
    pg.wait_for_timeout(250)
    pg.evaluate("window.__bp.api.go(5)")
    svg_text = pg.inner_text(".st-view")
    expect(f"{r0['f']['L']:.3f}" in svg_text, f"the loss on the graph is NumPy's {r0['f']['L']:.3f}")
    pg.evaluate("window.__bp.api.go(19)")
    cells = pg.locator(".bp-table tr").nth(1).all_inner_texts()[0]
    expect(f"{abs(r0['grads'][0]):.8f}"[:8] in cells.replace("−", "-"), f"the table shows NumPy's gradient of W1[1,1] ({r0['grads'][0]:.8f}): {cells.split(chr(9))[:3]}")

    # it fits: 1440x900 and 1280x720, every stage of every example, with the question showing, with and without the code
    misfits, checked = [], 0
    for w_, h_ in ((1440, 900), (1280, 720)):
        pg.set_viewport_size({"width": w_, "height": h_})
        for code in (False, True):
            pg.evaluate(f"window.__bp.api.toggleCode({'true' if code else 'false'})")
            for i in range(7):
                pg.select_option("#st-preset", str(i))
                pg.wait_for_timeout(120)
                for k in range(22):
                    st = pg.evaluate(f"""(() => {{ const a = window.__bp.api, t = a.S.trace, k = {k};
                        a.S.predict = true; a.S.answered = {{}}; a.S.lastAnswer = null;
                        if (t.steps[k].ask) a.go(k - 1); else a.go(k); return !!t.steps[k].ask; }})()""")
                    s = pg.evaluate(STATE)
                    checked += 1
                    if s["doc"][0] > w_ or s["doc"][1] > h_ + 1 or s["view"][0] > 1 or s["view"][1] > 1 or s["side"][0] > 1:
                        misfits.append(f"{w_}x{h_}{' code' if code else ''} example {i + 1} step {k}{' (question)' if st else ''}: {s}")
                    if (w_, code, i, k) in ((1280, False, 0, 5), (1280, True, 1, 12), (1280, False, 5, 13), (1440, True, 4, 19), (1280, False, 6, 21)):
                        pg.screenshot(path=str(OUT / f"2_fit_{w_}x{h_}{'_code' if code else ''}_ex{i + 1}_step{k}.png"))
            pg.evaluate("window.__bp.api.toggleCode(false)")
        fit = pg.evaluate("[document.documentElement.scrollWidth, document.documentElement.scrollHeight]")
        expect(fit[0] <= w_ and fit[1] <= h_ + 1, f"{w_}x{h_}: the page fits without scrolling ({fit[0]}x{fit[1]})")
    expect(not misfits, f"nothing scrolls (page, board or code card) in {checked} views: 2 screen sizes x code shown or not x 7 examples x 22 steps, questions showing"
           + ("" if not misfits else " -- " + " | ".join(misfits[:4]) + f" (+{len(misfits) - 4})" * (len(misfits) > 4)))
    pg.set_viewport_size({"width": 1440, "height": 900})

    # the shareable link, and the class example inside the app's frame
    pg.select_option("#st-preset", "4")
    pg.wait_for_timeout(300)
    link = pg.evaluate("location.hash")
    p2 = b.new_page(viewport={"width": 1400, "height": 900})
    p2.goto(PAGE.as_uri() + link)
    p2.wait_for_function("window.__bp && window.__bp.api.S.trace")
    expect(p2.input_value("#st-W1") == "0.5 0.4; 0.3 -0.4" and p2.input_value("#st-preset") == "4", f"the link restores the inputs and selects the example ({link[:50]}…)")
    p2.close()
    p3 = framed(b, PAGE.as_uri() + "#x1=2&x2=-1&y=2&more=&W1=0.5+-0.4%3B+0.3+0.8&b1=0.1+0.2&W2=0.7+-0.5%3B+-0.6+0.4&b2=0+0&lr=0.1&eps=1e-6", OUT, net)
    p3.wait_for_function(LAST + " !== null", timeout=15000)
    m = p3.evaluate(LAST)
    expect(m["state"].startswith("x1=2&x2=-1&y=2") and m["summary"].startswith("x = (2, -1), class 2, η = 0.1, ε = 1e-6"), f"framed: reports the setup it opened with ({m})")
    p3.frame_locator("#f").locator(".st-link", has_text="Change the input").click()
    p3.frame_locator("#f").locator("#st-more").fill("1 1 1")
    p3.wait_for_function(LAST + ".state.includes('more=1+1+1')", timeout=5000)
    m = p3.evaluate(LAST)
    expect("mini-batch of 2" in m["summary"], f"framed: a change is reported ({m['summary']})")
    p3.close()

    # bad input
    pg.locator(".st-link", has_text="Change the input").click()
    pg.fill("#st-W1", "0.5 -0.4 0.3")
    pg.wait_for_timeout(400)
    expect("Two rows of two numbers" in pg.inner_text(".st-panel"), "a bad weight matrix is refused with a message")
    pg.fill("#st-more", "1 2 3")
    pg.fill("#st-W1", "0.5 -0.4; 0.3 0.8")
    pg.wait_for_timeout(400)
    expect("class 1 or 2" in pg.inner_text(".st-panel"), "a bad extra example is refused with a message")
    pg.screenshot(path=str(OUT / "7_bad_input.png"))
    pg.fill("#st-more", "")
    pg.keyboard.press("Escape")

    # phone
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.select_option("#st-preset", "5")
    pg.wait_for_timeout(300)
    pg.evaluate("window.__bp.api.go(9)")
    sw = pg.evaluate("document.documentElement.scrollWidth")
    expect(sw <= 392, f"phone: no sideways scrolling ({sw}px)")
    pg.screenshot(path=str(OUT / "8_phone.png"), full_page=True)
    pg.set_viewport_size({"width": 1440, "height": 900})
    pg.select_option("#st-preset", "0")
    pg.wait_for_timeout(250)
    pg.screenshot(path=str(OUT / "1_start.png"))
    expect(not errs, f"no page errors {errs[:3] if errs else ''}")
    expect(not net, f"no network requests (works offline) {net[:3] if net else ''}")
    b.close()
print("PROBLEMS:", problems or "none")
sys.exit(1 if problems else 0)
