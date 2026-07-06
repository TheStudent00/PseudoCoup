# Fidelity closeout: ExercisesScreen / ProgramsScreen geometry misses + SettingsScreen regression fix

## Starting point (per fidelity_377_restored.md)

FIDELITY ALL: 412/423 -- ExercisesScreen 27/35 (8 misses), ProgramsScreen 18/21 (3 misses), all other
26 screens 100%.

## Evidence: the MISS lines before any fix (host runs 050/051, `layout_diff.py`)

### ExercisesScreen (8 FAIL, from `Cable Chest Fly` onward -- the tail of a ~35-row LazyColumn)

```
  PASS  Bench Dip                       compose y=74.4 h=2.1 | kivy y=77.3 h=2.2 | worst Δ 2.8%
  PASS  Triceps · Bodyweight            compose y=76.5 h=1.5 | kivy y=79.5 h=1.6 | worst Δ 3.0%
  FAIL  Cable Chest Fly                 compose y=79.8 h=2.1 | kivy y=82.8 h=2.2 | worst Δ 3.1%
  FAIL  Chest · Cable Machine           compose y=81.9 h=1.5 | kivy y=85.0 h=1.6 | worst Δ 3.2%
  FAIL  Cable Lateral Raise             compose y=85.1 h=2.1 | kivy y=88.4 h=2.2 | worst Δ 3.3%
  FAIL  Side Delts · Cable Machine      compose y=87.2 h=1.5 | kivy y=90.6 h=1.6 | worst Δ 3.4%
  FAIL  Close-Grip Bench Press          compose y=90.5 h=2.1 | kivy y=94.0 h=2.2 | worst Δ 3.5%
  FAIL  Triceps · Barbell               compose y=92.6 h=1.5 | kivy y=96.2 h=1.6 | worst Δ 3.6%
  FAIL  Decline Bench Press             compose y=95.8 h=2.1 | kivy y=99.6 h=2.2 | worst Δ 3.7%
  FAIL  Chest · Barbell                 compose y=97.9 h=1.5 | kivy y=101.7 h=1.6 | worst Δ 3.8%
matched 35/35 compose components; 27 within ±3.0%   LAYOUT FIDELITY: 77% (27/35)
```

The Δ grows monotonically (2.8% -> 3.8%) purely as a function of row index -- a linear, cumulative
vertical drift, not a one-off geometry bug on any single component.

### ProgramsScreen (3 FAIL -- all program-card TITLE width, never position/height)

```
  FAIL  3-Day Full Body — Ground Up      compose w=60.6 | kivy w=63.8 | worst Δ 3.2%
  FAIL  3-Day Strength — Compound Focus  compose w=73.2 | kivy w=77.1 | worst Δ 3.9%
  FAIL  4-Day Full Body — Movement (A/B) compose w=72.3 | kivy w=75.6 | worst Δ 3.3%
matched 24/21 compose components; 18 within ±3.0%   LAYOUT FIDELITY: 86% (18/21)
```

Every other component on the card (path pills, description, Join button) PASSED -- only the
`titleMedium` + `fontWeight=SemiBold` program-name Text overshot, and only in WIDTH.

## Cause 1 (ExercisesScreen): a +1px single-line label height overshoot, compounding down a long list

Direct pixel comparison (`inspect_layout.py` dumps, compose ground truth vs kivy) of the exact same
strings: `Arnold Press` (bodyLarge 16sp) measured compose h=19, kivy h=20; `Front Delts · Side Delts
· Dumbbell` (bodySmall 12sp) measured compose h=14, kivy h=15 -- both **exactly +1px**, every
occurrence, across the whole ~35-row list (and, cross-checked against the Specimen dump, across many
other screens too: `SettingsScreen`, `WorkoutExecutionScreen`, `ExercisePickerScreen`, etc. all show
the identical `19->20` / `14->15` pattern on isolated components, but only ExercisesScreen stacks
enough of these single-line labels back-to-back in one uninterrupted LazyColumn for the compounding
+1px/label (2 labels per exercise row: name + muscle line) to cross the ±3% tolerance band before the
list ends).

Specimen (`dumpSpecimen`, compose vs kivy, both single-line): `labelSmall` 11sp (13 vs 14), `bodySmall`/
`labelMedium` 12sp (14 vs 15), `bodyLarge` 16sp (19 vs 20) all overshoot by 1px; `titleMedium` 18sp (22
vs 22) and `titleLarge`/`headlineSmall` 22-24sp (27 vs 27, 29 vs 29) match exactly. This is a genuine
SDL2 texture-height quantization quirk of Kivy's text provider at <=16sp, not a font-metrics fact to
special-case per screen.

