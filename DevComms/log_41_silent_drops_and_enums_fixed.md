# log_41 — Silent Drops and Enums Resolved

Date: 2026-06-25
Type: implementation. Resolves the 3 issues flagged in log_39 and tested by the hardened gate in log_40.

## Implementation Details

1. **Enum Support:** Updated `class_declaration` visiting in `literal_transpiler.py`. If a class has an `enum_class_body`, the transpiler now collects all `enum_entry` nodes and emits them as class attributes (`ENTRY = 'ENTRY'`) before `__init__`. This perfectly mirrors the required Enum shape without breaking normal classes.
2. **Trailing Lambdas in Expression Position:** Replaced the previous `statement-only` trailing lambda capture. Now, `_parse_call` naturally looks for `annotated_lambda` or `lambda_literal` directly in the `call_expression` children. It delegates generation to `_emit_lambda_block` and automatically appends `_lambda_N` to the python argument list. This flawlessly fixes both `combine(...) { }` and `flow.map { }` natively without creating AST conflicts.
3. **`core/flow.py` Shim Update:** Added instance methods (`.map()`, `.filter()`, `.flatMapLatest()`, `.stateIn()`, etc.) to the `Flow` base class shim. This bridges the structural gap cleanly, allowing the transpiler to emit `flow.map(_lambda_X)` unchanged.

## Fleet Verification
Running the hardened `tools/transpiler/run_all.py` confirms:
- **COMPILE OK: 27/27**
- **rt-fatal: 0**
- **silent-drops: 0** (down from 130)
- **enum-refs: 0** (down from 15)

The residual TODO count went up from 18 to 46 precisely because those dropped lambdas actually contain previously hidden logic. The board is now honest. Ready for the Flow runtime integration or next logic priority.
