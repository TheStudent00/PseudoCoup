# log_79 — pseudokotlin P1 COMPLETE: grammar fully classified, 130/278 WFL compile

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_78 (P1 batch 1).

## P1 done: exhaustiveness gate enforced

`coverage.py`: **114 kinds · 39 ROUTED · 69 container · 6 out-of-scope · 0 UNROUTED.**
Every named grammar kind is now accounted for, and `test_coverage.py` enforces it
(`EXHAUSTIVENESS_ENFORCED = True`) — a kind going unclassified fails CI. 10/10 tests green.

## Batch 2 handlers added (12, on top of batch 1's 27)

- `when_expression` → if/elif/else, with **value-distribution**: `return when(x){…}` and
  `val y = when(x){…}` push `return `/`y = ` onto each branch (same machinery upgraded
  `if` in value position).
- `try_expression` → try/except/finally (`catch (e: T)` → `except T as e`).
- `lambda_literal` → `lambda …:` (single-expression); `v_call` now also picks up the
  **trailing lambda** (`xs.map { v -> v*2 }` → `xs.map(lambda v: v*2)`).
- `range_expression` (`0..n` → `range(0, n + 1)`), `infix_expression`
  (`to`→tuple, `until`/`downTo`/`step`→range forms, generic→method call),
  `collection_literal`, `callable_reference`, `qualified_identifier`,
  `spread_expression`, `annotated_expression`/`labeled_expression` (strip), `do_while`.
- elvis `?:` in `v_binary` → `(a if a is not None else b)`.

**Out-of-scope (6), deferred ON PURPOSE — not half-baked:** `object_declaration`,
`companion_object`, `object_literal`, `secondary_constructor`, `anonymous_function`,
`anonymous_initializer`. These are the Kotlin-model ≠ Python-model design decision
(TRANSPILER_SCOPE Group C: singleton/static mapping). They FAIL loudly until a
dedicated design pass — honest, per map·wrap·fail.

## P1 on the real WFL corpus (278 .kt) — the honest number

**130/278 py_compile-clean** (144 transpile without refusing). This is the first
real-corpus measurement; the remaining failures are a concrete, ranked P2 worklist:

| count | kind | what it needs |
|---:|---|---|
| 53 | `lambda_literal` | multi-statement lambdas → a `def` helper (Python lambdas are 1-expr) |
| 37 | `property_delegate` | `by lazy {…}` / `by remember {…}` → delegate lowering |
| 26 | `object_declaration` | the Group C OOP-model pass (deferred by design) |
| 17 | `getter` | custom `val x get() = …` → `@property` / method |
|  1 | `unary_expression` | one operator edge |

The three mechanical ones (lambda 53, delegate 37, getter 17 ≈ 107 file-hits) are the
high-leverage P2 batch; objects (26) are the design pass. None are mysteries — each is
a named node with a known shape, surfaced by the corpus exactly as P2 is meant to.

## Discipline notes

- The exhaustiveness + `routed ⊆ grammar` gates kept batch 2 honest: every new handler
  targets a real kind, every kind is bucketed.
- Value-distribution (`lead` threaded through `_if`/`_when`/`_branch`) is the clean
  answer to "Kotlin expressions vs Python statements" without the donor's block-wrapper
  functions — verified by `return when` / `val = when` goldens that compile.

## Next (P2)
Work the ranked worklist on the real corpus: multi-statement lambda → def-helper,
property delegates, getters; re-measure each. Then the Group C object/companion design
pass. Target: drive 130/278 toward 278, each file gated by py_compile (and ultimately
the WFL test oracle).
