"""Graphical convolution, step by step (Manim video). Signals and Systems (IIIT-D ECE250).

    x(t) = 1 for 0 <= t <= 2 (a rectangular pulse),   h(t) = e^(-t) u(t)
    y(t) = (x * h)(t) = integral of x(tau) h(t - tau) dtau
         = 0                    t < 0
           1 - e^(-t)           0 <= t < 2
           (e^2 - 1) e^(-t)     t >= 2

Nothing on screen is typed in by hand: the area readout is a numerical integral of the shaded product, the y(t) curve is
the closed form, and check_convolution() confirms before anything is drawn that the two agree, and that both agree with
numpy's own (discrete) convolution. The result is written next to this file as graphical_convolution_check.json.

    Temporary/manim_env/Scripts/python.exe -m manim -qm graphical_convolution.py GraphicalConvolution     (720p)
    Temporary/manim_env/Scripts/python.exe -m manim -qh graphical_convolution.py GraphicalConvolution     (1080p)
No LaTeX needed: formulas are Pango text (superscripts with <sup>).
"""
import json
from pathlib import Path

import numpy as np
from manim import (BLACK, DOWN, GREEN, GREY_B, GREY_D, LEFT, ORIGIN, RIGHT, UL, UP, WHITE, YELLOW, BLUE, Axes, Create, DashedLine, Dot, Square,
                   FadeIn, FadeOut, Line, MarkupText, Polygon, Rectangle, Scene, Text, ValueTracker, VGroup, VMobject, Write,
                   always_redraw, linear, smooth)

T0, T1 = -3.0, 6.5          # the tau axis and the t axis cover the same range, one above the other
W = 2.0                     # pulse width
FONT = "Segoe UI"
SOFT = "#9AA3B2"


# ------------------------------------------------------------------ the mathematics (computed, then checked)
def x(tau):
    tau = np.asarray(tau, float)
    return np.where((tau >= 0) & (tau <= W), 1.0, 0.0)


def h(t):
    t = np.asarray(t, float)
    return np.where(t >= 0, np.exp(-np.maximum(t, 0.0)), 0.0)


def y_exact(t):
    t = np.asarray(t, float)
    return np.where(t < 0, 0.0, np.where(t < W, 1 - np.exp(-t), (np.exp(W) - 1) * np.exp(-t)))


def y_area(t, n=4001):
    """The shaded area at shift t: the integral of x(tau) h(t - tau) over the overlap, by the trapezoid rule."""
    lo, hi = 0.0, min(t, W)
    if hi <= lo:
        return 0.0
    tau = np.linspace(lo, hi, n)
    return float(np.trapezoid(x(tau) * h(t - tau), tau))


def check_convolution() -> dict:
    ts = np.round(np.arange(T0, T1 + 1e-9, 0.01), 4)
    area = np.array([y_area(t) for t in ts])
    exact = y_exact(ts)
    dt = 1e-3                                         # independent check: numpy's discrete convolution of the samples
    grid = np.arange(0, 12, dt)
    conv = np.convolve(x(grid), h(grid))[: len(grid)] * dt
    disc = np.interp(ts, grid, conv, left=0.0)
    out = {"signals": {"x": "1 for 0 <= t <= 2", "h": "e^(-t) u(t)"},
           "max_difference_area_vs_formula": float(np.max(np.abs(area - exact))),
           "max_difference_numpy_convolve_vs_formula": float(np.max(np.abs(disc - exact))),
           "peak": {"t": W, "y": float(y_exact(W)), "formula": "1 - e^-2"},
           "points_checked": int(len(ts))}
    assert out["max_difference_area_vs_formula"] < 1e-6, out
    assert out["max_difference_numpy_convolve_vs_formula"] < 2e-3, out
    assert abs(ts[np.argmax(exact)] - W) < 0.011, "the largest output must be at t = 2"
    (Path(__file__).with_name("graphical_convolution_check.json")).write_text(json.dumps(out, indent=1), encoding="utf-8")
    return out


