# UI layout ledger (KIT side) -- programs

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Programs]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Text[Active]  <leaf>   size: wrap(rel)  style=section_header(abs)
  - Column[2]  <container>   size: wrap(rel)  style=prog_card_active(abs)
    - Row[0]  <container>   size: wrap(rel)  style=prog_top(abs)
      - Text[3-Day Full Body — Ground Up]  <leaf>   size: weight(1.0)(rel)  style=prog_name(abs)
      - Text[Active]  <leaf>   size: wrap(rel)  style=outline_pill(abs)
    - Row[1]  <container>   size: wrap(rel)  style=prog_pill_row(abs)
      - Text[Ground Up]  <leaf>   size: wrap(rel)  style=outline_pill(abs)
    - Text[Three macrocycles that walk a …]  <leaf>   size: wrap(rel)  style=prog_desc(abs)
  - Column[3]  <container>   size: wrap(rel)  style=prog_card(abs)
    - Row[0]  <container>   size: wrap(rel)  style=prog_top(abs)
      - Text[Hypertrophy Base]  <leaf>   size: weight(1.0)(rel)  style=prog_name(abs)
    - Row[1]  <container>   size: wrap(rel)  style=prog_pill_row(abs)
      - Text[General Fitness]  <leaf>   size: wrap(rel)  style=outline_pill(abs)
    - Text[4-day upper/lower hypertrophy …]  <leaf>   size: wrap(rel)  style=prog_desc(abs)
    - Column[3]  <container>   size: wrap(rel)  style=prog_swap_wrap(abs)
      - Button[Swap for this program]  <leaf>   size: wrap(rel)  style=tonal(abs)
    - Button[⋮]  <leaf>   size: wrap(rel)  style=prog_menu(abs)
  - Column[4]  <container>   size: wrap(rel)  style=prog_card(abs)
    - Row[0]  <container>   size: wrap(rel)  style=prog_top(abs)
      - Text[Strength Starter]  <leaf>   size: weight(1.0)(rel)  style=prog_name(abs)
    - Row[1]  <container>   size: wrap(rel)  style=prog_pill_row(abs)
      - Text[Strength Foundations]  <leaf>   size: wrap(rel)  style=outline_pill(abs)
    - Text[A 3-day per week intro strengt…]  <leaf>   size: wrap(rel)  style=prog_desc(abs)
    - Column[3]  <container>   size: wrap(rel)  style=prog_swap_wrap(abs)
      - Button[Swap for this program]  <leaf>   size: wrap(rel)  style=tonal(abs)
    - Button[⋮]  <leaf>   size: wrap(rel)  style=prog_menu(abs)
  - Overlay[5]  <container>   size: wrap(rel)
    - Button[+]  <leaf>   size: wrap(rel)  style=fab(abs)

---
## cross-side compare: Compose ProgramsScreen <-> kit programs
- distinct widget signatures matched: 3/20 = 15%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
