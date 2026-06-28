# PseudoUI generated kit screen -- gym_editor  (from Compose GymEditorScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (68 calls)
```python
ui.define_box("gym_editor_z00_launchedeffect", "content", "V")
ui.define_box("gym_editor_z01_scaffold", "content", "V")
ui.define_box("gym_editor_z02_box", "gym_editor_z01_scaffold", "V")
ui.define_box("gym_editor_z03_circularprogress", "gym_editor_z02_box", "V")
ui.define_box("gym_editor_z04_lazycolumn", "gym_editor_z01_scaffold", "V")
ui.define_box("gym_editor_z05_labeledfield", "gym_editor_z04_lazycolumn", "V")
ui.define_box("gym_editor_z06_column", "gym_editor_z05_labeledfield", "V")
ui.define_box("gym_editor_z07_fieldlabel", "gym_editor_z06_column", "V")
ui.define_text("gym_editor_z08_gym_name", "gym_editor_z07_fieldlabel", "Gym name")
ui.define_box("gym_editor_z09_compactvaluefiel", "gym_editor_z05_labeledfield", "V")
ui.define_input_zone("gym_editor_z10_field", "gym_editor_z09_compactvaluefiel", "", "")
ui.define_text("gym_editor_z11_equipment", "gym_editor_z04_lazycolumn", "Equipment")
ui.define_divider_zone("gym_editor_z12_divider", "gym_editor_z04_lazycolumn")
ui.define_text("gym_editor_z13_no_equipment_add", "gym_editor_z04_lazycolumn", "No equipment added yet.")
ui.define_box("gym_editor_z14_row", "gym_editor_z04_lazycolumn", "H")
ui.define_text("gym_editor_z15_type_displayname", "gym_editor_z14_row", "type.displayName()")
ui.define_icon("gym_editor_z16_collapse_expand", "gym_editor_z14_row", "Collapse|Expand")
ui.define_box("gym_editor_z17_equipmentrow", "gym_editor_z04_lazycolumn", "V")
ui.define_box("gym_editor_z18_listitem", "gym_editor_z17_equipmentrow", "V")
ui.define_text("gym_editor_z19_draft_name_ifbla", "gym_editor_z18_listitem", "draft.name.ifBlank { draft.typ…")
ui.define_text("gym_editor_z20_x", "gym_editor_z18_listitem", " · ")
ui.define_icon("gym_editor_z21_remove", "gym_editor_z18_listitem", "Remove")
ui.define_spacer_zone("gym_editor_z22_spacer", "gym_editor_z04_lazycolumn")
ui.define_box("gym_editor_z23_topappbar", "gym_editor_z01_scaffold", "V")
ui.define_text("gym_editor_z24_new_gym_edit_gym", "gym_editor_z23_topappbar", "New gym|Edit gym")
ui.define_icon("gym_editor_z25_back", "gym_editor_z23_topappbar", "Back")
ui.define_button("gym_editor_z26_save", "gym_editor_z23_topappbar", "Save")
ui.define_icon("gym_editor_z27_add_equipment", "gym_editor_z01_scaffold", "Add equipment")
ui.define_box("gym_editor_z28_addequipmentdial", "content", "V")
ui.define_box("gym_editor_z29_alertdialog", "gym_editor_z28_addequipmentdial", "V")
ui.define_text("gym_editor_z30_add_equipment", "gym_editor_z29_alertdialog", "Add equipment")
ui.define_box("gym_editor_z31_column", "gym_editor_z29_alertdialog", "V")
ui.define_box("gym_editor_z32_labeledfield", "gym_editor_z31_column", "V")
ui.define_box("gym_editor_z33_column", "gym_editor_z32_labeledfield", "V")
ui.define_box("gym_editor_z34_fieldlabel", "gym_editor_z33_column", "V")
ui.define_text("gym_editor_z35_type", "gym_editor_z34_fieldlabel", "Type")
ui.define_box("gym_editor_z36_compactdropdown", "gym_editor_z32_labeledfield", "V")
ui.define_box("gym_editor_z37_box", "gym_editor_z36_compactdropdown", "V")
ui.define_box("gym_editor_z38_roundedcornersha", "gym_editor_z37_box", "V")
ui.define_box("gym_editor_z39_row", "gym_editor_z37_box", "H")
ui.define_text("gym_editor_z40_label_selected", "gym_editor_z39_row", "label(selected)")
ui.define_icon("gym_editor_z41_change", "gym_editor_z39_row", "Change")
ui.define_box("gym_editor_z42_dropdownmenu", "gym_editor_z37_box", "V")
ui.define_box("gym_editor_z43_dropdownmenuitem", "gym_editor_z42_dropdownmenu", "V")
ui.define_text("gym_editor_z44_label_option", "gym_editor_z43_dropdownmenuitem", "label(option)")
ui.define_box("gym_editor_z45_labeledfield", "gym_editor_z31_column", "V")
ui.define_box("gym_editor_z46_column", "gym_editor_z45_labeledfield", "V")
ui.define_box("gym_editor_z47_fieldlabel", "gym_editor_z46_column", "V")
ui.define_text("gym_editor_z48_name_optional", "gym_editor_z47_fieldlabel", "Name (optional)")
ui.define_box("gym_editor_z49_compactvaluefiel", "gym_editor_z45_labeledfield", "V")
ui.define_input_zone("gym_editor_z50_field", "gym_editor_z49_compactvaluefiel", "", "")
ui.define_box("gym_editor_z51_row", "gym_editor_z31_column", "H")
ui.define_box("gym_editor_z52_labeledfield", "gym_editor_z51_row", "V")
ui.define_box("gym_editor_z53_column", "gym_editor_z52_labeledfield", "V")
ui.define_box("gym_editor_z54_fieldlabel", "gym_editor_z53_column", "V")
ui.define_text("gym_editor_z55_weight", "gym_editor_z54_fieldlabel", "Weight")
ui.define_box("gym_editor_z56_compactvaluefiel", "gym_editor_z52_labeledfield", "V")
ui.define_input_zone("gym_editor_z57_field", "gym_editor_z56_compactvaluefiel", "", "")
ui.define_box("gym_editor_z58_singlechoicesegm", "gym_editor_z51_row", "V")
ui.define_box("gym_editor_z59_segmentedbutton", "gym_editor_z58_singlechoicesegm", "V")
ui.define_text("gym_editor_z60_u_name", "gym_editor_z59_segmentedbutton", "u.name")
ui.define_box("gym_editor_z61_row", "gym_editor_z31_column", "H")
ui.define_text("gym_editor_z62_quantity", "gym_editor_z61_row", "Quantity")
ui.define_icon("gym_editor_z63_decrease", "gym_editor_z61_row", "Decrease")
ui.define_text("gym_editor_z64_quantity_tostrin", "gym_editor_z61_row", "quantity.toString()")
ui.define_icon("gym_editor_z65_increase", "gym_editor_z61_row", "Increase")
ui.define_button("gym_editor_z66_add", "gym_editor_z29_alertdialog", "Add")
ui.define_button("gym_editor_z67_cancel", "gym_editor_z29_alertdialog", "Cancel")
```

