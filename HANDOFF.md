# Session handoff — 2026-07-04 (written by the outgoing Claude session for its successor)

You are continuing an ongoing autonomous engineering loop. Read this file, then
`PROGRESS_ondeck.md`, then proceed with the top on-deck item. The user says "proceed" and steps
away; work rounds end with a report, dashboard update (`PROGRESS_ondeck.md` edit + `python3
tools/pseudokotlin/track.py`), and a commit-push of BOTH repos (PseudoCoup on main,
WFL_MixingCenter on master). Memory files in the auto-memory directory carry the standing rules
(general-solve-first, communication protocol, render-count honesty, Kotlin adjustability); they
load automatically.

## The task

Complete the KtToPy transpiler (`tools/pseudokotlin/`) so the WFL Kotlin app runs in Python/Kivy
(`~/Programming/WFL_MixingCenter/`). The continue/shutdown criterion is the LAYOUT-FIDELITY
instrument: real Compose (Robolectric) vs the kivy kit, both dump component boxes, compared as
%-of-display at ±3% (`tools/pseudokotlin/fidelity.py` runs everything; per-screen diffs land in
`layout_inspect/*.diff.txt`).

Hard rules: zero hand-edits to transpiled WFL-Python (regenerate via
`tools/pseudokotlin/build_mixingcenter.py`); fixes go in shared layers (kivy_kit / compose runtime
/ loader / differ / transpiler); one cause = one general fix; never game the meter. Kotlin inside
WFL_MixingCenter/WFL may be adjusted only if appearance/function is unchanged. Font/shaper bridges
are the one sanctioned non-general area, and every text/list metric must be derived from the
specimen tests (dumpSpecimen / dumpSpecimenList in LayoutDumpTest.kt + their python halves in
render/inspect_layout.py), never from mixed app screens.

## State at handoff

- Dashboard: 254/344 components within tolerance across all 28 measurable screens (DebugPanel is
  dev-only, excluded). The original 20 screens are all at 100% (231/231) — do not regress them.
- The 8 newly measured screens seed program/session fixtures through the app's OWN repositories
  (SampleProgramRepository.seedIfNeeded + WorkoutExecutionRepository.startSessionFromProgramDay
  on BOTH engines — Kotlin side in the generated LayoutDumpAllTest assembler(seed=...), python
  side in inspect_layout.seed_fixtures). Deterministic ids: program `prog_gup_3d_beg`, day
  `day_gup_3d_beg_w1_d1`; sessionIds are per-engine (only rendered text must match).
- This round landed 6 general runtime/transpiler fixes (ktext extension dispatch + build pre-pass
  registry, Java printf ',' grouping, Room enum query params, Room aliased-star JOIN reads,
  combine(collection) overload, debounce/firstNotNullOfOrNull, IntrinsicSize non-numeric wrapper).
  All committed and pushed.

## State update (2026-07-04 night session)

Geometry COMPLETE: 377/377 across all 28 measurable screens (DebugPanel = sole intentional skip,
verified exhaustive). Paint layer underway via delegated Opus slices (pattern in memory:
delegate-to-opus-tight-briefs): slice 1 = kit paint mechanism (stub-guarded), slice 2 = real runtime
color table (Color/shapes/colorScheme through the app theme). Both committed+pushed. Current slice
(may be uncommitted if the session hit the usage ceiling — check git status + DevComms/*_report.md
for the latest agent report): paint pass 2 = text contrast roles, top-bar surface tint,
button/chip container colors. Gate for EVERY paint slice: fidelity.py must stay exactly 377/377.
Remaining board: popups hidden until opened, Scaffold innerPadding/modifier-order minor, .kt line map,
domain oracle breadth.

## Command crib

- Full gauge: `cd tools/pseudokotlin && python3 fidelity.py`
- Regenerate WFL-Python after transpiler/runtime edits: `python3 tools/pseudokotlin/build_mixingcenter.py`
- Regenerate the auto layout tests after generator edits: `python3 tools/pseudokotlin/gen_layout_dumps.py`
- One screen's kivy dump: `cd ~/Programming/WFL_MixingCenter/render && python3 inspect_layout.py <ScreenName>`
- One screen's compose dump: `cd ~/Programming/WFL_MixingCenter/WFL && ./gradlew -p app testDebugUnitTest --tests '*LayoutDump*.dump<ScreenName>'`
- Dashboard: edit PROGRESS_ondeck.md, then `python3 tools/pseudokotlin/track.py` (never hand-edit PROGRESS.md/html)
