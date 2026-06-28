# PseudoUI generated kit screen -- workout_summary  (from Compose WorkoutSummaryScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (63 calls)
```python
ui.define_box("workout_summary_z00_scaffold", "content", "V")
ui.define_box("workout_summary_z01_box", "workout_summary_z00_scaffold", "V")
ui.define_box("workout_summary_z02_circularprogress", "workout_summary_z01_box", "V")
ui.define_box("workout_summary_z03_lazycolumn", "workout_summary_z00_scaffold", "V")
ui.define_box("workout_summary_z04_row", "workout_summary_z03_lazycolumn", "H")
ui.define_box("workout_summary_z05_statcard", "workout_summary_z04_row", "V")
ui.define_box("workout_summary_z06_wflcard", "workout_summary_z05_statcard", "V")
ui.define_box("workout_summary_z07_roundedcornersha", "workout_summary_z06_wflcard", "V")
ui.define_box("workout_summary_z08_borderstroke", "workout_summary_z06_wflcard", "V")
ui.define_box("workout_summary_z09_card", "workout_summary_z06_wflcard", "V")
ui.define_box("workout_summary_z10_card", "workout_summary_z06_wflcard", "V")
ui.define_box("workout_summary_z11_column", "workout_summary_z06_wflcard", "V")
ui.define_text("workout_summary_z12_x", "workout_summary_z11_column", "—")
ui.define_text("workout_summary_z13_duration", "workout_summary_z11_column", "Duration")
ui.define_box("workout_summary_z14_statcard", "workout_summary_z04_row", "V")
ui.define_box("workout_summary_z15_wflcard", "workout_summary_z14_statcard", "V")
ui.define_box("workout_summary_z16_roundedcornersha", "workout_summary_z15_wflcard", "V")
ui.define_box("workout_summary_z17_borderstroke", "workout_summary_z15_wflcard", "V")
ui.define_box("workout_summary_z18_card", "workout_summary_z15_wflcard", "V")
ui.define_box("workout_summary_z19_card", "workout_summary_z15_wflcard", "V")
ui.define_box("workout_summary_z20_column", "workout_summary_z15_wflcard", "V")
ui.define_text("workout_summary_z21_formatvolume_uis", "workout_summary_z20_column", "formatVolume(uiState.totalVolu…")
ui.define_text("workout_summary_z22_volume", "workout_summary_z20_column", "Volume")
ui.define_box("workout_summary_z23_statcard", "workout_summary_z04_row", "V")
ui.define_box("workout_summary_z24_wflcard", "workout_summary_z23_statcard", "V")
ui.define_box("workout_summary_z25_roundedcornersha", "workout_summary_z24_wflcard", "V")
ui.define_box("workout_summary_z26_borderstroke", "workout_summary_z24_wflcard", "V")
ui.define_box("workout_summary_z27_card", "workout_summary_z24_wflcard", "V")
ui.define_box("workout_summary_z28_card", "workout_summary_z24_wflcard", "V")
ui.define_box("workout_summary_z29_column", "workout_summary_z24_wflcard", "V")
ui.define_text("workout_summary_z30_uistate_exercise", "workout_summary_z29_column", "uiState.exerciseSummaries.size…")
ui.define_text("workout_summary_z31_exercises", "workout_summary_z29_column", "Exercises")
ui.define_text("workout_summary_z32_personal_records", "workout_summary_z03_lazycolumn", "Personal records")
ui.define_box("workout_summary_z33_prrow", "workout_summary_z03_lazycolumn", "V")
ui.define_box("workout_summary_z34_wflcard", "workout_summary_z33_prrow", "V")
ui.define_box("workout_summary_z35_roundedcornersha", "workout_summary_z34_wflcard", "V")
ui.define_box("workout_summary_z36_borderstroke", "workout_summary_z34_wflcard", "V")
ui.define_box("workout_summary_z37_card", "workout_summary_z34_wflcard", "V")
ui.define_box("workout_summary_z38_card", "workout_summary_z34_wflcard", "V")
ui.define_box("workout_summary_z39_row", "workout_summary_z34_wflcard", "H")
ui.define_box("workout_summary_z40_column", "workout_summary_z39_row", "V")
ui.define_text("workout_summary_z41_pr_exercisename", "workout_summary_z40_column", "pr.exerciseName")
ui.define_text("workout_summary_z42_new_estimated_1r", "workout_summary_z40_column", "New estimated 1RM|New $it-rep …")
ui.define_text("workout_summary_z43_formatweight_pr_", "workout_summary_z39_row", "formatWeight(pr.weightKg, unit)")
ui.define_spacer_zone("workout_summary_z44_spacer", "workout_summary_z03_lazycolumn")
ui.define_divider_zone("workout_summary_z45_divider", "workout_summary_z03_lazycolumn")
ui.define_text("workout_summary_z46_exercise_summary", "workout_summary_z03_lazycolumn", "Exercise summary")
ui.define_box("workout_summary_z47_exercisesummaryc", "workout_summary_z03_lazycolumn", "V")
ui.define_box("workout_summary_z48_wflcard", "workout_summary_z47_exercisesummaryc", "V")
ui.define_box("workout_summary_z49_roundedcornersha", "workout_summary_z48_wflcard", "V")
ui.define_box("workout_summary_z50_borderstroke", "workout_summary_z48_wflcard", "V")
ui.define_box("workout_summary_z51_card", "workout_summary_z48_wflcard", "V")
ui.define_box("workout_summary_z52_card", "workout_summary_z48_wflcard", "V")
ui.define_box("workout_summary_z53_row", "workout_summary_z48_wflcard", "H")
ui.define_box("workout_summary_z54_column", "workout_summary_z53_row", "V")
ui.define_text("workout_summary_z55_summary_exercise", "workout_summary_z54_column", "summary.exerciseName")
ui.define_text("workout_summary_z56_topstr", "workout_summary_z54_column", "topStr")
ui.define_text("workout_summary_z57_summary_complete", "workout_summary_z53_row", "${summary.completedSets} sets")
ui.define_spacer_zone("workout_summary_z58_spacer", "workout_summary_z03_lazycolumn")
ui.define_box("workout_summary_z59_topappbar", "workout_summary_z00_scaffold", "V")
ui.define_text("workout_summary_z60_workout_complete", "workout_summary_z59_topappbar", "Workout complete")
ui.define_icon("workout_summary_z61_edit_workout", "workout_summary_z59_topappbar", "Edit workout")
ui.define_button("workout_summary_z62_done", "workout_summary_z59_topappbar", "Done")
```

