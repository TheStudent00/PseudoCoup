# PseudoUI generated kit screen -- my_program  (from Compose MyProgramScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (158 calls)
```python
ui.define_box("my_program_z00_box", "content", "V")
ui.define_box("my_program_z01_column", "my_program_z00_box", "V")
ui.define_spacer_zone("my_program_z02_spacer", "my_program_z01_column")
ui.define_box("my_program_z03_noprogram", "my_program_z01_column", "V")
ui.define_box("my_program_z04_column", "my_program_z03_noprogram", "V")
ui.define_text("my_program_z05_no_program_yet", "my_program_z04_column", "No program yet")
ui.define_text("my_program_z06_join_a_program_t", "my_program_z04_column", "Join a program to see your tra…")
ui.define_spacer_zone("my_program_z07_spacer", "my_program_z04_column")
ui.define_button("my_program_z08_browse_programs", "my_program_z04_column", "Browse programs")
ui.define_box("my_program_z09_activeadaptation", "my_program_z01_column", "V")
ui.define_box("my_program_z10_surface", "my_program_z09_activeadaptation", "V")
ui.define_box("my_program_z11_row", "my_program_z10_surface", "H")
ui.define_box("my_program_z12_column", "my_program_z11_row", "V")
ui.define_text("my_program_z13_active", "my_program_z12_column", "Active")
ui.define_text("my_program_z14_data_summary", "my_program_z12_column", "data.summary")
ui.define_text("my_program_z15_manage", "my_program_z11_row", "Manage")
ui.define_spacer_zone("my_program_z16_spacer", "my_program_z01_column")
ui.define_box("my_program_z17_row", "my_program_z01_column", "H")
ui.define_text("my_program_z18_current_program_", "my_program_z17_row", "current.program.name")
ui.define_spacer_zone("my_program_z19_spacer", "my_program_z17_row")
ui.define_box("my_program_z20_enrolledbadge", "my_program_z17_row", "V")
ui.define_box("my_program_z21_surface", "my_program_z20_enrolledbadge", "V")
ui.define_text("my_program_z22_enrolled", "my_program_z21_surface", "Enrolled")
ui.define_spacer_zone("my_program_z23_spacer", "my_program_z01_column")
ui.define_text("my_program_z24_desc", "my_program_z01_column", "desc")
ui.define_spacer_zone("my_program_z25_spacer", "my_program_z01_column")
ui.define_box("my_program_z26_programroadmapvi", "my_program_z01_column", "V")
ui.define_box("my_program_z27_roadmapview", "my_program_z26_programroadmapvi", "V")
ui.define_text("my_program_z28_this_program_doe", "my_program_z27_roadmapview", "This program doesn't have any …")
ui.define_box("my_program_z29_column", "my_program_z27_roadmapview", "V")
ui.define_box("my_program_z30_railrow", "my_program_z29_column", "V")
ui.define_box("my_program_z31_row", "my_program_z30_railrow", "H")
ui.define_box("my_program_z32_column", "my_program_z31_row", "V")
ui.define_box("my_program_z33_box", "my_program_z32_column", "V")
ui.define_box("my_program_z34_box", "my_program_z32_column", "V")
ui.define_box("my_program_z35_box", "my_program_z31_row", "V")
ui.define_box("my_program_z36_macrocontent", "my_program_z30_railrow", "V")
ui.define_box("my_program_z37_column", "my_program_z36_macrocontent", "V")
ui.define_text("my_program_z38_annotatedtitle", "my_program_z37_column", "annotatedTitle")
ui.define_text("my_program_z39_macro_durationla", "my_program_z37_column", " — ${macro.durationLabel}")
ui.define_box("my_program_z40_phasecontent", "my_program_z30_railrow", "V")
ui.define_box("my_program_z41_column", "my_program_z40_phasecontent", "V")
ui.define_text("my_program_z42_phase_label_phas", "my_program_z41_column", "${phase.label} · ${phase.typeL…")
ui.define_text("my_program_z43_phase_durationla", "my_program_z41_column", " — ${phase.durationLabel}")
ui.define_box("my_program_z44_weekcontent", "my_program_z30_railrow", "V")
ui.define_box("my_program_z45_column", "my_program_z44_weekcontent", "V")
ui.define_box("my_program_z46_column", "my_program_z45_column", "V")
ui.define_text("my_program_z47_week_label", "my_program_z46_column", "week.label")
ui.define_text("my_program_z48_week_typelabel", "my_program_z46_column", "week.typeLabel")
ui.define_spacer_zone("my_program_z49_spacer", "my_program_z45_column")
ui.define_box("my_program_z50_youareherepill", "my_program_z45_column", "V")
ui.define_box("my_program_z51_surface", "my_program_z50_youareherepill", "V")
ui.define_text("my_program_z52_you_are_here", "my_program_z51_surface", "You are here")
ui.define_spacer_zone("my_program_z53_spacer", "my_program_z45_column")
ui.define_box("my_program_z54_dayrow", "my_program_z45_column", "V")
ui.define_box("my_program_z55_row", "my_program_z54_dayrow", "H")
ui.define_box("my_program_z56_box", "my_program_z55_row", "V")
ui.define_box("my_program_z57_box", "my_program_z55_row", "V")
ui.define_spacer_zone("my_program_z58_spacer", "my_program_z55_row")
ui.define_text("my_program_z59_day_name", "my_program_z55_row", "day.name")
ui.define_text("my_program_z60_up_next", "my_program_z55_row", "Up next")
ui.define_box("my_program_z61_railmarker", "my_program_z30_railrow", "V")
ui.define_box("my_program_z62_box", "my_program_z61_railmarker", "V")
ui.define_box("my_program_z63_box", "my_program_z61_railmarker", "V")
ui.define_box("my_program_z64_weeknode", "my_program_z61_railmarker", "V")
ui.define_box("my_program_z65_box", "my_program_z64_weeknode", "V")
ui.define_icon("my_program_z66_completed", "my_program_z65_box", "Completed")
ui.define_box("my_program_z67_box", "my_program_z64_weeknode", "V")
ui.define_box("my_program_z68_box", "my_program_z64_weeknode", "V")
ui.define_box("my_program_z69_box", "my_program_z64_weeknode", "V")
ui.define_box("my_program_z70_cycledetaildialo", "my_program_z27_roadmapview", "V")
ui.define_box("my_program_z71_dialog", "my_program_z70_cycledetaildialo", "V")
ui.define_box("my_program_z72_wflcard", "my_program_z71_dialog", "V")
ui.define_box("my_program_z73_roundedcornersha", "my_program_z72_wflcard", "V")
ui.define_box("my_program_z74_borderstroke", "my_program_z72_wflcard", "V")
ui.define_box("my_program_z75_card", "my_program_z72_wflcard", "V")
ui.define_box("my_program_z76_card", "my_program_z72_wflcard", "V")
ui.define_box("my_program_z77_column", "my_program_z72_wflcard", "V")
ui.define_text("my_program_z78_detail_title", "my_program_z77_column", "detail.title")
ui.define_spacer_zone("my_program_z79_spacer", "my_program_z77_column")
ui.define_text("my_program_z80_subtitle", "my_program_z77_column", "subtitle")
ui.define_spacer_zone("my_program_z81_spacer", "my_program_z77_column")
ui.define_divider_zone("my_program_z82_divider", "my_program_z77_column")
ui.define_spacer_zone("my_program_z83_spacer", "my_program_z77_column")
ui.define_box("my_program_z84_column", "my_program_z77_column", "V")
ui.define_box("my_program_z85_detailsection", "my_program_z84_column", "V")
ui.define_box("my_program_z86_column", "my_program_z85_detailsection", "V")
ui.define_text("my_program_z87_this_cycle", "my_program_z86_column", "This cycle")
ui.define_spacer_zone("my_program_z88_spacer", "my_program_z86_column")
ui.define_text("my_program_z89_detail_descripti", "my_program_z86_column", "detail.description!!")
ui.define_box("my_program_z90_detailsection", "my_program_z84_column", "V")
ui.define_box("my_program_z91_column", "my_program_z90_detailsection", "V")
ui.define_text("my_program_z92_the_science_behi", "my_program_z91_column", "The science behind this")
ui.define_spacer_zone("my_program_z93_spacer", "my_program_z91_column")
ui.define_text("my_program_z94_detail_scienceno", "my_program_z91_column", "detail.scienceNote!!")
ui.define_text("my_program_z95_no_details_for_t", "my_program_z84_column", "No details for this cycle yet.")
ui.define_spacer_zone("my_program_z96_spacer", "my_program_z77_column")
ui.define_button("my_program_z97_close", "my_program_z77_column", "Close")
ui.define_spacer_zone("my_program_z98_spacer", "my_program_z01_column")
ui.define_button("my_program_z99_view_other_progr", "my_program_z01_column", "View other programs")
ui.define_spacer_zone("my_program_z100_spacer", "my_program_z01_column")
ui.define_box("my_program_z101_enrolledprograms", "my_program_z00_box", "V")
ui.define_box("my_program_z102_column", "my_program_z101_enrolledprograms", "V")
ui.define_button("my_program_z103_update_program", "my_program_z102_column", "Update program")
ui.define_icon("my_program_z104_close_menu_updat", "my_program_z102_column", "Close menu|Update program")
ui.define_box("my_program_z105_dayexercisesdial", "content", "V")
ui.define_box("my_program_z106_dialog", "my_program_z105_dayexercisesdial", "V")
ui.define_box("my_program_z107_wflcard", "my_program_z106_dialog", "V")
ui.define_box("my_program_z108_roundedcornersha", "my_program_z107_wflcard", "V")
ui.define_box("my_program_z109_borderstroke", "my_program_z107_wflcard", "V")
ui.define_box("my_program_z110_card", "my_program_z107_wflcard", "V")
ui.define_box("my_program_z111_card", "my_program_z107_wflcard", "V")
ui.define_box("my_program_z112_column", "my_program_z107_wflcard", "V")
ui.define_text("my_program_z113_preview_dayname", "my_program_z112_column", "preview.dayName")
ui.define_divider_zone("my_program_z114_divider", "my_program_z112_column")
ui.define_text("my_program_z115_no_exercises_pro", "my_program_z112_column", "No exercises programmed for th…")
ui.define_box("my_program_z116_column", "my_program_z112_column", "V")
ui.define_box("my_program_z117_row", "my_program_z116_column", "H")
ui.define_box("my_program_z118_box", "my_program_z117_row", "V")
ui.define_box("my_program_z119_column", "my_program_z117_row", "V")
ui.define_text("my_program_z120_exercise_name", "my_program_z119_column", "exercise.name")
ui.define_text("my_program_z121_daysetsummary_ex", "my_program_z119_column", "daySetSummary(exercise, previe…")
ui.define_button("my_program_z122_close", "my_program_z112_column", "Close")
ui.define_box("my_program_z123_activeadaptation", "content", "V")
ui.define_box("my_program_z124_modalbottomsheet", "my_program_z123_activeadaptation", "V")
ui.define_box("my_program_z125_column", "my_program_z124_modalbottomsheet", "V")
ui.define_text("my_program_z126_active_adjustmen", "my_program_z125_column", "Active adjustments")
ui.define_spacer_zone("my_program_z127_spacer", "my_program_z125_column")
ui.define_text("my_program_z128_things_currently", "my_program_z125_column", "Things currently changing your…")
ui.define_spacer_zone("my_program_z129_spacer", "my_program_z125_column")
ui.define_box("my_program_z130_adaptationrow", "my_program_z125_column", "V")
ui.define_box("my_program_z131_row", "my_program_z130_adaptationrow", "H")
ui.define_box("my_program_z132_column", "my_program_z131_row", "V")
ui.define_text("my_program_z133_lifeeventtitle_e", "my_program_z132_column", "lifeEventTitle(ev)")
ui.define_text("my_program_z134_it", "my_program_z132_column", "it")
ui.define_button("my_program_z135_1_wk", "my_program_z131_row", "−1 wk")
ui.define_button("my_program_z136_1_wk", "my_program_z131_row", "+1 wk")
ui.define_button("my_program_z137_end", "my_program_z131_row", "End")
ui.define_divider_zone("my_program_z138_divider", "my_program_z130_adaptationrow")
ui.define_box("my_program_z139_adaptationrow", "my_program_z125_column", "V")
ui.define_box("my_program_z140_row", "my_program_z139_adaptationrow", "H")
ui.define_box("my_program_z141_column", "my_program_z140_row", "V")
ui.define_text("my_program_z142_injury_inj_bodyp", "my_program_z141_column", "Injury — ${inj.bodyPart}")
ui.define_text("my_program_z143_it", "my_program_z141_column", "it")
ui.define_button("my_program_z144_1_wk", "my_program_z140_row", "−1 wk")
ui.define_button("my_program_z145_1_wk", "my_program_z140_row", "+1 wk")
ui.define_button("my_program_z146_end", "my_program_z140_row", "End")
ui.define_divider_zone("my_program_z147_divider", "my_program_z139_adaptationrow")
ui.define_box("my_program_z148_adaptationrow", "my_program_z125_column", "V")
ui.define_box("my_program_z149_row", "my_program_z148_adaptationrow", "H")
ui.define_box("my_program_z150_column", "my_program_z149_row", "V")
ui.define_text("my_program_z151_directivetitle_d", "my_program_z150_column", "directiveTitle(d)")
ui.define_text("my_program_z152_it", "my_program_z150_column", "it")
ui.define_button("my_program_z153_1_wk", "my_program_z149_row", "−1 wk")
ui.define_button("my_program_z154_1_wk", "my_program_z149_row", "+1 wk")
ui.define_button("my_program_z155_end", "my_program_z149_row", "End")
ui.define_divider_zone("my_program_z156_divider", "my_program_z148_adaptationrow")
ui.define_spacer_zone("my_program_z157_spacer", "my_program_z125_column")
```

