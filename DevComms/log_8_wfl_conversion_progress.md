# log_8 — WFL → PseudoUI conversion: progress at 26 screens

Date: 2026-06-23 (updated)
Type: progress log. Pairs with log_5 (plan), log_6 (kit build spec), log_7 (kit complete).

## Where it stands

**26 of ~30 WFL screens converted**, each rendered by the ONE PseudoFlutter kit on
both paths (Flutter ship + Kivy debug) from the WFL re-skin token profile
(`tokens.wfl.json`) — the kit code is unchanged across themes; only the token data
differs. Golden suite: **61/61 green** (gate on the real exit code, not a piped tail).

| #  | screen | verified | headline component(s) |
|----|--------|----------|------------------------|
| 1  | LogWinSheet | 3-way | overlays, FilterChip outline+check |
| 2  | Paths | 3-way | bottom_nav_bar, app_bar |
| 3  | Settings / You | 3-way | setting_row, text role:section |
| 4  | Today / Home | 3-way | panel, card_header, workout_row |
| 5  | Progress | 3-way | donut, filled_button(solid) |
| 6  | Program | 3-way | roadmap_row (nested rail timeline) |
| 7  | WorkoutExecution (set logging) | 3-way | top_bar, set_table_header, set_row |
| 8  | Warm up | 3-way | activity_card |
| 9  | Exercises library | 3-way | setting_row "favorite" trailing |
| 10 | Gym profiles | 3-way | reuse only |
| 11 | Report a bug | 2-way | reuse only |
| 12 | Onboarding step | 2-way | selection_card |
| 13 | Workout Summary | 2-way | stat_card |
| 14 | Path detail | 2-way | reuse (title + info chips + sections) |
| 15 | Log cardio | 2-way | reuse (chips + outlined_button + nav) |
| 16 | Cooldown | 2-way | reuse (activity_card twin of Warm up) |
| 17 | Suggested stretches | 2-way | **info_card** |
| 18 | Exercise detail | 2-way | reuse (chips + sections + divider) |
| 19 | History | 2-way | info_card (week headers + session/cardio) |
| 20 | Exercise picker | 2-way | reuse (search_bar + chips + favorite rows) |
| 21 | New/Edit exercise | 2-way | **dropdown_field** |
| 22 | Session detail | 2-way | **set_line** (per-exercise set breakdown) |
| 23 | Rest timer overlay | 2-way | reuse (progress_ring + outlined_button) |
| 24 | Plate calculator | 2-way | **value_stepper** |
| 25 | Debug panel | 2-way | reuse (+ outlined_button full_width fix) |
| 26 | Gym editor | 2-way | reuse (grouped collapsible list) |

"3-way" = diffed against a screencap of the **real WFL app** on the `WFL_Compare_AVD`
Android emulator. "2-way" = Flutter↔Kivy source-faithful (the screen is first-run or
deep in navigation; the Android leg is pending, not skipped).

## The methodology that worked

Per screen: **read the Compose source (and/or screencap the real screen) → assemble
from the kit → render both engines → diff.** The verification loop (Flutter golden +
Kivy `export_to_png` under xvfb + `tools/sidebyside.py`) is mechanical; the structural
assembly is the judgment (see "why not mechanical" below).

## The kit converged — then grew slowly and deliberately

Screens 14–26 add **at most one small leaf each**, and several add none. The leaves
added this stretch, each genuinely reused:

- **info_card** — a WflCard list card: heading (+ optional trailing tonal pill),
  optional subtitle, body, and a spaced stat row. Shared by History + Suggested
  stretches + Session-detail PR cards + Debug-panel readout.
- **dropdown_field** — an outlined form select (value/placeholder + expand_more caret).
  The editor forms' workhorse.
- **set_line** — a compact logged-set row (label · weight×reps · effort · ★), distinct
  from the editable 5-column `set_row`. (Session detail.)
- **value_stepper** — a full-width headline adjuster (filled round −, big string value
  with unit, filled round +). The prominent sibling of inline `stepper`. (Plate calc.)

## Fidelity work & bugs fixed this stretch

- **outlined_button parity bug.** Flutter's `alignment:center` made the button fill any
  bounded width (full-width in a column/Wrap) while the Kivy button hugged its label —
  a real cross-engine divergence. Fixed by adding `full_width` (default = hug label) to
  both kits; `full_width:true` stretches on both. Log-cardio's "When" updated to true.
- **progress_ring arc.** Pixel-verified (masking the purple button text that had
  contaminated the colour centroid) that both engines sweep clockwise from 12 o'clock
  by the same fraction — confirmed matching, not mirrored, despite the composite's
  optical illusion.
- Carets render via the shared Material icon (`expand_more`/`expand_less`), never a
  unicode glyph, so they can't go tofu or drift between engines.

## Known, tracked deltas (not silently shipped)

- **Colour emoji** → monochrome Material-icon stand-ins (warmup/cooldown/onboarding).
- A few omitted accessories: the Today/GymEditor FABs, per-row delete icons, top-bar
  favourite/overflow icons (top_bar carries a text action, not icon actions).
- The Kivy chip flow-gap is a touch wider than Flutter's Wrap spacing (cosmetic).

## Why it isn't fully mechanical (recorded for the open question)

A transpiler would *lower* (intent → primitives); this conversion *lifts* WFL's Compose
primitives up into kit intent. Recognising "this **is** a workout_row / info_card" is
pattern recognition, not syntax mapping — and a transpiler that *didn't* lift would
just reproduce WFL's primitives, defeating the kit. The grading is mechanical; the lift
is semantic. The most-mechanical path available is intent→intent: `WFL_PyHaxe/src/ui/`
holds every screen in Python against the *old* kit, so porting those skips the lift.

## Remaining tail (~4 screens)

Program editor, Program-day editor, Gym-create wizard, and the celebration check-in
sheet (MesocycleCheckInSheet). Each should be mostly assembly now.
