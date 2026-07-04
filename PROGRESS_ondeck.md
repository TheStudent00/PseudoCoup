# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

The app RUNS in Python (boots, navigates by real buttons, real db) and the LAYOUT-FIDELITY instrument is
live: the real Compose engine (Robolectric, headless) and the kivy kit both dump every component's box;
`layout_diff.py` compares them as %-of-display within a tolerance band. That number is now a measured
gauge on this board — the continue/shutdown instrument.

- [fidelity] LogCardio: the ~140px block between "Duration" and "Intensity" — a custom stepper control (CompactControls) renders ~2.5x taller than compose; probe its widget chain (the M3 56dp text-field rule landed but this block isn't a bare text field). Drives the uniform 12.9% drift on 6 components below it.
- [fidelity] LogCardio chip line-break off by one chip (Sport) — cumulative chip-width drift moves the wrap point; likely the SELECTED chip's leading checkmark (Run is selected; compose adds ~26px my tree doesn't have).
- [fidelity] "Notes (optional)" MISS — an OutlinedTextField label slot that never emits; find which slot lambda is swallowed.
- [fidelity] Exercises "No exercises found" — Box(contentAlignment=Center) child not centering (x 5.8 vs 34.3).
- [fidelity] GymList 7th: Delete-gym in-button anchoring still Δ>3 — revisit with button-box ground truth.
- [fidelity] Add Settings/Today to LayoutDumpTest (deeper VM chains — mirror di.py's assembly).
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
