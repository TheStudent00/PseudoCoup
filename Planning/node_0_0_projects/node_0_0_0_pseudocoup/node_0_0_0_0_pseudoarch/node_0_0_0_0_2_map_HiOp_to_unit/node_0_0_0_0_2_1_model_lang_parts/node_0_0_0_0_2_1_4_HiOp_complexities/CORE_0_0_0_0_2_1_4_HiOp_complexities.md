---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOp_complexities
level: 6
status: draft
settled_by: Dee
supersedes: null
designation: code (container)
node:
    name: HiOp_complexities
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_4_HiOp_complexities/CORE_0_0_0_0_2_1_4_HiOp_complexities.md
super_node:
    name: model_lang_parts
    path: ../CORE_0_0_0_0_2_1_model_lang_parts.md
sub_nodes:
    - name: HiOp_sorter
      path: node_0_0_0_0_2_1_4_0_HiOp_sorter/CORE_0_0_0_0_2_1_4_0_HiOp_sorter.md
---

# CORE 0_0_0_0_2_1_4 — HiOp_complexities

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOp_complexities
- **level:** 6
- **status:** draft
- **designation:** code (container)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [model_lang_parts](../CORE_0_0_0_0_2_1_model_lang_parts.md)

## sub_nodes

- [HiOp_sorter](node_0_0_0_0_2_1_4_0_HiOp_sorter/CORE_0_0_0_0_2_1_4_0_HiOp_sorter.md) — Sorts a language's operators into Dee's call-complexity classes (`simple`, `hybrid`, `complex`, `undetermined`) and by their in-HiOp `BranchTree` depth (`depth 0` vs.

## definition

How complex each HiOp is, read from the operator's definition and in-HiOp
`BranchTree` in its lowerer's own code along two orthogonal axes:

1. **Downstream Unit Call-Complexity (Dee's classes, log 373):**
   - `simple`: its own call key, and no other calls. It lowers directly.
   - `hybrid`: its own call key, and other calls.
   - `complex`: other calls only, with no key of its own.
   - `undetermined`: neither, so it is read again.
   Dee, 2026-10-06 : "a hybrid callee is where a callee is
   defined with other calls but also its own unique call key. that means that
   the hybrid complexity callee (HiOp) cannot be composed by a collection of
   simple callees because its own `main_call_key` is unique."

2. **In-HiOp Branch-Tree Depth (`depth 0` vs. `depth 1+` in `find_unreached_paths`):**
   - **Depth `0` (`0` internal branches in the HiOp's own functions):**
     `1,472` of the `1,806` GNU C operators (`1,059` solved + `413` refused).
     A single accepted probe from `EQUIVALENCE_CLASS_HOLDERS` immediately
     covers `100%` of the operator's in-HiOp code (`open = 0`).
   - **Depth `1+` (`1` or more internal branches in the HiOp's own functions):**
     `329` of the `1,806` GNU C operators (`284` solved + `45` refused), unlocked
     by `branch_trees.unlock_branch` using equivalence classes and `derived_info`
     (`state_info[n]`) until `open == 0`.
