# PseudoUI generated kit screen -- workout_cooldown  (from Compose WorkoutCooldownScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (80 calls)
```python
ui.define_box("workout_cooldown_z00_scienceinfodialo", "content", "V")
ui.define_box("workout_cooldown_z01_alertdialog", "workout_cooldown_z00_scienceinfodialo", "V")
ui.define_button("workout_cooldown_z02_got_it", "workout_cooldown_z01_alertdialog", "Got it")
ui.define_text("workout_cooldown_z03_why_cool_down", "workout_cooldown_z01_alertdialog", "Why cool down?")
ui.define_box("workout_cooldown_z04_column", "workout_cooldown_z01_alertdialog", "V")
ui.define_text("workout_cooldown_z05_conditioningcata", "workout_cooldown_z04_column", "ConditioningCatalog.COOLDOWN_W…")
ui.define_box("workout_cooldown_z06_column", "workout_cooldown_z04_column", "V")
ui.define_text("workout_cooldown_z07_note_heading", "workout_cooldown_z06_column", "note.heading")
ui.define_text("workout_cooldown_z08_note_body", "workout_cooldown_z06_column", "note.body")
ui.define_box("workout_cooldown_z09_scaffold", "content", "V")
ui.define_box("workout_cooldown_z10_column", "workout_cooldown_z09_scaffold", "V")
ui.define_box("workout_cooldown_z11_cooldownselectin", "workout_cooldown_z10_column", "V")
ui.define_box("workout_cooldown_z12_column", "workout_cooldown_z11_cooldownselectin", "V")
ui.define_spacer_zone("workout_cooldown_z13_spacer", "workout_cooldown_z12_column")
ui.define_text("workout_cooldown_z14_take_a_few_minut", "workout_cooldown_z12_column", "Take a few minutes to come dow…")
ui.define_text("workout_cooldown_z15_your_muscles_are", "workout_cooldown_z12_column", "Your muscles are warmest right…")
ui.define_box("workout_cooldown_z16_conditioningacti", "workout_cooldown_z12_column", "V")
ui.define_box("workout_cooldown_z17_column", "workout_cooldown_z16_conditioningacti", "V")
ui.define_box("workout_cooldown_z18_activitycard", "workout_cooldown_z17_column", "V")
ui.define_box("workout_cooldown_z19_surface", "workout_cooldown_z18_activitycard", "V")
ui.define_box("workout_cooldown_z20_row", "workout_cooldown_z19_surface", "H")
ui.define_text("workout_cooldown_z21_activity_emoji", "workout_cooldown_z20_row", "activity.emoji")
ui.define_spacer_zone("workout_cooldown_z22_spacer", "workout_cooldown_z20_row")
ui.define_box("workout_cooldown_z23_column", "workout_cooldown_z20_row", "V")
ui.define_box("workout_cooldown_z24_row", "workout_cooldown_z23_column", "H")
ui.define_text("workout_cooldown_z25_activity_name", "workout_cooldown_z24_row", "activity.name")
ui.define_spacer_zone("workout_cooldown_z26_spacer", "workout_cooldown_z24_row")
ui.define_text("workout_cooldown_z27_formatminutes_ac", "workout_cooldown_z24_row", "formatMinutes(activity.default…")
ui.define_text("workout_cooldown_z28_activity_tagline", "workout_cooldown_z23_column", "activity.tagline")
ui.define_spacer_zone("workout_cooldown_z29_spacer", "workout_cooldown_z20_row")
ui.define_box("workout_cooldown_z30_box", "workout_cooldown_z20_row", "V")
ui.define_icon("workout_cooldown_z31_start_activity_n", "workout_cooldown_z30_box", "Start ${activity.name}")
ui.define_button("workout_cooldown_z32_forgot_something", "workout_cooldown_z12_column", "Forgot something? Back to work…")
ui.define_button("workout_cooldown_z33_done_wrap_up", "workout_cooldown_z12_column", "Done — wrap up")
ui.define_spacer_zone("workout_cooldown_z34_spacer", "workout_cooldown_z12_column")
ui.define_box("workout_cooldown_z35_conditioningtime", "workout_cooldown_z10_column", "V")
ui.define_box("workout_cooldown_z36_column", "workout_cooldown_z35_conditioningtime", "V")
ui.define_text("workout_cooldown_z37_state_activity_p", "workout_cooldown_z36_column", "state.activity.phase.label()")
ui.define_spacer_zone("workout_cooldown_z38_spacer", "workout_cooldown_z36_column")
ui.define_text("workout_cooldown_z39_state_activity_e", "workout_cooldown_z36_column", "${state.activity.emoji} ${stat…")
ui.define_spacer_zone("workout_cooldown_z40_spacer", "workout_cooldown_z36_column")
ui.define_box("workout_cooldown_z41_box", "workout_cooldown_z36_column", "V")
ui.define_box("workout_cooldown_z42_box", "workout_cooldown_z41_box", "V")
ui.define_text("workout_cooldown_z43_formattime_state", "workout_cooldown_z41_box", "formatTime(state.remainingSeco…")
ui.define_spacer_zone("workout_cooldown_z44_spacer", "workout_cooldown_z36_column")
ui.define_text("workout_cooldown_z45_state_activity_t", "workout_cooldown_z36_column", "state.activity.tagline")
ui.define_spacer_zone("workout_cooldown_z46_spacer", "workout_cooldown_z36_column")
ui.define_box("workout_cooldown_z47_row", "workout_cooldown_z36_column", "H")
ui.define_button("workout_cooldown_z48_1_min", "workout_cooldown_z47_row", "+1 min")
ui.define_spacer_zone("workout_cooldown_z49_spacer", "workout_cooldown_z47_row")
ui.define_button("workout_cooldown_z50_i_m_done", "workout_cooldown_z47_row", "I'm done")
ui.define_box("workout_cooldown_z51_conditioningfini", "workout_cooldown_z10_column", "V")
ui.define_box("workout_cooldown_z52_column", "workout_cooldown_z51_conditioningfini", "V")
ui.define_spacer_zone("workout_cooldown_z53_spacer", "workout_cooldown_z52_column")
ui.define_text("workout_cooldown_z54_x", "workout_cooldown_z52_column", "🌙")
ui.define_spacer_zone("workout_cooldown_z55_spacer", "workout_cooldown_z52_column")
ui.define_text("workout_cooldown_z56_nicely_done", "workout_cooldown_z52_column", "Nicely done")
ui.define_spacer_zone("workout_cooldown_z57_spacer", "workout_cooldown_z52_column")
ui.define_text("workout_cooldown_z58_it", "workout_cooldown_z52_column", "it")
ui.define_spacer_zone("workout_cooldown_z59_spacer", "workout_cooldown_z52_column")
ui.define_spacer_zone("workout_cooldown_z60_spacer", "workout_cooldown_z52_column")
ui.define_button("workout_cooldown_z61_finish", "workout_cooldown_z52_column", "Finish")
ui.define_spacer_zone("workout_cooldown_z62_spacer", "workout_cooldown_z52_column")
ui.define_box("workout_cooldown_z63_postworkoutcheck", "workout_cooldown_z51_conditioningfini", "V")
ui.define_box("workout_cooldown_z64_wflcard", "workout_cooldown_z63_postworkoutcheck", "V")
ui.define_box("workout_cooldown_z65_roundedcornersha", "workout_cooldown_z64_wflcard", "V")
ui.define_box("workout_cooldown_z66_borderstroke", "workout_cooldown_z64_wflcard", "V")
ui.define_box("workout_cooldown_z67_card", "workout_cooldown_z64_wflcard", "V")
ui.define_box("workout_cooldown_z68_card", "workout_cooldown_z64_wflcard", "V")
ui.define_box("workout_cooldown_z69_column", "workout_cooldown_z64_wflcard", "V")
ui.define_text("workout_cooldown_z70_how_are_you_feel", "workout_cooldown_z69_column", "How are you feeling?")
ui.define_text("workout_cooldown_z71_compared_to_when", "workout_cooldown_z69_column", "Compared to when you started")
ui.define_box("workout_cooldown_z72_row", "workout_cooldown_z69_column", "H")
ui.define_box("workout_cooldown_z73_surface", "workout_cooldown_z72_row", "V")
ui.define_box("workout_cooldown_z74_box", "workout_cooldown_z73_surface", "V")
ui.define_text("workout_cooldown_z75_label", "workout_cooldown_z74_box", "label")
ui.define_box("workout_cooldown_z76_topappbar", "workout_cooldown_z09_scaffold", "V")
ui.define_text("workout_cooldown_z77_cooldown_cooldow", "workout_cooldown_z76_topappbar", "Cooldown|Cooldown")
ui.define_icon("workout_cooldown_z78_back_to_workout_", "workout_cooldown_z76_topappbar", "Back to workout|Back to cooldo…")
ui.define_icon("workout_cooldown_z79_why_cool_down", "workout_cooldown_z76_topappbar", "Why cool down?")
```

