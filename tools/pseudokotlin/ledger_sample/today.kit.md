# UI layout ledger (KIT side) -- today

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Column[0]  <container>   size: wrap(rel)  style=card(abs)
    - Row[0]  <container>   size: wrap(rel)  style=card_title_row(abs)
      - Text[This week's workouts]  <leaf>   size: weight(1.0)(rel)  style=card_title_lead(abs)
    - Text[Set up a program to see your w…]  <leaf>   size: wrap(rel)  style=note(abs)
  - Column[1]  <container>   size: wrap(rel)  style=card(abs)
    - Row[0]  <container>   size: wrap(rel)  style=card_title_row(abs)
      - Marker[0]  <leaf>   size: wrap(rel)
      - Text[1]  <leaf>   size: weight(1.0)(rel)  style=card_title_lead(abs)
    - Text[1]  <leaf>   size: wrap(rel)  style=card_body(abs)
    - Text[of 3 sessions this week]  <leaf>   size: wrap(rel)  style=note(abs)
    - Progress[3]  <leaf>   size: wrap(rel)
  - Text[No program enrolled yet. Head …]  <leaf>   size: wrap(rel)  style=note(abs)
  - Overlay[3]  <container>   size: wrap(rel)
    - Button[+]  <leaf>   size: wrap(rel)  style=fab(abs)

  ids:
    today/Column[0]
    today/Column[0]/Row[0]
    today/Column[0]/Row[0]/Text[This week's workouts]
    today/Column[0]/Text[Set up a program to see your w…]
    today/Column[1]
    today/Column[1]/Row[0]
    today/Column[1]/Row[0]/Marker[0]
    today/Column[1]/Row[0]/Text[1]
    today/Column[1]/Text[1]
    today/Column[1]/Text[of 3 sessions this week]
    today/Column[1]/Progress[3]
    today/Text[No program enrolled yet. Head …]
    today/Overlay[3]
    today/Overlay[3]/Button[+]

---
## cross-side compare: Compose TodayScreen <-> kit today
- STRUCTURAL leaf match (LCS, dynamic-aware): 5/165 Compose leaves aligned to kit (3%)
- static content matched (by literal): 3
    = No program enrolled yet. Head …
    = Set up a program to see your w…
    = This week's workouts
- Compose leaves NOT aligned: 160  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 72, kit-only 2)
