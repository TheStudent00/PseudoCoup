# log_103 — app-seeded compare across all screens: the kit is a faithful SUBSET

Date: 2026-06-28
Type: measurement + calibration. Replaces per-screen seeders with the app's own seed and a
metric robust to instance counts, to get a real cross-screen number.

## Universal seeder

Instead of hand-writing per-screen seeders, the trace now runs the app's OWN `AppMain._seed()`
once on a fresh `InMemoryDb` -> the real faithful state (185 exercises, 3 programs, 4 paths,
gym, sessions, full program hierarchy). Every screen is then traced with the real VM over real
data. Headless via a `kit` stub + a one-symbol `pseudodart.discipline.dart_extern` stub (the
engines import a no-op discipline decorator). One call seeds all 24 screens.

## Instance-count-robust metric

Full data makes a list screen render every row (185 exercises), so an ordered/positional metric
over-penalizes. The compare now matches the SETS of distinct leaf SIGNATURES: a static leaf ->
(type, content); a dynamic binding -> (type, DYN); kit content that isn't a Compose static
literal is treated as DYN. Instance counts no longer matter.

## Result (24 app-seeded screens)

```
distinct widget signatures matched: 119/508 = 23%
kit signatures NOT in Compose:      8   (total, across all 24 screens)
best: debug_panel 86% · log_cardio 58% · exercise_create 57%
low:  workout_execution 3% · exercise_detail 4% · program_day_editor 5%
```

## What it actually says

- **The kit fabricates ~nothing: kit-extra = 8 total across 24 screens.** Whatever it renders
  is a faithful subset of the Compose design (the 8 are glyphs `←`/`+` and a couple of helper
  extras). This is the strongest faithfulness signal and it is now aggregate-wide.
- **The 23% is COVERAGE, not fidelity.** Compose is parsed statically -> every distinct string
  across every state / dialog / branch counts (onboarding 54, workout_execution 66). The kit
  trace is ONE runtime state. So a screen whose one state ≈ its whole surface scores high
  (debug_panel 86%), and a multi-state screen scores low (workout_execution 3%) — that's the
  one-state-vs-all-states asymmetry, not 97% missing wrappers.

So the honest verdict, now with real data across the app: **the hand-built kit is a faithful
subset of Compose — it adds nothing, and covers a portion of Compose's full state-space in any
single trace.** There IS substantial UI surface not yet covered (other states + thinner
screens), but the foundation is faithful, not a mess.

## Where this leaves the measurement

The UI ledger now has: both sides, real-data tracing, instance-robust metric, and a stable
verdict (faithful subset, kit-extra≈0). Pushing the coverage % higher needs same-STATE
comparison (evaluate the Compose side with the same data / drive the kit through each state) —
a big lift for diminishing calibration value. The measurement has reached a useful plateau.

The higher-value next move is the GENERATOR (PseudoUI): the slice + these traces have the
Compose-tree -> kit-define_* mapping; encoding it lets us GENERATE kit screens and verify each
with this same ledger. That turns "the kit covers 23% of Compose" into a crank that raises
coverage mechanically.
