# On-deck — next sub-tasks

Edit this list freely; `track.py render` folds it into PROGRESS.html / .md. Format: `- [area] task — why/where`.
Top of the list is what's next.

The app RUNS in Python (boots, navigates by real buttons, real db) and the LAYOUT-FIDELITY instrument is
live: the real Compose engine (Robolectric, headless) and the kivy kit both dump every component's box;
`layout_diff.py` compares them as %-of-display within a tolerance band. That number is now a measured
gauge on this board — the continue/shutdown instrument.

- [fidelity] 128/128 -- ALL 10 measured screens at 100% (+WinsList with a seeded win card, +Progress via the first sanctioned Kotlin adjustment: winsViewModel threaded through ProgressScreen so a non-Hilt host can supply it, runtime default unchanged). Two specimen gates guard derived metrics. Next: LogWorkout, Onboarding (CrashlyticsBridge stand-in), a seeded program (Programs/Today populated lists).
- [fidelity] The ONE sanctioned non-general bridge: small-text (<=12sp) widths get a 1.035 shaper calibration (the ground-truth engine measures small text wider than the font file itself — measured on the specimen against two fonts; user-approved as engine-specific). Everything else remains general.
- [fidelity] SPECIMEN gate is live in fidelity.py (synthetic, not counted, fail-loud): the text-metric rules (natural single-line stacking; letterSpacing widths) are DERIVED from dumpSpecimen. Extend it when a new metric question appears — never infer from mixed app screens.
- [ui] Paint layer — colors/cards/icons are not drawn yet (geometry first, then paint). Even perfect geometry looks unlike the original until this lands.
- [ui] Popups render inline — DropdownMenu items should be hidden until opened (Settings overlaps).
- [ui] Scaffold innerPadding inset + Modifier order (padding-before-size vs after) — minor, after the big rows.
- [transpiler] .kt line map — emit a py-line→kt-line sidecar during generation so the layout inspector links each component to its exact Kotlin line (it has file-level links today).
- [domain] Broaden runnable coverage — point the oracle at more repositories / use-cases.

Recently shipped:
- History renders a real session card, byte-identical text to compose — the instrument caught 4 CONTENT bugs: Kotlin printf-format (.format/String.format) transpiled to brace-format (silent template passthrough), TemporalAdjusters stubbed (week starts wrong), java date patterns' quoted literals mangled ('at' -> 'AMt'), and Int32 overflow inside timedelta (plusDays(6) == -1 day). All fixed in transpiler/runtime; 254/254 regenerated.
- 4 of 5 screens at/near-perfect: GymList 7/7, LogCardio 23/25, Exercises 7/7, Today 3/3; Settings 22/44. One session took the gauge 24/39 → 62/86 (5 screens) via: M3 slot order, class heights/insets, real line-height stacking (app Typography honored end-to-end), popups excluded from layout, harness renders inside the app theme, loader same-package shadowing (Kotlin visibility), real Font/FontFamily + variable-font weight instancing, off-viewport differ rule.
- Input fields render their slot subtrees: a node with text AND children is a field container (value as child label), not a leaf — one fix removed the 100px stepper block AND the "Notes (optional)" MISS. BasicTextField dropped from the 56dp rule (it's foundation, undecorated); empty Box collapses instead of Kivy's 100x100 default. Save Δ26.9→0.2.
- Layout-fidelity instrument: LayoutDumpTest (real Compose boxes, headless JVM) + inspect_layout JSON + layout_diff (%-of-display, tolerance band) → per-screen fidelity %, now a measured gauge (`fidelity.py`).
- Layout inspector (`layout_inspect/*.html`): per component — the code line that created it (file:line, .kt path) ‖ declared shape ‖ live computed box.
- Compose measure/place reconstructed on Kivy: wrap-by-default, Box z-stack, arrangement spacers, Scaffold slot framing + FAB float, fill-vs-scroll reconciliation, weight-on-parent-axis, top-pack columns (Kivy bottom-packs spare space — measured), M3 type scale + TopAppBar/icon-button spec geometry, `then`-chain splicing, Spacer(weight).
- Theme tokens live: real CompositionLocal — WflTheme.tokens.* resolve to real dp values (24 files move together).
