# WFL → Python — project dashboard

What the project is, the one goal now, and where it stands. (Browser version: `PROGRESS.html`.)

Updated 2026-06-29, after regenerating the foundation with the advanced transpiler.

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

## The one goal now — complete the transpiler

We work on this and nothing else until the foundation is solid. The transpiler is checked by three
gates, each stricter than the last:

```
gate    what it proves                                           command                result
parse   every file becomes Python with no syntax errors          build_mixingcenter.py  254 / 254
load    the non-UI domain loads under the runtime                 loadcheck.py           165 / 165
logic   tested components compute the same answers as Kotlin      oracle.py              11 / 11  (160 methods)
```

The **load** gate, added this pass, caught two real bugs that parsing alone had hidden — both because
the affected code wasn't being emitted at all: a companion-object property whose value is an anonymous
object dropped the lifted class (`MIGRATION_1_2 = _Obj1(1, 2)` with no `class _Obj1`), and Kotlin raw
`"""…"""` strings spanning lines were emitted with a single `"`. Both fixed.

The whole non-UI domain now loads. The names the load gate surfaced were added to `kotlin_rt` (which
already held `java.lang.Math`, the Java collections, and JUnit — so it's the catch-all bare-name runtime,
not "Kotlin stdlib only"; a separate file for a handful of names would have been premature structure):
`Date`/`Locale`/`SimpleDateFormat` (the last a real wrapper — pattern → strftime), `ArrayDeque` (a
functional deque), `Any` (a lock object), and a documented `Migration` stub (no Python Room). The only
non-loaders are Compose UI — the `ui/` screens plus two nav-orchestration files (the NavHost and the
bottom bar) — which defer with the UI phase. Splitting the runtime by origin (and renaming `kotlin_rt`)
is deferred until that phase makes it earn its keep.

Earlier construct work this stretch: the `by` delegate; a trailing lambda after a named argument;
`when`/standalone `is Type` → `isinstance`; `if`/`when` as a value (hoisted to a temp); hex literals
keeping `F`/`f` digits; `a?.b = v` → a guarded assignment; anonymous objects → a hoisted class + instance.

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
