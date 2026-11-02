---
id: hq.projects.pseudocoup.ledgerer.support.gnu_c_declarations_by_hand
status: draft
---

# SUPPORT — gnu_c_declarations_by_hand

What the ledger does with each GNU C declaration, modelled by hand, with
riscv64's layout numbers as clang fixes them. Written 2026-10-13 by Claude
(Opus 5.5), 

> by-hand now, later potentially by modelling

> same with this. if you can do them by hand. do them please.

**What breaks in transpilation, and for whom.** Every program: each one
declares holders, and the ledger has to place each holder where riscv64
would, at its size, with its first value. A declaration writes data, not
instructions: clang turns it into a place, a size and first bytes, and the
Units then read and write those places.

The rules are log 385's 22, each read from clang
(`Planning/CORE_0_0_0_pseudocoup.md); §2 adds the declarations the list
named since; §3 the attributes; §4 riscv64's numbers, read back from clang by
run elv2_l157.

## 1. The 22 rules, and what the ledger does

Table 1. Log 385's rules, one line each. "Data" means the ledger records it
and no instruction comes from it.

| rule | the declaration | what the ledger does |
|---|---|---|
| 1 | a name | points it at its declaration |
| 2 | a written value (`0.5`, `'x'`, `"text"`) | a constant of its holder; a string's bytes go in the program's data |
| 3 | a conversion that only changes the holder | the same bits, seen as the new holder |
| 4 | a parameter | a holder in the function's frame; its first value is the argument |
| 5 | a variable | a holder of its type: in the frame when local and not `static`; in the program's data when `static` or at file scope; defined elsewhere when `extern`; first value from its initializer, else 0 (the owner, log 446); an array sized while the program runs takes its room when its line runs |
| 6 | a declaration line | nothing of its own: its declarations, in order |
| 7 | a struct or union | a new holder, laid out by §4's rules |
| 8 | a field | an offset in its struct, or a range of bits for a bit-field |
| 9 | an enum | an integer holder (4 bytes; 8 when a constant needs it, §4) |
| 10 | an enum constant | a number: the one written, or one more than the constant before, from 0 |
| 11 | a `typedef` | a new name for a holder |
| 12 | a `_Static_assert` | nothing: checked while compiling |
| 13 | a function declared without a body | nothing: a name for a function made elsewhere |
| 14 | a value worked out while compiling | the number clang computed |
| 15 | an initializer list | fills fields or elements in order, at §4's offsets; anything not written is 0; `{.y = 9}` is `{0, 9}` |
| 16 | a compound literal | an unnamed holder of its type, filled by rule 15 |
| 17–21 | attributes | §3 |
| 22 | a documentation comment | carried as text with its declaration |

## 2. The declarations named since log 385

Table 2. Each one, and the rule it comes under.

| declaration | example | what the ledger does |
|---|---|---|
| `__func__` | `printf("%s", __func__);` in `mean` | a `static const char[]` holding the function's name, `"mean"`: rule 5 and rule 2 (`__FUNCTION__` is the same, log 448) |
| an array with no size | `int primes[] = {2, 3, 5};` | its size from its initializer, 3 `int`s; `extern int table[];` takes its size from the definition elsewhere |
| a function with no prototype | `int old();` | rule 13; a call to it passes each argument promoted (`float` as `double`, `char` and `short` as `int`), as clang's call already does |
| a label, and `__label__` | `done:`; `__label__ retry;` | nothing of its own: a label is a place in the function's code, and `&&done` is a kept HiOp; `__label__` only limits where the name is seen |
| an anonymous member | `struct { union { int i; float f; }; int k; }` | its fields are found as fields of the enclosing struct, at the member's offset plus their own: `i` and `f` at 0, `k` at 4 |
| a designated initializer | `{.y = 9}`, `[2] = 5`, GNU's `[1 ... 3] = 7` | rule 15, element by element |
| a thread's own variable | `_Thread_local int seen;` | rule 5, with one copy per thread; riscv64 finds it from the `tp` register (my reading: each emulated thread keeps its own copy) |
| a run-time-sized array | `int buf[n];` | rule 5: room taken when its line runs (the owner: "okay", log 446) |
| `const`, `volatile` | `const int limit = 9;` | `const`: placed like any holder, in read-only data where clang puts it there; `volatile`: every read and write stays, as at `-O0` they already do |

## 3. Attributes

Table 3. Every GNU C attribute on a declaration, sorted by what it changes.
Log 385 rules 17 to 21, with the rest of GNU C's declaration attributes
placed by what each does.

| what it changes | attributes | what the ledger does |
|---|---|---|
| when or whether code runs | `constructor`, `destructor`, `cleanup(f)` | `constructor`: runs before `main` (`.init_array`); `destructor`: after `main` returns (`.fini_array`); `cleanup(f)`: `f(&holder)` is called where the holder's scope ends |
| which definition is used, and who sees it | `weak`, `visibility`, `alias`, `section`, `used` | `weak`: a definition elsewhere may replace it; `visibility`: whether other parts of the program see it; `alias("g")`: a second name for `g`; `section`: the part of the program file it sits in; `used`: kept even when nothing names it |
| the layout | `packed`, `aligned` | §4: `packed` drops the padding (`{char; int}` is 5 bytes), `aligned(16)` raises a field's or struct's alignment |
| the holder itself | `mode`, `vector_size`, `ext_vector_type` | `mode(DI)` makes an `int` 8 bytes; `vector_size(16)` and `ext_vector_type(4)` make vector holders (`v.x` is `v[0]`, log 448) |
| nothing a program does | `noreturn`, `unused`, `deprecated`, `nonnull`, `format`, `warn_unused_result`, `always_inline`, `noinline`, `cold`, `hot`, `pure`, `const`, `malloc`, `sentinel`, `fallthrough` and the other hints and checks | dropped: a hint or a check while compiling; where one changes the instructions (`noreturn` takes the caller's return away, log 448: riscv64 7 instructions, not 12), the change is already in the lowered words |

## 4. riscv64's layout, as clang fixes it

Read back from the assembly clang writes for
`Research/lower_HiOp/samples_l157/declarations_riscv64_layout.c`, by run
elv2_l157 (`out/samples_l157/layout_riscv64.txt`): 65 of 65 rows read; my 63
predictions (the RISC-V psABI, LP64D) all held; 2 rows were only recorded.
the owner's ruling: riscv64's layouts only, since AutoPoly runs riscv64's LoOps.

Table 4. Sizes and alignments, in bytes.

| holder | size | alignment |
|---|---|---|
| `char`, `_Bool` | 1 | 1 |
| `short`, `_Float16`, `__bf16` | 2 | 2 |
| `int`, `float`, `wchar_t`, an enum | 4 | 4 |
| `long`, `long long`, a pointer, `size_t`, `double`, `va_list` | 8 | 8 |
| `__int128`, `long double` | 16 | 16 |
| `float _Complex`, `double _Complex`, `long double _Complex` | 8, 16, 32 | as their parts |
| `max_align_t` | not read | 16 |

- Plain `char` is unsigned; `wchar_t` is signed.

Table 5. The layout rules, each with the instance clang gave.

| rule | instance | clang's numbers |
|---|---|---|
| a field sits at the next multiple of its alignment | `struct { char c; int i; }` | `i` at 4, size 8 |
| | `struct { char c; double d; }` | `d` at 8, size 16 |
| | `struct { char c; long double x; }` | `x` at 16, size 32, alignment 16 |
| a struct's size is a multiple of its largest alignment | `struct { int i; char c; }` | size 8 |
| a union is as large as its largest member | `union { char c; double d; }` | size 8 |
| an array is its elements, end to end | `int[3]` | size 12, alignment 4 |
| `packed` drops the padding | `struct __attribute__((packed)) { char c; int i; }` | `i` at 1, size 5, alignment 1 |
| `aligned` raises it | `struct { char c; int i __attribute__((aligned(16))); }` | `i` at 16, size 32 |
| | `struct { char c; } __attribute__((aligned(8)))` | size 8, alignment 8 |
| a flexible array member adds no size | `struct { int n; char data[]; }` | size 4 |
| | `struct { char c; long data[]; }` | `data` at 8, size 8 |
| a bit-field never crosses a unit of its own type | `struct { int a : 3; int b : 5; }` | size 4 |
| | `struct { int a : 31; int b : 2; }` | size 8: `b` starts the next `int` |
| | `struct { char a; int b : 24; }` | size 4: `b` fits in bits 8 to 31 |
| | `struct { long long a : 40; int b : 24; }` | size 8 |
| | `struct { unsigned a : 1; }` | size 4, alignment 4 |
| bits are given from the lowest | `{ unsigned a : 3; unsigned b : 5; unsigned c : 24; }` with `b = 1` | the word reads 8: `b` is bits 3 to 7 |
| a zero-width bit-field moves the next one to its type's next unit | `struct { char a : 1; int : 0; char b : 1; }` | size 5, alignment 1 (recorded, not predicted) |
| an enum with a constant too large for `int` | `enum { LARGE = 0x100000000 }` | size 8 |
