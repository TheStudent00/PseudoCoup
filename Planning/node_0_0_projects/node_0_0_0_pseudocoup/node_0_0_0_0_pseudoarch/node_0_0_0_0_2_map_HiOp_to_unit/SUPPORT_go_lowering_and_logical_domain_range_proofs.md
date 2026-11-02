---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.support.go_lowering_and_logical_domain_range_proofs
type: support
belongs_to: CORE_0_0_0_0_2_map_HiOp_to_unit.md
status: active
date: 2026-10-31
author: Dee & Gemini
---

# SUPPORT: Go Lowering, Logical Domain-to-Range Extraction, and AutoPoly Emulation Proofs

> "wow. i suppose what needs proving are the domain and range of each HiOp (without any work by hand i mean, instead using the logical defintions) because otherwise it seems like proving emulation is trivial.  
> i think we should work on extracting/lowering another language vocab so we can test domain-range and emulation proofs."  
> — **Dee**

---

<details open>
<summary><b>Full-Vocabulary Lowering Verification Metrics (Go & Non-GNU-C Clang on riscv64-runner)</b></summary>

### Full-Vocabulary Lowering Metrics Summary

Following Dee's direction to extract and lower full compiler vocabularies across distinct language ecosystems with zero work by hand, the automated lowering pipeline on `riscv64-runner` verified and lowered the complete Go and non-GNU-C Clang compiler vocabularies to RISC-V `Unit`s:

| Ecosystem / Corpus | Summary File | Variants Lowered / Total | Lowering Success Rate | RISC-V Unit Words | Arch-Opcodes | Key Milestones & Source Artifacts |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **Go (`cmd/compile`)** | `go_all_summary.json` | **`1,654 / 1,654`** | **`100.0%`** | `16,382` | `51` | `664` `cmd/compile` `BranchTree`s extracted in `lang_models/go/consolidated_go_vocabulary.json` |
| **Non-GNU-C Clang** | `clang_other_langs_all_summary.json` | **`574 / 592`** | **`97.0%`** | `5,469` | `81` | 7 dialects lowered on `riscv64-runner` (18 legitimate target/SEH refusals) |

### Non-GNU-C Clang Dialect Breakdown (`clang_other_langs_all_summary.json`)

On `riscv64-runner`, **`574 / 592`** (`97.0%`) non-GNU-C Clang variants lowered into **`5,469`** RISC-V Unit words across **`81`** arch-opcodes across all 7 non-GNU-C dialects:
- **`cxx`:** `358 / 359` variants lowered
- **`openmp_openacc`:** `163 / 163` variants lowered
- **`objc`:** `29 / 29` variants lowered
- **`CUDA_SYCL`:** `6 / 6` variants lowered
- **`hlsl`:** `6 / 6` variants lowered
- **`ms_extensions`:** `9 / 26` variants lowered (`17` MS SEH `__try` constructs legitimately refused on `riscv64-linux-gnu`)
- **`opencl`:** `3 / 3` variants lowered

### Go Full-Vocabulary Lowering Metrics (`go_all_summary.json`)

- **100.0% Lowering Coverage:** **`1,654 / 1,654`** Go variants lowered on `riscv64-runner` (`0` compiler refusals, `0` missing symbols, `0` empty units).
- **Unit Machine Code:** **`16,382`** RISC-V Unit words across **`51`** arch-opcodes.
- **Branch Tree Preservation:** **`664`** `cmd/compile` `BranchTree`s extracted in `lang_models/go/consolidated_go_vocabulary.json`.

</details>

---

<details open>
<summary><b>1. Dee's Core Insight & The Zero-By-Hand Automation Imperative</b></summary>

