# log_126 — 2 transpiler bugs fixed + the real runnable-domain measurement

Date: 2026-06-28
Type: feature + measurement. Delivers the payoff of the user's "Foundation: start with DI" choice.

## 2 transpiler bugs fixed (the "control-flow as an expression" class)

Both are Kotlin idioms that put control flow where Python needs a value:

1. **`val x = expr ?: continue`** (elvis with a continue/break RHS). The elvis guard already existed
   for `return`/`throw`; `continue`/`break` parse as *identifiers* and slipped past `is_value`. Fix:
   detect them in the elvis handler → hoist a guard (`_elvN = expr; if _elvN is None: continue`).
   This pattern hit **30+ sites in AutoregulationRepository** alone.
2. **`val id = s.ifEmpty { continue }`** (control flow *inside a lambda* → became a `def`, so an
   illegal `continue`). Fix: a new `_empty_guard` for `ifEmpty`/`ifBlank` with a control-flow body →
   hoist (`_ifeN = s; if not _ifeN: continue; … = _ifeN`).

Both verified; **oracle stays ALL GREEN 11/11**. All **20/20 repositories now syntax-clean** (was 18/20).

## The real runnable-domain measurement (load → construct → CALL)

With a domain runtime namespace (kotlin_rt + `UUID`/`System`/`Flow` shims + permissive entity
stand-ins) and stub DAOs:

```
LOAD (parse+exec):     19/20
CONSTRUCT (DI wired):  17/20
RAN >=1 real method:   14/20
methods EXECUTED:      127/232  (55%)
```

vs `literal_transpiler` (WFL_MixingCenter): ~1/20 even had a usable constructor.

## What the remaining gaps are (NOT transpiler bugs)

- `CardioRecoveryRepository`: a module-level numeric calc `*` a permissive stub — my dumb fixture, not
  a transpile error.
- `CelebrationRepository`: `KtList` has no `flatMapLatest` (a Flow operator) — a kotlin_rt/shim
  COVERAGE gap, not a transpile error.

So the transpiler's part is essentially done for the repository layer (20/20 parse, DI correct, member
refs resolved); the 14→20 remainder is **runtime-shim completeness** + better fixtures.

## Caveat (honest)

This measures **runnability** (the code executes without crashing), NOT **runtime-equivalence** (correct
results) — that is the oracle's separate ladder (11 engines proven). Still, it moves Track B's real
floor from "parse-clean scaffolding" (log_124) to "the domain logic runs."

## Net

Track B's foundation, measured honestly via the canonical transpiler: **20/20 repos parse, 14/20 run
real methods, 127/232 methods execute.** The parse-clean → runnable jump for the repository layer is
largely done; what's left is runtime-shim coverage (Flow operators), not transpiler work.
