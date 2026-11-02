---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.mask_maker
level: 5
status: draft
settled_by: the owner
supersedes: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.DRY_mask_maker
designation: code (module)
node:
    name: mask_maker
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_3_mask_maker/CORE_0_0_0_0_2_3_mask_maker.md
super_node:
    name: map_HiOp_to_unit
    path: ../CORE_0_0_0_0_2_map_HiOp_to_unit.md
sub_nodes: []
---

# CORE 0_0_0_0_2_3 — mask_maker

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.mask_maker
- **level:** 5
- **status:** draft
- **designation:** code (module)
- **settled_by:** the owner
- **supersedes:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.DRY_mask_maker

## super_node

- [map_HiOp_to_unit](../CORE_0_0_0_0_2_map_HiOp_to_unit.md)

## sub_nodes

*(none yet)*

## definition

A module, `mask_maker.py` (formerly `DRY_mask_maker.py`; DRY: Don't Repeat Yourself). It makes
`grid_mask_of_knowns`, the data structure: operators crossed with holders,
and the lowerer's verdict on every cell: accepted or refused. (A lowerer is a language's map from its HiOps to arch-units: in practice its compiler or interpreter.) Cells already known are carried over, so only the
rest go to the lowerer, and they go in bulk.

It records all the work already done, in both stages of `map_HiOp_to_unit`:
the verdict on each cell, and each cell whose arch-unit is already extracted.
So neither stage redoes a cell. the owner, 2026-10-05: "it also prevents one from
re-running cells that have already have extracted arch-units. its all the
work thats already been done -- hence, DRY". That is why it moved up that day
(log 361), from under `extract_lang_vocabulary` to beside it under
`map_HiOp_to_unit`. Code: `Projects/PseudoArch/map_HiOp_to_unit/mask_maker.py`.

    cells  = grid(operators, holders)      # one holder per operand slot
    known  = knowns(lang, cells)           # judged before: accepted or refused
    judged = judge(lang, cells - known)    # the lowerer, many cells per file
    mask   = known + judged                # every cell accepted or refused

A compiler reports each refusal by line; an interpreter raises it when the
cell runs. Either way the refusal is the lowerer's own testimony.

When a language changes, only the cells whose declarations changed are
judged again. That is also the answer to churn.

Since 2026-10-11  the standard-form's routing written in this module is read from the record of `HiOp_configuration_solver` (`ROUTING`, made by `routing_from_the_record`); the tables written by hand until then stay here as `INERT_PART_ROLES_BY_HAND`, `INERT_PART_EXPRESSIONS_BY_HAND`, `C_JUMPS_BY_HAND` and `C_STATEMENT_CONTEXT_BY_HAND` (`ROUTING_BY_HAND`), the check.

A cell is addressed by its position in the two lists, never by an
operator's spelling (the spelling ban).

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
- lowerer is a language's compiler or interpreter: what lowers a HiOp to a Unit
