---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOp_configurations
level: 6
status: draft
settled_by: Dee
supersedes: null
designation: code (container)
node:
    name: HiOp_configurations
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_5_HiOp_configurations/CORE_0_0_0_0_2_1_5_HiOp_configurations.md
super_node:
    name: model_lang_parts
    path: ../CORE_0_0_0_0_2_1_model_lang_parts.md
sub_nodes:
    - name: dependent_HiOp_reader
      path: node_0_0_0_0_2_1_5_0_dependent_HiOp_reader/CORE_0_0_0_0_2_1_5_0_dependent_HiOp_reader.md
    - name: HiOp_configuration_solver
      path: node_0_0_0_0_2_1_5_1_HiOp_configuration_solver/CORE_0_0_0_0_2_1_5_1_HiOp_configuration_solver.md
---

# CORE 0_0_0_0_2_1_5 — HiOp_configurations

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.HiOp_configurations
- **level:** 6
- **status:** draft
- **designation:** code (container)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [model_lang_parts](../CORE_0_0_0_0_2_1_model_lang_parts.md)

## sub_nodes

- [dependent_HiOp_reader](node_0_0_0_0_2_1_5_0_dependent_HiOp_reader/CORE_0_0_0_0_2_1_5_0_dependent_HiOp_reader.md) — Reads from the lowerer's checking code where each dependent-HiOp (such as `BreakStmt`, `ContinueStmt`, `CaseStmt`, `DefaultStmt`, `ReturnStmt`) may stand and which depended-HiOp container (`SwitchStmt`, `WhileStmt`, `DoStmt`, `ForStmt`, function body) it requires.
- [HiOp_configuration_solver](node_0_0_0_0_2_1_5_1_HiOp_configuration_solver/CORE_0_0_0_0_2_1_5_1_HiOp_configuration_solver.md) — Finds each operator's held-form configuration (`N`-body statement patterns, depended-HiOp containers, and multi-template syntactic forms `operators_of(key)`) by testing arrangements on the lowerer and verifying them against `dependent_HiOp_reader` and `branch_trees`.

## definition

The syntactic and structural pattern each HiOp is held in:
- a HiOp with `N` bodies (`N = 0` is the HiOp alone; `if (a) b; else c;` has 2 bodies; `ForStmt (1..4 parts)` has optional init/cond/inc + body),
- a depended-HiOp with its dependent-HiOps inside (`break;` / `continue;` inside a loop; `case` / `default` inside `switch`; `goto *&&m; m:` for `IndirectGotoStmt` + `LabelStmt`), or
- multi-template syntactic forms of a single AST operator key (`operators_of(key)` in `enumerate_branch_candidates.py`, such as `MemberExpr` dot `a.m` vs. arrow `a->m`, `UnaryExprOrTypeTraitExpr` expression `sizeof a` vs. type `sizeof(T)`, and `GenericSelectionExpr` expression vs. type controlling argument).

Dee, 2026-10-10: "the correct held-form configuration (such as "HiOp with N
bodies")". The name is Dee's, 2026-10-15: "`model_lang_components ->
HiOp_configurations`?"

- `dependent_HiOp_reader` reads, from the lowerer's code, where each
  dependent-HiOp may stand.
- `HiOp_configuration_solver` finds each configuration (and feeds the
  language's `templates` in `lang_models/<lang>/templates`).
