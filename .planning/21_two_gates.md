# 21 — The Two Gates (direction note, authored in U4)

PseudoCoup now carries TWO gates. They check opposite directions of the pipeline and neither
subsumes the other. This note exists so nobody ever conflates them.

| | pseudoir gate (egress) | coverage gate (ingress) |
|---|---|---|
| Lives at | `pseudoir.gate` (PseudoIR repo, imported) | `pseudocoup/ingress/coverage.py` (in BASE since U5's port; original still in the WFL vendored copy) |
| Direction | egress — Hub source → named targets | ingress — source language → UR-AST |
| Runs | PRE-transpile (before ingest/emit), wired into `pseudocoup/cli.py` `main()` in U4 | POST-parse, hooked into the ingestor's `_map_node`/`parse` walk (currently `ingress/kotlin.py` only) |
| Question it answers | "Does every construct in this Hub source have a confirmed, non-`fail` realization in EVERY target I named?" | "Did the parser UNDERSTAND every node in the source — was anything dropped or silently skipped during ingest?" |
| Failure means | a target cannot realize a construct (a registry op has a `fail` or unconfirmed cell for that target), or a construct binds to no registry op at all (MAP failure) | the ingress parser has a gap: a tree-sitter node type it never visited or explicitly dropped |
| Applies to | Hub-notation input only: Python source that verifiably imports the `U` namespace (detected with `pseudoir.binder.u_import_present`, the gate's own definition). Plain python and the other 10 ingress languages are never gated | whichever ingestors carry the `record_seen`/`record_dropped` hooks — Kotlin today; the hook pattern is source-language-agnostic (~4 lines per ingestor) |
| On FAIL | print `pseudoir.gate.format_report`, refuse to emit, exit nonzero (matching `pseudoir.transpile`'s own contract) | report the dropped/unvisited node types against a baseline (see the WFL driver `tools/transpile_wfl.py --gate-coverage`) |
| Escape hatch | `--no-gate` CLI flag (default ON for Hub source) | driver-level: the gate is invoked by the coverage-aware driver, not by `cli.py` |

## Why they are complementary

The coverage gate guards "we understood the INPUT": it cannot say anything about whether the
output language can express what was understood. The pseudoir gate guards "the OUTPUT is
realizable": it cannot say anything about whether the parser silently dropped half the source
before the question was even asked. A pipeline that passes both has a stronger claim than either
alone: everything in the source was seen, and everything seen can be realized in the target.

## U4 scoping decisions (recorded per the natural-answer norm)

- The pseudoir gate runs only when `--source-lang python` AND the source imports `U`. Rationale:
  the gate MAP-fails plain-python idioms outside Hub discipline (verified: `examples/fox.py` and
  `examples/space_station.py` both MAP-fail it), so gating all python source would break every
  existing transpile; and the other ingress languages are not Hub notation by definition.
- `--no-gate` exists and the default is ON for Hub source. Rationale: discipline should be opt-out
  not opt-in (matching `pseudoir.transpile`, which always gates), but a developer iterating on a
  Hub file legitimately needs to inspect partial output.
- The gate receives the resolved target as a singleton list (PseudoCoup transpiles one target per
  invocation; alias forms like `kt`/`cs`/`ts` are canonicalized to registry column names first).
- D3 (binding, decided by Dee): `pending` status on swift/csharp cells is PASS-WITH-WARNING —
  recorded on stderr, non-blocking — for those two targets only. `pseudoir.gate` itself treats
  pending as not-ok (`LookupResult.ok` requires confirmed status); the downgrade is implemented on
  the PseudoCoup side in `cli.py`, leaving pseudoir semantics untouched. A `fail` strategy, or a
  pending cell in any OTHER target (e.g. `op.safe_call` @ cpp, `strategy=fail`), still blocks.

## Coverage-gate location note (post-U5)

Since U5's ratified port (D2), `ingress/coverage.py` exists in BASE PseudoCoup, byte-identical to
the vendored original at `/home/lucas/Programming/WFL_PseudoCoup/pseudocoup/ingress/coverage.py`,
with its hooks wired into base `ingress/kotlin.py`. The vendored copy remains untouched and
authoritative for the WFL project's own phases. References in older docs to the coverage gate
"living only in the vendored copy" describe the pre-U5 state.
