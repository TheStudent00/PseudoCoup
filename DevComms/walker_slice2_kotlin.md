# WALKER slice 2 of 3 — the KOTLIN recorder

**STATUS: UNEXECUTED.** No Gradle/JVM/Android SDK is available in the authoring sandbox. Everything
below was written by reading the real Kotlin sources closely (imports, signatures, package names, DAO
methods, entity constructors) and cross-checking every non-obvious Compose-test/org.json API against
external documentation, but **nothing was compiled or run**. Compile/run happens on the user's machine —
see "HOST RUN INSTRUCTIONS" below. Treat the new test file as a careful, reviewed first draft, not a
verified artifact.

## Deliverables

- `WFL/app/src/test/java/com/sara/workoutforlife/walk/WalkRecorderTest.kt` (new file, test sources only)
- `WFL/app/src/main/java/com/sara/workoutforlife/navigation/AppNavigation.kt` (one additive app-code
  change — see "App-code touch" below)

Neither file was committed, per the task instructions.

## What the test does

`WalkRecorderTest.walkApp()`:
1. Seeds a fresh in-memory Room `WorkoutDatabase` with the SAME rows the Python walker's
   `run_app.build_app_composition` seeds (a completed-onboarding `UserEntity`, one active `GymProfileEntity`,
   one `CardioSessionEntity` at the fixed epoch `1718438400000L`), then calls
   `ExerciseRepository.seedIfNeeded()` / `SampleProgramRepository.seedIfNeeded()` — mirroring
   `LayoutDumpAllTest.kt`'s own fixture values verbatim so both Kotlin test suites and the Python walker
   start from the same DB state.
2. Mounts the REAL `AppNavigation` composable (not a bare screen, unlike every existing Kotlin test) via
   `rule.setContent { WorkoutforlifeTheme(darkTheme = false) { AppNavigation(...) } }`, using
   `Assembler.build(AppViewModel::class.java)` (the existing reflective constructor-picker from
   `LayoutDumpAllTest.kt`'s `Assembler.kt`) to hand-wire `AppViewModel`'s 9 constructor dependencies —
   every one of them is a concrete class reachable from `WorkoutDatabase` + `Context` + `TimeProvider`, so
   the existing `Assembler` resolves the whole graph with no code changes to it.
3. Waits past `AppNavigation`'s `onboardingCompleted == null` splash race (same race class as the
   "ProgramEditor stateIn race" documented in `LayoutDumpAllTest.kt` lines 50–58) using `waitUntil` polling,
   not a single `waitForIdle()`.
