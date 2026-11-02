---
id: hq.projects.pseudocoup.hub.support.universal_12_language_autopoly_and_hub_construction
type: support
belongs_to: CORE_0_0_0_2_hub.md
status: active
date: 2026-11-01
author: the owner & Gemini
---

# SUPPORT: 12-Language AutoPoly Status & Constructing the Hub

<details open>
<summary><b>1. 12-Language AutoPoly Coverage & Canonical Unit Deduplication</b></summary>

Across all 12 lowered languages (`665,719 / 665,847` variants = `99.98%`), `Research/autopoly/universal_12_lang_hub.py` indexes every lowered `Unit` into the three AutoPoly execution tiers (`SUPPORT_BRAINSTORM_hub.md` §3, `CORE_0_0_0_2_0_autopoly.md`):

| Language / Group | Lowered / Listed Variants | Distinct `LoOp`s | Canonical `Unit` Modes | Tier 1: Exact `HiOp` ($\Delta=\emptyset$) | Tier 2: Piecewise `HiOp` ($D_{\text{fast}} \sqcup D_{\text{edge}}$) | Tier 3: `LoOp` Primitive Backstop |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **GNU C** | `57,370 / 57,480` | `406` | `438` | `29,205` | `9,194` | `18,971` |
| **7 Clang Dialects** (`C++`, `OMP`, `ObjC`, `MS`, `CUDA`, `HLSL`, `OpenCL`) | `574 / 592` | `81` | `144` | `368` | `44` | `162` |
| **Go** (`cmd/compile`) | `1,654 / 1,654` | `51` | `540` | `876` | `778` | `0` |
| **Rust** (`rustc`) | `1,168 / 1,168` | `115` | `355` | `313` | `855` | `0` |
| **Python** (`CPython`) | `599,954 / 599,954` | `52` | `34` | `339,104` | `130,425` | `130,425` |
| **Java** (`javac` + HotSpot) | `4,999 / 4,999` | `71` | `63` | `3,671` | `1,318` | `10` |
| **12-Language Total** | **`665,719 / 665,847` (`99.98%`)** | **`410` union** | **`1,545` union** | **`373,537` (`56.1%`)** | **`142,614` (`21.4%`)** | **`149,568` (`22.5%`)** |

- **77.5% (`516,151` variants) run via native or piecewise `HiOp`-to-`HiOp` synthesis (Tiers 1 & 2)** without decomposing into individual `LoOp`s.
- **22.5% (`149,568` variants) run via the Guaranteed `LoOp`-to-`HiOpPrimitive` Backstop (Tier 3)**, composing each `LoOp` from the target language's `13` `HiOpPrimitives` plus whole-lowered `compiler-rt` (`58` routines) and atomic fences (`SUPPORT_riscv64_ordering_per_target_language.md`).

</details>

---

<details open>
<summary><b>2. The 13 Universal <code>HiOpPrimitives</code> (Guaranteed Backstop Basis)</b></summary>

Every integer and control-flow `LoOp` in the Sail RISC-V model (`map_LoOp_to_lean`) decomposes into `13` primitive bitvector operations, each mapped to a proven `HiOpPrimitive` in every target language:

