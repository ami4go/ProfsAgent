"""Automatic checks of the interactive DBSCAN page (Chrome, network blocked).
    python simulations/ml.clustering.dbscan/qa.py [page.html] [screenshot folder]
(scripts/sims.py qa builds the single-file page first and passes it here)

Every label is compared with scikit-learn's DBSCAN on the same points (same core points, same noise, same grouping of
core points, every border point within eps of a core point of its own cluster), over 4 datasets x 4 eps x 3 minPts;
the page's own live check must agree. Then: the video's example gives the video's result, step mode replays to the
same labels, clicking adds / dragging moves / Shift+click removes a point, speed, phone layout, offline."""
import sys
from pathlib import Path
from urllib.parse import parse_qsl

import numpy as np
from playwright.sync_api import sync_playwright
from sklearn.cluster import DBSCAN

for _s in (sys.stdout, sys.stderr):
    _s.reconfigure(encoding="utf-8", errors="replace")
HERE = Path(__file__).resolve().parent
PAGE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent / "_build" / f"{HERE.name}.html"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "_build" / "qa" / HERE.name
OUT.mkdir(parents=True, exist_ok=True)
problems = []


def expect(cond, msg):
    print(("ok: " if cond else "PROBLEM: ") + msg)
    if not cond:
        problems.append(msg)


def compare_with_sklearn(P, eps, min_pts, lab, core):
    """Number of points whose label disagrees with scikit-learn's DBSCAN (allowing renamed clusters and the legitimate
    choice of cluster for a border point reachable from two clusters)."""
    if not len(P):
        return 0
    P = np.array(P)
    sk = DBSCAN(eps=eps, min_samples=min_pts).fit(P)
    sk_core = np.zeros(len(P), bool)
    sk_core[sk.core_sample_indices_] = True
    D = np.linalg.norm(P[:, None] - P[None], axis=2)
    lab, core = np.array(lab), np.array(core, bool)
    mapping, back, wrong = {}, {}, 0
    for i in range(len(P)):
        ok = core[i] == sk_core[i] and ((lab[i] == -1) == (sk.labels_[i] == -1))
        if ok and core[i]:
            a, b = lab[i], sk.labels_[i]
            ok = mapping.setdefault(a, b) == b and back.setdefault(b, a) == a
        elif ok and lab[i] >= 0:
            ok = any(D[i, j] <= eps + 1e-9 and core[j] and lab[j] == lab[i] for j in range(len(P)))
        wrong += not ok
    return wrong


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


