# log_137 — PLAN: one ledger, EVERYTHING TRACKED (id born on the Kotlin side via tree-sitter, emitted at runtime, carried through transpile)

Date: 2026-07-09
Type: plan (design). No code changed yet. Supersedes the boundsKey identity direction — see end.

## The one cause, the one fix

CAUSE: identity is RECONSTRUCTED after the fact. The walker guesses which node it is looking at from
`(label, handlerKind, boundsKey)` at fire time (`WalkRecorderTest.kt:591`), and the ledgers reconstruct the
Python side by exec-introspect (`ledger.py`) and runtime-trace (`kit_ledger.py`) — even though we AUTHOR the
Python side. Every downstream symptom (ambiguity, the `ProgramCard ×2` hand-record, the 664017d
discard-on-ambiguous saga) is a symptom of guessing.

FIX (one coordinated move across a named group): generate a unique id at the SOURCE via tree-sitter, inject
`emitId` calls into the Kotlin source, transpile so BOTH sides carry it, and match on the emitted id. The
group that moves together: { new id generator, new `emitId` injection pass, the three ledgers collapse into
one, `resolveTarget` becomes an id lookup }.

Pipeline in order (the correction from our discussion — id is born on the Kotlin side, NOT minted by the
transpiler):

    tree-sitter -> unique id per Kotlin node
        -> inject emitId(id, instanceKey) into the Kotlin source
            -> transpile Kotlin->Python (emitId + ids ride along for free)
                -> both sides emit at runtime
                    -> one ledger; walker matches on the id

## Decisions that are yours (I will NOT pick these — §6)

- The id string shape (how the branch path + per-instance key are encoded).
- Where the id generator runs (standalone, or inside the ledger — you said arbitrary; pick one).
- What counts as "an object" to track — the full set for EVERYTHING IS TRACKED (composables + functions +
  engine methods + data holders?).
- The single ledger's record schema (the superset) and its on-disk form + name.
- Names: `emitId`, the ledger module, the id generator.
Names below marked (name TBD) are placeholders, not proposals.

## Phases (each independently verifiable)

PHASE 1 — id generator, Kotlin side, tree-sitter.  (name TBD)
  The branch-path walk already exists: `ui_ledger.py:264 render_node` builds `full = "/".join(path + [seg])`
  down the tree. Two changes:
    (a) FIX `_segment` (`ui_ledger.py:238`) to carry the child index at EVERY node unconditionally, not only
        as a fallback when there is no content anchor — this is the exact line that breaks uniqueness today
        (log_136 Finding 2). Then siblings never collide.
    (b) extend the walk ABOVE the composable boundary so ONE tree covers module -> class -> function ->
        widget. Today `ledger.py` stops at the frame and the UI ledgers pick up inside it (log_136); this
        removes that seam.
  Output: { kt source node -> unique id }.
  VERIFY: assert NO duplicate id across the whole tree. That assertion has never existed; it is the proof of
  uniqueness you have been asking for.

PHASE 2 — inject emitId into the Kotlin source.  (name TBD)
  For each tracked node, splice `emitId(id, instanceKey())` at the point the object is called — BEFORE the
  wrapped framework API if it is behind one. Source-position injection has precedent: `ledger.py:229 inject()`
  already splices tags into transpiled output by lineno. The instance key = emission order (the Nth time this
  id fires in a render pass), a runtime counter keyed by id — this is what distinguishes repeated renders of
  one source node (the list-of-identical-cards case).
  VERIFY: instrumented Kotlin still compiles; a smoke run emits a unique `(id, instance)` per LIVE node,
  including the repeated-sibling cases (`ProgramCard` list, `Text["30 min"]`).

PHASE 3 — transpile carries it.  (existing pipeline, `tools/pseudokotlin/build_mixingcenter.py`)
  Run the existing transpile. The `emitId` calls and their id literals ride into the Python side for free —
  no separate Python instrumentation.
  VERIFY: transpiled Python contains `emit_id` calls with the SAME ids; KT emit sites and PY emit sites
  correspond 1:1. That 1:1 IS the extra information to verify what-is-what — it replaces the hand-recorded
  correspondence `ledger.json` (log_62) entirely.

PHASE 4 — one ledger.  (name TBD; collapses `ledger.py` + `ui_ledger.py` + `kit_ledger.py`)
  Build a SINGLE ledger keyed by the unique id, one record per node, superset schema — UI fields simply stay
  empty for non-UI frames (your point: a non-UI object does not fill them). Built from the emit sites, not
  from exec-introspect or runtime-trace.
  VERIFY (the EVERYTHING-IS-TRACKED invariant, asserted): every emitted id has exactly one ledger entry;
  entry count == tracked-node count; zero untracked emissions; zero orphan entries.

PHASE 5 — walker matches on the id.  (`WalkRecorderTest.kt`)
  `InteractiveRef` / `PathStep` carry the emitted `(id, instance)` instead of `(label, handlerKind,
  boundsKey)`; `resolveTarget` becomes an id lookup — one match by construction, `Ambiguous` becomes
  impossible. `oracle_registry`'s non-unique coordinate key is retired for identity.
  VERIFY: re-run the walk (a 176-style host run). RESOLVE log shows zero identity-collision
  Ambiguous/Missing; kt coverage clears the ~21-state baseline instead of the 7 states 664017d produced
  (log_136, HANDOFF).

PHASE 6 — Python ledger as the cheap cross-check.  (optional; you flagged it as probably-good)
  Because both sides now carry `emit_id`, a Python-side pass just confirms KT emits == PY emits == ledger.
  Trivial by construction — the verification, not a second reconstruction.

## What this supersedes

The boundsKey re-fix line (b70d65e -> 664017d; HANDOFF top block, items 1 and 2) becomes moot: there is no
ambiguity left to discard, so discard-on-ambiguous has nothing to do. The queued budget-parity runs (item 2)
should wait for Phase 5, not for another boundsKey re-run.
