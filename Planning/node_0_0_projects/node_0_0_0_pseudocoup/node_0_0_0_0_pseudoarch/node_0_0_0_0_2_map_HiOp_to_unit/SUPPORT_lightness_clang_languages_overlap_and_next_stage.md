---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.lightness_clang_languages_overlap_and_next_stage
status: draft
---

# SUPPORT — lightness_clang_languages_overlap_and_next_stage

Detailed measurements of how light the new 100% vocabulary extraction method is, how much overlap exists across all Clang languages (`2,162` total keyed operators across `C`, `C++`, `Objective-C`, `OpenMP/OpenACC`, `OpenCL`, `CUDA/SYCL`, `HLSL`, and `MS extensions`), what a full clean re-run of GNU C and the remaining Clang languages entails, and the readiness of the final `lower_HiOp` / `PseudoArch` stage.

---

## 1. How Light Is the New Vocab Extraction Method? (Timings & Candidate Counts)

* **1.1. Why the New Method (`riscv64-runner_l21..l22`) Is ~`50x`–`100x` Lighter Than Earlier Runs**
  * **Earlier runs (`fable1` / `riscv64-runner_l14..l19`):**
    * `riscv64-runner_l14` alone traced **`76,681` contexts across `590` operators** because it attempted to unlock branches in *every* function on the call path (including out-of-HiOp general conversion/diagnostic helpers) and took Cartesian products over `25`–`98` holders (`25^2 = 625` to `98^2 = 9,604` combinations).
    * Prior to `riscv64-runner_l18`, each worker also re-ran `objdump` (`~88s` per multi-function trace) and compiled every candidate twice (once for the binary trace, once for `lines.json`).
  * **The New Method (`riscv64-runner_l21` & `riscv64-runner_l22`):**
    1. **In-HiOp `BranchTree` Scoping (`in_hiop_spans.json`):**
       * **`1,047` of the `1,376` accepted GNU C operators (`76.1%`) have `0` in-HiOp branches** (`0` `if`/`switch`/`?:`/`&&`/`||` inside the Clang checking/lowering code that implements that operator).
       * Those `1,047` operators require **`0` rounds of branch-unlocking**—once their seed/signature equivalence classes are traced in Round 0, `unreached_branches` immediately proves `0` open branches left!
    2. **Gate-Predicate Equivalence Classes (`26` Canonical `EQUIVALENCE_CLASS_HOLDERS` in `holder_facts.json`):**
       * For the **`329` accepted GNU C operators that DO have in-HiOp branches**, `CandidateWriter` no longer tries brute-force Cartesian products of `98` holders. Instead, it looks up the exact gate-predicate equivalence class (`isIntegerType()`, `isFloatingType()`, `isVectorType()`, `isPointerType()`, etc.) in `holder_facts.json` and emits only **`1`–`6` targeted candidates per open branch**.
       * **Measured proof from `riscv64-runner_l21` and `riscv64-runner_l22`:**
         * Across all `42` operators with new candidates in `riscv64-runner_l21` (`4` parts): only **`1,030` candidates total** were traced (`~24.5` candidates per operator).
         * Across all `44` hardest remaining operators in `riscv64-runner_l22` (`4` parts): only **`109` new candidates total** were traced, and the `4` parallel parts finished in **`14.2s`, `22.4s`, `45.2s`, and `56.9s` wall-clock** (**under `1 minute` total**)!
    3. **Single-Compile Trace (`run_one_with_lines`) + `TLP_LISTING_CACHE` (`lines_run.py`):**
       * Every candidate is compiled once for its execution trace (producing both `paths.json` and `lines.json` from the same recording) plus once with `-S -emit-llvm` for its LLVM IR (`ir` / `ir_typed`), and `objdump` listings are read from the gzipped disk cache in milliseconds.

