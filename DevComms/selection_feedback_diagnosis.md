# Selection / Enrollment Feedback Diagnosis — Symptom 1 (Paths selection) & Symptom 2 (Today enrollment)

## Summary

Both user-reported symptoms are confirmed real, reproduced end-to-end programmatically with
concrete before/after evidence, and root-caused to specific lines. They are **two independent
defects**, not one shared cause:

- **Symptom 1** (no visual feedback on Paths card tap): the tap handler fires correctly and the
  ViewModel's selection state updates correctly (confirmed live). The break is entirely in the
  **paint layer**: `ui/theme/WflCard.py` (transpiled from `WflCard.kt`) builds its `colors=`/
  `border=` arguments from `CardDefaults.cardColors(...)` / `BorderStroke(...)`, both of which
  resolve to the runtime's generic inert autostub object (`runtime/compose_ui.py`'s `_UIChain`,
  `_UI`) because neither `CardDefaults` nor `BorderStroke` has a real wrapper anywhere in the
  runtime. The real `containerColor`/`borderColor`/`borderWidth` values are discarded the moment
  they're passed into those stub constructors. Even independent of that, `render/kivy_kit.py`'s
  `_paint_spec()` has no code path that would read a `Card`'s `colors=`/`border=` constructor
  kwargs at all — it only reads `Modifier.background(...)`/`Modifier.border(...)` chain ops or a
  static per-kind `_SURFACE_ROLE` theme-role table (`{"Card": ("surface", 12.0), ...}`), which is
  the same fill color for every Card regardless of `isSelected`. Two compounding gaps, either
  alone sufficient to explain the symptom, both in `tools/pseudokotlin` (PseudoCoup) — in scope.

