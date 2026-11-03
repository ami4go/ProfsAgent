"""Headless check of simulations/dbms.index.bplus_tree/page.html.

1. Fuzz: random insert/delete sequences for max 3, 4, 5 keys per page; every final tree is checked by a
   separate Python rule checker, and the page's own after-every-operation check must report nothing.
2. Coverage: the fuzz must include cascading splits (3+ levels), cascading merges (2+) and root shrinks.
3. Examples and UI walk-through, with screenshots.

    python simulations/dbms.index.bplus_tree/qa.py [page.html] [screenshot folder]"""
import math
import random
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().with_name("page.html")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[1] / "_build" / "qa" / Path(__file__).resolve().parent.name
OUT.mkdir(parents=True, exist_ok=True)


def check_tree(T, expected):
    M, nodes, root = T["M"], {int(k): v for k, v in T["nodes"].items()}, T["root"]
    errs, depths, leaves = [], set(), []

    def walk(i, d, lo, hi):
        n, ks = nodes[i], nodes[i]["keys"]
        if ks != sorted(set(ks)):
            errs.append("unsorted page")
        if len(ks) > M:
            errs.append("page over max")
        if n["leaf"]:
            if i != root and len(ks) < math.ceil(M / 2):
                errs.append("leaf under min")
            if any((lo is not None and k < lo) or (hi is not None and k >= hi) for k in ks):
                errs.append("key under wrong signpost")
            depths.add(d); leaves.append(i)
        else:
            if len(n["ch"]) != len(ks) + 1:
                errs.append("pointer count")
            if len(ks) < (1 if i == root else M // 2):
                errs.append("index page under min")
            for j, c in enumerate(n["ch"]):
                walk(c, d + 1, lo if j == 0 else ks[j - 1], hi if j == len(ks) else ks[j])

    walk(root, 0, None, None)
    if len(depths) > 1:
        errs.append("leaves at different depths")
    chain, x = [], leaves[0] if leaves else None
    while x is not None:
        chain.append(x); x = nodes[x]["next"]
    if chain != leaves:
        errs.append("leaf chain broken")
    if [k for l in leaves for k in nodes[l]["keys"]] != sorted(expected):
        errs.append("keys differ from model")
    return errs


problems = []
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 1280, "height": 900})
    errs_page = []
    pg.on("pageerror", lambda e: errs_page.append(str(e)))
    pg.goto(HTML.as_uri()); pg.wait_for_timeout(400)

    # 0. the textbook example (order 3, middle key copied up) must give exactly the hand-worked tree
    def levels(T):
        nodes, out, row = {int(k): v for k, v in T["nodes"].items()}, [], [T["root"]]
        while row:
            out.append([nodes[i]["keys"] for i in row])
            row = [c for i in row for c in nodes[i]["ch"]]
        return out
    ref_ops = [["i", k] for k in (2, 6, 10, 20, 78, 5, 90)]
    got = levels(pg.evaluate("ops => bptSim.run(2, ops, { mode: 'children', leafBias: 'right', midBias: 'right' }).tree", ref_ops))
    want = [[[10]], [[6], [20, 78]], [[2, 5], [6], [10], [20], [78, 90]]]
    print("textbook order-3 example:", got, "OK" if got == want else "MISMATCH")
    if got != want:
        problems.append(f"order-3 textbook example: {got} != {want}")
    other = levels(pg.evaluate("ops => bptSim.run(2, ops, { leafBias: 'left' }).tree", ref_ops))
    print("same keys with 'extra key to the left page':", other)

    # 1-2. fuzz
    rnd = random.Random(5)
    CFGS = [{"leafBias": a, "midBias": b} for a in ("left", "right") for b in ("left", "right")]
    cover = {"splits3": 0, "merges2": 0, "shrank": 0}
    runs = 0
    for M in range(2, 11):
        for run in range(130 if M in (3, 4, 5) else 40):
            model, ops = set(), []
            if run < 10:   # sorted runs force the deepest cascades (ascending, descending, then delete all)
                seq = list(range(1, 151)) if run % 2 == 0 else list(range(150, 0, -1))
                ops = [["i", k] for k in seq] + [["d", k] for k in (seq if run % 4 < 2 else seq[::-1])]
            space, length = (90, rnd.randint(20, 140)) if run % 2 else (400, rnd.randint(100, 320))
            for _ in range(0 if run < 10 else length):
                if model and rnd.random() < 0.4:
                    k = rnd.choice(sorted(model)) if rnd.random() < 0.9 else rnd.randint(1, space)
                    ops.append(["d", k]); model.discard(k)
                else:
                    k = rnd.randint(1, space); ops.append(["i", k]); model.add(k)
            # delete everything at the end sometimes, to force full shrink
            if rnd.random() < 0.3:
                for k in rnd.sample(sorted(model), len(model)):
                    ops.append(["d", k]); model.discard(k)
            cfg = CFGS[run % 4]
            r = pg.evaluate("([M, ops, cfg]) => bptSim.run(M, ops, cfg)", [M, ops, cfg])
            runs += 1
            if r["errs"]:
                problems.append(f"M={M} {cfg}: page check failed: {r['errs'][0]}")
            e = check_tree(r["tree"], model)
            if e:
                problems.append(f"M={M} {cfg}: python check failed: {e[0]} (ops {ops[:8]}...)")
            cover["splits3"] += r["maxSplits"] >= 3
            cover["merges2"] += r["maxMerges"] >= 2
            cover["shrank"] += r["shrank"] > 0
    print(f"fuzz: {runs} random sequences checked; runs with 3+ cascading splits: {cover['splits3']}, 2+ cascading merges: {cover['merges2']}, root shrink: {cover['shrank']}")
    if not all(cover.values()):
        problems.append(f"cascades not covered: {cover}")

    # 3. examples
    def texts_from(first_only=False):
        n = int(pg.evaluate("document.getElementById('scrub').max"))
        start = int(pg.evaluate("document.getElementById('scrub').value"))
        out = []
        for i in range(start, n + 1):
            pg.evaluate(f"(() => {{ const s = document.getElementById('scrub'); s.value = {i}; s.dispatchEvent(new Event('input')); }})()")
            out.append(pg.inner_text("#explain"))
        return out

    expect = {"order3": ["Insert 90 done", "extra key goes to the right page", "copy the first key of the right page, 6"], "splits": ["new root", "The leaf has", "The index page has"], "merges": ["merge", "shrinks one level"],
              "borrow": ["borrow"], "range": ["15, 20, 25, 30, 35"], "build": ["Insert 17 done"], "big": ["40 random keys"]}
    for ex, needles in expect.items():
        pg.select_option("#ex", ex); pg.wait_for_timeout(200)
        pg.screenshot(path=str(OUT / f"ex_{ex}_start.png"), full_page=True)
        t = " ".join(texts_from())
        for nd in needles:
            if nd not in t:
                problems.append(f"example {ex}: missing '{nd}'")
        if "✓" not in pg.inner_text("#check"):
            problems.append(f"example {ex}: badge {pg.inner_text('#check')[:120]}")
        if ex == "splits":
            print("splits example:", [x for x in t.split(". ") if "new root" in x][:1])
        pg.screenshot(path=str(OUT / f"ex_{ex}_end.png"), full_page=True)

    # mid-step screenshots of the cascading examples
    for ex, label in [("splits", "overflow"), ("merges", "underflow")]:
        pg.select_option("#ex", ex)
        n = int(pg.evaluate("document.getElementById('scrub').max"))
        for i in range(n + 1):
            pg.evaluate(f"(() => {{ const s = document.getElementById('scrub'); s.value = {i}; s.dispatchEvent(new Event('input')); }})()")
            if "cascaded" in pg.inner_text("#explain"):
                pg.screenshot(path=str(OUT / f"cascade_{ex}.png"), full_page=True); break

    # UI walk-through
    pg.select_option("#ex", "build")
    pg.fill("#key", "25"); pg.click("#insBtn"); pg.wait_for_timeout(100)
    if not pg.locator("[data-p]").count():
        problems.append("insert question missing")
    pg.locator('[data-p="1"]').click()
    pg.click("#playBtn"); pg.wait_for_timeout(9000)
    if "Insert 25 done" not in pg.inner_text("#explain"):
        problems.append("play did not finish insert 25: " + pg.inner_text("#explain")[:120])
    pg.screenshot(path=str(OUT / "ui_insert25.png"), full_page=True)
    pg.fill("#key", "abc"); pg.click("#insBtn")
    if not pg.locator("#ferr .err").count():
        problems.append("bad key accepted")
    pg.fill("#key", "6"); pg.click("#delBtn")
    pg.evaluate("(() => { const s = document.getElementById('scrub'); s.value = s.max; s.dispatchEvent(new Event('input')); })()")
    if "Delete 6 done" not in pg.inner_text("#explain"):
        problems.append("delete 6 did not finish")
    pg.fill("#key", "12"); pg.click("#findBtn")
    pg.evaluate("(() => { const s = document.getElementById('scrub'); s.value = s.max; s.dispatchEvent(new Event('input')); })()")
    if "Found" not in pg.inner_text("#explain"):
        problems.append("find 12 failed")
    # typed setup: rebuild the current keys with max 5 (no steps)
    pg.select_option("#sizeMode", "keys"); pg.click("#useBtn"); pg.fill("#M", "5"); pg.uncheck("#stepsChk"); pg.click("#buildBtn"); pg.wait_for_timeout(200)
    if "Built a tree" not in pg.inner_text("#explain") or "Up to 5 keys per page" not in pg.inner_text("#stats") or "✓" not in pg.inner_text("#check"):
        problems.append("rebuild with typed max 5 failed: " + pg.inner_text("#explain")[:100])
    pg.screenshot(path=str(OUT / "ui_rebuilt_max5.png"), full_page=True)
    for bad in ("1", "11", "x", ""):
        pg.fill("#M", bad); pg.click("#buildBtn")
        if not pg.locator("#ferr .err").count():
            problems.append(f"max keys {bad!r} accepted")
    pg.fill("#M", "2"); pg.fill("#list", "5 1 9 3 7 2 8 4 6 5"); pg.check("#stepsChk"); pg.click("#buildBtn"); pg.wait_for_timeout(200)
    if "1 repeated key was skipped" not in pg.inner_text("#explain"):
        problems.append("duplicate note missing: " + pg.inner_text("#explain")[:120])
    pg.evaluate("(() => { const s = document.getElementById('scrub'); s.value = s.max; s.dispatchEvent(new Event('input')); })()")
    if "Insert 6 done" not in pg.inner_text("#explain") or "Up to 2 keys per page" not in pg.inner_text("#stats") or "✓" not in pg.inner_text("#check"):
        problems.append("max 2 build failed: " + pg.inner_text("#explain")[:120])
    pg.screenshot(path=str(OUT / "ui_max2.png"), full_page=True)
    pg.fill("#M", "7"); pg.fill("#list", " ".join(str(k) for k in range(3, 120, 3))); pg.uncheck("#stepsChk"); pg.click("#buildBtn"); pg.wait_for_timeout(200)
    if "Up to 7 keys per page" not in pg.inner_text("#stats") or "39 keys" not in pg.inner_text("#stats"):
        problems.append("max 7 build failed: " + pg.inner_text("#stats"))
    pg.screenshot(path=str(OUT / "ui_max7.png"), full_page=True)
    pg.fill("#list", ""); pg.click("#buildBtn")
    if "empty tree" not in pg.inner_text("#explain"):
        problems.append("empty initial keys failed")
    pg.fill("#list", " ".join(str(k) for k in range(1, 62))); pg.click("#buildBtn")
    if not pg.locator("#ferr .err").count():
        problems.append("61 keys accepted")
    pg.fill("#ra", "30"); pg.fill("#rb", "10"); pg.click("#rangeBtn")
    if not pg.locator("#ferr .err").count():
        problems.append("reversed range accepted")
    pg.fill("#list", "8 3 1 9 4 2"); pg.click("#buildBtn")
    if "✓" not in pg.inner_text("#check"):
        problems.append("build list badge failed")
    # order mode: order 3..11 only
    pg.select_option("#sizeMode", "children")
    for bad in ("2", "12"):
        pg.fill("#M", bad); pg.click("#buildBtn")
        if not pg.locator("#ferr .err").count():
            problems.append(f"order {bad} accepted")
    pg.fill("#M", "4"); pg.fill("#list", "1 2 3 4 5 6 7 8 9 10"); pg.click("#buildBtn")
    if "Order 4" not in pg.inner_text("#stats") or "✓" not in pg.inner_text("#check"):
        problems.append("order 4 build failed: " + pg.inner_text("#stats"))
    print("page errors:", errs_page or "none")
    problems += errs_page
    pg.close()

    ph = b.new_page(viewport={"width": 390, "height": 844})
    ph.goto(HTML.as_uri()); ph.wait_for_timeout(300)
    ph.select_option("#ex", "splits")
    ph.evaluate("(() => { const s = document.getElementById('scrub'); s.value = s.max; s.dispatchEvent(new Event('input')); })()")
    ph.screenshot(path=str(OUT / "phone_splits_end.png"), full_page=True)
    ph.close()
    b.close()
print("PROBLEMS:", problems or "none")
sys.exit(1 if problems else 0)
