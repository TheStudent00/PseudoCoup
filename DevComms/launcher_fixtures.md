# Launcher fixtures: PathDetailScreen fix + navArg audit

Scope: `~/Programming/WFL_MixingCenter/render/inspect_layout.py` only (SCREEN_ARGS / SCREEN_SEEDS /
seed_fixtures — shared by the launcher `run_app.py` AND the fidelity dump path). Goal: every screen renders
real content on DIRECT launch, without moving the geometry gauge (which measures the dump path).

## The PathDetailScreen bug

- Cause (named): `PathDetailScreen(pathId: String, onNavigateBack)` takes its navArg as a **direct function
  parameter** and has **no ViewModel**. Every other navArg screen receives its id through a ViewModel's
  `SavedStateHandle` (the `nav` dict -> `viewmodel_for`), so `SCREEN_ARGS` reaches them. PathDetailScreen is
  not fed by that path: the caller's arg loop (`run_app.build_composition` AND `inspect_layout.build`) sees a
  no-default parameter and hands it a `Stub()`. `PathDefinition.findById(Stub)` misses -> the screen renders
  its `"Path not found."` branch.
- `pathId` resolves against **static** `PathDefinition.ALL` (`findById` = list lookup), NOT the DB. So it
  needs a real id, no DB seed. Used `path_just_show_up` (already the deterministic path id in the `wins`
  seed and `PathDefinition.LEVER_EMPHASIS`).

### Fix (launcher-gated, general)

- `SCREEN_ARGS["PathDetailScreen"] = {"pathId": "path_just_show_up"}` — the id source.
- New helper `_bind_direct_nav_args(ns, screen)`, called at the top of `seed_fixtures`: for a screen whose
  `SCREEN_ARGS` keys match its **own declared parameters** (not VM-fed), it rebinds `ns[screen]` to a wrapper
  that pre-fills those params and exposes only the remaining ones to the caller's arg loop (so the leftover
  callbacks still get Stubbed, and there is no positional/keyword collision).
- **Why a wrapper, not `functools.partial`**: `pathId` is the first positional param, so `partial(fn,
  pathId=...)` collides when the caller passes the `onNavigateBack` Stub positionally. The wrapper carries an
  explicit `__signature__` of only the unbound params.
- **Gauge safety — the critical bit**: the helper is gated on `kivy_kit.OVERLAYS_ENABLED`, which `run_app`
  sets `True` (the running app) and `inspect_layout` leaves `False` (the dump). The Kotlin ground truth
  (`LayoutDumpAllTest.dumpPathDetailScreen`) renders PathDetailScreen with `pathId = ""` -> `"Path not
  found."`. So the DUMP must keep passing a Stub/empty and rendering that same empty state; only the LAUNCHER
  gets the populated path. Binding in the dump would populate only the Python side and move the gauge.
- Verified: launcher renders the real path (title "Just Show Up", tagline, session chips, The evidence / Why
  it works / Modality sections — 39 nodes). Dump still renders `"Path not found."` (unchanged),
  `PathDetailScreen: 1/1 within tolerance`.

## Audit of every other screen (layout_screens.txt, 28 screens)

navArg screens fall into two groups. Findings:

- **VM-fed via SavedStateHandle, `checkNotNull` (need a real id) — all already covered, no change:**
  - `ExerciseDetailScreen` exerciseId (`ex_squat`, SCREEN_ARGS ✓)
  - `ProgramEditorScreen` programId (`prog_gup_3d_beg`, SCREEN_ARGS ✓)
  - `ProgramDayEditorScreen` dayId (`day_gup_3d_beg_w1_d1`, SCREEN_ARGS ✓)
  - `ExercisePickerScreen` dayId (`day_gup_3d_beg_w1_d1`, SCREEN_ARGS ✓)
  - `WorkoutExecutionScreen`, `WorkoutCooldownScreen`, `SuggestedStretchesScreen` sessionId (dynamic id from
    the `session` seed's return ✓)
  - `WorkoutSummaryScreen`, `SessionDetailScreen` sessionId (dynamic id from the `sessionDone` seed ✓)
- **VM-fed, nullable navArg (missing id = valid "create new" mode, NOT a placeholder bug) — left as-is:**
  - `ExerciseCreateViewModel` exerciseId (nullable -> create-new form)
  - `GymEditorViewModel` gymId (nullable -> create-new gym form)
- **Direct-parameter navArg (like PathDetail) — only two, and only one was broken:**
  - `PathDetailScreen` pathId — FIXED (above).
  - `ReportBugScreen(onNavigateBack, originRoute: String, viewModel=None)` — `originRoute` IS a direct no-
    default param (gets a Stub), but it is read ONLY inside `onSubmit=lambda: viewModel.submit(originRoute)`,
    never during render. So it renders the full bug-report form on direct launch. **Already OK, no change.**
- **All remaining screens** take `innerPadding: PaddingValues` + callbacks + `viewModel` (default None). A
  Stub `innerPadding` is just scaffold padding; the ViewModel supplies the content. They render fine and are
  already measured in the 377. Not navArg screens; nothing to add.

Nothing had to be flagged as "can't populate" — every navArg screen either renders real content already or
was fixed.

## Gates

- `python3 fidelity.py` -> **FIDELITY ALL: 377/377** components within tolerance (28 screens). **Gauge held
  at 377/377.** (PathDetailScreen 1/1, unchanged — the dump still renders the empty state that matches the
  Kotlin `pathId=""` ground truth.)
- `python3 interact.py` -> **INTERACT: 513 fired, 513 ok, 0 failures across 27 screens.**
- `run_app.py PathDetailScreen` -> screenshot `layout_inspect/shots/fix_pathdetail0001.png` shows the real
  populated path (not "Path not found.").
