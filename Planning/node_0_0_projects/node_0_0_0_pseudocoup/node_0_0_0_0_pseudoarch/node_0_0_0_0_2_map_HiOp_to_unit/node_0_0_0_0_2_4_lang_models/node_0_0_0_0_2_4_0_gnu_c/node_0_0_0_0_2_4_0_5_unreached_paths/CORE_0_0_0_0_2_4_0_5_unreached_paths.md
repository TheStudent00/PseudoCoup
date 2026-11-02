---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.unreached_paths
level: 7
status: draft
settled_by: the owner
supersedes: null
designation: data (record)
node:
    name: unreached_paths
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/node_0_0_0_0_2_4_0_gnu_c/node_0_0_0_0_2_4_0_5_unreached_paths/CORE_0_0_0_0_2_4_0_5_unreached_paths.md
super_node:
    name: gnu_c
    path: ../CORE_0_0_0_0_2_4_0_gnu_c.md
sub_nodes: []
---

# CORE 0_0_0_0_2_4_0_5 — unreached_paths

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.unreached_paths
- **level:** 7
- **status:** draft
- **designation:** data (record)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [gnu_c](../CORE_0_0_0_0_2_4_0_gnu_c.md)

## sub_nodes

*(none yet)*

## definition

The data structure and solved model records (`unreached_paths.json`, replacing
the research filename `what_is_left.json`, together with `paths.json`,
`lines.json`, `branch_candidates.json`, `trees/`, and `SUPPORT_*` pages)
produced for GNU C by `model_lang_parts/HiOps/find_unreached_paths`.

### Solved GNU C Summary in `unreached_paths.json` (`1,806` Operators)

- **Depth `0` (`1,472` HiOps with `0` internal branches in the HiOp's own functions):**
  - **Solved:** **`1,059` HiOps** (`100%` of accepted depth-`0` HiOps).
  - **Refused:** `413` HiOps.
  - **With open branches left:** **`0` HiOps** (`0` open branches, `0` distinct branches left).
- **Depth `1` or more (`329` HiOps with internal branches in the HiOp's own functions):**
  - **Solved:** **`284` HiOps** (`100%` of accepted depth-`1+` HiOps).
  - **Refused:** `45` HiOps.
  - **With open branches left:** **`0` HiOps** (`0` open branches, `0` distinct branches left).
- **Untraceable pseudo-constructs (`5` HiOps):** `5` HiOps.
- **Total open / unreached branches remaining across all `1,806` GNU C HiOps:**
  **`0` open branches (`0` distinct branches left)** across **`0` HiOps** (`1,376 / 1,376` accepted in-HiOp keys completely settled).
