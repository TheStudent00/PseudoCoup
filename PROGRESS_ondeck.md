# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

The foundation LOADS (all 254 files) and now RENDERS: a headless Compose runtime turns transpiled Kotlin
screens into UI trees — 17/29 screens render (LogCardioScreen = 82 nodes), all gates green. UI was never a
transpiler problem; it needed the wrapper floor + a Compose stand-in (the room.py move).

- [ui] Clear the render long-tail — the ~12 non-rendering screens are mostly receiver-lambda builders (`buildString`/`buildList` — extend the apply/with/run support) + a few harness artifacts (Stub passed for a param the screen does arithmetic on — real calls pass real args). Push render OK toward 29/29.
- [ui] Reactive bridge + styling — `collectAsState`/`remember` → real state that drives re-render (today they stub, so state-branching bodies render thin); thread `Modifier`/colors through the tree. This is rungs 3→4 for the UI.
- [ui] Point the tree at a pixel kit — the headless tree is neutral; render it on the PseudoUI Flutter/Kivy kit for actual pixels + goldens. (Architecture call.)
- [transpiler] AST-kind-aware stubs (your refinement) — tag each external name by kind from the AST; shape the stub to match. Permissive floor stays the fallback.
- [domain] Broaden runnable coverage — point the oracle at more repositories / use-cases. Running real code keeps surfacing real bugs.

Recently shipped:
- Headless Compose (`runtime/compose.py`): a `@Composable` emits a UI tree; registered so autostub serves Column/Text/Button real and stubs styling. Transpiled ReportForm → full form (intro, fields, 3 live BugSeverity buttons, Send). 17/29 screens render.
- Auto-stub floor: one front door binds every external (real → builtin → inert stub); ALL 254 files load (87/87 UI, was 0). Platform/DI glue blessed real so extern stays 0. UI-load is now a measured gate.
- Transpiler fixes the render surfaced: Unit, inline fully-qualified-ref collapse, qualified extension receivers, const-hoist + nested-class-default late-binding.
