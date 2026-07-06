# Card selected-state paint — mechanism, audit, verification

## Status: COMPLETE, VERIFIED END-TO-END (targeted proof PASSED, all gates GREEN, no gate moved)

## 1. Ground truth (Kotlin, verified directly against the live files, not the diagnosis doc alone)

`WFL_MixingCenter/WFL/app/src/main/java/com/sara/workoutforlife/ui/paths/PathSelectionSheet.kt`:

- `PathCard` (lines 178-234): `isSelected` computed at `PathSelectionSheet.kt:133`
  (`def.id in state.selectedPathIds`).
- **Selected container fill**: `MaterialTheme.colorScheme.primaryContainer` — `PathSelectionSheet.kt:185`
  (unselected: `MaterialTheme.colorScheme.surface` — `PathSelectionSheet.kt:186`).
- **Selected border**: `MaterialTheme.colorScheme.primary` at `2.dp` — `PathSelectionSheet.kt:192,194`
  (unselected: `MaterialTheme.colorScheme.outlineVariant` at `1.dp`).
- These flow into `WflCard(containerColor=, borderColor=, borderWidth=)`
  (`PathSelectionSheet.kt:188-194`), which is where the actual M3 factory calls live:
  `WFL_MixingCenter/WFL/app/src/main/java/com/sara/workoutforlife/ui/theme/WflCard.kt`:
  - `border = BorderStroke(borderWidth, borderColor)` — `WflCard.kt:46`
  - `colors = CardDefaults.cardColors(containerColor = containerColor)` — `WflCard.kt:47`
  - both passed to `Card(colors=colors, border=border, ...)` — `WflCard.kt:56-57` (and 65-67, the
    non-clickable branch).
- A third cue, structurally separate from this fix (not a paint-layer gap): a checkmark `Surface(color =
  MaterialTheme.colorScheme.primary, ...)` gated `if (isSelected)` at `PathSelectionSheet.kt:215-231`. This
  was already rendering correctly (state/recompose was never broken per the original diagnosis); untouched
  here.

Note: the diagnosis doc's path (`PseudoCoup/WFL/app/src/main/java/...`) does not exist in this checkout —
the real Kotlin ground truth lives under `WFL_MixingCenter/WFL/app/src/main/java/...`. Re-verified directly
against that tree; the diagnosis doc's line numbers and role names were confirmed accurate.

## 2. Mechanism implemented

### `tools/pseudokotlin/runtime/compose_ui.py`

Removed `CardDefaults`, `BorderStroke`, `ButtonDefaults`, `FilterChipDefaults`, `AssistChipDefaults`,
`TopAppBarDefaults` from the generic inert `_UIChain` autostub list (`_NAMES`). Added real,
value-retaining replacements:

- **`_scheme_role(role)`**: a lazy lookup of `MaterialTheme.colorScheme.<role>`, reusing the EXACT same
  `_ColorScheme`/`MaterialTheme` mechanism the file already provides for the kit's own `_theme_color()` —
  no second color table, no new resolution path. Returns `None` when the scheme is unresolved or the role
  is absent (never invents).
- **`ColorsSpec`**: the one real class backing every `*Defaults.xColors(...)` factory. Retains every
  explicitly-passed role kwarg AS-IS, including `Color.Unspecified` (kept as the inert marker — never
  resolved, per the "unresolved color = no paint, never invented" law). Any role kwarg OMITTED resolves via
  `_scheme_role` to its natural M3 colorScheme counterpart (e.g. omitted `containerColor` -> `surface`,
  omitted `selectedContainerColor` -> `secondaryContainer`). Exposes `containerColorFor(selected, disabled)`
  / `contentColorFor(selected, disabled)` so a paint routine can resolve the same selected/disabled
  precedence M3 itself uses.
- **`CardDefaults.cardColors` / `.elevatedCardColors` / `.outlinedCardColors`**: all three build the same
  `ColorsSpec` (the app never actually differentiates them — see audit below; `elevatedCardColors` /
  `outlinedCardColors` are not used anywhere in the app, wired for completeness per the task spec, not
  because any call site needs them).
- **`ButtonDefaults.buttonColors` / `.textButtonColors`** (+ aliases `outlinedButtonColors` /
  `elevatedButtonColors` / `filledTonalButtonColors`, unused but harmless): real `ColorsSpec`.
- **`FilterChipDefaults.filterChipColors`**, **`AssistChipDefaults.assistChipColors`**,
  **`TopAppBarDefaults.topAppBarColors`**: real `ColorsSpec`, scoped to exactly the kwargs each factory's
  real Kotlin call sites in this app actually pass (see audit).
