---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.progress
status: living
---

# PROGRESS — lower_HiOp

- 2026-09-22: node created from the ontology in
  `Planning/CORE_0_0_0_pseudocoup.md
- 2026-10-07: three sub-nodes created at the owner's word, from this node's own
  definition: `compile_held_source`, `read_words_at_symbol`,
  `map_words_to_LoOps` (`Planning/CORE_0_0_0_pseudocoup.md). The rejected run of 2026-09-26/27 had made
  four (`lower_by_compiling`, `lower_by_slicing`, `decode_word`,
  `decode_by_sail`), removed by the restore of 2026-09-27; none is carried.
- 2026-10-07, later: `map_words_to_LoOps` removed at the owner's word and moved to
  `.archive/map_words_to_LoOps_removed_2026-10-07/`. It read each word back
  into the Sail model's constructor, which the owner had already ruled out on
  2026-09-21 ("the mapping between arch-opcode and machine-opcode is
  1-to-1"). The two CORE paragraphs that carried that reading were removed
  with it. Two sub-nodes remain: the compile, and the words at the symbol
  read as arch-opcodes, which are the LoHiOp
  (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-07, later: coded fresh at the owner's word ("lets build `lower_HiOp` and
  test it"): `Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp.py`. Nine checks
  with known answers pass (runs elv2_l96 and elv2_l97). Then, at the owner's word,
  run over GNU C's HiOps (elv2_l97): 321,404 of 322,610 lowered, 1,206
  refused by clang, none missing a symbol; 4,478,799 words, every one read
  by name (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-08, elv2_l99: run again at the owner's word ("proceed with doing the
  runs again with these agreed compiler configurations"), with the optimizer
  off and the debug table on (`-O0 -g`, the owner's rule of the same day). The nine
  checks pass; 321,402 of 322,610 lowered, 1,208 refused by clang (the same
  1,206 as with `-O1`, and 2 more), none missing a symbol; 6,973,300 words,
  every one read by name. The `-O1` results moved to
  `Research/lower_HiOp/out/optimizer_on_2026-10-07/` (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-08, elv2_l101 to elv2_l105: every GNU C HiOp lowered for x86-64
  and aarch64 too, at the owner's word ("should we do find the parts that the
  lowerer supports across all the architectures? ... if you can proceed with
  doing the work, please proceed"). By the rule (kept: words of its own on all
  three, or only the frame's words on all three), 307,374 of 322,610 are
  kept. 14,028 that lower on riscv64 leave: 10,549 because riscv64's va_list
  is a plain `void *`, 3,145 in LLVM's aarch64 backend, 331 that do something
  on x86-64 only (all of `__builtin_eh_return`), 3 by plain char's sign. The
  480 refusals of ours are refused on all three
  (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-09, elv2_l108 to elv2_l110: every GNU C HiOp lowered again on all
  three architectures, in the held-form with inert parts. By the rule,
  307,782 of 322,610 are kept (307,374 before), 14,790 are out (14,756
  before), and 38 are refused because of our held source (480 before). The
  scratch space (`/work`, 4 GB) filled with clang's crash reports during
  elv2_l109's aarch64 run; elv2_l110 ran it again on the same code, and each
  compile run now gets its own folder for them. The Unit count in
  `Research/lower_HiOp/compare_three_architectures.py` fixed: a call counts
  by the name of what it calls, and no place in the file counts; riscv64 759,
  x86-64 1,564, aarch64 1,447 for the 34,877 kept control HiOps (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-09, elv2_l112: every GNU C HiOp lowered again with both corrections
  to the held-form. riscv64 321,882 of 322,610 lowered, x86-64 321,641,
  aarch64 308,194 (each 38 more than log 399); every refusal left is clang's
  or LLVM's. By the rule: 307,820 kept, 14,790 out, 0 ours (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-09, elv2_l113: every GNU C HiOp lowered again with the held-form
  matching log 404, and set beside its log 402 result HiOp by HiOp
  (`Research/lower_HiOp/compare_two_held_forms.py`): 508 / 508 / 473 of
  322,610 changed, all `return`, `goto *a;`, `continue;` and
  `__atomic_always_lock_free` HiOps; lowered 321,882 / 321,641 / 308,194,
  as in log 402. Kept control HiOps' Units, now counted from the results
  (they were read from log 397's trial files): 769 / 1,571 / 1,456 (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-11, `elv2_l143` : every GNU C HiOp lowered again on all three architectures with the held sources routed by the record of `HiOp_configuration_solver`; results beside log 405's, under names ending `_routed_by_the_record` (`Research/lower_HiOp/out/`), log 405's 15 files checked unchanged. Lowered 321,882 / 321,641 / 308,194, as in log 405; the same words as log 405 on all three for 320,760 of 322,610 HiOps (`Research/lower_HiOp/out/words_routed_by_the_record_beside_log_405.txt`); the 1,850 others: the `for` start's answer kept where its holder leaves words (aggregates, wide integers, `long double` and vectors; 1,751 HiOps of the 4 listings), `default` 52, `__builtin_fpclassify` 32, `goto *a;` 13, `goto m;` 1, `&&m` 1. Kept 307,819 (307,820): `&&m` is out because riscv64's words of it end after the frame. Found then, not fixed: on riscv64 no word read in either run computes an address from a local label (every `auipc` of 389,113 and 389,319 is a call's), so the reading most likely stops at such a label; log 405's `&&m` on riscv64 was 5 words too. Two faults of my comparison, fixed before the counts above: the run's work folder named in a refusal's words (5,689 HiOps read as changed at first), and that folder taken out only after a refusal is cut to 200 characters (1,861). Status: done.
- 2026-10-12, `elv2_l144` : why riscv64 reads `&&m` short. On riscv64 the object keeps a local label (`.Lpcrel_hi0`, `.Ltmp0`) where a function computes an address, the disassembler prints a header line for it inside the function, and `symbol_bodies` (`lower_HiOp.py` lines 270 to 283) starts a new function at every header line; so `read_words_at_symbol` keeps 5 of `&&m`'s 16 words (log 405's `&&m`: 5 of 12), and `goto *a;`, with no local label, keeps all 25. From the records alone (`Research/lower_HiOp/how_many_riscv64_Units_are_read_short.py`, writing `out/how_many_riscv64_Units_are_read_short.txt`): 1,170 of the 319,621 riscv64 Units the records can tell are read short in log 405, and 1,170 of 319,622 in log 424 (`__scoped_atomic_thread_fence` 1,155, `__builtin___NSStringMakeConstantString` 13, `__builtin_huge_valf16` 1, `__builtin_inff16` 1); 2,260 others cannot be told without the functions' sizes; aarch64 0 of 295,040. Status: open; the reader is unchanged, its fix waiting for the owner's word.
- 2026-10-13, late : `HeldSource` moved to
  `held_HiOp_wrapper.py`, as the note on it said it would once that node had
  a module; this module imports it from there, so `lower_HiOp.HeldSource`
  still names it. Nothing else here changed. Status: done.
- 2026-10-14 , at the owner's ask for "a set of small examples that
  makes the behavior of bit-fields and the problem observable":
  `SUPPORT_gnu_c_bit_fields_walk.py`, three statements on
  `struct Q { int a : 13; int b : 13; int r : 13; }` with `a = 1000`,
  `b = -7`, each Python line doing what clang's riscv64 words beside it do
  (run elv2_l146). `q->r = q->a + q->b` never takes `a` or `b` out of their
  bytes; `q->r = q->a / q->b` and `s_r = q->a + q->b` do. Checked by running
  clang's words on 64-bit registers for 19,999 random pairs: C's answer every
  time. Nothing in the product changed. Status: done.
- 2026-10-26: Gained `standard_HiOp_wrapper` (`0_0_0_0_2_2_0`) and `extract_unit_from_LoHiOp` (`0_0_0_0_2_2_3`), with `compile_standard_source` (`0_0_0_0_2_2_1`) and `read_words_at_symbol` (`0_0_0_0_2_2_2`) renumbered in between, per `.NASCENT/SUPPORT_migration_map.md`.
