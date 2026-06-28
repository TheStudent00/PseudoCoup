# PseudoUI generated kit screen -- gym_list  (from Compose GymListScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (38 calls)
```python
ui.define_box("gym_list_z00_scaffold", "content", "V")
ui.define_box("gym_list_z01_box", "gym_list_z00_scaffold", "V")
ui.define_text("gym_list_z02_no_gyms_yet_tap_", "gym_list_z01_box", "No gyms yet. Tap + to add one.")
ui.define_box("gym_list_z03_lazycolumn", "gym_list_z00_scaffold", "V")
ui.define_box("gym_list_z04_gymlistitem", "gym_list_z03_lazycolumn", "V")
ui.define_box("gym_list_z05_wflcard", "gym_list_z04_gymlistitem", "V")
ui.define_box("gym_list_z06_roundedcornersha", "gym_list_z05_wflcard", "V")
ui.define_box("gym_list_z07_borderstroke", "gym_list_z05_wflcard", "V")
ui.define_box("gym_list_z08_card", "gym_list_z05_wflcard", "V")
ui.define_box("gym_list_z09_card", "gym_list_z05_wflcard", "V")
ui.define_box("gym_list_z10_column", "gym_list_z05_wflcard", "V")
ui.define_box("gym_list_z11_row", "gym_list_z10_column", "H")
ui.define_text("gym_list_z12_gym_name", "gym_list_z11_row", "gym.name")
ui.define_box("gym_list_z13_assistchip", "gym_list_z11_row", "V")
ui.define_text("gym_list_z14_active", "gym_list_z13_assistchip", "Active")
ui.define_icon("gym_list_z15_icon", "gym_list_z13_assistchip", "")
ui.define_button("gym_list_z16_set_active", "gym_list_z11_row", "Set active")
ui.define_spacer_zone("gym_list_z17_spacer", "gym_list_z10_column")
ui.define_text("gym_list_z18_type_emoji_type_", "gym_list_z10_column", "${type.emoji} ${type.displayNa…")
ui.define_spacer_zone("gym_list_z19_spacer", "gym_list_z10_column")
ui.define_box("gym_list_z20_row", "gym_list_z10_column", "H")
ui.define_box("gym_list_z21_labeledstat", "gym_list_z20_row", "V")
ui.define_box("gym_list_z22_column", "gym_list_z21_labeledstat", "V")
ui.define_text("gym_list_z23_equipment", "gym_list_z22_column", "Equipment")
ui.define_text("gym_list_z24_equipmentlist_si", "gym_list_z22_column", "${equipmentList.size} items")
ui.define_spacer_zone("gym_list_z25_spacer", "gym_list_z10_column")
ui.define_text("gym_list_z26_equipment", "gym_list_z10_column", "Equipment")
ui.define_box("gym_list_z27_box", "gym_list_z10_column", "V")
ui.define_text("gym_list_z28_equipmentnames", "gym_list_z27_box", "equipmentNames")
ui.define_box("gym_list_z29_box", "gym_list_z27_box", "V")
ui.define_text("gym_list_z30_no_equipment_lis", "gym_list_z10_column", "No equipment listed")
ui.define_spacer_zone("gym_list_z31_spacer", "gym_list_z10_column")
ui.define_box("gym_list_z32_row", "gym_list_z10_column", "H")
ui.define_button("gym_list_z33_delete_gym", "gym_list_z32_row", "Delete gym")
ui.define_box("gym_list_z34_topappbar", "gym_list_z00_scaffold", "V")
ui.define_text("gym_list_z35_gym_profiles", "gym_list_z34_topappbar", "Gym profiles")
ui.define_icon("gym_list_z36_back", "gym_list_z34_topappbar", "Back")
ui.define_icon("gym_list_z37_add_gym", "gym_list_z00_scaffold", "Add gym")
```

## generated tree
  - Column[z00_scaffold]  <container>
    - Column[z01_box]  <container>
      - Text[No gyms yet. Tap + to add one.]  <leaf>
    - Column[z03_lazycolumn]  <container>
      - Column[z04_gymlistitem]  <container>
        - Column[z05_wflcard]  <container>
          - Column[z06_roundedcornersha]  <leaf>
          - Column[z07_borderstroke]  <leaf>
          - Column[z08_card]  <leaf>
          - Column[z09_card]  <leaf>
          - Column[z10_column]  <container>
            - Row[z11_row]  <container>
              - Text[gym.name]  <leaf>
              - Column[z13_assistchip]  <container>
                - Text[Active]  <leaf>
                - Icon[z15_icon]  <leaf>
              - Button[Set active]  <leaf>
            - Spacer[z17_spacer]  <leaf>
            - Text[${type.emoji} ${type.displayNa…]  <leaf>
            - Spacer[z19_spacer]  <leaf>
            - Row[z20_row]  <container>
              - Column[z21_labeledstat]  <container>
                - Column[z22_column]  <container>
                  - Text[Equipment]  <leaf>
                  - Text[${equipmentList.size} items]  <leaf>
            - Spacer[z25_spacer]  <leaf>
            - Text[Equipment]  <leaf>
            - Column[z27_box]  <container>
              - Text[equipmentNames]  <leaf>
              - Column[z29_box]  <leaf>
            - Text[No equipment listed]  <leaf>
            - Spacer[z31_spacer]  <leaf>
            - Row[z32_row]  <container>
              - Button[Delete gym]  <leaf>
    - Column[z34_topappbar]  <container>
      - Text[Gym profiles]  <leaf>
      - Icon[Back]  <leaf>
    - Icon[Add gym]  <leaf>

---
## verify vs Compose source (GymListScreen)
- distinct leaf signatures matched: 10/10 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 38 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (gym_list_screen.py)
- leaf signatures shared:        4
- generated-only (other states / not in this trace): 6
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:Add gym
    GEN-only I:Back
    GEN-only T:Active
    GEN-only T:No equipment listed
    GEN-only T:No gyms yet. Tap + to add one.
    GEN-only T:Set active
