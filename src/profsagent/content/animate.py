"""Animated figures for the narrated video, made with Manim (pip install manim; no LaTeX needed).

    animate_deck(d, deck, cfg, seconds) -> {slide number: {path, x, y, w, h}}

Each flow figure of a deck becomes a short clip in the figure's own place and shape (render.py writes layout.json): the
steps appear one by one, each with its arrow, over about the time the slide's narration takes (`seconds`), then the
finished figure stays. narrate.py puts the clip over the static figure of slides_narrated.pptx, playing with the voice,
so the exported MP4 shows the process being built while it is explained. Clips are cached by their content in
material/<lecture>/anim/. No AI calls. Other figure kinds (code, tables) stay static.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from profsagent.content.models import LectureDeck

EMU_PER_IN = 914400


def _clip(steps: list[str], w_in: float, h_in: float, seconds: float, colors: dict, out: Path) -> Path:
    """Render one flow as an MP4: rounded boxes appear top to bottom (or left to right when wide), each with its arrow."""
    import manim as M
    accent, ink = "#" + colors["accent"], "#" + colors["ink"]
    wide = w_in > h_in * 1.6
    px_h = 720
    px_w = int(round(px_h * w_in / h_in / 2) * 2)
    frame_h = 8.0
    frame_w = frame_h * w_in / h_in
    per = max(0.6, min(2.5, (seconds * 0.7) / max(1, len(steps))))

    class Flow(M.Scene):
        def construct(self):
            n = len(steps)
            if wide:
                bw, bh = min(3.2, (frame_w - 0.6 * (n - 1) - 0.6) / n), 1.6
            else:
                bw, bh = frame_w * 0.8, min(1.3, (frame_h - 0.5 * (n - 1) - 0.4) / n)
            labels = [M.Text(s, font="Calibri", color=ink, font_size=36) for s in steps]
            k = min(min(bw * 0.88 / lb.width for lb in labels), min(bh * 0.5 / lb.height for lb in labels))  # one size for all
            boxes = []
            for lb in labels:
                lb.scale(k)
                boxes.append(M.VGroup(M.RoundedRectangle(corner_radius=0.15, width=bw, height=bh, color=accent, stroke_width=4), lb))
            group = M.VGroup(*boxes).arrange(M.RIGHT if wide else M.DOWN, buff=0.6 if wide else 0.5).move_to(M.ORIGIN)
            for i, b in enumerate(boxes):
                if i:
                    a, z = boxes[i - 1][0], b[0]
                    start, end = (a.get_right(), z.get_left()) if wide else (a.get_bottom(), z.get_top())
                    self.play(M.GrowArrow(M.Arrow(start, end, buff=0.05, color=accent, stroke_width=5)), run_time=per * 0.35)
                self.play(M.FadeIn(b, shift=(M.RIGHT if wide else M.DOWN) * 0.2), run_time=per * 0.65)
            self.wait(max(0.5, seconds - per * len(steps)))

    with M.tempconfig({"pixel_width": px_w, "pixel_height": px_h, "frame_height": frame_h, "frame_width": frame_w,
                       "frame_rate": 24, "background_color": "#FFFFFF", "media_dir": str(out.parent / "_manim"),
                       "output_file": out.stem, "disable_caching": True, "verbosity": "ERROR", "progress_bar": "none"}):
        scene = Flow()
        scene.render()
        made = Path(scene.renderer.file_writer.movie_file_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    made.replace(out)
    return out


def animate_deck(d: Path, deck: LectureDeck, cfg: dict, seconds: list[float]) -> dict[int, dict]:
    """`seconds`: narration length of each .pptx slide (index 0 = slide 1). Returns the clips by .pptx slide number."""
    layout = json.loads((d / "layout.json").read_text(encoding="utf-8"))
    by_no = dict(enumerate(deck.slides, 3))
    out = {}
    for fg in layout["figures"]:
        s = by_no.get(fg["slide"])
        if not s or fg["kind"] != "flow" or len(s.figure.steps) < 2:
            continue
        pad = int(0.08 * EMU_PER_IN)          # the clip covers the static figure's border strokes too
        fg = {**fg, "x": fg["x"] - pad, "y": fg["y"] - pad, "w": fg["w"] + 2 * pad, "h": fg["h"] + 2 * pad}
        w_in, h_in = fg["w"] / EMU_PER_IN, fg["h"] / EMU_PER_IN
        secs = seconds[fg["slide"] - 1] if fg["slide"] - 1 < len(seconds) else 8.0
        key = hashlib.sha1(json.dumps([2, s.figure.steps, round(w_in, 2), round(h_in, 2), round(secs), cfg["render"]["colors"]]).encode()).hexdigest()[:10]
        path = d / "anim" / f"slide_{fg['slide']:02d}_{key}.mp4"
        if not path.exists():
            _clip(s.figure.steps, w_in, h_in, secs, cfg["render"]["colors"], path)
        out[fg["slide"]] = {"path": str(path.resolve()), **{k: fg[k] for k in ("x", "y", "w", "h")}}
    return out
