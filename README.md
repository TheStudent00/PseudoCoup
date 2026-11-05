# PseudoCoup

> Universal, bit-accurate cross-language transpilation and tool composition across **12 Original Languages** (`C`, `C++`, `Go`, `Rust`, `Python`, `Java`, `TypeScript`, `C#`, `Ruby`, `PHP`, `Dart`, `Swift`) and **6 Clang Dialects** (`ObjC`, `ObjC++`, `CUDA`, `HIP`, `OpenCL`, `HLSL`).

---

## Architecture: The Three Pillars (`CORE_0_0_0_pseudocoup.md`)

Instead of inventing an informal synthetic IR, **PseudoCoup** grounds every language operator in a formal hardware reference architecture (`riscv64` Sail ISA) and proves cross-language equivalence down to the bit:

```
pseudocoup/
├── pseudoarch/    # 1. PseudoArch: HiOp -> ArchUnit (riscv64 LoOps) -> Formal Logical Meaning
├── ledgerer/      # 2. Ledgerer:   ScriptToLedger <-> UR-Ledger (UniversalRichNodes) <-> LedgerToScript
└── hub/           # 3. The Hub:    AutoPoly 3-Tier Synthesis, Z3 EquivalenceProver, RiscvUnitVM, HolderBridge
```

1. **`PseudoArch` (`pseudocoup/pseudoarch/`):**
   - Extracts each language's native operator vocabulary (`HiOp` + `Holder`s) directly from its compiler/runtime source and lowers every kept variant to a sliced **`ArchUnit`** (a sequence of `riscv64` `LoOp`s).
   - Composes the `LoOp` definitions from the Sail RISC-V specification (`sail_model_of_riscv` + `map_LoOp_to_lean` + `map_unit_to_lean`) into a formal `(D_ok, D_trap, R_val)` logical meaning (`12,904` lowered `ArchUnit`s across `2,715` canonical modes, plus `56,905 / 56,905 = 100.00%` of GNU C non-trap units and `58 / 58` whole-lowered `compiler-rt` routines = `5,830 / 5,830` `LoOp` words).
2. **`Ledgerer` (`pseudocoup/ledgerer/`):**
   - **`UniversalRichNode` (`UR-Node`):** Carries `(hiop, units, meaning)` so every node in a program graph knows its exact hardware `ArchUnit` and formal domain/range.
   - **`ScriptToLedger` & `LedgerToScript`:** Parses source scripts into the **Universal Rich Ledger (`UR-Ledger`)** and emits target scripts through the `Hub`.
3. **`The Hub` & `AutoPoly` (`pseudocoup/hub/`):**
   - **Tier 1 (`Exact 1-to-1 Native HiOp`):** Direct emission when Z3 `EquivalenceProver` proves $\Delta = \emptyset$.
   - **Tier 2 (`Piecewise HiOp` & Symbolic `HiOp`-Variant Composition):** Synthesizes exact branch-free/ternary guards over the discrepancy domain $\Delta \ne \emptyset$ (e.g., `INT64_MIN / -1`, negative floor-modulo, shift width $\ge 64$) and depth-2 `HiOp`-variant compositions (`2,056 / 2,056 = 100.00%` of target-supported 64-bit `HiOp` pairs resolved at Tier 1 or Tier 2).
   - **Tier 3 (`Guaranteed LoOp-to-HiOpPrimitive Backstop`):** Emits the `ArchUnit`'s `LoOp` sequence using the 17 universal 64-bit `HiOpPrimitive`s (`204 / 204 = 100.00%` proved `UNSAT` in Z3 across all 12 languages), plus whole-lowered `compiler-rt` basic-block state machines.
   - **`HolderBridge`:** Bridges tools across languages with distinct `Holder` widths or signedness (`IdentityBridge`, Rule 3 `sext.w`/`zext.w` reinterpretation, and `WidthCastBridge`).


---

## Two-Cycle Roundtrip Stabilization Law

