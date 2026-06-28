# UI layout ledger (KIT side) -- debug_panel

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

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

  ids:
    debug_panel/Row[0]
    debug_panel/Row[0]/Button[←]
    debug_panel/Row[0]/Column[1]
    debug_panel/Row[0]/Column[1]/Text[Debug panel]
    debug_panel/Text[Debug builds only. Shifts the …]
    debug_panel/Column[2]
    debug_panel/Column[2]/Text[Effective now]
    debug_panel/Column[2]/Text[Offset: +0 days · Programs in …]
    debug_panel/Text[Time travel]
    debug_panel/Row[4]
    debug_panel/Row[4]/Button[+1d]
    debug_panel/Row[4]/Button[+5d]
    debug_panel/Row[4]/Button[+1w]
    debug_panel/Row[4]/Button[+2w]
    debug_panel/Row[4]/Button[+1mo]
    debug_panel/Row[4]/Button[+1y]
    debug_panel/Row[4]/Button[-1d]
    debug_panel/Button[Reset to real time]
    debug_panel/Text[Activity seeding]
    debug_panel/Text[Then advance time to cross a g…]
    debug_panel/Button[Seed completed session (today)]
    debug_panel/Button[Seed completed session (20 day…]
    debug_panel/Button[Arm block-completion celebrati…]
    debug_panel/Button[Clear all sessions]
    debug_panel/Text[Life events (load overrides)]
    debug_panel/Button[Maintenance — 14 days]
    debug_panel/Button[Deload level — 14 days]
    debug_panel/Button[Snail's pace — 14 days]
    debug_panel/Button[Bodyweight-only — 7 days]
    debug_panel/Text[Connectivity / diagnostics]
    debug_panel/Button[Send test diagnostics (GitHub …]
    debug_panel/Button[Refresh DB info]
    debug_panel/Button[Check & repair program data]
    debug_panel/Button[Re-sync curated programs (keep…]
    debug_panel/Text[Danger zone]
    debug_panel/Button[Wipe & re-seed database]
    debug_panel/Button[Simulate crash (kills the app)]

---
## cross-side compare: Compose DebugPanelScreen <-> kit debug_panel
- STRUCTURAL leaf match (LCS, dynamic-aware): 33/50 Compose leaves aligned to kit (66%)
- static content matched (by literal): 30
    = +1d
    = +1mo
    = +1w
    = +1y
    = +2w
    = +5d
    = -1d
    = Activity seeding
    = Arm block-completion celebrati…
    = Bodyweight-only — 7 days
    = Check & repair program data
    = Clear all sessions
    = Connectivity / diagnostics
    = Danger zone
    = Debug builds only. Shifts the …
- Compose leaves NOT aligned: 17  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 11, kit-only 3)
