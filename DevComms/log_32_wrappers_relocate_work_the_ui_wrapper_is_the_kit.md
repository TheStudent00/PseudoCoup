# log_32 — the wrapper idea is right; it relocates work, doesn't delete it (and the UI wrapper already exists: it's the kit)

Date: 2026-06-25
Type: reframe. Answers: *"for the things that don't map to Python, why not write wrappers that
absorb them, hand-wire the wrappers once, and let the transpile preserve structure so it doesn't
feel a difference?"*

## The instinct is correct — this is the standard technique

Shim/runtime-library transpilation is exactly how real cross-compilers bridge a runtime gap:
Kotlin/JS ships `kotlin-stdlib.js`, J2ObjC ships a JRE emulation lib, GWT/TeaVM/Emscripten all ship
a runtime the emitted code calls into. "Absorb the un-mappable constructs behind wrappers, emit calls
against them, preserve source structure" is the right architecture, not a naive one. log_31 was too
gloomy by treating Tier 2/3 as walls rather than as wrapper targets.

## The one correction: a wrapper RELOCATES the hard work, it doesn't delete it

A wrapper absorbs the **syntax** (so the transpiled code reads like the Kotlin — structure preserved).
But the wrapper's **body** still has to do the real thing. Two outcomes:

- where the behavior has an **automatic source**, the wrapper is a pure win;
- where it **doesn't**, the wrapper just moves the same hand-work *inside itself*.

Per tier (counts from log_31, real WFL):

| layer | wrapper viable? | why |
|---|---|---|
| **Tier 2 — Flow/coroutines** (348 suspend, 125 StateFlow, 35 combine, 49 stateIn, 20 flatMapLatest) | **YES — genuine win** | build once on `asyncio` (`suspend`→`async def`, `launch`→`create_task`, `collect`→`async for`); ~350 sites then emit structure-for-structure against it |
| **Tier 3 — Room** (285) | **YES** | the SQL is already in the `@Query("…")` string; shim runs it on sqlite, maps rows |
| **Tier 3 — Hilt DI** (159) | **YES** | a small container; classic easy shim |
| **Tier 3 — Compose** (257 @Composable, 1212 Modifier, 120 remember) | **wrapper absorbs syntax, but its body IS the hand-work** | `Modifier.padding().clickable{}` → real Flutter `Padding`+`GestureDetector`, one mapping per distinct API × hundreds; `remember` needs a positional slot-table runtime |

## The punchline: the UI wrapper already exists — it's the kit

PC's PseudoFlutter **kit is the Tier-3 Compose wrapper**, already built and golden-passing. PC didn't
"fight" the transpile with discipline; it *built the UI shim by hand* — which is the only way that
shim ever gets built (no automatic Compose→Flutter source exists). What PC did **not** build is the
**Tier-2 Flow wrapper** — it chose synchronous lowering instead (the audit's method-based providers).

So the wrapper framing sharpens the decision better than "literal-transpile everything":

- **UI wrapper (Compose→kit): already paid for.** A transpiler re-deriving it refunds nothing.
- **Flow wrapper (Tier 2): genuinely missing** — the one shim that would let WFL's VM logic transpile
  structure-preserved instead of being hand-rewritten. This is the real, scoped, buildable piece.

## Two caveats so it isn't oversold

1. **Wrappers fix the runtime gap (Tier 2/3); they do nothing for the expression gap (Tier 1).**
   `?.` (488), `?:` (474), `.copy(` (346), `let/apply/…` (242), `when` (108), templates (526) still
   need the lowering pass for the emitted code to even *call* the wrappers. Wrappers are necessary,
   not sufficient.
2. **"Doesn't feel a difference" holds for structure, not automatically for behavior.** Runtime
   fidelity is only as good as the shim's semantics — `flatMapLatest` cancel-previous,
   `SharingStarted.WhileSubscribed` ref-counting, `combine` re-emit timing. Those are the fiddly bits
   that decide whether the wrapped app actually behaves like WFL.

## Concrete next step on offer

Scope the **Flow shim** against WFL's *actual* usage — enumerate the exact operator set it must
provide (the 35 `combine`, 49 `stateIn`, 20 `flatMapLatest`, 103 `asStateFlow/asSharedFlow`, plus
`SharingStarted` variants) and what each needs — so the real size is visible before committing to
build it. Not started; awaiting the go.

Pointers: log_31 (the tiers + counts), log_30 (the audit), `WFL_PseudoCoup/src/kit.py` +
`app_flutter/lib/kit.dart` (the existing Tier-3 UI wrapper).
