# log_40 — hardened the gate to catch silent drops: 130 found (were invisible). Next drive-to-0 target.

Date: 2026-06-25
Type: tooling (verifier only — `run_all.py`; I did not touch the transpiler). Follows log_39
finding #3.

## What I added

`run_all.py` now checks three gating axes (was just compile), plus two informational:

```
COMPILE OK 27/27   residual TODOs: 18   rt-fatal: 0   silent-drops: 130   enum-refs?: 15
GATE: exit 1  (silent-drops > 0)
```

- **silent-drops (GATING, new):** operator calls that lost their trailing lambda — `.map()`,
  `.filter()`, `.let()`, `.sortedBy()`, `combine(...)()`, etc. Empty args where Kotlin had `{ ... }`.
  This is the finding-#3 class: dropped logic that emits *nothing loud* (worse than `__TODO_EXPR__`)
  and that `py_compile` + the rt-fatal check both pass clean. **130 across the fleet** — i.e. the
  dominant remaining gap was entirely invisible until now (only 18 loud TODOs were visible).
- **enum-refs (informational, heuristic):** `Class.CONST` references to a class defined in-file that
  declares no such constant -> likely dropped enum entry -> AttributeError. **15 flagged.**

## Precision check (I validated before trusting the number)

Spot-checked the flagged sites against the Kotlin source: every one corresponds to a real trailing
lambda. e.g. `MyProgramViewModel`: emitted `.filter()` / `.sortedBy()` / `.map()` line up with
Kotlin `.filter {`, `.sortedBy {`, `.map {`. Distribution: `let()` 40, `map()` 20, `filter()` 13, …
All are operators that always take a lambda — no legit-no-arg false positives (any/all/count/first are
deliberately excluded from the operator list).

## Why this matters

"rt-fatal 0 / instance-shaped" (log_38) was real, but the green was over-optimistic precisely because
this class was unmeasured. With it gated, the board is honest:

```
compile 27/27 ✓   rt-fatal 0 ✓   silent-drops 130 ✗   enum-refs 15 (info)
```

## The drive-to-0 target for the next transpiler round (Gemini)

1. **Capture trailing lambdas in expression / RHS position.** They're currently only captured at
   statement level; in `self.x = a.map { } ` / `combine(a,b){ }` they vanish. Emit the lambda (as a
   `def _lambda_N` or inline) — and if it genuinely can't be translated, a loud marker, **never empty
   `()`**. Target: silent-drops -> 0.
2. **Generate enum entries** (finding #2): enum class -> class with `MEMBER = <ordinal/sentinel>`
   constants. Target: enum-refs -> 0.
3. Note the related shim mismatch: the shims define `map`/`combine`/etc. as *free functions* but the
   emitted code calls them as *methods* (`flow.map(...)`). Either give the `Flow` class those methods
   or have the transpiler emit `map(flow, ...)`. (Resolve alongside #1, or it AttributeErrors anyway.)

Gate command: `python3 tools/transpiler/run_all.py` — green requires compile 27/27, rt-fatal 0,
silent-drops 0.

Pointers: `tools/transpiler/run_all.py` (the new checks + the `_LAMBDA_OPS` list), log_39 (the three
findings), `core/flow.py` (free-fn vs method).
