"""Headless check of simulations/algorithms.graph.kosaraju/page.html.

1. Every preset: the simulation's SCCs must equal an independent Python answer.
2. Click through every step of the textbook graph (no page errors allowed).
3. Quiz, play/pause, keyboard and edit mode.
4. Screenshots at laptop and phone width -> Temporary/kosaraju_qa/

    python simulations/algorithms.graph.kosaraju/qa.py [page.html] [screenshot folder]"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().with_name("page.html")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[1] / "_build" / "qa" / Path(__file__).resolve().parent.name
OUT.mkdir(parents=True, exist_ok=True)


def reference_sccs(edges, nodes):
    """Mutual reachability, written separately from the page's code."""
    adj = {n: [] for n in nodes}
    for a, b in edges:
        adj[a].append(b)

    def reach(s):
        seen, todo = {s}, [s]
        while todo:
            x = todo.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    todo.append(y)
        return seen

    r = {n: reach(n) for n in nodes}
    return {frozenset(v for v in nodes if v in r[u] and u in r[v]) for u in nodes}


problems = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for tag, w, h in [("desk", 1280, 860), ("phone", 390, 844)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(HTML.as_uri())
        pg.wait_for_timeout(300)
        shot = lambda name, full=False: pg.screenshot(path=str(OUT / f"{tag}_{name}.png"), full_page=full)
        step = lambda: pg.locator("#stepno").inner_text()

        if tag == "desk":
            presets = pg.evaluate("Object.fromEntries(Object.entries(kosarajuSim.presets).map(([k, v]) => [k, v]))")
            for key, pr in presets.items():
                edges = [e.split(">") for e in pr["edges"].split()]
                got = pg.evaluate(f"kosarajuSim.run('{key}')")
                got_set = {frozenset(c) for c in got["comps"]}
                ref = reference_sccs(edges, list(pr["nodes"]))
                ok = got_set == ref
                print(f"{key:9s} steps={got['steps']:3d} SCCs={sorted(sorted(c) for c in got_set)} {'OK' if ok else 'MISMATCH ' + str(ref)}")
                if not ok:
                    problems.append(key)
                pg.select_option("#preset", key)
                last = pg.evaluate("document.getElementById('scrub').max")
                pg.evaluate(f"(() => {{ const s = document.getElementById('scrub'); s.value = {last}; s.dispatchEvent(new Event('input')); }})()")
                badge = pg.locator("#check").inner_text()
                if "✓" not in badge:
                    problems.append(key + " badge: " + badge)
                if not step().startswith(f"Step {got['steps']} "):
                    problems.append(f"{key}: slider jump to the end failed ({step()})")
                shown = pg.locator("#sccs").inner_text()
                for c in ref:
                    if ", ".join(sorted(c)) not in shown:
                        problems.append(f"{key}: screen does not list {sorted(c)}: {shown!r}")
            pg.select_option("#preset", "textbook")

        # step 0 + prediction quiz
        pg.locator('[data-predict="4"]').click()
        shot("01_start_predict")
        # click through every step
        total = int(step().split("/")[1])
        snaps = {6: "02_pass1_going_deeper", 9: "03_pass1_finish"}
        for i in range(1, total):
            if pg.locator("#nextBtn").is_disabled():
                break
            pg.locator("#nextBtn").click()
            if i in snaps:
                shot(snaps[i])
            if pg.locator('[data-start]').count() and "rev" not in snaps.values():
                rev_step = i
                shot("04_reverse_quiz")
                pg.locator('[data-start="C"]').click()   # wrong on purpose
                shot("05_quiz_wrong")
                pg.locator('[data-start="A"]').click()   # A finished last
                shot("06_quiz_right")
                snaps[-1] = "rev"
            if i == total - 12:
                shot("07_pass2_middle")
        shot("08_done", full=True)
        if not step().startswith(f"Step {total} "):
            problems.append(f"{tag}: did not reach the last step ({step()})")
        if "You predicted" not in pg.locator("#explain").inner_text():
            problems.append(f"{tag}: prediction feedback missing")

        # keyboard + play/pause
        pg.locator("#resetBtn").click()
        pg.locator("body").click(position={"x": 5, "y": 5})
        for _ in range(3):
            pg.keyboard.press("ArrowRight")
        if not step().startswith("Step 4 "):
            problems.append(f"{tag}: keyboard stepping gave {step()}")
        pg.locator("#playBtn").click()
        pg.wait_for_timeout(2600)
        pg.locator("#playBtn").click()
        played = int(step().split()[1])
        if played <= 4:
            problems.append(f"{tag}: play did not advance ({step()})")

        # edit mode: No loops graph + edge D->A makes one SCC
        pg.select_option("#preset", "noLoops")
        pg.locator("#editBtn").click()
        pg.locator('.node[data-id="D"]').click()
        pg.locator('.node[data-id="A"]').click()
        shot("09_edit_added_edge")
        pg.locator("#editBtn").click()
        last = pg.evaluate("document.getElementById('scrub').max")
        pg.evaluate(f"(() => {{ const s = document.getElementById('scrub'); s.value = {last}; s.dispatchEvent(new Event('input')); }})()")
        sccs = pg.locator("#sccs").inner_text()
        if "A, B, C, D" not in sccs:
            problems.append(f"{tag}: edit mode result wrong: {sccs!r}")
        shot("10_edit_result", full=True)
        print(tag, "page errors:", errs or "none")
        problems += [f"{tag}: {e}" for e in errs]
        pg.close()
    b.close()

print("PROBLEMS:", problems or "none")
sys.exit(1 if problems else 0)
