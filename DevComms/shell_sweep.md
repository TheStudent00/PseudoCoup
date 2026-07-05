# Shell sweep -- extending interact.py to cover the app shell

## What it covers

`interact.py`'s existing sweep only ever composes ONE destination at a time (`build_screen`), so it never
exercised the app shell that the real app actually runs: `AppNavigation` (`run_app.build_app_composition`) --
a `Scaffold` whose slots are the bottom `NavigationBar`, the top bar, and (when present) a FAB, framing a
`NavHost` that swaps destinations by route. A regression that silently broke a nav tap, a top-bar action, or
a FAB would never show up in the 513/513 destination number.

Added a second phase, `sweep_shell(ns)`, that:

1. Builds the WHOLE app via `run_app.build_app_composition(ns)` (`build_shell`), after resetting the DB the
   same way `build_screen` does (`fresh_db()`), for the same per-handler isolation floor the destination
   sweep already uses.
2. **Settles** the composition: `AppNavigation`'s first compose can still be on the
   `onboardingCompleted == null` loading branch (a bare `CircularProgressIndicator`, no Scaffold/nav bar
   yet) before the seeded user's state resolves. `build_shell` recomposes in a loop, checking
   `comp.root.count()` for two consecutive equal reads (a settle-by-observation, not a fixed sleep --
   headless so no Kivy Clock/Window loop is involved, just repeated `comp.compose()`).
3. **Scopes to shell chrome only**: `find_scaffold_path` walks the tree to the one `Scaffold` node
   (`compose.py`'s `Scaffold()` already tags every child with `props["slot"]` -- `topBar` / `bottomBar` /
   `content` / `floatingActionButton` / `snackbarHost` -- so this reuses existing, general instrumentation
   rather than inventing new per-screen markers). `enumerate_shell_handlers` only walks the `topBar`,
   `bottomBar`, and `floatingActionButton` slot subtrees -- never `content`, which is the NavHost's current
   destination and is already covered by the 513-handler destination sweep. In practice this yields the 5
   `NavigationBarItem` taps (Home/Program/Paths/Progress/You); the top-bar notification star and the
   resume-session banner only render when their driving state is true, which the fresh seed leaves false,
   so they aren't in this run's count -- the mechanism would pick them up automatically if a fixture ever
   seeds that state (no per-screen exclusion needed).
4. Fires each shell handler on its OWN fresh shell build (fresh DB + fresh compose + re-settle), exactly
   mirroring the per-destination isolation contract, using the SAME `fire()` / `_invoke()` / exception
   grouping machinery -- no separate accounting path that could hide a real crash.

## Route-assertion design

For every fired handler whose owning node is `kind == "NavigationBarItem"` and `kind == "onClick"`, the
sweep additionally asserts `runtime.navigation.last_controller.currentRoute()` equals that item's OWN
destination route, read from one small declarative table (`NAV_ROUTES`) sourced directly off
`BottomNavItem.kt`'s 5 entries (label -> route): Home->today, Program->my_program, Paths->paths,
Progress->progress, You->settings. `navigation.last_controller` is the module-level "most recent NavHost's
controller" the runtime already exposes (same handle `realtap_gate.py`'s real-touch gate reads). A tap that
fires without moving the route to its OWN target raises `AssertionError` and is counted as a FAILURE, not an
ok -- this is a genuine behavioural check, not a survives-without-crashing check: if `navigate()` silently
no-opped, the handler would still "run" cleanly but the assertion catches it.

## A finding, fixed inside the file fence

Importing `run_app` (needed for `build_app_composition`) has a MODULE-LEVEL side effect: it flips
`kivy_kit.OVERLAYS_ENABLED` from `False` to `True` (`run_app.py` line 41 -- "the RUNNING app shows popups as
Window overlays; the layout inspector leaves this False"). Left unguarded, that import alone silently changed
the DESTINATION sweep too: `PathDetailScreen`'s handler count flipped 1 -> 3 between runs once `run_app` was
imported, because overlay subtrees started emitting handlers the un-shelled sweep never saw before -- this
would have broken the "513/513 stays comparable" requirement. Fixed by resetting
`kivy_kit.OVERLAYS_ENABLED = False` right after the import (restoring the instrument's own default for the
destination sweep), and only flipping it `True` for the duration of `build_shell`/`sweep_shell`, restored via
`try/finally` afterward. This is a fix inside the file fence (`interact.py` only) to the INSTRUMENT's own
state hygiene -- not a change to `run_app.py`, `kivy_kit.py`, or the runtime.

## Final numbers (two back-to-back runs, `xvfb-run -a python3 interact.py`)

Run 1:
```
INTERACT: 513 fired, 513 ok, 0 failures across 27 screens
SHELL: 5 fired, 5 ok, 0 failures
INTERACT: 513 fired, 513 ok, 0 failures across 27 screens + shell(5 handlers)
SHELL DETAIL: 5 fired, 5 ok, 0 failures
```

Run 2 (identical):
```
INTERACT: 513 fired, 513 ok, 0 failures across 27 screens
SHELL: 5 fired, 5 ok, 0 failures
INTERACT: 513 fired, 513 ok, 0 failures across 27 screens + shell(5 handlers)
SHELL DETAIL: 5 fired, 5 ok, 0 failures
```

`fidelity.py`: `FIDELITY ALL: 377/377 components within tolerance (28 screens)` -- unchanged, confirming no
shared-state damage from touching `interact.py`.

## Scope note

Only 5 shell handlers exist to fire in this seed state (the 5 bottom-nav items). The top-bar notification
star and the resume-session banner button are real shell chrome but gated behind state
(`showNotificationPanel`, `activeSession`) that the fresh seed leaves false/null, so they don't render in
this composition and aren't enumerated -- this is the SAME kind of declarative, state-dependent visibility
the destination sweep already lives with (e.g. dialogs that only render when a flag is true), not a
per-screen special case. If a future fixture seeds an active session or unread notifications, the general
mechanism (walk topBar/bottomBar/FAB slot subtrees, fire every handler found) picks them up with no
`interact.py` changes required.

FILE FENCE respected: only `~/Programming/WFL_MixingCenter/render/interact.py` was touched. `run_app.py`,
`kivy_kit.py`, `realtap_gate.py`, and the runtime are unmodified.
