# UI layout ledger (KIT side) -- exercise_create

Python/kit side, runtime-traced through the app's OWN seeded InMemoryDb (real data).
A recording UI captured every define_* call; tree rebuilt from the explicit parent ids.

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

---
## cross-side compare: Compose ExerciseCreateScreen <-> kit exercise_create
- distinct widget signatures matched: 11/19 = 57%
  (static leaf by content; dynamic binding by type -- instance counts ignored)
- kit signatures NOT in Compose: 4
    PY  F:Coaching cues (optional)
    PY  F:Form notes (optional)
    PY  F:·DYN·
    PY  T:Save
