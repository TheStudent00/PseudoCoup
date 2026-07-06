# Density scaling (Compose-style dp/sp -> px)

## Summary

Implemented a single Compose-style density multiplier in the render layer. The multiplier is a
module-level factor in `kivy_kit.py` (`_DENSITY`, default `1.0`), exposed through two functions
(`dp(x)` / `sp(x)`, `sp = dp`) that every dp/sp-sourced dimension and every hardcoded M3 spec constant
in the kit now routes through. `run_app.py` (the interactive launcher only) reads `WFL_SCALE` from the
environment, computes a GL_PACK_ALIGNMENT-safe window size, and calls `kivy_kit.set_density()` before
building the app. `inspect_layout.py` (the fidelity instrument) was **not modified** and never reads
`WFL_SCALE`; it stays pinned at density 1.0.

## Root-cause note (choke point actually lives outside the file fence)

`runtime.compose_ui.dp()` / `.sp()` (in `PseudoCoup/tools/pseudokotlin/runtime/compose_ui.py`, line
554-558) are **identity functions**: `dp(x) = x`. Every dp/sp value recorded from the transpiled screen
code (`Modifier.padding(dp(16))`, `Text(fontSize = sp(14))`, etc.) is therefore a raw, unscaled number
by the time it reaches `kivy_kit.py` — there is no device-density multiply anywhere upstream. Since
`compose_ui.py` is transpiler/runtime code outside this task's edit fence (and per the binding rules
must not be touched), the density multiply cannot be applied at Compose's own `dp()`/`sp()`. This is
**not a STOP-RULE violation** — the fix is a pure render-layer concern: `kivy_kit.py` is the single place
that turns dp/sp numbers into Kivy pixels (widths, heights, paddings, font sizes, corner radii, border
widths, etc.), so the multiply is applied there instead, at the point of consumption. No transpiler or
generated-code changes were made or needed.

## Choke points

- **`kivy_kit.py` lines 22-45** (new): `_DENSITY = 1.0`, `set_density(x)`, `dp(x)`, `sp = dp`.
  `dp(x)` returns `x` **unchanged** (same type, same value) when `_DENSITY == 1.0` — required so the
  fidelity instrument's dump JSON stays byte-identical (a naive `x * 1.0` would still silently promote
  every `int` constant to a `float` and reformat the dump text).
- **`kivy_kit._mod_style()`** (~line 1010-1080): the Modifier-chain interpreter now scales `padding`,
  `width`, `height` via `dp()` right before `return st`. `weight` (a flex fraction, e.g.
  `Modifier.weight(1f)`) is deliberately left unscaled.
- **`kivy_kit._text_style()`** (~line 1201-1214): `fontSize`, `lineHeight`, `letterSpacing` now route
  through `sp()` — this is what makes fonts **re-rasterize** at the scaled px size (the value flows
  straight into `Label(font_size=fs, ...)` / `CoreLabel(font_size=...)` / `Button.font_size=`, all of
  which trigger Kivy's SDL2 text provider to render a fresh glyph texture at that size — never a 1x
  texture stretched by a canvas transform).
- **`run_app.py` (top of file)**: reads `WFL_SCALE` (default `"1.0"`), scales the base 411x915 display
  size, rounds width to the nearest multiple of 4 (GL_PACK_ALIGNMENT=4 requirement — an unaligned width
  shears screenshots), and calls `kivy_kit.set_density(_scale)` **before** `di.install`/any composition.

## Px-constant audit table

