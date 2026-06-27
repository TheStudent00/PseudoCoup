# log_89 — long-tail correctness: list +=, continue/break, map[k], _name_of (104→112)

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_88. Oracle-judged.

## Reach: 112/128 passing methods (87.5%), 3/10 engines green, 0 FAILs

AutoregulationEngine **57**/59 · CalibrationEngine 15/15 · **CardioRecovery 11**/12 ·
NotificationTriggers 5/5 · RestartEngine 14/17 · SubstitutionEngine 5/5 · **Warmup 5**/12.

## Fixes (each a real Kotlin↔Python semantic gap the oracle localized)

- **`_name_of` (latent, broad).** `var remaining = targetPerSide` transpiled to
  `targetPerSide = targetPerSide` — for a property whose value is a bare identifier, the
  name lookup grabbed the VALUE id instead of the variable name (nested in
  `variable_declaration`). Any `val x = someVar` was wrong. Now the var-decl name wins.
- **Member extension functions.** `object E { fun Tier.demote() = … }` → top-level def +
  `Tier.demote = demote` patch (not a method of E, which the object-rebinding broke).
- **`list += elem`.** Kotlin appends; Python `+=` is `__iadd__` = extend, which ITERATES
  the element (`'WarmupSet' object is not iterable`). KtList.__iadd__ appends a non-
  collection, extends a collection. Also KtList.__add__ (concat vs append) and slice
  __getitem__ now stay KtList (a `list + list` had dropped back to a plain list).
- **`continue` / `break`.** They parse as plain `identifier` nodes in this grammar, so
  `if (a) continue` became `(continue_ if a else None)` (mangled + ternary). Now emitted
  verbatim and treated as statement-shaped, so the one-armed if is a statement.
- **`map[k]` → None for absent keys.** Kotlin returns null; Python `dict[k]` raises
  KeyError. KtMap.__missing__ returns None.
- **Ranges → KtList** so `(a..b).map { }` works.
- **Comparators** (log_88 tail): Comparator + compareBy/compareByDescending +
  KtList.sortedWith.

## Known hard limit
AutoregulationEngine's last 2 are Kotlin **method overloading** — two `seedWeightFromRelated`
(by SeedRelationship vs Double); Python keeps only the last def. Faithful handling needs
generated type-dispatch; deferred.

## Next
CardioRecovery 11/12 (one more), Restart 14/17, Warmup 5/12; then the exec-level 0-reach
engines (Periodization `VolumeLandmark`, PathDefinition self-ref, SampleProgramData) and
the `MS_PER_DAY`/default-after-nondefault dep issues.
