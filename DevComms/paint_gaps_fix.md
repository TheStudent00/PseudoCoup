# Paint gaps fix — three general appearance bugs (kivy_kit.py)

Date: 2026-07-05. File touched: `~/Programming/WFL_MixingCenter/render/kivy_kit.py` ONLY.
All fixes are canvas-only (paint), no geometry change. Gates below stay green.

---

## Bug 1 — "fixed TabRow" renders as a solid dark-gray bar (ExercisesScreen, ProgressScreen)

- **Cause (the report's hypothesis was wrong):** it is NOT a fixed-vs-scrollable container color.
  It is the *tabs themselves*. `ExercisesScreen` uses `PrimaryScrollableTabRow` + `Tab`;
  `ProgressScreen` uses `TabRow` + `Tab`. Both use real **`Tab`** composables. `Tab`/`LeadingIconTab`
  are in `BUTTON_KINDS` but had **no entry in `_BUTTON_ROLE` and are not `CHIP_KINDS`**, so
  `_theme_button()` returned early and left Kivy's DEFAULT gray button texture (white text on gray).
  Packed edge-to-edge (or side-by-side) those gray buttons read as one dark bar.
  The "scrollable tab rows render light" screens (WinsList, ExercisePicker, SuggestedStretches) do
  NOT use `Tab` at all — they use **`FilterChip`**, which `_theme_button` already themes (surface +
  outline). That is the entire source of the light-vs-dark difference.
- **General fix (kind-driven):** added `TAB_KINDS = {"Tab","LeadingIconTab"}` and a branch in
  `_theme_button`: Tabs get a **transparent container** (the TabRow's surface shows through, exactly
  like an IconButton) and their label/icon color = `primary` when `selected is True` else
  `onSurfaceVariant` (M3 tab indicator/label roles). No invented color (LAW 1); one branch moves both
  screens (LAW 2).
- **Role/file:** `_theme_button` + `TAB_KINDS` in `kivy_kit.py`.
- **Verify:** Exercises + Progress tab bars now read light/themed, selected tab in primary. FilterChip
  screens (WinsList etc.) unchanged — the branch never touches them (no regression).

## Bug 2 — missing leading icons / tofu boxes (Warmup, Cooldown, GymCreateWizard, UpdateProgramWizard)

- **Cause (also mis-framed as Material icons):** these are **NOT `Icon` composables and NOT Material
  icon names**. They are bare **`Text(activity.emoji)` / `Text(type.emoji)` color-emoji graphemes**
  (🕺 ☀️ 🤸 🥊 🚴 🚶 🏋️ 🧩 🏠 …). They flow through `_leaf_label` and render in the app's own
  typeface (Figtree), which has **no emoji glyphs** → the Label draws an empty box (tofu). The Material
  toolbar icons on the same screens (ArrowBack/HelpOutline/Check/Add/play-triangle) resolve fine
  because they take the separate `_draw_icon` Material-font path. So it is a subset symptom, but the
  subset is *emoji Text*, not unmapped icon names.
- **Why not just register an emoji font in Kivy:** the only emoji font on the machine is
  `NotoColorEmoji.ttf` (a CBDT bitmap-strike color font). Registering it with Kivy's SDL text provider
  and refreshing a glyph **segfaults** (verified). Pillow, however, rasterizes it cleanly
  (`embedded_color=True`, fixed 109px strike) — verified all the used graphemes render.
- **General fix:** added an emoji raster path that mirrors `_draw_icon`:
  `_emoji_pil_font()` (loads NotoColorEmoji via Pillow once), `_emoji_texture()` (rasterizes a grapheme
  string — whole string so base+variation-selector like 🏋️/☀️ render as one glyph — to a cached Kivy
  Texture), `_draw_emoji()` (paints it on `canvas.after`, scaled to the Label's height, centered, bound
  to pos/size). In `_leaf_label`, when `_emoji_only(node.text)` and a glyph was drawn, the Label's own
  color is set to alpha 0 so the tofu is hidden and only the emoji texture shows. **Geometry untouched**
  — the existing emoji width/height bindings still run (LAW 3).
- **Role/file:** `_load`/`_emoji_pil_font`/`_emoji_texture`/`_draw_emoji` + call site in `_leaf_label`.
- **Legitimately still empty:** none of the four screens. If the emoji font were absent, or a grapheme
  the font lacks, `_draw_emoji` returns False and the Label renders its own text (no wrong glyph). No
  emoji in these screens hit that case.
- **NOT a transpiler/runtime issue** — the emoji reach `_leaf_label` as normal Text nodes; the miss was
  purely the render kit having no emoji glyph source. Fixed in-kit.

## Bug 3 — Checkbox/Switch render with no visible box (ExerciseCreateScreen)

- **Cause:** `Switch`/`Checkbox`/`TriStateCheckbox`/`RadioButton` are `ATOM_KINDS`. `_leaf_atom` gave
  them their intrinsic reserved box (Switch 52x32, others 24x24) but **painted nothing** — the control
  was invisible. ExerciseCreate's "Unilateral"/"Compound" use `Switch(checked=…)`.
- **General fix (kind-driven):** added `_CONTROL_KINDS` + `_control_checked()` (reads the recorded
  `checked`/`selected` bool, or a resolved `State.value`, else False) + `_draw_switch/_draw_checkbox/
  _draw_radio` + `_draw_control` dispatch, called from `_leaf_atom`. All colors come from theme roles:
  - Switch: checked = primary track + onPrimary thumb (24dp, right); unchecked = surfaceVariant track +
    outline stroke + outline thumb (16dp, left).
  - Checkbox: checked = filled primary + onPrimary checkmark; unchecked = 2dp onSurfaceVariant outline.
  - RadioButton: primary/onSurfaceVariant ring + primary inner dot when selected.
  Any role the theme omits -> that piece is skipped (unthemed run paints nothing, identical to before).
  canvas.after only; the reserved box is untouched (LAW 3), no invented color (LAW 1).
- **Role/file:** `_CONTROL_KINDS` / `_control_checked` / `_draw_switch` / `_draw_checkbox` /
  `_draw_radio` / `_draw_control` + call site in `_leaf_atom`.
- **Verify:** ExerciseCreate shows both switches (unchecked resting state: light track + left thumb).

---

## Gate outputs

- `cd ~/Programming/PseudoCoup/tools/pseudokotlin && python3 fidelity.py`
  → **FIDELITY ALL: 377/377 components within tolerance (28 screens)**
- `cd ~/Programming/WFL_MixingCenter/render && python3 interact.py`
  → **INTERACT: 513 fired, 513 ok, 0 failures across 27 screens**

## Shots (layout_inspect/shots/)

- `before_ExercisesScreen0001.png` / `after_ExercisesScreen0001.png` — gray bar -> light themed tabs
- `before_ProgressScreen0001.png` / `after_ProgressScreen0001.png` — gray bar -> light themed tabs
- `before_WorkoutWarmupScreen0001.png` / `after_WorkoutWarmupScreen0001.png` — tofu -> color emoji
- `before_ExerciseCreateScreen0001.png` / `after_ExerciseCreateScreen0001.png` — invisible -> visible switches
- `after_WinsListScreen0001.png` — FilterChip tabs unchanged (no regression)
- `after_UpdateProgramWizardScreen0001.png`, `after_GymCreateWizardScreen0001.png` — emoji cards fixed
