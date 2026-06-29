# PseudoUI generated kit screen -- exercise_detail  (from Compose ExerciseDetailScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (70 calls)
```python
ui.define_box("exercise_detail_z00_launchedeffect", "content", "V")
ui.define_box("exercise_detail_z01_launchedeffect", "content", "V")
ui.define_box("exercise_detail_z02_scaffold", "content", "V")
ui.define_box("exercise_detail_z03_exercisedetailco", "exercise_detail_z02_scaffold", "V")
ui.define_box("exercise_detail_z04_lazycolumn", "exercise_detail_z03_exercisedetailco", "V")
ui.define_box("exercise_detail_z05_flowrow", "exercise_detail_z04_lazycolumn", "H")
ui.define_box("exercise_detail_z06_suggestionchip", "exercise_detail_z05_flowrow", "V")
ui.define_text("exercise_detail_z07_custom", "exercise_detail_z06_suggestionchip", "Custom")
ui.define_box("exercise_detail_z08_suggestionchip", "exercise_detail_z05_flowrow", "V")
ui.define_text("exercise_detail_z09_built_in", "exercise_detail_z08_suggestionchip", "Built-in")
ui.define_box("exercise_detail_z10_suggestionchip", "exercise_detail_z05_flowrow", "V")
ui.define_text("exercise_detail_z11_compound_isolati", "exercise_detail_z10_suggestionchip", "Compound|Isolation")
ui.define_box("exercise_detail_z12_suggestionchip", "exercise_detail_z05_flowrow", "V")
ui.define_text("exercise_detail_z13_unilateral_bilat", "exercise_detail_z12_suggestionchip", "Unilateral|Bilateral")
ui.define_box("exercise_detail_z14_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z15_column", "exercise_detail_z14_detailsection", "V")
ui.define_text("exercise_detail_z16_primary_muscles", "exercise_detail_z15_column", "Primary muscles")
ui.define_box("exercise_detail_z17_flowrow", "exercise_detail_z14_detailsection", "H")
ui.define_box("exercise_detail_z18_assistchip", "exercise_detail_z17_flowrow", "V")
ui.define_text("exercise_detail_z19_m_displayname", "exercise_detail_z18_assistchip", "m.displayName()")
ui.define_box("exercise_detail_z20_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z21_column", "exercise_detail_z20_detailsection", "V")
ui.define_text("exercise_detail_z22_secondary_muscle", "exercise_detail_z21_column", "Secondary muscles")
ui.define_box("exercise_detail_z23_flowrow", "exercise_detail_z20_detailsection", "H")
ui.define_box("exercise_detail_z24_suggestionchip", "exercise_detail_z23_flowrow", "V")
ui.define_text("exercise_detail_z25_m_displayname", "exercise_detail_z24_suggestionchip", "m.displayName()")
ui.define_box("exercise_detail_z26_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z27_column", "exercise_detail_z26_detailsection", "V")
ui.define_text("exercise_detail_z28_movement_equipme", "exercise_detail_z27_column", "Movement & equipment")
ui.define_text("exercise_detail_z29_exercise_movemen", "exercise_detail_z26_detailsection", "${exercise.movementPattern.dis…")
ui.define_divider_zone("exercise_detail_z30_divider", "exercise_detail_z04_lazycolumn")
ui.define_spacer_zone("exercise_detail_z31_spacer", "exercise_detail_z04_lazycolumn")
ui.define_box("exercise_detail_z32_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z33_column", "exercise_detail_z32_detailsection", "V")
ui.define_text("exercise_detail_z34_form_notes", "exercise_detail_z33_column", "Form notes")
ui.define_text("exercise_detail_z35_exercise_instruc", "exercise_detail_z32_detailsection", "exercise.instructions")
ui.define_box("exercise_detail_z36_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z37_column", "exercise_detail_z36_detailsection", "V")
ui.define_text("exercise_detail_z38_coaching_cues", "exercise_detail_z37_column", "Coaching cues")
ui.define_text("exercise_detail_z39_exercise_cues", "exercise_detail_z36_detailsection", "exercise.cues")
ui.define_box("exercise_detail_z40_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z41_column", "exercise_detail_z40_detailsection", "V")
ui.define_text("exercise_detail_z42_video_reference", "exercise_detail_z41_column", "Video reference")
ui.define_text("exercise_detail_z43_exercise_videoli", "exercise_detail_z40_detailsection", "exercise.videoLink")
ui.define_box("exercise_detail_z44_topappbar", "exercise_detail_z02_scaffold", "V")
ui.define_text("exercise_detail_z45_text", "exercise_detail_z44_topappbar", "")
ui.define_icon("exercise_detail_z46_back", "exercise_detail_z44_topappbar", "Back")
ui.define_icon("exercise_detail_z47_toggle_favorite", "exercise_detail_z44_topappbar", "Toggle favorite")
ui.define_icon("exercise_detail_z48_more", "exercise_detail_z44_topappbar", "More")
ui.define_box("exercise_detail_z49_dropdownmenu", "exercise_detail_z44_topappbar", "V")
ui.define_box("exercise_detail_z50_dropdownmenuitem", "exercise_detail_z49_dropdownmenu", "V")
ui.define_text("exercise_detail_z51_duplicate_edit", "exercise_detail_z50_dropdownmenuitem", "Duplicate & Edit")
ui.define_box("exercise_detail_z52_dropdownmenuitem", "exercise_detail_z49_dropdownmenu", "V")
ui.define_text("exercise_detail_z53_allow_programmin", "exercise_detail_z52_dropdownmenuitem", "Allow programming again|Never …")
ui.define_box("exercise_detail_z54_dropdownmenuitem", "exercise_detail_z49_dropdownmenu", "V")
ui.define_text("exercise_detail_z55_edit", "exercise_detail_z54_dropdownmenuitem", "Edit")
ui.define_box("exercise_detail_z56_dropdownmenuitem", "exercise_detail_z49_dropdownmenu", "V")
ui.define_text("exercise_detail_z57_delete", "exercise_detail_z56_dropdownmenuitem", "Delete")
ui.define_box("exercise_detail_z58_alertdialog", "content", "V")
ui.define_text("exercise_detail_z59_delete_exercise", "exercise_detail_z58_alertdialog", "Delete exercise?")
ui.define_text("exercise_detail_z60_this_will_perman", "exercise_detail_z58_alertdialog", "This will permanently delete \…")
ui.define_button("exercise_detail_z61_delete", "exercise_detail_z58_alertdialog", "Delete")
ui.define_button("exercise_detail_z62_cancel", "exercise_detail_z58_alertdialog", "Cancel")
ui.define_box("exercise_detail_z63_alertdialog", "content", "V")
ui.define_text("exercise_detail_z64_already_in_your_", "exercise_detail_z63_alertdialog", "Already in your program")
ui.define_text("exercise_detail_z65_is_in_where_swap", "exercise_detail_z63_alertdialog", "\| is in $where. |Swap it for …")
ui.define_button("exercise_detail_z66_swap_all_now", "exercise_detail_z63_alertdialog", "Swap all now")
ui.define_button("exercise_detail_z67_got_it", "exercise_detail_z63_alertdialog", "Got it")
ui.define_button("exercise_detail_z68_swap_during_work", "exercise_detail_z63_alertdialog", "Swap during workouts")
ui.define_button("exercise_detail_z69_cancel", "exercise_detail_z63_alertdialog", "Cancel")
```

