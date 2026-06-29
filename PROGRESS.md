# WFL → Python — project dashboard

What the project is, the one goal now, and where it stands. (Browser version: `PROGRESS.html`.)

Updated 2026-06-29, after building the resolve phase + wrapper registry and emitting real imports.

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

The **foundation** is the 1:1 Python KtToPy produces from the Kotlin copy. It is the thing everything
else is built on. It is meant to carry the framework the transpiler system provides — the 1:1s,
wrappers, ledger, tags, structure, connectivity. Nothing in it exists without a Kotlin source.

## How the transpiler is built (the architecture)

A transpiler is a compiler whose output is source code. The spine is a pipeline where each stage hands
the next a *richer* version of the program, under one rule: **resolve before you translate** — never emit
a name until you know what it refers to.

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

- **resolve** is the phase that was missing. `import java.text.SimpleDateFormat` binds the bare name
  `SimpleDateFormat`, in that file, to the external symbol `java.text.SimpleDateFormat`. Kotlin's default
  imports (`kotlin.collections.*`, `java.lang.*`) are the same, implicit. After this pass every name is
  classified, and the full external-dependency set is a printable fact — not a runtime surprise.
- **registry** maps a fully-qualified name to the Python wrapper that stands in for it. The import gives
  the key; the registry gives the target. A missing wrapper is a BUILD-TIME gap you can list, never a
  `NameError` tripped over at runtime.
- **map / wrap / fail** (the existing instinct) becomes precise: map an app construct, wrap a *resolved*
  external to its registry wrapper, fail loudly on a resolved external with no wrapper.

This replaces runtime whack-a-mole with a checklist — the 367 external names the imports already declare,
each routed to a wrapper by its origin package. **The construct handlers and the oracle keep working; they
bolt onto the `map` stage.** What was missing sits between `parse` and `map`, and building it is the work.

> **Related (PseudoCoup):** this import-inferred external→wrapper mapping is the *inference-side* counterpart
> to PseudoCoup's *explicit* `@<lang>_extern` tag — `@haxe_extern` (and a `dart_extern` stub) in
> `discipline.py`, which marks a non-portable binding that needs a wrapper. For the multi-target vision they
> converge: an explicit `@<target>_extern` tag could drive this same per-language wrapper registry, so an
> external is declared once and resolved per target. (PseudoCoup-side; not WFL→Python work right now.)

## The one goal now — complete the transpiler

We work on this and nothing else until the foundation is solid. The transpiler now runs the full pipeline
— parse → resolve → map → generate(+imports) — checked by four gates:

```
gate     what it proves                                       command                result
parse    every file becomes Python, no syntax errors          build_mixingcenter.py  254 / 254
load     the non-UI domain loads under the runtime            loadcheck.py           165 / 165
extern   every external name the foundation USES is wrapped   externals.py           0 real gaps
logic    tested ENGINES match Kotlin's answers                oracle.py              11 / 11  (160 methods)
data     the DATA LAYER runs the project's own DAO/txn tests  datalayer_oracle.py    2 / 2
```

**load ≠ run — the finding that drove this pass.** `load` (165/165) only proves the modules *load*; it
misses names used inside method bodies. The new `resolve` phase reads every file's imports — they name
exactly where each external symbol comes from — and `externals.py` cross-checks them against the registry:
a deterministic checklist that replaces the old run-and-watch-it-fail hunt. It found **65 real external
names** `load` never surfaced (coroutines `Flow`/`StateFlow`/`combine`, java `Instant`/`UUID`/`File`,
android `Context`/`Log`, …). All are now covered — real wrappers where Python has an equivalent (a
synchronous `coroutines` Flow/StateFlow, `java_rt` time/UUID, `json_rt`), honest stubs where it doesn't
(`android_rt`, off-device platform glue). 0 real non-UI gaps. And `generate` now emits the imports: **106
foundation files carry `from runtime.<wrapper> import <name>`** — a use of an external module maps to the
module that wraps it, in the code itself.

