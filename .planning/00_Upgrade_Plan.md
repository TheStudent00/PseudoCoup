# PseudoCoup V4 — Upgrade Plan: Integrate PseudoIR v2 as Operator-Semantics Authority

> VERSION: this upgrade IS the V3 -> V4 transition. As part of U1, bump `pyproject.toml`
> `version = "3.0.0"` -> `"4.0.0"` (rename approved by Dee in the executing session). Any doc
> text below still reading "V3" refers to the pre-upgrade baseline being described, not to a
> conflicting version decision.

## Execution status (updated by the executing session)

| Unit | Status | Evidence |
|---|---|---|
| U1 dependency wiring | COMPLETE 2026-07-14 | pseudoir relocated to PseudoIR repo root (git renames), its 17 tests pass from new location; PseudoCoup pyproject: version 4.0.0, pseudoir dep added, duplicate tree-sitter-dart removed, tree-sitter pin relaxed to >=0.22 (0.21.3 broke the CLI with current grammar wheels — recorded in pyproject comment); smoke import prints native_operator |
| U2 registry consultation | not started | blocked on U1 (now clear) + U3 mechanism scaffold |
| U3 hoister unification | not started | blocked on U1 (now clear) |
| U4 gate integration | COMPLETE 2026-07-14 | pseudoir.gate wired into cli.py main() as pre-transpile check: runs when --source-lang python AND source imports U (binder.u_import_present — plain python like fox.py MAP-fails the gate, verified, so it is skipped); singleton target list, aliases canonicalized; FAIL prints format_report + refuses to emit (exit 1); D3 pending-swift/csharp downgrade to stderr warning implemented in cli.py (pseudoir untouched); --no-gate escape hatch; 21_two_gates.md authored; tests/test_gate.py adds 6 tests (pass/refuse-on-real-fail-cell op.safe_call@cpp/warn/skip/bypass) — suite now 54 passing |
| U5 divergence reconciliation | COMPLETE 2026-07-14 | 22_divergence_inventory.md authored (17 rows: 9 ported, 5 app-specific, 3 deferred); coverage.py/ledger/ur_ast byte-identical to vendored; kotlin.py ported minus Compose pieces; dart.py +404 (import-hide, async propagation, .copy() synthesis); WFL copy untouched; 48 tests pass |
| U6a test harness | COMPLETE 2026-07-14 | run_tests.sh repaired; tests/test_transpile.py + test_snapshot.py (48 passing); 24-file pre-upgrade snapshot at tests/snapshot_pre_upgrade/ |
| U6b full verification | not started | blocked on U2/U3/U4 |

Status date: 2026-07-14. Author-of-record: planning agent, for Dee's sign-off. This is a
PLANNING document only — no code in any repo was modified to produce it. It is written to be
executed by a FRESH agent session with no memory of the conversation that produced it; every
path, count, and decision needed is stated inline here.

Formatting note (binding on every executor of this plan): tabular data goes in markdown pipe
tables or prose — NEVER in whitespace-aligned code blocks. This is per
`/home/lucas/Programming/WFL_PseudoCoup/.DevComms/LLM_communication_protocol.md` §3. Code blocks
are for actual code only. See "Standing rules" below.

---

## Mission

`pseudocoup` (the V3 transpiler at `/home/lucas/Programming/PseudoCoup`) currently hardcodes
operator-lowering semantics independently inside all 12 egress emitters. `pseudoir` (the
productized package at `/home/lucas/Programming/PseudoIR/v2/pseudoir`, version 0.1.0, landed
2026-07-14) exists as the machine-confirmed authority for exactly that knowledge: which source
operator lowers to which target strategy, backed by recorded runtime confirmation per language
column.

The mission of this upgrade is: **PseudoCoup imports `pseudoir` and consults it as its
operator-semantics authority**, replacing its 12 duplicated, inconsistent, in-places-broken inline
operator-lowering chains with registry lookups; unifying its (currently nonexistent) expression
hoisting on `pseudoir.hoist`; and gaining `pseudoir.gate` as a pre-transpile discipline check for
Hub-authored source.

This upgrade plan IS the concrete realization of what PseudoIR's own plan called "X1 —
cross-pollination back to WFL_PseudoCoup." See `20_PseudoIR_X1_supersession_note.md` in this
directory and the updated X1 stub in `/home/lucas/Programming/PseudoIR/v2/PLAN.md`.

---

## Terms (defined once)

Registry
    The `pseudoir` operator table. Each cell answers "operator/construct X in target language Y →
    what lowering strategy, is it confirmed?".
    example tied to context:
        `pseudoir.registry.lookup("op.overloaded_binary", "dart")` returns a `LookupResult` whose
        `.strategy` is `native_operator` (Dart lets you define `operator +`), while the same call
        with `"go"` returns `.strategy == "method_call"` (Go forbids operator overloading, so
        `a + b` must lower to `a.add(b)`).

Informal lowering
    An operator-to-target mapping hardcoded inline inside a PseudoCoup emitter's
    `visit_BinaryOpNode` / `visit_CallNode`, with no shared source of truth.
    example tied to context:
        `pseudocoup/egress/go.py` `visit_BinaryOpNode` (~lines 262-285) maps `//` to
        `({left} / {right})` and `is` to `{left} == {right}` by hand; nothing else in the repo
        knows those decisions were made.

Hoisting
    Lifting a construct that cannot legally sit in target expression position out into one or more
    preceding statements plus a temp variable. `pseudoir` provides ONE shared mechanism,
    `pseudoir.hoist()` → `Hoister`, with `Hoister.hoist_stmt(stmt_lines, result_expr) ->
    (temp_name, result_expr)`.
    example tied to context:
        `pseudocoup/egress/go.py` currently fakes an expression-position dict-membership test with
        an inline IIFE (`func() bool { _, ok := m[k]; return ok }()`) — a one-off substitute for
        the general hoisting `pseudoir.hoist` provides.

Gate
    `pseudoir.gate.check(src_bytes, targets) -> GateResult`. Parses a Hub source file
    (Python-notation using the `U.` null-safety namespace + annotated types) and returns PASS/FAIL
    for a chosen target-language set: every construct must bind to a registry op or a baseline
    node (MAP), and every bound op must have a confirmed non-`fail` lowering column in every target
    named (WRAP).

Coverage gate (WFL)
    A DIFFERENT gate, living in the vendored WFL copy at
    `/home/lucas/Programming/WFL_PseudoCoup/pseudocoup/ingress/coverage.py`. It instruments the
    Kotlin INGRESS parser and reports which tree-sitter nodes were dropped/unvisited during
    parsing. It checks the ingress direction (did we understand the source?), whereas the
    `pseudoir` gate checks the egress direction (can every construct be realized in every target?).
    Keeping these two straight is the whole content of work unit U4.

Base PseudoCoup
    `/home/lucas/Programming/PseudoCoup` — the repo this plan upgrades. Git repo, branch `master`,
    package import name `pseudocoup`, version 3.0.0.

