---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.extract_unit_from_LoHiOp
level: 6
status: draft
settled_by: the owner
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.extract_unit_from_LoHiOp
designation: code (module)
node:
    name: extract_unit_from_LoHiOp
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_2_lower_HiOp/node_0_0_0_0_2_2_3_extract_unit_from_LoHiOp/CORE_0_0_0_0_2_2_3_extract_unit_from_LoHiOp.md
super_node:
    name: lower_HiOp
    path: ../CORE_0_0_0_0_2_2_lower_HiOp.md
sub_nodes: []
---

# CORE 0_0_0_0_2_2_3 — extract_unit_from_LoHiOp

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.extract_unit_from_LoHiOp
- **level:** 6
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.extract_unit_from_LoHiOp

## super_node

- [lower_HiOp](../CORE_0_0_0_0_2_2_lower_HiOp.md)

## sub_nodes

*(none yet)*

## definition

The lowered HiOp (LoHiOp) carries a prologue, an arrival, a return.
None of that is the HiOp. What is left once the context is pinned and
the chaff removed is the Unit.

The held wrapper makes this node load-bearing rather than tidy: held
adds a uniform arrival, and this is what takes it back off.

*notes:*

- The cut, at the owner's word of 2026-10-12 (`Planning/CORE_0_0_0_pseudocoup.md
  the owner: "if the answer being yes reduces work, i dont see why we
  wouldnt"): the Unit keeps the words that fetch its holders' values, the
  operation, and the word that stores its result; the frame (prologue and return) and the copy of `p` (the
  arrival) are cut. The question was mine (log 437 §2); the yes is the owner's.
- How the Unit's words are told. the owner, 2026-10-13 (`Planning/CORE_0_0_0_pseudocoup.md):
  "we need some way to tell which arch-opcodes belong to the lowered HiOp. is
  that not enough to settle this particular issue?" My answer, the means: the
  debug table that `-g` writes names the source line of each word, so the Unit
  is the words under the HiOp's line, with the HiOp on a line of its own in
  the standard source. Nothing has to know what a frame is. A part's call is
  still known by its relocation (log 406). Built 2026-10-13
  (`Projects/PseudoArch/map_HiOp_to_unit/extract_unit_from_LoHiOp.py`) and run
  over every GNU C HiOp on all three machines (run elv2_l156, .
  The line alone kept clang's loads of `p` (the standard function's parameter,
  the address of the holders' struct), which this note's first point puts
  out; since log 453 each one leaves the Unit's words and its place is kept,
  "from here, this register holds `p`".
- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
