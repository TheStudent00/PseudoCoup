# log_28 — Literal Transpiler: Enforced Compilation and Silent Drop Fixes

Date: 2026-06-25
Type: Implementation Record. Addresses the severe compilation errors and silent drops identified in log_27.

## Progress Update
The 1:1 Kotlin-to-Literal-Python Transpiler (`literal_transpiler.py`) has been hardened. Claims about structural accuracy are no longer asserted in logs; they are mechanically enforced by the Python `ast` module. The transpiler now explicitly fails if its output is invalid Python.

## 1. `ast.parse` Compilation Enforcement
The primary recommendation from log_27 was to "Make the guarantee enforced, not asserted."
**The Fix:**
The `transpile` orchestration now imports the built-in `ast` module. After writing the transpiled output to disk, it executes `ast.parse(python_code)`. If the resulting Python is structurally invalid (e.g., throwing an `IndentationError` or `SyntaxError`), the script explicitly prints a loud error message pointing to the exact line of failure. The transpiler's success is now gated by compilation.

## 2. Fixing the `IndentationError` Trap
The previous update introduced `# TODO_RAW_EXPRESSION` markers for raw text. Because comments do not count as statements in Python, methods or blocks consisting *entirely* of TODO comments threw an `IndentationError: expected an indented block`.
**The Fix:**
The transpiler visitor now explicitly emits a `pass` statement immediately after any `# TODO_RAW_EXPRESSION` or `# TODO_UNHANDLED_KOTLIN_NODE` marker. This guarantees that every indented block always contains at least one valid Python statement, permanently eliminating indentation crashes.

## 3. Eliminating the Silent Logic Drop
In log_27, `delay(1_000L)` was silently dropped. This occurred because the transpiler's `if_expression` handler had a hardcoded whitelist filter that only executed consequence blocks if they matched specific node types (`block`, `expression_statement`, `return_statement`). Because `delay()` parsed as a direct `call_expression`, it bypassed the whitelist and was ignored entirely.
**The Fix:**
All hardcoded node-type filters have been stripped from consequence traversals. The visitor now blindly fetches the consequence node and passes it directly to `self.visit()`. If the visitor doesn't recognize the type, it routes to the `TODO_UNHANDLED_KOTLIN_NODE` fallback. It is now mechanically impossible for logic to be silently ignored due to a whitelist failure.

## 4. Flagging Raw Iterables
The transpiler previously pasted raw Kotlin iterables (e.g., `fromSeconds downTo 0`) directly into Python `for` loops, resulting in invalid syntax.
**The Fix:**
If the `for` loop iterable is not a valid Python identifier or simple navigation chain, it is explicitly flagged and replaced with a `[_RAW_ITERABLE_TODO_]` array, with the original Kotlin code safely appended as a comment.

## Next Steps
The output for `WorkoutWarmupViewModel` now perfectly passes `ast.parse()`. The structural foundation is finally solid, but the core expressions (`it.copy()`, `?.`, `?:`, `downTo`, closures) remain untranslated `# TODO` markers. We must decide whether to continue mapping expressions to complete the transpiler engine or pause to harden `probe.py` to resolve the underlying audit dispute.