### Fix (general, shared runtime)

File: `WFL_MixingCenter/render/kivy_kit.py`, function `_leaf_label` -> inner `_line_h` (the single-line
natural-height stacking rule).

```python
def _line_h(w, ts, _lh=lh, _fs=fs):
    lines = max(1, round(ts[1] / max(1.0, _fs * 1.2)))
    if not _lh or lines == 1:
        w.height = ts[1] - 1 if _fs <= 16 else ts[1]
    else:
        w.height = ts[1] / lines + (lines - 1) * _lh
```

Applies a specimen-verified -1px correction to every single-line label at <=16sp (any style, any
screen) -- not keyed on ExercisesScreen or any component name. Multi-line labels (lines > 1) are
untouched, since the overshoot is specific to the single-line texture-height measurement.

## Cause 2 (ProgramsScreen): the SemiBold width-widening calibration is size-dependent, not flat

`_SHAPER_CAL` (same file, `_leaf_label`) widens Kivy's measured text width to emulate Compose's shaper,
including an extra multiplier for SemiBold+ weights, calibrated as a flat `1.042` for all of "16sp and
up." That constant was derived from a single specimen point: `headlineSmall` at 24sp (SemiBold ratio
1.064 vs Normal). Program-card titles use `titleMedium` (18sp) with an explicit `fontWeight=SemiBold`
override -- a different, uncovered point on the same curve. Adding a matching 18sp SemiBold entry to
the Specimen (`LayoutDumpTest.kt` + its Python mirror `inspect_layout.py`) and re-measuring showed the
TRUE ratio at 18sp is only ~1.02 (SemiBold 205px vs plain 201px), not 1.064 -- the widening is strongly
size-dependent, and applying the 24sp-derived flat constant at 18sp overshot program-card titles by
~5% width, exactly matching the observed 3.2-3.9% Δ.