- **`BorderStroke(width, color)`**: a real class retaining `.width`/`.color`. `color=None` (omitted)
  resolves to `MaterialTheme.colorScheme.outline` (M3's own `BorderStroke` default); an explicit
  `Color.Unspecified` stays unresolved.

All of the above resolve an omitted color to the SAME theme-role table `kivy_kit.py`'s `_theme_color()`
already reads (`MaterialTheme.colorScheme`) — one shared source of truth, not a parallel table.

Regenerated the transpiled app via `python3 tools/pseudokotlin/build_mixingcenter.py` (254/254 clean,
0 errors) per the LAW. Confirmed byte-identical transpiled output before/after
(`diff -rq` over `WFL_MixingCenter/ui/` = no differences) — expected, since only `compose_ui.py`'s runtime
VALUES changed, not the transpiler's structural output.

### `WFL_MixingCenter/render/kivy_kit.py`, `_paint_spec()` (~419-511, grew from the original 419-464)

Added two new resolvers:
- **`_colors_spec_fill(node)`**: reads `node.props["colors"]` — only if it's a real `ColorsSpec` (type-name
  guarded, so an inert leftover autostub anywhere else in the tree is never misread as a color) — and
  resolves `containerColorFor(selected=node.props.get("selected") is True)` to rgba via the existing
  `_channels()` resolver.
- **`_border_stroke_spec(node)`**: reads `node.props["border"]` — only if it's a real `BorderStroke` — and
  resolves `.color`/`.width` to `(width, rgba, radius)` via `_channels()`.

