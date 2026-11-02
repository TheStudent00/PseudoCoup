---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp
level: 5
status: draft
settled_by: Dee
supersedes: null
designation: code (module)
node:
    name: lower_HiOp
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_2_lower_HiOp/CORE_0_0_0_0_2_2_lower_HiOp.md
super_node:
    name: map_HiOp_to_unit
    path: ../CORE_0_0_0_0_2_map_HiOp_to_unit.md
sub_nodes:
    - name: standard_HiOp_wrapper
      path: node_0_0_0_0_2_2_0_standard_HiOp_wrapper/CORE_0_0_0_0_2_2_0_standard_HiOp_wrapper.md
    - name: compile_standard_source
      path: node_0_0_0_0_2_2_1_compile_standard_source/CORE_0_0_0_0_2_2_1_compile_standard_source.md
    - name: read_words_at_symbol
      path: node_0_0_0_0_2_2_2_read_words_at_symbol/CORE_0_0_0_0_2_2_2_read_words_at_symbol.md
    - name: extract_unit_from_LoHiOp
      path: node_0_0_0_0_2_2_3_extract_unit_from_LoHiOp/CORE_0_0_0_0_2_2_3_extract_unit_from_LoHiOp.md
---

# CORE 0_0_0_0_2_2 — lower_HiOp

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp
- **level:** 5
- **status:** draft
- **designation:** code (module)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [map_HiOp_to_unit](../CORE_0_0_0_0_2_map_HiOp_to_unit.md)

## sub_nodes

- [standard_HiOp_wrapper](node_0_0_0_0_2_2_0_standard_HiOp_wrapper/CORE_0_0_0_0_2_2_0_standard_HiOp_wrapper.md) — A parameter is a value the function owns, so a write to it is dead and the compiler deletes it — which is why `a++` lowers to a bare return and `a!` to nothing at all.
- [compile_standard_source](node_0_0_0_0_2_2_1_compile_standard_source/CORE_0_0_0_0_2_2_1_compile_standard_source.md) — The standard source becomes an object file.
- [read_words_at_symbol](node_0_0_0_0_2_2_2_read_words_at_symbol/CORE_0_0_0_0_2_2_2_read_words_at_symbol.md) — The standard function's machine words, read out of the object file as arch-opcodes: from the function's symbol, for the symbol's size, in order.
- [extract_unit_from_LoHiOp](node_0_0_0_0_2_2_3_extract_unit_from_LoHiOp/CORE_0_0_0_0_2_2_3_extract_unit_from_LoHiOp.md) — The lowered HiOp (LoHiOp) carries a prologue, an arrival, a return.

## definition

The HiOp becomes machine words. Those words ARE LoOps — the
arch-opcode and the machine-opcode are one thing in two spellings, so
nothing is mapped between them.

Refuses when the language declines the HiOp, or when no symbol reaches
the object.

The words, read as arch-opcodes at the standard function's symbol, are the
LoHiOp. The Sail model is not read here; it is read in the Lean part
(`map_LoOp_to_lean`).

*Removed 2026-10-07, at Dee's word:* two paragraphs that had each word read
back into the Sail model's constructor here, by inverting the model's
assembly clause because the Lean emit marks Sail's decoder `noncomputable`.
Dee, 2026-09-21: "the mapping between arch-opcode and machine-opcode is
1-to-1"; and 2026-10-07: "we arent at the Sail part of the project are we?"
The removed text, and the finding about sail-riscv's build that one of them
held, are kept in
`Planning/CORE_0_0_0_pseudocoup.md
§3.

Since 2026-10-11  the standard sources it lowers take their routing from the record of `HiOp_configuration_solver` (`DRY_mask_maker.ROUTING`), no longer from tables written by hand.

Support files:

- [SUPPORT_gnu_c_bit_fields_walk.py](SUPPORT_gnu_c_bit_fields_walk.py):
  what a GNU C bit-field is, and why its riscv64 words change with the
  operator and with where the result goes, in Python. PCHQ  logs 470
  and 473.

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