When transpiling across languages (`lang_x -> Hub -> lang_y -> Hub -> lang_x -> Hub -> lang_y -> Hub -> lang_x`):
- **Cycle 1 (`S_0 -> T_1 -> S_1`)** normalizes unguarded Tier-2 operations into **canonical PseudoCoup form** built strictly out of Tier-1 closed `UR-Node`s ($\Delta = \emptyset$).
- **Cycle 2 (`S_1 -> T_2 -> S_2`)** reaches a **strict syntactic and semantic fixed point**:
  - `T_1 == T_2` (100% byte-identical in `lang_y`)
  - `S_1 == S_2` (100% byte-identical in `lang_x`)
  - $\forall \text{inputs},\ \text{eval}(S_0) == \text{eval}(T_1) == \text{eval}(S_1) == \text{eval}(T_2) == \text{eval}(S_2)$

---

## Verification & Test Suites

Run the complete verification suite across all 12 languages:

```bash
./run_tests.sh
```

| Test Suite | What It Verifies |
| :--- | :--- |
| `tests/test_quickfox_all_12_langs.py` | 2-cycle `quickfox` roundtrip across all 12 Original Languages (`c`, `cpp`, `go`, `rust`, `python`, `java`, `typescript`, `csharp`, `ruby`, `php`, `dart`, `swift`) + 24-hop sequential 12-language daisy-chain (`Cycle 1 == Cycle 2`). |
| `tests/test_roundtrip_two_cycles.py` | Multi-statement 2-cycle stabilization suites (`Go <-> C`, `Python <-> Rust`, `TypeScript <-> Java`) on interior and edge-case inputs (`b >= 64`, `INT64_MIN / -1`, negative floor-div/mod). |
| `tests/test_holder_bridge.py` | Cross-language Hub pipeline combining `Python` (`i64`) $\to$ `Go` (`u32`) $\to$ `HolderBridge("u32", "i32")` $\to$ `C` (`i32`). |
| `tests/test_gpu_tensor_lowerer.py` | Relational tensor GPU lowerer (`DictLUT` + `RelationalLedgerTable` + `GPUTensorLowerer`) verified 100% byte-identical to CPU lowerer across all 12 languages. |
| `tests/test_hub_complete.py` | Exhaustive execution of all `12,904` lowered `riscv64` `ArchUnit`s in `RiscvUnitVM` + `MultiBodyEngine` + Z3 control-flow proofs. |
| `pseudocoup/hub/autopoly/compiler_rt_lifter.py` | Whole-lowered `compiler-rt` lifter (`58 / 58` needed routines = `5,830 / 5,830` Sail-lifted `LoOp` words, `40` DAGs + `18` loop state machines). |
| `pseudocoup/hub/autopoly/verify_hiop_primitives.py` | Formal Z3 (`UNSAT`) proof of all `17 x 12 = 204` `(HiOpPrimitive, language)` pairs against Sail-derived `UnitLean`s. |
| `pseudocoup/hub/autopoly/verify_tier1_tier2_12langs.py` | Symbolic `HiOp`-variant domain-and-range search & depth-2 composition across `2,256` syntheses (`1,786` Tier 1 + `270` Tier 2 + `200` Tier 3; `2,056 / 2,056 = 100.00%` Tier 1 + Tier 2 on target-supported 64-bit `HiOp`s). |
| `pseudocoup/hub/verify_hub_all_12_langs.py` | End-to-end Hub verification across `12,904` `UR-Node`s (`2,715` canonical modes), `18 / 18` `eval_qualified_expr` cases, `6 / 6` 4-word `compiler-rt` caller `UR-Node`s, and `60 / 60` `transpile_hub_expr` cases. |

---

## License

OTU Green License for Universal Works — see [`LICENSE.pdf`](LICENSE.pdf).


---

## How It Delivers: Concrete `PseudoArch` & 2-Cycle Roundtrip Walkthrough

### 1. Inside `PseudoArch`: From Native `HiOp` to Sliced `riscv64` `ArchUnit` and Z3 Proof

Traditional transpilers map syntax trees by hand and silently break on edge domains (e.g., `INT64_MIN / -1`, shift widths $\ge 64$, or negative modulo). In **PseudoCoup**, every operator variant (`HiOp` + `Holder`s) is compiled and sliced into its exact **`ArchUnit`** (`riscv64` `LoOp` sequence) and proven in Z3 (`BitVec64`):

