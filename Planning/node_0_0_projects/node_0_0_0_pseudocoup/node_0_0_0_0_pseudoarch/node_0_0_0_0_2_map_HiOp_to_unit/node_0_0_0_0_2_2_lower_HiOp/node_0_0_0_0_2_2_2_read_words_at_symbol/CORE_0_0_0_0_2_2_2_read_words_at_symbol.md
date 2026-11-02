---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.read_words_at_symbol
level: 6
status: draft
settled_by: the owner
supersedes: null
designation: code (function)
node:
    name: read_words_at_symbol
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_2_lower_HiOp/node_0_0_0_0_2_2_2_read_words_at_symbol/CORE_0_0_0_0_2_2_2_read_words_at_symbol.md
super_node:
    name: lower_HiOp
    path: ../CORE_0_0_0_0_2_2_lower_HiOp.md
sub_nodes: []
---

# CORE 0_0_0_0_2_2_2 — read_words_at_symbol

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.read_words_at_symbol
- **level:** 6
- **status:** draft
- **designation:** code (function)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [lower_HiOp](../CORE_0_0_0_0_2_2_lower_HiOp.md)

## sub_nodes

*(none yet)*

## definition

The standard function's machine words, read out of the object file as
arch-opcodes: from the function's symbol, for the symbol's size, in order.
That list is the LoHiOp. Each word comes with:

- its arch-opcode and operands, in the architecture's own names
  (`addw a0, a0, a2`), never an assembler shorthand that stands for one
  (`ret` stands for `jalr zero, 0(ra)`);
- its bytes (2 or 4 on our target) and its address;
- any relocation on it: the name a call or an address refers to, which the
  object leaves to be filled in when the program is linked.

A machine word and its arch-opcode are one thing in two forms
(`lower_HiOp`'s definition), so reading one as the other maps nothing.

Refuses when the symbol is not in the object (`lower_HiOp`'s second
refusal: "no symbol reaches the object").

The words are read as the target the compile used, never as a list of
extensions written by hand.

The symbol is the standard function's name, which `standard_HiOp_wrapper` hands on
with the source.

Written 2026-10-07 by Claude (Opus 5.5), at the owner's word ("yes as long as it
makes sense for the current context of the project"), from `lower_HiOp`'s
own definition. Changed later the same day, at the owner's word: its words, read
as arch-opcodes, are the LoHiOp
(`Planning/CORE_0_0_0_pseudocoup.md). The wording is mine (`Planning/CORE_0_0_0_pseudocoup.md).

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
