# UI layout ledger (KIT side) -- log_cardio

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Log other exercise]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Text[Log cardio or other activity s…]  <leaf>   size: wrap(rel)  style=note(abs)
  - Text[Activity]  <leaf>   size: wrap(rel)  style=note(abs)
  - Row[3]  <container>   size: wrap(rel)  style=chip_row(abs)
    - Button[Run]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[Bike]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[Swim]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[Walk]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[Hike]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[Row]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[Elliptical]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[HIIT]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[Class]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[Sport]  <leaf>   size: wrap(rel)  style=chip_off(abs)
    - Button[Other]  <leaf>   size: wrap(rel)  style=chip_off(abs)
  - Text[When]  <leaf>   size: wrap(rel)  style=note(abs)
  - Button[Today]  <leaf>   size: wrap(rel)  style=btn_outlined(abs)
  - Text[Duration (minutes)]  <leaf>   size: wrap(rel)  style=note(abs)
  - TextField[Minutes]  <leaf>   size: wrap(rel)
  - Text[Intensity]  <leaf>   size: wrap(rel)  style=note(abs)
  - Row[9]  <container>   size: wrap(rel)  style=seg_row(abs)
    - Button[Low]  <leaf>   size: wrap(rel)  style=seg_first_off(abs)
    - Button[Moderate]  <leaf>   size: wrap(rel)  style=seg_mid_off(abs)
    - Button[High]  <leaf>   size: wrap(rel)  style=seg_last_off(abs)
  - Column[10]  <container>   size: wrap(rel)  style=labeled_field(abs)
    - Text[Distance (km)]  <leaf>   size: wrap(rel)  style=field_label(abs)
    - TextField[Distance]  <leaf>   size: wrap(rel)
  - Column[11]  <container>   size: wrap(rel)  style=labeled_field(abs)
    - Text[Avg HR (bpm)]  <leaf>   size: wrap(rel)  style=field_label(abs)
    - TextField[Avg HR]  <leaf>   size: wrap(rel)
  - Text[Notes (optional)]  <leaf>   size: wrap(rel)  style=note(abs)
  - TextField[Notes]  <leaf>   size: wrap(rel)
  - Button[Save]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Zone[15]  <leaf>   size: wrap(rel)

  ids:
    log_cardio/Row[0]
    log_cardio/Row[0]/Button[←]
    log_cardio/Row[0]/Column[1]
    log_cardio/Row[0]/Column[1]/Text[Log other exercise]
    log_cardio/Text[Log cardio or other activity s…]
    log_cardio/Text[Activity]
    log_cardio/Row[3]
    log_cardio/Row[3]/Button[Run]
    log_cardio/Row[3]/Button[Bike]
    log_cardio/Row[3]/Button[Swim]
    log_cardio/Row[3]/Button[Walk]
    log_cardio/Row[3]/Button[Hike]
    log_cardio/Row[3]/Button[Row]
    log_cardio/Row[3]/Button[Elliptical]
    log_cardio/Row[3]/Button[HIIT]
    log_cardio/Row[3]/Button[Class]
    log_cardio/Row[3]/Button[Sport]
    log_cardio/Row[3]/Button[Other]
    log_cardio/Text[When]
    log_cardio/Button[Today]
    log_cardio/Text[Duration (minutes)]
    log_cardio/TextField[Minutes]
    log_cardio/Text[Intensity]
    log_cardio/Row[9]
    log_cardio/Row[9]/Button[Low]
    log_cardio/Row[9]/Button[Moderate]
    log_cardio/Row[9]/Button[High]
    log_cardio/Column[10]
    log_cardio/Column[10]/Text[Distance (km)]
    log_cardio/Column[10]/TextField[Distance]
    log_cardio/Column[11]
    log_cardio/Column[11]/Text[Avg HR (bpm)]
    log_cardio/Column[11]/TextField[Avg HR]
    log_cardio/Text[Notes (optional)]
    log_cardio/TextField[Notes]
    log_cardio/Button[Save]
    log_cardio/Zone[15]

---
## cross-side compare: Compose LogCardioScreen <-> kit log_cardio
- STRUCTURAL leaf match (LCS, dynamic-aware): 15/30 Compose leaves aligned to kit (50%)
- static content matched (by literal): 10
    = Activity
    = Avg HR (bpm)
    = Distance (km)
    = Duration (minutes)
    = Intensity
    = Log cardio or other activity s…
    = Log other exercise
    = Notes (optional)
    = Save
    = When
- Compose leaves NOT aligned: 15  ·  kit leaves not aligned: 15
- (raw content-anchor only: Compose-only 13, kit-only 20)
