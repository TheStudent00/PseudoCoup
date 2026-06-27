# log_90 — runtime-oracle session milestone: 5 → 113 passing, 3 engines EQUIVALENT both-sides

Date: 2026-06-27
Type: milestone summary. Caps the arc logs 84–89.

## Where the runtime oracle stands

| metric | value |
|---|---|
| passing methods | **113 / 128 (88%)** |
| engines fully green | **3 / 10** |
| both-sides EQUIVALENT (Python + JVM) | NotificationTriggers, CalibrationEngine, SubstitutionEngine |
| behavioral divergences (FAIL) | **0** |

Per engine: Autoregulation **57**/59 · Calibration 15/15 · Substitution 5/5 ·
NotificationTriggers 5/5 · CardioRecovery 11/12 · Restart 14/17 · Warmup 5/12 ·
PathDefinition 1/5 · Periodization 0/1 · SampleProgramData 0/1.

The result that matters: **0 FAILs across 113 methods** — wherever a transpiled engine
runs, it behaves identically to the Kotlin, and three complete engines are verified
green on BOTH the transpiled Python and the JVM.

## What the oracle drove (this session)

Starting from "the oracle is stood up, 5 methods pass" (log 84), every fix below was
chosen because the oracle localized it, and verified because the oracle re-ran:
closure loading · enum entries · default params (fn + ctor + required-after-default) ·
@Test detection · extension-function dispatch (incl. member extensions) · the
KtList/KtMap/KtSet runtime (the whole collection tail + `+`/`+=`/slice/`map[k]` semantics)
· scope functions + non-local-return guard · comparators · trailing-lambda merge · local-
variable shadowing · the `_name_of` value-identifier bug · `continue`/`break` ·
companion self-reference deferral · numeric conversions · ranges.

Two bugs the oracle caught that compile-clean never would: the `assertEquals(…, delta)`
shim mishandling (24 false-FAILs, log 86) and the non-local-return divergence (log 88) —
both surfaced as sharp uniform signals because of the negative-control discipline.

## Remaining (hard / niche, diminishing per-method returns)
- **Method overloading** (Autoreg 2): two `seedWeightFromRelated`; Python keeps the last
  def. Needs generated type-dispatch.
- **Extension receiver-member access** (Warmup `loadKg`, 7): `fun WarmupSet.triple() =
  Triple(loadKg, …)` — bare access to the receiver's fields needs receiver-type member
  resolution.
- **Imported companion const used bare** (Restart `MS_PER_DAY`, 3): cross-file import.
- **Self-reference ordering** (Periodization `VolumeLandmark`, SampleProgramData): nested
  type / large-closure exec ordering.
- A `float`-as-int (CardioRecovery, 1).

Each is its own feature; the 88% is the natural plateau before them.