* **1.2. Cost of Re-Running GNU C Whole from a Clean Slate with the New Method**
  * If we run the new method from scratch across **all `1,806` GNU C operators** so every single operator's `paths.json`, `lines.json`, `branch_candidates.json`, and `unreached_paths.json` comes from one uniform run of the new pipeline:
    * **Mode A — Targeted Equivalence-Class Seed + Full In-HiOp Branch Unlocking:**
      * Round 0 traces each operator's accepted signature equivalence-class seeds (`~1`–`4` seeds for branchless operators; `~5`–`26` seeds for polymorphic/branchy operators), followed by `unlock_branch` to exhaustion (`0` open in-HiOp branches).
      * **Total contexts to trace across all `1,806` operators:** **~`5,000`–`8,000` contexts** (vs. `154,064` across the historical runs).
      * **Wall-clock time on `riscv64-runner`:** **~`6 to 12 minutes`** across parallel parts!
    * **Mode B — Full 26-Equivalence-Class Sweep on Every Operator + Full In-HiOp Branch Unlocking:**
      * If we also test all `26` canonical `EQUIVALENCE_CLASS_HOLDERS` on every operator in Round 0 (so even branchless operators record every accepted holder equivalence class in `paths.json`), plus full branch unlocking on the `329` branchy operators:
      * **Total contexts to trace:** **~`45,000`–`50,000` contexts**.
      * **Wall-clock time on `riscv64-runner`:** **~`20 to 30 minutes`** (or **~`3 to 5 minutes`** if Round 0 is batched with `one_program_for_many_candidates.py`).

---

## 2. Overlap Across All Clang Languages (`2,162` Total Keyed Operators in Clang 21.1.8)

`Projects/PseudoArch/map_HiOp_to_unit/extract_lang_vocab/operator_reader/clang.py` (`SUPPORT_vocabulary_runs_results.vocabulary_entries()`) already reads Clang 21.1.8's master tables (`StmtNodes.td`, `OperationKinds.def`, `TokenKinds.def`, `Builtins.td`, `BuiltinsRISCV.td`, `TypeTraits.h`, `ExpressionTraits.h`) across **all Clang languages**.