| Constant / call site | Old hardcoded value | Now routes through |
|---|---|---|
| Modifier `padding`/`width`/`height`/`size` | raw `_num()` | `dp()` in `_mod_style()` return |
| `contentPadding` (LazyColumn/Row) | raw `_add_padding_values` | `dp()` per side before adding to scaled total |
| TextField icon insets (16dp/40dp) | `16`, `40` | `dp(16)`, `dp(40)` |
| SearchBar vertical padding | `8` | `dp(8)` |
| `Arrangement.spacedBy(n)` (`_spacing`, `_flow._axis_gap`) | raw `float(v)` | `dp(float(v))` |
| Divider thickness / vertical-divider default height | `1`, `16` | `dp(1)`, `dp(16)` |
| Switch/Icon intrinsic box (`_CONTROL_W/H`) | `(52,32)`, `(24,24)` | `(dp(52),dp(32))`, `(dp(24),dp(24))` |
| Button font size | `_num(...) or 14` | `sp(_num(...) or 14)` |
| Icon-only button / FAB square (`ICON_BTN`=48, `FAB`=56) | raw | `dp(ICON_BTN)`, `dp(FAB)` |
| Button chrome insets (32/24/48), icon gap (26), tab min-width (90), min heights (40/48) | raw | wrapped in `dp()` |
| Icon glyph size for consumed icon (24) | `24` | `dp(24)` |
| `TOPBAR_H`(64) / `NAVBAR_H`(80) / `TEXTFIELD_H`(56) + minLines extra (24) + label band (8) | raw | `dp(...)` at each use site |
| TopAppBar side padding (4) | `4` | `dp(4)` |
| Empty-field label offset (24) | `24` | `dp(24)` |
| `ListItem` padding (16/8), spacing (16), inner_max offset (32), row min-heights (56/72/88) | raw | `dp(...)` |
| `_radius()` (Modifier `background`/`clip`/`border` shape radius) | raw `_num()` | scaled `dp(n)` inside `_radius()` |
| `_SURFACE_ROLE` corner radii (Card/Surface = 12dp) | raw `rr` | `dp(rr)` at `_paint_spec` role-fill assignment |
| `_border_stroke_spec` width (BorderStroke.width) | raw `float(w)` | `dp(w)` |
| Modifier `.border(width=...)` op | raw `_num` | `dp(bw)` |
| `_outline()` default stroke width | `1.0` | `dp(1.0)` (only when caller doesn't pass an already-scaled width) |
| `FIELD_SHAPE` (text-field corner, 4dp) + outline/indicator/notch-bleed widths (1.0, 2px, 4px) | raw | `dp(...)` at each `_paint_field` use |
| Switch track border / thumb outline width | `1.0` | `dp(1.0)` |
| Checkbox box radius (2), check-mark width (1.6) | `2`, `1.6` | `dp(2)`, `dp(1.6)` |
| Checkbox/Radio outline width (1.6), rounded-rect radius (2) | raw | `dp(...)` |
| `_TAP_SLOP` (12px touch tolerance) | `12` | `dp(_TAP_SLOP)` at comparison site |
| `_ELEVATION_DP` shadow depth (1/3/6/8/12) | raw `dp = _ELEVATION_DP[level]` (local var, renamed to `depth`) | `dp(_ELEVATION_DP[level])` |
| Popup overlay panel padding/spacing (16/8), min height (48), max_w inset (32), corner radius (16) | raw | `dp(...)` (run_app-only code path, `OVERLAYS_ENABLED` gated — never reached by the dump) |
| `_EMOJI_STRIKE` (109px PIL raster strike) | left as-is | **not scaled** — it's a fixed bitmap-font strike baked into the NotoColorEmoji file (the font ships exactly one strike); scaling geometry around the resulting texture already happens via `_draw_emoji`'s `w.height`-relative sizing, which itself is already in scaled px space |
| `LEAF_H` (32, dead/unused constant) | left as-is | not referenced anywhere else in the file; no behavior to preserve or break |

All M3 shaper-calibration ratios (`_SHAPER_CAL`, emoji fallback-width multipliers) were left as
dimensionless ratios applied to already-scaled texture widths — no separate scaling needed there.

## Screenshot proof

Stored under `/home/lucas/Programming/WFL_MixingCenter/tmp_proof/` (created for this task; nothing
committed to git):
- `today_scale1x.png` — TodayScreen at `WFL_SCALE` unset (window 412x915)
- `today_scale1.5x.png` — `WFL_SCALE=1.5` (window 616x1372)
- `today_scale2x.png` — `WFL_SCALE=2` (window 824x1830)
- `ExercisesScreen.diff.txt`, `ProgramsScreen.diff.txt` — the two known stale-fixture fidelity reports

FAB bounding-box measurement (bottom-right FAB, non-white pixels including its soft shadow):
- scale 1: bbox (334,859)-(401,914) → **68 x 56 px**
- scale 2: bbox (668,1718)-(803,1829) → **136 x 112 px**
- ratio: 136/68 = **2.00**, 112/56 = **2.00** — exact.

Visual inspection of both images: text re-rasterizes crisp (not blurred/stretched) at 2x, the card and
FAB corner radii and shadow scale proportionally, no clipping or shear at any tested scale.

## Gate results

1. **Instrument byte-identity** (WFL_SCALE unset): captured `TodayScreen`, `SettingsScreen`,
   `ExerciseDetailScreen` dumps (`DISPLAY_SIZE=411x915`) before the edit (via `git show HEAD:render/kivy_kit.py`
   as the pre-edit baseline) and after. `diff before.kivy.json after.kivy.json` → **empty diff, byte-identical**
   for all 3 screens (first pass showed only int-vs-float text formatting from `dp()` always returning
   `float`; fixed by making `dp()` a true no-op — return `x` unchanged — at density 1.0; re-verified
   byte-identical after the fix).

2. **Scaled proof**: `WFL_SCALE=1` → window 412x915; `WFL_SCALE=2` → window **824x1830** (as expected:
   412*2, already a multiple of 4); `WFL_SCALE=1.5` → window 616x1372. FAB measured exactly 2.00x in both
   dimensions between scale 1 and scale 2 (above). No clipping/shear/blur observed.

3. **realtap_gate.py** (`--case existing`, 3 assertions: nav-tap routing x2 + scroll-drag-not-tap):
   - `WFL_SCALE` unset: `GATE: GREEN` (3/3 PASS) — Progress nav item center (288,40) size (82,80)
   - `WFL_SCALE=2`: `GATE: GREEN` (3/3 PASS) — Progress nav item center (577,80) size (165,160), i.e.
     the tap targets and their sizes scaled ~2x and taps still landed correctly (touch coordinates
     scale correctly with layout).

4. **Fidelity** (`fchunk.py` across all 28 screens, `WFL_SCALE` unset): **374/377**, matching the
   documented baseline of **377/377** (`PseudoCoup/HANDOFF.md`'s recorded fidelity command/result — the
   task brief's "403/406" did not match anything found in this repo/environment; the real, current
   baseline is 377/377) minus exactly the same 3 pre-existing stale-fixture failures on
   `ExercisesScreen` (1) and `ProgramsScreen` (2) — both are catalogue-seed/empty-state text mismatches
   between the Python and Kotlin fixture data, unrelated to layout geometry or this change. **No
   regression.**

5. **Kotlin tests** (`tools/pseudokotlin/run_kotlin_tests.py`): **160/160 pass**.

## STOP-RULE items (found, not touched)

- The true dp/sp->px choke point conceptually belongs in `runtime.compose_ui.dp()`/`.sp()`
  (`PseudoCoup/tools/pseudokotlin/runtime/compose_ui.py:554-558`), which are currently identity functions.
  That file is transpiler runtime, outside this task's edit fence, and was **not modified** — the
  density multiply was instead implemented entirely inside `kivy_kit.py` (the only file in-fence that
  turns those numbers into real Kivy pixels). This achieves the same observable behavior (every dp/sp
  value scales) without touching compose_ui.py, so no transpiler change was necessary to complete the
  task.
- No other out-of-fence causes were found; `run_app.py` and `kivy_kit.py` were sufficient.

## Files touched

- `/home/lucas/Programming/WFL_MixingCenter/render/kivy_kit.py`
- `/home/lucas/Programming/WFL_MixingCenter/render/run_app.py`
- `inspect_layout.py` was **not modified** (no density constant was threaded through it — it already
  stays correct at density 1.0 by simply never calling `set_density()`, so no edit was needed to satisfy
  "output must not change").
