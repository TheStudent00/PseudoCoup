---
id: hq.projects.pseudocoup.ledgerer.progress
status: living
---

# PROGRESS — ledgerer

- 2026-09-22: node created from the ontology in
  `Planning/CORE_0_0_0_pseudocoup.md
- 2026-10-09, design: the UR-Node is locked by the owner ("well its a strong
  argument. we can lock that design in. i have no disagreements with it."):
  a HiOp variant carried with its Units, one per architecture, and their Lean
  terms. Recorded as the register entry `universal_rich_node`
  (`realize: false`, code (class)) and the CORE's `## design`. The artifact's
  name is now the UR-Ledger, formerly UR-AST (the owner: "great, lets update that
  part of the design too"), and the ledger is an RCG, in the owner's words, in the
  CORE's definition. Status: design locked; no code
  (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-13, declarations by hand: done. `SUPPORT_gnu_c_declarations_by_hand.md`
  holds log 385's 22 rules, the declarations named since, the attributes, and
  riscv64's layout read back from clang by run elv2_l157 (65 of 65 rows; my
  63 predictions all held). Status: done by hand; modelling later, at the owner's
  word (`Planning/CORE_0_0_0_pseudocoup.md).

- 2026-11-01, implementation & 2-cycle roundtrip verification: `UniversalRichNode`
  (`Projects/PseudoCoup/ledgerer/universal_rich_node.py`), `URLedger`,
  `ScriptToLedger`, and `LedgerToScript` (`Projects/PseudoCoup/ledgerer/ur_ledger.py`)
  built and verified in `Projects/PseudoCoup/ledgerer/test_roundtrip_two_cycles.py`.
  Verified 2-cycle roundtrip idempotence (`lang_x -> Hub -> lang_y -> Hub -> lang_x -> Hub -> lang_y -> Hub -> lang_x`)
  with `T_1 == T_2`, `S_1 == S_2`, and 100% bit-identical evaluation across all 5 stages.
