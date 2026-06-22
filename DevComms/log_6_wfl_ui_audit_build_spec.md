# log_6 — WFL UI audit: the derived build spec

Date: 2026-06-22
Type: spec (derived from a read-only audit of `~/Programming/WFL`). This is the
component/capability/token target for finishing the kit before converting WFL. It
turns "which components and capabilities matter" from a guess into a measured list.
Pairs with log_5 (the conversion plan).

## Headline findings (some change the plan)

- **35 screens/sheets**, not 15-25. Feature areas: today, wins, history, progress,
  programs (6 screens — the densest), execution (6), cardio, exercises, gym, paths,
  onboarding, settings, debug, report, celebration.
- **WFL is flat + hairline + purple + true-black-dark** — and my kit's `card` already
  matches WFL's `WflCard` identity (flat fill, 1dp hairline border, **zero elevation**,
  12dp radius). The aesthetic is already close; the re-skin is mostly tokens, not a
  structural redesign.
- **No snackbars anywhere** — feedback goes through dialogs/sheets. Drop snackbar.
- **No Slider** (0 uses). I built `slider`; it's general-kit value but NOT WFL-needed.
  Same for `avatar`/`badge` (not used by WFL). Not wasted, just not WFL-critical.
- **`Icon` is the single most-used component (127 sites)** — and icons are the
  cross-engine glyph problem at scale. This forces an icon-strategy decision now.
- **`TextButton` (89) is the most-used button, then `IconButton` (57), `Button` (42),
  `OutlinedButton` (23).** I only have a filled button (`pill_button`). The button
  family is the biggest leaf gap.
- **Scrolling is universal** — `LazyColumn` (33) + `verticalScroll` (21). Every real
  screen scrolls.
- **Overlays are heavily used** — `ModalBottomSheet` (7 screens), `AlertDialog` (25) +
  custom `Dialog` (4), `DropdownMenu` (9). These are the structural frontier.
- **Animation is sparse and localized** — `AnimatedContent` for wizard step transitions
  (onboarding, update-program, gym wizard, cooldown, execution); a couple
  `AnimatedVisibility`. Lower priority.
- **Custom Canvas drawing** centers on progress rings/arcs (rest timer, conditioning
  timer, wins ring) and one line chart (progress sparkline). Needs a draw primitive.

## Gap analysis vs the current kit (20 components + column/row + present)

**Already covered (map, maybe minor tweaks):**
`card`→WflCard ✓ · `divider`→HorizontalDivider ✓ · `chip`→FilterChip ✓ ·
`toggle`→Switch ✓ · `checkbox` ✓ · `radio_group`→RadioButton ✓ ·
`progress_bar`→LinearProgressIndicator ✓ · `collapsible_section`→WflSectionHeader ✓ ·
`list_row`→ListItem ✓ · `stepper`→the ± ValueAdjuster ✓ ·
`text_field`→OutlinedTextField ✓ · `switch_tile`→ToggleRow ✓ ·
`nav` (segmented control) ≈ SegmentedButton ✓ (reuse) · `header`→TopAppBar (needs a
leading back-nav slot) · `fab` (needs an Extended variant).

**Leaf gaps WFL needs (ranked by usage):**
1. **icon** (127) — needs an icon system (see decision below). Highest leverage.
2. **text_button** (89), **icon_button** (57), **outlined_button** (23) — the button family.
3. **tab_bar** / TabRow + scrollable tabs (progress, exercises screens).
4. **search_bar** (exercises, exercise picker) — a text_field variant.
5. **surface**/container (27) — a generic toned container (pills, sections).
6. chip variants: AssistChip, SuggestionChip (minor on top of `chip`).

**Structural capabilities (the frontier — build before converting):**
1. **scroll container** (LazyColumn / verticalScroll) — universal. Priority #1.
2. **overlays**: **dialog** (29), **bottom_sheet** (7), **menu/dropdown** (9) — a layer
   above the screen. Priority #2.
3. **draw primitive** (arc/path/line/circle) for rings + the chart. Priority #3.
4. **animation** (AnimatedContent step transitions) — needed only for the wizard
   screens; defer.

## Token spec for the re-skin (when converting)

- **Brand purple, two-tone.** Light primary `#753DF0`; dark `#8755F2`. Accent has a
  separate legible-contrast tone (light `#380B98`, dark `#D0BDFA`).
- **Light:** background/surface `#FFFFFF` (surface == background), onBackground
  `#1C1B1F`, hairline/outlineVariant `#DCD6E0`, surfaceVariant `#F2ECFC`.
- **Dark:** background/surface `#000000` (true black), onBackground `#E6E0EB`,
  outlineVariant `#353139`. Both themes exist — model light + dark.
- **Font: Figtree** (custom variable font, bundled `res/font/figtree_variable.ttf`,
  weights 400/500/600/700). To match WFL, bundle Figtree — not Roboto. 11 customized
  text styles (display/headline LARGE+MEDIUM use Material defaults).
- **Radii:** card/button 12dp, sheet (top) 20dp (Material default shape scale otherwise:
  4/8/12/16/28).
- **Spacing:** 4pt grid; screenMargin 16, cardPadding 16, sectionGap 16, itemGap 8,
  blockGap 24, rowVertical 12, hairline 1. Two densities (Comfortable default; Compact
  for the execution screen).
- Beyond the Material scheme, also model: `accent`, `accentContrast`, `celebrationPulse`,
  `celebrationGlitter[]`, `chartPalette[6]`.

## The icon decision (needs an owner call)

`Icon` is the #1 component (127 uses) and the kit has none. To match WFL (Material
Symbols icons) across both engines, the options are:
- **(a) bundle an icon font** (e.g. Material Symbols) that both Flutter and Kivy load,
  and reference icons by codepoint/name — durable, scalable, matches how WFL does it;
- **(b) per-icon SVG path data** drawn on both engines — more control, more work per icon.

Recommendation: **(a)** — an icon font is how Material itself ships icons; it makes
`icon("calendar")` a one-liner in both kits and ends the tofu/glyph problem for good.

## Suggested build order

1. **Button family** (text/outlined/icon_button) — trivial, unblocks 169 call sites.
2. **icon** — once the font decision is made (the highest-leverage single piece).
3. **scroll container** — foundational; unblocks rendering real (tall) screens.
4. **overlays** (dialog → bottom_sheet → menu).
5. tab_bar, search_bar, surface; the draw primitive; animation last.

Then convert WFL screen-by-screen (simplest first: LogWinSheet, PathDetailScreen,
WorkoutWarmupScreen, SuggestedStretchesScreen, ExercisePickerScreen), 3-way verified.
