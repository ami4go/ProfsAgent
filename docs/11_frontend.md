# The professor app's frontend (v2)

**Status:** built 11 Nov 2026 · **Code:** `frontend/` (source), `src/profsagent/app/static/ui/` (the build the app serves) ·
**Read with:** `docs/10_ui_improvement_plan.md` (the plan this follows), `docs/04_phase2_UI_integration_guide.md` (the API).

The first app was one 2,200-line `index.html`. This one is a small React application with a design system, built once
and served by the same FastAPI app. The backend API is unchanged except for one read-only endpoint (section 6).

## 1. Run it

```bash
python scripts/run_app.py              # the app, as before: http://127.0.0.1:8000 (needs no Node: the build is committed)
python scripts/run_app_demo.py         # the same app with recorded runs replayed instead of the AI pipeline (no keys, no Neo4j)

cd frontend && npm install             # only to change the frontend
npm run dev                            # http://localhost:5173, API calls go to the app on port 8000
npm run build                          # type-check, then write src/profsagent/app/static/ui (commit it with the change)
npm test                               # unit tests: status logic, lecture-plan logic, token contrast
```

`run_app_demo.py` seeds seven courses, one in each state (waiting at each check, working, paused, stopped on a problem,
stopped by the professor, approved with lecture results), from finished runs under `runs/`. Everything on screen comes
from the real server code (`views.py`, `edits.py`, `validate/`, `delivery.py`); only the AI stages are replayed.

## 2. Stack

| What | Choice | Why |
|---|---|---|
| UI | React 19, TypeScript (strict) | components and types for an API with ~50 endpoints |
| Build | Vite 8 | one command, hashed files, a dev server with an API proxy |
| Styling | Tailwind CSS 4, tokens in `src/styles/index.css` | every colour, size and radius is a token |
| Server state | TanStack Query | one hook per resource; pages refresh themselves while work runs |
| Routing | React Router (hash routes) | the server keeps serving one page; old `#/run/…` and `#/delivery/…` links redirect |
| Accessible parts | Radix (dialog, menu, tooltip), cmdk (Ctrl K) | focus trap, Escape, arrow keys, screen-reader roles |
| Motion | Motion, CSS | the gliding tab line and pill, toasts, dialogs |
| Icons, fonts | Lucide; Geist, Geist Mono, Newsreader (OFL, bundled) | works offline |

## 3. Where things are

```
frontend/src/
  styles/index.css       the design tokens, base styles, and the few bespoke pieces (loader, glow, textures)
  lib/                   api.ts (fetch + ApiError) · queries.ts (one hook per resource) · types.ts (the API's shapes)
                         status.ts (the status vocabulary) · delivery.ts (lecture status, the class-time bar) · format.ts · md.tsx
  components/ui/         the kit: Button, Badge, Card, StatTile, Field/Input/Select/Checkbox/Switch, Tabs, Segmented,
                         Modal + confirm(), Tooltip, Toaster, Callout, EmptyState, Skeleton, Meter, DataTable, FileLink, Menu, Stars
  components/app/        Shell (sidebar, top bar), CommandPalette, StageRail, Findings, Decision (approval dialog),
                         RunPanels (progress, review record, evaluation), Charts (class-time bar, CO–PO matrix, bar list),
                         CourseForm, SimPreview
  pages/                 Courses · NewCourse · course/ (Layout, Overview) · design/ (Design, Context, Outcomes, FinalSheet,
                         editing) · lectures/ (Lectures, Lecture, Results, Slides, Plan, SimCard, Student, Documents) · Simulations
```

Routes: `/` courses · `/new` · `/courses/:id` overview · `/courses/:id/design[/details|context|outcomes|final]` ·
`/courses/:id/lectures[/:lecture[/kit|/notebooklm]]` · `/courses/:id/student` · `/simulations`.
The course is the place you work in (plan §7): delivery is a tab of the course, not a second place to pick it again.

## 4. Design system

**Colour: four colours carry meaning on a graphite base.** Each has one job, and never appears without words or an icon.

