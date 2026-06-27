# Goal
Task 0: Make the `connectivity_gate` metric trustworthy by fixing alignment failures for `workout_execution_screen` and `program_day_editor_screen`, and by stripping noisy `spacer` nodes from `kt_only` gaps.

## Proposed Changes

### 1. `tools/dualgraph/align.py` - Structure & Label Normalization
- The root cause of `matched=0` for large screens like `workout_execution` is that their root composables (like `ExecutionContent` or `ExerciseGroupCard`) do not expand. They only expand if `_inline_ok` detects sufficient inner matches with the PseudoCoup (PC) tree.
- The inner matches fail because PC often abbreviates long Kotlin strings (e.g., `"No exercises"` vs `"This workout has no exercises"`) or ignores newlines. `align.py` currently demands strict `la == lb` equality.
- **Change:** I will relax the label matching in `_score` and the Phase 1 text matching to allow substring matches (e.g., `la in lb or lb in la`) as long as the match is reasonably long (e.g., > 4 chars). This will allow the inner strings to hit, triggering `_inline_ok` to expand the composables, and drastically increasing `matched` node counts.

### 2. `tools/dualgraph/align.py` - Strip Noise (Spacers)
- The gate counts bare `spacer` nodes as `KOTLIN-only` gaps, artificially inflating the gap metric with purely visual layout adjustments that have no behavioral wiring.
- **Change:** I will filter out nodes with `kind == "spacer"` from the `kt_only` list before it is returned in the `align` function, so they don't count against the gate metric.

## Verification
- Run `python3 tools/dualgraph/align.py workout_execution_screen` and verify `matched` > 0 and `ExecutionContent` expands.
- Run `python3 tools/dualgraph/align.py program_day_editor_screen` and verify `matched` > 0 and `ExerciseGroupCard` expands.
- Check `tools/dualgraph/connectivity_gate.py` to confirm overall numbers improve.
- Run `python3 tools/dualgraph/connectivity_gate.py --snapshot` to lock in the new trustworthy baseline.

## User Review Required
Please review this plan. If approved, I will implement these fixes for Task 0 and we can move on to the actual screen porting (the work-list).