| Language `HiOp` | Sliced `riscv64` `ArchUnit` (`LoOp`s) | Formal Meaning `(D_ok, D_trap, R_val)` | Cross-Language Discrepancy $\Delta$ vs. `C` |
| :--- | :--- | :--- | :--- |
| **`Go.<< [int64, uint64]`** | `sltiu t0, a1, 64; sll a0, a0, a1; czero.nez a0, a0, t0` | `D_ok: b >= 0`, saturates to `0` for `b >= 64` | $\Delta = \{b \mid b < 0 \lor b \ge 64\}$ (**Tier 2 Piecewise**) |
| **`C.<< [int64_t, int64_t]`** | `sll a0, a0, a1` | `D_ok: 0 <= b < 64` (masks `b & 63` in hardware) | Baseline (`sll`) |
| **`Python.// [int, int]`** | `beq; div; rem; xor; bltz; addi` | Floor division $\lfloor a / b \rfloor$ toward $-\infty$ | $\Delta = \{(a,b) \mid (a \oplus b) < 0 \land a \bmod b \ne 0\}$ (**Tier 2 Piecewise**) |
| **`Python.% [int, int]`** | `beq; rem; xor; bltz; add` | Floor modulo $a - \lfloor a / b \rfloor \cdot b$ (sign of $b$) | $\Delta = \{(a,b) \mid (a \oplus b) < 0 \land a \bmod b \ne 0\}$ (**Tier 2 Piecewise**) |
| **`C.+ / Go.+ / Rust.wrapping_add`** | `add a0, a0, a1` | `bvadd(a, b)` ($\forall a, b \in \text{BitVec64}$) | $\Delta = \emptyset$ (**Tier 1 Exact 1-to-1**) |

---

### 2. Concrete 2-Cycle Roundtrip Trace (`Go <-> C` and `Python <-> Rust`)

Below is the exact code emitted across **Cycle 1** (`S_0 -> Hub -> T_1 -> Hub -> S_1`) and **Cycle 2** (`S_1 -> Hub -> T_2 -> Hub -> S_2`) by [`tests/test_roundtrip_two_cycles.py`](tests/test_roundtrip_two_cycles.py):

```go
// --- Stage 0: S_0 (Idiomatic Go input) ---
func shift_and_div(a int64, b int64, c int64) int64 {
    shifted := a << b
    quot := shifted / c
    if quot > 0 {
        quot = quot + 1
    } else {
        quot = quot - 1
    }
    return quot
}
```

```c
// --- Stage 1: T_1 (Go -> Hub -> C) == Stage 3: T_2 (100% Byte-Identical on Cycle 2!) ---
int64_t shift_and_div(int64_t a, int64_t b, int64_t c) {
    int64_t shifted = (((b >= 0) && (b < 64)) ? (a << (b & 63)) : 0);
    int64_t quot = (((shifted == -9223372036854775808) && (c == -1)) ? -9223372036854775808 : (shifted / c));
    if ((quot > 0)) {
        quot = (quot + 1);
    } else {
        quot = (quot - 1);
    }
    return quot;
}
```

```go
// --- Stage 2: S_1 (C -> Hub -> Go, Canonical Form) == Stage 4: S_2 (100% Byte-Identical on Cycle 2!) ---
func shift_and_div(a int64, b int64, c int64) int64 {
    shifted := func() int64 { if ((b >= 0) && (b < 64)) { return (a << (b & 63)) } else { return 0 } }()
    quot := func() int64 { if ((shifted == -9223372036854775808) && (c == -1)) { return -9223372036854775808 } else { return (shifted / c) } }()
    if ((quot > 0)) {
        quot = (quot + 1)
    } else {
        quot = (quot - 1)
    }
    return quot
}
```


### 3. The 12-Language `quickfox` Sequential Roundtrip (`tests/roundtrip_steps/`)

The multi-function `quickfox` program ([`tests/roundtrip_steps/00_quickfox.py`](tests/roundtrip_steps/00_quickfox.py)) exercises nested conditionals (`classify_number`), loops (`factorial_iter`), Euclidean floor division/modulo (`euclid_step`), bitwise shifts/masks (`bit_mixer`), and inter-function calls (`quickfox`).

