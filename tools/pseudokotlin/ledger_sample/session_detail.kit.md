# UI layout ledger (KIT side) -- session_detail

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Ad-hoc Workout]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Row[1]  <container>   size: wrap(rel)  style=stat_card_row(abs)
    - Column[0]  <container>   size: weight(1.0)(rel)  style=stat_card(abs)
      - Text[—]  <leaf>   size: wrap(rel)  style=stat_card_value(abs)
      - Text[Duration]  <leaf>   size: wrap(rel)  style=stat_card_label(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=stat_card(abs)
      - Text[0 kg]  <leaf>   size: wrap(rel)  style=stat_card_value(abs)
      - Text[Volume]  <leaf>   size: wrap(rel)  style=stat_card_label(abs)
    - Column[2]  <container>   size: weight(1.0)(rel)  style=stat_card(abs)
      - Text[0]  <leaf>   size: wrap(rel)  style=stat_card_value(abs)
      - Text[Exercises]  <leaf>   size: wrap(rel)  style=stat_card_label(abs)
  - Divider[2]  <leaf>   size: wrap(rel)
  - Text[Exercises]  <leaf>   size: wrap(rel)  style=section_header(abs)

---
## cross-side compare: Compose SessionDetailScreen <-> kit session_detail
- distinct widget signatures matched: 4/7 = 57%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
