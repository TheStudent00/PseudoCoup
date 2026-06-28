# PseudoUI generated kit screen -- session_detail  (from Compose SessionDetailScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (70 calls)
```python
ui.define_box("session_detail_z00_scaffold", "content", "V")
ui.define_box("session_detail_z01_box", "session_detail_z00_scaffold", "V")
ui.define_box("session_detail_z02_circularprogress", "session_detail_z01_box", "V")
ui.define_box("session_detail_z03_lazycolumn", "session_detail_z00_scaffold", "V")
ui.define_box("session_detail_z04_row", "session_detail_z03_lazycolumn", "H")
ui.define_box("session_detail_z05_statcard", "session_detail_z04_row", "V")
ui.define_box("session_detail_z06_wflcard", "session_detail_z05_statcard", "V")
ui.define_box("session_detail_z07_roundedcornersha", "session_detail_z06_wflcard", "V")
ui.define_box("session_detail_z08_borderstroke", "session_detail_z06_wflcard", "V")
ui.define_box("session_detail_z09_card", "session_detail_z06_wflcard", "V")
ui.define_box("session_detail_z10_card", "session_detail_z06_wflcard", "V")
ui.define_box("session_detail_z11_column", "session_detail_z06_wflcard", "V")
ui.define_text("session_detail_z12_x", "session_detail_z11_column", "—")
ui.define_text("session_detail_z13_duration", "session_detail_z11_column", "Duration")
ui.define_box("session_detail_z14_statcard", "session_detail_z04_row", "V")
ui.define_box("session_detail_z15_wflcard", "session_detail_z14_statcard", "V")
ui.define_box("session_detail_z16_roundedcornersha", "session_detail_z15_wflcard", "V")
ui.define_box("session_detail_z17_borderstroke", "session_detail_z15_wflcard", "V")
ui.define_box("session_detail_z18_card", "session_detail_z15_wflcard", "V")
ui.define_box("session_detail_z19_card", "session_detail_z15_wflcard", "V")
ui.define_box("session_detail_z20_column", "session_detail_z15_wflcard", "V")
ui.define_text("session_detail_z21_formatvolume_uis", "session_detail_z20_column", "formatVolume(uiState.totalVolu…")
ui.define_text("session_detail_z22_volume", "session_detail_z20_column", "Volume")
ui.define_box("session_detail_z23_statcard", "session_detail_z04_row", "V")
ui.define_box("session_detail_z24_wflcard", "session_detail_z23_statcard", "V")
ui.define_box("session_detail_z25_roundedcornersha", "session_detail_z24_wflcard", "V")
ui.define_box("session_detail_z26_borderstroke", "session_detail_z24_wflcard", "V")
ui.define_box("session_detail_z27_card", "session_detail_z24_wflcard", "V")
ui.define_box("session_detail_z28_card", "session_detail_z24_wflcard", "V")
ui.define_box("session_detail_z29_column", "session_detail_z24_wflcard", "V")
ui.define_text("session_detail_z30_uistate_exercise", "session_detail_z29_column", "uiState.exercises.size.toStrin…")
ui.define_text("session_detail_z31_exercises", "session_detail_z29_column", "Exercises")
ui.define_text("session_detail_z32_personal_records", "session_detail_z03_lazycolumn", "Personal records")
ui.define_box("session_detail_z33_prcard", "session_detail_z03_lazycolumn", "V")
ui.define_box("session_detail_z34_wflcard", "session_detail_z33_prcard", "V")
ui.define_box("session_detail_z35_roundedcornersha", "session_detail_z34_wflcard", "V")
ui.define_box("session_detail_z36_borderstroke", "session_detail_z34_wflcard", "V")
ui.define_box("session_detail_z37_card", "session_detail_z34_wflcard", "V")
ui.define_box("session_detail_z38_card", "session_detail_z34_wflcard", "V")
ui.define_box("session_detail_z39_row", "session_detail_z34_wflcard", "H")
ui.define_box("session_detail_z40_column", "session_detail_z39_row", "V")
ui.define_text("session_detail_z41_pr_exercisename", "session_detail_z40_column", "pr.exerciseName")
ui.define_text("session_detail_z42_new_estimated_1r", "session_detail_z40_column", "New estimated 1RM|New $it-rep …")
ui.define_text("session_detail_z43_formatweight_pr_", "session_detail_z39_row", "formatWeight(pr.weightKg, unit)")
ui.define_spacer_zone("session_detail_z44_spacer", "session_detail_z03_lazycolumn")
ui.define_divider_zone("session_detail_z45_divider", "session_detail_z03_lazycolumn")
ui.define_text("session_detail_z46_exercises", "session_detail_z03_lazycolumn", "Exercises")
ui.define_box("session_detail_z47_exercisesection", "session_detail_z03_lazycolumn", "V")
ui.define_box("session_detail_z48_wflcard", "session_detail_z47_exercisesection", "V")
ui.define_box("session_detail_z49_roundedcornersha", "session_detail_z48_wflcard", "V")
ui.define_box("session_detail_z50_borderstroke", "session_detail_z48_wflcard", "V")
ui.define_box("session_detail_z51_card", "session_detail_z48_wflcard", "V")
ui.define_box("session_detail_z52_card", "session_detail_z48_wflcard", "V")
ui.define_box("session_detail_z53_column", "session_detail_z48_wflcard", "V")
ui.define_box("session_detail_z54_row", "session_detail_z53_column", "H")
ui.define_text("session_detail_z55_entry_exercisena", "session_detail_z54_row", "entry.exerciseName")
ui.define_text("session_detail_z56_formatvolume_ent", "session_detail_z54_row", "formatVolume(entry.volumeKg, u…")
ui.define_spacer_zone("session_detail_z57_spacer", "session_detail_z53_column")
ui.define_box("session_detail_z58_setrowitem", "session_detail_z53_column", "V")
ui.define_box("session_detail_z59_row", "session_detail_z58_setrowitem", "H")
ui.define_text("session_detail_z60_label", "session_detail_z59_row", "label")
ui.define_text("session_detail_z61_weightreps", "session_detail_z59_row", "weightReps")
ui.define_text("session_detail_z62_it", "session_detail_z59_row", "it")
ui.define_text("session_detail_z63_x", "session_detail_z59_row", "★")
ui.define_spacer_zone("session_detail_z64_spacer", "session_detail_z03_lazycolumn")
ui.define_box("session_detail_z65_topappbar", "session_detail_z00_scaffold", "V")
ui.define_box("session_detail_z66_column", "session_detail_z65_topappbar", "V")
ui.define_text("session_detail_z67_ad_hoc_workout", "session_detail_z66_column", "Ad-hoc Workout")
ui.define_text("session_detail_z68_formatdetaildate", "session_detail_z66_column", "formatDetailDate(uiState.start…")
ui.define_icon("session_detail_z69_back", "session_detail_z65_topappbar", "Back")
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
              - Text[uiState.exercises.size.toStrin…]  <leaf>
              - Text[Exercises]  <leaf>
      - Text[Personal records]  <leaf>
      - Column[z33_prcard]  <container>
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
      - Text[Exercises]  <leaf>
      - Column[z47_exercisesection]  <container>
        - Column[z48_wflcard]  <container>
          - Column[z49_roundedcornersha]  <leaf>
          - Column[z50_borderstroke]  <leaf>
          - Column[z51_card]  <leaf>
          - Column[z52_card]  <leaf>
          - Column[z53_column]  <container>
            - Row[z54_row]  <container>
              - Text[entry.exerciseName]  <leaf>
              - Text[formatVolume(entry.volumeKg, u…]  <leaf>
            - Spacer[z57_spacer]  <leaf>
            - Column[z58_setrowitem]  <container>
              - Row[z59_row]  <container>
                - Text[label]  <leaf>
                - Text[weightReps]  <leaf>
                - Text[it]  <leaf>
                - Text[★]  <leaf>
      - Spacer[z64_spacer]  <leaf>
    - Column[z65_topappbar]  <container>
      - Column[z66_column]  <container>
        - Text[Ad-hoc Workout]  <leaf>
        - Text[formatDetailDate(uiState.start…]  <leaf>
      - Icon[Back]  <leaf>

---
## verify vs Compose source (SessionDetailScreen)
- distinct leaf signatures matched: 7/7 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 70 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (session_detail_screen.py)
- leaf signatures shared:        4
- generated-only (other states / not in this trace): 3
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:Back
    GEN-only T:Personal records
    GEN-only T:★
