# UI layout ledger (KIT side) -- gym_create_wizard

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Add new gym]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Column[1]  <container>   size: wrap(rel)
    - Text[Tell us about your gym]  <leaf>   size: wrap(rel)  style=wiz_title(abs)
    - Text[We'll pre-load the most common…]  <leaf>   size: wrap(rel)  style=note(abs)
    - Column[2]  <container>   size: wrap(rel)  style=labeled_field(abs)
      - Text[Gym name]  <leaf>   size: wrap(rel)  style=field_label(abs)
      - TextField[1]  <leaf>   size: wrap(rel)
    - Row[3]  <container>   size: wrap(rel)  style=selection_card(abs)
      - Text[🏠]  <leaf>   size: wrap(rel)  style=sel_emoji(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)  style=sel_col(abs)
        - Text[Home Gym]  <leaf>   size: wrap(rel)  style=sel_title(abs)
        - Text[Equipment you own or share a s…]  <leaf>   size: wrap(rel)  style=sel_sub(abs)
    - Row[4]  <container>   size: wrap(rel)  style=selection_card(abs)
      - Text[🏢]  <leaf>   size: wrap(rel)  style=sel_emoji(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)  style=sel_col(abs)
        - Text[Big Box Gym]  <leaf>   size: wrap(rel)  style=sel_title(abs)
        - Text[Chains, full rack rooms, cardi…]  <leaf>   size: wrap(rel)  style=sel_sub(abs)
    - Row[5]  <container>   size: wrap(rel)  style=selection_card(abs)
      - Text[🏋]  <leaf>   size: wrap(rel)  style=sel_emoji(abs)
      - Column[1]  <container>   size: weight(1.0)(rel)  style=sel_col(abs)
        - Text[Strength Gym]  <leaf>   size: wrap(rel)  style=sel_title(abs)
        - Text[Lifting-focused. Chalk probabl…]  <leaf>   size: wrap(rel)  style=sel_sub(abs)
  - Zone[2]  <leaf>   size: wrap(rel)

---
## cross-side compare: Compose GymCreateWizardScreen <-> kit gym_create_wizard
- distinct widget signatures matched: 5/9 = 55%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
