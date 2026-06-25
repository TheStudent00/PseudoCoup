# Transpiler Architecture Pivot: Intermediate Representation (IR)

## The Problem with `ingest.py`
The current Kotlin-to-PseudoCoup transpiler (`ingest.py`) attempts to perform two highly complex operations in a single pass:
1. **Language Translation:** Parsing Kotlin syntax and translating it into Python syntax.
2. **Paradigm Interpretation:** Interpreting Jetpack Compose/Android state, lifecycle, and navigation paradigms and mapping them into the rigid `Screen`/`Component` structural hierarchy of the PseudoCoup discipline.

By conflating language translation and paradigm interpretation, the transpiler is forced to rely on massive, hardcoded mapping dictionaries (`KNOWN_CUSTOM`, `NAV_RESOLUTION`). When it encounters complex control flow like `when` statements or `forEach` loops determining navigation routes (e.g., the workout roadmap logic), the "Paradigm Interpretation" phase fails to gracefully squash this into PseudoCoup constructs. As a result, critical state transitions and wiring are dropped, leading to the broken runtime behavior detected by the Tracer Dye tests.

## The Solution: The Intermediate Representation (IR) Pipeline
To guarantee complete connectivity and logical fidelity, we must separate language translation from structural interpretation. We can achieve this by introducing a strict 1:1 Intermediate Representation.

### Phase 1: Kotlin to Literal Python (Zero Paradigm Shift)
We will construct a new transpiler module that performs a literal, 1:1 translation from Kotlin AST to Python AST. 
- Kotlin `class` -> Python `class`
- Kotlin `when` -> Python `match`/`if-elif`
- Kotlin `onClick` -> Python callbacks
- No PseudoCoup principles are enforced during this stage.

**Result:** A structurally identical, fully-wired representation of the WFL application logic written entirely in standard Python.

### Phase 2: Python IR to PseudoCoup Python (AST Transformation)
With a complete Python representation of the app's logic in hand, transforming the application into the PseudoCoup architecture becomes a pure AST (Abstract Syntax Tree) transformation problem *within the same language*.
Using Python's powerful built-in `ast` module, we can systematically traverse the literal Python code and migrate it into `ComponentManager` structures, `Screen` definitions, and formal routing systems.

**Result:** A fully compliant PseudoCoup Python application. Because this transformation operates on a guaranteed, 1:1 translation of the original source logic, we can mathematically ensure that every edge and node (connectivity) is preserved during the structural shift.

### Phase 3: PseudoDart Emission
The standard PseudoCoup compiler toolchain takes over, converting the structurally sound PseudoCoup Python into Dart/Flutter targets via `transpile.py`.

## Review Request (For Claude)
Please review this proposed architectural pivot. Does decoupling language translation from paradigm interpretation through a literal Python IR align with your goals for the PseudoCoup transpilation pipeline? Do you foresee any roadblocks in building the Kotlin-to-Literal-Python parser using the existing `tree-sitter` bindings?
