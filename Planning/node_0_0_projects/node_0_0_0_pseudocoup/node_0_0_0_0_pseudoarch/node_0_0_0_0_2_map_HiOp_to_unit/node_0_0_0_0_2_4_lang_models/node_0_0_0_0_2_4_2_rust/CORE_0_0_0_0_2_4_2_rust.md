---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.rust
level: 6
status: draft
settled_by: the owner
supersedes: null
designation: code (container)
node:
    name: rust
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/node_0_0_0_0_2_4_2_rust/CORE_0_0_0_0_2_4_2_rust.md
super_node:
    name: lang_models
    path: ../CORE_0_0_0_0_2_4_lang_models.md
sub_nodes: []
---

# CORE 0_0_0_0_2_4_2 — rust

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.rust
- **level:** 6
- **status:** draft
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [lang_models](../CORE_0_0_0_0_2_4_lang_models.md)

## sub_nodes

*(none yet)*

## definition

Rust's own parts of `map_HiOp_to_unit`, as `gnu_c` and `go` hold GNU C's and Go's: what
Rust adds to the language-agnostic machinery in `model_lang_parts`, starting with
its lowerer, `rustc`.

With GNU C and Go modelled, Rust plugs into the exact same 4-pillar `model_lang_parts`
pipeline (`BranchTree`s over `compiler/rustc_hir_typeck`, `compiler/rustc_mir_build`,
and `compiler/rustc_codegen_ssa` with calls not followed; gate-predicate equivalence
classes over Rust type-system traits and primitive type predicates; native riscv64
lowering via `rustc --target riscv64gc-unknown-linux-gnu -C opt-level=0 -C debuginfo=2 -C overflow-checks=off`;
and `find_unreached_paths` -> `lang_models/rust/unreached_paths.json`).
