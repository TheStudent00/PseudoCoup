# log_53 — TASK + PROTOCOL for a FRESH Gemini conversation: siloed, ongoing, zero sleight-of-hand

Date: 2026-06-26
Type: task + operating protocol. Self-contained for a new Gemini conversation (no prior context
assumed). Written after the previous conversation re-snapshotted the connectivity baseline to hide 4
screens that LOST matched nodes (log_52). The protocol below exists so that cannot recur.

## Operating protocol — read first, applies to EVERY change

### 1. Silos + one central mix point
- **Your silo (implementer):** you edit implementation files only — matcher code under
  `tools/dualgraph/*.py` (NOT the baseline), screens in `src/ui/`, ViewModels, services.
- **Central / protected (the single source of truth):** `tools/dualgraph/connectivity_baseline.json`.
  **You never edit it. You never run `connectivity_gate.py --snapshot`.** It is the agreed record of
  current connectivity. Only the review/mix point ratchets it, and only after a change is
  independently verified clean.
- **The mix point (review):** your change + your evidence go to review. The reviewer re-runs the gate
  against the untouched baseline, pair-inspects, and ratchets only if clean. You do not own the
  goalposts, so you cannot move them — that is the whole point.

Why: the prior conversation re-snapshotted the baseline and thereby masked 4 matched-losses. With the
baseline owned centrally, a dropped connection surfaces the instant the reviewer runs the gate.

### 2. This is an ongoing process, not a finish line
There is no "done" to declare and no success assessment to write. Each change is one step of a
continuous loop; you report the honest current state — including losses, regressions, and unknowns —
every time. "It compiles" / "the number went up" is not success.

### 3. Total scrutiny — and the one fireable offense
Every change is independently re-run, diffed per-screen against the baseline, and pair-inspected — by
the reviewer and, at times, by a second independent agent. Assume everything is checked, line by line.
The one unforgivable act is **sleight of hand**: masking a regression (snapshotting over a
matched-loss), claiming a fix that doesn't survive independent re-run, or reporting inflated or
cherry-picked numbers. That ends the collaboration. **Honest failure costs nothing; hidden failure is
terminal.** When in doubt, report the ugly number.

### 4. Hygiene
No stray/scratch files in the tree. One coherent commit per change. Never leave a stopping point
uncommitted. Never overwrite a shared artifact.

## The per-change loop (mandatory, every time)
1. Make ONE focused change.
2. Run `python3 tools/dualgraph/connectivity_gate.py` (it reads the baseline you must not touch).
3. Report the **full** per-screen delta vs baseline — every screen where `matched` fell OR `kt_only`
   rose, not only the ones you meant to move.
4. **Any `matched` decrease on ANY screen → STOP.** That is a dropped connection. Diagnose; fix or
   revert. Do not proceed, do not present it as done.
5. **Any `matched` increase → attach the actual KT↔PC pairs** (`align._desc(node)`) proving they are
   genuine same-element matches, not spurious (e.g. a button paired to an unrelated row). Counts
   without pairs are rejected.
6. Hand the change + evidence to the mix point. The reviewer ratchets the baseline if clean.

## IMMEDIATE punch-list — finish Task 0 correctly (it is currently half-done and dirty)

Current state: matcher change uncommitted; it contains a REAL expansion fix (keep it) and the safe
`text_match` rule (keep it), but it bled across 28/30 screens, **regressed 4** (`onboarding 8→5`,
`exercise_create 13→12`, `paths 5→4`, `session_detail 6→5`), has ≥1 spurious pair
(`workout_execution`: button 'Log Set & Next' ↔ `in_progress_set_row`), overwrote the baseline, and
left stray files (`patch.py`, `test.py`, `tools/dualgraph/test.py`).

1. **Restore the original committed baseline:** `git checkout tools/dualgraph/connectivity_baseline.json`.
   Do not trust the overwritten one.
2. **Keep** the safe `text_match` and the `_inline_ok` expansion fix — those are good.
3. **Resolve the 4 matched-regressions:** for each screen, find the real lost match and restore it, OR
   prove with pairs it was a correct re-pairing. `matched` must not fall on any screen vs the restored
   baseline.
4. **Pair-inspect the high-delta screens** (`update_program` +8, `workout_execution`,
   `program_day_editor`) and remove spurious pairs.
5. **Remove the stray files.**
6. **Commit cleanly.** Report per-screen deltas + pair evidence. **Do NOT snapshot — hand to review.**

## Then: the ongoing screen-completion loop (per log_49), under this protocol

Same loop, applied to closing each screen's real `kt_only` gaps by **reusing** `src/ui/widgets.py`
(73 components) + `src/kit.py` + the **already-built** ViewModels/services (the domain AND the 27 VMs
exist — log_46; do **not** "re-port ViewModel logic"). One screen per change; gate every change; never
snapshot; hand each to review with pair evidence.

## Note on enforcement (reviewer side)
The reviewer will add a structural lock so `--snapshot` refuses without a reviewer-held token — making
the silo mechanical, not honor-system. Until then it is protocol: you do not snapshot, full stop.

Pointers: `tools/dualgraph/connectivity_gate.py`, `tools/dualgraph/align.py`, `src/ui/widgets.py`,
log_46 (domain+VMs already built), log_49 (screen work-list), log_52 (what went wrong).
