# DI fail-loud + complete seed fixture (Bug 1 fix)

Status: both parts of the fix implemented, verified working by execution. File fence honored:
only `render/di.py` and `render/run_app.py` touched, in WFL_MixingCenter. No transpiler/runtime
files touched (`runtime/room.py`, `runtime/coroutines.py` untouched, per instructions). No Kotlin
source touched. Nothing committed.

---

## 1. `render/di.py` -- `viewmodel_of` now fails loud

**Before:** `viewmodel_of` (and the near-duplicate `viewmodel_for`) wrapped `build(cls, ns, ctx)` in
`try/except Exception: return None`, silently converting ANY construction-time exception -- including
a genuine bug like `ProgramsViewModel`'s eager `combine(...).stateIn(...)` raising `AttributeError`
on `user.trainingExperience.ordinal` when `trainingExperience` was `None` -- into "not fully
buildable," which made the screen fall back to `runtime/extras.py`'s inert placeholder. That
placeholder's `!= None` truthiness (no `__eq__`/`__ne__` override) made every `if x.value != None`
dialog guard in `ProgramsScreen.py` evaluate `True` simultaneously, stacking 3 `AlertDialog`s.

**After (`render/di.py`, `viewmodel_of`, ~line 131-154):** the `except Exception: return None` is
replaced with `except Exception as e: raise RuntimeError(...) from e`, naming the offending
ViewModel class, the original exception class/message, and chaining the real traceback via `from e`.
The ONLY remaining silent-`None` path is the pre-existing, unrelated one: `ctx["real"] == False`,
set inside `build`/`_resolve` when a dependency is legitimately unresolvable off-Android (no
exception is ever raised on that path -- it's a deliberate "can't build this off-Android" signal, not
error-swallowing). This is exactly the law's target: "fail loud on real bugs, still tolerate the
known off-Android gaps."

`viewmodel_for` (used by `build_composition`, the standalone-screen launcher) previously had its own
copy of the same `try/except Exception: return None` broad-catch. It's now a one-line delegate to
`viewmodel_of`, so the fix is ONE place, not two -- the "one cause = one general fix in a shared
layer" law: any future VM-construction bug anywhere in the app (not just Bug 1's `ProgramsViewModel`)
now surfaces immediately and identically through whichever entry point builds it (`di.install`'s
runtime factory, or `viewmodel_for`'s standalone-screen path).

`di.install`'s `factory` closure calls `viewmodel_of` directly, so it inherits the fail-loud behavior
with no changes needed there.

## 2. `render/run_app.py` -- complete seeded UserEntity

**Before (`build_app_composition`, ~line 98-100):** the seeded `UserEntity` supplied only
`id, displayName, weightUnit, workoutMode, onboardingCompleted, createdAt, updatedAt` -- 4 required
Kotlin fields (`trainingExperience`, `bodyWeightKg`, `strengthGainProfile`, `trainingRecency`) were
left at the transpiled entity's Python default of `None`, even though `trainingExperience` is
non-nullable in the real Kotlin `UserEntity` and gets read unconditionally
(`ProgramVariants.collapseByExperience` -> `.ordinal`).

**Researched, not invented:** read `WFL/app/.../data/db/entity/UserEntity.kt` (the real schema),
`TrainingExperience.kt`/`StrengthGainProfile.kt`/`TrainingRecency.kt` (the real enum values), and
`OnboardingViewModel.kt`/`UserRepository.kt` (what onboarding actually sets vs. leaves alone) to
build a fixture that matches a genuine onboarded user's shape -- not an invented one:

- `workoutMode` is **never** touched by onboarding -- stays `RPE` (the seed default), unchanged.
- `trainingExperience`, `trainingRecency`, `strengthGainProfile`, `bodyWeightKg` ARE set by
  onboarding (user selections / parsed input) -- now given real enum values (`BEGINNER`,
  `CURRENTLY_TRAINING`, `GRADUAL`, `80.0`) instead of `None`.

```python
db.userDao().insertIfAbsent(ns["UserEntity"](
    id="user_default_id", displayName="User", weightUnit=ns["WeightUnit"].KG,
    workoutMode=ns["WorkoutMode"].RPE, trainingExperience=ns["TrainingExperience"].BEGINNER,
    bodyWeightKg=80.0, strengthGainProfile=ns["StrengthGainProfile"].GRADUAL,
    trainingRecency=ns["TrainingRecency"].CURRENTLY_TRAINING,
    onboardingCompleted=True, createdAt=0, updatedAt=0))
```

Notification-preference fields (`notifWorkoutReminder` etc.) were left unset -- they carry real
Kotlin defaults (`IN_APP`) all the way through the transpiler already, so they were never the gap.

---

## Environment note (pre-existing, out of fence, blocks fast iteration)

Both `WFL_MixingCenter/` and `PseudoCoup/` contain a **self-referential symlink** at their own root
(`WFL_MixingCenter/WFL_MixingCenter -> WFL_MixingCenter`, `PseudoCoup/PseudoCoup -> PseudoCoup`,
confirmed via `readlink`/`stat` on both the sandbox mount and the real host paths). Every module
that does `glob.glob(root + "/**/*.py", recursive=True)` (`loader.py`, `oracle.py`,
`resolve.py`, `externals.py`, `datalayer.py`, `build_mixingcenter.py`, ...) recurses through that
loop and hangs indefinitely under this sandbox's mounted filesystem (`find` on the same tree
finishes in <1s; Python's recursive glob does not terminate within the sandbox's 45s hard cap).
This is NOT something my two in-fence files caused or can fix (loader.py/oracle.py are out of
fence) -- I only worked around it in throwaway `/tmp` probe scripts (monkeypatching `glob.glob` to
shell out to `find -L` with the loop path excluded, mirroring the diagnosis doc's own
"never edit the repo, only patch in-process for measurement" convention). Recommend someone
in-fence for those files either delete the stray symlinks or fix the glob call to exclude
self-references.

