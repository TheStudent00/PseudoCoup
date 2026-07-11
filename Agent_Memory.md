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

## Current arc (2026-07-10, end of session state — see HANDOFF top block for full detail)

- Run 206 = FIRST honest kt graph: 200/200 steps spent (forwarding fix verified), 63 states /
  200 edges, all 219 REPLAY-MOUNT route=today, 347 exact-walkid / 199 exact / 1 missing-walkid,
  6 error edges (5 AssertionError, 1 ReplayError — unexamined). Walk stopped on BUDGET, not
  frontier exhaustion: more kt territory exists.
- Progress mandate implemented this session (service + kt emitter + guard test); kt emitter's
  compile check = next kt run.
- Next per plan: 204 pixel-probe PNGs -> frozen kt bundle -> py bundle -> atlas. En route:
  settings->exercises py divergence (kt navigates, py silently doesn't); Phase 6 id cross-check;
  cleanup pile (legacy WalkEmit.emitId in TodayScreen.kt; today FAB untagged; injector nav-gate;
  tree_sitter assert in build_mixingcenter.py).
