# TRANSPILER_SCOPE — Kotlin→Python literal transpiler: coverage, gaps, and the path to "complete"

Status: 2026-06-27, evidence from transpiling the whole WFL app (254 `.kt`) and a
ground-truth coverage instrument. Reproduce the live numbers anytime:
`python3 tools/transpiler/coverage.py`.

---

## 1. The ideal we're building toward

A **total transpiler over the tree-sitter-Kotlin grammar**. tree-sitter is the *truth*;
the transpiler is the other side of the same coin. For **every** grammar node (and every
structurally-significant child shape), it must do exactly one of:

1. **Map** it to the equivalent Python, OR
2. **Wrap** it — emit a call into a shim layer — when Kotlin has no Python equivalent yet
   (`16.dp` → `dp(16)`; a `Flow` → a `core/flow.py` type), OR
3. **Fail loudly** — refuse to emit — if it can neither map nor wrap.

The one thing it must **never** do is **emit-and-hope**: reconstruct hopeful text that is
valid Kotlin but invalid (or silently wrong) Python. Today it does exactly that, which is the
root of every failure below.

## 2. How it works today, and the two structural flaws

The transpiler is already a node-type dispatcher: `parse_expression` is a big `if t == "...":`
chain for expressions, and a statement visitor handles declarations/statements. That skeleton
is **right**. Two flaws make it "literal/weak" rather than complete:

**Flaw 1 — dispatch is keyed on node TYPE only, not (TYPE + child structure).**
A handler emits one shape for every sub-case. The poster child:
```python
# navigation_expression handler — ONE rule for ALL member access:
return f"{left}.{right}"
```
So these two — which you correctly noted are *different keys* — collapse to the same path:
```
[navigation, [identifier,     identifier]]  foo.bar -> "foo.bar"   valid
[navigation, [number_literal, identifier]]  16.dp   -> "16.dp"     INVALID PYTHON
```
The `number_literal` child is sitting right there in the tree; the handler just never looks at
it. Same disease in `call_expression` (a trailing lambda appended *after* keyword args →
`Row(modifier=…, _lambda_5)`, a positional-after-keyword SyntaxError) and `assignment` (a
null-safe LHS `a?.b = c` → assignment to a conditional expression).

