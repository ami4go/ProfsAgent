"""Headless check of simulations/os.scheduling.round_robin/page.html.

1. Hand-computed textbook answer (P1..P5, q=2) must match.
2. Page vs a separate Python implementation on every example and 400 random cases, both tie rules.
3. Click-through, questions, editing (incl. invalid input), quantum and tie-rule controls, screenshots.

    python simulations/os.scheduling.round_robin/qa.py [page.html] [screenshot folder]"""
import random
from collections import deque
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

HTML = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().with_name("page.html")
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).resolve().parents[1] / "_build" / "qa" / Path(__file__).resolve().parent.name
OUT.mkdir(parents=True, exist_ok=True)


def reference(procs, q, rule):
    order = sorted(range(len(procs)), key=lambda i: (procs[i]["at"], i))
    rem = {p["id"]: p["bt"] for p in procs}
    ct, queue, t, k = {}, deque(), 0, 0

    def admit(pred):
        nonlocal k
        while k < len(order) and pred(procs[order[k]]["at"]):
            queue.append(procs[order[k]]["id"]); k += 1

    admit(lambda a: a <= t)
    while len(ct) < len(procs):
        if not queue:
            t = procs[order[k]]["at"]; admit(lambda a: a <= t); continue
        p = queue.popleft(); run = min(q, rem[p]); t += run; rem[p] -= run
        admit(lambda a: a < t)
        if rem[p] == 0:
            ct[p] = t; admit(lambda a: a <= t)
        elif rule == "preemptedFirst":
            queue.append(p); admit(lambda a: a <= t)
        else:
            admit(lambda a: a <= t); queue.append(p)
    return ct


problems = []
with sync_playwright() as pw:
    b = pw.chromium.launch()
    for tag, w, h in [("desk", 1280, 900), ("phone", 390, 844)]:
        pg = b.new_page(viewport={"width": w, "height": h})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
        pg.goto(HTML.as_uri()); pg.wait_for_timeout(300)
        shot = lambda name, full=False: pg.screenshot(path=str(OUT / f"{tag}_{name}.png"), full_page=full)
        step = lambda: pg.locator("#stepno").inner_text()
        jump_end = lambda: pg.evaluate("(() => { const s = document.getElementById('scrub'); s.value = s.max; s.dispatchEvent(new Event('input')); })()")

        if tag == "desk":
            # 1. hand-computed textbook answer
            tb = [{"id": i, "at": a, "bt": c} for i, a, c in [("P1", 0, 5), ("P2", 1, 3), ("P3", 2, 1), ("P4", 3, 2), ("P5", 4, 3)]]
            got = pg.evaluate("(p) => rrSim.run(p, 2, 'arrivalFirst').ct", tb)
            want = {"P1": 13, "P2": 12, "P3": 5, "P4": 9, "P5": 14}
            print("textbook finish times:", got, "OK" if got == want else "MISMATCH")
            if got != want:
                problems.append(f"textbook: {got} != hand answer {want}")
            # 2. examples + random cases, both rules
            presets = pg.evaluate("rrSim.presets")
            cases = [([{"id": i, "at": a, "bt": c} for i, a, c in pr["procs"]], pr["q"]) for pr in presets.values()]
            rnd = random.Random(7)
            for _ in range(400):
                n = rnd.randint(1, 6)
                cases.append(([{"id": f"P{j+1}", "at": rnd.randint(0, 10), "bt": rnd.randint(1, 8)} for j in range(n)], rnd.randint(1, 5)))
            bad = 0
            for procs, q in cases:
                for rule in ("arrivalFirst", "preemptedFirst"):
                    got = pg.evaluate("([p, q, r]) => rrSim.run(p, q, r).ct", [procs, q, rule])
                    ref = reference(procs, q, rule)
                    if got != ref:
                        bad += 1
                        if bad <= 3:
                            problems.append(f"mismatch {procs} q={q} {rule}: page {got} ref {ref}")
            print(f"compared {len(cases) * 2} cases, mismatches: {bad}")
            # tie rule changes the order on the 'tie' example
            pg.select_option("#preset", "tie"); jump_end()
            a = pg.evaluate("rrSim.run([{id:'P1',at:0,bt:4},{id:'P2',at:2,bt:2},{id:'P3',at:2,bt:3}], 2, 'arrivalFirst').gantt.map(g => g.id).join(',')")
            c = pg.evaluate("rrSim.run([{id:'P1',at:0,bt:4},{id:'P2',at:2,bt:2},{id:'P3',at:2,bt:3}], 2, 'preemptedFirst').gantt.map(g => g.id).join(',')")
            print("tie example order  arrival-first:", a, " preempted-first:", c)
            if a == c:
                problems.append("tie rule made no difference on the tie example")
            pg.select_option("#rule", "preemptedFirst"); jump_end()
            if "✓" not in pg.locator("#check").inner_text():
                problems.append("badge failed with preempted-first rule")
            shot("09_tie_rule", full=True)
            pg.select_option("#rule", "arrivalFirst")
            pg.select_option("#preset", "textbook")

        # 3. UI walk-through on the textbook example
        pg.locator('[data-predict="P3"]').click()
        shot("01_start")
        total = int(step().split("/")[1]); asked = False
        for i in range(1, total):
            if pg.locator("#nextBtn").is_disabled():
                break
            if pg.locator("[data-pick]").count() and not asked:
                shot("03_next_quiz")
                pg.locator("[data-pick]").first.click()
                asked = True
            pg.locator("#nextBtn").click()
            if i == 3:
                shot("02_dispatch")
            if i == 12:
                shot("04_middle")
        shot("05_done", full=True)
        if not asked:
            problems.append(f"{tag}: next-process question never appeared")
        ex = pg.locator("#explain").inner_text()
        if "correct" not in ex or "8.6" not in ex or "5.8" not in ex:
            problems.append(f"{tag}: final text wrong: {ex!r}")
        foot = pg.locator("#pfoot").inner_text()
        if "8.6" not in foot or "5.8" not in foot:
            problems.append(f"{tag}: averages row wrong: {foot!r}")
        # editing: invalid burst, then valid change, add and remove
        inp = pg.locator('input[data-j="0"][data-k="bt"]')
        inp.fill("0"); inp.dispatch_event("change")
        if not pg.locator("#perr .err").count():
            problems.append(f"{tag}: burst 0 was accepted")
        inp.fill("6"); inp.dispatch_event("change")
        if pg.locator("#perr .err").count():
            problems.append(f"{tag}: error stayed after a valid value")
        pg.locator("#addBtn").click()
        if pg.locator("#ptab tr").count() != 6:
            problems.append(f"{tag}: add process failed")
        pg.locator('[data-del="5"]').click()
        pg.evaluate("(() => { const q = document.getElementById('qIn'); q.value = 3; q.dispatchEvent(new Event('input')); })()")
        jump_end()
        if "✓" not in pg.locator("#check").inner_text():
            problems.append(f"{tag}: badge failed after edits")
        shot("06_edited", full=True)
        # keyboard + play
        pg.locator("#resetBtn").click(); pg.locator("body").click(position={"x": 5, "y": 5})
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
