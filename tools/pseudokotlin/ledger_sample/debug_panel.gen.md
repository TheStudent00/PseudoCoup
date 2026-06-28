# PseudoUI generated kit screen -- debug_panel  (from Compose DebugPanelScreen)

Mechanically generated from the Compose @Composable tree: each node mapped to a kit
define_* call with a content-anchored, referenceable zone id. NOT hand-written.

## generated define_* sequence  (62 calls)
```python
ui.define_box("debug_panel_z00_alertdialog", "content", "V")
ui.define_text("debug_panel_z01_wipe_re_seed_dat", "debug_panel_z00_alertdialog", "Wipe & re-seed database?")
ui.define_text("debug_panel_z02_this_erases_ever", "debug_panel_z00_alertdialog", "This erases everything — worko…")
ui.define_button("debug_panel_z03_export_wipe", "debug_panel_z00_alertdialog", "Export & wipe")
ui.define_box("debug_panel_z04_row", "debug_panel_z00_alertdialog", "H")
ui.define_button("debug_panel_z05_cancel", "debug_panel_z04_row", "Cancel")
ui.define_button("debug_panel_z06_wipe_no_backup", "debug_panel_z04_row", "Wipe, no backup")
ui.define_box("debug_panel_z07_column", "content", "V")
ui.define_text("debug_panel_z08_debug_panel", "debug_panel_z07_column", "Debug Panel")
ui.define_text("debug_panel_z09_debug_builds_onl", "debug_panel_z07_column", "Debug builds only. Shifts the …")
ui.define_box("debug_panel_z10_wflcard", "debug_panel_z07_column", "V")
ui.define_box("debug_panel_z11_roundedcornersha", "debug_panel_z10_wflcard", "V")
ui.define_box("debug_panel_z12_borderstroke", "debug_panel_z10_wflcard", "V")
ui.define_box("debug_panel_z13_card", "debug_panel_z10_wflcard", "V")
ui.define_box("debug_panel_z14_card", "debug_panel_z10_wflcard", "V")
ui.define_box("debug_panel_z15_column", "debug_panel_z10_wflcard", "V")
ui.define_text("debug_panel_z16_effective_now", "debug_panel_z15_column", "Effective now")
ui.define_text("debug_panel_z17_nowlabel", "debug_panel_z15_column", "nowLabel")
ui.define_text("debug_panel_z18_offset_if_offset", "debug_panel_z15_column", "Offset: ${if (offsetDays >= 0)…")
ui.define_text("debug_panel_z19_it", "debug_panel_z15_column", "it")
ui.define_text("debug_panel_z20_it", "debug_panel_z07_column", "it")
ui.define_box("debug_panel_z21_section", "debug_panel_z07_column", "V")
ui.define_text("debug_panel_z22_time_travel", "debug_panel_z21_section", "Time travel")
ui.define_box("debug_panel_z23_flowrow", "debug_panel_z07_column", "H")
ui.define_box("debug_panel_z24_chipbutton", "debug_panel_z23_flowrow", "V")
ui.define_button("debug_panel_z25_1d", "debug_panel_z24_chipbutton", "+1d")
ui.define_box("debug_panel_z26_chipbutton", "debug_panel_z23_flowrow", "V")
ui.define_button("debug_panel_z27_5d", "debug_panel_z26_chipbutton", "+5d")
ui.define_box("debug_panel_z28_chipbutton", "debug_panel_z23_flowrow", "V")
ui.define_button("debug_panel_z29_1w", "debug_panel_z28_chipbutton", "+1w")
ui.define_box("debug_panel_z30_chipbutton", "debug_panel_z23_flowrow", "V")
ui.define_button("debug_panel_z31_2w", "debug_panel_z30_chipbutton", "+2w")
ui.define_box("debug_panel_z32_chipbutton", "debug_panel_z23_flowrow", "V")
ui.define_button("debug_panel_z33_1mo", "debug_panel_z32_chipbutton", "+1mo")
ui.define_box("debug_panel_z34_chipbutton", "debug_panel_z23_flowrow", "V")
ui.define_button("debug_panel_z35_1y", "debug_panel_z34_chipbutton", "+1y")
ui.define_box("debug_panel_z36_chipbutton", "debug_panel_z23_flowrow", "V")
ui.define_button("debug_panel_z37_1d", "debug_panel_z36_chipbutton", "-1d")
ui.define_button("debug_panel_z38_reset_to_real_ti", "debug_panel_z07_column", "Reset to real time")
ui.define_box("debug_panel_z39_section", "debug_panel_z07_column", "V")
ui.define_text("debug_panel_z40_activity_seeding", "debug_panel_z39_section", "Activity seeding")
ui.define_text("debug_panel_z41_then_advance_tim", "debug_panel_z07_column", "Then advance time to cross a g…")
ui.define_button("debug_panel_z42_seed_completed_s", "debug_panel_z07_column", "Seed completed session (today)")
ui.define_button("debug_panel_z43_seed_completed_s", "debug_panel_z07_column", "Seed completed session (20 day…")
ui.define_button("debug_panel_z44_arm_block_comple", "debug_panel_z07_column", "Arm block-completion celebrati…")
ui.define_button("debug_panel_z45_clear_all_sessio", "debug_panel_z07_column", "Clear all sessions")
ui.define_box("debug_panel_z46_section", "debug_panel_z07_column", "V")
ui.define_text("debug_panel_z47_life_events_load", "debug_panel_z46_section", "Life events (load overrides)")
ui.define_button("debug_panel_z48_maintenance_14_d", "debug_panel_z07_column", "Maintenance — 14 days")
ui.define_button("debug_panel_z49_deload_level_14_", "debug_panel_z07_column", "Deload level — 14 days")
ui.define_button("debug_panel_z50_snail_s_pace_14_", "debug_panel_z07_column", "Snail's pace — 14 days")
ui.define_button("debug_panel_z51_bodyweight_only_", "debug_panel_z07_column", "Bodyweight-only — 7 days")
ui.define_box("debug_panel_z52_section", "debug_panel_z07_column", "V")
ui.define_text("debug_panel_z53_connectivity_dia", "debug_panel_z52_section", "Connectivity / diagnostics")
ui.define_button("debug_panel_z54_send_test_diagno", "debug_panel_z07_column", "Send test diagnostics (GitHub …")
ui.define_button("debug_panel_z55_refresh_db_info", "debug_panel_z07_column", "Refresh DB info")
ui.define_button("debug_panel_z56_check_repair_pro", "debug_panel_z07_column", "Check & repair program data")
ui.define_button("debug_panel_z57_re_sync_curated_", "debug_panel_z07_column", "Re-sync curated programs (keep…")
ui.define_box("debug_panel_z58_section", "debug_panel_z07_column", "V")
ui.define_text("debug_panel_z59_danger_zone", "debug_panel_z58_section", "Danger zone")
ui.define_button("debug_panel_z60_wipe_re_seed_dat", "debug_panel_z07_column", "Wipe & re-seed database")
ui.define_button("debug_panel_z61_simulate_crash_k", "debug_panel_z07_column", "Simulate crash (kills the app)")
```

