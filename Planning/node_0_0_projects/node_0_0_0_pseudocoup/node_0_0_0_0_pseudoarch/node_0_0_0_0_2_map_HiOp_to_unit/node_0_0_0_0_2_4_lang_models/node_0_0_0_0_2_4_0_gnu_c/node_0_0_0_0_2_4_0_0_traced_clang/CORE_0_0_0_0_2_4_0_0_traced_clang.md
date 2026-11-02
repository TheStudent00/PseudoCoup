---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.traced_clang
level: 7
status: draft
settled_by: Dee
supersedes: null
designation: code (module)
node:
    name: traced_clang
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/node_0_0_0_0_2_4_0_gnu_c/node_0_0_0_0_2_4_0_0_traced_clang/CORE_0_0_0_0_2_4_0_0_traced_clang.md
super_node:
    name: gnu_c
    path: ../CORE_0_0_0_0_2_4_0_gnu_c.md
sub_nodes: []
---

# CORE 0_0_0_0_2_4_0_0 — traced_clang

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.traced_clang
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [gnu_c](../CORE_0_0_0_0_2_4_0_gnu_c.md)

## sub_nodes

*(none yet)*

## definition

The instrumented Clang 21.1.8 binary (`traced_clang`) and its coverage runtime
(`path_recorder.c`), compiled with `-fsanitize-coverage=trace-pc-guard` and
`-gline-tables-only` over Clang's `Sema` and `CodeGen` translation units so
every basic block and `IRBuilder` exit executed while compiling a HiOp is
recorded in exact execution order.
