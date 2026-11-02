---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.context.entry_context
level: 7
status: draft
settled_by: Dee
supersedes: null
designation: code (module)
node:
    name: entry_context
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_3_context/node_0_0_0_0_2_1_3_0_entry_context/CORE_0_0_0_0_2_1_3_0_entry_context.md
super_node:
    name: context
    path: ../CORE_0_0_0_0_2_1_3_context.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_3_0 — entry_context

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.context.entry_context
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [context](../CORE_0_0_0_0_2_1_3_context.md)

## sub_nodes

*(none yet)*

## definition

Models the `entry_info` (`state_info[0]`) object carried into the lowerer for
every candidate probe (`context.py`: `Context(operator, holders, setup,
preamble, program)` and `VALUE_FORMS`).

By the Lowerer's Promise, `state_info[0]`—comprising the operator syntax
template, the operand holder types, the operand value forms (`lvalue` `p->a`,
integer constants `0..5`, address-of `&p->a`, dereference `*(p->a)`), the
compile flags (`setup`), and the target—uniquely determines every `derived_info`
(`state_info[n]`) local variable inside the HiOp and the exact `(entry, exit)`
path taken through the lowerer.
