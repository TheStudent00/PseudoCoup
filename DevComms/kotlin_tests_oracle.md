# Kotlin unit-test suite under KtToPy — oracle runner

## What the runner does
`tools/pseudokotlin/run_kotlin_tests.py` runs the app's own JUnit unit-test suite through the
transpiler and reports pass/fail truthfully. For each test class it:

1. transpiles the same-named subject engine (if one exists) + the test `.kt` to Python, reusing
   `oracle.transpile` / `oracle.closure` (the same machinery the equivalence oracle uses) —
   subject is transpiled first so its field/type registrations are in place before the test refs;
2. execs the dependency closure + subject + test into a namespace seeded with `registry.namespace()`,
   which carries the JUnit shim (`runtime/kotlin_rt.py`: `@Test`, `@Before`, and
   `assertEquals/assertTrue/assertFalse/assertNull/assertNotNull/assertNotEquals/assertThrows`
   mapped to real Python `assert`s — general, already existed, not per-test);
3. discovers `@Test` methods, runs each in isolation (fresh instance + `@Before` setup), and prints a
   per-test `PASS`/`FAIL`/`ERROR` table plus a `RESULT: N/M pass` summary line.

Difference from `oracle.py --all`: this targets exactly the 11 task-named classes (skips
`ExampleUnitTest`), and instance construction happens *inside* the per-test `try`, so a missing
framework class would surface as an honest `ERROR` row rather than crashing the whole run
(`oracle.py --all` currently aborts on an unrelated corpus test that references `TimeZone`, because it
constructs the instance outside the try — not in scope to change here).

## Final result

```
RESULT: 160/160 pass
```

| Class | Pass/Total |
|---|---|
| AutoregulationEngineTest | 59/59 |
| CalibrationEngineTest | 15/15 |
| CardioRecoveryEngineTest | 12/12 |
| NotificationTriggersTest | 5/5 |
| PeriodizationEngineTest | 17/17 |
| ReadinessProgressionGateTest | 9/9 |
| RestartEngineTest | 17/17 |
| SubstitutionEngineTest | 5/5 |
| WarmupEngineTest | 12/12 |
| PathDefinitionTest | 5/5 |
| SampleProgramDataTest | 4/4 |

Method counts match the Kotlin `@Test` counts exactly (59+15+12+5+17+9+17+5+12+5+4 = 160): every
`@Test` is discovered and run, none skipped.

## Transpiler / runtime fixes made
None. The transpiler, the dependency-closure resolver, and the pre-existing JUnit shim in
`runtime/kotlin_rt.py` already cover everything these 11 classes exercise. The only new file is the
runner. Verified the shim is not silently passing: `assertEquals(3,4)` and `assertTrue(False)` both
raise `AssertionError` (so `FAIL` rows are reachable), and the discovered method count equals the
source `@Test` count (so nothing is being skipped to inflate the total).

## Named limitations
- Out of the 11 targeted classes: none. Full 160/160.
- Beyond this set, `oracle.py --all` also discovers other `*Test.kt` in the corpus; at least one
  (a NotificationGenerator-style test) references `java.util.TimeZone`, which the runtime does not
  shim — that is genuinely out of scope for this task (not among the 11 named files) and is left as a
  known gap rather than faked.

## Fence / hack audit
- Only file touched under the fence: `tools/pseudokotlin/run_kotlin_tests.py` (new) + this report.
  No edits to `transpiler.py`, `datalayer.py`, `nodes/`, or `runtime/`.
- No per-name hacks: the only test-specific identifiers in the runner are the suite manifest lists
  (`ENGINE_TESTS`/`MODEL_TESTS`) naming which classes to run — no test-specific branching in transpiler
  or runtime code.
