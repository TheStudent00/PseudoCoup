---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps.operator_reader
level: 7
status: draft
settled_by: Dee
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.extract_lang_vocab.operator_reader
designation: code (module)
node:
    name: operator_reader
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_0_HiOps/node_0_0_0_0_2_1_0_0_operator_reader/CORE_0_0_0_0_2_1_0_0_operator_reader.md
super_node:
    name: HiOps
    path: ../CORE_0_0_0_0_2_1_0_HiOps.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_0_0 — operator_reader

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps.operator_reader
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** Dee
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.extract_lang_vocab.operator_reader

## super_node

- [HiOps](../CORE_0_0_0_0_2_1_0_HiOps.md)

## sub_nodes

*(none yet)*

## definition

Reads the complete list of operators (expressions, statements, builtins, and
library calls, each keyed by its AST kind and part count) directly from a
language's lowerer tables.

For GNU C (`lang_models/gnu_c`), `operator_reader` reads Clang 21.1.8's
statement, expression, and builtin tables (`StmtNodes.td`, `BuiltinNames.def`,
`OperatorKinds.def`), yielding the `1,806` GNU C operators (`357` expressions,
`1,421` builtins and library calls, `28` statements).
