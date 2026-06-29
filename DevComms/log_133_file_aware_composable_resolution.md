# log_133 — generator: file-aware composable resolution (overloads) → 100% Compose coverage

Date: 2026-06-29
Type: generator fix. Resolves the DetailSection overload blemish from log_132.

## The bug

The generator's composable-definition maps (`ui_ledger._comp_defs` for the structural side,
`pseudoui_run._comp_bodies` for the behaviour side) were GLOBAL `name -> def` dicts built by walking
the whole `ui/` tree — **last-wins**. `DetailSection` is defined 3 times:
`ExerciseDetailScreen`'s `(title, content: @Composable)`, `PathDetailScreen`'s, and
`CycleDetailDialog`'s `(title, body: String)`. The `body: String` version overwrote the content-slot
one, so exercise_detail's `DetailSection(title){ content }` calls inlined the wrong overload — the
content slot became an unbound `body` text leaf rendering `None`.

## The fix

Both maps now also keep a per-file map (`_DEFS_ALL` / `_BODIES_ALL`: `name -> {file -> def}`), and a
`*_for(screen_path)` resolver prefers the definition in the SCREEN'S OWN FILE, falling back to the
global default. The structural generator (`pseudoui.generate`) and the behaviour generator
(`build_ir`) both pass the screen path. So exercise_detail's `DetailSection` now resolves to its
own file's content-slot version.

## Verified

- **Compose leaf coverage 99% (493/496) → 100% (496/496)** — the 3 previously-missed DetailSection
  slots are now covered.
- no regression: 0 fabricated, 0 orphan trees, hand-built-leaves-not-reproduced unchanged at 6 (kit
  glyph decorations, not Compose); gym_list 10/10 (--auto + --app), all screens stable, oracle
  untouched.
- exercise_detail: stray `None` leaves **2 → 0**; re-vendored; `test_exercise_detail_gen` RESULT MATCH
  (render + SharedFlow nav + reactive dialog); smoke 30/30.

## exercise_detail routing — still deferred (one real reason)

The `None` blemish is gone, but the generated screen renders the overflow-menu items INLINE
(`Duplicate & Edit` / `Never program this` + a `More` icon) because the DropdownMenu collapse behaviour
isn't modeled — the menu STRUCTURE is captured (more faithful than the simplified hand-built) but its
items show always-visible. So routing exercise_detail would change the visible UI. Left vendored +
proven; routing awaits DropdownMenu-collapse modeling (a generator feature) or an explicit OK to ship
the more-complete menu.
