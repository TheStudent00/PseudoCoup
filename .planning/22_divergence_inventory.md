# 22 — Divergence inventory: base PseudoCoup vs WFL vendored copy (U5)

Status date: 2026-07-14. Classification ratified by Dee as decision D2 (see
`00_Upgrade_Plan.md`, "Decision queue — ALL DECIDED"); this note records the classification and
the per-row execution status after the U5 ports landed. Rule applied (per D2): framework-agnostic
= UPSTREAM, Compose/WFL-shaped = APP-SPECIFIC. Upstreaming was copy-forward only — the vendored
copy at `/home/lucas/Programming/WFL_PseudoCoup/pseudocoup/` was not modified.

Divergence scope (verified byte-level, survey of 2026-07-14): confined to `core/ledger.py`,
`core/ur_ast.py`, `ingress/kotlin.py`, `egress/dart.py`, plus two vendored-only files
(`ingress/coverage.py`, `egress/dart_compose_vocab.py`). Every other file was already identical.

## Inventory

| # | Divergence item | Vendored location | Classification (D2) | Status | Notes |
|---|---|---|---|---|---|
| 1 | Coverage gate (`CoverageRecorder` + `record_seen`/`record_dropped` hooks) | `ingress/coverage.py`, `ingress/kotlin.py` | UPSTREAM | ported | `pseudocoup/ingress/coverage.py` copied byte-identical; hooks live in `ingress/kotlin.py` only (verified: no other ingestor references coverage) |
| 2 | Coverage hooks in the other 10 ingestors | n/a (new work, ~4 lines each) | UPSTREAM | deferred | Cross-language behavior change; per U5 escalation rule ("confirm scope with Dee before touching more than Kotlin") this is deferred, not silently done |
| 3 | Param-shape ledger (`register_param_shape`, `get_param_shape`, scoped variants) | `core/ledger.py` | UPSTREAM (methods) | ported | Base `core/ledger.py` is now byte-identical to the vendored copy |
| 4 | Wiring param-shape registration into non-Kotlin ingestors | n/a | UPSTREAM (schema only) | deferred | Ratified as "UPSTREAM the ledger METHODS; DEFER wiring other languages" |
| 5 | Symbol-owner / ambiguous-import ledger infra (`file_map`, `symbol_owners`, `register_symbol_file`, `register_symbol_owner_only`) | `core/ledger.py` | UPSTREAM | ported | Included in the byte-identical `ledger.py` port; population is driver-side (a multi-file driver registers symbol files) |
| 6 | Enum/singleton/method-return/suspend/async-required ledger tables | `core/ledger.py` | UPSTREAM | ported | Included in the `ledger.py` port; consumed by the dart.py async propagation (row 12) |
| 7 | UR-AST additions (`LiteralNode.raw`, `ModifierNode`, `DeclarativeNode`) | `core/ur_ast.py` | UPSTREAM (inert schema) | ported | Base `core/ur_ast.py` byte-identical to vendored; base `kotlin.py` never PRODUCES `DeclarativeNode`/`ModifierNode` (that production is row 10, app-specific), so the nodes are inert in base |
| 8 | Kotlin enum/object/companion/init-block/object-literal ingress | `ingress/kotlin.py` | UPSTREAM | ported | Only one Kotlin ingestor exists; ported wholesale |
| 9 | Kotlin `when` lowering, elvis normalization, string interp, scope-function receiver binding | `ingress/kotlin.py` | UPSTREAM (Kotlin-generic parts) | ported | App-specific names excluded from the port: `BUILTIN_RECEIVER_MEMBERS` (kit.dart method names) and the WFL coroutine-scope names `launchSeed`/`appScope` (base keeps the generic `launch`/`withContext`/`runBlocking` over `viewModelScope`/`scope`) |
| 10 | Compose Modifier-chain extraction + declarative-call heuristic (`_extract_modifier_chain`, `DeclarativeNode` production, `declarative_heuristic_hits`) | `ingress/kotlin.py` | APP-SPECIFIC | stayed app-specific | Excluded from base `kotlin.py` (verified against vendored diff) |
| 11 | Dart import-hide computation (`_compute_import_hides`) | `egress/dart.py` | UPSTREAM (generic source only) | ported | Only the generic transpiled-vs-transpiled collision source (ledger `symbol_owners`/`file_map` driven) was ported. The two other collision sources in the vendored function — `KIT_CANONICAL_SYMBOLS` (kit.dart shims) and `FLUTTER_MATERIAL_HIDDEN` (flutter/material vs kit) — are WFL/Flutter app-specific and stayed. The split was clean (the function enumerates its three sources independently), so no escalation was needed |
| 12 | Dart transitive async/suspend propagation (`_compute_async_required` fixpoint pre-pass, `_call_is_async_result`, `_iter_calls`, `_collect_module_methods`, await-injection in `visit_CallNode`, `Future<R> ... async` signature lowering, plus the minimal ledger-driven resolver subset it needs: `_strip_generic_wrapper`, `_get_bare_identifier_type`, `_resolve_receiver_method_return`, `_is_receiver_method_suspend`) | `egress/dart.py` | UPSTREAM | ported | Verified on a kotlin→dart smoke case: `suspend fun` lowers to `Future<Int> fetch() async`, a sync caller is promoted (`Future<Int> load() async` with `await repo.fetch()`), and a second-order caller is promoted by the fixpoint (`indirect()` awaits the bare-`this` call). Unresolvable calls keep the honest `/* AWAIT-IN-SYNC */` flag, never guessed |
| 13 | Dart data-class `.copy()` synthesis (`_synth_data_class_copy`) | `egress/dart.py` | UPSTREAM | ported | Driven by `metadata['is_data']`/`data_fields` from the ported Kotlin ingress; skips classes that declare their own `copy` |
| 14 | Dart data-class named-constructor synthesis (`_synth_data_class_ctor`, `_synth_ctor_from_fields`, const-default machinery) | `egress/dart.py` | UPSTREAM by rule, outside the ratified row | deferred | Framework-agnostic companion to row 13, but D2's ratified row names exactly three egress concerns (import-hide, async propagation, `.copy()`); porting the ctor chain (init-formals, const-safety allow-lists) is a coherent follow-up unit, not forced into U5 |
| 15 | Dart Compose→Flutter declarative UI rendering (`visit_DeclarativeNode`, widget lowering) + `dart_compose_vocab.py` | `egress/dart.py`, `egress/dart_compose_vocab.py` | APP-SPECIFIC | stayed app-specific | 100% WFL data; not copied. Nothing in base references `dart_compose_vocab` (verified) |
| 16 | Dart enum/object/object-literal emission, init-block merge, nested-class hoisting, member-extension hoisting, multi-hop type resolvers (`_resolve_expr_type`), collection getter/`.size` mappings, cascade rendering (rest of vendored `egress/dart.py`) | `egress/dart.py` | APP-SPECIFIC per ratified SPLIT | stayed app-specific | Survey/D2: "the egress half is Dart-idiom-specific and would need re-deriving per target"; entangled with the vendored emitter's rewritten `_visit_FunctionDefNode_impl` and the Compose path |
| 17 | WFL driver/baseline (`tools/transpile_wfl.py`, `coverage_baseline.json`, `sync_wfl_src.sh`) | vendored `tools/` (outside package) | APP-SPECIFIC | stayed app-specific | Not upstream candidates; they are the WFL-side glue that populates rows 5 and 1 |

