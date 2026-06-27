# log_75 — structural backlog cleared: construct gate 12/12 (20/20 total)

Date: 2026-06-27
Type: implementation + measurement. Continuation of log_74. Worked the four
backlog items to PASS; one required a shared base-inference fix.

## Result

`gate.py` (the granular per-construct compile gate): **12/12 PASS**. With the
original 8-construct atlas (`run_atlas.sh`, still 8/8), **20/20 distinct constructs
compile to idiomatic Kotlin in a single hop**, every one verified by kotlinc.

## The four backlog fixes

1. **list comprehension** — pristine py2many had no Kotlin `visit_ListComp`, so it
   hit the common "unsupported" path and emitted `FAILED`. Added a lowering:
   `[elt for x in it if c]` → `it.filter { x -> c }.map { x -> elt }.toTypedArray()`.
   (`.toTypedArray()` keeps the result an `Array`, consistent with py2many's
   `List → Array` choice — otherwise `.map`'s `List` result mismatches the
   declared `Array<Int>` return.)
2. **tuple value** — Kotlin has no anonymous tuple literal. 2-tuple → `Pair(...)`,
   3-tuple → `Triple(...)`; removed the old `_visit_AssignOne` double-wrap that
   would now produce `PairPair(...)`.
3. **tuple type** — `Tuple[int,int]` return annotation resolved to the generic
   fallback `RT`; added a branch in clike's `_typename_from_annotation` (beside
   Optional/Callable) → `Pair<Int,Int>` / `Triple<…>`.
4. **type-aware `len`** — pristine maps `len(x)` → `x.size` unconditionally, which
   is wrong for `String` (`.length`). Added a pre-dispatch check in `visit_Call`
   that resolves the arg's declared type (via scope) and emits `.length` for
   `String`/`String?`, `.size` otherwise.

## The shared fix (the one that wasn't backend-local)

`dict_ops` produced an invalid `Union[Union[Union[…]]]` return type. Root cause is
**upstream**, in the base `py2many/inference.py` `visit_Return`: when a return
value's inferred type string differs from the *declared* return type, it did
`scope.returns.id = f"Union[{declared},{inferred}]"` — **clobbering the
source-declared annotation** — and compounded it across passes (`int` vs an
already-mapped `Int` is enough to trigger it). The function's own else-branch even
comments "Do not overwrite source annotation with inferred"; the if-branch
violated that.

Fix (`base_inference.patch`, separate from `pykt.patch` because it's shared):
flag annotations py2many infers itself (`py2many_inferred = True`) and only widen
*those* into a Union — never a source-declared one. Functions without a return
annotation behave identically (their inferred return is still flagged + widened).

**Regression check (shared code):** original Kotlin atlas still 8/8; cross-backend
smoke on `atlas.py` for Rust / C++ / Go / Julia all emit with no traceback and no
`Union[Union…]` nesting. The change is strictly more correct — it stops emitting
invalid nested unions; it never removes a union a backend legitimately inferred.

## Artifacts (committed)

- `pykt.patch` — Kotlin backend, now 4 files, round-trips vs pristine 0.8 wheel.
- `base_inference.patch` — the single shared-inference fix, round-trips.
- `constructs/` + `gate.py` — 12/12.
- README updated (apply = both patches; standing = 12/12, 20/20 total).

## Where this leaves the Python→Kotlin path

The routine + structural tiers are done and compile-verified: control flow,
arithmetic, collections, nullable, simple OOP, comprehensions, tuples, enums,
dataclasses, default args, type-aware stdlib. What remains is genuinely the hard
tier (unchanged): the broad stdlib long-tail (mapped one-by-one as usage demands),
and the Kotlin-specific idioms WFL leans on — Compose, coroutines/Flow, extension
functions — which are wrap-layer + manual, verified by the WFL test oracle.

Next: seed `constructs/` from the *actual* WFL_MixingCenter Python so the long-tail
mappings are driven by real usage rather than guessed; each addition gated by
kotlinc as before.
