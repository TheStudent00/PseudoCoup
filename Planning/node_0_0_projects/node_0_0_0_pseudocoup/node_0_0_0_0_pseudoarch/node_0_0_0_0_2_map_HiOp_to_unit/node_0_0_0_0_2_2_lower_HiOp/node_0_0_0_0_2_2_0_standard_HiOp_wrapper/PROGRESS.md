---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lower_HiOp.standard_HiOp_wrapper.progress
status: living
---

# PROGRESS — standard_HiOp_wrapper

- 2026-09-22: node created from the ontology in
  `Planning/CORE_0_0_0_pseudocoup.md
- 2026-10-07: the abstract design written into the CORE, at Dee's word
  (`Planning/CORE_0_0_0_pseudocoup.md
  §2 and §3). The state that day, by language:
  - GNU C: written, in `DRY_mask_maker.py`. Log 377 lowered 1,127 programs
    on riscv64, x86-64 and aarch64, and kept 1,115. 1,126 of the programs
    were written by `held_cell_lines`; the other one, `&&m` (the address of
    a label), was written by hand, since the grid holds no accepted variant
    of it.
  - C++: written, with the result stored (`decltype`).
  - Go, Rust, Java: written for the grid's syntax check, with the result in
    a local, so the result is not stored yet (the CORE's Block A, line 5).
  - Python: held as an object (`PythonHeld`) and run, for the grid.
  - C#, Dart, Swift, Ruby, PHP, JavaScript: not written.
  - Not checked: whether clang keeps anything of GNU C's 15 statements with
    the optimizer on, since a held statement stores no result
    (`while (p->a) p->b;` writes no field).
- 2026-10-07, measured by lowering GNU C's HiOps at `-O1` (elv2_l97;
  `Planning/CORE_0_0_0_pseudocoup.md):
  - The statements check: a held statement stores nothing, and of the
    321,404 lowered, 8,654 came out as nothing but the return. Most of them
    are statements: `if` 3,414 of 4,303, `{}` 2,257 of 2,757, `switch`
    1,040 of 1,196, `case` 1,035 of 1,144. `while` keeps its loop.
  - 37 variants refused for the held form itself: the result field takes a
    `const` type (`__builtin_align_up` and `__builtin_align_down` on a
    `const int`, 18 each; `__builtin_nondeterministic_value`, 1).
- 2026-10-08, elv2_l99, lowered again with the optimizer off (`-O0 -g`):
  of the 9,171 HiOps with no word of their own at `-O1`, 3,681 now have words
  (`if` all 3,414, `for` 156), and 5,489 still have only the function's frame
  (`{}` 2,257, `switch` 1,040, `case` 987, `default` 47, and builtins whose
  lowering is nothing). So the empty `if`s were the optimizer's; the empty
  `{}`, `switch`, `case` and `default` are the held form's: their parts store
  nothing, and clang writes no read for an expression whose value nobody uses
  (`CGExpr.cpp`, `EmitIgnoredExpr`). The 37 `const` refusals are unchanged
  (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-08, what is ours in the `-O0 -g` lowering (`Planning/CORE_0_0_0_pseudocoup.md):
  480 of the 1,208 refusals (37 a `const` result field; 442
  `__atomic_always_lock_free`, its size read from a field where clang needs a
  constant; 1 `__builtin_counted_by_ref`, no holder is a flexible array
  member), and 4,331 of the 5,489 HiOps with only the frame's words (the
  statements `{}`, `switch`, `case`, `default`, whose parts store nothing).
  Not started.
