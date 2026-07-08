# PseudoCoup

> Write an application **once**, in one good notation—disciplined, intentful pseudo-code—and render it to **any** platform through **any** target, staying completely lossless and future-safe.

PseudoCoup is the umbrella: a coup against un-portable, un-intentful design. It owns nothing technical itself; it is the altitude above all targets. You write *disciplined Python* (one notation, platform-agnostic); each target is a transpiler powered by `tree-sitter` AST evaluation to emit native code.

## The V2 Universal Architecture

PseudoCoup relies on a 3-stage memoryless pipeline. Unlike typical 1-to-1 transpilers, PseudoCoup does not attempt to map Python directly to Kotlin. Instead, it distills all code into pure, language-agnostic intent.

1. **Ingress (Flatteners):** Source code from *any* of the 13 supported languages is parsed by `tree-sitter` into an AST and flattened down into the Universal Linear Intermediate Representation (IR). 
2. **The Brain (Universal Graph):** The core engine completely throws away the source language syntax. It reconstructs a Control Flow Graph (CFG), transforms the variables into Static Single Assignment (SSA) form, and propagates types dynamically.
3. **Egress (Generators):** An Out-of-SSA optimizer strips away internal compiler tracking and reconstructs a high-level AST. The Generators then emit clean, highly readable, natively formatted code in the target language.

**Supported Languages:** Python, Dart, Kotlin, Rust, Go, TypeScript, C#, C++, C, Java, Swift, Ruby, PHP.

## How to Use (CLI API)

PseudoCoup is fully operable via its centralized command-line interface.

```bash
python3 -m pseudocoup.cli --source <filepath> --source-lang <lang> --target-lang <lang> [--emit-dot]
```

**Parameters:**
- `--source`: Path to the source code file.
- `--source-lang`: The language of the source file (default: `python`).
- `--target-lang`: The target language you wish to transpile to.
- `--emit-dot`: (Optional) Generates a GraphViz `.dot` file and `.png` image of the Universal Control Flow Graph for debugging.

**Example: Transpiling Python to Rust**
```bash
python3 -m pseudocoup.cli --source examples/fox.py --source-lang python --target-lang rust
```

## The Universal Discipline

To achieve lossless transpilation across infinite architectures, developers must adhere to **The Universal Discipline**:

1. **Intent, not Mechanism:** Code describes what the app *wants*, never how a toolkit does it. Intent survives churn because it never names the mechanism.
2. **Concrete Constructs:** Rely on standard OOP Composition, strictly typed data structures, and concrete control flow logic (`while`, `if`, standard arithmetic, `try/catch`).
3. **Map -> Wrap -> Fail:** The Golden Rule of translation. 
   - First, attempt to *Map* logic to a native 1:1 equivalent.
   - If impossible, *Wrap* the logic in a custom semantic registry wrapper.
   - If wrapping breaks portability, *Fail* loudly. The compiler should never hallucinate approximations.

## The "Quick Fox" Infinite Daisy-Chain

Because PseudoCoup relies on pure Universal Graphs and Out-of-SSA optimization, it does not suffer from code degradation or graph bloat. 

To prove this, PseudoCoup runs an infinite daisy-chain parity test on `examples/fox.py` (a comprehensive script executing math, conditionals, classes, hashmaps, and loops). We compile the script through all 13 languages sequentially:

`Python -> Dart -> Kotlin -> Rust -> Go -> TypeScript -> C# -> C++ -> C -> Java -> Swift -> Ruby -> PHP -> Python`

You can view the actual output files from this exact 13-language transpilation loop in the **`examples/emitted_fox/`** directory.

The final output Python code returns **perfectly identically formatted and pristine**, with no SSA bloat, no dropped blocks, and perfect structural integrity. PseudoCoup proves that lossless, cross-platform Universal Translation is definitively possible.

## License

OTU-GL — see the bundled license PDF.
