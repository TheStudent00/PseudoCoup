# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

The whole foundation now LOADS — all 254 files (87/87 UI, 167/167 non-UI), every gate green. UI was never a
transpiler problem; it just needed the wrapper floor. The remaining UI work is making the inert stubs DO
something (render), which is kit-wiring, not transpiler work.

- [ui] Make one screen RENDER — wire the autostub stubs to the PseudoUI kit (Compose `Column`/`Text`/`Button` → kit primitives) + the reactive bridge (`collectAsState`/`remember` → kit re-render). Bring up a single screen on the kit, validate against the ledger, then scale. This is rungs 3–4 for the UI.
- [transpiler] AST-kind-aware stub generation (your refinement) — tag each external name from the AST as {module / class / function / attribute} and shape the stub to match (instead of one permissive Stub for all). Better structural fidelity + cleaner refine-to-real. The permissive floor stays as the fallback.
- [domain] Broaden runnable coverage — point the oracle at more repositories / use-cases / unit tests. Running real code is what surfaced every recent bug (braceless loops, nested-lambda, forward-ref defaults). High yield, low risk.
- [multi-target] `@<target>_extern` tag drives the per-language wrapper registry — declare an external once, resolve it per target (PseudoCoup-side).

Recently shipped:
- Auto-stub floor (your design): one front door (`runtime/autostub.py`) binds EVERY external name — real wrapper → Python builtin → inert Stub. ALL 254 files load (87/87 UI, was 0), zero NameErrors. Real wrappers + stubs are one system; the stub inventory is the visible "inert" list; non-UI platform/DI glue blessed as real no-ops so extern stays honestly 0.
- Stragglers en route: LocalDate.EPOCH, R resources, fully-qualified extension receivers (`_strip_pkg`), top-level const hoist + nested-class-default late-binding (forward-ref defaults), abs→builtin.
- Before that: the full instrumented data-layer suite (4/4: backup + migration) and the receiver-lambda / `$name` transpiler fixes.
