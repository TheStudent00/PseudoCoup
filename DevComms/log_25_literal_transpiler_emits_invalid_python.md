# log_25 — review of log_22/24: the literal transpiler currently emits invalid Python (raw Kotlin)

Date: 2026-06-25
Type: review (grounded). Ran `literal_transpiler.py` on the `WorkoutWarmupViewModel.kt` it
cites and inspected the actual output before answering.

## Bottom line

The engine's *intent* and the TODO-for-unknown mechanism are sound, but the **actual output is
not "logically identical Python" — it's largely raw Kotlin pasted in, and it does not compile.**
The log_22/24 claims ("logically identical Python," "100% valid representation," "absolute
connectivity preservation," "Zero Silent Drops") are not met by the emitted file. And the
methodology has a hole: **mis-handled nodes don't trigger TODO**, so logic is garbled *silently* —
the opposite of the guarantee.

## Evidence (the emitted `build/literal/WorkoutWarmupViewModel.py`)

- `python3 -m py_compile` → **SyntaxError** at line 56 (`if (remaining > 0) delay(1_000L)`). Invalid Python.
- State fields are stubs + comments: `self._uiState = None  # private val _uiState = MutableStateFlow(...)`.
  The state — i.e. the connectivity — is `None`; the Kotlin is parked in a comment.
- Method bodies are **verbatim Kotlin**. `runTimer` came out as:
  ```
  _uiState.update { it.copy(stage = ConditioningStage.RUNNING, activity = activity, ...) }
  timerJob = viewModelScope.launch {
      for (remaining in fromSeconds downTo 0) {
          _uiState.update { it.copy(remainingSeconds = remaining) }
          if (remaining > 0) delay(1_000L)
      }
  }
  ```
  None of that is translated.

Why the flow-control handlers from log_24 don't fire here: ~all the real logic sits inside
`viewModelScope.launch { }` / `_state.update { }` **trailing lambdas**. The visitor treats those
call+lambda nodes as raw → dumps the whole block. So the `for/if/when` handlers exist but never
reach the code that matters. The reactive layer doesn't just need handling — it *encloses* the
logic, so handling top-level `if/for` buys little.

## Three specific technical flags

1. **`when → match/case` is unsound** (lines ~139-152). Python `match/case` is structural pattern
   matching, not Kotlin `when`:
   - `case bareName:` is a **capture** (binds, matches everything), not an equality test — a *silent*
     mistranslation.
   - `when` with `is Type` / `in range` / no subject (boolean arms) → invalid `case` syntax.
   The faithful literal mapping is **`if/elif`** with explicit `==` / `isinstance` / `in` (what
   log_19/21 recommended). `match/case` is a trap: when it's wrong it doesn't TODO, it silently
   means something else.
2. **`assignment`/`return`/etc. emit `get_text()` raw** (lines ~165-212) — the *expressions* aren't
   translated. `?:`, `?.`, `it.copy()`, string templates `"$x"`, `downTo`, `1_000L`, lambdas all land
   as raw Kotlin = invalid Python, and the connectivity references end up in untranslated text rather
   than a clean Python AST.
3. **"Zero Silent Drops" only covers UNHANDLED node types** → TODO. It does NOT cover *mis*-handled
   nodes (raw-copy, `when→match`). Those are "handled" (no TODO) but garbled — so silent logic
   corruption slips through the exact gate meant to close it. The guarantee must also fail loud when
   a handler can't translate its node faithfully.

## What's genuinely right

The discipline/intent; the TODO-for-unknown-types fallback; the structural class/method/param
extraction (signatures come out clean).

## The real work is expression translation, not statement skeletons

The hard surface is exactly what log_19/21 listed: scope functions/lambdas (`let/run/apply`, `it`),
null-safety (`?.`/`?:`/`!!`), `data class .copy()` → replace, string templates, range ops
(`downTo`/`until`/`step`), and descending *into* the reactive lambdas. Pasting raw text isn't
translation; until expressions are translated, the output is neither valid Python nor a clean
connectivity graph.

## Strategic (the part that matters for the decision)

This tool is being built to justify discarding the hand port — on the 465 number log_21 showed is a
measurement artifact. The current output shows the transpiler is a long way from producing *usable*
Python, let alone a replacement for the verified, golden-passing app. So: building the literal IR has
standalone value (a verification reference; a future migration on-ramp) and is fine to continue —
but **do not discard the working PC.** The replacement does not exist and is far off, and the audit
that motivated the discard still hasn't been re-run with a hardened probe.

## Recommendation

1. Make **mis-handled = TODO too** — a handler that can't translate faithfully must emit a marker,
   not raw text. That makes "Zero Silent Drops" actually true.
2. Switch **`when → if/elif`** (not `match/case`).
3. Invest in **expression translation + descending into lambdas** — that's where the connectivity
   lives and where the difficulty is.
4. **Keep the hand port**; harden the probe and re-run the audit before any discard decision.

Pointers: `PseudoCoup/tools/transpiler/literal_transpiler.py`; output `build/literal/`; prior
log_19 (probe), log_21 (audit-is-an-artifact).