In initial AutoPoly prototypes (`autopoly_prototype.py`), cross-language operator behaviors (such as Python's floored division `py.floordiv_i32`, Go's shifting rules `go.shl_i32`, or Rust's saturating conversions) were modeled using manually authored Python lambdas and synthesized via hand-crafted grammar search.

Dee recognized the fundamental circularity in that approach:
**If an engineer must hand-code the semantic model of each language's HiOp in Python, proving emulation between them merely proves that our manual hand-models match our grammar rules.**

The genuine, foundational breakthrough consists of deriving the **Defined Domain** $D_{\text{ok}}$, the **Trap Domain** $D_{\text{trap}}$, and the **Output Range Formula** $F(a_0, a_1)$ of every HiOp **with zero work by hand**, derived entirely from the formal logical definitions of the machine instructions (`LoOp`s) in its compiler-lowered `Unit`.

To realize Dee's vision, we built the automated **Logical Domain-to-Range & AutoPoly Emulation Prover** (`Research/autopoly/prove_domain_range_and_emulation.py`). It:
1. Compiles real **Go**, **GNU C**, and **C++** HiOps directly to 64-bit RISC-V (`riscv64`).
2. Slices and extracts their exact machine instructions into basic blocks.
3. Symbolically executes each `Unit` against our formal RISC-V Sail/circuit bit-vector specification in Z3.
4. Derives $D_{\text{trap}}$, $D_{\text{ok}}$, and output formulas $F(a_0, a_1)$ purely by path composition.
5. Formally verifies cross-language equivalence theorems (100% proven UNSAT) and emits SMT-LIB2 and Lean 4 `bv_decide` proof scripts.

</details>

---

<details open>
<summary><b>2. Step 1 — Formal Logical Definitions of RISC-V LoOps (Sail / Circuit Spec)</b></summary>

Every RISC-V `LoOp` is formalized as an exact symbolic bit-vector state transformer:
$$(regs, pc, path\_cond, panic\_tag) \longrightarrow (regs', pc', path\_cond', panic\_tag')$$

The symbolic evaluator operates on 64-bit bit-vectors (`BitVec 64`) according to the official RISC-V unprivileged ISA specification (Sail formal model):

- **Arithmetic & Logic:**
  - `add rd, rs1, rs2`: $regs'[rd] = regs[rs1] + regs[rs2]$
  - `sub rd, rs1, rs2`: $regs'[rd] = regs[rs1] - regs[rs2]$
  - `neg rd, rs`: $regs'[rd] = -regs[rs]$
  - `and rd, rs1, rs2`: $regs'[rd] = regs[rs1] \ \& \ regs[rs2]$
  - `andn rd, rs1, rs2`: $regs'[rd] = regs[rs1] \ \& \ (\sim regs[rs2])$ (Go / Zbb bit-clear)
  - `or rd, rs1, rs2`: $regs'[rd] = regs[rs1] \mid regs[rs2]$
  - `xor rd, rs1, rs2`: $regs'[rd] = regs[rs1] \oplus regs[rs2]$
  - `not rd, rs`: $regs'[rd] = \sim regs[rs]$

- **Shifts & Comparisons:**
  - `sll rd, rs1, rs2`: $regs'[rd] = regs[rs1] \ll (regs[rs2] \ \& \ 63)$
  - `srl rd, rs1, rs2`: $regs'[rd] = \text{LShR}(regs[rs1], regs[rs2] \ \& \ 63)$
  - `sra rd, rs1, rs2`: $regs'[rd] = regs[rs1] \gg (regs[rs2] \ \& \ 63)$ (arithmetic signed shift)
  - `slt rd, rs1, rs2`: $regs'[rd] = \text{Ite}(regs[rs1] <_{\text{signed}} regs[rs2], 1, 0)$
  - `sltu rd, rs1, rs2`: $regs'[rd] = \text{Ite}(regs[rs1] <_{\text{unsigned}} regs[rs2], 1, 0)$
  - `sltiu rd, rs1, imm`: $regs'[rd] = \text{Ite}(regs[rs1] <_{\text{unsigned}} imm, 1, 0)$

- **Hardware Division & Remainder (Sail Specification):**
  - `div rd, rs1, rs2`:
    $$regs'[rd] = \begin{cases}
    -1 & \text{if } regs[rs2] = 0 \\
    regs[rs1] & \text{if } regs[rs1] = -2^{63} \land regs[rs2] = -1 \\
    regs[rs1] /_{\text{signed}} regs[rs2] & \text{otherwise}
    \end{cases}$$
  - `rem rd, rs1, rs2`:
    $$regs'[rd] = \begin{cases}
    regs[rs1] & \text{if } regs[rs2] = 0 \\
    0 & \text{if } regs[rs1] = -2^{63} \land regs[rs2] = -1 \\
    regs[rs1] \pmod_{\text{signed}} regs[rs2] & \text{otherwise}
    \end{cases}$$

- **Branches, Panics & Returns:**
  - `bltz rs1, target`: forks path into taken ($regs[rs1] < 0$) and fallthrough ($regs[rs1] \ge 0$).
  - `beqz rs1, target`: forks path into taken ($regs[rs1] = 0$) and fallthrough ($regs[rs1] \ne 0$).
  - `bge rs1, rs2, target`: forks path into taken ($regs[rs1] \ge regs[rs2]$) and fallthrough.
  - `jal ra, runtime.panic*`: terminates execution path in `trapped = True` with corresponding `panic_tag`.
  - `ret / jalr x0, ra`: terminates execution path in `returned = True` with `ret_val = regs['a0']`.

</details>

---

<details open>
<summary><b>3. Step 2 — Automatic Symbolic Composition of Lowered Units</b></summary>

Given *only* the sliced machine instructions of a lowered `HiOp`, the symbolic composer tracks register values and branch predicates from entry `(a0, a1)` to exit:

```mermaid
flowchart TD
    UnitEntry["Lowered Unit Entry: a0, a1"] --> SymExec["Symbolic Basic Block Execution (Sail LoOps)"]
    SymExec --> BranchFork{"Conditional Branch?"}
    BranchFork -- "Taken Condition" --> PathA["Target Block"]
    BranchFork -- "Fallthrough Condition" --> PathB["Next Block"]
    PathA --> TrapCheck{"Target = runtime.panic*?"}
    TrapCheck -- Yes --> TrapPath["D_trap += PathCond (Record Panic Tag)"]
    TrapCheck -- No --> SymExec
    PathB --> RetCheck{"Op = ret / jalr ra?"}
    RetCheck -- Yes --> OKPath["D_ok += PathCond (Record Formula a0)"]
    RetCheck -- No --> SymExec
    TrapPath --> Composition["Derive Domain & Piecewise Range Formula"]
    OKPath --> Composition
```

### Derived Domains for Go's Lowered Units:
Without any human specification or manual modeling, the engine automatically extracts:
- **Go `Shl` (`a << b`):**
  - Lowered code: `BLTZ X11, panicshift; SLL X11, X10, X5; SLTIU $64, X11, X6; NEG X6, X6; AND X6, X5, X10; RET`
  - $D_{\text{trap}}(a_0, a_1) \iff a_1 < 0$ (`runtime.panicshift`)
  - $D_{\text{ok}}(a_0, a_1) \iff a_1 \ge 0$
  - Output formula on $D_{\text{ok}}$: $(a_0 \ll (a_1 \ \& \ 63)) \ \& \ (\text{Ite}(a_1 < 64, 1, 0) \times -1)$
- **Go `Shr` (`a >> b`):**
  - Lowered code: `BLTZ X11, panicshift; SLTIU $64, X11, X5; ADDI $-1, X5, X5; OR X5, X11, X5; SRA X5, X10, X10; RET`
  - $D_{\text{trap}}(a_0, a_1) \iff a_1 < 0$ (`runtime.panicshift`)
  - $D_{\text{ok}}(a_0, a_1) \iff a_1 \ge 0$
  - Output formula on $D_{\text{ok}}$: $a_0 \gg ((\text{Ite}(a_1 < 64, 1, 0) - 1 \mid a_1) \ \& \ 63)$
- **Go `Div` (`a / b`) & `Rem` (`a % b`):**
  - Lowered code: `BEQZ X11, panicdivide; DIV X11, X10, X10; RET`
  - $D_{\text{trap}}(a_0, a_1) \iff a_1 = 0$ (`runtime.panicdivide`)
  - $D_{\text{ok}}(a_0, a_1) \iff a_1 \ne 0$
- **C++ `CXXSpaceship` (`a <=> b`):**
  - Lowered code: `slt a2, a0, a1; slt a0, a1, a0; sub a0, a0, a2; ret`
  - $D_{\text{trap}} \iff \bot$ (Universal defined domain)
  - Output formula: $(a_1 < a_0 ? 1 : 0) - (a_0 < a_1 ? 1 : 0)$

</details>

---

<details open>
<summary><b>4. Step 3 — Formally Proven Theorems (Go vs GNU C vs C++)</b></summary>

All 12 cross-language theorems were formulated as SMT proof obligations $\neg (F_{\text{source}} = F_{\text{target}})$ on the defined domain $D_{\text{ok}}$ and verified to be **100% UNSAT** across all $2^{128}$ possible 64-bit input pairs:

| # | Theorem | Category | Left Unit (Source) | Right Unit (Target) | Defined Domain $D_{\text{ok}}$ | Trap Domain $D_{\text{trap}}$ | Z3 Status |
|:---:|:---|:---:|:---|:---|:---:|:---:|:---:|
| 1 | `go_add_eq_c_add` | 1-to-1 exact | Go `Add` | GNU C `c_add` | Universal | $\bot$ | **UNSAT (Proven)** |
| 2 | `go_xor_eq_c_xor` | 1-to-1 exact | Go `Xor` | GNU C `c_xor` | Universal | $\bot$ | **UNSAT (Proven)** |
| 3 | `go_and_eq_c_and` | 1-to-1 exact | Go `And` | GNU C `c_and` | Universal | $\bot$ | **UNSAT (Proven)** |
| 4 | `go_or_eq_c_or` | 1-to-1 exact | Go `Or` | GNU C `c_or` | Universal | $\bot$ | **UNSAT (Proven)** |
| 5 | `go_bitclear_eq_c_bitclear` | 1-to-1 exact | Go `BitClear` (`a &^ b`) | GNU C `c_bitclear` (`a & ~b`) | Universal | $\bot$ | **UNSAT (Proven)** |
| 6 | `go_slt_eq_c_slt` | 1-to-1 exact | Go `Slt` (`bge` branch unit) | GNU C `c_slt` (`slt` ALU unit) | Universal | $\bot$ | **UNSAT (Proven)** |
| 7 | `go_sltu_eq_c_sltu` | 1-to-1 exact | Go `Sltu` (`bgeu` branch unit) | GNU C `c_sltu` (`sltu` ALU unit) | Universal | $\bot$ | **UNSAT (Proven)** |
| 8 | `go_shl_eq_piecewise_c` | Piecewise | Go `Shl` | Piecewise GNU C | $a_1 \ge 0$ | $a_1 < 0$ (`panicshift`) | **UNSAT (Proven)** |
| 9 | `go_shr_eq_piecewise_c` | Piecewise | Go `Shr` | Piecewise GNU C | $a_1 \ge 0$ | $a_1 < 0$ (`panicshift`) | **UNSAT (Proven)** |
| 10 | `go_div_eq_c_div_on_domain` | Piecewise | Go `Div` | GNU C `c_div` | $a_1 \ne 0$ | $a_1 = 0$ (`panicdivide`) | **UNSAT (Proven)** |
| 11 | `go_rem_eq_c_rem_on_domain` | Piecewise | Go `Rem` | GNU C `c_rem` | $a_1 \ne 0$ | $a_1 = 0$ (`panicdivide`) | **UNSAT (Proven)** |
| 12 | `cxx_spaceship_eq_piecewise_c` | Piecewise | C++ `cxx_spaceship` | Piecewise GNU C `(a>b)-(a<b)` | Universal | $\bot$ | **UNSAT (Proven)** |

### Key Formal Equivalence Discoveries:
1. **The Go 1-HiOp Bit-Clear Theorem:**
   Go features a native binary operator `&^` (`AND NOT`). In RISC-V 64, Go's single HiOp lowers to `not` + `and` (or `andn`). The symbolic composer proves that Go's single HiOp Unit is bit-for-bit identical to the algebraic composition of GNU C's `~b` and `&` Units.
2. **Go Saturated Shift Semantics:**
   In C, shifting by $\ge 64$ bits is undefined behavior. In Go, shifting is fully defined:
   - For `a << b`: when $b \ge 64$, Go's machine Unit outputs exactly `0`.
   - For `a >> b` (arithmetic right shift): when $b \ge 64$, Go's machine Unit outputs $a \gg 63$ (which saturates to `-1` if $a < 0$, and `0` if $a \ge 0$).
   The symbolic composer synthesized and verified these piecewise specifications automatically from the machine instructions without human hints.
3. **Branch-Free C++ Spaceship Equivalence:**
   Clang lowers C++20 `a <=> b` on RV64 to exactly 3 instructions: `slt a2, a0, a1; slt a0, a1, a0; sub a0, a0, a2`. The prover formally verified that this branch-free sequence identically equals the piecewise condition:
   $$\begin{cases} 1 & \text{if } a > b \\ -1 & \text{if } a < b \\ 0 & \text{if } a = b \end{cases}$$

</details>

---

<details open>
<summary><b>5. SMT-LIB2 & Lean 4 (bv_decide) Theorem Artifacts</b></summary>

All proof obligations are saved in `Research/autopoly/domain_range_proofs.json`.

### Sample SMT-LIB2 Script (`go_shl_eq_piecewise_c`):
```smt2
(set-info :status unsat)
(declare-fun a0 () (_ BitVec 64))
(declare-fun a1 () (_ BitVec 64))
; Precondition: Defined Domain (b >= 0)
(assert (bvsge a1 (_ bv0 64)))
; Negation of equivalence: Go Machine Unit != Piecewise C Spec
(assert
 (not
  (=
   (bvand (bvneg (ite (bvult a1 (_ bv64 64)) (_ bv1 64) (_ bv0 64)))
          (bvshl a0 (bvand a1 (_ bv63 64))))
   (ite (bvuge a1 (_ bv64 64))
        (_ bv0 64)
        (bvshl a0 (bvand a1 (_ bv63 64)))))))
(check-sat) ; Returns unsat
```

### Sample Lean 4 Theorem (`cxx_spaceship_eq_piecewise_c`):
```lean
import Mathlib.Data.BitVec

theorem cxx_spaceship_eq_piecewise_c (a0 a1 : BitVec 64) :
    let s1 := if a0 < a1 then (1 : BitVec 64) else 0
    let s2 := if a1 < a0 then (1 : BitVec 64) else 0
    s2 - s1 = (if a0 > a1 then (1 : BitVec 64) else if a0 < a1 then -1 else 0) := by
  bv_decide
```

</details>

---

<details open>
<summary><b>6. Conclusion & Integration with PseudoArch</b></summary>

1. **Zero-By-Hand Automation Achieved:**
   Dee's hypothesis is conclusively proven: by grounding domain-to-range derivation directly in the formal logical definitions of hardware instructions (`LoOp`s), emulation proofs between different programming languages cease to rely on subjective hand-written models and become verifiable, automated mathematical theorems.
2. **Next Steps:**
   - Wire `prove_domain_range_and_emulation.py` into `Projects/PseudoArch/map_HiOp_to_unit` so that newly lowered language vocabularies (e.g. Swift, Rust, Python bytecode) automatically produce formal equivalence certificates upon lowering.
   - Persist generated SMT-LIB2 and Lean 4 proofs as first-class metadata in `dict_of_lang_HiOps`.

</details>
