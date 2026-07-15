# Phase 3: AST Lifting & Automated Fill

## Overview
Once the IR Opcodes have been mathematically aligned between the Source and Target, we must translate that alignment back into high-level syntax. This phase covers extracting the Target AST node from the verified probe and registering it as automated fill for `PseudoCoup`.

## Objectives
- Parse the verified Target Probe back into a high-level AST.
- Extract the specific AST node representing the executed logic.
- Register this node in a format `PseudoCoup` can use for zero-flattening egress.

## Sub-Tasks

### 3a: Target Probe Parsing
- **Task:** Utilize the respective language's `tree-sitter` grammar to parse the Target Probe.
- **Details:** For example, parsing `[].add(1)` in Dart to produce the structural `MethodInvocation` node.

### 3b: AST Node Extraction & Serialization
- **Task:** Extract the relevant node and serialize it into an "automated fill" template.
- **Details:** The extracted node must be parameterized (e.g., separating the base list from the argument `1`) so it can accept generic inputs during transpilation.

### 3c: Automated Registration API
- **Task:** Build the API that injects this serialized AST node directly into `PseudoCoup`'s Egress registry.
- **Details:** `PseudoCoup` will query this API. If a match is found for a given Python built-in, it uses the AST template instead of falling back to the strict `Map -> Wrap -> Fail` protocol.
