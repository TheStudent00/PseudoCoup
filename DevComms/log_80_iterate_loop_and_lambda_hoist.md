# log_80 — the iterate loop: oracle confirmed + transpiler iteration 1 (lambda hoisting)

Date: 2026-06-27
Type: methodology + implementation. Adopts the owner's plan and runs the first turn of it.

## The plan (owner's), adopted

Iterate between (a) **improving the transpiler** and (b) **adjusting WFL toward the
transpiler — but provably equivalent to un-modified WFL**. Two disciplines pin it down:

- **Which side moves:** the transpiler is the default mover. WFL only moves for a
  construct that is a genuine model-mismatch or not worth the transpiler complexity AND
  has a clean equivalent form. We don't mangle idiomatic Kotlin (lambdas, getters,
  objects) — those are the transpiler's job.
- **"Provably equivalent" = the WFL test oracle.** Refactor → `./gradlew
  :app:testDebugUnitTest` green → behavior-preserving.

## Oracle confirmed operational (the linchpin)

WFL's unit tests are the **engine tests** (Warmup/Autoregulation/Calibration/…), pure
JVM logic — exactly the layer we transpile. Verified runnable HERE:
`./gradlew :app:testDebugUnitTest` → **BUILD SUCCESSFUL in 71s, 161 testcases pass**
(12 test classes). So WFL-side refactors are gateable for real, not in theory.

## Transpiler iteration 1: multi-statement lambda → hoisted `def`

Python lambdas are single-expression; Kotlin lambdas are multi-statement. Built a
**hoist buffer**: a multi-statement `lambda_literal` emits a named `def _lamN(...)` into
`self._hoist`, returns the name, and every suite renderer (`render_statements`) flushes
hoisted defs immediately BEFORE the statement that used them. Nesting works (inner def
hoisted before outer). Example:

```
xs.map { v -> val d = v*2; d + 1 }
  ->
def _lam1(v):
    d = v * 2
    return d + 1
... xs.map(_lam1)
```

Also: trailing-lambda already wired into `v_call`; empty-lambda-body guard
(`{}` -> `lambda: None`) fixed a ValueError on 3 files. 10/10 gate green.

## Measurement (WFL corpus, excluding gradle-generated build/)

| | files | transpiled | py_compile-clean |
|---|---:|---:|---:|
| before (P1) | 278 | 144 | 130 |
| **after lambda hoist** | 278 | **190** | **146** |

+46 transpiled, +16 compile-clean. The smaller compile-clean gain is expected: many
lambda-blocked files have a *second* blocker, so fixing lambda moves them to the next
one (objects/getters/delegates) rather than all the way to clean.

Remaining top blockers (ranked):
- ALL: `property_delegate` 40 (mostly UI `by remember` → P3 wrap), `object_declaration`
  26, `getter` 17.
- **NON-UI domain (the oracle-relevant layer): `object_declaration` 24, `getter` 8,
  `property_delegate` 4, `unary_expression` 3.**

## Next iteration
Domain layer's dominant blocker is now `object_declaration`/`companion_object` — the
Group C OOP-model. Lean transpiler-side with the faithful singleton mapping
(`class Foo: …` + `Foo = Foo()` rebind preserves Kotlin's single-instance semantics).
Then `getter` → `@property`. Re-measure each; once a domain file transpiles clean,
verify its engine with the test oracle.
