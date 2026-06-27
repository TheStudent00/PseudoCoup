# log_84 — the runtime equivalence oracle stands up (rung 2 of the ladder)

Date: 2026-06-27
Type: implementation + first behavioral-equivalence proof. Continuation of log_83
(compile-fault sweep). This is the rung above the compile gate on the verification
ladder from log_80: tests → **runtime/state-trace** → symbolic.

## Why compile-clean was never the finish line

log_83 drove the domain layer to 96% compile-clean, but compile-clean only proves the
Python *parses*. The companion-drop bug (log_81) is the cautionary tale: it `py_compile`d
fine and lost behavior. Extension functions and `buildString` compile today but won't
*run* without their shims. The oracle is what turns "transpiles" into "behaves the same."

## What landed — `tools/pseudokotlin/oracle.py` + `runtime/kotlin_rt.py`

For an engine + its JUnit test, the oracle:
1. transpiles BOTH engine and test Kotlin → Python;
2. execs them into one namespace seeded with the `kotlin_rt` shim (JUnit asserts +
   Kotlin stdlib helpers the transpiled code calls by bare name);
3. runs each test method — a **JVM-verified assertion now executing against the
   TRANSPILED engine**. Python passes every assertion the JVM passes ⟺ behaviorally
   equivalent on those inputs;
4. with `--jvm`, runs the Gradle test for the same class too, so "both sides" is literal.

The JUnit assertions are the oracle: they encode behavior the 161 green JVM tests already
verified. Re-running them against the transpiled engine is the cross-language differential.

## First proof — NotificationTriggers: EQUIVALENT (both green)

```
=== NotificationTriggers  (python: 5/5 methods) ===
  [ok] absence_nudge_fires_at_or_past_threshold   ... (all 5)
  JVM: green  ->  EQUIVALENT (both green)
```

A pure-predicate `object` (singleton) of boolean rules — the transpiled Python passes all
5 JUnit methods, and the JVM passes the same 5. First concrete equivalence proof.

**Negative control (the oracle has teeth):** inject an off-by-one into the transpiled
engine (`gapDays >= MIN` → `>`) and exactly one method flips —
`absence_nudge_fires_at_or_past_threshold` FAILs, the other four stay green. Divergence is
*detected* and *localized* to the offending predicate. An always-green oracle proves
nothing; this one fails when it should.

## The sweep — `oracle.py --all` — and the worklist it surfaced

| engines fully green | 1/10 (NotificationTriggers 5/5) |

The other 9 are red, and the errors bucket cleanly into the next worklist (this is the
oracle doing its real job — generating the next iterate-loop targets):

1. **Dependency-closure loading (dominant).** Most failures are `NameError` for *other
   domain types* the engine/test reference — `SetInput`, `ConfidenceTier`, `RepRange`,
   `ProgressionType`, `DeloadSessionSummary`, … The harness loads only the single engine
   file; it must transpile + load the engine's **dependency closure** (the entities/enums).
2. **Kotlin default parameters → Python defaults.** `suggestFromE1rm() missing 3 required
   positional arguments` — the transpiler drops Kotlin default-arg values, so the test's
   shorter calls fail. A real transpiler gap.
3. **Kotlin stdlib method/extension mapping.** `'int' has no attribute 'coerceAtMost'`,
   `'list' has no attribute 'isEmpty'`, `require(...)` — `coerceAtMost/AtLeast` → min/max,
   `xs.isEmpty()` → `len(xs)==0`, `require` → shim. WRAP layer (transpiler) + `kotlin_rt`.

## Status / next
The oracle is **operational and proven** (both-sides EQUIVALENT on 1 engine, teeth
verified, sweeps all 10). Reach is gated on the three buckets above, in priority order:
dependency-closure loading first (unlocks the most engines at once), then default params,
then the stdlib-method WRAP set. Each is an iterate-loop turn with the oracle — not the
compile gate — as the pass/fail.
