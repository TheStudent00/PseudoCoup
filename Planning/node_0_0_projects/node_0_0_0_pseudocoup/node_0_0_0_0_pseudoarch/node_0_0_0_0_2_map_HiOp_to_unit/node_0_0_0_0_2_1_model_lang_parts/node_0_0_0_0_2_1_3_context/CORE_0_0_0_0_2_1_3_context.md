---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.context
level: 6
status: draft
settled_by: the owner
supersedes: null
designation: code (container)
node:
    name: context
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_3_context/CORE_0_0_0_0_2_1_3_context.md
super_node:
    name: model_lang_parts
    path: ../CORE_0_0_0_0_2_1_model_lang_parts.md
sub_nodes:
    - name: entry_context
      path: node_0_0_0_0_2_1_3_0_entry_context/CORE_0_0_0_0_2_1_3_0_entry_context.md
    - name: model_contexts
      path: node_0_0_0_0_2_1_3_1_model_contexts/CORE_0_0_0_0_2_1_3_1_model_contexts.md
---

# CORE 0_0_0_0_2_1_3 — context

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.context
- **level:** 6
- **status:** draft
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [model_lang_parts](../CORE_0_0_0_0_2_1_model_lang_parts.md)

## sub_nodes

- [entry_context](node_0_0_0_0_2_1_3_0_entry_context/CORE_0_0_0_0_2_1_3_0_entry_context.md) — Models the `entry_info` (`state_info[0]`) object carried into the lowerer for every candidate probe (`context.py`: `Context(operator, holders, setup, preamble, program)` and `VALUE_FORMS`).
- [model_contexts](node_0_0_0_0_2_1_3_1_model_contexts/CORE_0_0_0_0_2_1_3_1_model_contexts.md) — Models how each storage place or surrounding context modifies a lowered Unit, so the lowerer's place logic is learned once and applied uniformly across every HiOp (`model_contexts.py`, moved here from `model_HiOps`).

## definition

The contexts a holder or HiOp can be in, both at entry into the lowerer
(`entry_context`: `entry_info` / `state_info[0]`) and in how each place
modifies a lowered Unit (`model_contexts`): the lowerer's logic for a place,
modelled once and applied the same way to every HiOp.

the owner, 2026-10-15 : "the way the context changes things is logic
defined within the lowerer. i want the way that context changes things to be
modelled. thats what context is. context could change a bunch of things but it
changes it according to its model."

- `entry_context` (`context.py`: `Context(operator, holders, setup, preamble, program)`)
  models the complete `entry_info` (`state_info[0]`) passed into the lowerer:
  the operator template, operand holders, places, value forms (`VALUE_FORMS`:
  lvalue `p->a` vs. integer constant literals `0..5` vs. address-of `&p->a`
  vs. dereference `*(p->a)`), and compile flags (`setup`).
- `model_contexts` models how each storage place (such as the bit-field place,
  learned in 1,092 of 1,092 riscv64 functions, log 479) transforms a Unit.
