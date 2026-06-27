# log_87 — KtList runtime + ctor defaults + trailing-lambda merge: a second engine goes EQUIVALENT

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_86. Oracle-judged.

## Headline: CalibrationEngine 15/15 — EQUIVALENT both sides (2nd fully-green engine)

`oracle.py CalibrationEngine --jvm` → both the transpiled Python and the JVM pass all 15
JUnit methods. A complete, non-trivial domain engine (calibration seeding, cold-start
multipliers, related-lift ratios) transpiled Kotlin→Python with proven runtime
equivalence — not compile-clean, *behaviorally identical*.

| | passing methods | engines green |
|---|---:|---:|
| log_86 | 68 | 1/10 |
| **this turn** | **81** | **2/10** |

AutoregulationEngine 33→**38**/59 · CalibrationEngine →**15/15** · Restart 14/17 ·
CardioRecovery 6/12 · NotificationTriggers 5/5 · Warmup 3/12. Still **0 FAILs**.

## What landed

**KtList / KtMap runtime types (kotlin_rt).** The collection-method tail (sortedBy,
associateBy, mapNotNull, sumOf, groupBy, fold, zipWithNext, chunked, windowed, partition,
…) is long; piecemeal call-site WRAP doesn't scale. Instead `listOf`/`emptyList`/
`mutableListOf`/`mapOf` now return `KtList`(a `list` subclass)/`KtMap`(a `dict` subclass)
carrying the Kotlin methods. List-returning methods return KtList so chains stay typed;
map-returning methods (associateBy/groupBy) return KtMap. Collection methods were removed
from the call-site WRAP (which now keeps only string/number ops: isEmpty/coerceIn/
roundToInt/.size). Map.Entry is modelled by `KtEntry` for `mapValues { it.value }`.

**Constructor-parameter defaults.** I handled function defaults in log_85 but not
primary-constructor defaults — `class WarmupSet(val isEmptyBar: Boolean = false)` threw
`__init__ missing 'isEmptyBar'`. Now the default (inside the `class_parameter`, after `=`)
is emitted into `__init__`, with the same self/param-reference sentinel guard.

**Trailing-lambda merge (the big lifter, +~10).** `require(x > 0) { "msg" }` parses as
`(require(x > 0))(lambda)` — an outer call whose function is the inner `require(x>0)` call,
plus a trailing lambda. The transpiler was emitting exactly that (`bool` object then
called → `'bool' is not callable`, 15 hits). Kotlin semantics: `f(args) { λ }` =
`f(args, λ)`. v_call now detects this nesting and merges the lambda into the inner call's
arguments. Fixes require/check/fold/any `f(a){λ}` form across all engines.

## Next
- AutoregulationEngine 38/59 — the largest engine; the remaining gaps (set `+` union,
  enum-to-number comparison, a few `NoneType not callable`) are the next bucket.
- Four 0-reach engines (Substitution/Periodization/PathDefinition/SampleProgramData) still
  fail at exec — per-engine causes (e.g. `VolumeLandmark`, `PathDefinition` self-reference).