## generated tree
  - Column[z00_alertdialog]  <container>
    - Text[Wipe & re-seed database?]  <leaf>
    - Text[This erases everything — worko…]  <leaf>
    - Button[Export & wipe]  <leaf>
    - Row[z04_row]  <container>
      - Button[Cancel]  <leaf>
      - Button[Wipe, no backup]  <leaf>
  - Column[z07_column]  <container>
    - Text[Debug Panel]  <leaf>
    - Text[Debug builds only. Shifts the …]  <leaf>
    - Column[z10_wflcard]  <container>
      - Column[z11_roundedcornersha]  <leaf>
      - Column[z12_borderstroke]  <leaf>
      - Column[z13_card]  <leaf>
      - Column[z14_card]  <leaf>
      - Column[z15_column]  <container>
        - Text[Effective now]  <leaf>
        - Text[nowLabel]  <leaf>
        - Text[Offset: ${if (offsetDays >= 0)…]  <leaf>
        - Text[it]  <leaf>
    - Text[it]  <leaf>
    - Column[z21_section]  <container>
      - Text[Time travel]  <leaf>
    - Row[z23_flowrow]  <container>
      - Column[z24_chipbutton]  <container>
        - Button[+1d]  <leaf>
      - Column[z26_chipbutton]  <container>
        - Button[+5d]  <leaf>
      - Column[z28_chipbutton]  <container>
        - Button[+1w]  <leaf>
      - Column[z30_chipbutton]  <container>
        - Button[+2w]  <leaf>
      - Column[z32_chipbutton]  <container>
        - Button[+1mo]  <leaf>
      - Column[z34_chipbutton]  <container>
        - Button[+1y]  <leaf>
      - Column[z36_chipbutton]  <container>
        - Button[-1d]  <leaf>
    - Button[Reset to real time]  <leaf>
    - Column[z39_section]  <container>
      - Text[Activity seeding]  <leaf>
    - Text[Then advance time to cross a g…]  <leaf>
    - Button[Seed completed session (today)]  <leaf>
    - Button[Seed completed session (20 day…]  <leaf>
    - Button[Arm block-completion celebrati…]  <leaf>
    - Button[Clear all sessions]  <leaf>
    - Column[z46_section]  <container>
      - Text[Life events (load overrides)]  <leaf>
    - Button[Maintenance — 14 days]  <leaf>
    - Button[Deload level — 14 days]  <leaf>
    - Button[Snail's pace — 14 days]  <leaf>
    - Button[Bodyweight-only — 7 days]  <leaf>
    - Column[z52_section]  <container>
      - Text[Connectivity / diagnostics]  <leaf>
    - Button[Send test diagnostics (GitHub …]  <leaf>
    - Button[Refresh DB info]  <leaf>
    - Button[Check & repair program data]  <leaf>
    - Button[Re-sync curated programs (keep…]  <leaf>
    - Column[z58_section]  <container>
      - Text[Danger zone]  <leaf>
    - Button[Wipe & re-seed database]  <leaf>
    - Button[Simulate crash (kills the app)]  <leaf>

---
## verify vs Compose source (DebugPanelScreen)
- distinct leaf signatures matched: 36/36 = 100%
- generated signatures NOT in Compose (fabricated): 0
- tree validity: 62 nodes, 0 orphan parents

---
## generated  <->  hand-built kit (debug_panel_screen.py)
- leaf signatures shared:        31
- generated-only (other states / not in this trace): 5
- hand-built-only (helper glyphs / human representation): 0
    GEN-only T:Cancel
    GEN-only T:Debug Panel
    GEN-only T:Export & wipe
    GEN-only T:Wipe & re-seed database?
    GEN-only T:Wipe, no backup
