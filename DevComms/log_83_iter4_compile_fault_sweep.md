# log_83 — transpiler iteration 4: ++/by-lazy, then a compile-fault sweep (domain 137→185 / 191)

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_81 (OOP-model pass) under the
iterate-loop (improve the transpiler to meet WFL; WFL refactors only on true model-
mismatch).

## How this iteration actually went

Started as the planned small tail (`++`/`--`, `by lazy`). Adding a standing
measurement tool (`tools/pseudokotlin/measure.py`) and re-measuring turned the
`<py_compile>` bucket — files that **transpile but emit Python that doesn't compile** —
into the real frontier. That bucket was 46 domain files; it is now 2. None of the bugs
were slop: each was a missing case in value-distribution or a model mismatch, caught by
the py_compile gate (never silently shipped).

## Landed

Behavioral additions:
- **`i++` / `i--` → augmented assignment** (`i += 1`). Pre/post distinction collapses;
  faithful in statement position (value position would `py_compile`-fail loudly, not
  mis-behave).
- **`val x by lazy { … }` → cached `@property`** (compute-once into `self._x`, guarded by
  `hasattr`). Single-threaded compute-on-first-access matches Kotlin `lazy`. Only `by
  lazy` is accepted — any other delegate (`Delegates.observable`, `viewModels()`, …)
  **fails loudly**, never silently mis-mapped.

The compile-fault sweep (the bulk of the win):
- **Expression-body value-distribution.** `fun f() = when/if { … }` was emitting
  `return <statement>` (→ `return if cond:`). The distribution logic already existed in
  `v_return`/`_render_property`; consolidated it into one `_distribute(node, lead)` and
  routed every value position through it (`= expr` bodies, getters, lazy, lambda tails,
  branch tails).
- **Extension functions.** `fun Recv.name(…)` is top-level; the receiver now becomes a
  `self` param (its `.` token is the marker). Same for **extension-property getters**
  (`val List<X>.tot get() = …` → top-level `def tot(self): …`).
- **Elvis with early return.** `val x = e ?: return d` cannot be a Python ternary (RHS is
  a statement). Now hoists a guard: `tmp = e; if tmp is None: return d; x = tmp`. This
  single fix was the biggest lever — pervasive in the repository layer (+~20 files).
- **Guard clauses.** One-armed `if (c) return x` was collapsing to `(return x if c else
  None)`. The `if` shape-check only looked for `block`; now a unified `_renders_stmt`
  predicate (block · when · try · block-if · return/throw/assign/loop/`++`) forces
  statement form whenever a branch is statement-shaped.
- **try-as-value.** `fun f() = try { a } catch(e) { b }` distributes the lead into the
  try/catch blocks (not `finally`, which never carries the value).
- **`_branch` unified through `_distribute`** so a branch whose last statement is itself a
  when/if/return/throw/`++` is handled correctly instead of blindly prefixed.
- **Python-keyword + backtick names.** `_safe()` (in the dispatcher base, applied at
  EMISSION only — match sets stay keyed on raw Kotlin names): `from`→`from_`, and
  `` fun `human readable name`() `` → a sanitized identifier (the Kotlin test idiom).
  Applied to def names, params, lambda params, members, navigation/infix selectors.

## Measurement (WFL corpus, excl. build/; domain = no `/ui/` segment, n=191)

| step | ALL /278 | domain /191 |
|---|---:|---:|
| start of iter 4 | 157 | 137 |
| + ++/by-lazy | 167 | 145 |
| + ext-fn / distribution / keyword names | 174 | 152 |
| + guard clause (stmt-form fix) | 174→… | 152→166 |
| + elvis-early-return + lambda-tail | 202 | 166 |
| + `_branch` unify + ++/-- in branches | 211 | 171 |
| + try-as-value | 226 | 181 |
| **+ extension-property getter** | **230** | **185** |

Domain **96%** compile-clean. The 6 remaining domain files all fail **loudly**:
`property_delegate` ×3 (non-lazy Compose/nav delegates — `by viewModels()` etc.),
`object_literal` ×1 (Room `object : Migration`), and 2 `<py_compile>` edge cases
(safe-call on an assignment LHS `crashlytics?.x = enabled`; `${n++}` — increment as a
value inside string interpolation). These are genuinely hard / out-of-scope, not slop.

## Discipline notes
- One `_distribute` + one `_renders_stmt` now own the Kotlin-expression-vs-Python-
  statement decision. Earlier the logic was duplicated across `v_return`,
  `_render_property`, `_render_function_body`, `_branch`, and `v_lambda` — every site
  that missed a case was a compile-fault. Consolidation is why the tail closed fast.
- 20 goldens (was 7): added guard-clause, elvis-early-return, expr-body-when,
  extension-fn, try-as-value, extension-property-getter, keyword-name, ++/--, by-lazy,
  loud-fail-on-non-lazy-delegate. Each asserts the Python **compiles** (anti-slop oracle).
- Coverage gate still green: `property_delegate`/`getter` stay CONTAINER (consumed by the
  property renderer, never dispatched); no UNROUTED introduced.

## Next
The compile gate is near-saturated for the domain layer — diminishing returns on chasing
the last 2 edge cases. The higher-value move is the **P4 runtime oracle**: transpile one
engine + its JVM test, run both sides, diff. Compile-clean ≠ behaves (extension fns and
`buildString` compile but won't *run* without their shims) — the oracle is what turns
"transpiles" into "provably equivalent," the next rung on the ladder (tests → state-trace
→ symbolic) from log_80.
