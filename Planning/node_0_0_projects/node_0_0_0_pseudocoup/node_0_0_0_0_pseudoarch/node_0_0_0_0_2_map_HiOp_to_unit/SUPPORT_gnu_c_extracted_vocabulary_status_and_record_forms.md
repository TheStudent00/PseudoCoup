---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.gnu_c_extracted_vocabulary_status_and_record_forms
status: draft
---

# SUPPORT — gnu_c_extracted_vocabulary_status_and_record_forms

Complete status of the extracted GNU C vocabulary across all `1,806` operators and an exact comparison between the record forms produced prior to the new method vs. by the new method (`riscv64-runner_l21` / `riscv64-runner_l22`), structured with collapsible sections and nested bullet hierarchies.

---

## 1. Current Status of the GNU C Extracted Vocabulary (`1,806` Total HiOps)

* **1.1. Overall State Across All `1,806` GNU C Operators (`unreached_paths.json` / `what_is_left.json` & `holders_each_hiop_accepts.json`)**
  * **Total GNU C operators in the vocabulary:** **`1,806`**
    * **Depth `0` (no helper functions entered inside Clang's checking/lowering):** **`1,472` HiOps**
      * **Solved (`0` open branches / `0` unreached paths):** **`1,059` HiOps** in `what_is_left.json` (`1,089` accepted across all `paths.json` + `lines.json` records in `holders_each_hiop_accepts.json`).
      * **Refused on every traced context:** **`413` HiOps** in `what_is_left.json` (`383` refused across both `paths.json` and `lines.json`).
      * **Open / unreached branches remaining:** **`0`**.
    * **Depth `1+` (enters 1 or more helper functions inside Clang's checking/lowering):** **`329` HiOps**
      * **Solved (`0` open branches / `0` unreached paths):** **`284` HiOps** (`285` in `holders_each_hiop_accepts.json`).
      * **Refused on every traced context:** **`45` HiOps** (`44` in `holders_each_hiop_accepts.json`).
      * **Open / unreached branches remaining:** **`0`**.
    * **Constant-argument builtins traced in `fable1_l157` (`paths.json`) but without a separate `bt1_l02` entry tree (`depth: None` in `what_is_left.json`):** **`5` HiOps**
      * `CallExpr.BI__builtin_alloca_with_align` (`9` contexts, `7` accepted, `9` variants, all 5 checks passed)
      * `CallExpr.BI__builtin_alloca_with_align_uninitialized` (`9` contexts, `7` accepted, `9` variants, all 5 checks passed)
      * `CallExpr.BI__builtin_assume_dereferenceable` (`9` contexts, `1` accepted, `9` variants, all 5 checks passed)
      * `CallExpr.BI__builtin_memcpy_inline` (`81` contexts, `1` accepted, `75` variants, all 5 checks passed)
      * `CallExpr.BI__builtin_memset_inline` (`81` contexts, `7` accepted, `75` variants, all 5 checks passed)
  * **Aggregate Trace Totals:**
    * **`1,376 / 1,376` (`100%`)** of accepted GNU C operators have **`0` open or unreached in-HiOp branches remaining**.
    * **`154,064` total traced paths** (`96,857` accepted paths) recorded across `205` `paths.json` files and `119` `lines.json` files.

* **1.2. What the `430`–`458` "Refused on Every Context" Operators Are**
  * Every one of these operators was tested against the holder seed lists and refused by Clang in our `-std=gnu17 -target riscv64-linux-gnu` standard-form harness for one of five reasons (catalogued in `bt1_l05/holders_each_hiop_accepts.json`):
    1. **Non-C / C++-only / Objective-C / OpenMP AST operators included in Clang's master operator table:** e.g., `BinaryOperator.Cmp` (`<=>`), `BinaryOperator.PtrMemD` (`.*`), `BinaryOperator.PtrMemI` (`->*`), `ArraySectionExpr`, `ArrayInitLoopExpr`, `CallExpr.BImove`, `CallExpr.BIforward`, `CallExpr.BIaddressof`.
    2. **Target-specific builtins unsupported on `riscv64-linux-gnu`:** e.g., pointer-authentication builtins (`"this target does not support pointer authentication"`).
    3. **Undeclared C library builtins requiring header declarations or non-standard prototypes in C99/C17:** e.g., `"call to undeclared library function '...' with type '...'"`.
    4. **Builtins/atomics whose fixed arity or special literal arguments (e.g., string-literal-only formats/options or 2+/3+ argument atomics tested in a 1-arg slot) were refused by Sema.**

---

## 2. Are the Results Prior to the New Method in the Same Form as What the New Method Produces?

This question has **three distinct layers**—**(A) the JSON record schema inside `trace_logical_paths_clone`**, **(B) which holders/contexts populate those records across earlier runs vs. `riscv64-runner_l21..l22`**, and **(C) the pre-`trace_logical_paths_clone` `dict_of_lang_HiOps` (`c.knowns.jsonl.gz`) format**:

* **2.1. Layer A — Record File Schema Inside `trace_logical_paths_clone` (`paths.json`, `lines.json`, `branch_candidates.json`): YES, 100% Identical Schema**
  * **Why they match:** The new method (`riscv64-runner_l21` and `riscv64-runner_l22`) did **not** alter the output schema of `check_trace_logical_paths.py`, `trace_lines_on_the_paths.py`, or `enumerate_branch_candidates.py`. It changed **how candidate `Context`s are constructed** (using gate-predicate equivalence classes from `holder_facts.json` + in-HiOp `derived_info` `state_info[n]`) before passing those `Context`s into the exact same tracing pipeline.
  * **Exact comparison of `paths.json` (`fable1_l141` vs. `riscv64-runner_l14` vs. `riscv64-runner_l21` vs. `riscv64-runner_l22`):**
    * Top-level keys in all runs: `["clang", "setup", "operators"]`
    * Per-operator keys in all runs: `["contexts", "accepted", "variants", "checks", "same_lowering"]` *(note: `fable1_l141` also carried an optional `"ir_clang"` string key)*
    * Per-variant keys (`variants[i]`) in all runs:
      * `["contexts", "accepted", "exits", "checking_action", "lowering_mark", "events", "checking_steps", "lowering_steps", "ir", "ir_typed", "messages", "tests"]`
    * Per-operator `checks` keys in all runs:
      * `["1_same_path_twice", "2_exits_in_ir", "3_same_instructions_per_path", "4_tests_read_holders", "5_same_lowering_other_paths"]`
  * **Exact comparison of `lines.json` (`119` files across `fable1_*` and `riscv64-runner_*`):**
    * Top-level keys in all runs: `["clang", "setup", "small", "functions", "operators", "progress"]`
    * Per-function keys: `["file", "first", "last", "lines", "leaves", "paths", "contexts"]`
    * Per-operator keys: `["paths"]`
  * **One historical filename change (`untaken_sides.json` -> `branch_candidates.json`), already unified by the reader:**
    * Runs `fable1_l159..l193` (`8` folders) wrote `untaken_sides.json` (from `take_every_side.py`).
    * Runs `riscv64-runner_l02..l22` (`93` folders) wrote `branch_candidates.json` (from `enumerate_branch_candidates.py`).
    * Both `SUPPORT_vocabulary_runs_clangs_code.read_loop_records()` and `what_is_left_for_each_hiop.py` (`find_unreached_paths.py`) read both filenames and merge them into the exact same per-operator `sides` dictionary via `newest_per_operator()`.

* **2.2. Layer B — Holder & Candidate Provenance Across Runs (`fable1` / `riscv64-runner_l02..l20` vs. `riscv64-runner_l21..l22`): Scattered Across `205` Run Folders ("Later Wins")**
  * While the **JSON schema** of `paths.json` and `lines.json` is identical across all runs, the **GNU C vocabulary records are currently distributed across `205` incremental run folders** (`fable1_*` and `riscv64-runner_*`), merged at read time by the rule **"newest run per operator wins"** (`newest_per_operator`):
    1. **Operators solved prior to `riscv64-runner_l21` (~`1,280` operators, including the `1,047` branchless depth-0 operators and the depth-1+ operators solved in `riscv64-runner_l14..l20`):**
       * Their `paths.json` and `lines.json` records come from `fable1_l141..l193` and `riscv64-runner_l14..l20`.
       * Those runs traced contexts drawn from the earlier holder sets (the old method's accepted holders in `fable1_l141`, the 25-holder or 98-holder seed lists, or the pre-equivalence-class `accepted_signatures.py` tables) rather than the final `26`-holder `EQUIVALENCE_CLASS_HOLDERS` basis.
    2. **Operators solved in `riscv64-runner_l21` and `riscv64-runner_l22` (`56` operators in `riscv64-runner_l21` + `44` in `riscv64-runner_l22`):**
       * Their newest `paths.json`, `lines.json`, and `branch_candidates.json` records come from `riscv64-runner_l21_in_hiop_part_01..04` and `riscv64-runner_l22_in_hiop_part_01..04`, generated by the new gate-predicate equivalence-class + `derived_info` (`state_info[n]`) method.
  * **Implication:**
    * Right now, to read the complete GNU C vocabulary, a consumer has to scan and merge all `205` `paths.json` / `119` `lines.json` / `101` loop-record folders in chronological order (or read the summary in `bt1_l04/what_is_left.json`).
    * We have **not yet consolidated** the winning records for all `1,806` GNU C operators into a single clean, unified dataset under `Projects/PseudoArch/map_HiOp_to_unit/lang_models/gnu_c/unreached_paths/` (or re-run a single uniform pass of the new `100%` method across all `1,806` operators if you want every operator's variants expressed purely in the `26` canonical `EQUIVALENCE_CLASS_HOLDERS`).

* **2.3. Layer C — Pre-`trace_logical_paths_clone` Static Vocabulary Format (`dict_of_lang_HiOps.py` / `c.knowns.jsonl.gz`): Different Schema**
  * Before `trace_logical_paths_clone` was created, the old `extract_lang_vocab` pipeline wrote `Research/extract_lang_vocabulary/mask/gnu17/c.knowns.jsonl.gz` (read/written by `Projects/PseudoArch/map_HiOp_to_unit/dict_of_lang_HiOps.py`), where each line was a flat cell:
    * Old `dict_of_lang_HiOps.py` entry:
      `{"lang": "c", "operator": "BinaryOperator.Add", "template": "a + b", "operands": ["a", "b"], "source": "...", "holders": [["Int", "int", "..."], ["Int", "int", "..."]], "evidence": "..."}`
  * By contrast, `trace_logical_paths_clone`'s `paths.json` groups contexts by **distinct logical path through Clang** (`variants`), where each variant carries:
    * `contexts`: all traced holder tuples (or `(holders, preamble, program)` triples) that took that exact path,
    * `checking_steps` and `lowering_steps`: the exact sequence of Clang basic blocks / source lines and LLVM IR builder exits along the path,
    * `ir` and `ir_typed`: the exact lowered LLVM IR instructions produced by that variant,
    * `checks`: the 5 determinism and completeness invariants verified on that operator.
  * **`dict_of_lang_HiOps.py` has not yet been updated** to read directly from the consolidated `trace_logical_paths_clone` `paths.json` variants instead of the old `extract_lang_vocab` grid.

---

## 3. Two Options for Consolidating the GNU C Vocabulary Records Next

Depending on how you want `lang_models/gnu_c` and `dict_of_lang_HiOps` populated:

* **Option 1 — Consolidate the Existing Solved Records (`fable1` + `riscv64-runner_l02..l22`) into One Unified Record Set in `lang_models/gnu_c` (Fastest — No Re-Tracing Needed):**
  * Since `paths.json` and `lines.json` already have the exact same schema across all `205` run folders, we can merge the winning (`newest_per_operator`) `paths.json`, `lines.json`, and `unreached_paths.json` records for all `1,806` GNU C operators into a single canonical record set under `Projects/PseudoArch/map_HiOp_to_unit/lang_models/gnu_c/` and wire `dict_of_lang_HiOps.py` to read its `Variant` entries directly from those merged `variants`.
* **Option 2 — Run a Single Clean Pass of the New 100% Method Across All Accepted GNU C Operators (Uniform `EQUIVALENCE_CLASS_HOLDERS` Basis):**
  * If you want even the earlier ~`1,280` operators (which were traced in `fable1` / `riscv64-runner_l02..l20` with the older 25/98-holder lists) to have their `paths.json` variants expressed uniformly over the `26` canonical `EQUIVALENCE_CLASS_HOLDERS` (`holder_facts.json`) from a single clean run of the final method, we can run the final `riscv64-runner_l22` pipeline across all accepted operators and write one unified `paths.json` + `lines.json` + `unreached_paths.json`.
