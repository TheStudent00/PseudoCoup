# WFL → Python — project dashboard

What the project is, the one goal now, and where it stands. (Browser version: `PROGRESS.html`.)

Updated 2026-06-29 — numeric-fidelity wrappers now emit at literals *and* declared-type boundaries; all
five gates green. Narrative detail lives in `DevComms/` logs.

## What the project is

```
WFL  (the original Kotlin app)              upstream ~/Programming/WFL — untouched source of truth
  │
  │   copied, then edited to "meet the transpiler in the middle"
  ▼
WFL_MixingCenter/WFL/  (the Kotlin copy)    edits kept honest by WFL's own tests
  │
  │   KtToPy  — the advanced transpiler  (lives in PseudoCoup/tools/pseudokotlin)
  ▼
WFL_MixingCenter/*.py  (THE FOUNDATION)     the 1:1 Python the transpiler produces
```

- **foundation** = the 1:1 Python KtToPy produces from the Kotlin copy (`WFL_MixingCenter/*.py`).
  Everything else is built on it.
- It carries the transpiler's framework: the 1:1s, wrappers, ledger, tags, structure, connectivity.
- Nothing in it exists without a Kotlin source.

## How the transpiler is built (the architecture)

A transpiler is a compiler whose output is source code. The spine is a pipeline; each stage hands the next
a *richer* version of the program, under one rule: **resolve before you translate** — never emit a name
until you know what it refers to.

```
Kotlin source
   │  1. parse                       tree-sitter — done
   ▼
syntax tree           shape only: `SimpleDateFormat(p)` is "a call", meaning unknown
   │  2. resolve   ← imports + scopes + declarations
   ▼
resolved tree         every name tagged: local | member | app class | EXTERNAL + origin
   │  3. map       ← wrapper registry keyed by origin
   ▼
Python model          java.text.SimpleDateFormat  →  runtime/java_text.py : SimpleDateFormat
   │  4. generate     emit imports + code
   ▼
Python source   +   runtime library (wrappers organized by origin)
```

