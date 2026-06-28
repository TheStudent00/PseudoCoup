# PseudoUI generated kit screen -- program_editor  (from Compose ProgramEditorScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (152 calls)
```python
ui.define_box("program_editor_z00_launchedeffect", "content", "V")
ui.define_box("program_editor_z01_scaffold", "content", "V")
ui.define_box("program_editor_z02_lazycolumn", "program_editor_z01_scaffold", "V")
ui.define_text("program_editor_z03_name", "program_editor_z02_lazycolumn", "name")
ui.define_box("program_editor_z04_labeledfield", "program_editor_z02_lazycolumn", "V")
ui.define_box("program_editor_z05_column", "program_editor_z04_labeledfield", "V")
ui.define_box("program_editor_z06_fieldlabel", "program_editor_z05_column", "V")
ui.define_text("program_editor_z07_program_name", "program_editor_z06_fieldlabel", "Program name")
ui.define_box("program_editor_z08_compactvaluefiel", "program_editor_z04_labeledfield", "V")
ui.define_input_zone("program_editor_z09_field", "program_editor_z08_compactvaluefiel", "", "")
ui.define_text("program_editor_z10_description", "program_editor_z02_lazycolumn", "description")
ui.define_input_zone("program_editor_z11_description", "program_editor_z02_lazycolumn", "", "Description")
ui.define_box("program_editor_z12_pathsmultiselect", "program_editor_z02_lazycolumn", "V")
ui.define_box("program_editor_z13_column", "program_editor_z12_pathsmultiselect", "V")
ui.define_box("program_editor_z14_row", "program_editor_z13_column", "H")
ui.define_text("program_editor_z15_linked_paths", "program_editor_z14_row", "Linked paths")
ui.define_box("program_editor_z16_row", "program_editor_z14_row", "H")
ui.define_text("program_editor_z17_selectedpathids_", "program_editor_z16_row", "${selectedPathIds.size} select…")
ui.define_icon("program_editor_z18_collapse_expand", "program_editor_z16_row", "Collapse|Expand")
ui.define_spacer_zone("program_editor_z19_spacer", "program_editor_z13_column")
ui.define_box("program_editor_z20_flowrow", "program_editor_z13_column", "H")
ui.define_box("program_editor_z21_filterchip", "program_editor_z20_flowrow", "V")
ui.define_text("program_editor_z22_path_name", "program_editor_z21_filterchip", "path.name")
ui.define_box("program_editor_z23_surface", "program_editor_z02_lazycolumn", "V")
ui.define_text("program_editor_z24_guidance", "program_editor_z23_surface", "guidance")
ui.define_divider_zone("program_editor_z25_divider", "program_editor_z02_lazycolumn")
ui.define_spacer_zone("program_editor_z26_spacer", "program_editor_z02_lazycolumn")
ui.define_box("program_editor_z27_row", "program_editor_z02_lazycolumn", "H")
ui.define_text("program_editor_z28_weeks", "program_editor_z27_row", "Weeks")
ui.define_button("program_editor_z29_add_week", "program_editor_z27_row", "Add week")
ui.define_box("program_editor_z30_roadmapview", "program_editor_z02_lazycolumn", "V")
ui.define_text("program_editor_z31_this_program_doe", "program_editor_z30_roadmapview", "This program doesn't have any …")
ui.define_box("program_editor_z32_column", "program_editor_z30_roadmapview", "V")
ui.define_box("program_editor_z33_railrow", "program_editor_z32_column", "V")
ui.define_box("program_editor_z34_row", "program_editor_z33_railrow", "H")
ui.define_box("program_editor_z35_column", "program_editor_z34_row", "V")
ui.define_box("program_editor_z36_box", "program_editor_z35_column", "V")
ui.define_box("program_editor_z37_box", "program_editor_z35_column", "V")
ui.define_box("program_editor_z38_box", "program_editor_z34_row", "V")
ui.define_box("program_editor_z39_macrocontent", "program_editor_z33_railrow", "V")
ui.define_box("program_editor_z40_column", "program_editor_z39_macrocontent", "V")
ui.define_text("program_editor_z41_annotatedtitle", "program_editor_z40_column", "annotatedTitle")
ui.define_text("program_editor_z42_macro_durationla", "program_editor_z40_column", " — ${macro.durationLabel}")
ui.define_box("program_editor_z43_phasecontent", "program_editor_z33_railrow", "V")
ui.define_box("program_editor_z44_column", "program_editor_z43_phasecontent", "V")
ui.define_text("program_editor_z45_phase_label_phas", "program_editor_z44_column", "${phase.label} · ${phase.typeL…")
ui.define_text("program_editor_z46_phase_durationla", "program_editor_z44_column", " — ${phase.durationLabel}")
ui.define_box("program_editor_z47_weekcontent", "program_editor_z33_railrow", "V")
ui.define_box("program_editor_z48_column", "program_editor_z47_weekcontent", "V")
ui.define_box("program_editor_z49_column", "program_editor_z48_column", "V")
ui.define_text("program_editor_z50_week_label", "program_editor_z49_column", "week.label")
ui.define_text("program_editor_z51_week_typelabel", "program_editor_z49_column", "week.typeLabel")
ui.define_spacer_zone("program_editor_z52_spacer", "program_editor_z48_column")
ui.define_box("program_editor_z53_youareherepill", "program_editor_z48_column", "V")
ui.define_box("program_editor_z54_surface", "program_editor_z53_youareherepill", "V")
ui.define_text("program_editor_z55_you_are_here", "program_editor_z54_surface", "You are here")
ui.define_spacer_zone("program_editor_z56_spacer", "program_editor_z48_column")
ui.define_box("program_editor_z57_dayrow", "program_editor_z48_column", "V")
ui.define_box("program_editor_z58_row", "program_editor_z57_dayrow", "H")
ui.define_box("program_editor_z59_box", "program_editor_z58_row", "V")
ui.define_box("program_editor_z60_box", "program_editor_z58_row", "V")
ui.define_spacer_zone("program_editor_z61_spacer", "program_editor_z58_row")
ui.define_text("program_editor_z62_day_name", "program_editor_z58_row", "day.name")
ui.define_text("program_editor_z63_up_next", "program_editor_z58_row", "Up next")
ui.define_box("program_editor_z64_railmarker", "program_editor_z33_railrow", "V")
ui.define_box("program_editor_z65_box", "program_editor_z64_railmarker", "V")
ui.define_box("program_editor_z66_box", "program_editor_z64_railmarker", "V")
ui.define_box("program_editor_z67_weeknode", "program_editor_z64_railmarker", "V")
ui.define_box("program_editor_z68_box", "program_editor_z67_weeknode", "V")
ui.define_icon("program_editor_z69_completed", "program_editor_z68_box", "Completed")
ui.define_box("program_editor_z70_box", "program_editor_z67_weeknode", "V")
ui.define_box("program_editor_z71_box", "program_editor_z67_weeknode", "V")
ui.define_box("program_editor_z72_box", "program_editor_z67_weeknode", "V")
ui.define_box("program_editor_z73_cycledetaildialo", "program_editor_z30_roadmapview", "V")
ui.define_box("program_editor_z74_dialog", "program_editor_z73_cycledetaildialo", "V")
ui.define_box("program_editor_z75_wflcard", "program_editor_z74_dialog", "V")
ui.define_box("program_editor_z76_roundedcornersha", "program_editor_z75_wflcard", "V")
ui.define_box("program_editor_z77_borderstroke", "program_editor_z75_wflcard", "V")
ui.define_box("program_editor_z78_card", "program_editor_z75_wflcard", "V")
ui.define_box("program_editor_z79_card", "program_editor_z75_wflcard", "V")
ui.define_box("program_editor_z80_column", "program_editor_z75_wflcard", "V")
ui.define_text("program_editor_z81_detail_title", "program_editor_z80_column", "detail.title")
ui.define_spacer_zone("program_editor_z82_spacer", "program_editor_z80_column")
ui.define_text("program_editor_z83_subtitle", "program_editor_z80_column", "subtitle")
ui.define_spacer_zone("program_editor_z84_spacer", "program_editor_z80_column")
ui.define_divider_zone("program_editor_z85_divider", "program_editor_z80_column")
ui.define_spacer_zone("program_editor_z86_spacer", "program_editor_z80_column")
ui.define_box("program_editor_z87_column", "program_editor_z80_column", "V")
ui.define_box("program_editor_z88_detailsection", "program_editor_z87_column", "V")
ui.define_box("program_editor_z89_column", "program_editor_z88_detailsection", "V")
ui.define_text("program_editor_z90_this_cycle", "program_editor_z89_column", "This cycle")
ui.define_spacer_zone("program_editor_z91_spacer", "program_editor_z89_column")
ui.define_text("program_editor_z92_detail_descripti", "program_editor_z89_column", "detail.description!!")
ui.define_box("program_editor_z93_detailsection", "program_editor_z87_column", "V")
ui.define_box("program_editor_z94_column", "program_editor_z93_detailsection", "V")
ui.define_text("program_editor_z95_the_science_behi", "program_editor_z94_column", "The science behind this")
ui.define_spacer_zone("program_editor_z96_spacer", "program_editor_z94_column")
ui.define_text("program_editor_z97_detail_scienceno", "program_editor_z94_column", "detail.scienceNote!!")
ui.define_text("program_editor_z98_no_details_for_t", "program_editor_z87_column", "No details for this cycle yet.")
ui.define_spacer_zone("program_editor_z99_spacer", "program_editor_z80_column")
ui.define_button("program_editor_z100_close", "program_editor_z80_column", "Close")
ui.define_text("program_editor_z101_no_structure_yet", "program_editor_z02_lazycolumn", "No structure yet. Tap Add Week…")
ui.define_box("program_editor_z102_topappbar", "program_editor_z01_scaffold", "V")
ui.define_text("program_editor_z103_program_details", "program_editor_z102_topappbar", "Program details")
ui.define_icon("program_editor_z104_back", "program_editor_z102_topappbar", "Back")
ui.define_button("program_editor_z105_clone", "program_editor_z102_topappbar", "Clone")
ui.define_button("program_editor_z106_swap", "program_editor_z102_topappbar", "Swap")
ui.define_button("program_editor_z107_join", "program_editor_z102_topappbar", "Join")
ui.define_box("program_editor_z108_dayexercisesdial", "content", "V")
ui.define_box("program_editor_z109_dialog", "program_editor_z108_dayexercisesdial", "V")
ui.define_box("program_editor_z110_wflcard", "program_editor_z109_dialog", "V")
ui.define_box("program_editor_z111_roundedcornersha", "program_editor_z110_wflcard", "V")
ui.define_box("program_editor_z112_borderstroke", "program_editor_z110_wflcard", "V")
ui.define_box("program_editor_z113_card", "program_editor_z110_wflcard", "V")
ui.define_box("program_editor_z114_card", "program_editor_z110_wflcard", "V")
ui.define_box("program_editor_z115_column", "program_editor_z110_wflcard", "V")
ui.define_text("program_editor_z116_preview_dayname", "program_editor_z115_column", "preview.dayName")
ui.define_divider_zone("program_editor_z117_divider", "program_editor_z115_column")
ui.define_text("program_editor_z118_no_exercises_pro", "program_editor_z115_column", "No exercises programmed for th…")
ui.define_box("program_editor_z119_column", "program_editor_z115_column", "V")
ui.define_box("program_editor_z120_row", "program_editor_z119_column", "H")
ui.define_box("program_editor_z121_box", "program_editor_z120_row", "V")
ui.define_box("program_editor_z122_column", "program_editor_z120_row", "V")
ui.define_text("program_editor_z123_exercise_name", "program_editor_z122_column", "exercise.name")
ui.define_text("program_editor_z124_daysetsummary_ex", "program_editor_z122_column", "daySetSummary(exercise, previe…")
ui.define_button("program_editor_z125_close", "program_editor_z115_column", "Close")
ui.define_box("program_editor_z126_adddaydialog", "content", "V")
ui.define_box("program_editor_z127_alertdialog", "program_editor_z126_adddaydialog", "V")
ui.define_text("program_editor_z128_add_day", "program_editor_z127_alertdialog", "Add day")
ui.define_box("program_editor_z129_labeledfield", "program_editor_z127_alertdialog", "V")
ui.define_box("program_editor_z130_column", "program_editor_z129_labeledfield", "V")
ui.define_box("program_editor_z131_fieldlabel", "program_editor_z130_column", "V")
ui.define_text("program_editor_z132_day_name_e_g_pus", "program_editor_z131_fieldlabel", "Day name (e.g. Push A)")
ui.define_box("program_editor_z133_compactvaluefiel", "program_editor_z129_labeledfield", "V")
ui.define_input_zone("program_editor_z134_field", "program_editor_z133_compactvaluefiel", "", "")
ui.define_button("program_editor_z135_add", "program_editor_z127_alertdialog", "Add")
ui.define_button("program_editor_z136_cancel", "program_editor_z127_alertdialog", "Cancel")
ui.define_box("program_editor_z137_alertdialog", "content", "V")
ui.define_text("program_editor_z138_remove_week", "program_editor_z137_alertdialog", "Remove week?")
ui.define_text("program_editor_z139_all_days_and_exe", "program_editor_z137_alertdialog", "All days and exercises in this…")
ui.define_button("program_editor_z140_remove", "program_editor_z137_alertdialog", "Remove")
ui.define_button("program_editor_z141_cancel", "program_editor_z137_alertdialog", "Cancel")
ui.define_box("program_editor_z142_alertdialog", "content", "V")
ui.define_text("program_editor_z143_remove_day", "program_editor_z142_alertdialog", "Remove day?")
ui.define_text("program_editor_z144_all_exercises_in", "program_editor_z142_alertdialog", "All exercises in this day will…")
ui.define_button("program_editor_z145_remove", "program_editor_z142_alertdialog", "Remove")
ui.define_button("program_editor_z146_cancel", "program_editor_z142_alertdialog", "Cancel")
ui.define_box("program_editor_z147_alertdialog", "content", "V")
ui.define_text("program_editor_z148_swap_to_programn", "program_editor_z147_alertdialog", "Swap to $programName?")
ui.define_text("program_editor_z149_switching_progra", "program_editor_z147_alertdialog", "Switching programs will restar…")
ui.define_button("program_editor_z150_swap", "program_editor_z147_alertdialog", "Swap")
ui.define_button("program_editor_z151_cancel", "program_editor_z147_alertdialog", "Cancel")
```

