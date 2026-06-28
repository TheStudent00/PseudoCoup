# PseudoUI generated kit screen -- today  (from Compose TodayScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (240 calls)
```python
ui.define_box("today_z00_launchedeffect", "content", "V")
ui.define_box("today_z01_launchedeffect", "content", "V")
ui.define_box("today_z02_dayexercisesdial", "content", "V")
ui.define_box("today_z03_dialog", "today_z02_dayexercisesdial", "V")
ui.define_box("today_z04_wflcard", "today_z03_dialog", "V")
ui.define_box("today_z05_roundedcornersha", "today_z04_wflcard", "V")
ui.define_box("today_z06_borderstroke", "today_z04_wflcard", "V")
ui.define_box("today_z07_card", "today_z04_wflcard", "V")
ui.define_box("today_z08_card", "today_z04_wflcard", "V")
ui.define_box("today_z09_column", "today_z04_wflcard", "V")
ui.define_text("today_z10_preview_dayname", "today_z09_column", "preview.dayName")
ui.define_divider_zone("today_z11_divider", "today_z09_column")
ui.define_text("today_z12_no_exercises_pro", "today_z09_column", "No exercises programmed for th…")
ui.define_box("today_z13_column", "today_z09_column", "V")
ui.define_box("today_z14_row", "today_z13_column", "H")
ui.define_box("today_z15_box", "today_z14_row", "V")
ui.define_box("today_z16_column", "today_z14_row", "V")
ui.define_text("today_z17_exercise_name", "today_z16_column", "exercise.name")
ui.define_text("today_z18_daysetsummary_ex", "today_z16_column", "daySetSummary(exercise, previe…")
ui.define_button("today_z19_close", "today_z09_column", "Close")
ui.define_box("today_z20_welcomebacksheet", "content", "V")
ui.define_box("today_z21_modalbottomsheet", "today_z20_welcomebacksheet", "V")
ui.define_box("today_z22_column", "today_z21_modalbottomsheet", "V")
ui.define_box("today_z23_column", "today_z22_column", "V")
ui.define_text("today_z24_welcome_back", "today_z23_column", "Welcome back")
ui.define_text("today_z25_you_ve_been_away", "today_z23_column", "You've been away for $gapLabel…")
ui.define_text("today_z26_it", "today_z23_column", "it")
ui.define_divider_zone("today_z27_divider", "today_z22_column")
ui.define_box("today_z28_questionblock", "today_z22_column", "V")
ui.define_box("today_z29_column", "today_z28_questionblock", "V")
ui.define_text("today_z30_what_brought_you", "today_z29_column", "What brought you away?")
ui.define_box("today_z31_chiprow", "today_z28_questionblock", "V")
ui.define_box("today_z32_lazyrow", "today_z31_chiprow", "H")
ui.define_box("today_z33_filterchip", "today_z32_lazyrow", "V")
ui.define_text("today_z34_label", "today_z33_filterchip", "label")
ui.define_box("today_z35_questionblock", "today_z22_column", "V")
ui.define_box("today_z36_column", "today_z35_questionblock", "V")
ui.define_text("today_z37_how_active_were_", "today_z36_column", "How active were you while away?")
ui.define_box("today_z38_chiprow", "today_z35_questionblock", "V")
ui.define_box("today_z39_lazyrow", "today_z38_chiprow", "H")
ui.define_box("today_z40_filterchip", "today_z39_lazyrow", "V")
ui.define_text("today_z41_label", "today_z40_filterchip", "label")
ui.define_box("today_z42_questionblock", "today_z22_column", "V")
ui.define_box("today_z43_column", "today_z42_questionblock", "V")
ui.define_text("today_z44_how_does_your_bo", "today_z43_column", "How does your body feel right …")
ui.define_box("today_z45_chiprow", "today_z42_questionblock", "V")
ui.define_box("today_z46_lazyrow", "today_z45_chiprow", "H")
ui.define_box("today_z47_filterchip", "today_z46_lazyrow", "V")
ui.define_text("today_z48_label", "today_z47_filterchip", "label")
ui.define_spacer_zone("today_z49_spacer", "today_z22_column")
ui.define_box("today_z50_row", "today_z22_column", "H")
ui.define_button("today_z51_i_m_fine_continu", "today_z50_row", "I'm fine, continue")
ui.define_button("today_z52_apply_restart_we", "today_z50_row", "Apply restart weights")
ui.define_spacer_zone("today_z53_spacer", "today_z22_column")
ui.define_box("today_z54_precheckinsheet", "content", "V")
ui.define_box("today_z55_modalbottomsheet", "today_z54_precheckinsheet", "V")
ui.define_box("today_z56_column", "today_z55_modalbottomsheet", "V")
ui.define_text("today_z57_before_we_start", "today_z56_column", "Before we start")
ui.define_text("today_z58_5_seconds_helps_", "today_z56_column", "5 seconds. Helps you spot patt…")
ui.define_text("today_z59_how_did_you_slee", "today_z56_column", "How did you sleep?")
ui.define_box("today_z60_checkinbuttonrow", "today_z56_column", "V")
ui.define_box("today_z61_row", "today_z60_checkinbuttonrow", "H")
ui.define_box("today_z62_surface", "today_z61_row", "V")
ui.define_box("today_z63_box", "today_z62_surface", "V")
ui.define_text("today_z64_label", "today_z63_box", "label")
ui.define_text("today_z65_energy_right_now", "today_z56_column", "Energy right now?")
ui.define_box("today_z66_checkinbuttonrow", "today_z56_column", "V")
ui.define_box("today_z67_row", "today_z66_checkinbuttonrow", "H")
ui.define_box("today_z68_surface", "today_z67_row", "V")
ui.define_box("today_z69_box", "today_z68_surface", "V")
ui.define_text("today_z70_label", "today_z69_box", "label")
ui.define_button("today_z71_let_s_go", "today_z56_column", "Let's go")
ui.define_button("today_z72_skip_check_in", "today_z56_column", "Skip check-in")
ui.define_box("today_z73_box", "content", "V")
ui.define_box("today_z74_lazycolumn", "today_z73_box", "V")
ui.define_box("today_z75_welcomebackbanne", "today_z74_lazycolumn", "V")
ui.define_box("today_z76_wflcard", "today_z75_welcomebackbanne", "V")
ui.define_box("today_z77_roundedcornersha", "today_z76_wflcard", "V")
ui.define_box("today_z78_borderstroke", "today_z76_wflcard", "V")
ui.define_box("today_z79_card", "today_z76_wflcard", "V")
ui.define_box("today_z80_card", "today_z76_wflcard", "V")
ui.define_box("today_z81_column", "today_z76_wflcard", "V")
ui.define_text("today_z82_welcome_back", "today_z81_column", "Welcome back 👋")
ui.define_text("today_z83_you_ve_been_away", "today_z81_column", "You've been away for $gapLabel…")
ui.define_box("today_z84_quietstretchcard", "today_z74_lazycolumn", "V")
ui.define_box("today_z85_wflcard", "today_z84_quietstretchcard", "V")
ui.define_box("today_z86_roundedcornersha", "today_z85_wflcard", "V")
ui.define_box("today_z87_borderstroke", "today_z85_wflcard", "V")
ui.define_box("today_z88_card", "today_z85_wflcard", "V")
ui.define_box("today_z89_card", "today_z85_wflcard", "V")
ui.define_box("today_z90_column", "today_z85_wflcard", "V")
ui.define_box("today_z91_row", "today_z90_column", "H")
ui.define_box("today_z92_column", "today_z91_row", "V")
ui.define_box("today_z93_wflcardtitle", "today_z92_column", "V")
ui.define_text("today_z94_it_s_been_gaplab", "today_z93_wflcardtitle", "It's been $gapLabel")
ui.define_spacer_zone("today_z95_spacer", "today_z92_column")
ui.define_text("today_z96_no_pressure_life", "today_z92_column", "No pressure — life happens. Wa…")
ui.define_icon("today_z97_dismiss", "today_z91_row", "Dismiss")
ui.define_spacer_zone("today_z98_spacer", "today_z90_column")
ui.define_box("today_z99_row", "today_z90_column", "H")
ui.define_button("today_z100_that_was_rest", "today_z99_row", "That was rest")
ui.define_button("today_z101_not_now", "today_z99_row", "Not now")
ui.define_box("today_z102_deloadnudgecard", "today_z74_lazycolumn", "V")
ui.define_box("today_z103_scienceinfodialo", "today_z102_deloadnudgecard", "V")
ui.define_box("today_z104_alertdialog", "today_z103_scienceinfodialo", "V")
ui.define_button("today_z105_got_it", "today_z104_alertdialog", "Got it")
ui.define_text("today_z106_why_a_deload", "today_z104_alertdialog", "Why a deload?")
ui.define_box("today_z107_column", "today_z104_alertdialog", "V")
ui.define_text("today_z108_autoregulationsc", "today_z107_column", "AutoregulationScience.DELOAD_I…")
ui.define_box("today_z109_column", "today_z107_column", "V")
ui.define_text("today_z110_note_heading", "today_z109_column", "note.heading")
ui.define_text("today_z111_note_body", "today_z109_column", "note.body")
ui.define_box("today_z112_wflcard", "today_z102_deloadnudgecard", "V")
ui.define_box("today_z113_roundedcornersha", "today_z112_wflcard", "V")
ui.define_box("today_z114_borderstroke", "today_z112_wflcard", "V")
ui.define_box("today_z115_card", "today_z112_wflcard", "V")
ui.define_box("today_z116_card", "today_z112_wflcard", "V")
ui.define_box("today_z117_column", "today_z112_wflcard", "V")
ui.define_box("today_z118_row", "today_z117_column", "H")
ui.define_box("today_z119_column", "today_z118_row", "V")
ui.define_box("today_z120_wflcardtitle", "today_z119_column", "V")
ui.define_text("today_z121_title", "today_z120_wflcardtitle", "title")
ui.define_spacer_zone("today_z122_spacer", "today_z119_column")
ui.define_text("today_z123_body", "today_z119_column", "body")
ui.define_box("today_z124_sciencehelpbutto", "today_z118_row", "V")
ui.define_icon("today_z125_here_s_the_scien", "today_z124_sciencehelpbutto", "Here's the science")
ui.define_icon("today_z126_dismiss", "today_z118_row", "Dismiss")
ui.define_spacer_zone("today_z127_spacer", "today_z117_column")
ui.define_box("today_z128_row", "today_z117_column", "H")
ui.define_button("today_z129_start_deload", "today_z128_row", "Start deload")
ui.define_button("today_z130_not_now", "today_z128_row", "Not now")
ui.define_box("today_z131_graduationnudgec", "today_z74_lazycolumn", "V")
ui.define_box("today_z132_scienceinfodialo", "today_z131_graduationnudgec", "V")
ui.define_box("today_z133_alertdialog", "today_z132_scienceinfodialo", "V")
ui.define_button("today_z134_got_it", "today_z133_alertdialog", "Got it")
ui.define_text("today_z135_linear_vs_double", "today_z133_alertdialog", "Linear vs double progression")
ui.define_box("today_z136_column", "today_z133_alertdialog", "V")
ui.define_text("today_z137_autoregulationsc", "today_z136_column", "AutoregulationScience.PROGRESS…")
ui.define_box("today_z138_column", "today_z136_column", "V")
ui.define_text("today_z139_note_heading", "today_z138_column", "note.heading")
ui.define_text("today_z140_note_body", "today_z138_column", "note.body")
ui.define_box("today_z141_wflcard", "today_z131_graduationnudgec", "V")
ui.define_box("today_z142_roundedcornersha", "today_z141_wflcard", "V")
ui.define_box("today_z143_borderstroke", "today_z141_wflcard", "V")
ui.define_box("today_z144_card", "today_z141_wflcard", "V")
ui.define_box("today_z145_card", "today_z141_wflcard", "V")
ui.define_box("today_z146_column", "today_z141_wflcard", "V")
ui.define_box("today_z147_row", "today_z146_column", "H")
ui.define_box("today_z148_column", "today_z147_row", "V")
ui.define_box("today_z149_wflcardtitle", "today_z148_column", "V")
ui.define_text("today_z150_you_ve_outgrown_", "today_z149_wflcardtitle", "You've outgrown linear progres…")
ui.define_spacer_zone("today_z151_spacer", "today_z148_column")
ui.define_text("today_z152_adding_weight_ev", "today_z148_column", "Adding weight every session ha…")
ui.define_box("today_z153_sciencehelpbutto", "today_z147_row", "V")
ui.define_icon("today_z154_here_s_the_scien", "today_z153_sciencehelpbutto", "Here's the science")
ui.define_icon("today_z155_dismiss", "today_z147_row", "Dismiss")
ui.define_spacer_zone("today_z156_spacer", "today_z146_column")
ui.define_box("today_z157_row", "today_z146_column", "H")
ui.define_button("today_z158_switch_to_double", "today_z157_row", "Switch to double progression")
ui.define_button("today_z159_not_yet", "today_z157_row", "Not yet")
ui.define_box("today_z160_weeklyworkoutsca", "today_z74_lazycolumn", "V")
ui.define_box("today_z161_wflcard", "today_z160_weeklyworkoutsca", "V")
ui.define_box("today_z162_roundedcornersha", "today_z161_wflcard", "V")
ui.define_box("today_z163_borderstroke", "today_z161_wflcard", "V")
ui.define_box("today_z164_card", "today_z161_wflcard", "V")
ui.define_box("today_z165_card", "today_z161_wflcard", "V")
ui.define_box("today_z166_row", "today_z161_wflcard", "H")
ui.define_box("today_z167_wflcardtitle", "today_z166_row", "V")
ui.define_text("today_z168_this_week_s_work", "today_z167_wflcardtitle", "This week's workouts")
ui.define_text("today_z169_donecount_of_tot", "today_z166_row", "$doneCount of $totalCount done")
ui.define_text("today_z170_set_up_a_program", "today_z161_wflcard", "Set up a program to see your w…")
ui.define_divider_zone("today_z171_divider", "today_z161_wflcard")
ui.define_box("today_z172_workoutdayrow", "today_z161_wflcard", "V")
ui.define_box("today_z173_row", "today_z172_workoutdayrow", "H")
ui.define_box("today_z174_daystatusdot", "today_z173_row", "V")
ui.define_box("today_z175_surface", "today_z174_daystatusdot", "V")
ui.define_box("today_z176_box", "today_z175_surface", "V")
ui.define_icon("today_z177_icon", "today_z176_box", "")
ui.define_box("today_z178_box", "today_z174_daystatusdot", "V")
ui.define_box("today_z179_surface", "today_z178_box", "V")
ui.define_box("today_z180_box", "today_z178_box", "V")
ui.define_box("today_z181_surface", "today_z174_daystatusdot", "V")
ui.define_box("today_z182_column", "today_z173_row", "V")
ui.define_box("today_z183_row", "today_z182_column", "H")
ui.define_text("today_z184_item_day_name", "today_z183_row", "item.day.name")
ui.define_text("today_z185_item_daylabel", "today_z183_row", "item.dayLabel")
ui.define_text("today_z186_subtitle", "today_z182_column", "subtitle")
ui.define_box("today_z187_surface", "today_z173_row", "V")
ui.define_text("today_z188_up_next", "today_z187_surface", "Up next")
ui.define_box("today_z189_restdayrow", "today_z161_wflcard", "V")
ui.define_box("today_z190_row", "today_z189_restdayrow", "H")
ui.define_box("today_z191_restdaydot", "today_z190_row", "V")
ui.define_box("today_z192_canvas", "today_z191_restdaydot", "V")
ui.define_box("today_z193_stroke", "today_z192_canvas", "V")
ui.define_text("today_z194_rest_day_taken_r", "today_z190_row", "Rest day · taken|Rest day")
ui.define_spacer_zone("today_z195_spacer", "today_z190_row")
ui.define_text("today_z196_row_daylabel", "today_z190_row", "row.dayLabel")
ui.define_button("today_z197_resume_state_act", "today_z74_lazycolumn", "Resume ${state.activeSessionNa…")
ui.define_box("today_z198_pathencouragemen", "today_z74_lazycolumn", "V")
ui.define_box("today_z199_wflcard", "today_z198_pathencouragemen", "V")
ui.define_box("today_z200_roundedcornersha", "today_z199_wflcard", "V")
ui.define_box("today_z201_borderstroke", "today_z199_wflcard", "V")
ui.define_box("today_z202_card", "today_z199_wflcard", "V")
ui.define_box("today_z203_card", "today_z199_wflcard", "V")
ui.define_box("today_z204_column", "today_z199_wflcard", "V")
ui.define_box("today_z205_row", "today_z204_column", "H")
ui.define_box("today_z206_box", "today_z205_row", "V")
ui.define_box("today_z207_wflcardtitle", "today_z205_row", "V")
ui.define_text("today_z208_activepath_name", "today_z207_wflcardtitle", "activePath.name")
ui.define_text("today_z209_keep_showing_up_", "today_z204_column", "Keep showing up. That's what i…")
ui.define_spacer_zone("today_z210_spacer", "today_z204_column")
ui.define_text("today_z211_donecount_of_fre", "today_z204_column", "$doneCount of $frequencyPerWee…")
ui.define_spacer_zone("today_z212_spacer", "today_z204_column")
ui.define_box("today_z213_sessionprogressb", "today_z204_column", "V")
ui.define_box("today_z214_box", "today_z213_sessionprogressb", "V")
ui.define_box("today_z215_box", "today_z214_box", "V")
ui.define_text("today_z216_no_program_enrol", "today_z74_lazycolumn", "No program enrolled yet. Head …")
ui.define_box("today_z217_todayactionmenu", "today_z73_box", "V")
ui.define_box("today_z218_box", "today_z217_todayactionmenu", "V")
ui.define_box("today_z219_box", "today_z218_box", "V")
ui.define_box("today_z220_column", "today_z218_box", "V")
ui.define_button("today_z221_new_mobility_ses", "today_z220_column", "New mobility session")
ui.define_button("today_z222_log_a_win", "today_z220_column", "Log a Win")
ui.define_button("today_z223_log_other_exerci", "today_z220_column", "Log other exercise")
ui.define_icon("today_z224_close_actions_op", "today_z220_column", "Close actions|Open actions")
ui.define_box("today_z225_logwinsheet", "content", "V")
ui.define_box("today_z226_modalbottomsheet", "today_z225_logwinsheet", "V")
ui.define_box("today_z227_column", "today_z226_modalbottomsheet", "V")
ui.define_text("today_z228_log_a_win", "today_z227_column", "Log a win")
ui.define_text("today_z229_something_happen", "today_z227_column", "Something happened in real lif…")
ui.define_text("today_z230_which_path", "today_z227_column", "Which path?")
ui.define_box("today_z231_flowrow", "today_z227_column", "H")
ui.define_box("today_z232_filterchip", "today_z231_flowrow", "V")
ui.define_text("today_z233_path_name", "today_z232_filterchip", "path.name")
ui.define_text("today_z234_tag", "today_z227_column", "Tag")
ui.define_box("today_z235_flowrow", "today_z227_column", "H")
ui.define_box("today_z236_filterchip", "today_z235_flowrow", "V")
ui.define_text("today_z237_tag_label", "today_z236_filterchip", "tag.label")
ui.define_input_zone("today_z238_e_g_carried_all_", "today_z227_column", "", "e.g. carried all the groceries…")
ui.define_button("today_z239_save_win", "today_z227_column", "Save win")
```

