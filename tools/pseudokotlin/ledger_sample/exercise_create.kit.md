# UI layout ledger (KIT side) -- exercise_create

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[New exercise]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[Save]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Column[1]  <container>   size: wrap(rel)  style=labeled_field(abs)
    - Text[Exercise name]  <leaf>   size: wrap(rel)  style=field_label(abs)
    - TextField[Name]  <leaf>   size: wrap(rel)
  - Text[Primary muscles *]  <leaf>   size: wrap(rel)  style=note(abs)
  - Row[3]  <container>   size: wrap(rel)  style=dropdown_field(abs)
    - Text[Select muscles]  <leaf>   size: weight(1.0)(rel)  style=dropdown_ph(abs)
    - Text[▾]  <leaf>   size: wrap(rel)  style=dropdown_caret(abs)
  - Text[Secondary muscles]  <leaf>   size: wrap(rel)  style=note(abs)
  - Row[5]  <container>   size: wrap(rel)  style=dropdown_field(abs)
    - Text[Select muscles]  <leaf>   size: weight(1.0)(rel)  style=dropdown_ph(abs)
    - Text[▾]  <leaf>   size: wrap(rel)  style=dropdown_caret(abs)
  - Column[6]  <container>   size: wrap(rel)  style=labeled_field(abs)
    - Text[Movement pattern]  <leaf>   size: wrap(rel)  style=field_label(abs)
    - Row[1]  <container>   size: wrap(rel)  style=dropdown_field(abs)
      - Text[Push Horizontal]  <leaf>   size: weight(1.0)(rel)  style=dropdown_value(abs)
      - Text[▾]  <leaf>   size: wrap(rel)  style=dropdown_caret(abs)
  - Column[7]  <container>   size: wrap(rel)  style=labeled_field(abs)
    - Text[Equipment]  <leaf>   size: wrap(rel)  style=field_label(abs)
    - Row[1]  <container>   size: wrap(rel)  style=dropdown_field(abs)
      - Text[Barbell]  <leaf>   size: weight(1.0)(rel)  style=dropdown_value(abs)
      - Text[▾]  <leaf>   size: wrap(rel)  style=dropdown_caret(abs)
  - Row[8]  <container>   size: wrap(rel)  style=switch_row(abs)
    - Row[0]  <container>   size: weight(1.0)(rel)  style=switch_row(abs)
      - Text[Unilateral]  <leaf>   size: weight(1.0)(rel)  style=switch_label(abs)
      - Row[1]  <container>   size: wrap(rel)  style=toggle_track_off(abs)
        - Marker[0]  <leaf>   size: wrap(rel)
        - Text[1]  <leaf>   size: weight(1.0)(rel)
    - Row[1]  <container>   size: weight(1.0)(rel)  style=switch_row(abs)
      - Text[Compound]  <leaf>   size: weight(1.0)(rel)  style=switch_label(abs)
      - Row[1]  <container>   size: wrap(rel)  style=toggle_track_off(abs)
        - Marker[0]  <leaf>   size: wrap(rel)
        - Text[1]  <leaf>   size: weight(1.0)(rel)
  - Column[9]  <container>   size: wrap(rel)  style=labeled_field(abs)
    - Text[Base starting weight on (optio…]  <leaf>   size: wrap(rel)  style=field_label(abs)
    - Row[1]  <container>   size: wrap(rel)  style=dropdown_field(abs)
      - Text[None — start light]  <leaf>   size: weight(1.0)(rel)  style=dropdown_value(abs)
      - Text[▾]  <leaf>   size: wrap(rel)  style=dropdown_caret(abs)
  - Text[For a new movement, we'll star…]  <leaf>   size: wrap(rel)  style=note(abs)
  - TextField[Form notes (optional)]  <leaf>   size: wrap(rel)
  - TextField[Coaching cues (optional)]  <leaf>   size: wrap(rel)
  - Column[13]  <container>   size: wrap(rel)  style=labeled_field(abs)
    - Text[Video link (optional)]  <leaf>   size: wrap(rel)  style=field_label(abs)
    - TextField[Video link]  <leaf>   size: wrap(rel)
  - Zone[14]  <leaf>   size: wrap(rel)

  ids:
    exercise_create/Row[0]
    exercise_create/Row[0]/Button[←]
    exercise_create/Row[0]/Column[1]
    exercise_create/Row[0]/Column[1]/Text[New exercise]
    exercise_create/Row[0]/Button[Save]
    exercise_create/Column[1]
    exercise_create/Column[1]/Text[Exercise name]
    exercise_create/Column[1]/TextField[Name]
    exercise_create/Text[Primary muscles *]
    exercise_create/Row[3]
    exercise_create/Row[3]/Text[Select muscles]
    exercise_create/Row[3]/Text[▾]
    exercise_create/Text[Secondary muscles]
    exercise_create/Row[5]
    exercise_create/Row[5]/Text[Select muscles]
    exercise_create/Row[5]/Text[▾]
    exercise_create/Column[6]
    exercise_create/Column[6]/Text[Movement pattern]
    exercise_create/Column[6]/Row[1]
    exercise_create/Column[6]/Row[1]/Text[Push Horizontal]
    exercise_create/Column[6]/Row[1]/Text[▾]
    exercise_create/Column[7]
    exercise_create/Column[7]/Text[Equipment]
    exercise_create/Column[7]/Row[1]
    exercise_create/Column[7]/Row[1]/Text[Barbell]
    exercise_create/Column[7]/Row[1]/Text[▾]
    exercise_create/Row[8]
    exercise_create/Row[8]/Row[0]
    exercise_create/Row[8]/Row[0]/Text[Unilateral]
    exercise_create/Row[8]/Row[0]/Row[1]
    exercise_create/Row[8]/Row[0]/Row[1]/Marker[0]
    exercise_create/Row[8]/Row[0]/Row[1]/Text[1]
    exercise_create/Row[8]/Row[1]
    exercise_create/Row[8]/Row[1]/Text[Compound]
    exercise_create/Row[8]/Row[1]/Row[1]
    exercise_create/Row[8]/Row[1]/Row[1]/Marker[0]
    exercise_create/Row[8]/Row[1]/Row[1]/Text[1]
    exercise_create/Column[9]
    exercise_create/Column[9]/Text[Base starting weight on (optio…]
    exercise_create/Column[9]/Row[1]
    exercise_create/Column[9]/Row[1]/Text[None — start light]
    exercise_create/Column[9]/Row[1]/Text[▾]
    exercise_create/Text[For a new movement, we'll star…]
    exercise_create/TextField[Form notes (optional)]
    exercise_create/TextField[Coaching cues (optional)]
    exercise_create/Column[13]
    exercise_create/Column[13]/Text[Video link (optional)]
    exercise_create/Column[13]/TextField[Video link]
    exercise_create/Zone[14]

---
## cross-side compare: Compose ExerciseCreateScreen <-> kit exercise_create
- STRUCTURAL leaf match (LCS, dynamic-aware): 23/55 Compose leaves aligned to kit (41%)
- static content matched (by literal): 13
    = Base starting weight on (optio…
    = Coaching cues (optional)
    = Compound
    = Equipment
    = Exercise name
    = For a new movement, we'll star…
    = Form notes (optional)
    = Movement pattern
    = Primary muscles *
    = Save
    = Secondary muscles
    = Unilateral
    = Video link (optional)
- Compose leaves NOT aligned: 32  ·  kit leaves not aligned: 4
- (raw content-anchor only: Compose-only 13, kit-only 9)
