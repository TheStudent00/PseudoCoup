---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.infra
level: 6
status: draft
settled_by: Dee
supersedes: null
designation: code (container)
node:
    name: infra
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_1_model_lang_parts/node_0_0_0_0_2_1_2_infra/CORE_0_0_0_0_2_1_2_infra.md
super_node:
    name: model_lang_parts
    path: ../CORE_0_0_0_0_2_1_model_lang_parts.md
sub_nodes: []
---

# CORE 0_0_0_0_2_1_2 — infra

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.infra
- **level:** 6
- **status:** draft
- **designation:** code (container)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [model_lang_parts](../CORE_0_0_0_0_2_1_model_lang_parts.md)

## sub_nodes

*(none yet)*

## definition

The infrastructure a language's Units call: code outside the HiOps that a
Unit calls into. Today that is compiler-rt's routines for riscv64: run
elv2_l159 lowered compiler-rt whole, and the 54 routines riscv64's Units
call reach 58 routines in all .

Dee, 2026-10-14 , the note this node comes from: "a
thought that came to mind is that `extract_lang_infrastructure` or
`extract_lang_infra` might make sense in the ontology since the work we did
was extracting vocabulary but also infrastructure and that extraction was
different because we lowered it (we can upgrade that extraction after we
build the new PseudoCoup)"

- It was the work list's `extract_lang_infra`; in Dee's tree of 2026-10-15
  it is this part.
- Nothing is in it yet. The record of that lowering is `hub/autopoly`'s
  `SUPPORT_gnu_c_infrastructure_lowered_whole.md`, which log 456 §6 said
  would move here.

Made 2026-10-15 in `map_HiOp_to_unit`'s `.NASCENT/`, at Dee's word: "please fill in the .NASCENT for `map_HiOps_to_unit` as best you can." Not live until the rework puts `.NASCENT`'s contents in place (PlanPlan `framework/PROTOCOL.md` §6d).

## support

- [SUPPORT_gnu_c_infrastructure_lowered_whole.md](SUPPORT_gnu_c_infrastructure_lowered_whole.md) — The compiler-rt routines riscv64's Units call, lowered whole and optimized (run `elv2_l159`).