# ------------------------------------------------------------------ drawing helpers
def T(s, size=24, color=WHITE, **kw):
    return Text(s, font=FONT, font_size=size, color=color, **kw)


def M(s, size=24, color=WHITE):
    return MarkupText(s, font=FONT, font_size=size, color=color)


def num(v: float, d: int = 0) -> str:
    return f"{v:.{d}f}".replace("-", "−")


def poly(ax, pts, color, width=4):
    m = VMobject(color=color, stroke_width=width)
    m.set_points_as_corners([ax.c2p(a, b) for a, b in pts])
    return m


def x_pts():
    return [(T0, 0), (0, 0), (0, 1), (W, 1), (W, 0), (T1, 0)]


def h_pts():
    s = np.linspace(0, -T0, 120)            # up to tau = 3 (e^-3 ≈ 0.05), so the flipped copy stays inside the axis
    return [(T0, 0), (0, 0), (0, 1)] + [(a, float(np.exp(-a))) for a in s]


def h_shift_pts(t):
    """h(t - tau) as a function of tau: e^-(t - tau) for tau <= t, then 0. Its jump sits at tau = t."""
    if t <= T0:
        return [(T0, 0), (T1, 0)]
    right = min(t, T1)
    s = np.linspace(T0, right, 160)
    pts = [(a, float(np.exp(-(t - a)))) for a in s]
    if t < T1:
        pts += [(t, 0.0), (T1, 0.0)]
    return pts


