---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.extract_unit_from_LoHiOp.progress
status: living
---

# PROGRESS — extract_unit_from_LoHiOp

- 2026-09-22: node created from the ontology in
  `Planning/CORE_0_0_0_pseudocoup.md
- 2026-10-09, observed, not decided (`Planning/CORE_0_0_0_pseudocoup.md §3.2): the debug line table that
  `-g` already puts in every object says which source line wrote each word.
  In a held source written with the HiOp on a line of its own, the HiOp's
  words can be picked out from its context's (a `break;` in a `switch`: one
  word under the break's line). Caveat seen in zlib: the table can file the
  next line's first word one line early.
- 2026-10-09, looked at, not decided (`Planning/CORE_0_0_0_pseudocoup.md
  §4): no sub-nodes. The CORE's definition is the 2026-09-22
  conversation's, not Dee's; Dee's own words are log 302 and the message of
  2026-09-18 ("the context removes the chaff during the slicing. that
  sliced/simplified lowered form is the arch-unit."), whose
  "sliced/simplified" meets Dee's 2026-10-08 rule, "an honest lowering, not
  a simplification". A draft of the extraction (log 405, Block D) and the
  past work, marked whose and whether it holds. Since log 405 a jumping
  HiOp's words hold the jump rule's test and skipped call, which the
  extraction must take off. PlanPlan development: Dee's call.
- 2026-10-09, Dee's words for its development, and my answer, not decided
  (`Planning/CORE_0_0_0_pseudocoup.md).
  Dee: "we are modelling HiOps. there is nothing to simplify"; "we still
  need to have placeholders that can be swapped out by other code"; "it
  cant just be a flattened extraction. it needs structure still"; and the
  abstraction over N `if`-`else` chains "is not found in the arch-units
  themselves". Log 406: a lowered placeholder is one call named by its
  relocation on all three architectures; the call goes, the part becomes a
  named unknown (not an identity); a Unit carries its placeholders and,
  for a body, where each way out lands; N lives in the program's tree and
  in induction. Of 307,820 kept HiOps, 34,874 hold placeholders; 268,240
  (riscv64) / 247,067 (x86-64) / 260,033 (aarch64) are straight-line.
- 2026-10-10, a correction to the entry above (`Planning/CORE_0_0_0_pseudocoup.md):
  its straight-line counts (268,240 / 247,067 / 260,033) are of the lowered
  words, the machine's level. At the held-form's level, the structure Dee
  means, 272,946 of the 307,820 kept HiOps hold no placeholder and 34,874
  hold placeholders, the same on all three architectures.
- 2026-10-12, Dee's words on the wrapper (`Planning/CORE_0_0_0_pseudocoup.md
  §2): "the function wrapper was only meant to contain the arch-opcodes
  associated with the HiOp ... its just for the sake of isolating the
  associated arch-opcodes." Log 437 asked whether the operands' fetches and
  the result's store count as the HiOp's own arch-opcodes.
- 2026-10-12, DECIDED at Dee's word
  (`Planning/CORE_0_0_0_pseudocoup.md):
  "if the answer being yes reduces work, i dont see why we wouldnt." It
  does: items 16 and 27 to 30 of the list close, and no prelude, epilogue or
  ledger of the September canon form has to be built. So a Unit is the
  HiOp's operand fetches, its operation and its result's store; the frame
  and the copy of `p` are cut. Instance, `op_1970` on riscv64: 4 of its 15
  words are the Unit (log 440, Table 1). The register that holds `p` when
  the Unit starts is read from the cut copy, not modelled.
- 2026-10-13, settled how, at Dee's question ("we need some way to tell which
  arch-opcodes belong to the lowered HiOp. is that not enough to settle this
  particular issue?"): the debug table names the source line of each word.
  Instance, run elv2_l154 (`Research/lower_HiOp/out/samples_l154/units.listing.txt`):
  `mean`'s 16 words fall 6 under its first line, `lw lw divw sw` under
  `int average = total / count;`, and 6 under the return. The held source
  writes each held function on one line today, so the HiOp moves to its own
  line. Asked of Dee, not started: a small run, then one wide run with item 23's fix
  (`Planning/CORE_0_0_0_pseudocoup.md
  §4).
- 2026-10-13, built and run , at Dee's "any work that you can
  complete now, do so please": `Projects/PseudoArch/map_HiOp_to_unit/extract_unit_from_LoHiOp.py`
  keeps the words the debug table files under the HiOp's own line, and the
  parts those words call. Run elv2_l156, every GNU C HiOp on all three
  machines: riscv64 3,981,370 of 7,161,872 words are Units' words (321,882
  lowered); x86-64 4,226,812 of 6,264,681 (321,641); aarch64 3,736,520 of
  5,574,608 (308,194). Every word has a source line; no Unit holds a word that
  opens a frame; a Unit holds a return only for a HiOp that leaves the
  function. Two errors of the check itself were corrected and the check read
  again (`Research/lower_HiOp/read_units_of_the_cut.py`). Status: done.
- 2026-10-13, late : the copy of `p` cut, as Dee's log 440
  says. The debug table files clang's loads of `p` under the HiOp's line, so
  the cut of log 449 kept them (found by Gemini, log 450; counted in log 451).
  `extract_unit` now takes each one out of the Unit's words and keeps its
  place in `Unit.holds_p` ("from here, this register holds `p`"), by machine
  (`ARRIVAL`: the register `p` arrives in, and the words that store and load
  it). Every Unit was cut again from run elv2_l156's records, no compile
  (`Research/lower_HiOp/cut_again_without_the_copy_of_p.py`): exactly log
  451's counts came out on all three machines (riscv64 509,236 of 3,981,370
  Unit words), nothing else changed. The Unit of `a + b` is log 440's 4
  words. Run elv2_l160 on the VM, once it was back: 12 of 12 checks passed
  (check 11: log 440's 4 words; check 12: `a++`, `p` in a2 then a1), and its
  records are the same as the laptop's. Status: done.
- 2026-10-26: Moved under `lower_HiOp` as `0_0_0_0_2_2_3_extract_unit_from_LoHiOp` in the `.NASCENT` rework of `map_HiOp_to_unit`.
