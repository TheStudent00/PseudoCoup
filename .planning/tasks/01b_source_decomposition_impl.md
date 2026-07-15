# Phase 1b: Implement Source IR Extraction via Python `dis`

## 1. Context & Objective
As per the `PseudoIR v3` Master Plan, Phase 1 focuses on extracting Source IR Opcodes from high-level Python code. We previously hypothesized that `PseudoCoup_v1` contained robust `dis`-based extraction logic. However, a structural audit revealed that `v1`'s `extractor.py` was strictly `tree-sitter` AST-based, and its `models.py` defined high-level IR structures (`OpCode`, `BasicBlock`, `ControlFlowGraph`) without a concrete bytecode lifting mechanism.

**Objective**: Your task is to implement the foundation of the new `extractor` module in `PseudoIR v3` that explicitly leverages Python's built-in `dis` module to extract actual bytecode execution logic, completely bypassing syntax parsers like `tree-sitter`.

## 2. Technical Requirements

### A. Data Structure Definition (`pseudoir/core/models.py`)
1. Review the legacy `v1` models at `~/Programming/0_Archive/PseudoCoup_v1/pseudocoup/core/models.py` for inspiration, but do NOT copy them verbatim.
2. Define a clean, modern dataclass named `SourceOpcode`. It must, at a minimum, capture:
   - `opname`: The name of the instruction (e.g., `'LOAD_FAST'`, `'BINARY_ADD'`).
   - `opcode`: The integer identifier.
   - `arg`: The numeric argument (if any).
   - `argval`: The resolved argument value (e.g., the variable name or constant).
   - `offset`: The bytecode offset (critical for resolving jumps).

### B. The Extractor Module (`pseudoir/core/extractor.py`)
1. Implement a class or function (e.g., `extract_bytecode(target_callable)`) that uses `dis.Bytecode` or `dis.get_instructions`.
2. The extractor must accept a Python function or code object as input and return an ordered sequence (List) of `SourceOpcode` dataclass instances representing its logic.
3. Ensure the extractor correctly identifies and logs jump offsets for control-flow instructions (e.g., `POP_JUMP_IF_FALSE`).

### C. Testing & Verification (`tests/test_extractor.py`)
1. Write a unit test that defines a simple function involving our Priority 1 operations (e.g., a function that unpacks a tuple: `a, b = get_tuple()`).
2. Extract its opcodes and assert that the `UNPACK_SEQUENCE` instruction is successfully identified in the resulting `SourceOpcode` list.

## 3. Strict Operating Rules
- **No AST Parsing**: This module operates purely on execution bytecode (`dis`). Do not use `tree-sitter` or the `ast` module.
- **Execution Parity**: We only care about what the execution engine does, not the syntax.
- **Archive Protocol**: When complete, move this task document into the `.archive` directory within the tasks folder.

## 4. Work Environment
You will be working in the `PseudoIR` codebase (`~/Programming/PseudoIR`). Ensure `pseudoir/core/` is structured correctly as a Python package.
