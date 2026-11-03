"""Automatic checks of the page-replacement page (Chrome, network blocked).
    python simulations/os.memory.page_replacement/qa.py [page.html] [screenshot folder]
(scripts/sims.py qa builds the single-file page first and passes it here)

Textbook answers (Silberschatz: FIFO 15, LRU 12, Optimal 9 faults with 3 frames; Belady: FIFO 9 faults with 3 frames,
10 with 4); the page against a third implementation written here in Python on 300 random reference strings x 1-6 frames
x 3 algorithms (faults, and replaced pages for FIFO and LRU); predict questions; the shareable link; bad input;
keyboard; phone; offline."""
import random
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

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


def reference(refs, frames, algo):
    """Python reference: (faults, replaced pages). Optimal: farthest next use, never-used-again first, ties to the lowest frame."""
    mem, faults, out, last, loaded = [], 0, [], {}, {}
    for t, p in enumerate(refs):
        if p in mem:
            last[p] = t
            continue
        faults += 1
        if len(mem) < frames:
            mem.append(p)
        else:
            if algo == "fifo":
                v = min(mem, key=lambda q: loaded[q])
            elif algo == "lru":
                v = min(mem, key=lambda q: last[q])
            else:
                def nxt(q):
                    try:
                        return refs.index(q, t + 1)
                    except ValueError:
                        return float("inf")
                v = max(mem, key=lambda q: (nxt(q), -mem.index(q)))
            out.append(v)
            mem[mem.index(v)] = p
        loaded[p] = last[p] = t
    return faults, out


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


with sync_playwright() as pw:
    b = pw.chromium.launch(channel="chrome")
    pg = b.new_page(viewport={"width": 1400, "height": 900})
    errs, net = [], []
    pg.on("pageerror", lambda e: errs.append(str(e)[:300]))
    pg.on("console", lambda m: errs.append(m.text[:300]) if m.type == "error" else None)
    pg.route("http*://**", lambda r: (net.append(r.request.url), r.abort()))
    pg.goto(PAGE.as_uri())
    pg.wait_for_function("window.__pagerep && window.__pagerep.api.S.trace")

    # ---- textbook answers
    tb = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1, 2, 0, 1, 7, 0, 1]
    got = pg.evaluate("r => ['fifo', 'lru', 'opt'].map(a => window.__pagerep.simulate(r, 3, a).faults)", tb)
    expect(got == [15, 12, 9], f"textbook (Silberschatz) with 3 frames: FIFO/LRU/Optimal faults {got} (expected 15, 12, 9)")
    bel = pg.evaluate("r => [3, 4].map(f => window.__pagerep.simulate(r, f, 'fifo').faults)", [1, 2, 3, 4, 1, 2, 5, 1, 2, 3, 4, 5])
    expect(bel == [9, 10], f"Belady's anomaly: FIFO faults with 3 and 4 frames {bel} (expected 9, 10)")

    # ---- the page against the Python reference on random strings
    rnd, bad, n = random.Random(7), 0, 0
    for _ in range(300):
        refs = [rnd.randrange(0, rnd.choice([4, 6, 9])) for _ in range(rnd.randint(1, 30))]
        res = pg.evaluate("""r => { const S = window.__pagerep.simulate, out = {};
            for (const a of ['fifo', 'lru', 'opt']) for (let f = 1; f <= 6; f++) { const s = S(r, f, a); out[a + f] = [s.faults, s.events.filter(e => e.victim !== null).map(e => e.victim)]; }
            return out; }""", refs)
        for a in ("fifo", "lru", "opt"):
            for f in range(1, 7):
                n += 1
                faults, victims = reference(refs, f, a)
                pf, pv = res[f"{a}{f}"]
                bad += pf != faults or pv != victims          # same tie rule for Optimal, so the replaced pages match too
    expect(bad == 0, f"page vs a Python implementation: {n} runs (300 strings x 6 frame counts x 3 algorithms), {bad} differ")

    # ---- the page itself: live check, predict questions, keyboard, link, bad input
    expect(pg.inner_text(".st-check").startswith("✓ Checked"), "the page's live check passes on the first example")
    pg.screenshot(path=str(OUT / "1_start.png"))
    for _ in range(4):
        pg.keyboard.press("ArrowRight")
    expect("Step 3 of 20" in pg.inner_text(".st-pos"), f"keyboard → steps forward ({pg.inner_text('.st-pos')!r})")
    asked = pg.locator(".st-ask button").count() > 0
    expect(asked and "Which page will FIFO replace?" in pg.inner_text(".st-note"), "before the first replacement it asks which page goes")
    pg.locator(".st-ask button", has_text="7").first.click()
    expect("✓ Right" in pg.inner_text(".st-note"), f"answering 7 (the right one) says Right: {pg.inner_text('.st-note')[:90]!r}")
    pg.screenshot(path=str(OUT / "2_predict.png"))
    pg.select_option("#st-preset", "4")
    pg.wait_for_timeout(300)
    expect("anomaly" in pg.inner_text(".st-summary").lower(), "Belady example: the summary points out the anomaly")
    pg.click("text=⏭")
    expect("10" in pg.inner_text(".side") and "Step 12 of 12" in pg.inner_text(".st-pos"), "the last step shows 10 faults")
    pg.screenshot(path=str(OUT / "3_belady.png"))
    link = pg.evaluate("location.hash")
    p2 = b.new_page(viewport={"width": 1400, "height": 900})
    p2.goto(PAGE.as_uri() + link)
    p2.wait_for_function("window.__pagerep && window.__pagerep.api.S.trace")
    expect(p2.input_value("#st-frames") == "4" and p2.input_value("#st-refs").startswith("1 2 3 4 1 2 5"), f"the shareable link restores the inputs ({link[:40]}…)")
    expect(p2.input_value("#st-preset") == "4", "a link that matches an example selects that example")
    p2.close()

    # ---- class example (the app): the framed page reports its setup, and the reported setup reopens it
    p3 = framed(b, PAGE.as_uri() + "#refs=1+2+3+1+4&frames=2&algo=opt", OUT, net)
    p3.wait_for_function(LAST + " !== null", timeout=15000)
    m = p3.evaluate(LAST)
    expect(m["state"] == "refs=1+2+3+1+4&frames=2&algo=opt" and m["summary"].startswith("Optimal, 2 frames"), f"framed: reports the setup it opened with ({m})")
    p3.frame_locator("#f").locator("#st-frames").fill("3")
    p3.wait_for_function(LAST + ".state.includes('frames=3')", timeout=5000)
    expect(True, "framed: a change is reported")
    p3.close()
    pg.fill("#st-refs", "1 2 x 4")
    pg.wait_for_timeout(400)
    expect("not a page number" in pg.inner_text(".st-panel"), "bad input is refused with a message")

    # ---- phone
    pg.set_viewport_size({"width": 390, "height": 844})
    pg.fill("#st-refs", "7 0 1 2 0 3 0 4 2 3 0 3 2 1 2 0 1 7 0 1"); pg.wait_for_timeout(400)
    sw = pg.evaluate("document.documentElement.scrollWidth")
    expect(sw <= 392, f"phone: no sideways scrolling of the page ({sw}px; the grid scrolls inside its box)")
    pg.screenshot(path=str(OUT / "4_phone.png"), full_page=True)
    expect(not errs, f"no page errors {errs[:3] if errs else ''}")
    expect(not net, f"no network requests (works offline) {net[:3] if net else ''}")
    b.close()
print("PROBLEMS:", problems or "none")
sys.exit(1 if problems else 0)