```python
HIOP_PRIMITIVES = {
    "BV_ADD":  {"c": "a + b",                   "go": "a + b",                    "rust": "a.wrapping_add(b)",                 "python": "(a + b) & MASK",          "java": "a + b"},
    "BV_SUB":  {"c": "a - b",                   "go": "a - b",                    "rust": "a.wrapping_sub(b)",                 "python": "(a - b) & MASK",          "java": "a - b"},
    "BV_MUL":  {"c": "a * b",                   "go": "a * b",                    "rust": "a.wrapping_mul(b)",                 "python": "(a * b) & MASK",          "java": "a * b"},
    "BV_AND":  {"c": "a & b",                   "go": "a & b",                    "rust": "a & b",                             "python": "a & b",                   "java": "a & b"},
    "BV_OR":   {"c": "a | b",                   "go": "a | b",                    "rust": "a | b",                             "python": "a | b",                   "java": "a | b"},
    "BV_XOR":  {"c": "a ^ b",                   "go": "a ^ b",                    "rust": "a ^ b",                             "python": "a ^ b",                   "java": "a ^ b"},
    "BV_NOT":  {"c": "~a",                      "go": "^a",                       "rust": "!a",                                "python": "~a & MASK",               "java": "~a"},
    "BV_SHL":  {"c": "a << (b & 63)",           "go": "a << (b & 63)",            "rust": "a.wrapping_shl(b as u32)",          "python": "(a << (b & 63)) & MASK",  "java": "a << b"},
    "BV_LSHR": {"c": "(uint64_t)a >> (b & 63)", "go": "uint64(a) >> (b & 63)",    "rust": "(a as u64).wrapping_shr(b as u32)", "python": "(a & MASK) >> (b & 63)",  "java": "a >>> b"},
    "BV_ASHR": {"c": "a >> (b & 63)",           "go": "a >> (b & 63)",            "rust": "a.wrapping_shr(b as u32)",          "python": "ashr64(a, b & 63)",       "java": "a >> b"},
    "BV_ULT":  {"c": "(uint64_t)a < (uint64_t)b","go": "uint64(a) < uint64(b)",   "rust": "(a as u64) < (b as u64)",           "python": "(a & MASK) < (b & MASK)", "java": "Long.compareUnsigned(a, b) < 0"},
    "BV_SLT":  {"c": "a < b",                   "go": "a < b",                    "rust": "a < b",                             "python": "s64(a) < s64(b)",         "java": "a < b"},
    "BV_ITE":  {"c": "c ? a : b",               "go": "ite(c, a, b)",             "rust": "if c { a } else { b }",             "python": "a if c else b",           "java": "c ? a : b"},
}
```

</details>

---

<details open>
<summary><b>3. Constructing the Hub: <code>UR-Node</code> Dispatch & Qualified Operator Syntax</b></summary>

Per `CORE_0_0_0_2_hub.md` and `SUPPORT_BRAINSTORM_hub.md` (§1 rows 1–11), the Hub is a modified Python runtime that holds AutoPoly and executes qualified cross-language operators (`y = (m C.* x) C.+ b`) directly through `UR-Node`s (`hiop`, `units`, `meaning`):

```python
class URNode:
    # Universal Rich Node (`CORE_0_0_0_1_ledgerer.md`): hiop, units, meaning
    def __init__(self, lang: str, op: str, units_rv64: list[str], tier: str, domain_ok: str, range_expr: str):
        self.hiop = f"{lang}.{op}"                                      # e.g. "Go./", "Rust.%", "Java.>>>"
        self.units = {"riscv64": units_rv64}                            # sliced machine Unit
        self.meaning = {"tier": tier, "D_ok": domain_ok, "R_val": range_expr}

# Hub verification outputs (`Research/autopoly/universal_12_lang_hub_summary.json`):
#   "(m C.* x) C.+ b"         (m=7, x=6, b=3)      -> 45                    (Tier 1: Exact 1-to-1 HiOp)
#   "(a Go./ b) at MIN/-1"    (a=INT64_MIN, b=-1)  -> -9223372036854775808  (Tier 2: Piecewise non-trapping wrap)
#   "(a Rust.% b) at MIN/-1"  (a=INT64_MIN, b=-1)  -> "PANIC:SignedOverflow"(Tier 2: Piecewise overflow trap)
#   "(a Python.// b) at -7/2" (a=-7, b=2)          -> -4                    (Tier 2: Piecewise floor-div guard)
#   "(a Java.>>> b) at -1>>>60"(a=-1, b=60)        -> 15                    (Tier 1: 1-to-1 RISC-V `srl`)
```

</details>

---

<details open>
<summary><b>4. Production Hub Package (`Projects/PseudoCoup/hub` & <code>Projects/PseudoCoup/ledgerer</code>)</b></summary>

