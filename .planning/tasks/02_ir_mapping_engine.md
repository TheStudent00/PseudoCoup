# Phase 2: Semantic Probing & Alignment

## Overview
This phase handles the critical translation verification step: taking the extracted Source Language IR Opcodes and automatically aligning them with corresponding Target Language IR Opcodes using "Rosetta Stone" probes.

## Objectives
- Eliminate manual dictionary mapping by automating opcode alignment.
- Build the semantic probe runner to compile and extract Target IR.
- Develop the mathematical alignment engine to verify execution parity between Source and Target IR.

## Sub-Tasks

### 2a: Establish the Probe Interface
- **Task:** Define the standard interface for a "Rosetta Stone" probe.
- **Details:** Probes must be atomic, identical semantic operations (e.g. `[].append(1)` for Python, `[].add(1)` for Dart).

### 2b: Target IR Extraction Hooks
- **Task:** Build automated hooks that compile a Target Probe and extract its resulting opcodes.
- **Details:** This involves invoking the target's compiler (e.g. Dart VM, `rustc`) on the probe and parsing the dumped IR.

### 2c: Mathematical Alignment Engine
- **Task:** Build the system that compares the sequence of Source Opcodes to the sequence of Target Opcodes.
- **Details:** The engine must account for context variations and verify that `Source IR Sequence A == Target IR Sequence B`, effectively proving semantic equivalence on the stack.
