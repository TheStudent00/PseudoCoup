# STATUS: UNEXECUTED — no emulator started, no code run, dry-build only

Everything in this document describes a code/design port that was written and read-reviewed but never
compiled, never run, and never exercised against a real device or emulator. No `python3`, no `adb`, no
`gradle` command was executed while producing any of the artifacts this document describes.

## 1. Summary — ported vs written fresh

| Artifact | Status | Notes |
|---|---|---|
| `WFL/app/src/main/java/com/sara/workoutforlife/core/debug/CommandReceiver.kt` | **Ported** | Ported from `StressTestingBot/ToStressTest/WFL/.../CommandReceiver.kt` against CURRENT `WFL_MixingCenter` sources. Package path unchanged. |
| `WFL/app/src/debug/AndroidManifest.xml` | **Ported** | Debug-variant manifest fragment registering the receiver; already exists on disk. |
| `render/emuwalk_utils.py` | **Written fresh** | Small vendor-copied adb/uiautomator helpers, trimmed from reading StressTestingBot source files, with NO import dependency on that repo. |
| `render/emu_walker.py` | **Written fresh** | Mirrors `render/walker.py`'s BFS policy (state hashing, settle debounce, tap-path replay, checkpoint/resume, states/edges schema), adapted for a real device/emulator via adb/uiautomator instead of in-process Robolectric/Kivy tree access. |
| `DevComms/emulator_walk_drybuild.md` (this file) | **Written fresh** | This deliverable doc. |

`render/walker.py` itself is **not present in this checkout's working tree** (only `.git` internals and
top-level `DevComms/*.md`/`PROGRESS*.md` docs exist under `/home/lucas/Programming/PseudoCoup` at the
time of this port); its design, schema, and specific line-number citations used throughout
`emu_walker.py`'s docstring and this document were taken from the two prior dev-comms reports that
quote it directly and extensively: `DevComms/walker_slice1.md` (the Python walker's own design/fix
history, citing e.g. walker.py:132, 178-187, 202-204, 216, 225-236, 437-469, 481-539, 531-539, 565-566,
654-668, 668-673) and `DevComms/walker_slice2_kotlin.md` (the Kotlin recorder's parity table, which
independently re-cites most of the same line ranges when cross-checking its own port against
`walker.py`). Every walker.py line-number citation in `render/emu_walker.py`'s docstring traces to one
of those two documents, not to a direct read of a `walker.py` file, since no such file exists on disk
in this checkout.

## 2. Schema-drift findings (file:line citations)

- **`DebugSeeder.seedTestFixture()` no longer exists** on the current `DebugSeeder`
  (`core/debug/DebugSeeder.kt:32-130` — full class body read; its actual public surface is
  `seedCompletedSessionDaysAgo()`, `clearSessions()`, `armCelebration()`, `seedLifeEvent()`,
  `resetDatabase()`). The ported `CommandReceiver.kt`'s `"setup_test_fixture"` branch
  (`CommandReceiver.kt:124-129`) drops the call entirely and instead logs a warning
  (`Log.w("WFL_CMD", "setup_test_fixture is no longer supported ...")`) and no-ops, directing callers to
  `reset_db` (`resetDatabase()`, still present at `DebugSeeder.kt:116-125`) instead.
- **`SetLogEntity` gained a defaulted `midMicrocycleFlag` field.** `WorkoutDatabase.kt:776-780`
  (`MIGRATION_29_30`) adds `ALTER TABLE set_logs ADD COLUMN midMicrocycleFlag INTEGER NOT NULL DEFAULT
  0`. The ported `CommandReceiver.kt`'s `seed_set` and `seed_test_session` branches
  (`CommandReceiver.kt:177-208`, `CommandReceiver.kt:250-290`) now pass `midMicrocycleFlag = false`
  explicitly on every `SetLogEntity(...)` construction rather than relying on the default, per this
  port's own comment at `CommandReceiver.kt:46-48`.
- **All other DAOs/entities confirmed unchanged** (prior verification, stated generically per the task
  instructions, since the original stale `ToStressTest` version is not directly accessible in this
  session for a side-by-side diff): `ProgramDao`, `MicrocycleDao`, `MicrocycleTargetDao`,
  `ExerciseLogDao`, `ProgramDayDao`, `WorkoutSessionDao`, `SetLogDao`, `AutoregulationRepository`,
  `WorkoutExecutionRepository`, `DiagnosticsCollector` — all referenced with identical signatures in the
  ported receiver (`CommandReceiver.kt:71-79`), per that file's own class-doc drift note
  (`CommandReceiver.kt:49-52`).

## 3. Parity table — walker.py mechanism/field → emu_walker.py mechanism/field

