---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.gnu_c.support.gnu_c_vocab_what_is_missing
status: draft
---

# SUPPORT — gnu_c_vocab_what_is_missing

GNU C's vocabulary, the dict's keys for GNU C, is complete at Dee's word of
2026-10-07:

> that is a pretty definitive answer. i think we can confidently move on. a
> dozen polyfilled by-hand is nothing. more than manage-able (especially if
> those are stable in `GNU-C`).
>
> lets consider `GNU-C` vocab extraction complete (with a note of what is
> missing for maintenance and thoroughness in general)

This file is that note. Written 2026-10-07 by Claude (Opus 5.5). The account of
the day is PCHQ  log 381. Every gap carries a status: open, excluded by
a rule, or outside the vocabulary. The file is kept current: when a gap closes,
its row changes in the same edit.

Items 12 to 26 (§2b) were added on 2026-10-12 (log 431), items 27 and 28 the
same day from run elv2_l145 (log 432), and items 29 and 30 from runs
elv2_l146 and elv2_l147 (log 433), with §2c, the items under the two filters, and items 31 to 34
the same day from clang's source and log 405's lowered HiOps (log 434), and items 35 to 38 from
comparing clang's remaining lists, runs elv2_l148 and elv2_l149 (log 435), and item 39 and the end of item 26 from runs elv2_l150 and elv2_l151 (log 436): the gaps found after
2026-10-10 that had gone into logs and not here, and what a comparison with
clang's other lists found. From 2026-10-12, a gap is added here the turn it is
found, and the chat names its item number. Item 40 was added on 2026-10-13 (log 443). Items 16 and 27 to 30 were closed
the same day at Dee's yes: a HiOp's operand fetches and result store are its
own words, so the words that vary with a holder's place sit inside one Unit
(log 440).

**The work that remains: `Planning/node_0_0_projects/node_0_0_0_pseudocoup/SUPPORT_gnu_c_work_remaining.md`,
started over on 2026-10-13 with everything done taken out (log 449, at Dee's
"i asked you to start the list over with the things we solved removed"),
with a page that shows each problem once on one small program in Python's
syntax beside it (log 445).** This file stays the record of each item; items
41 to 45 were added on 2026-10-13 (log 449), and Table 2h gives every item's
status that day; item 46 was added the same evening (log 451), from Gemini's
review (log 450).

GNU C here is clang 21.1.8 compiling `-std=gnu17` (Dee, 2026-10-05: the C that
industry writes). Paths are from `~/Programming/PRIVATE/PseudoCoup/`.

## 1. What is complete

- **The list** (log 367): 1,127 operators that clang accepts as GNU C for
  riscv64 and reads back as written. 81 are expressions and statements, and
  1,046 are builtins (2 of them under their own expression kinds,
  `ShuffleVectorExpr` and `ConvertVectorExpr`).
- **Lowered on all three major architectures** (log 377): 1,115 of the 1,127.
  The other 12 are left out by that rule (Table 2, item 8).
- **Classes, from the trace of which callee sent each message** (log 379), over
  the 1,115: simple 103, hybrid 57, complex 894, undetermined 61.
  103 + 57 + 894 + 61 = 1,115.
