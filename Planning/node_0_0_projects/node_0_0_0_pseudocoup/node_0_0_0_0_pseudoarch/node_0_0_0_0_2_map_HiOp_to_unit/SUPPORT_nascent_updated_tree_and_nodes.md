---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.nascent_updated_tree_and_nodes
status: draft
---

# SUPPORT — nascent_updated_tree_and_nodes

**SUPPORT — Updated `.NASCENT` Tree, Node `CORE` Definitions, Migration Map, and 2026-10-26 Standard Progress View (`100%` GNU C Completion)**

- **1. Complete Updated `.NASCENT` Node Hierarchy for `node_0_0_0_0_2_map_HiOp_to_unit`**
    - **Why this page exists:**
        - Because `site_writer.py` skips dot-prefixed folders like `.NASCENT/`, this page renders the complete updated `.NASCENT/` tree, every node's updated `CORE` definition, the updated `SUPPORT_migration_map.md`, and the 2026-10-26 Standard Progress View table directly in the PlanPlan wiki.
    - **Full Node Tree (`node_0_0_0_0_2_map_HiOp_to_unit`):**
        - **`node_0_0_0_0_2_map_HiOp_to_unit`** (`CORE_0_0_0_0_2_map_HiOp_to_unit.md`)
            - **`node_0_0_0_0_2_0_dict_of_lang_HiOps`** — Per language, every HiOp: an operator with the holder types it is applied to, and its lowered Unit.
            - **`node_0_0_0_0_2_1_model_lang_parts`** — Language-agnostic machinery that reads and models each part of a language from its lowerer:
                - **`node_0_0_0_0_2_1_0_HiOps`** (`model_lang_parts/HiOps`):
                    - `node_0_0_0_0_2_1_0_0_operator_reader` — Lists the operators of a language from its lowerer's tables.
                    - `node_0_0_0_0_2_1_0_1_branch_trees` — Parses in-HiOp `BranchTree`s (calls not followed) and solves untaken gate chains (`unlock_branch`, `PartConstraint`, `AbstractConstraint`, `CandidateWriter`) using gate-predicate equivalence classes and `derived_info` (`state_info[n]`).
                    - `node_0_0_0_0_2_1_0_2_enumerate_branch_candidates` — Closed-loop driver (`UnreachedBranch`, `BranchCondition`, `VariantCandidate`, `Record`, `enumerate_every_path`) that traces candidates (`--in-hiop`), classifies branches (`taken`, `not needed`, `cannot reach`, `open`), and iterates until `open == 0`.
                    - `node_0_0_0_0_2_1_0_3_enumerate_paths` — Groups accepted traces into distinct deterministic `(entry, exit)` paths (the HiOp variants).
                    - **`node_0_0_0_0_2_1_0_4_find_unreached_paths`** — Compares all traced paths across the vocabulary against the lowerer's in-HiOp `BranchTree`s and outputs `unreached_paths` (`unreached_paths.json`).
                - **`node_0_0_0_0_2_1_1_holders`** (`model_lang_parts/holders`):
                    - `node_0_0_0_0_2_1_1_0_holder_reader` — Reads built-in and derived holder types declared by the lowerer.
                    - `node_0_0_0_0_2_1_1_1_accepted_signatures` — Queries the lowerer's AST and IR predicates (`type_answers`, `llvm_type_answers`) on the candidate holder pool to produce `holder_facts.json`.
                    - `node_0_0_0_0_2_1_1_2_equivalence_classes` — Partitions the holder pool by its lowerer gate-predicate answers into canonical gate-predicate equivalence class representatives (`EQUIVALENCE_CLASS_HOLDERS` + `TYPE_ONLY_HOLDERS`).
                - **`node_0_0_0_0_2_1_2_infra`** (`model_lang_parts/infra`) — Runtime / `compiler-rt` helper routines and target builtins that lowered Units call.
                - **`node_0_0_0_0_2_1_3_context`** (`model_lang_parts/context`):
                    - `node_0_0_0_0_2_1_3_0_entry_context` — `Context(operator, holders, setup, preamble, program)`: the `entry_info` (`state_info[0]`) object carried into the lowerer (`holders`, `places`, `VALUE_FORMS` `0..5`, compile options, target).
                    - `node_0_0_0_0_2_1_3_1_model_contexts` — Models how each storage place/context modifies a lowered Unit.
                - **`node_0_0_0_0_2_1_4_HiOp_complexities`** (`model_lang_parts/HiOp_complexities`):
                    - `node_0_0_0_0_2_1_4_0_HiOp_sorter` — Sorts operators by call complexity (`simple`, `hybrid`, `complex`) and in-HiOp `BranchTree` depth (`depth 0` single-probe vs. `depth 1+` branch-tree unlocking).
                - **`node_0_0_0_0_2_1_5_HiOp_configurations`** (`model_lang_parts/HiOp_configurations`):
                    - `node_0_0_0_0_2_1_5_0_dependent_HiOp_reader` — Reads where each dependent-HiOp may stand from the lowerer's checking code.
                    - `node_0_0_0_0_2_1_5_1_HiOp_configuration_solver` — Solves `N`-body statement configurations, depended-HiOp containers, and multi-template syntactic forms (`operators_of(key)`).
            - **`node_0_0_0_0_2_2_lower_HiOp`** — Standard-form wrapper, compiler lowering to LoHiOp, and Unit slicing:
                - `node_0_0_0_0_2_2_0_standard_HiOp_wrapper`
                - `node_0_0_0_0_2_2_1_compile_standard_source`
                - `node_0_0_0_0_2_2_2_read_words_at_symbol`
                - `node_0_0_0_0_2_2_3_extract_unit_from_LoHiOp`
            - **`node_0_0_0_0_2_3_mask_maker`** — `mask_maker.py` (`grid_mask_of_knowns`, DRY).
            - **`node_0_0_0_0_2_4_lang_models`** (`lang_models`, renaming `langs`) — One sub-node per language, holding that language's lowerer specifics and solved records (without language prefixes inside the folder):
                - **`node_0_0_0_0_2_4_0_gnu_c`** (`lang_models/gnu_c`):
                    - `node_0_0_0_0_2_4_0_0_traced_clang` — `-fsanitize-coverage=trace-pc-guard` instrumented Clang 21.1.8 binary & `path_recorder.c`.
                    - `node_0_0_0_0_2_4_0_1_trace` — `trace.py`, `trace_once.py`, `logical_path.py`, `lines_run.py` (`--in-hiop` trace runner & cutter).
                    - `node_0_0_0_0_2_4_0_2_gate_tables` — Clang C++ AST/LLVM gate-predicate & `derived_info` (`state_info[n]`) tables (`PART_NAMES`, `INNER_READS`, `OPTION_NAMES`, `LANGUAGE_NAMES`, `NOT_NEEDED_NAMES`, `CANNOT_REACH_NAMES`, `REFUSAL`, `entry_info_unreachable`, Clang `leaf_reading`).
                    - `node_0_0_0_0_2_4_0_3_equivalence_classes` — `holder_facts.json` (`180` holders), `42` `EQUIVALENCE_CLASS_HOLDERS` + `3` `TYPE_ONLY_HOLDERS`, `HOLDER_PREAMBLE`.
                    - `node_0_0_0_0_2_4_0_4_templates` — GNU C standard-form templates (`operators_of(key)`, `operator_candidates`).
                    - **`node_0_0_0_0_2_4_0_5_unreached_paths`** — **`unreached_paths.json`** (`1,806` HiOps, `0` open branches / `0` distinct branches left), `paths.json`, `lines.json`, `branch_candidates.json`, `trees/`, and `SUPPORT_*` pages.
                - **`node_0_0_0_0_2_4_1_go`** (`lang_models/go`) — Go's lowerer specifics (`cmd/compile`) and model records.

