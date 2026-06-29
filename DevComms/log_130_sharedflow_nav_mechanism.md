# log_130 — generator: SharedFlow-mediated nav (VM events → screen nav callbacks)

Date: 2026-06-28
Type: feature (reusable generator capability). Closes the gap log_129 flagged.

## What

exercise_detail's edit-nav is INDIRECT: a VM action emits to a `navigateToEdit` SharedFlow, a
`LaunchedEffect` collects it and calls `onNavigateToEdit(id)`. The generator modeled only DIRECT
onClicks. Now the shim supports collector registration and the screen's nav callbacks are wired to the
VM's nav flows via a DECLARED `nav_flows` map (not by parsing `LaunchedEffect` — consistent with "nav
targets live in the app NavHost, declared per screen").

## How

- shim (`_StateFlow` / vendored `StateFlow`): a `_collectors` list; `collect(h)` registers; `emit(*a)`
  notifies them synchronously (the pull analog of a LaunchedEffect collecting). One class serves both
  MutableStateFlow value-flows and MutableSharedFlow event-flows.
- `NAV_HANDLERS["exercise_detail"]["nav_flows"]` = `{navigateBack: _nav_back, navigateToEdit: _nav_edit}`;
  nav methods accept the emitted value (Unit ignored / id used). `Unit` added to the shim ns.
- `emit_app_screen` emits, in `build()`, `self.vm.<flow>.collect(<cb>)` for each nav_flow.

## Verified

- exercise_detail: `build()` registers the collectors; firing `vm.editCurrent()` emits `navigateToEdit`
  → collector → `_nav_edit` → `router.navigate('exercise_create')`. The indirect edit-nav now fires.
- no regression: gym_list **5/5** (no nav_flows → emission unchanged), smoke **30/30**, all `--auto` stable.

## Remaining for a full exercise_detail drop-in

- `vm.delete()` emits `navigateBack` but its body errors first (swallowed by `launch`) — the
  exercise_detail ADAPTER doesn't support `repository.delete`; same for `onToggleExcluded`'s
  `countExerciseOccurrences`/`bestSubstitute`. Adapter extension is the next per-screen piece, then
  vendor + route + swap-under the transpiled ExerciseRepository.

## Net

The generator now models BOTH direct-onClick nav AND VM-SharedFlow event nav — the last general UI
mechanism the screens needed. exercise_detail's edit-nav works; the remainder is per-screen adapter +
vendoring.
