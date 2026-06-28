# UI layout ledger (KIT side) -- log_cardio

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Log other exercise]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Text[Log cardio or other activity s…]  <leaf>   size: wrap(rel)  style=note(abs)
  - Text[Activity]  <leaf>   size: wrap(rel)  style=note(abs)
  - Row[3]  <container>   size: wrap(rel)  style=chip_row(abs)
    - Button[Run]  <leaf>   size: wrap(rel)  style=chip_on(abs)
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
    - Button[Moderate]  <leaf>   size: wrap(rel)  style=seg_mid_on(abs)
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

---
## cross-side compare: Compose LogCardioScreen <-> kit log_cardio
- distinct widget signatures matched: 10/17 = 58%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 1
    PY  F:·DYN·