(A first attempt skipped the SemiBold multiplier entirely whenever a real per-weight font file was
already resolved (`fname` set) reasoning that a real weight file needs no synthetic-bold width
correction. This fixed ProgramsScreen but broke `WorkoutCooldownScreen`'s existing 24sp SemiBold
wrap-threshold text -- which ALSO resolves a real weight file yet still needs a widening correction
there. That confirms the correction is real (Compose's shaper genuinely widens SemiBold beyond the
font file's own static advances at some sizes) and is a function of SIZE, not of whether a real weight
file was instantiated. The fix below replaces that failed attempt.)

### Fix (general, shared runtime + Specimen extension)

1. `WFL_MixingCenter/WFL/app/src/test/java/com/sara/workoutforlife/layout/LayoutDumpTest.kt` --
   added a matched pair (`titleMedium` + `fontWeight=SemiBold` / plain `titleMedium`) of the exact
   text style ProgramCard uses, to `dumpSpecimen()`. This is the test/dump harness, not the read-only
   main app source.
2. `WFL_MixingCenter/render/inspect_layout.py` -- added the matching pair to `_specimen()`, the Python
   mirror of the Kotlin Specimen composable (kept in sync by convention; this is harness tooling, not
   transpiler output).
3. `WFL_MixingCenter/render/kivy_kit.py`, `_leaf_label`'s `_SHAPER_CAL`: replaced the flat `1.042` for
   all SemiBold+ text at fs>=16 with a size-banded value using the two specimen-measured interior
   points: `1.006` at <=12sp (unchanged), `1.013` at 13-19sp (new, from the 18sp titleMedium pair),
   `1.042` at 20sp+ (unchanged, still covers `headlineSmall`'s 24sp case). Not keyed on ProgramsScreen
   or any component name -- it is purely a function of font size and weight, applied identically
   wherever `titleMedium`/`labelMedium`/`headlineSmall` etc. appear across the app.

### Verification (previous pass)

- Specimen gate (host run 072): 26/26, including the new 18sp SemiBold pair (0.4% Δ) and the original
  24sp SemiBold wrap case (`Take a few minutes to come down.`, 2.0% Δ, still wraps correctly in both
  engines).
- `layout_diff.py` per-screen re-checks (host run 074): `ExercisesScreen` 35/35, `ProgramsScreen`
  21/21, `WorkoutCooldownScreen` 25/25 (confirmed no regression from the size-banding).
- Full run (host 077): FIDELITY ALL 418/424, all screens 100% EXCEPT `SettingsScreen` 36/42 -- a
  newly-exposed regression, diagnosed and fixed below.

## The SettingsScreen regression: root cause and fix

### What broke and why it wasn't Cause 1 or Cause 2 directly

After Cause 1/2 shipped, `SettingsScreen` dropped from a previously-100%-passing 41/41 to 36/42 (the
"42" in the intermediate run's denominator was itself an artifact: the shortfall in kivy's total scrolled
content height made "Back up my data" spuriously visible in kivy's viewport while compose's ground
truth kept it below the fold, inflating the paired-component count from 41 to 42 with one component
that should never have been comparable at all -- see final tally below, which confirms the screen's
TRUE denominator is 41, matching `fidelity_377_restored.md`'s original 41/41 exactly).

Deep pixel-level reconstruction (`layout_diff.py` SettingsScreen re-run, plus raw JSON node dumps read
directly from `WFL/app/build/layout_dump/SettingsScreen.json` (compose ground truth) and
`PseudoCoup/layout_inspect/SettingsScreen.kivy.json` (kivy transpile), both at full un-rounded pixel
precision) isolated the exact mechanism:

`SettingsScreen`'s `NotificationRow` (title + labelSmall subtitle + `SingleChoiceSegmentedButtonRow` of
three `SegmentedButton`s) repeats 4 times. Comparing consecutive NotificationRow title y-positions:

```
compose title-to-title (row 1 -> row 2): 563 - 459 = 104px
kivy    title-to-title (row 1 -> row 2): 554 - 459 =  95px
shortfall per row: 9px, compounding identically at every subsequent row (measured 9.15px/row
across all 4 rows in the percent-normalized layout_diff output)
```

Of that 9px/row shortfall, ~1px is legitimately Cause 1's -1px correction on the row's own bodyMedium
title label (correctly applied, harmless in isolation). The remaining ~8px was traced to
`kivy_kit.py`'s `_leaf_button`, which special-cased `SegmentedButton`'s layout-box height to a flat,
hardcoded `dp(40)` with the comment "SegmentedButton opts out" of Compose's
`minimumInteractiveComponentSize` (the rule, used correctly for every OTHER clickable in the same
function, that pads any clickable's final LAYOUT box to >= 48dp tall even when its visual surface is
smaller).

Checking the real M3 `SegmentedButton` source (`androidx.compose.material3.SegmentedButton.kt`,
`SingleChoiceSegmentedButtonRowScope.SegmentedButton`) confirms the Surface backing each segment IS
itself a clickable/selectable component (`selected`/`onClick` semantics), so Compose Foundation's
`minimumInteractiveComponentSize()` machinery applies to it exactly like every other button/chip/tab in
the app -- the 40dp `OutlinedSegmentedButtonTokens.ContainerHeight` is only the VISUAL surface size; the
actual LAYOUT box Compose reserves is >= 48dp, with the 40dp surface centered inside it. The "opts out"
assumption baked into the original comment was never verified against a real measurement; it was an
inference from the M3 spec doc (which describes the visual container height, not the interactive layout
box) that happened to go unnoticed because `SettingsScreen` had enough incidental slack elsewhere to
absorb the ~2-3px/row it produced -- until Cause 1's legitimate -1px/label correction on the row's own
labels removed the last of that slack and pushed the screen's later NotificationRow instances over the
±3% tolerance band.

This is why the regression was NOT caused by "the -1px correction being over-broad" (option a in the
original task framing): the SegmentedButton's `Push`/`In-app`/`None` labels are drawn by Kivy's `Button`
widget inside `_leaf_button`, not by `_leaf_label`/`_line_h` at all -- the -1px correction never touches
them. The correction only shaved 1px off the row's own bodyMedium title, an unrelated and correctly-sized
change. The real, pre-existing gap was entirely in the SegmentedButton row's own height calibration
(option b): `SettingsScreen` was the ONLY screen in the app using `SingleChoiceSegmentedButtonRow`/
`SegmentedButton`, so no other screen could have exposed this gap, and no other screen's tolerance
margin could be affected by fixing it.

### The fix (general, shared runtime, not SettingsScreen-specific)

File: `WFL_MixingCenter/render/kivy_kit.py`, function `_leaf_button`.

Before:
```python
if b.size_hint_y is None and st["height"] is not None and node.kind != "SegmentedButton":
    b.height = max(dp(48), b.height)
if b.size_hint_y is None and st["height"] is None:
    b.height = dp(40) if node.kind == "SegmentedButton" else dp(48)
```

After: both `SegmentedButton` opt-outs removed. `SegmentedButton` now goes through the exact same
`minimumInteractiveComponentSize`-derived `dp(48)` path as every other clickable in the function (button,
chip, tab, icon button) -- no per-kind special case remains for height, and no screen name appears
anywhere in the change. This is keyed purely on Compose Foundation's own universal clickable-sizing rule,
which the function already implements correctly for six other component kinds; `SegmentedButton` was the
one incorrect exception, now removed.

### Verification

- `run tools/pseudokotlin/build_mixingcenter.py`: clean regen, 255/255 .kt files transpiled and
  py-compiled with 0 errors.
- `layout_diff.py` re-checks (host runs 079/082/084, each preceded by a fresh `inspect_layout.py` dump):
  - `SettingsScreen`: **41/41** (100%) -- fully restored, matching the ORIGINAL `fidelity_377_restored.md`
    baseline exactly (same true denominator, all 41 components in-band; the previously-misleading
    "Back up my data" visibility mismatch is gone because kivy's now-taller content correctly scrolls
    it below the fold in both engines, matching compose).
  - `ExercisesScreen`: **35/35** (100%) -- held, no regression from touching `_leaf_button`.
  - `ProgramsScreen`: **21/21** (100%) -- held, no regression from touching `_leaf_button`.
- `run_kotlin_tests.py` (host run 086): **160/160 pass** -- the fix only touches the Kivy-side runtime
  kit, not any Kotlin domain-engine code.

## Final authoritative tally (verbatim, host run 087_fidelity_full3.log)

```
  Specimen gate: 26/26 (not counted)
  SpecimenList gate: 5/5 (not counted)
  ExerciseDetailScreen: 16/16 within tolerance
  ExercisesScreen: 35/35 within tolerance
  GymListScreen: 7/7 within tolerance
  HistoryScreen: 7/7 within tolerance
  LogCardioScreen: 25/25 within tolerance
  ProgramsScreen: 21/21 within tolerance
  ProgressScreen: 9/9 within tolerance
  SettingsScreen: 41/41 within tolerance
  TodayScreen: 3/3 within tolerance
  WinsListScreen: 10/10 within tolerance
  OnboardingScreen: 3/3 within tolerance
  SessionDetailScreen: 14/14 within tolerance
  ReportBugScreen: 10/10 within tolerance
  ExerciseCreateScreen: 18/18 within tolerance
  GymCreateWizardScreen: 13/13 within tolerance
  GymEditorScreen: 5/5 within tolerance
  PathDetailScreen: 1/1 within tolerance
  PathsScreen: 3/3 within tolerance
  SuggestedStretchesScreen: 3/3 within tolerance
  WorkoutCooldownScreen: 25/25 within tolerance
  WorkoutExecutionScreen: 31/31 within tolerance
  WorkoutSummaryScreen: 2/2 within tolerance
  WorkoutWarmupScreen: 32/32 within tolerance
  ExercisePickerScreen: 26/26 within tolerance
  MyProgramScreen: 3/3 within tolerance
  ProgramDayEditorScreen: 13/13 within tolerance
  ProgramEditorScreen: 32/32 within tolerance
  UpdateProgramWizardScreen: 15/15 within tolerance
FIDELITY ALL: 423/423 components within tolerance (28 screens)
```

**423/423 -- every screen at 100%.** (423, not 424: the intermediate 424 in the prior pass's tally was
the artifact denominator described above, produced by the not-yet-fixed SegmentedButton gap making
"Back up my data" spuriously visible in kivy only; with the fix, kivy's content height correctly matches
compose's and that component drops out of the comparable set on both sides, exactly as it does in the
original 412/423 and 377-family baselines. 423 is the correct, stable total.)

All originally-assigned misses (ExercisesScreen 27/35 -> 35/35, ProgramsScreen 18/21 -> 21/21) remain
closed, and the SettingsScreen regression (41/41 -> 36/42 -> 41/41) introduced and then fixed within this
same body of work is fully resolved with no residual gap and no other screen affected.

## Budget

`fidelity.py`: 3/3 runs used across the full task (065 mid-diagnosis catching the WorkoutCooldownScreen
regression before shipping it; 077 confirming Cause 1/2 fixed but surfacing the SettingsScreen
regression; 087, this pass's single allotted run, confirming the SettingsScreen fix and the final
423/423 tally). `layout_diff.py`/`run_kotlin_tests.py` have no run-budget restriction and were used
freely to verify before spending the final `fidelity.py` run.
