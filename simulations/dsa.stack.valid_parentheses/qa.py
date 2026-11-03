"""Headless check of simulations/dsa.stack.valid_parentheses/page.html.
    python simulations/dsa.stack.valid_parentheses/qa.py [page.html] [screenshot folder]"""
import random
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().with_name("page.html")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[1] / "_build" / "qa" / Path(__file__).resolve().parent.name
OUT.mkdir(parents=True, exist_ok=True)


def reference(s):
    """Separate stack implementation: returns (valid, how it ended, index)."""
    pairs, st = {")": "(", "]": "[", "}": "{"}, []
    for i, c in enumerate(s):
        if c in "([{":
            st.append(c)
        elif c in ")]}":
            if not st:
                return False, "fail-empty", i
            if st[-1] != pairs[c]:
                return False, "fail-mismatch", i
            st.pop()
    return (True, "end-valid", len(s)) if not st else (False, "end-unclosed", len(s))


problems = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for tag, w, h in [("desk", 1280, 900), ("phone", 390, 844)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(HTML.as_uri()); pg.wait_for_timeout(300)
        shot = lambda name, full=False: pg.screenshot(path=str(OUT / f"{tag}_{name}.png"), full_page=full)
        step = lambda: pg.locator("#stepno").inner_text()

        if tag == "desk":
            rnd = random.Random(11)
            cases = ["", "()", "()[]{}", "{[()()]}", "a*(b+c)-{d/[e]}", "(]", "([)]", "((()", "())", "]", "(", "x y z"]
            cases += ["".join(rnd.choice("()[]{}ab ") for _ in range(rnd.randint(0, 30))) for _ in range(2500)]
            cases += [pg.evaluate("parenSim.randomString()") for _ in range(500)]
            bad = 0
            for s in cases:
                got = pg.evaluate("s => parenSim.run(s)", s)
                ref = reference(s)
                other = pg.evaluate("s => parenSim.pairRemoval(s)", s)
                if (got["valid"], got["action"], got["i"]) != ref or other != ref[0]:
                    bad += 1
                    if bad <= 3:
                        problems.append(f"{s!r}: page {got} ref {ref} pair-removal {other}")
            rv = sum(1 for s in cases[-500:] if reference(s)[0])
            print(f"compared {len(cases)} strings, mismatches: {bad}; random button gives {rv}/500 valid")

        # prediction + play to the end on the default example
        pg.locator('[data-p="1"]').click()
        shot("01_start")
        pg.locator("#nextBtn").click(); pg.locator("#nextBtn").click(); pg.locator("#nextBtn").click()
        shot("02_pushing")
        total = int(step().split("/")[1])
        for _ in range(total):
            if pg.locator("#nextBtn").is_disabled():
                break
            pg.locator("#nextBtn").click()
            if step().startswith("Step 6 "):
                shot("03_pop")
        shot("04_valid", full=True)
        res = pg.locator("#result").inner_text()
        if "Valid" not in res or "correct" not in res:
            problems.append(f"{tag}: final result wrong: {res!r}")
        # an invalid one by typing
        pg.fill("#s", "([)]"); pg.keyboard.press("Enter")
        for _ in range(10):
            if pg.locator("#nextBtn").is_disabled():
                break
            pg.locator("#nextBtn").click()
        res = pg.locator("#result").inner_text()
        if "Not valid" not in res or "index 2" not in res:
            problems.append(f"{tag}: ([)] result wrong: {res!r}")
        shot("05_mismatch", full=True)
        # unclosed
        pg.select_option("#ex", "5")
        pg.evaluate("(() => { const s = document.getElementById('scrub'); s.value = s.max; s.dispatchEvent(new Event('input')); })()")
        if "never closed" not in pg.locator("#result").inner_text():
            problems.append(f"{tag}: ((() should say never closed")
        shot("06_unclosed", full=True)
        # too long input
        pg.fill("#s", "(" * 31); pg.keyboard.press("Enter")
        if not pg.locator("#ferr .err").count():
            problems.append(f"{tag}: 31 characters were accepted")
        pg.fill("#s", "(())"); pg.keyboard.press("Enter")
        if pg.locator("#ferr .err").count():
            problems.append(f"{tag}: error stayed after a valid input")
        # random + play + keyboard
        pg.locator("#randBtn").click()
        if "✓" not in pg.locator("#check").inner_text():
            problems.append(f"{tag}: badge failed for random string")
        pg.locator("#resetBtn").click(); pg.locator("body").click(position={"x": 3, "y": 3})
        pg.keyboard.press("ArrowRight"); pg.keyboard.press("ArrowRight")
        if not step().startswith("Step 3 "):
            problems.append(f"{tag}: keyboard gave {step()}")
        print(tag, "page errors:", errs or "none")
        problems += [f"{tag}: {e}" for e in errs]
        pg.close()
    b.close()
print("PROBLEMS:", problems or "none")
sys.exit(1 if problems else 0)
