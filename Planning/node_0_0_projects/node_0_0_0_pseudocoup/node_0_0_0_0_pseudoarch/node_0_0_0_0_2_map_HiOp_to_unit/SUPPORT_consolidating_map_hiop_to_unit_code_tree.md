# Consolidating `Projects/PseudoArch/map_HiOp_to_unit/` to Match the Migrated `.NASCENT` Ontology

**Date:** 2026-10-28  
**Scope:** Why duplicate files/folders remain in [Projects/PseudoArch/map_HiOp_to_unit/](file://Projects/PseudoArch/map_HiOp_to_unit) after the `.NASCENT` migration, and the exact consolidation steps to align the Python code tree 1-to-1 with [Planning/.../node_0_0_0_0_2_map_HiOp_to_unit/](file://Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit).

---

<details open>
<summary><b>1. Why Duplicates Exist: <code>Planning/</code> Archival vs. <code>Projects/</code> Copy-Plus-Shim</b></summary>

When the `.NASCENT` ontology migration ran earlier (before merging `LOCAL/PseudoCoup(Gemini)` into `PRIVATE/PseudoCoup`):

1. **In `Planning/.../node_0_0_0_0_2_map_HiOp_to_unit/` (100% Consolidated):**
   - All 8 superseded pre-`.NASCENT` planning directories (`node_0_0_0_0_2_1_standard_HiOp_wrapper` through `node_0_0_0_0_2_8_model_HiOps`) were **moved** into [`.archive/superseded_by_nascent_2026-10-27/`](file://Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/.archive/superseded_by_nascent_2026-10-27).
   - Only the 5 canonical `.NASCENT` children remain live:
     - `node_0_0_0_0_2_0_dict_of_lang_HiOps`
     - `node_0_0_0_0_2_1_model_lang_parts`
     - `node_0_0_0_0_2_2_lower_HiOp`
     - `node_0_0_0_0_2_3_mask_maker`
     - `node_0_0_0_0_2_4_lang_models`

2. **In `Projects/PseudoArch/map_HiOp_to_unit/` (Copied Without Archiving the Old Code):**
   - The migration subagent created the new `.NASCENT` packages (`model_lang_parts/`, `lower_HiOp/`, `mask_maker.py`, `lang_models/`) by **copying** the implementation files into their new ontological homes, **but left the old pre-`.NASCENT` files and directories sitting at the root of `Projects/PseudoArch/map_HiOp_to_unit/`** so old import paths (`from PseudoArch.map_HiOp_to_unit import extract_lang_vocab, DRY_mask_maker, standard_HiOp_wrapper, ...`) would not fail.
   - Because both `PRIVATE/PseudoCoup` and `LOCAL/PseudoCoup(Gemini)` received that same `.NASCENT` migration, our subsequent repo diff between `PCHQ(Gemini)` and `PCHQ` showed `0` differences inside `Projects/PseudoArch/map_HiOp_to_unit/` — both repos had the exact same side-by-side old + new layout.

</details>

---

<details open>
<summary><b>2. Exact Inventory of Duplicate / Superseded Files in <code>Projects/PseudoArch/map_HiOp_to_unit/</code></b></summary>

### A. Root-Level Files Duplicated Inside `lower_HiOp/` or `mask_maker.py`

| Legacy Root File in `map_HiOp_to_unit/` | Canonical `.NASCENT` Location | Current State & SHA256 |
| :--- | :--- | :--- |
| [lower_HiOp.py](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp.py) (`15,079 B`) | [lower_HiOp/__init__.py](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/__init__.py) (`15,161 B`) | **Python module/package collision:** `lower_HiOp.py` sits next to package directory `lower_HiOp/`. Identical except `lower_HiOp/__init__.py` appends `from . import standard_HiOp_wrapper, extract_unit_from_LoHiOp`. |
| [standard_HiOp_wrapper.py](file://Projects/PseudoArch/map_HiOp_to_unit/standard_HiOp_wrapper.py) (`48,984 B`) | [lower_HiOp/standard_HiOp_wrapper.py](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/standard_HiOp_wrapper.py) (`48,985 B`) | Byte-for-byte identical except line 23 (`from .extract_lang_vocab` vs `from ..extract_lang_vocab`). |
| [extract_unit_from_LoHiOp.py](file://Projects/PseudoArch/map_HiOp_to_unit/extract_unit_from_LoHiOp.py) (`6,905 B`, `58c991dac64e`) | [lower_HiOp/extract_unit_from_LoHiOp.py](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/extract_unit_from_LoHiOp.py) (`6,905 B`, `58c991dac64e`) | `100%` identical copy (`sha256:58c991dac64e`). |
| [atomic_parts_c.json](file://Projects/PseudoArch/map_HiOp_to_unit/atomic_parts_c.json) (`3,076 B`, `42955f3f68b7`) | [lower_HiOp/atomic_parts_c.json](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/atomic_parts_c.json) (`3,076 B`, `42955f3f68b7`) | `100%` identical copy (`sha256:42955f3f68b7`). |
| [library_declarations_c.json](file://Projects/PseudoArch/map_HiOp_to_unit/library_declarations_c.json) (`13,074 B`, `fb5476ae0f14`) | [lower_HiOp/library_declarations_c.json](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/library_declarations_c.json) (`13,074 B`, `fb5476ae0f14`) | `100%` identical copy (`sha256:fb5476ae0f14`). |
| [DRY_mask_maker.py](file://Projects/PseudoArch/map_HiOp_to_unit/DRY_mask_maker.py) (`121 B`) | [mask_maker.py](file://Projects/PseudoArch/map_HiOp_to_unit/mask_maker.py) (`74,043 B`) | 2-line shim (`from .mask_maker import *`). |

### B. Root-Level Directories Duplicated Inside `model_lang_parts/` and `lang_models/`

| Legacy Root Directory in `map_HiOp_to_unit/` | Canonical `.NASCENT` Location(s) | Current State |
| :--- | :--- | :--- |
| [extract_lang_vocab/](file://Projects/PseudoArch/map_HiOp_to_unit/extract_lang_vocab) (`15` files) | <ul><li>[model_lang_parts/HiOps/operator_reader/](file://Projects/PseudoArch/map_HiOp_to_unit/model_lang_parts/HiOps/operator_reader)</li><li>[model_lang_parts/holders/holder_reader.py](file://Projects/PseudoArch/map_HiOp_to_unit/model_lang_parts/holders/holder_reader.py)</li><li>[model_lang_parts/HiOp_configurations/](file://Projects/PseudoArch/map_HiOp_to_unit/model_lang_parts/HiOp_configurations) (`dependent_HiOp_reader/`, `HiOp_configuration_solver/`)</li><li>[lang_models/gnu_c/clang.py](file://Projects/PseudoArch/map_HiOp_to_unit/lang_models/gnu_c/clang.py)</li></ul> | All children were copied into `model_lang_parts/` and `lang_models/gnu_c/`, but the old `extract_lang_vocab/` directory was left at the root, and internal imports still point to `PseudoArch.map_HiOp_to_unit.extract_lang_vocab`. |
| [complex_signature_reader/](file://Projects/PseudoArch/map_HiOp_to_unit/complex_signature_reader) (`6` files) | [model_lang_parts/holders/accepted_signatures.py](file://Projects/PseudoArch/map_HiOp_to_unit/model_lang_parts/holders/accepted_signatures.py) (plus superseded AST-walk files `walk.py`, `clang_walk.py`, `cpp_walk.py`, `checking_reader.py`) | `accepted_signatures.py` was migrated to `model_lang_parts/holders/`; the superseded walk files belong in `.archive/` just like `node_0_0_0_0_2_6_complex_signature_reader`. |
| [model_HiOps/](file://Projects/PseudoArch/map_HiOp_to_unit/model_HiOps) (`4` files) | <ul><li>[model_lang_parts/context/model_contexts.py](file://Projects/PseudoArch/map_HiOp_to_unit/model_lang_parts/context/model_contexts.py) (`sha256:db61a8d9e1ae`)</li><li>[model_lang_parts/HiOp_complexities/HiOp_sorter/](file://Projects/PseudoArch/map_HiOp_to_unit/model_lang_parts/HiOp_complexities/HiOp_sorter)</li></ul> | `100%` duplicated inside `model_lang_parts/`. |

</details>

---

<details open>
<summary><b>3. Consolidation Executed & Verified (1-to-1 with <code>Planning/</code>)</b></summary>

All 4 consolidation steps have been executed and verified across all `35` modules in [Projects/PseudoArch/map_HiOp_to_unit/](file://Projects/PseudoArch/map_HiOp_to_unit):

1. **Moved Shared Language-Part Definitions to [model_lang_parts/__init__.py](file://Projects/PseudoArch/map_HiOp_to_unit/model_lang_parts/__init__.py):**
   - Migrated `Operator`, `Holder`, `Declaration`, `declaring_file_path`, `preprocessed_file_path`, `declaration_of`, `PLACEHOLDER`, `placeholders_of`, `Judged`, `Extracted`, and `extract()` into `model_lang_parts/__init__.py`.

2. **Pointed Internal & Research Imports Strictly to the 5 Canonical `.NASCENT` Nodes:**
   - Updated [map_HiOp_to_unit/__init__.py](file://Projects/PseudoArch/map_HiOp_to_unit/__init__.py), [dict_of_lang_HiOps.py](file://Projects/PseudoArch/map_HiOp_to_unit/dict_of_lang_HiOps.py), [mask_maker.py](file://Projects/PseudoArch/map_HiOp_to_unit/mask_maker.py), [lower_HiOp/standard_HiOp_wrapper.py](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/standard_HiOp_wrapper.py), [lang_models/gnu_c/clang.py](file://Projects/PseudoArch/map_HiOp_to_unit/lang_models/gnu_c/clang.py), [model_lang_parts/](file://Projects/PseudoArch/map_HiOp_to_unit/model_lang_parts), [Research/lower_HiOp/](file://Research/lower_HiOp), and [Research/trace_logical_paths_clone/](file://Research/trace_logical_paths_clone) to import exclusively from `dict_of_lang_HiOps`, `model_lang_parts`, `lower_HiOp`, `mask_maker`, and `lang_models`.
   - Fixed the relative path depth (`PROJECTS` and `HAND_TABLES`) in `HiOp_configuration_solver.py`, `dependent_HiOp_reader.py`, `entry_context.py`, and `branch_trees.py`.

3. **Archived the Superseded Root Files and Directories:**
   - Moved `lower_HiOp.py`, `standard_HiOp_wrapper.py`, `extract_unit_from_LoHiOp.py`, `DRY_mask_maker.py`, `atomic_parts_c.json`, `library_declarations_c.json`, `extract_lang_vocab/`, `complex_signature_reader/`, and `model_HiOps/` into [Research/.archive/superseded_by_nascent_2026-10-27/Projects_PseudoArch_map_HiOp_to_unit/](file://Research/.archive/superseded_by_nascent_2026-10-27/Projects_PseudoArch_map_HiOp_to_unit).

4. **Verified Top-Level `Projects/PseudoArch/map_HiOp_to_unit/` Tree (1-to-1 with `Planning/`):**
   ```text
   Projects/PseudoArch/map_HiOp_to_unit/
   ├── __init__.py
   ├── dict_of_lang_HiOps.py       # node_0_0_0_0_2_0_dict_of_lang_HiOps
   ├── model_lang_parts/           # node_0_0_0_0_2_1_model_lang_parts
   ├── lower_HiOp/                 # node_0_0_0_0_2_2_lower_HiOp
   ├── mask_maker.py               # node_0_0_0_0_2_3_mask_maker
   └── lang_models/                # node_0_0_0_0_2_4_lang_models
   ```
   - All `35` modules import with `0` errors and `dict_of_lang_HiOps.from_consolidated_paths()` loads all `57,480` consolidated GNU C variants cleanly.

</details>
