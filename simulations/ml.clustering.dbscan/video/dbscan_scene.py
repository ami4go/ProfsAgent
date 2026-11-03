"""DBSCAN, step by step (Manim video). Machine Learning (IIIT-D CSE343 / AI201).

45 points, eps = 0.62, minPts = 4. Everything drawn comes from dbscan_core.run(): which points are core, border or noise,
the order they are visited, and each wave of points a cluster reaches. Before rendering, dbscan_core.check() compares
the result with scikit-learn's DBSCAN (same core points, same noise, same clusters); the scene refuses to render if
they differ, and writes the comparison to dbscan_check.json.

    Temporary/manim_env/Scripts/python.exe -m manim -ql dbscan_scene.py DBSCANScene     (draft)
    Temporary/manim_env/Scripts/python.exe -m manim -qh --frame_rate 30 dbscan_scene.py DBSCANScene     (1080p)
"""
import json
from pathlib import Path

import numpy as np
from manim import (BLACK, DOWN, GREY_B, GREY_C, LEFT, ORIGIN, RIGHT, UP, WHITE, YELLOW, Circle, Create, DashedVMobject, Dot,
                   FadeIn, FadeOut, Flash, Indicate, Line, MarkupText, Rectangle, RoundedRectangle, Scene, Text, Transform,
                   VGroup)

from dbscan_core import NOISE, check, dataset, run

FONT = "Segoe UI"
SOFT = "#9AA3B2"
EPS, MINPTS, SEED = 0.62, 4, 3
COL = ["#58C4DD", "#F5A623", "#83C167"]          # cluster 1, 2, 3
GREYX = "#8B93A1"
S_ = 1.1                                           # screen units per data unit
CX, CY = -2.35, -0.3                               # where the data centre goes on screen