This is also why `cd tools/pseudokotlin && python3 run_kotlin_tests.py` (the required 160/160 gate)
**times out at 45s with no output** in this sandbox -- it hits the identical glob hang before a
single test runs. It has nothing to do with the `di.py`/`run_app.py` changes (neither file is
imported by that suite) -- confirmed by the fact that `loader.Loader()` alone, patched around the
symlink loop, completes in ~1.1s with 0 load failures across all 254 transpiled files.

---

## TARGETED PROOF A -- full-app boot, Programs dialog, exactly one overlay

Script driven headless (`xvfb-run -a python3 -u <script>`), with the glob workaround applied
in-process only (no repo edits): boot `build_app_composition`, settle via repeated `compose()`
(node count: 15 -> 42 -> 42, stabilized), navigate Program tab -> Browse programs (route
confirmed `programs` via `NavController.currentRoute()`), then drive the real, user-reachable
"add a program" action -- `ProgramsViewModel.openCreateDialog()`, the live VM instance
`hiltViewModel` hands the composed screen (confirmed `type(vm).__name__ == "ProgramsViewModel"`,
not a placeholder).

```
compose #0: 15 nodes
compose #1: 42 nodes
compose #2: 42 nodes
route: programs
AlertDialog count BEFORE add-program action: 0
AlertDialog overlay count after openCreateDialog(): 1
  overlay texts: ['New program', 'Program name', '', 'Create', 'Cancel']
PASS: exactly ONE dialog overlay present after the add-program action
dialog buttons: [('TextButton', ['Create'], True), ('TextButton', ['Cancel'], True)]
PASS: all dialog buttons carry live onClick handlers
AlertDialog overlay count after firing dismiss handler: 0
PASS: overlay closed after dismiss handler fired
PROOF A: ALL PASS
```

Pre-fix (per `overlay_path_diagnosis.md`), this same screen showed **3** simultaneously-open
`AlertDialog`s (create + phantom delete-confirm + phantom swap-confirm) with zero user action
taken, because `ProgramsViewModel` silently fell back to the inert placeholder. Post-fix: 0
dialogs before any action, exactly 1 after the real add-program action, both buttons carry live
`onClick` handlers, and firing the dismiss (`Cancel`) handler closes it back to 0.

(Note: the screen's `FloatingActionButton` -- the FAB visual for "add program" -- is itself gated
in `ProgramsScreen.py` by `uiState.value.isOnMyOwnJourney`, which is `False` for a fresh fixture
user with no enrolled custom path; this is real, unrelated Kotlin-mirrored UI logic, confirmed by
reading `ProgramsScreen.py` line 22-24, not a defect this task's fence covers. The equivalent,
always-reachable trigger -- `openCreateDialog()`, the exact handler the FAB's `onClick` calls -- was
used instead to exercise the identical guard logic the bug was about.)

