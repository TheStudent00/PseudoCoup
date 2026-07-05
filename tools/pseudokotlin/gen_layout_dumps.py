"""gen_layout_dumps.py -- GENERATE the layout ground-truth test for every screen in the app.

The per-screen wiring in LayoutDumpTest.kt was hand-written while the kit was being diagnosed; this
makes the rest mechanical. It scans ui/**/*.kt for top-level `fun XxxScreen(...)` composables, reads
each parameter list, and emits one @Test per screen into LayoutDumpAllTest.kt:

  * `viewModel: X = hiltViewModel()`  -> `viewModel = a.build(X::class.java)` (Assembler.kt builds any
    ViewModel by constructor type, the way the python harness's di.py does)
  * `innerPadding: PaddingValues`     -> `PaddingValues(0.dp)`
  * callbacks `(...) -> Unit`         -> `{}`
  * nullable / defaulted params       -> omitted or null
  * anything else                     -> the screen is SKIPPED, with the reason printed

Screens already covered by hand-written tests (they carry per-screen fixtures) are excluded here.
EXCEPTIONS holds the few per-screen facts a machine cannot guess (waitFor anchors, nav args, skips).
Both engines seed the SAME standard fixture (one gym + one cardio session), mirroring
inspect_layout.seed_fixtures. The generated file also writes screens_all.txt -- the manifest
fidelity.py reads.

    python3 gen_layout_dumps.py          # rewrites LayoutDumpAllTest.kt + layout_screens.txt
"""
import os
import re

ROOT = os.path.expanduser("~/Programming/WFL_MixingCenter")
UI = os.path.join(ROOT, "WFL/app/src/main/java/com/sara/workoutforlife/ui")
OUT_KT = os.path.join(ROOT, "WFL/app/src/test/java/com/sara/workoutforlife/layout/LayoutDumpAllTest.kt")
OUT_MANIFEST = os.path.join(ROOT, "render/layout_screens.txt")

# screens with DEDICATED tests (per-screen fixtures / nav args) -- not regenerated here
HANDWRITTEN = {"GymListScreen", "LogCardioScreen", "ExercisesScreen", "SettingsScreen", "TodayScreen",
               "ProgramsScreen", "HistoryScreen", "ExerciseDetailScreen", "WinsListScreen",
               "ProgressScreen"}

# the per-screen facts a machine cannot guess
# seed values: "program" = exercise catalog + curated sample programs (deterministic ids --
# prog_gup_3d_beg / day_gup_3d_beg_w1_d1); "session" = program + a live session started from that
# day THROUGH the app's own WorkoutExecutionRepository (its generated sessionId becomes the
# "sessionId" nav arg -- ids need not match across engines, only rendered text does);
# "sessionDone" = the same session, completed.
EXCEPTIONS = {
    "waitFor": {                      # screen -> a text that must be on screen before dumping
        # waitForIdle alone can dump the stateIn() INITIAL state before the Room flow emits --
        # anchor on a text only the loaded state renders (seeded ids are deterministic)
        "ProgramDayEditorScreen": "Full Body A — Squat",
        "SessionDetailScreen": "Full Body A — Squat",
        "WorkoutExecutionScreen": "Full Body A — Squat",
    },
    "navArgs": {                      # screen -> kotlin map literal for the SavedStateHandle
        "ProgramEditorScreen": 'mapOf("programId" to "prog_gup_3d_beg")',
        "ProgramDayEditorScreen": 'mapOf("dayId" to "day_gup_3d_beg_w1_d1")',
        "ExercisePickerScreen": 'mapOf("dayId" to "day_gup_3d_beg_w1_d1")',
    },
    "seed": {                         # screen -> fixture bundle beyond the standard gym+cardio
        "ProgramEditorScreen": "program",
        "ProgramDayEditorScreen": "program",
        "ExercisePickerScreen": "program",
        "WorkoutExecutionScreen": "session",
        "WorkoutCooldownScreen": "session",
        "SuggestedStretchesScreen": "session",
        "WorkoutSummaryScreen": "sessionDone",
        "SessionDetailScreen": "sessionDone",
    },
    "skip": {                         # screen -> reason (filled as runs surface real blockers)
        "DebugPanelScreen": "dev-only tool; PaddingValues type clash in its signature",
    },
}

