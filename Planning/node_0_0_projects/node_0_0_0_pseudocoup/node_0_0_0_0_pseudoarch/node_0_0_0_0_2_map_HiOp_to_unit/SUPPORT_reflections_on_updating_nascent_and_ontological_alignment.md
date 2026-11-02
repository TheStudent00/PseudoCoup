---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.reflections_on_updating_nascent_and_ontological_alignment
status: draft
---

# SUPPORT — reflections_on_updating_nascent_and_ontological_alignment

**SUPPORT — Reflections on Updating `.NASCENT` (`model_lang_parts` and `lang_models/gnu_c`), Naming `find_unreached_paths` / `unreached_paths`, and Language-Agnostic Vocabulary Extraction**

- **1. Refined Naming in the Ontology: `find_unreached_paths` (System) and `unreached_paths` (Data Structure)**
    - **Why the old research names (`what_is_left_for_each_hiop.py` and `what_is_left.json`) are replaced:**
        - Under `model_lang_parts` -> `HiOps`, the parent container node already says `HiOps`, so repeating `_for_each_hiop` or `_HiOp_` in the child node's name is redundant.
        - Separating the **system/function that finds remaining unreached paths** from the **data structure/record it produces** makes each role explicit:
            - **`find_unreached_paths` (`model_lang_parts/HiOps/find_unreached_paths`):**
                - The system/module (replacing `what_is_left_for_each_hiop.py`) that compares all traced paths of every operator in the vocabulary against the lowerer's branch trees and finds any unreached branches/paths that remain open.
            - **`unreached_paths` (`lang_models/gnu_c/unreached_paths.json`):**
                - The data structure/record (replacing `what_is_left.json`) produced by `find_unreached_paths`, holding the per-operator and whole-vocabulary unreached-path state (`0` open branches / `0` unreached paths left across all `1,806` GNU C HiOps).

- **2. Why This Method Solves Vocabulary Extraction for All C-Family Languages and Other Compiled Languages in Principle**
    - **A. All C-Family Languages (C89/C90, C99, C11, C17, C23, GNU C, C++, Objective-C, OpenCL C, CUDA/HIP):**
        - **For Clang-lowered C dialects and C-family languages, 90%+ of the lowerer is literally the same Clang C++ codebase (`Sema*`, `CGExpr*`, `CGStmt*`, `CGBuiltin.cpp`):**
            - Every branch in Clang that we settled as `"not needed: outside GNU C"` during GNU C extraction (`getLangOpts().CPlusPlus`, `getLangOpts().C99`, `getLangOpts().C23`, `getLangOpts().ObjC`, `getLangOpts().OpenCL`, `getLangOpts().CUDA`, `inTemplateInstantiation()`, `CXXRecordDecl`, `ObjCObjectPointerType`, `BlockExpr`) is **already parsed into our `BranchTree`s**.
            - **Moving to another C dialect (C89, C99, C23):**
                - Only the compile standard flag in `setup` (`-std=c89`, `-std=c99`, `-std=c23`) changes. The `42` equivalence-class holders and `BranchTree` solver automatically take the dialect-gated branches that open up and close the GNU-only branches that turn off.
            - **Moving to C++ (`lang_models/cpp`) or Objective-C / OpenCL:**
                - The `BranchTree`s of `Sema` and `CodeGen` are already built.
                - Predicates that were in `LANGUAGE_NAMES` for GNU C (`isReferenceType`, `isMemberPointerType`, `CXXRecordDecl`, `getCXXOverloadedOperator`) move into the active gate table (`CHANGE_FOR`), and we add the C++-specific equivalence-class holders (lvalue/rvalue references `int &`, `int &&`, member pointers `int S::*`, class with non-trivial copy/destructor, template specialization).
                - No brute-force cross-product is needed: `unlock_branch` reads the C++ gate predicates along each in-HiOp branch chain and picks `1` representative per surviving C++ equivalence class.
    - **B. Other Compiled Languages Beyond the C Family (`go`, `rust`, `fortran`, `zig`, `swift`, `ada`):**
        - **Why the method itself is completely language-agnostic:**
            - The method relies on **4 structural invariants** that hold for **every** compiler/lowerer, regardless of source language:
                - **1. The Lowerer's Promise (`entry_info` -> Deterministic Path to Lowering or Refusal):**
                    - Every compiler accepts a syntax form + operand descriptors (`state_info[0]`) and either lowers it along a deterministic path to IR/machine instructions or refuses it along a diagnostic path.
                - **2. Finite Within-Function Control-Flow Trees (`BranchTree`, Calls Not Followed):**
                    - Every compiler is written in a structured implementation language (C++ for Clang/GCC/LLVM-frontends, Go for `cmd/compile`, Rust for `rustc`, etc.) that `tree-sitter` parses into `if` / `else` / `switch` / `match` branch trees.
                    - Analysing `calls not followed, only code within the HiOp` keeps every function's branch tree shallow and finite in any compiler.
                - **3. Finite Gate-Predicate Equivalence Classes (`EQUIVALENCE_CLASS_HOLDERS`):**
                    - No compiler writes separate branches for millions of concrete types; every compiler gates its lowering on **finite type-category predicates**:
                        - Clang (C/C++): `isIntegerType()`, `isFloatingType()`, `isVectorType()`, `isPointerType()`
                        - Go (`cmd/compile/internal/types`): `t.IsInteger()`, `t.IsFloat()`, `t.IsComplex()`, `t.IsSlice()`, `t.IsMap()`, `t.IsInterface()`, `t.IsChan()`
                        - Rust (`rustc_middle::ty`): `ty.is_integral()`, `ty.is_floating_point()`, `ty.is_simd()`, `ty.is_raw_ptr()`, `ty.is_ref()`, `ty.is_adt()`
                    - Pre-querying the compiler's type predicates on a candidate holder pool (`accepted_signatures`) always partitions the language's types into a small set of **gate-predicate equivalence classes** (`~20`–`50` canonical representatives), avoiding combinatorial explosion in every language.
                - **4. Forward Trace + In-HiOp Gate Unlocking (`trace` + `unlock_branch` + `find_unreached_paths`):**
                    - Recording executed basic blocks/lines in the lowerer binary (via `-fsanitize-coverage=trace-pc-guard` for C/C++/Rust lowerers, or Go coverage instrumentation for Go's compiler) tells `find_unreached_paths` which gates were not taken, and `unlock_branch` intersects the gate constraints along the chain to emit `1` candidate per surviving equivalence class.
        - **What stays invariant in `model_lang_parts` vs. what is plugged in per language in `lang_models/<lang>`:**
            - **`model_lang_parts` (100% language-agnostic, written once):**
                - `BranchTree`, `PartConstraint`, `AbstractConstraint`, `CandidateWriter`, `unlock_branch`, `enumerate_branch_candidates`, `enumerate_paths`, and `find_unreached_paths`.
            - **`lang_models/<lang>` (the thin language-specific plug-in):**
                - The lowerer's trace/line recorder (`trace`, `lines_run`),
                - The lowerer's gate-predicate name table (`leaf_reading` / `PART_NAMES` for that compiler's AST methods),
                - The language's equivalence-class holders (`EQUIVALENCE_CLASS_HOLDERS` and `holder_facts.json`), and
                - The language's standard-form wrapper templates (`templates.py`).