* **2.1. Exact Overlap Breakdown (`2,162` Total Keyed Operators Across All of Clang)**
  * **Total unique keyed operators across all Clang languages (`keyed`):** **`2,162` operators** (`2,417` raw entries).
  * **1. Core C / GNU C Operators Shared Across Almost All Clang Languages (`1,634 / 2,162` = `75.6%`):**
    * These `1,634` operators (`BinaryOperator.*`, `UnaryOperator.*`, `CompoundAssignOperator.*`, `CastExpr`, `CallExpr`, `ArraySubscriptExpr`, `MemberExpr`, `ConditionalOperator`, `AtomicExpr.AO*`, `CallExpr.BI*`, etc.) are shared directly by **`GNU C`, `C++ / GNU C++`, `Objective-C / Objective-C++`, `OpenCL C / C++`, `CUDA`, `HIP`, and `HLSL`**.
    * When compiled in C++ or Objective-C on standard C/fundamental types, Clang routes them through the **exact same Sema checking and CodeGen lowering functions** (`SemaExpr.cpp`, `SemaChecking.cpp`, `CGExprScalar.cpp`, `CGBuiltin.cpp`, `CGAtomic.cpp`) that we already modelled to `100%` in GNU C! (In C++, operator overloading on class/enum types branches into `SemaOverload.cpp` / `CXXOperatorCallExpr`, which is a separate AST node in the `356` list below.)
  * **2. Dialect-Gated Operators Already Inside Our `1,806` List (`172 / 2,162` = `8.0%`, `outside_gnu_c`):**
    * These `172` operators are already in the `1,806` operator list (`1,634 + 172 = 1,806`) and were only refused in `-std=gnu17` because their lexer/parser keyword requires a non-C dialect flag:
      * **C++ (`155` keys — `-x c++ -std=gnu++20`):**
        * `152` C++ type-trait operators (`TypeTraitExpr.*` with `KEYCXX` in `TokenKinds.def`, e.g., `__is_trivially_copyable`, `__is_constructible`, `__is_base_of`, `__is_same`, `__datasizeof`), all checked in `SemaTypeTraits.cpp` (whose `BranchTree` is **already parsed** in `riscv64-runner_l13_the_branch_trees/trees/clang/lib/Sema/SemaTypeTraits.cpp.json`!) and lowered to constant booleans/integers in `CGExprScalar.cpp`.
        * `3` C++ binary operators: `BinaryOperator.Cmp` (`<=>`), `BinaryOperator.PtrMemD` (`.*`), `BinaryOperator.PtrMemI` (`->*`).
      * **HLSL (`6` keys — `-x hlsl`):** `IsIntangibleType`, `IsScalarizedLayoutCompatible`, `IsTypedResourceElementCompatible` (2 forms each).
      * **Microsoft Extensions (`4` keys — `-fms-extensions`):** `IsInterfaceClass`, `IsSealed` (2 forms each).
      * **OpenMP / OpenACC (`4` keys — `-fopenmp`):** `ArraySectionExpr` (`1..4` parts).
      * **OpenCL (`2` keys — `-x cl`):** `__builtin_astype` (`AsTypeExpr`), `VecStep` (`UnaryExprOrTypeTraitExpr.VecStep`).
      * **Clang Error Recovery (`2` keys):** `RecoveryExpr` (internal AST node emitted only on invalid code).
  * **3. Non-C AST Classes Outside the `1,806` List (`356 / 2,162` = `16.5%`, `keyed - gnu_c`):**
    * Grouped by Clang language dialect:
      * **C++ (`146` keys):**
        * `CXXFoldExpr.*` (`66` keys — C++17 fold expressions `(... + args)`, `(args + ...)` across the 33 binary operators).
        * `CXXRewrittenBinaryOperator` (`33` keys — C++20 `<=>` / `==` rewritten comparisons).
        * `CXX*CastExpr` (`6` keys — `static_cast`, `dynamic_cast`, `reinterpret_cast`, `const_cast`, `CXXFunctionalCastExpr`, `CXXAddrspaceCastExpr`).
        * Calls, Construction & Destruction (`14` keys — `CXXConstructExpr`, `CXXTemporaryObjectExpr`, `CXXUnresolvedConstructExpr`, `CXXMemberCallExpr`, `CXXOperatorCallExpr`, `CXXDeleteExpr`, `CXXScalarValueInitExpr`, `CXXPseudoDestructorExpr`).
        * Exceptions, RTTI & Type/Expression Traits (`17` keys — `CXXTryStmt` `7`, `CXXCatchStmt` `3`, `CXXThrowExpr` `1`, `CXXTypeidExpr` `1`, `CXXNoexceptExpr` `1`, `ArrayTypeTraitExpr` `2`, `ExpressionTraitExpr` `2`).
        * Coroutines & Parameter Packs (`10` keys — `CoawaitExpr`, `CoyieldExpr`, `CoreturnStmt` `2`, `DependentCoawaitExpr`, `PackExpansionExpr`, `PackIndexingExpr`, `CXXDependentScopeMemberExpr`, `UnresolvedMemberExpr`).
      * **OpenMP & OpenACC (`160` keys):**
        * `76` OpenMP/OpenACC directives (`OMPParallelDirective`, `OMPForDirective`, `OMPSimdDirective`, `OMPTargetDirective`, `OMPTaskDirective`, `OMPAtomicDirective`, `OpenACCAtomicConstruct`, etc., `2` forms each = `152` keys) + `OMPIteratorExpr` (`5`) + `OMPArrayShapingExpr` (`3`).
      * **Objective-C (`25` keys):**
        * `ObjCMessageExpr` (`5`), `ObjCAtSynchronizedStmt` (`3`), `ObjCAutoreleasePoolStmt` (`3`), `ObjCArrayLiteral` (`2`), `ObjCDictionaryLiteral` (`2`), `ObjCAtThrowStmt` (`2`), `ObjCAtTryStmt` (`1`), `ObjCAtCatchStmt` (`1`), `ObjCForCollectionStmt` (`1`), `ObjCBoxedExpr` (`1`), `ObjCEncodeExpr` (`1`), `ObjCIsaExpr` (`1`), `ObjCPropertyRefExpr` (`1`), `ObjCSubscriptRefExpr` (`1`).
      * **Microsoft SEH / Extensions (`18` keys):**
        * `SEHTryStmt` (`5`), `SEHExceptStmt` (`3`), `SEHFinallyStmt` (`3`), `MSDependentExistsStmt` (`3`), `SEHLeaveStmt` (`1`), `MSPropertySubscriptExpr` (`1`), `CXXUuidofExpr` (`1`).
      * **CUDA & SYCL (`7` keys):**
        * `CUDAKernelCallExpr` (`5`), `SYCLKernelCallStmt` (`1`), `SYCLUniqueStableNameExpr` (`1`).

