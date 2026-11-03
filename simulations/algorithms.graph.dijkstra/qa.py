"""Headless check of simulations/algorithms.graph.dijkstra/page.html (same idea as qa_kosaraju.py).
    python simulations/algorithms.graph.dijkstra/qa.py [page.html] [screenshot folder]"""
import heapq
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().with_name("page.html")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[1] / "_build" / "qa" / Path(__file__).resolve().parent.name
OUT.mkdir(parents=True, exist_ok=True)


def reference(edges, nodes, s):
    g = {n: [] for n in nodes}
    for a, b, w in edges:
        g[a].append((b, w))
    dist = {n: None for n in nodes}
    pq = [(0, s)]
    while pq:
        d, u = heapq.heappop(pq)
        if dist[u] is not None:
            continue
        dist[u] = d
        for v, w in g[u]:
            if dist[v] is None:
                heapq.heappush(pq, (d + w, v))
    return dist   # None = unreachable


problems = []
with sync_playwright() as p:
    b = p.chromium.launch()
    for tag, w, h in [("desk", 1280, 900), ("phone", 390, 844)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(HTML.as_uri())
        pg.wait_for_timeout(300)
        shot = lambda name, full=False: pg.screenshot(path=str(OUT / f"{tag}_{name}.png"), full_page=full)
        step = lambda: pg.locator("#stepno").inner_text()
        jump_end = lambda: pg.evaluate("(() => { const s = document.getElementById('scrub'); s.value = s.max; s.dispatchEvent(new Event('input')); })()")

        if tag == "desk":
            presets = pg.evaluate("dijkstraSim.presets")
            for key, pr in presets.items():
                edges = [(e.split(":")[0].split(">")[0], e.split(":")[0].split(">")[1], int(e.split(":")[1])) for e in pr["edges"].split()]
                for src in sorted(pr["nodes"]):
                    got = pg.evaluate(f"dijkstraSim.run('{key}', '{src}')")["dist"]
                    got = {k: (None if v == float("inf") else v) for k, v in got.items()}
                    ref = reference(edges, list(pr["nodes"]), src)
                    if got != ref:
                        problems.append(f"{key} from {src}: page {got} vs reference {ref}")
                ref = reference(edges, list(pr["nodes"]), pr["source"])
                print(f"{key:9s} from {pr['source']}: {ref}")
                pg.select_option("#preset", key)
                jump_end()
                if "✓" not in pg.locator("#check").inner_text():
                    problems.append(key + " badge failed")
                table = pg.locator("#dist").inner_text()
                for n, d in ref.items():
                    want = "∞" if d is None else str(d)
                    row = [r for r in table.splitlines() if r.split("\t")[0].strip() == n]
                    if not row or row[0].split("\t")[1].strip() != want:
                        problems.append(f"{key}: table row for {n} is {row}, want {want}")
            pg.select_option("#preset", "textbook")

        # prediction question (empty -> error, then a value)
        pg.locator("#predBtn").click()
        if not pg.locator("#quiz .err").count():
            problems.append(f"{tag}: empty prediction was accepted")
        pg.fill("#predIn", "12")
        pg.locator("#predBtn").click()
        shot("01_start")
        total = int(step().split("/")[1])
        asked = False
        for i in range(1, total):
            if pg.locator("#nextBtn").is_disabled():
                break
            if pg.locator("[data-next]").count() and not asked:
                shot("03_next_quiz")
                pg.locator('[data-next="C"]').click()   # C (dist 2) is the right answer on the textbook graph
                if "Right" not in pg.locator("#quiz").inner_text():
                    problems.append(f"{tag}: next-node quiz did not accept C")
                asked = True
            pg.locator("#nextBtn").click()
            if i == 4:
                shot("02_relax")
            if i == 14:
                shot("04_middle")
        if not asked:
            problems.append(f"{tag}: next-node quiz never appeared")
        shot("05_done", full=True)
        if "correct" not in pg.locator("#explain").inner_text():
            problems.append(f"{tag}: prediction 12 for F not marked correct: {pg.locator('#explain').inner_text()}")
        pg.locator('.node[data-id="F"]').click()
        path = pg.locator("#pathbox").inner_text()
        if "A → C → B → D → E → F" not in path:
            problems.append(f"{tag}: path to F shown as {path!r}")
        shot("06_path_F", full=True)

        # other source
        pg.select_option("#source", "C")
        jump_end()
        if "✓" not in pg.locator("#check").inner_text():
            problems.append(f"{tag}: badge failed for source C")

        # edit: change weight A->C (2 -> 3) and add an edge
        pg.select_option("#preset", "trap")
        pg.locator("#editBtn").click()
        pg.locator('.wl[data-e="0"]').click()          # A->D weight 10 -> 1
        pg.locator('.node[data-id="B"]').click()
        pg.locator('.node[data-id="A"]').click()       # add B->A (5)
        shot("07_editing")
        pg.locator("#editBtn").click()
        jump_end()
        table = pg.locator("#dist").inner_text()
        if not any(r.startswith("D\t1") for r in table.splitlines()):
            problems.append(f"{tag}: after editing A->D to 1, D should be 1: {table!r}")
        if "✓" not in pg.locator("#check").inner_text():
            problems.append(f"{tag}: badge failed after editing")

        # keyboard + play
        pg.locator("#resetBtn").click()
        pg.locator("body").click(position={"x": 5, "y": 5})
        for _ in range(3):
            pg.keyboard.press("ArrowRight")
        if not step().startswith("Step 4 "):
            problems.append(f"{tag}: keyboard gave {step()}")
        pg.locator("#playBtn").click(); pg.wait_for_timeout(2600); pg.locator("#playBtn").click()
        if int(step().split()[1]) <= 4:
            problems.append(f"{tag}: play did not advance")
        print(tag, "page errors:", errs or "none")
        problems += [f"{tag}: {e}" for e in errs]
        pg.close()
    b.close()
print("PROBLEMS:", problems or "none")
sys.exit(1 if problems else 0)