## generated tree
  - Column[launchedeffect]  <leaf>
  - Column[launchedeffect]  <leaf>
  - Column[dayexercisesdial]  <container>
    - Column[dialog]  <container>
      - Column[wflcard]  <container>
        - Column[roundedcornersha]  <leaf>
        - Column[borderstroke]  <leaf>
        - Column[card]  <leaf>
        - Column[card]  <leaf>
        - Column[column]  <container>
          - Text[preview.dayName]  <leaf>
          - Divider[divider]  <leaf>
          - Text[No exercises programmed for th…]  <leaf>
          - Column[column]  <container>
            - Row[row]  <container>
              - Column[box]  <leaf>
              - Column[column]  <container>
                - Text[exercise.name]  <leaf>
                - Text[daySetSummary(exercise, previe…]  <leaf>
          - Button[Close]  <leaf>
  - Column[welcomebacksheet]  <container>
    - Column[modalbottomsheet]  <container>
      - Column[column]  <container>
        - Column[column]  <container>
          - Text[Welcome back]  <leaf>
          - Text[You've been away for $gapLabel…]  <leaf>
          - Text[it]  <leaf>
        - Divider[divider]  <leaf>
        - Column[questionblock]  <container>
          - Column[column]  <container>
            - Text[What brought you away?]  <leaf>
          - Column[chiprow]  <container>
            - Row[lazyrow]  <container>
              - Column[filterchip]  <container>
                - Text[label]  <leaf>
        - Column[questionblock]  <container>
          - Column[column]  <container>
            - Text[How active were you while away?]  <leaf>
          - Column[chiprow]  <container>
            - Row[lazyrow]  <container>
              - Column[filterchip]  <container>
                - Text[label]  <leaf>
        - Column[questionblock]  <container>
          - Column[column]  <container>
            - Text[How does your body feel right …]  <leaf>
          - Column[chiprow]  <container>
            - Row[lazyrow]  <container>
              - Column[filterchip]  <container>
                - Text[label]  <leaf>
        - Spacer[spacer]  <leaf>
        - Row[row]  <container>
          - Button[I'm fine, continue]  <leaf>
          - Button[Apply restart weights]  <leaf>
        - Spacer[spacer]  <leaf>
  - Column[precheckinsheet]  <container>
    - Column[modalbottomsheet]  <container>
      - Column[column]  <container>
        - Text[Before we start]  <leaf>
        - Text[5 seconds. Helps you spot patt…]  <leaf>
        - Text[How did you sleep?]  <leaf>
        - Column[checkinbuttonrow]  <container>
          - Row[row]  <container>
            - Column[surface]  <container>
              - Column[box]  <container>
                - Text[label]  <leaf>
        - Text[Energy right now?]  <leaf>
        - Column[checkinbuttonrow]  <container>
          - Row[row]  <container>
            - Column[surface]  <container>
              - Column[box]  <container>
                - Text[label]  <leaf>
        - Button[Let's go]  <leaf>
        - Button[Skip check-in]  <leaf>
  - Column[box]  <container>
    - Column[lazycolumn]  <container>
      - Column[welcomebackbanne]  <container>
        - Column[wflcard]  <container>
          - Column[roundedcornersha]  <leaf>
          - Column[borderstroke]  <leaf>
          - Column[card]  <leaf>
          - Column[card]  <leaf>
          - Column[column]  <container>
            - Text[Welcome back 👋]  <leaf>
            - Text[You've been away for $gapLabel…]  <leaf>
      - Column[quietstretchcard]  <container>
        - Column[wflcard]  <container>
          - Column[roundedcornersha]  <leaf>
          - Column[borderstroke]  <leaf>
          - Column[card]  <leaf>
          - Column[card]  <leaf>
          - Column[column]  <container>
            - Row[row]  <container>
              - Column[column]  <container>
                - Column[wflcardtitle]  <container>
                  - Text[It's been $gapLabel]  <leaf>
                - Spacer[spacer]  <leaf>
                - Text[No pressure — life happens. Wa…]  <leaf>
              - Icon[Dismiss]  <leaf>
            - Spacer[spacer]  <leaf>
            - Row[row]  <container>
              - Button[That was rest]  <leaf>
              - Button[Not now]  <leaf>
      - Column[deloadnudgecard]  <container>
        - Column[scienceinfodialo]  <container>
          - Column[alertdialog]  <container>
            - Button[Got it]  <leaf>
            - Text[Why a deload?]  <leaf>
            - Column[column]  <container>
              - Text[AutoregulationScience.DELOAD_I…]  <leaf>
              - Column[column]  <container>
                - Text[note.heading]  <leaf>
                - Text[note.body]  <leaf>
        - Column[wflcard]  <container>
          - Column[roundedcornersha]  <leaf>
          - Column[borderstroke]  <leaf>
          - Column[card]  <leaf>
          - Column[card]  <leaf>
          - Column[column]  <container>
            - Row[row]  <container>
              - Column[column]  <container>
                - Column[wflcardtitle]  <container>
                  - Text[title]  <leaf>
                - Spacer[spacer]  <leaf>
                - Text[body]  <leaf>
              - Column[sciencehelpbutto]  <container>
                - Icon[Here's the science]  <leaf>
              - Icon[Dismiss]  <leaf>
            - Spacer[spacer]  <leaf>
            - Row[row]  <container>
              - Button[Start deload]  <leaf>
              - Button[Not now]  <leaf>
      - Column[graduationnudgec]  <container>
        - Column[scienceinfodialo]  <container>
          - Column[alertdialog]  <container>
            - Button[Got it]  <leaf>
            - Text[Linear vs double progression]  <leaf>
            - Column[column]  <container>
              - Text[AutoregulationScience.PROGRESS…]  <leaf>
              - Column[column]  <container>
                - Text[note.heading]  <leaf>
                - Text[note.body]  <leaf>
        - Column[wflcard]  <container>
          - Column[roundedcornersha]  <leaf>
          - Column[borderstroke]  <leaf>
          - Column[card]  <leaf>
          - Column[card]  <leaf>
          - Column[column]  <container>
            - Row[row]  <container>
              - Column[column]  <container>
                - Column[wflcardtitle]  <container>
                  - Text[You've outgrown linear progres…]  <leaf>
                - Spacer[spacer]  <leaf>
                - Text[Adding weight every session ha…]  <leaf>
              - Column[sciencehelpbutto]  <container>
                - Icon[Here's the science]  <leaf>
              - Icon[Dismiss]  <leaf>
            - Spacer[spacer]  <leaf>
            - Row[row]  <container>
              - Button[Switch to double progression]  <leaf>
              - Button[Not yet]  <leaf>
      - Column[weeklyworkoutsca]  <container>
        - Column[wflcard]  <container>
          - Column[roundedcornersha]  <leaf>
          - Column[borderstroke]  <leaf>
          - Column[card]  <leaf>
          - Column[card]  <leaf>
          - Row[row]  <container>
            - Column[wflcardtitle]  <container>
              - Text[This week's workouts]  <leaf>
            - Text[$doneCount of $totalCount done]  <leaf>
          - Text[Set up a program to see your w…]  <leaf>
          - Divider[divider]  <leaf>
          - Column[workoutdayrow]  <container>
            - Row[row]  <container>
              - Column[daystatusdot]  <container>
                - Column[surface]  <container>
                  - Column[box]  <container>
                    - Icon[icon]  <leaf>
                - Column[box]  <container>
                  - Column[surface]  <leaf>
                  - Column[box]  <leaf>
                - Column[surface]  <leaf>
              - Column[column]  <container>
                - Row[row]  <container>
                  - Text[item.day.name]  <leaf>
                  - Text[item.dayLabel]  <leaf>
                - Text[subtitle]  <leaf>
              - Column[surface]  <container>
                - Text[Up next]  <leaf>
          - Column[restdayrow]  <container>
            - Row[row]  <container>
              - Column[restdaydot]  <container>
                - Column[canvas]  <container>
                  - Column[stroke]  <leaf>
              - Text[Rest day · taken|Rest day]  <leaf>
              - Spacer[spacer]  <leaf>
              - Text[row.dayLabel]  <leaf>
      - Button[Resume ${state.activeSessionNa…]  <leaf>
      - Column[pathencouragemen]  <container>
        - Column[wflcard]  <container>
          - Column[roundedcornersha]  <leaf>
          - Column[borderstroke]  <leaf>
          - Column[card]  <leaf>
          - Column[card]  <leaf>
          - Column[column]  <container>
            - Row[row]  <container>
              - Column[box]  <leaf>
              - Column[wflcardtitle]  <container>
                - Text[activePath.name]  <leaf>
            - Text[Keep showing up. That's what i…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[$doneCount of $frequencyPerWee…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[sessionprogressb]  <container>
              - Column[box]  <container>
                - Column[box]  <leaf>
      - Text[No program enrolled yet. Head …]  <leaf>
    - Column[todayactionmenu]  <container>
      - Column[box]  <container>
        - Column[box]  <leaf>
        - Column[column]  <container>
          - Button[New mobility session]  <leaf>
          - Button[Log a Win]  <leaf>
          - Button[Log other exercise]  <leaf>
          - Icon[Close actions|Open actions]  <leaf>
  - Column[logwinsheet]  <container>
    - Column[modalbottomsheet]  <container>
      - Column[column]  <container>
        - Text[Log a win]  <leaf>
        - Text[Something happened in real lif…]  <leaf>
        - Text[Which path?]  <leaf>
        - Row[flowrow]  <container>
          - Column[filterchip]  <container>
            - Text[path.name]  <leaf>
        - Text[Tag]  <leaf>
        - Row[flowrow]  <container>
          - Column[filterchip]  <container>
            - Text[tag.label]  <leaf>
        - TextField[e.g. carried all the groceries…]  <leaf>
        - Button[Save win]  <leaf>

---
## verify vs Compose source (TodayScreen)
- distinct leaf signatures matched: 41/41 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 240 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (today_screen.py)
- leaf signatures shared:        3
- generated-only (other states / not in this trace): 38
- hand-built-only (helper glyphs / human representation): 0
    GEN-only F:e.g. carried all the groceries…
    GEN-only I:Dismiss
    GEN-only I:Here's the science
    GEN-only I:·DYN·
    GEN-only T:5 seconds. Helps you spot patt…
    GEN-only T:Apply restart weights
    GEN-only T:Before we start
    GEN-only T:Close
    GEN-only T:Energy right now?
    GEN-only T:Got it
    GEN-only T:How active were you while away?
    GEN-only T:How did you sleep?
