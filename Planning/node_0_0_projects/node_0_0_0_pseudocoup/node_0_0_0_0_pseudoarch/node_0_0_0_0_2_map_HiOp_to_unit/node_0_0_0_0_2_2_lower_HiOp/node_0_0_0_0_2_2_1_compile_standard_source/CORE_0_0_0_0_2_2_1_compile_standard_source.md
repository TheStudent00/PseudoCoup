---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.compile_standard_source
level: 6
status: draft
settled_by: Dee
supersedes: null
designation: code (function)
node:
    name: compile_standard_source
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_2_lower_HiOp/node_0_0_0_0_2_2_1_compile_standard_source/CORE_0_0_0_0_2_2_1_compile_standard_source.md
super_node:
    name: lower_HiOp
    path: ../CORE_0_0_0_0_2_2_lower_HiOp.md
sub_nodes: []
---

# CORE 0_0_0_0_2_2_1 — compile_standard_source

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.compile_standard_source
- **level:** 6
- **status:** draft
- **designation:** code (function)
- **settled_by:** Dee
- **supersedes:** null

## super_node

- [lower_HiOp](../CORE_0_0_0_0_2_2_lower_HiOp.md)

## sub_nodes

*(none yet)*

## definition

The standard source becomes an object file. The language's compiler compiles
it for riscv64 with the optimizer off and the debug table on, and the object
holds the standard function's machine words.

Refuses when the compiler refuses the source: the language declines the
HiOp (`lower_HiOp`'s first refusal). The refusal keeps the compiler's own
words.

The optimizer is off. Dee, 2026-10-08: "we want an honest lowering, not a
simplification ... the default is no optimizer for all lowerings where we are
trying to extract the arch-units. im not saying that its unacceptable to use
the optimizer under any circumstance but it needs to be justified and stated
explicitly before doing so."

The debug table is on, so each word can be traced to the field it reads.
Dee, the same day: "debug as a default might be a good rule to have.
obviously if its going to cause full memory/disk or tasks to take days, i want
to understand before."

For GNU C the compile is
`clang -std=gnu17 -O0 -g --target=riscv64-unknown-linux-gnu -nostdlibinc -ferror-limit=0 -c`:

- `-O0`, the optimizer off, and `-g`, the debug table on;
- `-std=gnu17`, GNU C, the dialect the grid checked the standard sources in
  (`DRY_mask_maker.JUDGE_COMMAND["c"]`);
- no `-march`, because our target is clang's own riscv64 default;
- `-ferror-limit=0`, so clang lists every error, not only the first 19.

Each language is one row: its compiler and its flags.

Corrected 2026-10-08: until then this definition said "with the optimizer on"
and gave `-O1`, "because the held-form exists for the optimizer". That was my
reading, against Dee's process (`Planning/CORE_0_0_0_pseudocoup.md,
third correction).

Written 2026-10-07 by Claude (Opus 5.5), at Dee's word ("yes as long as it
makes sense for the current context of the project"), from `lower_HiOp`'s
own definition. The wording is mine (`Planning/CORE_0_0_0_pseudocoup.md).

*notes:*

- LoOp is shorthand for lower-operator, equivalent to arch-opcode
- HiOp is an operator variant native to a language, with its holders
- Unit is the ArchUnit: the lowered, sliced form of one HiOp variant
