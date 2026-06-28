# UI layout ledger (KIT side) -- exercise_picker

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Add exercise]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No day selected]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[Go back and try again.]  <leaf>   size: wrap(rel)  style=empty_body(abs)

---
## cross-side compare: Compose ExercisePickerScreen <-> kit exercise_picker
- distinct widget signatures matched: 2/8 = 25%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 0
