---
id: hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.python
level: 6
status: active
settled_by: the owner
supersedes: null
designation: code (container)
node:
    name: python
    path: Planning/node_0_0_projects/node_0_0_0_pseudocoup/node_0_0_0_0_pseudoarch/node_0_0_0_0_2_map_HiOp_to_unit/node_0_0_0_0_2_4_lang_models/node_0_0_0_0_2_4_3_python/CORE_0_0_0_0_2_4_3_python.md
super_node:
    name: lang_models
    path: ../CORE_0_0_0_0_2_4_lang_models.md
sub_nodes: []
---

# CORE 0_0_0_0_2_4_3 — python

## metadata

- **id:** hq.projects.pseudocoup.pseudoarch.map_HiOp_to_unit.lang_models.python
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

Python / CPython's own parts of `map_HiOp_to_unit`, as `gnu_c`, `go`, and `rust` hold GNU C's, Go's, and Rust's:
what Python adds to the language-agnostic machinery in `model_lang_parts`, starting with its lowerer and bytecode compiler, CPython 3.13.

Plugs into the exact same 4-pillar `model_lang_parts` pipeline:
1. **`BranchTree`s over CPython's Compiler & Evaluator Sources:** `Python/compile.c`, `Python/bytecodes.c`,
   `Python/generated_cases.c.h`, `Objects/abstract.c`, `Objects/longobject.c`, and `Objects/floatobject.c`
   (767 functions, max depth 44) with tree-sitter C branch extraction.
2. **Consolidated Vocabulary & Dynamic Grid:** 599,954 accepted variants across 53 operators extracted
   from `extract_lang_vocabulary/vocabulary/python.json` and `mask/python.compact.json` into
   `lang_models/python/consolidated_python_vocabulary.jsonl.gz` and `consolidated_python_vocabulary.json`.
3. **Dual-Level Lowering (`lower_python.py`):**
   - **CPython Bytecode `Unit`s:** via Python's `compile()` + `dis` + PEP 657 `co_lines()` slicing out wrapper chaff;
   - **RISC-V Machine `Unit`s (`riscv64` on `riscv64-runner`):** compiling specialized CPython fast-paths for each `(operator, holder_types)`
     variant with `clang --target=riscv64-unknown-linux-gnu -O0 -g -c` and slicing via `llvm-objdump -d -r -l -M no-aliases`.
4. **Automated Logical Domain-to-Range Proofs (`prove_python_domain_range.py`):** Z3 proofs establishing 100% UNSAT
   domain-range equivalence and AutoPoly piecewise emulation between Python, GNU C, Go, and Rust.
