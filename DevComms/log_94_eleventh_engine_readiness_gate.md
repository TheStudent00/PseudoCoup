# log_94 — 11th engine wired up: ReadinessProgressionGate (9/9), 160/160 methods

Date: 2026-06-27
Type: oracle-harness change + a latent-fragility finding. Bucket 1 of the "what remains" plan.

## 11/11 engines green · 160/160 methods · 0 FAILs · ReadinessProgressionGate JVM-EQUIVALENT

`ReadinessProgressionGateTest` (9 @Test methods) was being silently skipped by the oracle:
it has no same-named `ReadinessProgressionGate.kt` — its subject is methods ON
`AutoregulationEngine` (`isReadinessTrendLow`, `applyReadinessProgressionHold`, the nested
`ReadinessDay`). The oracle resolved a test only to a same-named main file, so this real
suite never ran.

Two harness changes (oracle.py — NOT the transpiler):
1. **`oracle(name)`**: a same-named main engine is now optional. When absent, the subject
   arrives via the test's own dependency closure (the test references `AutoregulationEngine`,
   which the closure pulls in as a dep). The engine seed is just `[]` in that case.
2. **`all_engines()`**: admits a `*Test.kt` with no same-named engine **iff** it references a
   MAIN-defined symbol — which includes ReadinessProgressionGate (→ AutoregulationEngine) and
   still excludes Android's boilerplate `ExampleUnitTest` (references nothing in the corpus).

Result: ReadinessProgressionGate **9/9**, JVM cross-checked **EQUIVALENT (both green)**. The
sweep is now **11/11 engines, 160/160 methods, 0 FAILs**.

## A latent transpiler fragility this surfaced (worth a real fix later)

First cut of the change transpiled the test BEFORE the engine — and WarmupEngine regressed
12/12 → 5/12 with `NameError: name 'loadKg' is not defined`. Root cause: **`transpile()` has
order-dependent global side effects.** It populates type/field registries (`_TYPE_FIELDS`,
used for extension-receiver field resolution) as it goes, so a reference like
`WarmupEngine.loadKg` only resolves to a field access if WarmupEngine.kt was transpiled
*first*; transpiled after the referrer, `loadKg` is emitted as a bare free name → NameError.

Fixed for now by pinning the oracle's order (engine before test, matching the prior implicit
contract). But the deeper issue stands: **transpilation is not order-independent.** The sound
fix is a two-pass design — index every type/field across the whole closure first, then
transpile — so output never depends on visit order. Filed here as the next transpiler-
hardening candidate; the oracle currently relies on a specific order to stay correct.

## Net
Bucket 1 done. Behavioural-equivalence coverage: 10 → **11 test-backed classes**, all green,
all 0 FAILs, the new one JVM-verified. Next (bucket 2): the differential-fuzzing oracle —
random inputs run both sides and compared — to push past "has a hand-written test" toward
"equivalent on arbitrary inputs."