- 2026-10-08, Dee's idea tried, in research and not in the held-form's code
  (`Research/lower_HiOp/try_inert_parts.py`, elv2_l103 and l104): the 34,877
  control HiOps the three-architecture rule keeps, every part held as an
  inert call (a body as a void call, a value as a call returning the value
  read, a switch on a call with a case label). On riscv64, 32,023 have words of
  their own, 2,849 only their parts' calls (blocks, labels, most `return a;`),
  5 only the frame (`;`, `{ }`, `return;`, and `break;` and `goto m;`, whose
  held source puts the jump's target right after the jump). They come to 727
  different Units. Correction to the entry above: the frame-only HiOps of ours
  are 4,380, not 4,331; 49 had a jump to the next word as their only word
  (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-09, the inert parts moved into the held-form at Dee's word ("it
  seems like the new held-form is incredibly successful and would make sense
  to be in the project PlanPlan and its implementation"): the CORE states them
  as a rule, and `DRY_mask_maker.held_cell_lines` writes them. An operand GNU
  C needs as a constant is written as a zero of the value read from its
  holder (`CONSTANT_FORM`): `__atomic_always_lock_free`'s size, and a case
  label. Run on all three architectures (elv2_l108 to l110): the control
  HiOps lower as in the research node; the other 286,022 HiOps lower to the
  same words as before; 408 of the 442 `__atomic_always_lock_free` HiOps are
  kept, 34 are out with aarch64's va_list. Left that is ours: 38 refusals (37
  `const` result fields, 1 `__builtin_counted_by_ref`), and `break;` and
  `goto m;`, whose jumps still go to the very next word: what each was given
  to jump over is reached by no path and is not in the words. Correction to
  the entry above: the 34,877 come to 759 Units on riscv64, not 727 (my count
  left out what a call calls) (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-09, a look at Dee's word ("perhaps its worth having at look at it,
  in case it does reveal how we can model it with automation"), run elv2_l111,
  research only: the 40 HiOps of ours held by hand all lower on all three
  architectures. The 37 `const` results with the result field written
  `__typeof_unqual__` (one word): their words equal the same operators' on
  holders without `const`, 37 of 37 on each. `__builtin_counted_by_ref` needs
  a flexible array member and a use clang allows (its answer may not be
  stored), and writes no word of its own. `break;` and `goto m;` need code
  other paths reach between the jump and its target; with it, each is one
  jump. Nothing in the held-form changed (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-09, both corrections made at Dee's word ("okay go ahead and make
  both corrections to the held-form"), run elv2_l112: `break;` and `goto m;`
  behind an inert test with an inert call after them; the result field of
  `__builtin_align_up`, `__builtin_align_down` and
  `__builtin_nondeterministic_value` typed with `__typeof_unqual__`, for
  those three only; `__builtin_counted_by_ref` on a flexible array member,
  storing through its answer. None of GNU C's 322,610 HiOps is ours now: the
  38 refusals lower and are kept, `break;` and `goto m;` have words of their
  own; 322,570 of the other 322,607 HiOps have the same words as before (the
  37 that differ are the `const` ones, now lowered). The held-form written in
  Python, and CPython's compiler dropping a call no path reaches too: §4 of
  `Planning/CORE_0_0_0_pseudocoup.md
- 2026-10-09, a draft at Dee's word ("something like log 373 style ... do you
  want to try doing that for this held-form idea?"), no run, the plan
  unchanged: the held-form for any language, in log 373's form. Five steps the
  same for every language (hold each placeholder by its role; apply the HiOp;
  keep its answer; stand it where it can stand, with the jump rule and its
  contexts; write the held source), each language giving only a row of words.
  Writing it showed that `continue;` and `return a;` do not follow the jump
  rule yet (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-09, done, after Dee asked "should we not make `GNU-C` current with
  the most advanced design?": the GNU C code matches log 404's draft. Every
  statement that jumps (`C_JUMPS`) stands behind an inert test with an inert
  call after it: `continue;`, `goto *a;`, `return a;` and `return;` joined
  `break;` and `goto m;`. A constant operand has no field. Run elv2_l113: of
  322,610 HiOps only those five operators' changed (508 on riscv64 and
  x86-64, 473 on aarch64), none between lowered and refused, the same
  307,820 kept. Log 404 §2 is now
  [SUPPORT_held_form_for_any_language.md](SUPPORT_standard_form_for_any_language.md),
  at Dee's word, with four additions the code showed it needed
  (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-09, found, open, Dee's call (`Planning/CORE_0_0_0_pseudocoup.md
  §3.1): all 2,548 kept HiOps that take a memory order (the `__atomic`,
  `__c11_atomic`, `__scoped_atomic` builtins and the fences) branch on all
  three architectures, because the held-form reads the order from a field
  and clang then writes a choice among every order (CGAtomic.cpp line 1325).
  Real code passes a constant order and gets one form. The same kind of
  question as log 398's constant size.
- 2026-10-10: `SUPPORT_held_form_in_modelling_abstraction.md` added at Dee's
  word ("i would like it to be something i can navigate to from the PlanPlan
  web navigator"): the held-form in the context of modelling abstraction, in
  log 373's form, without the compiling details. A first draft for Dee to
  build on; its code runs. Status: draft, nothing ruled. It was first written
  as `Planning/CORE_0_0_0_pseudocoup.md, which now points here.
- 2026-10-10: `SUPPORT_held_form_in_modelling_abstraction.md` rewritten,
  much shorter, at Dee's word ("i need it way more simple than you just
  made. please try again."): six configurations drawn after Dee's sketch, no
  code. Status: draft, nothing ruled. The first draft is in git history.
- 2026-10-10: `SUPPORT_held_form_in_modelling_abstraction.md`, configuration
  3 corrected at Dee's message ("i think one of the things that really sets
  off alarm-bells for me is "otherwise" being very out of place"): it is now
  a depended-HiOp and its dependent-HiOp right after its body, an `if` and its
  `else`; the made-up word `otherwise` is gone. Status: draft, nothing ruled
  (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-10: `SUPPORT_held_form_in_modelling_abstraction.md`, configuration
  3 back to "a HiOp with two bodies", written with `else`, at Dee's word ("if
  the pattern for listed HiOps is "HiOp and two bodies" or "HiOp and N
  bodies", then we just need to model in that way"); the pattern holds in
  clang, CPython, Go's compiler and rustc. A line says configurations 1 to 3
  are one pattern, a HiOp with N bodies. Status: draft, nothing ruled
  (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-10: `SUPPORT_held_form_in_modelling_abstraction.md`, third draft,
  at Dee's word ("but `else` is not the abstraction is it?"; "currently you
  have "HiOp and two bodies" for only `else` and nothing in the
  configurations for "HiOp and N bodies""): configurations 1 to 3 became one,
  a HiOp with N bodies, written in Dee's notation `HiOp[0](...)` to
  `HiOp[N-1](...)`, with a table of instances (clang's `IfStmt`, `ForStmt`
  and others, CPython's `For`); the dependent-HiOp configurations are now 2
  to 4. Status: draft, nothing ruled.
- 2026-10-10: found, at Dee's question ("is the "HiOp with N bodies" category
  automate-able like the rest? ... if it requires by-hand, thats a
  problem"): which parts of a control HiOp are bodies comes from a table
  written by hand, `INERT_PART_ROLES` in
  `Projects/PseudoArch/map_HiOp_to_unit/DRY_mask_maker.py` (31 entries, keyed by
  each variant's C text). clang says it in its lowering code
  (`EmitStmt` for a body, `EvaluateExprAsBool` for a tested value); the
  write-back code agrees except on `for`'s step. Status: open; recommended,
  not started: read the bodies from clang and retire the table
  (`Planning/CORE_0_0_0_pseudocoup.md).
- 2026-10-10: reading the control HiOps' bodies from clang in place of
  `INERT_PART_ROLES`: planned at Dee's preference ("yes i would prefer to do
  so"), not started. Estimated at three steps, two reading files on the
  laptop and one tower run, with the hand table as the check: clang's
  write-back code agrees on 47 of the table's 54 parts, and two rules from its
  lowering code settle the other 7 (log 413 §5).
- 2026-10-10: Dee's meaning of automation: "our reading of lang_x's listed
  vocabulary and the routing of each listing to the correct held-form
  configuration (such as "HiOp with N bodies")". Against it, GNU C's routing
  is by code for the 1,107 of 1,127 operators in N = 0 (`HiOp(...)` alone),
  and by hand for the other 20 (the 19 control operators, in 31 variants, and
  `&&m`): four tables in `DRY_mask_maker.py` (`INERT_PART_ROLES`,
  `INERT_PART_EXPRESSIONS`, `C_JUMPS`, `C_STATEMENT_CONTEXT`), two code
  branches, and `&&m`'s held function in `run_elv3.py`. The estimate of log
  413 §5 covers `INERT_PART_ROLES` only. Status: automating the routing not
  started, not estimated (log 413, correction note and Table 3).
- 2026-10-11, part (b) of log 420 §4 at Dee's word ("proceed with part b"): GNU C's routing (which configuration each listing takes) is read from the record of `HiOp_configuration_solver` by `DRY_mask_maker.routing_from_the_record` (`ROUTING`, rules R1 to R7), and the held-form uses only it; the tables, branches and `&&m`'s two held functions written by hand stay as `*_BY_HAND`, the check. Entry by entry (`Research/lower_HiOp/out/routing_by_the_record_beside_the_hand_routing.txt`): roles 45 of 54 parts agree (the 9 others: the `for` start in 4 listings, a value now; 5 operands of the 4 expressions, bodies now, held as values are, since an expression hands its body's value on); jumps 5 of 5; contexts 3 of 6 (`goto m;` and `goto *a;` with their label holding an inert call, `default` before a case that holds nothing in place of after a case that breaks); `__builtin_fpclassify` now held with inert parts; `&&m` with its answer in a local and its label after it. 8,247 of 322,610 held sources change. Run `elv2_l143` (896 s, exit 0): 320,760 of 322,610 HiOps have the same words on all three as in log 405; the 1,850 others are all in those listings; none moved between lowered and refused; 307,819 kept, `&&m` no longer (its riscv64 words end after the frame; see `lower_HiOp`). Status: done, the change of routing awaiting Dee's reading .
- 2026-10-13, late , at Dee's word "okay lets move the tools
  into their places": this node has its module,
  `Projects/PseudoArch/map_HiOp_to_unit/held_HiOp_wrapper.py` (843 lines). GNU
  C's held-form moved into it from `DRY_mask_maker.py` line for line: 59
  statements, from `FIELD_ACCESS` to `flexible_array_lines`. Three changes:
  `held_cell_lines` is named `held_HiOp_wrapper`; the routing is always handed
  by the caller (`held_cell_lines`, a pass-through left in `DRY_mask_maker.py`,
  hands it `ROUTING`, the solver's routing, which also still sits there; log
  461); its
  error messages name this module. `HeldSource`, what this node hands to
  `lower_HiOp`, moved here from `lower_HiOp.py`, as the note on it said it
  would. Checked on the laptop, with no compile: every held source written
  before and after the move, as one digest, the runner's 322,610 HiOps and
  the grid's 2,088,155 records (13,139 of them raise, compared by their
  messages): `05824684…` both times. Status: done.
