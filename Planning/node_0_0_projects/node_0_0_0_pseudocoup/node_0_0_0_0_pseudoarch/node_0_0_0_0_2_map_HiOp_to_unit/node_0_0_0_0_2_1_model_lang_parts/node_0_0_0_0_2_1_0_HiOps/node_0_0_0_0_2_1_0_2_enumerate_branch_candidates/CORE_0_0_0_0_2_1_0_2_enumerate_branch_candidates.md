---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps.enumerate_branch_candidates
level: 7
status: draft
settled_by: Dee
supersedes: null
designation: code (module)
node:
    name: enumerate_branch_candidates
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_0_HiOps/node_0_0_0_0_2_1_0_2_enumerate_branch_candidates/CORE_0_0_0_0_2_1_0_2_enumerate_branch_candidates.md
super_node:
    name: HiOps
    path: ../CORE_0_0_0_0_2_1_0_HiOps.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_0_2 — enumerate_branch_candidates

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps.enumerate_branch_candidates
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [HiOps](../CORE_0_0_0_0_2_1_0_HiOps.md)

## sub_nodes

*(none yet)*

## definition

The closed-loop in-HiOp candidate driver and branch classifier
(`enumerate_branch_candidates.py`: `UnreachedBranch`, `BranchCondition`,
`VariantCandidate`, `Record`, `classify_branches`, `enumerate_every_path`).

- Wraps candidate holder tuples and options into standard-form source programs
  via `context/entry_context` (`Context`) and the language's `templates`
  (`operators_of(key)`).
- Runs the language's instrumented lowerer (`--in-hiop`) to record executed
  in-HiOp source lines, basic blocks, checking actions, lowering marks, and
  emitted IR exits.
- Classifies every branch in the HiOp's `BranchTree` into one of four states:
  - `taken`: reached and executed by at least one traced candidate.
  - `not needed`: proven to be a refusal/diagnostic path (`REFUSAL`), a
    non-target language guard (`LANGUAGE_NAMES`), or a debug/warning/sanitizer
    guard (`NOT_NEEDED_NAMES`).
  - `cannot reach`: proven unreachable from valid single-HiOp `entry_info`
    (`entry_info_unreachable`), target invariant (`CANNOT_REACH_NAMES`),
    `llvm_unreachable`, or DWARF closing-brace trampoline (`is_closing_brace_block`).
  - `open`: passed to `branch_trees.unlock_branch` to generate next-round
    equivalence-class candidates until `open == 0`.
