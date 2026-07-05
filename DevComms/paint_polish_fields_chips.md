# Paint polish — text fields + chips

Scope: two M3 paint refinements in the Kivy kit. Edited ONLY
`~/Programming/WFL_MixingCenter/render/kivy_kit.py`. No runtime/transpiler change; no commit/push.

## 1. Text-field decoration (NEW)

New `_paint_field(w, node)` + `_find_widget(w, pred)` helper + `FIELD_SHAPE = 4.0` constant, hooked at the
`to_widget` chokepoint right after `_paint`. All drawing is canvas instructions bound to the field's
pos/size — geometry is never touched. Applied ONLY to `TEXTFIELD_KINDS` (the kit's own set of genuine
Material fields); `BasicTextField` (foundation, undecorated) is deliberately excluded. The dump path has no
live focus, so the **unfocused resting state** is painted consistently — no faked focus ring.

- **OutlinedTextField** → 1dp rounded stroke (radius 4dp = M3 extra-small shape) in the `outline` role,
  drawn in `canvas.after` so it sits over the box. **Label notch:** the label slot widget is located via
  `_find_widget` (predicate: `node.props["slot"] == "label"`) and backed with a `surface`-colored rect
  (2px horizontal bleed) in its `canvas.before`, so the border reads as broken behind the floating label —
  the M3 label/notch treatment. `surface` is the container color the label sits on, not an invented clear.
- **TextField (filled)** → `surfaceVariant` container fill with top corners rounded 4dp / square bottom,
  plus a 1dp `onSurfaceVariant` active-indicator line along the bottom edge (M3 unfocused indicator color).

Every piece resolves from the app theme (`_theme_color`) or is skipped — LAW 1. `outline`/`surface`/
`onSurfaceVariant` all resolve in this app's theme; `surfaceVariant` resolves if the app defines it, else the
filled fill is skipped (no filled Material `TextField` appears on any current screen anyway — only
`OutlinedTextField` + `BasicTextField` — so the filled path is general-but-unexercised on today's screens).

Roles/colors and where they resolve from:
- outline stroke → `colorScheme.outline`
- label notch backing → `colorScheme.surface`
- filled container → `colorScheme.surfaceVariant`
- filled indicator → `colorScheme.onSurfaceVariant`

## 2. Chips — container correct, elevation DEFERRED

Chip container treatment was **already correct** from the prior paint pass (`_theme_button` +
`CHIP_KINDS`): unselected filter/assist chips → `outline` border (M3 keys off the recorded `selected`
prop); selected → `secondaryContainer` fill + `onSecondaryContainer` label. Confirmed visually on
ExercisePicker (24 FilterChips: "All muscles" selected = lavender fill, others outlined). No code change
needed here.

**Elevation (1dp shadow): DEFERRED.** A faithful M3 elevation shadow needs a soft/blurred drop-shadow,
which requires a general blurred-texture shadow mechanism the kit does not have; a crisp offset rect would
be exactly the one-off hack the task warns against, and a real elevation mechanism also ties into the
pending top-bar elevation-tint decision (surfaceContainer tint roles this app does not define). Per the
task's contingency, chips ship with border/fill only and elevation is left for a general elevation slice.

## Gates

- `cd ~/Programming/PseudoCoup/tools/pseudokotlin && python3 fidelity.py`
  → `FIDELITY ALL: 377/377 components within tolerance (28 screens)` (unchanged — paint never moves geometry).
- `cd ~/Programming/WFL_MixingCenter/render && python3 interact.py`
  → `INTERACT: 513 fired, 513 ok, 0 failures across 27 screens`.

## Screenshots (`~/Programming/PseudoCoup/layout_inspect/shots/`, 411×915, export_to_png)

- `ReportBugScreen_before.png` / `ReportBugScreen_after.png` — outlined field: after shows the
  "What happened?" OutlinedTextField gains a gray rounded outline with the label notched/readable.
- `ExerciseCreateScreen_before.png` / `ExerciseCreateScreen_after.png` — "Form notes (optional)" and
  "Coaching cues (optional)" OutlinedTextFields gain outlines + notched labels.
- `ExercisePickerScreen_before.png` / `ExercisePickerScreen_after.png` — FilterChips: outlined unselected,
  lavender-filled selected (already-correct chip container confirmed).

Inspected all after-shots: outlines clean, labels readable through the notch, no black boxes, no geometry
shift vs before.