**Flaw 2 — emit-and-hope: handlers don't guarantee their output, and only *missing* handlers are loud.**
The loud fallthroughs (`return '"__TODO_EXPR__"'`; `# TODO_UNHANDLED_KOTLIN_NODE`) fire **only**
for node types with *no* handler at all. A handler that exists but is over-general emits broken
text that sails straight to the file; nothing validates it. (That answers "why didn't it just
fail to emit?" — `navigation_expression` *has* a handler, so it never reaches the loud path.)
Even the "loud" punts are quietly valid Python (`"__TODO_EXPR__"` is a string), so they
**compile** — which is why "192/254 compile-clean" massively overstates correctness.

## 3. Coverage over the grammar (ground truth)

The WFL corpus exercises **93 distinct node types**:

| bucket | count | meaning |
|---|---:|---|
| handled | 25 | a real rule that maps correctly (the common path) |
| **over-general** | 3 | `navigation_expression`, `call_expression`, `assignment` — handled but structure-blind → wrong on sub-cases |
| **punt** | 20 | dropped: `"__TODO_EXPR__"` (expr) or `# TODO_UNHANDLED` (stmt) |
| type-system | 11 | `user_type`, `nullable_type`, `function_type`, `type_arguments`… — needed for faithful annotations |
| container/trivia | 35 | consumed by a parent rule (`value_argument`, `string_content`, modifiers…) |

**Dropped this run: 187 expressions + 184 statements.** Those 371 drops are real logic the
emitted Python is missing.

## 4. The gaps, enumerated (nothing hiding) and ranked by effort

### Group A — trivial maps currently dropped (a few small fixes clear ~150 drops)
- **One statement-level fallback** ("if a statement is an expression node I don't special-case,
  emit `parse_expression(node)`") clears the bare-expression-statement drops:
  `unary_expression` (26), `in_expression` (28), `index_expression` (9), `binary_expression` (2),
  `identifier` (10), `string_literal` (1), `lambda_literal` (1) ≈ **77 drops, one fix**.
- **`this_expression` → `self`** (20 drops), **`super_expression` → `super()`** (3),
  **`range_expression` → `range(a, b+1)`** (4), **`return_expression`** edge (2).
- **`try_expression` wiring** (10): `catch_block` and `finally_block` are *already* handled — the
  `try_expression` node just isn't routed to emit `try/except/finally`.

### Group B — moderate, well-defined rules
- **Structure-aware sub-dispatch for the 3 over-general handlers**: `navigation` (number-receiver
  → unit wrap; enum/static access), `call` (trailing-lambda placement, named args, varargs),
  `assignment` (null-safe LHS).
- **`infix_expression`** (57 drops): map the known infix vocab (`to`→tuple, `until`/`downTo`/`step`
  →range forms, `and`/`or`/`shl`…) and generic infix → method call.
- **`assignment` in expression position** (108 drops): Kotlin allows assignment where Python
  doesn't (lambda bodies, `when` branches) → hoist to a statement / restructure.
- **`annotated_expression`** (6): strip or honor the annotation.

### Group C — design decisions required (Kotlin model ≠ Python model)
- **`object_declaration` (59) / `companion_object` (20) / `object_literal` (40)** — singletons,
  statics, anonymous objects. Need a chosen mapping (module-singleton vs class+classmethods;
  companion → class-level; object literal → anonymous class).
- **Type system (11 node types)** — `user_type`, `nullable_type` (`T?`→`Optional[T]`),
  `function_type` (`(A)->B`→`Callable`), generics. Needed for *faithful* annotations vs dropping
  them.

### Group D — the WRAP layer (your "wrap what has no Python equivalent yet")
Not node-type gaps — whole semantic categories that need a **shim registry + runtime libs**
(`core/coroutines.py`, `core/flow.py` are the start):
- **Kotlin stdlib extension functions** — `.dp`/`.sp`, `.let/.also/.run/.apply`, `.map/.filter/
  .firstOrNull`, `.isNotBlank()`… (thousands; `16.dp` is one). The general problem behind Flaw 1.
- **Jetpack Compose** — the `@Composable` DSL: declarative tree, `Modifier` chains, trailing-lambda
  content/slots, `remember`/state.
- **Coroutines / Flow / `suspend`** — `StateFlow`, `combine`, `flatMapLatest`, `collectAsState`.
- **Android framework** — `Activity`, `Context`, `registerForActivityResult`, Room DAOs, WorkManager.
- **DI / Hilt** — `@Inject`, `@Module`, `@HiltViewModel`.

## 5. How far off is "literal" from the ideal?

**Structurally: not far. In completeness of contract: a real redesign, but a bounded one.**
The grammar is finite (93 types here). The work is enumerable:
- ~8 fixes in Group A clear the bulk of the silent drops (one of them, the statement fallback, is
  a single change).
- ~4 rules in Group B (incl. making the 3 over-general handlers structure-aware).
- ~2 design calls in Group C (singletons; type/annotation policy).
- 1 architectural piece: the **wrap registry + the map-or-wrap-or-fail contract** (Group D) — this
  is the actual shift from "literal" to "complete": no handler may emit text it can't guarantee;
  unknown/foreign constructs wrap into a shim instead of reconstructing hopeful text.

It is **not** a rewrite. It's: (a) finish the ~20-node coverage gap, (b) refine 3 handlers to key
on child structure, (c) replace emit-and-hope with map-or-wrap-or-fail + a shim registry. Progress
is measurable — `coverage.py` drives PUNT and over-general counts toward zero.

## 6. Reproduce / track

- `python3 tools/transpiler/coverage.py` — the full 93-node inventory with live drop counts (the
  "nothing hiding" table; re-run as gaps close).
- `python3 tools/transpiler/transpile_app.py` — transpile the whole app → WFL_MixingCenter and
  report py-compile pass/fail.

> Note: the dominant *visible* failure (`N.dp`, 53 files) is a Group-D extension-property wrap and
> a Flaw-1 structure-aware fix at once. But it MASKS the trailing-lambda failure underneath it in
> nearly every UI file — so the headline error counts are a floor; the gap list above is the truth.
