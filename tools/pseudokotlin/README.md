# pseudokotlin — the disciplined Kotlin→Python transpiler

tree-sitter is the truth; the transpiler is the other side of the same coin. Every
named grammar node kind is, on the record, exactly one of: **handled** (a registered
handler), **container/trivia** (consumed by a parent), **wrapped** (a shim — no
Python equivalent), or **out-of-scope** (refused). A coverage gate proves it.

## The contract — map · wrap · fail (never emit-and-hope)
A handler returns Python it can *guarantee* parses (MAP), or routes to a shim when
Kotlin has no Python equivalent (WRAP, e.g. `16.dp` → `dp(16)`), or raises (FAIL).
No handler returns hopeful text; unknown / parse-error nodes fail loudly.

## Routing
`@kind("if_expression", ...)` registers a method into an explicit `_route` dict;
`Visitor.visit` dispatches off `node.type` through it. The dict is introspectable, so
`coverage.py` / `test_coverage.py` diff its keys against the live grammar — that
check (not the lookup itself) is what makes this stable where an if-chain is not.

## Layout
```
parse.py        tree-sitter frontend + named_kinds() (the routing surface)
dispatch.py     Visitor, @kind registry, the map/wrap/fail contract, Untranspilable
classify.py     the 4 buckets (CONTAINER / WRAP / OUT_OF_SCOPE / + ROUTED)
transpiler.py   KtToPy(Visitor) — handlers land here in P1 (donor: ../transpiler)
coverage.py     worklist report — every kind + its bucket; drive UNROUTED → 0
tests/          test_coverage.py — consistency now, exhaustiveness at end of P1
nodes/          (P1) per-concern handler modules
wrap/           (P3) shim registry + runtime (seeded from ../../core)
```

## Run
```
python3 tools/pseudokotlin/coverage.py            # the worklist
python3 -m pytest tools/pseudokotlin/tests -q     # the gate
```

Status: **P0** — spine + registry + coverage gate stood up; `_route` is empty by
design, so the report shows the full construct surface as the worklist.