class GraphicalConvolution(Scene):
    def construct(self):
        check = check_convolution()
        t = ValueTracker(0.0)
        tv = lambda: t.get_value()  # noqa: E731

        # ---------------- layout: tau axis on top, t axis below, aligned column for column
        top = Axes(x_range=[T0, T1, 1], y_range=[0, 1.25, 0.5], x_length=11.6, y_length=2.0, tips=False,
                   axis_config={"color": GREY_B, "stroke_width": 2}).move_to([0, 0.85, 0])
        bot = Axes(x_range=[T0, T1, 1], y_range=[0, 1.0, 0.5], x_length=11.6, y_length=1.7, tips=False,
                   axis_config={"color": GREY_B, "stroke_width": 2}).move_to([0, -2.55, 0])

        def ticks(ax, name, ylab):
            g = VGroup(*[T(num(v), 17, SOFT).next_to(ax.c2p(v, 0), DOWN, buff=0.1) for v in range(-2, 7)])
            g.add(T(name, 24, SOFT).next_to(ax.x_axis.get_end(), RIGHT, buff=0.12))
            g.add(T("1", 17, SOFT).next_to(ax.c2p(0, 1), LEFT, buff=0.1))
            if ylab:
                g.add(M(ylab, 20, SOFT).next_to(ax.c2p(T0, 1.0), UP + RIGHT, buff=0.05))
            return g

        title = T("Graphical convolution: flip, slide, multiply, add up the area", 28).to_edge(UP, buff=0.2)
        formula = M("y(t) = ∫ x(τ) h(t − τ) dτ", 24, YELLOW).next_to(title, DOWN, buff=0.1)
        names = ["1  Flip h", "2  Slide by t", "3  Multiply", "4  Area = y(t)", "5  Repeat for every t"]
        steps = VGroup(*[T(s, 19, GREY_D) for s in names]).arrange(RIGHT, buff=0.45).next_to(formula, DOWN, buff=0.12)

        def step(i):
            return [s.animate.set_color(YELLOW if k <= i else GREY_D) for k, s in enumerate(steps)]

        self.play(FadeIn(title), run_time=0.8)
        self.play(Write(formula), FadeIn(steps), run_time=1.2)

        # ---------------- the two signals on the tau axis, named in a fixed legend row above it
        top_ticks = ticks(top, "τ", "")
        self.play(Create(top), FadeIn(top_ticks), run_time=1.0)
        LY = steps.get_bottom()[1] - 0.3

        def key(color, markup, left_x):
            g = VGroup(Square(0.17, fill_color=color, fill_opacity=1, stroke_width=0), M(markup, 20, color)).arrange(RIGHT, buff=0.12)
            return g.move_to([0, LY, 0]).align_to([left_x, 0, 0], LEFT)

        xg = poly(top, x_pts(), BLUE)
        xk = key(BLUE, "x(τ) = 1 for 0 ≤ τ ≤ 2", -6.6)
        self.play(Create(xg), FadeIn(xk), run_time=1.2)
        hg = poly(top, h_pts(), YELLOW)
        hk = key(YELLOW, "h(τ) = e<sup>−τ</sup> for τ ≥ 0", -2.4)
        self.play(Create(hg), FadeIn(hk), run_time=1.2)
        self.wait(0.8)

        # ---------------- step 1: flip
        self.play(*step(0), run_time=0.4)
        hk2 = key(YELLOW, "h(−τ): h mirrored about τ = 0", -2.4)
        self.play(hg.animate.flip(UP, about_point=top.c2p(0, 0)), FadeOut(hk), FadeIn(hk2), run_time=1.8)
        self.wait(1.0)

        # ---------------- step 2: slide (the jump of h(t - tau) sits at tau = t)
        moving = always_redraw(lambda: poly(top, h_shift_pts(tv()), YELLOW))
        self.remove(hg)
        self.add(moving)
        hk3 = key(YELLOW, "h(t − τ): flipped, edge at τ = t", -2.4)
        self.play(*step(1), FadeOut(hk2), FadeIn(hk3), run_time=0.6)
        self.play(t.animate.set_value(-2.0), run_time=2.2, rate_func=smooth)
        self.wait(0.5)

        # ---------------- steps 3-4: multiply, shade, and the output axis
        def area():
            lo, hi = 0.0, min(tv(), W)
            if hi <= lo + 1e-4:
                return VMobject()
            s = np.linspace(lo, hi, 90)
            pts = [top.c2p(lo, 0)] + [top.c2p(a, float(np.exp(-(tv() - a)))) for a in s] + [top.c2p(hi, 0)]
            return Polygon(*pts, stroke_width=0, fill_color=GREEN, fill_opacity=0.6)

        shade = always_redraw(area)
        bot_ticks = ticks(bot, "t", "y(t)")
        trace = always_redraw(lambda: poly(bot, [(a, float(y_exact(a))) for a in np.linspace(T0, max(tv(), T0 + 0.01), max(2, int((tv() - T0) * 40)))], GREEN, 5))
        dot = always_redraw(lambda: Dot(bot.c2p(tv(), float(y_exact(tv()))), color=GREEN, radius=0.07))
        link = always_redraw(lambda: (DashedLine(top.c2p(tv(), 1.05), bot.c2p(tv(), float(y_exact(tv()))), dash_length=0.08, color=GREY_B,
                                                 stroke_width=2) if T0 < tv() < T1 else VMobject()).set_z_index(1))
        readout = always_redraw(lambda: M(f"t = {num(tv(), 2)}     shaded area = y(t) = {y_area(tv()):.3f}", 22, GREEN)
                                .move_to([3.15, -1.38, 0]).add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06).set_z_index(5))
        gk = key(GREEN, "x · h: its area is y(t)", 3.1)
        self.play(*step(3), Create(bot), FadeIn(bot_ticks), FadeIn(gk), run_time=1.0)
        self.add(shade, trace, dot, link, readout)
        self.wait(0.3)

        def caption(markup):
            c = M(markup, 21)
            if c.width > 13.4:
                c.scale_to_fit_width(13.4)
            return c.move_to([0, -0.9, 0]).add_background_rectangle(color=BLACK, opacity=0.9, buff=0.06).set_z_index(5)

        # Case 1: no overlap
        cap = caption("<b>Case 1 · t &lt; 0</b>: the flipped h has not reached the pulse, so the product is 0 everywhere → y(t) = 0")
        self.play(FadeIn(cap), run_time=0.6)
        self.play(t.animate.set_value(0.0), run_time=2.4, rate_func=linear)
        self.wait(0.5)
        sep0 = DashedLine(bot.c2p(0, 0), bot.c2p(0, 1.0), dash_length=0.06, color=GREY_D)

        # Case 2: partial overlap
        cap2 = caption("<b>Case 2 · 0 ≤ t &lt; 2</b>: overlap τ ∈ [0, t]   →   y(t) = ∫<sub>0</sub><sup>t</sup> e<sup>−(t−τ)</sup> dτ = 1 − e<sup>−t</sup>")
        self.play(FadeOut(cap), FadeIn(cap2), FadeIn(sep0), *step(4), run_time=0.6)
        self.play(t.animate.set_value(W), run_time=6.0, rate_func=linear)
        peak = M(f"Largest area at t = 2:  y(2) = 1 − e<sup>−2</sup> ≈ {float(y_exact(W)):.3f}", 22, GREEN)\
            .next_to(bot.c2p(W, 1.1), LEFT, buff=0.35).add_background_rectangle(color=BLACK, opacity=0.9, buff=0.05).set_z_index(5)
        self.play(FadeIn(peak), run_time=0.5)
        self.wait(1.5)
        sep2 = DashedLine(bot.c2p(W, 0), bot.c2p(W, 1.0), dash_length=0.06, color=GREY_D)

        # Case 3: the jump has passed the end of the pulse
        cap3 = caption("<b>Case 3 · t ≥ 2</b>: overlap τ ∈ [0, 2]   →   y(t) = ∫<sub>0</sub><sup>2</sup> e<sup>−(t−τ)</sup> dτ = (e<sup>2</sup> − 1) e<sup>−t</sup>")
        self.play(FadeOut(cap2), FadeOut(peak), FadeIn(cap3), FadeIn(sep2), run_time=0.6)
        self.play(t.animate.set_value(6.2), run_time=6.0, rate_func=linear)
        self.wait(0.8)

        # ---------------- summary
        cases = VGroup(M("t &lt; 0: no overlap", 19, SOFT), M("0 ≤ t &lt; 2: overlap grows", 19, SOFT), M("t ≥ 2: overlap fixed, h decays", 19, SOFT))
        cases[0].move_to(bot.c2p(-1.4, 1.2))
        cases[1].move_to(bot.c2p(1.0, 1.2))
        cases[2].move_to(bot.c2p(4.3, 1.2))
        top_stuff = VGroup(top, top_ticks, xg, moving, shade, xk, hk3, gk)
        self.play(FadeOut(cap3), FadeOut(readout), FadeOut(link), FadeOut(top_stuff), FadeIn(cases), run_time=0.9)
        box_lines = VGroup(
            M("<b>y(t) = x(t) * h(t)</b>", 26, GREEN),
            M("= 0                          for t &lt; 0", 22),
            M("= 1 − e<sup>−t</sup>                  for 0 ≤ t &lt; 2", 22),
            M("= (e<sup>2</sup> − 1) e<sup>−t</sup>          for t ≥ 2", 22),
            M(f"Checked: the shaded areas match the formula (largest difference {check['max_difference_area_vs_formula']:.0e}),", 17, SOFT),
            M(f"and numpy's convolution matches it too (largest difference {check['max_difference_numpy_convolve_vs_formula']:.0e}).", 17, SOFT),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        panel = Rectangle(width=box_lines.width + 0.6, height=box_lines.height + 0.45, fill_color="#111827", fill_opacity=0.93,
                          stroke_color=GREEN, stroke_width=2).move_to([0, 0.85, 0])
        box_lines.move_to(panel.get_center())
        self.play(FadeIn(panel), FadeIn(box_lines), run_time=1.0)
        self.wait(4.0)
