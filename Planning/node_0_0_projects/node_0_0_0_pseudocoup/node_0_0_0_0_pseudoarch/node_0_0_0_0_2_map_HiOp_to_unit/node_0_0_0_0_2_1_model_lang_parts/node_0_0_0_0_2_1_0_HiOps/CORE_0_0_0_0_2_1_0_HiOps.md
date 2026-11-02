---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps
level: 6
status: draft
settled_by: Dee
supersedes: null
designation: code (container)
node:
    name: HiOps
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_0_HiOps/CORE_0_0_0_0_2_1_0_HiOps.md
super_node:
    name: model_lang_parts
    path: ../CORE_0_0_0_0_2_1_model_lang_parts.md
sub_nodes:
    - name: operator_reader
      path: node_0_0_0_0_2_1_0_0_operator_reader/CORE_0_0_0_0_2_1_0_0_operator_reader.md
    - name: branch_trees
      path: node_0_0_0_0_2_1_0_1_branch_trees/CORE_0_0_0_0_2_1_0_1_branch_trees.md
    - name: enumerate_branch_candidates
      path: node_0_0_0_0_2_1_0_2_enumerate_branch_candidates/CORE_0_0_0_0_2_1_0_2_enumerate_branch_candidates.md
    - name: enumerate_paths
      path: node_0_0_0_0_2_1_0_3_enumerate_paths/CORE_0_0_0_0_2_1_0_3_enumerate_paths.md
    - name: find_unreached_paths
      path: node_0_0_0_0_2_1_0_4_find_unreached_paths/CORE_0_0_0_0_2_1_0_4_find_unreached_paths.md
---

# CORE 0_0_0_0_2_1_0 — HiOps

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps
- **level:** 6
- **status:** draft
- **designation:** code (container)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [model_lang_parts](../CORE_0_0_0_0_2_1_model_lang_parts.md)

## sub_nodes

- [operator_reader](node_0_0_0_0_2_1_0_0_operator_reader/CORE_0_0_0_0_2_1_0_0_operator_reader.md) — Reads the complete list of operators (expressions, statements, builtins, and library calls, each keyed by its AST kind and part count) directly from a language's lowerer tables.
- [branch_trees](node_0_0_0_0_2_1_0_1_branch_trees/CORE_0_0_0_0_2_1_0_1_branch_trees.md) — The language-agnostic in-HiOp control-flow tree builder and gate-chain solver (`branch_trees.py`: `BranchTree`, `tree_of_function`, `super_chain_of_branch`, `PartConstraint`, `AbstractConstraint`, `CandidateWriter`, `unlock_branch`).
- [enumerate_branch_candidates](node_0_0_0_0_2_1_0_2_enumerate_branch_candidates/CORE_0_0_0_0_2_1_0_2_enumerate_branch_candidates.md) — The closed-loop in-HiOp candidate driver and branch classifier (`enumerate_branch_candidates.py`: `UnreachedBranch`, `BranchCondition`, `VariantCandidate`, `Record`, `classify_branches`, `enumerate_every_path`).
- [enumerate_paths](node_0_0_0_0_2_1_0_3_enumerate_paths/CORE_0_0_0_0_2_1_0_3_enumerate_paths.md) — Groups all accepted traced runs of each operator into distinct deterministic `(entry, exit)` lowering paths (`paths.json`), where each distinct path defines a HiOp variant and records its checking action, lowering mark, inner basic-block sequence, emitted IR instructions (`ir`, `ir_typed`, `exits`), and the equivalence-class holder tuples that take that path.
- [find_unreached_paths](node_0_0_0_0_2_1_0_4_find_unreached_paths/CORE_0_0_0_0_2_1_0_4_find_unreached_paths.md) — The whole-vocabulary completeness verifier (`find_unreached_paths.py`, replacing the research script `what_is_left_for_each_hiop.py`; named without `_HiOp_` because its parent container node is already `HiOps`).

## definition

A language's HiOps: its operators, each with the holders its lowerer
accepts with it and the deterministic `(entry, exit)` paths its lowerer
takes. One HiOp variant per distinct accepted lowering path, filed under
the operator as the program writes it; its holders and `entry_info`
(`state_info[0]`) are context that selects the path and modifies its
meaning. Dee, 2026-10-15 : "those signatures look like HiOp
variants with context that modifies their meanings."

Updated 2026-10-26: the earlier brute-force grid (`extract()`) and static
cross-function walker (`complex_signature_reader`) are replaced by the
5-module language-agnostic pipeline:

1. `operator_reader` reads the operator list declared by the lowerer.
2. `branch_trees` builds the finite in-HiOp `BranchTree` (calls not followed,
   only code within the HiOp's own checking and lowering functions) and
   solves untaken gate chains via `unlock_branch` using canonical
   gate-predicate equivalence classes and `derived_info` (`state_info[n]`).
3. `enumerate_branch_candidates` runs the closed-loop trace-and-unlock cycle
   until every in-HiOp branch is `taken`, `not needed`, or `cannot reach`
   (`open == 0`).
4. `enumerate_paths` groups all accepted runs into distinct `(entry, exit)`
   lowering paths.
5. `find_unreached_paths` (named without `_HiOp_` because its parent node is
   already `HiOps`) audits the entire vocabulary against the lowerer's
   `BranchTree`s and writes `unreached_paths` (`unreached_paths.json` under
   `lang_models/<lang>`).

All three faults inherited from the legacy grid (`SUPPORT_gnu_c_vocab_what_is_missing.md`
items 47, 51, and 52) are closed by this pipeline:

- **Item 47 closed:** builtins that lower at another width or via an inline
  IR path are traced through their exact `CGBuiltin.cpp` path and kept.
- **Item 51 closed:** `42` canonical gate-predicate equivalence classes cover
  every gate-distinct holder category (including pointers to `short`/`char`/`void`/functions/noderef, vectors of every element kind, `_BitInt`, `_Atomic`, `_Float16`, anonymous structs, etc.).
- **Item 52 closed:** every refused or non-GNU-C operator and branch is
  explicitly classified and recorded in `unreached_paths.json` (`458` refused
  operators: `413` at depth 0 + `45` at depth 1+; `0` open branches left).
