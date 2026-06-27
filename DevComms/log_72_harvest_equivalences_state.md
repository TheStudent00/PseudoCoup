# log_72 — state: harvesting Kotlin↔Python equivalences from existing transpilers

Date: 2026-06-27
Type: conversation-state capture (design thread). No production code changed; the work is
exploratory in `~/.../scratchpad/` until a sub-project is scaffolded. Continuation of log_71.

## The objective (stated correctly — earlier turns mis-framed it)

Build a **subsystem that mechanically harvests a construct-equivalence mapping between two
languages** by using existing transpilers as **data generators** (not by hand-authoring rules,
and NOT by Haxe "reading Kotlin" — Haxe never reads Kotlin in this design). For Kotlin↔Python:
fan a common source out to multiple targets via mature transpilers; the outputs are equivalent
by construction; extract the construct↔construct table from the aligned pairs. Generalizes to
any language pair joined by a transpiler path. Explicitly accepted: it won't cover the hard
idioms (Compose, coroutines, extension fns) — it bootstraps the routine bulk; the rest is
filtering/manual, verified by the WFL test oracle (slop = unverified, not hand-written).

NOTE for continuity: do not re-derive "Haxe can't read Kotlin" as an objection — it's
irrelevant; Haxe is a *fan-out data generator* here.

## Done already (earlier logs + this thread)

- **WFL_MixingCenter seeded**: full literal K→Py transpile of WFL (254 .py = WFL's 254 .kt,
  192 compile-clean), private GitHub repo `TheStudent00/WFL_MixingCenter`. (transpile_app.py)
- **Transpiler scope mapped**: `TRANSPILER_SCOPE.md` + `tools/transpiler/coverage.py`
  (116 grammar node kinds; visitor-dispatch + coverage-test + map/wrap/fail is the target
  architecture for a fresh `PseudoKotlin` sub-project; py2many's "typed-Python-as-IL" is the
  reusable idea; old `literal_transpiler.py` is a DONOR not a foundation). See log_71.

## The harvester — built and MEASURED (this thread)

- **Haxe IS installed**: `/home/lucas/Programming/PyHaxeUI/scratch/haxe/haxe` (4.3.6, std at
  `.../haxe/std`). It was a PATH miss earlier, not absent — do not re-litigate. JDK present at
  `/usr/lib/jvm/java-25-openjdk-amd64`.
- **`scratchpad/harvest.py`** — differential construct-harvester: per-construct minimal Haxe
  snippet → compile to Python AND Java → subtract the empty-program baseline (strips the
  constant Haxe runtime) → the remaining lines are that construct's representation in each
  target, with line-counts giving 1→N **cardinality tracking** (e.g. map 8→3, method 18→45).
- **Result (Python side, the goal output): 6 clean · 4 partial · 1 failed of 11 constructs.**
  Clean idiomatic Python for arithmetic, if/else, ternary, while, array, null-check (and the
  class/method body). Leakage is **located at Haxe stdlib boundaries** (map→`haxe_ds_StringMap`,
  string→`HxOverrides`, range→`python_lib_Random`+while-desugar, Math→`python_lib_Math`) →
  ~8 recognizable runtime tokens, filterable or mapped-once to native.
- **Asymmetry (quantified):** Python comes out clean; **Java comes out heavily Haxe-scaffolded**
  (`haxe.Log.trace.__hx_invoke2_o`, `extends HxObject`, `Runtime.eq`, `__hx_ctor__`). Since
  Kotlin = Java + J2K, the Kotlin column inherits that scaffolding — the matching-to-real-WFL
  limiter.

## The composition architecture (user's design + the one refinement)

Generate: Haxe→Python, Haxe→Java, Java→Kotlin(J2K). Build `Table_Py_J` (from Haxe fan-out) and
`Table_J_Kt` (from REAL open-source Kotlin↔Java, e.g. J2K on a real Java project or migration
git-history). Compose: `Table_Py_J ⋈ Table_J_Kt = Table_Py_Kt`.

**Refinement (real, not a blocker):** the two Java columns are different dialects — Haxe-Java
(scaffolded) vs real-Java (idiomatic) — so the join key must be the **abstract construct / an
IR**, NOT literal Java text (`__hx_invoke2_o` ≠ `println`). Normalize both Java columns to one
IR; join in IR space. Sourcing real Kotlin (vs Haxe-Kotlin) is what makes the idiomatic version
worth the abstract-join.

## py2many — two uses; measuring it FIRST (decided)

1. As the **typed-Python-IL pivot** for the join (Python→IL→Kotlin).
2. **More direct: py2many has a Python→Kotlin backend (beta)** — feed it a Python construct atlas
   → aligned Python↔Kotlin pairs with **no Haxe/Java detour**, possibly collapsing the whole
   pipeline. Caveat: beta quality, py2many-flavored Kotlin (same matching caveat).
**Decision: measure py2many's Python→Kotlin backend on the construct atlas first** — if decent,
it's the shortest path to `Table_Py_Kt`.

## Open items

- **J2K has no clean headless CLI** (IDE-coupled) — the one tooling gap for the J↔Kt leg if the
  py2many path doesn't pan out.
- Residual hard idioms (Compose/coroutines/extension-fns) — out of scope for harvesting; filter +
  WFL-test-oracle verify.
- Scaffold `PseudoKotlin` (visitor + coverage-test + map/wrap/fail) when we move from harvesting
  to the transpiler proper.

## Immediate next action
Run py2many's Python→Kotlin backend on the harvester's construct atlas; report output quality +
how much extracts cleanly (the number that decides direct-py2many vs the Haxe/J2K composition).