Vendored PseudoCoup
    `/home/lucas/Programming/WFL_PseudoCoup/pseudocoup/` — a copy that diverged during the "WFL
    push," gaining a coverage gate, param-shape ledger, Kotlin object-model handling, and a much
    larger Kotlin-ingress / Dart-egress. Divergence inventory is work unit U5.

---

## Current-state survey (results, 2026-07-14)

All findings below were gathered by read-only survey. Claims are sourced to file/line where
load-bearing. "unverified" marks anything not directly confirmed this pass.

### Base PseudoCoup structure

The repo root holds `README.md`, `pyproject.toml`, `run_tests.sh`, `LICENSE.pdf`, `examples/`,
`tests/`, and the importable package `pseudocoup/`. Note the task brief assumed top-level
`core/ ingress/ egress/`; in reality those live one level down inside the package:
`pseudocoup/core/`, `pseudocoup/ingress/`, `pseudocoup/egress/`.

- `pseudocoup/core/`: `ledger.py` (45 lines — cross-language symbol table, `Ledger` class with
  `dump()/load()` to `.ledger.json`), `ur_ast.py` (124 lines — the Universal Rich AST node types:
  `URNode`, `ModuleNode`, `FunctionDefNode`, `BinaryOpNode(left,right,operator)`, `CallNode`,
  `IdentifierNode`, `LiteralNode`, control-flow nodes, `ListNode/DictNode/SubscriptNode/
  AttributeNode`). No dedicated node types for unary ops, ternaries, comprehensions, lambdas,
  f-strings, walrus, or destructuring — those are either smuggled through `BinaryOpNode` or absent.
- `pseudocoup/ingress/`: 11 parsers (Python, Dart, Kotlin, Java, C#, TypeScript, Swift, Rust, C++,
  Ruby, PHP), each a `<Lang>Ingestor` using tree-sitter + a `_map_node` recursive walker. **No
  `go.py`** — Go is egress-only.
- `pseudocoup/egress/`: 12 emitters (the 11 above PLUS `go.py`), each a `<Lang>Emitter` dispatching
  via `getattr(self, f"visit_{type(node).__name__}", generic_visit)`; `generic_visit` raises
  `NotImplementedError` (unmapped node types hard-fail, they do not degrade silently).
- `pseudocoup/graph/` and `pseudocoup/semantic/`: **orphaned** — only stale `__pycache__/*.pyc`
  remain (filenames `cfg_builder`, `ssa`, `type_prop`, `registry`), source `.py` deleted in the V3
  rewrite commit `5fcb2ae`. Notably a `semantic/registry.py` existed in V2 and was removed; worth a
  `git log --diff-filter=D` look before designing the new consultation path, but it is not
  load-bearing for this plan.

### Base PseudoCoup — the informal operator lowerings (the U2 target)

Every one of the 12 emitters implements `visit_BinaryOpNode` as an independent hand-written
if/elif chain reading `node.operator` (a raw string) and emitting target syntax. **There is no
shared table anywhere.** Per-emitter locations and the operators each handles:

| Emitter (file) | `visit_BinaryOpNode` approx lines | Operators handled inline (and notable bugs) |
|---|---|---|
| `egress/python.py` | ~232-245 | reverses ingress normalization only (`&&`→`and`, `||`→`or`, `!`→`not`); target is Python |
| `egress/dart.py` | ~224-238 | `in`→`.contains()`, `//`→`~/`, `is`+null→`==`; non-null `is` falls through to Dart type-check `is` (latent bug) |
| `egress/go.py` | ~262-285 | `in`→type-branched (`Contains`/IIFE), `//`→`/`, `/`→float64 cast, `is`→`==`; **`**`/`%` unhandled → invalid Go** |
| `egress/kotlin.py` | ~229-248 | `//`→`(a/b).toInt()`, `is`/`is not`+null→`===`/`!==`; **`**`/`%` unhandled → invalid Kotlin**; dead `} else {` branch ~332-335 |
| `egress/java.py` | ~257-280 | `in`→`.contains()`, `//`→`(int)` cast, `is`+null→`==`, non-null `is`→`instanceof`; **missing `and`/`or`→`&&`/`||`** |
| `egress/csharp.py` | ~258-281 | like java.py but DOES map `and`/`or`→`&&`/`||` (inconsistency with java.py) |
| `egress/typescript.py` | ~218-240 | `in`→native `in`, `//`→`Math.floor` (only correct floor-div), `is`+null→`===`, non-null `is`→`instanceof` |
| `egress/swift.py` | ~206-227 | `//`→`Int(a/b)`; **no `in` handling at all**, **no null-guard on `is`** (both bugs) |
| `egress/rust.py` | ~235-251 | `//`→`/` (no int/float branch), `is`→`==`, `and/or`→`&&`/`||`; **`**` unhandled → invalid Rust** |
| `egress/cpp.py` | ~211-227 | near-identical to rust.py; **`**` unhandled → invalid C++**; `visit_ForNode` string-sniffs `"builtins_py::range("` prefix |
| `egress/ruby.py` | ~100-116 | `//`→`/` (accidentally correct), `is`→`==` |
| `egress/php.py` | ~141-157 | `//`→`intdiv()`, `is`/`is not`→`===`/`!==`; **missing `+`-as-string-concat (PHP needs `.`)** — correctness bug |

Cross-cutting duplicated patterns (not operators but same "reimplemented per emitter" problem,
relevant context for U2/U3): builtin-remap tables (`print`/`len`/`str`/`range`/`math.`/`os.`
namespace prefixes) duplicated per emitter's `visit_CallNode`; unary ops smuggled through
`BinaryOpNode` with an empty-named `IdentifierNode` sentinel; elif-chain detection reimplemented
7×; `__name__ == "__main__"` sniffing reimplemented (go.py has none → main-guard silently vanishes).

**Consequence for the plan:** the operator lowerings PseudoCoup hardcodes map directly onto
`pseudoir` registry ops. The mapping (U2) is: PseudoCoup's `//`, `is`/`is not`, `**`, `in`,
`and`/`or` handling → the registry answers those per target with confirmed strategies; PseudoCoup's
`range()`/`__range__` builtins → `op.range`; its string-formatting → `op.string_interp`; its
spread handling → `op.spread_call`/`decl.variadic`; user-type operators (not currently modeled)
→ `op.overloaded_binary`. Several base bugs above (`**`/`%` unhandled in Go/Kotlin/Rust/C++, Swift
missing `in` and the null-guard, Java missing `and`/`or`, PHP `+`-concat) are things the registry
gives correct answers for — U2 should FIX them via the registry, not just relocate them.

### Base PseudoCoup — hoisting