| Concept | `render/walker.py` | `render/emu_walker.py` |
|---|---|---|
| State hashing | `sha256(json.dumps({"route":...,"tree_summary":...}, sort_keys=True))` (walker.py:202-204, per walker_slice2_kotlin.md's citation) | Identical algorithm/field set — `state_id_of()` in emu_walker.py, byte-compatible so hashes can be diffed directly across walk sources |
| Settle detection | `Session.settle(max_rounds=12)` polls in-process node count until two consecutive counts match; honestly reports `unsettled=True` on cap-out (walker_slice1.md "Settle CAP" section) | `settle(max_rounds=12)` polls `uiautomator dump` (via `emuwalk_utils.get_ui_hierarchy_xml()`) until two consecutive normalized dumps are byte-identical; same cap, same honest `unsettled` flag threaded into every edge |
| Action/tap mechanism | Real synthetic touch via `EventLoop.post_dispatch_input`, never a direct handler call (walker_slice1.md/walker_slice2_kotlin.md "Never game a meter") | Real `adb shell input tap <x> <y>` at the target node's bounds-center (`emuwalk_utils.bounds_center()`/`tap_bounds()`), never any in-process invocation |
| `tree_summary` schema | `[{"kind","text","interactive"}, ...]`, document (pre)order, geometry excluded (walker.py:178-187, 225-236) | Identical field set and pre-order DFS, parsed from uiautomator XML (`parse_hierarchy()`); bounds tracked in a separate, unhashed field purely for tap replay |
| Checkpoint/resume | `walks/py_walk_progress.json`, atomic `os.replace()` after every edge, records `states`/`edges`/`frontier` (walker.py:489-494, walker_slice1.md checkpoint proof) | `walks/emu_walk_checkpoint.json` (adapted name), same atomic write-then-`os.replace()` after every edge, same `states`/`edges`/`frontier`/`visited_state_ids` shape |
| Edge exploration / recovery | Fresh process reboot per edge + tap-path replay from root (`replay_and_step`, walker.py:481-539) | Fresh `reset_db` broadcast per edge (`emuwalk_utils.reset_db()`, matching `CommandReceiver.kt`'s `"reset_db"` branch) + tap-path replay from root (`replay_path()`) — same ONE general replay mechanism, "reboot the process" swapped for "reset the DB via broadcast" as the analogous full-reset primitive |
| Output schema | `{"meta", "states", "edges"}`, `json.dump(..., indent=1, sort_keys=True)` (walker.py:668-673) | Identical top-level shape and serialization options, written to `walks/emu_walk.json` |

## 4. Self-review

### 4a. Every adb command in `emuwalk_utils.py` checked against StressBot's patterns

| `emuwalk_utils.py` function | Checked against | Citation | Result |
|---|---|---|---|
| `get_adb_path()` | `AdbUtils.get_adb_path` | `adb_utils.py:6-15` | Matches (which-adb-then-local-SDK-path fallback) |
| `run_adb()` | `AdbUtils.run_command` | `adb_utils.py:17-26` | Same subprocess pattern, swallow-and-return-"" on failure; added an explicit `timeout_s` not present upstream, a defensive addition (not a drift) |
| `get_devices()` | `AdbUtils.get_devices` | `adb_utils.py:28-37` | Matches |
| `send_wfl_broadcast()` | `AdbUtils.send_broadcast` / `WFL_CMD_ACTION` / `WFL_RECEIVER` constants, and `WFLCommandAdapter.reset_database()`'s actual extras dict | `adb_utils.py:45-64`, `wfl_command_adapter.py:6-7, 40-45` | Matches the explicit-component (`-n`) targeting rationale and the quoted `--es` value convention; extras key is `"action"` (matching `CommandReceiver.kt`'s `intent?.getStringExtra("action")`), not the `--es cmd ...` shorthand mentioned as a style example in the task prompt — called out explicitly in the function's own docstring to avoid silent mismatch |
| `read_app_file()` | `AdbUtils.read_app_file` | `adb_utils.py:66-72` | Matches (`run-as ... cat files/<name>`, since `adb pull` cannot reach app-private storage on a non-root device) |
| `get_ui_hierarchy_xml()` | N/A — new mechanism, `uiautomator dump` | — | StressBot's own files (`maestro_utils.py:13-19`, `parser.py`, `wfl_command_adapter.py:144-156`) show it uses `maestro hierarchy`, NOT `uiautomator`. This port deliberately chose `uiautomator dump` instead (see emuwalk_utils.py's module docstring "NOTE ON HIERARCHY SOURCE") specifically to avoid an unverified assumption about Maestro's JSON bounds key name — StressBot's own `StateParser.parse_ui_hierarchy` (`parser.py:23-47`) only ever reads a `text` attribute, never bounds, so there is no evidence in the read source of how Maestro exposes tap-able bounds |
| `get_hierarchy_via_maestro()` | `MaestroUtils.get_hierarchy` | `maestro_utils.py:13-19` | Kept as a parity/fallback wrapper, not used by `emu_walker.py`'s default path |
| `bounds_center()` | N/A — new helper, standard uiautomator XML `bounds="[x1,y1][x2,y2]"` attribute format | — | Not adb-command-shaped; a pure string-parsing helper, documented as such |
| `is_device_online()`, `wait_for_boot()` | `EmulatorUtils.is_device_online`, `EmulatorUtils.wait_for_boot` | `emulator_utils.py:32-34`, `emulator_utils.py:54-68` | Matches, including the 3s post-boot settle sleep |
| `EmulatorBootPrefs` headless flags | `EmulatorUtils.boot`'s headless branch | `emulator_utils.py:37-52` | `-no-snapshot`, `-no-window`, `-no-audio`, `-gpu swiftshader_indirect` all match; `EmulatorUtils` expresses no opinion on AVD image API level or `-memory`/`-no-boot-anim` — those extra flags proposed below (§5) are UNVERIFIED against this source, not sourced from it |

