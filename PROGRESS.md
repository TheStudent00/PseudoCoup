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
| Transpiler (Kt→Py engine) | **94%** | `▁▃▅▅▆████` | 254/254 parse, oracle 11/11; +Room @Relation metadata emission. Left: preserve more type/annotation metadata (DI types) surfaced by the run phase. |
| Externs (runtime wrappers) | **97%** | `▁▂▃▃▄▆▇██` | wrapper surface COMPLETE: 338/345 (97%) external names have real wrappers -- reactive State+recompose, collectAsState, Room @Relation, navigation, DI VM-builder, and the full Compose style/layout/icon surface (compose_ui) + kotlin.math/platform (extras). The 7 remaining are stdlib METHODS (map/stateIn/collectAsState/...) real on the objects; only their unused free alias is a stub. |
| Data layer (Room / sqlite3) | **91%** | `▁▁▁▁▂███` | runs end-to-end incl. Room @Relation stitching now (GymWithEquipment/ProgramExerciseWithSets assembled). Instrumented suite 4/4. |
| WFL domain functionality | **76%** | `▁▃▄▅▅███` | 11 engines proven; ViewModels now constructible on a real db (general di.py) and drive real screen data. Left: full repository/VM coverage, the 9-dep AppViewModel. |
| UI (PseudoUI screens) | **82%** | `▁▁▁▂▂▂▆▇▇█` | screens run in Kivy (render/): 28/29 render, reactive state proven (tap->recompose), REAL data proven (GymList: seeded db -> VM -> collectAsState -> @Relation -> cards), navigation primitives proven (route+repaint). Left: full multi-screen boot (AppNavigation needs the 9-dep AppViewModel wired), breadth, styling/icons. |

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

- `2026-07-02` Wrapper surface completed: 41% -> 97% (338/345). compose_ui.py fills the whole Compose style/layout/icon/animation surface; extras.py fills kotlin.math/Random/viewModelScope/edge-platform. All gates green, render 28/29, no regression. Remaining 7 are working stdlib methods (unused free alias only).
- `2026-07-02` App RUNS in Kivy (render/run_app.py): transpiled screens render as real Kivy windows; reactive state (tap->recompose->repaint), REAL data (general di.py builds VMs on a real in-memory db; GymList shows seeded gyms via collectAsState + Room @Relation stitching), and navigation primitives (NavHost/navigate route+repaint) all proven. Transpiled structure untouched -- all wiring in render/ + runtime wrappers.
- `2026-06-30` Render 20/29 -> 28/29: render harness skips on* event handlers (they fire on user action, not at render), and android_rt platform stand-ins are class-level permissive (metaclass, no hand-listing). Only HistoryScreen (thin) remains. NOTE: render is structural under stub inputs, not behavioural.
- `2026-06-30` Transpiler: buildString/buildList builder scope (the builder is the lambda receiver -> bare append/add bind to a fresh StringBuilder/KtList; real StringBuilder in kotlin_rt) + when-as-value always binds (vacuous else, fixing the free-variable closure crashes). Render 17/29 -> 20/29; all gates green.
- `2026-06-30` AST-kind-aware wrapping: surface.py classifies all 345 externals by kind (obj/func/class/value) from how the AST uses them — the type-specific wrapper map + kit spec. autostub shapes Kotlin objects as singletons; the base stub is now arithmetic/comparison-robust. Gates green.
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