## generated tree
  - Column[z00_box]  <container>
    - Column[z01_column]  <container>
      - Spacer[z02_spacer]  <leaf>
      - Column[z03_noprogram]  <container>
        - Column[z04_column]  <container>
          - Text[No program yet]  <leaf>
          - Text[Join a program to see your tra…]  <leaf>
          - Spacer[z07_spacer]  <leaf>
          - Button[Browse programs]  <leaf>
      - Column[z09_activeadaptation]  <container>
        - Column[z10_surface]  <container>
          - Row[z11_row]  <container>
            - Column[z12_column]  <container>
              - Text[Active]  <leaf>
              - Text[data.summary]  <leaf>
            - Text[Manage]  <leaf>
      - Spacer[z16_spacer]  <leaf>
      - Row[z17_row]  <container>
        - Text[current.program.name]  <leaf>
        - Spacer[z19_spacer]  <leaf>
        - Column[z20_enrolledbadge]  <container>
          - Column[z21_surface]  <container>
            - Text[Enrolled]  <leaf>
      - Spacer[z23_spacer]  <leaf>
      - Text[desc]  <leaf>
      - Spacer[z25_spacer]  <leaf>
      - Column[z26_programroadmapvi]  <container>
        - Column[z27_roadmapview]  <container>
          - Text[This program doesn't have any …]  <leaf>
          - Column[z29_column]  <container>
            - Column[z30_railrow]  <container>
              - Row[z31_row]  <container>
                - Column[z32_column]  <container>
                  - Column[z33_box]  <leaf>
                  - Column[z34_box]  <leaf>
                - Column[z35_box]  <leaf>
              - Column[z36_macrocontent]  <container>
                - Column[z37_column]  <container>
                  - Text[annotatedTitle]  <leaf>
                  - Text[ — ${macro.durationLabel}]  <leaf>
              - Column[z40_phasecontent]  <container>
                - Column[z41_column]  <container>
                  - Text[${phase.label} · ${phase.typeL…]  <leaf>
                  - Text[ — ${phase.durationLabel}]  <leaf>
              - Column[z44_weekcontent]  <container>
                - Column[z45_column]  <container>
                  - Column[z46_column]  <container>
                    - Text[week.label]  <leaf>
                    - Text[week.typeLabel]  <leaf>
                  - Spacer[z49_spacer]  <leaf>
                  - Column[z50_youareherepill]  <container>
                    - Column[z51_surface]  <container>
                      - Text[You are here]  <leaf>
                  - Spacer[z53_spacer]  <leaf>
                  - Column[z54_dayrow]  <container>
                    - Row[z55_row]  <container>
                      - Column[z56_box]  <leaf>
                      - Column[z57_box]  <leaf>
                      - Spacer[z58_spacer]  <leaf>
                      - Text[day.name]  <leaf>
                      - Text[Up next]  <leaf>
              - Column[z61_railmarker]  <container>
                - Column[z62_box]  <leaf>
                - Column[z63_box]  <leaf>
                - Column[z64_weeknode]  <container>
                  - Column[z65_box]  <container>
                    - Icon[Completed]  <leaf>
                  - Column[z67_box]  <leaf>
                  - Column[z68_box]  <leaf>
                  - Column[z69_box]  <leaf>
          - Column[z70_cycledetaildialo]  <container>
            - Column[z71_dialog]  <container>
              - Column[z72_wflcard]  <container>
                - Column[z73_roundedcornersha]  <leaf>
                - Column[z74_borderstroke]  <leaf>
                - Column[z75_card]  <leaf>
                - Column[z76_card]  <leaf>
                - Column[z77_column]  <container>
                  - Text[detail.title]  <leaf>
                  - Spacer[z79_spacer]  <leaf>
                  - Text[subtitle]  <leaf>
                  - Spacer[z81_spacer]  <leaf>
                  - Divider[z82_divider]  <leaf>
                  - Spacer[z83_spacer]  <leaf>
                  - Column[z84_column]  <container>
                    - Column[z85_detailsection]  <container>
                      - Column[z86_column]  <container>
                        - Text[This cycle]  <leaf>
                        - Spacer[z88_spacer]  <leaf>
                        - Text[detail.description!!]  <leaf>
                    - Column[z90_detailsection]  <container>
                      - Column[z91_column]  <container>
                        - Text[The science behind this]  <leaf>
                        - Spacer[z93_spacer]  <leaf>
                        - Text[detail.scienceNote!!]  <leaf>
                    - Text[No details for this cycle yet.]  <leaf>
                  - Spacer[z96_spacer]  <leaf>
                  - Button[Close]  <leaf>
      - Spacer[z98_spacer]  <leaf>
      - Button[View other programs]  <leaf>
      - Spacer[z100_spacer]  <leaf>
    - Column[z101_enrolledprograms]  <container>
      - Column[z102_column]  <container>
        - Button[Update program]  <leaf>
        - Icon[Close menu|Update program]  <leaf>
  - Column[z105_dayexercisesdial]  <container>
    - Column[z106_dialog]  <container>
      - Column[z107_wflcard]  <container>
        - Column[z108_roundedcornersha]  <leaf>
        - Column[z109_borderstroke]  <leaf>
        - Column[z110_card]  <leaf>
        - Column[z111_card]  <leaf>
        - Column[z112_column]  <container>
          - Text[preview.dayName]  <leaf>
          - Divider[z114_divider]  <leaf>
          - Text[No exercises programmed for th…]  <leaf>
          - Column[z116_column]  <container>
            - Row[z117_row]  <container>
              - Column[z118_box]  <leaf>
              - Column[z119_column]  <container>
                - Text[exercise.name]  <leaf>
                - Text[daySetSummary(exercise, previe…]  <leaf>
          - Button[Close]  <leaf>
  - Column[z123_activeadaptation]  <container>
    - Column[z124_modalbottomsheet]  <container>
      - Column[z125_column]  <container>
        - Text[Active adjustments]  <leaf>
        - Spacer[z127_spacer]  <leaf>
        - Text[Things currently changing your…]  <leaf>
        - Spacer[z129_spacer]  <leaf>
        - Column[z130_adaptationrow]  <container>
          - Row[z131_row]  <container>
            - Column[z132_column]  <container>
              - Text[lifeEventTitle(ev)]  <leaf>
              - Text[it]  <leaf>
            - Button[−1 wk]  <leaf>
            - Button[+1 wk]  <leaf>
            - Button[End]  <leaf>
          - Divider[z138_divider]  <leaf>
        - Column[z139_adaptationrow]  <container>
          - Row[z140_row]  <container>
            - Column[z141_column]  <container>
              - Text[Injury — ${inj.bodyPart}]  <leaf>
              - Text[it]  <leaf>
            - Button[−1 wk]  <leaf>
            - Button[+1 wk]  <leaf>
            - Button[End]  <leaf>
          - Divider[z147_divider]  <leaf>
        - Column[z148_adaptationrow]  <container>
          - Row[z149_row]  <container>
            - Column[z150_column]  <container>
              - Text[directiveTitle(d)]  <leaf>
              - Text[it]  <leaf>
            - Button[−1 wk]  <leaf>
            - Button[+1 wk]  <leaf>
            - Button[End]  <leaf>
          - Divider[z156_divider]  <leaf>
        - Spacer[z157_spacer]  <leaf>

---
## verify vs Compose source (MyProgramScreen)
- distinct leaf signatures matched: 24/24 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 158 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (my_program_screen.py)
- leaf signatures shared:        5
- generated-only (other states / not in this trace): 19
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:Completed
    GEN-only I:·DYN·
    GEN-only T:+1 wk
    GEN-only T:Active
    GEN-only T:Active adjustments
    GEN-only T:Browse programs
    GEN-only T:Close
    GEN-only T:End
    GEN-only T:Join a program to see your tra…
    GEN-only T:Manage
    GEN-only T:No details for this cycle yet.
    GEN-only T:No exercises programmed for th…
