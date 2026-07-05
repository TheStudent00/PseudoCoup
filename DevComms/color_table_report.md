# Color table made real (compose_ui.py)

Task: light up the already-landed, stub-guarded paint layer in `render/kivy_kit.py` by making the
compose runtime's color/shape/scheme surface carry real values that flow entirely from the app's own
transpiled theme code. No hardcoded palettes.

Fence honored: only `tools/pseudokotlin/runtime/compose_ui.py` was edited.

## What became real

Promoted 5 names out of the inert `_NAMES` stub list into real classes/functions:

- **`Color`** — real class.
  - Packed form `Color(Int32(0xFF6650A4))`: the app's `Color.kt` builds every color as
    `Color(Int32(0x..))`, and `Int32` wraps the long to a **signed** 32-bit int (e.g. 0xFF8755F2 →
    negative). The constructor masks back with `& 0xFFFFFFFF` before unpacking A/R/G/B, so the signed
    delivery is handled.
  - Float form `Color(r, g, b[, a])` and channel kwargs (`red=`, `green=`, …).
  - Exposes `.red/.green/.blue/.alpha` as 0..1 floats (what the kit's `_channels` reads), plus
    `.value`, `.toArgb()`, and `.copy(alpha=…)` returning a new Color for chains the kit doesn't model.
    A permissive `__getattr__` tail returns the inert `_UI` for any other chained call.
  - Companions: `Color.White/Black/Transparent/Red/…`. **`Color.Unspecified = _UI`** — deliberately the
    inert `_UIChain` sentinel, NOT a Color, so `_channels` rejects it by type name (`_INERT`). The
    `WflColors` default of `Color.Unspecified` therefore paints nothing (correct) instead of a stray
    black.
- **`RoundedCornerShape(r)`** — exposes numeric `.radius` (and `.topStart/.topEnd/…` for the 4-corner
  kwarg form) for the kit's `_radius`.
- **`CircleShape`** — a singleton exposing `.radius = 9999.0`; the kit clamps to half the widget size.
- **`lightColorScheme(**roles)` / `darkColorScheme(**roles)`** — build an `_ColorScheme` whose role
  kwargs become attributes (each a real Color). Omitted roles are simply **absent** (`getattr → None`);
  no baseline palette is invented, so the kit falls back rather than the runtime guessing.

## How `MaterialTheme.colorScheme` resolves through the theme

The transpiled `WorkoutforlifeTheme` (ui/theme/Theme.py) calls
`MaterialTheme(colorScheme=(Dark|Light)ColorScheme, typography=Typography, content=…)`.
`_MaterialTheme.__call__` already installed the passed `typography`; I mirrored that one line for
`colorScheme`: when the kwarg is an `_ColorScheme`, `self.colorScheme = cs`. The kit's `_theme_color(role)`
reads `getattr(MaterialTheme.colorScheme, role, None)` → the app-installed scheme's Color → `_channels`.
So Card/Surface/Scaffold/Divider container colors, and any `MaterialTheme.colorScheme.<role>` read, now
flow from `LightColorScheme`/`DarkColorScheme` built in the app's own `Theme.py` from `Color.kt` values.

`WflTheme.colors.*` custom tokens already ride the real `CompositionLocal` plumbing; once `Color` became
real they carry real Colors automatically (verified: accent Int32 unpacks to sane channels). No change
needed there.

## Coercion fixes forced by the geometry gate

None. Fidelity held at the exact baseline on the first run (see below) — real Colors/shapes flowing
through the previously-stubbed paths did not shift any measurement, because the shapes expose plain
floats and Colors don't participate in layout arithmetic.

## Gate results

1. **Geometry** — `python3 fidelity.py` → `FIDELITY ALL: 377/377 components within tolerance (28
   screens)`, every screen at its baseline count, Specimen 24/24, SpecimenList 5/5. Unchanged.
2. **Paint visibly on** — regenerated screenshots into `layout_inspect/shots/` for TodayScreen,
   SettingsScreen, ProgramEditorScreen, GymListScreen, WorkoutExecutionScreen via a /tmp runner
   mirroring inspect_layout's Inspector (build → mount → settle → `Window.screenshot`). All render with
   themed white backgrounds, dark readable text, and tinted top app bars / buttons / FABs (Join, Finish,
   Add set, Log set, Active, Delete gym) with white labels. No black-on-black, no white-on-white.
3. **Sanity** — `Color(0xFF6650A4)` → `red=0.4 green=0.3137 blue=0.6431 alpha=1.0`. Sane 0..1.

Not committed / not pushed, per instructions.
