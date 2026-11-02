---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit
level: 4
status: draft
settled_by: Dee
supersedes: null
designation: code (container)
node:
    name: map_HiOp_to_unit
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/CORE_0_0_0_0_2_map_HiOp_to_unit.md
super_node:
    name: pseudoarch
    path: ../CORE_0_0_0_0_pseudoarch.md
sub_nodes:
    - name: dict_of_lang_HiOps
      path: node_0_0_0_0_2_0_dict_of_lang_HiOps/CORE_0_0_0_0_2_0_dict_of_lang_HiOps.md
    - name: model_lang_parts
      path: node_0_0_0_0_2_1_model_lang_parts/CORE_0_0_0_0_2_1_model_lang_parts.md
    - name: lower_HiOp
      path: node_0_0_0_0_2_2_lower_HiOp/CORE_0_0_0_0_2_2_lower_HiOp.md
    - name: mask_maker
      path: node_0_0_0_0_2_3_mask_maker/CORE_0_0_0_0_2_3_mask_maker.md
    - name: lang_models
      path: node_0_0_0_0_2_4_lang_models/CORE_0_0_0_0_2_4_lang_models.md
---

# CORE 0_0_0_0_2 — map_HiOp_to_unit

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit
- **level:** 4
- **status:** draft
- **designation:** code (container)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [pseudoarch](../CORE_0_0_0_0_pseudoarch.md)

## sub_nodes

