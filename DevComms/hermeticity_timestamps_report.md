# Hermeticity + deterministic timestamps report

## TASK A — compose test hermeticity

### Mechanism (named precisely)
- The flip carrier is the **JVM-static `androidx.arch.core.executor.ArchTaskExecutor` IO thread pool**,
  which Room uses as its default query/transaction executor when none is set on the builder.
- `ProgramEditorViewModel.uiState` is a `combine(programFlow, roadmapFlow, activePaths.map{...})`
  turned into a `StateFlow` via `stateIn(..., SharingStarted.WhileSubscribed(5_000), ProgramEditorUiState())`.
  The **initial** value `ProgramEditorUiState()` has `isReadOnly = false`, and
  `ProgramEditorScreen.kt` renders the **editable** branch ("Program name" `LabeledField`) whenever
  `!isReadOnly`. The correct **read-only** branch ("Join") only appears AFTER the combine emits its
  first real value (the seeded `prog_gup_3d_beg` has `isAppCurated = true`, so every real emission is
  read-only). So the dump is correct only if the Room-backed flows have emitted before `dump()` reads
  the tree.
- The tests are NOT hermetic: `Assembler` builds ViewModels but never cancels their `viewModelScope`,
  so each test's `WhileSubscribed` / `init{}` flow collectors keep running for the rest of the JVM's
  life. Because every test's in-memory DB shared the ONE static ArchTaskExecutor pool, the leaked
  collectors from `dumpOnboardingScreen` + `dumpReportBugScreen` + `dumpExercisePickerScreen`
  (jointly, per `leak_bisect_report.md`) contend that shared pool enough that
  `dumpProgramEditorScreen`'s first Room-flow emission arrives after `waitForIdle()`/`dump()` — so the
  dump captures the `isReadOnly=false` initial state → **editable**. This is the "JVM-lifetime state
  shared across tests" (not a DataStore/preferences file — `Assembler` wires `SystemTimeProvider`, and
  `UserRepository`/`PathRepository` are pure Room, so no preferences are on the read path).

### Fix (files + what)
- `tools/pseudokotlin/gen_layout_dumps.py` — in the generated `assembler()`, give each test its own
  Room executors instead of the shared static pool:
  `Executors.newFixedThreadPool(4)` passed to `.setQueryExecutor(...)` / `.setTransactionExecutor(...)`
  on the `inMemoryDatabaseBuilder`. One change, all tests, no per-screen special-casing. Regenerated
  `LayoutDumpAllTest.kt`.

### Verification
- Baseline (before fix), full `LayoutDumpAllTest` + `LayoutDumpTest` run → `ProgramEditorScreen.json`
  = **editable** (bug reproduced), BUILD SUCCESSFUL.
- After fix, same full run → `ProgramEditorScreen.json` = **readonly**, **BUILD SUCCESSFUL**.

## TASK B — deterministic session timestamps

### Mechanism (named precisely)
- Both engines seed a live session via `WorkoutExecutionRepository.startSessionFromProgramDay(...)`
  (+ `completeSession(...)` for `sessionDone`), which stamps `WorkoutSessionEntity.startedAt`
  (and `completedAt`) from wall-clock `now`. `SessionDetailScreen` renders
  `formatDetailDate(startedAt)` in its header, so the two engines disagree by whatever minute each run
  landed on ('...8:41 PM' vs '...8:42 PM') → 13/14.

### Fix (files + what)
- After seeding, pin the created row's `startedAt` (and `completedAt` only if set) to the fixed instant
  **1718438400000** (2024-06-15 08:00 UTC — the same instant already used for the cardio fixture), via
  `workoutSessionDao().getById(sid).first()` → `.copy(...)` → `.update(...)`, mirrored on both halves:
  - Kotlin: generator assembler template in `tools/pseudokotlin/gen_layout_dumps.py`
    (added `import kotlinx.coroutines.flow.first`); regenerated `LayoutDumpAllTest.kt`.
  - Python: `render/inspect_layout.py` `seed_fixtures`.

### Verification (DISPLAY_SIZE=411x915, layout_diff)
- SessionDetailScreen: **14/14** (was 13/14) — header now 'Sat, Jun 15 at 8:00 AM' on both engines.
- WorkoutSummaryScreen (sessionDone): **2/2** (no regression).
- WorkoutExecutionScreen (session): **28/31** (unchanged).
- WorkoutCooldownScreen (session): **25/25** (unchanged).
- SuggestedStretchesScreen (session): **3/3** (unchanged).
