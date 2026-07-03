# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

The app RUNS in Python (boots, navigates by real buttons, real db) and the LAYOUT-FIDELITY instrument is
live: the real Compose engine (Robolectric, headless) and the kivy kit both dump every component's box;
`layout_diff.py` compares them as %-of-display within a tolerance band. That number is now a measured
gauge on this board — the continue/shutdown instrument.

- [fidelity] Rows not going full-width — the three big GymList FAILs share one signature (title width, chip x, Delete-gym x all pack left): fillMaxWidth isn't landing on some card rows. One cause; find it in the kit/recorder, never per-screen.
- [fidelity] Extend LayoutDumpTest to more screens (Settings, Today, LogCardio) once GymList climbs — each screen needs its fixture seeded identically on both sides.
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
