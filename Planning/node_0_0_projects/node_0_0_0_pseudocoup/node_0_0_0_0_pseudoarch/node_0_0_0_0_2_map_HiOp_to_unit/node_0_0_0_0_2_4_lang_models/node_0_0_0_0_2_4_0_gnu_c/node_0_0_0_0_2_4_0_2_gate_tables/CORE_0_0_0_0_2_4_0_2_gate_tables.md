---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.gate_tables
level: 7
status: draft
settled_by: the owner
supersedes: null
designation: code (module)
node:
    name: gate_tables
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/node_0_0_0_0_2_4_0_gnu_c/node_0_0_0_0_2_4_0_2_gate_tables/CORE_0_0_0_0_2_4_0_2_gate_tables.md
super_node:
    name: gnu_c
    path: ../CORE_0_0_0_0_2_4_0_gnu_c.md
sub_nodes: []
---

# CORE 0_0_0_0_2_4_0_2 — gate_tables

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.gate_tables
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [gnu_c](../CORE_0_0_0_0_2_4_0_gnu_c.md)

## sub_nodes

*(none yet)*

## definition

Clang's C++ AST/LLVM gate-predicate and `derived_info` (`state_info[n]`)
lookup tables (`gate_tables.py`):

- **`PART_NAMES` and `INNER_READS`:** maps Clang C++ operand expressions and
  in-HiOp `derived_info` (`state_info[n]`) local variables (`SrcTy`, `SrcType`,
  `SrcEltType`, `SrcEltTy`, `InputSigned`, `DstTy`, `DstType`, `DstEltType`,
  `DstEltTy`, `OutputSigned`, `TInfo`, `UnderlyingType`, `PromoteType`,
  `ValType`, `AtomTy`, `IndexExpr`) to their operand index (`part`) and
  `outer` vs. `inner` (vector element / pointer pointee) level.
- **Clang `leaf_reading` rules:** maps C++ type/value/relational checks
  (`isIntegerType`, `isFloatingType`, `isVectorType`, `isPointerType`,
  `isa<...>`, `getAs<...>`, `PromotionType.isNull()`, `typesAreCompatible`,
  `elementSize.isOne()`, `hasSameType`, `hasAttr(attr::NoDeref)`, etc.) to
  `holder_facts.json` keys and `VALUE_FORMS`.
- **Branch classification tables:** `OPTION_NAMES` (compile flags such as
  `-fsanitize=...`, `-g`, `-std=gnu2x`), `LANGUAGE_NAMES` (non-GNU-C guards),
  `NOT_NEEDED_NAMES`, `CANNOT_REACH_NAMES`, `REFUSAL`, and
  `entry_info_unreachable` (branches fixed by the HiOp's own `state_info[0]`
  entry identity).