Constructed in `Projects/PseudoCoup/` following the ontology in `Planning/CORE_0_0_0_pseudocoup.md
- [`Projects/PseudoCoup/ledgerer/universal_rich_node.py`](file://Projects/PseudoCoup/ledgerer/universal_rich_node.py) — `UniversalRichNode` (`hiop`, `units`, `meaning`, `canonical_lo_ops()`, `mode_key()`).
- [`Projects/PseudoCoup/hub/autopoly/equivalence_prover.py`](file://Projects/PseudoCoup/hub/autopoly/equivalence_prover.py) — Z3 BitVec64 `EquivalenceProver` proving exact mode equivalence ($\Delta = \emptyset$) and piecewise interior equivalence ($D = D_{\text{fast}} \sqcup D_{\text{edge}}$).
- [`Projects/PseudoCoup/hub/autopoly/polyfill.py`](file://Projects/PseudoCoup/hub/autopoly/polyfill.py) — 3-Tier `AutoPoly` synthesizer and the `13` universal `HiOpPrimitives`.
- [`Projects/PseudoCoup/hub/__init__.py`](file://Projects/PseudoCoup/hub/__init__.py) — `Hub` runtime:
  - `load_lowered_vocabularies()`: ingests `9,830` lowered variants across `C`, `C++`, `Go`, `Rust`, `Python`, `Java`, and the Clang dialects into `764` canonical `Unit` modes (`67` shared cross-language modes).
  - `eval_qualified_expr(expr, env)` & `transpile_hub_expr(expr, target_lang)`: evaluates and transpiles nested cross-language expressions across all 6 target languages:

```python
# Cross-language Hub transpilation (`Hub.transpile_hub_expr("(a Java.>>> s) Go.+ (x Go.<< k)", target_lang)`):
{
  "c":      "(((uint64_t)a >> (s & 63)) + (((uint64_t)k < (uint64_t)64) ? (x << (k & 63)) : 0))",
  "cpp":    "(((uint64_t)a >> (s & 63)) + (((uint64_t)k < (uint64_t)64) ? (x << (k & 63)) : 0))",
  "go":     "((uint64(a) >> (s & 63)) + ite((uint64(k) < uint64(64)), (x << (k & 63)), 0))",
  "rust":   "(a as u64).wrapping_shr(s as u32) as i64.wrapping_add((if ((k as u64) < (64 as u64)) { x.wrapping_shl(k as u32) } else { 0 }))",
  "python": "((((a & 0xFFFFFFFFFFFFFFFF) >> (s & 63)) + (((x << (k & 63)) & 0xFFFFFFFFFFFFFFFF) if ((k & 0xFFFFFFFFFFFFFFFF) < (64 & 0xFFFFFFFFFFFFFFFF)) else 0)) & 0xFFFFFFFFFFFFFFFF)",
  "java":   "((a >>> s) + ((Long.compareUnsigned(k, 64) < 0) ? (x << k) : 0))"
}
```

</details>

---

<details open>
<summary><b>5. Multi-Body Control Flow, Complex Holders &amp; 3-Level Verification Suite (<code>unit_vm.py</code>, <code>control_flow.py</code>, <code>test_hub_complete.py</code>)</b></summary>

Extended `Projects/PseudoCoup/hub/` so all `9,814` lowered `Unit`s (including multi-body control flow and complex holders) are 100% operational in the Hub:
- [`Projects/PseudoCoup/hub/unit_vm.py`](file://Projects/PseudoCoup/hub/unit_vm.py) — [`RiscvUnitVM`](file://Projects/PseudoCoup/hub/unit_vm.py#L43-L216): steps any sliced RISC-V `Unit` (`words`, `unit`, `parts`), resolves internal `.L0` branch relocations, invokes `part_*` callbacks at `R_RISCV_CALL_PLT` sites, and propagates [`BreakSignal`](file://Projects/PseudoCoup/hub/unit_vm.py#L14-L15) / [`ContinueSignal`](file://Projects/PseudoCoup/hub/unit_vm.py#L18-L19) / [`ReturnSignal`](file://Projects/PseudoCoup/hub/unit_vm.py#L22-L26).
- [`Projects/PseudoCoup/hub/control_flow.py`](file://Projects/PseudoCoup/hub/control_flow.py) — [`ComplexHolder`](file://Projects/PseudoCoup/hub/control_flow.py#L18-L41) (`struct` & `array` compositions of machine words) and [`MultiBodyEngine`](file://Projects/PseudoCoup/hub/control_flow.py#L44-L162) (`if/else`, `while`, `for`, `switch`, `?:`, short-circuit `&&` / `||`, dependent `break` / `continue`, and multi-body transpilation to `c`, `cpp`, `go`, `rust`, `python`, `java`).
- [`Projects/PseudoCoup/hub/test_hub_complete.py`](file://Projects/PseudoCoup/hub/test_hub_complete.py) — 3-level verification suite:

```json
{
  "level1_exhaustive_unit_vm": {
    "total_units_executed": 9814,
    "multi_body_units_executed": 34,
    "riscv_conditional_unit_true":  {"steps": 13, "called_parts": ["part_1324_a", "part_1324_b"], "a0": 100},
    "riscv_conditional_unit_false": {"steps": 12, "called_parts": ["part_1324_a", "part_1324_c"], "a0": 200}
  },
  "level2_polyglot_multi_body_program": {
    "iterations_run": 5,
    "final_acc": 33,
    "final_idx": 5,
    "short_circuit_side_effects": 0,
    "transpiled_while_rust": "while (idx < 5 != 0) { acc = acc.wrapping_mul(2).wrapping_add(step) }",
    "transpiled_ternary_python": "(val // 2 if (val < 0 != 0) else int(val / 2))"
  },
  "level3_z3_control_flow_theorems": {
    "if_else_kept_test_decomposition": "unsat",
    "short_circuit_land_equivalence": "unsat"
  }
}
```

</details>

---

<details open>
<summary><b>6. Remaining 6 Original Languages Extracted, Lowered, Proven in Z3 &amp; Wired into the Hub (<code>TypeScript</code>, <code>C#</code>, <code>Ruby</code>, <code>PHP</code>, <code>Dart</code>, <code>Swift</code>)</b></summary>

Extracted, lowered to RISC-V `Unit`s (`clang-21 --target=riscv64-unknown-linux-gnu -march=rv64gc -O0 -g` + `llvm-objdump-21`), proven in Z3, and registered in the Hub via [`lower_remaining_six_langs.py`](file://Research/lower_HiOp/lower_remaining_six_langs.py) and [`prove_remaining_six_langs.py`](file://Research/autopoly/prove_remaining_six_langs.py):

| Original Language | Compiler / VM Baseline | Consolidated Vocabulary (`lang_models/<lang>/`) | Lowered / Listed Variants | RISC-V `Unit` Words | Distinct `LoOp`s | Z3 Theorems (`UNSAT`) | Hub `RiscvUnitVM` Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **TypeScript / JS** | `tsc 6.0.3` + `node v24.22.1` (V8) | `consolidated_typescript_vocabulary.jsonl.gz` | `432 / 432` (**100%**) | `3,008` | `55` | `3 / 3` | **100% Operational** |
| **C# (`csharp`)** | Roslyn + `.NET 8.0.407` (CoreCLR) | `consolidated_csharp_vocabulary.jsonl.gz` | `440 / 440` (**100%**) | `3,542` | `73` | `4 / 4` | **100% Operational** |
| **Ruby (`ruby`)** | `ruby 3.3.8` (YARV + `vm_insnhelper.c`) | `consolidated_ruby_vocabulary.jsonl.gz` | `354 / 354` (**100%**) | `2,960` | `39` | `3 / 3` | **100% Operational** |
| **PHP (`php`)** | `php 8.5.4` (Zend Engine 4) | `consolidated_php_vocabulary.jsonl.gz` | `315 / 315` (**100%**) | `2,421` | `49` | `2 / 2` | **100% Operational** |
| **Dart (`dart`)** | `dart 3.13.7` (Dart Kernel + VM AOT) | `consolidated_dart_vocabulary.jsonl.gz` | `345 / 345` (**100%**) | `2,954` | `56` | `3 / 3` | **100% Operational** |
| **Swift (`swift`)** | `swift 6.0.3` (SIL + `swift-llvm`) | `consolidated_swift_vocabulary.jsonl.gz` | `464 / 464` (**100%**) | `3,266` | `73` | `3 / 3` | **100% Operational** |
| **Subtotal (New 6)** | **6 Remaining Original Languages** | **6 Consolidated Models** | **`2,350 / 2,350` (`100%`)** | **`18,151`** | **`89` union** | **`18 / 18` (`UNSAT`)** | **100% Operational** |
| **Grand Total (All 12 Original + 6 Clang Dialects)** | **18 Language / Dialect Models** | **All Models Persisted** | **`668,069 / 668,197` (`99.98%`)** | **`7,427,338`** | **`410` union** | **`75 / 75` (`UNSAT`)** | **`12,164 / 12,164` Units Executed in Hub VM** |

```python
# Verified in Projects/PseudoCoup/hub/test_hub_complete.py:
{
  "TypeScript.>>> (-1 >>> 28)": 15,   # ToUint32 logical shift (srlw)
  "C#.>>> (-1 >>> 60)":         15,   # C# 11 unsigned right shift (srl)
  "Ruby.<=> (10 <=> 20)":       -1,   # 3-way spaceship comparison
  "PHP.<=> (20 <=> 10)":         1,   # Zend ZEND_SPACESHIP
  "Dart.% (-7 % 3 Euclidean)":   2,   # Non-negative Euclidean modulo
  "Swift.&+ and Swift.&*":      45    # Wrapping overflow operators `(7 Swift.&* 6) Swift.&+ 3`
}
```

</details>


## 6. Two-Cycle Roundtrip Stabilization (`Ledgerer` + `Hub`)

```
Cycle 1 (Canonicalization):  S_0 (lang_x) -> Hub -> T_1 (lang_y) -> Hub -> S_1 (lang_x)   [S_0 != S_1]
Cycle 2 (Fixed-Point):       S_1 (lang_x) -> Hub -> T_2 (lang_y) -> Hub -> S_2 (lang_x)   [T_1 == T_2, S_1 == S_2]
```

| Roundtrip Suite (`Projects/PseudoCoup/ledgerer/test_roundtrip_two_cycles.py`) | Cycle 1 Reshapes (`S_0 != S_1`) | Cycle 2 Target Fixed-Point (`T_1 == T_2`) | Cycle 2 Source Fixed-Point (`S_1 == S_2`) | 5-Stage Semantic Equivalence (`eval(S_0)==...==eval(S_2)`) |
| :--- | :---: | :---: | :---: | :---: |
| **`Go <-> C`** (`a << b`, `shifted / c`, `if/else`) | `True` | **`True` (100% byte-identical)** | **`True` (100% byte-identical)** | `PASS` (`b=70`, `INT64_MIN/-1`) |
| **`Python <-> Rust`** (`a // b`, `a % b`, `if`) | `True` | **`True` (100% byte-identical)** | **`True` (100% byte-identical)** | `PASS` (`-17 // 5`, `17 % -5`) |
| **`TypeScript <-> Java`** (`while`, `^`, `<<`) | `True` | **`True` (100% byte-identical)** | **`True` (100% byte-identical)** | `PASS` (`step=2`, `step=68`) |


