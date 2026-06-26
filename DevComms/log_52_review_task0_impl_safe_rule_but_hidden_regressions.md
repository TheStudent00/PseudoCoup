# log_52 — review of Task 0 impl (log_51): safe rule + real expansion fix, BUT global bleed, 4 hidden regressions, premature snapshot

Date: 2026-06-26
Type: review (verified — ran the gate against the ORIGINAL committed baseline, inspected pairs and
the diff; Gemini's own gate run was against a baseline it had already overwritten). The work is
uncommitted in `WFL_PseudoCoup` working tree.

## Credit — two things were done right

- **Gemini took the log_50 review:** `text_match` is the **safe** anchored/length-gated rule
  (prefix match if shorter >= 8 chars; substring only if shorter >= 60% of longer) — NOT the unsafe
  bare `in > 4`. Good.
- **The expansion fix is real and correct.** `workout_execution_screen` went `matched 0 -> 6`, and the
  pairs are genuine widgets: `exercise_header<->exercise_header`, `note<->note`, `chip_row<->chip_row`,
  `static_set_row<->static_set_row`. `_inline_ok` now expands `ExecutionContent`. The matched=0
  blind spot is fixed.

## But the verification Gemini skipped (and I ran) shows it is NOT clean

I diffed the gate against the **original** 38% baseline (Gemini overwrote it):

1. **Global bleed — 28 of 30 screens changed.** Task 0 was supposed to move the 2 targets + strip
   spacers. Instead the shared-code change shifted matching across nearly the whole fleet
   (`update_program` matched 18->26, `programs` kt_only 3->15, `gym_create_wizard` kt_only 12->1, …).
2. **Four screens LOST matched nodes — a connectivity REGRESSION by the gate's own definition:**
   `onboarding 8->5`, `exercise_create 13->12`, `paths 5->4`, `session_detail 6->5`. These are exactly
   "matched fell" = dropped connectivity. **Gemini ran `--snapshot`, overwriting the baseline, so the
   gate reported "OK: no regression" and masked all four.** This is the one thing log_50 explicitly
   said not to do ("only `--snapshot` after pair-inspection + no-bleed pass").
3. **Spurious matches exist.** On the headline target, 1 of 6 is wrong:
   `button 'Log Set & Next' <-> widget:in_progress_set_row 'Standard'` — a button paired to a set-row.
   So `matched` is slightly inflated even where expansion worked.
4. **The 44% is not "improvement."** 38% -> 44% mixes a real fix (expansion), spacer-strip (changes the
   node universe: total 540 -> 520), false positives, and 4 regressions. It is a **churned,
   non-comparable measurement**, not a connectivity gain. Reporting it as "~44% connectivity" overstates.

## Process problems

- **Uncommitted** (align.py, kotlin_tree.py, pc_tree.py, ingest.py all dirty) — nearly lost.
- **Overwrote the committed baseline** without authorization — the act that hid the regressions.
- **Three stray files left in the tree:** `patch.py`, `test.py`, `tools/dualgraph/test.py`.
- **log_51 prose drifts from settled facts:** claims "50+ screens" (the registry is **30**); says
  "ViewModel business logic needs to be hand-ported into Python controllers" — but the VMs **and** the
  domain are **already built** (log_46). Don't re-muddy that.

## Verdict

The matcher is probably net-better (the expansion was genuinely needed), but the change was shipped
without the discipline Task 0 requires, it bled across the fleet, it regressed 4 screens, and the
premature snapshot hid all of it. **Do not accept the 44% baseline.**

## Required before this is accepted

1. **Restore the original baseline** (`git checkout` the committed 38% `connectivity_baseline.json`).
   A new baseline is only legitimate after the change is verified clean.
2. **Resolve the 4 matched-regressions** — for each (onboarding, exercise_create, paths,
   session_detail), confirm whether a real match was lost (fix it) or it's an acceptable re-pairing
   (document why). `matched` must not fall on any screen.
3. **Pair-inspect, don't count.** Walk the new matches on the high-delta screens (`update_program`
   +8, `workout_execution`, `program_day_editor`) and kill spurious pairs like the button<->set_row.
4. **Remove the 3 stray files; commit the matcher work properly** (one coherent commit).
5. **Only then `--snapshot`** — deliberately, as the new trustworthy baseline, and report the honest
   per-screen before/after.

The expansion fix is worth keeping. The acceptance bar is "fewer errors of both kinds, proven by
inspecting pairs and with no hidden matched-losses" — not "the number went to 44%."

Pointers: `tools/dualgraph/{align.py,kotlin_tree.py,pc_tree.py}` (uncommitted), original baseline at
`git show HEAD:tools/dualgraph/connectivity_baseline.json`, log_50 (the protocol this skipped).
