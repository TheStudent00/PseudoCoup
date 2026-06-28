# PseudoUI generated kit screen -- log_cardio  (from Compose LogCardioScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (58 calls)
```python
ui.define_box("log_cardio_z00_launchedeffect", "content", "V")
ui.define_box("log_cardio_z01_alertdialog", "content", "V")
ui.define_text("log_cardio_z02_oops_already_log", "log_cardio_z01_alertdialog", "Oops — already logged?")
ui.define_text("log_cardio_z03_was_this_already", "log_cardio_z01_alertdialog", "Was this already logged automa…")
ui.define_button("log_cardio_z04_keep_both", "log_cardio_z01_alertdialog", "Keep both")
ui.define_button("log_cardio_z05_it_s_already_log", "log_cardio_z01_alertdialog", "It's already logged")
ui.define_box("log_cardio_z06_scaffold", "content", "V")
ui.define_box("log_cardio_z07_column", "log_cardio_z06_scaffold", "V")
ui.define_text("log_cardio_z08_log_cardio_or_ot", "log_cardio_z07_column", "Log cardio or other activity s…")
ui.define_spacer_zone("log_cardio_z09_spacer", "log_cardio_z07_column")
ui.define_text("log_cardio_z10_activity", "log_cardio_z07_column", "Activity")
ui.define_spacer_zone("log_cardio_z11_spacer", "log_cardio_z07_column")
ui.define_box("log_cardio_z12_flowrow", "log_cardio_z07_column", "H")
ui.define_box("log_cardio_z13_filterchip", "log_cardio_z12_flowrow", "V")
ui.define_text("log_cardio_z14_type_displayname", "log_cardio_z13_filterchip", "type.displayName()")
ui.define_spacer_zone("log_cardio_z15_spacer", "log_cardio_z07_column")
ui.define_text("log_cardio_z16_when", "log_cardio_z07_column", "When")
ui.define_spacer_zone("log_cardio_z17_spacer", "log_cardio_z07_column")
ui.define_button("log_cardio_z18_whenlabel_state_", "log_cardio_z07_column", "whenLabel(state.selectedDate, …")
ui.define_box("log_cardio_z19_cardiodatepicker", "log_cardio_z07_column", "V")
ui.define_box("log_cardio_z20_datepickerdialog", "log_cardio_z19_cardiodatepicker", "V")
ui.define_box("log_cardio_z21_datepicker", "log_cardio_z20_datepickerdialog", "V")
ui.define_button("log_cardio_z22_ok", "log_cardio_z20_datepickerdialog", "OK")
ui.define_button("log_cardio_z23_cancel", "log_cardio_z20_datepickerdialog", "Cancel")
ui.define_spacer_zone("log_cardio_z24_spacer", "log_cardio_z07_column")
ui.define_box("log_cardio_z25_labeledfield", "log_cardio_z07_column", "V")
ui.define_box("log_cardio_z26_column", "log_cardio_z25_labeledfield", "V")
ui.define_box("log_cardio_z27_fieldlabel", "log_cardio_z26_column", "V")
ui.define_text("log_cardio_z28_duration_minutes", "log_cardio_z27_fieldlabel", "Duration (minutes)")
ui.define_box("log_cardio_z29_compactvaluefiel", "log_cardio_z25_labeledfield", "V")
ui.define_input_zone("log_cardio_z30_field", "log_cardio_z29_compactvaluefiel", "", "")
ui.define_spacer_zone("log_cardio_z31_spacer", "log_cardio_z07_column")
ui.define_text("log_cardio_z32_intensity", "log_cardio_z07_column", "Intensity")
ui.define_spacer_zone("log_cardio_z33_spacer", "log_cardio_z07_column")
ui.define_box("log_cardio_z34_singlechoicesegm", "log_cardio_z07_column", "V")
ui.define_box("log_cardio_z35_segmentedbutton", "log_cardio_z34_singlechoicesegm", "V")
ui.define_text("log_cardio_z36_option_label", "log_cardio_z35_segmentedbutton", "option.label()")
ui.define_spacer_zone("log_cardio_z37_spacer", "log_cardio_z07_column")
ui.define_box("log_cardio_z38_row", "log_cardio_z07_column", "H")
ui.define_box("log_cardio_z39_labeledfield", "log_cardio_z38_row", "V")
ui.define_box("log_cardio_z40_column", "log_cardio_z39_labeledfield", "V")
ui.define_box("log_cardio_z41_fieldlabel", "log_cardio_z40_column", "V")
ui.define_text("log_cardio_z42_distance_km", "log_cardio_z41_fieldlabel", "Distance (km)")
ui.define_box("log_cardio_z43_compactvaluefiel", "log_cardio_z39_labeledfield", "V")
ui.define_input_zone("log_cardio_z44_field", "log_cardio_z43_compactvaluefiel", "", "")
ui.define_box("log_cardio_z45_labeledfield", "log_cardio_z38_row", "V")
ui.define_box("log_cardio_z46_column", "log_cardio_z45_labeledfield", "V")
ui.define_box("log_cardio_z47_fieldlabel", "log_cardio_z46_column", "V")
ui.define_text("log_cardio_z48_avg_hr_bpm", "log_cardio_z47_fieldlabel", "Avg HR (bpm)")
ui.define_box("log_cardio_z49_compactvaluefiel", "log_cardio_z45_labeledfield", "V")
ui.define_input_zone("log_cardio_z50_field", "log_cardio_z49_compactvaluefiel", "", "")
ui.define_spacer_zone("log_cardio_z51_spacer", "log_cardio_z07_column")
ui.define_input_zone("log_cardio_z52_notes_optional", "log_cardio_z07_column", "", "Notes (optional)")
ui.define_spacer_zone("log_cardio_z53_spacer", "log_cardio_z07_column")
ui.define_button("log_cardio_z54_save", "log_cardio_z07_column", "Save")
ui.define_box("log_cardio_z55_topappbar", "log_cardio_z06_scaffold", "V")
ui.define_text("log_cardio_z56_log_other_exerci", "log_cardio_z55_topappbar", "Log other exercise")
ui.define_icon("log_cardio_z57_back", "log_cardio_z55_topappbar", "Back")
```

