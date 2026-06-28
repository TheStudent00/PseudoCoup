# log_120 — reactive/pull bridge bug: the transpiled VM's flow must RE-QUERY, not snapshot

Date: 2026-06-28
Type: bug fix (imperative/reactive seam). Found while auditing for paradigm complexities.

## Direct answer

The generated gym_list looked like a complete interactive drop-in, but it had a real reactive/pull
bug: after a mutation it rendered STALE data. Now fixed and guarded.

```
BEFORE:  build 1 shows "Home Gym"  ->  delete (db gyms 1->0)  ->  rebuild STILL shows "Home Gym"  (stale)
AFTER:   build 1 shows "Home Gym"  ->  delete (db gyms 1->0)  ->  rebuild shows the empty state     (correct)
```

The handler test had checked the db changed but never that the screen RE-RENDERS -- so it slipped
through. `tools/test_gym_list_gen.py` now asserts the rebuild reflects the delete (a permanent guard).

## Root cause -- the bridge was done halfway

- Kotlin: `repo.getAllWithEquipment()` is a Room `Flow` that RE-EMITS on every db change ->
  `vm.gyms.value` is always current.
- PseudoCoup: the hand-built VM's `gyms()` is a METHOD, re-queried every `build()` -> always current.
- My reactive shim: `stateIn` captured the list ONCE at VM construction. A frozen snapshot. Every
  rebuild re-read the dead snapshot.

Both source and target read FRESH; only the bridge didn't.

## Fix -- a lazy shim (the correct reactive -> pull mapping)

A `Flow` now wraps a value OR a THUNK; `.value` / `.collectAsState()` call the thunk fresh, and
`stateIn` returns the SAME lazy flow (not a snapshot). The adapter wraps its query bodies in thunks:

```python
def getAllWithEquipment(self):
    def q(): return KtList(GymWithEquipment(_lift(g), KtList(eq.get_by_gym(g.id)))
                           for g in GymService(self.db).get_all())
    return Flow(q)          # re-queried on every read
```

So each `build()` re-reads the db -- matching Kotlin's re-emit and PseudoCoup's re-query at once.
Applied in BOTH the tools shim (`pseudoui_run._reactive_ns` / `_gym_repo_adapter`, for --auto/--app)
and the vendored shim (`vendor_gym_list.py` -> WFL_PseudoCoup `generated/`). No regression: in-app
5/5 (match + 4 handlers + re-render), smoke 30/30, --auto/--app/--1to1 unchanged.

## The OTHER reactive complexity (still latent -- for the breadth play)

The transpiled VM's `MutableStateFlow` UI-FLAGS (a dialog-open, a search query) map to a plain holder
in the shim, NOT PseudoCoup's recompose-observed `State` -- so setting one wouldn't repaint. gym_list
has only DERIVED flows so it's clean; `exercise_detail` (`excludePrompt`) and `exercise_picker`
(`query`/`filter`) will hit it. Fix when generalising: map `MutableStateFlow` -> PseudoCoup `State`.

## Status

gym_list is now genuinely a complete interactive drop-in: renders 10/10, 4/4 handlers fire, AND the
re-render reflects mutations -- routed by the real AppRouter, smoke 30/30. The reactive/pull bridge is
correct for derived flows; the MutableStateFlow-as-State mapping is the remaining reactive item.