**No emitter implements general hoisting.** Every `visit_*` returns a single self-contained string
built by recursive `self.generate()` calls. No `pending_statements` list, no temp-var injection,
anywhere in the ~5,127 lines of egress. The only two workarounds: go.py's dict-`in` IIFE
(`visit_BinaryOpNode`), and swift.py's shallow `try`-prepend heuristic in `visit_TryCatchNode`
(~349-369, explicitly commented as incomplete). This makes U3 partly a from-scratch build of
hoisting infrastructure, not a pure refactor — but `pseudoir.hoist` supplies the mechanism.

### Base PseudoCoup — test state

- **No pytest test functions exist.** `grep` for `def test_`/`import pytest`/`import unittest`
  across `tests/` returned zero. `.pytest_cache/` at root is a stale artifact (empty run).
- `tests/roundtrip/` is NOT a test suite — it is a directory of generated transpilation artifacts
  (per-language `.dart/.go/.kt/...` outputs + Python round-trip files) produced by manually running
  `run_tests.sh`. No assertions, no pass/fail signal.
- `run_tests.sh` (repo root) is **stale/broken**: it references `examples/quickfox.py` and
  `examples/quickfox.ledger.json`, neither of which exists (only `examples/fox.py` and
  `examples/space_station.py` exist — `fox.py` was likely renamed from `quickfox.py`).
- No CI config (`.github/`, no `.yml`), no `pytest.ini`/`conftest.py`/`tox.ini`.
- `examples/emitted_fox/` is a stale (Jul 8) snapshot; `08_c.c` shows visibly broken output
  (`printf();`, `if () {}`) — evidence a prior pipeline run produced invalid target code.

**Consequence:** there is no existing automated regression net in base PseudoCoup. U6 must build
one alongside the integration, and must first repair or replace `run_tests.sh` before it can be
relied on.

### Base PseudoCoup — package layout (for U1)

Python package, flat layout, `pyproject.toml` (setuptools). `[project] name = "pseudocoup"`,
`version = "3.0.0"`, `requires-python = ">=3.10"`, console script
`pseudocoup = "pseudocoup.cli:main"`. Dependencies: `tree-sitter==0.21.3` plus per-language
grammars (note `tree-sitter-dart` is listed twice — a duplicate; and `tree-sitter-c` /
`tree-sitter-go` are present though there is no C ingress/egress and no Go ingress — vestigial).
`pseudoir` is NOT currently a dependency. Import name would be `import pseudoir`.

### PseudoIR v2 — the package being imported (for U1/U2/U3/U4)

Package root `/home/lucas/Programming/PseudoIR/v2/pseudoir`, `pyproject.toml` name `pseudoir`
version `0.1.0`, `requires-python >=3.10`, deps `tree-sitter>=0.21` + `tree-sitter-python`,
console script `pseudoir = "pseudoir.__main__:main"`. Installed editable via
`pip install -e /home/lucas/Programming/PseudoIR/v2/pseudoir`. Import name `import pseudoir`.

The consumer API surface (from `pseudoir/INTEGRATION.md`), with exact signatures:

- `pseudoir.registry.lookup(op_id, target) -> LookupResult` — module-level convenience over
  `Registry.lookup`. `LookupResult` fields: `.op_id, .target, .kind ("op"|"xform"), .strategy,
  .status, .lowering, .source_binding, .evidence, .ok (strategy≠fail AND status confirmed),
  .is_fail, .present`.
- `pseudoir.hoist() -> Hoister`. `Hoister.hoist_stmt(self, stmt_lines, result_expr) ->
  (temp_name, result_expr)` (appends to `.prelude`, replaces `@TMP@` placeholder with a fresh
  temp); `Hoister.fresh() -> str`.
- `pseudoir.gate.check(src_bytes, targets, hub_file="<source>") -> GateResult`. `GateResult`
  fields: `.passed, .bound_ops, .map_failures, .wrap_failures (list of (op,target,strategy,
  status)), .coverage, .baseline_node_types, .classification, .u_import_verified`. Also
  `pseudoir.gate.check_file(path, targets)`, `pseudoir.gate.format_report(res) -> str`.
- `pseudoir.transpile(source, target) -> str` — gate-checks first (raises `pseudoir.GateFailure`
  with `.report`/`.result` on FAIL), then emits. `SUPPORTED_TARGETS = ("python", "typescript",
  "go", "dart")`; `RUNNABLE_IN_SANDBOX = ("python", "typescript")`.
- `from pseudoir import U` — the Hub null-safety runtime (`U.coalesce`, `U.safe`, `U.not_null`).

Registry coverage (12 ids): `op.null_coalesce`, `op.safe_call`, `op.coalesce_assign`,
`op.not_null_assert`, `op.destructure`, `op.overloaded_binary`, `op.range`, `op.spread_call`,
`op.string_interp`, `op.match_expr`, `xform.named_args`, `decl.variadic`. Language columns:
10/12 runtime-confirmed on most tiers (python, typescript, java, go, rust, ruby, php, kotlin, cpp,
dart); **swift and csharp are honestly `pending`** (no host toolchain). This pending state is
upgrade-relevant: PseudoCoup emits 12 targets including swift and csharp, but the registry cannot
yet confirm those two — see decision D3.

Gate direction (from `v2/gate/DISCIPLINE_CHECK.md`): the gate's SOURCE is a Hub Python-notation
file; its TARGETS are the output languages named in the call. It checks "does every construct in
this Hub source have a provable realization in every target I named" — Hub-source → per-target
realizability. It does NOT check target code against source.

Tests: exactly **17 pytest items** (verified against the cached nodeids) —
`tests/test_gate_fixtures.py` (3), `tests/test_probers.py` (1 parametrized × 9 = 9),
`tests/test_roundtrip.py` (5). Run with `cd /home/lucas/Programming/PseudoIR/v2/pseudoir &&
python -m pytest`. Caveat: `test_probers.py`/`test_roundtrip.py` reach sibling dirs under `v2/`
(`registry/`, `prober/`, `gate/fixtures/`) via a `..`/`..` path — the suite is NOT self-contained
to the `pseudoir/` subpackage. This matters for U1 if `pseudoir` is relocated out of `v2/`
(decision D1).

### Base-vs-vendored divergence (the U5 input)

Comparing `/home/lucas/Programming/PseudoCoup/pseudocoup/` (base) against
`/home/lucas/Programming/WFL_PseudoCoup/pseudocoup/` (vendored). The divergence is surgically
scoped: every non-Kotlin/non-Dart file is byte-identical between the two copies. Confirmed
byte-identical: all `egress/*` except `dart.py`, all `ingress/*` except `kotlin.py`,
`core/__init__.py`, `cli.py`, `__init__.py`.

Files ONLY in vendored: `pseudocoup/ingress/coverage.py` (new, ~82 lines), and
`pseudocoup/egress/dart_compose_vocab.py` (new, ~250 lines). Files that DIFFER:

| File | Base lines | Vendored lines | What the vendored copy added |
|---|---|---|---|
| `core/ur_ast.py` | 124 | 142 | `LiteralNode.raw` flag; two new node types `ModifierNode`, `DeclarativeNode` |
| `core/ledger.py` | 45 | 289 | param-shape ledger (`param_shapes`, `param_shapes_scoped`, `register_param_shape`, `get_param_shape`); symbol-owner/ambiguous-import infra (`file_map`, `symbol_owners`); enum/singleton/method-return/suspend tables |
| `ingress/kotlin.py` | 427 | 1804 | coverage hooks; enum/object/companion/init-block/object-literal handling; scope-function receiver binding; `when` lowering; elvis normalization; Compose Modifier-chain extraction |
| `egress/dart.py` | 411 | 3562 | Compose→Flutter declarative UI rendering; async/suspend propagation; import-hide computation; data-class `.copy()` synthesis; ledger-driven type resolvers; enum/object/object-literal emission |

Classification of the vendored improvements (generic-and-upstreamable vs app-specific), which is
the exact question U5 answers for Dee:

- **Coverage gate** (`ingress/coverage.py` + the `record_seen`/`record_dropped` hooks in
  `kotlin.py` `_map_node`/`parse`): GENERIC. `coverage.py` has zero Kotlin/WFL-specific logic; the
  hook pattern is ~4 source-language-agnostic lines droppable into every ingestor. The
  `tools/transpile_wfl.py` driver and `tools/coverage_baseline.json` are the only WFL-specific glue
  and live OUTSIDE the `pseudocoup/` package.
- **Param-shape ledger** (`core/ledger.py` methods): GENERIC schema, currently NARROW usage
  (populated only by `ingress/kotlin.py`, consumed only by `egress/dart.py`). Upstreaming the
  ledger methods is low-risk; wiring other languages is a separate effort.
- **Enum/object-model handling** (`kotlin.py` `_map_node` branches; `dart.py` `_visit_enum_class`,
  `_visit_object`, `_visit_object_literal`, `_merge_init_blocks`): SPLIT. The ingress half is "the"
  Kotlin implementation (only one Kotlin ingestor exists) — portable wholesale. The egress half is
  Dart-idiom-specific and would need re-deriving per target.
- **Kotlin ingress advances** beyond object-model (scope-function binding, `_map_when`, elvis,
  string interp): SPLIT. `when`/elvis/scope-function are Kotlin-generic; `BUILTIN_RECEIVER_MEMBERS`
  (kit.dart names) and Compose Modifier-chain extraction are WFL/Compose-specific.
- **Dart egress advances** (`egress/dart.py` + `dart_compose_vocab.py`): MOSTLY app-specific.
  `dart_compose_vocab.py` is 100% WFL data (curated from grepping WFL's Dart output). But
  `_compute_import_hides` (ambiguous-import avoidance) and `_compute_async_required` (transitive
  suspend/async propagation) and the data-class `.copy()` synthesis are generic Kotlin→Dart
  concerns.
- **UR-AST schema additions** (`LiteralNode.raw`, `ModifierNode`, `DeclarativeNode`): GENERIC,
  low-risk to upstream as inert/optional schema (other languages simply never produce them).

Tests: base has the 40-file `tests/roundtrip/` fixture set (but no assertions, see above); vendored
has NO `tests/` dir, NO `pyproject.toml`, NO `run_tests.sh` at all — it substituted a real-codebase
transpile + coverage gate (`tools/transpile_wfl.py --gate-coverage` over 325 Kotlin files) as its
correctness oracle. So the vendored Kotlin/Dart changes have never been exercised by base's
round-trip suite, and the base's 11 untouched language pairs have no automated check either.

---

## Work-unit sequence

Six units, U1..U6. Dependency order: U1 must land first (nothing else can import `pseudoir`
without it). U2 and U3 both depend on U1 and may proceed in parallel once U1 lands, but U3 (hoister)
should be scaffolded before U2 emitters that need hoisting for a given op. U4 depends on U1 only.
U5 is independent of U1-U4 and can run in parallel from the start (it is a survey-and-classify unit
whose output is a Dee decision, not code). U6 depends on U1-U4 landing and on U5's decision.

Each unit is specified in full in this document below. Per-unit fields follow the WFL house
standard: What / Where (file+function level) / Evidence (counts, sourced) / Acceptance (falsifiable
check) / Escalation triggers.

### U1 — Dependency wiring: `pseudoir` installable from PseudoCoup

**What.** Make `pseudoir` importable inside the `pseudocoup` package so U2-U4 can call it. Two
options exist; Dee decides (decision D1). Wire whichever is chosen into
`/home/lucas/Programming/PseudoCoup/pyproject.toml` `[project] dependencies`, and add an
integration smoke import.

Option A — **path/editable dependency**: `pseudocoup` declares a dependency on `pseudoir` pointing
at `/home/lucas/Programming/PseudoIR/v2/pseudoir` (or wherever it is relocated). Executor documents
the exact install line: `pip install -e /home/lucas/Programming/PseudoIR/v2/pseudoir` then
`pip install -e /home/lucas/Programming/PseudoCoup`. Pro: single source of truth, pseudoir
improvements flow automatically. Con: PseudoCoup's build now depends on a sibling repo path;
`pseudoir`'s test suite is not self-contained to its subpackage (it reaches `v2/registry`,
`v2/prober`, `v2/gate/fixtures` via `..`) — relocating `pseudoir` out of `v2/` would break
`pseudoir`'s OWN tests unless those sibling data dirs move too. Flag this to Dee under D1.

Option B — **vendored copy**: copy the `pseudoir` package into `pseudocoup/` (e.g.
`pseudocoup/_pseudoir/` or a top-level `pseudoir/` under the PseudoCoup repo), pinned at a recorded
version/commit. Pro: PseudoCoup builds standalone; no cross-repo path. Con: a second vendored copy
to keep in sync (the project already has one painful vendoring relationship — WFL's copy of
PseudoCoup); registry JSON updates in PseudoIR must be re-synced manually.

**Where.** `/home/lucas/Programming/PseudoCoup/pyproject.toml` (`dependencies` list — also fix the
duplicate `tree-sitter-dart` entry on lines 21 and 25 while here, and note the vestigial
`tree-sitter-c`/`tree-sitter-go`). A new smoke test file (path decided in U6). No emitter code
changes in U1.

**Evidence.** `pseudoir` is pip-installable: confirmed `pyproject.toml` name `pseudoir` v0.1.0,
`pseudoir.egg-info/` present (already built editable in its environment once). Import name
`pseudoir`. `pseudocoup` `pyproject.toml` currently has NO `pseudoir` dependency (14 deps listed,
lines 18-34, none is pseudoir). Both require Python >=3.10 (compatible). Both pin/allow
`tree-sitter` but at different specs: PseudoCoup pins `tree-sitter==0.21.3`, PseudoIR requires
`tree-sitter>=0.21` — compatible, but note the pin narrows the shared range (flag if a conflict
surfaces at install).

**Acceptance.** From a fresh venv, installing PseudoCoup (per whichever option) makes
`python -c "import pseudocoup; import pseudoir; from pseudoir import registry, gate, hoist;
print(registry.lookup('op.overloaded_binary','dart').strategy)"` print `native_operator` with exit
0. The `tree-sitter` install resolves without a version conflict.

