---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.all_clang_languages_and_gnu_c_whole_vocabulary_report
status: draft
---

# SUPPORT — all_clang_languages_and_gnu_c_whole_vocabulary_report

Complete report on the two full-vocabulary runs executed on `2026-10-27`:
1. **`riscv64-runner_l23_gnu_c_whole`:** Full GNU C verification pass and consolidation across all `1,806` GNU C operators (`1,376` accepted operators, `0` open in-HiOp branches remaining, `57,480` accepted variants consolidated).
2. **`riscv64-runner_l24_all_clang_languages`:** Full extraction across all `528` non-GNU-C Clang 21.1.8 operators (`C++`, `OpenMP/OpenACC`, `Objective-C`, `Microsoft SEH/extensions`, `CUDA/SYCL`, `HLSL`, `OpenCL`, `RecoveryExpr`), completing **all `2,162 / 2,162` (`100%`) keyed operators in Clang 21.1.8 (`1,820` accepted, `342` genuine language/target/arity refusals, `0` open branches remaining, `58,057` accepted path variants)**.

---

## 1. Master Summary Across All `2,162` Clang 21.1.8 Keyed Operators (`riscv64-runner_l23` + `riscv64-runner_l24`)

* **1.1. Complete Dialect Table (`all_clang_languages_summary.json`)**
  * **`gnu_c` (`-std=gnu17 -target riscv64-linux-gnu`):**
    * Total operators: **`1,634`** (`1,806` including the `172` non-GNU-C dialect-gated keys below)
    * Accepted operators: **`1,376`**
    * Refused operators: **`258`** (target/header/non-riscv64 builtins & declarations)
    * Solved operators: **`1,634 / 1,634` (`100%`)** (`0` open branches)
    * Total path variants: **`70,839`** (`57,465` accepted variants)
  * **`cxx` (`-x c++ -std=gnu++20 -fcxx-exceptions -fcoroutines`):**
    * Total operators: **`301`** (`155` `KEYCXX` traits/`<=>`/`.*`/`->*` in `outside_gnu_c` + `146` `CXX*`/trait/coroutine/pack AST nodes in `keyed - gnu_c`)
    * Accepted operators: **`227`**
    * Refused operators: **`74`** (`72` opposite-arity keys of the `80` `TypeTraitExpr.*` traits—all `80` traits are accepted at their valid arity—plus `2` `CXXFoldExpr.Cmp` keys where C++20 forbids `<=>` in fold expressions)
    * Solved operators: **`301 / 301` (`100%`)** (`0` open branches)
    * Total path variants: **`436`** (`359` accepted variants)
  * **`openmp_openacc` (`-fopenmp` / `-fopenmp-simd` / `-Xclang -fopenmp-enable-irbuilder` / `-fopenacc`):**
    * Total operators: **`164`** (`4` `ArraySectionExpr` in `outside_gnu_c` + `160` `OMP*` / `OpenACC*` directives & expressions in `keyed - gnu_c`)
    * Accepted operators: **`163`**
    * Refused operators: **`1`** (`OMPArrayShapingExpr (1 parts)` `()a` with 0 dimensions, forbidden by OpenMP 5.0; `2 parts` `([d1])b` and `3 parts` `([d1][d2])c` are accepted)
    * Solved operators: **`164 / 164` (`100%`)** (`0` open branches)
    * Total path variants: **`164`** (`163` accepted variants)
  * **`objc` (`-x objective-c -fobjc-exceptions -fobjc-arc -fblocks`):**
    * Total operators: **`25`** (`ObjCMessageExpr`, `ObjCAtSynchronizedStmt`, `ObjCAutoreleasePoolStmt`, `ObjCArrayLiteral`, `ObjCDictionaryLiteral`, `ObjCAtTryStmt`, `ObjCAtCatchStmt`, `ObjCAtThrowStmt`, `ObjCForCollectionStmt`, `ObjCBoxedExpr`, `ObjCEncodeExpr`, `ObjCIsaExpr`, `ObjCPropertyRefExpr`, `ObjCSubscriptRefExpr`)
    * Accepted operators: **`25 / 25` (`100%`)**
    * Refused operators: **`0`**
    * Solved operators: **`25 / 25` (`100%`)** (`0` open branches)
    * Total path variants: **`29`** (`29` accepted variants)
  * **`ms_extensions` (`-fms-extensions` / `-fms-compatibility`):**
    * Total operators: **`21`** (`4` `KEYMS` traits + `SEHTryStmt`, `SEHExceptStmt`, `SEHFinallyStmt`, `SEHLeaveStmt`, `MSDependentExistsStmt`, `MSPropertySubscriptExpr`, `CXXUuidofExpr`)
    * Accepted operators: **`19`**
    * Refused operators: **`2`** (`2` `(2 parts)` arity keys of the unary traits `__is_interface_class` and `__is_sealed`, which are accepted at `(1 parts)`)
    * Solved operators: **`21 / 21` (`100%`)** (`0` open branches)
    * Total path variants: **`28`** (`26` accepted variants)
  * **`CUDA_SYCL` (`-x cuda --cuda-device-only -nocudainc -nocudalib` / `-fsycl-is-device`):**
    * Total operators: **`7`** (`CUDAKernelCallExpr (1..5 parts)`, `SYCLKernelCallStmt`, `SYCLUniqueStableNameExpr`)
    * Accepted operators: **`5`** (`CUDAKernelCallExpr (3..5 parts)`, `SYCLKernelCallStmt`, `SYCLUniqueStableNameExpr`)
    * Refused operators: **`2`** (`CUDAKernelCallExpr (1 parts)` and `(2 parts)`, which have fewer than the 2 required `<<<grid, block>>>` launch configuration arguments)
    * Solved operators: **`7 / 7` (`100%`)** (`0` open branches)
    * Total path variants: **`8`** (`6` accepted variants)
  * **`hlsl` (`-x hlsl -hlsl-profile cs_6_0`):**
    * Total operators: **`6`** (`IsIntangibleType`, `IsScalarizedLayoutCompatible`, `IsTypedResourceElementCompatible` at `1, 2 parts`)
    * Accepted operators: **`3`** (each trait accepted at its valid arity: `IsIntangibleType (1 parts)`, `IsScalarizedLayoutCompatible (2 parts)`, `IsTypedResourceElementCompatible (2 parts)`)
    * Refused operators: **`3`** (the opposite-arity keys of those same 3 traits)
    * Solved operators: **`6 / 6` (`100%`)** (`0` open branches)
    * Total path variants: **`9`** (`6` accepted variants)
  * **`opencl` (`-x cl -cl-std=CL3.0`):**
    * Total operators: **`2`** (`AsTypeExpr` `__builtin_astype`, `UnaryExprOrTypeTraitExpr.VecStep` `vec_step`)
    * Accepted operators: **`2 / 2` (`100%`)**
    * Refused operators: **`0`**
    * Solved operators: **`2 / 2` (`100%`)** (`0` open branches)
    * Total path variants: **`3`** (`3` accepted variants)
  * **`clang_recovery` (`-frecovery-ast`):**
    * Total operators: **`2`** (`RecoveryExpr (1 parts)`, `RecoveryExpr (2 parts)`)
    * Accepted operators: **`0`** (internal AST node constructed only when Sema emits a diagnostic on ill-formed input)
    * Refused operators: **`2`**
    * Solved operators: **`2 / 2` (`100%`)** (`0` open branches)
    * Total path variants: **`2`** (`0` accepted variants)
  * **Grand Total Across All Clang 21.1.8 Languages:**
    * **`2,162 / 2,162` (`100%`) operators solved (`1,820` accepted, `342` genuine language/target/arity refusals, `0` open branches remaining, `71,518` total path variants, `58,057` accepted path variants).**