### 4b. Every DAO/entity/table reference in `CommandReceiver.kt` checked against current WFL_MixingCenter sources

| Reference | Checked against | Result |
|---|---|---|
| `DebugSeeder` surface (`resetDatabase`, `seedCompletedSessionDaysAgo`, `clearSessions`, `armCelebration`, `seedLifeEvent`) | `core/debug/DebugSeeder.kt:32-130` (full class read) | Confirmed present with these exact signatures; `seedTestFixture()` confirmed ABSENT — drift documented in §2 above |
| `SetLogEntity` constructor fields, including `midMicrocycleFlag` | `WorkoutDatabase.kt:776-780` (`MIGRATION_29_30`) | Confirmed the column/field was added via migration with a default; ported receiver passes it explicitly rather than relying on the default (§2 above) |
| `ProgramDao.getEnrolled()`, `MicrocycleDao.getByProgram()`, `MicrocycleTargetDao.getByMicrocycle()`, `ExerciseLogDao.getBySession()`, `ProgramDayDao.getByProgram()`, `WorkoutSessionDao`, `SetLogDao.insert()`, `AutoregulationRepository.calculateAndPersistTargets()`, `WorkoutExecutionRepository.startSessionFromProgramDay()`/`completeSession()`, `DiagnosticsCollector.collect()` | Referenced call sites in `CommandReceiver.kt:88-93, 105-402` | All confirmed to exist with identical signatures used by the ported receiver — flagged in the receiver's own class doc (`CommandReceiver.kt:49-52`) as "all other DAOs/entities/repositories ... still exist with identical signatures", stated here as prior verification since the original stale `ToStressTest` version of this file is not directly accessible in this session for a literal side-by-side diff — drift is therefore reported as "fixed" for the two items in §2 (the only two differences actually located), not as an exhaustive guarantee no other silent drift exists beyond those two |

## 5. RAM/AVD note

`StressTestingBot/StressBot/utils/emulator_utils.py`'s `EmulatorUtils.boot()` (`emulator_utils.py:37-52`)
DOES express an opinion on some flags: for a headless boot it passes `-no-snapshot`, `-no-window`,
`-no-audio`, `-gpu swiftshader_indirect`. It has **no opinion** on AVD image API level or `-memory`/
`-no-boot-anim`. For those, this port proposes reasonable defaults, **marked UNVERIFIED since nothing
was run**:

- AVD image: Pixel-class device, API 30-33 system image
- `-no-snapshot` (confirmed, matches `emulator_utils.py:46`)
- `-gpu swiftshader_indirect` (confirmed, matches `emulator_utils.py:48`)
- `-memory 1536-2048` (UNVERIFIED — not present in `emulator_utils.py`)
- `-no-audio` (confirmed, matches `emulator_utils.py:48`)
- `-no-boot-anim` (UNVERIFIED — not present in `emulator_utils.py`)

## 6. TO RUN LATER — NOT RUN NOW

The following host commands are the intended next steps once this dry-build is reviewed. **None of
these were executed while producing this document or the two Python files it describes.**

