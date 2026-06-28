# log_93 — 10/10 engines green: the 10th via meet-in-the-middle

Date: 2026-06-27
Type: implementation + measurement. Closes the engine sweep started in log_84.

## 10/10 engines green · 151/151 methods · 0 FAILs · SampleProgramData JVM-verified EQUIVALENT

SampleProgramData — the lone holdout (1/4, the "type-inference wall" of log_91/92) — is now
**4/4 and EQUIVALENT both sides**. The close used the methodology the user asked about:
**getting WFL to meet the transpiler in the middle**, applied only where the Kotlin carries
information the transpiler genuinely can't recover, and *proven* behaviour-preserving by
running the edited Kotlin's own JUnit suite green on the JVM.

Before this, no WFL-side convergence had been done — every prior gain was transpiler-only.
This is the first deliberate meet-in-the-middle pass, and it's the right tool exactly here:
both walls were cases where Kotlin's static types disambiguate something the transpiler sees
no syntactic signal for.

### What met in the middle (WFL_MixingCenter/…/SampleProgramData.kt — behaviour-identical Kotlin)

1. **`plusAssign` element-vs-collection** (the log_92 wall):
   `groups += mutableListOf(a, partner)` — a `List<List<Int>>` appending ONE inner list —
   was extending (flattening) under the runtime `__iadd__` heuristic. Rewrote as the explicit
   `groups.add(mutableListOf(a, partner))`. Kotlin resolves `+=` here to exactly `.add`, so
   identical behaviour; the explicit call is unambiguous append for the transpiler.

2. **`Int / Int` truncating division → float** (a *real* transpiler gap, not an ambiguity):
   Kotlin `Int / Int` truncates to `Int`; Python `/` yields a float, which poisoned
   `range(sets)` downstream (`'float' object cannot be interpreted as an integer`). Two sites
   (`b.startSets / 2`, `rest * 3 / 5`) rewritten with explicit `.floorDiv(…)`. For the
   non-negative operands here (set counts / rest seconds) floorDiv == truncation == Python `//`,
   so identical Kotlin behaviour, and the integer intent is now carried syntactically.

### What the transpiler/runtime gained (general — not WFL-specific)

- **`.floorDiv` / Kotlin Int op → Python `//`** mapping (exact semantic match: both floor).
- **`groupingBy { }`** + a `_KtGrouping` (eachCount / fold / reduce / aggregate).
- **`orEmpty`** (non-null receiver → identity).
- **`mapTo` / `mapNotNullTo` / `filterTo` / `flatMapTo`** (map/filter into a destination, return it).
- **Java collection constructors**: `HashSet` / `LinkedHashSet` / `ArrayList` / `HashMap` / `LinkedHashMap`.

Each surfaced as a sharp ERR from the oracle, was fixed, and verified by re-run — the same
oracle-driven loop as logs 84–92, now run to completion.

## Why meet-in-the-middle is honest here (not a dodge)

The discipline (log_91/92): never produce a SILENT wrong result. A heuristic guess on the
`+=` ambiguity would have been exactly that. The meet-in-the-middle edit instead removes the
ambiguity at the source AND is *checked*: the JVM runs the edited Kotlin's full
SampleProgramDataTest green, so the edit provably preserves Kotlin behaviour, and the
transpiled Python passes the same assertions — `JVM: green -> EQUIVALENT (both green)`. Both
sides verified, nothing assumed.

## Net
Engine sweep complete: **5 → 151 passing methods, 1 → 10 green engines, 0 behavioural
divergences throughout.** Seven+ engines cross-checked EQUIVALENT on the JVM (incl. the
largest, AutoregulationEngine, and now SampleProgramData). The transpiler covers the full
engine+model corpus, judged at every step by runtime behaviour.

## Housekeeping
Stopped the idle Gradle + Kotlin compile daemons (~4 GB RSS) left from `--jvm` runs; they
re-spawn on demand for the next cross-check, so nothing is needed round-to-round.
