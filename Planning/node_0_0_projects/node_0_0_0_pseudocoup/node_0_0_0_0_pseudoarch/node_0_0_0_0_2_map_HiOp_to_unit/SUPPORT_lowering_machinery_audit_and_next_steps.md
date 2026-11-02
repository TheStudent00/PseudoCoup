---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.lowering_machinery_audit_and_next_steps
status: draft
---

# SUPPORT — lowering_machinery_audit_and_next_steps

Complete status of **vocabulary extraction** (100% complete) and **lowering & ArchUnit extraction (`lower_HiOp` / `extract_unit_from_LoHiOp`)**: what the machinery covers, which historical issues were already solved, how the Unit workload collapses just like vocab extraction, and the concrete step to run `map_HiOp_to_unit` on our new `57,480`-variant consolidated vocabulary on the tower (`riscv64-runner`).

---

<details open>
<summary><b>1. Vocabulary Extraction Status: 100% Up to Date Across All Clang 21.1.8 Languages</b></summary>

Yes — vocabulary extraction and the `.NASCENT` code/planning migration are **100% complete and synced** across `PRIVATE/PseudoCoup`, `LOCAL/PseudoCoup(Gemini)`, and `riscv64-runner`:

| Scope | Total Keyed Operators | Accepted Operators | Genuine Compiler Refusals | Open Branches Remaining | Consolidated Distinct Path Variants | Canonical Dataset Location |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| **GNU C (`riscv64-runner_l23_gnu_c_whole`)** | `1,806` | `1,376` | `430` | **`0`** (`100%` closed) | **`57,480`** (`60,413` contexts) | [consolidated_gnu_c_vocabulary.jsonl.gz](file://Projects/PseudoArch/map_HiOp_to_unit/lang_models/gnu_c/unreached_paths/consolidated_gnu_c_vocabulary.jsonl.gz) |
| **All Other Clang Languages (`riscv64-runner_l24`: `cxx`, `openmp_openacc`, `objc`, `ms_extensions`, `CUDA_SYCL`, `hlsl`, `opencl`, `clang_recovery`)** | `528` (`356` disjoint from GNU C) | `444` (`437` new beyond GNU C) | `84` | **`0`** (`100%` closed) | **`592`** (`577` new beyond GNU C) | [consolidated_all_clang_languages_vocabulary.jsonl.gz](file://Projects/PseudoArch/map_HiOp_to_unit/lang_models/consolidated_all_clang_languages_vocabulary.jsonl.gz) |
| **Combined Clang 21.1.8 Total** | **`2,162`** | **`1,820`** | **`342`** | **`0`** | **`58,057`** | [Projects/PseudoArch/map_HiOp_to_unit/lang_models/](file://Projects/PseudoArch/map_HiOp_to_unit/lang_models) |

</details>

---

<details open>
<summary><b>2. What the Lowering &amp; Unit-Extraction Machinery Covers (And What Historical Issues Were Solved)</b></summary>

The lowering and Unit-extraction pipeline in [Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp) is **already built and verified** across `321,882` lowered GNU C variants on `riscv64`, `x86_64`, and `aarch64` (`elv2_l156` and `elv2_l160`).

### 2.1. The 4 Sub-Nodes of `lower_HiOp`

1. **[standard_HiOp_wrapper.py](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/standard_HiOp_wrapper.py) (`0_0_0_0_2_2_0_standard_HiOp_wrapper` — `1,091` lines):**
   - Wraps each HiOp variant in a standard C function `void op_k(struct P_k *p)` where the caller-owned `struct P_k` holds the operand fields (`p->a`, `p->b`, ...) and `p->result`.
   - Places the HiOp on its own `\t`-indented source line (`HiOp_on_its_own_line`) so DWARF debug info (`-g`) attaches a unique line number (`HiOp_line`) to the HiOp's instructions, separate from the opening `{` and closing `}`.
2. **`compile_standard_source` in [lower_HiOp/__init__.py](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/__init__.py) (`0_0_0_0_2_2_1_compile_standard_source`):**
   - Compiles batches of `2,000` standard functions per `.c` file with `clang -std=gnu17 -O0 -g --target=riscv64-unknown-linux-gnu -nostdlibinc -ferror-limit=0 -c`.
   - If a batch has any compiler refusal, `map_batch` in [map_HiOp_to_unit/__init__.py](file://Projects/PseudoArch/map_HiOp_to_unit/__init__.py) automatically bisects/isolates the refused function(s) and compiles the rest.
3. **`read_words_at_symbol` in [lower_HiOp/__init__.py](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/__init__.py) (`0_0_0_0_2_2_2_read_words_at_symbol`):**
   - Uses `llvm-nm --print-size --defined-only` and `llvm-objdump -d -r -l -M no-aliases` to read each function's machine words (`LoHiOp`) as architectural opcodes with their DWARF source line numbers and relocations.
4. **[extract_unit_from_LoHiOp.py](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/extract_unit_from_LoHiOp.py) (`0_0_0_0_2_2_3_extract_unit_from_LoHiOp` — `175` lines):**
   - Cuts each `LoHiOp` down to `Unit(symbol, words, parts, holds_p, refusal)`:
     1. **DWARF Line Cut (`words_on_line`):** Keeps only words whose DWARF line equals `HiOp_line`, cleanly removing the wrapper's stack frame setup (`addi sp, sp, -0x20`, `sd ra`, `sd s0`) and return (`ld ra`, `ld s0`, `c.jr ra`).
     2. **Wrapper Pointer `p` Cut (`without_the_copy_of_p`):** Removes the `-O0` stack reload of the struct pointer `p` (`ld a1, -0x18(s0)`) and records `(word_index, register_name)` in `Unit.holds_p`.
     3. **Sub-Body Part Markers (`parts_called`):** Extracts any `R_RISCV_CALL_PLT part_k_*` relocations into `Unit.parts`.

### 2.2. The 5 Historical Issues You Remember — All 5 Were Solved in `lower_HiOp`

| Historical Issue During `lower_HiOp` Research | How It Was Solved | Verification Result (`elv2_l156` / `elv2_l160`) |
| :--- | :--- | :--- |
| **1. Isolating the HiOp's instructions from the function prologue/epilogue** | Put the HiOp on its own `\t`-indented line (`HiOp_line`) and filter `llvm-objdump -l` by `word.line == HiOp_line` (the owner's ruling, logs 440 & 446). | Across `321,882` lowered `riscv64` Units (`7,161,872` total words), **`0` frame-opening words** and **`0` spurious returns** leaked into any Unit ([units_of_cut_without_the_copy_of_p_all.txt](file://Research/lower_HiOp/out/units_of_cut_without_the_copy_of_p_all.txt)). |
| **2. Clang `-O0` reloading the wrapper struct pointer `p` (`ld a1, -0x18(s0)`) on the HiOp's line** | `extract_unit_from_LoHiOp.without_the_copy_of_p` identifies the stack slot where `a0` (`p`) was spilled in the prologue, strips every load from that slot out of `Unit.words`, and records the target register in `Unit.holds_p` (log 453). | Stripped `509,236` loads of `p` across `292,248` `riscv64` Units with **`0` faults** ([cut_without_the_copy_of_p.txt](file://Research/lower_HiOp/out/cut_without_the_copy_of_p.txt)). `a + b (int, int)` is cut from `15` words to the exact `4` words: `c.lw a0, 0x0(a1) . c.lw a2, 0x4(a1) . c.addw a0, a2 . c.sw a0, 0x8(a1)`. |
| **3. Control statements (`if`, `for`, `while`, `switch`, `goto`, `break`, `return`) having empty bodies or dead jumps deleted** | `HiOp_configuration_solver` routing (`ROUTING` in `mask_maker.py`) places inert calls (`part_k_a()`, `part_k_b()`) in each body/test slot so the compiler emits the full control skeleton with `R_RISCV_CALL_PLT part_k_*` relocations marking where each body goes (logs 399 & 424). | All `36,153` control/body variants on `riscv64` preserve their exact branch structure and `Unit.parts` list (`['part_8697_a', 'part_8697_b', 'part_8697_c']`). |
| **4. `riscv64` disassembler truncating `1,172` Units (`&&m`, `__scoped_atomic_thread_fence`, `_Float16` constants) at internal `.Lpcrel_hi0` / `.Ltmp0` labels** | `lower_HiOp.symbol_bodies` reads symbol byte sizes from `llvm-nm --print-size` so local labels with size `0` inside a function no longer split the function body (log 449). | All `1,172` previously truncated `riscv64` Units gained their full trailing instructions (`0` short reads remaining). |
| **5. Bit-field places (`q->r = q->a + q->b`) changing instruction words vs. ordinary struct fields** | Modelled once in [model_contexts.py](file://Projects/PseudoArch/map_HiOp_to_unit/model_lang_parts/context/model_contexts.py) (`model_lang_parts/context/model_contexts.py`, log 479) and verified on `19,999` random input pairs (`SUPPORT_gnu_c_bit_fields_walk.py`). | `100%` match on `riscv64` bit-field load/mask/insert sequences. |

</details>

---

<details open>
<summary><b>3. Why Most HiOp Units Are Simple — And How That Collapses Our Workload</b></summary>

Your intuition is completely right: just as vocabulary extraction collapsed from millions of brute-force probes to `57,480` equivalence-class variants, **Unit extraction and modelling collapse along three dimensions**:

### Reduction 1: Equivalence-Class Vocabulary Already Cut the Unit Count by `5.6x` (`321,882` $\rightarrow$ `57,480`)
- The earlier lowering runs (`elv2_l156` / `elv2_l160`) lowered **`321,882` brute-force grid cells** across `1,115` operators, because every holder combination was lowered separately even when Clang took the exact same internal code path.
- Our new consolidated GNU C vocabulary (`consolidated_gnu_c_vocabulary.jsonl.gz`) covers **`1,376` accepted operators (`+261` more operators)** in only **`57,480` distinct path variants** (`5.6x` fewer Units to lower!).

### Reduction 2: Anatomy of the Lowered RISC-V Units (`88.8%` Pure Expressions, `68.4%` Zero Calls)
From the full `riscv64` Unit cut ([units_of_cut_without_the_copy_of_p_all.txt](file://Research/lower_HiOp/out/units_of_cut_without_the_copy_of_p_all.txt) and [calls_to_runtime_routines.txt](file://Research/lower_HiOp/out/calls_to_runtime_routines.txt)):

| Unit Category on `riscv64` | Share of Lowered Units | What the Unit Looks Like | Why the Workload Collapses |
| :--- | ---: | :--- | :--- |
| **1. Pure Inline Straight-Line Units (No `parts`, No Runtime Calls)** | **`~57.2%`** (`184,500+` in old grid) | `4–12` inline RISC-V instructions (`lw`/`fld` $\rightarrow$ arithmetic/logic/cast $\rightarrow$ `sw`/`fsd`), e.g. `a + b` (`4` words), `a++` (`4` words). | **Zero external dependencies.** Each Unit is a self-contained sequence of RISC-V LoOps whose Sail/Lean definitions already exist. |
| **2. Units That Call Shared Runtime Infrastructure (`compiler-rt` / `libatomic`)** | **`~31.6%`** (`97,167` in old grid) | Argument load + `jalr` to one of **only `56` runtime functions** (`77,332` `long double` `tf` calls like `__addtf3`/`__extenddftf2`, `15,964` `__int128` `ti` calls like `__divti3`, `913` `_Float16`/`__bf16` calls, `492` `libatomic` calls, `350` complex mul/div calls). | **`97,167` variants reduce to `56` runtime functions**, and `compiler-rt` was already lowered whole for `riscv64` in `elv2_l159` ([lower_compiler_rt_whole.py](file://Research/lower_HiOp/lower_compiler_rt_whole.py))! |
| **3. Control / Body Units (`Unit.parts != []`)** | **`~11.2%`** (`36,153` in old grid) | Branch skeleton around inert calls `part_k_a`, `part_k_b` (e.g., `if (a) b; else c;` is `10` words; `while (a) b;` is `8` words). | **Inert body types don't change the Unit!** Across all `34,877` kept control HiOps on `riscv64`, there are **only `769` distinct control Units** (`elv2_l113`, log 405), because the body is an opaque call `part_k_b()` regardless of what holder type sits in `b`! |
| **4. Zero-Word / Pure-Annotation Units (`len(Unit.words) == 0`)** | **`~0.36%`** (`1,159` in old grid) | `0` instructions (`NullStmt`, `CompoundStmt`, `__builtin_assume`, `__builtin_unreachable`, `__xray_customevent`, `va_end`). | **Trivial no-op Units** (`0` LoOps to execute). |

</details>

---

<details open>
<summary><b>4. What Remains to Finish Lowering on Our New 100% Vocabulary (Tower <code>riscv64-runner</code>)</b></summary>

Because the core compiler/disassembler/slicer in [Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp) is already built and verified, **only one bridge step remains** to produce the complete `Unit` dataset for our new `1,376` GNU C operators (`57,480` path variants):

1. **Wire [standard_HiOp_wrapper.py](file://Projects/PseudoArch/map_HiOp_to_unit/lower_HiOp/standard_HiOp_wrapper.py) to the New Consolidated Vocabulary Contexts:**
   - The old runner ([Research/lower_HiOp/lower_gnu_c.py](file://Research/lower_HiOp/lower_gnu_c.py)) read the old `1,115`-operator grid (`c.knowns.jsonl.gz`) and `13` holder typedefs (`C_HELD_TYPES`).
   - Our new `consolidated_gnu_c_vocabulary.jsonl.gz` (`1,376` operators, `57,480` path variants) already stores the exact accepted `holders` (from our `26` equivalence-class holder types in [entry_context.py](file://Projects/PseudoArch/map_HiOp_to_unit/model_lang_parts/context/entry_context.py)) and any per-variant `setup` / `preamble` / `program` overrides that unlocked the remaining `261` operators.
2. **Run the Full `map_HiOp_to_unit` Pass on the Tower (`riscv64-runner`):**
   - Lowering `57,480` variants in batches of `2,000` is only **`29` Clang invocations** on `riscv64-runner` (compared to `162` batches in the old `321,882`-variant run) — it will finish in **under 2 minutes on `riscv64-runner`**!
   - We can also lower the **`592` accepted non-GNU-C Clang variants** (`cxx`, `openmp_openacc`, `objc`, `ms_extensions`, `CUDA_SYCL`, `hlsl`, `opencl`) on `riscv64-runner` right alongside GNU C.

</details>