```bash
# --- AVD creation/launch (UNVERIFIED flags per §5 marked as such) ---
avdmanager create avd -n StressTest_AVD -k "system-images;android-33;google_apis;x86_64" -d pixel_5
emulator -avd StressTest_AVD -no-snapshot -no-window -no-audio -gpu swiftshader_indirect -memory 2048 -no-boot-anim

# --- build + install the debug APK ---
cd WFL_MixingCenter/WFL
./gradlew :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk

# --- trigger the walk's DB-reset primitive manually, for a sanity check ---
adb shell am broadcast -a com.sara.workoutforlife.WFL_CMD \
    -n com.sara.workoutforlife/.core.debug.CommandReceiver \
    --es action reset_db

# --- run the emulator walker itself ---
cd PseudoCoup/render
python3 emu_walker.py --steps 60 --reset
python3 emu_walker.py --steps 60 --resume   # to continue from walks/emu_walk_checkpoint.json
```

---

## 8. CONTINUATION -- files relocated, re-verified line-for-line against the REAL `render/walker.py`

`emu_walker.py` and `emuwalk_utils.py` have been moved to `/home/lucas/Programming/WFL_MixingCenter/render/`
(their eventual correct home, alongside the real `render/walker.py`, `render/interact.py`,
`render/run_app.py`, etc.). Section 7 above documents why the ORIGINAL port (produced when this
checkout had no `render/walker.py` on disk at all) could only cite line numbers secondhand, via
`walker_slice1.md`/`walker_slice2_kotlin.md`'s quotations. This continuation re-reads the REAL
`render/walker.py` directly and re-checks every citation in `emu_walker.py`'s docstring and the parity
table (§3) against it line-for-line. Net result: the field-name/algorithm-level claims in §3 all HOLD
UP; one genuine, previously-unverifiable drift was found and fixed, one is flagged as a structural gap
that cannot be fixed without new on-device signal, and one is a step-budget-accounting nuance flagged
for awareness (behavior/output-shape unaffected).

### 8a. Drifts found (import/path constants)

**None.** `emu_walker.py`'s `import emuwalk_utils as eu` and its `OUT_DIR`/`FINAL_PATH`/
`CHECKPOINT_PATH` constants (all derived from `os.path.dirname(os.path.abspath(__file__))`, i.e.
self-relative to wherever the file physically sits) were already location-independent -- moving both
files together into `render/` required no import or path-constant changes. Confirmed by direct
re-inspection of every `import`/`os.path`/`sys.path` line in both files after the move.

### 8b. Drift found and FIXED: `current_route()` returned raw `dumpsys` text, not a route name

`walker.py`'s `route` field (module docstring, walker.py:26-35; populated via `app.nc.currentRoute()`
at walker.py:252/413/425/443) is a real, stable, repeatable nav-graph route STRING (e.g. `"today"`,
`"my_program"`) -- exactly the kind of thing the task LAW requires ("real route names", never a gamed
placeholder). The ORIGINAL `emu_walker.py`'s `current_route()` returned the ENTIRE raw
`mResumedActivity`/`topResumedActivity` line from `dumpsys activity activities` verbatim -- including
the ActivityRecord's hex object id and task id, both of which are NOT stable across launches/recreations
even when the on-screen screen is identical. This would have silently made every "route" value
effectively unique per boot, breaking any real cross-run state_id comparison and violating the "real
route names" law by presenting non-repeatable debug text as if it were a route. **Fixed** (see
`render/emu_walker.py`'s `current_route()`, now paired with a new `_RESUMED_ACTIVITY_RE` regex): extracts
just the stable `<package>/<ActivityClass>` component name from the ActivityRecord line. Residual, HONEST
limitation documented in the function's own updated docstring: WFL is a single-Activity app (all nav-graph
routing happens inside `MainActivity`'s own in-Compose `NavController`, invisible to `dumpsys`), so this
device-side route signal cannot currently distinguish "today" from "my_program" the way `walker.py`'s or
the Kotlin recorder's route field can -- every in-app screen currently collapses to the same
`"com.sara.workoutforlife/.MainActivity"` string. States are STILL correctly distinguished (state_id
hashes tree_summary content too), just without a human-readable per-screen route label. Not
"solved" further because doing so would require either a new adb-visible signal this app doesn't
currently expose, or scraping visible nav-bar text as a route guess -- rejected as an unverified
heuristic per the same "never fabricate a signal" reasoning already used elsewhere in this file.

### 8c. Drift found, FLAGGED (not fixable without new on-device signal): dialogs/menus not tagged as distinct states

`walker.py`'s `capture_states()` (walker.py:207-221) tags an open dialog/menu with `"<route>#dialog:<Kind>"`
/ `"<route>#menu:<Kind>"`, sourced from `kivy_kit._active_overlays` -- an in-process registry with no
adb/uiautomator equivalent. `emu_walker.py`'s `parse_hierarchy()` walks whatever uiautomator currently
sees flat into one `tree_summary` (so an open dialog's content DOES still change tree_summary and
therefore state_id -- states are not silently merged), but the `route` field for that state will never
carry the `#dialog:`/`#menu:` tag `walker.py`'s would. Documented as a code comment directly above
`tree_summary_of()` in `render/emu_walker.py` rather than silently matched or silently dropped.

