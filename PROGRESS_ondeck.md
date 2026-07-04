# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

The app RUNS in Python (boots, navigates by real buttons, real db) and the LAYOUT-FIDELITY instrument is
live: the real Compose engine (Robolectric, headless) and the kivy kit both dump every component's box;
`layout_diff.py` compares them as %-of-display within a tolerance band. That number is now a measured
gauge on this board — the continue/shutdown instrument.

- [fidelity] LogCardio chip line-break off by one chip (Sport) — cumulative chip-width drift moves the wrap point. NOT the selected chip's checkmark (measured: compose's selected "Run" text starts at the same x as unselected chips); it is kivy's font running slightly wider per chip (Elliptical 14.1% vs 12.9%) until the last chip tips over. Needs a font-metric answer, not a per-chip constant.
- [fidelity] LogCardio residual: 7 components sit 0.2–1.0% OUTSIDE the ±3% band — small per-block y accumulations (a few px at each label/spacer/button boundary), no single dominant cause left.
- [fidelity] Exercises "No exercises found" — Box(contentAlignment=Center) child not centering (x 5.8 vs 34.3).
- [fidelity] GymList 7th: Delete-gym in-button anchoring still Δ>3 — revisit with button-box ground truth.
- [fidelity] Add Settings/Today to LayoutDumpTest (deeper VM chains — mirror di.py's assembly).
- [ui] Paint layer — colors/cards/icons are not drawn yet (geometry first, then paint). Even perfect geometry looks unlike the original until this lands.
- [ui] Popups render inline — DropdownMenu items should be hidden until opened (Settings overlaps).
- [ui] Scaffold innerPadding inset + Modifier order (padding-before-size vs after) — minor, after the big rows.
- [transpiler] .kt line map — emit a py-line→kt-line sidecar during generation so the layout inspector links each component to its exact Kotlin line (it has file-level links today).
- [domain] Broaden runnable coverage — point the oracle at more repositories / use-cases.

Recently shipped:
- Input fields render their slot subtrees: a node with text AND children is a field container (value as child label), not a leaf — one fix removed the 100px stepper block AND the "Notes (optional)" MISS. BasicTextField dropped from the 56dp rule (it's foundation, undecorated); empty Box collapses instead of Kivy's 100x100 default. Save Δ26.9→0.2.
- Layout-fidelity instrument: LayoutDumpTest (real Compose boxes, headless JVM) + inspect_layout JSON + layout_diff (%-of-display, tolerance band) → per-screen fidelity %, now a measured gauge (`fidelity.py`).
- Layout inspector (`layout_inspect/*.html`): per component — the code line that created it (file:line, .kt path) ‖ declared shape ‖ live computed box.
- Compose measure/place reconstructed on Kivy: wrap-by-default, Box z-stack, arrangement spacers, Scaffold slot framing + FAB float, fill-vs-scroll reconciliation, weight-on-parent-axis, top-pack columns (Kivy bottom-packs spare space — measured), M3 type scale + TopAppBar/icon-button spec geometry, `then`-chain splicing, Spacer(weight).
- Theme tokens live: real CompositionLocal — WflTheme.tokens.* resolve to real dp values (24 files move together).
