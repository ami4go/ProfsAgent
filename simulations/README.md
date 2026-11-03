# Simulations catalogue

The plan is in `docs/09_phase2_A_simulation_catalogue.md`.

**What it is:**
- Every simulation is a folder here, named by its id.
- Each folder holds a `sim.yaml`: type, courses, topics, interactivity level, engine, checks, version and change log.
- Each folder also holds the page and a `qa.py` that checks it in a real browser with the network blocked.
- Some entries also keep the source of a Manim video.

```
simulations/
  types.yaml                    the 12 simulation types (+ composites, + examples of "none" topics)
  _lib/                         pinned shared libraries (manim-web 0.40.1 + licence notices)
  _engines/stepper/             engine for type 1, step-through processes (README.md has its API)
  _engines/share/share.js       a page's setup in its link, and sent to the app (class examples)
  external/                     links to simulations on trusted sites: sources.yaml (sites + hand-written entries), index.json (built)
  classifier/labels.tsv         165 hand-labelled topics for the topic -> type classifier (params.json: its calibration)
  coverage.md                   generated: how many of each department's topics get which type
  <id>/sim.yaml, page(.src).html, qa.py, video/
  _build/                       generated, not committed: single-file pages, QA screenshots, reports
```

| Command | What it does |
|---|---|
| `python scripts/sims.py list` | Lists the entries |
| `python scripts/sims.py check` | Checks every `sim.yaml`: known type and level, courses in the IIIT-D catalogue, files present, nothing loaded from the internet, change log up to date |
| `python scripts/sims.py build [id …]` | Builds each page into **one offline HTML file** in `_build/`, with shared libraries, engines and licence notices inlined |
| `python scripts/sims.py qa [id …]` | Builds, then runs each `qa.py`; the report goes to `_build/qa_report.json` |
| `python scripts/sims.py coverage` | Runs the topic → type classifier over all weekly topics, then rewrites `coverage.md` |
| `python scripts/sims.py external` | Downloads PhET's and Falstad's lists, adds the hand-written ones from `external/sources.yaml`, and rewrites `external/index.json` |

**Adding a simulation:**
1. Make a folder `<area>.<topic>.<name>`.
2. Write the page:
   - `page.html` if it is self-contained;
   - or `page.src.html` that loads `../_lib/...js` or `../_engines/...`.
3. Write `qa.py`. It takes `[page] [screenshot folder]`, prints `PROBLEMS: …` and exits non-zero on a problem. Every simulation must check its answers with an **independent** method (docs/09 §4).
4. Write `sim.yaml`, starting from an existing one (with a one-line `summary` of what students do).
5. Run `check`, then `qa`.

**When you change a simulation,** bump its version and add a change-log line. A professor's approval in the app belongs to a version.

**In the app** (`src/profsagent/app/simulations.py`; decisions.md 26):
- every entry appears on the **Simulations** page;
- entries whose title or `topics` match a lecture are suggested on that lecture's page (so write `topics` the way course plans word them);
- `summary` is the one line professors and students read.
- **Class example:** set `class_example: true` only if the page loads `../_engines/share/share.js` and calls `SimShare.write(values, summary)` whenever its setup changes, and restores the setup from `SimShare.read()` when it opens. The stepper engine does both for you; `check` enforces it. The app then lets a professor save a setup that students open at.
- Pages are served sandboxed with no network, so they must not use `localStorage` or fetch anything.

**Repo tests:** `tests/test_sims.py` runs the fast checks (manifests, builds, labels) with the rest of the suite. The browser QA runs with `scripts/sims.py qa`.

**Links to other sites** (`external/`): simulations on trusted sites are suggested on lecture pages as links only. They are not copied or embedded, and we do not check them; the professor judges them. To add a site, add it to `external/sources.yaml` (hand-written entries, or a parser in `src/profsagent/sims/external.py` if the site publishes a list), then run `external`.

**Built by the machine** (`auto.*` folders; decisions.md 28): when a professor asks for a simulation in the app, `src/profsagent/sims/autobuild.py` asks the AI for a recipe for the step-by-step engine (`_engines/stepper/README.md`, "Recipes") and keeps it only if `_engines/stepper/qa_recipe.py` passes. These entries start as `status: draft` with `built_by: machine`; a team member reviews the teaching and sets `team-checked`. Each request's attempts, problems and AI calls are in `runs/_simulation_builds/<request>/`.
- `python -m profsagent.sims.autobuild example` checks the hand-written example recipe; `python -m profsagent.sims.autobuild worker` builds every queued request (the app starts it by itself).