### 8d. Drift found, FLAGGED (behavioral nuance, no output-shape impact): frontier `n_actions` resolution timing

`walker.py`'s main BFS loop (walker.py:529-548) defers resolving a new frontier frame's `n_actions` to a
TRAILING pass that runs once per invocation AFTER the main loop exits (walker.py:591-622), explicitly
counted against that invocation's step budget (`spent += 1`, walker.py:619). `emu_walker.py`'s loop
resolves `n_actions is None` INLINE the first time such a frame reaches the frontier's head, via a nested
`replay_path()` call, and does NOT charge that resolution against `steps_run`. Final BFS shape (state
discovery order, edge set, state_ids) is unaffected -- this only affects how much actual replay work one
`--steps N` invocation performs, which matters for CI step-budget tuning, not for output correctness.
Documented as a code comment above the `Frame` dataclass in `render/emu_walker.py`.

### 8e. Verified UNCHANGED (re-checked against real walker.py, no drift)

- **State hashing** (`state_id_of`): byte-identical algorithm and field set to `walker.py:202-204`
  (`sha256(json.dumps({"route":..., "tree_summary":...}, sort_keys=True))`). Confirmed against the real
  source this time, not a secondhand citation.
- **tree_summary schema**: `{"kind","text","interactive"}`, document pre-order DFS, geometry excluded --
  matches `walker.py:178-187`'s `_component_list()` field-for-field.
- **Action descriptor fields**: `{"kind","label","handler_kind","ordinal"}` matches `walker.py:436`'s
  `action = {"kind": node.kind, "label": lab, "handler_kind": hk, "ordinal": ordinal}` field-for-field.
- **"42" text-input convention**: confirmed directly against `render/interact.py:159-182`'s
  `infer_value()` (`return "42"` for a plain text field, `cur.copy(text="42")` for a `TextFieldValue`-
  shaped current value) -- `emu_walker.py`'s literal `"42"` sent via `adb shell input text 42` matches.
- **Output schema**: `{"meta","states","edges"}` top-level shape, `json.dump(..., indent=1,
  sort_keys=True)` -- matches `walker.py:668-673` (this file's own `write_final()`/checkpoint writers use
  the same `json.dump(..., indent=1, sort_keys=True)` call shape).
- **Recovery policy**: "one general mechanism, tap-path replay from root" -- confirmed this file's
  `replay_path()`/`reset_to_root()` still follow the SAME single mechanism `walker.py`'s
  `replay_and_step` does (walker.py:404-469), substituting a DB-reset broadcast for a process reboot as
  the reset primitive, exactly as originally documented; no second recovery path was introduced.

### 8f. `kt_walk.json` (Kotlin/Robolectric side) field-name cross-check