- 2026-10-14 : since log 424, `inert_parts` stopped with an
  error (in `routing.roles[...]`) on any statement that the solver's record
  doesn't hold, so no grid run could finish: 13,139 of the 2,088,155
  combinations `judge_pass` tries hold such a statement (C++'s `try` and
  `if consteval`, Objective-C's `@try`, and others GNU C refuses; clang had
  accepted none of them on 2026-10-06). I added `roles_of`, which gives such
  a statement's parts the roles R1 gives any placeholder the record doesn't
  list: a name for a placeholder that names something (`m` in `goto m;`), a
  value otherwise. I checked on the laptop: `held_HiOp_wrapper` writes the
  same text for the lowering's 322,610 HiOps (digest `1f90b1c6…`) and for
  the grid's other 2,075,016 combinations (`a7ccc691…`), and it now writes
  the 13,139. Status: done.
- 2026-10-15: node renamed `held_HiOp_wrapper` -> `standard_HiOp_wrapper` by `rename_node.py`. id changed with it (PROTOCOL §3 vs. `node-self-name` — see rename_node.py's own docstring): `hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.held_HiOp_wrapper` -> `hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.standard_HiOp_wrapper`.
- 2026-10-15: the held-form renamed the standard-form, at Dee's word ("okay
  as in make the change"). Dee: "held meant that the struct held onto the
  variable through the lowering process and resisted the optimizer. but we
  have the optimizer turned off and the debugger on." The two support files
  renamed with it: `SUPPORT_standard_form_for_any_language.md` and
  `SUPPORT_standard_form_in_modelling_abstraction.md`. The code: module
  `standard_HiOp_wrapper.py`, classes `StandardHiOp` and `StandardSource`,
  `compile_standard_source`; the plan's prose and the code's say
  "standard-form", "standard source" and "standard function". Dee's quoted
  words, this file's dated entries and the  logs keep the old name.
- 2026-10-26: Moved under `lower_HiOp` as `0_0_0_0_2_2_0_standard_HiOp_wrapper` in the `.NASCENT` rework of `map_HiOp_to_unit`.
