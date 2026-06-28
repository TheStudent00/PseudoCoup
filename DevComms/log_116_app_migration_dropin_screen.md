# log_116 — app migration (path c): a generated Screen class drops into the app contract

Date: 2026-06-28
Type: milestone. The first slice of the live-app migration. pseudoui_run.py `--app`.

## Direct answer

The generator now emits a screen as a real APP Screen class — `__init__(self, db)` +
`build(self, ui, content_zone_id, router)`, exactly what `AppRouter` instantiates and mounts —
backed by the TRANSPILED viewmodel. Mounted the way the router mounts it, it produces the
IDENTICAL tree to the hand-built screen:

```
gym_list --app:  GymListScreenGen(db).build(ui, "content", router)  (the router's own contract)
  -> 30 define_* calls;  vs hand-built leaf shared 10, gen-only 0, hb-only 0   (COMPLETE match)
```

So a generated screen is a drop-in for the hand-built one at the app's Screen contract: same ctor,
same build signature, same router, same seeded db, same tree.

## The generated app Screen (verbatim head)

```python
class GymListScreenGen:
    def __init__(self, db):
        self.db = db
        self.vm = build_transpiled_vm('gym_list', db)   # the 1:1 backend (KtToPy VM + adapter + shim)

    def build(self, ui, content_zone_id, router):
        viewModel = self.vm
        content = content_zone_id
        gyms = _ev(lambda: viewModel.gyms.collectAsStateWithLifecycle())
        ...
        for _i5, gymWithEquipment in enumerate(gyms or []):
            gym = _ev(lambda: gymWithEquipment.profile)
            ui.define_text(("gym_list_z13_" + str(_i5)), _id12, _ev(lambda: gym.name))
            ...
```

`build_transpiled_vm(key, db)` is the "1:1 backend": it loads the transpiled GymListViewModel +
entities + GymType, wired to the kit InMemoryDb through the screen's adapter and the fixed reactive/
stdlib shim. The screen, the viewmodel, the entities, and every binding all derive from the same
Kotlin source.

## Two fixes this needed

- The generated root box attached to a hardcoded `"content"`; now it uses the `content`/
  `content_zone_id` the app passes (so it nests under the router's real content zone).
- Python-keyword variable names: a Kotlin loop var `def` was emitted raw (`for _i, def in …` — a
  SyntaxError) while the transpiled body used `def_`. The IR's foreach/let vars and val-bind names
  now pass through the transpiler's `_safe` (keyword -> trailing `_`), matching the bindings. (Fixed
  paths' emit too: 148-line build(), runs, 3/3.)

## Honest scope — what's proven, what remains

PROVEN: a generated screen + the transpiled viewmodel are contract-compatible and tree-identical to
the hand build, mounted exactly as the live router mounts screens.

REMAINING for the screen to run in the SHIPPING app unaided:
1. Vendor the 1:1 backend into the app — today `build_transpiled_vm` transpiles at runtime via
   tools/; the app would import a pre-generated `*_view_model.py` (committed) + a small reactive
   shim + kotlin_rt, so it needs no transpiler at runtime.
2. Register `GymListScreenGen` in `AppRouter` in place of `GymListScreen`.
3. Run the actual Kivy/Flutter goldens against it (the final pixel check).

None of those are transpiler or generator gaps — they're packaging + a one-line router swap +
a golden run. The hard part (a generated, Kotlin-derived screen that reproduces the hand build at
the app's own contract) is done.
