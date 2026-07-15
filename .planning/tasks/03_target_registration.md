# Phase 3: Automated Compilation & Extraction

## Overview
Once the Full QuickFox Fuzzer has generated the exhaustive target language file, this phase focuses on compiling that file to extract the definitive Intermediate Representation (IR) opcodes. By matching the generated function names back to the `tree-sitter` nodes, we establish a perfect, mechanized mapping.

## Objectives
- Invoke the target compiler on the generated QuickFox file.
- Parse the resulting IR dump.
- Build the definitive mapping dictionary aligning `tree-sitter` nodes to execution opcodes.

## Sub-Tasks

### 3a: Target Compiler Hook
- **Task:** Build an automated execution runner that passes the QuickFox file into the target compiler.
- **Details:** For Go, this involves running `GOSSAFUNC` on every generated `Probe_` function and intercepting the output (e.g., `ssa.html`).

### 3b: IR Dump Parsing
- **Task:** Write a parser to strip the raw opcodes from the compiler's output dump.
- **Details:** Extract the flat sequence or Data Flow Graph of operations executed within each `Probe_` function.

### 3c: Mechanistic Dictionary Assembly
- **Task:** Build the final mapping dictionary.
- **Details:** Since the function name dictates the `tree-sitter` node (e.g., `Probe_BinaryExpression_Add`), map that node directly to the extracted SSA opcodes. Serialize this exhaustive dictionary for use by `PseudoCoup` in Phase 4.
