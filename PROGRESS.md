# WFL → Python — progress

Measured by re-running the gates (`tools/pseudokotlin/track.py`) — never hand-typed. A 🔴 gate or a falling
sparkline is a real regression, not a stale doc. (Browser version with trend charts: `PROGRESS.html`.)

As of 2026-06-29.

## Gates + momentum (measured)

| metric | now | trend | gate |
|---|---|---|---|
| Parse — all .kt transpile + compile | **278/278** | `▄` | 🟢 |
| Load — non-UI domain imports clean | **165/165** | `▄` | 🟢 |
| Logic — engine methods match Kotlin | **160/160** | `▄` | 🟢 |
| Data — instrumented DB tests green | **4/4** | `▄` | 🟢 |
| External gaps — used but unwrapped | **0** ↓better | `▄` | 🟢 |
| Grammar kinds unrouted — the worklist | **0** ↓better | `▄` |  |

## Major objectives — estimated completion (chronological)

Estimates (judgment, anchored to the measured gates above), traced across the project's milestones.

| objective | est. | trend (Jun 20→29) | what's left |
|---|---|---|---|
| Transpiler (Kt→Py engine) | **92%** | `▁▃▅▅▆█` | grammar fully routed, 278/278 parse, oracle 11/11; recent: numeric fidelity, $name interp, receiver-lambdas, braceless-loop bodies, nested-lambda hoist, companion members. Left: edge idioms surfaced by the UI phase. |
| Externs (runtime wrappers) | **74%** | `▁▂▃▄▅█` | non-UI externals 100% wrapped (0 real gaps) via resolve + registry. Left: the UI external surface (compose / hilt / nav). |
| Data layer (Room / sqlite3) | **90%** | `▁▁▁▁▂█` | runs end-to-end — @Entity/@Dao/@Database, CRUD + transactions, backup round-trip, and migration replay + schema validation. The instrumented suite is COMPLETE (4/4). Left: runtime edge cases as more app code exercises it. |
| WFL domain functionality | **72%** | `▁▃▅▅▆█` | 11 engines proven (160 methods match Kotlin), repositories run on the data layer. Left: full repository coverage, feature surfaces (backup, etc.). |
| UI (PseudoUI screens) | **18%** | `▁▃▄▆▇█` | generator tooling + structural work exist but are set-aside / unvalidated into the foundation. The plan's step 2–3. |

## On-deck — next sub-tasks (top = next)

1. **[domain]** Broaden runnable coverage  ← next
  - point the oracle at more of the foundation (more repositories / use-cases / unit tests). Running real code is what surfaced the braceless-loop, nested-lambda, and companion-member bugs; more of it will find more. High yield, low risk.
1. **[ui]** Bring one screen into the foundation
  - the plan's step 2: validate it keeps structure/connectivity against the ledger; paint-by-numbers a fresh one if the salvaged part is mangled. Confirm the approach first (user's architecture call).
1. **[extern]** Default-import stdlib names
  - grow kotlin_rt as they surface (several landed with backup/migration: runCatching, synchronized, trimIndent, trimMargin). Low priority, demand-driven.
1. **[multi-target]** `@<target>_extern` tag drives the per-language wrapper registry
  - declare an external once, resolve it per target (PseudoCoup-side).
1. **[numeric]** Unsigned wrappers (UInt/ULong) + `ushr`
  - DEFERRED: unused anywhere in the foundation today (0 references). Do it only if a UI/new file needs it.
1. Data layer COMPLETE (4/4 instrumented): MigrationTest green — MigrationTestHelper over sqlite3 recreates each old schema from Room's exported JSON, replays all 39 migrations (v1/v17/v24/v30 → v40), validates the result. Plus the backup round-trip (3/4) before it.
1. 4 general transpiler bugs surfaced by running that real code: braceless-loop bodies dropped (74 files), nested-lambda hoist scope, companion-member access, bare `$name` interpolation. Plus receiver-lambda scope functions (apply/with/run).

## Milestones — what landed, when

- `2026-06-29` Data 3/4 → 4/4 (instrumented suite COMPLETE): MigrationTest green — a MigrationTestHelper over sqlite3 recreates each old schema from Room's exported JSON, replays all 39 migrations (v1/v17/v24/v30 → v40), and validates the result.
- `2026-06-29` Data 2/4 → 3/4: BackupRepositoryRoundTripTest runs green (export → clearAllTables → import over a sqlite3 Cursor + org.json). Surfaced + fixed 3 transpiler bugs: braceless-loop bodies were dropped (74 files), nested-lambda hoist scope, companion-member access.
- `2026-06-29` Transpiler: receiver-lambda scope functions (apply/with/run) — a body's bare member calls/assignments bind to the receiver; the apply blocker for the backup test is gone.
- `2026-06-29` Transpiler: bare `$name` string interpolation (47 foundation files had literal `$name` in SQL/log strings — now interpolated).
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