**Escalation triggers.**
- D1 (Dee): path-dependency vs vendored-copy — introduces new structure/a new vendoring
  relationship. NAMING/STRUCTURE decision. Do NOT pick unilaterally.
- If Option A is chosen AND relocating `pseudoir` out of `v2/` is desired: pseudoir's own tests
  break (they reach `v2/` siblings). Escalate the relocation as a coupled change to PseudoIR's
  owner, do not relocate silently.
- If `tree-sitter` version specs conflict at install time: flag, do not force-pin.

### U2 — Registry consultation in egress

**What.** Replace each PseudoCoup emitter's inline operator-lowering decisions with
`pseudoir.registry.lookup(op_id, target)` calls, so the registry becomes the single authority.
For each emitter, and for each informal lowering it currently hardcodes, map the lowering to its
registry op and route the decision through `lookup`. Where the registry gives a DIFFERENT (correct)
answer than the current hardcode (the base bugs listed in the survey), adopt the registry answer —
U2 fixes those, it does not preserve them.

The op-to-emitter mapping (this is the survey deliverable that drives the work):

| PseudoCoup informal lowering | Where it lives now | Registry op to consult |
|---|---|---|
| `//` floor-division per target | every emitter's `visit_BinaryOpNode` | (no direct registry op today — see escalation E2a: floor-div is not currently a registry op; either add one in PseudoIR or keep hardcoded and record the gap) |
| `**` power / `%` modulo (unhandled in Go/Kotlin/Rust/C++) | those 4 emitters' `visit_BinaryOpNode` | same gap as `//` — E2a |
| `is`/`is not` (identity/None) | all emitters `visit_BinaryOpNode` | `op.null_coalesce` family covers null-safety; identity-vs-None is adjacent — E2a (may need a new registry op) |
| user-type operator (`a + b` on annotated user types) | NOT modeled in base today | `op.overloaded_binary` — the cleanest fit; `native_operator` vs `method_call` per target |
| `range(...)` / range builtins | `visit_CallNode`, cpp.py `visit_ForNode` string-sniff | `op.range` |
| string formatting / `.format()` sniffing | `visit_AttributeNode`/`visit_CallNode` per emitter | `op.string_interp` |
| spread / variadic call | not cleanly modeled | `op.spread_call` + `decl.variadic` |
| kwargs / named-argument calls | not cleanly modeled | `xform.named_args` |
| destructuring (tuple targets) | not cleanly modeled | `op.destructure` |
| match/when/switch | not modeled | `op.match_expr` |

**Where.** All 12 files under `/home/lucas/Programming/PseudoCoup/pseudocoup/egress/`, primarily
their `visit_BinaryOpNode` and `visit_CallNode` methods (line ranges in the survey table above).
The registry gives per-target answers, so the emitter passes its own target name (e.g. the Dart
emitter passes `"dart"`). Note only 4 targets are in `SUPPORTED_TARGETS` for pseudoir's own
transpiler (`python, typescript, go, dart`), but the REGISTRY columns cover more languages — the
lookup works for any column present; confirm each of PseudoCoup's 12 targets has a column before
relying on it (swift/csharp are `pending` — decision D3).

**Evidence.** 12 emitters, each with an independent `visit_BinaryOpNode` (confirmed byte-level: the
11 non-Dart emitters are identical between base and vendored, so a fix here is a clean single-site
change per emitter). Registry has 12 op/xform ids. Base bugs the registry can fix: `**`/`%` invalid
in 4 emitters, Swift missing `in` + null-guard, Java missing `and`/`or`, PHP `+`-concat — all
sourced in the survey table.

**Acceptance.** For at least the 4 pseudoir-supported targets (python, typescript, go, dart), each
emitter's operator lowering for the ops that HAVE a registry column is produced by a `lookup` call
(no inline hardcode remains for those ops), and a targeted test (U6) confirms the emitted operator
form matches the registry's recorded lowering for a representative operator per target. The
specific known base bugs that fall inside covered ops are fixed (verified by test). Ops with NO
registry column (see E2a) remain hardcoded but are explicitly listed in a "registry gaps" note.

**Escalation triggers.**
- E2a (Dee + PseudoIR owner): several core arithmetic/identity operators PseudoCoup lowers (`//`,
  `**`, `%`, `is`-identity) do NOT have a dedicated registry op today (the registry's 12 ids are
  null-safety / destructure / overloaded-binary / range / spread / interp / match / named-args /
  variadic). Deciding whether to (a) extend the PseudoIR registry with these operators, or (b) keep
  them hardcoded in PseudoCoup and record the gap, is a scope/ownership call. Do NOT extend the
  registry unilaterally.
- If a PseudoCoup target has no registry column at all for an op (swift/csharp pending): see D3.
- Any op-to-emitter mapping that requires a NEW UR-AST node type (user-type operators,
  destructuring, match — none are modeled in base `ur_ast.py` today) is a structure decision → Dee.

### U3 — Hoister unification

**What.** Introduce `pseudoir.hoist()` as PseudoCoup's single expression-position-to-statement
lowering mechanism, replacing the ad-hoc workarounds. Since base PseudoCoup has NO general hoisting,
this is mostly a from-scratch wiring of `pseudoir.hoist` into the emit path (an emitter accumulates
a prelude of hoisted statements and emits them before the statement that needed them), then
migrating the two existing one-off workarounds onto it.

**Where.** The two existing workarounds to migrate:
`/home/lucas/Programming/PseudoCoup/pseudocoup/egress/go.py` `visit_BinaryOpNode` (dict-`in` IIFE,
~lines 262-285) and `/home/lucas/Programming/PseudoCoup/pseudocoup/egress/swift.py`
`visit_TryCatchNode` (shallow `try`-prepend, ~lines 349-369). The new prelude-accumulation
mechanism touches each emitter's statement-emission sites (the block-body emission loops that
already exist in every emitter). Because base emitters return self-contained strings with no
accumulator, this requires a small shared change to how statement bodies are assembled — design it
once, apply per emitter.

**Evidence.** Zero `pending_statements`/accumulator patterns exist in ~5,127 lines of base egress
(survey). Only 2 one-off workarounds. `pseudoir.hoist()` returns a `Hoister` with
`hoist_stmt(stmt_lines, result_expr) -> (temp, result_expr)` appending to `.prelude`. PseudoIR
already proved the mechanism (its R4 double-hoist example: `total = U.coalesce(a,0) + U.coalesce(b,0)`
hoists two temps `_h0`/`_h1` in source order).

**Acceptance.** The go.py dict-`in` case and the swift.py `try` case are both expressed via
`pseudoir.hoist` (no bespoke IIFE / no bespoke shallow heuristic remains). A test (U6) transpiles a
construct requiring hoisting to a target that needs it and confirms the emitted output has the
prelude statement(s) before the use site and a correct temp reference at the use site.

