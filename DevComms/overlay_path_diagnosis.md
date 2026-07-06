# Overlay / Path Diagnosis — Bug 1 (stuck Program dialog) & Bug 2 ("find your path" after enroll)

Status: both bugs reproduced programmatically (confirmed-by-execution), root-caused to specific
lines, and the two are **NOT** the same general cause — they are two independent defects that happen
to both surface through "an overlay/flow that doesn't behave." Neither traces into Kotlin source; both
live in the Python runtime layer (`tools/pseudokotlin/runtime/`) plus one seeding gap in
`render/run_app.py`. No code was modified in either repo (see "Repro environment" for how this was
verified clean).

---

## Repro environment (note on paths)

Kivy/xvfb were not preinstalled in the isolated workspace; `pip install kivy` was run in the sandbox
only (does not touch the repos). `render/run_app.py` hardcodes `~/Programming/PseudoCoup` and
`~/Programming/WFL_MixingCenter`; the sandbox's `$HOME` didn't have that layout, so two **symlinks**
were created at `/sessions/charming-zealous-hopper/Programming/{PseudoCoup,WFL_MixingCenter}` pointing
at the real mounted repos (`/sessions/charming-zealous-hopper/mnt/...`) purely so `os.path.expanduser`
resolved correctly. Those symlinks lived outside both repos and were deleted at the end of the session.
All diagnostic probe scripts were written to `/tmp` (outside both repos), never inside PseudoCoup or
WFL_MixingCenter. Verified clean afterward:

```
cd .../PseudoCoup && git status --porcelain      # only a pre-existing untracked .claude/
cd .../WFL_MixingCenter && git status --porcelain # only __pycache__ (deleted), no tracked file touched
git diff --stat (both repos)                      # empty
```

No file inside either repo was edited. All tracing was done via runtime monkeypatching from throwaway
`/tmp` scripts (e.g. wrapping `AlertDialog`, `MutableStateFlow.__init__`, `di.install`) — never by
editing the real modules.

---

## Bug 1 — Programs screen "add a program" dialog is completely dead

### Repro (confirmed by execution)

Script: `/tmp/probe2.py` (headless, `xvfb-run -a python3 <script>`, real `EventLoop.post_dispatch_input`
touches plus direct `_fire()` calls once real-touch dispatch on a specific button proved flaky — see
"Touch-dispatch aside" below).

Steps: boot the full app (`run_app.build_app_composition`) → nav to "Program" tab (route → `my_program`,
confirmed) → tap "Browse programs" (route → `programs`, confirmed) → tap the FAB (`FloatingActionButton`,
opens the create-program dialog).

Evidence, from the actual run:

```
AlertDialog node count in tree BEFORE FAB tap: 3      <-- already 3, before ANY dialog was ever opened
FAB found: True center: [28.0, 28.0]
active_overlays count: 3
  overlay kind: AlertDialog children: [('Text', ['New program']), ('Column', [...]), ('TextButton', ['Create']), ('TextButton', ['Cancel'])]
  overlay kind: AlertDialog children: [('Text', ['Delete program?']), ..., ('TextButton', ['Delete']), ('TextButton', ['Cancel'])]
  overlay kind: AlertDialog children: [('Text', ['Swap to <extra>?']), ..., ('TextButton', ['Swap']), ('TextButton', ['Cancel'])]
```

**Three `AlertDialog`s are simultaneously "open"** — the create dialog the user actually tapped for,
plus the screen's *delete-confirm* and *swap-confirm* dialogs, neither of which should exist yet (their
Kotlin guards are `if (deleteConfirmId != null)` and `swapConfirmProgram?.let { ... }`, both `null` at
this point). Note the literal text `"Swap to <extra>?"` — `<extra>` is the `__repr__` of the runtime's
inert placeholder object (`runtime/extras.py`'s `_P`), which is the smoking gun (see Root cause).

Kivy stacks Window-overlay children so the **last-added is on top**; `_collect_open_popups` walks the
tree in source order (create, delete, swap), so the Swap overlay is topmost and eats every touch —
its scrim intercepts taps meant for the visible "New program" panel, and tap-outside routes to
`viewModel.dismissSwap`, which is a no-op because `viewModel` itself is the inert placeholder (see
below). This is why **nothing in the visible dialog responds and no tap dismisses anything** — the
user is actually interacting with (or being blocked by) a different, invisible dialog's overlay.

Screenshots (isolated workspace paths; these are ephemeral to the sandbox run, not saved into either
repo):
`/tmp/shots/dialog_open.png`, `/tmp/shots/after_cancel_attempt.png`, `/tmp/shots/after_tapoutside.png`
(all three show the same visually-identical "stuck" dialog, since the 3 overlapping overlays render at
the same painted position).

### Root cause (confirmed by execution, file + line)

`render/di.py`, `install()` (around line 157-167): the per-route ViewModel factory calls
`viewmodel_of(cls, ns, args)` and, if `build()` raises **any** exception, silently returns `None` — the
screen then falls back to `runtime/extras.py`'s `hiltViewModel()` inert placeholder (`_P_`, line 61,
whose `__repr__` is `"<extra>"`).

