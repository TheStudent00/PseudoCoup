# UI layout ledger (KIT side) -- exercise_picker

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Add exercise]  <leaf>   size: wrap(rel)  style=tb_title(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No day selected]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[Go back and try again.]  <leaf>   size: wrap(rel)  style=empty_body(abs)

  ids:
    exercise_picker/Row[0]
    exercise_picker/Row[0]/Button[←]
    exercise_picker/Row[0]/Column[1]
    exercise_picker/Row[0]/Column[1]/Text[Add exercise]
    exercise_picker/Column[1]
    exercise_picker/Column[1]/Text[No day selected]
    exercise_picker/Column[1]/Text[Go back and try again.]

---
## cross-side compare: Compose ExercisePickerScreen <-> kit exercise_picker
- STRUCTURAL leaf match (LCS, dynamic-aware): 4/13 Compose leaves aligned to kit (30%)
- static content matched (by literal): 1
    = Add exercise
- Compose leaves NOT aligned: 9  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 9, kit-only 3)