**Escalation triggers.**
- The shared "how a statement body accumulates a prelude" change touches every emitter's structure.
  If the cleanest design introduces a new base class / new shared helper module, that is a structure
  decision → Dee.
- If migrating swift's `try` case reveals it needs deeper hoisting than the shallow heuristic (a
  throwing call nested inside a larger expression), that is a genuine new capability, not a
  refactor — scope it as its own unit and flag, do not silently expand U3.

### U4 — Gate integration (pre-transpile discipline check)

**What.** Wire `pseudoir.gate.check(src_bytes, targets)` into PseudoCoup as a PRE-transpile check
for **Hub-authored source** inputs (Python-notation source using the `U.` namespace + annotated
types — the input shape pseudoir's gate understands). When PseudoCoup is asked to transpile a Hub
source to a target set, run the gate first; on FAIL, surface the report and refuse to emit (matching
`pseudoir.transpile`'s own contract, which raises `GateFailure`). Document clearly how this relates
to the WFL coverage gate.

The two gates check DIFFERENT DIRECTIONS — this is the load-bearing documentation deliverable of
U4, and it must be written into `/home/lucas/Programming/PseudoCoup/.planning/` (a short
`21_two_gates.md` note) and referenced from PseudoCoup's own docs:

- **pseudoir gate** (EGRESS direction, for Hub-source inputs): source is a Hub Python-notation
  file; targets are the output languages; it asks "does every construct in this source have a
  confirmed, non-`fail` realization in EVERY target I named?" It is a pre-EMIT check. Failure means
  a target can't realize a construct.
- **WFL coverage gate** (INGRESS direction, for Kotlin-source inputs): lives in the VENDORED copy
  at `/home/lucas/Programming/WFL_PseudoCoup/pseudocoup/ingress/coverage.py`; it instruments the
  Kotlin PARSER and asks "did we UNDERSTAND every node in the source — was anything dropped or
  silently skipped during ingest?" It is a post-PARSE / pre-anything check on the ingress side.
  Failure means the parser didn't handle a source construct.

They are complementary, not redundant: one guards "we understood the input," the other guards "the
output is realizable." Neither subsumes the other. U4 wires in the pseudoir (egress) gate for Hub
inputs; it does NOT move or modify the WFL coverage gate (that lives in the vendored copy and is
governed by U5's upstreaming decision, D2).

**Where.** PseudoCoup's transpile entry path — `/home/lucas/Programming/PseudoCoup/pseudocoup/cli.py`
(the `main()` dispatch) and/or a new pre-transpile hook. The gate call is
`pseudoir.gate.check(src_bytes, targets)`; the target set is whatever the CLI `--target-lang`
resolves to (note: currently one target per invocation; the gate takes a LIST — decide whether to
pass a singleton list or the full 12). The direction-documentation note goes to
`/home/lucas/Programming/PseudoCoup/.planning/21_two_gates.md`.

**Evidence.** `pseudoir.gate.check` signature and semantics confirmed (survey + `INTEGRATION.md` +
`DISCIPLINE_CHECK.md`). WFL coverage gate confirmed at
`/home/lucas/Programming/WFL_PseudoCoup/pseudocoup/ingress/coverage.py` (82 lines, `CoverageRecorder`
class, hooks in `kotlin.py` `_map_node`/`parse`). The gate only makes sense for Hub-notation input
(Python with `U.` + annotations); PseudoCoup's other 10 ingress languages are NOT Hub notation, so
the gate applies to the Python-Hub ingress path specifically — flag this scoping (E4a).

**Acceptance.** Transpiling a Hub source that the gate should PASS emits normally; transpiling a Hub
source with an unrealizable construct for the chosen target (e.g. an `op.safe_call` targeting a
column with a `fail` cell) refuses to emit and surfaces `pseudoir.gate.format_report` output. The
`21_two_gates.md` note exists and correctly states the two directions. The WFL coverage gate is
untouched.

**Escalation triggers.**
- E4a (Dee): the gate is Hub-notation-specific but PseudoCoup ingests 12 languages. Deciding
  WHICH ingress paths the gate runs on (only Python-Hub? all? off by default with a flag?) is a
  behavior decision → Dee.
- If passing PseudoCoup's full 12-target set to the gate causes spurious FAILs because swift/csharp
  columns are `pending` (not `fail`, but not `runtime-confirmed` either — check whether the gate
  treats `pending` as pass or fail): see D3, and flag.

### U5 — Divergence reconciliation (vendored improvements → base, or declared app-specific)

**What.** Take the classified divergence inventory (in the survey above and reproduced as the
starting table below) and, for each vendored improvement, produce a recommendation
(upstream-to-base vs declare-app-specific) for Dee to ratify (decision D2). This unit's OUTPUT is a
decision-ready classified inventory plus, for the items Dee approves as upstream, the port itself.
This is where the WFL copy's coverage gate, param-shape ledger, enum/object-model handling, UR-AST
schema additions, etc. get either merged into base PseudoCoup or explicitly recorded as
WFL-app-specific.

Starting classification (from the survey; U5 refines and Dee ratifies):

| Vendored improvement | Where | Recommendation (for Dee) |
|---|---|---|
| Coverage gate (`ingress/coverage.py` + `_map_node`/`parse` hooks) | vendored `ingress/coverage.py`, `ingress/kotlin.py` | UPSTREAM — generic, source-language-agnostic; port `coverage.py` and add the ~4-line hook pattern to base ingestors |
| Param-shape ledger (`register_param_shape`, `get_param_shape`, scoped variants) | vendored `core/ledger.py` | UPSTREAM the ledger METHODS (generic schema); DEFER wiring other languages (narrow usage today) |
| Symbol-owner / ambiguous-import ledger infra (`file_map`, `symbol_owners`) | vendored `core/ledger.py` | UPSTREAM — generic multi-file-emit infra, low risk |
| UR-AST additions (`LiteralNode.raw`, `ModifierNode`, `DeclarativeNode`) | vendored `core/ur_ast.py` | UPSTREAM as inert/optional schema — other languages never produce them, zero risk |
| Kotlin enum/object-model INGRESS (`_map_node` branches) | vendored `ingress/kotlin.py` | UPSTREAM — it is the only Kotlin ingestor; portable wholesale |
| Kotlin `when`/elvis/scope-function ingress | vendored `ingress/kotlin.py` | UPSTREAM the Kotlin-generic parts; leave `BUILTIN_RECEIVER_MEMBERS`/Compose-Modifier app-specific |
| Kotlin Compose Modifier-chain extraction | vendored `ingress/kotlin.py` | APP-SPECIFIC (Compose→Flutter only) — declare, do not upstream |
| Dart async/suspend propagation, import-hide, data-class `.copy()` synthesis | vendored `egress/dart.py` | UPSTREAM the generic Kotlin→Dart concerns (import-hide, async-propagation, data-class copy) |
| Dart Compose→Flutter declarative UI + `dart_compose_vocab.py` | vendored `egress/dart.py`, `egress/dart_compose_vocab.py` | APP-SPECIFIC (100% WFL data) — declare, do not upstream |
| WFL driver/baseline (`tools/transpile_wfl.py`, `coverage_baseline.json`, `sync_wfl_src.sh`) | vendored `tools/` (outside package) | APP-SPECIFIC — not upstream candidates |

**Where.** Reading from `/home/lucas/Programming/WFL_PseudoCoup/pseudocoup/` (bash mount works
there) and writing (for approved upstream items) to
`/home/lucas/Programming/PseudoCoup/pseudocoup/`. The classified inventory note goes to
`/home/lucas/Programming/PseudoCoup/.planning/22_divergence_inventory.md`.

**Evidence.** Byte-level diff confirms divergence is scoped to 4 files + 2 new files (survey table).
Every other file is identical, so upstreaming a generic item (e.g. the coverage gate) into base
does not collide with base's other emitters. Line deltas: `ledger.py` +244, `ur_ast.py` +18,
`kotlin.py` +1377, `dart.py` +3151.

**Acceptance.** `22_divergence_inventory.md` exists with every vendored improvement classified and a
recommendation. For each item Dee ratifies as UPSTREAM, the port lands in base PseudoCoup and the
base's other-language emitters still produce identical output (verified by U6's round-trip on the
untouched languages). For each item Dee ratifies as APP-SPECIFIC, it is recorded as such (a note in
the inventory) and NOT copied into base. The vendored copy is not modified by this unit (base is the
target of upstreaming; the vendored copy stays as-is unless Dee says otherwise).

**Escalation triggers.**
- D2 (Dee): the upstream/app-specific split for EACH item is Dee's ratification. The table above is
  a recommendation, not a decision. Present it; do not port anything Dee has not approved.
- Any upstream port that changes base behavior for a language other than the one it came from
  (e.g. adding coverage hooks to all 11 ingestors) is a behavior change across languages → confirm
  scope with Dee before touching more than Kotlin.
- If upstreaming an item requires the param-shape ledger or symbol-owner infra as a prerequisite
  (dependency between items), sequence them and flag the coupling.

### U6 — Verification

**What.** Establish the regression net this integration needs (base PseudoCoup currently has none)
and prove the integration works end-to-end. Three layers: (1) PseudoCoup's own round-trip tests —
first REPAIR the broken `run_tests.sh` (it references nonexistent `examples/quickfox.py`) or replace
it with a real pytest harness; (2) pseudoir's 17-test suite must still pass (run in its own repo);
(3) a NEW cross-integration round-trip: a Hub source transpiled via PseudoCoup-consulting-pseudoir,
with the emitted operator forms checked against the registry's recorded lowerings, and (for the
pseudoir-runnable targets python/typescript) executed and compared against the CPython oracle.

**Where.** `/home/lucas/Programming/PseudoCoup/run_tests.sh` (repair or replace); a new test
location under `/home/lucas/Programming/PseudoCoup/tests/` (real pytest, since none exists today);
pseudoir's suite runs at `/home/lucas/Programming/PseudoIR/v2/pseudoir` via `python -m pytest`.

**Evidence.** Base has zero pytest tests (survey), a broken `run_tests.sh`, a stale broken
`emitted_fox/08_c.c`. pseudoir has exactly 17 passing tests (verified nodeids). pseudoir's suite is
NOT self-contained to its subpackage (reaches `v2/` siblings) — so run it from its own repo root,
do not assume it runs from PseudoCoup (relevant if D1 chose vendoring). pseudoir round-trip already
proves python+typescript byte-match the CPython oracle for a program using U-ops/kwargs/destructure/
Vector2-operators/range/interp/match.

**Acceptance.** (1) `run_tests.sh` (or its replacement) runs green — no reference to nonexistent
files, produces a pass/fail signal. (2) `cd /home/lucas/Programming/PseudoIR/v2/pseudoir &&
python -m pytest` = 17 passing (unchanged by this upgrade — pseudoir is imported, not modified). (3)
The new cross-integration round-trip: at least one Hub program transpiled through
PseudoCoup-with-pseudoir to python and typescript, both executed, both matching the CPython oracle;
and for a representative operator per pseudoir-supported target, the emitted form equals the
registry's recorded lowering (proves U2 actually consults the registry rather than a stale
hardcode). (4) The 11 base language emitters not touched by upstreaming (U5) still produce identical
output to pre-upgrade (regression check).

