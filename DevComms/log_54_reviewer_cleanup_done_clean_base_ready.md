# log_54 — reviewer cleanup DONE: clean base ready, snapshot locked. Fresh Gemini starts at screen work.

Date: 2026-06-26
Type: state record. The user chose option (a): I (reviewer) cleaned up the prior conversation's
half-done Task 0 so the new Gemini starts from a verified-clean base rather than untangling the mess.
The log_53 immediate punch-list is now COMPLETE — done here, not handed forward.

## What I did (verified at each step, same rigor demanded of Gemini)

Isolated the good from the bad by testing one variable at a time:
- **Kept (the real fix):** `kotlin_tree.py:_inline_ok` expansion (cap 60->150, `text_match` hit test,
  `hits>=2`) — `workout_execution` now expands `matched 0->5` with genuine widget pairs;
  `pc_tree.text_match` (the safe anchored/length-gated rule); `ingest.py` widget vocabulary
  (`ExerciseHeader->exercise_header`, etc.).
- **Reverted (the regression source):** `align.py`. Its Phase-1 rewrite + spacer-strip-before-alignment
  + `text_match` in scored alignment caused the 4 matched-losses, the spurious `button<->set_row`
  pairs, and the 28/30 global bleed. Back to committed strict matching.
- **Removed** stray `patch.py`, `test.py`, `tools/dualgraph/test.py`.

## Verified-clean result

```
matched-loss regressions:  0   (was 4: onboarding/exercise_create/paths/session_detail)
spurious pairs:            none (align.py strict; button<->set_row gone)
screens changed:           7/30 (all honest kt_only reveals from expansion — no losses)
new baseline:              211/578 = 37%
```
matched went UP (204->211 from the expansion fix); the % dipped 38->37 only because expansion exposes
MORE real gaps (kt_only up) — i.e. the 37% is *more honest* than the old 38%, not a regression.

## The silo is now structural, not honor-system

`connectivity_gate.py --snapshot` now **refuses** unless `CONNECTIVITY_RATCHET=1` (reviewer-held).
Implementers cannot move the baseline; only the review/mix point ratchets, post-verification. The
goalpost-moving that hid the prior regressions is now mechanically blocked.

## Starting state for the fresh Gemina conversation

- Baseline is clean and committed (`WFL_PseudoCoup` `kit-migration-primitives`); gate is green.
- **Skip the log_53 punch-list — it's done.** Start directly at the screen-completion loop (log_49)
  under the log_53 protocol: one screen per change, reuse `widgets.py`+kit+existing VMs/services, gate
  every change vs the untouched baseline, any `matched` drop = STOP, hand to review with pair evidence,
  never `--snapshot`.
- **One open refinement (optional, low priority, under protocol):** `program_day_editor_screen` is
  still matcher-blind (`matched=0`, unchanged from baseline — not worse). Fully fixing its expansion
  without reintroducing regressions is a careful future task, not a blocker.

Pointers: `WFL_PseudoCoup` commit on `kit-migration-primitives` (the cleanup), log_53 (protocol),
log_52 (what went wrong), log_49 (the screen work-list).
