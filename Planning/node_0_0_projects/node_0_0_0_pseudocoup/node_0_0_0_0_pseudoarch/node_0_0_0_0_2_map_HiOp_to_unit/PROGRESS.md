---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.progress
status: living
---

# PROGRESS — map_HiOp_to_unit

- 2026-09-22: node created from the ontology in
  `Planning/CORE_0_0_0_pseudocoup.md
- 2026-10-13, late : GNU C's HiOps and Units are done:
  every HiOp lowered and cut on three machines, the copy of `p` out (log
  453). The loops that run this node's parts over a whole language are still
  research scripts (`Research/extract_lang_vocabulary/run_elv3.py`,
  `Research/lower_HiOp/lower_gnu_c.py`); each has its place in this plan
  (`extract_lang_vocab.extract()`, `dict_of_lang_HiOps`, this node's own
  entry). Dee, the same evening: "how about we continue solving GNU C first
  because its unclear if this mess is just going to keep getting worse and id
  rather not make the mess in the main-line." Moving them into their places
  is the next step whenever Dee chooses it.
- 2026-10-13, late , at Dee's word "okay lets move the tools
  into their places": this node's own loop is in the product,
  `Projects/PseudoArch/map_HiOp_to_unit/__init__.py`: `map_HiOp_to_unit(lang,
  held_HiOps, preamble, machine)` lowers and cuts many held HiOps at once,
  2,000 to a source, and splits a refused source until each refusal belongs to
  one HiOp (`map_batch`). It was the loop of
  `Research/lower_HiOp/lower_gnu_c.py`, moved as it was; the script keeps what
  a run decides (which HiOps, which machine, eight batches at a time, the
  records). The held-form moved into `held_HiOp_wrapper.py` the same turn (that
  node's PROGRESS). Checked by run elv2_l162 (elv2_l161 was cut short when the
  VM restarted): the 12 known checks, 12 of 12; one HiOp per operator beside
  elv2_l156's, 1,115 of 1,115 the same on each machine; every HiOp beside
  elv2_l160's records, field by field, 322,610 of 322,610 on each of the three
  machines. A refusal is compared by clang's words: the run's folder, the
  memory addresses in clang's crash reports and where the record's
  1,000-character cut falls change in every run, and the run's own comparison,
  which did not know that, first read 719, 697 and 3,838 refusals as changed
  (`Research/lower_HiOp/compare_records_whole.py`, fixed and run again on the
  laptop). Left of the three moves:
  `extract_lang_vocab`'s `extract()`, which fills `dict_of_lang_HiOps`
  (`Research/extract_lang_vocabulary/run_elv3.py` does it today). Status: two
  of three moved.
- 2026-10-14 : I moved the third tool into its place:
  `extract()`, with GNU C's own steps in `extract_lang_vocab/clang.py`; and
  `dict_of_lang_HiOps` writes a language's HiOps to a file (those nodes'
  PROGRESS). Corrected 2026-10-14 (log 461): this entry said "All three
  tools are in their places", which was false. The code that tries
  operators and holders in the lowerer (33 parts) and the held-form's
  routing (81 parts) still sit in `DRY_mask_maker.py`. `lower_gnu_c.py` keeps
  its HiOp list of 2026-10-06 for now: the dict that `extract()` made today
  differs from that list by two faults (log 456 §5), and fixing them changes
  which HiOps the lowering lowers, so the fix waits for Dee's word. Log 457
  measured how stable this node's Units are: runs elv2_l168 and elv2_l169
  had clang 20.1.8 and clang 22.1.2 lower every GNU C HiOp on riscv64, and
  set each Unit beside clang 21.1.8's: the same arch-opcodes for 318,135
  (clang 20) and 290,484 (clang 22) of 322,610. Clang 19.1.7's debug table
  files the frame's last words under the HiOp's line, so `cut` needs clang
  20 or later. Status: the move is not complete (log 461); the faults open.

- 2026-10-15: sub-node 7, `langs` (one sub-node per language, for each
  language's own parts of this node), made at Dee's word, with `gnu_c` under
  it . Nothing moved in yet.

- 2026-10-15: `.NASCENT/` opened in this node's folder, at Dee's word ("please fill in the .NASCENT for
  `map_HiOps_to_unit` as best you can"), by PlanPlan's `framework/PROTOCOL.md` §6d. It holds the new CORE,
  the new nodes (`model_lang_parts` and its six parts, `lang_models` → `go`) and
  `SUPPORT_migration_map.md`. Today's nodes stay live until the rework moves them; a node added, moved or
  deleted here meanwhile goes into the migration map too.
- 2026-10-26: Completed the `.NASCENT` rework of `map_HiOp_to_unit` ([SUPPORT_migration_map.md](SUPPORT_migration_map.md), PlanPlan `framework/PROTOCOL.md` §6d). Superseded nodes (`extract_lang_vocab`, `complex_signature_reader`, `langs`, `model_HiOps`) and the old `CORE` moved to `.archive/`; `model_lang_parts` (`0_0_0_0_2_1`) and `lang_models` (`0_0_0_0_2_4`, holding `gnu_c` and `go`) moved into place; `standard_HiOp_wrapper` (`0_0_0_0_2_2_0`) and `extract_unit_from_LoHiOp` (`0_0_0_0_2_2_3`) moved under `lower_HiOp` (`0_0_0_0_2_2`); `DRY_mask_maker` renamed to `mask_maker` (`0_0_0_0_2_3`). `.NASCENT/` removed.
