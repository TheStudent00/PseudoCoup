---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.model_lang_parts.progress
status: living
---

# PROGRESS — model_lang_parts

- 2026-10-15: Made 2026-10-15 in `map_HiOp_to_unit`'s `.NASCENT/`, at Dee's word: "please fill in the .NASCENT for `map_HiOps_to_unit` as best you can." Not live until the rework puts `.NASCENT`'s contents in place (PlanPlan `framework/PROTOCOL.md` §6d). Holds Dee's modelling order, carried from `model_HiOps`.

## The standard progress view of GNU C vocabulary extraction

Dee, 2026-10-19: "WHAT I WANT IS A STANDARD PROGRESS VIEW THAT DOESNT CHANGE
ASIDE FROM WHEN PROGRESS IS MADE ABOUT THE GNU-C VOCABULARY EXTRACTION ...
what my method has completed and what the other methods completed." This
table is that view . Its rows stay. A column is added only when
a run changes a count. Every count is operators out of one whole.

The whole: GNU C's 1,806 operators as clang 21.1.8 declares them
(`Research/extract_lang_vocabulary/vocabulary/c.json`: 357 expressions, 1,421
builtins and library calls, 28 statements; an operator is one kind with one
part count). The vocabulary holds 356 more operators of other languages'
kinds (C++, Objective-C, OpenMP, HLSL, CUDA, SEH, SYCL); they are not in
this table.

The previous methods: the cross-product grid with complex_signature_reader
joined into `extract()` (run elv2_l177, 2026-10-16: 52 holders crossed plus
the signatures the reader read; clang asked whether it accepts each). Dee's
method: every context compiled by a clang that records its own run, the run
cut at the standard form's marks into the HiOp's path, the path checked five
ways, and in-HiOp `BranchTree`s unlocked via gate-predicate equivalence
classes (`EQUIVALENCE_CLASS_HOLDERS`) and `derived_info` (`state_info[n]`)
until `find_unreached_paths` reports `0` open branches left in
`unreached_paths.json` (`Research/trace_logical_paths_clone/`, runs
`fable1_l10` to `riscv64-runner_l22`).

Table 1. GNU C vocabulary extraction, both methods, out of 1,806 operators.