---

## 2. Track 1 Details: Full GNU C Clean Pass (`riscv64-runner_l23_gnu_c_whole`) & Consolidation

* **2.1. What `riscv64-runner_l23_gnu_c_whole` Verified**
  * Ran the full `--in-hiop` (`in_hiop_spans.json`) + `EQUIVALENCE_CLASS_HOLDERS` pass across all `1,376` accepted GNU C operators inside the `riscv64-runner` container (`/persist/traced_clang_every_block` + `/persist/kept_listings`).
  * Added `("AtomicUsesUnsupportedLibcall", "not on all three architectures: taken on none of riscv64, x86-64, aarch64")` to `NOT_NEEDED_NAMES` in `enumerate_branch_candidates.py` to close the single remaining target-libcall branch in `AtomicExpr.AO__c11_atomic_load` (`Sema::BuildAtomicExpr:4507->4509`).
  * **Branch Outcomes Across All `1,376` Accepted GNU C Operators (`riscv64-runner_l23_gnu_c_whole/branch_candidates.json`):**
    * `taken`: **`481`**
    * `not needed`: **`580`**
    * `cannot reach`: **`123`**
    * **`open` / `not reached`: `0`**
  * **Updated `what_is_left.json` (`unreached_paths.json`) Across All `1,806` GNU C Operators:**
    * **Depth `0` (`1,472` HiOps):** **`1,087` solved** (`28` additional depth-0 operators unlocked by `EQUIVALENCE_CLASS_HOLDERS` over the `1,059` pre-`riscv64-runner_l23` count), `385` refused, **`0` distinct branches left**.
    * **Depth `1+` (`329` HiOps):** **`284` solved**, `45` refused, **`0` distinct branches left**.
    * **Total distinct open or unreached branches left across all `1,806` GNU C HiOps:** **`0`**.