FUN_RE = re.compile(r"^fun ([A-Z][A-Za-z]*Screen)\(", re.M)


def params_of(src, start):
    """The parameter list text of the function starting at `start` (balanced parens)."""
    i = src.index("(", start)
    depth, j = 0, i
    while j < len(src):
        depth += {"(": 1, ")": -1}.get(src[j], 0)
        if depth == 0:
            break
        j += 1
    return src[i + 1:j]


def split_params(text):
    """Top-level comma split (respects nested parens/braces; NOT <> -- the `>` in `->` corrupted
    bracket counting and swallowed every lambda-typed parameter after the first)."""
    out, depth, cur = [], 0, []
    for ch in text:
        if ch in "({[":
            depth += 1
        elif ch in ")}]":
            depth -= 1
        if ch == "," and depth == 0:
            out.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    tail = "".join(cur).strip()
    if tail:
        out.append(tail)
    return [p for p in out if p and not p.startswith("//")]


def classify(p, pkg=""):
    """One parameter -> (kotlin argument text or None-to-omit) or ('SKIP', reason)."""
    p = re.sub(r"^@\w+(\([^)]*\))?\s*", "", p.strip())
    m = re.match(r"(\w+)\s*:\s*(.+?)(?:\s*=\s*(.+))?$", p, re.S)
    if not m:
        return ("SKIP", f"unparsed param: {p[:40]}")
    name, typ, default = m.group(1), m.group(2).strip(), m.group(3)
    if "-> Unit" in typ or typ.endswith("-> Unit)?"):
        return f"{name} = {{}}"
    if "ViewModel" in typ:
        vm = typ.split("=")[0].strip()
        q = vm if "." in vm else f"{pkg}.{vm}"   # the VM lives in the screen's own package
        return f"{name} = a.build({q}::class.java)"
    if typ.startswith("PaddingValues"):
        return f"{name} = PaddingValues(0.dp)"
    if default is not None:
        return None                              # keep the declared default
    if typ.endswith("?"):
        return f"{name} = null"
    if typ == "String":
        return f'{name} = ""'
    if typ == "Boolean":
        return f"{name} = false"
    return ("SKIP", f"required {typ} '{name}'")


