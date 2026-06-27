# log_73 — py2many Kotlin backend patched; atlas compiles clean (Python→Kotlin path)

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_72 (decided: "measure
py2many's Python→Kotlin first; if decent, it's the shortest path to Table_Py_Kt").
This log: cracked open the backend, fixed the bugs, and **compiled the output**.

## Result (one line)

After 7 localized fixes to py2many 0.8's `--kotlin` backend, **all 8 construct-atlas
functions compile clean under `kotlinc` (jar builds, exit 0)** — single hop, zero
runtime scaffolding. py2many is a viable Python→Kotlin path for the routine bulk.

## What was broken vs. fixed

log_72 measured 6/8 "clean" by eye. Cracking it open + **actually compiling** found
the real count was lower — eyeballing is not a compiler. Fixes (all in
`pykt/{transpiler,clike,plugins}.py`; see `tools/py2many_kotlin/pykt.patch`):

1. `Optional[int]` → `Nothing<Int>`  ⟶  `Int?`  (arg-annotation path, clike.py)
2. same in subscript-annotation position (transpiler.py visit_Subscript)
3. `val self.x: Int` (self. leaked into the field name) ⟶ `var x: Int`
4. `self.x = x` in `__init__` emitted `var x: Int = x` (a shadowing local, never
   wrote the field) ⟶ plain `this.x = x`
5. self reads emitted bare `x` (ambiguous vs the ctor param) ⟶ `this.x`
6. `fun __init__(...)` ⟶ Kotlin `constructor(...)`
7. `math.sqrt(intExpr)` left unmapped ⟶ `kotlin.math.sqrt((...).toDouble())` + import

**The one the compiler caught that the eye missed:** Kotlin params are `val`.
`while_loop`'s `k -= 1` reassigns the parameter → `error: 'val' cannot be reassigned`.
Fix: shadow any reassigned param with a local `var k = k`. (py2many's `mutable_vars`
flags only vars assigned **>1** time — it misses a param reassigned exactly once — so
the patch scans assignment targets directly.) This is exactly the anti-slop oracle
discipline: transpile → compile → the compiler is the truth, not the read-through.

## Final Kotlin (representative)

```kotlin
fun ternary(a: Int): Int { var y: Int = if (a > 0) 1 else -1 ; return y }
fun while_loop(k: Int): Int { var k = k ; while (k > 0) { k -= 1 } ; return k }
fun null_check(z: Int?): String { if (z == null) { return "z" } ; return "v" }
class Pt {
  var x: Int
  var y: Int
  constructor(x: Int, y: Int) { this.x = x ; this.y = y }
  fun dist(): Double { return sqrt(((this.x*this.x) + (this.y*this.y)).toDouble()) }
}
```

## Reproducible artifacts (in repo)

`tools/py2many_kotlin/`:
- `pykt.patch`   — unified diff vs the pristine `py2many-0.8` wheel; round-trips
  (apply to pristine ⇒ reproduces the working tree byte-for-byte).
- `atlas.py`     — the 8-construct atlas.
- `run_atlas.sh` — regenerate + **compile with kotlinc**; exit 0 ⇔ jar builds. Verified PASS.
- `README.md`    — apply instructions + the fix table + scope caveats.

Toolchain: kotlinc bundled in Android Studio snap
(`/snap/android-studio/232/plugins/Kotlin/kotlinc/bin/kotlinc`), JDK 25.

## What this settles, and what it doesn't

- **Settles:** Python→Kotlin via py2many collapses the Haxe→Java→J2K pipeline for
  routine control-flow/arithmetic/collections/nullable/simple-OOP. One hop, clean,
  and now *compile-verified* — not just visually idiomatic.
- **Does NOT settle (the long tail, unchanged from log_72):**
  - **stdlib breadth** — only `sqrt`/`floor`/`min`/`max` mapped; the rest is
    one-by-one as the corpus demands. This is the bulk of remaining harvest work.
  - **hard Kotlin idioms** — Compose, coroutines, extension functions: wrap-layer /
    manual, verified by the WFL test oracle.
  - **direction** — this is Python→Kotlin. WFL is **Kotlin→Python**. py2many proves
    the *construct-equivalence table* is mechanically harvestable and the emitted
    Kotlin is real; using it to drive the K→Py transpiler (or to validate it
    round-trip) is the next design question, not yet decided.

## Next

Two open forks (unchanged owner decision):
1. Scale the atlas toward the actual WFL construct inventory (drive the stdlib
   long-tail mappings from real usage), re-run compile-gate each addition.
2. Decide how this Py↔Kt evidence feeds the K→Py transpiler proper (PseudoKotlin
   scaffold from log_71: visitor dispatch + 116-node coverage test + map/wrap/fail).
