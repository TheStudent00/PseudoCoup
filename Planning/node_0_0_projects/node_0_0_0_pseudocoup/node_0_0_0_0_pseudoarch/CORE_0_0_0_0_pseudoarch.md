---
id: hq.projects.pseudocoup.pseudoarch
level: 3
status: draft
settled_by: the owner
supersedes: null
designation: code (container)
node:
    name: pseudoarch
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/CORE_0_0_0_0_pseudoarch.md
super_node:
    name: pseudocoup
    path: ../CORE_0_0_0_pseudocoup.md
sub_nodes:
    - name: sail_model_of_riscv
      path: node_0_0_0_0_0_sail_model_of_riscv/CORE_0_0_0_0_0_sail_model_of_riscv.md
    - name: map_LoOp_to_lean
      path: node_0_0_0_0_1_map_LoOp_to_lean/CORE_0_0_0_0_1_map_LoOp_to_lean.md
    - name: map_HiOp_to_unit
      path: node_0_0_0_0_2_map_HiOp_to_unit/CORE_0_0_0_0_2_map_HiOp_to_unit.md
    - name: map_unit_to_lean
      path: node_0_0_0_0_3_map_unit_to_lean/CORE_0_0_0_0_3_map_unit_to_lean.md
---

# CORE 0_0_0_0 — pseudoarch

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch
- **level:** 3
- **status:** draft
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [pseudocoup](../CORE_0_0_0_pseudocoup.md)

## sub_nodes

- [sail_model_of_riscv](node_0_0_0_0_0_sail_model_of_riscv/CORE_0_0_0_0_0_sail_model_of_riscv.md) — The RISC-V model, Sail-emitted to Lean.
- [map_LoOp_to_lean](node_0_0_0_0_1_map_LoOp_to_lean/CORE_0_0_0_0_1_map_LoOp_to_lean.md) — One Lean expression per LoOp, with nothing left body-less.
- [map_HiOp_to_unit](node_0_0_0_0_2_map_HiOp_to_unit/CORE_0_0_0_0_2_map_HiOp_to_unit.md) — A HiOp with its holders lowers to a sequence of LoOps; the context removes the chaff during the slicing; the sliced form is the Unit.
- [map_unit_to_lean](node_0_0_0_0_3_map_unit_to_lean/CORE_0_0_0_0_3_map_unit_to_lean.md) — The Unit's LoOps in order, each one's Lean from `map_LoOp_to_lean`, composed into a single term.

## definition

The system the Hub is constructed with. Three maps, and the model
they are all written against.

The chain, end to end:

    HiOp          lowers to a Unit
    Unit          is a sequence of LoOps
    LoOp          has a Lean expression, from the Sail model

So `map_HiOp_to_unit` gets the Unit, `map_LoOp_to_lean` gets each
LoOp's expression, and `map_unit_to_lean` composes them.

Built at `Projects/PseudoArch`; a sub-node of pseudocoup here, a sibling
directory on disk.

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