For `ProgramsViewModel` specifically, construction *does* raise, inside eager `Flow.combine(...).stateIn(...)`
evaluation:

```
ui/programs/ProgramsViewModel.py:57  -> combine(programRepository.getAll(), pathRepository.activePaths,
                                          userRepository.getUser(), _lam1).stateIn(...)
data/model/ProgramVariants.py:37     -> collapseByExperience(nonArchived, user.trainingExperience)
data/model/ProgramVariants.py:54     -> ... userLevel.ordinal ...
AttributeError: 'NoneType' object has no attribute 'ordinal'
```

`user.trainingExperience` is `None` because the seeded user in **`render/run_app.py`,
`build_app_composition()` (lines 98-100)** constructs `UserEntity(...)` **without** the required
`trainingExperience` field:

```python
db.userDao().insertIfAbsent(ns["UserEntity"](
    id="user_default_id", displayName="User", weightUnit=ns["WeightUnit"].KG,
    workoutMode=ns["WorkoutMode"].RPE, onboardingCompleted=True, createdAt=0, updatedAt=0))
```

`UserEntity.trainingExperience: TrainingExperience` (non-nullable in Kotlin,
`WFL/app/.../data/db/entity/UserEntity.kt:18`) silently defaults to `None` in the transpiled/seeded
Python object, and nothing downstream guards against that — `ProgramVariants.pickForExperience` calls
`.ordinal` on it unconditionally.

Because `hiltViewModel(ProgramsViewModel)` then returns the inert `_P_` placeholder, every
`viewModel.<stateFlow>.value` read in `ProgramsScreen.py` (`showCreateDialog.value`,
`deleteConfirmId.value`, `swapConfirmProgram.value`) is actually a `Stub`/`_P` attribute access — and
`Stub()/_P() != None` is **always `True`** (neither defines `__eq__`, so Python falls back to identity
inequality). That is why **all three of ProgramsScreen's dialogs compose unconditionally on every
render**, regardless of which one the user actually asked to open — confirmed directly:
`render/di.py`'s `build(ProgramsViewModel, ...)` was traced live and reproduces the exact
`AttributeError` above when called with the app-shell's seeded user; the SAME call with a user that has
`trainingExperience` set (or via the standalone `build_composition(ns, "ProgramsScreen")` path, which
also happens to avoid hitting this because a different construction path is exercised) builds a real VM
and 0 `AlertDialog`s appear.

Confirmed with a direct compose-level repro (`/tmp/probe_di2.py`, no Kivy touch needed at all):
```
[FACTORY] cls=ProgramsViewModel nc_id=... route=programs key_in_cache=False
    -> built vm: None (None means placeholder returned)
...
AlertDialog count: 3
```

### Touch-dispatch aside (secondary finding, not the root cause of Bug 1)