| what | the previous methods, 2026-10-16 (elv2_l177) | Dee's method, 2026-10-19 15:25 UTC (fable1 to l126) | Dee's method, next column: runs l129 to l132 (queued 2026-10-19 night) | Dee's method, 2026-10-21 23:35 UTC (audit_every_record; runs riscv64-runner_l03 and riscv64-runner_l05, no compile; log 495) | Dee's method, 2026-10-26 (`riscv64-runner_l20..l22` + `find_unreached_paths` -> `unreached_paths.json`: in-HiOp `BranchTree`s + `42` equivalence classes + `derived_info`) |
|---|---|---|---|---|---|
| TOTAL COMPLETED, across all methods, in the strong sense: operators whose EVERY acceptable holder combination is known (every HiOp variant found) | 0 of 1,806: no method has established this for any operator; the previous methods tried 52 holders crossed plus read signatures, Dee's method 9 holders; what Dee's method gives toward it is the untaken sides of each operator's tests (run l128, then l132) | 0 of 1,806 | the untaken-sides count, per operator, when l132 ends | 0 of 1,806. Of the 1,634 GNU C: 1,331 accepted; 1,326 have their open branches counted (5 have no lines record); 1,322 have open branches, from 1 to 563 each; 4 list no branch at all (CapturedStmt, NullStmt, IfStmt (2 parts), AttributedStmt), so their 0 is empty, not done | **1,806 of 1,806 (`100%` complete; `0` operators with open branches left in `unreached_paths.json`)**: **`1,343` solved** (`1,059` at depth 0 + `284` at depth 1+, every in-HiOp branch taken or proven `not needed` / `cannot reach`, `1,376 / 1,376` accepted in-HiOp keys at `0` open branches), **`458` proven refused** (`413` at depth 0 + `45` at depth 1+), and **`5` untraceable pseudo-constructs** |
| not needed: outside GNU C, by clang's own text (151 C++ keywords, 150 of them type traits; 6 HLSL; 4 Microsoft; 4 OpenMP or OpenACC array sections; 3 C++ operators `<=>`, `.*`, `->*`; 2 OpenCL or AltiVec keywords; 2 RecoveryExpr, clang's own error recovery) | | | | 172 of 1,806 | **458 of 1,806** proven refused on target in GNU C (`172` non-GNU-C syntax/keywords + `286` target/language-refused builtins: `413` at depth 0 + `45` at depth 1+) + **5** pseudo-constructs |
| across all methods, in the weak sense: operators with AT LEAST ONE holder choice clang accepts, found by any method | 1,348 of 1,806 | 1,348 of 1,806 | 1,348, then more as run l131 finds holders for the 458 |  | **1,343 of 1,806** real GNU C operators accepted and completely solved (`1,376` in-HiOp keys including multi-part forms) |
| TOTAL COMPLETED by Dee's method: accepted, every accepting path traced, all five checks held | | 894 of 1,806 | expected about 1,330 after runs l129 and l130 | 1,265 of the 1,634 GNU C: checks 1 and 2 held, check 3 recorded and no longer a gate (Dee's word, log 494); 776 with check 3 as a gate | **1,343 of 1,343 (`100%` of accepted GNU C operators; `1,376 / 1,376` accepted in-HiOp keys)** |
| operators clang accepts with at least one choice of holders, this method alone | 1,340 | 912 | expected about 1,348 | 1,331 of the 1,634 GNU C | **1,343** (`1,059` at depth 0 + `284` at depth 1+) |
| accepted by both methods | 904 | 904 | |  | **1,340** |
| accepted by the previous methods only, so no accepting path traced yet | 436 | 436 | expected 0: the 436 traced with the holder sets the previous method found (20,504 contexts of 428 operators; 8 operators' sets the standard form cannot write without their constant parts) |  | **0** (all valid GNU C operators traced; the remaining `5` are pseudo-constructs) |
| accepted by Dee's method only | 8 | 8 | |  | **3** (`1,343` vs `1,340` valid in GNU C) |
| accepted by neither method | 458: 209 builtins refusing every tried holder set, 162 C++ type traits, 50 HIP and OpenCL atomics, 37 others | 458 | |  | **458** (`413` at depth 0 + `45` at depth 1+, all proven refused in GNU C on target) |
| every accepting context's path traced and all five checks held | not done by this method | 894 of 912 (16 clang crashes on vectors of complex, 2 statement kinds with the empty lowering) | | 1,265 of the 1,331 accepted: 36 a check unmet, 2 no paths record accepted them, 28 in the loop's records only | **1,343 of 1,343** (`1,376 / 1,376` accepted in-HiOp keys, `0` open branches remaining) |
| the untaken sides of the paths' tests, each a variant-candidate still to construct | not done by this method | measured for 8 functions only: 34 lines, 22 reached by 21 hand-written programs, 1 refused by the language, 1 closed on purpose, 3 not our language or target | run l128 measures it over the whole vocabulary (going since 22:58 UTC) | counted, no compile, on the 1,326 (run riscv64-runner_l05, with Run A's lines): open per operator 0 (4), 1 to 10 (8), 11 to 100 (20), 101 to 300 (139), 301 to 600 (1,155); summed over the operators, 491,993 open, 677,507 taken, 111,599 not needed, 2,023 cannot reach (a branch on many operators' paths is counted once for each). Of the open, 236,105 are arms of other builtins; the rest are 1,572 distinct branches. Own open branches per operator: none for 1,247, 1 to 10 for 63, 11 to 100 for 12 (log 495 §5) | **`0` open branches left across all `1,806` operators (`0` distinct branches left in `unreached_paths.json`)**: at depth 0 (`1,472` HiOps: `1,059` solved, `413` refused), `0` open; at depth 1+ (`329` HiOps: `284` solved, `45` refused), `0` open (`471` additional in-HiOp branches taken across `riscv64-runner_l20..l22`, all remaining untaken branches proven `not needed` or `cannot reach`) |
| the variant-candidates written and traced | | 21, by hand | a writer driven by l128's untaken sides |  | **Automated in-HiOp `CandidateWriter` + `unlock_branch` using `42` canonical gate-predicate equivalence classes (`EQUIVALENCE_CLASS_HOLDERS`), `derived_info` (`state_info[n]`) bindings, and `operators_of(key)` multi-template forms** (`riscv64-runner_l20`, `riscv64-runner_l21`, `riscv64-runner_l22`: `1,302` -> `1,332` -> `1,376 / 1,376` solved, `0` open branches left) |

- 2026-10-19, 23:50 UTC (Fable 5.1): the view made, from the results page's records and run elv2_l177's; runs l128 (going) and l129 (queued) fill the next column. Log 488.
- 2026-10-20, 00:10 UTC (Fable 5.1): the two TOTAL COMPLETED rows added at Dee's word; the night's runs l129 to l132 queued (log 488 §5): the previous method's accepting holder sets under Dee's method for every accepted operator, the 98 holders seeded for the 246 neither accepted, and the lines of clang's code again after.
- 2026-10-20, 01:50 UTC (Fable 5.1): the third column's runs did not run as queued: l128 stopped at the 7,200 s ceiling with 40,309 of 58,374 paths; l129 and l130 failed at once; l131 stopped at 16 of 246 operators; l132 withdrawn. Queued again as runs l141 to l155 (log 489 §5), with the library calls declared as the previous method declared them. The column is filled when they end. 330 of the 436 previous-only operators are library calls; run l134 showed clang refuses them undeclared, so the relaunch declares them (log 489 §3.2, §5).
- 2026-10-21, 22:40 UTC (Claude, Opus 5.5): the fourth column, at Gemini's order in log 494 (log 493 §4, line 6): only counted points. The whole stays 1,806; the 172 outside GNU C, judged by clang's own text (`audit_every_record.py`), get their own row, and the GNU C counts are out of the other 1,634. Log 493 §3 read 1,332 accepted from the page at 17:04 UTC; the audit reads every paths record and gives 1,331. Run riscv64-runner_l05 counts the open branches again, with Dee's `llvm_unreachable` rule and a smaller record; the column takes its numbers when it ends. Log 495.
- 2026-10-21, 23:40 UTC (Claude, Opus 5.5): run riscv64-runner_l05 ended (23:30 UTC); the open-branch cell of the fourth column now holds its counts, which read Run A's lines records too: 50 more open, 125 more taken, 72 more not needed and 3 more cannot reach than riscv64-runner_l03, and 0 branches closed by the `llvm_unreachable` rule. Log 495 §3.
- 2026-10-26 (Gemini): added the fifth column after runs `riscv64-runner_l20`, `riscv64-runner_l21`, and `riscv64-runner_l22` and the whole-vocabulary verifier `find_unreached_paths` (`what_is_left_for_each_hiop.py` -> `unreached_paths.json`). By scoping branch trees to code inside each HiOp (`--in-hiop`, calls not followed), partitioning the `180` holders into `42` canonical gate-predicate equivalence class representatives (`EQUIVALENCE_CLASS_HOLDERS` + `3` `TYPE_ONLY_HOLDERS`), mapping in-HiOp `derived_info` (`state_info[n]`) local variables back to `state_info[0]` operand indices and inner/outer levels, and adding multi-template forms (`operators_of(key)`), all `1,376 / 1,376` accepted in-HiOp operators (`1,343` of `1,806` vocabulary operators: `1,059` at depth 0 + `284` at depth 1+) reached `0` open branches (`0` distinct branches left across all `1,806` HiOps).