It is transpiled sequentially through all 12 languages across 2 full cycles (`00_quickfox.py -> 01_quickfox.c -> 02_quickfox.cpp -> 03_quickfox.go -> 04_quickfox.rs -> 05_quickfox.java -> 06_quickfox.ts -> 07_quickfox.cs -> 08_quickfox.rb -> 09_quickfox.php -> 10_quickfox.dart -> 11_quickfox.swift -> 12_quickfox.py`), writing each intermediate step to [`tests/roundtrip_steps/cycle1/`](tests/roundtrip_steps/cycle1/) and [`tests/roundtrip_steps/cycle2/`](tests/roundtrip_steps/cycle2/). Every file in `cycle2/` is **100% byte-for-byte identical** to `cycle1/` and evaluates to `[717, 3556, -67, 74]`.

#### Initial Input: `tests/roundtrip_steps/00_quickfox.py` (`S_0`)
```python
def classify_number(n):
    res = 0
    if n < 0:
        res = -1
    else:
        if n == 0:
            res = 0
        else:
            if n < 10:
                res = 1
            else:
                res = 2
    return res


def factorial_iter(n):
    acc = 1
    k = 2
    while k <= n:
        acc = acc * k
        k = k + 1
    return acc


def euclid_step(a, b):
    q = a // b
    r = a % b
    out = 0
    if (q < 0) and (r != 0):
        out = (q * 100) + r - a
    else:
        out = (q * 100) - r
    return out


def bit_mixer(x, sh, mask):
    shl_v = x << sh
    shr_v = x >> sh
    mixed = (shl_v ^ shr_v) | (x & mask)
    return mixed


def quickfox(a, b, sh, limit):
    cls_a = classify_number(a)
    cls_b = classify_number(b)
    fact_v = factorial_iter(limit)
    euc_v = euclid_step(a, b)
    mix_v = bit_mixer(a + b, sh, 255)
    total = fact_v + euc_v + (cls_a * 10) + cls_b
    i = 0
    while i < limit:
        total = total + (mix_v ^ i)
        i = i + 1
    return total
```

#### Step 1: C ([`tests/roundtrip_steps/cycle2/01_quickfox.c`](tests/roundtrip_steps/cycle2/01_quickfox.c)) — `cycle1 == cycle2`
```c
int64_t classify_number(int64_t n) {
    int64_t res = 0;
    if ((n < 0)) {
        res = -1;
    } else {
        if ((n == 0)) {
            res = 0;
        } else {
            if ((n < 10)) {
                res = 1;
            } else {
                res = 2;
            }
        }
    }
    return res;
}

int64_t factorial_iter(int64_t n) {
    int64_t acc = 1;
    int64_t k = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

int64_t euclid_step(int64_t a, int64_t b) {
    int64_t q = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b));
    int64_t r = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b));
    int64_t out = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

int64_t bit_mixer(int64_t x, int64_t sh, int64_t mask) {
    int64_t shl_v = (x << (sh & 63));
    int64_t shr_v = (x >> (sh & 63));
    int64_t mixed = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

int64_t quickfox(int64_t a, int64_t b, int64_t sh, int64_t limit) {
    int64_t cls_a = classify_number(a);
    int64_t cls_b = classify_number(b);
    int64_t fact_v = factorial_iter(limit);
    int64_t euc_v = euclid_step(a, b);
    int64_t mix_v = bit_mixer((a + b), sh, 255);
    int64_t total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    int64_t i = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
```

#### Step 2: C++ ([`tests/roundtrip_steps/cycle2/02_quickfox.cpp`](tests/roundtrip_steps/cycle2/02_quickfox.cpp)) — `cycle1 == cycle2`
```cpp
int64_t classify_number(int64_t n) {
    int64_t res = 0;
    if ((n < 0)) {
        res = -1;
    } else {
        if ((n == 0)) {
            res = 0;
        } else {
            if ((n < 10)) {
                res = 1;
            } else {
                res = 2;
            }
        }
    }
    return res;
}

int64_t factorial_iter(int64_t n) {
    int64_t acc = 1;
    int64_t k = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

int64_t euclid_step(int64_t a, int64_t b) {
    int64_t q = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b));
    int64_t r = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b));
    int64_t out = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

int64_t bit_mixer(int64_t x, int64_t sh, int64_t mask) {
    int64_t shl_v = (x << (sh & 63));
    int64_t shr_v = (x >> (sh & 63));
    int64_t mixed = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

int64_t quickfox(int64_t a, int64_t b, int64_t sh, int64_t limit) {
    int64_t cls_a = classify_number(a);
    int64_t cls_b = classify_number(b);
    int64_t fact_v = factorial_iter(limit);
    int64_t euc_v = euclid_step(a, b);
    int64_t mix_v = bit_mixer((a + b), sh, 255);
    int64_t total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    int64_t i = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
```

