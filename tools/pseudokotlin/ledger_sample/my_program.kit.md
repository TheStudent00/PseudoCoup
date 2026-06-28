# UI layout ledger (KIT side) -- my_program

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Column[0]  <container>   size: wrap(rel)  style=prog_header(abs)
    - Row[0]  <container>   size: wrap(rel)  style=prog_hdr_row(abs)
      - Text[0]  <leaf>   size: weight(1.0)(rel)  style=prog_hdr_title(abs)
      - Text[Enrolled]  <leaf>   size: wrap(rel)  style=enrolled_badge(abs)
  - Row[1]  <container>   size: wrap(rel)  style=rr_row_d0(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[0]  <leaf>   size: wrap(rel)  style=rr_title_macro(abs)
      - Text[— 4 weeks]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[2]  <container>   size: wrap(rel)  style=rr_row_d1(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Mesocycle 0 · Accumulation]  <leaf>   size: wrap(rel)  style=rr_title_phase(abs)
      - Text[— 2 weeks]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[3]  <container>   size: wrap(rel)  style=rr_row_d2(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Week 0]  <leaf>   size: wrap(rel)  style=rr_title_week_cur(abs)
      - Text[Progression]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[4]  <container>   size: wrap(rel)  style=rr_row_d2(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Week 0]  <leaf>   size: wrap(rel)  style=rr_title_week(abs)
      - Text[Progression]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[5]  <container>   size: wrap(rel)  style=rr_row_d1(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Mesocycle 0 · Accumulation]  <leaf>   size: wrap(rel)  style=rr_title_phase(abs)
      - Text[— 2 weeks]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[6]  <container>   size: wrap(rel)  style=rr_row_d2(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Week 0]  <leaf>   size: wrap(rel)  style=rr_title_week(abs)
      - Text[Progression]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[7]  <container>   size: wrap(rel)  style=rr_row_d2(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Week 0]  <leaf>   size: wrap(rel)  style=rr_title_week(abs)
      - Text[Progression]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[8]  <container>   size: wrap(rel)  style=rr_row_d0(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[0]  <leaf>   size: wrap(rel)  style=rr_title_macro(abs)
      - Text[— 4 weeks]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[9]  <container>   size: wrap(rel)  style=rr_row_d1(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Mesocycle 0 · Accumulation]  <leaf>   size: wrap(rel)  style=rr_title_phase(abs)
      - Text[— 2 weeks]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[10]  <container>   size: wrap(rel)  style=rr_row_d2(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Week 0]  <leaf>   size: wrap(rel)  style=rr_title_week(abs)
      - Text[Progression]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[11]  <container>   size: wrap(rel)  style=rr_row_d2(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Week 0]  <leaf>   size: wrap(rel)  style=rr_title_week(abs)
      - Text[Progression]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[12]  <container>   size: wrap(rel)  style=rr_row_d1(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Mesocycle 0 · Accumulation]  <leaf>   size: wrap(rel)  style=rr_title_phase(abs)
      - Text[— 2 weeks]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[13]  <container>   size: wrap(rel)  style=rr_row_d2(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Week 0]  <leaf>   size: wrap(rel)  style=rr_title_week(abs)
      - Text[Progression]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Row[14]  <container>   size: wrap(rel)  style=rr_row_d2(abs)
    - Column[0]  <container>   size: wrap(rel)  style=rr_gutter(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Marker[1]  <leaf>   size: wrap(rel)
      - Marker[2]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=rr_content(abs)
      - Text[Week 0]  <leaf>   size: wrap(rel)  style=rr_title_week(abs)
      - Text[Progression]  <leaf>   size: wrap(rel)  style=rr_sub(abs)
  - Button[View other programs]  <leaf>   size: wrap(rel)  style=btn_outlined(abs)
  - Overlay[16]  <container>   size: wrap(rel)
    - Button[+]  <leaf>   size: wrap(rel)  style=fab(abs)

  ids:
    my_program/Column[0]
    my_program/Column[0]/Row[0]
    my_program/Column[0]/Row[0]/Text[0]
    my_program/Column[0]/Row[0]/Text[Enrolled]
    my_program/Row[1]
    my_program/Row[1]/Column[0]
    my_program/Row[1]/Column[0]/Marker[0]
    my_program/Row[1]/Column[0]/Marker[1]
    my_program/Row[1]/Column[0]/Marker[2]
    my_program/Row[1]/Column[1]
    my_program/Row[1]/Column[1]/Text[0]
    my_program/Row[1]/Column[1]/Text[— 4 weeks]
    my_program/Row[2]
    my_program/Row[2]/Column[0]
    my_program/Row[2]/Column[0]/Marker[0]
    my_program/Row[2]/Column[0]/Marker[1]
    my_program/Row[2]/Column[0]/Marker[2]
    my_program/Row[2]/Column[1]
    my_program/Row[2]/Column[1]/Text[Mesocycle 0 · Accumulation]
    my_program/Row[2]/Column[1]/Text[— 2 weeks]
    my_program/Row[3]
    my_program/Row[3]/Column[0]
    my_program/Row[3]/Column[0]/Marker[0]
    my_program/Row[3]/Column[0]/Marker[1]
    my_program/Row[3]/Column[0]/Marker[2]
    my_program/Row[3]/Column[1]
    my_program/Row[3]/Column[1]/Text[Week 0]
    my_program/Row[3]/Column[1]/Text[Progression]
    my_program/Row[4]
    my_program/Row[4]/Column[0]
    my_program/Row[4]/Column[0]/Marker[0]
    my_program/Row[4]/Column[0]/Marker[1]
    my_program/Row[4]/Column[0]/Marker[2]
    my_program/Row[4]/Column[1]
    my_program/Row[4]/Column[1]/Text[Week 0]
    my_program/Row[4]/Column[1]/Text[Progression]
    my_program/Row[5]
    my_program/Row[5]/Column[0]
    my_program/Row[5]/Column[0]/Marker[0]
    my_program/Row[5]/Column[0]/Marker[1]
    my_program/Row[5]/Column[0]/Marker[2]
    my_program/Row[5]/Column[1]
    my_program/Row[5]/Column[1]/Text[Mesocycle 0 · Accumulation]
    my_program/Row[5]/Column[1]/Text[— 2 weeks]
    my_program/Row[6]
    my_program/Row[6]/Column[0]
    my_program/Row[6]/Column[0]/Marker[0]
    my_program/Row[6]/Column[0]/Marker[1]
    my_program/Row[6]/Column[0]/Marker[2]
    my_program/Row[6]/Column[1]
    my_program/Row[6]/Column[1]/Text[Week 0]
    my_program/Row[6]/Column[1]/Text[Progression]
    my_program/Row[7]
    my_program/Row[7]/Column[0]
    my_program/Row[7]/Column[0]/Marker[0]
    my_program/Row[7]/Column[0]/Marker[1]
    my_program/Row[7]/Column[0]/Marker[2]
    my_program/Row[7]/Column[1]
    my_program/Row[7]/Column[1]/Text[Week 0]
    my_program/Row[7]/Column[1]/Text[Progression]
    my_program/Row[8]
    my_program/Row[8]/Column[0]
    my_program/Row[8]/Column[0]/Marker[0]
    my_program/Row[8]/Column[0]/Marker[1]
    my_program/Row[8]/Column[0]/Marker[2]
    my_program/Row[8]/Column[1]
    my_program/Row[8]/Column[1]/Text[0]
    my_program/Row[8]/Column[1]/Text[— 4 weeks]
    my_program/Row[9]
    my_program/Row[9]/Column[0]
    my_program/Row[9]/Column[0]/Marker[0]
    my_program/Row[9]/Column[0]/Marker[1]
    my_program/Row[9]/Column[0]/Marker[2]
    my_program/Row[9]/Column[1]
    my_program/Row[9]/Column[1]/Text[Mesocycle 0 · Accumulation]
    my_program/Row[9]/Column[1]/Text[— 2 weeks]
    my_program/Row[10]
    my_program/Row[10]/Column[0]
    my_program/Row[10]/Column[0]/Marker[0]
    my_program/Row[10]/Column[0]/Marker[1]
    my_program/Row[10]/Column[0]/Marker[2]
    my_program/Row[10]/Column[1]
    my_program/Row[10]/Column[1]/Text[Week 0]
    my_program/Row[10]/Column[1]/Text[Progression]
    my_program/Row[11]
    my_program/Row[11]/Column[0]
    my_program/Row[11]/Column[0]/Marker[0]
    my_program/Row[11]/Column[0]/Marker[1]
    my_program/Row[11]/Column[0]/Marker[2]
    my_program/Row[11]/Column[1]
    my_program/Row[11]/Column[1]/Text[Week 0]
    my_program/Row[11]/Column[1]/Text[Progression]
    my_program/Row[12]
    my_program/Row[12]/Column[0]
    my_program/Row[12]/Column[0]/Marker[0]
    my_program/Row[12]/Column[0]/Marker[1]
    my_program/Row[12]/Column[0]/Marker[2]
    my_program/Row[12]/Column[1]
    my_program/Row[12]/Column[1]/Text[Mesocycle 0 · Accumulation]
    my_program/Row[12]/Column[1]/Text[— 2 weeks]
    my_program/Row[13]
    my_program/Row[13]/Column[0]
    my_program/Row[13]/Column[0]/Marker[0]
    my_program/Row[13]/Column[0]/Marker[1]
    my_program/Row[13]/Column[0]/Marker[2]
    my_program/Row[13]/Column[1]
    my_program/Row[13]/Column[1]/Text[Week 0]
    my_program/Row[13]/Column[1]/Text[Progression]
    my_program/Row[14]
    my_program/Row[14]/Column[0]
    my_program/Row[14]/Column[0]/Marker[0]
    my_program/Row[14]/Column[0]/Marker[1]
    my_program/Row[14]/Column[0]/Marker[2]
    my_program/Row[14]/Column[1]
    my_program/Row[14]/Column[1]/Text[Week 0]
    my_program/Row[14]/Column[1]/Text[Progression]
    my_program/Button[View other programs]
    my_program/Overlay[16]
    my_program/Overlay[16]/Button[+]

---
## cross-side compare: Compose MyProgramScreen <-> kit my_program
- STRUCTURAL leaf match (LCS, dynamic-aware): 29/82 Compose leaves aligned to kit (35%)
- static content matched (by literal): 2
    = Enrolled
    = View other programs
- Compose leaves NOT aligned: 53  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 43, kit-only 6)
