---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.templates
level: 7
status: draft
settled_by: the owner
supersedes: null
designation: code (module)
node:
    name: templates
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/node_0_0_0_0_2_4_0_gnu_c/node_0_0_0_0_2_4_0_4_templates/CORE_0_0_0_0_2_4_0_4_templates.md
super_node:
    name: gnu_c
    path: ../CORE_0_0_0_0_2_4_0_gnu_c.md
sub_nodes: []
---

# CORE 0_0_0_0_2_4_0_4 — templates

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.templates
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

GNU C's standard-form C program wrapper templates (`operators_of(key)` and
`operator_candidates` in `templates.py`):

- Maps every GNU C operator key to its standard-form translation-unit template
  (`struct P_k { ... }; void op_k(struct P_k *p) { ... }`).
- Provides multiple syntactic templates (`operators_of(key)`) when a single
  Clang AST node can be entered via different C grammars (such as `MemberExpr`
  dot `a.m` vs. arrow `a->m`, `UnaryExprOrTypeTraitExpr` expression `sizeof a`
  vs. type `sizeof(T)`, and `GenericSelectionExpr` expression vs. type
  controlling argument) and compound-shape candidates (`operator_candidates`)
  for `counted_by` flexible array members, anonymous struct fields, `noderef`
  pointers, case ranges, and scoped atomic fences.