As of this continuation, `kt_walk.json` (item 1's `writeFinal()` output) does not exist yet -- the
Kotlin walker still fails before reaching the end of `walkApp()` (see
`walker_slice2_execution.md`'s continuation section for the precise residue). The IN-PROGRESS
checkpoint `kt_walk_progress.json`, however, DOES now exist and was inspected directly: its `states`
entries carry `state_id`/`route`/`tree_summary` (`kind`/`text`/`interactive`) fields, and its `edges`
entries carry `source`/`action`(`kind`/`label`/`handler_kind`/`ordinal`)/`destination`/`error`/
`unsettled` -- ALL of these field names match both `render/walker.py`'s and `render/emu_walker.py`'s
schemas exactly, byte-for-byte on key names. This is the first time all three artifacts' field-name
parity could be checked against real (not secondhand-cited) output on at least one side; full three-way
verification (including a completed `kt_walk.json` and an actual on-device `emu_walk.json`) remains
future work once item 1's Kotlin walker reaches green and an emulator run is actually performed.

## 7. `/tmp/gh` staging workaround note

An earlier session attempted to stage a working copy of `WFL_MixingCenter` under `/tmp/gh` (mirroring
the workaround documented in `DevComms/walker_slice1.md`'s "§4a HANG FIX" section, which used a `/tmp/gh`
staging copy for a different, glob-hang-related reason). For this port, the `rsync` used to populate
that staging copy hit an RPC error partway through and did not complete a usable mirror. Rather than
retry the staging step (out of scope for this dry-build, and not required for it), every file:line
citation in this document and in `CommandReceiver.kt`'s own port-provenance comment was produced by
reading the REAL `WFL_MixingCenter` sources directly at their normal repository paths (e.g.
`/home/lucas/Programming/WFL_MixingCenter/WFL/app/src/main/java/com/sara/workoutforlife/...`), not
against any staged `/tmp/gh` copy. This is noted here purely for continuity with the prior session's
staging convention, not because this port's citations depend on that staging in any way.


---

# ADDENDUM (merged from a stray copy misplaced in WFL_MixingCenter/DevComms — post-move parity pass)

# STATUS: UNEXECUTED — no emulator started, no code run, dry-build only

Everything below was produced by reading real sources closely (walker.py's exact logic/line numbers,
the Kotlin slice 2 doc, StressTestingBot's adb/maestro/parser utilities, ToStressTest's
CommandReceiver.kt, and the CURRENT WFL_MixingCenter Room/manifest sources). **No emulator, adb,
gradle, or python command was executed. No git commit was made.** This is a pure dry-build: files
were written/edited on disk only, per the task's explicit constraints.

## Summary — ported vs written fresh

**Ported (adapted, not blindly copied):**
- `WFL/app/src/main/java/com/sara/workoutforlife/core/debug/CommandReceiver.kt` — ported from
  `StressTestingBot/ToStressTest/WFL/app/src/main/java/com/sara/workoutforlife/core/debug/CommandReceiver.kt`.
  Package path unchanged (`com.sara.workoutforlife.core.debug`, module root `WFL/app` — both repos
  share this structure). All existing commands kept working against the current schema, with two
  fixes (see drift section) and two new commands added (`dump_db`, `dump_semantics`).

**Written fresh:**
- `WFL/app/src/debug/AndroidManifest.xml` — did not exist in WFL_MixingCenter before this task
  (confirmed: no `app/src/debug/` directory existed). ToStressTest registers `CommandReceiver`
  directly in its main manifest (`ToStressTest/WFL/app/src/main/AndroidManifest.xml:49-55`); this
  port instead isolates the registration to a new debug-only manifest fragment, the more
  conservative choice, leaving `WFL_MixingCenter/WFL/app/src/main/AndroidManifest.xml` completely
  untouched (verified: it currently has no `debug` package reference at all).
- `render/emu_walker.py` — new file, the emulator/uiautomator-based third walker.
- `render/emuwalk_utils.py` — new file, vendored/trimmed adb+uiautomator helpers, zero import
  dependency on StressTestingBot.

## Schema-drift findings (file:line citations)

All citations below are against the sources read directly for this task (StressTestingBot repo
files read directly; WFL_MixingCenter's real sources — confirmed no symlink-loop issue was hit
reading them directly, so no `/tmp/gh` staging copy was ultimately needed for the final citations
below; every file: path cited is the real, current file).

| # | Referenced symbol | Stale (ToStressTest) usage | Current WFL_MixingCenter reality | Verdict / fix |
|---|---|---|---|---|
| 1 | `DebugSeeder.seedTestFixture()` | Called for `setup_test_fixture` action (`ToStressTest CommandReceiver.kt:87-96`) | `core/debug/DebugSeeder.kt:32-130` — actual method surface is `seedCompletedSessionDaysAgo`, `clearSessions`, `armCelebration`, `seedLifeEvent`, `resetDatabase`. **No `seedTestFixture()` exists.** | DRIFTED/REMOVED. Ported receiver drops the real seeding call and logs a warning + no-op for `setup_test_fixture`, directing callers to `reset_db` instead (see `CommandReceiver.kt`'s "Drift fixed" doc comment). Not invented. |
| 2 | `SetLogEntity` constructor | 13-field constructor with no `midMicrocycleFlag` (`ToStressTest CommandReceiver.kt:151-168`, `230-247`) | `data/db/entity/SetLogEntity.kt:30-63` now has `midMicrocycleFlag: Boolean = false`, added by `WorkoutDatabase.kt:776-780` (`MIGRATION_29_30`) | Non-breaking (has a default) but the ported constructor calls now explicitly pass `midMicrocycleFlag = false` for clarity/forward-compat. |
| 3 | `ProgramDao.getEnrolled()` | Used in `activeMicrocycleId()`/`seed_test_session` | `data/db/dao/ProgramDao.kt:21-22` — signature unchanged | No drift. |
| 4 | `MicrocycleDao.getByProgram(programId)` | Used in `activeMicrocycleId()` | `data/db/dao/MicrocycleDao.kt:22-29` — signature unchanged | No drift. |
| 5 | `MicrocycleTargetDao.getByMicrocycle(id)` | Used in `get_targets` | `data/db/dao/MicrocycleTargetDao.kt:12-13` — signature unchanged | No drift. |
| 6 | `ProgramDayDao.getByProgram(programId)` | Used in `seed_test_session` | `data/db/dao/ProgramDayDao.kt:26-34` — signature unchanged | No drift. |
| 7 | `ExerciseLogDao.getBySession(sessionId)` | Used in `seed_test_session` | `data/db/dao/ExerciseLogDao.kt:21-22` — signature unchanged | No drift. |
| 8 | `WorkoutExecutionRepository.startSessionFromProgramDay` / `completeSession` | Used in `seed_test_session` | `data/repository/WorkoutExecutionRepository.kt:58` (class ctor), `:76` (`startSessionFromProgramDay`), `:419` (`completeSession`) — both present | No drift. |
| 9 | `AutoregulationRepository.calculateAndPersistTargets` | Used in `recalculate_targets` | `data/repository/AutoregulationRepository.kt:118` (class ctor), `:142` (method) — present | No drift. |
| 10 | `DiagnosticsCollector.collect(currentRoute: String?)` | Called with `null` in `get_diagnostics` | `core/diagnostics/DiagnosticsCollector.kt:38` — signature `collect(currentRoute: String?)` unchanged; returns `DiagnosticsSnapshot(environment, recentLogs, pendingCrash)` (`DiagnosticsCollector.kt:21-25`) | No drift. |
| 11 | `WorkoutDatabase` DAO surface used by the receiver (`SetLogDao`, `MicrocycleTargetDao`, `WorkoutSessionDao`, `MicrocycleDao`, `ExerciseLogDao`, `ProgramExerciseDao`, `ProgramDao`, `ProgramDayDao`) | All injected in ToStressTest's receiver | All present as abstract accessors on `data/db/WorkoutDatabase.kt:95-119` (`setLogDao()`, `microcycleTargetDao()`, `workoutSessionDao()`, `microcycleDao()`, `exerciseLogDao()`, `programExerciseDao()`, `programDao()`, `programDayDao()`) | No drift. |
| 12 | Manifest registration | `ToStressTest/WFL/app/src/main/AndroidManifest.xml:49-55`, registered directly in main manifest, `android:exported="true"`, no `BuildConfig.DEBUG` guard in code | `WFL_MixingCenter/WFL/app/src/main/AndroidManifest.xml` has zero receiver/debug references (confirmed by full read) | New debug-only manifest written at `WFL/app/src/debug/AndroidManifest.xml` (did not exist before); receiver code additionally hardened with an explicit `BuildConfig.DEBUG` guard in `onReceive` (ToStressTest's receiver had none — see next section). |

## Parity table — walker.py ↔ emu_walker.py

| Policy dimension | `render/walker.py` (WFL_MixingCenter copy) | `render/emu_walker.py` |
|---|---|---|
| state_id hash | `sha256(json.dumps({"route","tree_summary"}, sort_keys=True))` (walker.py:202-204) | Byte-identical algorithm, `state_id_of()` |
| tree_summary schema | `{"kind","text","interactive"}`, geometry excluded (walker.py:37-41, 178-187) | Same 3 fields via `component_list()`; geometry (uiautomator `bounds`) read only transiently for tapping, never stored/hashed |
| Settle detection | Poll compose()+remount until node COUNT stabilizes, capped `max_rounds`, `unsettled` flag on cap (walker.py:287-313) | Poll `uiautomator dump` until two consecutive dumps are structurally identical (volatile attrs normalized), same cap/flag discipline (`emuwalk_utils.settle_until_stable`) |
| Action schema | `{"kind","label","handler_kind","ordinal"}` (walker.py:59-64) | Same 4 fields; `kind`=uiautomator `class`, `label`=`text`/`content-desc`, `handler_kind` synthesized from `clickable`/`long-clickable`/EditText via fixed priority (mirrors slice 2's own fixed-priority simplification) |
| Checkpoint/resume | `walks/py_walk_progress.json`, atomic tmp+os.replace (walker.py:482-494) | `walks/emu_walk_checkpoint.json`, same atomic write, same `{states,edges,frontier,visited_state_ids,done}` shape |
| Edge exploration / replay | Fresh process boot + replay tap-path (ordinals, freshly re-resolved) from root per edge (walker.py:84-93, 404-469) | `reset_db` broadcast + force-stop/relaunch + replay tap-path (ordinals freshly re-resolved) from root per edge — the ONE mechanism, no second replay path |
| Output schema | `{"meta","states","edges"}`, `json.dump(indent=1, sort_keys=True)` (walker.py:668-673) | Byte-identical top-level shape and dump call, `walks/emu_walk.json` |
| Dialogs/menus as states | Implemented via `kivy_kit._active_overlays` (walker.py:99-101, 190-221) | NOT implemented — flagged, not guessed (uiautomator dump has no overlay-membership tag) |
| Scroll-into-view | Implemented, reused from `realtap_gate.py` (walker.py:79-82) | NOT implemented — flagged as a gap |

## Self-review — every adb command in emuwalk_utils.py vs its StressBot source pattern

| emuwalk_utils.py function | StressBot source pattern (file:line) | Match |
|---|---|---|
| `get_adb_path()` | `StressBot/utils/adb_utils.py:6-15` (`AdbUtils.get_adb_path`) | Identical fallback order (PATH → `~/Android/Sdk/platform-tools/adb` → bare `"adb"`) |
| `run_adb()` | `adb_utils.py:17-26` (`AdbUtils.run_command`) | Same subprocess wrapper shape; added a 30s timeout not present upstream (defensive, since this file drives long BFS loops unattended) |
| `send_broadcast()` | `adb_utils.py:45-64` (`WFL_CMD_ACTION`/`WFL_RECEIVER` constants + `send_broadcast`) | Explicit-component `-n` targeting and per-value double-quoting reproduced verbatim, same rationale comment |
| `read_app_file()` | `adb_utils.py:66-73` (`AdbUtils.read_app_file`) | Identical `run-as ... cat files/<name>` pattern |
| `read_app_json()` | `StressBot/adapters/wfl_command_adapter.py:76-90` (`get_diagnostics`'s "broadcast, sleep(1), json.loads, swallow to {}" shape) | Same shape, parameterized to any filename |
| `dump_hierarchy_xml()` | `StressBot/utils/maestro_utils.py:13-19` (`get_hierarchy`, but via the `maestro hierarchy` CLI + JSON) | DELIBERATELY DIFFERENT mechanism (uiautomator dump + XML, not Maestro CLI + JSON) — see the file's own "DESIGN NOTE" docstring for why (no per-tap flow-file/process overhead, no extra binary dependency) |
| `tap()` / `input_text()` | `StressBot/utils/maestro_utils.py:21-34` (`MaestroUtils.tap`, flow-file based) | DELIBERATELY DIFFERENT: bare `adb shell input tap`/`input text`, not a Maestro YAML flow round-trip, for per-node BFS-enumeration speed |
| `press_back()` | `maestro_utils.py:36-49` (`MaestroUtils.back`) | Structural analogue, `adb shell input keyevent 4` instead of a Maestro flow |

## RAM / AVD note

`StressBot/utils/emulator_utils.py:37-52` (`EmulatorUtils.boot`) already has an opinion for headless
boot flags: `-no-snapshot`, and when `headless=True`: `-no-window -no-audio -gpu swiftshader_indirect`.
No RAM/`-memory` flag or explicit API-level/Pixel-image preference is set anywhere in that file — it
takes `avd: str = "StressTest_AVD"` as an opaque name and does not construct the AVD itself
(`list_avds()` only lists what's already created). So for RAM/AVD-creation specifics beyond the flags
above, the following are **UNVERIFIED proposals** (nothing was run to confirm them):
- AVD image: Pixel-class, API 30–33 (unverified — no explicit StressBot preference found)
- `-no-snapshot` (confirmed StressBot preference, `emulator_utils.py:46`)
- `-no-window -no-audio -gpu swiftshader_indirect` for headless (confirmed, `emulator_utils.py:48`)
- `-memory 1536-2048` (UNVERIFIED — proposed default, not found in StressBot)
- `-no-boot-anim` (UNVERIFIED — proposed default, not found in StressBot; would shave boot time)

## Exact host commands to run LATER (NOT run now)

```bash
# 1. Create/confirm an AVD (one-time, UNVERIFIED flags beyond -no-snapshot/-no-window/-no-audio/-gpu):
avdmanager create avd -n StressTest_AVD -k "system-images;android-33;google_apis;x86_64"

# 2. Boot it headless (StressBot's own confirmed flags + UNVERIFIED RAM/boot-anim additions):
~/Android/Sdk/emulator/emulator -avd StressTest_AVD -no-snapshot -no-window -no-audio \
    -gpu swiftshader_indirect -memory 2048 -no-boot-anim

# 3. Build and install the debug APK (registers CommandReceiver via the new src/debug manifest):
cd WFL_MixingCenter/WFL && ./gradlew :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk

# 4. Sanity-check the receiver is reachable:
adb shell am broadcast -a com.sara.workoutforlife.WFL_CMD \
    -n com.sara.workoutforlife/.core.debug.CommandReceiver --es action reset_db

# 5. Run the emulator walker (writes walks/emu_walk.json + walks/emu_walk_checkpoint.json):
cd WFL_MixingCenter/render && python3 emu_walker.py --steps 60

# Resume a checkpointed walk:
python3 emu_walker.py --steps 60 --resume

# Discard checkpoint and start over:
python3 emu_walker.py --steps 60 --reset
```

All five command blocks above are for a LATER host run — nothing in this task executed any of them.
