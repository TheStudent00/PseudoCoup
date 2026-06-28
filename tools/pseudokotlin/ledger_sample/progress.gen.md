# PseudoUI generated kit screen -- progress  (from Compose ProgressScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (214 calls)
```python
ui.define_box("progress_z00_column", "content", "V")
ui.define_box("progress_z01_tabrow", "progress_z00_column", "V")
ui.define_box("progress_z02_tab", "progress_z01_tabrow", "V")
ui.define_text("progress_z03_tab_label", "progress_z02_tab", "tab.label")
ui.define_box("progress_z04_box", "progress_z00_column", "V")
ui.define_box("progress_z05_circularprogress", "progress_z04_box", "V")
ui.define_box("progress_z06_analyticscontent", "progress_z00_column", "V")
ui.define_box("progress_z07_lazycolumn", "progress_z06_analyticscontent", "V")
ui.define_box("progress_z08_checkininsightca", "progress_z07_lazycolumn", "V")
ui.define_box("progress_z09_wflcard", "progress_z08_checkininsightca", "V")
ui.define_box("progress_z10_roundedcornersha", "progress_z09_wflcard", "V")
ui.define_box("progress_z11_borderstroke", "progress_z09_wflcard", "V")
ui.define_box("progress_z12_card", "progress_z09_wflcard", "V")
ui.define_box("progress_z13_card", "progress_z09_wflcard", "V")
ui.define_box("progress_z14_column", "progress_z09_wflcard", "V")
ui.define_box("progress_z15_wflcardtitle", "progress_z14_column", "V")
ui.define_text("progress_z16_how_you_feel_aft", "progress_z15_wflcardtitle", "How you feel after training")
ui.define_text("progress_z17_on_stat_totalses", "progress_z14_column", "On ${stat.totalSessions} train…")
ui.define_box("progress_z18_winshomecard", "progress_z07_lazycolumn", "V")
ui.define_box("progress_z19_wflcard", "progress_z18_winshomecard", "V")
ui.define_box("progress_z20_roundedcornersha", "progress_z19_wflcard", "V")
ui.define_box("progress_z21_borderstroke", "progress_z19_wflcard", "V")
ui.define_box("progress_z22_card", "progress_z19_wflcard", "V")
ui.define_box("progress_z23_card", "progress_z19_wflcard", "V")
ui.define_box("progress_z24_column", "progress_z19_wflcard", "V")
ui.define_box("progress_z25_wflcardtitle", "progress_z24_column", "V")
ui.define_text("progress_z26_your_wins", "progress_z25_wflcardtitle", "Your wins")
ui.define_spacer_zone("progress_z27_spacer", "progress_z24_column")
ui.define_box("progress_z28_row", "progress_z24_column", "H")
ui.define_box("progress_z29_winsdonut", "progress_z28_row", "V")
ui.define_box("progress_z30_box", "progress_z29_winsdonut", "V")
ui.define_box("progress_z31_canvas", "progress_z30_box", "V")
ui.define_box("progress_z32_offset", "progress_z31_canvas", "V")
ui.define_box("progress_z33_size", "progress_z31_canvas", "V")
ui.define_box("progress_z34_stroke", "progress_z31_canvas", "V")
ui.define_box("progress_z35_column", "progress_z30_box", "V")
ui.define_text("progress_z36_total_tostring", "progress_z35_column", "total.toString()")
ui.define_text("progress_z37_win_wins", "progress_z35_column", "win|wins")
ui.define_box("progress_z38_column", "progress_z28_row", "V")
ui.define_text("progress_z39_more_than_the_nu", "progress_z38_column", "More than the numbers — the re…")
ui.define_button("progress_z40_log_a_win", "progress_z38_column", "Log a win")
ui.define_box("progress_z41_logwinsheet", "progress_z18_winshomecard", "V")
ui.define_box("progress_z42_modalbottomsheet", "progress_z41_logwinsheet", "V")
ui.define_box("progress_z43_column", "progress_z42_modalbottomsheet", "V")
ui.define_text("progress_z44_log_a_win", "progress_z43_column", "Log a win")
ui.define_text("progress_z45_something_happen", "progress_z43_column", "Something happened in real lif…")
ui.define_text("progress_z46_which_path", "progress_z43_column", "Which path?")
ui.define_box("progress_z47_flowrow", "progress_z43_column", "H")
ui.define_box("progress_z48_filterchip", "progress_z47_flowrow", "V")
ui.define_text("progress_z49_path_name", "progress_z48_filterchip", "path.name")
ui.define_text("progress_z50_tag", "progress_z43_column", "Tag")
ui.define_box("progress_z51_flowrow", "progress_z43_column", "H")
ui.define_box("progress_z52_filterchip", "progress_z51_flowrow", "V")
ui.define_text("progress_z53_tag_label", "progress_z52_filterchip", "tag.label")
ui.define_input_zone("progress_z54_e_g_carried_all_", "progress_z43_column", "", "e.g. carried all the groceries…")
ui.define_button("progress_z55_save_win", "progress_z43_column", "Save win")
ui.define_box("progress_z56_strengthcard", "progress_z07_lazycolumn", "V")
ui.define_box("progress_z57_wflcard", "progress_z56_strengthcard", "V")
ui.define_box("progress_z58_roundedcornersha", "progress_z57_wflcard", "V")
ui.define_box("progress_z59_borderstroke", "progress_z57_wflcard", "V")
ui.define_box("progress_z60_card", "progress_z57_wflcard", "V")
ui.define_box("progress_z61_card", "progress_z57_wflcard", "V")
ui.define_box("progress_z62_column", "progress_z57_wflcard", "V")
ui.define_box("progress_z63_wflcardtitle", "progress_z62_column", "V")
ui.define_text("progress_z64_strength_score", "progress_z63_wflcardtitle", "Strength score")
ui.define_box("progress_z65_column", "progress_z62_column", "V")
ui.define_text("progress_z66_formatvolume_sco", "progress_z65_column", "formatVolume(score.totalE1rmKg…")
ui.define_text("progress_z67_foundational_tot", "progress_z65_column", "Foundational total · best e1RM…")
ui.define_text("progress_z68_trend", "progress_z62_column", "trend")
ui.define_box("progress_z69_strengthlinechar", "progress_z62_column", "V")
ui.define_box("progress_z70_canvas", "progress_z69_strengthlinechar", "V")
ui.define_box("progress_z71_offset", "progress_z70_canvas", "V")
ui.define_box("progress_z72_offset", "progress_z70_canvas", "V")
ui.define_box("progress_z73_path", "progress_z70_canvas", "V")
ui.define_box("progress_z74_path", "progress_z70_canvas", "V")
ui.define_box("progress_z75_stroke", "progress_z70_canvas", "V")
ui.define_box("progress_z76_offset", "progress_z70_canvas", "V")
ui.define_text("progress_z77_keep_setting_prs", "progress_z62_column", "Keep setting PRs on your main …")
ui.define_box("progress_z78_tonnagecard", "progress_z07_lazycolumn", "V")
ui.define_box("progress_z79_wflcard", "progress_z78_tonnagecard", "V")
ui.define_box("progress_z80_roundedcornersha", "progress_z79_wflcard", "V")
ui.define_box("progress_z81_borderstroke", "progress_z79_wflcard", "V")
ui.define_box("progress_z82_card", "progress_z79_wflcard", "V")
ui.define_box("progress_z83_card", "progress_z79_wflcard", "V")
ui.define_box("progress_z84_column", "progress_z79_wflcard", "V")
ui.define_box("progress_z85_wflcardtitle", "progress_z84_column", "V")
ui.define_text("progress_z86_tonnage", "progress_z85_wflcardtitle", "Tonnage")
ui.define_box("progress_z87_row", "progress_z84_column", "H")
ui.define_box("progress_z88_metricstat", "progress_z87_row", "V")
ui.define_box("progress_z89_column", "progress_z88_metricstat", "V")
ui.define_text("progress_z90_last_7_days", "progress_z89_column", "Last 7 days")
ui.define_text("progress_z91_formatvolume_ton", "progress_z89_column", "formatVolume(tonnage7dKg, unit)")
ui.define_box("progress_z92_metricstat", "progress_z87_row", "V")
ui.define_box("progress_z93_column", "progress_z92_metricstat", "V")
ui.define_text("progress_z94_last_30_days", "progress_z93_column", "Last 30 days")
ui.define_text("progress_z95_formatvolume_ton", "progress_z93_column", "formatVolume(tonnage30dKg, uni…")
ui.define_box("progress_z96_activeminutescar", "progress_z07_lazycolumn", "V")
ui.define_box("progress_z97_wflcard", "progress_z96_activeminutescar", "V")
ui.define_box("progress_z98_roundedcornersha", "progress_z97_wflcard", "V")
ui.define_box("progress_z99_borderstroke", "progress_z97_wflcard", "V")
ui.define_box("progress_z100_card", "progress_z97_wflcard", "V")
ui.define_box("progress_z101_card", "progress_z97_wflcard", "V")
ui.define_box("progress_z102_column", "progress_z97_wflcard", "V")
ui.define_box("progress_z103_wflcardtitle", "progress_z102_column", "V")
ui.define_text("progress_z104_time_training", "progress_z103_wflcardtitle", "Time training")
ui.define_box("progress_z105_row", "progress_z102_column", "H")
ui.define_box("progress_z106_metricstat", "progress_z105_row", "V")
ui.define_box("progress_z107_column", "progress_z106_metricstat", "V")
ui.define_text("progress_z108_last_7_days", "progress_z107_column", "Last 7 days")
ui.define_text("progress_z109_formatminutes_mi", "progress_z107_column", "formatMinutes(minutes7d)")
ui.define_box("progress_z110_metricstat", "progress_z105_row", "V")
ui.define_box("progress_z111_column", "progress_z110_metricstat", "V")
ui.define_text("progress_z112_last_30_days", "progress_z111_column", "Last 30 days")
ui.define_text("progress_z113_formatminutes_mi", "progress_z111_column", "formatMinutes(minutes30d)")
ui.define_text("progress_z114_lifting_and_card", "progress_z102_column", "Lifting and cardio combined.")
ui.define_box("progress_z115_musclevolumecard", "progress_z07_lazycolumn", "V")
ui.define_box("progress_z116_wflcard", "progress_z115_musclevolumecard", "V")
ui.define_box("progress_z117_roundedcornersha", "progress_z116_wflcard", "V")
ui.define_box("progress_z118_borderstroke", "progress_z116_wflcard", "V")
ui.define_box("progress_z119_card", "progress_z116_wflcard", "V")
ui.define_box("progress_z120_card", "progress_z116_wflcard", "V")
ui.define_box("progress_z121_column", "progress_z116_wflcard", "V")
ui.define_box("progress_z122_row", "progress_z121_column", "H")
ui.define_box("progress_z123_wflcardtitle", "progress_z122_row", "V")
ui.define_text("progress_z124_volume_by_muscle", "progress_z123_wflcardtitle", "Volume by muscle")
ui.define_box("progress_z125_row", "progress_z122_row", "H")
ui.define_box("progress_z126_filterchip", "progress_z125_row", "V")
ui.define_text("progress_z127_option_label", "progress_z126_filterchip", "option.label")
ui.define_text("progress_z128_no_volume_logged", "progress_z121_column", "No volume logged in the last $…")
ui.define_spacer_zone("progress_z129_spacer", "progress_z121_column")
ui.define_divider_zone("progress_z130_divider", "progress_z121_column")
ui.define_box("progress_z131_musclevolumerowi", "progress_z121_column", "V")
ui.define_box("progress_z132_column", "progress_z131_musclevolumerowi", "V")
ui.define_box("progress_z133_row", "progress_z132_column", "H")
ui.define_text("progress_z134_row_musclegroup_", "progress_z133_row", "row.muscleGroup.displayName()")
ui.define_text("progress_z135_formatvolume_row", "progress_z133_row", "formatVolume(row.tonnageKg, un…")
ui.define_spacer_zone("progress_z136_spacer", "progress_z132_column")
ui.define_box("progress_z137_linearprogressin", "progress_z132_column", "V")
ui.define_text("progress_z138_log_your_first_w", "progress_z07_lazycolumn", "Log your first workout to see …")
ui.define_box("progress_z139_box", "progress_z00_column", "V")
ui.define_box("progress_z140_circularprogress", "progress_z139_box", "V")
ui.define_box("progress_z141_bestscontent", "progress_z00_column", "V")
ui.define_box("progress_z142_box", "progress_z141_bestscontent", "V")
ui.define_box("progress_z143_column", "progress_z142_box", "V")
ui.define_text("progress_z144_no_bests_yet", "progress_z143_column", "No bests yet")
ui.define_text("progress_z145_log_a_few_sets_t", "progress_z143_column", "Log a few sets to start tracki…")
ui.define_box("progress_z146_lazycolumn", "progress_z141_bestscontent", "V")
ui.define_box("progress_z147_bestsheaderrow", "progress_z146_lazycolumn", "V")
ui.define_box("progress_z148_row", "progress_z147_bestsheaderrow", "H")
ui.define_text("progress_z149_exercise", "progress_z148_row", "Exercise")
ui.define_text("progress_z150_best", "progress_z148_row", "Best")
ui.define_text("progress_z151_e1rm", "progress_z148_row", "e1RM")
ui.define_divider_zone("progress_z152_divider", "progress_z146_lazycolumn")
ui.define_box("progress_z153_bestsrowitem", "progress_z146_lazycolumn", "V")
ui.define_box("progress_z154_row", "progress_z153_bestsrowitem", "H")
ui.define_text("progress_z155_row_exercisename", "progress_z154_row", "row.exerciseName")
ui.define_text("progress_z156_formatweight_row", "progress_z154_row", "formatWeight(row.bestWeightKg,…")
ui.define_text("progress_z157_x", "progress_z154_row", "—")
ui.define_divider_zone("progress_z158_divider", "progress_z146_lazycolumn")
ui.define_box("progress_z159_historyscreen", "progress_z00_column", "V")
ui.define_box("progress_z160_box", "progress_z159_historyscreen", "V")
ui.define_box("progress_z161_circularprogress", "progress_z160_box", "V")
ui.define_box("progress_z162_box", "progress_z159_historyscreen", "V")
ui.define_box("progress_z163_column", "progress_z162_box", "V")
ui.define_text("progress_z164_no_workouts_yet", "progress_z163_column", "No workouts yet")
ui.define_text("progress_z165_completed_sessio", "progress_z163_column", "Completed sessions and cardio …")
ui.define_box("progress_z166_lazycolumn", "progress_z159_historyscreen", "V")
ui.define_box("progress_z167_weekheader", "progress_z166_lazycolumn", "V")
ui.define_box("progress_z168_surface", "progress_z167_weekheader", "V")
ui.define_box("progress_z169_row", "progress_z168_surface", "H")
ui.define_text("progress_z170_week_weeklabel", "progress_z169_row", "week.weekLabel")
ui.define_text("progress_z171_formatvolume_tot", "progress_z169_row", "formatVolume(totalVolumeKg, un…")
ui.define_box("progress_z172_sessioncard", "progress_z166_lazycolumn", "V")
ui.define_box("progress_z173_wflcard", "progress_z172_sessioncard", "V")
ui.define_box("progress_z174_roundedcornersha", "progress_z173_wflcard", "V")
ui.define_box("progress_z175_borderstroke", "progress_z173_wflcard", "V")
ui.define_box("progress_z176_card", "progress_z173_wflcard", "V")
ui.define_box("progress_z177_card", "progress_z173_wflcard", "V")
ui.define_box("progress_z178_column", "progress_z173_wflcard", "V")
ui.define_box("progress_z179_row", "progress_z178_column", "H")
ui.define_text("progress_z180_ad_hoc_workout", "progress_z179_row", "Ad-hoc Workout")
ui.define_box("progress_z181_surface", "progress_z179_row", "V")
ui.define_text("progress_z182_1_pr_session_prc", "progress_z181_surface", "1 PR|${session.prCount} PRs")
ui.define_text("progress_z183_formatsessiondat", "progress_z178_column", "formatSessionDate(session.star…")
ui.define_spacer_zone("progress_z184_spacer", "progress_z178_column")
ui.define_box("progress_z185_row", "progress_z178_column", "H")
ui.define_box("progress_z186_statlabel", "progress_z185_row", "V")
ui.define_text("progress_z187_formatduration_d", "progress_z186_statlabel", "formatDuration(dur)")
ui.define_box("progress_z188_statlabel", "progress_z185_row", "V")
ui.define_text("progress_z189_formatvolume_ses", "progress_z188_statlabel", "formatVolume(session.volumeKg,…")
ui.define_box("progress_z190_statlabel", "progress_z185_row", "V")
ui.define_text("progress_z191_session_setcount", "progress_z190_statlabel", "${session.setCount} sets")
ui.define_box("progress_z192_cardiocard", "progress_z166_lazycolumn", "V")
ui.define_box("progress_z193_wflcard", "progress_z192_cardiocard", "V")
ui.define_box("progress_z194_roundedcornersha", "progress_z193_wflcard", "V")
ui.define_box("progress_z195_borderstroke", "progress_z193_wflcard", "V")
ui.define_box("progress_z196_card", "progress_z193_wflcard", "V")
ui.define_box("progress_z197_card", "progress_z193_wflcard", "V")
ui.define_box("progress_z198_column", "progress_z193_wflcard", "V")
ui.define_box("progress_z199_row", "progress_z198_column", "H")
ui.define_text("progress_z200_cardio_type_disp", "progress_z199_row", "cardio.type.displayName()")
ui.define_text("progress_z201_cardio", "progress_z199_row", "Cardio")
ui.define_text("progress_z202_formatsessiondat", "progress_z198_column", "formatSessionDate(cardio.start…")
ui.define_spacer_zone("progress_z203_spacer", "progress_z198_column")
ui.define_box("progress_z204_row", "progress_z198_column", "H")
ui.define_box("progress_z205_statlabel", "progress_z204_row", "V")
ui.define_text("progress_z206_cardio_durationm", "progress_z205_statlabel", "${cardio.durationMinutes} min")
ui.define_box("progress_z207_statlabel", "progress_z204_row", "V")
ui.define_text("progress_z208_cardio_intensity", "progress_z207_statlabel", "cardio.intensity.summaryLabel()")
ui.define_box("progress_z209_statlabel", "progress_z204_row", "V")
ui.define_text("progress_z210_1f_km", "progress_z209_statlabel", "%.1f km")
ui.define_box("progress_z211_statlabel", "progress_z204_row", "V")
ui.define_text("progress_z212_it_bpm", "progress_z211_statlabel", "$it bpm")
ui.define_spacer_zone("progress_z213_spacer", "progress_z166_lazycolumn")
```