* **2.2. How Much Work Is Needed to Run the New Method on All Clang Languages?**
  * **83.5% of Clang (`1,806 / 2,162` operators) is already in our table**, and **`riscv64-runner_l13_the_branch_trees/trees/clang/` already parsed the C++ & Objective-C `BranchTree`s** (`SemaExprCXX.cpp.json`, `SemaOverload.cpp.json`, `SemaCast.cpp.json`, `SemaTypeTraits.cpp.json`, `SemaTemplateVariadic.cpp.json`, `SemaExceptionSpec.cpp.json`, `SemaObjC.cpp.json`, `SemaExprObjC.cpp.json`)!
  * To run the new method across the remaining Clang languages:
    1. **Dialect `Setup` flags:** Add `Setup` entries for `-x c++ -std=gnu++20 -fcxx-exceptions -fcoroutines`, `-fopenmp`, `-x cl -cl-std=CL3.0`, `-x objective-c -fobjc-exceptions`, and `-fms-extensions`.
    2. **C++ / Dialect Holder Equivalence Classes (`~8`–`10` new holders added to `EQUIVALENCE_CLASS_HOLDERS`):**
       * Add canonical C++ holder types (`struct ClassS` with virtual method/base/member pointer, `int &`, `int &&`, `int ClassS::*`, `int (ClassS::*)(int)`) so `SemaTypeTraits.cpp`, `SemaCast.cpp`, `CXXMemberCallExpr`, `PtrMemD` (`.*`), and `PtrMemI` (`->*`) have representatives for every C++ type-predicate equivalence class.
    3. **`in_hiop_spans.json` for the `146` `CXX*` + `155` `KEYCXX` operators:**
       * Run the `bt1_l01`/`bt1_l02` span extractor over the already-parsed `SemaExprCXX.cpp.json`, `SemaCast.cpp.json`, `SemaTypeTraits.cpp.json`, and `CGExprCXX.cpp` / `CGExprScalar.cpp` trees.

---

## 3. Readiness of the Final Stage of `map_HiOp_to_unit` and the Rest of `PseudoArch`

* **3.1. Inside `map_HiOp_to_unit` (`Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/`):**
  * **`standard_HiOp_wrapper.py` (`LoHiOp`):** Already implemented (`HiOp_on_its_own_line`, wrapping any `(operator, holders)` variant into its standalone C function `void op_k(struct P_k *p)`).
  * **`lower_HiOp.py` (`compile_standard_source` & `read_words_at_symbol`):** Already implemented (`371` lines, compiles with `-O0 -g` for `riscv64` and reads the DWARF line table + disassembly symbol words into a `LoHiOp`).
  * **`extract_unit_from_LoHiOp.py` (`extract_unit`):** Already implemented (`175` lines, slices the `LoHiOp` to the instructions filed under the HiOp's DWARF source line, strips the frame and the `ld <reg>, -0x18(s0)` reloads of `p` into `holds_p`, and preserves `part_<key>_<role>` relocations for multi-part HiOps).
* **3.2. What Remains in `map_HiOp_to_unit` After Vocab Extraction:**
  * Connecting the consolidated `paths.json` `variants` from our 100% vocabulary runs into `dict_of_lang_HiOps.py` -> `lower_HiOp.py` -> `extract_unit_from_LoHiOp.py` so every solved variant's lowered RISC-V `Unit` (and anyoutstanding items from `SUPPORT_work_remaining.md` / `SUPPORT_modelling_sketch_for_the_outstanding_items.md` such as control-flow/branching Units, calls, or special setup preambles) is extracted and verified against the Lean/Sail/GMP equivalence-checking pipeline (`sail_model_of_riscv`, `map_LoOp_to_lean`, `map_unit_to_lean`).
