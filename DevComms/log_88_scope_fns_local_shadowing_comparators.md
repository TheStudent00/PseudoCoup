# log_88 — scope functions, local shadowing, comparators: third engine green (89→102)

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_87. Oracle-judged.

## Headline: 3/10 engines fully green; 102 passing methods; still 0 FAILs

NotificationTriggers 5/5 · CalibrationEngine 15/15 · **SubstitutionEngine 5/5** ·
AutoregulationEngine **54**/59 · RestartEngine 14/17 · CardioRecovery 6/12 · Warmup 3/12.

## What landed (this turn, across two commits)

**Scope functions (bfb538a).** `x.let/takeIf/takeUnless/also { it… }` rewritten at the
call site (they apply to any type), `?.`-aware. Cleared the `NoneType is not callable` /
`.let` AttributeError bucket. Autoreg 38→45.

**Non-local return (bfb538a).** `accelerateWeight(...)?.let { return it }` — the `return`
exits the ENCLOSING fn, not the lambda. The naive scope rewrite discarded it; the oracle
caught the divergence (expected 110, got 120 — an uncapped weight). `let` with a non-local
return now hoists a proper guard; other scope fns with non-local return fail loudly.

**This commit:**
- **KtSet** (set subclass): `setA + setB` is union, but Python `set + set` is a TypeError.
  KtSet's `+` unions (single elem vs collection disambiguated); setOf/mutableSetOf/emptySet
  return it; collection methods delegate to KtList. Unblocked SubstitutionEngine.
- **Numeric conversions:** `toDouble/toFloat` → float, `toInt/toLong` → int (truncating),
  `toString` → str, at the call site. Autoreg 46→54.
- **`List(n) { … }` / `MutableList` factories** in the shim.
- **Local-variable shadowing (the real bug).** The transpiler tracked only *parameters* in
  scope, not local `val`/`var`. SubstitutionEngine has `fun score(...) { var score = …;
  score += W_PATTERN }` — the local `score` resolved to the *method* `self.score` (→
  `method += float`). Now a function's local declarations (and for-loop vars) are collected
  into its scope so they correctly shadow members.
- **Comparators:** `Comparator` type with `thenBy/thenByDescending/reversed`, `compareBy/
  compareByDescending`, and `KtList.sortedWith(cmp)` (via `functools.cmp_to_key`). The last
  piece for SubstitutionEngine → 5/5.

## Next
AutoregulationEngine 54/59 — last few (enum-to-number comparison, `demoteOneStep` nested
extension, `range.map`, an `UnboundLocalError`). Then CardioRecovery 6/12, Restart 14/17,
Warmup 3/12, and the three exec-level 0-reach engines (Periodization/PathDefinition/
SampleProgramData).
