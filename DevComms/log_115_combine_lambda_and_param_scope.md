# log_115 — transpiler fixes 3 & 4: combine-lambda hoist + lambda params shadow members

Date: 2026-06-28
Type: transpiler fixes (the last gate + one it uncovered). Oracle stayed ALL GREEN (11/11) through
every change.

## Direct answer

The two remaining transpiler bugs are fixed; a combine-based viewmodel now constructs AND renders
real data. exercise_picker's `combine` VM now produces the full seeded exercise list:

```
exercise_picker (AUTO):  before -> "VM did not construct (NameError _lam1)"
                          now    -> renders 185 real exercises (Arnold Press, Back Extension, …)
oracle: ALL GREEN (11/11)   ·   gym_list 10/10, paths 3/3, exercise_detail 4/5 (no regressions)
```

(The leaf MATCH stays low because the hand-built exercise_picker trace is degenerate — its harness
renders the empty list, not 185 rows — and the per-exercise muscle `displayName()` is unresolved
since the picker adapter doesn't lift its exercises. The SUBSTANCE — the combine VM constructs and
runs over real data — is proven.)

## Fix 3 — multi-statement `combine` lambda emitted with no def

`val uiState = combine(a, b) { x, y -> … }.stateIn(…)` is a class PROPERTY initializer. The
transpiler hoists a multi-statement lambda to `def _lamN(...)` on `self._hoist`, flushed by the
statement renderer — but property initializers were rendered by a list comprehension
(`[_render_property(p) for p in props]`) that never flushed `_hoist`, so `_lam1`'s def was lost
(`combine(…, _lam1)` referenced an undefined name -> the VM didn't construct). Fix
(`declarations.py`): render each property init in a loop that flushes `self._hoist` before the
assignment (mirroring `stmt_lines`), so `def _lam1(...)` is emitted just above
`self.uiState = combine(…, _lam1)`.

## Fix 4 — lambda params didn't shadow enclosing members

With the def emitted, the transform crashed: inside `combine{ …, query, … -> allExercises.filter {
ex -> query.isBlank() … } }`, the param `query` was rendered `self.query` (the VM's `query`
StateFlow property) instead of the lambda param — `v_lambda` never pushed its params onto
`self._scopes`, so `v_identifier` saw `query` as a member and qualified it. Fix (`expressions.py`):
`v_lambda` pushes its parameter names (and destructured names, or `it`) as a local scope for the
duration of body rendering, so params shadow members. `nonlocal` detection was adjusted to compute
captures against the OUTER scopes (excluding the lambda's own).

## Reading

All four transpiler gates the UI sequence surfaced are now closed (log_114: enum name/ordinal,
`!`-precedence/isNullOrBlank; here: combine-lambda hoist, lambda param scope) — each a real
correctness fix verified against the oracle, each unblocking many screens. The UI generator can now
drive a `combine` viewmodel end to end. What remains for broad coverage is per-screen harness polish
(lift each screen's entities for `displayName()`; wire detail/picker router ids for a fair
hand-built baseline) and the path-(c) app migration — no longer transpiler gaps.