## generated tree
  - Column[z00_scaffold]  <container>
    - Column[z01_box]  <container>
      - Column[z02_circularprogress]  <leaf>
    - Column[z03_lazycolumn]  <container>
      - Row[z04_row]  <container>
        - Column[z05_statcard]  <container>
          - Column[z06_wflcard]  <container>
            - Column[z07_roundedcornersha]  <leaf>
            - Column[z08_borderstroke]  <leaf>
            - Column[z09_card]  <leaf>
            - Column[z10_card]  <leaf>
            - Column[z11_column]  <container>
              - Text[—]  <leaf>
              - Text[Duration]  <leaf>
        - Column[z14_statcard]  <container>
          - Column[z15_wflcard]  <container>
            - Column[z16_roundedcornersha]  <leaf>
            - Column[z17_borderstroke]  <leaf>
            - Column[z18_card]  <leaf>
            - Column[z19_card]  <leaf>
            - Column[z20_column]  <container>
              - Text[formatVolume(uiState.totalVolu…]  <leaf>
              - Text[Volume]  <leaf>
        - Column[z23_statcard]  <container>
          - Column[z24_wflcard]  <container>
            - Column[z25_roundedcornersha]  <leaf>
            - Column[z26_borderstroke]  <leaf>
            - Column[z27_card]  <leaf>
            - Column[z28_card]  <leaf>
            - Column[z29_column]  <container>
              - Text[uiState.exerciseSummaries.size…]  <leaf>
              - Text[Exercises]  <leaf>
      - Text[Personal records]  <leaf>
      - Column[z33_prrow]  <container>
        - Column[z34_wflcard]  <container>
          - Column[z35_roundedcornersha]  <leaf>
          - Column[z36_borderstroke]  <leaf>
          - Column[z37_card]  <leaf>
          - Column[z38_card]  <leaf>
          - Row[z39_row]  <container>
            - Column[z40_column]  <container>
              - Text[pr.exerciseName]  <leaf>
              - Text[New estimated 1RM|New $it-rep …]  <leaf>
            - Text[formatWeight(pr.weightKg, unit)]  <leaf>
      - Spacer[z44_spacer]  <leaf>
      - Divider[z45_divider]  <leaf>
      - Text[Exercise summary]  <leaf>
      - Column[z47_exercisesummaryc]  <container>
        - Column[z48_wflcard]  <container>
          - Column[z49_roundedcornersha]  <leaf>
          - Column[z50_borderstroke]  <leaf>
          - Column[z51_card]  <leaf>
          - Column[z52_card]  <leaf>
          - Row[z53_row]  <container>
            - Column[z54_column]  <container>
              - Text[summary.exerciseName]  <leaf>
              - Text[topStr]  <leaf>
            - Text[${summary.completedSets} sets]  <leaf>
      - Spacer[z58_spacer]  <leaf>
    - Column[z59_topappbar]  <container>
      - Text[Workout complete]  <leaf>
      - Icon[Edit workout]  <leaf>
      - Button[Done]  <leaf>

---
## verify vs Compose source (WorkoutSummaryScreen)
- distinct leaf signatures matched: 9/9 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 63 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (workout_summary_screen.py)
- leaf signatures shared:        3
- generated-only (other states / not in this trace): 6
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:Edit workout
    GEN-only T:Duration
    GEN-only T:Exercise summary
    GEN-only T:Exercises
    GEN-only T:Personal records
    GEN-only T:Volume
