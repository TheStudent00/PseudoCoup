# log_20 — Phase 1 Audit Results & Phase 2 Kickoff Proposal

Date: 2026-06-25
Type: Audit Report & Architecture Proposal

## Phase 1 Connectivity Audit Results
Following the guidance in `log_19`, we scaled the static `probe.py` to recursively scan and auto-match all 26 screens between the fully-wired Kotlin reference application and the hand-built PseudoCoup Python port. 

The batch execution results definitively prove the massive scale of the "dropped edges" problem caused by the previous transpiler attempt:
- **Total Edges Preserved:** `171 / 636`
- **Connectivity Parity:** `26.89%`
- **Total Missing Connectivity Nodes:** `465`

Critical screens like `workout_execution` are missing 94% of their functional edges (`addSet`, `setWeight`, etc.), and `workout_summary` is missing 100% of its state payload.

## The Pivot Decision
We have decided that manually patching 465 gaps into the existing PseudoCoup Python files is an exercise in futility. The old `WFL_PseudoCoup` UI work is now considered effectively outdated because it cannot guarantee connectivity.

## Phase 2 Kickoff Proposal: The Literal IR Transpiler
We are officially pivoting to **Phase 2**. We will build a new transpiler module that performs a strict, literal, 1:1 translation from Kotlin AST to Python AST, with zero paradigm interpretation.

**Core Objectives for the Literal IR Transpiler:**
1. **Completeness:** It must use `tree-sitter` to translate all classes, state fields, methods, `when` statements, and control loops into their exact Python equivalents (`match`/`if-elif`).
2. **No Silent Drops:** As Claude noted in `log_19`, a partial translator that silently drops unhandled nodes reintroduces the exact gap we are trying to fix. The new transpiler MUST either translate the node faithfully or explicitly mark unhandled nodes (like `Flow` or `CoroutineScope`) with a loud, unmissable `TODO_UNHANDLED_NODE` marker in the output Python.
3. **Connectivity Verification:** The output of this Phase 2 transpiler will be run against the `probe.py` tool. It must achieve 100% connectivity preservation against the Kotlin reference.

**Review Request (For Claude):**
Please review this proposal for the Phase 2 Literal IR Transpiler. Do you agree with the strict "No Silent Drops" policy? Are there any specific tree-sitter Kotlin node types we should explicitly plan to handle (or ignore via explicit markers) during this literal 1:1 conversion?
