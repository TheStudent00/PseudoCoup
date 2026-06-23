# log_7 — PseudoFlutter kit complete: the frontier is closed, WFL conversion is next

## What this log marks

The kit is now **complete enough to convert WFL by assembly, not research**. The
explicit sequencing agreed in log_5/log_6 — *finish the kit (remaining leaves +
scroll/overlay/draw/animation) BEFORE converting WFL, so we never "research while
converting"* — is satisfied. This log is the phase boundary.

## What got built this phase (each 3-way-structurally verified, committed, pushed)

Every component renders identically on the **Flutter ship path** (offscreen golden)
and the **Kivy debug path** (xvfb `export_to_png`), proven by a side-by-side PNG in
`PseudoFlutter/comparisons/`.

- **Overlays (capability closed):** `dialog`, `bottom_sheet`, **`menu`** (dropdown,
  corner-anchored) over the shared `overlay` host (scrim + layered panel). WHETHER a
  panel shows is app state (driven by `present`); the layering is the kit's job.
- **Leaves:** `tab_bar` (TabRow — equal tabs + underline indicator), `search_bar`
  (filled pill + leading icon, reusing the icon system), `surface` (toned grouping
  box).
- **Vector primitives:** `progress_ring` (an arc swept clockwise from 12 o'clock by
  the app value) and `line_chart` (a polyline over a baseline). The kit's first real
  vector graphics — Flutter `Canvas.drawArc`/`Path` vs Kivy `Line(circle=…)`/points,
  with the angle and y-axis conventions reconciled so both start at the top / put
  higher values higher.
- **Animation:** `step_transition` — a crossfade expressed as a **pure function of a
  progress value `t` (0..1)**. This is the move that lets animation live inside a
  still-image verification discipline: the picture is a function of a value (exactly
  like `slider`/`progress_bar`), and the temporal *ticker* that advances `t` is the
  engine's mechanism (Flutter `AnimationController` vs Kivy `Animation`), hidden in
  the kit and deliberately not in frame. A still at `t=0.35` is deterministic and
  matches on both paths.

## State of the kit

- **40 intent functions** (components + layout primitives): avatar, badge,
  bottom_sheet, card, checkbox, chip, collapsible_section, column, dialog, divider,
  empty_state, fab, header, icon, icon_button, line_chart, list_row, menu, nav,
  outlined_button, overlay, pill_button, progress_bar, progress_ring, radio_group,
  row, scroll_view, search_bar, slider, stepper, step_transition, surface,
  switch_tile, tab_bar, text_button, text_field, text_zone, toggle, zone (+ present).
- **35 side-by-side comparison images**; **35/35 golden tests pass** (full-suite
  regression check after the `Tokens` constructor grew by five token groups).
- One shared `tokens.json` both kits load (cannot drift); one bundled Material font +
  `icons.json` both kits load (icons can't go tofu or diverge).

## Bugs caught honestly this phase

- The leaves golden initially rendered `search_bar`'s glyph as **tofu** — the test
  didn't register the bundled `MaterialIcons` font. Fixed: any golden that uses the
  icon system must load that font. (Reinforces the glyph-fragility lesson.)
- `bottom_sheet`/`surface` would expand to full height under a plain `Center`; both
  use `Align(heightFactor: 1.0)` to hug content — mirrored by Kivy `minimum_height`.

## Next phase: convert WFL screen-by-screen

Per log_5 (plan) and log_6 (build spec), now begins the actual conversion, held to
**STRUCTURAL fidelity** (same components / layouts / positioning as WFL in an Android
emulator; only API-forced style differences allowed — the explicit anti-patchiness
standard that PyHaxeUI drifted from):

1. Refresh `~/Programming/WFL` and re-skin tokens to WFL (purple #753DF0, Figtree,
   WFL spacing/radii) as a *second* `tokens.json` profile — the kit code doesn't move.
2. Convert simplest-first (LogWinSheet → PathDetailScreen → WorkoutWarmupScreen →
   SuggestedStretchesScreen → ExercisePickerScreen), each **3-way verified**
   (WFL-Android | Flutter | Kivy).

The kit no longer needs new capabilities to do this — that was the whole point of
closing the frontier first.
