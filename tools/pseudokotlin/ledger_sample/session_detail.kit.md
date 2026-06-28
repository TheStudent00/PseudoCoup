# UI layout ledger (KIT side) -- session_detail

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Ad-hoc Workout]  <leaf>   size: wrap(rel)  style=tb_title(abs)
      - Text[Thu, Jan 1 at 12:00 AM]  <leaf>   size: wrap(rel)  style=tb_sub(abs)
  - Row[1]  <container>   size: wrap(rel)  style=stat_card_row(abs)
    - Column[0]  <container>   size: weight(1.0)(rel)  style=stat_card(abs)
      - Text[m]  <leaf>   size: wrap(rel)  style=stat_card_value(abs)
      - Text[Duration]  <leaf>   size: wrap(rel)  style=stat_card_label(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=stat_card(abs)
      - Text[0 kg]  <leaf>   size: wrap(rel)  style=stat_card_value(abs)
      - Text[Volume]  <leaf>   size: wrap(rel)  style=stat_card_label(abs)
    - Column[2]  <container>   size: weight(1.0)(rel)  style=stat_card(abs)
      - Text[0]  <leaf>   size: wrap(rel)  style=stat_card_value(abs)
      - Text[Exercises]  <leaf>   size: wrap(rel)  style=stat_card_label(abs)
  - Divider[2]  <leaf>   size: wrap(rel)
  - Text[Exercises]  <leaf>   size: wrap(rel)  style=section_header(abs)

  ids:
    session_detail/Row[0]
    session_detail/Row[0]/Button[←]
    session_detail/Row[0]/Column[1]
    session_detail/Row[0]/Column[1]/Text[Ad-hoc Workout]
    session_detail/Row[0]/Column[1]/Text[Thu, Jan 1 at 12:00 AM]
    session_detail/Row[1]
    session_detail/Row[1]/Column[0]
    session_detail/Row[1]/Column[0]/Text[m]
    session_detail/Row[1]/Column[0]/Text[Duration]
    session_detail/Row[1]/Column[1]
    session_detail/Row[1]/Column[1]/Text[0 kg]
    session_detail/Row[1]/Column[1]/Text[Volume]
    session_detail/Row[1]/Column[2]
    session_detail/Row[1]/Column[2]/Text[0]
    session_detail/Row[1]/Column[2]/Text[Exercises]
    session_detail/Divider[2]
    session_detail/Text[Exercises]

---
## cross-side compare: Compose SessionDetailScreen <-> kit session_detail
- STRUCTURAL leaf match (LCS, dynamic-aware): 10/35 Compose leaves aligned to kit (28%)
- static content matched (by literal): 4
    = Ad-hoc Workout
    = Duration
    = Exercises
    = Volume
- Compose leaves NOT aligned: 25  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 16, kit-only 5)
