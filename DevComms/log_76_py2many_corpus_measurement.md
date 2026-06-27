# log_76 — patched backend vs py2many's OWN corpus: 26/67 (26/27 of supported)

Date: 2026-06-27
Type: measurement. Answers "is there a real corpus to validate against, not our
toy atlas or our own circular WFL output?" — yes: py2many's own test suite.

## Why this corpus (the user's point, conceded)

Round-tripping WFL_MixingCenter Python back through py2many gives **no new
information** — it's our own K→Py output fed back in, circular. There are also **no
real third-party py2many→Kotlin apps** (the Kotlin backend is officially beta;
py2many is a research transpiler, exercised through its own tests). The genuinely
independent corpus is **py2many's own `tests/`**: 67 Python cases, 27 with
committed Kotlin expected outputs (maintainer-curated). All 27 committed expected
`.kt` compile (27/27) — solid ground-truth.

## Result (patched backend, `run_corpus.sh`)

**26/67 cases compile.** The decisive split:
- **26 of the 27 cases py2many ships Kotlin support for compile.** The single miss
  is `comment_unsupported` — the *deliberate* unsupported-constructs test. So our
  patches reproduce compiling Kotlin across essentially py2many's entire supported
  Kotlin surface, **zero regressions** from our changes.
- **40 of the 41 failures have no committed Kotlin expected output** — features
  py2many does not claim to support for Kotlin.

So the failures are not "our patches broke things"; they map py2many's real ceiling.

## The 40 unsupported failures, categorized (the beyond-py2many backlog)

**A. Big language features the Kotlin backend doesn't implement** (emit non-Kotlin
→ "Expecting a top level declaration" / "Type expected"). ~19 cases:
- async / await (`async`, `asyncio_case`)
- generators / `yield` (`generator`, `test_generators`, `yield_from`, `gen_exp`)
- dict comprehension (`dict_comp`)  [we did *list* comp only]
- try/except/raise (`exceptions`, `exception_names`)
- context managers `with` (`with`)
- walrus `:=` (`walrus`, `test_walrus_simple`, `lambda_walrus`)
- starred/unpacking (`starred`, `test_star`, `scope`)
- `del` (`delete`); multi-feature (`hello-wuffs`, `langcomp_bench`)

**B. Stdlib / module references unmapped** ("unresolved reference"). ~12 cases:
- `pow` (math_func), `re` (regex_methods), `sys` (stdio), `tempfile` (with_open),
  `str.join` (fstring, test_dunder), `lstrip` (stdlib_str), complex literal `j`
  (complex), byte literal `b'..'` (byte_literals), `argparse` (fib_with_argparse),
  field `default_value` (equations, sudoku).

**C. Localized type/structural bugs — same class as the ones we already fixed**
(the quick-win tier). ~9 cases:
- `property must be initialized` (datatypes, datatypes_base, triangle_buggy) — a
  class field-init shape our class fix doesn't yet cover.
- `missing return statement` (demorgan, smt_types).
- Int used where Boolean expected (comparison).
- `dict.keys()` invocation (dict). Sealed-class conflicts (sealed).
- lambda param needs explicit type (simple_lambda).

## Read

py2many (patched) is a **validated seed for the routine + structural bulk** —
proven against its own curated Kotlin surface (26/27). It is **not** a complete
transpiler: it has no Kotlin support for generators, async, exceptions, `with`,
walrus, dict/gen comprehensions, complex/byte literals, or a long stdlib tail.
Several of those (coroutines≈async, exceptions, `with`/`use`) are constructs WFL's
Kotlin actually uses — so py2many alone will not carry WFL; it seeds the table and
the common cases, the rest is the real transpiler work (wrap-layer + manual,
verified by the WFL test oracle).

## Reproduce
`bash tools/py2many_kotlin/run_corpus.sh` — clones py2many shallow, runs the gate
over all 67 cases, prints the pass list + the supported-vs-failing cross-ref.

## Next (decision point, not mechanical)
Three tractable tiers from category C/B and one strategic fork:
1. **Quick-win bugs (C):** property-init shape, missing-return, lambda param type,
   `dict.keys`, bool-in-condition — same kind we fixed; cheap; lifts the seed.
2. **Stdlib (B):** add mappings as WFL demands them (pow/re/sys/join/lstrip…).
3. **Big features (A):** async/exceptions/with/generators — large; only the ones
   WFL needs, and they shade into writing the real transpiler.
4. **Strategic:** we've measured py2many's ceiling. Reconnect to the original
   objective — use the validated construct-equivalence mappings to drive the WFL
   K→Py transpiler (PseudoKotlin scaffold from log_71), rather than grinding
   py2many's full backlog.
