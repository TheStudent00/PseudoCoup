# log_77 — PLAN: the WFL Kotlin→Python transpiler (built on what we've already shipped)

Date: 2026-06-27
Type: PLAN (for review before any code). Nothing here discards the py2many thread —
it consumes its outputs. This is the convergence step, not a restart.

## 0. What we have already built (the inputs to this plan — not thrown away)

1. **A validated construct-equivalence table (Kotlin↔Python).** Two halves:
   - *Declarative spine* — harvested straight from py2many source (`extract_table.py`):
     primitive types, containers, stdlib-fn dispatch, for 10 languages on a Python
     pivot. (`equivalence_table.md`)
   - *Structural mappings* — compile-verified via the atlas + gate: if/for/while/
     ternary/class+ctor/comprehension/tuple/nullable/enum/dataclass/default-args/
     type-aware-`len`. 20/20 atlas constructs compile; **26/27 of py2many's own
     supported Kotlin cases compile** with our patched backend.
2. **The anti-slop oracle (compile gate).** `gate.py`/`run_atlas.sh`/`run_corpus.sh`:
   transpile → compile → the compiler is truth, not the read-through. This caught
   bugs eyeballing missed (val-param reassignment, the `Union` return inference).
3. **A measured map of py2many's ceiling** (log_76): no async/exceptions/`with`/
   generators/dict-comp; a known stdlib long-tail. So we know exactly which
   constructs the table already covers vs which we must author + verify ourselves.
4. **The literal transpiler** (`tools/transpiler/literal_transpiler.py`, Kt→Py):
   192/254 WFL files compile today. Its handler *logic* is real and reusable; only
   its *dispatch* (a flat if-chain) and its *emit-and-hope* contract are the problem.

The table is the **spec**, the gate is the **verifier**, py2many is the **reference
data generator**, the literal transpiler is the **donor**. This plan wires them
into one disciplined transpiler.

## 1. Goal and the single "done" indicator

`WFL_MixingCenter` = a faithful, complete **1:1 Kotlin→Python** of WFL.

**Done = the WFL test oracle passes on the transpiled Python, across the whole app:**
transpile WFL's code *and* its tests, run both sides, the results match. That is the
*only* real done indicator — it subsumes coverage (an un-transpiled or wrong file
fails its tests) and correctness (compiling ≠ correct). Compile-clean is an
intermediate checkpoint, not "done."

Correction to my earlier wording: `— no Kotlin source —` in the sidebyside is **not**
a done-condition. It is a standing project **invariant** — nothing may exist on the
Python side without a Kotlin origin — so it is never violated in the first place.
Citing it as a finish line was wrong.

## 2. The two flaws we are removing (from log_71/TRANSPILER_SCOPE, already diagnosed)

- **Flaw 1 — dispatch keyed on node TYPE only, not (TYPE + child structure).**
  `navigation_expression` emits `f"{left}.{right}"` for everything, so `16.dp`
  (number receiver) produces invalid Python. The handler never looks at the child.
- **Flaw 2 — emit-and-hope.** Handlers emit hopeful text nothing validates; only a
  *missing* handler is loud. Over-general handlers ship broken Python silently.

The fix is an architecture, not a patch: **map · wrap · fail, dispatched by a
visitor, guaranteed exhaustive by a coverage test.**

## 3. The build — `tools/pseudokotlin/` (under PseudoCoup; the umbrella already owns the K→Py transpiler)

