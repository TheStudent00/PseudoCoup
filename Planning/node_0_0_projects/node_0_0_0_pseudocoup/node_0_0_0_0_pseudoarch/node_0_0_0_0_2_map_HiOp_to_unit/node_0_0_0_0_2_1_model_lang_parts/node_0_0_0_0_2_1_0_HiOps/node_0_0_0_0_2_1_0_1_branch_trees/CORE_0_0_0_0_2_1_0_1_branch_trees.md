---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps.branch_trees
level: 7
status: draft
settled_by: Dee
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.complex_signature_reader
designation: code (module)
node:
    name: branch_trees
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_0_HiOps/node_0_0_0_0_2_1_0_1_branch_trees/CORE_0_0_0_0_2_1_0_1_branch_trees.md
super_node:
    name: HiOps
    path: ../CORE_0_0_0_0_2_1_0_HiOps.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_0_1 — branch_trees

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps.branch_trees
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** Dee
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.complex_signature_reader

## super_node

- [HiOps](../CORE_0_0_0_0_2_1_0_HiOps.md)

## sub_nodes

*(none yet)*

## definition

The language-agnostic in-HiOp control-flow tree builder and gate-chain solver
(`branch_trees.py`: `BranchTree`, `tree_of_function`, `super_chain_of_branch`,
`PartConstraint`, `AbstractConstraint`, `CandidateWriter`, `unlock_branch`).

- **In-HiOp `BranchTree` (Calls Not Followed):**
  Parses the lowerer's source functions for each HiOp into structured trees of
  `if`, `else if`, `else`, `switch`, `case`, `?:`, and short-circuit `&&` /
  `||` gates with exact line spans (`line..end_line`) and parent chains,
  restricted to code within the HiOp's own functions (`--in-hiop`).
- **`entry_info` (`state_info[0]`) and `derived_info` (`state_info[n]`) Gate Translation:**
  Reads each gate atom along an untaken branch chain (`chain_to_unlock`) using
  the language's `gate_tables` (`leaf_reading`, `PART_NAMES`, `INNER_READS`),
  mapping both direct `entry_info` expressions and in-HiOp local variables
  (`derived_info` / `state_info[n]`) to operand indices (`part`), nesting
  levels (`outer` vs. `inner` element/pointee), value forms (`0..5`), integer
  switch-case constants, and cross-operand relational constraints
  (`SrcType == DstType`, `hasSameType`).
- **Equivalence-Class Gate Unlocking (`unlock_branch`, `CandidateWriter.write_from_constraint`):**
  Intersects all gate predicates along the chain against the pre-queried
  `holder_facts` table and emits **one representative per surviving
  gate-predicate equivalence class** (`EQUIVALENCE_CLASS_HOLDERS`), unlocking
  every reachable branch without combinatorial explosion.