4. Walks the live Compose semantics tree breadth-first: at each discovered state, enumerates every
   interactive node in document (pre)order, drives each one for real via
   `SemanticsNodeInteraction.performClick()` / `.performTextInput("42")` (never invoking a handler lambda
   directly — same "drive the real wiring" law `walker.py`'s `real_tap()` follows), waits for idle, and
   records the resulting state + edge.
5. Recovery policy: fresh reboot per edge (new in-memory DB + new `rule.setContent{}` + replay the
   ordinal-path from boot) — the exact same policy `walker.py`'s module docstring specifies under
   "RECOVERY", for the same reason (no cross-edge state bleed).
6. Output: `{"meta": {...}, "states": {state_id: STATE}, "edges": [EDGE, ...]}`, byte-structurally the
   same top-level shape as `render/walker.py`'s output, written to `build/walks/kt_walk.json`
   (checkpoint file `build/walks/kt_walk_progress.json`), bounded by `-Dwalk.steps=N` /
   `-Dwalk.resume=true` / `-Dwalk.reset=true` JVM system properties (read via `System.getProperty`, since
   `-D` flags are the natural Gradle-side equivalent of `walker.py`'s `--steps`/`--resume`/`--reset` CLI
   flags — there is no existing `System.getProperty` precedent in this repo, only `System.getenv`, so
   this is a new but minimal convention, documented inline in the test).

## App-code touch (LAW-compliant)

`AppNavigation.kt` builds its own internal `NavController` via `rememberNavController()`
(`AppNavigation.kt:250`) with **no external accessor** — nothing in the existing code exposes the current
route to a caller. The walker needs this (the direct analogue of `walker.py`'s
`self.nc = navigation.last_controller`). The single change:

```kotlin
fun AppNavigation(
    appViewModel: AppViewModel = hiltViewModel(),
    deepLinkRoute: StateFlow<String?> = MutableStateFlow(null),
    onDeepLinkConsumed: () -> Unit = {},
    // Test-only hook (default no-op, so every production call site is byte-for-byte unaffected): ...
    onNavControllerReady: (androidx.navigation.NavController) -> Unit = {},
) {
    ...
    val navController = rememberNavController()
    LaunchedEffect(navController) { onNavControllerReady(navController) }
    ...
```

This is purely additive: a new optional trailing parameter with a default no-op lambda. The sole
production call site, `MainActivity.kt:38`, does not pass this argument and is therefore completely
unaffected — same composable output, same behavior, same recomposition graph (the new `LaunchedEffect`
keyed on `navController` fires the no-op once and never recomposes anything). This satisfies the LAW's
"may be adjusted ONLY if appearance/function is unchanged" clause. No other file under `app/src/main` was
touched.

## Self-review checklist (every referenced API checked against the real source)

| # | Reference | Checked against | Result |
|---|---|---|---|
| 1 | `UserEntity` constructor | `WFL/app/src/main/java/com/sara/workoutforlife/data/db/entity/UserEntity.kt` (full class read) | Field names/order/nullability match; `displayName`, `bodyWeightKg`, `onboardingCompleted`, `createdAt`, `updatedAt` have no defaults and are all supplied in the seed call |
| 2 | `UserDao.insertIfAbsent` | `.../data/db/dao/UserDao.kt:24-25`, `@Insert(onConflict = OnConflictStrategy.IGNORE) suspend fun insertIfAbsent(user: UserEntity)` | Matches call site `db.userDao().insertIfAbsent(UserEntity(...))` inside `runBlocking { }` |
| 3 | `WorkoutDatabase.userDao()` | `.../data/db/WorkoutDatabase.kt:110`, `abstract fun userDao(): UserDao` | Confirmed |
| 4 | `WeightUnit.KG`, `WorkoutMode.RPE`, `TrainingExperience.BEGINNER`, `StrengthGainProfile.GRADUAL`, `TrainingRecency.CURRENTLY_TRAINING` | Each enum file under `.../data/model/` | All 5 constant names confirmed to exist exactly as spelled; package `com.sara.workoutforlife.data.model` confirmed |
| 5 | `GymProfileEntity`, `CardioSessionEntity` constructors | Entity class definitions (not just `LayoutDumpAllTest.kt` call sites) | `createdAt`/`updatedAt` on `GymProfileEntity` have no defaults — supplied explicitly; `CardioSessionEntity`'s 18-field constructor matches the exact call in the new test, copied field-for-field from `LayoutDumpAllTest.kt:67-74` |
| 6 | `ExerciseRepository`, `SampleProgramRepository` `.seedIfNeeded()` | `data/repository/ExerciseRepository.kt:98-104`, `SampleProgramRepository.kt:41-45` | Both `suspend fun seedIfNeeded()`, called inside `runBlocking { }`, resolved via `Assembler.build(...)` exactly as `LayoutDumpAllTest.kt:77-80` does |
| 7 | `Assembler` reflective builder | `WFL/app/src/test/java/.../layout/Assembler.kt` (full file read) | `build(cls: Class<T>)` picks the max-arg-count constructor and resolves each param type via `resolve()`; `AppViewModel`'s 9 ctor params are ALL concrete classes (`UserRepository`, `WorkoutSessionDao` [a Room `@Dao` interface — matched by `resolve()`'s `type.simpleName.endsWith("Dao")` branch], `CelebrationRepository`, `ProgramRepository`, `ProgramAdaptationRepository`, `WinRepository`, `NotificationRepository`, `NotificationGenerator`, `CrashReporter`), each in turn resolvable from `WorkoutDatabase`/`Context`/`TimeProvider`/other DAOs — traced the full dependency graph by hand, no unresolved interface anywhere in it |
| 8 | `AppViewModel` constructor | `navigation/AppNavigation.kt:124-134` | 9-arg `@Inject constructor`, matches `Assembler`'s reflective resolution path exactly |
| 9 | `AppNavigation` signature + `Screen.Today.route` | `navigation/AppNavigation.kt:231-238`, `navigation/Screen.kt:5` (`object Today : Screen("today")`) | Confirmed; `onNavControllerReady` inserted as shown above |
| 10 | `NavController.currentBackStackEntry` | External API verification (androidx.navigation source) | `val currentBackStackEntry: NavBackStackEntry?`, distinct from `currentBackStackEntryFlow`; `.destination.route: String?` — confirmed |
| 11 | `createComposeRule()`, `rule.onRoot(useUnmergedTree = true)`, `SemanticsProperties.Text/EditableText/Role`, `getOrNull` | `LayoutDumpTest.kt` / `LayoutDumpAllTest.kt` imports and usage (identical in both) | Direct precedent, reused verbatim |
| 12 | `performClick()`, `performTextInput(String)` on `SemanticsNodeInteraction` | External API verification | Confirmed extension functions in `androidx.compose.ui.test`; **first use in this repo** — no existing precedent, flagged as a risk (see below) |
| 13 | `SemanticsMatcher(description, matcher)` + `rule.onNode(matcher)` | External API verification | Confirmed public constructor `SemanticsMatcher(val description: String, private val matcher: (SemanticsNode) -> Boolean)`; `onNode(matcher: SemanticsMatcher, useUnmergedTree = false)` accepts it directly |
| 14 | `SemanticsActions.OnClick/OnLongClick/SetText/SetProgress/SetSelection` | External API verification (`SemanticsProperties.kt`) | Confirmed `val` properties of type `SemanticsPropertyKey<AccessibilityAction<T>>`; `config.getOrNull(SemanticsActions.OnClick)` is the same access pattern as `SemanticsProperties.Text` |
| 15 | `rule.waitUntil(timeoutMillis = ..., condition = ...)` | External API verification | Actual current signature is `waitUntil(conditionDescription: String? = null, timeoutMillis: Long = 1_000, condition: () -> Boolean)` — calling positionally with just a `Long` would NOT compile; the test file uses the **named** form `waitUntil(timeoutMillis = 10_000) { ... }` throughout, which is safe against this |
| 16 | `org.json.JSONObject` null semantics | External API verification | `put(key, null)` silently REMOVES the key (does not write a JSON null) and `optString(key, null)` NPEs if the key is truly absent — the test file was corrected to use `JSONObject.NULL` explicitly on write and `isNull(key)` explicitly on read for every nullable edge field (`source`, `action`, `destination`, `error`), via two new helpers `edgeToJson`/`edgeFromJson` |
| 17 | Compose BOM version | `WFL/gradle/libs.versions.toml:10`, `composeBom = "2026.02.01"` | Confirmed comfortably new enough for every API used above |
| 18 | Robolectric version / `@Config` | `build.gradle.kts:165` (`org.robolectric:robolectric:4.16"`), `LayoutDumpTest.kt:69-74` | `@RunWith(RobolectricTestRunner::class)`, `@GraphicsMode(GraphicsMode.Mode.NATIVE)`, `@Config(sdk = [35], qualifiers = "w411dp-h915dp", application = android.app.Application::class)` copied verbatim |
| 19 | Dedicated Room executor pattern | `LayoutDumpAllTest.kt:59-62` | Copied verbatim (`Executors.newFixedThreadPool(4)` for both query and transaction executors) — this is the fix for the flow-emission race, see below |