- **2. Node-by-Node `CORE` Definitions in `.NASCENT/`**
    - **`CORE_0_0_0_0_2_map_HiOp_to_unit.md`:**
        - **Definition:** A HiOp with its holders lowers to a sequence of LoOps; the context removes the chaff during the slicing; the sliced form is the Unit. Each part of a language is read from its lowerer and modelled (`model_lang_parts`); the HiOps become the dict's keys and their Units its values (`dict_of_lang_HiOps`); `lower_HiOp` compiles and slices the Unit; `lang_models` holds each language's lowerer specifics and solved records (`unreached_paths.json`); `mask_maker` prevents redoing completed work.
        - **Key Notes:**
            - `entry_info` (`state_info[0]`) is the entry `Context(operator, holders, setup, preamble, program)` passed into the lowerer; `derived_info` (`state_info[n]`) is any in-HiOp local variable computed deterministically from `state_info[0]`.
            - `find_unreached_paths` (under `model_lang_parts/HiOps`) is the system that compares traced paths against the lowerer's in-HiOp `BranchTree`s to find any remaining open branches; `unreached_paths` (`unreached_paths.json` under `lang_models/<lang>`) is the data structure it produces.
    - **`CORE_0_0_0_0_2_1_model_lang_parts.md` (`model_lang_parts`):**
        - **4 Language-Agnostic Pillars:**
            - **1. The Lowerer's Promise (`entry_info` `state_info[0]` -> Deterministic Path to Lowering or Refusal):** Every compiler accepts an entry `Context` (`state_info[0]`) and either lowers it along a deterministic path or refuses it along a diagnostic path; every `derived_info` (`state_info[n]`) local variable is a deterministic function of `state_info[0]`.
            - **2. Finite In-HiOp Control-Flow Trees (`BranchTree`, Calls Not Followed):** Restricting branch-tree extraction to code inside the HiOp's own functions (`--in-hiop`) keeps every operator's tree finite and shallow in any compiler.
            - **3. Finite Gate-Predicate Equivalence Classes (`accepted_signatures` + `equivalence_classes`):** Pre-querying the compiler's type predicates on a candidate holder pool partitions all holders into a small set of canonical gate-predicate equivalence classes (`42` + `3` in GNU C), eliminating combinatorial explosion and closing item 51.
            - **4. Closed-Loop Forward Trace + In-HiOp Gate Unlocking (`enumerate_branch_candidates` + `find_unreached_paths`):** `find_unreached_paths` compares traced runs against `BranchTree`s to produce `unreached_paths`, and `unlock_branch` emits `1` candidate per surviving equivalence class until `open == 0`.
    - **`CORE_0_0_0_0_2_1_0_HiOps.md` (`model_lang_parts/HiOps`) and Its 5 Sub-Nodes:**
        - **`operator_reader`:** Lists the operators of a language from its lowerer's tables (`1,806` GNU C operators: `357` expressions, `1,421` builtins/library calls, `28` statements).
        - **`branch_trees`:** Parses each HiOp's in-file `BranchTree` (calls not followed) and solves untaken gate chains (`unlock_branch`, `PartConstraint`, `AbstractConstraint`, `CandidateWriter`) using gate-predicate equivalence classes and `derived_info` (`state_info[n]`).
        - **`enumerate_branch_candidates`:** Runs the closed-loop `--in-hiop` trace-and-unlock cycle (`UnreachedBranch`, `BranchCondition`, `VariantCandidate`, `Record`, `enumerate_every_path`) until every in-HiOp branch is `taken`, `not needed`, or `cannot reach` (`open == 0`).
        - **`enumerate_paths`:** Groups accepted traces into distinct deterministic `(entry, exit)` lowering paths (`paths.json`).
        - **`find_unreached_paths`:** Compares all traced paths across the vocabulary against the lowerer's `BranchTree`s and outputs `unreached_paths` (`unreached_paths.json`).
    - **`CORE_0_0_0_0_2_1_1_holders.md` (`model_lang_parts/holders`) and Its 3 Sub-Nodes:**
        - **`holder_reader`:** Reads built-in and derived holder types from the lowerer (`180` holders in GNU C).
        - **`accepted_signatures`:** Queries the lowerer's AST and IR type predicates (`type_answers`, `llvm_type_answers`) on every holder (outer and `.inner` element/pointee) to produce `holder_facts.json`.
        - **`equivalence_classes`:** Partitions the holder pool by its `holder_facts.json` answers into canonical gate-predicate equivalence class representatives (`EQUIVALENCE_CLASS_HOLDERS` + `TYPE_ONLY_HOLDERS`).
    - **`CORE_0_0_0_0_2_1_2_infra.md` (`model_lang_parts/infra`):**
        - Models external runtime / `compiler-rt` routines and target helpers called by lowered Units (`58` routines reached on `riscv64`).
    - **`CORE_0_0_0_0_2_1_3_context.md` (`model_lang_parts/context`) and Its 2 Sub-Nodes:**
        - **`entry_context`:** `Context(operator, holders, setup, preamble, program)` and `VALUE_FORMS` (`0..5`): the `entry_info` (`state_info[0]`) object carried into the lowerer.
        - **`model_contexts`:** Models how each storage place (e.g. the bit-field place) transforms a lowered Unit.
    - **`CORE_0_0_0_0_2_1_4_HiOp_complexities.md` (`model_lang_parts/HiOp_complexities`) and `HiOp_sorter`:**
        - Sorts operators along both call-complexity (`simple`, `hybrid`, `complex`) and in-HiOp `BranchTree` depth (`depth 0`: `1,472` GNU C HiOps with `0` internal branches; `depth 1+`: `329` GNU C HiOps with internal branches).
    - **`CORE_0_0_0_0_2_1_5_HiOp_configurations.md` (`model_lang_parts/HiOp_configurations`) and Its 2 Sub-Nodes:**
        - **`dependent_HiOp_reader`:** Reads where each dependent-HiOp (`break`, `continue`, `case`, `default`, `return`) may stand.
        - **`HiOp_configuration_solver`:** Solves `N`-body patterns, depended-HiOp containers, and multi-template syntactic forms (`operators_of(key)`).
    - **`CORE_0_0_0_0_2_4_lang_models.md` (`lang_models`), `gnu_c`, and `go`:**
        - **`lang_models/gnu_c` (`CORE_0_0_0_0_2_4_0_gnu_c.md`):** Holds Clang/GNU C specifics without `gnu_c_` filename prefixes:
            - `traced_clang` (`traced_clang` binary & `path_recorder.c`)
            - `trace` (`trace.py`, `trace_once.py`, `logical_path.py`, `lines_run.py`)
            - `gate_tables` (`PART_NAMES`, `INNER_READS`, `OPTION_NAMES`, `LANGUAGE_NAMES`, `NOT_NEEDED_NAMES`, `CANNOT_REACH_NAMES`, `REFUSAL`, `entry_info_unreachable`, Clang `leaf_reading`)
            - `equivalence_classes` (`holder_facts.json` for `180` holders, `42` `EQUIVALENCE_CLASS_HOLDERS` + `3` `TYPE_ONLY_HOLDERS`, `HOLDER_PREAMBLE`)
            - `templates` (`operators_of(key)`, `operator_candidates`)
            - `unreached_paths` (`unreached_paths.json`: `1,806` HiOps, `0` open branches left; `paths.json`; `lines.json`; `branch_candidates.json`; `trees/`)
        - **`lang_models/go` (`CORE_0_0_0_0_2_4_1_go.md`):** Describes how Go's `cmd/compile` plugs into the same 4-pillar `model_lang_parts` pipeline.