## generated tree
  - Column[z00_scienceinfodialo]  <container>
    - Column[z01_alertdialog]  <container>
      - Button[Got it]  <leaf>
      - Text[Why cool down?]  <leaf>
      - Column[z04_column]  <container>
        - Text[ConditioningCatalog.COOLDOWN_W…]  <leaf>
        - Column[z06_column]  <container>
          - Text[note.heading]  <leaf>
          - Text[note.body]  <leaf>
  - Column[z09_scaffold]  <container>
    - Column[z10_column]  <container>
      - Column[z11_cooldownselectin]  <container>
        - Column[z12_column]  <container>
          - Spacer[z13_spacer]  <leaf>
          - Text[Take a few minutes to come dow…]  <leaf>
          - Text[Your muscles are warmest right…]  <leaf>
          - Column[z16_conditioningacti]  <container>
            - Column[z17_column]  <container>
              - Column[z18_activitycard]  <container>
                - Column[z19_surface]  <container>
                  - Row[z20_row]  <container>
                    - Text[activity.emoji]  <leaf>
                    - Spacer[z22_spacer]  <leaf>
                    - Column[z23_column]  <container>
                      - Row[z24_row]  <container>
                        - Text[activity.name]  <leaf>
                        - Spacer[z26_spacer]  <leaf>
                        - Text[formatMinutes(activity.default…]  <leaf>
                      - Text[activity.tagline]  <leaf>
                    - Spacer[z29_spacer]  <leaf>
                    - Column[z30_box]  <container>
                      - Icon[Start ${activity.name}]  <leaf>
          - Button[Forgot something? Back to work…]  <leaf>
          - Button[Done — wrap up]  <leaf>
          - Spacer[z34_spacer]  <leaf>
      - Column[z35_conditioningtime]  <container>
        - Column[z36_column]  <container>
          - Text[state.activity.phase.label()]  <leaf>
          - Spacer[z38_spacer]  <leaf>
          - Text[${state.activity.emoji} ${stat…]  <leaf>
          - Spacer[z40_spacer]  <leaf>
          - Column[z41_box]  <container>
            - Column[z42_box]  <leaf>
            - Text[formatTime(state.remainingSeco…]  <leaf>
          - Spacer[z44_spacer]  <leaf>
          - Text[state.activity.tagline]  <leaf>
          - Spacer[z46_spacer]  <leaf>
          - Row[z47_row]  <container>
            - Button[+1 min]  <leaf>
            - Spacer[z49_spacer]  <leaf>
            - Button[I'm done]  <leaf>
      - Column[z51_conditioningfini]  <container>
        - Column[z52_column]  <container>
          - Spacer[z53_spacer]  <leaf>
          - Text[🌙]  <leaf>
          - Spacer[z55_spacer]  <leaf>
          - Text[Nicely done]  <leaf>
          - Spacer[z57_spacer]  <leaf>
          - Text[it]  <leaf>
          - Spacer[z59_spacer]  <leaf>
          - Spacer[z60_spacer]  <leaf>
          - Button[Finish]  <leaf>
          - Spacer[z62_spacer]  <leaf>
        - Column[z63_postworkoutcheck]  <container>
          - Column[z64_wflcard]  <container>
            - Column[z65_roundedcornersha]  <leaf>
            - Column[z66_borderstroke]  <leaf>
            - Column[z67_card]  <leaf>
            - Column[z68_card]  <leaf>
            - Column[z69_column]  <container>
              - Text[How are you feeling?]  <leaf>
              - Text[Compared to when you started]  <leaf>
              - Row[z72_row]  <container>
                - Column[z73_surface]  <container>
                  - Column[z74_box]  <container>
                    - Text[label]  <leaf>
    - Column[z76_topappbar]  <container>
      - Text[Cooldown|Cooldown]  <leaf>
      - Icon[Back to workout|Back to cooldo…]  <leaf>
      - Icon[Why cool down?]  <leaf>

---
## verify vs Compose source (WorkoutCooldownScreen)
- distinct leaf signatures matched: 14/14 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 80 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (workout_cooldown_screen.py)
- leaf signatures shared:        4
- generated-only (other states / not in this trace): 10
- hand-built-only (helper glyphs / human representation): 0
    GEN-only I:Why cool down?
    GEN-only I:·DYN·
    GEN-only T:+1 min
    GEN-only T:Compared to when you started
    GEN-only T:Finish
    GEN-only T:Got it
    GEN-only T:How are you feeling?
    GEN-only T:I'm done
    GEN-only T:Nicely done
    GEN-only T:Why cool down?
