# log_106 — behaviour layer: generated IR, interpreted on real data, ≡ hand-built (gym_list)

Date: 2026-06-28
Type: milestone. The behaviour/dynamic layer of PseudoUI. New file: pseudoui_run.py.

## Direct answer

The generator now reproduces BEHAVIOUR, not just structure. For gym_list it lifts the Compose
control flow into an IR, runs that IR against the app's real seeded data, and produces a trace
identical to the hand-built screen's — every branch taken correctly, every dynamic value resolved:

```
gym_list runtime verify (IR interpreted vs hand-built, SAME seeded InMemoryDb):
  resolved dynamic values matching hand-built:  4/4
    'Home Gym'  ·  '🏠 Home Gym'  ·  '2 items'  ·  'Olympic Bar, Adjustable Dumbbe…'
  leaf agreement:    shared 7   interp-only 3   hb-only 3
  unresolved IR exprs: 0
```

The control flow resolved correctly off real data: it took the isActive=true branch (the "Active"
chip, NOT the "Set active" button), the gymType-non-null branch (rendered the type line), and the
equipment-isNotEmpty branch (the names, NOT "No equipment listed"). The 3 interp-only vs 3
hand-built-only are the SAME three affordances in two representations (below) — not a behaviour
difference.

## Glossary (new words)

IR (intermediate representation)
    The control-flow skeleton lifted from Compose: a tree of `box / leaf / foreach / if / let`.
    Generated MECHANICALLY (`pseudoui_run.build_ir`). Dump it with `--ir`.
    e.g. `FOREACH gymWithEquipment in gyms: ... IF activeGym?.id==... : <chip> ELSE: <button>`.

interpreter
    Walks the IR against real seeded data: loops the real rows, takes the branch the data selects,
    resolves each binding to its real value, emits a `define_*`-style leaf trace.

binding spec
    The per-screen dict that maps a Compose expression to a kit value (`"gym.name"` ->
    `item.name`; `"equipmentList.size"` -> `len(vm.equipment_for(id))`). This is the DECLARED
    part — see "the seam" — ~10 entries for gym_list, explicit and inspectable.

resolved value
    A dynamic binding evaluated against real data: `gym.name` -> `"Home Gym"`. Both the interpreter
    and the hand-built screen run on the SAME seed, so resolved values compare directly = the
    dynamic-equivalence check.

## The seam: what is mechanical vs declared (the important finding)

Reading the two view models side by side showed the kit DELIBERATELY RESHAPED Compose's data path:

| Compose                                   | kit                                          |
|-------------------------------------------|----------------------------------------------|
| `viewModel.gyms : List<GymWithEquipment>` | `vm.gyms() : List<GymProfileEntity>`         |
| `gymWithEquipment.equipment` (bundled)    | `vm.equipment_for(gym.id)` (separate query)  |
| `activeGym?.id == profile.id`             | `gym.isActive` (per-row flag)                |
| `setActive(gym)` / `delete(gym)`          | `set_active(gym.id)` / `delete(gym.id)`      |

These are documented human judgment calls (the kit VM's own docstring explains the isActive one).
So BEHAVIOUR is NOT purely mechanical from Compose: the CONTROL-FLOW skeleton (IR) is generated,
but the DATA PATH (binding spec) must be declared. The win is that the reshaping is now EXPLICIT
and inspectable in a ~10-line spec, instead of buried inside hand-written screen code. For a screen
that did NOT reshape (used the 1:1 transpiled domain), the spec would be near-trivial — which
points at the cleanest way to finish: feed generated UI from the TRANSPILED viewmodels so binding
is 1:1 and "everything traces to Kotlin" holds end to end.

## The 3 representation diffs (the only non-data divergence)

| interpreter (from Compose)        | hand-built (kit)   |
|-----------------------------------|--------------------|
| `Icon[Back]`                      | `T '←'`            |
| `Icon[Add gym]`                   | `T '+'`            |
| `T 'Active'` (AssistChip label)   | `T '✓ Active'`     |

Same three affordances; the kit renders icons as glyphs (its top_bar/fab/chip helpers). A 1:1
representation map (Compose icon contentDescription -> kit glyph) would fold these — a small,
enumerable refinement, not a behaviour gap.

## How it works

`build_ir` walks the Compose entry composable's STATEMENTS (not just its widgets), recognising
`items(src){ var -> body }` -> foreach, `if/else` -> if, `expr?.let{ var -> body }` -> let, and
inlining the project's @Composable BODIES (WflCard/GymListItem/LabeledStat) with params bound —
so the control flow inside them is lifted too. `interpret` runs the IR with the binding spec over
`AppMain._seed()`'s InMemoryDb; the result is compared leaf-for-leaf against `kit_ledger.trace` of
the hand-built screen (also on the seed). Truncation is normalised to the ledgers' 30-char anchor
so resolved values compare fairly.

## Status

The behaviour layer is proven on one screen end to end: mechanical structure + mechanical control
flow + a small declared binding spec -> a runtime trace equivalent to the hand-built screen, with
only the known icon-glyph representation diffs. Next: (1) the icon->glyph representation map to
zero out those 3; (2) more binding specs (or, better, point screens at the transpiled viewmodels
to make specs 1:1); (3) emit the IR+spec as an actual runnable `*_screen.py` (today it interprets;
emitting source is the last mile to REPLACING a hand-built screen).
