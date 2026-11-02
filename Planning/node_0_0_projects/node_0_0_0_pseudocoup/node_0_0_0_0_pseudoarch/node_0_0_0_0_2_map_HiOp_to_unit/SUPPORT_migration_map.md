---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.migration_map
status: draft
migration:
    - from: dict_of_lang_HiOps
      to: dict_of_lang_HiOps
    - from: new
      to: model_lang_parts
    - from: new
      to: model_lang_parts/HiOps
    - from: extract_lang_vocab/operator_reader
      to: model_lang_parts/HiOps/operator_reader
    - from: new
      to: model_lang_parts/HiOps/branch_trees
    - from: new
      to: model_lang_parts/HiOps/enumerate_branch_candidates
    - from: new
      to: model_lang_parts/HiOps/enumerate_paths
    - from: new
      to: model_lang_parts/HiOps/find_unreached_paths
    - from: complex_signature_reader
      to: deleted
    - from: new
      to: model_lang_parts/holders
    - from: extract_lang_vocab/holder_reader
      to: model_lang_parts/holders/holder_reader
    - from: complex_signature_reader/accepted_signatures
      to: model_lang_parts/holders/accepted_signatures
    - from: new
      to: model_lang_parts/holders/equivalence_classes
    - from: new
      to: model_lang_parts/infra
    - from: new
      to: model_lang_parts/context
    - from: new
      to: model_lang_parts/context/entry_context
    - from: model_HiOps/model_contexts
      to: model_lang_parts/context/model_contexts
    - from: new
      to: model_lang_parts/HiOp_complexities
    - from: model_HiOps/HiOp_sorter
      to: model_lang_parts/HiOp_complexities/HiOp_sorter
    - from: new
      to: model_lang_parts/HiOp_configurations
    - from: extract_lang_vocab/dependent_HiOp_reader
      to: model_lang_parts/HiOp_configurations/dependent_HiOp_reader
    - from: extract_lang_vocab/HiOp_configuration_solver
      to: model_lang_parts/HiOp_configurations/HiOp_configuration_solver
    - from: extract_lang_vocab
      to: deleted
    - from: model_HiOps
      to: deleted
    - from: lower_HiOp
      to: lower_HiOp
    - from: standard_HiOp_wrapper
      to: lower_HiOp/standard_HiOp_wrapper
    - from: extract_unit_from_LoHiOp
      to: lower_HiOp/extract_unit_from_LoHiOp
    - from: DRY_mask_maker
      to: mask_maker
    - from: langs
      to: lang_models
    - from: langs/gnu_c
      to: lang_models/gnu_c
    - from: new
      to: lang_models/gnu_c/traced_clang
    - from: new
      to: lang_models/gnu_c/trace
    - from: new
      to: lang_models/gnu_c/gate_tables
    - from: new
      to: lang_models/gnu_c/equivalence_classes
    - from: new
      to: lang_models/gnu_c/templates
    - from: new
      to: lang_models/gnu_c/unreached_paths
    - from: new
      to: lang_models/go
---

# SUPPORT — migration_map

The record of `map_HiOp_to_unit`'s rework, by PlanPlan's
`framework/PROTOCOL.md` §6d. Opened 2026-10-15 at Dee's word ("please fill
in the .NASCENT for `map_HiOps_to_unit` as best you can") and updated
2026-10-26 to incorporate the winning 100%-complete in-HiOp branch-tree and
gate-predicate equivalence-class toolset (`Research/trace_logical_paths_clone/`,
runs `riscv64-runner_l20..l22`, `0` unreached paths left across all `1,806` GNU C HiOps)
and the refined ontological naming (`find_unreached_paths` system under
`model_lang_parts/HiOps` and `unreached_paths` data structure under
`lang_models/gnu_c`). See
[SUPPORT_reflections_on_updating_nascent_and_ontological_alignment.md](SUPPORT_reflections_on_updating_nascent_and_ontological_alignment.md).

How to read the list (§6d):

- A path is node names joined by `/`, from `map_HiOp_to_unit` down.
- An entry covers its node's whole sub-tree, unless an entry for a node
  deeper in it says otherwise.
