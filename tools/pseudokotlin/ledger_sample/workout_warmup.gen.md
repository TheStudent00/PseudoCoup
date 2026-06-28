# PseudoUI generated kit screen -- workout_warmup  (from Compose WorkoutWarmupScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (57 calls)
```python
ui.define_box("workout_warmup_z00_scaffold", "content", "V")
ui.define_box("workout_warmup_z01_column", "workout_warmup_z00_scaffold", "V")
ui.define_box("workout_warmup_z02_warmupselecting", "workout_warmup_z01_column", "V")
ui.define_box("workout_warmup_z03_column", "workout_warmup_z02_warmupselecting", "V")
ui.define_spacer_zone("workout_warmup_z04_spacer", "workout_warmup_z03_column")
ui.define_text("workout_warmup_z05_let_s_get_you_mo", "workout_warmup_z03_column", "Let's get you moving.")
ui.define_text("workout_warmup_z06_pick_something_f", "workout_warmup_z03_column", "Pick something fun for a few m…")
ui.define_box("workout_warmup_z07_conditioningacti", "workout_warmup_z03_column", "V")
ui.define_box("workout_warmup_z08_column", "workout_warmup_z07_conditioningacti", "V")
ui.define_box("workout_warmup_z09_activitycard", "workout_warmup_z08_column", "V")
ui.define_box("workout_warmup_z10_surface", "workout_warmup_z09_activitycard", "V")
ui.define_box("workout_warmup_z11_row", "workout_warmup_z10_surface", "H")
ui.define_text("workout_warmup_z12_activity_emoji", "workout_warmup_z11_row", "activity.emoji")
ui.define_spacer_zone("workout_warmup_z13_spacer", "workout_warmup_z11_row")
ui.define_box("workout_warmup_z14_column", "workout_warmup_z11_row", "V")
ui.define_box("workout_warmup_z15_row", "workout_warmup_z14_column", "H")
ui.define_text("workout_warmup_z16_activity_name", "workout_warmup_z15_row", "activity.name")
ui.define_spacer_zone("workout_warmup_z17_spacer", "workout_warmup_z15_row")
ui.define_text("workout_warmup_z18_formatminutes_ac", "workout_warmup_z15_row", "formatMinutes(activity.default…")
ui.define_text("workout_warmup_z19_activity_tagline", "workout_warmup_z14_column", "activity.tagline")
ui.define_spacer_zone("workout_warmup_z20_spacer", "workout_warmup_z11_row")
ui.define_box("workout_warmup_z21_box", "workout_warmup_z11_row", "V")
ui.define_icon("workout_warmup_z22_start_activity_n", "workout_warmup_z21_box", "Start ${activity.name}")
ui.define_button("workout_warmup_z23_skip_warm_up", "workout_warmup_z03_column", "Skip warm-up")
ui.define_spacer_zone("workout_warmup_z24_spacer", "workout_warmup_z03_column")
ui.define_box("workout_warmup_z25_conditioningtime", "workout_warmup_z01_column", "V")
ui.define_box("workout_warmup_z26_column", "workout_warmup_z25_conditioningtime", "V")
ui.define_text("workout_warmup_z27_state_activity_p", "workout_warmup_z26_column", "state.activity.phase.label()")
ui.define_spacer_zone("workout_warmup_z28_spacer", "workout_warmup_z26_column")
ui.define_text("workout_warmup_z29_state_activity_e", "workout_warmup_z26_column", "${state.activity.emoji} ${stat…")
ui.define_spacer_zone("workout_warmup_z30_spacer", "workout_warmup_z26_column")
ui.define_box("workout_warmup_z31_box", "workout_warmup_z26_column", "V")
ui.define_box("workout_warmup_z32_box", "workout_warmup_z31_box", "V")
ui.define_text("workout_warmup_z33_formattime_state", "workout_warmup_z31_box", "formatTime(state.remainingSeco…")
ui.define_spacer_zone("workout_warmup_z34_spacer", "workout_warmup_z26_column")
ui.define_text("workout_warmup_z35_state_activity_t", "workout_warmup_z26_column", "state.activity.tagline")
ui.define_spacer_zone("workout_warmup_z36_spacer", "workout_warmup_z26_column")
ui.define_box("workout_warmup_z37_row", "workout_warmup_z26_column", "H")
ui.define_button("workout_warmup_z38_1_min", "workout_warmup_z37_row", "+1 min")
ui.define_spacer_zone("workout_warmup_z39_spacer", "workout_warmup_z37_row")
ui.define_button("workout_warmup_z40_i_m_done", "workout_warmup_z37_row", "I'm done")
ui.define_box("workout_warmup_z41_conditioningfini", "workout_warmup_z01_column", "V")
ui.define_box("workout_warmup_z42_column", "workout_warmup_z41_conditioningfini", "V")
ui.define_spacer_zone("workout_warmup_z43_spacer", "workout_warmup_z42_column")
ui.define_text("workout_warmup_z44_x", "workout_warmup_z42_column", "💪")
ui.define_spacer_zone("workout_warmup_z45_spacer", "workout_warmup_z42_column")
ui.define_text("workout_warmup_z46_you_re_warmed_up", "workout_warmup_z42_column", "You're warmed up")
ui.define_spacer_zone("workout_warmup_z47_spacer", "workout_warmup_z42_column")
ui.define_text("workout_warmup_z48_it", "workout_warmup_z42_column", "it")
ui.define_spacer_zone("workout_warmup_z49_spacer", "workout_warmup_z42_column")
ui.define_spacer_zone("workout_warmup_z50_spacer", "workout_warmup_z42_column")
ui.define_button("workout_warmup_z51_start_workout", "workout_warmup_z42_column", "Start workout")
ui.define_spacer_zone("workout_warmup_z52_spacer", "workout_warmup_z42_column")
ui.define_box("workout_warmup_z53_topappbar", "workout_warmup_z00_scaffold", "V")
ui.define_text("workout_warmup_z54_warm_up_warm_up", "workout_warmup_z53_topappbar", "Warm up|Warm up")
ui.define_icon("workout_warmup_z55_back_back_to_war", "workout_warmup_z53_topappbar", "Back|Back to warm-ups")
ui.define_icon("workout_warmup_z56_why_warm_up", "workout_warmup_z53_topappbar", "Why warm up?")
```