## Walk-policy parity table (walker.py ↔ WalkRecorderTest.kt)

| Policy dimension | `render/walker.py` | `WalkRecorderTest.kt` |
|---|---|---|
| BFS order | FIFO list `prog["frontier"]`, one step = one `replay_and_step` call (walker.py:481-539) | FIFO `ArrayList<Frame>` `frontier`, one step = one `replayTo` + one action (`walkApp()`, BFS loop) |
| Unknown-`n_actions` frame handling | Rotates to back rather than crashing (walker.py ~531-539) | Same: if `frame.nActions == null`, replay once to discover it; if replay fails, `frontier.removeAt(0)` (drop, not crash) |
| `state_id` hash | `sha256(json.dumps({"route":..., "tree_summary":...}, sort_keys=True).encode("utf-8")).hexdigest()` (walker.py:202-204) | Hand-built canonical JSON string with keys pre-sorted alphabetically (`interactive < kind < text`, `route < tree_summary`) fed to `MessageDigest.getInstance("SHA-256")`, hex-encoded — same algorithm, same key ordering, since only this fixed key set ever appears |
| `route` string | `app.nc.currentRoute()` (Kivy nav controller) | `capturedNavController?.currentBackStackEntry?.destination?.route` (captured via the new `onNavControllerReady` hook) |
| Dialog/menu tagging | `"<route>#dialog:<Kind>"` / `"<route>#menu:<Kind>"` from `kivy_kit._active_overlays` (walker.py:216) | **NOT IMPLEMENTED — flagged, not guessed.** Compose has no first-class open-overlay registry analogous to `kivy_kit._active_overlays`; `AppNavigation.kt` only has local `showNotificationPanel`/`showCheckIn`/`showCrashPrompt` booleans gating a `ModalBottomSheet`/`AlertDialog`, with no existing tag convention. `currentRoute()` in the new test always returns the base nav route even when a dialog is open — a real gap, called out below under Risks, deferred to slice 3 rather than invented ad hoc |
| `tree_summary` fields | `{"kind": n.kind, "text": canonicalize_text(...), "interactive": bool(n.handlers)}`, geometry excluded (walker.py:178-187) | `Component(kind, text, interactive)` via `nodeKind()`/`nodeText()`/`nodeInteractive()`; geometry (`boundsInRoot`) never read for this list. **`kind` vocabulary differs by design** — Kivy's `n.kind` is this app's own transpiled Node kind string; Compose has no equivalent field, so `nodeKind()` derives from `SemanticsProperties.Role` (Button/Checkbox/...) or falls back to `"EditableText"`/`"Node"`. Emitted truthfully, not pre-normalized — the vocabulary mapping is explicitly deferred to slice 3 (see code comment) |
| Ordinal enumeration order | Document (pre)order DFS over `n.handlers` dict-insertion order, same walk as `_component_list` (walker.py:225-236) | Document (pre)order DFS over `SemanticsNode.children`, same walk as `componentList()`; one ordinal per node via a fixed action-kind priority (SetText > OnClick > OnLongClick > SetProgress > SetSelection) since Compose has no per-node handler dict to iterate |
| "42" text convention | `interact.py.infer_value()` returns `"42"` for any `on*Change`/`*ChangeFinished` handler on a text-shaped prop (interact.py:159-183) | `TEXT_INPUT_VALUE = "42"`, fired via `performTextInput("42")` whenever the enumerated action kind is `"onValueChange"` |
| Edge structure | `{"source", "action": {"kind","label","handler_kind","ordinal"}, "destination", "error"}` plus an always-present `"unsettled"` bool (walker.py docstring + lines 565-566) | `EdgeRec(source, action, destination, error, unsettled)` → `edgeToJson()` — same 5 keys, `unsettled` always written (currently always `false`; Compose's `waitForIdle()` is a hard synchronous barrier unlike Kivy's cooperative settle loop, so there is no Kotlin-side equivalent "unsettled" signal yet — flagged as a simplification, not a silent gap) |
| Error handling | try/except around the tap; `dest=None`, `error={"type": exc class name, "message": str(e)[:200]}`, never re-raised (walker.py:437-469); hard wall-clock watchdog via `Clock.schedule_once` | try/catch around `performAction`; `destState=null`, `error={"type": e.javaClass.simpleName, "message": e.message?.take(200)}`. **No watchdog/timeout implemented** — Robolectric tests can hang the whole JVM process on a genuine deadlock with no internal recovery; flagged as a risk, not addressed this slice (walker.py's own timeout uses Kivy's `Clock`, which has no Compose/Robolectric analogue readily available) |
| Recovery policy | Fresh process boot + replay ordinal-path from root, per edge (walker.py policy note) | Fresh in-memory Room DB + fresh `rule.setContent{}` + replay ordinal-path from root, per edge (`mountFreshApp`/`replayTo`) — same policy, cheaper primitive (no full process fork, just a new Compose composition + DB) |
| Checkpointing | `walks/py_walk_progress.json`, atomic `os.replace()` after every edge (walker.py:489-494) | `build/walks/kt_walk_progress.json`, write-to-`.tmp`-then-`renameTo()` after every edge — same shape (`states`/`edges`/`frontier`/`visited_state_ids`/`done`), same atomic-rename intent |
| Step bound | `argparse --steps` (default 60), argv captured before Kivy import mutates `sys.argv` (walker.py:132, 654-668) | `System.getProperty("walk.steps")` (default 60), read via `-Dwalk.steps=N` on the Gradle test JVM — no Kotlin-side argv-mutation hazard exists, so no equivalent workaround is needed |
| Output shape | `{"meta": {...}, "states": {id: STATE}, "edges": [...]}`, `json.dump(..., indent=1, sort_keys=True)` (walker.py:668-673) | Same 3 top-level keys via `writeFinal()`; `JSONObject.toString(1)` (org.json's own indent-1 pretty print) — key order is insertion order in org.json, not alphabetically sorted like Python's `sort_keys=True`, a byte-level (not structural) difference, noted for slice 3's diff tool to tolerate |

## Known risks, ranked

1. **HIGH — `AppViewModel` construction via `Assembler` is untested territory.** No existing Kotlin test
   ever constructs `AppViewModel` or calls `AppNavigation(...)`; `Assembler.build()` was designed and only
   ever exercised for simpler, per-screen ViewModels. The dependency graph was traced by hand (§ checklist
   item 7) and looks resolvable, but a genuinely new construction path like this is exactly where an
   unanticipated `@Inject constructor` param (e.g. a `Flow` type, a `CoroutineDispatcher` qualifier
   Assembler's `resolve()` doesn't handle) could throw at runtime. First thing to check on a failed host run.
2. **HIGH — Dialog/menu state tagging is not implemented.** Unlike `walker.py`'s
   `kivy_kit._active_overlays`, there is no general Compose mechanism wired up here to detect an open
   `AlertDialog`/`ModalBottomSheet` and tag its route `"#dialog:Kind"`. The walk will currently treat an
   open dialog's content as invisible (Compose dialogs mount in a separate window not reachable from
   `rule.onRoot()`) or, worse, may simply not enumerate the dialog's own interactive nodes at all,
   silently under-covering states that involve `showNotificationPanel`/`showCheckIn`/`showCrashPrompt`.
   This needs a real design pass (are Compose Dialogs visible to `Robolectric` + `createComposeRule()`'s
   single root at all, or does the test need `rule.onAllNodesWithTag(...)` against a different root, or
   `ComposeTestRule`'s dialog-aware node finders?) before slice 3 can trust dialog coverage. Flagged, not
   guessed, per the task law.
3. **MEDIUM — No watchdog/timeout on a hung step.** `walker.py` has an explicit `Clock.schedule_once`
   watchdog that force-fails a step exceeding 25s and records it as a `TimeoutError` edge, so a genuine
   deadlock never silently hangs the whole walk. `WalkRecorderTest` has no equivalent; a Robolectric
   deadlock (e.g. a coroutine that never completes) would hang the whole JVM test process with no
   recorded edge and no checkpoint saved for that step. Consider wrapping each step in a
   `kotlinx.coroutines.withTimeout`-guarded `runBlocking` or a JUnit `@Test(timeout = ...)` per invocation
   (though the latter kills the whole test, losing the in-progress checkpoint) — needs a host-side design
   decision, not resolved here.
4. **MEDIUM — `performClick()`/`performTextInput()` are first-use APIs in this repo.** Every existing
   Robolectric+Compose test only ever reads the tree (`LayoutDumpTest`/`LayoutDumpAllTest`); none performs
   real input actions. Signatures were verified against external Compose documentation, not against a
   local compile, so subtle version-specific behavior (e.g. `performTextInput` requiring the node be
   already focused, or IME-specific quirks under Robolectric) is unverified.
5. **MEDIUM — `onLongClick` handling is a placeholder.** The test currently calls `performClick()` for
   `onLongClick`-tagged nodes too (no `performTouchInput { longClick() }` precedent exists anywhere to
   copy), explicitly marked `TODO` in the code. If any screen's long-click handler behaves differently
   from its click handler, this under-tests that branch until fixed on the host.
6. **LOW-MEDIUM — one-ordinal-per-node assumption.** `walker.py` enumerates one ordinal per
   `(node, handler_kind)` pair (a node COULD have multiple handlers). The Kotlin side's
   `enumerateInteractive()` picks exactly one action per node via a fixed priority order (SetText > Click
   > LongClick > SetProgress > SetSelection), which happens to be a superset-collapsing simplification —
   correct today only because no current screen's node exposes two of these simultaneously (unverified
   claim, not proven by grep of the actual composables; a reasonable assumption given today's `LayoutDump*`
   coverage, but worth confirming on the host once real screens are walked).