## generated tree
  - Column[column]  <container>
    - Column[tabrow]  <container>
      - Column[tab]  <container>
        - Text[tab.label]  <leaf>
    - Column[box]  <container>
      - Column[circularprogress]  <leaf>
    - Column[analyticscontent]  <container>
      - Column[lazycolumn]  <container>
        - Column[checkininsightca]  <container>
          - Column[wflcard]  <container>
            - Column[roundedcornersha]  <leaf>
            - Column[borderstroke]  <leaf>
            - Column[card]  <leaf>
            - Column[card]  <leaf>
            - Column[column]  <container>
              - Column[wflcardtitle]  <container>
                - Text[How you feel after training]  <leaf>
              - Text[On ${stat.totalSessions} train…]  <leaf>
        - Column[winshomecard]  <container>
          - Column[wflcard]  <container>
            - Column[roundedcornersha]  <leaf>
            - Column[borderstroke]  <leaf>
            - Column[card]  <leaf>
            - Column[card]  <leaf>
            - Column[column]  <container>
              - Column[wflcardtitle]  <container>
                - Text[Your wins]  <leaf>
              - Spacer[spacer]  <leaf>
              - Row[row]  <container>
                - Column[winsdonut]  <container>
                  - Column[box]  <container>
                    - Column[canvas]  <container>
                      - Column[offset]  <leaf>
                      - Column[size]  <leaf>
                      - Column[stroke]  <leaf>
                    - Column[column]  <container>
                      - Text[total.toString()]  <leaf>
                      - Text[win|wins]  <leaf>
                - Column[column]  <container>
                  - Text[More than the numbers — the re…]  <leaf>
                  - Button[Log a win]  <leaf>
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
        - Column[strengthcard]  <container>
          - Column[wflcard]  <container>
            - Column[roundedcornersha]  <leaf>
            - Column[borderstroke]  <leaf>
            - Column[card]  <leaf>
            - Column[card]  <leaf>
            - Column[column]  <container>
              - Column[wflcardtitle]  <container>
                - Text[Strength score]  <leaf>
              - Column[column]  <container>
                - Text[formatVolume(score.totalE1rmKg…]  <leaf>
                - Text[Foundational total · best e1RM…]  <leaf>
              - Text[trend]  <leaf>
              - Column[strengthlinechar]  <container>
                - Column[canvas]  <container>
                  - Column[offset]  <leaf>
                  - Column[offset]  <leaf>
                  - Column[path]  <leaf>
                  - Column[path]  <leaf>
                  - Column[stroke]  <leaf>
                  - Column[offset]  <leaf>
              - Text[Keep setting PRs on your main …]  <leaf>
        - Column[tonnagecard]  <container>
          - Column[wflcard]  <container>
            - Column[roundedcornersha]  <leaf>
            - Column[borderstroke]  <leaf>
            - Column[card]  <leaf>
            - Column[card]  <leaf>
            - Column[column]  <container>
              - Column[wflcardtitle]  <container>
                - Text[Tonnage]  <leaf>
              - Row[row]  <container>
                - Column[metricstat]  <container>
                  - Column[column]  <container>
                    - Text[Last 7 days]  <leaf>
                    - Text[formatVolume(tonnage7dKg, unit)]  <leaf>
                - Column[metricstat]  <container>
                  - Column[column]  <container>
                    - Text[Last 30 days]  <leaf>
                    - Text[formatVolume(tonnage30dKg, uni…]  <leaf>
        - Column[activeminutescar]  <container>
          - Column[wflcard]  <container>
            - Column[roundedcornersha]  <leaf>
            - Column[borderstroke]  <leaf>
            - Column[card]  <leaf>
            - Column[card]  <leaf>
            - Column[column]  <container>
              - Column[wflcardtitle]  <container>
                - Text[Time training]  <leaf>
              - Row[row]  <container>
                - Column[metricstat]  <container>
                  - Column[column]  <container>
                    - Text[Last 7 days]  <leaf>
                    - Text[formatMinutes(minutes7d)]  <leaf>
                - Column[metricstat]  <container>
                  - Column[column]  <container>
                    - Text[Last 30 days]  <leaf>
                    - Text[formatMinutes(minutes30d)]  <leaf>
              - Text[Lifting and cardio combined.]  <leaf>
        - Column[musclevolumecard]  <container>
          - Column[wflcard]  <container>
            - Column[roundedcornersha]  <leaf>
            - Column[borderstroke]  <leaf>
            - Column[card]  <leaf>
            - Column[card]  <leaf>
            - Column[column]  <container>
              - Row[row]  <container>
                - Column[wflcardtitle]  <container>
                  - Text[Volume by muscle]  <leaf>
                - Row[row]  <container>
                  - Column[filterchip]  <container>
                    - Text[option.label]  <leaf>
              - Text[No volume logged in the last $…]  <leaf>
              - Spacer[spacer]  <leaf>
              - Divider[divider]  <leaf>
              - Column[musclevolumerowi]  <container>
                - Column[column]  <container>
                  - Row[row]  <container>
                    - Text[row.muscleGroup.displayName()]  <leaf>
                    - Text[formatVolume(row.tonnageKg, un…]  <leaf>
                  - Spacer[spacer]  <leaf>
                  - Column[linearprogressin]  <leaf>
        - Text[Log your first workout to see …]  <leaf>
    - Column[box]  <container>
      - Column[circularprogress]  <leaf>
    - Column[bestscontent]  <container>
      - Column[box]  <container>
        - Column[column]  <container>
          - Text[No bests yet]  <leaf>
          - Text[Log a few sets to start tracki…]  <leaf>
      - Column[lazycolumn]  <container>
        - Column[bestsheaderrow]  <container>
          - Row[row]  <container>
            - Text[Exercise]  <leaf>
            - Text[Best]  <leaf>
            - Text[e1RM]  <leaf>
        - Divider[divider]  <leaf>
        - Column[bestsrowitem]  <container>
          - Row[row]  <container>
            - Text[row.exerciseName]  <leaf>
            - Text[formatWeight(row.bestWeightKg,…]  <leaf>
            - Text[—]  <leaf>
        - Divider[divider]  <leaf>
    - Column[historyscreen]  <container>
      - Column[box]  <container>
        - Column[circularprogress]  <leaf>
      - Column[box]  <container>
        - Column[column]  <container>
          - Text[No workouts yet]  <leaf>
          - Text[Completed sessions and cardio …]  <leaf>
      - Column[lazycolumn]  <container>
        - Column[weekheader]  <container>
          - Column[surface]  <container>
            - Row[row]  <container>
              - Text[week.weekLabel]  <leaf>
              - Text[formatVolume(totalVolumeKg, un…]  <leaf>
        - Column[sessioncard]  <container>
          - Column[wflcard]  <container>
            - Column[roundedcornersha]  <leaf>
            - Column[borderstroke]  <leaf>
            - Column[card]  <leaf>
            - Column[card]  <leaf>
            - Column[column]  <container>
              - Row[row]  <container>
                - Text[Ad-hoc Workout]  <leaf>
                - Column[surface]  <container>
                  - Text[1 PR|${session.prCount} PRs]  <leaf>
              - Text[formatSessionDate(session.star…]  <leaf>
              - Spacer[spacer]  <leaf>
              - Row[row]  <container>
                - Column[statlabel]  <container>
                  - Text[formatDuration(dur)]  <leaf>
                - Column[statlabel]  <container>
                  - Text[formatVolume(session.volumeKg,…]  <leaf>
                - Column[statlabel]  <container>
                  - Text[${session.setCount} sets]  <leaf>
        - Column[cardiocard]  <container>
          - Column[wflcard]  <container>
            - Column[roundedcornersha]  <leaf>
            - Column[borderstroke]  <leaf>
            - Column[card]  <leaf>
            - Column[card]  <leaf>
            - Column[column]  <container>
              - Row[row]  <container>
                - Text[cardio.type.displayName()]  <leaf>
                - Text[Cardio]  <leaf>
              - Text[formatSessionDate(cardio.start…]  <leaf>
              - Spacer[spacer]  <leaf>
              - Row[row]  <container>
                - Column[statlabel]  <container>
                  - Text[${cardio.durationMinutes} min]  <leaf>
                - Column[statlabel]  <container>
                  - Text[cardio.intensity.summaryLabel()]  <leaf>
                - Column[statlabel]  <container>
                  - Text[%.1f km]  <leaf>
                - Column[statlabel]  <container>
                  - Text[$it bpm]  <leaf>
        - Spacer[spacer]  <leaf>

---
## verify vs Compose source (ProgressScreen)
- distinct leaf signatures matched: 28/28 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 214 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (progress_screen.py)
- leaf signatures shared:        5
- generated-only (other states / not in this trace): 23
- hand-built-only (helper glyphs / human representation): 0
    GEN-only F:e.g. carried all the groceries…
    GEN-only T:Best
    GEN-only T:Cardio
    GEN-only T:Completed sessions and cardio …
    GEN-only T:Exercise
    GEN-only T:Foundational total · best e1RM…
    GEN-only T:How you feel after training
    GEN-only T:Keep setting PRs on your main …
    GEN-only T:Last 30 days
    GEN-only T:Last 7 days
    GEN-only T:Lifting and cardio combined.
    GEN-only T:Log a few sets to start tracki…