- **3. Updated Migration Map (`SUPPORT_migration_map.md` Table 2)**

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

- **4. Updated Standard Progress View of GNU C Vocabulary Extraction (`model_lang_parts/PROGRESS.md` Table 1)**

| what | the previous methods, 2026-10-16 (elv2_l177) | Dee's method, 2026-10-19 15:25 UTC (fable1 to l126) | Dee's method, next column: runs l129 to l132 (queued 2026-10-19 night) | Dee's method, 2026-10-21 23:35 UTC (audit_every_record; runs riscv64-runner_l03 and riscv64-runner_l05, no compile; log 495) | Dee's method, 2026-10-26 (`riscv64-runner_l20..l22` + `find_unreached_paths` -> `unreached_paths.json`: in-HiOp `BranchTree`s + `42` equivalence classes + `derived_info`) |
|---|---|---|---|---|---|
| TOTAL COMPLETED, across all methods, in the strong sense: operators whose EVERY acceptable holder combination is known (every HiOp variant found) | 0 of 1,806 | 0 of 1,806 | the untaken-sides count, per operator, when l132 ends | 0 of 1,806 (1,322 have open branches) | **1,806 of 1,806 (`100%` complete; `0` operators with open branches left in `unreached_paths.json`)**: **`1,343` solved** (`1,059` at depth 0 + `284` at depth 1+, `1,376 / 1,376` accepted in-HiOp keys at `0` open branches), **`458` proven refused** (`413` at depth 0 + `45` at depth 1+), and **`5` untraceable pseudo-constructs** |
| not needed: outside GNU C, by clang's own text | | | | 172 of 1,806 | **458 of 1,806** proven refused on target in GNU C (`172` non-GNU-C syntax/keywords + `286` target/language-refused builtins: `413` at depth 0 + `45` at depth 1+) + **5** pseudo-constructs |
| across all methods, in the weak sense: operators with AT LEAST ONE holder choice clang accepts, found by any method | 1,348 of 1,806 | 1,348 of 1,806 | 1,348 |  | **1,343 of 1,806** real GNU C operators accepted and completely solved (`1,376` in-HiOp keys including multi-part forms) |
| TOTAL COMPLETED by Dee's method: accepted, every accepting path traced, all five checks held | | 894 of 1,806 | expected about 1,330 | 1,265 of the 1,634 GNU C | **1,343 of 1,343 (`100%` of accepted GNU C operators; `1,376 / 1,376` accepted in-HiOp keys)** |
| operators clang accepts with at least one choice of holders, this method alone | 1,340 | 912 | expected about 1,348 | 1,331 of the 1,634 GNU C | **1,343** (`1,059` at depth 0 + `284` at depth 1+) |
| accepted by both methods | 904 | 904 | |  | **1,340** |
| accepted by the previous methods only, so no accepting path traced yet | 436 | 436 | expected 0 |  | **0** (all valid GNU C operators traced; the remaining `5` are pseudo-constructs) |
| accepted by Dee's method only | 8 | 8 | |  | **3** (`1,343` vs `1,340` valid in GNU C) |
| accepted by neither method | 458 | 458 | |  | **458** (`413` at depth 0 + `45` at depth 1+, all proven refused in GNU C on target) |
| every accepting context's path traced and all five checks held | not done by this method | 894 of 912 | | 1,265 of the 1,331 accepted | **1,343 of 1,343** (`1,376 / 1,376` accepted in-HiOp keys, `0` open branches remaining) |
| the untaken sides of the paths' tests, each a variant-candidate still to construct | not done by this method | measured for 8 functions only | run l128 | 491,993 open (1,572 distinct branches) | **`0` open branches left across all `1,806` operators (`0` distinct branches left in `unreached_paths.json`)**: at depth 0 (`1,472` HiOps: `1,059` solved, `413` refused), `0` open; at depth 1+ (`329` HiOps: `284` solved, `45` refused), `0` open |
| the variant-candidates written and traced | | 21, by hand | a writer driven by l128's untaken sides |  | **Automated in-HiOp `CandidateWriter` + `unlock_branch` using `42` canonical gate-predicate equivalence classes (`EQUIVALENCE_CLASS_HOLDERS`), `derived_info` (`state_info[n]`) bindings, and `operators_of(key)` multi-template forms** (`riscv64-runner_l20..l22`: `1,302` -> `1,332` -> `1,376 / 1,376` solved, `0` open branches left) |
