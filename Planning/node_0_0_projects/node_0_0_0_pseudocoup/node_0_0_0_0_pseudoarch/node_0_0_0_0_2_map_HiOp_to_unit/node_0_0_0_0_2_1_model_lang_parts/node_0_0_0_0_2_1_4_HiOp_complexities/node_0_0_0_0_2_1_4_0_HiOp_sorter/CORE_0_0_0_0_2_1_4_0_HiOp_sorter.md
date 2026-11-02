---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOp_complexities.HiOp_sorter
level: 7
status: draft
settled_by: the owner
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_HiOps.HiOp_sorter
designation: code (module)
node:
    name: HiOp_sorter
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_4_HiOp_complexities/node_0_0_0_0_2_1_4_0_HiOp_sorter/CORE_0_0_0_0_2_1_4_0_HiOp_sorter.md
super_node:
    name: HiOp_complexities
    path: ../CORE_0_0_0_0_2_1_4_HiOp_complexities.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_4_0 — HiOp_sorter

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOp_complexities.HiOp_sorter
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_HiOps.HiOp_sorter

## super_node

- [HiOp_complexities](../CORE_0_0_0_0_2_1_4_HiOp_complexities.md)

## sub_nodes

*(none yet)*

## definition

Sorts a language's operators into the owner's call-complexity classes (`simple`,
`hybrid`, `complex`, `undetermined`) and by their in-HiOp `BranchTree` depth
(`depth 0` vs. `depth 1+`), setting the downstream Unit-modelling order of
`model_lang_parts`.
