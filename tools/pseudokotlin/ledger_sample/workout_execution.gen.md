# PseudoUI generated kit screen -- workout_execution  (from Compose WorkoutExecutionScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (457 calls)
```python
ui.define_box("workout_executio_z00_launchedeffect", "content", "V")
ui.define_box("workout_executio_z01_launchedeffect", "content", "V")
ui.define_box("workout_executio_z02_scaffold", "content", "V")
ui.define_box("workout_executio_z03_box", "workout_executio_z02_scaffold", "V")
ui.define_box("workout_executio_z04_circularprogress", "workout_executio_z03_box", "V")
ui.define_text("workout_executio_z05_uistate_error", "workout_executio_z03_box", "uiState.error!!")
ui.define_box("workout_executio_z06_column", "workout_executio_z03_box", "V")
ui.define_text("workout_executio_z07_this_workout_has", "workout_executio_z06_column", "This workout has no exercises")
ui.define_spacer_zone("workout_executio_z08_spacer", "workout_executio_z06_column")
ui.define_text("workout_executio_z09_its_program_day_", "workout_executio_z06_column", "Its program day came back empt…")
ui.define_spacer_zone("workout_executio_z10_spacer", "workout_executio_z06_column")
ui.define_button("workout_executio_z11_go_back", "workout_executio_z06_column", "Go back")
ui.define_box("workout_executio_z12_wflcompactdensit", "workout_executio_z03_box", "V")
ui.define_box("workout_executio_z13_compositionlocal", "workout_executio_z12_wflcompactdensit", "V")
ui.define_box("workout_executio_z14_executioncontent", "workout_executio_z12_wflcompactdensit", "V")
ui.define_box("workout_executio_z15_swapexercisedial", "workout_executio_z14_executioncontent", "V")
ui.define_box("workout_executio_z16_alertdialog", "workout_executio_z15_swapexercisedial", "V")
ui.define_text("workout_executio_z17_title", "workout_executio_z16_alertdialog", "title")
ui.define_box("workout_executio_z18_column", "workout_executio_z16_alertdialog", "V")
ui.define_box("workout_executio_z19_compactvaluefiel", "workout_executio_z18_column", "V")
ui.define_input_zone("workout_executio_z20_field", "workout_executio_z19_compactvaluefiel", "", "")
ui.define_text("workout_executio_z21_results_suggeste", "workout_executio_z18_column", "Results|Suggested")
ui.define_text("workout_executio_z22_no_matches_no_si", "workout_executio_z18_column", "No matches.|No similar exercis…")
ui.define_box("workout_executio_z23_lazycolumn", "workout_executio_z18_column", "V")
ui.define_box("workout_executio_z24_row", "workout_executio_z23_lazycolumn", "H")
ui.define_box("workout_executio_z25_column", "workout_executio_z24_row", "V")
ui.define_text("workout_executio_z26_exercise_name", "workout_executio_z25_column", "exercise.name")
ui.define_text("workout_executio_z27_x", "workout_executio_z25_column", " · ")
ui.define_box("workout_executio_z28_favoritetoggle", "workout_executio_z24_row", "V")
ui.define_icon("workout_executio_z29_remove_from_favo", "workout_executio_z28_favoritetoggle", "Remove from favourites|Add to …")
ui.define_divider_zone("workout_executio_z30_divider", "workout_executio_z23_lazycolumn")
ui.define_button("workout_executio_z31_remove_it", "workout_executio_z16_alertdialog", "Remove it")
ui.define_button("workout_executio_z32_close", "workout_executio_z16_alertdialog", "Close")
ui.define_box("workout_executio_z33_addexercisedialo", "workout_executio_z14_executioncontent", "V")
ui.define_box("workout_executio_z34_alertdialog", "workout_executio_z33_addexercisedialo", "V")
ui.define_text("workout_executio_z35_add_exercise", "workout_executio_z34_alertdialog", "Add exercise")
ui.define_box("workout_executio_z36_column", "workout_executio_z34_alertdialog", "V")
ui.define_box("workout_executio_z37_compactvaluefiel", "workout_executio_z36_column", "V")
ui.define_input_zone("workout_executio_z38_field", "workout_executio_z37_compactvaluefiel", "", "")
ui.define_box("workout_executio_z39_lazycolumn", "workout_executio_z36_column", "V")
ui.define_box("workout_executio_z40_row", "workout_executio_z39_lazycolumn", "H")
ui.define_text("workout_executio_z41_exercise_name", "workout_executio_z40_row", "exercise.name")
ui.define_box("workout_executio_z42_favoritetoggle", "workout_executio_z40_row", "V")
ui.define_icon("workout_executio_z43_remove_from_favo", "workout_executio_z42_favoritetoggle", "Remove from favourites|Add to …")
ui.define_divider_zone("workout_executio_z44_divider", "workout_executio_z39_lazycolumn")
ui.define_button("workout_executio_z45_close", "workout_executio_z34_alertdialog", "Close")
ui.define_box("workout_executio_z46_reorderexercises", "workout_executio_z14_executioncontent", "V")
ui.define_box("workout_executio_z47_alertdialog", "workout_executio_z46_reorderexercises", "V")
ui.define_text("workout_executio_z48_reorder_exercise", "workout_executio_z47_alertdialog", "Reorder exercises")
ui.define_box("workout_executio_z49_lazycolumn", "workout_executio_z47_alertdialog", "V")
ui.define_box("workout_executio_z50_row", "workout_executio_z49_lazycolumn", "H")
ui.define_text("workout_executio_z51_item_exercise_na", "workout_executio_z50_row", "item.exercise.name")
ui.define_icon("workout_executio_z52_move_up", "workout_executio_z50_row", "Move up")
ui.define_icon("workout_executio_z53_move_down", "workout_executio_z50_row", "Move down")
ui.define_button("workout_executio_z54_done", "workout_executio_z47_alertdialog", "Done")
ui.define_box("workout_executio_z55_removeexercisedi", "workout_executio_z14_executioncontent", "V")
ui.define_box("workout_executio_z56_alertdialog", "workout_executio_z55_removeexercisedi", "V")
ui.define_text("workout_executio_z57_remove_confirmit", "workout_executio_z56_alertdialog", "Remove ${confirmItem.exercise.…")
ui.define_text("workout_executio_z58_this_exercise_ha", "workout_executio_z56_alertdialog", "This exercise has logged sets.…")
ui.define_button("workout_executio_z59_remove", "workout_executio_z56_alertdialog", "Remove")
ui.define_button("workout_executio_z60_cancel", "workout_executio_z56_alertdialog", "Cancel")
ui.define_box("workout_executio_z61_alertdialog", "workout_executio_z55_removeexercisedi", "V")
ui.define_text("workout_executio_z62_remove_exercise", "workout_executio_z61_alertdialog", "Remove exercise")
ui.define_box("workout_executio_z63_lazycolumn", "workout_executio_z61_alertdialog", "V")
ui.define_box("workout_executio_z64_row", "workout_executio_z63_lazycolumn", "H")
ui.define_box("workout_executio_z65_column", "workout_executio_z64_row", "V")
ui.define_text("workout_executio_z66_item_exercise_na", "workout_executio_z65_column", "item.exercise.name")
ui.define_text("workout_executio_z67_item_completedse", "workout_executio_z65_column", "${item.completedSetsCount} set…")
ui.define_icon("workout_executio_z68_remove_item_exer", "workout_executio_z64_row", "Remove ${item.exercise.name}")
ui.define_button("workout_executio_z69_close", "workout_executio_z61_alertdialog", "Close")
ui.define_box("workout_executio_z70_editsupersetdial", "workout_executio_z14_executioncontent", "V")
ui.define_box("workout_executio_z71_alertdialog", "workout_executio_z70_editsupersetdial", "V")
ui.define_text("workout_executio_z72_edit_supersets", "workout_executio_z71_alertdialog", "Edit supersets")
ui.define_box("workout_executio_z73_column", "workout_executio_z71_alertdialog", "V")
ui.define_text("workout_executio_z74_check_exercises_", "workout_executio_z73_column", "Check exercises and tap Link t…")
ui.define_box("workout_executio_z75_lazycolumn", "workout_executio_z73_column", "V")
ui.define_box("workout_executio_z76_row", "workout_executio_z75_lazycolumn", "H")
ui.define_box("workout_executio_z77_checkbox", "workout_executio_z76_row", "V")
ui.define_box("workout_executio_z78_column", "workout_executio_z76_row", "V")
ui.define_text("workout_executio_z79_item_exercise_na", "workout_executio_z78_column", "item.exercise.name")
ui.define_box("workout_executio_z80_row", "workout_executio_z78_column", "H")
ui.define_icon("workout_executio_z81_icon", "workout_executio_z80_row", "")
ui.define_text("workout_executio_z82_superset_groupla", "workout_executio_z80_row", " Superset $groupLabel")
ui.define_icon("workout_executio_z83_move_up", "workout_executio_z76_row", "Move up")
ui.define_icon("workout_executio_z84_move_down", "workout_executio_z76_row", "Move down")
ui.define_box("workout_executio_z85_row", "workout_executio_z73_column", "H")
ui.define_button("workout_executio_z86_unlink", "workout_executio_z85_row", "Unlink")
ui.define_button("workout_executio_z87_link", "workout_executio_z85_row", "Link")
ui.define_button("workout_executio_z88_done", "workout_executio_z71_alertdialog", "Done")
ui.define_box("workout_executio_z89_alertdialog", "workout_executio_z14_executioncontent", "V")
ui.define_text("workout_executio_z90_some_set_lines_a", "workout_executio_z89_alertdialog", "Some set lines are empty")
ui.define_text("workout_executio_z91_do_you_want_to_u", "workout_executio_z89_alertdialog", "Do you want to update your dat…")
ui.define_button("workout_executio_z92_keep_editing", "workout_executio_z89_alertdialog", "Keep editing")
ui.define_button("workout_executio_z93_leave_anyway", "workout_executio_z89_alertdialog", "Leave anyway")
ui.define_box("workout_executio_z94_column", "workout_executio_z14_executioncontent", "V")
ui.define_box("workout_executio_z95_box", "workout_executio_z94_column", "V")
ui.define_box("workout_executio_z96_animatedcontent", "workout_executio_z95_box", "V")
ui.define_box("workout_executio_z97_box", "workout_executio_z96_animatedcontent", "V")
ui.define_box("workout_executio_z98_column", "workout_executio_z96_animatedcontent", "V")
ui.define_box("workout_executio_z99_exerciseheader", "workout_executio_z98_column", "V")
ui.define_box("workout_executio_z100_row", "workout_executio_z99_exerciseheader", "H")
ui.define_box("workout_executio_z101_column", "workout_executio_z100_row", "V")
ui.define_text("workout_executio_z102_exercise_name", "workout_executio_z101_column", "exercise.name")
ui.define_box("workout_executio_z103_row", "workout_executio_z101_column", "H")
ui.define_text("workout_executio_z104_it", "workout_executio_z103_row", "it")
ui.define_icon("workout_executio_z105_why_this_target", "workout_executio_z103_row", "Why this target")
ui.define_icon("workout_executio_z106_favorite", "workout_executio_z100_row", "Favorite")
ui.define_icon("workout_executio_z107_exercise_info", "workout_executio_z100_row", "Exercise info")
ui.define_box("workout_executio_z108_dialog", "workout_executio_z99_exerciseheader", "V")
ui.define_box("workout_executio_z109_surface", "workout_executio_z108_dialog", "V")
ui.define_box("workout_executio_z110_column", "workout_executio_z109_surface", "V")
ui.define_text("workout_executio_z111_exercise_name", "workout_executio_z110_column", "exercise.name")
ui.define_text("workout_executio_z112_no_instructions_", "workout_executio_z110_column", "No instructions provided.")
ui.define_button("workout_executio_z113_swap_exercise", "workout_executio_z110_column", "Swap exercise")
ui.define_button("workout_executio_z114_dismiss", "workout_executio_z110_column", "Dismiss")
ui.define_box("workout_executio_z115_dialog", "workout_executio_z99_exerciseheader", "V")
ui.define_box("workout_executio_z116_surface", "workout_executio_z115_dialog", "V")
ui.define_box("workout_executio_z117_column", "workout_executio_z116_surface", "V")
ui.define_text("workout_executio_z118_exercise_name", "workout_executio_z117_column", "exercise.name")
ui.define_text("workout_executio_z119_it", "workout_executio_z117_column", "it")
ui.define_text("workout_executio_z120_your_coach_s_not", "workout_executio_z117_column", "Your coach's note for this exe…")
ui.define_button("workout_executio_z121_dismiss", "workout_executio_z117_column", "Dismiss")
ui.define_spacer_zone("workout_executio_z122_spacer", "workout_executio_z98_column")
ui.define_box("workout_executio_z123_settable", "workout_executio_z98_column", "V")
ui.define_box("workout_executio_z124_mobilitysettable", "workout_executio_z123_settable", "V")
ui.define_box("workout_executio_z125_column", "workout_executio_z124_mobilitysettable", "V")
ui.define_box("workout_executio_z126_row", "workout_executio_z125_column", "H")
ui.define_text("workout_executio_z127_hold", "workout_executio_z126_row", "Hold")
ui.define_divider_zone("workout_executio_z128_divider", "workout_executio_z125_column")
ui.define_box("workout_executio_z129_row", "workout_executio_z125_column", "H")
ui.define_icon("workout_executio_z130_logged", "workout_executio_z129_row", "Logged")
ui.define_spacer_zone("workout_executio_z131_spacer", "workout_executio_z129_row")
ui.define_text("workout_executio_z132_loggedhold_durat", "workout_executio_z129_row", "${loggedHold.durationSeconds ?…")
ui.define_spacer_zone("workout_executio_z133_spacer", "workout_executio_z125_column")
ui.define_box("workout_executio_z134_row", "workout_executio_z125_column", "H")
ui.define_button("workout_executio_z135_x", "workout_executio_z134_row", "−")
ui.define_spacer_zone("workout_executio_z136_spacer", "workout_executio_z134_row")
ui.define_box("workout_executio_z137_column", "workout_executio_z134_row", "V")
ui.define_text("workout_executio_z138_uistate_pendingh", "workout_executio_z137_column", "${uiState.pendingHoldSeconds}s…")
ui.define_text("workout_executio_z139_hold", "workout_executio_z137_column", "hold")
ui.define_spacer_zone("workout_executio_z140_spacer", "workout_executio_z134_row")
ui.define_button("workout_executio_z141_x", "workout_executio_z134_row", "+")
ui.define_spacer_zone("workout_executio_z142_spacer", "workout_executio_z125_column")
ui.define_box("workout_executio_z143_restbar", "workout_executio_z125_column", "V")
ui.define_box("workout_executio_z144_box", "workout_executio_z143_restbar", "V")
ui.define_box("workout_executio_z145_box", "workout_executio_z144_box", "V")
ui.define_box("workout_executio_z146_row", "workout_executio_z144_box", "H")
ui.define_text("workout_executio_z147_rest", "workout_executio_z146_row", "REST")
ui.define_spacer_zone("workout_executio_z148_spacer", "workout_executio_z146_row")
ui.define_text("workout_executio_z149_formatresttime_r", "workout_executio_z146_row", "formatRestTime(restState.remai…")
ui.define_spacer_zone("workout_executio_z150_spacer", "workout_executio_z146_row")
ui.define_button("workout_executio_z151_30s", "workout_executio_z146_row", "+30s")
ui.define_button("workout_executio_z152_skip", "workout_executio_z146_row", "Skip")
ui.define_spacer_zone("workout_executio_z153_spacer", "workout_executio_z125_column")
ui.define_box("workout_executio_z154_row", "workout_executio_z125_column", "H")
ui.define_button("workout_executio_z155_restart_start_ho", "workout_executio_z154_row", "Restart|Start hold")
ui.define_button("workout_executio_z156_log_set_next", "workout_executio_z154_row", "Log Set & Next")
ui.define_spacer_zone("workout_executio_z157_spacer", "workout_executio_z125_column")
ui.define_box("workout_executio_z158_row", "workout_executio_z125_column", "H")
ui.define_text("workout_executio_z159_default_hold_sec", "workout_executio_z158_row", "${DEFAULT_HOLD_SECONDS}s$perSi…")
ui.define_divider_zone("workout_executio_z160_divider", "workout_executio_z125_column")
ui.define_box("workout_executio_z161_column", "workout_executio_z123_settable", "V")
ui.define_box("workout_executio_z162_row", "workout_executio_z161_column", "H")
ui.define_text("workout_executio_z163_set", "workout_executio_z162_row", "Set #")
ui.define_text("workout_executio_z164_rpeheader", "workout_executio_z162_row", "rpeHeader")
ui.define_text("workout_executio_z165_weight_unit_labe", "workout_executio_z162_row", "Weight (${unit.label()})")
ui.define_text("workout_executio_z166_reps", "workout_executio_z162_row", "Reps")
ui.define_text("workout_executio_z167_set_type", "workout_executio_z162_row", "Set type")
ui.define_divider_zone("workout_executio_z168_divider", "workout_executio_z161_column")
ui.define_box("workout_executio_z169_inprogresssetrow", "workout_executio_z161_column", "V")
ui.define_box("workout_executio_z170_column", "workout_executio_z169_inprogresssetrow", "V")
ui.define_box("workout_executio_z171_row", "workout_executio_z170_column", "H")
ui.define_text("workout_executio_z172_label", "workout_executio_z171_row", "label")
ui.define_text("workout_executio_z173_warmuppct_0", "workout_executio_z171_row", "${warmupPct ?: 0}%|?")
ui.define_text("workout_executio_z174_formatweightfiel", "workout_executio_z171_row", "${formatWeightField(uiState.pe…")
ui.define_text("workout_executio_z175_x", "workout_executio_z171_row", "—")
ui.define_box("workout_executio_z176_box", "workout_executio_z171_row", "V")
ui.define_text("workout_executio_z177_uistate_pendings", "workout_executio_z176_box", "uiState.pendingSetType.display…")
ui.define_box("workout_executio_z178_dropdownmenu", "workout_executio_z176_box", "V")
ui.define_box("workout_executio_z179_dropdownmenuitem", "workout_executio_z178_dropdownmenu", "V")
ui.define_text("workout_executio_z180_type_displayname", "workout_executio_z179_dropdownmenuitem", "type.displayName")
ui.define_spacer_zone("workout_executio_z181_spacer", "workout_executio_z170_column")
ui.define_box("workout_executio_z182_row", "workout_executio_z170_column", "H")
ui.define_box("workout_executio_z183_column", "workout_executio_z182_row", "V")
ui.define_text("workout_executio_z184_rpelabel", "workout_executio_z183_column", "rpeLabel")
ui.define_spacer_zone("workout_executio_z185_spacer", "workout_executio_z183_column")
ui.define_box("workout_executio_z186_valueadjuster", "workout_executio_z183_column", "V")
ui.define_box("workout_executio_z187_textfieldvalue", "workout_executio_z186_valueadjuster", "V")
ui.define_box("workout_executio_z188_launchedeffect", "workout_executio_z186_valueadjuster", "V")
ui.define_box("workout_executio_z189_textfieldvalue", "workout_executio_z188_launchedeffect", "V")
ui.define_box("workout_executio_z190_launchedeffect", "workout_executio_z186_valueadjuster", "V")
ui.define_box("workout_executio_z191_textrange", "workout_executio_z190_launchedeffect", "V")
ui.define_box("workout_executio_z192_row", "workout_executio_z186_valueadjuster", "H")
ui.define_button("workout_executio_z193_iconbutton", "workout_executio_z192_row", "")
ui.define_input_zone("workout_executio_z194_field", "workout_executio_z192_row", "", "")
ui.define_button("workout_executio_z195_iconbutton", "workout_executio_z192_row", "")
ui.define_box("workout_executio_z196_column", "workout_executio_z182_row", "V")
ui.define_text("workout_executio_z197_weight_per_side_", "workout_executio_z196_column", "Weight (per side)|Weight")
ui.define_spacer_zone("workout_executio_z198_spacer", "workout_executio_z196_column")
ui.define_box("workout_executio_z199_valueadjuster", "workout_executio_z196_column", "V")
ui.define_box("workout_executio_z200_textfieldvalue", "workout_executio_z199_valueadjuster", "V")
ui.define_box("workout_executio_z201_launchedeffect", "workout_executio_z199_valueadjuster", "V")
ui.define_box("workout_executio_z202_textfieldvalue", "workout_executio_z201_launchedeffect", "V")
ui.define_box("workout_executio_z203_launchedeffect", "workout_executio_z199_valueadjuster", "V")
ui.define_box("workout_executio_z204_textrange", "workout_executio_z203_launchedeffect", "V")
ui.define_box("workout_executio_z205_row", "workout_executio_z199_valueadjuster", "H")
ui.define_button("workout_executio_z206_iconbutton", "workout_executio_z205_row", "")
ui.define_input_zone("workout_executio_z207_field", "workout_executio_z205_row", "", "")
ui.define_button("workout_executio_z208_iconbutton", "workout_executio_z205_row", "")
ui.define_box("workout_executio_z209_column", "workout_executio_z182_row", "V")
ui.define_text("workout_executio_z210_reps", "workout_executio_z209_column", "Reps")
ui.define_spacer_zone("workout_executio_z211_spacer", "workout_executio_z209_column")
ui.define_box("workout_executio_z212_valueadjuster", "workout_executio_z209_column", "V")
ui.define_box("workout_executio_z213_textfieldvalue", "workout_executio_z212_valueadjuster", "V")
ui.define_box("workout_executio_z214_launchedeffect", "workout_executio_z212_valueadjuster", "V")
ui.define_box("workout_executio_z215_textfieldvalue", "workout_executio_z214_launchedeffect", "V")
ui.define_box("workout_executio_z216_launchedeffect", "workout_executio_z212_valueadjuster", "V")
ui.define_box("workout_executio_z217_textrange", "workout_executio_z216_launchedeffect", "V")
ui.define_box("workout_executio_z218_row", "workout_executio_z212_valueadjuster", "H")
ui.define_button("workout_executio_z219_iconbutton", "workout_executio_z218_row", "")
ui.define_input_zone("workout_executio_z220_field", "workout_executio_z218_row", "", "")
ui.define_button("workout_executio_z221_iconbutton", "workout_executio_z218_row", "")
ui.define_spacer_zone("workout_executio_z222_spacer", "workout_executio_z170_column")
ui.define_text("workout_executio_z223_effortscale_full", "workout_executio_z170_column", "EffortScale.full(currentRung, …")
ui.define_spacer_zone("workout_executio_z224_spacer", "workout_executio_z170_column")
ui.define_box("workout_executio_z225_subentryrow", "workout_executio_z170_column", "V")
ui.define_box("workout_executio_z226_row", "workout_executio_z225_subentryrow", "H")
ui.define_text("workout_executio_z227_setnumber_a_entr", "workout_executio_z226_row", "$setNumber${'a' + entry.entryI…")
ui.define_spacer_zone("workout_executio_z228_spacer", "workout_executio_z226_row")
ui.define_text("workout_executio_z229_weighttext", "workout_executio_z226_row", "weightText")
ui.define_text("workout_executio_z230_x", "workout_executio_z226_row", "—")
ui.define_spacer_zone("workout_executio_z231_spacer", "workout_executio_z226_row")
ui.define_spacer_zone("workout_executio_z232_spacer", "workout_executio_z170_column")
ui.define_box("workout_executio_z233_row", "workout_executio_z170_column", "H")
ui.define_button("workout_executio_z234_log_entryword", "workout_executio_z233_row", "Log $entryWord")
ui.define_button("workout_executio_z235_finish_set", "workout_executio_z233_row", "Finish set")
ui.define_button("workout_executio_z236_log_set_next_log", "workout_executio_z170_column", "Log set & next|Log set")
ui.define_box("workout_executio_z237_warmupstaticrow", "workout_executio_z161_column", "V")
ui.define_box("workout_executio_z238_row", "workout_executio_z237_warmupstaticrow", "H")
ui.define_box("workout_executio_z239_box", "workout_executio_z238_row", "V")
ui.define_text("workout_executio_z240_label", "workout_executio_z239_box", "label")
ui.define_icon("workout_executio_z241_completed", "workout_executio_z239_box", "Completed")
ui.define_text("workout_executio_z242_plan_pctofworkin", "workout_executio_z238_row", "${plan.pctOfWorking}%")
ui.define_text("workout_executio_z243_loadlabel", "workout_executio_z238_row", "loadLabel")
ui.define_text("workout_executio_z244_reps_tostring", "workout_executio_z238_row", "reps.toString()")
ui.define_text("workout_executio_z245_settype_warmup_d", "workout_executio_z238_row", "SetType.WARMUP.displayName")
ui.define_divider_zone("workout_executio_z246_divider", "workout_executio_z161_column")
ui.define_box("workout_executio_z247_restbar", "workout_executio_z161_column", "V")
ui.define_box("workout_executio_z248_box", "workout_executio_z247_restbar", "V")
ui.define_box("workout_executio_z249_box", "workout_executio_z248_box", "V")
ui.define_box("workout_executio_z250_row", "workout_executio_z248_box", "H")
ui.define_text("workout_executio_z251_rest", "workout_executio_z250_row", "REST")
ui.define_spacer_zone("workout_executio_z252_spacer", "workout_executio_z250_row")
ui.define_text("workout_executio_z253_formatresttime_r", "workout_executio_z250_row", "formatRestTime(restState.remai…")
ui.define_spacer_zone("workout_executio_z254_spacer", "workout_executio_z250_row")
ui.define_button("workout_executio_z255_30s", "workout_executio_z250_row", "+30s")
ui.define_button("workout_executio_z256_skip", "workout_executio_z250_row", "Skip")
ui.define_divider_zone("workout_executio_z257_divider", "workout_executio_z161_column")
ui.define_box("workout_executio_z258_inprogresssetrow", "workout_executio_z161_column", "V")
ui.define_box("workout_executio_z259_column", "workout_executio_z258_inprogresssetrow", "V")
ui.define_box("workout_executio_z260_row", "workout_executio_z259_column", "H")
ui.define_text("workout_executio_z261_setnumber_tostri", "workout_executio_z260_row", "setNumber.toString()")
ui.define_text("workout_executio_z262_warmuppct_0", "workout_executio_z260_row", "${warmupPct ?: 0}%|?")
ui.define_text("workout_executio_z263_formatweightfiel", "workout_executio_z260_row", "${formatWeightField(uiState.pe…")
ui.define_text("workout_executio_z264_x", "workout_executio_z260_row", "—")
ui.define_box("workout_executio_z265_box", "workout_executio_z260_row", "V")
ui.define_text("workout_executio_z266_uistate_pendings", "workout_executio_z265_box", "uiState.pendingSetType.display…")
ui.define_box("workout_executio_z267_dropdownmenu", "workout_executio_z265_box", "V")
ui.define_box("workout_executio_z268_dropdownmenuitem", "workout_executio_z267_dropdownmenu", "V")
ui.define_text("workout_executio_z269_type_displayname", "workout_executio_z268_dropdownmenuitem", "type.displayName")
ui.define_spacer_zone("workout_executio_z270_spacer", "workout_executio_z259_column")
ui.define_box("workout_executio_z271_row", "workout_executio_z259_column", "H")
ui.define_box("workout_executio_z272_column", "workout_executio_z271_row", "V")
ui.define_text("workout_executio_z273_rpelabel", "workout_executio_z272_column", "rpeLabel")
ui.define_spacer_zone("workout_executio_z274_spacer", "workout_executio_z272_column")
ui.define_box("workout_executio_z275_valueadjuster", "workout_executio_z272_column", "V")
ui.define_box("workout_executio_z276_textfieldvalue", "workout_executio_z275_valueadjuster", "V")
ui.define_box("workout_executio_z277_launchedeffect", "workout_executio_z275_valueadjuster", "V")
ui.define_box("workout_executio_z278_textfieldvalue", "workout_executio_z277_launchedeffect", "V")
ui.define_box("workout_executio_z279_launchedeffect", "workout_executio_z275_valueadjuster", "V")
ui.define_box("workout_executio_z280_textrange", "workout_executio_z279_launchedeffect", "V")
ui.define_box("workout_executio_z281_row", "workout_executio_z275_valueadjuster", "H")
ui.define_button("workout_executio_z282_iconbutton", "workout_executio_z281_row", "")
ui.define_input_zone("workout_executio_z283_field", "workout_executio_z281_row", "", "")
ui.define_button("workout_executio_z284_iconbutton", "workout_executio_z281_row", "")
ui.define_box("workout_executio_z285_column", "workout_executio_z271_row", "V")
ui.define_text("workout_executio_z286_weight_per_side_", "workout_executio_z285_column", "Weight (per side)|Weight")
ui.define_spacer_zone("workout_executio_z287_spacer", "workout_executio_z285_column")
ui.define_box("workout_executio_z288_valueadjuster", "workout_executio_z285_column", "V")
ui.define_box("workout_executio_z289_textfieldvalue", "workout_executio_z288_valueadjuster", "V")
ui.define_box("workout_executio_z290_launchedeffect", "workout_executio_z288_valueadjuster", "V")
ui.define_box("workout_executio_z291_textfieldvalue", "workout_executio_z290_launchedeffect", "V")
ui.define_box("workout_executio_z292_launchedeffect", "workout_executio_z288_valueadjuster", "V")
ui.define_box("workout_executio_z293_textrange", "workout_executio_z292_launchedeffect", "V")
ui.define_box("workout_executio_z294_row", "workout_executio_z288_valueadjuster", "H")
ui.define_button("workout_executio_z295_iconbutton", "workout_executio_z294_row", "")
ui.define_input_zone("workout_executio_z296_field", "workout_executio_z294_row", "", "")
ui.define_button("workout_executio_z297_iconbutton", "workout_executio_z294_row", "")
ui.define_box("workout_executio_z298_column", "workout_executio_z271_row", "V")
ui.define_text("workout_executio_z299_reps", "workout_executio_z298_column", "Reps")
ui.define_spacer_zone("workout_executio_z300_spacer", "workout_executio_z298_column")
ui.define_box("workout_executio_z301_valueadjuster", "workout_executio_z298_column", "V")
ui.define_box("workout_executio_z302_textfieldvalue", "workout_executio_z301_valueadjuster", "V")
ui.define_box("workout_executio_z303_launchedeffect", "workout_executio_z301_valueadjuster", "V")
ui.define_box("workout_executio_z304_textfieldvalue", "workout_executio_z303_launchedeffect", "V")
ui.define_box("workout_executio_z305_launchedeffect", "workout_executio_z301_valueadjuster", "V")
ui.define_box("workout_executio_z306_textrange", "workout_executio_z305_launchedeffect", "V")
ui.define_box("workout_executio_z307_row", "workout_executio_z301_valueadjuster", "H")
ui.define_button("workout_executio_z308_iconbutton", "workout_executio_z307_row", "")
ui.define_input_zone("workout_executio_z309_field", "workout_executio_z307_row", "", "")
ui.define_button("workout_executio_z310_iconbutton", "workout_executio_z307_row", "")
ui.define_spacer_zone("workout_executio_z311_spacer", "workout_executio_z259_column")
ui.define_text("workout_executio_z312_effortscale_full", "workout_executio_z259_column", "EffortScale.full(currentRung, …")
ui.define_spacer_zone("workout_executio_z313_spacer", "workout_executio_z259_column")
ui.define_box("workout_executio_z314_subentryrow", "workout_executio_z259_column", "V")
ui.define_box("workout_executio_z315_row", "workout_executio_z314_subentryrow", "H")
ui.define_text("workout_executio_z316_setnumber_a_entr", "workout_executio_z315_row", "$setNumber${'a' + entry.entryI…")
ui.define_spacer_zone("workout_executio_z317_spacer", "workout_executio_z315_row")
ui.define_text("workout_executio_z318_weighttext", "workout_executio_z315_row", "weightText")
ui.define_text("workout_executio_z319_x", "workout_executio_z315_row", "—")
ui.define_spacer_zone("workout_executio_z320_spacer", "workout_executio_z315_row")
ui.define_spacer_zone("workout_executio_z321_spacer", "workout_executio_z259_column")
ui.define_box("workout_executio_z322_row", "workout_executio_z259_column", "H")
ui.define_button("workout_executio_z323_log_entryword", "workout_executio_z322_row", "Log $entryWord")
ui.define_button("workout_executio_z324_finish_set", "workout_executio_z322_row", "Finish set")
ui.define_button("workout_executio_z325_log_set_next_log", "workout_executio_z259_column", "Log set & next|Log set")
ui.define_box("workout_executio_z326_column", "workout_executio_z161_column", "V")
ui.define_box("workout_executio_z327_swipeablesetrow", "workout_executio_z326_column", "V")
ui.define_box("workout_executio_z328_swipetodismissbo", "workout_executio_z327_swipeablesetrow", "V")
ui.define_box("workout_executio_z329_staticsetrow", "workout_executio_z328_swipetodismissbo", "V")
ui.define_box("workout_executio_z330_row", "workout_executio_z329_staticsetrow", "H")
ui.define_box("workout_executio_z331_box", "workout_executio_z330_row", "V")
ui.define_text("workout_executio_z332_setnumber_tostri", "workout_executio_z331_box", "setNumber.toString()")
ui.define_icon("workout_executio_z333_completed", "workout_executio_z331_box", "Completed")
ui.define_text("workout_executio_z334_rpetext", "workout_executio_z330_row", "rpeText")
ui.define_text("workout_executio_z335_weighttext", "workout_executio_z330_row", "weightText")
ui.define_text("workout_executio_z336_x", "workout_executio_z330_row", "—")
ui.define_text("workout_executio_z337_settype_displayn", "workout_executio_z330_row", "setType.displayName")
ui.define_box("workout_executio_z338_box", "workout_executio_z328_swipetodismissbo", "V")
ui.define_icon("workout_executio_z339_delete", "workout_executio_z338_box", "Delete")
ui.define_box("workout_executio_z340_subentryrow", "workout_executio_z326_column", "V")
ui.define_box("workout_executio_z341_row", "workout_executio_z340_subentryrow", "H")
ui.define_text("workout_executio_z342_setnumber_a_entr", "workout_executio_z341_row", "$setNumber${'a' + entry.entryI…")
ui.define_spacer_zone("workout_executio_z343_spacer", "workout_executio_z341_row")
ui.define_text("workout_executio_z344_weighttext", "workout_executio_z341_row", "weightText")
ui.define_text("workout_executio_z345_x", "workout_executio_z341_row", "—")
ui.define_spacer_zone("workout_executio_z346_spacer", "workout_executio_z341_row")
ui.define_divider_zone("workout_executio_z347_divider", "workout_executio_z161_column")
ui.define_spacer_zone("workout_executio_z348_spacer", "workout_executio_z161_column")
ui.define_button("workout_executio_z349_add_set", "workout_executio_z161_column", "Add set")
ui.define_spacer_zone("workout_executio_z350_spacer", "workout_executio_z98_column")
ui.define_input_zone("workout_executio_z351_exercise_notes", "workout_executio_z98_column", "", "Exercise notes")
ui.define_divider_zone("workout_executio_z352_divider", "workout_executio_z94_column")
ui.define_box("workout_executio_z353_upnextqueue", "workout_executio_z94_column", "V")
ui.define_box("workout_executio_z354_launchedeffect", "workout_executio_z353_upnextqueue", "V")
ui.define_box("workout_executio_z355_column", "workout_executio_z353_upnextqueue", "V")
ui.define_box("workout_executio_z356_row", "workout_executio_z355_column", "H")
ui.define_text("workout_executio_z357_up_next", "workout_executio_z356_row", "UP NEXT")
ui.define_box("workout_executio_z358_upnextmenu", "workout_executio_z356_row", "V")
ui.define_box("workout_executio_z359_box", "workout_executio_z358_upnextmenu", "V")
ui.define_icon("workout_executio_z360_manage_exercises", "workout_executio_z359_box", "Manage exercises")
ui.define_box("workout_executio_z361_dropdownmenu", "workout_executio_z359_box", "V")
ui.define_box("workout_executio_z362_dropdownmenuitem", "workout_executio_z361_dropdownmenu", "V")
ui.define_text("workout_executio_z363_add_exercise", "workout_executio_z362_dropdownmenuitem", "Add exercise")
ui.define_icon("workout_executio_z364_icon", "workout_executio_z362_dropdownmenuitem", "")
ui.define_box("workout_executio_z365_dropdownmenuitem", "workout_executio_z361_dropdownmenu", "V")
ui.define_text("workout_executio_z366_reorder_exercise", "workout_executio_z365_dropdownmenuitem", "Reorder exercises")
ui.define_icon("workout_executio_z367_icon", "workout_executio_z365_dropdownmenuitem", "")
ui.define_box("workout_executio_z368_dropdownmenuitem", "workout_executio_z361_dropdownmenu", "V")
ui.define_text("workout_executio_z369_edit_superset", "workout_executio_z368_dropdownmenuitem", "Edit superset")
ui.define_icon("workout_executio_z370_icon", "workout_executio_z368_dropdownmenuitem", "")
ui.define_box("workout_executio_z371_dropdownmenuitem", "workout_executio_z361_dropdownmenu", "V")
ui.define_text("workout_executio_z372_remove_exercise", "workout_executio_z371_dropdownmenuitem", "Remove exercise")
ui.define_icon("workout_executio_z373_icon", "workout_executio_z371_dropdownmenuitem", "")
ui.define_spacer_zone("workout_executio_z374_spacer", "workout_executio_z355_column")
ui.define_box("workout_executio_z375_lazyrow", "workout_executio_z355_column", "H")
ui.define_box("workout_executio_z376_box", "workout_executio_z375_lazyrow", "V")
ui.define_box("workout_executio_z377_exercisepill", "workout_executio_z376_box", "V")
ui.define_box("workout_executio_z378_surface", "workout_executio_z377_exercisepill", "V")
ui.define_text("workout_executio_z379_item_exercise_na", "workout_executio_z378_surface", "item.exercise.name")
ui.define_icon("workout_executio_z380_supersetted_with", "workout_executio_z376_box", "Supersetted with previous exer…")
ui.define_box("workout_executio_z381_column", "workout_executio_z03_box", "V")
ui.define_box("workout_executio_z382_animatedvisibili", "workout_executio_z381_column", "V")
ui.define_box("workout_executio_z383_prbanner", "workout_executio_z382_animatedvisibili", "V")
ui.define_box("workout_executio_z384_wflcard", "workout_executio_z383_prbanner", "V")
ui.define_box("workout_executio_z385_roundedcornersha", "workout_executio_z384_wflcard", "V")
ui.define_box("workout_executio_z386_borderstroke", "workout_executio_z384_wflcard", "V")
ui.define_box("workout_executio_z387_card", "workout_executio_z384_wflcard", "V")
ui.define_box("workout_executio_z388_card", "workout_executio_z384_wflcard", "V")
ui.define_box("workout_executio_z389_row", "workout_executio_z384_wflcard", "H")
ui.define_box("workout_executio_z390_column", "workout_executio_z389_row", "V")
ui.define_text("workout_executio_z391_new_personal_rec", "workout_executio_z390_column", "NEW PERSONAL RECORD")
ui.define_text("workout_executio_z392_text", "workout_executio_z390_column", "")
ui.define_text("workout_executio_z393_tap_to_dismiss", "workout_executio_z389_row", "tap to dismiss")
ui.define_box("workout_executio_z394_animatedvisibili", "workout_executio_z381_column", "V")
ui.define_box("workout_executio_z395_midmicrocycleban", "workout_executio_z394_animatedvisibili", "V")
ui.define_box("workout_executio_z396_wflcard", "workout_executio_z395_midmicrocycleban", "V")
ui.define_box("workout_executio_z397_roundedcornersha", "workout_executio_z396_wflcard", "V")
ui.define_box("workout_executio_z398_borderstroke", "workout_executio_z396_wflcard", "V")
ui.define_box("workout_executio_z399_card", "workout_executio_z396_wflcard", "V")
ui.define_box("workout_executio_z400_card", "workout_executio_z396_wflcard", "V")
ui.define_box("workout_executio_z401_row", "workout_executio_z396_wflcard", "H")
ui.define_text("workout_executio_z402_text", "workout_executio_z401_row", "")
ui.define_text("workout_executio_z403_tap_to_dismiss", "workout_executio_z401_row", "tap to dismiss")
ui.define_box("workout_executio_z404_animatedvisibili", "workout_executio_z381_column", "V")
ui.define_box("workout_executio_z405_cardioreadinessn", "workout_executio_z404_animatedvisibili", "V")
ui.define_box("workout_executio_z406_wflcard", "workout_executio_z405_cardioreadinessn", "V")
ui.define_box("workout_executio_z407_roundedcornersha", "workout_executio_z406_wflcard", "V")
ui.define_box("workout_executio_z408_borderstroke", "workout_executio_z406_wflcard", "V")
ui.define_box("workout_executio_z409_card", "workout_executio_z406_wflcard", "V")
ui.define_box("workout_executio_z410_card", "workout_executio_z406_wflcard", "V")
ui.define_text("workout_executio_z411_message", "workout_executio_z406_wflcard", "message")
ui.define_box("workout_executio_z412_alertdialog", "workout_executio_z02_scaffold", "V")
ui.define_text("workout_executio_z413_discard_this_wor", "workout_executio_z412_alertdialog", "Discard this workout?")
ui.define_text("workout_executio_z414_everything_you_v", "workout_executio_z412_alertdialog", "Everything you've logged in th…")
ui.define_button("workout_executio_z415_discard", "workout_executio_z412_alertdialog", "Discard")
ui.define_button("workout_executio_z416_keep_going", "workout_executio_z412_alertdialog", "Keep going")
ui.define_box("workout_executio_z417_platecalculators", "workout_executio_z02_scaffold", "V")
ui.define_box("workout_executio_z418_modalbottomsheet", "workout_executio_z417_platecalculators", "V")
ui.define_box("workout_executio_z419_column", "workout_executio_z418_modalbottomsheet", "V")
ui.define_text("workout_executio_z420_plate_calculator", "workout_executio_z419_column", "PLATE CALCULATOR")
ui.define_spacer_zone("workout_executio_z421_spacer", "workout_executio_z419_column")
ui.define_text("workout_executio_z422_target_weight", "workout_executio_z419_column", "TARGET WEIGHT")
ui.define_spacer_zone("workout_executio_z423_spacer", "workout_executio_z419_column")
ui.define_box("workout_executio_z424_row", "workout_executio_z419_column", "H")
ui.define_button("workout_executio_z425_fillediconbutton", "workout_executio_z424_row", "")
ui.define_text("workout_executio_z426_displaytarget_fm", "workout_executio_z424_row", "${displayTarget.fmt()} $unitLa…")
ui.define_button("workout_executio_z427_fillediconbutton", "workout_executio_z424_row", "")
ui.define_spacer_zone("workout_executio_z428_spacer", "workout_executio_z419_column")
ui.define_text("workout_executio_z429_bar", "workout_executio_z419_column", "BAR")
ui.define_spacer_zone("workout_executio_z430_spacer", "workout_executio_z419_column")
ui.define_box("workout_executio_z431_row", "workout_executio_z419_column", "H")
ui.define_box("workout_executio_z432_filterchip", "workout_executio_z431_row", "V")
ui.define_text("workout_executio_z433_label", "workout_executio_z432_filterchip", "label")
ui.define_spacer_zone("workout_executio_z434_spacer", "workout_executio_z419_column")
ui.define_divider_zone("workout_executio_z435_divider", "workout_executio_z419_column")
ui.define_spacer_zone("workout_executio_z436_spacer", "workout_executio_z419_column")
ui.define_text("workout_executio_z437_per_side_format_", "workout_executio_z419_column", "PER SIDE — ${|.format(perSideD…")
ui.define_spacer_zone("workout_executio_z438_spacer", "workout_executio_z419_column")
ui.define_text("workout_executio_z439_target_must_exce", "workout_executio_z419_column", "Target must exceed bar weight")
ui.define_text("workout_executio_z440_cannot_make_this", "workout_executio_z419_column", "Cannot make this weight with s…")
ui.define_box("workout_executio_z441_row", "workout_executio_z419_column", "H")
ui.define_text("workout_executio_z442_row_count_row_we", "workout_executio_z441_row", "${row.count} × ${row.weight.fm…")
ui.define_text("workout_executio_z443_row_count_row_we", "workout_executio_z441_row", "(${(row.count * row.weight).fm…")
ui.define_spacer_zone("workout_executio_z444_spacer", "workout_executio_z419_column")
ui.define_text("workout_executio_z445_format_remainder", "workout_executio_z419_column", "+${|.format(remainder)} $unitL…")
ui.define_box("workout_executio_z446_topappbar", "workout_executio_z02_scaffold", "V")
ui.define_text("workout_executio_z447_workout", "workout_executio_z446_topappbar", "Workout")
ui.define_icon("workout_executio_z448_back", "workout_executio_z446_topappbar", "Back")
ui.define_icon("workout_executio_z449_plate_calculator", "workout_executio_z446_topappbar", "Plate calculator")
ui.define_button("workout_executio_z450_finish", "workout_executio_z446_topappbar", "Finish")
ui.define_box("workout_executio_z451_box", "workout_executio_z446_topappbar", "V")
ui.define_icon("workout_executio_z452_more_options", "workout_executio_z451_box", "More options")
ui.define_box("workout_executio_z453_dropdownmenu", "workout_executio_z451_box", "V")
ui.define_box("workout_executio_z454_dropdownmenuitem", "workout_executio_z453_dropdownmenu", "V")
ui.define_text("workout_executio_z455_discard_workout", "workout_executio_z454_dropdownmenuitem", "Discard workout")
ui.define_icon("workout_executio_z456_icon", "workout_executio_z454_dropdownmenuitem", "")
```