## generated tree
  - Column[z00_launchedeffect]  <leaf>
  - Column[z01_alertdialog]  <container>
    - Text[Oops — already logged?]  <leaf>
    - Text[Was this already logged automa…]  <leaf>
    - Button[Keep both]  <leaf>
    - Button[It's already logged]  <leaf>
  - Column[z06_scaffold]  <container>
    - Column[z07_column]  <container>
      - Text[Log cardio or other activity s…]  <leaf>
      - Spacer[z09_spacer]  <leaf>
      - Text[Activity]  <leaf>
      - Spacer[z11_spacer]  <leaf>
      - Row[z12_flowrow]  <container>
        - Column[z13_filterchip]  <container>
          - Text[type.displayName()]  <leaf>
      - Spacer[z15_spacer]  <leaf>
      - Text[When]  <leaf>
      - Spacer[z17_spacer]  <leaf>
      - Button[whenLabel(state.selectedDate, …]  <leaf>
      - Column[z19_cardiodatepicker]  <container>
        - Column[z20_datepickerdialog]  <container>
          - Column[z21_datepicker]  <leaf>
          - Button[OK]  <leaf>
          - Button[Cancel]  <leaf>
      - Spacer[z24_spacer]  <leaf>
      - Column[z25_labeledfield]  <container>
        - Column[z26_column]  <container>
          - Column[z27_fieldlabel]  <container>
            - Text[Duration (minutes)]  <leaf>
        - Column[z29_compactvaluefiel]  <container>
          - TextField[z30_field]  <leaf>
      - Spacer[z31_spacer]  <leaf>
      - Text[Intensity]  <leaf>
      - Spacer[z33_spacer]  <leaf>
      - Column[z34_singlechoicesegm]  <container>
        - Column[z35_segmentedbutton]  <container>
          - Text[option.label()]  <leaf>
      - Spacer[z37_spacer]  <leaf>
      - Row[z38_row]  <container>
        - Column[z39_labeledfield]  <container>
          - Column[z40_column]  <container>
            - Column[z41_fieldlabel]  <container>
              - Text[Distance (km)]  <leaf>
          - Column[z43_compactvaluefiel]  <container>
            - TextField[z44_field]  <leaf>
        - Column[z45_labeledfield]  <container>
          - Column[z46_column]  <container>
            - Column[z47_fieldlabel]  <container>
              - Text[Avg HR (bpm)]  <leaf>
          - Column[z49_compactvaluefiel]  <container>
            - TextField[z50_field]  <leaf>
      - Spacer[z51_spacer]  <leaf>
      - TextField[Notes (optional)]  <leaf>
      - Spacer[z53_spacer]  <leaf>
      - Button[Save]  <leaf>
    - Column[z55_topappbar]  <container>
      - Text[Log other exercise]  <leaf>
      - Icon[Back]  <leaf>

---
## verify vs Compose source (LogCardioScreen)
- distinct leaf signatures matched: 16/16 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 58 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (log_cardio_screen.py)
- leaf signatures shared:        9
- generated-only (other states / not in this trace): 7
- hand-built-only (helper glyphs / human representation): 2
    HB-only  F:·DYN·
    HB-only  T:Notes (optional)
    GEN-only F:Notes (optional)
    GEN-only I:Back
    GEN-only T:Cancel
    GEN-only T:It's already logged
    GEN-only T:Keep both
    GEN-only T:OK
    GEN-only T:Oops — already logged?
