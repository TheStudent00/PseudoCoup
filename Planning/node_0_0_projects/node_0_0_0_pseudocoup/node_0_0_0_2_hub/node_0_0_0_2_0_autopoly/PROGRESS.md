---
id: hq.projects.pseudocoup.hub.autopoly.progress
status: living
---

# PROGRESS — autopoly

- 2026-09-22: node created from the ontology in
  `Planning/CORE_0_0_0_pseudocoup.md
- 2026-09-27: a known divergence, for section 5. go's unsigned `<<` and `>>`
  give 0 when the shift count is the bit width or more; c's, cpp's and rust's
  compiled arch-units give `x << (n mod width)`, because riscv64's shift uses
  only the count's low bits (in C the shift itself is undefined). Lean produced
  the separating input in Fable's run of 2026-09-26, which is reverted; go's
  own specification says the same.
- 2026-10-13, two by-hand pieces of infrastructure, done :
  - other threads: `SUPPORT_riscv64_ordering_per_target_language.md`, all
    twelve languages; the c row is clang's own mapping, read from run
    elv2_l158 (20 C11 atomic builtins held by hand, 37 held functions, lowered
    and cut on all three machines); the other eleven rows are my reading;
  - compiler-rt lowered whole for riscv64, `-O2 -g` (run elv2_l159): 155 of
    its 159 files; the 54 routines riscv64's Units call reach 58, 5,830
    words; `SUPPORT_gnu_c_infrastructure_lowered_whole.md`. The C library
    waits on the owner's choice. Running these whole is this node's work, not
    started.
