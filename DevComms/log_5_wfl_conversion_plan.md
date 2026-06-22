# log_5 — Converting WFL's UI into PseudoUI: the plan

Date: 2026-06-22
Type: plan / decision. Captures the conversion strategy agreed in conversation so
the points are not lost. NOT started — deliberately sequenced AFTER the kit is
complete, to avoid the research-while-converting mistake that made PyHaxeUI patchy.

## The reference

The original WFL repo (`~/Programming/WFL`, may need refreshing) as it looks running
in an Android emulator is the thing to reverse-engineer into PseudoUI. WFL is a
**native Android app in Jetpack Compose + Material3** (254 Kotlin files; feature
screens under `ui/today`, `ui/programs`, `ui/wins`, `ui/exercises`, `ui/onboarding`;
bottom **sheets** e.g. `LogWinSheet`, `ActiveAdaptationsSheet`; MVVM ViewModels).

## The fidelity standard (this is the load-bearing correction)

Fidelity = **structural match**, NOT pixel-perfect styling. Same component inventory,
same layouts, effectively identical relative/absolute positioning. Differences are
allowed ONLY where the UI API genuinely forces them (a Flutter/Kivy switch will not
be pixel-identical to a Material switch). "It won't be perfect" means *style details
forced by different APIs* — it does NOT mean "approximate / patchy is acceptable."

This corrects the exact misunderstanding that made PyHaxeUI drift: the owner's "I
don't expect it to be perfect" was misread as "matching doesn't matter much." It
matters. The components and layouts should match structurally; Android's UI vocabulary
is not so alien to Kivy/Flutter that near-identical components and positioning aren't
available.

Tailwind: WFL is **Material3** and **Flutter is natively Material**, so
Compose-Material3 → Flutter is nearly 1:1 structurally; the Kivy side already renders
the same intents identically. The structural bar is genuinely reachable.

## Why this beats the WFL_PyHaxe attempt (don't repeat the patchiness)

The patchiness then was structural, not bad luck: an immature kit forced bespoke
per-screen code; bespoke screens don't share a design language; there was no token
table to pull drift back; three unknowns per screen (kit + vocabulary + port at once).

Now: a settled kit + compose-from-intent (screens are assembly, proven by
settings_demo/cycle_demo), one `tokens.json` as the single design-language source, and
a reproducible side-by-side fidelity harness.

**The discipline that prevents re-patchiness:** every fix lands in a SHARED place —
the token table or a component's visual — NEVER in per-screen code. Because screens are
compositions, a shared fix propagates to every screen at once, so fidelity converges
instead of drifting. The moment we patch one screen specifically, we are back in the
old failure mode.

## Sequencing (agreed): finish the kit BEFORE converting

Do not research-while-converting. Complete the kit first:

1. **Remaining leaf components** — tab_bar, banner/callout, icon_button, dropdown/
   select, search_bar, tag, segmented_progress, rating, image, … (the cheap tail).
2. **The three structural capabilities WFL provably needs:**
   - **scrolling** — every screen needs a scroll container;
   - **overlays** — WFL has bottom sheets, plus dialogs/menus/snackbars live on a
     layer above the screen, not inline;
   - **animation** — transitions and the collapse animation (collapse is instant now).

Only then convert — as pure assembly.

## Conversion method (when we get there)

1. Audit WFL's Compose to inventory exactly which Material3 components + layouts each
   screen uses → the precise kit target (derived, not guessed).
2. Fill `tokens.json` to WFL's Material3 design language (colour, type scale, spacing,
   radii).
3. Author each component's visual to Material3 once.
4. Build each WFL screen as a composition of intents (column/row + components), screen
   by screen.
5. Verify **3-way: WFL-on-Android | Flutter | Kivy.** Iterate the tokens / component
   visuals (shared), never per-screen.

## Status

Plan only. Resume after the kit's leaf set + scroll/overlay/animation are done.
