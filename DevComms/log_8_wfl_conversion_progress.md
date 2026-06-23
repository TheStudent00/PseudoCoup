# log_8 — WFL → PseudoUI conversion: progress at 12 screens

Date: 2026-06-23
Type: progress log. Pairs with log_5 (plan), log_6 (kit build spec), log_7 (kit complete).

## Where it stands

**12 of ~30 WFL screens converted**, each rendered by the ONE PseudoFlutter kit on
both paths (Flutter ship + Kivy debug) from the WFL re-skin token profile
(`tokens.wfl.json`) — the kit code is unchanged; only the token data differs.

| # | screen | verified | headline component(s) added |
|---|--------|----------|------------------------------|
| 1 | LogWinSheet | 3-way | (overlays, FilterChip outline+check) |
| 2 | Paths | 3-way | bottom_nav_bar, app_bar |
| 3 | Settings / You | 3-way | setting_row, text role:section |
| 4 | Today / Home | 3-way | panel, card_header, workout_row |
| 5 | Progress | 3-way | donut, filled_button(solid) |
| 6 | Program | 3-way | roadmap_row (nested rail timeline) |
| 7 | WorkoutExecution (set logging) | 3-way | top_bar, set_table_header, set_row |
| 8 | Warm up | 3-way | activity_card |
| 9 | Exercises library | 3-way | setting_row "favorite" trailing |
| 10 | Gym profiles | 3-way | (reuse only) |
| 11 | Report a bug | 2-way | (reuse only) |
| 12 | Onboarding step | 2-way | selection_card |

"3-way" = diffed against a screencap of the **real WFL app** running on the
`WFL_Compare_AVD` Android emulator (boot → install APK → `adb screencap`). "2-way" =
Flutter↔Kivy source-faithful (the screen is first-run/deep-in-navigation; the Android
leg is pending, not skipped).

## The methodology that worked

Per screen: **read the Compose source (and/or screencap the real screen) → assemble
from the kit → render both engines → diff against the emulator.** The verification
loop (render Flutter golden + render Kivy PNG + `adb screencap` + composite) is fully
mechanical; the structural assembly is the part that takes judgment (see "why not
mechanical" below).

Every conversion is committed with its 3-way/2-way comparison PNG in
`PseudoFlutter/comparisons/`; the real-app references live in `comparisons/wfl_ref/`.
Golden suite: **47/47 green**.

## The kit converged

Across 12 screens the component vocabulary stopped growing fast — recent screens add
**at most one small component** (activity_card, selection_card, a trailing kind). The
kit now spans ~55 intent functions. New screens are increasingly pure assembly.

## Fidelity work done

- **Font is theme-as-data.** WFL screens render in **Figtree** (instanced from the
  variable font to static Regular/SemiBold); the default theme stays Roboto. One
  token (`font.family`) flips it; every component reads `theme.fontFamily`.
- **FilterChip** made faithful (outline-when-unselected + tonal-fill + leading check).
- **filled_button** gained `solid` (vivid accent) vs the tonal CTA, after the real
  Progress screen showed the wins-card button is the vivid variant.

## Known, tracked deltas (not silently shipped)

- **Colour emoji.** WFL uses emoji as leading glyphs (warmup activities, gym/onboarding
  cards). Colour emoji can't render identically across Flutter goldens + Kivy, so
  monochrome Material-icon stand-ins are used (they map well per-activity). Fixing it
  means bundling an emoji font — deferred.
- A few omitted accessories (the "+" FAB on Today, "Add set", a help icon) — minor.
- Two Kivy demo-harness positioning glitches were found and fixed (Program desc,
  Exercises column height); they were in the render scripts, never the kit components.

## Why it isn't fully mechanical (recorded for the open question)

A transpiler would *lower* (intent → primitives); this conversion *lifts* WFL's
Compose primitives (`Row{ Box; Column{ Text; Text }; Surface }`) up into kit intent
(`workout_row(...)`). Recognising "this **is** a workout_row" is pattern recognition,
not syntax mapping — and a transpiler that *didn't* lift would just reproduce WFL's
primitives, defeating the kit. The grading is mechanical; the lift is semantic. The
most-mechanical path available is intent→intent: `WFL_PyHaxe/src/ui/` already holds
every screen in Python against the *old* kit, so porting those to the new kit skips
the lift.

## Remaining tail (~18 screens)

Execution flow (Cooldown, Summary, rest-timer, plate calculator), exercise
detail/create, exercise picker, cardio log, history/session detail, path detail,
update-program wizard, stretch suggestions, celebration, debug panel. Each should be
mostly assembly now; expect the occasional new leaf.
