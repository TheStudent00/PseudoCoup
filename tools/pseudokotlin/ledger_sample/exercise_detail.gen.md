# PseudoUI generated kit screen -- exercise_detail  (from Compose ExerciseDetailScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (82 calls)
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
ui.define_spacer_zone("exercise_detail_z17_spacer", "exercise_detail_z15_column")
ui.define_text("exercise_detail_z18_body", "exercise_detail_z15_column", "body")
ui.define_box("exercise_detail_z19_flowrow", "exercise_detail_z14_detailsection", "H")
ui.define_box("exercise_detail_z20_assistchip", "exercise_detail_z19_flowrow", "V")
ui.define_text("exercise_detail_z21_m_displayname", "exercise_detail_z20_assistchip", "m.displayName()")
ui.define_box("exercise_detail_z22_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z23_column", "exercise_detail_z22_detailsection", "V")
ui.define_text("exercise_detail_z24_secondary_muscle", "exercise_detail_z23_column", "Secondary muscles")
ui.define_spacer_zone("exercise_detail_z25_spacer", "exercise_detail_z23_column")
ui.define_text("exercise_detail_z26_body", "exercise_detail_z23_column", "body")
ui.define_box("exercise_detail_z27_flowrow", "exercise_detail_z22_detailsection", "H")
ui.define_box("exercise_detail_z28_suggestionchip", "exercise_detail_z27_flowrow", "V")
ui.define_text("exercise_detail_z29_m_displayname", "exercise_detail_z28_suggestionchip", "m.displayName()")
ui.define_box("exercise_detail_z30_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z31_column", "exercise_detail_z30_detailsection", "V")
ui.define_text("exercise_detail_z32_movement_equipme", "exercise_detail_z31_column", "Movement & equipment")
ui.define_spacer_zone("exercise_detail_z33_spacer", "exercise_detail_z31_column")
ui.define_text("exercise_detail_z34_body", "exercise_detail_z31_column", "body")
ui.define_text("exercise_detail_z35_exercise_movemen", "exercise_detail_z30_detailsection", "${exercise.movementPattern.dis…")
ui.define_divider_zone("exercise_detail_z36_divider", "exercise_detail_z04_lazycolumn")
ui.define_spacer_zone("exercise_detail_z37_spacer", "exercise_detail_z04_lazycolumn")
ui.define_box("exercise_detail_z38_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z39_column", "exercise_detail_z38_detailsection", "V")
ui.define_text("exercise_detail_z40_form_notes", "exercise_detail_z39_column", "Form notes")
ui.define_spacer_zone("exercise_detail_z41_spacer", "exercise_detail_z39_column")
ui.define_text("exercise_detail_z42_body", "exercise_detail_z39_column", "body")
ui.define_text("exercise_detail_z43_exercise_instruc", "exercise_detail_z38_detailsection", "exercise.instructions")
ui.define_box("exercise_detail_z44_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z45_column", "exercise_detail_z44_detailsection", "V")
ui.define_text("exercise_detail_z46_coaching_cues", "exercise_detail_z45_column", "Coaching cues")
ui.define_spacer_zone("exercise_detail_z47_spacer", "exercise_detail_z45_column")
ui.define_text("exercise_detail_z48_body", "exercise_detail_z45_column", "body")
ui.define_text("exercise_detail_z49_exercise_cues", "exercise_detail_z44_detailsection", "exercise.cues")
ui.define_box("exercise_detail_z50_detailsection", "exercise_detail_z04_lazycolumn", "V")
ui.define_box("exercise_detail_z51_column", "exercise_detail_z50_detailsection", "V")
ui.define_text("exercise_detail_z52_video_reference", "exercise_detail_z51_column", "Video reference")
ui.define_spacer_zone("exercise_detail_z53_spacer", "exercise_detail_z51_column")
ui.define_text("exercise_detail_z54_body", "exercise_detail_z51_column", "body")
ui.define_text("exercise_detail_z55_exercise_videoli", "exercise_detail_z50_detailsection", "exercise.videoLink")
ui.define_box("exercise_detail_z56_topappbar", "exercise_detail_z02_scaffold", "V")
ui.define_text("exercise_detail_z57_text", "exercise_detail_z56_topappbar", "")
ui.define_icon("exercise_detail_z58_back", "exercise_detail_z56_topappbar", "Back")
ui.define_icon("exercise_detail_z59_toggle_favorite", "exercise_detail_z56_topappbar", "Toggle favorite")
ui.define_icon("exercise_detail_z60_more", "exercise_detail_z56_topappbar", "More")
ui.define_box("exercise_detail_z61_dropdownmenu", "exercise_detail_z56_topappbar", "V")
ui.define_box("exercise_detail_z62_dropdownmenuitem", "exercise_detail_z61_dropdownmenu", "V")
ui.define_text("exercise_detail_z63_duplicate_edit", "exercise_detail_z62_dropdownmenuitem", "Duplicate & Edit")
ui.define_box("exercise_detail_z64_dropdownmenuitem", "exercise_detail_z61_dropdownmenu", "V")
ui.define_text("exercise_detail_z65_allow_programmin", "exercise_detail_z64_dropdownmenuitem", "Allow programming again|Never …")
ui.define_box("exercise_detail_z66_dropdownmenuitem", "exercise_detail_z61_dropdownmenu", "V")
ui.define_text("exercise_detail_z67_edit", "exercise_detail_z66_dropdownmenuitem", "Edit")
ui.define_box("exercise_detail_z68_dropdownmenuitem", "exercise_detail_z61_dropdownmenu", "V")
ui.define_text("exercise_detail_z69_delete", "exercise_detail_z68_dropdownmenuitem", "Delete")
ui.define_box("exercise_detail_z70_alertdialog", "content", "V")
ui.define_text("exercise_detail_z71_delete_exercise", "exercise_detail_z70_alertdialog", "Delete exercise?")
ui.define_text("exercise_detail_z72_this_will_perman", "exercise_detail_z70_alertdialog", "This will permanently delete \…")
ui.define_button("exercise_detail_z73_delete", "exercise_detail_z70_alertdialog", "Delete")
ui.define_button("exercise_detail_z74_cancel", "exercise_detail_z70_alertdialog", "Cancel")
ui.define_box("exercise_detail_z75_alertdialog", "content", "V")
ui.define_text("exercise_detail_z76_already_in_your_", "exercise_detail_z75_alertdialog", "Already in your program")
ui.define_text("exercise_detail_z77_is_in_where_swap", "exercise_detail_z75_alertdialog", "\| is in $where. |Swap it for …")
ui.define_button("exercise_detail_z78_swap_all_now", "exercise_detail_z75_alertdialog", "Swap all now")
ui.define_button("exercise_detail_z79_got_it", "exercise_detail_z75_alertdialog", "Got it")
ui.define_button("exercise_detail_z80_swap_during_work", "exercise_detail_z75_alertdialog", "Swap during workouts")
ui.define_button("exercise_detail_z81_cancel", "exercise_detail_z75_alertdialog", "Cancel")
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
            - Spacer[z17_spacer]  <leaf>
            - Text[body]  <leaf>
          - Row[z19_flowrow]  <container>
            - Column[z20_assistchip]  <container>
              - Text[m.displayName()]  <leaf>
        - Column[z22_detailsection]  <container>
          - Column[z23_column]  <container>
            - Text[Secondary muscles]  <leaf>
            - Spacer[z25_spacer]  <leaf>
            - Text[body]  <leaf>
          - Row[z27_flowrow]  <container>
            - Column[z28_suggestionchip]  <container>
              - Text[m.displayName()]  <leaf>
        - Column[z30_detailsection]  <container>
          - Column[z31_column]  <container>
            - Text[Movement & equipment]  <leaf>
            - Spacer[z33_spacer]  <leaf>
            - Text[body]  <leaf>
          - Text[${exercise.movementPattern.dis…]  <leaf>
        - Divider[z36_divider]  <leaf>
        - Spacer[z37_spacer]  <leaf>
        - Column[z38_detailsection]  <container>
          - Column[z39_column]  <container>
            - Text[Form notes]  <leaf>
            - Spacer[z41_spacer]  <leaf>
            - Text[body]  <leaf>
          - Text[exercise.instructions]  <leaf>
        - Column[z44_detailsection]  <container>
          - Column[z45_column]  <container>
            - Text[Coaching cues]  <leaf>
            - Spacer[z47_spacer]  <leaf>
            - Text[body]  <leaf>
          - Text[exercise.cues]  <leaf>
        - Column[z50_detailsection]  <container>
          - Column[z51_column]  <container>
            - Text[Video reference]  <leaf>
            - Spacer[z53_spacer]  <leaf>
            - Text[body]  <leaf>
          - Text[exercise.videoLink]  <leaf>
    - Column[z56_topappbar]  <container>
      - Text[z57_text]  <leaf>
      - Icon[Back]  <leaf>
      - Icon[Toggle favorite]  <leaf>
      - Icon[More]  <leaf>
      - Column[z61_dropdownmenu]  <container>
        - Column[z62_dropdownmenuitem]  <container>
          - Text[Duplicate & Edit]  <leaf>
        - Column[z64_dropdownmenuitem]  <container>
          - Text[Allow programming again|Never …]  <leaf>
        - Column[z66_dropdownmenuitem]  <container>
          - Text[Edit]  <leaf>
        - Column[z68_dropdownmenuitem]  <container>
          - Text[Delete]  <leaf>
  - Column[z70_alertdialog]  <container>
    - Text[Delete exercise?]  <leaf>
    - Text[This will permanently delete \…]  <leaf>
    - Button[Delete]  <leaf>
    - Button[Cancel]  <leaf>
  - Column[z75_alertdialog]  <container>
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
- tree validity: 82 nodes, 0 orphan parents

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
