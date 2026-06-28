# UI layout ledger (KIT side) -- gym_list

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Gym profiles]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Column[1]  <container>   size: wrap(rel)  style=gym_card(abs)
    - Row[0]  <container>   size: wrap(rel)  style=gym_top(abs)
      - Text[Home Gym]  <leaf>   size: weight(1.0)(rel)  style=gym_name(abs)
      - Text[✓ Active]  <leaf>   size: wrap(rel)  style=chip_assist(abs)
    - Text[🏠 Home Gym]  <leaf>   size: wrap(rel)  style=gym_type(abs)
    - Text[Equipment]  <leaf>   size: wrap(rel)  style=gym_eq_hdr(abs)
    - Text[2 items]  <leaf>   size: wrap(rel)  style=gym_eq_count(abs)
    - Text[Equipment]  <leaf>   size: wrap(rel)  style=gym_eq_hdr(abs)
    - Text[Olympic Bar, Adjustable Dumbbe…]  <leaf>   size: wrap(rel)  style=gym_eq_names(abs)
    - Row[6]  <container>   size: wrap(rel)  style=gym_del_row(abs)
      - Button[Delete gym]  <leaf>   size: wrap(rel)  style=gym_del(abs)
  - Overlay[2]  <container>   size: wrap(rel)
    - Button[+]  <leaf>   size: wrap(rel)  style=fab(abs)

---
## cross-side compare: Compose GymListScreen <-> kit gym_list
- distinct widget signatures matched: 4/11 = 36%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