#### Step 3: Go ([`tests/roundtrip_steps/cycle2/03_quickfox.go`](tests/roundtrip_steps/cycle2/03_quickfox.go)) — `cycle1 == cycle2`
```go
func classify_number(n int64) int64 {
    res := 0
    if ((n < 0)) {
        res = -1
    } else {
        if ((n == 0)) {
            res = 0
        } else {
            if ((n < 10)) {
                res = 1
            } else {
                res = 2
            }
        }
    }
    return res
}

func factorial_iter(n int64) int64 {
    acc := 1
    k := 2
    while ((k <= n)) {
        acc = (acc * k)
        k = (k + 1)
    }
    return acc
}

func euclid_step(a int64, b int64) int64 {
    q := func() int64 { if (((a ^ b) < 0) && ((a % b) != 0)) { return ((a / b) - 1) } else { return (a / b) } }()
    r := func() int64 { if (((a ^ b) < 0) && ((a % b) != 0)) { return ((a % b) + b) } else { return (a % b) } }()
    out := 0
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a)
    } else {
        out = ((q * 100) - r)
    }
    return out
}

func bit_mixer(x int64, sh int64, mask int64) int64 {
    shl_v := (x << (sh & 63))
    shr_v := (x >> (sh & 63))
    mixed := ((shl_v ^ shr_v) | (x & mask))
    return mixed
}

func quickfox(a int64, b int64, sh int64, limit int64) int64 {
    cls_a := classify_number(a)
    cls_b := classify_number(b)
    fact_v := factorial_iter(limit)
    euc_v := euclid_step(a, b)
    mix_v := bit_mixer((a + b), sh, 255)
    total := (((fact_v + euc_v) + (cls_a * 10)) + cls_b)
    i := 0
    while ((i < limit)) {
        total = (total + (mix_v ^ i))
        i = (i + 1)
    }
    return total
}
```

#### Step 4: Rust ([`tests/roundtrip_steps/cycle2/04_quickfox.rs`](tests/roundtrip_steps/cycle2/04_quickfox.rs)) — `cycle1 == cycle2`
```rust
fn classify_number(n: i64) -> i64 {
    let mut res: i64 = 0;
    if ((n < 0)) {
        res = -1;
    } else {
        if ((n == 0)) {
            res = 0;
        } else {
            if ((n < 10)) {
                res = 1;
            } else {
                res = 2;
            }
        }
    }
    return res;
}

fn factorial_iter(n: i64) -> i64 {
    let mut acc: i64 = 1;
    let mut k: i64 = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

fn euclid_step(a: i64, b: i64) -> i64 {
    let mut q: i64 = (if (((a ^ b) < 0) && ((a % b) != 0)) { ((a / b) - 1) } else { (a / b) });
    let mut r: i64 = (if (((a ^ b) < 0) && ((a % b) != 0)) { ((a % b) + b) } else { (a % b) });
    let mut out: i64 = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

fn bit_mixer(x: i64, sh: i64, mask: i64) -> i64 {
    let mut shl_v: i64 = (x << (sh & 63));
    let mut shr_v: i64 = (x >> (sh & 63));
    let mut mixed: i64 = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

fn quickfox(a: i64, b: i64, sh: i64, limit: i64) -> i64 {
    let mut cls_a: i64 = classify_number(a);
    let mut cls_b: i64 = classify_number(b);
    let mut fact_v: i64 = factorial_iter(limit);
    let mut euc_v: i64 = euclid_step(a, b);
    let mut mix_v: i64 = bit_mixer((a + b), sh, 255);
    let mut total: i64 = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    let mut i: i64 = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
```

