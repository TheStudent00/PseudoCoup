# log_111 — --emit generalises (2nd screen) + representation map -> gym_list is a COMPLETE match

Date: 2026-06-28
Type: milestone. Two sequential steps: emit generality, then faithfulness (icon→glyph).

## Direct answer

`--emit` now works on a second screen, and gym_list is now a 100% leaf match of the hand-built
screen — generated as runnable code, with nothing diverging:

```
gym_list --emit:  30 define_* calls; leaf shared 10, gen-only 0, hb-only 0   (COMPLETE match)
gym_list --auto:  leaf shared 10, interp-only 0, hb-only 0; dynamic 4/4
paths    --emit:   9 define_* calls; leaf shared  3, gen-only 0, hb-only 0   (COMPLETE match)
```

Both generated screens reproduce the hand-built kit EXACTLY. Both `*_screen.gen.py` files parse and
run.

## Step 1 — emit generalises (robust value emission)

paths crashed on emit: a Kotlin `val subtitle = if (…) "a" else "b"` transpiles to a MULTI-LINE
Python if/else statement, but the emitter assumed every binding was a one-line expression and spliced
the halves into invalid syntax. Fixed with a uniform value layer:

- `_py_expr` returns a single-line RHS, or None if the transpile is multi-line (a Kotlin if/when
  value); those go through `_py_stmt`, which emits the transpiled block (assigning the target).
- Single-line values are wrapped `_ev(lambda: <expr>)` so an unbound composable param (WflCard's
  `onClick`, paths' `PathDefinition`) yields None and the branch/leaf is skipped — exactly the
  interpreter's best-effort. Multi-line values reference bound locals, so they need no guard.

With that, paths emits a 98-line build() that runs and reproduces its empty/discovery state (3/3).
The emitter is no longer gym_list-specific.

## Step 2 — representation map (faithfulness): the last 3 leaves

The only gym_list diffs were 3 affordances the kit draws as glyphs (its top_bar/fab/chip helpers):
Compose `Icon(Back)`→`←`, `Icon(Add)`→`+`, and an `AssistChip(Check + "Active")`→`✓ Active`. A
small representation pass on the IR (shared by --auto and --emit) encodes that kit convention:

- icon contentDescription in `{Back→←, Add→+, Close/Cancel→✕}` → a text-glyph leaf;
- an `AssistChip` with a leading icon → fold a `✓ ` into its label.

This is the kit backend's icon representation (the same way its Kivy/Flutter backends draw an
abstraction differently), applied so the generated trace matches — and so a generated screen could
REPLACE the hand build. After it: gym_list 10 shared / 0 / 0.

## The generated file (verbatim, the real artifact)

```python
def build(ui, content, viewModel):
    gyms = _ev(lambda: viewModel.gyms.collectAsStateWithLifecycle())
    ...
    for _i5, gymWithEquipment in enumerate(gyms or []):
        gym = _ev(lambda: gymWithEquipment.profile)
        equipmentList = _ev(lambda: gymWithEquipment.equipment)
        ...
        ui.define_text(("gym_list_z13_" + str(_i5)), _id12, _ev(lambda: gym.name))
        if _ev(lambda: (activeGym.id if activeGym is not None else None) == gymWithEquipment.profile.id):
            ui.define_text(..., '✓ Active')
        else:
            ui.define_button(..., 'Set active')
        type = _ev(lambda: gym.gymType)
        if type is not None:
            ui.define_text(..., _ev(lambda: f"{type.emoji} {type.displayName}"))
```

## Where this leaves the project

Two screens now go Compose → runnable kit screen, COMPLETE-match-verified, with the bindings and
control flow all mechanical from Kotlin. Sequence remaining: (1) a dynamic-data 2nd screen
(exercises) to exercise enum `displayName()` lifts + `.forEach{}` at runtime (paths' dynamic path is
lifted but unenrolled-by-design); (2) the path-(c) app migration so a generated `*_screen.gen.py`
drops into the live app (the app must consume the transpiled viewmodels). The generator side is now
end-to-end: structure → IR → transpiled VM → transpiler bindings → runnable code → complete match.