**Escalation triggers.**
- Repairing vs replacing `run_tests.sh` — if the cleanest fix is a full pytest rewrite (new test
  structure/files), that is new structure → confirm approach with Dee (small if it's a
  path-fix; big if it's a new harness).
- If the cross-integration round-trip surfaces a registry column that PseudoCoup needs but pseudoir
  has as `pending` (swift/csharp): see D3.
- Never fake a runtime confirmation; `pending`/skipped is an honest status (per the PseudoIR
  standing rule). If a target can't be executed in-sandbox, record it as emitted-but-unconfirmed,
  do not claim a pass.

---

## Decision queue — ALL DECIDED (Dee, 2026-07-14)

Executors: these are settled. Do not re-open them or re-present them as questions. Standing norm
from Dee, added to the delegation rules: when a question has a natural answer, DECIDE it, record
the decision and rationale in the relevant doc, and move on — escalate only genuine forks (where
two options have materially different, hard-to-reverse consequences and no evident winner).

- **D5 — DECIDED: add the new UR-AST node types.** Relaxing the discipline is the point of this
  upgrade; without representation there is nothing to look up. Add nodes for the registry-covered
  constructs U2 routes (destructure, match-expr, user-type operators; null-ops/range/spread/interp
  where not already representable). An upgrade limited to already-representable constructs would be
  cleanup, not relaxation — explicitly rejected.
- **D4 — DECIDED: extend the PseudoIR registry** with `**`, `//`, `%`, and `is`-identity (a
  PseudoIR-side work item feeding this upgrade). These are registry-shaped problems: per-language
  spellings (`**` -> `Math.pow`/`math.Pow`/`.pow()`) and genuine semantic forks (`//` floor-vs-
  truncating division on negatives, `%` sign conventions — vector material exactly like the falsy
  trap). Fixing them hardcoded in 12 emitters would repeat the pattern the registry exists to kill.
- **D1 — DECIDED: path/editable dependency (Option A), no vendored copy.** One painful
  copy-relationship (WFL's vendored pseudocoup) is enough; the sibling-folder requirement is
  acceptable for this development setup. Coordinated sub-decision, also approved: relocate the
  `pseudoir` package from `PseudoIR/v2/pseudoir/` to the PseudoIR repo root as part of U1, fixing
  the package's own test paths in the same change (the tests' reach into `v2/` siblings gets
  corrected then — this is the sanctioned moment for that cleanup).
- **D3 — DECIDED: option (b) — swift/csharp keep their existing hardcoded lowerings** until their
  registry columns are runtime-confirmed; do not route them through the registry on pending status.
  The gate treats `pending` as PASS-WITH-WARNING for these two targets only (recorded, visible,
  non-blocking). Confirmation happens on demand: csharp when a dotnet toolchain is convenient;
  swift only if it ever becomes a real target (standing stance: not catering to Apple).
- **D2 — DECIDED: the U5 inventory's recommended classification is ratified as-is** (generic items
  upstream: coverage gate, ledger schema, symbol-owner infra, UR-AST additions, Kotlin enum/object-
  model ingress; app-specific stay: Compose Modifier-chain handling, dart_compose_vocab.py, the WFL
  driver). One binding constraint: upstreaming is copy-forward, never move — the WFL vendored copy
  must remain untouched and working until that project's own phases complete in its own branch.
  Any inventory row discovered later that doesn't clearly fit the classification rule (framework-
  agnostic = upstream, Compose/WFL-shaped = app-specific) is a genuine fork: escalate that row only.

