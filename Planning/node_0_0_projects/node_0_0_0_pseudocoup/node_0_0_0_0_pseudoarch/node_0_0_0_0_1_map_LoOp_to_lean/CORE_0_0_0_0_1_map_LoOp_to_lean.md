---
id: hq.projects.pseudocoup.pseudoarch.map_LoOp_to_lean
level: 4
status: draft
settled_by: the owner
supersedes: null
designation: code (container)
node:
    name: map_LoOp_to_lean
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_1_map_LoOp_to_lean/CORE_0_0_0_0_1_map_LoOp_to_lean.md
super_node:
    name: pseudoarch
    path: ../CORE_0_0_0_0_pseudoarch.md
sub_nodes:
    - name: map_sail_to_lean_direct
      path: node_0_0_0_0_1_0_map_sail_to_lean_direct/CORE_0_0_0_0_1_0_map_sail_to_lean_direct.md
    - name: map_sail_to_lean_by_gmp
      path: node_0_0_0_0_1_1_map_sail_to_lean_by_gmp/CORE_0_0_0_0_1_1_map_sail_to_lean_by_gmp.md
---

# CORE 0_0_0_0_1 — map_LoOp_to_lean

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_LoOp_to_lean
- **level:** 4
- **status:** draft
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [pseudoarch](../CORE_0_0_0_0_pseudoarch.md)

## sub_nodes

- [map_sail_to_lean_direct](node_0_0_0_0_1_0_map_sail_to_lean_direct/CORE_0_0_0_0_1_0_map_sail_to_lean_direct.md) — A LoOp's Lean is the body Sail already emitted for it.
- [map_sail_to_lean_by_gmp](node_0_0_0_0_1_1_map_sail_to_lean_by_gmp/CORE_0_0_0_0_1_1_map_sail_to_lean_by_gmp.md) — The Sail emit leaves the floating-point externals as `axiom` with no body.

## definition

One Lean expression per LoOp, with nothing left body-less.

Two routes, because the Sail emit leaves a floating-point remainder:
the model's own execute clause covers the integer and control LoOps
directly, and the rest are given bodies by slicing GMP's SoftFloat.

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
