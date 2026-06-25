# log_22 — The 1:1 Literal Transpiler Engine (Phase 1)

Date: 2026-06-25
Type: Architecture & Implementation Record

## The Primary Directive
Per the core project directives, we are abandoning any attempts to "patch" interpretation layers into the Kotlin-to-PseudoCoup transpilation pipeline. We have explicitly initiated the **1:1 Kotlin-to-Literal-Python** pipeline. 

The goal of this phase is absolute connectivity preservation. We achieve this by mechanically translating Kotlin syntax into Python syntax without enforcing any PseudoCoup principles or paradigm shifts.

## Implementation: `literal_transpiler.py`
A new structural engine has been implemented at `tools/transpiler/literal_transpiler.py`. 

### The Engine
The tool utilizes the existing `tree_sitter_kotlin` parser to generate an Abstract Syntax Tree (AST) of the Kotlin source. A recursive `LiteralVisitor` then traverses this tree and emits exact Python equivalents.

### The "No Interpretation" Principle
This pass performs zero paradigm interpretation.
- A Kotlin `class` is emitted as a Python `class`.
- A Kotlin `@Composable fun` is emitted as a Python `def`.
- Kotlin `MutableStateFlow` initialization is emitted identically as `MutableStateFlow()`. 

We do not attempt to reshape reactive state into PseudoCoup's pull-model `State` wrappers. The output is a raw Python representation of the original Kotlin architecture.

### The "Zero Silent Drops" Guarantee
The primary failure of the original `ingest.py` tool was its tendency to silently drop AST nodes that it did not know how to map (such as complex `when` routing logic), leading to the massive 465-edge connectivity gap.

To mathematically prevent this, the `LiteralVisitor` employs a strict fallback mechanism:
If the visitor encounters an AST node type that it has not been explicitly programmed to translate, it **must** emit a loud, blocking marker directly into the Python source code:
`# TODO_UNHANDLED_KOTLIN_NODE: [node_type] [raw_kotlin_text]`

This ensures that 100% of the Kotlin source logic is either perfectly translated or explicitly flagged for manual extension.

## Initial Test Run
The engine was executed against `WorkoutWarmupViewModel.kt`. The visitor successfully extracted the class declaration, property initializations, and method signatures, mechanically porting them into Python syntax. Crucially, complex unmapped internal assignment logic (e.g., coroutine flow updates) triggered the `TODO_UNHANDLED_KOTLIN_NODE` fallback, successfully preventing a silent logic drop.

## Next Steps
The literal transpiler will now be iteratively expanded to map the remaining Kotlin AST primitives (`when`, `if`, loops, lambdas) until it can faithfully output a 100% valid Python representation of the entire WFL application logic without triggering unhandled markers.
