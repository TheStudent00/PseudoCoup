# log_119 — handler/navigation emission: the generated gym_list is fully INTERACTIVE

Date: 2026-06-28
Type: milestone. The behaviour layer's last piece -- on_click handlers. The routed generated screen
now renders AND interacts.

## Direct answer

The generated gym_list now emits its on_click handlers, and every one fires correctly through the
transpiled viewmodel + a small per-screen nav map -- verified by firing them in-app:

```
python tools/test_gym_list_gen.py   (in WFL_PseudoCoup, on the seeded InMemoryDb)
  RESULT: MATCH -- generated screen is a drop-in        (renders 10/10)
  OK  back   -> router.navigate('you')
  OK  FAB    -> router.navigate('gym_create_wizard')
  OK  card   -> router.selected_id set + router.navigate('gym_editor')
  OK  delete -> gym removed from the db (VM action via the transpiled VM + adapter)
python tools/smoke_screens.py  ->  SMOKE: 30/30 screens built   (no regression)
```

## How handlers are emitted

The IR now captures each clickable widget's `onClick` (resolved through composable-param binding:
GymListItem's onEdit/onSetActive/onDelete -> the call-site lambdas). The emitter, for a clickable
node, writes a nested handler that captures the per-row loop var by default-arg and calls the
transpiler's Kt->Py of the onClick body with two substitutions:

```python
for _i5, gymWithEquipment in enumerate(gyms or []):
    ...
    def _h20(evt, gymWithEquipment=gymWithEquipment): self.vm.setActive(gymWithEquipment.profile)
    ui.on_click(zid, _h20)
    def _h39(evt, gymWithEquipment=gymWithEquipment): self.vm.delete(gymWithEquipment.profile)
    ui.on_click(zid, _h39)
...
def _h43(evt): self._nav_back()
def _h45(evt): self._nav_editor(None)
```

- `viewModel.X(...)` -> `self.vm.X(...)` (mechanical; runs the transpiled VM -> adapter -> kit db).
- a nav callback -> its declared `self._nav_*` method (the DECLARATIVE part).

## The one declared piece: the nav map

The route TARGETS (which screen `onNavigateBack` / `onNavigateToEditor(id)` go to) live in the app's
NavHost, NOT the screen's Compose -- so they are declared once per screen, like the data adapter:

```python
NAV_HANDLERS["gym_list"] = {"subs": {onNavigateBack->self._nav_back, onNavigateToEditor->self._nav_editor},
  "methods": [_nav_back -> navigate('you');  _nav_editor(id) -> id is None ? 'gym_create_wizard'
                                                                          : selected_id=id, 'gym_editor']}
```

The VM actions need no declaration -- `viewModel.setActive/delete` map mechanically.

## Reactive parity

A VM action repaints in Compose because Room's Flow re-emits; PseudoCoup is pull-based, so the
vendored adapter's setActive/deleteGym now call the kit's `invalidate()` after mutating (exactly the
hand-built viewmodel's behaviour) -- so the generated screen repaints after an action too.

## Status

gym_list is now a COMPLETE generated drop-in in the live app: structure + control flow from Compose,
viewmodel/entities/enum transpiled from Kotlin, bindings transpiler-emitted, handlers emitted +
nav-mapped -- renders identically (10/10), interacts correctly (4/4 handlers), routed by the real
AppRouter, smoke 30/30. The whole vertical traces to Kotlin and runs in the app, end to end.

Remaining frontier: the Python->Dart transpilation for the Flutter pixel goldens (a second-transpiler
concern below PseudoUI) -- and generalising all of this (adapter, nav map) beyond gym_list.
