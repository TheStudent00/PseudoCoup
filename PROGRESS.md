# WFL → Python — progress

Measured by re-running the gates (`tools/pseudokotlin/track.py`) — never hand-typed. A 🔴 gate or a falling
sparkline is a real regression, not a stale doc. (Browser version with trend charts: `PROGRESS.html`.)

As of 2026-06-29.

## Gates + momentum

| metric | now | trend | gate |
|---|---|---|---|
| Parse — all .kt transpile + compile | **278/278** | `▄` | 🟢 |
| Load — non-UI domain imports clean | **165/165** | `▄` | 🟢 |
| Logic — engine methods match Kotlin | **160/160** | `▄` | 🟢 |
| Data — instrumented DB tests green | **2/4** | `▄` | 🟢 |
| External gaps — used but unwrapped | **0** ↓better | `▄` | 🟢 |
| Grammar kinds unrouted — the worklist | **0** ↓better | `▄` |  |

## On-deck — next sub-tasks (top = next)

1. **[data]** BackupRepositoryRoundTripTest  ← next
  - build the backup feature surface (column-introspective JSON dump/restore engine + a Cursor API), and fix the stale constructor arg in the Kotlin copy. Moves the data metric 2/4 → 3/4.
1. **[data]** MigrationTest
  - wire Room's MigrationTestHelper (schema-version test infrastructure). Moves data 3/4 → 4/4.
1. **[numeric]** Unsigned wrappers (UInt/ULong) + `ushr`
  - the one numeric class still bare; closes the last fidelity gap in runtime/numbers.py.
1. **[extern]** Default-import stdlib names (e.g. `runCatching`)
  - a known gap class the extern checklist doesn't track (it lists explicit imports only); grow kotlin_rt as they surface.
1. **[ui]** Bring one screen into the foundation
  - validate it keeps structure/connectivity against the ledger; paint-by-numbers a fresh one if the salvaged part is mangled. This is the plan's step 2.
1. **[multi-target]** `@<target>_extern` tag drives the per-language wrapper registry
  - declare an external once, resolve it per target (PseudoCoup-side; the inference/explicit convergence noted in the architecture).

## Milestones — what landed, when

- `2026-06-29` Measured dashboard (track.py): gates re-run on demand, trend charts + on-deck queue.
- `2026-06-29` Numeric fidelity (2/2): declared-type coercion at param/constructor/val boundaries (literal-free chains carry width).
- `2026-06-29` Numeric fidelity (1/2): fixed-width wrappers emitted at literals (Int32/Int64/Float32).
- `2026-06-29` Data layer RUNS end-to-end — sqlite3-backed Room; the project's own DAO/txn instrumented tests pass headless.
- `2026-06-29` resolve phase + wrapper registry → real imports emitted (load ≠ run closed; 0 non-UI gaps).
- `2026-06-28` SharedFlow-nav done; exercise_detail remainder scoped per-screen.
- `2026-06-27` UI sizing/positioning extractor (ui_ledger.py) + samples.
- `2026-06-26` Whole WFL app transpiles → WFL_MixingCenter (transpile_app.py); PROJECT_MAP corrected.
- `2026-06-25` Connectivity-checked reuse workflow is real and tooled (DevComms log_48).
- `2026-06-20` Project start — KtToPy transpiler scaffold (parse → map handlers).

## Orientation

The **foundation** is the 1:1 Python **KtToPy** produces from the Kotlin copy (`WFL_MixingCenter/*.py`); the
one goal now is to complete the transpiler so it is solid. Pipeline: parse → resolve (classify every name) →
map (wrap externals by origin) → generate (code + imports). Narrative detail lives in `DevComms/` logs.
