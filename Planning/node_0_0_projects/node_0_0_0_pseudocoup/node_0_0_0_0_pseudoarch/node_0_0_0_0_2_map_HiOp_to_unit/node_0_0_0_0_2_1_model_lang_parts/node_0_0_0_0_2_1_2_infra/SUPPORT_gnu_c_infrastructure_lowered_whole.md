---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.infra.support.gnu_c_infrastructure_lowered_whole
status: draft
---

# SUPPORT — gnu_c_infrastructure_lowered_whole

The routines riscv64's Units call, lowered whole and optimized, for AutoPoly
to run whole. Written 2026-10-13 by Claude (Opus 5.5), 
plan, the same day:

> theyre self contained objects. they dont need to be split. so the entire
> thing can be optimized in its lowering and emulated.

**What breaks in transpilation, and for whom.** A Unit that is a call means
nothing until the routine it calls is there. Instance: `long double total =
x + y;` lowers to `call __addtf3`; its meaning is `__addtf3`'s own code. Of
the 321,882 riscv64 Units of run elv2_l156, 186,529 call at least one
routine.

## 1. What was lowered

Run elv2_l159 (`Research/lower_HiOp/lower_compiler_rt_whole.py`; records in
`out/infrastructure_l157/compiler_rt_riscv64.jsonl.gz`, one routine per line,
every word with its source line).

- **compiler-rt** is clang's own runtime: the routines clang calls where
  riscv64 has no instruction. Its riscv64 build lists 159 files; each was
  compiled whole for riscv64 with `-O2 -g -DNDEBUG` (CMake's RelWithDebInfo,
  a standard build with the debug table on).
- 155 of the 159 compiled. The other 4 each need a header of the C library,
  so they sit on it: `emutls.c` (`stdlib.h`), `enable_execute_stack.c`
  (`sys/mman.h`), `eprintf.c` (`stdio.h`), `clear_cache.c` (`assert.h`).
- 268 routines are defined.
- riscv64's Units call 462 routines (90 named `__...`, 372 others). 54 of
  them are compiler-rt's, called by 99,150 of the 321,882 Units. Following
  what those call reaches 58 routines: 5,830 words in all, 144 distinct
  arch-opcodes. The largest are `__divtc3` (745
  words), `__divtf3` (470), `__multc3` (428) and `__addtf3` (354).
- One call leaves compiler-rt: `memcpy`, from `__atomic_load` and
  `__atomic_store`.

## 2. The other 408 routines

Table 1. The 408 routines riscv64's Units call that compiler-rt's builtins
do not define, sorted by name (my reading of each group), with how many of
the 321,882 Units call them and my recommendation. A Unit can call routines
of two groups, so the Units column overlaps.

| group | routines | Units | what breaks | recommendation |
|---|---|---|---|---|
| the C library and its maths library | 297, such as `malloc`, `strlen`, `printf`, `sin` | 140,765 | everything that prints, allocates or computes a function | lower the C library whole (§3) |
| `float128` maths (`sinf128` and 48 more) | 49 | 14,727 | `__float128` maths | glibc has them, musl does not (my reading): by hand, or with glibc |
| `_Float16` maths (`sinf16` and 22 more) | 23 | 5,123 | `_Float16` maths | no C library on Linux has them, by my reading; LLVM's own C library does (80 `*f16` files, written in C++) |
| glibc's checked copies (`__memcpy_chk` and 17 more) | 18 | 1,664 | `__builtin___memcpy_chk` and its family | each is its plain routine after a size check: by hand, or with glibc |
| `__riscv_flush_icache` | 1 | 169 | `__builtin___clear_cache` | a system call: by hand per target, with the other system calls |
| compiler-rt's BlocksRuntime (`_Block_object_assign`, `_Block_object_dispose`), written in C | 2 | 622 | blocks, Apple's extension | lower it whole with the C library, which it calls |
| Apple's libraries only (`__cospi`, `__sinpi`, `__tanpi`, `__exp10`, each with its `f` form, and `objc_memmove_collectable`) | 9 | 452 | none on Linux: no library there defines them | out: a program calling them does not link on Linux |
| compiler-rt's SafeStack, written in C++ (`__get_unsafe_stack_ptr` and 3 more) | 4 | 4 | only programs built with `-fsanitize=safe-stack` | out: not our configuration |
| `__trunctfbf2` (`long double` to `__bf16`), which compiler-rt defines for x86-64 only | 1 | 12 | the program does not link with compiler-rt on riscv64 | out: clang's own runtime lacks it |
| `__fixhfti`, `__fixunshfti`, `__floattihf`, `__floatuntihf` (`_Float16` with `__int128`) | 4 | 126 | the same: no runtime of compiler-rt defines them | out, for the same reason |

- 297 + 49 + 23 + 18 + 1 + 2 + 9 + 4 + 1 + 4 = 408.

## 3. What remains

- **The C library.** Which one is the owner's choice. My recommendation is musl:
  - clang builds it, where glibc is built with GCC (clang's support is
    partial);
  - it is small enough to lower whole and run whole: plain C, with a few
    assembly files per machine.
  - What clang calls that musl lacks is in Table 1: the `float128` maths and
    glibc's checked copies, by hand or out.
- **System calls.** By hand, per target language: the target's own calls
  (log 447).
- **Start-up.** The instructions before `main`: lowered whole with the C
  library.
- **Running them whole** is AutoPoly's part, which is not built.
