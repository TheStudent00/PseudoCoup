---
id: hq.projects.pseudocoup.pseudoarch.sail_model_of_riscv
level: 4
status: draft
settled_by: the owner
supersedes: null
designation: code (container)
node:
    name: sail_model_of_riscv
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_0_sail_model_of_riscv/CORE_0_0_0_0_0_sail_model_of_riscv.md
super_node:
    name: pseudoarch
    path: ../CORE_0_0_0_0_pseudoarch.md
sub_nodes: []
---

# CORE 0_0_0_0_0 — sail_model_of_riscv

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.sail_model_of_riscv
- **level:** 4
- **status:** draft
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [pseudoarch](../CORE_0_0_0_0_pseudoarch.md)

## sub_nodes

*(none yet)*

## definition

The RISC-V model, Sail-emitted to Lean. Every LoOp's definition
comes from here, and so does the spelling of every assembly clause.

Two subtrees read it, which is why it is its own node rather than one
of `map_LoOp_to_lean`'s: that map reads its execute clauses, and
`lower_HiOp` reads its assembly clauses to name a carved word.

It is the only node in the tree that is not ours to change.

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