- **3. Updated `.NASCENT` Structure for `model_lang_parts` and `lang_models/gnu_c`**
    - **`model_lang_parts` (`node_0_0_0_0_2_1_model_lang_parts`) — Language-General Machinery:**
        - **`node_0_0_0_0_2_1_0_HiOps` (`model_lang_parts/HiOps`):**
            - `operator_reader`: lists the operators from the lowerer's tables.
            - `branch_trees` (`BranchTree`, `PartConstraint`, `AbstractConstraint`, `CandidateWriter`, `unlock_branch`): reads the lowerer's in-HiOp branch trees and solves gate chains using equivalence classes and `derived_info` (`state_info[n]`).
            - `enumerate_branch_candidates` (`UnreachedBranch`, `BranchCondition`, `VariantCandidate`, `Record`, `enumerate_every_path`): runs the closed-loop trace-and-unlock cycle until every in-HiOp branch is `taken`, `not needed`, or `cannot reach` (`open == 0`).
            - `enumerate_paths`: groups accepted traces into distinct deterministic `(entry, exit)` paths (the HiOp variants).
            - **`find_unreached_paths`**: compares all traced paths against the lowerer's branch trees and outputs `unreached_paths`.
        - **`node_0_0_0_0_2_1_1_holders` (`model_lang_parts/holders`):**
            - `holder_reader` + `accepted_signatures`: queries the lowerer on the holder pool to produce `holder_facts.json`.
            - `equivalence_classes` (`EQUIVALENCE_CLASS_HOLDERS`, `TYPE_ONLY_HOLDERS`): partitions holders by their lowerer gate-predicate answers into canonical equivalence-class representatives.
        - **`node_0_0_0_0_2_1_2_infra` (`model_lang_parts/infra`):**
            - Runtime / compiler-rt helper routines and target builtins that lowered Units call.
        - **`node_0_0_0_0_2_1_3_context` (`model_lang_parts/context`):**
            - `Context(operator, holders, setup, preamble, program)`: the `entry_info` (`state_info[0]`) object carried into the lowerer (`holders`, `places`, `VALUE_FORMS`, `options`, `target`), plus `model_contexts`.
        - **`node_0_0_0_0_2_1_4_HiOp_complexities` (`model_lang_parts/HiOp_complexities`):**
            - Call-complexity classes (`simple`, `hybrid`, `complex`) + in-HiOp branch depth (`depth 0` single-probe vs. `depth 1+` branch-tree unlocking).
        - **`node_0_0_0_0_2_1_5_HiOp_configurations` (`model_lang_parts/HiOp_configurations`):**
            - `N`-body / depended-HiOp container configurations + multi-template syntactic forms (`operators_of(key)`).
    - **`lang_models/gnu_c` (`node_0_0_0_0_2_4_0_gnu_c`) — GNU C and Clang Specifics (No `gnu_c_` Filename Prefix Needed):**
        - **Clang's instrumented binary & trace cutter:** `traced_clang`, `path_recorder.c`, `trace.py`, `logical_path.py`, `lines_run.py`.
        - **Clang's gate-predicate & `derived_info` tables:** `gate_tables.py` (`PART_NAMES`, `INNER_READS`, `OPTION_NAMES`, `LANGUAGE_NAMES`, `NOT_NEEDED_NAMES`, `CANNOT_REACH_NAMES`, `REFUSAL`, `entry_info_unreachable`, Clang C++ `leaf_reading` rules).
        - **GNU C's holder facts & equivalence classes:** `holder_facts.json` (`180` holders), `equivalence_classes.py` (`42` canonical representatives + `3` type-slot holders, `HOLDER_PREAMBLE`).
        - **GNU C's standard-form templates:** `templates.py` (`operators_of(key)`, `operator_candidates`).
        - **GNU C's solved model records:** **`unreached_paths.json`** (`0` open branches across all `1,806` HiOps), `paths.json`, `lines.json`, `branch_candidates.json`, `trees/`, and `SUPPORT_*` pages.
