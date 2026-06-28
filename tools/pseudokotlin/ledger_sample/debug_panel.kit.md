# UI layout ledger (KIT side) -- debug_panel

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Debug panel]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Text[Debug builds only. Shifts the …]  <leaf>   size: wrap(rel)  style=note(abs)
  - Column[2]  <container>   size: wrap(rel)  style=card(abs)
    - Text[Effective now]  <leaf>   size: wrap(rel)  style=card_title(abs)
    - Text[Offset: +0 days · Programs in …]  <leaf>   size: wrap(rel)  style=card_body(abs)
  - Text[Time travel]  <leaf>   size: wrap(rel)  style=section_header(abs)
  - Row[4]  <container>   size: wrap(rel)  style=chip_row(abs)
    - Button[+1d]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[+5d]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[+1w]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[+2w]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[+1mo]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[+1y]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[-1d]  <leaf>   size: wrap(rel)  style=chip_off(abs)
  - Button[Reset to real time]  <leaf>   size: wrap(rel)  style=btn_outlined(abs)
  - Text[Activity seeding]  <leaf>   size: wrap(rel)  style=section_header(abs)
  - Text[Then advance time to cross a g…]  <leaf>   size: wrap(rel)  style=note(abs)
  - Button[Seed completed session (today)]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Button[Seed completed session (20 day…]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Button[Arm block-completion celebrati…]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Button[Clear all sessions]  <leaf>   size: wrap(rel)  style=btn_outlined(abs)
  - Text[Life events (load overrides)]  <leaf>   size: wrap(rel)  style=section_header(abs)
  - Button[Maintenance — 14 days]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Button[Deload level — 14 days]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Button[Snail's pace — 14 days]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Button[Bodyweight-only — 7 days]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Text[Connectivity / diagnostics]  <leaf>   size: wrap(rel)  style=section_header(abs)
  - Button[Send test diagnostics (GitHub …]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Button[Refresh DB info]  <leaf>   size: wrap(rel)  style=btn_outlined(abs)
  - Button[Check & repair program data]  <leaf>   size: wrap(rel)  style=btn_outlined(abs)
  - Button[Re-sync curated programs (keep…]  <leaf>   size: wrap(rel)  style=btn_outlined(abs)
  - Text[Danger zone]  <leaf>   size: wrap(rel)  style=section_header(abs)
  - Button[Wipe & re-seed database]  <leaf>   size: wrap(rel)  style=btn_outlined(abs)
  - Button[Simulate crash (kills the app)]  <leaf>   size: wrap(rel)  style=btn_outlined(abs)

---
## cross-side compare: Compose DebugPanelScreen <-> kit debug_panel
- distinct widget signatures matched: 31/36 = 86%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