- `to: deleted` takes a node out of the live tree; its files go to
  `.archive/` (PlanPlan never deletes a file).
- `from: new` marks a node built here, in `.NASCENT/`.

Table 1. What `.NASCENT/` holds.

| in `.NASCENT/` | what it is |
|---|---|
| `CORE_0_0_0_0_2_map_HiOp_to_unit.md` | the node's new CORE: its updated definition, notes (`entry_info` `state_info[0]`, `derived_info` `state_info[n]`, `find_unreached_paths`, `unreached_paths`), and register |
| `node_0_0_0_0_2_1_model_lang_parts/`, with its six parts and their sub-nodes | the language-agnostic modelling machinery (`HiOps`, `holders`, `infra`, `context`, `HiOp_complexities`, `HiOp_configurations`), each with its `CORE` and `PROGRESS` at its final address |
| `node_0_0_0_0_2_4_lang_models/`, with `gnu_c` (and its 6 sub-nodes) and `go` | `lang_models` (renaming `langs`), holding `gnu_c` (`traced_clang`, `trace`, `gate_tables`, `equivalence_classes`, `templates`, `unreached_paths`) and `go` |
| `SUPPORT_migration_map.md` | this file |

Table 2. Files, research tools, and code moving into `model_lang_parts` and `lang_models/gnu_c`, or retiring to `.archive/`.

| what | today in | goes to | whose |
|---|---|---|---|
| CORE, PROGRESS, CHECK, DASHBOARD of retired nodes | `extract_lang_vocab`, `model_HiOps`, `complex_signature_reader` | `.archive/` | §6d |
| `branch_trees.py` (`BranchTree`, `PartConstraint`, `AbstractConstraint`, `CandidateWriter`, `unlock_branch`: language-general tree solver) | `Research/trace_logical_paths_clone/branch_trees.py` | `model_lang_parts/HiOps/branch_trees` | Dee + Gemini (2026-10-26) |
| `enumerate_branch_candidates.py` (`UnreachedBranch`, `BranchCondition`, `VariantCandidate`, `Record`, `enumerate_every_path`, `classify_branches`) | `Research/trace_logical_paths_clone/enumerate_branch_candidates.py` | `model_lang_parts/HiOps/enumerate_branch_candidates` | Dee + Gemini (2026-10-26) |
| `enumerate_paths.py` (groups accepted traces into deterministic `(entry, exit)` paths / HiOp variants) | `Research/trace_logical_paths_clone/enumerate_paths.py` | `model_lang_parts/HiOps/enumerate_paths` | Dee + Gemini (2026-10-26) |
| `what_is_left_for_each_hiop.py` -> renamed **`find_unreached_paths.py`** (system comparing traced paths against `BranchTree`s to find remaining open branches) | `Research/trace_logical_paths_clone/what_is_left_for_each_hiop.py` | `model_lang_parts/HiOps/find_unreached_paths` | Dee (2026-10-26): no `_HiOp_` in name under `HiOps` |
| `accepted_signatures.py` (`type_answers`, `llvm_type_answers` querying the lowerer on the holder pool) | `Projects/PseudoArch/map_HiOp_to_unit/complex_signature_reader/accepted_signatures.py` | `model_lang_parts/holders/accepted_signatures` | Dee + Gemini (2026-10-26) |
| Gate-predicate equivalence-class partitioner (`EQUIVALENCE_CLASS_HOLDERS` / `TYPE_ONLY_HOLDERS` partitioning logic) | `Research/trace_logical_paths_clone/branch_trees.py` | `model_lang_parts/holders/equivalence_classes` | Dee + Gemini (2026-10-26) |
| `context.py` (`Context(operator, holders, setup, preamble, program)`: `entry_info` `state_info[0]`, `VALUE_FORMS`) | `Research/trace_logical_paths_clone/context.py` | `model_lang_parts/context/entry_context` | Dee + Gemini (2026-10-26) |
| `traced_clang` & `path_recorder.c` (`-fsanitize-coverage=trace-pc-guard` instrumented Clang 21.1.8 binary) | `Research/trace_logical_paths/` | `lang_models/gnu_c/traced_clang` | Dee: Clang stuff under `gnu_c` |
| `trace.py`, `trace_once.py`, `logical_path.py`, `lines_run.py` (`--in-hiop` trace runner and cutter) | `Research/trace_logical_paths_clone/` | `lang_models/gnu_c/trace` | Dee + Gemini (2026-10-26) |
| Clang C++ gate-predicate & `derived_info` tables (`PART_NAMES`, `INNER_READS`, `OPTION_NAMES`, `LANGUAGE_NAMES`, `NOT_NEEDED_NAMES`, `CANNOT_REACH_NAMES`, `REFUSAL`, `entry_info_unreachable`, Clang `leaf_reading` rules) | `Research/trace_logical_paths_clone/branch_trees.py` & `enumerate_branch_candidates.py` | `lang_models/gnu_c/gate_tables` | Dee + Gemini (2026-10-26) |
| GNU C holder facts & equivalence classes (`holder_facts_riscv64-runner_l14.json` -> `holder_facts.json` for `180` holders; `42` `EQUIVALENCE_CLASS_HOLDERS` + `3` `TYPE_ONLY_HOLDERS`, `HOLDER_PREAMBLE`) | `Research/trace_logical_paths_clone/` | `lang_models/gnu_c/equivalence_classes` | Dee + Gemini (2026-10-26) |
| GNU C standard-form templates (`operators_of(key)`, `operator_candidates`) | `Research/trace_logical_paths_clone/enumerate_branch_candidates.py` | `lang_models/gnu_c/templates` | Dee + Gemini (2026-10-26) |
| `what_is_left.json` -> renamed **`unreached_paths.json`** (solved GNU C record: `1,806` HiOps, `0` open branches left), plus `paths.json`, `lines.json`, `branch_candidates.json`, `trees/`, and `SUPPORT_*` pages | `Research/trace_logical_paths_clone/bt1_l04_.../` & `Planning/node_0_1_research/node_0_1_5_trace_logical_paths_clone/` | `lang_models/gnu_c/unreached_paths` | Dee (2026-10-26): `unreached_paths` data structure |
| clang's own readers: `extract_lang_vocab/clang.py`, `extract_lang_vocab/operator_reader/clang.py`, `model_HiOps/HiOp_sorter/clang.py`, `read_clang_types` in `holder_reader.py` | `Projects/PseudoArch/map_HiOp_to_unit/` | `lang_models/gnu_c` | Dee: "we can keep clang stuff under gnu_c" |
| `SUPPORT_gnu_c_infrastructure_lowered_whole.md` | `hub/autopoly` | `model_lang_parts/infra` | 

