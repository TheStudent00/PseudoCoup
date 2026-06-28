# log_112 — dynamic 2nd screen: exercise_detail resolves real data; the scaling blockers surface

Date: 2026-06-28
Type: generality test (dynamic data) + findings. Continues the sequence after log_111.

## Direct answer

The crank's dynamic resolution generalises to a second screen with REAL data. `exercise_detail`,
run through `--auto` against the transpiled viewModel + the seeded "Back Squat" exercise:

```
exercise_detail (AUTO): leaf shared 7, interp-only 4, hb-only 3; dynamic 3/4 match; unresolved 7
  resolved (verified against the seeded eSquat):
    'Back Squat' (name)  ·  'Compound' (isCompound)  ·  'Bilateral' (isUnilateral)  ·  'Never program this' (isExcluded)
```

All four dynamic values resolved correctly off the real exercise; three also appear in the
hand-built's single-state trace (the 4th, "Never program this", sits in a dropdown the hand-built
trace has closed — the one-state-vs-all-states asymmetry, not a miss). gym_list (10/10) and paths
(3/3) unchanged.

## What it took for screen #2 (per-screen surface)

- a `SCREEN_CFG` entry (3 lines) + a ~10-line adapter (`repository.getById → Flow(kit exercise)`,
  a `savedStateHandle` returning the id);
- `sel: "eSquat"` so the HAND-BUILT trace loads the SAME exercise. exercise_detail reads its id
  from `router.selected_id`, which `KL.trace` left as a mock → the hand-built rendered
  "Exercise not found". `KL.trace` now accepts a router; the baseline is fair.

The IR machinery again needed nothing screen-specific. Fixed infra grew once: a `combine` shim,
`.forEach { x -> }` lifting, and `Screen`/`checkNotNull` stubs — all reused henceforth.

## The scaling blockers, now concrete (the real value of this test)

1. **Enum lift (recurring).** `"${movementPattern.displayName()} · ${equipmentType.displayName()}"`
   is hb-only ('Squat · Barbell'): the kit stores these enums as INTS, so `displayName()` fails. Same
   class as gym_list's gymType int→GymType lift — but gym_list's adapter lifted ONE field by hand.
   The general fix is an automatic int→transpiled-enum lift driven by the Kotlin entity's field
   types; that would clear this line and most other screens' enum content at once.

2. **Transpiler precedence bug.** `!exercise.cues.isNullOrBlank()` transpiles to
   `(not exercise.cues).isNullOrBlank()` — the `not` binds to the receiver instead of the call.
   Wrong; it makes the instructions/cues/video conditions unresolved. A transpiler fix
   (unary-`!` precedence over a trailing call), not a UI issue.

3. **Multi-statement combine lambda.** exercise_picker's VM didn't construct: the transpiler emits
   `combine(…, _lam1)` but never defines `_lam1` (the transform is a multi-statement lambda Python
   can't inline). `verify_auto` now reports this as "VM did not construct — transpiler gap, not UI".

## Reading

The UI side scales cleanly — the IR + auto-bindings + emit are screen-agnostic; per-screen cost is
a tiny adapter. What gates broader coverage is the LAYER BELOW: the transpiler (multi-statement
lambdas, `!`-precedence) and the data-shape lifts (int→enum) the kit reshaped. Those are the honest
next targets — and they pay off across many screens at once, not one at a time. The dynamic crank
itself is proven on two shapes now: a list (gym_list, 4/4 end-to-end) and a detail (exercise_detail,
real values resolved).