- **resolve** — the phase that was missing. An import binds a bare name, in that file, to its external
  symbol (`import java.text.SimpleDateFormat` → the name `SimpleDateFormat` means `java.text.SimpleDateFormat`;
  Kotlin's default imports are the same, implicit). After it, every name is classified and the full external
  set is a printable fact, not a runtime surprise.
- **registry** — maps a fully-qualified name → the Python wrapper standing in for it. A missing wrapper is a
  build-time gap you list, never a `NameError` at runtime.
- **map / wrap / fail** — map an app construct · wrap a resolved external to its registry wrapper · fail
  loudly on a resolved external with no wrapper.
- Net: runtime whack-a-mole becomes a checklist — the 367 external names the imports declare, each routed by
  origin. The construct handlers and the oracle bolt onto `map`.

> **Related (PseudoCoup):** this import-inferred external→wrapper mapping is the *inference-side* counterpart
> to PseudoCoup's *explicit* `@<lang>_extern` tag (`@haxe_extern` in `discipline.py`). For the multi-target
> vision they converge: one `@<target>_extern` tag could drive this same per-language registry, so an
> external is declared once and resolved per target. (PseudoCoup-side; not WFL→Python work right now.)

## The one goal now — complete the transpiler

Work this and nothing else until the foundation is solid. The transpiler runs the full pipeline — parse →
resolve → map → generate(+imports) — checked by five gates:

```
gate     what it proves                                       command                result
parse    every file becomes Python, no syntax errors          build_mixingcenter.py  254 / 254
load     the non-UI domain loads under the runtime            loadcheck.py           165 / 165
extern   every external name the foundation USES is wrapped   externals.py           0 real gaps
logic    tested ENGINES match Kotlin's answers                oracle.py              11 / 11  (160 methods)
data     the DATA LAYER runs the project's DAO/txn tests      datalayer_oracle.py    2 / 2
```

**load ≠ run** — the finding that drove the resolve pass:
- `load` (165/165) proves the modules *load* — it misses names used inside method bodies.
- `resolve` + `externals.py` cross-check imports against the registry: a deterministic checklist. It found
  **65 names** `load` never surfaced — coroutines `Flow`/`StateFlow`/`combine`, java `Instant`/`UUID`/`File`,
  android `Context`/`Log`.
- All covered: real wrappers where Python has an equal (a synchronous `coroutines` Flow/StateFlow, `java_rt`,
  `json_rt`), honest stubs where it doesn't (`android_rt`). **0 real non-UI gaps.**
- `generate` emits them: **106 files carry `from runtime.<wrapper> import <name>`**.

**numeric fidelity** — wrap the semantics Python's built-ins silently drop (`runtime/numbers.py`):
- Kotlin `Int`/`Long`/`Float` → fixed-width wrappers (`Int32`/`Int64`/`Float32`): two's-complement overflow,
  32-bit float rounding, truncating integer `/`, and `Int < Long < Float < Double` promotion.
- Emitted at **both** ends: at literals (by suffix) **and** at declared-type boundaries (params, constructor
  fields, typed `val`s) — so a chain that never touches a literal (e.g. a value straight off a DAO) still
  carries the width.
- `Double` stays bare `float` (faithful). Wrappers subclass `int`/`float`, so `isinstance`, indexing, and
  `str`/format come for free; only arithmetic is overridden.
- Fidelity-first, behind a dial: wrap by default, bare-emit/unwrap later where a context proves it safe.

**Two deeper truths the checklist exposed:**
- **The data layer RUNS** — not stubbed.
  - Room generates a `@Dao`'s query bodies *at compile time* — they aren't in the source. That looked like a wall.
  - But `@Query` strings are real SQLite SQL and Python ships `sqlite3` → faithfully implementable. Built
    `runtime/room.py` (sqlite3-backed, entity↔row converters) + `datalayer.py` (`@Entity`→table schema,
    `@Dao`→real query bodies, `@Database`→a `WorkoutDatabase` that registers entities and wires DAO accessors).
  - Verified by the project's OWN instrumented tests, run as written headless: **ExerciseDaoMuscleGroupTest**
    (queries, converters, raw-SQL boundary) and **GymRepositoryTransactionTest** (`withTransaction` rollback)
    — both green.
  - The 2 remaining instrumented tests are blocked *above* the data layer: `BackupRepositoryRoundTripTest`
    (the backup feature + a stale ctor arg in the copy), `MigrationTest` (needs Room's `MigrationTestHelper`).
- **Platform glue is off-device** — Activities, notifications, Firebase, WorkManager are stubbed to resolve
  names, not to run. When a piece must run, lift that logic into the domain layer.

## The plan, in order

1. **Complete the transpiler** → the foundation (`WFL_MixingCenter`) is solid. ← we are here
   - 1a. Construct translation (the `map` stage) — **done**: 254/254 parse, 165/165 non-UI load, oracle 11/11.
   - 1b. The `resolve` phase — import table + scopes + a project symbol table — **done**.
   - 1c. Wrapper registry + the build-time external checklist (replaces the runtime load-gate hunt) — **done**.
   - 1d. Emit imports in the generated Python (externals from their origin wrapper, app classes from their path) — **done**.
   - 1e. Numeric fidelity — fixed-width wrappers at literals + declared types — **done**.
2. **Evaluate set-aside parts.** Bring a part (e.g. a UI screen) into the foundation only after rigorous
   validation that it keeps structure/connectivity. If a part is invalid or mangled, don't fix it —
   **paint-by-numbers** a fresh one (or mechanize it when the part-type allows).
3. **Upgrade the UI to PseudoUI discipline.** A salvaged part that is already valid Python, passes the ledger
   validation, and carries the discipline gets used — extra discipline is not a reason to ignore it.

## Set aside (not failed — parked, picked up later only if it validates)

- `WFL_PseudoCoup` — an earlier hand-built effort (the pre-rigor "trusted baseline" idea that got cratered).
  Its hand-built code is untrusted until validated against the foundation.
- The PseudoUI generator + swap-in work done in `WFL_PseudoCoup` in prior conversations. The generator *tool*
  may be reused for "paint-by-numbers a screen fresh," but only aimed at the foundation.
- The transpiler fixes made along the way (e.g. `expr ?: continue`) are **not** set aside — they live in
  `tools/pseudokotlin` and improve KtToPy directly.

## Glossary (your terms, anchored)

- **foundation** — the 1:1 Python KtToPy produces from the Kotlin copy, `WFL_MixingCenter/*.py`.
  e.g. `data/repository/GymRepository.py`, transpiled from the matching `.kt`.
- **meet the transpiler in the middle** — editing the Kotlin copy (`WFL_MixingCenter/WFL/`) so the transpiler
  can handle it, verified by WFL's own tests. e.g. the `SampleProgramData` change.
- **complete the transpiler** — KtToPy handles every Kotlin construct in the copy, so all 254 files transpile
  and the gaps (like the `by`-delegate error) are gone.
- **fixed-width wrapper** — a Python `int`/`float` subclass that re-applies a Kotlin numeric semantic Python
  drops. e.g. `Int32` in `runtime/numbers.py` — overflow wraps two's-complement.
- **set aside** — parked, out of scope now, picked up later only if it validates. Not discarded.
- **paint-by-numbers** — build a fresh part by hand following the foundation's structure, when a set-aside
  part is too mangled to validate.
- **ledger / structure / connectivity** — the accounting that proves each Python object traces to its Kotlin
  source and is wired the same way; used to validate a swap-in.
- **PseudoUI discipline** — the constrained Python style the UI should follow; applied later, after the
  foundation is solid.
