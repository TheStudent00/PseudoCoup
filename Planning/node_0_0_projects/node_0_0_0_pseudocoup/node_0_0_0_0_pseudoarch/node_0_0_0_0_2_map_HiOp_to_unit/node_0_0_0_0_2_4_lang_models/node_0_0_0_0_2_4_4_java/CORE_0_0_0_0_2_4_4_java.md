---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.java
level: 6
status: active
settled_by: the owner
supersedes: null
designation: code (container)
node:
    name: java
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/node_0_0_0_0_2_4_4_java/CORE_0_0_0_0_2_4_4_java.md
super_node:
    name: lang_models
    path: ../CORE_0_0_0_0_2_4_lang_models.md
sub_nodes: []
---

# CORE 0_0_0_0_2_4_4 — java

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.java
- **level:** 6
- **status:** active
- **designation:** code (container)
- **settled_by:** the owner
- **supersedes:** null

## super_node

- [lang_models](../CORE_0_0_0_0_2_4_lang_models.md)

## sub_nodes

*(none yet)*

## definition

Java's own parts of `map_HiOp_to_unit`, as `gnu_c`, `go`, `rust`, and `python` hold GNU C's, Go's, Rust's, and Python's:
what Java adds to the language-agnostic machinery in `model_lang_parts`, starting with its lowerer, `javac` 25.0.4.1 and HotSpot JVM.

Plugs into the exact same 4-pillar `model_lang_parts` pipeline:
1. **`BranchTree`s over Java Compiler & HotSpot RISC-V Lowering Sources:** `com.sun.tools.javac.comp.Attr`,
   `Lower`, `Gen`, `Operators`, and HotSpot bytecode-to-RISC-V templates `templateTable_riscv.cpp`,
   `c1_LIRAssembler_arith_riscv.cpp` (808 functions, max depth 41) with tree-sitter Java and tree-sitter C++ branch extraction.
2. **Consolidated Vocabulary & Semantic Mask:** 4,999 accepted variants across 42 accepted operators (44 total operators)
   extracted from `extract_lang_vocabulary/vocabulary/java.json` and `mask/java.jsonl` into
   `lang_models/java/consolidated_java_vocabulary.jsonl.gz` and `consolidated_java_vocabulary.json`.
3. **Dual-Level Lowering (`lower_java.py` on `riscv64-runner`):**
   - **JVM Bytecode `Unit`s:** via `javac -g` + `javap -c -l` slicing the `LineNumberTable` to extract exact JVM bytecode `Unit`s
     (`iadd`, `ladd`, `idiv`, `irem`, `ishl`, `ishr`, `iushr`, `lcmp`, `fcmpl`, `fcmpg`, `checkcast`, etc.);
   - **RISC-V Machine `Unit`s (`riscv64` on `riscv64-runner`):** compiling exact JLS/HotSpot semantics for each `(operator, holder_types)`
     variant (`byte`, `short`, `char`, `int`, `long`, `float`, `double`, `boolean`, `String`, arrays, unsigned right shift `>>>`,
     JLS §15.17.2 non-trapping overflow, JLS §15.15.4 saturating float-to-int cast) to `riscv64-unknown-linux-gnu` object code
     with `-O0 -g` and slicing into RISC-V `Unit`s via `llvm-objdump -d -r -l -M no-aliases`.
4. **Automated Logical Domain-to-Range & Universal Cross-Language Proofs (`prove_java_domain_range.py`):**
   Z3 proofs establishing 100% UNSAT equivalence and AutoPoly piecewise emulation between Java, GNU C, Go, Rust, and Python,
   culminating in the 5-Language Universal Cross-Language Matrix.
