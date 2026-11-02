---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.context.model_contexts
level: 7
status: draft
settled_by: the owner
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_HiOps.model_contexts
designation: code (module)
node:
    name: model_contexts
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_3_context/node_0_0_0_0_2_1_3_1_model_contexts/CORE_0_0_0_0_2_1_3_1_model_contexts.md
super_node:
    name: context
    path: ../CORE_0_0_0_0_2_1_3_context.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_3_1 — model_contexts

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.context.model_contexts
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_HiOps.model_contexts

## super_node

- [context](../CORE_0_0_0_0_2_1_3_context.md)

## sub_nodes

*(none yet)*

## definition

Models how each storage place or surrounding context modifies a lowered Unit,
so the lowerer's place logic is learned once and applied uniformly across
every HiOp (`model_contexts.py`, moved here from `model_HiOps`).

Has one place coded: the bit-field place, learned by automation across 1,092
of 1,092 riscv64 functions .
