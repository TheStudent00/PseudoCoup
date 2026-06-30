# WFL → Python — progress

Measured by re-running the gates (`tools/pseudokotlin/track.py`) — never hand-typed. A 🔴 gate or a falling
sparkline is a real regression, not a stale doc. (Browser version with trend charts: `PROGRESS.html`.)

As of 2026-06-30.

## Gates + momentum (measured)

| metric | now | trend | gate |
|---|---|---|---|
| Parse — all .kt transpile + compile | **278/278** | `▄▄` | 🟢 |
| Load — non-UI domain imports clean | **167/167** | `▁█` | 🟢 |
| UI — files load (inert via autostub) | **87/87** | `▄` | 🟢 |
| Logic — engine methods match Kotlin | **160/160** | `▄▄` | 🟢 |
| Data — instrumented DB tests green | **4/4** | `▄▄` | 🟢 |
| External gaps — used but unwrapped | **0** ↓better | `▄▄` | 🟢 |
| Grammar kinds unrouted — the worklist | **0** ↓better | `▄▄` |  |

## Major objectives — estimated completion (chronological)

Estimates (judgment, anchored to the measured gates above), traced across the project's milestones.

| objective | est. | trend (Jun 20→29) | what's left |
|---|---|---|---|
| Transpiler (Kt→Py engine) | **93%** | `▁▃▅▅▆██` | grammar fully routed, 278/278 parse, oracle 11/11; recent: numeric fidelity, $name interp, receiver-lambdas, braceless-loop bodies, nested-lambda hoist, companion members. Left: edge idioms surfaced by the UI phase. |
| Externs (runtime wrappers) | **90%** | `▁▂▃▃▄▇█` | every external name now BINDS via autostub — non-UI real wrappers, UI inert stubs. Left: make the UI stubs real (point Button/Text/… at the kit). |
| Data layer (Room / sqlite3) | **90%** | `▁▁▁▁▂██` | runs end-to-end — @Entity/@Dao/@Database, CRUD + transactions, backup round-trip, and migration replay + schema validation. The instrumented suite is COMPLETE (4/4). Left: runtime edge cases as more app code exercises it. |
| WFL domain functionality | **73%** | `▁▃▅▅▅██` | 11 engines proven (160 methods match Kotlin), repositories run on the data layer. Left: full repository coverage, feature surfaces (backup, etc.). |
| UI (PseudoUI screens) | **62%** | `▁▁▂▂▂▃█` | transpiled Kotlin screens now RENDER a structural UI tree (headless Compose, runtime/compose.py) — real text + enum-driven widgets. Left: styling (Modifier/colors), reactive state (collectAsState→re-render), and a pixel kit (Flutter/Kivy). |

## On-deck — next sub-tasks (top = next)

1. **[ui]** Clear the render long-tail  ← next
  - the ~12 non-rendering screens are mostly receiver-lambda builders (`buildString`/`buildList` — extend the apply/with/run support) + a few harness artifacts (Stub passed for a param the screen does arithmetic on — real calls pass real args). Push render OK toward 29/29.
1. **[ui]** Reactive bridge + styling
  - `collectAsState`/`remember` → real state that drives re-render (today they stub, so state-branching bodies render thin); thread `Modifier`/colors through the tree. This is rungs 3→4 for the UI.
1. **[ui]** Point the tree at a pixel kit
  - the headless tree is neutral; render it on the PseudoUI Flutter/Kivy kit for actual pixels + goldens. (Architecture call.)
1. **[transpiler]** AST-kind-aware stubs (your refinement)
  - tag each external name by kind from the AST; shape the stub to match. Permissive floor stays the fallback.
1. **[domain]** Broaden runnable coverage
  - point the oracle at more repositories / use-cases. Running real code keeps surfacing real bugs.
1. Headless Compose (`runtime/compose.py`): a `@Composable` emits a UI tree; registered so autostub serves Column/Text/Button real and stubs styling. Transpiled ReportForm → full form (intro, fields, 3 live BugSeverity buttons, Send). 17/29 screens render.
1. Auto-stub floor: one front door binds every external (real → builtin → inert stub); ALL 254 files load (87/87 UI, was 0). Platform/DI glue blessed real so extern stays 0. UI-load is now a measured gate.
1. Transpiler fixes the render surfaced: Unit, inline fully-qualified-ref collapse, qualified extension receivers, const-hoist + nested-class-default late-binding.

## Milestones — what landed, when

- `2026-06-30` 17/29 transpiled screens render via headless Compose (Unit + inline fully-qualified-ref collapse). LogCardioScreen = 82 nodes. Remaining are receiver-lambda builders + harness stub-arg artifacts; all gates green.
- `2026-06-30` UI RENDERS: runtime/compose.py (headless Compose) — a @Composable emits a UI tree. The transpiled ReportForm renders to Scaffold/Column/Text/SegmentedButton/Button with real text and live BugSeverity-driven options. Rung 3 for the UI via the transpiler path; all gates green.
- `2026-06-30` Auto-stub floor: one front door binds EVERY external name (real wrapper → builtin → inert stub) → ALL 254 foundation files load, 87/87 UI (was 0), zero NameErrors. UI is no longer a transpiler problem — only kit-wiring remains.
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
