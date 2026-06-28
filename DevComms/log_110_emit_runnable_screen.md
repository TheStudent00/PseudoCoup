# log_110 — the last mile: PseudoUI EMITS a runnable *_screen.py (generative, not just verifying)

Date: 2026-06-28
Type: milestone. pseudoui_run.py `--emit`. The crank now PRODUCES code.

## Direct answer

The generator now emits an actual runnable screen file from the IR + transpiler bindings, and the
emitted file RUNS and reproduces the hand-built screen's content exactly:

```
gym_list --emit:  wrote gym_list_screen.gen.py (76 lines), ran -> 30 define_* calls
  SHARED with hand-built (7): '2 items' · 'Delete gym' · 'Equipment' · 'Gym profiles'
                              · 'Home Gym' · 'Olympic Bar, Adjustable Dumbbe…' · '🏠 Home Gym'
  GEN-only (1): 'Active'        (Compose chip label)
  HB-only  (3): '+' · '←' · '✓ Active'   (kit glyphs)
```

All 7 content leaves match — including every dynamic value (Home Gym, 2 items, the equipment
names, the gym-type line). The only differences are the 3 icon-glyph representations (FAB `+`,
back `←`, chip `✓`) vs Compose's icon descriptions — the same known representation gap, not a
generation error.

## What it emits (a real, readable build())

`emit_py` walks the IR and writes Python: the screen's actual loop and conditionals, with each
binding the transpiler's Kt→Py output. Verbatim excerpt of the GENERATED file:

```python
def build(ui, content, viewModel):
    gyms = viewModel.gyms.collectAsStateWithLifecycle()
    ...
    else:
        ui.define_box(_id3, _id0, "V")
        for _i4, gymWithEquipment in enumerate(gyms):
            ui.define_box(_id5, _id3, "V")
            gym = gymWithEquipment.profile
            equipmentList = gymWithEquipment.equipment
            ...
            ui.define_text(("gym_list_z11_" + str(_i4)), _id10, gym.name)
            if _ev(lambda: (activeGym.id if activeGym is not None else None) == gymWithEquipment.profile.id):
                ui.define_text(..., 'Active')
            else:
                ui.define_button(..., 'Set active')
            type = gym.gymType
            if type is not None:
                ui.define_text(..., f"{type.emoji} {type.displayName}")
            ...
            if _ev(lambda: (len(equipmentList) != 0)):
                equipmentNames = equipmentList.joinToString(", ", (lambda it=None: it.name))
                ui.define_text(..., equipmentNames)
            else:
                ui.define_text(..., 'No equipment listed')
```

This is the real screen — the loop over real rows, the isActive branch, the gymType `?.let`, the
equipment fallback — none of it hand-written. The bindings are the transpiler's output; the
control flow is the lifted IR; the zone ids are minted (loop-indexed for uniqueness).

## Three codegen rules that made it run

- **Dead-bind pruning**: a `val` is emitted only if its name is referenced downstream, so WflCard's
  styling binds (`shape = RoundedCornerShape(...)`, which reference Compose theme symbols) are
  dropped — they were never rendered.
- **Robust conditions**: `if _ev(lambda: <cond>):` — a condition that references an unbound
  composable param (WflCard's `onClick != null`) evaluates to falsy and takes the else, mirroring
  the interpreter's best-effort. Both its branches are empty styling boxes, so output is unchanged.
- **Skip no-content leaves**: a decorative `Icon(contentDescription = null)` is skipped (the
  interpreter does the same), instead of emitting a broken `None` content.

## Honest scope

The emitted screen runs against the TRANSPILED viewModel + the fixed reactive/DAO/stdlib shims
(the 1:1 stack). So it is runnable and verified HERE; dropping it into the live app as a
replacement needs the app to consume the transpiled viewmodels (the path-(c) migration), which is
a separate, deliberate step. What this proves: the pipeline is now end-to-end GENERATIVE — Compose
in, a runnable kit screen out, whose content matches the hand build with only representation diffs.

## The chain, now complete (gym_list)

structure (pseudoui) → control-flow IR (build_ir) → transpiled viewModel (KtToPy) → transpiler-
emitted bindings (--auto) → **emitted runnable *_screen.py (--emit)**. Every layer mechanical from
Kotlin. Next: the icon→glyph representation map (closes the last 3-leaf gap); generalise emit to a
2nd screen; and the path-(c) app migration to make a generated screen drop in.