## Escalations

None. No row required forcing a generic/Compose-inseparable split: the import-hide function's
app-specific collision sources were cleanly separable (row 11), and the one genuinely ambiguous
discovery (row 14) fits the classification rule cleanly (framework-agnostic) and was deferred as
out of the ratified three-concern scope rather than escalated as a fork.

## Verification (2026-07-14)

| Check | Result |
|---|---|
| `python3 -m pytest tests/ -q` in `/home/lucas/Programming/PseudoCoup` | 48 passed (24 smoke + 24 snapshot vs `tests/snapshot_pre_upgrade/`) |
| Snapshot byte-compare after the `egress/dart.py` port | No diffs — python-ingress dart output (fox.py, space_station.py) unchanged; the base emitter's imports-before-body assembly order was deliberately preserved so single-file output stays byte-identical |
| Base vs vendored `ingress/coverage.py`, `core/ledger.py`, `core/ur_ast.py` | Byte-identical (full copy-forward) |
| Base vs vendored `ingress/kotlin.py` | Differs ONLY by the excluded app-specific pieces in rows 9-10 (verified by diff) |
| Coverage hooks outside `kotlin.py` | None (grep across `pseudocoup/ingress/`) |
| kotlin→dart smoke (data class + suspend + transitive caller) | `copy()` synthesized; `Future<R> ... async` emitted; `await` injected including fixpoint-promoted second-order caller |
| Import-hide unit check | Two owners of symbol `Foo` (`mod_a`, `mod_b`, last-writer `mod_b`) with both imported yields `{'mod_a': {'Foo'}}` — canonical owner stays visible, other hidden |

The vendored copy at `/home/lucas/Programming/WFL_PseudoCoup/` was not modified (binding D2
constraint: copy-forward only).
