# log_56 — exercise_detail_screen gap closed

Date: 2026-06-26
Type: verification report

## The Gap
- **Screen**: `exercise_detail_screen`
- **Gap**: `widget:chip *click->?`
- **Context**: The `connectivity_gate.py` tool reported 1 `kt_only` node for `exercise_detail_screen`. 

## The Cause
The Kotlin blueprint uses static `if/else` branches to render the attributes (Custom vs. Built-in, Compound vs. Isolation, etc.). The Kotlin AST parser (`kotlin_tree.py`) traverses all branches, extracting **4 distinct chip nodes**.

The PseudoCoup side used a comma-joined string + `_chip_flow` (which iterates over the string via a `while` loop), so `pc_tree.py` collapsed them and extracted only **1 loop node**. This caused a 4-to-1 cardinality mismatch in `align.py`, leaving one of the 4 KT chips unmatched and reported as a `kt_only` gap.

## The Fix
Unrolled the `_chip_flow` loop in `src/ui/exercise_detail_screen.py` into distinct `chip()` calls that exactly match the `if/else` branching logic of the Kotlin blueprint. This allows `pc_tree.py` to extract 4 separate chips that perfectly align with the 4 KT chips.

## Verification
- **Gate Output**: `+ exercise_detail_screen: matched 10->11  kt_only 1->0`
- **Smoke Tests**: `SWEEP: 30/30 screens rendered clean` (Pass)
- **Flutter Tests**: `All tests passed!` (Pass)

The change successfully closes the gap without regressions. The reviewer can now ratchet the baseline (`--snapshot`).
