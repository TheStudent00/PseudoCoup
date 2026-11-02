---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOp_configurations.dependent_HiOp_reader
level: 7
status: draft
settled_by: the owner
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.extract_lang_vocab.dependent_HiOp_reader
designation: code (module)
node:
    name: dependent_HiOp_reader
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_5_HiOp_configurations/node_0_0_0_0_2_1_5_0_dependent_HiOp_reader/CORE_0_0_0_0_2_1_5_0_dependent_HiOp_reader.md
super_node:
    name: HiOp_configurations
    path: ../CORE_0_0_0_0_2_1_5_HiOp_configurations.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_5_0 — dependent_HiOp_reader

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOp_configurations.dependent_HiOp_reader
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.extract_lang_vocab.dependent_HiOp_reader

## super_node

- [HiOp_configurations](../CORE_0_0_0_0_2_1_5_HiOp_configurations.md)

## sub_nodes

*(none yet)*

## definition

Reads from the lowerer's checking code where each dependent-HiOp (such as
`BreakStmt`, `ContinueStmt`, `CaseStmt`, `DefaultStmt`, `ReturnStmt`) may
stand and which depended-HiOp container (`SwitchStmt`, `WhileStmt`, `DoStmt`,
`ForStmt`, function body) it requires.
