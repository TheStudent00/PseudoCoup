# Oracle breadth — full domain corpus runs to completion

## Task
Make `oracle.py --all` run to completion (it was aborting mid-run), fix or honestly catalog every
failure, and extend coverage to repository/use-case surfaces where they can be asserted for real.

## Harness bug (fixed)
- **Cause:** `run_python` constructed the test instance (`inst = test_cls()`) *outside* the per-test
  `try`. One corpus test (`LayoutDumpTest`) touches `java.util.TimeZone` in its `init {}` block, so
  the constructor raised `NameError` and aborted the whole `--all` run before ~half the engines ran.
- **Fix:** moved `inst = test_cls()` *inside* the per-test `try` (oracle.py, `run_python`). A class
  whose ctor touches an unshimmed name now yields an honest `ERROR` row for its own methods instead
  of crashing the corpus. Same shape the newer `run_kotlin_tests.py` already used.
- **File:** `tools/pseudokotlin/oracle.py` (only file changed).

## Corpus scope — before / after
- **Before:** `oracle.py --all` aborted at `CardioRecoveryEngine` → only ~3 of 12 discovered classes
  reported; run ended in a traceback.
- **After:** all 12 discovered classes run to completion; summary prints a verdict.

`all_engines()` discovers 12 test subjects (11 pure engine/model + 1 UI-layout instrument). The
repository/DAO surface is covered by a *separate* runner, `datalayer_oracle.py`, against the app's
own `androidTest` classes on the real sqlite3 Room engine.

## Per-area results

### Domain engines / models — `oracle.py --all` (11/12 fully green)
| Subject | python methods |
|---|---|
| AutoregulationEngine | 59/59 |
| CalibrationEngine | 15/15 |
| CardioRecoveryEngine | 12/12 |
| NotificationTriggers | 5/5 |
| PathDefinition | 5/5 |
| PeriodizationEngine | 17/17 |
| ReadinessProgressionGate | 9/9 |
| RestartEngine | 17/17 |
| SampleProgramData | 4/4 |
| SubstitutionEngine | 5/5 |
| WarmupEngine | 12/12 |
| **LayoutDump** | **0/12 — ERROR (named limitation, below)** |

160 domain assertions, all pass — matches `run_kotlin_tests.py` exactly.

### Repository / DAO layer — `datalayer_oracle.py` (4/4 classes, 9 assertions, all green)
Runs the app's own instrumented tests headless against sqlite3 Room:
| Class | assertions |
|---|---|
| ExerciseDaoMuscleGroupTest | 2/2 (muscle-group token matching) |
| GymRepositoryTransactionTest | 1/1 (setActive rollback atomicity) |
| BackupRepositoryRoundTripTest | 2/2 (export→wipe→import restore; newer-schema rejection) |
| MigrationTest | 4/4 (v1/v17/v24/v30 → latest schema migrations) |

These are real, JVM-verified invariants (transaction rollback, backup round-trip fidelity, schema
migration), not smoke rows.

## General fixes (cause → fix → file)
- **Harness abort on ctor NameError** → construct instance inside per-test try → `oracle.py`.
- No transpiler/runtime shims added. The domain engines and the repository layer already run on the
  existing runtime + Room/sqlite shim; nothing was silently patched.

## Named limitations / uncovered surfaces
- **LayoutDumpTest / LayoutDumpAllTest (UI-render instrument, out of oracle scope).** These are not
  domain-equivalence tests — they drive the real Compose layout engine under Robolectric
  (`createComposeRule`, `setContent`, `waitForIdle`) to dump semantics bounds for the layout-fidelity
  instrument. The first unshimmed name they hit is `java.util.TimeZone` (set in `init {}` for a
  deterministic clock), but a TimeZone shim would move **nothing** to green: `TimeZone` is used in
  **zero** main-source files (grep: 0 hits) and past it these tests still require a full Compose/
  Robolectric render engine the oracle namespace has no equivalent for. Adding a TimeZone shim no
  runnable test exercises would be shim-for-show, so it is deliberately **not** added. Catalogued as a
  UI-instrument limitation; its own fidelity coverage lives in `gen_layout_dumps.py` / `fidelity.py`.
- **No use-case layer to cover.** The corpus has no `usecase/` package (grep: 0 dirs) — the engines
  *are* the use-case tier and are fully covered.
- **Repositories without app-authored tests** (Restart/Program/Periodization/Win/User/Cardio/… ~11
  thin Room wrappers). The app ships instrumented tests for exactly 4 repository/DAO surfaces (all
  green above). The rest have no JVM-verified oracle. Authoring my own assertions for them would
  either be out-of-fence new `.kt` in `WFL_MixingCenter`, or unanchored Python assertions with no
  JVM cross-check — both fail the "real, verified invariants only" bar. Listed as **uncovered**
  rather than faked with smoke rows.

## Verification gates
```
oracle.py --all      : 11/12 engines fully green; run completes (no abort).
                       12th = LayoutDump (UI-render instrument, ERROR by design, catalogued).
                       11 domain subjects = 160 assertions, all pass.
datalayer_oracle.py  : ALL GREEN — 4 classes / 9 assertions (repository + DAO + migration).
run_kotlin_tests.py  : RESULT: 160/160 pass  (unchanged)
interact.py (render) : INTERACT: 513 fired, 513 ok, 0 failures across 27 screens  (unchanged)
```

## Fence audit
- Only file changed: `tools/pseudokotlin/oracle.py` (one edit: construct instance inside try) + this
  report. No edits to transpiler/runtime/WFL sources. No per-name special cases.
