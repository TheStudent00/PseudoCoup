# log_49 — TASK (Gemini): complete the screen port, connectivity-gated on every change

Date: 2026-06-26
Type: task assignment. The user's hard requirement: **every change must verify connectivity is
maintained.** This log defines that gate, the work-list, and the per-task loop. Read log_46/48 first
(domain is already built; this is screen gap-fill + reuse, not a rebuild).

## Prime directive

No change may DROP connectivity. After every change, the connectivity gate must stay green:
**no screen may lose `matched` nodes or gain `kt_only` gaps.** Progress = drive `kt_only` down and
ratchet the baseline. This is non-negotiable and is enforced mechanically, not by eyeball.

## What the metric is (and isn't) — read this so you don't misuse it

`tools/dualgraph/connectivity_gate.py` diffs each **hand-built** `src/ui/*_screen.py` against its WFL
Kotlin blueprint: `matched` / `kt_only` (WFL nodes PC lacks) / `pc_only` (PC nodes with no WFL source).

- It has **nothing to do with the transpiler.** It reads hand-built screens only.
- The absolute number (currently **204/540 = 38%**) is a **noisy lower bound**: the matcher is a fuzzy
  cross-framework aligner (Compose vs the kit), it under-credits differently-structured screens, and
  it produces some noise (bare `spacer`s in `kt_only`). **Do NOT treat 38% as truth or chase a literal
  100%.** Use it RELATIVELY: the gate's job is "this change didn't drop a node we already had."
- `kt_only` is a **prioritized to-do hint** (after ignoring noise), not a literal drop list.

## Verification protocol — run ALL of these after every change

```
python3 tools/dualgraph/connectivity_gate.py     # MUST exit 0 (no screen regressed)
python3 tools/smoke_screens.py                   # 30/30 screens construct
$HOME/Programming/flutter/bin/flutter test app_flutter   # goldens (CFE-strict)
# (only if you touch the transpiler:) python3 tools/transpiler/run_all.py
```
After a change that REDUCES a screen's `kt_only`, lock the gain in:
`python3 tools/dualgraph/connectivity_gate.py --snapshot`  (ratchet — never snapshot to hide a drop).

## Task 0 (DO FIRST) — make the metric trustworthy

The gate is blind where the matcher fails. Fix these before relying on it elsewhere:
1. **`matched=0` screens are matcher failures, not empty screens:** `workout_execution_screen`
   (360 LOC) and `program_day_editor_screen` (485 LOC) are fully built but align to nothing. Fix the
   `align.py` matching (label/structure normalization) so they pair their real nodes. Until then the
   gate can't protect them.
2. **Strip noise:** bare `spacer` nodes inflate `kt_only`. Filter layout-only nodes out of the diff
   (or mark them non-gating) so `kt_only` reflects real, wireable gaps.
Re-`--snapshot` after Task 0 so the baseline reflects the trustworthy numbers.

## The work-list (per-screen `kt_only`, ranked — the gap surface)

```
onboarding 68 · calibrate 30 · update_program 29 · settings_notifications 27 · debug_panel 26
log_cardio 13 · my_program 13 · workout_execution 13* · gym_create_wizard 12 · today 11 · you 11
progress 10 · report_bug 10 · wins 8 · stretch_suggestions 7 · gym_list 6 · program_editor 6
session_detail 5 · workout_summary 5 · exercise_picker 4 · gym_editor 4 · workout_warmup 4
paths 3 · program_day_editor 3* · programs 3 · exercise_detail 2 · workout_cooldown 2
exercise_create 1 · exercises 0 · path_detail 0      (* = matcher-blind, see Task 0)
```
`exercises_screen` and `path_detail_screen` are already at 0 — they show what "done" looks like.
Suggested order: Task 0 → low-hanging (the 1-6 screens, fast wins + validate the loop) → the heavy
ones (onboarding/calibrate/update_program). Tackle ONE screen per change.

## Per-task loop (one screen)

1. `python3 tools/dualgraph/connectivity_gate.py <slug>` → list its `kt_only` gap nodes.
2. For each REAL gap (skip pure layout noise — note which you skip and why):
   - build it by **reusing** `src/ui/widgets.py` (73 components: card, set_editor, list_row, fab,
     chip_row, switch_row, dropdown_field, …) + `src/kit.py` primitives — do NOT hand-roll what exists;
   - wire its handler/nav to the screen's **existing** ViewModel (`src/viewmodel/`), which is already
     de-reactified and points at the real `src/domain` / `src/engine` services. (Only the few WHOLE
     missing screens — history, wins_list, etc. — need a new VM; use the transpiler skeleton there.)
3. `connectivity_gate.py` → confirm this screen's `kt_only` dropped AND **no other screen regressed**
   (shared-widget edits can break siblings — the gate checks all 30).
4. `smoke_screens.py` + `flutter test` → no crashes, no golden regressions.
5. `connectivity_gate.py --snapshot` → ratchet. Commit (per-turn checkpoint).

## Guardrails (how connectivity gets faked — don't)

- **Structural ≠ behavioral.** The gate sees that a `button 'Delete gym'` node exists; it CANNOT see
  that its handler actually deletes via `gym_service`. Wiring a node means wiring its REAL handler to
  the REAL service — not a stub that just makes the node appear. That correctness is on you.
- **No node-stuffing.** Don't emit empty/placeholder nodes to satisfy the matcher.
- **Don't delete `pc_only` to inflate the ratio.** The gate watches `matched` (must not fall), so you
  can't game the percentage by removing PC nodes.
- **Reuse over rebuild.** If a gap matches an existing widget pattern, use it; new components are built
  once then reused.

## Definition of done

- Per screen: real gaps closed (`kt_only` at its noise floor), gate green, smoke 30/30, goldens pass,
  baseline ratcheted.
- Overall: `matched` up / `kt_only` down across the fleet, every step gated — and because the gate
  runs all 30 screens each time, nothing silently drops along the way. That is the connectivity
  guarantee the user asked for.

Pointers: `tools/dualgraph/connectivity_gate.py` (gate + `<slug>` gap lister + `--snapshot`),
`tools/dualgraph/align.py` (the diff), `src/ui/widgets.py` (reuse library), log_48 (why this is
fill-in not rebuild), log_46 (domain already built).