`_paint_spec()`'s priority order (highest first): `colors=`/`border=` node-constructor props > the
Modifier chain's `background`/`border` ops > the static `_SURFACE_ROLE` table. The Modifier-chain loop was
changed to only apply its `background`/`border` findings when `fill`/`border` are still `None` (i.e. never
override an already-resolved `colors=`/`border=` value). The `_SURFACE_ROLE` table now ALWAYS supplies the
corner radius (and M3 tonal-elevation tint) for its kinds, but only supplies the FILL COLOR when nothing
more specific resolved one first — so a selected Card's `colors=`-driven `primaryContainer` fill still gets
the same 12dp corner radius the unselected Card gets from the role table (previously the role-table branch
was skipped entirely once any fill resolved, which would have left a `colors=`-only Card's radius at 0).
A `colors=`/`border=`-driven border that carries no shape info (BorderStroke has none) inherits the node's
own resolved corner radius, so the stroke traces the same rounded rect as the fill.

### `WFL_MixingCenter/render/kivy_kit.py`, `_theme_button()` (~661-720)

Same priority: after computing the static `_BUTTON_ROLE`/chip/tab role colors as before, a recorded
`colors=` `ColorsSpec` overrides whichever of fill/content it resolves (via the same
`containerColorFor`/`contentColorFor`, honoring `selected`), and a recorded `border=` `BorderStroke`
overrides the role-driven outline. Anything the spec leaves unresolved (e.g. it carries no
`disabledContainerColor`) falls through to the untouched role-table value — never a regression to the
existing role-driven Button/Chip painting when a screen doesn't pass explicit colors.

## 3. Component audit (grep evidence against the real Kotlin tree)

```
grep -rnoE '[A-Za-z]+Defaults\.[a-zA-Z]+Colors\(' WFL_MixingCenter/WFL/app/src/main/java/com/sara/workoutforlife
```

| Factory | Used with explicit colors? | Sites (sample) | Covered? |
|---|---|---|---|
| `CardDefaults.cardColors` | Yes | `WflCard.kt:47` (only call site in the app) | Yes |
| `CardDefaults.elevatedCardColors` / `outlinedCardColors` | **No** — never called anywhere | — | Wired (same class) but no real call site needs it |
| `BorderStroke(...)` | Yes, 17 call sites | `WflCard.kt:46`, `TodayScreen.kt:1177-1178`, `ProgramsScreen.kt:388`, `MyProgramScreen.kt:218`, `AppNavigation.kt:826`, etc. | Yes |
| `ButtonDefaults.buttonColors` | Yes, ~18 call sites | `PathSelectionSheet.kt:92`, `PathsScreen.kt:180`, `ProgramsScreen.kt:366`, `TodayScreen.kt:327/1147`, `OnboardingScreen.kt` (7x), etc. | Yes |
| `ButtonDefaults.textButtonColors` | Yes | `DebugPanelScreen.kt:87`, `WorkoutExecutionScreen.kt:1187`, `GymListScreen.kt:253` | Yes |
| `FilterChipDefaults.filterChipColors` | Yes | `ExerciseQueue.kt:81`, `GymCreateWizardScreen.kt:242`, `OnboardingScreen.kt:974`, `UpdateProgramWizardScreen.kt:898` | Yes |
| `AssistChipDefaults.assistChipColors` | Yes | `GymListScreen.kt:152` | Yes |
| `TopAppBarDefaults.topAppBarColors` | Yes | `WorkoutExecutionScreen.kt:211` | Yes |

`ElevatedCard`/`OutlinedCard` composables themselves: **never used anywhere** in the app (grep confirmed
zero call sites) — `elevatedCardColors`/`outlinedCardColors` were still implemented (same `ColorsSpec`
shape as `cardColors`, per the task's explicit ask), but there was no real usage to extend scope for beyond
that; not over-built past what the task required.

This is the "one fix moves a GROUP" law in practice: one `ColorsSpec` class + one `_scheme_role` resolver in
`compose_ui.py`, plus one priority-ordering change in each of `_paint_spec()`/`_theme_button()` in
`kivy_kit.py`, covers every M3 `*Defaults.*Colors(...)`/`BorderStroke` construct the app actually invokes
with explicit arguments — Card, Button, TextButton, FilterChip, AssistChip, and TopAppBar all light up from
the same two mechanisms, not six separate patches.

## 4. Targeted proof (real handler chain, not synthetic state injection)

Booted the full app (`render/run_app.build_app_composition`), settled via repeated `compose()` until node
count stabilized, then drove the REAL handler chain a user's taps would fire:
1. tap "Paths" (bottom nav) -> route: paths
2. tap "Find your path" (`EmptyPathsState`'s button, `viewModel::startPicker`) -> picker opens
3. **BEFORE** screenshot + node-tree inspection of the "Just Show Up" `Card`
4. tap "Just Show Up" (`PathCard`'s `onClick = { onTogglePathSelection(def.id) }`, the REAL
   `PathsViewModel.togglePathSelection` handler, not a synthetic state write)
5. **AFTER** screenshot + node-tree inspection of the same `Card`

Node-tree evidence (props are now real, retaining objects — was previously entirely absent per the
diagnosis):
```
BEFORE props: colors=ColorsSpec, border=BorderStroke
BEFORE paint_spec: fill=(0.973, 0.962, 0.997, 1.0)  radius=12.0  border=(1.0, (0.863, 0.839, 0.878, 1.0), 12.0)
AFTER  props: colors=ColorsSpec, border=BorderStroke
AFTER  paint_spec: fill=(0.925, 0.899, 0.997, 1.0)  radius=12.0  border=(2.0, (0.459, 0.239, 0.941, 1.0), 12.0)
```
BEFORE = `surface` fill + `outlineVariant` border @ 1dp; AFTER = `primaryContainer` fill + `primary` border
@ 2dp — exactly the Kotlin spec (`PathSelectionSheet.kt:185-194`).

**Screenshots** (mnt-accessible paths, `0001` suffix as documented):
- `/home/lucas/Programming/PseudoCoup/DevComms/shots/card_before0001.png`
- `/home/lucas/Programming/PseudoCoup/DevComms/shots/card_after0001.png`

Visually confirmed: BEFORE shows "Just Show Up" with the same faint hairline border as every other
unselected path card; AFTER shows it with a thick purple border and a lightly-tinted purple fill, visually
distinct from all other (unselected) cards on screen — the previously-reported "no visual feedback on tap"
symptom is resolved.

## 5. Gate results (actual numbers observed)

| Gate | Result | vs. expected |
|---|---|---|
| `run_kotlin_tests.py` | **160/160 PASS** | matches |
| `datalayer_oracle.py` | **ALL GREEN** (2+1+2+4 = 9/9) | matches |
| `realtap_gate.py --case existing` | **GATE: GREEN** (3/3) | matches |
| `realtap_gate.py --case overlay` | **GATE: GREEN** (7/7) | matches |
| `realtap_gate.py --case reactivity` | **GATE: GREEN** (4/4) | matches |
| `interact.py` (28 screens + shell, chunked via `chunk.py`/`hchunk.py`/`shell.py`) | **540/542 ok** (2 fail: `onQueryChange(None)` in `ExercisesScreen` + `ExercisePickerScreen`, same pre-existing `render/interact.py` arg-inference gap documented in `ktmap_fix_gate_reconciliation.md`, unmoved) | matches, unmoved |
| `fidelity` (30 screens via `fchunk.py`) | **403/406** (`ProgramsScreen` 1/3, `ExercisesScreen` 6/7 — same pre-existing stale-baseline/fuller-live-tree mismatches) | matches, unmoved |
| Geometry (`layout_diff.py ProgramsScreen`) | Same `Programs` FAIL, worst Δ **11.1%** — byte-identical to the pre-existing documented drift | unchanged, confirms this was a paint-only change |

No thresholds were tuned, no ground-truth dumps were edited, and no failing assertion was massaged to reach
these numbers. Every number matches the pre-existing baseline exactly except the targeted proof, which is
now a genuine PASS where it previously showed the recorded colors/border props entirely absent.

## 6. Files touched (within the file fence)

- `tools/pseudokotlin/runtime/compose_ui.py` — `ColorsSpec`, `_scheme_role`, `CardDefaults`,
  `ButtonDefaults`, `FilterChipDefaults`, `AssistChipDefaults`, `TopAppBarDefaults`, `BorderStroke`.
- `WFL_MixingCenter/render/kivy_kit.py` — `_colors_spec_fill`, `_border_stroke_spec`, `_paint_spec()`
  priority reorder, `_theme_button()` `colors=`/`border=` override.
- Transpiled output regenerated via `build_mixingcenter.py` (LAW-compliant); confirmed byte-identical to
  before (no transpiled file actually changed, since only runtime VALUES changed, not transpiler structure).

No files outside this fence were edited. No hand-edits to transpiled Python. Nothing committed to git.
