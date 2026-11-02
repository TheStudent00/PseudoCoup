---
id: hq.projects.pseudocoup.support.gnu_c_work_remaining
status: draft
---

# SUPPORT — gnu_c_work_remaining

What remains for GNU C, started over on 2026-10-13 with everything done
taken out , at Dee's word:

> i asked you to start the list over with the things we solved removed. im
> sick of scanning so many items and tracking a bunch of numbers.

The page beside this file,
[SUPPORT_gnu_c_work_remaining_in_python.html](SUPPORT_gnu_c_work_remaining_in_python.html),
shows the same on one small program; its list shows only what remains. The
record of every gap ever found stays in
[SUPPORT_gnu_c_vocab_what_is_missing.md](node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_extract_lang_vocab/SUPPORT_gnu_c_vocab_what_is_missing.md).

## What remains: one stable table

Since 2026-10-19 the standard progress view of GNU C vocabulary extraction,
both methods side by side out of one whole, lives in
`node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/.NASCENT/node_0_0_0_0_2_1_model_lang_parts/PROGRESS.md`,
Table 1 (Dee's word; . Table 1 below is the previous methods'
own table, kept as it stood.

Dee, 2026-10-16: "idk why we cant keep a stable table that i can look at to
know what progress is being made. we were trying to solve specific problems
which were gaps." Table 1 keeps the same rows from now on, and each time GNU
C's list is made again it gains a column.

Table 1. The problems being solved for GNU C's list. Every count is
operators, out of the 1,416 operators clang accepts with at least one choice
of holders (run elv2_l177). An operator is one builtin, expression or
statement as a program writes it, with its number of arguments:
`__sync_fetch_and_add(a, b)` and `__sync_fetch_and_add(a, b, c)` are two
operators of one builtin.

| problem | 2026-10-14 (run elv2_l166) | 2026-10-16 (run elv2_l177) | status |
|---|---|---|---|
| operators in the list | 1,178 | 1,358 | |
| left out: our check asked clang about one choice of holders, and clang made the same builtin at another size (`__sync_fetch_and_add_4` on a `char *` becomes the 1-byte add) | 165 | 0 | done 2026-10-16 (log 480) |
| left out: `extract()` had tried no holder clang accepts (`__c11_atomic_*` take a pointer to an `_Atomic`, and none of the 52 holders is one) | 15 | 0 | done 2026-10-16 for the builtins with custom typechecking (log 480) |
| left out: our check asked clang about one choice of holders, and clang made another operator, one the list holds under its own name (other languages' operators whose text is C's: C++20's rewritten `a * b` is C's `a * b`, `BinaryOperator` `Mul`) | 53 | 53 | nothing lost |
| left out: our check asked clang about one choice of holders, and clang made another operator; the operator written is lost (Table 2) | 5 | 5 | 3 already ruled: the compound literal by hand, `v.x` as `v[0]`, `fallthrough` by hand (gap list items 5 and 19); open: `__builtin_fpclassify`, `__builtin_invoke`, and statement attributes other than `fallthrough` |
| all operators clang accepts | 1,416 | 1,416 | counted as standard_HiOp_wrapper holds each text: GNU C's statement expression `({ a; })` and initializer list `{a}` are never accepted there (gap list items 5 and 11), so they are outside this whole |
| `extract()` makes its whole list again every run, and sets it beside the last one | not done | done in the code: every combination asked of clang again, the past answers only set beside the new ones (Dee: "until PseudoCoup is completed, i dont want to assume that our past answers are correct") | checked 2026-10-17 by run elv2_l178 (small: each pass's first 40 operators, run elv2_l177's answers as the past): 44,806 of 44,806 combinations asked again (pass a 2,971, b 36,051, c 5,784), all 44,806 answered as before, 0 changed |
| with three or more arguments, each holder the reader gives is tried once, not in every combination | | Claude's choice: every combination stopped run elv2_l174 | waits on Dee's word |
| the operators added since 2026-10-14 lowered to Units | | not lowered yet | waits on Dee's word |
| fusing `a * b + c` into one `fmadd.d` | later | later | Dee: "we will get it later when we find a way to optimize arch-opcodes" |

Changes to Table 1's rows, each with its reason:

- 2026-10-17: the row "all operators clang accepts" names its whole in its
  status: the operators clang accepts as standard_HiOp_wrapper holds them.
  Clang accepts GNU C's `({ a; })` and `{a}` inside a function and an
  initializer, and refuses every one of our programs holding them (gap list
  items 5 and 11). The counts are unchanged.

- 2026-10-16, second edit: the row "left out: ... clang made another
  operator" (58) is two rows, 53 + 5, since only the 5 lose anything; the
  row "the reader can't read which size clang picks for a `__sync` builtin"
  is out. The list doesn't need that reading: clang picks the size itself
  when it compiles each HiOp variant. The reading would matter for modelling
  `__sync`'s context from clang's code, which is not one of the list's
  problems.

Table 2. The 5 operators of Table 1's "lost" row: what a program writes,
what our list's text was, what clang made of it, and the cause.

| operator | C writes | our text | clang made | cause | status |
|---|---|---|---|---|---|
| `CompoundLiteralExpr` | `(int){5}` | `(T)a` | a cast, `CStyleCastExpr` | the reader writes the initializer without its braces | covered by hand (gap list item 5, at Dee's word of 2026-10-13) |
| `ExtVectorElementExpr` | `v.x`, `v.xy` (an element of an ext vector, by letter) | `a.m` | a member of a struct, `MemberExpr` | the reader writes a struct member's name where an element's letter goes | solved before as a complex HiOp: `v.x` is `v[0]`, the subscript the list holds on the same holder (gap list item 19, log 448, after Dee's "arent these complex HiOps?"); written "open" here on 2026-10-16 without that row read |
| `AttributedStmt` | `__attribute__((fallthrough));` | `a;` | the statement `a;` alone | the reader writes no attribute (its code calls `Attr->printPretty`) | `fallthrough`: by hand, the same instructions as without it (gap list item 19, log 447); clang's other statement attributes (`nomerge`, `musttail`, `likely`, ...): not ruled on |
| `__builtin_fpclassify` | `__builtin_fpclassify(0, 1, 4, 3, 2, x)` | the same | the assignment `p->result = (...)` | our check looks for the call where the standard form put it before log 424 | waits on Dee's word |
| `__builtin_invoke` | `__builtin_invoke(f, x)` | the same | the plain call `f(x)` | clang's check (`BuiltinInvoke`) builds the plain call in its place | waits on Dee's word |

Dee, 2026-10-16: "what is the abstraction for not dropping these?" Claude's
answer, waiting for Dee's word, two rules:

1. clang's acceptance alone decides what is kept. Our check records what
   clang built from each accepted signature, and never drops a signature for
   it; one text is one HiOp, so another language's name that writes a C text
   joins C's operator. It makes Dee's ruling for the `__sync` sizes general
   ("every signature clang accepts is a HiOp variant of the name written"),
   and it keeps `__builtin_invoke` and `__builtin_fpclassify`.
2. Every part clang's printer writes is a slot with a kind of its own, filled
   from clang's own list for that kind, as a value slot is filled from the
   holders. The reader knows three kinds today (a value or a type, from the
   holders; a name, `m` or `n`). The other three lost operators each have a
   part of another kind: a compound literal's initializer (an initializer
   list, `{a}`), an ext vector's element (its letters, `x`, `xy`, ...), and a
   statement's attribute (clang's attribute list).

2026-10-17: the three operators of rule 2 already have rulings: the compound
literal by hand (gap list item 5), `v.x` as the complex HiOp `v[0]` (item
19, log 448), and `fallthrough` by hand, the same as without it (item 19,
log 447). And rule 1 keeps all of the 1,416 by its own terms, while the
1,416 leave out what standard_HiOp_wrapper never lets clang accept (items 5
and 11). Dee, 2026-10-17: "okay prove it then" and "it feels like these
rules are a bunch of patch work"; the proof is being measured on clang's
own code .

Until 2026-10-16 this section's table had four rows, with no counts by
date: `extract()` making its whole list again, the signatures dropped by a
one-row check, `__builtin_fpclassify`'s HiOps dropped, and fusing. Each is
in Table 1; `__builtin_fpclassify` is now inside "another operator".

## What was done on 2026-10-16 (log 480)

- **The reader joined to `extract()`**, at Dee's word ("do it now"): for
  each builtin with custom typechecking, the holders its checking code accepts,
  read by `complex_signature_reader`, are tried, and clang accepts or refuses
  each. Table 1's third row.
- **Signatures dropped by a one-row check, kept**, at Dee's word of
  2026-10-15 ("if it works, then yeah sure"). Table 1's second row.
- **Clang's files read preprocessed** (run elv2_l173), and a fault that
  lost 101 of 902 expressions and statements found by run elv2_l176 and
  fixed: `assert(...)` is a cast to void once preprocessed (log 480 §5).

## What was done on 2026-10-15 (log 479)

- **Bit-fields, modelled as a context by automation** (log 479). A bit-field
  is a context, not a holder: clang keeps its width out of its type. clang's
  logic for each place, learned from `a + b`, predicts the IR it writes in
  3,126 of 3,126 functions, 1,001 of them with a bit-field. The bit-field
  place's riscv64 words, lowered alone and spliced in where a plain field's
  access stood, give C's value in 1,092 of 1,092 functions, 34,944 of 34,944
  inputs (runs elv2_l171, elv2_l172; `struct Q`'s three fields). At your word
  ("please update the project to include your work") the model is the
  project's code:
  [model_contexts](node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_8_model_HiOps/node_0_0_0_0_2_8_1_model_contexts/CORE_0_0_0_0_2_8_1_model_contexts.md),
  under `model_HiOps`, which writes the same spliced assembly as the runs, byte
  for byte, in 12 of 12 cases. Not yet run: other widths, positions, types and
  `unsigned` fields.

## What was done on 2026-10-14 (logs 456 and 457)

- **`extract()` in its node** (log 456; this heading said "The last tool in
  its place" until log 461: the trying code `extract()` calls is not in its
  place yet, Table 1). I moved `extract()` into the
  product. It reads clang's own lists through the product's readers and makes
  GNU C's grid; GNU C's own steps sit in `extract_lang_vocab/clang.py`, and
  `dict_of_lang_HiOps` writes a language's HiOps to a file. Run elv2_l166 made
  the grid twice the same day, once with the old script and once through
  `extract()`: clang's answers were the same, 2,088,155 of 2,088,155, in
  order, and so were the HiOps, 325,613 of 325,613.
- **The grid runs again** (log 456). Since log 424, every grid run had
  stopped on the 116 statements GNU C lacks (C++'s `try` and others), which
  `judge_pass` tries on purpose so that clang refuses them.
  `standard_HiOp_wrapper.roles_of` now gives those statements' parts R1's own
  roles, and `standard_HiOp_wrapper` writes the same text as before for the
  lowering's 322,610 HiOps.
- **The one-over of GNU C** (log 457): the page's program, the models in
  pseudo-code, and how stable they are across clang 19, 20, 21 and 22.
- **The explanations, rewritten** (logs 458 to 460), at Dee's critiques: the
  544 are types that `judge_holders` tried as GNU C's holders, and clang
  accepted 52; every card, log and list entry written today now names who
  does each step, defines its words, and gives each claim a second route
  (log 460 lists what changed).

## What was done late on 2026-10-13 (log 454)

- **Two of the three tools in their places** (log 454). Lowering and cutting
  every HiOp is `map_HiOp_to_unit`'s own loop, and the standard-form is
  `standard_HiOp_wrapper`'s own module. Every record came out the same as before,
  field by field: 322,610 of 322,610 on each of the three machines (run
  elv2_l162). So did every standard source: one digest over 322,610 HiOps and
  2,088,155 grid records.

## What was done late on 2026-10-13 (log 453)

- **The copy of `p` out of every Unit, as your log 440 says** (log 453).
  `p` is the standard function's one parameter: the address of the struct whose
  fields are the HiOp's holders. Each load of `p` left the Unit's words, and
  its place is kept ("from here, this register holds `p`"). Every Unit was cut
  again from run elv2_l156's records, with no compile: on riscv64 509,236 of
  3,981,370 Unit words came out, in 292,248 of 321,882 Units, exactly as
  counted beforehand (log 451), and nothing else changed. The Unit of `a + b`
  is log 440's 4 words: `c.lw c.lw c.addw c.sw`.
- **Five groups out, by your own rulings** (log 453): Apple-only routines
  and SafeStack's 4 are outside our configuration (log 446); `__trunctfbf2`,
  the 4 `_Float16`-with-`__int128` conversions and `__builtin_eh_return` are
  clang's own gaps (log 446: "thats on clang").
- **The trace's sort closed** (log 453): it was there to save modelling work
  (your words of 2026-09-30: "modelling the basic HiOps gives us the more
  complex HiOps essentially for free"), and every operator was lowered and
  cut anyway.

## What was done on 2026-10-13

- **Every GNU C HiOp lowered and cut, on all three machines** (run
  elv2_l156). The Unit is the words the debug table files under the HiOp's
  own line: on riscv64, 3,981,370 of 7,161,872 words; the rest is the frame
  and the arrival of `p`. On no machine does a Unit hold a word that opens a
  frame. 509,236 of those 3,981,370 words were clang's loads of `p`, which log
  440 puts out of the Unit; taken out later the same day, above. [extract_unit_from_LoHiOp](node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_3_extract_unit_from_LoHiOp/CORE_0_0_0_0_2_3_extract_unit_from_LoHiOp.md)
  is built.
- **The reader fixed, and checked over every HiOp** (run elv2_l156): on
  riscv64, 1,172 of 322,610 Units gained the words they had been missing, as
  predicted; on x86-64 and aarch64, none changed.
- **The C11 atomics, by hand** (run elv2_l158): 20 builtins in 37 held
  functions, lowered and cut on all three machines.
- **Declarations, by hand**:
  [the ledgerer's file](node_0_0_0_1_ledgerer/SUPPORT_gnu_c_declarations_by_hand.md),
  with riscv64's layout read back from clang (run elv2_l157; my 63
  predictions all held).
- **Other threads, by hand**:
  [autopoly's file](node_0_0_0_2_hub/node_0_0_0_2_0_autopoly/SUPPORT_riscv64_ordering_per_target_language.md),
  for all twelve languages.
- **compiler-rt lowered whole for riscv64, optimized** (run elv2_l159):
  [autopoly's file](node_0_0_0_2_hub/node_0_0_0_2_0_autopoly/SUPPORT_gnu_c_infrastructure_lowered_whole.md).

Block A. The old list's 40 items, and the 10 found since, where they stand
on 2026-10-14 (log 464). It counts; the names of what remains are in Table 1.

```
40  on the old list
├── 29  done: 9 when 2026-10-13 began, 19 during it,
│         and extract() written on 2026-10-14
├──  6  out: the all-three-architectures rule, our
│         configuration, and the C library's 2
├──  4  closed: the trace's sort
└──  1  later: fusing a * b + c
10  found since
├──  5  out: Apple-only routines, SafeStack,
│         and three of clang's own gaps
├──  1  done: the copy of p out of every Unit
├──  3  waiting for your word: Table 1's first
│         three rows
└──  1  off the list at your word: another clang
```
