---
id: hq.projects.pseudocoup.pseudoarch.map_unit_to_lean.compose_LoOp_leans
level: 5
status: draft
settled_by: Dee
supersedes: null
designation: code (module)
node:
    name: compose_LoOp_leans
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_3_map_unit_to_lean/node_0_0_0_0_3_0_compose_LoOp_leans/CORE_0_0_0_0_3_0_compose_LoOp_leans.md
super_node:
    name: map_unit_to_lean
    path: ../CORE_0_0_0_0_3_map_unit_to_lean.md
sub_nodes: []
---

# CORE 0_0_0_0_3_0 — compose_LoOp_leans

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_unit_to_lean.compose_LoOp_leans
- **level:** 5
- **status:** draft
- **designation:** code (module)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [map_unit_to_lean](../CORE_0_0_0_0_3_map_unit_to_lean.md)

## sub_nodes

*(none yet)*

## definition

One term per Unit. It also decides straight-line against
fall-through trace: a Unit that branches before its end is not its
whole body, only the path taken when nothing branches, and the term
says so.

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
