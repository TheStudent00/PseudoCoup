# PseudoUI generated kit screen -- onboarding  (from Compose OnboardingScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (356 calls)
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
ui.define_spacer_zone("onboarding_z50_spacer", "onboarding_z47_column")
ui.define_text("onboarding_z51_opt_qualifier", "onboarding_z47_column", "opt.qualifier")
ui.define_icon("onboarding_z52_icon", "onboarding_z44_row", "")
ui.define_spacer_zone("onboarding_z53_spacer", "onboarding_z31_column")
ui.define_spacer_zone("onboarding_z54_spacer", "onboarding_z31_column")
ui.define_button("onboarding_z55_i_ll_set_this_la", "onboarding_z31_column", "I'll set this later")
ui.define_spacer_zone("onboarding_z56_spacer", "onboarding_z31_column")
ui.define_box("onboarding_z57_trainingstatusst", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z58_column", "onboarding_z57_trainingstatusst", "V")
ui.define_spacer_zone("onboarding_z59_spacer", "onboarding_z58_column")
ui.define_box("onboarding_z60_stepheading", "onboarding_z58_column", "V")
ui.define_text("onboarding_z61_are_you_training", "onboarding_z60_stepheading", "Are you training right now?")
ui.define_spacer_zone("onboarding_z62_spacer", "onboarding_z58_column")
ui.define_text("onboarding_z63_if_you_ve_been_a", "onboarding_z58_column", "If you've been away for a whil…")
ui.define_spacer_zone("onboarding_z64_spacer", "onboarding_z58_column")
ui.define_box("onboarding_z65_selectioncard", "onboarding_z58_column", "V")
ui.define_box("onboarding_z66_wflcard", "onboarding_z65_selectioncard", "V")
ui.define_box("onboarding_z67_roundedcornersha", "onboarding_z66_wflcard", "V")
ui.define_box("onboarding_z68_borderstroke", "onboarding_z66_wflcard", "V")
ui.define_box("onboarding_z69_card", "onboarding_z66_wflcard", "V")
ui.define_box("onboarding_z70_card", "onboarding_z66_wflcard", "V")
ui.define_box("onboarding_z71_row", "onboarding_z66_wflcard", "H")
ui.define_text("onboarding_z72_opt_emoji", "onboarding_z71_row", "opt.emoji")
ui.define_spacer_zone("onboarding_z73_spacer", "onboarding_z71_row")
ui.define_box("onboarding_z74_column", "onboarding_z71_row", "V")
ui.define_text("onboarding_z75_opt_title", "onboarding_z74_column", "opt.title")
ui.define_text("onboarding_z76_opt_subtitle", "onboarding_z74_column", "opt.subtitle")
ui.define_spacer_zone("onboarding_z77_spacer", "onboarding_z74_column")
ui.define_text("onboarding_z78_qualifier", "onboarding_z74_column", "qualifier")
ui.define_icon("onboarding_z79_icon", "onboarding_z71_row", "")
ui.define_spacer_zone("onboarding_z80_spacer", "onboarding_z58_column")
ui.define_spacer_zone("onboarding_z81_spacer", "onboarding_z58_column")
ui.define_button("onboarding_z82_i_ll_set_this_la", "onboarding_z58_column", "I'll set this later")
ui.define_spacer_zone("onboarding_z83_spacer", "onboarding_z58_column")
ui.define_box("onboarding_z84_weightunitstep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z85_column", "onboarding_z84_weightunitstep", "V")
ui.define_box("onboarding_z86_stepheading", "onboarding_z85_column", "V")
ui.define_text("onboarding_z87_how_do_you_measu", "onboarding_z86_stepheading", "How do you measure your weight…")
ui.define_spacer_zone("onboarding_z88_spacer", "onboarding_z85_column")
ui.define_text("onboarding_z89_used_across_the_", "onboarding_z85_column", "Used across the whole app and …")
ui.define_spacer_zone("onboarding_z90_spacer", "onboarding_z85_column")
ui.define_box("onboarding_z91_row", "onboarding_z85_column", "H")
ui.define_box("onboarding_z92_selectioncard", "onboarding_z91_row", "V")
ui.define_box("onboarding_z93_wflcard", "onboarding_z92_selectioncard", "V")
ui.define_box("onboarding_z94_roundedcornersha", "onboarding_z93_wflcard", "V")
ui.define_box("onboarding_z95_borderstroke", "onboarding_z93_wflcard", "V")
ui.define_box("onboarding_z96_card", "onboarding_z93_wflcard", "V")
ui.define_box("onboarding_z97_card", "onboarding_z93_wflcard", "V")
ui.define_box("onboarding_z98_row", "onboarding_z93_wflcard", "H")
ui.define_text("onboarding_z99_x", "onboarding_z98_row", "⚖️")
ui.define_spacer_zone("onboarding_z100_spacer", "onboarding_z98_row")
ui.define_box("onboarding_z101_column", "onboarding_z98_row", "V")
ui.define_text("onboarding_z102_unit_name", "onboarding_z101_column", "unit.name")
ui.define_text("onboarding_z103_n", "onboarding_z101_column", "\n|(|)")
ui.define_spacer_zone("onboarding_z104_spacer", "onboarding_z101_column")
ui.define_text("onboarding_z105_qualifier", "onboarding_z101_column", "qualifier")
ui.define_icon("onboarding_z106_icon", "onboarding_z98_row", "")
ui.define_box("onboarding_z107_startingstrength", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z108_column", "onboarding_z107_startingstrength", "V")
ui.define_spacer_zone("onboarding_z109_spacer", "onboarding_z108_column")
ui.define_box("onboarding_z110_stepheading", "onboarding_z108_column", "V")
ui.define_text("onboarding_z111_a_bit_about_your", "onboarding_z110_stepheading", "A bit about your body")
ui.define_spacer_zone("onboarding_z112_spacer", "onboarding_z108_column")
ui.define_text("onboarding_z113_this_just_sets_y", "onboarding_z108_column", "This just sets your very first…")
ui.define_spacer_zone("onboarding_z114_spacer", "onboarding_z108_column")
ui.define_box("onboarding_z115_labeledfield", "onboarding_z108_column", "V")
ui.define_box("onboarding_z116_column", "onboarding_z115_labeledfield", "V")
ui.define_box("onboarding_z117_fieldlabel", "onboarding_z116_column", "V")
ui.define_text("onboarding_z118_bodyweight_weigh", "onboarding_z117_fieldlabel", "Bodyweight (${weightUnit.name.…")
ui.define_box("onboarding_z119_compactvaluefiel", "onboarding_z115_labeledfield", "V")
ui.define_input_zone("onboarding_z120_field", "onboarding_z119_compactvaluefiel", "", "")
ui.define_text("onboarding_z121_optional_helps_s", "onboarding_z115_labeledfield", "Optional — helps size your fir…")
ui.define_spacer_zone("onboarding_z122_spacer", "onboarding_z108_column")
ui.define_text("onboarding_z123_which_sounds_mor", "onboarding_z108_column", "Which sounds more like your bo…")
ui.define_spacer_zone("onboarding_z124_spacer", "onboarding_z108_column")
ui.define_box("onboarding_z125_selectioncard", "onboarding_z108_column", "V")
ui.define_box("onboarding_z126_wflcard", "onboarding_z125_selectioncard", "V")
ui.define_box("onboarding_z127_roundedcornersha", "onboarding_z126_wflcard", "V")
ui.define_box("onboarding_z128_borderstroke", "onboarding_z126_wflcard", "V")
ui.define_box("onboarding_z129_card", "onboarding_z126_wflcard", "V")
ui.define_box("onboarding_z130_card", "onboarding_z126_wflcard", "V")
ui.define_box("onboarding_z131_row", "onboarding_z126_wflcard", "H")
ui.define_text("onboarding_z132_opt_emoji", "onboarding_z131_row", "opt.emoji")
ui.define_spacer_zone("onboarding_z133_spacer", "onboarding_z131_row")
ui.define_box("onboarding_z134_column", "onboarding_z131_row", "V")
ui.define_text("onboarding_z135_opt_title", "onboarding_z134_column", "opt.title")
ui.define_text("onboarding_z136_opt_subtitle", "onboarding_z134_column", "opt.subtitle")
ui.define_spacer_zone("onboarding_z137_spacer", "onboarding_z134_column")
ui.define_text("onboarding_z138_opt_examples", "onboarding_z134_column", "opt.examples")
ui.define_icon("onboarding_z139_icon", "onboarding_z131_row", "")
ui.define_spacer_zone("onboarding_z140_spacer", "onboarding_z108_column")
ui.define_text("onboarding_z141_not_sure_leave_i", "onboarding_z108_column", "Not sure? Leave it — we'll sta…")
ui.define_spacer_zone("onboarding_z142_spacer", "onboarding_z108_column")
ui.define_button("onboarding_z143_continue", "onboarding_z108_column", "Continue")
ui.define_button("onboarding_z144_skip_for_now", "onboarding_z108_column", "Skip for now")
ui.define_spacer_zone("onboarding_z145_spacer", "onboarding_z108_column")
ui.define_box("onboarding_z146_calibrationstep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z147_column", "onboarding_z146_calibrationstep", "V")
ui.define_spacer_zone("onboarding_z148_spacer", "onboarding_z147_column")
ui.define_box("onboarding_z149_stepheading", "onboarding_z147_column", "V")
ui.define_text("onboarding_z150_you_re_calibrate", "onboarding_z149_stepheading", "You're calibrated")
ui.define_spacer_zone("onboarding_z151_spacer", "onboarding_z147_column")
ui.define_text("onboarding_z152_your_starting_we", "onboarding_z147_column", "Your starting weights come fro…")
ui.define_spacer_zone("onboarding_z153_spacer", "onboarding_z147_column")
ui.define_box("onboarding_z154_calibrationoutco", "onboarding_z147_column", "V")
ui.define_box("onboarding_z155_wflcard", "onboarding_z154_calibrationoutco", "V")
ui.define_box("onboarding_z156_roundedcornersha", "onboarding_z155_wflcard", "V")
ui.define_box("onboarding_z157_borderstroke", "onboarding_z155_wflcard", "V")
ui.define_box("onboarding_z158_card", "onboarding_z155_wflcard", "V")
ui.define_box("onboarding_z159_card", "onboarding_z155_wflcard", "V")
ui.define_box("onboarding_z160_column", "onboarding_z155_wflcard", "V")
ui.define_text("onboarding_z161_outcome_label", "onboarding_z160_column", "outcome.label")
ui.define_text("onboarding_z162_confidencelabel_", "onboarding_z160_column", "confidenceLabel(outcome.confid…")
ui.define_spacer_zone("onboarding_z163_spacer", "onboarding_z147_column")
ui.define_spacer_zone("onboarding_z164_spacer", "onboarding_z147_column")
ui.define_button("onboarding_z165_continue", "onboarding_z147_column", "Continue")
ui.define_spacer_zone("onboarding_z166_spacer", "onboarding_z147_column")
ui.define_box("onboarding_z167_stepheading", "onboarding_z147_column", "V")
ui.define_text("onboarding_z168_find_your_starti", "onboarding_z167_stepheading", "Find your starting weights")
ui.define_spacer_zone("onboarding_z169_spacer", "onboarding_z147_column")
ui.define_text("onboarding_z170_no_max_out_testi", "onboarding_z147_column", "No max-out testing, ever — it'…")
ui.define_spacer_zone("onboarding_z171_spacer", "onboarding_z147_column")
ui.define_box("onboarding_z172_selectioncard", "onboarding_z147_column", "V")
ui.define_box("onboarding_z173_wflcard", "onboarding_z172_selectioncard", "V")
ui.define_box("onboarding_z174_roundedcornersha", "onboarding_z173_wflcard", "V")
ui.define_box("onboarding_z175_borderstroke", "onboarding_z173_wflcard", "V")
ui.define_box("onboarding_z176_card", "onboarding_z173_wflcard", "V")
ui.define_box("onboarding_z177_card", "onboarding_z173_wflcard", "V")
ui.define_box("onboarding_z178_row", "onboarding_z173_wflcard", "H")
ui.define_text("onboarding_z179_x", "onboarding_z178_row", "⌨️")
ui.define_spacer_zone("onboarding_z180_spacer", "onboarding_z178_row")
ui.define_box("onboarding_z181_column", "onboarding_z178_row", "V")
ui.define_text("onboarding_z182_enter_your_numbe", "onboarding_z181_column", "Enter your numbers")
ui.define_text("onboarding_z183_type_a_recent_wo", "onboarding_z181_column", "Type a recent working weight f…")
ui.define_spacer_zone("onboarding_z184_spacer", "onboarding_z181_column")
ui.define_text("onboarding_z185_qualifier", "onboarding_z181_column", "qualifier")
ui.define_icon("onboarding_z186_icon", "onboarding_z178_row", "")
ui.define_spacer_zone("onboarding_z187_spacer", "onboarding_z147_column")
ui.define_box("onboarding_z188_selectioncard", "onboarding_z147_column", "V")
ui.define_box("onboarding_z189_wflcard", "onboarding_z188_selectioncard", "V")
ui.define_box("onboarding_z190_roundedcornersha", "onboarding_z189_wflcard", "V")
ui.define_box("onboarding_z191_borderstroke", "onboarding_z189_wflcard", "V")
ui.define_box("onboarding_z192_card", "onboarding_z189_wflcard", "V")
ui.define_box("onboarding_z193_card", "onboarding_z189_wflcard", "V")
ui.define_box("onboarding_z194_row", "onboarding_z189_wflcard", "H")
ui.define_text("onboarding_z195_x", "onboarding_z194_row", "🏋️")
ui.define_spacer_zone("onboarding_z196_spacer", "onboarding_z194_row")
ui.define_box("onboarding_z197_column", "onboarding_z194_row", "V")
ui.define_text("onboarding_z198_calibrate_with_u", "onboarding_z197_column", "Calibrate with us")
ui.define_text("onboarding_z199_work_up_to_a_tou", "onboarding_z197_column", "Work up to a tough set of a fe…")
ui.define_spacer_zone("onboarding_z200_spacer", "onboarding_z197_column")
ui.define_text("onboarding_z201_qualifier", "onboarding_z197_column", "qualifier")
ui.define_icon("onboarding_z202_icon", "onboarding_z194_row", "")
ui.define_spacer_zone("onboarding_z203_spacer", "onboarding_z147_column")
ui.define_button("onboarding_z204_skip_just_start_", "onboarding_z147_column", "Skip — just start me light")
ui.define_spacer_zone("onboarding_z205_spacer", "onboarding_z147_column")
ui.define_box("onboarding_z206_stepheading", "onboarding_z147_column", "V")
ui.define_text("onboarding_z207_enter_your_numbe", "onboarding_z206_stepheading", "Enter your numbers|Calibrate w…")
ui.define_spacer_zone("onboarding_z208_spacer", "onboarding_z147_column")
ui.define_text("onboarding_z209_calibrationformh", "onboarding_z147_column", "calibrationFormHint(effectiveM…")
ui.define_spacer_zone("onboarding_z210_spacer", "onboarding_z147_column")
ui.define_box("onboarding_z211_labeledfield", "onboarding_z147_column", "V")
ui.define_box("onboarding_z212_column", "onboarding_z211_labeledfield", "V")
ui.define_box("onboarding_z213_fieldlabel", "onboarding_z212_column", "V")
ui.define_text("onboarding_z214_lift_label_weigh", "onboarding_z213_fieldlabel", "${lift.label} (${weightUnit.na…")
ui.define_box("onboarding_z215_compactvaluefiel", "onboarding_z211_labeledfield", "V")
ui.define_input_zone("onboarding_z216_field", "onboarding_z215_compactvaluefiel", "", "")
ui.define_spacer_zone("onboarding_z217_spacer", "onboarding_z147_column")
ui.define_text("onboarding_z218_enter_what_you_c", "onboarding_z147_column", "Enter what you can — leave any…")
ui.define_spacer_zone("onboarding_z219_spacer", "onboarding_z147_column")
ui.define_button("onboarding_z220_saving_save_my_n", "onboarding_z147_column", "Saving…|Save my numbers")
ui.define_button("onboarding_z221_back_to_options", "onboarding_z147_column", "Back to options")
ui.define_button("onboarding_z222_skip_for_now", "onboarding_z147_column", "Skip for now")
ui.define_spacer_zone("onboarding_z223_spacer", "onboarding_z147_column")
ui.define_box("onboarding_z224_gymtypestep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z225_column", "onboarding_z224_gymtypestep", "V")
ui.define_spacer_zone("onboarding_z226_spacer", "onboarding_z225_column")
ui.define_box("onboarding_z227_stepheading", "onboarding_z225_column", "V")
ui.define_text("onboarding_z228_tell_us_about_yo", "onboarding_z227_stepheading", "Tell us about your gym")
ui.define_spacer_zone("onboarding_z229_spacer", "onboarding_z225_column")
ui.define_text("onboarding_z230_we_ll_pre_load_t", "onboarding_z225_column", "We'll pre-load the most common…")
ui.define_spacer_zone("onboarding_z231_spacer", "onboarding_z225_column")
ui.define_box("onboarding_z232_labeledfield", "onboarding_z225_column", "V")
ui.define_box("onboarding_z233_column", "onboarding_z232_labeledfield", "V")
ui.define_box("onboarding_z234_fieldlabel", "onboarding_z233_column", "V")
ui.define_text("onboarding_z235_gym_name", "onboarding_z234_fieldlabel", "Gym name")
ui.define_box("onboarding_z236_compactvaluefiel", "onboarding_z232_labeledfield", "V")
ui.define_input_zone("onboarding_z237_field", "onboarding_z236_compactvaluefiel", "", "")
ui.define_spacer_zone("onboarding_z238_spacer", "onboarding_z225_column")
ui.define_box("onboarding_z239_selectioncard", "onboarding_z225_column", "V")
ui.define_box("onboarding_z240_wflcard", "onboarding_z239_selectioncard", "V")
ui.define_box("onboarding_z241_roundedcornersha", "onboarding_z240_wflcard", "V")
ui.define_box("onboarding_z242_borderstroke", "onboarding_z240_wflcard", "V")
ui.define_box("onboarding_z243_card", "onboarding_z240_wflcard", "V")
ui.define_box("onboarding_z244_card", "onboarding_z240_wflcard", "V")
ui.define_box("onboarding_z245_row", "onboarding_z240_wflcard", "H")
ui.define_text("onboarding_z246_type_emoji", "onboarding_z245_row", "type.emoji")
ui.define_spacer_zone("onboarding_z247_spacer", "onboarding_z245_row")
ui.define_box("onboarding_z248_column", "onboarding_z245_row", "V")
ui.define_text("onboarding_z249_type_displayname", "onboarding_z248_column", "type.displayName")
ui.define_text("onboarding_z250_type_description", "onboarding_z248_column", "type.description")
ui.define_spacer_zone("onboarding_z251_spacer", "onboarding_z248_column")
ui.define_text("onboarding_z252_qualifier", "onboarding_z248_column", "qualifier")
ui.define_icon("onboarding_z253_icon", "onboarding_z245_row", "")
ui.define_spacer_zone("onboarding_z254_spacer", "onboarding_z225_column")
ui.define_spacer_zone("onboarding_z255_spacer", "onboarding_z225_column")
ui.define_button("onboarding_z256_skip_gym_setup_f", "onboarding_z225_column", "Skip gym setup for now")
ui.define_spacer_zone("onboarding_z257_spacer", "onboarding_z225_column")
ui.define_box("onboarding_z258_equipmentstep", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z259_column", "onboarding_z258_equipmentstep", "V")
ui.define_box("onboarding_z260_column", "onboarding_z259_column", "V")
ui.define_spacer_zone("onboarding_z261_spacer", "onboarding_z260_column")
ui.define_box("onboarding_z262_stepheading", "onboarding_z260_column", "V")
ui.define_text("onboarding_z263_what_does_gymtyp", "onboarding_z262_stepheading", "What does ${gymType.displayNam…")
ui.define_text("onboarding_z264_suggested_equipm", "onboarding_z260_column", "Suggested equipment is pre-che…")
ui.define_spacer_zone("onboarding_z265_spacer", "onboarding_z260_column")
ui.define_box("onboarding_z266_labeledfield", "onboarding_z260_column", "V")
ui.define_box("onboarding_z267_column", "onboarding_z266_labeledfield", "V")
ui.define_box("onboarding_z268_fieldlabel", "onboarding_z267_column", "V")
ui.define_text("onboarding_z269_search_all_equip", "onboarding_z268_fieldlabel", "Search all equipment")
ui.define_box("onboarding_z270_compactvaluefiel", "onboarding_z266_labeledfield", "V")
ui.define_input_zone("onboarding_z271_field", "onboarding_z270_compactvaluefiel", "", "")
ui.define_spacer_zone("onboarding_z272_spacer", "onboarding_z260_column")
ui.define_box("onboarding_z273_lazycolumn", "onboarding_z259_column", "V")
ui.define_box("onboarding_z274_filterchip", "onboarding_z273_lazycolumn", "V")
ui.define_box("onboarding_z275_column", "onboarding_z274_filterchip", "V")
ui.define_text("onboarding_z276_item_label", "onboarding_z275_column", "item.label")
ui.define_text("onboarding_z277_always_included", "onboarding_z275_column", "Always included")
ui.define_spacer_zone("onboarding_z278_spacer", "onboarding_z273_lazycolumn")
ui.define_box("onboarding_z279_column", "onboarding_z273_lazycolumn", "V")
ui.define_text("onboarding_z280_selected_size_it", "onboarding_z279_column", "${selected.size} item${if (sel…")
ui.define_spacer_zone("onboarding_z281_spacer", "onboarding_z279_column")
ui.define_box("onboarding_z282_column", "onboarding_z259_column", "V")
ui.define_button("onboarding_z283_done_selecting", "onboarding_z282_column", "Done selecting")
ui.define_spacer_zone("onboarding_z284_spacer", "onboarding_z282_column")
ui.define_button("onboarding_z285_configure_equipm", "onboarding_z282_column", "Configure equipment later")
ui.define_box("onboarding_z286_learntolistenpro", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z287_column", "onboarding_z286_learntolistenpro", "V")
ui.define_icon("onboarding_z288_icon", "onboarding_z287_column", "")
ui.define_spacer_zone("onboarding_z289_spacer", "onboarding_z287_column")
ui.define_text("onboarding_z290_strongly_recomme", "onboarding_z287_column", "Strongly Recommended:\nLearn t…")
ui.define_spacer_zone("onboarding_z291_spacer", "onboarding_z287_column")
ui.define_text("onboarding_z292_since_you_re_sta", "onboarding_z287_column", "Since you're starting out, we …")
ui.define_spacer_zone("onboarding_z293_spacer", "onboarding_z287_column")
ui.define_button("onboarding_z294_join_learn_to_li", "onboarding_z287_column", "Join 'Learn to Listen' (Recomm…")
ui.define_spacer_zone("onboarding_z295_spacer", "onboarding_z287_column")
ui.define_button("onboarding_z296_i_ll_choose_my_o", "onboarding_z287_column", "I'll choose my own path")
ui.define_box("onboarding_z297_pathselectionste", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z298_column", "onboarding_z297_pathselectionste", "V")
ui.define_box("onboarding_z299_column", "onboarding_z298_column", "V")
ui.define_spacer_zone("onboarding_z300_spacer", "onboarding_z299_column")
ui.define_box("onboarding_z301_stepheading", "onboarding_z299_column", "V")
ui.define_text("onboarding_z302_choose_your_firs", "onboarding_z301_stepheading", "Choose your first path")
ui.define_text("onboarding_z303_your_path_sets_t", "onboarding_z299_column", "Your path sets the intention f…")
ui.define_spacer_zone("onboarding_z304_spacer", "onboarding_z299_column")
ui.define_box("onboarding_z305_lazycolumn", "onboarding_z298_column", "V")
ui.define_box("onboarding_z306_pathcard", "onboarding_z305_lazycolumn", "V")
ui.define_box("onboarding_z307_wflcard", "onboarding_z306_pathcard", "V")
ui.define_box("onboarding_z308_roundedcornersha", "onboarding_z307_wflcard", "V")
ui.define_box("onboarding_z309_borderstroke", "onboarding_z307_wflcard", "V")
ui.define_box("onboarding_z310_card", "onboarding_z307_wflcard", "V")
ui.define_box("onboarding_z311_card", "onboarding_z307_wflcard", "V")
ui.define_box("onboarding_z312_column", "onboarding_z307_wflcard", "V")
ui.define_box("onboarding_z313_row", "onboarding_z312_column", "H")
ui.define_text("onboarding_z314_path_name", "onboarding_z313_row", "path.name")
ui.define_icon("onboarding_z315_selected", "onboarding_z313_row", "Selected")
ui.define_spacer_zone("onboarding_z316_spacer", "onboarding_z312_column")
ui.define_text("onboarding_z317_path_tagline", "onboarding_z312_column", "path.tagline")
ui.define_spacer_zone("onboarding_z318_spacer", "onboarding_z312_column")
ui.define_text("onboarding_z319_path_minsessions", "onboarding_z312_column", "${path.minSessionsPerWeek}–${p…")
ui.define_spacer_zone("onboarding_z320_spacer", "onboarding_z305_lazycolumn")
ui.define_box("onboarding_z321_column", "onboarding_z298_column", "V")
ui.define_button("onboarding_z322_continue", "onboarding_z321_column", "Continue →")
ui.define_box("onboarding_z323_programselection", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z324_column", "onboarding_z323_programselection", "V")
ui.define_box("onboarding_z325_column", "onboarding_z324_column", "V")
ui.define_spacer_zone("onboarding_z326_spacer", "onboarding_z325_column")
ui.define_box("onboarding_z327_stepheading", "onboarding_z325_column", "V")
ui.define_text("onboarding_z328_pick_your_starti", "onboarding_z327_stepheading", "Pick your starting program")
ui.define_text("onboarding_z329_programs_for_you", "onboarding_z325_column", "Programs for your chosen path.…")
ui.define_spacer_zone("onboarding_z330_spacer", "onboarding_z325_column")
ui.define_box("onboarding_z331_box", "onboarding_z324_column", "V")
ui.define_box("onboarding_z332_circularprogress", "onboarding_z331_box", "V")
ui.define_box("onboarding_z333_lazycolumn", "onboarding_z324_column", "V")
ui.define_box("onboarding_z334_onboardingprogra", "onboarding_z333_lazycolumn", "V")
ui.define_box("onboarding_z335_wflcard", "onboarding_z334_onboardingprogra", "V")
ui.define_box("onboarding_z336_roundedcornersha", "onboarding_z335_wflcard", "V")
ui.define_box("onboarding_z337_borderstroke", "onboarding_z335_wflcard", "V")
ui.define_box("onboarding_z338_card", "onboarding_z335_wflcard", "V")
ui.define_box("onboarding_z339_card", "onboarding_z335_wflcard", "V")
ui.define_box("onboarding_z340_column", "onboarding_z335_wflcard", "V")
ui.define_box("onboarding_z341_row", "onboarding_z340_column", "H")
ui.define_text("onboarding_z342_program_name", "onboarding_z341_row", "program.name")
ui.define_icon("onboarding_z343_selected", "onboarding_z341_row", "Selected")
ui.define_spacer_zone("onboarding_z344_spacer", "onboarding_z340_column")
ui.define_text("onboarding_z345_desc", "onboarding_z340_column", "desc")
ui.define_spacer_zone("onboarding_z346_spacer", "onboarding_z340_column")
ui.define_text("onboarding_z347_program_totalwee", "onboarding_z340_column", "${program.totalWeeks} week${if…")
ui.define_spacer_zone("onboarding_z348_spacer", "onboarding_z333_lazycolumn")
ui.define_box("onboarding_z349_column", "onboarding_z324_column", "V")
ui.define_button("onboarding_z350_let_s_go", "onboarding_z349_column", "Let's go →")
ui.define_spacer_zone("onboarding_z351_spacer", "onboarding_z349_column")
ui.define_button("onboarding_z352_skip_for_now_i_l", "onboarding_z349_column", "Skip for now — I'll choose lat…")
ui.define_box("onboarding_z353_box", "onboarding_z05_animatedcontent", "V")
ui.define_box("onboarding_z354_topappbar", "onboarding_z02_scaffold", "V")
ui.define_icon("onboarding_z355_back", "onboarding_z354_topappbar", "Back")
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
                    - Text[opt.qualifier]  <leaf>
                  - Icon[icon]  <leaf>
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
                    - Text[qualifier]  <leaf>
                  - Icon[icon]  <leaf>
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
                      - Spacer[spacer]  <leaf>
                      - Text[qualifier]  <leaf>
                    - Icon[icon]  <leaf>
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
                    - Text[opt.examples]  <leaf>
                  - Icon[icon]  <leaf>
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
                    - Text[qualifier]  <leaf>
                  - Icon[icon]  <leaf>
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
                    - Text[qualifier]  <leaf>
                  - Icon[icon]  <leaf>
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
            - Column[stepheading]  <container>
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
                    - Text[qualifier]  <leaf>
                  - Icon[icon]  <leaf>
            - Spacer[spacer]  <leaf>
            - Spacer[spacer]  <leaf>
            - Button[Skip gym setup for now]  <leaf>
            - Spacer[spacer]  <leaf>
        - Column[equipmentstep]  <container>
          - Column[column]  <container>
            - Column[column]  <container>
              - Spacer[spacer]  <leaf>
              - Column[stepheading]  <container>
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
              - Button[Done selecting]  <leaf>
              - Spacer[spacer]  <leaf>
              - Button[Configure equipment later]  <leaf>
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
                  - Column[column]  <container>
                    - Row[row]  <container>
                      - Text[path.name]  <leaf>
                      - Icon[Selected]  <leaf>
                    - Spacer[spacer]  <leaf>
                    - Text[path.tagline]  <leaf>
                    - Spacer[spacer]  <leaf>
                    - Text[${path.minSessionsPerWeek}–${p…]  <leaf>
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
- distinct leaf signatures matched: 53/53 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 356 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (onboarding_screen.py)
- leaf signatures shared:        4
- generated-only (other states / not in this trace): 49
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
    GEN-only T:Configure equipment later
    GEN-only T:Continue →
    GEN-only T:Done selecting
    GEN-only T:Enter what you can — leave any…
