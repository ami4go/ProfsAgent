"""Automatic checks of the interactive convolution page (Chrome, network blocked).
    python simulations/signals.convolution.graphical/qa.py [page.html] [screenshot folder]
(scripts/sims.py qa builds the single-file page first and passes it here)"""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")
HERE = Path(__file__).resolve().parent
PAGE = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent / "_build" / f"{HERE.name}.html"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE.parent / "_build" / "qa" / HERE.name
OUT.mkdir(parents=True, exist_ok=True)
problems = []


def expect(cond, msg):
    print(("ok: " if cond else "PROBLEM: ") + msg)
    if not cond:
        problems.append(msg)


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
    pg.wait_for_function("window.__convolution && window.__convolution.S.y")

    # ---- the formula parser
    cases = [("2t", 3, 6), ("-t^2", 2, -4), ("2^-1", 0, 0.5), ("(t+1)(t-1)", 3, 8), ("sin(pi/2)", 0, 1), ("u(0)", 0, 0.5),
             ("u(t)", -1, 0), ("min(t, 2)", 3, 2), ("e^1", 0, 2.718281828), ("3e2", 0, 300), ("2exp(0)", 0, 2), ("t W", 2, 4),
             ("rect(t)", 0.5, 0.5), ("tri(t - 1)", 1.5, 0.5), ("sinc(0)", 0, 1), ("ramp(t-1)", 3, 2), ("4 − t", 1, 3), ("2·t", 2, 4)]
    res = pg.evaluate("""cases => cases.map(([s, t, want]) => { try { const c = window.__convolution.compile(s); return [s, c.f({t, W: 2, a: 1}), want]; }
                                                                catch (e) { return [s, 'ERR ' + e.message, want]; } })""", cases)
    bad = [r for r in res if not isinstance(r[1], (int, float)) or abs(r[1] - r[2]) > 1e-6]
    expect(not bad, f"parser: {len(cases)} formulas evaluate correctly" + (f" — wrong: {bad}" if bad else ""))
    errs_txt = pg.evaluate("""() => ['exp t', 'x + 1', '2*(t', 'u()', 'min(t)', 't $ 2', ''].map(s => { try { window.__convolution.compile(s); return null; } catch (e) { return e.message; } })""")
    expect(all(errs_txt), f"parser: 7 broken formulas are refused with a message ({errs_txt[1]!r}, ...)")

    # ---- accuracy against the exact answers, over W, a and t (including t between samples)
    worst = pg.evaluate("""() => {
        const C = window.__convolution, out = [];
        for (const pi of [0, 1, 2]) for (const W of [0.5, 1.3, 2, 3.7]) for (const a of [0.2, 1, 1.7, 3]) {
            C.S.W = W; C.S.a = a; C.usePreset(pi);
            let md = 0, mc = 0;
            for (let t = -2; t <= 9.5; t += 0.37) { const e = C.PRESETS[pi].exact(t, W, a); md = Math.max(md, Math.abs(C.directArea(t) - e)); mc = Math.max(mc, Math.abs(C.yAt(t) - e)); }
            out.push([pi, W, a, md, mc]);
        }
        return out; }""")
    md = max(w[3] for w in worst)
    mc = max(w[4] for w in worst)
    expect(md < 2e-3, f"accuracy: direct area vs exact answer, worst difference {md:.1e} (3 examples × 16 settings × 32 values of t)")
    expect(mc < 5e-3, f"accuracy: convolution sum vs exact answer, worst difference {mc:.1e}")

    # ---- the page itself: example, check line, sliders
    pg.select_option("#preset", "0")
    pg.fill("#W", "2"); pg.dispatch_event("#W", "input")
    pg.fill("#a", "1"); pg.dispatch_event("#a", "input")
    pg.fill("#t", "1"); pg.dispatch_event("#t", "input")
    chk = pg.inner_text("#check")
    expect(chk.startswith("✓ Checked") and "exact 0.6321" in chk, f"check line at t = 1: {chk!r}")
    pg.screenshot(path=str(OUT / "1_default.png"))

    # ---- own functions, a broken one, and one that never dies out
    pg.fill("#xin", "exp(-2t)u(t)"); pg.fill("#hin", "tri(t - 2)")
    pg.wait_for_timeout(500)
    expect(pg.input_value("#preset") == "own" and pg.inner_text("#xerr") == "" and pg.inner_text("#check").startswith("✓"), "own functions: accepted and checked by the two methods")
    pg.fill("#hin", "tri(t - 2")
    pg.wait_for_timeout(500)
    expect("Expected" in pg.inner_text("#herr") and "bad" in (pg.get_attribute("#hin", "class") or ""), f"broken formula shows: {pg.inner_text('#herr')!r}")
    pg.fill("#hin", "u(t)")
    pg.wait_for_timeout(500)
    expect("not zero at the edge" in pg.inner_text("#warn"), "a signal that never dies out gets a warning")
    pg.select_option("#preset", "4")
    pg.wait_for_timeout(300)
    pg.fill("#t", "2.3"); pg.dispatch_event("#t", "input")
    expect(pg.inner_text("#check").startswith("✓"), "sine burst example: positive and negative areas, the methods agree")
    pg.screenshot(path=str(OUT / "2_sine_burst.png"))

    # ---- speed
    ms = pg.evaluate("""() => { const C = window.__convolution; let t0 = performance.now(); for (let i = 0; i < 20; i++) { C.S.t = -2 + i * 0.4; C.frame(); } const f = (performance.now() - t0) / 20;
                                 t0 = performance.now(); C.full(); return [f, performance.now() - t0]; }""")
    expect(ms[0] < 40, f"speed: one frame (moving t) takes {ms[0]:.1f} ms; changing a function takes {ms[1]:.0f} ms")

    # ---- play and the flip animation
    pg.select_option("#preset", "0")
    t_before = float(pg.input_value("#t"))
    pg.click("#play"); pg.wait_for_timeout(1500); pg.click("#play")
    expect(abs(float(pg.input_value("#t")) - t_before) > 0.5, "Play moves t")
    pg.click("#flip")
    pg.wait_for_timeout(1900)
    pg.screenshot(path=str(OUT / "3_flip_midway.png"))
    pg.wait_for_function("!document.getElementById('flip').disabled", timeout=15000)
    expect(True, "Show the flip runs and gives the controls back")

    # ---- class example (the app): a link opens a setup; the framed page reports its setup and its changes
    p2 = b.new_page(viewport={"width": 1400, "height": 900})
    p2.route("http*://**", lambda r: (net.append(r.request.url), r.abort()))
    p2.goto(PAGE.as_uri() + "#p=own&x=u(t)-u(t-1)&h=exp(-t)*u(t)&W=3.0&a=1.5&t=2.50")
    p2.wait_for_function("window.__convolution && window.__convolution.S.y")
    v = p2.evaluate("() => { const S = window.__convolution.S; return [S.W, S.a, S.t, document.getElementById('xin').value, document.getElementById('preset').value]; }")
    expect(v == [3, 1.5, 2.5, "u(t)-u(t-1)", "own"], f"a link opens its own functions and values ({v})")
    p2.goto(PAGE.as_uri() + "#p=1&W=2.0&a=0.5&t=1.00")
    p2.reload()
    p2.wait_for_function("window.__convolution && window.__convolution.S.y")
    v = p2.evaluate("() => [window.__convolution.S.a, document.getElementById('preset').value, document.getElementById('hin').value]")
    expect(v == [0.5, "1", "u(t) - u(t - a)"], f"a link opens an example with its values ({v})")
    expect(p2.inner_text("#check").startswith("✓"), "the check passes on a setup opened from a link")
    p2.close()
    p3 = framed(b, PAGE.as_uri() + "#p=1&W=2.0&a=1.0&t=1.00", OUT, net)
    p3.wait_for_function(LAST + " !== null", timeout=20000)
    m = p3.evaluate(LAST)
    expect(m["state"] == "p=1&W=2.0&a=1.0&t=1.00" and "Pulse ∗ pulse" in m["summary"], f"framed: reports its setup ({m})")
    p3.frame_locator("#f").locator("#t").evaluate("el => { el.value = '3.2'; el.dispatchEvent(new Event('input', {bubbles: true})); }")
    p3.wait_for_function(LAST + ".state.includes('t=3.20')", timeout=5000)
    expect(True, "framed: moving t is reported")
    p3.close()

    # ---- narrow screen
    pg.set_viewport_size({"width": 820, "height": 1100}); pg.wait_for_timeout(500)
    sw = pg.evaluate("document.documentElement.scrollWidth")
    expect(sw <= 822, f"narrow screen: no sideways scrolling ({sw}px)")
    pg.screenshot(path=str(OUT / "4_narrow.png"), full_page=True)
    expect(not errs, f"no page errors {errs[:3] if errs else ''}")
    expect(not net, f"no network requests (works offline) {net[:3] if net else ''}")
    b.close()
print("PROBLEMS:", problems or "none")
sys.exit(1 if problems else 0)
