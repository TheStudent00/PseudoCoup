# M3 elevation — one general, role-driven mechanism

Scope: ONE elevation mechanism in the Kivy kit. Edited ONLY
`~/Programming/WFL_MixingCenter/render/kivy_kit.py`. No runtime/transpiler change; no commit/push.

## Mechanism (all canvas-only — LAW 3: geometry untouched, 377/377 preserved)

Elevation is stored in the role table as ONE level per painted kind. Two paints derive from that level,
both bound to the widget's pos/size, neither touching the layout box:

1. **TONAL tint** — `_tonal_fill(fill, level)`: M3 tonal elevation overlays surfaceTint (== the theme's
   `surfaceTint`, defaulting to `primary`) on a surface-colored fill at the spec alpha for the level.
   Applied in `_paint_spec` at the one place a surface-role fill is resolved, so every surface container
   (top bar, card) tints from the same code path. Blend: `out = surface*(1-a) + tint*a`, alpha `a` from the
   M3 spec table below.
2. **SHADOW** — `_draw_shadow(w, node)`: Kivy has no blur, so the general approximation is 4 stacked
   translucent black rounded rects (each `KColor(0,0,0,0.05)`), each larger and offset downward (bias
   `spread*1.6` down, `spread` sideways, `spread` scaled by the role's dp depth). Their overlap fades from a
   soft near-edge darkness out to nothing — a soft drop shadow. Drawn in `canvas.before` BEFORE the fill so
   it sits behind the container; corner radius matches the container's own. No-op for level-0 kinds.

Both are invoked generally: `_draw_shadow` from the `to_widget` chokepoint (every node), `_tonal_fill` from
`_paint_spec`. No per-screen code, no per-name patch (LAW 2).

## Role → level table (M3 spec)

| Kind | Level | dp | Tonal α | Spec citation |
|------|-------|----|---------|---------------|
| Card, ElevatedCard | 1 | 1dp | 5% | M3 filled/elevated card resting elevation = 1dp |
| TopAppBar, CenterAligned…, Medium… | 2 | 3dp | 8% | see TOPBAR note |
| FloatingActionButton, ExtendedFAB | 3 | 6dp | 11% | M3 FAB resting elevation = 6dp |
| ElevatedFilterChip | 1 | 1dp | 5% | M3 elevated-chip resting elevation = 1dp |

Excluded (level 0, no tint/shadow, correct per spec): OutlinedCard (outline, 0dp); flat AssistChip /
FilterChip / SuggestionChip (0dp — only the *Elevated* variants are raised); Surface/Scaffold background.

M3 tonal-overlay alpha table (spec): L1 5% · L2 8% · L3 11% · L4 12% · L5 14%.
Level→dp: L1 1 · L2 3 · L3 6 · L4 8 · L5 12.

**TOPBAR note.** The M3 small top app bar's RESTING container elevation is 0dp (`containerColor = surface`).
At rest that equals the Scaffold `background` role, so the bar cannot separate — this IS the reported
"white/black-on-itself" symptom. M3's own separation mechanism is the on-scroll container,
`TopAppBarDefaults.scrolledContainerColor = surfaceColorAtElevation(3.dp)` == tonal level 2. We adopt that
spec level so the bar reads as a distinct surface (the task's visual gate). It is a spec value, not invented.

## Tint math (verified against rendered pixels)

Injected M3 baseline dark palette: surface `#1C1B1F`=(28,27,31), primary/surfaceTint `#D0BCFF`=(208,188,255).
- Top bar L2 (α .08): 28·.92+208·.08 = **42**, 27·.92+188·.08 = **40**, 31·.92+255·.08 = **49** → measured bar (42,40,49). ✓
- Card L1 (α .05): 28·.95+208·.05 = **37**, 27·.95+188·.05 = **35**, 31·.95+255·.05 = **42** → measured card (37,35,42). ✓
Background stays (28,27,31). Elevation-off renders bar=card=bg=(28,27,31) — fully flat.

## Shadow decision: SHIPPED (tint + shadow)

The stacked-rect shadow reads as a clean soft drop shadow on eyeballing (see GymList: the "My Gym" card and
the FAB both float cleanly; the top bar has a subtle underline of shadow). No muddy fill, no hard dark box.
So both the tonal tint AND the shadow ship. Tint remains the load-bearing separator; the shadow reinforces.

## Current repo state (important)

`MaterialTheme.colorScheme` is still an inert `_UIChain` stub in this repo — every role resolves to `None`,
so the ENTIRE theme paint layer (existing `_paint`, `_paint_field`, `_theme_button`, and this new tint) is
correctly DORMANT per LAW 1 (unresolved color == no paint; never an invented hex). Verified during a live
`run_app` render: `MaterialTheme.colorScheme` type == `_UIChain`, `.surface`/`.primary`/… all `_UIChain`.
(The gray chips seen on screen are Kivy's default Button skin, not themed fills; the black top bar is the
unpainted window default.) The mechanism lights up the instant the color table becomes real — no further
change here — exactly like the rest of the paint layer.

Because theme colors are stubbed, a themed before/after cannot be produced without either editing
`compose_ui` (out of fence) or inventing colors (violates LAW 1). So the shots were rendered by a **throwaway
verification harness** (`/tmp/elev_demo.py`, NOT shipped) that injects the standard published M3 baseline
dark palette into `_theme_color` only, to exercise the dormant mechanism as it will run once the table is
real. The shipped `kivy_kit.py` invents nothing.

## Gates

- `cd ~/Programming/PseudoCoup/tools/pseudokotlin && python3 fidelity.py`
  → `FIDELITY ALL: 377/377 components within tolerance (28 screens)` (geometry untouched — LAW 3).
- `cd ~/Programming/WFL_MixingCenter/render && python3 interact.py`
  → `INTERACT: 513 fired, 513 ok, 0 failures across 27 screens`.

## Shots (`~/Programming/PseudoCoup/layout_inspect/shots/`, injected M3 dark palette, `off` = elevation
disabled, `on` = mechanism active)

- `ExerciseDetail_elev_off0001.png` / `_on0001.png` — TOP BAR: off = bar identical to background
  (indistinguishable); on = bar is a distinct lighter surface with a soft shadow beneath. Outlined
  assist chips correctly stay flat (level 0).
- `GymListScreen_elev_off0001.png` / `_on0001.png` — CARD + FAB + top bar: off = card flush with
  background; on = the "My Gym" card reads as an elevated surface (subtle tint + soft shadow) and the FAB
  floats with its shadow. Clean, no dark-boxing.
- `ProgramsScreen_elev_{off,on}0001.png`, `HistoryScreen_elev_{off,on}0001.png` — additional top-bar
  confirmations.

Inspected all `on` shots: top bar reads as a distinct surface, card/FAB read as elevated, nothing muddy or
dark-boxed; pixel deltas match the spec tint math above.
</content>
</invoke>
