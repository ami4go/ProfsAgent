"""Narration for a generated deck: each slide read aloud from its speaker notes, as a narrated .pptx and, optionally, an
MP4 video (the "series of 10-15 minute videos": a class's notes run about that long when read).

    narrate(material_dir, deck, frame, cfg, video=False) -> manifest entry

1. script   one text per .pptx slide (narration_script): the title and objectives from the frame, each content slide's
            notes; a question is read with its options, a pause, then the answer and why.
2. voice    one WAV per slide with the Windows speech synthesizer (System.Speech, offline, no install; the voice in
            config/content.yaml `narration.voice`).
3. deck     slides_narrated.pptx through PowerPoint: each slide plays its audio on entry and advances when it ends.
4. video    with video=True, PowerPoint exports slides_narrated.mp4 using those timings.
Windows with PowerPoint only (both are driven from PowerShell); elsewhere it raises NarrationUnavailable.
The audio, the narrated deck and the video are large, so they are not committed (.gitignore).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

from profsagent.content.models import LectureDeck
from profsagent.content.render import answer

LETTERS = "ABCDE"


class NarrationUnavailable(RuntimeError):
    pass


def _speakable(text: str) -> str:
    """Text as a voice should read it: no markdown, arrows and ids spelled out, one line."""
    t = re.sub(r"[`*_#>]", "", text or "")
    t = t.replace("→", " to ").replace("≈", " about ").replace("–", " to ").replace("&", " and ")
    t = re.sub(r"\(CO\d+\.LO\d+\)", "", t)
    t = re.sub(r"\[([CL]\d+)\]", "", t)
    return re.sub(r"\s+", " ", t).strip()


def narration_script(deck: LectureDeck, frame: dict) -> list[str]:
    """One text per slide of slides.pptx, in order: title, objectives, the content slides, references."""
    out = [f"{frame['course']}. {deck.title}. {frame['subtitle'].replace('·', ',')}.",
           "In this class you will learn to: " + " ".join(f"{o.rstrip('.')}." for o in frame["objectives"])]
    for s in deck.slides:
        text = s.notes
        if s.kind == "watch" and s.clip:
            text += f" Now watch: {s.clip}."
        if s.kind == "simulation" and s.link:
            text += f" Open the simulation: {s.link.split(' — ')[0]}."
        q = s.quiz
        if q:
            opts = " ".join(f"{LETTERS[i]}: {o}." for i, o in enumerate(q.options))
            text += (f" Here is a question. {q.question} {opts} Pause the video and choose your answer."
                     f" {answer(q).replace('Answer:', 'The answer is')}. {q.explanation}")
        out.append(_speakable(text) or _speakable(s.title))
    out.append("The sources for this class are listed on this slide.")     # dropped when the deck has no references slide
    return [_speakable(t) for t in out]


def _powershell(script: str, args: dict, timeout: int) -> None:
    if not shutil.which("powershell"):
        raise NarrationUnavailable("narration needs Windows (PowerShell, its speech synthesizer and PowerPoint)")
    with tempfile.TemporaryDirectory() as d:
        ps, js = Path(d) / "run.ps1", Path(d) / "args.json"
        ps.write_text(script, encoding="utf-8-sig")
        js.write_text(json.dumps(args), encoding="utf-8")
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(ps), str(js)],
                           capture_output=True, text=True, timeout=timeout)
        if r.returncode != 0:
            raise NarrationUnavailable((r.stderr or r.stdout).strip()[-400:])


SPEAK = r"""
$a = Get-Content -Raw -Encoding UTF8 $args[0] | ConvertFrom-Json
Add-Type -AssemblyName System.Speech
$s = New-Object System.Speech.Synthesis.SpeechSynthesizer
try { $s.SelectVoice($a.voice) } catch { }
$s.Rate = [int]$a.rate
$fmt = New-Object System.Speech.AudioFormat.SpeechAudioFormatInfo([int]$a.sample_rate, 'Sixteen', 'Mono')
foreach ($x in $a.items) { $s.SetOutputToWaveFile($x.path, $fmt); $s.Speak($x.text) }
$s.SetOutputToNull(); $s.Dispose()
"""

# PowerPoint: the audio plays with the slide's entry (MainSequence effect 83 = media play, trigger 2 = with previous)
# and the slide advances on time; then save, and optionally export a video with those timings.
DECK = r"""
$a = Get-Content -Raw -Encoding UTF8 $args[0] | ConvertFrom-Json
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open($a.pptx, $true, $false, $false)
try {
  for ($i = 0; $i -lt $a.items.Count; $i++) {
    $x = $a.items[$i]; $sl = $p.Slides.Item($i + 1)
    $m = $sl.Shapes.AddMediaObject2($x.path, 0, -1, $p.PageSetup.SlideWidth - 40, $p.PageSetup.SlideHeight - 40, 24, 24)
    $m.AnimationSettings.PlaySettings.HideWhileNotPlaying = -1
    $e = $sl.TimeLine.MainSequence.AddEffect($m, 83, 0, 2)
    $sl.SlideShowTransition.AdvanceOnClick = 0
    $sl.SlideShowTransition.AdvanceOnTime = -1
    $sl.SlideShowTransition.AdvanceTime = [double]$x.seconds + [double]$a.gap_s
  }
  $p.SaveAs($a.out)
  if ($a.video) {
    $p.CreateVideo($a.video, $true, 5, [int]$a.height, [int]$a.fps, [int]$a.quality)
    $t = 0
    while ($p.CreateVideoStatus -eq 1 -or $p.CreateVideoStatus -eq 2) { Start-Sleep 2; $t += 2; if ($t -gt [int]$a.timeout) { throw "video export timed out" } }
    if ($p.CreateVideoStatus -ne 3) { throw "video export failed (status $($p.CreateVideoStatus))" }
  }
} finally { $p.Close(); if ($app.Presentations.Count -eq 0) { $app.Quit() } }
"""


def narrate(d: Path, deck: LectureDeck, frame: dict, cfg: dict, video: bool = False) -> dict:
    """Narration files for the deck in material dir `d` (slides.pptx must exist). Returns material.json's `narration`."""
    from pptx import Presentation
    n = cfg["narration"]
    count = len(Presentation(str(d / "slides.pptx")).slides)
    texts = narration_script(deck, frame)[:count]
    out = d / "narration"
    out.mkdir(exist_ok=True)
    items = [{"text": t, "path": str((out / f"slide_{i:02d}.wav").resolve())} for i, t in enumerate(texts, 1)]
    _powershell(SPEAK, {"voice": n["voice"], "rate": n["rate"], "sample_rate": n["sample_rate"], "items": items},
                timeout=60 + 30 * len(items))
    for x in items:
        with wave.open(x["path"]) as w:
            x["seconds"] = round(w.getnframes() / w.getframerate(), 1)
    v = n["video"]
    args = {"pptx": str((d / "slides.pptx").resolve()), "out": str((d / "slides_narrated.pptx").resolve()), "items": items,
            "gap_s": n["gap_s"], "video": str((d / "slides_narrated.mp4").resolve()) if video else "",
            "height": v["height"], "fps": v["fps"], "quality": v["quality"], "timeout": v["timeout_s"]}
    _powershell(DECK, args, timeout=120 + (v["timeout_s"] if video else 0))
    total = sum(x["seconds"] + n["gap_s"] for x in items)
    return {"voice": n["voice"], "engine": "Windows System.Speech + PowerPoint", "slides": len(items),
            "minutes": round(total / 60, 1), "files": {"deck": "slides_narrated.pptx", "audio": "narration/",
                                                        **({"video": "slides_narrated.mp4"} if video else {})},
            "per_slide_seconds": [x["seconds"] for x in items]}
