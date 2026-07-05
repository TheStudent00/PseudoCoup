# WFL → Python — progress

Measured by re-running the gates (`tools/pseudokotlin/track.py`) — never hand-typed. A 🔴 gate or a falling
sparkline is a real regression, not a stale doc. (Browser version with trend charts: `PROGRESS.html`.)

As of 2026-07-05.

## Gates + momentum (measured)

| metric | now | trend | gate |
|---|---|---|---|
| Parse — all .kt transpile + compile | **280/281** | `▁▁▅██` | 🔴 |
| Load — non-UI domain imports clean | **167/167** | `▁████` | 🟢 |
| UI — files load (inert via autostub) | **87/87** | `▄▄▄▄` | 🟢 |
| Logic — engine methods match Kotlin | **86/86** | `███▁▁` | 🔴 |
| Data — instrumented DB tests green | **4/4** | `▄▄▄▄▄` | 🟢 |
| External gaps — used but unwrapped | **0** ↓better | `▄▄▄▄▄` | 🟢 |
| Grammar kinds unrouted — the worklist | **0** ↓better | `▄▄▄▄▄` |  |
| Layout fidelity — matches real Compose (±3% of display) | **377/377** | `▁██` |  |

## Major objectives — estimated completion (chronological)

Estimates (judgment, anchored to the measured gates above), traced across the project's milestones.

| objective | est. | trend (Jun 20→29) | what's left |
|---|---|---|---|
| Transpiler (Kt→Py engine) | **97%** | `▁▃▅▅▆█████` | 254/254 parse, oracle 11/11. Now preserves: types, generics, inheritance, data-class copy/equality, trailing-lambda slots, safe-call scope fns, reified filterIsInstance, when-val bindings, const-as-static. Left: whatever running the rest surfaces. |
| Externs (runtime wrappers) | **97%** | `▁▂▃▃▄▆▇██` | wrapper surface COMPLETE: 338/345 (97%) external names have real wrappers -- reactive State+recompose, collectAsState, Room @Relation, navigation, DI VM-builder, and the full Compose style/layout/icon surface (compose_ui) + kotlin.math/platform (extras). The 7 remaining are stdlib METHODS (map/stateIn/collectAsState/...) real on the objects; only their unused free alias is a stub. |
| Data layer (Room / sqlite3) | **91%** | `▁▁▁▁▂███` | runs end-to-end incl. Room @Relation stitching now (GymWithEquipment/ProgramExerciseWithSets assembled). Instrumented suite 4/4. |
| WFL domain functionality | **76%** | `▁▃▄▅▅███` | 11 engines proven; ViewModels now constructible on a real db (general di.py) and drive real screen data. Left: full repository/VM coverage, the 9-dep AppViewModel. |
| UI (PseudoUI screens) | **96%** | `▁▁▁▂▂▂▅▆▆▇▇██` | the FULL walk is green AND styling flows: the wrapper records (Modifier chain ops, fonts, spacing, alignment as real distinct values), the kit applies (padding/size/weight/spacing/font/halign). sample_styled_logcardio.png. Left: layout polish (row-height/weight overlaps), deeper interaction walks, colors/theming. |

## On-deck — next sub-tasks (top = next)

1. **[fidelity]** 305/322 components within tolerance, 25 of 28 screens at 100% (the original 20 all hold). This round's five general fixes: (1) differ pairing order  ← next
  - repeated texts' below-fold zero-bound compose copies stole visible kivy twins (ProgramEditor's 13-week roadmap); visible-first pairing on BOTH sides + "invisible in EITHER engine" now covers off-right (horizontal scroll) and zero-area, not just below-fold. (2) buildAnnotatedString was an autostub — now a transpiler builder scope (like buildString) + real AnnotatedStringBuilder; the MACROCYCLE headers render. (3) The dump's fixed 2.6s settle read geometry mid-flight under xvfb (labels thousands of px from correct parents — this WAS the "unmounted twin" 100x100 mystery, timing not a phantom tree); replaced with settle detection (two identical consecutive geometry snapshots). (4) ListItem was stacked as a column (trailing IconButton under the text: +8px per row, no 16dp inset); now a real M3 row (leading | overline/headline/supporting | trailing, 56/72/88 min heights). (5) fidelity.py gradle now --max-workers=1 -Xmx2g (RAM crash guard). Results: ProgramEditor 0/34→31/32, ExercisePicker 6/46→26/26.