Edges that change at the end, in nodes that stay:

- `lower_HiOp`'s register gains `standard_HiOp_wrapper` and
  `extract_unit_from_LoHiOp`, in this order: `standard_HiOp_wrapper`,
  `compile_standard_source`, `read_words_at_symbol`,
  `extract_unit_from_LoHiOp`.
- `langs`'s CORE becomes `lang_models`'s, and its register holds `gnu_c`
  (with its 6 sub-nodes) and `go`.
- `DRY_mask_maker` becomes `mask_maker`: its node, and its code,
  `DRY_mask_maker.py` to `mask_maker.py`, whose comments keep what DRY
  means and what the module does. Dee, 2026-10-16: "i want to change
  `DRY_mask_maker` to `mask_maker`. comments inside can still example what
  its about DRY and what its doing."

Resolved questions (2026-10-26):

1. **Refined naming (`find_unreached_paths` vs. `unreached_paths`):**
   - The system/module under `model_lang_parts/HiOps` is named `find_unreached_paths` (without repeating `_HiOp_` inside `HiOps`).
   - The data structure/record it produces under `lang_models/gnu_c` is named `unreached_paths` (`unreached_paths.json`).
2. **Legacy brute-force / static `complex_signature_reader` walkers retired:**
   - The static cross-function walkers (`walk.py`, `cpp_walk.py`, `clang_walk.py`, `checking_reader.py`, `lowering_reader.py`) are superseded by `model_lang_parts/HiOps/branch_trees` (in-HiOp `BranchTree`s, calls not followed) and `model_lang_parts/holders/accepted_signatures` + `equivalence_classes`.
