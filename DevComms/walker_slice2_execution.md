# WalkRecorderTest execution log (walker slice 2)

Mechanism chosen: **proper Hilt test setup**, per the task's stated preference — `@HiltAndroidTest` +
`HiltAndroidRule` + `@Config(application = HiltTestApplication::class)`, added
`hilt-android-testing` (+ `kspTest(libs.hilt.compiler)`) to `app/build.gradle.kts` /
`gradle/libs.versions.toml` as `testImplementation`-only additions. The walk mounts the app's REAL
`AppNavigation`, so its screens' `hiltViewModel()` calls resolve against a genuine Hilt test
component — no wiring was swapped or faked.

**Residue at stop (round-trip budget exhausted): the walker still does not complete a full run.**
Root cause is isolated and precise (see "Current blocker" below), but not yet fixed within budget.

## Request log

| id | cmd focus | failure | fix |
|---|---|---|---|
| 003_walk | first Hilt-enabled run | `IllegalStateException` at `EntryPoints.get`: bare `ComponentActivity` (via `createComposeRule()`) doesn't implement `GeneratedComponent` | switched to a dedicated `@AndroidEntryPoint class WalkHostActivity : ComponentActivity()` (test sources) + `createAndroidComposeRule<WalkHostActivity>()` |
| 004_walk | manifest merge | `processDebugUnitTestManifest` "Manifest merging exception" | added `app/src/test/AndroidManifest.xml` registering `WalkHostActivity`; first attempt missing `package=` attribute |
| 005_walk | manifest merge | SAXParseException: `"--"` not permitted in XML comments (my own doc-comment used `--` prose dashes) | rewrote comment prose to avoid `--` |
| 006_walk | Robolectric activity resolution | `RuntimeException: Unable to resolve activity ... cmp=.../.walk.WalkHostActivity` (Robolectric PR 4736) despite the activity being present in the merged text manifest | added `<intent-filter>` (MAIN/LAUNCHER) to `WalkHostActivity`'s manifest entry, on the (later disproven) theory that explicit-component intents still need a filter match |
| 007_walk | same, after full `clean` | identical failure even from a guaranteed-fresh build | ruled out stale-cache theory |
| 008_walk | manifest merge | SAXParseException `"--"` again, in the NEW intent-filter comment | fixed comment again |
| 009_walk | (stacktrace re-run of 008) | confirmed same `--` cause | — |
| 010_walk | Robolectric activity resolution, intent-filter present, manifest confirmed correct | **same** "Unable to resolve activity" | Diagnosed root cause: `app/build/intermediates/apk_for_local_test/.../apk-for-local-test.ap_` (the resource APK Robolectric's `PackageManager` actually resolves activities against, per `test_config.properties`'s `android_resource_apk` key) is built by `packageDebugUnitTestForUnitTest` from the **debug variant's own `processDebugResources`/main manifest** — never from `processDebugUnitTestManifest`'s merged **test** manifest. Verified directly: extracted `AndroidManifest.xml` from that `.ap_` and found `MainActivity` but no `WalkHostActivity`, even though the separate merged **text** manifest file correctly listed it. This is a genuine AGP↔Robolectric wiring gap for JVM unit tests, not a mistake in the added manifest. |
| 011_walk | forced `packageDebugUnitTestForUnitTest` explicitly | task still `UP-TO-DATE` (its declared inputs don't include the test manifest at all) | confirms the gap is structural, not a staleness/caching bug |
| 012_walk | abandoned `WalkHostActivity`; switched to real `MainActivity` (`@AndroidEntryPoint`, already manifest-registered) via `createAndroidComposeRule<MainActivity>()` | manifest merge exception again (leftover no-op test manifest had a fresh `--` typo) | fixed comment prose once more |
| 013_walk | (stacktrace re-run) | confirmed same `--` cause | — |
| 014_walk | clean no-op test manifest | `IllegalStateException`: "`MainActivity` has already set content" — `MainActivity.onCreate()` (production code) already calls `setContent { AppNavigation(...) }` for real, so the test rule's own first `rule.setContent{}` call collides with it | added one small, additive, default-off seam to `MainActivity.kt` (main sources): an `Intent` extra `EXTRA_SKIP_SETCONTENT` (default absent/false) that makes `onCreate` return before its production `setContent{}` call. Every real launch is byte-for-byte unaffected (extra is never set outside this test). Built a custom `ActivityScenarioRule<MainActivity>` with that extra pre-set, wrapped in `AndroidComposeTestRule`. |
| 015_walk | compile | Kotlin inference errors on the manual `AndroidComposeTestRule(...)` construction | added explicit generic type args |
| 016_walk | compile | `AndroidComposeTestRule`'s `(activityRule, environment)` constructor is private/experimental | switched to the public `(activityRule, activityProvider)` constructor, providing `activityProvider` via `scenario.onActivity { ... }` |
| 017_walk | run | compiles and runs; **same** "`MainActivity` has already set content" error, but now at `mountFreshApp` → `replayTo` (i.e. the *second* call to `rule.setContent{}`, not the first) — the boot mount succeeds, the first BFS replay's fresh mount does not | **STOPPED HERE, budget exhausted** |

## Current blocker (precise)

`WalkRecorderTest.walkApp()`'s BFS walk calls `mountFreshApp()` once per replay (by design — "ONE FRESH
APP MOUNT per replay", `WalkRecorderTest.kt`'s own comment above that function), and `mountFreshApp()`
calls `rule.setContent{}` unconditionally every time. The **first** call (test boot) now succeeds
against `MainActivity` with `EXTRA_SKIP_SETCONTENT`. The **second** call (inside the first `replayTo`)
fails with the same "has already set content" `IllegalStateException` Compose's test rule throws when
an Activity already carries a Compose root. This means `AndroidComposeTestRule.setContent{}` is not
being called against a genuinely fresh Activity/root on subsequent replays — either:

- the `ActivityScenarioRule`'s single `MainActivity` instance is being reused across all replays with
  its Compose root from the FIRST `setContent{}` call never cleared, so the second call collides with
  the test's own prior content (not the production one anymore) — i.e. the walker's "fresh mount per
  edge" design assumed a fresh Activity/Compose root each time (as `createComposeRule()`'s ad hoc
  ComponentActivity effectively gave the original, unexecuted draft), which is not what happens when
  reusing one `ActivityScenarioRule`-backed real Activity across an entire JUnit test method; or