- **Holders and the grid** (log 367): 52 of 60 holders kept. The grid accepts
  309,454 operator-holder pairs for 1,114 of the 1,115 operators. The other
  one, `AddrLabelExpr` (`&&m`, a label's address), is asked on its own, in a
  function that has the label.
- **Against real code** (log 380): in zlib 1.3.1, Lua 5.4.7, SQLite 3.46.0,
  curl 8.11.1 and CPython 3.13.15's core, 99.977% of the operator uses are of
  operators the trace classified.

What that number leaves out, and why it matters for transpiling. Dee,
2026-10-07: "why does it matter? ... whats the problem?"
- It counts operators only. Declarations, such as `int n = 0;`, are not
  operators in GNU C's list, so they were never counted.
- A transpiled function needs them. In `int n = 0; n = n + 1; return n;` the
  vocabulary covers `=`, `+` and `return`, and nothing makes `n`.
- The five code bases hold 44,083 declaration statements in 18,681
  functions, about two per function.
- My reading: a declaration with a value is the holder, plus a store into it.
  Clang makes that store with the same function as `=`,
  `EmitStoreThroughLValue` (`clang/lib/CodeGen/CGDecl.cpp` line 794 for
  `int n = 0;`, `clang/lib/CodeGen/CGExprScalar.cpp` line 5127 for `n = 0`).
  If so, a declaration is built from what is classified: complex, and
  autopoly builds it. Not traced.
- It does not stop the Units of the 1,115 operators from being made. But a
  transpiled function needs its declarations: without them nothing makes `n`.
  (Corrected 2026-10-12, log 432. The first wording, "It does not hold up GNU
  C's Units", was reassurance where a flag belonged; log 412 §3 named it.)

Table 1. The same count three times over. Each entry holds one number.

| what is counted | uses | uses not classified | share classified |
|---|---|---|---|
| A. operators, as log 380 counted | 1,310,611 | 303 | 99.977% |
| B. A, and 6 library builtins | 1,310,762 | 454 | 99.965% |
| C. B, and the 4 forms | 1,360,453 | 50,145 | 96.314% |

- A's 303 uses are item 1's 12 builtins.
- B adds item 3's 151 calls, to `fprintf`, `fopen` and four more.
- C adds item 5's 49,691 uses of declarations and the other three forms.

## 2. What is missing, by cause

Table 2. Each gap, its size, its cause and its status. Items 1 to 7, and 11,
are gaps in the vocabulary. Items 8 to 10 are kept here so the whole sits in
one place.
The numbers behind each size are in the bullets under the table.

| item | what | size | cause | status |
|---|---|---|---|---|
| 1 | builtins the five code bases use that the list lacks: `__builtin_va_start` (what `va_start` becomes); nine `__c11_atomic_*` (what `<stdatomic.h>` becomes): `_load`, `_store`, `_exchange`, `_compare_exchange_strong`, `_compare_exchange_weak`, `_fetch_add`, `_fetch_sub`, `_fetch_and`, `_fetch_or`; `__atomic_compare_exchange_n`; `__builtin_assume_aligned` | 12 builtins | the test program could not write them: they need an operand no holder in the grid gives, such as a pointer to an `_Atomic` holder or a real `va_list` (log 367, Table 3) | open. Dee, 2026-10-07: polyfill them by hand. Their stability is §3. Unlocked 2026-10-12 (run elv2_l146, log 433 §3): written with the address of a holder in a place, constant orders and alignment, and a standard function taking `...`, all 12 compile on all three architectures; not yet held and lowered 2026-10-13 (log 444): a HiOp to hold and lower for riscv64 (`map_HiOp_to_unit`); what it promises other threads is item 34. 2026-10-13 (log 446): later, by hand, as Dee ruled on 2026-10-07; log 445's page had shown it as open. 2026-10-13 (log 447), Dee's correction: by hand now, "later potentially by modelling" (log 446 had written "later, by hand"). 2026-10-13 (log 449): done by hand: held with item 2's 8 in 37 functions, the order a holder and again written as seq_cst, lowered and cut on all three machines (run elv2_l158, `Research/lower_HiOp/samples_l157/`). |
| 2 | the other members of item 1's families, which the five do not use: `__c11_atomic_init`, `_fetch_xor`, `_fetch_nand`, `_fetch_max`, `_fetch_min`; `__atomic_compare_exchange`, `__atomic_test_and_set`, `__atomic_clear` | 8 builtins | as item 1 | open; the same fix as item 1 2026-10-13 (log 444): as item 1. 2026-10-13 (log 446): later, by hand, as item 1. 2026-10-13 (log 447), Dee's correction: by hand now, "later potentially by modelling" (log 446 had written "later, by hand"). 2026-10-13 (log 449): done by hand, with item 1 (run elv2_l158). |
| 3 | library builtins the list lacks that the five call: `fprintf`, `fopen`, `fwrite`, `fread`, `vfprintf`, `_setjmp` | 6 builtins | not checked. My reading: an operand no holder gives (`FILE *`, `jmp_buf`) | open. Their meaning is in libc in any case (item 10). 2026-10-13 (log 446): next, in the agreed run (log 444 Table 3): the C library's code, lowered once. 2026-10-13 (log 447): settled (Dee: "this is settled then yes?"): the C library's code is lowered once in the agreed run; its system calls are by hand per target language. 2026-10-13 (log 448), Dee's plan for the infrastructure: "theyre self contained objects. they dont need to be split. so the entire thing can be optimized in its lowering and emulated": each routine lowered whole, with the optimizer (a literal program, Dee's rule of 2026-10-09), and AutoPoly emulates its LoOps; only `ecall` meets the target language, by hand. 2026-10-13 (log 449): waits on Dee's choice of C library; my recommendation, musl (autopoly's `SUPPORT_gnu_c_infrastructure_lowered_whole.md` §3). 2026-10-13 (log 452): later, with AutoPoly: GNU C's HiOps and Units do not need the C library; a transpiled program needs it when it runs. Which library is Dee's choice then. 2026-10-14 (log 464): out, at Dee's word, asked twice: "why do we need the C library is we are covering GNU-C?" (01:53 UTC) and "the C library? excuse me? why is that on the list" (19:08 UTC). GNU C's HiOps don't need it: the call is the HiOp, and its Unit is cut. |
| 4 | the rest of the builtins clang marks for every language that the list lacks: HIP and OpenCL atomics (for GPU languages), scoped atomics, and others | 101 builtins | not sorted into GNU C or not | open |
| 5 | forms the list does not name: declarations (`int n = 0;`), initializer lists (`{1, 2}`, with the zeros clang fills in), compound literals (`(struct point){1, 2}`), and `__func__` | 4 forms | the operator reader leaves declarations out of `c.json`, and the test program cannot write the others (log 367 §2.4) | open: covered as data by log 385's 22 rules (2026-10-07; rules 4 to 16), not yet joined to the Units. Run elv2_l145 (log 432): `int n = 7;` lowers to the same words as `n = 7;` on all three architectures, and `static int n = 7;` is data, with no words 2026-10-13 (log 444): the ledger's (`ledgerer`): declarations and first values are what a program declares. 2026-10-13 (log 446), at Dee's word: later, by hand: "i thought we solved declarations like ten times by now ... we can model that by-hand and pick it up later potentially once PseudoCoup is actually up and running". Settled before in logs 382, 383, 385, 432 and 433. 2026-10-13 (log 447), Dee's correction: by hand now, "later potentially by modelling" (log 446 had written "later, by hand"). 2026-10-13 (log 449): done by hand: the ledgerer's `SUPPORT_gnu_c_declarations_by_hand.md`, log 385's 22 rules and the declarations named since. |
| 6 | classes that change with the holders: one holder set was traced per operator | not counted | a class goes with the holders (log 374, item 1) | open 2026-10-13 (log 449): my recommendation, close: every kept HiOp is lowered and cut whatever its class, so the sort decides nothing the product needs. 2026-10-13 (log 452): my recommendation is now later, not closed: the sort is Dee's design (`HiOp_sorter`), and its loose ends matter again when something uses which operators are built from which. 2026-10-13 (log 453): closed. Dee's words of 2026-09-30 (log 319) give the sort's job: "modelling the basic HiOps gives us the more complex HiOps essentially for free"; every operator was lowered and cut anyway, so nothing is left for it to save. |
| 7 | traced programs whose messages were printed by opcode only, so their `main_call_key`s are coarser | 7 programs | the printing of the message's text failed for them (log 379) | open 2026-10-13 (log 449): my recommendation, close, as item 6. 2026-10-13 (log 452): my recommendation, later, as item 6. 2026-10-13 (log 453): closed, as item 6. |
| 8 | operators not lowered on all three architectures | 12 operators | the rule of 2026-10-01: model only what lowers on every major architecture | excluded by that rule |
| 9 | the product's code: `extract()` in `Projects/PseudoArch/map_HiOp_to_unit/extract_lang_vocab/__init__.py` raises `NotImplementedError`, and research scripts make the vocabulary (§4) | 1 function | | open (log 368, W1 and W6) 2026-10-13 (log 449): my recommendation: write it once, when the next language starts, with GNU C's research results as its check; D3's label set is superseded by the routing read from the record (log 424). 2026-10-13 (log 453): with the tools into their places in the plan, once GNU C is done (Dee: "how about we continue solving GNU C first ... id rather not make the mess in the main-line"). 2026-10-14 (log 456): done, at Dee's word "lets do it": `extract()` written once, for any language, with GNU C's own steps in `extract_lang_vocab/clang.py`; GNU C's grid made through it the same day is the old grid, 2,088,155 of 2,088,155 verdicts and 325,613 of 325,613 HiOps (run elv2_l166). 2026-10-14 (log 461): the trying code `extract()` calls still sits in `DRY_mask_maker.py`, item 50. |
| 10 | functions the five call but do not define: the C library, POSIX, and CPython's own in `Modules/` | 271 functions | not vocabulary: their meaning lives in libc and the kernel | outside the vocabulary. The next limit on what transpiles (log 380 §6). 2026-10-13 (log 446): next, in the agreed run: the C library's functions lowered once; a system call is where the emulation meets the environment. 2026-10-13 (log 447): settled: the C library is GNU C, lowered once; system calls, where the emulation meets the environment, are by hand per target language (log 447 Table 1). 2026-10-13 (log 448), Dee's plan for the infrastructure: "theyre self contained objects. they dont need to be split. so the entire thing can be optimized in its lowering and emulated": each routine lowered whole, with the optimizer (a literal program, Dee's rule of 2026-10-09), and AutoPoly emulates its LoOps; only `ecall` meets the target language, by hand. 2026-10-13 (log 449): compiler-rt lowered whole (item 32); the C library waits on Dee's choice. What it must provide, by group: autopoly's `SUPPORT_gnu_c_infrastructure_lowered_whole.md` Table 1 (297 routines, 49 `float128`, 23 `_Float16`, 18 checked copies, `__riscv_flush_icache`, BlocksRuntime's 2). 2026-10-13 (log 452): later, with AutoPoly, as item 3. 2026-10-14 (log 464): out, at Dee's word, asked twice: "why do we need the C library is we are covering GNU-C?" (01:53 UTC) and "the C library? excuse me? why is that on the list" (19:08 UTC). GNU C's HiOps don't need it: the call is the HiOp, and its Unit is cut. |
| 11 | GNU's statement expressions: `({ a; })` and `({ a; b; })`, a block whose last statement gives the value | 2 variants | the grid's test program wrote them at file scope: every try refused, "statement expression not allowed at file scope" (13 of 13 and 169 of 169; `mask/gnu17/pass_a_forms.json`) | open: a test program that writes them inside a function (log 413 §1). 2026-10-13 (log 445, run elv2_l154): written inside a function, `int k = ({ int t = n * 2; t + 1; });` lowers on riscv64 (8 words), so the fix named here works. 2026-10-13 (log 447): closed. Held by hand inside a function (run elv2_l155): on all three machines `({ p->a; p->b; })` lowers to the last statement's read, a copy through a stack slot, and the store, all HiOps we have; the grid's refusals were our test program's, which asked the result's type outside the function. |

- Item 1: 303 uses in the five code bases.
- Item 3: 151 calls: `fprintf` 82, `fopen` 32, `fwrite` 24, `fread` 11,
  `vfprintf` 1, `_setjmp` 1. Checked 2026-10-10 (log 413 §1): the grid
  refused the library `setjmp` family as "call to undeclared function" (they
  need `<setjmp.h>`), and `__builtin_setjmp` and `__builtin_longjmp` as "not
  supported for the current target": clang lowers those only where
  `hasSjLjLowering()` holds, not on riscv64 or aarch64, so they are out by
  the all-major-architectures rule.
- Item 4: 12 HIP atomics, 13 OpenCL atomics, 24 scoped atomics and 52
  others. The 52 hold GNU C extensions the five do not use
  (`__builtin_object_size`, `__builtin_expect_with_probability`,
  `__builtin_isfpclass`, `setjmp`, `longjmp`) and ones for other targets
  (`__builtin_ptrauth_*`, `__builtin_cpu_is`).
- Item 5: 49,691 uses in the five: declarations 44,083; initializer lists
  3,232, with 1,510 zeros filled in; compound literals 552; `__func__` 314.
- Item 6: real code uses 14,241 operator-holder sets, and the grid accepts
  309,454 operator-holder pairs. Instance: `CStyleCastExpr` (72,173 uses) and
  `ReturnStmt` (33,612 uses) sent nothing on their traced programs, but a
  cast from `int` to `long` sends a `sext`.
- Item 10: 63 are builtins in the list, classified as a library call; 192
  are libc and POSIX functions, 6 of them item 3; 16 are CPython's own.
  63 + 192 + 16 = 271.

Item 4's numbers, from `Research/extract_lang_vocabulary/vocabulary/c.json`
(clang's builtins for C and C++, 1,254 names) against the list:
- 1,044 names are in the list as calls, and 2 under their own expression kinds;
- 70 `__sync_*` names are in it under the size clang picks from the holder
  (`__sync_add_and_fetch_1` on an `int *` comes back as
  `__sync_add_and_fetch_4`; log 367 §2.2);
- 138 are not: 127 marked for every language (items 1 to 4:
  12 + 8 + 6 + 101), 10 for C++ only, 1 for C23 only.
- 1,044 + 2 + 70 + 138 = 1,254. The 138 are log 367's "138 have no call form
  accepted at all".

## 2b. Gaps found after 2026-10-10 (added 2026-10-12, log 431)

Compared on 2026-10-12, beyond log 380's operators and log 411's keywords
(log 431 §6.2): clang's expression and statement kinds (`StmtNodes.td`), its
declaration kinds (`DeclNodes.td`), its type kinds (`TypeNodes.td`), its
conversion kinds (`OperationKinds.def`), the kinds of place its code reaches a
holder in (`CGValue.h`, `CGExpr.cpp`), and its driver's floating-point
default. Item 26 names what is not compared yet.

Table 2b. Each gap, its size, its cause and its status.

| item | what | size | cause | status |
|---|---|---|---|---|
| 12 | holder contexts: every holder is in one kind of place, an address computed from a pointer (`p->a`) | 5 of the 6 kinds of place never held (log 431, Table 2) | the standard-form's one shape | not waiting for Dee (corrected 2026-10-13, log 443). The old status, "open: the contexts' design waits for Dee (logs 426 to 431)", was left stale after the logs that settled it: log 431 (Dee: "the number of runs is actually within reason"), log 433 (the model of places checked at Dee's "okay do it"), log 437 (mapping work, not a model), log 440 (the fetch and store words are the HiOp's own) and log 442 (a place changes the words, never the value: 13,026 of 13,026 functions). What remains is mapping work: lowering HiOps with their holders in the other kinds of place, where the product needs those Units' words. Measured by run elv2_l145 (log 432) on three architectures: each kind of place gives its own fetch and store words; a `static` inside a function lowers as a global; a symbol that may live in another file goes through the global offset table |
| 13 | names (`DeclRefExpr`): a variable's, a function's or an enum constant's name; clang picks a holder's place under it (log 429) | 1 expression kind | not an operator in GNU C's list; the standard-form names no holder | open: its data side is log 385's rule 1; its words are item 12's 2026-10-13 (log 444): the ledger's: a name is where the ledger keeps a holder. 2026-10-13 (log 446): closed, nothing to model: a name is where the ledger keeps a holder, and the ledger fills it in when it is built (Dee: "i dont see where the problem is"). |
| 14 | constants as operands: integer, floating, character, string and imaginary (`5i`) literals, and the null pointer constant | 5 expression kinds, 1 conversion | the standard-form reads every operand from a field | open; its data side is log 385's rule 2. Measured by run elv2_l145 (log 432): the constant changes the operation's own word on all three architectures (`a + 5` is `c.addiw a0, 0x5`, `addl $0x5, %eax`, `add w8, w8, #0x5`) 2026-10-13 (log 444): the ledger's, my reading: a constant is a value the ledger passes; `a + 5` means `a + b` with `b` = 5, the same value in other words (`addiw`). 2026-10-13 (log 447): closed at Dee's "sure": a constant is a value the ledger passes. |
| 15 | `a * b + c` and `a * b - c` on floating types (and `+=`, `-=` with a product): clang writes one fused multiply-add at every optimization level; riscv64 and aarch64 use one instruction, our x86-64 baseline two, so the last bit can differ between them | 4 operators, each with a `*` inside | clang's driver turns floating-point contraction on by default (`clang/lib/Driver/ToolChains/Clang.cpp` line 2810; `clang/lib/CodeGen/CGExprScalar.cpp` lines 4364 to 4373) | open: composing `*` and `+` does not give these words. Measured by run elv2_l145 (log 432) at `-O0`: `fmadd.d` on riscv64, `fmadd` on aarch64, `mulsd` then `addsd` on x86-64; written as two statements, two words on all three. 2026-10-13 (log 446), at Dee's word: later: "no, leave it. we will get it later when we find a way to optimize arch-opcodes." The Units compose `*` and then `+`. |
| 16 | x86-64 folds a fetch into the operation's own word (`op_1970`: `addl 0x4(%rax), %ecx`) | 1 architecture | an x86-64 arithmetic instruction can read memory | closed 2026-10-12 (log 440), at Dee's yes: "if the answer being yes reduces work, i dont see why we wouldnt". The fetches of a HiOp's operands and the store of its result are its own words, so the varying words sit inside one Unit; no model needed. Before that: open: `extract_unit_from_LoHiOp` cannot simply cut the fetch words there. Measured by run elv2_l145 (log 432): the add reads its second operand from the stack, a global, or through a pointer. 2026-10-12 (log 437): no model needed. Dee: the wrapper only isolates the HiOp's own arch-opcodes; on my reading (asked in log 437) the fetch is the HiOp's own, so the folded word is simply part of the Unit |
| 17 | type kinds never sampled: arrays without a size (`int a[];`), sized at run time (`int a[n];`), functions without a prototype (`int f();`, whose call promotes its arguments) | 3 of GNU C's 14 type kinds | the 34 samples took other kinds | open. 2026-10-13 (log 446): later, by hand, on my reading of Dee's declarations ruling (item 5): its three kinds are made only by declarations (`int buf[n];`, `extern int a[];`, `int f();`). Clang lowers `int buf[n];` fine: its words move the stack pointer (run elv2_l154). 2026-10-13 (log 447), Dee's correction: by hand now, "later potentially by modelling" (log 446 had written "later, by hand"). Dee: "okay" to 17 going with declarations. 2026-10-13 (log 449): done by hand, with item 5 (the ledgerer's file, Table 2). |
| 18 | conversions never seen: `(void)a`, a null pointer constant, a function used as a pointer | 3 of clang's 69 conversion kinds, and 2 unsure | `void` is not a holder type; names and constants are not held | open. 2026-10-13 (log 447): closed, nothing to model (run elv2_l155): `p->result = f;` is `f`'s address through a relocation; `(void)p->a;` writes no instruction; `p->result = 0;` is a constant. |
| 19 | expression and statement kinds never asked, beyond items 5 and 11: `asm`, `__builtin_choose_expr`, `__builtin_LINE()` and the like, `__FUNCTION__` and `__PRETTY_FUNCTION__`, designated initializers (`.m = a`), `v.x` on an extended vector, `__attribute__((fallthrough));` | 7 kinds | the operator reader leaves `asm` out; the test program cannot write the rest (log 367 §2.4) | open; `asm` holds one machine's text, so my reading is that the all-major-architectures rule leaves it out. 2026-10-13 (log 446): `asm` is out by the all-three-architectures rule, at Dee's word ("if its not accepted in all three architectures, then its not a problem we need to solve"); the designated initializer is an initializer list, so it goes with declarations (item 5; my reading). Open: `__builtin_choose_expr`, `__builtin_LINE()`, `__FUNCTION__`, `v.x` on a vector and `fallthrough`, one update to the standard-form. 2026-10-13 (log 447): by hand (run elv2_l155): `__builtin_choose_expr(1, a, b)` writes the same instructions as `a`, and `fallthrough` the same as without it; `__builtin_LINE()` is a constant; `__FUNCTION__` the same as `__func__` (declarations); `v.x` and `v.w` on an extended vector are real HiOps, held and lowered by hand on all three machines. 2026-10-13 (log 448): solved, retracting log 447's "by hand" (Dee: "arent these complex HiOps?"): `v.x` is `v[0]`, the subscript on the same holder with the constant 0, and `a[b]` on the extended vector `ev4si` is among the kept HiOps (23 variants, log 424's run). |
| 20 | declarations beyond item 5's `int n = 0;`: functions, struct and union layouts (field offsets, padding, bit-field packing), enums, typedefs, labels and `__label__`, `_Static_assert`, file-scope `asm`, members of anonymous structs and unions | 12 declaration kinds | declarations are not operators | open; their data side is log 385's rules 4 to 13 (2026-10-07); log 427 quotes Dee: "type-declarations could be modelled later, perhaps closer to the ledgerer" 2026-10-13 (log 444): the ledger's, as Dee said in log 427. 2026-10-13 (log 446), at Dee's word: later, by hand (item 5's ruling). 2026-10-13 (log 447), Dee's correction: by hand now, "later potentially by modelling" (log 446 had written "later, by hand"). 2026-10-13 (log 449): done by hand: the ledgerer's file; riscv64's layout read back from clang (run elv2_l157): 65 of 65 rows, 63 of 63 predictions held. |
| 21 | the function around each HiOp: its frame, each architecture's calling convention (where arguments and results go), variadic functions | 10 of `op_1970`'s 15 riscv64 words | `extract_unit_from_LoHiOp`'s draft cuts the frame as "the frame's" (log 405 §4.3) | open: no node models it. Measured by run elv2_l149 (log 435): 24 of the 52 holder types are passed or returned differently on the three machines (riscv64 sign-extends 32-bit values, `unsigned int` too, and aarch64 extends none; x86-64 splits `__int128` in two; riscv64 passes GNU vectors in integer registers; complex types are passed differently on each machine), and `__fp16` cannot be passed at all on riscv64 and x86-64 (item 35) 2026-10-13 (log 444): the frame is cut (Dee's yes, log 440); a call inside a Unit follows riscv64's convention inside the emulation; the other machines' conventions matter only for the all-three-architectures rule. 2026-10-13 (log 446): settled how, at Dee's question ("we need some way to tell which arch-opcodes belong to the lowered HiOp. is that not enough to settle this particular issue?"): the debug table names the source line that wrote each word, so the Unit is the words under the HiOp's line, with the HiOp on a line of its own in the standard source. Instance (run elv2_l154): `mean`'s line 20 holds `lw lw divw sw`. Next. 2026-10-13 (log 449): done: the cut by the debug table (`extract_unit_from_LoHiOp.py`), every HiOp on all three machines (run elv2_l156); no Unit holds a frame-opening word on any machine. |
| 22 | relocations: words the linker fills in (globals, labels, thread-locals, the global offset table) | not counted | the Units keep the relocation lines | open: what they mean for the Lean step is not modelled 2026-10-13 (log 444): not a model of the machine. A relocation names a part (log 406), a routine (log 437) or a label; where a global lives is the ledger's. 2026-10-13 (log 446): closed, nothing to model: a relocation is a blank the linker fills; in the emulation the ledger fills it, and in the Lean term it is a named unknown (log 406's rule for a part's call). |
| 23 | the riscv64 reader ends a function at a local label, so Units are read short | log 424 §7 | `symbol_bodies` in `Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp.py` | open: waits for Dee's ruling. Fixed 2026-10-13 at Dee's word ("yes proceed with the fixes", log 445): a header line opens a new function only for a name the symbol table gives a size above 0 (`opens_a_function`). Small run elv2_l153, one variant per operator: on riscv64, 5 of 1,115 Units gained their missing words, each keeping the old ones first (`&&m` 5 to 16; the four builtins of log 424 Table 7); on x86-64 and aarch64, 1,115 of 1,115 unchanged, as predicted. The wide run over every HiOp waits for Dee's read. 2026-10-13 (log 449): done: the wide run held its prediction on all three machines (run elv2_l156): 1,172 of 322,610 riscv64 Units gained words, the old ones first; none changed on x86-64 or aarch64. |
| 24 | log 379's record of the read of a holder (`LValueToRValue`) is the standard-form's own `=` | 1 operator | one of its roots is clang's general `Visit` (log 430 §4.3) | open: waits for Dee's word 2026-10-13 (log 449): my recommendation, close, as item 6. 2026-10-13 (log 452): my recommendation, later, as item 6. 2026-10-13 (log 453): closed, as item 6. |
| 25 | builtins with an operand clang leaves unread, not sorted yet | 31 builtins | log 431 §4 | open 2026-10-13 (log 449): my recommendation, close, as item 6. 2026-10-13 (log 452): my recommendation, later, as item 6. 2026-10-13 (log 453): closed, as item 6. |
| 27 | bit-fields: riscv64 and aarch64 merge a field's extraction into the operation, so the field's fetch is not words of its own there (riscv64 adds the raw word, then masks; aarch64 `add w10, w8, w9, asr #25`); x86-64 keeps the parts apart | 2 of 3 architectures | the backend combines them even at `-O0` | closed 2026-10-12 (log 440), as item 16. Before that: open: the model of places has to carry it (run elv2_l145, log 432). Measured by run elv2_l146 (log 433): of 1,092 functions with a bit-field per machine, riscv64 predicts 830, x86-64 954, aarch64 732 (all its misses in thread-local functions, item 30). 2026-10-12 (log 437): no model needed if the operands' fetches and the result's store are the HiOp's own words (asked): the words that vary sit inside one Unit, and a transpiler never rebuilds a program's machine code from Units 2026-10-13 (log 442, run elv2_l152): the 760 functions whose words the model of places missed for this cause all give the predicted values on 4 pairs of inputs each (riscv64 262 of 262, x86-64 138 of 138, aarch64 360 of 360). |
| 28 | aarch64 reads the thread pointer once per function (`mrs x9, TPIDR_EL0`), and every thread-local access in it shares that word | 1 of 3 architectures | the backend reuses the read | closed 2026-10-12 (log 440), as item 16. Before that: carried by the model (log 433): aarch64 selects every thread-local function with SelectionDAG (item 30), which reads the thread pointer once. 2026-10-12 (log 437): no model needed, as item 27 |
| 29 | x86-64's division and shifts tie operands to fixed registers (`%eax` and `%edx`; the count in `%cl`), so moves appear or not by where the other holders live | 200 of 4,342 functions not predicted (run elv2_l146) | the machine's instructions | closed 2026-10-12 (log 440), as item 16. Before that: open (log 433 §1, Block A). 2026-10-12 (log 437): no model needed, as item 27 2026-10-13 (log 442, run elv2_l152): the 200 x86-64 functions whose words the model missed for this cause all give the predicted values (200 of 200). |
| 30 | aarch64 picks its instruction selector per function: GlobalISel, or SelectionDAG when the function touches a thread-local, so a HiOp's aarch64 words depend on what else is in its function | 91 of 91 thread-local functions fall back, and no other, in the `int_add` case (run elv2_l147) | clang's backend for aarch64 at `-O0` | closed 2026-10-12 (log 440), as item 16. Before that: open: what else makes GlobalISel fall back is not mapped (log 433 §1). 2026-10-12 (log 437): no model needed, as item 27 2026-10-13 (log 442, run elv2_l152): the 72 aarch64 thread-local functions whose words the model missed all give the predicted values (72 of 72). |
| 31 | the same HiOp gives different values on the three architectures, because clang's description of each machine makes the holder different: plain `char` is signed on x86-64 and unsigned on riscv64 and aarch64; `long double` is the 80-bit x87 float on x86-64 (64-bit significand) and the 128-bit IEEE float on riscv64 and aarch64 (113-bit significand); `wchar_t`, the type of `L'x'`, is `int` on x86-64 and riscv64 and `unsigned int` on aarch64; `va_list` is three different types. Instance: `op_37449`, `a + b` with a plain `char` and an `int`: x86-64 reads the byte with `movsbl` (sign-extended), riscv64 with `c.lbu` and aarch64 with `ldrb` (zero-extended), so the byte 0xC8 plus 1 is -55 on x86-64 and 201 on the other two | 38,465 of the 307,820 kept HiOps hold a plain `char` (13,938) or a `long double` of either form (25,203); 676 hold both | clang's description of each machine: `TransferrableTargetInfo` (`clang/include/clang/Basic/TargetInfo.h` lines 89 to 209); `char`'s sign in `isSignedCharDefault` (`clang/lib/Driver/ToolChains/Clang.cpp` line 1175); `long double` in `clang/lib/Basic/Targets/X86.h` line 196, `AArch64.cpp` line 161, `RISCV.h` line 44 | open: which machine's value a translation keeps is not decided. Met before only in part: log 397 left out 3 builtins over `char`'s sign, and log 370 met `long double` as a call. The all-three-architectures rule keeps these HiOps, because it checks that they lower, not that they agree (log 434). Dee, 2026-10-12, defined a faithful AutoPoly: "coding components of any GNU-C program has polyfill that is computationally equivalent", and "i would settle for just RISCV". My reading: each machine's own value is the meaning, and polyfills are made per machine, so nothing has to be reconciled; the facts per machine are read from clang's macros (run elv2_l149; log 435). 2026-10-12 (log 437): each machine's own words carry its values; no model needed 2026-10-13 (log 444): nothing to decide for the product: the plan emulates riscv64's LoOps (one model, RISC-V's), so riscv64's own facts are the meaning; the other machines' facts matter only for the all-three-architectures rule. |
| 32 | HiOps whose words call a routine of the compiler's runtime library where the machine has no instruction for the holder (`__addtf3`, `__divti3`, `__muldc3`, `__extendhfsf2` and the like): the Unit's meaning is in that routine's code, not in its words. Instance: `op_38159`, `a + b` on `long double`: riscv64 `call __addtf3`, aarch64 `bl __addtf3`, x86-64 no call (`fldt`, `fldt`, `faddp`, `fstpt`) | 119,861 of the 307,820 kept HiOps call one on at least one architecture: 51,241 on all three, 68,620 on one or two; the other 187,959 call none | LLVM writes the call after clang, for a holder the machine has no instruction for (log 370 §3.3) | open: the routines are written in C (compiler-rt), so they can be lowered like any other C, but nothing joins them to the Units. Met in log 370 Point 3 and log 372, never listed; counted by `Research/lower_HiOp/count_calls_to_runtime_routines.py` into `Research/lower_HiOp/out/calls_to_runtime_routines.txt` (log 434). 2026-10-12 (log 437): no model of LLVM's routines (Dee: map each building block straight to its low level). The called routine's words are part of the block's low level, and each routine is mapped once: 151 of LLVM's on riscv64, 200 on x86-64, 148 on aarch64. 2026-10-13 (log 446): no modelling problem (Dee: "it gets lowered and it works correct?": yes). compiler-rt is C, lowered once, and its words go with each call to it. Next, in the agreed run. 2026-10-13 (log 447): Dee: "would that not count as a complex HiOp?" In substance yes: its meaning is the routine's code; the trace called `+` simple from `int` holders (item 6). The routine is infrastructure: compiler-rt is C, lowered once (log 447 Table 1). 2026-10-13 (log 448), Dee's plan for the infrastructure: "theyre self contained objects. they dont need to be split. so the entire thing can be optimized in its lowering and emulated": each routine lowered whole, with the optimizer (a literal program, Dee's rule of 2026-10-09), and AutoPoly emulates its LoOps; only `ecall` meets the target language, by hand. compiler-rt's builtins are C (181 files; 4 small assembly files for riscv64), plain operators on `__uint128_t`, `__builtin_clzll`, and two inline instructions for the rounding mode (`frrm`, `csrsi fflags`). 2026-10-13 (log 449): done: compiler-rt lowered whole for riscv64, `-O2 -g` (run elv2_l159): 155 of 159 files; the 54 routines the Units call reach 58; running them whole is AutoPoly's part. |
| 33 | where C gives no result, the three machines give different ones, and nothing marks the inputs where C gives one. Instance: `a / b` with `b` = 0: riscv64 gives -1 (`~/Programming/SOURCES/sail-riscv/model/extensions/M/mext_insts.sail` line 59), x86-64 stops the program with a divide error (`~/Programming/SOURCES/X86-64-semantics/semantics/x86-mint-wrapper.k` lines 776 to 778), aarch64 gives 0 (Arm's manual; not checked) | not counted | C's own rules: division by zero, signed overflow, out-of-range shifts and float-to-integer conversions out of range have no result in C | open: clang's own list of these conditions is `clang/include/clang/Basic/Sanitizers.def` (62 entries: `integer-divide-by-zero` line 100, `signed-integer-overflow` line 115, `shift-base` line 112, `float-cast-overflow` line 97); with `-fsanitize=undefined`, clang writes each check as code before the operation (my reading; not run) (log 434). Under Dee's definition of 2026-10-12 (item 31), my reading is that a machine's own answer is the meaning, which leaves three cases (log 435): a value of its own needs nothing more (float to `int` out of range or NaN: riscv64 0x7FFFFFFF, x86-64 -0x80000000, Arm 0x7FFFFFFF and 0 for NaN, per Berkeley SoftFloat's per-machine files, `RISCV/specialize.h`, `8086-SSE/specialize.h` and `ARM-VFPv2/specialize.h` in `~/Programming/SOURCES/sail-riscv/dependencies/softfloat/berkeley-softfloat-3/source/` lines 57 to 59); a trap needs a model of traps and signals; whatever was already there (a local read before anything wrote it) waits for Dee's word. The 19 checks of clang's group "undefined" name the operations 2026-10-13 (log 444): its first two cases are in the LoOps already: Sail's definitions (riscv64's divide gives -1 and never traps; float-to-integer per SoftFloat's RISC-V file). A bad address is the one trap left, where the emulated memory ends. Its third case is the ledger's: what a holder holds before its first write, Dee's definition. 2026-10-13 (log 446): closed. Its third case, at Dee's word ("could we not initialize to zero?"): the ledger gives a holder declared without a value 0, and a comparison with riscv64's own run accepts any value of the holder's type. 2026-10-13 (log 447): Dee: "if clang or whatever is allocating space without initializing to zeroes, we will do so." |
| 34 | what an atomic HiOp promises other threads: a fence changes no register and no memory in the thread that runs it, so its whole meaning is what other threads may see, and each machine writes it differently. Instance: `op_98915`, `__atomic_thread_fence(a)` with the order read from a `bool`: riscv64 writes `fence r, rw`, `fence rw, w`, `fence.tso` or `fence rw, rw` by the order; aarch64 `dmb ishld` or `dmb ish`; x86-64 nothing for three of the four orders, and `lock orl $0x0, -0x40(%rsp)` for the strongest | the kept fences (34 per machine for `__atomic_thread_fence` alone) and every kept HiOp that takes a memory order (2,548 in log 406 §3.1); items 1 and 2 join them | the three machines order memory differently; x86-64 keeps most orders without a word | open: a Unit read as a change to registers and memory makes every fence nothing at all. My reading, not checked: Sail's Lean output follows one thread (log 434) 2026-10-13 (log 444): the one machine item left, `hub/autopoly`'s: what the fence, AMO and LR/SC LoOps promise other harts (RVWMO). Sail's definitions follow one hart. 2026-10-13 (log 446): next, in the agreed run (log 444 Table 3: RVWMO, with herd7's RISC-V model). 2026-10-13 (log 447): infrastructure, at Dee's question ("its more of an infrastructure thing no?"): by hand, per target language, the target's own threads ordered at least as RVWMO orders them; it leaves the agreed run's herd7 part (my answer, log 447 §5). 2026-10-13 (log 449): done by hand: autopoly's `SUPPORT_riscv64_ordering_per_target_language.md`, all twelve languages; the c row is clang's own mapping (run elv2_l158), the other eleven my reading. |
| 35 | what one machine accepts and the others refuse: `__fp16` as a parameter or a result (aarch64 only: "parameters cannot have __fp16 type" on riscv64 and x86-64, run elv2_l148); `_BitInt(N)` wider than 128 bits (x86-64 only: `__BITINT_MAXWIDTH__` is 8,388,608 there, 128 on the other two); `__float128` (x86-64 only, `__FLOAT128__`); the address spaces `__seg_fs` and `__seg_gs` (x86-64 only) | 4 constructs | clang's description of each machine: `HalfArgsAndReturns` (`clang/lib/Basic/Targets/AArch64.cpp` line 146), `HasFloat128` (`X86.h` line 635) | out by the all-three-architectures rule, named so they cannot surprise (log 435) |
| 36 | layouts that differ per machine: aarch64 aligns a struct to its unnamed bit-fields (`struct { char a; int : 0; char b; }` is 5 bytes on riscv64 and x86-64, 8 on aarch64; 5 of the 10 bit-field structs sampled differ); `_BitInt(128)` aligns to 16 on aarch64 and 8 on the others; `__builtin_va_list` is 8, 24 and 32 bytes; x86-64 aligns global arrays of 16 bytes or more to 16 | 4 rules | clang's description of each machine: `UseZeroLengthBitfieldAlignment` (`AArch64.cpp` line 188), which `clang/lib/AST/RecordLayoutBuilder.cpp` lines 1772 to 1777 apply to every unnamed bit-field ("Anonymous members don't affect the overall record alignment, except on targets where they do"); `LargeArrayMinWidth` and `LargeArrayAlign` (`X86.h` lines 743 and 744) | open: log 385's layout rules have no column per machine (item 20). Measured by run elv2_l149 (log 435) 2026-10-13 (log 444): the ledger's, riscv64's layouts only; the other machines' matter only for the all-three-architectures rule. 2026-10-13 (log 446): later, by hand, with declarations (item 5's ruling); riscv64's layouts only. 2026-10-13 (log 447), Dee's correction: by hand now, "later potentially by modelling" (log 446 had written "later, by hand"). 2026-10-13 (log 449): done by hand, riscv64's layout only (run elv2_l157): the zero-width bit-field struct is 5 bytes, alignment 1. |
| 37 | a program's own build flags change GNU C: `-funsigned-char` (`char`'s sign), `-fshort-enums` (an enum's size), `-fpack-struct` (layouts), `-fwrapv`, `-fstack-protector` (frame words and calls to `__stack_chk_fail`), `-ffp-contract=off` (item 15), and the machine's extensions; the Units are lowered with clang's defaults only | 329 language options, not sorted | clang's language options (`clang/include/clang/Basic/LangOptions.def`), most of them set by a flag | open: which flags a program was built with is part of what it means. Not checked against the five code bases' own build files (log 435). The compiling machine's installed tools count too: on aarch64 Linux, clang turns on outline atomics when it finds compiler-rt or a GCC of 9.3.1 or newer (`clang/lib/Driver/ToolChains/Linux.cpp` lines 775 to 786), and then every atomic HiOp becomes a call to one of LLVM's 100 `__aarch64_*` routines; the tower's run container has no aarch64 GCC, so our Units are inline (log 436). 2026-10-13 (log 445, run elv2_l154): two instances on one program: `-ffp-contract=off` makes `a * b + c` two words (`fmul.d`, `fadd.d`), and `-fsigned-char` makes `c + 1` read its byte with `lb`, so 0xC8 + 1 is -55. 2026-10-13 (log 446), at Dee's word: out of our configuration: "our configuration is `GNU-C` unoptimized and debugging. if it changes the computational natural of the program, thats on clang." |
| 38 | the floating-point environment: a float HiOp's Unit reads the rounding mode from a machine register (riscv64's `fadd.d fa5, fa5, fa4, dyn` reads `fcsr`'s rounding mode, Sail's `select_instr_or_fcsr_rm` in `~/Programming/SOURCES/sail-riscv/model/extensions/FD/fext_insts.sail`), and sets exception flags there (my reading for the flags; not checked); a program changes and reads them through `fesetround` and `fetestexcept`, and `#pragma STDC FENV_ACCESS` and `FENV_ROUND` | every float HiOp, not counted | the machines keep the rounding mode and flags in a register (riscv64 `fcsr`, x86-64 `MXCSR`, aarch64 `FPCR` and `FPSR`) | open: the Units assume round-to-nearest and leave the flags out (log 435) 2026-10-13 (log 444): in the LoOps already: Sail's float LoOps read the rounding mode from `fcsr` and set its flags, and SoftFloat's slices cover all five rounding modes (`Research/oracle/riscv/softfloat_slices/`); the emulation keeps `fcsr` as state. 2026-10-13 (log 445): the emulations made so far are at rounding mode 1, toward zero, only (`Research/oracle/riscv/softfloat_slices/emulations/README.md` line 18); mode 0, C's default, is sliced and not emulated: AutoPoly's work. |
| 39 | attributes that can change a Unit or a layout: of the 283 attributes a C program can write for every machine or one of ours, 122 are read by clang's lowering code for C on our three machines (`clang/lib/CodeGen`, and the layout and type code in `clang/lib/AST`); 9 of them hold on one machine only (clang's `AnyX86Interrupt`, `AnyX86NoCallerSavedRegisters`, `AnyX86NoCfCheck`, `FunctionReturnThunks`, `PragmaClangTextSection`, `PreserveNone`, `RISCVInterrupt`, `TargetVersion`, `X86ForceAlignArgPointer`), so they are out by the all-three-architectures rule; the other 161 are read only by clang's checking code, by this scan (`Research/lower_HiOp/compare_clangs_other_lists.py`) | 113 attributes for every machine, not run | an attribute is part of a holder's or a function's context (log 430, group 7); only the 6 that place a holder are modelled (logs 430, 431) | open: which of the 113 C accepts on all three machines, and what each changes, needs a run that writes a use of each, as log 367's grid did for operators. Some of the 113 belong to other languages or to calling conventions our machines ignore (`ObjCBoxable`, `StdCall`), which only that run sorts out (log 436). 2026-10-13 (log 447): `noreturn` held by hand (run elv2_l155): it drops only the caller's return instructions after the call (on riscv64 7 instructions against 12), which are the function's, not the HiOp's. Recommended: sort the 113 by reading clang's code into hints, layouts (declarations, by hand) and the few that change what a program does (`cleanup`, `constructor`). 2026-10-13 (log 448): by hand, with declarations, on my reading: an attribute is written on a declaration or as a hint on a statement; what it changes is a layout or a frame (declaration work, e.g. `noreturn` drops the caller's return), or nothing, or it adds a call or start-up code (`cleanup`, `constructor`), which are HiOps we have or infrastructure. 2026-10-13 (log 449): done by hand: the ledgerer's file, Table 3, every attribute sorted by what it changes. |
| 40 | bit-fields, a context (corrected 2026-10-15, log 479: clang keeps a bit-field's width out of its type, so the field is where its holder lives; filed below as holders since log 443): `int a : 13` holds -4096 to 4095, so a value that does not fit is cut to the width when it is stored; the standard-form holds no bit-field holder | not counted: each operator that takes a whole-number holder, times each width | C17 6.7.2.1: a bit-field has the width it declares; my reading, not run: clang's store keeps the value's low bits | open, found 2026-10-13 (log 443). Run elv2_l152 (log 442) counted bit-fields among the kinds of place and chose inputs whose results fit 13 bits, so it never stored a value that does not fit. The width belongs with the holder's type, not its place. 2026-10-13 (log 445, run elv2_l154): the store half is now seen: `mode.level = 5000;` on riscv64 keeps 5,000's low 13 bits (`lhu`, `c.lui`, `c.and`, `sh2add`, `sh`). Reading -3,192 back is still my reading, not run; Python's ctypes gives -3,192. 2026-10-13 (log 446): one update to the standard-form (Dee: "should be able to be modelled by one update"): its holders are already fields of a struct, and a bit-field is a field with a width. It needs a choice of widths, as D2 does for `_BitInt(N)`. 2026-10-13 (log 447): by hand (run elv2_l155): 6 held and lowered on all three machines (stores into `int a : 31`, `int a : 13`, `unsigned int a : 31`, a read and add, `+=`, `++`). 31 is the largest width below `int`'s own (Dee: "perhaps the largest one"; 32 is a plain `int`). Corrects log 446: the width changes the access size too (13 bits as `lhu`/`sh`, 31 as `lwu`/`sw`), not only the constants. 2026-10-13 (log 448): solved, retracting log 447's "by hand": a bit-field operation is a complex HiOp, the word that holds the field changed with `&`, `|`, `<<` and `>>` and stored again; where the field sits is its struct's layout, which goes with declarations. 2026-10-15 (log 479): a context, modelled by automation: clang's logic for each place, learned from `a + b`, predicts its IR in 3,126 of 3,126 functions (1,001 of 1,001 with a bit-field); the bit-field place's riscv64 words, lowered alone and spliced in, give C's value in 1,092 of 1,092 functions (runs elv2_l171, elv2_l172; `struct Q`'s three fields). Code: `model_HiOps/model_contexts`. Not yet run: other widths, positions, types and `unsigned` fields. |
| 41 | Apple-only routines a Unit calls: `__cospi`, `__cospif`, `__sinpi`, `__sinpif`, `__tanpi`, `__tanpif`, `__exp10`, `__exp10f`, `objc_memmove_collectable` | 9 routines, 452 riscv64 Units | no library on Linux defines them (run elv2_l159, log 449) | open, found 2026-10-13: my recommendation, out; waits for Dee's word 2026-10-13 (log 453): out, by Dee's ruling of log 446: our configuration is GNU C on riscv64 Linux, where no library defines these. |
| 42 | SafeStack's routines, `__get_unsafe_stack_bottom`, `_ptr`, `_start` and `_top`: compiler-rt defines them only in its SafeStack runtime, written in C++ (`compiler-rt/lib/safestack/safestack.cpp`) | 4 routines, 4 Units | only a program built with `-fsanitize=safe-stack` links them | open, found 2026-10-13: my recommendation, out (not our configuration) 2026-10-13 (log 453): out, by Dee's ruling of log 446: not our configuration. |
| 43 | `__trunctfbf2`, `long double` to `__bf16`: compiler-rt defines it for x86-64 only (`builtins/trunctfbf2.c`, under `defined(__x86_64__)`) | 1 routine, 12 Units | clang's own runtime lacks it on riscv64 | open, found 2026-10-13: my recommendation, out 2026-10-13 (log 453): out, by Dee's ruling of log 446: clang's own gap ("thats on clang"). |
| 44 | `__fixhfti`, `__fixunshfti`, `__floattihf`, `__floatuntihf`, between `_Float16` and `__int128`: no runtime of compiler-rt defines them | 4 routines, 126 Units | as item 43 | open, found 2026-10-13: my recommendation, out 2026-10-13 (log 453): out, as item 43. |
| 45 | `__builtin_eh_return`: clang writes no instruction for it on riscv64 and aarch64 (the standard function ends after its frame opens: 360 riscv64 Units and 330 aarch64 Units with no words); on x86-64 its 13 words end in a return | 1 builtin | the unwinder's builtin; on riscv64 its lowering does nothing (run elv2_l156) | open, found 2026-10-13: my recommendation, out 2026-10-13 (log 453): out, as item 43, and by the all-three-architectures rule: it lowers to nothing on two of the three. |
| 46 | the cut keeps the copy of `p` back inside the Unit: the debug table files clang's reload of `p` from its stack slot (riscv64 `ld a1, -0x18(s0)`) under the HiOp's line, so my cut of log 449 kept it, where log 440 Table 1 puts it out (the Unit of `a + b` is 4 words, not 5). Found by Gemini (log 450); checked in log 451 | riscv64: 509,236 of 3,981,370 Unit words, in 292,248 of 321,882 Units; x86-64: 674,472 of 4,226,812, in 292,369 of 321,641; aarch64: 759,478 of 3,736,520, in 279,390 of 308,194 (run elv2_l156) | my cut by line, which cannot tell a reload of `p` from a fetch, since both sit on the HiOp's line | open, 2026-10-13 (log 451): my recommendation, take each reload out of the Unit's words and keep it at its place as "this register holds `p` from here"; dropping the reloads with no place (Gemini's fix) changes what 191,072 riscv64 Units do (21,127 of them certainly, `a++` among them). The records keep every word and its line, so the Units can be cut again without a new compile. Waits for Dee's word 2026-10-13 (log 453): done, as log 440 says: `extract_unit_from_LoHiOp` takes each load of `p` out of the Unit's words and keeps its place in `holds_p`; every Unit cut again from run elv2_l156's records, no compile: riscv64 509,236 of 3,981,370 Unit words out, in 292,248 of 321,882 Units; x86-64 674,472 of 4,226,812, in 292,369 of 321,641; aarch64 759,478 of 3,736,520, in 279,390 of 308,194; exactly this row's counts, nothing else changed. Run elv2_l160 on the VM: 12 of 12 checks passed (11: `a + b` as log 440's 4 words; 12: `a++`), and the same records. |
| 47 | Signatures dropped by a one-row check. Our check (`kinds_pass`, `extract_lang_vocab/clang.py`) asks clang which builtin it made of the first row of each written form. When clang made another size of the same builtin (it sizes a `__sync_*` builtin by what the pointer points to: `__sync_fetch_and_add_4(&flag, 1)` with `flag` a `char` becomes `__sync_fetch_and_add_1`), `add_HiOps` (`extract_lang_vocab/__init__.py`) drops the whole form, and a written name none of whose forms passed is dropped from the lowering's list too. Each dropped signature (the builtin as written, with its holders) is a HiOp variant clang accepts and lowers, the holders being context that changes its meaning. Dee, 2026-10-15: "the lowering is correct and the signatures are unique, so whats the problem? those signatures look like HiOp variants with context that modifies their meanings." Filing a HiOp under the name written is right; log 456's reading of this item as a misfiling is withdrawn (log 478) | 165 of the 1,237 written forms checked (2026-10-06's grid), of 100 written names; they hold 23,045 signatures clang accepts. The lowering's list holds 4,509 of them; the list `extract()` makes holds none. 70 written names lose every form, among them `__sync_fetch_and_add` with no size and `__sync_fetch_and_add_8` | checking one combination per written form, and keeping or dropping the form by that one answer (`kinds_pass`, `add_HiOps`) | done 2026-10-16 (log 480), at Dee's word of 2026-10-15 ("if it works, then yeah sure"): `read_back_as_written` (`extract_lang_vocab/clang.py`) keeps a form clang read back as the same builtin at another size. Run elv2_l177: the 165 such forms kept; 32,890 HiOps of the grid's own cells added by it, and more from the signatures read (item 51); `__sync_fetch_and_add_4(a, b)` 0 HiOps on 2026-10-14, 1,447 now. Each with its own Unit once lowered: the lowering has not run on the new list yet |
| 48 | `__builtin_fpclassify(0, 1, 4, 3, 2, x)` tells which kind of number `x` is (0 NaN, 1 infinite, 4 normal, 3 subnormal, 2 zero: the program's own codes, in that order). Since log 424, `standard_HiOp_wrapper` writes the five codes as inert parts; `kinds_pass` (`extract_lang_vocab/clang.py`) looks for the call in the syntax tree clang prints, where `standard_HiOp_wrapper` put it before log 424, doesn't find it, and marks the operator not as written | 32 HiOps, which `add_HiOps` drops from today's dict (the lowering's list, from 2026-10-06's answers, still has them) | `kinds_pass` looks for the call where `standard_HiOp_wrapper` no longer puts it | open, found 2026-10-14 (log 456): my recommendation, teach `kinds_pass` (its helper `parsed_node_c`) where the inert parts put the call. Waits for Dee's word, with item 47 |
| 49 | another clang lowers some HiOps to other arch-opcodes, and refuses some: measured on riscv64 over all 322,610 HiOps beside clang 21.1.8 (runs elv2_l168, elv2_l169) | clang 20.1.8: 280,203 the same words, 37,932 the same arch-opcodes (jump targets moved), 3,154 other arch-opcodes, 593 refused by one of the two; clang 22.1.2: 249,004, 41,480, 2,238, and 29,161 refused by clang 22 alone (an incompatible pointer, such as `char *` from `int *`, is an error in clang 22 and a warning in clang 21); clang 19.1.7 files the frame's last words under the HiOp's line, so the cut takes them | clang's releases (log 457) | later: our configuration is clang 21.1.8 (Dee, log 446); this is what changes if the configuration's clang does 2026-10-14 (log 464): off the list, at Dee's word: "no fuck that. no. remove it. i never added that to the list." Log 457's measurement stays as a record. |
| 50 | `extract()` reuses past answers, where Dee set it (2026-10-14, log 462) to make its whole list every run and check it against the past findings ("it can easily generate a new list and it can validate the past findings"): `judge_pass` (`extract_lang_vocab/clang.py`, lines 580 to 584) skips every combination clang answered before. And the code that tries combinations, `extract_lang_vocab`'s job, sits outside that node, with the standard-form's routing, `HiOp_configuration_solver`'s job (log 461) | the trying code: 33 parts, 395 lines of code; the routing: 81 parts, 778 lines. A whole fresh list of GNU C took 123 s in run elv2_l166 | each move since 2026-09-30 left the trying code and the routing where they were, and on 2026-10-13 and 14 I wrote the move as done (log 461 §1); I then read the reuse of past answers into `extract()` as Dee's definition (log 462 §3) | done in the code 2026-10-16, at Dee's word: "until PseudoCoup is completed, i dont want to assume that our past answers are correct." `judge_pass` asks every combination again and reads the past answers only to set them beside the new ones (`beside_past`); run_elv3 writes `beside_past.json`. Its first run, elv2_l178 (small, run elv2_l177's answers as the past), 2026-10-17 19:26 to 19:28 UTC, exit 0: every combination asked again, 44,806 of 44,806 (pass a 2,971, pass b 36,051, pass c 5,784), all 44,806 answered before, the same answer for 44,806, 0 changed (`Research/extract_lang_vocabulary/reader_joined/elv2_l178/beside_past.small.json`). Done for the small run; the wide run is not run. Found 2026-10-14 (logs 461, 462) |
| 51 | holders never tried. `extract()` tries the same 52 holders as each of a HiOp's holders (2,704 pairs for `__sync_fetch_and_add_4(a, b)`). Of its pointers, only `char *`, `int *` and `const int *` point to an integer, so no pointer to a `short`, `long`, `long long`, `__int128`, unsigned integer or `_BitInt` is tried. The HiOp variants clang accepts with such a pointer are never tried, among them `__sync_fetch_and_add_4(a, b)` with `a: short *` (a 2-byte add), `a: long long *` (8 bytes) or `a: __int128 *` (16 bytes) | not counted: no run has tried them. For `__sync_fetch_and_add_4(a, b)`, 5 of the 52 holders pass as `a` (`char *`, `int *`, `int **`, `arr4`, `_Atomic(int *)`; `Research/extract_lang_vocabulary/mask/gnu17/c.knowns.jsonl.gz`, 2026-10-06), while clang's check, `BuiltinAtomicOverloaded`, takes a pointer to any integer or pointer of 1, 2, 4, 8 or 16 bytes that is not const (`complex_signature_reader`'s `checking.json`, 2026-10-01: 30 accepting paths); by clang's code, not yet run | the holders C builds from others are `REPRESENTATIVES` in `extract_lang_vocab/clang.py`: one or more of each kind of type clang declares, picked by hand, ten of them pointers. None is read from an operator's own definition | done 2026-10-16 for the builtins with custom typechecking (log 480), at Dee's word: "why would i solve problems with the reader and not use those solutions in extract? ... do it now." `extract()` reads `complex_signature_reader`'s accepting rules for the 305 such builtins and tries the signatures they accept (`complex_signature_reader/accepted_signatures.py`), over the 52 holders kept and a pointer to each (46 added, all kept in a field); clang judges each. Run elv2_l177: 158,733 HiOps added from the signatures read; for `__sync_fetch_and_add_4(a, b)`, `a` takes 31 holders, the reading's 31, all accepted. The other builtins and the forms are crossed with the 52 as before. Found 2026-10-15 from Dee's idea: "is it not possible to use tree-sitter to identify where these operator definitions start and end, and then extract all the accepted signatures or the holders it processes? ... those holder list become the possible variant to check if GNU-C accepts it." |
| 52 | dropped forms are not flagged. `add_HiOps` (`extract_lang_vocab/__init__.py`) skips every operator not read back as written, and the run prints only a count ("N of M read back as written", `kinds_pass` in `extract_lang_vocab/clang.py`). The read-back rows, with what clang made and `same_builtin_other_size`, stay in what `extract()` returns (`passes.kinds_b`, `passes.kinds_c`), but nothing lists the dropped forms or their variants | not counted for `extract()`'s run of 2026-10-14. The research run of 2026-10-06 listed them in its `summary.json`: 56 forms read back as another operator, 165 builtin forms made at another size, 1 rewritten as another kind | `extract()` returns the rows and writes none of them out; only the research run's summary listed the drops | open, found 2026-10-15 (Dee: "they are flagged still yes, they arent dropped silently?"). Its place in the tree being settled is `model_lang_parts` → `HiOps`. 2026-10-16: counted and listed by hand, not by `extract()` (`Planning/node_0_0_projects/node_0_0_0_pseudocoup/SUPPORT_gnu_c_work_remaining.md`, Tables 1 and 2): of the 1,416 operators clang accepts (run elv2_l177), 58 are left out after the one-row check, as on 2026-10-14; 53 are other languages' operators whose text is a C operator the list holds under its own name, and 5 are lost (items 5, 48, 55, 56 and 57) |
| 53 | the checking reader cannot look a value up in a table a function declares. In `Sema::BuiltinAtomicOverloaded`, clang picks the sized builtin as `BuiltinIndices[BuiltinIndex][SizeIndex]`, and `checking_reader` keeps that condition unread, so it cannot say which size clang makes for a holder | `BI__sync_fetch_and_add_4`: the same 2 unread conditions as written and as preprocessed (2026-10-16: run elv2_l173 made the files; the reading ran on the laptop). Of the 139 GNU C builtins the reader reads, 75 have a condition unread (2026-10-01 and again 2026-10-16, preprocessed: the same 64 whole and 75 not). The 32 `__sync` builtins have two causes only: this table, and the sized builtin's declaration found by name (`LookupName`). The other 43 have others: whether a type is complete (24), a constant's value (22), an atomic's scope model (22), a type's size (22), a vector's element type (9), the target's long double format (8), a type's kind (4), and about 20 more, 1 to 3 builtins each; 14 of the 22 `__atomic_*` builtins need only the first four | since 2026-10-16 the table's text is plain, every macro expanded, and the condition stays unread: the walk does not work out a subscript into a table the function declares (read from the result, not from the walk's code) | open, found 2026-10-16; macros are no longer the cause (Dee: "lets implement that so we never have to be bothered by these again"). Its place in the tree being settled: `model_lang_parts` → `HiOps` → `complex_signature_reader` |
| 54 | the operator reader lost the printers that assert first once it read clang's files preprocessed: with NDEBUG, as clang's release build has it, `assert(...)` is `(static_cast<void> (0));` (glibc's assert.h), which the reader could not read | 101 of the 902 forms of 2026-10-06 (CompoundStmt 3, StmtExpr 2, and 96 of C++, SEH and Objective-C); 2,757 of 2026-10-14's HiOps gone in run elv2_l176, all compound statements (`{ a; b; }` 2,704, `{ a; }` 52, `{ }` 1) | run elv2_l173 compared the functions, the lists and the write-back functions as written and as preprocessed, never the forms the operator reader makes from them | fixed 2026-10-16 (log 480): `VOID_CAST` in `operator_reader/clang.py`, a cast to void writes nothing, as the assert did. Run elv2_l177 checks the forms before anything else: 902 of 902 and 1,510 of 1,510 builtin forms, as on 2026-10-06; none of 2026-10-14's HiOps gone |
| 55 | `ExtVectorElementExpr`, an element of an ext vector by its letter (`v.x`, `v.xy`), is not in the list: the operator reader writes it `a.m`, with a struct member's name where an element's letter goes | 1 operator; clang made `MemberExpr` of its one accepted choice (`struct S`), and refuses `.m` on every ext vector | the printer writes `getAccessor().getName()`, and the reader puts the member placeholder there | open, found 2026-10-16 (Dee: "what is the problem with these?", of the operators left out). 2026-10-17: item 19 had already solved it, and this row was written without reading that one: `v.x` is `v[0]`, a complex HiOp, the subscript on the same holder with the constant 0 (log 448, after Dee's "arent these complex HiOps?"). What stays: the list names no `ExtVectorElementExpr` |
| 56 | `AttributedStmt`, a statement with an attribute (`__attribute__((fallthrough));`), is not in the list: the operator reader writes it `a;`, with no attribute | 1 operator; clang made the statement `a;` alone | the reader leaves out what `Attr->printPretty(OS, Policy)` writes (its left-out list says so) | open, found 2026-10-16, as item 55. 2026-10-17: item 19 had already settled `fallthrough` by hand: the same instructions as without it (log 447, run elv2_l155). Open: clang's other statement attributes (`nomerge`, `musttail`, `likely` and the others its Attr.td gives a statement), not ruled on |
| 57 | `__builtin_invoke(f, x)` is not in the list: clang's check builds the plain call `f(x)` in its place, so our check finds a call to `f`, not to the builtin | 1 operator | clang's `BuiltinInvoke` (`clang/lib/Sema/SemaChecking.cpp`) returns `ActOnCallExpr(..., Args.front(), ..., Args.drop_front(), ...)` for a callee that is not a member pointer | open, found 2026-10-16, as item 55; like the sizes of item 47, every signature clang accepts would be a HiOp variant of the name written. Waits for Dee's word |
| 26 | not compared yet: clang's attributes beyond the 6 that place a holder (function attributes such as `noreturn`, `naked`, `weak`, `alias`, `constructor`), pragmas (`#pragma pack`, `#pragma STDC FENV_ACCESS`, `#pragma clang fp`), the driver's defaults beyond floating-point contraction (position-independent code, the code model). Added 2026-10-12 (log 434): clang's description of each machine beyond item 31's four facts (`TransferrableTargetInfo`); each machine's calling-convention code (`clang/lib/CodeGen/Targets/RISCV.cpp`, `X86.cpp`, `AArch64.cpp`: 853, 3,529 and 1,355 lines); LLVM's list of runtime routines (`llvm/include/llvm/IR/RuntimeLibcalls.td`); the predefined macros, through which a program's own text differs per machine before clang reads it (`clang/lib/Frontend/InitPreprocessor.cpp`, `__CHAR_UNSIGNED__` at line 1268); the language options (`clang/include/clang/Basic/LangOptions.def`, 329 entries) | 7 lists compared; 2 not run | not read until 2026-10-12 | compared 2026-10-12 (log 435): the predefined macros, the driver's defaults, each machine's calling convention and layouts (run elv2_l149, read by `Research/lower_HiOp/read_samples_l149.py`), and clang's description of each machine, LLVM's runtime routines, `Sanitizers.def`, `LangOptions.def`, `Attr.td` and the pragmas, read from source (`Research/lower_HiOp/compare_clangs_other_lists.py`). They added items 35 to 38, and sizes for items 21 and 33. Finished 2026-10-12 (log 436): LLVM's routines, expanded per machine by `llvm-tblgen` (run elv2_l150), number 439 for riscv64, 515 for x86-64 and 544 for aarch64, and the kept HiOps call 151, 200 and 148 of them; the rest are done by instructions on our machines, reached only under build flags or a toolchain (item 37), atomics of other sizes (items 1, 2, 34), or operations C does not write. The attributes narrow to item 39. The 54 pragmas map onto items 15, 22, 32, 36, 38 and 39 (my reading of each handler). Done |

## 2c. The items under the project's two filters (2026-10-12, log 433 §4)

Dee, 2026-10-12, asked how the list counts what the all-three-architectures
rule and the order simple, then hybrid, then complex already set aside. It
counted those items as if they were work now. This table applies both
filters. The stages are log 379's classes; "not a HiOp" is data, libc, or
words clang never writes.

Table 2c. Each item's stage, and whether the rule keeps it.

| stage | items | count | count before log 440 |
|---|---|---|---|
| simple, the stage now: carried by the model of places (log 433) | 12 | 1 | 3 (12, 16, 28) |
| simple, the stage now: open | 6, 7, 14, 15, 17, 18, 21, 22, 25, 31, 32, 33, 34, 37, 38, 39, 40 | 17 | 19 (with 27, 29, 30; 40 did not exist) |
| hybrid, next | 1, 2 | 2 | 2 |
| complex, free where composition holds | 11 | 1 | 1 |
| not a HiOp (data, libc) | 3, 5, 10, 13, 19, 20, 36 | 7 | 7 |
| our own tools | 9, 23, 24 | 3 | 3 |
| out by the all-three-architectures rule | 4, 8, 35 | 3 | 3 |
| done: every list compared (log 436) | 26 | 1 | 1 |
| closed: the words sit inside one Unit, at Dee's yes (log 440) | 16, 27, 28, 29, 30 | 5 | 0 |
| all | | 40 | 39 |

- What the filters set aside is still work at its own stage: 57 hybrid
  operators after the simple ones, and 894 complex operators, free only
  where composition holds. Item 15 is one place it does not hold.

Table 2d. Each item by the plan node it belongs to (2026-10-13, ,
under the plan's design: `pseudoarch` holds one model, RISC-V's; every LoOp's
Lean is Sail's body, or SoftFloat sliced over the 24 GMP primitives; AutoPoly
emulates each LoOp in a language from that language's Units proven equal to
the primitives (its CORE). So a polyfill gives what riscv64 gives.

| where it sits | items | count |
|---|---|---|
| `map_LoOp_to_lean`: already in every LoOp | 31, 38 | 2 |
| `map_HiOp_to_unit`: HiOps to hold and lower for riscv64 | 1, 2, 11, 15, 17, 18, 19, 37, 39, 40 | 10 |
| `map_HiOp_to_unit`: the routines a Unit calls (system calls are where the emulation meets the environment) | 3, 10, 32 | 3 |
| `lower_HiOp` and `extract_unit_from_LoHiOp` | 21, 22, 23 | 3 |
| `ledgerer`: declarations, places, names, constants as values, layouts, a holder's value before its first write | 5, 12, 13, 14, 20, 33, 36 | 7 |
| `hub/autopoly`: what other threads see | 34 | 1 |
| our tools: the simple/hybrid/complex sort | 6, 7, 24, 25 | 4 |
| the product's code | 9 | 1 |
| out by the all-three-architectures rule | 4, 8, 35 | 3 |
| closed or done | 16, 26, 27, 28, 29, 30 | 6 |
| all | | 40 |

- Log 437's sort put 1, 2, 22, 33, 34 and 38 under "a model of the machine
  level". That was mostly `map_LoOp_to_lean`, built in research (Step 1.2,
  2026-09-17); only item 34 is left of it.
- The three-machine facts in items 15, 21, 31, 33, 35 and 36 stay on record;
  they serve the all-three-architectures rule.

Table 2e. Each item by status (2026-10-13, , beside log 445's. Dee
ruled on declarations, build flags, the fused multiply-add, `asm` and a holder
read before its first write, and asked about the rest; log 446 answers each.

| status | items | count | log 445 |
|---|---|---|---|
| solved | 12, 13, 16, 22, 27, 28, 29, 30, 31, 33, 38 | 11 | 8 |
| next, in the agreed run | 3, 10, 21, 23, 32, 34 | 6 | 2 |
| later (by hand, or with optimizing) | 1, 2, 5, 15, 17, 20, 36 | 7 | 0 |
| open | 6, 7, 9, 11, 14, 18, 19, 24, 25, 39, 40 | 11 | 26 |
| out (the rule, or our configuration) | 4, 8, 35, 37 | 4 | 3 |
| done | 26 | 1 | 1 |
| all | | 40 | 40 |

Table 2f. Each item by status (2026-10-13, , beside log 446's.
Dee corrected "later, by hand" to by hand now, and asked about the rest; run
elv2_l155 held items 11, 18, 19, 39 and 40 by hand.

| status | items | count | log 446 |
|---|---|---|---|
| solved | 11, 12, 13, 14, 16, 18, 22, 27, 28, 29, 30, 31, 33, 38 | 14 | 11 |
| by hand now | 1, 2, 5, 17, 19, 20, 34, 36, 40 | 9 | 0 |
| next, in the agreed run | 3, 10, 21, 23, 32 | 5 | 6 |
| later | 15 | 1 | 7 |
| open | 6, 7, 9, 24, 25, 39 | 6 | 11 |
| out | 4, 8, 35, 37 | 4 | 4 |
| done | 26 | 1 | 1 |
| all | | 40 | 40 |

Table 2g. Each item by status (2026-10-13, , beside log 447's.
Dee: "arent these complex HiOps?" (19, 40); attributes go with declarations on
my reading (39). No item with a line in the Python program is open; the 5 open
are our tools.

| status | items | count | log 447 |
|---|---|---|---|
| solved | 11, 12, 13, 14, 16, 18, 19, 22, 27, 28, 29, 30, 31, 33, 38, 40 | 16 | 14 |
| by hand now | 1, 2, 5, 17, 20, 34, 36, 39 | 8 | 9 |
| next, in the agreed run | 3, 10, 21, 23, 32 | 5 | 5 |
| later | 15 | 1 | 1 |
| open (our tools) | 6, 7, 9, 24, 25 | 5 | 6 |
| out | 4, 8, 35, 37 | 4 | 4 |
| done | 26 | 1 | 1 |
| all | | 40 | 40 |

Table 2h. Each item by status (2026-10-13, , beside log 448's.
Dee: "the agreed run? why isnt it settled then. also any work that you can
complete now, do so please"; "if you can do them by hand. do them please."
Items 41 to 45 were found the same day.

| status | items | count | log 448 |
|---|---|---|---|
| done | 1, 2, 5, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 38, 39, 40 | 28 | 17 (16 solved, 1 done) |
| waits on Dee's choice of C library | 3, 10 | 2 | 2, in "next" |
| my recommendation, close (the trace's sort) | 6, 7, 24, 25 | 4 | 4, in "open" |
| my recommendation, with the next language (`extract()`) | 9 | 1 | 1, in "open" |
| later | 15 | 1 | 1 |
| out | 4, 8, 35, 37 | 4 | 4 |
| found today; my recommendation, out | 41, 42, 43, 44, 45 | 5 | none |
| all | | 45 | 40 |

Item 46, added later the same day (log 451): open, waiting for Dee's word on the fix. 46 items in all.

Table 2i. Each item by status (2026-10-13, , beside log 449's
Table 2h. Dee: "why am i answering a million questions?"; the five groups and
the sort follow from Dee's rulings, and item 46 from log 440.

| status | items | count | log 449 |
|---|---|---|---|
| done | 1, 2, 5, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 38, 39, 40, 46 | 29 | 28 |
| out | 4, 8, 35, 37, 41, 42, 43, 44, 45 | 9 | 4 (41 to 45 waited for Dee's word) |
| closed | 6, 7, 24, 25 | 4 | 0 (they were "open") |
| later | 3, 10, 15 | 3 | 1 (3 and 10 were "waits on the C library") |
| with the tools into their places | 9 | 1 | 1 |
| all | | 46 | 45 |

Table 2j. Each item by status (2026-10-14, , beside log
453's Table 2i. Item 9 is done: `extract()` is written and makes the
vocabulary; items 47 and 48 were found by the move's check, item 49 by
measuring the Units under clang 19, 20 and 22. (Corrected 2026-10-14, log
461: this caption said "the tools are in their places". Two parts are not:
the trying code and the routing, item 50.)

| status | items | count | log 453 |
|---|---|---|---|
| done | 1, 2, 5, 9, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 38, 39, 40, 46 | 30 | 29 |
| open, waiting for Dee's word | 47, 48 | 2 | 0 (new) |
| out | 4, 8, 35, 37, 41, 42, 43, 44, 45 | 9 | 9 |
| closed | 6, 7, 24, 25 | 4 | 4 |
| later | 3, 10, 15, 49 | 4 | 3 |
| with the tools into their places | | 0 | 1 (item 9) |
| all | | 49 | 46 |

Table 2k. Each item by status (2026-10-14, , beside Table 2j.
Item 50 is new: `extract()` as Dee set it on 2026-10-14, and its trying code
outside its node (logs 461, 462).

| status | items | count | Table 2j |
|---|---|---|---|
| done | 1, 2, 5, 9, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 38, 39, 40, 46 | 30 | 30 |
| open, waiting for Dee's word | 47, 48, 50 | 3 | 2 |
| out | 4, 8, 35, 37, 41, 42, 43, 44, 45 | 9 | 9 |
| closed | 6, 7, 24, 25 | 4 | 4 |
| later | 3, 10, 15, 49 | 4 | 4 |
| all | | 50 | 49 |

Table 2l. Each item by status (2026-10-14, , beside Table 2k. At
Dee's word, the C library's two entries are out (not GNU C's work), and another
clang is off the list.

| status | items | count | Table 2k |
|---|---|---|---|
| done | 1, 2, 5, 9, 11, 12, 13, 14, 16, 17, 18, 19, 20, 21, 22, 23, 26, 27, 28, 29, 30, 31, 32, 33, 34, 36, 38, 39, 40, 46 | 30 | 30 |
| open, waiting for Dee's word | 47, 48, 50 | 3 | 3 |
| out | 3, 4, 8, 10, 35, 37, 41, 42, 43, 44, 45 | 11 | 9 |
| closed | 6, 7, 24, 25 | 4 | 4 |
| later | 15 | 1 | 4 |
| off the list at Dee's word | 49 | 1 | 0 |
| all | | 50 | 50 |

## 3. Item 1 is stable in clang's GNU C

Read from clang's own history (the llvm-project repository), in the file that
declares the builtins: `clang/include/clang/Basic/Builtins.def`, rewritten as
`Builtins.td` on 2024-01-24.

Table 3. When each of item 1's builtins was declared, and every change to its
declaration since.

| builtin | declared | changes since |
|---|---|---|
| `__builtin_va_start` | 2007-10-11 | 2007 to 2009-01-20: four changes to how its `va_list` operand is written, ending in `"vA."` (a reference to a `va_list`); 2011-08-27: marked for clang's own type checking (`"n"` became `"nt"`); 2024-01-24: the file's new format |
| the 9 `__c11_atomic_*` | 2012-04-11, "to implement C11's <stdatomic.h> header" | 2012-04-12: moved under `ATOMIC_BUILTIN`, with the same type and flags; 2024-01-24: the new format |
| `__atomic_compare_exchange_n` | 2012-04-12, one of "the GNU-compatible __atomic builtins" | 2024-01-24: the new format |
| `__builtin_assume_aligned` | 2014-09-07 | 2022-09: marked for clang's own type checking (`"nc"` became `"nct"`); 2022-10-21: usable in constant expressions (`"nctE"`); 2024-01-24: the new format; 2024-12-19: a new error message for a non-pointer argument |

- None of the 12 has changed what it takes or gives since 2014 at the latest.
  `"vA."` has stood for `__builtin_va_start` since 2009-01-20, `"v."` for the
  10 atomics since they were declared in 2012, and `"v*vC*z."` for
  `__builtin_assume_aligned` since it was declared in 2014. Clang 21.1.8's
  `Builtins.td` writes the same types in its new form, for example
  `"void(__builtin_va_list_ref, ...)"`.
- The changes since are to clang's checking of the operands and to the file's
  format.
- Clang's own headers make them, at 21.1.8:
  `clang/lib/Headers/stdatomic.h` line 144,
  `#define atomic_load(object) __c11_atomic_load(object, __ATOMIC_SEQ_CST)`;
  and `clang/lib/Headers/__stdarg_va_arg.h` line 17,
  `#define va_start(ap, param) __builtin_va_start(ap, param)` (before C23).
- Not checked: how clang lowered them over those years.

## 4. How the vocabulary is made again

When clang changes version, these steps make the vocabulary again, in order.
Scripts are under `Research/extract_lang_vocabulary/`; every run goes through
Airlock on the tower.

Table 4. The steps, the script each runs, and the log where it was run.

| step | scripts | log |
|---|---|---|
| 1. clang's own lists of operators, builtins and holders | `complex_signature_reader/covered_vocabulary.py`, which writes `vocabulary/c.json` | 327 |
| 2. GNU C's list and the grid's verdicts | `run_elv3.py grid`, with `Projects/PseudoArch/map_HiOp_to_unit/DRY_mask_maker.py` | 367 |
| 3. lowered on riscv64, x86-64 and aarch64 | `what_clang_writes/all_architectures/make_probes.py`, then `read_verdicts.py` | 377 |
| 4. our clang, its lowering code compiled `-O0 -g` | run script `lanes_elv2/elv2_l86_debug_clang_rebuilt_with_ubuntus_builtin_lists_and_every_operator_traced.sh` | 379 |
| 5. the trace and the classes | `what_clang_writes/which_callee_sent_each_message/trace_callees_debug_clang.py`, `read_debug_trace.py`, `classify_callees.py` | 379 |
| 6. against real code | `what_real_code_uses/list_units.py`, `census_ast.py`, `sum_census.py` | 380 |
| 7. the chart | `what_clang_writes/builtins/make_figure.py` | 379 |

- Step 4 must use the distribution's own generated headers. Upstream's
  builtin lists, laid over them, made 30 programs come out different from the
  distribution's clang (log 379).
- Step 6 keeps its five code bases in elv2's `/persist/corpora` (199 MB).

## 5. Rulings and work still open from logs 361 to 375

Table 5. Each item, where it was raised, and its status on 2026-10-07.

| item | what | raised in | status |
|---|---|---|---|
| D2 | `_BitInt(N)`: one holder per width, or one for the group | log 366 | open, Dee's |
| D3 | the set of signature labels (the words "determined" and "undetermined" are agreed) | log 361 | open, Dee's; W6 follows it |
| W1 | GNU C's list lives in `run_elv3.py`, not in `operator_reader` | log 367 | open (item 9) |
| W2 | a builtin's case that tests the target | log 368 | my reading: answered by the trace, which follows the path clang takes for riscv64 (log 379) |
| W4 | the store of verdicts is keyed by how a program writes each operator, which `DRY_mask_maker`'s CORE rules out | log 367 | open |
| W5 | each operand's rule, read from clang's checking code | log 367 | open (`complex_signature_reader`) |
| W6 | the labels, and `extract()` | log 367 | open, after D3 |
| log 374, item 4 | `for` fits the prefix, main and postfix shape | log 374 | my reading: superseded by change 7 of log 375, an ordered list of calls |
| log 374, item 6 | the polyfill work is the set of `main_call_key`s | log 374 | counted in log 380 §5: 760 `main_call_key`s |
| log 375, change 3 | callees that carry the same `main_call_key` and no other calls are one simple HiOp | log 375 | later |
| log 375, change 6 | a `main_call_key` that splits into keys simple callees carry counts as calls to them | log 375 | later |

## See also

- `Planning/CORE_0_0_0_pseudocoup.md
  the account of 2026-10-07.
- `Planning/CORE_0_0_0_pseudocoup.md
  the census of the five code bases.
- `Planning/CORE_0_0_0_pseudocoup.md
  §4: the trace and the classes.
- `Planning/CORE_0_0_0_pseudocoup.md
  the 12 left out.
- `Planning/CORE_0_0_0_pseudocoup.md
  Point 2: how the list is made, and Table 3, what it refused.
