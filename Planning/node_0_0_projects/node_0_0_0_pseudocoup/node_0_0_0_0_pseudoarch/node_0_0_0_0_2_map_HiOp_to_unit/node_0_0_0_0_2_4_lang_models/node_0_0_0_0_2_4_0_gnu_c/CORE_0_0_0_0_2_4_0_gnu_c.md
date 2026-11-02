---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c
level: 6
status: draft
settled_by: the owner
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.langs.gnu_c
designation: code (container)
node:
    name: gnu_c
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/node_0_0_0_0_2_4_0_gnu_c/CORE_0_0_0_0_2_4_0_gnu_c.md
super_node:
    name: lang_models
    path: ../CORE_0_0_0_0_2_4_lang_models.md
sub_nodes:
    - name: traced_clang
      path: node_0_0_0_0_2_4_0_0_traced_clang/CORE_0_0_0_0_2_4_0_0_traced_clang.md
    - name: trace
      path: node_0_0_0_0_2_4_0_1_trace/CORE_0_0_0_0_2_4_0_1_trace.md
    - name: gate_tables
      path: node_0_0_0_0_2_4_0_2_gate_tables/CORE_0_0_0_0_2_4_0_2_gate_tables.md
    - name: equivalence_classes
      path: node_0_0_0_0_2_4_0_3_equivalence_classes/CORE_0_0_0_0_2_4_0_3_equivalence_classes.md
    - name: templates
      path: node_0_0_0_0_2_4_0_4_templates/CORE_0_0_0_0_2_4_0_4_templates.md
    - name: unreached_paths
      path: node_0_0_0_0_2_4_0_5_unreached_paths/CORE_0_0_0_0_2_4_0_5_unreached_paths.md
---

# CORE 0_0_0_0_2_4_0 — gnu_c

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c
- **level:** 6
- **status:** draft
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.langs.gnu_c

## super_node

- [lang_models](../CORE_0_0_0_0_2_4_lang_models.md)

## sub_nodes

- [traced_clang](node_0_0_0_0_2_4_0_0_traced_clang/CORE_0_0_0_0_2_4_0_0_traced_clang.md) — The instrumented Clang 21.1.8 binary (`traced_clang`) and its coverage runtime (`path_recorder.c`), compiled with `-fsanitize-coverage=trace-pc-guard` and `-gline-tables-only` over Clang's `Sema` and `CodeGen` translation units so every basic block and `IRBuilder` exit executed while compiling a HiOp is recorded in exact execution order.
- [trace](node_0_0_0_0_2_4_0_1_trace/CORE_0_0_0_0_2_4_0_1_trace.md) — Runs `traced_clang` on a wrapped C candidate (`trace.py`, `trace_once.py`, `logical_path.py`, `lines_run.py`), cuts the raw PC-guard trace at the standard-form entry/exit markers, filters executed lines to the HiOp's own Clang C++ functions (`--in-hiop`), and extracts the `checking_action`, `lowering_mark`, executed source lines (`lines_run`), and emitted LLVM IR instructions (`ir`, `ir_typed`, `exits`).
- [gate_tables](node_0_0_0_0_2_4_0_2_gate_tables/CORE_0_0_0_0_2_4_0_2_gate_tables.md) — Clang's C++ AST/LLVM gate-predicate and `derived_info` (`state_info[n]`) lookup tables (`gate_tables.py`).
- [equivalence_classes](node_0_0_0_0_2_4_0_3_equivalence_classes/CORE_0_0_0_0_2_4_0_3_equivalence_classes.md) — GNU C's pre-queried holder facts and canonical gate-predicate equivalence class representatives.
- [templates](node_0_0_0_0_2_4_0_4_templates/CORE_0_0_0_0_2_4_0_4_templates.md) — GNU C's standard-form C program wrapper templates (`operators_of(key)` and `operator_candidates` in `templates.py`).
- [unreached_paths](node_0_0_0_0_2_4_0_5_unreached_paths/CORE_0_0_0_0_2_4_0_5_unreached_paths.md) — The data structure and solved model records (`unreached_paths.json`, replacing the research filename `what_is_left.json`, together with `paths.json`, `lines.json`, `branch_candidates.json`, `trees/`, and `SUPPORT_*` pages) produced for GNU C by `model_lang_parts/HiOps/find_unreached_paths`.

## definition

GNU C's own parts of `map_HiOp_to_unit` (without `gnu_c_` prefixes on files
inside this folder). GNU C's lowerer is Clang 21.1.8 compiling with
`-std=gnu17`.

Updated 2026-10-26: holds the 6 language-specific components that plug into
`model_lang_parts` (`traced_clang`, `trace`, `gate_tables`,
`equivalence_classes`, `templates`, and `unreached_paths`) and the complete
100%-solved GNU C vocabulary model (`1,806` operators: `1,343` solved with
every in-HiOp branch taken or proven `not needed`/`cannot reach`, `458`
proven refused on target, `5` untraceable pseudo-constructs; `1,376 / 1,376`
accepted in-HiOp keys at `0` open branches; `0` distinct open branches left
in `unreached_paths.json`).

## support

- [SUPPORT_gnu_c_operators_breakdown.html](SUPPORT_gnu_c_operators_breakdown.html): GNU C's operators as Clang 21.1.8 names them for riscv64, sorted into simple, complex, and no operation of their own.
- [SUPPORT_gnu_c_simple_hiops_state.html](SUPPORT_gnu_c_simple_hiops_state.html): GNU C's simple HiOps split by where each operator's holders came from before the in-HiOp branch-tree rework.
- [SUPPORT_gnu_c_operators_sorted_by_clangs_code.html](SUPPORT_gnu_c_operators_sorted_by_clangs_code.html): GNU C's operators sorted mechanically by their definitions in Clang's lowering code (`HiOp_sorter`).
- [SUPPORT_gnu_c_operators_by_what_clang_writes.html](SUPPORT_gnu_c_operators_by_what_clang_writes.html): Sunburst of what Clang writes for each GNU C operator at `-O0`.
- [SUPPORT_gnu_c_vocab_what_is_missing.md](SUPPORT_gnu_c_vocab_what_is_missing.md): Record of GNU C vocabulary gaps tracked during extraction (all `1,806` GNU C operators now settled with `0` open branches in `unreached_paths`).
