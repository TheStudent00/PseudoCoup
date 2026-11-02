---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.holders.holder_reader
level: 7
status: draft
settled_by: Dee
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.extract_lang_vocab.holder_reader
designation: code (module)
node:
    name: holder_reader
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_1_holders/node_0_0_0_0_2_1_1_0_holder_reader/CORE_0_0_0_0_2_1_1_0_holder_reader.md
super_node:
    name: holders
    path: ../CORE_0_0_0_0_2_1_1_holders.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_1_0 — holder_reader

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.holders.holder_reader
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** Dee
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.extract_lang_vocab.holder_reader

## super_node

- [holders](../CORE_0_0_0_0_2_1_1_holders.md)

## sub_nodes

*(none yet)*

## definition

Reads the built-in types a language's lowerer declares (such as Clang's
`BuiltinTypes.def`) and constructs the candidate pool of primitive and
derived holders (pointers, arrays, vectors, records, atomics, bit-precise
integers, qualified types) to be queried by `accepted_signatures`.
