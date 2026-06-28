# PseudoUI generated kit screen -- exercise_create  (from Compose ExerciseCreateScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (104 calls)
```python
ui.define_box("exercise_create_z00_launchedeffect", "content", "V")
ui.define_box("exercise_create_z01_scaffold", "content", "V")
ui.define_box("exercise_create_z02_lazycolumn", "exercise_create_z01_scaffold", "V")
ui.define_box("exercise_create_z03_labeledfield", "exercise_create_z02_lazycolumn", "V")
ui.define_box("exercise_create_z04_column", "exercise_create_z03_labeledfield", "V")
ui.define_box("exercise_create_z05_fieldlabel", "exercise_create_z04_column", "V")
ui.define_text("exercise_create_z06_exercise_name", "exercise_create_z05_fieldlabel", "Exercise name")
ui.define_box("exercise_create_z07_compactvaluefiel", "exercise_create_z03_labeledfield", "V")
ui.define_input_zone("exercise_create_z08_field", "exercise_create_z07_compactvaluefiel", "", "")
ui.define_text("exercise_create_z09_name_is_required", "exercise_create_z02_lazycolumn", "Name is required")
ui.define_box("exercise_create_z10_muscleselector", "exercise_create_z02_lazycolumn", "V")
ui.define_box("exercise_create_z11_column", "exercise_create_z10_muscleselector", "V")
ui.define_text("exercise_create_z12_primary_muscles", "exercise_create_z11_column", "Primary muscles *")
ui.define_box("exercise_create_z13_compactmultisele", "exercise_create_z11_column", "V")
ui.define_box("exercise_create_z14_box", "exercise_create_z13_compactmultisele", "V")
ui.define_box("exercise_create_z15_row", "exercise_create_z14_box", "H")
ui.define_text("exercise_create_z16_x", "exercise_create_z15_row", ", ")
ui.define_icon("exercise_create_z17_change", "exercise_create_z15_row", "Change")
ui.define_box("exercise_create_z18_dropdownmenu", "exercise_create_z14_box", "V")
ui.define_box("exercise_create_z19_dropdownmenuitem", "exercise_create_z18_dropdownmenu", "V")
ui.define_text("exercise_create_z20_label_option", "exercise_create_z19_dropdownmenuitem", "label(option)")
ui.define_icon("exercise_create_z21_icon", "exercise_create_z19_dropdownmenuitem", "")
ui.define_spacer_zone("exercise_create_z22_spacer", "exercise_create_z19_dropdownmenuitem")
ui.define_text("exercise_create_z23_select_at_least_", "exercise_create_z11_column", "Select at least one primary mu…")
ui.define_box("exercise_create_z24_muscleselector", "exercise_create_z02_lazycolumn", "V")
ui.define_box("exercise_create_z25_column", "exercise_create_z24_muscleselector", "V")
ui.define_text("exercise_create_z26_secondary_muscle", "exercise_create_z25_column", "Secondary muscles")
ui.define_box("exercise_create_z27_compactmultisele", "exercise_create_z25_column", "V")
ui.define_box("exercise_create_z28_box", "exercise_create_z27_compactmultisele", "V")
ui.define_box("exercise_create_z29_row", "exercise_create_z28_box", "H")
ui.define_text("exercise_create_z30_x", "exercise_create_z29_row", ", ")
ui.define_icon("exercise_create_z31_change", "exercise_create_z29_row", "Change")
ui.define_box("exercise_create_z32_dropdownmenu", "exercise_create_z28_box", "V")
ui.define_box("exercise_create_z33_dropdownmenuitem", "exercise_create_z32_dropdownmenu", "V")
ui.define_text("exercise_create_z34_label_option", "exercise_create_z33_dropdownmenuitem", "label(option)")
ui.define_icon("exercise_create_z35_icon", "exercise_create_z33_dropdownmenuitem", "")
ui.define_spacer_zone("exercise_create_z36_spacer", "exercise_create_z33_dropdownmenuitem")
ui.define_text("exercise_create_z37_select_at_least_", "exercise_create_z25_column", "Select at least one primary mu…")
ui.define_box("exercise_create_z38_enumdropdown", "exercise_create_z02_lazycolumn", "V")
ui.define_box("exercise_create_z39_labeledfield", "exercise_create_z38_enumdropdown", "V")
ui.define_box("exercise_create_z40_column", "exercise_create_z39_labeledfield", "V")
ui.define_box("exercise_create_z41_fieldlabel", "exercise_create_z40_column", "V")
ui.define_text("exercise_create_z42_movement_pattern", "exercise_create_z41_fieldlabel", "Movement pattern")
ui.define_box("exercise_create_z43_compactdropdown", "exercise_create_z39_labeledfield", "V")
ui.define_box("exercise_create_z44_box", "exercise_create_z43_compactdropdown", "V")
ui.define_box("exercise_create_z45_roundedcornersha", "exercise_create_z44_box", "V")
ui.define_box("exercise_create_z46_row", "exercise_create_z44_box", "H")
ui.define_text("exercise_create_z47_label_selected", "exercise_create_z46_row", "label(selected)")
ui.define_icon("exercise_create_z48_change", "exercise_create_z46_row", "Change")
ui.define_box("exercise_create_z49_dropdownmenu", "exercise_create_z44_box", "V")
ui.define_box("exercise_create_z50_dropdownmenuitem", "exercise_create_z49_dropdownmenu", "V")
ui.define_text("exercise_create_z51_label_option", "exercise_create_z50_dropdownmenuitem", "label(option)")
ui.define_box("exercise_create_z52_enumdropdown", "exercise_create_z02_lazycolumn", "V")
ui.define_box("exercise_create_z53_labeledfield", "exercise_create_z52_enumdropdown", "V")
ui.define_box("exercise_create_z54_column", "exercise_create_z53_labeledfield", "V")
ui.define_box("exercise_create_z55_fieldlabel", "exercise_create_z54_column", "V")
ui.define_text("exercise_create_z56_equipment", "exercise_create_z55_fieldlabel", "Equipment")
ui.define_box("exercise_create_z57_compactdropdown", "exercise_create_z53_labeledfield", "V")
ui.define_box("exercise_create_z58_box", "exercise_create_z57_compactdropdown", "V")
ui.define_box("exercise_create_z59_roundedcornersha", "exercise_create_z58_box", "V")
ui.define_box("exercise_create_z60_row", "exercise_create_z58_box", "H")
ui.define_text("exercise_create_z61_label_selected", "exercise_create_z60_row", "label(selected)")
ui.define_icon("exercise_create_z62_change", "exercise_create_z60_row", "Change")
ui.define_box("exercise_create_z63_dropdownmenu", "exercise_create_z58_box", "V")
ui.define_box("exercise_create_z64_dropdownmenuitem", "exercise_create_z63_dropdownmenu", "V")
ui.define_text("exercise_create_z65_label_option", "exercise_create_z64_dropdownmenuitem", "label(option)")
ui.define_box("exercise_create_z66_row", "exercise_create_z02_lazycolumn", "H")
ui.define_box("exercise_create_z67_compacttoggle", "exercise_create_z66_row", "V")
ui.define_box("exercise_create_z68_row", "exercise_create_z67_compacttoggle", "H")
ui.define_text("exercise_create_z69_unilateral", "exercise_create_z68_row", "Unilateral")
ui.define_box("exercise_create_z70_switch", "exercise_create_z68_row", "V")
ui.define_box("exercise_create_z71_compacttoggle", "exercise_create_z66_row", "V")
ui.define_box("exercise_create_z72_row", "exercise_create_z71_compacttoggle", "H")
ui.define_text("exercise_create_z73_compound", "exercise_create_z72_row", "Compound")
ui.define_box("exercise_create_z74_switch", "exercise_create_z72_row", "V")
ui.define_box("exercise_create_z75_seedsourcedropdo", "exercise_create_z02_lazycolumn", "V")
ui.define_box("exercise_create_z76_column", "exercise_create_z75_seedsourcedropdo", "V")
ui.define_box("exercise_create_z77_labeledfield", "exercise_create_z76_column", "V")
ui.define_box("exercise_create_z78_column", "exercise_create_z77_labeledfield", "V")
ui.define_box("exercise_create_z79_fieldlabel", "exercise_create_z78_column", "V")
ui.define_text("exercise_create_z80_base_starting_we", "exercise_create_z79_fieldlabel", "Base starting weight on (optio…")
ui.define_box("exercise_create_z81_compactdropdown", "exercise_create_z77_labeledfield", "V")
ui.define_box("exercise_create_z82_box", "exercise_create_z81_compactdropdown", "V")
ui.define_box("exercise_create_z83_roundedcornersha", "exercise_create_z82_box", "V")
ui.define_box("exercise_create_z84_row", "exercise_create_z82_box", "H")
ui.define_text("exercise_create_z85_label_selected", "exercise_create_z84_row", "label(selected)")
ui.define_icon("exercise_create_z86_change", "exercise_create_z84_row", "Change")
ui.define_box("exercise_create_z87_dropdownmenu", "exercise_create_z82_box", "V")
ui.define_box("exercise_create_z88_dropdownmenuitem", "exercise_create_z87_dropdownmenu", "V")
ui.define_text("exercise_create_z89_label_option", "exercise_create_z88_dropdownmenuitem", "label(option)")
ui.define_text("exercise_create_z90_for_a_new_moveme", "exercise_create_z76_column", "For a new movement, we'll star…")
ui.define_input_zone("exercise_create_z91_form_notes_optio", "exercise_create_z02_lazycolumn", "", "Form notes (optional)")
ui.define_input_zone("exercise_create_z92_coaching_cues_op", "exercise_create_z02_lazycolumn", "", "Coaching cues (optional)")
ui.define_box("exercise_create_z93_labeledfield", "exercise_create_z02_lazycolumn", "V")
ui.define_box("exercise_create_z94_column", "exercise_create_z93_labeledfield", "V")
ui.define_box("exercise_create_z95_fieldlabel", "exercise_create_z94_column", "V")
ui.define_text("exercise_create_z96_video_link_optio", "exercise_create_z95_fieldlabel", "Video link (optional)")
ui.define_box("exercise_create_z97_compactvaluefiel", "exercise_create_z93_labeledfield", "V")
ui.define_input_zone("exercise_create_z98_field", "exercise_create_z97_compactvaluefiel", "", "")
ui.define_spacer_zone("exercise_create_z99_spacer", "exercise_create_z02_lazycolumn")
ui.define_box("exercise_create_z100_topappbar", "exercise_create_z01_scaffold", "V")
ui.define_text("exercise_create_z101_edit_exercise_ne", "exercise_create_z100_topappbar", "Edit exercise|New exercise")
ui.define_icon("exercise_create_z102_back", "exercise_create_z100_topappbar", "Back")
ui.define_icon("exercise_create_z103_save", "exercise_create_z100_topappbar", "Save")
```

