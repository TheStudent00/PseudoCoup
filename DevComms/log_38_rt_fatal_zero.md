# log_38 — rt-fatal 0 Achieved

Date: 2026-06-25
Type: implementation. Resolves the 3 issues flagged in log_37.

## Success Metric Achieved: Compiles + Instance-Shaped
As requested, the transpiler now correctly implements instance mapping for the fleet without asserting "runnable" status (which waits on Flow/domain stubbing). 

The 183 `self.X = ...` assignments leaking into the class-body indent have been eliminated. `__init__` synthesis correctly gathers the primary constructor arguments, properties, and `init` blocks.

## Implementations
1. **Scope Stack:** Replaced `self.local_vars` with `self.scopes = []`. The stack pushes/pops on `function_declaration`, `lambda_literal`, and correctly maps `it` alongside other parameters, completely solving the shadowing bug.
2. **Value-position Structures:** Value-position `when` blocks and `if` blocks are now cleanly hoisted into `def _block_N()` generators instead of returning `__TODO_EXPR__`.
3. **AST Filtering:** Upgraded `node.named_children` array access throughout the parser to explicitly filter `line_comment` and `block_comment`. This fixed several trailing lambda and method chain bugs where comments structurally leaked into `__TODO_EXPR__`.

## Fleet Verification
Running `tools/transpiler/run_all.py` confirms:
- **COMPILE OK: 27/27**
- **rt-fatal: 0**
- Residual `__TODO_EXPR__` / TODO marks dropped to 18 (almost exclusively raw imports for android and java dependencies).

Ready for the next step (which will likely involve Flow/domain stubbing based on product decisions).
