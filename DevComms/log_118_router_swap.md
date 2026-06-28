# log_118 — router swap: the app now SERVES the generated gym_list (smoke 30/30)

Date: 2026-06-28
Type: milestone. The app uses the generated screen via its real router. Touches WFL_PseudoCoup
(app_router.py + the regenerated screen).

## Direct answer

`AppRouter` now mounts the GENERATED gym_list screen instead of the hand-built one, and the app's
own smoke test still passes:

```
app_router.py:  self.gym_list = GymListScreenGen(db)    # was GymListScreen(db)
python tools/smoke_screens.py  ->  SMOKE: 30/30 screens built   (gym_list = generated, via navigate())
python tools/test_gym_list_gen.py -> shared 10, gen-only [], hb-only []  (still a drop-in match)
```

So the live app routes gym_list through the screen whose structure+control flow came from Compose,
whose viewmodel/entities/enum are transpiled Kotlin, and whose bindings are transpiler-emitted —
mounted and rendered by the real router, validated by the app's own headless harness.

## What the swap needed

The router does two things with a screen: `screen.build(ui, CONTENT_ID, self)` and, on navigate-away,
`screen.owned_ids` (the zones to tear down). The generated screen emitted only the build; now
`emit_app_screen` wraps `ui` in a `_Track` proxy that records every `define_*`'s zone id into
`self.owned_ids`, and adds `screen_id()`. So the generated screen is mount- AND teardown-compatible.
30 zones tracked; matches the hand build 10/10.

## Honest caveat — interaction is not wired yet

The generated screen RENDERS identically but does not yet wire on_click NAVIGATION handlers
(the FAB -> create wizard, a card tap -> editor, back -> you). The emitter produces structure + data,
not the handler graph — and the navigation TARGETS aren't in the screen's Compose (they live in the
app's NavHost), so they need a small per-screen nav-target declaration (the way the data path needed
the adapter). The VM ACTIONS (setActive/delete) are on the transpiled VM and are mechanical; only the
route targets are declarative. Smoke (build-only) passes; full interaction is the next increment.
The swap is one line and reversible (the hand-built GymListScreen(db) is the swap-back).

## Status

The end-to-end vertical is now LIVE in the app for rendering: Compose -> structure -> control-flow IR
-> transpiled viewmodel -> transpiler-emitted bindings -> vendored runnable screen -> mounted by the
real router -> smoke 30/30. Remaining: (1) emit the on_click/nav handlers (+ a per-screen nav-target
map) for full interaction; (2) the Python->Dart frontier for the Flutter pixel goldens.
