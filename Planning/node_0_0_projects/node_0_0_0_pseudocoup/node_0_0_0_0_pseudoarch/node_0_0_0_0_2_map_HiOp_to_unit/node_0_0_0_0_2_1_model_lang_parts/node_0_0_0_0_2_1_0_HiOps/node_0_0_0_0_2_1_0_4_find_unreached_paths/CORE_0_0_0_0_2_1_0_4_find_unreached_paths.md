---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps.find_unreached_paths
level: 7
status: draft
settled_by: the owner
supersedes: null
designation: code (module)
node:
    name: find_unreached_paths
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_0_HiOps/node_0_0_0_0_2_1_0_4_find_unreached_paths/CORE_0_0_0_0_2_1_0_4_find_unreached_paths.md
super_node:
    name: HiOps
    path: ../CORE_0_0_0_0_2_1_0_HiOps.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_0_4 — find_unreached_paths

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOps.find_unreached_paths
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [HiOps](../CORE_0_0_0_0_2_1_0_HiOps.md)

## sub_nodes

*(none yet)*

## definition

The whole-vocabulary completeness verifier (`find_unreached_paths.py`,
replacing the research script `what_is_left_for_each_hiop.py`; named without
`_HiOp_` because its parent container node is already `HiOps`).

- Compares all traced runs and branch-candidate records of every operator in
  a language's vocabulary (`depth 0` and `depth 1+` alike) against the
  lowerer's in-HiOp `BranchTree`s.
- Produces the language's **`unreached_paths`** data structure
  (`unreached_paths.json` under `lang_models/<lang>/unreached_paths`),
  recording per operator and across the whole vocabulary:
  - `solved` vs. `refused` status at `depth 0` and `depth 1+`,
  - counts of `taken`, `not needed`, `cannot reach`, and `open` branches, and
  - any remaining open branches (`0` open branches / `0` distinct branches
    left across all `1,806` GNU C operators).
