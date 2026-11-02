---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.trace
level: 7
status: draft
settled_by: the owner
supersedes: null
designation: code (module)
node:
    name: trace
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/node_0_0_0_0_2_4_0_gnu_c/node_0_0_0_0_2_4_0_1_trace/CORE_0_0_0_0_2_4_0_1_trace.md
super_node:
    name: gnu_c
    path: ../CORE_0_0_0_0_2_4_0_gnu_c.md
sub_nodes: []
---

# CORE 0_0_0_0_2_4_0_1 — trace

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.trace
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [gnu_c](../CORE_0_0_0_0_2_4_0_gnu_c.md)

## sub_nodes

*(none yet)*

## definition

Runs `traced_clang` on a wrapped C candidate (`trace.py`, `trace_once.py`,
`logical_path.py`, `lines_run.py`), cuts the raw PC-guard trace at the
standard-form entry/exit markers, filters executed lines to the HiOp's own
Clang C++ functions (`--in-hiop`), and extracts the `checking_action`,
`lowering_mark`, executed source lines (`lines_run`), and emitted LLVM IR
instructions (`ir`, `ir_typed`, `exits`).
