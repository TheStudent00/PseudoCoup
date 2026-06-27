# log_71 — transpiler architecture (dispatch discipline) + the Haxe / IR question

Date: 2026-06-27
Type: design commentary / decision record. No code changes. Captures the reasoning for a
fresh K→Py transpiler sub-project and assesses the "reuse Haxe" idea. Source-of-truth spec is
`TRANSPILER_SCOPE.md`; coverage instrument is `tools/transpiler/coverage.py`.

## 1. Why the current transpiler "feels loose and unstable" — it's the dispatch

`literal_transpiler.py` dispatches with a giant `if t == "...": elif ...` chain. That is the
weakest pattern: no exhaustiveness, order-dependent, and (the real flaw) handlers **emit-and-hope**
— a structurally-blind handler reconstructs hopeful text that nothing validates (see log: `16.dp`
→ `"16.dp"`, valid Kotlin, invalid Python; only a downstream py_compile catches it, and only the
syntactic failures).

Spectrum, loose → stable:
- **if/elif on node type** — the current transpiler. No safety net.
- **visitor: method-per-node, name dispatch** — Python's `ast.NodeVisitor`, AND our own
  **PyHaxe** (`emit_expr`/`emit_stmt` do `getattr(self, "expr_"+type(node).__name__)`, explicit
  unhandled→TODO). Modular, findable, has an explicit unknown path.
- **pattern-match over variant types** — OCaml/Rust/Scala. The **Haxe compiler itself is OCaml**
  and `match`es over typed-AST variants with **compiler-enforced exhaustiveness**. Gold standard.

PyHaxe already rejects the if-chain; the Kotlin transpiler is the outlier (it fell into string
compares because tree-sitter nodes are strings, not typed classes).

## 2. The Python-rigorous design (OCaml exhaustiveness without OCaml)

1. **Visitor dispatch** — `getattr(self, "v_" + node.type)`, one small method per node kind (the
   tree-sitter type string IS the suffix). Mirrors PyHaxe.
2. **Grammar-coverage test** — the compiled grammar enumerates **116 named node kinds**
   (`Language.node_kind_count` / `node_kind_for_id` / `node_kind_is_named`, verified). A test
   asserts every one of the 116 is handled / classified container-trivia / routed-to-wrap /
   explicitly-out-of-scope, and **fails CI otherwise**. This is the exhaustiveness guarantee — the
   analog of OCaml's compile-time check. (WFL corpus exercises 93 of 116; the test covers all 116.)
3. **Contract: map · wrap · fail — never emit-and-hope.** No handler returns text it can't
   guarantee parses; unknown/foreign constructs wrap or fail loudly.

## 3. Proposed fresh sub-project (donor, not foundation)

```
<repo>/  README (the contract+invariant) ·
  ktpy/ parse.py · dispatch.py (visitor core) · nodes/ (handlers, one concern per file) ·
        wrap/registry.py (curated Kotlin-construct→Python-shim) · wrap/runtime/ (shim libs)
  tests/ test_coverage.py (all 116 kinds) · test_nodes.py (per-construct golden)
  tools/ coverage.py (ported)
```
Reuse policy = no slop: `literal_transpiler.py` is a **donor**. Port handler logic one node at a
time, each rewritten as a tested `v_<kind>` method. Reused as-is: `coverage.py`, the tree-sitter
setup, `TRANSPILER_SCOPE.md` as spec. Everything else earns its way in.

Open decisions: repo name (proposed **PseudoKotlin**; alts KotlinPseudo / Kt2Pseudo) and
new-sibling-repo (recommended) vs subdir-of-PseudoCoup.

## 4. The Haxe / IR question — assessment

Idea floated: Haxe targets Java and Python, so can we use Haxe to get a Kotlin→Python transpiler,
or map a Haxe app to both Kotlin and Python?

- **The specific mechanism does NOT work.** Haxe is a **source language**: its compiler ingests
  **Haxe**, not Kotlin or Java. Its targets include Java and Python, but "targets Java" ≠ "emits
  Kotlin" and ≠ "reads Kotlin." There is no Haxe Kotlin target and no Kotlin/Java→Haxe source
  translator (jar2haxe etc. produce *externs* = API signatures, not translated logic). So Haxe
  gives us no Kotlin ingestion. Dead end as a translator.
- **The instinct is right, though: go through a resolved IR, not source text.** The robust analog
  is **Kotlin's own open-source compiler IR** (FIR/IR) + a custom **Python backend/plugin**. The IR
  is *semantically resolved* — types, overloads, extension properties (`16.dp`!), null-safety — all
  the things tree-sitter forces us to special-case are already resolved. This is the genuinely
  "stable" path the gut keeps pointing at. Cost: steep (Kotlin compiler internals, JVM/Gradle, large
  IR), but it eliminates whole categories of our gap list for free.
- **What IS reusable from Haxe:** study its `genpy` Python generator as a *reference* for idiomatic
  Python emission (closures, statics, class model) — read, don't ingest.
- **Parallel-corpus idea** (one app in both languages → learn the mapping) is an ML/statistical
  data strategy; it conflicts with the stated goal of a **deterministic, no-slop, complete**
  transpiler. Flagged, not recommended for the core.

**The real strategic fork** (independent of Haxe): FRONTEND choice —
- **tree-sitter (syntactic)** — light, no JVM, but WE resolve all semantics by hand (current path;
  `16.dp` is a special-case).
- **Kotlin compiler IR (semantic)** — heavy, JVM-bound, but the compiler resolves semantics; our
  job shrinks to IR→Python emission.

Recommendation pending owner input: prototype-scope first (we already have tree-sitter momentum and
a coverage discipline); keep the IR backend as the "if we need full semantic fidelity" escalation.
Worth a focused web/research pass on (a) existing Kotlin→Python transpilers to reuse/reverse, and
(b) the maturity of writing a Kotlin IR backend, before committing.
