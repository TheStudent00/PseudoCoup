# Paint pass 2 — report

Scope: fix the three gaps from the first eyeball pass. Edited only
`~/Programming/WFL_MixingCenter/render/kivy_kit.py`. `compose_ui.py` needed no change (its
color table already resolves every role/Text color correctly — see gap 1).

## Theme probe (mirrors inspect_layout.build → MaterialTheme.colorScheme, light)
Real, non-inert Colors flow. Key roles:
- primary `(.459,.239,.941)` · onPrimary `(1,1,1)` · primaryContainer `(.949,.933,1)` · onPrimaryContainer `(.102,0,.365)`
- secondaryContainer `(.949,.925,.988)` · onSecondaryContainer `(.192,.157,.271)`
- surface `(1,1,1)` == background `(1,1,1)` · onSurface `(.110,.106,.122)` · onSurfaceVariant `(.286,.271,.306)` · outline `(.478,.459,.498)`
- surfaceContainer / surfaceContainerHigh/Low: ABSENT (app defines no container roles)

## Gap 1 — TEXT CONTRAST
- Cause: NOT a live bug. The existing `_leaf_label` already does
  `_tc = _channels(color) or _theme_color("onSurface")`, and both resolve: recorded per-Text colors
  are real dark Colors, onSurface is near-black. The committed pale-gray screenshots were **stale** —
  generated before the color table / text-color code landed (in them even "This week's workouts",
  which carries a recorded purple, rendered pale gray; with current code it renders purple).
- Fix: none needed to the color logic. The distinction the task asked for is already honored:
  explicitly-colored Text keeps its recorded color; only default-role Text falls back to onSurface.
- Secondary finding: the committed shots were also **sheared / black-background** artifacts of
  `Window.screenshot` glReadPixels at a non-4-aligned width. Regeneration now uses
  `widget.export_to_png` (clean Fbo readback) at 412×915. New shots show near-black body text on white.
- Role used: `onSurface` (default fallback), recorded Color otherwise.

## Gap 2 — TOP APP BAR
- Cause: `TOPBAR_KINDS` were absent from `_SURFACE_ROLE`, so the bar container was never painted.
- Fix: added `TopAppBar` / `CenterAlignedTopAppBar` / `MediumTopAppBar` → `("surface", 0.0)` in
  `_SURFACE_ROLE`; the existing `_paint_spec`/`_paint` mechanism now fills them.
- Role used: `surface` (M3 small-top-app-bar container; the app defines no surfaceContainer role, so
  surface is the spec-correct fallback M3 itself uses at rest).
- Note: because this theme has `surface == background == white`, the painted bar is correct but not
  visually distinct from the page. Making it a different tint would require inventing a color, which
  project law forbids. See remaining gaps.

## Gap 3 — BUTTONS / CHIPS
- Cause: buttons carry no recorded container color and were left at Kivy's default gray skin.
- Fix: new `_theme_button(b, node)` (called at the end of `_leaf_button`), plus `_BUTTON_ROLE` map and
  an `_outline()` canvas.after stroke helper. One consistent approach: `background_normal =
  background_down = ""` + flat `background_color` for the container, `b.color` for the label, an
  outline Line for bordered kinds. Roles come only from the theme; an unmapped kind or a missing role
  leaves Kivy's default.
- Roles used:
  - filled `Button` → container `primary`, label `onPrimary`
  - `FilledTonalButton` → `secondaryContainer` / `onSecondaryContainer`
  - `FloatingActionButton` / `ExtendedFloatingActionButton` → `primaryContainer` / `onPrimaryContainer`
  - `OutlinedButton` → transparent container, label `primary`, border `outline`
  - `TextButton` → transparent container, label `primary`
  - icon buttons (`ICON_BUTTON_KINDS`) → transparent container
  - chips + segmented buttons (`CHIP_KINDS`): selected → `secondaryContainer`/`onSecondaryContainer`;
    unselected → container `surface`, label `onSurfaceVariant`, border `outline` (keyed off the
    recorded `selected` prop — one general chip rule, no per-chip special case)

## Gate results
1. `python3 fidelity.py` → `FIDELITY ALL: 377/377 components within tolerance (28 screens)`; every
   screen at baseline; `Specimen gate: 24/24`; `SpecimenList gate: 5/5`. (Paint never touches geometry.)
2. Regenerated shots (export_to_png) for TodayScreen, SettingsScreen, ProgramEditorScreen,
   GymListScreen, WorkoutExecutionScreen, HistoryScreen and inspected them: body text near-black on
   white; TextButtons (Finish/Add set/Delete gym/Join) purple; filled Button (Log set) purple with
   white label; segmented buttons show selected=lavender vs unselected=outlined; AssistChip (Active)
   surface+outline; FABs lavender (primaryContainer); icon buttons transparent; outlined text fields
   bordered.
3. No invented hex: `git diff` grep for `0x…/#…/Color(0.…)/rgba(` returns nothing. Only role-name
   strings and structural constants (fully-transparent `(0,0,0,0)`, 1px outline width) added.

Not committed / not pushed.
