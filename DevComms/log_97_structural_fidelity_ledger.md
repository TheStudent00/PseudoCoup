# log_97 — structural/connective fidelity ledger (the dropped concept, restored)

Date: 2026-06-27
Type: new tool (tools/pseudokotlin/ledger.py) + sample artifacts. Answers the concern raised
this session: the pseudokotlin pipeline proved the FUNCTIONAL half (oracle/fuzz) but had NO
structural-fidelity tracking — the ledger concept from earlier tracks (dualgraph object
correspondence; coverage tags) was not wired in. This restores it for Track B.

## What it is (agreed design)

Two artifacts per engine, built by comparing both sides:

1. **in-output TAGS** — a correspondence docstring injected into each FRAME (module, class,
   function/method) of the transpiled Python: the frame's own Kotlin equivalent, its
   divergence kind, and a compact attribute map. "Frames" carry docstrings; "smaller objects"
   (attributes / const fields) fold into their owning frame's docstring; locals untracked.
   → `ledger_sample/<Engine>.tagged.py` (valid Python — docstrings are inert).

2. **external LEDGER** (meta-data, separate file) — one record per object: Kotlin {name,
   1-degree connections} and Python {name, 1-degree connections}, with the divergence kind.
   → `ledger_sample/<Engine>.ledger.md`.

## Method (so the ledger is ground-truth, not a guess)

- **Kotlin shape**: read statically with tree-sitter (the source spec).
- **Python shape**: read by EXECing the transpiled module and introspecting the real objects —
  the same modules the oracle already runs. So enum entries (assigned outside the class body)
  and data-class / object const fields (set in `__init__`) are seen exactly as they exist at
  runtime, not approximated from the AST.
- **Connectivity**: 1-degree references derived from each side independently and compared. The
  Kotlin walk skips `user_type` nodes (type annotations, which Python drops) so the two sides
  are comparable; each frame's own nested types are excluded (they're contained, not peers).

## Divergence kinds it catches (silently introduced by the transpiler, now tracked)

| kind | Kotlin | Python |
|---|---|---|
| object→instance | `object Foo` | `class Foo` + `Foo = Foo()` |
| overload-split | `fun f` (×N) | `_f__0.._f__{N-1}` + `f` wrapper |
| extension-hoist | `fun Recv.f()` | top-level `def f` (off the receiver) |
| relocated vs dropped | ref in a companion | ref hoisted to another frame |

The **relocated-vs-dropped** distinction is the one that matters for the swap-in concern: a
1-degree connection is only **broken** if it's absent from the whole Python module. If it just
moved frames (e.g. a `companion object` catalogue hoisted to module scope — exactly what
PathDefinition does with its `GoalType`/`FocusArea` wiring), the connection is intact and the
ledger says **relocated**, not broken.

## Result (10 engines)

All 10 engine/model files: **0 dropped connections, 0 missing members.** Every object→instance,
overload-split, extension-hoist, and nested-type correspondence resolved; data-class and enum
fields matched (e.g. AutoregulationEngine: object→instance, 1 overload-split, 1 extension-hoist,
11 nested types, attrs 18/18, connectivity OK). PathDefinition correctly reports its companion
catalogue as *relocated*, not broken.

## Where this sits

This is the STRUCTURAL/CONNECTIVE half; the oracle + fuzz are the FUNCTIONAL half. Together
they are the "equivalent (structurally AND dynamically/functionally)" bar. Next iterations:
UI sizing/positioning (the `ui/` frames, when bucket 3 is in scope — the record schema already
reserves the field), and emitting the tags from the transpiler itself rather than post-hoc.
