# py2many Kotlin backend — patch + atlas (Python → Kotlin path)

Measures whether **py2many's `--kotlin` backend** is a viable single-hop path for
Python → Kotlin (the `Table_Py_Kt` we want), vs. the 3-hop Haxe→Java→J2K path.
Verdict so far: **yes for the routine bulk** — once 7 localized beta-backend bugs
are fixed, all 8 construct-atlas functions compile clean under `kotlinc`, in a
single hop, with zero runtime scaffolding (no `HxObject`/`__hx_invoke`).

## Files

- `atlas.py`   — 8 typed-Python constructs (arithmetic, if/else, ternary, range
  loop, while, list ops, nullable, a class with `__init__`+method). All compile.
- `constructs/` — one construct per file; the growing atlas toward WFL's real
  inventory. `gate.py` compiles each in isolation and reports per-construct
  PASS/FAIL with the exact kotlinc error (the long-tail to-do list).
- `extract_table.py` → `equivalence_table.md` — harvest the **declarative** part
  of the table (primitive types, containers, stdlib-fn coverage) straight from
  py2many's source dicts, for all 10 backends at once (Python pivot). Source for
  breadth; the compile gate is truth (the table even shows a source row the gate
  proved wrong: Kotlin `Optional` → `Nothing` should be `T?`).
- `pykt.patch` — unified diff against **py2many 0.8** (`py2many-0.8-py3-none-any.whl`)
  fixing the defects below. Touches `pykt/{transpiler,clike,plugins,inference}.py`.
- `run_atlas.sh` — regenerate `atlas.kt` and **compile it with kotlinc** (the
  anti-slop oracle). Exit 0 ⇔ the jar builds.
- `gate.py` — granular gate over `constructs/`; exit 0 ⇔ every construct compiles.

## Apply

```bash
# from the repo root:
DIR="$PWD/tools/py2many_kotlin"
PKG=$(python3 -c 'import py2many,os;print(os.path.dirname(py2many.__file__))')
# patch paths are a/py2many/... so strip 1 component, applied from site-packages:
( cd "$(dirname "$PKG")" \
    && patch -p1 < "$DIR/pykt.patch" \
    && patch -p1 < "$DIR/base_inference.patch" )
bash tools/py2many_kotlin/run_atlas.sh        # original atlas -> PASS (8/8)
python3 tools/py2many_kotlin/gate.py          # constructs/    -> 12/12 PASS
```

Two patches: **`pykt.patch`** (the Kotlin backend, `pykt/{transpiler,clike,plugins,
inference}.py`) and **`base_inference.patch`** (one fix in the *shared*
`py2many/inference.py` — see below; affects all backends, verified non-regressing).

Pristine baseline for the diff: `pip download py2many==0.8 --no-deps` (wheel).
The patch round-trips: applied to the pristine wheel it reproduces the working
tree byte-for-byte.

## The 7 fixes (all in the Kotlin backend)

| # | symptom (pristine 0.8) | fix | file |
|---|---|---|---|
| 1 | `z: Optional[int]` → `Nothing<Int>` | arg-annotation `Optional[T]` → `T?` | clike.py |
| 2 | same in subscript-annotation position | `Optional[T]` → `T?` | transpiler.py |
| 3 | `val self.x: Int` (self. leaked into field name) | strip `self.` → `var x: Int` | transpiler.py |
| 4 | `self.x = x` in `__init__` → `var x: Int = x` (shadow, no field write) | attribute-target AnnAssign → plain `this.x = x` | transpiler.py |
| 5 | self reads → bare `x` (ambiguous in ctor) | self-arg attribute → `this.x` | transpiler.py |
| 6 | `fun __init__(...)` (not a constructor) | `__init__` → Kotlin `constructor(...)` | transpiler.py |
| 7 | `math.sqrt(intExpr)` (unmapped + Int arg) | `kotlin.math.sqrt((...).toDouble())` + import | plugins.py |

Plus one defect **the compiler caught that eyeballing didn't**: Kotlin params are
`val`, so `while_loop`'s `k -= 1` (reassigning a param) failed to compile. Fix:
shadow any reassigned parameter with a local `var k = k` at the top of the body.
(py2many's `mutable_vars` flags only vars assigned **>1** time, missing a param
reassigned exactly once — so the patch detects assignment targets directly.)

Atlas-growth round 2 (from `constructs/`, all compile-gated) added:

| symptom | fix | file |
|---|---|---|
| `class { var x; var x }` (field declared twice — `self.x` + reassignment collide) | dedup field names | transpiler.py |
| `fun f<T>(…)` (Kotlin wants type params **before** the name) | `fun <T> f(…)` | transpiler.py |
| `Dict<K,V>` (not a Kotlin type) | `HashMap<K,V>` | inference.py |
| `abs(x)` unresolved | `kotlin.math.abs` | plugins.py |
| `s.upper()` unresolved | str-method map → `s.uppercase()` (+ lower/strip/startswith/endswith) | transpiler.py |

Atlas-growth round 3 — the structural/type-aware tier, all now compile-gated:

| symptom | fix | file |
|---|---|---|
| list comprehension hit the "unsupported" path | `visit_ListComp` → `iter.filter{}.map{}.toTypedArray()` | transpiler.py |
| `(q,r)` had no Kotlin form | 2-tuple → `Pair(...)`, 3-tuple → `Triple(...)` (+ drop the old double-wrap) | transpiler.py |
| `Tuple[int,int]` return type → `RT` | → `Pair<Int,Int>` / `Triple<…>` | clike.py |
| `len(s)` type-blind → `.size` on a `String` | type-aware: `String` → `.length`, else `.size` | transpiler.py |
| **`Union[Union[…]]` return type** | **shared base fix**: never clobber a *source-declared* return annotation (only widen inferred ones) | inference.py |

### Construct gate — current standing (`python3 gate.py`)

**12/12 PASS.** Combined with the original 8-construct atlas, **20/20 distinct
constructs compile** to idiomatic Kotlin, single hop.

## Scope / what this does NOT cover

The atlas is the *routine bulk*. Still out of scope (the long tail): the rest of
the Python/Kotlin stdlib beyond `sqrt`/`floor`/`min`/`max` (mapped one-by-one as
needed), and the hard Kotlin idioms (Compose, coroutines, extension functions) —
those are the wrap-layer / manual work, verified against the WFL test oracle.