def T(s, size=22, color=WHITE, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def M(s, size=22, color=WHITE):
    return MarkupText(s, font=FONT, font_size=size, color=color)


class DBSCANScene(Scene):
    def construct(self):
        P = dataset(SEED)
        order = np.random.RandomState(SEED + 1000).permutation(len(P)).tolist()
        R = run(P, EPS, MINPTS, order)
        ck = check(P, EPS, MINPTS, R)
        (Path(__file__).with_name("dbscan_check.json")).write_text(json.dumps(ck, indent=1), encoding="utf-8")
        assert ck["passed"], ck
        n = len(P)
        DX, DY = (P[:, 0].min() + P[:, 0].max()) / 2, (P[:, 1].min() + P[:, 1].max()) / 2
        S = lambda i: np.array([CX + S_ * (P[i][0] - DX), CY + S_ * (P[i][1] - DY), 0.0])  # noqa: E731
        r_eps = EPS * S_

        # ---------------- point looks
        def m_unseen(i):
            return Dot(S(i), radius=0.065, color=WHITE)

        def m_core(i, c):
            return Dot(S(i), radius=0.1, color=COL[c])

        def m_border(i, c):
            return Circle(radius=0.095, stroke_color=COL[c], stroke_width=4, fill_color=BLACK, fill_opacity=1).move_to(S(i))

        def m_noise(i):
            p, d = S(i), 0.085
            return VGroup(Line(p + [-d, -d, 0], p + [d, d, 0]), Line(p + [-d, d, 0], p + [d, -d, 0])).set_stroke(GREYX, 4)

        def eps_circle(i, color=YELLOW, fill=0.08, dashed=True):
            c = Circle(radius=r_eps, stroke_color=color, stroke_width=2.5, fill_color=color, fill_opacity=fill).move_to(S(i))
            return VGroup(c.copy().set_stroke(width=0), DashedVMobject(c, num_dashes=44)) if dashed else c

        def halos(idx, color=YELLOW):
            return VGroup(*[Circle(radius=0.17, stroke_color=color, stroke_width=2.5).move_to(S(j)) for j in idx])

        # ---------------- header, frame, side panel
        title = T("DBSCAN: finding clusters by density", 32).to_edge(UP, buff=0.22)
        sub = T("Density-Based Spatial Clustering of Applications with Noise", 19, SOFT).next_to(title, DOWN, buff=0.08)
        frame = RoundedRectangle(corner_radius=0.15, width=8.25, height=5.75, stroke_color="#2A3140", stroke_width=2).move_to([CX, CY - 0.02, 0])
        px = 2.35                                          # left edge of the side panel

        def left(m, y):
            return m.move_to([0, y, 0]).align_to([px, 0, 0], LEFT)

        settings = VGroup(
            left(T("Settings", 22, WHITE, weight="BOLD"), 2.35),
            left(M(f"ε = {EPS}   <span foreground='{SOFT}'>circle radius</span>", 20), 1.98),
            left(M(f"minPts = {MINPTS}   <span foreground='{SOFT}'>points needed inside</span>", 20), 1.64))
        key_rows = [(Dot(radius=0.1, color=COL[0]), "core point: ≥ minPts within ε"),
                    (Circle(radius=0.095, stroke_color=COL[0], stroke_width=4), "border point: near a core point"),
                    (m_noise(0).move_to(ORIGIN), "noise: neither (an outlier)"),
                    (Dot(radius=0.065, color=WHITE), "not visited yet")]
        legend = VGroup(left(T("Labels", 22, WHITE, weight="BOLD"), 1.12))
        for k, (mk, txt) in enumerate(key_rows):
            y = 0.78 - 0.32 * k
            mk.move_to([px + 0.12, y, 0])
            legend.add(mk, T(txt, 19).move_to([0, y, 0]).align_to([px + 0.4, 0, 0], LEFT))

        def counters(vis, k, nz):
            return VGroup(left(T("Progress", 22, WHITE, weight="BOLD"), -0.72),
                          left(T(f"Visited  {vis} / {n}", 20), -1.06), left(T(f"Clusters  {k}", 20), -1.37),
                          left(T(f"Noise  {nz}", 20, GREYX), -1.68))

        state = {"vis": 0, "k": 0, "nz": 0}
        cnt = counters(0, 0, 0)

        def recount():
            new = counters(state["vis"], state["k"], state["nz"])
            return Transform(cnt, new)

        cap = T(" ", 22).move_to([0, -3.5, 0])

        def caption(markup, size=22):
            c = M(markup, size)
            if c.width > 13.6:
                c.scale_to_fit_width(13.6)
            return c.move_to([0, -3.5, 0])

        def say(markup, size=22, rt=0.5):
            new = caption(markup, size)
            self.play(Transform(cap, new), run_time=rt)

        dots = {i: m_unseen(i) for i in range(n)}
        self.play(FadeIn(title), FadeIn(sub), run_time=0.8)
        self.play(Create(frame), FadeIn(settings), FadeIn(legend), FadeIn(cnt), run_time=1.0)
        self.add(cap)
        self.play(*[FadeIn(d, scale=0.5) for d in dots.values()], run_time=1.2)
        say("45 points, no labels. DBSCAN groups points that are <b>packed closely together</b>, and leaves lonely points out as <b>noise</b>.")
        self.wait(2.0)

        # ---------------- the three kinds of point, on real examples
        nb = R["nbrs"]
        core_ex = max((i for i in range(n) if R["core"][i]), key=lambda i: len(nb[i]))
        border_ex = next(i for i in range(n) if R["labels"][i] >= 0 and not R["core"][i] and len(nb[i]) == 3)
        noise_ex = next(i for i in range(n) if R["labels"][i] == NOISE and S(i)[0] > -1)

        def explain(i, markup, final):
            circ, hal = eps_circle(i), halos(nb[i])
            num = T(f"{len(nb[i])} inside", 19, YELLOW).next_to(circ, UP, buff=0.05)
            self.play(Create(circ), run_time=0.6)
            self.play(FadeIn(hal), FadeIn(num), run_time=0.6)
            say(markup, 22)
            self.wait(2.2)
            self.play(Transform(dots[i], final), FadeOut(circ), FadeOut(hal), FadeOut(num), run_time=0.6)

        explain(core_ex, f"<b>Core point</b>: {len(nb[core_ex])} points lie within ε (counting itself), at least minPts = {MINPTS}.",
                m_core(core_ex, 0).set_color(WHITE))
        near_core = next(j for j in nb[border_ex] if R["core"][j])
        explain(border_ex, f"<b>Border point</b>: only {len(nb[border_ex])} within ε (fewer than {MINPTS}), but one of them is a core point, so it belongs to that cluster.",
                Circle(radius=0.095, stroke_color=WHITE, stroke_width=4, fill_color=BLACK, fill_opacity=1).move_to(S(border_ex)))
        explain(noise_ex, f"<b>Noise</b>: only {len(nb[noise_ex])} within ε (itself), and no core point is that close. It stays an outlier.",
                m_noise(noise_ex).set_stroke(WHITE))
        self.play(*[Transform(dots[i], m_unseen(i)) for i in (core_ex, border_ex, noise_ex)], run_time=0.5)
        say("Now the algorithm: visit points one by one, in a random order. <b>Every point gets exactly one label.</b>")
        self.wait(1.6)

        # ---------------- run DBSCAN, event by event
        first_noise = True
        for ev in R["events"]:
            if ev[0] == "noise":
                i = ev[1]
                ring, circ, hal = Circle(radius=0.2, stroke_color=YELLOW, stroke_width=4).move_to(S(i)), eps_circle(i), halos(nb[i])
                state["vis"] += 1
                state["nz"] += 1
                fast = not first_noise
                self.play(FadeIn(ring), Create(circ), FadeIn(hal), run_time=0.35 if fast else 0.7)
                if first_noise:
                    say(f"Visit a point: only {len(nb[i])} within ε, not a core point, and no cluster has reached it → mark it <b>noise (for now)</b>.")
                    self.wait(1.4)
                else:
                    say(f"Visit: {len(nb[i])} within ε → <b>noise</b> (for now).", rt=0.3)
                self.play(Transform(dots[i], m_noise(i)), FadeOut(ring), FadeOut(circ), FadeOut(hal), recount(),
                          run_time=0.35 if fast else 0.6)
                first_noise = False
            elif ev[0] == "seed":
                i, c = ev[1], ev[2]
                ring, circ, hal = Circle(radius=0.2, stroke_color=YELLOW, stroke_width=4).move_to(S(i)), eps_circle(i), halos(nb[i])
                state["vis"] += 1
                state["k"] += 1
                self.play(FadeIn(ring), Create(circ), FadeIn(hal), run_time=0.6)
                say(f"Visit: {len(nb[i])} within ε ≥ {MINPTS} → a <b>core point</b>. It starts "
                    f"<span foreground='{COL[c]}'><b>Cluster {c + 1}</b></span>.", rt=0.4)
                self.wait(0.9 if c == 0 else 0.4)
                self.play(Transform(dots[i], m_core(i, c)), FadeOut(ring), FadeOut(circ), FadeOut(hal), recount(), run_time=0.5)
                frontier = [i]
                waves_seen = 0
            elif ev[0] == "wave":
                c, wave = ev[1], ev[2]
                waves_seen += 1
                circles = VGroup(*[eps_circle(f, COL[c], 0.07) for f in frontier])
                detail = c == 0 and waves_seen <= 2
                self.play(FadeIn(circles), run_time=0.5 if detail else 0.3)
                if c == 0 and waves_seen == 1:
                    say(f"<b>Expand</b>: every point inside a core point's circle joins <span foreground='{COL[c]}'><b>Cluster 1</b></span>. "
                        "Core points among them spread the cluster further.")
                    self.wait(1.6)
                anims, flashes = [], []
                for j, kind, from_noise in wave:
                    anims.append(Transform(dots[j], m_core(j, c) if kind == "core" else m_border(j, c)))
                    if from_noise:
                        flashes.append(j)
                        state["nz"] -= 1
                    else:
                        state["vis"] += 1
                self.play(*anims, recount(), run_time=0.7 if detail else 0.45)
                for j in flashes:
                    self.play(Flash(S(j), color=COL[c], line_length=0.18, flash_radius=0.24), run_time=0.6)
                    say(f"This point was marked noise earlier, but it lies within ε of a core point → it becomes a <b>border point</b> "
                        f"of <span foreground='{COL[c]}'><b>Cluster {c + 1}</b></span>.")
                    self.wait(1.8)
                self.play(FadeOut(circles), run_time=0.3)
                frontier = [j for j, kind, _ in wave if kind == "core"]
                if not frontier:
                    members = [k for k in range(n) if R["labels"][k] == c]
                    say(f"No more points within reach: <span foreground='{COL[c]}'><b>Cluster {c + 1}</b></span> is complete "
                        f"({len(members)} points).", rt=0.4)
                    self.wait(0.8)
        # ---------------- result: a tag next to each cluster, in the emptiest nearby spot, and the list in the side panel
        allp = np.array([S(k)[:2] for k in range(n)])
        tags, placed = VGroup(), []
        for c in range(R["n_clusters"]):
            mem = allp[[k for k in range(n) if R["labels"][k] == c]]
            (x0, y0), (x1, y1) = mem.min(0), mem.max(0)
            tag = T(f"Cluster {c + 1}", 19, COL[c], weight="BOLD")
            w, h = tag.width / 2 + 0.12, tag.height / 2 + 0.1
            cands = [((x0 + x1) / 2, y1 + 0.38), ((x0 + x1) / 2, y0 - 0.38), (x0 - w - 0.2, (y0 + y1) / 2), (x1 + w + 0.2, (y0 + y1) / 2),
                     (x0 - w, y1 + 0.3), (x1 + w, y1 + 0.3), (x0 - w, y0 - 0.3), (x1 + w, y0 - 0.3)]

            def clearance(q):
                box = np.array([[q[0] + dx * w, q[1] + dy * h] for dx in (-1, 0, 1) for dy in (-1, 0, 1)])
                d_pts = np.min(np.linalg.norm(allp[None, :, :] - box[:, None, :], axis=2))
                d_tags = min([np.hypot(q[0] - r[0], q[1] - r[1]) - 1.4 for r in placed] or [9])
                return min(d_pts, d_tags)
            inside = [q for q in cands if -6.35 + w < q[0] < 1.65 - w and -2.8 + h < q[1] < 2.45 - h]
            best = max(inside, key=clearance)
            placed.append(best)
            tags.add(tag.move_to([best[0], best[1], 0]))
        noise_pts = [k for k in range(n) if R["labels"][k] == NOISE]
        rows = [T("Result", 22, WHITE, weight="BOLD")]
        for c in range(R["n_clusters"]):
            mem = [k for k in range(n) if R["labels"][k] == c]
            core_n = sum(R["core"][k] for k in mem)
            rows.append(T(f"Cluster {c + 1}:  {len(mem)} points ({core_n} core, {len(mem) - core_n} border)", 18, COL[c]))
        rows.append(T(f"Noise:  {len(noise_pts)} points", 18, GREYX))
        result = VGroup(*[left(r, -0.72 - 0.32 * k) for k, r in enumerate(rows)])
        self.play(FadeIn(tags), FadeOut(cnt), FadeIn(result), *[Indicate(dots[k], color=GREYX, scale_factor=1.6) for k in noise_pts], run_time=1.2)
        say(f"Done: <b>{R['n_clusters']} clusters</b> of different shapes (a blob, a strip and an arc) and <b>{len(noise_pts)} noise points</b>, "
            "without saying how many clusters to look for.", 21)
        self.wait(2.8)
        say("Why DBSCAN: no need to fix the number of clusters · clusters of any shape · outliers marked as noise. "
            "But ε and minPts must suit the data.", 20)
        self.wait(3.2)
        say(f"Checked: scikit-learn's DBSCAN on the same {n} points gives the same core points, the same noise and the same "
            f"{ck['clusters_sklearn']} clusters.", 20)
        self.wait(4.0)
