# log_36 — I took a turn on the transpiler: 18/27 → 27/27 compile, and the output now resolves self/it/null/elvis/lambdas

Date: 2026-06-25
Type: implementation (Claude). Rather than hand back another prose list (log_35), I fixed the
defects directly and measured. The gate is the same one from log_35: run the transpiler on all 27
VMs, `py_compile` every output.

## Result

```
Gemini baseline (log_34):  COMPILE OK 18/27   ran: 0
After these fixes:         COMPILE OK 27/27   (every VM emits valid Python)
```

Verified, not asserted — the loop is in the commit and reproducible:
`for f in .../*ViewModel.kt; do literal_transpiler.py $f; python3 -m py_compile out; done`.

## What I changed (architecture untouched — same LiteralVisitor/parse_expression/visit)

1. **All contexts route through `parse_expression`.** `if`/`when`/`while`/`for` conditions and
   iterables previously used raw `get_text`, leaking `||`, `!`, `==`. Now translated. (fixed
   Onboarding-class failures)
2. **`unary_expression` `!x` → `(not x)`.** (fixed ReportBug)
3. **String templates → f-strings.** `"day${if (n==1L) "" else "s"}"` →
   `f'day{("" if n == 1 else "s")}'`, with quote selection to avoid nesting conflicts. (fixed DebugPanel)
4. **`if`-as-value → ternary; `when`-as-value → nested ternary; `when`-statement → if/elif chain**
   (incl. subjectless `when {}`, `is` → `isinstance`, `in` → `in`).
5. **Elvis with control flow.** `val a = x ?: return` is lowered at statement level to
   `a = x; if a is None: return`. Bare `continue`/`break` parse as plain identifiers in this grammar
   (only `return`/`throw` get `*_expression` nodes), so detection is text-aware. Nested-in-expression
   elvis-jumps that Python can't carry inline degrade to `(x if x is not None else None)` (loud loss,
   not a break).
6. **Implicit `this` → `self.<field>`.** Class fields/methods/ctor-params are collected per class;
   bare member references become `self.x`. So `_uiState`/`timerJob` are no longer undefined names.
7. **Function-local `val/var` → real locals** (`s = self._uiState.value`), not `self.s = None`.
8. **Lambdas:** unique names (`_lambda_0`, `_lambda_1`…), `it=None` param (so both `block()` and
   `block(value)` call sites work), and implicit `return` of the final expression. So
   `update { it.copy(...) }` → `def _lambda_0(it=None): return it.copy(...)`.
9. **`null` → `None`; numeric suffixes** (`1_000L` → `1000`); `as?`/`as` casts dropped;
   `x[i]` indexing; Python-keyword method names (`.with(` → `.with_(`) mangled.
10. **The emit gate is now blocking** — `run()` `sys.exit(2)` on invalid Python.
11. **Safe fallback:** an untranslatable expression emits `"__TODO_EXPR__"` (valid, greppable),
    never raw Kotlin. This is what stops comment-unicode (`§`, `→`, `—`) from breaking the parse.

Before/after on `WorkoutWarmupViewModel.finishActivity` (the log_34 example):

```
# Gemini:                              # after:
(timerJob.cancel() if timerJob ...)    (self.timerJob.cancel() if self.timerJob is not None else None)
def _lambda():                         def _lambda_0(it=None):
    it.copy(stage=FINISHED)                return it.copy(stage=ConditioningStage.FINISHED)
_uiState.update(_lambda)               self._uiState.update(_lambda_0)
```

## Honest state — compiles, does NOT yet run end-to-end

"Compiles" is not "runs," and I'm holding myself to the same bar I held log_34 to:

- **Residual untranslated surface (now loud, not silent):** 72 `__TODO_EXPR__` + 76
  `TODO_UNHANDLED_KOTLIN_NODE` across the 27. These are real dropped expressions/statements —
  value-position `when` with block bodies, some nested closures, misc node types — now visible
  placeholders instead of raw-Kotlin breaks or silent drops. `_RAW_ITERABLE_TODO_` and leaked `null`
  are both at **0**.
- **The shims are still inert** (`core/flow.py`: `combine`/`stateIn`/`flatMapLatest` return empty
  `Flow()`, `collect` is `pass`). So even though the reactive *calls* are now emitted against `self.`
  with correct lambdas, **no data flows**. Structure is faithful; behavior is not. This remains the
  real Tier-2 work (option-(a)), and I deliberately did **not** start it — it's a product decision,
  and there's no point implementing reactive semantics until the emitted code reliably runs.
- Member resolution is heuristic (a local shadowing a field name would be wrongly `self.`-prefixed);
  fine for the VM pattern, a known sharp edge.

## Suggested division of labor from here

- If we pursue the transpile path: the next mechanical layer is draining the 148 TODO spots
  (value-position `when`-blocks are the biggest cluster) and `__init__`/constructor generation (no VM
  currently emits an `__init__`, so fields default to module-load-time, not per-instance).
- The genuinely new piece remains the **real Flow runtime** — but that waits on the product call
  (build the deferred features vs. keep the current subset), per log_30/33.

Numbering note: this is log_36. There are currently two `log_29` files (mine + Gemini's
`log_29_flow_and_coroutine_shims`); suggest renaming the shim one to keep the sequence linear.

Pointers: `tools/transpiler/literal_transpiler.py` (header lists the 11 changes), `core/flow.py`,
`core/coroutines.py`; log_34 (claims), log_35 (the review that scoped these fixes).
