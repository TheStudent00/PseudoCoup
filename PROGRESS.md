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

## The one goal now — complete the transpiler

We work on this and nothing else until the foundation is solid. The transpiler is checked by three
gates, each stricter than the last:

```
gate    what it proves                                           command                result
parse   every file becomes Python with no syntax errors          build_mixingcenter.py  254 / 254
load    the non-UI foundation actually loads under kotlin_rt      loadcheck.py           163 / 167
logic   tested components compute the same answers as Kotlin      oracle.py              11 / 11  (160 methods)
```

The **load** gate, added this pass, caught two real bugs that parsing alone had hidden — both because
the affected code wasn't being emitted at all: a companion-object property whose value is an anonymous
object dropped the lifted class (`MIGRATION_1_2 = _Obj1(1, 2)` with no `class _Obj1`), and Kotlin raw
`"""…"""` strings spanning lines were emitted with a single `"`. Both fixed.

The 4 files the load gate still blocks are stopped by **external platform names** the foundation calls —
a Room `Migration`, a Java `SimpleDateFormat`, and two Compose names (`Icons`, `hiltViewModel`) — not by
any transpiler defect. Supplying those names is the runtime-support layer; the Compose ones belong with
the UI, a later phase.

Earlier construct work this stretch: the `by` delegate; a trailing lambda after a named argument;
`when`/standalone `is Type` → `isinstance`; `if`/`when` as a value (hoisted to a temp); hex literals
keeping `F`/`f` digits; `a?.b = v` → a guarded assignment; anonymous objects → a hoisted class + instance.

## The plan, in order

1. **Complete the transpiler** → the foundation (`WFL_MixingCenter`) is solid. ← we are here
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
