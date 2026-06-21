# log_1 — PseudoFlutter: the intention-based UI process

Date: 2026-06-21
Type: brainstorming (settles the UI process before building PseudoFlutter).
Sharpens the three-tier kit model + intent-not-mechanism rule (already in
`PyHaxeUI_development_plan.md`) into three concrete decisions. Distinct from the
settled-decisions handoff; this is the design we agree before code.

## Why this exists

Before building PseudoFlutter (the UI kit over the Dart target), pin down the
intention-based UI process — because PyHaxeUI/WFL had real confusion when UI work
began, and we want to not repeat it.

## What actually made PyHaxeUI/WFL hard (it was NOT the layout)

Pure proportional layout — "this section is 0.90 of device width, side padding
0.05, top/bottom 2x the side" — is just math, and every toolkit (Kivy, Flutter)
does fractional layout. STRUCTURE was never the hard part. Three other things were:

	1  the kit, the intent vocabulary, AND the app port were built at once —
	   three unknowns per screen.
	2  the goal was to MATCH an existing pixel-perfect design (original WFL), which
	   is manual reverse-engineering — a different job from authoring a portable one.
	3  the real per-platform work is a component's RENDERING and BEHAVIOR (the
	   chevron, divider, press ripple, collapse animation) — not its proportions.

## The three decisions

### 1. Layout numbers are ROLES, not raw values

The app never writes `0.90`. It names a role; the theme maps role -> number.

	app:    collapsible_section(role="content", title="Mesocycle", body=[...])
	theme:  content.width_fraction = 0.90
	        content.pad_x_fraction = 0.05
	        content.pad_y_factor   = 2.0      # top/bottom = 2x side

A raw `0.90` in app code is both a magic number (un-portable design language) and
mechanism leaking into intent. A role keeps the app at intent-level and lets the
theme own the number once. A different width -> name a different role
(`"full_bleed"`, `"inset"`). This is WHY the structure is portable: both kits read
the same role->proportion table, so both produce identical structure by construction.

### 2. Two kinds of state; only one crosses the platform boundary

	UI-local state   collapse open/closed, press ripple, scroll, focus.
	                 the KIT owns it. the app never sees it. so it never touches
	                 the reactive-vs-imperative question.
	app state        the actual data shown. flows app -> kit via the intent (+
	                 `present` for updates). THIS is the only place the transpiler
	                 absorbs reactive (Flutter) vs imperative (Kivy) — the settled
	                 "empty present / state-set" point (handoff section 2).

Consequence: the app says `collapsible_section(title, body)` and never holds a
`collapsed` bool — the kit does. Most of what FEELS interactive is kit-internal,
so it is simply a non-issue for portability.

### 3. Structure is invariant; only rendering varies

The app's structure — a collapsible with this header + body; a nav with these
items — is identical on every platform (the portability guarantee, non-negotiable).
The kit varies only HOW it renders (Flutter widget vs Kivy drawing, ripple vs none,
chevron vs caret). Platform-divergent LAYOUT, if ever wanted (bottom tabs on iOS,
side nav on Android), is a choice made INSIDE the kit's component, hidden from the
app. The app intent never changes.

## What this buys

The app is fully platform-agnostic (named intents + roles, one structure).
Everything platform- or design-specific lives in exactly two authored-once places:

	theme tokens            (data)   proportions by role, colors, sizes
	per-component rendering  (code)   each generic component, once per kit (Flutter, Kivy)

And "match old WFL" stops being a per-screen fight: it becomes filling the theme
tokens + authoring the ~20-30 components' visuals to spec — a bounded, one-time
design pass, because screens are just compositions of intents that already render
consistently.

## Open question (owner call)

Decision 1 (roles vs raw numbers) most shapes how app code reads. Owner gut-check
pending: does naming a role feel right, or too indirect vs passing the number?

## Status / next

Brainstorm only; nothing built. PseudoFlutter has no repo yet. Agreed next step is a
worked example: build `pill_button` end-to-end — the intent surface, the theme
tokens, and the Flutter rendering (and the Kivy rendering, to see them side by side
from one call).
