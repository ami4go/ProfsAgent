---
id: D9
version: 0.2.0
stage: Phase 2 · C · which parts of this lecture does this video teach, and where? (AI reads the transcript)
model_class: read
temperature: 0.1
output_model: VideoReading
inputs:
  lecture: {topic, course level}
  parts: [{id, title, teaches, key_terms, minutes}]
  video: {title, channel, duration}
  chapters: the creator's chapters, if any
  transcript: lines starting with a [m:ss] marker
---
## SYSTEM
A professor wants to know which parts of a lecture a YouTube video can teach, and the exact minutes that do it. You get
the parts in teaching order, and the transcript of the video with a time marker [m:ss] about every 30 seconds. A long
video's transcript is cut to the passages closest to the parts; "[… skipped to m:ss]" marks what is not shown. A
transcript can be AI notes of the video rather than its captions; read it the same way.

For every part, say whether this video teaches it:
- teaches: "fully" means a student who watches only those minutes learns what `teaches` asks for (small gaps are fine);
  "partly" means it teaches some of it; "no" means it does not, or only names it (an introduction that lists what the
  video will cover, a summary, an advert, a passing mention).
- start, end: for "fully" or "partly", the markers copied exactly from the transcript: the first line where the real
  explanation of this part begins and the last line that still teaches it. Leave out the welcome, channel plugs, sponsor
  reads and the outro, and stop where the video moves on. One continuous stretch per part, between 1 and 25 minutes.
  Give the whole explanation, with its examples, not the one passage that says it best: `minutes` is how long the part
  takes in class, and a stretch under about a third of that rarely teaches it (say "partly" if the video really is that
  brief). Empty strings for "no".
- why: at most 20 words on what those minutes do.

The same stretch may teach two neighbouring parts, and one video may teach several parts one after another: give each
part its own start and end. Most videos teach only some parts of a lecture; answer "no" for the rest. Check the sense of
the words: a stretch that uses a part's terms for something else (for example "execution traces" of a phone app's
performance monitor when the part is about the steps of a coding agent) is "no", however many words it shares. Judge only
from the text given; never guess what the skipped passages say. Output one JSON object only:
{"parts": [{"part": "C1", "teaches": "fully", "start": "4:30", "end": "11:00", "why": "..."}, {"part": "C2", "teaches": "no", "start": "", "end": "", "why": "..."}]}

## USER
<context name="lecture">{{ lecture | tojson }}</context>
<context name="parts">{{ parts | tojson }}</context>
<context name="video">{{ video | tojson }}</context>
<context name="chapters">{{ chapters | tojson }}</context>
<transcript>
{{ transcript }}
</transcript>

Answer for every part. Return only the JSON object.
