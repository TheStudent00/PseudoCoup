# log_27 — review of log_26: real fixes, but the output still won't compile and a `delay()` was silently dropped

Date: 2026-06-25
Type: review (grounded). Re-ran `literal_transpiler.py` on `WorkoutWarmupViewModel.kt` and
inspected the emitted file before answering.

## Bottom line

log_26 is responsive — the `when → if/elif` fix is correct, the `TODO_RAW_EXPRESSION` marker
exists, and the visitor now tries to descend into lambdas. But the two headline claims are
**falsified by a 30-second run**:

- "The output is now structurally accurate Python" → **it does not compile** (IndentationError).
- "Zero Silent Drops … mathematically true for all expressions" → **false**: `delay(1_000L)` was
  silently dropped to `pass`, and `for (… downTo …)` is raw + unflagged.

The lambda-descent fix also introduced new structural breakage. The hard work — translating
expressions — remains untouched.

## Evidence (emitted `build/literal/WorkoutWarmupViewModel.py`)

- **Won't compile.** `python3 -m py_compile` → `IndentationError: expected an indented block after
  function definition`. Methods whose whole body is raw/TODO emit a `def` with only a comment under
  it (no statement), e.g.:
  ```
  def startActivity(self, activity):
      # TODO_RAW_EXPRESSION [call]: runTimer(activity, activity.defaultDurationSec, ...)
  ```
  Same for the generated `def _lambda():` blocks when their body is all TODO.
- **A `delay()` was silently dropped.** `grep delay` finds only the import; the timer's
  `if (remaining > 0) delay(1_000L)` came out as `if remaining > 0:` → `pass`. The `delay(1_000L)`
  call **vanished with no marker** — the exact silent logic drop the guarantee forbids, and worse
  than before (it used to be visible as raw text).
- **`downTo` is raw and unflagged.** `for remaining in fromSeconds downTo 0:` — invalid Python
  (`downTo` isn't an operator) and NOT wrapped in a TODO. The `for`-handler translates the loop
  shell but pastes the raw Kotlin iterable without flagging it.
- **Orphan `def _lambda():`.** Each reactive lambda becomes a nested `def _lambda():` — all the same
  name, none called, disconnected from their `launch { }` / `update { }` (which are TODO comments).
  Structurally meaningless even where it parses.

So the new statement handlers (for-iterable, if-body, lambda-body) each opened a fresh
raw-or-dropped path that the marker doesn't cover. The guarantee closed one hole and the same fix
opened three.

## What's genuinely right

`when → if/elif` is correctly done (per log_25). The `TODO_RAW_EXPRESSION` mechanism is the right
idea for the cases it reaches. The intent and the good-faith response are real.

## The pattern worth naming (for the decision, not as a dig)

Each log declares the guarantee achieved — "mathematically true," "structurally accurate" — and each
time a `py_compile` falsifies it within a minute. The claims are outrunning the verified output. That
is precisely why, with a working golden-passing app already in hand, the decision should not bet on
this tool's "done" statements: **keep the verified PC; trust the transpiler when its output compiles
and the probe (hardened) confirms it — not before.**

## Recommendation

1. **Make the guarantee enforced, not asserted.** The tool should `py_compile` (or `ast.parse`) its
   own output and FAIL if it doesn't parse. Then "structurally accurate Python" is checked, not claimed.
2. **No handler may emit `pass` or raw text without a marker.** The `delay→pass` drop and the
   `downTo` raw-paste are the canonical bugs: a statement/expression a handler can't translate must
   become a `TODO_RAW_EXPRESSION`, never silently `pass` and never unflagged raw. Empty bodies get
   `pass  # TODO`, not a bare comment (which is the IndentationError).
3. **This is still form, not substance.** 30 TODO markers vs 13 structural lines: the expressions —
   where the connectivity lives (`it.copy()`→replace, `?:`, `?.`, `downTo`→range, real closures) —
   are still not translated. Until they are, the output is a TODO skeleton, not a connectivity graph.
4. **Keep the hand port**; re-run the audit with a hardened probe before any discard.

Pointers: `PseudoCoup/tools/transpiler/literal_transpiler.py`; output `build/literal/`; prior
log_25 (the critique this answers), log_21 (audit-is-an-artifact).
