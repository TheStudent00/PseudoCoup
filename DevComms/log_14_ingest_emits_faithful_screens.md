# log_14 — the ingest transpiler now emits faithful, widget-backed screens (Step 3 done) + the cleanup backlog

Date: 2026-06-24
Type: status + backlog. Records the state after Steps 3a/3a'/3b/3c so it survives a compaction
and feeds verification.

## Bottom line

- The Kotlin/Compose → PseudoCoup ingest transpiler (`WFL_PseudoCoup/tools/ingest/ingest.py`)
  now **emits faithful, widget-backed PseudoCoup for all 30 screens**. Every emitted screen
  PARSES as Python and its `build()` EXECUTES against the real `ui/widgets.py` (290 widget
  call-sites, 0 arity mismatches).
- The emit is driven by an evidence-derived vocabulary: **34 new `widgets.py` functions** +
  the `define_layer` / `define_progress` primitives, built from the 30-screen flag harvest.
- The differ mechanically enumerated the interpretation gaps in the hand-written screens —
  the original thesis, now proven per-screen.
- A real **cleanup backlog** remains (impedance mismatches + small mapping gaps). Listed below.
- Still pending: **Step 4** (nav/wiring resolution from `AppNavigation.kt`) and **Step 5**
  (full verification: oracles / smoke / analyze / goldens / live 2-way).

## What was built (Steps 3a–3c)

```
3a  harvest: ran the mapper over all 30 → flags aggregated → triaged work list. HARVEST.md.
3a' mapper hardening: vocabulary→existing primitives, noise-skip (let/effects),
    control-flow descent (AnimatedContent/AnimatedVisibility). 30/30 mapped clean, 0 gaps.
3b  shared infra: define_layer + define_progress in BOTH kits; 34 widgets.py functions across
    4 verified batches (widgets.py 68 fns, theme 337 tokens). transpile clean, SWEEP 30/30.
3c  wiring: MappingTable.KNOWN_CUSTOM = a param-plan table mapping each custom @Composable to
    its widget + per-param arg recovery. emit mode re-runs all 30 → <screen>.py/.flags.md/.diff.md
    under build/ingested/.
```

Three design calls settled: `switch_row` composed from existing primitives (no toggle
primitive); charts approximated (confirmed the kit has NO arc API — `define_canvas_zone` is a
scatter surface); `SwipeToDismissBox` deferred.

## Coverage (Step 3c emit)

- 261 custom call-sites → **199 mapped to a widget**, 62 flagged: specific named modals w/ no
  dedicated widget 27 (DayExercisesDialog, PlateCalculatorSheet, SwapExerciseDialog, …),
  genuinely-unknown 19, needs-primitive 12 (the progress indicators — see backlog), needs-widget 4.
- Param-level flags on mapped widgets: 42 runtime-list/template, 157 non-literal scalar — the
  honest cost of wiring runtime-data composables; never guessed.

## The payoff — interpretation gaps the differ surfaced (across 30 .diff.md)

- **single row-template vs hand while-loop (×28)** — hand screens drive real service-data loops;
  ingest faithfully emits one flagged template (never unrolls runtime data).
- **HorizontalDivider dropped by hand (×10)** — blueprint draws dividers the hand screens omit.
- **top-bar back-affordance divergence (×7)** — hand screens invent or drop an `on_back` vs the
  blueprint's `navigationIcon` (settings invents one; today drops one the blueprint has).
- **text field dropped by hand (×4)**; custom composables hand-built vs flagged (×2).

## Cleanup backlog (Step 3c')

Impedance mismatches (widget signature vs how Compose calls it — found, not hacked):
1. `ConditioningTimerView → conditioning_timer_view` — Compose passes one `state` object; the
   widget wants 5 flat params (all fields of state). Needs a state→params adapter.
2. `AlertDialog → confirm_dialog` — confirm/dismiss labels live in nested
   `confirmButton={TextButton{Text("Delete")}}` lambdas, not flat args; currently defaulted
   "OK"/"Cancel"/danger=False. Needs nested-button-label + danger recovery.
3. `ListItem → list_item` — Compose `trailingContent` is an IconButton; widget `trailing` is a
   glyph string, so the affordance is dropped.
4. `StatCard → stat_card` — Compose `StatCard` is ONE tile; the widget is a parallel-list ROW.
   Each call emits a 1-tile row, not the N-tile row the hand screen builds. (Widget likely
   should be a single tile; the row is the screen's loop.)
5. `WelcomeBackBanner` / `WinsHomeCard` bake fixed body copy internally; not blueprint-sourced.

Small mapping gaps:
- Section-header LABEL not recovered — `section_header_collapsible(..., "", ...)` emits an empty
  label (count/expanded correctly flagged). The literal section labels ("Notifications", …)
  should be recovered.
- `CircularProgressIndicator`/`LinearProgressIndicator` → still flagged `needs primitive`, but
  `define_progress` now EXISTS — wire them to it.
- `PrimaryScrollableTabRow`/`TabRow` → `tab_row` exists — wire it (was omitted from the
  correspondence list).

Manual, no blueprint signal:
- `settings_notifications_screen` and `you_screen` both back onto the ONE `SettingsScreen.kt`;
  the section split (which rows belong to which hand screen) is a hand decision the tool can't
  derive — emitted screens currently carry the whole SettingsScreen.

## Fidelity notes banked

- Palette gap: WFL theme's tertiary/secondary *container* colors were dropped from the PseudoCoup
  palette; pr_card / banners map to closest existing roles. Re-adding the constants is a small
  faithful theme-completion.
- `define_layer` "trigger" anchor pins top-right in v1 (retained tree carries no zone geometry).
- Charts (wins donut, conditioning timer ring) approximated — the one accepted fidelity gap.