| Token | Value | Means |
|---|---|---|
| `canvas` / `surface-1…4` | `#0a0c10` / `#11141a` `#161a22` `#1d222c` `#262c38` | depth = a lighter surface + a hairline (`line`, `line-strong`) + a soft shadow |
| `ink-1…4` | `#eceef2` `#aeb5c0` `#868e9c` `#5a6170` | text: primary, secondary, tertiary (all ≥ 4.5:1 on every surface), decorative |
| `iris-*` | `#6e7cf7` (500) | **ProfsAgent**: what it wrote and has not been approved, actions, focus, "working" |
| `mint-*` | `#45d6a4` (400) | **approved / verified by you** |
| `amber-*` | `#f5b544` (400) | **waiting for your decision**, warnings |
| `rose-*` | `#f47a74` (400) | a blocking problem, destructive actions |
| `way-*`, `heat-*` | chart palette | the class-time bar and the CO–PO matrix only; never used for status |

Generated content carries the iris "Written by ProfsAgent" badge, approved content the mint "Approved by you" badge, and
what the professor edited "Changed by you" (with the changes in its tooltip). `src/lib/__tests__/tokens.test.ts` checks
the contrast of every text/surface pair, so a token change that breaks readability fails the tests.

**Type.** Geist for the interface (14 px base, 13 px secondary, 11 px caps labels), Newsreader for page and course titles
(the academic voice), Geist Mono for identifiers (lecture ids, ISBNs, clause references). Scale: 11, 12, 13, 14, 15, 17, 20, 24, 30, 38.

**Space and shape.** A 4 px grid. Radii 4 / 6 / 8 / 12 / 16 / 20 (inputs 8, cards 12, dialogs 16). Controls are 32 / 36 / 44 px
high. Sidebar 256 px, top bar 52 px, content up to 1120 px (1344 px for wide pages, 800 px for reading).
Breakpoints: 640, 768, 1024 (the sidebar becomes a drawer below it), 1280.

**Depth and glass.** Three shadows (`shadow-1…3`). Glass (blur + translucency) is used only for chrome that floats over
content: the sidebar, the top bar, dialogs, menus, toasts and the decision bar.

**Motion.** 150–250 ms, ease-out, never on things done many times. Pressed buttons scale to 0.98; the tab line and the
segmented pill glide; toasts rise from the bottom. `prefers-reduced-motion` turns movement off and keeps fades.

**Icons.** Lucide, 16 px in controls and 18 px in navigation, always beside a label; an icon-only button has an
`aria-label` and a tooltip.

**States of every control:** hover (one surface lighter), pressed (0.98), focus (2 px iris ring, 2 px offset),
disabled (45% opacity), invalid (rose border + message), loading (a spinner in place of the icon, the label stays).

**Charts** (`components/app/Charts.tsx`): thin marks, a 2 px gap between touching marks, a legend whenever there is more
than one series, values on hover and on keyboard focus, and a second channel beside hue (labels inside tall bars, hatching
for "simulation" and "before class"). The four class-time hues were checked for colour-blind separation on the card surface.

## 5. Principles the screens follow

1. **Always say what the system is doing.** One progress pattern (`ProgressPanel`, the cradle loader): what is happening,
   how far along, and that it is safe to leave.
2. **Generated is not approved.** Iris vs mint, on every check, slide deck, lecture plan and resource.
3. **Evidence is one click away.** Every rule shows its source; every resource and speaker shows why it ranks where it
   does (review, checked video minutes, the score per criterion), and what was removed and why.
4. **Findings in sentences.** `Findings` groups repeats, says who can fix each one, and keeps check codes behind "Show the detail".
5. **Decisions are explicit.** Approving opens a dialog that says what is approved and what happens next; with open
   problems it asks for a reason, which is recorded. Stopping asks why.
6. **Context is kept.** The course header and the four steps stay on screen; an approved step can be opened again, read-only.
7. **Loading, empty, error, success and pending** each have one component: `Skeleton`, `EmptyState`, `Callout`, toast, `Badge`.

## 6. The one backend addition

`GET /api/runs/{id}/stage/{gate}` returns what a check shows, built by the same `views.py` code as the waiting check,
with `editable: true` only for the check that is waiting. It lets an approved step be read again
(`tests/test_app.py::test_a_step_can_be_read_again_after_it_is_approved`). Nothing else in the API changed. `GET /` now
serves `static/ui/index.html`, and `/ui/…` its scripts, styles and fonts.

## 7. Accessibility

Semantic landmarks (`nav`, `main`, `aside`), a skip link, one `h1` per page with ordered headings, tables with captions
and scope, dialogs that trap focus and return it, tabs and menus with arrow keys, a visible focus ring everywhere,
status never by colour alone, live regions for progress and toasts, and reduced motion. An axe audit (WCAG 2.1 A/AA and
best practices) of the nine main screens reports no violations.
