---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts
level: 5
status: draft
settled_by: the owner
supersedes: null
designation: code (container)
node:
    name: model_lang_parts
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/CORE_0_0_0_0_2_1_model_lang_parts.md
super_node:
    name: map_HiOp_to_unit
    path: ../CORE_0_0_0_0_2_map_HiOp_to_unit.md
sub_nodes:
    - name: HiOps
      path: node_0_0_0_0_2_1_0_HiOps/CORE_0_0_0_0_2_1_0_HiOps.md
    - name: holders
      path: node_0_0_0_0_2_1_1_holders/CORE_0_0_0_0_2_1_1_holders.md
    - name: infra
      path: node_0_0_0_0_2_1_2_infra/CORE_0_0_0_0_2_1_2_infra.md
    - name: context
      path: node_0_0_0_0_2_1_3_context/CORE_0_0_0_0_2_1_3_context.md
    - name: HiOp_complexities
      path: node_0_0_0_0_2_1_4_HiOp_complexities/CORE_0_0_0_0_2_1_4_HiOp_complexities.md
    - name: HiOp_configurations
      path: node_0_0_0_0_2_1_5_HiOp_configurations/CORE_0_0_0_0_2_1_5_HiOp_configurations.md
---

# CORE 0_0_0_0_2_1 — model_lang_parts

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts
- **level:** 5
- **status:** draft
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [map_HiOp_to_unit](../CORE_0_0_0_0_2_map_HiOp_to_unit.md)

## sub_nodes

- [HiOps](node_0_0_0_0_2_1_0_HiOps/CORE_0_0_0_0_2_1_0_HiOps.md) — A language's HiOps: its operators, each with the holders its lowerer accepts with it and the deterministic `(entry, exit)` paths its lowerer takes.
- [holders](node_0_0_0_0_2_1_1_holders/CORE_0_0_0_0_2_1_1_holders.md) — A language's holders: the types an operand or a result is held in, such as `int`, `double`, `int *`, `v4si`, or `struct S`.
- [infra](node_0_0_0_0_2_1_2_infra/CORE_0_0_0_0_2_1_2_infra.md) — The infrastructure a language's Units call: code outside the HiOps that a Unit calls into.
- [context](node_0_0_0_0_2_1_3_context/CORE_0_0_0_0_2_1_3_context.md) — The contexts a holder or HiOp can be in, both at entry into the lowerer (`entry_context`: `entry_info` / `state_info[0]`) and in how each place modifies a lowered Unit (`model_contexts`): the lowerer's logic for a place, modelled once and applied the same way to every HiOp.
- [HiOp_complexities](node_0_0_0_0_2_1_4_HiOp_complexities/CORE_0_0_0_0_2_1_4_HiOp_complexities.md) — How complex each HiOp is, read from the operator's definition and in-HiOp `BranchTree` in its lowerer's own code along two orthogonal axes.
- [HiOp_configurations](node_0_0_0_0_2_1_5_HiOp_configurations/CORE_0_0_0_0_2_1_5_HiOp_configurations.md) — The syntactic and structural pattern each HiOp is held in.

## definition

Each part of a language, read from its lowerer and modelled by
language-agnostic machinery: its HiOps, its holders, the infrastructure its
Units call, the contexts that change what a HiOp does, how complex each HiOp
is, and each HiOp's configuration.

the owner's sketch, 2026-10-15, named this node `model_lang_components`; then:
"i might change components for parts. `model_lang_parts`. shorter, same
info."

### The 4 Language-Agnostic Pillars of `model_lang_parts`

Updated 2026-10-26 after runs `riscv64-runner_l20..l22` and `find_unreached_paths`
achieved **100% completion across all `1,806` GNU C operators (`0` open
branches / `0` unreached paths left)**. The machinery in `model_lang_parts`
solves vocabulary extraction and HiOp modelling for all C-family languages
(C89, C99, C11, C17, C23, GNU C, C++, Objective-C, OpenCL) and other compiled
languages (Go, Rust, Fortran, Zig, etc.) in principle because it relies on
four invariants that hold in every compiler:

1. **The Lowerer's Promise (`entry_info` `state_info[0]` -> Deterministic Path to Lowering or Refusal):**
   Every compiler accepts an entry `Context` (`state_info[0]`: operator syntax,
   operand holder types, value forms `0..5`, compile options, target) and
   either lowers it along a deterministic path to IR/machine instructions or
   refuses it along a diagnostic path. Any in-HiOp local variable tested along
   that path (`derived_info` / `state_info[n]`) is a deterministic function of
   `state_info[0]`.
2. **Finite In-HiOp Control-Flow Trees (`BranchTree`, Calls Not Followed):**
   Every compiler is written in a structured implementation language that
   `tree-sitter` parses into `if` / `else` / `switch` / `case` / `?:` / `&&` /
   `||` branch trees (`HiOps/branch_trees`). Restricting analysis to **code
   within the HiOp's own functions (`--in-hiop`, calls not followed)** keeps
   every operator's branch tree finite and shallow (`depth 0` with `0` internal
   branches, or `depth 1+` with a small tree of type/option gates).
3. **Finite Gate-Predicate Equivalence Classes (`holders/accepted_signatures` + `holders/equivalence_classes`):**
   No compiler branches on millions of concrete types; every compiler gates its
   lowering on a finite set of type-category predicates (e.g. `isIntegerType()`,
   `isFloatingType()`, `isVectorType()`, `isPointerType()` in Clang;
   `t.IsInteger()`, `t.IsFloat()`, `t.IsSlice()`, `t.IsInterface()` in Go's
   `cmd/compile`). Pre-querying the compiler's type predicates on a candidate
   holder pool (`accepted_signatures`) partitions all holders into a small set
   of **canonical gate-predicate equivalence classes** (`42` representatives +
   `3` type-slot holders in GNU C), eliminating combinatorial explosion and
   closing item 51 (`holders never tried`).
4. **Closed-Loop Forward Trace + In-HiOp Gate Unlocking (`enumerate_branch_candidates` + `find_unreached_paths`):**
   An instrumented lowerer records the exact lines/basic blocks executed inside
   the HiOp's functions. `find_unreached_paths` compares all traced paths
   against the lowerer's `BranchTree`s to produce `unreached_paths`, and
   `unlock_branch` intersects the gate predicates along each untaken chain to
   emit `1` candidate per surviving equivalence class until `open == 0`.

### the owner's Downstream Unit-Modelling Order

Once all HiOp variants and their deterministic `(entry, exit)` paths are
enumerated (`open == 0`), downstream Unit slicing and composition follow
the owner's complexity order (the owner, 2026-10-12, 
simple HiOps, then model hybrid HiOps, then model complex HiOps. because each
preceding stage helps us model the next -- with complex being essentially
free"):

```python
def model_HiOps(simple_HiOps, hybrid_HiOps, complex_HiOps, contexts):
	simple_Units = model_simple(simple_HiOps, contexts)	# 1
	hybrid_Units = model_hybrid(hybrid_HiOps, simple_Units)	# 2
	complex_Units = compose_complex(complex_HiOps, simple_Units, hybrid_Units)	# 3
	Units = simple_Units + hybrid_Units + complex_Units
	return Units
```