While driving the repro, a real `EventLoop.post_dispatch_input` tap on the "Browse programs" `Button`
(a normal, non-overlay `BUTTON_KINDS` widget on `MyProgramScreen`) silently failed to fire `on_press`
even though the widget, its coordinates, and its `onClick` handler were all verified correct and firing
the SAME handler via `kivy_kit._fire()` worked instantly. This was traced to a **probe artifact**, not
an app bug: calling `Composition.compose()` directly (bypassing the app's `_remount()` host, i.e.
calling `compose()` without also rebuilding+reattaching the Kivy widget tree) corrupts the correspondence
between the live widget tree Kivy dispatches touches into and the tree `self._box` was last populated
from. Once the probe was fixed to always settle via `_remount()` (matching `WflApp._remount` /
`realtap_gate.py`'s own pattern), real touches worked normally for ordinary buttons. Flagging this
because it is a real trap for any future headless-touch harness that calls `comp.compose()` ad hoc
without remounting — but it is not what causes either of the two user-reported bugs.

---

## Bug 2 — Paths: "Start my Path" enrolls in the DB but the screen still shows the empty state

### Repro (confirmed by execution)

Script: `/tmp/probe_paths2.py` / `/tmp/probe_paths3.py`. Built the full app shell, navigated to the
`paths` route (confirmed via `NavController.currentRoute()`), obtained the **live** `PathsViewModel`
instance the screen itself uses (via `runtime.extras.hiltViewModel(ns["PathsViewModel"])`, which returns
the same cached instance `di.install`'s factory hands to the composed screen), and drove the real
handler sequence: `startPicker()` → `togglePathSelection("path_just_show_up")` → `enrollAndFinish()`
(the transpiled equivalent of tapping "Find your path", selecting a path card, then "Start my Path").

Evidence:

```
BEFORE any interaction, texts: [..., 'Start with your why.', ..., 'Find your path']
activePaths BEFORE enroll: []
pickerState after startPicker: <PathPickerState ...>
pickerState after toggle: <PathPickerState ...>
pickerState after enrollAndFinish: None                 <-- picker correctly closes
AFTER enroll+recompose, texts: [..., 'Start with your why.', ..., 'Find your path']   <-- STILL empty state
vm.activePaths.value AFTER enroll: []                    <-- unchanged, on the SAME live VM instance
```

Direct DB check (bypassing the VM/Flow entirely, raw SQL against the exact same sqlite connection
`di._db(ns)` holds):

```
DB active rows BEFORE enroll: []
DB active rows AFTER enroll (direct SQL query on same db): [<sqlite3.Row ...>]   <-- the write DID happen
vm.activePaths.value (VM's cached Flow, unchanged): []                          <-- but the VM never saw it
```

**The DB write succeeds.** `PathsViewModel.enrollAndFinish()` → `repository.enroll(pathId, ...)` →
`pathDao.update(...)` genuinely flips `isActive = 1` in sqlite. The bug is entirely on the read side: the
live ViewModel's own `activePaths` `StateFlow` never reflects the new row, in-process, on the exact
instance the screen renders from — this rules out "handler never fired" (bug would be: DB stays empty)
and rules out "screen doesn't recompose" (rules out a Kivy/kit remount-scheduling gap) — the recompose
mechanism runs fine (`pickerState` DID flip to `None` and the picker correctly closed), but the value it
reads for `activePaths` is stale by construction, not by a missed invalidation signal.

### Root cause (confirmed by execution, file + line)

`tools/pseudokotlin/runtime/room.py`, `Dao._flow()` (lines 217-218):

```python
def _flow(self, sql, params=None, pojo=None):    # Flow<List<X>> -- emits the whole list as ONE value
    return Flow([self._db.query(sql, params, pojo=pojo)])
```

This runs the SQL **once**, at the moment `_flow()` is called (i.e. once, eagerly, when
`PathRepository.activePaths = pathDao.getActive()` is evaluated during `PathsViewModel.__init__`), and
wraps that one-shot Python list in a static, single-element `Flow`. Real Room's `Flow<List<PathEntity>>`
re-runs the query and re-emits automatically whenever any write touches the table it reads from (Room's
InvalidationTracker), which is exactly the mechanism `@Query fun getActive(): Flow<List<PathEntity>>`
(`WFL/.../data/db/dao/PathDao.kt:22`) depends on. This stand-in has no such tracking at all — it is a
frozen snapshot, forever. `PathsViewModel.activePaths` (`.stateIn(viewModelScope, ...)` over that dead
Flow) inherits the staleness permanently: no amount of writing to the `paths` table will ever change
what `PathsViewModel.activePaths.value` reports, for the lifetime of that VM instance.

This is a **general** gap, not specific to Paths: `Dao._flow()` / `_flowOne()` back every `Flow<...>`-typed
Room query in the transpiled app (any screen whose UI list is driven by a DAO Flow rather than a
`suspend fun ...Once()` one-shot call is subject to the identical staleness — Paths just happens to be
the screen the user found it on, because its empty/non-empty state is the most visibly binary of the
DAO-Flow-driven UIs).

---

## Do Bug 1 and Bug 2 share one general cause?

**No.** They are independent defects that happen to both look like "the overlay/flow doesn't work":

- **Bug 1** is a `di.py`/seed-data problem: a required entity field (`UserEntity.trainingExperience`)
  is omitted by the app-shell's seeding call in `render/run_app.py`, which causes one specific
  ViewModel's eager `combine(...)` block to throw, which `di.py`'s broad `except Exception: return None`
  swallows into "not fully buildable," which makes `hiltViewModel()` hand back the inert placeholder
  object, whose `!= None` / truthiness semantics happen to make **every** conditionally-guarded
  `AlertDialog` in that one screen emit unconditionally. It is not about the `_bind_click`/`to_widget`
  overlay choke point at all — overlay content DOES route through `to_widget`/`_bind_click` correctly
  (confirmed: `Create`/`Cancel` widgets were found with real `.center` coordinates and real bound
  handlers once a single, correctly-scoped dialog was isolated) — the apparent "dead overlay" is really
  three overlapping, indistinguishable overlays stacked by Kivy's Window child order, with the
  user's taps landing on the wrong (topmost) one whose dismiss handler is *also* a no-op stub call.

- **Bug 2** is a `runtime/room.py` reactive-Flow problem: the DB write is real, the handler is real, and
  the screen's recompose mechanism is real and fires — but the ViewModel's own state source
  (`Dao._flow()`) is a one-shot snapshot with no invalidation tracking, so nothing downstream of it can
  ever see the new row. This has nothing to do with overlays, `_bind_click`, or `to_widget` at all —
  `PathSelectionSheet` in this app is not even a `POPUP_KIND`/Window overlay (it's inline
  `AnimatedVisibility` content inside `PathsScreen`'s own tree, per `PathsScreen.kt`), so the overlay
  choke-point hypothesis doesn't even apply to Bug 2's mechanism.

The task's two candidate "general cause" hypotheses (overlay content bypassing `_bind_click`; or overlay
handlers firing but not triggering host recompose) are **both ruled out by execution**: overlay content
IS wired through `_bind_click` correctly, and recompose DOES fire correctly (proven by `pickerState`
flipping to `None` and the picker screen closing in Bug 2, and by the correct handler identity/behavior
found for Bug 1's dialog buttons once isolated). The real causes are one DI/seed-data gap and one
Room-Flow-stub gap, unrelated to each other and unrelated to the touch-dispatch/overlay machinery the
task suspected.

---

## Recommended fix locations (prose only, no patch)

**Bug 1** — two independent, complementary fixes, either alone resolves the user-visible symptom, both
together are the general fix:
1. `render/run_app.py`, `build_app_composition()` (~line 98-100): the seeded `UserEntity` should include
   a `trainingExperience` value (matching whatever a real onboarded user would have), so
   `ProgramsViewModel` builds for real instead of raising.
2. `render/di.py`, `viewmodel_of()`/`build()` (~lines 117-141): the blanket `except Exception: return None`
   silently converts ANY construction-time exception into "fall back to the inert placeholder," which is
   how a completely unrelated data gap (`trainingExperience`) turned into three simultaneously-open
   dialogs on an unrelated screen. Surfacing (logging, or at minimum distinguishing "build failed because
   of a real bug" from "build failed because a dependency is legitimately unbuildable off-Android") would
   have caught this immediately instead of manifesting as silent, misleading UI overlay corruption.
   This is the general, systemic half of the fix: it's the mechanism that lets any future VM-construction
   exception anywhere in the app turn into the same "phantom stacked dialogs" symptom.

**Bug 2** — `tools/pseudokotlin/runtime/room.py`, `Dao._flow()` / `_flowOne()` (~lines 217-221): these
need genuine invalidation tracking — re-running the SQL and re-emitting whenever `_insert`/`_update`/
`_delete` touches a table the Flow's query reads from (a minimal per-table subscriber list on
`Database`, notified from `_insert`/`_update`/`_delete`, is the natural mechanism — mirroring what Room's
real InvalidationTracker does). This is the single, general fix location: every Flow-typed Room query in
the whole transpiled app rides on this same code path, so fixing it here fixes Paths and every other
DAO-Flow-driven list screen at once, without touching any transpiled screen or ViewModel code.
