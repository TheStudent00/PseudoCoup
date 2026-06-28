# PseudoUI generated kit screen -- onboarding  (from Compose OnboardingScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (332 calls)
```python
ui.define_box("onboarding_z00_backhandler", "content", "V")
ui.define_box("onboarding_z01_launchedeffect", "content", "V")
ui.define_box("onboarding_z02_scaffold", "content", "V")
ui.define_box("onboarding_z03_column", "onboarding_z02_scaffold", "V")
ui.define_box("onboarding_z04_linearprogressin", "onboarding_z03_column", "V")
ui.define_box("onboarding_z05_animatedcontent", "onboarding_z03_column", "V")
ui.define_box("onboarding_z06_welcomestep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z07_column", "onboarding_z06_welcomestep", "V")
ui.define_icon("onboarding_z08_icon", "onboarding_z07_column", "")
ui.define_spacer_zone("onboarding_z09_spacer", "onboarding_z07_column")
ui.define_text("onboarding_z10_workout_for_life", "onboarding_z07_column", "Workout for Life")
ui.define_spacer_zone("onboarding_z11_spacer", "onboarding_z07_column")
ui.define_text("onboarding_z12_your_workouts_yo", "onboarding_z07_column", "Your workouts. Your way. Built…")
ui.define_spacer_zone("onboarding_z13_spacer", "onboarding_z07_column")
ui.define_button("onboarding_z14_let_s_go", "onboarding_z07_column", "Let's go")
ui.define_box("onboarding_z15_namestep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z16_column", "onboarding_z15_namestep", "V")
ui.define_box("onboarding_z17_stepheading", "onboarding_z16_column", "V")
ui.define_text("onboarding_z18_what_should_we_c", "onboarding_z17_stepheading", "What should we call you?")
ui.define_spacer_zone("onboarding_z19_spacer", "onboarding_z16_column")
ui.define_text("onboarding_z20_even_just_initia", "onboarding_z16_column", "Even just initials work.")
ui.define_spacer_zone("onboarding_z21_spacer", "onboarding_z16_column")
ui.define_box("onboarding_z22_labeledfield", "onboarding_z16_column", "V")
ui.define_box("onboarding_z23_column", "onboarding_z22_labeledfield", "V")
ui.define_box("onboarding_z24_fieldlabel", "onboarding_z23_column", "V")
ui.define_text("onboarding_z25_your_name", "onboarding_z24_fieldlabel", "Your name")
ui.define_box("onboarding_z26_compactvaluefiel", "onboarding_z22_labeledfield", "V")
ui.define_input_zone("onboarding_z27_field", "onboarding_z26_compactvaluefiel", "", "")
ui.define_spacer_zone("onboarding_z28_spacer", "onboarding_z16_column")
ui.define_button("onboarding_z29_continue", "onboarding_z16_column", "Continue")
ui.define_box("onboarding_z30_experiencestep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z31_column", "onboarding_z30_experiencestep", "V")
ui.define_spacer_zone("onboarding_z32_spacer", "onboarding_z31_column")
ui.define_box("onboarding_z33_stepheading", "onboarding_z31_column", "V")
ui.define_text("onboarding_z34_how_long_have_yo", "onboarding_z33_stepheading", "How long have you been trainin…")
ui.define_spacer_zone("onboarding_z35_spacer", "onboarding_z31_column")
ui.define_text("onboarding_z36_this_helps_tune_", "onboarding_z31_column", "This helps tune your progressi…")
ui.define_spacer_zone("onboarding_z37_spacer", "onboarding_z31_column")
ui.define_box("onboarding_z38_selectioncard", "onboarding_z31_column", "V")
ui.define_box("onboarding_z39_wflcard", "onboarding_z38_selectioncard", "V")
ui.define_box("onboarding_z40_roundedcornersha", "onboarding_z39_wflcard", "V")
ui.define_box("onboarding_z41_borderstroke", "onboarding_z39_wflcard", "V")
ui.define_box("onboarding_z42_card", "onboarding_z39_wflcard", "V")
ui.define_box("onboarding_z43_card", "onboarding_z39_wflcard", "V")
ui.define_box("onboarding_z44_row", "onboarding_z39_wflcard", "H")
ui.define_text("onboarding_z45_opt_emoji", "onboarding_z44_row", "opt.emoji")
ui.define_spacer_zone("onboarding_z46_spacer", "onboarding_z44_row")
ui.define_box("onboarding_z47_column", "onboarding_z44_row", "V")
ui.define_text("onboarding_z48_opt_title", "onboarding_z47_column", "opt.title")
ui.define_text("onboarding_z49_opt_subtitle", "onboarding_z47_column", "opt.subtitle")
ui.define_spacer_zone("onboarding_z50_spacer", "onboarding_z31_column")
ui.define_spacer_zone("onboarding_z51_spacer", "onboarding_z31_column")
ui.define_button("onboarding_z52_i_ll_set_this_la", "onboarding_z31_column", "I'll set this later")
ui.define_spacer_zone("onboarding_z53_spacer", "onboarding_z31_column")
ui.define_box("onboarding_z54_trainingstatusst", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z55_column", "onboarding_z54_trainingstatusst", "V")
ui.define_spacer_zone("onboarding_z56_spacer", "onboarding_z55_column")
ui.define_box("onboarding_z57_stepheading", "onboarding_z55_column", "V")
ui.define_text("onboarding_z58_are_you_training", "onboarding_z57_stepheading", "Are you training right now?")
ui.define_spacer_zone("onboarding_z59_spacer", "onboarding_z55_column")
ui.define_text("onboarding_z60_if_you_ve_been_a", "onboarding_z55_column", "If you've been away for a whil…")
ui.define_spacer_zone("onboarding_z61_spacer", "onboarding_z55_column")
ui.define_box("onboarding_z62_selectioncard", "onboarding_z55_column", "V")
ui.define_box("onboarding_z63_wflcard", "onboarding_z62_selectioncard", "V")
ui.define_box("onboarding_z64_roundedcornersha", "onboarding_z63_wflcard", "V")
ui.define_box("onboarding_z65_borderstroke", "onboarding_z63_wflcard", "V")
ui.define_box("onboarding_z66_card", "onboarding_z63_wflcard", "V")
ui.define_box("onboarding_z67_card", "onboarding_z63_wflcard", "V")
ui.define_box("onboarding_z68_row", "onboarding_z63_wflcard", "H")
ui.define_text("onboarding_z69_opt_emoji", "onboarding_z68_row", "opt.emoji")
ui.define_spacer_zone("onboarding_z70_spacer", "onboarding_z68_row")
ui.define_box("onboarding_z71_column", "onboarding_z68_row", "V")
ui.define_text("onboarding_z72_opt_title", "onboarding_z71_column", "opt.title")
ui.define_text("onboarding_z73_opt_subtitle", "onboarding_z71_column", "opt.subtitle")
ui.define_spacer_zone("onboarding_z74_spacer", "onboarding_z55_column")
ui.define_spacer_zone("onboarding_z75_spacer", "onboarding_z55_column")
ui.define_button("onboarding_z76_i_ll_set_this_la", "onboarding_z55_column", "I'll set this later")
ui.define_spacer_zone("onboarding_z77_spacer", "onboarding_z55_column")
ui.define_box("onboarding_z78_weightunitstep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z79_column", "onboarding_z78_weightunitstep", "V")
ui.define_box("onboarding_z80_stepheading", "onboarding_z79_column", "V")
ui.define_text("onboarding_z81_how_do_you_measu", "onboarding_z80_stepheading", "How do you measure your weight…")
ui.define_spacer_zone("onboarding_z82_spacer", "onboarding_z79_column")
ui.define_text("onboarding_z83_used_across_the_", "onboarding_z79_column", "Used across the whole app and …")
ui.define_spacer_zone("onboarding_z84_spacer", "onboarding_z79_column")
ui.define_box("onboarding_z85_row", "onboarding_z79_column", "H")
ui.define_box("onboarding_z86_selectioncard", "onboarding_z85_row", "V")
ui.define_box("onboarding_z87_wflcard", "onboarding_z86_selectioncard", "V")
ui.define_box("onboarding_z88_roundedcornersha", "onboarding_z87_wflcard", "V")
ui.define_box("onboarding_z89_borderstroke", "onboarding_z87_wflcard", "V")
ui.define_box("onboarding_z90_card", "onboarding_z87_wflcard", "V")
ui.define_box("onboarding_z91_card", "onboarding_z87_wflcard", "V")
ui.define_box("onboarding_z92_row", "onboarding_z87_wflcard", "H")
ui.define_text("onboarding_z93_x", "onboarding_z92_row", "⚖️")
ui.define_spacer_zone("onboarding_z94_spacer", "onboarding_z92_row")
ui.define_box("onboarding_z95_column", "onboarding_z92_row", "V")
ui.define_text("onboarding_z96_unit_name", "onboarding_z95_column", "unit.name")
ui.define_text("onboarding_z97_n", "onboarding_z95_column", "\n|(|)")
ui.define_box("onboarding_z98_startingstrength", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z99_column", "onboarding_z98_startingstrength", "V")
ui.define_spacer_zone("onboarding_z100_spacer", "onboarding_z99_column")
ui.define_box("onboarding_z101_stepheading", "onboarding_z99_column", "V")
ui.define_text("onboarding_z102_a_bit_about_your", "onboarding_z101_stepheading", "A bit about your body")
ui.define_spacer_zone("onboarding_z103_spacer", "onboarding_z99_column")
ui.define_text("onboarding_z104_this_just_sets_y", "onboarding_z99_column", "This just sets your very first…")
ui.define_spacer_zone("onboarding_z105_spacer", "onboarding_z99_column")
ui.define_box("onboarding_z106_labeledfield", "onboarding_z99_column", "V")
ui.define_box("onboarding_z107_column", "onboarding_z106_labeledfield", "V")
ui.define_box("onboarding_z108_fieldlabel", "onboarding_z107_column", "V")
ui.define_text("onboarding_z109_bodyweight_weigh", "onboarding_z108_fieldlabel", "Bodyweight (${weightUnit.name.…")
ui.define_box("onboarding_z110_compactvaluefiel", "onboarding_z106_labeledfield", "V")
ui.define_input_zone("onboarding_z111_field", "onboarding_z110_compactvaluefiel", "", "")
ui.define_text("onboarding_z112_optional_helps_s", "onboarding_z106_labeledfield", "Optional — helps size your fir…")
ui.define_spacer_zone("onboarding_z113_spacer", "onboarding_z99_column")
ui.define_text("onboarding_z114_which_sounds_mor", "onboarding_z99_column", "Which sounds more like your bo…")
ui.define_spacer_zone("onboarding_z115_spacer", "onboarding_z99_column")
ui.define_box("onboarding_z116_selectioncard", "onboarding_z99_column", "V")
ui.define_box("onboarding_z117_wflcard", "onboarding_z116_selectioncard", "V")
ui.define_box("onboarding_z118_roundedcornersha", "onboarding_z117_wflcard", "V")
ui.define_box("onboarding_z119_borderstroke", "onboarding_z117_wflcard", "V")
ui.define_box("onboarding_z120_card", "onboarding_z117_wflcard", "V")
ui.define_box("onboarding_z121_card", "onboarding_z117_wflcard", "V")
ui.define_box("onboarding_z122_row", "onboarding_z117_wflcard", "H")
ui.define_text("onboarding_z123_opt_emoji", "onboarding_z122_row", "opt.emoji")
ui.define_spacer_zone("onboarding_z124_spacer", "onboarding_z122_row")
ui.define_box("onboarding_z125_column", "onboarding_z122_row", "V")
ui.define_text("onboarding_z126_opt_title", "onboarding_z125_column", "opt.title")
ui.define_text("onboarding_z127_opt_subtitle", "onboarding_z125_column", "opt.subtitle")
ui.define_spacer_zone("onboarding_z128_spacer", "onboarding_z99_column")
ui.define_text("onboarding_z129_not_sure_leave_i", "onboarding_z99_column", "Not sure? Leave it — we'll sta…")
ui.define_spacer_zone("onboarding_z130_spacer", "onboarding_z99_column")
ui.define_button("onboarding_z131_continue", "onboarding_z99_column", "Continue")
ui.define_button("onboarding_z132_skip_for_now", "onboarding_z99_column", "Skip for now")
ui.define_spacer_zone("onboarding_z133_spacer", "onboarding_z99_column")
ui.define_box("onboarding_z134_calibrationstep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z135_column", "onboarding_z134_calibrationstep", "V")
ui.define_spacer_zone("onboarding_z136_spacer", "onboarding_z135_column")
ui.define_box("onboarding_z137_stepheading", "onboarding_z135_column", "V")
ui.define_text("onboarding_z138_you_re_calibrate", "onboarding_z137_stepheading", "You're calibrated")
ui.define_spacer_zone("onboarding_z139_spacer", "onboarding_z135_column")
ui.define_text("onboarding_z140_your_starting_we", "onboarding_z135_column", "Your starting weights come fro…")
ui.define_spacer_zone("onboarding_z141_spacer", "onboarding_z135_column")
ui.define_box("onboarding_z142_calibrationoutco", "onboarding_z135_column", "V")
ui.define_box("onboarding_z143_wflcard", "onboarding_z142_calibrationoutco", "V")
ui.define_box("onboarding_z144_roundedcornersha", "onboarding_z143_wflcard", "V")
ui.define_box("onboarding_z145_borderstroke", "onboarding_z143_wflcard", "V")
ui.define_box("onboarding_z146_card", "onboarding_z143_wflcard", "V")
ui.define_box("onboarding_z147_card", "onboarding_z143_wflcard", "V")
ui.define_box("onboarding_z148_column", "onboarding_z143_wflcard", "V")
ui.define_text("onboarding_z149_outcome_label", "onboarding_z148_column", "outcome.label")
ui.define_text("onboarding_z150_confidencelabel_", "onboarding_z148_column", "confidenceLabel(outcome.confid…")
ui.define_spacer_zone("onboarding_z151_spacer", "onboarding_z135_column")
ui.define_spacer_zone("onboarding_z152_spacer", "onboarding_z135_column")
ui.define_button("onboarding_z153_continue", "onboarding_z135_column", "Continue")
ui.define_spacer_zone("onboarding_z154_spacer", "onboarding_z135_column")
ui.define_box("onboarding_z155_stepheading", "onboarding_z135_column", "V")
ui.define_text("onboarding_z156_find_your_starti", "onboarding_z155_stepheading", "Find your starting weights")
ui.define_spacer_zone("onboarding_z157_spacer", "onboarding_z135_column")
ui.define_text("onboarding_z158_no_max_out_testi", "onboarding_z135_column", "No max-out testing, ever — it'…")
ui.define_spacer_zone("onboarding_z159_spacer", "onboarding_z135_column")
ui.define_box("onboarding_z160_selectioncard", "onboarding_z135_column", "V")
ui.define_box("onboarding_z161_wflcard", "onboarding_z160_selectioncard", "V")
ui.define_box("onboarding_z162_roundedcornersha", "onboarding_z161_wflcard", "V")
ui.define_box("onboarding_z163_borderstroke", "onboarding_z161_wflcard", "V")
ui.define_box("onboarding_z164_card", "onboarding_z161_wflcard", "V")
ui.define_box("onboarding_z165_card", "onboarding_z161_wflcard", "V")
ui.define_box("onboarding_z166_row", "onboarding_z161_wflcard", "H")
ui.define_text("onboarding_z167_x", "onboarding_z166_row", "⌨️")
ui.define_spacer_zone("onboarding_z168_spacer", "onboarding_z166_row")
ui.define_box("onboarding_z169_column", "onboarding_z166_row", "V")
ui.define_text("onboarding_z170_enter_your_numbe", "onboarding_z169_column", "Enter your numbers")
ui.define_text("onboarding_z171_type_a_recent_wo", "onboarding_z169_column", "Type a recent working weight f…")
ui.define_spacer_zone("onboarding_z172_spacer", "onboarding_z135_column")
ui.define_box("onboarding_z173_selectioncard", "onboarding_z135_column", "V")
ui.define_box("onboarding_z174_wflcard", "onboarding_z173_selectioncard", "V")
ui.define_box("onboarding_z175_roundedcornersha", "onboarding_z174_wflcard", "V")
ui.define_box("onboarding_z176_borderstroke", "onboarding_z174_wflcard", "V")
ui.define_box("onboarding_z177_card", "onboarding_z174_wflcard", "V")
ui.define_box("onboarding_z178_card", "onboarding_z174_wflcard", "V")
ui.define_box("onboarding_z179_row", "onboarding_z174_wflcard", "H")
ui.define_text("onboarding_z180_x", "onboarding_z179_row", "🏋️")
ui.define_spacer_zone("onboarding_z181_spacer", "onboarding_z179_row")
ui.define_box("onboarding_z182_column", "onboarding_z179_row", "V")
ui.define_text("onboarding_z183_calibrate_with_u", "onboarding_z182_column", "Calibrate with us")
ui.define_text("onboarding_z184_work_up_to_a_tou", "onboarding_z182_column", "Work up to a tough set of a fe…")
ui.define_spacer_zone("onboarding_z185_spacer", "onboarding_z135_column")
ui.define_button("onboarding_z186_skip_just_start_", "onboarding_z135_column", "Skip — just start me light")
ui.define_spacer_zone("onboarding_z187_spacer", "onboarding_z135_column")
ui.define_box("onboarding_z188_stepheading", "onboarding_z135_column", "V")
ui.define_text("onboarding_z189_enter_your_numbe", "onboarding_z188_stepheading", "Enter your numbers|Calibrate w…")
ui.define_spacer_zone("onboarding_z190_spacer", "onboarding_z135_column")
ui.define_text("onboarding_z191_calibrationformh", "onboarding_z135_column", "calibrationFormHint(effectiveM…")
ui.define_spacer_zone("onboarding_z192_spacer", "onboarding_z135_column")
ui.define_box("onboarding_z193_labeledfield", "onboarding_z135_column", "V")
ui.define_box("onboarding_z194_column", "onboarding_z193_labeledfield", "V")
ui.define_box("onboarding_z195_fieldlabel", "onboarding_z194_column", "V")
ui.define_text("onboarding_z196_lift_label_weigh", "onboarding_z195_fieldlabel", "${lift.label} (${weightUnit.na…")
ui.define_box("onboarding_z197_compactvaluefiel", "onboarding_z193_labeledfield", "V")
ui.define_input_zone("onboarding_z198_field", "onboarding_z197_compactvaluefiel", "", "")
ui.define_spacer_zone("onboarding_z199_spacer", "onboarding_z135_column")
ui.define_text("onboarding_z200_enter_what_you_c", "onboarding_z135_column", "Enter what you can — leave any…")
ui.define_spacer_zone("onboarding_z201_spacer", "onboarding_z135_column")
ui.define_button("onboarding_z202_saving_save_my_n", "onboarding_z135_column", "Saving…|Save my numbers")
ui.define_button("onboarding_z203_back_to_options", "onboarding_z135_column", "Back to options")
ui.define_button("onboarding_z204_skip_for_now", "onboarding_z135_column", "Skip for now")
ui.define_spacer_zone("onboarding_z205_spacer", "onboarding_z135_column")
ui.define_box("onboarding_z206_gymtypestep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z207_column", "onboarding_z206_gymtypestep", "V")
ui.define_spacer_zone("onboarding_z208_spacer", "onboarding_z207_column")
ui.define_text("onboarding_z209_tell_us_about_yo", "onboarding_z207_column", "Tell us about your gym")
ui.define_spacer_zone("onboarding_z210_spacer", "onboarding_z207_column")
ui.define_text("onboarding_z211_we_ll_pre_load_t", "onboarding_z207_column", "We'll pre-load the most common…")
ui.define_spacer_zone("onboarding_z212_spacer", "onboarding_z207_column")
ui.define_box("onboarding_z213_labeledfield", "onboarding_z207_column", "V")
ui.define_box("onboarding_z214_column", "onboarding_z213_labeledfield", "V")
ui.define_box("onboarding_z215_fieldlabel", "onboarding_z214_column", "V")
ui.define_text("onboarding_z216_gym_name", "onboarding_z215_fieldlabel", "Gym name")
ui.define_box("onboarding_z217_compactvaluefiel", "onboarding_z213_labeledfield", "V")
ui.define_input_zone("onboarding_z218_field", "onboarding_z217_compactvaluefiel", "", "")
ui.define_spacer_zone("onboarding_z219_spacer", "onboarding_z207_column")
ui.define_box("onboarding_z220_selectioncard", "onboarding_z207_column", "V")
ui.define_box("onboarding_z221_wflcard", "onboarding_z220_selectioncard", "V")
ui.define_box("onboarding_z222_roundedcornersha", "onboarding_z221_wflcard", "V")
ui.define_box("onboarding_z223_borderstroke", "onboarding_z221_wflcard", "V")
ui.define_box("onboarding_z224_card", "onboarding_z221_wflcard", "V")
ui.define_box("onboarding_z225_card", "onboarding_z221_wflcard", "V")
ui.define_box("onboarding_z226_row", "onboarding_z221_wflcard", "H")
ui.define_text("onboarding_z227_type_emoji", "onboarding_z226_row", "type.emoji")
ui.define_spacer_zone("onboarding_z228_spacer", "onboarding_z226_row")
ui.define_box("onboarding_z229_column", "onboarding_z226_row", "V")
ui.define_text("onboarding_z230_type_displayname", "onboarding_z229_column", "type.displayName")
ui.define_text("onboarding_z231_type_description", "onboarding_z229_column", "type.description")
ui.define_spacer_zone("onboarding_z232_spacer", "onboarding_z207_column")
ui.define_spacer_zone("onboarding_z233_spacer", "onboarding_z207_column")
ui.define_box("onboarding_z234_equipmentstep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z235_column", "onboarding_z234_equipmentstep", "V")
ui.define_box("onboarding_z236_column", "onboarding_z235_column", "V")
ui.define_spacer_zone("onboarding_z237_spacer", "onboarding_z236_column")
ui.define_text("onboarding_z238_what_does_gymtyp", "onboarding_z236_column", "What does ${gymType.displayNam…")
ui.define_text("onboarding_z239_suggested_equipm", "onboarding_z236_column", "Suggested equipment is pre-che…")
ui.define_spacer_zone("onboarding_z240_spacer", "onboarding_z236_column")
ui.define_box("onboarding_z241_labeledfield", "onboarding_z236_column", "V")
ui.define_box("onboarding_z242_column", "onboarding_z241_labeledfield", "V")
ui.define_box("onboarding_z243_fieldlabel", "onboarding_z242_column", "V")
ui.define_text("onboarding_z244_search_all_equip", "onboarding_z243_fieldlabel", "Search all equipment")
ui.define_box("onboarding_z245_compactvaluefiel", "onboarding_z241_labeledfield", "V")
ui.define_input_zone("onboarding_z246_field", "onboarding_z245_compactvaluefiel", "", "")
ui.define_spacer_zone("onboarding_z247_spacer", "onboarding_z236_column")
ui.define_box("onboarding_z248_lazycolumn", "onboarding_z235_column", "V")
ui.define_box("onboarding_z249_filterchip", "onboarding_z248_lazycolumn", "V")
ui.define_box("onboarding_z250_column", "onboarding_z249_filterchip", "V")
ui.define_text("onboarding_z251_item_label", "onboarding_z250_column", "item.label")
ui.define_text("onboarding_z252_always_included", "onboarding_z250_column", "Always included")
ui.define_spacer_zone("onboarding_z253_spacer", "onboarding_z248_lazycolumn")
ui.define_box("onboarding_z254_column", "onboarding_z248_lazycolumn", "V")
ui.define_text("onboarding_z255_selected_size_it", "onboarding_z254_column", "${selected.size} item${if (sel…")
ui.define_spacer_zone("onboarding_z256_spacer", "onboarding_z254_column")
ui.define_box("onboarding_z257_column", "onboarding_z235_column", "V")
ui.define_button("onboarding_z258_saving_done_sele", "onboarding_z257_column", "Saving...|Done selecting")
ui.define_box("onboarding_z259_learntolistenpro", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z260_column", "onboarding_z259_learntolistenpro", "V")
ui.define_icon("onboarding_z261_icon", "onboarding_z260_column", "")
ui.define_spacer_zone("onboarding_z262_spacer", "onboarding_z260_column")
ui.define_text("onboarding_z263_strongly_recomme", "onboarding_z260_column", "Strongly Recommended:\nLearn t…")
ui.define_spacer_zone("onboarding_z264_spacer", "onboarding_z260_column")
ui.define_text("onboarding_z265_since_you_re_sta", "onboarding_z260_column", "Since you're starting out, we …")
ui.define_spacer_zone("onboarding_z266_spacer", "onboarding_z260_column")
ui.define_button("onboarding_z267_join_learn_to_li", "onboarding_z260_column", "Join 'Learn to Listen' (Recomm…")
ui.define_spacer_zone("onboarding_z268_spacer", "onboarding_z260_column")
ui.define_button("onboarding_z269_i_ll_choose_my_o", "onboarding_z260_column", "I'll choose my own path")
ui.define_box("onboarding_z270_pathselectionste", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z271_column", "onboarding_z270_pathselectionste", "V")
ui.define_box("onboarding_z272_column", "onboarding_z271_column", "V")
ui.define_spacer_zone("onboarding_z273_spacer", "onboarding_z272_column")
ui.define_box("onboarding_z274_stepheading", "onboarding_z272_column", "V")
ui.define_text("onboarding_z275_choose_your_firs", "onboarding_z274_stepheading", "Choose your first path")
ui.define_text("onboarding_z276_your_path_sets_t", "onboarding_z272_column", "Your path sets the intention f…")
ui.define_spacer_zone("onboarding_z277_spacer", "onboarding_z272_column")
ui.define_box("onboarding_z278_lazycolumn", "onboarding_z271_column", "V")
ui.define_box("onboarding_z279_pathcard", "onboarding_z278_lazycolumn", "V")
ui.define_box("onboarding_z280_wflcard", "onboarding_z279_pathcard", "V")
ui.define_box("onboarding_z281_roundedcornersha", "onboarding_z280_wflcard", "V")
ui.define_box("onboarding_z282_borderstroke", "onboarding_z280_wflcard", "V")
ui.define_box("onboarding_z283_card", "onboarding_z280_wflcard", "V")
ui.define_box("onboarding_z284_card", "onboarding_z280_wflcard", "V")
ui.define_box("onboarding_z285_row", "onboarding_z280_wflcard", "H")
ui.define_box("onboarding_z286_column", "onboarding_z285_row", "V")
ui.define_text("onboarding_z287_definition_name", "onboarding_z286_column", "definition.name")
ui.define_spacer_zone("onboarding_z288_spacer", "onboarding_z286_column")
ui.define_text("onboarding_z289_definition_tagli", "onboarding_z286_column", "definition.tagline")
ui.define_spacer_zone("onboarding_z290_spacer", "onboarding_z286_column")
ui.define_text("onboarding_z291_definition_minse", "onboarding_z286_column", "${definition.minSessionsPerWee…")
ui.define_spacer_zone("onboarding_z292_spacer", "onboarding_z285_row")
ui.define_box("onboarding_z293_surface", "onboarding_z285_row", "V")
ui.define_box("onboarding_z294_box", "onboarding_z293_surface", "V")
ui.define_icon("onboarding_z295_icon", "onboarding_z294_box", "")
ui.define_spacer_zone("onboarding_z296_spacer", "onboarding_z278_lazycolumn")
ui.define_box("onboarding_z297_column", "onboarding_z271_column", "V")
ui.define_button("onboarding_z298_continue", "onboarding_z297_column", "Continue →")
ui.define_box("onboarding_z299_programselection", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z300_column", "onboarding_z299_programselection", "V")
ui.define_box("onboarding_z301_column", "onboarding_z300_column", "V")
ui.define_spacer_zone("onboarding_z302_spacer", "onboarding_z301_column")
ui.define_box("onboarding_z303_stepheading", "onboarding_z301_column", "V")
ui.define_text("onboarding_z304_pick_your_starti", "onboarding_z303_stepheading", "Pick your starting program")
ui.define_text("onboarding_z305_programs_for_you", "onboarding_z301_column", "Programs for your chosen path.…")
ui.define_spacer_zone("onboarding_z306_spacer", "onboarding_z301_column")
ui.define_box("onboarding_z307_box", "onboarding_z300_column", "V")
ui.define_box("onboarding_z308_circularprogress", "onboarding_z307_box", "V")
ui.define_box("onboarding_z309_lazycolumn", "onboarding_z300_column", "V")
ui.define_box("onboarding_z310_onboardingprogra", "onboarding_z309_lazycolumn", "V")
ui.define_box("onboarding_z311_wflcard", "onboarding_z310_onboardingprogra", "V")
ui.define_box("onboarding_z312_roundedcornersha", "onboarding_z311_wflcard", "V")
ui.define_box("onboarding_z313_borderstroke", "onboarding_z311_wflcard", "V")
ui.define_box("onboarding_z314_card", "onboarding_z311_wflcard", "V")
ui.define_box("onboarding_z315_card", "onboarding_z311_wflcard", "V")
ui.define_box("onboarding_z316_column", "onboarding_z311_wflcard", "V")
ui.define_box("onboarding_z317_row", "onboarding_z316_column", "H")
ui.define_text("onboarding_z318_program_name", "onboarding_z317_row", "program.name")
ui.define_icon("onboarding_z319_selected", "onboarding_z317_row", "Selected")
ui.define_spacer_zone("onboarding_z320_spacer", "onboarding_z316_column")
ui.define_text("onboarding_z321_desc", "onboarding_z316_column", "desc")
ui.define_spacer_zone("onboarding_z322_spacer", "onboarding_z316_column")
ui.define_text("onboarding_z323_program_totalwee", "onboarding_z316_column", "${program.totalWeeks} week${if…")
ui.define_spacer_zone("onboarding_z324_spacer", "onboarding_z309_lazycolumn")
ui.define_box("onboarding_z325_column", "onboarding_z300_column", "V")
ui.define_button("onboarding_z326_let_s_go", "onboarding_z325_column", "Let's go →")
ui.define_spacer_zone("onboarding_z327_spacer", "onboarding_z325_column")
ui.define_button("onboarding_z328_skip_for_now_i_l", "onboarding_z325_column", "Skip for now — I'll choose lat…")
ui.define_box("onboarding_z329_box", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z330_topappbar", "onboarding_z02_scaffold", "V")
ui.define_icon("onboarding_z331_back", "onboarding_z330_topappbar", "Back")
```

