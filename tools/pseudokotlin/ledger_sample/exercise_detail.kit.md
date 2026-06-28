# UI layout ledger (KIT side) -- exercise_detail

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[0]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[♡]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Button[⋮]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Row[2]  <container>   size: wrap(rel)  style=chip_row(abs)
    - Text[Built-in]  <leaf>   size: wrap(rel)  style=chip_suggestion(abs)
    - Text[Isolation]  <leaf>   size: wrap(rel)  style=chip_suggestion(abs)
    - Text[Bilateral]  <leaf>   size: wrap(rel)  style=chip_suggestion(abs)
  - Column[3]  <container>   size: wrap(rel)  style=detail_section(abs)
    - Text[Primary muscles]  <leaf>   size: wrap(rel)  style=section_label(abs)
    - Column[1]  <container>   size: wrap(rel)  style=detail_content(abs)
      - Row[0]  <leaf>   size: wrap(rel)  style=chip_row(abs)
  - Column[4]  <container>   size: wrap(rel)  style=detail_section(abs)
    - Text[Movement & equipment]  <leaf>   size: wrap(rel)  style=section_label(abs)
    - Column[1]  <container>   size: wrap(rel)  style=detail_content(abs)
      - Text[Mobility · Other]  <leaf>   size: wrap(rel)  style=card_body(abs)

  ids:
    exercise_detail/Row[0]
    exercise_detail/Row[0]/Button[←]
    exercise_detail/Row[0]/Column[1]
    exercise_detail/Row[0]/Column[1]/Text[0]
    exercise_detail/Row[0]/Button[♡]
    exercise_detail/Button[⋮]
    exercise_detail/Row[2]
    exercise_detail/Row[2]/Text[Built-in]
    exercise_detail/Row[2]/Text[Isolation]
    exercise_detail/Row[2]/Text[Bilateral]
    exercise_detail/Column[3]
    exercise_detail/Column[3]/Text[Primary muscles]
    exercise_detail/Column[3]/Column[1]
    exercise_detail/Column[3]/Column[1]/Row[0]
    exercise_detail/Column[4]
    exercise_detail/Column[4]/Text[Movement & equipment]
    exercise_detail/Column[4]/Column[1]
    exercise_detail/Column[4]/Column[1]/Text[Mobility · Other]

---
## cross-side compare: Compose ExerciseDetailScreen <-> kit exercise_detail
- STRUCTURAL leaf match (LCS, dynamic-aware): 9/63 Compose leaves aligned to kit (14%)
- static content matched (by literal): 3
    = Built-in
    = Movement & equipment
    = Primary muscles
- Compose leaves NOT aligned: 54  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 29, kit-only 6)