## 7. Canonical `quickfox` 12-Language 2-Cycle Roundtrip & `HolderBridge` Tool Composition

- **12-Language `quickfox` 2-Cycle Suite** ([`test_quickfox_all_12_langs.py`](file://Projects/PseudoCoup/ledgerer/test_quickfox_all_12_langs.py) $\to$ [`quickfox_12_langs_results.json`](file://Projects/PseudoCoup/ledgerer/quickfox_12_langs_results.json)):
  - Every Original Language (`c`, `cpp`, `go`, `rust`, `python`, `java`, `typescript`, `csharp`, `ruby`, `php`, `dart`, `swift`) passes 2-cycle roundtripping (`T_1 == T_2`, `S_1 == S_2`, outputs `[375, 3841, 678, 313]`).
  - Full **12-Language Sequential Daisy-Chain** (`Python -> C -> C++ -> Go -> Rust -> Python -> Java -> TypeScript -> C# -> Ruby -> PHP -> Dart -> Swift -> Python` across 2 cycles) achieves **`Cycle1 == Cycle2` (100% byte-identical)**.
- **Cross-Language `HolderBridge` Tool Pipeline** ([`holder_bridge.py`](file://Projects/PseudoCoup/hub/holder_bridge.py)):
  - Composes `py_grid_cell` (`Python`, `i64` floor-div/mod) $\to$ `go_pack_u32` (`Go`, saturating shift $\to$ `u32`) $\to$ `HolderBridge("u32", "i32")` (`rule3_reinterpretation_sext_zext`) $\to$ `c_mix_i32` (`C`, signed `i32` mixer).