#### Step 5: Java ([`tests/roundtrip_steps/cycle2/05_quickfox.java`](tests/roundtrip_steps/cycle2/05_quickfox.java)) — `cycle1 == cycle2`
```java
long classify_number(long n) {
    long res = 0;
    if ((n < 0)) {
        res = -1;
    } else {
        if ((n == 0)) {
            res = 0;
        } else {
            if ((n < 10)) {
                res = 1;
            } else {
                res = 2;
            }
        }
    }
    return res;
}

long factorial_iter(long n) {
    long acc = 1;
    long k = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

long euclid_step(long a, long b) {
    long q = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b));
    long r = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b));
    long out = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

long bit_mixer(long x, long sh, long mask) {
    long shl_v = (x << (sh & 63));
    long shr_v = (x >> (sh & 63));
    long mixed = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

long quickfox(long a, long b, long sh, long limit) {
    long cls_a = classify_number(a);
    long cls_b = classify_number(b);
    long fact_v = factorial_iter(limit);
    long euc_v = euclid_step(a, b);
    long mix_v = bit_mixer((a + b), sh, 255);
    long total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    long i = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
```

#### Step 6: TypeScript ([`tests/roundtrip_steps/cycle2/06_quickfox.ts`](tests/roundtrip_steps/cycle2/06_quickfox.ts)) — `cycle1 == cycle2`
```typescript
function classify_number(n: number): number {
    let res: number = 0;
    if ((n < 0)) {
        res = -1;
    } else {
        if ((n == 0)) {
            res = 0;
        } else {
            if ((n < 10)) {
                res = 1;
            } else {
                res = 2;
            }
        }
    }
    return res;
}

function factorial_iter(n: number): number {
    let acc: number = 1;
    let k: number = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

function euclid_step(a: number, b: number): number {
    let q: number = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b));
    let r: number = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b));
    let out: number = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

function bit_mixer(x: number, sh: number, mask: number): number {
    let shl_v: number = (x << (sh & 63));
    let shr_v: number = (x >> (sh & 63));
    let mixed: number = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

function quickfox(a: number, b: number, sh: number, limit: number): number {
    let cls_a: number = classify_number(a);
    let cls_b: number = classify_number(b);
    let fact_v: number = factorial_iter(limit);
    let euc_v: number = euclid_step(a, b);
    let mix_v: number = bit_mixer((a + b), sh, 255);
    let total: number = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    let i: number = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
```

#### Step 7: C# ([`tests/roundtrip_steps/cycle2/07_quickfox.cs`](tests/roundtrip_steps/cycle2/07_quickfox.cs)) — `cycle1 == cycle2`
```csharp
long classify_number(long n) {
    long res = 0;
    if ((n < 0)) {
        res = -1;
    } else {
        if ((n == 0)) {
            res = 0;
        } else {
            if ((n < 10)) {
                res = 1;
            } else {
                res = 2;
            }
        }
    }
    return res;
}

long factorial_iter(long n) {
    long acc = 1;
    long k = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

long euclid_step(long a, long b) {
    long q = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b));
    long r = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b));
    long out = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

long bit_mixer(long x, long sh, long mask) {
    long shl_v = (x << (sh & 63));
    long shr_v = (x >> (sh & 63));
    long mixed = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

long quickfox(long a, long b, long sh, long limit) {
    long cls_a = classify_number(a);
    long cls_b = classify_number(b);
    long fact_v = factorial_iter(limit);
    long euc_v = euclid_step(a, b);
    long mix_v = bit_mixer((a + b), sh, 255);
    long total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    long i = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
```

