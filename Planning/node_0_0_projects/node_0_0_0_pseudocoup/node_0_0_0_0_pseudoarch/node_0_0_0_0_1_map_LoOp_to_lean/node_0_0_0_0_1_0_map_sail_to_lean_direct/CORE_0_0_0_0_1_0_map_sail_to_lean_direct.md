---
id: hq.projects.pseudocoup.pseudoarch.map_LoOp_to_lean.map_sail_to_lean_direct
level: 5
status: draft
settled_by: the owner
supersedes: null
designation: code (module)
node:
    name: map_sail_to_lean_direct
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_1_map_LoOp_to_lean/node_0_0_0_0_1_0_map_sail_to_lean_direct/CORE_0_0_0_0_1_0_map_sail_to_lean_direct.md
super_node:
    name: map_LoOp_to_lean
    path: ../CORE_0_0_0_0_1_map_LoOp_to_lean.md
sub_nodes: []
---

# CORE 0_0_0_0_1_0 — map_sail_to_lean_direct

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_LoOp_to_lean.map_sail_to_lean_direct
- **level:** 5
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [map_LoOp_to_lean](../CORE_0_0_0_0_1_map_LoOp_to_lean.md)

## sub_nodes

*(none yet)*

## definition

A LoOp's Lean is the body Sail already emitted for it. One clause
covers several LoOps where the clause dispatches on an enum.

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