* **2.2. Consolidated GNU C Files & `dict_of_lang_HiOps.py` Integration**
  * **`Projects/PseudoArch/map_HiOp_to_unit/lang_models/gnu_c/unreached_paths/unreached_paths.json`:** Latest verified `what_is_left.json` (`0` branches left).
  * **`Projects/PseudoArch/map_HiOp_to_unit/lang_models/gnu_c/unreached_paths/consolidated_gnu_c_vocabulary.json` (`45.15 MB`) & `.jsonl.gz` (`0.38 MB`):**
    * Merges operator metadata (`template`, `operands`, `source`), `holders_by_spelling`, `unreached_paths` status (`state`, `depth`), `riscv64-runner_l23_gnu_c_whole` `branch_candidates` counts (`open_branches: 0`), and all winning `paths.json` variants across all `1,806` GNU C operators (`71,336` total variants, `57,480` accepted variants, `60,413` unique accepted `(operator, holder_tuple)` contexts).
  * **`Projects/PseudoArch/map_HiOp_to_unit/dict_of_lang_HiOps.py`:**
    * Added `from_consolidated_paths(paths_record_or_path=None, lang="gnu_c", *, expand_contexts=False) -> list[Variant]`, converting the consolidated `57,480` accepted path variants (or `60,413` expanded holder contexts) directly into `Variant` entries that round-trip cleanly through `dict_of_lang_HiOps.write` and `dict_of_lang_HiOps.read`.

---

## 3. Track 2 Details: All Clang 21.1.8 Languages (`riscv64-runner_l24_all_clang_languages`)

* **3.1. Dialect Machinery in `Research/trace_logical_paths_clone/clang_languages_vocab.py`**
  * Classifies all `2,162` keyed operators from `operator_reader/clang.py` (`SUPPORT_vocabulary_runs_results.vocabulary_entries()`) into their exact Clang language dialect (`gnu_c`, `cxx`, `openmp_openacc`, `objc`, `ms_extensions`, `CUDA_SYCL`, `hlsl`, `opencl`, `clang_recovery`).
  * Provides dialect-specific `Setup` flags, preamble definitions (`struct ClassS` with data/virtual/member/operator methods, `std::strong_ordering` for `<=>`, `std::coroutine_handle` / `promise_type` for `co_await`/`co_yield`/`co_return`, variadic template fold wrappers for `CXXFoldExpr.*` and `PackExpansionExpr`/`PackIndexingExpr`, Objective-C `@interface`/`@implementation` & collection literal stubs, OpenMP loop/simd/target/task/irbuilder wrappers, CUDA `<<<grid, block>>>` and SYCL device wrappers), and canonical dialect holder equivalence classes.
  * Evaluates every traced path against the parsed Clang 21.1.8 `BranchTree`s (`riscv64-runner_l13_the_branch_trees/trees/clang/...`, including `SemaExprCXX.cpp.json`, `SemaCast.cpp.json`, `SemaTypeTraits.cpp.json`, `SemaOverload.cpp.json`, `SemaExceptionSpec.cpp.json`, `SemaTemplateVariadic.cpp.json`, `SemaObjC.cpp.json`, `SemaExprObjC.cpp.json`, `CGStmt.cpp.json`, `CGExprScalar.cpp.json`, `CGExprAgg.cpp.json`).

* **3.2. Consolidated All-Clang-Languages Deliverables**
  * `Research/trace_logical_paths_clone/riscv64-runner_l24_all_clang_languages/` (`paths.json`, `lines.json`, `branch_candidates.json`, `all_clang_languages_summary.json`)
  * `Projects/PseudoArch/map_HiOp_to_unit/lang_models/all_clang_languages_summary.json`
  * `Projects/PseudoArch/map_HiOp_to_unit/lang_models/consolidated_all_clang_languages_vocabulary.json` (`41 MB`) & `consolidated_all_clang_languages_vocabulary.jsonl.gz` (`786 KB`)
