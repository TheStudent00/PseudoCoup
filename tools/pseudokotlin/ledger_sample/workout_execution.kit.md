# UI layout ledger (KIT side) -- workout_execution

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[0]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[Finish]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No exercises]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[This session has no exercises.]  <leaf>   size: wrap(rel)  style=empty_body(abs)

  ids:
    workout_execution/Row[0]
    workout_execution/Row[0]/Button[←]
    workout_execution/Row[0]/Column[1]
    workout_execution/Row[0]/Column[1]/Text[0]
    workout_execution/Row[0]/Button[Finish]
    workout_execution/Column[1]
    workout_execution/Column[1]/Text[No exercises]
    workout_execution/Column[1]/Text[This session has no exercises.]

---
## cross-side compare: Compose WorkoutExecutionScreen <-> kit workout_execution
- STRUCTURAL leaf match (LCS, dynamic-aware): 4/558 Compose leaves aligned to kit (0%)
- static content matched (by literal): 1
    = Finish
- Compose leaves NOT aligned: 554  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 119, kit-only 3)