- [dict_of_lang_HiOps](node_0_0_0_0_2_0_dict_of_lang_HiOps/CORE_0_0_0_0_2_0_dict_of_lang_HiOps.md) — Per language, every HiOp: an operator with the holder types it is applied to.
- [model_lang_parts](node_0_0_0_0_2_1_model_lang_parts/CORE_0_0_0_0_2_1_model_lang_parts.md) — Each part of a language, read from its lowerer and modelled by language-agnostic machinery: its HiOps, its holders, the infrastructure its Units call, the contexts that change what a HiOp does, how complex each HiOp is, and each HiOp's configuration.
- [lower_HiOp](node_0_0_0_0_2_2_lower_HiOp/CORE_0_0_0_0_2_2_lower_HiOp.md) — The HiOp becomes machine words.
- [mask_maker](node_0_0_0_0_2_3_mask_maker/CORE_0_0_0_0_2_3_mask_maker.md) — A module, `mask_maker.py` (formerly `DRY_mask_maker.py`; DRY: Don't Repeat Yourself).
- [lang_models](node_0_0_0_0_2_4_lang_models/CORE_0_0_0_0_2_4_lang_models.md) — One sub-node per language, each holding what that language adds to the language-agnostic machinery in `model_lang_parts`: its lowerer's instrumented runner, its lowerer's gate-predicate and `derived_info` tables, its pre-queried `holder_facts.json` and canonical `EQUIVALENCE_CLASS_HOLDERS`, its standard-form source templates, and its solved model records (`unreached_paths.json`, `paths.json`, `lines.json`, `trees/`).

## definition

- A HiOp with its holders lowers to a sequence of LoOps; the context removes
the chaff during the slicing; the sliced form is the Unit.

- Each part of a language is read from its lowerer and modelled. The HiOps
become the dict's keys, and their Units its values.

  ```
    model_lang_parts    ->  each part of a language, read from its lowerer and modelled (language-agnostic machinery: BranchTree, unlock_branch, equivalence_classes, find_unreached_paths)
    dict_of_lang_HiOps  ->  the keys (HiOp variants, from HiOps) and their values (Units)
    lower_HiOp          ->  LoHiOp, and the Unit cut out of it: the values
    lang_models         ->  what each language adds, its lowerer's own pieces and solved records (unreached_paths) included
    mask_maker          ->  grid_mask_of_knowns: all work already done, so none is redone
  ```


- Redrawn 2026-10-15 at Dee's word, in place of a tree that had grown by our
steps (extract, then model), and updated 2026-10-26 after Dee's in-HiOp
branch-tree + gate-predicate equivalence-class method achieved 100% completion
across all `1,806` GNU C operators (`0` open branches / `0` unreached paths
left in `unreached_paths.json`):

  > what an unbelievable mess this is. it might actually be faster to start over and re-create the ontology from scratch then to try and disentangle this.

Every change is in [SUPPORT_migration_map.md](SUPPORT_migration_map.md).
Dee's decisions, in Dee's words, are in
[SUPPORT_settling_the_ontology.md](SUPPORT_settling_the_ontology.md), and the
2026-10-26 ontological alignment (`find_unreached_paths` vs. `unreached_paths`
and why this architecture solves vocabulary extraction for all C-family and
compiled languages in principle) is in
[SUPPORT_reflections_on_updating_nascent_and_ontological_alignment.md](SUPPORT_reflections_on_updating_nascent_and_ontological_alignment.md)
and [SUPPORT_nascent_updated_tree_and_nodes.md](SUPPORT_nascent_updated_tree_and_nodes.md).

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- LoHiOp is a HiOp lowered: its standard source compiled by the lowerer
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
- `entry_info` (`state_info[0]`) is the entry `Context(operator, holders, setup, preamble, program)` passed into the lowerer; `derived_info` (`state_info[n]`) is any in-HiOp local variable computed deterministically from `state_info[0]`
- `find_unreached_paths` (under `model_lang_parts/HiOps`) is the system that compares traced paths against the lowerer's in-HiOp `BranchTree`s to find any remaining open branches; `unreached_paths` (`unreached_paths.json` under `lang_models/<lang>`) is the data structure it produces

## support

- [SUPPORT_java_vocabulary_lowering_and_universal_language_matrix.md](SUPPORT_java_vocabulary_lowering_and_universal_language_matrix.md):
  Full Java / OpenJDK vocabulary (44 operators, 18,962 grid cells, 4,999 accepted variants) and `BranchTree`s
  (6 compiler/JVM files, 808 functions, max depth 41 across `Attr.java`, `Lower.java`, `Gen.java`, `Operators.java`,
  `templateTable_riscv.cpp`, `c1_LIRAssembler_arith_riscv.cpp`) consolidated into `lang_models/java/`; 100.0% lowered at both
  levels (`4,999 / 4,999` variants: 6,499 JVM bytecode instructions and 8,664 RISC-V Unit words on `riscv64-runner`,
  71 distinct arch-opcodes, 77 bytecode opcodes); 16 cross-language Domain-to-Range & AutoPoly emulation theorems formally
  proven in Z3 (`UNSAT` over all $2^{128}$ input pairs) across Java, GNU C, Go, Rust, and Python (`>>>` unsigned shift,
  JLS §15.17.2 non-trapping division `LONG_MIN / -1 == LONG_MIN`, `lcmp` $\equiv$ C++ `<=>`, and saturating float cast $\equiv$ Rust `as i64`);
  plus the complete **Universal All-Languages Matrix** across GNU C, 8 Clang dialects (`C++`, `OpenMP`, `ObjC`, `CUDA`, `HLSL`, `OpenCL`, `MS`),
  Go, Rust, Python, and Java (665,791 / 665,940 variants lowered, 99.98% coverage).
- [SUPPORT_python_vocabulary_lowering_and_domain_range_proofs.md](SUPPORT_python_vocabulary_lowering_and_domain_range_proofs.md):
  Full Python / CPython vocabulary (53 operators, 834,596 grid cells, 599,954 accepted variants) and `BranchTree`s
  (6 compiler/evaluator files, 767 functions, max depth 44 across `compile.c`, `bytecodes.c`, `generated_cases.c.h`,
  `abstract.c`, `longobject.c`, `floatobject.c`) consolidated into `lang_models/python/`; 100.0% lowered at both
  levels (`599,954 / 599,954` variants: 8,079,035 CPython bytecode instructions and 6,991,809 RISC-V Unit words on `riscv64-runner`,
  52 distinct arch-opcodes, 22 bytecode opcodes); 15 cross-language Domain-to-Range & AutoPoly emulation theorems formally
  proven in Z3 (`UNSAT` over all $2^{128}$ input pairs and $2^{192}$ triples) across Python, GNU C, Go, and Rust (floored division
  `a // b`, floored modulo `a % b`, division-modulo algebraic preservation, chained comparison conjunctions `a < b < c`,
  and shift range guards).
- [SUPPORT_rust_vocabulary_lowering_and_domain_range_proofs.md](SUPPORT_rust_vocabulary_lowering_and_domain_range_proofs.md):
  Full Rust compiler vocabulary (41 operators, 1,168 accepted variants) and `BranchTree`s
  (132 files, 2,145 functions, 2,157 branch points across `compiler/rustc_hir_typeck`,
  `compiler/rustc_mir_build`, and `compiler/rustc_codegen_ssa`) consolidated into `lang_models/rust/`;
  100.0% lowered to RISC-V `Unit`s on `riscv64-runner` (`1,168 / 1,168` variants, 14,138 words, 8,271 Unit words,
  115 distinct arch-opcodes); 14 cross-language Domain-to-Range & AutoPoly emulation theorems formally
  proven in Z3 (`UNSAT` over all $2^{128}$ input pairs) across Rust, GNU C, and Go (saturating float-to-int
  cast, division-by-zero & overflow panic guards, 128-bit multi-word carry addition, and in-range shift equivalences).
- [SUPPORT_go_lowering_and_logical_domain_range_proofs.md](SUPPORT_go_lowering_and_logical_domain_range_proofs.md):
  Dee's insight realized: automated derivation of defined domains $D_{\text{ok}}$,
  trap domains $D_{\text{trap}}$ (`runtime.panicdivide`, `runtime.panicshift`), and
  symbolic output formulas with zero work by hand solely by composing formal logical
  RISC-V `LoOp` Sail specifications in lowered Units; 12 cross-language equivalence
  theorems verified with Z3 (100% UNSAT) across Go, GNU C, and C++ (`<=>` spaceship,
  saturated shifts, division panics, bit-clear `a &^ b`), emitting SMT-LIB2 and Lean 4
  `bv_decide` proof obligations.
- [SUPPORT_autopoly_interactive_explorer.html](SUPPORT_autopoly_interactive_explorer.html):
  Interactive 2D domain-to-range matrix, automatically learned boundary predicates,
  synthesized piecewise C code, and lowered RISC-V Units (`divw`, `remw`, `sllw`, `sraw`,
  `fcvt.w.s`) for cross-language HiOp equivalence (`py.floordiv_i32`, `py.mod_i32`,
  `go.shl_i32`, `go.ashr_i32`, `rust.wrapping_div_i32`, `rust.cast_f32_to_i32`), verified
  across 10,000 / 10,000 random fuzz trials and all boundary probes.
- [SUPPORT_cross_arch_venn_diagram.html](SUPPORT_cross_arch_venn_diagram.html):
  Interactive 3-architecture Venn diagram (`riscv64`, `x86_64`, `aarch64`) comparing
  full-vocabulary variant lowering (57,480 variants, 91.48% universal) against
  first-of-each operator probes (1,379 operators, 84.84% universal), with click-to-inspect
  root cause diagnostics for AAPCS64 `va_list` ABI structs, x86 fixed registers,
  soft-float soften patterns, and SelectionDAG backend limits.
- [SUPPORT_cross_arch_venn_158_refusals_and_autopoly_domain_to_range.md](SUPPORT_cross_arch_venn_158_refusals_and_autopoly_domain_to_range.md):
  7-region Venn diagrams across RISC-V 64, x86-64, and AArch64 for operators
  (1,379) and variants (57,480); root cause analysis and complete elimination of
  all 51 Group B wrapper artifacts (dropping refusals to 110 genuine backend
  SelectionDAG failures on riscv64, 57,370 lowered); Arch-Unit extraction counts
  and DWARF line slicing vs Direct Lowerer Hijack; AutoPoly cross-language
  domain-to-range mapping and piecewise synthesis prototype verified at 100%.
- [SUPPORT_lowerer_hijack_and_gnu_c_lowering_results.md](SUPPORT_lowerer_hijack_and_gnu_c_lowering_results.md):
  Direct lowerer hijacking prototype results across all 12 troublesome former
  wrapper patch cases on riscv64, x86_64, and aarch64 (zero by-hand wrapper
  scaffolding or DWARF line slicing), plus the consolidated lowering pass on
  riscv64-runner: the 1,379-operator cross-architectural run and the full 57,480-variant
  run on riscv64 (57,240 canonical wrappers compiled, 57,322 lowered).
- [SUPPORT_hijacking_the_lowerer_vs_by_hand_wrappers.md](SUPPORT_hijacking_the_lowerer_vs_by_hand_wrappers.md):
  Dee's architectural realization: eliminating by-hand wrapper forms and DWARF
  slicing by hijacking the lowerer (`CodeGenFunction`) directly at the entry
  point (`state[0]` -> target exit), why all 12 patches in
  `standard_HiOp_wrapper.py` only existed to appease the C parser/Sema outside
  the HiOp, a ~60-line C++ direct lowerer hook, and a side-by-side comparison
  showing how source-level wrapper modeling collapses across all Clang languages.
- [SUPPORT_python_and_cpython_standard_hiop_wrapper.md](SUPPORT_python_and_cpython_standard_hiop_wrapper.md):
  Python and CPython equivalents of `standard_HiOp_wrapper`, showing how the 4
  core wrapper rules translate across GNU C, Pure Python bytecode, and CPython
  C-API, why 10 of the 12 historical GNU C wrapper patches disappear completely,
  and a complete, runnable implementation in ~85 lines of Python.
- [SUPPORT_lowering_efficiency_and_wrapper_algorithm_review.md](SUPPORT_lowering_efficiency_and_wrapper_algorithm_review.md):
  lowering wiring verification of `consolidated_gnu_c_vocabulary.jsonl.gz`
  (`57,480` variants, `110` uniform batches), the 4 hidden inefficiencies in the
  legacy lowering method (wrapper deduplication, whole-batch recompilation,
  compiler-setup grouping, disassembly overhead), full anatomy of
  `standard_HiOp_wrapper.py` (4 Core Rules vs. 12 Historical Patches), and a
  unified table-driven wrapper proposal.
- [SUPPORT_consolidating_map_hiop_to_unit_code_tree.md](SUPPORT_consolidating_map_hiop_to_unit_code_tree.md):
  exact inventory of why `Planning/.../node_0_0_0_0_2_map_HiOp_to_unit/` is
  already consolidated (`8` superseded folders moved to `.archive/`) while
  `Projects/PseudoArch/map_HiOp_to_unit/` kept both the new `.NASCENT` packages
  and the legacy root files/folders side by side, plus the 4-step cleanup to
  make `Projects/PseudoArch/map_HiOp_to_unit/` match `Planning/` 1-to-1.
- [SUPPORT_lowering_machinery_audit_and_next_steps.md](SUPPORT_lowering_machinery_audit_and_next_steps.md):
  complete audit of the existing lowering machinery (`standard_HiOp_wrapper.py`,
  `lower_HiOp.py`, `extract_unit_from_LoHiOp.py`, `map_HiOp_to_unit`, and
  `Research/lower_HiOp/lower_gnu_c.py`), what is already built and verified on
  `321,882` variants, and the 4 concrete gaps to wire our new 100% vocabulary
  (`57,480` GNU C variants + `592` non-GNU-C Clang variants) into it on the
  tower (`riscv64-runner`).
- [SUPPORT_all_clang_languages_and_gnu_c_whole_vocabulary_report.md](SUPPORT_all_clang_languages_and_gnu_c_whole_vocabulary_report.md):
  complete report on `riscv64-runner_l23_gnu_c_whole` (full GNU C clean pass and
  consolidation across `1,806` operators) and `riscv64-runner_l24_all_clang_languages`
  (all `528` non-GNU-C Clang 21.1.8 operators across `cxx`, `openmp_openacc`,
  `objc`, `ms_extensions`, `CUDA_SYCL`, `hlsl`, `opencl`, and
  `clang_recovery`, completing all `2,162 / 2,162` Clang 21.1.8 operators with
  `0` open branches).
- [SUPPORT_lightness_clang_languages_overlap_and_next_stage.md](SUPPORT_lightness_clang_languages_overlap_and_next_stage.md):
  exact runtime and candidate-count measurements of the new 100% vocabulary
  extraction method, operator overlap across all Clang languages (`2,162`
  keyed operators across `C`, `C++`, `Objective-C`, `OpenMP/OpenACC`,
  `OpenCL`, `CUDA/SYCL`, `HLSL`, and `MS extensions`), and readiness of the
  final `lower_HiOp` / `PseudoArch` stage.
- [SUPPORT_gnu_c_extracted_vocabulary_status_and_record_forms.md](SUPPORT_gnu_c_extracted_vocabulary_status_and_record_forms.md):
  status of the extracted GNU C vocabulary across all `1,806` operators and
  comparison of the record schemas (`paths.json`, `lines.json`,
  `branch_candidates.json`, `dict_of_lang_HiOps.py`) prior to vs. in the new
  100% method.
- [SUPPORT_diff_between_pseudocouphq_gemini_and_pseudocouphq.md](SUPPORT_diff_between_pseudocouphq_gemini_and_pseudocouphq.md):
  complete file-by-file comparison between `LOCAL/PseudoCoup(Gemini)` and
  `PRIVATE/PseudoCoup`, showing what exists only in `PRIVATE/PseudoCoup`,
  what exists only in `LOCAL/PseudoCoup(Gemini)`, and the exact
  subsystem-by-subsystem diffs.
- [SUPPORT_migration_map.md](SUPPORT_migration_map.md): every node of the
  tree before 2026-10-15 and every new one (updated 2026-10-26 with the 100%
  in-HiOp branch-tree & equivalence-class toolset), each with where it went
  (PlanPlan `framework/PROTOCOL.md` §6d); the record of this rework.
- [SUPPORT_reflections_on_updating_nascent_and_ontological_alignment.md](SUPPORT_reflections_on_updating_nascent_and_ontological_alignment.md):
  2026-10-26 reflections on refining the ontology (`find_unreached_paths`
  system under `model_lang_parts/HiOps` vs. `unreached_paths` data structure
  under `lang_models/gnu_c`) and why the 4-pillar architecture solves
  vocabulary extraction for all C-family languages and other compiled
  languages in principle.
- [SUPPORT_nascent_updated_tree_and_nodes.md](SUPPORT_nascent_updated_tree_and_nodes.md):
  complete visible view of the updated `.NASCENT` node hierarchy, every
  node's `CORE` definition, the updated migration map, and the 2026-10-26
  Standard Progress View showing 100% GNU C completion (`0` unreached paths).
- [SUPPORT_modelling_sketch_for_the_outstanding_items.md](SUPPORT_modelling_sketch_for_the_outstanding_items.md):
  a page of sketches, one per model (places, a Unit's meaning, holders per
  machine, calls, traps, data, control, threads), each with the open items of
  the what-is-missing list it would close. Dee, 2026-10-12: "id also like a
  sketch of the modelling we would have to do to solve the outstanding items."
- [SUPPORT_settling_the_ontology.md](SUPPORT_settling_the_ontology.md): how
  this tree was settled, 2026-10-15: Dee's sketch, Dee's decisions in Dee's
  words, and what was left open.
- [SUPPORT_work_remaining.md](SUPPORT_work_remaining.md): what must still be
  completed in this node, in the order to go through it, one or two items at
  a time. Dee, 2026-10-15: "make a list of things that must be completed
  within the `map_HiOp_to_unit` node that we need to go through."