- **Symptom 2** (Today screen doesn't reflect a fresh enrollment): the DB write happens correctly,
  and the Room-Flow-invalidation fix (already landed, confirmed still green) correctly propagates
  the new `isEnrolled` row into `TodayViewModel._outerState`'s `combine(...)` — confirmed directly:
  `_outerState.first().enrolledProgram` IS the newly enrolled `ProgramEntity` immediately after
  the enroll call. The break is one step downstream: `_dataState = _outerState.flatMapLatest { ... }`
  (`ui/today/TodayViewModel.py`, transpiled from `TodayViewModel.kt:301`). `runtime/coroutines.py`'s
  `Flow.flatMapLatest()` (`~line 138-139`) runs the inner lambda **once, eagerly**, against
  whatever snapshot value `self._values[-1]` held at the moment `flatMapLatest` was called (VM
  construction time, when no program was enrolled yet), and returns a plain, non-live `Flow`/
  `StateFlow` with **no subscription back to the outer flow** — unlike `combine()`, which the
  Room-invalidation fix specifically wired up via `_link_live()`, `flatMapLatest` was never given
  the equivalent treatment. So `_dataState` (and everything downstream: `uiState`) is frozen
  forever at its first-ever computed value, regardless of how many times `_outerState` later
  changes. This is a **general** gap: every VM in the app that uses `.flatMapLatest(...)` off a
  Room-backed (or otherwise live) flow — not just Today — inherits the same permanent staleness.
  In scope, in `tools/pseudokotlin/runtime/coroutines.py`.

Both root causes live inside `tools/pseudokotlin` (PseudoCoup) / are exercised through
`WFL_MixingCenter/render` and `WFL_MixingCenter/ui/...` (the transpiled app code, which is
faithful to the Kotlin ground truth in both cases — nothing in the Kotlin source is at fault).

---

## Symptom 1 — Paths selection has no visual feedback

### Ground truth (Kotlin)

`WFL/app/src/main/java/com/sara/workoutforlife/ui/paths/PathSelectionSheet.kt`:

- `PathCard` (lines 178-234): a selected path card is supposed to show THREE simultaneous cues:
  1. **Container background** flips to `MaterialTheme.colorScheme.primaryContainer` (line 185-186,
     vs. `colorScheme.surface` unselected).
  2. **Border** flips to `MaterialTheme.colorScheme.primary` at `2.dp` width (vs.
     `colorScheme.outlineVariant` at `1.dp`, lines 192-194).
  3. A **checkmark badge**: a filled circular `Surface` with a `Check` icon appears at the card's
     trailing edge only `if (isSelected)` (lines 215-231).
- `isSelected` is computed per-card at line 133: `def.id in state.selectedPathIds`.
- The bottom "Start my Path" button is `enabled = state.selectedPathIds.isNotEmpty()` (line 91) —
  a fourth, secondary cue.

`ui/paths/PathsViewModel.kt`'s `togglePathSelection(pathId)` (lines 52-66) updates
`_pickerState.value` (a `MutableStateFlow<PathPickerState?>`), which is exactly the kind of write
that should recompose the sheet with a new `selectedPathIds` set.

### Repro evidence (before/after)

Booted the real app shell (`render/run_app.build_composition(ns, "PathsScreen")` and, separately,
the standalone `PathSelectionSheet` composed with the real live `PathsViewModel`'s handlers),
fired the real handler chain a tap on "Just Show Up" would fire, and inspected the composed node
tree directly:

```
pickerState.selectedPathIds after toggle: KtSet({'path_just_show_up'})   # <- state DID update
found handler for 'Just Show Up': True                                   # <- handler correctly wired to the Card node
node kind carrying handler: Card

--- AFTER tap+recompose: matching card subtree props ---
target card found: True
props: {'modifier': <Modifier fillMaxWidth>, 'enabled': True,
        'shape': <runtime.compose_ui.RoundedCornerShape object ...>}
```

Note `containerColor`/`borderColor`/`borderWidth`/`colors`/`border` are **entirely absent** from
the rendered `Card` node's props — not present-but-null, missing outright. Traced with an
in-process-only, reverted-afterward instrumentation of `runtime/compose.py`'s kwarg recorder
(confirmed clean via `git diff` after the probe): `Card(...)` is called by `WflCard.py` with
`colors=`, `border=`, `elevation=` kwargs, but they never appear in the recorded node — proving the
loss happens before the values ever reach the generic `Card` emitter.

Direct trace of `WflCard.py`'s own module globals:

```
CardDefaults -> <ui> <class 'runtime.compose_ui._UIChain'>
BorderStroke -> <ui> <class 'runtime.compose_ui._UIChain'>
cardColors(containerColor="TESTCOLOR") result: <ui>  (callable: True)
BorderStroke("W", "C") result: <ui>                  (callable: True)
```

Both are the generic `_UI`/`_UIChain` autostub — calling them with the real color/width values
discards those values and returns the same inert, callable singleton.

### Root cause (confirmed by execution, file + line)

Two independent, compounding gaps in `tools/pseudokotlin`:

1. **`tools/pseudokotlin/runtime/compose_ui.py`**: `CardDefaults` and `BorderStroke` are both in
   the generic `_NAMES` list (`~line 66-87`) that binds every listed name to the single inert
   `_UIChain` instance `_UI` (`~line 12-64, 89-90`). Neither has a real, purpose-built wrapper
   that would carry the `containerColor`/`borderColor`/`borderWidth` values it's constructed with
   forward into a usable form. `ui/theme/WflCard.py` (`~line 7-11`, transpiled from
   `WflCard.kt`) calls `BorderStroke(borderWidth, borderColor)` and
   `CardDefaults.cardColors(containerColor=containerColor)`, both of which immediately collapse
   to `_UI`, throwing the real values away before `Card(...)` is even called.

2. **`WFL_MixingCenter/render/kivy_kit.py`**, `_paint_spec()` (`~line 419-464`): even if `colors=`/
   `border=` did survive onto the `Card` node's `props`, this function — the ONLY place fill/border
   color is ever resolved for painting — has no code path that reads them. It reads only
   `node.props["modifier"]`'s `background`/`clip`/`border` **Modifier-chain ops**, or, failing
   that, a static `_SURFACE_ROLE` table (`~line 338`: `"Card": ("surface", 12.0)`) that paints
   every `Card` the same theme-role color regardless of any `isSelected`-driven kwarg. There is no
   mechanism anywhere in `kivy_kit.py` for a Card's constructor-level `colors=`/`border=`
   arguments (the M3-idiomatic way `WflCard.kt` expresses per-instance selected/unselected
   styling) to reach the paint pass at all.

Also confirmed as NOT the cause (ruled out by execution): the `item(key=...)` lazy-list slot
mechanism (`runtime/compose.py`), the recompose/remount pipeline (`render/run_app.py`'s
`_remount()` fully clears and rebuilds the Kivy widget tree every recompose, so there's no stale-
widget paint problem), and the handler-wiring path (`_bind_click`) — all verified working
correctly via direct execution.

### In scope?

Yes — both breaks are inside `tools/pseudokotlin` (`runtime/compose_ui.py`) and
`WFL_MixingCenter/render` (`kivy_kit.py`). The Kotlin ground truth and the transpiled
`WflCard.py`/`PathSelectionSheet.py` are faithful; nothing in the Kotlin source or the transpiler's
structural output is at fault.

---

## Symptom 2 — Program enrollment doesn't reflect on Home/Today

### Ground truth (Kotlin)

- `WFL/app/.../data/repository/ProgramRepository.kt`: `enrollProgram(programId)`
  (`~line 83-91`) does `database.withTransaction { programDao.unenrollAll(now); ... update(isEnrolled=true) }`
  against the `programs` table.
- `WFL/app/.../data/db/dao/ProgramDao.kt`: `getEnrolled(): Flow<ProgramEntity?>` (`line 21-22`),
  `SELECT * FROM programs WHERE isEnrolled = 1 LIMIT 1`.
- `WFL/app/.../ui/today/TodayViewModel.kt`:
  - `_outerState: Flow<OuterState>` (`line 280-299`) is a `combine(userRepository.getUser(),
    programDao.getEnrolled(), sessionDao.getActiveSession(), pathRepository.activePaths) { ... }`.
  - `_dataState: Flow<HomeUiState>` (`line 301-452`) is `_outerState.flatMapLatest { outer -> ... }`
    — when `outer.enrolledProgram` is non-null, it builds a second, nested `combine(...)` over
    `programDayDao.getByProgram(programId)` and four other DAO flows to build the week's
    `weeklyRows`/`todayDayId`.
  - `uiState` (`line 454-474`) is `combine(_dataState, _checkInState, ...).stateIn(...)`.
- Trigger path: `ui/programs/ProgramsScreen.kt:162/190` `onJoin = { viewModel.enrollProgram(program.id) }`
  → `ProgramsViewModel.kt:120-122` → `ProgramRepository.enrollProgram(programId)`.

### Repro evidence (before/after)

Booted the full app (`render/run_app.build_app_composition`), obtained the real, DI-cached
`TodayViewModel` and `ProgramsViewModel` instances the running `AppNavigation` composition
actually uses (via `runtime.extras.hiltViewModel(...)`, the same accessor the composed screens
call), then drove the real handler a tap on "Join" would fire:

```
BEFORE enroll:
today uiState.todayDayId: None
today uiState.weeklyRows count: 0

enrolling program: prog_gup_3d_beg  (via programs_vm.enrollProgram(programId))

AFTER enroll (immediately):
DB direct check: programDao.getEnrolled().first() -> <ProgramEntity ...>   # <- write succeeded
today_vm.uiState.value.todayDayId: None                                    # <- STILL stale
today_vm.uiState.value.weeklyRows count: 0

AFTER recompose settle (2x compose()):
today_vm.uiState.value.todayDayId: None                                    # <- still stale
Today screen visible texts: [..., "This week's workouts",
  'Set up a program to see your week here.',
  'No program enrolled yet. Head to Paths to get started.']                # <- exact user-reported symptom
```

Deeper trace on the SAME live `TodayViewModel` instance the composed screen renders from
(`runtime.extras.hiltViewModel(ns["TodayViewModel"])`):

```
_outerState (MutableStateFlow) has _add_listener: False
_outerState.first().enrolledProgram: <ProgramEntity ...>     # <- the outer state DOES see the enrollment
                                                               #    when freshly recomputed via .first()

_dataState (plain Flow, built via _outerState.flatMapLatest(...)) has _add_listener: False
_dataState.first().todayDayId: None                           # <- but the flatMapLatest'd Flow is frozen
_dataState.first().weeklyRows count: 0                        #    at its ORIGINAL (no-program) snapshot

uiState.value.todayDayId: None                                 # <- and so is everything built on top of it

Direct check of programDayDao.getByProgram(enrolled programId).first(): 259 days   # <- real day
                                                                                     #    structure exists;
                                                                                     #    not a data gap
```

This isolates the break precisely: `_outerState` itself is current (proving the Room-invalidation
fix IS working correctly for `combine()`), the underlying DAO data is real and complete (259
program days), but `_dataState` — built by `.flatMapLatest(...)` off `_outerState` — never
re-runs after being constructed once at VM-init time, because `flatMapLatest` performs no live
subscription at all.

### Root cause (confirmed by execution, file + line)

`tools/pseudokotlin/runtime/coroutines.py`, `Flow.flatMapLatest()` (`~line 138-139`):

```python
def flatMapLatest(self, fn):
    return fn(self._values[-1]) if self._values else Flow()
```

This runs `fn` **exactly once**, against whichever value `self._values[-1]` held at the moment
`flatMapLatest` was called (i.e. once, eagerly, during `TodayViewModel.__init__`, when
`_outerState`'s snapshot had `enrolledProgram = None`), and returns whatever plain `Flow`/
`StateFlow` `fn` happens to produce for that one snapshot — with **no listener registered back on
`self`** to re-run `fn` and push a fresh value when the outer flow later changes. Compare
`combine()` (`~line 271-292`), which the already-landed Room-invalidation fix specifically wired
via `_link_live()` (`~line 261-268`) to duck-type-check `_add_listener` on its inputs and
re-subscribe — `flatMapLatest` was never given the equivalent treatment, so a `flatMapLatest`
sitting anywhere between a live (Room-backed or `combine()`-derived-live) flow and its consumer
breaks the liveness chain completely, permanently freezing everything downstream at its very
first computed value.

This is a **general** gap, not Today-specific: any transpiled ViewModel using
`someFlow.flatMapLatest { ... }` off a live upstream flow (Room DAO flow, or a `combine()` result
that is itself live) inherits the identical permanent-staleness bug. `TodayViewModel` just happens
to be the screen the user found it on because "enrolled program becomes non-null" is the most
visible before/after transition through a `flatMapLatest`.

Explicitly **not** the cause: the Room Dao-flow invalidation mechanism (confirmed still fixed/green
— `_outerState`'s own `combine()` correctly reflects the write); the DI/ViewModel-scoping
mechanism (confirmed: the same cached `TodayViewModel` instance is used across recomposes — this
is not a "stale VM re-created" or "wrong VM instance" issue, it is the SAME instance's own
`_dataState` field that never updates); and the enrollment write path itself (confirmed to commit
successfully and correctly, including the `withTransaction` unenroll-all + enroll-one pair).

### In scope?

Yes — the root cause is entirely inside `tools/pseudokotlin/runtime/coroutines.py`
(`Flow.flatMapLatest`), exercised through the transpiled `ui/today/TodayViewModel.py` in
`WFL_MixingCenter`. The Kotlin ground truth (`TodayViewModel.kt`) and its Python transpile are
both faithful and correct; nothing in the Kotlin source is at fault.

---

## One cause or two?

**Two separate causes.** They fail at completely different layers of the stack and share no
mechanism:

- Symptom 1 is a **paint-layer / styling-wrapper gap**: real state updates correctly, real
  recompose fires correctly, but the visual style intent (`colors=`/`border=` on a `Card`) is
  discarded by inert autostub wrappers (`CardDefaults`, `BorderStroke` in `compose_ui.py`) and,
  redundantly, has no consumer in the Kivy paint pass (`kivy_kit.py`'s `_paint_spec`) even if it
  did survive. This has nothing to do with Flow/StateFlow reactivity at all — `PathPickerState`
  is a plain `MutableStateFlow`, not Room-backed, and its own state IS current at recompose time;
  the failure is purely about what happens to *styling* kwargs on the way to pixels.

- Symptom 2 is a **reactive-Flow-operator gap**: the write and the state are both genuinely
  correct at the point `flatMapLatest` is invoked; the failure is that the operator itself never
  re-subscribes to its upstream. This has nothing to do with painting/rendering, Kivy widgets, or
  Compose styling at all.

The only surface-level similarity ("the user does something and nothing visibly changes") is
coincidental — as with Bug 1/Bug 2 in the prior overlay diagnosis, this task's candidate "shared
general cause" hypotheses (a single recompose-plumbing gap, or a single state-wiring gap) are both
ruled out by direct execution: Symptom 1's state and recompose are proven live; Symptom 2's paint/
render pipeline is irrelevant to its failure.

---

## Recommended fix locations (conceptual only, no code)

**Symptom 1** — two complementary fixes, either alone would resolve the visible symptom, both
together are the general fix:

1. `tools/pseudokotlin/runtime/compose_ui.py`: give `CardDefaults.cardColors(...)` and
   `BorderStroke(...)` real, purpose-built wrapper classes (mirroring how `Color` already has one)
   that actually retain the `containerColor`/`contentColor`/`width`/`color` values they're
   constructed with, instead of falling through to the generic `_UIChain` autostub. `ButtonDefaults`
   and any other `*Defaults.xColors(...)` factory used the same way should get the same treatment
   as one general fix, since the identical discard happens for every M3 component that expresses
   selected/pressed/disabled state via a `colors=`/`border=` constructor kwarg rather than a
   `Modifier.background/border` chain.
2. `WFL_MixingCenter/render/kivy_kit.py`, `_paint_spec()`: add a code path that reads a `Card`
   (and other M3-styled-via-kwarg components)'s recorded `colors=`/`border=` node props — once
   they carry real `Color`/width values per fix #1 — ahead of (or instead of) the static
   `_SURFACE_ROLE` fallback, so an explicit per-instance `containerColor`/`borderColor` actually
   overrides the generic theme-role paint.

**Symptom 2** — one general fix location:

`tools/pseudokotlin/runtime/coroutines.py`, `Flow.flatMapLatest()` (and the free-function
`flatMapLatest()` wrapper around it): needs the same live-subscription treatment `combine()`
already got from the Room-invalidation fix — i.e. `flatMapLatest` should duck-type-check its
receiver flow for `_add_listener` (the same mechanism `_link_live()` already implements) and, when
present, register a listener that re-runs `fn` against the new upstream value and pushes the
result into the returned flow's sink whenever the upstream re-emits, rather than computing `fn`
once against a frozen snapshot. This is the single, general fix location: every VM in the app that
chains `.flatMapLatest(...)` off a live (Room-backed or combine-derived-live) flow — not just
`TodayViewModel` — rides on this same operator, so fixing it here fixes Today's enrollment-
staleness and any other screen exhibiting the identical "flatMapLatest never re-runs" pattern at
once, without touching any transpiled ViewModel code.
