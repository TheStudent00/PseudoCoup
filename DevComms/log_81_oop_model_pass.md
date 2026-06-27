# log_81 — transpiler iteration 2: the OOP-model pass (object / companion / init)

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_80 (iterate loop).

## What landed (Group C — the Kotlin-model ≠ Python-model decisions)

- **`object Foo {…}` → singleton:** emit the class, then `Foo = Foo()` — rebinds the
  name to a sole instance, so `Foo.x`/`Foo.f()` resolve and no extra instances are
  constructible. Faithful to Kotlin's single-instance semantics.
- **`companion object {…}` → static members on the enclosing class:** properties →
  class-level attrs; functions → `@staticmethod`. Companion-member references resolve to
  `ClassName.member` (new `_static_members`/`_static_class` resolution in the identifier
  handler, parallel to instance `self.x`).
- **`init { … }` → folded into `__init__`** (after the ctor-param assigns and property
  inits), in instance scope.

```
object Config { val max = 5; fun limit(x:Int) = if (x>max) max else x }
  -> class Config:
         def __init__(self): self.max = 5
         def limit(self, x): return (self.max if x > self.max else x)
     Config = Config()

class Counter(val start:Int){ var n=0; init{n=start}; companion object{ val D=10; fun make()=Counter(D) } }
  -> class Counter:
         def __init__(self, start): self.start=start; self.n=0; self.n=start
         D = 10
         @staticmethod
         def make(): return Counter(Counter.D)
```

## Two correctness wins the discipline forced (py_compile alone would miss both)

1. **No more silent class-member drops.** The class renderer used to collect only
   property/function members and silently ignore the rest — so `companion_object` and
   `anonymous_initializer` were being **dropped** (files "compiled" with the code gone).
   Now: companion/init are handled; the remaining OOP members (`secondary_constructor`,
   `object_literal`) **fail loudly** (`_OOP_DEFER`) — never dropped.
2. **The companion descent bug.** Companion members live in a *nested* `class_body`
   (`companion_object → class_body → members`); the first cut read the wrong level and
   emitted an EMPTY companion — a silent drop that **py_compile passed** (empty companion
   is valid Python) but lost behavior. Exactly the failure mode the owner's state-trace
   oracle is designed to catch and a compile-check cannot. Fixed by descending.

This is why the headline number moved 154→152 after the fix: the 154 was inflated by
the silent drop; 152 is companions actually transpiled.

## Measurement (WFL corpus, excl. build/)

| step | ALL clean | NON-UI domain clean |
|---|---:|---:|
| after lambda hoist (log_80) | 146 | 113 |
| **after OOP-model pass** | **152** | **121** |

+6 / +8, plus the silent drops eliminated. Domain-layer remaining blockers:
`getter` 9, `property_delegate` 6, `unary_expression` 4, `object_literal` 1.

## Next
Iteration 3: `getter` (`val x get() = …`) → `@property`. Then `property_delegate`
(`by lazy`). After a clutch of domain files transpile clean, stand up the P4 oracle on
the Python side (transpile an engine + its test, run, compare) — the runtime end of the
verification ladder (log_80): tests → state-trace → symbolic.