## generated tree
  - Column[z00_scaffold]  <container>
    - Column[z01_column]  <container>
      - Column[z02_warmupselecting]  <container>
        - Column[z03_column]  <container>
          - Spacer[z04_spacer]  <leaf>
          - Text[Let's get you moving.]  <leaf>
          - Text[Pick something fun for a few m…]  <leaf>
          - Column[z07_conditioningacti]  <container>
            - Column[z08_column]  <container>
              - Column[z09_activitycard]  <container>
                - Column[z10_surface]  <container>
                  - Row[z11_row]  <container>
                    - Text[activity.emoji]  <leaf>
                    - Spacer[z13_spacer]  <leaf>
                    - Column[z14_column]  <container>
                      - Row[z15_row]  <container>
                        - Text[activity.name]  <leaf>
                        - Spacer[z17_spacer]  <leaf>
                        - Text[formatMinutes(activity.default…]  <leaf>
                      - Text[activity.tagline]  <leaf>
                    - Spacer[z20_spacer]  <leaf>
                    - Column[z21_box]  <container>
                      - Icon[Start ${activity.name}]  <leaf>
          - Button[Skip warm-up]  <leaf>
          - Spacer[z24_spacer]  <leaf>
      - Column[z25_conditioningtime]  <container>
        - Column[z26_column]  <container>
          - Text[state.activity.phase.label()]  <leaf>
          - Spacer[z28_spacer]  <leaf>
          - Text[${state.activity.emoji} ${stat…]  <leaf>
          - Spacer[z30_spacer]  <leaf>
          - Column[z31_box]  <container>
            - Column[z32_box]  <leaf>
            - Text[formatTime(state.remainingSeco…]  <leaf>
          - Spacer[z34_spacer]  <leaf>
          - Text[state.activity.tagline]  <leaf>
          - Spacer[z36_spacer]  <leaf>
          - Row[z37_row]  <container>
            - Button[+1 min]  <leaf>
            - Spacer[z39_spacer]  <leaf>
            - Button[I'm done]  <leaf>
      - Column[z41_conditioningfini]  <container>
        - Column[z42_column]  <container>
          - Spacer[z43_spacer]  <leaf>
          - Text[💪]  <leaf>
          - Spacer[z45_spacer]  <leaf>
          - Text[You're warmed up]  <leaf>
          - Spacer[z47_spacer]  <leaf>
          - Text[it]  <leaf>
          - Spacer[z49_spacer]  <leaf>
          - Spacer[z50_spacer]  <leaf>
          - Button[Start workout]  <leaf>
          - Spacer[z52_spacer]  <leaf>
    - Column[z53_topappbar]  <container>
      - Text[Warm up|Warm up]  <leaf>
      - Icon[Back|Back to warm-ups]  <leaf>
      - Icon[Why warm up?]  <leaf>

---
## verify vs Compose source (WorkoutWarmupScreen)
- distinct leaf signatures matched: 9/9 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 57 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (workout_warmup_screen.py)
- leaf signatures shared:        3
- generated-only (other states / not in this trace): 6
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:Why warm up?
    GEN-only I:·DYN·
    GEN-only T:+1 min
    GEN-only T:I'm done
    GEN-only T:Start workout
    GEN-only T:You're warmed up
