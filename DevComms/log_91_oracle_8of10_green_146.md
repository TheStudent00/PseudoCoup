# log_91 — runtime oracle: 8/10 engines green, 146/151 methods, 0 FAILs

Date: 2026-06-27
Type: milestone summary. Caps the long reach push (logs 84–90).

## State

| metric | value |
|---|---|
| passing methods | **146 / 151 (97%)** |
| engines fully green | **8 / 10** |
| both-sides EQUIVALENT (Python + JVM) | NotificationTriggers, Calibration, Substitution, CardioRecovery, Restart (spot-checked) |
| behavioral divergences (FAIL) | **0** |

Green: NotificationTriggers 5/5 · Calibration 15/15 · Substitution 5/5 · CardioRecovery
12/12 · Restart 17/17 · PathDefinition 5/5 · Periodization 17/17 · Warmup 12/12.
Remaining: AutoregulationEngine 57/59 · SampleProgramData 1/4.

**0 FAILs across 146 methods** — wherever a transpiled engine runs, it behaves identically
to the Kotlin, and eight complete engines pass their full JUnit suites on the transpiled
Python (five cross-checked green on the JVM too).

## Constructs the transpiler now handles (all oracle-driven this session)

Runtime types: KtList/KtMap/KtSet/Pair/Triple/Comparator/Regex/Math + the Kotlin
collection tail (sortedBy/associateBy/groupBy/fold/zipWithNext/chunked/windowed/partition/
sortedWith/find/…), set union/`+=`, `map[k]`→None, list concat/slice staying typed.

Language: dependency-closure loading · enum entries + values()/entries()/valueOf · default
params (fn + ctor + required-after-default + self/param-ref sentinel) · @Test/@Before ·
extension functions (incl. member extensions + receiver-field resolution) · scope functions
(let/also/takeIf/takeUnless) with non-local-return guard · trailing-lambda merge ·
destructuring lambda params + destructuring `val (a,b)=` · local-variable shadowing ·
nested types + module aliases · companion const aliases · deferred object instantiation ·
closure-captured mutation (nonlocal, lambdas + nested fns) · `continue`/`break` ·
increment-as-value hoist · range membership (`x in a..b`) · `.first/.second/.last` props ·
generic-call misparse (`f<T>(x)`) · prefix-op precedence (`!w.x`) · Char arithmetic ·
string concat coercion · numeric conversions · String methods · the `_name_of` value-id bug.

## Remaining (hard tail, low per-method yield)
- **AutoregulationEngine 2** — Kotlin method overloading (two `seedWeightFromRelated`);
  Python keeps the last def. Needs generated type-dispatch.
- **SampleProgramData 3** — a single pathologically-deep 320-line nested builder; ~15
  distinct edge cases fixed already, each revealing the next (`int not iterable` is current).
  Every general fix it surfaced is committed; the residue is this one file's whack-a-mole.

## The methodology held
Two bugs the oracle caught that compile-clean never could — the `assertEquals(…, delta)`
shim (24 false-FAILs) and the non-local-return divergence (110 vs 120) — both surfaced as
sharp uniform signals because of the negative-control discipline. The `0 FAILs` is the
headline: this is verified behavioral equivalence, not "it parses."
