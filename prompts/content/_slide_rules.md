---
id: _slide_rules
version: 0.3.0
stage: Phase 2 · B · shared text, included by B1 and B8
---
How to write a slide:
- Title: a short statement or question (at most 10 words).
- Bullets: 2-6, each at most 20 words, in plain words. No paragraphs, no filler ("In this slide we will…").
- One idea per slide. A slide with blocks needs fewer bullets (0-3): the blocks carry the content.
- Maths and symbols: write every formula, symbol and variable in LaTeX. Inline, inside bullets and text, as
  \( ... \) (e.g. "the distance \(d(v)\) of a vertex never decreases", "the window \(W\) doubles every round trip"),
  also in table cells, flow boxes, captions and quiz options: a LaTeX command outside \( \) shows as raw code. Never
  $...$, never maths in titles. Escape backslashes for JSON ("\\frac", "\\(", "\\min"). Keep every { } balanced.
  A topic without formulas needs none of this.
- `blocks` (optional, in order, shown below the bullets):
  - `math`: one key display formula in `latex` (no delimiters), e.g. "d(v) = \\min_{u}\\,(d(u) + w(u, v))".
  - `steps`: a derivation, proof, calculation or trace, 2-6 lines in `steps` [{latex, why}]: each line follows from
    the previous one by ONE move, and `why` names that move in at most 10 words ("relax edge (A, C)", "apply the
    induction hypothesis", "divide both sides by n"). A `why` naming two moves means two steps. Before using an
    identity, lemma or fact, state it as its own step with its reason, or point to the slide that shows it. Never skip
    a step a first-year student would need; split a long one over consecutive slides ("… 1/3", "2/3", …). The first
    line's `why` may be empty.
  - `definition`: a new term in `term`, its meaning in `text`, the first time the term is used.
  - `think`: a question in `text` students answer before you explain (asked, then answered in the notes).
  - `note`: a short boxed remark in `text`: the takeaway, a warning or a common mistake.
  Use blocks when they teach better than bullets: a formula for every quantity students must compute, steps for every
  result students must derive or trace, a definition for each new term. Do not use them on a check slide.
- `figure` (optional, at most one): `flow` for a process, pipeline or sequence of events (2-6 short box labels),
  `code` for a short snippet (at most 14 lines, real and runnable in spirit), `table` for a comparison or a state
  table (header row + at most 5 rows, 4 columns), `plot` for a chart of the running example's numbers (below). Use
  `none` when a figure would not help.
  A figure is complete or absent: a flow has its steps, a table its header and every row filled to the same width,
  a code figure its code. If you cannot fill it, use `none` and put the content in bullets or blocks. Never announce
  content the slide does not show ("four criteria…", "the table below…") without showing all of it.

The running example (`lecture.example`, when given: its title, story, conventions and computed values, each with a
name, meaning (with the formula or rule that produced it) and value):
- Make it THE example of the lecture: pose its question early, return to it on every example and worked_problem
  slide, and show each method's result on it (and, when two methods should agree, that they do).
- Never type a number the example computed. Write `[[name]]` and code puts in the computed value, e.g. bullet
  "After the first round \\(d(B) = [[d_B_round1]]\\)", step latex "W_4 = 2 \\cdot [[W_3]] = [[W_4]]", table cell
  "[[total_cost]]". Use only names listed in `lecture.example.values`. A list is written as (a, b, c), a matrix as a
  matrix in maths. Numbers that are not from the example (a definition's bounds, an exponent) you write yourself.
- Before you write [[name]], check that the value's meaning (its formula or rule) is what your slide says it is. If it
  differs, even by a constant factor, a normalisation, a unit or a convention, do not use the value: write the formula
  with symbols instead.
- Show only the values listed for your slide when a plan gives them (`slide.values`): a value from a later result must
  not appear before the slide that produces it.
- Never compute a number yourself, not even a small sum: if a value you want is not in the list, write it with symbols
  or with the [[names]] that are there, or leave the number out. Code checks the arithmetic of every line made only of
  numbers, and a wrong one is sent back.
- A worked example shows every hand step with the example's intermediate values, as `steps`.
- A plot is `"figure": {"kind": "plot", "caption": "...", "plot": {"x_label": "...", "y_label": "...", "log_y": false,
  "series": [{"kind": "points"|"line"|"bars"|"segments", "x": NAME, "y": NAME, "y2": NAME, "label": "..."}]}}`
  (the series go inside `plot`). x, y and y2 are NAMES of list values from the example, never numbers; `segments`
  draws a vertical line from y to y2 at each x (e.g. the gap between a measurement and a prediction). Plot what
  students should see: the data a result came from, together with the result; a quantity changing over steps or time
  (log_y when it spans orders of magnitude); settings or methods compared on the same axes.
- `notes`: what the professor says, 90-150 words: the explanation, an example, a common misconception. (The notes
  are also read aloud for the narrated video, so write them as speech.)
- `minutes`: teaching time for the slide; all slides together ≈ the lecture length ({{ lecture.minutes }} minutes).
- `sources`: ids of the given sources the slide draws on. Cite only ids from the list; cite nothing rather than guess.
- A check slide's `quiz` always has an `explanation`: why the right answer is right and why the most tempting wrong
  one is wrong.

Accuracy: write only what you are confident is correct for this course level. Do not invent statistics, dates,
benchmark numbers, quotes or URLs. If a source is needed for a claim, cite a given source or leave the claim out.
