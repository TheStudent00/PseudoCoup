---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.dict_of_lang_HiOps
level: 5
status: draft
settled_by: the owner
supersedes: null
designation: code (module)
node:
    name: dict_of_lang_HiOps
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_0_dict_of_lang_HiOps/CORE_0_0_0_0_2_0_dict_of_lang_HiOps.md
super_node:
    name: map_HiOp_to_unit
    path: ../CORE_0_0_0_0_2_map_HiOp_to_unit.md
sub_nodes: []
---

# CORE 0_0_0_0_2_0 — dict_of_lang_HiOps

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.dict_of_lang_HiOps
- **level:** 5
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [map_HiOp_to_unit](../CORE_0_0_0_0_2_map_HiOp_to_unit.md)

## sub_nodes

*(none yet)*

## definition

Per language, every HiOp: an operator with the holder types it is applied
to. One entry per variant.

## the dict is derived from the language, never hand-written

Settled 2026-09-23; corrected 2026-09-28. Every one of the twelve languages
declares its operators and its holders in its lowerer's own source. (A
lowerer is a language's map from its HiOps to arch-units: in practice its
compiler or interpreter.)
`extract_lang_vocabulary` reads the two lists, crosses them, and keeps the
cells the lowerer accepts; those cells are the dict's entries. A grid we
write ourselves is never a source.

Eight languages also write some pairings down as data: java, dart, rust,
swift, ruby, csharp, go, and php for long and double. Those are an ORACLE
for the lowerer's verdict. Four keep their pairings only as code: c, cpp,
python, javascript. For them the lowerer's verdict is the only record, and
nothing is missing.

The position that fell, 2026-09-28: "eleven of twelve declare the grid; c
and cpp are the outlier", with five shapes of declaration. It rested on
readers of ours that had not looked far enough: ruby's signatures, python's
source and php's conversion switch were missed, and javascript was not
looked at. The five shapes are kept with the superseded readers in
`extract_lang_vocabulary/.archive/five_readers_superseded_2026-09-28/`.

Every citation is in
[SUPPORT_declared_vocabularies.md](SUPPORT_declared_vocabularies.md).

## a holder is identified by what it lowers to, never by its spelling

the owner, 2026-09-27: "we are lowering things into RISC-V. if theyre the same type,
theyre provably so. why would we hand-write a normalizer when normalization can
be done by automation?"

Whether go's `int64` and rust's `i64` are one holder is not looked up in a
table of names. It is read off what each lowers to, and it is a proof.

## support

- [SUPPORT_declared_vocabularies.md](SUPPORT_declared_vocabularies.md) —
  where each language's lowerer declares its operators, its holders, and
  the pairings it writes down as data, file by file

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
- lowerer is a language's compiler or interpreter: what lowers a HiOp to a Unit
