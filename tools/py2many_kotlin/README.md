# py2many Kotlin backend — patch + atlas (Python → Kotlin path)

Measures whether **py2many's `--kotlin` backend** is a viable single-hop path for
Python → Kotlin (the `Table_Py_Kt` we want), vs. the 3-hop Haxe→Java→J2K path.
Verdict so far: **yes for the routine bulk** — once 7 localized beta-backend bugs
are fixed, all 8 construct-atlas functions compile clean under `kotlinc`, in a
single hop, with zero runtime scaffolding (no `HxObject`/`__hx_invoke`).

## Files

- `atlas.py`   — 8 typed-Python constructs (arithmetic, if/else, ternary, range
  loop, while, list ops, nullable, a class with `__init__`+method).
- `pykt.patch` — unified diff against **py2many 0.8** (`py2many-0.8-py3-none-any.whl`)
  fixing the 7 defects below. Touches only `pykt/{transpiler,clike,plugins}.py`.
- `run_atlas.sh` — regenerate `atlas.kt` and **compile it with kotlinc** (the
  anti-slop oracle). Exit 0 ⇔ the jar builds.

## Apply

```bash
# from the repo root:
PATCH="$PWD/tools/py2many_kotlin/pykt.patch"
PKG=$(python3 -c 'import py2many,os;print(os.path.dirname(py2many.__file__))')
# patch paths are a/py2many/... so strip 1 component, applied from site-packages:
( cd "$(dirname "$PKG")" && patch -p1 < "$PATCH" )
bash tools/py2many_kotlin/run_atlas.sh        # -> PASS
```

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

## Scope / what this does NOT cover

The atlas is the *routine bulk*. Still out of scope (the long tail): the rest of
the Python/Kotlin stdlib beyond `sqrt`/`floor`/`min`/`max` (mapped one-by-one as
needed), and the hard Kotlin idioms (Compose, coroutines, extension functions) —
those are the wrap-layer / manual work, verified against the WFL test oracle.