## generated tree
  - Column[z00_launchedeffect]  <leaf>
  - Column[z01_scaffold]  <container>
    - Column[z02_lazycolumn]  <container>
      - Text[name]  <leaf>
      - Column[z04_labeledfield]  <container>
        - Column[z05_column]  <container>
          - Column[z06_fieldlabel]  <container>
            - Text[Program name]  <leaf>
        - Column[z08_compactvaluefiel]  <container>
          - TextField[z09_field]  <leaf>
      - Text[description]  <leaf>
      - TextField[Description]  <leaf>
      - Column[z12_pathsmultiselect]  <container>
        - Column[z13_column]  <container>
          - Row[z14_row]  <container>
            - Text[Linked paths]  <leaf>
            - Row[z16_row]  <container>
              - Text[${selectedPathIds.size} select…]  <leaf>
              - Icon[Collapse|Expand]  <leaf>
          - Spacer[z19_spacer]  <leaf>
          - Row[z20_flowrow]  <container>
            - Column[z21_filterchip]  <container>
              - Text[path.name]  <leaf>
      - Column[z23_surface]  <container>
        - Text[guidance]  <leaf>
      - Divider[z25_divider]  <leaf>
      - Spacer[z26_spacer]  <leaf>
      - Row[z27_row]  <container>
        - Text[Weeks]  <leaf>
        - Button[Add week]  <leaf>
      - Column[z30_roadmapview]  <container>
        - Text[This program doesn't have any …]  <leaf>
        - Column[z32_column]  <container>
          - Column[z33_railrow]  <container>
            - Row[z34_row]  <container>
              - Column[z35_column]  <container>
                - Column[z36_box]  <leaf>
                - Column[z37_box]  <leaf>
              - Column[z38_box]  <leaf>
            - Column[z39_macrocontent]  <container>
              - Column[z40_column]  <container>
                - Text[annotatedTitle]  <leaf>
                - Text[ — ${macro.durationLabel}]  <leaf>
            - Column[z43_phasecontent]  <container>
              - Column[z44_column]  <container>
                - Text[${phase.label} · ${phase.typeL…]  <leaf>
                - Text[ — ${phase.durationLabel}]  <leaf>
            - Column[z47_weekcontent]  <container>
              - Column[z48_column]  <container>
                - Column[z49_column]  <container>
                  - Text[week.label]  <leaf>
                  - Text[week.typeLabel]  <leaf>
                - Spacer[z52_spacer]  <leaf>
                - Column[z53_youareherepill]  <container>
                  - Column[z54_surface]  <container>
                    - Text[You are here]  <leaf>
                - Spacer[z56_spacer]  <leaf>
                - Column[z57_dayrow]  <container>
                  - Row[z58_row]  <container>
                    - Column[z59_box]  <leaf>
                    - Column[z60_box]  <leaf>
                    - Spacer[z61_spacer]  <leaf>
                    - Text[day.name]  <leaf>
                    - Text[Up next]  <leaf>
            - Column[z64_railmarker]  <container>
              - Column[z65_box]  <leaf>
              - Column[z66_box]  <leaf>
              - Column[z67_weeknode]  <container>
                - Column[z68_box]  <container>
                  - Icon[Completed]  <leaf>
                - Column[z70_box]  <leaf>
                - Column[z71_box]  <leaf>
                - Column[z72_box]  <leaf>
        - Column[z73_cycledetaildialo]  <container>
          - Column[z74_dialog]  <container>
            - Column[z75_wflcard]  <container>
              - Column[z76_roundedcornersha]  <leaf>
              - Column[z77_borderstroke]  <leaf>
              - Column[z78_card]  <leaf>
              - Column[z79_card]  <leaf>
              - Column[z80_column]  <container>
                - Text[detail.title]  <leaf>
                - Spacer[z82_spacer]  <leaf>
                - Text[subtitle]  <leaf>
                - Spacer[z84_spacer]  <leaf>
                - Divider[z85_divider]  <leaf>
                - Spacer[z86_spacer]  <leaf>
                - Column[z87_column]  <container>
                  - Column[z88_detailsection]  <container>
                    - Column[z89_column]  <container>
                      - Text[This cycle]  <leaf>
                      - Spacer[z91_spacer]  <leaf>
                      - Text[detail.description!!]  <leaf>
                  - Column[z93_detailsection]  <container>
                    - Column[z94_column]  <container>
                      - Text[The science behind this]  <leaf>
                      - Spacer[z96_spacer]  <leaf>
                      - Text[detail.scienceNote!!]  <leaf>
                  - Text[No details for this cycle yet.]  <leaf>
                - Spacer[z99_spacer]  <leaf>
                - Button[Close]  <leaf>
      - Text[No structure yet. Tap Add Week…]  <leaf>
    - Column[z102_topappbar]  <container>
      - Text[Program details]  <leaf>
      - Icon[Back]  <leaf>
      - Button[Clone]  <leaf>
      - Button[Swap]  <leaf>
      - Button[Join]  <leaf>
  - Column[z108_dayexercisesdial]  <container>
    - Column[z109_dialog]  <container>
      - Column[z110_wflcard]  <container>
        - Column[z111_roundedcornersha]  <leaf>
        - Column[z112_borderstroke]  <leaf>
        - Column[z113_card]  <leaf>
        - Column[z114_card]  <leaf>
        - Column[z115_column]  <container>
          - Text[preview.dayName]  <leaf>
          - Divider[z117_divider]  <leaf>
          - Text[No exercises programmed for th…]  <leaf>
          - Column[z119_column]  <container>
            - Row[z120_row]  <container>
              - Column[z121_box]  <leaf>
              - Column[z122_column]  <container>
                - Text[exercise.name]  <leaf>
                - Text[daySetSummary(exercise, previe…]  <leaf>
          - Button[Close]  <leaf>
  - Column[z126_adddaydialog]  <container>
    - Column[z127_alertdialog]  <container>
      - Text[Add day]  <leaf>
      - Column[z129_labeledfield]  <container>
        - Column[z130_column]  <container>
          - Column[z131_fieldlabel]  <container>
            - Text[Day name (e.g. Push A)]  <leaf>
        - Column[z133_compactvaluefiel]  <container>
          - TextField[z134_field]  <leaf>
      - Button[Add]  <leaf>
      - Button[Cancel]  <leaf>
  - Column[z137_alertdialog]  <container>
    - Text[Remove week?]  <leaf>
    - Text[All days and exercises in this…]  <leaf>
    - Button[Remove]  <leaf>
    - Button[Cancel]  <leaf>
  - Column[z142_alertdialog]  <container>
    - Text[Remove day?]  <leaf>
    - Text[All exercises in this day will…]  <leaf>
    - Button[Remove]  <leaf>
    - Button[Cancel]  <leaf>
  - Column[z147_alertdialog]  <container>
    - Text[Swap to $programName?]  <leaf>
    - Text[Switching programs will restar…]  <leaf>
    - Button[Swap]  <leaf>
    - Button[Cancel]  <leaf>

---
## verify vs Compose source (ProgramEditorScreen)
- distinct leaf signatures matched: 31/31 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 152 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (program_editor_screen.py)
- leaf signatures shared:        3
- generated-only (other states / not in this trace): 28
- hand-built-only (helper glyphs / human representation): 0
    GEN-only F:Description
    GEN-only I:Back
    GEN-only I:Completed
    GEN-only I:·DYN·
    GEN-only T:Add
    GEN-only T:Add day
    GEN-only T:Add week
    GEN-only T:All days and exercises in this…
    GEN-only T:All exercises in this day will…
    GEN-only T:Cancel
    GEN-only T:Clone
    GEN-only T:Close
