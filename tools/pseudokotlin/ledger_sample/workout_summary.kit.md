# UI layout ledger (KIT side) -- workout_summary

Python/kit side, runtime-traced: a recording UI captured every define_* call (incl.
helper-emitted), tree rebuilt from the explicit parent ids. Same normalized schema as
the Compose side. (Mock db/VM; a couple of mock items per list so row STRUCTURE renders.)

  - Row[0]  <container>   size: wrap(rel)  style=top_bar(abs)
    - Button[←]  <leaf>   size: wrap(rel)  style=tb_back(abs)
    - Column[1]  <container>   size: weight(1.0)(rel)
      - Text[Workout complete]  <leaf>   size: wrap(rel)  style=tb_title(abs)
    - Button[Done]  <leaf>   size: wrap(rel)  style=tb_action(abs)
  - Column[1]  <container>   size: wrap(rel)  style=empty(abs)
    - Text[No session]  <leaf>   size: wrap(rel)  style=empty_title(abs)
    - Text[No session data found.]  <leaf>   size: wrap(rel)  style=empty_body(abs)

  ids:
    workout_summary/Row[0]
    workout_summary/Row[0]/Button[←]
    workout_summary/Row[0]/Column[1]
    workout_summary/Row[0]/Column[1]/Text[Workout complete]
    workout_summary/Row[0]/Button[Done]
    workout_summary/Column[1]
    workout_summary/Column[1]/Text[No session]
    workout_summary/Column[1]/Text[No session data found.]

---
## cross-side compare: Compose WorkoutSummaryScreen <-> kit workout_summary
- STRUCTURAL leaf match (LCS, dynamic-aware): 5/25 Compose leaves aligned to kit (20%)
- static content matched (by literal): 2
    = Done
    = Workout complete
- Compose leaves NOT aligned: 20  ·  kit leaves not aligned: 0
- (raw content-anchor only: Compose-only 17, kit-only 3)
