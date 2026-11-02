---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.holders.accepted_signatures
level: 7
status: draft
settled_by: the owner
supersedes: null
designation: code (module)
node:
    name: accepted_signatures
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_1_holders/node_0_0_0_0_2_1_1_1_accepted_signatures/CORE_0_0_0_0_2_1_1_1_accepted_signatures.md
super_node:
    name: holders
    path: ../CORE_0_0_0_0_2_1_1_holders.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_1_1 — accepted_signatures

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.holders.accepted_signatures
- **level:** 7
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [holders](../CORE_0_0_0_0_2_1_1_holders.md)

## sub_nodes

*(none yet)*

## definition

Queries the lowerer's own AST and IR type predicates (`type_answers(t)` and
`llvm_type_answers(t)` in `accepted_signatures.py`) on every candidate holder
in the language's pool (both on the outer type and on `.inner` vector/array
elements and pointer pointees) to produce the precomputed `holder_facts.json`
table.

Because `holder_facts.json` records the lowerer's exact boolean and integer
answers for every gate predicate (`isIntegerType`, `isSignedIntegerOrEnumerationType`,
`isUnsignedIntegerType`, `isFloatingType`, `isComplexType`, `isVectorType`,
`isExtVectorType`, `isExtVectorBoolType`, `isPointerType`, `isFunctionPointerType`,
`isRecordType`, `isUnionType`, `isAtomicType`, `isBitIntType`,
`isPromotableIntegerType`, `PromotionType.isNull`, `elementSize.isOne`, LLVM
IR type predicates, bitwidths, etc.), `branch_trees.py` can evaluate any gate
chain in microseconds in pure Python without guessing how the lowerer
classifies a type.
