# log_100 — UI cross-side compare at scale: the real number (it is NOT 95–99% done)

Date: 2026-06-28
Type: measurement + calibration. Pushes the kit<->Compose compare (log_99) to full resolution
and runs it across every both-sides screen, to replace a spot-check with an aggregate.

## Why this log exists

After log_99 I said the kit wrappers are "filled, not empty," and the owner reasonably asked:
"are we 95–99% done?" Answer, measured: **no, not close.** This records the real number and,
just as important, why the number is a *lower bound* and what it can and can't claim.

## The full-resolution push (all done)

- **inline custom composables + resolve params** (Compose side): `LabeledField(label="X")` ->
  `FieldLabel(label)` -> `Text(label)` now all resolve to `"X"` (chained substitution through a
  cross-file composable-definition index).
- **slot APIs**: `_children` descends named-arg lambdas (`Scaffold(topBar=…)`, `TopAppBar(title=…)`).
- **dynamic structure + mock robustness** (kit side): the mock yields list items and survives
  numeric coercion / arithmetic / comparison, so all 24 traces now COMPLETE (0 partial crashes,
  was 5).

Each fix raised matches (report_bug 4 -> 7). Then `kit_ledger.py --all`.

## The aggregate (24 paired screens)

```
matched anchors:   107
Compose-only:      760
kit-only:          136
anchor match rate: 107/867 = 12%   (lower bound)
```

Spread is enormous:
```
debug_panel       30/41  = 73%      workout_execution  1/120 = 0%
exercise_create   13/26  = 50%      onboarding         1/92  = 1%
log_cardio        10/23  = 43%      program_day_editor 0/27  = 0%
report_bug         7/22  = 31%      progress           2/63  = 3%
```

## What the number means — and what it CAN'T claim

The 12% is a **severe lower bound** from a *fundamental measurement asymmetry*, not a fidelity
verdict:
- the **Compose side is parsed statically** -> it lists EVERY node, every conditional/dialog
  state, every branch (WorkoutExecutionScreen: 120 anchors).
- the **kit side is traced at runtime** -> ONE render path, with EMPTY mock data (no real rows).

So dynamic-heavy screens look terrible (workout_execution 8 kit nodes vs 120 Compose anchors)
purely from static-all-states vs runtime-one-empty-path — NOT proof the kit is 7% built. Where a
screen is mostly static (debug_panel), the comparison is meaningful and shows **73%** content-
anchor fidelity. And all of this is **content-anchor only** — visible strings, not structure /
size / position / behaviour.

A TRUE faithfulness number needs **real seed data** (so dynamic rows render) and **render-path
alignment** (compare the same state on both sides). That's a bigger, Track-A-coupled effort.

## Bottom line (the calibration the owner asked for)

- **Not 95–99%.** Measured aggregate content-anchor match is ~12% (lower bound); the cleanest
  static screen is ~73%; many screens can't be judged yet because the measurement is asymmetric.
- The hand-built kit (Track A) is **faithful where statically comparable**, filled not empty —
  but "faithful on the screens I can compare cleanly" is NOT "the UI is done."
- And regardless: the **transpiler still produces ~0% of the UI** — these kit screens are
  hand-built. The ledger/compare is a measuring instrument, not a generator.

Honest status: the engine/logic layer is proven (oracle+fuzz); the UI has a working two-sided
ledger that now MEASURES correspondence, and that measurement says there is substantial UI work
left — both to build/transpile and to verify with real data.

## CLARIFICATION (owner, after the run)

Two things the owner corrected, which reframe this log:
1. The "95–99%?" question was about **Kt→Py specifically**, not the whole project or the UI. At
   that scope the intuition is basically RIGHT: **non-UI Kt→Py is ~97% compile-clean (162/167)**;
   the gaps are the last ~5 non-UI files, the unverified middle (only 11 classes proven), and the
   UI layer (34% clean) as a separate bucket. This log measured the UI track, a different thing.
2. This UI ledger ended up **verifying hand-built UI** (the Track-A kit), because the UI doesn't
   transpile — so there is no transpiler UI output to measure. That was not the original intent
   for the ledger (which was built to check transpiler Kt→Py OUTPUT, as the engine ledger does).
   Flagged as a redirect point: measuring hand-built Track-A UI may not be where effort belongs.
