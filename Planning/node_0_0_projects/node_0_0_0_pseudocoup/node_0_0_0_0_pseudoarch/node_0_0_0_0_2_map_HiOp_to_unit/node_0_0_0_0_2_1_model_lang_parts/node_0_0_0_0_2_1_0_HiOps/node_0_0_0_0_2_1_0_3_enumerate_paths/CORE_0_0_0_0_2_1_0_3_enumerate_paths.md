---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps.enumerate_paths
level: 7
status: draft
settled_by: the owner
supersedes: null
designation: code (module)
node:
    name: enumerate_paths
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_0_HiOps/node_0_0_0_0_2_1_0_3_enumerate_paths/CORE_0_0_0_0_2_1_0_3_enumerate_paths.md
super_node:
    name: HiOps
    path: ../CORE_0_0_0_0_2_1_0_HiOps.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_0_3 — enumerate_paths

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps.enumerate_paths
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [HiOps](../CORE_0_0_0_0_2_1_0_HiOps.md)

## sub_nodes

*(none yet)*

## definition

Groups all accepted traced runs of each operator into distinct deterministic
`(entry, exit)` lowering paths (`paths.json`), where each distinct path
defines a HiOp variant and records its checking action, lowering mark, inner
basic-block sequence, emitted IR instructions (`ir`, `ir_typed`, `exits`),
and the equivalence-class holder tuples that take that path.
