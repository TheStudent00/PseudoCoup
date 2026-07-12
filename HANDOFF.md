# HANDOFF — read this whole top document before doing anything (updated 2026-07-12)

## What this project is

The Kotlin app (~/Programming/WFL_MixingCenter/WFL) is GROUND TRUTH. The Python app is its transpiled
twin (built by PseudoCoup_v0's KtToPy transpiler, run via WFL_MixingCenter/render/run_app.py) and must
be PROVEN to behave identically. Where it doesn't, the system itself must say so, precisely, with no
human archaeology. Standing spec underneath everything, owner's words: EVERYTHING IS TRACKED — no UI
component exists, gets touched, or disappears at runtime without being named in the live log and
cross-checked against the ledger. No mysteries, ever.

Two id concepts, do NOT collapse them (this confusion cost owner trust once already):
  Ledger id — computed by parsing (idgen.py); every Kotlin source node has one; never injected.
  walkTag insertion — inject_emitid.py writes `.walkTag("<ledger id>")` into Kotlin source so the SAME
  id is visible at runtime; the transpile carries it into Python for free. Insertion is a replay-stable
  handle, NOT the tracking itself — the tracking catch-all is the runtime construction hook
  (identity.py on py, semantics enumeration on kt) + loud ledger cross-check (ORACLE UNKNOWN).

## SESSION 2026-07-12 — B14 + B08 FIXED (workout feature ALIVE on py); faithful journey runs end-to-end

THE HEADLINE: the owner's faithful directed journey now runs END-TO-END on py, both tails: 9a (finish
early -> workout_cooldown, 24/24 steps) and 9b (log all sets to natural completion -> cooldown ->
summary -> today, 27/27 steps). B14 was NOT a read-before-write race — it was THREE stacked runtime
bugs (full detail: BUG_PROFILE.md B14): (1) navigation.py's NavHost handed destination lambdas a Stub
instead of the live back-stack entry, so backStackEntry.arguments.getString(...) yielded the string
"<stub getString>" and warmup navigated to literally execution/<stub getString> — the real session row
sat in the DB under its UUID the whole time (probe evidence; fix: _call_dest passes the real
_BackEntry, androidx semantics); (2) room.py Database.execute committed mid-withTransaction and the
resulting failed ROLLBACK masked everything ("cannot rollback - no transaction is active") — this
killed completeSession/Finish before the nav emit (fix: no commit at _txn_depth>0; a rollback failure
never replaces the original exception); (3) the numeric wrappers lacked Kotlin's NAMED operator
methods (`?.div(60)` transpiles to a literal .div() CALL) — AttributeError in Today's weekly recompute
the first time a completed session flowed through the live combine chain (fix: named operator family
on _NumOps, numbers.py). B08 (settings->exercises dead nav) NO LONGER REPRODUCES after these fixes
(probe_b08: route settings -> exercises, clean) — same nav-stub root, closed by the same fix.

NEW INSTRUMENT (B17): kivy_kit._fire swallowed ALL handler exceptions with a bare `pass` — a broken tap
was indistinguishable from a working one (this hid bug 2 above for a whole arc: Finish "did nothing"
while its handler was throwing). Now: loud FIRE-ERROR line + kivy_kit.LAST_FIRE_ERROR, recorded per
scenario step as fire_error. BFS-walker adoption of the same read is a pending follow-up.