def main():
    tests, manifest, skipped = [], [], []
    for dirpath, _, files in os.walk(UI):
        for f in sorted(files):
            if not f.endswith(".kt"):
                continue
            src = open(os.path.join(dirpath, f)).read()
            pkg = re.search(r"^package (\S+)", src, re.M).group(1)
            for m in FUN_RE.finditer(src):
                screen = m.group(1)
                if screen in HANDWRITTEN:
                    continue
                if screen in EXCEPTIONS["skip"]:
                    skipped.append((screen, EXCEPTIONS["skip"][screen]))
                    continue
                args, reason = [], None
                for p in split_params(params_of(src, m.start())):
                    c = classify(p, pkg)
                    if isinstance(c, tuple):
                        reason = c[1]
                        break
                    if c is not None:
                        args.append(c)
                if reason:
                    skipped.append((screen, reason))
                    continue
                nav = EXCEPTIONS["navArgs"].get(screen, "emptyMap()")
                seed = EXCEPTIONS["seed"].get(screen)
                seed_arg = f', seed = "{seed}"' if seed else ""
                wf = EXCEPTIONS["waitFor"].get(screen)
                wf_arg = f', waitFor = "{wf}"' if wf else ""
                arg_txt = ",\n                ".join(args)
                tests.append(f"""
    @Test
    fun dump{screen}() {{
        val a = assembler({nav}{seed_arg})
        dump("{screen}"{wf_arg}) {{
            {pkg}.{screen}(
                {arg_txt},
            )
        }}
    }}""")
                manifest.append(screen)

    header = '''package com.sara.workoutforlife.layout

// GENERATED by PseudoCoup tools/pseudokotlin/gen_layout_dumps.py -- do not hand-edit.
// One layout ground-truth dump per screen, wired automatically (see Assembler.kt). Screens with
// dedicated hand-written tests (per-screen fixtures) live in LayoutDumpTest.kt instead.

import android.content.Context
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.runtime.Composable
import androidx.compose.ui.semantics.SemanticsProperties
import androidx.compose.ui.semantics.getOrNull
import androidx.compose.ui.test.hasText
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import androidx.compose.ui.unit.dp
import androidx.room.Room
import androidx.test.core.app.ApplicationProvider
import com.sara.workoutforlife.data.db.WorkoutDatabase
import com.sara.workoutforlife.data.db.entity.GymProfileEntity
import com.sara.workoutforlife.ui.theme.WorkoutforlifeTheme
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner
import org.robolectric.annotation.Config
import org.robolectric.annotation.GraphicsMode
import java.io.File

@RunWith(RobolectricTestRunner::class)
@GraphicsMode(GraphicsMode.Mode.NATIVE)
@Config(sdk = [35], qualifiers = "w411dp-h915dp", application = android.app.Application::class)
class LayoutDumpAllTest {

    @get:Rule
    val rule = createComposeRule()

    init {
        java.util.TimeZone.setDefault(java.util.TimeZone.getTimeZone("UTC"))
    }

    /** The STANDARD fixture, identical to the python harness's global seed (inspect_layout.
     *  seed_fixtures): one active gym, one cardio session at a fixed instant. `seed` layers the
     *  program/session bundles on top -- always THROUGH the app's own repositories, so both engines
     *  produce the same rows by construction (see EXCEPTIONS["seed"] in the generator). */
    private fun assembler(navArgs: Map<String, Any?> = emptyMap(), seed: String? = null): Assembler {
        val ctx = ApplicationProvider.getApplicationContext<Context>()
        // Give every test its OWN Room executors. Room otherwise falls back to the JVM-static
        // ArchTaskExecutor IO pool, which is shared across the whole test class: the WhileSubscribed /
        // init{} flow collectors that earlier tests' ViewModels leak (viewModelScope is never
        // cancelled here) stay parked on that shared pool and contend its threads, so a later screen's
        // first Room-flow emission can arrive after the dump. That is exactly how ProgramEditorScreen
        // gets captured in its stateIn INITIAL state (ProgramEditorUiState(isReadOnly=false) -> the
        // editable branch) instead of the loaded read-only branch. A per-test executor isolates each
        // test's DB traffic, restoring hermeticity for the whole class in one place.
        val dbExecutor = java.util.concurrent.Executors.newFixedThreadPool(4)
        val db = Room.inMemoryDatabaseBuilder(ctx, WorkoutDatabase::class.java)
            .setQueryExecutor(dbExecutor).setTransactionExecutor(dbExecutor)
            .allowMainThreadQueries().build()
        var args = navArgs
        runBlocking {
            db.gymProfileDao().insert(GymProfileEntity(
                id = "fixture-gym-1", name = "My Gym", isActive = true, createdAt = 0L, updatedAt = 0L))
            db.cardioSessionDao().insert(com.sara.workoutforlife.data.db.entity.CardioSessionEntity(
                id = "fixture-cardio-1", type = com.sara.workoutforlife.data.model.CardioType.RUN,
                source = com.sara.workoutforlife.data.model.CardioSource.MANUAL,
                startedAt = 1718438400000L, endedAt = null, durationMinutes = 30,
                intensity = com.sara.workoutforlife.data.model.CardioIntensity.MODERATE,
                perceivedRpe = null, distanceMeters = 5000.0, avgHeartRate = null, maxHeartRate = null,
                activeKcal = null, affectsMuscleGroups = emptyList(), linkedWorkoutSessionId = null,
                externalId = null, notes = null, createdAt = 1718438400000L, updatedAt = 1718438400000L))
            if (seed != null) {
                val boot = Assembler(db, ctx)
                boot.build(com.sara.workoutforlife.data.repository.ExerciseRepository::class.java)
                    .seedIfNeeded()
                boot.build(com.sara.workoutforlife.data.repository.SampleProgramRepository::class.java)
                    .seedIfNeeded()
                if (seed == "session" || seed == "sessionDone") {
                    val exec = boot.build(
                        com.sara.workoutforlife.data.repository.WorkoutExecutionRepository::class.java)
                    val sid = exec.startSessionFromProgramDay("day_gup_3d_beg_w1_d1")
                    if (seed == "sessionDone") exec.completeSession(sid)
                    // Pin the live session's wall-clock timestamps to the SAME fixed instant the
                    // python half uses (inspect_layout.seed_fixtures), so the date/time header text
                    // is deterministic across engines instead of reflecting each run's clock.
                    db.workoutSessionDao().getById(sid).first()?.let { row ->
                        db.workoutSessionDao().update(row.copy(
                            startedAt = 1718438400000L,
                            completedAt = row.completedAt?.let { 1718438400000L },
                        ))
                    }
                    args = mapOf("sessionId" to sid)
                }
            }
        }
        return Assembler(db, ctx, args)
    }

    private fun dump(screen: String, waitFor: String? = null, content: @Composable () -> Unit) {
        rule.setContent { WorkoutforlifeTheme(darkTheme = false) { content() } }
        rule.waitForIdle()
        if (waitFor != null) {
            rule.waitUntil(timeoutMillis = 10_000) {
                rule.onAllNodes(hasText(waitFor), useUnmergedTree = true)
                    .fetchSemanticsNodes().isNotEmpty()
            }
        }
        val root = rule.onRoot(useUnmergedTree = true).fetchSemanticsNode()
        val out = JSONObject()
        out.put("screen", screen)
        out.put("engine", "compose-robolectric")
        out.put("display", JSONObject().put("w", root.size.width).put("h", root.size.height))
        val nodes = JSONArray()
        fun walk(node: androidx.compose.ui.semantics.SemanticsNode, path: String) {
            val b = node.boundsInRoot
            val text = node.config.getOrNull(SemanticsProperties.Text)?.joinToString("") { it.text }
                ?: node.config.getOrNull(SemanticsProperties.EditableText)?.text
            val o = JSONObject()
            o.put("path", path)
            if (text != null) o.put("text", text)
            o.put("x", b.left).put("y", b.top).put("w", b.width).put("h", b.height)
            nodes.put(o)
            node.children.forEachIndexed { i, c -> walk(c, "$path/$i") }
        }
        walk(root, "0")
        out.put("nodes", nodes)
        val dir = File(System.getenv("LAYOUT_DUMP_DIR") ?: "build/layout_dump").apply { mkdirs() }
        File(dir, "$screen.json").writeText(out.toString(2))
    }
'''
    with open(OUT_KT, "w") as f:
        f.write(header + "\n".join(tests) + "\n}\n")
    with open(OUT_MANIFEST, "w") as f:
        f.write("\n".join(sorted(HANDWRITTEN)) + "\n" + "\n".join(manifest) + "\n")
    print(f"generated {len(tests)} tests -> {os.path.relpath(OUT_KT, ROOT)}")
    print(f"manifest {len(manifest) + len(HANDWRITTEN)} screens -> {os.path.relpath(OUT_MANIFEST, ROOT)}")
    for s, r in skipped:
        print(f"  SKIP {s}: {r}")


if __name__ == "__main__":
    main()
