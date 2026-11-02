---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.holders
level: 6
status: draft
settled_by: the owner
supersedes: null
designation: code (container)
node:
    name: holders
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_1_holders/CORE_0_0_0_0_2_1_1_holders.md
super_node:
    name: model_lang_parts
    path: ../CORE_0_0_0_0_2_1_model_lang_parts.md
sub_nodes:
    - name: holder_reader
      path: node_0_0_0_0_2_1_1_0_holder_reader/CORE_0_0_0_0_2_1_1_0_holder_reader.md
    - name: accepted_signatures
      path: node_0_0_0_0_2_1_1_1_accepted_signatures/CORE_0_0_0_0_2_1_1_1_accepted_signatures.md
    - name: equivalence_classes
      path: node_0_0_0_0_2_1_1_2_equivalence_classes/CORE_0_0_0_0_2_1_1_2_equivalence_classes.md
---

# CORE 0_0_0_0_2_1_1 — holders

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.holders
- **level:** 6
- **status:** draft
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [model_lang_parts](../CORE_0_0_0_0_2_1_model_lang_parts.md)

## sub_nodes

- [holder_reader](node_0_0_0_0_2_1_1_0_holder_reader/CORE_0_0_0_0_2_1_1_0_holder_reader.md) — Reads the built-in types a language's lowerer declares (such as Clang's `BuiltinTypes.def`) and constructs the candidate pool of primitive and derived holders (pointers, arrays, vectors, records, atomics, bit-precise integers, qualified types) to be queried by `accepted_signatures`.
- [accepted_signatures](node_0_0_0_0_2_1_1_1_accepted_signatures/CORE_0_0_0_0_2_1_1_1_accepted_signatures.md) — Queries the lowerer's own AST and IR type predicates (`type_answers(t)` and `llvm_type_answers(t)` in `accepted_signatures.py`) on every candidate holder in the language's pool (both on the outer type and on `.inner` vector/array elements and pointer pointees) to produce the precomputed `holder_facts.json` table.
- [equivalence_classes](node_0_0_0_0_2_1_1_2_equivalence_classes/CORE_0_0_0_0_2_1_1_2_equivalence_classes.md) — Partitions a language's holder pool by its `holder_facts.json` gate-predicate answers into canonical **gate-predicate equivalence class representatives** (`EQUIVALENCE_CLASS_HOLDERS` and `TYPE_ONLY_HOLDERS`).

## definition

A language's holders: the types an operand or a result is held in, such as
`int`, `double`, `int *`, `v4si`, or `struct S`. the owner, 2026-10-12 (PCHQ log
426): "`m` is the holder content and its context. every variable has an
address that can be read as an integer." So a holder is its content and its
context; its type is the content's shape.

Updated 2026-10-26: instead of guessing a hand-picked list of `52`
representatives and crossing them blindly (which left item 51 open and caused
combinatorial explosion on multi-part operators), `holders` models a
language's type pool in three steps:

1. `holder_reader` enumerates the language's built-in and derived holder
   spellings (`180` holders in GNU C covering scalars, pointers, noderef
   pointers, arrays, VLAs, GCC/ext vectors, structs, anonymous structs,
   unions, enums, atomics, `_BitInt`, and type-only slots).
2. `accepted_signatures` asks the lowerer itself how every AST and IR type
   predicate answers on each holder (`outer` and `.inner` element/pointee),
   storing the result in `holder_facts.json`.
3. `equivalence_classes` groups holders that give identical answers to the
   lowerer's gate predicates into canonical **gate-predicate equivalence
   classes** (`42` `EQUIVALENCE_CLASS_HOLDERS` + `3` `TYPE_ONLY_HOLDERS` in
   GNU C). When `branch_trees.unlock_branch` solves a gate chain, it picks
   `1` representative per surviving equivalence class—guaranteeing complete
   gate coverage (closing item 51) with zero redundant cross-product trials.
