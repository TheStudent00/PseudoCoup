# log_55 — KICKOFF for a fresh Gemini conversation (this is the ONE doc to hand over)

Date: 2026-06-26
Type: self-contained kickoff. You are continuing a Kotlin(Compose)→Python(`WFL_PseudoCoup`) port.
Everything you need to start is here; log_53 (full protocol) and log_49 (full work-list) are the
deeper references.

## What you are doing (and NOT doing)

The non-UI layer is **already built** — 9 engines, 27 entities, repositories, 39 domain services, the
27 ViewModels (~37k LOC of synchronous Python). **Do not re-port domain or ViewModel logic.** Your job
is to **close per-screen UI gaps**: each PseudoCoup screen (`src/ui/*_screen.py`) implements a subset
of its Kotlin blueprint; you add the missing widgets and wire them to the EXISTING ViewModels/services,
**reusing** `src/ui/widgets.py` (73 components) + `src/kit.py` primitives.

## Current state (clean — verified)

- Repo: `~/Programming/WFL_PseudoCoup`, branch `kit-migration-primitives`. Gate is GREEN.
- Connectivity baseline: **211/578 (37%)**, just verified clean (0 regressions). It is the committed
  source of truth at `tools/dualgraph/connectivity_baseline.json`.
- Prior cleanup is DONE — there is no punch-list to redo. Start at the screen loop below.

## NON-NEGOTIABLE rules (a fresh read — these are enforced, not aspirational)

1. **You NEVER run `connectivity_gate.py --snapshot`, and you NEVER edit the baseline.** It is owned
   by the reviewer (the snapshot is now locked behind a token you do not have). You propose changes;
   the reviewer ratchets the baseline after verifying.
2. **Any screen's `matched` count dropping = STOP.** That is a dropped connection. Fix or revert before
   doing anything else. Never present a change where matched fell on any screen.
3. **Any `matched` increase must come with the actual KT↔PC pairs** (`align._desc(node)`) proving they
   are the same element, not spurious. Counts alone are rejected.
4. **This is an ongoing process — there is no "done" to declare, no success assessment to write.** You
   report the honest current state every step, including losses and unknowns. "The number went up" is
   not success.
5. **Everything you do is independently re-run and pair-inspected** (by a reviewer and a second
   independent agent). Honest failure costs nothing. Masking a regression, claiming a fix that doesn't
   survive re-run, or reporting inflated numbers ends the collaboration.
6. **Hygiene:** no stray/scratch files; one coherent commit per change; never leave work uncommitted.

## The per-change loop (every change, exactly this)

```
# 1. pick ONE screen; list its real gaps:
python3 tools/dualgraph/connectivity_gate.py <slug>        # e.g. exercise_create_screen
# 2. close the REAL gaps in src/ui/<slug>.py by REUSING widgets.py + kit, wired to src/viewmodel/<...>
# 3. verify connectivity maintained + improved:
python3 tools/dualgraph/connectivity_gate.py              # MUST exit 0; report the FULL per-screen delta
python3 tools/smoke_screens.py                            # 30/30 construct
$HOME/Programming/flutter/bin/flutter test app_flutter    # goldens
# 4. commit cleanly. Hand the change + the KT<->PC pair evidence to review. DO NOT snapshot.
```
Any matched drop on ANY screen in step 3 → STOP and fix. The reviewer ratchets the baseline if clean.

## Your first task (a fast win to prove the loop)

Start with a low-gap screen, in this order: **`exercise_create_screen` (1 gap)**, then
`exercise_detail_screen` (2), `workout_cooldown_screen` (2). Run the loop above on it, close the
gap(s) by reusing existing widgets, and hand it to review with pair evidence. Once the loop is proven,
work up the list (the bulk is `onboarding` 68, `workout_execution` 37, `calibrate` 30 — later).

## Caveats already known (don't rediscover or paper over)

- `program_day_editor_screen` is matcher-blind (`matched=0`) — a tool limitation, not your fault and
  not yours to "fix" by forcing matches. Leave it; it's a separate careful task.
- Structural match ≠ behavior. Wiring a `button 'Delete'` node means wiring its REAL handler to the
  REAL service — not a stub that just makes the node appear. The gate can't see behavior; that's on you.

Full detail: log_53 (protocol), log_49 (work-list), log_54 (how this clean base was produced),
log_46 (why the domain is already built).