7. **LOW — SemanticsNode identity across recompositions.** `isSameNode()` matches by `SemanticsNode.id`,
   assumed stable across a *within-composition* re-fetch of the tree (used immediately after
   `enumerateInteractive` without an intervening structural change) but NOT held across a full
   recomposition/settle — the code re-enumerates fresh every time before matching, by design, to avoid
   holding stale `SemanticsNode` references, but this pattern itself is unverified against Robolectric's
   actual `id`-stability guarantees.
8. **LOW — checkpoint file key-order mismatch vs Python.** org.json's `JSONObject` preserves insertion
   order rather than alphabetizing keys (unlike Python's `sort_keys=True`), so `kt_walk.json` and
   `py_walk.json` will not be byte-identical even for structurally identical content. Purely cosmetic —
   slice 3's diff tool must parse-then-compare, never byte-compare, which the task's own framing
   ("slice 3 diffs the two JSONs") already implies is necessary regardless.

## HOST RUN INSTRUCTIONS

From `WFL_MixingCenter/WFL/`:

```bash
# First run (fresh walk, capped at 60 steps):
./gradlew :app:testDebugUnitTest --tests "com.sara.workoutforlife.walk.WalkRecorderTest" \
    --rerun -Dwalk.steps=60

# Resume a checkpointed walk (continues from build/walks/kt_walk_progress.json):
./gradlew :app:testDebugUnitTest --tests "com.sara.workoutforlife.walk.WalkRecorderTest" \
    --rerun -Dwalk.steps=60 -Dwalk.resume=true

# Discard any checkpoint and start completely over:
./gradlew :app:testDebugUnitTest --tests "com.sara.workoutforlife.walk.WalkRecorderTest" \
    --rerun -Dwalk.reset=true -Dwalk.steps=60
```

Notes:
- `--rerun` is required because Gradle otherwise caches a green test result and skips re-execution on
  a second invocation with the same inputs.
- Output lands at `WFL/app/build/walks/kt_walk.json` (checkpoint at
  `WFL/app/build/walks/kt_walk_progress.json`), matching the task's requested path. Override the directory
  with `WALK_OUT_DIR` env var if needed (same `System.getenv` convention `LAYOUT_DUMP_DIR` already uses).
- **Expected runtime**: each BFS step does a full fresh `rule.setContent{}` mount (new in-memory Room DB +
  full `AppNavigation` composition + settle), which is considerably heavier than `LayoutDumpTest`'s
  single-screen dumps. Budget roughly 1–3 seconds per step conservatively (Robolectric JVM startup is
  amortized across the whole test run, but Room DB creation + Compose recomposition per edge is not) — a
  60-step walk should complete in low single-digit minutes, but this is an estimate, not a measurement;
  confirm on first host run and adjust `-Dwalk.steps` for CI time budgets accordingly.
- If the very first run hangs or throws during `AppViewModel` construction, see Risk #1 above — start
  there.

### Troubleshooting

- **Robolectric main-looper idling**: if `rule.waitForIdle()` returns before a Room-flow emission has
  actually landed (the "ProgramEditor stateIn race" class of bug — see `LayoutDumpAllTest.kt:50-58`),
  symptoms look like: `currentRoute()` stuck on `"unknown"`, or the walk silently starting from a stale
  screen. Mitigation already applied: (a) each `mountFreshApp` uses its OWN dedicated
  `Executors.newFixedThreadPool(4)` Room executor rather than sharing the JVM-static `ArchTaskExecutor` IO
  pool a leaked prior ViewModel might be parked on; (b) `mountFreshApp` polls
  (`rule.waitUntil(timeoutMillis = 10_000) { ... }`) rather than calling `waitForIdle()` exactly once. If
  this still flakes on the host, the next lever is Robolectric's `ShadowLooper.idleMainLooper()` /
  `mainClock.advanceTimeBy(...)` (not currently used, since this repo has no prior precedent for it —
  would need to be introduced and verified fresh).
- **Flow emission waits**: if a screen inside `AppNavigation` (e.g. `ProgramEditorScreen`, per the exact
  prior-art bug already documented) gets captured mid-recomposition in a `stateIn` INITIAL value, the
  symptom is a `tree_summary` that looks like the loading/editable-default branch instead of the real
  loaded branch. Since the walker takes a snapshot immediately after `waitForIdle()`, this is a live risk
  for ANY screen the walk reaches that has its own async `stateIn`, not just Today. If this repeats, add a
  `waitUntil` gate keyed on a screen-specific expected-text marker analogous to `LayoutDumpTest.kt`'s
  `waitFor` parameter, generalized to "wait until the just-navigated-to screen shows ANY non-empty
  interactive node" as a cheap universal heuristic — not implemented yet, since it's unclear if it's
  needed until a real host run surfaces the failure.
- **`Assembler` resolution failures**: if `Assembler.build(AppViewModel::class.java)` throws
  `error("unmapped interface: ...")` or `error("no dao on db for ...")`, that pinpoints exactly which
  constructor parameter's type `Assembler.resolve()` doesn't know how to build — extend `resolve()`'s
  `when` in `Assembler.kt` (test sources only, so this stays LAW-compliant) rather than hand-wiring
  `AppViewModel` directly in the test.
- **Gradle test gating**: this new test class will run as part of every `assembleDebug`/`testDebugUnitTest`
  invocation per `build.gradle.kts`'s existing `if (!project.hasProperty("skipUnitTests"))` wiring (lines
  191–195) unless `-PskipUnitTests` is passed — a full 60-step walk on every build may be too slow for
  routine CI; consider gating this specific test behind its own Gradle property once runtime is measured.

## "Never game a meter" compliance note

The recorder never invokes a handler lambda directly, never fabricates a destination state without
actually driving the real Compose input pipeline (`performClick`/`performTextInput`), never skips or
special-cases a specific screen's ordinal enumeration, and records every error/replay-failure as data
(never silently discarded) — the same discipline `walker.py`'s own docstring insists on ("No handler is
ever invoked directly — a same-cause-same-fix violation the LAW forbids"). The one mechanism
(`enumerateInteractive` + `performAction` + BFS frontier) applies uniformly to every screen in the app;
no screen has bespoke walker logic beyond the existing seed/fixture tables already used by
`LayoutDumpTest`/`LayoutDumpAllTest`.
