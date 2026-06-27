# log_74 — table-from-source (the spine) + atlas growth via compile gate

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_73. Two things this turn:
(1) answered "does py2many's source make the table easier?" — yes, built the
extractor; (2) grew the atlas toward WFL's real construct inventory behind a
granular compile gate, fixing the mechanical gaps it surfaced.

## 1. The table is partly WRITTEN DOWN in py2many source (don't black-box it)

py2many encodes the **declarative** half of the Python↔target mapping as explicit
dicts in every backend: a primitive `*_TYPE_MAP`, a `*_CONTAINER_TYPE_MAP`, and
the stdlib-fn dispatch maps (`SMALL_DISPATCH_MAP`/`DISPATCH_MAP`). **10 of 11
backends** carry all three, all keyed by the same **Python pivot** — so reading
them yields a multi-language table (Python × N targets) for free, no snippets.

`tools/py2many_kotlin/extract_table.py` → `equivalence_table.md` does exactly
that (7 backends import cleanly: Kotlin/Rust/Go/Nim/Julia/Zig/Mojo). Sample row,
straight from source:

| Python | Kotlin | Rust | Go | Nim | Julia | Zig | Mojo |
|---|---|---|---|---|---|---|---|
| `int` | Int | i32 | int | int | Int64 | i32 | Int |
| `float` | Double | f64 | float64 | float64 | Float64 | f64 | Float64 |

**But source ≠ truth.** The extractor reads py2many's *intent*; the compile gate
reads *reality*. Live proof in our own table: the Kotlin `Optional` row reads
`Nothing` (the pristine-0.8 source value) — which is **wrong**; the gate proved
it must be `T?`. So the architecture is: **source for breadth (declarative rows,
all languages, free) + compile gate for correctness (and for the structural
constructs source can't tabulate).**

### What source CANNOT give you
The structural constructs — `if`/`for`/`while`/ternary/class-shape/operators/
assignment — are imperative emit-templates in `visit_*` methods, not dict rows.
Those only come out by running + compiling (the atlas). This is the dividing line.

## 2. Atlas growth behind a granular compile gate

`constructs/` = one construct per file; `gate.py` transpiles each with the
patched backend, compiles each `.kt` in isolation with kotlinc, and reports
per-construct PASS/FAIL **with the exact error**. This is how the long tail gets
mapped against actual usage: add a construct → any gap shows up as a located
kotlinc error to fix in `pykt.patch` or route to the wrap-layer.

First batch of 12 → **5/12**, then fixed the mechanical gaps → **8/12**.

### Fixed this round (mechanical, compile-verified)
- **duplicate field** — `self.x` (from `__init__`) and `x` (from a later
  reassignment) both reduced to `x` after the self-strip → `var x` declared
  twice. Dedup field names. (A bug my own log_73 self-strip introduced; the gate
  caught it via `method_call`.)
- **generic param placement** — `fun f<T>(…)` → `fun <T> f(…)` (Kotlin order).
- **`Dict` container type** — `Dict<K,V>` (not a type) → `HashMap<K,V>`.
- **`abs`** → `kotlin.math.abs`.
- **str methods** — `.upper()/.lower()/.strip()/.startswith()/.endswith()` →
  `.uppercase()/.lowercase()/.trim()/.startsWith()/.endsWith()` (name-based).

### Backlog (deeper — logged, not rushed)
- `list_comp` — needs `visit_ListComp` lowering `[x*2 for x in xs]` → `.map { }`.
- `tuple_return` — `(q,r)` and `Tuple[int,int]` → `Pair(...)` / `Pair<…>`
  (visit_Tuple is used in several positions; needs care).
- `optional_chain` — `len(s)` on a `String` emits `.size`; needs **type-aware**
  dispatch (`String` → `.length`). The general "len/append/index are container-
  type-dependent" problem.
- `dict_ops` — py2many's multi-return inference yields a nested `Union[Union[…]]`
  return type → invalid signature. Upstream inference bug, not a backend template.

These four are the genuine "structural / type-aware" tier — the same tier as the
WFL hard idioms. They get worked deliberately, each verified by the gate.

## Artifacts (all in `tools/py2many_kotlin/`, committed)
- `pykt.patch` — now touches `transpiler/clike/plugins/inference.py`; round-trips
  vs the pristine 0.8 wheel (apply ⇒ reproduces working tree byte-for-byte).
- `extract_table.py` + `equivalence_table.md` — the source-harvested spine.
- `constructs/` + `gate.py` — granular compile gate (8/12).
- `atlas.py` + `run_atlas.sh` — the original 8-construct smoke (8/8, one jar).

## Net
Counting both sets, **12 of 16 distinct constructs now compile** to idiomatic
Kotlin, single hop. The path is real and measured at every step by kotlinc. The
4 open are structural/type-aware (the expected hard tier), now itemized with
exact errors. Next: work the backlog (likely `list_comp` and `tuple→Pair` first —
both common in WFL), gate each; and grow `constructs/` from the actual
WFL_MixingCenter Python as the source of "real usage."
