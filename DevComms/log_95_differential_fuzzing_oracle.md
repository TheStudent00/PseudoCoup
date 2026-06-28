# log_95 — differential-fuzzing oracle: 5000 random cases, both sides equivalent

Date: 2026-06-27
Type: new tool (tools/pseudokotlin/fuzz.py). Bucket 2 of the "what remains" plan.

## What it is

The runtime oracle (oracle.py) proves equivalence on the engines' HAND-WRITTEN JUnit cases.
This pushes past that ceiling: **generate random inputs in each target's domain, run the SAME
cases on BOTH sides — the transpiled Python engine and the JVM Kotlin engine — and diff the
outputs.** A divergence is a real behavioural bug the hand-written tests never reached. This
is the rung above "passes its tests": evidence of equivalence on *arbitrary* inputs.

## How it runs both sides on identical cases

- Cases are drawn from a small deterministic LCG (not Python's RNG) so the case stream is
  identical every run, every machine — no hash-seed / platform dependence.
- **Python side**: load the transpiled engine via the oracle's own machinery (closure +
  multipass exec into the kotlin_rt-seeded namespace), call `engine.method(*args)` per case.
- **JVM side**: emit a throwaway JUnit harness that calls the engine on the embedded cases and
  writes `ti<TAB>ci<TAB>ok|err<TAB>value` to a temp file; run it through the EXISTING Gradle
  setup (classpath/deps just work), then read + compare. The harness is always cleaned up
  (`finally`), so the corpus stays pristine.
- Compare: Doubles within 1e-9 relative (genuine algorithm divergences dwarf float-print
  noise; both decimal strings round-trip to the same float64 when the IEEE bits match), Ints
  and Booleans exact, and "both threw" counts as agreement.

Two JVM-harness gotchas handled: a single method with thousands of calls blows the JVM's
64 KB per-method bytecode limit (→ chunk into ~300-call methods); and Double literals must
carry a decimal point or Kotlin reads them as Int.

## Result

| | |
|---|---|
| targets | **10** pure primitive→scalar functions across **3 engines** |
| cases | **500 each → 5000 total** |
| divergences | **0 — ALL EQUIVALENT** |

Targets: AutoregulationEngine {computeE1rm, suggestRawWeight, predictReps, roundToIncrement,
applyReadinessProgressionHold, isReadinessGood}; CardioRecoveryEngine {durationFactor,
recencyDecay}; PeriodizationEngine {volumeWaveFraction, setTargetForWeek}.

## The negative control (why the green means something)

A verifier never seen to fail proves nothing — the session's standing discipline. Injected a
+5.0 error into one Python result and confirmed the fuzzer flagged **exactly that case and no
other**. So "ALL EQUIVALENT across 5000 cases" is a real signal, not a no-op.

## Net
Bucket 2 done. Equivalence evidence now goes beyond hand-written tests: 10 pure functions
across 3 engines are equivalent on 5000 random inputs, with a passing negative control. The
tool is a flat `TARGETS` list — extending coverage is just adding rows (the natural next
growth is functions that take data-class inputs, which need a shared constructor on both
sides). Bucket 3 (Compose UI) remains intentionally out of scope.
