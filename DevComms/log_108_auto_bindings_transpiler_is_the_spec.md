# log_108 — the crank: bindings emitted by the TRANSPILER (no hand-written spec)

Date: 2026-06-28
Type: milestone. The "natural next step" after log_107: auto-emit the binding glue. pseudoui_run.py
`--auto`.

## Direct answer

The per-screen binding spec is gone. Each binding expression in the screen's IR (a `val` RHS, an
`if` condition, a `foreach` source, a `?.let` subject, a dynamic leaf) is now transpiled Kt→Py by
the SAME pseudokotlin transpiler and eval'd against `kotlin_rt` (the stdlib runtime) + the
transpiled viewModel. No hand lambdas. gym_list, on real seeded data:

```
gym_list --auto  (bindings = transpiler output, NO hand spec):
  resolved dynamic values matching hand-built:  4/4
    'Home Gym'  ·  '🏠 Home Gym'  ·  '2 items'  ·  'Olympic Bar, Adjustable Dumbbe…'
  unresolved IR exprs: 1   (WflCard's internal `onClick != null` — both branches empty; no effect)
```

Same 4/4 as the hand-spec runs (log_106/107), now with nothing written per screen.

## What "auto" means concretely

Captured the screen's `val` declarations into the IR as `bind` nodes (e.g.
`val gym = gymWithEquipment.profile`, `val gyms by viewModel.gyms.collectAsStateWithLifecycle()`),
and made the interpreter take a generic `resolve(expr, env)` strategy. The `--auto` strategy is the
transpiler. Verbatim emitted bindings (from the run's report):

```
activeGym?.id == gymWithEquipment.profile.id
   -> (activeGym.id if activeGym is not None else None) == gymWithEquipment.profile.id
equipmentList.isNotEmpty()        -> (len(equipmentList) != 0)
equipmentList.joinToString(", ") { it.name }  -> equipmentList.joinToString(", ", (lambda it=None: it.name))
"${type.emoji} ${type.displayName}"           -> f"{type.emoji} {type.displayName}"
```

`.joinToString` resolves because the equipment lists are wrapped as `kotlin_rt.KtList`; `.size`/
`.isEmpty/.isNotEmpty` are converted to Python by the transpiler. The `by … collectAsState()`
delegate (which the transpiler rejects at statement scope) is handled by lifting its RHS and giving
the reactive `_StateFlow` a `collectAsStateWithLifecycle() -> .value` shim.

## The three strategies now in pseudoui_run.py

| mode      | binding source                          | hand-written per screen | gym_list   |
|-----------|-----------------------------------------|-------------------------|------------|
| (default) | reshaped spec (Compose→kit lambdas)     | ~10 lambdas             | 4/4, unres 0 |
| `--1to1`  | transpiled VM + Kotlin-shaped lambdas   | ~10 (but identity)      | 4/4, unres 0 |
| `--auto`  | the TRANSPILER itself                   | **0**                   | 4/4, unres 1 |

Down the table, more of the screen derives mechanically from Kotlin. `--auto` is the crank: every
layer — structure (pseudoui), control flow (IR), the viewmodel (KtToPy), and now the bindings
(KtToPy) — comes from the same Kotlin source. Drift has nowhere to enter.

## The one unresolved (honest)

`onClick != null` — a condition INSIDE WflCard checking whether a click handler was passed.
`onClick` is a composable parameter (a handler lambda), not data, so it isn't in the eval env; the
interpreter takes the `else` branch. Both branches are empty styling `Card` boxes (no leaves), so
the rendered trace is identical either way. Resolving it cleanly = binding composable params into
the env when inlining (a small follow-up); it changes nothing here.

## Fixed seams that remain (once, not per-screen)

- reactive shim: `Flow/stateIn/viewModelScope.launch/collectAsState` → synchronous pull.
- Room DAO → InMemoryDb adapter (`getAllWithEquipment` bundling; gymType int → GymType enum).
- `kotlin_rt` is the stdlib runtime (already exists; used by the oracle) — `KtList.joinToString` etc.

## Status / next

The crank works on gym_list with zero hand-written binding. Remaining build-out: (1) bind composable
params into the env to clear the `onClick`-style residue; (2) run a SECOND screen through `--auto`
to see how the fixed shims generalise (the per-screen surface should be ~0); (3) emit the IR+auto
bindings as a runnable `*_screen.py` — the last mile to a generated screen that REPLACES a hand
build. Each is incremental; the architecture (everything traces to Kotlin) is proven.
