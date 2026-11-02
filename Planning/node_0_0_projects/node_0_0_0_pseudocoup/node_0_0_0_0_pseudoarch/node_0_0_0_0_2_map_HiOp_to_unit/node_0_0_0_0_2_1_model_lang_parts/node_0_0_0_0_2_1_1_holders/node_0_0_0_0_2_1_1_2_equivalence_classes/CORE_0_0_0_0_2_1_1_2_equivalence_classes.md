---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.holders.equivalence_classes
level: 7
status: draft
settled_by: Dee
supersedes: null
designation: code (module)
node:
    name: equivalence_classes
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_1_holders/node_0_0_0_0_2_1_1_2_equivalence_classes/CORE_0_0_0_0_2_1_1_2_equivalence_classes.md
super_node:
    name: holders
    path: ../CORE_0_0_0_0_2_1_1_holders.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_1_2 — equivalence_classes

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.holders.equivalence_classes
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [holders](../CORE_0_0_0_0_2_1_1_holders.md)

## sub_nodes

*(none yet)*

## definition

Partitions a language's holder pool by its `holder_facts.json` gate-predicate
answers into canonical **gate-predicate equivalence class representatives**
(`EQUIVALENCE_CLASS_HOLDERS` and `TYPE_ONLY_HOLDERS`).

Two holders belong to the same gate-predicate equivalence class when they give
identical answers to the lowerer's type-checking and IR-lowering predicates.
Selecting one canonical representative per equivalence class (`42`
`EQUIVALENCE_CLASS_HOLDERS` + `3` `TYPE_ONLY_HOLDERS` in GNU C) guarantees
that `branch_trees.unlock_branch` tests every gate-distinct holder category
(closing `SUPPORT_gnu_c_vocab_what_is_missing.md` item 51) without
combinatorial cross-product explosion.
