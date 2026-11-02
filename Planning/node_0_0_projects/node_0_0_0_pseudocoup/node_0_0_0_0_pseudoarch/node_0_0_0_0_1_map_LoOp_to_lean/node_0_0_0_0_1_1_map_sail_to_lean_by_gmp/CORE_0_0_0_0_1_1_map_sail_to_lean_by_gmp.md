---
id: hq.projects.pseudocoup.pseudoarch.map_LoOp_to_lean.map_sail_to_lean_by_gmp
level: 5
status: draft
settled_by: the owner
supersedes: null
designation: code (module)
node:
    name: map_sail_to_lean_by_gmp
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_1_map_LoOp_to_lean/node_0_0_0_0_1_1_map_sail_to_lean_by_gmp/CORE_0_0_0_0_1_1_map_sail_to_lean_by_gmp.md
super_node:
    name: map_LoOp_to_lean
    path: ../CORE_0_0_0_0_1_map_LoOp_to_lean.md
sub_nodes: []
---

# CORE 0_0_0_0_1_1 — map_sail_to_lean_by_gmp

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_LoOp_to_lean.map_sail_to_lean_by_gmp
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

The Sail emit leaves the floating-point externals as `axiom` with no
body. Each one is given a body by slicing Berkeley SoftFloat to the
context, flattening it to one basic block, and walking that block to
Lean over the GMP primitives.

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
