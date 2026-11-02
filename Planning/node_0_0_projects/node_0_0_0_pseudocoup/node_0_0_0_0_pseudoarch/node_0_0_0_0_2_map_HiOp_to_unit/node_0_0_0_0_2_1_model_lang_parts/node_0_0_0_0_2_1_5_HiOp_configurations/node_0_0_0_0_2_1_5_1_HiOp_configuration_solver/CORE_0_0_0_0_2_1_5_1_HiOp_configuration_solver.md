---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOp_configurations.HiOp_configuration_solver
level: 7
status: draft
settled_by: Dee
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.extract_lang_vocab.HiOp_configuration_solver
designation: code (module)
node:
    name: HiOp_configuration_solver
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_5_HiOp_configurations/node_0_0_0_0_2_1_5_1_HiOp_configuration_solver/CORE_0_0_0_0_2_1_5_1_HiOp_configuration_solver.md
super_node:
    name: HiOp_configurations
    path: ../CORE_0_0_0_0_2_1_5_HiOp_configurations.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_5_1 — HiOp_configuration_solver

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOp_configurations.HiOp_configuration_solver
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** Dee
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.extract_lang_vocab.HiOp_configuration_solver

## super_node

- [HiOp_configurations](../CORE_0_0_0_0_2_1_5_HiOp_configurations.md)

## sub_nodes

*(none yet)*

## definition

Finds each operator's held-form configuration (`N`-body statement patterns,
depended-HiOp containers, and multi-template syntactic forms `operators_of(key)`)
by testing arrangements on the lowerer and verifying them against
`dependent_HiOp_reader` and `branch_trees`.
