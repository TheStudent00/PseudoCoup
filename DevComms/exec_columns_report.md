# WorkoutExecutionScreen set-log columns — fix report

## Cause (one sentence)
The `Box(Modifier.weight(1f))` swipe container that holds the whole set table is a `Box`
(z-stack) handled by `_zstack`, which — unlike the generic-container branch — never
propagated fill-width from its `fillMaxSize` child, so the Box collapsed to Kivy's default
~100px and every weighted table cell divided that stub width instead of the full display.

## Fix
- File: `~/Programming/WFL_MixingCenter/render/kivy_kit.py`, function `_zstack`.
- Change: mirror the existing generic-container rule (line ~888, "a fillMaxWidth child
  forces its wrapping parent that wide"). Compute `_kids_fill_x = any(k.size_hint_x is not
  None for k in kids)` and, in the wrap-width `else` branch, set `fl.size_hint_x = 1` when a
  child fills width (else `None` as before).
- Why general: it applies the same Compose constraint-propagation the generic branch already
  uses (a fill-width child's width IS the incoming max), now for the Box/z-stack path too. No
  screen name, text, or tolerance is referenced; any wrapping Box with a fill-width child
  benefits.

## Verification (LAYOUT FIDELITY)
| Screen | Before | After |
|---|---|---|
| WorkoutExecutionScreen | 8/31 (26%) | 28/31 (90%) |
| GymListScreen | 7/7 | 7/7 |
| SettingsScreen | 41/41 | 41/41 |
| LogCardioScreen | 25/25 | 25/25 |
| ExercisePickerScreen | 26/26 | 26/26 |
| ProgramDayEditorScreen | 13/13 | 13/13 |
| WorkoutCooldownScreen | 25/25 | 25/25 |
| Specimen | 21/21 | 21/21 |
| SpecimenList | 5/5 | 5/5 |

The five table header cells (Set #, RPE, Weight (kg), Reps, Set type) now land within 0.1%
of the Compose x/w ground truth. The 3 remaining WorkoutExecution misses/extras are
unrelated content-set differences (a MISS'd "6"/"12" preview pair and XTRA up-next items),
not column geometry.
