# UI layout ledger (KIT side) -- progress

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=tab_row(abs)
    - Column[0]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[Analytics]  <leaf>   size: wrap(rel)  style=tab_off(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[Bests]  <leaf>   size: wrap(rel)  style=tab_off(abs)
    - Column[2]  <container>   size: weight(1.0)(rel)  style=tab_col(abs)
      - Button[History]  <leaf>   size: wrap(rel)  style=tab_off(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No workouts yet]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[Completed sessions and cardio …]  <leaf>   size: wrap(rel)  style=empty_body(abs)

  ids:
    progress/Row[0]
    progress/Row[0]/Column[0]
    progress/Row[0]/Column[0]/Button[Analytics]
    progress/Row[0]/Column[1]
    progress/Row[0]/Column[1]/Button[Bests]
    progress/Row[0]/Column[2]
    progress/Row[0]/Column[2]/Button[History]
    progress/Column[1]
    progress/Column[1]/Text[No workouts yet]
    progress/Column[1]/Text[Completed sessions and cardio …]

---
## cross-side compare: Compose ProgressScreen <-> kit progress
- STRUCTURAL leaf match (LCS, dynamic-aware): 5/147 Compose leaves aligned to kit (3%)
- static content matched (by literal): 2
    = Completed sessions and cardio …
    = No workouts yet
- Compose leaves NOT aligned: 142  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 61, kit-only 3)
