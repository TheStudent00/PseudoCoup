# UI layout ledger (KIT side) -- gym_list

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Gym profiles]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Column[1]  <container>   size: wrap(rel)  style=gym_card(abs)
    - Row[0]  <container>   size: wrap(rel)  style=gym_top(abs)
      - Text[Commercial Gym]  <leaf>   size: weight(1.0)(rel)  style=gym_name(abs)
      - Button[Set active]  <leaf>   size: wrap(rel)  style=gym_chip_inactive(abs)
    - Text[🏢 Big Box Gym]  <leaf>   size: wrap(rel)  style=gym_type(abs)
    - Text[Equipment]  <leaf>   size: wrap(rel)  style=gym_eq_hdr(abs)
    - Text[0 items]  <leaf>   size: wrap(rel)  style=gym_eq_count(abs)
    - Text[No equipment listed]  <leaf>   size: wrap(rel)  style=gym_eq_names(abs)
    - Row[5]  <container>   size: wrap(rel)  style=gym_del_row(abs)
      - Button[Delete gym]  <leaf>   size: wrap(rel)  style=gym_del(abs)
  - Column[2]  <container>   size: wrap(rel)  style=gym_card(abs)
    - Row[0]  <container>   size: wrap(rel)  style=gym_top(abs)
      - Text[Home Gym]  <leaf>   size: weight(1.0)(rel)  style=gym_name(abs)
      - Text[✓ Active]  <leaf>   size: wrap(rel)  style=chip_assist(abs)
    - Text[🏠 Home Gym]  <leaf>   size: wrap(rel)  style=gym_type(abs)
    - Text[Equipment]  <leaf>   size: wrap(rel)  style=gym_eq_hdr(abs)
    - Text[0 items]  <leaf>   size: wrap(rel)  style=gym_eq_count(abs)
    - Text[No equipment listed]  <leaf>   size: wrap(rel)  style=gym_eq_names(abs)
    - Row[5]  <container>   size: wrap(rel)  style=gym_del_row(abs)
      - Button[Delete gym]  <leaf>   size: wrap(rel)  style=gym_del(abs)
  - Overlay[3]  <container>   size: wrap(rel)
    - Button[+]  <leaf>   size: wrap(rel)  style=fab(abs)

  ids:
    gym_list/Row[0]
    gym_list/Row[0]/Button[←]
    gym_list/Row[0]/Column[1]
    gym_list/Row[0]/Column[1]/Text[Gym profiles]
    gym_list/Column[1]
    gym_list/Column[1]/Row[0]
    gym_list/Column[1]/Row[0]/Text[Commercial Gym]
    gym_list/Column[1]/Row[0]/Button[Set active]
    gym_list/Column[1]/Text[🏢 Big Box Gym]
    gym_list/Column[1]/Text[Equipment]
    gym_list/Column[1]/Text[0 items]
    gym_list/Column[1]/Text[No equipment listed]
    gym_list/Column[1]/Row[5]
    gym_list/Column[1]/Row[5]/Button[Delete gym]
    gym_list/Column[2]
    gym_list/Column[2]/Row[0]
    gym_list/Column[2]/Row[0]/Text[Home Gym]
    gym_list/Column[2]/Row[0]/Text[✓ Active]
    gym_list/Column[2]/Text[🏠 Home Gym]
    gym_list/Column[2]/Text[Equipment]
    gym_list/Column[2]/Text[0 items]
    gym_list/Column[2]/Text[No equipment listed]
    gym_list/Column[2]/Row[5]
    gym_list/Column[2]/Row[5]/Button[Delete gym]
    gym_list/Overlay[3]
    gym_list/Overlay[3]/Button[+]

---
## cross-side compare: Compose GymListScreen <-> kit gym_list
- STRUCTURAL leaf match (LCS, dynamic-aware): 16/30 Compose leaves aligned to kit (53%)
- static content matched (by literal): 5
    = Delete gym
    = Equipment
    = Gym profiles
    = No equipment listed
    = Set active
- Compose leaves NOT aligned: 14  ·  kit leaves not aligned: 1
- (raw content-anchor only: Compose-only 11, kit-only 8)
