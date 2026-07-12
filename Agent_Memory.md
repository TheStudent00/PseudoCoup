# Agent_Memory.md — persistent agent memory (survives context drift/collapse)

Read this alongside HANDOFF.md. HANDOFF = project state for a cold reader. THIS file = the agent's
standing duties, habits, owner mandates, and scars. Update it whenever a duty, mandate, or lesson
is added — an entry here is cheaper than re-learning the lesson.

## Standing duties (every session, no reminder needed)

- COMMIT MESSAGES: the owner pushes via ~/Programming/PseudoCoup_v0/WFL_and_PseudoCoup_v0_git_push.sh,
  which reads DevComms/next_commit_message.txt (file consumed after use; arg overrides; fallback
  "update"). After any meaningful change, WRITE the commit message there. If the file still holds an
  unconsumed message, APPEND below it (blank line between) — never overwrite an unpushed message
  (owner assigned this duty 2026-07-10).
- HANDOFF.md: keep the top document current; demote superseded blocks to the HISTORY section.
- BUG_PROFILE.md: the living catalog of kt↔py divergences. Update it whenever a bug is found, fixed,
  disproven, or reclassified — the point is to spot CLUSTERS (several symptoms, one cause).
- This file: add scars/mandates/duties as they happen, prune stale ones.
- Task list (TaskCreate/TaskUpdate) for any multi-step work; verification step included.

## Owner mandates (non-negotiable, with enforcement where built)

- PROGRESS COUNTER (2026-07-10): a percentage is shown ONLY as the walk's own "PROGRESS spent=A/B"
  counter over its own --steps/-Dwalk.steps budget. py counter = walker.py stdout; kt counter =
  kt_activations.log (gradle swallows test stdout). No counter -> no percentage, ever. Enforced:
  green budgeted walk with zero counter lines = "progress_defect" in result json + banner;
  tools/test_walk_service_progress.py fails if the enforcement or plumbing is removed. Run that
  test before touching walk_service.py. Emitter lives in WalkRecorderTest.kt's walkApp loop.
  WHY this is written down: the owner had to re-demand a working progress indicator repeatedly;
  it kept eroding because nothing failed when the counter vanished.
- EVERYTHING IS TRACKED: no UI component exists/gets touched/disappears at runtime without being
  named in the live log and cross-checked against the ledger. Loud on failure (ORACLE UNKNOWN).
- Never game a meter: no error-swallowing, threshold-tuning, assert-free passes.
- One cause = one general fix in a shared layer. No per-screen patches.
- Zero hand-edits to transpiled WFL-Python; regenerate via tools/pseudokotlin/build_mixingcenter.py
  (requires python tree_sitter INSTALLED or every enum column silently degrades to text).
- Retraction discipline: when an earlier in-session claim turns out wrong, say so explicitly and
  mark it WITHDRAWN in the record; never quietly revise.
- Accounting: every request file / artifact has a named author. requests/202_py_walk_exhaust.json
  (origin never resolved, owner cancelled it, tombstone result written) is the standing example of
  the failure mode. Subagent briefs carry a no-silent-actions rule.

## Communication protocol (owner's saved preferences are binding — highlights)

- Direct answer first. If asked "X or Y?", answer X or Y.
- Keep the owner's words; don't swap synonyms. New term -> glossary entry with a CONTEXTUAL example.
- Anchor every abstraction (what maps to what, what sits between what). No unexplained jargon.
- Structural overviews in the exact class/attributes/methods format from the saved protocol.
- Architecture/ontology/naming decisions are the OWNER'S. Proposals are labeled proposals.
- Don't anticipate objections not raised; don't pad answers with unrequested alternatives.

## Glossary (owner-anchored; check before reusing a term)

Ledger id
    the unique positional-path id idgen.py computes for every Kotlin source node by parsing.
    Never injected; exists for ALL nodes; ledger_unified.py is the record keyed by it.
walkTag (insertion)
    inject_emitid.py writing `.walkTag("<ledger id>")` into Kotlin source so that SAME id is
    visible at runtime. Same id space; a replay-stable handle, NOT the tracking itself.
    DO NOT collapse these two — the confusion cost owner trust once already.
State (walk graph)
    one settled screen configuration; state_id hashed from route + settled tree summary.
    example: run 206's kt walk found 63 of them.