FAITHFUL SCENARIO VARIANTS (scenario.py argv[1]; ScenarioTest.kt mirrors as three @Test methods
runScenario / runScenarioFaithfulEarlyFinish / runScenarioFaithfulComplete): faithful_early_finish
(default, 9a) / faithful_complete (9b) / v1_pathfirst (old journey verbatim, old output paths). Fresh
seed: WALK_SEED=fresh env -> run_app.build_app_composition seeds onboardingCompleted=False and nothing
else (py mirror of kt -Dwalk.seed=fresh, field-for-field; kt side selects fresh per test method, no new
-D flag needed). New step kinds: set_text ("42" convention; kt performTextReplacement) and
tap_text_until_gone (repeat-tap until the label leaves the screen; loud runaway guard). Onboarding IS
the natural path+program enrollment flow (PATH_SELECTION + PROGRAM_SELECTION are onboarding steps — no
Browse-Programs detour). Discovery corrections that matter: calibration's mode-choice screen is
BYPASSED when experience is skipped (kt OnboardingScreen.kt:700 effectiveMode — py matches kt, NOT a
divergence); "Start " needs its trailing space (bare "Start" matched "Starts strong…"); select_program
pinned to "3-Day Strength" text (kt semantics Roles can't distinguish IconButton/Card kinds, so text
targets are the cross-engine-stable form; kt tap_kind("IconButton") is mirrored as "icon-only
clickable, label==kind"). ARGV SCAR: Kivy's Window import rewrites sys.argv — scenario.py reads the
variant from _ORIG_ARGV saved BEFORE `import walker` (the first faithful_complete invocation silently
ran the default variant).

QUEUED: 246 kt scenario (all three variants in one run — doubles as the COMPILE CHECK for the
sandbox-authored ScenarioTest.kt edits) · 247 capture into results/246_*. The kt run is the parity
check for the whole journey (kt screenshots vs py's render/walks/scenario_faithful_*). Diagnostic
probes kept in render/: probe_b14.py, probe_finish.py, probe_b08.py. NOTE: the runtime fixes touch
walking-relevant layers (navigation/room/numbers) — prior py bundles (238/240/242) predate them; the
next py capture walk re-baselines.

## SESSION 2026-07-11/12 — bug-fixing arc + DIRECTED SCENARIO RUNNER (context still current; B14/B08 statuses below are SUPERSEDED by the block above)

THE BIG SHIFT: the atlas is now REAL and TWO-SIDED, and the primary instrument changed. The aimless BFS
walker (render/walker.py) reboots the WHOLE Kivy app per edge for hermeticity — which means it can NEVER
build up app-state (no path selected, no program enrolled, no workout in progress), so it only ever maps
the blank seeded app, and it is SLOW (~14s/step; a 400-step walk = ~93 min). The fix is the DIRECTED
SCENARIO RUNNER: one stateful session, a scripted sequence of taps, screenshot per step. render/scenario.py
(py) ran the full journey in ~17s and REACHED rich states the BFS walker structurally cannot (Home showing
an enrolled program's weekly schedule). ScenarioTest.kt is the kt mirror (host: `./gradlew :app:test... --tests
"com.sara.workoutforlife.walk.ScenarioTest"`). render/atlas/scenario_side_by_side.html = kt|py per-step.
USE THE SCENARIO RUNNER for first-few-taps / directed debugging; the BFS walker is for breadth coverage only.

NEW LIVING ARTIFACT: PseudoCoup_v0/BUG_PROFILE.md — the catalog of every kt↔py divergence, clustered to find
shared causes. Keep it updated. The model that emerged: most workout-flow "bugs" collapse into ONE root (B14).

BUGS THIS SESSION (full detail + status in BUG_PROFILE.md):
  FIXED + verified:
  - B07 "Finish workout does nothing" / ALL one-shot SharedFlow events dead on py. Root: runtime
    coroutines.py MutableSharedFlow.emit/tryEmit only buffered, never notified registered collectors, so
    LaunchedEffect{flow.collect} events emitted after subscribe were dropped. Fixed (_deliver notifies
    listeners). GENERAL: 8 ViewModels. Confirmed: py reached workout_cooldown (impossible before).
  - B12 workout-flow state explosion. Root: py walker read the CONCRETE route (app.nc.currentRoute() ->
    execution/abc-123) baking session UUIDs into state_id; kt reads the PATTERN. Fixed: walker.py
    _route_pattern(app) (currentBackStackEntry.destination.route) at all 6 state-route points. Also erases
    the concrete-vs-pattern atlas mismatch. Confirmed run 242: 7 execution states (was 22+), pattern routes.
  - py walker TEARDOWN HANG: Kivy/SDL2 native teardown hangs after ~5 App-restart cycles. Fixed with a
    guarded os._exit(0) after successful final write (errors still surface nonzero).
  - B11 loud stub-degradation instrument BUILT (autostub DEGRADATIONS + STUB_LOUD/STUB_STRICT +
    degradation_report). Finding: the FULL-APP runtime has ZERO degradations — the runtime is fairly
    complete; remaining bugs are real logic/wiring, not silent stubs.
  DISPROVEN (not bugs):
  - B01 "DB mismatch": seed code identical AND py seed result correct/complete (24 programs, 182 exercises).
  - B03 "RPE buttons": workoutMode is GLOBAL (UserEntity) — RPE controls correct by design.
  OPEN — the real remaining work:
  - B14 (HIGH): WorkoutExecutionScreen shows "Session not found" (blank) right after the session row is
    created — a read-before-write RACE in the transpiled coroutine/data layer. This is the ROOT blocking the
    whole workout feature (B02 "launch crash", B04/B06/B07-symptoms all trace here). Fix this next.
  - B09: Programs screen — py lists all 24 sample programs; kt correctly shows "No programs yet" because
    ProgramsScreen FILTERS by ACTIVE PATH (empty when none selected). py's filter (ProgramsViewModel combine)
    is not applied. Confirmed visually (kt 236 bundle vs py 242 bundle).
  - B08: settings->exercises tap does nothing on py (dead nav). Blocks the whole exercises branch.
  - B15: path-enrollment and program-enrollment are separate systems, can be contradictory. Verify vs kt.
  - B16 (instrument): `import walker` (via interact.py) disables kivy_kit.OVERLAYS_ENABLED at import time —
    breaks popup/dialog taps in the BFS walker too. Fix upstream.

OWNER'S DIRECTED JOURNEY (their exact ordered list — the scenario to run FAITHFULLY next; my first run
DISTORTED it by skipping onboarding, starting at Home, and routing program-selection through the buggy
Browse-Programs screen — do NOT repeat that):
  (1) onboarding (skip the questions) (2) select path (3) select program (4) home screen (5) start workout
  (6) increment weight (7) log sets (8) log set and next exercise (9a) click Finish before the end (verify
  the button) (9b) continue until the workout finishes. Faithful version = fresh-seed onboarding -> path ->
  program via the NATURAL enrollment flow -> Home -> workout. walk.seed=fresh gives onboardingCompleted=false.

INFRA changes this session: build.gradle.kts forwards walk.capture + walk.seed (allowlist) and sets test JVM
maxHeapSize=4g (the -Xmx2g on the gradle line sizes the DAEMON, not the forked test JVM — that caused an OOM
mid-walk). Flag values MUST be =true, not =1 (Kotlin String.toBoolean() only accepts "true"). kt bundle =
run 236 (180 states/screenshots, -Dwalk.capture). py bundle = run 242 (51 states, WALK_CAPTURE env).
nav_graph.py + log_148: static screen graph (29 screens/65 edges) + reachability diff -> microVM NOT forced
for any screen (all reachable by nav and/or DB seed). Overlay capture SOLVED (PixelProbeTest per-compose-root
draw + fire OnClick semantics action, NOT a bare performClick which taps off-screen coords).

RUN THE REAL KT APP (emulator, owner-facing): open ~/Programming/WFL_MixingCenter/WFL (the INNER Gradle root
— settings.gradle.kts is there — NOT the outer Python folder) in Android Studio, Run 'app'. applicationId =
com.sara.workoutforlife/.MainActivity. `adb shell pm clear com.sara.workoutforlife` for fresh onboarding.
"cmd: Can't find service: package" on install = emulator not fully booted (wait for sys.boot_completed=1).

## The plan (owner's design, decided 2026-07-10; full records: WFL DevComms/log_143 + log_144)

Build a side-by-side HTML ATLAS of both apps. One page per screen-state: kt screenshot beside py
screenshot, each overlaid with the OBSERVED boundaries of its interactive components, differences
visible, interactive regions clickable — a click follows the recorded edge to the destination state's
page. A clickable twin of both apps at once.

How, per owner decisions:
1. MAP BEFORE NAVIGATING: every screen gets its full one-tap-deep map before any deeper exploration.
   Overlays (dialogs/sheets) are just states — the settled-tree hash already distinguishes them.
2. BOUNDARIES BY REAL TAPS, LOG AS SENSOR: a tap either makes a component announce its inserted id in
   the log, or it hit nothing. Boundaries found by SEARCH, not brute force: the live mount log says
   what's on screen and roughly where; a few taps confirm; bisection finds edges; nested components
   same logic. NO randomness — a tap answering with an id the mount list didn't predict is itself a
   loud defect (the mystery detector comes free from the cross-check).
3. SAVED STATES make taps constant-time: py = fork() (child takes the tap and dies, parent keeps the
   screen); kt = qemu/kvm microVM snapshot (owner's choice; laptop RAM is tight, 48GB swap available).
4. ASYMMETRIC BUNDLES: kt is walked/screenshotted/boundary-mapped ONCE into a frozen in-repo bundle
   stamped with the kt commit hash (flat-UI PNGs, whole bundle ~MBs). py regenerates its bundle every
   iteration and is diffed against the frozen kt bundle.
5. Defects handled as they surface — no separate defect phase.

## Where it stands right now

DONE and host-verified this arc: walkTag insertion is app-wide on both engines (86 files + 973
added-modifier args; runs 189/194 prove it compiles); both walkers resolve actions by inserted id
(py run 196: 274 exact-walkid vs 26 ordinal-fallback; kt run 199: 59 exact-walkid, 0 missing); kt's
replay-mount contamination is FIXED (NavController back stack restored across scenario.recreate() —
mountFreshApp now pops to start destination; all 67 replay mounts landed route=today in run 199).

IN FLIGHT (queued host runs — owner runs `python3 tools/walk_service.py`, results land in
DevComms/hostruns/results/):
  204/205 pixel probe rerun — the atlas's screenshot mechanism. First try (202) timed out inside
  captureToImage: Robolectric needs robolectric.pixelCopyRenderMode=hardware in the TEST JVM.
  204 must yield real PNGs in results/204_pixelprobe/.
  206/207 kt walk, 200 steps — the first kt walk whose budget flags actually arrive (see next line).
  202_py_walk_exhaust (running/ran) — 2000-step resumed py walk. ORIGIN UNACCOUNTED: written by no
  reporting agent nor the orchestrator; content benign; accounting failure on record.

CRITICAL CORRECTION discovered via the pixel-probe failure: WFL/app/build.gradle.kts NEVER forwarded
-D properties into the forked test JVM. Every kt walk this arc ran the test's internal 60-step default;
-Dwalk.steps/-Dwalk.reset never arrived. So there is NO trustworthy kt state graph yet — run 199's
33 states / 60 edges is a 60-budget walk exhausting normally (its earlier readings as "frontier defect"
and "legitimate completion" are both retracted). Forwarding is now added (walk.* + pixelCopyRenderMode);
run 206 is the verification. Treat ALL prior kt coverage numbers as 60-budget artifacts.

KNOWN OPEN DEFECT (py twin divergence, the kind this project exists to catch): on route=settings, the
action label='Exercises / Browse, favourite...' handler=onClick NAVIGATES on kt (settings->exercises)
but does NOTHING on py (settings->settings, silent, reproduced twice in run 196). Blocks py from
exercises/gym_list/settings_notifications/wins. Possibly related: 26 LookupErrors clustered on
Settings/ModalBottomSheet.

## Next steps, in order

1. Read 204's PNGs (results/204_pixelprobe/) — screenshot mechanism proven or diagnose.
2. Read 206's walk (results/206_*) — first honest kt graph; check REPLAY-MOUNT all route=today and
   steps actually spent.
3. Build the frozen kt bundle: walk + screenshot per state + boundary maps (tap-grid per log_143).
4. py bundle, same shape; first atlas pages; diff.
5. En route: the settings divergence defect; Phase 6 id cross-check (kt emits == py emits == ledger);
   cleanup pile (legacy WalkEmit.emitId statements in TodayScreen.kt; today FAB untagged, log_141;
   injector nav-gate hardening, log_139; build_mixingcenter.py should assert tree_sitter importable).

## Operational (how to actually work here — scars included)

Host-run loop: write request JSON to DevComms/hostruns/requests/NNN_name.json {"id","cwd","cmd",
"timeout"} — id must equal filename; cmd[0] must be one of gradlew/python3/xvfb-run/adb/git; owner runs
tools/walk_service.py; results/NNN.log+.json appear; a request with no result file re-runs on service
restart. Tee/copy artifacts you need into results/ via a follow-up python3 -c request (gradle swallows
test stdout; build dirs are not results).
Commits: owner runs ~/Programming/PseudoCoup_v0/WFL_and_PseudoCoup_v0_git_push.sh after turns; write
the message to DevComms/next_commit_message.txt (script consumes it; arg overrides; fallback "update").
Sandbox: bash 45s hard cap; mounts can CREATE but not DELETE files (stale .git/index.lock = owner's
push script clears it; never bypass with plumbing); host paths differ from file-tool paths; kivy runs
in-sandbox (xvfb-run -a; ~/Programming symlinks needed); NEVER hand-edit transpiled py — regenerate
via tools/pseudokotlin/build_mixingcenter.py (which requires python tree_sitter INSTALLED, else every
enum column silently degrades to text — this happened, run 186 era).
Owner communication protocol is saved and binding: direct answers first, keep the owner's words, anchor
every abstraction, no unexplained jargon, SHOW with smallest-example evidence rather than describe,
never present your own inventions as settled decisions — proposals are labeled proposals, and
architecture/ontology/naming decisions are the OWNER'S. Subagent briefs must carry file fences, exact
gates, stop-rules, and a no-silent-actions rule (see UNACCOUNTED file above for why).
Walk budgets + progress display — OWNER MANDATE 2026-07-10, NON-REMOVABLE (owner has had to
re-demand a working progress indicator repeatedly; it eroded because nothing failed when the counter
vanished — that is now closed): a percentage is shown ONLY as the walk's own "PROGRESS spent=A/B"
counter over its own --steps/-Dwalk.steps budget. py counter = walker.py stdout; kt counter = read
from <cwd>/app/build/walks/kt_activations.log (gradle swallows test stdout). Unbudgeted runs show
elapsed + prior-median, labeled "no step counter", NEVER a percentage. ENFORCED: a budgeted walk
exiting rc=0 with zero counter lines gets "progress_defect" in its result json + terminal/history
banner; tools/test_walk_service_progress.py fails if the enforcement or counter plumbing is removed —
run it before touching walk_service.py. KT EMITTER STATUS: WalkRecorderTest must print
"PROGRESS spent=A/B" into kt_activations.log each loop iteration — until that lands (WFL repo),
every green kt walk will correctly flag PROGRESS DEFECT.

# ===================== HISTORY BELOW (chronological, newest first; superseded) =====================

# Session handoff — 2026-07-10 LATE (KT CEILING ROOT-CAUSED: mount drift, NOT identity; runs 194-201 done, superseded by the block above)

THE BIG FINDING (Opus diagnosis, DevComms/log_140_kt_ceiling_diagnosis.md -- read it): the kt walker's
7-state ceiling that survived THREE identity redesigns is NOT an identity problem. Run 189's captured
RESOLVE trail proves: discovery works (all 7 boot ordinals fire), but every subsequent fresh replay mount
NAVIGATES TO THE WRONG SCREEN -- the same "This workout has no exercises / Go back / Finish" execution
dead-end -- regardless of which path prefix it should reproduce. The recorded node isn't on the screen
that actually rendered, so NO identity key (however unique) can match; walkApp drops each failed frame,
frontier empties at 10/200 steps (kt_walk.json meta steps_this_run=10 -- budget was never exhausted).
Ranked hypotheses: H1 stale nav/coroutine/Room-flow state bleeding across mounts (most likely), H2 FAB
nondeterminism, H3 unsettled lazy tree (largely ruled out). Identity work is DOWNSTREAM of this; do not
invest further in identity until mount reproducibility is fixed.
PROBE LANDED (additive logging only, WalkRecorderTest.kt replayTo): REPLAY-MOUNT (route + expected first
step) + REPLAY-MOUNT-ENUM (settled enumeration head) lines -- grep both in 194_kt_activations.log. If
boot route varies per mount -> H1 confirmed; fix = hermetic per-replay mount (test-source only). This
mirrors the py walker's hermeticity scar (di.reset() per Session, 2026-07-08 block) -- same disease, kt flavor.

INJECTOR EXTENSION LANDED (--add-modifier flag, off by default; DevComms/log_141_injector_add_modifier.md):
adds `modifier = Modifier.walkTag(...)` as a NEW named arg ONLY where the callee provably accepts modifier
(app composables: tree-sitter declaration check; library widgets: curated M3 allowlist; any doubt = skip).
973 added across 49 files; idgen/ledger clean; transpile 256/256; parity 53/53; sandbox smoke shows
NavigationBarItems firing with non-null walk_id. Mid-run the agent caught + fixed a stale-id duplicate-chain
bug and added an _already_walktagged guard (idempotent now). CAVEAT flagged: the today FAB was NOT tagged --
agent claimed TodayScreen.kt "outside the 86-file scope", which contradicts ui/** scoping; bookkeeping
suspect, chase next session. Run 181's risk class re-opened deliberately; run 194 IS the compile check.

BROADENING RESULTS (runs 189-193, pre-extension): py 40 states/188 edges, 96 exact-walkid / 204
ordinal-fallback / 0 missing / 0 collisions at 200 steps -- base#rank holds under real replay load on py.
kt flat at 7/10 (now explained by the mount drift above). walk_diff 4 shared / 3 kt-only / 34 py-only /
166 edge mismatches -- still mostly comparing fallback policies + coverage, not identity.

RUN 194 RESULTS (H1 CONFIRMED + compile green): rc=0 -- the 973 added modifier args COMPILE (run-181 risk
retired); nav items now carry real walk_ids on kt. THE PROBE: 17 REPLAY-MOUNT lines, only 8 route=today;
6 route=execution/{sessionId}, 1 each my_program/paths/progress -- INCLUDING pathLen=0 boot mounts already
sitting on non-boot screens. Stale state across mounts confirmed as THE ceiling cause.
ROOT OBJECT (log_142): the NavController BACK STACK, restored via Android saved-instance-state --
mountFreshApp() uses scenario.recreate(), which runs onSaveInstanceState/onRestore, and AppNavigation's
rememberNavController() persists its back stack through SavedStateRegistry. "Fresh" mounts booted onto
whatever screen the last replay left. Same disease as py's di._DB leak (2026-07-08), kt flavor.
FIX LANDED (test sources only, WalkRecorderTest.kt): mountFreshApp pops the restored back stack to the
graph start destination (public NavController API, only on the test-captured controller; production
MainActivity never passes onNavControllerReady -> app behavior untouched). REPLAY-MOUNT probes kept as
proof. NOT YET HOST-VERIFIED -- run 199 is the check. SUCCESS CRITERIA for 199: every REPLAY-MOUNT
route=today; steps_this_run near 200; states >> 7.

QUEUED (in order): 196 py walk (was killed mid-run by an accidental ctrl-C -- no result file, so the
service re-runs it from --reset on restart, safe) · 197 py capture · 198 walk_diff · 199 kt walk
HERMETIC (the fix's verification) · 200 kt capture · 201 walk_diff again.
PROGRESS BAR v2: walker.py now prints "PROGRESS spent=A/B" (its actual budget counter) each loop
iteration; walk_service reads the LAST of those (falls back to STEP-counting only on old logs). The v1
bar counted "STEP " lines and overcounted (202/200 shown to owner -- STEP-prefixed non-budget markers
like crash tracebacks/frame-exhausted inflated it).

TOOLING THIS BLOCK: walk_service progress bar now REAL for walker.py runs (counts STEP lines vs --steps,
incremental tail reads; shows "step N/M"; "⚠ log quiet Ns" stall indicator after 30s; non-walker runs keep
the estimate, labeled "~Ns-est"). Push script reads DevComms/next_commit_message.txt. Caveat: walker
prints slightly more STEP lines than budget (213 vs 200 in run 191), so the bar can touch 99% early.

# Session handoff — 2026-07-10 (walkTag BROADENED app-wide; runs 189-193 done, superseded by the block above)

GLOSSARY (owner-anchored; do not collapse these two layers again -- doing so cost trust this session):
  Ledger id
      the unique positional-path id idgen.py COMPUTES for every Kotlin source node by parsing.
      Never injected; exists for ALL nodes; ledger_unified.py is the record keyed by it.
      example: AppNavigation's FAB call has a ledger id even though (pre-broadening) its source
      carried no walkTag.
  walkTag (insertion)
      inject_emitid.py writing `.walkTag("<ledger id>")` into Kotlin source so that SAME id is
      present at runtime and the node can announce it. Same id space; injection makes a ledger id
      visible to the running app. Purpose: a replay-stable handle for the walker.
  EVERYTHING IS TRACKED (owner's spec, runtime property, does NOT rest on insertion)
      no component exists/gets touched/disappears at runtime without the system naming it: every
      widget construction -- app code OR imported library -- passes through the runtime's hooked
      node-construction choke point (identity.py on py; semantics enumeration on kt), lands in the
      MOUNT/ACTIVATE log with an identity, and cross-checks against the ledger loudly (ORACLE
      UNKNOWN on failure). Insertion is a stronger handle layered on top where reachable; the
      choke-point hook is the catch-all for what insertion can't reach (e.g. components built
      inside library code).

STATUS: walkTag injection broadened from 2 files to the whole app UI in ONE SHOT (owner's call:
one shot, revert to increments if noticeably broken). 86 kt files (ui/** + navigation/AppNavigation.kt),
+928 walkTag calls, idgen 0 dupes, ledger check clean, re-transpile 256/256 files 0 errors, kt<->py
walkTag count parity 52/52 tagged files exact (the old TodayScreen 90v89 drift did NOT reproduce:
89/89 now). Report: WFL DevComms/log_139_walktag_broadening.md. Kotlin COMPILE NOT YET VERIFIED --
sandbox can't run gradle; host run 189 IS the compile check. REVERT SURFACE if 189 fails: git-level,
258 WFL files (86 kt + 86 py + 86 linemaps); PseudoCoup_v0 untouched.

KNOWN GAP (flagged, owner decision pending): the injector is REWRITE-ONLY (the run-181 fix) -- it
chains onto an existing modifier= but never ADDS one. AppNavigation's NavigationBarItems/FAB pass no
modifier, so the walk's dominant interactive nodes are STILL un-inserted (walk_id=None) after this
broadening. Proposed fix: injector extension that adds `modifier = Modifier.walkTag(...)` as a new
named arg ONLY when the callee provably accepts a modifier param -- re-opens the run-181 risk class,
so gate it on 189's compile result. Owner has not yet said go.

QUEUED HOST RUNS (in order): 189 kt walk 200 steps --reset (doubles as compile check) · 190 captures
kt_walk.json+kt_activations.log into results/ as 189_* · 191 py walk 200 steps --reset · 192 captures
py artifacts as 191_* · 193 walk_diff. Runs 186-188 (this session, pre-broadening): py walk 40 states/
188 edges/10 routes at 200 steps, 300 RESOLVEs all ordinal-fallback, 0 missing; only 4 fired actions
hit tagged nodes (self-loops/known states, so never replayed -> 0 exact-walkid is coherent). walk_diff
188: 4 shared/3 kt-only/34 py-only/167 edge mismatches. CAUTION (retraction enforced): pre-broadening
kt-vs-py coverage numbers compare FALLBACK POLICIES (kt discards unresolvable paths; py ordinal-replays
and never discards), NOT the id mechanism -- do not draw identity conclusions from them.

ALSO THIS SESSION: Phase 5 py side landed + verified (block below). Build bug found: the 2026-07-09
transpile was made with tree_sitter missing -> ALL enum Cols degraded to text -> sqlite crash at seed;
rebuilt correctly (build_mixingcenter.py should assert tree_sitter importability -- unfixed). Push
script now reads DevComms/next_commit_message.txt (arg > file > "update"; file emptied after use).
walk_service progress bar is a median-of-prior-runs ESTIMATE capped at 99% until child exit -- a
possible upgrade: count ^STEP lines vs --steps for walker.py runs. 26 pre-existing LookupError
(ModalBottomSheet/Settings widget-mount) + 2 step timeouts remain open, unrelated.

# Session handoff — 2026-07-09 LATE (Phase 5 PYTHON SIDE LANDED; host runs 186-188 done) (superseded by the block above)

STATUS: Phase 5's Python side is IMPLEMENTED and sandbox-verified; the full host py walk that makes a real
KT-vs-PY comparison possible is QUEUED as requests 186 (the walk: 200 steps, --reset) + 187 (copies py_walk.json + py_activations.log
into results/ as 186_*, per the run-176 capture lesson). Request 185 was REFUSED by walk_service
(cmd[0]="bash" not on ALLOWED list) and could not be deleted from the sandbox (mount can't unlink) --
it is dead, ignore it; 186/187 replace it. Report: WFL_MixingCenter
DevComms/log_138_py_walkid_wiring.md.

WHAT LANDED (committed: PseudoCoup_v0 runtime/compose.py + WFL_MixingCenter render/walker.py):
  - runtime/compose.py: Node.walk_id extracted from the .walkTag(...) op in the modifier chain at Node
    construction (walkTag was previously autostub-swallowed by _Mod.__getattr__ and ignored). Last-wins on
    multiple tags, WALKTAG-MULTI logged. One Node per composable call on py -- tag lands on the SAME node
    that owns the handler, so NO nearestWalkId neighborhood search needed (unlike Compose's wrapper split).
  - walker.py: enumerate_interactive assigns base#rank positionally (rank = position among same-base-id
    nodes in enumeration order -- same scheme run 184 proved on kt); duplicate final ids nulled + logged.
    Steps persist {ordinal, label, handler_kind, bounds_key, walk_id} (snake_case, matches kt progress
    keys; owner decision). Replay: walkId FIRST (exactly 1 match = fire; 0 or >1 = Missing, path discarded,
    MISSING-RESOLVE-CONTEXT/-ENTRY logging); walk_id null = today's raw-ordinal behavior UNCHANGED (owner
    decision: no (label,handlerKind,boundsKey) port to py). Old bare-int progress paths load fine.
    py_walk.json edges[].action now carries walk_id + bounds_key.
  - VERIFIED (Opus reviewer, real sandbox walk): all spec items pass; exact-walkid fires (proven by
    injection), ordinal-fallback fires, missing path logs, old progress loads, walk files restored
    byte-identical after smoke runs.

BUILD BUG FOUND AND FIXED IN PASSING (the real reason walker boots crashed): the 2026-07-09 transpiled
build was produced with python tree_sitter MISSING, so resolve.app_enums() returned empty and EVERY enum
column in the data layer degraded to plain text (sqlite3 InterfaceError binding CardioType at seed).
Rebuilt with tree_sitter installed: 256 files, 0 errors, 19 entity files regained typed enum Cols,
walker boots clean with no shim. Build outputs left UNCOMMITTED per standing policy (regenerate via
build_mixingcenter.py). LESSON: build_mixingcenter.py should probably assert tree_sitter importability.

KNOWN, EXPECTED, NOT DEFECTS:
  - Boot-state interactive nodes (nav Surface/NavigationBarItems/FAB) all have walk_id=None -- they live in
    untagged nav/AppNavigation (the known instrumentation-coverage gap). Tagged ids on the today screen
    currently land on Card/Column containers, not the interactives; broadening walkTag to clickables is the
    same pending INSTRUMENTATION COVERAGE item as before.
  - walkTag count drift: TodayScreen.py has 89, TodayScreen.kt now has 90 (was byte-identical at 89 in
    phase 3). 1-off, cause not chased this session -- check whether a kt-side injector re-run added one.
  - 26 pre-existing LookupError widget-mount issues (Settings/Dropdown) surfaced in the smoke walk,
    unrelated to this change.

NEXT (in order): host runs 186+187 (py walk + capture) then walk_diff for the FIRST real KT-vs-PY walkId comparison;
Phase 6 id cross-check; emitId-statement cleanup in TodayScreen.kt; broaden walkTag instrumentation.

# Session handoff — 2026-07-09 (post-run 184) UNIFIED LEDGER / UNIQUE-ID REDESIGN, Phases 1-5 (superseded by the block above)

STATUS: a new redesign is underway, superseding the boundsKey identity work below. FULL PLAN:
DevComms/log_137_unified_ledger_plan.md. AUDIT that motivated it: DevComms/log_136_ledger_id_uniqueness_audit.md.
CORE IDEA (owner's design): every callable emits a UNIQUE id, born from tree-sitter on the KOTLIN side,
injected into Kotlin source, carried into Python by the transpile for free, and the walker matches on that
id instead of reconstructing identity from (label, handlerKind, boundsKey). One id space spans both apps.

PHASES 1-4 -- DONE and verified this session:
  (1) idgen.py (tools/pseudokotlin/) -- assigns a UNIQUE positional-path id to every Kotlin source node
      (segment = "<childIndex>:<nodeKind>", index at EVERY node). Whole-app: 16979 nodes, 0 duplicate ids.
  (2) Injection + runtime emission. Host run 180 PROVED emission fires at runtime with a per-instance
      counter (one source id fired as instance 0..N).
  (3) Transpile carries the ids 1:1 into Python. Re-ran the transpile after the Phase-5 change: e.g.
      ui/today/TodayScreen.py now has 89 walkTag ids, BYTE-IDENTICAL to TodayScreen.kt. IMPORTANT: the
      Python the walker runs is the TRANSPILED MIRROR (WFL_MixingCenter/ui/*.py via run_app), NOT the
      separate hand-written kit at WFL_PseudoCoup/src -- that kit is only for the fidelity ledger, ignore it.
  (4) ledger_unified.py -- ONE ledger keyed by id, one record per node, whole app (16979 entries, asserted:
      entry_count == node_count, 0 dupes). Collapses the old ledger.py/ui_ledger.py/kit_ledger.py record-
      keeping. (ledger.py's PYTHON exec-introspect cross-check deferred to Phase 6.)

PHASE 5 -- walker matches on the id. KOTLIN SIDE IN PROGRESS, PYTHON SIDE NOT STARTED.
  Mechanism landed (WFL_MixingCenter): core/debug/WalkEmit.kt defines `WalkId` (a Compose SemanticsPropertyKey)
  and `Modifier.walkTag(id)` which stamps the BASE id onto the node's semantics. WalkRecorderTest.kt reads it:
  `nearestWalkId` searches the node + parents(<=3) + children(<=3) for the tag (because Compose puts the tag
  on a WRAPPER node, not the clickable, in the unmerged tree), then INTERPRETS the instance as "base#rank"
  where rank = the node's position among same-id nodes in enumeration order. resolveTarget matches walkId
  FIRST, falls back to (label, handlerKind, boundsKey) for untagged nodes (no regression).
  Two hard-won facts (do NOT re-litigate): (a) the tag lands on a wrapper node -> neighborhood search needed
  (runs 182/183); (b) the instance index MUST be interpreted positionally (base#rank), NOT a running counter
  -- the counter drifts across recompositions so record-time id != replay-time id (run 183 had exact-walkid=0
  for exactly this reason; run 184 fixed it).

WHERE RUN 184 ACTUALLY LANDS (and an earlier overclaim CORRECTED):
  184: BUILD ok, exact-walkid resolves now HAPPEN (3), AMBIGUOUS resolves = 0 (the specific bug the redesign
  targets is gone), BUT 6 MISSING resolves remain (a recorded node not re-found at replay -- still an
  identity failure that drops paths), and coverage is still 7 states / 10 edges.
  CORRECTION: an earlier note in-session claimed "coverage is a navigation problem, not identity" by
  comparing KT's 7 states to "Python's 35". That 35 came from an OLD pre-walkId Python walk (py-side identity,
  render/walks/py_walk.json) -- NOT a comparable run. There is NO live Python walk with walkId yet, so that
  comparison is INVALID and is retracted. Honest position: the ambiguity class is fixed; missing resolves
  remain; what caps KT coverage at 7 is NOT yet determined and needs a real KT-vs-PY comparison.

PENDING (in order):
  - Phase 5 PYTHON side: wire walker.py to install + read walkId (the analog of WalkRecorderTest's wiring),
    then run a Python walk. Only THEN is a real Kotlin-vs-Python comparison possible.
  - Phase 6: id cross-check (KT emits == PY emits == ledger).
  - CLEANUP: TodayScreen.kt currently has a MIX of legacy `WalkEmit.emitId(...)` statements AND `walkTag(...)`
    -- the emitId statements are now redundant, remove them.
  - INSTRUMENTATION COVERAGE: only ui/today + ui/progress screen BODIES are walkTagged; nav/AppNavigation is
    not, so most interactive nodes still use the fallback identity. Broaden once the mechanism is trusted.

RUN LEDGER this arc: 179-180 emitId smoke (180 proved emission) · 181 walkTag compile FAIL (modifier added to
non-widgets like PaddingValues/Stroke -> fixed to _is_widget + rewrite-only) · 182 compiled but walkId=null
(wrapper-node issue) · 183 walkId found but unstable (counter drift) · 184 base#rank stable, exact-walkid
works, coverage flat at 7.

TOOLING: walk_service.py got a live progress bar + idle status + persistent DevComms/hostruns/service_history.log
(runs no longer look hung). git: the recurring commit block is a stale .git/index.lock left by sandbox git
(the mount can create but not delete it); WFL_and_PseudoCoup_v0_git_push.sh was hardened to clear it. No
background processes started or left running.

# Session handoff — 2026-07-09 (post-run 176–178) VERIFICATION: KT RE-FIX 664017d FAILED ON HOST (superseded by the block above; kept as the pre-redesign record)

STATUS: the re-run the block below left QUEUED has now executed. The walk service ran the queued batch --
176 (kt walk, re-fix 664017d, 200-step budget), 177 (walk_diff.py), 178 (mount_diff.py); results in
DevComms/hostruns/results/. OUTCOME: item (1)'s re-fix DID NOT HOLD. kt-walker coverage fell FURTHER
instead of recovering. Item (2) (budget-parity exhaustion runs) stays BLOCKED -- its precondition (664017d
"restores or improves on the ~21-state/43-edge baseline with a clean RESOLVE log") is not met.

WHAT THE RUNS SHOW (one cause; the numbers are the evidence). kt-walker coverage at the same 200-step
budget, across the three states this fix has passed through -- pre-regression baseline, the regressed run
that b70d65e produced, and this re-fix run:

    metric                          pre-regression    regressed run      re-fix run
                                    baseline          169 / 174 / 175    176 / 177 / 178
    kt states reached               ~21 / 43 edges    10 / 18 edges      7 / (not captured)
    mount_diff T1 coords matched    (not on record)   107                50
    mount_diff kt-only pairs        (not on record)   156                98

  - "states" here = shared + kt-only from walk_diff (the metric that makes run 169 = 10). Evidence:
    177_walk_diff_refix.log line 3 "TOTAL: 4 shared states, 3 kt-only" (= 7); 174_walk_diff_exhaustion.log
    line 3 "4 shared states, 6 kt-only" (= 10, the regressed run); ~21/43 baseline is from the block below
    (pre-b70d65e).
  - coords matched: 178_mount_diff_refix.log line 1098 "T1: 50 coordinates matched" vs
    175_mount_diff_exhaustion.log "T1: 107 coordinates matched". kt-only pairs 98 vs 156 from the same two
    lines.

CAUSE (inferred from the coverage direction; the per-path RESOLVE trail is NOT in the captured results --
see UNVERIFIED below): 664017d's rule -- "treat Ambiguous the same as Missing: never fire a match you
cannot uniquely identify, discard the path" -- over-corrected. boundsKey (the node's boundsInRoot rounded
to whole pixels) is not narrowing the ambiguous (label, handlerKind) match sets down to exactly one node
often enough. So the paths that b70d65e used to fire (wrongly, on a guessed node) now resolve Ambiguous and
get DISCARDED, and discarding them drops coverage BELOW even the regressed run: 7 states vs 10 regressed vs
the ~21 baseline the fix was meant to restore. The fix removed the dishonesty (it no longer fires a node it
cannot identify) but at the cost of exploring almost nothing. The FAB case from the block below is exactly
where boundsKey fails to discriminate: an icon-only FAB whose label falls back to nodeKind = "Button", a
(label="Button", handlerKind="onClick") pair shared across screens, and boundsKey did not uniquely narrow
it.

UNVERIFIED FROM CAPTURED ARTIFACTS: run 176's captured result (176_kt_walk_resolve_refix.log) is gradle
stdout ONLY -- "BUILD SUCCESSFUL in 59s", returncode 0, no walk summary. The kt_walk.json state/edge counts
and the new MISSING-RESOLVE-CONTEXT / MISSING-RESOLVE-ENTRY RESOLVE trail this fix added live in
WFL_MixingCenter (WFL/app/build/walks/kt_activations.log, kt_walk.json) and were NOT copied into
DevComms/hostruns/results/. The coverage drop is real and visible because walk_diff (177) and mount_diff
(178) read those host logs directly and reported on them -- but the per-path reasons (how many paths
resolved Ambiguous vs Missing, and what boundsKey each searched for against what settled enumeration) are
NOT in the captured artifacts and have not been read this session. TO CLOSE THIS: the next run request must
tee WFL/app/build/walks/kt_activations.log and kt_walk.json into results/ alongside the gradle stdout
(request 176 captured neither -- see DevComms/hostruns/requests/176_kt_walk_resolve_refix.json, cmd has no
tee).

NEXT DECISION (owner's -- this is a naming/ontology call about what "node identity" IS in the walker, so
deferred, not chosen this session): discard-on-ambiguous as it stands trades false coverage for near-zero
coverage. Two directions:
  (a) make the identity discriminator stronger so fewer matches are ambiguous in the first place --
      (label, handlerKind, boundsKey) is not enough for the icon-only FAB. Candidate: fold route + subtree
      structure into the identity, not just those three fields.
  (b) keep discard-on-ambiguous but stop the ambiguity forming at all -- capture a stable identity at
      RECORD time and persist it, rather than reconstructing one at fire time, so a path always resolves
      to the same node it was recorded against.

CANONICAL ORDERING: unchanged, still held pending evidence.
SEED ROOTS: unchanged, still deferred.
No PseudoCoup_v0 transpiler/tooling code touched this session. No background processes started or left
running.

# Session handoff — 2026-07-09 FRONTIER ALIGNMENT PHASE (superseded by the block above; kept as the pre-run record -- it explains why runs 176–178 were queued)

STATUS: owner approved a two-item frontier-alignment plan this session. Item (1) REGRESSED on its first
host run, diagnosed, and re-fixed this session (WFL_MixingCenter commit 664017d) -- re-run queued, not yet
executed. Item (2) is still QUEUED, blocked on item (1)'s re-run confirming the fix actually holds.

(1) KT MISFIRE FIX -- LANDED then REGRESSED then RE-FIXED (WFL_MixingCenter commits b70d65e -> 664017d,
test sources only, WFL/app/src/test/java/com/sara/workoutforlife/walk/WalkRecorderTest.kt).

  ORIGINAL FIX (b70d65e): fixed the kt walker's self-documented ANOMALY 1 settle-race misfires (bare
  ordinal captured at one settled enumeration silently drifting onto a DIFFERENT node when replayed against
  a later, independently-settled mount). Resolved fire targets by (label, handler_kind) identity within the
  just-settled enumeration instead of raw ordinal position; an ambiguous match (>1 node sharing that
  (label, handler_kind) pair) fell back to `ordinal`'s position WITHIN the matching subset.

  REGRESSION (first real host run of b70d65e, DevComms/hostruns/results/169_kt_walk_exhaustion.log +
  WFL/app/build/walks/kt_activations.log): 200-step budget, 98s runtime, finished at only 10 states/18
  edges -- WORSE than the pre-b70d65e baseline (21 states/43 edges) the fix was meant to improve on. Only
  38 total RESOLVE lines logged in the whole run. Root cause, confirmed directly against the RESOLVE/
  ACTIVATE trail: the AMBIGUOUS fallback ("ordinal's position WITHIN the matching subset") was ITSELF a
  blind stale-position guess -- the exact class of bug b70d65e was supposed to eliminate, one level deeper.
  Evidence: frontier path [0] on route "today" is a bare icon-only FAB whose subtreeText() has no text
  anywhere in its subtree, so its label falls back to nodeKind(node) = the generic string "Button" -- not a
  distinguishing identity. That (label="Button", handlerKind="onClick") pair matches MULTIPLE unrelated
  nodes across MULTIPLE unrelated screens. Replaying path [0] four separate times in one run (nActions
  discovery + fire, called across separate walkApp() iterations off the same frontier frame) landed on FOUR
  DIFFERENT ROUTES: "today" (twice), "execution/{sessionId}" (matchCount=3, ambiguous), and "log_cardio"
  (kt_activations.log lines 14679/14681/15602/19149/22845) -- the ambiguous-fallback guess picked a
  different actual node each time. This corrupted the walk two ways at once: (a) a frame's own
  nActions-discovery replay and its later fire replay could land on two different mounts' states, so
  frame.nActions was computed against a tree the fire step never revisited; (b) newly-discovered frontier
  Frames carried this same non-unique (label, handlerKind) forward into their own PathStep, so later
  replays of THOSE paths sometimes found the recorded pair nowhere in a further mount's tree at all
  ("RESOLVE ... label=UNKNOWN method=missing"), returned false from replayTo(), and were discarded as a
  ReplayError instead of explored -- which is why the walk exhausted its 200-step budget in 98s having
  logged only 38 RESOLVE calls total.

  RE-FIX (this session, commit 664017d): stop guessing on ambiguity. InteractiveRef/PathStep now also carry
  `boundsKey` (the node's own boundsInRoot, rounded to whole pixels -- already computed elsewhere in the
  file for the ACTIVATE log's origin=, so free to capture here too). resolveTarget() uses boundsKey ONLY to
  NARROW an already-ambiguous (label, handlerKind) match set to the exact recorded screen position -- never
  as a sole identity key on its own, and never a position-guess fallback. If boundsKey narrows the set to
  exactly one node, that resolution is Exact; if it doesn't (key absent from the match set, or still >1
  match), resolution is honestly Ambiguous/Missing -- replayTo() now treats Ambiguous the same as Missing
  (returns false; never fires a match it cannot uniquely identify), same principle b70d65e already applied
  to Missing. NOTHING-HIDDEN RULE: every failed resolution (Ambiguous or Missing) now logs the exact
  (label, handlerKind, boundsKey) it searched for AND up to 10 entries of the settled enumeration it
  actually searched against (new MISSING-RESOLVE-CONTEXT / MISSING-RESOLVE-ENTRY log lines) -- the original
  regression's kt_activations.log recorded only "label=UNKNOWN handler=UNKNOWN method=missing" with no way
  to tell from the log alone what was being searched for or what was actually on screen; reconstructing the
  actual cause this session required cross-referencing RESOLVE/ACTIVATE lines by hand across the whole log,
  which this fix's logging closes. loadProgress() now explicitly handles a THIRD progress-file generation
  (bare-ordinal legacy pre-b70d65e, then label/handlerKind-only from b70d65e itself, now +boundsKey from
  this fix), using has()-guarded reads so a progress file missing the bounds_key key degrades to null
  instead of throwing (org.json's isNull() throws on a genuinely absent key, not just JSONObject.NULL).
  ordinal's semantics in the persisted kt_walk.json WALK FORMAT remain UNCHANGED throughout both sessions --
  ActionRec.ordinal still records the enumeration index at RECORD time; only fire-time RESOLUTION logic
  changed. UNVERIFIED ON HOST: this fix itself has not been run yet -- diagnosed and re-fixed from the
  169 hostrun's logs only (per this session's constraints, gradle was not runnable here); the next host run
  is the real verification, and per this task's own instructions IS the queued re-run referenced in STATUS
  above (folded into item (2)'s budget-parity runs rather than a separate item).

(2) BUDGET-PARITY EXHAUSTION RUNS -- QUEUED, not started. BLOCKED on confirming item (1)'s re-fix (commit
664017d) actually resolves the regression on a real host run first -- re-running budget-parity comparisons
against a still-broken kt walker would just reproduce the same corrupted-coverage numbers. Once a host run
confirms 664017d restores (or improves on) the pre-regression ~21-state/43-edge baseline with a clean
RESOLVE log (no unexplained Ambiguous/Missing clusters), proceed to: re-run both engines' walkers at
matched step budgets to get a genuine apples-to-apples exhaustion comparison (kt's original 21-state
exhaustion was partly an artifact of the ANOMALY 1 bug, not a true structural ceiling).

CANONICAL ORDERING: held pending evidence -- not decided this session, no change.

SEED ROOTS: deferred. A structural-reachability survey found nothing currently unreachable from the
existing seed/boot state on either engine, so there is no known gap forcing new seed roots yet; revisit if
the queued exhaustion runs (item 2) surface one.

No PseudoCoup_v0 transpiler/tooling code was touched this session -- the fix is WFL_MixingCenter-only
(test sources). No background processes were started by this session; none were left running.

# Session handoff — 2026-07-08 ORACLE SCAN GAP CLOSED + T1 DIFFER ROWS CLASSIFIED (read this block first)

STATUS: both open items from the 165_py_walk_dense_linemaps.log full host walk (DevComms/hostruns/results/
165_py_walk_dense_linemaps.log, dense linemaps, 0 approximate mounts) are CLOSED this session.

(1) ORACLE SCAN GAP CLOSED (WFL_MixingCenter commit 30d726a): the log's 22 "ORACLE UNKNOWN" lines were all
ONE distinct coordinate (`ui/components/CompactControls.kt:118 kind=Text`), traced to a registry-scan gap,
NOT a misattribution or an out-of-scan-root file. Root cause: compose.py's `_composable(kind)` factory
(shared by BasicTextField/TextField/OutlinedTextField) special-cases a `decorationBox=` keyword by calling
the slot with a synthetic `_inner` that builds a bare `Node("Text")` the instant the slot's own lambda
invokes its `inner`/`innerTextField` parameter — there is genuinely no `Text(...)` token anywhere in app
source at that coordinate (CompactControls.py's `return inner()`, linemap-exact to kt:118); the name "Text"
is synthesized one frame away, inside the runtime. `oracle_registry.py`'s existing scan (`Call(func=Name(
PascalCase))`) can never discover this by construction — no widening of recognized call SHAPES would find
it, since app source calls a lowercase, parameter-bound name there. FIX: added a second registry-scan pass
keyed off the `decorationBox=` keyword itself (resolve its value to the slot body — inline Lambda or a
same-file nested def — find every call to that body's own first parameter recursively through nested
wrapper lambdas, register each resolved coordinate as "Text"). Registry 2272->2273 entries. Verified live:
sandboxed short walker.py boot (--steps 15 --resume) shows all previously-UNKNOWN CompactControls.kt:118
occurrences now print "ORACLE OK"; the repo's second decorationBox site (WorkoutExecutionScreen.py) also
resolves correctly. EXPECTED REMAINDER: 0 UNKNOWN for the boot-reachable subset this session verified; a
coordinate this fix does NOT and cannot cover is one where a live component's origin resolves to a kt
coordinate with NO backing composable declaration/primitive/decorationBox shape at all (a genuinely new,
different scan gap or a real identity.py misattribution) — none such were found in this log (all 22 lines
were the one decorationBox coordinate), but the next full host walk is what confirms 0 UNKNOWN at full
(non-boot-limited) coverage.

(2) T1 DENSITY-DIFFER ROWS CLASSIFIED (WFL_MixingCenter commit 3600e1e, render/walks/density_differ_analysis.md
2026-07-08 section): mount_diff_report.txt's T1 set is now 14 (coord,kind) rows (was 16), coverage having
grown 58->83 T1-matched coordinates. 7 rows are the already-classified B (real per-visit variation) rows
carried forward unchanged (ProgressScreen.kt:284, WflCard.kt:51/62/80, WinsHomeCard.kt:127/73/87). The 7 NEW
rows (WinsHomeCard.kt:71/74/83/92/166/167/172) were investigated with the same method (exact linemap hits,
per-STATE-block mount counts on both engines) and are ALL class B too — same already-documented root cause
(py's BFS-replay walk sampled 2 extra non-ANALYTICS `progress` sub-states kt's single-path walk never
reached; every one of the 7 mounts 1:1 with kt whenever WinsHomeCard actually renders). **NO CLASS-A ROW
FOUND** — 0 of 14 current T1 DENSITY-DIFFER rows show real twin divergence; nothing from this pass requires
owner escalation.

Sandbox process cleanup confirmed (ps aux showed no leftover xvfb/python3/walker.py processes after
verification runs). No PseudoCoup_v0 code was touched this session — both fixes are WFL_MixingCenter-only
(render/oracle_registry.py, render/walks/density_differ_analysis.md).

# Session handoff — 2026-07-08 LINEMAP DENSITY FIX (read this block first)

LINEMAP DENSITY FIX (tools/pseudokotlin/nodes/statements.py, `_distribute()`): the density-differ
analysis (render/walks/density_differ_analysis.md, rows 1/3/4/5/6/8/13/16) traced 9 of 16 T1
DENSITY-DIFFER rows to ONE transpiler gap -- `_distribute()` (used by `v_lambda`'s trailing
statement, `_receiver_scope`'s apply/run trailing statement, and if/when branch trailing
statements) returned its rendered line WITHOUT the `#@@KTSRC <n>` marker that `stmt_lines()`
already applies to every other statement, so the LAST statement of any multi-statement lambda body
(the common composable-nesting shape, e.g. WinsHomeCard's "Log a win" button subtree, or
AppTopBar's two sibling Texts) had no linemap entry and fell back to identity.py's nearest-line
guess, silently crediting several distinct composable calls to one earlier, unrelated coordinate.
Fix: `_distribute()` now calls `self._kt_tag(...)` on both of its terminal return paths (the
`_stmt_shaped` case and the plain `lead+expr` case), tagging with the trailing node's own line —
same marker/strip/JSON format as everywhere else, no format change, no regression to the block-form
if/when/try paths (those already tag every branch statement via `_branch`->`render_statements`).
Verified: WinsHomeCard.py.linemap.json entries 33->49 (lines 27-31, the "Log a win" subtree, now
each map to their own kt line: 98/92/83/74/71 instead of all falling back to 97); AppNavigation.py
line 379 (second sibling Text) now kt:1012 and line 380 (Column wrapper) now kt:1006, instead of
both collapsing onto line 378's kt:1007 (row 1's exact case). Sandbox short walker.py runs
(steps=8, reset) on the SAME route sequence: pre-fix 165/283 MOUNT lines carried the "~" approximate
marker (58.3%); post-fix 0/362 in a longer-reaching run of the same walk. HOST RE-WALK PENDING: the
3767-approximate count from hostrun 164 was measured against a full walker.py budget on real device
state; a fresh full host walk (not just this sandboxed short smoke check) is needed to get the real
post-fix approximate-mount count for the record. PseudoCoup_v0 commits: "linemap density: every
composable-call line gets its own entry (...)" (transpiler fix, tools/pseudokotlin only) then
"handoff: linemap density fix, host re-walk pending" (this entry). WFL_MixingCenter's regenerated
.py/.py.linemap.json build outputs were NOT committed (left uncommitted per standing build-output
policy — re-running `build_mixingcenter.py` regenerates them identically).

# Session handoff — 2026-07-08 LATE update (COMPONENT IDENTITY SYSTEM; successor model: read this block fully)

OWNER'S STANDING SPEC (verbatim intent, non-negotiable): zero opaqueness. Every UI component and every
activator carries an identity tag; a live runtime log announces what is what (mounts, activations); every
entry cross-checks against the Oracle ledger AT RUNTIME, so a one-sided "empty" entry is impossible to
assert — the system itself names what is at each position on both engines or names the ledger entry that
failed to appear. Also: communication per the owner's saved protocol (direct answer first, keep their
words, anchor every abstraction, no jargon, ask before ontology/naming choices), delegate heavy work to
Sonnet subagents, commit small and often (high-resolution chronology; sandbox commits, owner pushes).

THE IDENTITY SYSTEM AS BUILT (all committed, WFL_MixingCenter master):
- Shared identity key: Kotlin source coordinate (File.kt:line) of the composable call that produced a
  component. Python gets it via the transpiler's linemaps (<file>.py.linemap.json, generated line -> kt
  line); Kotlin gets it via Compose's composition source information.
- render/identity.py: hooks Node construction (di.install pattern), stack-walks to the transpiled call
  site, linemap-translates to kt coordinate, stores node.origin. NOTE: found compose.py defines
  _call_site() twice (late-binding bug, node.src untrustworthy) — identity.py does its own walk.
- render/oracle_registry.py: the Oracle — 1658 composable call sites scanned from 253 transpiled files;
  {kt_coordinate: composable_name}. Walker verifies every mounted widget against it live: "ORACLE OK" /
  "ORACLE UNKNOWN origin=..." lines. PROVEN: full 50-step walk (hostrun 150) = 0 UNKNOWN.
- kivy_kit.py MOUNT/UNMOUNT + walker.py ACTIVATE lines all carry origin=<kt coord> (IDENTITY_LOG flag,
  on for walker runs, off for fidelity/interact to keep their parsed stdout clean).
- Kotlin half: WFL/app/src/test/.../walk/SourceProbe.kt wraps AppNavigation in the walk test, reads
  currentComposer.compositionData (public API reproduction of Layout Inspector's Inspectable; the
  currentComposer read must stay OUTSIDE try/catch — Compose compiler rule, cost us hostrun 149).
  WalkRecorderTest emitMountLog() dumps "MOUNT engine=kt origin=File.kt:line kind=..." per settled state
  + origin= on ACTIVATE lines, all into WFL/app/build/walks/kt_activations.log (gradle swallows test
  stdout — the file IS the nothing-hidden log). CHANNELS lines = per-node semantics action/property dump.
- render/mount_diff.py: the coordinate-join instrument. Parses both identity logs, normalizes kt bare
  filenames -> registry paths (unique-basename index; ambiguity reported never guessed), filters non-app
  frames, reports per-route and global: both / py-only / kt-only coordinates, each named with registry
  entry + log evidence. Output: render/walks/mount_diff_report.txt.

KT LINE-NUMBER DEFECT = DIAGNOSED AND PARKED (2026-07-08, WFL_MixingCenter commits through c688f54): kt
Group.location systematically misattributes app-level conditional/nested composable call groups to the
nearest ANCESTOR group that carries a source location, rather than the call's own frame — this is Compose's
own ui-tooling-data SourceInformation parser/slot-walk behavior, not a bug in this repo's traversal or in
WalkRecorderTest.kt's print format (confirmed, not guessed, via GROUPDUMP hostrun 156: a raw, unfiltered
per-group name/loc/box/children dump showed `name=Scaffold loc=AppNavigation.kt:249` while the file's only
real `Scaffold(...)` call is at line 385 — line 249 is the enclosing function body's first executable
region; library-internal frames are unaffected and resolve correctly, e.g. `Surface@Scaffold.kt:96`; test-
harness caller frames are also correct, e.g. `AppNavigation@WalkRecorderTest.kt:765`). Reimplementing
Compose's own slot-walk to fix this is out of scope — kt line-exact coordinates are PARKED as unattainable.
What both engines DO prove correctly without exception: FILE and COMPOSABLE NAME. The agreement gauge is
therefore render/mount_diff.py's TIER 2, now COUNT-BASED: for every (file, composable-name) pair, the
MULTISET COUNT of mount occurrences is compared between engines (per route where both engines have route
data, else globally), reported as AGREE / COUNT MISMATCH / py-only / kt-only, with a registry distinct-
call-site count alongside as context (not an equality target). Tier 1 line-exact join is kept in the report,
labeled, and stays the aspirational (currently ~0, by the parked defect) finer-grained measure.
STATUS UPDATE (2026-07-08, WFL_MixingCenter commit fa11c79): kt mount undercount (~1/100th of py's per
mount_diff's count tier; 138-group GROUPDUMP hostrun 156 mostly childCount=1 wrapper chains) root-caused
separately from the line-attribution defect above — SourceProbe.kt only ever read the ROOT composition's
CompositionData, and anything mounted via SubcomposeLayout (Scaffold's own internal slots, LazyColumn/
LazyRow item subcompositions, etc.) composes into its OWN CompositionData with no edge from the root's
Group tree. Fix implemented: SourceProbe now also provides androidx.compose.runtime.tooling.
LocalInspectionTables (a synchronized MutableSet<CompositionData>) around content() via
CompositionLocalProvider; verified directly against ComposerImpl.startRoot() runtime source that every
(sub)composition unconditionally registers its own compositionData into that set when non-null, the same
bridge ui-tooling's own Inspectable uses. WalkRecorderTest's emitMountLog/emitGroupDump now walk root data
plus every registered table (deduped by identity, "TABLE k/N" headers); GROUPDUMP cap raised 3000->6000.
STATUS: subcomposition capture VERIFIED on host (242 tables, T1exact 0->67); mount_diff refined (vocabulary
filter, per-route counts). GRANULARITY PARITY (commits 231bf79/153f03d): py now dumps its mount set ONCE
per settled state under a STATE header (per-creation lines behind IDENTITY_LOG_VERBOSE) -- recompose churn
had inflated py counts ~35-40x; oracle_registry is coordinate->[names] (518/1658 coordinates carry multiple
same-line composables; flat dict had silently dropped primitives). Hostruns 159 (py walk, new format) + 160
(mount_diff) run -- FIRST directly-comparable count run showed raw per-route mount counts still 0 count-agree
(py's BFS-replay walk redumps the same route many more times than kt's single-visit walk -- 137 STATE dumps
across 17 py states vs 21 dumps across 21 kt states -- so raw counts were never comparable, only the VISIT-
NORMALIZED rate is). FIX (WFL_MixingCenter commit 9e233bc): mount_diff's verdicts are now DENSITY-based --
(mounts of a pair/coordinate on route R) / (STATE dumps that engine recorded on route R), compared as an
EXACT fractions.Fraction (no float, no tolerance/epsilon). STATUS UPDATE (2026-07-08, latest run): "MOUNT
DIFF: T1: 62 matched, 19 density-agree, 16 density-differ / T2 24 density-agree, 18 density-differ, 13
not-comparable, 38 py-only, 298 kt-only pairs" -- density comparison surfaces real agreement (0->19 T1,
0->24 T2) that raw counts could never show; remaining DIFFER cases are genuine per-visit rendering variation
(e.g. LazyColumn item counts differing by visit), not noise -- see mount_diff.py's "DENSITY VERDICTS" comment.
DENSITY-DIFFER ANALYSIS (2026-07-08, render/walks/density_differ_analysis.md, WFL_MixingCenter commit
3b691d0): all 16 T1 DENSITY-DIFFER rows investigated row-by-row against raw log evidence + kt/py source --
result: 0 real twin divergence (A), 7 real per-visit variation (B, rows 7/9/10/11/12/14/15 -- entirely
traced to py's BFS-replay walk sampling 2 extra `progress` tab sub-states kt's single-path walk never
reached, plus row 10's genuine hasAnyMetric-gated conditional content), 9 instrument artifact (C, rows
1/2/3/4/5/6/8/13/16 -- two flavors: kt-side Compose runtime frames [`<get-colorScheme>`,
`rememberComposableLambda`] sharing an "enclosing group location" with the real call, and py-side
identity.py's nearest-line fallback silently miscrediting multiple distinct composables sharing one
collapsed/unmapped python line onto one kt coordinate). ARTIFACT FIXES COMMITTED (WFL_MixingCenter commits
19143bc/893650b): (1) identity.py's resolve_kt_coord() now marks every fallback-resolved coordinate with a
trailing "~" (e.g. "AppNavigation.kt:414~") so approximate attributions are visibly distinguished from exact
linemap hits, never silently conflated -- verified live via a sandbox boot dump showing both forms on real
MOUNT lines. (2) mount_diff.py: approximate ("~") coordinates now participate in T2 (file+name) but are
excluded from T1 (line-exact) density material entirely, with their own "py approximate-coordinate mounts: N"
context count; T1 density is now keyed by (coordinate, kind) instead of coordinate alone, so linemap-collapse
rows compare each kind's own rate independently instead of summing unrelated composables together (same-line,
same-kind siblings remain mutually indistinguishable -- an inherent limit of the coordinate format, not
claimed to be solved); kt-side true-infrastructure kinds (remember, rememberComposableLambda,
collectAsStateWithLifecycle, `<get-...>`) are now excluded from coord_route_counts regardless of vocabulary
status, fixing the row-2/row-8 runtime-frame-doubles-the-real-call's-count defect. Re-run against current
logs: T1 DENSITY-DIFFER dropped from 16 to 9 (coord,kind) keys, all of them B-classified rows plus residual
same-kind-sibling ambiguity (e.g. AppNavigation.kt:1007's two Text calls) -- exactly as the analysis
predicted. CAVEAT: this re-run used the PRE-FIX py_activations.log (walker.py has not been re-run since the
identity.py fix), so it carries no "~" markers yet (0 approximate mounts reported) and the row-1/13-style
same-kind-sibling miscredits are still baked into that log's raw MOUNT lines; full effect of the marking fix
(further T1 differ reduction, nonzero approximate-mount context count) needs a FRESH host walker.py run,
which is PENDING (not performed in this session, sandboxed boot-only verification was substituted per task
scope).

WALK DIFF STATE (hostrun 153): mutual territory 4 shared / 4 kt-only / 10 py-only / 69 edge mismatches;
COVERAGE GAP kt-only routes [execution, exercise_detail, exercises, gym_list, settings_notifications,
wins, cooldown, summary] (13 states), py-only [programs, settings] (3). Owner-approved policy: coverage
gaps are never counted as mismatches. Dismiss parity done (kt recorder ranks Dismiss above OnClick; differ
aligns onDismissRequest on handler alone — labels structurally can't match). Numeric text canonicalized
('42'=='42.0'). Ledger-join reporting: every one-sided state resolves to nearest counterpart with overlap
ratio + RESOLVED PAIRs; UNRESOLVED is loud. Max overlap 0.83 -> remaining unshared states differ by real
content, mostly reachability.

NEXT STEPS QUEUE (after the kt location fix): (a) frontier/BFS alignment so both walkers spend budgets on
the same territory (owner approved scoped-diff-first, then alignment); (b) named seed roots for
unreachable screens (Onboarding, ReportBug-crash, WorkoutWarmup) — same seed both engines; (c) make
mount_diff a tracked gate once kt locations are line-exact; (d) owner decision pending: ~61 pre-existing
uncommitted WFL files (mostly regenerated py twins from the T3 transpiler fix — build output awaiting
gate acceptance) — commit or hold; (e) PseudoDart phase per original HANDOFF (discipline-checker gauge
first — note the identity/type discussion: transpiler preserves type ANNOTATIONS/wrappers (Int32/Float32
on values) but variables are unenforced names; owner is aware and parked local-variable annotations until
it bites).

OPERATIONAL (successor model, learn from this session's scars): hostrun loop = write request JSON to
DevComms/hostruns/requests/NNN_name.json {"id","cwd","cmd","timeout"}, owner runs tools/walk_service.py,
read results/NNN.log+.json. A request with NO result file gets re-run on service restart — never leave a
--reset walk request dangling (it wiped 99 steps of progress once; delete/park request files after
failures). Sandbox bash: 45s hard cap per call, background processes are reaped, host paths differ from
Read/Edit paths (see Shell access mapping). Git in mounted repos: stale .lock files appear when a call is
killed mid-git — rm -f .git/*.lock and retry; NEVER bypass with write-tree/commit-tree (an agent's manual
ref writes desynced the index and silently reverted 11 files in a later commit — always `git status` +
`git diff HEAD --stat` after agent commits). Kivy runs in-sandbox (pip install kivy --break-system-packages,
xvfb-run -a, apt libmtdev1); loader needs ~/Programming symlinks (ln -s /sessions/<s>/mnt/X ~/Programming/X).
Repo renamed PseudoCoup->PseudoCoup_v0 2026-07-08; if GitHub repo renamed too: git remote set-url.

# Session handoff — 2026-07-08 update (discipline slice + walker hermeticity; details in PROGRESS_ondeck.md)

REPO RENAMED: PseudoCoup -> PseudoCoup_v0 (user freed the name for a new public repo). All hardcoded
~/Programming/PseudoCoup path constants updated (render/ tooling, vendor scripts, walk_service usage
line). If the GitHub repo is also renamed: `git remote set-url origin .../PseudoCoup_v0.git`.

MAIN-SOURCE DISCIPLINE SLICE (DevComms/main_source_discipline.md; user-approved Tiers 1+2+3, all
landed + verified): T1a merged semantics on 26 container clickables (walker labels carry child text
natively); T1b AppTopBar day-name + TodayScreen week read TimeProvider (closes the AppNavigation.kt:994
open decision); T2 explicit locales (String.format weight, wins formatter/sort); T3 transpiler emits
raise (not None) for the synthetic exhaustive-when else, gated to value-consumed whens only. Runtime
grew Locale.US/ENGLISH as a real class + ktformat skips a leading Locale arg. Gates after: kotlin
green, fidelity 423/423, interact 1410/1410 + shell 6.

WALKER HERMETICITY (the big correction): di._DB was process-global while Session.build re-ran
load_ns() per episode -> later episodes read rows hydrated through the PREVIOUS namespace's enum
classes (identity mismatch -> synthetic when-else None). The "first real app bugs" note is REVISED:
Resume/WorkoutExecutionViewModel float*NoneType and the phantom "Workout in progress" states were
walker leakage, NOT app bugs (ModalBottomSheet dismiss LookupError remains open/real). Fix:
di.reset() per Session boot, closes old sqlite conn (a 100-episode walk otherwise OOMs — hostrun 119
died SIGKILL at 99/100). Crash tracebacks now print to walk logs (di.py + walker.py, log-only).
Second clock gap found+fixed: WalkRecorderTest bypasses Hilt, so FixedTimeModule never reached
Assembler-built ViewModels — Assembler gained an optional TimeProvider override (default unchanged).

WALK DIFF (hostrun 142, both walks clock-pinned, hermetic): 4 shared / 17 kt-only / 19 py-only /
122 edge mismatches (was 4/17/29/170). Bucket teardown (agent, 2026-07-08): unmapped overlay/container
kinds (py records DropdownMenu/ModalBottomSheet/Card; kt semantics tree has no such kinds) = 17/36
unshared states + 72/122 edge mismatches — DOMINANT remaining lever, currently deliberate KIND_MAP
policy, needs a user design decision; BFS reachability = 13 states + 21 edges; "42" vs "42.0" display
drift = downstream formatting, differ-canonicalization decision pending; kt 'Button' vs py
'FloatingActionButton' labels = 14 edges.

# Session handoff — 2026-07-07 update (walker era; read PROGRESS_ondeck.md top entries for full detail)

CURRENT STATE: acceptance-drive bugs fixed (Room invalidation, live flow operators, fail-loud DI, M3
Defaults colors, density scaling via WFL_SCALE). The DECISION-TREE WALKER is live: render/walker.py
(Python side, real taps), WalkRecorderTest.kt (Kotlin side, Robolectric + Hilt, FixedTimeModule clock
pin), render/walk_diff.py (differ, format v2 = meaning-bearing nodes only, KIND collapse table).
It already found+we fixed: Modifier.clickable never promoted to handlers (whole class touch-dead),
touch z-order (bars must outrank content; Kivy Window is its own parent — cycle guard load-bearing).
GATES (all green, re-baselined): fidelity 423/423 (28 screens), interact 1410/1410 + shell 6,
realtap GREEN (5 case groups), kotlin tests 160/160, datalayer ALL GREEN.
WALK DIFF: 4 shared / 17 kt-only / 3 py-only / 37 edge mismatches — next work: kt empty edge labels
(unmerged semantics), deeper py coverage, extra seeded walk roots (Onboarding etc.), emulator walk
(dry-built, unexecuted: render/emu_walker.py + CommandReceiver.kt ported, debug-only manifest).
HOST LOOP: user runs `python3 tools/walk_service.py` on their machine; I write request JSONs to
DevComms/hostruns/requests/, read results/ — this is how ALL gradle/xvfb verification runs. The
Cowork sandbox caps every bash call at 45s; staging copy at /tmp/gh/Programming (beware rsyncing
the repos' self-symlinks into it — they hang recursive globs and parent walks).

# Original handoff — 2026-07-05 (for continuation in Claude Desktop Cowork)

You are continuing an ongoing engineering loop with Lucas. Read this file, then `PROGRESS_ondeck.md`
(top = newest state), then the memory files (they load automatically and carry the standing rules).
Work rounds end with: report → dashboard update (`PROGRESS_ondeck.md` edit + `python3
tools/pseudokotlin/track.py`) → commit-push of BOTH repos (PseudoCoup on main, WFL_MixingCenter on
master). Reports from delegated agents live in `DevComms/*.md` — that directory is the project's
paper trail; read the recent ones before assuming anything.

## Where the project stands: KtToPy is DONE pending user acceptance

The WFL Kotlin app (`~/Programming/WFL_MixingCenter/WFL/`) runs fully in Python/Kivy via the
KtToPy transpiler (`tools/pseudokotlin/`). Every measured gate is green:

| Gate | Command | Expected |
|---|---|---|
| Geometry (dump path vs real Compose) | `cd tools/pseudokotlin && python3 fidelity.py` | `377/377 (28 screens)` |
| Interaction + shell sweep | `cd ~/Programming/WFL_MixingCenter/render && python3 interact.py` | `513/513 across 27 screens + shell(5 handlers)` |
| Real synthetic touches (nav bar) | `cd ~/Programming/WFL_MixingCenter/render && xvfb-run -a python3 realtap_gate.py` | `GATE: GREEN` |
| Kotlin unit tests in Python | `cd tools/pseudokotlin && python3 run_kotlin_tests.py` | `160/160 pass` |
| Domain corpus | `cd tools/pseudokotlin && python3 oracle.py --all` | 11/12 green (12th = LayoutDumpTest, ERR by design — needs real Compose) |
| DAO invariants | `cd tools/pseudokotlin && python3 datalayer_oracle.py` | ALL GREEN (9 invariants) |

The runnable app: `cd ~/Programming/WFL_MixingCenter/render && python3 run_app.py` — no arg boots
the WHOLE app (AppNavigation shell: bottom nav bar + NavHost, phone display 412x915 portrait,
seeded completed user, boots to Today; nav taps work with real touches). `run_app.py <ScreenName>`
runs one screen in isolation (names in `render/layout_screens.txt`). Fonts (Material icons +
NotoColorEmoji) are vendored in `render/assets/` — no OS package dependencies.

**The only open item: Lucas's acceptance drive.** He taps around the real app; anything that feels
un-Kotlin becomes the punch list. Minor known non-defects: ProgramEditor "Deload" label slightly
overlaps (within tolerance, legible); default launch has no enrolled program (Today shows the
empty state — could seed an enrolled program if he wants a richer demo).

## Next phase (after acceptance): Python → PseudoDart

Converting the Python output into "Python disciplined in Dart" (restrict to constructs that map
1:1 to Dart) so later conversions happen in an easy-to-run environment. Agreed shape, in order:
1. **Discipline-checker gauge first** (the measured instrument defining the discipline — analogous
   to fidelity.py; a number that can't be gamed). ~1 slice.
2. **Typed emission from Kotlin** — the transpiler sees Kotlin's types; emit them rather than
   reconstructing. ~1–2 slices.
3. **Static runtime twin** — the runtime's dynamism (autostub, loader __missing__, monkeypatching)
   is exactly what Dart forbids; replace with explicit typed modules. Hard part, ~2–4 slices.
4. UI can likely reuse the existing PseudoFlutter kit (WFL conversion prior art, 65/65 goldens).
Estimated 6–12 work rounds total. Key lesson to carry (memory: launcher-vs-instrument-path): every
gauge certifies only the path it measures — PseudoDart's checker must run against the same artifact
that executes.

## Standing law (also in memory files — they are binding)

- Zero hand-edits to transpiled WFL-Python; regenerate via `python3 tools/pseudokotlin/build_mixingcenter.py`.
- One cause = one general fix in a shared layer (kivy_kit / runtime / loader / differ / transpiler).
  A real fix moves a GROUP of failures. No per-screen/per-name patches.
- Never game a meter: no error-swallowing, threshold-tuning, or assert-free "passes".
- Kotlin in WFL_MixingCenter/WFL may be adjusted only if appearance/function is unchanged.
- Font/shaper bridges are the ONE sanctioned non-general area; every metric specimen-derived
  (dumpSpecimen/dumpSpecimenList), never inferred from mixed app screens.
- Instruments certify only what they measure: the fidelity gauge covers the DUMP path; the
  runnable app (run_app.py) is a separate wiring surface — eyeball it before trusting it.

## Delegation policy (memory: delegate-to-opus-tight-briefs)

Split work into small fenced sub-tasks for subagents; the orchestrator reviews, runs final gates,
and commits. **Sonnet by default** for scoped implementation with verifiable gates; **Opus only for
open-ended diagnosis**. Every brief carries: (1) the law verbatim, (2) an explicit file fence,
(3) exact verification gates with expected outputs, (4) a stop-rule ("cause out of fence → report,
don't fix"), (5) a DevComms report, and (6) "do the work in your own turn — your final reply is
the deliverable" (Sonnet once backgrounded its task and quit). Sequence agents sharing a file;
parallelize only disjoint fences. Hold commits while any agent is editing shared files.

## Command crib

- Full geometry gauge: `cd tools/pseudokotlin && python3 fidelity.py`
- Regenerate WFL-Python after transpiler/runtime edits: `python3 tools/pseudokotlin/build_mixingcenter.py`
- Regenerate auto layout tests after generator edits: `python3 tools/pseudokotlin/gen_layout_dumps.py`
- One screen's kivy dump: `cd ~/Programming/WFL_MixingCenter/render && python3 inspect_layout.py <ScreenName>`
- One screen's compose dump: `cd ~/Programming/WFL_MixingCenter/WFL && ./gradlew -p app testDebugUnitTest --tests '*LayoutDump*.dump<ScreenName>' --rerun` (use `--rerun` — gradle silently skips up-to-date tests)
- Screenshot a run: `SHOT=out.png xvfb-run -a python3 run_app.py [Screen]` (file gets a frame suffix: out0001.png)
- Dashboard: edit PROGRESS_ondeck.md, then `python3 tools/pseudokotlin/track.py` (never hand-edit PROGRESS.md/html)
- Headless probes of the full app MUST settle first (repeated `comp.compose()` until node count
  stabilizes) — the first compose renders a loading-spinner branch; reading too early gives a
  15-node tree and false "broken" conclusions (this burned us once).
