# log_107 — path (c): UI binds to the TRANSPILED viewmodel; binding collapses to Kt→Py

Date: 2026-06-28
Type: milestone — the completion path. The UI now provably traces to Kotlin end to end.
pseudoui_run.py `--1to1`.

## Direct answer

When the generated screen binds to the TRANSPILED (1:1-with-Kotlin) viewmodel + entities instead of
a hand-reshaped kit VM, the per-screen "binding spec" stops being judgment and becomes the Kotlin
expressions themselves (mechanical Kt→Py). Proven on gym_list, end to end, on real seeded data:

```
gym_list, IR interpreted against the TRANSPILED GymListViewModel:
  resolved dynamic values matching hand-built:  4/4
    'Home Gym'  ·  '🏠 Home Gym'  ·  '2 items'  ·  'Olympic Bar, Adjustable Dumbbe…'
  unresolved IR exprs: 0
```

Same 4/4 as the reshaped-spec run (log_106) — but now nothing was reshaped by hand.

## What is now mechanical (every layer traces to Kotlin)

1. STRUCTURE — Compose tree → kit define_* (pseudoui.py, 99%).
2. CONTROL FLOW — Compose `items/if/?.let` → IR (pseudoui_run.build_ir).
3. THE VIEWMODEL — `KtToPy().transpile(GymListViewModel.kt)` gives a structurally 1:1 Python VM
   (`vm.gyms`, `vm.activeGym`, `setActive(gym)`, `delete(gym)`); GymProfileEntity, GymWithEquipment
   (`profile`+`equipment`), and the GymType enum (`.emoji`/`.displayName`) all transpile clean.
4. THE BINDINGS — fed to the transpiler, the screen's Kotlin expressions come back as Python with
   IDENTICAL accessor chains (this is the crux; verbatim transpiler output):

   ```
   "${type.emoji} ${type.displayName}"        -> f"{type.emoji} {type.displayName}"
   activeGym?.id == gymWithEquipment.profile.id -> (activeGym.id if activeGym is not None else None) == gymWithEquipment.profile.id
   equipmentList.size                          -> len(equipmentList)
   gyms.isEmpty()                              -> (len(gyms) == 0)
   equipment.joinToString(", "){ it.name }     -> equipment.joinToString(", ", (lambda it=None: it.name))
   ```

   The accessor SHAPES (`gymWithEquipment.equipment`, `type.emoji`, `…profile.id`) are identity with
   Kotlin. That is the whole point of (c): with a 1:1 VM there is no reshaping to declare.

## The collapse, concretely

| binding              | reshaped spec (kit VM)            | 1:1 spec (transpiled VM)                  |
|----------------------|-----------------------------------|-------------------------------------------|
| active?              | `item.isActive` (invented flag)   | `activeGym.value.id == gw.profile.id`     |
| equipment            | `vm.equipment_for(id)` (2nd query)| `gymWithEquipment.equipment` (identity)   |
| gym type label       | `gym_type_emoji(int)+…` (helpers) | `type.emoji + " " + type.displayName`     |

The kit VM forced 10 reshaping decisions; the transpiled VM needs none — the bindings ARE the
Kotlin, syntactically converted.

## The only non-1:1 seams (FIXED, not per-screen)

- Reactive shim (~8 lines): `Flow/stateIn/viewModelScope.launch/SharingStarted` → synchronous pull.
  This is the reactive↔sync gap that made PseudoCoup pull-based in the first place; it is one fixed
  rule, not a per-screen choice.
- Room DAO → InMemoryDb adapter: `getAllWithEquipment()` bundles profile+equipment and lifts the
  stored `gymType` int → the `GymType` enum (the storage boundary the kit had reshaped away).
- Kotlin stdlib helpers (`joinToString`) need a runtime shim — fixed, library-level, once.

## Honest scope

Proven on gym_list only. In this harness the 1:1 binding lambdas are hand-written, but each is
exactly what the transpiler emits for the corresponding Kotlin expression (shown above) — so the
remaining engineering is to EMIT the binding glue from the transpiler instead of hand-writing it,
plus the small stdlib-helper shims. The architecture is proven; the auto-emission is the build-out.

## Why this matters for finishing the project

This is the "everything traces to Kotlin" invariant reaching the UI. The path to completion is now
clear and mechanical: generate structure + control-flow IR from Compose, bind to the TRANSPILED
viewmodels (Kt→Py, 1:1), supply the fixed reactive/DAO/stdlib shims once. Drift can't creep in,
because nothing is re-decided per screen — the screen, its viewmodel, and its data all derive from
the same Kotlin source.
