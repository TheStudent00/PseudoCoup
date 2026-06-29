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

We work on this and nothing else until the foundation is solid.

**231 / 254** parse-clean (242 of 254 produce Python). We clear the transpiler one Kotlin construct
at a time.

- **DONE — the `by` delegate.** `val/var x by remember/collectAsState/lazy` at the top of a
  `@Composable` now transpiles: `x = D`, with reads/writes of `x` going through `x.value`.
- **DONE — trailing lambda after a named argument.** `Box(x, contentAlignment=Y) { content }` now
  emits `Box(x, contentAlignment=Y, content=lambda)`. `content=` is a convention (correct for most
  Compose slots; a wrong one fails loudly, never silently, and gets the real name when callee
  signatures land). Moved ~35 files to parse-clean (196 → 231).
- **REMAINING — 23 of 254:** 12 transpiler errors (`no handler`: an `object_literal` in
  `WorkoutDatabase`, a `type_test` in `DebugPanelViewModel`) + 11 emitted-invalid (9 plain syntax,
  1 hex literal).

Parse-clean is not the same as runnable; runnability is a later check. The metric now is: does every
Kotlin construct in the copy transpile. Regenerate with `python3 tools/pseudokotlin/build_mixingcenter.py`.

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
