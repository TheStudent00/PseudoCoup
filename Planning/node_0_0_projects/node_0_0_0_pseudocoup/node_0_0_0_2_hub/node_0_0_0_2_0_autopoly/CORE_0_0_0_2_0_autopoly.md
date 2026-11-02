---
id: hq.projects.pseudocoup.hub.autopoly
level: 4
status: draft
settled_by: Dee
supersedes: null
designation: code (container)
node:
    name: autopoly
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_2_hub/node_0_0_0_2_0_autopoly/CORE_0_0_0_2_0_autopoly.md
super_node:
    name: hub
    path: ../CORE_0_0_0_2_hub.md
sub_nodes: []
---

# CORE 0_0_0_2_0 — autopoly

## metadata

- **id:** hq.projects.pseudocoup.hub.autopoly
- **level:** 4
- **status:** draft
- **designation:** code (container)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [hub](../CORE_0_0_0_2_hub.md)

## sub_nodes

*(none yet)*

## definition

A LoOp is defined as a composition of primitives. Swap that
composition for the language's HiOpPrimitives — its Units that were
proven equal to those primitives — and the LoOp runs in that language.
Every LoOp emulated means every Unit emulated, which means every HiOp
emulated. That is the polyfill.

- What AutoPoly carries across languages is the UR-Node (Dee's
  `UniversalRichNode`, which log 302 places under both AutoPoly and the
  Ledgerer). Its design, locked by Dee on 2026-10-09, is defined once, in the
  ledgerer's CORE (`## design`): a HiOp variant with its Units, one per
  architecture, and their Lean terms. The polyfill is what makes a UR-Node's
  meaning the same in every language .

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant

## support

- [SUPPORT_riscv64_ordering_per_target_language.md](SUPPORT_riscv64_ordering_per_target_language.md):
  what each riscv64 word that orders memory promises other threads (fences,
  AMOs, LR/SC), and how each of the twelve languages keeps it at least as
  strongly, by hand. Dee, 2026-10-13, on the fence: "its more of an
  infrastructure thing no?" .
- [SUPPORT_gnu_c_infrastructure_lowered_whole.md](SUPPORT_gnu_c_infrastructure_lowered_whole.md):
  the routines riscv64's Units call, lowered whole and optimized for
  AutoPoly to run whole: compiler-rt done (run elv2_l159), the C library
  waiting on Dee's choice. Dee: "theyre self contained objects. they dont need
  to be split" (logs 448, 449).
