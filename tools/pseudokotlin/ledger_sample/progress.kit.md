# UI layout ledger (KIT side) -- progress

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=tab_row(abs)
    - Column[0]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[Analytics]  <leaf>   size: wrap(rel)  style=tab_on(abs)
      - Marker[1]  <leaf>   size: wrap(rel)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[Bests]  <leaf>   size: wrap(rel)  style=tab_off(abs)
    - Column[2]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[History]  <leaf>   size: wrap(rel)  style=tab_off(abs)
  - Column[1]  <container>   size: wrap(rel)  style=card(abs)
    - Row[0]  <container>   size: wrap(rel)  style=card_title_row(abs)
      - Text[Your wins]  <leaf>   size: weight(1.0)(rel)  style=card_title_lead(abs)
    - Row[1]  <container>   size: wrap(rel)  style=wins_row(abs)
      - Column[0]  <container>   size: wrap(rel)  style=wins_donut(abs)
        - Marker[0]  <leaf>   size: wrap(rel)
        - Text[2]  <leaf>   size: wrap(rel)  style=wins_donut_count(abs)
        - Text[wins]  <leaf>   size: wrap(rel)  style=wins_donut_unit(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)  style=wins_col(abs)
        - Text[More than the numbers — the re…]  <leaf>   size: wrap(rel)  style=wins_body(abs)
        - Column[1]  <container>   size: wrap(rel)  style=wins_btn_wrap(abs)
          - Button[Log a win]  <leaf>   size: wrap(rel)  style=btn_filled(abs)
  - Text[Log your first workout to see …]  <leaf>   size: wrap(rel)  style=note(abs)

---
## cross-side compare: Compose ProgressScreen <-> kit progress
- distinct widget signatures matched: 5/28 = 17%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
