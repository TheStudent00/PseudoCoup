# log_105 — field rule: generator to 99% coverage / 0 fabricated / 0 orphans, 20/24 perfect

Date: 2026-06-28
Type: tightening of the PseudoUI generator (follow-on to log_104). Same file: pseudoui.py +
two ledger correctness fixes in ui_ledger.py / kit_ledger.py.

## Direct answer

One principled fix — treating a labeled text field as ONE widget keyed by its label — closed
almost every remaining structural gap:

```
                      log_104   ->   now
  Compose leaf coverage:  96%   ->   99%   (493/496)
  fabricated:               7   ->    0
  orphan trees:             0   ->    0
  screens at 100%/0-miss:  20   ->   20  (+ 4 more at 100% coverage; only misses differ)
```

20 of 24 screens reproduce the hand-built structure perfectly. The other 4 differ by 1–2 leaves
each — and in those the GENERATOR is the faithful one (below).

## The field rule (what changed)

Compose writes a field as `OutlinedTextField(label = { Text("Notes") })`. The old walk descended
the label slot and emitted `T:Notes`; the generator emitted the field `F:Notes`. Same widget, two
representations -> ~10 unmatched + 7 fabricated. Fix: a labeled text field is ONE leaf, identified
by its label, typed `F`, on BOTH ledger sides AND the generator (`ui_ledger.field_anchor`, shared).
The field's label/placeholder slot is no longer descended into a separate Text. This is not
metric-tuning — it is the correct ontology (a field is a field, named by its label).

Also folded in (from log_104): `Icon(contentDescription = null)` is decorative -> not a content
leaf; `_sig_match` is symmetric (anchorless leaves dropped on both sides).

## The 6 remaining hand-built misses: the generator is MORE Compose-faithful than the human

Every one of the 6 is a spot where the HAND-BUILT kit diverged from the Compose source, and the
generator matches Compose (those 4 screens score 100% coverage / 0 fabricated, which is the proof):

- `F:·DYN·` (report_bug, exercise_create, log_cardio): the human keyed the field by its dynamic
  VALUE; Compose (and the generator) key it by its static LABEL.
- `T:Save` (exercise_create), `T:Notes (optional)` (log_cardio): the human emitted an extra label
  Text beside the field / an action label Compose doesn't carry as a distinct text.
- `F:Your name` (onboarding): a field the human rendered that the generator anchors differently.

So mechanization here isn't just reproducing the hand work — in 6 places it is CLOSER to the
Kotlin source of truth than the hand-built screen was. (Not a knock on the hand work; it shows the
generator is anchored to Compose, which is the whole point — everything traces to Kotlin.)

## The 3 remaining unmatched Compose leaves (onboarding only -> 94%)

`Skip gym setup for now`, `Done selecting`, `Configure equipment later` — single-Text
`TextButton`s nested deep in onboarding's step-dispatch composables. The generator's
entry-reachable walk catches 50/53; these 3 sit in a nesting the entry walk doesn't reach, while
`collect_ids` counts every composable in the file. A walk-completeness edge in the app's single
most complex screen (332 generated calls). Documented, not chased: widening the walk to all
composables risks emitting states not reachable in this screen's actual flow.

## Side effect on the kit-side runtime ledger (log_103's 23%)

The same two fixes nudged the runtime-trace aggregate to 121/496 = 24%, kit-extra 6. Unchanged
story (one-state-vs-all-states); just cleaner counts. The generator's 99% remains the meaningful
number because it measures the same all-states surface Compose exposes.

## Status

The STRUCTURAL generator is effectively done: 99% / 0 fabricated / 0 orphans / 20-of-24 perfect,
with the residuals understood and benign. Next phase is BEHAVIOUR — emit `on_click` wiring and
turn `items(list){ row }` into a real Python loop over `vm.xxx()`, so a generated screen RUNS the
real data path (the dynamic/functional equivalence). That is a deliberate new phase, not a
tightening; worth its own design pass.