1. **[fidelity]** 373/377 (98.9%), 26/28 screens at 100%. Second wave this round (3 general fixes + 2 harness fixes, the last three delegated to Opus subagents under tight briefs): (1) ListItem M3 row + Box fill-width propagation in _zstack (exec table columns spread; 8/31→28/31). (2) Compose-suite hermeticity: per-test Room executors in the generated assembler
  - the leak was contention on the JVM-static ArchTaskExecutor pool delaying ProgramEditor's first flow emission past the dump (3-test conjunction, bisected). (3) Session fixtures pin startedAt/completedAt to the fixed instant on BOTH engines (SessionDetail 14/14). (4) Transpiler wave from exec-screen diagnosis, all general: forEach/forEachIndexed with bare non-local return lower to real for loops; `!f(a,b)` unary-on-callee parse quirk; extension PROPERTIES patch as @property with sibling+collection-API receiver members; suspend relation DAO queries return values not Flows; imports count as known free names (builder-scope misbinding); lambda scopes carry body locals (nonlocal emission); KtList.mapIndexedNotNull; Room relation rows are KtList.
1. **[fidelity]** MILESTONE: 377/377
  - 100% of every component on ALL 28 measurable screens. Closers: (1) 12sp SemiBold shaper band specimen-derived (SemiBold widening is size-dependent: 1.006 at <=12sp vs 1.042 at 24sp) — ProgramEditor 32/32. (2) TextFieldValue was an inert stub destroying field values at construction — now a real class + recorder unwrap; Modifier.size(width=,height=) keyword form honored — WorkoutExecution 31/31. (3) ProgramEditor compose dump anchored on the read-only branch text (the stateIn initial value renders the editable branch until Room emits; executor isolation alone didn't close the race).
1. **[fidelity]** COVERAGE COMPLETE (verified exhaustive): the app has 29 top-level Screen composables; 28 measured at 100%, DebugPanel is the sole intentional skip (dev-only; SAF launchers need a real Activity). The geometry gauge has nothing left to measure
  - next fidelity work is behavioral/visual, not structural.
1. [fidelity] Sanctioned non-general bridges (user-approved as engine/font-specific, all specimen-pinned): shaper width calibration by size/weight band, and emoji advance = 1.28 x fontSize. Everything else remains general.
1. **[fidelity]** SPECIMEN gate is live in fidelity.py (synthetic, not counted, fail-loud): the text-metric rules (natural single-line stacking; letterSpacing widths) are DERIVED from dumpSpecimen. Extend it when a new metric question appears
  - never infer from mixed app screens.
1. **[ui]** Paint layer STARTED (two delegated slices): (1) kit paint mechanism
  - canvas.before fill/border from recorded background/clip/border ops + M3 surface roles + text color, all resolvers stub-guarded (unresolved = no paint, never invented). (2) Runtime color table real: Color (packed Int32 masked to unsigned), RoundedCornerShape/CircleShape radii, light/darkColorScheme, MaterialTheme.colorScheme resolving through the app's installed theme; Color.Unspecified stays an unresolvable sentinel. Geometry gate held 377/377 both times. Shots in layout_inspect/shots/. Pass 2 done: top-bar surface role, M3 button/chip role map, selected-chip rule; text contrast was a stale-shot artifact (already live). Pass 3: icons DONE — real MaterialIcons TTF + shipped codepoints from the OS package (36/36 app icon names; unmapped stays empty, never a wrong glyph). Remaining paint polish: elevation-tint for the white-on-white top bar (mechanism decision for the user), text-field notch/focus tint, chip elevation. NOTE for next session: system icon font is an OS package dependency (fonts-material-design-icons-iconfont) — consider vendoring into render/assets with user approval for portability.
1. [ui] Popups DONE: excluded from layout (closed) + real overlays in the running app (open): presence=open for dialogs/sheets, expanded-flag for menus, tap-outside dismisses through the recorded handler; measurement path isolated (OVERLAYS_ENABLED, run_app-only). Proof shot: layout_inspect/shots/popup_proof.png.
1. **[ui]** Scaffold innerPadding inset + Modifier order (padding-before-size vs after)
  - minor, after the big rows.
1. **[behavior]** KOTLIN TEST SUITE PASSES IN PYTHON: 160/160 across all 11 app test classes (9 engines + PathDefinition + SampleProgramData) via new `run_kotlin_tests.py`
  - method counts match Kotlin @Test counts exactly, zero new transpiler fixes needed (rendering-round fixes carried the domain). Named limitation: oracle.py --all still aborts on an unrelated corpus test (java.util.TimeZone unshimmed). Report: DevComms/kotlin_tests_oracle.md.
1. **[behavior]** Interaction oracle LIVE and CLEAN (`render/interact.py`): fires every recorded handler on every destination from a fresh seeded DB + fresh compose per handler. First sweep found 15 failures in 10 root-cause groups; fix wave 1 (delegated) closed all app-side groups with general fixes: (1) cross-file trailing-lambda slot binds to the callee's real last param via a build pre-pass registry; (2) new kstrext CharSequence-extension dispatcher (str gets Kotlin String.filter/etc.) + Char predicate mapping; (3) bare stdlib calls on extension `this` routed through receiver rewrite; (4) KtMap.maxByOrNull/minByOrNull/maxWithOrNull; (5) BIG ONE
  - remember/slot table was keyed by raw ordinal so conditional content shifted later slots onto foreign values; re-keyed by call site + occurrence index (Compose's positional memoization), hardening State app-wide. Instrument-side: recorder keeps the typed TextFieldValue in props; probe mirrors the value's type. NOW: 513 fired, 513 ok, 0 failures, 27 screens; kotlin tests 160/160; geometry 377/377 — all three gates re-verified together. Reports: DevComms/interaction_oracle.md, interact_fix_wave1.md. Report: DevComms/interaction_oracle.md.
1. **[transpiler]** .kt line map
  - emit a py-line→kt-line sidecar during generation so the layout inspector links each component to its exact Kotlin line (it has file-level links today).
1. **[domain]** Broaden runnable coverage
  - point the oracle at more repositories / use-cases.
1. History renders a real session card, byte-identical text to compose — the instrument caught 4 CONTENT bugs: Kotlin printf-format (.format/String.format) transpiled to brace-format (silent template passthrough), TemporalAdjusters stubbed (week starts wrong), java date patterns' quoted literals mangled ('at' -> 'AMt'), and Int32 overflow inside timedelta (plusDays(6) == -1 day). All fixed in transpiler/runtime; 254/254 regenerated.
1. 4 of 5 screens at/near-perfect: GymList 7/7, LogCardio 23/25, Exercises 7/7, Today 3/3; Settings 22/44. One session took the gauge 24/39 → 62/86 (5 screens) via: M3 slot order, class heights/insets, real line-height stacking (app Typography honored end-to-end), popups excluded from layout, harness renders inside the app theme, loader same-package shadowing (Kotlin visibility), real Font/FontFamily + variable-font weight instancing, off-viewport differ rule.
1. Input fields render their slot subtrees: a node with text AND children is a field container (value as child label), not a leaf — one fix removed the 100px stepper block AND the "Notes (optional)" MISS. BasicTextField dropped from the 56dp rule (it's foundation, undecorated); empty Box collapses instead of Kivy's 100x100 default. Save Δ26.9→0.2.
1. Layout-fidelity instrument: LayoutDumpTest (real Compose boxes, headless JVM) + inspect_layout JSON + layout_diff (%-of-display, tolerance band) → per-screen fidelity %, now a measured gauge (`fidelity.py`).
1. Layout inspector (`layout_inspect/*.html`): per component — the code line that created it (file:line, .kt path) ‖ declared shape ‖ live computed box.
1. Compose measure/place reconstructed on Kivy: wrap-by-default, Box z-stack, arrangement spacers, Scaffold slot framing + FAB float, fill-vs-scroll reconciliation, weight-on-parent-axis, top-pack columns (Kivy bottom-packs spare space — measured), M3 type scale + TopAppBar/icon-button spec geometry, `then`-chain splicing, Spacer(weight).
1. Theme tokens live: real CompositionLocal — WflTheme.tokens.* resolve to real dp values (24 files move together).

## Milestones — what landed, when

- `2026-07-02` Styling pipeline live: Node.props + recording Modifier + real style constants (wrapper records) -> kivy_kit applies padding/dims/weight/spacing/fonts/alignment. Spaced chip rows, padded text, real selector values on screen. Gates green, walk 16/16.
- `2026-07-02` FULL WALK GREEN: onboarding end-to-end (41 real steps: calibration, gym, equipment catalog, path, program) -> today -> every destination renders with real data -> real card-tap into gym_editor. Fixed en route: LaunchedEffect runs (slot-backed), per-destination slot scoping, implicit-it enclosing capture, dp/sp number properties, real DayOfWeek display names, ifBlank/ifEmpty. All gates green.
- `2026-07-02` THE APP RUNS IN KIVY: full boot (AppNavigation) -- real onboarding on fresh install, the navigation courier (route-pattern matching -> SavedStateHandle) delivers which-item arguments, hiltViewModel is per-call with its declared type, natural flow proven headless AND in a window (sample_app_boot_onboarding.png). render 29/29, VMs 19/31, real-data 16/29, all gates green.
- `2026-07-02` Per-file namespaces land (loader.py, Kotlin file-visibility; class-body lookups pre-bound) -- all name-collision victims recover. Data classes get copy/value-equality. render 29/29 HONEST (strict error surfacing), screens with REAL data 16/29, VMs clean 18/31, all gates green, 0 loader gaps.
- `2026-07-02` Five general causes fixed in one pass: string->number conversion family (real kotlin parse rules), real SavedStateHandle (which-item holder), real app storage (files+prefs as local folder/JSON), compose error-swallowing removed (render gate honestly 28->25: 4 hidden failures exposed, 1 fixed same-pass), when-val subject binding + is-checks on object singletons. Screens with REAL data 9->11, VMs clean 14/31. Named next cause: one-namespace loader collisions (per-file namespaces).
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