## generated tree
  - Column[z00_launchedeffect]  <leaf>
  - Column[z01_launchedeffect]  <leaf>
  - Column[z02_scaffold]  <container>
    - Column[z03_exercisedetailco]  <container>
      - Column[z04_lazycolumn]  <container>
        - Row[z05_flowrow]  <container>
          - Column[z06_suggestionchip]  <container>
            - Text[Custom]  <leaf>
          - Column[z08_suggestionchip]  <container>
            - Text[Built-in]  <leaf>
          - Column[z10_suggestionchip]  <container>
            - Text[Compound|Isolation]  <leaf>
          - Column[z12_suggestionchip]  <container>
            - Text[Unilateral|Bilateral]  <leaf>
        - Column[z14_detailsection]  <container>
          - Column[z15_column]  <container>
            - Text[Primary muscles]  <leaf>
          - Row[z17_flowrow]  <container>
            - Column[z18_assistchip]  <container>
              - Text[m.displayName()]  <leaf>
        - Column[z20_detailsection]  <container>
          - Column[z21_column]  <container>
            - Text[Secondary muscles]  <leaf>
          - Row[z23_flowrow]  <container>
            - Column[z24_suggestionchip]  <container>
              - Text[m.displayName()]  <leaf>
        - Column[z26_detailsection]  <container>
          - Column[z27_column]  <container>
            - Text[Movement & equipment]  <leaf>
          - Text[${exercise.movementPattern.dis…]  <leaf>
        - Divider[z30_divider]  <leaf>
        - Spacer[z31_spacer]  <leaf>
        - Column[z32_detailsection]  <container>
          - Column[z33_column]  <container>
            - Text[Form notes]  <leaf>
          - Text[exercise.instructions]  <leaf>
        - Column[z36_detailsection]  <container>
          - Column[z37_column]  <container>
            - Text[Coaching cues]  <leaf>
          - Text[exercise.cues]  <leaf>
        - Column[z40_detailsection]  <container>
          - Column[z41_column]  <container>
            - Text[Video reference]  <leaf>
          - Text[exercise.videoLink]  <leaf>
    - Column[z44_topappbar]  <container>
      - Text[z45_text]  <leaf>
      - Icon[Back]  <leaf>
      - Icon[Toggle favorite]  <leaf>
      - Icon[More]  <leaf>
      - Column[z49_dropdownmenu]  <container>
        - Column[z50_dropdownmenuitem]  <container>
          - Text[Duplicate & Edit]  <leaf>
        - Column[z52_dropdownmenuitem]  <container>
          - Text[Allow programming again|Never …]  <leaf>
        - Column[z54_dropdownmenuitem]  <container>
          - Text[Edit]  <leaf>
        - Column[z56_dropdownmenuitem]  <container>
          - Text[Delete]  <leaf>
  - Column[z58_alertdialog]  <container>
    - Text[Delete exercise?]  <leaf>
    - Text[This will permanently delete \…]  <leaf>
    - Button[Delete]  <leaf>
    - Button[Cancel]  <leaf>
  - Column[z63_alertdialog]  <container>
    - Text[Already in your program]  <leaf>
    - Text[\| is in $where. |Swap it for …]  <leaf>
    - Button[Swap all now]  <leaf>
    - Button[Got it]  <leaf>
    - Button[Swap during workouts]  <leaf>
    - Button[Cancel]  <leaf>

---
## verify vs Compose source (ExerciseDetailScreen)
- distinct leaf signatures matched: 21/21 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 70 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (exercise_detail_screen.py)
- leaf signatures shared:        1
- generated-only (other states / not in this trace): 20
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:Back
    GEN-only I:More
    GEN-only I:Toggle favorite
    GEN-only T:Already in your program
    GEN-only T:Built-in
    GEN-only T:Cancel
    GEN-only T:Coaching cues
    GEN-only T:Custom
    GEN-only T:Delete
    GEN-only T:Delete exercise?
    GEN-only T:Duplicate & Edit
    GEN-only T:Edit