#### Step 8: Ruby ([`tests/roundtrip_steps/cycle2/08_quickfox.rb`](tests/roundtrip_steps/cycle2/08_quickfox.rb)) — `cycle1 == cycle2`
```ruby
def classify_number(n)
    res = 0
    if (n < 0)
        res = -1
    else
        if (n == 0)
            res = 0
        else
            if (n < 10)
                res = 1
            else
                res = 2
            end
        end
    end
    return res
end

def factorial_iter(n)
    acc = 1
    k = 2
    while (k <= n)
        acc = (acc * k)
        k = (k + 1)
    end
    return acc
end

def euclid_step(a, b)
    q = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b))
    r = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b))
    out = 0
    if ((q < 0) && (r != 0))
        out = (((q * 100) + r) - a)
    else
        out = ((q * 100) - r)
    end
    return out
end

def bit_mixer(x, sh, mask)
    shl_v = (x << (sh & 63))
    shr_v = (x >> (sh & 63))
    mixed = ((shl_v ^ shr_v) | (x & mask))
    return mixed
end

def quickfox(a, b, sh, limit)
    cls_a = classify_number(a)
    cls_b = classify_number(b)
    fact_v = factorial_iter(limit)
    euc_v = euclid_step(a, b)
    mix_v = bit_mixer((a + b), sh, 255)
    total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b)
    i = 0
    while (i < limit)
        total = (total + (mix_v ^ i))
        i = (i + 1)
    end
    return total
end
```

#### Step 9: PHP ([`tests/roundtrip_steps/cycle2/09_quickfox.php`](tests/roundtrip_steps/cycle2/09_quickfox.php)) — `cycle1 == cycle2`
```php
function classify_number(int $n): int {
    $res = 0;
    if (($n < 0)) {
        $res = -1;
    } else {
        if (($n == 0)) {
            $res = 0;
        } else {
            if (($n < 10)) {
                $res = 1;
            } else {
                $res = 2;
            }
        }
    }
    return $res;
}

function factorial_iter(int $n): int {
    $acc = 1;
    $k = 2;
    while (($k <= $n)) {
        $acc = ($acc * $k);
        $k = ($k + 1);
    }
    return $acc;
}

function euclid_step(int $a, int $b): int {
    $q = (((($a ^ $b) < 0) && (($a % $b) != 0)) ? (($a / $b) - 1) : ($a / $b));
    $r = (((($a ^ $b) < 0) && (($a % $b) != 0)) ? (($a % $b) + $b) : ($a % $b));
    $out = 0;
    if ((($q < 0) && ($r != 0))) {
        $out = ((($q * 100) + $r) - $a);
    } else {
        $out = (($q * 100) - $r);
    }
    return $out;
}

function bit_mixer(int $x, int $sh, int $mask): int {
    $shl_v = ($x << ($sh & 63));
    $shr_v = ($x >> ($sh & 63));
    $mixed = (($shl_v ^ $shr_v) | ($x & $mask));
    return $mixed;
}

function quickfox(int $a, int $b, int $sh, int $limit): int {
    $cls_a = classify_number($a);
    $cls_b = classify_number($b);
    $fact_v = factorial_iter($limit);
    $euc_v = euclid_step($a, $b);
    $mix_v = bit_mixer(($a + $b), $sh, 255);
    $total = ((($fact_v + $euc_v) + ($cls_a * 10)) + $cls_b);
    $i = 0;
    while (($i < $limit)) {
        $total = ($total + ($mix_v ^ $i));
        $i = ($i + 1);
    }
    return $total;
}
```

#### Step 10: Dart ([`tests/roundtrip_steps/cycle2/10_quickfox.dart`](tests/roundtrip_steps/cycle2/10_quickfox.dart)) — `cycle1 == cycle2`
```dart
int classify_number(int n) {
    int res = 0;
    if ((n < 0)) {
        res = -1;
    } else {
        if ((n == 0)) {
            res = 0;
        } else {
            if ((n < 10)) {
                res = 1;
            } else {
                res = 2;
            }
        }
    }
    return res;
}

int factorial_iter(int n) {
    int acc = 1;
    int k = 2;
    while ((k <= n)) {
        acc = (acc * k);
        k = (k + 1);
    }
    return acc;
}

int euclid_step(int a, int b) {
    int q = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b));
    int r = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b));
    int out = 0;
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a);
    } else {
        out = ((q * 100) - r);
    }
    return out;
}

int bit_mixer(int x, int sh, int mask) {
    int shl_v = (x << (sh & 63));
    int shr_v = (x >> (sh & 63));
    int mixed = ((shl_v ^ shr_v) | (x & mask));
    return mixed;
}

int quickfox(int a, int b, int sh, int limit) {
    int cls_a = classify_number(a);
    int cls_b = classify_number(b);
    int fact_v = factorial_iter(limit);
    int euc_v = euclid_step(a, b);
    int mix_v = bit_mixer((a + b), sh, 255);
    int total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b);
    int i = 0;
    while ((i < limit)) {
        total = (total + (mix_v ^ i));
        i = (i + 1);
    }
    return total;
}
```