Edge (walk graph)
    one FIRED action recorded as (source state, action, destination state): the walker resolved a
    node, fired its handler, captured the settled result. An edge with an error field (e.g.
    AssertionError) recorded a fire that threw instead of landing on a destination state.
    example: run 206 = 200 edges because a 200-step budget fires (up to) one action per step;
    206 had 194 clean edges + 6 error edges.
BFS walker (render/walker.py, WalkRecorderTest.kt)
    breadth-first explorer: reboots the whole app fresh per edge (hermetic), so app-state never
    accumulates. Maps the blank seeded app only; slow (~14s/step on py). For BREADTH coverage.
Directed scenario runner (render/scenario.py, ScenarioTest.kt)
    stateful, scripted: ONE session, an ordered list of semantic taps (by visible text), screenshot
    per step. State accumulates across steps, so it reaches rich states the BFS walker cannot.
    example: it drove enroll-a-program and Home then showed the weekly schedule; 18 steps in ~17s.
    Output side-by-side: render/atlas/scenario_side_by_side.html (kt|py per step).

## Operational scars (each one cost a session or worse)

- Hostrun loop: request JSON -> DevComms/hostruns/requests/NNN_name.json {"id","cwd","cmd","timeout"};
  id must equal filename; cmd[0] in {gradlew, python3, xvfb-run, adb, git}; results in results/.
  A request with NO result file re-runs on service restart — never leave a --reset walk dangling
  (once wiped 99 steps of progress). Dead request that can't be deleted from sandbox: write a
  tombstone result json explaining why (the 202 pattern).
- Request ids: check for collisions before numbering (202 was used twice).
- Capture artifacts INTO results/ via a follow-up request — gradle swallows test stdout; build
  dirs are not results (run-176 lesson).
- Sandbox: bash 45s hard cap; mounts CREATE but can't DELETE; host paths differ from file-tool
  paths; stale .git/index.lock -> owner's push script clears it; NEVER bypass git with plumbing
  (write-tree/commit-tree once silently reverted 11 files).
- walk_service must be RESTARTED to pick up edits to walk_service.py (it's a running process on
  the owner's machine).
- kt_activations.log persists across runs; anything tailing it must skip stale content
  (walk_service._StepCounter does: offset starts at file size, resets on truncation).
- Headless full-app probes must settle first (repeated comp.compose() until node count stabilizes)
  — first compose renders a loading spinner; reading early gives a false-broken 15-node tree.
- Don't count proxy lines as progress (v1 bar counted "STEP " lines; crash tracebacks inflated it).
  Only the walk's own counter is trusted.

## Current arc (2026-07-12 — see HANDOFF top block + BUG_PROFILE.md for full detail)

- B14 FIXED (3 stacked runtime bugs: NavHost stub backStackEntry -> "<stub getString>" session id;
  Database.execute mid-txn commit whose failed ROLLBACK masked everything; missing named operator
  methods .div etc. on Int32/Int64/Float32). B08 no longer reproduces (same nav root). The owner's
  faithful journey runs END-TO-END on py, both 9a and 9b tails. kt mirror queued as run 246/247.
- NEW INSTRUMENT: kivy_kit.LAST_FIRE_ERROR + FIRE-ERROR lines (handler exceptions were silently
  swallowed by _fire — B17). scenario.py records fire_error per step. Walker adoption pending.
- Scenario variants: scenario.py argv[1] = faithful_early_finish / faithful_complete / v1_pathfirst;
  ScenarioTest.kt = three @Test methods. WALK_SEED=fresh (py) mirrors -Dwalk.seed=fresh (kt).
- Prior py bundles (238/240/242) predate the runtime fixes — next py capture walk re-baselines.

## Previous arc (2026-07-11/12 — statuses partly superseded above)

- PRIMARY INSTRUMENT CHANGED: aimless BFS walking is superseded for debugging by the DIRECTED SCENARIO
  RUNNER (render/scenario.py py + ScenarioTest.kt kt). It is STATEFUL (one session, state accumulates:
  select path -> enroll program -> Home shows the schedule -> start workout) and FAST (~17s vs ~93 min).
  The BFS walker reboots the whole app per edge, so it CAN'T build app-state (only maps the blank seeded
  app) and is slow. Use the scenario runner for directed/first-few-taps work; BFS for breadth only.