## generated tree
  - Column[z00_launchedeffect]  <leaf>
  - Column[z01_scaffold]  <container>
    - Column[z02_box]  <container>
      - Column[z03_circularprogress]  <leaf>
    - Column[z04_lazycolumn]  <container>
      - Column[z05_labeledfield]  <container>
        - Column[z06_column]  <container>
          - Column[z07_fieldlabel]  <container>
            - Text[Gym name]  <leaf>
        - Column[z09_compactvaluefiel]  <container>
          - TextField[z10_field]  <leaf>
      - Text[Equipment]  <leaf>
      - Divider[z12_divider]  <leaf>
      - Text[No equipment added yet.]  <leaf>
      - Row[z14_row]  <container>
        - Text[type.displayName()]  <leaf>
        - Icon[Collapse|Expand]  <leaf>
      - Column[z17_equipmentrow]  <container>
        - Column[z18_listitem]  <container>
          - Text[draft.name.ifBlank { draft.typ…]  <leaf>
          - Text[ · ]  <leaf>
          - Icon[Remove]  <leaf>
      - Spacer[z22_spacer]  <leaf>
    - Column[z23_topappbar]  <container>
      - Text[New gym|Edit gym]  <leaf>
      - Icon[Back]  <leaf>
      - Button[Save]  <leaf>
    - Icon[Add equipment]  <leaf>
  - Column[z28_addequipmentdial]  <container>
    - Column[z29_alertdialog]  <container>
      - Text[Add equipment]  <leaf>
      - Column[z31_column]  <container>
        - Column[z32_labeledfield]  <container>
          - Column[z33_column]  <container>
            - Column[z34_fieldlabel]  <container>
              - Text[Type]  <leaf>
          - Column[z36_compactdropdown]  <container>
            - Column[z37_box]  <container>
              - Column[z38_roundedcornersha]  <leaf>
              - Row[z39_row]  <container>
                - Text[label(selected)]  <leaf>
                - Icon[Change]  <leaf>
              - Column[z42_dropdownmenu]  <container>
                - Column[z43_dropdownmenuitem]  <container>
                  - Text[label(option)]  <leaf>
        - Column[z45_labeledfield]  <container>
          - Column[z46_column]  <container>
            - Column[z47_fieldlabel]  <container>
              - Text[Name (optional)]  <leaf>
          - Column[z49_compactvaluefiel]  <container>
            - TextField[z50_field]  <leaf>
        - Row[z51_row]  <container>
          - Column[z52_labeledfield]  <container>
            - Column[z53_column]  <container>
              - Column[z54_fieldlabel]  <container>
                - Text[Weight]  <leaf>
            - Column[z56_compactvaluefiel]  <container>
              - TextField[z57_field]  <leaf>
          - Column[z58_singlechoicesegm]  <container>
            - Column[z59_segmentedbutton]  <container>
              - Text[u.name]  <leaf>
        - Row[z61_row]  <container>
          - Text[Quantity]  <leaf>
          - Icon[Decrease]  <leaf>
          - Text[quantity.toString()]  <leaf>
          - Icon[Increase]  <leaf>
      - Button[Add]  <leaf>
      - Button[Cancel]  <leaf>

---
## verify vs Compose source (GymEditorScreen)
- distinct leaf signatures matched: 19/20 = 95%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 68 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (gym_editor_screen.py)
- leaf signatures shared:        2
- generated-only (other states / not in this trace): 17
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:Add equipment
    GEN-only I:Back
    GEN-only I:Change
    GEN-only I:Decrease
    GEN-only I:Increase
    GEN-only I:Remove
    GEN-only I:·DYN·
    GEN-only T:Add
    GEN-only T:Add equipment
    GEN-only T:Cancel
    GEN-only T:Equipment
    GEN-only T:Gym name