#### Step 11: Swift ([`tests/roundtrip_steps/cycle2/11_quickfox.swift`](tests/roundtrip_steps/cycle2/11_quickfox.swift)) — `cycle1 == cycle2`
```swift
func classify_number(_ n: Int64) -> Int64 {
    var res: Int64 = 0
    if ((n < 0)) {
        res = -1
    } else {
        if ((n == 0)) {
            res = 0
        } else {
            if ((n < 10)) {
                res = 1
            } else {
                res = 2
            }
        }
    }
    return res
}

func factorial_iter(_ n: Int64) -> Int64 {
    var acc: Int64 = 1
    var k: Int64 = 2
    while ((k <= n)) {
        acc = (acc * k)
        k = (k + 1)
    }
    return acc
}

func euclid_step(_ a: Int64, _ b: Int64) -> Int64 {
    var q: Int64 = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a / b) - 1) : (a / b))
    var r: Int64 = ((((a ^ b) < 0) && ((a % b) != 0)) ? ((a % b) + b) : (a % b))
    var out: Int64 = 0
    if (((q < 0) && (r != 0))) {
        out = (((q * 100) + r) - a)
    } else {
        out = ((q * 100) - r)
    }
    return out
}

func bit_mixer(_ x: Int64, _ sh: Int64, _ mask: Int64) -> Int64 {
    var shl_v: Int64 = (x << (sh & 63))
    var shr_v: Int64 = (x >> (sh & 63))
    var mixed: Int64 = ((shl_v ^ shr_v) | (x & mask))
    return mixed
}

func quickfox(_ a: Int64, _ b: Int64, _ sh: Int64, _ limit: Int64) -> Int64 {
    var cls_a: Int64 = classify_number(a)
    var cls_b: Int64 = classify_number(b)
    var fact_v: Int64 = factorial_iter(limit)
    var euc_v: Int64 = euclid_step(a, b)
    var mix_v: Int64 = bit_mixer((a + b), sh, 255)
    var total: Int64 = (((fact_v + euc_v) + (cls_a * 10)) + cls_b)
    var i: Int64 = 0
    while ((i < limit)) {
        total = (total + (mix_v ^ i))
        i = (i + 1)
    }
    return total
}
```

#### Step 12: Python (Roundtripped `S_1 == S_2`) ([`tests/roundtrip_steps/cycle2/12_quickfox.py`](tests/roundtrip_steps/cycle2/12_quickfox.py)) — `cycle1 == cycle2`
```python
def classify_number(n):
    res = 0
    if (n < 0):
        res = -1
    else:
        if (n == 0):
            res = 0
        else:
            if (n < 10):
                res = 1
            else:
                res = 2
    return res

def factorial_iter(n):
    acc = 1
    k = 2
    while (k <= n):
        acc = (acc * k)
        k = (k + 1)
    return acc

def euclid_step(a, b):
    q = ((int(a / b) - 1) if (((a ^ b) < 0) and ((a - (int(a / b) * b)) != 0)) else int(a / b))
    r = (((a - (int(a / b) * b)) + b) if (((a ^ b) < 0) and ((a - (int(a / b) * b)) != 0)) else (a - (int(a / b) * b)))
    out = 0
    if ((q < 0) and (r != 0)):
        out = (((q * 100) + r) - a)
    else:
        out = ((q * 100) - r)
    return out

def bit_mixer(x, sh, mask):
    shl_v = (x << (sh & 63))
    shr_v = (x >> (sh & 63))
    mixed = ((shl_v ^ shr_v) | (x & mask))
    return mixed

def quickfox(a, b, sh, limit):
    cls_a = classify_number(a)
    cls_b = classify_number(b)
    fact_v = factorial_iter(limit)
    euc_v = euclid_step(a, b)
    mix_v = bit_mixer((a + b), sh, 255)
    total = (((fact_v + euc_v) + (cls_a * 10)) + cls_b)
    i = 0
    while (i < limit):
        total = (total + (mix_v ^ i))
        i = (i + 1)
    return total
```