Screenshot capture (`SHOT` env var) was not attempted: `WflApp.run()`'s real event loop needs
several seconds of `Clock.schedule_once` settling time that doesn't fit the sandbox's 45s
hard cap once `load_ns()`/Kivy window init overhead is included; the compose-tree assertions above
are the load-bearing proof (same node/handler objects the real Kivy widgets are built from).

## TARGETED PROOF B -- construct every ViewModel, assert zero construction exceptions

Built all 30 concrete `*ViewModel` classes the loaded namespace exposes via `di.viewmodel_of`,
using the app's seeded fixture (`build_app_composition`) plus, for screens that take real route
arguments, the SAME `SCREEN_ARGS`/`SCREEN_SEEDS` table `render/inspect_layout.py` already uses for
standalone screen launches (not inventing new fixture shapes).

```
21 ViewModels: OK-real, zero exceptions --
  AppViewModel, DebugPanelViewModel, ExerciseCreateViewModel, ExerciseDetailViewModel,
  ExercisePickerViewModel, ExercisesViewModel, GymCreateWizardViewModel, GymEditorViewModel,
  GymListViewModel, HistoryViewModel, LogCardioViewModel, MyProgramViewModel,
  OnboardingViewModel, PathsViewModel, ProgramDayEditorViewModel, ProgramEditorViewModel,
  ProgramsViewModel, ProgressViewModel, ReportBugViewModel, SettingsViewModel, TodayViewModel,
  UpdateProgramWizardViewModel, WinsHomeViewModel, WinsListViewModel, WorkoutWarmupViewModel

5 ViewModels: EXCEPTION (all the SAME shape -- a missing route arg, not a seed/DI defect) --
  SessionDetailViewModel, SuggestedStretchesViewModel, WorkoutCooldownViewModel,
  WorkoutExecutionViewModel, WorkoutSummaryViewModel
  -> RuntimeError: ... raised RuntimeError: value was null
```

All 5 failures are `checkNotNull(savedStateHandle[ARG_SESSION_ID])` (confirmed by reading
`WorkoutExecutionViewModel.py` line 32 and the equivalent lines in the other 4) -- these screens are
only reachable mid-workout with a real, in-progress session/cardio-log id, and
`render/inspect_layout.py`'s `SCREEN_ARGS` table (out of fence) has no entry supplying one for
these 5 (only `ExerciseDetailScreen`, `ProgramEditorScreen`, `ProgramDayEditorScreen`,
`ExercisePickerScreen`, `PathDetailScreen` have entries, and all 4 of those DO build clean --
see the OK-real list above, which includes `ExerciseDetailViewModel`, `ExercisePickerViewModel`,
`ProgramDayEditorViewModel`, `ProgramEditorViewModel` built WITH their real args from that same
table). This is the fail-loud mechanism working exactly as intended: it distinguishes "this VM has
a real bug" (none found) from "this VM legitimately needs a route argument the harness didn't
supply" (an honest, informative `RuntimeError` naming the exact missing arg, not a silent
placeholder) -- confirming the DI fail-loud change does NOT newly crash the app anywhere a real
seed/nav-arg exists for it. Filling in `SCREEN_ARGS` for the workout-execution flow is a
`render/inspect_layout.py` change and is out of this task's file fence; flagged, not fixed.

---

## Gate: `cd tools/pseudokotlin && python3 run_kotlin_tests.py`

**Did not complete within the sandbox's 45s hard cap** -- times out with zero output before a
single test runs, due to the pre-existing self-referential-symlink glob hang described above
(confirmed present in both repos' `**/*.py` recursive globs, unrelated to `di.py`/`run_app.py`,
which that suite doesn't import). Per the task's own note ("if not, note it; it touched nothing
you changed") this is reported rather than worked around inside the repo. `loader.Loader()` alone,
exercised with an in-process-only glob patch (no disk writes), completed in ~1.1s with `failed: []`
across all 254 transpiled files -- i.e. the loader itself is fine; only the raw filesystem walk in
this sandbox is pathological.

---

## Files changed (fence-compliant)

- `/home/lucas/Programming/WFL_MixingCenter/render/di.py` -- `viewmodel_of` fails loud;
  `viewmodel_for` delegates to it (removed its duplicate broad-catch).
- `/home/lucas/Programming/WFL_MixingCenter/render/run_app.py` -- `build_app_composition`'s
  seeded `UserEntity` now carries all 4 previously-`None` onboarding-set fields with real,
  Kotlin-schema-derived values.

No other file touched. Nothing committed (`git status`/`git diff` left for the user to review and
commit).
