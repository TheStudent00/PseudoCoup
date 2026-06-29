# log_131 — exercise_detail: full interaction proven (render + SharedFlow nav + reactive dialog)

Date: 2026-06-29
Type: milestone. The 2nd screen's hard UI patterns all work via the transpiled VM + generator.

## What works (`test_exercise_detail_interactive.py`, ALL PASS)

1. **Renders** the seeded exercise (transpiled ExerciseDetailViewModel + adapter + enum lift).
2. **editCurrent()** → the `navigateToEdit` SharedFlow → collector → `_nav_edit` →
   `navigate('exercise_create')` (the SharedFlow-mediated nav, log_130).
3. **onToggleExcluded()** → sets `excludePrompt` (MutableStateFlow→State, log_123) → rebuild renders
   the AlertDialog (`Already in your program` / `Got it` / `Cancel`).
4. **confirmSwapLater()** → clears `excludePrompt` → rebuild, dialog gone (reactive repaint).

## What it took

- `return@launch` transpiler fix (was emitting `return launch`; the VM's editCurrent/delete use
  `?: return@launch`).
- adapter extension (`_exercise_detail_adapter`): `repository.delete/setExcluded/bestSubstitute/
  toggleFavorite/duplicate` + a `programRepository.countExerciseOccurrences` (>0 → the prompt appears).
- The IR already captured the `excludePrompt?.let` AlertDialog; the generator emits it under a
  `prompt is not None` guard; MutableStateFlow→State drives the repaint.

## Net

exercise_detail's full interaction — the hardest UI patterns (indirect SharedFlow nav, a reactive modal
dialog) — works end-to-end in the sandbox via the transpiled VM. The general mechanisms (generator,
MutableStateFlow→State, SharedFlow-nav) are all exercised by a 2nd screen.

## Remaining for a deployed drop-in

Vendor + route (like gym_list, logs 117/118): write the transpiled VM + ExerciseEntity + the exercise
enums (MovementPattern/EquipmentType/MuscleGroup) + a vendored lift + adapter to
`WFL_PseudoCoup/src/generated`, then route `exercise_detail` via `ExerciseDetailScreenGen`. The
ExerciseEntity lift is heavier than gym_list's (list-of-enum muscle-group fields).
