# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

The app RUNS in Python (boots, navigates by real buttons, real db) and the LAYOUT-FIDELITY instrument is
live: the real Compose engine (Robolectric, headless) and the kivy kit both dump every component's box;
`layout_diff.py` compares them as %-of-display within a tolerance band. That number is now a measured
gauge on this board — the continue/shutdown instrument.

- [fidelity] FlowRow line-wrapping — LogCardio's dominant cause: chips run off-screen in ONE row (kivy x to 167% of display); Compose wraps to new lines. Kit: implement wrap layout for FlowRow/FlowColumn.
- [fidelity] Text soft-wrap at the max-width constraint — wrap-width labels grow unbounded (the LogCardio intro is 171% wide); Compose wraps text at the incoming max width. Same family as the constraint-propagation rule.
- [fidelity] SearchBar (+ any container still in compose_ui's inert list) swallows its content lambda — Exercises' tabs/search never enter the TREE (recorder-level, not kit). Audit _NAMES for containers that take content.
- [fidelity] GymList 7th: M3 in-button anchoring refined (content-group centering landed; Delete-gym still Δ>3) — revisit with the button-box ground truth (compose dumps Role=Button boxes; differ could pair those too).
- [fidelity] Add Settings/Today to LayoutDumpTest (deeper VM chains: BackupRepository/TodayViewModel — mirror di.py's assembly).
- [ui] Paint layer — colors/cards/icons are not drawn yet (geometry first, then paint). Even perfect geometry looks unlike the original until this lands.
- [ui] Popups render inline — DropdownMenu items should be hidden until opened (Settings overlaps).
- [ui] Scaffold innerPadding inset + Modifier order (padding-before-size vs after) — minor, after the big rows.
- [transpiler] .kt line map — emit a py-line→kt-line sidecar during generation so the layout inspector links each component to its exact Kotlin line (it has file-level links today).
- [domain] Broaden runnable coverage — point the oracle at more repositories / use-cases.

Recently shipped:
- Layout-fidelity instrument: LayoutDumpTest (real Compose boxes, headless JVM) + inspect_layout JSON + layout_diff (%-of-display, tolerance band) → per-screen fidelity %, now a measured gauge (`fidelity.py`).
- Layout inspector (`layout_inspect/*.html`): per component — the code line that created it (file:line, .kt path) ‖ declared shape ‖ live computed box.
- Compose measure/place reconstructed on Kivy: wrap-by-default, Box z-stack, arrangement spacers, Scaffold slot framing + FAB float, fill-vs-scroll reconciliation, weight-on-parent-axis, top-pack columns (Kivy bottom-packs spare space — measured), M3 type scale + TopAppBar/icon-button spec geometry, `then`-chain splicing, Spacer(weight).
- Theme tokens live: real CompositionLocal — WflTheme.tokens.* resolve to real dp values (24 files move together).
