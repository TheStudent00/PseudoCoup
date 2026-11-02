---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models
level: 5
status: draft
settled_by: the owner
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.langs
designation: code (container)
node:
    name: lang_models
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/CORE_0_0_0_0_2_4_lang_models.md
super_node:
    name: map_HiOp_to_unit
    path: ../CORE_0_0_0_0_2_map_HiOp_to_unit.md
sub_nodes:
    - name: gnu_c
      path: node_0_0_0_0_2_4_0_gnu_c/CORE_0_0_0_0_2_4_0_gnu_c.md
    - name: go
      path: node_0_0_0_0_2_4_1_go/CORE_0_0_0_0_2_4_1_go.md
    - name: rust
      path: node_0_0_0_0_2_4_2_rust/CORE_0_0_0_0_2_4_2_rust.md
    - name: python
      path: node_0_0_0_0_2_4_3_python/CORE_0_0_0_0_2_4_3_python.md
    - name: java
      path: node_0_0_0_0_2_4_4_java/CORE_0_0_0_0_2_4_4_java.md
---

# CORE 0_0_0_0_2_4 — lang_models

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models
- **level:** 5
- **status:** draft
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.langs

## super_node

- [map_HiOp_to_unit](../CORE_0_0_0_0_2_map_HiOp_to_unit.md)

## sub_nodes

- [gnu_c](node_0_0_0_0_2_4_0_gnu_c/CORE_0_0_0_0_2_4_0_gnu_c.md) — GNU C's own parts of `map_HiOp_to_unit` (without `gnu_c_` prefixes on files inside this folder).
- [go](node_0_0_0_0_2_4_1_go/CORE_0_0_0_0_2_4_1_go.md) — Go's own parts of `map_HiOp_to_unit`, as `gnu_c` holds GNU C's: what Go adds to the language-agnostic machinery in `model_lang_parts`, starting with its lowerer, `cmd/compile`.
- [rust](node_0_0_0_0_2_4_2_rust/CORE_0_0_0_0_2_4_2_rust.md) — Rust's own parts of `map_HiOp_to_unit`, as `gnu_c` and `go` hold GNU C's and Go's: what Rust adds to the language-agnostic machinery in `model_lang_parts`, starting with its lowerer, `rustc`.
- [python](node_0_0_0_0_2_4_3_python/CORE_0_0_0_0_2_4_3_python.md) — Python / CPython's own parts of `map_HiOp_to_unit`, as `gnu_c`, `go`, and `rust` hold GNU C's, Go's, and Rust's: what Python adds to the language-agnostic machinery in `model_lang_parts`, starting with its lowerer, CPython 3.13.
- [java](node_0_0_0_0_2_4_4_java/CORE_0_0_0_0_2_4_4_java.md) — Java's own parts of `map_HiOp_to_unit`, as `gnu_c`, `go`, `rust`, and `python` hold GNU C's, Go's, Rust's, and Python's: what Java adds to the language-agnostic machinery in `model_lang_parts`, starting with its lowerer, `javac` 25.0.4.1 and HotSpot JVM.

## definition

One sub-node per language, each holding what that language adds to the
language-agnostic machinery in `model_lang_parts`: its lowerer's instrumented
runner, its lowerer's gate-predicate and `derived_info` tables, its
pre-queried `holder_facts.json` and canonical `EQUIVALENCE_CLASS_HOLDERS`,
its standard-form source templates, and its solved model records
(`unreached_paths.json`, `paths.json`, `lines.json`, `trees/`).

A file inside a language's folder carries no language prefix (`unreached_paths.json`,
`holder_facts.json`, `gate_tables.py`, `templates.py`): the parent folder
(`lang_models/gnu_c/`, `lang_models/go/`, etc.) identifies the language.

- the owner, 2026-10-14: "something we absolutely do need is a node to hold
  language specific stuff if we dont already have it. that way we wouldnt
  have to label everything with a language specifier since the container
  folder would clarify it."
- the owner, 2026-10-15: renamed `langs` to `lang_models` in `map_HiOp_to_unit`'s
  redrawn ontology (`SUPPORT_settling_the_ontology.md`).

### How Additional Languages Plug Into `lang_models/<lang>`

1. **Other C-Family Dialects and C++ (`c89`, `c99`, `c23`, `cpp`, `objc`, `opencl`):**
   Because 90%+ of Clang's `Sema*` and `CG*` C++ functions are shared across
   all Clang-lowered languages and their `BranchTree`s are already parsed,
   adding another C standard only changes the compile standard flag in `setup`,
   and adding C++ moves C++ predicates (`isReferenceType`, `isMemberPointerType`,
   `CXXRecordDecl`) from `LANGUAGE_NAMES` into active gate tables and adds
   C++-specific equivalence-class holders.
2. **Other Compiled Languages (`go`, `rust`, `fortran`, `zig`):**
   Each language plugs in its own instrumented compiler trace (`trace`), its
   compiler's AST type-predicate table (`gate_tables`), its pre-queried
   `holder_facts.json` + `equivalence_classes`, and its wrapper `templates`,
   while `model_lang_parts` (`branch_trees`, `unlock_branch`,
   `enumerate_branch_candidates`, `enumerate_paths`, `find_unreached_paths`)
   runs unchanged.