with sync_playwright() as p:
    b = p.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1400, "height": 900})
    errs, net = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
    pg.on("console", lambda m: errs.append(m.text[:300]) if m.type == "error" else None)
    pg.route("http*://**", lambda r: (net.append(r.request.url), r.abort()))
    pg.goto(PAGE.as_uri())
    pg.wait_for_function("window.__dbscan && window.__dbscan.W.R")

    # ---- the video's example gives the video's result
    s = pg.inner_text("#summary")
    expect("3 clusters" in s and "6 border" in s and "6 noise" in s and "45 points" in s, f"video example: {s!r}")
    expect(pg.inner_text("#check").startswith("✓ Checked"), "the page's own check passes on the video example")
    pg.screenshot(path=str(OUT / "1_video_example.png"))

    # ---- every label against scikit-learn, over datasets and settings
    total = bad = page_bad = 0
    for preset in range(4):
        for eps in (0.25, 0.4, 0.62, 0.9):
            for mp in (2, 4, 7):
                r = pg.evaluate("""([pi, eps, mp]) => { const D = window.__dbscan; D.usePreset(pi); D.setParams(eps, mp); D.update();
                                   const c = D.checkByDefinition(D.W.P, eps, mp, D.W.R);
                                   return { P: D.W.P, lab: D.W.R.lab, core: D.W.R.core, pageWrong: c.wrong }; }""", [preset, eps, mp])
                w = compare_with_sklearn(r["P"], eps, mp, r["lab"], r["core"])
                total += len(r["P"]); bad += w; page_bad += r["pageWrong"]
    expect(bad == 0, f"scikit-learn agrees on every label: {total} labels checked (4 datasets x 4 eps x 3 minPts), {bad} differ")
    expect(page_bad == 0, f"the page's live check agrees too ({page_bad} flagged)")

    # ---- step mode replays to the same labels, and shows a noise point becoming a border point
    pg.select_option("#preset", "0")
    pg.wait_for_timeout(200)
    captions, steps = [], 0
    while not pg.is_disabled("#step") and steps < 200:
        pg.click("#step"); steps += 1
        captions.append(pg.inner_text("#caption"))
    same = pg.evaluate("() => { const D = window.__dbscan; return JSON.stringify(D.W.R.lab) === JSON.stringify((() => { const W = D.W; return W.R.lab; })()); }")
    final_ok = pg.evaluate("""() => { const D = window.__dbscan, W = D.W; const lab = new Array(W.P.length).fill(-2);
        for (const e of W.R.events) { if (e.k === 'noise') lab[e.i] = -1; else if (e.k === 'seed') lab[e.i] = e.c; else for (const w of e.wave) lab[w.j] = e.c; }
        return JSON.stringify(lab) === JSON.stringify(W.R.lab); }""")
    expect(steps == 22 and final_ok and same, f"step mode: {steps} steps (the video has 22) end on the same labels")
    expect(any("marked noise earlier" in c for c in captions), "step mode shows a noise point becoming a border point")
    pg.screenshot(path=str(OUT / "2_step_mode.png"))
    pg.click("#back")
    expect(pg.inner_text("#stepinfo") == f"Step {steps - 1} of {steps}", "Back goes one step back")
    pg.click("#done")

    # ---- add, drag, remove with the mouse
    def client(x, y):
        return pg.evaluate("""([x, y]) => { const c = document.querySelector('#scene canvas').getBoundingClientRect(), S = window.__dbscan.S;
                              return [c.left + (x * S / (128 / 9) + 0.5) * c.width, c.top + (0.5 - y * S / 8) * c.height]; }""", [x, y])
    n0 = pg.evaluate("window.__dbscan.W.P.length")
    pg.mouse.click(*client(3.9, -2.2))
    n1 = pg.evaluate("window.__dbscan.W.P.length")
    expect(n1 == n0 + 1, f"click on empty space adds a point ({n0} → {n1})")
    x, y = client(3.9, -2.2)
    pg.mouse.move(x, y); pg.mouse.down(); pg.mouse.move(x - 60, y - 40, steps=6); pg.mouse.up()
    moved = pg.evaluate("window.__dbscan.W.P[window.__dbscan.W.P.length - 1]")
    expect(abs(moved[0] - 3.9) > 0.2 and n1 == pg.evaluate("window.__dbscan.W.P.length"), f"drag moves the point to ({moved[0]:.2f}, {moved[1]:.2f})")
    pg.keyboard.down("Shift"); pg.mouse.click(*client(*moved)); pg.keyboard.up("Shift")
    expect(pg.evaluate("window.__dbscan.W.P.length") == n0, "Shift+click removes it")
    expect(pg.inner_text("#check").startswith("✓"), "still checked after editing")

    # ---- speed, the empty example, circles
    pg.select_option("#preset", "1")
    ms = pg.evaluate("() => { const D = window.__dbscan; const t0 = performance.now(); for (let i = 0; i < 20; i++) { D.W.eps = 0.3 + i * 0.02; D.update(); } return (performance.now() - t0) / 20; }")
    expect(ms < 50, f"speed: one update with {pg.evaluate('window.__dbscan.W.P.length')} points takes {ms:.1f} ms")
    pg.check("#circles"); pg.wait_for_timeout(200)
    pg.screenshot(path=str(OUT / "3_moons_circles.png"))
    pg.select_option("#preset", "4")
    expect("No points yet" in pg.inner_text("#summary"), "the empty example asks for points")

    # ---- class example (the app): a link opens a setup (with the professor's own points); the framed page reports changes
    p2 = b.new_page(viewport={"width": 1400, "height": 900})
    p2.route("http*://**", lambda r: (net.append(r.request.url), r.abort()))
    p2.goto(PAGE.as_uri() + "#p=1&eps=0.45&min=5")
    p2.wait_for_function("window.__dbscan && window.__dbscan.W.R")
    v = p2.evaluate("() => { const W = window.__dbscan.W; return [W.preset, W.eps, W.minPts, W.edited, W.P.length, document.getElementById('preset').value]; }")
    expect(v == [1, 0.45, 5, False, 106, "1"], f"a link opens an example with its settings ({v})")
    p2.goto(PAGE.as_uri() + "#p=4&eps=0.70&min=3&pts=0.00,0.00;0.30,0.00;0.00,0.30;3.00,2.00")
    p2.reload()
    p2.wait_for_function("window.__dbscan && window.__dbscan.W.R")
    expect(p2.inner_text("#summary").startswith("1 cluster · 3 core · 0 border · 1 noise (4 points)"), f"a link opens the professor's own points ({p2.inner_text('#summary')!r})")
    p2.close()
    p3 = framed(b, PAGE.as_uri() + "#p=0&eps=0.62&min=4", OUT, net)
    p3.wait_for_function(LAST + " !== null", timeout=20000)
    m = p3.evaluate(LAST)
    expect(m["state"] == "p=0&eps=0.62&min=4" and "video" in m["summary"], f"framed: reports its setup ({m})")
    fr = p3.frame_locator("#f")
    fr.locator("#clear").click()
    fr.locator("canvas").click(position={"x": 300, "y": 250})
    p3.wait_for_function(LAST + ".state.includes('pts=')", timeout=5000)
    m = p3.evaluate(LAST)
    pts = dict(parse_qsl(m["state"])).get("pts", "")
    expect(len(pts.split(";")) == 1 and pts.count(",") == 1 and "changed by you (1 point)" in m["summary"], f"framed: the professor's own points are reported ({pts!r}; {m['summary']!r})")
    p3.close()

    # ---- phone
    pg.set_viewport_size({"width": 390, "height": 844}); pg.wait_for_timeout(400)
    sw = pg.evaluate("document.documentElement.scrollWidth")
    expect(sw <= 392, f"phone: no sideways scrolling ({sw}px)")
    pg.screenshot(path=str(OUT / "4_phone.png"), full_page=True)
    expect(not errs, f"no page errors {errs[:3] if errs else ''}")
    expect(not net, f"no network requests (works offline) {net[:3] if net else ''}")
    b.close()
print("PROBLEMS:", problems or "none")
sys.exit(1 if problems else 0)
