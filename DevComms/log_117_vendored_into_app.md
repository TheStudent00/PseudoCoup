# log_117 — vendored: the generated gym_list runs IN THE APP, drop-in match (no transpiler at runtime)

Date: 2026-06-28
Type: milestone. The app-migration vendoring slice. Touches WFL_PseudoCoup (additive only).

## Direct answer

The generated gym_list screen + its 1:1 backend are now VENDORED into WFL_PseudoCoup/src as committed
.py (no transpiler at app runtime), and they run in the app's own environment and reproduce the
hand-built screen exactly:

```
python tools/test_gym_list_gen.py   (boots AppMain on a seeded InMemoryDb, app's own kit)
  GENERATED gym_list built in-app: 30 define_* calls
  hand-built leaves 10 · generated leaves 10 · shared 10 · gen-only [] · hb-only []
  RESULT: MATCH -- generated screen is a drop-in

python tools/smoke_screens.py  ->  SMOKE: 30/30 screens built   (no regression; purely additive)
```

## What was vendored (WFL_PseudoCoup/src, all NEW files)

- `generated/kotlin_rt.py` — the Kotlin stdlib runtime (KtList.joinToString etc.), copied (stdlib-
  only deps).
- `generated/reactive_shim.py` — Kotlin Flow/StateFlow/coroutines -> PseudoCoup's synchronous pull
  (stateIn/collectAsState/launch/combine). The FIXED boundary, not per-screen.
- `generated/gym_list_kt.py` — the TRANSPILED (KtToPy) GymType + GymProfileEntity/GymWithEquipment +
  GymListViewModel (1:1 with Kotlin), with shim/kotlin_rt imports.
- `generated/gym_list_backend.py` — the Room-DAO -> InMemoryDb adapter (getAllWithEquipment/getActive
  over the kit's repos) + the int->enum lift + `make_vm(db)`.
- `ui/gym_list_screen_gen.py` — the GENERATED screen: a real app Screen class (`__init__(self, db)` +
  `build(self, ui, content_zone_id, router)`), `self.vm = make_vm(db)`, body = the emitted build.
- `tools/test_gym_list_gen.py` — the in-app comparison (above).

The vendoring is reproducible: PseudoCoup/tools/pseudokotlin/vendor_gym_list.py regenerates all of it
(transpiles the .kt, writes the shim/adapter, emits the screen).

## Why it matters

This closes the loop the project set out to prove: a screen whose STRUCTURE + CONTROL FLOW come from
Compose, whose VIEWMODEL + ENTITIES + ENUM are the transpiled Kotlin, and whose BINDINGS are
transpiler-emitted — running inside the real app, on the real seeded data, through the real kit,
producing the SAME tree the hand build produces. Everything traces to Kotlin, end to end, in the app.

## Honest scope — what's done, what remains

DONE: the generated screen is a verified drop-in at the app's Screen contract, in the app's runtime,
with the 1:1 backend vendored (no transpiler needed at runtime). Additive — the existing 30 screens
and their smoke pass unchanged.

REMAINING:
1. Swap the `AppRouter` registration `self.gym_list = GymListScreen(db)` ->
   `GymListScreenGen(db)` to make the app actually USE it (one line; reversible).
2. The FLUTTER pixel goldens: the app renders via a Python->Dart transpiler (tools/transpile.py).
   The generated screen's runtime (`_ev` lambdas, kotlin_rt, the transpiled VM) is not yet Dart-
   transpilable -- so passing the Flutter goldens needs either that runtime ported to Dart, or the
   screen emitted in a Dart-friendly form. The Python-side (smoke + this tree-match) is the gate it
   passes today. This is the next real frontier, and it is below the generator -- a second
   transpiler (Py->Dart) concern, not a PseudoUI gap.
