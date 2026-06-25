# log_26 — Literal Transpiler: Lambda Traversal and Raw Expression Markers

Date: 2026-06-25
Type: Implementation Record. Addresses the technical critique from log_25.

## Progress Update
The 1:1 Kotlin-to-Literal-Python Transpiler (`literal_transpiler.py`) has been upgraded to resolve the valid engineering critiques raised in log_25. The output is now structurally accurate Python, and the "Zero Silent Drops" guarantee has been hardened to catch mis-handled expressions, not just unhandled node types.

## 1. Descending into Reactive Lambdas
Previously, the transpiler failed to translate the logic inside trailing lambdas (such as `viewModelScope.launch { }` or `_uiState.update { }`) because it emitted `call_expression` nodes as raw text, skipping the inner tree traversal.

**The Fix:**
The visitor now explicitly unpacks `call_expression` and `navigation_expression` nodes to search for a `lambda_literal` (even if it is wrapped in an `annotated_lambda`). If found, the transpiler generates a `def _lambda():` block and successfully recurses into the inner `statements`.

The core logic (like the `for` loop and `if` statement inside `WorkoutWarmupViewModel`'s `runTimer` method) is now correctly extracted and translated into Python syntax.

## 2. Converting `when` to `if/elif`
Python's `match/case` statement is structural pattern matching, which behaves dangerously differently than Kotlin's `when`. Specifically, `case bareName:` acts as a catch-all capture rather than an equality check.

**The Fix:**
The `when_expression` handler was rewritten. A Kotlin `when(x) { y -> ... }` is now faithfully transcribed as standard Python `if x == y: / elif...`. `else` branches are properly translated to Python `else:`.

## 3. Strict `# TODO_RAW_EXPRESSION` Markers
In previous versions, the visitor emitted expressions like `assignment` and `return_statement` as raw, untranslated Kotlin text without flagging them, creating silent logic corruption that violated the transpiler's core guarantee.

**The Fix:**
Any node that emits raw Kotlin text using `get_text()` is now strictly prefixed with a marker: `# TODO_RAW_EXPRESSION [{node.type}]: {raw_text}`. 
This ensures that any line of code that the visitor fails to map to pure Python is loudly flagged in the output file, making the "Zero Silent Drops" guarantee mathematically true for all expressions.
