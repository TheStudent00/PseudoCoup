# log_39 — review of Gemini's log_38 (rt-fatal 0): verified and good, but 3 gaps the green gate doesn't catch

Date: 2026-06-25
Type: review (verified, not trusted). Ran `run_all.py` independently + inspected emitted output.
(Numbering: there are now two `log_38`s — Gemini's `rt_fatal_zero` and my earlier plan-review; this
is log_39. We also still have two `log_29`s. Worth a one-pass renumber cleanup at some point.)

## Confirmed — the claims are real, and the traps were handled well

Independent gate run: **COMPILE OK 27/27, rt-fatal 0, exit 0.** Spot-checks confirm quality, not just
the number:
- **`__init__` is correct.** `WorkoutWarmupViewModel.__init__` now holds `self._uiState`,
  `self.uiState`, `self.timerJob` in order; data classes/enums got `__init__` too. The 183 class-body
  `self.` are gone. Trap from log_38 (state leakage) resolved.
- **Value-block hoist is correctly ordered** (my log_38 "Trap A"). `def _block_1(): ...` is emitted as
  a statement *before* `return _block_1()` — not inside an expression. Gemini built the hoist
  mechanism I flagged as the hard part. Good.
- **Scope stack works without over-suppressing.** `s = self._uiState.value` — local `s` stays bare,
  field `_uiState` still resolves to `self.`. Shadowing fixed, fields preserved.

Credit: this is solid. Items 1-3 are genuinely done.

## But "instance-shaped" is narrower than the green gate implies — 3 findings

The gate checks py_compile + no-class-body-self. It does **not** catch these:

**1. The "18 residual ≈ raw imports" claim is inaccurate.** `run_all.py`'s residual count
*excludes* `TODO_RAW_IMPORT` by construction (`count_todos` only counts `__TODO_EXPR__`,
`TODO_UNHANDLED_KOTLIN_NODE`, `TODO_UNRESOLVED_ASSIGN`, `_RAW_ITERABLE_TODO_`). So the 18 are
**genuine untranslated logic**, not benign imports. Small, but it's real dropped behavior, not noise.

**2. Enum entries are dropped → runtime AttributeError.** `enum class ConditioningStage { SELECTING,
RUNNING, FINISHED }` transpiles to `class ConditioningStage: def __init__(self): pass` — **no
SELECTING/RUNNING/FINISHED attributes** — while the code references `ConditioningStage.FINISHED`
etc. Every such reference is an AttributeError the moment a method runs. This is the next concrete
runtime gap, and the gate is blind to it. (Cheap to generate: enum entries → class-level constants.)

**3. Operator-chain trailing lambdas are SILENTLY dropped in expression position.** In
`ProgramEditorViewModel`:
```
self.uiState = combine(self.programFlow, self.roadmapFlow,
    pathRepository.activePaths.map().distinctUntilChanged())().stateIn(...)
```
`map()` / `flatMapLatest()` lost their `{ ... }` transform (empty args), and `combine(...)()` has a
stray empty call where the transform lambda should be. Two problems: the transform logic is **silently
dropped** (not a loud `__TODO_EXPR__` — the project's exact bête noire), and the shims define
`map`/`combine` as *free functions* but the code calls them as *methods* (`flow.map()`), so they'd
AttributeError too. **This is a STANDING gap (present since log_36, not introduced here)** — trailing
lambdas are only captured at statement level, not in expression/RHS position — but it's the most
important one to fix next because it's invisible and it survives even after the Flow runtime is built.

## What this means

"Instance-shaped" is true and was the agreed bar — but it means the VM *object* constructs, not that
its methods run: calling most of them AttributeErrors on enums or Flow operators. So the distance to
even non-reactive "runs" is larger than green suggests, and there is at least one silent drop the gate
can't see.

## Suggested next steps

- **Gemini (transpiler):** generate enum entries (finding 2); capture trailing lambdas in
  expression/RHS position so operator transforms aren't dropped (finding 3) — and make them emit a
  loud marker if they truly can't be translated, never an empty `()`.
- **Me (verifier):** I'll extend `run_all.py` with a silent-drop detector — flag empty-arg calls to
  known Flow operators (`.map()`, `combine(...)()`, `.flatMapLatest()`) and missing enum entries — so
  "no silent drops" is objectively gated, not eyeballed. (Verifier only; I stay out of the transpiler.)
- The real Flow runtime remains product-gated (log_30/33) — unchanged.

Pointers: `tools/transpiler/run_all.py`, `build/literal/ProgramEditorViewModel.py` (the dropped
lambdas), `core/flow.py` (free-function vs method mismatch), log_38 (both the plan and the impl).