- BUG_PROFILE.md is now a standing living artifact — keep it current (see duty below).
- Bugs FIXED (verified): B07 (SharedFlow emit never notified collectors; coroutines.py; 8 VMs),
  B12 (py walker read concrete route not pattern; walker.py _route_pattern), py teardown hang (os._exit),
  B11 loud-stub instrument built (finding: full-app runtime has ZERO degradations). DISPROVEN: B01 (seeds
  identical), B03 (RPE global = correct).
- Bugs OPEN, in priority order: B14 (WorkoutExecution "Session not found" read-before-write race — the
  ROOT of the whole workout-flow cluster, fix NEXT), B09 (Programs: py shows all samples, kt filters by
  active-path -> empty; py filter unapplied), B08 (settings->exercises dead nav), B15 (path/program dual
  enrollment), B16 (import walker disables OVERLAYS_ENABLED).
- Owner's directed journey (run it FAITHFULLY next — my first run distorted it): fresh-seed onboarding
  (skip questions) -> select path -> select program (NATURAL flow, NOT the buggy Browse-Programs screen)
  -> Home -> start workout -> increment weight -> log sets -> log-set-and-next -> 9a finish early -> 9b
  continue to completion.
- Infra: kt bundle = run 236 (180 states); py bundle = run 242 (51 states). nav_graph.py + log_148:
  microVM NOT forced for any screen. Progress mandate fully implemented + guard test.

## New scars this session (2026-07-11/12)

- DON'T call a walk HUNG on a short freshness check. Checked the log's mtime over ~7s and declared runs
  238/240/242 "hung"; 242 was just SLOW and completed 400 steps in ~93 min (~14s/step, per-edge App
  reboot). Prematurely tombstoned + hand-grabbed partial data. A step can take minutes — wait for the
  result json, or check `steps.spent` isn't advancing over MINUTES, not seconds, before calling it hung.
  (238's teardown hang WAS real and is fixed; the mid-walk "hangs" were slowness.)
- FORWARDING ALLOWLIST is hardcoded in build.gradle.kts testOptions.unitTests.all — a new -Dwalk.X flag
  is INVISIBLE to the test JVM until added there (bit walk.steps once, walk.capture again this session).
- Flag values must be `=true`, NOT `=1` — Kotlin String.toBoolean() only accepts "true"/"TRUE".
- Test-JVM heap: `-Dorg.gradle.jvmargs=-Xmx2g` sizes the GRADLE DAEMON, not the forked test JVM. Set
  `test.maxHeapSize` in build.gradle.kts testOptions (default heap OOM'd a long walk mid-run).
- kt taps: a bare performClick taps the node's ON-SCREEN COORDINATES — a scrolled-off node gets a
  dead tap. Use performSemanticsAction(SemanticsActions.OnClick) (or performScrollTo first). This cost
  the whole PixelProbeTest overlay saga.
- Compose one-shot events: LaunchedEffect{ sharedFlow.collect{} } needs MutableSharedFlow.emit to NOTIFY
  live listeners (not just buffer). Distinct from StateFlow (which the UI reads by value). This class of
  event-driven navigation was ALL dead on py until B07's fix.
- `import walker` has an import-time side effect (via interact.py) that disables OVERLAYS_ENABLED — any
  tool importing walker inherits dead overlay taps (B16).

## New scars (2026-07-12)

- Kivy's Window import REWRITES sys.argv — read CLI args from a copy saved BEFORE any Kivy-importing
  import (scenario.py._ORIG_ARGV; walker.py already knew). A missed read silently runs defaults.
- `import scenario` sets WALK_SEED=fresh at import time (its default variant) — a probe wanting the
  completed-user seed must pop the env var AFTER that import, not before.
- Handler exceptions must be READ from kivy_kit.LAST_FIRE_ERROR after tap-driving — _fire cannot
  re-raise into Kivy's touch dispatch, so silence there is structural; the flag is the loud channel.
- In-sandbox kivy needs python3.13 explicitly (`xvfb-run -a python3.13 ...`); plain python3 lacks kivy.
- The runtime's kt-parity gap class "named operator methods" (`a?.div(b)` → .div() CALL): check the
  wrapper types in numbers.py/kotlin_rt.py before assuming an operator exists.