## generated tree
  - Column[z00_launchedeffect]  <leaf>
  - Column[z01_launchedeffect]  <leaf>
  - Column[z02_scaffold]  <container>
    - Column[z03_box]  <container>
      - Column[z04_circularprogress]  <leaf>
      - Text[uiState.error!!]  <leaf>
      - Column[z06_column]  <container>
        - Text[This workout has no exercises]  <leaf>
        - Spacer[z08_spacer]  <leaf>
        - Text[Its program day came back empt…]  <leaf>
        - Spacer[z10_spacer]  <leaf>
        - Button[Go back]  <leaf>
      - Column[z12_wflcompactdensit]  <container>
        - Column[z13_compositionlocal]  <leaf>
        - Column[z14_executioncontent]  <container>
          - Column[z15_swapexercisedial]  <container>
            - Column[z16_alertdialog]  <container>
              - Text[title]  <leaf>
              - Column[z18_column]  <container>
                - Column[z19_compactvaluefiel]  <container>
                  - TextField[z20_field]  <leaf>
                - Text[Results|Suggested]  <leaf>
                - Text[No matches.|No similar exercis…]  <leaf>
                - Column[z23_lazycolumn]  <container>
                  - Row[z24_row]  <container>
                    - Column[z25_column]  <container>
                      - Text[exercise.name]  <leaf>
                      - Text[ · ]  <leaf>
                    - Column[z28_favoritetoggle]  <container>
                      - Icon[Remove from favourites|Add to …]  <leaf>
                  - Divider[z30_divider]  <leaf>
              - Button[Remove it]  <leaf>
              - Button[Close]  <leaf>
          - Column[z33_addexercisedialo]  <container>
            - Column[z34_alertdialog]  <container>
              - Text[Add exercise]  <leaf>
              - Column[z36_column]  <container>
                - Column[z37_compactvaluefiel]  <container>
                  - TextField[z38_field]  <leaf>
                - Column[z39_lazycolumn]  <container>
                  - Row[z40_row]  <container>
                    - Text[exercise.name]  <leaf>
                    - Column[z42_favoritetoggle]  <container>
                      - Icon[Remove from favourites|Add to …]  <leaf>
                  - Divider[z44_divider]  <leaf>
              - Button[Close]  <leaf>
          - Column[z46_reorderexercises]  <container>
            - Column[z47_alertdialog]  <container>
              - Text[Reorder exercises]  <leaf>
              - Column[z49_lazycolumn]  <container>
                - Row[z50_row]  <container>
                  - Text[item.exercise.name]  <leaf>
                  - Icon[Move up]  <leaf>
                  - Icon[Move down]  <leaf>
              - Button[Done]  <leaf>
          - Column[z55_removeexercisedi]  <container>
            - Column[z56_alertdialog]  <container>
              - Text[Remove ${confirmItem.exercise.…]  <leaf>
              - Text[This exercise has logged sets.…]  <leaf>
              - Button[Remove]  <leaf>
              - Button[Cancel]  <leaf>
            - Column[z61_alertdialog]  <container>
              - Text[Remove exercise]  <leaf>
              - Column[z63_lazycolumn]  <container>
                - Row[z64_row]  <container>
                  - Column[z65_column]  <container>
                    - Text[item.exercise.name]  <leaf>
                    - Text[${item.completedSetsCount} set…]  <leaf>
                  - Icon[Remove ${item.exercise.name}]  <leaf>
              - Button[Close]  <leaf>
          - Column[z70_editsupersetdial]  <container>
            - Column[z71_alertdialog]  <container>
              - Text[Edit supersets]  <leaf>
              - Column[z73_column]  <container>
                - Text[Check exercises and tap Link t…]  <leaf>
                - Column[z75_lazycolumn]  <container>
                  - Row[z76_row]  <container>
                    - Column[z77_checkbox]  <leaf>
                    - Column[z78_column]  <container>
                      - Text[item.exercise.name]  <leaf>
                      - Row[z80_row]  <container>
                        - Icon[z81_icon]  <leaf>
                        - Text[ Superset $groupLabel]  <leaf>
                    - Icon[Move up]  <leaf>
                    - Icon[Move down]  <leaf>
                - Row[z85_row]  <container>
                  - Button[Unlink]  <leaf>
                  - Button[Link]  <leaf>
              - Button[Done]  <leaf>
          - Column[z89_alertdialog]  <container>
            - Text[Some set lines are empty]  <leaf>
            - Text[Do you want to update your dat…]  <leaf>
            - Button[Keep editing]  <leaf>
            - Button[Leave anyway]  <leaf>
          - Column[z94_column]  <container>
            - Column[z95_box]  <container>
              - Column[z96_animatedcontent]  <container>
                - Column[z97_box]  <leaf>
                - Column[z98_column]  <container>
                  - Column[z99_exerciseheader]  <container>
                    - Row[z100_row]  <container>
                      - Column[z101_column]  <container>
                        - Text[exercise.name]  <leaf>
                        - Row[z103_row]  <container>
                          - Text[it]  <leaf>
                          - Icon[Why this target]  <leaf>
                      - Icon[Favorite]  <leaf>
                      - Icon[Exercise info]  <leaf>
                    - Column[z108_dialog]  <container>
                      - Column[z109_surface]  <container>
                        - Column[z110_column]  <container>
                          - Text[exercise.name]  <leaf>
                          - Text[No instructions provided.]  <leaf>
                          - Button[Swap exercise]  <leaf>
                          - Button[Dismiss]  <leaf>
                    - Column[z115_dialog]  <container>
                      - Column[z116_surface]  <container>
                        - Column[z117_column]  <container>
                          - Text[exercise.name]  <leaf>
                          - Text[it]  <leaf>
                          - Text[Your coach's note for this exe…]  <leaf>
                          - Button[Dismiss]  <leaf>
                  - Spacer[z122_spacer]  <leaf>
                  - Column[z123_settable]  <container>
                    - Column[z124_mobilitysettable]  <container>
                      - Column[z125_column]  <container>
                        - Row[z126_row]  <container>
                          - Text[Hold]  <leaf>
                        - Divider[z128_divider]  <leaf>
                        - Row[z129_row]  <container>
                          - Icon[Logged]  <leaf>
                          - Spacer[z131_spacer]  <leaf>
                          - Text[${loggedHold.durationSeconds ?…]  <leaf>
                        - Spacer[z133_spacer]  <leaf>
                        - Row[z134_row]  <container>
                          - Button[−]  <leaf>
                          - Spacer[z136_spacer]  <leaf>
                          - Column[z137_column]  <container>
                            - Text[${uiState.pendingHoldSeconds}s…]  <leaf>
                            - Text[hold]  <leaf>
                          - Spacer[z140_spacer]  <leaf>
                          - Button[+]  <leaf>
                        - Spacer[z142_spacer]  <leaf>
                        - Column[z143_restbar]  <container>
                          - Column[z144_box]  <container>
                            - Column[z145_box]  <leaf>
                            - Row[z146_row]  <container>
                              - Text[REST]  <leaf>
                              - Spacer[z148_spacer]  <leaf>
                              - Text[formatRestTime(restState.remai…]  <leaf>
                              - Spacer[z150_spacer]  <leaf>
                              - Button[+30s]  <leaf>
                              - Button[Skip]  <leaf>
                        - Spacer[z153_spacer]  <leaf>
                        - Row[z154_row]  <container>
                          - Button[Restart|Start hold]  <leaf>
                          - Button[Log Set & Next]  <leaf>
                        - Spacer[z157_spacer]  <leaf>
                        - Row[z158_row]  <container>
                          - Text[${DEFAULT_HOLD_SECONDS}s$perSi…]  <leaf>
                        - Divider[z160_divider]  <leaf>
                    - Column[z161_column]  <container>
                      - Row[z162_row]  <container>
                        - Text[Set #]  <leaf>
                        - Text[rpeHeader]  <leaf>
                        - Text[Weight (${unit.label()})]  <leaf>
                        - Text[Reps]  <leaf>
                        - Text[Set type]  <leaf>
                      - Divider[z168_divider]  <leaf>
                      - Column[z169_inprogresssetrow]  <container>
                        - Column[z170_column]  <container>
                          - Row[z171_row]  <container>
                            - Text[label]  <leaf>
                            - Text[${warmupPct ?: 0}%|?]  <leaf>
                            - Text[${formatWeightField(uiState.pe…]  <leaf>
                            - Text[—]  <leaf>
                            - Column[z176_box]  <container>
                              - Text[uiState.pendingSetType.display…]  <leaf>
                              - Column[z178_dropdownmenu]  <container>
                                - Column[z179_dropdownmenuitem]  <container>
                                  - Text[type.displayName]  <leaf>
                          - Spacer[z181_spacer]  <leaf>
                          - Row[z182_row]  <container>
                            - Column[z183_column]  <container>
                              - Text[rpeLabel]  <leaf>
                              - Spacer[z185_spacer]  <leaf>
                              - Column[z186_valueadjuster]  <container>
                                - Column[z187_textfieldvalue]  <leaf>
                                - Column[z188_launchedeffect]  <container>
                                  - Column[z189_textfieldvalue]  <leaf>
                                - Column[z190_launchedeffect]  <container>
                                  - Column[z191_textrange]  <leaf>
                                - Row[z192_row]  <container>
                                  - Button[z193_iconbutton]  <leaf>
                                  - TextField[z194_field]  <leaf>
                                  - Button[z195_iconbutton]  <leaf>
                            - Column[z196_column]  <container>
                              - Text[Weight (per side)|Weight]  <leaf>
                              - Spacer[z198_spacer]  <leaf>
                              - Column[z199_valueadjuster]  <container>
                                - Column[z200_textfieldvalue]  <leaf>
                                - Column[z201_launchedeffect]  <container>
                                  - Column[z202_textfieldvalue]  <leaf>
                                - Column[z203_launchedeffect]  <container>
                                  - Column[z204_textrange]  <leaf>
                                - Row[z205_row]  <container>
                                  - Button[z206_iconbutton]  <leaf>
                                  - TextField[z207_field]  <leaf>
                                  - Button[z208_iconbutton]  <leaf>
                            - Column[z209_column]  <container>
                              - Text[Reps]  <leaf>
                              - Spacer[z211_spacer]  <leaf>
                              - Column[z212_valueadjuster]  <container>
                                - Column[z213_textfieldvalue]  <leaf>
                                - Column[z214_launchedeffect]  <container>
                                  - Column[z215_textfieldvalue]  <leaf>
                                - Column[z216_launchedeffect]  <container>
                                  - Column[z217_textrange]  <leaf>
                                - Row[z218_row]  <container>
                                  - Button[z219_iconbutton]  <leaf>
                                  - TextField[z220_field]  <leaf>
                                  - Button[z221_iconbutton]  <leaf>
                          - Spacer[z222_spacer]  <leaf>
                          - Text[EffortScale.full(currentRung, …]  <leaf>
                          - Spacer[z224_spacer]  <leaf>
                          - Column[z225_subentryrow]  <container>
                            - Row[z226_row]  <container>
                              - Text[$setNumber${'a' + entry.entryI…]  <leaf>
                              - Spacer[z228_spacer]  <leaf>
                              - Text[weightText]  <leaf>
                              - Text[—]  <leaf>
                              - Spacer[z231_spacer]  <leaf>
                          - Spacer[z232_spacer]  <leaf>
                          - Row[z233_row]  <container>
                            - Button[Log $entryWord]  <leaf>
                            - Button[Finish set]  <leaf>
                          - Button[Log set & next|Log set]  <leaf>
                      - Column[z237_warmupstaticrow]  <container>
                        - Row[z238_row]  <container>
                          - Column[z239_box]  <container>
                            - Text[label]  <leaf>
                            - Icon[Completed]  <leaf>
                          - Text[${plan.pctOfWorking}%]  <leaf>
                          - Text[loadLabel]  <leaf>
                          - Text[reps.toString()]  <leaf>
                          - Text[SetType.WARMUP.displayName]  <leaf>
                      - Divider[z246_divider]  <leaf>
                      - Column[z247_restbar]  <container>
                        - Column[z248_box]  <container>
                          - Column[z249_box]  <leaf>
                          - Row[z250_row]  <container>
                            - Text[REST]  <leaf>
                            - Spacer[z252_spacer]  <leaf>
                            - Text[formatRestTime(restState.remai…]  <leaf>
                            - Spacer[z254_spacer]  <leaf>
                            - Button[+30s]  <leaf>
                            - Button[Skip]  <leaf>
                      - Divider[z257_divider]  <leaf>
                      - Column[z258_inprogresssetrow]  <container>
                        - Column[z259_column]  <container>
                          - Row[z260_row]  <container>
                            - Text[setNumber.toString()]  <leaf>
                            - Text[${warmupPct ?: 0}%|?]  <leaf>
                            - Text[${formatWeightField(uiState.pe…]  <leaf>
                            - Text[—]  <leaf>
                            - Column[z265_box]  <container>
                              - Text[uiState.pendingSetType.display…]  <leaf>
                              - Column[z267_dropdownmenu]  <container>
                                - Column[z268_dropdownmenuitem]  <container>
                                  - Text[type.displayName]  <leaf>
                          - Spacer[z270_spacer]  <leaf>
                          - Row[z271_row]  <container>
                            - Column[z272_column]  <container>
                              - Text[rpeLabel]  <leaf>
                              - Spacer[z274_spacer]  <leaf>
                              - Column[z275_valueadjuster]  <container>
                                - Column[z276_textfieldvalue]  <leaf>
                                - Column[z277_launchedeffect]  <container>
                                  - Column[z278_textfieldvalue]  <leaf>
                                - Column[z279_launchedeffect]  <container>
                                  - Column[z280_textrange]  <leaf>
                                - Row[z281_row]  <container>
                                  - Button[z282_iconbutton]  <leaf>
                                  - TextField[z283_field]  <leaf>
                                  - Button[z284_iconbutton]  <leaf>
                            - Column[z285_column]  <container>
                              - Text[Weight (per side)|Weight]  <leaf>
                              - Spacer[z287_spacer]  <leaf>
                              - Column[z288_valueadjuster]  <container>
                                - Column[z289_textfieldvalue]  <leaf>
                                - Column[z290_launchedeffect]  <container>
                                  - Column[z291_textfieldvalue]  <leaf>
                                - Column[z292_launchedeffect]  <container>
                                  - Column[z293_textrange]  <leaf>
                                - Row[z294_row]  <container>
                                  - Button[z295_iconbutton]  <leaf>
                                  - TextField[z296_field]  <leaf>
                                  - Button[z297_iconbutton]  <leaf>
                            - Column[z298_column]  <container>
                              - Text[Reps]  <leaf>
                              - Spacer[z300_spacer]  <leaf>
                              - Column[z301_valueadjuster]  <container>
                                - Column[z302_textfieldvalue]  <leaf>
                                - Column[z303_launchedeffect]  <container>
                                  - Column[z304_textfieldvalue]  <leaf>
                                - Column[z305_launchedeffect]  <container>
                                  - Column[z306_textrange]  <leaf>
                                - Row[z307_row]  <container>
                                  - Button[z308_iconbutton]  <leaf>
                                  - TextField[z309_field]  <leaf>
                                  - Button[z310_iconbutton]  <leaf>
                          - Spacer[z311_spacer]  <leaf>
                          - Text[EffortScale.full(currentRung, …]  <leaf>
                          - Spacer[z313_spacer]  <leaf>
                          - Column[z314_subentryrow]  <container>
                            - Row[z315_row]  <container>
                              - Text[$setNumber${'a' + entry.entryI…]  <leaf>
                              - Spacer[z317_spacer]  <leaf>
                              - Text[weightText]  <leaf>
                              - Text[—]  <leaf>
                              - Spacer[z320_spacer]  <leaf>
                          - Spacer[z321_spacer]  <leaf>
                          - Row[z322_row]  <container>
                            - Button[Log $entryWord]  <leaf>
                            - Button[Finish set]  <leaf>
                          - Button[Log set & next|Log set]  <leaf>
                      - Column[z326_column]  <container>
                        - Column[z327_swipeablesetrow]  <container>
                          - Column[z328_swipetodismissbo]  <container>
                            - Column[z329_staticsetrow]  <container>
                              - Row[z330_row]  <container>
                                - Column[z331_box]  <container>
                                  - Text[setNumber.toString()]  <leaf>
                                  - Icon[Completed]  <leaf>
                                - Text[rpeText]  <leaf>
                                - Text[weightText]  <leaf>
                                - Text[—]  <leaf>
                                - Text[setType.displayName]  <leaf>
                            - Column[z338_box]  <container>
                              - Icon[Delete]  <leaf>
                        - Column[z340_subentryrow]  <container>
                          - Row[z341_row]  <container>
                            - Text[$setNumber${'a' + entry.entryI…]  <leaf>
                            - Spacer[z343_spacer]  <leaf>
                            - Text[weightText]  <leaf>
                            - Text[—]  <leaf>
                            - Spacer[z346_spacer]  <leaf>
                      - Divider[z347_divider]  <leaf>
                      - Spacer[z348_spacer]  <leaf>
                      - Button[Add set]  <leaf>
                  - Spacer[z350_spacer]  <leaf>
                  - TextField[Exercise notes]  <leaf>
            - Divider[z352_divider]  <leaf>
            - Column[z353_upnextqueue]  <container>
              - Column[z354_launchedeffect]  <leaf>
              - Column[z355_column]  <container>
                - Row[z356_row]  <container>
                  - Text[UP NEXT]  <leaf>
                  - Column[z358_upnextmenu]  <container>
                    - Column[z359_box]  <container>
                      - Icon[Manage exercises]  <leaf>
                      - Column[z361_dropdownmenu]  <container>
                        - Column[z362_dropdownmenuitem]  <container>
                          - Text[Add exercise]  <leaf>
                          - Icon[z364_icon]  <leaf>
                        - Column[z365_dropdownmenuitem]  <container>
                          - Text[Reorder exercises]  <leaf>
                          - Icon[z367_icon]  <leaf>
                        - Column[z368_dropdownmenuitem]  <container>
                          - Text[Edit superset]  <leaf>
                          - Icon[z370_icon]  <leaf>
                        - Column[z371_dropdownmenuitem]  <container>
                          - Text[Remove exercise]  <leaf>
                          - Icon[z373_icon]  <leaf>
                - Spacer[z374_spacer]  <leaf>
                - Row[z375_lazyrow]  <container>
                  - Column[z376_box]  <container>
                    - Column[z377_exercisepill]  <container>
                      - Column[z378_surface]  <container>
                        - Text[item.exercise.name]  <leaf>
                    - Icon[Supersetted with previous exer…]  <leaf>
      - Column[z381_column]  <container>
        - Column[z382_animatedvisibili]  <container>
          - Column[z383_prbanner]  <container>
            - Column[z384_wflcard]  <container>
              - Column[z385_roundedcornersha]  <leaf>
              - Column[z386_borderstroke]  <leaf>
              - Column[z387_card]  <leaf>
              - Column[z388_card]  <leaf>
              - Row[z389_row]  <container>
                - Column[z390_column]  <container>
                  - Text[NEW PERSONAL RECORD]  <leaf>
                  - Text[z392_text]  <leaf>
                - Text[tap to dismiss]  <leaf>
        - Column[z394_animatedvisibili]  <container>
          - Column[z395_midmicrocycleban]  <container>
            - Column[z396_wflcard]  <container>
              - Column[z397_roundedcornersha]  <leaf>
              - Column[z398_borderstroke]  <leaf>
              - Column[z399_card]  <leaf>
              - Column[z400_card]  <leaf>
              - Row[z401_row]  <container>
                - Text[z402_text]  <leaf>
                - Text[tap to dismiss]  <leaf>
        - Column[z404_animatedvisibili]  <container>
          - Column[z405_cardioreadinessn]  <container>
            - Column[z406_wflcard]  <container>
              - Column[z407_roundedcornersha]  <leaf>
              - Column[z408_borderstroke]  <leaf>
              - Column[z409_card]  <leaf>
              - Column[z410_card]  <leaf>
              - Text[message]  <leaf>
    - Column[z412_alertdialog]  <container>
      - Text[Discard this workout?]  <leaf>
      - Text[Everything you've logged in th…]  <leaf>
      - Button[Discard]  <leaf>
      - Button[Keep going]  <leaf>
    - Column[z417_platecalculators]  <container>
      - Column[z418_modalbottomsheet]  <container>
        - Column[z419_column]  <container>
          - Text[PLATE CALCULATOR]  <leaf>
          - Spacer[z421_spacer]  <leaf>
          - Text[TARGET WEIGHT]  <leaf>
          - Spacer[z423_spacer]  <leaf>
          - Row[z424_row]  <container>
            - Button[z425_fillediconbutton]  <leaf>
            - Text[${displayTarget.fmt()} $unitLa…]  <leaf>
            - Button[z427_fillediconbutton]  <leaf>
          - Spacer[z428_spacer]  <leaf>
          - Text[BAR]  <leaf>
          - Spacer[z430_spacer]  <leaf>
          - Row[z431_row]  <container>
            - Column[z432_filterchip]  <container>
              - Text[label]  <leaf>
          - Spacer[z434_spacer]  <leaf>
          - Divider[z435_divider]  <leaf>
          - Spacer[z436_spacer]  <leaf>
          - Text[PER SIDE — ${|.format(perSideD…]  <leaf>
          - Spacer[z438_spacer]  <leaf>
          - Text[Target must exceed bar weight]  <leaf>
          - Text[Cannot make this weight with s…]  <leaf>
          - Row[z441_row]  <container>
            - Text[${row.count} × ${row.weight.fm…]  <leaf>
            - Text[(${(row.count * row.weight).fm…]  <leaf>
          - Spacer[z444_spacer]  <leaf>
          - Text[+${|.format(remainder)} $unitL…]  <leaf>
    - Column[z446_topappbar]  <container>
      - Text[Workout]  <leaf>
      - Icon[Back]  <leaf>
      - Icon[Plate calculator]  <leaf>
      - Button[Finish]  <leaf>
      - Column[z451_box]  <container>
        - Icon[More options]  <leaf>
        - Column[z453_dropdownmenu]  <container>
          - Column[z454_dropdownmenuitem]  <container>
            - Text[Discard workout]  <leaf>
            - Icon[z456_icon]  <leaf>

---
## verify vs Compose source (WorkoutExecutionScreen)
- distinct leaf signatures matched: 63/63 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 457 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (workout_execution_screen.py)
- leaf signatures shared:        2
- generated-only (other states / not in this trace): 61
- hand-built-only (helper glyphs / human representation): 0
    GEN-only F:Exercise notes
    GEN-only I:Back
    GEN-only I:Completed
    GEN-only I:Delete
    GEN-only I:Exercise info
    GEN-only I:Favorite
    GEN-only I:Logged
    GEN-only I:Manage exercises
    GEN-only I:More options
    GEN-only I:Move down
    GEN-only I:Move up
    GEN-only I:Plate calculator