**Two deeper truths the checklist exposed:**
- **The data layer — now RUNS, end to end.** The reactive flows are fed by Room DAOs whose query bodies Room
  *generates at compile time* — not in the Kotlin source. That looked like a wall. But Room's `@Query` strings
  are real SQLite SQL, and Python ships `sqlite3` — so the data layer is *faithfully* implementable, not
  stubbed. Built: `runtime/room.py` (a sqlite3-backed Room — entity↔row converters, the `Room` builder) and
  `datalayer.py` (the transpiler turns `@Entity`→a table schema, `@Dao`'s `@Query`/`@Insert`/`@Update`/`@Delete`
  →real bodies, and `@Database`→a `WorkoutDatabase` that registers every entity and wires the DAO accessors).
  Verified by the project's OWN instrumented tests, run AS WRITTEN headless (`datalayer_oracle.py`, a
  data-layer twin of the engine oracle pointed at `androidTest`): **ExerciseDaoMuscleGroupTest** (queries,
  converters, the raw-SQL `openHelper` whole-token boundary guard) and **GymRepositoryTransactionTest**
  (`withTransaction` rolls back a failed write) — both green. The two other instrumented tests are blocked
  not by the data layer but by higher-level surfaces: `BackupRepositoryRoundTripTest` exercises the backup
  *feature* (a column-introspective JSON dump/restore engine, a Cursor API, `clearAllTables`, `runCatching`)
  and also has a stale constructor arg in the copy; `MigrationTest` needs Room's `MigrationTestHelper`
  (schema-version testing infrastructure). (`runCatching` and other default-import stdlib names are a known
  gap class the `extern` checklist doesn't track — it lists explicit imports; `kotlin_rt` grows them as
  surfaced.)
- **Platform glue.** Activities, notifications, Firebase, WorkManager are off-device by nature — stubbed to
  resolve names, not to run. When a piece must run (e.g. notification content built from domain data), lift
  that logic into the domain layer where it's testable.

## The plan, in order

1. **Complete the transpiler** → the foundation (`WFL_MixingCenter`) is solid. ← we are here
   1a. Construct translation (the `map` stage) — **done**: 254/254 parse, 165/165 non-UI load, oracle 11/11.
   1b. **Build the `resolve` phase** — the import table + scopes + a project symbol table, so every name is
       classified (local / member / app class / external + origin) before it is translated.
   1c. **Wrapper registry keyed by fully-qualified name**, and the build-time external-reference checklist
       that lists every external use and whether a wrapper covers it (replaces the runtime load-gate hunt).
   1d. **Emit imports in the generated Python** — external uses import from their origin wrapper module,
       app classes from their module path. Files become real modules, not a flat namespace.
2. **Evaluate set-aside parts.** Bring a part (e.g. a UI screen) into the foundation only after rigorous
   validation that it keeps structure/connectivity. If a part is invalid or mangled, don't fix it —
   **paint-by-numbers** a fresh one (or mechanize it when the part-type allows).
3. **Upgrade the UI to PseudoUI discipline.** A salvaged part that is already valid Python, passes the
   ledger validation, and carries the discipline gets used — extra discipline is not a reason to ignore it.

## Set aside (not failed — parked, picked up later only if it validates)

- `WFL_PseudoCoup` — an earlier hand-built effort (the pre-rigor "trusted baseline" idea that got
  cratered). Its hand-built code is untrusted until validated against the foundation.
- The PseudoUI generator + swap-in work done in `WFL_PseudoCoup` in prior conversations. The generator
  *tool* may be reused later for "paint-by-numbers a screen fresh," but only aimed at the foundation,
  not at matching `WFL_PseudoCoup`.
- The transpiler fixes made along the way (e.g. `expr ?: continue`) are **not** set aside — they live in
  `tools/pseudokotlin` and improve KtToPy directly.

## Glossary (your terms, anchored)

- **foundation** — the 1:1 Python KtToPy produces from the Kotlin copy, `WFL_MixingCenter/*.py`.
  e.g. `data/repository/GymRepository.py`, transpiled from the matching `.kt`.
- **meet the transpiler in the middle** — editing the Kotlin copy (`WFL_MixingCenter/WFL/`) so the
  transpiler can handle it, verified by WFL's own tests. e.g. the `SampleProgramData` change.
- **complete the transpiler** — KtToPy handles every Kotlin construct in the copy, so all 254 files
  transpile and the gaps (like the `by`-delegate error) are gone.
- **set aside** — parked, out of scope now, picked up later only if it validates. Not discarded.
- **paint-by-numbers** — build a fresh part by hand following the foundation's structure, when a
  set-aside part is too mangled to validate.
- **ledger / structure / connectivity** — the accounting that proves each Python object traces to its
  Kotlin source and is wired the same way; used to validate a swap-in.
- **PseudoUI discipline** — the constrained Python style the UI should follow; applied later, after the
  foundation is solid.