---

## Dispatch plan

- **U1** lands first, solo. Blocks U2/U3/U4. Small once D1 is decided.
- **U5** runs in PARALLEL from the start (survey-and-classify; its code output is gated on D2 but
  its inventory note is not). It touches the vendored copy's reading and base's writing — no overlap
  with U1-U4's files except where an upstreamed generic item (coverage gate, ledger) later
  interacts with U2/U4; sequence those interactions (coverage-gate upstream before U4's
  two-gates documentation is finalized).
- **U2** and **U3** run after U1, may parallelize, but for any op that needs hoisting, U3's shared
  prelude mechanism must be scaffolded before that op's U2 emitter work. Dispatch U3's mechanism
  first, then U2 per-emitter in parallel.
- **U4** runs after U1, independent of U2/U3, but its `21_two_gates.md` note should be reconciled
  with U5's coverage-gate upstreaming decision (D2) so the doc describes the final state.
- **U6** runs last (needs U1-U4 landed and U5's decision), but its FIRST sub-task — repairing
  `run_tests.sh` and standing up a pytest harness — can start immediately in parallel, since base
  PseudoCoup has no test net at all and everything else depends on having one.

Per the delegation hierarchy (below): an Opus sub-agent owns each unit, breaks it into concrete work
items, and dispatches those to Sonnet sub-agents for the code edits / transpile runs / greps /
tests. Each unit ends with its Acceptance check re-run before being reported complete.

## Out of scope (this upgrade)

- SUPERSEDED (2026-07-14, by Dee's D1/D4 decisions — this bullet previously forbade modifying
  `pseudoir`; that ban is LIFTED for exactly two sanctioned items and executors must not refuse
  them): (a) D1 relocation — moving the `pseudoir` package from `PseudoIR/v2/pseudoir/` to the
  PseudoIR repo root, fixing its own test paths in the same change, done as part of U1; (b) D4
  registry extension — adding `**`, `//`, `%`, and `is`-identity ops to the PseudoIR registry with
  vectors and per-language columns, following the established prober pattern (harvest spellings,
  execute vectors on available runtimes, honest pending elsewhere). All OTHER pseudoir
  modifications remain out of scope (notably: flipping swift/csharp pending columns — D3 keeps
  those hardcoded until confirmed; new op families beyond D4's four; U-API surface changes).
- Modifying the WFL vendored copy (`/home/lucas/Programming/WFL_PseudoCoup/pseudocoup/`). U5
  upstreams FROM it INTO base; it does not edit the vendored copy. The vendored copy's own
  WFL-specific pieces (Compose vocab, transpile driver) stay where they are.
- Building the Compose→Flutter declarative-UI path into base PseudoCoup — that is declared
  app-specific in U5.
- Adding new source languages or new target languages to PseudoCoup.
- Fixing every latent base emitter bug. U2 fixes the operator bugs that fall inside a registry op's
  coverage as a byproduct of consulting the registry; bugs outside any registry op (e.g. dead
  `} else {` in kotlin.py, the `sugared_args` dead code, main-guard vanishing in go.py) are noted
  but not this upgrade's job.
- A general Hub authoring surface for PseudoCoup. The gate (U4) applies to Hub-notation input;
  turning PseudoCoup into a full Hub-authoring tool is not in scope.

## Standing rules

- **Delegation hierarchy** (from `/home/lucas/Programming/WFL_PseudoCoup/.planning/AGENT_DELEGATION.md`,
  applies here by reference): Dee (human principal, ultimate decision + escalation endpoint) →
  top-level agent (high-level triage/ordering/architecture/review/planning updates only, no heavy
  lifting inline) → Opus sub-agents (own one unit each, break into work items, verify before
  reporting up) → Sonnet sub-agents (the heavy lifting: code edits, transpile/test runs, greps).
  Decisions that introduce new names, files, abstractions, or structure go UP the chain (ultimately
  to Dee), never invented downward. Each unit ends with a verification step before being reported
  complete.
- **Communication protocol** (from `/home/lucas/Programming/WFL_PseudoCoup/.DevComms/LLM_communication_protocol.md`,
  binding on every executor and every report/planning doc): tabular data goes in markdown pipe
  tables or prose — NEVER whitespace-aligned code blocks (the ban is explicit and applies to chat,
  planning docs, reports, and sub-agent output alike). Code blocks are for actual code and bordered
  text diagrams only. Claims about code carry evidence (actual lines/output/error, not paraphrase);
  unverified-this-session claims are marked "unverified." Report problems grouped by root cause with
  a per-item status (open/fixed-where/historical), not by individual sighting. Define load-bearing
  terms once (glossary format). Answer the question asked; no unrequested alternatives.
- **Honest status**: never fake a runtime confirmation. `pending`/skipped/emitted-but-unconfirmed
  are honest statuses (per PseudoIR's standing rules). This applies to any swift/csharp work under
  D3 and to any in-sandbox execution limits in U6.
- **No silent structural choices, but no re-litigating settled ones either**: any NEW file, name,
  abstraction, or cross-repo relationship not already covered by the decision queue is escalated.
  D1-D5 are DECIDED (see the decision queue) — executors act on them without re-asking. Dee's
  standing norm applies: questions with natural answers get decided and recorded by the executor;
  only genuine forks (materially different, hard-to-reverse, no evident winner) go up.

## Document map (this directory)

- `00_Upgrade_Plan.md` — this file (mission, survey, U1-U6, decisions, dispatch, rules).
- `20_PseudoIR_X1_supersession_note.md` — records that this plan realizes PseudoIR's X1; mirror of
  the X1 stub update in `/home/lucas/Programming/PseudoIR/v2/PLAN.md`.
- `21_two_gates.md` — (to be authored in U4) the pseudoir-egress-gate vs WFL-ingress-coverage-gate
  direction documentation.
- `22_divergence_inventory.md` — (to be authored in U5) the classified base-vs-vendored divergence
  inventory with per-item upstream/app-specific recommendations for Dee.