## generated tree
  - Column[backhandler]  <leaf>
  - Column[launchedeffect]  <leaf>
  - Column[scaffold]  <container>
    - Column[column]  <container>
      - Column[linearprogressin]  <leaf>
      - Column[animatedcontent]  <container>
        - Column[welcomestep]  <container>
          - Column[column]  <container>
            - Icon[icon]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[Workout for Life]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[Your workouts. Your way. Built…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[Let's go]  <leaf>
        - Column[namestep]  <container>
          - Column[column]  <container>
            - Column[stepheading]  <container>
              - Text[What should we call you?]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[Even just initials work.]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[labeledfield]  <container>
              - Column[column]  <container>
                - Column[fieldlabel]  <container>
                  - Text[Your name]  <leaf>
              - Column[compactvaluefiel]  <container>
                - TextField[field]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[Continue]  <leaf>
        - Column[experiencestep]  <container>
          - Column[column]  <container>
            - Spacer[spacer]  <leaf>
            - Column[stepheading]  <container>
              - Text[How long have you been trainin…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[This helps tune your progressi…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[selectioncard]  <container>
              - Column[wflcard]  <container>
                - Column[roundedcornersha]  <leaf>
                - Column[borderstroke]  <leaf>
                - Column[card]  <leaf>
                - Column[card]  <leaf>
                - Row[row]  <container>
                  - Text[opt.emoji]  <leaf>
                  - Spacer[spacer]  <leaf>
                  - Column[column]  <container>
                    - Text[opt.title]  <leaf>
                    - Text[opt.subtitle]  <leaf>
            - Spacer[spacer]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[I'll set this later]  <leaf>
            - Spacer[spacer]  <leaf>
        - Column[trainingstatusst]  <container>
          - Column[column]  <container>
            - Spacer[spacer]  <leaf>
            - Column[stepheading]  <container>
              - Text[Are you training right now?]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[If you've been away for a whil…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[selectioncard]  <container>
              - Column[wflcard]  <container>
                - Column[roundedcornersha]  <leaf>
                - Column[borderstroke]  <leaf>
                - Column[card]  <leaf>
                - Column[card]  <leaf>
                - Row[row]  <container>
                  - Text[opt.emoji]  <leaf>
                  - Spacer[spacer]  <leaf>
                  - Column[column]  <container>
                    - Text[opt.title]  <leaf>
                    - Text[opt.subtitle]  <leaf>
            - Spacer[spacer]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[I'll set this later]  <leaf>
            - Spacer[spacer]  <leaf>
        - Column[weightunitstep]  <container>
          - Column[column]  <container>
            - Column[stepheading]  <container>
              - Text[How do you measure your weight…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[Used across the whole app and …]  <leaf>
            - Spacer[spacer]  <leaf>
            - Row[row]  <container>
              - Column[selectioncard]  <container>
                - Column[wflcard]  <container>
                  - Column[roundedcornersha]  <leaf>
                  - Column[borderstroke]  <leaf>
                  - Column[card]  <leaf>
                  - Column[card]  <leaf>
                  - Row[row]  <container>
                    - Text[⚖️]  <leaf>
                    - Spacer[spacer]  <leaf>
                    - Column[column]  <container>
                      - Text[unit.name]  <leaf>
                      - Text[\n|(|)]  <leaf>
        - Column[startingstrength]  <container>
          - Column[column]  <container>
            - Spacer[spacer]  <leaf>
            - Column[stepheading]  <container>
              - Text[A bit about your body]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[This just sets your very first…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[labeledfield]  <container>
              - Column[column]  <container>
                - Column[fieldlabel]  <container>
                  - Text[Bodyweight (${weightUnit.name.…]  <leaf>
              - Column[compactvaluefiel]  <container>
                - TextField[field]  <leaf>
              - Text[Optional — helps size your fir…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[Which sounds more like your bo…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[selectioncard]  <container>
              - Column[wflcard]  <container>
                - Column[roundedcornersha]  <leaf>
                - Column[borderstroke]  <leaf>
                - Column[card]  <leaf>
                - Column[card]  <leaf>
                - Row[row]  <container>
                  - Text[opt.emoji]  <leaf>
                  - Spacer[spacer]  <leaf>
                  - Column[column]  <container>
                    - Text[opt.title]  <leaf>
                    - Text[opt.subtitle]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[Not sure? Leave it — we'll sta…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[Continue]  <leaf>
            - Button[Skip for now]  <leaf>
            - Spacer[spacer]  <leaf>
        - Column[calibrationstep]  <container>
          - Column[column]  <container>
            - Spacer[spacer]  <leaf>
            - Column[stepheading]  <container>
              - Text[You're calibrated]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[Your starting weights come fro…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[calibrationoutco]  <container>
              - Column[wflcard]  <container>
                - Column[roundedcornersha]  <leaf>
                - Column[borderstroke]  <leaf>
                - Column[card]  <leaf>
                - Column[card]  <leaf>
                - Column[column]  <container>
                  - Text[outcome.label]  <leaf>
                  - Text[confidenceLabel(outcome.confid…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[Continue]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[stepheading]  <container>
              - Text[Find your starting weights]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[No max-out testing, ever — it'…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[selectioncard]  <container>
              - Column[wflcard]  <container>
                - Column[roundedcornersha]  <leaf>
                - Column[borderstroke]  <leaf>
                - Column[card]  <leaf>
                - Column[card]  <leaf>
                - Row[row]  <container>
                  - Text[⌨️]  <leaf>
                  - Spacer[spacer]  <leaf>
                  - Column[column]  <container>
                    - Text[Enter your numbers]  <leaf>
                    - Text[Type a recent working weight f…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[selectioncard]  <container>
              - Column[wflcard]  <container>
                - Column[roundedcornersha]  <leaf>
                - Column[borderstroke]  <leaf>
                - Column[card]  <leaf>
                - Column[card]  <leaf>
                - Row[row]  <container>
                  - Text[🏋️]  <leaf>
                  - Spacer[spacer]  <leaf>
                  - Column[column]  <container>
                    - Text[Calibrate with us]  <leaf>
                    - Text[Work up to a tough set of a fe…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[Skip — just start me light]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[stepheading]  <container>
              - Text[Enter your numbers|Calibrate w…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[calibrationFormHint(effectiveM…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[labeledfield]  <container>
              - Column[column]  <container>
                - Column[fieldlabel]  <container>
                  - Text[${lift.label} (${weightUnit.na…]  <leaf>
              - Column[compactvaluefiel]  <container>
                - TextField[field]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[Enter what you can — leave any…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[Saving…|Save my numbers]  <leaf>
            - Button[Back to options]  <leaf>
            - Button[Skip for now]  <leaf>
            - Spacer[spacer]  <leaf>
        - Column[gymtypestep]  <container>
          - Column[column]  <container>
            - Spacer[spacer]  <leaf>
            - Text[Tell us about your gym]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[We'll pre-load the most common…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[labeledfield]  <container>
              - Column[column]  <container>
                - Column[fieldlabel]  <container>
                  - Text[Gym name]  <leaf>
              - Column[compactvaluefiel]  <container>
                - TextField[field]  <leaf>
            - Spacer[spacer]  <leaf>
            - Column[selectioncard]  <container>
              - Column[wflcard]  <container>
                - Column[roundedcornersha]  <leaf>
                - Column[borderstroke]  <leaf>
                - Column[card]  <leaf>
                - Column[card]  <leaf>
                - Row[row]  <container>
                  - Text[type.emoji]  <leaf>
                  - Spacer[spacer]  <leaf>
                  - Column[column]  <container>
                    - Text[type.displayName]  <leaf>
                    - Text[type.description]  <leaf>
            - Spacer[spacer]  <leaf>
            - Spacer[spacer]  <leaf>
        - Column[equipmentstep]  <container>
          - Column[column]  <container>
            - Column[column]  <container>
              - Spacer[spacer]  <leaf>
              - Text[What does ${gymType.displayNam…]  <leaf>
              - Text[Suggested equipment is pre-che…]  <leaf>
              - Spacer[spacer]  <leaf>
              - Column[labeledfield]  <container>
                - Column[column]  <container>
                  - Column[fieldlabel]  <container>
                    - Text[Search all equipment]  <leaf>
                - Column[compactvaluefiel]  <container>
                  - TextField[field]  <leaf>
              - Spacer[spacer]  <leaf>
            - Column[lazycolumn]  <container>
              - Column[filterchip]  <container>
                - Column[column]  <container>
                  - Text[item.label]  <leaf>
                  - Text[Always included]  <leaf>
              - Spacer[spacer]  <leaf>
              - Column[column]  <container>
                - Text[${selected.size} item${if (sel…]  <leaf>
                - Spacer[spacer]  <leaf>
            - Column[column]  <container>
              - Button[Saving...|Done selecting]  <leaf>
        - Column[learntolistenpro]  <container>
          - Column[column]  <container>
            - Icon[icon]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[Strongly Recommended:\nLearn t…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Text[Since you're starting out, we …]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[Join 'Learn to Listen' (Recomm…]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[I'll choose my own path]  <leaf>
        - Column[pathselectionste]  <container>
          - Column[column]  <container>
            - Column[column]  <container>
              - Spacer[spacer]  <leaf>
              - Column[stepheading]  <container>
                - Text[Choose your first path]  <leaf>
              - Text[Your path sets the intention f…]  <leaf>
              - Spacer[spacer]  <leaf>
            - Column[lazycolumn]  <container>
              - Column[pathcard]  <container>
                - Column[wflcard]  <container>
                  - Column[roundedcornersha]  <leaf>
                  - Column[borderstroke]  <leaf>
                  - Column[card]  <leaf>
                  - Column[card]  <leaf>
                  - Row[row]  <container>
                    - Column[column]  <container>
                      - Text[definition.name]  <leaf>
                      - Spacer[spacer]  <leaf>
                      - Text[definition.tagline]  <leaf>
                      - Spacer[spacer]  <leaf>
                      - Text[${definition.minSessionsPerWee…]  <leaf>
                    - Spacer[spacer]  <leaf>
                    - Column[surface]  <container>
                      - Column[box]  <container>
                        - Icon[icon]  <leaf>
              - Spacer[spacer]  <leaf>
            - Column[column]  <container>
              - Button[Continue →]  <leaf>
        - Column[programselection]  <container>
          - Column[column]  <container>
            - Column[column]  <container>
              - Spacer[spacer]  <leaf>
              - Column[stepheading]  <container>
                - Text[Pick your starting program]  <leaf>
              - Text[Programs for your chosen path.…]  <leaf>
              - Spacer[spacer]  <leaf>
            - Column[box]  <container>
              - Column[circularprogress]  <leaf>
            - Column[lazycolumn]  <container>
              - Column[onboardingprogra]  <container>
                - Column[wflcard]  <container>
                  - Column[roundedcornersha]  <leaf>
                  - Column[borderstroke]  <leaf>
                  - Column[card]  <leaf>
                  - Column[card]  <leaf>
                  - Column[column]  <container>
                    - Row[row]  <container>
                      - Text[program.name]  <leaf>
                      - Icon[Selected]  <leaf>
                    - Spacer[spacer]  <leaf>
                    - Text[desc]  <leaf>
                    - Spacer[spacer]  <leaf>
                    - Text[${program.totalWeeks} week${if…]  <leaf>
              - Spacer[spacer]  <leaf>
            - Column[column]  <container>
              - Button[Let's go →]  <leaf>
              - Spacer[spacer]  <leaf>
              - Button[Skip for now — I'll choose lat…]  <leaf>
        - Column[box]  <leaf>
    - Column[topappbar]  <container>
      - Icon[Back]  <leaf>

---
## verify vs Compose source (OnboardingScreen)
- distinct leaf signatures matched: 50/53 = 94%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 332 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (onboarding_screen.py)
- leaf signatures shared:        4
- generated-only (other states / not in this trace): 46
- hand-built-only (helper glyphs / human representation): 1
    HB-only  F:Your name
    GEN-only I:Back
    GEN-only I:Selected
    GEN-only T:A bit about your body
    GEN-only T:Always included
    GEN-only T:Are you training right now?
    GEN-only T:Back to options
    GEN-only T:Calibrate with us
    GEN-only T:Choose your first path
    GEN-only T:Continue →
    GEN-only T:Enter what you can — leave any…
    GEN-only T:Enter your numbers
    GEN-only T:Find your starting weights
