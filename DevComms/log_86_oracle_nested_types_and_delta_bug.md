# log_86 — oracle reach: nested types, stdlib WRAP, and the oracle catching the oracle's own bug

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_85. Oracle-judged throughout.

## Headline: 5 → 68 passing methods this session (26 → 68 this turn)

| stage | passing methods | engines green |
|---|---:|---:|
| log_84 (oracle stood up) | 5 | 1/10 |
| log_85 (closure/enums/defaults/@Test) | 22 | 1/10 |
| + ext-fn dispatch + stdlib WRAP (6ab9457) | 26 | 1/10 |
| + nested types | 42 | 1/10 |
| + math/collection WRAP | 44 | 1/10 |
| **+ assertEquals delta fix** | **68** | 1/10 |

AutoregulationEngine 5→**31**/59 · CalibrationEngine →**11**/15 · RestartEngine →**13**/17 ·
CardioRecovery →6/12 · NotificationTriggers 5/5 · Warmup 2/12. **0 FAILs** — every method
that runs MATCHES the JVM-verified value. Reds are unimplemented gaps (ERR), not divergence.

## What landed

**Nested types (the big lifter, +16).** `ConfidenceTier` lives inside
`object AutoregulationEngine`; the index only saw top-level decls, so it was unresolved
(23 hits). Now:
- the oracle's symbol index descends into class/object bodies and maps nested TYPE names
  → their file (members are NOT indexed — that pulled in the whole corpus, a bug caught
  and reverted mid-change);
- the transpiler emits a module-level alias per nested type (`ConfidenceTier =
  AutoregulationEngine.ConfidenceTier`), flushed after all decls, so bare cross-file refs
  resolve. Aliases compose for deep nesting (each level aliases its own children).

**Stdlib WRAP grew:** `roundToInt/roundToLong` (Kotlin half-up via the shim),
`minOf/maxOf` (shim), and call-site collection rewrites `filter/toList/toSet/asSequence
(identity)/take/first/firstOrNull` alongside the earlier `isEmpty/coerceIn/.size/…`.

**The oracle caught the ORACLE's own bug (+24).** 24 methods FAILed with `got 1e-09`/
`1e-06`/`0.0001`. Not a transpiler bug — `applyDeadband` transpiled perfectly. It was the
`kotlin_rt.assertEquals` shim: JUnit's `assertEquals(expected, actual, delta)` float
overload has a **tolerance delta** as the third arg, but the shim treated the last arg as
`actual` and compared the real value against the `1e-9` *delta*. Fixed to handle all
JUnit overloads (optional leading String message — only with 3+ args so `assertEquals("a",
"b")` still compares two strings; optional trailing numeric delta → tolerance compare).
That one fix flipped 24 false-FAILs to PASS. The negative-control discipline (log_84) is
exactly why this surfaced as a sharp, uniform signal instead of silent wrong-greens.

## Next
- Collection-method long tail — `sortedBy`, `associateBy`, `mapNotNull`, `sumOf`,
  `groupBy`, `zipWithNext`, `takeLast`, `maxOfOrNull`. Piecemeal call-site WRAP works but
  the tail is long; a **KtList runtime type** (list subclass carrying the Kotlin methods,
  emitted by `listOf`/collection literals) would cover them uniformly. Decide next turn.
- The four 0-reach engines (Substitution/Periodization/PathDefinition/SampleProgramData)
  still fail at exec — separate per-engine causes to dig into.