## generated tree
  - Column[z00_launchedeffect]  <leaf>
  - Column[z01_scaffold]  <container>
    - Column[z02_lazycolumn]  <container>
      - Column[z03_labeledfield]  <container>
        - Column[z04_column]  <container>
          - Column[z05_fieldlabel]  <container>
            - Text[Exercise name]  <leaf>
        - Column[z07_compactvaluefiel]  <container>
          - TextField[z08_field]  <leaf>
      - Text[Name is required]  <leaf>
      - Column[z10_muscleselector]  <container>
        - Column[z11_column]  <container>
          - Text[Primary muscles *]  <leaf>
          - Column[z13_compactmultisele]  <container>
            - Column[z14_box]  <container>
              - Row[z15_row]  <container>
                - Text[, ]  <leaf>
                - Icon[Change]  <leaf>
              - Column[z18_dropdownmenu]  <container>
                - Column[z19_dropdownmenuitem]  <container>
                  - Text[label(option)]  <leaf>
                  - Icon[z21_icon]  <leaf>
                  - Spacer[z22_spacer]  <leaf>
          - Text[Select at least one primary mu…]  <leaf>
      - Column[z24_muscleselector]  <container>
        - Column[z25_column]  <container>
          - Text[Secondary muscles]  <leaf>
          - Column[z27_compactmultisele]  <container>
            - Column[z28_box]  <container>
              - Row[z29_row]  <container>
                - Text[, ]  <leaf>
                - Icon[Change]  <leaf>
              - Column[z32_dropdownmenu]  <container>
                - Column[z33_dropdownmenuitem]  <container>
                  - Text[label(option)]  <leaf>
                  - Icon[z35_icon]  <leaf>
                  - Spacer[z36_spacer]  <leaf>
          - Text[Select at least one primary mu…]  <leaf>
      - Column[z38_enumdropdown]  <container>
        - Column[z39_labeledfield]  <container>
          - Column[z40_column]  <container>
            - Column[z41_fieldlabel]  <container>
              - Text[Movement pattern]  <leaf>
          - Column[z43_compactdropdown]  <container>
            - Column[z44_box]  <container>
              - Column[z45_roundedcornersha]  <leaf>
              - Row[z46_row]  <container>
                - Text[label(selected)]  <leaf>
                - Icon[Change]  <leaf>
              - Column[z49_dropdownmenu]  <container>
                - Column[z50_dropdownmenuitem]  <container>
                  - Text[label(option)]  <leaf>
      - Column[z52_enumdropdown]  <container>
        - Column[z53_labeledfield]  <container>
          - Column[z54_column]  <container>
            - Column[z55_fieldlabel]  <container>
              - Text[Equipment]  <leaf>
          - Column[z57_compactdropdown]  <container>
            - Column[z58_box]  <container>
              - Column[z59_roundedcornersha]  <leaf>
              - Row[z60_row]  <container>
                - Text[label(selected)]  <leaf>
                - Icon[Change]  <leaf>
              - Column[z63_dropdownmenu]  <container>
                - Column[z64_dropdownmenuitem]  <container>
                  - Text[label(option)]  <leaf>
      - Row[z66_row]  <container>
        - Column[z67_compacttoggle]  <container>
          - Row[z68_row]  <container>
            - Text[Unilateral]  <leaf>
            - Column[z70_switch]  <leaf>
        - Column[z71_compacttoggle]  <container>
          - Row[z72_row]  <container>
            - Text[Compound]  <leaf>
            - Column[z74_switch]  <leaf>
      - Column[z75_seedsourcedropdo]  <container>
        - Column[z76_column]  <container>
          - Column[z77_labeledfield]  <container>
            - Column[z78_column]  <container>
              - Column[z79_fieldlabel]  <container>
                - Text[Base starting weight on (optio…]  <leaf>
            - Column[z81_compactdropdown]  <container>
              - Column[z82_box]  <container>
                - Column[z83_roundedcornersha]  <leaf>
                - Row[z84_row]  <container>
                  - Text[label(selected)]  <leaf>
                  - Icon[Change]  <leaf>
                - Column[z87_dropdownmenu]  <container>
                  - Column[z88_dropdownmenuitem]  <container>
                    - Text[label(option)]  <leaf>
          - Text[For a new movement, we'll star…]  <leaf>
      - TextField[Form notes (optional)]  <leaf>
      - TextField[Coaching cues (optional)]  <leaf>
      - Column[z93_labeledfield]  <container>
        - Column[z94_column]  <container>
          - Column[z95_fieldlabel]  <container>
            - Text[Video link (optional)]  <leaf>
        - Column[z97_compactvaluefiel]  <container>
          - TextField[z98_field]  <leaf>
      - Spacer[z99_spacer]  <leaf>
    - Column[z100_topappbar]  <container>
      - Text[Edit exercise|New exercise]  <leaf>
      - Icon[Back]  <leaf>
      - Icon[Save]  <leaf>

---
## verify vs Compose source (ExerciseCreateScreen)
- distinct leaf signatures matched: 18/18 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 104 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (exercise_create_screen.py)
- leaf signatures shared:        13
- generated-only (other states / not in this trace): 5
- hand-built-only (helper glyphs / human representation): 2
    HB-only  F:·DYN·
    HB-only  T:Save
    GEN-only I:Back
    GEN-only I:Change
    GEN-only I:Save
    GEN-only T:Name is required
    GEN-only T:Select at least one primary mu…