- `mountFreshApp()` needs an explicit `scenario.recreate()` / relaunch per replay to get Compose back to
  a content-less state before calling `rule.setContent{}` again.

Next fix to try (not yet attempted): either (a) call `composeRule.activityRule.scenario.recreate()` (with
`EXTRA_SKIP_SETCONTENT` still set, so recreate's `onCreate` also skips production content) at the top of
`mountFreshApp()` before `rule.setContent{}`, or (b) special-case the FIRST mount to use `rule.setContent{}`
directly and all SUBSEQUENT mounts to dispose/replace via a held `ComposeView` reference obtained from the
first mount (per the error message's own suggested pattern: "populate the Activity with a ComposeView,
call setContent on that ComposeView instead of on the test rule"). Option (a) is more in the spirit of the
walker's existing "fresh reboot per edge" policy comment and should be tried first.

## Final walk stats

**Not available.** No run has completed `walkApp()` successfully yet; `build/walks/kt_walk.json` was
never produced by any of the 003–017 runs (confirmed: the test fails before `writeFinal()` is ever
reached, since it fails inside the very first `replayTo()` call of the BFS loop). No `-Dwalk.steps=60`
run was attempted since the `-Dwalk.steps=20` smoke run never got past its first edge.

## Files touched

- `WFL/app/src/test/java/com/sara/workoutforlife/walk/WalkRecorderTest.kt` — Hilt rule chain, custom
  `ActivityScenarioRule<MainActivity>` construction, `hiltInjected` guard. Test sources only.
- `WFL/app/src/main/java/com/sara/workoutforlife/MainActivity.kt` — added `EXTRA_SKIP_SETCONTENT`
  (default absent/false; no behavior change for any real launch) so the test can suppress the
  production `setContent{}` call. This is the one main-source touch beyond the pre-existing
  `AppNavigation.onNavControllerReady` param the file's own header already documents; it follows the
  same "additive, default-neutral" pattern.
- `WFL/app/build.gradle.kts` / `WFL/gradle/libs.versions.toml` — added
  `testImplementation(libs.hilt.android.testing)` and `kspTest(libs.hilt.compiler)` /
  `hilt-android-testing` coordinate. `testImplementation`/`kspTest` only, no main-source or
  shipped-APK impact.
- `WFL/app/src/test/AndroidManifest.xml` — added, then reduced to a no-op (`<application />`) once the
  `WalkHostActivity` approach was abandoned; left in place empty because this sandbox's file tools
  cannot delete a file once created (only overwrite). Currently inert.

## Parity comparison against render/walker.py (Python side) — deferred, not fully checkable yet

Requested as a sanity check for the differ slice, but since no Kotlin walk has actually completed, this
is a **static read-through comparison only** (field names / hashing inputs), not a comparison of real
output. From `WalkRecorderTest.kt`'s own inline documentation (which explicitly cross-references
`render/walker.py`'s docstring throughout) plus the Python `render/walker.py` module docstring:

- **state_id hashing**: both sides claim `sha256(json.dumps({"route": route, "tree_summary": [...]},
  sort_keys=True))` — Kotlin hand-builds the sorted-key JSON string (`stateIdOf`/`canonicalComponentJson`)
  since `org.json.JSONObject` doesn't preserve/sort keys the way Python's `json.dumps(sort_keys=True)`
  does. This is a plausible-by-inspection match (same field set, same alphabetical key order per object)
  but **UNVERIFIED against a real Python-side hash** — no test asserts a Kotlin state_id equals a Python
  state_id for the same conceptual state, and none can be computed until the Kotlin walk actually runs.
- **Component fields**: Kotlin's `Component(kind, text, interactive)` vs Python's presumed
  `(kind, text, ...)` shape — the Kotlin file's own comment (lines ~152–169) flags that Compose's `kind`
  vocabulary (`Role.Button`, `"EditableText"`, `"Node"`) is a **deliberately different vocabulary** than
  Kivy's `Node.kind` (e.g. `"Button"`, `"NavigationBarItem"`, `"OutlinedTextField"`) — this is the
  headline parity gap the task already anticipated: **any differ built on top of this must map
  Compose-Role-space to Kivy-kind-space explicitly; it cannot assume the same `kind` string means the
  same thing on both sides.**
- **Action/edge fields**: `ActionRec(kind, label, handler_kind, ordinal)` — `handler_kind` enumeration
  (`onClick`/`onLongClick`/`onValueChange`/`onSelectedChange`) is Compose-semantics-shaped and likely does
  not line up 1:1 with whatever handler-kind vocabulary `walker.py` uses for Kivy widgets (not
  independently re-verified in this session; flagged by the Kotlin file's own comment as a policy point,
  not confirmed against the actual Python source in this pass).
- **TEXT_INPUT_VALUE**: both sides reportedly use the literal `"42"` for text-shaped actions (per the
  Kotlin file's comment referencing `render/interact.py`'s `infer_value()` policy) — not independently
  re-checked against `interact.py` in this session.

**Bottom line for the differ slice**: field NAMES appear aligned by design (both intentionally mirror the
same dict/JSON shape), but `kind` values are explicitly NOT aligned (Compose Role vocabulary vs Kivy
Node.kind vocabulary) and must be mapped, not compared raw. This was already flagged in the original
(unexecuted) draft's own comments; this session did not add new parity findings beyond confirming the
gap is real and re-stating it precisely, because no actual Kotlin walk output exists yet to diff against
a real Python walk output.

---

## CONTINUATION SESSION (round-trips 018-021) -- real progress, still not fully green

Budget for this session: ~5 gradle round-trips. Used 4 (018/019/020/021); stopping per budget, residue
below is precise.

### Fix implemented (round 018): `scenario.recreate()` per replay

Per round 017's "Next fix to try" note, implemented option (a): `mountFreshApp()` now calls
`scenarioRule.scenario.recreate()` before every replay's `rule.setContent{}` EXCEPT the very first mount
of the whole test (tracked via a new `everMounted: Boolean` field). `recreate()` preserves the ORIGINAL
launch `Intent` (including `EXTRA_SKIP_SETCONTENT=true`), so the new Activity instance's `onCreate` still
skips `MainActivity`'s production `setContent{}` call -- confirmed this actually fixed the original
blocker: round 018's failure moved from "Activity has already set content" (the round-017 blocker) to a
NEW, later failure (`ComposeTimeoutException` at the `capturedNavController` `waitUntil`), proving the
double-`setContent` collision is gone. Files touched: `WalkRecorderTest.kt` only (test sources), per LAW.

### Round-by-round log (continuation)

| id | failure | fix applied |
|---|---|---|
| 018_walk | `IllegalStateException` "Activity has already set content" GONE. New: `ComposeTimeoutException` at `mountFreshApp`'s `rule.waitUntil { capturedNavController != null }` (line ~425 at the time) -- `scenario.recreate()`'s scheduled onCreate/onResume callbacks never actually ran before the wait started | added `shadowOf(Looper.getMainLooper()).idle()` right after `recreate()` (Robolectric's documented remedy for its own "Main looper has queued unexecuted runnables" suppressed-exception hint, which appeared verbatim in round 018's stack trace) |
| 019_walk | SAME `ComposeTimeoutException`, same line (now shifted +11 lines by the new comment/idle() call) -- `capturedNavController` STILL never set after recreate, but the "unexecuted runnables" suppressed exception is now GONE (confirms the idle() fix worked for the looper-drain part) | forced `currentActivity` to point at the NEW post-recreate() Activity immediately via an explicit `scenarioRule.scenario.onActivity { currentActivity = it }` call, rather than relying on `AndroidComposeTestRule`'s own lazy `activityProvider` invocation timing |
| 020_walk | `capturedNavController` wait now PASSES. New failure: `AssertionError: Expected exactly '1' node but found '2' nodes that satisfy: (isRoot)` at the second `waitUntil`'s `rule.onRoot(useUnmergedTree = true).fetchSemanticsNode()` call -- TWO Compose roots exist simultaneously (same (0,0)-(411,915) bounds), meaning the PREVIOUS (destroyed) Activity's Compose root is not unregistered by the time `recreate()` returns/settles | added a `currentRootNode()` helper using `rule.onAllNodes(isRoot(), useUnmergedTree = true)` and picking the LAST root (Compose's root registry only ever appends, never reorders or removes eagerly on Robolectric activity destroy, per direct observation) -- replaced every `rule.onRoot(useUnmergedTree = true).fetchSemanticsNode()` call site in the file with `currentRootNode()` |
| 021_walk | Root-picking fix worked: `mountFreshApp()`'s OWN two `waitUntil` calls both now pass on repeated replays (confirmed: `kt_walk_progress.json` was written with **7 real states, 10 edges**, states include real route names `today`, `my_program`, `paths` -- i.e. several fresh mounts + replays + new edges genuinely succeeded). Run still ends FAILED: a LATER `mountFreshApp()` call (deeper into the BFS, inside `replayTo` for a longer path) hits the SAME `ComposeTimeoutException` at the same `capturedNavController` `waitUntil` that rounds 018/019 hit -- i.e. the recreate()-settle race from round 018/019 is not fully eliminated by the `onActivity{}` force-refresh; it now happens INTERMITTENTLY (succeeds several times, then recurs) rather than on every replay | **NOT YET FIXED -- budget exhausted, stopping here per the ~5 round-trip cap** |

### Residue at stop (precise)

The `capturedNavController != null` wait inside `mountFreshApp()` (currently `WalkRecorderTest.kt` around
line 441, `rule.waitUntil(timeoutMillis = 10_000) { capturedNavController != null }`) still times out
**intermittently** on later replays (those with a longer replay `path`, i.e. deeper BFS frames), even
though it now reliably succeeds on the first several replays (proven by the 7-state/10-edge progress
file). This means the fix is real but incomplete: `scenario.recreate()` + `shadowOf(...).idle()` +
forced `onActivity{}` refresh gets the new Activity's Compose content mounted and its
`onNavControllerReady` callback fired MOST of the time, but not with 100% reliability across many
recreate() cycles in one JUnit test method -- consistent with a residual Robolectric main-looper
scheduling race that `idle()` drains most but not all of (e.g. a coroutine-dispatched Room-flow emission
that lands on a slightly later looper tick than the one `idle()` drained). This is the SAME general class
of race already named in the file's own comment ("the SAME class of Robolectric flow-emission race as
the 'ProgramEditor stateIn race'"), just resurfacing with lower but nonzero frequency after the other
fixes landed.

**Next fix to try (not yet attempted, in priority order):**
1. Replace the single `shadowOf(Looper.getMainLooper()).idle()` call after `recreate()` with a bounded
   RETRY loop (`idle()` + short sleep, repeated up to N times or until `capturedNavController != null`),
   since one `idle()` pass appears to drain the queue most-but-not-all of the time.
2. Investigate whether `seedDb()`'s dedicated `Executors.newFixedThreadPool(4)` per mount is leaking a
   prior mount's Room executor threads across `recreate()` cycles (each `mountFreshApp()` call creates a
   BRAND NEW in-memory DB + executor pool without ever shutting down the previous one) -- accumulating
   thread-pool contention across many recreate() cycles in one test method could plausibly explain an
   INTERMITTENT (not-every-time) timeout that gets more likely deeper into the walk (more mounts
   accumulated). This was not true in earlier rounds (which failed on EVERY replay, a hard bug); this
   round's INTERMITTENT failure profile is more consistent with a resource-accumulation race than a
   structural one.

### Final walk stats (round 021, `-Dwalk.steps=20`, `-Dwalk.reset=1`)

**Partial, from `build/walks/kt_walk_progress.json`** (the run's checkpoint; `kt_walk.json`, the
`writeFinal()` output, was NOT written since the test itself still fails before reaching the end of
`walkApp()`):

- **states: 7** (all `>0`, satisfying the sanity-assert law) -- real route names confirmed: `today`,
  `my_program`, `paths`, plus others not enumerated above (see raw file for full list)
- **edges: 10**
- **frontier remaining: 6** (BFS not exhausted within this run's step budget/failure point)

No `-Dwalk.steps=60` run was attempted (budget exhausted before reaching a green `-Dwalk.steps=20` run,
per the task's own gating condition "LOOP until green ... THEN one run at steps=60").

### Files touched (continuation, in addition to prior session's list)

- `WFL/app/src/test/java/com/sara/workoutforlife/walk/WalkRecorderTest.kt` (test sources only, per LAW):
  - `everMounted: Boolean` field + `scenario.recreate()` call gated on it, in `mountFreshApp()`
  - `shadowOf(Looper.getMainLooper()).idle()` immediately after `recreate()`
  - explicit `scenarioRule.scenario.onActivity { currentActivity = it }` refresh after `recreate()`
  - new `currentRootNode()` helper (picks the last of `onAllNodes(isRoot())`) replacing every
    `rule.onRoot(useUnmergedTree = true).fetchSemanticsNode()` call site in the file
  - added import `org.robolectric.Shadows.shadowOf`
- No main-source files touched in this continuation session (MainActivity.kt's `EXTRA_SKIP_SETCONTENT`
  seam is unchanged from the prior session).

---

## CONTINUATION SESSION 2 (rounds 022-024) -- GREEN, WalkRecorderTest passes

Budget: ~5 round-trips. Used 3 (022/023/024). **Test is green.**

### Fix implemented (round 022): per-mount Room executor teardown + bounded looper-drain retry

Per round 021's residue diagnosis and this session's brief (resource accumulation across
`scenario.recreate()` cycles), applied the SAME per-test-executor mechanism the compose dump suite used
(`LayoutDumpAllTest.kt`'s `Executors.newFixedThreadPool(4)` on the Room builder, fixing the
`ArchTaskExecutor`-contention race documented in `DevComms/hermeticity_timestamps_report.md`), but scoped
PER-MOUNT instead of per-test, since one `WalkRecorderTest` JUnit method performs MANY mounts:

- `seedDb()` now returns a `SeededDb(db, executor)` pair instead of just the `db`, so the caller can hold
  and later shut down the executor it created (previously the `Executors.newFixedThreadPool(4)` was
  created and discarded every mount with no reference kept -- a genuine leak: 4 live threads per mount,
  accumulating for the life of the JVM/test method, each potentially still serving a leaked ViewModel's
  `WhileSubscribed` flow collector from the app's un-cancelled `viewModelScope`, contending with
  Robolectric's single main-looper thread more as the walk goes deeper).
- `mountFreshApp()` now tracks `currentDb: WorkoutDatabase?` and `currentDbExecutor: ExecutorService?`,
  and calls a new `teardownPreviousMount()` (closes the previous db, `shutdownNow()` + bounded
  `awaitTermination` on its executor) BEFORE every `scenario.recreate()` call -- i.e. one cause (leaked
  per-mount Room executors/DB connections never closed across `recreate()` cycles), one general fix
  (explicit close/shutdown of the PREVIOUS mount's resources before creating the next mount's).
- Also added a bounded retry loop around both the post-`recreate()` looper drain (`idle()` + `sleep(20)`,
  up to 5 attempts, replacing the single `idle()` call from round 018) and the `capturedNavController`
  `waitUntil` itself (catch `ComposeTimeoutException`, re-idle + short sleep, retry up to 3 attempts) --
  per the task brief's "also consider retry-looping the idle(), but fix the leak first" guidance. This is
  additional insurance for whatever residual scheduling jitter remains after the leak fix, not a
  substitute for it.

Files touched: `WalkRecorderTest.kt` only (test sources), per LAW/FENCE. No generated-assembler or
main-source changes were needed; the per-mount executor pattern was implemented directly in the test file
by having `seedDb()` return the executor handle for the caller to own, which is the "mirror it within
test sources" fallback the task brief allowed for.

### Round-by-round log (session 2)

| id | steps | result |
|---|---|---|
| 022_walk | `-Dwalk.steps=20 -Dwalk.reset=1` | **BUILD SUCCESSFUL** (212s). `kt_walk.json` written (test reached `writeFinal()` -- first time ever). **30 states, 51 edges**, 11 distinct real routes (`today`, `my_program`, `paths`, `progress`, `wins`, `settings_notifications`, `gym_editor?gymId={gymId}`, `gym_list`, `execution/{sessionId}`, `workout_cooldown/{sessionId}`, `workout_summary/{sessionId}`). |
| 023_walk | same cmd (repeat, per determinism check) | **BUILD SUCCESSFUL** (200s). Also 30 states / 51 edges, same 11 routes, same per-route counts. Diffed byte-for-byte against 022's `kt_walk.json`: **29/30 states and 50/51 edges identical** (same `state_id`s); the ONE differing state is on `settings_notifications` and differs only in an `EditableText` node's accumulated text (`"42424242424242424242User"` vs `"4242424242424242424242User"` -- one extra `"42"` repetition), a pre-existing artifact of the walk's own `TEXT_INPUT_VALUE = "42"` policy hitting the SAME text field via multiple BFS paths/orderings (append-only text field state), not a symptom of the recreate()/executor race this session fixed. All routes, all other 29 states, and 50 of 51 edges are exactly reproduced. |
| 024_walk | `-Dwalk.steps=60 -Dwalk.reset=1` | **BUILD SUCCESSFUL** (148s). 22 states, 53 edges, 7 real routes (`today`, `my_program`, `paths`, `progress`, `execution/{sessionId}`, `programs`, `program_editor/{programId}`) -- walk completed (frontier exhausted) well inside the 60-step budget. |

### Final walk stats

- **steps=20 (round 022, first green run): 30 states, 51 edges, 11 real routes.**
- **steps=20 (round 023, repeat): 30 states, 51 edges, 11 real routes; 29/30 states and 50/51 edges
  byte-identical to round 022 (state_ids match) -- the sole divergence is a known, pre-existing
  text-accumulation artifact on one `settings_notifications` `EditableText` node, unrelated to the
  recreate()/executor fix.**
- **steps=60 (round 024): 22 states, 53 edges, 7 real routes, walk completed before hitting the step cap.**
- No `ComposeTimeoutException` / "has already set content" / "2 nodes satisfy isRoot" failures recurred
  in any of the three rounds -- the intermittent-timeout residue from round 021 is gone.

### Files touched (session 2, in addition to prior sessions' lists)

- `WFL/app/src/test/java/com/sara/workoutforlife/walk/WalkRecorderTest.kt` (test sources only):
  - `seedDb()` return type changed from `WorkoutDatabase` to a new private `SeededDb(db, executor)` data
    class, so the executor it creates is no longer discarded by the caller.
  - `mountFreshApp()`: new `currentDb` / `currentDbExecutor` fields, new `teardownPreviousMount()`
    (closes prior db, shuts down prior executor) called before every `scenario.recreate()`.
  - Post-`recreate()` looper drain changed from a single `idle()` call to a bounded `repeat(5) {
    idle(); Thread.sleep(20) }` loop.
  - `capturedNavController` `waitUntil` wrapped in a bounded retry loop (up to 3 attempts, re-idling and
    sleeping between attempts) catching `ComposeTimeoutException`.

DELIVERABLE STATUS: **DONE.** WalkRecorderTest is green at steps=20 (twice, near-fully deterministic) and
steps=60 (once). Not committed, per instructions.
