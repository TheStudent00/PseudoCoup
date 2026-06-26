# log_65 — TASK: everything remaining to finish the connectivity port + oversight

Date: 2026-06-26
Type: full task backlog (the task that should have accompanied log_64). For the implementer, under the
log_55 protocol. Reviewer verifies + ratchets. Baseline today: 220/451 = 49%, 231 gaps, 30 screens.
**Do every track. Report each increment as a DevComms log. Never `--snapshot` (reviewer-only).**

## Track A — finish the OVERSIGHT (do first; it's how the rest gets checked)

1. **Resolve Kotlin handlers in `kotlin_tree.py`.** 45 matched objects show `*click->?` because the
   extractor doesn't resolve the onClick lambda to its target (VM method / nav). Resolve them (lambda
   body → method name / navigate target) so the side-by-side edge check can actually verify them.
2. **Handler-name ledger** (edge analogue of the object ledger). KT/PC handler names diverge
   (`onNavigateToDetail` vs `on_item_click`) — record confirmed correspondences so the 17 flagged
   edge-mismatches reduce to GENUINE source→target differences. Same rules: each entry verified against
   the Kotlin source; no over-aliasing.
3. **Wire edge-verification into `connectivity_gate.py`.** Once 1+2 cut the noise, make the gate FAIL
   when a matched object is wired to a different target in KT vs PC. This turns "same object present"
   into "same object wired the same way" — the connectivity guarantee. Ratchet an edge baseline.
4. **Size/position extraction.** `pc_tree` captures ZERO layout; the Node schema has no width/height/x/y.
   Extract it: `pc_tree` from the kit's zone params (direction/weight), `kotlin_tree` from Compose
   `Modifier` (size/arrangement/alignment); add fields to the Node; show in `build_sidebyside.py`.
   Decide with the reviewer whether it gates or is informational (it overlaps what the goldens guard).

## Track B — finish the OBJECT ledger (kills the false-negatives)

5. **Sweep the fleet for kind-alias renames** (same class as ledger v1). Strong signal: a kt_only that
   mirrors a pc_only. Known candidates: `CircularProgressIndicator`↔`progress` (gym_editor /
   session_detail / workout_summary), `*Card`/`*Row` composables ↔ PC `*_card`/`*_row` widgets. Record
   ONLY after confirming each against the Kotlin source (mandatory `ref` file:line).
6. **paths `PathSelectionSheet` (1:N)** — deferred from v1. Read the Kotlin composable; inline it via the
   `_inline_ok`/`ExecutionContent` expansion mechanism so its internals (scrim/note/section_header) match
   PC's — NOT a 1:N ledger row. Show the Kotlin evidence.
7. **Onboarding wizard steps.** PC has 2 `wizard_step_scaffold` vs 8 KT `*Step` composables — so ~6 are
   GENUINE gaps, ~2 are renames. Confirm which against `OnboardingScreen.kt`; record only true renames.

## Track C — close the GENUINE gaps (the screen loop)

8. After B reduces false-negatives, the remaining red rows are real. Close each **faithfully**: reuse
   `src/ui/widgets.py` + `src/kit.py`, wire to the EXISTING ViewModel (`src/viewmodel/`), and **confirm
   against the Kotlin blueprint (file:line)** that the element is genuinely absent and the type/copy you
   add matches. Big screens: onboarding (33), workout_execution (37), calibrate (30), update_program,
   settings_notifications.
9. Drive toward 100% of REAL gaps. Ceiling: some kt_only are deliberately **deferred features** PC chose
   not to build — those are product calls; **flag them, do not fake them**.

## The discipline (every track, non-negotiable)

- **Verify against the blueprint, not the matcher.** Three ways people have gamed it, all rejected
  (log_55): spacers aren't gaps; don't inline a helper to flip a kind; don't rewrite copy / swap element
  types to satisfy a string/kind compare. Only change a screen for a genuinely-absent element.
- **You never `--snapshot` or edit `connectivity_baseline.json`.** The reviewer ratchets after verifying.
- **Report every change as a DevComms log** with: the gaps, Kotlin `ref` evidence, the fix, KT↔PC pair
  evidence, gate/smoke/golden results.
- **Per-turn: commit both repos** (PseudoCoup `main`, WFL_PseudoCoup `kit-migration-primitives`).

Pointers: log_66 (the full handoff / reviewer manual), log_55 (implementer protocol), log_62 (object
ledger), log_64 (oversight v2), `tools/dualgraph/*`.