Architecture (the rigor asked for — replaces the if-chain, **reuses the donor's logic**):

```
tools/pseudokotlin/
  parse.py            tree-sitter-kotlin -> CST (the truth)
  dispatch.py         visitor core: getattr(self, "v_"+node.type); unknown -> wrap/fail
  nodes/              one file per concern; each handler a tested v_<kind> method,
                      ported deliberately from literal_transpiler, made structure-aware
  wrap/registry.py    curated Kotlin-construct -> Python-shim table (.dp, Flow, ...)
  wrap/runtime/       the shim libs (core/units.py, core/flow.py, ...)
  tests/test_coverage.py   asserts ALL 116 grammar node kinds are classified
  tests/test_nodes.py      per-construct goldens (seeded from the verified table)
  tools/coverage.py        ported instrument (drop counts -> 0)
```

Three contracts, enforced:
1. **Visitor dispatch** — `v_<node.type>`, one small method per kind. No flat if-chain.
2. **Coverage test** — the compiled grammar enumerates 116 named node kinds; the test
   asserts each is one of {handled, container/trivia, routed-to-wrap, out-of-scope}
   and **fails otherwise**. This is the exhaustiveness guarantee (OCaml-match analog).
3. **map · wrap · fail** — a handler either maps to Python it can *guarantee* parses,
   or wraps into a shim when Kotlin has no Python equivalent (`16.dp` → `dp(16)`),
   or fails loudly. Never emit-and-hope.

## 4. How each existing asset plugs in (so nothing is re-derived)

- **Per-handler target output comes from the verified table**, not guesswork. The
  table says Kotlin `for (i in 0..n-1)` ↔ Python `for i in range(n)`; that pair is
  the golden for `v_for_statement`. Where the table is silent, we author + gate it.
- **py2many stays the reference generator + round-trip check**: transpile WFL Kt→Py
  with PseudoKotlin, then Py→Kt with patched py2many, compile — a cross-check that
  the Python is structurally faithful, on top of the WFL test oracle.
- **The donor supplies handler logic**: each `parse_expression`/statement branch is
  ported one node at a time into a `v_<kind>` method, fixing Flaw 1 (look at child
  structure) and Flaw 2 (guarantee or wrap) as it moves.
- **The gate is the acceptance test** at every step (no construct lands un-compiled).

## 5. Phases (each ends green; incremental, not a big-bang rewrite)

- **P0 — spine + safety net.** parse.py, dispatch.py, the 116-kind coverage test
  (initially everything classified "unhandled→fail"), ported coverage.py. Deliverable:
  the test runs and lists exactly what's unhandled. *No behavior yet — just the net.*
- **P1 — routine tier (already table-verified).** Port handlers for the constructs the
  atlas/corpus already proved: literals, arithmetic/bool/compare, if/when→if-expr,
  for/while, functions, classes+ctor, calls, navigation **(structure-aware: `16.dp`→
  wrap)**, returns, assignments, comprehensions, tuples, nullable. Gate: re-transpile
  the WFL files that already compile and hold the count; coverage drops → 0 for these.
- **P2 — close the 62 WFL failures.** Drive by the actual failing files (not guesses);
  each failure is one unhandled/over-general node → add/repair its `v_<kind>` against
  the table, gate it. Deliverable: WFL_MixingCenter compile count 192/254 → 254/254.
- **P3 — the wrap layer (the hard WFL idioms py2many can't do).** `.dp`/`.sp` units,
  Compose `@Composable` DSL, coroutines/Flow, Android/Hilt — into `wrap/registry.py`
  + shim runtime. These have no Python equivalent; they wrap, they don't reconstruct.
- **P4 — correctness, not just compile.** Run the WFL test oracle (code+tests both
  sides) to catch semantic slop the compiler can't. This is the real bar.

## 6. What this plan explicitly is NOT

- NOT a fresh start that discards py2many — it consumes the table, the gate, and the
  ceiling map. Those are the foundation.
- NOT a throwaway of the literal transpiler — its handler logic is the donor, ported
  deliberately; only the loose dispatch + emit-and-hope are replaced.
- NOT hand-translated slop — every landed construct is gated (compile) and ultimately
  oracle-checked (tests), exactly the discipline we already built.

## 7. Genuine open question (one, real)

The **wrap-layer scope** (P3) is the only place with real design uncertainty: how far
to model Compose/coroutines as runnable Python shims vs. as faithful-but-inert
structure. That decision needs the P2 data (what WFL actually leans on, by frequency)
before it can be made well — so it is deliberately deferred to its own log after P2,
not guessed now.

## 8. PseudoCoup internal cleanup — DONE (2026-06-27)

(The `~/Programming` ecosystem reorg is a separate problem, deferred — not in scope.)

**Executed:** the old mapping subsystem (`interactive_map/`, `runtime_uimap/`, `uimap/`,
`run_mapper.sh`, `tools/connectivity/`, `tools/dynamic_mapper/`) + the two stale root
docs moved to `_deprecated/` (self-documented by `_deprecated/README.md`).
`TRANSPILER_SCOPE.md` → `docs/`. The license PDF → `LICENSE.pdf`. `.pytest_cache/`
gitignored; stray committed `.pyc` dropped. **Correction made during execution:** `core/`
is NOT sandbox — it's the live Flow/coroutine shim runtime the transpiler emits, so it
stayed. Active `tools/` is now just `transpiler/` + `py2many_kotlin/`. Root markdown is
now only `README.md` + `PROJECT_MAP.md`. Smoke-checked: transpiler still imports, `core/`
resolves. The proposal that drove this is preserved below.

### The rule (the thing I violated)
**One home per kind of file, no floaters:**
- **Markdown logs / decision / handoff / protocol / concept docs → `DevComms/` only.**
  Nothing log-like at the repo root or scattered in tool dirs. (I broke this; fixing it.)
- **Specs** (`TRANSPILER_SCOPE.md`) → a `docs/` folder.
- **Repo entry docs** (`README.md`, `PROJECT_MAP.md`) → root, and only those two.
- **A tool's own `README.md`** → co-located in that tool's dir (a tool readme is not a
  log). Generated artifacts (e.g. `equivalence_table.md`) → the tool dir, gitignored if
  regenerable.
- **Generated / cache** (`build/`, `.pytest_cache/`) → gitignored, never committed.

### Current mess (measured)
- Root floaters that are really logs: `connectivity_audit_results.md`,
  `implementation_plan.md` → belong in `DevComms/`.
- `.pytest_cache/README.md` is committed (junk) → gitignore.
- Old **mapper sandbox** at root: `core/`, `interactive_map/`, `runtime_uimap/`,
  `run_mapper.sh`, `uimap/` (each carrying stray `.md`) → dead weight.
- `OTU GREEN LICENSE FOR UNIVERSAL WORKS.pdf` at root (mystery solved — a license PDF).
- DevComms has two `log_29` and two `log_38` (duplicate numbers). Logs are an
  append-only ledger, so I will NOT renumber history — just noting the collision.

### Proposed tree
```
PseudoCoup/
├── README.md  PROJECT_MAP.md         # the only markdown at root
├── LICENSE.pdf                       # the renamed "OTU GREEN LICENSE..." PDF
├── DevComms/                         # THE markdown home: all logs + protocol/handoff/
│                                     #   concept docs + the two relocated root docs
├── docs/                             # specs (not logs): TRANSPILER_SCOPE.md
├── tools/
│   ├── transpiler/                   # literal Kt→Py engine — the DONOR
│   ├── pseudokotlin/                 # disciplined Kt→Py transpiler — NEW (P0 onward)
│   └── py2many_kotlin/               # Py↔Kt table + gate (README co-located = fine)
├── uimap/                            # oversight render — sidebyside.html  [IF active]
├── build/                            # generated; gitignored
└── _deprecated/                      # the dead mapper sandbox — frozen, not deleted
    ├── core/  interactive_map/  runtime_uimap/  run_mapper.sh
    └── connectivity_audit_results.md (if stale)
```
Plus: add `.pytest_cache/` to `.gitignore`.

### Two real confirmations before I move anything
1. **`uimap/`** — is it the *live* oversight render (the sidebyside artifact you view),
   or old-mapper residue? If live, it stays; if dead, it joins `_deprecated/`.
2. **`tools/connectivity/`** and **`tools/dynamic_mapper/`** — active, or part of the
   dead mapper sandbox (→ `_deprecated/`)?

Everything else above is unambiguous. On your answer I do one scripted `git mv` pass,
logged, then update PROJECT_MAP.md to match.

## 9. First actions (independent — either can go first)

- **Cleanup:** the scripted `git mv` pass above, once you answer the two confirmations.
- **Transpiler P0:** scaffold `tools/pseudokotlin/` — parse.py + dispatch.py + the
  116-kind coverage test wired to fail-loud + ported coverage.py. The safety net and
  the exact unhandled-node worklist, before a single handler is written.
