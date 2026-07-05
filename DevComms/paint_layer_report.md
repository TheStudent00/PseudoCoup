# Paint Layer — Slice 1 Report

Scope: color/surface drawing in the Compose→Kivy kit, without disturbing geometry.
Edited ONLY `~/Programming/WFL_MixingCenter/render/kivy_kit.py`. Read (not edited)
`runtime/compose_ui.py` for the theme/CompositionLocal plumbing.

## Headline finding: the color table is entirely inert stubs

Before writing paint I probed the runtime (three `/tmp` probes across all 28 screens). Result:

- `Color(0xFF112233)` → `_UIChain` stub (`<ui>`). In `compose_ui.py`, `Color` is one of the
  `_NAMES` bound to the shared `_UI` stub; calling it returns the stub. **No color literal in the
  app resolves to channels.**
- `RoundedCornerShape(12)` → `_UIChain` stub. **No corner radius resolves to a number** either.
- `MaterialTheme.colorScheme.{surface,background,onSurface,onSurfaceVariant,primary,outlineVariant,...}`
  → all `_UIChain` stubs. `_MaterialTheme.colorScheme` is set to `_UI` with the explicit comment
  *"colorScheme stays inert until the kit paints colors."*
- The recorded `Modifier` ops ARE present and plentiful across the tree:
  `background` ×146, `border` ×314, `clip` ×305 — but every `color=`/`shape=` argument is `<ui>`.
  (`border`'s `width=` IS real, e.g. `Int32(1)`, because `dp` is real — but with a stub color it
  can't be drawn.)
- **Zero** nodes record an explicit `color=`/`containerColor=`/`colors=` prop. Nothing is
  concretely recorded as a resolvable color anywhere.
- Card/ElevatedCard/OutlinedCard/Surface kinds are not even present on these screens; the only
  surface-ish kind that appears is `HorizontalDivider` — whose color would come from the (stub)
  `outlineVariant`.

Per the task's contingency ("if colorScheme values turn out to be inert stubs, paint ONLY what is
concretely recorded; do not invent a palette, do not hardcode hex"): there is nothing concretely
recorded to paint. So this slice paints **nothing visible today** — correctly and honestly — and
instead lands the *general mechanism* fully guarded, so paint switches on with no change here the
moment the color table becomes real.

## What was built (general mechanism, in `kivy_kit.py`)

All resolvers reject the inert stub by type name FIRST (`_INERT = {"_UIChain","Stub"}`), because the
stub duck-types as `0.0` under `float()` and would otherwise silently read as black.

1. `_channels(v)` — a concretely-resolvable color → `(r,g,b,a)` in 0..1, else `None`. Handles a
   packed int `0xAARRGGBB`, an `(r,g,b[,a])` 0..1 sequence, or an object with float
   `.red/.green/.blue[/.alpha]`. Stubs → `None`.
2. `_radius(shape)` — a shape's corner radius as a number, else square. Stub → default.
3. `_theme_color(role)` — reads `MaterialTheme.colorScheme.<role>` through `_channels`. `None` today.
4. `_paint_spec(node)` — interprets `background`/`clip`/`border` modifier ops PLUS the M3 surface
   role for Card/Surface/Scaffold/Divider kinds → `(fill_rgba, fill_radius, border)`, each piece
   `None` when unresolved. `clip(RoundedCornerShape)` rounds an accompanying background fill.
   Card = surface role @ 12dp, Surface = surface @ square, Scaffold = background role, Divider =
   outlineVariant. (These are M3 *structure*; the *color* still comes from the theme.)
5. `_paint(w, node)` — draws fill (`RoundedRectangle`) and/or border (`Line rounded_rectangle`) into
   `w.canvas.before`, bound to follow `pos`/`size`. **No-op** when nothing resolves, so geometry AND
   pixels are untouched. Hooked once at the `to_widget` chokepoint (a general layer, not per-screen).
6. Text color (`_leaf_label`): `lbl.color = _channels(node.props["color"]) or _theme_color("onSurface")`
   when non-None; else Kivy's default stays. Resolves to `None` today → default kept, never a wrong guess.

## Deferred / blocked

- All actual painting is blocked on the color table. **Required runtime change (out of this task's
  edit scope):** in `compose_ui.py`, make `Color(...)` pack an rgba value, install a real
  `colorScheme` (the app's `WorkoutforlifeTheme` M3 palette, resolved through the CompositionLocal
  path that already exists but currently hands back `_UI`), and make `RoundedCornerShape` carry a
  numeric radius. With those three, the mechanism here lights up unchanged: backgrounds, borders,
  card/surface/scaffold container colors, dividers, and text colors all begin drawing.
- No palette was invented and no hex was hardcoded from screenshots, per project law.

## Gate results

1. GEOMETRY UNCHANGED — `fidelity.py`: see `FIDELITY_RESULT` line below (must read
   `FIDELITY ALL: 377/377`). The paint pass only adds `canvas.before` instructions and pos/size
   binds; it changes no `size_hint`, size, or position, so geometry is structurally untouched.
2. Screenshots (411×915) written to `~/Programming/PseudoCoup/layout_inspect/shots/`:
   `TodayScreen.png`, `SettingsScreen.png`, `ProgramEditorScreen.png`, `GymListScreen.png`,
   `WorkoutExecutionScreen.png`. They show Kivy defaults (white bg, gray buttons, readable gray
   text) — i.e. no paint yet, matching the stubbed-theme reality. No black-on-black, no missing text.

FIDELITY_RESULT: PASS — `FIDELITY ALL: 377/377 components within tolerance (28 screens)`;
Specimen 24/24, SpecimenList 5/5. All per-screen counts identical to the pre-paint baseline.
